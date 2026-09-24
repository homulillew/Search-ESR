"""Tool Affordance probe (CLAUDE_NEXT.md section 6, "两题都不调用 Find" branch).

Fixed checkpoint replay: take a real api_request moment from a finished v3a
rollout and re-ask "what is your next action?" under two tool descriptions,
without executing any tool.

  A: the frozen v3a SEARCH_FIND_TOOLS, verbatim.
  B: identical except the find/open descriptions carry the strengthened general
     boundary only ("找同文档另一个事实用 Find；当前段落缺上下文才 Open").

A checkpoint qualifies when the model had just received a search result that
re-discovered an already-known D# (the relocation moment find was meant to
absorb) and its actual next action was another global search. Selection is
mechanical (earliest N per run), never hand-picked toward a hoped-for outcome.

This is an independent experiment: it writes only under its own directory and
never modifies the replayed run directories or the frozen v3a protocol.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from llm_chat.search_find_agent import SEARCH_FIND_TOOLS  # noqa: E402
from llm_chat.client import Config  # noqa: E402
from openai import OpenAI  # noqa: E402

PROBE_ROOT = Path(__file__).resolve().parent / 'probe_tool_affordance'

# Variant B: the strengthened general boundary lives in the tool schema itself.
# No question-specific hint, no change to names, order or parameter schemas.
BOUNDARY_FIND = (
    'Locate a specific fact inside one previously discovered D# document using a local lexical query. '
    'Returns an exact raw-text W# window. When you need a fact or wording from a document you have '
    'already discovered, call find instead of running another global search: find moves you to the '
    'exact passage, while search only re-discovers documents you already know. '
    'Use a different find query for another fact in the same document.'
)
BOUNDARY_OPEN = (
    'Read adjacent raw text around an observed W# window. before/after read neighboring text; '
    'around expands the current span. Use open only when a passage you can already see is relevant '
    'but needs adjacent context; when you are looking for a different fact elsewhere in the document, '
    'use find instead.'
)


def variant_b():
    tools = copy.deepcopy(SEARCH_FIND_TOOLS)
    for tool in tools:
        if tool['function']['name'] == 'find':
            tool['function']['description'] = BOUNDARY_FIND
        elif tool['function']['name'] == 'open':
            tool['function']['description'] = BOUNDARY_OPEN
    return tools


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


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
    """api_response immediately follows its api_request; kinds do not share a seq."""
    paired, pending = {}, None
    for e in events:
        if e['kind'] == 'api_request':
            pending = e
        elif e['kind'] == 'api_response' and pending is not None:
            paired[pending['seq']] = e
            pending = None
    return paired


def select_checkpoints(run_dir, max_n):
    """Earliest moments where a search re-discovered a known D# and the model
    then chose another global search. These are exactly the repeated-global-
    search decisions find was supposed to absorb."""
    events = load_events(run_dir)
    responses = pair_responses(events)
    out = []
    for e in events:
        if e['kind'] != 'api_request':
            continue
        msgs = e['request']['messages']
        if msgs[-1].get('role') != 'tool':
            continue
        try:
            payload = json.loads(msgs[-1].get('content', ''))
        except (ValueError, TypeError):
            continue
        if not (isinstance(payload, dict) and 'results' in payload):
            continue
        rediscovered = [r['doc_ref'] for r in payload.get('results', [])
                        if r.get('previously_discovered')]
        if not rediscovered:
            continue
        resp = responses.get(e['seq'])
        if not resp:
            continue
        calls = resp['response']['choices'][0]['message'].get('tool_calls') or []
        names = [c['function']['name'] for c in calls]
        if not names or names[0] != 'search':
            continue
        out.append({'seq': e['seq'], 'rediscovered': rediscovered,
                    'actual_next': names,
                    'request': e['request']})
        if len(out) >= max_n:
            break
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


def run_gate(run_dirs, checkpoints_by_run, variant_a, tools_b, probe_dir):
    print('Offline gate (section 1):')
    g = Gate()
    g.check('probe output dir is outside every replayed run dir',
            all(not str(probe_dir).startswith(str(Path(d).resolve()) + '/')
                and probe_dir.resolve() != Path(d).resolve() for d in run_dirs))
    g.check('at least one checkpoint selected', sum(len(c) for c in checkpoints_by_run.values()) > 0)

    frozen_hash = sha(SEARCH_FIND_TOOLS)
    g.check('variant A is the frozen SEARCH_FIND_TOOLS object verbatim',
            sha(variant_a) == frozen_hash,
            f'probe={sha(variant_a)} module={frozen_hash}')

    # Variant A must match the source recorded in each replayed run's manifest.
    for run_dir in run_dirs:
        manifest = json.load((Path(run_dir) / 'manifest.json').open())
        want = (manifest.get('source_sha256') or {}).get('llm_chat/search_find_agent.py')
        actual = hashlib.sha256((ROOT / 'llm_chat/search_find_agent.py').read_bytes()).hexdigest()
        g.check(f'search_find_agent.py matches {Path(run_dir).name} manifest',
                want == actual, f'manifest={want} current={actual}')

    # Variant B: only the find/open descriptions change.
    names_a = [t['function']['name'] for t in variant_a]
    names_b = [t['function']['name'] for t in tools_b]
    g.check('A and B have the same tool names in the same order', names_a == names_b)
    same_params = all(a['function']['parameters'] == b['function']['parameters']
                      for a, b in zip(variant_a, tools_b))
    g.check('A and B have identical parameter schemas', same_params)
    changed = [a['function']['name'] for a, b in zip(variant_a, tools_b)
               if a['function']['description'] != b['function']['description']]
    g.check('only find and open descriptions differ in B',
            sorted(changed) == ['find', 'open'], f'changed={changed}')
    g.check('search description is untouched in B',
            next(a['function']['description'] for a in variant_a
                 if a['function']['name'] == 'search')
            == next(b['function']['description'] for b in tools_b
                    if b['function']['name'] == 'search'))

    # Each checkpoint is a genuine mid-episode state, not the opening turn.
    for run_dir, checkpoints in checkpoints_by_run.items():
        for cp in checkpoints:
            msgs = cp['request']['messages']
            g.check(f"checkpoint seq={cp['seq']} starts with a system message",
                    msgs and msgs[0].get('role') == 'system')
            g.check(f"checkpoint seq={cp['seq']} ends with a tool observation",
                    msgs and msgs[-1].get('role') == 'tool')
    g.check('every replay uses tool_choice auto (never none)',
            all(cp['request'].get('tool_choice') == 'auto' for cps in checkpoints_by_run.values()
                for cp in cps))
    return g


def replay(client, model, checkpoint, tools, timeout):
    """One API call. No tool is ever executed."""
    recorded = checkpoint['request']
    request = {'model': model, 'messages': copy.deepcopy(recorded['messages']),
               'tools': tools, 'tool_choice': 'auto', 'stream': False}
    # Fidelity: the replay may differ from the recorded request only in tools.
    assert request['model'] == recorded['model']
    assert request['messages'] == recorded['messages']
    assert request['tool_choice'] == recorded['tool_choice']
    assert request['stream'] == recorded['stream']
    start = time.monotonic()
    response = client.chat.completions.create(**request, timeout=timeout)
    elapsed = time.monotonic() - start
    msg = response.choices[0].message
    calls = [{'name': c.function.name, 'arguments': c.function.arguments}
             for c in (msg.tool_calls or [])]
    finish = response.choices[0].finish_reason
    reasoning = (msg.reasoning_content or '')[-1200:]
    usage = response.usage.model_dump() if response.usage else {}
    return {'next_actions': calls, 'finish_reason': finish,
            'reasoning_tail': reasoning, 'usage': usage, 'elapsed_seconds': elapsed}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run-dir', action='append', required=True,
                    help='finished v3a rollout directory (repeatable)')
    ap.add_argument('--max-checkpoints', type=int, default=5,
                    help='earliest relocation-moment checkpoints per run (default 5)')
    ap.add_argument('--samples', type=int, default=1,
                    help='independent samples per (checkpoint, variant) pair (default 1)')
    ap.add_argument('--dry-run', action='store_true',
                    help='run the offline gate and freeze record only; no paid call')
    args = ap.parse_args()

    run_dirs = [Path(d).resolve() for d in args.run_dir]
    for d in run_dirs:
        if not (d / 'events.jsonl').exists():
            raise SystemExit(f'no events.jsonl: {d}')

    config = Config.load()
    variant_a = copy.deepcopy(SEARCH_FIND_TOOLS)
    tools_b = variant_b()
    checkpoints_by_run = {str(d): select_checkpoints(d, args.max_checkpoints) for d in run_dirs}
    total = sum(len(c) for c in checkpoints_by_run.values())
    if total == 0:
        raise SystemExit('no relocation-moment checkpoints found in the given runs')

    probe_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    probe_dir = PROBE_ROOT / probe_id
    probe_dir.mkdir(parents=True, exist_ok=False)

    freeze = {
        'probe': 'tool_affordance',
        'probe_id': probe_id,
        'head': git_head(),
        'model': config.model,
        'base_url_host': config.base_url.split('//')[-1].split('/')[0],
        'timeout': config.timeout,
        'python': sys.version,
        'openai_sdk': __import__('openai').__version__,
        'max_checkpoints_per_run': args.max_checkpoints,
        'samples_per_checkpoint_variant': args.samples,
        'variant_a_tools_sha256': sha(variant_a),
        'variant_b_tools_sha256': sha(tools_b),
        'runs': {str(d): [cp['seq'] for cp in cps]
                 for d, cps in checkpoints_by_run.items()},
    }
    (probe_dir / 'freeze.json').write_text(json.dumps(freeze, ensure_ascii=False, indent=2))

    gate = run_gate(run_dirs, checkpoints_by_run, variant_a, tools_b, probe_dir)
    if not gate.ok():
        (probe_dir / 'gate_failure.txt').write_text('\n'.join(gate.failures) + '\n')
        raise SystemExit(f'offline gate failed: {gate.failures} -- stopping before any paid call')
    if args.dry_run:
        print(f'\nDry run only. Freeze record: {probe_dir / "freeze.json"}')
        return

    # Paid calls begin here. The freeze record above is immutable.
    client = OpenAI(api_key=config.api_key, base_url=config.base_url, max_retries=2)
    log = (probe_dir / 'events.jsonl').open('w', encoding='utf-8')
    seq_counter = [0]

    def emit(kind, **data):
        seq_counter[0] += 1
        event = {'seq': seq_counter[0], 'time': datetime.now(timezone.utc).isoformat(),
                 'kind': kind, **data}
        log.write(json.dumps(event, ensure_ascii=False) + '\n')
        log.flush()

    results = []
    for run_dir, checkpoints in checkpoints_by_run.items():
        for cp in checkpoints:
            emit('checkpoint', run_dir=run_dir, seq=cp['seq'],
                 rediscovered=cp['rediscovered'], actual_next=cp['actual_next'])
            for label, tools in (('A', variant_a), ('B', tools_b)):
                for sample in range(args.samples):
                    outcome = replay(client, config.model, cp, tools, config.timeout)
                    emit('probe_response', run_dir=run_dir, seq=cp['seq'], variant=label,
                         sample=sample, next_actions=outcome['next_actions'],
                         finish_reason=outcome['finish_reason'],
                         usage=outcome['usage'], elapsed_seconds=outcome['elapsed_seconds'])
                    results.append({'run_dir': run_dir, 'seq': cp['seq'], 'variant': label,
                                    'sample': sample, 'rediscovered': cp['rediscovered'],
                                    'actual_next': cp['actual_next'], **outcome})
                    names = [c['name'] for c in outcome['next_actions']] or ['(no tool call)']
                    print(f"  {Path(run_dir).name} seq={cp['seq']:>3} "
                          f"variant={label} sample={sample} -> {names}")

    log.close()
    client.close()
    (probe_dir / 'probe_results.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2))

    print(f'\nProbe complete: {len(results)} replay responses in {probe_dir}')

    # Rates per variant. A single sample cannot separate a variant effect from
    # model sampling noise -- variant A is byte-identical to what the original
    # run sent, yet A replays still diverge from the original, so the model is
    # non-deterministic at these checkpoints.
    from collections import Counter, defaultdict
    by_variant = defaultdict(Counter)
    for r in results:
        names = tuple(c['name'] for c in r['next_actions'])
        key = names[0] if names else '(no tool call)'
        by_variant[r['variant']][key] += 1
    print('\n  first-action rate by variant:')
    for label in ('A', 'B'):
        total = sum(by_variant[label].values())
        parts = ', '.join(f'{k}={v}/{total}' for k, v in sorted(by_variant[label].items()))
        print(f'    {label}: {parts}')

    changed = [r for r in results
               if [c['name'] for c in r['next_actions']] != r['actual_next']]
    print(f'\n  replays whose next action differs from the original run: {len(changed)}/{len(results)}')
    for r in changed:
        got = [c['name'] for c in r['next_actions']] or ['(no tool call)']
        print(f"    seq={r['seq']} variant={r['variant']} sample={r['sample']}: "
              f"{r['actual_next']} -> {got}")


if __name__ == '__main__':
    main()
