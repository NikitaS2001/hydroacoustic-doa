"""Stable paths for new experiment bundles."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "experiments/encoder_phase_pilot"
CACHE = Path.home() / ".cache/hydroacoustic-doa"
