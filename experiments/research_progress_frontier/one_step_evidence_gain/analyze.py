"""Deterministic Stage D aggregation from raw events and prefix-bound review."""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
C = STUDY / "action_routing"
selected = json.loads((C / "stage_d_preselection.json").read_text())
cases = {c["case_id"]: c for c in json.loads((C / "review_cases.json").read_text())}
review = {r["case_id"]: r for r in json.loads((HERE / "review.json").read_text())}
events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]


def main():
    tool_results = {e["case_id"]: e for e in events if e["kind"] == "tool_result"}
    tool_errors = {e["case_id"]: e for e in events if e["kind"] == "tool_error"}
    verifications = {(e["case_id"], e["arm"]): e for e in events if e["kind"] == "verify_response"}
    verify_errors = {(e["case_id"], e["arm"]): e for e in events if e["kind"] == "verify_error"}
    if len(selected) != 8 or len(tool_results) != 7 or tool_errors or len(verifications) != 3 or verify_errors:
        raise ValueError("Stage D response count or errors differ; inspect events")
    if set(review) != set(tool_results):
        raise ValueError("Incomplete retrieval review")
    rows = []
    for cid in selected:
        case = cases[cid]
        result = tool_results.get(cid)
        if result:
            r = review[cid]
            if r["source_compatible"] not in (True, False, "unclear") or r["useful_evidence"] not in (
                "yes", "partial", "no") or r["gap_effect"] not in (
                "supports_closure", "refutes", "narrows", "no_progress") or not r["reason"]:
                raise ValueError(cid)
            for ref in r["compatible_refs"]:
                got = result["result"]
                valid = {x["doc_ref"] for x in got.get("results", [])} if result["name"] == "search" else {
                    got.get("doc_ref")}
                if ref not in valid:
                    raise ValueError(f"Invalid compatible ref {cid}:{ref}")
            row = {"case_id": cid, "uncertainty_type": case["uncertainty_type_private"],
                   "active_gap": case["active_gap"], "action": result["name"],
                   "arguments": result["arguments"], "result_status": result["result"]["status"], **r}
            if result["name"] == "find":
                row["find_record"] = {"ActiveGap": case["active_gap"],
                                      "TargetDocument": result["arguments"]["doc_ref"],
                                      "FindQuery": result["arguments"]["query"],
                                      "ReturnedWindow": [x["window_ref"] for x in result["result"]["matches"]],
                                      "UsefulEvidence": r["useful_evidence"]}
            rows.append(row)
    verify_rows = []
    for cid in selected:
        if cases[cid]["uncertainty_type_private"] != "closure":
            continue
        for arm in ("V0", "V1"):
            e = verifications.get((cid, arm))
            if e is None:
                verify_rows.append({"case_id": cid, "arm": arm, "called": False,
                                    "correct_closure": False, "reason": "Free Actor chose retrieval"})
                continue
            choice = e["response"]["choices"][0]
            content = choice["message"].get("content") or ""
            m = re.search(r"(?im)^Status:\s*(supported|refuted|open)\s*$", content)
            ref = cases[cid]["current_evidence_refs"][0]
            cited = bool(re.search(r"(?im)^Evidence refs:\s*" + re.escape(ref) + r"\s*$", content))
            status = m.group(1) if m and choice["finish_reason"] == "stop" else None
            verify_rows.append({"case_id": cid, "arm": arm, "called": True,
                                "status": status, "cited_frozen_ref": cited,
                                "correct_closure": status == "supported" and cited,
                                "response": content})
    by_action = {}
    for action in ("search", "find", "open"):
        group = [r for r in rows if r["action"] == action]
        by_action[action] = {"n": len(group),
                             "compatible": sum(r["source_compatible"] is True for r in group),
                             "useful_yes": sum(r["useful_evidence"] == "yes" for r in group),
                             "useful_partial": sum(r["useful_evidence"] == "partial" for r in group),
                             "gap_progress": sum(r["gap_effect"] != "no_progress" for r in group)}
    summary = {"selected_cases": len(selected), "retrieval_executed": len(rows),
               "retrieval_errors": len(tool_errors), "by_action": by_action,
               "retrieval_compatible": sum(r["source_compatible"] is True for r in rows),
               "retrieval_useful_yes": sum(r["useful_evidence"] == "yes" for r in rows),
               "retrieval_gap_progress": sum(r["gap_effect"] != "no_progress" for r in rows),
               "gap_effect_distribution": dict(Counter(r["gap_effect"] for r in rows)),
               "verify": {arm: {"closure_cases": 2,
                                "called": sum(r["called"] for r in verify_rows if r["arm"] == arm),
                                "correct_closure": sum(r["correct_closure"] for r in verify_rows if r["arm"] == arm)}
                          for arm in ("V0", "V1")},
               "free_closure_extra_retrieval": sum(r["uncertainty_type"] == "closure" for r in rows),
               "cache": cache(),
               "notes": "One-step local progress, not full-question accuracy; related qid/checkpoints are correlated."}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "retrieval_rows": rows,
                                                    "verify_rows": verify_rows}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cache():
    hit = miss = count = 0
    for e in events:
        if e["kind"] != "verify_response" or e["cache_usage"]["status"] != "reported":
            continue
        count += 1
        hit += e["cache_usage"]["prompt_cache_hit_tokens"]
        miss += e["cache_usage"]["prompt_cache_miss_tokens"]
    return {"reported": count, "hit_tokens": hit, "miss_tokens": miss,
            "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}


if __name__ == "__main__":
    main()
