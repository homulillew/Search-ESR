"""Audit F2 request isolation, exact W and one verifier call per packet."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
bank = {p["packet_id"]: p for p in json.loads((HERE / "BANK.json").read_text())}
events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
counts = Counter(e["kind"] for e in events)
requests = [e for e in events if e["kind"] == "model_request"]
assert len(requests) == len(bank) == 53
assert len({e["packet_id"] for e in requests}) == 53
for e in requests:
    p = bank[e["packet_id"]]
    user = json.loads(e["request"]["messages"][1]["content"])
    assert set(user) == {"active_gap", "finding", "exact_observation", "relevant_committed_claims"}
    assert user["finding"] == p["finding"]
    assert user["exact_observation"]["text"] == p["new_observation"]["text"]
    assert e["request"]["model"] == "deepseek-flash"
summary = {"packets": 53, "single_call_per_packet": True,
           "requests_without_review_labels_or_query_arguments": 53,
           "responses": counts["model_response"], "errors": counts["cell_error"],
           "event_counts": dict(counts)}
(HERE / "INPUT_AUDIT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))
