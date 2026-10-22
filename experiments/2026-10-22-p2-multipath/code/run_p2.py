#!/usr/bin/env python3
"""P2: multipath/domain-randomized E pretraining, frozen phase readout."""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as Fn

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.dont_write_bytecode = True

from experiments._common import generators as G  # noqa: E402
from experiments._common import models as M  # noqa: E402
from experiments._common import readout as R  # noqa: E402
from experiments._common import io  # noqa: E402

M.b.DEVICE = "cpu"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
assert DEVICE == "cuda", "P2 requires CUDA"
torch.set_num_threads(4)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False

C = 16
F = 43
T_E = 15
T_IN = 29
MCH = 8
ENV_TRAIN = [7101, 7102, 7103, 7104, 7105, 7106, 7107, 7108]
ENV_EVAL = [7201, 7202, 7203, 7204]
ENV_FIT = ENV_TRAIN
SNRS = [0, 5, 10]


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
    return loss + 0.01 * Fn.relu(1.0 - pred[mask].std(0).mean())


def make_mp(source_seed, n_per, snrs, envs):
    parts = []
    for snr in snrs:
        h = G.gen_hard(n_per, source_seed, envs, "mp_cal", snr)
        parts.append(h["obs"])
    return G.obs_to_reim(torch.cat(parts, 0))


def make_sp(source_seed, n_per, snrs):
    parts = []
    for k, snr in enumerate(snrs):
        _, _, obs = G.gen8(n_per, source_seed, 9103 + 100 * k, snr)
        parts.append(G.complex_stft8(obs))
    return G.obs_to_reim(torch.cat(parts, 0))


def train_one(kind, objective, seed, train_x, val_x, steps, batch, scale):
    torch.manual_seed(seed)
    E = M.MODELS["hybrid_small"]().to(DEVICE)
    head = Head(C if objective == "jepa" else 2).to(DEVICE)
    ema = EMA(E) if objective == "jepa" else None
    opt = torch.optim.AdamW(list(E.parameters()) + list(head.parameters()), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator().manual_seed(seed)
    vm = block_mask_batch(batch, 777).to(DEVICE)
    vmi = mask_input(vm).to(DEVICE)
    vx = val_x[:batch].to(DEVICE) / scale
    traces = []
    t0 = time.time()
    for step in range(steps):
        idx = torch.randint(0, len(train_x), (batch,), generator=g)
        x = train_x[idx].to(DEVICE) / scale
        mask = block_mask_batch(batch, seed * 100000 + step).to(DEVICE)
        mi = mask_input(mask).to(DEVICE)
        loss = loss_batch(objective, E, head, ema, x, mask, mi)
        assert torch.isfinite(loss), (kind, objective, seed, step)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(list(E.parameters()) + list(head.parameters()), 1.0)
        opt.step()
        if ema is not None:
            ema.update(E)
        if step % 500 == 0 or step == steps - 1:
            traces.append([step + 1, float(loss.detach())])
    E.eval()
    with torch.no_grad():
        vloss = float(loss_batch(objective, E, head, ema, vx, vm, vmi))
        z = E(vx)
        std = float(z.std().cpu())
        flat = z.reshape(z.shape[0], -1)
        rank = int(torch.linalg.matrix_rank(flat - flat.mean(0)).cpu())
    return E, {"kind": kind, "objective": objective, "seed": seed,
               "steps": steps, "train_loss_last": traces[-1][1], "val_loss": vloss,
               "feature_std": std, "feature_rank": rank,
               "seconds": round(time.time() - t0, 2),
               "loss_trace": traces}


def encode8(enc, x, chunk=64):
    n, m, c, f, t = x.shape
    rows = x.reshape(n * m, c, f, t)
    if enc is None:
        z = M.b.encoded(None, rows)
    else:
        outs = []
        with torch.no_grad():
            for i in range(0, len(rows), chunk):
                outs.append(enc(rows[i:i + chunk].to(DEVICE)).cpu())
        z = torch.cat(outs, 0)
    return z.reshape(n, m, z.shape[1], z.shape[2], z.shape[3])


def eval_model(enc, fit, ev, pairs, scale):
    xf = torch.stack((fit["obs"].real, fit["obs"].imag), dim=2) / scale
    xe = torch.stack((ev["obs"].real, ev["obs"].imag), dim=2) / scale
    zf = encode8(enc, xf)
    ze = encode8(enc, xe)
    acc = {}
    for (i, j) in pairs:
        ff = R.per_bin_feats(zf, i, j)
        fe = R.per_bin_feats(ze, i, j)
        phif = R.phase_from_Z(fit["direct"], i, j)
        phie = R.phase_from_Z(ev["direct"], i, j)
        phihat = np.column_stack([
            R.predict_phase(R.fit_phase(ff[:, f], phif[:, f]), fe[:, f])
            for f in range(F)])
        tau, bound = R.phase_to_tau(phihat)
        perr = R.phase_err(phihat, phie).mean(1)
        acc[(i, j)] = {"tau": tau, "bound": bound, "perr": perr}
    return R.summarize(acc, ev, pairs)


def refs_for(ev, pairs):
    preds = {p: R.phase_to_tau(R.phase_from_Z(ev["direct"], *p))[0] for p in pairs}
    oracle = {"u_k1": R.u_metrics(R.slope(preds, 1), ev["u"]),
              "u_k7": R.u_metrics(R.slope(preds, 7), ev["u"])}
    preds = {p: R.phase_to_tau(R.phase_from_Z(ev["obs"], *p))[0] for p in pairs}
    raw_slope = {"u_k1": R.u_metrics(R.slope(preds, 1), ev["u"]),
                 "u_k7": R.u_metrics(R.slope(preds, 7), ev["u"])}
    return {"oracle": oracle, "raw_phase_slope": raw_slope}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--seeds", default="101,202,303")
    ap.add_argument("--objectives", default="recon,jepa")
    ap.add_argument("--kinds", default="mp,sp")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    steps = 20 if args.quick else args.steps
    n_per = 16 if args.quick else 512
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    objectives = [s.strip() for s in args.objectives.split(",") if s.strip()]
    kinds = [s.strip() for s in args.kinds.split(",") if s.strip()]

    t0 = time.time()
    train_mp = make_mp(8105, n_per, SNRS, ENV_TRAIN)
    train_sp = make_sp(8105, n_per, SNRS)
    val_mp = make_mp(8106, max(8, n_per // 4), SNRS, ENV_TRAIN)
    val_sp = make_sp(8106, max(8, n_per // 4), SNRS)
    scale = float(torch.sqrt(torch.mean(train_mp.square())))
    data_seconds = round(time.time() - t0, 2)

    fit = G.gen_hard(512, 8103, ENV_FIT, "mp_cal", 10)
    ev10 = G.gen_hard(256, 8102, ENV_EVAL, "mp_cal", 10)
    ev0 = G.gen_hard(256, 8102, ENV_EVAL, "mp_cal", 0)
    pairs = [(i, j) for i in range(MCH) for j in range(i + 1, MCH)]

    # Resource preflight.
    m0 = M.MODELS["hybrid_small"]().to(DEVICE)
    x0 = torch.randn(16, 2, F, T_IN, device=DEVICE)
    torch.cuda.reset_peak_memory_stats()
    p0 = time.time()
    m0(x0).square().mean().backward()
    torch.cuda.synchronize()
    preflight = {"seconds": round(time.time() - p0, 3),
                 "peak_bytes": int(torch.cuda.max_memory_allocated())}
    del m0, x0

    results = {"meta": {"device": DEVICE, "gpu": torch.cuda.get_device_name(0),
                         "steps": steps, "seeds": seeds, "objectives": objectives,
                         "kinds": kinds, "scale": scale, "data_seconds": data_seconds,
                         "preflight": preflight,
                         "split": {"train": 8105, "val": 8106, "fit": 8103,
                                   "eval": 8102, "test": 8104, "test_used": False},
                         "train_envs": ENV_TRAIN, "eval_envs": ENV_EVAL},
               "runs": [], "eval": {}, "refs": {}}
    weights = []
    for kind in kinds:
        tr = train_mp if kind == "mp" else train_sp
        va = val_mp if kind == "mp" else val_sp
        for objective in objectives:
            for seed in seeds:
                E, row = train_one(kind, objective, seed, tr, va, steps, 16, scale)
                row["eval"] = {
                    "mp_cal_10": eval_model(E, fit, ev10, pairs, scale),
                    "mp_cal_0": eval_model(E, fit, ev0, pairs, scale)}
                row["kind_objective_seed"] = f"{kind}:{objective}:{seed}"
                results["runs"].append(row)
                results["eval"][row["kind_objective_seed"]] = row["eval"]
                wdir = Path.home() / ".cache/hydroacoustic-doa/p2-20261022"
                wdir.mkdir(parents=True, exist_ok=True)
                wpath = wdir / f"{kind}-{objective}-{seed}.pt"
                torch.save({"encoder": E.state_dict(), "config": results["meta"]}, wpath)
                row["weight_path"] = str(wpath)
                row["weight_sha256"] = io.sha256(wpath)
                weights.append({"path": str(wpath), "bytes": wpath.stat().st_size,
                                "sha256": row["weight_sha256"]})
                out = BUNDLE / "results" / row["kind_objective_seed"]
                out.mkdir(parents=True, exist_ok=True)
                io.write_json(out / "metrics.json", row)
                print(f"{row['kind_objective_seed']} val={row['val_loss']:.4f}", flush=True)

    # Controls: untrained, single-path best already in runs; raw readout.
    controls = {}
    for seed in seeds:
        M.seed_cpu(seed)
        E = M.MODELS["hybrid_small"]().to(DEVICE)
        controls[f"untrained:{seed}"] = {
            "mp_cal_10": eval_model(E, fit, ev10, pairs, scale),
            "mp_cal_0": eval_model(E, fit, ev0, pairs, scale)}
    controls["raw_perbin"] = {
        "mp_cal_10": eval_model(None, fit, ev10, pairs, scale),
        "mp_cal_0": eval_model(None, fit, ev0, pairs, scale)}
    results["refs"] = {"untrained": controls,
                       "oracle_raw": {"mp_cal_10": refs_for(ev10, pairs),
                                      "mp_cal_0": refs_for(ev0, pairs)}}
    io.write_json(BUNDLE / "results" / "index.json", results)
    io.write_json(BUNDLE / "weights_manifest.json", {"weights": weights})
    checks = {
        "cuda": True,
        "test_not_used": 8104 not in (8105, 8106, 8103, 8102),
        "env_disjoint": set(ENV_TRAIN).isdisjoint(ENV_EVAL),
        "weights_sha": all(io.sha256(w["path"]) == w["sha256"] for w in weights),
        "runs": len(results["runs"]),
        "feature_rank_min": min(r["feature_rank"] for r in results["runs"]),
    }
    io.write_json(BUNDLE / "checks.json", checks)
    bundle = io.read_json(BUNDLE / "bundle.json")
    bundle["status"] = "completed"
    io.write_json(BUNDLE / "bundle.json", bundle)
    print(json.dumps({"bundle": str(BUNDLE), "checks": checks,
                      "wall_seconds": round(time.time() - t0, 2)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
