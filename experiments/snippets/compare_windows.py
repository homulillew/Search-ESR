"""Replay frozen v001 observations: fixed chunks versus anchor + context window."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.snippets.window import WindowSelector
from transformers import AutoTokenizer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',default='experiments/offline/snippets_v001/20260917T095014.433850Z')
    args = parser.parse_args()
    source = ROOT/args.source
    original = json.loads((source/'manifest.json').read_text())
    dest = ROOT/'experiments/offline/snippets_v002'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    dest.mkdir(parents=True)
    manifest = {'source':str(source.relative_to(ROOT)), 'source_comparisons_sha256':hashlib.sha256((source/'comparisons.jsonl').read_bytes()).hexdigest(),
                'budget':original['per_document_text_token_cap'], 'tokenizer':original['tokenizer'],
                'scope':'Offline frozen queries/documents. A=v001 fixed BM25 chunk, B=sentence/line BM25 anchor plus alternating context expansion.',
                'limitations':['Candidate units change BM25 statistics; not an expansion-only ablation.',
                               'Regex sentence boundaries; only Markdown headings delimit sections; no HTML cleaning or remote headers.',
                               'Equal text token caps, not equal actual consumption; metadata overhead excluded. No online claims.'],
                'source_sha256':{}}
    for name in ['selector.py','window.py','compare_windows.py']:
        path = Path(__file__).parent/name
        shutil.copy2(path,dest/name)
        manifest['source_sha256'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    tokenizer = AutoTokenizer.from_pretrained(original['tokenizer'],local_files_only=True,use_fast=True)
    selector = WindowSelector(tokenizer,budget=manifest['budget'])
    dbpath = ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
    db = sqlite3.connect(f'{dbpath.as_uri()}?mode=ro',uri=True)
    cache, rows, reports = {}, [], {}
    for line in (source/'comparisons.jsonl').read_text().splitlines():
        old = json.loads(line)
        did = old['docid']
        if did not in cache:
            text = db.execute('SELECT text FROM documents WHERE docid=?',(did,)).fetchone()[0]
            cache[did] = (text,selector.units(did,text) if not old['raw_html'] else [])
        text, units = cache[did]
        assert hashlib.sha256(text.encode()).hexdigest() == old['document_sha256']
        if old['raw_html']:
            new = dict(old['A'],anchor=None,selection={'fallback':'raw_html_deferred_use_prefix'},stop={})
        else:
            new = selector.observe(old['query'],text,units)
        assert new['text'] == text[new['start_char']:new['end_char']]
        assert selector.count(new['text']) == new['tokens'] <= manifest['budget']
        row = {k:old[k] for k in ['qid','search_number','source_event','rank','query','docid','url','document_score','document_sha256']}
        row.update(A=old['B'],B=new,unit_count=len(units))
        rows.append(row)
        report = reports.setdefault(row['qid'],[f'# qid={row["qid"]} 固定块与定位后扩展对照',''])
        report.extend([f'## Search {row["search_number"]} / Rank {row["rank"]} / docid {did}', '', row['query'],''])
        for key in ['A','B']:
            obs = row[key]
            report.extend([f'### {key} · {obs["tokens"]} tokens · [{obs["start_char"]}, {obs["end_char"]})','', '````text',obs['text'],'````',''])
        report.extend(['定位与停止信息：`'+json.dumps({k:v for k,v in new.items() if k!='text'},ensure_ascii=False)+'`',''])
    with (dest/'comparisons.jsonl').open('w') as out:
        for row in rows:out.write(json.dumps(row,ensure_ascii=False)+'\n')
    summary = {}
    for qid, report in reports.items():
        (dest/f'qid_{qid}.md').write_text('\n'.join(report))
        group = [r for r in rows if r['qid']==qid]
        summary[qid] = {'observations':len(group),'documents':len({r['docid'] for r in group}),
                        'A_tokens':sum(r['A']['tokens'] for r in group),'B_tokens':sum(r['B']['tokens'] for r in group),
                        'changed_windows':sum(r['A']['text']!=r['B']['text'] for r in group),
                        'expanded_windows':sum(r['B'].get('expanded_units_before',0)+r['B'].get('expanded_units_after',0)>0 for r in group),
                        'oversize_anchors':sum((r['B'].get('anchor') or {}).get('boundary')=='oversize_split' for r in group),
                        'fallbacks':sum(bool(r['B']['selection']['fallback']) for r in group)}
    (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    db.close()
    print(dest)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
