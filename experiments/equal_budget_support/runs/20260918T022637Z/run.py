import sys,json,hashlib,sqlite3,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('/data/WSH/Search-ESR');sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.window_locator import Selector
out=Path('/tmp/search-esr-equal-budget')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out.mkdir()
tasks=json.loads((ROOT/'experiments/local_support/runs/20260917T184725.353925Z/tasks.offline.json').read_text())
frozen=json.loads((ROOT/'全链路排查报告/Search-Open冻结清单.json').read_text())
for rel,digest in frozen['files'].items():
 assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
b=RawWindowBuilder(tok);db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
rows=[]
for t in tasks:
 text,url=db.execute('select text,url from documents where docid=?',(t['docid'],)).fetchone()
 assert hashlib.sha256(text.encode()).hexdigest()==t['source_hash']
 current=b.search(t['docid'],text,url,t['query']);title=current['title'];tc=b.count(title)
 def view(a,z):return dict(text=text[a:z],offset=a,end_char=z,title=title,title_span=current['title_span'])
 prefix=Selector(tok,budget=400-tc,overlap=0).prefix(text)
 arms=dict(legacy1600=view(0,min(1600,len(text))),prefix400=view(0,len(prefix)),windows400=current)
 for arm,v in arms.items():
  if arm=='windows400': nxt=b.open(v['window_ref'],'after')
  else:
   a=v['end_char'];raw=Selector(tok,budget=1200-tc,overlap=0).prefix(text[a:]);nxt=view(a,a+len(raw))
  def hit(views):
   span=t['reference_span']
   if span is None:return None
   intervals=[(x['offset'],x['end_char']) for x in views]+[tuple(x['title_span']) for x in views if x['title_span']]
   reached=span[0]
   for a,z in sorted(intervals):
    if a<=reached:reached=max(reached,z)
   return reached>=span[1]
  for x in [v,nxt]:assert x['text']==text[x['offset']:x['end_char']]
  nt=tc+b.count(v['text']);rt=tc+b.count(nxt['text'])
  assert arm=='legacy1600' or nt<=400
  assert rt<=1200
  rows.append(dict(task=t['id'],arm=arm,initial=v,after=nxt,initial_hit=hit([v]),after_hit=hit([v,nxt]),initial_tokens=nt,read_tokens=rt))
summary={}
for arm in arms:
 rr=[r for r in rows if r['arm']==arm]
 summary[arm]=dict(positive_cases=sum(r['initial_hit'] is not None for r in rr),initial_hits=sum(r['initial_hit'] is True for r in rr),after_hits=sum(r['after_hit'] is True for r in rr),initial_tokens=sum(r['initial_tokens'] for r in rr),total_tokens=sum(r['initial_tokens']+r['read_tokens'] for r in rr))
pairs=[]
for t in tasks:
 rr={r['arm']:r for r in rows if r['task']==t['id']}
 pairs.append(dict(task=t['id'],query=t['query'],prefix=rr['prefix400']['initial_hit'],window=rr['windows400']['initial_hit'],prefix_after=rr['prefix400']['after_hit'],window_after=rr['windows400']['after_hit']))
for name,value in [('tasks.offline.json',tasks),('observations.json',rows),('summary.json',summary),('pairs.json',pairs)]:
 (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
shutil.copy2(__file__,out/'run.py')
for rel in ['llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py']:
 p=out/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
(out/'manifest.json').write_text(json.dumps(dict(frozen_manifest_verified=True,source_hashes=frozen['files'],protocol='20 existing convenience cases, 19 positive single spans + one unscored mismatch. Fixed documents and queries; same title, title+body budget 400; fixed after once with title+body budget 1200. No API or oracle direction. Legacy1600 has standardized title and continuation, not original whole tool. Actual usage differs. Gold not passed to selectors. Raw slices and budgets asserted.'),indent=2))
print(out);print(json.dumps(summary,indent=2));print(json.dumps(pairs,ensure_ascii=False,indent=2))
