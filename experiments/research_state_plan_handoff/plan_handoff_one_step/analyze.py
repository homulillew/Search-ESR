"""Paired plan-realization accounting without collapsing mixed tool batches."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/model_backend_deepseek"
ANNOTATIONS = ROOT / "experiments/model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json"


def read(path):
    return [json.loads(line) for line in path.open()]


def action_row(q, seq, arm, event, planned, plausible):
    cell = f"{q}:{seq}:{arm}"
    if not event or event["kind"] != "api_response":
        return {"cell": cell, "qid": q, "seq": seq, "arm": arm,
                "planned_scope": planned.get("parsed_scope"), "planned_target": planned.get("parsed_target"),
                "response": False, "error": (event or {}).get("error_type", "missing_response"),
                "valid": False, "first_call": None, "all_calls": [],
                "contains_plan_consistent_action": False, "contains_conflicting_action": False,
                "document_plan_realized": False, "target_realized": False,
                "source_compatible_find": None, "search_despite_non_corpus": False}
    valid = event.get("validation") == "valid"
    calls = event.get("parsed_calls") or [] if valid else []
    names = [c["name"] for c in calls]
    scope = planned.get("parsed_scope")
    intended = {"corpus": "search", "document": "find", "window": "open"}.get(scope)
    stop = valid and not calls and event.get("raw_finish_reason") == "stop"
    consistent = stop if scope == "stop" else valid and intended in names
    conflicting = bool(names) if scope == "stop" else any(n != intended for n in names)
    finds = [c["arguments"].get("doc_ref") for c in calls if c["name"] == "find"]
    target = planned.get("parsed_target")
    return {"cell": cell, "qid": q, "seq": seq, "arm": arm,
            "planned_scope": scope, "planned_target": target,
            "plan_target_prefix_compatible": planned.get("target_compatible"),
            "response": True, "valid": valid, "validation": event.get("validation"),
            "raw_finish_reason": event.get("raw_finish_reason"),
            "first_call": names[0] if names else None, "all_calls": names,
            "batch_size": len(names), "mixed_batch": len(set(names)) > 1,
            "contains_plan_consistent_action": bool(consistent),
            "contains_conflicting_action": bool(conflicting),
            "document_plan_realized": scope == "document" and valid and bool(finds),
            "first_call_document_realized": scope == "document" and valid and bool(names) and names[0] == "find",
            "find_targets": finds,
            "target_realized": scope == "document" and valid and bool(target) and target in finds,
            "source_compatible_find": any(d in plausible for d in finds) if finds else None,
            "search_despite_non_corpus": scope != "corpus" and "search" in names}


def main():
    frozen = json.loads((HERE / "freeze.json").read_text())
    m1 = json.loads((OLD / "planning_probe/mechanical_summary.json").read_text())
    labels = {(r["qid"], r["seq"]): r for r in json.loads(ANNOTATIONS.read_text())["rows"]}
    plans = {(r["qid"], r["seq"]): r for r in m1["rows"] if r["model"] == "deepseek-flash"}
    h0 = read(OLD / "natural_action_probe/events.jsonl")
    h1 = read(HERE / "events.jsonl")
    rows = []
    for q, seq in frozen["cases"]:
        p = plans[(q, seq)]
        plausible = labels[(q, seq)]["plausible_document_refs"]
        for arm, events, key in (("H0", h0, f"{q}:{seq}:deepseek-flash"),
                                 ("H1", h1, f"{q}:{seq}:H1")):
            response = next((e for e in events if e["kind"] == "api_response" and e["cell"] == key), None)
            error = next((e for e in events if e["kind"] == "api_error" and e["cell"] == key), None)
            rows.append(action_row(q, seq, arm, response or error, p, plausible))
    aggregates = {}
    for arm in ("H0", "H1"):
        group = [r for r in rows if r["arm"] == arm]
        doc = [r for r in group if r["planned_scope"] == "document"]
        noncorpus = [r for r in group if r["planned_scope"] != "corpus"]
        actions = Counter(c for r in group for c in r["all_calls"])
        aggregates[arm] = {"cells": len(group), "responses": sum(r["response"] for r in group),
          "valid_batches": sum(r["valid"] for r in group), "all_calls": dict(actions),
          "mixed_batches": sum(r.get("mixed_batch", False) for r in group),
          "scope_realized": sum(r["contains_plan_consistent_action"] for r in group),
          "scope_realized_with_conflict": sum(r["contains_plan_consistent_action"] and
                                               r["contains_conflicting_action"] for r in group),
          "document_plan_count": len(doc),
          "document_plan_realized": sum(r["document_plan_realized"] for r in doc),
          "first_call_document_realized": sum(r.get("first_call_document_realized", False) for r in doc),
          "document_target_realized": sum(r["target_realized"] for r in doc),
          "document_plan_target_prefix_compatible": sum(r.get("plan_target_prefix_compatible") is True for r in doc),
          "non_corpus_plan_count": len(noncorpus),
          "search_despite_non_corpus": sum(r["search_despite_non_corpus"] for r in noncorpus),
          "source_compatible_find_cells": sum(r["source_compatible_find"] is True for r in group)}
    paired = []
    for q, seq in frozen["cases"]:
        a, b = (next(r for r in rows if r["qid"] == q and r["seq"] == seq and r["arm"] == arm)
                for arm in ("H0", "H1"))
        paired.append({"qid": q, "seq": seq, "plan_scope": a["planned_scope"],
                       "plan_target": a["planned_target"],
                       "plan_target_prefix_compatible": a.get("plan_target_prefix_compatible"),
                       "h0_calls": a["all_calls"], "h1_calls": b["all_calls"],
                       "h0_document_realized": a["document_plan_realized"],
                       "h1_document_realized": b["document_plan_realized"],
                       "h1_find_targets": b.get("find_targets", []),
                       "h1_target_realized": b["target_realized"]})
    result = {"aggregates": aggregates, "paired": paired, "rows": rows,
      "interpretation_note": "Realization is any consistent call, reported with conflicting and first-call metrics. Prefix-plausible D# is a source-quality proxy, not measured evidence gain; P1 executes no tools."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"aggregates": aggregates, "paired": paired}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
