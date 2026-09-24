"""Score the frozen V1 natural-Finding paired comparison."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
labels = {r["candidate_id"]: r for r in json.loads((HERE / "ANNOTATIONS.json").read_text())}
outcomes = json.loads((HERE / "verifier_outcomes.json").read_text())
events = [json.loads(line) for line in (HERE / "verifier_events.jsonl").open()]
assert len(labels) == len(outcomes) == 55
assert set(labels) == set(outcomes)


def div(a, b):
    return a / b if b else None


def score(accepted):
    ids = [cid for cid in labels if accepted(cid)]
    support = sum(labels[cid]["source_supported"] for cid in ids)
    eligible = sum(labels[cid]["claim_eligible"] for cid in ids)
    all_supported = sum(x["source_supported"] for x in labels.values())
    return {
        "accepted": len(ids),
        "source_supported_accepted": support,
        "source_precision": div(support, len(ids)),
        "claim_eligible_accepted": eligible,
        "full_claim_precision": div(eligible, len(ids)),
        "supported_recall": div(support, all_supported),
        "unsupported_false_promotions": len(ids) - support,
        "supported_false_rejections": all_supported - support,
        "off_gap_or_duplicate_accepted": sum(not labels[cid]["claim_eligible"] and
                                              labels[cid]["source_supported"] for cid in ids),
    }


direct = score(lambda _: True)
verify = score(lambda cid: outcomes[cid]["output"]["supported"])
responses = [x for x in events if x["kind"] == "model_response"]
assert len(responses) == 55
usage = {k: sum(x["response"]["usage"].get(k, 0) for x in responses)
         for k in ("prompt_tokens", "completion_tokens", "total_tokens",
                   "prompt_cache_hit_tokens", "prompt_cache_miss_tokens")}
latency = [x["latency_seconds"] for x in responses]
unsupported = sum(not x["source_supported"] for x in labels.values())
removed = unsupported - verify["unsupported_false_promotions"]
decision = {
    "A_necessity_unproven": direct["source_precision"] >= .97 and unsupported < 5,
    "B_verify_deployable": unsupported >= 5 and div(removed, unsupported) >= .60 and
        verify["supported_recall"] >= .95,
    "C_verify_recall_prohibits": verify["supported_recall"] < .90,
    "R1_direct_admissible": direct["source_precision"] >= .97 and
        direct["full_claim_precision"] >= .95,
    "R1_verify_admissible": verify["source_precision"] >= .97 and
        verify["full_claim_precision"] >= .95 and verify["supported_recall"] >= .95,
}
if not any(decision.values()):
    decision["interpretation"] = "Gray zone: V improves source precision, but neither path is admissible for R1."
elif not decision["R1_direct_admissible"] and not decision["R1_verify_admissible"]:
    decision["interpretation"] = "Neither V1 policy is admissible for R1."
else:
    decision["interpretation"] = "At least one V1 policy is admissible for R1."
result = {
    "n_packets": 52, "n_findings": 55, "n_qids_with_findings": 10,
    "direct": direct, "verify": verify,
    "rejected_ids": [cid for cid in labels if not outcomes[cid]["output"]["supported"]],
    "unsupported_ids": [cid for cid in labels if not labels[cid]["source_supported"]],
    "api_errors": sum(x["error"] is not None for x in outcomes.values()),
    "extra_verifier_calls": len(responses), "verifier_usage": usage,
    "verifier_prompt_cache_hit_rate": div(usage["prompt_cache_hit_tokens"], usage["prompt_tokens"]),
    "verifier_latency_seconds_sum": sum(latency),
    "verifier_latency_seconds_median": sorted(latency)[len(latency)//2],
    "unsupported_removed_fraction": div(removed, unsupported),
    "decision": decision,
}
(HERE / "RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
