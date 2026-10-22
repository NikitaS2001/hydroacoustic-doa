"""Synthetic array-data generators shared by new E experiments."""
import numpy as np
import torch

from .models import b, CFG

M = 8
F = 43
T_IN = 1 + (CFG["length"] - CFG["nfft"]) // CFG["hop"]
FREQS = np.arange(11, 54) * CFG["fs"] / CFG["nfft"]


def gen8(n, source_seed, noise_seed, snr, per_source=False):
    """Eight synchronous single-path channels with independent noise per channel."""
    src = b.sources(n, source_seed)
    u = np.asarray(src[2], dtype=np.float64)
    clean = torch.stack([b.wave(src, m * CFG["d"] * u / CFG["c"]) for m in range(M)], dim=1)
    obs = clean.clone()
    if per_source:
        rng = np.random.default_rng(noise_seed)
        values = rng.uniform(0, 20, n).astype(np.float32)
        arg = torch.tensor(values, dtype=torch.float32, device=b.DEVICE).reshape(n, 1)
        for m in range(M):
            obs[:, m] = b.noisy(clean[:, m], arg, noise_seed + m)
    elif isinstance(snr, str):
        pass
    else:
        for m in range(M):
            obs[:, m] = b.noisy(clean[:, m], snr, noise_seed + m)
    return src, clean, obs


def stft8(x):
    """x: (n,M,L) -> (n,M,2,F,T)."""
    n, m, length = x.shape
    z = b.stft(x.reshape(n * m, length))
    return z.reshape(n, m, z.shape[1], z.shape[2], z.shape[3])


def complex_stft8(x):
    """x: (n,M,L) -> (n,M,F,T) complex."""
    z = stft8(x)
    return torch.complex(z[:, :, 0], z[:, :, 1])


def obs_to_reim(obs):
    """(n,M,F,T) complex -> (n*M,2,F,T)."""
    return torch.stack((obs.real, obs.imag), dim=2).reshape(-1, 2, F, T_IN)


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
    cal = env["gain"][:, None] * np.exp(
        1j * (env["phase"][:, None] - 2 * np.pi * FREQS[None, :] * env["skew"][:, None]))
    return torch.tensor(cal, dtype=torch.complex64)


def gen_hard(n, source_seed, env_seeds, condition, snr):
    """Multipath/calibration/interference generator; condition in direct/mp/cal/mp_cal/mp_cal_int."""
    envs = [make_env(seed) for seed in env_seeds]
    src = b.sources(n, source_seed)
    u = np.asarray(src[2], dtype=np.float64)
    env_idx = np.arange(n) % len(envs)
    obs = torch.zeros((n, M, F, T_IN), dtype=torch.complex64)
    direct = torch.zeros_like(obs)
    direct_cal = torch.zeros_like(obs)
    for e, env in enumerate(envs):
        idx = np.where(env_idx == e)[0]
        if idx.size == 0:
            continue
        s = (src[0][idx], src[1][idx], src[2][idx])
        ue = np.asarray(src[2][idx], dtype=np.float64)
        d = torch.stack([b.wave(s, m * CFG["d"] * ue / CFG["c"]) for m in range(M)], dim=1)
        total = d.clone()
        if condition in ("mp", "mp_cal", "mp_cal_int"):
            for p in range(len(env["u_refl"])):
                r = torch.stack([
                    b.wave(s, np.full(len(idx), env["tau_refl"][p] + m * CFG["d"] * env["u_refl"][p] / CFG["c"]))
                    for m in range(M)], dim=1)
                total = total + float(env["amp_refl"][p]) * r
        if condition == "mp_cal_int":
            sint = b.sources(len(idx), source_seed + 1000 + e)
            it = torch.stack([b.wave(sint, np.full(len(idx), m * CFG["d"] * env["u_int"] / CFG["c"]))
                              for m in range(M)], dim=1)
            pd = d.square().mean((1, 2))
            pi = it.square().mean((1, 2))
            a = torch.sqrt(pd / (pi * 10 ** (env["sir_db"] / 10.0)))
            total = total + it * a[:, None, None]
        zt = complex_stft8(total)
        zd = complex_stft8(d)
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
            noise = torch.randn((len(idx), M, CFG["length"]), generator=gen) * torch.sqrt(var)[:, None, None]
            zt = zt + complex_stft8(noise)
        obs[idx] = zt
        direct[idx] = zd
        direct_cal[idx] = zdc
    return {"obs": obs, "direct": direct, "direct_cal": direct_cal, "u": u}
