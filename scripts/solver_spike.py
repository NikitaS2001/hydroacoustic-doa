"""Solver spike: verify the bellhopcuda + arlpy pairing (ADR-0002 checklist).

Run: uv run python scripts/solver_spike.py

Checks:
  (a) arlpy resolves `bellhop` from the venv bin symlink -> bellhopcuda
  (b) .arr output parses; per-sensor arrival delay structure reported
  (c) per-sensor radial runs (5 distinct r_i at one depth) work
  (d) no-shift: arrival structure at different r_i differs beyond a common delay
  (f) receiver-range-vector batching: 1 run x 5 ranges vs 5 separate runs

Env mirrors the protocol Section 7.2a worked example: depth 32 m, surface
speed 1495 m/s, gradient +0.02 (m/s)/m, bottom 1650 m/s / 1.6 g/cm^3 / 0.4 dB/lambda,
source depth 10 m, receiver depth 8 m, azimuth +22.5 deg at range 300 m -> per-sensor
radial ranges r = [300.42, 300.23, 300.04, 299.96, 299.58] m.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

R_I = [300.42, 300.23, 300.04, 299.96, 299.58]
FREQ_HZ = 1000.0


def check_a_binary_resolution() -> str:
    resolved = shutil.which("bellhop")
    assert resolved is not None, "bellhop not on PATH"
    target = str(Path(resolved).resolve())
    assert "bellhopcuda" in target, f"resolved to {target}, expected bellhopcuda"
    return target


def make_env(uwapm, rx_range, tag: str, freq: float = FREQ_HZ):
    return uwapm.create_env2d(
        name=tag,
        depth=32.0,
        soundspeed=[[0.0, 1495.0], [10.7, 1495.2], [21.3, 1495.4], [32.0, 1495.64]],
        bottom_soundspeed=1650.0,
        bottom_density=1600.0,
        bottom_absorption=0.4,
        frequency=freq,
        min_angle=-20,
        max_angle=20,
        tx_depth=10.0,
        rx_depth=8.0,
        rx_range=np.asarray(rx_range, dtype=float),
    )


def arrivals_of(uwapm, env):
    arr = uwapm.compute_arrivals(env, debug=False)
    assert arr is not None and len(arr) > 0, "no arrivals parsed"
    return arr


def norm_amplitudes(arr):
    a = np.abs(np.asarray(arr["arrival_amplitude"], dtype=complex))
    return a / max(a.max(), 1e-12) if a.size else a


def check_d_noshift(per_sensor: list) -> float:
    """Channels at different r_i must differ beyond a common delay subtraction."""
    ref = per_sensor[0]
    ref_t = np.asarray(ref["time_of_arrival"], dtype=float)
    ref_t = ref_t - ref_t.min()
    ref_a = norm_amplitudes(ref)
    diffs = []
    for arr in per_sensor[1:]:
        t = np.asarray(arr["time_of_arrival"], dtype=float)
        t = t - t.min()
        a = norm_amplitudes(arr)
        n = min(len(t), len(ref_t))
        dt = np.max(np.abs(t[:n] - ref_t[:n]))
        da = np.max(np.abs(a[:n] - ref_a[:n]))
        diffs.append(float(dt + da))
    total = float(np.mean(diffs))
    assert total > 1e-9, "channels look like pure time shifts of one another (no-shift violated)"
    return total


C_EFF = 1495.2  # mean water-column speed along the direct path (SSP 1495.0..1495.64)
TX_DEPTH, RX_DEPTH = 10.0, 8.0


def check_pdoa(uwapm, freqs=(500.0, 1000.0, 1400.0)) -> float:
    """PDOA/IPD fidelity seed (protocol Section 4: the primary cue is PDOA, not TDOA).

    arlpy's arrival_amplitude carries the full propagation phase at the RUN
    frequency (amp = A * exp(-1j*(alpha + omega*tau))), so the direct-path
    inter-sensor phase difference is arg(amp_i) - arg(amp_j) -- and the solver
    must be run at each frequency under test. Compare against the geometric
    prediction from slant-range travel times at the effective sound speed.
    Seed of the Section 6.4 direct-path PDOA/IPD preservation diagnostic.
    """
    worst = 0.0
    tau_geom = [np.sqrt(r**2 + (TX_DEPTH - RX_DEPTH) ** 2) / C_EFF for r in R_I]
    for f in freqs:
        phis = []
        for i, r in enumerate(R_I):
            arr = arrivals_of(uwapm, make_env(uwapm, [r], f"pdoa{int(f)}s{i}", freq=f))
            k = int(np.argmin(arr["time_of_arrival"]))
            phis.append(np.angle(complex(arr["arrival_amplitude"].iloc[k])))
        for i in range(len(R_I)):
            for j in range(i + 1, len(R_I)):
                dphi_arr = float(np.angle(np.exp(1j * (phis[i] - phis[j]))))
                dphi_geom = float(np.angle(np.exp(-1j * 2 * np.pi * f * (tau_geom[i] - tau_geom[j]))))
                worst = max(worst, abs(float(np.angle(np.exp(1j * (dphi_arr - dphi_geom))))))
    return worst


def main() -> int:
    print("== solver spike (ADR-0002) ==")
    target = check_a_binary_resolution()
    print(f"(a) bellhop -> {target}")

    from arlpy import uwapm  # noqa: PLC0415 (kept local: heavy import)

    cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as td:
        os.chdir(td)  # arlpy runs bellhop in the CWD; it has no workdir key
        try:
            per_sensor = []
            for i, r in enumerate(R_I):
                arr = arrivals_of(uwapm, make_env(uwapm, [r], f"sensor{i}"))
                per_sensor.append(arr)
            span_us = 1e6 * float(
                np.max(per_sensor[0]["time_of_arrival"]) - np.min(per_sensor[0]["time_of_arrival"])
            )
            print(f"(c) per-sensor runs: paths per sensor = {[len(a) for a in per_sensor]}")
            print(f"(b) sensor0 multipath delay span = {span_us:.3f} us")

            arr_batch = arrivals_of(uwapm, make_env(uwapm, R_I, "batch"))
            n_sep = sum(len(a) for a in per_sensor)
            print(f"(f) batch run rows = {len(arr_batch)} (sum of separate runs = {n_sep})")
            # BELLHOP sorts receiver ranges ascending; remap by range value, not index
            first_by_range = {
                round(float(rr), 3): float(np.min(g["time_of_arrival"]))
                for rr, g in arr_batch.groupby("rx_range")
            }
            first_separate = {
                round(r, 3): float(np.min(a["time_of_arrival"]))
                for r, a in zip(R_I, per_sensor, strict=True)
            }
            pairs = sorted(first_by_range.items())
            sep_sorted = sorted(first_separate.items())
            dev_us = 1e6 * float(np.max(np.abs(np.array([p[1] for p in pairs])
                                               - np.array([p[1] for p in sep_sorted]))))
            delay_span_us = 1e6 * (pairs[-1][1] - pairs[0][1])
            print(f"(f) batch-vs-separate first-arrival deviation = {dev_us:.6f} us")
            print(f"    auxiliary delay QA: first-arrival spread = {delay_span_us:.3f} us "
                  f"(geometry {1e6 * (max(R_I) - min(R_I)) / 1500.0:.3f} us @ c=1500; "
                  f"auxiliary only - the primary cue is PDOA/IPD, protocol Section 4)")

            no_shift_stat = check_d_noshift(per_sensor)
            print(f"(d) no-shift structural-difference statistic = {no_shift_stat:.3e} (> 0 required)")

            pdoa_dev = check_pdoa(uwapm)
            print(f"(p) PDOA check: max |phase residual| = {pdoa_dev:.6f} rad "
                  f"(band 500/1000/1400 Hz; eps_phi(1400) = {2 * np.pi * 1400 * 3e-6:.4f} rad)")
        finally:
            os.chdir(cwd)

    print("== spike OK ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
