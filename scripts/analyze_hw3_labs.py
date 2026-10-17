"""Offline inventory of raw L04 evidence; heuristic answer flags are explicit."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
folder = sorted((ROOT / 'evidence/hw3-labs').iterdir())[-1]
rows = json.loads((folder / 'captures.json').read_text(encoding='utf-8'))
out = []
for r in rows:
    searches = [t['result'] for t in r['tool_calls'] if t['name'] == 'search_knowledge_base']
    fragments = [f for s in searches for f in s['fragments']]
    unique = {f['id']: f for f in fragments}
    quote = [t['result'] for t in r['tool_calls'] if t['name'] == 'quote_fx']
    answer = r['response']['answer']
    entry = {'id': r['id'], 'request_id': r['response']['request_id'],
             'searches': searches, 'unique_fragment_ids': list(unique),
             'answer': answer, 'quotes': quote, 'usage': r['usage'],
             'models': sorted({a.get('gen_ai.request.model', '') for a in r['llm_calls']}),
             'prompt_snapshot_sha256': r['conditions']['prompt_snapshot_sha256']}
    if r['id'].startswith('topk-'):
        facts = [any(f['id'] == fid for f in fragments) for fid in ('tariffs.md#s2', 'limits.md#s1')]
        relevant = sum(f['id'] in ('tariffs.md#s2', 'limits.md#s1') for f in fragments)
        entry.update(context_recall={'n': sum(facts), 'm': 2},
                     context_precision={'n': relevant, 'm': len(fragments)},
                     complete_answer_candidate=bool(re.search(r'0[.,]9', answer) and re.search(r'20[ ,\u00a0]?000', answer)))
    out.append(entry)
(folder / 'inventory.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
for e in out:
    print(json.dumps({k: v for k, v in e.items() if k not in ('searches', 'answer', 'quotes')}, ensure_ascii=False))
