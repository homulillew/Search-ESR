"""Mechanical archived-prefix conversion; no semantic calls or retrieval queries."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sqlite3
from experiments.recoverable_loop_clean.micro_recovery.prepare import from_audits, restore
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from llm_chat.recoverable_loop.tools import ToolBridge
from llm_chat.recoverable_loop.state import State, Claim, Hypothesis, skeleton, append_event, digest
from llm_chat.recoverable_loop.engine import RecoverableLoop

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent


def read(path): return json.loads(Path(path).read_text())
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f: json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def prepare():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True, padding_side='left')
    selection = read(BASE/'SELECTION_PRECOMMIT.json')
    bank = read(ROOT/'experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json')
    reports = []; packets = []; sources = dict(selection['source_files_sha256'])
    class NoCalls:
        def complete(self, req): raise AssertionError('No model call in prefix preparation')
    for cell in selection['selected_before_semantic_review']:
        mapping = {}; attempts = []; last_search = None
        if cell['source'] == 'acquisition_S01':
            snapshot = read(ROOT/cell['path']); old = snapshot['state']; audits = []
            decision = int(snapshot['transition'].split('_')[1])
            for n in range(1, decision+1):
                path = (ROOT/cell['path']).parent/f'decision{n}_tool.json'
                tool = read(path); sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
                a = tool['action']; action = {'tool': a['tool'], 'arguments': {k: v for k, v in a.items() if k != 'tool'}}
                audits.append((action, tool['audit']))
                if a['tool'] == 'search': last_search = action
            reg, attempts = from_audits(audits)
            q = old['question']; old_claims = old['claims']; hypothesis = old['hypothesis']
            mapping = {w['window_ref']: w['window_ref'] for w in reg['windows']}
        else:
            row = next(r for r in bank if r['checkpoint_id'] == cell['checkpoint_id'])
            old = row['state']; q = row['question']; old_claims = old['verified_claims']; hypothesis = old['working_hypothesis']
            if cell['family'] == 'R2' and not hypothesis:
                reports.append({**cell, 'eligible': False, 'reason': 'No seed H; cannot test weak/wrong-H recovery. No fabricated H or replacement.'})
                continue
            workspace = old['available_workspace']
            tools = OrthogonalSearchFindTools(); tools.window_builder = RawWindowBuilder(tokenizer); b = ToolBridge(tools)
            windows = []; doc_rows = []
            with sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro", uri=True) as db:
                for d in workspace['known_documents']:
                    text, url = db.execute('select text,url from documents where docid=?', (d['docid'],)).fetchone()
                    key = tools.window_builder.register(d['docid'], text, url)
                    assert tools.handles.document(key)[0] == d['doc_ref']
                    doc_rows.append({'doc_ref': d['doc_ref'], 'docid': key[0], 'document_sha256': key[1]})
                for old_w in workspace['observed_windows']:
                    key = tools.handles.resolve_document(old_w['doc_ref']); full = tools.window_builder.documents[key]['text']
                    assert full.count(old_w['text']) == 1, 'Observed prefix must be an exact unambiguous contiguous raw source span'
                    offset = full.index(old_w['text']); raw = tools.window_builder._emit(key, offset, offset+len(old_w['text']))
                    assert raw['title'] == old_w['title'] and raw['url'] == old_w['url'], 'Archived source metadata changed'
                    wr = tools.handles.window(raw['window_ref'])[0]; assert wr == old_w['window_ref']
                    normalized = b._normalize({'tool': 'open', 'raw_result': raw, 'handles': tools.handles.snapshot()})
                    b.evidence.add(normalized)
                    windows.append({**raw, 'source_window_ref': raw['window_ref'], 'window_ref': wr, 'doc_ref': old_w['doc_ref']})
                    mapping[old_w['source_id']] = wr
                    tools.discovery_previews.setdefault(old_w['doc_ref'], wr)
            reg = {'documents': doc_rows, 'windows': windows, 'discovery_previews': tools.discovery_previews}
        claims = tuple(Claim(f'C{i}', c['statement'], tuple(mapping[r] for r in c['support_refs'])) for i, c in enumerate(old_claims, 1))
        hs = (Hypothesis('H1', hypothesis, 'active', ()),) if hypothesis else ()
        s = State(q, skeleton(q, [{'source_spans': [{'text': q}]}]), claims, hs)
        for a in attempts[-3:]: s = append_event(s, 'step_outcome', a)
        s = append_event(s, 'archived_prefix_conversion', {'source': cell['path'], 'source_checkpoint': cell.get('checkpoint_id', 'S01'),
                         'source_to_window_refs': mapping, 'note': 'Deterministic legacy seed conversion before model calls; never H-output repair.'})
        forced = None
        if cell['family'] == 'R1':
            assert last_search is not None
            forced = {'decision': 'acquire', 'focus_requirement_id': 'R1',
                      'one_gap': 'Check the relation expressed by the last observed Search query: '+last_search['arguments']['query'],
                      'strategy': 'LOCATE_SOURCE', 'hypothesis_ids_under_test': [], 'action': last_search}
        elif cell['family'] == 'R3': forced = {'decision': 'request_closure'}
        packet = {**cell, 'state': asdict(s), 'registry': reg, 'forced_first': forced,
                  'provenance': {'original_snapshot': cell['path'], 'checkpoint': cell.get('checkpoint_id', 'S01'),
                                 'skeleton': 'Mechanical whole original Q; no LLM decomposition',
                                 'claims': 'Literal archived statements; prefix-only support review required before live H2.',
                                 'H': 'Literal archived hypothesis, not known-gold false. R2 may be inconclusive without contradiction.',
                                 'reference_conversion': mapping, 'full_source_visible_to_roles': False}}
        packet['prefix_sha256'] = digest({'state': packet['state'], 'registry': reg})
        restored, b = restore(packet, tokenizer); loop = RecoverableLoop(restored, b, NoCalls()); loop.close()
        save(BASE/'prefixes'/(cell['cell_id']+'.json'), packet)
        save(BASE/'review_packets'/(cell['cell_id']+'.json'), {'cell_id': cell['cell_id'], 'Q': q,
             'H': [asdict(h) for h in hs], 'claims': [{'claim': asdict(c), 'Evidence': b.evidence.select(c.evidence_refs)} for c in claims],
             'all_prefix_observations': [asdict(b.evidence.get(w['window_ref'])) for w in reg['windows']],
             'forced_first': forced, 'note': 'Only the chosen prefix; no gold or later trajectory.'})
        reports.append({**cell, 'eligible': True, 'documents': len(reg['documents']), 'windows': len(reg['windows']), 'claims': len(claims),
                        'hypotheses': len(hs), 'mechanical_integrity_verified': True, 'semantic_seed_review': 'pending'})
        packets.append(packet)
    save(BASE/'PREFIX_PREFLIGHT.json', {'sources': sources, 'cells': reports, 'paid_calls': 0, 'live_retrieval_calls': 0})
    save(BASE/'SCHEDULE.json', [{'trajectory_id': p['cell_id']+'__rep1', 'cell_id': p['cell_id'], 'family': p['family'], 'replicate': 1} for p in packets])
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == '__main__': prepare()
