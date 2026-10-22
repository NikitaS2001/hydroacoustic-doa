"""Per-bin phase readout and angular metrics for new E experiments."""
import numpy as np
import torch

from .generators import FREQS
from .models import b

M = 8
TAUS_US = np.arange(-130.0, 130.0001, 0.25)


def targets(u):
    u = np.asarray(u, dtype=np.float64)
    return {(i, j): (i - j) * b.CFG["d"] * u / b.CFG["c"] * 1e6
            for i in range(M) for j in range(i + 1, M)}


def slope(preds, max_sep=7):
    num = 0.0
    den = 0.0
    for (i, j), p in preds.items():
        if abs(i - j) > max_sep:
            continue
        num = num + (i - j) * p
        den += (i - j) ** 2
    return (num / den) * b.CFG["c"] / b.CFG["d"] * 1e-6


def basic(err):
    err = np.asarray(err, dtype=np.float64)
    if err.size == 0:
        return {"n": 0, "median": None, "p95": None, "mean": None}
    return {"n": int(err.size), "median": float(np.median(err)),
            "p95": float(np.percentile(err, 95)), "mean": float(np.mean(err))}


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


def per_bin_feats(z, i, j):
    """z: (n,M,C,F,T) -> (n,F,C*C) cross-product features."""
    n, m, c, f, t = z.shape
    cross = torch.einsum("ncft,ndft->nfcd", z[:, i], z[:, j]) / t
    return cross.reshape(n, f, c * c).cpu().numpy()


def phase_from_Z(Z, i, j):
    """Z: (n,M,F,T) complex -> (n,F) phase of the mean cross-spectrum."""
    g = Z[:, i] * torch.conj(Z[:, j])
    return torch.angle(g.mean(-1)).cpu().numpy()


def fit_phase(feat, phi):
    target = np.column_stack((np.cos(phi), np.sin(phi)))
    return b.probe_fit(feat, target)


def predict_phase(probe, feat):
    pred = b.probe_apply(probe, feat)
    return np.arctan2(pred[:, 1], pred[:, 0])


def phase_to_tau(phi):
    """phi: (n,F) -> (tau_us, boundary_flag) via grid search."""
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
    return np.abs(np.angle(np.exp(1j * (phi_hat - phi_true))))


def fmt_err(err):
    err = np.asarray(err, dtype=np.float64).ravel()
    if err.size == 0:
        return {"n": 0, "median": None, "p95": None}
    return {"n": int(err.size), "median": float(np.median(err)),
            "p95": float(np.percentile(err, 95))}


def summarize(acc, ev, pairs):
    preds = {p: v["tau"] for p, v in acc.items()}
    true_tau = targets(ev["u"])
    u1 = u_metrics(slope(preds, 1), ev["u"])
    u7 = u_metrics(slope(preds, 7), ev["u"])
    perr = np.concatenate([v["perr"] for v in acc.values()])
    boundary = float(np.mean([v["bound"].mean() for v in acc.values()]))
    pair_med = {f"{i}-{j}": float(np.median(np.abs(v["tau"] - true_tau[(i, j)])))
                for (i, j), v in acc.items()}
    return {"u_k1": u1, "u_k7": u7, "pair_median_tdoa_us": pair_med,
            "phase_err_rad": fmt_err(perr), "boundary_fraction": boundary,
            "n_pairs": len(preds)}
