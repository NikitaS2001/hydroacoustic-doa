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

Every acquisition group, including background and unlabelled content, has an immutable ledger entry specifying permitted uses: calibration, development/QA, training, normalization fitting, simulated-noise overlay source, optional E1 adaptation, optional E4 R pretraining, or sealed final evaluation. Derived files and overlapping clips inherit the source group's status.

**S** is the default strict simulation-only E4 track: every fit—encoder/EMA teacher, VAE decoder and variance branch, HuBERT-style descriptor scaling and codebook, normalizers, probes, checkpoint or hyperparameter selection, and simulator tuning—uses only permitted simulated development material. Separately acquired fixed instrument calibration/survey is allowed equally. Sealed real groups, including unlabelled/background/source-off material and every channel or crop derived from them, fit nothing.

**R** is an optional, separately approved, unlabelled real-pretraining track within E4's total budget, not E1 adaptation and not an automatic expansion of the study. Before it begins, release actual lawful real development groups/corpus with file, session, time, and channel identities and split groups before windows or channels. R may supply observed material to VAE, HuBERT-style, or B pretraining, but cannot supply A/A+B direct targets without real paired references and does not authorize real angular-label fine-tuning or real simulator tuning. The ledger declares every permitted fit, including whether normalization, descriptor scaling, or codebook fitting changes from the S default; otherwise S normalizers remain fixed. If no approved corpus exists, R is not run. Sealed real groups must not enter either track; a group does not move from sealed evaluation to development.

Zero-shot simulation-to-real evaluation, optional E1 labelled adaptation, and optional E4 R pretraining are separately named tracks with separate access ledgers. Real-noise overlays on simulated controlled sources may improve robustness training but are not real-data validation and do not convert a simulated source into a field observation. The minimal R data-source contrast is preregistered **B/S versus B/R** with a fixed simulated-plus-real mixture, paired initialization, matched pretraining update budget, common diagnostic/downstream protocol, and recorded real hours/examples, mixture, data/compute access. It is distinct from an objective comparison; VAE/H may use the same approved R access only if a matched comparison is explicitly selected, never by automatic factorial expansion.

### 15.5 Simulation: bounded development and geometry scope

Simulation provides a controlled development environment, not an automatic numerical programme. Build a resource-bounded set of physically checked environments with per-sensor propagation sufficient to preserve inter-sensor delay, phase, amplitude, and multipath. Use controlled signal conditions and noise/interference only to the extent required by the frozen research question and local compute/storage budget.

The minimum simulation uses the measured linear configuration across independent environments, with justified calibration and coordinate-measurement uncertainty. It supports method comparison and applicability analysis, not a compulsory geometry-transfer endpoint. Deliberately held-out linear layouts/spacing or sensor subsets are optional E2 studies. If E4 is selected, it is instead the bounded two-stage channel-encoder pretraining study, Re/Im STFT versus one chosen alternative front end, **or** non-linear topology transfer that is simulation-only; these alternatives are not combined. IQ is the first alternate input, with the real waveform as the next control candidate, not another automatically approved experiment. None is necessary for minimum completion or evidence of transfer to a new physical field geometry.

Physical band, sampling, source waveform, receiver/source configuration, array spacing/aperture, simulation count, numerical front-end settings, and resource budget must be selected from named evidence gates: source and hydrophone response, sampled-channel/aliasing constraints, surveyed field geometry, bench phase-preservation tests, simulation convergence/feasibility evidence, and available compute/storage. Until such evidence is recorded, these settings are unresolved. The primary representation itself is **Re/Im STFT**; the candidate catalogue does not authorize arbitrary replacement.

Simulation splits separate independent environments before nested source/waveform, channel, crop, and overlay draws. Hold out the environmental factors relevant to a stated generalization claim. A noise overlay, repeated channel use, or different waveform realization does not create a new environment. Maintain complete replay provenance for each derived example: environment/configuration, source draw, per-sensor propagation, overlay, preprocessing, and generator version.

Reusable source/noise realizations and their derived crops or augmentations must not cross development/final split boundaries. Within an allowed split and a fixed environment/source/receiver configuration, validated clean propagation responses may be reused for different waveforms and ordinary noise overlays; these do not require new propagation runs or create independent units. Coherent interferers require their own spatial response. Size the dataset from measured runtime, I/O and storage, including receiver/frequency evaluations and convergence checks.

Each derived-example manifest records its parent identities, realized source/noise/interference parameters, random-number algorithm and stream/seed derivation, generator version, crop/filter/scaling settings and component/output checksums. Check replay under the pinned environment before accepting the dataset. Training augmentation may vary reproducibly by epoch; evaluation realizations are frozen and must not be regenerated in place. A changed generator produces a new versioned dataset, not a mutation of the sealed set.

#### Representation provenance and optional comparison

Keep one physical observation and derive the declared representations under [architecture §8](architecture.md#8-input-representation-strategy). Record representation identifier, source channel/order, physical duration/band, original and processed rates, calibration and amplitude units, shared-scale fit provenance, tensor axes/dtypes, filter/transient/raw-sample support, and exact transform parameters. STFT metadata include window, hop, FFT, bins, normalization, centering and padding; IQ additionally records analytic conversion, physical centre frequency, oscillator phase/time reference and decimation. A lower-rate IQ tensor is not a shorter observation, and an adjacent crop or alternate transform is not a new independent unit.

Observation-crop duration/hop and raw support are distinct from STFT frame support and from the encoder attention neighbourhood. The selected [hybrid channel encoder](architecture.md#91-shared-model-contract) initially uses full temporal attention only within each bounded input window. Derive each input from its declared raw support before contextual encoding; do not encode an entire recording and then crop its features. H's student masks precede the stem and contextual mixing; B's current and future windows are encoded independently without cross-window signal caches or normalization. Sliding crops retain their parent-group identity and do not constitute a local-attention configuration.

If the E4 representation option is selected, freeze the actual primary-versus-alternative contrast and one reference training regime under [evaluation §17.5](evaluation.md#175-selected-input-representation-comparison). Generate views from the same permitted parent scenes/records and retained physical band, preserving signal/reference alignment. Do not create separate easier scenes for each input or allow a nonlocal transform to see undeclared context. A catalogue entry is not permission to fit a new normalizer on sealed data, release a real corpus, or cross all representations with VAE/H/A/B/A+B.

#### E4 two-stage channel-encoder pretraining provenance, if selected

The optional E4 study follows [Training Strategy §13.5](training_strategy.md#135-two-stage-channel-encoder-pretraining-study). Stage 1 pretrains the same transferable, shared-sensor channel encoder `E` as **VAE**, HuBERT-style **H**, JEPA **A**, JEPA **B**, and JEPA **A+B**; it has no full Fusion/DOA-head training and no supervised-from-scratch `0`. Freeze `E` after pretraining for matched diagnostic probes. Stage 2 then initializes Fusion and the azimuth head anew and jointly trains `E`, Fusion, and one azimuth head for all five pretrained encoders plus the matched supervised-from-scratch `0` regime. The coordinate-free twin remains outside this matrix. Stage 1's VAE reconstructs observed `X` through a training-only decoder/variance branch and transfers deterministic posterior mean `mu=E(X)`; H predicts fixed masked discrete units derived from an offline codebook of phase-bearing real/imag complex-STFT descriptors; neither declares a direct-path reconstruction target. H descriptor scaling/codebook and mask/support, VAE likelihood scale and latent-usage/collapse monitoring, JEPA regularizer/diagnostics, and all selection rules are frozen from permitted track material before diagnostics.

For every simulated parent scene, preserve `X[m,k]=D[m,k]+R[m,k]+N[m,k]` and record the observed assembly and component identities/checksums. A sends observed `X[m,k]` to a predictor targeting the EMA encoder's stop-gradient direct, noise-free same-window `D[m,k]`; B uses observed `X[m,k]` with declared physical `delta_t` to target only the EMA encoder's stop-gradient future observed window `X[m,k+1]`; A+B uses both separate predictors with declared normalized weights. B context and target have disjoint raw-sample support including STFT/filter support, and the target encoder receives only the future window. Common phase augmentation is aligned across sensors, context, and targets; independent channel phase rotations, normalization, random convolution, or realignment are prohibited. Missing/invalid `D` makes the A/A+B reference gate ineligible and is recorded without fabricating a direct target or silently narrowing the frozen core downstream cohort. A/A+B therefore use privileged simulator references, whereas VAE/H/B use observed material; temporal access and all data access remain disclosed, so this is a complete-recipe comparison rather than a loss-only or equal-information claim.

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

The compact supervised geometry-conditioned model and matched no-coordinate model are a single core pair. **Re/Im STFT** is the primary phase-bearing input, with numerical processing and phase integrity subject to the bench gate. MVDR/Capon and MUSIC are required classical comparisons; Bartlett is diagnostic. All methods receive the same calibration and identifiable-sector prior. The E4 two-stage channel-encoder study is an optional bounded extension on that same Re/Im STFT representation: Stage 1 compares frozen VAE/H/A/B/A+B encoders with diagnostic probes, and Stage 2 compares those five initializations plus supervised-from-scratch `0` on the fixed coordinate-aware core. The unchanged no-coordinate twin is not crossed with SSL. One selected alternative input (IQ first; real waveform as the next control candidate) or arbitrary-topology simulation transfer is the alternative E4 choice. These, wide representation sweeps, and adaptation cannot be used to rescue a null core result.

### 16.2 Valid real-data evaluation

Before final-group access, freeze the methods, calibration use, sector/range rule, preprocessing, model budget, and analysis plan. Evaluate at the independent acquisition-group level. Repeated transmissions and windows can describe within-group variability but cannot create independent evidence.

The primary real-data angular error is circular angular distance,

`abs(atan2(sin(delta), cos(delta)))`,

reported in degrees within the physically identifiable preregistered sector. Do not silently clip predictions to make an error smaller. Report per-unit median and p95 error, failure/coverage, source/receiver truth uncertainty, sector/mirror limitation, calibration status, and range/far-field interpretation. Report paired model contrasts in degrees at the independent-unit level. Confidence intervals are appropriate only when their assumptions are supported by the actual number and structure of independent groups; few groups require descriptive bounded reporting rather than spurious bootstrap certainty.

Apply the common failure and seed-aggregation rules in [evaluation.md](evaluation.md): all methods use the same fixed eligible examples, failed estimates receive the maximum circular-error penalty in the primary paired statistic, and valid-only errors/coverage are also retained. Do not let a method improve its comparison by silently omitting hard examples or treating seeds as independent field groups.

The final report separately labels simulation, S zero-shot simulation-to-real, optional E1 adaptation, optional E4 R-assisted pretraining, and sealed real-test results. It states whether the exact bay is confirmed, what conditions were actually recorded, every unevaluated/failed gate, and whether independent final groups existed. No claim of SOTA-wide superiority, full-circle azimuth, non-linear physical transfer, detailed ice-model validity, dissertation acceptance, degree, or publication outcome follows from this protocol.

### 16.3 Optional work boundary

At most one extension may be active after the minimum pipeline and labelled-data quality work are secure, no core gate or writing milestone is endangered, and no new extension begins after **2027-02-01**. Candidate extensions are: small real-development adaptation/label budget; controlled linear subset/spacing sensitivity; modest ice/boundary or calibration sensitivity; or E4, which is either the bounded two-stage VAE/H/A/B/A+B channel-encoder study, Re/Im STFT versus one selected alternative input, or arbitrary-topology **simulation-only** transfer. E4 alternatives are not combined; naming three principal representation candidates does not approve three arms or a representation-by-pretraining factorial. E4 retains the existing cap of five focused working days and may be frozen on **2027-02-15**; if the complete study cannot fit, defer it or explicitly revise the protocol before testing rather than dropping variants, data-access disclosures, or the channel-encoder study's Stage 2 supervised-from-scratch control.

### 16.4 Unevaluated status

No simulations, hardware feasibility demonstrations, safe field access, calibration results, recordings, or real-data evaluation results are asserted here. The evidence gates, uncertainty records, access ledger, and archived acquisition groups in the winter protocol are prerequisites for any real-data conclusion.

---
