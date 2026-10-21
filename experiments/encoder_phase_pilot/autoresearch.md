# Ограниченный пилот обучаемых энкодеров — план до кода (2026-10-02)

Статус: completed — исходный план ниже сохранён; итоги в ledger. Пользователь разрешил сравнить обученные энкодеры; среда uv/CUDA прошла smoke-тест. Прямое исполнение без делегирования. `/autoresearch` не является доступным tool в этой сессии: используется обычный bounded shell benchmark с журналом каждого запуска/решения; автоматического поиска/keep-revert архитектур нет.

## Бюджет и фиксированная постановка

- NumPy/PyTorch из uv.lock, GPU, float32, без AMP/torch.compile. 3 paired seeds: 101/202/303.
- Три малые инженерные сети, не канонический E-M: real Conv; complex Conv с радиальным нелинейным модулем; complex-stem + один малый Conformer-like temporal block + local-frequency Conv. Одинаковый выход C=16, F=43, T_e=15 (stride2); разное число параметров честно измерить. Не рейтинг при равном compute.
- 2048 mono train / 256 development исходных источников, 300 шагов AdamW lr=.001 wd=.0001 batch16 для каждой сети. Последний checkpoint, без early stopping/выбора по тесту. Общий decoder C→2 и bilinear resize к исходной TF. Loss реконструкции чистой STFT (не EMA/JEPA, не latent loss), нет коллапса к постоянной цели как приемлемого решения. Никакого bypass из raw к decoder.
- Источник: stationary random multitone, все FFT-биновые частоты 11..53 при fs96k/FFT256 (4125..19875 Hz), L2048; непрерывная аналитическая дробная задержка через фазу каждой синусоиды, без FFT circular-shift raw. Амплитуды/фазы источника случайны, нормированная генерируемая чистая мощность; одна source-реализация = parent group. Только независимый AWGN, train SNR Uniform[0,20]dB. Без BELLHOP/эхо/поля. Датчики отдельно одним E, без доступа к u/координатам/другому каналу.
- Geometry only for generation/truth: d=.027m c1500m/s |u|≤.8, tau0=0 tau1=d*u/c. TDOA tau0-tau1; phase target clean D cross-phase на 12kHz (bin32). Межчастотная Hann-утечка может отличать фазу STFT от идеальной exp(-iωτ); не требовать ложного совпадения.
- Probe sources 512 disjoint; test sources 512 disjoint, matched по всем сетям/seeds. SNR test clean/0/10/20dB; разные noise seeds, одинаковые clean sources. На каждый run отдельно один одинаковый ridge readout: per-frequency 16×16 bilinear channel products, average по t, затем averaging frequency for delay и bin32 products for phase. Outputs delay normalized + cos/sin. Train-derived probe scaling, ridge .01, без подбора. Направление/истинная фаза/сигнал D не входят в features. Targets доступны только на разрешённой probe fit split. Zero-delay и mean-phase predictor = обязательный baseline. Raw Re/Im и необученный E каждого run обязательны; magnitude control при возможности. Probe raw имеет меньше признаков, это reference, не matched params.
- 9 training runs максимум, общий запуск ≤15min. Если OOM/finite fail — сохранить failed run, не менять параметры после просмотра теста. Размеры/ресурсы, train/dev loss, feature std, invalid coverage, signed-delay median/p95, circular phase median/p95 по каждому seed; агрегаты medians across seeds, не статистическая значимость/независимые акустические среды.
- Веса вне Git `/home/niksm/.cache/hydroacoustic-doa/encoder-phase-pilot-20261002/`, маленькие JSON/log/config/code в Git. Hash/source versions и parent IDs проверять, тест не использовать для выбора.

## Минимальные проверки до реализации

1. Disjoint source seeds/IDs; shared positive scale только train; paired same source across sensors; noise независим, clean identity, signed delay ±u/0.
2. Analytical single-tone phase sign/truth; Torch STFT vs NumPy уже smoke PASS. Complex convolution against direct complex formula, radial phase equivariance numerical unit test.
3. Каждая сеть shape, finite forward/backward; freeze eval all state; identical batches/order across three models same seed; no coordinate/channel mixing/raw bypass.
4. Probe finite estimates, zero vector invalid; no clipping/symmetry reflection; p95 signed-delay error без кругового wrapping.
5. Small JSON trace/table consistency, old JSON unchanged, register new paths, full validator/diff.

## Интерпретация

Это прямой-wave **reconstruction pretraining**, не Stage-1 JEPA, не полный E gate, не выбор основного scaffold. Single geometry/narrow sector/stationary sources/repeated windows limit conclusions. Feature variance and denoising improvements do not prove general phase preservation. Fixed probe failure может быть failure считывателя, не доказательством уничтожения информации.

## Ledger

- plan: saved before implementation.
- code/unit tests: PASS; 9/9 training runs completed, no architecture selected.
- diagnosis: development reconstruction worse than noisy raw baseline in all models; evidence retained, not silently fixed.
- verification: 9 checkpoint reloads/readouts + one 300-step replay PASS; split hash counts corrected from uniform512 to actual2048/256/512/512.
- analysis: generated in canonical outputs/mono_phase_encoder_feasibility.md; no main-scaffold promotion or E gate.
- optional magnitude control executed after runs as preregistered diagnostic; no model/probe hyperparameter changed.
- execution: ordinary shell; slash workflow not an available tool.
- checkpoint weights external; re-running benchmark overwrites outputs/weights. New hypotheses require a new directory and new evaluation source seeds.
