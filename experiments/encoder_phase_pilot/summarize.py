#!/usr/bin/env python3
"""Render numerical section of the one canonical report from saved results."""
import json
from pathlib import Path
import statistics as st

HERE=Path(__file__).resolve().parent
REPORT=HERE.parents[1]/'outputs/mono_phase_encoder_feasibility.md'
BEGIN='<!-- trained-encoder-pilot:start -->'
END='<!-- trained-encoder-pilot:end -->'
NAMES={'real_conv':'Re/Im Conv','complex_conv':'Комплексный Conv','hybrid_small':'Малый гибрид'}


def render():
    j=json.loads((HERE/'results.json').read_text());v=json.loads((HERE/'verification.json').read_text())
    assert j['status']=='COMPLETED' and v['status']=='PASS'
    rows={n:[r for r in j['runs'] if r['architecture']==n] for n in NAMES}
    def med(n,kind,snr,metric):return st.median(r['results'][kind][snr][metric] for r in rows[n])
    def pair(n,kind,snr):return f"{med(n,kind,snr,'median_tdoa_us'):.3f} / {med(n,kind,snr,'p95_tdoa_us'):.3f}"
    text='''## Выполненное сравнение обучаемых энкодеров (02.10.2026)

**Фактически выполнено:** девять запусков, три архитектуры × три парных seed. Это малые инженерные сети и обычное mono-предобучение реконструкцией чистой Re/Im STFT из зашумлённой: **не EMA/JEPA, не полный E-M и не канонический frozen-E gate**. Канонические `docs/` не менялись. Предварительный [план и бюджет](../experiments/encoder_phase_pilot/autoresearch.md), [код](../experiments/encoder_phase_pilot/benchmark.py), [команда запуска](../experiments/encoder_phase_pilot/autoresearch.sh), [первичные результаты](../experiments/encoder_phase_pilot/results.json), [stdout](../experiments/encoder_phase_pilot/benchmark.log), [реестр запусков/решений](../experiments/encoder_phase_pilot/autoresearch.jsonl) и [дополнительная проверка](../experiments/encoder_phase_pilot/verification.json) сохранены. Числа этого раздела автоматически вычислены `experiments/encoder_phase_pilot/summarize.py`; агрегаты — **медианы соответствующих seed-wise метрик**, не p95 объединённого набора и не независимые среды.

### Данные, обучение и считыватель

`fs=96000`, 2048 отсчёта; случайная стационарная сумма синусоид на FFT-бинах 11..53 (4125..19875 Гц). Дробная задержка задаётся аналитической фазой каждой синусоиды; не используется круговой сдвиг записи. Фазы и амплитуды источника случайны, исходная мощность чистой суммы фиксирована. Два синхронных наблюдения имеют один исходный источник, разные задержки и независимые шумы AWGN. Только предполагаемые d=.027 м, c=1500 м/с, `u∈[−.8,.8]`, соседняя пара. Знаковая TDOA `τ₀−τ₁=−d*u/c`; целевая относительная фаза — фактический clean-D взаимный угол STFT на 12 кГц, не ложное требование идеальной фазовой разности при спектральной Hann-утечке.

Случайные исходные источники: **2048 mono train / 256 development / 512 probe fit / 512 test**, четыре раздельных source seeds. Все test-SNR используют те же чистые источники, разные noise seeds; test — пилотный синтетический отчётный набор, не закрытый зимний final. Scale единственный общий положительный RMS из train Re/Im; encoder не видит координаты/u/второй датчик. Hann256/hop64/center=False, сохраняются 43 частоты. Все сети: одинаковый выход `[N_ch,16,43,15]`, временной stride2; decoder `Conv1x1 16→2` и bilinear interpolation к 29 исходным кадрам, без raw bypass. По **300 AdamW-шагов**, batch16, lr=.001, wd=.0001, seed101/202/303; одинаковые batch indices внутри seed. Последний checkpoint, без подбора по test/early stopping; float32, без AMP/compile/TF32.

Real Conv — три вещественные 3×3 свёртки с GELU. Complex Conv — три комплексные свёртки, общие вещественная/мнимая матрицы весов, радиальный gain без фазового сдвига; выход — lossless Re/Im. Гибрид — комплексный stem, один малый FFN/темпоральное внимание/временная depthwise Conv/FFN блок, затем локальный frequency Conv; это **не полная выбранная E-M/Conformer реализация**, размер выбран только для отдельного пилота. Различаются параметры/операции/ёмкость, потому выводы не означают преимущество при равной стоимости.

После обучения E полностью заморожен (`eval`, no-grad, параметры frozen). Один и тот же тип ridge-readout с коэффициентом .01 отдельно подгоняется на probe split: 16×16 билinear произведения отдельно закодированных каналов, среднее по t, затем среднее по f для TDOA и признаки bin32 для фазы. Всего **512 признаков + intercept**, три выхода: нормированная TDOA и cos/sin. Нормировка признаков считывателя только по probe fit. Этот readout сравнительно ёмок для 512 исходных probe-сцен и **не объявляется согласованной low-capacity пробой основного допуска**. Ни truth/u/D ни sensor ID не входят во вход считывателя. Raw/magnitude reference имеют восемь bilinear признаков, поэтому у них иной бюджет readout; сравнение trained/untrained каждого E сопоставимее. В нулевом контроле TDOA всегда 0, фазовый прогноз — средний cos/sin только probe fit. Порог нормы 1e−6 лишь численный; физические пороги не установлены.

### Знаковая задержка: обученные E

| Условие | Re/Im Conv: медиана/p95, мкс | Комплексный Conv: медиана/p95, мкс | Малый гибрид: медиана/p95, мкс | Raw Re/Im + probe, медиана/p95, мкс |
|---|---:|---:|---:|---:|
'''
    for snr,label in [('clean','Без шума'),('0','0 dB'),('10','10 dB'),('20','20 dB')]:
        raw=j['baselines'][snr]['raw']
        text+=f"| {label} | "+' | '.join(pair(n,'trained',snr) for n in NAMES)+f" | {raw['median_tdoa_us']:.3f} / {raw['p95_tdoa_us']:.3f} |\n"
    text+='''
### Что изменило обучение: контроль на 10 dB

| Представление | TDOA необученного → обученного E: медиана, мкс | Фаза необученного → обученного E: медиана, рад | Фаза обученного E: p95, рад |
|---|---:|---:|---:|
'''
    for n,label in NAMES.items():
        text+=f"| {label} | {med(n,'untrained','10','median_tdoa_us'):.3f} → {med(n,'trained','10','median_tdoa_us'):.3f} | {med(n,'untrained','10','median_phase_rad'):.4f} → {med(n,'trained','10','median_phase_rad'):.4f} | {med(n,'trained','10','p95_phase_rad'):.4f} |\n"
    for k,label in [('raw','Raw Re/Im'),('zero_delay_mean_phase','Нулевая задержка / средняя фаза')]:
        r=j['baselines']['10'][k]
        text+=f"| {label} | {r['median_tdoa_us']:.3f} (без E) | {r['median_phase_rad']:.4f} (без E) | {r['p95_phase_rad']:.4f} |\n"
    r=v['magnitude_readout']['10']
    text+=f"| Только модуль, диагностический контроль после запуска | {r['median_tdoa_us']:.3f} (без E) | {r['median_phase_rad']:.4f} (без E) | {r['p95_phase_rad']:.4f} |\n"
    text+='''
По всем условиям отчёта — 512/512 конечных пригодных прогнозов каждой пробы; это coverage, не физический допуск. Полные untrained/phase/feature-std значения каждого seed — `results.json`. Сравнение не даёт независимых групп акустической среды или доверительных интервалов переноса.

### Реконструкция и стоимость

| Сеть | Параметры E | Параметры decoder | Development MSE чистой STFT | Медиана времени 300 шагов, с | Максимальный peak allocated GPU, MiB |
|---|---:|---:|---:|---:|---:|
'''
    for n,label in NAMES.items():
        rr=rows[n];text+=f"| {label} | {rr[0]['encoder_params']} | {rr[0]['decoder_params']} | {st.median(r['dev_reconstruction_mse'] for r in rr):.4f} | {st.median(r['training_seconds'] for r in rr):.3f} | {max(r['peak_allocated_bytes'] for r in rr)/1048576:.2f} |\n"
    text+=f"\nБез сети development MSE самого шумного входа: **{j['runs'][0]['dev_noisy_input_mse']:.4f}** (тот же scale/набор). Время — измеренная синхронизированная часть optimization loop, не цена подготовки, readout/проверок/всего проекта. Peak включает резидентные данные, копию untrained E и decoder, не является максимальной памятью большого E. Основной benchmark целиком: **{j['wall_seconds']:.2f} с**, без повторной проверки/установки. Неожиданно короткий запуск дополнительно проверен повторением 300 optimization steps одного real seed; веса совпали до **{v['one_training_replay']['max_weight_difference']:.2e}** абсолютной ошибки. Это не гарантия битовой воспроизводимости всех GPU-операций.\n"
    text+='''
**Наблюдение, не спрятанный отрицательный результат:** MSE снизилась относительно начала обучения, но у всех моделей осталась хуже исходного шумного входа. Поэтому ни одна из этих конфигураций **не демонстрирует полезное шумоподавление на development**. Возможный вклад — слишком ограниченный decoder с временным stride2/interpolation и стационарная фазово-вращающаяся TF-сетка; причинная роль decoder **не изолирована абляцией**. Нельзя приписывать это доказанному провалу комплексных/реальных encoder вообще. На выходе латентного E информация для парной фазы/задержки всё же доступна по результатам probes.

### Проверки, пробелы и решение

- До обучения: комплексная свёртка сопоставлена с direct complex Conv, radial-equivariance, выходные формы и finite gradients; аналитический тоновый знак для ±u/0. Численные остатки — `results.json/unit_checks`.
- После подозрительно быстрых/аккуратных запусков: проверены все девять checkpoint SHA; веса заново загружены, probes на 10 dB повторены с **нулевой разницей сохранённых метрик**. Один реальный 300-шаговый запуск повторён без перезаписи старых весов. Это повтор того же кода/генератора, **не независимая физическая репликация**.
- Дополнительная проверка реальных размеров source splits: хеши всех исходных amplitude/phase/u групп уникальны и раздельны. Первоначальная проверка ошибочно генерировала по 512 групп для каждого split; исправлена на фактические 2048/256/512/512 и повторена, результаты training/test не менялись. Noise independence/power и magnitude reference сохранены в `verification.json`; это цифровые проверки, не калибровка аппаратуры.
- Предупреждение Torch о преобразовании requires-grad Tensor в float возникло только при численной unit-проверке; код/исходный stdout сохранены, training grads этим не отсекались. Веса лежат вне Git в локальном `.cache/hydroacoustic-doa/encoder-phase-pilot-20261002/`; пути/хеши в results, архивирование/перенос не выполнены. Команда повторного benchmark перезаписывает его локальные outputs/веса; для следующего эксперимента нужен **новый каталог и новый test split**, не повторное использование этого test для подбора.
- Гибрид имеет меньшую медианную фазовую ошибку среди обученных E, но почти без выигрыша от обучения; real Conv лучше по TDOA в этом конкретном считывателе. Raw reference лучше по фазе. Комплексная сеть не показала заявляемого по одному лишь типу арифметики преимущества. Эти наблюдения не исключают потерю информации, которую данный readout не смог обнаружить, и не устанавливают архитектурное превосходство.

**Решение: сохранить все результаты/неудачи; не назначать победителя для основного протокола.** Не менять JEPA scaffold по этому тесту. Если продолжать: на новых development данных сначала проверить decoder/stride как отдельный инженерный фактор; затем зафиксировать один ресурсно доступный E и рецепт EMA/антиколлапс, изучать настоящий latent A/S и заранее согласованные low-capacity phase/TDOA probes, позже независимые multipath/поле. Ни winter evidence, ни допуск E, ни Stage2 этим сравнением не разблокированы.
'''
    return BEGIN+'\n'+text+'\n'+END


def main():
    s=REPORT.read_text()
    section=render()
    if BEGIN in s:
        a=s.index(BEGIN);z=s.index(END,a)+len(END);s=s[:a]+section+s[z:]
    else:
        anchor='## Зависимости через uv: история подготовки (02.10.2026)'
        assert anchor in s;s=s.replace(anchor,section+'\n\n'+anchor)
    REPORT.write_text(s)
    print('Rendered report section from results.json and verification.json')


if __name__=='__main__':main()
