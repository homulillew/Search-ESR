"""Apply the original M1 rubric to Qwen baseline and DeepSeek responses."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_atria.planning_probe.analyze import parse

HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/model_backend_atria"
MODEL = "deepseek-flash"


def main():
    labels = {(r["qid"], r["seq"]): r for r in json.loads(
        (OLD / "PREFIX_ONLY_ANNOTATIONS.json").read_text())["rows"]}
    old = json.loads((OLD / "planning_probe/mechanical_summary.json").read_text())
    qwen = {(r["qid"], r["seq"]): r for r in old["rows"] if r["model"] == "qwen3.7-flash"}
    events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    responses = {e["cell"]: e for e in events if e["kind"] == "api_response"}
    errors = {e["cell"]: e for e in events if e["kind"] == "api_error"}
    scores_path = HERE / "semantic_scores.json"
    scores = json.loads(scores_path.read_text()) if scores_path.exists() else {}
    rows = []
    paired = []
    for key, label in labels.items():
        q, seq = key
        cell = f"{q}:{seq}:{MODEL}"
        e = responses.get(cell)
        if e:
            choice = (e["response"].get("choices") or [{}])[0]
            content = (choice.get("message") or {}).get("content") or ""
            parsed = parse(content)
            scope = parsed["parsed_scope"]
            target = parsed["parsed_target"]
            row = {"cell": cell, "qid": q, "seq": seq, "model": MODEL,
                   "finish_reason": choice.get("finish_reason"), "content": content,
                   **parsed, "ambiguity": label["ambiguity"],
                   "scope_compatible": scope in label["acceptable_scopes"] if scope else False,
                   "target_compatible": target in label["plausible_document_refs"]
                   if scope == "document" else None,
                   "over_search": scope == "corpus" and "corpus" not in label["acceptable_scopes"],
                   "premature_local": scope in {"document", "window"} and
                   label["acceptable_scopes"] == ["corpus"],
                   "need_agreement": scores.get(cell, {}).get("need_agreement"),
                   "source_type_agreement": scores.get(cell, {}).get("source_type_agreement")}
        else:
            row = {"cell": cell, "qid": q, "seq": seq, "model": MODEL,
                   "error": errors.get(cell, {}).get("error_type", "missing_response"),
                   "ambiguity": label["ambiguity"], "scope_compatible": False,
                   "need_agreement": None, "source_type_agreement": None}
        rows.append(row)
        qr = qwen[key]
        paired.append({"qid": q, "seq": seq, "acceptable_scopes": label["acceptable_scopes"],
                       "qwen_scope": qr.get("parsed_scope"), "deepseek_scope": row.get("parsed_scope"),
                       "qwen_compatible": qr["scope_compatible"],
                       "deepseek_compatible": row["scope_compatible"],
                       "qwen_response": "content" in qr, "deepseek_response": "content" in row})
    if set(scores) - {r["cell"] for r in rows}:
        raise ValueError("Unknown semantic score cell")
    for cell, score in scores.items():
        if not all(score.get(k) in (True, False) for k in
                   ("need_agreement", "source_type_agreement")) or not score.get("reason"):
            raise ValueError(f"Incomplete semantic score: {cell}")
    qwen_rows = list(qwen.values())
    def agg(rs):
        return {"responses": sum("content" in r for r in rs),
                "scope_compatible": sum(r["scope_compatible"] for r in rs),
                "document_plans": sum(r.get("parsed_scope") == "document" for r in rs),
                "target_compatible_among_document_plans": sum(r.get("target_compatible") is True for r in rs),
                "need_agreement": sum(r.get("need_agreement") is True for r in rs),
                "source_type_agreement": sum(r.get("source_type_agreement") is True for r in rs),
                "semantic_scores_complete": sum(r["cell"] in scores for r in rs) if rs is rows else
                  old["aggregates"]["qwen3.7-flash"]["semantic_scores_complete"],
                "over_search": sum(r.get("over_search", False) for r in rs),
                "premature_local": sum(r.get("premature_local", False) for r in rs)}
    from math import comb
    qonly = sum(p["qwen_compatible"] and not p["deepseek_compatible"] for p in paired)
    donly = sum(p["deepseek_compatible"] and not p["qwen_compatible"] for p in paired)
    n = qonly + donly
    pvalue = min(1.0, 2 * sum(comb(n, i) for i in range(min(qonly, donly) + 1)) / 2**n) if n else 1.0
    both = [p for p in paired if p["qwen_response"] and p["deepseek_response"]]
    summary = {"rows": qwen_rows + rows, "paired": paired,
               "aggregates": {"qwen3.7-flash": agg(qwen_rows), MODEL: agg(rows)},
               "complete_case": {"n": len(both),
                 "qwen_compatible": sum(p["qwen_compatible"] for p in both),
                 "deepseek_compatible": sum(p["deepseek_compatible"] for p in both)},
               "exact_mcnemar_scope": {"qwen_only": qonly, "deepseek_only": donly,
                                       "exact_two_sided_p": pvalue},
               "error_cells": list(errors),
               "semantic_scoring": "Original frozen single-reviewer rubric; unscored responses are null"}
    (HERE / "mechanical_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("aggregates", "complete_case", "exact_mcnemar_scope", "error_cells")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
