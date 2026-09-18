"""Prepare source excerpts for human review; no LLM judge, no online gold use."""
import sys,json,re,sqlite3,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from llm_chat.window_locator import terms


def main():
    p=Path(sys.argv[1]).resolve();wanted=set(sys.argv[2:]);tasks={t['qid']:t for t in json.loads((p/'tasks.json').read_text())};pool=json.loads((p/'review_pool.json').read_text())
    gold={str(r['query_id']):r['answer'] for line in (ROOT/'BCPlus/data/bcplus/qa.jsonl').open() if (r:=json.loads(line)) and str(r['query_id']) in tasks}
    db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True);out=[]
    stop=set('the a an of in on at to and or as was were is are this that these those their they who which with from between before after year years name first last certain person individual university article published prior december based following what how one some could can you me it its has had have been into by for not'.split())
    for qid,t in tasks.items():
        if wanted and qid not in wanted:continue
        print('\nQUESTION',qid,t['question'],'\nOFFLINE_ANSWER',gold[qid]);docs=[d for d in pool if d['qid']==qid]
        raw={d['docid']:db.execute('select text from documents where docid=?',(d['docid'],)).fetchone()[0] for d in docs}
        tokens={did:set(terms(text)) for did,text in raw.items()};qt=set(terms(t['question']))-stop
        weights={term:math.log(1+len(docs)/(1+sum(term in ts for ts in tokens.values()))) for term in qt}
        for d in docs:
            text=raw[d['docid']];segments=[]
            for m in re.finditer(r'[^\n]+',text):
                if len(m.group())<40:continue
                score=sum(weights[x] for x in set(terms(m.group()))&qt)
                if score:segments.append((score,m.start(),m.end()))
            segments.sort(reverse=True);selected=[]
            for score,a,z in segments:
                if any(max(a,x)<min(z,y) for x,y in selected):continue
                selected.append((a,min(z,a+650)))
                if len(selected)==2:break
            answer=str(gold[qid]);pos=text.casefold().find(answer.casefold()) if len(answer)>=4 else -1
            if pos>=0:selected=[(max(0,pos-180),min(len(text),pos+len(answer)+280))]+selected[:1]
            snippets=[dict(start=a,end=z,text=text[a:z],visible_in_any_window=any(w['offset']<=a and w['end_char']>=z for w in d['windows'])) for a,z in selected]
            print('DOC',d['docid'],d['title'],'chars',len(text),'answer_literal',pos>=0)
            for v in snippets:print(f"[{v['start']}:{v['end']}]",v['text'].replace('\n',' '))
            out.append(dict(qid=qid,docid=d['docid'],snippets=snippets))
    (p/('review_excerpts_'+('_'.join(sys.argv[2:]) or 'all')+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
