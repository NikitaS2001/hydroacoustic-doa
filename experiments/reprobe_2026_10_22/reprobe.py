#!/usr/bin/env python3
"""All-aperture re-probe of saved encoder checkpoints.

Diagnostic only: no training, no test split, no repo writes.
Reads the nine checkpoints saved by experiments/encoder_phase_pilot/benchmark.py
and compares three readouts at the same frozen E:
  1. old 2-channel adjacent-pair probe (b.features / b.probe_fit / b.metrics)
  2. new probe on the same pair with the same 512 features
  3. all-pair probe (28 pairs) -> OLS slope -> u_hat
Fit on probe sources 8103, evaluate on dev sources 8102. Test 8104 is never used.
"""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "experiments/encoder_phase_pilot"
sys.path.insert(0, str(PILOT))
import benchmark as b  # noqa: E402

b.DEVICE = "cpu"
torch.set_num_threads(4)

M = 8
FIT_SRC, FIT_NOISE = 8103, 9103
EVAL_SRC, EVAL_NOISE = 8102, 9200
TEST_SRC = 8104
CONDS = [("clean", "clean"), ("0", 0), ("10", 10), ("20", 20)]
SCALE = None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_cpu(s):
    torch.manual_seed(s)


def gen8(n, source_seed, noise_seed, snr, per_source=False):
    """Generate 8 synchronous channels for one source; per-channel independent noise."""
    src = b.sources(n, source_seed)
    u = np.asarray(src[2], dtype=np.float64)
    clean = torch.stack([b.wave(src, m * b.CFG["d"] * u / b.CFG["c"]) for m in range(M)], dim=1)
    obs = clean.clone()
    if per_source:
        rng = np.random.default_rng(noise_seed)
        sv = rng.uniform(0, 20, n).astype(np.float32)
        arg = torch.tensor(sv, dtype=torch.float32, device=b.DEVICE).reshape(n, 1)
        for m in range(M):
            obs[:, m] = b.noisy(clean[:, m], arg, noise_seed + m)
    elif isinstance(snr, str):
        pass  # clean
    else:
        for m in range(M):
            obs[:, m] = b.noisy(clean[:, m], snr, noise_seed + m)
    return src, clean, obs


def stft8(x):
    """x: (n,M,L) -> (n,M,2,F,T)."""
    n, m, length = x.shape
    z = b.stft(x.reshape(n * m, length))
    return z.reshape(n, m, z.shape[1], z.shape[2], z.shape[3])


def encode8(enc, x):
    """x: (n,M,2,F,T) -> (n,M,C,Fe,Te)."""
    n, m, c, f, t = x.shape
    z = b.encoded(enc, x.reshape(n * m, c, f, t))
    return z.reshape(n, m, z.shape[1], z.shape[2], z.shape[3])


def pair_feats(z, mode="mid12"):
    """z: (n,M,C,F,T) -> {(i,j): (n,D)}.

    mid12: mean over F + 12 kHz bin (same 512 features as b.features), but for
           |i-j|>2 the 12 kHz phase is ambiguous at |u|=0.8.
    low4:  4.125 and 4.5 kHz bins (512 features), unambiguous for all 28 pairs
           at |u|<=0.8 (max tau 100.8 us < half-period 111-121 us).
    meanf: mean over F only (256 features), reference.
    """
    n, m, c, f, t = z.shape
    out = {}
    for i in range(m):
        for j in range(i + 1, m):
            cross = torch.einsum("ncft,ndft->nfcd", z[:, i], z[:, j]) / t
            if mode == "mid12":
                feat = torch.cat((cross.mean(1).reshape(n, -1), cross[:, 21].reshape(n, -1)), dim=1)
            elif mode == "low4":
                feat = torch.cat((cross[:, 11].reshape(n, -1), cross[:, 12].reshape(n, -1)), dim=1)
            elif mode == "fmax":
                sep = abs(i - j)
                fmax = 0.9 * b.CFG["c"] / (2.0 * sep * b.CFG["d"] * b.CFG["umax"])
                freqs = np.arange(11, 54) * b.CFG["fs"] / b.CFG["nfft"]
                valid = np.where(freqs <= fmax)[0]
                bin_idx = int(valid[-1]) if valid.size else 0
                feat = cross[:, bin_idx].reshape(n, -1)
            elif mode == "meanf":
                feat = cross.mean(1).reshape(n, -1)
            else:
                raise ValueError(mode)
            out[(i, j)] = feat.detach().cpu().numpy()
    return out


def targets(u):
    """True pairwise TDOA in microseconds: tau_i - tau_j = (i-j) d u / c."""
    u = np.asarray(u, dtype=np.float64)
    return {(i, j): (i - j) * b.CFG["d"] * u / b.CFG["c"] * 1e6
            for i in range(M) for j in range(i + 1, M)}


def slope(preds, max_sep=7):
    """OLS slope of tau_ij over (i-j), using pairs with |i-j| <= max_sep.

    u_hat = slope * c / d / 1e6 because targets are in microseconds.
    """
    num = 0.0
    den = 0.0
    for (i, j), p in preds.items():
        if abs(i - j) > max_sep:
            continue
        num = num + (i - j) * p
        den += (i - j) ** 2
    # targets are in microseconds: tau_ij = (i-j) d u / c * 1e6.
    return (num / den) * b.CFG["c"] / b.CFG["d"] * 1e-6


def basic(err):
    err = np.asarray(err, dtype=np.float64)
    if err.size == 0:
        return {"n": 0, "median": None, "p95": None, "mean": None}
    return {"n": int(err.size),
            "median": float(np.median(err)),
            "p95": float(np.percentile(err, 95)),
            "mean": float(np.mean(err))}


def tdoa_metrics(pred, tau):
    pred = np.asarray(pred, dtype=np.float64)
    tau = np.asarray(tau, dtype=np.float64)
    finite = np.isfinite(pred)
    return {"coverage": float(finite.mean()), **basic(np.abs(pred[finite] - tau[finite]))}


def u_metrics(u_hat, u_true):
    u_hat = np.asarray(u_hat, dtype=np.float64)
    u_true = np.asarray(u_true, dtype=np.float64)
    finite = np.isfinite(u_hat)
    uh = u_hat[finite]
    ut = u_true[finite]
    theta_hat = np.degrees(np.arcsin(np.clip(uh, -1.0, 1.0)))
    theta_true = np.degrees(np.arcsin(ut))
    return {"coverage": float(finite.mean()),
            "out_of_sector": float((np.abs(uh) > b.CFG["umax"]).mean()) if uh.size else None,
            "u": basic(np.abs(uh - ut)),
            "theta_deg": basic(np.abs(theta_hat - theta_true))}


def old_state(enc, fit_pairs, eval_pairs):
    af, bf, tf, tauf, phf = fit_pairs
    ff, _ = b.features(enc, af, bf)
    probe = b.probe_fit(ff, tf)
    out = {}
    for cond, (ae, be, te, taue, phe) in eval_pairs.items():
        fe, _ = b.features(enc, ae, be)
        out[cond] = b.metrics(b.probe_apply(probe, fe), taue, phe)
    return out


def eval_state(enc, fit8, eval8, mode="mid12", with_pairs=False):
    src_f, clean_f, obs_f = fit8
    zf = encode8(enc, stft8(obs_f) / SCALE)
    ff = pair_feats(zf, mode)
    tf = targets(src_f[2])
    probes = {p: b.probe_fit(ff[p], tf[p]) for p in ff}
    out = {}
    for cond, (src_e, clean_e, obs_e) in eval8.items():
        ze = encode8(enc, stft8(obs_e) / SCALE)
        fe = pair_feats(ze, mode)
        te = targets(src_e[2])
        preds = {p: b.probe_apply(probes[p], fe[p]).reshape(-1) for p in fe}
        pair_err_mean = np.mean([np.abs(preds[p] - te[p]) for p in preds], axis=0)
        uh7 = slope(preds, 7)
        uh3 = slope(preds, 3)
        uh2 = slope(preds, 2)
        uh1 = slope(preds, 1)
        block = {
            "adjacent_tdoa_us": tdoa_metrics(preds[(0, 1)], te[(0, 1)]),
            "allpairs_u": u_metrics(uh7, src_e[2]),
            "slope_u_k3": u_metrics(uh3, src_e[2])["u"],
            "slope_u_k2": u_metrics(uh2, src_e[2])["u"],
            "slope_u_k1": u_metrics(uh1, src_e[2])["u"],
            "pair_mean_tdoa_us": basic(pair_err_mean),
            "n_pairs": len(preds),
        }
        if with_pairs:
            block["pair_median_tdoa_us"] = {
                f"{i}-{j}": float(np.median(np.abs(preds[(i, j)] - te[(i, j)])))
                for (i, j) in preds
            }
        out[cond] = block
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "out"))
    ap.add_argument("--only", default="", help="comma-separated architecture:seed")
    ap.add_argument("--quick", action="store_true", help="small n for smoke test")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    global SCALE
    res = json.loads((PILOT / "results.json").read_text())
    SCALE = float(res["scale_train_only"])
    runs = res["runs"]

    sha_ok = all(sha256(r["weight_path"]) == r["weight_sha256"] for r in runs)
    test_ok = TEST_SRC not in (FIT_SRC, EVAL_SRC)
    assert sha_ok, "checkpoint SHA mismatch"
    assert test_ok, "test seed used"

    n_fit = 64 if args.quick else 512
    n_eval = 64 if args.quick else 256
    t_start = time.time()

    fit8 = gen8(n_fit, FIT_SRC, FIT_NOISE, "train", per_source=True)
    fit_pairs = b.pairs(n_fit, FIT_SRC, FIT_NOISE, "train", SCALE)
    eval8 = {}
    eval_pairs = {}
    for k, (cond, snr) in enumerate(CONDS):
        eval8[cond] = gen8(n_eval, EVAL_SRC, EVAL_NOISE + 2 * k, snr)
        eval_pairs[cond] = b.pairs(n_eval, EVAL_SRC, EVAL_NOISE + 2 * k, snr, SCALE)

    x8_fit = stft8(fit8[2]) / SCALE
    x8_10 = stft8(eval8["10"][2]) / SCALE
    ch_fit = bool(np.allclose(x8_fit[:, 0].numpy(), fit_pairs[0].numpy(), atol=1e-6, rtol=1e-5)
                  and np.allclose(x8_fit[:, 1].numpy(), fit_pairs[1].numpy(), atol=1e-6, rtol=1e-5))
    ch_eval = bool(np.allclose(x8_10[:, 0].numpy(), eval_pairs["10"][0].numpy(), atol=1e-6, rtol=1e-5)
                   and np.allclose(x8_10[:, 1].numpy(), eval_pairs["10"][1].numpy(), atol=1e-6, rtol=1e-5))

    u0 = np.array([-0.6, 0.0, 0.6])
    uh0 = slope(targets(u0))
    slope_ok = bool(np.allclose(uh0, u0, atol=1e-9))

    first = next((r for r in runs if not only or f"{r['architecture']}:{r['seed']}" in only), None)
    assert first is not None
    ck0 = torch.load(first["weight_path"], map_location="cpu", weights_only=True)
    m0 = b.MODELS[first["architecture"]]()
    m0.load_state_dict(ck0["encoder"])
    m0.eval()
    m0.requires_grad_(False)
    z1 = encode8(m0, stft8(fit8[2]) / SCALE)
    z2 = encode8(m0, stft8(fit8[2]) / SCALE)
    det_ok = bool(torch.equal(z1, z2))
    ff0 = pair_feats(z1)
    old_ff0, _ = b.features(m0, fit_pairs[0], fit_pairs[1])
    feat_ok = bool(np.allclose(ff0[(0, 1)], old_ff0, atol=1e-5, rtol=1e-5))

    checks = {
        "checkpoints_sha": sha_ok,
        "test_not_used": test_ok,
        "channels01_match_pairs_fit": ch_fit,
        "channels01_match_pairs_eval10": ch_eval,
        "features_match_old_probe": feat_ok,
        "noiseless_slope": slope_ok,
        "deterministic_encoding": det_ok,
    }

    meta = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "platform": platform.platform(),
        "device": "cpu",
        "scale_train_only": SCALE,
        "split": {"fit_source": FIT_SRC, "fit_noise": FIT_NOISE,
                  "eval_source": EVAL_SRC, "eval_noise": EVAL_NOISE,
                  "test_source": TEST_SRC, "test_used": False},
        "n_fit": n_fit, "n_eval": n_eval, "quick": bool(args.quick),
        "script_sha256": sha256(__file__),
        "protocol_sha256": sha256(out / "protocol.json") if (out / "protocol.json").exists() else None,
        "benchmark_sha256": sha256(PILOT / "benchmark.py"),
        "results_sha256": sha256(PILOT / "results.json"),
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
        seed_cpu(run["seed"])
        untrained = b.MODELS[run["architecture"]]()
        untrained.eval()
        untrained.requires_grad_(False)
        same = all(torch.equal(trained.state_dict()[k], untrained.state_dict()[k])
                   for k in trained.state_dict())
        assert not same, f"untrained equals trained: {key}"

        row = {"architecture": run["architecture"], "seed": run["seed"],
               "weight_sha256": run["weight_sha256"], "states": {}}
        for state_name, enc in (("trained", trained), ("untrained", untrained)):
            t0 = time.time()
            old = old_state(enc, fit_pairs, eval_pairs)
            mid = eval_state(enc, fit8, eval8, "mid12", with_pairs=True)
            low = eval_state(enc, fit8, eval8, "low4")
            fmax = eval_state(enc, fit8, eval8, "fmax")
            row["states"][state_name] = {"old": old, "mid12": mid, "low4": low, "fmax": fmax,
                                         "seconds": round(time.time() - t0, 3)}
        rows.append(row)
        payload = {"meta": meta,
                   "raw": {"old": old_state(None, fit_pairs, eval_pairs),
                           "mid12": eval_state(None, fit8, eval8, "mid12", with_pairs=True),
                           "low4": eval_state(None, fit8, eval8, "low4"),
                           "fmax": eval_state(None, fit8, eval8, "fmax")},
                   "rows": rows}
        (out / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
        print(f"{key} done", flush=True)

    payload = {"meta": {**meta, "wall_seconds": round(time.time() - t_start, 2)},
               "raw": {"old": old_state(None, fit_pairs, eval_pairs),
                       "mid12": eval_state(None, fit8, eval8, "mid12", with_pairs=True),
                       "low4": eval_state(None, fit8, eval8, "low4"),
                       "fmax": eval_state(None, fit8, eval8, "fmax")},
               "rows": rows}
    (out / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"out": str(out), "checks": checks,
                      "wall_seconds": payload["meta"]["wall_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
