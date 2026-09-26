# Hydro-DOA World Model

> Candidate-dissertation research on hydroacoustic azimuth estimation: controlled simulation and winter under-ice recordings on a **linear hydrophone array**.

## Current Goal

Prepare a **complete Candidate of Sciences dissertation text by 2027-03-31**, with a reproducible research study and manuscript preparation in parallel. Real measurements from ice in a bay during winter 2026–2027 are part of the **minimum**, not a later optional validation stage.

The real array is **linear only**. Uniform spacing, sensor count, aperture, exact bay, source/recorder capabilities and safe ice dates are not confirmed. A linear array has structural mirror/front-back ambiguity: the experiment needs a surveyed identifiable source sector/half-plane, shared by every method. No unambiguous 360-degree or arbitrary-topology real-transfer claim is planned.

The required number of **published articles** is unknown and must be clarified with the supervisor/institution by **2026-09-30**. The March deadline is for the full text, not a promise of publication acceptance, formal eligibility, defense or a degree award.

## Minimum Study

| Part | Required result |
|---|---|
| M1 — winter data | Labelled, calibrated linear-array recordings with source/receiver truth, uncertainty, independent acquisition groups, QA and verified raw-data backups |
| M2 — controlled development | Physically qualified, resource-bounded simulation; MVDR/Capon and MUSIC comparisons, Bartlett diagnostic |
| M3 — compact method | One supervised coordinate-aware model and a matched no-coordinate twin; one **Re/Im STFT** phase-preserving front end and one azimuth output |
| M4 — evidence | Accuracy, robustness, applicability limits and simulation-to-recording domain shift on the measured linear array; independent-unit analysis and reproducibility |
| M5 — writing | Full dissertation and a main submission-ready manuscript package by 2027-03-31; article count remains subject to formal requirements |

**Re/Im STFT** is the primary neural front end: real and imaginary parts are two feature channels, not expanded frequency or time axes. The broad representation catalogue is deliberately not an experiment commitment. Its three principal candidates are primary Re/Im STFT, first-alternative time-domain baseband IQ, and next-control real-valued waveform; complex CWT, magnitude plus sine/cosine phase STFT, and magnitude-only STFT/mel remain wider catalogue entries. Only the primary is mandatory. A selected E4 front-end comparison contrasts it with one resource-approved alternative, prioritizing IQ and then the real waveform; including both alternatives requires an explicit scope/resource revision. [Architecture §8](docs/research/framework/architecture.md#8-input-representation-strategy) defines the representation decisions and safeguards.
The selected core basis is one common hybrid Conformer-like channel encoder: a compact complex Conv2D stem is followed by lossless Re/Im packing of its features, then real temporal blocks apply full attention within the bounded input window at each frequency position, retain the frequency grid, and use local frequency mixing. It has no sensor-slot or cross-sensor attention inside the encoder; sensors are grouped for separate Fusion and the one azimuth head. The final feature grid is real learned coordinates, not a full-complex or phase-preservation guarantee; its evidence-gated configuration is canonical in [architecture §9.1](docs/research/framework/architecture.md#91-shared-model-contract).

The selected [coordinate-aware channel-attention Fusion](docs/research/framework/architecture.md#102-array-aggregation-requirements) combines shared coordinate/frequency encodings with sensor attention at each TF position, then masked sensor and valid-TF means. The E-M pilot uses one block, four heads and FFN `96→192→96`; its matched no-coordinate arm supplies a constant zero coordinate input. No fixed ULA mirror pairing or proven arbitrary-array transfer is implied.

The selected [single-azimuth head](docs/research/framework/architecture.md#12-downstream-heads) maps pooled features through `C → C → 2` and trains raw `(a,b)` against `(cos θ,sin θ)` by mean summed-component MSE. Finite nondegenerate vectors decode via `atan2(b,a)`; invalid vectors are prediction failures, not default zero angles. Circular angular error remains the evaluation metric, with no sector clipping or added head.

A positive coordinate effect is not guaranteed. The supervisor must assess the scientific contribution, including the adequacy of any negative result; completing a comparison is not automatically sufficient dissertation novelty.

**Approved claim hierarchy:** the central contribution is the DOA method and its experimentally established accuracy, robustness and limits on the available linear array. Transfer to other geometries is an optional simulation study, not a completion criterion for the dissertation. The coordinate/no-coordinate comparison is a component ablation, not a substitute for the practical method comparisons or evidence of arbitrary-array real transfer.

## Calendar

| Period | Priority |
|---|---|
| September–October 2026 | Clarify formal requirements; confirm apparatus/source/field feasibility by 10-15; prepare literature and measurement design |
| November 2026 | Baselines and compact pilot; freeze measured configuration/analysis by 11-15; end-to-end recording, QA and backup rehearsal by 11-30 |
| December 2026–January 2027 | Main campaign at an authorised safe opportunity; independent final groups reserved; risk review on 01-15 if usable labelled data are absent |
| February 2027 | Safe targeted reacquisition reserve through 02-15; complete core analysis and freeze experiments by 02-28 |
| March 2027 | First complete dissertation by 03-10; supervisor review and final text by 03-31 |

The [E-S/E-M/E-L engineering presets](docs/research/framework/architecture.md#913-engineering-size-presets-and-single-size-selection) define candidate sizes: E-M starts the pilot, E-S is the resource fallback, and E-L a development reserve. One size and its complete configuration—including within-window attention scope—are frozen from phase/resource evidence before the November gate. The presets are not three compulsory fits, measured parameter totals, or a size-by-pretraining matrix.

These are planning targets, **not forecasts of safe ice**. The qualified field lead and local procedures control access and abort decisions. Failure to obtain valid winter data requires an explicit scientific-scope decision; simulation or real-noise overlays do not silently replace the field minimum.

## Additional Studies

In priority order: E1 small labelled real-development adaptation; E2 within-linear sensor-subset/spacing sensitivity; E3 bounded calibration/ice-assumption sensitivity; E4 one bounded study: either the two-stage channel-encoder comparison—Stage 1 VAE, HuBERT-style (H), and JEPA task ablations A, B and A+B; Stage 2 those five pretrained encoders plus matched full-model supervised-from-scratch **0**—**or** primary Re/Im STFT versus one selected, resource-approved alternative (baseband IQ first; real waveform as the next control candidate) **or** arbitrary-topology **simulation-only** transfer. E4 does not create an automatic three-way front-end comparison or representation × pretraining × architecture factorial.
The hybrid Conformer-like encoder is the selected common core for the compact pair and all E4 channel-encoder regimes, not an additional E4 experiment, a CNN-first prerequisite, or an architecture factorial.

At most one extension is active, only when the minimum and writing are on track. JEPA is one pretraining family within E4, not the whole study; its predictors and every other pretraining-only branch are removed before the one jointly fine-tuned azimuth model. Stage-1 probes diagnose transferable spatial cues but cannot establish a final DOA benefit. E4 has a total **five-focused-working-day scheduling stop cap**, not a runtime estimate: remeasure the enlarged resource scope before launch, gate the planned three paired seeds on that evidence, and treat its 18 downstream fits as the total for six regimes—not automatically 18 fits beyond an exactly matched core. The strict simulated-data track S remains the default; optional approved unlabelled real-assisted track R is separate from labelled E1 and does not silently multiply the comparison matrix. No new extension starts after **2027-02-01**; optional results freeze by **2027-02-15**. All extensions may be dropped. Scene/world-model dynamics, additional downstream task heads, large-scale architecture ladders, 3-D/multi-source tracking and a real-time product are outside this deadline-bound programme.

## Documentation

| Document | Role |
|---|---|
| [Roadmap and success criteria](docs/research/framework/roadmap.md) | Authoritative minimum, extensions, decisions, calendar and dissertation deliverables |
| [Winter field protocol](docs/experiments/winter_field_protocol.md) | Active preparation/acquisition, calibration/truth, QA, split/access and contingency contract |
| [Framework overview](docs/research/framework/overview.md) | Research question, scope, linear-array limitations and terminology |
| [Architecture](docs/research/framework/architecture.md#91-shared-model-contract) / [training](docs/research/framework/training_strategy.md#135-two-stage-channel-encoder-pretraining-study) | Selected shared hybrid Conformer-like channel encoder for the compact pair; canonical §9.1 defines its common backbone contract, while §13.5 defines the optional two-stage E4 protocol, data tracks and training-only branches |
| [Data and simulation](docs/research/framework/data_and_simulation.md) | Winter dataset, simulation role and ice/domain limitations |
| [Evaluation](docs/research/framework/evaluation.md) / [risks](docs/research/framework/risks.md) | Evidence, independent units, uncertainty and stop/revision rules |
| [Documentation index](docs/README.md) | Complete document map |

## Repository and Evidence Status

This repository contains **documentation only**. Implementation and artifact locations remain to be decided; this plan does not imply an executable system or completed experiments.

The winter campaign, new method and new empirical gates are **not yet evaluated**. Solver execution alone is not evidence of a validated ice model or a completed dissertation experiment. An open-water pressure-release surface is not an ice boundary.

The repository name is historical: the active study does **not** claim a predictive “world model.”
