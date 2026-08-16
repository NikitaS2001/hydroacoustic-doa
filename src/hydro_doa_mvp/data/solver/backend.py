"""Solver backend abstraction (ADR-0001/0002).

Contract highlights encoded here:
- 2-D arrivals run type ``A`` only.
- One solver run per sensor at its own radial range ``r_i`` (mandatory; the
  batch receiver-vector mode is a separate, explicitly-flagged code path).
- Deriving one sensor's channel from another by delay/phase shift or
  interpolation is forbidden and has no code path here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class SolverEnv:
    """Range-independent 2-D shallow-water environment (protocol Section 6.2)."""

    depth_m: float
    ssp: np.ndarray  # (n, 2) depth_m, speed_m_s; n >= 4 (arlpy constraint)
    bottom_soundspeed_m_s: float
    bottom_density_kg_m3: float
    bottom_absorption_db_lambda: float
    tx_depth_m: float
    rx_depth_m: float
    min_angle_deg: float = -20.0
    max_angle_deg: float = 20.0
    nbeams: int = 0  # 0 = solver default

    def validate(self) -> None:
        if self.ssp.ndim != 2 or self.ssp.shape[1] != 2 or len(self.ssp) < 4:
            raise ValueError(f"ssp must be (>=4, 2), got {self.ssp.shape}")
        if self.tx_depth_m <= 0 or self.tx_depth_m >= self.depth_m:
            raise ValueError("tx_depth_m must be inside the water column")
        if self.rx_depth_m <= 0 or self.rx_depth_m >= self.depth_m:
            raise ValueError("rx_depth_m must be inside the water column")


@dataclass(frozen=True)
class ArrivalSet:
    """Arrivals for one sensor at one frequency: continuous delays, complex amplitudes."""

    range_m: float
    frequency_hz: float
    delays_s: np.ndarray
    amplitudes: np.ndarray  # complex, includes propagation phase at frequency_hz
    surface_bounces: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=int))
    bottom_bounces: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=int))

    def direct_path_index(self) -> int:
        return int(np.argmin(self.delays_s))

    def validate(self) -> None:
        if self.delays_s.ndim != 1 or self.amplitudes.shape != self.delays_s.shape:
            raise ValueError("delays/amplitudes shape mismatch")
        if not np.all(np.isfinite(self.delays_s)) or np.any(self.delays_s < 0):
            raise ValueError("delays must be finite and nonnegative")
        if not np.all(np.isfinite(self.amplitudes)):
            raise ValueError("amplitudes must be finite")

    def transfer_function(self, freqs_hz: np.ndarray) -> np.ndarray:
        """H(f) = sum_p A_p * exp(-j 2 pi f tau_p) for the single run frequency's amplitudes.

        Only valid at the run frequency by construction of the arrival phases;
        broadband synthesis across frequencies is data/synthesis.py's job.
        """
        f = np.asarray(freqs_hz, dtype=float)
        if not np.allclose(f, self.frequency_hz):
            raise ValueError("arrival amplitudes carry phase at the run frequency only")
        return np.sum(self.amplitudes * np.exp(-1j * 2 * np.pi * f[:, None] * self.delays_s), axis=1)


class SolverBackend(Protocol):
    """Run one 2-D arrivals computation per sensor radial range."""

    name: str

    def run_sensor(
        self, env: SolverEnv, radial_range_m: float, frequency_hz: float
    ) -> ArrivalSet: ...

    def run_config(
        self, env: SolverEnv, radial_ranges_m: Sequence[float], frequency_hz: float
    ) -> list[ArrivalSet]:
        """Per-sensor runs (default mode, ADR-0001): one solver call per sensor."""
        return [self.run_sensor(env, r, frequency_hz) for r in radial_ranges_m]
