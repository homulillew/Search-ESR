"""Two native DeepSeek trajectories from the original questions, 12 decisions max."""

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from experiments.search_find_v3b.orthogonal_search.run_partial import load_events

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((STUDY / "provider.json").read_text())
BASELINES = json.loads((STUDY / "BASELINE_FINGERPRINTS.json").read_text())["sha256"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
QIDS = ("546", "1094")
HORIZON = 12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def initial_request(q):
    original = next(e["request"] for e in load_events(q) if e["kind"] == "api_request")
    params = json.loads(json.dumps(original))
    params["model"] = CONFIG["model"]
    return params


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if not all(sha(ROOT / p) == h for p, h in BASELINES.items()):
        raise AssertionError("Baseline changed")
    if not json.loads((STUDY / "evidence_update/mechanical_summary.json").read_text())["aggregates"][CONFIG["model"]]["e1_semantic_scored"] == 8:
        raise AssertionError("M4 semantic review incomplete")
    sources = ["experiments/model_backend_deepseek/deepseek_native/run.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/agent.py", "llm_chat/search_find_agent.py",
               "llm_chat/search_find_v3b_agent.py", "llm_chat/raw_windows.py",
               "llm_chat/window_locator.py", "llm_chat/window_units.py",
               "BCPlus/scripts/search_bcplus.py"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "qids": QIDS, "model": CONFIG["model"],
           "base_url_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "horizon_api_decisions": HORIZON, "replicates": 1,
           "harness": "Orthogonal Search, no State, unchanged prompt/schema/retriever",
           "natural_stop_only": True, "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
           "m1_summary_sha256": sha(STUDY / "planning_probe/mechanical_summary.json"),
           "m4_summary_sha256": sha(STUDY / "evidence_update/mechanical_summary.json"),
           "baseline_fingerprints_sha256": sha(STUDY / "BASELINE_FINGERPRINTS.json"),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "initial_request_sha256": {q: digest(initial_request(q)) for q in QIDS},
           "failure_policy": "one native trajectory per qid; no selective retry; record errors and horizon_no_answer"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"baseline": all(sha(ROOT / p) == h for p, h in BASELINES.items()) and
              sha(STUDY / "BASELINE_FINGERPRINTS.json") == doc["baseline_fingerprints_sha256"],
              "sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "m1": sha(STUDY / "planning_probe/mechanical_summary.json") == doc["m1_summary_sha256"],
              "m4": sha(STUDY / "evidence_update/mechanical_summary.json") == doc["m4_summary_sha256"],
              "schema": digest(SEARCH_FIND_TOOLS) == doc["tool_schema_sha256"],
              "model": doc["model"] == CONFIG["model"] and
                       doc["base_url_host"] == urlsplit(CONFIG["base_url"]).hostname,
              "initial": all(digest(initial_request(q)) == doc["initial_request_sha256"][q] for q in QIDS),
              "horizon": doc["horizon_api_decisions"] == HORIZON and doc["replicates"] == 1}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    for q in QIDS:
        params = initial_request(q)
        if params["tools"] != SEARCH_FIND_TOOLS or params["tool_choice"] != "auto" or len(params["messages"]) != 2:
            raise AssertionError(f"Initial request differs from historical schema for {q}")


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run_cell(client, searcher, q):
    cell = f"{q}:{CONFIG['model']}"
    tools = OrthogonalSearchFindTools()
    tools.searcher = searcher
    messages = initial_request(q)["messages"]
    status = "horizon_no_answer"
    start = time.monotonic()
    emit("cell_start", cell=cell, qid=q)
    try:
        for decision in range(1, HORIZON + 1):
            params = initial_request(q)
            params["messages"] = messages
            emit("api_request", cell=cell, decision=decision, request=params)
            began = time.monotonic()
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
            except Exception as exc:
                emit("api_error", cell=cell, decision=decision,
                     error_type=type(exc).__name__, http_status=getattr(exc, "status_code", None),
                     error=str(exc)[:500], elapsed_seconds=time.monotonic() - began)
                status = "api_error"
                break
            choice = (raw.get("choices") or [{}])[0]
            parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                           allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
            emit("api_response", cell=cell, decision=decision, response=raw,
                 raw_finish_reason=choice.get("finish_reason"),
                 raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
                 validation=error or "valid", parsed_calls=parsed,
                 cache_usage=extract(raw), elapsed_seconds=time.monotonic() - began)
            if error:
                status = "invalid_tool_batch"
                break
            if not parsed:
                status = "natural_stop"
                emit("answer", cell=cell, decision=decision,
                     text=(choice.get("message") or {}).get("content") or "")
                break
            assistant = {k: v for k, v in (choice.get("message") or {}).items()
                         if v is not None and k in ("role", "content", "tool_calls", "reasoning_content")}
            messages.append(assistant)
            for index, call in enumerate(parsed, 1):
                emit("tool_start", cell=cell, decision=decision,
                     call_index=index, name=call["name"], arguments=call["arguments"])
                try:
                    result = tools.execute(call["name"], call["arguments"])
                except Exception as exc:
                    emit("tool_error", cell=cell, decision=decision, call_index=index,
                         error_type=type(exc).__name__, error=str(exc)[:500])
                    status = "tool_error"
                    break
                emit("tool_result", cell=cell, decision=decision,
                     call_index=index, name=call["name"], result=result)
                emit("tool_internal", cell=cell, decision=decision,
                     call_index=index, name=call["name"], audit=tools.audit_record())
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})
            if status == "tool_error":
                break
    except Exception as exc:
        status = "harness_error"
        emit("harness_error", cell=cell, error_type=type(exc).__name__, error=str(exc)[:500])
    finally:
        emit("cell_end", cell=cell, status=status,
             documents=len(tools.handles.snapshot()["documents"]),
             windows=len(tools.handles.snapshot()["windows"]),
             elapsed_seconds=time.monotonic() - start)
        tools.close()
    return status


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        searcher = BCPlusSearcher()
        try:
            for q in QIDS:
                print(q, run_cell(client, searcher, q), flush=True)
        finally:
            searcher.close()


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
