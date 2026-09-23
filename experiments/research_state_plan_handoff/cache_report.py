"""Study-local, provider-reported DeepSeek prompt-cache telemetry."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STAGES = {
    "P1": HERE / "plan_handoff_one_step/events.jsonl",
    "P2": HERE / "plan_orthogonal_interaction/events.jsonl",
    "P3": HERE / "atomic_need_timing/events.jsonl",
}


def main():
    groups = {}
    for stage, path in STAGES.items():
        if not path.exists():
            continue
        for line in path.open():
            e = json.loads(line)
            if e["kind"] not in ("api_response", "actor_response", "planner_response",
                                  "api_error", "actor_error", "planner_error"):
                continue
            role = "planner" if "planner" in e["kind"] else "actor"
            key = f"{stage}_{role}"
            group = groups.setdefault(key, {"responses": 0, "api_errors": 0,
                "usage_reported": 0, "usage_unavailable": 0,
                "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 0,
                "per_response": []})
            if e["kind"].endswith("error"):
                group["api_errors"] += 1
                continue
            raw = e.get("response") or {}
            if raw.get("model") != "deepseek-flash":
                continue
            usage = extract(raw)
            group["responses"] += 1
            if usage["status"] == "reported":
                group["usage_reported"] += 1
                group["prompt_cache_hit_tokens"] += usage["prompt_cache_hit_tokens"]
                group["prompt_cache_miss_tokens"] += usage["prompt_cache_miss_tokens"]
            else:
                group["usage_unavailable"] += 1
            group["per_response"].append({"cell": e.get("cell"),
                                          "decision": e.get("decision"), "usage": usage})
    for group in groups.values():
        denominator = group["prompt_cache_hit_tokens"] + group["prompt_cache_miss_tokens"]
        group["weighted_hit_rate"] = group["prompt_cache_hit_tokens"] / denominator if denominator else None
    totals = {name: sum(g[name] for g in groups.values()) for name in
              ("responses", "api_errors", "usage_reported", "usage_unavailable",
               "prompt_cache_hit_tokens", "prompt_cache_miss_tokens")}
    denominator = totals["prompt_cache_hit_tokens"] + totals["prompt_cache_miss_tokens"]
    totals["weighted_hit_rate"] = totals["prompt_cache_hit_tokens"] / denominator if denominator else None
    report = {"model": "deepseek-flash", "groups": groups, "all_stages": totals,
              "definition": "sum(provider prompt_cache_hit_tokens) / sum(hit+miss) on consistent response usage; errors unknown, never zero hit"}
    (HERE / "CACHE_USAGE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"groups": {k: {m: v[m] for m in ("responses", "api_errors", "weighted_hit_rate")} for k, v in groups.items()},
                      "all_stages": totals}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
