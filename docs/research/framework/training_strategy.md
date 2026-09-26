# Training And Adaptation Strategy

> This document specifies the minimum training and adaptation decisions for the [authoritative roadmap](roadmap.md) and the [winter field protocol](../../experiments/winter_field_protocol.md). It is a prospective protocol: no data access, feasibility gate, model run, or result has occurred merely because it is described here.

## 13. Training Strategy

### 13.1 Minimum supervised path

The reproducible **scratch control** and field-minimum comparison train a compact supervised neural pair on the same permitted development distribution:

- a coordinate-aware complex-STFT model using the measured/simulated linear-array coordinates; and
- a matched no-coordinate twin with the same inputs apart from coordinate-derived information.

Both produce one single-source azimuth estimate in the same surveyed identifiable sector. The source half-plane/sector prior, calibration access, classical-method inputs, loss definition, optimization budget, and stopping rule are shared. MVDR/Capon and MUSIC are required comparisons, while Bartlett is diagnostic. The neural pair is not a claim of broad SOTA superiority.

Before the 2026-11-15 analysis freeze, a local feasibility run measures the selected compact model's runtime, memory, and practical per-run compute. That measured envelope fixes the architecture and training cap. The planning target is **three paired seeds for each neural model**, using matched seed assignments so the coordinate contrast can be analysed pairwise. If the measured budget cannot support that target, the failure action is an explicit supervisor-approved reduction or amended inference scope before final testing—not unreported seed removal or a larger-model rescue.

The primary front end is **Re/Im STFT**, with the tensor interface, coherent processing, and phase/delay safeguards defined in [architecture §8](architecture.md#8-input-representation-strategy). The physical band, sample rate, STFT parameters, sensor coordinate convention, and model budget must be bench-validated and frozen by 2026-11-15. No fixed frequency band, SNR grid, parameter-count band, effect threshold, or requirement to train every size is mandated here. The broader representation catalogue does not leave the core input or its parameterization open to result-driven replacement.

The selected common channel encoder is the hybrid complex Conv2D stem plus real Conformer-like temporal blocks and local frequency mixing in [architecture §9.1](architecture.md#91-shared-model-contract). It preserves a real feature/time-frequency grid until separate Fusion. Start with full, potentially bidirectional temporal attention inside each bounded observation window, separately per frequency position; sliding input crops do not imply sliding-window attention. The coordinate-aware/no-coordinate pair uses the same configuration, without a CNN-first prerequisite or an added architecture-comparison arm. The feasibility run must exercise the complete complex-stem/real-block forward and backward path at the intended shapes and attention backend, not infer its cost or phase behaviour from speech models.

The [E-S/E-M/E-L engineering presets](architecture.md#913-engineering-size-presets-and-single-size-selection) define candidate widths/depths, not three compulsory fits. Start the resource and full-encoder phase/delay pilot with **E-M**; use E-S if E-M does not fit the measured resource envelope, while E-L remains a separately justified development reserve, not a larger-model rescue. Freeze one preset and its complete configuration by 2026-11-15 and before comparative pretraining. That same size and output width serve the core pair, the Stage-1/Stage-2 JEPA path and the supervised-from-scratch comparator. Any resource comparison among presets keeps the physical input window, representation, attention policy and non-size processing choices matched or explicitly reports differences.

The initial E-M pilot candidate uses **`C=96`, `F_e=F`, `T_e≈T/2`**: test moderate temporal subsampling in the complex stem before considering frequency-axis reduction. This is not a frozen stride or a claim of phase/delay preservation. Specify exact output sizes, position alignment, and raw-sample support from the declared kernels, strides, and padding/boundary handling, then accept or revise the candidate under the full-encoder phase/delay and measured-resource gates. No compulsory full-resolution comparison or output-form/resolution-by-pretraining matrix is added.

The selected [coordinate-aware channel-attention Fusion](architecture.md#102-array-aggregation-requirements) is a shared part of the supervised core and the JEPA Stage-2 and Stage-3 paths, not another architecture factor. The initial E-M Fusion uses one pre-LayerNorm block, `C=96`, four heads and FFN `96 -> 192 -> 96`, independently at each retained `(f,t)`. Shared coordinate and physical-frequency encodings enter the tokens before Q/K/V projection; masked sensor pooling precedes valid-TF pooling. The no-coordinate twin keeps the structure and frequency encoding but supplies a constant zero coordinate input to `g_r`, with no topology, mirror-pair or slot shortcut.

Freeze the geometry-reference rule, fixed physical length/frequency scales, coordinate/frequency MLP configuration, frequency-position mapping, mask/empty-input handling and full Fusion implementation before comparative downstream training. Learn Fusion jointly through the selected [single-azimuth vector head and supervised MSE](architecture.md#12-downstream-heads); this does not prescribe an extra geometry loss, pretrained Fusion, angular grid or curriculum. Include the complete encoder/Fusion/head forward/backward/inference path in the phase, permutation and resource gates. Different sensor counts or coordinate inputs do not establish generalization: geometry transfer remains the existing optional study, without automatically importing the published methods' geometry-training curricula.

The common head maps the pooled `[N,C]` features through `Linear(C,C) -> GELU -> Linear(C,2)` and predicts raw `(a,b)` for target `(cos(theta),sin(theta))` in the declared coordinate frame. Optimize the batch mean of per-example **sum** of squared component errors, without output normalization or a separate angular/spectrum loss; decode only at inference with `atan2(b,a)` if both components are finite and their norm exceeds the predeclared numerical degeneracy threshold. Record and freeze that threshold before sealed scoring; a degenerate vector is a failure, not a zero-degree answer. Hold the head, labels, reduction and failure rule identical for the matched pair and either Stage-3 branch and the supervised-from-scratch comparator. The primary circular angular error remains an **evaluation measure**, not the optimization loss.

### 13.2 Independent-unit and access discipline

Simulation environments are the simulation inference units. Field deployment/session/day blocks are real acquisition groups; repeated transmissions, bearings, bursts, and overlapping clips do not become independent replicates. Multiple independently acquired field groups are an acquisition target where safe and practicable, not guaranteed statistical power. One usable session permits only appropriately descriptive, bounded conclusions.

The default sim-to-real track is immutable **zero-shot**:

| Material or action | Immutable zero-shot track |
|---|---|
| Simulated development data | Permitted for training, normalizer fitting, simulator development, and model selection as frozen by protocol |
| Real development groups | Not used |
| Sealed real test groups, including unlabelled clips and noise-only recordings | Never used for training, normalizers, simulator tuning, SSL, augmentation selection, early stopping, or model selection |
| Calibration | Frozen separately and supplied identically to all compared methods |

Real-noise overlay on a simulated source is not real-data validation. The [winter field protocol](../../experiments/winter_field_protocol.md) governs manifests, acquisition groups, calibration, raw-data immutability, and the access ledger. The analysis and evaluation documents govern the final test lock; this training document must not create a competing split or data-access exception.

### 13.3 Training safeguards

The model pair must use the same supervised target, source sector/half-plane prior, permissible training material, and reporting units. Each run records the frozen configuration, code/data version identifiers when implementation exists, random seed, resource use, and any allowed adaptation access. The coordinate-aware arm is compared directly with its seed-matched no-coordinate twin; an unpaired average over arbitrary runs is not a substitute.

The following safeguards are blocking conditions for interpreting a neural coordinate effect:

1. **Phase integrity:** preprocessing, the complete hybrid channel encoder, and aggregation retain recoverable controlled relative delay, phase, coherence, and timing information. Checking the complex stem alone is insufficient. Independent per-channel phase randomization, random time shifts, or per-channel normalization are not generic augmentations.
2. **Joint permutation canary:** jointly reordering channel signals, coordinates, calibration fields, and masks leaves the model output unchanged to the predeclared reporting resolution.
3. **Coordinate association canary:** detaching or permuting coordinate fields while the signal channels remain fixed is a predeclared diagnostic for signal-coordinate association. It does not authorize tuning on sealed real data.
4. **No-coordinate isolation:** the twin has no coordinate-derived, topology-label, or stable channel-slot shortcut.

A failed safeguard stops the associated inference. It is not repaired by adding SSL, a larger model, more heads, or an unplanned architecture sweep.

### 13.4 Scope and conditional extensions

The **JEPA/JEPA-like three-stage protocol** in §13.5 is the primary SSL research path, not the old optional five-encoder E4 slate. A compact supervised-from-scratch geometry-aware/no-coordinate pair, MVDR/Capon, MUSIC, mandatory winter field work and writing remain the minimum controls/evidence. Whether completing all three SSL stages is a formal M3 minimum or a hypothesis contingent on gates and measured resources requires explicit candidate/supervisor sign-off by the November freeze; until then report failed/unrun stages rather than claiming the minimum completed by an incomplete method. **TODO: owner candidate + supervisor; measured compute and dissertation-scope decision.** Historical E4's five-focused-day cap cannot be assumed sufficient for the new main method.

E1 labelled-real adaptation is separate from the unlabelled R regime. Limited within-linear subset/spacing, ice/boundary/calibration, representation and simulated non-linear-topology extensions are optional only after the main protocol and winter minimum are secure, under an individually approved time/access budget; none replaces the JEPA path or introduces VAE/HuBERT as an experimental control. No new optional extension begins after 2027-02-01; optional results target freeze by 2027-02-15. A selected front-end comparison would compare Re/Im STFT with **one** predeclared alternative under [evaluation §17.5](evaluation.md#175-selected-input-representation-comparison), not a factorial cross with SSL.

### 13.5 Three-stage JEPA protocol and gating

**Status:** method direction agreed; precise budgets, Stage-1 run composition, teacher-token layout, mask law and hardware are still evidence-gated. JEPA here denotes a predictor of stop-gradient/EMA *continuous latent* targets; the source/probe signal alone is not the actual receiver-specific direct-path recording. One shared encoder `E` processes each channel independently on a common time base, without coordinates or per-channel arrival alignment. Stage 2 learns Fusion with `E` frozen. Stage 3 has two **parallel** descendants of the same Stage-2 checkpoint, not a 3a→3b sequence. Neither predictor nor EMA teacher is deployed.

#### 13.5.1 Access, references and eligibility

- **S — strict sim-only:** every SSL fit, teacher/EMA, normalizer, probe, checkpoint/architecture choice and labelled supervised fit uses only permitted simulation development groups; separate fixed metrology/calibration can be supplied identically to comparators. Final real and simulated groups stay sealed. The S model's later sealed real evaluation is zero-shot.
- **R — separately authorized unlabelled real development:** release files/groups and lawful purpose *before* access; split by session/deployment **before** channel/window extraction; no sealed group, azimuth labels, simulator tuning or retrospective threshold selection. Record every normalizer, teacher, pretraining and selection fit. R-assisted performance is not S zero-shot even if no angle labels are used.
- **E1 — labelled real adaptation:** independently approved real development groups and label budget. Freeze and report S and any R outcomes separately, never reclassify sealed groups. The winter field data and physically measured linear-array sector remain mandatory.
- Simulate/store `X_m=D_m+R_m+N_m` with receiver-specific direct `D_m` including propagation time and phase, plus component/provenance checks. A/S uses `D_m` as latent teacher input only in simulation. Real A/R would use **estimated** `D_hat_m` from a known probe, only after bench/simulation and real-development resolvability, calibration, TDOA/phase uncertainty, rejection and coverage gates predeclared in [direct-path review](../../../outputs/direct_path_real_jepa_literature_review.md); until then **unverified/not authorized**. Synchronization/preamble detection alone is not enough. Failure keeps A/S only, with B/R as a conditional observed-target real alternative. A/R is an R-assisted recipe, not new S evidence.

#### 13.5.2 Stage 1 — single-channel encoder, before any Fusion SSL

**A/S:** online `E_theta(X_m)` and temporary predictor estimate `sg(E_EMA(D_m))` for the same receiver/window. D is phase- and delay-aligned with X by the simulator's physical clock; E output remains an unpooled TF grid. **B/R (or matched B/S control):** current observed window predicts EMA features of a **future observed**, not clean, window of the same channel. Define physical offset and ensure disjoint raw/filter/STFT support; do not generate both views by encoding a complete record then slicing. A and B are *alternative task/data recipes*: whether separate runs or A/S→B/R continuation, what checkpoint feeds Stage 2, the B/S-vs-B/R control, regularizer, seed plan and matched update budgets are **TODO: development decision before launch**. B/R requires R release and is not presumed available. Do not silently train a combined A+B loss or require VAE/H comparisons.

**E gate first:** on independently grouped simulated development/reporting scenes, freeze E and fit a predeclared small pairwise probe over two independently encoded channels; test accessible signed TDOA and circular relative phase from full E features, first under a controlled direct plane wave and then noisy/multipath/perturbed-calibration cases. Keep a **common** signal clock and registration; do not independently align each sensor. Report direct-D vs observed-X targets separately, probe fit/selection groups, median/p95/coverage/failures by angle and aperture, feature dispersion/rank and anti-collapse diagnostics. Compare under matched probe capacity/data/budget with raw-signal and untrained-E controls. A weak probe does not prove information *cannot* exist, but a failed predeclared delay/phase gate blocks claims of a phase-competent E and the Stage-2 main pilot until a documented design correction/recheck. Thresholds **TODO: justified by physical DOA error and development data, not final test**.

#### 13.5.3 Stage 2 — random subarray predicts full-array latent token grid

With a Stage-1 checkpoint that passes the E gate, freeze E. For an eligible scene with `N_good>=3` synchronized/calibrated channels, choose random `K` and hidden set `H` with `1<=K<=N_good-2`; `V` contains all other valid sensors (at least two). Distribution over K/subsets, two-sensor aperture/aliasing strata and dev-only selection remain **TODO**, not a universal uniform-sampling promise. For missing inputs, use zeroed E features **and explicit availability masks**, preventing masked keys/values and masked pooling in online Fusion. Remove hidden content **before any cross-sensor mixing or data-dependent batch statistics**. Use measured coordinates for both visible positions and masked *query positions*, not channel-slot IDs; no hidden signal goes into predictor/online Fusion.

Online `F_theta` processes visible `(E(X_m),r_m)`. Temporary predictor emits per-sensor TF tokens **at all array positions** before pooling. EMA `F_bar` (only Fusion weights; E frozen) processes all valid channels and provides stopped target tokens **before sensor/TF pooling**. Score only eligible hidden channel/TF positions, e.g. `L2=mean_{m in H, valid f,t} ||P(F_theta(V),r_{1:N},mask)_{m,f,t}-sg(F_bar(E(X_all),r_all)_{m,f,t})||²`; visible predictions do not enter the initial loss. This is a proposal to freeze after interface/pilot, not a completed implementation. Resolve teacher normalization/EMA state, embedding scale, token sizes and anti-collapse diagnostics on development. Predictability of hidden noise/reflections is not guaranteed even when azimuth is identifiable from two elements.

#### 13.5.4 Stage 3 — independent supervised branches and attribution

Start **both branches from the same post-Stage-2 E+Fusion SSL checkpoint** with separate newly initialized `C→C→2` azimuth heads; 3a freezes E+Fusion and fits only the head (representation readability); 3b fine-tunes E+Fusion+head jointly (practical initialized model). Both use identical permitted angular-label groups, raw-component MSE on unnormalized `(a,b)` to `(cosθ,sinθ)`, fixed sector, failure-aware `atan2`, downstream optimization/selection budget where comparisons require it, and independently seeded runs. Never call 3a a demonstrated practical optimum. Full-model supervised-from-scratch on identical permitted data and downstream budget is the practical comparator for 3b; compare 3a with matched Stage-1-only frozen features when feasible, and 3b with Stage-1-only initialized Fusion under disclosed additional costs to isolate Stage 2. Include no-coordinate and classical comparators. Report all SSL pretraining/probe costs in addition to downstream costs; do not claim equal total compute from equal downstream steps. Contrasts S, R and E1 must not be pooled.

#### 13.5.5 Stop rules and reproducibility

No experiments beyond development can interpret a failed clock, label, reference, phase, leakage, collapse, masked-attention, sensor-coordinate permutation or replay check as a positive result. Log group/file/checkpoint/configuration IDs, seed assignment, all teacher/target access, K/mask distributions, numbers of rejected samples, resources and exact gate outcomes. Freeze complete method, data access, thresholds and analysis before sealed evaluation. A stage that does not fit measured budget or lacks permitted data is **not run/blocked**, not evidence of benefit. Field safety and the full dissertation text by 2027-03-31 override optional expansions; approve any alteration of the M1–M5 scientific minimum with the supervisor.

## 14. Geometry Adaptation Protocol

### 14.1 Minimum nominal-array training and optional geometry transfer

The minimum trains and evaluates the compact methods for the measured linear configuration across independent simulated environments and justified calibration/measurement uncertainty. Its purpose is method accuracy, robustness, real-data domain shift and applicability limits. The coordinate/no-coordinate pair remains a component ablation; neither a positive coordinate effect nor transfer to a different layout is required for minimum completion.

If an optional E2 within-linear or reserve E4 simulation-only topology study is selected, preregister its held-out linear layouts/spacing or non-linear simulated topologies and match the methods' conditions and budget. A zero-shot geometry result requires exclusion of that target condition from training, normalization fitting, simulator tuning and selection. It supports only the stated simulation domain, does not resolve physical linear-array ambiguity, and cannot be promoted into real arbitrary-topology transfer by combining it with a fixed-array field result.

### 14.2 Bounded real-development adaptation track

E1 adaptation is optional and must remain separate from zero-shot. Before it starts, the protocol freezes:

- the released real development groups and their small label budget;
- permissible parameters to fit (for example, only a declared adaptation layer or output layer);
- whether any normalizer is refitted (default: no, unless the ledger explicitly permits it);
- compute and seed budget;
- the untouched real evaluation groups; and
- the comparison between adapted and immutable zero-shot results.

No held-out real material, including unlabelled/noise clips, may become an SSL corpus, normalization source, simulator-tuning set, or model-selection aid. Adaptation cannot be presented as a zero-shot result or as evidence of arbitrary-topology transfer.

### 14.3 Common-method conditions and reporting

Every geometry condition supplies the same surveyed source half-plane/identifiable sector to neural and classical methods. Coordinates, calibration, steering assumptions, and any far-field/range restriction are documented in the same array coordinate frame. A missing or unjustified sector means azimuth is structurally ambiguous and the claim must be amended rather than predictions clipped.

For each simulated or real condition, the report records:

- whether it is core S sim-only zero-shot, E1 labelled adaptation, E2 within-linear sensitivity, or E4; for JEPA record stages 1/2/3a/3b, A/S, conditional B/S or B/R and gated A/R, with S versus separately approved R versus E1 access. Distinguish simulation, sim-only field transfer, and real-assisted field evaluation; E4 topology-transfer evidence stays simulation-only;
- the exact allowed data groups and fit operations;
- linear layout/spacing/subset condition and calibration status;
- model/seed pairing and measured compute use;
- all canary and phase-integrity outcomes; and
- the limitation that follows from the available independent units.

### 14.4 Decision gates

The 2026-10-15 hardware/field-feasibility gate determines whether the measured linear-array plan, source sector, synchronization, and positioning are viable. The 2026-11-15 freeze fixes the compact paired design and access policy after bench evidence. The first usable field recording may support development and QA; independently reserved groups are required for final real-data claims. If no usable labelled data or safe access exists by **2027-01-15**, the field lead and supervisor must immediately agree an explicit contingency and claim limit. Essential acquisition is targeted no later than **2027-02-15** without overriding safety; core data, models, tables, and experiments freeze by **2027-02-28**.

No gate guarantees an effect, a publication outcome, field access, or a degree. A null or limited result is reported within the evidence available rather than broadened through new architectures or an unplanned data route.
