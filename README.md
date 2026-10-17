# L04 · RAGAS Diagnostic Report — PayPilot · ДЗ №3

Статус: підготовка, до лабораторних прогонів. Мандат: Ship it.
Набір із ДЗ2: [paypilot-hw2](https://github.com/roman-olshevskiy/paypilot-hw2), Golden v2, 37 кейсів.
Робоча гілка: codex/hw3. Зміни main — лише через PR після рев’ю.

## Поточна готовність

- golden.jsonl — побайтова копія Golden v2; SHA256 76c936eba16dd02e0a79cba2345282bf32400e857b356483dd84940ca1c7959b.
- set_hash базового набору: 76c936eba16d. 32 daily + 5 human/release.
- Нові retrieval-кейси ще не додані. Це не фінальний набір ДЗ3.
- Оригінал шаблону отримано з посилання викладача; незмінна копія лежить у sources/.
- ragas-diagnostic-report.md — робоча форма; невиміряні поля не заповнені числами з лекції.
- Лабораторні докази L04 і прогони фінального набору ще не виконані.

## Середовище

Стенд: локальний клон репозиторію лектора D:/neoversity/paypilot-stand-shared, commit 86a22ea645536003e356f3095f159ca2a13a57f3.
Кіт: roman-olshevskiy/paypilot-l03-eval, commit 76ce435 (повний hash у evidence/preparation-manifest.json).
Контейнер: paypilot-stand-shared-stand-1, порт 8000; Phoenix — 6006.
Provider: anthropic; LLM_MODEL порожній. У попередніх v2 traces модель claude-haiku-5-5; підтвердити у кожній новій серії.
Clock: 2026-09-15T10:00:00Z. Серії на одному стенді виконувати послідовно.
Shared містить зміни L04 ADR 0005/0006; числові результати лекції не переносяться автоматично.

## Запуск

Після додавання retrieval-кейсів скопіювати golden.jsonl у sets/golden.jsonl чистого кіту L03.
В .env кіту задати STAND_DIR=../paypilot-stand-shared та EVAL_STAND_URL=http://host.docker.internal:8000.

```powershell
docker compose run --rm eval --set golden --dry-run
docker compose run --rm eval --set golden --profile clean
docker compose run --rm eval --set golden --profile lesson-04
```

Ці команди ще не запускалися для фінального набору ДЗ3. Перед запуском lesson-04 має існувати окремий коміт прогнозу.
Daily не оцінює п’ять human/release кейсів; зелений daily-прогін не є результатом усіх кейсів.

## Retrieval-кейси

| id | Джерело | Файл і рядок корпусу |
|---|---|---|
| Ще не додані | — | — |

Мінімум 10 нових кейсів; не більше двох із лабораторних вправ 1–2. Reference дослівно з корпусу, added_in=hw3.

## Прогони

| Прогін | Профіль | Результат | Звіт |
|---|---|---|---|
| Baseline ДЗ3 | clean | не виконувався | — |
| Профіль заняття | lesson-04 | не виконувався | — |

Прогноз до прогону lesson-04: буде сформовано після визначення retrieval-кейсів, до оцінювальних запусків.
Коміт із прогнозом: ще немає.
Що впало / розбіжність із прогнозом: ще не вимірювали.

## Рев’ю

План серій — docs/measurement-plan.md. Походження файлів — evidence/preparation-manifest.json.
Перший checkpoint: каркас та умови вимірювань; після рев’ю — лабораторні прогони.
Окремий репозиторій ДЗ2 не змінюється; сирі історичні звіти не перезаписуються.

L04: 26 captures completed; details: [lab review](docs/lab-review.md). Final dataset runs remain pending.
