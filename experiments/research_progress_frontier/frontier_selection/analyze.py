"""Stage B selected-frontier metrics with frozen reviewer rubric."""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "review_cases.json").read_text())


def parse(raw):
    choice = (raw.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    gap = re.search(r"(?im)^\s*Active gap\s*:\s*(G[1-4])\b", text)
    why = re.search(r"(?im)^\s*Why now\s*:\s*(.+)$", text)
    source_type = re.search(r"(?im)^\s*Expected source type\s*:\s*(.+)$", text)
    known = re.search(r"(?im)^\s*Known suitable source\s*:\s*(none|D\d+)\b", text)
    return {"gap": gap.group(1) if gap and choice.get("finish_reason") == "stop" else None,
            "why_now": why.group(1).strip() if why else None,
            "source_type": source_type.group(1).strip() if source_type else None,
            "known_source": known.group(1) if known else None,
            "finish_reason": choice.get("finish_reason"), "content": text}


def main():
    events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    responses = {e["case_id"]: e for e in events if e["kind"] == "api_response"}
    errors = {e["case_id"]: e for e in events if e["kind"] == "api_error"}
    semantic_path = HERE / "semantic_scores.json"
    if not semantic_path.exists():
        raise FileNotFoundError("Complete post-call source-type review before Stage B gate calculation")
    semantic = json.loads(semantic_path.read_text())
    if set(semantic) != {c["case_id"] for c in CASES} or len(responses) + len(errors) != len(CASES):
        raise ValueError("Missing review or model result")
    rows = []
    for case in CASES:
        cid = case["case_id"]
        parsed = parse(responses[cid]["response"]) if cid in responses else None
        gap = parsed["gap"] if parsed else None
        score = semantic[cid]
        if not isinstance(score.get("source_type_compatible"), bool) or \
           not isinstance(score.get("known_source_valid"), bool) or \
           not isinstance(score.get("premature_commitment_text"), bool) or not score.get("reason"):
            raise ValueError(cid)
        accepted = gap in case["acceptable_active_gaps"]
        closed = gap in case["unacceptable_closed_gaps"]
        premature = gap in case["unsupported_hypothesis_gaps"] or score["premature_commitment_text"]
        directory_refs = {d["doc_ref"] for d in case["source_directory"]}
        source_exists = bool(parsed and (parsed["known_source"] == "none" or
                                         parsed["known_source"] in directory_refs))
        rows.append({"case_id": cid, "qid": case["qid"], "ambiguity": case["ambiguity"],
                     "selected_gap": gap, "acceptable": accepted, "closed_gap_reselected": closed,
                     "premature_downstream": premature,
                     "source_type_compatible": score["source_type_compatible"],
                     "known_source_valid": score["known_source_valid"],
                     "source_ref_exists_or_none": source_exists,
                     "review_reason": score["reason"], "parsed": parsed,
                     "api_error": errors[cid]["error_type"] if cid in errors else None})
    n = len(rows)
    acceptable = sum(r["acceptable"] for r in rows)
    closed = sum(r["closed_gap_reselected"] for r in rows)
    premature = sum(r["premature_downstream"] for r in rows)
    low = [r for r in rows if r["ambiguity"] == "low"]
    gate = {"acceptable_ge_75pct": acceptable / n >= .75,
            "closed_reselection_le_10pct": closed / n <= .10,
            "premature_downstream_le_15pct": premature / n <= .15}
    hit = miss = reported = 0
    for e in responses.values():
        usage = e["cache_usage"]
        if usage["status"] == "reported":
            reported += 1
            hit += usage["prompt_cache_hit_tokens"]
            miss += usage["prompt_cache_miss_tokens"]
    summary = {"cases": n, "qids": len({r["qid"] for r in rows}),
               "responses": len(responses), "api_errors": len(errors),
               "acceptable": {"n": acceptable, "rate": acceptable/n},
               "closed_gap_reselection": {"n": closed, "rate": closed/n},
               "premature_downstream": {"n": premature, "rate": premature/n},
               "source_type_compatible": sum(r["source_type_compatible"] for r in rows),
               "known_source_valid": sum(r["known_source_valid"] for r in rows),
               "source_ref_exists_or_none": sum(r["source_ref_exists_or_none"] for r in rows),
               "low_ambiguity": {"n": len(low), "acceptable": sum(r["acceptable"] for r in low),
                                 "closed": sum(r["closed_gap_reselected"] for r in low),
                                 "premature": sum(r["premature_downstream"] for r in low)},
               "cache": {"usage_reported": reported, "hit_tokens": hit, "miss_tokens": miss,
                         "weighted_hit_rate": hit/(hit+miss) if hit+miss else None},
               "gate": gate, "stage_B_pass": all(gate.values()),
               "caveat": "Only eight one-per-qid clean reviewer-authored views; no full history or tool observations."}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows},
                                                   ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
