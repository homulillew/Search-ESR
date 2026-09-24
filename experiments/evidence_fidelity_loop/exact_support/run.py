"""Frozen E2 whole-packet versus exact-pointer verifier calls."""

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
PROMPTS = {"V0": STUDY / "prompts/whole_packet_verifier.md",
           "V1": STUDY / "prompts/support_pointer_verifier.md"}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paths():
    own = [STUDY / p for p in (
        "E1_GATE_AMENDMENT.md", "PROTOCOL.md", "exact_support/PROTOCOL.md",
        "prompts/whole_packet_verifier.md",
        "prompts/support_pointer_verifier.md", "exact_support/prepare_bank.py",
        "exact_support/BANK.json", "exact_support/REVIEW_RUBRIC.md", "exact_support/run.py")]
    prior = [STUDY / p for p in (
        "evidence_packet/BANK.json", "evidence_packet/outcomes.json",
        "evidence_packet/REVIEWS.json", "evidence_packet/results.json")]
    return own + prior + [ROOT / "experiments/model_backend_deepseek/provider.json",
                          ROOT / "experiments/model_backend_deepseek/cache_usage.py"]


def order():
    return sorted(BANK, key=lambda c: digest(c["case_id"]))


def arms(i):
    return ("V0", "V1") if i % 2 == 0 else ("V1", "V0")


def request(case, arm):
    user = {k: case[k] for k in ("raw_question", "active_gap",
                                 "relevant_committed_claims", "finding", "observation")}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPTS[arm].read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 68 and sum(c["origin"] == "all_actual_E1_P_findings" for c in BANK) == 46
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths()},
         "prompt_hashes": {a: sha(p) for a, p in PROMPTS.items()},
         "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "case_order": [c["case_id"] for c in order()],
         "arm_order": {c["case_id"]: list(arms(i)) for i, c in enumerate(order())},
         "qids": sorted({c["qid"] for c in BANK}),
         "case_hashes": {c["case_id"]: {k: digest(c[k]) for k in (
             "source_case", "qid", "raw_question", "active_gap",
             "relevant_committed_claims", "observation", "finding", "review")}
                         for c in BANK},
         "identity_hashes": {c["case_id"]: {k: digest(c["observation"][k]) for k in
             ("doc_ref", "window_ref", "title", "url", "text")} for c in BANK},
         "request_hashes": {c["case_id"] + ":" + a: digest(request(c, a))
                            for c in BANK for a in ("V0", "V1")},
         "sample_count": 68, "stress_count": 22, "arm_count": 2,
         "gate": {"commit_precision_min": .97, "commit_recall_min": .90,
                  "temporal_false_accept_max": .05, "identity_false_accept_max": .05,
                  "sequence_false_accept_max": .05, "pointer_validity_min": .98,
                  "stress_negative_rejection_min": .90, "V0_false_accept_trigger": 5,
                  "V1_net_improvements_min": 4, "reverse_worsening_max": 1},
         "failure_policy": "One request per case/arm; max_retries=0, no best-of. Invalid/malformed V1 pointers reject. All failures and raw responses retained."}
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
                        for c in BANK for a in ("V0", "V1"))}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                                  "kind": kind, **fields}, ensure_ascii=False) + "\n")


def validate(case, arm, value):
    if not isinstance(value, dict):
        raise ValueError("not_object")
    required = {"verdict", "reason"} if arm == "V0" else {
        "verdict", "support", "source_metadata_used", "reason"}
    if set(value) != required or value["verdict"] not in ("supported", "insufficient"):
        raise ValueError("top_level_schema")
    if not isinstance(value["reason"], str):
        raise ValueError("reason_schema")
    if arm == "V0":
        return value, True, None
    w = case["observation"]
    support, meta = value["support"], value["source_metadata_used"]
    if not isinstance(support, list) or not isinstance(meta, list):
        return value, False, "pointer_list_schema"
    if value["verdict"] == "insufficient":
        return value, not support and not meta, None if not support and not meta else "insufficient_with_pointer"
    if not 1 <= len(support) <= 2:
        return value, False, "span_count"
    if len(meta) != len(set(map(str, meta))) or any(m not in ("title", "url") or not w[m] for m in meta):
        return value, False, "metadata_allowlist"
    for span in support:
        if not isinstance(span, dict) or set(span) != {"window_ref", "start", "end"}:
            return value, False, "span_schema"
        a, b = span["start"], span["end"]
        if span["window_ref"] != w["window_ref"] or type(a) is not int or type(b) is not int:
            return value, False, "span_ref_or_offset_type"
        if not 0 <= a < b <= len(w["text"]):
            return value, False, "span_bounds"
        # Bounds above make this slice an exact substring of the current W.
    return value, True, None


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
        value, mechanical_valid, mechanical_error = validate(
            case, arm, json.loads(raw["choices"][0]["message"]["content"]))
        emit("cell_outcome", cell=cell, output=value, mechanical_valid=mechanical_valid,
             mechanical_error=mechanical_error)
        return {"cell": cell, "output": value, "mechanical_valid": mechanical_valid,
                "mechanical_error": mechanical_error, "error": None}
    except Exception as exc:
        emit("cell_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - t)
        return {"cell": cell, "output": None, "mechanical_valid": False,
                "mechanical_error": None, "error": type(exc).__name__}


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
