"""Check the proposed call ceiling including early Closure and finalization."""
import json
from pathlib import Path


def test_micro_recovery_joint_request_bound():
    plan = json.loads((Path(__file__).resolve().parents[2] /
                       'experiments/recoverable_loop_clean/CALL_ESTIMATE.json').read_text())

    def costs(slots):
        if slots == 0: return [0]
        tail = costs(slots-1)
        return [6+x for x in tail] + [2+x for x in tail] + [3]  # acquisition, CONTINUE, READY+final

    r1 = max(5+x for x in costs(2))
    r2 = max(costs(3))
    r3 = max([1+x for x in costs(2)] + [2])  # forced Closure, or immediate READY+final
    assert [r1,r2,r3] == [17,18,13]
    assert 4*(r1+r2+r3) == plan['semantic_requests_tight_joint_max'] == 192
    assert plan['max_retries'] == plan['current_task_paid_requests'] == 0
