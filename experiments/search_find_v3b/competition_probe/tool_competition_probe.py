"""Tool Competition Upper-Bound Probe (v3b Experiment 1).

Pre-registered in HYPOTHESES.md / EXPERIMENT_PLAN.md. Question: is `find` unused
because global `search` dominates the action space (H1), or because the model
lacks the control state to switch from discovery to verification (H2)?

Take the 10 frozen relocation-moment checkpoints from the finished v3a runs,
re-ask "what is your next action?" under three arms, and *never execute a tool*:

  A (as_is)           search+find+open, frozen v3a schema and prompt verbatim.
  B (search_hidden)   find+open only; everything else byte-identical, including
                      the prompt that still describes search. This is the single
                      intervention: search removed from the action space.
  C (local_only)      find+open only (same tools object as B) plus ONE frozen
                      paragraph swap telling the model global discovery is done
                      and this step offers no further global search.

Arm A is NOT re-sampled: the v3a affordance probe already produced 50 A records
under byte-identical conditions (tools sha256 60de1d45...). They are copied in
with provenance; the original probe directory is read-only here.

Independent experiment: writes only under experiments/search_find_v3b/. The
replayed v3a run directories and the frozen v3a protocol are never modified.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from llm_chat.search_find_agent import SEARCH_FIND_TOOLS, SEARCH_FIND_PROMPT  # noqa: E402
from llm_chat.client import Config  # noqa: E402
from openai import OpenAI  # noqa: E402

PROBE_ROOT = Path(__file__).resolve().parent

# Frozen, pre-registered. The search-describing paragraph of SEARCH_FIND_PROMPT
# is replaced verbatim by LOCAL_ONLY_PARAGRAPH in arm C. Nothing else changes.
SEARCH_PARAGRAPH_INDEX = 1
LOCAL_ONLY_PARAGRAPH = (
    'Global document discovery for this question has already been done. '
    'The documents identified by the D# handles in this conversation are the '
    'candidate set, and this step offers no further global search. '
    'Use find and open on the D# / W# material already in the conversation.'
)

# Arm C's added text may not steer the model. Pre-registered forbidden patterns,
# checked mechanically by the gate.
FORBIDDEN_IN_LOCAL_ONLY = [
    'Ding Junhui', 'Judd Trump', 'Neil Robertson', 'Mark Selby',
    'Andrea Pirlo', 'Lionel Messi', 'Selçuk', 'Inan',
    'century', 'break', 'snooker', 'Inter Milan', 'Inter', 'Pirlo',
    'Milan', 'Fenerbah', 'Galatasaray',
    'find(D', 'find (D', 'should find', 'call find', 'next query',
    'docid', 'document_sha256',
]

# Pre-registered interpretation bands, copied verbatim into freeze.json so the
# reading of the outcome is fixed before any paid call.
BANDS = {
    'metric': 'arm C exploratory_find count out of 50, with arm A near 0',
    'strong': '>= 15/50 AND spread over >= 5/10 checkpoints -> H1 holds; go to Experiment 2',
    'medium': '5-14/50 -> go to Experiment 2, keep H2 alive in parallel',
    'weak': '<= 4/50 -> stop attributing to search dominance; go to Experiment 3',
}

# The 10 frozen checkpoints, pre-registered. Mechanical selection rule (v3a
# probe): the earliest api_request per run whose last tool observation re-hits
# an already-discovered D# and whose recorded next action is another search.
FROZEN_CHECKPOINTS = {
    'v003a_search_find/qid_546/20260922T121742.932067Z': [9, 17, 25, 33, 41],
    'v003a_search_find/qid_1094/20260922T113202.256169Z': [23, 34, 45, 53, 61],
}
RUNS = ROOT / 'experiments/runs'

V3A_PROBE_DIR = ROOT / 'experiments/search_find_v3a/probe_tool_affordance/20260922T141730.317105Z'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha_bytes(Path(path).read_bytes())


def git_head():
    try:
        return subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'unavailable'


def load_events(run_dir):
    with (Path(run_dir) / 'events.jsonl').open() as f:
        return [json.loads(line) for line in f]


def pair_responses(events):
    """api_response immediately follows its api_request; shared seq namespace."""
    paired, pending = {}, None
    for e in events:
        if e['kind'] == 'api_request':
            pending = e
        elif e['kind'] == 'api_response' and pending is not None:
            paired[pending['seq']] = e
            pending = None
    return paired


def arm_b_tools():
    """Search removed, original order preserved, find/open untouched."""
    return [copy.deepcopy(t) for t in SEARCH_FIND_TOOLS
            if t['function']['name'] != 'search']


def arm_c_prompt():
    paras = SEARCH_FIND_PROMPT.split('\n\n')
    assert paras[SEARCH_PARAGRAPH_INDEX].startswith('search(query)'), \
        'frozen prompt structure changed: paragraph 1 is no longer the search one'
    paras = list(paras)
    paras[SEARCH_PARAGRAPH_INDEX] = LOCAL_ONLY_PARAGRAPH
    return '\n\n'.join(paras)


def load_checkpoints(run_dir, seqs):
    """Deep-copy the recorded api_request for each frozen seq. No rebuilding."""
    events = load_events(run_dir)
    requests = {e['seq']: e for e in events if e['kind'] == 'api_request'}
    responses = pair_responses(events)
    out = []
    for seq in seqs:
        if seq not in requests:
            raise SystemExit(f'checkpoint seq={seq} missing in {run_dir}')
        req = copy.deepcopy(requests[seq]['request'])
        resp = responses.get(seq)
        if resp is None:
            raise SystemExit(f'no api_response pairs with seq={seq} in {run_dir}')
        calls = resp['response']['choices'][0]['message'].get('tool_calls') or []
        names = [c['function']['name'] for c in calls]
        msgs = req['messages']
        rediscovered = []
        last = msgs[-1]
        if last.get('role') == 'tool':
            try:
                payload = json.loads(last.get('content', ''))
            except (ValueError, TypeError):
                payload = None
            if isinstance(payload, dict):
                rediscovered = [r['doc_ref'] for r in payload.get('results', [])
                                if r.get('previously_discovered')]
        out.append({'seq': seq, 'request': req, 'actual_next': names,
                    'last_role': msgs[-1].get('role'), 'rediscovered': rediscovered})
    return out


class Gate:
    def __init__(self):
        self.failures = []

    def check(self, name, condition, detail=''):
        status = 'PASS' if condition else 'FAIL'
        print(f'  [{status}] {name}' + (f' -- {detail}' if detail and not condition else ''))
        if not condition:
            self.failures.append(name)

    def ok(self):
        return not self.failures


def run_gate(ctx):
    print('Offline gate (pre-registered, EXPERIMENT_PLAN.md stage 1):')
    g = Gate()
    checks = ctx['checkpoints_by_run']
    probe_dir, run_dirs = ctx['probe_dir'], ctx['run_dirs']
    a_tools, b_tools = ctx['a_tools'], ctx['b_tools']
    c_prompt = ctx['c_prompt']

    # 1. Output isolation.
    g.check('probe output dir is outside every replayed run dir',
            all(not str(probe_dir).startswith(str(Path(d).resolve()) + '/')
                and probe_dir.resolve() != Path(d).resolve() for d in run_dirs))
    g.check('probe output dir is outside the v3a probe dir',
            not str(probe_dir).startswith(str(V3A_PROBE_DIR) + '/'))

    # 2. Checkpoint identity with the frozen list.
    got = {Path(d).name + '/' + str(s): True
           for d, cps in checks.items() for s in [c['seq'] for c in cps]}
    want = {Path(d).name + '/' + str(s): True for d, ss in FROZEN_CHECKPOINTS.items() for s in ss}
    g.check('checkpoint seqs match the frozen pre-registered list exactly',
            sorted(got) == sorted(want), f'got={sorted(got)} want={sorted(want)}')
    g.check('exactly 10 checkpoints (2 runs x 5)', sum(len(c) for c in checks.values()) == 10)

    # 3. The qualifying condition still holds at every checkpoint.
    for run_dir, cps in checks.items():
        for cp in cps:
            g.check(f"{Path(run_dir).name} seq={cp['seq']} ends with a tool observation",
                    cp['last_role'] == 'tool')
            g.check(f"{Path(run_dir).name} seq={cp['seq']} recorded next action starts with search",
                    bool(cp['actual_next']) and cp['actual_next'][0] == 'search')

    # 4. Arm A is the frozen schema verbatim.
    frozen_tools = sha(SEARCH_FIND_TOOLS)
    g.check('arm A tools == frozen SEARCH_FIND_TOOLS (sha 60de1d45...)',
            sha(a_tools) == frozen_tools, f'arm_a={sha(a_tools)} frozen={frozen_tools}')
    g.check('arm A tool order is search, find, open',
            [t['function']['name'] for t in a_tools] == ['search', 'find', 'open'])

    # 5. Arm B is pure subtraction: same order minus search, find/open untouched.
    g.check('arm B tools are find, open in original order',
            [t['function']['name'] for t in b_tools] == ['find', 'open'])
    g.check('arm B find/open schemas+descriptions are byte-identical to arm A',
            [t for t in a_tools if t['function']['name'] != 'search'] == b_tools)

    # 6. Arm C shares the tools object with B; only ONE prompt paragraph differs.
    g.check('arm C prompt differs from the frozen prompt (arm B keeps it verbatim)',
            c_prompt != SEARCH_FIND_PROMPT)
    c_paras, a_paras = c_prompt.split('\n\n'), SEARCH_FIND_PROMPT.split('\n\n')
    g.check('arm C has the same paragraph count as the frozen prompt',
            len(c_paras) == len(a_paras), f'c={len(c_paras)} a={len(a_paras)}')
    diff = [i for i, (x, y) in enumerate(zip(a_paras, c_paras)) if x != y]
    g.check('arm C differs from the frozen prompt in exactly one paragraph',
            diff == [SEARCH_PARAGRAPH_INDEX], f'diff_idx={diff}')
    g.check('the differing paragraph was the search-describing one',
            a_paras[SEARCH_PARAGRAPH_INDEX].startswith('search(query)'))
    for other in (0, 2, 3, 4):
        g.check(f'arm C keeps frozen prompt paragraph {other} byte-identical',
                a_paras[other] == c_paras[other])

    # 7. Arm C's added text steers nothing.
    hits = [p for p in FORBIDDEN_IN_LOCAL_ONLY if p.lower() in LOCAL_ONLY_PARAGRAPH.lower()]
    g.check('arm C added text contains no entity / gold / docid / query hint',
            not hits, f'forbidden hits={hits}')

    # 8. Request fidelity: messages, model, stream, tool_choice preserved.
    for run_dir, cps in checks.items():
        for cp in cps:
            r = cp['request']
            g.check(f"{Path(run_dir).name} seq={cp['seq']} tool_choice is auto",
                    r.get('tool_choice') == 'auto')
            g.check(f"{Path(run_dir).name} seq={cp['seq']} has no temperature override",
                    'temperature' not in r, 'temperature present in recorded request')
            g.check(f"{Path(run_dir).name} seq={cp['seq']} has no max_tokens override",
                    'max_tokens' not in r, 'max_tokens present in recorded request')
            blob = json.dumps(r['messages'], ensure_ascii=False)
            # Gold may legitimately appear inside tool observations (corpus
            # text); it must never appear in harness-authored messages.
            authored = json.dumps([m for m in r['messages']
                                   if m.get('role') in ('system', 'user')],
                                  ensure_ascii=False)
            gold = 'Ding Junhui' if 'qid_546' in str(run_dir) else 'Andrea Pirlo'
            g.check(f"{Path(run_dir).name} seq={cp['seq']} gold entity absent from "
                    f"system+user messages ({gold})", gold not in authored)
            g.check(f"{Path(run_dir).name} seq={cp['seq']} messages contain no docid",
                    'docid' not in blob)
            g.check(f"{Path(run_dir).name} seq={cp['seq']} messages contain no document_sha256",
                    'document_sha256' not in blob)

    # 9. The replayed runs were produced by the current frozen v3a protocol.
    for run_dir in run_dirs:
        manifest = json.load((Path(run_dir) / 'manifest.json').open())
        for rel, want in (manifest.get('source_sha256') or {}).items():
            path = ROOT / rel
            g.check(f'{rel} matches {Path(run_dir).name} manifest',
                    path.exists() and file_sha(path) == want,
                    f'manifest={want} current={file_sha(path) if path.exists() else "MISSING"}')
        g.check(f'{Path(run_dir).name} was a search_find_v3a rollout',
                manifest.get('agent_protocol') == 'search_find_v3a')

    # 10. Reused arm A samples: right cells, right tools, originals untouched.
    reused = ctx['reused_a']
    g.check('reused arm A records exist (50)', len(reused) == 50,
            f'got {len(reused)}')
    cells = Counter((Path(r['run_dir']).name, r['seq']) for r in reused)
    expect = {(Path(d).resolve().name, s): 5
              for d, ss in FROZEN_CHECKPOINTS.items() for s in ss}
    g.check('reused arm A covers exactly the 10 frozen cells x 5 samples',
            dict(cells) == expect, f'got={dict(cells)}')
    g.check('all reused arm A records are variant A',
            all(r['variant'] == 'A' for r in reused))
    g.check('all reused arm A records carry a reasoning tail',
            all(bool(r.get('reasoning_tail')) for r in reused))
    g.check('reused arm A came from the recorded v3a probe file',
            sha_bytes(json.dumps(reused, ensure_ascii=False, sort_keys=True).encode())
            == ctx['reused_a_sha_at_freeze'])

    # 11. Gold is not consulted. Recorded before the probe starts.
    g.check('gold answer files are absent from the probe workspace',
            not (probe_dir / 'gold').exists())
    return g


class NoToolExecutionClient:
    """Structural guarantee: the probe may only call chat.completions.create."""

    def __init__(self, inner):
        self._inner = inner
        self.calls = []

    def __getattr__(self, name):
        if name != 'chat':
            raise AssertionError(f'probe must not touch client.{name}')
        return _OnlyChat(self._inner.chat, self.calls)

    def close(self):
        self._inner.close()


class _OnlyChat:
    def __init__(self, chat, calls):
        self._chat = chat
        self._calls = calls

    @property
    def completions(self):
        return _OnlyCreate(self._chat.completions, self._calls)


class _OnlyCreate:
    def __init__(self, completions, calls):
        self._completions = completions
        self._calls = calls

    def create(self, **kwargs):
        # `timeout` is a client-side transport option, not a sampling knob.
        assert set(kwargs) == {'model', 'messages', 'tools', 'tool_choice',
                               'stream', 'timeout'}, \
            f'replay request fields drifted: {sorted(kwargs)}'
        assert kwargs['tool_choice'] == 'auto', 'tool_choice must never be forced'
        assert 'temperature' not in kwargs and 'max_tokens' not in kwargs, \
            'replay must keep provider-default sampling like the original run'
        self._calls.append(kwargs)
        return self._completions.create(**kwargs)


def classify(calls, finish):
    """First-action label, pre-registered. `calls` is the recorded list of
    tool-call dicts (name/arguments). Free-text search attempts are evidenced
    by reasoning_tail / answer_head and scored in SCORING.md, never by a
    heuristic here."""
    if calls:
        name = calls[0]['name']
        if name == 'search':
            return 'search'          # a real search call: only possible in arm A
        if name in ('find', 'open'):
            return name
        return 'other'               # e.g. a made-up tool name
    if finish in ('stop', 'length'):
        return 'answer-stop'         # length = truncated while answering
    return 'invalid'                 # provider signals tool_calls but none present


def replay(guarded, model, checkpoint, tools, timeout, system_override=None):
    """One API call. No tool is ever executed."""
    recorded = checkpoint['request']
    messages = copy.deepcopy(recorded['messages'])
    if system_override is not None:
        assert messages and messages[0].get('role') == 'system'
        messages[0] = {'role': 'system', 'content': system_override}
    request = {'model': model, 'messages': messages, 'tools': tools,
               'tool_choice': 'auto', 'stream': False}
    # Fidelity: the replay may differ from the recorded request only in tools
    # (arms B/C) and, for arm C only, the first (system) message.
    assert request['model'] == recorded['model']
    assert request['tool_choice'] == recorded['tool_choice']
    assert request['stream'] == recorded['stream']
    if system_override is None:
        assert request['messages'] == recorded['messages']
    else:
        assert request['messages'][1:] == recorded['messages'][1:]
    start = time.monotonic()
    response = guarded.chat.completions.create(**request, timeout=timeout)
    elapsed = time.monotonic() - start
    msg = response.choices[0].message
    calls = [{'name': c.function.name, 'arguments': c.function.arguments}
             for c in (msg.tool_calls or [])]
    finish = response.choices[0].finish_reason
    reasoning = (getattr(msg, 'reasoning_content', None) or '')
    answer_text = (msg.content or '')
    usage = response.usage.model_dump() if response.usage else {}
    return {'next_actions': calls, 'finish_reason': finish,
            'reasoning_tail': reasoning[-1600:],
            'answer_head': answer_text[:400],
            'usage': usage, 'elapsed_seconds': elapsed}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--samples', type=int, default=5,
                    help='independent samples per (checkpoint, arm) for arms B/C (default 5)')
    ap.add_argument('--dry-run', action='store_true',
                    help='run the offline gate and freeze record only; no paid call')
    args = ap.parse_args()

    run_dirs = [RUNS / p for p in FROZEN_CHECKPOINTS]
    for d in run_dirs:
        if not (d / 'events.jsonl').exists():
            raise SystemExit(f'no events.jsonl: {d}')

    config = Config.load()
    a_tools = copy.deepcopy(SEARCH_FIND_TOOLS)
    b_tools = arm_b_tools()
    c_prompt = arm_c_prompt()

    checkpoints_by_run = {str(d): load_checkpoints(d, FROZEN_CHECKPOINTS[rel])
                          for d, rel in ((RUNS / p, p) for p in FROZEN_CHECKPOINTS)}

    # Arm A: reuse the v3a affordance probe's 50 records (byte-identical
    # conditions). Copied in with provenance; the source file is read-only.
    v3a_results_path = V3A_PROBE_DIR / 'probe_results.json'
    if not v3a_results_path.exists():
        raise SystemExit(f'missing arm A source: {v3a_results_path}')
    v3a_records = json.loads(v3a_results_path.read_text())
    reused_a = [copy.deepcopy(r) for r in v3a_records if r['variant'] == 'A']
    for r in reused_a:
        r['reused_from_probe_id'] = V3A_PROBE_DIR.name
    reused_a_sha = sha_bytes(
        json.dumps(reused_a, ensure_ascii=False, sort_keys=True).encode())

    probe_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    probe_dir = PROBE_ROOT / probe_id
    probe_dir.mkdir(parents=True, exist_ok=False)

    freeze = {
        'probe': 'tool_competition_upper_bound',
        'probe_id': probe_id,
        'head': git_head(),
        'model': config.model,
        'base_url_host': config.base_url.split('//')[-1].split('/')[0],
        'timeout': config.timeout,
        'python': sys.version,
        'openai_sdk': __import__('openai').__version__,
        'arm_a_tools_sha256': sha(a_tools),
        'arm_b_tools_sha256': sha(b_tools),
        'arm_c_tools_sha256': sha(b_tools),
        'arm_a_prompt_sha256': sha(SEARCH_FIND_PROMPT),
        'arm_b_prompt_sha256': sha(SEARCH_FIND_PROMPT),
        'arm_c_prompt_sha256': sha(c_prompt),
        'arm_c_local_only_paragraph': LOCAL_ONLY_PARAGRAPH,
        'arm_c_replaced_paragraph_sha256': sha(SEARCH_FIND_PROMPT.split('\n\n')[SEARCH_PARAGRAPH_INDEX]),
        'samples_per_checkpoint_arm': args.samples,
        'arm_a_source': 'reused from v3a probe 20260922T141730.317105Z (not re-sampled)',
        'arm_a_records': len(reused_a),
        'arm_a_records_sha256': reused_a_sha,
        'checkpoints': {str(d): [c['seq'] for c in cps]
                        for d, cps in checkpoints_by_run.items()},
        'no_tool_executed': True,
        'tool_choice': 'auto',
        'sampling': 'provider default (recorded requests carry no temperature/max_tokens)',
        'interpretation_bands': BANDS,
        'find_subdivision': {
            'exploratory_find': 'candidate or constraint not yet settled at call time; find tests, compares, or locates something not pinned',
            'confirmation_find': 'answer already locked when find is called; find only confirms the prior',
        },
    }
    (probe_dir / 'freeze.json').write_text(json.dumps(freeze, ensure_ascii=False, indent=2))

    ctx = {'probe_dir': probe_dir, 'run_dirs': run_dirs,
           'checkpoints_by_run': checkpoints_by_run,
           'a_tools': a_tools, 'b_tools': b_tools, 'c_prompt': c_prompt,
           'reused_a': reused_a, 'reused_a_sha_at_freeze': reused_a_sha}
    gate = run_gate(ctx)
    (probe_dir / 'gate.txt').write_text(
        f'offline gate {"PASSED" if gate.ok() else "FAILED"}\nfailures: {gate.failures}\n')
    if not gate.ok():
        raise SystemExit(f'offline gate failed: {gate.failures} -- stopping before any paid call')
    if args.dry_run:
        print(f'\nDry run only. Freeze record: {probe_dir / "freeze.json"}')
        return

    # Paid calls begin here. freeze.json above is immutable.
    client = NoToolExecutionClient(OpenAI(api_key=config.api_key,
                                          base_url=config.base_url, max_retries=2))
    log = (probe_dir / 'events.jsonl').open('w', encoding='utf-8')
    seq_counter = [0]

    def emit(kind, **data):
        seq_counter[0] += 1
        log.write(json.dumps({'seq': seq_counter[0],
                              'time': datetime.now(timezone.utc).isoformat(),
                              'kind': kind, **data}, ensure_ascii=False) + '\n')
        log.flush()

    results = []
    for run_dir, checkpoints in checkpoints_by_run.items():
        for cp in checkpoints:
            emit('checkpoint', run_dir=run_dir, seq=cp['seq'],
                 rediscovered=cp['rediscovered'], actual_next=cp['actual_next'])
            for label, tools, system_override in (
                    ('B', b_tools, None), ('C', b_tools, c_prompt)):
                for sample in range(args.samples):
                    outcome = replay(client, config.model, cp, tools, config.timeout,
                                     system_override)
                    names = [c['name'] for c in outcome['next_actions']]
                    first = classify(outcome['next_actions'], outcome['finish_reason'])
                    emit('probe_response', run_dir=run_dir, seq=cp['seq'], arm=label,
                         sample=sample, next_actions=outcome['next_actions'],
                         finish_reason=outcome['finish_reason'], label=first,
                         usage=outcome['usage'], elapsed_seconds=outcome['elapsed_seconds'])
                    results.append({'run_dir': run_dir, 'seq': cp['seq'], 'arm': label,
                                    'sample': sample, 'actual_next': cp['actual_next'],
                                    'label': first, 'next_actions': outcome['next_actions'],
                                    'finish_reason': outcome['finish_reason'],
                                    'reasoning_tail': outcome['reasoning_tail'],
                                    'answer_head': outcome['answer_head'],
                                    'usage': outcome['usage'],
                                    'elapsed_seconds': outcome['elapsed_seconds']})
                    shown = names or ['(no tool call)']
                    print(f"  {Path(run_dir).name} seq={cp['seq']:>3} arm={label} "
                          f"sample={sample} -> {shown} [{first}]")

    log.close()
    client.close()
    assert all(c['tools'] == b_tools for c in client.calls), 'arm C leaked search?'
    assert not any(t['function']['name'] == 'search' for c in client.calls
                   for t in c['tools']), 'a replay exposed the search tool to arms B/C'
    assert all(sorted(c) == ['messages', 'model', 'stream', 'timeout', 'tool_choice', 'tools']
               for c in client.calls), 'a replay request drifted from the frozen fields'
    print(f'\nReplays sent: {len(client.calls)}. No tool was executed.')

    # Arm A is attached from the immutable copy, not re-scored live.
    (probe_dir / 'probe_results.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2))
    (probe_dir / 'arm_a_reused_from_v3a_probe.json').write_text(
        json.dumps(reused_a, ensure_ascii=False, indent=2))

    print('\n  first-action rate by arm:')
    by_arm = defaultdict(Counter)
    for r in results:
        by_arm[r['arm']][r['label']] += 1
    for label in ('B', 'C'):
        total = sum(by_arm[label].values())
        parts = ', '.join(f'{k}={v}/{total}' for k, v in sorted(by_arm[label].items()))
        print(f'    {label}: {parts}')

    finds = [r for r in results if r['label'] == 'find']
    print(f'\n  find occurrences in new arms: {len(finds)}')
    for r in finds:
        q = r['next_actions'][0].get('arguments') if r['next_actions'] else ''
        print(f"    arm={r['arm']} seq={r['seq']} sample={r['sample']} query={q}")


if __name__ == '__main__':
    main()
