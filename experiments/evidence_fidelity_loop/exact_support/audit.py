"""Audit E2 no-retry paired requests and pointer mechanics."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from run import BANK, FREEZE, digest, gate, request, validate

HERE = Path(__file__).resolve().parent
gate()
f = json.loads(FREEZE.read_text())
events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
counts = Counter(e["kind"] for e in events)
assert counts == {"model_request": 136, "model_response": 136, "cell_outcome": 136}, counts
by_cell = defaultdict(list)
for event in events:
    by_cell[event["cell"]].append(event)
assert len(by_cell) == 136
outcomes = json.loads((HERE / "outcomes.json").read_text())
reviews = json.loads((HERE / "REVIEWS.json").read_text())
assert len(outcomes) == 136 and len(reviews) == 68
for case in BANK:
    for arm in ("V0", "V1"):
        cell = case["case_id"] + ":" + arm
        ev = by_cell[cell]
        assert [e["kind"] for e in ev] == ["model_request", "model_response", "cell_outcome"]
        assert ev[0]["request"] == request(case, arm)
        assert ev[0]["request_hash"] == f["request_hashes"][cell] == digest(ev[0]["request"])
        assert ev[1]["response"]["choices"][0]["finish_reason"] == "stop"
        value, valid, error = validate(case, arm, outcomes[cell]["output"])
        assert (value, valid, error) == (outcomes[cell]["output"], outcomes[cell]["mechanical_valid"],
                                         outcomes[cell]["mechanical_error"])
    v0 = request(case, "V0")["messages"]
    v1 = request(case, "V1")["messages"]
    assert v0[1] == v1[1]
    assert v0[0] != v1[0]
print("PASS: 68 paired cases, 136 single responses, zero retries; V0/V1 user inputs identical; pointer outcomes reproducible")
