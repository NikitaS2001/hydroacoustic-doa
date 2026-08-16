# Hydro-DOA World Model GO / NO-GO Decision History

This document is the historical decision log for research readiness. It records why a particular repository state allowed or blocked the next stage, which evidence supported the decision, and what must change before the decision can be reconsidered.

This document is not:

- the normative experiment specification; that role belongs to [`docs/experiments/bellhop_mvp_protocol.md`](experiments/bellhop_mvp_protocol.md);
- a replacement for the architecture and statistical contracts under [`docs/research/framework/`](research/framework/);
- evidence that any solver, data, model, or statistical gate has passed;
- an external replication or publication peer review;
- a task tracker; accepted findings must be transferred to a separate implementation plan or issue tracker.

The log is append-only. Earlier decisions are not silently rewritten. A new review adds a dated entry and may mark an earlier entry `SUPERSEDED` while preserving its original scope and rationale.

## Current Status

Status date: **2026-08-16**.

| Decision area | Status | Basis |
|---|---|---|
| Full dataset generation | **NO-GO** | Solver/build, full-multipath frequency-grid, cross-solver, port-equivalence, fractional-delay, runtime/storage, and replay gates have not run |
| Confirmatory claims | **NO-GO** | No data, model runs, pilot `sigma_d` report, frozen `N_power`, baseline/model results, or executed sealed margin test exist |
| Diagnostic pilot | **CONDITIONAL GO** | The consolidated P0 remediation block from the 2026-08-07/09/16 reviews was applied at the documentation level on 2026-08-16; remaining conditions are the solver-spike verification (ADR-0002 checklist) and the pilot gates themselves |
| Empirical readiness | **NOT YET EVALUATED** | The repository contains no experiment implementation artifacts yet, solver manifests, datasets, checkpoints, or empirical results |

In practical terms, only preparation and minimal diagnostic work that cannot be mistaken for a completed confirmatory study are allowed. Full generation and scientific claims remain blocked.

## Audited State

The published product corpus is pinned to:

```text
e200bcc1638687f081b2833ab06ab98d1c7cd5c3
```

The remediation range is:

```text
5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3
```

It contains `16` product commits, `11` changed paths, and `6091` lines in the published corpus (`README.md`, `docs/README.md`, `docs/research/framework/*.md`, and `docs/experiments/bellhop_mvp_protocol.md`). The following commit, `e57432cd11f1dac07e4496a5ce6119af7663d5fe`, changes only the provenance of this historical audit and does not change the product protocol.

Reproduce the snapshot with:

```zsh
git rev-list --count 5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3
git diff --name-only 5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3 | sort
git worktree add --detach <temporary-path> e200bcc1638687f081b2833ab06ab98d1c7cd5c3
```

Run the final command only with a disposable worktree and remove that worktree after verification.

## Decision Timeline

### 2026-07-16/17 — Initial Methodology Audit

**State:** checkpoint `09d16fa8769dde7da73a0bdc06abc67a6df0ea85`.

**Decision:** `NO-GO` for full dataset generation.

**Primary reasons:** an incomplete BELLHOP broadband contract, mixed solver modes, an unidentified geometry effect, a contradictory sealed design, an insufficient TDOA/IPD gate, unverified statistical power, and no empirical artifacts.

**Outcome:** commit `a06e4a6caf109688c2f2d9ca40cf6211271bb049` (`docs(audit): record 2026-07-17 methodology no-go review`) recorded the audit and initiated documentation remediation.

**Entry status:** `SUPERSEDED` by later reviews. Retrieve the original text with:

```zsh
git show a06e4a6caf109688c2f2d9ca40cf6211271bb049:docs/research_plan_analysis.md
```

### 2026-07-22 — Internal Re-audit After Remediation

**State:** `86d037893e3b7b5584d964f6efb386033843986c`, later refined through `e1fe8c27a3688a15b75317cec18a0d9e1b26e06b`.

**Decision:** `CONDITIONAL GO` for a future diagnostic pilot only; `NO-GO` for full generation and confirmatory claims.

**Items considered documentation-resolved:** Rect-5 roles, matched coordinate controls, supervised Tier-0 scope, continuous-delay synthesis, the alias-safe primary band, environment-level inference, a single sealed access, and separation of diagnostic and stress outputs.

**Items still pilot-dependent:** solver/build identity, ray and broadband convergence, comparison solver, fractional-delay recovery, runtime/storage, replay, ICC and paired-effect variance, `N_power`, and model gates.

**Outcome:** commit `c1c07e90dc045b01b9c8a344fb4c6bda6e8454c3` (`docs(audit): refresh remediation status`) updated the status matrix.

**Entry status:** `SUPERSEDED` by later reviews. It covers only the original P0 catalog and does not include the new findings from the August reviews.

### 2026-08-07 — External Review of the Product Corpus

**State:** `e200bcc1638687f081b2833ab06ab98d1c7cd5c3`.

**Source:** independent review of 2026-08-07 (archived locally in `.omo/reviews/research_plan_review_2026-08-07.md`; not part of the published corpus).

**Decision:** `CONDITIONAL GO` for a diagnostic pilot only after an additional group of static corrections; confirmatory claims remain `NO-GO`.

**New rationale:** a possible missing sensor-count multiplier in the runtime budget; ambiguity in the estimand and the hierarchy between the confidence interval and the `15%` gate; underspecified bootstrap and seed handling; missing causal controls; risk in the IPD recoverability gate; and the need for more conservative novelty positioning.

**Entry status:** `ACTIVE REVIEW INPUT`. Each finding still requires classification as a confirmed defect, a scientific design decision, or a pilot-dependent risk.

### 2026-08-09 — Verification and Extension of the External Review

**State:** the same product commit, `e200bcc1638687f081b2833ab06ab98d1c7cd5c3`.

**Source:** independent review of 2026-08-09 (archived locally in `.omo/reviews/research_plan_review_2026-08-09.md`; not part of the published corpus).

**Decision:** the form remains unchanged, `CONDITIONAL GO` for a diagnostic pilot only, but the preliminary conditions are broader.

**Confirmed or strengthened concerns:**

- the formulas for run count, interferer budget, runtime, and storage do not explicitly reflect separate per-sensor BELLHOP calculations;
- the primary environment-level confidence interval and the practical `15%` improvement threshold do not form one explicit decision hierarchy;
- the target effect used for power analysis is not separated from the decision threshold;
- the Tier-0 training input requires an unambiguous relationship to the primary inference view;
- MVDR/MUSIC aggregation, comparator fallback, angular-boundary handling, and permutation-canary sampling require clarification;
- prior art limits component novelty and supports positioning the work as domain evidence and methodological rigor.

**Clarifications in favor of the plan:** seed handling is underspecified rather than logically contradictory; an attempt log exists; and the original Rect-5 RBF extrapolation concern was overstated.

**Entry status:** `ACTIVE REVIEW INPUT`. This document is a follow-up verification of the earlier review, not a fully independent replication.

### 2026-08-12 — Completion of Internal Static Remediation

**Product state:** `e200bcc1638687f081b2833ab06ab98d1c7cd5c3`.

**Audit wrapper:** `e57432cd11f1dac07e4496a5ce6119af7663d5fe`.

**Internal gate decision:** the original `P0.1–P0.11` set, the latest SNR/noise/interference blockers, and P1 synchronization were considered closed at the documentation level. This permits only a diagnostic pilot and is not an empirical `PASS`.

**Decision boundary:** the internal gate checked its own predefined criterion catalog. It does not invalidate new findings from the 7 and 9 August external reviews. The historical statement that no static P0 items remained is therefore valid only relative to the internal catalog and must not be read as a universal assessment of the methodology.

**Entry status:** `CURRENT INTERNAL GATE`, qualified by the active external review inputs.

### 2026-08-16 — External Review (Third Iteration) and Application of the Consolidated P0 Remediation

**State:** working tree on top of `e57432cd11f1dac07e4496a5ce6119af7663d5fe`; the product corpus before this remediation was still `e200bcc1638687f081b2833ab06ab98d1c7cd5c3` (unchanged since the August reviews).

**Source:** independent review of 2026-08-16 (archived locally in `.omo/reviews/research_plan_review_2026-08-16.md`; not part of the published corpus).

**Review decision:** the corpus was unchanged since 2026-08-09; the review independently confirmed all key findings of the two prior reviews and found none of the proposed fixes applied. Scores unchanged (novelty 3.0, realizability 5.5, completeness 8.0, clarity 6.0, readiness 3.0, MVP adequacy 6.0).

**Remediation applied the same day (documentation level, this commit):**

- per-sensor run multiplier `N_sensors` added to `N_narrowband_runs`, `N_interferer_runs`, `T_total_seconds`, and `B_storage` (`N_sensor_channel_runs`); historical budget table recomputed `x5`;
- frozen statistical decision contract (protocol Section 12.1): single estimand, one-sided margin test `H0: R <= 15%` at `alpha = 0.05`, target effect `20%`, `t`-interval primary CI, seed-averaged predictions, `N_sealed = max(20, N_power)` from the pilot upper CI of `sigma_d`, Holm-corrected stratified secondaries; kill criteria consolidated (former kills 4/5 reclassified as operational retry / part of the single margin decision);
- calibration controls: `random-coordinate` mode, ceiling-reference run, absolute clean floor (`<= 10 deg`, pilot-frozen), mandatory per-example channel-order randomization, no-coordinate strength diagnostic;
- solver contract: ADR-0001 (2-D, per-sensor individual computation, shift-based synthesis banned, Nx2D degeneracy rationale) and ADR-0002 (bellhopcuda engine + arlpy interface + reference BELLHOP port-equivalence gate + KRAKEN independent cross-solver); port-equivalence and `.arr`-precision checks added to Section 6.4; limitation statement extended;
- gate 13.4: predefined phase-auxiliary-loss rescue path; phase-tolerance hierarchy (0.05 rad full-multipath vs `eps_phi` per-path estimands) documented;
- Tier-0 scope reduction: train `120,000 -> 60,000`, dev-test `48,000 -> 24,000`; colored `1/f`, `1/f²` noise promoted to Tier-0 secondary strata in every split (user decision); OOD panels, Novik-like, tonal/coherent-interferer banks deferred to Tier-1; sealed-policy attempt cap `3x` quota + mandatory dev dry-run + survivorship audit;
- clarity: glossary (Section 0), data-flow diagram (Section 7.4), worked numeric example (Section 7.2a), primary endpoint stated in Section 1; geometry-neutral view IDs;
- framework corpus: global section renumbering (collisions §6/§21/§22 removed; corpus now §1–30), supervised-first fixes in evaluation Section 21.11/19.0, MFP positioning, bibliography extended with Baek 2025 / IPDnet / GC-SSF / Cao 2024 / Grinstein 2023 / Tammen 2024, novelty repositioned as domain evidence + methodological rigor (overview 2.2, architecture 9.11), roadmap SSL criteria made conditional, README updated (MVP claim block, repo boundary with in-repo `src/` implementation, ADR links, all three reviews linked).

**Decision boundary:** this entry closes the *static documentation* portion of the open review findings. It is not an empirical pass of any gate; all solver, runtime, replay, statistical, and model gates remain `NOT_YET_EVALUATED`. The solver stack was pinned by workstation inventory (ADR-0002 spike table); its equivalence/cross-solver gates are pilot work.

**Entry status:** `CURRENT INTERNAL GATE`.

## Open NO-GO Rationale

The categories below are not an implementation backlog. Before work starts, each finding needs an owner, precise acceptance criteria, and an explicit `accept`, `reject`, or `defer-to-pilot` decision. Statuses below reflect the 2026-08-16 static remediation: documentation-level items are marked `RESOLVED (DOCUMENTATION)`; everything empirical remains open.

| Category | Current status | Reconsideration condition |
|---|---|---|
| Solver/build and full-multipath fidelity | `NOT YET EVALUATED` (stack pinned in ADR-0002; engine/reference/KRAKEN roles fixed) | Pass port-equivalence, convergence, KRAKEN cross-solver, and fractional-delay gates in the pilot |
| Runtime/storage and allocation | `RESOLVED (DOCUMENTATION)` — formulas carry `N_sensor_channel_runs`; budgets await measured p95 | Measure p95 runtime and I/O in the 100-config pilot benchmark |
| Statistical decision contract | `RESOLVED (DOCUMENTATION)` — single estimand, margin test, target effect, bootstrap, seeds, `N_sealed = max(20, N_power)` frozen in protocol Section 12.1 | Pilot must produce `sigma_d` with CI; freeze `N_power` |
| Tier-0 data path | `RESOLVED (DOCUMENTATION)` — training consumes the primary view of eligible rows; view IDs geometry-neutral | Verify in implementation and replay gate |
| Controls and baselines | `RESOLVED (DOCUMENTATION)` — random-coordinate, ceiling, absolute floor, channel-order randomization, MVDR/MUSIC aggregation, Conformer fallback frozen | Verify empirically in pilot |
| Phase/IPD recoverability | `PILOT-DEPENDENT RISK` (predefined auxiliary-loss rescue path added) | Run the end-to-end diagnostic; single auxiliary-loss retry permitted |
| Scientific novelty | `RESOLVED (DOCUMENTATION)` — prior-art matrix extended; claims limited to domain evidence + methodological rigor | Re-check prior art before publication |
| Empirical evidence | `NOT YET EVALUATED` | Produce separate reproducible code, manifests, data, runs, checkpoints, and result artifacts |

## Conditions for Lifting NO-GO

The `NO-GO` for full dataset generation may be reconsidered only after:

1. Every `OPEN REVIEW FINDING` is classified and either corrected or rejected with verifiable technical justification.
2. A minimal diagnostic pilot reproducibly passes the solver/build, convergence, fractional-delay, runtime/storage, and replay gates.
3. Allocation and power derive from measured pilot quantities rather than nested rows, overlays, views, or model seeds.
4. One primary statistical decision contract is frozen without competing non-hierarchical rules.
5. An immutable evidence manifest records exact solver, code, configuration, and result versions.

The `NO-GO` for confirmatory claims may be reconsidered only after a separate frozen-protocol run. Documentation completion or a successful diagnostic pilot does not lift that decision by itself.

## Maintaining This Log

Append every new entry to the end of the decision timeline using:

```text
### YYYY-MM-DD — Short Review Name

State: full commit SHA and exact scope.
Review type: internal audit / external review / pilot gate / confirmatory gate.
Decision: GO / CONDITIONAL GO / NO-GO / SUPERSEDED.
Rationale: reproducible facts plus explicitly labeled expert judgments.
Change from the previous decision: what opened, closed, or was clarified.
Artifacts: tracked paths, commands, manifests, or reports.
Next reconsideration conditions: concrete observable criteria.
```

Maintenance rules:

- always record a full commit SHA and never mix the tracked corpus with local untracked files;
- distinguish `documentation-resolved` from `empirically passed`;
- never present reviewer scores or schedule estimates as measured facts;
- mark old decisions `SUPERSEDED` instead of deleting them;
- keep the detailed review in its source document and record only the decision, rationale, and link here;
- never declare `GO` while mandatory artifacts are absent or remain `NOT YET EVALUATED`.

## Historical Reproducibility

Detailed earlier versions remain available in Git and are not duplicated in the current file:

```zsh
git show a06e4a6caf109688c2f2d9ca40cf6211271bb049:docs/research_plan_analysis.md
git show c1c07e90dc045b01b9c8a344fb4c6bda6e8454c3:docs/research_plan_analysis.md
git show e57432cd11f1dac07e4496a5ce6119af7663d5fe:docs/research_plan_analysis.md
```

This preserves the audit trail without asking current readers to treat superseded line anchors and judgments as the active scientific contract.
