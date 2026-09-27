"""Freeze selection, preflight and source dependencies before any paid call."""
from dataclasses import asdict
from importlib.metadata import version
from .common import *
from llm_chat.recoverable_loop.state import state_from_dict,actor_view,fact_view
from llm_chat.recoverable_loop.tools import EvidenceWindow
from llm_chat.recoverable_loop.roles import request


def freeze():
    initials={}
    for path in sorted((BASE/'prefixes').glob('R?_Q*.json')):
        if '.seed_review.' in path.name:continue
        p=read(path);s=state_from_dict(p['state']);reg=p['registry']
        metadata={w['doc_ref']:w for w in reg['windows']}
        handles={'documents':[{'doc_ref':d['doc_ref'],'title':metadata[d['doc_ref']]['title'],'url':metadata[d['doc_ref']]['url']} for d in reg['documents']],
                 'windows':[{'window_ref':w['window_ref'],'doc_ref':w['doc_ref']} for w in reg['windows']]}
        actor=request('actor',actor_view(s,handles));first=None
        if p['family']=='R2':first=actor
        if p['family']=='R3':
            ws={w['window_ref']:w for w in reg['windows']};evidence=[]
            refs=list(dict.fromkeys(r for c in s.C for r in c.evidence_refs))
            for r in refs:
                w=ws[r]
                e={k:w[k] for k in EvidenceWindow.__dataclass_fields__ if k!='text_sha256'}
                e['text_sha256']=hashlib.sha256(w['text'].encode()).hexdigest();evidence.append(e)
            first=request('closure',{**fact_view(s),'Evidence':evidence})
        initials[p['cell_id']]={'actor_hash':actor.request_hash,'actor':asdict(actor),'first_paid_hash':first.request_hash if first else None,
                               'first_paid_request':asdict(first) if first else 'Depends on forced Search real observation; request hash recorded before dispatch.'}
    save(BASE/'INITIAL_REQUESTS.json',initials)
    deps=[]
    for folder in ['llm_chat/recoverable_loop','tests/recoverable_loop_clean','experiments/recoverable_loop_clean/h1_contract_continuation']:
        deps += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.json','.md') and '__pycache__' not in str(p)]
    for p in ['llm_chat/search_find_agent.py','llm_chat/search_find_v3b_agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','llm_chat/agent.py','llm_chat/client.py',
              'experiments/recoverable_loop_clean/micro_recovery/run.py',
              'experiments/recoverable_loop_clean/micro_recovery/prepare.py',
              'experiments/recoverable_loop_clean/micro_recovery/common.py',
              'experiments/recoverable_loop_clean/micro_recovery/transport.py',
              'experiments/recoverable_loop_clean/micro_recovery/external_source/search_bcplus.py',
              'experiments/recoverable_loop_clean/h_fix/NEXT_EXPERIMENT_PLAN.md','experiments/recoverable_loop_clean/h_fix/CALL_ESTIMATE.json','AGENTS.md']:
        deps.append(ROOT/p)
    sources=read(BASE/'PREFIX_PREFLIGHT.json')['sources']
    files={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(deps))}
    files.update(sources)
    binaries=[ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite']+sorted((ROOT/'BCPlus/indexes/qwen3-embedding-8b').glob('*.pkl'))
    binaries+=sorted(Path('/data/model/Qwen3-Embedding-8B').glob('*'))
    meta={str(p):{'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in binaries if p.is_file()}
    save(BASE/'FREEZE.json',{'created_utc':now(),'pre_freeze_head':head(),'files':files,'binary_files':meta,
        'external_source_files':{'BCPlus/scripts/search_bcplus.py':{'sha256':sha(ROOT/'BCPlus/scripts/search_bcplus.py'),'committed_snapshot':'experiments/recoverable_loop_clean/micro_recovery/external_source/search_bcplus.py'}},
        'versions':{p:version(p) for p in ['httpx','torch','transformers','jsonschema','pytest']},
        'config':read(BASE/'CONFIG.json'),'schedule':read(BASE/'SCHEDULE.json'),
        'selection_annotation':'H1 same six historical prefixes, result-informed interface continuation diagnostic, NOT independent confirmation. Selection byte-identical to old cohort; no added cells or replacement.',
        'rubric':'PROTOCOL.md Review rubric frozen; post-run Codex prefix-relative single review, no paid reviewer.',
        'max_retries':0,'horizon':3,'max_requests':192,'max_acquisitions':32,
        'freeze_head_note':'The following commit contains this manifest. Runtime requires HEAD to contain identical committed frozen bytes; all request artifacts archive that execution HEAD.'})

if __name__=='__main__':freeze()
