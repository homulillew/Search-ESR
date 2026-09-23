"""Paired 2x2 trajectory, no-gain transition, and inspection review accounting."""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/model_backend_deepseek"


def read(path):
    return [json.loads(line) for line in path.open()]


def source_preview(result):
    if result.get("matches"):
        return "\n".join(x.get("text", "") for x in result["matches"][:2])[:1800]
    return (result.get("text") or "")[:1800]


def plan_scope(fields):
    raw = (fields or {}).get("Best scope", "")
    match = re.search(r"\b(corpus|document|window|stop)\b", raw, re.I)
    return match.group(1).lower() if match else None


def cell_analysis(events, cell, q, seq, harness, handoff, label, scores, cards):
    sub = [e for e in events if e.get("cell") == cell]
    end = next((e for e in sub if e["kind"] == "cell_end"), {})
    starts = [e for e in sub if e["kind"] == "tool_start"]
    results = [e for e in sub if e["kind"] == "tool_result"]
    responses = [e for e in sub if e["kind"] in ("actor_response", "api_response")]
    requests = [e for e in sub if e["kind"] in ("actor_request", "api_request")]
    plans = {e["decision"]: e.get("current_plan") for e in requests if e["kind"] == "actor_request"}
    names_by_decision = {}
    for e in starts:
        names_by_decision.setdefault(e["decision"], []).append(e["name"])
    response_decisions = {e["decision"] for e in responses}
    no_gain_calls = 0
    no_gain_decisions = set()
    new_hits = 0
    for e in results:
        if e["name"] != "search":
            continue
        hits = e["result"].get("results") or []
        new = sum(x.get("previously_discovered") is False for x in hits)
        new_hits += new
        if harness == "P1" and new == 0:
            no_gain_calls += 1
            no_gain_decisions.add(e["decision"])
    eligible = [d for d in no_gain_decisions if d + 1 in response_decisions]
    compatible = gain = reviewed = 0
    inspections = []
    for e in results:
        if e["name"] not in ("find", "open"):
            continue
        identifier = f"{cell}:{e['decision']}:{e['call_index']}"
        result = e["result"]
        need = (plans.get(e["decision"]) or {}).get("Current unresolved need", label["current_need"])
        card = {"id": identifier, "cell": cell, "qid": q, "seq": seq,
                "harness": harness, "handoff": handoff, "decision": e["decision"],
                "name": e["name"], "arguments": next((x["arguments"] for x in starts
                  if x["decision"] == e["decision"] and x["call_index"] == e["call_index"]), {}),
                "active_need": need, "result_status": result.get("status"),
                "doc_ref": result.get("doc_ref"), "observed_excerpt": source_preview(result),
                "review_instruction": "Judge D# compatibility with this need and direct evidence gain from this observation only; entity overlap is insufficient."}
        cards.append(card)
        score = scores.get(identifier)
        if score:
            if score.get("source_compatible") not in (True, False, None) or \
               score.get("useful_evidence") not in (True, False, None) or not score.get("reason"):
                raise ValueError(f"Incomplete inspection score: {identifier}")
            reviewed += 1
            compatible += score["source_compatible"] is True
            gain += score["useful_evidence"] is True
        inspections.append({"id": identifier, "doc_ref": result.get("doc_ref"),
                            "source_compatible": score.get("source_compatible") if score else None,
                            "useful_evidence": score.get("useful_evidence") if score else None})
    realized = conflict = 0
    plan_decisions = 0
    if handoff == "H1":
        for d in response_decisions:
            scope = plan_scope(plans.get(d))
            if not scope:
                continue
            plan_decisions += 1
            names = names_by_decision.get(d, [])
            intended = {"corpus": "search", "document": "find", "window": "open"}.get(scope)
            match = not names if scope == "stop" else intended in names
            realized += bool(match)
            conflict += bool(match and (bool(names) if scope == "stop" else any(n != intended for n in names)))
    return {"cell": cell, "qid": q, "seq": seq, "harness": harness, "handoff": handoff,
            "status": end.get("status", "missing_cell_end"), "actor_responses": len(responses),
            "planner_responses": sum(e["kind"] == "planner_response" for e in sub),
            "actions": dict(Counter(e["name"] for e in starts)), "new_document_hits": new_hits,
            "no_gain_search_calls": no_gain_calls, "no_gain_decisions_with_followup": len(eligible),
            "next_decision_inspect_after_no_gain": sum(any(n in ("find", "open") for n in names_by_decision.get(d + 1, [])) for d in eligible),
            "next_decision_search_after_no_gain": sum("search" in names_by_decision.get(d + 1, []) for d in eligible),
            "plan_decisions": plan_decisions, "plan_realized_decisions": realized,
            "plan_realized_with_conflict": conflict,
            "inspections": inspections, "inspections_reviewed": reviewed,
            "compatible_inspections": compatible, "useful_evidence_inspections": gain}


def main():
    selection = json.loads((OLD / "orthogonal_partial/SELECTION.json").read_text())["cells"]
    labels = {(r["qid"], r["seq"]): r for r in json.loads((ROOT / "experiments/model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json").read_text())["rows"]}
    h0, h1 = read(OLD / "orthogonal_partial/events.jsonl"), read(HERE / "events.jsonl")
    score_path = HERE / "inspection_scores.json"
    scores = json.loads(score_path.read_text()) if score_path.exists() else {}
    rows = []
    cards = []
    for x in selection:
        q, seq = x["qid"], x["seq"]
        for harness in ("P0", "P1"):
            rows.append(cell_analysis(h0, f"{q}:{seq}:{harness}:deepseek-flash",
                                      q, seq, harness, "H0", labels[(q, seq)], scores, cards))
            rows.append(cell_analysis(h1, f"{q}:{seq}:{harness}H1",
                                      q, seq, harness, "H1", labels[(q, seq)], scores, cards))
    if set(scores) - {c["id"] for c in cards}:
        raise ValueError("Unknown inspection score IDs")
    (HERE / "inspection_review_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n")
    aggregates = {}
    for harness in ("P0", "P1"):
        for handoff in ("H0", "H1"):
            group = [r for r in rows if r["harness"] == harness and r["handoff"] == handoff]
            names = Counter()
            for r in group:
                names.update(r["actions"])
            aggregates[harness + handoff] = {"cells": len(group), "actions": dict(names),
              "natural_stops": sum(r["status"] == "natural_stop" for r in group),
              "api_or_planner_failures": sum(r["status"] in ("actor_api_error", "planner_api_error", "planner_invalid", "api_error") for r in group),
              "new_document_hits": sum(r["new_document_hits"] for r in group),
              "no_gain_search_calls": sum(r["no_gain_search_calls"] for r in group),
              "no_gain_decisions_with_followup": sum(r["no_gain_decisions_with_followup"] for r in group),
              "next_decision_inspect_after_no_gain": sum(r["next_decision_inspect_after_no_gain"] for r in group),
              "next_decision_search_after_no_gain": sum(r["next_decision_search_after_no_gain"] for r in group),
              "plan_decisions": sum(r["plan_decisions"] for r in group),
              "plan_realized_decisions": sum(r["plan_realized_decisions"] for r in group),
              "plan_realized_with_conflict": sum(r["plan_realized_with_conflict"] for r in group),
              "inspections": sum(len(r["inspections"]) for r in group),
              "inspections_reviewed": sum(r["inspections_reviewed"] for r in group),
              "compatible_inspections": sum(r["compatible_inspections"] for r in group),
              "useful_evidence_inspections": sum(r["useful_evidence_inspections"] for r in group)}
    result = {"rows": rows, "aggregates": aggregates,
      "metric_note": "NoGain is a P1 Search call with zero new D#. Transition denominator includes only no-gain decisions with a subsequent Actor response. Parallel same-batch calls cannot react to their own result. Manual source/evidence labels refer only to visible source text and current need."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(aggregates, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
