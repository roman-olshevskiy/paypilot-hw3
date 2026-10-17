# Основний звіт для фінального рев’ю

[RAGAS Diagnostic Report](ragas-diagnostic-report.md) - основний файл здачі, шість розділів. PDF у output/pdf - попередня допоміжна версія для перевірки обсягу; після редактури Markdown не оновлювався.
[Додаток із доказами й визначенням метрик](docs/report-evidence.md), [фінальний чекліст](docs/final-review.md).
Сукупні витрати за 17.10.2026 - близько $0.21.
Підготовка звіту не робила нових запитів до моделі. Публікація/PR/merge ще не виконані.

---
# Поточна версія ДЗ3 — HW3 v2

47 кейсів, set_hash 97dc8e0936fa. 42 daily + 5 human/release. Повторний clean: 42/42 (retrieval 10/10); lesson-04: 34/42 (retrieval 7/10 за runner).
У RET-H01 виявлено хибний PASS: гіпотетичне 5,000 не є підтвердженим allowance. За ручним розбором повних відповідей retrieval 6/10; це не context recall і не редагування raw report.
Деталі: [повторні прогони](docs/runs-v2-review.md), [зміни тестів](evidence/dataset-revision-v2.json), [порівняння](evidence/eval-v2-comparison.json).
Прогноз v2 закомічено ДО старту обох повторних серій: 88749f8; evidence/forecast-v2-commit.json.
Поточні звіти: reports/golden-clean-20261017T115231.json і reports/golden-lesson-04-20261017T115632.json.
Відтворення: скопіювати поточний golden.jsonl у sets/golden.jsonl кіту, scripts/hw3_capture.py у корінь кіту; STAND_DIR=../paypilot-stand-shared. Команди нижче застосовуються до поточного набору, якщо явно не позначені v1.
П’ять human/release не запускалися. Здане ДЗ2 не змінювалося.

---

## Історична підготовка та серія v1

Нижче збережено попередні результати й прогнози за версіями. Поточний hash/результати наведено вище.
# L04 · RAGAS Diagnostic Report — PayPilot · ДЗ №3

Статус: clean і lesson-04 завершені; див. [рев’ю прогонів](docs/runs-review.md). Фінальний звіт ще готується.
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

Dry-run і два live-прогони цього набору завершено. Прогноз зафіксовано комітом 7d5bb19 до старту обох серій.
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
| Baseline | clean | 39/42; retrieval 10/10 | reports/golden-clean-20261017T113833.json |
| Профіль заняття | lesson-04 | 29/42; retrieval 5/10 | reports/golden-lesson-04-20261017T114249.json |

Коміт із прогнозом: 7d5bb19; доказ часу й hash набору: evidence/forecast-commit.json.
Нові падіння lesson-04: RET-H01,H03,H08,H09,H10. За id прогноз збігся у 6/10; H08 — форматний false negative. Деталі: docs/runs-review.md.

## Статус

Таблиця етапів: docs/status.md. Здане ДЗ2 та історичні звіти не змінювалися.
Оригінальний шаблон: sources/RAGAS_Diagnostic_Report_template.md. Секрети й .env виключені з Git.

---
# Прогноз до оцінювальних прогонів ДЗ3

Дата: 2026-10-17. Набір: golden.jsonl, 47 кейсів; set_hash b3c8813ca3ca.
Daily: 42, із них 10 retrieval. П’ять human/release не входять до цієї серії.
Стенд: stand-shared 86a22ea; модель очікується claude-haiku-5-5, перевірити за новими traces.
Умови: clean або lesson-04, без extra defects та явного index override, базовий RAG_TOP_K=4, clock 2026-09-15T10:00:00Z.
Дані прогнозу: корпус, фактичні лабораторні traces, правила D16/D17/D05; результати цієї eval-серії ще не отримані.

## Retrieval: точковий прогноз lesson-04

| id | Прогноз | Причина |
|---|---|---|
| RET-H01 | FAIL | Tier 3 allowance обрізаний між tariffs.md#b3 і #b4; k1 не дає повного рядка |
| RET-H02 | FAIL | Загальний query про daily/monthly limits може принести вступ без обох cap; заголовок таблиці також розрізаний |
| RET-H03 | FAIL | Та сама проблема видачі k1 для Tier 1, ризик втрати правильної прив’язки колонок |
| RET-H04 | FAIL | Та сама проблема для Tier 3; вступ може випередити фрагмент із числами |
| RET-H05 | PASS | Повний Tier 1 spread/allowance міститься в tariffs.md#b3 |
| RET-H06 | PASS | SEPA row повністю в tariffs.md#b4; пряме прохання шукати має обійти довідник D05 |
| RET-H07 | PASS | Card payment row цілісний у tariffs.md#b5; D05 стосується переказних комісій |
| RET-H08 | PASS | goods_not_received і 90 цілісні в disputes.md#b2; reason-specific query має його знайти |
| RET-H09 | PASS | unauthorized_debit і 56 цілісні в disputes.md#b3 |
| RET-H10 | FAIL | service_not_rendered розірваний між disputes.md#b2 і #b3; k1 ризикує не принести повний код із числом |

Точковий прогноз: 5/10 retrieval PASS, 5/10 FAIL. Це припущення, а не вимога підігнати результат.
Найменша впевненість у H02–H04: числа всіх tier є в limits.md#b3; вдалий query або повторний пошук може забезпечити PASS.
Навіть H01/H10 можуть пройти за рахунок іншого інструмента, повторного пошуку чи виведення з сусідніх фрагментів.
H06 може впасти, якщо модель усе ж виконає правило D05 або не дістане тарифний рядок.

## Clean і базові кейси

Clean: очікуємо 10/10 нових retrieval PASS при повних секційних фрагментах і k4; можливі промахи ранжування та false negatives формату regex.
Для базових 32 daily не оголошуємо старий результат 30/30 новим baseline: версії стенду/моделі й набір змінилися.
На lesson-04 очікуємо ризик SWF-001/SWF-002 через D05; числовий tool_grounded_numeric може не пройти, якщо модель відповість без потрібного tool.
CMP-C14/CMP-004 можуть втратити window через k1. Жодного точного підсумку для всіх 42 кейсів наперед не заявляємо.

## Фіксація і порівняння

Цей текст включити в README та окремо закомітити ДО clean/lesson-04 eval.
Після коміту зберегти його hash/час і hash набору в evidence/forecast-commit.json; прогноз заднім числом не редагувати.
Після прогонів зіставити кожний RET-H id із прогнозом, а причину розбіжності довести trace.
Сирі reports не змінювати, набір між двома профілями не змінювати.

---
# Прогноз перед повторною серією HW3 v2

Дата: 2026-10-17. Набір 47 кейсів, set_hash 97dc8e0936fa.
Це новий прогноз, зроблений після аналізу v1 і ДО запусків v2. Прогноз v1 у коміті 7d5bb19 не змінюється.
Виправлено customer_id для DIS-002-N/DIS-006/DIS-007, перевірки DIS-002-N/FX-003-S/RET-H08. Зміни очікуваних бізнес-чисел відсутні.

Clean: точковий прогноз 42/42, зокрема 10/10 retrieval. Автентифіковані dispute-кейси мають отримати правильний refusal/eligible=false;
семантично рівні 0.9/0.90% та 90 days/90-day не повинні давати false negative.
Можливі нові промахи пошуку й мовного формату: прогноз не є гарантією.

| Retrieval id | Прогноз lesson-04 | Підстава, відома до v2 |
|---|---|---|
| RET-H01 | FAIL | Обрізаний Tier 3 allowance tariffs.md#b3, повтори не повернули #b4 у v1 |
| RET-H02 | PASS | v1 отримав обидва Tier 2 limits з #b3, попри неповний header |
| RET-H03 | FAIL | v1 пошуки давали limits.md#b1 без чисел |
| RET-H04 | PASS | v1 отримав обидва Tier 3 limits з #b3 |
| RET-H05 | PASS | Повний Tier 1 tariff row у #b3 |
| RET-H06 | PASS | SEPA row цілий у tariffs.md#b4 |
| RET-H07 | PASS | Prompt D05 містить правильний 1.2%; PASS відповіді може приховати відсутність числа в retrieved fragments |
| RET-H08 | PASS | Виправлено форматний false negative; у v1 повторний пошук дістав 90 |
| RET-H09 | FAIL | У v1 потрібний disputes.md#b3 не був виданий |
| RET-H10 | FAIL | У v1 видано вступ без window |

Очікуємо retrieval 6/10 на lesson-04. Припускаємо падіння CMP-004, CMP-C14, SWF-001, SWF-002,
але вже не трьох автентифікованих dispute-кейсів або FX-003-S через формат. Точковий прогноз lesson-04: 34/42.
Один прогін не фіксує поведінку моделі: запити до пошуку, повтори й обхід через інші джерела можуть змінитися.

Окремо оцінювати answer correctness і фактично retrieved evidence; H07 не є доказом успішного retrieval лише тому, що assertion зелений.
Набір між clean і lesson-04 не змінювати. Після серії зберегти всі розбіжності з цим прогнозом.
