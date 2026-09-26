# Roadmap And Success Criteria

> Active planning baseline: 2026-09-19. Candidate of Sciences dissertation; full text by **2027-03-31**. This file is authoritative for the minimum study, extensions, calendar and writing milestones. Acquisition and analysis details live in the [winter field protocol](../../experiments/winter_field_protocol.md).

## 25. Confirmed Constraints and Open Decisions

### 25.1 Confirmed constraints

- The target is a **Candidate of Sciences dissertation (кандидатская диссертация)**, not merely a prototype or experiment report.
- “Before April 2027” is conservatively scheduled as **2027-03-31** for the complete text. This is not a promised defense, degree award or publication acceptance date.
- The required number of **published** articles is not yet known. Submission, acceptance and publication are different milestones; a manuscript count cannot substitute for institutional requirements.
- Real measurements will take place **from ice in a bay during winter 2026–2027**, and are a central part of the minimum study.
- Real measurements use **only a linear hydrophone array**. Uniform spacing, sensor count, aperture and exact submerged coordinates are not yet specified. A linear array is not automatically a uniform linear array (ULA).
- The repository contains documentation only. Implementation, field readiness and new scientific results are not established by this plan.

The exact bay has not been reconfirmed. Novik Bay / Russky Island remains the earlier motivating candidate, not a newly confirmed expedition site. Safe ice dates, source availability, source positioning, access, recorder capabilities and the available project effort must be checked, not inferred from the deadline.

### 25.2 Decision register

Dates below are planning targets. The candidate maintains the register; a responsible role must accept each decision and link its evidence before it is closed.

| Decision | Responsible role | Evidence required | Due | If unresolved |
|---|---|---|---|---|
| Scientific specialty, dissertation structure and proposed contributions | Candidate + supervisor | Institution/specialty requirements; contribution-to-chapter outline; prior-art review | 2026-09-30 | Re-scope the scientific minimum; do not assume an engineering comparison suffices |
| Published-article count, eligible venues, required publication stage | Candidate + supervisor / dissertation council | Applicable formal requirements and feasible publication route | 2026-09-30 | Publication readiness remains an open risk; no promise of meeting the count by March |
| Effort, compute, acquisition equipment and storage | Candidate + equipment/field leads | Inventory, availability commitments and bench/runtime measurements | 2026-10-15 | Reduce optional work and model size; escalate if the minimum cannot fit |
| Bay, authorised access, winter window and contingency | Field lead + supervisor | Local permissions, qualified safety process, logistics and reserve opportunity | 2026-10-15; recheck before every outing | No unsafe outing; agree a claims-limited alternative explicitly |
| Linear array, controllable source and underwater ground truth | Equipment + metrology leads | Bench/rehearsal response and timing evidence; demonstrated underwater-survey method, preliminary geometry and uncertainty budget; actual positions recorded per winter deployment | 2026-10-15 feasibility | Unlabelled noise alone cannot satisfy DOA validation; resolve or revise scope before winter |
| Band, sample rate, identifiable sector, primary Re/Im STFT front end and numerical QA limits | Candidate + metrology lead | Bench data, spatial-aliasing/ambiguity analysis, acquisition precision and uncertainty | 2026-11-15 | No final quantitative campaign/evaluation freeze until justified |
| Model/baseline slate, one selected E-S/E-M/E-L hybrid channel-encoder preset and complete configuration (including attention scope), splits, metrics, practical-effect interpretation and independent-unit plan | Candidate + supervisor | E-M-first development pilot, phase/delay and resource evidence, rationale for the one-size choice, written architecture/analysis/access policy | 2026-11-15 | Continue development-only work; consider E-S for resource limits, not automatic escalation to E-L; do not inspect final held-out results |

The [engineering size presets](architecture.md#913-engineering-size-presets-and-single-size-selection) are not three mandatory model arms: E-M is the first candidate, E-S the resource fallback, and E-L a justified development reserve. Freeze one size for the core pair and, if selected, every encoder-pretraining regime plus downstream `0`; no size-by-objective factorial or change to E4's total stop cap follows.

## 26. Minimum Scope and Exclusions

### 26.1 One coherent scientific study

Study single-source hydroacoustic azimuth estimation on the **available measured linear array**, with phase-preserving processing, explicit geometry/calibration assumptions, controlled simulation and independent under-ice recordings. The central contribution is the method and its experimentally established accuracy, robustness and applicability limits. Compare the compact estimator with the declared classical methods; use the matched no-coordinate twin as a component ablation, not as the sole basis for a practical advantage or novelty claim. Transfer to other geometries is optional simulation research and is not required to complete the minimum.

Two evidence domains must remain separate:

1. **Controlled simulation:** independently sampled acoustic environments representative of the measured linear configuration support method development, comparator evaluation and bounded calibration/measurement-uncertainty checks. Deliberately held-out layouts, spacings or topologies belong to optional E2/E4 studies, not a required geometry-transfer endpoint.
2. **Measured data:** the actual linear array establishes performance, failure modes and simulation-to-recording domain shift under recorded winter conditions. A single fixed physical array does **not** establish transfer to arbitrary physical topologies. Constant coordinates in one deployment cannot by themselves isolate the causal benefit of geometry conditioning.

Linear-array mirror/front-back ambiguity is structural. The primary azimuth study requires a surveyed, physically identifiable source half-plane/sector, supplied as the same prior to every method. Neither neural training nor coordinates create missing directional information. If that prior cannot be established, an ambiguous-direction/direction-cosine formulation and its claims must be agreed before freezing the experiment; do not silently claim full-circle azimuth. Far-field validity must also be checked against the actual aperture, wavelength and range; use valid restricted conditions or declared range-aware steering rather than relabelling near-field data as far field.

The 1D azimuth formulation also requires fixed/known elevation or a justified depth/range bound showing negligible elevation effects at the stated uncertainty. If this cannot be established, the linear array supports an ambiguous direction projection rather than the proposed azimuth claim; agree the task revision before final evaluation.

### 26.2 Minimum method slate

- One calibrated, phase-preserving primary representation: **Re/Im STFT** (real and imaginary components) is the planning default, subject to the pre-campaign bench freeze. No mandatory IQ/STFT/CWT sweep.
- One compact supervised coordinate-conditioned model and a matched no-coordinate model; same observations, output, preprocessing, splits, training/tuning budget and information policy except the declared coordinate branch. Target **three paired seeds per neural model**, subject to the November feasibility review; report actual repetitions, not assumed precision.
- The selected common core is a hybrid Conformer-like channel encoder for the primary Re/Im STFT: compact complex Conv2D stem, lossless paired real/imaginary representation, real temporal Conformer-like processing with full attention within the bounded input window separately at each frequency position, and local frequency mixing before sensors regroup for separate Fusion and one azimuth head. It is fixed for the compact pair and all E4 channel-encoder regimes, not an E4 architecture experiment or CNN-versus-Transformer prerequisite; final real features do not guarantee a full-complex or strict phase-preserving network. [Architecture §9.1](architecture.md#91-shared-model-contract) is canonical, while concrete sizing and feasibility remain gated by the 11-15 decision.
- **MVDR/Capon and MUSIC** as the classical comparisons, configured on development data with the same band, identifiable sector and available calibration. **Bartlett/delay-and-sum** is a diagnostic reference.
- One azimuth output and the indispensable phase, calibration, permutation, leakage and reproducibility checks. No source-presence head or tracking system is required.
- A resource-bounded simulation pilot before full generation. BELLHOP is a candidate propagation tool, not an already validated model of ice. An open-water pressure-release surface is not an ice boundary; unvalidated ice physics means generic simulation/domain-shift conclusions, not validated under-ice propagation claims.

The broad representation catalogue is not a commitment to run every entry. Its three principal candidates are primary Re/Im STFT, first-alternative time-domain baseband IQ, and next-control real-valued waveform; complex CWT, magnitude plus sine/cosine phase STFT, and magnitude-only STFT/mel remain wider catalogue entries. Only Re/Im STFT is mandatory. If E4 selects a front-end comparison, it is primary versus exactly one resource-approved alternative, prioritizing IQ and then the real waveform; including both requires a scope/resource revision. It stays mutually exclusive with E4's channel-encoder and topology choices. No representation × pretraining × architecture factorial is authorized; detailed decisions are in [architecture §8](architecture.md#8-input-representation-strategy).


This slate supports comparisons with the named methods, not universal or state-of-the-art superiority.

The no-coordinate twin is an information ablation. Its observable target and possible symmetry-induced error floor must be diagnosed before the comparison is interpreted. Supplying missing position information is not, by itself, a novel architecture or proof of superiority over strong fixed-layout neural methods; see the [evaluation contract](evaluation.md).

### 26.3 Outside the deadline-bound minimum

Predictive latent scene/world-model claims; multiple downstream task heads; multi-source tracking; 3-D localization; Base/Large/XL scaling; broad SSL and representation benchmarks beyond the bounded E4 study; and a deployable real-time/edge product. E4's permitted temporal prediction is pretraining of latent signal windows, not an exception for scene dynamics or tracking. Non-linear physical arrays are outside the confirmed acquisition scope, not a reserve campaign requirement.

## 27. Minimum Deliverables and Additional Studies

### 27.1 Minimum deliverables

| ID | Required deliverable | Observable completion evidence | Dissertation use |
|---|---|---|---|
| M1 | Quality-controlled labelled winter recordings on the linear array | Raw files reopened, checksums/backups, calibration and underwater source/receiver truth with uncertainty, background recordings, acquisition-group and split manifests; field acceptance criteria met | Experimental methodology and measured-data chapter |
| M2 | Controlled, physically qualified simulation and classical baselines | Development-only validity/resource pilot, documented boundary assumptions, reproducible environment splits and baseline checks | Problem formulation, methods and controlled evaluation |
| M3 | Compact DOA method and component ablation | Frozen estimator/classical comparisons and matched coordinate ablation, declared budget/seeds, one output/front end, integrity checks and independent predictions | Method accuracy, robustness and component analysis for the measured linear configuration; no required geometry-transfer claim |
| M4 | Bounded simulation and measured-data analysis | Per-independent-unit error/failure/coverage tables, uncertainty and limitations, simulator/field separation, no held-out contamination, reproducibility package | Results, discussion and defensible conclusions |
| M5 | Full dissertation text and manuscript package | All chapters, introduction, conclusions, references and appendices; evidence-to-claim traceability; supervisor corrections; a submission-ready main manuscript | Deadline deliverable by 2027-03-31 |

M1 requires a controllable/otherwise independently localized source and trustworthy labels; availability is a prerequisite to confirm, not an equipment fact supplied by the owner. Multiple independently acquired groups are an acquisition objective—preferably at least three redeployed sessions/days where safe and feasible—not proof of statistical power. Thousands of windows from one deployment remain one deployment. With too few groups, narrow the inference and report descriptive uncertainty limits; do not manufacture confidence by resampling correlated clips.

A failure to obtain usable labelled winter data means **M1 and the real-data portion of M4 are not complete**. Simulation alone cannot silently replace them. The supervisor must explicitly approve any revised thesis scope and its scientific adequacy.

### 27.2 Additional studies, in priority order

All entries are optional. At most **one** may be active. Proposed effort caps are scheduling stop limits, not measured runtime estimates; remeasure the selected scope before launch and revise downward if it threatens a minimum deliverable.

| ID | Additional question | Start prerequisite | Planning cap and stopping rule | Permissible claim |
|---|---|---|---|---|
| E1 | Does small-budget adaptation on real development data reduce the sim-to-real gap? | M1 quality gate, frozen sim-only baseline, separate adaptation/development and held-out real groups; a useful label-budget comparison is feasible | Up to 5 focused working days; stop if the budget/access contract or core analyses slip | Label-budget-specific adaptation on measured conditions; not zero-shot performance |
| E2 | How sensitive is the estimator to linear sensor subsets or spacing? | Already available data/metadata support the contrast without risking essential acquisition; same held-out policy | Up to 3 focused working days; no additional non-linear field deployment | Within-linear sensitivity; a subset is not an independent physical topology or campaign |
| E3 | How much do measured calibration or ice-boundary assumptions affect the result beyond core QA? | Core diagnostics complete; parameters have measured bounds or explicitly justified sensitivity ranges | Up to 5 focused working days; stop before an unvalidated propagation-model development project forms | Sensitivity under stated assumptions, not a validated elastic-ice model |
| E4 | Does the two-stage channel-encoder comparison on the fixed core inference architecture—Stage 1 VAE, HuBERT-style H, and JEPA A/B/A+B; Stage 2 those five pretrained encoders plus full-model supervised-from-scratch 0—produce a useful or robust result; **or**, instead, is Re/Im STFT versus one selected alternative informative (baseband IQ first, real waveform as the next control candidate); **or** is simulated non-linear topology transfer informative? | Minimum results and writing are on track; enough permitted development data/compute and remeasured resources; for A/A+B, valid direct-reference eligibility; any R corpus/access separately approved; representation comparisons declare one training regime and any input-block differences | Up to 5 focused working days total, a scheduling stop cap rather than a runtime estimate; no combined architecture/coordinate sweep. If the complete selected protocol cannot fit, defer it or explicitly revise it | Conditional evidence only for the selected comparison; no automatic three-way front-end experiment, representation × pretraining × architecture factorial, or real non-linear topology claim |

The selected hybrid Conformer-like channel encoder is the fixed common core in the channel-encoder option: E4 compares training objectives and learned weights on that backbone, not Conformer against CNN-first or other architectures. Its full temporal attention remains within the bounded input window at each frequency position; any development/resource-driven scope decision must be made before comparative pretraining and apply identically to every regime.

No extension starts after **2027-02-01**; optional results freeze by **2027-02-15**. Late arrival of field data can eliminate the entire extension programme. Extensions cannot rescue a failed primary result by changing its endpoint or replacing the reported comparison. In the E4 channel-encoder option, JEPA is one family with A/B task ablations; Stage 1 has the five specified pretraining variants, then frozen encoders with matched trained diagnostic probes, while Stage 2 has six full-model downstream regimes. Three paired seeds remain evidence-gated: 18 is the total downstream-fit count, not automatically 18 additional fits after an exact matching core. Fusion/head start anew and train jointly with the encoder in each Stage-2 regime; the no-coordinate twin remains outside the SSL matrix. If E4 instead selects a front-end comparison, it is primary Re/Im STFT versus one resource-approved alternative, prioritizing IQ and then the real waveform; including both requires a scope/resource revision within the same five-focused-working-day total cap.

S remains strict sim-only. The optional unlabelled R pretraining track requires explicit corpus/access approval and group-level provenance within the same E4 budget; it is separate from labelled E1 and never fabricates direct targets or silently multiplies the matrix. The complete channel-encoder access, target, phase, resource and reporting contract remains in [training §13.5](training_strategy.md#135-two-stage-channel-encoder-pretraining-study).

### 27.3 Writing and publication workstream

Plan a main coherent manuscript alongside the dissertation; this is a workload unit, **not** a claim that one article satisfies the degree rules. Once the formal publication requirements are known, set article/venue/submission priorities with the supervisor and assess whether acceptance/publication lead times fit. More work or an extra experiment does not guarantee journal acceptance by March.

Proposed chapter map, subject to institutional rules:

1. Problem, relevance, literature, research question and explicit contributions.
2. Linear-array observation model, identifiability, calibration and estimation methods.
3. Controlled simulation, compact method, baselines and ablation design.
4. Winter measurement methodology, dataset quality and independent evaluation.
5. Joint analysis, applicability boundaries, limitations and conclusions.

Maintain the bibliography, figures, tables and methods text during the experiments. Each claimed contribution must map to a comparison, data split, artifact and limitation. A well-conducted negative result may be useful, but neither a dataset nor a null comparison automatically provides sufficient novelty for a candidate dissertation; review that question with the supervisor in September and after the November pilot.

## 28. Calendar and Decision Gates

### 28.1 Calendar

Winter dates are **planning targets, not forecasts of safe ice**. Field authorisation has precedence over all dates. Preparation and chapter writing run in parallel.

| Period | Research / acquisition | Text / publication output | Gate or result |
|---|---|---|---|
| 2026-09-19–09-30 | Confirm specialty/contribution requirements, article rules, equipment/effort inventory; scope linear-array question | Dissertation outline, evidence map and bibliography structure | Formal requirements and feasibility owners assigned |
| October 2026 | Source/receiver/synchronization/positioning feasibility by 10-15; acquisition/QA/calibration prototype and controlled sanity checks | Introduction/literature drafts; field-methods outline by 10-31 | R1: a credible labelled acquisition route; otherwise early scope revision |
| November 2026 | Classical methods and compact pair; physics/resource pilot; measurement/analysis contract frozen by 11-15; complete end-to-end lab rehearsal by 11-30 | Methods and controlled-study draft; main manuscript outline | R2: reopen real recorder files, verify phase/timing/labels/QA/backup end to end; model training must fit the budget |
| December 2026–2027-01-31 | Main winter acquisition at the earliest authorised safe opportunity; development/QA recording first, independent final groups reserved | Update measurement chapter and development results as data arrive | R3: usable labelled data; 01-15 risk checkpoint if access/data are still absent |
| 2027-02-01–02-15 | Targeted essential reacquisition only if safe and needed; core evaluation and reproducibility; optional work only under §27.2 | Results tables and measured-data chapter drafts | No new extension after 02-01; reserve acquisition/optional results target ends 02-15 |
| 2027-02-16–02-28 | Complete core comparisons, uncertainty, failure analysis and evidence audit; freeze data/models/tables | Assemble all results/chapter drafts and main manuscript results | R4: experiment freeze on 02-28; missing field evidence escalated, never hidden |
| 2027-03-01–03-10 | Only necessary error correction/reproducibility repair; no new research branch | First complete dissertation manuscript by 03-10 | R5: all chapters, conclusions, references and appendices present |
| 2027-03-11–03-21 | Resolve reviewer/supervisor questions within frozen scope; record any result-changing correction | Supervisor review and revisions | Corrections tracked against evidence |
| 2027-03-22–03-31 | Final consistency and artifact checks | Full dissertation text and submission-ready manuscript package | R6: complete text by 03-31; no claim that degree/publication requirements are automatically fulfilled |

A data-integrity error discovered after freeze must be corrected and disclosed even if it changes conclusions; a deadline is not a reason to retain invalid results. Any schedule impact is escalated, not concealed through a new metric or selective omission.

### 28.2 Field readiness and contingency

Before the first authorised winter outing, rehearse the entire path: recorder → immutable raw files → channel map/timing/calibration → source truth → diagnostic estimates → QA decision → verified backups. Readiness does not require finishing every neural experiment; a development-only recording must not be delayed by optional model work.

The field lead controls access, weather/ice safety and abort decisions under local professional/institutional procedures. This research plan sets no ice-thickness criterion. Missing source/positioning capability, timing failure, missing labels, clipping/dropouts or unusable geometry must be detected while a safe reserve opportunity still exists.

At **2027-01-15**, if there is no usable labelled recording or credible safe access, the candidate, supervisor and field lead review the reserve window and a scientifically explicit contingency. Options may include a safely available alternative labelled acquisition arrangement or a formally narrowed dissertation scope; neither is presumed available or equivalent to the promised winter study. If the field minimum cannot be met by the February analysis window, state that risk immediately. Do not wait until March, fabricate a second campaign or present simulated-plus-real-noise overlays as field validation.

## 29. Success, Evidence and Stop Criteria

### 29.1 Completion is distinct from a positive hypothesis

The minimum is complete when M1–M5 have their specified evidence, the conclusions match what was actually measured, and the supervisor has assessed the contribution/formal-requirement fit. Neither a positive coordinate-ablation effect nor successful transfer to other geometries is a completion condition. A null or adverse method result is reported and its scientific adequacy reviewed, not replaced by a new architecture search.

- Optional geometry-transfer results support only the tested simulation domain; they cannot establish transfer to unmeasured physical geometries and are not required for minimum completion.
- Real performance is bounded by measured conditions, independent acquisition groups, linear-array ambiguity and ground-truth uncertainty.
- No cross-topology real transfer, all-weather/open-water generality, full-circle identifiability or deployment readiness follows from this campaign.
- Primary angular error uses the circular distance within the declared identifiable sector; no silent clipping. Report median, p95, coverage/failure rate and per-unit paired contrasts. The [evaluation contract](evaluation.md) governs aggregation and justified uncertainty.
- The amount of independent data—not the number of windows, overlays or training seeds—limits precision. Thresholds and any power claims require development evidence and pre-test freezing.

### 29.2 Stop / pivot rules

| Trigger | Required action |
|---|---|
| Hardware, source truth or synchronisation cannot support labelled DOA | Fix the metrology/acquisition route before final recordings; escalate scope rather than collecting unusable volume |
| No safe winter access or no valid labelled data by the risk checkpoint | Invoke §28.2 with the field lead/supervisor; safety overrides schedule |
| Linear ambiguity, far-field or ice assumptions do not hold | Restrict/amend the observable task and physical claim before final evaluation; do not train away an unidentifiable label |
| Pair does not outperform no-coordinate or classical methods | Report the negative/conditional result and diagnose within the frozen scope; assess scientific adequacy with supervisor |
| Phase/permutation/leakage/replay gate fails | Treat affected results as invalid until repaired; no additional model branch as a substitute |
| Too few independent field groups | Report limited descriptive results; no fabricated cross-session inference or sample power |
| Minimum or writing milestone slips | Stop all extensions first; any reduction of the minimum requires explicit supervisor/owner approval |
| Publication requirements exceed the current manuscript route | Replan the publication strategy early; distinguish research completion from formal eligibility |

## 30. Final Research Statement

The deadline-bound study investigates **phase-preserving, geometry-aware hydroacoustic azimuth estimation for a linear hydrophone array**, combining controlled simulated contrasts with winter under-ice recordings and explicit calibration, identifiability and domain-shift analysis.

The intended output is a scientifically bounded candidate-dissertation study and full text by **2027-03-31**, with a reproducible evidence package and manuscript preparation in parallel. It is not a promise of a general “world model,” arbitrary-array real transfer, a positive neural advantage, publication acceptance or a completed defense. Additional studies are expendable; trustworthy winter data, honest conclusions and the complete text are not silently expendable.
