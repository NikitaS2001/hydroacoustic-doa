# channel-encoder-architecture - Work Plan

## TL;DR (For humans)

**What you'll get:** A research-grade architecture plan for the hydroacoustic channel encoder family: phase-preserving inputs, Tiny/Small/Base/Large/XL model ladder, hybrid SSL+VAE/KVAE-style branches, geometry-aware array encoding, and reproducibility handoff to a separate MVP subgit repo.

**Why this approach:** KVAE/KVAE-Audio is useful as a source of tokenizer and continuous-latent ideas, but not as a direct DOA model. The plan keeps Tier 0 simple and testable first, then adds VAE/SSL/JEPA/Mamba-style methods only behind evidence gates.

**What it will NOT do:** It will not put MVP training code or generated datasets into this research repo. It will not claim KVAE-Audio is directly usable for hydroacoustic DOA. It will not advance Stage 3/Tier 2 before classical/no-geometry baselines are passed.

**Effort:** Medium
**Risk:** Medium - the main risk is over-designing model families before the BELLHOP MVP establishes phase/delay and geometry-transfer evidence.
**Decisions I made for you:** Treat this repo as canonical research/reproducibility control plane; use a separate MVP subgit repo for executable training/generation code; start with analytic/IQ TCN + geometry-aware pairwise array encoder; use VAE/KVAE as an auxiliary/ablation branch, not the mainline; use data2vec-style SSL before JEPA/DINO/Mamba; require phase-preservation gates before accepting any compressed latent.

Your next move: run `$omo:start-work .omo/plans/channel-encoder-architecture.md` or say "start work" to execute this plan. Full execution detail follows below.

---

> TL;DR (machine): Medium effort, medium risk, docs/control-plane plan for phase-preserving channel encoder architecture and MVP subgit reproducibility boundary.

## Scope

### Must have

- Update the research/control-plane documentation so the channel encoder architecture is explicit, reviewable, and compatible with the existing framework split.
- Preserve the current repository as the canonical reproducible research repo:
  - architecture decisions;
  - protocols;
  - dataset manifests;
  - pinned MVP subgit commits;
  - result/evidence references;
  - final reports.
- Define the MVP implementation boundary:
  - MVP code, training scripts, runners, generated datasets, and mutable outputs live in a separate nested Git repo/submodule;
  - this repo references that work only through pinned commits, config snapshots, manifests, and evidence/result paths.
- Add a channel encoder model family design:
  - Tiny: 1-5M params, analytic/IQ TCN sanity/debug baseline;
  - Small: 10-30M params, IQ + STFT real/imag with CNN+TCN and pairwise geometry Transformer, main MVP target;
  - Base: 50-120M params, Conformer-lite or Transformer plus data2vec-style SSL;
  - Large: 200-500M params, hybrid VAE/KVAE-like continuous latent plus stronger SSL and Neural-SRP auxiliary branch;
  - XL: 1B+ params, JEPA/Mamba/world-model research branch only after Tier 0 evidence.
- Define the VAE/KVAE position:
  - use KVAE/KVAE-Audio as design inspiration and optional frozen/ported ablation;
  - do not treat public KVAE-Audio weights as the default hydroacoustic encoder;
  - require phase/delay preservation gates before a compressed continuous latent can feed the array encoder.
- Define phase-safe representation rules:
  - no raw wrapped phase scalar regression;
  - use analytic/IQ and STFT real+imag as primary phase-preserving representations;
  - optionally add cyclic phase, phase increment, group delay, TDOA, coherence, and calibration probes.
- Define Stage-compatible training strategy:
  - Tier 0 supervised + masked single-channel feature/latent modeling;
  - Stage 2 geometry-aware array SSL/auxiliary tasks;
  - VAE branch as auxiliary/ablation;
  - data2vec-style SSL before JEPA/DINO;
  - Stage 3 latent dynamics deferred.
- Add ablation and success gates:
  - SSL-only;
  - VAE-only;
  - hybrid SSL+VAE;
  - KVAE-Audio reference/frozen baseline if license/dependency checks pass;
  - complex-STFT phase encoder;
  - no-geometry baseline;
  - classical baselines.

### Must NOT have (guardrails, anti-slop, scope boundaries)

- No MVP implementation code in the main research repo.
- No training runners, experiment scripts, generated datasets, checkpoint files, or mutable output trees in the main research repo.
- No claim that KVAE/KVAE-Audio is directly usable as the hydroacoustic channel model.
- No SOTA claim without matched-information comparison against MVDR/Capon, MUSIC, GCC/SRP-PHAT/SRP-style methods, and strong neural baselines.
- No Stage 3, JEPA/DINO, Mamba, XL tokenizer, or world-model work before Tier 0/no-geometry/classical gates pass.
- No independent per-channel normalization, resampling, phase jitter, random time shift, or augmentation that can destroy DOA cues.
- No single fixed-vector pooling from the single-channel encoder as the default array input unless an early-pooling ablation passes.
- No real-world Novik Bay claim from BELLHOP-only evidence.
- No importing external KVAE/KVAE-Audio code into the main repo before license, dependency, and domain-fit review.

## Verification strategy

> Zero human intervention - all verification is agent-executed.

- Test decision: tests-after for document consistency only; no runtime model tests because this plan edits research/control-plane artifacts, not executable model code.
- Static checks:
  - `rg -n "KVAE|VAE|SSL|phase|subgit|repository boundary|Tiny|Small|Base|Large|XL" docs .omo`
  - `rg -n "MVP implementation code|generated datasets|training scripts" docs .omo`
  - `test -s docs/research/framework/architecture.md`
  - `test -s docs/experiments/bellhop_mvp_protocol.md`
  - `test -s .omo/plans/channel-encoder-architecture.md`
- Consistency checks:
  - the research repo/subgit boundary appears in both the plan and target documentation;
  - every model family has a size range, role, allowed stage, and rejection gate;
  - KVAE/KVAE-Audio is described as inspiration/ablation, not the default encoder;
  - phase representation uses IQ or real+imag/cyclic forms, not raw scalar phase;
  - Stage 3/Tier 2 methods are explicitly deferred.
- Evidence: `.omo/evidence/channel-encoder-architecture-plan-verification.md`

## Execution strategy

### Parallel execution waves

- Wave 1: Update the canonical architecture decisions and repository-boundary contract. Tasks 1-3 can be done in parallel after reading the existing framework files.
- Wave 2: Update MVP protocol touchpoints and evaluation gates. Tasks 4-6 can be done in parallel after Wave 1 because they depend on the terminology and model-family ladder.
- Wave 3: Run final consistency verification and write evidence. Task 7 depends on all earlier tasks.

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 | none | 4, 5, 7 | 2, 3 |
| 2 | none | 4, 5, 6, 7 | 1, 3 |
| 3 | none | 4, 6, 7 | 1, 2 |
| 4 | 1, 2, 3 | 7 | 5, 6 |
| 5 | 1, 2 | 7 | 4, 6 |
| 6 | 2, 3 | 7 | 4, 5 |
| 7 | 1, 2, 3, 4, 5, 6 | final verification | none |

## Todos

- [ ] 1. Add the repository-boundary contract to the research framework docs
  What to do / Must NOT do: Add a concise section to the appropriate framework document, preferably `docs/research/framework/overview.md` or `docs/research/framework/roadmap.md`, defining this repository as the canonical research/reproducibility control plane and the MVP as a separate subgit repo/submodule. Specify what lives here, what lives in the MVP repo, and what artifacts connect them: pinned commit, config snapshot, dataset manifest, evidence/result paths. Do not add executable MVP code or scripts.
  Parallelization: Wave 1 | Blocked by: none | Blocks: 4, 5, 7
  References (executor has NO interview context - be exhaustive): `.omo/drafts/channel-encoder-architecture.md`; `docs/research/framework/overview.md`; `docs/research/framework/roadmap.md`; `docs/experiments/bellhop_mvp_protocol.md`
  Acceptance criteria (agent-executable): `rg -n "canonical research|reproducibility|subgit|submodule|pinned commit|dataset manifest|evidence" docs/research docs/experiments .omo/plans/channel-encoder-architecture.md`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify the boundary is stated without ambiguity, Evidence `.omo/evidence/task-1-channel-encoder-architecture.md`; failure: run `rg -n "training script|runner|checkpoint|generated dataset" docs/research/framework/overview.md docs/research/framework/roadmap.md` and verify the section does not authorize putting MVP code or mutable outputs in the main repo.
  Commit: Y | docs(research-boundary): define MVP subgit reproducibility boundary

- [ ] 2. Add the channel encoder model-family ladder to architecture docs
  What to do / Must NOT do: Update `docs/research/framework/architecture.md` with an explicit channel encoder family ladder: Tiny, Small, Base, Large, XL. For each family, specify parameter range, intended stage, input representation, backbone, objective family, role, and rejection gate. Do not present Large/XL as MVP requirements.
  Parallelization: Wave 1 | Blocked by: none | Blocks: 4, 5, 6, 7
  References (executor has NO interview context - be exhaustive): `.omo/drafts/channel-encoder-architecture.md` sections `Derived Technical Answer`, `Adopted Defaults`, `Proposed Architecture Families`; `docs/research/framework/architecture.md` sections on Tier 0/Tier 1/Tier 2, input representations, single-channel encoder, array encoder, and phase preservation.
  Acceptance criteria (agent-executable): `rg -n "Tiny|Small|Base|Large|XL|TCN|Conformer|data2vec|JEPA|Mamba|phase-preservation gate" docs/research/framework/architecture.md`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify every size tier has a role and stage; failure: run `rg -n "Large.*MVP|XL.*MVP|JEPA.*MVP|Mamba.*MVP" docs/research/framework/architecture.md` and verify no advanced tier is framed as required for MVP.
  Commit: Y | docs(architecture): add channel encoder model ladder

- [ ] 3. Define the VAE/KVAE and SSL hybrid architecture contract
  What to do / Must NOT do: Add a dedicated section to `docs/research/framework/architecture.md` or a linked architecture subsection explaining that KVAE/KVAE-Audio is inspiration/ablation, not a direct channel model. Specify the hybrid design: shared phase-safe frontend, deterministic SSL latent `h_ssl`, optional variational/continuous latent `z_vae`, reconstruction/compactness losses, teacher-student SSL losses, and explicit phase/delay/coherence probes. Do not claim public KVAE-Audio weights solve hydroacoustic DOA.
  Parallelization: Wave 1 | Blocked by: none | Blocks: 4, 6, 7
  References (executor has NO interview context - be exhaustive): `.omo/drafts/channel-encoder-architecture.md` external evidence ledger; `docs/research/framework/architecture.md`; KVAE-Audio README at `https://github.com/kandinskylab/kvae-audio`; KVAE README at `https://github.com/kandinskylab/kvae`; Habr article at `https://habr.com/ru/companies/sberbank/articles/1053410/`
  Acceptance criteria (agent-executable): `rg -n "KVAE|KVAE-Audio|h_ssl|z_vae|teacher-student|reconstruction|phase increment|group delay|TDOA|coherence" docs/research/framework/architecture.md`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify the hybrid branches are named and staged; failure: run `rg -n "directly usable|drop-in|ready-made|default.*KVAE|KVAE.*default encoder" docs/research/framework/architecture.md` and verify no direct-use claim exists.
  Commit: Y | docs(architecture): define SSL and KVAE-inspired hybrid encoder contract

- [ ] 4. Update the BELLHOP MVP protocol with model-family scope and ablation matrix
  What to do / Must NOT do: Update `docs/experiments/bellhop_mvp_protocol.md` so the first executable protocol points to the model-family ladder but keeps MVP scope narrow. Define allowed MVP variants: Tiny supervised/IQ TCN, Small IQ+STFT CNN+TCN with geometry-aware pairwise Transformer, optional VAE branch ablation, optional SSL branch if it uses MVP-safe augmentations. Explicitly defer Base/Large/XL, JEPA, DINO, Mamba, and latent dynamics. Do not expand the MVP claim.
  Parallelization: Wave 2 | Blocked by: 1, 2, 3 | Blocks: 7
  References (executor has NO interview context - be exhaustive): `docs/experiments/bellhop_mvp_protocol.md` sections `MVP Claim`, `Signal And Preprocessing Configuration`, `Training Stages`, `Dataset Cardinality`, `Baselines`; `docs/research/framework/architecture.md`; `.omo/drafts/channel-encoder-architecture.md`
  Acceptance criteria (agent-executable): `rg -n "Tiny|Small|ablation|SSL-only|VAE-only|hybrid|no-geometry|Base|Large|XL|defer|MVP claim" docs/experiments/bellhop_mvp_protocol.md`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify the ablation matrix is present; failure: run `rg -n "Stage 3|JEPA|DINO|Mamba|Large|XL" docs/experiments/bellhop_mvp_protocol.md` and verify every occurrence is marked out-of-scope/deferred unless already in a general exclusion list.
  Commit: Y | docs(mvp): add channel encoder ablation scope

- [ ] 5. Add phase-preservation and interpretability gates
  What to do / Must NOT do: Define concrete gates for accepting an encoder latent: TDOA recoverability, phase increment consistency, pairwise coherence preservation, calibration perturbation sanity, permutation canary, and early-pooling rejection. Tie each gate to a pass/fail criterion in docs, even if numeric thresholds remain protocol-specific. Do not allow phase-destroying augmentations.
  Parallelization: Wave 2 | Blocked by: 1, 2 | Blocks: 7
  References (executor has NO interview context - be exhaustive): `docs/research/framework/architecture.md` sections on phase preservation, normalization, early pooling, array encoder, permutation canary; `docs/research/framework/evaluation.md`; `docs/experiments/bellhop_mvp_protocol.md`
  Acceptance criteria (agent-executable): `rg -n "TDOA|phase increment|coherence|calibration|permutation canary|early-pooling|phase-preservation|raw wrapped phase|independent per-channel" docs/research docs/experiments`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify every listed gate appears; failure: run `rg -n "phase jitter|random time shift|independent per-channel normalization|magnitude-only.*primary" docs/research docs/experiments` and verify such operations are banned or diagnostic-only.
  Commit: Y | docs(evaluation): add phase preservation gates

- [ ] 6. Define reproducible external-dependency and KVAE reference policy
  What to do / Must NOT do: Add a policy section, likely in `docs/research/framework/risks.md` or `docs/research/framework/data_and_simulation.md`, for external model/code references. Specify that KVAE/KVAE-Audio, EnCodec/DAC/SNAC/WavTokenizer, data2vec/BEATs, and video tokenizer ideas are research references unless explicitly imported in the MVP subgit repo after license/dependency/pinned-commit review. Do not vendor external repos into this main repo.
  Parallelization: Wave 2 | Blocked by: 2, 3 | Blocks: 7
  References (executor has NO interview context - be exhaustive): `.omo/drafts/channel-encoder-architecture.md` external evidence ledger; `docs/research/framework/risks.md`; `docs/research/framework/data_and_simulation.md`; `docs/research/framework/evaluation.md`
  Acceptance criteria (agent-executable): `rg -n "external dependency|license|pinned commit|KVAE|Encodec|DAC|SNAC|WavTokenizer|data2vec|research reference|subgit" docs/research .omo/plans/channel-encoder-architecture.md`
  QA scenarios (name the exact tool + invocation): happy: run the acceptance `rg` and verify the policy separates references from dependencies; failure: run `find . -maxdepth 4 -type d \\( -iname '*kvae*' -o -iname '*encodec*' -o -iname '*dac*' \\)` and verify no external repo was vendored into the main repo by this task.
  Commit: Y | docs(risks): define external architecture reference policy

- [ ] 7. Verify consistency, write evidence, and update the final research handoff
  What to do / Must NOT do: Run all verification commands, collect short evidence into `.omo/evidence/channel-encoder-architecture-plan-verification.md`, and update any `.omo` handoff note needed for the next executor. Confirm the plan and docs agree on repository boundary, model ladder, KVAE policy, phase gates, MVP scope, and deferred advanced methods. Do not mark success from grep alone; include a human-readable synthesis of what each command proved.
  Parallelization: Wave 3 | Blocked by: 1, 2, 3, 4, 5, 6 | Blocks: final verification
  References (executor has NO interview context - be exhaustive): all changed docs from Todos 1-6; `.omo/drafts/channel-encoder-architecture.md`; `.omo/plans/channel-encoder-architecture.md`; `.omo/evidence/`
  Acceptance criteria (agent-executable): `test -s .omo/evidence/channel-encoder-architecture-plan-verification.md && rg -n "APPROVE|repository boundary|model ladder|KVAE|phase|MVP scope|deferred" .omo/evidence/channel-encoder-architecture-plan-verification.md`
  QA scenarios (name the exact tool + invocation): happy: run every acceptance command from Todos 1-6 plus the Todo 7 acceptance command, Evidence `.omo/evidence/channel-encoder-architecture-plan-verification.md`; failure: run `rg -n "<fill|<title>|TODO|TBD|directly usable|drop-in" .omo/plans/channel-encoder-architecture.md docs/research docs/experiments` and either remove placeholders/unsafe claims or document why any remaining occurrence is intentional.
  Commit: Y | docs(channel-encoder): verify architecture plan consistency

## Final verification wave

> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [ ] F1. Plan compliance audit
  Verify that every todo maps to one of the eight Components Ledger items in `.omo/drafts/channel-encoder-architecture.md`, has references, acceptance criteria, happy/failure QA, and commit guidance. Command: `rg -n "^- \\[ \\]|Acceptance criteria|QA scenarios|Commit:" .omo/plans/channel-encoder-architecture.md`
- [ ] F2. Code quality review
  Review changed docs for contradictions, unsupported claims, and scope creep. Command: `git diff -- docs .omo/plans/channel-encoder-architecture.md .omo/drafts/channel-encoder-architecture.md`
- [ ] F3. Real manual QA
  Drive the docs as a reader: follow the framework links from `docs/experiments/bellhop_mvp_protocol.md`, confirm a new executor can identify which repo owns research docs vs MVP code, and record findings in `.omo/evidence/channel-encoder-architecture-plan-verification.md`.
- [ ] F4. Scope fidelity
  Confirm that no executable MVP code, external vendor code, generated datasets, or checkpoint files were added to the main repo. Commands: `git status --short`; `find . -maxdepth 4 -type f \\( -iname '*.pt' -o -iname '*.pth' -o -iname '*.ckpt' -o -iname '*.npy' -o -iname '*.wav' \\)`

## Commit strategy

- Prefer small documentation commits if executing manually:
  - `docs(research-boundary): define MVP subgit reproducibility boundary`
  - `docs(architecture): add channel encoder model ladder`
  - `docs(architecture): define SSL and KVAE-inspired hybrid encoder contract`
  - `docs(mvp): add channel encoder ablation scope`
  - `docs(evaluation): add phase preservation gates`
  - `docs(risks): define external architecture reference policy`
  - `docs(channel-encoder): verify architecture plan consistency`
- If the executor keeps all edits in one pass, a single commit is acceptable:
  - `docs(channel-encoder): define phase-preserving architecture plan`
- Do not commit generated datasets, checkpoints, audio files, external model repos, or MVP implementation code into the main research repo.
- If the MVP subgit repo already exists, record only its pinned commit/config/evidence references in this repo. Do not modify the subgit repo unless a separate execution plan explicitly targets it.

## Success criteria

- The current repo clearly states its role as canonical research/reproducibility control plane.
- The MVP implementation boundary is explicit and prevents training/generation churn from entering the main repo.
- The channel encoder architecture has a concrete Tiny/Small/Base/Large/XL ladder.
- KVAE/KVAE-Audio is correctly positioned as reference/ablation/inspiration, not a direct default hydroacoustic encoder.
- The hybrid SSL+VAE design is specified with phase-safe frontend, deterministic SSL latent, optional variational continuous latent, and physics probes.
- Phase, TDOA, coherence, permutation, calibration, and early-pooling gates are documented.
- The BELLHOP MVP protocol remains narrow and simulation-only.
- Advanced methods such as JEPA, DINO, Mamba, Large/XL tokenizers, and Stage 3 dynamics are deferred behind explicit evidence gates.
- Verification evidence exists under `.omo/evidence/` and does not rely on human-only inspection.
