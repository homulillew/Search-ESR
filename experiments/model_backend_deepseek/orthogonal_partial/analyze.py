"""M3 paired trajectory-shape accounting on the selected four checkpoints."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QWEN = ROOT / "experiments/search_find_v3b/orthogonal_search/events.jsonl"
DEEPSEEK = HERE / "events.jsonl"


def read(path):
    return [json.loads(line) for line in path.open()]


def analyze_cell(events, cell, model, arm):
    sub = [e for e in events if e.get("cell") == cell]
    end = next((e for e in sub if e["kind"] == "cell_end"), {})
    tool = [e for e in sub if e["kind"] == "tool_start"]
    results = [e for e in sub if e["kind"] == "tool_result"]
    actions = Counter(e["name"] for e in tool)
    no_gain_decisions = set()
    new_doc_hits = 0
    for e in results:
        if e["name"] != "search":
            continue
        hits = e["result"].get("results") or []
        if arm == "P1":
            new = sum(x.get("previously_discovered") is False for x in hits)
            # Historical and DeepSeek P1 both expose only metadata for old hits.
            if not new:
                no_gain_decisions.add(e["decision"])
            new_doc_hits += new
        else:
            new_doc_hits += sum(x.get("previously_discovered") is False for x in hits)
    names_by_decision = {}
    for e in tool:
        names_by_decision.setdefault(e["decision"], []).append(e["name"])
    next_find = sum("find" in names_by_decision.get(d + 1, []) for d in no_gain_decisions)
    next_search = sum("search" in names_by_decision.get(d + 1, []) for d in no_gain_decisions)
    finds = [e for e in results if e["name"] == "find"]
    return {"cell": cell, "model": model, "arm": arm,
            "status": end.get("status", "missing_cell_end"),
            "decisions": len([e for e in sub if e["kind"] == "api_response"]),
            "actions": dict(actions), "new_document_hits": new_doc_hits,
            "no_gain_search_decisions": len(no_gain_decisions),
            "next_decision_find_after_no_gain": next_find,
            "next_decision_search_after_no_gain": next_search,
            "find_results": [{"decision": e["decision"],
                              "status": e["result"].get("status"),
                              "doc_ref": e["result"].get("doc_ref"),
                              "match_count": len(e["result"].get("matches") or [])}
                             for e in finds]}


def main():
    selection = json.loads((HERE / "SELECTION.json").read_text())["cells"]
    qe, de = read(QWEN), read(DEEPSEEK)
    rows = []
    for x in selection:
        for arm in ("P0", "P1"):
            base = f"{x['qid']}:{x['seq']}:{arm}"
            rows.append(analyze_cell(qe, base, "qwen3.7-flash", arm))
            rows.append(analyze_cell(de, base + ":deepseek-flash", "deepseek-flash", arm))
    aggregates = {}
    for model in ("qwen3.7-flash", "deepseek-flash"):
        aggregates[model] = {}
        for arm in ("P0", "P1"):
            group = [r for r in rows if r["model"] == model and r["arm"] == arm]
            counts = Counter()
            for r in group:
                counts.update(r["actions"])
            aggregates[model][arm] = {"cells": len(group), "actions": dict(counts),
                "natural_stops": sum(r["status"] == "natural_stop" for r in group),
                "new_document_hits": sum(r["new_document_hits"] for r in group),
                "no_gain_search_decisions": sum(r["no_gain_search_decisions"] for r in group),
                "next_decision_find_after_no_gain": sum(r["next_decision_find_after_no_gain"] for r in group),
                "next_decision_search_after_no_gain": sum(r["next_decision_search_after_no_gain"] for r in group)}
    result = {"rows": rows, "aggregates": aggregates,
              "metric_note": "A NoGain decision contains at least one P1 Search call with no new document; another call in the same batch may gain one. Next-decision metrics count decisions, not tool calls; current-batch calls cannot react to their own results."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(aggregates, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
