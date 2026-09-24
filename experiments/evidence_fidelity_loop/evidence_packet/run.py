"""Frozen paired text/full evidence reading using DeepSeek; no retries."""

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
BANK = json.loads((HERE / "BANK.json").read_text())
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
PROMPT = STUDY / "prompts/evidence_packet_reader.md"
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paths():
    own = [STUDY / p for p in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md",
           "FROZEN_STATE.md", "prompts/evidence_packet_reader.md",
           "evidence_packet/prepare_bank.py", "evidence_packet/BANK.json",
           "evidence_packet/REVIEW_RUBRIC.md", "evidence_packet/run.py")]
    prior = [ROOT / p for p in (
        "experiments/gap_evidence_claim_loop/finding_extraction/BANK.json",
        "experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json",
        "experiments/model_backend_deepseek/provider.json",
        "experiments/model_backend_deepseek/cache_usage.py")]
    return own + prior


def order():
    return sorted(BANK, key=lambda c: digest(c["case_id"]))


def arms(i):
    return ("T", "P") if i % 2 == 0 else ("P", "T")


def request(case, arm):
    w = case["observation"]
    observation = {"window_ref": w["window_ref"], "text": w["text"]}
    if arm == "P":
        observation = {"doc_ref": w["doc_ref"], "title": w["title"], "url": w["url"], **observation}
    user = {"raw_question": case["raw_question"], "active_gap": case["active_gap"],
            "relevant_committed_claims": case["relevant_committed_claims"],
            "observation": observation}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPT.read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 44 and len({c["qid"] for c in BANK}) == 12
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "base_head": "4b460c76f9ec9aaeaa5b4255f142d8c31c64b26d",
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths()},
         "prompt_hash": sha(PROMPT), "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "case_order": [c["case_id"] for c in order()],
         "arm_order": {c["case_id"]: list(arms(i)) for i, c in enumerate(order())},
         "qids": sorted({c["qid"] for c in BANK}),
         "case_hashes": {c["case_id"]: {k: digest(c[k]) for k in (
             "historical_origin", "raw_question", "active_gap", "relevant_committed_claims",
             "observation", "required_findings", "forbidden_inferences", "category",
             "metadata_required")} for c in BANK},
         "identity_hashes": {c["case_id"]: {k: digest(c["observation"][k]) for k in
             ("doc_ref", "window_ref", "title", "url", "text")} for c in BANK},
         "request_hashes": {c["case_id"] + ":" + a: digest(request(c, a))
                            for c in BANK for a in ("T", "P")},
         "gate": {"precision_min": .95, "recall_min": .90,
                  "identity_min": .90, "temporal_min": .90,
                  "metadata_overreach_max": .05, "T_error_trigger": 5,
                  "P_net_improvement_min": 4, "reverse_worsening_max": 1},
         "sample_count": 44, "arm_count": 2,
         "failure_policy": "One request per case/arm, max_retries=0, no best-of; all errors and invalid responses retained as misses, never repaired."}
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {
        "sources": f["source_hashes"] == {str(p.relative_to(ROOT)): sha(p) for p in paths()},
        "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname,
            "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
            "max_retries": CONFIG["max_retries"]},
        "order": f["case_order"] == [c["case_id"] for c in order()],
        "requests": all(f["request_hashes"][c["case_id"] + ":" + a] == digest(request(c, a))
                        for c in BANK for a in ("T", "P"))}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                                  "kind": kind, **fields}, ensure_ascii=False) + "\n")


def validate(case, value):
    if not isinstance(value, dict) or set(value) != {"findings"} or not isinstance(value["findings"], list):
        raise ValueError("top_level_schema")
    if len(value["findings"]) > 3:
        raise ValueError("more_than_three_findings")
    for x in value["findings"]:
        if not isinstance(x, dict) or set(x) != {"statement", "evidence_refs"}:
            raise ValueError("finding_schema")
        if not isinstance(x["statement"], str) or not x["statement"].strip():
            raise ValueError("empty_statement")
        if x["evidence_refs"] != [case["observation"]["window_ref"]]:
            raise ValueError("invalid_ref")
    return value


def one(client, case, arm):
    cell = case["case_id"] + ":" + arm
    req = request(case, arm)
    emit("model_request", cell=cell, request=req, request_hash=digest(req))
    t = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("model_response", cell=cell, response=raw, cache_usage=extract(raw),
             latency_seconds=time.monotonic() - t)
        if raw["choices"][0]["finish_reason"] != "stop":
            raise ValueError("abnormal_finish")
        value = validate(case, json.loads(raw["choices"][0]["message"]["content"]))
        emit("cell_outcome", cell=cell, output=value)
        return {"cell": cell, "output": value, "error": None}
    except Exception as exc:
        emit("cell_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - t)
        return {"cell": cell, "output": {"findings": []}, "error": type(exc).__name__}


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    tasks = [(c, a) for i, c in enumerate(order()) for a in arms(i)]
    outcomes = {}
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(one, client, c, a): (c, a) for c, a in tasks}
            for future in as_completed(futures):
                result = future.result()
                outcomes[result["cell"]] = result
                print(result["cell"], "ok" if result["error"] is None else result["error"], flush=True)
    assert len(outcomes) == len(tasks)
    (HERE / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
