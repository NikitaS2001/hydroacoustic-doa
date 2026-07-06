# Research Framework Overview

> Split from `docs/research_framework.md`. This file covers the framework purpose, target domain, motivation, hypothesis, and terminology.

## Document Status

This document defines a **high-level research framework** for developing neural models for hydroacoustic direction-of-arrival (DOA) estimation and related array-signal tasks.

It is not intended to be a final experimental protocol, a fixed model specification, or a complete dataset description. Instead, it defines the conceptual research direction, modular architecture, design principles, validation philosophy, and required experimental families for future concrete studies.

Experiment-specific parameters such as array geometry, sampling rate, frequency range, STFT configuration, signal classes, dataset size, channel model parameters, loss functions, and train/validation/test split details must be specified in separate experiment-level protocols.

The current initial deployment-motivated scenario is the hydroacoustic environment near **Russky Island, Novik Bay**. This location is used as a motivating target environment, not as a fully specified experimental protocol. Exact environmental parameters, array parameters, and real-recording validation data are not yet available and must be introduced through later experiment-level specifications.

---

## Abstract

This research framework proposes a **geometry-conditioned self-supervised backbone** for hydroacoustic array-signal representation learning.

The goal is to develop a transferable neural representation that can be adapted to different hydrophone array geometries without full retraining and used with multiple downstream heads, including:

- DOA regression;
- angular probability-map estimation;
- source presence detection.

The framework combines single-channel signal representation learning, array-level geometry-aware aggregation, and predictive latent dynamics. The resulting latent state is intended to represent the evolving hydroacoustic observation scene and support multiple DOA-related tasks through lightweight task-specific heads.

The baseline simulation scenario assumes the use of **BELLHOP** to model realistic underwater acoustic propagation. Controlled synthetic source signals are propagated through BELLHOP-based hydroacoustic channels before being used for representation learning, DOA experiments, and ablation studies.

The final validation target is real hydroacoustic data. BELLHOP-based simulation is treated as the main physically motivated development and testing environment, especially during the initial research stage where real recordings are not yet available, but it must eventually be followed by validation on real hydroacoustic recordings.

---

## 1. Purpose and Scope

### 1.1 Purpose

The purpose of this document is to define a research framework for building neural models that can learn useful latent representations of hydroacoustic array signals.

The framework focuses on three central ideas:

1. **Self-supervised representation learning** from unlabeled hydroacoustic or hydroacoustic-like signal data.
2. **Geometry-conditioned array modeling**, allowing the learned backbone to adapt to different hydrophone array layouts.
3. **Modular downstream heads**, enabling the same latent representation to support multiple DOA-related tasks.

### 1.2 Scope

This document covers:

- high-level research motivation;
- conceptual model architecture;
- data strategy;
- hydroacoustic validation philosophy;
- geometry adaptation strategy;
- downstream head design;
- baseline requirements;
- experimental families;
- risks and validity threats;
- reproducibility requirements.

This document does not define:

- one fixed array geometry;
- one final neural architecture;
- one final preprocessing configuration;
- one final dataset;
- one final loss function;
- one final evaluation benchmark.

Those details should be defined in separate experiment-level specifications.

---

## 2. Target Domain

The target domain is **hydroacoustic DOA estimation using hydrophone arrays**.

The initial geographically motivated target environment is **Novik Bay near Russky Island**. The first DOA formulation is expected to be **far-field one-dimensional azimuth estimation**. Azimuth/elevation estimation may be added later, but it is not part of the initial core target unless an experiment-level protocol explicitly introduces it.

The first array studies should assume simple hydrophone-array families rather than one fixed known array. Candidate initial geometries include:

- uniform linear arrays (ULA);
- square or rectangular arrays;
- other simple planar geometries, if required for controlled geometry-transfer experiments.

Exact hydrophone coordinates, number of sensors, aperture, spacing, calibration properties, and synchronization assumptions are currently unknown and must be specified before any concrete experiment is treated as reproducible.

The framework is intended for array-signal scenes where the useful information for DOA is encoded in inter-sensor relationships such as:

- relative time delays;
- inter-channel phase differences;
- cross-channel coherence;
- spatial covariance;
- frequency-dependent propagation effects;
- array geometry.

The baseline development scenario should use **BELLHOP-based hydroacoustic propagation simulation**. In this scenario, controlled source signals are generated first and then propagated through a physically motivated underwater acoustic channel.

The final validation domain must be real hydroacoustic data. This may include:

- real multi-channel hydrophone recordings;
- controlled tank experiments;
- lake, river, or sea recordings;
- hybrid synthetic-real datasets.

BELLHOP simulation is therefore an intermediate physically grounded validation layer, not a substitute for final real-recording validation.

During the initial phase, BELLHOP-generated data is the primary training and evaluation source. Claims from this phase must be limited to simulation-based hydroacoustic validation and must not be presented as demonstrated real-world performance.

### 2.1 Hydroacoustic Target-Domain Placeholder

The following parameters are intentionally left as placeholders and must be specified in experiment-level protocols:

- hydrophone array geometry;
- number of sensors;
- sensor coordinates;
- sampling rate;
- frequency range;
- sound-speed assumptions;
- source distance range;
- source depth;
- receiver depth;
- far-field or near-field assumption;
- single-source or multi-source setting;
- noise types;
- SNR range;
- BELLHOP environment configuration;
- sound-speed profile;
- bathymetry;
- bottom properties;
- surface assumptions;
- source and receiver depths;
- range grid;
- ray, eigenray, arrival, or impulse-response generation mode;
- reverberation and multipath model;
- source motion assumptions;
- receiver motion assumptions;
- ground-truth DOA acquisition method.

For the initial Novik Bay scenario, the experiment-level protocol must additionally specify:

- whether the bay is modeled as range-independent or range-dependent;
- bathymetry source and spatial resolution;
- sound-speed profile source, season, and depth coverage;
- bottom type and acoustic parameters;
- surface model and sea-state assumptions;
- source and receiver depth ranges appropriate for the bay;
- whether the far-field approximation is valid for the selected array aperture and source ranges;
- whether DOA is limited to 1D azimuth or extended to azimuth/elevation;
- which simple array geometries are used for training, validation, and held-out geometry-transfer tests.

The framework must not assume that a model validated only on simplified chirp simulations is sufficient for hydroacoustic deployment.

---

## 2.2 Relationship to Existing Work

This framework is a forward-looking research direction. It is not a replacement for the existing supervised DOA pipeline (current M4 baseline) and does not resolve open issues in that pipeline by default.

- If an open problem in the current supervised baseline (e.g. occupancy-head mode collapse under sim-to-real shift) is later addressed using ideas from this framework, the connection must be stated explicitly in the relevant experiment-level protocol, including why the SSL/geometry-conditioning approach is expected to help with that specific failure mode rather than more direct fixes (e.g. additional real data, domain adaptation on the existing supervised model, BELLHOP environment recalibration).
- This framework should be treated as a separate, longer-horizon research track unless and until an experiment-level protocol demonstrates it improves on a documented limitation of the current supervised pipeline under matched evaluation conditions.
- Resource allocation between this framework and the existing supervised pipeline is outside the scope of this document and must be decided separately.

---

## 3. Research Motivation

Classical DOA estimation methods are often based on explicit signal and array models. They can be accurate and interpretable, but their performance may degrade when their assumptions are violated, for example under strong reverberation, colored noise, geometry mismatch, sensor calibration errors, or complex nonstationary signals.

Supervised neural DOA estimators can learn flexible mappings from signal features to angles, but they usually require labeled data and may generalize poorly across array geometries, acoustic conditions, source types, and noise regimes.

Hydroacoustic data often contains large amounts of unlabeled recordings but relatively limited labeled DOA data. This makes self-supervised learning attractive: the model can learn signal and array representations before task-specific fine-tuning.

The key research idea is that a geometry-conditioned self-supervised backbone can learn reusable latent representations of hydroacoustic array scenes and support multiple downstream DOA-related tasks with lightweight adaptation.

---

## 4. Core Research Hypothesis

The central hypothesis is:

> A geometry-conditioned self-supervised latent model can learn transferable representations of hydroacoustic array scenes. These representations can be adapted to different hydrophone array geometries without full retraining and can support multiple downstream heads, including DOA regression, angular probability-map estimation, and source presence detection.

This hypothesis has four parts:

1. **Self-supervised learning hypothesis**  
   Unlabeled hydroacoustic signal data can be used to learn representations that improve downstream DOA performance and label efficiency.

2. **Geometry-conditioning hypothesis**  
   Providing array geometry information to the model improves generalization across hydrophone layouts and reduces the need for full retraining.

3. **Predictive latent-state hypothesis**  
   A latent state trained to predict future or masked signal-scene representations can capture physically meaningful temporal and spatial structure.

4. **Modular-head hypothesis**  
   A shared backbone can support multiple downstream heads without redesigning or retraining the full model for each task.

### 4.1 Claim and Novelty Framing

The initial novelty claim should be framed conservatively as a **conceptual and engineering integration** of:

- geometry-conditioned self-supervised representation learning;
- BELLHOP-based hydroacoustic simulation for controlled development;
- lightweight adaptation to simple and modified hydrophone-array geometries;
- multi-head DOA-related readout from a shared latent backbone.

The document should not claim that the method is a proven new state-of-the-art DOA estimator until concrete experiments compare it against strong classical and neural baselines. Scientific novelty must be supported by ablations showing which part of the framework contributes measurable value.

For the first research stage, claims should be limited to BELLHOP-based hydroacoustic simulation near the intended Novik Bay use case. Real-world performance, operational deployment, and BELLHOP-to-real transfer must remain future validation claims until real recordings become available.

### 4.2 SSL Premise Validity Check

The self-supervised learning hypothesis (4.1, part 1) is motivated by domain-level data availability (Section 3), not by the data actually available to this project at the time of writing. Before Stage 1/2 SSL training is treated as a core deliverable rather than an exploratory branch, the experiment-level protocol must state:

- the actual volume and source of unlabeled real hydroacoustic recordings available to this project, if any;
- whether the BELLHOP-only setting (where DOA ground truth is free) provides any genuine SSL motivation, or whether SSL value in this setting is restricted to representation-quality and label-efficiency ablations rather than "solving a labeled-data scarcity problem";
- if no real unlabeled corpus exists yet, SSL claims must be scoped to "representation quality under simulated data" only, and the document must not imply that SSL addresses a labeled-data bottleneck that does not yet exist in the BELLHOP-only stage.

In a BELLHOP-only setting, supervised DOA labels are available by construction. Therefore, self-supervised learning must not be justified as solving label scarcity unless a real unlabeled corpus and a constrained labeled subset are explicitly present. In the initial simulation-only stage, the legitimate SSL claims are narrower:

- improved representation quality under controlled probes;
- improved label efficiency under deliberately matched label-budget experiments;
- improved robustness or transfer under held-out geometry, noise, or BELLHOP environment splits;
- reduced adaptation cost relative to supervised-from-scratch baselines.

---

## 5. Terminology

### 5.1 Hydrophone Array

A hydrophone array is a set of spatially distributed underwater acoustic sensors. Each sensor records a channel of the acoustic field.

### 5.2 DOA

Direction of arrival refers to the direction from which an acoustic signal reaches the array. Depending on the experiment, DOA may be represented as:

- one-dimensional azimuth;
- azimuth and elevation;
- an angular sector;
- an angular probability distribution;
- a spatial probability map.

The specific DOA representation is experiment-dependent.

### 5.3 Backbone

The backbone is the shared neural representation model trained primarily through self-supervised objectives. It is intended to produce latent representations useful for multiple downstream tasks.

### 5.4 Downstream Head

A downstream head is a task-specific module attached to the backbone. In this framework, the primary heads are:

- DOA regression head;
- angular probability-map head;
- source presence detection head.

### 5.5 Predictive Latent Scene State

The term "world model" must not be used in papers, grant materials, or external presentations describing this component, because it invites a vision/RL-style interpretation (full environment modeling) that this framework explicitly does not implement. Internally, the component may be informally called a predictive latent scene state. The "scene" is not the full physical ocean environment. It refers to the latent state of the hydroacoustic array observation scene.

The model qualifies as a predictive latent scene representation if it learns an internal state that:

- summarizes the current hydroacoustic array observation;
- captures inter-channel structure related to the array geometry;
- predicts future or masked latent states;
- supports DOA-related readouts through downstream heads.

---

