#!/usr/bin/env python3
"""Synthetic eight-channel STFT/TDOA sanity test; NOT a hardware or E-encoder test.
Pure NumPy, float64. Save metrics and failed checks to a JSON file.
"""
import json
import sys
from pathlib import Path

import numpy as np

FS = 96_000
D = 0.027
C = 1500.0  # assumed, not measured
N_CH = 8
L = 12_288  # 128 ms
NFFT = 256
HOPS = (64, 128)
UPSAMPLE = 64
BAND = (4_000, 20_000)
OUT = Path(__file__).with_suffix('.json')


def source():
    t = np.arange(4_800) / FS  # 50 ms
    # Linear FM with deterministic continuous phase; 2-ms raised-cosine taper.
    phase = 2 * np.pi * (4_000*t + 0.5*(16_000/.05)*t*t)
    s = np.sin(phase)
    taper = np.ones(len(s))
    r = int(.002*FS)
    taper[:r] = np.sin(np.linspace(0, np.pi/2, r, endpoint=False))**2
    taper[-r:] = np.sin(np.linspace(np.pi/2, 0, r, endpoint=False))**2
    x = np.zeros(L)
    x[2_400:2_400+len(s)] = s*taper  # starts 25 ms into the common record
    return x


def shift(x, tau):
    # Circular Fourier shift is valid here only because both margins have zero energy.
    f = np.fft.rfftfreq(len(x), 1/FS)
    return np.fft.irfft(np.fft.rfft(x)*np.exp(-2j*np.pi*f*tau), n=len(x))


def signals(u, noisy=False):
    x = source()
    loc = D*np.arange(N_CH)
    direct = np.stack([shift(x, d*u/C) for d in loc])
    if not noisy:
        return direct
    echo = np.stack([shift(x, .002 + d*(-.3)/C) for d in loc])
    rng = np.random.default_rng(20260926)
    return direct + .35*echo + .02*rng.standard_normal(direct.shape)


def stft(x, hop):
    win = np.hanning(NFFT+1)[:-1]  # periodic Hann
    starts = np.arange(0, L-NFFT+1, hop)
    frames = np.stack([x[:, k:k+NFFT]*win for k in starts], axis=1)
    return np.fft.rfft(frames, axis=-1), starts, win


def istft(z, starts, win):
    out = np.zeros((z.shape[0], L))
    denom = np.zeros(L)
    frames = np.fft.irfft(z, n=NFFT, axis=-1)
    for n, k in enumerate(starts):
        out[:, k:k+NFFT] += frames[:, n, :]*win
        denom[k:k+NFFT] += win**2
    covered = denom > 1e-12
    out[:, covered] /= denom[covered]
    return out, covered


def gcc_from_cross(cross, freqs, n, up=UPSAMPLE):
    band = (freqs >= BAND[0]) & (freqs <= BAND[1])
    c = np.zeros_like(cross, dtype=complex)
    amp = np.abs(cross)
    c[band] = cross[band] / np.maximum(amp[band], 1e-12*amp[band].max())
    corr = np.fft.irfft(c, n=n*up)
    maxlag = int(np.ceil(.00025*FS*up))  # ±250 us; includes all assumed direct-array TDOAs
    section = np.r_[corr[-maxlag:], corr[:maxlag+1]]
    k = int(np.argmax(section)) - maxlag
    return k/(FS*up)  # positive when first input arrives later than second


def metrics(x, z=None):
    n = L if z is None else NFFT
    freqs = np.fft.rfftfreq(n, 1/FS)
    spectrum = np.fft.rfft(x, axis=-1) if z is None else z
    pairs = [(i, i+1) for i in range(7)] + [(0, 7)]
    out = []
    for i, j in pairs:
        cross = spectrum[i]*np.conj(spectrum[j])
        if z is not None:
            cross = cross.mean(axis=0)
        lag = gcc_from_cross(cross, freqs, n)
        out.append({'pair':[i,j], 'lag_us':lag*1e6})
    if z is not None:
        # Bin 32 is 12 kHz for 96k/256; actual phase in a chirp frame may deviate
        # from a perfectly stationary plane wave.
        k = 32
        cross = (z[0,:,k]*np.conj(z[1,:,k])).sum()
        phase = float(np.angle(cross))
        return out, phase
    return out, None


def wrap(rad):
    return float(np.angle(np.exp(1j*rad)))


def run():
    results = {'assumptions': {'fs_Hz':FS,'n_channels':N_CH,'pitch_m':D,
                'sound_speed_mps_assumed':C,'record_samples':L,'chirp_Hz':list(BAND),
                'chirp_ms':50,'window_samples':NFFT,'hops':list(HOPS),
                'gcc_upsample':UPSAMPLE,'noisy_echo_level':.35,'noisy_std':.02,
                'rng_seed':20260926}, 'cases': [], 'checks': {}}
    for noisy in (False, True):
        for u in (-.6, 0., .6):
            x = signals(u, noisy)
            raw, _ = metrics(x)
            case = {'u':u, 'condition':'echo+white_noise' if noisy else 'direct_only',
                    'raw':raw,'hops':{}}
            for hop in HOPS:
                z, starts, win = stft(x, hop)
                recon, covered = istft(z, starts, win)
                # Exclude uncovered Hann endpoint where direct/echo amplitude is zero.
                rms = float(np.sqrt(np.mean((x[:,covered]-recon[:,covered])**2)) /
                            np.sqrt(np.mean(x[:,covered]**2)))
                pairs, phase = metrics(x, z)
                truth = [D*(i-j)*u/C*1e6 for i,j in [(k,k+1) for k in range(7)]+[(0,7)]]
                case['hops'][str(hop)] = {
                    'frames':len(starts),'coverage_fraction':float(covered.mean()),
                    'inverse_relative_rms':rms,'tf':pairs,
                    'true_tdoa_us':truth,
                    'max_abs_raw_truth_us':float(max(abs(p['lag_us']-t) for p,t in zip(raw,truth))),
                    'max_abs_tf_truth_us':float(max(abs(p['lag_us']-t) for p,t in zip(pairs,truth))),
                    'max_abs_tf_raw_us':float(max(abs(p['lag_us']-q['lag_us']) for p,q in zip(pairs,raw))),
                    'stft_phase_pair_01_at_12k_rad':phase,
                    'expected_phase_pair_01_rad':wrap(-2*np.pi*12_000*D*(0-1)*u/C),
                    'circular_phase_error_rad':abs(wrap(phase+2*np.pi*12_000*D*(0-1)*u/C))}
            results['cases'].append(case)
    ideal=[c for c in results['cases'] if c['condition']=='direct_only']
    results['checks']['inverse_rms_ideal_under_1e-10'] = all(c['hops'][str(h)]['inverse_relative_rms'] < 1e-10 for c in ideal for h in HOPS)
    results['checks']['raw_and_tf_tdoa_ideal_within_5us'] = all(max(c['hops'][str(h)]['max_abs_raw_truth_us'],c['hops'][str(h)]['max_abs_tf_truth_us']) <= 5 for c in ideal for h in HOPS)
    results['checks']['tf_phase_ideal_within_0p2rad'] = all(c['hops'][str(h)]['circular_phase_error_rad'] <= .2 for c in ideal for h in HOPS)
    OUT.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    for case in results['cases']:
        print(case['condition'], 'u', case['u'], 'raw max-us',round(case['hops']['64']['max_abs_raw_truth_us'],3))
        for h in HOPS:
            v=case['hops'][str(h)]
            print('  hop',h,'frames',v['frames'],'inverse_rms',f"{v['inverse_relative_rms']:.3g}",
                  'tf max-us',round(v['max_abs_tf_truth_us'],3),'vs raw max-us',round(v['max_abs_tf_raw_us'],3),
                  'phase_err_rad',round(v['circular_phase_error_rad'],3))
    print('checks',results['checks']);print('saved',OUT)
    return all(results['checks'].values())


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
