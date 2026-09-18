"""Audit completed/live raw-window traces without model or answer-label access."""
import argparse
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]


def audit(path):
    events=[json.loads(x) for x in (path/'events.jsonl').read_text().splitlines()]
    counts=Counter();seen_docs=set();seen_ranges={};refs={};queries=[];searches=[];opens=[];errors=[]
    def ranges_added(docid,a,b):
        spans=seen_ranges.setdefault(docid,[])
        overlaps=sorted((max(a,x),min(b,y)) for x,y in spans if x<b and a<y)
        covered=0;last=a
        for x,y in overlaps:
            x=max(x,last)
            if y>x:covered+=y-x;last=y
        spans.append((a,b));return b-a-covered
    for e in events:
        if e['kind']=='tool_start':
            counts[e['name']]+=1
            if e['name']=='search':queries.append(e['arguments']['query'])
        if e['kind']=='tool_error':errors.append(e)
        if e['kind']!='tool_result':continue
        items=e['result'] if isinstance(e['result'],list) else [e['result']]
        newdocs=[];newchars=0
        for d in items:
            if 'window_ref' not in d:continue
            ref=d['window_ref'];signature=(d['docid'],d['document_sha256'],d['offset'],d['end_char'],d['text'])
            assert ref not in refs or refs[ref]==signature,'Mutable window reference'
            refs[ref]=signature
            added=ranges_added((d['docid'],d['document_sha256']),d['offset'],d['end_char']);newchars+=added
            if d['docid'] not in seen_docs:newdocs.append(d['docid']);seen_docs.add(d['docid'])
            if e['name']=='search':assert d['text_tokens']+d['title_tokens']<=400
            if e['name']=='open':
                parent=refs[d['parent_window_ref']]
                opens.append({'event':e['seq'],'docid':d['docid'],'ref':ref,'new_chars':added,'status':d['status'],'parent_seen':bool(parent)})
        if e['name']=='search':searches.append({'event':e['seq'],'new_docids':newdocs,'new_raw_chars':newchars})
    return {'tool_calls':dict(counts),'unique_docids':len(seen_docs),'unique_windows':len(refs),
      'duplicate_queries':len(queries)-len(set(queries)),'searches_without_new_docs':sum(not s['new_docids'] for s in searches),
      'searches_without_new_raw_chars':sum(s['new_raw_chars']==0 for s in searches),'searches':searches,'opens':opens,'tool_errors':errors,
      'complete':any(e['kind']=='run_end' for e in events)}


def main():
    p=argparse.ArgumentParser();p.add_argument('batch');args=p.parse_args()
    batchpath=ROOT/'experiments/batches'/args.batch
    manifest=json.loads((batchpath/'batch.json').read_text())
    output={qid:audit(ROOT/run['directory']) for qid,run in manifest['runs'].items() if run.get('directory')}
    (batchpath/'window_audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2));print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
