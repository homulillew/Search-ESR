"""Frozen F2 verifier-gated minimal Claim commit versus direct admission."""

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
F1 = STUDY / "finding_extraction"
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
BANK = json.loads((HERE / "BANK.json").read_text())
PROMPT = (STUDY / "prompts/finding_verifier.md").read_text()
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_paths():
    paths = [STUDY / x for x in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md", "FROZEN_STATE.md",
             "prompts/finding_verifier.md", "claim_commit/PROTOCOL.md",
             "claim_commit/REVIEW_RUBRIC.md", "claim_commit/prepare_bank.py",
             "claim_commit/BANK.json", "claim_commit/run.py")]
    paths += [F1 / x for x in ("BANK.json", "outcomes.json", "REVIEWS.json",
                              "PRIVATE_MAPPING.json", "results.json")]
    paths += [ROOT / "experiments/model_backend_deepseek/provider.json",
              ROOT / "experiments/model_backend_deepseek/cache_usage.py"]
    return paths


def source_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}


def order():
    return sorted(BANK, key=lambda p: digest(p["packet_id"]))


def request(packet):
    user = {"active_gap": packet["active_gap"], "finding": packet["finding"],
            "exact_observation": {"ref": packet["new_observation"]["ref"],
                                  "text": packet["new_observation"]["text"]},
            "relevant_committed_claims": packet["existing_claims"]}
    assert "review" not in user
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def commit(packet):
    cids = [int(c["claim_id"][1:]) for c in packet["existing_claims"] if c["claim_id"].startswith("C") and c["claim_id"][1:].isdigit()]
    return {"claim_id": f"C{max(cids, default=0)+1}",
            "statement": packet["finding"]["statement"],
            "evidence_refs": packet["finding"]["evidence_refs"], "version": 1}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    f1 = json.loads((F1 / "results.json").read_text())
    assert f1["f1_pass"]
    assert len(BANK) == 53 and sum(p["part"] == "A" for p in BANK) == 38
    assert sum(p["part"] == "B" for p in BANK) == 15
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": source_hashes(),
         "prompt_sha256": digest(PROMPT),
         "schema_sha256": digest({"verdict": ["supported", "insufficient"], "reason": "nonempty string"}),
         "packet_order": [p["packet_id"] for p in order()],
         "packet_ids": [p["packet_id"] for p in BANK],
         "qids_checkpoints": {p["packet_id"]: [p["qid"], p["source_checkpoint"]] for p in BANK},
         "gap_hashes": {p["packet_id"]: digest(p["active_gap"]) for p in BANK},
         "existing_claim_hashes": {p["packet_id"]: digest(p["existing_claims"]) for p in BANK},
         "observation_hashes": {p["packet_id"]: digest(p["new_observation"]) for p in BANK},
         "finding_hashes": {p["packet_id"]: digest(p["finding"]) for p in BANK},
         "review_hash": sha(HERE / "BANK.json"),
         "request_hashes": {p["packet_id"]: digest(request(p)) for p in BANK},
         "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "arm_order": ["D mechanical", "V verifier"],
         "gate": {"committed_precision_min": .95, "commit_recall_min": .90,
                  "false_promotion_max": .05, "stress_rejection_min": .90,
                  "direct_false_promotion_trigger": 4},
         "failure_policy": "One V call per packet; max_retries=0. Invalid/failed verdict means insufficient, remains in denominator. D deterministic. No best-of."}
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {"source_hashes": f["source_hashes"] == source_hashes(),
              "provider": f["provider"] == {
                  "host": urlsplit(CONFIG["base_url"]).hostname,
                  "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                  "max_retries": CONFIG["max_retries"]},
              "order": f["packet_order"] == [p["packet_id"] for p in order()],
              "bank": f["review_hash"] == sha(HERE / "BANK.json"),
              "requests": all(f["request_hashes"][p["packet_id"]] == digest(request(p)) for p in BANK)}
    (HERE / "gate.txt").write_text("\n".join(("PASS " if ok else "FAIL ") + key
                                                for key, ok in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                                  "kind": kind, **fields}, ensure_ascii=False) + "\n")


def validate(value):
    if not isinstance(value, dict) or set(value) != {"verdict", "reason"}:
        raise ValueError("verdict_schema")
    if value["verdict"] not in ("supported", "insufficient"):
        raise ValueError("invalid_verdict")
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        raise ValueError("empty_reason")
    return value


def one_packet(client, packet):
    pid = packet["packet_id"]
    req = request(packet)
    emit("model_request", packet_id=pid, request=req, request_hash=digest(req))
    started = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("model_response", packet_id=pid, response=raw,
             cache_usage=extract(raw), latency_seconds=time.monotonic() - started)
        if raw["choices"][0]["finish_reason"] != "stop":
            raise ValueError("abnormal_finish")
        verdict = validate(json.loads(raw["choices"][0]["message"]["content"]))
        err = None
    except Exception as exc:
        emit("cell_error", packet_id=pid, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - started)
        verdict = {"verdict": "insufficient", "reason": "failed or invalid verifier response"}
        err = type(exc).__name__
    candidate = commit(packet)
    outcome = {"packet_id": pid, "verdict": verdict, "error": err,
               "D_commit": candidate,
               "V_commit": candidate if verdict["verdict"] == "supported" else None}
    emit("cell_outcome", packet_id=pid, output=outcome)
    return outcome


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
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(one_packet, client, p): p for p in order()}
            for future in as_completed(futures):
                p = futures[future]
                result = future.result()
                outcomes[p["packet_id"]] = result
                print(p["packet_id"], "ok" if result["error"] is None else result["error"], flush=True)
    assert len(outcomes) == len(BANK)
    (HERE / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
