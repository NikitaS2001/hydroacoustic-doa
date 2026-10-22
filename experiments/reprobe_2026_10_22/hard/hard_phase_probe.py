#!/usr/bin/env python3
"""Hard-regime phase probe: multipath, calibration errors, coherent interference.

Diagnostic only: no training, no test split, no tracked-file writes.
Reuses the per-bin phase readout from phase_probe.py on the same nine checkpoints.
Fit on probe sources 8103 (fit environments), evaluate on dev sources 8102
(eval environments). Test 8104 is never used.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "phase"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import torch  # noqa: E402

import reprobe as R  # noqa: E402
import phase_probe as P  # noqa: E402
import benchmark as b  # noqa: E402

b.DEVICE = "cpu"
torch.set_num_threads(4)

M = 8
D, C = b.CFG["d"], b.CFG["c"]
L = b.CFG["length"]
F = 43
T = 1 + (L - b.CFG["nfft"]) // b.CFG["hop"]
FIT_SRC, EVAL_SRC, TEST_SRC = 8103, 8102, 8104
ENV_FIT = [7101, 7102, 7103, 7104]
ENV_EVAL = [7201, 7202, 7203, 7204]
SCALE = None


def make_env(seed):
    rng = np.random.default_rng(seed)
    n_refl = int(rng.integers(1, 3))
    return {
        "seed": seed,
        "u_refl": rng.uniform(-0.95, 0.95, n_refl),
        "tau_refl": rng.uniform(50e-6, 5e-3, n_refl),
        "amp_refl": rng.uniform(0.2, 0.8, n_refl) * rng.choice([-1.0, 1.0], n_refl),
        "gain": 10 ** (rng.uniform(-0.5, 0.5, M) / 20.0),
        "phase": rng.uniform(-0.05, 0.05, M),
        "skew": rng.uniform(-0.1e-6, 0.1e-6, M),
        "u_int": float(rng.uniform(-0.95, 0.95)),
        "sir_db": float(rng.uniform(0.0, 10.0)),
    }


def cal_matrix(env):
    f = P.FREQS
    cal = env["gain"][:, None] * np.exp(
        1j * (env["phase"][:, None] - 2 * np.pi * f[None, :] * env["skew"][:, None]))
    return torch.tensor(cal, dtype=torch.complex64)


def gen_hard(n, source_seed, env_seeds, condition, snr):
    envs = [make_env(s) for s in env_seeds]
    src = b.sources(n, source_seed)
    u = np.asarray(src[2], dtype=np.float64)
    env_idx = np.arange(n) % len(envs)
    obs = torch.zeros((n, M, F, T), dtype=torch.complex64)
    direct = torch.zeros_like(obs)
    direct_cal = torch.zeros_like(obs)
    for e, env in enumerate(envs):
        idx = np.where(env_idx == e)[0]
        if idx.size == 0:
            continue
        s = (src[0][idx], src[1][idx], src[2][idx])
        ue = np.asarray(src[2][idx], dtype=np.float64)
        d = torch.stack([b.wave(s, m * D * ue / C) for m in range(M)], dim=1)
        total = d.clone()
        if condition in ("mp", "mp_cal", "mp_cal_int"):
            for p in range(len(env["u_refl"])):
                r = torch.stack([b.wave(s, np.full(len(idx), env["tau_refl"][p] + m * D * env["u_refl"][p] / C))
                                 for m in range(M)], dim=1)
                total = total + float(env["amp_refl"][p]) * r
        if condition == "mp_cal_int":
            sint = b.sources(len(idx), source_seed + 1000 + e)
            it = torch.stack([b.wave(sint, np.full(len(idx), m * D * env["u_int"] / C))
                              for m in range(M)], dim=1)
            pd = d.square().mean((1, 2))
            pi = it.square().mean((1, 2))
            a = torch.sqrt(pd / (pi * 10 ** (env["sir_db"] / 10.0)))
            total = total + it * a[:, None, None]
        zt = P.complex_stft8(total)
        zd = P.complex_stft8(d)
        if condition in ("cal", "mp_cal", "mp_cal_int"):
            cal = cal_matrix(env)
            zt = zt * cal[None, :, :, None]
            zdc = zd * cal[None, :, :, None]
        else:
            zdc = zd
        if snr != "clean":
            pd = d.square().mean((1, 2))
            var = pd / 10 ** (float(snr) / 10.0)
            gen = torch.Generator().manual_seed(source_seed + 2000 + e)
            noise = torch.randn((len(idx), M, L), generator=gen) * torch.sqrt(var)[:, None, None]
            zt = zt + P.complex_stft8(noise)
        obs[idx] = zt
        direct[idx] = zd
        direct_cal[idx] = zdc
    return {"obs": obs, "direct": direct, "direct_cal": direct_cal, "u": u}


def run_condition(enc, fit, ev, pairs):
    xf = torch.stack((fit["obs"].real, fit["obs"].imag), dim=2)
    xe = torch.stack((ev["obs"].real, ev["obs"].imag), dim=2)
    zf = R.encode8(enc, xf / SCALE)
    ze = R.encode8(enc, xe / SCALE)
    acc = {}
    for (i, j) in pairs:
        ff = P.per_bin_feats(zf, i, j)
        fe = P.per_bin_feats(ze, i, j)
        phif = P.phase_from_Z(fit["direct"], i, j)
        phie = P.phase_from_Z(ev["direct"], i, j)
        phihat = np.column_stack([
            P.predict_phase(P.fit_phase(ff[:, f], phif[:, f]), fe[:, f])
            for f in range(F)])
        tau, bound = P.phase_to_tau(phihat)
        perr = P.phase_err(phihat, phie).mean(1)
        acc[(i, j)] = {"tau": tau, "bound": bound, "perr": perr}
    return acc


def summarize(acc, ev, pairs):
    preds = {p: v["tau"] for p, v in acc.items()}
    true_tau = R.targets(ev["u"])
    u1 = R.u_metrics(R.slope(preds, 1), ev["u"])
    u7 = R.u_metrics(R.slope(preds, 7), ev["u"])
    perr = np.concatenate([v["perr"] for v in acc.values()])
    boundary = float(np.mean([v["bound"].mean() for v in acc.values()]))
    pair_med = {f"{i}-{j}": float(np.median(np.abs(v["tau"] - true_tau[(i, j)])))
                for (i, j), v in acc.items()}
    return {"u_k1": u1, "u_k7": u7, "pair_median_tdoa_us": pair_med,
            "phase_err_rad": P.fmt_err(perr), "boundary_fraction": boundary,
            "n_pairs": len(preds)}


def oracle(ev, pairs):
    preds = {p: P.phase_to_tau(P.phase_from_Z(ev["direct"], *p))[0] for p in pairs}
    return {"u_k1": R.u_metrics(R.slope(preds, 1), ev["u"]),
            "u_k7": R.u_metrics(R.slope(preds, 7), ev["u"])}


def raw_phase_slope(ev, pairs):
    preds = {p: P.phase_to_tau(P.phase_from_Z(ev["obs"], *p))[0] for p in pairs}
    return {"u_k1": R.u_metrics(R.slope(preds, 1), ev["u"]),
            "u_k7": R.u_metrics(R.slope(preds, 7), ev["u"])}


STAGES = {
    "H1": [("direct", 10), ("mp", 10), ("cal", 10), ("mp_cal", 10)],
    "H2": [("mp", 0), ("mp", -5), ("mp_cal", 0), ("mp_cal", -5)],
    "H3": [("mp_cal_int", 10), ("mp_cal_int", 0)],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--only", default="")
    ap.add_argument("--stage", default="H1", choices=sorted(STAGES))
    ap.add_argument("--pairs", type=int, default=7, choices=[1, 2, 3, 7])
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    global SCALE
    res = json.loads((R.PILOT / "results.json").read_text())
    SCALE = float(res["scale_train_only"])
    runs = res["runs"]
    sha_ok = all(R.sha256(r["weight_path"]) == r["weight_sha256"] for r in runs)
    test_ok = TEST_SRC not in (FIT_SRC, EVAL_SRC)
    env_ok = set(ENV_FIT).isdisjoint(ENV_EVAL)
    assert sha_ok and test_ok and env_ok

    n_fit = 64 if args.quick else 512
    n_eval = 64 if args.quick else 256
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M) if (j - i) <= args.pairs]
    t_start = time.time()

    # Check: direct/clean must match the old generator.
    h = gen_hard(64, FIT_SRC, ENV_FIT, "direct", "clean")
    _, clean, _ = R.gen8(64, FIT_SRC, 9103, "clean")
    gen_ok = bool(np.allclose(h["obs"].numpy(), P.complex_stft8(clean).numpy(), atol=1e-6))
    # Check: zero calibration is identity.
    env0 = make_env(7101)
    cal0 = cal_matrix({**env0, "gain": np.ones(M), "phase": np.zeros(M), "skew": np.zeros(M)})
    cal_ok = bool(np.allclose(cal0.numpy(), np.ones((M, F), dtype=np.complex64)))
    # Check: noiseless geometric-direct grid.
    phi = P.phase_from_Z(h["direct"], 0, 1)
    tau0, _ = P.phase_to_tau(phi)
    true0 = R.targets(h["u"])[(0, 1)]
    grid_ok = bool(np.median(np.abs(tau0 - true0)) < 0.05)

    checks = {"checkpoints_sha": sha_ok, "test_not_used": test_ok,
              "env_disjoint": env_ok, "direct_clean_matches_gen8": gen_ok,
              "zero_calibration": cal_ok, "noiseless_grid": grid_ok}

    meta = {
        "python": __import__("platform").python_version(),
        "numpy": np.__version__, "torch": torch.__version__,
        "device": "cpu", "scale_train_only": SCALE,
        "split": {"fit_source": FIT_SRC, "eval_source": EVAL_SRC,
                  "test_source": TEST_SRC, "test_used": False,
                  "env_fit": ENV_FIT, "env_eval": ENV_EVAL},
        "n_fit": n_fit, "n_eval": n_eval, "pairs": args.pairs,
        "stage": args.stage, "quick": bool(args.quick),
        "script_sha256": R.sha256(__file__),
        "protocol_sha256": R.sha256(out / "hard_protocol.json") if (out / "hard_protocol.json").exists() else None,
        "checks": checks,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    rows = []
    refs = {}
    for condition, snr in STAGES[args.stage]:
        fit = gen_hard(n_fit, FIT_SRC, ENV_FIT, condition, snr)
        ev = gen_hard(n_eval, EVAL_SRC, ENV_EVAL, condition, snr)
        key = f"{condition}:{snr}"
        refs[key] = {"oracle": oracle(ev, pairs), "raw_phase_slope": raw_phase_slope(ev, pairs)}
        for run in runs:
            rkey = f"{run['architecture']}:{run['seed']}"
            if only and rkey not in only:
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
            assert not all(torch.equal(trained.state_dict()[k], untrained.state_dict()[k])
                           for k in trained.state_dict())
            row = {"architecture": run["architecture"], "seed": run["seed"], "conditions": {}}
            for state_name, enc in (("trained", trained), ("untrained", untrained)):
                acc = run_condition(enc, fit, ev, pairs)
                row["conditions"][state_name] = summarize(acc, ev, pairs)
            rows.append({"architecture": run["architecture"], "seed": run["seed"],
                         "condition": condition, "snr": snr,
                         "trained": row["conditions"]["trained"],
                         "untrained": row["conditions"]["untrained"]})
        raw_acc = run_condition(None, fit, ev, pairs)
        refs[key]["raw_readout"] = summarize(raw_acc, ev, pairs)
        (out / "hard_results.json").write_text(
            json.dumps({"meta": meta, "rows": rows, "refs": refs}, indent=2) + "\n")
        print(f"{key} done", flush=True)

    payload = {"meta": {**meta, "wall_seconds": round(time.time() - t_start, 2)},
               "rows": rows, "refs": refs}
    (out / "hard_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out / "hard_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"out": str(out), "checks": checks,
                      "wall_seconds": payload["meta"]["wall_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
