"""arlpy-driven backend: arlpy.uwapm -> bellhopcuda via venv-bin symlink (ADR-0002).

Integration facts established by the stage-1 spike:
- arlpy invokes the solver as ``bellhop.exe`` with ``shell=True`` on every
  platform, so the venv ``bin/`` must expose a symlink named ``bellhop.exe``
  pointing at the bellhopcuda binary (a plain ``bellhop`` symlink is kept too).
- arlpy runs the solver in the current working directory (no workdir key);
  this adapter serializes all runs behind a process-wide lock and chdirs to
  its workdir.
- SSP profiles need >= 4 points; ``rx_range`` must be a numpy array.
- BELLHOP sorts receiver ranges ascending; batch results are remapped back to
  sensors by range value, never by index.
- The raw arrival ORDER for near-equal delays is not stable across solver
  runs (parallel beam-contribution order); this adapter canonicalizes every
  ArrivalSet by stable-sorting on continuous delay, which makes runs
  reproducible and matches the protocol's delay/order path matching.
"""

from __future__ import annotations

import os
import tempfile
import threading
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from arlpy import uwapm

from hydro_doa_mvp.data.solver.backend import ArrivalSet, SolverEnv

_CWD_LOCK = threading.Lock()


class ArlpyBackend:
    """Per-sensor 2-D arrivals via arlpy + bellhopcuda."""

    name = "arlpy+bellhopcuda"

    def __init__(self, workdir: str | Path | None = None) -> None:
        self._workdir = (
            Path(workdir) if workdir is not None else Path(tempfile.mkdtemp(prefix="bhop-"))
        )
        self._workdir.mkdir(parents=True, exist_ok=True)

    def _run_arrivals(self, env: SolverEnv, rx_range: np.ndarray, tag: str, frequency_hz: float):
        spec = {
            "name": tag,
            "depth": env.depth_m,
            "soundspeed": np.asarray(env.ssp, dtype=float),
            "bottom_soundspeed": env.bottom_soundspeed_m_s,
            "bottom_density": env.bottom_density_kg_m3,
            "bottom_absorption": env.bottom_absorption_db_lambda,
            "frequency": float(frequency_hz),
            "min_angle": env.min_angle_deg,
            "max_angle": env.max_angle_deg,
            "tx_depth": env.tx_depth_m,
            "rx_depth": env.rx_depth_m,
            "rx_range": rx_range,
        }
        if env.nbeams:
            spec["nbeams"] = env.nbeams
        with _CWD_LOCK:
            prev = Path.cwd()
            os.chdir(self._workdir)
            try:
                return uwapm.compute_arrivals(uwapm.create_env2d(**spec))
            finally:
                os.chdir(prev)

    @staticmethod
    def _arrival_set(range_m: float, frequency_hz: float, arr) -> ArrivalSet:
        if arr is None or len(arr) == 0:
            raise RuntimeError("empty arrivals")
        order = np.argsort(np.asarray(arr["time_of_arrival"], dtype=float), kind="stable")
        out = ArrivalSet(
            range_m=range_m,
            frequency_hz=frequency_hz,
            delays_s=np.asarray(arr["time_of_arrival"], dtype=float)[order],
            amplitudes=np.asarray(arr["arrival_amplitude"], dtype=complex)[order],
            surface_bounces=np.asarray(arr["surface_bounces"], dtype=int)[order],
            bottom_bounces=np.asarray(arr["bottom_bounces"], dtype=int)[order],
        )
        out.validate()
        return out

    def run_sensor(self, env: SolverEnv, radial_range_m: float, frequency_hz: float) -> ArrivalSet:
        env.validate()
        tag = f"r{radial_range_m:.4f}f{frequency_hz:.1f}".replace(".", "_")
        arr = self._run_arrivals(
            env, np.asarray([radial_range_m], dtype=float), tag, frequency_hz
        )
        if arr is None or len(arr) == 0:
            raise RuntimeError(f"no arrivals for range={radial_range_m} f={frequency_hz}")
        return self._arrival_set(float(radial_range_m), float(frequency_hz), arr)

    def run_config(
        self, env: SolverEnv, radial_ranges_m: Sequence[float], frequency_hz: float
    ) -> list[ArrivalSet]:
        """Per-sensor runs (default mode, ADR-0001): one solver call per sensor."""
        return [self.run_sensor(env, r, frequency_hz) for r in radial_ranges_m]

    def run_batch(
        self, env: SolverEnv, radial_ranges_m: Sequence[float], frequency_hz: float
    ) -> list[ArrivalSet]:
        """EXPERIMENTAL receiver-vector mode (ADR-0001 clause 4): one solver run,
        remapped to sensors by range value. Requires the pilot 20-config
        equivalence gate before any protocol use; use run_config otherwise.
        """
        env.validate()
        ranges = sorted(float(r) for r in radial_ranges_m)
        if len(set(ranges)) != len(ranges):
            raise ValueError("batch mode requires distinct radial ranges")
        tag = f"batchf{frequency_hz:.1f}".replace(".", "_")
        arr = self._run_arrivals(env, np.asarray(ranges, dtype=float), tag, frequency_hz)
        if arr is None or len(arr) == 0:
            raise RuntimeError("no arrivals in batch run")
        return [
            self._arrival_set(r, float(frequency_hz), arr[np.isclose(arr["rx_range"], r)])
            for r in ranges
        ]
