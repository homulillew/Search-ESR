"""Mechanical E1 provenance, request isolation, and no-retry audit."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from run import BANK, FREEZE, gate, request, digest

HERE = Path(__file__).resolve().parent
gate()
f = json.loads(FREEZE.read_text())
events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
counts = Counter(e["kind"] for e in events)
assert counts == {"model_request": 88, "model_response": 88, "cell_outcome": 88}, counts
by_cell = defaultdict(list)
for event in events:
    by_cell[event["cell"]].append(event)
assert len(by_cell) == 88
for c in BANK:
    for arm in ("T", "P"):
        cell = c["case_id"] + ":" + arm
        ev = by_cell[cell]
        assert len(ev) == 3 and [x["kind"] for x in ev] == [
            "model_request", "model_response", "cell_outcome"]
        assert ev[0]["request"] == request(c, arm)
        assert ev[0]["request_hash"] == f["request_hashes"][cell]
        assert ev[0]["request_hash"] == digest(ev[0]["request"])
        assert ev[0]["request"]["model"] == "deepseek-flash"
        assert ev[1]["response"]["choices"][0]["finish_reason"] == "stop"
    t = request(c, "T")["messages"]
    p = request(c, "P")["messages"]
    assert t[0] == p[0]
    tu, pu = json.loads(t[1]["content"]), json.loads(p[1]["content"])
    assert {k: v for k, v in pu.items() if k != "observation"} == {
        k: v for k, v in tu.items() if k != "observation"}
    assert {k: v for k, v in pu["observation"].items()
            if k not in ("doc_ref", "title", "url")} == tu["observation"]
assert len(json.loads((HERE / "REVIEWS.json").read_text())) == 88
assert len(json.loads((HERE / "outcomes.json").read_text())) == 88
print("PASS: 44 pairs, 88 single requests, 88 single responses, 88 outcomes; only observed metadata differs")
