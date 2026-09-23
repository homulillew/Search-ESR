"""Receding-horizon broad plan handoff under v3a and Orthogonal Search."""

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS, SearchFindTools
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from experiments.model_backend_atria.planning_probe.run import DIAGNOSTIC
from experiments.model_backend_atria.planning_probe.analyze import parse
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from experiments.search_find_v3b.orthogonal_search.run_partial import checkpoint, restore_prefix
from experiments.research_state_plan_handoff.plan_handoff_one_step.run import card, plan

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OLD = ROOT / "experiments/model_backend_deepseek"
CONFIG = json.loads((OLD / "provider.json").read_text())
SELECT = json.loads((OLD / "orthogonal_partial/SELECTION.json").read_text())["cells"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
HORIZON = 4
FIELD_NAMES = ("Current unresolved need", "Expected source type", "Best scope", "Target document/window")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def initial_params(q, seq):
    original, _, _ = checkpoint(q, seq)
    params = json.loads(json.dumps(original))
    params["model"] = CONFIG["model"]
    return params


def parse_plan(raw):
    choice = (raw.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content") or ""
    parsed = parse(content)
    fields = {k: parsed[k] for k in FIELD_NAMES}
    valid = all(isinstance(v, str) and v.strip() for v in fields.values()) and \
            parsed["parsed_scope"] in {"corpus", "document", "window", "stop"}
    return fields, bool(valid), parsed["parsed_scope"]


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if len(SELECT) != 4 or len({(x["qid"], x["seq"]) for x in SELECT}) != 4:
        raise ValueError("Expected four frozen M3 cells")
    p1 = [json.loads(line) for line in (STUDY / "plan_handoff_one_step/events.jsonl").open()]
    if len([e for e in p1 if e["kind"] in ("api_response", "api_error")]) != 13:
        raise ValueError("P1 not complete")
    sources = ["experiments/research_state_plan_handoff/plan_orthogonal_interaction/run.py",
               "experiments/research_state_plan_handoff/plan_orthogonal_interaction/RUBRIC.json",
               "experiments/research_state_plan_handoff/plan_handoff_one_step/run.py",
               "experiments/model_backend_atria/planning_probe/run.py",
               "experiments/model_backend_atria/planning_probe/analyze.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/search_find_agent.py", "llm_chat/search_find_v3b_agent.py",
               "llm_chat/agent.py", "llm_chat/raw_windows.py",
               "BCPlus/scripts/search_bcplus.py"]
    historical = ["experiments/model_backend_deepseek/planning_probe/events.jsonl",
                  "experiments/model_backend_deepseek/planning_probe/mechanical_summary.json",
                  "experiments/model_backend_deepseek/orthogonal_partial/SELECTION.json",
                  "experiments/model_backend_deepseek/orthogonal_partial/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_handoff_one_step/mechanical_summary.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "selection": SELECT, "arms": ["P0H1", "P1H1"], "sample_count": 8,
           "horizon_actor_decisions": HORIZON,
           "decision_1_plan": "reuse exact historical M1 plan at same prefix",
           "decision_2_plus": "new no-tool M1 diagnostic on current real history",
           "actor_history": "current prefix and real tool observations plus only latest card",
           "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
           "agent_prompt_sha256": hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
           "diagnostic_sha256": hashlib.sha256(DIAGNOSTIC.encode()).hexdigest(),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "historical_sha256": {p: sha(ROOT / p) for p in historical},
           "first_plan_sha256": {f"{x['qid']}:{x['seq']}": digest(plan(x["qid"], x["seq"])) for x in SELECT},
           "initial_request_sha256": {f"{x['qid']}:{x['seq']}": digest(initial_params(x["qid"], x["seq"])) for x in SELECT},
           "failure_policy": "eight cells once; stop cell on first provider, planner, validation, or tool error"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["historical_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and
                 doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname,
              "selection": doc["selection"] == SELECT and doc["sample_count"] == 8,
              "schema": doc["tool_schema_sha256"] == digest(SEARCH_FIND_TOOLS),
              "prompt": doc["agent_prompt_sha256"] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
              "diagnostic": doc["diagnostic_sha256"] == hashlib.sha256(DIAGNOSTIC.encode()).hexdigest(),
              "first_plans": all(digest(plan(x["qid"], x["seq"])) == doc["first_plan_sha256"][f"{x['qid']}:{x['seq']}"] for x in SELECT),
              "requests": all(digest(initial_params(x["qid"], x["seq"])) == doc["initial_request_sha256"][f"{x['qid']}:{x['seq']}"] for x in SELECT),
              "horizon": doc["horizon_actor_decisions"] == HORIZON and doc["max_retries"] == 0}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    for x in SELECT:
        _, prior, _ = checkpoint(x["qid"], x["seq"])
        for cls in (SearchFindTools, OrthogonalSearchFindTools):
            tools = cls()
            try:
                restore_prefix(tools, prior)
            finally:
                tools.close()


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                              "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def request_planner(client, cell, decision, history):
    params = {"model": CONFIG["model"],
              "messages": history + [{"role": "user", "content": DIAGNOSTIC}],
              "stream": False}
    emit("planner_request", cell=cell, decision=decision, request=params)
    try:
        raw = client.chat.completions.create(**params).model_dump(mode="json")
    except Exception as exc:
        emit("planner_error", cell=cell, decision=decision,
             error_type=type(exc).__name__, http_status=getattr(exc, "status_code", None),
             error=str(exc)[:500])
        return None, "planner_api_error"
    fields, valid, scope = parse_plan(raw)
    emit("planner_response", cell=cell, decision=decision, response=raw,
         fields=fields, parsed_scope=scope, valid=valid, cache_usage=extract(raw))
    return fields, None if valid else "planner_invalid"


def run_cell(client, searcher, x, harness):
    q, seq = x["qid"], x["seq"]
    cell = f"{q}:{seq}:{harness}H1"
    original, prior, _ = checkpoint(q, seq)
    tools = SearchFindTools() if harness == "P0" else OrthogonalSearchFindTools()
    status = "horizon"
    started = time.monotonic()
    try:
        restored = restore_prefix(tools, prior)
        tools.searcher = searcher
        emit("cell_start", cell=cell, restoration=restored, selection_role=x["role"])
        history = json.loads(json.dumps(original["messages"]))
        for decision in range(1, HORIZON + 1):
            if decision == 1:
                fields = plan(q, seq)
                emit("planner_reuse", cell=cell, decision=decision,
                     source_cell=f"{q}:{seq}:{CONFIG['model']}",
                     fields=fields, plan_sha256=digest(fields))
            else:
                fields, error = request_planner(client, cell, decision, history)
                if error:
                    status = error
                    break
            params = initial_params(q, seq)
            params["messages"] = history + [{"role": "user", "content": card(fields)}]
            emit("actor_request", cell=cell, decision=decision, request=params,
                 current_plan=fields, plan_sha256=digest(fields))
            began = time.monotonic()
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
            except Exception as exc:
                emit("actor_error", cell=cell, decision=decision,
                     error_type=type(exc).__name__, http_status=getattr(exc, "status_code", None),
                     error=str(exc)[:500], elapsed_seconds=time.monotonic() - began)
                status = "actor_api_error"
                break
            choice = (raw.get("choices") or [{}])[0]
            parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                         allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
            emit("actor_response", cell=cell, decision=decision, response=raw,
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
            history.append(assistant)
            for index, call in enumerate(parsed, 1):
                emit("tool_start", cell=cell, decision=decision,
                     call_index=index, name=call["name"], arguments=call["arguments"])
                try:
                    result = tools.execute(call["name"], call["arguments"])
                except Exception as exc:
                    emit("tool_error", cell=cell, decision=decision,
                         call_index=index, error_type=type(exc).__name__, error=str(exc)[:500])
                    status = "tool_error"
                    break
                emit("tool_result", cell=cell, decision=decision,
                     call_index=index, name=call["name"], result=result)
                emit("tool_internal", cell=cell, decision=decision,
                     call_index=index, name=call["name"], audit=tools.audit_record())
                history.append({"role": "tool", "tool_call_id": call["id"],
                                "content": json.dumps(result, ensure_ascii=False)})
            if status == "tool_error":
                break
    except Exception as exc:
        status = "harness_error"
        emit("harness_error", cell=cell, error_type=type(exc).__name__, error=str(exc)[:500])
    finally:
        emit("cell_end", cell=cell, status=status,
             elapsed_seconds=time.monotonic() - started)
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
            for x in SELECT:
                for harness in ("P0", "P1"):
                    print(x["qid"], x["seq"], harness,
                          run_cell(client, searcher, x, harness), flush=True)
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
