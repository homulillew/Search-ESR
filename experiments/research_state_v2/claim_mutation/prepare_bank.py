"""Copy historical M1 packets and freeze a repaired reviewer label set before calls."""

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / "transactional_research_progress/state_transition"


def main():
    cases = json.loads((OLD / "CASES.json").read_text())
    labels = copy.deepcopy(json.loads((OLD / "REVIEW_LABELS.json").read_text()))
    assert len(cases) == 41 and len({c["qid"] for c in cases}) == 12
    for case in cases:
        label = labels[case["case_id"]]
        label["routing_affected_claim_ids"] = [x["claim_id"] for x in label["required_claim_mutations"]]
        label["routing_only_unscorable"] = []
        label["unscorable_gap_ids"] = []
        if case["case_id"] == "T5_186":
            label["routing_affected_claim_ids"].append("C4")
            label["routing_only_unscorable"] = ["C4"]
            label["unscorable_gap_ids"] = ["G1", "G2"]
            label["forbidden_claim_mutations"].remove("C4")
            label["reason"] += " W1 also names Sean Michael Puckett and Terri L. Puckett, so C4 is routing-positive; its meta wording is not status-scorable."
        if case["case_id"] == "T7_186":
            label["routing_affected_claim_ids"].append("C2")
            label["routing_only_unscorable"] = ["C2"]
            label["unscorable_gap_ids"] = ["G2"]
            label["forbidden_claim_mutations"].remove("C2")
            label["reason"] += " W2 names two Puckett credits, so C2 is routing-positive; its imperative wording is not status-scorable."
        label["routing_affected_claim_ids"] = sorted(set(label["routing_affected_claim_ids"]))
    assert set(labels) == {c["case_id"] for c in cases}
    rules = {c["case_id"]: {g["gap_id"]: "all_supported" for g in c["previous_state"]["gaps"]}
             for c in cases}
    (HERE / "CASES.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n")
    (HERE / "REVIEW_LABELS_V2.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2) + "\n")
    (HERE / "GAP_RULES.json").write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
