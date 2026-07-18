# Строгий аудит плана исследования Hydro-DOA World Model

Дата аудита: **2026-07-17**. Проверены два последовательных документарных checkpoint: C1 `89ce838e9a38621a33a0a1b6b2cd10dfbc1913ba` (`docs(index): move framework index under docs`) и C2 `09d16fa8769dde7da73a0bdc06abc67a6df0ea85` (`docs(protocol): checkpoint BELLHOP MVP methodology draft`). C1 является предком C2; настоящий аудит относится к состоянию корпуса на C2.

Проверяемый корпус: `README.md`, `docs/README.md`, все `docs/research/framework/*.md` и `docs/experiments/bellhop_mvp_protocol.md` — **5938 строк** по воспроизводимой команде `wc -l README.md docs/README.md docs/research/framework/*.md docs/experiments/bellhop_mvp_protocol.md | tail -1`. Это аудит документации, а не результатов: код, данные, запуски solver/model, power analysis и экспериментальные артефакты отсутствуют; ни один эмпирический gate не считается пройденным.

## Повторный аудит после изменений — актуальный вердикт

Внутренняя adversarial-проверка по направлениям соответствия цели, научной корректности, механики документа, research integrity и git/context дала общий вердикт **FAIL / NO-GO для полной генерации данных**. Это внутренняя проверка одной агентной системы, не внешняя репликация и не эмпирическая валидация. План стал заметно сильнее, но всё ещё не является замкнутой исполнимой спецификацией.

| Критерий | Было | Сейчас | Повторный вердикт |
|---|---:|---:|---|
| Научная перспективность | 7/10 | **7/10** | Постановка остаётся сильной и фальсифицируемой |
| Реализуемость MVP | 4/10 | **4/10** | Существенный прогресс, но новые/оставшиеся P0 делают запуск преждевременным |
| Полнота описания | 7/10 концептуально; 4/10 исполнимо | **8/10 концептуально; 5/10 исполнимо** | Протокол гораздо подробнее, однако содержит взаимоисключающие числа и незамкнутые физические контракты |
| Компонентная новизна | 2/10 | **2/10** | Не изменилась; большинство компонентов имеет прямой prior art |
| Комбинационная новизна | 5/10 unresolved | **5/10 unresolved** | Возможна только как проверенная интеграция, не как новый objective/primitive |
| Реальная готовность | 2/10 | **2/10** | По-прежнему TRL 2→3; real-data и Novik Bay validation отсутствуют |

### Что действительно улучшено

- Добавлены две train-геометрии и неколлинеарная конфигурация, а также matched coordinate ablations (`bellhop_mvp_protocol.md:53-168`).
- CW получил явное исключение из несовместимого onset/trailing-context правила (`:329-332`).
- TDOA-gate заменён на frequency-scaled PDOA/IPD recovery, а calibration gate теперь сравнивается с аналитически введённой фазовой ошибкой (`:1093-1148`).
- Добавлены dev-test/sealed роли, access log, hierarchical paired estimator, pilot coverage, LHS и factorial OOD panels (`:477-796,1067-1087,1203-1225`).
- Early-pooling больше не блокирует основной unpooled путь (`:1148`).
- SSL-specific kill criteria отделены от Tier-0 geometry claim (`:1150-1176`).
- Новизна сформулирована консервативно как проверяемая интеграция, а не firstness (`overview.md:213-224`).

### Статус прежних P0-блокеров

| Прежний блокер | Статус | Основание |
|---|---|---|
| Геометрический эффект не идентифицируем | **Частично исправлен** | Две train-геометрии и matched modes добавлены, но `shuffled-coordinates` совместно переставляет сигнал и координаты и проверяет equivariance, а не зависимость от правильных координат; Tier-0 также снова описывает другой compact TCN/CRNN baseline (`:156-168,872-919`) |
| Broadband/azimuth BELLHOP contract отсутствует | **Открыт в новой форме** | Grid и bearing появились, но solver не выбран согласованно, а интерполяция sparse complex `H(f)` физически не замкнута (`:396-422,588-620`) |
| Слишком слабый TDOA gate | **Исправлен** | Frequency-scaled IPD gate с `τ_max=3 μs` (`:1122-1144`) |
| Нефизичный calibration threshold | **Исправлен по принципу** | Сравнение с аналитическим IPD и ratio/sign gates (`:1141-1147`); остаётся ошибка моделирования clock offset постоянным phase rotation |
| Unit of inference отсутствует | **Частично исправлен** | Environment-level paired bootstrap задан (`:1067-1075`), но sealed allocation противоречит собственной минимальной мощности |
| Adaptive test reuse | **Частично исправлен** | Sealed policy/log добавлены; geometry-only dev-test панель больше не использует Rect-5 (`:506-516,784-796`). Доступ всё ещё разрешён для нескольких frozen configurations — это остаётся уточнить. |
| Dataset coverage не обоснован | **Частично исправлен** | Pilot/LHS/coverage gates добавлены, однако allocations противоречат арифметике и power остаётся будущим условием (`:467-495,658-782,1074`) |

## Статус P0.1–P0.11 на checkpoint C2

| ID | Статус на C2 | Краткое основание |
|---|---|---|
| P0.1 | **Открыт** | `4` sealed environments против floor `10`; единый global access не задан |
| P0.2 | **Исправлен в документации** | Dev-test geometry-only использует Square-4, не Rect-5 |
| P0.3 | **Открыт** | Sparse-complex broadband interpolation не замкнута по delay spread |
| P0.4 | **Открыт** | Arrivals/3-D receiver/mode `C` задают несовместимый solver path |
| P0.5 | **Открыт** | Matched geometry control меняет backbone; mismatched-coordinate control отсутствует |
| P0.6 | **Частично исправлен** | Per-geometry/SNR multiplier исправлены; reuse, runtime, units и единый allocation source ещё дефектны |
| P0.7 | **Открыт** | Sealed primary band включает aliasing Rect-5 |
| P0.8 | **Открыт** | Supervised Tier-0, SSL и adaptation primary mode не заморожены |
| P0.9 | **Открыт** | Duration draws и convolution/crop contract несовместимы |
| P0.10 | **Открыт** | Cross-solver gate сравнивает несопоставимые outputs |
| P0.11 | **Открыт** | Nearest-sample arrivals несовместимы с `<3 μs` IPD gate |

Подробные основания и минимальные исправления приведены ниже; эта матрица фиксирует статус каждого P0 без утверждений об эмпирическом прохождении.

### P0.1 Sealed design противоречит сам себе

Sealed split содержит `4` environments (`bellhop_mvp_protocol.md:343-349,666-672`), но kill criterion автоматически отвергает результат при числе successful sealed environments меньше `10` (`:1159-1168`). При environment как верхнем unit of inference четыре кластера также не дают надёжной confirmatory мощности; тысячи вложенных examples этого не исправляют.

Исправление: число sealed environments определяется pilot power analysis, но не может быть ниже собственного floor `10`; allocation, channel-bank table, dataset counts и access policy обновляются совместно.

### P0.2 Утечка Rect-5 в dev-test — исправлена в checkpoint C2

Rect-5 запрещён для model selection (`:126-155`), а geometry-only OOD panel в текущем C2 использует только Square-4 (`:825-837`). Поэтому прежнее противоречие «Rect-5 одновременно sealed и dev-test» **разрешено в документации**.

Остающийся соседний дефект относится к P0.1: политика всё ещё допускает несколько обращений по frozen configurations, поэтому единственный глобальный preregistered confirmatory access не зафиксирован. Rect-5 и его derived examples/manifests должны оставаться недоступными до этого доступа.

### P0.3 Broadband synthesis физически незамкнут

План интерполирует complex `H(f)` между BELLHOP runs с шагом `250 Hz`; даже “very fine” reference имеет шаг `50 Hz` (`:408-415,588-618`). Но путь с задержкой `τ` содержит фазу `exp(-j2πfτ)`: при retained delay до `2 s` консервативное Nyquist-sampling complex response требует `Δf ≤ 1/(2τ) = 0.25 Hz` (для одной только IFFT delay-unambiguity — `Δf < 1/τ = 0.5 Hz`). Source bandwidth не задаёт требуемую частотную дискретизацию канала. Direct-path-only convergence также не валидирует multipath synthesis.

Исправление: либо сопоставлять paths между частотами и интерполировать amplitude/delay после удаления reference delay, либо выбирать grid по измеренному excess-delay spread; затем валидировать полный multipath IR, а не только direct-path examples.

### P0.4 BELLHOP solver/mode не определён исполнимо

Протокол одновременно требует arrivals, “3-D receiver set” и solver mode `C` (`:396-422`). В BELLHOP arrivals и coherent/incoherent TL — разные run types; обычный BELLHOP является range-depth solver, а `arlpy.uwapm` не превращает произвольные planar `(x,y)` coordinates в совместный 3-D receiver run автоматически.

Минимальный путь для horizontally invariant MVP: явно выбрать 2-D BELLHOP arrivals и определить `r_i = hypot(source_x-x_i, source_y-y_i)` для каждого sensor при общих depths, затем аналитически проверить coherent pairwise phase. Если нужен BELLHOP3D/Nx2D, назвать конкретный solver/version/input format и проверить известные 3-D receiver limitations BellhopCUDA.

### P0.5 Геометрический control остаётся причинно нечистым

Section 9.4 обещает один backbone с изменением только geometry input (`:872-883`), но Tier-0 снова задаёт no-geometry как compact TCN/CRNN, а proposed model как pairwise Transformer (`:899-919`). Совместная перестановка signals+coordinates является правильным permutation canary, но не negative control для неверных coordinates.

Исправление: оставить exactly matched geometry-disabled Transformer и добавить отдельный mismatched-coordinate control, где координаты переставляются относительно signal channels. Topology-specific/fixed-slot baseline следует показывать отдельно, а не называть matched ablation.

### P0.6 Dataset arithmetic — частично исправлена

Прежние ошибки столбца `per geometry` в `:467-475` исправлены: dev-test теперь 12k на геометрию при 48k total, sealed 12k при одной Rect-5, Novik 4k при одной geometry. SNR вынесен в постобработку и больше не умножает число BELLHOP-конфигураций.

Статус остаётся **частично исправлен**: no-reuse total и границы повторного использования не выведены из одной allocation table, runtime table не учитывает все narrowband runs/единицы и sealed allocation противоречит power floor. Все derived counts, reuse factors, units и runtime должны вычисляться из одного pilot/power-aware контракта; существующие исправления не являются эмпирической проверкой стоимости.

### P0.7 Primary endpoint смешан с преднамеренным spatial aliasing

Rect-5 имеет `f_max_eff≈1460 Hz`, но является единственной sealed geometry и primary endpoint на band `500–3000 Hz` (`:185-202,1072`). Для high-frequency CW часть задач фундаментально неоднозначна; это смешивает geometry transfer с physical non-identifiability.

Исправление: использовать alias-safe sealed geometry либо preregister alias-safe primary band, а aliased band публиковать только как stress panel. Для planar arrays оценивать полный steering manifold/baseline lattice, а не только minimum spacing.

### P0.8 Protocol scope не заморожен

Единственный MVP claim не включает SSL (`:17-31`), SSL/VAE названы optional exploratory (`:885-897,1150-1157`), но prescribed execution обязательно обучает Stage 1/2 SSL (`:936-944`). Adaptation одновременно предлагает zero-shot, head-only, adapter и full fine-tuning без primary mode и без отдельного adaptation split (`:1021-1026`).

Исправление: Tier-0 geometry paper выполняется supervised-only; SSL становится отдельным preregistered secondary claim. Для sealed Rect-5 primary endpoint используется zero-shot; любые labeled adaptation modes получают отдельный adaptation/dev split и не касаются sealed test.

### P0.9 Signal-generation contract всё ещё допускает невозможные draws

Non-CW source должен иметь onset `≥0.10 s` и trailing context `≥0.10 s` в `2.0 s` chunk, поэтому maximum active duration равна `1.8 s`; LFM и noise burst всё ещё допускают `2.0 s` (`:683-709`). Также convolution 2 s signal с arrivals до 2 s даёт почти 4 s output, но crop/alignment policy отсутствует.

Исправление: conditional sampling/rejection с `duration ≤ chunk-onset-tail`; заморозить pre-roll, convolution length, crop reference и label timestamp.

### P0.10 Cross-solver gate сравнивает несопоставимые величины

Протокол требует phase difference между `KRAKEN/SCOOTER` и BELLHOP arrivals (`:422,433`). KRAKEN — normal-mode solver, SCOOTER — FFP solver; общий сопоставимый выход этих методов и BELLHOP — coherent complex pressure/transfer function на одинаковых частоте и receivers, а не ray-arrival phase как отдельный объект.

Исправление: определить matched environment, source, receiver и frequency grid; сравнивать complex pressure/transfer function после общей reference-phase convention. Метрику, phase unwrap, amplitude floor и допустимые исключения заморозить до пилота.

### P0.11 Fractional-delay synthesis не совместим с IPD gate

При `48 kHz` один sample равен `20.833 μs`. Nearest-sample placement arrival даёт до `10.417 μs` ошибки на канал и до `20.833 μs` differential error, тогда как protocol требует эквивалентную ошибку `<3 μs` (`:402-415,1093-1144`). Метод субсэмплового синтеза arrivals не зафиксирован; типовой IR helper с округлением delay до sample этот gate пройти физически не может.

Исправление: требовать phase-domain или проверенный fractional-delay synthesis, а затем end-to-end тестировать восстановление известного differential delay через весь путь `arrivals → waveform → features → IPD recovery`.

## Последняя проверка SNR/noise/interference contract

Перенос обычного шума в постобработку — правильное направление (`bellhop_mvp_protocol.md:436-462,756-823,1108-1116`), но текущий контракт ещё не обеспечивает точное воспроизведение и корректный статистический вывод.

| Блокер | Статус на C2 | Что требуется до запуска |
|---|---|---|
| SNR scaling, time support и filter | **Открыт** | Задать одну формулу масштабирования, reference sensor/array-wide scalar, участок времени и band/filter, где измеряются мощности; отдельно сохранять target и achieved SNR |
| Identity derived example | **Открыт** | `(channel_config_id, snr_level, noise_seed)` недостаточно: нужны source waveform/clean-scene id, noise asset/class, segment/offset, RNG algorithm/version, overlay version и scaling metadata |
| Dynamic RNG mapping | **Открыт** | Зафиксировать отображение namespace `(split, epoch, clean_scene_id, overlay_index)` в seed; validation/test mapping должен быть неизменяемым, training replay — детерминированным |
| Nested overlay hierarchy | **Открыт** | Noise realizations являются вложенными overlays одной clean scene/channel config и не увеличивают число независимых environments; bootstrap/power должны сохранять эту иерархию |
| SIR и coherent-interferer provenance | **Открыт** | Отделить `interference_class × sir_db` от `noise_class × snr_db`; для coherent source хранить собственные source/channel ids, solver provenance и array-wide scaling |
| Coherent-interferer budget | **Открыт** | Отдельно посчитать дополнительные propagation configs/runs; не скрывать их в обычном post-hoc noise budget |
| Noise-factor taxonomy | **Открыт** | Развести sensor/self noise, incoherent synthetic/recorded noise, tonal interference и propagated coherent interferer; запрещено смешивать их одной меткой `SNR/SIR` |
| Full-band reporting | **Открыт** | Наряду с target/achieved in-band SNR/SIR публиковать achieved full-band значения и отклонения; не выдавать заданный target за измеренный achieved level |

До закрытия этих пунктов fixed validation/sealed overlays нельзя считать replayable evidence, dynamic training augmentation нельзя считать воспроизводимой, а число overlay-реализаций нельзя использовать как независимую статистическую мощность. Фактический replay и achieved-level checks остаются **not yet evaluated**.

## Текущие P1 и документарные дефекты

- L-5 coordinates образуют симметричный cross/plus, а не L (`bellhop_mvp_protocol.md:72-89`). Название должно соответствовать topology.
- Frame counts неверны: для `(2.0 s, 256/64 ms)` получается `28`, не `24`; для `64/16 ms` — `122`, не `~124` (`:262-280`).
- Constant phase rotation не “subsumes” synchronization error: clock delay создаёт линейную зависимость `Δφ(f)=-2πfτ`, а не frequency-independent offset (`:170-183`).
- LHS одновременно включает source range/depths в environment parameters и снова варьирует их на channel level (`:354-368,658-720`). Environment design и nested source/receiver design надо разделить.
- CRLB задан формулой ULA, но требуется per geometry для L-5/Square-4/Rect-5 (`evaluation.md:39-67`; MVP `:976-988,1249-1250`). Нужен geometry-specific steering-vector Fisher information.
- Broadband MUSIC/MVDR/GCC aggregation и tuning policy всё ещё только “must be frozen”, а не frozen (`:962-974`).
- Требование одновременно получить paired-difference CI, исключающий ноль, и неперекрывающиеся marginal CI (`:1067-1075`) избыточно и статистически неэквивалентно paired test; авторитетным должен быть environment-level paired contrast.
- Framework требует strong SOTA-adjacent neural comparator, но MVP neural set его не включает (`evaluation.md:109-136`; MVP `:990-999`).
- `architecture.md:763-809` по-прежнему ошибочно запрещает attached coordinate embeddings как нарушающие equivariance, хотя MVP их требует; joint permutation token+coordinate сохраняет equivariance.
- `architecture.md:596` по-прежнему неверно связывает arXiv `2310.10922` с mHuBERT-147; корректная ссылка требует повторной библиографической проверки.
- Root `README.md` всё ещё содержит parameter ladder, отличную от canonical `architecture.md:602-628`.
- Перенос индекса в `docs/README.md` и входящая ссылка из root README исправлены в C1; старый путь `docs/research_framework.md` больше не является live navigation target.
- Игнорируемый Git и неотслеживаемый `.omo/visuals/bellhop_mvp_implementation_plan.html` содержит старые ULA-6/Rect-6/TDOA assumptions и может ввести будущую реализацию в заблуждение.

## Повторная рекомендация

**NO-GO для full dataset generation и confirmatory claims.** Разрешён только маленький diagnostic pilot после закрытия открытых частей P0.1, P0.3–P0.6 и P0.9–P0.11; P0.2 уже исправлен в документации, но не является эмпирическим PASS. До пилота нужно согласовать allocation arithmetic и SNR/replay contract, а по его результатам численно заморозить solver, broadband reconstruction, sealed environment count и matched controls.

Порядок исправления:

1. Устранить оставшиеся sealed contradictions: environment count и one-access policy; уже исправленную утечку Rect-5 не возвращать.
2. Выбрать один BELLHOP execution path, корректный broadband reconstruction method, fractional-delay synthesis и сопоставимую cross-solver величину.
3. Заморозить causal geometry controls и supervised Tier-0 scope.
4. Исправить allocation/frame/runtime arithmetic и signal-duration/crop rules.
5. Выполнить direct-path + multipath pilot; по его variance/delay-spread/runtime определить grid, environment count и channel bank.
6. Только после прохождения pilot gates открывать full generation; SSL, adapters и real-data validation остаются отдельными стадиями.

---

## Архив первичного аудита 2026-07-16 — superseded

Разделы ниже сохранены как историческая база и включают пользовательские дополнения о dataset coverage. Их оценки, line anchors и формулировки относятся к предыдущей версии протокола и **не должны использоваться как текущий GO/NO-GO verdict**. Актуален только повторный аудит выше.

### Итоговый вердикт первичной версии

| Критерий | Оценка | Вердикт |
|---|---:|---|
| Научная перспективность | **7/10** | Сильная постановка для отрицательного или положительного методологического результата; практическая ценность зависит от реальных данных |
| Реализуемость текущего MVP | **4/10** | Условно реализуем после исправления блокирующих противоречий; как написано сейчас — нет |
| Полнота описания | **7/10** концептуально; **4/10** исполнимо | Документация необычно подробна, но несколько ключевых контрактов физически или статистически не определены |
| Компонентная новизна | **2/10** | Большинство компонентов уже опубликовано |
| Комбинационная новизна | **5/10, unresolved** | Возможна узкая новизна интеграции, но firstness не доказана и без абляций не является научным вкладом |
| Готовность к реальному применению | **2/10** | TRL примерно 2→3; Novik Bay и sim-to-real не подтверждены |

Шкала едина для всех оценок: `0–2` — не подтверждено/не готово; `3–4` — серьёзные блокеры; `5–6` — условно, требуется существенная проверка; `7–8` — сильное и в основном реализуемое; `9–10` — доказано результатами и независимо воспроизводимо. Баллы получены консервативным минимумом по полноте спецификации, физической корректности, причинной идентифицируемости, статистической валидности и наличию внешнего подтверждения; это экспертная rubric, а не измеренный экспериментальный показатель.

Рекомендация: **условный GO только для сокращённого, заранее зарегистрированного simulator-methodology MVP**. Нельзя начинать полный многостадийный world-model roadmap до устранения P0-блокеров и прохождения дешёвого пилота.

## Что в плане действительно хорошо

1. План честно ограничивает первые выводы BELLHOP-симуляцией и прямо запрещает выдавать их за real-world performance (`overview.md:114-123`; `bellhop_mvp_protocol.md:695-706`).
2. Хорошо проработаны leakage-правила: среды, waveform/noise seeds и связанные augmented views разделяются по split; нормализация только по train (`bellhop_mvp_protocol.md:294-323`).
3. Есть сильные классические сравнения, отдельный privileged oracle MFP и запрет спасать провал масштабированием архитектуры (`bellhop_mvp_protocol.md:532-555,660-672`).
4. Есть kill/pivot логика, артефактный контракт и требование показывать провалы, а не только средние значения (`bellhop_mvp_protocol.md:660-719`).
5. Сам документ уже замечает важнейшую проблему: в BELLHOP-only режиме labels бесплатны, поэтому SSL нельзя оправдывать дефицитом разметки без реального unlabeled корпуса (`overview.md:226-239`).

## P0: блокеры до генерации данных

### 1. Геометрический эффект причинно не идентифицируем

Обучение использует только одну ULA-5 с `y=0`, а square/rectangular arrays полностью held out (`bellhop_mvp_protocol.md:53-108`). Параметры, связывающие вторую координату с attention, не получают обучающего сигнала; сама геометрия внутри train почти константна. Кроме того, proposed pairwise Transformer сравнивается с compact TCN/CRNN без геометрии (`:436-442,477-487`): одновременно меняются координаты, архитектура, pairwise processing и ёмкость.

Исправление: обучать минимум на двух неколлинеарных геометриях (либо множестве повёрнутых ULA), третью оставить held out; сравнить один и тот же backbone в режимах no-coordinate / coordinates-only / pairwise-only / full / shuffled-coordinates.

### 2. BELLHOP-контракт для broadband и азимута не определён

Диапазон 500–3000 Гц не имеет center-frequency, sub-band grid и правила recombination (`bellhop_mvp_protocol.md:124-138,255-265`). Руководство BELLHOP требует sub-banding для достаточно широкополосных источников из-за частотно-зависимого затухания ([BELLHOP manual](https://oalib-acoustics.org/website_resources/AcousticsToolbox/Bellhop-2010-1.pdf)). Обычный BELLHOP — range-depth модель; план не определяет, как planar coordinates и signed bearing превращаются в 2-D/Nx2D/3-D receiver geometry.

Исправление: заморозить source coordinates, array heading, bearing convention, solver mode, receiver layout, sub-band synthesis и проверить совместный против независимого расчёта hydrophones.

### 3. Допуск TDOA недостаточен для заявленного углового разрешения

Допуск TDOA `0.25 ms` (`bellhop_mvp_protocol.md:271-275,653`) для шага 2.5° у ULA-5 около broadside составляет примерно семь угловых bins. Это нарушает собственное требование `evaluation.md:901-909`, что TDOA tolerance должна быть существенно меньше downstream angular resolution. Отдельный phase-increment probe `<0.2 rad` (`evaluation.md:909-919`) измеряет другой estimand и не является прямым противоречием TDOA gate.

Исправление: частотно-масштабируемый допуск, около 10 μs на верхней частоте, и paired validation комплексной фазы.

### 4. Calibration gate физически требует преувеличенной реакции

План вводит coordinate noise σ=5 mm (clip 15 mm) и sync error ±10 μs (`:110-120`), но требует median latent TDOA change ≥50 μs (`:656`). Даже максимальная односенсорная прямая поправка около 20.3 μs. Физически верный encoder может провалиться, а гиперчувствительный — пройти.

Исправление: сравнивать знак и величину latent-derived delta с аналитической injected pairwise delta, а не с произвольным минимумом.

### 5. Статистический unit of inference отсутствует

48 000 test examples вложены всего в 12 environments и 5–10 тыс. reused channel configs (`bellhop_mvp_protocol.md:204-211,310-349`). Они не являются независимыми репликами. Не заданы hierarchical estimator, paired effect, resampling order и power. Это создаёт pseudoreplication ([Saravanan et al., 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7906290/)).

Исправление: environment — верхний sampling unit; paired hierarchical bootstrap; model seeds crossed with environments; pilot-based power для минимального значимого эффекта.

### 6. Test bank станет частью разработки

Один test split используется для большого адаптивного множества архитектур, абляций и gates (`bellhop_mvp_protocol.md:457-555`). Нет sealed confirmation bank и журнала доступов. Это ведёт к selection overfitting ([Cawley & Talbot, 2010](https://www.jmlr.org/papers/v11/cawley10a.html); [Dwork et al., 2015](https://pubmed.ncbi.nlm.nih.gov/26250683/)).

Исправление: exploratory dev-test и независимо сгенерированный sealed confirmatory bank с одним доступом после freeze.

### 7. Датасет: размер, покрытие и статистическая достаточность не обоснованы

Протокол заявляет `~120 000 / ~24 000 / ~48 000` array examples, но не показывает, что это достаточно для обучения, валидации и тестирования, и не разбирает эффективное число независимых наблюдений. Это методологический риск, сравнимый по важности с P0-блокерами выше.

#### 7.1 Эффективное число независимых сцен

Протокол использует channel reuse `6–12` examples per channel config (`bellhop_mvp_protocol.md:477-483`). Если один channel config описывает одну физическую сцену (environment + geometry + range + depth + azimuth), то:

```text
Effective independent train scenes ≤ 120 000 / 12 ≈ 10 000
Effective independent train scenes ≥ 120 000 / 6  ≈ 20 000
```

Эти 10–20 тысяч сцен распределены по:
- `32` BELLHOP environments;
- `2` train geometries (ULA-5-H, L-5);
- `37` train azimuths;
- `5` source families;
- множеству SNR/SIR/шумовых условий;
- диапазону source range и source/receiver depth.

Даже при верхней оценке `20 000` сцен на `32` environment даёт ~625 сцен на среду. После разбиения по геометрии, азимуту и семейству многие ячейки покрытия окажутся пустыми или содержать единичные примеры. Для сравнения: `32` среды — это не 32 независимых реплики генеральной совокупности Novik Bay, а 32 deterministic draw из 9-мерного параметрического пространства.

#### 7.2 Покрытие параметрического пространства сред

Случайные параметры среды (`bellhop_mvp_protocol.md:307-327`):

| Параметр | Диапазон | Тип |
|---|---|---|
| Water depth | 15–60 m | continuous |
| Source depth | 3–20 m (≥3 m от дна) | continuous |
| Receiver depth | 3–20 m (≥3 m от дна) | continuous |
| Source range | 50–1000 m (test: 1200 m) | continuous |
| Surface sound speed | 1460–1530 m/s | continuous |
| SSP gradient | [-0.05, +0.05] (m/s)/m | continuous |
| Bottom compressional speed | 1450–1800 m/s | continuous |
| Bottom density | 1.3–2.0 g/cm³ | continuous |
| Bottom attenuation | 0.1–1.0 dB/λ | continuous |

Это 9 continuous факторов. `32` train environments не могут покрыть комбинаторику. Нужно:
- либо Latin Hypercube Sampling (LHS) с явным stratification;
- либо минимальное число сред, обоснованное power analysis;
- либо признание, что generalization claims ограничены convex hull этих 32 точек.

Протокол не указывает sampling strategy для environments. Равномерный случайный draw из 9-мерного box даёт неравномерное покрытие (clustering по углам и пустоты в центре).

#### 7.3 Покрытие сигнального пространства

Source families и их параметры (`bellhop_mvp_protocol.md:259-290`):

| Family | Weight | Ключевые параметры |
|---|---|---|
| CW | 1.0 | carrier 500–3000 Hz, 2.0 s |
| LFM chirp | 1.0 | bandwidth 500–2000 Hz, duration 0.5–2.0 s |
| NLFM chirp | 1.0 | polynomial order 2/3 |
| Broadband pulse | 1.0 | center 1000–2500 Hz, bandwidth 500–1500 Hz, 50–250 ms |
| Impulsive transient | 0.5 | 10–80 ms |
| Band-limited noise burst | 1.0 | band 500–3000 Hz, 0.25–2.0 s |

Проблемы:

- **CW доминирует по энергии и простоте.** Для classical baselines CW — почти optimal case. Если 1/5.5 ≈ 18% данных — CW, модель может переобучиться на CW-like patterns.
- **Импульсные transient (weight 0.5)** имеют малую энергию и короткую длительность; их может быть недостаточно для обучения robust DOA head.
- **Нет явного контроля за spectral overlap** между семействами. Например, LFM chirp с bandwidth 500–2000 Hz и broadband pulse с bandwidth 500–1500 Hz сильно перекрываются.
- **20% OOD holdout per family** уменьшает train coverage ещё сильнее.

#### 7.4 SNR/SIR regimes

Протокол (`bellhop_mvp_protocol.md:395-405`):

| Condition | Values | Split policy |
|---|---|---|
| Clean | no noise | all splits |
| White noise | 20, 10, 0, -5 dB | all splits |
| Colored noise | 1/f, 1/f²; 20, 10, 0 dB | all splits |
| Narrowband interference | SIR 20, 10, 0 dB | disjoint freq bins |
| Acoustic interferer | SIR 20, 10, 0 dB | diagnostic only |

Проблемы:

- **-5 dB white noise:** на короткобазной решётке с 6 сенсорами DOA может быть практически случайным. Если `~25%` white-noise примеров приходится на 0/-5 dB, это большая часть датасета с низким информационным содержанием.
- **Colored noise 1/f²:** доминирует низкочастотная энергия; может искажать оценку SNR в useful band 500–3000 Hz.
- **Нет явного SNR-dependent sampling budget.** Рекомендуется фиксировать минимальное число примеров на SNR/семейство/среду.

#### 7.5 Длительность chunk и стационарность источника

Протокол: chunk `2.0 s`, hop `1.0 s`, источник статичен в пределах одного примера.

- Для `f = 500 Гц` в 2.0 s укладывается `1000` циклов — достаточно для narrowband DOA.
- Для `f = 3000 Гц` — `6000` циклов — избыточно, но не вредит.
- **Проблема:** real-world источники движутся. MVP статичен по определению, и это должно быть явно заявлено как ограничение generalizability.
- **Hop 1.0 s** создаёт overlap 50% между соседними chunks, увеличивая число examples без увеличения независимой информации.

#### 7.6 Azimuth grid и интерполяция

- Train: `5°` spacing, 37 значений.
- Test: `2.5°` spacing, 73 значения.

Test angles лежат ровно между train angles. Это deliberate interpolation test, но:
- если модель запомнит train angles, interpolation error может быть занижен;
- нужен дополнительный OOD test с углами, не кратными `2.5°` (например, случайные).

#### 7.7 Channel bank vs example count

Протокол заявляет `10 000–20 000` unique channel configs для train. С учётом:
- `32` environments,
- `2` train geometries,
- `37` train azimuths,
- range bins,
- depth bins,

получаем потенциальные миллионы комбинаций. `10 000–20 000` configs покрывают лишь малую часть. Нужно явное stratified subsampling с контролем покрытия.

#### 7.8 Рекомендуемые минимальные dataset-quality gates

До начала обучения должны быть выполнены:

1. **Coverage matrix:** таблица `environment × geometry × azimuth-sector × source-family × SNR` с числом examples в каждой ячейке; минимум `N_min` examples per cell (например, `N_min = 10`).
2. **Effective independence report:** число уникальных channel configs, сред на split, и effective examples после учёта reuse.
3. **SNR-conditioned stratification:** train/val/test должны содержать одинаковые пропорции SNR/SIR/семейств.
4. **Environment sampling audit:** показать scatter plot или LHS design для 32 train / 8 val / 12 dev-test / 4 sealed environments.
5. **Pilot dataset minimum:** перед генерацией 120k примеров обучить Tiny модель на пилоте `≥ 2000` независимых scenes и проверить, что geometry effect наблюдается.

#### Исправление

- Добавить в протокол явный раздел **Dataset Design and Coverage** с sampling strategy, coverage audit, minimum examples per cell, и effective-independence accounting. **(Частично сделано: Section 8.2 протокола определяет environment allocation, signal parameters, source-array geometry, SNR regimes, stratification, и OOD panels.)**
- Провести пилот на `~20 000` train examples (`~10 000` per geometry) до массовой генерации.
- Обосновать 120k/24k/48k через power analysis и coverage requirements, а не через convenience. **(Требуется numeric power analysis в будущем.)**

---

## P1: серьёзные противоречия документа

- CW длится 2.0 s, но общий контракт требует onset 0.10–0.30 s и trailing context ≥0.10 s внутри 2.0 s chunk (`bellhop_mvp_protocol.md:176-193`). Нужен exception или shorter CW.
- ULA spacing 0.25 m объявлен λ/2 при 3 кГц и 1500 m/s, но randomized c снижается до 1460 m/s (`:64-71,221-222`), поэтому верхняя часть band spatially aliased. Ограничить `f_max≈2.92 kHz` либо сделать aliasing явным stress regime.
- Early-pooling gate логически инвертирован: ухудшение должно отвергать pooling, но все gates обязаны pass до отчётности (`evaluation.md:961-984`; MVP `:658`). Это interface-selection ablation, не validity gate основного пути.
- Основной Stage-1 masked objective остаётся label-free, но **опциональный** contrastive variant разрешает negative pairs по DOA (`training_strategy.md:97-123`). Именно этот вариант является weak supervision и должен маркироваться отдельно; вывод не относится ко всему Stage 1 (`bellhop_mvp_protocol.md:500-518`).
- `architecture.md:769-801` одновременно требует coordinate embeddings и запрещает их как permutation-breaking. При совместной перестановке signal+coordinate tokens координаты не нарушают set equivariance.
- README содержит устаревшую parameter ladder относительно `architecture.md:608-628` и MVP.
- MVP claim не включает SSL, но kill criterion требует остановки при провале optional SSL (`bellhop_mvp_protocol.md:19-31,450-455,660-672`). Kill criteria надо разделить по claims.
- Independent per-hydrophone BELLHOP runs не согласованы с run budget и могут ухудшить межсенсорную когерентность; предпочтителен joint receiver array.
- Baseline MUSIC/MVDR для broadband не имеет frozen frequency aggregation/tuning policy.
- Минимальный MVP не гарантирует сильный neural comparator: framework требует SOTA-adjacent models (`evaluation.md:65-125,290-299`), но executable MVP допускает только компактные CRNN/TCN и оставляет stronger comparator условным (`bellhop_mvp_protocol.md:546-553`). Без него нельзя заявлять neural superiority.
- Transfer mode не заморожен: frozen backbone, adapters, partial и full fine-tuning перечислены как варианты (`bellhop_mvp_protocol.md:577-582`; `training_strategy.md:782-819`), поэтому «lightweight adaptation» пока не является воспроизводимым claim. Нужен один primary режим и matched cost/accuracy comparison.
- SSL и VAE помечены optional, однако присутствуют в mandatory-looking ablation grid (`bellhop_mvp_protocol.md:444-471`). Следует разделить обязательную Tier-0 матрицу и exploratory branches, иначе объём/kill logic неоднозначны.
- Joint test одновременно меняет environment, geometry, angle grid, source parameters и range; нужен factorial OOD decomposition.

## Новизна: строгая проверка prior art

Компонентная новизна не подтверждается:

| Заявленная идея | Ближайшие работы | Вывод |
|---|---|---|
| Underwater neural DOA + BELLHOP | [Li et al., 2022](https://doi.org/10.3389/fmars.2022.1027830) | Не ново |
| Arbitrary hydrophone geometry / wideband | [Dubrovinskaya et al., 2020](https://doi.org/10.3390/s20143862) | Не ново как задача |
| Geometry-conditioned variable-array neural DOA | [Kowalk et al., ICASSP 2023](https://doi.org/10.1109/ICASSP49357.2023.10096047), [Neural-SRP](https://arxiv.org/abs/2403.09455), GI-DOAEnet DOI `10.1109/TASLPRO.2025.3577336` | Core claim не нов |
| Hydroacoustic SSL / predictive latent learning | DOI `10.1109/SENSORS47087.2021.9639566`, DOI `10.1109/JSEN.2022.3179405` | Не ново |
| Self-supervised acoustic maps for DOA and array adaptation | [Latent Acoustic Mapping, 2025](https://doi.org/10.1109/WASPAA66052.2025.11231008) | Прямое сильное пересечение |
| Audio + geometry/grid localization | [AGG-RL, ICLR 2026](https://openreview.net/pdf?id=bWXpJFesLS), [PhaseCoder](https://arxiv.org/abs/2601.21124) | Сильно сужает geometry/frequency novelty; в AGG-RL `SSL` означает sound source localization, не self-supervised learning |
| Synthetic-to-real adaptation underwater | [Cao et al., 2021](https://doi.org/10.1121/10.0003645), [Kari & Singer, 2025](https://arxiv.org/abs/2503.23262) | Не ново |

Не найден точный предшественник всей комбинации: phase-preserving hydroacoustic backbone + domain-randomized BELLHOP + geometry-conditioned SSL + held-out topology transfer + optional between-window latent state + multiple heads. Это **не доказывает firstness**. Корректная формулировка: «мы проверяем, даёт ли такая интеграция измеримый выигрыш». Термин “world model” лучше не использовать: план сам признаёт, что это не полная модель среды (`overview.md:273-282`).

Дополнительная проверка существенно сузила новизну Stage-2 objective family: [Guided-MELD](https://arxiv.org/abs/2404.08264) использует masked-sensor EMA self-distillation, но с supervised event labels; [CCSR](https://arxiv.org/abs/2312.00476) — label-free cross-channel masked reconstruction без explicit variable-array geometry conditioning; [wav2pos](https://arxiv.org/abs/2408.15771) — masking, microphone coordinates и variable/missing arrays, но supervised localization. Эти работы закрывают соседние компоненты, а точная комбинация label-free masked-sensor prediction, explicit arbitrary geometry и hydroacoustic transfer остаётся **unresolved**.

## Значимость и реальные примеры

Практическая потребность реальна: passive acoustic monitoring используется для локализации морских млекопитающих и наблюдения, а массивы применяются для surveillance. Для внешней проверки доступен [SWellEx-96](https://swellex96.ucsd.edu/) с array geometry, GPS tracks и CTD; однако его 50–400 Гц не пересекаются с MVP 500–3000 Гц, поэтому нужен отдельный frozen low-frequency branch. [OOI broadband hydrophones](https://oceanobservatories.org/instrument-class/hydbb/) полезны для unlabeled pretraining/noise adaptation, но обычно не дают синхронной DOA ground truth.

Следовательно, значимость области высокая, но значимость именно предложенного метода пока гипотетическая. BELLHOP domain randomization снижает риск, но не является доказательством sim-to-real. BellhopCUDA сам документирует ограничения точности и 3-D receiver issues ([README](https://github.com/A-New-BellHope/bellhopcuda)).

Ресурсная реализуемость также условна. 196 тыс. шестиканальных 2-секундных примеров дают нижнюю оценку порядка 210 GiB для 12 kHz complex64 IQ или 421 GiB для 48 kHz float32 waveforms; raw+IQ+STFT+arrivals+caches могут превысить 1 TB. Наивный полный cross-product `5 seeds × 7 matrix rows × 3 label budgets` дал бы 105 запусков, но это не минимум: одна строка classical, часть branches optional, и не все строки обязаны запускаться при каждом label budget. Реальный run budget должен быть выписан явно. Планирование BellhopCUDA по 0.2/1/5 s — арифметические сценарии, не benchmark; arrivals workload, I/O и возможный per-hydrophone multiplier требуют локального пилота (`bellhop_mvp_protocol.md:325-405`).

## Предложение по учёту SNR

Моделирование распространения сигнала следует отделить от генерации шума. BELLHOP должен использоваться для создания банка чистых многоканальных откликов, а шум заданного типа и SNR — накладываться позднее, в том числе динамически во время обучения. Поэтому SNR не следует использовать как множитель при расчёте числа BELLHOP-конфигураций и размера банка каналов. При этом SNR необходимо сохранить как вложенный экспериментальный фактор при оценке качества и дисперсии: для validation и test должны применяться фиксированные уровни SNR и замороженные noise seeds, а статистические выводы и power analysis должны выполняться на уровне независимых сред с усреднением по шумовым реализациям. Простое постналожение допустимо для сенсорного и некогерентного шума; пространственно-когерентные помехи следует моделировать отдельным каналом распространения или многоканальными записями.

Это предложение внесено в `docs/experiments/bellhop_mvp_protocol.md` Section 7 и Section 8.2.4.

## Минимальный научно защитимый план

1. Исправить P0 physics/spec contradictions и выполнить 100-case solver pilot.
2. Сократить MVP до одного matched backbone, geometry/no-geometry causal ablation и сильных classical baselines.
3. Обучать на ≥2 неколлинеарных geometries; третью держать sealed.
4. Выбрать один primary endpoint и paired hierarchical estimator; мощность определить по пилоту.
5. Разделить environment-only, geometry-only, source-only, range-only и joint-stress panels.
6. Создать sealed final environments; все архитектурные решения принять до единственного доступа.
7. Проверить BELLHOP против KRAKEN/SCOOTER на low-frequency shallow-water corner.
8. Только после положительного Tier-0 результата добавлять Stage 3, DINO/JEPA, Mamba, большие модели и multi-head extensions.
9. Провести отдельную реальную validation branch с surveyed array, shared clock, CTD/SSP, source GPS/emission timing и calibrated complex sensor response.

## Критерии GO / NO-GO

GO после: executable broadband/azimuth contract; matched ablations; physically consistent gates; pilot runtime/storage; hierarchical power; sealed test policy; минимум две обучающие geometry families.

NO-GO/публиковать отрицательный результат, если: geometry gain исчезает в matched ablation; baseline competitiveness не достигается с paired CI; solver/phase gates не сходятся; learned geometry не переносится за пределы training topology; real/cross-solver challenge выявляет simulator shortcut.

## Заключение

План необычно зрелый как каталог рисков, но переоценивает готовность исполнимого протокола. Его сильнейший научный вклад сейчас — не “новая world model”, а строгая проверка того, приносит ли geometry-conditioned SSL дополнительную ценность сверх matched supervised и classical baselines в физически контролируемой hydroacoustic simulation. После исправления P0-блокеров это перспективная работа с высокой вероятностью полезного результата даже при отрицательном исходе. Без этих исправлений положительный результат будет причинно неоднозначным, статистически переуверенным и слишком слабым для заявлений о переносимости или реальном применении.

## Методика аудита

Первичный аудит использовал семь параллельных направлений; его временные team artifacts больше не присутствуют в репозитории, поэтому этот исторический раздел не является самостоятельно воспроизводимым evidence package. Повторный аудит 2026-07-17 выполнен пятью специализированными subagent review-lanes по текущему незакоммиченному рабочему дереву. Их ответы остались сессионными и также не являются сохранённым evidence package; воспроизводимыми основаниями отчёта служат приведённые line anchors, расчёты и внешние ссылки. Использовались проверки полного корпуса, git/history, Markdown rendering, арифметические проверки, официальная документация BELLHOP/BellhopCUDA и counter-review физических/статистических утверждений.
