"""Measure observed support spans and reading volume; not full-answer accuracy."""
import argparse,json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');args=ap.parse_args();dest=Path(args.directory)
    tasks=json.loads((dest/'tasks.offline.json').read_text());offline=json.loads((dest/'offline.json').read_text())
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)
    rows=[]
    for task in tasks:
        for arm in ['legacy','windows']:
            path=dest/task['id']/arm
            if not (path/'summary.json').exists():continue
            result=json.loads((path/'summary.json').read_text());events=list(map(json.loads,(path/'events.jsonl').read_text().splitlines()))
            observations=[e['result'] for e in events if e['kind'] in ('initial_observation','read') and 'text' in e['result']]
            span=task['reference_span']
            visible=lambda v:bool(span and v['offset']<=span[0] and v['end_char']>=span[1])
            payload=sum(len(tok.encode(json.dumps(v,ensure_ascii=False),add_special_tokens=False)) for v in observations)
            seen=set();newchars=[]
            for v in observations:
                positions=set(range(v['offset'],v['end_char']));newchars.append(len(positions-seen));seen|=positions
            handoff=(path/'handoff.md').read_text() if (path/'handoff.md').exists() else ''
            cited=set(re.findall(r'w_[a-f0-9]+',handoff));known={v['window_ref'] for v in observations if 'window_ref' in v}
            original=next(x for x in offline if x['task']==task['id'] and x['arm']==arm)
            rows.append({'task':task['id'],'split':task['split'],'arm':arm,'status':result['status'],'reads':result.get('reads',0),
             'initial_reference_visible':visible(observations[0]),'eventual_reference_visible':any(visible(v) for v in observations),
             'one_probe_reference_visible':original['one_read_reference_visible'],'payload_tokens':payload,'initial_payload_tokens':original['initial_payload_tokens'],
             'zero_new_char_reads':sum(x==0 for x in newchars[1:]),'api_tokens':result.get('usage',{}).get('total_tokens',0),
             'invalid_window_refs':sorted(cited-known),'valid_window_refs':sorted(cited&known),
             'tool_errors':sum(e['kind']=='read' and 'error' in e['result'] for e in events)})
    summary={}
    for split in ['all','regression','new_case','regression_mismatch']:
        summary[split]={}
        for arm in ['legacy','windows']:
            group=[r for r in rows if r['arm']==arm and (split=='all' or r['split']==split)]
            eligible=[r for r in group if r['split']!='regression_mismatch']
            summary[split][arm]={'sessions':len(group),'annotated_positive_cases':len(eligible),'initial_span_visible':sum(r['initial_reference_visible'] for r in eligible),
             'one_probe_span_visible':sum(r['one_probe_reference_visible'] for r in eligible),'eventual_span_visible':sum(r['eventual_reference_visible'] for r in eligible),
             **{key:sum(r[key] for r in group) for key in ['reads','payload_tokens','initial_payload_tokens','zero_new_char_reads','api_tokens','tool_errors']},
             'sessions_invalid_refs':sum(bool(r['invalid_window_refs']) for r in group),'complete':sum(r['status']=='complete' for r in group)}
    (dest/'measurements.json').write_text(json.dumps({'notes':'Reference-span visibility is a narrow proxy, not semantic support or answer accuracy. Single annotation per positive task, nonexhaustive. Payload token estimates use local embedding tokenizer, not provider tokenizer.','rows':rows,'summary':summary},ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
