"""Integration tests for the arlpy solver adapter (requires bellhopcuda via venv symlink).

Skipped automatically when the solver binary is not resolvable.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest

from hydro_doa_mvp.data.solver.arlpy_adapter import ArlpyBackend
from hydro_doa_mvp.data.solver.backend import SolverEnv

pytestmark = pytest.mark.skipif(
    shutil.which("bellhop") is None
    or "bellhopcuda" not in str(Path(shutil.which("bellhop") or "").resolve()),
    reason="bellhopcuda not resolvable through venv bin symlink",
)

ENV = SolverEnv(
    depth_m=32.0,
    ssp=np.array([[0.0, 1495.0], [10.7, 1495.2], [21.3, 1495.4], [32.0, 1495.64]]),
    bottom_soundspeed_m_s=1650.0,
    bottom_density_kg_m3=1600.0,
    bottom_absorption_db_lambda=0.4,
    tx_depth_m=10.0,
    rx_depth_m=8.0,
)

R_I = [300.42, 300.23, 300.04, 299.96, 299.58]


def test_env_validation():
    with pytest.raises(ValueError, match="ssp"):
        SolverEnv(
            depth_m=32.0,
            ssp=np.array([[0.0, 1500.0], [32.0, 1500.0]]),
            bottom_soundspeed_m_s=1650.0,
            bottom_density_kg_m3=1600.0,
            bottom_absorption_db_lambda=0.4,
            tx_depth_m=10.0,
            rx_depth_m=8.0,
        ).validate()
    with pytest.raises(ValueError, match="water column"):
        SolverEnv(
            depth_m=32.0,
            ssp=ENV.ssp,
            bottom_soundspeed_m_s=1650.0,
            bottom_density_kg_m3=1600.0,
            bottom_absorption_db_lambda=0.4,
            tx_depth_m=40.0,
            rx_depth_m=8.0,
        ).validate()


def test_per_sensor_runs_and_reproducibility(tmp_path):
    be = ArlpyBackend(workdir=tmp_path)
    a = be.run_sensor(ENV, R_I[0], 1000.0)
    b = be.run_sensor(ENV, R_I[0], 1000.0)
    np.testing.assert_array_equal(a.delays_s, b.delays_s)
    np.testing.assert_array_equal(a.amplitudes, b.amplitudes)
    assert a.delays_s.min() > 0


def test_per_sensor_multipath_and_no_shift(tmp_path):
    be = ArlpyBackend(workdir=tmp_path)
    sets = be.run_config(ENV, R_I, 1000.0)
    assert len(sets) == 5
    for s in sets:
        assert len(s.delays_s) >= 5  # multipath, not a single impulse
    # channels must differ beyond a common delay subtraction (ADR-0001)
    t0 = sets[0].delays_s - sets[0].delays_s.min()
    a0 = np.abs(sets[0].amplitudes)
    a0 = a0 / a0.max()
    ref = np.sort(t0)
    for s in sets[1:]:
        t = np.sort(s.delays_s - s.delays_s.min())
        n = min(len(t), len(ref))
        assert np.max(np.abs(t[:n] - ref[:n])) > 1e-9


def test_batch_equals_separate_first_arrival(tmp_path):
    be = ArlpyBackend(workdir=tmp_path)
    separate = be.run_config(ENV, R_I, 1000.0)
    batch = be.run_batch(ENV, R_I, 1000.0)
    sep_by_range = {s.range_m: s.delays_s.min() for s in separate}
    worst_us = 0.0
    for s in batch:
        worst_us = max(worst_us, 1e6 * abs(s.delays_s.min() - sep_by_range[s.range_m]))
    assert worst_us < 1e-3  # spike measured exactly 0.000000 us
