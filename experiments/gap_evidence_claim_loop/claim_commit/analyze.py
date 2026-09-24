"""Pre-call F2 truth, direct and verifier-gated Claim admission metrics."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())
EVENTS = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]


def score():
    assert len(BANK) == len(OUTCOMES) == 53
    rows = []
    for p in BANK:
        o = OUTCOMES[p["packet_id"]]
        assert set(o["D_commit"]) == {"claim_id", "statement", "evidence_refs", "version"}
        assert o["D_commit"]["statement"] == p["finding"]["statement"]
        assert o["D_commit"]["evidence_refs"] == [p["new_observation"]["ref"]]
        for arm in ("D", "V"):
            claim = o[arm + "_commit"]
            rows.append({"packet_id": p["packet_id"], "source_case": p["source_case"],
                         "qid": p["qid"], "part": p["part"],
                         "stress_type": p.get("stress_type"), "arm": arm,
                         "expected_supported": p["review"]["expected_supported"],
                         "verdict": o["verdict"]["verdict"], "error": o["error"],
                         "committed": claim is not None,
                         "evidence_binding_valid": claim is None or
                           claim["evidence_refs"] == [p["new_observation"]["ref"]]})
    by_arm = {}
    for arm in ("D", "V"):
        group = [r for r in rows if r["arm"] == arm]
        accepted = [r for r in group if r["committed"]]
        supported = [r for r in group if r["expected_supported"]]
        negative = [r for r in group if not r["expected_supported"]]
        stress = [r for r in group if r["part"] == "B"]
        by_arm[arm] = {"packets": len(group), "committed": len(accepted),
            "supported_committed": sum(r["expected_supported"] for r in accepted),
            "unsupported_committed": sum(not r["expected_supported"] for r in accepted),
            "committed_claim_precision": sum(r["expected_supported"] for r in accepted)/len(accepted) if accepted else 0,
            "commit_recall": sum(r["committed"] for r in supported)/len(supported),
            "false_promotion": sum(r["committed"] for r in negative)/len(negative),
            "stress_rejection": sum(not r["committed"] for r in stress)/len(stress),
            "evidence_binding_accuracy": sum(r["evidence_binding_valid"] for r in accepted)/len(accepted) if accepted else 0,
            "claim_bloat": sum(not r["expected_supported"] for r in accepted),
            "errors": sum(r["error"] is not None for r in group)}
    v = by_arm["V"]
    checks = {"precision": v["committed_claim_precision"] >= .95,
              "recall": v["commit_recall"] >= .90,
              "false_promotion": v["false_promotion"] <= .05,
              "stress_rejection": v["stress_rejection"] >= .90}
    responses = [e for e in EVENTS if e["kind"] == "model_response"]
    prompt_tokens = sum(e["cache_usage"].get("prompt_tokens") or 0 for e in responses)
    hit_tokens = sum(e["cache_usage"].get("prompt_cache_hit_tokens") or 0 for e in responses)
    result = {"by_arm": by_arm, "verdict_counts": dict(Counter(OUTCOMES[p["packet_id"]]["verdict"]["verdict"] for p in BANK)),
              "stress_by_type": {kind: {"n":sum(r["stress_type"] == kind for r in rows if r["arm"] == "V"),
                                   "rejected":sum(r["stress_type"] == kind and not r["committed"] for r in rows if r["arm"] == "V")}
                                 for kind in ("V1","V2","V3","V4","V5")},
              "paired_false_promotion_reductions": sum(OUTCOMES[p["packet_id"]]["V_commit"] is None
                                                      for p in BANK if not p["review"]["expected_supported"]),
              "gate_checks": checks, "f2_pass": all(checks.values()),
              "cache_usage": {"calls": len(responses), "prompt_tokens": prompt_tokens,
                              "hit_tokens": hit_tokens,
                              "weighted_hit_rate": hit_tokens/prompt_tokens if prompt_tokens else None},
              "rows": rows}
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__": score()
