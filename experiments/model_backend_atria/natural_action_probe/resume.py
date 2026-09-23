"""Frozen recovery of M2 cells left without a terminal event by interruption."""

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

import run as m2

HERE = Path(__file__).resolve().parent
EVENTS = HERE / 'events.jsonl'
RECOVERY = HERE / 'resume_freeze.json'


def event_state():
    events = [json.loads(line) for line in EVENTS.open()]
    frozen = json.loads((HERE / 'freeze.json').read_text())
    cells = [(q, seq, model) for q, seq in frozen['selection']
             for model in (frozen['qwen_model'], frozen['atria_model'])]
    requested = [e['cell'] for e in events if e['kind'] == 'api_request']
    terminal = [e['cell'] for e in events if e['kind'] in ('api_response', 'api_error')]
    if len(set(terminal)) != len(terminal) or not set(terminal) <= set(requested):
        raise ValueError('duplicate or unrequested terminal event')
    pending = [f'{q}:{seq}:{model}' for q, seq, model in cells
               if f'{q}:{seq}:{model}' not in terminal]
    in_flight = [cell for cell in pending if cell in requested]
    if len(in_flight) != 1 or requested.count(in_flight[0]) != 1:
        raise ValueError('expected exactly one interrupted in-flight request')
    if any(requested.count(cell) for cell in pending if cell not in in_flight):
        raise ValueError('unattempted cell unexpectedly has a request event')
    return cells, terminal, pending, in_flight


def freeze():
    m2.gate()
    if RECOVERY.exists():
        raise FileExistsError(RECOVERY)
    cells, terminal, pending, in_flight = event_state()
    doc = {
        'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                            cwd=m2.ROOT, text=True).strip(),
        'reason': 'turn interrupted while M2 original process awaited provider response',
        'terminal_count_before_resume': len(terminal),
        'pending_cells_in_frozen_order': pending,
        'in_flight_without_terminal': in_flight,
        'original_events_sha256': m2.sha(EVENTS),
        'original_stage_freeze_sha256': m2.sha(HERE / 'freeze.json'),
        'original_runner_sha256': m2.sha(HERE / 'run.py'),
        'recovery_runner_sha256': m2.sha(__file__),
        'attempt_policy': 'never rerun terminal cells; record interrupted in-flight attempt, then request only unfinished cells once under original frozen settings',
        'pending_request_sha256': {f'{q}:{seq}:{model}': m2.digest(m2.request(q, seq, model))
                                   for q, seq, model in cells
                                   if f'{q}:{seq}:{model}' in pending},
    }
    RECOVERY.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    return {'terminal': len(terminal), 'pending': len(pending),
            'in_flight': in_flight}


def run():
    m2.gate()
    frozen = json.loads(RECOVERY.read_text())
    if m2.sha(EVENTS) != frozen['original_events_sha256'] \
            or m2.sha(HERE / 'freeze.json') != frozen['original_stage_freeze_sha256'] \
            or m2.sha(HERE / 'run.py') != frozen['original_runner_sha256'] \
            or m2.sha(__file__) != frozen['recovery_runner_sha256']:
        raise ValueError('M2 recovery integrity gate failed')
    cells, terminal, pending, in_flight = event_state()
    if len(terminal) != frozen['terminal_count_before_resume'] \
            or pending != frozen['pending_cells_in_frozen_order'] \
            or in_flight != frozen['in_flight_without_terminal']:
        raise ValueError('M2 event state differs from recovery freeze')
    qwen = m2.Config.load()
    stage = json.loads((HERE / 'freeze.json').read_text())
    if qwen.model != stage['qwen_model'] \
            or urlsplit(qwen.base_url).hostname != stage['qwen_host'] \
            or qwen.timeout != stage['qwen_timeout_seconds']:
        raise ValueError('Qwen config differs from M2 freeze')
    key = dotenv_values(m2.ROOT / m2.ATRIA['credential_file']).get(m2.ATRIA['credential_field'])
    if not key:
        raise ValueError('Atria key missing')
    with OpenAI(api_key=qwen.api_key, base_url=qwen.base_url,
                timeout=qwen.timeout, max_retries=0) as qc, \
         OpenAI(api_key=key, base_url=m2.ATRIA['base_url'],
                timeout=m2.ATRIA['timeout_seconds'], max_retries=0) as ac:
        for q, seq, model in cells:
            cell = f'{q}:{seq}:{model}'
            if cell not in pending:
                continue
            if cell in in_flight:
                m2.emit('interruption', cell=cell,
                        reason='turn_aborted_no_terminal_event', prior_attempt=1)
            params = m2.request(q, seq, model)
            if m2.digest(params) != frozen['pending_request_sha256'][cell]:
                raise ValueError(f'request changed: {cell}')
            attempt = 2 if cell in in_flight else 1
            m2.emit('api_request', cell=cell, attempt=attempt, request=params)
            client = qc if model == qwen.model else ac
            allow = False if model == qwen.model else m2.ATRIA['allow_tool_calls_with_stop']
            try:
                response = client.chat.completions.create(**params)
                raw = response.model_dump(mode='json')
                choice = (raw.get('choices') or [{}])[0]
                parsed, error = m2.validate_batch(choice, m2.SEARCH_FIND_TOOLS,
                                                  allow_stop_with_calls=allow)
                m2.emit('api_response', cell=cell, attempt=attempt, response=raw,
                        raw_finish_reason=choice.get('finish_reason'),
                        raw_tool_calls=(choice.get('message') or {}).get('tool_calls'),
                        validation=error or 'valid', parsed_calls=parsed,
                        action=parsed[0]['name'] if len(parsed) == 1 and error is None
                        else 'batch' if len(parsed) > 1 and error is None
                        else 'stop' if not parsed and error is None else 'invalid')
                print(cell, 'response', flush=True)
            except Exception as exc:
                m2.emit('api_error', cell=cell, attempt=attempt,
                        error_type=type(exc).__name__,
                        http_status=getattr(exc, 'status_code', None),
                        error=str(exc)[:500])
                print(cell, 'error', type(exc).__name__, flush=True)


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'freeze'
    if action == 'freeze':
        print(freeze())
    elif action == 'run':
        run()
    else:
        raise SystemExit('use freeze|run')
