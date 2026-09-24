"""Score post-call F1 W reviews under the pre-call rubric."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = {x["case_id"]: x for x in json.loads((HERE / "BANK.json").read_text())}
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())
REVIEWS = {x["cell"]: x for x in json.loads((HERE / "REVIEWS.json").read_text())}
EVENTS = [json.loads(x) for x in (HERE / "events.jsonl").open()]
assert len(BANK) == 24 and len(OUTCOMES) == len(REVIEWS) == 48


def div(a, b):
    return a / b if b else None


def usage(stage, arm):
    selected = [e for e in EVENTS if e["kind"] == stage + "_response" and e["cell"].endswith(":" + arm)]
    out = {k: sum(e["response"]["usage"].get(k, 0) for e in selected)
           for k in ("prompt_tokens", "completion_tokens", "total_tokens",
                     "prompt_cache_hit_tokens", "prompt_cache_miss_tokens")}
    out["calls"] = len(selected)
    out["prompt_cache_hit_rate"] = div(out["prompt_cache_hit_tokens"], out["prompt_tokens"])
    return out


cells = {}
for cell, outcome in OUTCOMES.items():
    review = REVIEWS[cell]
    obs_refs = [x["window_ref"] for x in outcome["observations"]]
    assert [x["window_ref"] for x in review["observation_reviews"]] == obs_refs, cell
    assert all(type(x["useful_evidence"]) is bool and isinstance(x["reason"], str) and x["reason"]
               for x in review["observation_reviews"]), cell
    assert type(review["scope_correct"]) is bool and type(review["gap_scatter"]) is bool
    assert type(review["redundant"]) is bool and review["action_reason"]
    useful = any(x["useful_evidence"] for x in review["observation_reviews"])
    frontier = any(x["frontier_specific"] for x in review["observation_reviews"])
    cells[cell] = {"useful_evidence": useful, "no_gain": not useful,
                   "frontier_specific_progress": frontier,
                   "scope_correct": review["scope_correct"],
                   "gap_scatter": review["gap_scatter"],
                   "redundant": review["redundant"],
                   "action": outcome["action"],
                   "error": outcome["error"]}

arms = {}
for arm in ("A0", "A1"):
    rows = [v for k, v in cells.items() if k.endswith(":" + arm)]
    arms[arm] = {"useful": sum(x["useful_evidence"] for x in rows),
                 "useful_rate": div(sum(x["useful_evidence"] for x in rows), len(rows)),
                 "no_gain": sum(x["no_gain"] for x in rows),
                 "frontier_specific_progress": sum(x["frontier_specific_progress"] for x in rows),
                 "scope_correct": sum(x["scope_correct"] for x in rows),
                 "gap_scatter": sum(x["gap_scatter"] for x in rows),
                 "redundant": sum(x["redundant"] for x in rows),
                 "errors": sum(x["error"] is not None for x in rows),
                 "action_counts": {tool: sum(x["action"] is not None and x["action"]["name"] == tool for x in rows)
                                   for tool in ("search", "find", "open")},
                 "model_usage": {stage: usage(stage, arm) for stage in ("selector", "actor")}}

wins = [id for id in BANK if cells[id + ":A1"]["useful_evidence"] and not cells[id + ":A0"]["useful_evidence"]]
reversals = [id for id in BANK if cells[id + ":A0"]["useful_evidence"] and not cells[id + ":A1"]["useful_evidence"]]
same_yes = [id for id in BANK if cells[id + ":A0"]["useful_evidence"] and cells[id + ":A1"]["useful_evidence"]]
same_no = [id for id in BANK if not cells[id + ":A0"]["useful_evidence"] and not cells[id + ":A1"]["useful_evidence"]]
preferred = sum(OUTCOMES[id + ":A1"]["selected_gap"] == c["review"]["preferred_next_gap"]
                for id, c in BANK.items())
result = {"sample_count": 24, "qids": 10, "arms": arms,
          "paired": {"A1_only_useful": wins, "A0_only_useful": reversals,
                     "both_useful": same_yes, "neither_useful": same_no,
                     "net_useful_improvement": len(wins) - len(reversals),
                     "wins_qids": sorted({BANK[id]["qid"] for id in wins}),
                     "reverse_qids": sorted({BANK[id]["qid"] for id in reversals})},
          "selector_preferred_agreement": preferred,
          "selector_valid_count": sum(OUTCOMES[id + ":A1"]["selected_gap"] is not None for id in BANK),
          "cells": cells}
a0_failures = sum(cells[id + ":A0"]["no_gain"] or cells[id + ":A0"]["gap_scatter"] or
                  not cells[id + ":A0"]["scope_correct"] for id in BANK)
result["A0_diagnostic_failures"] = a0_failures
result["gate"] = {"A0_failure_condition_met": a0_failures >= 5,
                  "net_improvement_met": len(wins) - len(reversals) >= 4,
                  "reverse_worsening_met": len(reversals) <= 1,
                  "useful_rate_no_decline": arms["A1"]["useful_rate"] >= arms["A0"]["useful_rate"],
                  "no_gain_no_increase": arms["A1"]["no_gain"] <= arms["A0"]["no_gain"]}
result["gate"]["explicit_frontier_worth_extra_call"] = all(result["gate"].values())
(HERE / "RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "cells"}, ensure_ascii=False, indent=2))
