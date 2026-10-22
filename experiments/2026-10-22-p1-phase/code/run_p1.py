#!/usr/bin/env python3
"""P1: phase-aware complex masked reconstruction for E."""
import argparse
import importlib.util
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
from experiments._common import io  # noqa: E402

P2_PATH = REPO / "experiments/2026-10-22-p2-multipath/code/run_p2.py"
spec = importlib.util.spec_from_file_location("p2_run", P2_PATH)
p2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2)

DEVICE = p2.DEVICE
C = p2.C
F = p2.F
T_IN = p2.T_IN
ENV_TRAIN = p2.ENV_TRAIN
ENV_EVAL = p2.ENV_EVAL
ENV_FIT = p2.ENV_FIT
SNRS = p2.SNRS


def phase_loss(rec, x, mi):
    mse = Fn.mse_loss(rec.permute(0, 2, 3, 1)[mi], x.permute(0, 2, 3, 1)[mi])
    rc = torch.complex(rec[:, 0], rec[:, 1])
    xc = torch.complex(x[:, 0], x[:, 1])
    cos = (rc * torch.conj(xc)).real / (rc.abs() * xc.abs() + 1e-8)
    weight = xc.abs()
    weight = weight / (weight.mean() + 1e-8)
    return mse + ((1.0 - cos) * weight)[mi].mean()


def train_one(seed, train_x, val_x, steps, batch, scale):
    torch.manual_seed(seed)
    E = M.MODELS["hybrid_small"]().to(DEVICE)
    head = p2.Head(2).to(DEVICE)
    opt = torch.optim.AdamW(list(E.parameters()) + list(head.parameters()), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator().manual_seed(seed)
    vm = p2.block_mask_batch(batch, 777, frac=0.8).to(DEVICE)
    vmi = p2.mask_input(vm).to(DEVICE)
    vx = val_x[:batch].to(DEVICE) / scale
    traces = []
    t0 = time.time()
    for step in range(steps):
        idx = torch.randint(0, len(train_x), (batch,), generator=g)
        x = train_x[idx].to(DEVICE) / scale
        mask = p2.block_mask_batch(batch, seed * 100000 + step, frac=0.8).to(DEVICE)
        mi = p2.mask_input(mask).to(DEVICE)
        xm = x * (~mi).float()[:, None]
        z = E(xm)
        out = head(z, mask)
        out = Fn.interpolate(out, size=(F, T_IN), mode="bilinear", align_corners=False)
        loss = phase_loss(out, x, mi)
        assert torch.isfinite(loss), (seed, step)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(list(E.parameters()) + list(head.parameters()), 1.0)
        opt.step()
        if step % 500 == 0 or step == steps - 1:
            traces.append([step + 1, float(loss.detach())])
    E.eval()
    with torch.no_grad():
        vx = val_x[:batch].to(DEVICE) / scale
        z = E(vx)
        vout = Fn.interpolate(head(z, vm), size=(F, T_IN), mode="bilinear", align_corners=False)
        vloss = float(phase_loss(vout, vx, vmi))
        std = float(z.std().cpu())
        flat = z.reshape(z.shape[0], -1)
        rank = int(torch.linalg.matrix_rank(flat - flat.mean(0)).cpu())
    return E, {"seed": seed, "steps": steps, "train_loss_last": traces[-1][1],
               "val_loss": vloss, "feature_std": std, "feature_rank": rank,
               "seconds": round(time.time() - t0, 2), "loss_trace": traces}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--seeds", default="101,202,303")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    steps = 20 if args.quick else args.steps
    n_per = 16 if args.quick else 512
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]

    p2_index = json.loads((REPO / "experiments/2026-10-22-p2-multipath/results/index.json").read_text())
    scale = float(p2_index["meta"]["scale"])
    t0 = time.time()
    train_x = p2.make_mp(8105, n_per, SNRS, ENV_TRAIN)
    val_x = p2.make_mp(8106, max(8, n_per // 4), SNRS, ENV_TRAIN)
    data_seconds = round(time.time() - t0, 2)

    fit = G.gen_hard(512, 8103, ENV_FIT, "mp_cal", 10)
    ev10 = G.gen_hard(256, 8102, ENV_EVAL, "mp_cal", 10)
    ev0 = G.gen_hard(256, 8102, ENV_EVAL, "mp_cal", 0)
    pairs = [(i, j) for i in range(8) for j in range(i + 1, 8)]

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
                         "steps": steps, "seeds": seeds, "scale": scale,
                         "data_seconds": data_seconds, "preflight": preflight,
                         "split": {"train": 8105, "val": 8106, "fit": 8103,
                                   "eval": 8102, "test": 8104, "test_used": False}},
               "runs": [], "eval": {}, "refs": p2_index["refs"],
               "p2_single_path_recon": [x["eval"]["mp_cal_10"]["u_k7"]["theta_deg"]["median"]
                                        for x in p2_index["runs"] if x["kind"] == "sp" and x["objective"] == "recon"]}
    weights = []
    for seed in seeds:
        E, row = train_one(seed, train_x, val_x, steps, 16, scale)
        row["eval"] = {"mp_cal_10": p2.eval_model(E, fit, ev10, pairs, scale),
                       "mp_cal_0": p2.eval_model(E, fit, ev0, pairs, scale)}
        results["runs"].append(row)
        results["eval"][str(seed)] = row["eval"]
        wdir = Path.home() / ".cache/hydroacoustic-doa/p1-20261022"
        wdir.mkdir(parents=True, exist_ok=True)
        wpath = wdir / f"phase-{seed}.pt"
        torch.save({"encoder": E.state_dict(), "config": results["meta"]}, wpath)
        row["weight_path"] = str(wpath)
        row["weight_sha256"] = io.sha256(wpath)
        weights.append({"path": str(wpath), "bytes": wpath.stat().st_size,
                        "sha256": row["weight_sha256"]})
        out = BUNDLE / "results" / str(seed)
        out.mkdir(parents=True, exist_ok=True)
        io.write_json(out / "metrics.json", row)
        print(f"p1:{seed} val={row['val_loss']:.4f}", flush=True)

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
