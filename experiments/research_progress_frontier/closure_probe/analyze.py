"""Prespecified Stage A closure metrics and gate; no model reruns."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "review_cases.json").read_text())


def parse(raw):
    choice = (raw.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    status_match = re.search(r"(?im)^\s*Status\s*:\s*(supported|refuted|open)\s*$", content)
    refs_match = re.search(r"(?im)^\s*Evidence refs\s*:\s*(.*?)\s*$", content)
    missing_match = re.search(r"(?im)^\s*Missing evidence\s*:\s*(.*?)\s*$", content)
    reason_match = re.search(r"(?im)^\s*Reason\s*:\s*(.*?)\s*$", content)
    status = status_match.group(1).lower() if status_match and choice.get("finish_reason") == "stop" else None
    ref_text = refs_match.group(1).strip() if refs_match else None
    refs = [] if ref_text is None or ref_text.lower() == "none" else [r.strip(" []`") for r in ref_text.split(",")]
    return {"status": status, "finish_reason": choice.get("finish_reason"),
            "evidence_refs": refs, "ref_field_present": ref_text is not None,
            "missing_evidence": missing_match.group(1).strip() if missing_match else None,
            "reason": reason_match.group(1).strip() if reason_match else None,
            "content": content}


def main():
    events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    responses = {e["case_id"]: e for e in events if e["kind"] == "api_response"}
    errors = {e["case_id"]: e for e in events if e["kind"] == "api_error"}
    if len(responses) + len(errors) != len(CASES) or set(responses) & set(errors):
        raise ValueError("Missing or duplicate completed case")
    rows = []
    for case in CASES:
        cid = case["case_id"]
        parsed = parse(responses[cid]["response"]) if cid in responses else None
        label = case["review_label"]
        status = parsed["status"] if parsed else None
        refs = {x["ref"] for x in case["visible_evidence"]}
        bad_refs = [r for r in parsed["evidence_refs"] if r not in refs] if parsed else []
        rows.append({"case_id": cid, "qid": case["qid"], "checkpoint": case["checkpoint"],
                     "case_type": case["case_type"], "ambiguity": case["ambiguity"],
                     "review_label": label, "model_status": status, "agree": status == label,
                     "false_close": label == "open" and status in ("supported", "refuted"),
                     "missed_closure": label in ("supported", "refuted") and status == "open",
                     "invalid_refs": bad_refs, "api_error": errors[cid]["error_type"] if cid in errors else None,
                     "parsed": parsed})
    by_label = {label: {"n": sum(r["review_label"] == label for r in rows),
                        "correct": sum(r["review_label"] == label and r["agree"] for r in rows)}
                for label in ("supported", "refuted", "open")}
    stale = [r for r in rows if r["case_type"] == "stale_gap"]
    stale_low = [r for r in stale if r["ambiguity"] == "low"]
    confusion = {label: dict(Counter(r["model_status"] or "invalid" for r in rows if r["review_label"] == label))
                 for label in by_label}
    hit = miss = usage_reported = 0
    for e in responses.values():
        usage = e["cache_usage"]
        if usage["status"] == "reported":
            usage_reported += 1
            hit += usage["prompt_cache_hit_tokens"]
            miss += usage["prompt_cache_miss_tokens"]
    overall = sum(r["agree"] for r in rows) / len(rows)
    false_close = sum(r["false_close"] for r in rows) / by_label["open"]["n"]
    stale_count = sum(r["agree"] for r in stale)
    gate = {"overall_ge_80pct": overall >= .8,
            "false_close_le_10pct": false_close <= .1,
            "stale_closure_ge_4of5": stale_count >= 4}
    summary = {"total": len(rows), "qids": len({r["qid"] for r in rows}),
               "api_responses": len(responses), "api_errors": len(errors),
               "valid_statuses": sum(r["model_status"] is not None for r in rows),
               "agreement": {"correct": sum(r["agree"] for r in rows), "rate": overall},
               "by_label": by_label, "confusion": confusion,
               "false_close": {"n": sum(r["false_close"] for r in rows), "denominator": by_label["open"]["n"],
                               "rate": false_close},
               "missed_closure": {"n": sum(r["missed_closure"] for r in rows),
                                  "denominator": by_label["supported"]["n"] + by_label["refuted"]["n"]},
               "stale_gap": {"correct": stale_count, "n": len(stale),
                             "low_ambiguity_correct": sum(r["agree"] for r in stale_low),
                             "low_ambiguity_n": len(stale_low)},
               "invalid_ref_cases": [r["case_id"] for r in rows if r["invalid_refs"]],
               "cache": {"usage_reported": usage_reported, "hit_tokens": hit, "miss_tokens": miss,
                         "weighted_hit_rate": hit / (hit + miss) if hit + miss else None},
               "gate": gate, "stage_A_pass": all(gate.values()),
               "caveat": "Single responses, single-reviewer labels, repeated claim/checkpoint siblings; not independent trials."}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows},
                                                   ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
