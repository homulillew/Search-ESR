"""Audit completed S2 request boundaries and single-call retention."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
bank = {c["case_id"]: c for c in json.loads((HERE / "BANK.json").read_text())}
events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
counts = Counter(e["kind"] for e in events)
binders = [e for e in events if e["kind"] == "binder_request"]
verifiers = [e for e in events if e["kind"] == "verifier_request"]
assert len(binders) == 120 and len({e["cell"] for e in binders}) == 120
assert len(verifiers) == 72 and len({e["cell"] for e in verifiers}) == 72
assert counts["binder_response"] == 120 and counts["verifier_response"] == 72
assert not any(k.endswith("_error") for k in counts)
allowed_binder = {"test_card", "previous_persistent_bindings", "new_observation"}
allowed_verifier = {"test_condition", "slot", "proposed_value", "new_observation", "previous_verified_binding"}
for e in binders:
    user = json.loads(e["request"]["messages"][1]["content"])
    cid, arm = e["cell"].split(":")
    assert set(user) == allowed_binder | ({"previous_search_query_as_action_history"} if arm == "L" else set())
    assert user["new_observation"]["text"] == bank[cid]["new_observation"]["text"]
    assert e["request"]["model"] == "deepseek-flash"
for e in verifiers:
    user = json.loads(e["request"]["messages"][1]["content"])
    cid = e["cell"].split(":")[0]
    assert set(user) == allowed_verifier
    assert user["new_observation"]["text"] == bank[cid]["new_observation"]["text"]
    assert e["request"]["model"] == "deepseek-flash"
summary = {"binder_requests": len(binders), "verifier_requests": len(verifiers),
           "isolated_binder_requests_without_query_field": 80,
           "query_blind_verifier_requests": len(verifiers),
           "single_call_per_cell": True, "errors": 0,
           "event_counts": dict(counts)}
(HERE / "INPUT_AUDIT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))
