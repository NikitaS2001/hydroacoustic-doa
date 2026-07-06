# Wave 0 Digest: Local Framework And External Anchors

## Local Findings

- The document explicitly defines itself as a high-level framework, not an experimental protocol or fixed architecture (`docs/research_framework.md:5-9`).
- The initial Novik Bay scenario is only a motivating target; exact environmental parameters, array parameters, and real-recording validation data are not yet available (`docs/research_framework.md:11`).
- The core hypothesis is geometry-conditioned SSL latent representation transfer across hydrophone geometries with DOA/probability/source-presence heads (`docs/research_framework.md:177-195`).
- The framework correctly limits novelty to conceptual/engineering integration until ablations and strong baselines exist (`docs/research_framework.md:197-208`).
- The document correctly warns that SSL is not justified by label scarcity in BELLHOP-only simulation, because DOA labels are available by construction (`docs/research_framework.md:210-223`).
- Tiering is mature: Tier 0 excludes Stage 3 and advanced SSL until core value is shown (`docs/research_framework.md:300-309`, `docs/research_framework.md:2723-2759`).
- The minimum viable protocol is concrete enough as a skeleton but not yet executable: it still requires numeric array, signal, BELLHOP, environment-count, split, and compute choices (`docs/research_framework.md:3066-3247`).
- The strongest local safeguards are permutation canary, held-out geometry/environment splits, fair baseline requirements, and kill/pivot criteria (`docs/research_framework.md:930-949`, `docs/research_framework.md:3406-3424`, `docs/research_framework.md:3880-3890`).

## External Anchors

- BELLHOP is an appropriate simulation candidate for a first physical propagation layer because the official manual describes ocean acoustic field computation via beam tracing with range/depth-dependent sound speed.
- ARLPY documents the practical path from BELLHOP arrivals to impulse responses, matching the framework's proposed per-hydrophone IR construction.
- Geometry-aware DOA is externally plausible: arXiv 2212.04788 states supervised DNN DOA models trained on one array geometry often perform poorly on another, and proposes microphone coordinates as geometry-aware input.
- Spatial acoustic SSL is externally plausible but mostly non-hydroacoustic: arXiv 2312.00476 proposes cross-channel reconstruction for spatial acoustic representation learning and explicitly motivates it by sim-to-real mismatch and lack of annotated real data.
- Underwater neural DOA is plausible: Frontiers 2022 uses BELLHOP-generated multipath signals and STFT phase features for CRNN DOA with a ULA.
- Strong classical baselines remain mandatory: the SRP-PHAT review describes SRP as widely used in sound source localization, and underwater MFP literature warns that localization accuracy is sensitive to environmental mismatch.
- Novik Bay is a hard target: external sources describe it as shallow, seasonally stratified/ice-affected, relatively isolated, and not a generic deep-water scene.

## EXPAND
- LEAD: quantify minimum BELLHOP environment count and variance needed for credible generalization — WHY: local doc uses approximate 10 held-out environments but no statistical basis — ANGLE: external simulation/benchmark practice and internal risk framing.
- LEAD: verify whether recent geometry-invariant/acoustic-map SSL work is directly relevant or only adjacent — WHY: prior report cites 2025-2026 works; they may not be hydroacoustic — ANGLE: arXiv/OpenReview search for latent acoustic mapping and geometry-invariant SSL.
- LEAD: assess whether Novik Bay far-field 1D azimuth is physically plausible for likely array aperture/source range — WHY: local doc leaves this unresolved — ANGLE: local geometry formula and Novik Bay dimensions.
