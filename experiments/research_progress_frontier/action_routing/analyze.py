"""Stage C class-conditional action routing, optional Verify and argument checks."""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "review_cases.json").read_text())


def parse_a(raw):
    choice = (raw.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content") or ""
    match = re.search(r"(?im)^\s*Action\s*:\s*(search|find|open|verify|submit)\s*$", content)
    args_match = re.search(r"(?im)^\s*Arguments\s*:\s*(\{.*\})\s*$", content)
    args = None
    if args_match:
        try:
            args = json.loads(args_match.group(1))
        except json.JSONDecodeError:
            pass
    return {"action": match.group(1).lower() if match and choice.get("finish_reason") == "stop" else None,
            "arguments": args, "finish_reason": choice.get("finish_reason"), "content": content}


def parse_b(event):
    raw = event["response"]
    choice = (raw.get("choices") or [{}])[0]
    calls = event.get("parsed_calls") or []
    valid = event.get("validation") == "valid"
    action = (calls[0]["name"] if calls else "submit" if valid and
              choice.get("finish_reason") == "stop" and
              ((choice.get("message") or {}).get("content") or "").strip() else None)
    return {"action": action, "arguments": calls[0]["arguments"] if calls else None,
            "all_calls": calls, "validation": event.get("validation"),
            "finish_reason": choice.get("finish_reason"),
            "content": (choice.get("message") or {}).get("content") or ""}


def args_valid(case, arm, parsed):
    action = parsed["action"]
    args = parsed["arguments"]
    if action is None:
        return False
    if action == "submit":
        return arm == "B" or args == {}
    if not isinstance(args, dict):
        return False
    if action == "search":
        return isinstance(args.get("query"), str) and bool(args["query"].strip())
    if action == "find":
        return args.get("doc_ref") == case["known_suitable_document"] and \
               isinstance(args.get("query"), str) and bool(args["query"].strip())
    if action == "open":
        return args.get("window_ref") == case["known_relevant_window"] and \
               args.get("direction") in ("before", "after", "around")
    if action == "verify":
        refs = args.get("evidence_refs")
        return args.get("claim_ref") == case["claim_ref"] and isinstance(refs, list) and \
               bool(refs) and set(refs) <= set(case["current_evidence_refs"])
    return False


def main():
    events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    responses = {e["cell"]: e for e in events if e["kind"] == "api_response"}
    errors = {e["cell"]: e for e in events if e["kind"] == "api_error"}
    if len(responses) + len(errors) != 50 or set(responses) & set(errors):
        raise ValueError("Incomplete Stage C sample")
    rows = []
    for case in CASES:
        for arm in ("A", "B"):
            cell = f"{case['case_id']}:{arm}"
            parsed = (parse_a(responses[cell]["response"]) if arm == "A" else parse_b(responses[cell])) \
                     if cell in responses else None
            action = parsed["action"] if parsed else None
            rows.append({"cell": cell, "case_id": case["case_id"], "qid": case["qid"],
                         "arm": arm, "uncertainty_type": case["uncertainty_type_private"],
                         "expected_action": case["expected_action"], "action": action,
                         "correct": action == case["expected_action"],
                         "argument_valid": args_valid(case, arm, parsed) if parsed else False,
                         "api_error": errors[cell]["error_type"] if cell in errors else None,
                         "parsed": parsed})
    groups = {}
    for arm in ("A", "B"):
        subset = [r for r in rows if r["arm"] == arm]
        by_class = {}
        for kind in ("source", "location", "context", "closure", "complete"):
            group = [r for r in subset if r["uncertainty_type"] == kind]
            by_class[kind] = {"n": len(group), "correct": sum(r["correct"] for r in group),
                              "action_distribution": dict(Counter(r["action"] or "invalid" for r in group)),
                              "valid_arguments": sum(r["argument_valid"] for r in group)}
        groups[arm] = {"n": len(subset), "correct": sum(r["correct"] for r in subset),
                       "valid_arguments": sum(r["argument_valid"] for r in subset),
                       "api_errors": sum(r["api_error"] is not None for r in subset),
                       "by_class": by_class}
    closure_b = [r for r in rows if r["arm"] == "B" and r["uncertainty_type"] == "closure"]
    a = groups["A"]
    gate = {"overall_correct_ge_75pct": a["correct"] / a["n"] >= .75,
            "every_class_ge_60pct": all(x["correct"] / x["n"] >= .60 for x in a["by_class"].values())}
    cache = {}
    for arm in ("A", "B"):
        hit = miss = reported = 0
        for cell, event in responses.items():
            if not cell.endswith(":" + arm):
                continue
            usage = event["cache_usage"]
            if usage["status"] == "reported":
                reported += 1
                hit += usage["prompt_cache_hit_tokens"]
                miss += usage["prompt_cache_miss_tokens"]
        cache[arm] = {"usage_reported": reported, "hit_tokens": hit, "miss_tokens": miss,
                      "weighted_hit_rate": hit/(hit+miss) if hit+miss else None}
    summary = {"groups": groups,
               "optional_verify": {"n_closure": len(closure_b),
                                   "verify_first": sum(r["action"] == "verify" for r in closure_b),
                                   "other_first": dict(Counter(r["action"] or "invalid" for r in closure_b
                                                       if r["action"] != "verify"))},
               "cache": cache, "gate": gate, "stage_C_pass": all(gate.values()),
               "note": "C-A gate is prespecified; C-B free optional Verify is descriptive and does not by itself stop D. No tools executed."}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows},
                                                   ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
