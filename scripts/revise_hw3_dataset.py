"""Versioned repair of five known test defects; preserves all other JSONL lines."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path('/deliverables')
OLD = 'b3c8813ca3cacce3f2fd4d101ff1e3cac1b873861ae57896e771893abc1d00f4'
source = ROOT/'sources/golden-hw3-v1.jsonl'
base = source.read_bytes()
assert hashlib.sha256(base).hexdigest() == OLD
lines = base.splitlines(keepends=True)
patched, changes = [], []
for line in lines:
    c = json.loads(line)
    before = json.loads(line)
    m = c['additional_metadata']
    if c['id'] in ('DIS-002-N', 'DIS-006'):
        c['context']['customer_id'] = 'CUS-0004'
    if c['id'] == 'DIS-007':
        c['context']['customer_id'] = 'CUS-0006'
    if c['id'] == 'DIS-002-N':
        m['assertion'] = 'regex'
        m.pop('forbidden_pattern')
        m['pattern'] = r"(?is)^(?=.*(?:\bnot\s+eligible\b|\b(?:cannot|can't)\s+(?:still\s+)?(?:dispute|open|file)\b|\b(?:outside|past)\s+(?:the\s+)?(?:\d+[- ]day\s+)?(?:dispute\s+)?window\b|\bwindow\b[^\n.]*\b(?:closed|expired|passed)\b))(?!.*\byou\s+can(?:\s+still)?\s+(?:dispute|open|file)\b).*"
        c['expected_output'] = 'Explicit refusal or expired dispute window; no offer to dispute/open/file.'
        m['why_this_level'] = 'Level 3 requires an explicit refusal/expired-window statement and rejects a direct offer; uncertainty about eligibility alone is insufficient. This replaces the old bare is eligible prohibition.'
    if c['id'] == 'FX-003-S':
        m['assertion'] = 'regex'
        m['pattern'] = r'(?<![\d.,])0[.,]90*\s*%'
        m['why_this_level'] = 'Level 3 checks 0.9 percent while accepting equivalent 0.90% and decimal-comma formatting; corpus/engine expectation is unchanged.'
    if c['id'] == 'RET-H08':
        m['pattern'] = r'(?is)(?=.*\bgoods_not_received\b)(?=.*\b90\s*(?:calendar\s*)?[-\u2010-\u2015]?\s*days?\b).*'
    if c != before:
        patched.append((json.dumps(c, ensure_ascii=False)+'\n').encode())
        changes.append({'id': c['id'], 'before': before, 'after': c})
    else:
        patched.append(line)
assert len(changes) == 5
result = b''.join(patched)
cases = {c['id']: c for c in map(json.loads, result.splitlines())}


class RegressionChecks(unittest.TestCase):
    def test_authenticated_owners_match_seed(self):
        # Read the actual clean seed using AST; do not query a running stand.
        import ast
        tree = ast.parse(Path('/course/app/seed.py').read_text())
        assignments = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                       and n.targets[0].id in ('CUSTOMERS', 'ACCOUNTS', 'TRANSACTIONS')}
        # Positional IDs are explicit in the course seed tuples.
        self.assertTrue(any(row[0] == 'ACC-1005' and row[1] == 'CUS-0004' for row in assignments['ACCOUNTS']))
        self.assertTrue(any(row[0] == 'TX-0402' and row[1] == 'ACC-1005' for row in assignments['TRANSACTIONS']))
        self.assertTrue(any(row[0] == 'ACC-1007' and row[1] == 'CUS-0006' for row in assignments['ACCOUNTS']))
        self.assertTrue(any(row[0] == 'TX-0601' and row[1] == 'ACC-1007' for row in assignments['TRANSACTIONS']))

    def test_percentage_equivalence_and_wrong_values(self):
        p = cases['FX-003-S']['additional_metadata']['pattern']
        for answer in ('The spread is 0.9%.', 'The spread is 0.90%.', 'Spread 0,900 %'):
            self.assertRegex(answer, p)
        for answer in ('Spread 1.9%', 'Spread 10.9%', 'Spread 0.09%', 'Spread unavailable'):
            self.assertIsNone(re.search(p, answer))

    def test_hyphenated_window_and_wrong_numbers(self):
        p = cases['RET-H08']['additional_metadata']['pattern']
        for answer in ('goods_not_received: 90 days', 'goods_not_received has a 90-day window', 'goods_not_received: 90 calendar days'):
            self.assertRegex(answer, p)
        for answer in ('goods_not_received: 60 days', 'unauthorized_debit: 90-day window', 'goods_not_received: 190 days'):
            self.assertIsNone(re.search(p, answer))

    def test_refusal_rejects_uncertainty_and_positive_offer(self):
        p = cases['DIS-002-N']['additional_metadata']['pattern']
        for answer in ('TX-0402 is not eligible because its window expired.', 'You cannot dispute this charge.', 'It is past the 60-day window.'):
            self.assertRegex(answer, p)
        for answer in ("I can't check whether TX-0402 is eligible.", 'TX-0402 is eligible.',
                       'It is not eligible, but you can still dispute it.', 'No customer is signed in.'):
            self.assertIsNone(re.search(p, answer))

    def test_previous_captured_format_failures_now_pass(self):
        old_captures = list((ROOT/'evidence/eval-runs').glob('*-lesson-04/captures.json'))
        self.assertEqual(len(old_captures), 1)
        captures = json.loads(old_captures[0].read_text())
        for cid in ('FX-003-S', 'RET-H08'):
            answer = next(c['response']['answer'] for c in captures if c['case_id'] == cid)
            self.assertRegex(answer, cases[cid]['additional_metadata']['pattern'])

    def test_unchanged_lines_preserved(self):
        self.assertEqual(len(cases), 47)
        self.assertEqual(sum(a == b for a, b in zip(lines, patched)), 42)
        for change in changes:
            if change['id'] != 'DIS-002-N':
                self.assertEqual(change['before']['expected_output'], change['after']['expected_output'])
            if change['id'] == 'RET-H08':
                self.assertEqual(change['before']['additional_metadata']['reference'], change['after']['additional_metadata']['reference'])


suite = unittest.defaultTestLoader.loadTestsFromTestCase(RegressionChecks)
test_result = unittest.TextTestRunner(verbosity=2).run(suite)
if not test_result.wasSuccessful():
    raise SystemExit(1)
(ROOT/'golden.jsonl').write_bytes(result)
manifest = {'old_set_hash': OLD[:12], 'new_set_hash': hashlib.sha256(result).hexdigest()[:12],
            'sha256': hashlib.sha256(result).hexdigest(), 'cases': 47, 'changed': 5, 'unchanged_lines': 42,
            'offline_tests_passed': test_result.testsRun, 'changes': changes,
            'note': 'HW3 revision only; submitted HW2, original sources and previous raw reports remain unchanged.'}
(ROOT/'evidence/dataset-revision-v2.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k != 'changes'}, indent=2))
