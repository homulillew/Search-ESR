"""One DeepSeek natural Search/Find/Open decision at each frozen M2 prefix."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/search_find_v3b/orthogonal_search"))
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from run_partial import checkpoint
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OLD = ROOT / "experiments/model_backend_atria"
CONFIG = json.loads((STUDY / "provider.json").read_text())
BASELINES = json.loads((STUDY / "BASELINE_FINGERPRINTS.json").read_text())["sha256"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def selection():
    paired = json.loads((STUDY / "planning_probe/mechanical_summary.json").read_text())["paired"]
    a = [(r["qid"], r["seq"]) for r in paired if r["deepseek_scope"] == "document" and r["qwen_scope"] == "corpus"][:3]
    b = [(r["qid"], r["seq"]) for r in paired if r["deepseek_scope"] == "document" and r["qwen_scope"] == "document"][:2]
    c = [(r["qid"], r["seq"]) for r in paired if r["deepseek_scope"] == "corpus" and r["qwen_scope"] == "corpus"][:2]
    if len(a) < 3 or len(b) < 2 or len(c) < 2:
        return [(r["qid"], r["seq"]) for r in paired], "all_13_due_to_short_stratum"
    return list(dict.fromkeys(a + b + c)), "stratified_first_in_frozen_order"


def request(q, seq):
    original, _, _ = checkpoint(q, seq)
    params = json.loads(json.dumps(original))
    params["model"] = CONFIG["model"]
    return params


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if not all(sha(ROOT / p) == h for p, h in BASELINES.items()):
        raise AssertionError("Baseline changed")
    chosen, rule = selection()
    sources = ["experiments/model_backend_deepseek/natural_action_probe/run.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/search_find_agent.py"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "model": CONFIG["model"], "base_url": CONFIG["base_url"],
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "selection": chosen, "selection_rule": rule,
           "one_decision_per_model": True, "no_tool_execution": True,
           "thinking_mode": "provider default", "samples_per_cell": 1,
           "schema_sha256": digest(SEARCH_FIND_TOOLS),
           "m1_summary_sha256": sha(STUDY / "planning_probe/mechanical_summary.json"),
           "qwen_events_sha256": sha(OLD / "natural_action_probe/events.jsonl"),
           "baseline_fingerprints_sha256": sha(STUDY / "BASELINE_FINGERPRINTS.json"),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "request_sha256": {f"{q}:{s}": digest(request(q, s)) for q, s in chosen},
           "failure_policy": "All selected cells once; preserve errors and raw tool calls"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    chosen, rule = selection()
    checks = {"baseline": all(sha(ROOT / p) == h for p, h in BASELINES.items()) and
              sha(STUDY / "BASELINE_FINGERPRINTS.json") == doc["baseline_fingerprints_sha256"],
              "m1": sha(STUDY / "planning_probe/mechanical_summary.json") == doc["m1_summary_sha256"],
              "qwen": sha(OLD / "natural_action_probe/events.jsonl") == doc["qwen_events_sha256"],
              "selection": chosen == [tuple(x) for x in doc["selection"]] and rule == doc["selection_rule"],
              "sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "schema": digest(SEARCH_FIND_TOOLS) == doc["schema_sha256"],
              "requests": all(digest(request(q, s)) == doc["request_sha256"][f"{q}:{s}"] for q, s in chosen),
              "provider": doc["model"] == CONFIG["model"] and doc["base_url"] == CONFIG["base_url"],
              "one_step": doc["one_decision_per_model"] and doc["no_tool_execution"]}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    chosen, _ = selection()
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for q, s in chosen:
            cell = f"{q}:{s}:{CONFIG['model']}"
            params = request(q, s)
            emit("api_request", cell=cell, request=params)
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
                choice = (raw.get("choices") or [{}])[0]
                parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                    allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
                action = (parsed[0]["name"] if len(parsed) == 1 and error is None else
                          "batch" if len(parsed) > 1 and error is None else
                          "stop" if not parsed and error is None else "invalid")
                emit("api_response", cell=cell, response=raw,
                     raw_finish_reason=choice.get("finish_reason"),
                     raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
                     validation=error or "valid", parsed_calls=parsed, action=action,
                     cache_usage=extract(raw))
                print(cell, action, flush=True)
            except Exception as exc:
                emit("api_error", cell=cell, error_type=type(exc).__name__,
                     http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
                print(cell, "error", type(exc).__name__, flush=True)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze":
        freeze()
    elif action == "gate":
        gate()
        print("PASS")
    elif action == "run":
        run()
    else:
        raise SystemExit("freeze|gate|run")
