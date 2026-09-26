# Provenance and verification — waveform/front-end review (2026-09-26)

## Scope and access

User-supplied inputs: 96 ksample/s, «32 bit», 8-element ULA, approximately 27-mm pitch (not measured). The review's 4–20-kHz, 50-ms LFM, 2-ms taper, ≥0.5-s quiet, 128-ms crop and STFT 256/64 are **author proposals**, not hardware specifications or empirically optimized results. Hypothetical sound speeds 1400/1500/1550 m/s are explicitly calculation scenarios, not observed site data. Raw/device format, source, microphone response, transmit authorization, depths/ranges and effective ADC resolution remain unavailable.

- Read repository field protocol and architecture §8 and prior direct-arrival review `outputs/direct_path_real_jepa_literature_review.md` (earlier report's arXiv texts and Europe PMC access noted in its `.provenance.md`).
- Fresh alphaXiv search returned 2411.11726 and related titles; second alphaXiv request failed `MCP error -32000 Connection closed`; did **not** retry that failed route. arXiv metadata checked with `feynman_science_database_search` for 2411.11726, 2103.14236, 2404.10316, 2308.12203; Europe PMC full-text section inventory/abstract checked for `PMC6554273` (2019, long-range Arctic). No new full-text read of 2404.10316; its contribution was limited to its **abstract**; 2103.14236/2411.11726/2308.12203 already summarized in previous reviewed report, and no new paper-specific numerical instrument defaults were inferred.
- OpenAlex search located related but noncentral DOIs, none used as numerical support. Semantic Scholar narrow queries yielded zero or unrelated results. `2508.21373` studies **communications error rates**, not waveforms for this DOA; not used to claim superiority.

## Calculation audit

- Saved original script and stdout: `experiments/signal_geometry_check.py`, `experiments/signal_geometry_check.log`. Recompute checks using independent arithmetic and test `f_alias(1400)<f_alias(1500)<f_alias(1550)`, `d*(8-1)=.189`, `N_stft(12288,256,64)=189`, `N_stft(12288,512,128)=93`, `(1/16000)*1e6=62.5`. Numerical formula is the full-sector, half-wavelength sufficient condition for conventional plane-wave ULA analysis, **not** a theorem that a broadband inference method can never operate above it.
- Claims of phase preservation, real direct-path extraction, acoustic output level or JEPA advantage: **not tested**. Their statuses remain blocked/unverified pending bench/water development and prior-to-test freeze.

## Direct source URLs

https://arxiv.org/abs/2103.14236 ; https://arxiv.org/abs/2404.10316 ; https://arxiv.org/abs/2411.11726 ; https://arxiv.org/abs/2308.12203 ; https://europepmc.org/articles/PMC6554273
