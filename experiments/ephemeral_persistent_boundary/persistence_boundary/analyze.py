"""Frozen-label scoring for S2, including all failed model cells."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
bank = json.loads((HERE / "BANK.json").read_text())
outcomes = json.loads((HERE / "outcomes.json").read_text())
events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]


def matches(value, truth):
    return isinstance(value, str) and truth is not None and value.casefold().strip() == truth.casefold().strip()


def score():
    assert len(outcomes) == len(bank) * 3 == 120
    rows = []
    for c in bank:
        for arm in ("L", "I", "X"):
            o = outcomes[c["case_id"] + ":" + arm]
            truth = c["review"]["correct_new_value"]
            ps = o["proposals"]
            cm = o["committed"]
            false_ps = [p for p in ps if not matches(p["value"], truth)]
            correct_cm = [p for p in cm if matches(p["value"], truth)]
            false_cm = [p for p in cm if not matches(p["value"], truth)]
            copied = [p for p in ps if any(p["value"].casefold().strip() == g.casefold().strip() for g in c["ephemeral_guess_values"])]
            rows.append({"case_id": c["case_id"], "qid": c["qid"], "category": c["category"], "arm": arm,
                         "error": o["error"], "proposal_count": len(ps), "false_proposal": bool(false_ps),
                         "false_proposal_count": len(false_ps), "query_guess_copied": bool(copied),
                         "mechanical_rejections": len(ps) - len(o["mechanically_accepted"]),
                         "verifier_rejections": len(o["mechanically_accepted"]) - len(cm),
                         "commit_count": len(cm), "correct_commit_count": len(correct_cm),
                         "false_commit_count": len(false_cm), "correct_recovery": bool(correct_cm),
                         "no_state_change": len(cm) == 0})
    by_arm = {}
    for arm in ("L", "I", "X"):
        group = [r for r in rows if r["arm"] == arm]
        binding = [r for r in group if r["category"] in ("P1", "P5", "P6")]
        false_sensitive = [r for r in group if r["category"] in ("P2", "P3", "P4")]
        p4 = [r for r in group if r["category"] == "P4"]
        p5 = [r for r in group if r["category"] == "P5"]
        p6 = [r for r in group if r["category"] == "P6"]
        cc = sum(r["correct_commit_count"] for r in group)
        ac = sum(r["commit_count"] for r in group)
        by_arm[arm] = {"n":len(group),"categories":dict(Counter(r["category"] for r in group)),
            "errors":sum(r["error"] is not None for r in group),
            "proposal_copy_cases":sum(r["query_guess_copied"] for r in group),
            "false_proposal_cases":sum(r["false_proposal"] for r in group),
            "false_proposal_count":sum(r["false_proposal_count"] for r in group),
            "mechanical_rejections":sum(r["mechanical_rejections"] for r in group),
            "verifier_rejections":sum(r["verifier_rejections"] for r in group),
            "committed_binding_precision":cc/ac if ac else 0,
            "binding_recall":sum(r["correct_recovery"] for r in binding)/len(binding),
            "false_promotion_rate":sum(r["false_commit_count"]>0 for r in false_sensitive)/len(false_sensitive),
            "nogain_preservation":sum(r["no_state_change"] for r in p4)/len(p4),
            "alternative_value_recovery":sum(r["correct_recovery"] for r in p5)/len(p5),
            "conflict_recovery_count":sum(r["correct_recovery"] for r in p6),
            "unsupported_commits":sum(r["false_commit_count"] for r in group),
            "correct_commits":cc,"all_commits":ac}
    idx = {(r["case_id"],r["arm"]):r for r in rows}
    paired = {}
    for comparator in ("I","X"):
        improvements = sum(idx[(c["case_id"],"L")]["false_proposal"] and not idx[(c["case_id"],comparator)]["false_proposal"] for c in bank)
        worsens = sum(idx[(c["case_id"],comparator)]["false_proposal"] and not idx[(c["case_id"],"L")]["false_proposal"] for c in bank)
        promotion_improve = sum(idx[(c["case_id"],"L")]["false_commit_count"]>0 and idx[(c["case_id"],comparator)]["false_commit_count"]==0 for c in bank)
        promotion_worsen = sum(idx[(c["case_id"],comparator)]["false_commit_count"]>0 and idx[(c["case_id"],"L")]["false_commit_count"]==0 for c in bank)
        paired[comparator + "_vs_L"] = {"false_proposal_improvements":improvements,"false_proposal_worsenings":worsens,
            "false_promotion_improvements":promotion_improve,"false_promotion_worsenings":promotion_worsen,
            "any_false_improvements":sum((idx[(c["case_id"],"L")]["false_proposal"] or idx[(c["case_id"],"L")]["false_commit_count"]>0) and
                not (idx[(c["case_id"],comparator)]["false_proposal"] or idx[(c["case_id"],comparator)]["false_commit_count"]>0) for c in bank),
            "any_false_worsenings":sum((idx[(c["case_id"],comparator)]["false_proposal"] or idx[(c["case_id"],comparator)]["false_commit_count"]>0) and
                not (idx[(c["case_id"],"L")]["false_proposal"] or idx[(c["case_id"],"L")]["false_commit_count"]>0) for c in bank)}
    x=by_arm["X"]; pair=paired["X_vs_L"]
    checks={"precision":x["committed_binding_precision"]>=.95,
        "recall":x["binding_recall"]>=.85,"false_promotion":x["false_promotion_rate"]<=.05,
        "nogain":x["nogain_preservation"]>=.90,"alternative_recovery":x["alternative_value_recovery"]>=.80,
        "conflict":x["conflict_recovery_count"]>=3,
        "paired_improvement":pair["any_false_improvements"]>=6,
        "reverse_worsening":pair["any_false_worsenings"] < pair["any_false_improvements"]/2}
    caches={}
    for kind in ("binder_response","verifier_response"):
        relevant=[e for e in events if e["kind"]==kind]
        pt=sum(e.get("cache_usage",{}).get("prompt_tokens") or 0 for e in relevant)
        hit=sum(e.get("cache_usage",{}).get("prompt_cache_hit_tokens") or 0 for e in relevant)
        caches[kind]={"calls":len(relevant),"prompt_tokens":pt,"hit_tokens":hit,"weighted_hit_rate":hit/pt if pt else None}
    result={"by_arm":by_arm,"paired":paired,"gate_checks":checks,"s2_pass":all(checks.values()),
            "cache_usage":caches,"rows":rows}
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},ensure_ascii=False,indent=2))


if __name__=="__main__":score()
