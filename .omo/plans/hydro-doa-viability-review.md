# Hydro DOA Viability Research Review Plan

## TL;DR
> Summary:      Produce a research-only viability review for the geometry-conditioned hydroacoustic DOA framework, separating "plausible research track" from "experiment-ready method" and "deployable system". The final synthesis must score the idea against local framework claims, prior external evidence, missing protocol inputs, and kill/pivot criteria.
> Deliverables:
> - Evidence-backed final synthesis in `.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md`
> - Claim-to-evidence scorecard covering viability, maturity, missing evidence, and next action
> - External-source ledger for all internet-supported or contested claims
> - Quality-gate checklist with go/hold/pivot decision
> Effort:       Medium
> Risk:         High - the idea is conceptually strong but current readiness depends on missing experiment protocol, real data, BELLHOP parameters, baselines, and held-out environment evidence.

## Scope
### Must have
- Use the two local source files as the local evidence base: `docs/research_framework.md` and `.omo/ultraresearch/20260623-170253/SYNTHESIS.md`.
- Research external evidence only to verify or challenge claims surfaced by those two files and the prior report's seed sources.
- Produce a final synthesis that explicitly distinguishes:
  - viability as a long-term research track;
  - readiness for the first reproducible BELLHOP-only experiment;
  - readiness for real-world or deployment claims.
- Cover 5 research axes:
  - local claim and maturity inventory;
  - external literature and source audit;
  - protocol/data/BELLHOP readiness;
  - falsification, baselines, and kill/pivot gate;
  - final synthesis and quality review.
- Include pass/fail evidence for every axis and preserve evidence under `.omo/evidence/`.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not write product code, run model training, implement simulations, or edit source code.
- Do not treat BELLHOP-only results as real-world hydroacoustic validation; the framework forbids that claim at `docs/research_framework.md:105` and `docs/research_framework.md:3867`.
- Do not expand architecture recommendations before the minimum Tier 0 claim set is assessed; Tier 0/Tier 1/Tier 2 ordering is defined at `docs/research_framework.md:300`.
- Do not claim state of the art without concrete comparison against strong classical and neural baselines, as constrained at `docs/research_framework.md:206`.
- Do not present the Novik Bay scenario as specified; the framework says exact environmental, array, and real-recording parameters are not yet available at `docs/research_framework.md:11`.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: none + research artifact checks. This is a research-only task; verification is format, citation, coverage, and consistency checking of generated research artifacts.
- QA policy: every task has agent-executed scenarios
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Local claim and maturity inventory
- Task 2: External literature and source audit
- Task 3: Protocol, data, BELLHOP, and reproducibility readiness audit
- Task 4: Falsification, baselines, and kill/pivot gate

Wave 2 (after Wave 1):
- Task 5: depends [1, 2, 3, 4]

Critical path: Task 1 -> Task 5

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 5      | 2, 3, 4              |
| 2    | none       | 5      | 1, 3, 4              |
| 3    | none       | 5      | 1, 2, 4              |
| 4    | none       | 5      | 1, 2, 3              |
| 5    | 1, 2, 3, 4 | none   | none                 |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Local claim and maturity inventory

  What to do: Build `.omo/ultraresearch/20260623-viability-review/local-claim-inventory.md` with a table: claim, local source line, current maturity, required evidence, current status, and reviewer note. Cover the central hypothesis, SSL premise, geometry-conditioning premise, BELLHOP/real-data limitation, minimum viable claim set, success criteria, and prior report scores.
  Must NOT do: Do not add external claims in this file; this task is local-source-only.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `docs/research_framework.md:7` - framework is not a final protocol or fixed model specification.
  - Pattern:  `docs/research_framework.md:9` - experiment parameters must be specified in separate protocols.
  - Pattern:  `docs/research_framework.md:177` - central hypothesis and its four parts.
  - Pattern:  `docs/research_framework.md:210` - SSL premise must be checked against actual data availability.
  - Pattern:  `docs/research_framework.md:300` - Tier 0/Tier 1/Tier 2 priority ordering.
  - Pattern:  `docs/research_framework.md:2723` - minimum viable claim set.
  - Pattern:  `docs/research_framework.md:3849` - success criteria and scorecard requirement.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:7` - prior report viability summary.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:11` - prior report numeric readiness scores.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:78` - prior report missing experiment-readiness inputs.

  Acceptance criteria (agent-executable only):
  - [ ] `test -s .omo/ultraresearch/20260623-viability-review/local-claim-inventory.md`
  - [ ] `python3 - <<'PY'\nfrom pathlib import Path\np=Path('.omo/ultraresearch/20260623-viability-review/local-claim-inventory.md')\ns=p.read_text()\nrequired=['central hypothesis','SSL premise','geometry conditioning','BELLHOP-only','minimum viable claim set','success criteria','kill/pivot','prior report']\nmissing=[x for x in required if x.lower() not in s.lower()]\nassert not missing, missing\nPY`
  - [ ] PASS evidence: every major claim is categorized as `supported locally`, `partially specified`, `not yet evidenced`, or `future-only`.
  - [ ] FAIL evidence: any local claim presented as proven without an experiment or any real-world claim based only on BELLHOP is marked as a blocker.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: local coverage table exists
    Tool:     bash
    Steps:    mkdir -p .omo/evidence && python3 - <<'PY' > .omo/evidence/task-1-local-claim-inventory.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/local-claim-inventory.md').read_text()
              for key in ['central hypothesis','SSL premise','geometry conditioning','BELLHOP-only','minimum viable claim set','success criteria']:
                  assert key.lower() in s.lower(), key
              print('PASS local claim inventory coverage')
              PY
    Expected: command exits 0 and evidence file contains `PASS local claim inventory coverage`
    Evidence: .omo/evidence/task-1-local-claim-inventory.txt

  Scenario: local-only guardrail
    Tool:     bash
    Steps:    python3 - <<'PY' > .omo/evidence/task-1-local-claim-inventory-error.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/local-claim-inventory.md').read_text().lower()
              forbidden=['demonstrated real-world performance','proven sota','deployment-ready']
              hits=[x for x in forbidden if x in s]
              assert not hits, hits
              print('PASS no unsupported local overclaim')
              PY
    Expected: command exits 0 and evidence file contains `PASS no unsupported local overclaim`
    Evidence: .omo/evidence/task-1-local-claim-inventory-error.txt
  ```

  Commit: NO | Message: `docs(research): inventory hydro doa viability claims` | Files: [`.omo/ultraresearch/20260623-viability-review/local-claim-inventory.md`, `.omo/evidence/task-1-local-claim-inventory.txt`, `.omo/evidence/task-1-local-claim-inventory-error.txt`]

- [ ] 2. External literature and source audit

  What to do: Build `.omo/ultraresearch/20260623-viability-review/external-source-ledger.md`. Start from every external source cited in the prior synthesis, then run counter-searches for BELLHOP suitability, geometry-aware DOA, acoustic SSL, classical hydroacoustic baselines, sim-to-real mismatch, and Novik Bay environmental constraints. Classify each source as primary/official, peer-reviewed, preprint, implementation, or secondary; classify support as direct hydroacoustic support, indirect acoustic support, caution/negative evidence, or not applicable.
  Must NOT do: Do not cite snippets without opening the source. Do not use non-hydroacoustic microphone-array work as direct hydroacoustic proof.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:38` - prior report external-check section.
  - External: `https://oalib-acoustics.org/website_resources/AcousticsToolbox/manual/node61.html` - BELLHOP manual seed from prior synthesis line 42.
  - External: `https://arlpy.readthedocs.io/en/latest/uwapm.html` - ARLPY BELLHOP arrivals/impulse-response seed from prior synthesis line 43.
  - External: `https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1027830/full` - underwater neural DOA seed from prior synthesis line 44.
  - External: `https://uol.de/f/6/dept/mediphysik/ag/sigproc/download/papers/SP2022_26.pdf` - geometry-aware DOA seed from prior synthesis line 45.
  - External: `https://arxiv.org/html/2312.00476v2` - spatial acoustic SSL seed from prior synthesis line 46.
  - External: `https://arxiv.org/html/2507.07066v1` - self-supervised acoustic maps seed from prior synthesis line 47.
  - External: `https://openreview.net/forum?id=bWXpJFesLS` - geometry-invariant SSL seed from prior synthesis line 47.
  - External: `https://arxiv.org/pdf/2405.02991` - SRP-PHAT review seed from prior synthesis line 48.
  - External: `https://pubs.aip.org/asa/jasa/article/83/2/571/799091/Matched-field-processing-Source-localization-in` - MFP seed from prior synthesis line 48.
  - External: `https://arl.nus.edu.sg/wp-content/uploads/2025/03/A-gradient-based-optimization-approach-for-underwater-acoustic-source-localization.pdf` - environmental mismatch seed from prior synthesis line 49.
  - External: `https://physical-oceanography.ru/repository/issues/2021/06/03/` - Novik Bay local-oceanography seed from prior synthesis line 50.
  - External: `https://www.mdpi.com/2077-1312/11/10/1973` - Novik Bay geography/environment seed from prior synthesis line 50.

  Acceptance criteria (agent-executable only):
  - [ ] `test -s .omo/ultraresearch/20260623-viability-review/external-source-ledger.md`
  - [ ] `python3 - <<'PY'\nfrom pathlib import Path\ns=Path('.omo/ultraresearch/20260623-viability-review/external-source-ledger.md').read_text().lower()\nfor key in ['bellhop','geometry-aware','self-supervised','mvdr','music','srp-phat','matched-field','sim-to-real','novik']:\n    assert key in s, key\nassert s.count('counter-search') >= 5\nPY`
  - [ ] PASS evidence: each final synthesis claim about external literature has at least one source classification and one source-specific caveat.
  - [ ] FAIL evidence: any source that supports only generic room-acoustic SSL is not allowed to support a direct hydroacoustic deployment claim.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: source ledger covers all external territories
    Tool:     bash
    Steps:    mkdir -p .omo/evidence && python3 - <<'PY' > .omo/evidence/task-2-external-source-ledger.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/external-source-ledger.md').read_text().lower()
              required=['bellhop','geometry-aware','self-supervised','classical','matched-field','sim-to-real','novik bay']
              missing=[x for x in required if x not in s]
              assert not missing, missing
              print('PASS external territory coverage')
              PY
    Expected: command exits 0 and evidence file contains `PASS external territory coverage`
    Evidence: .omo/evidence/task-2-external-source-ledger.txt

  Scenario: no uncaveated indirect evidence
    Tool:     bash
    Steps:    python3 - <<'PY' > .omo/evidence/task-2-external-source-ledger-error.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/external-source-ledger.md').read_text().lower()
              assert 'indirect acoustic support' in s
              assert 'direct hydroacoustic support' in s
              assert 'caution' in s or 'negative evidence' in s
              print('PASS support classes present')
              PY
    Expected: command exits 0 and evidence file contains `PASS support classes present`
    Evidence: .omo/evidence/task-2-external-source-ledger-error.txt
  ```

  Commit: NO | Message: `docs(research): audit hydro doa external evidence` | Files: [`.omo/ultraresearch/20260623-viability-review/external-source-ledger.md`, `.omo/evidence/task-2-external-source-ledger.txt`, `.omo/evidence/task-2-external-source-ledger-error.txt`]

- [ ] 3. Protocol, data, BELLHOP, and reproducibility readiness audit

  What to do: Build `.omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md`. Evaluate whether the idea is ready for the first reproducible BELLHOP-only experiment. Produce a gap table for array geometry, sampling/preprocessing, source families, BELLHOP configuration, Novik Bay assumptions, noise/interference, train/test splits, metrics, reproducibility artifacts, and compute/latency reporting.
  Must NOT do: Do not accept "TBD" as ready. Unspecified numeric or split inputs are blockers or partial blockers.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `docs/research_framework.md:109` - target-domain placeholders that must be specified.
  - Pattern:  `docs/research_framework.md:139` - Novik Bay-specific protocol requirements.
  - Pattern:  `docs/research_framework.md:416` - sampling-rate, basebanding, chunking policy.
  - Pattern:  `docs/research_framework.md:2041` - data levels, including BELLHOP and real-data stages.
  - Pattern:  `docs/research_framework.md:2090` - BELLHOP-based propagation requirements.
  - Pattern:  `docs/research_framework.md:2268` - real-data availability constraints.
  - Pattern:  `docs/research_framework.md:2288` - data splitting principles and leakage risks.
  - Pattern:  `docs/research_framework.md:2319` - hydroacoustic validation philosophy.
  - Pattern:  `docs/research_framework.md:3006` - reproducibility requirements.
  - Pattern:  `docs/research_framework.md:3066` - experiment-level protocol skeleton.
  - Pattern:  `docs/research_framework.md:3220` - minimal v1 protocol recommendation.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:63` - prior report states no experiments, dataset, array specification, BELLHOP distribution, real recordings, or Novik Bay ground truth.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:78` - prior report lists missing experiment-readiness inputs.

  Acceptance criteria (agent-executable only):
  - [ ] `test -s .omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md`
  - [ ] `python3 - <<'PY'\nfrom pathlib import Path\ns=Path('.omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md').read_text().lower()\nrequired=['array geometry','bellhop','novik bay','sampling','preprocessing','train','test','split','noise','interference','reproducibility','compute']\nmissing=[x for x in required if x not in s]\nassert not missing, missing\nPY`
  - [ ] PASS evidence: the audit states whether first BELLHOP-only readiness is `ready`, `partially ready`, or `not ready`, with blockers.
  - [ ] FAIL evidence: readiness is `not ready` or `partially ready` if array geometry, BELLHOP environment distribution, split units, and baseline definitions are missing.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: protocol readiness gap table covers mandatory blocks
    Tool:     bash
    Steps:    mkdir -p .omo/evidence && python3 - <<'PY' > .omo/evidence/task-3-protocol-readiness.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md').read_text().lower()
              required=['task definition','array configuration','signal and input','bellhop configuration','dataset and split','baseline configuration','evaluation and reporting','compute']
              missing=[x for x in required if x not in s]
              assert not missing, missing
              print('PASS protocol blocks covered')
              PY
    Expected: command exits 0 and evidence file contains `PASS protocol blocks covered`
    Evidence: .omo/evidence/task-3-protocol-readiness.txt

  Scenario: unresolved placeholders are treated as blockers
    Tool:     bash
    Steps:    python3 - <<'PY' > .omo/evidence/task-3-protocol-readiness-error.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md').read_text().lower()
              assert 'blocker' in s or 'partial blocker' in s
              assert 'ready without numeric assumptions' not in s
              print('PASS placeholders gated')
              PY
    Expected: command exits 0 and evidence file contains `PASS placeholders gated`
    Evidence: .omo/evidence/task-3-protocol-readiness-error.txt
  ```

  Commit: NO | Message: `docs(research): audit hydro doa protocol readiness` | Files: [`.omo/ultraresearch/20260623-viability-review/protocol-readiness-audit.md`, `.omo/evidence/task-3-protocol-readiness.txt`, `.omo/evidence/task-3-protocol-readiness-error.txt`]

- [ ] 4. Falsification, baselines, and kill/pivot gate

  What to do: Build `.omo/ultraresearch/20260623-viability-review/viability-gate.md`. Define concrete pass/fail gates for: SSL label efficiency, geometry transfer, BELLHOP environment generalization, baseline competitiveness, permutation canary, Stage 3 deferral, real-data boundary, and architecture expansion. Include "viable", "underdeveloped", and "pause/pivot" definitions.
  Must NOT do: Do not let a positive average metric override failure on held-out geometry, permutation canary, BELLHOP environment split, or strong baseline comparison.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `docs/research_framework.md:930` - permutation and ordering policy.
  - Pattern:  `docs/research_framework.md:946` - permutation canary is required before Stage 2 reporting.
  - Pattern:  `docs/research_framework.md:1981` - geometry adaptation protocol.
  - Pattern:  `docs/research_framework.md:2373` - baseline and fair comparison protocol.
  - Pattern:  `docs/research_framework.md:2558` - evaluation metrics.
  - Pattern:  `docs/research_framework.md:2654` - claim-to-evidence mapping.
  - Pattern:  `docs/research_framework.md:2692` - statistical reliability and failure reporting.
  - Pattern:  `docs/research_framework.md:2723` - minimum viable claim set.
  - Pattern:  `docs/research_framework.md:3488` - weak baseline comparison risk.
  - Pattern:  `docs/research_framework.md:3880` - kill/pivot criteria.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:101` - prior report recommendation to freeze around a minimum viable claim set.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:106` - prior report required gates.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:114` - prior report pivot rule.

  Acceptance criteria (agent-executable only):
  - [ ] `test -s .omo/ultraresearch/20260623-viability-review/viability-gate.md`
  - [ ] `python3 - <<'PY'\nfrom pathlib import Path\ns=Path('.omo/ultraresearch/20260623-viability-review/viability-gate.md').read_text().lower()\nrequired=['ssl','label efficiency','geometry transfer','permutation canary','bellhop','mvdr','music','srp-phat','matched-field','kill','pivot','stage 3']\nmissing=[x for x in required if x not in s]\nassert not missing, missing\nPY`
  - [ ] PASS evidence: the gate defines measurable conditions under which the idea remains viable as a research track.
  - [ ] FAIL evidence: the gate defines conditions under which the idea is underdeveloped or must pause/pivot instead of adding architecture.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: viability gate contains falsifiable blockers
    Tool:     bash
    Steps:    mkdir -p .omo/evidence && python3 - <<'PY' > .omo/evidence/task-4-viability-gate.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/viability-gate.md').read_text().lower()
              for key in ['viable if','underdeveloped if','pause/pivot if','permutation canary','50% label budget','mvdr','music']:
                  assert key in s, key
              print('PASS viability gate is falsifiable')
              PY
    Expected: command exits 0 and evidence file contains `PASS viability gate is falsifiable`
    Evidence: .omo/evidence/task-4-viability-gate.txt

  Scenario: no architecture expansion before Tier 0
    Tool:     bash
    Steps:    python3 - <<'PY' > .omo/evidence/task-4-viability-gate-error.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/viability-gate.md').read_text().lower()
              assert 'stage 3' in s and ('defer' in s or 'only after tier 0' in s)
              assert 'dino' not in s or 'tier 2' in s
              print('PASS architecture expansion constrained')
              PY
    Expected: command exits 0 and evidence file contains `PASS architecture expansion constrained`
    Evidence: .omo/evidence/task-4-viability-gate-error.txt
  ```

  Commit: NO | Message: `docs(research): define hydro doa viability gate` | Files: [`.omo/ultraresearch/20260623-viability-review/viability-gate.md`, `.omo/evidence/task-4-viability-gate.txt`, `.omo/evidence/task-4-viability-gate-error.txt`]

- [ ] 5. Final synthesis and quality gate review

  What to do: Write `.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md` in Russian, keeping technical terms where useful. The synthesis must answer: "Is the idea viable, how developed is it, what evidence is missing, and what progress would make it viable?" Include executive conclusion, research axes, external evidence summary, local maturity scorecard, protocol readiness, falsification gates, underdeveloped areas, next research steps, and `## EXPAND`.
  Must NOT do: Do not present internet sources as stronger than they are; do not omit negative or cautionary evidence; do not convert this into an implementation plan.

  Parallelization: Can parallel: NO | Wave 2 | Blocks: [] | Blocked by: [1, 2, 3, 4]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `docs/research_framework.md:1` - framework title and topic.
  - Pattern:  `docs/research_framework.md:17` - proposed geometry-conditioned SSL backbone.
  - Pattern:  `docs/research_framework.md:27` - BELLHOP as baseline simulation scenario.
  - Pattern:  `docs/research_framework.md:29` - final validation target is real hydroacoustic data.
  - Pattern:  `docs/research_framework.md:85` - array coordinates, aperture, spacing, calibration, and synchronization are unknown.
  - Pattern:  `docs/research_framework.md:151` - simplified chirp simulations are insufficient for deployment.
  - Pattern:  `docs/research_framework.md:218` - BELLHOP-only labels are available by construction, so SSL overclaiming is invalid.
  - Pattern:  `docs/research_framework.md:3220` - minimal v1 protocol recommendation.
  - Pattern:  `docs/research_framework.md:3240` - protocol validity rules.
  - Pattern:  `docs/research_framework.md:3703` - assumptions, including real recordings not yet available.
  - Pattern:  `docs/research_framework.md:3880` - kill/pivot criteria.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:52` - prior report viability positives.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:61` - prior report negative readiness findings.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:89` - prior report ranked risks.
  - Pattern:  `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:116` - prior report bottom line.
  - Test:     `.omo/evidence/task-1-local-claim-inventory.txt` - confirms local claim coverage.
  - Test:     `.omo/evidence/task-2-external-source-ledger.txt` - confirms external territory coverage.
  - Test:     `.omo/evidence/task-3-protocol-readiness.txt` - confirms protocol block coverage.
  - Test:     `.omo/evidence/task-4-viability-gate.txt` - confirms falsifiable gate coverage.

  Acceptance criteria (agent-executable only):
  - [ ] `test -s .omo/ultraresearch/20260623-viability-review/SYNTHESIS.md`
  - [ ] `python3 - <<'PY'\nfrom pathlib import Path\ns=Path('.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md').read_text().lower()\nrequired=['краткий вывод','research axes','scorecard','bellhop','geometry','ssl','baselines','kill','pivot','underdeveloped','expand']\nmissing=[x for x in required if x not in s]\nassert not missing, missing\nPY`
  - [ ] PASS evidence: final synthesis states that the idea is viable as a research track only if Tier 0 evidence, fair baselines, geometry transfer, and BELLHOP generalization pass.
  - [ ] FAIL evidence: final synthesis marks the idea underdeveloped if it lacks array/BELLHOP parameters, held-out environment counts, fair baselines, permutation canary, label-efficiency result, or real-data boundary.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: final synthesis quality gate
    Tool:     bash
    Steps:    mkdir -p .omo/evidence && python3 - <<'PY' > .omo/evidence/task-5-final-synthesis.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md').read_text().lower()
              required=['краткий вывод','жизнеспособ', 'проработан', 'bellhop', 'novik', 'geometry', 'ssl', 'mvdr', 'music', 'scorecard', '## expand']
              missing=[x for x in required if x not in s]
              assert not missing, missing
              print('PASS final synthesis contains required decision content')
              PY
    Expected: command exits 0 and evidence file contains `PASS final synthesis contains required decision content`
    Evidence: .omo/evidence/task-5-final-synthesis.txt

  Scenario: final synthesis does not overclaim
    Tool:     bash
    Steps:    python3 - <<'PY' > .omo/evidence/task-5-final-synthesis-error.txt
              from pathlib import Path
              s=Path('.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md').read_text().lower()
              forbidden=['готовая методика','доказанная real-world performance','deployment-ready','proven state-of-the-art','proven sota']
              hits=[x for x in forbidden if x in s]
              assert not hits, hits
              assert 'real' in s and ('будущ' in s or 'future' in s or 'not yet' in s)
              print('PASS final synthesis avoids overclaiming')
              PY
    Expected: command exits 0 and evidence file contains `PASS final synthesis avoids overclaiming`
    Evidence: .omo/evidence/task-5-final-synthesis-error.txt
  ```

  Commit: NO | Message: `docs(research): synthesize hydro doa viability review` | Files: [`.omo/ultraresearch/20260623-viability-review/SYNTHESIS.md`, `.omo/evidence/task-5-final-synthesis.txt`, `.omo/evidence/task-5-final-synthesis-error.txt`]

## Final verification wave (MANDATORY - after all implementation tasks)
> Runs in PARALLEL. ALL must APPROVE. Surface results to the caller and wait for an explicit "okay" before declaring complete.
- [ ] F1. Plan compliance audit - every task done, every acceptance criterion met
- [ ] F2. Code quality review - diagnostics clean, idioms match, no dead code
- [ ] F3. Real manual QA - every QA scenario executed with evidence captured
- [ ] F4. Scope fidelity - nothing extra shipped beyond Must-Have, nothing Must-NOT-Have introduced

## Commit strategy
- One logical change per commit. Conventional Commits (`<type>(<scope>): <subject>` body + footer).
- Atomic: every commit builds and passes tests on its own.
- No "WIP" / "fix typo squash later" commits on the final branch - clean up before merge.
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/hydro-doa-viability-review.md`.
- For this research-only assignment, do not create a git commit unless the caller explicitly asks. If asked to commit research artifacts, use `docs(research): evaluate hydro doa viability`.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
- The final synthesis makes a defensible decision:
  - Viable as a research track if external literature supports plausibility, the local framework remains conservatively framed, and Tier 0 falsification gates are executable.
  - Underdeveloped if the first BELLHOP-only protocol still lacks numeric array, environment, split, baseline, metric, and reproducibility specifications.
  - Pause or pivot if the minimum viable claim set fails the no-geometry, 50% label-budget, MVDR/MUSIC, permutation-canary, or held-out-environment gates.

## EXPAND
- LEAD: Define a minimum independent held-out BELLHOP environment count and variance threshold for the first claim, seeded by `docs/research_framework.md:3406` and `docs/research_framework.md:3421`.
- LEAD: Verify Novik Bay bathymetry, seasonal SSP, bottom, surface/ice, and feasible far-field assumptions from primary local/oceanographic sources, seeded by `docs/research_framework.md:139` and prior synthesis line 50.
- LEAD: Find direct hydroacoustic geometry-conditioned or self-supervised DOA papers beyond room/microphone-array analogs; current prior synthesis says support is plausible but indirect at `.omo/ultraresearch/20260623-170253/SYNTHESIS.md:46`.
- LEAD: Validate BELLHOP arrivals-to-impulse-response construction best practice and convergence checks against official/manual sources, seeded by prior synthesis lines 42-43 and `docs/research_framework.md:3137`.
