# Строгий аудит плана исследования Hydro-DOA World Model

Дата актуализации: **2026-08-12**. Точный аудируемый product corpus зафиксирован через `e200bcc1638687f081b2833ab06ab98d1c7cd5c3`: диапазон `5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3` содержит **16 product commits** и **11 изменённых путей**, а опубликованный corpus — **6091 строки**. За ним следует этот audit-only provenance commit как handoff wrapper: его parent — `e200bcc1638687f081b2833ab06ab98d1c7cd5c3`, а собственный SHA — enclosing Git object, разрешаемый `git rev-parse HEAD`. Воспроизведение product counts: `git rev-list --count 5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3`, `git diff --name-only 5b61fc25812deac44ea9951a58f4621be487f195..e200bcc1638687f081b2833ab06ab98d1c7cd5c3 | sort`, и `wc -l README.md docs/README.md docs/research/framework/*.md docs/experiments/bellhop_mvp_protocol.md | tail -1` на immutable `e200bcc` objects.

Проверяемый опубликованный корпус — `README.md`, `docs/README.md`, все `docs/research/framework/*.md` и `docs/experiments/bellhop_mvp_protocol.md`: **6091 строки** по `wc -l README.md docs/README.md docs/research/framework/*.md docs/experiments/bellhop_mvp_protocol.md | tail -1`. Сам аудит и handoff wrapper в этот счёт не входят. Код, данные, solver/model runs, power analysis, checkpoints и экспериментальные результаты отсутствуют.

## Проверенная история remediation

| ID | Полный SHA | Коммит |
|---|---|---|
| C1 | `89ce838e9a38621a33a0a1b6b2cd10dfbc1913ba` | `docs(index): move framework index under docs` |
| C2 | `09d16fa8769dde7da73a0bdc06abc67a6df0ea85` | `docs(protocol): checkpoint BELLHOP MVP methodology draft` |
| C3 | `a06e4a6caf109688c2f2d9ca40cf6211271bb049` | `docs(audit): record 2026-07-17 methodology no-go review` |
| C4 | `44343b611d0eda0531b4e2913d9ca6dcfbab67fb` | `docs(protocol): freeze Tier-0 and sealed evaluation contract` |
| C5 | `d0d853e9a8703ba2f319d64b5b569a42143f3d79` | `docs(protocol): close propagation and signal synthesis contracts` |
| C6 | `033c3a4b341a98fe759d35e258e55618da16f1e2` | `docs(protocol): specify reproducible post-hoc noise generation` |
| C7 | `bb7084212f2bfc4cb4f9a85871939a33246bee7d` | `docs(protocol): derive allocation and power contracts` |
| C8 | `e66623953f7491382787f8e2f46713222749c074` | `docs(protocol): freeze causal controls and evaluation baselines` |
| C9 | `9a0507a9a2fabc34ff3e52edbe7cf50f1a96258a` | `docs(architecture): align geometry and stage contracts` |
| C10 | `ef1e7339faa73a470a407648586afbe18612156a` | `docs(evaluation): align inference and physical bounds` |
| C11 | `2c4bd616d1835d3d43ed9f8403f929dc04908560` | `docs(framework): align data and execution constraints` |
| C12 | `b3d6b6f4e29b68f499db24179e57aabe6ec6e6e4` | `docs(readme): align research documentation navigation` |
| C9a | `86d037893e3b7b5584d964f6efb386033843986c` | focused architecture fix: `docs(architecture): correct Tier-1 SSL scope` |
| C13 | `c1c07e90dc045b01b9c8a344fb4c6bda6e8454c3` | `docs(audit): refresh remediation status` |
| C14 | `e1fe8c27a3688a15b75317cec18a0d9e1b26e06b` | `docs(protocol): isolate alias-safe primary inference` |
| C15 | `e200bcc1638687f081b2833ab06ab98d1c7cd5c3` | `docs(protocol): require primary-band source eligibility` |

Все ссылки ниже — текущие line anchors на этом состоянии. Используются только три статуса: `documentation-resolved` означает закрытый статический контракт; `pilot-dependent/not-yet-evaluated` означает специфицированный, но ещё не выполненный эмпирический gate; `still-open` означает незакрытый статический дефект.

## P0.1–P0.11

| ID | Статус | Текущее основание |
|---|---|---|
| P0.1 | **documentation-resolved; F2-2 repair** | `N_power`, `N_sealed=max(10,N_power)`, `N_sealed_examples` и effective `N` выводятся только из полных primary-eligible environments; overlays/views не создают units (`docs/experiments/bellhop_mvp_protocol.md:570-610`). Единственный global preregistered sealed batch и zero-shot policy сохранены (`:637-667`). Сам `N_power` остаётся будущим измерением. |
| P0.2 | **documentation-resolved** | Rect-5 закреплён только за sealed topology и исключён из development/adaptation (`bellhop_mvp_protocol.md:128-156,637-648`). |
| P0.3 | **pilot-dependent/not-yet-evaluated** | Raw sparse-complex interpolation запрещена; заданы path matching, residual-delay interpolation и full-multipath phase-domain synthesis (`bellhop_mvp_protocol.md:422-425`). Частотный grid выбирается только будущим convergence pilot (`:694-704`). |
| P0.4 | **pilot-dependent/not-yet-evaluated** | Единственный executable route — 2-D BELLHOP arrivals type `A` с per-sensor range/depth mapping (`bellhop_mvp_protocol.md:403-411`); build/ray convergence ещё не проверены (`:437-446`). |
| P0.5 | **documentation-resolved** | Matched modes и отдельные mismatched-coordinate/joint-permutation controls различены (`bellhop_mvp_protocol.md:156-169`); frozen Small backbone и неизменяемые training fields заданы в `:965-982`. |
| P0.6 | **pilot-dependent/not-yet-evaluated; F2-2 repair** | Одна allocation table задаёт primary-eligible quotas и выводит totals, reuse, runs, storage и runtime; attempt/stress/source-absent rows вынесены из `E` (`bellhop_mvp_protocol.md:570-610,672-736`). Sealed size, eligible-scene quota, frequency count и measured runtime остаются pilot-derived. |
| P0.7 | **documentation-resolved; F2-2 repair** | Для всех source families задан generator-level primary-support profile; после propagation действует exact finite positive per-sensor projected-power check без произвольного magnitude threshold (`bellhop_mvp_protocol.md:323-344,491-517,765-789`). Неeligible rows — только stress/source-presence; paired models/baselines получают один ordered eligibility manifest, а primary metrics/bootstrap/CI используют только полные eligible environments (`:1121-1136,1168-1176`). |
| P0.8 | **documentation-resolved** | Единственный claim — supervised-from-scratch Tier-0 matched pair (`bellhop_mvp_protocol.md:17-27,965-982`); sealed mode только zero-shot (`:637-648`), SSL — optional separately preregistered Tier-1 (`docs/research/framework/architecture.md:33-41`). |
| P0.9 | **documentation-resolved** | Conditional duration и CW exception закрывают невозможные draws (`bellhop_mvp_protocol.md:315-339`); continuous arrivals, full linear convolution, `[0,2.0 s)` emission-time crop, padding и label timestamp заданы в `:406-425`. |
| P0.10 | **pilot-dependent/not-yet-evaluated** | Cross-solver estimand теперь matched coherent complex pressure с общей phase convention, amplitude floor и frozen thresholds (`bellhop_mvp_protocol.md:432-437`); comparison solver/result ещё не выбраны и не вычислены. |
| P0.11 | **pilot-dependent/not-yet-evaluated** | Nearest-sample placement запрещён, synthesis сохраняет continuous fractional delay (`bellhop_mvp_protocol.md:406,422-424`); end-to-end PDOA/IPD gate остаётся будущим (`:437-446`). |

Итого: статически незакрытых P0 нет; `still-open` строк — **0**. Это разрешает только будущий diagnostic pilot. Пять pilot-dependent строк не являются свидетельством прохождения solver, broadband, runtime/power, cross-solver или fractional-delay gates.

## Последние SNR/noise/interference blockers

| Блокер | Статус | Текущее основание |
|---|---|---|
| SNR scaling, time support и filter | **documentation-resolved; F2-2 repair** | Исходный 2.0 s `500-3000 Hz` base-overlay Butterworth/scalar contract сохранён; exact primary eligibility проверяется до overlay scaling, а zero-primary power использует null-SNR/source-absent sentinel и не входит в DOA (`bellhop_mvp_protocol.md`, Sections 7.2-7.2a). |
| Identity derived example | **documentation-resolved; F2-2 repair** | Replay key включает source profile, per-sensor/array primary power, eligibility/reason/hash, parent/view/mask/component/scalar и achieved levels (`bellhop_mvp_protocol.md`, Sections 7.2a-7.3). |
| Dynamic RNG mapping | **documentation-resolved** | Canonical namespace, Philox algorithm, digest/counter mapping и immutable evaluation rows заданы в `bellhop_mvp_protocol.md:519-534`. |
| Nested overlay hierarchy | **documentation-resolved; F2-2 repair** | Eligibility принадлежит clean realization и наследуется overlays/views; ни те ни другие не создают power units или sealed accesses. До freeze допустима только metadata/power-driven replacement по fixed quota; после sealed output/label/result resampling запрещён (`bellhop_mvp_protocol.md`, Sections 7.2a, 7.4 и 8.1a). |
| SIR и coherent-interferer provenance | **documentation-resolved** | `noise_class × snr_db` отделён от `interference_class × sir_db`; coherent source имеет отдельный propagation/provenance path (`bellhop_mvp_protocol.md:478-489,547-559`). |
| Coherent-interferer budget | **documentation-resolved** | Дополнительный diagnostic bank и отдельная формула runs не входят в ordinary channel bank/power (`bellhop_mvp_protocol.md:547-559,608`). |
| Noise-factor taxonomy | **documentation-resolved** | Clean, ordinary sensor/recorded/synthetic noise, tonal и propagated coherent interference имеют отдельные классы и axes (`bellhop_mvp_protocol.md:450-462,478-489,818-830`). |
| Full-band reporting | **documentation-resolved; F2 repair** | Обязательны исходные base-overlay `500-3000 Hz`/full-band levels и отдельные primary/stress view ID, target, scalar и achieved levels per sensor/array mean (`bellhop_mvp_protocol.md`, Sections 7.2a и 16). |

Статические восемь blockers закрыты, но фактический deterministic replay, achieved-level tolerances и noise/interference outcomes имеют статус **pilot-dependent/not-yet-evaluated**. Overlay realizations остаются repeated measurements, не независимыми environments.

## P1 и синхронизация корпуса

| Пункт | Статус | Текущее основание |
|---|---|---|
| Cross-5 topology/channel count | **documentation-resolved** | Пять уникальных sensors и один общий center: `bellhop_mvp_protocol.md:74-88`; `docs/research/framework/architecture.md:759`. |
| Frame counts | **documentation-resolved** | Для трёх scales зафиксированы `12/28/122`: `bellhop_mvp_protocol.md:270-280`. |
| Clock delay против phase rotation | **documentation-resolved** | Frequency-independent phase error и `Δφ(f)=-2πfτ` разведены: `bellhop_mvp_protocol.md:185`. |
| Environment LHS separation | **documentation-resolved** | Шесть environment factors отделены от nested source/receiver/channel draws: `bellhop_mvp_protocol.md:352-356,738-747`; `docs/research/framework/data_and_simulation.md:106-111`. |
| General-array CRLB | **documentation-resolved** | Deterministic conditional model, nuisance-projected Fisher information и `MSE / CRLB` охватывают actual geometry: `docs/research/framework/evaluation.md:41-61,93`. |
| Baseline freeze и strong comparator | **documentation-resolved** | Numerical MVDR/MUSIC/GCC-PHAT/PDOA settings: `bellhop_mvp_protocol.md:1047-1058`; bounded CNN-Conformer: `:1091-1099`. Их результаты — **pilot-dependent/not-yet-evaluated**. |
| Coordinate equivariance | **documentation-resolved** | Attached coordinate-token association сохраняет joint permutation equivariance: `docs/research/framework/architecture.md:759-809,839`. |
| Bibliography | **documentation-resolved** | Spatial HuBERT `2310.10922` и mHuBERT-147 `2406.06371` разведены: `docs/research/framework/architecture.md:595-602`. |
| Model ladder и navigation | **documentation-resolved** | Canonical ladder `0.5-5M / 5-30M / 30-120M / 120-500M / 500M+`: `docs/research/framework/architecture.md:610-634`, синхронно `README.md:76-94`; dated audit и protocol связаны в `README.md:81-85`. |
| Paired CI decision rule | **documentation-resolved; F2-2 repair** | Авторитетен paired environment-level contrast только по одному frozen ordered eligibility manifest для `full`, `no-coordinate` и applicable baselines; ineligible/stress rows не входят в prediction/metric/bootstrap/CI/power (`docs/research/framework/evaluation.md:397-413`; `bellhop_mvp_protocol.md:513-517,1172-1176`). |
| Ignored visual exclusion | **documentation-resolved** | `.omo/` и generated/stale visuals явно non-authoritative: `README.md:113-115`; они не входят в опубликованный corpus и commit scope. |

## Итоговый вердикт и границы утверждений

**NO-GO для full dataset generation и confirmatory claims.** Документация пригодна только для будущего diagnostic pilot, поскольку все найденные статические prerequisites закрыты. Пилот должен измерить solver/build и ray convergence, full-multipath frequency-grid convergence, cross-solver agreement, fractional-delay recovery, runtime/storage, exact eligibility/overlay replay и achieved levels, eligible-environment ICC/paired-effect variance и `N_power`, а также baseline/model/CRLB/coherence gates. До появления предписанных артефактов каждый такой результат — `pilot-dependent/not-yet-evaluated`; документарное закрытие не является эмпирическим результатом.

Проверка выполнялась внутренними агентами по девяти adversarial classes: malformed input, prompt injection, cancel/resume, stale state, dirty worktree, hung/long commands, flaky tests, misleading success output и repeated interruptions. Это **internal subagent review**, не independent replication, не внешний peer review и не эмпирическая проверка научных claims.

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
