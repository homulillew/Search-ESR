"""Four-checkpoint DeepSeek P0/P1 partial continuation under the frozen harnesses."""

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
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS, SearchFindTools
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from experiments.search_find_v3b.orthogonal_search.run_partial import checkpoint, restore_prefix

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((STUDY / "provider.json").read_text())
SELECT = json.loads((HERE / "SELECTION.json").read_text())
BASELINES = json.loads((STUDY / "BASELINE_FINGERPRINTS.json").read_text())["sha256"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def cell_params(q, seq, messages):
    original, _, _ = checkpoint(q, seq)
    params = json.loads(json.dumps(original))
    params["model"] = CONFIG["model"]
    params["messages"] = messages
    return params


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if not all(sha(ROOT / p) == h for p, h in BASELINES.items()):
        raise AssertionError("Baseline changed")
    if SELECT["decisions_per_cell"] != 4 or len(SELECT["cells"]) != 4:
        raise AssertionError("M3 selection mismatch")
    sources = ["experiments/model_backend_deepseek/orthogonal_partial/run.py",
               "experiments/model_backend_deepseek/orthogonal_partial/SELECTION.json",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/agent.py", "llm_chat/search_find_agent.py",
               "llm_chat/search_find_v3b_agent.py", "llm_chat/raw_windows.py",
               "llm_chat/window_locator.py", "llm_chat/window_units.py",
               "BCPlus/scripts/search_bcplus.py"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "selection": SELECT["cells"], "arm_order": ["P0", "P1"],
           "horizon_api_decisions": 4, "replicates": 1,
           "model": CONFIG["model"], "base_url_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
           "selection_sha256": sha(HERE / "SELECTION.json"),
           "baseline_fingerprints_sha256": sha(STUDY / "BASELINE_FINGERPRINTS.json"),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "initial_request_sha256": {f"{x['qid']}:{x['seq']}":
              digest(cell_params(x["qid"], x["seq"], checkpoint(x["qid"], x["seq"])[0]["messages"]))
              for x in SELECT["cells"]},
           "continuation": "natural stop only; no forced final answer",
           "failure_policy": "All eight cells once, stop each on error; preserve raw output and cache usage"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"baseline": all(sha(ROOT / p) == h for p, h in BASELINES.items()) and
              sha(STUDY / "BASELINE_FINGERPRINTS.json") == doc["baseline_fingerprints_sha256"],
              "sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "selection": sha(HERE / "SELECTION.json") == doc["selection_sha256"],
              "schema": digest(SEARCH_FIND_TOOLS) == doc["tool_schema_sha256"],
              "model": doc["model"] == CONFIG["model"] and
                       doc["base_url_host"] == urlsplit(CONFIG["base_url"]).hostname,
              "requests": all(digest(cell_params(x["qid"], x["seq"],
                         checkpoint(x["qid"], x["seq"])[0]["messages"])) ==
                         doc["initial_request_sha256"][f"{x['qid']}:{x['seq']}"] for x in SELECT["cells"]),
              "horizon": doc["horizon_api_decisions"] == 4 and doc["replicates"] == 1}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    # Verify both restored action spaces against the exact prefix before any calls.
    for x in SELECT["cells"]:
        _, prior, _ = checkpoint(x["qid"], x["seq"])
        for cls in (SearchFindTools, OrthogonalSearchFindTools):
            tools = cls()
            try:
                restore_prefix(tools, prior)
            finally:
                tools.close()


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run_cell(client, searcher, x, arm):
    q, seq = x["qid"], x["seq"]
    cell = f"{q}:{seq}:{arm}:{CONFIG['model']}"
    original, prior, _ = checkpoint(q, seq)
    tools = SearchFindTools() if arm == "P0" else OrthogonalSearchFindTools()
    status = "horizon"
    start = time.monotonic()
    try:
        restoration = restore_prefix(tools, prior)
        tools.searcher = searcher
        emit("cell_start", cell=cell, role=x["role"], restoration=restoration)
        messages = json.loads(json.dumps(original["messages"]))
        for decision in range(1, 5):
            params = cell_params(q, seq, messages)
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
        emit("cell_end", cell=cell, role=x["role"], status=status,
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
            for x in SELECT["cells"]:
                for arm in ("P0", "P1"):
                    print(x["qid"], x["seq"], arm, run_cell(client, searcher, x, arm), flush=True)
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
