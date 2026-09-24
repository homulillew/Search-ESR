"""Arm-masked semantic review packets and frozen F1 metrics/gate."""

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())


def rid(cell):
    return "F" + hashlib.sha256(("F1 blind Finding review:" + cell).encode()).hexdigest()[:14]


def prepare_review():
    if (HERE / "REVIEW_PACKETS.json").exists():
        raise FileExistsError("REVIEW_PACKETS.json")
    outcomes = json.loads((HERE / "outcomes.json").read_text())
    assert len(outcomes) == 123
    packets = []
    mapping = {}
    for c in BANK:
        for arm in ("A", "B", "C"):
            cell = c["case_id"] + ":" + arm
            review_id = rid(cell)
            mapping[review_id] = cell
            packets.append({"review_id": review_id, "case_id": c["case_id"], "qid": c["qid"],
                            "raw_question": c["raw_question"], "active_gap": c["active_gap"],
                            "existing_claims_for_review": c["existing_claims"],
                            "new_observation": c["new_observation"],
                            "precall_review": c["review"],
                            "output": outcomes[cell]["output"], "error": outcomes[cell]["error"]})
    packets.sort(key=lambda p: hashlib.sha256(p["review_id"].encode()).hexdigest())
    (HERE / "REVIEW_PACKETS.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRIVATE_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")


def validate_review(packet, review):
    if not isinstance(review, list) or len(review) != len(packet["output"]["findings"]):
        raise ValueError("review count " + packet["review_id"])
    for row in review:
        if not isinstance(row, dict) or set(row) != {"evidence_grounded", "gap_relevant", "world_fact", "overreach",
                                                   "duplicate_existing", "matched_required", "reason"}:
            raise ValueError("review schema " + packet["review_id"])
        if any(not isinstance(row[k], bool) for k in ("evidence_grounded", "gap_relevant", "world_fact", "overreach", "duplicate_existing")):
            raise ValueError("review flags " + packet["review_id"])
        if not isinstance(row["reason"], str) or not row["reason"].strip():
            raise ValueError("review reason " + packet["review_id"])
        if not isinstance(row["matched_required"], list) or len(set(row["matched_required"])) != len(row["matched_required"]):
            raise ValueError("review match " + packet["review_id"])
        if any(type(i) is not int or i not in range(len(packet["precall_review"]["required_findings"])) for i in row["matched_required"]):
            raise ValueError("review match index " + packet["review_id"])
        if row["matched_required"] and (not row["evidence_grounded"] or not row["gap_relevant"] or not row["world_fact"] or row["overreach"]):
            raise ValueError("invalid required match " + packet["review_id"])


def score():
    packets = {p["review_id"]: p for p in json.loads((HERE / "REVIEW_PACKETS.json").read_text())}
    mapping = json.loads((HERE / "PRIVATE_MAPPING.json").read_text())
    reviews = json.loads((HERE / "REVIEWS.json").read_text())
    if set(packets) != set(mapping) or set(reviews) != set(mapping):
        raise ValueError("review mapping mismatch")
    rows = []
    for review_id, cell in mapping.items():
        p = packets[review_id]
        review = reviews[review_id]
        validate_review(p, review)
        arm = cell.split(":")[1]
        covered = {i for item in review for i in item["matched_required"]}
        quality = [x["evidence_grounded"] and x["gap_relevant"] and x["world_fact"] and not x["overreach"] and
                   (arm != "C" or not x["duplicate_existing"]) for x in review]
        rows.append({"cell": cell, "case_id": p["case_id"], "qid": p["qid"], "arm": arm,
                     "type": p["precall_review"]["type"], "error": p["error"],
                     "finding_count": len(review), "quality_count": sum(quality),
                     "required_total": len(p["precall_review"]["required_findings"]),
                     "required_covered": len(covered),
                     "unsupported_count": sum(not x["evidence_grounded"] or x["overreach"] for x in review),
                     "irrelevant_count": sum(not x["gap_relevant"] for x in review),
                     "duplicate_count": sum(x["duplicate_existing"] for x in review),
                     "meta_count": sum(not x["world_fact"] for x in review),
                     "empty": len(review) == 0, "review_id": review_id})
    by_arm = {}
    for arm in ("A", "B", "C"):
        group = [r for r in rows if r["arm"] == arm]
        finds = sum(r["finding_count"] for r in group)
        required = sum(r["required_total"] for r in group)
        nogain = [r for r in group if r["type"] == "E6"]
        by_arm[arm] = {"cases": len(group), "errors": sum(r["error"] is not None for r in group),
                       "findings": finds, "quality_findings": sum(r["quality_count"] for r in group),
                       "finding_precision": sum(r["quality_count"] for r in group) / finds if finds else 0,
                       "finding_recall": sum(r["required_covered"] for r in group) / required if required else 0,
                       "unsupported_inference_rate": sum(r["unsupported_count"] for r in group) / finds if finds else 0,
                       "gap_irrelevant_fact_rate": sum(r["irrelevant_count"] for r in group) / finds if finds else 0,
                       "duplicate_rate": sum(r["duplicate_count"] for r in group) / finds if finds else 0,
                       "meta_count": sum(r["meta_count"] for r in group),
                       "nogain_silence": sum(r["empty"] for r in nogain) / len(nogain),
                       "mean_findings": statistics.mean(r["finding_count"] for r in group),
                       "irrelevant_error_cases": sum(r["irrelevant_count"] > 0 for r in group),
                       "duplicate_error_cases": sum(r["duplicate_count"] > 0 for r in group)}
    idx = {(r["case_id"], r["arm"]): r for r in rows}
    pair = {}
    for treatment in ("B", "C"):
        good = bad = 0
        for c in BANK:
            a, t = idx[(c["case_id"], "A")], idx[(c["case_id"], treatment)]
            good += a["irrelevant_count"] > 0 and t["irrelevant_count"] == 0
            bad += a["irrelevant_count"] == 0 and t["irrelevant_count"] > 0
        pair[treatment + "_vs_A_irrelevant"] = {"improved": good, "worsened": bad, "net": good - bad}
    good = bad = 0
    for c in BANK:
        b, x = idx[(c["case_id"], "B")], idx[(c["case_id"], "C")]
        good += b["duplicate_count"] > 0 and x["duplicate_count"] == 0
        bad += b["duplicate_count"] == 0 and x["duplicate_count"] > 0
    pair["C_vs_B_duplicate"] = {"improved": good, "worsened": bad, "net": good - bad}
    c = by_arm["C"]
    gate = {"precision": c["finding_precision"] >= .90,
            "recall": c["finding_recall"] >= .85,
            "unsupported_inference": c["unsupported_inference_rate"] <= .05,
            "nogain_silence": c["nogain_silence"] >= .90,
            "duplicate_rate": c["duplicate_rate"] <= .10,
            "gap_comparison": by_arm["A"]["irrelevant_error_cases"] < 5 or
                 pair["B_vs_A_irrelevant"]["net"] >= 4 or pair["C_vs_A_irrelevant"]["net"] >= 4,
            "claim_comparison": by_arm["B"]["duplicate_error_cases"] < 4 or
                 pair["C_vs_B_duplicate"]["net"] >= 3}
    results = {"by_arm": by_arm, "paired": pair, "gate_checks": gate,
               "f1_pass": all(gate.values()), "rows": rows}
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "prepare_review": prepare_review()
    elif sys.argv[1] == "score": score()
    else: raise SystemExit("prepare_review|score")
