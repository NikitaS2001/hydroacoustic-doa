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

## Spike checklist (stage 1, before the layer is trusted)

(a) arlpy `compute_arrivals` resolves the venv-`bin/` symlink and drives bellhopcuda; (b) bellhopcuda v1.5 `.arr` output parses with both arlpy and our own parser at the required precision; (c) per-sensor radial runs (`r_i`) and single-frequency-per-run work through the adapter; (d) no-shift regression test: channels at different `r_i` differ beyond a common delay (ADR-0001); (e) KRAKEN subprocess invocation; (f) first check of the receiver-range-vector batching equivalence (ADR-0001 clause 4).
