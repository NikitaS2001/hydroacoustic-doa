#!/usr/bin/env python3
"""Multipath-trained representation pilot.

Two observed-only objectives on the same hybrid_small encoder:
  recon: masked reconstruction of observed X
  jepa:  masked latent prediction with an EMA teacher
Evaluate the frozen E with the per-bin phase readout on mp_cal (10 and 0 dB).
Fit readout on 8103, evaluate on 8102 (unseen environments). Test 8104 is never used.
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

TRAIN = Path(__file__).resolve().parent
BASE = TRAIN.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "phase"))
sys.path.insert(0, str(BASE / "hard"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import torch  # noqa: E402
from torch import nn  # noqa: E402
from torch.nn import functional as Fn  # noqa: E402

import reprobe as R  # noqa: E402
import phase_probe as P  # noqa: E402
import hard_phase_probe as H  # noqa: E402
import benchmark as b  # noqa: E402

b.DEVICE = "cpu"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_num_threads(4)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False

C = 16
F = 43
T_E = 15
T_IN = 29
M = 8


def obs_to_reim(obs):
    x = torch.stack((obs.real, obs.imag), dim=2)
    return x.reshape(-1, 2, F, T_IN)


def gen_split(source_seed, envs, n_per_snr, snrs):
    parts = []
    for snr in snrs:
        h = H.gen_hard(n_per_snr, source_seed, envs, "mp_cal", snr)
        parts.append(h["obs"])
    return torch.cat(parts, 0)


def block_mask_batch(batch, seed, frac=0.3, block=4):
    g = torch.Generator().manual_seed(seed)
    m = torch.zeros(batch, F, T_E)
    nb = max(1, int(round(frac * F * T_E / (block * block))))
    for b in range(batch):
        for _ in range(nb):
            f0 = torch.randint(0, F - block + 1, (1,), generator=g).item()
            t0 = torch.randint(0, T_E - block + 1, (1,), generator=g).item()
            m[b, f0:f0 + block, t0:t0 + block] = 1.0
    return m.bool()


def mask_input(mask):
    mi = Fn.interpolate(mask.float()[:, None], size=(F, T_IN), mode="nearest")[:, 0]
    return mi > 0.5


class Head(nn.Module):
    def __init__(self, out_ch):
        super().__init__()
        self.mask_token = nn.Parameter(torch.zeros(1, C, 1, 1))
        self.net = nn.Sequential(
            nn.Conv2d(C, C, 3, padding=1, dilation=1), nn.GELU(),
            nn.Conv2d(C, C, 3, padding=2, dilation=2), nn.GELU(),
            nn.Conv2d(C, C, 3, padding=4, dilation=4), nn.GELU())
        self.out = nn.Conv2d(C, out_ch, 1)

    def forward(self, z, mask):
        m = mask.float()[:, None]
        z = z * (1 - m) + self.mask_token * m
        return self.out(self.net(z))


class EMA:
    def __init__(self, model, decay=0.996):
        self.ema = copy.deepcopy(model).eval()
        for p in self.ema.parameters():
            p.requires_grad_(False)
        self.decay = decay

    @torch.no_grad()
    def update(self, model):
        for e, p in zip(self.ema.parameters(), model.parameters()):
            e.mul_(self.decay).add_(p, alpha=1 - self.decay)


def encode8_gpu(enc, x, chunk=64):
    if enc is None:
        return R.encode8(None, x)
    n, m, c, f, t = x.shape
    rows = x.reshape(n * m, c, f, t)
    outs = []
    with torch.no_grad():
        for i in range(0, len(rows), chunk):
            outs.append(enc(rows[i:i + chunk].to(DEVICE)).cpu())
    z = torch.cat(outs, 0)
    return z.reshape(n, m, z.shape[1], z.shape[2], z.shape[3])


def eval_model(enc, fit, ev, pairs):
    xf = torch.stack((fit["obs"].real, fit["obs"].imag), dim=2) / R.SCALE
    xe = torch.stack((ev["obs"].real, ev["obs"].imag), dim=2) / R.SCALE
    zf = encode8_gpu(enc, xf)
    ze = encode8_gpu(enc, xe)
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
    return H.summarize(acc, ev, pairs)


def loss_batch(objective, E, head, ema, x, mask, mi):
    xm = x * (~mi).float()[:, None]
    z = E(xm)
    if objective == "recon":
        out = head(z, mask)
        out = Fn.interpolate(out, size=(F, T_IN), mode="bilinear", align_corners=False)
        op = out.permute(0, 2, 3, 1)
        xp = x.permute(0, 2, 3, 1)
        return Fn.mse_loss(op[mi], xp[mi])
    with torch.no_grad():
        tgt = ema.ema(x).permute(0, 2, 3, 1)
        tgt = Fn.layer_norm(tgt, (C,))
    pred = head(z, mask).permute(0, 2, 3, 1)
    loss = Fn.mse_loss(pred[mask], tgt[mask])
    std = pred[mask].std(0).mean()
    return loss + 0.01 * Fn.relu(1.0 - std)


def train_one(objective, seed, train_x, val_x, steps, batch):
    torch.manual_seed(seed)
    E = b.MODELS["hybrid_small"]().to(DEVICE)
    head = Head(C if objective == "jepa" else 2).to(DEVICE)
    ema = EMA(E) if objective == "jepa" else None
    opt = torch.optim.AdamW(list(E.parameters()) + list(head.parameters()), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator().manual_seed(seed)
    vm = block_mask_batch(batch, 777)
    vmi = mask_input(vm)
    vx = val_x[:batch].to(DEVICE) / R.SCALE
    vm = vm.to(DEVICE)
    vmi = vmi.to(DEVICE)
    traces = []
    torch.cuda.reset_peak_memory_stats() if DEVICE == "cuda" else None
    t0 = time.time()
    for step in range(steps):
        idx = torch.randint(0, len(train_x), (batch,), generator=g)
        x = train_x[idx].to(DEVICE) / R.SCALE
        mask = block_mask_batch(batch, seed * 100000 + step).to(DEVICE)
        mi = mask_input(mask).to(DEVICE)
        loss = loss_batch(objective, E, head, ema, x, mask, mi)
        assert torch.isfinite(loss), (objective, seed, step)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        assert all(torch.isfinite(p.grad).all() for p in E.parameters())
        torch.nn.utils.clip_grad_norm_(list(E.parameters()) + list(head.parameters()), 1.0)
        opt.step()
        if ema is not None:
            ema.update(E)
        if step % 100 == 0 or step == steps - 1:
            traces.append([step + 1, float(loss.detach())])
    E.eval()
    head.eval()
    with torch.no_grad():
        vloss = float(loss_batch(objective, E, head, ema, vx, vm, vmi))
        z = E(vx)
        feat_std = float(z.std().cpu())
        rank = int(torch.linalg.matrix_rank(z.reshape(z.shape[0], -1) - z.reshape(z.shape[0], -1).mean(0)).cpu())
    peak = int(torch.cuda.max_memory_allocated()) if DEVICE == "cuda" else 0
    seconds = time.time() - t0
    return E, {"objective": objective, "seed": seed, "steps": steps,
               "train_loss_last": traces[-1][1], "val_loss": vloss,
               "feature_std": feat_std, "feature_rank": rank,
               "seconds": round(seconds, 2), "peak_bytes": peak,
               "loss_trace": traces}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(TRAIN / "out"))
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--objectives", default="recon,jepa")
    ap.add_argument("--seeds", default="101,202,303")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    objectives = tuple(s.strip() for s in args.objectives.split(",") if s.strip())
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    steps = 30 if args.quick else args.steps
    n_train = 64 if args.quick else 1365
    n_val = 8 if args.quick else 170
    n_fit = 64 if args.quick else 512
    n_eval = 64 if args.quick else 256

    res = json.loads((R.PILOT / "results.json").read_text())
    R.SCALE = float(res["scale_train_only"])
    cuda_ok = torch.cuda.is_available()
    assert cuda_ok, "CUDA is required for this pilot"

    # Resource preflight.
    batch = 16
    m0 = b.MODELS["hybrid_small"]().to(DEVICE)
    x0 = torch.randn(batch, 2, F, T_IN, device=DEVICE)
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    y = m0(x0)
    y.square().mean().backward()
    torch.cuda.synchronize()
    preflight = {"batch": batch, "seconds": round(time.time() - t0, 3),
                 "peak_bytes": int(torch.cuda.max_memory_allocated()),
                 "out_shape": list(y.shape)}
    del m0, x0, y

    t_data = time.time()
    train_obs = gen_split(8105, H.ENV_FIT, n_train, [0, 5, 10])
    val_obs = gen_split(8106, H.ENV_FIT, n_val, [0, 5, 10])
    train_x = obs_to_reim(train_obs)
    val_x = obs_to_reim(val_obs)
    fit = H.gen_hard(n_fit, 8103, H.ENV_FIT, "mp_cal", 10)
    ev10 = H.gen_hard(n_eval, 8102, H.ENV_EVAL, "mp_cal", 10)
    ev0 = H.gen_hard(n_eval, 8102, H.ENV_EVAL, "mp_cal", 0)
    data_seconds = round(time.time() - t_data, 2)

    checks = {
        "gpu_available": cuda_ok,
        "train_val_disjoint": 8105 != 8106,
        "fit_eval_disjoint": 8103 != 8102,
        "test_not_used": 8104 not in (8105, 8106, 8103, 8102),
        "env_disjoint": set(H.ENV_FIT).isdisjoint(H.ENV_EVAL),
        "mask_zeroed": None,
        "ema_no_grad": None,
    }
    # Mask canary: masked coefficients are exactly zero and insensitive to hidden content.
    xb = train_x[:4].to(DEVICE) / R.SCALE
    mb = block_mask_batch(4, 123).to(DEVICE)
    mib = mask_input(mb).to(DEVICE)
    xa = xb * (~mib).float()[:, None]
    xc = (xb + mib[:, None].float()) * (~mib).float()[:, None]
    checks["mask_zeroed"] = bool(torch.equal(xa, xc) and (xa.permute(0, 2, 3, 1)[mib] == 0).all())
    e0 = b.MODELS["hybrid_small"]().to(DEVICE)
    checks["ema_no_grad"] = bool(all(not p.requires_grad for p in EMA(e0).ema.parameters()))

    meta = {"device": DEVICE, "gpu": torch.cuda.get_device_name(0),
            "torch": torch.__version__, "numpy": np.__version__,
            "scale": R.SCALE, "steps": steps, "batch": batch,
            "objectives": objectives, "seeds": seeds,
            "split": {"train": 8105, "val": 8106, "readout": 8103,
                      "eval": 8102, "test": 8104, "test_used": False},
            "preflight": preflight, "data_seconds": data_seconds,
            "script_sha256": R.sha256(__file__),
            "checks": checks}

    pairs = [(i, j) for i in range(M) for j in range(i + 1, M)]
    rows = []
    evals = {}
    for objective in objectives:
        for seed in seeds:
            E, row = train_one(objective, seed, train_x, val_x, steps, batch)
            row["eval"] = {}
            for tag, ev in (("mp_cal_10", ev10), ("mp_cal_0", ev0)):
                row["eval"][tag] = eval_model(E, fit, ev, pairs)
            rows.append(row)
            evals[f"{objective}:{seed}"] = row["eval"]
            wdir = Path.home() / ".cache/hydroacoustic-doa/multipath-pilot-20261022"
            wdir.mkdir(parents=True, exist_ok=True)
            wpath = wdir / f"{objective}-{seed}.pt"
            torch.save({"encoder": E.state_dict(), "config": meta}, wpath)
            row["weight_path"] = str(wpath)
            row["weight_sha256"] = R.sha256(wpath)
            (out / "results.json").write_text(json.dumps(
                {"meta": meta, "rows": rows, "evals": evals}, indent=2) + "\n")
            print(f"{objective}:{seed} done val={row['val_loss']:.4f} "
                  f"std={row['feature_std']:.4f} rank={row['feature_rank']}", flush=True)

    refs = {"untrained": {}, "raw": {}, "oracle": {}, "raw_phase_slope": {}}
    for seed in seeds:
        R.seed_cpu(seed)
        E = b.MODELS["hybrid_small"]().to(DEVICE)
        refs["untrained"][str(seed)] = {
            "mp_cal_10": eval_model(E, fit, ev10, pairs),
            "mp_cal_0": eval_model(E, fit, ev0, pairs)}
    refs["raw"] = {"mp_cal_10": eval_model(None, fit, ev10, pairs),
                   "mp_cal_0": eval_model(None, fit, ev0, pairs)}
    for tag, ev in (("mp_cal_10", ev10), ("mp_cal_0", ev0)):
        refs["oracle"][tag] = H.oracle(ev, pairs)
        refs["raw_phase_slope"][tag] = H.raw_phase_slope(ev, pairs)

    payload = {"meta": meta, "rows": rows, "evals": evals, "refs": refs}
    (out / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"out": str(out), "checks": checks,
                      "preflight": preflight}, indent=2), flush=True)


if __name__ == "__main__":
    main()
