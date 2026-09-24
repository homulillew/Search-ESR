"""Score C1 against frozen claim-only local Gap labels."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
bank = {x["case_id"]: x for x in json.loads((HERE / "BANK.json").read_text())}
outcomes = json.loads((HERE / "outcomes.json").read_text())
events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
assert len(bank) == 40 and len(outcomes) == 80


def div(a, b):
    return a / b if b else None


result = {"n_packets": 40, "n_qids": 10, "arms": {}}
for arm in ("C0", "C1"):
    full = [c for c in bank.values() if c["review"]["status"] == "resolved"]
    opened = [c for c in bank.values() if c["review"]["status"] == "open"]
    trap = [c for c in bank.values() if c["review"]["category"] == "near_complete"]

    def pred(c):
        output = outcomes[c["case_id"] + ":" + arm]["output"]
        return output["status"] if output else "invalid"

    premature = [c["case_id"] for c in opened if pred(c) == "resolved"]
    missed = [c["case_id"] for c in full if pred(c) != "resolved"]
    rejected_trap = [c["case_id"] for c in trap if pred(c) == "open"]
    responses = [x for x in events if x["kind"] == "model_response" and x["cell"].endswith(":" + arm)]
    usage = {key: sum(x["response"]["usage"].get(key, 0) for x in responses)
             for key in ("prompt_tokens", "completion_tokens", "total_tokens",
                         "prompt_cache_hit_tokens", "prompt_cache_miss_tokens")}
    result["arms"][arm] = {
        "valid": sum(outcomes[c["case_id"] + ":" + arm]["error"] is None for c in bank.values()),
        "errors": {c["case_id"]: outcomes[c["case_id"] + ":" + arm]["error"]
                   for c in bank.values() if outcomes[c["case_id"] + ":" + arm]["error"]},
        "premature_close_ids": premature, "premature_close_rate": div(len(premature), len(opened)),
        "missed_close_ids": missed, "missed_close_rate": div(len(missed), len(full)),
        "fully_resolved_recall": div(len(full) - len(missed), len(full)),
        "near_complete_rejected": len(rejected_trap), "near_complete_total": len(trap),
        "near_complete_trap_rejection": div(len(rejected_trap), len(trap)),
        "usage": usage, "prompt_cache_hit_rate": div(usage["prompt_cache_hit_tokens"], usage["prompt_tokens"]),
        "latency_seconds_sum": sum(x["latency_seconds"] for x in responses),
    }
    s = result["arms"][arm]
    s["gate_pass"] = s["premature_close_rate"] <= .05 and s["missed_close_rate"] <= .10 and \
        s["fully_resolved_recall"] >= .90 and s["near_complete_trap_rejection"] >= .90

# Single-reviewer manual semantic audit of all 20 C1 open-case missing strings
# is recorded separately in MISSING_REVIEW.json.
review = json.loads((HERE / "MISSING_REVIEW.json").read_text())
assert len(review) == 20 and {x["case_id"] for x in review} == \
    {c["case_id"] for c in bank.values() if c["review"]["status"] == "open"}
result["arms"]["C1"]["missing_description_accurate"] = sum(x["accurate"] for x in review)
result["arms"]["C1"]["missing_description_total"] = len(review)
result["chosen_policy"] = "C0" if result["arms"]["C0"]["gate_pass"] else \
    "C1" if result["arms"]["C1"]["gate_pass"] else "none"
(HERE / "RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
