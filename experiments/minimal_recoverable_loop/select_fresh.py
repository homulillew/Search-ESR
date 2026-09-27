"""Conservative repository exposure audit; no reference-answer data is opened."""
import re
from .common import *

SEED='minimal-recoverable-loop-fresh-v1'

def main():
    corpus_path=ROOT/'BCPlus/topics-qrels/queries.tsv'
    corpus=dict(line.split('\t',1) for line in corpus_path.read_text().splitlines() if '\t' in line)
    reverse={v:k for k,v in corpus.items()}
    exposure={q:[] for q in corpus};scanned=[];skipped=[]
    paths=set(git('-c','core.quotePath=false','ls-files').splitlines())
    for directory in ('experiments','research_loop'):
        paths.update(rel(p) for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    patterns=[re.compile(p) for p in (r'["\'](?:qid|question_id|query_id)["\']\s*:\s*["\']?(\d+)',r'\bqid\s*[=:]\s*["\']?(\d+)',r'\b(?:qid[_-]?|QID[_-]?)(\d+)\b')]
    for name in sorted(paths):
        p=ROOT/name
        if name.startswith(rel(P)+'/') or not p.is_file():continue
        if name.startswith(('BCPlus/','data/','datasets/')):
            skipped.append({'path':name,'reason':'original distribution, not experiment exposure'});continue
        if p.suffix.lower() not in ('.json','.jsonl','.md','.txt','.py','.yaml','.yml','.tsv','.csv','.sh','.log'):continue
        if p.stat().st_size>100_000_000:raise RuntimeError('Large exposure artifact needs explicit read-only audit: '+name)
        try:t=p.read_text()
        except UnicodeError:continue
        hits=set()
        for pat in patterns:hits.update(pat.findall(t));hits.update(pat.findall(name))
        for m in re.finditer(r'["\'](?:[^"\'\n]*qids|question_ids|query_ids)["\']\s*:\s*\[([^\]]*)\]',t):hits.update(re.findall(r'\b\d+\b',m[1]))
        for m in re.finditer(r'"(?:question|raw_question|original_question|Original Question|Q)"\s*:\s*("(?:\\.|[^"\\])*")',t):
            try:q=reverse.get(json.loads(m[1]))
            except ValueError:q=None
            if q is not None:hits.add(q)
        if p.suffix not in ('.json','.jsonl'):
            for q,question in corpus.items():
                if question[:80] in t and question[-60:] in t:hits.add(q)
        hits &= corpus.keys()
        scanned.append({'path':name,'sha256':sha(p),'exposed_qids':sorted(hits,key=int)})
        for q in hits:exposure[q].append(name)
        if len(scanned)%5000==0:print('Exposure files audited',len(scanned),flush=True)
    for q in {'546','1094','228','637','843','971'}|{r['qid'] for r in read(P/'e0_reference/ADMISSION_BANK.json')}:
        exposure[q].append('current-development-or-admission-bank')
    remaining=sorted([q for q,text in corpus.items() if text.strip() and not exposure[q]],key=lambda q:digest([SEED,q]))
    selected=remaining[:10]
    write(P/'e0_reference/EXPOSURE_AUDIT.json',{'base':BASE,'corpus':rel(corpus_path),'corpus_sha256':sha(corpus_path),'scanned_files':scanned,'skipped':skipped,'exposure_provenance':{q:v for q,v in exposure.items() if v},'gold_answers_read':False,'rule':'Union of explicit qid fields/path mentions/ID lists, exact original-question fields and question text matches in non-JSON; original corpus distribution excluded. Includes local experiments/research_loop; cannot prove foundation-model non-exposure.'})
    write(P/'e0_reference/FRESH_SELECTION.json',{'seed':SEED,'rule':'All nonempty corpus questions with no repository experiment exposure; SHA256 canonical JSON [seed,qid] ascending, first10. No semantic/ease or gold filtering. Fewer than10 retained if shortfall.','eligible':len(remaining),'eligible_unexposed_order':remaining,'selected_qids':selected,'actual':len(selected),'shortfall':max(0,10-len(selected)),'no_replacement':True,'meaning_of_fresh':'repository-experiment-unexposed; no claim of model-training-unseen','questions_not_used_for_prompt_tuning':True})
    write(P/'e0_reference/FRESH_QUESTIONS.json',[{'qid':q,'Q':corpus[q],'question_sha256':text_hash(corpus[q])} for q in selected])
    print('Fresh count',len(selected),'eligible',len(remaining),'selected IDs',selected)

if __name__=='__main__': main()
