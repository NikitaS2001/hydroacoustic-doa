# BELLHOP MVP Experiment Protocol

## Status

This is the first numeric, executable experiment protocol for the geometry-conditioned hydroacoustic DOA framework. It is a **BELLHOP-only simulation-stage protocol**. Results from this protocol may support simulation-stage claims only and must not be reported as real-world Novik Bay performance.

Framework references:

- [Overview](../research/framework/overview.md)
- [Architecture](../research/framework/architecture.md)
- [Training And Adaptation Strategy](../research/framework/training_strategy.md)
- [Data, Simulation, And Hydroacoustic Validation](../research/framework/data_and_simulation.md)
- [Evaluation, Baselines, And Protocols](../research/framework/evaluation.md)
- [Risks And Validity Threats](../research/framework/risks.md)
- [Roadmap And Success Criteria](../research/framework/roadmap.md)

## 1. MVP Claim

The only positive claim this protocol may support is:

> In domain-randomized BELLHOP shallow-water simulation under matched information conditions, a Tier 0 geometry-conditioned model improves held-out simple-array transfer over a no-geometry model and remains competitive with strong classical baselines.

Out of scope for this protocol:

- real-world hydroacoustic performance;
- BELLHOP-to-real transfer;
- operational Novik Bay deployment;
- multi-source DOA;
- near-field localization;
- Stage 3 predictive latent dynamics;
- Tier 2 SSL objectives such as DINO/JEPA/wav2vec/HuBERT/Mamba.

## 2. Task Definition

| Field | Value |
|---|---|
| Stage | BELLHOP-only simulation |
| DOA target | Single-source 1D azimuth |
| Azimuth range | `[-90 deg, +90 deg]` broadside-relative |
| Train azimuth grid | `5 deg` spacing, 37 values |
| Test azimuth grid | `2.5 deg` spacing, 73 values |
| Source count | 1 target source |
| Source state | Static within one 2 s example |
| Receiver state | Static |
| Far-field assumption | Required; validate with Section 6.3 before dataset generation |
| Output heads | DOA regression and angular probability map |
| Source presence head | Diagnostic only: target-present vs noise/interference-only windows |

## 3. Array Configuration

All coordinates are in meters in an array-centered coordinate system. `x` is horizontal across the aperture, `y` is horizontal orthogonal to `x`, and `z = 0` for all sensors in this MVP.

### 3.1 Training Geometry: ULA-6

| Sensor | x | y | z |
|---:|---:|---:|---:|
| 0 | -0.625 | 0.000 | 0.000 |
| 1 | -0.375 | 0.000 | 0.000 |
| 2 | -0.125 | 0.000 | 0.000 |
| 3 | 0.125 | 0.000 | 0.000 |
| 4 | 0.375 | 0.000 | 0.000 |
| 5 | 0.625 | 0.000 | 0.000 |

Parameters:

- hydrophones: `6`;
- spacing: `0.25 m`;
- aperture: `1.25 m`;
- nominal sound speed for geometry checks: `1500 m/s`;
- minimum wavelength at 3000 Hz: `0.5 m`;
- spacing-to-wavelength ratio at 3000 Hz: `0.5`.

### 3.2 Validation Geometry: ULA-6-Shifted-Aperture

Same topology and sensor count as ULA-6, but spacing is `0.20 m` and aperture is `1.00 m`. This tests changed aperture without changed topology.

### 3.3 Held-Out Geometry A: Square-4

| Sensor | x | y | z |
|---:|---:|---:|---:|
| 0 | -0.375 | -0.375 | 0.000 |
| 1 | -0.375 | 0.375 | 0.000 |
| 2 | 0.375 | -0.375 | 0.000 |
| 3 | 0.375 | 0.375 | 0.000 |

Parameters:

- hydrophones: `4`;
- side length: `0.75 m`;
- maximum aperture: `1.061 m`;
- role: held-out topology transfer.

### 3.4 Held-Out Geometry B: Rect-6

| Sensor | x | y | z |
|---:|---:|---:|---:|
| 0 | -0.500 | -0.250 | 0.000 |
| 1 | 0.000 | -0.250 | 0.000 |
| 2 | 0.500 | -0.250 | 0.000 |
| 3 | -0.500 | 0.250 | 0.000 |
| 4 | 0.000 | 0.250 | 0.000 |
| 5 | 0.500 | 0.250 | 0.000 |

Parameters:

- hydrophones: `6`;
- maximum aperture: `1.118 m`;
- role: held-out topology transfer with same sensor count as ULA-6.

### 3.5 Sensor Perturbation Conditions

Sensor-coordinate perturbation is used only for robustness testing, not for the primary clean comparison.

| Condition | Coordinate noise | Gain error | Phase/sync error |
|---|---:|---:|---:|
| Clean | `0 mm` | `0 dB` | `0 us` |
| Calibration-lite | Gaussian `sigma = 5 mm`, clipped at `15 mm` | Uniform `[-0.5, 0.5] dB` | Uniform `[-10, 10] us` |
| Calibration-stress | Gaussian `sigma = 15 mm`, clipped at `40 mm` | Uniform `[-1.5, 1.5] dB` | Uniform `[-40, 40] us` |

Calibration-stress is diagnostic. It must not be used to support the main MVP claim.

## 4. Signal And Preprocessing Configuration

| Field | Value |
|---|---|
| Useful acoustic band | `500 Hz` to `3000 Hz` |
| Master simulation sample rate | `48000 Hz` |
| Future sound-card acquisition sample rate | `48000 Hz` |
| Model target sample rate | `12000 Hz` |
| Decimation factor | `4` after coherent anti-alias filtering |
| Anti-alias low-pass before decimation | FIR, passband `<= 3400 Hz`, transition band `3400-5400 Hz`, stopband `>= 5400 Hz` |
| Chunk duration | `2.0 s` |
| Chunk hop | `1.0 s` |
| Samples per chunk at acquisition rate | `96000` |
| Samples per chunk at model target rate | `24000` |
| Primary neural input | Analytic signal / IQ from band-limited real waveform |
| Secondary input | STFT real+imaginary channels |
| CWT | Excluded from MVP; future ablation only |

Sound-card policy:

- the real acquisition target is multichannel `48 kHz` PCM from a shared-clock audio interface;
- all hydrophone channels must be sampled by the same device clock with no independent per-channel resampling;
- preferred bit depth is `24-bit` PCM or float capture from the interface driver;
- automatic gain control, noise suppression, echo cancellation, and per-channel DSP must be disabled;
- raw captured files must preserve the acquisition sample rate and channel order in metadata;
- if a specific interface only supports `96 kHz` reliably, capture may use `96 kHz`, but the MVP model input still decimates coherently to `12 kHz` after the same useful-band filtering;
- `44.1 kHz` capture is not used for MVP training unless hardware forces it, because integer decimation to the `12 kHz` model rate is not clean.

STFT settings:

| Field | Value |
|---|---|
| Window | Hann |
| Window duration | `64 ms` |
| Window samples at 12000 Hz | `768` |
| Hop duration | `16 ms` |
| Hop samples at 12000 Hz | `192` |
| FFT size | `1024` |
| Retained band | `500 Hz` to `3000 Hz` |
| Phase representation | real and imaginary STFT channels |
| Magnitude-only STFT | Diagnostic baseline only |

Normalization:

- one shared RMS scale factor per multi-channel array chunk;
- statistics estimated on training split only;
- no independent per-channel RMS normalization;
- no per-frame max normalization;
- preserve phase, delay, and inter-channel amplitude ratios.

## 5. Synthetic Source Families

Each family must produce examples across the full train azimuth grid and all train BELLHOP environments.

All synthetic source waveforms are generated at the `48000 Hz` master rate before BELLHOP propagation. Unless a family states otherwise:

- waveform duration is embedded in a `2.0 s` chunk;
- active source onset is sampled uniformly from `0.10-0.30 s`;
- active source offset must leave at least `0.10 s` trailing context;
- amplitude is peak-normalized to `-6 dBFS` before propagation and then randomly scaled by `[-6, +3] dB`;
- start phase is sampled uniformly from `[0, 2*pi)`;
- onset and offset use a Tukey or raised-cosine ramp of `10-25 ms`;
- no generated waveform may clip before or after propagation.

| Family | Count weight | Numeric parameters |
|---|---:|---|
| CW | `1.0` | carrier sampled uniformly from `500-3000 Hz`; duration `2.0 s` |
| LFM chirp | `1.0` | start/end in `500-3000 Hz`; bandwidth `500-2000 Hz`; duration `0.5-2.0 s` |
| NLFM chirp | `1.0` | start/end in `500-3000 Hz`; polynomial order `2` or `3` |
| Broadband pulse | `1.0` | center `1000-2500 Hz`; bandwidth `500-1500 Hz`; pulse length `50-250 ms` |
| Impulsive transient | `0.5` | length `10-80 ms`; tapered with Tukey window `alpha = 0.25` |
| Band-limited noise burst | `1.0` | band within `500-3000 Hz`; burst length `0.25-2.0 s` |

OOD source-family test:

- hold out `20%` of parameter ranges per family for OOD evaluation;
- additionally run one complete-family holdout where NLFM is excluded from training and included only in test.

## 6. BELLHOP Environment Configuration

### 6.1 Environment Counts

| Split | Independent environments | Role |
|---|---:|---|
| Train | `32` | model training and train-split normalization |
| Validation | `8` | model selection and early stopping |
| Randomized test | `12` | primary held-out environment result |
| Novik-like target placeholder | `1` | diagnostic target benchmark only |

Environment-generalization claims must report mean, standard deviation, minimum, maximum, and per-environment results across the `12` randomized test environments. If fewer than `10` randomized test environments are successfully generated, environment-generalization claims are preliminary only.

### 6.2 Randomized Shallow-Water Parameter Ranges

| Parameter | Train range | Validation/test policy |
|---|---:|---|
| Water depth | `15-60 m` | held-out values sampled independently |
| Source depth | `3-20 m` and at least `3 m` above bottom | independent |
| Receiver depth | `3-20 m` and at least `3 m` above bottom | independent |
| Source range | `50-1000 m` | test includes `50-1200 m` |
| Sound speed at surface | `1460-1530 m/s` | independent |
| Linear SSP gradient | `[-0.05, +0.05] (m/s)/m` | independent |
| Bottom compressional speed | `1450-1800 m/s` | independent |
| Bottom density | `1.3-2.0 g/cm^3` | independent |
| Bottom attenuation | `0.1-1.0 dB/lambda` | independent |
| Surface | pressure-release flat surface | same |
| Bathymetry | range-independent flat bottom for MVP | same |

The MVP intentionally uses range-independent flat-bottom environments to keep the first protocol executable. Range-dependent bathymetry and seasonal Novik Bay SSP are future protocol extensions.

### 6.3 Far-Field Validity Gate

Before generating a dataset for a geometry/source-range combination:

```text
R_min >= max(10 * aperture, 2 * aperture^2 / lambda_min)
```

where:

- `aperture` is the maximum sensor-to-sensor distance for the geometry;
- `lambda_min = c / f_max`;
- `c = 1500 m/s`;
- `f_max = 3000 Hz`;
- `lambda_min = 0.5 m`.

For ULA-6:

```text
max(10 * 1.25, 2 * 1.25^2 / 0.5) = max(12.5, 6.25) = 12.5 m
```

The protocol uses `R_min = 50 m`, so the MVP far-field gate passes for all specified arrays. If later arrays use larger apertures or higher frequency bands, this calculation must be repeated.

### 6.4 BELLHOP Run Mode And Outputs

Primary generation mode:

- BELLHOP mode: arrivals;
- per-hydrophone arrivals generated independently using the physical hydrophone coordinates;
- impulse response sampling rate: `48000 Hz`;
- impulse response duration: `2.5 s`;
- maximum arrival delay retained: `2.0 s`;
- arrivals below `-60 dB` relative to strongest arrival may be discarded after metadata logging;
- controlled source waveform convolved with per-hydrophone impulse responses.

Sanity and convergence checks:

| Check | Requirement |
|---|---|
| Ray fan convergence | run with `N_beams = 2001` and `4001`; primary DOA metrics may proceed only if median arrival delay difference is `< 0.25 ms` and relative received-energy difference is `< 1 dB` on a 5-environment sample |
| Arrival ordering | first-arrival delay must be finite for every hydrophone |
| Inter-sensor TDOA bound | absolute direct-path delay difference must be `<= aperture / 1450 m/s + 0.25 ms` |
| Phase/delay preservation | synthetic direct-path-only diagnostic must recover expected TDOA within `0.25 ms` |
| Metadata completeness | every example stores environment id, array id, hydrophone coordinates, source depth/range/azimuth, SSP parameters, bottom parameters, SNR/SIR, seed, and BELLHOP run config |

## 7. Noise And Interference

Primary SNR values are in-band SNR over `500-3000 Hz`.

| Condition | Values | Split policy |
|---|---|---|
| Clean | no additive noise | all splits |
| White noise | SNR `{20, 10, 0, -5} dB` | all splits |
| Colored noise | `1/f` and `1/f^2`; SNR `{20, 10, 0} dB` | all splits |
| Narrowband tonal interference | SIR `{20, 10, 0} dB`; tone frequency `700-2800 Hz` | train/val/test use disjoint tone-frequency bins |
| Acoustic interferer | one BELLHOP-propagated interferer, angular separation `{15, 30, 60} deg`, SIR `{20, 10, 0} dB` | diagnostic only in MVP |

Real-noise augmentation:

- excluded from the primary MVP because no real-noise corpus is assumed available;
- if introduced, it must be reported as augmentation only, never as real-world validation.

## 8. Dataset Size And Split Units

Split units are independent environments and simulation seeds, not overlapping windows.

Counting convention:

- one **array example** is one physical scene rendered as a synchronized multi-channel hydrophone chunk for one array geometry;
- `~120,000 / ~24,000 / ~48,000` are counts of array examples, not counts per azimuth-grid element and not counts of single-channel clips;
- for an array with `N` hydrophones, one array example yields `N` single-channel views for Stage 1 SSL;
- ULA-6 therefore yields up to `~720,000` Stage 1 single-channel views from `~120,000` train array examples before masking/cropping augmentation;
- Square-4 yields `4` Stage 1 views per array example, Rect-6 yields `6`;
- Stage 2 and Stage 4 consume array examples, not independent channel views;
- DOA labels are attached to array examples and are hidden from Stage 1/2 SSL pretraining unless a diagnostic probe explicitly uses labels.

Primary balanced dataset target:

| Split | Approx examples | Construction |
|---|---:|---|
| Train | `~120,000` | 32 environments x train geometries x source families x azimuths x SNR/noise seeds |
| Validation | `~24,000` | 8 environments x ULA-6 + ULA-6-shifted x matched source/noise coverage |
| Randomized test | `~48,000` | 12 environments x all geometries x denser azimuth grid x held-out source parameters |
| Novik-like placeholder | `~4,000` | one diagnostic environment, no model selection |

Leakage rules:

- no BELLHOP environment appears in more than one split;
- no source waveform seed appears in more than one split;
- no noise or interference seed appears in more than one split;
- augmented views of the same physical scene remain in the same split;
- validation/test normalization uses train-split statistics only.

### 8.1 Channel Bank And BellhopCUDA Runtime Budget

The final `~120,000 / ~24,000 / ~48,000` array examples must not be implemented as one independent BELLHOP/BellhopCUDA run per final example. BELLHOP is used to generate a **channel**, not every source/noise variant. A channel is defined by:

```text
environment_id
+ array_geometry_id
+ source_range
+ source_depth
+ receiver_depth
+ azimuth
+ hydrophone_coordinates
+ BELLHOP run configuration
```

The generated channel or per-hydrophone impulse responses may then be reused across several source waveforms, source-family parameter draws, and noise/SNR variants. This is required to keep the MVP computationally feasible.

Recommended channel-bank target:

| Split | Final array examples | Unique BELLHOP channel configs | Reuse factor |
|---|---:|---:|---:|
| Train | `~120,000` | `10,000-20,000` | `6-12` examples per channel |
| Validation | `~24,000` | `2,000-4,000` | `6-12` examples per channel |
| Randomized test | `~48,000` | `5,000-10,000` | `4-10` examples per channel |
| Novik-like placeholder | `~4,000` | `500-1,000` | `4-8` examples per channel |

Total planned BellhopCUDA channel runs:

```text
low  = 10,000 + 2,000 + 5,000 + 500   = 17,500
high = 20,000 + 4,000 + 10,000 + 1,000 = 35,000
```

Naive no-reuse upper bound:

```text
120,000 + 24,000 + 48,000 + 4,000 = 196,000 BellhopCUDA runs
```

The no-reuse upper bound is not the intended implementation. If the implementation requires close to `196,000` BellhopCUDA runs, reduce the final dataset size or increase channel reuse before training.

BellhopCUDA public performance notes do not provide a single absolute runtime that applies to this protocol. They report that CUDA speedups depend on ray count, receiver layout, run type, precision, and file I/O. The BellhopCUDA README reports typical speedups of about `10x-50x` on consumer GPUs such as RTX 3060 and `20x-100x` on server GPUs such as A100 for large runs with few receivers, while the performance notes warn that arrivals runs and receiver layout can reduce speedup and that file I/O can dominate runtime.

Therefore, this protocol requires a local pilot benchmark before freezing the channel-bank size.

Pilot benchmark:

| Step | Requirement |
|---|---|
| Sample size | `100` representative channel configs |
| Coverage | include all train geometries, all held-out geometries, `5` BELLHOP environments, near/far range bins, shallow/deep source depths |
| Runs per config | one `N_beams = 2001` run and one `N_beams = 4001` convergence run |
| Timing metrics | median, p90, p95, max wall time per run; separate compute time from file I/O if possible |
| Hardware report | GPU model, CUDA version, BellhopCUDA commit/tag, precision mode, CPU, RAM, storage type |
| Freeze rule | choose final channel-bank size only after p95 runtime is known |

Runtime estimate formula:

```text
T_total_seconds = N_channel_configs * T_p95_seconds_per_config * convergence_multiplier + T_io
```

Use `convergence_multiplier = 2` if both `2001` and `4001` beam runs are required for every generated channel. Use `convergence_multiplier = 1.1-1.3` only if the full convergence check is run on a representative subset and routine generation uses the chosen beam count.

Planning table excluding file I/O:

| Unique channel configs | `0.2 s/run` | `1 s/run` | `5 s/run` |
|---:|---:|---:|---:|
| `17,500` | `0.97 h` | `4.86 h` | `24.3 h` |
| `35,000` | `1.94 h` | `9.72 h` | `48.6 h` |
| `196,000` no-reuse bound | `10.9 h` | `54.4 h` | `272 h` / `11.3 days` |

If p95 runtime exceeds `5 s` per channel on the available GPU, the MVP should start with a smaller pilot dataset:

| Split | Final array examples | Unique channel configs |
|---|---:|---:|
| Train pilot | `~24,000` | `2,000-4,000` |
| Validation pilot | `~6,000` | `500-1,000` |
| Test pilot | `~12,000` | `1,000-2,000` |

The full `120k/24k/48k` dataset should be generated only after the pilot benchmark and pilot training confirm that the channel bank is computationally affordable and scientifically useful.

## 9. Models Under Test

Tier 0 only:

1. **No-geometry supervised neural baseline**
   - input: multi-channel IQ or STFT tensor;
   - no sensor-coordinate input;
   - architecture: compact TCN or CRNN;
   - purpose: test whether geometry metadata matters.

2. **Geometry-conditioned pairwise Transformer**
   - input: per-channel encoder outputs plus sensor coordinates and pairwise geometry features;
   - no learned slot-index embeddings;
   - sensor availability mask required;
   - primary proposed model for MVP.

3. **Geometry-conditioned GNN / relation network**
   - same inputs as pairwise Transformer;
   - complete graph over hydrophones;
   - permutation-invariant graph readout;
   - secondary proposed model.

4. **Supervised-from-scratch TCN/CRNN**
   - same Stage 4 heads;
   - no SSL pretraining;
   - used for label-efficiency comparison.

SSL scope:

- Stage 1 SSL objective: masked single-channel latent/feature modeling on `12 kHz` IQ and STFT branches;
- Stage 2 SSL objective: masked sensor latent prediction using Stage 1 per-channel encoder outputs plus geometry metadata;
- Stage 4 supervised heads: DOA regression, angular probability map, and diagnostic source presence;
- Stage 3 latent dynamics: excluded from MVP and evaluated only after Tier 0 gates pass;
- Tier 2 objectives and backbones: no DINO/JEPA/wav2vec/HuBERT/Mamba in MVP.

Stage-wise execution order:

1. Run supervised-from-scratch baselines first to establish a non-SSL reference.
2. Train Stage 1 SSL single-channel encoder on channel views extracted from the BELLHOP training array examples, without DOA labels and without treating hydrophones from the same array scene as independent split units.
3. Freeze or EMA-stabilize the Stage 1 encoder, then train Stage 2 masked-sensor SSL on full array examples with geometry metadata.
4. Attach Stage 4 heads and evaluate head-only probing, adapter tuning, and full fine-tuning under `10%`, `50%`, and `100%` label budgets.
5. Compare against no-SSL and no-geometry ablations before making any SSL or geometry-transfer claim.

Stage-wise data usage:

| Stage | Training unit | Uses `~120k` train array examples? | Label use | Notes |
|---|---|---:|---|---|
| Supervised baseline | array example | yes | DOA labels | Establishes no-SSL reference before SSL claims. |
| Stage 1 SSL | single-channel view extracted from array example | yes, expanded to channel views | no DOA labels | ULA-6 gives `6` views per array example; split identity remains the parent array scene. |
| Stage 2 SSL | full array example with masked sensors | yes | no DOA labels | Uses Stage 1 encoder outputs plus geometry metadata. |
| Stage 4 head-only / adapter / fine-tune | labeled array example | label-budget subset of train examples | DOA labels | Budgets are `10%`, `50%`, `100%` of train array examples, not channel views. |
| Validation/test | array example | no; uses held-out val/test examples | labels for evaluation only | No validation/test channel views may influence Stage 1/2 training. |

## 10. Classical And Neural Baselines

Classical baselines:

| Baseline | Role | Required settings |
|---|---|---|
| Delay-and-sum / Bartlett | sanity lower-bound | same steering grid and sound speed |
| MVDR / Capon | primary classical comparator | covariance window `2.0 s`, diagonal loading `{1e-3, 1e-2, 1e-1}` |
| MUSIC | primary classical comparator | source count fixed to `1`; same grid |
| GCC-PHAT / TDOA | broadband comparator | pairwise TDOA then least-squares azimuth fit |
| SRP-PHAT | primary broadband comparator | azimuth grid `[-90, 90]` with `1 deg` resolution |
| Bartlett MFP | hydroacoustic physics baseline | if BELLHOP replica fields can be generated for the same environment |
| Oracle-environment MFP | privileged upper bound | reported separately, never as equal-information baseline |

Neural baselines:

- supervised TCN;
- supervised CRNN;
- no-geometry version of the proposed model;
- same model trained from scratch without SSL;
- head-only probe on frozen SSL backbone;
- full fine-tuning as upper bound.

Every baseline must use the same train/validation/test split, chunk duration, sampling rate, SNR/SIR condition, and primary metrics.

## 11. Training And Adaptation Protocol

Label budgets:

| Budget | Labeled train examples | Purpose |
|---|---:|---|
| 10% | `~12,000` | low-label setting |
| 50% | `~60,000` | primary SSL label-efficiency gate |
| 100% | `~120,000` | full supervised comparison |

Training runs:

- random seeds: `5` per model/budget;
- early stopping: validation median angular error, patience `10` epochs;
- maximum epochs: `100`;
- batch size: chosen by memory, but effective batch size must be reported;
- optimizer, learning rate, scheduler, and weight decay must be reported before running.

Adaptation modes on held-out geometries:

1. zero-shot inference;
2. head-only tuning using `10%` labeled examples from the held-out geometry;
3. geometry-adapter tuning using `10%` labeled examples;
4. full fine-tuning as upper bound.

## 12. Metrics

Primary DOA metrics:

- median angular error;
- 95th percentile angular error;
- accuracy within `5 deg`;
- accuracy within `10 deg`.

Angular probability-map metrics:

- negative log-likelihood;
- top-1 angular error;
- probability mass within `5 deg` of true angle;
- expected calibration error with `15` confidence bins.

Source presence diagnostic metrics:

- F1;
- false alarm rate;
- missed detection rate.

Stratification:

- array geometry;
- BELLHOP environment id;
- source family;
- azimuth sector: `[-90,-60]`, `[-60,-30]`, `[-30,0]`, `[0,30]`, `[30,60]`, `[60,90]`;
- SNR/SIR;
- clean/noisy/interfered;
- source range bins: `50-150 m`, `150-400 m`, `400-700 m`, `700-1200 m`.

## 13. Mandatory Gates

### 13.1 Data And Simulator Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| BELLHOP convergence | Section 6.4 thresholds pass on 5-environment sample | stop dataset generation |
| Phase/delay preservation | TDOA diagnostic error `< 0.25 ms` | fix preprocessing/IR construction |
| Metadata completeness | `100%` examples have required metadata fields | block training |
| Leakage audit | no environment/source/noise seed appears in multiple splits | regenerate splits |

### 13.2 Geometry Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| Permutation canary | shuffled channel order changes median angular error by `< 0.1 deg` and probability-map NLL by `< 1%` | block Stage 2/downstream reporting |
| No-geometry comparison | geometry-conditioned model improves held-out geometry median angular error by at least `15%` relative to no-geometry baseline | do not claim geometry transfer |
| Changed aperture | degradation from ULA-6 to ULA-6-shifted is `< 25%` relative median angular error increase | mark transfer partial |
| Missing sensor diagnostic | random one-sensor dropout increases median error by `< 50%` | mark missing-sensor robustness unsupported |

### 13.3 SSL And Baseline Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| 50% label efficiency | SSL-pretrained model at 50% labels is within `5%` of 100% supervised-from-scratch median error or improves over 50% supervised-from-scratch by `>= 10%` | do not claim SSL label-efficiency benefit |
| Classical competitiveness | proposed model beats or matches MVDR/Capon and MUSIC within `10%` median angular error under matched information | do not claim competitive DOA performance |
| SRP-PHAT comparison | proposed model beats SRP-PHAT by `>= 10%` on noisy/interfered subsets or reports where it loses | claim only partial |
| Seed reliability | direction of improvement holds in at least `4/5` random seeds | mark result preliminary |

## 14. Kill / Pivot Criteria

Pause architecture expansion and report a negative or partial result if any of the following hold:

1. permutation canary fails;
2. geometry-conditioned model does not improve held-out geometry transfer over no-geometry baseline by at least `15%`;
3. SSL pretraining fails the 50% label-efficiency gate;
4. proposed model loses to both MVDR/Capon and MUSIC under matched information;
5. randomized test has fewer than `10` successful held-out BELLHOP environments;
6. held-out environment median error variance is so high that the best model's 95% confidence interval overlaps the no-geometry baseline;
7. BELLHOP convergence or TDOA preservation gates fail.

If a kill/pivot criterion triggers, do not add Stage 3, DINO/JEPA, Mamba, wav2vec/HuBERT, or larger backbones as a rescue step. First report the failure and isolate whether the blocker is simulation construction, preprocessing, geometry modeling, baseline strength, or SSL objective choice.

## 15. Required Artifacts

Before interpreting results, the run directory must contain:

- frozen protocol copy;
- YAML or JSON configs for data generation, preprocessing, model, training, and evaluation;
- generated environment manifest with all randomized parameters;
- array geometry manifest;
- source waveform seed manifest;
- split manifest;
- BELLHOP `.env` files or equivalent generated inputs;
- BELLHOP arrivals and impulse-response metadata;
- convergence-check report;
- phase/delay preservation report;
- permutation-canary report;
- leakage-audit report;
- baseline configs and tuned hyperparameters;
- metrics tables with per-seed and per-environment results;
- failure-case table;
- compute report: parameter count, memory, preprocessing time, inference latency, hardware.

## 16. Reporting Rules

The report must use this claim status vocabulary:

- `supported`;
- `partially supported`;
- `not supported`;
- `not yet evaluated`.

Mandatory limitation statement:

> This experiment is BELLHOP-only and simulation-stage only. It does not demonstrate real-world hydroacoustic performance, BELLHOP-to-real transfer, or operational Novik Bay readiness.

Minimum report tables:

1. main model vs baselines;
2. classical baselines;
3. neural ablations;
4. geometry transfer;
5. label efficiency;
6. noise/interference robustness;
7. held-out BELLHOP environment spread;
8. compute and latency;
9. claim-to-evidence scorecard;
10. failed/partial/not-yet-evaluated claims.
