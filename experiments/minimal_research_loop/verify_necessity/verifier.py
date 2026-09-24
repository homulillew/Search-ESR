"""V1 single boolean Verify calls on all frozen natural Findings."""

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
CANDIDATES = json.loads((HERE / "CANDIDATES.json").read_text())
LABELS = json.loads((HERE / "ANNOTATIONS.json").read_text())
PROMPT = STUDY / "prompts/verifier.md"
FREEZE = HERE / "verifier_freeze.json"
EVENTS = HERE / "verifier_events.jsonl"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paths():
    own = [STUDY / p for p in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md",
        "FROZEN_STATE.md", "prompts/verifier.md", "verify_necessity/PROTOCOL.md",
        "verify_necessity/REVIEW_RUBRIC.md", "verify_necessity/VERIFIER_PROTOCOL.md",
        "verify_necessity/OBSERVATIONS.json", "verify_necessity/reader_outcomes.json",
        "verify_necessity/CANDIDATES.json", "verify_necessity/ANNOTATIONS.json",
        "verify_necessity/annotate_candidates.py", "verify_necessity/verifier.py")]
    return own + [ROOT / "experiments/model_backend_deepseek/provider.json",
                  ROOT / "experiments/model_backend_deepseek/cache_usage.py"]


def order():
    return sorted(CANDIDATES, key=lambda c: digest(c["candidate_id"]))


def request(candidate):
    user = {"finding": candidate["finding"], "observation": candidate["observation"]}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPT.read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(CANDIDATES) == len(LABELS) == 55
    assert {c["candidate_id"] for c in CANDIDATES} == {l["candidate_id"] for l in LABELS}
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths()},
         "prompt_hash": sha(PROMPT), "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "candidate_count": 55, "reader_packet_count": 52,
         "case_order": [c["candidate_id"] for c in order()],
         "paths": {"D": "deterministic_direct_commit_zero_calls", "V": "one_boolean_verifier_call_per_finding"},
         "question_hashes": {c["candidate_id"]: digest(c["raw_question"]) for c in CANDIDATES},
         "claim_hashes": {c["candidate_id"]: digest(c["relevant_committed_claims"]) for c in CANDIDATES},
         "gap_hashes": {c["candidate_id"]: digest(c["active_gap"]) for c in CANDIDATES},
         "workspace_hashes": {c["candidate_id"]: digest(c["observation"]) for c in CANDIDATES},
         "identity_hashes": {c["candidate_id"]: {k: digest(c["observation"][k]) for k in
             ("doc_ref", "window_ref", "title", "url", "date", "text")} for c in CANDIDATES},
         "finding_hashes": {c["candidate_id"]: digest(c["finding"]) for c in CANDIDATES},
         "label_hash": sha(HERE / "ANNOTATIONS.json"),
         "reader_outcomes_hash": sha(HERE / "reader_outcomes.json"),
         "request_hashes": {c["candidate_id"]: digest(request(c)) for c in CANDIDATES},
         "decision": {"A_direct_source_precision_min": .97, "A_unsupported_lt": 5,
                      "B_unsupported_min": 5, "B_removed_unsupported_min": .60,
                      "B_supported_recall_min": .95, "C_undeployable_recall_lt": .90,
                      "R1_source_precision_min": .97, "R1_claim_precision_min": .95,
                      "R1_supported_recall_min": .95},
         "failure_policy": "One verifier request per natural Finding, max_retries=0, no repair/best-of; all failures retained and counted as false/rejected."}
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {"sources": f["source_hashes"] == {str(p.relative_to(ROOT)): sha(p) for p in paths()},
              "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname,
                  "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                  "max_retries": CONFIG["max_retries"]},
              "order": f["case_order"] == [c["candidate_id"] for c in order()],
              "requests": all(f["request_hashes"][c["candidate_id"]] == digest(request(c)) for c in CANDIDATES)}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")


def validate(value):
    if not isinstance(value, dict) or set(value) != {"supported"} or type(value["supported"]) is not bool:
        raise ValueError("boolean_schema")
    return value


def one(client, candidate):
    cid = candidate["candidate_id"]
    req = request(candidate)
    emit("model_request", cell=cid, request=req, request_hash=digest(req))
    t = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("model_response", cell=cid, response=raw, cache_usage=extract(raw),
             latency_seconds=time.monotonic() - t)
        if raw["choices"][0]["finish_reason"] != "stop":
            raise ValueError("abnormal_finish")
        value = validate(json.loads(raw["choices"][0]["message"]["content"]))
        emit("cell_outcome", cell=cid, output=value)
        return {"cell": cid, "output": value, "error": None}
    except Exception as exc:
        emit("cell_error", cell=cid, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - t)
        return {"cell": cid, "output": {"supported": False}, "error": type(exc).__name__}


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
            futures = {pool.submit(one, client, c): c for c in order()}
            for future in as_completed(futures):
                result = future.result()
                outcomes[result["cell"]] = result
                print(result["cell"], "ok" if result["error"] is None else result["error"], flush=True)
    assert len(outcomes) == len(CANDIDATES)
    (HERE / "verifier_outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
