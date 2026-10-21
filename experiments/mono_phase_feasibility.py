#!/usr/bin/env python3
"""Small NumPy-only narrowband mono-encoder/probe diagnostic; NOT a JEPA/E-M gate.

Run: python3 experiments/mono_phase_feasibility.py > experiments/mono_phase_feasibility.log
Writes the paired JSON next to this file. No source/field data or pretrained weights.
"""
import json
from pathlib import Path
import platform
import numpy as np

FS_HZ = 96000  # contextual nominal rate, no sampled waveform generated
F_HZ = 12000.0
D_M = 0.027
C_MPS = 1500.0
U_MAX = 0.8
N_ENC = 4096
N_PROBE = 4096
N_REPORT = 1024
TRAIN_SNR_DB = 10.0
SNR_REPORT = (None, 0.0, 10.0, 20.0)
SEEDS = {'encoder': 20261002, 'probe': 20261003,
         'report': {str(s): 20261100 + k for k, s in enumerate(SNR_REPORT)}}
PROBE_NORM_FLOOR = 1e-6  # numerical diagnostic only, not DOA output threshold


def wrap(x):
    return np.arctan2(np.sin(x), np.cos(x))


def make_scenes(n, seed, snr_db):
    rng = np.random.default_rng(seed)
    u = rng.uniform(-U_MAX, U_MAX, size=n)
    phi = rng.uniform(-np.pi, np.pi, size=n)
    tau = np.stack((np.zeros(n), D_M * u / C_MPS), axis=1)
    clean = np.exp(1j * (phi[:, None] - 2 * np.pi * F_HZ * tau))
    noise_power = 0.0 if snr_db is None else 10 ** (-snr_db / 10)
    noise = np.sqrt(noise_power / 2) * (rng.standard_normal((n, 2))
                                        + 1j * rng.standard_normal((n, 2)))
    observed = clean + noise
    truth_us = (tau[:, 0] - tau[:, 1]) * 1e6
    truth_phase = -2 * np.pi * F_HZ * (tau[:, 0] - tau[:, 1])
    return {'u': u, 'clean': clean, 'observed': observed,
            'truth_us': truth_us, 'truth_phase': truth_phase}


def ri(z, scale):
    return np.stack((z.real, z.imag), axis=-1) / scale


def fit_linear_denoiser(scenes, scale):
    x = ri(scenes['observed'], scale).reshape(-1, 2)
    y = ri(scenes['clean'], scale).reshape(-1, 2)
    # Same shared 2x2 mapping for all mono channels, learned only on training scenes.
    matrix = np.linalg.solve(x.T @ x, x.T @ y)
    uu, singular, vv = np.linalg.svd(matrix, full_matrices=False)
    rank1 = (uu[:, :1] * singular[:1]) @ vv[:1, :]
    return matrix, rank1, singular


def encode(name, observed, scale, full, rank1, random_matrix):
    x = ri(observed, scale)
    if name == 'raw_reim':
        return x
    if name == 'linear_full':
        return x @ full
    if name == 'linear_rank1':
        return x @ rank1
    if name == 'random_real':
        return x @ random_matrix
    if name == 'magnitude_only':
        return np.stack((np.linalg.norm(x, axis=-1), np.zeros(x.shape[:2])), axis=-1)
    raise ValueError(name)


def pair_features(z):
    # Fixed low-capacity, identical probe interface for all representations.
    # Products are all 2x2 bilinear terms of separately encoded channels.
    a, b = z[:, 0], z[:, 1]
    return np.einsum('ni,nj->nij', a, b).reshape(len(z), 4)


def fit_probe(features, truth_phase):
    x = np.column_stack((np.ones(len(features)), features))
    target = np.column_stack((np.cos(truth_phase), np.sin(truth_phase)))
    cov = x.T @ x
    ridge = 1e-3 * np.trace(cov[1:, 1:]) / 4
    reg = np.diag([0.0, ridge, ridge, ridge, ridge])
    return np.linalg.solve(cov + reg, x.T @ target)


def evaluate(features, probe, scenes):
    x = np.column_stack((np.ones(len(features)), features))
    predicted = x @ probe
    norm = np.linalg.norm(predicted, axis=1)
    valid = np.isfinite(norm) & (norm > PROBE_NORM_FLOOR)
    phase = np.arctan2(predicted[:, 1], predicted[:, 0])
    pred_us = -phase / (2 * np.pi * F_HZ) * 1e6
    err_phase = np.abs(wrap(phase[valid] - scenes['truth_phase'][valid]))
    err_tdoa = np.abs(pred_us[valid] - scenes['truth_us'][valid])
    return {'n': int(len(features)), 'valid': int(valid.sum()),
            'median_phase_error_rad_valid': float(np.median(err_phase)) if valid.any() else None,
            'p95_phase_error_rad_valid': float(np.percentile(err_phase, 95)) if valid.any() else None,
            'median_signed_tdoa_abs_error_us_valid': float(np.median(err_tdoa)) if valid.any() else None,
            'p95_signed_tdoa_abs_error_us_valid': float(np.percentile(err_tdoa, 95)) if valid.any() else None}


def checks():
    assert D_M * U_MAX / C_MPS * 1e6 < 1e6 / (2 * F_HZ)
    for u in (-0.6, 0.0, 0.6):
        tau0, tau1 = 0, D_M * u / C_MPS
        z0, z1 = np.exp(-2j * np.pi * F_HZ * tau0), np.exp(-2j * np.pi * F_HZ * tau1)
        phase = np.angle(z0 * z1.conjugate())
        recovered = -phase / (2 * np.pi * F_HZ)
        assert abs(recovered - (tau0 - tau1)) < 1e-13
        assert abs(wrap(phase + 2 * np.pi * F_HZ * (tau0 - tau1))) < 1e-12
    assert len(set((SEEDS['encoder'], SEEDS['probe'], *SEEDS['report'].values()))) == 6
    clean = make_scenes(5, 151, None)
    assert np.max(np.abs(clean['observed'] - clean['clean'])) == 0
    assert np.allclose(np.abs(clean['clean']), 1)
    assert np.all(np.isfinite(pair_features(ri(clean['observed'], 1))))
    return ['adjacent-tone-unambiguous-on-declared-sector', 'signed-phase-for-u-negative-zero-positive',
            'disjoint-seeds', 'clean-identity', 'finite-pair-features']


def main():
    passed = checks()
    encoder_train = make_scenes(N_ENC, SEEDS['encoder'], TRAIN_SNR_DB)
    probe_fit = make_scenes(N_PROBE, SEEDS['probe'], TRAIN_SNR_DB)
    # Single shared positive scale from training only, across sensors and Re/Im.
    scale = float(np.sqrt(np.mean(np.abs(encoder_train['observed']) ** 2)))
    assert scale > 0
    full, rank1, singular = fit_linear_denoiser(encoder_train, scale)
    rng = np.random.default_rng(20261234)
    random_matrix = rng.normal(size=(2, 2)) / np.sqrt(2)
    names = ('raw_reim', 'linear_full', 'linear_rank1', 'random_real', 'magnitude_only')
    probes = {}
    for name in names:
        features = pair_features(encode(name, probe_fit['observed'], scale, full, rank1, random_matrix))
        probes[name] = fit_probe(features, probe_fit['truth_phase'])
    results = {}
    for snr in SNR_REPORT:
        label = 'clean' if snr is None else f'{int(snr)}_db'
        scenes = make_scenes(N_REPORT, SEEDS['report'][str(snr)], snr)
        results[label] = {}
        for name in names:
            feats = pair_features(encode(name, scenes['observed'], scale, full, rank1, random_matrix))
            results[label][name] = evaluate(feats, probes[name], scenes)
    result = {
        'status': 'narrowband-linear-diagnostic-only; not trained JEPA/CNN/Conformer or frozen-E gate',
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'assumptions': {'f_hz': F_HZ, 'fs_context_only_hz': FS_HZ, 'pitch_m_assumed': D_M,
                        'sound_speed_mps_assumed': C_MPS, 'u_max': U_MAX,
                        'train_snr_db': TRAIN_SNR_DB, 'n_encoder_scenes': N_ENC,
                        'n_probe_scenes': N_PROBE, 'n_report_scenes_per_snr': N_REPORT,
                        'one_shared_amplitude_scale': scale, 'noise_power_definition': 'E|noise|^2=10^(-SNR_dB/10)',
                        'probe_norm_floor_numerical_only': PROBE_NORM_FLOOR, 'seeds': SEEDS},
        'checks': passed,
        'learned_mono_linear_matrix': full.tolist(), 'rank1_matrix': rank1.tolist(),
        'full_matrix_singular_values': singular.tolist(),
        'fixed_random_matrix': random_matrix.tolist(),
        'probe_coefficients': {k: v.tolist() for k, v in probes.items()},
        'results': results,
    }
    out = Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'saved': str(out), 'checks': passed, 'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
