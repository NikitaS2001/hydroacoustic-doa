# ADR-0002: Solver stack — bellhopcuda engine + arlpy interface + KRAKEN cross-check

- **Status:** accepted (2026-08-16); spike inventory recorded below
- **Deciders:** research owner (stack choice confirmed in planning 2026-08-16)
- **Scope:** solver layer of `src/hydro_doa_mvp/`, pilot manifests (protocol Section 6.4 fields)

## Decision

Three-role solver stack on Linux, all roles pinned by manifest:

| Role | Component | Notes |
|---|---|---|
| Generation engine | **bellhopcuda** (C++/CUDA port of BELLHOP; multithreaded CPU + CUDA) | v1.5+ aligned `.arr`/`.shd` formats with the Acoustics Toolbox 2024 behavior; published speedups 10–50x (consumer GPU) / 20–100x (A100 class) |
| Python interface | **arlpy** (`arlpy.uwapm`: `create_env2d` → `compute_arrivals`) | arlpy resolves the solver through the `bellhop` name on `PATH`; integration = symlink `bellhop -> <bellhopcuda binary>` placed in the project venv `bin/` (uv-managed; system PATH untouched) |
| Reference build (port-equivalence gate) | CPU **BELLHOP** from the Acoustics Toolbox | same-algorithm reference; a port cannot be its own reference |
| Independent cross-solver | **KRAKEN** from the Acoustics Toolbox, called via subprocess | normal-mode physics; satisfies the protocol's "independently frozen comparison solver" requirement |

UnderwaterAcoustics.jl / Julia are **removed** from the stack: its added value (multi-model wrappers, differentiable models, 3-D) is not needed in the frozen 2-D scope, and it would add an interop dependency. arlpy being in maintenance mode is accepted; it is isolated behind a single adapter module, with vendoring/patching (BSD-3) or a self-written `.env` writer as the fallback if incompatibilities appear in the spike.

## Spike inventory (2026-08-16, this workstation)

| Fact | Value |
|---|---|
| bellhopcuda binary | `/home/nik/app/bellhopcuda/bin/bellhopcuda` (symlinked at `~/.local/bin/bellhopcuda`) |
| Binary SHA-256 | `3e9b028ea7cdc8b1d624828abc6c91cb286f4ac3440c94186a2ab84a4db62acf` |
| Source tree | `/home/nik/app/bellhopcuda` @ `b396d40ba49c2f349258b9687cfae8ff8323828f` (`v1.5-dirty`; dirty only in `examples/province.cpp`, not solver core) |
| Upstream | `https://github.com/A-New-BellHope/bellhopcuda.git` |
| Available binaries | `bellhopcuda` (2-D), `bellhopcuda2d/3d/nx2d`, `bellhopcxx` (CPU multithreaded) + variants, `libbellhopcudalib.so` (library mode) |
| Local GPU | NVIDIA RTX 3070 Ti, compute capability 8.6, driver 580.95.05 |
| arlpy | not installed yet → `uv add arlpy` in stage 1 |
| Reference BELLHOP / KRAKEN | not present on this machine → build from the Acoustics Toolbox in stage 2 and pin |
| License | bellhopcuda GPL-3.0 (fine for internal research; redistribution of a linked pipeline would need a separate decision); arlpy BSD-3-Clause |

## Gates and fallbacks

1. **Port-equivalence gate (precondition for using bellhopcuda as engine):** on the 20 pilot configurations, matched-path phase residual `< 0.01 rad`, magnitude residual `< 0.2 dB` vs the reference CPU BELLHOP. Fail → use the reference build as engine and recompute the runtime budget (protocol Section 6.4).
2. **Cross-solver gate (KRAKEN):** phase `< 0.05 rad`, magnitude `< 1 dB` per protocol Section 6.4 — unchanged.
3. **`.arr` precision check:** serialized delays must resolve `<= 0.3 us` (`10x` finer than `tau_max = 3 us`).
4. Known port caveat: Pisha et al. (JASA 2023) report occasional edge-case mismatches vs original BELLHOP — this is exactly what gate 1 exists to catch on our environment distribution; per-environment fallback to the reference build is allowed and must be recorded in the run manifest.
5. Pinning: every manifest row records `solver_repository`, `solver_build_sha` (or binary SHA-256 for prebuilt), compiler, precision, and input-file hashes (protocol Section 6.4 fields).

## Spike checklist (stage 1) — executed 2026-08-16, all items PASSED

Executed via `uv run python scripts/solver_spike.py` (env of the protocol §7.2a worked example; 1000 Hz; 5 per-sensor radial ranges of Rect-5 at azimuth +22.5°, range 300 m):

| Item | Result |
|---|---|
| (a) arlpy → bellhopcuda | **PASS**, with one integration nuance: arlpy hardcodes the solver invocation as `bellhop.exe` (all platforms, `shell=True`), so the venv-`bin/` symlink must be named **`bellhop.exe` → bellhopcuda binary**; a `bellhop` symlink is kept for direct calls |
| (b) `.arr` parsing & precision | **PASS**: arlpy 1.9.3 parses bellhopcuda v1.5 `.arr` (2D multi-receiver header); batch-vs-separate first-arrival deviation `0.000000 us` (far below the `0.3 us` bound); per-sensor multipath span `13.0 ms` (real bottom/surface bounces) |
| (c) per-sensor radial runs | **PASS**: 12–13 eigenray paths per sensor at the 5 distinct `r_i`; TDOA span `561.77 us` matches geometry (`0.84 m / ~1495 m/s = 561.9 us`) |
| (d) no-shift regression | **PASS**: arrival structure at different `r_i` differs beyond a common delay subtraction (statistic `0.85 >> 0`) — channels are individually computed multipath, not shifts |
| (e) KRAKEN subprocess | **DEFERRED to stage 2**: reference BELLHOP/KRAKEN not yet built on this machine |
| (f) receiver-vector batching | **PASS at first-arrival level**: `1 run x 5 ranges` reproduces all 61 arrivals of the 5 separate runs with zero deviation; **BELLHOP sorts receiver ranges ascending** — adapters must remap `rx_range_ndx` back to sensor order by range value. Full 20-config multipath equivalence gate remains pilot work before batching may replace per-sensor runs |

Consequences recorded for the adapter design: env `rx_range` must be a numpy array; arlpy runs the solver in the CWD (no workdir key); SSP profiles need >= 4 points; `arrival_amplitude`/`time_of_arrival`/`rx_range_ndx` are the working DataFrame columns.
