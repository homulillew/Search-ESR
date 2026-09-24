"""Score frozen E2 with independent semantic pointer reviews."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())
REVIEWS = json.loads((HERE / "REVIEWS.json").read_text())
FREEZE = json.loads((HERE / "freeze.json").read_text())
BY_ID = {c["case_id"]: c for c in BANK}


def ratio(n, d):
    return n / d if d else None


def raw_supported(cell):
    x = OUTCOMES[cell]
    return x["error"] is None and x["output"]["verdict"] == "supported"


def accepted(case, arm):
    cell = case["case_id"] + ":" + arm
    if not raw_supported(cell):
        return False
    if arm == "V0":
        return True
    return OUTCOMES[cell]["mechanical_valid"] and REVIEWS[cell]["pointer_sufficient"]


def operational_v1_accepted(case):
    """What the Harness could actually commit without a semantic reviewer."""
    cell = case["case_id"] + ":V1"
    return raw_supported(cell) and OUTCOMES[cell]["mechanical_valid"]


def arm_metrics(arm):
    accepted_cases = [c for c in BANK if accepted(c, arm)]
    true = [c for c in BANK if c["review"]["source_supported"]]
    stress_neg = [c for c in BANK if c["origin"] == "genuine_W_stress" and not c["review"]["source_supported"]]
    false_accept = [c for c in accepted_cases if not c["review"]["source_supported"]]
    return {"calls": len(BANK), "errors": sum(OUTCOMES[c["case_id"] + ":" + arm]["error"] is not None for c in BANK),
            "raw_supported_verdicts": sum(raw_supported(c["case_id"] + ":" + arm) for c in BANK),
            "accepted": len(accepted_cases), "true_accepted": len(accepted_cases) - len(false_accept),
            "false_accepted": len(false_accept),
            "commit_precision": ratio(len(accepted_cases) - len(false_accept), len(accepted_cases)),
            "commit_recall": ratio(sum(accepted(c, arm) for c in true), len(true)),
            "full_claim_eligibility_precision": ratio(sum(c["review"]["claim_eligible"] for c in accepted_cases), len(accepted_cases)),
            "stress_negative_rejected": sum(not accepted(c, arm) for c in stress_neg),
            "stress_negative_total": len(stress_neg),
            "stress_negative_rejection_rate": ratio(sum(not accepted(c, arm) for c in stress_neg), len(stress_neg)),
            "false_accept_ids": [c["case_id"] for c in false_accept],
            "missed_true_ids": [c["case_id"] for c in true if not accepted(c, arm)]}


v0, v1 = arm_metrics("V0"), arm_metrics("V1")
operational_cases = [c for c in BANK if operational_v1_accepted(c)]
operational_true = [c for c in BANK if c["review"]["source_supported"]]
operational_stress_negative = [c for c in BANK if c["origin"] == "genuine_W_stress"
                               and not c["review"]["source_supported"]]
operational = {
    "accepted_by_mechanics": len(operational_cases),
    "source_supported_accepted": sum(c["review"]["source_supported"] for c in operational_cases),
    "source_false_accepted": [c["case_id"] for c in operational_cases if not c["review"]["source_supported"]],
    "source_precision": ratio(sum(c["review"]["source_supported"] for c in operational_cases), len(operational_cases)),
    "source_recall": ratio(sum(operational_v1_accepted(c) for c in operational_true), len(operational_true)),
    "exact_pointer_sufficient_accepted": sum(REVIEWS[c["case_id"] + ":V1"]["pointer_sufficient"] for c in operational_cases),
    "exact_support_precision": ratio(sum(REVIEWS[c["case_id"] + ":V1"]["pointer_sufficient"] for c in operational_cases), len(operational_cases)),
    "full_claim_eligibility_precision": ratio(sum(c["review"]["claim_eligible"]
                                                   and REVIEWS[c["case_id"] + ":V1"]["pointer_sufficient"]
                                                   for c in operational_cases), len(operational_cases)),
    "stress_negative_rejected": sum(not operational_v1_accepted(c) for c in operational_stress_negative),
    "stress_negative_total": len(operational_stress_negative),
}
raw_v1 = [c for c in BANK if raw_supported(c["case_id"] + ":V1")]
mechanical_valid = [c for c in raw_v1 if OUTCOMES[c["case_id"] + ":V1"]["mechanical_valid"]]
pointer_sufficient = [c for c in mechanical_valid if REVIEWS[c["case_id"] + ":V1"]["pointer_sufficient"]]
pointer = {"raw_supported": len(raw_v1), "mechanically_valid": len(mechanical_valid),
           "mechanical_validity_rate": ratio(len(mechanical_valid), len(raw_v1)),
           "semantically_sufficient": len(pointer_sufficient),
           "support_sufficiency_rate_among_valid": ratio(len(pointer_sufficient), len(mechanical_valid)),
           "mechanical_invalid_ids": [c["case_id"] for c in raw_v1 if c not in mechanical_valid],
           "semantically_insufficient_ids": [c["case_id"] for c in mechanical_valid if c not in pointer_sufficient]}
stress = {}
for kind in ("S1", "S2", "S3", "S4", "S5", "S6"):
    cells = [c for c in BANK if c["review"]["stress_type"] == kind]
    stress[kind] = {"total": len(cells), "truth_supported": sum(c["review"]["source_supported"] for c in cells),
                    "V0_accept": sum(accepted(c, "V0") for c in cells),
                    "V1_accept": sum(accepted(c, "V1") for c in cells),
                    "V0_false_accept": sum(accepted(c, "V0") and not c["review"]["source_supported"] for c in cells),
                    "V1_false_accept": sum(accepted(c, "V1") and not c["review"]["source_supported"] for c in cells)}
v0_false_ids = set(v0["false_accept_ids"])
v1_false_ids = set(v1["false_accept_ids"])
paired_fixes = sorted(v0_false_ids - v1_false_ids)
paired_regressions = sorted(v1_false_ids - v0_false_ids)
g = FREEZE["gate"]
checks = {"commit_precision": v1["commit_precision"] >= g["commit_precision_min"],
          "commit_recall": v1["commit_recall"] >= g["commit_recall_min"],
          "temporal_false_accept": stress["S1"]["V1_false_accept"] / stress["S1"]["total"] <= g["temporal_false_accept_max"],
          "identity_false_accept": stress["S2"]["V1_false_accept"] / stress["S2"]["total"] <= g["identity_false_accept_max"],
          "sequence_false_accept": stress["S3"]["V1_false_accept"] / stress["S3"]["total"] <= g["sequence_false_accept_max"],
          "pointer_validity": pointer["mechanical_validity_rate"] >= g["pointer_validity_min"],
          "stress_negative_rejection": v1["stress_negative_rejection_rate"] >= g["stress_negative_rejection_min"]}
trigger = v0["false_accepted"] >= g["V0_false_accept_trigger"]
if trigger:
    checks["conditional_superiority"] = (len(paired_fixes) - len(paired_regressions) >= g["V1_net_improvements_min"]
                                          and len(paired_regressions) <= g["reverse_worsening_max"])
cache = Counter()
for line in (HERE / "events.jsonl").open():
    e = json.loads(line)
    if e["kind"] == "model_response":
        for k in ("prompt_cache_hit_tokens", "prompt_cache_miss_tokens"):
            cache[k] += (e.get("cache_usage") or {}).get(k, 0) or 0
result = {"V0": v0, "V1": v1, "pointer": pointer, "stress": stress,
          "V1_metric_semantics": "offline-review-filtered; semantic reviewer is not an operational Harness gate",
          "V1_operational_mechanical_only": operational,
          "V1_operational_checks": {
              "exact_support_precision": operational["exact_support_precision"] >= g["commit_precision_min"],
              "source_recall": operational["source_recall"] >= g["commit_recall_min"],
              "temporal_false_accept": not any(operational_v1_accepted(c) for c in BANK if c["review"]["stress_type"] == "S1"),
              "pointer_validity": pointer["mechanical_validity_rate"] >= g["pointer_validity_min"],
              "stress_negative_rejection": operational["stress_negative_rejected"] / operational["stress_negative_total"] >= g["stress_negative_rejection_min"]},
          "paired_false_accept_fixes": paired_fixes,
          "paired_false_accept_regressions": paired_regressions,
          "conditional_superiority_activated": trigger,
          "checks": checks, "gate_pass": all(checks.values()),
          "cache": dict(cache), "all_outcomes_retained": len(OUTCOMES) == 136}
(HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
