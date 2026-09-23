"""Native trajectory shape and explicit provider-error accounting."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.search_find_v3b.orthogonal_search.run_partial import load_events

HERE = Path(__file__).resolve().parent


def qwen_first_n(qid, n=12):
    events = load_events(qid)
    requests = [e for e in events if e["kind"] == "api_request"]
    boundary = requests[n]["seq"] if len(requests) > n else float("inf")
    first = [e for e in events if e["seq"] < boundary]
    internals = [e for e in first if e["kind"] == "tool_internal"]
    handles = internals[-1]["audit"]["handles"] if internals else {"documents": [], "windows": []}
    return {"decisions": min(n, len([e for e in first if e["kind"] == "api_response"])),
            "actions": dict(Counter(e["name"] for e in first if e["kind"] == "tool_start")),
            "documents": len(handles["documents"]), "windows": len(handles["windows"]),
            "comparison_note": "Qwen historical v3a; different harness and possible horizon"}


def main():
    events = [json.loads(line) for line in (HERE / "events.jsonl").open()]
    rows = []
    for q in ("546", "1094"):
        cell = f"{q}:deepseek-flash"
        sub = [e for e in events if e.get("cell") == cell]
        end = next(e for e in sub if e["kind"] == "cell_end")
        errors = [e for e in sub if e["kind"] in ("api_error", "tool_error", "harness_error")]
        rows.append({"qid": q, "model": "deepseek-flash", "status": end["status"],
                     "decisions": len([e for e in sub if e["kind"] == "api_response"]),
                     "actions": dict(Counter(e["name"] for e in sub if e["kind"] == "tool_start")),
                     "documents": end["documents"], "windows": end["windows"],
                     "errors": [{"kind": e["kind"], "decision": e.get("decision"),
                                 "error_type": e.get("error_type"),
                                 "http_status": e.get("http_status")} for e in errors],
                     "qwen_historical_first_12": qwen_first_n(q)})
    result = {"rows": rows, "model_effect_caveat": "Native DeepSeek used Orthogonal Search; historical Qwen used v3a. Tool mix and registry size are descriptive, not a randomized model-only effect."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
