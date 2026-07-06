# Draft: channel-encoder-architecture

status: plan-written
pending_action: execute `.omo/plans/channel-encoder-architecture.md` only after explicit start-work approval
intent_route: UNCLEAR
classification: Architecture
tier: HEAVY - architecture-scale planning, external research, model-line decisions, and multiple future implementation modules.

## Skill And Tool Notes

- Skill used: `omo:ulw-plan`, because the request is an architecture/research planning request with no single fixed implementation outcome.
- CodeGraph was attempted first and returned no useful indexed symbols for this docs-only repo; local grounding used direct reads of framework docs.
- No subagents were spawned because the available `multi_agent_v1.spawn_agent` tool explicitly restricts delegation unless the user asked for subagents. This conflicts with the full UNCLEAR auto-review path, so the draft records that high-accuracy review is pending for the post-approval plan phase.
- `.omo/plans/channel-encoder-architecture.md` already exists as a 60-line scaffold with empty TL;DR, scope, verification, todos, final verification, commit strategy, and success criteria. The next approved planner action is to fill that scaffold, not to recreate it.
- Plannotator approval received: "Вывод по созданию рабочего плана на основе проделланой работы мне нравиться. Даю одобрение". The scaffold was filled into a 212-line executable work plan. Approval does not start implementation.

## User-Visible Deliverable

Prepare a decision-complete plan for adapting KVAE/KVAE-Audio and other SOTA audio/video representation ideas into a hydroacoustic channel-model encoder family that is accurate, interpretable, phase-preserving, and scalable by model size.

## Core Local Evidence

- `docs/research/framework/architecture.md:35` defines the framework's priority tiers: Tier 0 first, Stage 3 later, Tier 2 advanced SSL/model families only after Tier 0/Tier 1 evidence.
- `docs/research/framework/architecture.md:47` limits primary single-channel inputs to IQ, STFT, and CWT; multi-channel phase/covariance features are auxiliary, diagnostics, or baselines, not primary single-channel inputs.
- `docs/research/framework/architecture.md:151` requires coherent band selection, downconversion, anti-aliasing, resampling, and physical-time chunking.
- `docs/research/framework/architecture.md:259` states phase, inter-sensor delay, cross-channel coherence, relative timing, and geometry structure must be preserved.
- `docs/research/framework/architecture.md:273` rejects independent per-channel normalization because it can erase spatial cues.
- `docs/research/framework/architecture.md:414` narrows first single-channel candidates to TCN, Transformer, and CNN+TCN.
- `docs/research/framework/architecture.md:501` warns that too-early fixed-vector pooling can destroy timing and phase relationships before array aggregation.
- `docs/research/framework/architecture.md:522` sets masked signal/modeling as first objective and V-JEPA-style latent prediction as advanced follow-up.
- `docs/research/framework/architecture.md:595` defines the array encoder's required targets: inter-channel phase, delay, coherence, sensor positions, aperture, ambiguity, and calibration effects.
- `docs/research/framework/architecture.md:635` prioritizes geometry-aware pairwise Transformer, GNN/relation network, Neural-SRP branch, then optional temporal mixer.
- `docs/research/framework/architecture.md:665` requires permutation invariance/equivariance and a permutation canary.
- `docs/experiments/bellhop_mvp_protocol.md:17` restricts the MVP claim to BELLHOP-only simulation under matched information.
- `docs/experiments/bellhop_mvp_protocol.md:122` already fixes a viable MVP preprocessing envelope: 48 kHz simulation, 12 kHz target rate, 2 s chunks, analytic/IQ primary input, real+imag STFT secondary, CWT excluded from MVP.
- `docs/research/framework/roadmap.md:151` says success requires concrete evidence, with simulation-stage and real-world success reported separately.

## External Evidence Ledger

### KVAE / KVAE-Audio

- `https://github.com/kandinskylab/kvae-audio` and `https://huggingface.co/kandinskylab/KVAE-Audio`: KVAE-Audio is a continuous 48 kHz waveform autoencoder with compact continuous latents for reconstruction and generative models; model card reports 166.9M params and latent dim 64 on public metrics.
- `https://github.com/kandinskylab/kvae`: KVAE is an image/video tokenizer family for diffusion models; video models report temporal compression and spatial compression variants, and the repo explicitly frames tokenizer quality through generation/reconstruction evaluation.
- `https://habr.com/ru/companies/sberbank/articles/1053410/`: Sber/Kandinsky article reports KVAE-Audio evaluation tables for reconstruction and generation; useful as a model-reference source, not hydroacoustic evidence.
- Interpretation: KVAE is useful as design inspiration for compact continuous latent bottlenecks, hierarchical downsampling, and reconstruction/generation metrics. It cannot be used directly as the channel model because it optimizes perceptual/generative reconstruction, not DOA-relevant phase, delay, coherence, or geometry transfer.
- 2026-07-06 recheck: the public KVAE-Audio README still describes the model as a continuous full-band `48 kHz` audio autoencoder for compact continuous latents and generative-model latent space; the repository still exposes MIT license metadata. The source model defaults still use encoder rates `[2, 3, 4, 5, 8]`, so the hop length is `960` samples, i.e. about `50 Hz` latent frame rate at `48 kHz`. That compression is useful for compact tokenization but too aggressive to trust for DOA phase/delay unless a phase-preservation gate passes.
- 2026-07-06 recheck: the KVAE image/video README still frames KVAE as image/video tokenizers for diffusion models and reports video variants with temporal compression and spatial compression. This supports borrowing tokenizer design patterns, not importing the domain objective as hydroacoustic evidence.

### Audio Tokenizers / Codecs

- EnCodec: `https://audiocraft.metademolab.com/encodec.html` - real-time high-fidelity autoencoder with residual vector quantization and parallel token streams.
- DAC: `https://github.com/descriptinc/descript-audio-codec` - high-fidelity RVQGAN audio codec, 44.1 kHz, low-bitrate discrete codes, broad audio domains.
- SNAC: `https://arxiv.org/html/2410.14411v1` - multi-scale neural audio codec with RVQ at different temporal resolutions.
- WavTokenizer: `https://openreview.net/forum?id=yBlVlS2Fd9` / `https://github.com/jishengpeng/WavTokenizer` - low-token-rate discrete acoustic tokenizer for audio language modeling.
- Mimi/Moshi: `https://arxiv.org/html/2410.00037v2` - neural audio codec used for real-time speech-text modeling with low frame-rate codec streams.
- DualCodec: `https://arxiv.org/abs/2505.13000` - dual-stream codec integrating SSL and waveform representations; important because it independently supports the proposed split between precise acoustic waveform information and semantic/SSL targets.
- SAC: `https://aclanthology.org/2026.acl-long.138.pdf` - recent semantic-acoustic dual-stream speech codec; useful as evidence that semantic and acoustic information should often be separated rather than forced through one code stream.
- SUNAC: `https://www.merl.com/publications/docs/TR2026-032.pdf` - source-aware unified neural audio codec; relevant as a future reference for mixture/source-aware channel latents, not MVP.
- XY-Tokenizer: `https://arxiv.org/html/2506.23325v1` - addresses semantic/acoustic conflict in low-bitrate speech codecs; reinforces that a hydroacoustic codec must not optimize semantic compression at the expense of phase/delay fidelity.
- Adaptation value: multi-scale temporal token streams, RVQ/codebook diagnostics, semantic/acoustic stream separation, and codec-size baselines. Risk: discrete codecs can discard phase or delay details unless explicitly constrained.

### Audio SSL And Semantic Tokenizers

- BEATs: `https://arxiv.org/abs/2212.09058` - iterative audio pretraining with acoustic tokenizers and masked label prediction; useful for semantic-token targets, not as direct hydroacoustic spatial evidence.
- data2vec: `https://arxiv.org/abs/2202.03555` - masked-view prediction of contextual latent representations across modalities; strong template for EMA teacher latent targets.
- Spatial acoustic SSL / CCSR: `https://arxiv.org/html/2312.00476v2` - cross-channel signal reconstruction with MC-Conformer learns spatial acoustic representation from unlabeled multichannel data; directly relevant as a Stage 2 pretext idea, but from microphone/spatial audio, not hydroacoustics.

### Spatial Localization And Geometry-Aware Models

- Geometry-aware DOA: `https://arxiv.org/abs/2212.04788` - coordinate-aware DNN for geometry generalization; indirect microphone-array evidence.
- Neural-SRP: `https://arxiv.org/abs/2403.09455` - combines SRP flexibility with neural localization for ad-hoc distributed arrays; relevant physics-informed branch.
- SELD/PSELD/BiMamba: `https://arxiv.org/abs/2506.13455` - recent SELD direction showing Mamba sequence modeling can reduce Transformer cost in acoustic localization; relevant only after Tier 0 evidence.
- Physics-informed audio-geometry-grid representation learning: `https://openreview.net/forum?id=bWXpJFesLS` - recent geometry-invariant/grid-flexible localization direction; relevant as a future geometry-conditioned acoustic-map branch.
- GI-DOAEnet: `https://israelcohen.com/wp-content/uploads/2025/06/DNN-Based_Geometry-Invariant_DOA_Estimation_With_Microphone_Positional_Encoding_and_Complexity_Gradual_Training-1.pdf` - supports microphone positional encoding and staged fixed-to-dynamic geometry training; indirect room/microphone-array evidence, not hydroacoustic proof.

### Video/World-Model Representation Sources

- V-JEPA 2: `https://arxiv.org/html/2506.09985v1` - self-supervised video model predicts in latent space and reports strong motion/action/planning results; best conceptual reference for predictive latent state, not a drop-in audio model.
- MAGVIT-v2: `https://arxiv.org/html/2310.05737v3` - video tokenizer with lookup-free quantization and shared image/video vocabulary; useful for discrete tokenizer design and codebook usage diagnostics.
- OmniTokenizer: `https://arxiv.org/abs/2406.09399` - joint image-video tokenizer with spatial-temporal decoupling; useful for separating spatial and temporal modeling in channel latents.
- Divot: `https://arxiv.org/abs/2412.04432` - diffusion-powered video tokenizer for comprehension and generation; useful as a self-supervised tokenizer-quality idea, too heavy for MVP.
- Cosmos Tokenizer: `https://github.com/NVIDIA/Cosmos-Tokenizer` / `https://research.nvidia.com/labs/dir/cosmos-tokenizer` - current visual tokenizer suite with continuous and discrete image/video variants and multiple compression factors; useful as a model-family pattern for continuous vs discrete hydroacoustic latents and explicit compression-rate ladders.
- MambaVideo tokenizer: `https://arxiv.org/html/2507.04559v1` - recent discrete video tokenizer using Mamba-based encoder-decoder; useful as a later low-compute sequence-tokenizer candidate after TCN/Transformer baselines.

## Derived Technical Answer

Yes, VAE/KVAE and SSL can be combined, but not by averaging their embeddings. The defensible design is a dual-target representation:

1. A continuous compact latent branch inspired by KVAE/VAE for smooth, interpolatable, compressible channel state.
2. A teacher/SSL branch for accurate latent targets and invariances, using masked modeling, data2vec-style EMA targets, and later JEPA-style prediction.
3. Explicit physics-preservation auxiliaries for phase increment, group delay/TDOA bins, pairwise coherence, and calibration perturbation diagnostics.
4. Geometry-conditioned array aggregation that sees per-channel temporal feature maps plus sensor coordinates and pairwise delay constraints.

The latent should be interpretable by construction through factorized heads and probes, not by hoping a VAE latent is meaningful. Required interpretable axes:

- amplitude/envelope and SNR features;
- instantaneous phase or phase increment, represented cyclically;
- instantaneous frequency/chirp-rate summaries;
- channel impulse-response or multipath summary latent;
- pairwise delay/coherence relation tokens after array aggregation;
- global array-scene latent plus angular probability map.

Repository boundary added by the user: the current repository should remain the main reproducible research repository for the complete model program across all stages, selected architectures, training methods, datasets, protocols, evidence, and final reports. MVP implementation work should live in a separate nested Git repository/submodule ("subgit repo") and be referenced from here by pinned commit, configuration snapshot, dataset manifest, and result/evidence paths. The final plan must therefore treat this repo as the canonical research/control plane, not as the place where MVP training code is developed directly.

## Adopted Defaults

1. Do not use KVAE-Audio weights directly for hydroacoustic channel modeling.
   - Rationale: its objective is high-fidelity/generative 48 kHz full-band audio reconstruction, not phase-preserving geometry-conditioned DOA.
   - Reversible: yes; later can evaluate as frozen feature baseline.

2. Use KVAE as inspiration for a continuous latent bottleneck, not as the primary SSL method.
   - Rationale: VAE gives smoother latent space and compression, but may blur task-critical fine phase; SSL teacher targets can recover accuracy.
   - Reversible: yes; can compare no-VAE, beta-VAE, VQ/RVQ, and KL-free autoencoder variants.

3. Keep Tier 0 first: analytic/IQ TCN baseline + geometry-aware pairwise Transformer or GNN + supervised DOA heads.
   - Rationale: local MVP protocol explicitly excludes Tier 2 objectives; success must be measured against no-geometry and classical baselines first.
   - Reversible: partly; changing the first baseline changes comparability.

4. For phase encoding, never regress raw wrapped phase as an ordinary scalar.
   - Rationale: local framework requires cyclic phase representations and preservation of phase/delay/coherence.
   - Reversible: no practical downside; this should be a hard contract.

5. Use a model size ladder from day one:
   - Tiny: 1-5M params, TCN + shallow GNN/pairwise attention, real-time/debug.
   - Small: 10-30M params, TCN/CNN+TCN + pairwise Transformer, main MVP.
   - Base: 50-120M params, Conformer-lite/data2vec-style SSL, serious ablations.
   - Large: 200-500M params, KVAE-like bottleneck + JEPA/DINO-style array SSL, only after Tier 0 wins.
   - XL: 1B+ params, research-only world-model branch if real/unlabeled corpus and compute justify it.
   - Reversible: yes, but parameter budgets must be reported in every experiment.

6. Treat SOTA video/audio methods as adapters of ideas, not pretrained dependencies.
   - Rationale: domains differ; most sources are speech, general audio, image/video, or room-acoustic localization.
   - Reversible: yes; frozen-baseline evaluation can be added later.

7. Explicitly separate semantic, acoustic, and spatial streams in the plan.
   - Rationale: newer audio codecs such as DualCodec, SAC, and XY-Tokenizer treat semantic/acoustic conflict as a design problem; the hydroacoustic version needs an additional spatial/geometry stream to protect DOA cues.
   - Reversible: yes; can ablate single-stream vs dual-stream vs tri-stream.

## Proposed Architecture Families For The Final Plan

### Family A: Phase-Preserving Continuous Latent Channel Encoder

- Input: analytic/IQ chunks and optional STFT real+imag patches.
- Encoder: TCN or CNN+TCN.
- Bottleneck: continuous latent with KL/beta-VAE ablation and collapse/variance diagnostics.
- Objectives: masked latent/feature reconstruction, phase-increment auxiliary, envelope/frequency-slope auxiliary.
- Role: interpretable compact per-channel latent baseline.

### Family B: SSL Teacher-Student Channel Encoder

- Input: same as Family A.
- Encoder: TCN -> Conformer-lite or Transformer as size increases.
- Target: EMA teacher latent from full/weakly corrupted chunk.
- Objectives: data2vec-style masked contextual latent prediction; later JEPA next-embedding prediction.
- Role: accuracy-first branch that preserves details VAE may smooth out.

### Family C: Hybrid VAE + SSL Channel Model

- Shared frontend, two heads:
  - continuous reconstruction/compression latent;
  - SSL latent prediction head.
- Alignment: contrastive/cosine or CCA-style latent alignment with variance/covariance regularization.
- Interpretable probes: phase increment, instantaneous frequency, SNR, source activity, signal family, chirp-rate.
- Role: combine smooth latent geometry with SSL precision.

### Family D: Geometry-Conditioned Array Model

- Input: per-channel temporal feature maps, sensor coordinate embeddings, pairwise displacement/distance/max-delay features, sensor mask.
- Core: geometry-aware pairwise Transformer as primary; GNN/relation network as robustness/variable-sensor alternative.
- Optional branch: Neural-SRP style angular map for interpretability and classical comparison.
- Required canary: channel permutation invariance/equivariance.

### Family E: Latent Dynamics / World Model

- Only after Tier 0.
- Input: array-scene latents over physical-time chunks.
- Core: small TCN/GRU/Mamba/Transformer temporal module.
- Objective: residual latent refinement and JEPA-style future scene-latent prediction.
- Role: temporal robustness and tracking, not raw waveform generation.

## Must-NOT-Have For Final Plan

- No claim that KVAE/KVAE-Audio is directly usable as the hydroacoustic channel model.
- No SOTA claim without BELLHOP matched-information comparison against MVDR/Capon, MUSIC, GCC/SRP-PHAT, and strong neural baselines.
- No Stage 3 or Tier 2 advanced SSL before Tier 0/no-geometry baselines exist.
- No independent per-channel time shifts, phase jitter, or normalization that destroys DOA cues.
- No single fixed vector from the single-channel encoder as the default array input unless an early-pooling ablation passes.
- No real-world Novik Bay claim from BELLHOP-only evidence.
- No MVP implementation code, experiment runners, training scripts, or mutable generated datasets directly inside the main research repo; those belong in the separate MVP subgit repo and are referenced from here reproducibly.

## Components Ledger

1. Preprocessing and phase-safe representation contract.
2. Channel encoder family ladder.
3. Hybrid VAE/SSL objective suite.
4. Geometry-conditioned array encoder.
5. Interpretability probes and physics auxiliaries.
6. Baselines, ablations, and model-size ladder.
7. Repository boundary and reproducibility handoff between the main research repo and MVP subgit repo.
8. Final verification and claim-control reporting.

## Open Assumptions Ledger

| Assumption | Default | Rationale | Reversible |
|---|---|---|---|
| First task | BELLHOP-only, single-source 1D far-field azimuth | Existing MVP protocol fixes this scope | Yes |
| Primary input | Analytic/IQ at 12 kHz target, 2 s chunks | Existing MVP protocol and phase preservation | Yes |
| Secondary input | STFT real+imag | Phase-preserving and comparable to classical methods | Yes |
| CWT | Future ablation, not MVP | Existing MVP excludes it; higher cost | Yes |
| First channel model | TCN masked latent/feature modeling | Local docs require stable simple baseline first | Yes |
| First array model | Geometry-aware pairwise Transformer, with GNN alternative | Best fit for pairwise geometry and sensor masks | Yes |
| First VAE use | Ablation branch, not mainline | VAE smoothness may reduce phase precision | Yes |
| SSL target | data2vec-style EMA latent before JEPA/DINO | Lower complexity bridge to latent prediction | Yes |
| Size ladder | Tiny/Small/Base/Large/XL | User requested line of model sizes from start | Yes |
| Repository boundary | Current repo is canonical research/reproducibility repo; MVP implementation lives in a separate subgit repo | User explicitly set this rule to keep full-program research separate from MVP execution churn | Partly: architecture docs can change, but execution plans must preserve the boundary unless user reverses it |

## Approval Brief To Present

I treated this as open-ended architecture planning and selected defaults instead of asking broad questions. The final plan I intend to write will focus on a hybrid phase-preserving channel-model architecture: Tier 0 analytic/IQ TCN baseline, geometry-aware pairwise array encoder, then a controlled VAE/KVAE-inspired continuous latent branch plus SSL teacher-student branch as ablations. It will explicitly defer KVAE-Audio weights, DINO/JEPA/Mamba/large tokenizer work, and latent dynamics until the MVP/no-geometry/classical-baseline gates pass. It will also preserve the repository boundary: this repo remains the canonical research/reproducibility repo, while MVP implementation belongs in a separate subgit repo referenced by pinned commits and evidence manifests.

Approval needed: write `.omo/plans/channel-encoder-architecture.md` with executable todos, acceptance criteria, QA evidence paths, and commit strategy. Approval does not start implementation.
