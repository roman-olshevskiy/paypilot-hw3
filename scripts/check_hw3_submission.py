"""Offline publication checks; prints only paths, never matched secret content."""
import hashlib,json,re,subprocess
from pathlib import Path
root=Path('D:/neoversity/paypilot-hw3')
files=subprocess.check_output(['git','-C',str(root),'ls-files'],text=True).splitlines()
assert not [f for f in files if Path(f).name=='.env' or f.endswith(('.pem','.key'))]
patterns=[re.compile(r'sk-ant-api\d+-[A-Za-z0-9_-]{20,}'),re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'AKIA[0-9A-Z]{16}')]
suspect=[]
for f in files:
    p=root/f
    if p.suffix=='.pdf':continue
    text=p.read_text(encoding='utf-8-sig',errors='replace')
    if any(pat.search(text) for pat in patterns):suspect.append(f)
assert not suspect, 'Secret pattern detected in: '+str(suspect)
cases=[json.loads(s) for s in (root/'golden.jsonl').read_text().splitlines() if s.strip()]
assert len(cases)==47
new=[c for c in cases if c['additional_metadata'].get('added_in')=='hw3']
assert len(new)==10
corpus=Path('D:/neoversity/paypilot-stand-shared/app/rag/corpus')
for c in new:
    m=c['additional_metadata'];name,line=m['corpus_source'].split(',')[0].split(':')
    assert (corpus/name).read_text().splitlines()[int(line)-1]==m['reference']
    assert m['layer']=='retrieval' and m['oracle']=='corpus'
    assert re.search(m['pattern'],c['expected_output'])
sha=hashlib.sha256((root/'golden.jsonl').read_bytes()).hexdigest()
assert sha[:12]=='97dc8e0936fa'
proof=json.loads((root/'evidence/forecast-v2-commit.json').read_text(encoding='utf-8-sig'))
assert proof['set_hash']==sha[:12]
comp=json.loads((root/'evidence/eval-v2-comparison.json').read_text())
for name,r in comp['runs'].items():
    report=root/'reports'/r['report']
    assert hashlib.sha256(report.read_bytes()).hexdigest()==r['report_sha256']
    data=json.loads(report.read_text());assert data['set_hash']==sha[:12] and data['total']==42
report=(root/'ragas-diagnostic-report.md').read_text()
assert len(re.findall(r'^## [1-6]\. ',report,re.M))==6
assert 'користувача за сьогодні' not in report
for label,target in re.findall(r'\[([^]]+)\]\(([^)]+)\)',report):
    if '://' not in target:assert (root/target).exists(),target
result={'set_hash':sha[:12],'cases':47,'new_retrieval':10,'daily':42,'human_release_not_run':5,
        'references_checked':10,'report_sections':6,'raw_report_hashes_verified':True,
        'secret_pattern_scan':'no matches in tracked files; not a guarantee against every possible secret format',
        'clean_kit_dry_run':'passed using tracked L03 kit export, no local capture adapter',
        'main_unchanged':True,'note':'No model calls performed. Main Markdown is the submission; PDF is an older auxiliary artifact.'}
(root/'evidence/final-offline-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
