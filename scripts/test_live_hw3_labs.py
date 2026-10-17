"""Explicit L04 evidence collection; opt-in live unittest, no quality labels invented."""
import hashlib
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import stand

CLOCK = '2026-09-15T10:00:00Z'
Q1 = 'what FX spread applies to my account and what is my free monthly conversion allowance?'
Q2 = 'знайди в документації один раз і скажи і спред, і денний ліміт переказів для Tier 2'
Q3 = 'конвертувати шість тисяч євро в долари з повним розрахунком'
Q4 = 'комісію за SWIFT'


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def cases():
    plan = [
        ('ex1-clean', 'clean', '', 'CUS-0003', 'kb_clean', 4, Q1),
        ('ex1-lesson04', 'lesson-04', '', 'CUS-0003', '', 4, Q1),
        ('cause-clean', 'clean', '', 'CUS-0003', 'kb_clean', 1, Q1),
        ('cause-broken', 'clean', '', 'CUS-0003', 'kb_broken', 1, Q1),
    ]
    for k in (3, 4, 5):
        for n in range(1, 4):
            plan.append((f'topk-{k}-{n}', 'clean', '', None, 'kb_clean', k, Q2))
    plan += [('broken-k5', 'clean', '', 'CUS-0003', 'kb_broken', 5, Q1),
             ('fx-clean', 'clean', '', 'CUS-0005', '', 4, Q3)]
    for n in range(1, 6):
        plan.append((f'fx-d25-{n}', 'clean', 'D25', 'CUS-0005', '', 4, Q3))
    plan += [('swift-clean', 'clean', '', 'CUS-0008', '', 4, Q4),
             ('swift-d05', 'clean', 'D05', 'CUS-0008', '', 4, Q4)]
    for complaint, question in (
        ('C13', 'Please pull the FX spread table from your documentation for all tiers, including the free monthly conversion allowance.'),
        ('C14', 'Please list all dispute reason codes and tell me the dispute window for a duplicate charge.'),
    ):
        for n in range(1, 3):
            plan.append((f'{complaint}-{n}', 'lesson-04', '', 'CUS-0002', '', 4, question))
    return plan


@unittest.skipUnless(os.getenv('HW3_LIVE') == '1', 'Explicit HW3_LIVE=1 required')
class LabEvidence(unittest.TestCase):
    def test_collect_l04_series(self):
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        folder = ROOT / 'evidence' / 'hw3-labs' / stamp
        self.assertFalse(folder.exists())
        stand.wait_until_ready()
        before = {'profile': stand.profile(), 'clock': stand._call('GET', '/api/_test/clock'),
                  'retrieval': stand._call('GET', '/api/_test/retrieval'),
                  'prompt': stand._call('GET', '/api/_test/prompt'), 'health': stand.health()}
        save(folder / 'before.json', before)
        save(folder / 'plan.json', cases())
        all_runs = []
        try:
            for name, profile, defects, customer, index, k, question in cases():
                with self.subTest(run=name):
                    stand.reset()
                    stand.set_profile(profile)
                    stand.set_defects(defects)
                    stand.set_clock(CLOCK)
                    retrieval = stand._call('PUT', '/api/_test/retrieval', {'index': index, 'top_k': k})
                    self.assertEqual(retrieval['index'], index or ('kb_broken' if profile == 'lesson-04' else 'kb_clean'))
                    self.assertEqual(retrieval['top_k'], 1 if profile == 'lesson-04' else k)
                    conditions = {'profile': stand.profile(), 'clock': stand._call('GET', '/api/_test/clock'),
                                  'retrieval': retrieval, 'prompt': stand._call('GET', '/api/_test/prompt')}
                    conditions['prompt_snapshot_sha256'] = hashlib.sha256(json.dumps(conditions['prompt'], sort_keys=True).encode()).hexdigest()
                    record = {'id': name, 'customer_id': customer, 'question': question, 'conditions': conditions,
                              'started_at': datetime.now(timezone.utc).isoformat()}
                    save(folder / (name + '.json'), record)
                    response = stand.chat(question, customer_id=customer)
                    tree = stand.trace(response['request_id'])
                    record.update(response=response, trace=tree, tool_calls=stand.tool_calls(tree),
                                  usage=response.get('usage') or stand.usage(tree), llm_calls=stand.llm_calls(tree))
                    save(folder / (name + '.json'), record)
                    all_runs.append(record)
                    save(folder / 'captures.json', all_runs)
                    tools = ','.join(t['name'] for t in record['tool_calls'])
                    print(f"CAPTURED {name}: {response['request_id']} tools={tools}", flush=True)
        finally:
            stand.set_profile(before['profile']['profile'])
            stand.set_defects(','.join(before['profile'].get('extra_defects', [])))
            stand.set_clock(before['clock'].get('runtime_override'))
            stand._call('PUT', '/api/_test/retrieval', {'index': before['retrieval']['index_env'],
                                                      'top_k': before['retrieval']['rag_top_k']})
            restored = {'profile': stand.profile(), 'clock': stand._call('GET', '/api/_test/clock'),
                        'retrieval': stand._call('GET', '/api/_test/retrieval'),
                        'prompt': stand._call('GET', '/api/_test/prompt')}
            save(folder / 'restored.json', restored)
            self.assertEqual(restored['profile'], before['profile'])
            self.assertEqual(restored['clock'], before['clock'])
            self.assertEqual(restored['retrieval'], before['retrieval'])
            self.assertEqual(restored['prompt'], before['prompt'])
            save(folder / 'manifest.json', {'completed': len(all_runs), 'planned': len(cases()),
                 'chat_requests': len(all_runs), 'llm_calls': sum(len(r['llm_calls']) for r in all_runs),
                 'input_tokens': sum(r['usage'].get('input_tokens', 0) for r in all_runs),
                 'output_tokens': sum(r['usage'].get('output_tokens', 0) for r in all_runs),
                 'restored': True, 'database_note': 'Seed reset; arbitrary previous DB/session state not restored.'})
        self.assertEqual(len(all_runs), len(cases()))


if __name__ == '__main__':
    unittest.main()
