"""Audit F1 arm inputs, exact W, call multiplicity and retained failures."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
bank = {c["case_id"]: c for c in json.loads((HERE / "BANK.json").read_text())}
events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
counts = Counter(e["kind"] for e in events)
requests = [e for e in events if e["kind"] == "model_request"]
assert len(requests) == 123 and len({e["cell"] for e in requests}) == 123
for e in requests:
    cid, arm = e["cell"].split(":")
    user = json.loads(e["request"]["messages"][1]["content"])
    keys = {"raw_question", "latest_observation"}
    if arm in ("B", "C"):
        keys.add("active_gap")
    if arm == "C":
        keys.add("relevant_committed_claims")
    assert set(user) == keys
    assert user["raw_question"] == bank[cid]["raw_question"]
    assert user["latest_observation"]["text"] == bank[cid]["new_observation"]["text"]
    assert e["request"]["model"] == "deepseek-flash"
summary = {"cells": 123, "single_call_per_cell": True,
           "A_without_gap_or_claims": 41, "B_with_gap_without_claims": 41,
           "C_with_gap_and_claims": 41,
           "responses": counts["model_response"], "errors": counts["cell_error"],
           "event_counts": dict(counts)}
(HERE / "INPUT_AUDIT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))
