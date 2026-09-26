"""Question-only selection; no answer/evidence labels and no Need-policy calls."""
import json,re,hashlib,subprocess,collections
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dg(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
tracked=subprocess.check_output(['git','ls-files','experiments'],cwd=ROOT,text=True).splitlines();excluded=collections.defaultdict(list)
for name in tracked:
 if name.startswith(str(P.relative_to(ROOT))):continue
 if not name.endswith(('.json','.jsonl')):continue
 if not any(k in Path(name).name.upper() for k in ['INPUT','REQUEST','BANK','SELECT','CHECKPOINT','INVENTORY','CASES','LABEL','QUESTIONS']):continue
 # Conservative question-level exclusion based on any old study inventory/request.
 raw=(ROOT/name).read_text()
 for qid in set(re.findall(r'"qid"\s*:\s*"?(\d+)"?',raw)):
  if len(excluded[qid])<4:excluded[qid].append(name)
questions=[]
for line in (ROOT/'BCPlus/topics-qrels/queries.tsv').read_text().splitlines():
 qid,q=line.split('\t',1)
 if qid not in excluded:questions.append({'qid':qid,'question':q})
questions.sort(key=lambda x:dg(['fresh-belief-acquisition-20260927-v1',x['qid']]))
assert len(questions)>=16
selected=[]
for i,x in enumerate(questions[:16]):selected.append({**x,'case_id':f'F{i+1:02}','split':'development' if i<6 else 'confirmation','acquisition_policy':'historical BC+ discovery Actor + frozen U1 Writer','horizon':3})
save(P/'acquisition/QUESTIONS.json',selected);save(P/'acquisition/EXCLUDED_QIDS.json',dict(excluded))
save(P/'acquisition/SELECTION.json',{'source':'BCPlus/topics-qrels/queries.tsv','source_sha256':sha(ROOT/'BCPlus/topics-qrels/queries.tsv'),'selection':'Exclude any qid recorded in tracked old INPUT/REQUEST/BANK/SELECT/CHECKPOINT/INVENTORY/CASES/LABEL/QUESTIONS JSON artifacts; sort remaining qids by fixed-seed SHA256; first6 dev,next10 confirmation. No gold/answer fields loaded.','excluded_qids':len(excluded),'eligible_qids':len(questions),'development_qids':[r['qid'] for r in selected if r['split']=='development'],'confirmation_qids':[r['qid'] for r in selected if r['split']=='confirmation'],'no_policy_or_model_output_used':True})
print('excluded',len(excluded),'eligible',len(questions));print([(r['case_id'],r['qid'],r['split']) for r in selected])
