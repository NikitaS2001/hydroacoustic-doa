# Evaluation, Baselines, And Protocols

> This document specifies evidence for the scoped dissertation study. It does not report completed experiments or passed gates. The authoritative calendar and scope are in the [roadmap](roadmap.md); acquisition, calibration, data custody, and real-data evaluation details are in the [winter field protocol](../../experiments/winter_field_protocol.md).

## 17. Baseline and Fair Comparison Protocol

### 17.1 Study Boundary and Comparators

The core study is a single-source azimuth experiment on a **real linear hydrophone array** recorded under ice in winter 2026–2027, supported by controlled simulation. The measured array need not be uniformly spaced. Its geometry, aperture, hydrophone count, calibration, source configuration, and usable band remain to be measured and frozen; it must not be described as a ULA unless the survey establishes that fact.

The required classical comparators are **MVDR/Capon** and **MUSIC**, using the same identifiable-sector prior, measured/simulated coordinates, calibration information, input duration, and development/test split as the neural comparison. Covariance estimation, diagonal loading, source-count assumption, steering convention, sound-speed/range assumption, and grid construction must be frozen before final testing. **Bartlett (delay-and-sum)** is a diagnostic only: it can expose sign, steering, coordinate, and calibration errors, but cannot establish a competitive advantage.

Broadband baseline settings must also specify the retained frequency bins, covariance snapshots, per-bin spectrum normalization, cross-frequency aggregation and peak selection. Use the same permitted signal band and observation duration for the comparison; methods may use their own documented front ends. Select numerical settings on development data, check steering/sign conventions on controlled cases, and freeze them before accessing final results.

The required neural contrast is one compact supervised geometry-conditioned model with a matched no-coordinate twin. They must differ only in geometry information; representation, parameter budget as far as feasible, optimization, stopping rule, seeds, and ordered evaluation units are matched. **Re/Im STFT** is the primary phase-bearing input; its numerical front-end settings require pre-campaign bench evidence. This narrow slate can show a bounded comparison under the documented conditions; it cannot support SOTA-wide or universal neural superiority claims.
If the E4 channel-encoder option is selected, Stage 1 pretrains the same transferable, shared-sensor encoder `E` as VAE, HuBERT-style **H**, JEPA **A**, JEPA **B**, and JEPA **A+B**, then freezes it for matched diagnostic probes; it contains neither full Fusion/DOA-head training nor supervised-from-scratch `0`. Stage 2 compares all five pretrained initializations plus the same full model trained supervised-from-scratch (`0`): Fusion and the azimuth head are initialized anew, and `E`, Fusion, and one azimuth head are jointly trained under identical supervised labels, preprocessing, optimizer, schedule, and paired seed contract. Pretraining-only decoder, variance, codebook classifier, predictor, and EMA branches are removed. The core no-coordinate twin remains unchanged and outside the SSL matrix. The canonical contract is [Training Strategy §13.5](training_strategy.md#135-two-stage-channel-encoder-pretraining-study).

The neural pair's selected shared-sensor encoder is the hybrid Conformer-like scaffold in [architecture §9.1](architecture.md#91-shared-model-contract): complex Conv2D stem, real temporal Conformer blocks with full attention inside each bounded window separately per frequency, and local frequency mixing. Match its configuration and observation/attention scope across the pair and, if selected, all E4 pretraining regimes and downstream `0`. This core choice is not an extra E4 architecture comparison; Fusion and the azimuth head remain separate.

Its selected [coordinate-aware channel-attention Fusion](architecture.md#102-array-aggregation-requirements) is also matched: one initial block, four heads, width `C` and FFN width `2*C`, coordinate/frequency token encoding, masked sensor mean and then valid-TF mean. The no-coordinate arm supplies only a shared zero input to the coordinate MLP; frequency information remains common. Fixed ULA mirror pairs and additional pairwise geometry biases are not part of the selected Fusion. Architectural support for different geometries/counts is not a geometry-transfer result or a removal of the single-source/sector boundary.

The single-azimuth head, `(cos(theta),sin(theta))` target and batch-mean raw-component squared-error training loss are fixed by [architecture §12](architecture.md#12-downstream-heads). Both neural arms, and any E4 Stage 2 downstream model, use the same `C -> C -> 2` head, target/reduction and finite/degenerate vector decoding rule. Training MSE is not the primary evaluation metric; the circular error and failure-aware policy in §18.1 remain authoritative.

Conditional methods such as Root-MUSIC, ESPRIT, SRP-PHAT, sparse estimators, or matched-field processing are optional only when their physical assumptions and information access are documented. A method using environmental replicas, oracle source count, or other privileged information is reported separately, never as an equal-information result.

### 17.2 Fairness and Information Control

Every matched comparison must use:

- the same coordinate frame, identifiable azimuth sector, timing and calibration version, source-presence policy, and preprocessing policy;
- the same independent simulated environment or field-acquisition group manifests, with all tuning confined to development data;
- the same labelled rows and declared exclusion/failure policy; and
- separate reporting for simulation, zero-shot field evaluation, and any optional adapted field evaluation.

Calibration is frozen separately and supplied identically to every comparator. No sealed real group—including unlabelled clips or background noise—may enter normalization fitting, simulator adjustment, representation learning, training, or model selection. Real-noise overlays on simulation are augmentation evidence, not field validation.

For E4, A/A+B have declared privileged simulator-derived direct references, whereas B predicts only a future observed window and VAE/H use only observed signal material. This precludes attributing an advantage solely to pretext loss or claiming equal teacher information; bounded comparisons of the complete declared recipes remain valid. **S** is the default strict simulation-only track: every fit, including encoder/teacher, VAE branches, H descriptor scaling/codebook, normalizers, probes, and selection, uses permitted simulated development material. An optional explicitly approved unlabelled **R** track is not E1 adaptation and is not automatic: it may release real development groups, split before windows/channels, to VAE/H/B only; it cannot create A/A+B direct targets, authorize real angular-label fine-tuning, or tune the simulator. Sealed real material fits nothing. The separately preregistered B/S-versus-B/R data-source contrast uses a fixed simulated-plus-real mixture, paired initialization, matched update budget, and common diagnostic/downstream protocol; it is distinct from the objective comparison and records real amount and access. Without an approved corpus, R is not run. S-trained E4 models may be evaluated on untouched real groups after the complete method/seed/preprocessing/analysis slate and access ledger are frozen; that is S zero-shot simulation-to-real evaluation, not simulation-only topology evidence.

A CRLB may be reported only as a diagnostic reference for a likelihood, steering model, noise covariance, snapshot independence, and nuisance treatment that match the reported condition. It is not an algorithmic comparator. Do not compare a median or p95 error with a CRLB, and do not use a free-field bound to certify a multipath or ice-boundary result.

### 17.3 Limited Comparator Interpretation

MVDR/Capon and MUSIC loss cases, numerical instability, sector ambiguity, and sensitivity to calibration are findings to report, not grounds to retune after the sealed test. Likewise, a neural null result, an E4 null result, or loss to either comparator is a valid bounded result. Additional architecture sweeps, extra SSL objectives, large models, or an expansive external baseline search are not a rescue path for the core contrast.

The no-coordinate twin is an information ablation. Diagnose its observable target before the final comparison: an unordered sensor set on a symmetric linear layout can lose signed-direction information even after the physical half-plane ambiguity is restricted. Record the resulting indistinguishable cases or attainable-error limitation on controlled development data. Do not sell recovery of deliberately withheld information as architectural novelty or superiority over a strong fixed-layout neural estimator; that broader neural claim would need an appropriate additional comparator and a pre-test scope decision.

### 17.4 Stage 1 frozen-encoder diagnostic contract

The main Stage 1 comparison evaluates the five frozen encoders in track S. An explicitly released R contrast covers only its declared compatible variants, not an automatic five-variant real-data matrix. Each corresponding task uses the same low-capacity pairwise readout class, fit data, budget, preprocessing, and seed rule. The readout compares two independently encoded channels or controlled signal views; it is not a deployed head, full Fusion, or single-channel DOA estimator.

Read out the final real feature grid after the complete hybrid encoder, not just its complex stem or an intermediate Re/Im representation. Inspecting a phase-bearing input is not evidence that the later attention, normalization, frequency mixing, or subsampling retains usable phase/delay information. The final real coordinates have no prescribed complex-pair interpretation, and exact complex phase equivariance is not an assumed pass criterion.

Separate groups for probe fitting, checkpoint/settings selection, and diagnostic reporting before window/channel extraction. Every fit, including H descriptor scaling and codebook generation, has declared provenance. No final simulated or real DOA groups enter these operations. Any diagnostic data used for a subsequent model decision remain development relative to Stage 2. B/S-versus-B/R uses the same probe fit/development/reporting corpus to isolate the pretraining-data contrast.

For every probe table, declare the target source before fitting: observed-mixture `X` phase/delay or a simulator direct-reference `D` phase/delay. The observed and direct targets answer different questions and are reported separately; neither is silently substituted for the other. Direct-reference targets require valid `D`, source-presence, timing, and synchronization eligibility; missing/invalid `D` is reported as unavailable for that diagnostic and blocks the associated A/A+B reference gate, but does not fabricate `D` or silently remove the example from the frozen core downstream cohort. Relative phase uses circular error and relative delay uses absolute error. For each target and justified noise, multipath, and calibration condition, report median, p95, failures, coverage, and physical-evidence-derived thresholds. Do not interpret the argument of an arbitrary latent coordinate as physical phase.

Direct-path controlled delay/phase toys diagnose whether relational cues are accessible; they do not replace per-sensor multipath production simulation or establish denoising, broadband-delay retention, or downstream azimuth performance. Robustness curves must retain the target distinction and the declared source/receiver, noise/interference, calibration, and access conditions. Stage 1 diagnostics guide only the stated representation interpretation; the Stage 2 DOA comparison remains the final model evaluation under the established error, failure, and independent-unit rules.

### 17.5 Selected input-representation comparison

The catalogue in [architecture §8](architecture.md#8-input-representation-strategy) distinguishes the mandatory Re/Im STFT input, the first alternative baseband IQ, and the next real-waveform control. The currently bounded representation option in E4 compares the primary with one explicitly selected alternative. Three principal candidates do not create three compulsory arms. CWT, STFT parameterizations, and magnitude/mel ablations remain separate reserve hypotheses; pairwise spatial features change the single-channel information contract.

Before fitting, freeze the selected contrast, one reference training regime, the intended inference claim, and the following matching rules:

- same permitted source records/scenes, parent groups, signal realizations and target information, with the same calibration, sector, independent-unit splits, and final seal;
- same physical observation duration and retained physical frequency band, not the same tensor length, frame count, or processed sample rate; record IQ carrier/reference conventions and demonstrate that transforms do not introduce undeclared past/future context;
- same declared tuning opportunities, paired seed policy, stopping rules, target definitions, and failure/coverage treatment;
- declared input-block and aggregation interfaces: one-dimensional temporal and two-dimensional STFT processing need not have identical architectures, but feature capacity, effective receptive-field duration, parameter count and optimizer differences must be disclosed;
- measured preprocessing, fitting and inference time, peak memory, storage and actual observation support, including any codebook, decoder, probe or conversion cost used by the chosen regime.

Run controlled phase/delay-integrity checks before interpreting neural performance. Any probe comparison uses the same physical target and declared readout-capacity policy; representation-specific reconstruction/pretext losses do not constitute a common ranking. If DOA is evaluated, use the existing circular-error, independent-unit, coverage and failure rules rather than selecting favourable windows or scoring only successful estimates.

Select or tune only on permitted development groups; catalogue membership and a phase-preservation check are not performance evidence. Report conclusions conditional on the chosen training regime and front-end/encoder combination. If input blocks or architectures differ, do not attribute the whole effect solely to input representation. Do not infer superiority under the other pretraining objectives or replace the frozen core input after final inspection. Expanding beyond the selected alternative or crossing representations with all five pretraining methods requires a pre-test scope/resource revision within the existing gates.

---

## 18. Evaluation Metrics and Evidence

### 18.1 Primary Azimuth Metric and Identifiability

Before final evaluation, the protocol must predeclare a physically identifiable source half-plane or other surveyed sector for the linear array. Within that sector, the primary per-unit angular error is the circular distance

```
e(theta_hat, theta) = abs(atan2(sin(theta_hat - theta), cos(theta_hat - theta)))
```

The trigonometric arguments are in radians; convert the resulting distance to degrees.

Predictions are **not** silently clipped, reflected or relabelled to resolve front/back ambiguity. Each report states the sector, array axis and azimuth convention. If a sector cannot be surveyed and sustained, report ambiguous direction/direction cosine and amend the claim before freeze with supervisor agreement; a full-circle unambiguous-azimuth claim is unavailable. The one-dimensional azimuth interpretation also requires fixed/known elevation or a measured bound showing its effect is negligible for the declared uncertainty. A half-plane prior alone does not remove unknown-elevation ambiguity.

For every independent unit and required method, report median and p95 angular error, valid-prediction coverage, failure rate/reason and ground-truth uncertainty. The primary evidence concerns the compact estimator's accuracy, robustness and limits relative to the declared classical methods on the measured configuration and representative simulation. The coordinate/no-coordinate contrast is a secondary component ablation, not the sole primary endpoint or a geometry-transfer claim. Mean absolute error and RMSE are secondary descriptive measures.

Score every finite prediction against its label without clipping, including out-of-sector predictions, and flag sector violations separately. Non-finite or missing predictions count as failures. For paired method comparisons over the same predeclared eligible examples, assign a failed prediction the maximum circular error of **180 degrees**; also report valid-prediction-only median/p95 alongside coverage so the convention is visible. Ground-truth/recording exclusions are predeclared QA decisions, never selected from a method's output.

For the neural vector head, decode `atan2(b,a)` only for finite components with norm exceeding the predeclared numerical degeneracy threshold `tau >= 0`; exact zero is invalid. Freeze `tau` from numerical/implementation considerations on permitted development data before final scoring and use the same rule for every neural comparison. Degenerate/non-finite vectors and empty valid Fusion observations are missing predictions under the same **180-degree failure-aware convention**, with reasons and valid-only coverage reported separately. Do not let a default `atan2(0,0)` fabricate a valid zero-degree prediction. Any finite, nondegenerate decoded angle is scored as-is, including out-of-sector angles; no normalization, clipping or reflection makes it valid by definition.

For each independent unit `u` and method `m`, define `E_u(m)` as its mean across declared training seeds of the within-unit median failure-aware error; a deterministic classical method contributes its single result, not artificial seed replicates. For each preregistered comparison with reference `b`, report `d_u(m,b) = E_u(b) - E_u(m)` in degrees; positive values favour `m`. Comparisons with MVDR/Capon and MUSIC are reported separately; the no-coordinate reference gives the secondary coordinate ablation. Simulation aggregates use equal independent-unit weights, not window counts; field reports retain every group contrast and may add an explicitly descriptive equal-group mean. Any joint superiority claim must preregister its comparator family and multiplicity treatment before final testing. Seeds are repeated fits, not new environments or acquisition groups. Report tails/failures separately; do not average predicted angles unless an ensemble was separately frozen as a method.

### 18.2 Units, Splits, and Uncertainty

The simulation inference unit is a genuinely independent simulated environment; windows, crops, repeated transmissions, noise overlays, and model seeds are nested observations, not extra independent replicates. The field inference unit is a genuinely independent acquisition group (for example, a deployment/session/day block defined in the field protocol). Overlapping windows, repeated bearings, and transmissions within a group do not create independent field evidence.

Field development groups and sealed final groups are separate. Confidence intervals and paired contrasts are conditional on the observed independent units and must name their count and construction. With few field groups, conclusions are descriptive and bounded; resampling windows cannot manufacture across-session evidence. A single field session cannot demonstrate across-session transfer.

For E4, downstream DOA evidence remains aggregated over the same valid independent environments or field acquisition groups; Stage 1 pretraining examples, codebook fits, probe rows, windows, targets, and seeds are nested observations, not added units. Record variant/track-specific target eligibility and direct-reference availability without changing the frozen core cohort, plus all additional examples, real-access mixture where applicable, reference information, optimization steps, total measured compute/memory/time, and inference resources. Extra SSL data, privileged references, or compute is not a free equal-compute comparison.

Any practical-effect threshold, sample-size target, or power calculation must be justified from pilot or application evidence and frozen before final test. Until a justified threshold and the necessary independent units exist, no power or confirmatory-effect claim is available.

### 18.3 Stratified and Failure Reporting

Report minimum simulation results by independent held-out environment, source condition, azimuth sector, noise/interference and justified calibration/measurement uncertainty for the measured linear configuration. Deliberately held-out layout/spacing contrasts are optional E2 work. If E4 instead selects non-linear topology transfer, report it as simulation-only evidence for the tested class; if E4 selects the two-stage channel-encoder study, separately label S zero-shot and any approved R-assisted results on sealed real groups. Neither is an obligatory primary geometry-effect endpoint or field-topology evidence.

Report field results by independent acquisition group, identifiable sector, source/range condition where valid, quality-control status, and calibration/ground-truth uncertainty. The field question is measured-array performance and sim-to-real domain shift on that one linear geometry—not transfer among arbitrary physical topologies. Preserve and explain failed estimates, excluded rows, coverage loss, and calibration/sector violations.

### 18.4 Claims-to-Evidence and Dissertation Contribution Matrix

| Candidate contribution or claim | Minimum evidence | Limit on interpretation | Status if result is null or incomplete |
|---|---|---|---|
| Reproducible under-ice labelled linear-array dataset and measured-array DOA protocol | Immutable raw files/manifests, calibration and truth-uncertainty record, QA, and independent acquisition groups from the winter campaign | Establishes documented data and protocol quality, not universal deployment validity | Report missing/limited acquisition honestly; it is not replaced by simulation |
| Coordinate component ablation on the measured configuration | Matched compact model/no-coordinate comparison under the frozen conditions and information policy | Secondary component evidence; fixed coordinates and information-induced ambiguity limit interpretation; not a geometry-transfer or standalone novelty claim | Report the contrast without requiring a positive coordinate effect |
| Classical and compact neural methods on the measured array | MVDR/Capon, MUSIC, Bartlett diagnostic, and matched neural pair on sealed field groups | Limited comparator slate; no SOTA-wide superiority claim | Report losses, failures, and domain shift by acquisition group |
| Zero-shot sim-to-real performance | Simulation-trained methods evaluated once on sealed field groups with no field data in training, fitting, selection, or simulator tuning | A measured linear-array domain-shift result only | Report as a negative/partial transfer result if it fails |
| Optional bounded E4 channel-encoder study | Frozen Stage 1 VAE/H/A/B/A+B encoder slate with common phase/delay probe contract and target/access/eligibility manifests; then Stage 2 VAE/H/A/B/A+B plus supervised-from-scratch `0` under matched downstream controls, canonical [Training Strategy §13.5](training_strategy.md#135-two-stage-channel-encoder-pretraining-study), diagnostics, failures, and measured resources | A/A+B have privileged simulated direct references while VAE/H/B use observed material; direct-reference and observed-mixture diagnostics differ, and this is neither a loss-only nor equal-information comparison. S zero-shot and any separately approved R assistance are distinct; a real evaluation is measured-array evidence, not topology transfer | Report a null, loss, diagnostic/reference failure, or defer the complete study; no representation gain, objective advantage, or label saving is promised |
| Optional bounded E4 input-representation comparison | Predeclared Re/Im STFT versus one selected alternative, one reference training regime, matched physical observations/band/duration and access, phase/delay checks, measured resources and the [§17.5 contract](#175-selected-input-representation-comparison) | Conditional on the selected regime and front-end/encoder combination; differing input blocks prevent a pure-representation attribution; catalogue membership is not evidence | Report a null, loss, integrity failure or unrun contrast honestly; no compulsory third arm or cross-product follows |
| Optional real-data adaptation effect | Separate development-only field data, explicit label/access ledger, then untouched sealed field groups | Not a zero-shot result; no claim about adaptation without that separation | Omit if data access/separation is unavailable |
| Optional transfer to unseen simulated geometries | Predeclared E2/E4 study with layouts/spacing/topologies excluded from training and selection | Simulation-only evidence for the tested class; no new physical-array transfer is demonstrated | Omit if not executed; the dissertation minimum is not incomplete for that reason |
| Dissertation contribution adequacy | Supervisor/specialty review of the assembled evidence and claims | Negative results may be scientifically useful but do not by themselves guarantee novelty or degree sufficiency | Obtain explicit review; do not promise adequacy |

Use only `supported`, `partially supported`, `not supported`, or `not yet evaluated` for claim status. The matrix is an evidence ledger, not a promise that any contribution or formal requirement will be met.

---

## 19. Experiment Families

### 19.1 Minimum Scoped Study

The minimum study contains four connected activities:

1. **Bench and protocol readiness.** Verify the selected complex-STFT path is feasible on the available measured signal chain; freeze representation, band, sampling rate, sector, compact-model budget, calibration/QA criteria, and analysis plan by 2026-11-15 after the 2026-10-15 hardware/source/field-feasibility decision.
2. **Controlled simulation.** Use physically checked simulation for debugging, method comparison and justified calibration/measurement uncertainty at the measured linear configuration. Held-out-layout transfer is optional, not a minimum endpoint. BELLHOP is a candidate simulator, not a validated under-ice model; preserve per-sensor phase/delay integrity if it is used.
3. **Winter field study.** Acquire quality-controlled labelled under-ice recordings on the measured linear array at the earliest professionally authorized safe opportunity during December 2026–January 2027, reserving independent final groups. This is a minimum constraint, not a later validation branch.
4. **Frozen evaluation and writing.** Evaluate the required comparator slate, assemble reproducible results and full text by 2027-03-31. The essential-acquisition planning deadline is 2027-02-15; the core dataset/models/tables freeze target is 2027-02-28.

### 19.2 Simulation and Field Tracks

Simulation develops and tests the controlled linear family. It must separate independent environments and preserve source, receiver, propagation, calibration, seed, and preprocessing provenance. It may diagnose simulator sensitivity and support bounded simulation claims. An acoustic pressure-release free surface is not ice; ice boundary behavior and ice-related structure-borne/acoustic noise must be explicit in every sim-to-real interpretation.

The primary field track is **S zero-shot**: neither real development nor sealed field recordings may be used for model training, normalization fitting, SSL, simulator fitting or model selection. The preregistered measured geometry/sector and separate instrument calibration are permitted physical inputs, not target-scene training data; their access is identical across methods except the declared coordinate ablation. Optional E1 labelled adaptation may use only explicitly designated, non-sealed field development data and must keep an access ledger identifying data purpose, labels, preprocessing fitting and every selection use. Optional E4 **R** is separately approved unlabelled pretraining access, not E1: it has a released group-before-window/channel ledger, cannot use sealed material, labels, or simulator tuning, and is reported separately from immutable S zero-shot and E1.

### 19.3 Bounded Optional Extensions

At most one extension may be active after the minimum pipeline and labelled-data quality work are secure: (E1) small real-development adaptation/label-budget study; (E2) controlled linear sensor-subset or spacing sensitivity; (E3) modest measured ice-boundary or calibration sensitivity; or (E4) either the bounded two-stage VAE/H/A/B/A+B channel-encoder study, Re/Im STFT versus one selected alternate front end under §17.5, **or** arbitrary-topology simulation-only transfer. E4 alternatives are not combined; its five-focused-working-day total cap is a scheduling stop rule, not a runtime estimate. IQ is the first representation alternative and the real waveform the next control candidate, not an automatic additional arm. No extension may delay the full text or begin after **2027-02-01**; all optional results freeze by **2027-02-15**. If the complete chosen study cannot fit, defer it or explicitly revise the protocol before testing rather than silently dropping declared comparisons, access disclosures, or the channel-encoder study's Stage 2 `0`.

---

## 20. Reproducibility Requirements

Each experiment report must retain immutable data and analysis manifests; raw-file checksums and reopen/backup records; coordinate-frame and sector definitions; array/source/receiver calibration and uncertainty records; acquisition-group membership; split and sealed-access ledgers; simulation configuration and version; preprocessing and normalization configuration; exact baseline/model settings; random seeds; ordered unit-level predictions; exclusions/failures; and generated tables/figures. If the E4 channel-encoder option is selected, its manifest additionally retains the frozen Stage 1 VAE/H/A/B/A+B and Stage 2 VAE/H/A/B/A+B/`0` slates; track S or R; released real group/corpus identities and group-before-window/channel split where R is used; every permitted fit and normalizer/codebook/probe provenance; VAE likelihood/latent-usage and H descriptor/codebook/mask freezes; JEPA target, direct-reference eligibility, common-phase augmentation, and temporal-support records; diagnostic target definitions/results; checkpoint/selection rules; and per-variant resources and failures.

The core model manifest also records the hybrid stem and Re/Im packing interface, the selected [E-S/E-M/E-L preset](architecture.md#913-engineering-size-presets-and-single-size-selection) and its selection evidence, block count, FFN width, temporal and frequency-block configuration, final feature axes/dtypes, positional encoding, normalization axes/state, subsampling, and separate Fusion/head choices. These presets use `C=2*C_s` without an extra stem-to-Conformer width projection. Distinguish STFT analysis window/hop, model observation duration/crop hop, and attention policy/neighbourhood. Record the initial full within-window policy or an explicitly approved pre-freeze local-attention change, its evidence and implementation; overlapping observation crops remain nested in their original scientific units.

For Fusion, retain the `[N,M,C,F_e,T_e]` to per-TF sensor-attention mapping; surveyed-coordinate reference `r_0`; fixed length/frequency scales `L_0,f_0`; coordinate and frequency MLP configurations; physical-frequency alignment; block/head/FFN widths; feature-only LayerNorm; sensor and TF masks; sensor-then-TF pooling; all-masked/no-valid-output handling; and the zero-coordinate ablation input. Report complete model resources, not only the encoder's temporal attention cost.

For the one-azimuth head, retain `C -> C -> 2` width and activation, raw-vector target `(cos(theta),sin(theta))` with radian/frame convention, batch-mean reduction over the sum of component squares, `atan2(b,a)` decoding, frozen shared numerical threshold `tau`, and degenerate/non-finite failure counts. The raw vector norm is not a calibrated uncertainty estimate. Keep the training loss separate from the circular evaluation metric and the 180-degree failed-prediction score.

If the E4 representation option is selected instead, retain its actual contrast and reference training regime, parent-observation pairing, physical-band/duration equivalence, tensor axes/dtypes, complete transform/normalizer provenance and raw-sample support, input-block/interface differences, tuning/selection record, measured resources, and §17.5 diagnostics/results. Catalogue entries that were not run are reported as such, not as missing rows of an implicitly approved matrix.

For simulated results, pin the solver source repository and exact revision/build or executable checksum, interface version, compiler/build options, numerical precision, and input-file hashes. Retain the convergence, delay/phase-preservation and reference-comparison configurations and outputs, with the tolerances used and any failures. Record the physical assumptions separately: reproducible execution and agreement between ports do not establish that the model describes the measured ice environment.

Retain an append-only final-data access ledger: timestamp, purpose, protocol/code/model versions, frozen configuration and data-manifest hashes, output artifacts, and any decision triggered by the access. Freeze the complete method/seed/preprocessing/analysis set before inspecting any final result; a result-driven change cannot be presented as part of that same confirmatory evaluation. Rehearse scoring, failure handling and report generation on development data before opening the final set.

Report measured resource use alongside accuracy: parameter count, peak memory, preprocessing/inference time, observation duration, batch/concurrency settings and hardware. For the E4 channel-encoder option, report each Stage 1 variant/track's pretraining examples, R mixture and real hours/examples where applicable, reference information, codebook/probe costs, optimization steps, measured compute/memory/time, and the shared Stage 2 downstream and inference resources. For the representation option, report conversion and input-block costs as well as the chosen regime's training/inference costs; do not compare only precomputed-input model throughput. Report simulation generation time/I/O separately from estimator inference; a throughput measurement alone is not evidence of a real-time deployed system.

For the hybrid encoder, include actual `N_ch`, `F_e`, `T_e`, feature widths, attention-head count, precision, and backend/version in resource reports. Measure the complete forward/backward path for fitting and the actual inference path, not only the complex stem or a cached feature readout. Full per-frequency temporal attention has a quadratic temporal pair count, but actual memory depends on the backend; neither a dense local mask nor a theoretical pair count substitutes for measured cost. A bidirectional bounded-window estimator is not evidence of causal/streaming operation.

E-M is the first pilot candidate, not a claim of optimal size or demonstrated fit. If resource measurements include another preset, use the same physical window, representation and attention policy, and disclose non-size processing differences. Report the actually measured configurations; unrun reserve presets are not missing experimental arms. Freeze one size across the matched core pair and the optional encoder-pretraining comparison. The `N_ch*F_e*B_enc*T_e^2*C` attention arithmetic term is not a full-network FLOP or memory estimate, and shared weights mean the encoder parameter count is not multiplied by sensor count.

Reports must identify every unresolved parameter rather than inventing it. They must distinguish simulation, S zero-shot field, optional E1 adapted field, optional E4 R-assisted pretraining, and sealed real-test results; preserve the original data ownership and access boundaries; and record whether any method uses privileged physical or environmental information.

---

## 21. Experiment-Level Protocol Skeleton

### 21.1 Required Frozen Blocks

Before sealed evaluation, the protocol must specify:

- the 1D azimuth target, coordinate convention, surveyed identifiable sector, and treatment of out-of-sector and ambiguous predictions;
- whether far-field steering is justified by source/array geometry or a range-aware/restricted alternative is used;
- actual linear-array coordinates, sensor ordering, aperture/spacing as measured, synchronization, gain/phase calibration, and permissible uncertainty;
- source, receiver, and clock-truth method, including hanging-cable motion, depths, and timing uncertainty;
- the primary Re/Im STFT contract and bench-frozen sampling/resampling, operating band, windowing, normalization, frame/padding convention, raw-sample support, and feasibility evidence;
- simulation boundary, environment and per-sensor propagation; geometry holdouts only if an optional geometry-transfer study is selected;
- field acquisition-group definition, development/final seal, quality criteria, and S zero-shot/E1 adaptation/E4 R-pretraining access ledgers;
- MVDR/Capon, MUSIC, Bartlett, and matched neural-pair configurations and equal-information rules;
- if the E4 channel-encoder option is selected, the complete Stage 1 VAE/H/A/B/A+B slate and Stage 2 VAE/H/A/B/A+B/`0` slate; canonical observed/direct target definitions; direct-reference eligibility; H codebook/probe and track provenance; common-phase and non-overlapping temporal-support checks; VAE latent-usage and JEPA anti-collapse diagnostics; matched downstream controls/resources; and the decision to defer or revise rather than silently narrow it;
- if the E4 representation option is selected, its one alternative, fixed reference training regime, physical observation/band matching, input-block differences, development-only selection, resource gate and §17.5 reporting contract;
- independent-unit metric summaries, practical threshold (if justified), uncertainty method, and failure/coverage reporting; and
- artifact, provenance, deadline, and supervisor decision records.

Unknown numerical settings belong in the decision register with responsible role, evidence needed, due date, and failure action.

### 21.2 Protocol Validity Rules

No result becomes final-test evidence before the required blocks are frozen. Post-hoc replacement of failed field units, sector redefinition, baseline tuning, or access changes invalidates a confirmatory interpretation and must be disclosed. A simulation-only result cannot be relabelled as field validation. If the winter minimum cannot be completed, the study requires an explicit supervisor-approved revision of the scientific minimum and an honest scope statement; simulation is not an automatic replacement.

---

## 22. Phase-Preservation and Interpretability Checks

The phase-sensitive pipeline must be checked before interpreting a neural DOA result. These are planned diagnostic safeguards, not statements that any check has passed. The protocol should assess: (1) recovery of inter-channel phase/delay cues appropriate to the measured baselines; (2) temporal/frequency phase consistency; (3) pairwise coherence preservation; (4) response to documented gain, phase, timing, and coordinate perturbations; and (5) channel-order permutation behavior when coordinates and signal channels are jointly permuted.

Independent random phase jitter, independent time shifts, magnitude-only primary input, and per-channel transformations that erase informative inter-channel relationships are not acceptable as unexplained preprocessing or augmentation. Numerical tolerances must be chosen from the measured array, operating band, sector resolution, and calibration capability before the sealed test.

Check the selected hybrid at the preprocessed input and at the final channel-encoder output, then through Fusion. Any fitted diagnostic readout must have declared capacity, fitting access, and target semantics; the optional five-encoder comparison uses §17.4's matched probes. Neither the complex stem nor lossless Re/Im packing certifies the full real Conformer path. Record the effects of normalization, positional encoding, temporal attention, frequency mixing, and subsampling without interpreting arbitrary real feature coordinates as physical phase.

For the selected Fusion, verify joint-permutation invariance through the final readout, the absence of masked-sensor/padding contributions, and safe all-masked handling under the existing prediction-failure rules. Check that coordinate association is retained and no coordinate-derived input reaches the twin. Coordinate/frequency addition, LayerNorm, channel attention and pooling remain part of the phase/delay diagnostic path; their mathematical permutation structure is not evidence of phase preservation or unseen-geometry accuracy.

A failed check limits the claim to the evidence that remains valid and triggers root-cause review of calibration, preprocessing, representation, or geometry handling. It does not justify silently changing the held-out evaluation, adding a larger model, or claiming that an unrun diagnostic passed.

For the E4 channel-encoder option, before Stage 2 DOA evaluation, use the Stage 1 frozen-encoder diagnostic contract to verify recoverable pairwise phase/delay cues and record VAE latent-usage or JEPA anti-collapse diagnostics as applicable. Record target source (observed mixture or direct reference), phase/delay target eligibility, context/target acquisition times, hop, window, STFT, and filter support; confirm that the initial B observed-future pair has no shared raw samples. Passing controlled diagnostics is not a guarantee of denoising, broadband-delay retention, or DOA performance in other conditions; failure blocks the corresponding E4 interpretation and is reported without changing the core evaluation cohort.

For H, verify mask support before the stem and all contextual mixing, including normalization and subsampling; an attention-only mask must not leave an unmasked feature bypass. For B, verify separately encoded current/future windows with no shared signal cache, cross-window normalization, or full-record encoding followed by cropping. Full bidirectional attention inside each permitted window is compatible with that separation; successful loss minimization is not evidence that the access boundary was respected.
