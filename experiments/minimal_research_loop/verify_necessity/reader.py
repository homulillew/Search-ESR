"""V1 single-call Reader over a frozen genuine Observation bank."""

import hashlib
import json
import re
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
BANK = json.loads((HERE / "OBSERVATIONS.json").read_text())
PROMPT = STUDY / "prompts/reader.md"
FREEZE = HERE / "reader_freeze.json"
EVENTS = HERE / "reader_events.jsonl"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paths():
    own = [STUDY / p for p in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md",
        "FROZEN_STATE.md", "prompts/reader.md", "verify_necessity/PROTOCOL.md",
        "verify_necessity/REVIEW_RUBRIC.md", "verify_necessity/prepare_bank.py",
        "verify_necessity/OBSERVATIONS.json", "verify_necessity/reader.py")]
    prior = [ROOT / p for p in (
        "experiments/evidence_fidelity_loop/evidence_packet/BANK.json",
        "experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json",
        "experiments/model_backend_deepseek/provider.json",
        "experiments/model_backend_deepseek/cache_usage.py")]
    return own + prior


def order():
    return sorted(BANK, key=lambda c: digest(c["case_id"]))


def request(case):
    user = {k: case[k] for k in ("raw_question", "active_gap", "relevant_committed_claims", "observation")}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPT.read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 52 and len({c["qid"] for c in BANK}) == 12
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "base_head": "9cf044ddbfad022cb8e5c0a1e689b715b84421b3",
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths()},
         "prompt_hash": sha(PROMPT), "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "sample_count": 52, "case_order": [c["case_id"] for c in order()],
         "qids": sorted({c["qid"] for c in BANK}),
         "input_hashes": {c["case_id"]: {k: digest(c[k]) for k in (
             "historical_origin", "raw_question", "active_gap", "relevant_committed_claims", "observation")}
             for c in BANK},
         "identity_hashes": {c["case_id"]: {k: digest(c["observation"][k]) for k in
             ("doc_ref", "window_ref", "title", "url", "date", "text")} for c in BANK},
         "request_hashes": {c["case_id"]: digest(request(c)) for c in BANK},
         "schema": {"findings": [{"statement": "nonempty string"}], "max_findings": 3},
         "failure_policy": "One Reader request per observation, max_retries=0, no repair or best-of; failed/invalid outputs retained as empty natural Findings."}
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {"sources": f["source_hashes"] == {str(p.relative_to(ROOT)): sha(p) for p in paths()},
              "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname,
                  "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                  "max_retries": CONFIG["max_retries"]},
              "order": f["case_order"] == [c["case_id"] for c in order()],
              "requests": all(f["request_hashes"][c["case_id"]] == digest(request(c)) for c in BANK)}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")


def validate(value):
    if not isinstance(value, dict) or set(value) != {"findings"} or not isinstance(value["findings"], list):
        raise ValueError("top_level_schema")
    if len(value["findings"]) > 3:
        raise ValueError("more_than_three")
    for x in value["findings"]:
        if not isinstance(x, dict) or set(x) != {"statement"} or not isinstance(x["statement"], str) or not x["statement"].strip():
            raise ValueError("finding_schema_or_forbidden_field")
        if re.search(r"\b(?:D|W|C)\d+\b|https?://|www\.", x["statement"], re.IGNORECASE):
            raise ValueError("model_generated_identity_or_location")
    return value


def one(client, case):
    cid = case["case_id"]
    req = request(case)
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
        return {"cell": cid, "output": value, "source_window": case["observation"]["window_ref"],
                "error": None}
    except Exception as exc:
        emit("cell_error", cell=cid, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - t)
        return {"cell": cid, "output": {"findings": []},
                "source_window": case["observation"]["window_ref"], "error": type(exc).__name__}


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
    assert len(outcomes) == len(BANK)
    (HERE / "reader_outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
