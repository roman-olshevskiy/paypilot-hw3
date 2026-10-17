# L04 · RAGAS Diagnostic Report — PayPilot

ДЗ №3. Мандат: Ship it.

Основний файл здачі: [ragas-diagnostic-report.md](ragas-diagnostic-report.md). Шість розділів звіту доповнює [покажчик доказів](docs/report-evidence.md).

## Набір

База: [Golden v2 із ДЗ №2](https://github.com/roman-olshevskiy/paypilot-hw2). Поточний набір — 47 кейсів: 42 daily та 5 human/release, із них 10 нових retrieval.

`set_hash`: **97dc8e0936fa**.

Джерело еталонів: корпус Verta у stand-shared `86a22ea`; reference дослівні. [Походження кейсів](evidence/retrieval-provenance.json). Після першої серії виправлено п’ять недоліків тестів: [зміни v2](evidence/dataset-revision-v2.json). Попередні версії збережені в `sources/`; здане ДЗ2 не змінювалося.

## Запуск

Кіт: [paypilot-l03-eval](https://github.com/roman-olshevskiy/paypilot-l03-eval), `76ce435`. Скопіювати `golden.jsonl` у `sets/golden.jsonl` кіту. У `.env` кіту: `STAND_DIR=../paypilot-stand-shared`, `EVAL_STAND_URL=http://host.docker.internal:8000`.

```powershell
docker compose run --rm eval --set golden --dry-run
docker compose run --rm eval --set golden --profile clean
docker compose run --rm eval --set golden --profile lesson-04
```

Для повних трейсів скопіювати `scripts/hw3_capture.py` у корінь кіту:

```powershell
docker compose run --rm -T eval python hw3_capture.py --set golden --profile clean
docker compose run --rm -T eval python hw3_capture.py --set golden --profile lesson-04
```

Модель серій: Anthropic `claude-haiku-5-5`; clock `2026-09-15T10:00:00Z`. Профіль, додаткові дефекти, clock і retrieval після запусків відновлено. БД/сесії скидаються до seed. Прогони на одному стенді виконувати послідовно.

## Retrieval-кейси

| id | Джерело | Файл і рядок корпусу |
|---|---|---|
| RET-H01 | lab | tariffs.md:16, FX spreads by tier |
| RET-H02 | corpus | limits.md:12, Daily and monthly limits by tier |
| RET-H03 | corpus | limits.md:11, Daily and monthly limits by tier |
| RET-H04 | corpus | limits.md:13, Daily and monthly limits by tier |
| RET-H05 | corpus | tariffs.md:14, FX spreads by tier |
| RET-H06 | corpus | tariffs.md:22, Transfer fees by type |
| RET-H07 | corpus | tariffs.md:24, Transfer fees by type |
| RET-H08 | corpus | disputes.md:9, Reason codes and chargeback windows |
| RET-H09 | corpus | disputes.md:12, Reason codes and chargeback windows |
| RET-H10 | corpus | disputes.md:11, Reason codes and chargeback windows |

Лише H01 походить із лабораторної, решта — власні запити до корпусу. L3 regex допускає еквівалентне форматування чисел; він не обчислює context recall автоматично.

## Прогони

| Прогін v2 | Профіль | Daily | Retrieval за ранером | Сирий звіт |
|---|---|---|---|---|
| Baseline | clean | 42/42 | 10/10 | [clean](reports/golden-clean-20261017T115231.json) |
| Профіль заняття | lesson-04 | 34/42 | 7/10 | [lesson-04](reports/golden-lesson-04-20261017T115632.json) |

Обидва звіти мають hash `97dc8e0936fa`; 5 human/release не запускалися. [Порівняння](evidence/eval-v2-comparison.json).

Прогноз v2: окремий коміт **88749f8 до старту обох серій**. [Текст](docs/forecast-v2-before-runs.md), [hash і час](evidence/forecast-v2-commit.json).

Очікували retrieval FAIL для H01/H03/H09/H10; ранер відхилив H03/H09/H10. H01 має хибний PASS: гіпотетичні 5,000 зараховано як підтверджений allowance. За id прогноз збігся у 9/10; ручний розбір відповідей дає 6/10, а не 7/10. Це не context recall. H07 отримав 1.2% із промпту, а не з документа.

[Розбір v2](docs/runs-v2-review.md) містить усі обмеження, включно з fallback без customer_id у DIS-001. [Серія v1](docs/runs-review.md) збережена окремо; raw reports не редагувалися.

## Витрати та стан

Сукупні витрати за 17.10.2026 — близько $0.21. Оцінки окремих серій зі стенду наведені в розборах.

[Таблиця етапів](docs/status.md) · [Фінальний чекліст](docs/final-review.md).

PDF у `output/pdf/` — попередня допоміжна версія для перевірки обсягу. Для здачі використовувати актуальний Markdown.
