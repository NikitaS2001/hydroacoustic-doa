# BELLHOP MVP Experiment Protocol

## Status

This is a **non-final draft** of the first numeric, executable experiment protocol for the geometry-conditioned hydroacoustic DOA framework. It is a **BELLHOP-only simulation-stage protocol**. Its status is **NO-GO**: full dataset generation and confirmatory claims remain blocked until the diagnostic pilot prerequisites and gates below are completed; no experiment described here has been executed. Future results from this protocol may support simulation-stage claims only and must not be reported as real-world Novik Bay performance.

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
| Azimuth range | `[-70 deg, +70 deg]` broadside-relative |
| Train azimuth sampling | uniform random over `[-70, +70] deg` |
| Dev-test azimuth grid | `2.5 deg` spacing over `[-70, +70] deg`, plus random OOD angles |
| Source count | 1 target source |
| Source state | Static within one 2 s example |
| Receiver state | Static |
| Far-field assumption | Required; validate with Section 6.3 before dataset generation |
| Output heads | DOA regression and angular probability map |
| Source presence head | Diagnostic only: target-present vs noise/interference-only windows |

## 3. Array Configuration

All coordinates are in meters in an array-centered coordinate system. `x` is horizontal across the aperture, `y` is horizontal orthogonal to `x`, and `z = 0` for all sensors in this MVP.

### 3.1 Training Geometry A: ULA-5-H

| Sensor | x | y | z |
|---|---|---:|---:|
| 0 | -0.500 | 0.000 | 0.000 |
| 1 | -0.250 | 0.000 | 0.000 |
| 2 | 0.000 | 0.000 | 0.000 |
| 3 | 0.250 | 0.000 | 0.000 |
| 4 | 0.500 | 0.000 | 0.000 |

Parameters:

- hydrophones: `5`;
- spacing: `0.25 m`;
- aperture: `1.00 m`;
- nominal sound speed for geometry checks: `1500 m/s`;
- minimum wavelength at 3000 Hz: `0.5 m`;
- spacing-to-wavelength ratio at 3000 Hz: `0.5`.

### 3.2 Training Geometry B: L-5

Symmetric L-shaped array with three sensors on the `x` axis and three sensors on the `y` axis, sharing the central sensor. This gives 5 unique sensors in a 2-D non-collinear cross topology. The symmetric shape avoids the asymmetric leg-length bias of the previous L-6 design. The leg spacing is kept at `0.25 m` to match the ULA-5-H element spacing and avoid spatial aliasing.

| Sensor | x | y | z |
|---|---|---:|---:|
| 0 | -0.250 | 0.000 | 0.000 |
| 1 | 0.000 | 0.000 | 0.000 |
| 2 | 0.250 | 0.000 | 0.000 |
| 3 | 0.000 | -0.250 | 0.000 |
| 4 | 0.000 | 0.250 | 0.000 |

Parameters:

- hydrophones: `5`;
- leg spacing: `0.25 m`;
- maximum aperture: `0.500 m` (along each leg);
- role: 2-D non-collinear symmetric training topology.

### 3.3 Validation Geometry: ULA-5-Shifted-Aperture

Same topology and sensor count as ULA-5-H, but spacing is `0.20 m` and aperture is `0.80 m`. This tests changed aperture without changed topology.

| Sensor | x | y | z |
|---|---|---:|---:|
| 0 | -0.400 | 0.000 | 0.000 |
| 1 | -0.200 | 0.000 | 0.000 |
| 2 | 0.000 | 0.000 | 0.000 |
| 3 | 0.200 | 0.000 | 0.000 |
| 4 | 0.400 | 0.000 | 0.000 |

Parameters:

- hydrophones: `5`;
- spacing: `0.20 m`;
- aperture: `0.80 m`;
- role: aperture transfer with same topology.

### 3.4 Held-Out Geometry A: Square-4

| Sensor | x | y | z |
|---|---:|---:|---:|
| 0 | -0.375 | -0.375 | 0.000 |
| 1 | -0.375 | 0.375 | 0.000 |
| 2 | 0.375 | -0.375 | 0.000 |
| 3 | 0.375 | 0.375 | 0.000 |

Parameters:

- hydrophones: `4`;
- side length: `0.75 m`;
- maximum aperture: `1.061 m`;
- role: held-out topology transfer; may be used for dev-test and model selection.

### 3.5 Held-Out Geometry B (Sealed): Rect-5

Asymmetric rectangular array with three sensors in the lower row and two sensors in the upper row. This topology is distinct from the ULA-5-H and L-5 training geometries while sharing the same 5-element sensor count.

| Sensor | x | y | z |
|---|---|---:|---:|
| 0 | -0.500 | -0.250 | 0.000 |
| 1 | 0.000 | -0.250 | 0.000 |
| 2 | 0.500 | -0.250 | 0.000 |
| 3 | -0.500 | 0.250 | 0.000 |
| 4 | 0.500 | 0.250 | 0.000 |

Parameters:

- hydrophones: `5`;
- maximum aperture: `1.118 m`;
- role: **sealed confirmatory topology transfer**; same sensor count as ULA-5-H and L-5. Rect-5 must not be used for model selection, ablation tuning, or hyperparameter search. It is evaluated once per frozen model configuration.

### 3.6 Geometry Split Policy

Training, validation, and sealed-test geometries are split as follows:

| Geometry | Split | Purpose |
|---|---|---|
| ULA-5-H | Train | Primary horizontal collinear topology |
| L-5 | Train | 2-D non-collinear symmetric topology; same sensor count as ULA-5-H |
| ULA-5-Shifted | Validation | Aperture transfer, same topology |
| Square-4 | Dev-test / validation | Held-out topology for development; tests transfer to different sensor count |
| Rect-5 | Sealed test | Final confirmatory topology transfer |

### 3.7 Matched Coordinate Ablation Modes

All geometry-conditioned models must be compared against the same backbone run in these coordinate-input modes to make the geometry effect causally identifiable:

| Mode | Coordinate input | Purpose |
|---|---|---|
| `no-coordinate` | None | Tests whether geometry metadata matters at all |
| `coordinates-only` | Raw `x,y,z` sensor coordinates | Tests raw coordinate conditioning |
| `pairwise-only` | Pairwise distances/directions/RBF | Tests relational geometry without raw coordinates |
| `full` | Raw coordinates + pairwise features | Primary proposed geometry conditioning |
| `shuffled-coordinates` | Same as `full`, random sensor permutation applied to signal and coordinates | Permutation canary |

The no-geometry baseline in the ablation matrix is `no-coordinate`. The primary proposed model is `full`.

### 3.8 Sensor Perturbation Conditions

Sensor-coordinate perturbation is used only for robustness testing and calibration gates, not for the primary clean comparison.

| Condition | Coordinate noise | Gain error | Phase error |
|---|---|---:|---:|
| Clean | `0 mm` | `0 dB` | `0 deg` |
| Calibration-lite | Gaussian `sigma = 5 mm`, clipped at `15 mm` | Uniform `[-0.5, 0.5] dB` | Uniform `[-5, +5] deg` |
| Calibration-stress | Gaussian `sigma = 15 mm`, clipped at `40 mm` | Uniform `[-1.5, +1.5] dB` | Uniform `[-15, +15] deg` |

Notes:

- `Phase error` is an explicit phase rotation applied to the complex analytic signal or STFT complex channels of the affected sensor. It subsumes small time-synchronisation errors for short-baseline arrays because the physically observable quantity is inter-channel phase difference (PDOA/IPD), not absolute time delay.
- Calibration-stress is diagnostic. It must not be used to support the main MVP claim.

### 3.9 Spatial Aliasing Note

The declared `λ/2` spacing at `3000 Hz` assumes `c = 1500 m/s`. The randomized SSP allows sound speeds as low as `1460 m/s`, which makes the wavelength at `3000 Hz` approximately `0.487 m`. At that speed, `0.25 m` spacing is slightly above `λ/2`, so the top of the band becomes a **spatial-aliasing stress regime**.

- Primary clean comparisons should treat the effective unambiguous upper frequency as `f_max_eff = c_min / (2 * spacing) = 1460 / (2 * 0.25) = 2920 Hz` for the `0.25 m` train geometries.
- The `3000 Hz` upper bound is retained for robustness and aliasing-stress diagnostics, but claims about clean-band performance must be restricted to `f ≤ 2920 Hz` for ULA-5-H and L-5 unless aliasing is explicitly modeled.

Effective unambiguous upper frequency per geometry (`c_min = 1460 m/s`):

| Geometry | Minimum spacing | `f_max_eff` | Status in useful band `500–3000 Hz` |
|---|---:|---:|:---|
| ULA-5-H | `0.25 m` | `2920 Hz` | Aliasing stress near top edge |
| L-5 | `0.25 m` | `2920 Hz` | Aliasing stress near top edge |
| ULA-5-Shifted | `0.20 m` | `3650 Hz` | Clean |
| Square-4 | `0.75 m` | `973 Hz` | Strong aliasing; held-out stress geometry |
| Rect-5 | `0.50 m` | `1460 Hz` | Aliasing above mid-band; sealed stress geometry |

Square-4 and Rect-5 are intentionally used as held-out / sealed stress geometries. Their aliasing behavior must be reported separately from the clean-band metrics of ULA-5-H and L-5.

### 3.10 Ideal Geometry Assumption and Real-World Scope Boundary

The MVP uses **ideal sensor positions** exactly as specified in Sections 3.1–3.6. Manufacturing tolerances, mounting uncertainties, cable-length variations, and thermal deformation are intentionally excluded from the BELLHOP simulation stage.

- The calibration perturbation gates in Section 3.8 test algorithmic robustness to injected position, gain, and phase errors, but they do not model a real manufacturing process.
- The useful band `500–3000 Hz` and the spatial-aliasing limits in Section 3.9 are computed from these ideal positions.
- Frequencies used in historical Novik Bay experiments (e.g., `3219 Hz`, `12000 Hz`) are not part of the MVP useful band. They are out of scope for the BELLHOP simulation stage and may be addressed only in a future real-world transfer protocol with a different array geometry or explicit aliasing modeling.

This assumption is valid because the MVP claim is restricted to BELLHOP-only simulation. A real-world protocol must re-evaluate array tolerances and choose a geometry whose aliasing-free band covers the intended operational frequencies.


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
| Phase representation | `cos(Δφ)` and `sin(Δφ)` or complex ratio `X_i / X_j`; raw wrapped phase regression is banned |
| Primary acoustic cue | PDOA / IPD (phase-difference of arrival / inter-channel phase difference), not TDOA |

Useful-band and sample-rate rationale:

- The useful acoustic band `500-3000 Hz` lies in the low-mid frequency regime where BELLHOP ray tracing is accurate (>200 Hz in shallow water) and matches the dominant frequency content of surface-ship radiated noise and many marine mammal vocalizations.
- It provides adequate angular resolution for the small-aperture arrays in this protocol (wavelength `0.5-3 m` at `c = 1500 m/s`) while avoiding the strong frequency-dependent absorption that limits long-range propagation at frequencies above `5 kHz`.
- The `48 kHz` master sample rate is a hardware and anti-aliasing convenience, not a signal-bandwidth requirement. It permits a sharp anti-alias transition band (`3400-5400 Hz`) before clean integer decimation to the `12 kHz` model rate, and it is a standard acquisition rate for multichannel audio interfaces and hydrophone front-ends. The model input remains band-limited to `500-3000 Hz`.

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

Neural input framing:

| Frame type | Primary | Alternative | STFT reference |
|---|---|---|---|
| Input branch | IQ / analytic signal | IQ / analytic signal | STFT |
| Frame duration | `512 ms` | `256 ms` | `64 ms` |
| Frame samples at 12 kHz | `6144` | `3072` | `768` |
| Hop duration | `128 ms` | `64 ms` | `16 ms` |
| Hop samples at 12 kHz | `1536` | `768` | `192` |
| Overlap | `75%` | `75%` | `75%` |
| Frames per 2.0 s chunk | `12` | `24` | `~124` |
| Purpose | Primary per-channel encoder input | Ablation / fast temporal model | Frequency-domain branch |

- The **512 ms IQ frame** is the primary discrete input to the per-channel encoder. At 500 Hz it contains 256 cycles, giving stable phase estimation; at 3000 Hz it contains 1536 cycles, which is more than sufficient.
- The **256 ms IQ frame** is the alternative for ablations that need higher temporal resolution. It is used only as a secondary ablation, not as the default.
- The per-channel encoder may process IQ frames independently or with light causal context; the array encoder aggregates frame-level embeddings across the 2.0 s chunk.
- Frame boundaries are aligned across all hydrophone channels for a given array example.

Processing mode:

- The MVP uses **block-based processing** with `2.0 s` chunks and `1.0 s` hop.
- The per-channel encoder and array encoder may use the full `2.0 s` chunk context; causal-only streaming inference is **not required** for the MVP.
- Real-time / causal streaming is an explicit future extension and is listed in the roadmap.

Normalization:

- one shared RMS scale factor per multi-channel array chunk;
- statistics estimated on training split only;
- no independent per-channel RMS normalization;
- no per-frame max normalization;
- preserve phase, delay, and inter-channel amplitude ratios.

Phase-difference preservation (PDOA/IPD):

- The array is short-baseline (aperture 1.00 m, spacing 0.25 m). The primary spatial cue is the inter-channel phase difference, not the absolute time delay.
- Phase differences must be represented through complex-valued channels or through `sin/cos` of the phase difference. Direct regression of wrapped phase is banned.
- For STFT inputs, the complex ratio `X_i[f,t] / X_j[f,t]` or its real and imaginary components must be available to downstream models.
- Independent random phase shifts across hydrophone channels are banned as augmentations unless they model a physically documented calibration error.

## 5. Synthetic Source Families

Each family must produce examples across the full train azimuth range and all train BELLHOP environments.

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

Detailed parameter distributions, sampling rules, and family-specific SNR masking are frozen in Section 8.2.

CW exception:

- CW is the only family allowed to use the full `2.0 s` active duration. The onset/offset ramp rule (active onset `0.10-0.30 s`, trailing context `≥ 0.10 s`) is waived for CW because a continuous tone is the defining characteristic of the family.
- All other families must follow the onset/offset contract.

OOD source-family test:

- hold out `20%` of parameter ranges per family for OOD evaluation;
- additionally run one complete-family holdout where NLFM is excluded from training and included only in test.

## 6. BELLHOP Environment Configuration

### 6.1 Environment Counts

| Split | Independent environments | Role |
|---|---|---:|
| Train | `32` | model training and train-split normalization |
| Validation | `8` | model selection and early stopping |
| Dev-test | `12` | development test for ablation tuning and gate debugging |
| Sealed confirmatory test | `4` | single-access confirmatory evaluation on held-out Rect-5 geometry |
| Novik-like target placeholder | `1` | diagnostic target benchmark only |


Environment-generalization claims must report mean, standard deviation, minimum, maximum, and per-environment results across the `12` dev-test environments. If fewer than `10` dev-test environments are successfully generated, environment-generalization claims are preliminary only. Confirmatory claims require the sealed test.

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

For ULA-5-H:

```text
max(10 * 1.00, 2 * 1.00^2 / 0.5) = max(10.0, 4.0) = 10.0 m
```

For L-5 the maximum aperture is `0.50 m`, giving an even smaller bound. The protocol uses `R_min = 50 m`, so the MVP far-field gate passes for all specified arrays. If later arrays use larger apertures or higher frequency bands, this calculation must be repeated.

### 6.4 BELLHOP Broadband/Azimuth Contract And Outputs

Primary generation mode:

- BELLHOP mode: arrivals;
- **receiver layout:** a single BELLHOP run computes arrivals for all hydrophones simultaneously as a 3-D receiver set. Independent per-hydrophone runs are forbidden unless a pilot proves equivalent inter-sensor coherence.
- impulse response sampling rate: `48000 Hz`;
- impulse response duration: `2.5 s`;
- maximum arrival delay retained: `2.0 s`;
- arrivals below `-60 dB` relative to strongest arrival may be discarded after metadata logging;
- controlled source waveform convolved with per-hydrophone impulse responses.

Broadband contract (frozen):

BELLHOP is a narrowband range-depth ray tracer. The source families defined in Section 5 remain broadband waveforms (LFM chirp, NLFM chirp, broadband pulse, noise burst, transient). To propagate these broadband waveforms through BELLHOP, the channel response is constructed from a set of narrowband BELLHOP runs and then recombined.

- **Ray-trace center-frequency grid (initial candidate):** `500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000 Hz` (11 frequencies, 250 Hz spacing). These are the frequencies at which BELLHOP computes arrivals; they are **not** source waveforms. The grid must cover the useful acoustic band and must be frozen after the frequency-grid convergence study in Section 8.1.
- **Narrowband run:** each BELLHOP run treats the source as a pure-tone CW at one center frequency for the purpose of computing the complex arrival amplitudes and delays at that frequency.
- **Broadband channel synthesis:** the per-frequency complex arrivals are combined into a single broadband channel transfer function `H(f)` on the ray-trace grid. The propagated signal is produced in the frequency domain as `Y(f) = S(f) * H(f)`, where `S(f)` is the Fourier transform of the source waveform, followed by an inverse Fourier transform to the time domain. The chosen interpolation rule for `H(f)` between ray-trace frequencies and the chosen IFFT parameters must be reported and frozen for the entire MVP.
- **arlpy limitation:** `arlpy.uwapm` runs BELLHOP at a single frequency per call and provides `arrivals_to_impulse_response` for one narrowband IR only. Broadband synthesis must be implemented outside `arlpy`, using repeated `compute_arrivals` calls and custom frequency-domain combination.
- **Solver mode:** `C` (coherent) for narrowband runs; `I` (incoherent) only for the final broadband energy check if explicitly reported.
- **Bearing convention:** `0 deg` is broadside; positive azimuth is clockwise from broadside when looking down the `+x` axis; source coordinates are
  - `source_x = range * sin(azimuth)`;
  - `source_y = range * cos(azimuth)`;
  - `source_z = source_depth`.
- **Array heading:** all arrays use the same heading; array rotation is modeled by rotating hydrophone coordinates, not by changing the bearing convention.
- **Cross-solver sanity:** at least one low-frequency shallow-water corner case must be re-run in KRAKEN or SCOOTER and compared with BELLHOP before the channel bank is frozen.


Sanity and convergence checks:

| Check | Requirement |
|---|---|
| Ray fan convergence | run with `N_beams = 2001` and `4001`; primary DOA metrics may proceed only if median arrival delay difference is `< 0.10 ms` and relative received-energy difference is `< 1 dB` on a 5-environment sample |
| Arrival ordering | first-arrival delay must be finite for every hydrophone |
| Inter-sensor TDOA bound | absolute direct-path delay difference must be `<= aperture / 1450 m/s + 0.05 ms` (auxiliary convergence bound, not the primary gate) |
| PDOA/IPD preservation | synthetic direct-path-only diagnostic must recover inter-channel phase difference within the frequency-dependent tolerance defined in Section 13.4 |
| Cross-solver agreement | KRAKEN/SCOOTER vs BELLHOP arrival phase difference within `0.05 rad` on the low-frequency corner case |
| Metadata completeness | every example stores environment id, array id, hydrophone coordinates, source depth/range/azimuth, SSP parameters, bottom parameters, SNR/SIR, seed, and BELLHOP run config |

## 7. Noise And Interference

BELLHOP is used only to compute **clean** multi-channel propagation responses. All additive noise, SNR scaling, and sensor-level interference are applied **after** channel generation. SNR is therefore a nested experimental factor, not a dimension of the BELLHOP channel bank.

### 7.1 Noise Model Categories

| Category | How generated | Spatial structure | Examples |
|---|---|---|---|
| Sensor-level additive noise | Post-hoc overlay on generated waveforms | Incoherent across channels by default | White noise, colored `1/f`/`1/f²` noise, sensor self-noise |
| Tonal narrowband interference | Post-hoc synthesized tone added per channel | Incoherent unless explicitly correlated | Single-tone interferer within `700-2800 Hz` |
| Acoustic interferer | Separate BELLHOP propagation run for the interfering source | Coherent across channels; same multipath structure as target | Second source at angular separation `{15, 30, 60} deg`, SIR `{20, 10, 0} dB` |
| Real recorded noise | Post-hoc overlay of recorded segments | Preserved if multi-channel recording; otherwise replicated per channel | Ambient sea noise, shipping noise |

### 7.2 SNR Definition and Nested Factor Status

Primary in-band SNR is computed over `500-3000 Hz` relative to the propagated signal power at the reference receiver (sensor index 0). Detailed SNR regimes are listed in Section 8.2.4.

Rules:

- SNR does **not** multiply the number of BELLHOP channel configurations or the channel-bank size. One clean channel config supports multiple SNR/noise seeds.
- For training, noise seeds may be redrawn each epoch (dynamic augmentation) or pre-generated and cached. Either way, the same physical scene (`environment + geometry + source position + azimuth`) remains one channel config.
- For validation and sealed confirmatory test, SNR levels and noise seeds must be **fixed and frozen** before model selection. Every validation/test example must be reproducible from its `(channel_config_id, snr_level, noise_seed)`.
- Statistical inference (power analysis, environment-level bootstrap, confidence intervals) is performed at the environment level, with averaging over noise realizations within each environment.

### 7.3 Spatially Coherent Interference

Simple post-hoc noise overlay is valid only for sensor-level or incoherent interference. Any interference that shares propagation structure across sensors (e.g., a second acoustic source, coherent surface/shipping noise) must be modeled as a separate BELLHOP propagation channel or obtained from multi-channel recordings. In MVP, acoustic interferers are diagnostic only and require an explicit separate BELLHOP run.

Real-noise augmentation:

- excluded from the primary MVP because no real-noise corpus is assumed available;
- if introduced, it must be reported as augmentation only, never as real-world validation.

## 8. Dataset Size And Split Units

Split units are independent environments and simulation seeds, not overlapping windows.

Counting convention:

- one **array example** is one physical scene rendered as a synchronized multi-channel hydrophone chunk for one array geometry;
- `~120,000 / ~24,000 / ~48,000` are counts of array examples, **total across the two train geometries (ULA-5-H and L-5)**, not counts per geometry and not counts of single-channel clips;
- for an array with `N` hydrophones, one array example yields `N` single-channel views for Stage 1 SSL;
- A 5-channel training geometry therefore yields up to `~600,000` Stage 1 single-channel views from `~120,000` train array examples before masking/cropping augmentation;
- Square-4 yields `4` Stage 1 views per array example, Rect-5 yields `5`;
- Stage 2 and Stage 4 consume array examples, not independent channel views;
- DOA labels are attached to array examples and are hidden from Stage 1/2 SSL pretraining unless a diagnostic probe explicitly uses labels.

Primary balanced dataset target:

| Split | Approx examples | Per geometry | Construction |
|---|---|---:|---:|
| Train | `~120,000` | `~60,000` | 32 environments × 2 train geometries × source families × azimuths × source-waveform seeds × post-hoc SNR/noise seeds |
| Validation | `~24,000` | `~12,000` | 8 environments × ULA-5-H + ULA-5-shifted × matched source coverage × frozen SNR/noise seeds |
| Dev-test | `~48,000` | `~12,000` | 12 environments × all non-sealed geometries × denser azimuth grid × held-out source parameters × frozen SNR/noise seeds |
| Sealed confirmatory test | `~12,000` | `~12,000` | independently generated from held-out Rect-5 geometry and held-out environments; frozen SNR/noise seeds; one formal access per frozen model |
| Novik-like placeholder | `~4,000` | `~4,000` | one diagnostic environment; frozen SNR/noise seeds; no model selection |

Pilot dataset target (preliminary, before full generation):

| Split | Approx examples | Per geometry | Purpose |
|---|---|---:|---|
| Train pilot | `~20,000` | `~10,000` | Verify geometry effect, classical baselines, PDOA/IPD gate, runtime feasibility |
| Validation pilot | `~4,000` | `~2,000` | Model selection on pilot scale |
| Dev-test pilot | `~8,000` | `~4,000` | Gate debugging, ablation sanity |
| Sealed pilot | not used | — | Sealed test is opened only after full-dataset model freeze |

Pilot coverage requirements:

- `8` train environments sampled via Latin Hypercube Sampling across the 9 environment parameters;
- both train geometries (ULA-5-H, L-5);
- train azimuths uniformly sampled from `[-70, +70] deg` with `~18` effective coverage bins and dev-test azimuths on the 2.5° grid over `[-70, +70] deg`;
- `3` source families (CW, LFM chirp, band-limited noise burst);
- `3` SNR regimes (clean, 10 dB, 0 dB) applied post-hoc;
- `2` source range bins and `2` source/receiver depth bins;
- `2` independent source-waveform seeds per channel config;
- `2` independent noise seeds per `(channel config, SNR regime)` for training;
- minimum `10` examples per `(geometry, environment, azimuth-sector, family, SNR)` cell.

Leakage rules:

- no BELLHOP environment appears in more than one split;
- no source waveform seed appears in more than one split;
- no validation/test noise or interference seed appears in more than one split;
- train noise seeds may be redrawn dynamically or cached, but must not leak into validation/test splits;
- augmented views of the same physical scene remain in the same split;
- validation/test normalization uses train-split statistics only;
- **sealed-test examples must not be inspected during model development, architecture selection, or hyperparameter tuning.**

### 8.1a Sealed Test Policy

The single randomized test split in the original protocol invited selection overfitting. This amendment splits evaluation into a development test and a sealed confirmatory test.

- **Dev-test:** used for model development, ablation tuning, gate debugging, and pilot experiments. May be accessed repeatedly. Results on dev-test alone may not support the primary MVP claim.
- **Sealed confirmatory test:** generated independently from the same environment distribution but held in isolation. Access requires:
  - architecture, backbone, geometry representation, and hyperparameters frozen in writing;
  - a single formal evaluation run per frozen model configuration;
  - every access logged with date, model version/commit, reason, and any decision triggered by the result.
- **Primary claim:** the main MVP claim (geometry-conditioned model improves held-out topology transfer) must be supported by sealed-test results.
- **Failure action:** if the sealed test is accessed before freeze, the corresponding result is exploratory and must not be reported as confirmatory evidence.


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

The generated channel or per-hydrophone impulse responses may then be reused across several source waveforms, source-family parameter draws, and post-hoc noise/SNR variants. This is required to keep the MVP computationally feasible. Because SNR is applied after BELLHOP, the number of BELLHOP runs is determined by unique channel configs and the frequency grid, not by the number of SNR conditions.

Recommended channel-bank target for full dataset:

| Split | Final array examples | Unique BELLHOP channel configs | Reuse factor |
|---|---|---:|---:|
| Train | `~120,000` | `10,000-20,000` | `6-12` examples per channel |
| Validation | `~24,000` | `2,000-4,000` | `6-12` examples per channel |
| Dev-test | `~48,000` | `5,000-10,000` | `4-10` examples per channel |
| Sealed confirmatory test | `~12,000` | `1,000-2,500` | `4-8` examples per channel |
| Novik-like placeholder | `~4,000` | `500-1,000` | `4-8` examples per channel |

Recommended channel-bank target for pilot dataset:

| Split | Pilot array examples | Unique BELLHOP channel configs | Reuse factor |
|---|---|---:|---:|
| Train pilot | `~20,000` | `1,500-3,000` | `6-12` examples per channel |
| Validation pilot | `~4,000` | `300-700` | `6-12` examples per channel |
| Dev-test pilot | `~8,000` | `800-1,600` | `4-10` examples per channel |

Total planned BellhopCUDA channel runs (full dataset):

```text
low  = 10,000 + 2,000 + 5,000 + 1,000 + 500   = 18,500
high = 20,000 + 4,000 + 10,000 + 2,500 + 1,000 = 37,500
```

Each unique channel config requires one BELLHOP run per ray-trace frequency. With the initial 11-frequency grid, multiply the numbers above by 11 to get the total narrowband BELLHOP runs.


Naive upper bound if every final array example required a unique BELLHOP channel config:

```text
120,000 + 24,000 + 48,000 + 12,000 + 4,000 = 208,000 BellhopCUDA runs
```

This bound counts SNR/source-seed variants as separate channels and is **not** the intended implementation. The intended BELLHOP workload is the channel-bank target above (`18,500-37,500` unique configs × `N_frequencies`). If the implementation requires close to `208,000` BellhopCUDA runs, it has failed to reuse channels across SNR/noise/source variants; reduce the dataset size or increase reuse before training.

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
| Frequency-grid convergence | run frequency-grid convergence study on `20` representative configs before freezing the grid |
| Freeze rule | choose final channel-bank size and frequency grid only after p95 runtime and convergence metrics are known |

### 8.1b Frequency-Grid Convergence Study

BELLHOP is a narrowband ray tracer; broadband channel responses must be synthesized from multiple single-frequency runs. The ray-trace frequency grid must be dense enough to capture frequency-dependent propagation but coarse enough to keep the MVP computationally feasible.

**Initial candidate grid:**

```
500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000 Hz
```

(11 frequencies, 250 Hz spacing.)

**Why 250 Hz as a starting point:** it is half the minimum bandwidth of the narrowest broadband source family in Section 5 (broadband pulse bandwidth ≥ 500 Hz), giving a Nyquist-like lower bound for spectral sampling.

**Convergence grids to compare in the pilot:**

| Grid name | Frequencies | Count | Relative cost |
|---|---|---:|---:|
| Coarse | `500, 1000, 1500, 2000, 2500, 3000` | 6 | 0.55× |
| Medium (candidate) | `500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000` | 11 | 1.0× |
| Fine | `500, 625, 750, ..., 3000` | 21 | 1.9× |
| Very fine | `500, 550, 600, ..., 3000` | 51 | 4.6× |

**Convergence criteria:** for each grid, synthesize the broadband channel response and evaluate on a small set of direct-path examples:

1. **DOA stability:** median angular error difference between the grid and the very-fine grid is `< 0.5°` on clean broadband-pulse examples.
2. **IPD stability:** maximum inter-channel phase-difference difference between the grid and the very-fine grid is `< 0.05 rad` on `≥ 90%` of frequency bins.
3. **Channel-energy stability:** relative energy difference of the synthesized IR is `< 1 dB`.
4. **Runtime budget:** p95 runtime per channel-config × grid-size must fit within the available compute budget.

**Grid selection rule:** choose the coarsest grid that satisfies criteria 1–3. If the candidate grid fails, refine it; if it passes with margin, consider a coarser grid. The chosen grid and the convergence evidence must be reported in the final artifacts.

**arlpy note:** `arlpy.uwapm` runs BELLHOP at a single frequency per call. The convergence study must be implemented by repeatedly calling `compute_arrivals` at each grid frequency and combining the arrivals in the frequency domain outside `arlpy`.

Runtime estimate formula:

```text
T_total_seconds = N_channel_configs * N_frequencies * T_p95_seconds_per_run * convergence_multiplier + T_io
```

where:

- `N_channel_configs` is the number of unique channel configurations;
- `N_frequencies` is the number of ray-trace frequencies in the chosen grid (initial candidate: 11);
- `T_p95_seconds_per_run` is the p95 wall time of one BELLHOP run at one frequency;
- `convergence_multiplier` accounts for beam-convergence checks.

Use `convergence_multiplier = 2` if both `2001` and `4001` beam runs are required for every generated channel. Use `convergence_multiplier = 1.1-1.3` only if the full convergence check is run on a representative subset and routine generation uses the chosen beam count.

Planning table excluding file I/O, assuming the 11-frequency initial candidate grid:

| Unique channel configs | `0.2 s/run` | `1 s/run` | `5 s/run` |
|---|---:|---:|---:|
| `18,500` | `10.7 h` | `53.5 h` | `267 h` / `11.1 days` |
| `37,500` | `21.7 h` | `108.7 h` | `544 h` / `22.7 days` |
| `208,000` no-reuse bound | `120.3 h` | `601.7 h` / `25.1 days` | `3,009 h` / `125.4 days` |

If a coarser grid is chosen after convergence (e.g., 6 frequencies), multiply the table values by `6/11 ≈ 0.55`. If a finer grid is needed, multiply accordingly.


If p95 runtime exceeds `5 s` per channel on the available GPU, the MVP should start with the pilot dataset defined in Section 8 and reduce the channel-bank size accordingly:

| Split | Pilot array examples | Unique channel configs |
|---|---|---:|
| Train pilot | `~20,000` | `1,500-3,000` |
| Validation pilot | `~4,000` | `300-700` |
| Dev-test pilot | `~8,000` | `800-1,600` |

The full `120k/24k/48k` dataset should be generated only after the pilot benchmark and pilot training confirm that the channel bank is computationally affordable and scientifically useful.

## 8.2 Dataset Design and Sampling Contract

This section fixes the sampling strategy for BELLHOP environments, source signals, source-array geometry, SNR, and stratification. These rules must be frozen before dataset generation begins.

### 8.2.1 Environment Allocation and Sharing

The same BELLHOP environment may be reused with different array geometries because the channel config includes both `environment_id` and `array_geometry_id`. Environments are never shared across splits.

| Split | Environments | Shared across geometries | Purpose |
|---|---|---|---|
| Train | `32` | ULA-5-H, L-5 | Learning geometry-conditioned representation |
| Validation | `8` | ULA-5-H, ULA-5-Shifted | Model selection, early stopping |
| Dev-test | `12` | ULA-5-H, L-5, ULA-5-Shifted, Square-4 | Ablation tuning, gate debugging |
| Sealed confirmatory | `4` | Rect-5 only | Final confirmatory evaluation |
| Novik-like placeholder | `1` | ULA-5-H only | Diagnostic target benchmark |

Environment sampling:

- Train environments must be drawn via **Latin Hypercube Sampling (LHS)** across the 9 continuous parameters in Section 6.2.
- LHS must be stratified by water-depth quartile (`15-26`, `26-37`, `37-48`, `48-60 m`) to avoid depth-clustering.
- Validation, dev-test, and sealed environments must be drawn independently from the same parameter ranges but are not required to use LHS; a uniform random draw is acceptable if the resulting coverage is reported.
- Every environment manifest must report the exact parameter vector and LHS stratum.

### 8.2.2 Source Signal Parameters (Frozen)

Signal families and their parameter distributions. Parameters are sampled independently unless noted.

| Family | Weight | Parameter | Distribution | Notes |
|---|---|---|---|---|
| CW | `1.0` | carrier frequency | uniform `500–3000 Hz` | full 2.0 s active duration; onset/offset ramp waived |
| | | start phase | uniform `[0, 2π)` | independent per example |
| LFM chirp | `1.0` | start frequency | uniform `500–2500 Hz` | end frequency = start + bandwidth |
| | | bandwidth | uniform `500–2000 Hz` | clipped so end ≤ 3000 Hz |
| | | duration | uniform `0.5–2.0 s` | within 2.0 s chunk with 0.10 s trailing context |
| NLFM chirp | `1.0` | start/end frequency | same as LFM | polynomial order `2` or `3` |
| | | polynomial order | categorical `{2, 3}` | each order weight `0.5` |
| Broadband pulse | `1.0` | center frequency | uniform `1000–2500 Hz` | |
| | | bandwidth | uniform `500–1500 Hz` | clipped to `500–3000 Hz` |
| | | pulse length | uniform `50–250 ms` | |
| Impulsive transient | `0.5` | center frequency | uniform `1000–2500 Hz` | |
| | | length | uniform `10–80 ms` | Tukey window α = 0.25 |
| Band-limited noise burst | `1.0` | low cutoff | uniform `500–1500 Hz` | |
| | | high cutoff | uniform `1500–3000 Hz` | high > low + 500 Hz |
| | | burst length | uniform `0.25–2.0 s` | within 2.0 s chunk |

Common signal rules:

- Peak normalization to `-6 dBFS` before propagation.
- Random amplitude scaling `[-6, +3] dB` after propagation.
- Tukey or raised-cosine onset/offset ramps `10–25 ms` (waived for CW).
- Active source onset uniform `0.10–0.30 s` except CW.
- Active source offset must leave at least `0.10 s` trailing context except CW.

### 8.2.3 Source-Array Geometry

All sources are static within a 2.0 s example. Far-field assumption is enforced by Section 6.3.

| Parameter | Train | Validation | Dev-test | Sealed |
|---|---|---|---|---|
| Source range | `50–1000 m` | `50–1000 m` | `50–1200 m` | `50–1200 m` |
| Source depth | `3–20 m`, ≥3 m above bottom | same | same | same |
| Receiver depth | `3–20 m`, ≥3 m above bottom | same | same | same |
| Azimuth | uniform `[-70, +70] deg` | uniform `[-70, +70] deg` | `[-70, +70] deg`, 2.5° grid + random OOD | same as dev-test |

Range bins for stratification and reporting:

- Near: `50–150 m`
- Mid: `150–400 m`
- Far: `400–700 m`
- Very far: `700–1200 m` (dev-test/sealed only)

Azimuth sectors for stratification:

- Left far: `[-70, -50]`
- Left outer: `[-50, -30]`
- Left inner: `[-30, 0]`
- Right inner: `[0, 30]`
- Right outer: `[30, 50]`
- Right far: `[50, 70]`

### 8.2.4 SNR Regimes and Post-Hoc Noise Overlay

BELLHOP generates **clean** multi-channel responses. All SNR/SIR conditions are produced by post-hoc addition of noise or interference to the clean propagated signal.

#### SNR regimes

Primary in-band SNR is computed over `500–3000 Hz` relative to the propagated signal power at the reference receiver (sensor index 0).

| Condition | In-band SNR | Split | Purpose |
|---|---|---|---|
| Clean | `+∞` (no additive noise) | all | Upper-bound reference |
| High white | `20 dB` | all | Easy noisy case |
| Medium white | `10 dB` | all | Moderate noise |
| Low white | `0 dB` | all | Challenging noise |
| Very low white | `-5 dB` | dev-test / sealed diagnostic | Stress regime; not primary metric |
| Colored `1/f` | `20, 10, 0 dB` | train / dev-test | Non-white ambient noise |
| Colored `1/f²` | `20, 10 dB` | train / dev-test | Low-frequency-dominated noise |
| Narrowband tonal interference | SIR `20, 10, 0 dB` | train / dev-test | Incoherent tone overlay; disjoint tone-frequency bins across splits |
| Acoustic interferer | SIR `20, 10, 0 dB` | dev-test diagnostic only | Separate BELLHOP-propagated second source |

#### Noise seed policy

| Split | Noise seed rule |
|---|---|
| Train | May be redrawn per epoch (dynamic augmentation) or pre-generated and cached. The same channel config may appear with multiple noise seeds. |
| Validation | Fixed SNR levels and frozen noise seeds. Reproducible from `(channel_config_id, snr_level, noise_seed)`. |
| Dev-test | Fixed SNR levels and frozen noise seeds. |
| Sealed confirmatory | Fixed SNR levels and frozen noise seeds selected before model freeze. |

Validation, dev-test, and sealed noise seeds must be stored in the dataset manifest and must not be altered after split creation.

#### Sensor-level vs coherent interference

- White, colored, and tonal interference are added as sensor-level waveforms. They are incoherent across channels unless a specific spatial-correlation model is declared and justified.
- Acoustic interferers have propagation structure and must be generated by a separate BELLHOP run (or multi-channel recording) before being added to the target observation.
- Real-noise augmentation, if used, must preserve any spatial coherence present in the recording.

#### SNR-dependent masking for Stage 1 per-channel encoder

- During Stage 1 SSL training, each single-channel view is augmented with **time-frequency masking** applied per 512 ms IQ frame (or per 64 ms STFT frame) whose probability depends on the example-wide in-band SNR:
  - Clean / 20 dB: mask ratio `0.10–0.25`;
  - 10 dB: mask ratio `0.25–0.40`;
  - 0 dB: mask ratio `0.40–0.60`;
  - -5 dB: mask ratio `0.50–0.70`.
- Masking is applied to the noisy waveform independently of the additive-noise realization.
- The masking pattern is random per epoch and does not break phase continuity within unmasked regions.
- Masking is **not** applied to the array encoder or Stage 4 fine-tuning unless explicitly ablated.

### 8.2.5 Stratification and Minimum Coverage

Every generated dataset must satisfy the following coverage rules. A dataset that violates them is invalid for training or reporting.

| Stratum | Minimum examples per cell (full) | Minimum examples per cell (pilot) |
|---|---:|---:|
| `(geometry, environment)` | `30` | `10` |
| `(geometry, environment, azimuth-sector)` | `5` | `2` |
| `(geometry, environment, source-family)` | `5` | `2` |
| `(geometry, environment, SNR-regime)` | `5` | `2` |
| `(geometry, environment, range-bin)` | `5` | `2` |

SNR-regime cells are generated from the same BELLHOP channel config by post-hoc noise overlay and therefore do not increase the number of BELLHOP runs.

Global balance:

- Equal total examples per train geometry (ULA-5-H and L-5).
- Equal total examples per source family within `±10%` after weighting by family weight.
- Equal total examples per SNR regime within `±10%`.
- No cell with zero examples in any stratification table used for reporting.

### 8.2.6 OOD and Stress Panels

In addition to the joint-stress dev-test, generate the following controlled panels:

| Panel | Changed factor | Held-constant factors | Size |
|---|---|---|---|
| Environment-only | 1 held-out environment | ULA-5-H, train families, train ranges, 10 dB SNR | `~1,000` |
| Geometry-only | Square-4 only | 1 held-out environment, train families, train ranges | `~1,000` |
| Source-family-only | 1 held-out family | ULA-5-H, 1 held-out environment, train ranges | `~1,000` |
| Range-only | Very-far bin `700–1200 m` | ULA-5-H, 1 held-out environment, train families | `~1,000` |
| Azimuth-irregular | random angles in `[-70, +70] deg` not on 2.5° grid | ULA-5-H, 1 held-out environment, train families | `~1,000` |

These panels are part of dev-test and may be used for diagnostic reporting and factorial OOD decomposition.

## 9. Models Under Test

### 9.1 Model-Family Scope

The full-model ladder in `docs/research/framework/architecture.md` Section 8.12 defines five rungs: Tiny, Small, Base, Large, and XL. The parameter ranges in that ladder refer to the full trainable stack: shared per-channel encoder, geometry-conditioned array encoder, heads, and any optional SSL/VAE branches. This protocol uses only the first two full-model rungs and follows the per-channel encoder caps in Section 8.12.1.

**In scope for MVP:**
- **Tiny (1-5M full-model parameters; 0.5-2M per-channel encoder):** IQ-only TCN or lightweight CNN. Intended for fast debugging, sanity checks, and hardware throughput tests. Not a primary scientific target.
- **Small (5-30M full-model parameters; 2-8M per-channel encoder):** IQ+STFT CNN+TCN frontend with a geometry-aware pairwise Transformer. This is the main MVP target.

**Explicitly deferred (not in MVP):**
- Base (30-120M parameters, Conformer-lite SSL backbone);
- Large (120-500M parameters, hybrid VAE+SSL);
- XL (500M+ parameters, research-only);
- JEPA, DINO, wav2vec, HuBERT, and Mamba backbones;
- Stage 3 predictive latent dynamics.

No model above the Small rung may be trained or reported as part of this MVP. If Tier 0 gates fail, do not rescue by scaling to Base or Large.

### 9.2 Allowed MVP Variants

Within the Tiny and Small rungs, the following variant configurations are permitted:

1. **Tiny supervised/IQ TCN**
   - single-channel IQ input only;
   - compact TCN or 1D CNN backbone;
   - no geometry input;
   - purpose: fast convergence test and pipeline validation.

2. **Small IQ+STFT CNN+TCN with geometry-aware pairwise Transformer**
   - dual-branch frontend: IQ analytic signal and STFT real+imaginary channels;
   - CNN+TCN encoder per channel;
   - pairwise geometry features and sensor coordinates fed into a lightweight Transformer;
   - no learned slot-index embeddings;
   - sensor availability mask required;
   - primary proposed model for MVP.

3. **Small IQ-only ablation**
   - same backbone as the primary Small model;
   - only the IQ/analytic-signal input branch is used;
   - STFT branch is removed;
   - purpose: isolate the contribution of the STFT branch.

4. **Small STFT-only ablation**
   - same backbone as the primary Small model;
   - only the STFT real+imaginary input branch is used;
   - IQ branch is removed;
   - purpose: isolate the contribution of the IQ branch.

5. **Optional VAE branch ablation**
   - same frontend and encoder as the Small variant;
   - adds a variational bottleneck (KVAE-inspired) on top of per-channel or array-level latents;
   - must run alongside the non-VAE Small variant to isolate VAE contribution;
   - not required for the primary MVP claim.

6. **Optional SSL branch (MVP-safe augmentations only)**
   - Stage 1: masked single-channel latent modeling on IQ/STFT;
   - Stage 2: masked sensor latent prediction with geometry metadata;
   - augmentations must be phase-safe and preserve inter-channel delay and amplitude ratios;
   - excluded augmentations: time warping that distorts inter-channel phase or group-delay structure, independent per-channel gain that breaks coherence, phase randomization that destroys group-delay structure;
   - if unsafe augmentations are used, the run must be reported as a non-MVP ablation.

### 9.3 Input-Format Ablation Matrix (Tier 0, mandatory)

The primary Small model uses both IQ and STFT branches. The following matrix uses the **same backbone** and `full` geometry mode, varying only the input representation. All rows are mandatory for claims about input representation.

| Ablation | Input branches | Geometry input | Purpose |
|---|---|---|---|
| **IQ-only** | IQ analytic signal, 512 ms frames | full | Tests whether IQ alone is sufficient. |
| **STFT-only** | STFT real+imaginary, 64 ms windows | full | Tests whether STFT alone is sufficient. |
| **IQ+STFT** | both branches | full | Primary proposed input representation. |

The IQ-only and STFT-only ablations use the same encoder capacity and the same `full` geometry conditioning as the primary IQ+STFT model; only the input branch is removed. This makes the input-format effect causally identifiable.

### 9.4 Coordinate-Conditioning Ablation Matrix (Tier 0, mandatory)

The primary MVP claim is about geometry conditioning. The following matrix uses the **same backbone** and varies only geometry input. All rows are mandatory for the geometry-transfer claim.

| Ablation | Coordinate input | Pairwise features | Purpose |
|---|---|---|---|
| **Classical baselines** | N/A | N/A | MVDR, MUSIC, SRP-PHAT, Bartlett as bounds. Not geometry-conditioned. |
| **No-geometry baseline** | none | none | Tests whether geometry metadata matters at all. |
| **Coordinates-only** | raw `x,y,z` | none | Tests raw coordinate conditioning. |
| **Pairwise-only** | none | distances/directions/RBF | Tests relational geometry without raw coordinates. |
| **Full geometry** | raw `x,y,z` | distances/directions/RBF | Primary proposed geometry conditioning. |
| **Shuffled-coordinates** | permuted raw + pairwise | permuted pairwise | Permutation canary; must not change predictions. |

### 9.5 SSL/VAE Ablation Matrix (Tier 1, exploratory)

SSL and VAE are optional exploratory branches. They may not be used to support the primary geometry-transfer claim, only a separate SSL/VAE claim. These rows are mandatory only if that separate claim is made.

| Ablation | Geometry input | SSL pretraining | VAE branch | Purpose |
|---|---|---|---|---|
| **Supervised-from-scratch** | full | none | none | Non-SSL reference for label-efficiency claims. |
| **SSL-only** | full | Stage 1+2 | none | Tests SSL contribution without variational complexity. |
| **VAE-only** | full | none | yes | Tests variational bottleneck without SSL objectives. |
| **Hybrid SSL+VAE** | full | Stage 1+2 | yes | Tests combined contribution; must improve over both SSL-only and VAE-only. |
| **Head-only probe** | full | frozen SSL backbone | optional | Tests how much of SSL benefit is in the backbone vs the head. |

All ablations must use the same train/validation/dev-test split, chunk duration, sampling rate, SNR/SIR conditions, and primary metrics defined in this protocol. A result may not be reported as supporting a claim unless the corresponding ablation row has been run and reported.

### 9.6 Tier 0 Baselines

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

### 9.7 SSL Scope

SSL scope:

- Stage 1 SSL objective: masked single-channel latent/feature modeling on `12 kHz` IQ and STFT branches;
- Stage 2 SSL objective: masked sensor latent prediction using Stage 1 per-channel encoder outputs plus geometry metadata;
- Stage 4 supervised heads: DOA regression, angular probability map, and diagnostic source presence;
- Stage 3 latent dynamics: excluded from MVP and evaluated only after Tier 0 gates pass;
- Tier 2 objectives and backbones: no DINO/JEPA/wav2vec/HuBERT/Mamba in MVP.

### 9.8 Stage-wise Execution Order

Stage-wise execution order:

1. Run supervised-from-scratch baselines first to establish a non-SSL reference.
2. Train Stage 1 SSL single-channel encoder on channel views extracted from the BELLHOP training array examples, without DOA labels and without treating hydrophones from the same array scene as independent split units.
3. Freeze or EMA-stabilize the Stage 1 encoder, then train Stage 2 masked-sensor SSL on full array examples with geometry metadata.
4. Attach Stage 4 heads and evaluate head-only probing, adapter tuning, and full fine-tuning under `10%`, `50%`, and `100%` label budgets.
5. Compare against no-SSL and no-geometry ablations before making any SSL or geometry-transfer claim.

### 9.9 Stage-wise Data Usage

Stage-wise data usage:

| Stage | Training unit | Uses `~120k` train array examples? | Label use | Notes |
|---|---|---:|---|---|
| Supervised baseline | array example | yes | DOA labels | Establishes no-SSL reference before SSL claims. |
| Stage 1 SSL | single-channel view extracted from array example | yes, expanded to channel views | no DOA labels | A 5-channel geometry gives `5` views per array example; a 4-channel geometry gives `4` views; split identity remains the parent array scene. |
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
| GCC-PHAT / PDOA | broadband comparator | pairwise phase difference per frequency, then least-squares azimuth fit; frequency aggregation must be frozen |
| SRP-PHAT | primary broadband comparator | azimuth grid `[-70, +70]` with `1 deg` resolution |
| PDOA-only estimator | short-baseline physics baseline | phase-difference of arrival across sensor pairs, using `sin/cos` or complex-ratio representation |
| Bartlett MFP | hydroacoustic physics baseline | if BELLHOP replica fields can be generated for the same environment |
| Oracle-environment MFP | privileged upper bound | reported separately, never as equal-information baseline |
| Cramér–Rao lower bound (CRLB) | theoretical lower bound | free-field single-path reference; optional BELLHOP-derived multipath bound; not a competitor |

For the short-baseline array in this protocol, the **PDOA-only estimator** is the most direct physics baseline. GCC-PHAT should be implemented with frequency-dependent phase information rather than a single broadband TDOA, and the frequency aggregation policy must be frozen and reported.

The **CRLB** must be reported as a theoretical reference. For a uniform linear array with `N` sensors, spacing `d`, wavelength `λ`, source azimuth `θ` measured from broadside, `K` snapshots, and per-snapshot SNR `ρ`, the narrowband stochastic CRLB is:

```
CRLB(θ) = 6 / ( K ρ N (N² - 1) (2π d cos θ / λ)² )
```

For broadband sources, pool per-frequency bounds via inverse variance:

```
CRLB_broadband(θ) = 1 / Σ_f [ 1 / CRLB(θ, f) ]
```

Report CRLB as a function of azimuth, frequency band, and SNR; do not present it as a baseline that the proposed model must beat.

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

**Fine-tuning data sampling:** Pre-training and fine-tuning must use cluster-aware sampling to prevent head-condition dominance. Cluster at the level of signal family × SNR regime × BELLHOP environment family. Assign cluster-level sampling weights; head clusters are down-weighted and tail clusters are up-weighted. Within each cluster, use domain-aware sampling to balance sub-domains (e.g., clean vs. noisy vs. interfered vs. real-noise-augmented; synthetic vs. recorded). This is especially critical for 10% and 50% label-budget experiments, where a small labeled subset can be severely skewed without explicit cluster-level balancing.

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

CRLB-relative metrics:

- `sqrt(CRLB(θ))` in degrees, median and 95th percentile over the test azimuth grid;
- `RMSE / sqrt(CRLB(θ))` efficiency ratio per geometry, frequency band, and SNR;
- percentage of test conditions where median angular error is within `3 dB` of the CRLB bound (`≤ sqrt(2 * CRLB)`);
- explicit flag when measured error falls below the CRLB, indicating bias, inconsistent SNR estimate, or incorrect CRLB assumptions.

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
- azimuth sector: `[-70,-50]`, `[-50,-30]`, `[-30,0]`, `[0,30]`, `[30,50]`, `[50,70]`;
- SNR/SIR;
- clean/noisy/interfered;
- source range bins: `50-150 m`, `150-400 m`, `400-700 m`, `700-1200 m`.

### 12.1 Statistical Unit Of Inference

Because examples are nested in environments and channel configs, the **BELLHOP environment** is the upper unit of inference.

- **Paired hierarchical bootstrap:** resample environments, then channel configs, then examples, all with replacement. Model seeds are crossed with environments, not averaged within environment.
- **Primary endpoint:** median angular error on the sealed held-out geometry (Rect-5).
- **Effect estimator:** paired difference between the geometry-conditioned model and the matched no-coordinate model within the same environment/channel-config/example triple.
- **Power analysis:** the pilot must estimate the minimum detectable effect (e.g., `10%` relative improvement in median angular error) and the required number of environments. The final channel-bank size must achieve `80%` power for that effect at `α = 0.05`.
- **Confidence intervals:** report bootstrap `95%` CI for the primary endpoint and for the paired difference. A claim of improvement requires that the CI for the paired difference excludes zero and is separated from the no-geometry baseline CI.

### 12.2 Factorial OOD Decomposition

The joint randomized test is decomposed into panels so that failures can be attributed to a single factor:

| Panel | Changed factor | Held-constant factors |
|---|---|---|
| Environment-only | BELLHOP environment | ULA-5-H geometry, train source families, train ranges |
| Geometry-only | Geometry (sealed Rect-5) | One held-out environment, train source families, train ranges |
| Source-family-only | Source family | ULA-5-H geometry, one held-out environment, train ranges |
| Range-only | Source range bin | ULA-5-H geometry, one held-out environment, train source families |
| Joint-stress | All factors simultaneously | Diagnostic only; reports composite robustness. |

## 13. Mandatory Gates

The gates in this section are the MVP-specific instantiations of the framework-level phase-preservation and interpretability gates defined in Section 21 of the evaluation specification. Each MVP gate maps to a framework gate as noted below.

### 13.1 Data And Simulator Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| BELLHOP convergence | Section 6.4 thresholds pass on 5-environment sample | stop dataset generation |
| PDOA/IPD preservation | direct-path diagnostic recovers inter-channel phase difference within the frequency-dependent tolerance in Section 13.4 | fix preprocessing/IR construction |
| Metadata completeness | `100%` examples have required metadata fields | block training |
| Leakage audit | no environment/source/noise seed appears in multiple splits; sealed test not accessed before freeze | regenerate splits; invalidate non-confirmatory claims |

### 13.2 Geometry Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| Permutation canary | shuffled channel order changes median angular error by `< 0.1 deg`, relative probability-map NLL by `< 1%`, and absolute NLL by `< 0.01` | block Stage 2/downstream reporting; see framework permutation canary gate (Section 21.6) |
| No-geometry comparison | geometry-conditioned `full` model improves sealed held-out geometry median angular error by at least `15%` relative to matched `no-coordinate` baseline | do not claim geometry transfer |
| Coordinates-only comparison | `coordinates-only` model improves sealed held-out geometry over `no-coordinate`; `full` does not underperform `coordinates-only` by more than `10%` | do not claim benefit from pairwise features |
| Pairwise-only comparison | `pairwise-only` model improves sealed held-out geometry over `no-coordinate` | do not claim pairwise geometry benefit |
| Changed aperture | degradation from ULA-5-H to ULA-5-shifted is `< 25%` relative median angular error increase | mark transfer partial |
| Missing sensor diagnostic | random one-sensor dropout increases median error by `< 50%` | mark missing-sensor robustness unsupported |

### 13.3 Baseline Gates

| Gate | Pass threshold | Failure action |
|---|---|---|
| Classical competitiveness | proposed model beats or matches MVDR/Capon and MUSIC within `10%` median angular error under matched information | do not claim competitive DOA performance |
| PDOA-only competitiveness | proposed model beats or matches the PDOA-only physics baseline within `10%` median angular error on clean examples | flag that the neural model does not improve over direct phase-difference estimation |
| SRP-PHAT comparison | proposed model beats SRP-PHAT by `>= 10%` on noisy/interfered subsets or reports where it loses | claim only partial |
| Seed reliability | direction of improvement holds in at least `4/5` random seeds | mark result preliminary |

### 13.4 Phase-Preservation and Interpretability Gates

These gates instantiate the framework-level definitions from Section 21 of the evaluation specification with MVP-specific thresholds, adapted to the short-baseline PDOA/IPD regime.

**Frequency-dependent phase tolerance.** The timing-equivalent bound is `τ_max = 3 μs`. The phase tolerance per frequency is:

```
ε_φ(f) = 2π f τ_max
```

For the MVP operating band:

| Frequency | ε_φ(f) |
|---|---:|
| 500 Hz | 0.009 rad |
| 1000 Hz | 0.019 rad |
| 2000 Hz | 0.038 rad |
| 3000 Hz | 0.057 rad |

| Gate | Framework reference | MVP pass threshold | Failure action |
|---|---|---|---|
| PDOA/IPD recoverability | Section 21.2 | circular mean absolute IPD error below `ε_φ(f)` for `≥ 90%` of frequency bins; worst-bin error below `2 * ε_φ(f)` on direct-path diagnostic set | block Stage 2 training and downstream reporting |
| Phase increment consistency | Section 21.3 | circular mean absolute phase increment error `< 0.2 rad` on clean CW and chirp examples | reject encoder configuration |
| Pairwise coherence preservation | Section 21.4 | Pearson correlation between input and latent-derived pairwise complex coherence `> 0.85` on clean examples across operating band | block array-encoder training |
| Calibration perturbation sanity | Section 21.5 | paired calibration-lite examples: sign of latent-derived IPD change matches injected analytical change for `≥ 80%` of affected pairs; magnitude ratio in `[0.5, 2.0]` for `≥ 80%` of affected pairs; affected-pair median change `≥ 2×` unaffected-pair median change; paired bootstrap `95%` CI excludes zero | flag calibration-invariant shortcuts; block geometry-transfer claims |
| Permutation canary | Section 21.6 | shuffled channel order changes median angular error by `< 0.1 deg`, relative probability-map NLL by `< 1%` using `abs(NLL_shuffled - NLL_original) / max(abs(NLL_original), 1e-6)`, and absolute NLL delta by `< 0.01` | block all Stage 2 and downstream reporting |
| Early-pooling interface ablation | Section 21.7 | early-pooling ablation is not more than `25%` worse than unpooled representation on median angular error | reject early fixed-vector pooling as default interface; does not block the main unpooled path |

### 13.5 SSL-Specific Gates (Tier 1, optional)

These gates apply only if a claim about SSL pretraining is made.

| Gate | Pass threshold | Failure action |
|---|---|---|
| 50% label efficiency | SSL-pretrained model at 50% labels is within `5%` of 100% supervised-from-scratch median error or improves over 50% supervised-from-scratch by `>= 10%` | do not claim SSL label-efficiency benefit |
| Head-only probe | frozen SSL backbone with head-only tuning is non-inferior to full fine-tuning within `15%` median angular error | do not claim representation reuse benefit |

## 14. Kill / Pivot Criteria

Pause architecture expansion and report a negative or partial result if any of the following hold:

1. permutation canary fails;
2. geometry-conditioned `full` model does not improve sealed held-out geometry transfer over matched `no-coordinate` baseline by at least `15%`;
3. proposed model loses to both MVDR/Capon and MUSIC under matched information;
4. sealed test has fewer than `10` successful held-out BELLHOP environments;
5. sealed-test median error variance is so high that the best model's 95% confidence interval overlaps the no-geometry baseline;
6. BELLHOP convergence or PDOA/IPD preservation gates fail;
7. calibration perturbation sanity fails (blocks geometry-transfer claims only).

SSL-specific kill criteria (apply only if an SSL claim is made):

1. SSL pretraining fails the 50% label-efficiency gate;
2. head-only probe fails the non-inferiority gate.

If a Tier 0 kill/pivot criterion triggers, do not add Stage 3, DINO/JEPA, Mamba, wav2vec/HuBERT, or larger backbones as a rescue step. First report the failure and isolate whether the blocker is simulation construction, preprocessing, geometry modeling, baseline strength, or SSL objective choice.

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
- frequency-grid convergence report;
- PDOA/IPD preservation report;
- permutation-canary report;
- leakage-audit report;
- sealed-test access log (see Section 15.1 for required fields);
- hierarchical-bootstrap and power-analysis report;
- factorial OOD decomposition report;
- baseline configs and tuned hyperparameters;
- metrics tables with per-seed and per-environment results;
- failure-case table;
- compute report: parameter count, memory, preprocessing time, inference latency, hardware.

### 15.1 Sealed-Test Access Log Format

The sealed confirmatory test must be accessed only after the model configuration is frozen. Every access must be recorded in a single append-only log file (e.g., `sealed_test_access_log.yaml` or `sealed_test_access_log.csv`) with the following fields:

| Field | Required | Description |
|---|---|---|
| `access_id` | yes | monotonically increasing integer or UUID |
| `timestamp_utc` | yes | ISO 8601 timestamp of the access |
| `model_version` | yes | commit hash or tag of the model/repository |
| `protocol_version` | yes | commit hash or tag of the canonical protocol |
| `frozen_config_hash` | yes | hash of the frozen architecture, hyperparameter, and preprocessing config file |
| `reason` | yes | why the sealed test was opened (e.g., "final evaluation of frozen Small full-geometry model") |
| `claim_supported` | yes | which claim this access is intended to support (e.g., "geometry transfer on Rect-5") |
| `metrics_file` | yes | path to the sealed-test metrics file produced by this access |
| `decision_triggered` | yes | `none` or a description of any architecture/hyperparameter decision triggered by this result |
| `regenerate_sealed_test` | yes | `true` only if the sealed test was regenerated; must be `false` for confirmatory access |

Rules:

- The log must be append-only; no entry may be deleted or edited after creation.
- If `decision_triggered` is not `none`, the corresponding result is exploratory and may not be reported as confirmatory evidence.
- If a sealed test is accessed before the model configuration is frozen, the access must be recorded and the result must be labeled as exploratory.
- The final confirmatory access must have `decision_triggered = none` and `regenerate_sealed_test = false`.

## 16. Reporting Rules

The report must use this claim status vocabulary:

- `supported`;
- `partially supported`;
- `not supported`;
- `not yet evaluated`.

Mandatory limitation statement:

> This experiment is BELLHOP-only and simulation-stage only. It does not demonstrate real-world hydroacoustic performance, BELLHOP-to-real transfer, or operational Novik Bay readiness.

Minimum report tables:

1. main model vs baselines (sealed-test);
2. classical baselines (sealed-test);
3. coordinate-conditioning ablations (sealed-test);
4. SSL/VAE ablations (dev-test or sealed-test, depending on claim);
5. geometry transfer (dev-test and sealed-test);
6. label efficiency (dev-test or sealed-test);
7. noise/interference robustness (sealed-test);
8. factorial OOD decomposition (sealed-test);
9. CRLB comparison: free-field single-path bound and optional BELLHOP-derived multipath bound vs measured RMSE per geometry/SNR (sealed-test);
10. held-out BELLHOP environment spread;
11. compute and latency;
12. claim-to-evidence scorecard;
13. failed/partial/not-yet-evaluated claims.

Dev-test results must be clearly labeled as exploratory. The primary MVP claim must be supported by sealed-test results only.
