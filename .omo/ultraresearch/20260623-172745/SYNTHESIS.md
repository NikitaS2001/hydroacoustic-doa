# Ultraresearch Synthesis: Viability Of Geometry-Conditioned Hydroacoustic DOA Framework

Date: 2026-06-23  
Local inputs:
- `docs/research_framework.md`
- `.omo/ultraresearch/20260623-170253/SYNTHESIS.md`

## Executive Summary

The idea is viable as a long-horizon research program, but not yet as a validated method or near-term deployable system. The core hypothesis is coherent: use self-supervised single-channel representation learning, geometry-conditioned array aggregation, and lightweight downstream heads for DOA-related tasks. This matches active external research directions in geometry-aware DoA, spatial acoustic SSL, latent acoustic mapping, and physics-informed geometry-invariant localization. The local document is strongest where it constrains its own claims: it explicitly says it is a framework rather than an experiment protocol, limits BELLHOP-only claims to simulation, requires real-recording validation later, demands strong classical baselines, and defines kill/pivot criteria.

The main weakness is not the idea. It is experiment readiness. The framework still lacks the numeric assumptions needed for a first reproducible experiment: hydrophone coordinates, aperture and spacing, sampling rate, frequency band, source ranges/depths, BELLHOP environment distribution, Novik Bay bathymetry/SSP/bottom/surface assumptions, train/validation/test split counts, model sizes, compute budget, and pass/fail thresholds. Because those are missing, the project can claim a defensible research direction but cannot yet claim a working algorithm, superiority over baselines, real-world transfer, or Novik Bay applicability.

Updated score:

| Dimension | Score | Rationale |
|---|---:|---|
| Scientific plausibility | 7.5/10 | Strong alignment with geometry-aware DoA and spatial acoustic SSL literature, but hydroacoustic transfer remains unproven. |
| Conceptual maturity | 8/10 | Clear decomposition, claim boundaries, baselines, risks, and kill criteria. |
| Experiment readiness | 4/10 | Protocol skeleton exists, but numeric data/simulation/model choices are missing. |
| Real-world deployment readiness | 2/10 | No real recordings, no fixed array, no calibrated Novik Bay setup, no real-time measurement. |
| Overclaim risk if executed casually | high | Simulation shortcuts, environment mismatch, weak baselines, and SSL overclaiming could easily produce false-positive results. |

## What The Idea Is

The local framework proposes a geometry-conditioned self-supervised latent model for hydroacoustic array scenes. The intended pipeline is:

1. IQ/STFT/CWT input representation.
2. Single-channel encoder.
3. Geometry-conditioned array encoder.
4. Optional predictive latent dynamics.
5. Heads for DOA regression, angular probability maps, and source presence.

The document states that it is not a final protocol or architecture (`docs/research_framework.md:5-9`). It also states that Novik Bay/Russky Island is currently a motivating scenario, not a fully specified experimental setup (`docs/research_framework.md:11`). That distinction is important: the document is mature as a framework, but intentionally incomplete as an executable experiment.

The central hypothesis is explicitly decomposed into SSL, geometry conditioning, predictive latent state, and modular heads (`docs/research_framework.md:177-195`). The novelty claim is framed conservatively as conceptual/engineering integration until ablations against strong baselines exist (`docs/research_framework.md:197-208`).

## External Plausibility Check

### BELLHOP Layer

BELLHOP is a reasonable first simulation tool. The Ocean Acoustics Library documentation describes BELLHOP as computing ocean acoustic fields via beam tracing in media where sound speed can vary with range and depth: https://oalib-acoustics.org/website_resources/AcousticsToolbox/manual/node61.html. ARLPY documents a practical workflow from BELLHOP arrivals to impulse response construction: https://arlpy.readthedocs.io/en/latest/uwapm.html.

This supports the framework's plan to use per-hydrophone arrivals or impulse responses. It does not validate real-world performance. The framework correctly says BELLHOP simulation is an intermediate physical validation layer, not a substitute for real recordings (`docs/research_framework.md:96-107`, `docs/research_framework.md:2160-2162`).

### Geometry Conditioning

The geometry-conditioning premise is externally supported. Kowalk, Doclo, and Bitzer state that supervised DNN DoA estimators trained for one microphone geometry often perform poorly on different geometry and propose coordinate-aware input features: https://arxiv.org/abs/2212.04788. This aligns with the local claim that geometry metadata should improve array transfer (`docs/research_framework.md:188-190`) and with the required held-out geometry protocol (`docs/research_framework.md:1981-2038`).

The local document is especially strong in adding a permutation/order policy. It requires the model not to depend on channel slot order and mandates a permutation canary before Stage 2/downstream reporting (`docs/research_framework.md:930-949`). That is not cosmetic; it directly protects the central transfer claim.

### Self-Supervised Spatial Acoustic Representation

The SSL premise is plausible but must be scoped carefully. Yang and Li's spatial acoustic SSL paper uses cross-channel signal reconstruction and explicitly motivates SSL by simulation-to-reality mismatch and limited annotated real data: https://arxiv.org/abs/2312.00476. LAM 2025 similarly proposes self-supervised acoustic mapping for DoA and reports adaptation across microphone arrays on LOCATA/STARSS-like spatial-audio benchmarks: https://arxiv.org/html/2507.07066v1. AGG-RL, an ICLR 2026 poster, targets geometry-invariant and grid-flexible sound source localization with physics-informed audio-geometry-grid learning: https://openreview.net/forum?id=bWXpJFesLS.

These sources support the research direction, not the hydroacoustic result. They are mainly microphone/spatial-audio works. The local framework correctly guards against SSL overclaiming: in a BELLHOP-only stage, labels are available by construction, so SSL cannot be justified as solving label scarcity unless a real unlabeled corpus and limited labeled subset exist (`docs/research_framework.md:210-223`).

### Underwater Neural DOA

Underwater neural DOA is plausible. A Frontiers 2022 CRNN paper formulates underwater DOA under multipath/low-SNR conditions, uses BELLHOP-generated multipath signals, and feeds STFT phase to a CRNN: https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1027830/full. This supports the general feasibility of neural DOA on BELLHOP-style data. It does not support the stronger claims of geometry transfer, SSL label efficiency, or BELLHOP-to-real transfer.

### Classical Baseline Pressure

The baseline set in the local document is appropriate. SRP-PHAT is a serious comparator, not a strawman; a 2024 review describes SRP as widely used in sound source localization and reviews over 200 SRP/SRP-PHAT papers: https://arxiv.org/abs/2405.02991. MFP is essential for hydroacoustic physics-aware comparison where environment replicas exist, but recent underwater localization work warns that MFP accuracy is sensitive to propagation-model parameter mismatch: https://arl.nus.edu.sg/wp-content/uploads/2025/03/A-gradient-based-optimization-approach-for-underwater-acoustic-source-localization.pdf.

This supports the framework's insistence on MVDR/Capon, MUSIC, GCC/TDOA, SRP-PHAT, and MFP where applicable (`docs/research_framework.md:2373-2555`). It also means a neural model beating only delay-and-sum or a weak CNN would not be meaningful.

### Novik Bay Target

Novik Bay is not a generic easy shallow-water test case. Physical Oceanography 2021 describes seasonal thermohaline structure, weak summer dynamics, ice formation, and shallow/isolation effects: https://physical-oceanography.ru/repository/issues/2021/06/03/. A 2023 Marine Science and Engineering article describes Novik Bay as over 12 km long, 12.7 km2 in area, up to about 20 m deep near the entrance, and relatively understudied: https://www.mdpi.com/2077-1312/11/10/1973.

This supports the framework's requirement that a Novik Bay protocol must specify bathymetry, SSP source/season/depth, bottom type, surface/ice assumptions, source/receiver depth ranges, and whether far-field 1D azimuth is valid (`docs/research_framework.md:139-149`, `docs/research_framework.md:2149-2158`).

## Strengths

1. The framework does not overclaim by design. It repeatedly separates framework, simulation-stage validation, Novik target benchmark, and real-world validation (`docs/research_framework.md:5-11`, `docs/research_framework.md:2160-2162`, `docs/research_framework.md:3851-3867`).

2. The architecture is staged well. Tier 0 limits the first result to input representation, single-channel encoder, geometry-conditioned array encoder, and Stage 4 heads. Stage 3 and advanced SSL are explicitly blocked until Tier 0 value is shown (`docs/research_framework.md:300-309`, `docs/research_framework.md:2723-2759`).

3. The baseline philosophy is strong. The document demands primary classical comparators and framework ablations, and it requires reporting privileged information separately (`docs/research_framework.md:2373-2555`).

4. The risk section is unusually useful. It names data leakage, BELLHOP-to-real gap, Novik Bay overfitting, sampling/chunking artifacts, normalization leakage, channel-order leakage, weak baselines, latent collapse, and Stage 3 over-smoothing (`docs/research_framework.md:3250-3699`).

5. The kill/pivot criteria are concrete enough to prevent architecture creep: stop if geometry conditioning does not beat no-geometry transfer, SSL does not improve 50% label-budget performance, the model does not beat MVDR/Capon or MUSIC under matched information, permutation canary fails, or held-out environment evidence is too small/high-variance (`docs/research_framework.md:3880-3890`).

## Weaknesses And Missing Pieces

### Missing For Reproducible Experiment

The document has a protocol skeleton but no executable protocol. Missing items include:

- fixed or sampled hydrophone coordinates, aperture, spacing, calibration, synchronization;
- useful frequency band, original/target sampling rates, chunk duration/hop, STFT/CWT settings;
- BELLHOP run mode, beam/ray convergence policy, arrivals-to-IR construction, environment count;
- sound-speed profile, bathymetry, bottom, surface/ice, source/receiver depth ranges;
- train/validation/test split units and held-out environment/geometry counts;
- model sizes, parameter counts, memory/latency target, compute budget;
- numeric success thresholds for angular error, label efficiency, transfer degradation, and baseline wins.

The local document itself requires these blocks before results are treated as reproducible (`docs/research_framework.md:3066-3247`).

### SSL Claim Is Conditional

The SSL component is scientifically plausible but not automatically useful. In pure simulation, DOA labels are free, so SSL must win on one of these measured claims:

- better head-only probe quality;
- better label efficiency at fixed budgets;
- better held-out geometry/environment transfer;
- lower adaptation cost than supervised-from-scratch;
- robustness to noise/interference or missing sensors.

Without those results, SSL is added complexity rather than a validated contribution.

### Far-Field 1D Azimuth Is Not Yet Justified

The local framework starts with far-field 1D azimuth (`docs/research_framework.md:77`) but correctly requires validation for Novik Bay (`docs/research_framework.md:147`). This is unresolved. Far-field validity depends on aperture and wavelength. A common Fraunhofer-style rule scales with aperture squared over wavelength; the Discovery of Sound in the Sea notes that the near/far transition depends on array size and wavelength: https://dosits.org/science/advanced-topics/near-far-field-propagation/.

Inference: for underwater sound speed near 1500 m/s, a 10 kHz signal has wavelength about 0.15 m. A 1 m aperture may be far-field after tens of meters, but a 10 m aperture can push the far-field boundary toward kilometer-scale ranges. Since Novik Bay is shallow and bounded, source range and array aperture must be fixed before 1D far-field azimuth can be assumed.

### Sim-To-Real Is The Dominant Unknown

BELLHOP helps avoid toy simulation, but real hydroacoustic recordings can differ through bathymetry error, bottom properties, SSP seasonality, surface/ice, reverberation, shipping/biological noise, sensor calibration, and synchronization. The framework cannot resolve this without real recordings and DOA ground truth. Domain randomization can reduce risk but cannot prove real transfer.

## Viability Verdict

### Viable Claims Now

- The research direction is coherent and externally plausible.
- BELLHOP-first simulation is a reasonable development layer.
- Geometry conditioning is a well-motivated way to attack array-transfer brittleness.
- Spatial SSL/cross-channel reconstruction/latent acoustic maps are active adjacent research directions.
- The framework document is mature as a research-control document: it states assumptions, risk controls, baselines, evidence mapping, and kill criteria.

### Claims Not Yet Viable

- The proposed method improves DOA performance.
- The proposed method improves label efficiency.
- The geometry-conditioned backbone transfers across hydrophone arrays.
- Stage 3 predictive latent dynamics adds value.
- BELLHOP simulation transfers to real hydroacoustic recordings.
- The approach is valid for Novik Bay operational use.
- The approach is real-time or edge feasible.

These remain not-yet-evaluated because no experiment, dataset, fixed array, BELLHOP environment distribution, real recordings, or baseline results are present.

## Recommendation

Do not add Stage 3, DINO/JEPA, Mamba, wav2vec/HuBERT, or a larger architecture yet. The next useful artifact is a numeric BELLHOP-only MVP protocol. It should freeze a narrow claim:

- single-source far-field 1D azimuth only if aperture/range justify it;
- 4-8 hydrophones;
- ULA to square/rectangular transfer;
- six synthetic signal families;
- domain-randomized shallow-water BELLHOP environments;
- explicit held-out environment count and variance reporting;
- IQ and STFT only for the first input representation pass;
- TCN/CRNN supervised-from-scratch baseline, no-geometry baseline, geometry-conditioned pairwise Transformer or GNN;
- MVDR/Capon, MUSIC, SRP-PHAT/GCC-TDOA, and MFP when environment replicas are available;
- head-only and full-fine-tuning comparison;
- label efficiency at 10/50/100%;
- mandatory permutation canary and BELLHOP ray/arrival sanity checks.

The first positive claim should be small: "In BELLHOP-domain randomized simulation under matched information, geometry conditioning improves held-out simple-array transfer over a no-geometry model and remains competitive with classical baselines." Anything stronger should wait.

## Source List

1. Local framework: `docs/research_framework.md`.
2. Prior synthesis: `.omo/ultraresearch/20260623-170253/SYNTHESIS.md`.
3. BELLHOP manual, Ocean Acoustics Library: https://oalib-acoustics.org/website_resources/AcousticsToolbox/manual/node61.html.
4. ARLPY underwater acoustic propagation/BELLHOP docs: https://arlpy.readthedocs.io/en/latest/uwapm.html.
5. Geometry-aware DoA estimation, arXiv 2212.04788: https://arxiv.org/abs/2212.04788.
6. Self-supervised spatial acoustic representation with cross-channel reconstruction, arXiv 2312.00476: https://arxiv.org/abs/2312.00476.
7. Underwater CRNN DOA with BELLHOP multipath, Frontiers 2022: https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1027830/full.
8. SRP-PHAT tutorial review, arXiv 2405.02991: https://arxiv.org/abs/2405.02991.
9. Underwater localization environmental mismatch / MFP sensitivity: https://arl.nus.edu.sg/wp-content/uploads/2025/03/A-gradient-based-optimization-approach-for-underwater-acoustic-source-localization.pdf.
10. Novik Bay hydrological regime, Physical Oceanography 2021: https://physical-oceanography.ru/repository/issues/2021/06/03/.
11. Novik Bay dimensions/bathymetry context, MDPI 2023: https://www.mdpi.com/2077-1312/11/10/1973.
12. Latent Acoustic Mapping, arXiv 2507.07066: https://arxiv.org/html/2507.07066v1.
13. AGG-RL OpenReview ICLR 2026 poster: https://openreview.net/forum?id=bWXpJFesLS.
14. DOSITS near/far-field propagation overview: https://dosits.org/science/advanced-topics/near-far-field-propagation/.

## Expansion Closure

Open leads from Wave 0 are closed as follows:

- Minimum held-out environment count: the local framework's "fewer than approximately 10 held-out environments is preliminary" rule is reasonable as a conservative reporting gate, but not a statistically complete power analysis. It should be treated as a floor, not proof.
- Recent geometry-invariant/acoustic-map SSL work: relevant as adjacent support, not hydroacoustic validation.
- Novik Bay far-field 1D azimuth: unresolved until array aperture, source range, and operating band are fixed.

Convergence reason: the main axes repeat the same conclusion across local and external evidence: the framework is conceptually strong and externally plausible, but experiment readiness and real-world validation remain the blockers.
