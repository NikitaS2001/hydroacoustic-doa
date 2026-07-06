# Geometry-Conditioned Hydroacoustic DOA Representation Framework

This document is now an index for the split research framework. The original monolithic draft was divided into topic-focused files under `docs/research/framework/` so that conceptual framing, architecture, data strategy, evaluation protocol, risks, and roadmap can be reviewed and versioned independently.

## Document Map

1. [Overview](research/framework/overview.md)  
   Purpose and scope, target domain, relationship to existing work, motivation, central hypothesis, novelty framing, SSL premise validity, and terminology.

2. [Architecture](research/framework/architecture.md)  
   Framework overview, component priority tiers, input representations, single-channel encoder, geometry-conditioned array encoder, predictive latent dynamics, and downstream heads.

3. [Training And Adaptation Strategy](research/framework/training_strategy.md)  
   Self-supervised training stages, Stage 1/2/3 objectives, Stage 4 fine-tuning, and geometry adaptation protocol.

4. [Data, Simulation, And Hydroacoustic Validation](research/framework/data_and_simulation.md)  
   Data levels, synthetic signal families, BELLHOP propagation, Novik Bay assumptions, noise/interference, real data, split principles, and hydroacoustic validation philosophy.

5. [Evaluation, Baselines, And Protocols](research/framework/evaluation.md)  
   Classical and neural baselines, fair comparison requirements, metrics, claim-to-evidence mapping, experiment families, reproducibility requirements, and experiment-level protocol skeleton.

6. [Risks And Validity Threats](research/framework/risks.md)  
   Data leakage, sim-to-real gap, Novik Bay overfitting, preprocessing and normalization artifacts, geometry/order leakage, weak baselines, latent collapse, Stage 3 risks, fine-tuning risks, and complexity constraints.

7. [Roadmap And Success Criteria](research/framework/roadmap.md)  
   Assumptions, out-of-scope items, expected deliverables, development roadmap, success criteria, kill/pivot criteria, and final research statement.

## Working Rule

Concrete experiment protocols should live outside this framework index, for example under `docs/experiments/`, and should cite the relevant framework files instead of accumulating more protocol detail in this index.
