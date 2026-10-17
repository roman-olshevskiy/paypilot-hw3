# ДЗ3 — нові retrieval-кейси для рев’ю

Крок 5 завершено: 47 кейсів, з них 10 нових retrieval; set_hash b3c8813ca3ca. Daily=42, human/release=5.

| Кейси | Нове покриття |
|---|---|
| RET-H01 | Tier 3: стандартний spread і повний allowance; один похідний кейс вправи 1 |
| RET-H02…H04 | Опубліковані daily/monthly caps для трьох tier; це не remaining balance з HW2 |
| RET-H05 | Tier 1: spread і повний allowance без sample quote |
| RET-H06 | Фіксована SEPA fee, інший тип переказу, ніж SWIFT у HW2 |
| RET-H07 | Процентна комісія card payment, не FX spread |
| RET-H08 | Window goods_not_received; HW2 перевіряє compliance eligibility, не цей observable |
| RET-H09 | Раніше не покритий unauthorized_debit та його 56-денне вікно |
| RET-H10 | Окремий reason code service_not_rendered та його policy row |

H08/H10 мають однакове число 90, але різні policy rules; regex вимагає правильний reason code.
C-13/C-14 залишаються в лабораторній діагностиці. Дублікат існуючого CMP-C14 як новий кейс не додаємо.

Перевірено: loader прийняв усі 47; базові 37 збережено побайтово; нові id/input унікальні; всі reference дослівно з відповідного рядка корпусу.
Provenance містить файл, номер рядка й SHA256 джерела. Ручне звірення: H01 — 0.5%/EUR 5,000; H06 — SEPA EUR 0.35; H09 — unauthorized_debit 56.
Лише один lab-derived case із дозволених двох. Live/model викликів на цьому етапі не було.

Використано підтримуваний assertion=regex рівня 3 замість contains: допускає крапку/кому й розділювачі тисяч, прив’язує daily/monthly до відповідних сум.
expected_output пояснює очікування; фактичну перевірку виконує metadata.pattern.
Негативні offline-перевірки відхилили 500 замість 5,000, 60 замість 56 та переставлені daily/monthly.

Межі: це перевірка явних фактів, а не всіх суперечностей відповіді. Для daily/monthly очікується label і число в одному рядку; інший коректний формат може дати false negative.
Course runner не обчислює context recall лише з layer=retrieval: потрібні окремі traces і зіставлення з reference.
Англійські запити утримують переклад поза предметом цієї серії.

Наступне: рев’ю кейсів → конкретний прогноз за id → окремий коміт → незмінний набір clean/lesson-04.
