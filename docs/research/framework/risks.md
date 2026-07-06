# Risks And Validity Threats

> Split from `docs/research_framework.md`. This file covers validity threats, leakage, sim-to-real risk, shortcut learning, model complexity, and deployment constraints.

## 21. Risks and Validity Threats

### Risk 1: Overfitting to a Narrow Synthetic Signal Family

The model may learn artifacts of a specific synthetic signal generator or signal morphology instead of general DOA-relevant structure.

This risk is especially high if training and validation are dominated by one family, such as chirps.

Mitigation:

- use the six core synthetic signal families;
- evaluate performance separately for each signal family;
- hold out selected signal families or parameter ranges for OOD testing;
- introduce hydroacoustic channel effects;
- validate on real hydroacoustic data.

### Risk 2: Loss of Phase or Delay Information

Preprocessing or single-channel encoding may remove information required for DOA.

Mitigation:

- preserve complex and phase-aware features;
- test inter-channel phase features;
- avoid excessive early pooling;
- perform representation ablation.

### Risk 3: Data Leakage

Overlapping windows, shared noise samples, shared real-noise recordings, shared channel impulse responses, or shared simulation seeds may leak information between train and test.

Mitigation:

- split by scene, not by window;
- separate synthetic and real noise banks;
- split real noise by recording session, day or deployment, location, sensor setup, and source file;
- separate simulation seeds;
- separate channel configurations;
- separate tonal-interference generation seeds and interferer trajectories;
- perform leakage audits.

### Risk 3a: Real-Noise Signature Memorization

If real recorded noise is reused across train and test, the model may memorize recording-specific spectral, temporal, sensor, or environmental signatures rather than learning robust DOA-relevant structure.

Mitigation:

- hold out complete real-noise recordings, sessions, locations, or deployments;
- evaluate on unseen real-noise recordings;
- report performance separately for synthetic noise, seen real-noise sources, and unseen real-noise sources;
- avoid splitting overlapping windows from the same real-noise recording across train, validation, and test sets.

### Risk 4: Poor Transfer from BELLHOP Simulation to Real Hydroacoustic Conditions

A model trained on BELLHOP-based simulation may still fail on real underwater recordings because real channels may include effects that are simplified, unknown, or misconfigured in the simulator.

Mitigation:

- introduce real data when it becomes available;
- randomize BELLHOP environment parameters;
- evaluate BELLHOP-to-real transfer explicitly;
- include real-data self-supervised pretraining;
- validate on held-out real hydroacoustic recordings.

During the initial BELLHOP-only phase, this risk cannot be resolved. It can only be reduced through domain randomization, environment splits, conservative claims, and preparation of a later real-recording validation protocol.

### Risk 4a: Simulator Shortcut Learning

The model may learn artifacts of the BELLHOP simulation setup rather than robust hydroacoustic DOA cues.

Mitigation:

- use multiple BELLHOP environment configurations;
- split train and test by environment, not only by signal window;
- randomize source depth, receiver depth, range, bathymetry, bottom parameters, and sound-speed profiles;
- test on BELLHOP environments not seen during training;
- compare against real recordings as the final validation layer.

### Risk 4b: Novik Bay Overfitting

A model trained or selected primarily on a Novik-like BELLHOP configuration may learn a narrow target-environment prior instead of robust hydroacoustic DOA structure.

Mitigation:

- keep the main training distribution domain-randomized across multiple BELLHOP environments;
- keep the Novik Bay BELLHOP setup as a separate target benchmark whenever possible;
- report randomized held-out environment performance separately from Novik target-benchmark performance;
- state explicitly whether Novik-like environments were included during training;
- validate on real Novik Bay or comparable recordings before making operational claims.

### Risk 4c: Unrealistic Real-Noise Mixing

Adding real recorded noise to BELLHOP-propagated target signals can create mixtures that do not correspond to a physically plausible hydroacoustic scene, especially when single-channel noise is copied across sensors or multi-channel noise is channel-shuffled incorrectly.

Mitigation:

- prefer multi-channel real noise when spatial noise structure matters;
- preserve channel order and timing for multi-channel noise recordings;
- mark single-channel real-noise augmentation as an approximation;
- document how single-channel noise is replicated, decorrelated, or randomized across channels;
- evaluate separately on synthetic noise, real-noise-augmented simulation, and later real recordings.

### Risk 4d: Narrowband Spectral Shortcut Learning

Under strong tonal or narrowband interference, the model may learn to associate specific spectral peaks, interference frequencies, or interference artifacts with DOA labels rather than using array geometry and inter-channel structure.

Mitigation:

- hold out tonal frequencies, bandwidths, SIR ranges, and interferer directions;
- include BELLHOP-propagated interferers with independent DOA when spatial interference matters;
- report target-interferer angular separation;
- compare performance under sensor-level tonal contamination and physically propagated acoustic interferers;
- evaluate on unseen narrowband interference conditions.

### Risk 4e: Sampling-Rate and Chunking Artifacts

Different original sampling rates, inconsistent resampling, or poorly defined chunking may create hidden domain labels or destroy DOA-relevant timing and phase cues.

Specific failure modes include:

- resampling or decimation changes inter-channel phase or delay;
- anti-alias filtering is missing or inconsistent across channels;
- STFT or CWT bins are not comparable across sampling rates;
- chunk boundaries cut transient source events;
- the model learns sampling-rate or preprocessing artifacts instead of hydroacoustic structure.

Mitigation:

- use a common target sampling rate for the first executable protocol;
- apply useful-band selection, anti-alias filtering, and documented decimation or resampling;
- use coherent preprocessing across all hydrophone channels;
- define chunks, hops, context windows, and prediction horizons in seconds;
- retain original and target sampling-rate metadata;
- report the preprocessing and chunking policy in every experiment-level protocol.

### Risk 4f: Destructive or Leaky Normalization

Normalization may remove DOA-relevant information or leak evaluation information into training.

Specific failure modes include:

- per-channel normalization erases inter-channel amplitude cues;
- independent I/Q normalization distorts complex phase structure;
- per-frame maximum normalization erases SNR and source-presence cues;
- validation or test statistics leak into preprocessing;
- STFT or CWT scaling makes frequency bins or scale bands incomparable across conditions.

Mitigation:

- estimate normalization statistics on the training split only;
- prefer array-level or train-split normalization over independent per-channel normalization;
- preserve complex phase through appropriate representation;
- specify STFT dB reference, epsilon, and clipping policy;
- report whether absolute signal level is preserved or discarded;
- keep normalization policies identical across fair comparisons unless representation-specific differences are justified.

### Risk 4g: Held-Out Environment Set Too Small for Generalization Claims

Several requirements in this framework depend on held-out BELLHOP environments as evidence of generalization. With too few generated environments, a held-out split can produce a misleadingly optimistic or pessimistic result because of sampling variance, regardless of whether the model actually generalizes across environmental conditions.

Specific failure modes include:

- a single train/test environment split is treated as sufficient evidence of environment generalization;
- a favorable result on a small held-out set is reported as a general claim without acknowledging the sample size;
- environment count is driven by BELLHOP compute cost rather than by what the claim requires, and the mismatch is not disclosed;
- variance across held-out environments is not reported, so a lucky or unlucky split cannot be distinguished from a real effect.

Mitigation:

- report the number of independent training and held-out environments alongside every environment-generalization claim;
- report variance or a range across held-out environments, not only the mean, whenever more than one held-out environment is available;
- treat environment-generalization claims from fewer than approximately 10 held-out environments as preliminary and explicitly label them as such in the claim-to-evidence table;
- prefer multiple smaller held-out environment groups with reported spread over a single large but homogeneous held-out set;
- if BELLHOP compute cost limits the number of environments that can be generated, state this constraint explicitly;
- treat the Novik Bay target benchmark as a single additional data point, not as a substitute for a sufficiently large randomized held-out set.

### Risk 5: Over-Specialization to One Array Geometry

The model may perform well only on one fixed array.

Mitigation:

- use geometry conditioning;
- train with multiple geometries when possible;
- evaluate unseen geometry transfer;
- use lightweight geometry adapters.

### Risk 5a: Geometry Overfitting Despite Conditioning

A model may receive geometry metadata but still overfit to the training geometry families, aperture, or spacing.

Mitigation:

- include no-geometry, coordinate-only, and pairwise-geometry baselines;
- test held-out topology, changed spacing, and changed aperture;
- evaluate missing sensors and subarray inference;
- compare zero-shot, adapter tuning, partial fine-tuning, and full fine-tuning.

### Risk 5a-bis: Channel-Order Leakage

The array encoder may learn to rely on channel slot position rather than physical geometry, even when geometry metadata is provided. This is a more fundamental failure mode than ordinary geometry overfitting: an order-leaking model has not learned a geometry-conditioned representation, because its predictions are tied to an arbitrary input-list convention rather than to sensor positions.

Specific failure modes include:

- a positional encoding or learned embedding implicitly indexed by slot position rather than by geometry features;
- a fixed concatenation, sorting, or pooling order before final readout that silently encodes slot identity;
- geometry features computed relative to "the first sensor in the list" instead of the documented array-center or physical reference;
- apparently strong same-geometry performance that does not survive the permutation canary test (9.3a).

Mitigation:

- run the permutation canary test (9.3a) before reporting any Stage 2 or downstream result;
- randomize channel ordering across training examples regardless of architecture family;
- audit the implementation for any operation that depends on input-list position rather than geometry features;
- treat a failed canary test as a blocking implementation bug, not as a modeling choice to ablate.

### Risk 5b: Steering-Aware Branch Overfits to Simplified Propagation

Neural-SRP or steering-aware branches may overfit to far-field, single-path, or simplified steering assumptions and fail under BELLHOP multipath or real hydroacoustic conditions.

Mitigation:

- evaluate steering-aware branches across multiple BELLHOP environments;
- compare against non-steering geometry-aware encoders;
- report performance separately for nominal, domain-randomized, and held-out BELLHOP environments;
- treat steering-aware outputs as physics-informed candidates, not final proof of real-world performance.

### Risk 5c: GNN Under-Models Dense Pairwise Structure

Graph message passing may under-model dense all-pairs phase, delay, and coherence relations if the graph connectivity, edge features, or message-passing depth are insufficient.

Mitigation:

- compare GNN / relation networks against pairwise Transformer models;
- include complete-graph and distance-threshold graph variants;
- evaluate masked-sensor prediction and pairwise relation diagnostics;
- monitor performance under missing sensors and changed topology.

### Risk 6: Weak Baseline Comparison

If baselines are missing, poorly tuned, or limited to very simple methods, the claimed benefit of the neural framework will be unreliable.

This risk is especially serious if the proposed model is compared mainly against delay-and-sum or Bartlett beamforming, or only against weak supervised CNN/CRNN baselines. Those methods are useful diagnostics and lower-bound references, but they are not strong evidence that the proposed model improves over competitive classical or neural DOA estimation.

Mitigation:

- include primary classical baselines such as MVDR / Capon, MUSIC, GCC-PHAT or TDOA estimation, SRP-PHAT, and matched-field processing when environment replicas are available;
- treat delay-and-sum or Bartlett beamforming only as a sanity-check and lower-bound diagnostic baseline;
- state applicability assumptions for ESPRIT, Root-MUSIC, sparse methods, and matched-field processing;
- report whether a baseline uses privileged BELLHOP or environmental information;
- include supervised neural baselines, including at least one strong SOTA-adjacent neural baseline when making superiority claims;
- include ablation baselines for SSL, geometry conditioning, latent dynamics, and Stage 4 adaptation;
- report whether neural baselines use handcrafted spatial features;
- tune baselines fairly;
- report runtime and preprocessing cost;
- report where the neural model wins and loses.

### Risk 7: Latent Collapse

Self-supervised training may produce uninformative embeddings.

Mitigation:

- monitor embedding variance;
- monitor embedding covariance and active embedding dimensions;
- use linear probes;
- use stop-gradient, EMA target encoders, or variance regularization when needed;
- compare multiple SSL objectives.

This risk is especially important for JEPA-style next-embedding prediction, because both the online encoder and the target encoder operate in latent space and do not reconstruct raw signals by default.

### Risk 7a: Trivial Next-Chunk Prediction

If Stage 1 training only predicts the immediately adjacent chunk, the model may learn local smoothness rather than reusable hydroacoustic signal structure.

Mitigation:

- compare one-step prediction against multi-horizon prediction;
- use temporal-gap prediction;
- include masked or random target chunks inside longer context windows;
- evaluate representation quality with shallow probes and downstream array-level DOA tasks;
- verify that timing-sensitive and phase-sensitive information remains available to the array encoder.

### Risk 7b: Destructive Phase or Timing Augmentation

Array-level SSL may accidentally train the model to ignore inter-channel phase, delay, or coherence if phase distortion, phase jitter, timing jitter, or per-channel delay perturbation are used as generic augmentations.

Mitigation:

- allow phase and timing perturbations only as bounded calibration or synchronization error simulations;
- document the perturbation range in experiment-level protocols;
- run phase and delay preservation diagnostics;
- compare against no-phase-perturbation baselines;
- verify downstream DOA performance under clean and perturbed conditions.

### Risk 7c: Self-Distillation Shortcut Invariance

DINOv3-inspired teacher-student self-distillation may learn invariance to array corruptions instead of learning geometry-aware inter-channel structure.

Mitigation:

- keep the teacher view full or only weakly corrupted;
- use geometry metadata in both teacher and student views;
- include sensor-token and pairwise-relation targets, not only global embeddings;
- evaluate held-out geometry transfer;
- test masked-sensor prediction and downstream DOA after pretraining.

### Risk 7d: Stage 3 Duplicates Stage 1 Temporal Modeling

The latent dynamics module may duplicate temporal structure already learned by the single-channel encoder instead of adding array-scene temporal value.

Mitigation:

- train the first Stage 3 model with Stage 1 and Stage 2 frozen;
- feed Stage 3 only array-scene latent states, not raw channel inputs or per-channel feature maps;
- compare against Stage 1 + Stage 2 without dynamics;
- compare against temporal pooling and lightweight TCN or GRU baselines.

### Risk 7e: Temporal Over-Smoothing

Stage 3 may reduce DOA jitter by over-smoothing real source onset, offset, impulsive transients, or rapidly changing source direction.

Mitigation:

- evaluate impulsive transients and intermittent source activity separately;
- report source presence detection metrics with and without dynamics;
- measure horizon-specific prediction errors;
- compare static-source stabilization against moving-source and event-aware tests;
- use residual refinement rather than replacing Stage 2 latents in first experiments.

### Risk 7f: BELLHOP Temporal Artifact Learning

Predictive dynamics may learn temporal artifacts of synthetic BELLHOP scene generation, source trajectories, or overlapping windows rather than robust hydroacoustic scene dynamics.

Mitigation:

- split train and test by trajectory, source signal seed, and BELLHOP environment;
- avoid overlapping-window leakage between train and test;
- evaluate held-out BELLHOP environments;
- compare static, moving, and event-aware scenarios separately.

### Risk 7g: Stage 3 Degrades Geometry Transfer

Temporal dynamics may overfit to geometry-specific latent trajectories and reduce zero-shot or lightweight adaptation performance on held-out arrays.

Mitigation:

- evaluate Stage 3 under held-out geometry splits;
- compare geometry-transfer performance with and without Stage 3;
- report missing-sensor and subarray inference performance;
- keep Stage 3 lightweight until geometry-transfer benefit is demonstrated.

### Risk 7h: Downstream Head Hides Weak Backbone

A powerful downstream head may compensate for a weak pretrained representation, making it unclear whether performance comes from self-supervised representation learning or from supervised head capacity.

Mitigation:

- require linear or head-only probing as the first Stage 4 evaluation;
- report head capacity and trainable parameter count;
- compare head-only probing, nonlinear head-only tuning, adapter tuning, and partial fine-tuning;
- keep splits and labeled-data budgets identical across Stage 4 adaptation modes.

### Risk 7i: Fine-Tuning Destroys SSL Representation

Full or aggressive partial fine-tuning may overwrite the self-supervised representation and reduce label efficiency, robustness, or transfer to new geometries.

Mitigation:

- treat full end-to-end fine-tuning as an upper-bound baseline;
- compare against frozen-backbone and adapter-tuning modes;
- use gradual unfreezing when partial fine-tuning is needed;
- evaluate pre- and post-fine-tuning representation quality with probes and downstream transfer tests.

### Risk 7j: Stage 4 Reduces Geometry Transfer

Task-specific fine-tuning may overfit to the labeled training geometry and reduce zero-shot or lightweight adaptation performance on held-out arrays.

Mitigation:

- evaluate all Stage 4 modes under held-out geometry splits;
- compare head-only, geometry-adapter, partial fine-tuning, and full fine-tuning;
- report performance gap to same-geometry evaluation;
- freeze geometry-conditioned components unless adaptation benefit is demonstrated.

### Risk 7k: Overfitting to BELLHOP Labels

Supervised Stage 4 training may overfit to labels generated under a narrow BELLHOP configuration and fail under held-out environments, real-noise augmentation, or later real recordings.

Mitigation:

- train and evaluate across domain-randomized BELLHOP environments;
- keep Novik Bay target benchmarks separate when possible;
- report held-out environment performance separately;
- evaluate real-noise-augmented BELLHOP data and later real recordings before making real-world claims.

### Risk 7l: Probability-Map Overconfidence

The angular probability-map head may produce sharp but poorly calibrated distributions, especially under multipath, low SNR, tonal interference, or ambiguous array geometries.

Mitigation:

- report negative log-likelihood and calibration metrics;
- use calibration-only tuning when needed;
- evaluate uncertainty under ambiguous, low-SNR, and multi-path BELLHOP scenarios;
- compare probability-map performance against regression-only heads.

### Risk 7m: Source-Presence Head Learns Noise Artifacts

The source-presence head may learn noise signatures, synthetic artifacts, or real-noise recording identity instead of true source activity.

Mitigation:

- split noise recordings by independent session, location, and source file;
- evaluate source presence on unseen real-noise recordings;
- include noise-only, interference-only, source-only, and source-plus-interference windows;
- report false alarm and missed detection rates by noise type and SNR.

### Risk 7n: Multi-Task Loss Imbalance

Combined training of DOA regression, angular probability maps, and source presence may cause one task to dominate optimization and degrade the others.

Mitigation:

- report all loss weights;
- compare single-head and multi-head training;
- monitor per-task metrics during training;
- treat multi-task training as beneficial only if it improves or preserves all core task families.

### Risk 8: Excessive Model Complexity

A large predictive model may be harder to train, debug, deploy, and interpret.

Mitigation:

- compare against simple baselines;
- report model size and inference time;
- use staged training;
- justify each architectural component through ablation.

### Risk 9: Real-Time and Edge-Computer Constraints

The framework is intended to remain compatible with future real-time and edge-computer use, but the initial research stage should not be forced into aggressive deployment optimization before the scientific claims are tested.

Mitigation:

- report model size, memory usage, and inference latency from the beginning;
- keep preprocessing and model components modular;
- compare large research models against smaller deployable variants;
- treat embedded optimization as a later engineering stage unless latency prevents meaningful use.

---

