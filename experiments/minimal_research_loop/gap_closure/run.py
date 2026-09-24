"""Frozen, paired C0/C1 claim-only closure calls."""

import hashlib
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
BANK = json.loads((HERE / "BANK.json").read_text())
PROMPTS = {arm: STUDY / "prompts" / name for arm, name in
           (("C0", "binary_gap_reviewer.md"), ("C1", "missing_first_gap_reviewer.md"))}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
LOCK = threading.Lock()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def source_paths():
    return [HERE / p for p in ("PROTOCOL.md", "build_bank.py", "BANK.json", "run.py")] + \
        list(PROMPTS.values()) + [ROOT / p for p in (
            "experiments/gap_evidence_claim_loop/claim_commit/BANK.json",
            "experiments/gap_evidence_claim_loop/claim_commit/outcomes.json",
            "experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json",
            "experiments/model_backend_deepseek/provider.json",
            "experiments/model_backend_deepseek/cache_usage.py")]


def order():
    return sorted(((c, arm) for c in BANK for arm in ("C0", "C1")),
                  key=lambda pair: digest(pair[0]["case_id"] + ":" + pair[1]))


def request(case, arm):
    view = {"Question": case["raw_question"], "Active Gap": case["active_gap"],
            "Committed Claims": case["committed_claims"]}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPTS[arm].read_text()},
        {"role": "user", "content": json.dumps(view, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 40 and len({x["qid"] for x in BANK}) == 10
    assert sum(x["review"]["status"] == "resolved" for x in BANK) == 20
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                        "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                        "max_retries": 0},
           "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
           "prompt_hashes": {a: sha(p) for a, p in PROMPTS.items()},
           "case_order": [c["case_id"] + ":" + arm for c, arm in order()],
           "request_hashes": {c["case_id"] + ":" + arm: digest(request(c, arm)) for c, arm in order()},
           "question_hashes": {c["case_id"]: digest(c["raw_question"]) for c in BANK},
           "gap_hashes": {c["case_id"]: digest(c["active_gap"]) for c in BANK},
           "claim_hashes": {c["case_id"]: digest(c["committed_claims"]) for c in BANK},
           "review_hash": digest({c["case_id"]: c["review"] for c in BANK}),
           "sample_count": 80, "tool_schema": "none", "horizon": "one call per arm and packet",
           "gate": {"premature_close_max": .05, "missed_close_max": .10,
                    "fully_resolved_recall_min": .90, "near_complete_rejection_min": .90,
                    "policy_preference": "C0 if both pass"},
           "failure_policy": "One request, max_retries=0; API/schema failures retained as wrong decisions; no replacement."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": doc["source_hashes"] == {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
              "provider": doc["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname,
                 "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                 "max_retries": CONFIG["max_retries"]},
              "order": doc["case_order"] == [c["case_id"] + ":" + arm for c, arm in order()],
              "requests": all(doc["request_hashes"][c["case_id"] + ":" + arm] == digest(request(c, arm))
                              for c, arm in order())}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **data):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                                  **data}, ensure_ascii=False) + "\n")


def validate(output, arm):
    if not isinstance(output, dict):
        raise ValueError("not_dict")
    if arm == "C0":
        if set(output) != {"status"}:
            raise ValueError("schema_keys")
    else:
        if set(output) != {"status", "missing"} or not isinstance(output["missing"], str):
            raise ValueError("schema_keys")
    if output["status"] not in ("resolved", "open"):
        raise ValueError("invalid_status")
    if arm == "C1" and bool(output["missing"].strip()) != (output["status"] == "open"):
        raise ValueError("missing_status_inconsistent")
    return output


def one(client, case, arm):
    cell = case["case_id"] + ":" + arm
    req = request(case, arm)
    emit("model_request", cell=cell, request=req, request_hash=digest(req))
    began = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("model_response", cell=cell, response=raw, cache_usage=extract(raw),
             latency_seconds=time.monotonic() - began)
        if raw["choices"][0]["finish_reason"] != "stop":
            raise ValueError("abnormal_finish")
        output = validate(json.loads(raw["choices"][0]["message"]["content"]), arm)
        emit("cell_outcome", cell=cell, output=output)
        return {"cell": cell, "output": output, "error": None}
    except Exception as exc:
        emit("cell_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - began)
        return {"cell": cell, "output": None, "error": type(exc).__name__}


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    outcomes = {}
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(one, client, c, arm) for c, arm in order()]
            for future in as_completed(futures):
                value = future.result()
                outcomes[value["cell"]] = value
                print(value["cell"], "ok" if value["error"] is None else value["error"], flush=True)
    assert len(outcomes) == 80
    (HERE / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
