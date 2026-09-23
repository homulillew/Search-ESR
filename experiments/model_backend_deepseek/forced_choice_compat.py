"""Separate, prospective compatibility check for DeepSeek's named tool choice."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import sys

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "provider.json").read_text())
FREEZE = HERE / "freeze_forced_choice.json"
EVENTS = HERE / "forced_choice_events.jsonl"
SUMMARY = HERE / "forced_choice_summary.json"
MESSAGES = [{"role": "user", "content": "Call search with query synthetic preflight and k=1."}]
CHOICE = {"type": "function", "function": {"name": "search"}}
EXTRA_BODY = {"thinking": {"type": "disabled"}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                              "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    paths = ["experiments/model_backend_deepseek/forced_choice_compat.py",
             "experiments/model_backend_deepseek/provider.json",
             "experiments/model_backend_deepseek/protocol.py",
             "experiments/model_backend_deepseek/cache_usage.py",
             "llm_chat/search_find_agent.py"]
    record = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
              "purpose": "Named tool choice with thinking disabled, after default-thinking 400",
              "model": CONFIG["model"], "host": urlsplit(CONFIG["base_url"]).hostname,
              "messages": MESSAGES, "tool_choice": CHOICE, "extra_body": EXTRA_BODY,
              "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
              "m0_summary_sha256": sha(HERE / "protocol_summary.json"),
              "source_sha256": {p: sha(ROOT / p) for p in paths},
              "max_retries": 0, "samples": 1,
              "success_gate": "A single valid search tool call and preserved raw finish reason"}
    FREEZE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def gate():
    record = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in record["source_sha256"].items()),
              "m0_unchanged": sha(HERE / "protocol_summary.json") == record["m0_summary_sha256"],
              "schema": digest(SEARCH_FIND_TOOLS) == record["tool_schema_sha256"],
              "model": record["model"] == CONFIG["model"],
              "host": record["host"] == urlsplit(CONFIG["base_url"]).hostname,
              "request": record["messages"] == MESSAGES and record["tool_choice"] == CHOICE
                         and record["extra_body"] == EXTRA_BODY}
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    params = {"model": CONFIG["model"], "messages": MESSAGES,
              "tools": SEARCH_FIND_TOOLS, "tool_choice": CHOICE,
              "extra_body": EXTRA_BODY, "stream": False}
    emit("api_request", request=params)
    try:
        with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                    timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
            raw = client.chat.completions.create(**params).model_dump(mode="json")
        choice = raw["choices"][0]
        parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                          allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
        emit("api_response", response=raw, raw_finish_reason=choice.get("finish_reason"),
             raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
             validation="valid" if error is None else error, parsed_calls=parsed,
             cache_usage=extract(raw))
        passed = error is None and len(parsed) == 1 and parsed[0]["name"] == "search"
        summary = {"pass": passed, "mode": "thinking disabled only for named-tool diagnostic",
                   "raw_finish_reason": choice.get("finish_reason"),
                   "tool_count": len(parsed), "validation": "valid" if error is None else error,
                   "cache_usage": extract(raw)}
    except Exception as exc:
        emit("api_error", error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
        summary = {"pass": False, "error_type": type(exc).__name__,
                   "http_status": getattr(exc, "status_code", None)}
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    import sys
    action = sys.argv[1]
    if action == "freeze":
        freeze()
    elif action == "gate":
        print(gate())
    elif action == "run":
        print(json.dumps(run(), ensure_ascii=False, indent=2))
    else:
        raise SystemExit("freeze|gate|run")
