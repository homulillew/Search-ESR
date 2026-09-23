"""Frozen DeepSeek M1 broad-plan handoff to the unchanged M2 actor request."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OLD = ROOT / "experiments/model_backend_deepseek"
CONFIG = json.loads((OLD / "provider.json").read_text())
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
M1 = json.loads((OLD / "planning_probe/mechanical_summary.json").read_text())
M2_EVENTS = [json.loads(line) for line in (OLD / "natural_action_probe/events.jsonl").open()]
CASES = [(r["qid"], r["seq"]) for r in M1["paired"]]
PLAN_LABELS = ("Current unresolved need", "Expected source type",
               "Best scope", "Target document/window")
CARD_PREFIX = "Current research control state:\n\n"
CARD_SUFFIX = ("\n\nThis state records the current research assessment. "
               "Choose the next action normally using the available tools.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def plan(q, seq):
    cell = f"{q}:{seq}:{CONFIG['model']}"
    row = next(r for r in M1["rows"] if r["cell"] == cell)
    fields = {k: row[k] for k in PLAN_LABELS}
    if not all(isinstance(v, str) and v.strip() for v in fields.values()):
        raise ValueError(f"Incomplete frozen M1 plan: {cell}")
    if row["parsed_scope"] not in {"corpus", "document", "window", "stop"}:
        raise ValueError(f"Invalid frozen M1 scope: {cell}")
    return fields


def card(fields):
    return (CARD_PREFIX +
      f"Current unresolved need:\n{fields['Current unresolved need']}\n\n"
      f"Expected source type:\n{fields['Expected source type']}\n\n"
      f"Recommended scope:\n{fields['Best scope']}\n\n"
      f"Current target:\n{fields['Target document/window']}" + CARD_SUFFIX)


def h0_request(q, seq):
    cell = f"{q}:{seq}:{CONFIG['model']}"
    matches = [e["request"] for e in M2_EVENTS if e["kind"] == "api_request" and e["cell"] == cell]
    if len(matches) != 1:
        raise ValueError(f"Expected one historical H0 request for {cell}")
    return matches[0]


def h1_request(q, seq):
    params = json.loads(json.dumps(h0_request(q, seq)))
    params["messages"].append({"role": "user", "content": card(plan(q, seq))})
    return params


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if len(CASES) != 13 or len(set(CASES)) != 13:
        raise ValueError("P1 requires all 13 unique cells")
    sources = ["experiments/research_state_plan_handoff/plan_handoff_one_step/run.py",
               "experiments/research_state_plan_handoff/plan_handoff_one_step/analyze.py",
               "experiments/research_state_plan_handoff/plan_handoff_one_step/RUBRIC.json",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "llm_chat/search_find_agent.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py"]
    historical = ["experiments/model_backend_deepseek/planning_probe/events.jsonl",
                  "experiments/model_backend_deepseek/planning_probe/mechanical_summary.json",
                  "experiments/model_backend_deepseek/natural_action_probe/events.jsonl",
                  "experiments/model_backend_deepseek/natural_action_probe/freeze.json",
                  "experiments/model_backend_deepseek/orthogonal_partial/SELECTION.json",
                  "experiments/model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json",
                  "experiments/search_find_v3b/orthogonal_search/freeze.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
           "agent_prompt_sha256": hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
           "card_prefix": CARD_PREFIX, "card_suffix": CARD_SUFFIX,
           "cases": CASES, "sample_count": 13, "h1_tools_executed": False,
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "historical_sha256": {p: sha(ROOT / p) for p in historical},
           "plan_sha256": {f"{q}:{s}": digest(plan(q, s)) for q, s in CASES},
           "h0_request_sha256": {f"{q}:{s}": digest(h0_request(q, s)) for q, s in CASES},
           "h1_request_sha256": {f"{q}:{s}": digest(h1_request(q, s)) for q, s in CASES},
           "failure_policy": "all 13 H1 cells once; errors retained; no best-of or tool execution"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["historical_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and
                doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and
                doc["timeout_seconds"] == CONFIG["timeout_seconds"],
              "schema": doc["tool_schema_sha256"] == digest(SEARCH_FIND_TOOLS),
              "agent_prompt": doc["agent_prompt_sha256"] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
              "card": doc["card_prefix"] == CARD_PREFIX and doc["card_suffix"] == CARD_SUFFIX,
              "cases": doc["cases"] == [list(x) for x in CASES] and doc["sample_count"] == 13,
              "plans": all(digest(plan(q, s)) == doc["plan_sha256"][f"{q}:{s}"] for q, s in CASES),
              "h0": all(digest(h0_request(q, s)) == doc["h0_request_sha256"][f"{q}:{s}"] for q, s in CASES),
              "h1": all(digest(h1_request(q, s)) == doc["h1_request_sha256"][f"{q}:{s}"] for q, s in CASES),
              "one_step": doc["h1_tools_executed"] is False and doc["max_retries"] == 0}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                              "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for q, seq in CASES:
            cell = f"{q}:{seq}:H1"
            params = h1_request(q, seq)
            emit("api_request", cell=cell, request=params,
                 plan_sha256=digest(plan(q, seq)), request_sha256=digest(params))
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
                choice = (raw.get("choices") or [{}])[0]
                parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                    allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
                emit("api_response", cell=cell, response=raw,
                     raw_finish_reason=choice.get("finish_reason"),
                     raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
                     parsed_calls=parsed, validation=error or "valid", cache_usage=extract(raw))
                print(cell, "response", error or "valid", flush=True)
            except Exception as exc:
                emit("api_error", cell=cell, error_type=type(exc).__name__,
                     http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
                print(cell, "error", type(exc).__name__, flush=True)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze":
        freeze()
    elif action == "gate":
        print(gate())
    elif action == "run":
        run()
    else:
        raise SystemExit("freeze|gate|run")
