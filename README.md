# Hydro-DOA World Model

> Research framework for geometry-conditioned self-supervised learning of hydroacoustic array-signal representations.
>
> **Note on terminology:** The term "world model" in this repository name refers to a *predictive latent scene representation* for hydroacoustic array observations, not an RL-style environment model. See [`docs/research/framework/overview.md`](docs/research/framework/overview.md) for the precise definition and usage restrictions.

## What This Is

This repository is the **canonical research and reproducibility control plane** for developing neural models that estimate direction-of-arrival (DOA) and related spatial properties from hydrophone arrays in underwater environments. It currently contains documentation and a non-final, **NO-GO** experiment-protocol draft only: there is no executable implementation, generated dataset, model checkpoint, or empirical result in this repository.

The primary Tier-0 hypothesis is that a **supervised geometry-conditioned backbone** improves held-out array transfer over a matched no-coordinate model. Self-supervised learning remains an optional, separately evaluated Tier-1 extension.

## Architecture at a Glance

```mermaid
graph TD
    A[Multi-channel hydroacoustic signal] --> B[Input representation layer<br/>IQ / STFT / CWT]
    B --> C[Single-channel encoder<br/>TCN / Transformer / Conformer]
    C --> D[Geometry-conditioned array encoder<br/>Pairwise Transformer / GNN]
    D --> E[Predictive latent dynamics<br/>Optional Stage 3]
    E --> F[Task-specific heads]
    F --> G[DOA regression]
    F --> H[Angular probability map]
    F --> I[Source presence detection]
```

## Repository Boundary

```mermaid
graph LR
    subgraph Research Repo [This repo — Research Control Plane]
        A[Architecture decisions]
        B[Protocols & framework]
        C[Dataset manifests]
        D[Pinned MVP commits]
        E[Evidence & results]
    end
    
    subgraph MVP Repo [MVP Subgit — Executable Code]
        F[Training scripts]
        G[Generated datasets]
        H[Checkpoints & logs]
    end
    
    A -.->|references| F
    D -.->|pins version| F
    F -.->|produces| G
    G -.->|evidence paths| E
```

## Repository Structure

```
.
├── docs/
│   ├── research/framework/     # Framework documentation
│   │   ├── overview.md         # Purpose, hypothesis, terminology
│   │   ├── architecture.md     # Pipeline, encoders, model ladder
│   │   ├── training_strategy.md # SSL stages, objectives, adaptation
│   │   ├── evaluation.md       # Metrics, baselines, gates
│   │   ├── risks.md            # Validity threats, external deps
│   │   └── ...
│   └── experiments/
│       └── bellhop_mvp_protocol.md  # Diagnostic protocol draft
├── .omo/                       # Local ignored planning/evidence; non-authoritative
│   ├── plans/                  # Work plans
│   ├── evidence/               # Verification evidence
│   └── drafts/                 # Research drafts
└── README.md                   # This file
```

## Quick Navigation

| I want to... | Go to |
|---|---|
| Browse the documentation index | [`docs/README.md`](docs/README.md) |
| Understand the big picture | [`docs/research/framework/overview.md`](docs/research/framework/overview.md) |
| See the model architecture | [`docs/research/framework/architecture.md`](docs/research/framework/architecture.md) |
| Understand training stages | [`docs/research/framework/training_strategy.md`](docs/research/framework/training_strategy.md) |
| Review data and simulation rules | [`docs/research/framework/data_and_simulation.md`](docs/research/framework/data_and_simulation.md) |
| See the first experiment | [`docs/experiments/bellhop_mvp_protocol.md`](docs/experiments/bellhop_mvp_protocol.md) |
| Check evaluation criteria | [`docs/research/framework/evaluation.md`](docs/research/framework/evaluation.md) |
| Review risks and threats | [`docs/research/framework/risks.md`](docs/research/framework/risks.md) |
| Follow the research roadmap | [`docs/research/framework/roadmap.md`](docs/research/framework/roadmap.md) |
| Read the dated methodology audit | [`docs/research_plan_analysis.md`](docs/research_plan_analysis.md) |

## Model Family Ladder

```mermaid
graph LR
    A[Tiny<br/>0.5-5M params<br/>Stage 1 debug] --> B[Small<br/>5-30M params<br/>MVP target]
    B --> C[Base<br/>30-120M params<br/>Tier 1]
    C --> D[Large<br/>120-500M params<br/>Tier 2]
    D --> E[XL<br/>500M+ params<br/>Research only]
    
    style A fill:#e1f5fe
    style B fill:#b3e5fc
    style C fill:#81d4fa
    style D fill:#4fc3f7
    style E fill:#29b6f6
```

## Key Design Principles

- **Phase-preserving representations** — IQ and STFT real+imag as primary inputs; no raw wrapped phase regression
- **Geometry-conditioned, not geometry-fixed** — Model adapts to different arrays via coordinate features, not retraining
- **Permutation equivariance** — Array encoder output must not depend on sensor ordering
- **Evidence-gated progression** — No Tier 2 (JEPA, Mamba, XL) until Tier 0 baseline passes
- **Simulation-first, real-world later** — BELLHOP MVP establishes baselines before real Novik Bay data

## Status

The framework and experiment protocol are active drafts. Full generation and confirmatory claims remain **NO-GO** until the protocol's documented prerequisites are satisfied. Simulator runs, power analysis, model training, dataset generation, checkpoints, and empirical results are all **not yet evaluated**.

The ignored `.omo/` directory is local planning and verification evidence, not published research documentation. Generated or stale local visuals are not authoritative; use the linked Markdown framework, protocol, and dated audit.

## Citation

This is an active research project. For questions or contributions, refer to the framework documentation or open an issue.
