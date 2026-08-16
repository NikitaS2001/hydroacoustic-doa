# Data, Simulation, And Hydroacoustic Validation

> This file covers synthetic data, BELLHOP, Novik Bay assumptions, noise/interference, real data, and validation philosophy.

## 15. Data Strategy

### 15.1 Data Levels

The framework should support several data levels:

1. **Controlled synthetic signals**  
   A limited but diverse set of synthetic signal families used for debugging, controlled ablation, representation comparison, and baseline evaluation.

2. **BELLHOP-based hydroacoustic scenes**  
   Controlled signals propagated through underwater acoustic channels generated with BELLHOP.

3. **Domain-randomized BELLHOP simulations**  
   Simulations with randomized environmental conditions and nested source, receiver, channel, waveform, geometry, and post-hoc overlay draws.

4. **Real unlabeled hydroacoustic recordings**  
   Used for self-supervised pretraining and representation learning when such recordings become available. Real recordings are not assumed to be available during the initial BELLHOP-only stage.

5. **Real labeled hydroacoustic subsets**  
   Used for validation, fine-tuning, or final evaluation when DOA ground truth becomes available. Until then, real-data claims must be deferred.

### 15.2 Core Synthetic Signal Families

The framework should not rely on a single synthetic signal type such as a chirp. Chirp signals are useful for controlled time-frequency analysis, but they are not sufficient for validating a general hydroacoustic representation model.

The initial framework should use the following six core synthetic signal families:

1. **Continuous-wave signals (CW)**  
   Narrowband stationary signals used to evaluate phase sensitivity, narrowband DOA behavior, and spatial aliasing effects.

2. **Linear chirps (LFM)**  
   Frequency-modulated signals with a linear time-frequency trajectory. These signals are useful for controlled nonstationary experiments and for comparing IQ, STFT, and CWT input representations.

3. **Nonlinear chirps (NLFM)**  
   Frequency-modulated signals with nonlinear time-frequency trajectories. These signals test whether the model can generalize beyond simple linear chirp patterns.

4. **Broadband pulses**  
   Short broadband signals used to evaluate time-delay sensitivity, broadband DOA estimation, and robustness to short-duration source events.

5. **Impulsive transients**  
   Very short, high-energy events used to test the model's ability to detect and represent transient acoustic phenomena.

6. **Band-limited noise bursts**  
   Stochastic source-like signals constrained to a specific frequency band. These signals help reduce the risk that the model learns deterministic waveform artifacts instead of array-related structure.

Chirp signals should therefore be treated as one part of the controlled signal set, not as the dominant or exclusive synthetic signal family.

The signal-family split should also support out-of-distribution evaluation. For example, some signal parameter ranges or complete signal families may be held out during training and used only for validation or testing.

### 15.3 BELLHOP-Based Hydroacoustic Propagation

In the baseline scenario, the six core synthetic signal families should be propagated through hydroacoustic channels generated with BELLHOP.

The BELLHOP strategy should distinguish three levels:

1. **Training distribution**  
   A broad set of domain-randomized BELLHOP environments used for supervised Tier-0 training, optional Tier-1 pretraining, ablation, and simulation-stage evaluation.

2. **Target benchmark**  
   A Novik Bay / Russky Island BELLHOP scenario used as a deployment-motivated benchmark once local environmental assumptions become available.

3. **Real validation**  
   Real Novik Bay or comparable hydroacoustic recordings used for final validation once recordings and DOA ground truth become available.

The initial training distribution should not be tightly tuned only to Novik Bay. A model trained and evaluated only on one Novik-like BELLHOP configuration would risk becoming a simulator-specific model rather than a geometry-conditioned hydroacoustic DOA representation framework. Novik Bay should therefore be treated as a target scenario and later benchmark, not as the only physical environment represented during training.

Until exact Novik Bay parameters are known, the Novik Bay BELLHOP setup should remain a configurable target-scenario placeholder rather than a fixed benchmark. The broader BELLHOP training distribution should remain configurable and should cover multiple physically plausible shallow-water environments.

The role of BELLHOP is to provide a physically motivated propagation layer between the clean source signal and the multi-channel hydrophone array observation.

A BELLHOP-based simulation protocol should specify:

- sound-speed profile;
- source depth;
- receiver depth;
- source-receiver range;
- bathymetry;
- bottom acoustic parameters;
- surface assumptions;
- operating frequency range;
- number and coordinates of hydrophones;
- propagation mode used for data generation;
- arrival structure or impulse-response construction;
- SNR and additive noise model;
- source state, including static, moving, intermittent, or event-like scenarios when used;
- source trajectory generation policy, when trajectories are used;
- number of independent environments;
- train/validation/test environment split.

The BELLHOP output should provide propagation information sufficient to construct received signals independently for each hydrophone. The preferred protocol should construct per-hydrophone arrivals or impulse responses and convolve controlled source signals with those channels. The resulting multi-channel observations must preserve inter-sensor delay, phase, amplitude, and multipath differences required for DOA estimation.

The BELLHOP training distribution should support randomized variation of:

- sound-speed profiles;
- source depth;
- receiver depth;
- source-receiver range;
- bathymetry;
- bottom acoustic parameters;
- surface assumptions;
- operating frequency band;
- nested post-hoc ordinary-noise/SNR overlays;
- array geometry;
- sensor availability and bounded sensor perturbations;
- source signal family and source-motion condition.

For the current MVP, these factors are not one joint sampling design. The six-factor environment LHS contains only the protocol-defined SSP/water/bottom factors. All source, receiver, geometry-specific channel, waveform, and overlay variables are separate nested draws or assignments within an environment.

The target Novik Bay BELLHOP benchmark should be kept separate from the broad randomized training distribution whenever possible. If Novik-like environments are included in training, the protocol must explicitly state this and must still include held-out environments that differ in environmental configuration, array geometry, and source conditions.

The Novik Bay benchmark must remain a configurable target-scenario placeholder until the experiment-level protocol specifies:

- bathymetry source and spatial resolution;
- sound-speed profile source, season, and depth coverage;
- bottom type and acoustic parameters;
- surface and ice assumptions;
- source and receiver depth ranges;
- source range assumptions and source-motion policy;
- whether far-field 1D azimuth is valid for the selected array aperture, operating band, and source ranges;
- whether the benchmark is used only for evaluation or also influences training/model selection.

For the initial BELLHOP-only phase, the protocol must clearly state that results are simulation-stage results. If real recordings are unavailable, the protocol should not report BELLHOP-to-real transfer as completed.

BELLHOP simulation should be treated as the main physically grounded development environment, but it should not be treated as final proof of real-world performance. Final validation must still be performed on real hydroacoustic recordings.

### 15.4 Noise and Narrowband Interference Robustness Protocol

Noise and interference should be treated as part of the data-generation protocol, not as an incidental augmentation detail. The goal is to train representations that preserve DOA-relevant inter-channel structure under realistic and out-of-distribution acoustic corruption.

The noise and interference taxonomy should include:

- white noise;
- colored noise;
- ambient sea noise;
- shipping-like low-frequency noise;
- wind- or wave-like noise;
- sensor self-noise;
- impulsive noise;
- narrowband tonal interference;
- harmonic interference;
- drifting tonal interference;
- intermittent narrowband interference.

The experiment-level protocol must specify the parameter ranges used for each noise or interference type, including SNR, signal-to-interference ratio, bandwidth, center frequency, duration, stationarity, and intermittency when applicable.

SNR should be defined in the useful signal band, not only over the full sampled bandwidth. For broadband or out-of-band noise, the protocol should compute the desired SNR over the occupied signal band and then scale the noise consistently over the full processed bandwidth. Reports must state whether SNR is in-band, full-band, or both.

The current MVP freezes reusable **clean** multichannel BELLHOP channels. Ordinary sensor noise and synthesized tonal contamination are deterministic post-hoc overlays, so neither SNR cells nor ordinary overlay identities multiply the clean channel bank. A coherent acoustic interferer is the exception: it is propagated as a separate BELLHOP channel before target/interferer mixing (this bank is Tier-1-deferred in the Tier-0 MVP). Frozen cells are clean `+inf`; Tier-0 noise strata are white SNR `{20,10,0}` (primary, every split) plus colored `1/f` SNR `{20,10,0}` and `1/f²` SNR `{20,10}` (secondary, every split), with white stress `-5` dev-test only; incoherent-tonal and coherent-acoustic interference cells are Tier-1-deferred. Primary source draws use family-specific `500-1400 Hz` support constraints and must pass the exact finite, positive per-sensor projected-clean-power manifest check before any output or sealed access. Manifests preserve the canonical `500-3000 Hz` base-overlay scalar and achieved/full-band reports, then record separate array-wide scalars, exact DFT masks, eligibility, target/achieved levels, and replay identity for the `500-1400 Hz` primary and `(1400,3000] Hz` stress inference views; per-sensor scaling is forbidden.

Every derived example is replayed from its complete base-channel, source-waveform/profile/eligibility, overlay/interferer, crop, preprocessing, generator-version, canonical Random123 Philox namespace, and child-view projection/scalar record; a seed tuple alone is not sufficient provenance. The inference hierarchy is `environment -> channel config -> clean source realization -> overlay -> inference view`. Eligibility is frozen at the clean realization; views and overlays are repeated/nested measurements, not independent samples or replicates for power. Primary power and effective sample size count only complete eligible environments; ineligible rows are stress/source-presence only.

The future diagnostic pilot has not run. Solver/build, broadband convergence, runtime, allocation/power, exact overlay replay, and model gates are `not yet evaluated`; full generation remains blocked.

Noise sources should be separated into three categories:

1. **Acoustic interferers**  
   Additional acoustic sources propagated through BELLHOP with their own source positions, depths, trajectories, and DOA values. This category should be used when the interference has meaningful spatial structure.

2. **Sensor-level noise**  
   Channel corruption added after BELLHOP propagation, including sensor self-noise, gain degradation, partial channel contamination, and channel-specific narrowband pollution.

3. **Real recorded noise**  
   Noise recordings added to BELLHOP-propagated target observations to improve robustness to realistic ambient and operational conditions.

The preferred real-noise augmentation pipeline is:

```text
clean source signal
-> BELLHOP propagation to each hydrophone
-> multi-channel target observation
+ real recorded noise segment
-> noisy multi-channel training example
```

Multi-channel real noise is preferred when available because it can preserve spatial coherence, inter-channel correlation, array-specific noise structure, and coherent external interference. Single-channel real noise may be used as an approximation, but the protocol must mark it as less physically faithful and must state how it is replicated, randomized, or decorrelated across channels.

Recorded-noise overlays are robustness training, not validation on real recordings. They can reduce the gap between clean BELLHOP simulation and real recordings, but final validation still requires real hydroacoustic data with appropriate evaluation metadata.

Training should use an SNR and SIR curriculum:

- clean or lightly corrupted examples for initial stability;
- moderate noise and moderate interference for standard training;
- low-SNR and strong-interference examples for robustness;
- out-of-distribution noise and interference settings for evaluation.

For narrowband interference, the protocol must specify:

- tonal frequency or frequency range;
- interference bandwidth;
- harmonic structure, when used;
- stationary, drifting, or intermittent behavior;
- signal-to-interference ratio;
- interferer DOA;
- angular separation between target and interferer;
- whether the interferer is BELLHOP-propagated or sensor-level.

Stage-specific use of noisy and interfered data should follow the stage contracts:

- **Tier 0** first trains the matched supervised Small models on the frozen clean/noise cells and evaluates downstream heads separately under clean, noisy, and interfered regimes.
- **Tier 1**, only under separate preregistration, may use noisy single-channel SSL, denoising prediction, array-level corrupted-student objectives, and SNR-dependent masking ablations.
- **Stage 3 predictive dynamics** remains deferred to a later protocol and is not part of the MVP data slate.

The core robustness test should hold out at least one major interference axis, such as unseen real-noise recordings, unseen tonal frequencies, unseen interferer directions, unseen SNR or SIR ranges, or held-out BELLHOP environments. A model that works only on seen tonal frequencies or seen noise recordings should not be considered robust.

### 15.5 Synthetic Data

Synthetic data may be used for:

- debugging;
- controlled ablation;
- pretraining;
- stress testing;
- controlled comparison of input representations and architectures.

However, performance on synthetic signals alone is not sufficient to validate hydroacoustic DOA performance.

The synthetic data generator should support controlled variation of:

- signal family;
- signal duration;
- center frequency;
- bandwidth;
- amplitude;
- SNR;
- source direction;
- source distance, if relevant;
- array geometry;
- BELLHOP channel/environment configuration;
- channel effects;
- noise type;
- interference type;
- SIR;
- interferer direction, when applicable.

### 15.6 Real Data

Real hydroacoustic data should be introduced as early as possible, but the initial research and training stage may be performed entirely on BELLHOP-generated data if real recordings are not yet available.

Possible uses:

- self-supervised pretraining;
- validation of learned representations;
- fine-tuning;
- final test;
- real-noise augmentation for BELLHOP-propagated simulations;
- synthetic-to-real transfer evaluation.

If real data is unavailable, the document and experiment reports must explicitly state:

- no real-recording validation has been performed;
- no real-world deployment claim is made;
- the next validation milestone is acquisition or access to real Novik Bay or comparable hydroacoustic recordings;
- future real-data protocols must define array geometry, sensor calibration, sampling rate, signal bandwidth, source types, source-receiver distances, DOA ground truth, and evaluation split.

### 15.7 Data Splitting Principles

Splits must be performed by independent scenes, not by overlapping windows.

Train, validation, and test sets should be separated by:

- scene identity;
- signal-family parameter ranges, when evaluating OOD generalization;
- source identity, when applicable;
- source trajectory, when applicable;
- noise recording;
- noise recording session;
- noise recording day or deployment;
- noise recording location;
- noise sensor setup;
- noise segment;
- channel impulse response;
- BELLHOP arrival set;
- simulation seed;
- tonal-interference generation seed;
- interferer trajectory, when applicable;
- environment configuration;
- sound-speed profile;
- bathymetry;
- bottom model;
- array geometry, when evaluating geometry transfer.

Augmented versions of the same source scene must not be split across train and test. Overlapping windows from the same real-noise recording must not be split across train, validation, and test sets.

Within a split, post-hoc overlays remain nested under their clean source realization. Statistical inference must average them within that realization or retain them as the lowest nested bootstrap level; it must never count overlays, source seeds, or model seeds as additional independent environments.

---

## 16. Hydroacoustic Validation Philosophy

The final target is validation on a hydroacoustic channel.

The initial validation stage may be limited to BELLHOP-generated hydroacoustic data. This is acceptable for framework development, ablation, and simulation-stage comparison, but it is not sufficient for a final real-world claim.

BELLHOP-stage validation should include both broad held-out randomized environments and, when parameters become available, a separate Novik Bay / Russky Island target benchmark. The Novik Bay benchmark should not replace held-out randomized environments, because the framework claims require robustness beyond a single target configuration.

A valid evaluation should answer the following questions:

1. Does the learned representation improve DOA performance under hydroacoustic conditions?
2. Does self-supervised pretraining reduce the need for labeled DOA data?
3. Does geometry conditioning improve adaptation to new arrays?
4. Does the predictive latent module improve robustness or temporal consistency?
5. Does the model outperform or complement classical DOA baselines?
6. Does the model generalize beyond the synthetic signal families used during development?
7. When real recordings become available, does performance transfer from BELLHOP-based simulation to real hydroacoustic recordings?

### 16.1 Placeholder for Hydroacoustic Validation Setup

The concrete hydroacoustic validation setup must be defined later.

At minimum, the experiment-level protocol should specify the BELLHOP simulation setup. If real recordings are not yet available, the protocol must explicitly mark the real-recording validation setup as future work rather than leaving it ambiguous.

For the BELLHOP stage, the protocol should specify:

- sound-speed profile;
- bathymetry;
- bottom properties;
- source and receiver depths;
- source-receiver ranges;
- propagation output used to construct received signals;
- array geometry;
- source state and trajectory policy, when temporal dynamics are evaluated;
- simulation split by environment.

For the real-recording stage, the protocol should specify:

- recording environment;
- array geometry;
- sensor calibration;
- sampling rate;
- signal bandwidth;
- source types;
- source-receiver distances;
- DOA ground truth;
- noise and reverberation conditions;
- evaluation split;
- baseline configuration.

For the initial BELLHOP-only stage, the validation report should include a limitation statement explaining that the evaluation is simulation-based and that real-data validation remains unresolved. If a Novik Bay BELLHOP benchmark is reported, the report must state whether Novik-like environments were included in training and must report separate results for randomized held-out environments and the Novik target benchmark.

---
