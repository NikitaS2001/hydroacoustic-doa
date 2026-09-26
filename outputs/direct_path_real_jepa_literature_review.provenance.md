# Provenance: direct-path real JEPA review

Дата поиска: 2026-09-26. Режим: целевой, не систематический обзор; primary arXiv full text/PDF Q&A via alpha, библиографический поиск OpenAlex, открытый PMC full text via Europe PMC. Исходные данные проекта и натурные файлы отсутствуют.

| Источник | Доступ/проверенное содержание | Статус |
|---|---|---|
| S1 https://arxiv.org/abs/2411.11726 | alpha_get_paper и alpha_ask_paper, PDF стр. 1–10, §§II–IV, особое внимание §III-D и рис. 6/8 | прочитаны извлечения первичного PDF; нет переноса численных параметров |
| S2 https://arxiv.org/abs/2211.12282 | alpha_get_paper и alpha_ask_paper, PDF §§II, IV, V, прямое утверждение §V-A, что real channel unknown, метрики real symbol MSE/BER | прочитаны извлечения первичного PDF |
| S3 https://arxiv.org/abs/2103.14236 | alpha_get_paper, полный текст §II, IV, V | прочитан первичный текст |
| S4 https://europepmc.org/articles/PMC6554273 | Europe PMC fulltext route; abstract, section excerpts Methods/Results/Discussion | частичные первичные фрагменты, не детальная сверка всех моделей |
| S5 https://arxiv.org/abs/2308.12203 | alpha_get_paper, полный текст §§I–IV | прочитан первичный текст |
| S6 https://arxiv.org/abs/2301.08243 | alpha_get_paper, первичный текст §3 | прочитан первичный текст |
| P1–P3 | локальные README.md, summaryV2.md, training_strategy.md, architecture.md, winter_field_protocol.md; ранее в текущей сессии | локальный план, не эмпирика |

Поиск: alpha semantic по underwater OFDM preamble, multipath direct-path, underwater impulse response; alpha keyword по Berger et al.; OpenAlex `openalex_search_works:underwater acoustic OFDM channel estimation sparse multipath first arrival` и `underwater acoustic channel impulse response measurements probing signal matched filter time varying multipath`. У OpenAlex отмечено отсутствие API key, но метаданные возвращены. Berger et al., *Sparse Channel Estimation for Multicarrier Underwater Acoustic Communication* (2010), DOI https://doi.org/10.1109/TSP.2009.2038424 найден по метаданным, но полный текст **не прочитан**; его результаты в отчёт не включены.

Проверка: локальные ссылки и отсутствие управляющих символов проверить перед выдачей. Модельные уравнения, разрешение ~1/B_eff и список gating metrics — аналитический вывод/предлагаемые измерения, а не готовые результаты. Возможность A/R в данном заливе **не проверена**. Не проводились код, симуляции, запись, количественная мета-аналитика или расчёт статистической мощности.
