#!/usr/bin/env python3
"""Frequency-resolved phase probe of saved encoder checkpoints.

Diagnostic only: no training, no test split, no tracked-file writes.
For each pair and each STFT bin, fit a ridge readout from the frozen E
cross-product features (C x C) to [cos(phi), sin(phi)] of the clean-D
cross-spectrum, then recover TDOA from the phase slope over frequency.

Fit on probe sources 8103, evaluate on dev sources 8102. Test 8104 is never used.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import torch  # noqa: E402

import reprobe as R  # noqa: E402
import benchmark as b  # noqa: E402

b.DEVICE = "cpu"
torch.set_num_threads(4)

M = 8
FIT_SRC, FIT_NOISE = 8103, 9103
EVAL_SRC, EVAL_NOISE = 8102, 9200
TEST_SRC = 8104
CONDS = [("clean", "clean"), ("0", 0), ("10", 10), ("20", 20)]
F_BINS = np.arange(11, 54)
FREQS = F_BINS * b.CFG["fs"] / b.CFG["nfft"]
TAUS_US = np.arange(-130.0, 130.0001, 0.25)
SCALE = None


def complex_stft8(x):
    """x: (n,M,L) -> (n,M,F,T) complex64, bins 11..53."""
    z = R.stft8(x)
    return torch.complex(z[:, :, 0], z[:, :, 1])


def phase_from_Z(Z, i, j):
    """Z: (n,M,F,T) -> (n,F) phase of the mean cross-spectrum."""
    g = Z[:, i] * torch.conj(Z[:, j])
    return torch.angle(g.mean(-1)).cpu().numpy()


def per_bin_feats(z, i, j):
    """z: (n,M,C,F,T) -> (n,F,C*C) cross-product features per bin."""
    n, m, c, f, t = z.shape
    cross = torch.einsum("ncft,ndft->nfcd", z[:, i], z[:, j]) / t
    return cross.reshape(n, f, c * c).cpu().numpy()


def fit_phase(feat, phi):
    target = np.column_stack((np.cos(phi), np.sin(phi)))
    return b.probe_fit(feat, target)


def predict_phase(probe, feat):
    pred = b.probe_apply(probe, feat)
    return np.arctan2(pred[:, 1], pred[:, 0])


def phase_to_tau(phi):
    """phi: (n,F) -> (tau_us, boundary_flag) via grid search over [-130,130] us."""
    e = np.exp(1j * phi)
    a = np.exp(1j * 2 * np.pi * FREQS[None, :] * TAUS_US[:, None] * 1e-6)
    mag = np.abs(e @ a.T)
    idx = np.argmax(mag, axis=1)
    n = len(idx)
    ic = np.clip(idx, 1, len(TAUS_US) - 2)
    y0 = mag[np.arange(n), ic - 1]
    y1 = mag[np.arange(n), ic]
    y2 = mag[np.arange(n), ic + 1]
    den = y0 - 2 * y1 + y2
    delta = np.where(np.abs(den) > 1e-12, 0.5 * (y0 - y2) / den, 0.0)
    tau = TAUS_US[ic] + delta * (TAUS_US[1] - TAUS_US[0])
    boundary = (idx == 0) | (idx == len(TAUS_US) - 1)
    return tau, boundary


def phase_err(phi_hat, phi_true):
    return np.abs(np.angle(np.exp(1j * (phi_hat - phi_true))))  # (n,F)


def fmt_err(err):
    err = np.asarray(err, dtype=np.float64).ravel()
    if err.size == 0:
        return {"n": 0, "median": None, "p95": None}
    return {"n": int(err.size), "median": float(np.median(err)),
            "p95": float(np.percentile(err, 95))}


def run_state(enc, fit10, fitrand, eval8, pairs, variants):
    z10 = R.encode8(enc, R.stft8(fit10[2]) / SCALE)
    zr = R.encode8(enc, R.stft8(fitrand[2]) / SCALE)
    zev = {c: R.encode8(enc, R.stft8(d[2]) / SCALE) for c, d in eval8.items()}
    z10c = complex_stft8(fit10[1])
    z10o = complex_stft8(fit10[2])
    zrc = complex_stft8(fitrand[1])
    zec = {c: complex_stft8(d[1]) for c, d in eval8.items()}

    acc = {}
    for (i, j) in pairs:
        f10 = per_bin_feats(z10, i, j)
        fr = per_bin_feats(zr, i, j)
        phi10c = phase_from_Z(z10c, i, j)
        phi10o = phase_from_Z(z10o, i, j)
        phirc = phase_from_Z(zrc, i, j)
        probes = {}
        for f in range(f10.shape[1]):
            probes[("clean10", f)] = fit_phase(f10[:, f], phi10c[:, f])
            probes[("cleanrand", f)] = fit_phase(fr[:, f], phirc[:, f])
            probes[("obs10", f)] = fit_phase(f10[:, f], phi10o[:, f])
        for cond, d in eval8.items():
            fe = per_bin_feats(zev[cond], i, j)
            phit = phase_from_Z(zec[cond], i, j)
            for variant in variants:
                if variant not in ("clean10", "cleanrand", "obs10"):
                    continue
                phihat = np.column_stack([predict_phase(probes[(variant, f)], fe[:, f])
                                          for f in range(fe.shape[1])])
                tau, boundary = phase_to_tau(phihat)
                perr = phase_err(phihat, phit).mean(1)
                acc.setdefault((variant, cond), {})[(i, j)] = {
                    "tau": tau, "boundary": boundary, "perr": perr}
    return acc


def summarize(acc, eval8, pairs, variants):
    out = {}
    for variant in variants:
        for cond in eval8:
            key = (variant, cond)
            if key not in acc:
                continue
            preds = {p: v["tau"] for p, v in acc[key].items()}
            true_tau = R.targets(eval8[cond][0][2])
            u1 = R.u_metrics(R.slope(preds, 1), eval8[cond][0][2])
            u7 = R.u_metrics(R.slope(preds, 7), eval8[cond][0][2])
            perr = np.concatenate([v["perr"] for v in acc[key].values()])
            boundary = float(np.mean([v["boundary"].mean() for v in acc[key].values()]))
            pair_med = {f"{i}-{j}": float(np.median(np.abs(v["tau"] - true_tau[(i, j)])))
                        for (i, j), v in acc[key].items()}
            out.setdefault(variant, {})[cond] = {
                "u_k1": u1, "u_k7": u7,
                "pair_median_tdoa_us": pair_med,
                "phase_err_rad": fmt_err(perr),
                "boundary_fraction": boundary,
                "n_pairs": len(preds),
            }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--only", default="")
    ap.add_argument("--pairs", type=int, default=1, choices=[1, 2, 3, 7])
    ap.add_argument("--variants", default="clean10,cleanrand,obs10")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    variants = tuple(s.strip() for s in args.variants.split(",") if s.strip())

    global SCALE
    res = json.loads((R.PILOT / "results.json").read_text())
    SCALE = float(res["scale_train_only"])
    runs = res["runs"]
    sha_ok = all(R.sha256(r["weight_path"]) == r["weight_sha256"] for r in runs)
    test_ok = TEST_SRC not in (FIT_SRC, EVAL_SRC)
    assert sha_ok and test_ok

    n_fit = 64 if args.quick else 512
    n_eval = 64 if args.quick else 256
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M) if (j - i) <= args.pairs]
    t_start = time.time()

    fit10 = R.gen8(n_fit, FIT_SRC, FIT_NOISE, 10)
    fitrand = R.gen8(n_fit, FIT_SRC, FIT_NOISE, "train", per_source=True)
    eval8 = {c: R.gen8(n_eval, EVAL_SRC, EVAL_NOISE + 2 * k, snr)
             for k, (c, snr) in enumerate(CONDS)}

    # Checks on the first selected model.
    first = next(r for r in runs if not only or f"{r['architecture']}:{r['seed']}" in only)
    ck0 = torch.load(first["weight_path"], map_location="cpu", weights_only=True)
    m0 = b.MODELS[first["architecture"]]()
    m0.load_state_dict(ck0["encoder"])
    m0.eval()
    m0.requires_grad_(False)
    z10 = R.encode8(m0, R.stft8(fit10[2]) / SCALE)
    z10b = R.encode8(m0, R.stft8(fit10[2]) / SCALE)
    det_ok = bool(torch.equal(z10, z10b))
    f10 = per_bin_feats(z10, 0, 1)
    old = R.pair_feats(z10, "mid12")[(0, 1)]
    feat_ok = bool(np.allclose(f10[:, 21], old[:, 256:], atol=1e-5, rtol=1e-5))
    phi = phase_from_Z(complex_stft8(fit10[1]), 0, 1)
    tau0, boundary0 = phase_to_tau(phi)
    true0 = R.targets(fit10[0][2])[(0, 1)]
    grid_ok = bool(np.median(np.abs(tau0 - true0)) < 0.05)
    u0 = R.slope({(0, 1): true0}, 1)
    slope_ok = bool(np.max(np.abs(u0 - np.asarray(fit10[0][2]))) < 1e-6)

    checks = {
        "checkpoints_sha": sha_ok,
        "test_not_used": test_ok,
        "features_bin21_match": feat_ok,
        "noiseless_phase_grid": grid_ok,
        "noiseless_slope": slope_ok,
        "deterministic_encoding": det_ok,
    }
    meta = {
        "python": __import__("platform").python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "device": "cpu",
        "scale_train_only": SCALE,
        "split": {"fit_source": FIT_SRC, "fit_noise": FIT_NOISE,
                  "eval_source": EVAL_SRC, "eval_noise": EVAL_NOISE,
                  "test_source": TEST_SRC, "test_used": False},
        "n_fit": n_fit, "n_eval": n_eval, "pairs": args.pairs,
        "variants": variants, "quick": bool(args.quick),
        "script_sha256": R.sha256(__file__),
        "protocol_sha256": R.sha256(out / "phase_protocol.json") if (out / "phase_protocol.json").exists() else None,
        "benchmark_sha256": R.sha256(R.PILOT / "benchmark.py"),
        "checks": checks,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    rows = []
    for run in runs:
        key = f"{run['architecture']}:{run['seed']}"
        if only and key not in only:
            continue
        ck = torch.load(run["weight_path"], map_location="cpu", weights_only=True)
        trained = b.MODELS[run["architecture"]]()
        trained.load_state_dict(ck["encoder"])
        trained.eval()
        trained.requires_grad_(False)
        R.seed_cpu(run["seed"])
        untrained = b.MODELS[run["architecture"]]()
        untrained.eval()
        untrained.requires_grad_(False)
        same = all(torch.equal(trained.state_dict()[k], untrained.state_dict()[k])
                   for k in trained.state_dict())
        assert not same, f"untrained equals trained: {key}"

        row = {"architecture": run["architecture"], "seed": run["seed"], "states": {}}
        for state_name, enc in (("trained", trained), ("untrained", untrained)):
            t0 = time.time()
            acc = run_state(enc, fit10, fitrand, eval8, pairs, variants)
            row["states"][state_name] = {
                "variants": summarize(acc, eval8, pairs, variants),
                "seconds": round(time.time() - t0, 2),
            }
        rows.append(row)
        (out / "phase_results.json").write_text(
            json.dumps({"meta": meta, "rows": rows}, indent=2) + "\n")
        print(f"{key} done", flush=True)

    # Raw reference (enc=None), clean10 only.
    raw_acc = run_state(None, fit10, fitrand, eval8, pairs, ("clean10",))
    raw = summarize(raw_acc, eval8, pairs, ("clean10",))
    payload = {"meta": {**meta, "wall_seconds": round(time.time() - t_start, 2)},
               "rows": rows, "raw": raw}
    (out / "phase_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out / "phase_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"out": str(out), "checks": checks,
                      "wall_seconds": payload["meta"]["wall_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
