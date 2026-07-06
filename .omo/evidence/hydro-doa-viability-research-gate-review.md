# Gate Review: Hydro DOA Viability Research Synthesis

## recommendation

APPROVE

## originalIntent

The user asked in Russian for a detailed ULW/ultraresearch analysis of the idea in `docs/research_framework.md` and the prior report `.omo/ultraresearch/20260623-170253/SYNTHESIS.md`, using local files and internet sources, to assess the idea's viability and maturity.

## desiredOutcome

A research synthesis that answers whether the geometry-conditioned self-supervised hydroacoustic DOA framework is viable and sufficiently developed, while separating research-track plausibility from experiment/deployment readiness, naming risks/gaps/recommendations, and avoiding unsupported real-world or SOTA claims.

## checked artifact paths

- `docs/research_framework.md`
- `.omo/ultraresearch/20260623-170253/SYNTHESIS.md`
- `.omo/ultraresearch/20260623-172745/SYNTHESIS.md`
- `.omo/ultraresearch/20260623-172745/claim-ledger.md`
- `.omo/ultraresearch/20260623-172745/expansion-log.md`

## userOutcomeReview

The current synthesis satisfies the user-visible request. It directly scores and explains viability/maturity at `.omo/ultraresearch/20260623-172745/SYNTHESIS.md:10-22`, identifies experiment-readiness gaps at lines 86-100, separates viable research claims from not-yet-viable method/deployment claims at lines 124-144, and gives concrete recommendations at lines 146-163.

It uses both required local files: the synthesis names `docs/research_framework.md` and the prior synthesis as local inputs at lines 3-7 and lists both in the source list at lines 165-168. It uses internet sources throughout lines 40-72 and lists them at lines 169-180.

It separates research-track viability from deployment readiness. The synthesis says the idea is viable as a long-horizon research program but not as a validated method or near-term deployable system at line 10, assigns deployment readiness 2/10 at line 21, and explicitly says BELLHOP does not validate real-world performance at lines 44, 56, 60, 120-122, and 134-144.

It avoids unsupported SOTA or real-world claims. It frames LAM/AGG-RL and spatial SSL as adjacent support rather than hydroacoustic validation at lines 52-56 and labels stronger claims as not yet viable at lines 134-144. It also states the first positive claim should be limited to BELLHOP-domain randomized simulation under matched information at line 163.

## direct evidence checks

- `docs/research_framework.md:5-11` supports the synthesis claim that the document is a framework, not a final protocol, and that Novik Bay is only a motivating target.
- `docs/research_framework.md:96-107` and `docs/research_framework.md:2160-2162` support the synthesis's BELLHOP-only/simulation-only limitation.
- `docs/research_framework.md:177-223` supports the synthesis's decomposition of the central hypothesis and SSL caveat.
- `docs/research_framework.md:930-949` supports the permutation canary discussion.
- `docs/research_framework.md:1981-2038` supports the geometry-transfer/adaptation requirements.
- `docs/research_framework.md:2373-2555` supports the baseline/fair-comparison discussion.
- `docs/research_framework.md:3066-3247` supports the experiment-protocol missing-pieces list.
- `docs/research_framework.md:3851-3890` supports the success criteria and kill/pivot discussion.

External spot checks support the cited claims:

- BELLHOP manual describes beam tracing in ocean acoustic fields and convergence checks.
- ARLPY docs expose BELLHOP arrivals-to-impulse-response workflow.
- arXiv 2212.04788 states fixed-geometry supervised DNN DOA can perform poorly on different geometries and proposes geometry-aware input.
- arXiv 2312.00476 motivates spatial acoustic SSL by sim-to-real mismatch and limited annotated real data.
- Frontiers 2022 uses BELLHOP-generated multipath data and STFT phase for underwater CRNN DOA.
- arXiv 2405.02991 describes SRP/SRP-PHAT as widely used and reviews over 200 papers.
- Novik Bay sources support seasonal/shallow/understudied context.
- DOSITS supports near/far-field dependence on wavelength and array/source geometry; the synthesis labels its numeric example as inference.

## claim-ledger and expansion-log consistency

The claim ledger is consistent with the synthesis:

- Ledger line 5 matches synthesis lines 10-22 and 124-144.
- Ledger line 6 matches synthesis lines 40-44.
- Ledger line 7 matches synthesis lines 46-50.
- Ledger line 8 matches synthesis lines 52-56 and 102-112.
- Ledger line 9 matches synthesis lines 68-72.
- Ledger line 10 matches synthesis lines 86-100.

The expansion log is consistent with the synthesis:

- Expansion-log lines 18-21 say local files and web sources were opened, matching synthesis source list lines 165-180.
- Expansion-log lines 23-24 say claims are verified/refuted/unresolved and no active subagents remain, matching synthesis expansion closure lines 182-190.

## remove-ai-slops / programming review

No production code or tests were in scope. The slop/overfit pass therefore focused on research-artifact quality rather than code mechanics:

- No excessive or tautological tests are present.
- No deletion-only or requested-removal tests are present.
- No implementation-mirroring test evidence is claimed.
- No unnecessary production extraction, parsing, or normalization is present.
- No scope drift found: the synthesis stays on viability, maturity, risks, gaps, and next-step protocol.
- No false-confidence language found: unresolved and not-yet-viable claims are explicit.

The upstream code-review-report requirement is not applicable to this research-only deliverable because no code diff or tests were supplied in the requested artifact set. Direct gate review coverage replaces no evidence; it is the evidence for this read-only research gate.

## blockers

None.

## exact evidence gaps

None blocking. Residual gaps are correctly disclosed by the synthesis itself as future research/protocol gaps: no executable BELLHOP protocol, no fixed array, no real recordings, no baseline results, no Novik Bay parameterization, and no deployment measurements.

## EXPAND

none
