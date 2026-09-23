"""P3 one-step timing accounting and prefix-only semantic review cards."""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/model_backend_deepseek"


def read(path):
    return [json.loads(line) for line in path.open()]


def fields_for(events, q, seq, arm):
    key = f"{q}:{'question' if arm == 'A1' else seq}:{arm}"
    item = next((e for e in events if e["kind"] == "planner_response" and e["cell"] == key), None)
    return item.get("fields") if item else None


def actor_for(events, q, seq, arm):
    key = f"{q}:{seq}:{arm}"
    return next((e for e in events if e["kind"] == "actor_response" and e["cell"] == key), None)


def main():
    selected = json.loads((HERE / "SELECTION.json").read_text())["cells"]
    events = read(HERE / "events.jsonl")
    broad_events = read(HERE.parent / "plan_handoff_one_step/events.jsonl")
    m1 = json.loads((OLD / "planning_probe/mechanical_summary.json").read_text())
    broad = {(r["qid"], r["seq"]): r for r in m1["rows"] if r["model"] == "deepseek-flash"}
    annotations = {(r["qid"], r["seq"]): r for r in json.loads((ROOT / "experiments/model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json").read_text())["rows"]}
    packets = {(p["qid"], p["seq"]): p for p in json.loads((ROOT / "experiments/model_backend_atria/PREFIX_ONLY_PACKETS.json").read_text())["packets"]}
    semantic_path = HERE / "semantic_review.json"
    scores = json.loads(semantic_path.read_text()) if semantic_path.exists() else {}
    rows = []
    cards = []
    for x in selected:
        q, seq = x["qid"], x["seq"]
        label = annotations[(q, seq)]
        packet = packets[(q, str(seq))]
        for arm in ("A0", "A1", "A2"):
            p = (None if arm == "A0" else fields_for(events, q, seq, arm))
            if arm == "A0":
                br = broad[(q, seq)]
                p = {"need": br["Current unresolved need"],
                     "source": br["Expected source type"],
                     "scope": br["Best scope"],
                     "target": br["Target document/window"],
                     "grounding": "prefix_broad", "basis": "visible prefix"}
                event = next((e for e in broad_events if e["kind"] == "api_response" and
                              e["cell"] == f"{q}:{seq}:H1"), None)
            else:
                event = actor_for(events, q, seq, arm)
            calls = event.get("parsed_calls") or [] if event and event.get("validation") == "valid" else []
            names = [c["name"] for c in calls]
            refs = [c["arguments"].get("doc_ref") if c["name"] == "find" else
                    c["arguments"].get("window_ref") if c["name"] == "open" else None for c in calls]
            scope_raw = (p or {}).get("scope", "")
            match = re.search(r"\b(corpus|document|window|stop)\b", scope_raw, re.I)
            scope = match.group(1).lower() if match else None
            intended = {"corpus": "search", "document": "find", "window": "open"}.get(scope)
            realized = ((not names and event.get("raw_finish_reason") == "stop") if scope == "stop" else
                        intended in names) if scope and event else None
            key = f"{q}:{seq}:{arm}"
            score = scores.get(key)
            if score:
                if score.get("premature_commitment") not in (True, False) or \
                   score.get("need_fidelity") not in (True, False) or \
                   score.get("granularity") not in ("too_broad", "appropriate", "over_fragmented", "none") or \
                   score.get("source_compatibility") not in (True, False, None) or \
                   score.get("action_matches_need") not in (True, False, None) or \
                   score.get("concrete_source_quality") not in (True, False, None) or not score.get("reason"):
                    raise ValueError(f"Incomplete semantic review: {key}")
            row = {"cell": key, "qid": q, "seq": seq, "arm": arm,
                   "plan": p, "actor_response": bool(event),
                   "validation": event.get("validation") if event else None,
                   "raw_finish_reason": event.get("raw_finish_reason") if event else None,
                   "first_call": names[0] if names else None, "all_calls": names,
                   "inspect_refs": [r for r in refs if r],
                   "mixed_batch": len(set(names)) > 1,
                   "stated_scope": scope, "stated_scope_realized": realized,
                   "plan_target_prefix_compatible": p.get("target") in label["plausible_document_refs"]
                     if p and scope == "document" else None,
                   "premature_commitment": score.get("premature_commitment") if score else None,
                   "need_fidelity": score.get("need_fidelity") if score else None,
                   "granularity": score.get("granularity") if score else None,
                   "source_compatibility": score.get("source_compatibility") if score else None,
                   "action_matches_need": score.get("action_matches_need") if score else None,
                   "concrete_source_quality": score.get("concrete_source_quality") if score else None}
            rows.append(row)
            if arm in ("A1", "A2"):
                cards.append({"cell": key, "qid": q, "seq": seq, "arm": arm,
                              "question": packet["question"],
                              "prefix_only_current_need": label["current_need"],
                              "prefix_only_expected_source_types": label["expected_source_type"],
                              "prefix_only_plausible_document_refs": label["plausible_document_refs"],
                              "visible_documents": packet["observed_documents"],
                              "last_visible_reasoning": packet["last_visible_reasoning"],
                              "plan": p, "actor_calls": [{"name": c["name"],
                                "arguments": c["arguments"]} for c in calls],
                              "review_instruction": "Use only question and current prefix information; score one need, source, unsupported commitment, action and D# quality. Do not use future trajectory or gold."})
    if set(scores) - {r["cell"] for r in rows}:
        raise ValueError("Unknown semantic review cells")
    (HERE / "semantic_review_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n")
    aggregates = {}
    for arm in ("A0", "A1", "A2"):
        group = [r for r in rows if r["arm"] == arm]
        aggregates[arm] = {"cells": len(group),
          "actor_responses": sum(r["actor_response"] for r in group),
          "valid_batches": sum(r["validation"] == "valid" for r in group),
          "actions": dict(Counter(c for r in group for c in r["all_calls"])),
          "inspect_cells": sum(any(c in ("find", "open") for c in r["all_calls"]) for r in group),
          "stated_scope_count": sum(r["stated_scope"] is not None for r in group),
          "stated_scope_realized": sum(r["stated_scope_realized"] is True for r in group),
          "semantic_reviewed": sum(r["cell"] in scores for r in group),
          "premature_commitment": sum(r["premature_commitment"] is True for r in group),
          "need_fidelity": sum(r["need_fidelity"] is True for r in group),
          "appropriate_granularity": sum(r["granularity"] == "appropriate" for r in group),
          "source_compatibility": sum(r["source_compatibility"] is True for r in group),
          "action_matches_need": sum(r["action_matches_need"] is True for r in group),
          "concrete_source_quality": sum(r["concrete_source_quality"] is True for r in group)}
    result = {"rows": rows, "aggregates": aggregates,
      "note": "A1 has two unique question-only planner outputs persisted across four checkpoints each; its eight semantic rows are repeated-state evaluations, not eight independent plans. A0 reuses frozen broad H1. No P3 tools executed, so evidence gain is unobserved."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(aggregates, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
