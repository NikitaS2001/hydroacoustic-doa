# Risks And Validity Threats

> This register covers the scoped Candidate of Sciences dissertation study. It records planned mitigations and decision points, not completed mitigations or passed empirical gates. The authoritative calendar is in the [roadmap](roadmap.md); operational controls are in the [winter field protocol](../../experiments/winter_field_protocol.md).

## 23. Risks and Validity Threats

### Active Scope and Decision Rule

The minimum is a winter 2026–2027 under-ice recording campaign using **only a measured linear array**, a quality-controlled labelled dataset, controlled simulation, MVDR/Capon and MUSIC comparisons, Bartlett diagnostics, and one compact geometry-conditioned/no-coordinate neural pair. Exact bay, safe-ice access, array and source configuration, calibration capability, and band are unconfirmed. The full-text planning deadline is 2027-03-31; it is not a guarantee of defense, degree award, publication acceptance, or field access.

A risk action may limit a claim, stop an extension, or trigger an explicit supervisor decision. It must not silently change the independent unit, sector, information available to a method, or minimum scientific scope.

### Risk 1: Missed or Unsafe Ice Window

**Threat.** Safe, authorized under-ice access or usable labelled recordings may not be available during the winter window.

**Actions and deadlines.** Complete equipment/source/field-access feasibility by 2026-10-15 and the bench-supported measurement/QA/analysis freeze by 2026-11-15; complete the full end-to-end lab rehearsal, raw-file reopen and backup readiness review by 2026-11-30. Use the earliest professionally authorized safe opportunity in December–January; escalate to supervisor and field lead on 2027-01-15 if usable labelled data or safe access is absent; reserve 2027-02-01..15 for targeted reacquisition only when safe and necessary. No calendar target overrides qualified local field leadership, approvals or safety procedures.

**Limit.** Do not automatically replace failed field work with simulation, promise a new campaign, or claim that the real-data minimum was met. If winter evidence is missing by the 2027-02-28 core-freeze target, obtain an explicit supervisor-approved revision of the minimum claim and disclose the incomplete field evidence.

### Risk 2: Unknown Array, Source, and Field Parameters

**Threat.** Hydrophone positions, cable motion, spacing/aperture, source spectrum/directivity, receiver/source depths, timing, synchronization, access, and local conditions may invalidate an intended steering or simulation setup.

**Actions and deadlines.** Survey and record the actual array coordinate frame rather than assuming uniform spacing or a ULA; bench-test source/receiver/synchronization/positioning in October; freeze the hardware/source/field decision by 2026-10-15 and the representation, band, sector, calibration, QA, and analysis contract by 2026-11-15. Keep unresolved numerical values in the decision register with owner, evidence, due date, and failure action.

**Limit.** Bay identity, source performance, uniform spacing, far-field validity and usable band require evidence. If geometry does not justify far-field steering, restrict conditions or use a valid range-aware formulation and limit the claim accordingly.

### Risk 3: Linear-Array Mirror Ambiguity

**Threat.** A linear array has structural front/back ambiguity; coordinates and machine learning cannot recover full-circle azimuth not identified by the measurements.

**Actions.** Survey a known-source half-plane or other identifiable sector before final evaluation; give the same sector prior to every method; record array axis, azimuth convention, source placement, and sector violations. Use circular angular distance only within the frozen sector and report predictions outside it under the predeclared rule.

**Limit.** Never silently clip, reflect, or relabel predictions. If no defensible sector is available, report ambiguous direction/direction cosine and obtain supervisor agreement to amend the claim before freeze. Do not claim 360-degree unambiguous azimuth.

### Risk 4: Ice Boundary and Sim-to-Real Mismatch

**Threat.** A pressure-release free surface is not an ice boundary. BELLHOP, if used, may omit or misrepresent ice interaction, multipath, structure-borne/acoustic noise, sensor coupling, or uncertain local environment.

**Actions.** Treat BELLHOP as a candidate controlled simulator; document its boundary assumptions, per-sensor phase/delay checks, convergence/physical checks and parameter uncertainty. Hold out genuinely independent simulated environments for the measured linear configuration. New-layout/spacing holdouts belong to optional E2/E4 geometry studies, not the minimum. Record measured field conditions needed to interpret domain shift.

**Limit.** Without validated ice physics, make only generic simulation/domain-shift statements. Real-noise overlays on simulated sources are not real-data validation. Neither simulation nor a single measured linear geometry supports arbitrary-topology physical-transfer claims.

### Risk 5: Source Truth, Calibration, and Coverage Error

**Threat.** Hole positions or intended bearings alone are not underwater source truth. Cable motion, depth uncertainty, clock drift, gain/phase response, unknown range, and intermittent source behavior can bias both classical and neural estimates.

**Actions.** Capture source and sensor geometry in one defined coordinate frame; record calibration method/version and gain, phase, timing, depth, and position uncertainty; preserve raw files and immutable manifests. Use source/receiver geometry to justify the steering model and report per-unit truth uncertainty, valid-prediction coverage, and failure reasons.

**Limit.** A result with inadequate truth or calibration is a limited measurement/QA finding, not DOA-accuracy evidence. Do not exclude difficult rows after sealed evaluation without preserving the exclusion and its effect on coverage.

### Risk 6: Leakage and Window Pseudoreplication

**Threat.** Overlapping windows, repeated transmissions, shared field backgrounds, calibration recordings, simulator seeds, or real noise may leak between development and final testing; treating them as independent samples overstates evidence.

**Actions.** Define simulated environments as simulation inference units and deployment/session/day blocks as field acquisition groups. Keep windows, clips, transmissions, overlays, crops, and model seeds nested within their parent unit. Seal real final groups, including unlabelled audio/backgrounds, from training, normalization fitting, SSL, simulator tuning, and model selection. Retain an access/split/provenance ledger and audit it before final reporting.

Sliding observation crops do not imply local attention or independent replicates. For the selected Conformer-like encoder, full temporal attention is bounded by the current input window. H masks must precede the stem and all context mixing; B context and future-target windows are encoded independently, with disjoint raw support and no cache or data-dependent normalization that mixes the two windows. Bidirectionality inside a permitted window does not authorize full-record encoding followed by feature cropping.

**Limit.** Window bootstraps do not establish across-session field uncertainty. One field session cannot demonstrate across-session transfer. Reusing a sealed group for tuning invalidates confirmatory interpretation rather than creating a new test set.

### Risk 7: Few Independent Groups and Unjustified Precision

**Threat.** Weather, safety, and logistics may yield few independently acquired field groups, making conventional confidence intervals or power claims unstable.

**Actions.** Plan for multiple independently acquired groups, preferably three or more redeployed sessions/days when safe and practical, while recognizing this is an acquisition target—not proof of power. Report the actual group count, unit construction, median/p95 error, coverage, failure rate, truth uncertainty, and paired differences at the independent-unit level. Freeze a practical threshold or power target only if pilot/application evidence justifies it before final test.

**Limit.** With few groups, conclusions remain descriptive and conditional; do not manufacture certainty by treating windows, model seeds or repeated transmissions as new units.

### Risk 8: Narrow Comparator Slate and Overclaiming

**Threat.** MVDR/Capon, MUSIC, Bartlett, and one compact neural pair are a scientifically focused but limited slate. A favorable result may be overread as broad neural or SOTA superiority.

**Actions.** Tune required methods fairly under matched sector, coordinates, calibration, input duration, splits, and permitted information. Freeze covariance and steering choices for the classical methods. Treat Bartlett as a diagnostic. Report all wins, losses, numerical failures, and sensitivity to calibration and sector.

**Limit.** The slate supports only condition-bounded comparisons. It cannot establish SOTA-wide superiority, universal superiority over classical DOA, or performance on untested topologies. Extra architecture search is not a remedy for a null core contrast.

The no-coordinate twin may also have an information-induced ambiguity floor, especially on symmetric linear layouts with unordered channels. Diagnose this on development data before interpreting the contrast. A gain over that ablation alone cannot establish architectural novelty or an advantage over a strong fixed-layout neural estimator; contribution adequacy must be reviewed against that limitation.

### Risk 9: Phase/Timing, Front-End Confounding, and Model Complexity

**Threat.** Preprocessing, normalization, channel indexing, an over-complex neural model, or a changed front-end adapter may discard phase/delay/coherence information, exploit nonphysical shortcuts, or confound a selected representation contrast with architectural differences.

**Actions.** Use the primary **Re/Im STFT** path if the bench feasibility decision supports it; document all transformations; check inter-channel phase/delay and coherence recovery, calibration sensitivity, and joint signal-coordinate permutation behavior before interpreting neural results. Keep the compact paired models matched and within local compute resources. The broad representation catalogue remains distinct from selected experiments: its principal candidates are primary Re/Im STFT, first-alternative time-domain baseband IQ, and next-control real-valued waveform; complex CWT, magnitude plus sine/cosine phase STFT, and magnitude-only STFT/mel are catalogue entries, not mandatory runs.

**Selected encoder safeguard.** The [hybrid Conformer-like channel encoder](architecture.md#91-shared-model-contract) is the chosen core basis, not a deferred E4 architecture. Its complex Conv2D stem feeds real Conformer blocks and local frequency mixing; the final feature coordinates are not physical Re/Im pairs. Check recoverable phase/delay information after the entire encoder and Fusion, including normalization, positional encoding and subsampling. Native complex operators and lossless packing do not guarantee full-network phase equivariance or useful DOA features.

**Attention resource gate.** Before the 2026-11-15 freeze, measure the complete forward/backward and inference paths at the actual window, frequency count, batch, widths, heads, and backend. Initial attention is full in time within each bounded window, separately per frequency; its temporal pair count is quadratic in encoded window length. Local/sliding-window attention requires an explicit development decision before comparative pretraining and final freeze, common to all compared encoders, with measured cost and phase diagnostics. Neither a dense local mask nor a speech-model precedent proves feasibility. No silent backbone swap, architecture sweep, or causal/streaming claim follows from a resource failure.

**Preset-selection boundary.** The [E-S/E-M/E-L presets](architecture.md#913-engineering-size-presets-and-single-size-selection) specify engineering candidates, not validated resource or accuracy tiers. E-M starts the pilot; E-S is the resource fallback; E-L is a development reserve, not an automatic response to a failed phase check or unfavourable result. Choose one size before the configuration freeze and comparative pretraining, common to the core pair, VAE/H/A/B/A+B and downstream `0`. Measure the complete paths including applicable teacher/decoder/predictor overhead; parameter sharing across hydrophones does not eliminate activation or attention cost. No mandatory three-size benchmark, per-objective size change, or size-by-pretraining matrix is approved.

**Selected front-end comparison rule.** If E4 selects a front-end comparison, compare primary Re/Im STFT with exactly one resource-approved alternative, prioritizing IQ and then the real-waveform control. Adding both alternatives needs an explicit scope/resource revision; a second E4 branch or representation × pretraining × architecture factorial is not approved. Preserve the same permitted records/scenes/groups, calibration, access, sector, splits, targets, retained physical band, and physical duration. Record input-adapter capacity, receptive-field duration, interface, and time/memory.

**Limit.** These are planned checks, not evidence already obtained. A failed check limits the neural claim and requires root-cause review; it does not authorize changing sealed data, increasing model scale, or asserting that the model learned geometry. If front-end architectures differ, the comparison does not establish a pure representation effect.

### Risk 10: Zero-Shot and Adaptation Confusion

**Threat.** Field development data can leak into a purported sim-to-real test, and successful adaptation can be misreported as zero-shot transfer.

**Actions.** Maintain a field-data access ledger. The zero-shot track permits no target-scene recording use in fitting or selection; preregistered measured geometry/sector and separate instrument calibration remain allowed physical inputs under equal access. Optional adaptation may use only designated development field data, with label budget, normalization, simulator changes, representation learning and selection recorded; final evaluation remains on untouched groups.

**Limit.** Adapted and zero-shot results are separate claims. If access separation cannot be guaranteed, omit the transfer claim rather than relabelling it.

### Risk 11: Contribution, Publication, and Review Uncertainty

**Threat.** Required published-article count, accepted venues, acceptable publication stage, specialty expectations, novelty sufficiency, and review lead times are unknown. Negative results may be scientifically informative but may not meet formal dissertation requirements alone.

**Actions and deadlines.** Candidate and supervisor must clarify institutional/dissertation-council publication and specialty requirements by 2026-09-30. Build one coherent manuscript workload; create additional manuscripts only for independent substantive results, never artificial slicing. Seek supervisor review of contribution adequacy as the evidence matrix matures. Assemble a complete dissertation manuscript by 2027-03-10, reserve 2027-03-11..21 for review/corrections, and 2027-03-22..31 for final text and submission-ready package.

**Limit.** Do not invent an article count, venue, publication stage, review duration, acceptance, defense, degree, or formal novelty outcome. Full-text work proceeds in parallel with research; unknown review lead times cannot be assumed to resolve before the deadline.

### Risk 12: Scope Creep Against the Writing Deadline

**Threat.** Optional E4 two-stage channel-encoder work, a selected primary-Re/Im-STFT-versus-one-resource-approved-alternative comparison, or arbitrary-topology simulation work—along with multi-source/3D work, model scaling, or deployment studies—can consume the period needed for the winter minimum, analysis, and full text.

**Actions.** Maintain the single-source measured-linear core and write methods/results continuously. At most one extension may proceed only after the minimum pipeline and labelled-data quality work are secure; no extension starts after 2027-02-01, and all extension results freeze by 2027-02-15.

**May be cut.** E1 small labelled real-development adaptation; E2 within-linear sensor-subset/spacing sensitivity; E3 modest ice-boundary or calibration sensitivity; or E4 exactly one bounded study: the two-stage channel-encoder comparison, primary Re/Im STFT versus one resource-approved alternative (baseband IQ first; real waveform as the next control candidate), or arbitrary-topology **simulation-only** transfer. Any or all extensions may be cut without changing the minimum.

**E4 scope and resource risks.** In the channel-encoder option, Stage 1 compares VAE, HuBERT-style H, and JEPA A, B and A+B on one encoder; JEPA is one family with task ablations. Its frozen-encoder probes are diagnostics, not final DOA evidence. Stage 2 compares those five encoders with the matched full-model supervised-from-scratch 0, while the core no-coordinate twin stays outside the matrix. Three paired seeds are evidence-gated: 18 is the total number of downstream fits for six regimes, not automatically 18 additional fits after the core. Before launch, remeasure all pretraining, temporary-branch, codebook/probe and downstream resources. If the complete selected protocol cannot fit its total five-focused-working-day **scheduling stop cap**, defer it or explicitly revise it before testing; never silently prune methods or add an unapproved second E4 branch.

**Data, phase, and privileged-target limits.** Follow [training §13.5](training_strategy.md#135-two-stage-channel-encoder-pretraining-study): preserve coherent timing/emission phase, record signal support and phase/collapse diagnostics, and do not assume that any objective denoises or preserves phase. A/A+B's simulator-derived direct references are privileged and must be recorded; B has only an observed future target. S remains strict sim-only. Optional R is separately approved, provenance- and group-split-controlled unlabelled real-assisted pretraining within the same E4 budget—not labelled E1, not real angular-label fine-tuning, and not authority to fabricate A/A+B targets. Report the selected R contrast separately and all data access, reference eligibility, steps and measured resources.

**Requires supervisor-approved minimum revision.** Omission of the winter measured-linear campaign, quality-controlled labelled under-ice dataset, required MVDR/Capon and MUSIC comparisons, compact matched neural pair, or honest measured-array/domain-shift evaluation changes the minimum scientific scope. Such a change must be explicit; it is never an automatic simulation substitution. Multi-source tracking, 3D localization, latent world-model claims, broad SSL benchmarks beyond E4, large-model scaling, and deployment/edge claims remain deferred beyond the 2027-03-31 full-text deadline.

---

## 24. External Architecture References and Dependency Policy

External audio, array-processing, SSL, and world-model literature may inform questions about representations, compression, or objectives. It is research inspiration, not evidence that an imported model works for hydroacoustic DOA and not a commitment to an additional model family. Methodological E4 precedents include [VAE](https://arxiv.org/abs/1312.6114), [HuBERT](https://arxiv.org/abs/2106.07447), [GigaAM](https://arxiv.org/html/2607.10371v1) and [I-JEPA](https://arxiv.org/html/2301.08243v3), alongside KVAE/KVAE-Audio; EnCodec, DAC, SNAC, WavTokenizer, Mimi/Moshi, DualCodec, SAC, SUNAC, and XY-Tokenizer; data2vec and BEATs; and V-JEPA 2, MAGVIT-v2, OmniTokenizer, and Cosmos Tokenizer. GigaAM is speech recognition; none provides phase-aware hydrophone or under-ice DOA validation.

The primary [IQ-JEPA paper](https://arxiv.org/html/2607.22351v1) concerns masked **multichannel medical ultrasound** and simulated-only validation. It provides methodological inspiration, not evidence of novelty, single-channel hydrophone DOA performance, automatic phase preservation, or direct hydroacoustic transfer.

### 24.1 Applicability Safeguard

No external weights, architecture, or paper result may be presented as hydroacoustic, under-ice, phase-preserving, or geometry-transfer evidence without a task-appropriate controlled evaluation. External methods must not displace the compact matched pair or delay the minimum study. If an optional external architecture is selected, its information access, input representation, parameter/resource cost, licence, and phase/geometry implications must be documented.

### 24.2 Import and Vendoring Rules

1. Do not vendor external source repositories, weights, or training scripts into this documentation repository.
2. Any future executable import belongs only in the implementation location designated during planning, after licence verification, dependency audit, pinned commit/release review and domain-fit review; no separate repository is presumed already selected.
3. Record the pinned source, licence summary, dependency manifest, and evidence/approval path for each approved import.
4. A review of external code does not validate it scientifically or relax the field-data, calibration, sector, or leakage requirements in this framework.

Literature and external-code decisions must cite traceable public sources and retain the distinction between research inspiration and an approved dependency. Hidden local planning archives are not a required artifact or an authority for the current study.
