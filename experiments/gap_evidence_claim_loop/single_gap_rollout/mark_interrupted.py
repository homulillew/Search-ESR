"""Append an explicit terminal record for the user-interrupted in-flight cell.

This never repeats the model request or changes prior events.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / 'events.jsonl'
CELL = 'F3_177:R0'


def main():
    events = [json.loads(line) for line in PATH.open()]
    own = [e for e in events if e['cell'] == CELL]
    if any(e['kind'] == 'cell_end' for e in own):
        raise ValueError('cell already terminal')
    if own[-1]['kind'] != 'gap_review_request':
        raise ValueError('unexpected terminal event')
    decision = own[-1]['decision']
    responses = [e for e in own if e['kind'] == 'gap_review_response' and e['decision'] == decision]
    requests = [e for e in own if e['kind'] == 'gap_review_request' and e['decision'] == decision]
    if len(requests) - len(responses) != 1:
        raise ValueError('expected exactly one unanswered request')
    starts = [e for e in own if e['kind'] == 'cell_start']
    claims = list(starts[0]['seed_claims'])
    claims.extend(e['claim'] for e in own if e['kind'] == 'claim_commit')
    tools = [e for e in own if e['kind'] == 'tool_result']
    workspace = tools[-1]['audit']['handles'] if tools else None
    fields = [
        {'kind': 'cell_error', 'cell': CELL, 'decision': decision,
         'error_type': 'UserInterruptedInFlight',
         'error': 'Process ended after gap_review_request with no response; no retry performed.'},
        {'kind': 'cell_end', 'cell': CELL, 'status': 'interrupted_gap_review',
         'final_claims': claims, 'workspace': workspace},
    ]
    with PATH.open('a') as out:
        for field in fields:
            out.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
                                  **field}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
