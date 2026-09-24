"""Score frozen E1 reliability and conditional superiority gates."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())
REVIEWS = json.loads((HERE / "REVIEWS.json").read_text())
FREEZE = json.loads((HERE / "freeze.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())


def ratio(n, d):
    return n / d if d else None


def arm_metrics(arm):
    rows = [REVIEWS[c["case_id"] + ":" + arm] for c in BANK]
    emitted = [f for r in rows for f in r["findings"]]
    required = [v for r in rows for v in r["required_finding_hits"]]
    m2 = [REVIEWS[c["case_id"] + ":" + arm] for c in BANK if c["category"] == "M2"]
    m3 = [REVIEWS[c["case_id"] + ":" + arm] for c in BANK if c["category"] == "M3"]
    return {
        "cells": len(rows), "errors": sum(r["error"] is not None for r in rows),
        "findings": len(emitted),
        "source_supported": sum(f["source_supported"] for f in emitted),
        "supported_and_gap_relevant": sum(f["source_supported"] and f["gap_relevant_and_new"] for f in emitted),
        "support_only_precision": ratio(sum(f["source_supported"] for f in emitted), len(emitted)),
        "frozen_composite_precision": ratio(sum(f["source_supported"] and f["gap_relevant_and_new"] for f in emitted), len(emitted)),
        "required_hits": sum(required), "required_total": len(required),
        "recall": ratio(sum(required), len(required)),
        "identity_hits": sum(sum(r["required_finding_hits"]) for r in m2),
        "identity_total": sum(len(r["required_finding_hits"]) for r in m2),
        "identity_accuracy": ratio(sum(sum(r["required_finding_hits"]) for r in m2),
                                   sum(len(r["required_finding_hits"]) for r in m2)),
        "temporal_hits": sum(sum(r["required_finding_hits"]) for r in m3),
        "temporal_total": sum(len(r["required_finding_hits"]) for r in m3),
        "temporal_accuracy": ratio(sum(sum(r["required_finding_hits"]) for r in m3),
                                   sum(len(r["required_finding_hits"]) for r in m3)),
        "metadata_overreach": sum(f["metadata_overreach"] for f in emitted),
        "metadata_overreach_rate": ratio(sum(f["metadata_overreach"] for f in emitted), len(emitted)),
        "gap_relevance_rate": ratio(sum(f["gap_relevant_and_new"] for f in emitted), len(emitted)),
    }


t, p = arm_metrics("T"), arm_metrics("P")
metadata_cases = [c for c in BANK if c["category"] in ("M2", "M3")]
paired_fixes = []
paired_regressions = []
for c in metadata_cases:
    cid = c["case_id"]
    th = REVIEWS[cid + ":T"]["required_finding_hits"]
    ph = REVIEWS[cid + ":P"]["required_finding_hits"]
    assert len(th) == len(ph)
    for i, (tv, pv) in enumerate(zip(th, ph)):
        if not tv and pv:
            paired_fixes.append([cid, i])
        if tv and not pv:
            paired_regressions.append([cid, i])

g = FREEZE["gate"]
checks = {"frozen_composite_precision": p["frozen_composite_precision"] >= g["precision_min"],
          "recall": p["recall"] >= g["recall_min"],
          "identity": p["identity_accuracy"] >= g["identity_min"],
          "temporal": p["temporal_accuracy"] >= g["temporal_min"],
          "metadata_overreach": p["metadata_overreach_rate"] <= g["metadata_overreach_max"]}
trigger = t["identity_total"] - t["identity_hits"] + t["temporal_total"] - t["temporal_hits"] >= g["T_error_trigger"]
if trigger:
    checks["conditional_superiority"] = (len(paired_fixes) - len(paired_regressions) >= g["P_net_improvement_min"]
                                          and len(paired_regressions) <= g["reverse_worsening_max"])

cache = {"prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 0}
for line in (HERE / "events.jsonl").open():
    e = json.loads(line)
    if e["kind"] == "model_response":
        u = e.get("cache_usage") or {}
        for key in cache:
            cache[key] += u.get(key, 0) or 0

result = {"T": t, "P": p, "paired_metadata_fixes": paired_fixes,
          "paired_metadata_regressions": paired_regressions,
          "T_clear_M2_M3_errors": t["identity_total"] - t["identity_hits"] + t["temporal_total"] - t["temporal_hits"],
          "conditional_superiority_activated": trigger,
          "checks": checks, "gate_pass": all(checks.values()), "cache": cache,
          "all_outcomes_retained": len(OUTCOMES) == 88}
(HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
