"""Contemporaneous B/C one-step resolved projection intervention."""

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
from experiments.research_state_plan_handoff.plan_handoff_one_step.run import (
    CASES, CONFIG, digest, h0_request,
)
from experiments.research_state_qualification.qualification_upper_bound.run import (
    LABELS, request as appended_request,
)

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
ANNOTATIONS = json.loads((HERE / "PROJECTION_ANNOTATIONS.json").read_text())["rows"]
ROWS = {(r["qid"], r["seq"]): r for r in ANNOTATIONS}
CARD_SUFFIX = ("The promoted target, when present, is a source judged suitable for directly testing the current verification gap.\n"
               "Other hypotheses remain in the existing conversation history and are not promoted here.\n\n"
               "Choose the next action normally using the available tools.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolved_card(row):
    return ("Current research control state:\n\n"
            f"Current verification gap:\n{row['current_verification_gap']}\n\n"
            f"Required evidence/source type:\n{row['required_source_type']}\n\n"
            f"Promoted target:\n{row['promoted_target']}\n\n" + CARD_SUFFIX)


def request(q, seq, arm):
    if arm == "B":
        return json.loads(json.dumps(appended_request(q, seq)))
    if arm != "C":
        raise ValueError(arm)
    params = json.loads(json.dumps(h0_request(q, seq)))
    params["messages"].append({"role": "user", "content": resolved_card(ROWS[(q, seq)])})
    return params


def validate_design():
    if len(ANNOTATIONS) != 13 or len(ROWS) != 13 or set(ROWS) != set(CASES):
        raise ValueError("Projection annotations must cover every P1/R1 case once")
    for q, seq in CASES:
        row = ROWS[(q, seq)]
        old = LABELS[(q, seq)]
        expected = old["candidate_target"] if old["status"] == "inspectable" else "none"
        if row["promoted_target"] != expected:
            raise ValueError(f"Promotion mapping failed: {q}:{seq}")
        if not row["current_verification_gap"] or not row["required_source_type"] or not row["review_reason"]:
            raise ValueError(f"Incomplete projection: {q}:{seq}")
        if expected == "none" and re.search(r"\b[DW]\d+\b", resolved_card(row)):
            raise ValueError(f"Unpromoted handle leaked into C card: {q}:{seq}")
        b, c = request(q, seq, "B"), request(q, seq, "C")
        if b["messages"][:-2] != c["messages"][:-1] or \
           b["tools"] != c["tools"] or b["model"] != c["model"]:
            raise ValueError(f"B/C prefix, model or schema differs: {q}:{seq}")
        if b != appended_request(q, seq):
            raise ValueError(f"B is not exact R1 replay: {q}:{seq}")


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_design()
    source_paths = ["experiments/research_state_projection/resolved_control_state/run.py",
                    "experiments/research_state_projection/resolved_control_state/analyze.py",
                    "experiments/research_state_projection/resolved_control_state/EXPERIMENT_PLAN.md",
                    "experiments/research_state_projection/resolved_control_state/RUBRIC.json",
                    "experiments/research_state_projection/resolved_control_state/PROJECTION_ANNOTATIONS.json",
                    "experiments/research_state_projection/HYPOTHESES.md",
                    "experiments/model_backend_deepseek/provider.json",
                    "experiments/model_backend_deepseek/protocol.py",
                    "llm_chat/search_find_agent.py"]
    historical_paths = ["experiments/research_state_qualification/qualification_upper_bound/ANNOTATIONS.json",
                        "experiments/research_state_qualification/qualification_upper_bound/review_packets.json",
                        "experiments/research_state_qualification/qualification_upper_bound/events.jsonl",
                        "experiments/research_state_qualification/qualification_upper_bound/freeze.json",
                        "experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl",
                        "experiments/model_backend_deepseek/natural_action_probe/events.jsonl",
                        "experiments/research_state_projection/r1_gap_reanalysis/action_gap_scores.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "sample_count": 26, "decision_horizon": 1, "tools_executed": False,
           "cases": CASES, "order": {f"{q}:{seq}": ["B", "C"] if i % 2 == 0 else ["C", "B"] for i, (q, seq) in enumerate(CASES)},
           "source_sha256": {p: sha(ROOT / p) for p in source_paths},
           "historical_sha256": {p: sha(ROOT / p) for p in historical_paths},
           "prompt_sha256": hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
           "schema_sha256": digest(SEARCH_FIND_TOOLS),
           "B_request_sha256": {f"{q}:{seq}": digest(request(q, seq, "B")) for q, seq in CASES},
           "C_request_sha256": {f"{q}:{seq}": digest(request(q, seq, "C")) for q, seq in CASES},
           "failure_policy": "one B and one C response per case; no SDK retries, tool execution, selective rerun or repair"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["historical_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and doc["timeout_seconds"] == CONFIG["timeout_seconds"] and doc["max_retries"] == 0,
              "prompt_schema": doc["prompt_sha256"] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest() and doc["schema_sha256"] == digest(SEARCH_FIND_TOOLS),
              "sample": doc["sample_count"] == 26 and doc["decision_horizon"] == 1 and doc["tools_executed"] is False and doc["cases"] == [list(x) for x in CASES],
              "order": doc["order"] == {f"{q}:{seq}": ["B", "C"] if i % 2 == 0 else ["C", "B"] for i, (q, seq) in enumerate(CASES)},
              "requests": all(doc["B_request_sha256"][f"{q}:{seq}"] == digest(request(q, seq, "B")) and doc["C_request_sha256"][f"{q}:{seq}"] == digest(request(q, seq, "C")) for q, seq in CASES)}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) + f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **kwargs):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **kwargs}, ensure_ascii=False) + "\n")
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
        for i, (q, seq) in enumerate(CASES):
            for arm in (("B", "C") if i % 2 == 0 else ("C", "B")):
                cell = f"{q}:{seq}:{arm}"
                params = request(q, seq, arm)
                emit("actor_request", cell=cell, request=params, request_sha256=digest(params))
                try:
                    raw = client.chat.completions.create(**params).model_dump(mode="json")
                    choice = (raw.get("choices") or [{}])[0]
                    calls, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                        allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
                    emit("actor_response", cell=cell, response=raw,
                         raw_finish_reason=choice.get("finish_reason"),
                         raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
                         parsed_calls=calls, validation=error or "valid", cache_usage=extract(raw))
                    print(cell, error or "valid", flush=True)
                except Exception as exc:
                    emit("actor_error", cell=cell, error_type=type(exc).__name__,
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
