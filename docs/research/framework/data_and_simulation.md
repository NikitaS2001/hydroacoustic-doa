# Data, Simulation, And Hydroacoustic Validation

> This document defines the data strategy and simulation limits for the minimum study. The active real-data procedure is [Winter Under-Ice Linear-Array Field Protocol](../../experiments/winter_field_protocol.md). All gates and outcomes remain **not yet evaluated**.

## 15. Data Strategy

### 15.1 Minimum evidence and data hierarchy

The minimum study has two complementary evidence sources:

1. **A controlled, labelled under-ice field dataset from winter 2026–2027.** This is an obligatory and time-critical component, not a later optional validation branch. It uses **only one physical linear array**. The exact bay, array configuration, source, operating band, sample rate, safe access, and metrology resources are unconfirmed until the evidence gates in the [active winter protocol](../../experiments/winter_field_protocol.md) are passed.
2. **A compact, physically checked simulation dataset.** It supports debugging, development, controlled analysis, and simulation-only geometry/condition inference. It does not replace field evidence or prove real under-ice performance.

The simulation inference unit is an independent simulated environment. The real-data inference unit is an independently acquired deployment/session/day group. Windows, overlapping clips, repeated transmissions, bearings, noise overlays, source seeds, and model seeds are nested observations, not independent replicates. The field campaign should seek multiple independently acquired groups, preferably at least three redeployed sessions/days if safe and logistically possible; that is an acquisition target, not a proof of power.

The first usable field group may support development and quality assurance. Independent final groups must be reserved before model selection. If only one usable session remains, conclusions are descriptive and within-session only; they cannot establish across-session transfer by multiplying windows or resampling.

### 15.2 Field dataset: controlled source, linear geometry, and truth

The core field task is single-source azimuth estimation with a controlled labelled source, synchronously acquired multichannel data, and underwater source/receiver geometry. A controlled transmitter/source is a prerequisite to be confirmed by the hardware/source evidence gate, not confirmed equipment. Every accepted labelled block requires:

- phase-preserving multichannel raw recording from a demonstrated shared-clock or equivalently validated synchronous acquisition chain;
- actual underwater positions and depths of all hydrophones and the source in a defined array-centred coordinate frame, with a documented uncertainty method;
- measured array orientation, source range/bearing/depth, source timing/identity, and the preregistered identifiable half-plane/sector;
- calibration evidence for channel order, polarity, gain/phase response, timing/clock drift, and deployment state;
- paired source-on records and pre-/post-source background records, reconciled to an independent source timing log; and
- immutable raw-file provenance, checksums, reopened-file QA, and an acquisition-group access status.

Intended hole positions or planned bearings are not ground truth. Hanging cable motion, depth changes, source orientation where relevant, clock drift, sensor response, and geometry uncertainty must be measured or bounded and carried into interpretation. The field protocol gives the required decision register, schedule, archive procedure, and acceptance disposition.

A physical linear array may have non-uniform spacing. It has structural front/back mirror ambiguity. All compared methods receive the same surveyed identifiable sector/half-plane prior; a compact coordinate-conditioned model and its no-coordinate twin do not resolve an unobserved direction. If the sector cannot be established, report ambiguous direction/direction cosine and agree an amended claim before analysis is frozen. Never claim unambiguous full-circle azimuth and never silently clip predictions.

The geometry, aperture, band, ranges, source extent, and uncertainty must justify the far-field steering approximation actually used. Otherwise use a declared range-aware interpretation/steering model or limit analysis to justified measured conditions. This decision is made from evidence before recording and retained per acquisition group.

### 15.3 Field recording, archive, and quality controls

Each recording condition follows a source-off/background, controlled source-on, and post-source/background schedule. Source-on/off status comes from the transmission log or timing reference, not from a model prediction. Background manifests preserve ambient, ice-related, structure-borne, handling, vessel/equipment, and other observed noise/interference where present. Interruptions, anomalous conditions, aborted blocks, and changes to the array or acquisition chain are retained rather than cleaned from provenance.

Calibration raw data is frozen separately and provided identically to every comparison. For every block, record acquisition device/clock, sample rate and format, channel map, input and preamp settings, start/stop process, calibration state, file checksum, truth record, and operator log. Reopen copied raw files with the intended reader and verify checksum equality, channel count/order, duration, format/rate, and readable samples. Keep independent backup copies under institutional policy; failed checksum, missing metadata, unreadable data, channel mismatch, failed synchrony, or incomplete truth quarantines the block rather than turning it into training data.

Field QA is an evidence-based pass/fail/conditional register covering synchrony and drift, clipping/missing channels, polarity and channel order, gain/phase stability, calibration validity, source timing/identity, underwater truth and uncertainty, operational anomalies, and far-field/range-aware validity. Controlled-data phase/delay consistency checks may reveal channel swaps, polarity inversions, lost synchronization, timing shifts, or gross geometry disagreement. They are safeguards, not license to tune a final model with sealed data.

### 15.4 Access ledger and split reservation

Every acquisition group has an immutable access ledger; overlapping windows, channels and derivatives inherit group status. **S** permits only simulation development for every SSL/EMA/normalizer/probe/model-selection fit and labelled training; sealed simulated and real evaluation groups fit nothing. **R**, only after explicit lawful release of unlabelled real development groups, permits listed JEPA observed-target training and fits, splits by deployment *before* windows/channels and never uses real azimuth labels or simulator fitting. **E1** permits a separately approved labelled real-development adaptation budget and is neither S nor R. Sealed real groups cannot be reassigned to development. If R has no released corpus, record it **not run**, not zero-shot. A/R needs *validated estimated* `D_hat` and access/uncertainty gate; its absence leaves A/S and conditional B/R, never an invented real direct target.

### 15.5 Simulation: bounded development and geometry scope

Develop physically checked independent environments for the measured linear configuration, justified calibration uncertainty and a source/receiver signal simulator with synchronous raw channels. Record `X_m=D_m+R_m+N_m` and checksums/configuration of each receiver-specific direct `D_m` **including delay and phase**. The source waveform or preamble alone is not D. Simulate absent/weak direct arrival and unresolved multipath before deciding whether real `D_hat` is supportable; the [direct-path review](../../../outputs/direct_path_real_jepa_literature_review.md) defines the research question, not an approved real estimator. Stage 1 A/S teacher reads D and online E reads X; optional B/S and B/R use observed future windows with disjoint raw/filter/STFT support. Stage-1 pairwise phase/TDOA gate precedes Stage-2 Fusion SSL and retains independent group provenance. Stage 2 uses valid synchronized `N_good>=3`, random hidden `K∈[1,N_good-2]` and ≥2 visible channels, with masked-only latent loss, no hidden-content leak, pre-pooling EMA Fusion teacher targets. Stage 3 branches from the same checkpoint into frozen-head and joint fine-tuning, each reported separately with scratch and Stage-1-only controls where feasible; [training §13.5](training_strategy.md#135-three-stage-jepa-protocol-and-gating) is canonical.

Deliberately held-out linear geometry/spacing or sensor subset tests are optional E2; non-linear topology evidence can only be an approved simulation-only reserve study. Alternative representations are not a matrix against JEPA: a reserve contrast compares Re/Im STFT with **one** chosen alternative under [evaluation §17.5](evaluation.md#175-selected-input-representation-comparison), same parent sources, physical band and permitted access. No geometry-transfer result is a field acceptance condition.

#### Shared simulation QA and solver safeguards

Predeclare source-presence/DOA eligibility and generation-QA rules before final evaluation. Retain rejected attempts, reasons and bounded replacement procedures; report how exclusions change the sampled conditions. QA must not select easy examples using model predictions or comparative errors. All methods share the same frozen eligible-example manifest; failures on those examples remain in the comparison under the evaluation contract.

Simulation safeguards apply independently of the eventual solver stack:

- **Per-sensor physics:** calculate the multipath response at each hydrophone's own position. Do not synthesize the propagation dataset by shifting, phase-rotating or interpolating a different hydrophone's channel; this loses receiver-specific path amplitudes and path structure. Analytical direct-path cases are diagnostics, not substitutes for multipath scenes.
- **Delay and phase fidelity:** preserve continuous arrival delays through serialization and fractional-delay synthesis; nearest-sample rounding is not acceptable. Establish timing, phase and amplitude tolerances from the operating band and measurement/error budget, and check full-multipath and frequency-grid convergence, not only first-arrival agreement. Document whether solver amplitudes already include propagation phase so it is applied exactly once. Broadband synthesis must preserve linear convolution, a common timing reference and all paths contributing to the selected crop; circular wrap and independent sensor realignment are not acceptable.
- **Batching integrity:** a multi-receiver solver call may replace separate receiver calls only after equivalent full-multipath responses are demonstrated under the selected tolerances. Restore explicit sensor identities if the solver reorders receivers. Resource estimates must account for receiver and frequency evaluations, including convergence checks.
- **Physical scope:** justify propagation dimensionality, range/lateral dependence, boundary conditions and omitted effects for the simulated environments. A common 2-D range-depth representation cannot silently stand in for unmodelled horizontal refraction or laterally varying conditions.
- **Solver checks:** qualify the chosen implementation with analytical/reference cases and numerical-convergence evidence. If an accelerated port is used, check it against its reference implementation; this establishes port equivalence, not independent physical validation. Any independent cross-solver comparison must cover compatible physics and boundaries. Unresolved discrepancies limit the corresponding claims.

Pin the implementation, inputs and check artifacts under the [reproducibility requirements](evaluation.md). Solver selection and numerical tolerances require development evidence; reproducible computation alone does not establish ice fidelity.

### 15.6 Ice, boundary, noise, and sim-to-real limits

BELLHOP is a candidate for physically motivated propagation, not an already validated under-ice simulator. A pressure-release free surface is not equivalent to ice. Each simulation configuration must state its surface/boundary assumptions; whether ice structure, roughness, or ice-related acoustic/structure-borne noise is represented; the evidence for that representation; and the resulting sim-to-real limitation.

Field backgrounds and operational observations should preserve ice-contact/structure-borne, drilling/deployment/recovery, wind/ambient, vessel, and equipment noise evidence. Such observations contextualize domain shift but do not validate a detailed ice-physics model. Without an ice-boundary validation study, claims must remain generic simulation/domain-shift claims rather than claims of faithful ice propagation.

Separate sensor-level noise, coherent acoustic interferers, and recorded multichannel backgrounds in provenance and interpretation. A coherent acoustic interferer needs its own spatial propagation or a suitable multichannel recording; independent sensor noise is not a substitute. Preserve the spatial relationships in recorded background overlays. These corruptions remain nested draws, not independent environments or real-data DOA validation.

For any simulated SNR/SIR condition, freeze the measurement band, filter, active-sensor set, time window and aggregation rule. Let `P_s` and `P_n` be the mean squared clean-target and unscaled-noise samples over that same band, window and sensor set. For positive finite powers and requested SNR in dB, use `a = sqrt(P_s / (P_n * 10^(SNR_dB / 10)))`. Apply one scalar `a` to the entire multichannel noise realization, not independent scalars to channels or frequency bins; this preserves its inter-channel ratios and covariance structure. For SIR, replace the noise component with the spatially propagated interferer and record the ratio separately.

Record the requested ratio, applied scalar and achieved in-band ratio, both array-wide and per sensor. Measurement filtering is not silently substituted for the model front end; if an analysis uses a different band, label its measured ratio separately. Zero in-band target power gives an undefined relative SNR, not a denominator to repair with an epsilon: apply the predeclared source-presence/eligibility rule and report absolute noise power. A nonzero target with no noise is explicitly clean; a zero-power noise draw cannot realize a finite requested SNR. On field recordings, distinguish an estimated SNR from a known simulated component ratio and document the estimator and its assumptions.

### 15.7 Calendar, minimum acceptance, and contingency

The controlling plan is [Roadmap And Success Criteria](roadmap.md) §§25–30 and the active [winter protocol](../../experiments/winter_field_protocol.md):

- by **2026-10-15**, resolve hardware/source/array/field-access and geometry feasibility;
- by **2026-11-15**, freeze the bench-validated primary band/sample rate/sector/representation/model budget, calibration, QA, split, and analysis contract;
- by **2026-11-30**, complete end-to-end laboratory rehearsal, including raw-file reopen, QA, and backup;
- conduct the primary campaign from **December 2026 through 2027-01-31** at the earliest professionally authorized safe opportunity; December is not a safe-ice forecast;
- at **2027-01-15**, escalate immediately to supervisor and field lead if no usable labelled data or safe access exists;
- reserve **2027-02-01..15** for safe necessary reacquisition only, with no safety override;
- freeze core data, models, tables, and experiments by **2027-02-28**; and
- complete the full dissertation manuscript by **2027-03-10** and final text/traceability by **2027-03-31**.

The minimal labelled field dataset is accepted only when its evidence-gated controlled conditions have complete underwater truth/uncertainty, phase-preserving raw multichannel files, matching backgrounds, calibration/QA disposition, immutable provenance, and separated development and final-evaluation access. The number of blocks, sensor count, band, and source-condition grid are not invented quotas; they are part of the pre-campaign decision register.

If authorised safe access or usable labelled data is unavailable, the real-data minimum is incomplete. Simulation must not silently replace the field campaign. The candidate, supervisor, and qualified field lead must document a revised claims-limited scope, missing evidence, and unresolved adequacy; no later campaign, degree, or publication outcome is promised.

---

## 16. Hydroacoustic Validation Philosophy

### 16.1 What each evidence source can establish

Simulation can establish only controlled simulation-stage findings under its stated environment, propagation, geometry, and noise assumptions. It is appropriate for debugging, paired supervised-model comparisons, complex-STFT feasibility, MVDR/Capon and MUSIC comparisons, Bartlett diagnostics, and bounded linear-layout sensitivity. It cannot establish that an under-ice field system works.

The measured field linear array evaluates real performance and simulation-to-real domain shift on that array under the registered sector and range interpretation. It cannot establish arbitrary physical-topology transfer because no non-linear physical array is in the programme. A controlled linear sensor subset/spacing study may be a within-linear optional extension, not a separate field geometry or topology-transfer result.

The compact supervised coordinate-aware/no-coordinate pair, MVDR/Capon and MUSIC remain the field-minimum comparators on Re/Im STFT and the physically identifiable linear sector. The main JEPA research path adds Stage-1 E gate, Stage-2 Fusion SSL, Stage-3 parallel frozen-head/joint descendants and matched scratch controls, never replacing the minimum field experiment. No result from simulation, R assistance or fixed-array data demonstrates transfer to an unmeasured physical topology.

### 16.2 Valid real-data evaluation

Before final-group access, freeze the methods, calibration use, sector/range rule, preprocessing, model budget, and analysis plan. Evaluate at the independent acquisition-group level. Repeated transmissions and windows can describe within-group variability but cannot create independent evidence.

The primary real-data angular error is circular angular distance,

`abs(atan2(sin(delta), cos(delta)))`,

reported in degrees within the physically identifiable preregistered sector. Do not silently clip predictions to make an error smaller. Report per-unit median and p95 error, failure/coverage, source/receiver truth uncertainty, sector/mirror limitation, calibration status, and range/far-field interpretation. Report paired model contrasts in degrees at the independent-unit level. Confidence intervals are appropriate only when their assumptions are supported by the actual number and structure of independent groups; few groups require descriptive bounded reporting rather than spurious bootstrap certainty.

Apply the common failure and seed-aggregation rules in [evaluation.md](evaluation.md): all methods use the same fixed eligible examples, failed estimates receive the maximum circular-error penalty in the primary paired statistic, and valid-only errors/coverage are also retained. Do not let a method improve its comparison by silently omitting hard examples or treating seeds as independent field groups.

The final report separately labels simulation, S zero-shot simulation-to-real, optional E1 adaptation, separately authorized unlabelled R-assisted JEPA, and sealed real-test results. It states whether the exact bay is confirmed, what conditions were actually recorded, every unevaluated/failed gate, and whether independent final groups existed. No claim of SOTA-wide superiority, full-circle azimuth, non-linear physical transfer, detailed ice-model validity, dissertation acceptance, degree, or publication outcome follows from this protocol.

### 16.3 Optional work boundary

At most one *optional* E1/E2/E3 or reserve front-end/topology extension may be active only if the winter minimum, main JEPA integrity gates and writing are secure. No new optional work starts after 2027-02-01; optional results target freeze by 2027-02-15. The obsolete five-encoder E4 cap/slate does not bound the main JEPA path; measure resources and seek supervisor schedule approval. Never omit a failed E gate or silently convert sealed data to R.

### 16.4 Unevaluated status

No simulations, hardware feasibility demonstrations, safe field access, calibration results, recordings, or real-data evaluation results are asserted here. The evidence gates, uncertainty records, access ledger, and archived acquisition groups in the winter protocol are prerequisites for any real-data conclusion.

---
