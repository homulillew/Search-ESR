"""M4 relation, belief, and stop accounting against the frozen Qwen arm."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_atria.evidence_update.analyze import parse

HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/model_backend_atria/evidence_update"
MODEL = "deepseek-flash"


def main():
    cases = json.loads((OLD / "cases.json").read_text())["cases"]
    old = [json.loads(line) for line in (OLD / "events.jsonl").open()]
    new = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    events = old + new
    responses = {e["cell"]: e for e in events if e["kind"] == "api_response"
                 and e["cell"].endswith((":qwen3.7-flash", ":" + MODEL))}
    errors = {e["cell"]: e for e in events if e["kind"] == "api_error"
              and e["cell"].endswith((":qwen3.7-flash", ":" + MODEL))}
    scores_path = HERE / "semantic_scores.json"
    scores = json.loads(scores_path.read_text()) if scores_path.exists() else {}
    rows = []
    for case in cases:
        for arm in ("E0", "E1"):
            for model in ("qwen3.7-flash", MODEL):
                cell = f"{case['case_id']}:{arm}:{model}"
                event = responses.get(cell)
                if event:
                    choice = (event["response"].get("choices") or [{}])[0]
                    content = (choice.get("message") or {}).get("content") or ""
                    parsed = parse(content)
                    # The frozen instruction omits the colon after this field.
                    # The historical parser required one, so expose the literal
                    # yes/no separately for both arms without changing the rubric.
                    flag = re.search(r"(?im)^\s*Did the candidate change\?\s*:?\s*(yes|no)\b", content)
                    parsed["observed_candidate_changed"] = flag.group(1).lower() if flag else None
                    score = scores.get(cell, {}) if arm == "E1" else {}
                    row = {"cell": cell, "case_id": case["case_id"], "arm": arm,
                           "model": model, "expected_relation": case["expected_relation"],
                           "content": content, "finish_reason": choice.get("finish_reason"),
                           **parsed,
                           "relation_accurate": parsed["parsed_relation"] == case["expected_relation"]
                                                if arm == "E1" else None,
                           "stop_calibrated": parsed["parsed_scope"] not in (None, "stop")
                                              if arm == "E1" else None,
                           "belief_update_correct": score.get("belief_update_correct"),
                           "unsupported_override": score.get("unsupported_override")}
                else:
                    row = {"cell": cell, "case_id": case["case_id"], "arm": arm,
                           "model": model, "expected_relation": case["expected_relation"],
                           "error": errors.get(cell, {}).get("error_type", "missing_response"),
                           "parsed_relation": None, "parsed_scope": None,
                           "relation_accurate": None, "stop_calibrated": None,
                           "belief_update_correct": None, "unsupported_override": None}
                rows.append(row)
    e1 = {r["cell"] for r in rows if r["arm"] == "E1" and "content" in r}
    if set(scores) - e1:
        raise ValueError("Scores include absent or non-E1 cells")
    for cell, score in scores.items():
        if score.get("belief_update_correct") not in (True, False) or \
           score.get("unsupported_override") not in (True, False) or not score.get("reason"):
            raise ValueError(f"Incomplete score: {cell}")
    aggregates = {}
    for model in ("qwen3.7-flash", MODEL):
        group = [r for r in rows if r["model"] == model and r["arm"] == "E1"]
        aggregates[model] = {"e1_responses": sum("content" in r for r in group),
                             "e1_relation_accurate": sum(r["relation_accurate"] is True for r in group),
                             "e1_belief_update_correct": sum(r["belief_update_correct"] is True for r in group),
                             "e1_semantic_scored": sum(r["cell"] in scores for r in group),
                             "e1_unsupported_overrides": sum(r["unsupported_override"] is True for r in group),
                             "e1_stop_calibrated": sum(r["stop_calibrated"] is True for r in group)}
    paired = []
    for case in cases:
        for arm in ("E0", "E1"):
            item = {"case_id": case["case_id"], "arm": arm,
                    "expected_relation": case["expected_relation"] if arm == "E1" else None}
            for model, label in (("qwen3.7-flash", "qwen"), (MODEL, "deepseek")):
                row = next(r for r in rows if r["cell"] == f"{case['case_id']}:{arm}:{model}")
                item[label + "_relation"] = row["parsed_relation"]
                item[label + "_scope"] = row["parsed_scope"]
                item[label + "_error"] = row.get("error")
            paired.append(item)
    result = {"rows": rows, "paired": paired, "aggregates": aggregates,
              "metric_note": "E1 exact four-way relation; E0 descriptive; all E1 snippets are partial for full-question stop calibration",
              "change_flag_parse_note": "Frozen prompt says 'Did the candidate change? yes | no' without a colon; historical parser returns null. observed_candidate_changed accepts an optional colon, equally for both models."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"paired": paired, "aggregates": aggregates}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
