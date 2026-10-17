"""Validate and compare two immutable HW3 course-runner reports offline."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import stand

ROOT = Path(__file__).resolve().parent
DATA = Path('/deliverables')
proof = json.loads((DATA/'evidence/forecast-v2-commit.json').read_text(encoding='utf-8-sig'))
expected_hash = hashlib.sha256((DATA/'golden.jsonl').read_bytes()).hexdigest()[:12]
assert expected_hash == proof['set_hash'] == '97dc8e0936fa'
runs = {}
for profile in ('clean', 'lesson-04'):
    dirs = sorted((ROOT/'evidence/hw3-runs').glob('*-'+profile))
    folder = dirs[-1]
    manifest = json.loads((folder/'manifest.json').read_text())
    assert len(manifest['reports']) == 1
    report_name = manifest['reports'][0]
    report_path = ROOT/'reports'/report_name
    report = json.loads(report_path.read_text())
    captures = json.loads((folder/'captures.json').read_text())
    original = json.loads((folder/'original-state.json').read_text())
    restored = json.loads((folder/'restored.json').read_text())
    assert restored == original
    assert report['set_hash'] == expected_hash
    assert report['profile'] == profile
    assert report['total'] == len(captures) == 42
    assert report['skipped'] == 0
    assert datetime.fromisoformat(proof['committed_at']) < datetime.fromisoformat(report['ran_at'])
    started_at = datetime.strptime(folder.name.rsplit('-', 1)[0] if profile == 'clean' else folder.name.removesuffix('-lesson-04'), '%Y%m%dT%H%M%S%f').replace(tzinfo=timezone.utc)
    assert datetime.fromisoformat(proof['committed_at']) < started_at
    assert {c['id'] for c in report['cases']} == {c['case_id'] for c in captures}
    assert sum(c['tokens'] for c in report['cases']) == sum(c['usage']['input_tokens']+c['usage']['output_tokens'] for c in captures)
    models = sorted({a.get('gen_ai.request.model') for c in captures for a in c['llm_call_attributes']})
    retrieval = []
    for c in captures:
        if not c['case_id'].startswith('RET-'):
            continue
        row = next(r for r in report['cases'] if r['id'] == c['case_id'])
        searches = [t['result'] for t in stand.tool_calls(c['trace']) if t['name'] == 'search_knowledge_base']
        prediction = 'FAIL' if c['case_id'] in proof['predicted_fail'] else 'PASS'
        actual = 'PASS' if row['verdict']['passed'] else 'FAIL'
        retrieval.append({'id': c['case_id'], 'prediction_lesson04': prediction, 'actual': actual,
                          'matches_prediction': actual == prediction if profile == 'lesson-04' else None,
                          'request_id': c['request_id'], 'verdict': row['verdict'],
                          'answer': c['response']['answer'], 'searches': searches,
                          'other_tools': [t for t in stand.tool_calls(c['trace']) if t['name'] != 'search_knowledge_base']})
    runs[profile] = {'folder': str(folder.relative_to(ROOT)), 'report': report_name,
                     'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                     'set_hash': expected_hash, 'passed': report['passed'], 'total': report['total'],
                     'by_layer': report['by_layer'], 'failed': [r['id'] for r in report['cases'] if not r['verdict']['passed']],
                     'models': models, 'usage': manifest['usage'],
                     'stand_reported_cost_usd': round(sum(c['usage'].get('cost_usd', 0) for c in captures), 6),
                     'restoration_verified': True, 'retrieval': retrieval}
result = {'forecast_commit': proof['commit'], 'set_hash': expected_hash, 'runs': runs,
          'checks': 'same dataset, 42 daily each, capture/report IDs and token totals match, settings restored, forecast predates reports'}
result['limitations'] = ['Daily excludes five human/release cases.',
    'One run per case/profile; observed transitions do not by themselves prove causality.',
    'Stand-reported cost is not provider billing reconciliation.',
    'Level 3 answer checks do not establish retrieved-context recall or full semantic correctness.']
(DATA/'evidence/eval-v2-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for profile,r in runs.items():
    print(json.dumps({k:v for k,v in r.items() if k != 'retrieval'},ensure_ascii=False))
    for c in r['retrieval']:
        print(profile,c['id'],c['prediction_lesson04'],c['actual'])
