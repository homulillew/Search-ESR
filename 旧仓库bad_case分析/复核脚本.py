"""Read-only archive audit plus synthetic probes; never calls remote model/retrieval APIs.
Usage: python 复核脚本.py /path/to/ESR-GRPO-Code-L
"""
import collections
import inspect
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo / 'src'))
from esr_grpo.environment import ESREnvironment, IllegalActionError
from esr_grpo.models import RetrievedDocument, SearchHit, VerificationResult, VerificationStatus
from esr_grpo.retrieval import InMemoryRetriever
from esr_grpo.verification import KeywordVerifier, OpenAICompatibleVerifier
from esr_grpo.rollout import AgentRunner, OPENAI_TOOLS, BASELINE_TOOLS

report = {'commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(), 'batches': {}, 'probes': {}}
for directory in sorted((repo / 'results/exp1').iterdir()):
    if not directory.is_dir():
        continue
    entries = []
    empty = []
    for path in sorted((directory / 'stores').glob('*.sqlite')):
        with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='actions'").fetchone():
                empty.append(path.name)
                continue
            actions = [json.loads(r[0]) for r in db.execute('SELECT payload_json FROM actions ORDER BY sequence_index')]
            metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value_json FROM metadata')}
            states = [json.loads(r[0]) for r in db.execute('SELECT payload_json FROM task_states ORDER BY version')]
        counts = collections.Counter(a['kind'] for a in actions)
        illegal = collections.Counter(a['kind'] for a in actions if not a['legal'])
        entries.append({'qid': path.stem, 'submitted': bool(metadata.get('submit_action_id')),
                        'actions': len(actions), 'counts': dict(counts), 'illegal': dict(illegal),
                        'ever_supported': any(s['verification_status'] == 'supported' for s in states),
                        'parse_failures': sum('unparseable' in str(a.get('metadata', {})) for a in actions),
                        'final_gap_count': len(states[-1]['gaps']) if states else None})
    totals = collections.Counter()
    illegal = collections.Counter()
    for row in entries:
        totals.update(row['counts']); illegal.update(row['illegal'])
    report['batches'][directory.name] = {
        'runs_files': len(list((directory/'runs').glob('*.json'))), 'valid_stores': len(entries),
        'empty_stores': empty, 'submitted': sum(r['submitted'] for r in entries),
        'zero_open_attempts': sum(not r['counts'].get('open_page') for r in entries),
        'unsubmitted_with_verify_attempt': sum(not r['submitted'] and bool(r['counts'].get('verify_answer')) for r in entries),
        'supported_but_unsubmitted': [r['qid'] for r in entries if r['ever_supported'] and not r['submitted']],
        'action_counts': dict(totals), 'illegal_counts': dict(illegal),
        'parse_failures': sum(r['parse_failures'] for r in entries),
        'parse_failure_episodes': sum(r['parse_failures'] > 0 for r in entries), 'episodes': entries}

def make_env():
    return ESREnvironment('Who built Orion?', InMemoryRetriever.from_documents([
        RetrievedDocument('d1', 'Vector built Orion.')]), KeywordVerifier(('Vector',)))

def acquire(env, query='Vector'):
    s = env.search(query)
    return env.open_page('d1', search_action_id=s['action_id'])

p = report['probes']
schema = next(t for t in OPENAI_TOOLS if t['function']['name'] == 'read_evidence')
p['schema_has_offset_implementation_does_not'] = 'offset' in schema['function']['parameters']['properties'] and 'offset' not in inspect.signature(ESREnvironment.read_evidence).parameters

e = make_env(); page = acquire(e)
try:
    e.read_evidence(page['evidence_id'])
except IllegalActionError as exc:
    p['baseline_read_after_open_rejected'] = str(exc)
e.store.close()

# Same immutable document reopened by a different query changes displayed content,
# while verification reconstructs the first query's view.
class QueryRetriever:
    def search(self, query, top_k=5):
        return [SearchHit('d1', 'alpha beta')]
    def get_document(self, docid):
        return RetrievedDocument('d1', 'alpha fact; beta fact')
    def get_doc_chunks(self, docid, query, topk=3):
        return {'chunks': [{'chunk_index': 0 if query == 'alpha' else 1, 'score': 1, 'text': query + ' fact'}]}
class Recorder:
    def verify(self, question, answer, evidence):
        self.text = evidence[0].content
        return VerificationResult(VerificationStatus.SUPPORTED, (), 'synthetic probe')
v = Recorder(); e = ESREnvironment('Question', QueryRetriever(), v)
a = acquire(e, 'alpha'); b = acquire(e, 'beta')
e.update_state('beta', [{'evidence_id': b['evidence_id'], 'finding': 'beta fact'}], [b['evidence_id']])
e.verify_answer()
p['duplicate_open_view_mismatch'] = {'same_id': a['evidence_id'] == b['evidence_id'], 'last_open': b['content'], 'verifier': v.text, 'mismatch': b['content'] != v.text}
e.store.close()

v = OpenAICompatibleVerifier('https://unused.invalid', 'unused')
v._post = lambda *a: {'choices': [{'message': {'content': 'not json'}}]}
r = v.verify('Q', 'A', [])
p['parse_error_becomes_semantic_repair'] = {'status': r.status.value, 'gap': r.gaps[0]}

e = make_env(); acquire(e)
e.update_state('Vector', [{'evidence_id': 'e1', 'finding': 'Vector built Orion'}], ['e1'])
e.verify_answer()
p['supported_does_not_auto_submit'] = not e.is_submitted
e.update_state('Vector', [], ['e1'])
p['unchanged_update_resets_verification'] = e.current_state.verification_status.value
e.store.close()

# Tool dispatch has no ESR allowlist, even though finish is not in OPENAI_TOOLS.
e = make_env(); e.execute_tool('finish', {'answer': 'synthetic unverified answer'})
p['esr_dispatch_accepts_finish_without_verification'] = e.is_submitted
e.store.close()

# Compaction can retain tool results whose assistant tool_calls were dropped.
e = make_env(); runner = AgentRunner(e, None, compact_message_chars=1)
messages = [{'role': 'system', 'content': 's'}, {'role': 'user', 'content': 'q'},
            {'role': 'assistant', 'tool_calls': [{'id': 'c1'}, {'id': 'c2'}]},
            {'role': 'tool', 'tool_call_id': 'c1', 'content': 'x'},
            {'role': 'tool', 'tool_call_id': 'c2', 'content': 'y'},
            {'role': 'assistant', 'tool_calls': [{'id': 'c3'}]},
            {'role': 'tool', 'tool_call_id': 'c3', 'content': 'z'},
            {'role': 'user', 'content': 'guidance'}]
runner._maybe_compact(messages, 3)
ids = {c['id'] for m in messages for c in m.get('tool_calls', [])}
p['compaction_orphan_tool_results'] = [m['tool_call_id'] for m in messages if m['role'] == 'tool' and m['tool_call_id'] not in ids]
e.store.close()

# Verify the replay script's actual verifier input using a disposable episode.
import importlib.util
import tempfile
spec = importlib.util.spec_from_file_location('old_replay', repo / 'analysis-L/replay_shortboardA.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
with tempfile.TemporaryDirectory() as tmp:
    store_path = str(Path(tmp) / 'probe.sqlite')
    e = ESREnvironment('Question', QueryRetriever(), KeywordVerifier(), store_path=store_path)
    acquire(e, 'alpha')
    e.update_state('alpha', [{'evidence_id': 'e1', 'finding': 'alpha fact'}], ['e1'])
    e.store.close()
    recorder = Recorder()
    replay_result = replay.replay_case(('synthetic', 'alpha', store_path), QueryRetriever(), recorder)
    p['replay_logs_chunks_but_verifies_full_document'] = {
        'logged_view': replay_result['view_evidence'][0]['content'],
        'actual_verifier_input': recorder.text,
        'mismatch': replay_result['view_evidence'][0]['content'] != recorder.text,
    }

report['selected_traces'] = {}
trace_paths = [repo / 'results/exp1/exp100_merged_esr/stores' / f'{q}.sqlite' for q in ['120', '186', '324', '170', '1044']]
trace_paths += [repo / 'results/exp1/esr_retry20_v2_g1/stores' / f'{q}.sqlite' for q in ['416', '533']]
trace_paths += list((repo / 'analysis-L').glob('drive_*/*.sqlite')) + [repo / 'analysis-L/q120_e2.db']
for trace_path in trace_paths:
    with sqlite3.connect(trace_path.as_uri() + '?mode=ro', uri=True) as db:
        actions = [json.loads(r[0]) for r in db.execute('SELECT payload_json FROM actions ORDER BY sequence_index')]
        md = {k: json.loads(v) for k,v in db.execute('SELECT key,value_json FROM metadata')}
        report['selected_traces'][str(trace_path.relative_to(repo))] = {
            'actions': len(actions), 'submitted': bool(md.get('submit_action_id')),
            'verifications': [{'sequence_index': a['sequence_index'], 'legal': a['legal'], 'metadata': a['metadata']} for a in actions if a['kind'] == 'verify_answer']}
        if str(trace_path.relative_to(repo)) == 'results/exp1/exp100_merged_esr/stores/120.sqlite':
            for row in db.execute('SELECT payload_json FROM evidence'):
                ev = json.loads(row[0])
                if ev['source']['docid'] == '37015':
                    needle_text = 'Why would any graduate want to start a business in Nigeria?'
                    report['qid120_observation'] = {'docid': '37015', 'document_characters': len(ev['content']),
                        'answer_character_offset': ev['content'].find(needle_text), 'answer_in_head_16000': needle_text in ev['content'][:16000]}

path = Path(__file__).with_name('复核结果.json')
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'commit': report['commit'], 'probes': p}, ensure_ascii=False, indent=2))
print('Wrote', path)
