"""Paired R1 action accounting against frozen prefix-only qualification labels."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P1_EVENTS = ROOT / "experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl"


def read(path):
    return [json.loads(line) for line in path.open()]


def analyze_arm(q, seq, arm, annotation, packet, event):
    valid = bool(event and event.get("validation") == "valid")
    calls = (event.get("parsed_calls") or []) if valid else []
    by_window = {d["preview_ref"]: d["doc_ref"] for d in packet["observed_documents"]}
    target = annotation["candidate_target"]
    if target.startswith("W"):
        target = by_window.get(target, target)
    details = []
    for c in calls:
        name, args = c["name"], c["arguments"]
        doc = args.get("doc_ref") if name == "find" else by_window.get(args.get("window_ref")) if name == "open" else None
        scope = {"search": "corpus", "find": "document", "open": "window"}.get(name)
        details.append({"name": name, "arguments": args, "doc_ref": doc,
                        "scope_allowed": scope in annotation["acceptable_next_scopes"],
                        "inspects_candidate": doc is not None and doc == target})
    inspected = [c for c in details if c["name"] in ("find", "open")]
    return {"cell": f"{q}:{seq}:{arm}", "qid": q, "seq": seq, "arm": arm,
            "status": annotation["status"], "candidate_target": annotation["candidate_target"],
            "response": bool(event), "validation": event.get("validation") if event else None,
            "finish_reason": event.get("raw_finish_reason") if event else None,
            "calls": details, "first_call": details[0]["name"] if details else None,
            "mixed_batch": len({c["name"] for c in details}) > 1,
            "candidate_inspected": any(c["inspects_candidate"] for c in inspected),
            "candidate_first_call": bool(details and details[0]["inspects_candidate"]),
            "any_inspection": bool(inspected), "all_scopes_allowed": all(c["scope_allowed"] for c in details),
            "any_disallowed_scope": any(not c["scope_allowed"] for c in details),
            "search_calls": sum(c["name"] == "search" for c in details),
            "inspection_calls": len(inspected),
            "natural_stop": valid and not details and event.get("raw_finish_reason") == "stop" if event else False}


def main():
    selection = json.loads((HERE / "SELECTION.json").read_text())["cells"]
    annotations = {(a["qid"], a["seq"]): a for a in json.loads((HERE / "ANNOTATIONS.json").read_text())["rows"]}
    packets = {(p["qid"], p["seq"]): p for p in json.loads((HERE / "review_packets.json").read_text())}
    old, new = read(P1_EVENTS), read(HERE / "events.jsonl")
    rows = []
    pairs = []
    for x in selection:
        q, seq = x["qid"], x["seq"]
        baseline = next((e for e in old if e["kind"] == "api_response" and e["cell"] == f"{q}:{seq}:H1"), None)
        response = next((e for e in new if e["kind"] == "actor_response" and e["cell"] == f"{q}:{seq}:Q1"), None)
        h0 = analyze_arm(q, seq, "H0", annotations[(q, seq)], packets[(q, seq)], baseline)
        h1 = analyze_arm(q, seq, "H1", annotations[(q, seq)], packets[(q, seq)], response)
        rows.extend((h0, h1))
        pairs.append({"qid": q, "seq": seq, "status": h0["status"],
                      "target": h0["candidate_target"],
                      "h0_candidate_inspected": h0["candidate_inspected"],
                      "h1_candidate_inspected": h1["candidate_inspected"],
                      "h0_calls": [(c["name"], c["doc_ref"]) for c in h0["calls"]],
                      "h1_calls": [(c["name"], c["doc_ref"]) for c in h1["calls"]],
                      "action_changed": [(c["name"], c["doc_ref"]) for c in h0["calls"]] !=
                                        [(c["name"], c["doc_ref"]) for c in h1["calls"]]})
    aggregate = {}
    for status in ("no_target", "hypothesis_only", "inspectable"):
        for arm in ("H0", "H1"):
            group = [r for r in rows if r["status"] == status and r["arm"] == arm]
            actions = Counter(c["name"] for r in group for c in r["calls"])
            aggregate[f"{status}:{arm}"] = {"cells": len(group),
                "responses": sum(r["response"] for r in group),
                "valid": sum(r["validation"] == "valid" for r in group),
                "candidate_inspected_cells": sum(r["candidate_inspected"] for r in group),
                "candidate_first_call_cells": sum(r["candidate_first_call"] for r in group),
                "any_inspection_cells": sum(r["any_inspection"] for r in group),
                "all_scopes_allowed_cells": sum(r["all_scopes_allowed"] for r in group),
                "disallowed_scope_cells": sum(r["any_disallowed_scope"] for r in group),
                "natural_stops": sum(r["natural_stop"] for r in group),
                "mixed_batches": sum(r["mixed_batch"] for r in group),
                "actions": dict(actions)}
    output = {"aggregate": aggregate, "pairs": pairs, "rows": rows,
              "interpretation": "Candidate inspection maps prefix W to D. For hypothesis_only, candidate inspection is a harmful-target-follow proxy; a separate source observation would be required to assess evidence gain. Scope_allowed is not a source-quality judgment. H0 is historical P1 broad-plan handoff; H1 adds reviewed qualification card."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"aggregate": aggregate, "pairs": pairs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
