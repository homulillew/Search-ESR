"""Mechanically resume only interrupted/unstarted alias cells, preserving originals."""

import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_alias
from llm_chat.client import Config
from openai import OpenAI

HERE=Path(__file__).resolve().parent
REMAINING=[('1094',77),('1094',93)]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def original_events():return [json.loads(x) for x in (HERE/'events.jsonl').open()]


def freeze():
    path=HERE/'freeze_resume.json'
    if path.exists():raise FileExistsError('resume freeze exists')
    config=Config.load()
    doc={
        'frozen_at':datetime.now(timezone.utc).isoformat(),
        'remaining_cells':[f'{q}:{s}:AL' for q,s in REMAINING],
        'original_event_sha256':sha(HERE/'events.jsonl'),
        'original_freeze_sha256':sha(HERE/'freeze.json'),
        'frozen_executor_sha256':sha(HERE/'run_alias.py'),
        'resume_source_sha256':sha(__file__),
        'model':config.model,'base_url_host':urlsplit(config.base_url).hostname,
        'reason':'turn interruption killed process; completed cells retained, partial preserved',
    }
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    return doc


def gate():
    doc=json.loads((HERE/'freeze_resume.json').read_text())
    checks=[]
    def check(label,ok):checks.append((label,bool(ok)))
    check('original frozen gate still passes',run_alias.gate().endswith('PASS'))
    check('original event file unchanged',sha(HERE/'events.jsonl')==doc['original_event_sha256'])
    check('original freeze unchanged',sha(HERE/'freeze.json')==doc['original_freeze_sha256'])
    check('frozen executor unchanged',sha(HERE/'run_alias.py')==doc['frozen_executor_sha256'])
    check('resume source unchanged',sha(__file__)==doc['resume_source_sha256'])
    config=Config.load()
    check('provider same',config.model==doc['model'] and urlsplit(config.base_url).hostname==doc['base_url_host'])
    events=original_events()
    ends={e.get('cell') for e in events if e['kind']=='cell_end'}
    check('exactly first two cells complete',ends=={'546:9:AL','1094:69:AL'})
    check('third cell explicitly interrupted',any(e['kind']=='cell_interrupted' and e.get('cell')=='1094:77:AL' for e in events))
    check('fourth cell not begun',not any(e.get('cell')=='1094:93:AL' for e in events))
    check('mechanical remaining list',doc['remaining_cells']==['1094:77:AL','1094:93:AL'])
    lines=[f'{"PASS" if ok else "FAIL"} {label}' for label,ok in checks]
    lines.append(f'{sum(ok for _,ok in checks)}/{len(checks)} PASS')
    (HERE/'gate_resume.txt').write_text('\n'.join(lines)+'\n')
    if not all(ok for _,ok in checks):raise AssertionError('resume gate failed')
    return lines[-1]


def resume_emit(kind,**fields):
    event={'time':datetime.now(timezone.utc).isoformat(),'kind':kind,**fields}
    with (HERE/'events_resume.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(event,ensure_ascii=False)+'\n');f.flush()


def run():
    gate()
    if (HERE/'events_resume.jsonl').exists():raise FileExistsError('resume events exist')
    config=Config.load()
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher=None
    client=OpenAI(api_key=config.api_key,base_url=config.base_url,
                  timeout=config.timeout,max_retries=2)
    original_emit=run_alias.emit
    try:
        run_alias.emit=resume_emit
        searcher=BCPlusSearcher()
        for case in run_alias.CASES:
            if (case['qid'],case['seq']) in REMAINING:
                print(f"{case['qid']}:{case['seq']}:AL {run_alias.run_cell(client,searcher,case)}",flush=True)
    finally:
        run_alias.emit=original_emit
        client.close()
        if searcher is not None:searcher.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','gate','run'])
    args=parser.parse_args()
    if args.action=='freeze':freeze()
    elif args.action=='gate':print(gate())
    else:run()
