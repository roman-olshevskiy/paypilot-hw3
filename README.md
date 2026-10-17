# L04 · RAGAS Diagnostic Report — PayPilot · ДЗ №3

Статус: 10 нових retrieval-кейсів перевірено offline; оцінювальні прогони ще не виконано.
Мандат Ship it. Зміни main — лише через PR після рев’ю.
База: [ДЗ2, Golden v2](https://github.com/roman-olshevskiy/paypilot-hw2), 37 кейсів.

## Набір

47 кейсів = 37 незмінених базових + 10 retrieval. Daily=42; human/release=5.
set_hash: b3c8813ca3ca. SHA256 і дослівні рядки: evidence/retrieval-provenance.json.
Базові 37 збережено побайтово; копія для відтворення: sources/golden-v2.jsonl.
Один новий кейс походить із лабораторної, дев’ять — із власних запитів до корпусу.
Рівень 3 regex допускає різне форматування чисел; reference залишається дослівним. Подробиці й межі: docs/retrieval-cases-review.md.

## Середовище

stand-shared: 86a22ea; кіт L03: 76ce435. Corpus hashes: evidence/preparation-manifest.json.
Provider anthropic; модель лабораторної claude-haiku-5-5; clock 2026-09-15T10:00:00Z.
Лабораторна: 26 запитів, docs/lab-review.md. Форма звіту ще не завершена.

## Запуск

Покласти golden.jsonl у sets/golden.jsonl чистого кіту L03.
У .env кіту задати STAND_DIR=../paypilot-stand-shared і EVAL_STAND_URL=http://host.docker.internal:8000.

```powershell
docker compose run --rm eval --set golden --dry-run
docker compose run --rm eval --set golden --profile clean
docker compose run --rm eval --set golden --profile lesson-04
```

Dry-run актуального набору успішний. Live-прогони ще не виконувалися; перед ними потрібний окремий коміт прогнозу.
П’ять human/release не входять у daily.
Генератор: scripts/generate_hw3_retrieval.py; запускати в контейнері кіту з app стенду в /course/app і папкою ДЗ3 в /deliverables.

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

## Прогони

| Прогін | Профіль | Результат | Звіт |
|---|---|---|---|
| Baseline | clean | не виконувався | — |
| Профіль заняття | lesson-04 | не виконувався | — |

Прогноз конкретних падінь: наступний етап після рев’ю кейсів. Коміту прогнозу ще немає.
Що впало / розбіжність із прогнозом: ще не вимірювали.

## Статус

Таблиця етапів: docs/status.md. Здане ДЗ2 та історичні звіти не змінювалися.
Оригінальний шаблон: sources/RAGAS_Diagnostic_Report_template.md. Секрети й .env виключені з Git.
