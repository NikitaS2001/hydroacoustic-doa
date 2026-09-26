# Winter Under-Ice Linear-Array Field Protocol

## Status and purpose

This is the active preparation, acquisition, and real-data evaluation protocol for the winter 2026–2027 campaign. It is a planning document: every gate and result below is **not yet evaluated**. The campaign is a time-critical, obligatory part of the minimum dissertation study; its full-text writing/research deadline is **2027-03-31**. That deadline does not override qualified safety authority and is not a promise of defense, degree award, or publication.

The owner reports an **initial test configuration** of eight hydrophones in a nominal ULA at approximately 27 mm spacing, with 96 ksample/s and a stated «32 bit» recording mode. Actual underwater spacing/linearity, common clock, file format/effective ADC precision, sensor/transmitter response, the exact bay, access permissions, safe-ice opportunity, source level, operating band, acquisition chain and positioning resources remain unconfirmed. Novik Bay/Russky Island is only a prior motivating candidate. No physical deployment other than one **linear** array is in scope; call the physical field array a ULA only after surveying its submerged coordinates. A [proposed LFM and STFT pilot](../../outputs/signal_waveform_frontend_review.md) is not a frozen field setting.

This protocol implements the field portions of the [Roadmap And Success Criteria](../research/framework/roadmap.md) and is read with [Data, Simulation, And Hydroacoustic Validation](../research/framework/data_and_simulation.md).

## 1. Field claim boundary

The core field task is a controlled, single-source azimuth experiment using one calibrated physical linear array, a surveyed source in one preregistered identifiable half-plane/sector, and phase-preserving synchronous multichannel recordings. The deliverable is a quality-controlled labelled under-ice dataset with calibration, acquisition-group provenance, raw archives, backgrounds, and stated measurement uncertainty.

A linear array has structural front/back mirror ambiguity. The array can support an azimuth claim only within the surveyed, identifiable source sector shared as the same prior by all methods. It cannot support a 360-degree unambiguous azimuth claim. If the sector cannot be established, outputs and reports must retain the ambiguous direction/direction-cosine interpretation and the supervisor must approve an amended claim before analysis is frozen. Coordinates or learning methods do not resolve the unobserved mirror ambiguity.

The source and receiver geometry must either justify the selected far-field steering approximation for the measured aperture, band, ranges, and uncertainty, or use a range-aware steering/interpretation limited to the measured conditions. A nominal hole layout, intended bearing, or surface bearing alone is not ground truth.

A linear array primarily constrains the direction projection along its axis. Interpreting that projection as **azimuth** additionally requires a fixed/known source elevation or a measured source/receiver depth-and-range bound showing that elevation effects are negligible at the declared uncertainty. Freeze and check that condition per block; a known half-plane alone is insufficient when elevation is unconstrained. Otherwise amend the target to the observable direction quantity instead of claiming azimuth or adding an unplanned 3-D localization study.

## 2. Decision register and evidence gates

All entries are unresolved until their named evidence is recorded in the campaign register. A role may delegate work but remains accountable for the gate decision.

| Gate | Owner | Due planning date | Required evidence | Failure action |
|---|---|---:|---|---|
| G1 — institutional and scientific scope | Candidate and supervisor | 2026-09-30 | specialty/dissertation-council guidance on novelty and publication requirements; approved minimal field claim | revise the contribution plan; do not invent an article count or publication outcome |
| G2 — site, access, and safety authority | Qualified local field lead | 2026-10-15 | candidate site/access authorization, institutional approvals, local ice and acoustic-emission procedures, named abort authority | choose an authorized alternative only if it preserves the linear-array claim, or trigger the missing-field-evidence contingency |
| G3 — hardware and controlled source feasibility | Acquisition lead and transmitter owner | 2026-10-15 | inventory; hydrophone/interface compatibility; multichannel shared-clock proof; source/transmitter permission, source characterization, deployment/recovery method, and laboratory receive test | repair/replace/borrow only after a repeatable bench proof; otherwise declare field minimum at risk to supervisor |
| G4 — geometry and truth metrology | Metrology lead | 2026-10-15 | demonstrated survey/uncertainty method and preliminary linear layout; coordinate-frame plan; bench/rehearsal geometry evidence; planned range/far-field assessment | restrict sector/range, use justified range-aware analysis, or amend the claim before recording |
| G5 — phase-preserving acquisition | Acquisition lead | 2026-11-15 | synchronized recording rehearsal; channel order/polarity ledger; calibration measurements; clock drift and gain/phase characterization; raw-file reopen check | correct configuration and repeat rehearsal; no labelled campaign recording until passed |
| G6 — analysis and data-access freeze | Analysis lead and supervisor | 2026-11-15 | frozen sector, band/sample-rate/representation feasibility decision, compact model budget, calibration and QA criteria, split/access ledger, baseline configuration | freeze a reduced justified plan; leave unsupported settings unresolved |
| G7 — field readiness review | Field lead, acquisition lead, and supervisor | 2026-11-30 | completed rehearsal records, backup plan, archive media and checksum procedure, named operational/safety roles | defer campaign activity until all critical deficiencies have an authorized resolution |
| G8 — usable-labelled-data checkpoint | Field lead and supervisor | 2027-01-15 | reviewed manifests, QA disposition, ground-truth completeness, and access separation for acquired groups | immediately agree and record a claims-limited contingency; do not wait until March |
| G9 — core-data and analysis freeze | Candidate and supervisor | 2027-02-28 | immutable core manifests, calibration freeze, access ledger, and completed scope review | disclose missing field evidence and agree revised scientific scope; simulation is not a silent replacement |

Unknown apparatus or numerical settings are evidence-gated decisions, not defaults: operating frequency/bandwidth, sample rate, source level and waveform, array sensor count/spacing/aperture, acquisition duration, source ranges/bearings/depths, and minimum session/block counts. Evidence must include the relevant source/hydrophone response, sampling and aliasing constraint, surveyed geometry, transmit authorization, available compute/storage, and bench result.

The October/November gates freeze the demonstrated measurement procedure, intended hardware/geometry and acceptance criteria, not fictitious winter observations. Actual submerged coordinates, source truth, environment and calibration state are recorded and checked for each later deployment under that procedure. A material departure requires a documented amendment before final evaluation; it cannot be hidden as the originally frozen condition. Readiness checkpoints R1–R6 in the roadmap are distinct from field gates G1–G9 here.

## 3. Preparation and rehearsal

### 3.1 Hardware and transmitter feasibility

Before winter recording, inventory every item with serial/firmware status and accountable custodian: hydrophones, cables, deployment hardware, multichannel interface/recorder, clock distribution, power, storage, calibration source, controlled underwater transmitter/source, positioning/metrology equipment, and recovery equipment. The transmitter must be confirmed as a labelled controlled source; its availability is a prerequisite, not a confirmed fact. Its emission permission, operating limits, signal reproducibility, timing cue, and useful received band must be evidenced before selection.

The laboratory rehearsal must transmit and acquire a representative controlled source through the intended chain, demonstrate all intended channels, record the actual channel order and polarity, and prove that file metadata and media capacity match the planned acquisition. The selected primary representation is complex STFT only if its phase preservation and local-resource feasibility pass G6; otherwise the amended primary representation and limitations must be frozen before field data are used.

### 3.2 Synchronous, calibrated acquisition

All hydrophone channels must share one acquisition clock or an equivalently demonstrated synchronous timing architecture. Independent unsynchronized recorders, automatic gain control, noise suppression, echo cancellation, and uncontrolled per-channel DSP are prohibited for labelled analysis. Record the clock source, sample rate, bit depth/format, input ranges, preamp settings, channel map, start/stop mechanism, and any resampling history in each manifest.

Before and after each deployment or whenever the chain changes, acquire a calibration record sufficient to assess channel gain, phase/polarity, frequency response, and timing/clock drift in the selected band. Retain calibration raw files separately from analysis data and freeze their availability identically for MVDR/Capon, MUSIC, Bartlett diagnostic, and both supervised models. A calibration may correct documented response only under the frozen analysis plan; it must never leak test labels or give a method privileged information.

### 3.3 Underwater truth and uncertainty

Define an array-centred right-handed coordinate frame and record its orientation. For every acquisition block, preserve the measurement method, timestamp, operator, coordinate values, uncertainty model, and evidence for:

- each hydrophone's underwater three-dimensional position and depth, including actual linearity/non-uniform spacing and aperture;
- source underwater position/depth, source orientation where relevant, and source timing state;
- array orientation, source range, bearing and the selected identifiable half-plane/sector;
- hanging-cable geometry, motion, tension/deployment state, and observations or bounds relevant to position uncertainty; and
- clocks, calibration state, environmental observations, and any condition that could affect timing or phase.

A ground-truth record is accepted only when it describes underwater source and receiver geometry in this frame and carries uncertainty; planned hole coordinates alone are insufficient. Geometry changes require a new deployment/session identity and assessment against the frozen far-field/range-aware rule.

## 4. Recording design

### 4.1 Acquisition groups and reserved splits

The real inference unit is an independent field deployment/session/day block, not a waveform window, burst, repeated bearing, overlapping clip, transmission, model seed, or noise overlay. Plan multiple independently acquired groups, preferably at least three redeployed sessions/days when safe and logistically possible; this is an acquisition target, not proof of statistical power. The first usable recording may be development/QA data. Reserve independent final groups before model selection and record the reservation in the access ledger.

A sealed real group, including its source-on, source-off, background, unlabelled signals, calibration-derived products, and metadata, must not enter training, normalization fitting, simulator tuning, self-supervised learning, adaptation, hyperparameter selection, or model selection. Calibration is frozen separately and made equally available to all methods. If only one independent session survives QA, report descriptive, bounded within-session findings only; do not claim across-session transfer or manufacture independence through windows or resampling.

Physical array/sector survey metadata and separately acquired instrument-calibration records may be used as preregistered inference inputs or fixed calibration corrections. Their acquisition and permitted use must be declared before final testing, identical across methods apart from the coordinate ablation, and must not fit the model or simulator to final source-scene recordings/labels. Zero-shot refers to the absence of target-scene fitting, not the absence of instrument calibration. Raw-file/QA inspection of sealed groups follows fixed acceptance criteria and cannot become feedback for method selection.

### 4.2 Controlled schedule per recorded condition

The frozen campaign sheet must enumerate conditions rather than inventing a universal numeric quota. For every accepted labelled source condition it must schedule, in the same manifest:

1. pre-source background with no controlled transmission;
2. source-on controlled transmissions with a recorded source identity, signal specification, timing cue, and truth record;
3. source-off/background after transmission; and
4. repeat/background observations when conditions or array state change.

Source-on/off labels must derive from an independent transmission log or timing reference, reconciled to the recording clock. Backgrounds must identify ambient, ice-related, structure-borne, handling, and equipment-noise observations when present; absence of a sound may not be inferred merely from a failed label. Preserve every interruption, aborted block, equipment state, and anomalous event in the manifest.

The minimal labelled dataset is accepted only when the evidence-gated campaign sheet's required controlled conditions have complete underwater truth/uncertainty, phase-preserving raw multichannel files, matching pre/post backgrounds, calibration disposition, provenance, and QA acceptance. It must include at least one development-eligible group and a separately reserved final group to support a real test claim. A deficit in independent groups narrows the claim as above; a deficit in truth, synchrony, or calibration makes the corresponding labelled block unusable for DOA evaluation rather than silently relabelled.

### 4.3 Far-field and sector interpretation

Before analysis, calculate and record whether the measured range, aperture, selected band, source extent and geometry uncertainty support the far-field approximation used by each method. If not, restrict analysis to justified conditions or preregister a range-aware nuisance search/interpretation. True source range from the label record must not silently become a privileged steering input: a known-range experimental condition must be declared and shared fairly; an oracle-range reference is labelled diagnostic. Do not use a far-field label to conceal near-field curvature.

All compared methods receive the same preregistered identifiable sector/half-plane prior. Report the mirror ambiguity, any excluded/unidentifiable directions, the coordinate convention, and the range interpretation in every real-data result. No prediction is silently clipped into the sector.

The [evaluation contract](../research/framework/evaluation.md) controls error aggregation: finite predictions are scored without clipping; missing/non-finite estimates receive the maximum circular-error penalty for the primary paired comparison, with valid-only errors, coverage, sector violations and failure reasons reported separately. The same fixed eligible examples are used for every method.

## 5. Archive, quality assurance, and access controls

### 5.1 Immutable raw archive

Immediately after each recording block, create a raw manifest with a stable acquisition-group identifier, file paths/names, byte sizes, cryptographic checksums, recorder/channel metadata, geometry/truth record references, calibration references, source-on/off schedule, and operator log. Keep raw files immutable; derived data must retain a parent raw-file checksum and transformation/version record.

At the earliest practical opportunity, reopen each copied raw file with the intended reader, verify channel count/order, duration, sample format/rate, readable samples, and checksum equality. Maintain at least two independently stored copies according to institutional policy, record their locations/custodians and verification dates, and never overwrite raw data in place. A failed checksum, unreadable file, channel mismatch, missing manifest, or unresolved copy discrepancy quarantines the block until resolved; it does not become training data.

Derived-input manifests follow [architecture §8](../research/framework/architecture.md#8-input-representation-strategy): retain the representation identifier, amplitude units, calibration version, parent channel order, crop timing, original/processed rates, retained physical band, tensor axes, shared-scale provenance, and complete filter/transform support including transients and padding. Primary Re/Im STFT records its window, hop, FFT, bins, scaling and frame convention. If an IQ alternative is explicitly selected, also retain analytic-conversion method, physical centre frequency, oscillator phase/time reference, anti-alias filter and decimation. Alternate views of the same recording inherit its access group and do not become independent observations; catalogue membership does not authorize new real-data fitting or a broader field programme.

### 5.2 QA disposition

The pre-frozen QA register records pass/fail/conditional disposition with evidence for synchronization/clock drift, clipped or missing channels, channel order/polarity, gain/phase stability, calibration validity, source timing/identity, geometry/truth completeness, position/depth uncertainty, environmental/operational anomalies, and far-field/range-aware validity. Spectral and time-domain inspection is diagnostic, not proof that labels are correct.

Use phase/delay consistency checks on controlled records to detect channel swaps, polarity inversions, lost synchronization, unexpected timing shifts, and gross geometry disagreement. Do not tune the final model or simulator using sealed-group data while carrying out this QA. Any value used to set a threshold, practical effect, sample-size target, or model choice must be frozen from pilot/application evidence before final testing.

### 5.3 Leakage prevention and real-data tracks

Maintain an immutable per-group ledger for calibration, development/QA, training, normalizer and simulator fit, unlabelled **R** JEPA pretraining, labelled E1 adaptation and sealed final scoring. Groups are split by deployment/session before windows/channels; overlapping clips and derivatives inherit status. R requires explicit lawful access to listed unlabelled development files and all teacher/fitting purposes; it never permits angular labels, simulator tuning or sealed groups. S is fit entirely on simulated development, not real recordings. A/S direct targets are simulator-saved receiver-specific components. Real A/R is permitted only after development-only probe/pilot validation of estimated direct component `D_hat`, including uncertainty, path identification, failure/coverage and approval; a known transmitted preamble only synchronizes/estimates a composite channel. If the gate is absent, no real A targets: conditional B/R may use observed future windows with disjoint support and authorization. E1 labels stay separate.

Real-noise overlays are robustness augmentation, not real validation. Report S zero-shot, approved R-assisted unlabelled pretraining and E1 labelled adaptation separately; none consumes sealed final material. B/S-versus-B/R is a predeclared data-source comparison only when R is released; it does not automatically create a full additional method matrix.

## 6. Ice, noise, and simulation limits

The field archive must preserve observations relevant to under-ice acoustics and operations, including ice-contact/structure-borne noise, drilling/deployment/recovery activity, wind/ambient noise, vessel or equipment interference, and changes in the array/support state. These records contextualize domain shift; they do not validate a detailed ice propagation model by themselves.

Simulation is a controlled development and debugging resource, not proof of field performance. BELLHOP is a candidate propagation tool, not an already validated under-ice simulator. A pressure-release free-surface model is not equivalent to ice. Every simulation configuration must state surface/boundary assumptions, whether ice structure/noise is represented, its source of evidence, and the resulting sim-to-real limitation. Per-sensor propagation and preservation of inter-sensor delays, phase, amplitude, and multipath remain required safeguards.

Keep simulation resource-bounded: independent environments for the measured linear configuration, physically checked sensor delays/phase and recorded direct/reflected/noise components. Run the frozen-E phase/TDOA gate on simulation **before** the random-subarray Fusion pilot. Held-out linear layout/spacing remains optional E2; non-linear geometry evidence is only a separately approved simulation study, never field topology proof.

## 7. Campaign calendar and contingency

- **By 2026-11-15:** complete bench rehearsal and freeze G5–G6: band/sample rate/sector/representation, calibration/QA/splits, and **Stage-1 E gate, Stage-2 mask/target, Stage-3 branches, resource and supervisor scope decision**. Field readiness does not require positive JEPA results; unrun/failed gates are recorded, not fabricated.

If authorized safe access or usable labelled data is unavailable, do not claim the real-data minimum is complete, do not silently substitute simulation, and do not promise a later campaign. The candidate, supervisor, and field lead must document a revised scientific scope, what field evidence is missing, which conclusions remain simulation-only or descriptive, and what formal adequacy remains unresolved.

## 8. Unevaluated prerequisites

Before a field claim can be made, G1–G9 must have evidence-based dispositions. In particular, the campaign still requires confirmation of authorized site/access and safety leadership, a controlled labelled transmitter/source, one phase-preserving shared-clock linear-array acquisition chain, underwater geometry/uncertainty metrology, a justified identifiable sector, valid far-field or range-aware interpretation, independent groups with a reserved test group, and archive/QA access controls. No prerequisite in this protocol has been confirmed by this document.
