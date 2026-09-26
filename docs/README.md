# Hydroacoustic DOA Dissertation Documentation

**Active planning baseline: 2026-09-19.** Candidate of Sciences dissertation; full text by **2027-03-31**. Real winter 2026–2027 under-ice recordings in a bay use **only a linear array**. Uniform spacing and exact apparatus/site are not yet confirmed. The published-article requirement is unresolved, not assumed to be zero or a particular count.

The repository is documentation-only. The following documents specify planned work and evidence requirements, not completed experiments.

## Start Here and Document Authority

1. **[Roadmap and success criteria](research/framework/roadmap.md)** — authoritative minimum M1–M5, optional E1–E4 studies, including E4's mutually exclusive two-stage channel-encoder comparison, one selected front-end comparison, or simulation-only topology choice; the selected front-end comparison is primary Re/Im STFT versus exactly one resource-approved alternative, normally baseband IQ.
2. **[Winter field protocol](experiments/winter_field_protocol.md)** — active preparation and acquisition protocol: linear-array ambiguity, underwater source truth, timing/calibration, safety ownership, QA, independent groups, held-out access, archive and contingencies.
3. **[Framework overview](research/framework/overview.md)** — scientific question, hypothesis limits, context and terminology.

The central dissertation result concerns the method, accuracy, robustness and limits on the measured linear array. Geometry-transfer studies are optional simulation work; omitting them does not make the minimum incomplete. Coordinate ablations and within-array subsets must not be promoted into proof of transfer to arbitrary physical geometries.

The numerical measurement/analysis settings are frozen from development evidence by 2026-11-15. Dates in the calendar are planning targets and never override professional field-safety decisions. A failed winter acquisition is a risk to the stated minimum, not permission to call simulated data real validation.
The selected core is a common hybrid Conformer-like channel encoder for the primary Re/Im STFT: a compact complex stem leads to lossless paired real/imaginary features, real temporal attention within each bounded input window while retaining frequency positions, then local frequency mixing; Fusion and the azimuth head remain separate. Its detailed configuration is evidence-gated before the freeze and is canonical in [architecture §9.1](research/framework/architecture.md#91-shared-model-contract), not a separate E4 architecture experiment.

The selected [coordinate-aware channel-attention Fusion](research/framework/architecture.md#102-array-aggregation-requirements) adds shared coordinate/frequency encodings before sensor attention at each TF position, followed by masked sensor and valid-TF means. The E-M pilot uses one block, four heads and FFN `96→192→96`; no-coordinate ablation uses a shared zero coordinate input. This is a core choice, not a ULA mirror-pair architecture or evidence of arbitrary-array transfer.

The selected [single-azimuth head](research/framework/architecture.md#12-downstream-heads) uses `C → C → 2`, supervised `(cos θ,sin θ)` targets and mean summed-component MSE. Decode finite nondegenerate outputs with `atan2(b,a)`; count invalid vectors as failures under the existing circular-error evaluation policy, without clipping or adding an activity/uncertainty head.

The [E-S/E-M/E-L engineering presets](research/framework/architecture.md#913-engineering-size-presets-and-single-size-selection) specify candidate dimensions, not a mandatory size sweep: start with E-M, retain E-S for resource limits and E-L as a justified development reserve. One measured choice is frozen for the core pair and all optional encoder-pretraining regimes plus downstream `0`; it does not expand E4.

### Input-representation scope

The broad representation catalogue is not a commitment to run each entry. Its three principal candidates are primary **Re/Im STFT**, first-alternative time-domain baseband **IQ**, and next-control **real-valued waveform**; complex CWT, magnitude plus sine/cosine phase STFT, and magnitude-only STFT/mel remain wider catalogue entries. Only Re/Im STFT is mandatory. If E4 selects a front-end comparison, it is primary versus one resource-approved alternative, prioritizing IQ and then the real waveform; including both requires a scope/resource revision. This option remains mutually exclusive with the channel-encoder and topology E4 choices. Detailed decisions are in [architecture §8](research/framework/architecture.md#8-input-representation-strategy).
The primary front end uses the selected shared hybrid Conformer-like channel encoder described in [architecture §9.1](research/framework/architecture.md#91-shared-model-contract). Its final grid contains generic real learned features: lossless packing of the complex stem's output does not guarantee phase preservation through the stem or the later real blocks, and the hybrid is not a fully complex network.


## Framework Document Map

| Document | Active responsibility | Global sections |
|---|---|---|
| [Overview](research/framework/overview.md) | Scope, linear-array identifiability, questions, novelty assessment and repository boundary | §1–6 |
| [Architecture](research/framework/architecture.md#91-shared-model-contract) | Selected shared hybrid Conformer-like channel encoder, compact supervised pair and canonical input-representation strategy | §7–12 |
| [Training and adaptation](research/framework/training_strategy.md#135-two-stage-channel-encoder-pretraining-study) | Budgeted supervised core; canonical §13.5 for the optional two-stage E4 protocol, data tracks and training-only branches | §13–14 |
| [Data, simulation and validation](research/framework/data_and_simulation.md) | Mandatory winter data, qualified simulation, measurement uncertainty and domain limitations | §15–16 |
| [Evaluation](research/framework/evaluation.md) | Named baselines, sector-aware error, independent-unit analysis, claim-to-evidence boundaries | §17–22 |
| [Risks](research/framework/risks.md) | Ice window, metrology, ambiguity, leakage, limited groups, scope and publication risks | §23–24 |
| [Roadmap](research/framework/roadmap.md) | Minimum and optional research, calendar, full dissertation text and completion criteria | §25–30 |
| [Russian project summary](../summary.md) | Standalone Russian-language orientation; it is not the authority for the precise E4 protocol | Standalone |

The framework uses continuous top-level numbering (§1–30).

## Working Rules

- Keep minimum, optional and post-deadline work distinct. Do not add a branch to rescue an unfavourable final result.
- Separate simulation, zero-shot real evaluation and real-development adaptation. Final held-out real signals and noise do not enter training, SSL, normalizers or simulator/model tuning.
- Only a linear array is planned in the field; nonlinear topology transfer can be an optional simulation study, not an assumed physical measurement.
- E4 is one bounded choice: the two-stage channel-encoder comparison, primary Re/Im STFT versus one selected resource-approved alternative (baseband IQ first; real waveform as the next control candidate), or simulation-only topology transfer. It does not authorize a three-way front-end comparison or a representation × pretraining × architecture factorial. In the channel-encoder option, Stage 1 compares VAE/HuBERT-style/JEPA A/B/A+B encoders; Stage 2 compares all five pretrained encoders with full-model supervised-from-scratch 0. Its precise contract—including strict S and optional unlabelled R tracks—is canonical in [training §13.5](research/framework/training_strategy.md#135-two-stage-channel-encoder-pretraining-study); predictors and other pretraining-only branches are removed before inference.
- The selected hybrid Conformer-like channel encoder is fixed as the common core across these regimes; E4 changes objectives and learned weights, not the backbone, attention scope, or a CNN-versus-Transformer prerequisite.
- Record unknown decisions with an owner, evidence, due date and failure action. Do not invent hardware settings, safe ice dates, article counts, positive effects or statistical power.
- Maintain the full-text writing workstream from the start. Formal publication requirements and scientific novelty must be reviewed with the supervisor; this plan does not certify degree eligibility.
- Keep detailed experiment settings in the field protocol and coordinated method/evaluation documents; use the roadmap for deadlines rather than introducing conflicting local schedules.
