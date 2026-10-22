"""Model registry and encoder-pilot configuration shared by new experiments."""
import sys

import torch

from .paths import PILOT

if str(PILOT) not in sys.path:
    sys.path.insert(0, str(PILOT))

import benchmark as b  # noqa: E402

# Data generation in the new generators is CPU-first; training code moves tensors.
b.DEVICE = "cpu"

MODELS = b.MODELS
CFG = b.CFG


def seed_cpu(value):
    torch.manual_seed(value)


def set_data_device(device):
    """Set the device used by benchmark wave/STFT helpers for generated data."""
    b.DEVICE = device
