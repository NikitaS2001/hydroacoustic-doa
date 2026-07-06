# ULW Evidence: BELLHOP MVP Protocol

Task: create `docs/experiments/bellhop_mvp_protocol.md` as the first numeric BELLHOP-only MVP protocol outside the framework.

Tier: LIGHT. This is a documentation-only protocol artifact with no code, runtime process, database, external integration, or security behavior.

Success criteria:
- Protocol file exists and is non-empty.
- Protocol links to the split framework files instead of embedding framework content.
- Protocol contains numeric parameters for task, arrays, signal/preprocessing, BELLHOP environment counts, dataset size, training budgets, metrics, gates, and kill/pivot thresholds.
- Protocol is explicitly simulation-stage only and blocks real-world/Novik Bay deployment claims.

Evidence:
- `PASS_PROTOCOL_EXISTS`
- `PASS_PROTOCOL_COVERAGE`
- `PASS_PROTOCOL_LINKS`
- `PASS_NO_REAL_WORLD_OVERCLAIM`
- `wc -l docs/experiments/bellhop_mvp_protocol.md`: 496 lines
- Follow-up update: `PASS_SOUND_CARD_SIGNAL_SSL_UPDATE`

Self-review:
- Re-read the protocol outline and checks.
- Confirmed the protocol uses framework references under `docs/research/framework/`.
- Confirmed it includes concrete values: `32/8/12` BELLHOP environments, `500-3000 Hz`, `6` hydrophones, `0.25 m` ULA spacing, `2.0 s` chunks, `120,000` approximate train examples, `50%` label-efficiency gate, and `15%` geometry-transfer threshold.
- Follow-up confirmed the signal/sample-rate section now uses `48000 Hz` master/acquisition rate, coherent decimation to `12000 Hz`, and a stage-wise SSL execution order.
- Confirmed it limits claims to BELLHOP-only simulation and includes a mandatory limitation statement.
- No runtime state, servers, tmux sessions, browser contexts, temp dirs, or bound ports were created.
- No commit was made; the user did not request one.
