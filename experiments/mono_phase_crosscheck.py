#!/usr/bin/env python3
"""Secondary checks for the saved narrowband pilot; no model fit or new claims of physics validation."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent
j = json.loads((ROOT / 'mono_phase_feasibility.json').read_text())
a = j['assumptions']
f = a['f_hz']
assert a['n_report_scenes_per_snr'] == 1024
assert a['seeds']['encoder'] != a['seeds']['probe']
for s in a['seeds']['report'].values():
    assert s not in (a['seeds']['encoder'], a['seeds']['probe'])


def errors(ph, truth):
    circle = np.abs(np.angle(np.exp(1j * (ph - truth))))
    # Signed delay uses the principal-value phase estimate; do not wrap its error.
    us = np.abs(ph - truth) * 1e6 / (2 * np.pi * f)
    return {'median_phase_rad': float(np.median(circle)),
            'p95_phase_rad': float(np.percentile(circle, 95)),
            'median_abs_tdoa_us': float(np.median(us)),
            'p95_abs_tdoa_us': float(np.percentile(us, 95))}


out = {}
for label, snr in [('clean', None), ('0_db', 0), ('10_db', 10), ('20_db', 20)]:
    rng = np.random.default_rng(a['seeds']['report'][str(snr if snr is None else float(snr))])
    u = rng.uniform(-a['u_max'], a['u_max'], a['n_report_scenes_per_snr'])
    phi = rng.uniform(-np.pi, np.pi, len(u))
    tau = np.stack((np.zeros_like(u), a['pitch_m_assumed'] * u / a['sound_speed_mps_assumed']), axis=1)
    truth = 2 * np.pi * f * (tau[:, 1] - tau[:, 0])
    clean = np.exp(1j * (phi[:, None] - 2 * np.pi * f * tau))
    power = 0 if snr is None else 10 ** (-snr / 10)
    noise = np.sqrt(power / 2) * (rng.standard_normal(clean.shape) + 1j * rng.standard_normal(clean.shape))
    obs = clean + noise
    direct_phase = np.angle(obs[:, 0] * np.conj(obs[:, 1]))
    # Analytic clean truth and sign; this does not measure a learned E.
    assert np.max(np.abs(np.angle(clean[:, 0] * np.conj(clean[:, 1]) * np.exp(-1j * truth)))) < 1e-12
    if label == 'clean':
        assert np.max(np.abs(np.angle(np.exp(1j * (direct_phase - truth))))) < 1e-12
    out[label] = {'direct_cross_phase': errors(direct_phase, truth),
                  'predict_zero_delay': errors(np.zeros_like(truth), truth),
                  'mean_signed_truth_us': float(np.mean(-truth / (2 * np.pi * f) * 1e6))}
    # Accuracy from an almost constant predictor can have a deceptively low noisy p95.
    if label == 'clean':
        assert j['results'][label]['magnitude_only']['median_signed_tdoa_abs_error_us_valid'] > 5

# Invertible random real map retains information even when the raw angle of each output coordinate is not physical phase.
assert abs(np.linalg.det(np.asarray(j['fixed_random_matrix']))) > 1e-4
assert np.linalg.matrix_rank(np.asarray(j['rank1_matrix'])) == 1
path = ROOT / 'mono_phase_crosscheck.json'
path.write_text(json.dumps({'checks': ['independent-clean-cross-phase-sign', 'direct-raw-and-zero-delay-controls',
                                      'independent-scene-reconstruction', 'rank-and-random-invertibility'],
                            'results': out}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'saved': str(path), 'results': out}, ensure_ascii=False, indent=2))
