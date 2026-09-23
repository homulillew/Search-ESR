"""Question-only versus evidence-conditioned single AtomicNeed handoff."""

import hashlib
import json
import re
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
from experiments.search_find_v3b.orthogonal_search.run_partial import checkpoint, load_events
from experiments.research_state_plan_handoff.plan_handoff_one_step.run import h0_request

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OLD = ROOT / "experiments/model_backend_deepseek"
CONFIG = json.loads((OLD / "provider.json").read_text())
SELECT = json.loads((HERE / "SELECTION.json").read_text())["cells"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"

A1_PROMPT = ("Diagnostic only. You may use ONLY the original question below; no search results, candidate guesses, or document handles are available. "
 "Form at most ONE currently verifiable atomic information need chiefly answerable by one source type. "
 "Do not guess an unnamed entity, turn a range into an exact fact, or commit to a specific document. "
 "If a defensible atomic need cannot be formed, use none. Do not call tools.\n\n"
 "Original question:\n{question}\n\nReturn exactly one line per field, with the value on the same line as its label:\n"
 "Active atomic need:\nExpected source type:\nGrounding: question_only\nTarget: none")
A2_PROMPT = ("Diagnostic only. Using ONLY the original question and source observations visible in this conversation, "
 "form at most ONE currently verifiable atomic information need chiefly answerable by one source type. "
 "Treat candidates in prior reasoning as hypotheses, not evidence. Do not copy long source text or use future/gold information. "
 "If no defensible atomic need exists, use none. Do not call tools.\n\n"
 "Return exactly one line per field, with the value on the same line as its label:\n"
 "Active atomic need:\nExpected source type:\nGrounding: question_only | hypothesis_bound | evidence_bound\n"
 "Recommended scope: corpus | document | window | stop\nTarget: D# | W# | none\n"
 "Basis refs: question and/or visible D#/W# refs")
CARD_PREFIX = "Current research control state:\n\n"
CARD_SUFFIX = ("\n\nThis state records the current research assessment. "
               "Choose the next action normally using the available tools.")
PATTERNS = {"need": "Active atomic need", "source": "Expected source type",
            "grounding": "Grounding", "scope": "Recommended scope",
            "target": "Target", "basis": "Basis refs"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def question(q):
    first = next(e["request"] for e in load_events(q) if e["kind"] == "api_request")
    users = [m["content"] for m in first["messages"] if m["role"] == "user"]
    if len(users) != 1:
        raise ValueError("Expected one original user question")
    return users[0]


def prefix(q, seq):
    original, _, _ = checkpoint(q, seq)
    return json.loads(json.dumps(original["messages"]))


def planner_request(arm, q, seq=None):
    if arm == "A1":
        messages = [{"role": "user", "content": A1_PROMPT.format(question=question(q))}]
    elif arm == "A2":
        messages = prefix(q, seq) + [{"role": "user", "content": A2_PROMPT}]
    else:
        raise ValueError(arm)
    return {"model": CONFIG["model"], "messages": messages, "stream": False}


def field(content, label):
    match = re.search(rf"(?im)^[ \t]*{re.escape(label)}[ \t]*:[ \t]*(.*)$", content or "")
    return match.group(1).strip() if match else ""


def parse_plan(raw, arm):
    content = ((raw.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    names = ("need", "source", "grounding", "target") if arm == "A1" else tuple(PATTERNS)
    result = {k: field(content, PATTERNS[k]) for k in names}
    if arm == "A1":
        result.update(scope="none", basis="original question")
    valid = all(result.get(k) for k in names)
    valid = valid and result["grounding"] in {"question_only", "hypothesis_bound", "evidence_bound"}
    if arm == "A1":
        valid = valid and result["grounding"] == "question_only" and result["target"] == "none"
    else:
        valid = valid and result["scope"] in {"corpus", "document", "window", "stop"}
    return result, bool(valid)


def card(plan):
    return (CARD_PREFIX + f"Active atomic need:\n{plan['need']}\n\n"
      f"Expected source type:\n{plan['source']}\n\n"
      f"Grounding:\n{plan['grounding']}\n\n"
      f"Recommended scope:\n{plan['scope']}\n\n"
      f"Current target:\n{plan['target']}\n\n"
      f"Basis refs:\n{plan['basis']}" + CARD_SUFFIX)


def actor_request(q, seq, plan):
    params = json.loads(json.dumps(h0_request(q, seq)))
    params["messages"].append({"role": "user", "content": card(plan)})
    return params


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if len(SELECT) != 8 or len({(x["qid"], x["seq"]) for x in SELECT}) != 8:
        raise ValueError("Expected eight selected cells")
    p2 = [json.loads(line) for line in (STUDY / "plan_orthogonal_interaction/events.jsonl").open()]
    if len([e for e in p2 if e["kind"] == "cell_end"]) != 8:
        raise ValueError("P2 not complete")
    sources = ["experiments/research_state_plan_handoff/atomic_need_timing/run.py",
               "experiments/research_state_plan_handoff/atomic_need_timing/analyze.py",
               "experiments/research_state_plan_handoff/atomic_need_timing/RUBRIC.json",
               "experiments/research_state_plan_handoff/atomic_need_timing/SELECTION.json",
               "experiments/research_state_plan_handoff/plan_handoff_one_step/run.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/search_find_agent.py"]
    historical = ["experiments/model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json",
                  "experiments/model_backend_deepseek/planning_probe/mechanical_summary.json",
                  "experiments/model_backend_deepseek/natural_action_probe/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_handoff_one_step/mechanical_summary.json",
                  "experiments/research_state_plan_handoff/plan_orthogonal_interaction/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_orthogonal_interaction/mechanical_summary.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "selection": SELECT, "a1_planner_samples": 2, "a2_planner_samples": 8,
           "actor_samples": 16, "tools_executed": False,
           "actor_order": "alternating A1,A2 on even selection indices; A2,A1 on odd",
           "a1_prompt_sha256": hashlib.sha256(A1_PROMPT.encode()).hexdigest(),
           "a2_prompt_sha256": hashlib.sha256(A2_PROMPT.encode()).hexdigest(),
           "card_prefix": CARD_PREFIX, "card_suffix": CARD_SUFFIX,
           "tool_schema_sha256": digest(SEARCH_FIND_TOOLS),
           "agent_prompt_sha256": hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "historical_sha256": {p: sha(ROOT / p) for p in historical},
           "question_sha256": {q: hashlib.sha256(question(q).encode()).hexdigest() for q in ("546", "1094")},
           "prefix_sha256": {f"{x['qid']}:{x['seq']}": digest(prefix(x["qid"], x["seq"])) for x in SELECT},
           "failure_policy": "one planner response per A1 qid and A2 checkpoint; one Actor response per arm/checkpoint; no selective retry"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["historical_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname,
              "selection": doc["selection"] == SELECT and doc["actor_samples"] == 16,
              "prompts": doc["a1_prompt_sha256"] == hashlib.sha256(A1_PROMPT.encode()).hexdigest() and
                         doc["a2_prompt_sha256"] == hashlib.sha256(A2_PROMPT.encode()).hexdigest(),
              "card": doc["card_prefix"] == CARD_PREFIX and doc["card_suffix"] == CARD_SUFFIX,
              "schema": doc["tool_schema_sha256"] == digest(SEARCH_FIND_TOOLS),
              "agent_prompt": doc["agent_prompt_sha256"] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
              "questions": all(hashlib.sha256(question(q).encode()).hexdigest() == h for q, h in doc["question_sha256"].items()),
              "prefixes": all(digest(prefix(x["qid"], x["seq"])) == doc["prefix_sha256"][f"{x['qid']}:{x['seq']}"] for x in SELECT),
              "one_step": doc["tools_executed"] is False and doc["max_retries"] == 0}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **fields}, ensure_ascii=False) + "\n")
        out.flush()


def call_planner(client, arm, q, seq=None):
    cell = f"{q}:{seq if seq is not None else 'question'}:{arm}"
    params = planner_request(arm, q, seq)
    emit("planner_request", cell=cell, request=params)
    try:
        raw = client.chat.completions.create(**params).model_dump(mode="json")
        fields, valid = parse_plan(raw, arm)
        emit("planner_response", cell=cell, response=raw, fields=fields,
             valid=valid, cache_usage=extract(raw))
        return fields if valid else None
    except Exception as exc:
        emit("planner_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
        return None


def call_actor(client, arm, q, seq, fields):
    cell = f"{q}:{seq}:{arm}"
    if fields is None:
        emit("actor_skipped", cell=cell, reason="planner_failed_or_invalid")
        print(cell, "skipped", flush=True)
        return
    params = actor_request(q, seq, fields)
    emit("actor_request", cell=cell, request=params, plan=fields,
         plan_sha256=digest(fields))
    try:
        raw = client.chat.completions.create(**params).model_dump(mode="json")
        choice = (raw.get("choices") or [{}])[0]
        parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                      allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
        emit("actor_response", cell=cell, response=raw,
             raw_finish_reason=choice.get("finish_reason"),
             raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
             parsed_calls=parsed, validation=error or "valid", cache_usage=extract(raw))
        print(cell, "response", error or "valid", flush=True)
    except Exception as exc:
        emit("actor_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
        print(cell, "error", type(exc).__name__, flush=True)


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        a1 = {q: call_planner(client, "A1", q) for q in ("546", "1094")}
        for index, x in enumerate(SELECT):
            q, seq = x["qid"], x["seq"]
            a2 = call_planner(client, "A2", q, seq)
            order = ("A1", "A2") if index % 2 == 0 else ("A2", "A1")
            for arm in order:
                call_actor(client, arm, q, seq, a1[q] if arm == "A1" else a2)


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
