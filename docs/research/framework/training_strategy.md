# Training And Adaptation Strategy

> This document specifies the minimum training and adaptation decisions for the [authoritative roadmap](roadmap.md) and the [winter field protocol](../../experiments/winter_field_protocol.md). It is a prospective protocol: no data access, feasibility gate, model run, or result has occurred merely because it is described here.

## 13. Training Strategy

### 13.1 Minimum supervised path

The minimum path trains exactly a compact supervised neural pair on the same permitted development distribution:

- a coordinate-aware complex-STFT model using the measured/simulated linear-array coordinates; and
- a matched no-coordinate twin with the same inputs apart from coordinate-derived information.

Both produce one single-source azimuth estimate in the same surveyed identifiable sector. The source half-plane/sector prior, calibration access, classical-method inputs, loss definition, optimization budget, and stopping rule are shared. MVDR/Capon and MUSIC are required comparisons, while Bartlett is diagnostic. The neural pair is not a claim of broad SOTA superiority.

Before the 2026-11-15 analysis freeze, a local feasibility run measures the selected compact model's runtime, memory, and practical per-run compute. That measured envelope fixes the architecture and training cap. The planning target is **three paired seeds for each neural model**, using matched seed assignments so the coordinate contrast can be analysed pairwise. If the measured budget cannot support that target, the failure action is an explicit supervisor-approved reduction or amended inference scope before final testing—not unreported seed removal or a larger-model rescue.

The primary front end is **Re/Im STFT**, with the tensor interface, coherent processing, and phase/delay safeguards defined in [architecture §8](architecture.md#8-input-representation-strategy). The physical band, sample rate, STFT parameters, sensor coordinate convention, and model budget must be bench-validated and frozen by 2026-11-15. No fixed frequency band, SNR grid, parameter-count band, effect threshold, or requirement to train every size is mandated here. The broader representation catalogue does not leave the core input or its parameterization open to result-driven replacement.

The selected common channel encoder is the hybrid complex Conv2D stem plus real Conformer-like temporal blocks and local frequency mixing in [architecture §9.1](architecture.md#91-shared-model-contract). It preserves a real feature/time-frequency grid until separate Fusion. Start with full, potentially bidirectional temporal attention inside each bounded observation window, separately per frequency position; sliding input crops do not imply sliding-window attention. The coordinate-aware/no-coordinate pair uses the same configuration, without a CNN-first prerequisite or an added architecture-comparison arm. The feasibility run must exercise the complete complex-stem/real-block forward and backward path at the intended shapes and attention backend, not infer its cost or phase behaviour from speech models.

The [E-S/E-M/E-L engineering presets](architecture.md#913-engineering-size-presets-and-single-size-selection) define candidate widths/depths, not three compulsory fits. Start the resource and full-encoder phase/delay pilot with **E-M**; use E-S if E-M does not fit the measured resource envelope, while E-L remains a separately justified development reserve, not a larger-model rescue. Freeze one preset and its complete configuration by 2026-11-15 and before comparative pretraining. That same size and output width serve the core pair, all five optional pretraining variants, and downstream `0`. Any resource comparison among presets keeps the physical input window, representation, attention policy and non-size processing choices matched or explicitly reports differences.

The initial E-M pilot candidate uses **`C=96`, `F_e=F`, `T_e≈T/2`**: test moderate temporal subsampling in the complex stem before considering frequency-axis reduction. This is not a frozen stride or a claim of phase/delay preservation. Specify exact output sizes, position alignment, and raw-sample support from the declared kernels, strides, and padding/boundary handling, then accept or revise the candidate under the full-encoder phase/delay and measured-resource gates. No compulsory full-resolution comparison or output-form/resolution-by-pretraining matrix is added.

The selected [coordinate-aware channel-attention Fusion](architecture.md#102-array-aggregation-requirements) is a shared part of the supervised core and all optional Stage 2 regimes, not another architecture factor. The initial E-M Fusion uses one pre-LayerNorm block, `C=96`, four heads and FFN `96 -> 192 -> 96`, independently at each retained `(f,t)`. Shared coordinate and physical-frequency encodings enter the tokens before Q/K/V projection; masked sensor pooling precedes valid-TF pooling. The no-coordinate twin keeps the structure and frequency encoding but supplies a constant zero coordinate input to `g_r`, with no topology, mirror-pair or slot shortcut.

Freeze the geometry-reference rule, fixed physical length/frequency scales, coordinate/frequency MLP configuration, frequency-position mapping, mask/empty-input handling and full Fusion implementation before comparative downstream training. Learn Fusion jointly through the selected [single-azimuth vector head and supervised MSE](architecture.md#12-downstream-heads); this does not prescribe an extra geometry loss, pretrained Fusion, angular grid or curriculum. Include the complete encoder/Fusion/head forward/backward/inference path in the phase, permutation and resource gates. Different sensor counts or coordinate inputs do not establish generalization: geometry transfer remains the existing optional study, without automatically importing the published methods' geometry-training curricula.

The common head maps the pooled `[N,C]` features through `Linear(C,C) -> GELU -> Linear(C,2)` and predicts raw `(a,b)` for target `(cos(theta),sin(theta))` in the declared coordinate frame. Optimize the batch mean of per-example **sum** of squared component errors, without output normalization or a separate angular/spectrum loss; decode only at inference with `atan2(b,a)` if both components are finite and their norm exceeds the predeclared numerical degeneracy threshold. Record and freeze that threshold before sealed scoring; a degenerate vector is a failure, not a zero-degree answer. Hold the head, labels, reduction and failure rule identical for the matched pair and any optional Stage 2 regimes. The primary circular angular error remains an **evaluation measure**, not the optimization loss.

### 13.2 Independent-unit and access discipline

Simulation environments are the simulation inference units. Field deployment/session/day blocks are real acquisition groups; repeated transmissions, bearings, bursts, and overlapping clips do not become independent replicates. Multiple independently acquired field groups are an acquisition target where safe and practicable, not guaranteed statistical power. One usable session permits only appropriately descriptive, bounded conclusions.

The default sim-to-real track is immutable **zero-shot**:

| Material or action | Immutable zero-shot track |
|---|---|
| Simulated development data | Permitted for training, normalizer fitting, simulator development, and model selection as frozen by protocol |
| Real development groups | Not used |
| Sealed real test groups, including unlabelled clips and noise-only recordings | Never used for training, normalizers, simulator tuning, SSL, augmentation selection, early stopping, or model selection |
| Calibration | Frozen separately and supplied identically to all compared methods |

Real-noise overlay on a simulated source is not real-data validation. The [winter field protocol](../../experiments/winter_field_protocol.md) governs manifests, acquisition groups, calibration, raw-data immutability, and the access ledger. The analysis and evaluation documents govern the final test lock; this training document must not create a competing split or data-access exception.

### 13.3 Training safeguards

The model pair must use the same supervised target, source sector/half-plane prior, permissible training material, and reporting units. Each run records the frozen configuration, code/data version identifiers when implementation exists, random seed, resource use, and any allowed adaptation access. The coordinate-aware arm is compared directly with its seed-matched no-coordinate twin; an unpaired average over arbitrary runs is not a substitute.

The following safeguards are blocking conditions for interpreting a neural coordinate effect:

1. **Phase integrity:** preprocessing, the complete hybrid channel encoder, and aggregation retain recoverable controlled relative delay, phase, coherence, and timing information. Checking the complex stem alone is insufficient. Independent per-channel phase randomization, random time shifts, or per-channel normalization are not generic augmentations.
2. **Joint permutation canary:** jointly reordering channel signals, coordinates, calibration fields, and masks leaves the model output unchanged to the predeclared reporting resolution.
3. **Coordinate association canary:** detaching or permuting coordinate fields while the signal channels remain fixed is a predeclared diagnostic for signal-coordinate association. It does not authorize tuning on sealed real data.
4. **No-coordinate isolation:** the twin has no coordinate-derived, topology-label, or stable channel-slot shortcut.

A failed safeguard stops the associated inference. It is not repaired by adding SSL, a larger model, more heads, or an unplanned architecture sweep.

### 13.4 Optional adaptation and representation studies

Encoder pretraining, scene/world-model dynamics, CWT sweeps, multi-head learning, model ladders, and broad adaptation menus are **not** part of the minimum. The accepted two-stage channel-encoder comparison in §13.5 is an optional E4 study, not a requirement or a completed result.

If and only if the minimum pipeline, labelled-data quality work, and writing milestones are safe, one bounded extension may be active at a time:

- **E1 — small real-development adaptation / label budget.** This is a separately declared adaptation track, not zero-shot evidence. It may use only explicitly released real development material and a fixed small labelled budget. Its ledger identifies every permitted file/group and every fit step. Sealed real groups, including unlabelled or noise-only clips, remain excluded from SSL, normalizers, simulator tuning, early stopping, and model selection. The unadapted zero-shot result remains immutable and reported separately.
- **E2 — controlled linear sensor-subset/spacing sensitivity.** This may use simulated linear layouts and, where a physically available subset of the measured field array is valid, a within-linear real sensitivity analysis. It is not a second physical geometry, a non-linear-array experiment, or arbitrary-topology transfer evidence.
- **E3 — modest measured ice/boundary or calibration sensitivity.** This is confined to a scientifically justified diagnostic beyond the core calibration/ice checks; it cannot convert an unvalidated simulator into an ice-physics claim.
- **E4 — one bounded study:** the two-stage channel-encoder comparison in §13.5, the primary Re/Im STFT versus one selected alternative front end, **or** arbitrary-topology **simulation-only** transfer. These are mutually exclusive alternatives. Baseband IQ is the first representation alternative; the real-valued waveform is the next control candidate, not a second automatically approved arm. The encoder study compares VAE, HuBERT-style, and JEPA task variants on a fixed transferable encoder and fixed Re/Im STFT input, then the complete DOA models against supervised training from scratch. It is not a representation/model sweep and does not replace the core supervised pair.

An extension needs an explicit hypothesis, access ledger, compute measurement, stopping rule, and comparison with the frozen minimum. It may begin only after core work is secure; no new extension begins after **2027-02-01**, and extension results freeze by **2027-02-15**. If field data arrive late or quality/access is insufficient, all extensions are dropped rather than displacing the minimum.

For a selected representation contrast, freeze one reference training regime and give each input the same permitted physical observations, target information, tuning access, and evaluation splits under [evaluation §17.5](evaluation.md#175-selected-input-representation-comparison). Declare necessary temporal versus time-frequency input-block differences and measured capacity/resources; the result is conditional on that regime and implementation. A supervised-from-scratch comparison does not add `0` to Stage 1 of the separate pretraining study. No automatic transfer of all five objectives, codebooks, decoders, or target constructions to IQ/real-waveform inputs is authorized. A larger representation comparison or a combined objective-by-representation study needs a pre-test scope/resource revision, not silent multiplication of the E4 matrix.

### 13.5 Two-stage channel-encoder pretraining study

The study separates **representation quality** from **usefulness for DOA**. Its method families are VAE, HuBERT-style, and JEPA. Within JEPA, A and B are alternative context/target tasks, not two mandatory algorithms; A+B combines their losses. A generic masked-JEPA example explains the principle but does not add another experimental variant.

| Stage | Compared regimes | What is trained and evaluated |
|---|---|---|
| **1 — channel representations** | **VAE, H (HuBERT-style), A, B, A+B** | Pretrain the same channel encoder; freeze it and fit matched small diagnostic probes. No full Fusion/DOA training and no supervised-from-scratch regime 0 here |
| **2 — downstream DOA** | The five pretrained variants **plus supervised from scratch (0)** | Jointly train encoder, Fusion, and one azimuth output under the common supervised contract; assess actual DOA benefit |

The same hybrid Conformer-like encoder from [architecture §9.1](architecture.md#91-shared-model-contract), **Re/Im STFT** input and preprocessing, real feature/time-frequency output shape, and channel-shared weights are used throughout. Its structural attention scope, positional convention, normalization, and subsampling are fixed across methods; H's training-only input masks do not select another backbone. Only the learned weights and declared pretraining auxiliaries differ. Coordinates enter the existing Fusion, not an encoder-specific sensor slot. Baseband IQ and the real-waveform control are representation candidates outside this five-method study, not additional inputs to each row. The core no-coordinate twin and classical comparisons remain unchanged; no coordinate-by-pretraining factorial sweep is added.

Stage 1 can be completed and reported independently, but its ranking is not proof of downstream benefit or completion of Stage 2. Do not silently send only its winning encoder to Stage 2: the planned downstream slate contains all five variants and control 0. Any eligibility failure or proposed narrowing is disclosed and governed by the stopping/revision rules below.

#### 13.5.1 Inputs, references, and phase contract

For sensor `m` and window `k`, write the observed simulated signal as `X[m,k] = D[m,k] + R[m,k] + N[m,k]`: noise-free direct arrival, coherent reflections, and declared noise/interference. Generate channels from one physical scene with consistent source realization, emission phase, geometry, delays, calibration, and clock. Independent random channel filters are not spatially coherent multipath. Component provenance and pair eligibility follow [data_and_simulation.md](data_and_simulation.md).

The initial five-variant comparison draws from the same registered simulated parent-scene/input pool. VAE, H, and B use observed signals; B additionally sees a future target during training. A and A+B consume simulator-derived direct references. These are **unequal target-information recipes**, not a pure loss-function comparison with equal teacher information. Angular labels are not consumed by pretraining, but the direct reference is privileged information.

Missing, invalid, or physically absent direct arrivals block that reference-dependent task's feasibility gate. Record rejected attempts and reasons without fabricating a target or narrowing the frozen core evaluation cohort. Adding noise to a real recording does not remove its original noise or reflections and cannot provide a direct-path reference.

Features must retain recoverable relative phase/delay information until Fusion; an independently phase-invariant channel bottleneck is not acceptable merely because its pretext loss is low. Use common timing and the coherent scaling/calibration rules of [architecture §8](architecture.md). Any common phase augmentation must act consistently across paired views and array channels, not independently rotate them and force equal codes.

The selected hybrid does not assert strict complex phase equivariance: its final coordinates are learned real features, not prescribed complex amplitudes. Assess relative phase/delay accessibility after the entire stem, temporal blocks, frequency mixing, and any normalization/subsampling. Arbitrary latent coordinates do not automatically have a physical phase interpretation. Neither successful reconstruction, clustering, nor temporal prediction guarantees denoising or wavefront recovery.

#### 13.5.2 Data tracks: strict simulation and declared real-assisted pretraining

**S — strict sim-only, the default.** Every fit uses permitted simulated development material only: encoder, target/teacher, decoder, codebook and descriptor scaling, normalizers, diagnostic probes, simulator tuning, checkpoint selection, and hyperparameters. No real development recording is used for fitting. Separately acquired instrument calibration and physical survey remain frozen inference inputs shared fairly across methods. Final simulated and real groups are excluded from all fitting and selection.

**R — optional real-assisted unlabelled pretraining.** This requires an explicit release of an actual, lawfully usable real development corpus, a group/file-level access ledger, and a resource decision within E4's existing total cap. It does not assume that such a corpus exists. Split sessions/deployments before windows, sensors, or views; another hydrophone or adjacent crop from the final session is not an independent training group.

B can use consecutive observed windows without clean references or DOA labels. VAE and H can also use unlabelled observations; this capability is not unique to B. A/A+B do not acquire direct targets from ordinary real recordings, and no real-reference or sequential hybrid variant is silently added. Record source-containing and noise-only material separately; learning backgrounds alone is not evidence of spatial feature learning.

Only explicitly released pretraining and auxiliary-fit operations are allowed in R. Preserve the S normalizers by default; any real-data normalization or H codebook/teacher fitting must be declared. R does **not** authorize fitting the propagation simulator to real scenes or using real angular labels for DOA fine-tuning. Target-domain real pretraining may be unsupervised domain adaptation; an unrelated real corpus may provide general acoustic pretraining. Neither is the strict S sim-only result, and neither is automatically E1 few-shot labelled adaptation.

The minimal optional data-source contrast is **B/S versus B/R**, with R using a preregistered simulated-plus-real mixture, paired initialization, a matched update budget, and the same diagnostic/downstream protocol. Report mixture, real duration/examples, all fitting access, and measured cost. This tests the declared data-source recipe, not superiority of the B objective. A comparison with real-assisted VAE/H requires explicitly matched real access; it is not an automatic multiplication of the method matrix.

Sealed final recordings, including unlabelled, background, source-off, and derived files, never become training data in either track. Diagnostic validation used to select methods remains **development** relative to Stage 2. Freeze the complete final method/seed/access/analysis slate before inspecting any final result. The immutable S result remains separately reported when R is selected.

#### 13.5.3 VAE: variational reconstruction of the observed channel

Use the fixed transferable encoder's real output grid as the posterior mean: `mu = E_theta(X)`. A training-only branch predicts `log(sigma^2)` from the same features. Define `q(z|X) = Normal(mu, diag(sigma^2))` over these real learned coordinates, with `z = mu + sigma * epsilon`, `epsilon ~ Normal(0,I)`. The final latent coordinates need not form complex pairs. A compact training-only decoder reconstructs the Re/Im coefficients of the **observed X**, not direct component D.

Minimize the standard negative ELBO: `L_VAE = mean_examples(E_q[-log p_decoder(X|z)] + KL(q(z|X) || Normal(0,I)))`. A Gaussian likelihood on real and imaginary coefficients gives squared reconstruction error with a declared fixed likelihood scale. Freeze that scale and the reduction convention: independently averaging reconstruction and KL over different dimensions must not silently reweight the objective. This is one classical VAE control, not a beta-VAE or denoising-VAE sweep.

Remove the decoder and variance branch for probes and downstream use. Transfer deterministic `mu = E_theta(X)`, not a sampled latent or an extra architecture-specific mean encoder. Record reconstruction, KL, and posterior/latent-use diagnostics; neither low reconstruction error nor KL alone establishes phase preservation or useful DOA features. The methodological reference is [Kingma & Welling](https://arxiv.org/abs/1312.6114).

#### 13.5.4 H: HuBERT-style masked discrete-unit prediction

The initial hydroacoustic adaptation uses a fixed local phase-bearing real/imaginary complex-STFT descriptor `T(X)_t` of the **observed** input and one offline K-means codebook. Fit descriptor scaling and centroids `v_j` on permitted pretraining material only; assign `c_t = argmin_j ||T(X)_t - v_j||^2`. Freeze the descriptor, cluster count, fit/selection rule, and mask design before diagnostic evaluation. A VAE/JEPA-pretrained teacher or iterative teacher sweep is not part of this initial control.

The same encoder sees masked input. A temporary classifier predicts the assigned unit labels with `L_H = -mean_{t in M} log p(c_t | masked X)`, where `M` is the declared scored mask. Mask the student's declared input support before the complex stem, subsampling, data-dependent normalization, or other contextual mixing; masking only after the Conformer or only in its attention scores is insufficient. Record span/position support and account for STFT overlap, filtering, and receptive fields so hidden target content cannot bypass the mask. Labels still come from the permitted unmasked descriptor path, not a second unmasked student-feature path. No DOA or sensor-identity label is a clustering target.

If a permitted signal augmentation changes phase-bearing descriptors, derive unit labels from the corresponding augmented but unmasked view before masking the student input. Reusing unchanged labels across independently rotated views would impose an undeclared invariance.

Transfer continuous encoder features, **not cluster IDs**. Discard the classifier and codebook from inference. Track cluster use, label imbalance, and representation diagnostics; complex descriptors and discrete targets do not guarantee retention of physical phase/delay.

[HuBERT](https://arxiv.org/abs/2106.07447) supplies the masked-unit learning principle. [GigaAM Multilingual](https://arxiv.org/html/2607.10371v1) is a speech-recognition application using mel input, a 600M-parameter Conformer and 2M hours of audio, not a phase-aware hydrophone validation. Its architecture, weights, cluster count, masking rate, and data scale are not project defaults.

#### 13.5.5 JEPA: shared mechanism and context/target variants

JEPA predicts **continuous learned target features**, not necessarily raw signals, future samples, or clean waveforms. In the adopted EMA construction, an online encoder and predictor receive gradients; a target copy supplies stop-gradient features and updates as `theta_bar <- rho * theta_bar + (1-rho) * theta`. The target is learned, not an oracle representation. [I-JEPA](https://arxiv.org/html/2301.08243v3) demonstrates the masked-block construction; masking is a way to define a task, not a requirement to add another variant here.

The EMA target is a copy of the same complete hybrid `E`, including its real Conformer stages and output interface, not a different complex encoder. Declare how normalization state is handled as well as the parameter EMA; no target-window statistics or signal cache may enter the online context path.

| Variant | Online context | Stop-gradient EMA target | Training-only predictor |
|---|---|---|---|
| **A** | `E_theta(X[m,k])` | `E_bar(D[m,k])`, same-window direct reference | `P_C` |
| **B** | `E_theta(X[m,k])` and physical `delta_t` | `E_bar(X[m,k+1])`, future **observed** window | `P_T` |
| **A+B** | Shared current-window online representation | Both targets above, with shared online and EMA encoders | Separate `P_C` and `P_T` |

Use a common squared distance over the final learned **real** feature coordinates: `dist(a,b) = (a-b)^2` elementwise, reduced over the declared valid components/positions. Define `L_C = mean(dist(P_C(E_theta(X[m,k])), sg(E_bar(D[m,k]))))` and `L_T = mean(dist(P_T(E_theta(X[m,k]), delta_t), sg(E_bar(X[m,k+1]))))`. Do not impose an undeclared complex pairing or interpret feature angles as physical phase. A+B uses `lambda_C * L_C + lambda_T * L_T`; it is not a single corrupted-present-to-clean-future objective.

Use one declared anti-collapse regularizer/weight across the JEPA variants, plus variance/covariance or rank diagnostics. Do not automatically impose this regularizer on VAE or H. EMA/MSE alone does not guarantee a non-collapsed or spatially useful representation. Freeze feature scaling, loss reductions, EMA schedule, regularizer, and bounded loss-weight selection on permitted development data; retain separate component losses.

In A, noise and multipath are coherent signal corruptions, not automatically token masks. Any position mask has a separately declared role. Direct-arrival recovery from one obscured channel is not generally identifiable, and successful latent prediction is not a denoising guarantee.

In B, `k+1` denotes the next defined window, not an unspecified one-sample step. Initial context/target raw support is disjoint, including STFT/filter support; record window, start time, hop, guard interval, and `delta_t`. The online encoder receives only the current context and the target encoder only the future observed window. Full bidirectional attention within each separately encoded window is allowed; concatenating the windows or encoding the full record and then slicing features is not. Convolution, data-dependent normalization, and persistent attention/signal caches must not bypass this separation. B predicts features rather than forcing adjacent codes to be equal. Temporal unpredictability of a waveform does not establish DOA unobservability, and temporal SSL is not scene-motion modelling.

[IQ-JEPA](https://arxiv.org/html/2607.22351v1) motivates complex representation learning but concerns masked multichannel medical ultrasound with simulated-data evidence. It does not validate these single-channel hydrophone tasks or establish a first use of complex JEPA.

#### 13.5.6 Stage 1: frozen representation evaluation

After each pretraining run, freeze E and fit matched small, fixed-capacity diagnostic probes. For relational tests, encode two sensors or controlled signal views independently, then provide their codes to a declared pairwise readout. This is a small spatial diagnostic, not the complete Fusion/DOA system and not an attempt to identify arbitrary DOA from one channel.

Use the same unmasked observed inputs for probe feature extraction; pretraining masks and auxiliary branches are inactive. Any diagnostic corruption is a common declared test condition, not a method-specific leftover from pretraining.

The common primary tasks recover relative phase and delay, with circular phase error, absolute delay error, coverage/failures, and independent-unit summaries specified in [evaluation.md](evaluation.md). Use the same probe architecture, fit data, budget, seed rules, and split policy for each corresponding task. Fit on the probe-training groups, select checkpoints/settings on named diagnostic development groups, and score on independent diagnostic reporting groups; no final DOA groups enter this process. Diagnostic data used for any model decision remain development relative to Stage 2. The B/S-versus-B/R contrast uses the same diagnostic corpus and readout protocol.

Start with controlled direct-path phase/delay cases, then assess robustness under justified noise, multipath, and calibration conditions. Observed-mixture and direct-reference phase/delay are distinct targets; declare which is scored and use common reference-validity rules. Do not interpret arbitrary latent arguments as physical phase. Reconstruction is secondary, not a main ranking favouring VAE; pretext losses across methods are not comparable scores. A weak probe shows limited accessibility to that readout, not proof that all information is absent. Rank/variance alone is not usefulness.

Stage 1 includes no compulsory full-model-from-scratch run. It measures representation properties and pretraining cost; it cannot establish final DOA improvement, field validity, or the need for pretraining.

#### 13.5.7 Stage 2: common supervised DOA training

Initialize Fusion and the azimuth head anew, transfer each deterministic pretrained E, and jointly train **E + Fusion + the one azimuth output**. There is no obligatory permanent encoder freeze or warm-up stage. All pretraining-only branches and Stage 1 probes are removed from the deployed estimator. Keep the core evidence-frozen vector target, raw-component MSE and `atan2`/degenerate-output contract of [architecture §12](architecture.md#12-downstream-heads), downstream observed label budget, preprocessing, independent groups, optimizer/schedule, calibration, and sector prior identical across the six regimes.

Control **0** uses the same full model trained from scratch, not another architecture. Reuse a core control only when architecture, data, preprocessing, optimization, seed pairing, provenance, and final-access conditions match. No result-driven retrospective addition to an already inspected confirmatory test is authorized. The unchanged core no-coordinate model remains a separate information ablation, not a seventh SSL regime.

Stage 2 uses the established DOA error/failure and independent-unit analysis. Stage 1's best probe score need not predict the best result after joint fine-tuning. Report negative outcomes and the effect of additional data/compute, not an assumed advantage for JEPA or A+B.

#### 13.5.8 Resources, completion, and stopping rules

The planning target remains three paired seed assignments per regime, subject to a measured gate. Pretraining, probe, and downstream assignments are recorded, not multiplied into an unplanned seed Cartesian product. Six downstream regimes at three seeds mean **18 total downstream fits**, not necessarily 18 additional fits beyond a reusable core control; pretraining, teacher/codebook generation, and probes cost extra.

Measure the enlarged study before launch. Match declared pretraining example/update budgets where the tasks permit and record different information access and auxiliary costs. Report reference availability, actual examples/windows, real-data mixture if any, updates, wall time, memory, and total pretraining/probe/fine-tuning resources. Equal architecture or update count is not equal compute.

Measure the common hybrid at the actual channel-window batch, retained frequency count, encoded temporal length, and attention implementation, including EMA/decoder/predictor overhead for the applicable variant. Local attention is not an automatic per-method cost reduction: any resource-driven change from the initial full within-window policy is documented during development, before comparative pretraining and the architecture freeze, and shared across the complete slate. It does not create a new E4 branch or permit result-driven backbone replacement.

Record the selected preset and exact implemented parameter count, including the phase/resource evidence behind the one-size decision. Shared-sensor weights do not create a separate parameter copy per hydrophone; more channel windows still increase work and activation storage. The full training footprint includes method-specific auxiliaries, so core-model fit alone does not establish E4 feasibility. Do not give only an expensive objective a smaller encoder: if the complete slate cannot fit the frozen size, defer the study or explicitly revise scope before testing under the existing rules. Presets do not multiply the planned six downstream regimes or their 18 total fits into a size-by-objective matrix.

The existing **five-focused-working-day total E4 cap** covers both stages and any approved R contrast; it is a scheduling stop limit, not a claim of feasibility. No new extension begins after **2027-02-01**; optional results freeze by **2027-02-15**. The optional stage order does not displace core preparation, the winter campaign, or writing.

Freeze the method/seed/access/analysis slate before final testing and record all failures. Invalid references, collapse, failed phase/delay gates, unavailable lawful real data, or insufficient resources require an explicit disposition. A missing R corpus leaves R unrun, not permission to borrow sealed recordings. If the complete study cannot fit, defer it or explicitly revise scope before testing; do not silently drop variants/seeds, promote a Stage 1-only report to full completion, add architectures, or change the core endpoint. Scene/world dynamics, tracking, and additional deployed tasks remain deferred.

---

## 14. Geometry Adaptation Protocol

### 14.1 Minimum nominal-array training and optional geometry transfer

The minimum trains and evaluates the compact methods for the measured linear configuration across independent simulated environments and justified calibration/measurement uncertainty. Its purpose is method accuracy, robustness, real-data domain shift and applicability limits. The coordinate/no-coordinate pair remains a component ablation; neither a positive coordinate effect nor transfer to a different layout is required for minimum completion.

If an optional E2/E4 geometry-transfer study is selected, preregister its held-out linear layouts/spacing or non-linear simulated topologies and match the methods' conditions and budget. A zero-shot geometry result requires exclusion of that target condition from training, normalization fitting, simulator tuning and selection. It supports only the stated simulation domain, does not resolve physical linear-array ambiguity, and cannot be promoted into real arbitrary-topology transfer by combining it with a fixed-array field result.

### 14.2 Bounded real-development adaptation track

E1 adaptation is optional and must remain separate from zero-shot. Before it starts, the protocol freezes:

- the released real development groups and their small label budget;
- permissible parameters to fit (for example, only a declared adaptation layer or output layer);
- whether any normalizer is refitted (default: no, unless the ledger explicitly permits it);
- compute and seed budget;
- the untouched real evaluation groups; and
- the comparison between adapted and immutable zero-shot results.

No held-out real material, including unlabelled/noise clips, may become an SSL corpus, normalization source, simulator-tuning set, or model-selection aid. Adaptation cannot be presented as a zero-shot result or as evidence of arbitrary-topology transfer.

### 14.3 Common-method conditions and reporting

Every geometry condition supplies the same surveyed source half-plane/identifiable sector to neural and classical methods. Coordinates, calibration, steering assumptions, and any far-field/range restriction are documented in the same array coordinate frame. A missing or unjustified sector means azimuth is structurally ambiguous and the claim must be amended rather than predictions clipped.

For each simulated or real condition, the report records:

- whether it is core S sim-only zero-shot, E1 labelled adaptation, E2 within-linear sensitivity, or E4; for the encoder study record stage, VAE/H/A/B/A+B or downstream 0, and S versus separately approved R access. Distinguish simulation, sim-only field transfer, and real-assisted field evaluation; E4 topology-transfer evidence stays simulation-only;
- the exact allowed data groups and fit operations;
- linear layout/spacing/subset condition and calibration status;
- model/seed pairing and measured compute use;
- all canary and phase-integrity outcomes; and
- the limitation that follows from the available independent units.

### 14.4 Decision gates

The 2026-10-15 hardware/field-feasibility gate determines whether the measured linear-array plan, source sector, synchronization, and positioning are viable. The 2026-11-15 freeze fixes the compact paired design and access policy after bench evidence. The first usable field recording may support development and QA; independently reserved groups are required for final real-data claims. If no usable labelled data or safe access exists by **2027-01-15**, the field lead and supervisor must immediately agree an explicit contingency and claim limit. Essential acquisition is targeted no later than **2027-02-15** without overriding safety; core data, models, tables, and experiments freeze by **2027-02-28**.

No gate guarantees an effect, a publication outcome, field access, or a degree. A null or limited result is reported within the evidence available rather than broadened through new architectures or an unplanned data route.
