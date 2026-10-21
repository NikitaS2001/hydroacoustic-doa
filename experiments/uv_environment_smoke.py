#!/usr/bin/env python3
"""Small local dependency smoke test. Not encoder training, physics or E gate.
Run with: uv run --locked --offline python experiments/uv_environment_smoke.py
"""
import hashlib
import json
import platform
from pathlib import Path
import traceback

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
TOL = 2e-5


def check_device(device):
    torch.manual_seed(20261002)
    model = torch.nn.Conv2d(2, 4, 3, padding=1).to(device)
    x = torch.randn(2, 2, 17, 9, device=device, requires_grad=True)
    before = model.weight.detach().clone()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    y = model(x)
    assert tuple(y.shape) == (2, 4, 17, 9)
    loss = y.square().mean()
    loss.backward()
    for grad in (x.grad, model.weight.grad, model.bias.grad):
        assert grad is not None and torch.isfinite(grad).all() and grad.norm() > 0
    optimizer.step()
    assert not torch.equal(before, model.weight.detach())

    z = torch.randn(16, dtype=torch.complex64, device=device, requires_grad=True)
    z.abs().square().mean().backward()
    assert torch.isfinite(z.grad).all() and z.grad.abs().sum() > 0

    rng = np.random.default_rng(20261002)
    raw = rng.standard_normal((2, 1024)).astype(np.float32)
    wave = torch.tensor(raw, device=device, requires_grad=True)
    window = torch.hann_window(256, periodic=True, device=device)
    tf = torch.stft(wave, n_fft=256, hop_length=64, win_length=256,
                    window=window, center=False, return_complex=True)
    assert tuple(tf.shape) == (2, 129, 13)
    packed = torch.view_as_real(tf)
    assert torch.equal(torch.view_as_complex(packed), tf)
    # Independent NumPy rFFT on the same explicit unpadded frames and periodic Hann.
    frames = np.stack([raw[:, k:k + 256] for k in range(0, 769, 64)], axis=-1)
    hann = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(256) / 256)
    reference = np.fft.rfft(frames * hann[None, :, None], axis=1)
    observed = tf.detach().cpu().numpy()
    rel = float(np.linalg.norm(observed - reference) / np.linalg.norm(reference))
    assert rel <= TOL, (device, rel, TOL)
    tf.abs().square().mean().backward()
    assert torch.isfinite(wave.grad).all() and wave.grad.norm() > 0
    if device == 'cuda':
        torch.cuda.synchronize()
    return {'status': 'PASS', 'conv_loss_smoke_only': float(loss.detach().cpu()),
            'complex_backward': 'PASS', 'conv_forward_backward_step': 'PASS',
            'stft_shape': list(tf.shape), 'reim_roundtrip': 'PASS',
            'stft_numpy_relative_l2': rel, 'stft_tolerance': TOL,
            'stft_backward': 'PASS'}


def main():
    result = {'status': 'FAIL', 'purpose': 'environment smoke only; not a learned encoder or E gate',
              'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                           'torch': torch.__version__, 'cuda_build': torch.version.cuda},
              'config_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                for p in ('pyproject.toml', 'uv.lock', '.python-version')},
              'devices': {}}
    try:
        assert torch.cuda.is_available(), 'CUDA unavailable; no automatic CPU fallback'
        result['gpu'] = {'name': torch.cuda.get_device_name(0),
                         'total_memory_bytes': torch.cuda.get_device_properties(0).total_memory,
                         'capability': list(torch.cuda.get_device_capability(0))}
        for device in ('cpu', 'cuda'):
            result['devices'][device] = check_device(device)
        result['status'] = 'PASS'
    except Exception:
        result['error'] = traceback.format_exc()
    out = Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
