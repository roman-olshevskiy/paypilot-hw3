"""Build corpus-first HW3 cases without reading model answers or calling the stand."""
import hashlib
import json
import re
from pathlib import Path

OUT = Path('/deliverables')
CORPUS = Path('/course/app/rag/corpus')
BASE_HASH = '76c936eba16dd02e0a79cba2345282bf32400e857b356483dd84940ca1c7959b'
base = (OUT / 'sources/golden-v2.jsonl').read_bytes()
if hashlib.sha256(base).hexdigest() != BASE_HASH:
    raise RuntimeError('Expected untouched Golden v2; refusing to append twice or overwrite a changed set')


def number(value):
    groups = f'{value:,}'.split(',')
    return r'(?<![\d.,])' + r'[,\s\u00a0]?'.join(groups) + r'(?!\d|[.,]\d)'


def all_of(*patterns):
    return r'(?is)' + ''.join('(?=.*' + p + ')' for p in patterns) + r'.*'


specs = [
 ('RET-H01', 'lab', 'tariffs.md', 'FX spreads by tier', '| Tier 3 |',
  'From the Verta documentation, what is the standard Tier 3 FX spread after the free allowance is exhausted, and what is its total free monthly conversion allowance? Answer in English with both numbers. Do not quote a sample conversion.',
  'Tier 3: 0.5% spread; EUR 5,000 total free monthly conversion allowance.',
  all_of(r'(?<!\d)0[.,]5\s*%', number(5000)), 'chunking', 'high',
  'Lab exercise 1 derivative; checks both published tariff fields, not the effective spread of a quote.'),
 ('RET-H02', 'corpus', 'limits.md', 'Daily and monthly limits by tier', '| Tier 2 |',
  'Search the Verta documentation for Tier 2 transfer limits. State the full DAILY cap and full MONTHLY cap in EUR, in that order, with the words daily and monthly. I want published caps, not a remaining balance. Answer in English.',
  'Daily EUR 20,000; monthly EUR 200,000.',
  all_of(r'daily(?:(?!\bmonthly\b)[^\n;])*?' + number(20000), r'monthly(?:(?!\bdaily\b)[^\n;])*?' + number(200000)), 'top_k', 'high',
  'New two-column published-cap check; differs from HW2 remaining-balance engine tests and lab spread-plus-daily query.'),
 ('RET-H03', 'corpus', 'limits.md', 'Daily and monthly limits by tier', '| Tier 1 |',
  'According to Verta documentation, what are the full daily and monthly transfer caps for Tier 1? Label daily and monthly separately and answer in English. Do not calculate a remaining balance.',
  'Daily EUR 5,000; monthly EUR 50,000.',
  all_of(r'daily(?:(?!\bmonthly\b)[^\n;])*?' + number(5000), r'monthly(?:(?!\bdaily\b)[^\n;])*?' + number(50000)), 'chunking', 'high',
  'Independent Tier 1 limits row; detects substitution of higher-tier limits or swapping the two columns.'),
 ('RET-H04', 'corpus', 'limits.md', 'Daily and monthly limits by tier', '| Tier 3 |',
  'Find the published Tier 3 transfer limits in Verta documentation. What is the daily cap and what is the monthly cap, in EUR? Use daily and monthly labels and answer in English.',
  'Daily EUR 100,000; monthly EUR 1,000,000.',
  all_of(r'daily(?:(?!\bmonthly\b)[^\n;])*?' + number(100000), r'monthly(?:(?!\bdaily\b)[^\n;])*?' + number(1000000)), 'chunking', 'high',
  'Independent Tier 3 row; covers the million-EUR monthly value and daily/monthly mapping absent from HW2.'),
 ('RET-H05', 'corpus', 'tariffs.md', 'FX spreads by tier', '| Tier 1 |',
  'Look up the Tier 1 row in Verta documentation. Give its standard FX spread after the free allowance is exhausted and its total free monthly conversion allowance in EUR. Answer in English; no sample quote.',
  'Tier 1: 1.5% spread; EUR 500 total monthly conversion allowance.',
  all_of(r'(?<!\d)1[.,]5\s*%', number(500)), 'chunking', 'high',
  'Published Tier 1 terms, not HW2 conversion amounts or remaining allowance; separate tariff row from H01.'),
 ('RET-H06', 'corpus', 'tariffs.md', 'Transfer fees by type', '| SEPA |',
  'Search Verta documentation: what is the fixed EUR fee for a SEPA transfer? State the fixed fee in English, using a decimal amount.',
  'SEPA fixed fee EUR 0.35.', r'(?i)(?<!\d)0[.,]35(?!\d)', 'top_k', 'medium',
  'SEPA flat-fee observable; HW2 SWIFT total-fee scenarios do not cover this transfer type.'),
 ('RET-H07', 'corpus', 'tariffs.md', 'Transfer fees by type', '| Card payment |',
  'According to Verta transfer tariff documentation, what percentage fee applies to a card payment? Answer in English and include the percentage.',
  'Card payment percentage fee 1.2%.', r'(?i)(?<!\d)1[.,]2\s*%', 'chunking', 'high',
  'Card-payment percentage tariff, distinct from FX spreads and SWIFT or SEPA fees.'),
 ('RET-H08', 'corpus', 'disputes.md', 'Reason codes and chargeback windows', '| goods_not_received |',
  'Search Verta dispute documentation for goods_not_received. What is its dispute window in days from the transaction date? Answer in English; include the exact reason code and the number of days.',
  'goods_not_received: 90 days.', all_of(r'\bgoods_not_received\b', r'\b90\s*(?:calendar\s+)?days\b'), 'chunking', 'high',
  'Reason-specific published window; HW2 goods_not_received scenario checks compliance eligibility, not this window.'),
 ('RET-H09', 'corpus', 'disputes.md', 'Reason codes and chargeback windows', '| unauthorized_debit |',
  'Find unauthorized_debit in Verta dispute documentation. State its dispute window in days from the transaction date. Answer in English with the exact reason code and number of days.',
  'unauthorized_debit: 56 days.', all_of(r'\bunauthorized_debit\b', r'\b56\s*(?:calendar\s+)?days\b'), 'chunking', 'high',
  'Previously uncovered reason code with a distinct 56-day window; catches defaulting to 60/90/120.'),
 ('RET-H10', 'corpus', 'disputes.md', 'Reason codes and chargeback windows', '| service_not_rendered |',
  'Look up service_not_rendered in the Verta dispute rules. How many days from the transaction date does its dispute window last? Answer in English with the exact reason code and number of days.',
  'service_not_rendered: 90 days.', all_of(r'\bservice_not_rendered\b', r'\b90\s*(?:calendar\s+)?days\b'), 'chunking', 'high',
  'Different policy row and reason code from goods_not_received; catches a missing or mislabelled supported reason.'),
]
cases, provenance = [], []
for cid, source, doc, section, prefix, question, expected, pattern, mode, severity, novelty in specs:
    lines = (CORPUS / doc).read_text(encoding='utf-8').splitlines()
    matches = [(i, line) for i, line in enumerate(lines, 1) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f'Ambiguous source {cid}: {matches}')
    line_no, reference = matches[0]
    if not re.search(pattern, expected):
        raise RuntimeError(f'Pattern does not accept corpus-derived expectation for {cid}')
    context = {'clock': '2026-09-15T10:00:00Z'}
    if cid == 'RET-H01':
        context['customer_id'] = 'CUS-0003'
    case = {'id': cid, 'input': question, 'expected_output': expected, 'context': context,
      'additional_metadata': {'layer': 'retrieval', 'oracle': 'corpus', 'assertion': 'regex',
        'pattern': pattern, 'reference': reference, 'corpus_source': f'{doc}:{line_no}, {section}',
        'why_this_level': 'Level 3 checks explicit published facts in the answer; regex tolerates numeric grouping/decimal formatting. Retrieved-context coverage needs separate trace inspection.',
        'source': source, 'failure_mode': mode, 'severity': severity, 'runs': 1, 'gate': 'daily',
        'added_in': 'hw3', 'origin': 'own', 'novelty': novelty}}
    cases.append(case)
    provenance.append({'id': cid, 'file': doc, 'line': line_no, 'reference': reference,
                       'source_sha256': hashlib.sha256((CORPUS/doc).read_bytes()).hexdigest(), 'novelty': novelty})
old = [json.loads(line) for line in base.decode('utf-8').splitlines() if line.strip()]
assert len(old) == 37
assert not ({r['id'] for r in old} & {r['id'] for r in cases})
assert len({r['input'] for r in old+cases}) == len(old+cases)
assert sum(r['additional_metadata']['source'] == 'lab' for r in cases) == 1
# Verify numerical guardrails reject neighbouring tiers/extra trailing digits.
assert not re.search(number(500), 'EUR 5,000')
assert not re.search(number(5000), 'EUR 50,000')
assert re.search(number(1000000), 'EUR 1 000 000')
assert not re.search(cases[1]['additional_metadata']['pattern'], 'Daily EUR 200,000 monthly EUR 20,000')
assert not re.search(cases[0]['additional_metadata']['pattern'], 'Tier 3 spread 0.5%; allowance EUR 500.')
assert not re.search(cases[8]['additional_metadata']['pattern'], 'unauthorized_debit: 60 days.')
data = base + (b'' if base.endswith(b'\n') else b'\n')
data += ''.join(json.dumps(c, ensure_ascii=False)+'\n' for c in cases).encode('utf-8')
(OUT / 'golden.jsonl').write_bytes(data)
proof = {'base_sha256': BASE_HASH, 'base_bytes_preserved': data[:len(base)] == base,
         'cases_before': 37, 'cases_after': 47, 'added_retrieval': 10, 'lab_derived': 1,
         'sha256': hashlib.sha256(data).hexdigest(), 'set_hash': hashlib.sha256(data).hexdigest()[:12],
         'method': 'Reference rows from local corpus; no model answers read; no live requests.',
         'cases': provenance}
(OUT/'evidence/retrieval-provenance.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k != 'cases'}, indent=2))
