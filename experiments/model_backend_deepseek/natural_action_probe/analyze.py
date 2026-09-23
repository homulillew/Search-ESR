"""Mechanical M2 planning-to-action accounting against frozen Qwen cells."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/model_backend_atria"


def main():
    frozen = json.loads((HERE / "freeze.json").read_text())
    m1 = json.loads((STUDY / "planning_probe/mechanical_summary.json").read_text())
    planning = {r["cell"]: r for r in m1["rows"]}
    def read(path):
        return [json.loads(line) for line in path.open()]
    qevents = read(OLD / "natural_action_probe/events.jsonl")
    devents = read(HERE / "events.jsonl")
    events = qevents + devents
    responses = {e["cell"]: e for e in events if e["kind"] == "api_response"}
    errors = {e["cell"]: e for e in events if e["kind"] == "api_error"}
    rows = []
    for q, seq in frozen["selection"]:
        for model in ("qwen3.7-flash", frozen["model"]):
            cell = f"{q}:{seq}:{model}"
            event = responses.get(cell)
            planned = planning[cell].get("parsed_scope")
            if event:
                name = event["action"]
                calls = event.get("parsed_calls") or []
                target = (calls[0]["arguments"].get("doc_ref") if name == "find" else
                          calls[0]["arguments"].get("window_ref") if name == "open" else None)
                row = {"qid": q, "seq": seq, "model": model, "cell": cell,
                       "planning_scope": planned, "action": name,
                       "action_scope": {"search": "corpus", "find": "document",
                                        "open": "window", "stop": "stop"}.get(name),
                       "target_ref": target, "validation": event["validation"],
                       "raw_finish_reason": event["raw_finish_reason"],
                       "scope_realized": planned == "document" and name == "find",
                       "policy_realization_failure": planned == "document" and name == "search"}
            else:
                row = {"qid": q, "seq": seq, "model": model, "cell": cell,
                       "planning_scope": planned, "action": "api_error",
                       "action_scope": None, "target_ref": None,
                       "validation": errors.get(cell, {}).get("error_type", "missing"),
                       "scope_realized": False, "policy_realization_failure": False}
            rows.append(row)
    aggregates = {}
    for model in ("qwen3.7-flash", frozen["model"]):
        group = [r for r in rows if r["model"] == model]
        doc = [r for r in group if r["planning_scope"] == "document"]
        aggregates[model] = {"cells": len(group),
                             "actions": dict(Counter(r["action"] for r in group)),
                             "document_plan_count": len(doc),
                             "document_scope_realized": sum(r["scope_realized"] for r in doc),
                             "document_to_search_failures": sum(r["policy_realization_failure"] for r in doc)}
    paired = []
    for q, seq in frozen["selection"]:
        qrow, drow = (next(r for r in rows if r["cell"] == f"{q}:{seq}:{model}")
                      for model in ("qwen3.7-flash", frozen["model"]))
        paired.append({"qid": q, "seq": seq,
                       "qwen_planning_scope": qrow["planning_scope"], "qwen_action": qrow["action"],
                       "deepseek_planning_scope": drow["planning_scope"], "deepseek_action": drow["action"]})
    result = {"selection_rule": frozen["selection_rule"], "rows": rows,
              "paired": paired, "aggregates": aggregates,
              "scope_realization_denominator": "M1 document plans among M2 selected cells",
              "policy_realization_failure": "M1 document plan followed by single valid search"}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"paired": paired, "aggregates": aggregates}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
