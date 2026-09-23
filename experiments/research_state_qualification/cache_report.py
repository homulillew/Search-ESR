"""Provider-reported DeepSeek prompt-cache telemetry for this study."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
PATHS = {"R1_actor": HERE / "qualification_upper_bound/events.jsonl"}


def main():
    groups = {}
    for name, path in PATHS.items():
        if not path.exists():
            continue
        rows = []
        errors = 0
        for line in path.open():
            event = json.loads(line)
            if event["kind"] == "actor_error":
                errors += 1
            if event["kind"] != "actor_response":
                continue
            usage = extract(event["response"])
            rows.append({"cell": event["cell"], "usage": usage})
        hits = sum(r["usage"].get("prompt_cache_hit_tokens", 0) for r in rows)
        misses = sum(r["usage"].get("prompt_cache_miss_tokens", 0) for r in rows)
        groups[name] = {"responses": len(rows), "api_errors": errors,
                        "usage_reported": sum(r["usage"]["status"] == "reported" for r in rows),
                        "usage_unavailable": sum(r["usage"]["status"] != "reported" for r in rows),
                        "prompt_cache_hit_tokens": hits, "prompt_cache_miss_tokens": misses,
                        "weighted_hit_rate": hits / (hits + misses) if hits + misses else None,
                        "per_response": rows}
    report = {"model": "deepseek-flash", "groups": groups,
              "definition": "sum(provider prompt_cache_hit_tokens) / sum(hit + miss); unavailable usage excluded"}
    (HERE / "CACHE_USAGE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: {s: v[s] for s in ("responses", "api_errors", "usage_reported", "weighted_hit_rate")}
                      for k, v in groups.items()}, indent=2))


if __name__ == "__main__":
    main()
