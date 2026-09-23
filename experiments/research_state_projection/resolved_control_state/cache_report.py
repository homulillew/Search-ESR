"""Aggregate provider-reported cache usage from frozen S1 responses."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent


def main():
    groups = {arm: [] for arm in ("B", "C")}
    for line in (HERE / "events.jsonl").open():
        event = json.loads(line)
        if event["kind"] == "actor_response":
            groups[event["cell"].rsplit(":", 1)[1]].append(
                {"cell": event["cell"], "usage": extract(event["response"])})
    report = {"model": "deepseek-flash", "definition":
              "sum(provider prompt_cache_hit_tokens) / sum(hit + miss); unavailable responses excluded",
              "groups": {}}
    for arm, rows in groups.items():
        reported = [r for r in rows if r["usage"]["status"] == "reported"]
        hits = sum(r["usage"]["prompt_cache_hit_tokens"] for r in reported)
        misses = sum(r["usage"]["prompt_cache_miss_tokens"] for r in reported)
        report["groups"][arm] = {
            "responses": len(rows), "usage_reported": len(reported),
            "usage_unavailable": len(rows) - len(reported),
            "prompt_cache_hit_tokens": hits, "prompt_cache_miss_tokens": misses,
            "weighted_hit_rate": hits / (hits + misses) if hits + misses else None,
            "per_response": rows,
        }
    (HERE / "CACHE_USAGE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({arm: {key: value for key, value in group.items() if key != "per_response"}
                      for arm, group in report["groups"].items()}, indent=2))


if __name__ == "__main__":
    main()
