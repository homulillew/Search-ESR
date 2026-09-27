"""Repository-wide conservative exposure audit; read IDs, never answer content."""
import re
from .common import *
from .source_units import split_units
DEV = ['122','169','228','261','538','637','843','922','971','1259']
SEED = 'source-skeleton-fresh-20260927-v1'
RULE = 'At least 50 whitespace words; at least 3 mechanically delimited source units; at least 2 occurrences of relative/temporal/numeric markers (who/which/that/before/after/between/during/when/digit). SHA256(seed,qid) ascending; first 12; no semantic difficulty filtering.'
def select():
    corpus_path = ROOT/'BCPlus/topics-qrels/queries.tsv'
    corpus = dict(line.split('\t',1) for line in corpus_path.read_text().splitlines() if '\t' in line)
    exposure = {q:[] for q in corpus}; scanned=[]; skipped=[]
    reverse = {text:q for q,text in corpus.items()}
    paths = set(git('-c','core.quotePath=false','ls-files').splitlines())
    # Include task-relevant local experiment work as a conservative exclusion.
    for directory in ('experiments','research_loop'):
        paths.update(rel(p) for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in sorted(paths):
        p=ROOT/name
        if name.startswith(rel(P)+'/') or not p.is_file():continue
        if name.startswith(('BCPlus/','data/','datasets/')):
            skipped.append({'path':name,'reason':'original corpus/data distribution, not experiment exposure'});continue
        if p.suffix.lower() not in ('.json','.jsonl','.md','.txt','.py','.yaml','.yml','.tsv','.csv','.sh','.log'):
            skipped.append({'path':name,'reason':'non-text artifact'});continue
        if p.stat().st_size>100_000_000:
            skipped.append({'path':name,'reason':'over 100 MB; must audit separately before freeze'});continue
        try:t=p.read_text()
        except (UnicodeError,OSError):continue
        hits=set()
        # Conservative: any explicit qid mention counts, including candidate inventories.
        for pat in (r'["\'](?:qid|question_id|query_id)["\']\s*:\s*["\']?(\d+)', r'\bqid\s*[=:]\s*["\']?(\d+)', r'\b(?:qid[_-]?|QID[_-]?)(\d+)\b'):
            hits.update(re.findall(pat,t))
        for m in re.finditer(r'["\'](?:[^"\'\n]*qids|question_ids|query_ids)["\']\s*:\s*\[([^\]]*)\]',t):hits.update(re.findall(r'\b\d+\b',m[1]))
        # Full question prefix (80 chars), plus suffix confirmation: handles banks without qid fields.
        if p.suffix in ('.json','.jsonl'):
            for m in re.finditer(r'"(?:question|original_question|Original Question)"\s*:\s*("(?:\\.|[^"\\])*")',t):
                try: original=json.loads(m[1])
                except ValueError: continue
                if original in reverse:hits.add(reverse[original])
        else:
            for q,text in corpus.items():
                if text[:80] in t and text[-60:] in t:hits.add(q)
        hits &= corpus.keys()
        if len(scanned)%2000==0:print('Exposure files processed:',len(scanned),flush=True)
        scanned.append({'path':name,'sha256':sha(p),'exposed_qids':sorted(hits,key=int)})
        for q in hits:exposure[q].append(name)
    for q in DEV:exposure[q].append('task-explicit-development-bank')
    remaining=[]
    for q,text in corpus.items():
        units=split_units(text)
        eligible=len(text.split())>=50 and len(units)>=3 and len(re.findall(r'\b(?:who|which|that|before|after|between|during|when)\b|\d+',text,re.I))>=2
        if not exposure[q] and eligible:remaining.append(q)
    remaining.sort(key=lambda q:digest([SEED,q]))
    assert len(remaining)>=12,(len(remaining),'insufficient eligible unexposed questions')
    assert not any('over 100 MB' in x['reason'] for x in skipped), 'Review large files before selection'
    selected=remaining[:12]
    write(P/'e0_reference/EXPOSURE_AUDIT.json',{'base':git('rev-parse','HEAD'),'corpus':rel(corpus_path),'corpus_sha256':sha(corpus_path),'rule':'Conservative union of explicit ID fields/lists and exact original-question JSON-field matches and original-question prefix+suffix matches in non-JSON repository text plus local experiments/research_loop. Corpus distribution excluded. Candidate inventory IDs also excluded. No gold/answer fields displayed or used.','scanned_files':scanned,'skipped':skipped,'exposed_qids':sorted([q for q,v in exposure.items() if v],key=int),'exposure_provenance':{q:v for q,v in exposure.items() if v}})
    write(P/'e0_reference/FRESH_SELECTION.json',{'seed':SEED,'eligibility':RULE,'selection_method':'SHA256 canonical JSON [seed,qid], ascending','eligible_unexposed_order':remaining,'selected':selected,'no_reselection':True,'meaning_of_fresh':'repository-experiment-unexposed, not foundation-model-unseen'})
    historical=read(ROOT/'experiments/dynamic_local_obligation/e0_reference/CASES.json')
    dev=[]
    for q in DEV:
        qs={c['belief']['question'] for c in historical if str(c['qid'])==q};assert len(qs)==1
        question=qs.pop();assert question==corpus[q]
        dev.append(dict(qid=q,question=question,question_sha256=digest(question),source_units=split_units(question),exposure='exposed development'))
    fresh=[dict(qid=q,question=corpus[q],question_sha256=digest(corpus[q]),source_units=split_units(corpus[q]),exposure='repository-experiment-unexposed') for q in selected]
    write(P/'e0_reference/DEV_QUESTIONS.json',dev);write(P/'e0_reference/FRESH_QUESTIONS.json',fresh)
    write(P/'e0_reference/SOURCE_UNITS.json',{c['qid']:c['source_units'] for c in dev+fresh})
    print(json.dumps({'scanned':len(scanned),'exposed_qids':sum(bool(v) for v in exposure.values()),'eligible':len(remaining),'fresh':selected}))
if __name__=='__main__':select()
