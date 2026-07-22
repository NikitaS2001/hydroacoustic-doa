# Roadmap And Success Criteria

> This file covers assumptions, scope boundaries, deliverables, roadmap, success criteria, kill/pivot criteria, and the final research statement.

## 22. Assumptions

The framework assumes:

- multi-channel hydroacoustic data is available or can be simulated;
- array geometry is known, estimated, or defined synthetically for controlled simulations;
- unlabeled data is easier to obtain than labeled DOA data;
- downstream labeled subsets are available for evaluation or fine-tuning in simulation, and may become available later for real recordings;
- inter-channel structure contains useful DOA information;
- geometry conditioning can improve transfer across arrays.

For the initial Novik Bay research stage, the framework assumes that:

- exact hydrophone-array parameters are not yet fixed;
- initial array experiments can use simple geometries such as ULA, square, or rectangular arrays;
- exact BELLHOP environmental parameters are not yet fixed;
- BELLHOP training should use domain-randomized environments rather than only one Novik-like environment;
- the Novik Bay BELLHOP setup is a target benchmark placeholder until local parameters are available;
- real hydroacoustic recordings are not yet available;
- first-stage conclusions are limited to BELLHOP-based simulation unless explicitly updated by real-data validation.

Each concrete experiment must state which of these assumptions hold.

---

## 23. Out of Scope for the Initial Framework

The following are outside the initial framework scope unless explicitly added in later work:

- full oceanographic propagation modeling;
- full 3D source localization under arbitrary bathymetry;
- multi-source tracking;
- moving receiver platform modeling;
- end-to-end raw waveform reconstruction as the primary goal;
- aggressive deployment optimization for embedded hardware;
- complete real-time operational system design;
- causal streaming inference with fixed latency constraint;
- complete uncertainty-calibrated tracking pipeline.

These topics may be added later as extensions. However, because the intended application direction includes real-time and edge-computer use, experiment reports should still track computational cost, inference latency, memory footprint, and preprocessing cost.

---

## 24. Expected Deliverables

The research program should produce:

- full-model Tiny/Small/Base/Large/XL ladder with separate per-channel encoder parameter caps;
- modular IQ, STFT, and CWT preprocessing pipeline;
- optional Tier-1 self-supervised single-channel encoder;
- geometry-conditioned array encoder;
- deferred predictive latent dynamics module in a post-MVP protocol;
- DOA regression head;
- angular probability-map head;
- source presence detection head;
- baseline implementations;
- ablation study reports;
- first executable BELLHOP-only experiment protocol;
- hydroacoustic validation protocol;
- real-recording validation protocol, when data access becomes available;
- reproducible experiment configurations;
- computational cost and latency reports;
- final research report.

---

## 25. Suggested Development Roadmap

The roadmap follows the full-model ladder defined in `architecture.md` Section 8.12. Milestone 2 should use only Tiny and Small full-model families. Base is a post-Tier-0 scale-up candidate after Small passes its rejection gate. Large and XL are research-only branches and must not be used to rescue a failed MVP result.

For the current MVP, Milestone 2 freezes reusable clean BELLHOP channels, deterministic post-hoc ordinary-noise/tonal overlays, and separately propagated coherent acoustic interferers. Frozen cells are clean `+inf`; white SNR `{20,10,0}` plus dev-test stress `-5`; dev-test colored `1/f` SNR `{20,10,0}` and `1/f²` SNR `{20,10}`; and dev-test incoherent-tonal/coherent-acoustic SIR `{20,10,0}`. Primary source families use frozen `500-1400 Hz` support and a pre-output exact projected-clean-power eligibility check. The protocol preserves the canonical `500-3000 Hz` base-overlay scalar/report and derives replayable `500-1400 Hz` primary and `(1400,3000] Hz` stress views with one array-wide scalar each. Inference nests views below overlays; only identical eligible rows and complete eligible environments enter Tier-0 thresholds, CI, power, or effective `N`. The six-factor environment LHS excludes nested source/receiver/channel draws. The matched supervised Tier-0 pair precedes optional separately preregistered SSL Tier 1; Stage 3 is deferred.

The future diagnostic pilot has not run. Solver/build, broadband convergence, runtime, allocation/power, replay, and model gates are `not yet evaluated`; full generation remains blocked. Novik/real-recording validation is a later distinct branch and does not expand this simulation-only MVP.

### Milestone 1: Framework Formalization

- define task variants;
- define the initial Novik Bay / Russky Island target assumptions;
- define whether the first task is far-field 1D azimuth only;
- define array-geometry representation;
- define initial simple array families such as ULA and square or rectangular arrays;
- define core downstream heads;
- define baseline requirements;
- write the first executable BELLHOP-only experiment protocol skeleton.

### Milestone 2: Controlled Synthetic and BELLHOP Prototype

- implement the six core synthetic signal families;
- implement configurable BELLHOP-based hydroacoustic propagation;
- create a domain-randomized BELLHOP training distribution;
- create a preliminary Novik Bay BELLHOP target benchmark once environmental assumptions are available;
- construct multi-channel hydrophone-array observations from BELLHOP outputs;
- define synthetic noise and narrowband interference generation;
- collect, import, or reserve real noise recordings for augmentation when available;
- define real-noise metadata and split policy;
- implement real-noise augmentation for BELLHOP-propagated observations;
- implement IQ, STFT, and CWT input pipelines;
- train minimum supervised neural baselines;
- add at least one strong SOTA-adjacent neural baseline before making superiority claims;
- implement framework ablation baselines for SSL, geometry conditioning, and latent dynamics;
- run classical baselines.
- restrict neural model training to Tiny and Small full-model families unless a later protocol explicitly records that the Small rejection gate passed.

### Milestone 3: Optional Tier-1 Self-Supervised Backbone Prototype

- train single-channel SSL encoder;
- train array-level SSL encoder;
- evaluate representation quality using linear probes.
- evaluate Base-scale encoder variants only after the Small family passes Tier 0 gates.

### Milestone 4: Geometry Conditioning

- add sensor-coordinate conditioning;
- test one fixed geometry;
- test modified geometry;
- evaluate zero-shot and adapter-based transfer.

### Milestone 5: Predictive Latent Dynamics (Deferred Beyond MVP)

- implement latent prediction;
- compare against no-dynamics and temporal pooling;
- evaluate temporal robustness.

### Milestone 6: Task-Specific Fine-Tuning

- define the Stage 4 adaptation ladder;
- implement head-only probing;
- implement nonlinear head-only fine-tuning;
- implement adapter tuning;
- implement partial fine-tuning;
- run label-efficiency experiments;
- evaluate full end-to-end fine-tuning only as an upper-bound comparison;
- evaluate calibration-only tuning for probabilistic outputs.

### Milestone 7: Hydroacoustic Validation

- define the BELLHOP simulation protocol;
- document whether real recordings are available;
- define the real-recording validation protocol when data acquisition or access becomes available;
- run classical and neural baselines;
- evaluate core heads;
- perform BELLHOP-domain transfer analysis;
- perform BELLHOP-to-real transfer analysis only after real recordings and DOA ground truth are available.

### Milestone 8: Final Ablation and Reporting

- finalize ablation studies;
- report primary, secondary, and diagnostic metrics across SNR, SIR, angle, noise, channel, environment, and geometry;
- produce claim-to-evidence and final scorecard tables;
- explicitly report failed, partial, and not-yet-evaluated claims;
- report model size, memory footprint, inference latency, and preprocessing cost;
- document reproducibility;
- identify limitations and future work;
- document causal streaming inference and fixed-latency operation as a post-MVP extension if block-based results are successful.

---

## 26. Success Criteria

The framework can be considered successful only if concrete experiments provide corresponding evidence for each claimed contribution. Simulation-stage success and real-world success must be reported separately.

The success criteria are:

1. self-supervised pretraining improves label efficiency under controlled label-budget comparisons;
2. geometry conditioning improves transfer to new array layouts under held-out geometry tests;
3. the shared backbone supports multiple heads without full retraining;
4. the model performs competitively against strong classical DOA baselines, not only diagnostic lower-bound baselines;
5. the model performs competitively against strong neural baselines and relevant framework ablations;
6. the predictive latent module improves robustness or temporal consistency without over-smoothing source events;
7. performance remains meaningful under BELLHOP-based hydroacoustic simulation across held-out environments;
8. for the first-stage Novik Bay scenario, simulation-stage results remain robust across held-out BELLHOP environments and simple array geometries;
9. performance transfers to real hydroacoustic recordings once such recordings and DOA ground truth are available;
10. model size, preprocessing cost, memory footprint, throughput, and inference latency remain compatible with future real-time or edge-computer investigation;
11. results are reproducible across random seeds and dataset splits.

No claim should be marked successful unless the corresponding experiment family has been run and reported. BELLHOP-only results may support simulation-stage claims but must not be used as evidence for real-world hydroacoustic performance.

The final report should include a scorecard with:

- claim;
- required evidence;
- primary metrics;
- best classical baseline;
- best neural baseline;
- result status;
- limitation;
- next action.

### 26.1 Kill / Pivot Criteria

After the minimum viable claim set (18.0) is run, the framework should be paused or descoped — not extended with more architecture — if any of the following hold:

- geometry conditioning does not improve over a no-geometry baseline on the ULA → square/rectangular transfer test;
- SSL pretraining does not improve label efficiency at the 50% label budget compared to supervised-from-scratch;
- the proposed model does not beat MVDR/Capon or MUSIC on the BELLHOP-only benchmark under matched information conditions;
- the permutation canary test fails for the geometry-conditioned array encoder;
- held-out BELLHOP environment results have too few independent environments or too much variance to support the claimed generalization.

If any of these hold, the next step is to report this honestly as a negative or partial result, not to add Stage 3, advanced SSL objectives, or additional architecture candidates in search of a positive signal.

---

## 27. Final Research Statement

This research direction aims to develop a **geometry-conditioned self-supervised representation framework for hydroacoustic DOA and array-signal understanding**.

The model is intended to serve as a transferable backbone rather than a single fixed DOA estimator. It should learn latent representations from unlabeled hydroacoustic array data, condition those representations on hydrophone geometry, and support multiple downstream heads such as DOA regression, angular probability-map estimation, and source presence detection.

The central scientific question is whether such a backbone can generalize across hydroacoustic conditions and array geometries while requiring only lightweight adaptation to new configurations, and whether representations learned in BELLHOP-based simulation transfer to real hydroacoustic recordings.

The central engineering question is whether this framework can be implemented in a reproducible, modular, and experimentally verifiable way while remaining competitive with classical DOA methods and direct supervised neural baselines.
