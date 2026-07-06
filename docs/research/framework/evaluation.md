# Evaluation, Baselines, And Protocols

> Split from `docs/research_framework.md`. This file covers baselines, metrics, experiment families, reproducibility, and experiment-level protocol requirements.

## 16. Baseline and Fair Comparison Protocol

The framework requires comparison against classical and neural baselines.

### 16.1 Classical DOA Baselines

Classical baselines should be separated by role and applicability. They should not be treated as interchangeable.

#### Diagnostic Lower-Bound Baseline

Delay-and-sum or Bartlett beamforming should be included only as a sanity-check and lower-bound diagnostic baseline.

It is useful for:

- checking steering-grid construction;
- checking array-geometry conventions;
- checking delay-sign conventions;
- detecting errors in BELLHOP signal construction;
- establishing a simple interpretable lower-bound reference.

It should not be treated as a strong comparator and should not be used as the primary evidence for the proposed model's advantage.

#### Primary Classical Comparators

The primary classical comparators should include:

- MVDR / Capon beamforming;
- MUSIC;
- GCC-PHAT or pairwise TDOA estimation;
- SRP-PHAT;
- matched-field processing for BELLHOP-stage experiments when environment replicas are available.

MVDR / Capon, MUSIC, GCC-PHAT, and SRP-PHAT should be evaluated under the same BELLHOP environment splits, array-geometry splits, SNR/SIR regimes, and signal-family conditions as the proposed model.

#### Hydroacoustic Physics-Aware Baselines

Matched-field processing should be treated as the main hydroacoustic physics-aware baseline when the experiment provides enough environmental information to construct replica fields.

Concrete MFP variants may include:

- Bartlett MFP;
- MVDR or minimum-variance MFP;
- mismatched-environment MFP;
- oracle-environment MFP as a privileged upper-bound physics baseline.

Oracle MFP uses privileged environmental knowledge and must not be presented as an equal-information baseline. It should be reported separately from baselines that use only the information available to the proposed model.

#### Conditional Classical Baselines

The following baselines should be included only when their assumptions are explicitly satisfied:

- ESPRIT for shift-invariant array geometries;
- Root-MUSIC mainly for ULA or compatible narrowband assumptions;
- sparse, SAMV, or sparse Bayesian learning baselines as optional strict comparators;
- probabilistic focalization or ray-tracing Bayesian localization as optional advanced hydroacoustic baselines.

The experiment-level protocol must state why each conditional baseline is applicable before using it in a comparison.

### 16.2 Neural Baseline Protocol

Neural baselines should also be separated by role. They should be adapted to hydroacoustic BELLHOP-generated data and evaluated under the same splits as the proposed framework. SOTA-adjacent models from acoustic or SELD literature should not be presented as hydroacoustic SOTA unless this is demonstrated experimentally.

#### Minimum Neural Baselines

The minimum neural baseline set should include:

- direct supervised CNN or CRNN DOA estimator;
- supervised TCN DOA estimator;
- supervised Transformer or CNN-Transformer DOA estimator;
- supervised model trained from scratch with the same downstream heads as Stage 4;
- model trained from scratch without self-supervised pretraining.

The IQ-based model should be treated as the primary neural input baseline for the single-channel encoder.

#### SOTA-Adjacent Acoustic and SELD Baselines

The stronger neural baseline set should include SOTA-adjacent architectures from sound event localization and detection, acoustic localization, and sequence modeling:

- SELDnet or CRNN-style SELD baseline;
- SELD-TCN;
- ACCDOA or Multi-ACCDOA-style output formulation;
- ResNet-Conformer or SE-ResNet-Conformer;
- EINV2 or MFF-EINV2;
- SELD-Mamba or PSELDnet with BiMamba-style sequence modeling.

These baselines should be treated as architecture families requiring hydroacoustic adaptation, not as directly transferable pretrained systems.

#### Framework Ablation Baselines

The neural baseline suite must include ablations that test the framework's main claims:

- no-SSL baseline;
- no-geometry baseline;
- no-Stage 3 latent dynamics baseline;
- Stage 1 + Stage 2 only;
- Stage 1 + Stage 2 + temporal pooling;
- same Stage 4 heads trained from scratch;
- head-only probing;
- adapter tuning;
- partial fine-tuning;
- full fine-tuning as an upper-bound comparison.

#### Handcrafted-Feature Neural Baselines

External neural baselines may use handcrafted multi-channel spatial features:

- SALSA or SALSA-Lite neural baseline;
- NGCC-PHAT neural TDOA feature baseline;
- geometry-aware supervised DNN using coordinates and GCC-PHAT-like features.

These baselines are valid comparators, but they do not redefine the proposed Stage 2 input contract. Their use of handcrafted spatial features must be reported explicitly.

#### Hybrid Neural-Classical Baselines

Optional strict neural-classical baselines may include:

- SubspaceNet or DeepMUSIC-style methods;
- Neural-SRP or steering-aware neural baselines;
- SHAMaNS or neural steering-style baselines.

Methods originating from RF, narrowband array processing, or non-hydroacoustic microphone-array literature require explicit applicability checks before being used as hydroacoustic baselines.

For each neural baseline, the protocol should report:

- architecture family;
- input representation;
- whether IQ, STFT, CWT, or handcrafted spatial features are used;
- whether geometry metadata are used;
- whether self-supervised pretraining is used;
- whether BELLHOP labels or real labels are used;
- labeled-data budget;
- Stage 4 adaptation mode;
- parameter count;
- approximate compute or FLOPs, when available;
- inference latency;
- preprocessing cost;
- whether the model is trained from scratch or initialized from pretrained weights;
- whether privileged geometry, environment, or simulator information is used.

### 16.3 Fair Comparison Requirements

Baselines must be evaluated under the same conditions:

- same train/validation/test splits;
- same input duration;
- same sampling rate;
- same array geometry;
- same SNR conditions;
- same test scenes;
- same metrics.

For each classical baseline, the protocol must specify:

- near-field or far-field assumption;
- narrowband or broadband formulation;
- required array geometry;
- required number of sources, if applicable;
- covariance estimation policy;
- snapshot or window length;
- diagonal loading, if used;
- steering-grid resolution;
- sound-speed assumption;
- whether BELLHOP or other environment replicas are used.

For every classical or neural baseline, reports should include:

- input data or features;
- geometry knowledge used by the method;
- environment knowledge used by the method;
- whether privileged information is used;
- SNR and SIR regime;
- BELLHOP environment split;
- array geometry split;
- output type;
- metrics;
- tuned hyperparameters;
- runtime;
- preprocessing cost.

Classical baselines should be reasonably tuned. Weak or poorly configured baselines do not provide meaningful evidence for the proposed framework.

Handcrafted spatial features such as GCC-PHAT, covariance matrices, cross-spectra, inter-channel phase differences, beamspace features, SALSA/SALSA-Lite, or NGCC-PHAT may be used by external baselines. They must not be treated as Stage 2 encoder inputs for the proposed model unless the framework is explicitly redefined. The proposed Stage 2 path remains based on per-channel encoder outputs plus geometry metadata.

---

## 17. Evaluation Metrics

The exact metrics depend on the downstream head, but every experiment-level protocol should distinguish primary, secondary, and diagnostic metrics. Primary metrics are used for main claims. Secondary metrics provide supporting evidence. Diagnostic metrics are used to explain failure modes and should not by themselves support major claims.

### 17.1 DOA Regression Metrics

Primary DOA regression metrics:

- median angular error;
- 95th percentile angular error;
- accuracy within angular thresholds;
- circular angular error, when applicable.

Secondary DOA regression metrics:

- mean absolute angular error;
- root mean squared angular error.

Diagnostic DOA regression metrics:

- error by angle sector;
- error by signal family;
- error by BELLHOP environment;
- error by array geometry;
- error under clean, noisy, interfered, and real-noise-augmented conditions.

### 17.2 Angular Probability-Map Metrics

Primary angular probability-map metrics:

- negative log-likelihood;
- top-k angular error;
- calibration metrics;
- top-1 angular error.

Secondary angular probability-map metrics:

- probability mass around the true angle;
- peak sharpness;

Diagnostic angular probability-map metrics:

- spatial-spectrum similarity to classical methods, when appropriate;
- entropy or uncertainty by SNR and SIR;
- calibration by BELLHOP environment and array geometry;
- ambiguity behavior under multipath and target-interferer overlap.

### 17.3 Source Presence Metrics

Primary source presence metrics:

- F1 score;
- false alarm rate;
- missed detection rate.

Secondary source presence metrics:

- precision;
- recall;
- ROC-AUC;
- accuracy.

Diagnostic source presence metrics:

- confusion by noise type;
- confusion by interference type;
- false alarms on noise-only and interference-only windows;
- missed detections on low-SNR, impulsive, and intermittent-source windows.

### 17.4 Stratified Reporting Requirements

Metrics should be reported across:

- SNR levels;
- SIR levels;
- signal families;
- source state, including static, moving, intermittent, and event-like conditions when used;
- noise types;
- real-noise recording sources;
- tonal interference frequency;
- tonal interference bandwidth;
- interferer DOA;
- angular separation between target and interferer;
- source types;
- angular regions;
- array geometries;
- held-out geometry conditions;
- BELLHOP environments;
- Novik target benchmark, when available;
- channel conditions;
- clean, noisy, interfered, and real-noise-augmented data;
- BELLHOP simulation and later real recordings, when available;
- in-distribution and out-of-distribution settings.

Aggregate metrics alone are insufficient for major claims. A method that improves average error while failing on held-out geometries, low SNR, strong narrowband interference, or held-out BELLHOP environments should be reported as partially successful at most.

### 17.5 Claim-to-Evidence Mapping

Each major claim should be tied to explicit experiment-family evidence.

| Claim | Required evidence |
|---|---|
| Self-supervised learning improves label efficiency | Label-efficiency experiments comparing supervised-from-scratch, frozen SSL backbone, adapter tuning, and partial fine-tuning under identical splits |
| Geometry conditioning improves array transfer | Held-out geometry experiments comparing no-geometry, coordinate-only, pairwise-geometry, and geometry-conditioned models |
| Stage 3 improves temporal robustness | Static-source stabilization, moving-source prediction, and event-aware tests compared against no dynamics and temporal pooling baselines |
| The proposed model beats strong classical baselines | Comparisons against MVDR / Capon, MUSIC, GCC-PHAT or TDOA, SRP-PHAT, and MFP when applicable |
| The proposed model beats strong neural baselines | Comparisons against minimum neural baselines and at least one SOTA-adjacent neural baseline when making superiority claims |
| Real-noise augmentation improves robustness | Clean, synthetic-noise, narrowband-interference, and real-noise-augmented comparisons with unseen noise recordings |
| BELLHOP-to-real transfer works | Evaluation on real recordings with DOA ground truth; BELLHOP-only results cannot support this claim |
| Edge or real-time feasibility remains plausible | Reported model size, preprocessing cost, memory footprint, throughput, and inference latency |

Claim status should be reported as:

- supported;
- partially supported;
- not supported;
- not yet evaluated.

### 17.6 Required Reporting Tables

Final experiment reports should include:

- main baseline comparison table;
- classical baseline table;
- neural baseline table;
- ablation table;
- geometry-transfer table;
- noise and interference robustness table;
- label-efficiency table;
- BELLHOP-domain transfer table;
- BELLHOP-to-real transfer table, only when real recordings and DOA ground truth are available;
- compute and latency table;
- reproducibility and configuration table.

### 17.7 Statistical Reliability and Failure Reporting

Key comparisons should use:

- multiple random seeds;
- fixed train/validation/test splits for paired comparisons;
- mean and standard deviation;
- confidence intervals when feasible;
- held-out BELLHOP environments;
- held-out array geometries;
- tail metrics, including 95th percentile error, not only averages.

Single-run improvements should be marked as preliminary and should not support strong claims.

Reports must explicitly state where the proposed model:

- loses to classical baselines;
- loses to neural baselines;
- does not benefit from self-supervised pretraining;
- fails to improve geometry transfer;
- degrades when Stage 3 is added;
- over-smooths source onset, offset, or motion;
- fails under real-noise augmentation;
- exceeds practical compute, latency, or memory constraints.

---

## 18. Experiment Families

This framework defines experiment families rather than one fixed experiment.

### 18.0 Minimum Viable Claim Set

Before all eight experiment families are pursued, the following minimum subset constitutes a publishable/defensible result on its own:

1. **Experiment Family 1** (Input Representation) — restricted to IQ vs. STFT, dropping CWT unless Family 1 results motivate it.
2. **Experiment Family 3** (Geometry Conditioning) — ULA → square/rectangular transfer only, dropping changed-aperture and missing-sensor variants for the first pass.
3. **Experiment Family 6** (Head Study) — head-only probing and full fine-tuning only, dropping the adapter/partial/gradual-unfreezing ladder for the first pass.
4. **Experiment Family 8** (Label Efficiency) — 10%/50%/100% only.

The first minimum viable claim set should be limited to Tier 0 components:

- input representation layer;
- single-channel encoder;
- geometry-conditioned array encoder;
- Stage 4 heads.

The first pass should use a narrow task:

- single-source far-field 1D azimuth;
- fixed operating band;
- 4-8 hydrophones;
- ULA to square or rectangular geometry transfer;
- BELLHOP arrivals or per-hydrophone impulse responses;
- domain-randomized shallow-water BELLHOP environments;
- a separate Novik-like target benchmark only after local assumptions are specified.

The minimum comparison set must include:

- supervised-from-scratch TCN or CRNN baseline;
- no-geometry baseline;
- geometry-conditioned pairwise Transformer or GNN;
- head-only probing;
- full fine-tuning as an upper-bound comparison;
- MVDR / Capon, MUSIC, SRP-PHAT or GCC-TDOA, and MFP when the required information is available.

The first pass must not include Stage 3 latent dynamics, DINOv3-inspired self-distillation, JEPA-style advanced objectives, Mamba, wav2vec 2.0, HuBERT, or other Tier 2 components as claimed contributions. These may be introduced only after the Tier 0 minimum set shows measurable value over no-SSL, no-geometry, and supervised-from-scratch baselines under matched information conditions.

Experiment Families 2, 4, 5, 7 and the omitted variants above are extensions to be pursued only if the minimum set shows the backbone provides measurable value. This avoids running the full ablation matrix before establishing that the framework's core claims hold at all.

### Experiment Family 1: Input Representation Study

Compare the three core single-channel input representations:

- IQ signal representation;
- STFT representation;
- CWT representation.

The comparison must be performed across the six core synthetic signal families:

- CW;
- linear chirp;
- nonlinear chirp;
- broadband pulse;
- impulsive transient;
- band-limited noise burst.

The goal is to determine which single-channel input representation provides the most robust features for downstream geometry-conditioned array-level DOA estimation.

A representation should not be considered superior only because it performs well on one signal family. The preferred representation should remain robust across multiple signal morphologies and hydroacoustic channel conditions.

### Experiment Family 2: Self-Supervised Objective Study

Compare:

- masked signal / masked feature modeling;
- JEPA-style next-embedding prediction;
- JEPA-style multi-horizon or temporal-gap prediction;
- contrastive learning;
- wav2vec 2.0-style quantized latent prediction;
- HuBERT-style hidden-unit prediction;
- data2vec-style contextual latent prediction;
- denoising or corrupted-input prediction;
- general JEPA-style latent prediction for array-level or dynamics stages;
- DINOv3-inspired teacher-student array self-distillation;
- BYOL-style teacher-student alignment;
- cross-channel prediction;
- cross-channel signal reconstruction;
- spatial contrastive learning;
- Spatial-HuBERT-style hidden spatial unit prediction;
- geometry-conditioned latent or acoustic-map prediction;
- phase, delay, cross-spectrum, and coherence auxiliary prediction;
- temporal latent prediction.

Goal: determine which self-supervised objectives produce the most useful representations for downstream DOA tasks.

After the TCN masked-modeling baseline is stable, this experiment family may also compare advanced self-supervised encoder families such as wav2vec 2.0 / HuBERT-style models. Such comparisons must separate gains from the encoder architecture, the self-supervised objective, and the amount of pretraining data.

At minimum, the Stage 1 objective study should compare:

- masked signal or masked feature modeling;
- contrastive predictive learning;
- JEPA-style one-step next-embedding prediction;
- JEPA-style multi-horizon or temporal-gap prediction;
- denoising or corrupted-input prediction;
- optional wav2vec 2.0 / HuBERT / data2vec-style objectives.

At minimum, the Stage 2 objective study should compare:

- masked sensor or masked channel latent prediction;
- cross-channel signal reconstruction;
- spatial contrastive learning;
- DINOv3-inspired array-level self-distillation;
- DINOv3-inspired array-level self-distillation with VICReg-style variance and covariance regularization;
- geometry-conditioned latent or acoustic-map prediction, if an interpretable spatial-map branch is introduced;
- optional BYOL-style teacher-student alignment.

At minimum, the Stage 3 objective study should compare:

- no dynamics;
- temporal pooling;
- one-step scene-latent prediction;
- multi-horizon scene-latent prediction;
- masked scene-latent modeling;
- residual temporal refinement;
- weak temporal-consistency regularization.

When comparing objectives, the encoder architecture should be held fixed whenever possible. Otherwise, results cannot distinguish whether improvements come from the objective, the architecture, or the amount of pretraining data. Stage 2 comparisons must also use the same train/validation/test splits, array geometry sets, corruption policy, SNR ranges, and evaluation metrics.

For every self-supervised objective, the report must state:

- exact input view and target view;
- whether the target is raw signal, latent, clustered unit, teacher embedding, acoustic map, phase/delay target, or auxiliary diagnostic target;
- whether target generation uses only unlabeled observations or uses BELLHOP/DOA/environment metadata;
- augmentations and corruptions applied to each view;
- collapse diagnostics;
- downstream head-only probe result;
- label-efficiency result under matched label budgets;
- held-out geometry and held-out BELLHOP environment result.

### Experiment Family 3: Geometry Conditioning Study

Compare:

- no geometry input;
- sensor-coordinate embeddings;
- pairwise geometry features;
- geometry-aware pairwise Transformer;
- graph-based array encoder;
- GNN / relation network over hydrophones;
- Neural-SRP / steering-aware branch;
- steering-aware conditioning;
- adapter-based geometry tuning.

Goal: evaluate whether geometry conditioning improves transfer to new hydrophone arrays.

The geometry-conditioning study must use held-out geometry splits and should include:

- ULA to square or rectangular transfer;
- square or rectangular to changed-spacing transfer;
- held-out topology transfer;
- changed-aperture transfer;
- missing-sensor and subarray inference.

All geometry-conditioning comparisons should use the same Stage 2 pretraining objective, same train/validation/test split policy, same BELLHOP environment split, same SNR ranges, and same downstream metrics.

### Experiment Family 4: Latent Dynamics Study

Compare:

- no dynamics;
- temporal pooling;
- temporal attention pooling;
- recurrent temporal modeling;
- temporal convolution over scene latents;
- one-step latent prediction;
- multi-horizon latent prediction;
- JEPA-style teacher-student scene-latent prediction.

Goal: test whether predictive latent dynamics adds value beyond simpler temporal modeling.

This experiment family should be separated into three regimes:

1. **Static-source stabilization**  
   Test whether Stage 3 reduces latent and DOA jitter without suppressing valid signal evidence.

2. **Moving-source prediction**  
   Test whether Stage 3 predicts smooth scene-latent evolution for moving or changing source conditions. This claim requires simulated or real moving-source data.

3. **Event-aware temporal modeling**  
   Test whether Stage 3 preserves source onset, offset, intermittent activity, and impulsive transients.

Required comparisons:

- Stage 1 + Stage 2 only;
- Stage 1 + Stage 2 + temporal pooling;
- Stage 1 + Stage 2 + small TCN or GRU over scene latents;
- Stage 1 + Stage 2 + JEPA-style scene-latent dynamics.

Metrics should be reported separately for static sources, moving sources when available, intermittent sources, impulsive transients, varying SNR, missing windows, corrupted windows, BELLHOP environment, and array geometry.

### Experiment Family 5: Noise and Interference Robustness

Compare:

- clean BELLHOP-propagated target signals;
- BELLHOP target signals with synthetic noise;
- BELLHOP target signals with BELLHOP-propagated acoustic interferers;
- BELLHOP target signals with sensor-level noise;
- BELLHOP target signals with narrowband tonal interference;
- BELLHOP target signals with real recorded noise augmentation.

Goal: test whether the learned representation uses DOA-relevant array and geometry structure rather than memorizing noise signatures, tonal frequencies, or clean-simulation artifacts.

This experiment family should include:

- seen and unseen noise recordings;
- seen and unseen tonal frequencies;
- seen and unseen interferer directions;
- seen and unseen SNR or SIR ranges;
- held-out BELLHOP environments;
- held-out array geometries when evaluating geometry transfer.

Metrics should be reported separately by SNR, SIR, noise type, real-noise source, tonal frequency, tonal bandwidth, interferer DOA, angular target-interferer separation, BELLHOP environment, and array geometry.

### Experiment Family 6: Head Study

Compare:

- DOA regression;
- angular probability-map estimation;
- source presence detection;
- combined multi-head training.

Goal: evaluate whether a shared backbone can support multiple tasks and whether Stage 4 adaptation improves downstream performance without destroying transfer.

The head study should compare the following Stage 4 training modes under the same data splits and metrics:

- head-only probing;
- head-only nonlinear fine-tuning;
- adapter tuning;
- partial fine-tuning;
- gradual unfreezing, when used;
- calibration-only tuning for probabilistic outputs;
- full end-to-end fine-tuning as an upper-bound baseline.

For each head, the protocol should specify the loss function, trainable parameters, frozen backbone stages, labeled-data budget, and whether unlabeled data are used through semi-supervised fine-tuning.

### Experiment Family 7: BELLHOP-to-Real Transfer

When real recordings are available, compare performance across:

- clean controlled synthetic source signals;
- BELLHOP-propagated hydroacoustic simulations;
- domain-randomized BELLHOP simulations;
- real-noise-augmented BELLHOP simulations;
- real hydroacoustic recordings.

Goal: measure the gap between controlled source signals, BELLHOP-based propagation, and real hydroacoustic recordings. This experiment should determine whether the learned representation transfers from physically motivated simulation to real data.

If real recordings are not yet available, this experiment family should be split into two stages:

1. **BELLHOP-domain transfer**  
   Compare clean synthetic signals, nominal BELLHOP simulations, and domain-randomized BELLHOP simulations across held-out environments and array geometries.

2. **BELLHOP-to-real transfer**  
   Run only after real hydroacoustic recordings and DOA ground truth are available.

### Experiment Family 8: Label Efficiency

Evaluate downstream performance using different fractions of labeled data:

- 1%;
- 5%;
- 10%;
- 25%;
- 50%;
- 100%.

Goal: test whether self-supervised pretraining reduces the need for labeled DOA data.

The label-efficiency study should compare:

- supervised training from scratch;
- SSL-pretrained head-only probing;
- SSL-pretrained adapter tuning;
- SSL-pretrained partial fine-tuning;
- SSL-pretrained semi-supervised fine-tuning, when unlabeled data are available;
- full end-to-end fine-tuning as an upper bound.

All label-efficiency comparisons should use the same train/validation/test splits, BELLHOP environment split, array-geometry split, noise and interference settings, and evaluation metrics. Results should be reported across SNR, SIR, signal family, BELLHOP environment, array geometry, Novik target benchmark when available, real-noise augmentation, and later real recordings when available.

---

## 19. Reproducibility Requirements

Concrete experiments must provide:

- dataset generation scripts;
- BELLHOP environment files and simulator version;
- BELLHOP-generated arrival or impulse-response metadata;
- preprocessing configuration;
- original and target sampling-rate metadata;
- useful-band selection and retained-band configuration;
- anti-alias filter design;
- downconversion or basebanding policy;
- decimation or resampling method;
- group-delay compensation policy;
- chunking policy;
- representation grid configuration for IQ, STFT, or CWT;
- normalization scope and reference;
- train-split normalization statistics;
- STFT dB reference and clipping policy, when STFT is used;
- phase representation policy;
- per-array versus per-channel normalization policy;
- model configuration;
- training configuration;
- Stage 4 adaptation mode and trainable parameter groups;
- frozen and unfrozen backbone stages;
- adapter configuration, when adapters are used;
- downstream head configuration;
- supervised, semi-supervised, or calibration-only loss configuration;
- multi-task loss weights, when multi-task training is used;
- labeled-data budget used for fine-tuning;
- random seeds;
- train/validation/test split definitions;
- real-noise recording metadata and split definitions, when real-noise augmentation is used;
- synthetic interference configuration, when interference augmentation is used;
- in-band and full-band SNR definition and scaling policy;
- normalization statistics policy;
- hardware information;
- number of runs;
- confidence intervals or standard deviations;
- primary, secondary, and diagnostic metric definitions;
- claim-to-evidence status table;
- stratified reporting tables;
- failure-case reporting;
- baseline parameter settings;
- model checkpoints, when possible;
- evaluation scripts.

For real-time or edge-computer-oriented experiments, reports should additionally provide:

- model parameter count;
- memory footprint;
- inference latency;
- throughput for the target input window size;
- target hardware description;
- whether the reported timing includes preprocessing.

The framework should prefer configuration-driven experiments, for example using YAML or another structured configuration format.

---

## 20. Experiment-Level Protocol Skeleton

Every concrete experiment should be defined by an experiment-level protocol before results are interpreted as reproducible evidence. The protocol should be configuration-driven and should state which parameters are fixed, randomized, held out, or still unresolved.

The protocol must include the following blocks.

### 20.1 Task Definition

The protocol must specify:

- DOA target type, such as 1D azimuth or azimuth/elevation;
- far-field or near-field assumption;
- source presence policy;
- static, moving, intermittent, or event-like source state;
- whether the experiment is simulation-stage, real-recording-stage, or mixed.

### 20.2 Array Configuration

The protocol must specify:

- number of hydrophones;
- hydrophone coordinates;
- array geometry family;
- aperture;
- spacing;
- calibration assumptions;
- synchronization assumptions;
- held-out geometry policy;
- permutation canary test result (9.3a), required before any Stage 2 or downstream result from this protocol is reported.

### 20.3 Signal and Input Configuration

The protocol must specify:

- IQ, STFT, or CWT input branch;
- original sampling rate;
- target sampling rate;
- resampling mode;
- anti-alias filter;
- baseband or downconversion policy;
- operating frequency range;
- useful signal band used for SNR calculation;
- signal families;
- chunk duration;
- chunk hop;
- overlap ratio;
- chunk timestamp convention;
- STFT or CWT physical grid parameters, when used;
- window duration and overlap;
- normalization policy;
- representation-specific normalization;
- array-level normalization policy;
- STFT or CWT log, power, or dB scaling policy;
- phase encoding policy;
- representation-specific parameters.

### 20.4 BELLHOP Configuration

The protocol must specify:

- sound-speed profile;
- bathymetry;
- bottom properties;
- surface assumptions;
- source depth;
- receiver depth;
- range grid;
- operating frequency range;
- hydrophone coordinates;
- propagation output type;
- arrival or impulse-response construction;
- BELLHOP run mode, such as arrivals, eigenrays, coherent TL, incoherent TL, or semicoherent TL;
- ray or beam convergence check, including beam count and step-size policy;
- arrivals-to-impulse-response construction policy, when arrivals are used;
- per-hydrophone phase, delay, amplitude, and multipath preservation check;
- number of independent environments;
- environment split policy.

### 20.5 Noise and Interference Configuration

The protocol must specify:

- synthetic noise types;
- real-noise augmentation policy;
- SNR and SIR policy;
- in-band and full-band SNR scaling;
- narrowband interference generation;
- acoustic interferer versus sensor-level noise;
- held-out noise recording policy;
- held-out interference condition policy.

### 20.6 Dataset and Split Configuration

The protocol must specify:

- train/validation/test split units;
- held-out BELLHOP environments;
- held-out array geometries;
- held-out signal families or parameter ranges, when used;
- held-out noise recordings;
- held-out source trajectories, when used;
- leakage-audit policy.

### 20.7 Model and Stage Configuration

The protocol must specify:

- Stage 1 encoder;
- Stage 2 geometry-conditioned array encoder;
- Stage 3 dynamics module, if used;
- Stage 4 heads and adaptation mode;
- frozen and trainable components;
- SSL objectives;
- supervised losses;
- training schedule.

### 20.8 Baseline Configuration

The protocol must specify:

- classical baselines;
- neural baselines;
- matched-field processing baselines, when used;
- handcrafted-feature baselines, when used;
- applicability assumptions for conditional baselines;
- whether any baseline uses privileged environmental information.

### 20.9 Evaluation and Reporting Configuration

The protocol must specify:

- primary, secondary, and diagnostic metrics;
- stratified reporting dimensions;
- claim-to-evidence mapping;
- reporting tables;
- number of runs;
- random seeds;
- confidence intervals or standard deviations;
- failure-case reporting.

### 20.10 Compute and Artifact Configuration

The protocol must specify:

- hardware;
- model parameter count;
- preprocessing cost;
- inference latency measurement policy;
- throughput measurement policy;
- saved configurations;
- generated dataset manifests;
- model checkpoints, when possible;
- evaluation scripts.

### 20.11 Minimal v1 Protocol Recommendation

The first executable protocol should be:

- BELLHOP-only;
- simulation-stage only;
- far-field 1D azimuth;
- 4-8 hydrophones in simple ULA, square, or rectangular arrays;
- six core synthetic signal families;
- domain-randomized shallow-water BELLHOP environments;
- explicit count of training, validation, and held-out BELLHOP environments;
- BELLHOP arrivals or impulse-response construction per hydrophone;
- ray/beam convergence and phase/delay preservation checks;
- permutation canary before Stage 2 or downstream reporting;
- no-geometry and supervised-from-scratch baselines;
- MVDR / Capon, MUSIC, SRP-PHAT or GCC-TDOA classical baselines;
- optional real-noise augmentation if real noise recordings exist;
- Stage 1 + Stage 2 + Stage 4 as the first full model path;
- Stage 3 evaluated only after the static Stage 1 + Stage 2 + Stage 4 baseline is stable.

### 20.12 Protocol Validity Rules

A result should not be treated as reproducible unless the experiment-level protocol defines all required blocks or explicitly marks unresolved placeholders.

The protocol must separate simulation-stage claims from real-data claims. A BELLHOP-only protocol may support simulation-stage conclusions but cannot support real-world hydroacoustic performance claims.

The protocol must state whether each baseline uses only ordinary experiment information or privileged BELLHOP, environmental, or oracle information.

---
