# ADR-0001: Solver dimensionality (2-D) and mandatory per-sensor computation

- **Status:** accepted (2026-08-16)
- **Deciders:** research owner; external reviews 2026-08-07 / 2026-08-09 / 2026-08-16
- **Scope:** `docs/experiments/bellhop_mvp_protocol.md` Section 6.4 and all generation code

## Context

The MVP models a horizontal planar array (5 or 4 sensors, apertures 0.5–1.118 m) in domain-randomized shallow-water environments. The protocol needs one frozen answer to two questions: which propagation dimensionality to use (2-D / Nx2D / 3-D), and how the arbitrary horizontal array is represented in a 2-D range-depth solver.

## Decision

1. **Dimensionality: classic 2-D** (range-depth vertical plane), arrivals run type `A`. One solver run per sensor with that sensor's radial range `r_i = hypot(source_x - x_i, source_y - y_i)`, at common environment, source depth, and receiver depth.
2. **Per-sensor individual computation is mandatory.** Deriving any sensor's channel from another sensor's channel by geometric delay, phase shift, interpolation, or waveform translation is **forbidden**. Each `r_i` has its own eigenray set (path amplitudes, path births/deaths, caustics); inter-sensor multipath differences are the aperture information under study.
3. **BELLHOP3D and Nx2D are out of scope for the MVP.**
4. Optional efficiency clause: batching the per-sensor radial ranges as a receiver-range *vector* inside a single solver run is admissible **only** after an equivalence gate shows `1 run x 5 ranges == 5 separate runs` on the 20 pilot configurations (matched paths, tolerances of the port-equivalence gate) and only via an explicit protocol amendment. This is still per-element physics (arrivals are extracted at each element's own range), never shift-based synthesis.

## Rationale

- The MVP environment is range-independent with a flat bottom and a depth-only SSP (protocol Section 6.2): the medium is horizontally isotropic, so every azimuthal plane is physically identical and the field at a receiver depends only on `(r, z_src, z_rcv)`. Nx2D degenerates *exactly* (not approximately) to a single 2-D run at range `r_i`; running Nx2D would multiply cost without changing any number.
- Horizontal refraction and azimuth-dependent bottom interaction require lateral medium variation, which the MVP excludes by contract.
- The per-sensor radial representation carries the full array geometry into the solver; the run-count formulas therefore contain the `N_sensors` multiplier (protocol Section 8.1).
- 2-D is also what makes the independent cross-solver gate coherent: KRAKEN (range-independent normal modes) solves the same physics. A range-dependent (Nx2D/PE) upgrade would require a different independent solver.

## Consequences

- Reports must carry the limitation statement: 2-D, range-independent, per-element computation (protocol Section 16).
- Upgrade path (mandatory, not optional) when range-dependent bathymetry enters (Novik-like extension): switch to Nx2D or 3-D, re-derive the array-representation contract, and replace the cross-solver accordingly.
- Any future "reuse one channel with shifts" optimization is rejected regardless of its runtime win.

## Validation plan

- Port-equivalence and cross-solver gates (ADR-0002) run in 2-D mode on the 20 pilot configurations.
- Fractional-delay PDOA diagnostic verifies per-sensor delay fidelity against `tau_max = 3 us`.
