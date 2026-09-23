"""Post-run cache report including the separately frozen M0b compatibility call."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract, summarize

HERE = Path(__file__).resolve().parent


def main():
    report = summarize(["M0", "M1", "M2", "M3", "M4", "M5"])
    events = [json.loads(line) for line in (HERE / "forced_choice_events.jsonl").open()]
    responses = [e for e in events if e["kind"] == "api_response"]
    errors = [e for e in events if e["kind"] == "api_error"]
    caches = [extract(e["response"]) for e in responses]
    valid = [x for x in caches if x["status"] == "reported"]
    hit = sum(x["prompt_cache_hit_tokens"] for x in valid)
    miss = sum(x["prompt_cache_miss_tokens"] for x in valid)
    report["stages"]["M0b"] = {"responses": len(responses), "api_errors": len(errors),
        "usage_reported": len(valid), "usage_unavailable": len(caches) - len(valid),
        "prompt_cache_hit_tokens": hit, "prompt_cache_miss_tokens": miss,
        "weighted_hit_rate": hit / (hit + miss) if hit + miss else None,
        "per_response": [{"cell": "forced_single_tool_thinking_disabled", "cache": x} for x in caches]}
    totals = report["all_stages"]
    totals["responses"] += len(responses)
    totals["api_errors"] += len(errors)
    totals["usage_reported"] += len(valid)
    totals["usage_unavailable"] += len(caches) - len(valid)
    totals["prompt_cache_hit_tokens"] += hit
    totals["prompt_cache_miss_tokens"] += miss
    denom = totals["prompt_cache_hit_tokens"] + totals["prompt_cache_miss_tokens"]
    totals["weighted_hit_rate"] = totals["prompt_cache_hit_tokens"] / denom if denom else None
    report["scope_note"] = ("All experimental DeepSeek Chat Completions responses M0-M5, including M0b. "
        "Failed requests have unknown cache usage; no artificial cache warm-up. "
        "This observed hit rate may include provider cache from activity outside the experiment.")
    (HERE / "CACHE_USAGE_FINAL.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"stages": {k: {m: v[m] for m in ("responses", "api_errors", "prompt_cache_hit_tokens",
        "prompt_cache_miss_tokens", "weighted_hit_rate")} for k, v in report["stages"].items()},
        "all_stages": totals}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
