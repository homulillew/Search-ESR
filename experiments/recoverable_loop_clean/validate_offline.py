"""Reproduce offline tests and archive traces; never creates a model client.

Usage: python experiments/recoverable_loop_clean/validate_offline.py OUTPUT_DIR
OUTPUT_DIR must not exist, so prior validation results are not overwritten.
"""
from collections import Counter
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    command=[sys.executable,'-m','pytest','-q','tests/recoverable_loop_clean','tests/test_search_find_v3b.py',
             '--junitxml='+str(out/'junit.xml')]
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='clean-loop-offline-') as temp:
        proc=subprocess.run(command+['--basetemp='+temp],cwd=ROOT,text=True,capture_output=True)
        (out/'pytest.txt').write_text(proc.stdout+proc.stderr)
        traces=out/'traces';traces.mkdir()
        for p in Path(temp).rglob('*.jsonl'):
            if p.name=='tampered.jsonl': continue
            dest=traces/(p.parent.name+'__'+p.name)
            shutil.copyfile(p,dest)
    counts=Counter()
    tree=ET.parse(out/'junit.xml')
    for case in tree.findall('.//testcase'):
        status='failed' if case.find('failure') is not None or case.find('error') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
        counts[status]+=1
    source_files=[]
    for folder in ['llm_chat/recoverable_loop','tests/recoverable_loop_clean']:
        source_files+=list((ROOT/folder).glob('*.py'))
    report={'kind':'offline_engineering_validation','git_head_before_uncommitted_implementation':
            subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':command,'counts':dict(counts),'exit_code':proc.returncode,
            'elapsed_seconds':time.monotonic()-start,'python':sys.version,
            'dependencies':{p:version(p) for p in ['pytest','jsonschema']},
            'paid_api_requests':0,'live_bcplus_rollouts':0,'input_tokens':0,'output_tokens':0,
            'cache_hit_rate':None,'cache_note':'No requests; cache rate is undefined, not 0%.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_files)},
            'trace_sha256':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(traces.glob('*.jsonl'))},
            'semantic_accuracy_measured':False,
            'limits':'Scripted semantic judgments; network/Config.load denied in new tests, fake corpus and tokenizer, unchanged real executors.'}
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(proc.stdout);print(json.dumps({'counts':dict(counts),'output':str(out)}))
    return proc.returncode


if __name__=='__main__':raise SystemExit(main())
