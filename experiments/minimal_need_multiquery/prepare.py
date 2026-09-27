"""Offline-only builder. No API, credentials, retriever, or gold access."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OLD = ROOT / 'experiments/belief_need_budget_locality_repair'
BASE = '05d2eeec297c06ce7fa8d2cdd40bc7acb676b88c'
ARMS = {'B0': 'b0.txt', 'B1': 'b1_premise.txt', 'B2': 'b2_coherent.txt', 'B3': 'b3_combined.txt'}
PREMISE = '''Do not treat an unverified identity, event, relationship, or candidate-specific fact as a premise of the next question.

If an attribute question would require assuming an unverified event or relation first, investigate whether that event or relation holds before asking for its attribute.

The Working Hypothesis may identify what to test, but it cannot supply a fact.'''
COHERENCE = '''Choose one coherent unresolved research objective.

The objective may require several complementary retrieval queries if they all serve the same research judgment.

Do not bundle independent research objectives that could be resolved separately.'''

def read(path):
    return json.loads(Path(path).read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def relative(path):
    return str(Path(path).relative_to(ROOT))

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        if isinstance(value, str):
            f.write(value)
        else:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def historical_inventory():
    paths = subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', BASE, '--', 'experiments', '全链路排查报告', 'llm_chat'], cwd=ROOT).decode().split('\0')
    return {name: sha(ROOT / name) for name in paths if name and (ROOT / name).is_file()}

def exposure_inventory():
    """Conservative mechanical exclusion, not a completeness certificate."""
    found = {}
    scanned = 0
    failures = []
    def add(qid, path):
        if isinstance(qid, (int, str)) and not isinstance(qid, bool) and str(qid).isdigit():
            found.setdefault(str(int(qid)), set()).add(path)
    def walk(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if k.lower() in ('qid', 'question_id'):
                    add(v, path)
                elif k.lower() in ('qids', 'excluded_qids', 'selected_qids', 'question_ids') and isinstance(v, list):
                    for q in v:
                        add(q, path)
                walk(v, path)
        elif isinstance(x, list):
            for item in x:
                walk(item, path)
    names = subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', BASE, '--', 'experiments'], cwd=ROOT).decode().split('\0')
    for name in names:
        if not name:
            continue
        for q in re.findall(r'(?:qid[_/-]|qid=)(\d+)', name):
            add(q, name)
        if not name.endswith(('.json', '.jsonl')):
            continue
        scanned += 1
        try:
            with (ROOT / name).open() as f:
                if name.endswith('.jsonl'):
                    for line in f:
                        if line.strip():
                            walk(json.loads(line), name)
                else:
                    walk(json.load(f), name)
        except (ValueError, UnicodeError) as exc:
            failures.append({'path': name, 'error_type': type(exc).__name__})
    return {'base': BASE, 'status': 'CONSERVATIVE_EXCLUSION_NOT_FRESH_BANK', 'scanned_files': scanned,
            'parse_failures': failures, 'excluded_qids': sorted(found, key=int),
            'sources': {q: sorted(paths) for q, paths in sorted(found.items(), key=lambda x: int(x[0]))},
            'limitations': ['Qids encoded only in free prose/key names or untracked materials may be missed.',
                            'Refresh and manually audit at future acquisition/fresh freeze; no qid is certified fresh here.']}

def build():
    write(P / 'analysis/HISTORICAL_HASHES.json', historical_inventory())
    bank = read(OLD / 'bank/CONFIRMATION.json')
    review = read(OLD / 'need/confirmation/REVIEW.json')
    old_jobs = {j['input_id']: j for j in read(OLD / 'need/confirmation/JOBS.json')}
    records = {x['state_id']: x for x in bank}
    bad = [x for x in bank if set(review['B5__' + x['state_id']]['codes']) & {'P', 'A', 'W'}]
    assert len(bad) == 10
    controls = []
    seen_qids = set()
    for row in sorted(bank, key=lambda r: (int(r['qid']), r['state_id'])):
        if not review['B5__' + row['state_id']]['codes'] and row['qid'] not in seen_qids:
            controls.append(row)
            seen_qids.add(row['qid'])
    assert len(controls) >= 8
    selected = sorted(bad + controls[:8], key=lambda r: r['state_id'])
    write(P / 'e1_need/SELECTION.json', {
        'rule': 'All ten primary P/A/W states, then eight strict-valid controls: one per qid, earliest state, ascending numeric qid.',
        'source': relative(OLD / 'bank/CONFIRMATION.json'), 'source_sha256': sha(OLD / 'bank/CONFIRMATION.json'),
        'state_count': len(selected), 'qid_count': len({s['qid'] for s in selected}),
        'no_h_count': sum(not s['belief']['hypothesis'] for s in selected),
        'state_ids': [s['state_id'] for s in selected],
        'historical_errors': {s['state_id']: review['B5__' + s['state_id']] for s in selected},
        'fresh': False, 'controlled_delta_projections': 0, 'length_failure_reused': False,
        'limitations': 'Failure-enriched development; historical W rubric differs; concurrent B0 required.'})
    inputs = []
    audit = []
    support = read(OLD / 'bank/CLAIM_SUPPORT_REVIEW.json')
    sources = read(OLD / 'bank/SOURCES.json')
    unique_claims = {}
    used_sources = {}
    for s in selected:
        sid = s['state_id']
        case = sid.split('_')[0]
        snap_path = OLD / f'acquisition/trajectories/{case}/{sid.split("_")[1]}.json'
        snap = read(snap_path)
        raw = snap['state']
        b = {'question': raw['question'], 'claims': [c['statement'] for c in raw['claims']], 'hypothesis': raw['hypothesis'] or ''}
        assert b == s['belief']
        assert digest(b) == s['belief_sha256']
        inputs.append({'state_id': sid, 'qid': s['qid'], 'belief': b, 'belief_sha256': digest(b), 'natural': True, 'fresh': False})
        ca = []
        for c in s['claim_records']:
            match = [r for r in support if r['qid'] == s['qid'] and r['statement'] == c['statement'] and r['observation_hash'] in c['source_text_hashes']]
            assert match and all(r['review']['status'] == 'supported' for r in match)
            for r in match:
                h = r['observation_hash']
                assert hashlib.sha256(sources[h]['text'].encode()).hexdigest() == h
                used_sources[h] = sources[h]
                unique_claims[(s['qid'], c['statement'])] = r
            ca.append({'claim_record': c, 'inherited_source_support': match})
        h_origins = []
        for prev in sorted((OLD / f'acquisition/trajectories/{case}').glob('S*.json')):
            if prev.name > snap_path.name:
                continue
            r = read(prev)
            if (r['state']['hypothesis'] or '') == b['hypothesis']:
                h_origins.append({'snapshot': relative(prev), 'sha256': sha(prev), 'transition': r['transition']})
        audit.append({'state_id': sid, 'qid': s['qid'], 'snapshot': relative(snap_path), 'snapshot_sha256': sha(snap_path),
                      'claims': ca, 'hypothesis': b['hypothesis'], 'h_first_equal_snapshot': h_origins[0],
                      'h_status': 'provisional; no factual authority', 'support_scope': 'Inherited source-relative review plus mechanical identity check, not new global truth audit',
                      'old_need_request': relative(OLD / f'need/confirmation/calls/B5__{sid}.request.json'),
                      'old_request_sha256': sha(OLD / f'need/confirmation/calls/B5__{sid}.request.json')})
    write(P / 'e1_need/BANK.json', inputs)
    write(P / 'e1_need/PROVENANCE.json', audit)
    write(P / 'e1_need/CLAIM_SUPPORT.json', list(unique_claims.values()))
    write(P / 'e1_need/OBSERVED_SOURCES.json', used_sources)
    write(P / 'e1_need/REVIEW_INPUTS.md', '\n\n'.join('## ' + r['state_id'] + '\n\n' + json.dumps(r['belief'], ensure_ascii=False, indent=2) for r in inputs) + '\n')
    base = (OLD / 'need/prompts/B5.txt').read_text()
    prompts = {'B0': base, 'B1': base + '\n' + PREMISE + '\n',
               'B2': base + '\n' + COHERENCE + '\n', 'B3': base + '\n' + PREMISE + '\n\n' + COHERENCE + '\n'}
    for arm, filename in ARMS.items():
        write(P / 'prompts' / filename, prompts[arm])
    query_common = '''Express only the supplied Need as operational search language. Preserve its subject, relation direction, ranges, uncertainty and scope. Paraphrases, synonyms, source vocabulary and complementary lexical entry points are allowed. Do not invent identities, events, fixed years from ranges or unrelated constraints. A speculative query term is not a fact. Do not invent a value that would require another query's result. Return JSON only.'''
    write(P / 'prompts/query_single.txt', query_common + '\nReturn {"queries":["one search query"]}, exactly one nonempty query.\n')
    write(P / 'prompts/query_multi.txt', query_common + '\nReturn {"queries":["query"]}, one to three nonempty queries serving the same Need. All must be independently formulable before any results. Use complementary formulations only when useful; do not force three or bundle other objectives.\n')
    jobs = []
    order = sorted(inputs, key=lambda s: hashlib.sha256(('minimal-need-v1:' + s['state_id']).encode()).hexdigest())
    for i, s in enumerate(order):
        arms = list(ARMS)
        arms = arms[i % 4:] + arms[:i % 4]
        for arm in arms:
            req = copy.deepcopy(old_jobs[s['state_id']]['request'])
            assert req['messages'][0]['content'] == base
            req['messages'][0]['content'] = prompts[arm]
            assert 'max_tokens' not in req and 'tools' not in req
            jobs.append({'id': arm + '__' + s['state_id'], 'arm': arm, 'state_id': s['state_id'], 'qid': s['qid'],
                         'belief_sha256': s['belief_sha256'], 'request_sha256': digest(req), 'request': req})
    write(P / 'e1_need/SCHEDULE.json', jobs)
    write(P / 'analysis/FRESHNESS_EXCLUSIONS.json', exposure_inventory())
    e0 = []
    definitions = {
        'F08_S00': (2, False, 'W_independent', 'Separate marital/childlessness history and a donation transaction. Sharing the donor identity does not make those one bounded judgment.', ['donation to building', 'marital childlessness']),
        'F10_S00': (2, False, 'W_independent', 'Promotion in 2022 and same-university educational history are separate event families. Bachelor/master equality alone would be coherent; promotion adds another objective.', ['promotion event', 'education/university equality']),
        'F11_S00': (1, True, 'W_multiquery', 'Identify one book by its bounded publication/content profile: illustration count and telephone/telegraph descriptions. It does not add the separate rust-cleaning or biographical reference puzzles.', ['book illustration/content profile']),
        'F14_S00': (1, True, 'W_multiquery', 'Identify one DLC feature package. Religion, technology and national mechanics are facets of that same release profile; advisor education, thesis and designer credit are not bundled.', ['DLC release feature profile']),
        'F14_S01': (1, True, 'W_multiquery', 'Same bounded DLC feature profile within the observed EU4 game. This tests a candidate game product; it does not assert a named DLC is the answer or that its other question constraints hold.', ['DLC release feature profile'])}
    for sid, (count, coherent, label, reason, objectives) in definitions.items():
        s = records[sid]
        result = read(OLD / f'need/confirmation/calls/B5__{sid}.result.json')
        assert review['B5__' + sid]['codes'] == ['W']
        e0.append({'state_id': sid, 'qid': s['qid'], 'belief': s['belief'], 'need': result['output']['need'],
                   'old_label': 'W', 'old_review': review['B5__' + sid],
                   'historical_result': relative(OLD / f'need/confirmation/calls/B5__{sid}.result.json'),
                   'historical_result_sha256': sha(OLD / f'need/confirmation/calls/B5__{sid}.result.json'),
                   'objective_count': count, 'objectives': objectives,
                   'has_dependency': False, 'dependency_reason': 'Generic descriptive discovery queries can be formulated from Q without knowing another result. Candidate-specific follow-up attributes still require binding first; none is instantiated here.',
                   'single_resolution_judgment': coherent, 'multiquery_sufficient': coherent,
                   'multiquery_sufficient_meaning': 'Structurally fits one Need with independent lexical searches; retrieval sufficiency unmeasured.',
                   'new_label': label, 'valid_under_new_rubric': coherent,
                   'other_dimension_review': {'Relevant': True, 'Unresolved': True, 'Grounded': True, 'PremiseClosed': True, 'Coherent': coherent, 'Actionable': True},
                   'reason': reason, 'ambiguity': 'medium',
                   'alternative_reading': 'A strict single-relation reading would retain old W for the profile cases; treating all final-answer filters as one objective would also admit the two independent cases. Neither is the primary new rubric.',
                   'reviewer': 'Codex single reviewer; offline, nonblind, prefix QCH plus historical Need only'})
    write(P / 'e0_w_reaudit/REVIEW.json', e0)
    write(P / 'e0_w_reaudit/METRICS.json', {'reviewed': 5, 'unique_qids': 4, 'W_independent': 2, 'W_multiquery': 3,
          'valid_coherent_multiquery': 3, 'valid_coherent_unique_qids': 2, 'model_calls': 0, 'tool_calls': 0,
          'historical_score_changed': False, 'retrieval_gain_measured': False})
    # Estimate from exactly the selected historical B5 responses, not a pricing guess.
    old_results = [read(OLD / f'need/confirmation/calls/B5__{s["state_id"]}.result.json') for s in inputs]
    summed = {key: sum(r['token_accounting'][key] for r in old_results) for key in ('input', 'output', 'reasoning', 'hit', 'miss')}
    estimate = {'status': 'ESTIMATE_NOT_USAGE', 'scheduled_calls': len(jobs), 'observed_calls_this_task': 0,
                'historical_selected_B5_calls': len(inputs), 'historical_selected_B5_usage': summed,
                'four_arm_historical_output_proxy': 4 * summed['output'],
                'four_arm_historical_input_lower_proxy_before_prompt_additions': 4 * summed['input'],
                'payload_utf8_bytes_total': sum(len(json.dumps(j['request'], ensure_ascii=False).encode()) for j in jobs),
                'historical_selected_slowest_seconds': max(r['elapsed_seconds'] for r in old_results),
                'historical_selected_sum_latency_seconds': sum(r['elapsed_seconds'] for r in old_results),
                'stress_scenario_completion_tokens_65536_each': len(jobs) * 65536,
                'stress_is_not_configured_or_guaranteed_cap': True,
                'future_conditional_calls': {'bounded_revision': 'up to one new 72-call block, separate freeze', 'fresh_Need': '60–80 plus separately budgeted natural acquisition', 'E2_query_generation': '40–60 after E1 PASS; 40–120 Search invocations', 'E3_E4': 'not budgeted/executable until prerequisite gates and banks'},
                'monetary_estimate': None, 'limitations': 'No verified current price. Prompt additions, reasoning and cache can materially change costs; bytes are not provider tokens. No hard token cap is introduced.'}
    write(P / 'analysis/CALL_ESTIMATE.json', estimate)

def freeze():
    excluded = {'FREEZE.json', 'analysis/DRY_RUN.json', 'analysis/FINAL_INTEGRITY.json', 'analysis/TEST_RESULTS.txt', 'FINAL_CONCLUSION.md', 'README.md'}
    files = {relative(p): sha(p) for p in sorted(P.rglob('*')) if p.is_file() and p.relative_to(P).as_posix() not in excluded and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.suffix != '.pyc'}
    write(P / 'FREEZE.json', {'version': 'E1-development-v1', 'base_head': BASE, 'prepared_against_head': git('rev-parse', 'HEAD'),
          'model_calls': 72, 'horizon': 1, 'tools': [], 'files': files,
          'execution_head_rule': 'Runner records exact committed HEAD before first request, validates all files against git HEAD, and stores manifest digest.',
          'authorization': 'Not authorized in this preparation; explicit later user approval required by task section35.'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'freeze'])
    args = parser.parse_args()
    (build if args.mode == 'build' else freeze)()
