"""Frozen DeepSeek A/B/C one-Observation Finding extraction."""

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
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
LOCK = threading.Lock()
PROMPTS = {"A": STUDY / "prompts/observation_fact_reader.md",
           "B": STUDY / "prompts/gap_fact_reader.md",
           "C": STUDY / "prompts/gap_claim_fact_reader.md"}


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_paths():
    own = [STUDY / name for name in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md",
           "FROZEN_STATE.md", "finding_extraction/PROTOCOL.md",
           "finding_extraction/REVIEW_RUBRIC.md", "finding_extraction/prepare_bank.py",
           "finding_extraction/BANK.json", "finding_extraction/run.py")]
    return own + list(PROMPTS.values()) + [
        ROOT / "experiments/model_backend_deepseek/provider.json",
        ROOT / "experiments/model_backend_deepseek/cache_usage.py",
        ROOT / "experiments/research_state_v2/claim_mutation/CASES.json",
        ROOT / "experiments/research_progress_frontier/closure_probe/review_cases.json",
        ROOT / "experiments/variable_preserving_state/test_representation/CASES.json"]


def source_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}


def order():
    return sorted(BANK, key=lambda c: digest(c["case_id"]))


def arms(i):
    sequence = ("A", "B", "C")
    return sequence[i % 3:] + sequence[:i % 3]


def request(case, arm):
    user = {"raw_question": case["raw_question"],
            "latest_observation": {"ref": case["new_observation"]["ref"],
                                   "text": case["new_observation"]["text"]}}
    if arm in ("B", "C"):
        user["active_gap"] = case["active_gap"]
    if arm == "C":
        user["relevant_committed_claims"] = case["existing_claims"]
    assert "review" not in user
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPTS[arm].read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 41 and len({c["qid"] for c in BANK}) == 12
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "base_head": "85120d0f8e1dcbee74e68644ef92fedc5364602c",
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                      "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                      "max_retries": 0},
         "source_hashes": source_hashes(),
         "prompt_hashes": {a: sha(p) for a, p in PROMPTS.items()},
         "schema_hash": digest({"findings": [{"statement": "nonempty string",
                                            "evidence_refs": ["current W only"]}], "max_findings": 3}),
         "case_order": [c["case_id"] for c in order()],
         "arm_order": {c["case_id"]: list(arms(i)) for i,c in enumerate(order())},
         "qids": sorted({c["qid"] for c in BANK}),
         "checkpoints": {c["case_id"]: c["source_checkpoint"] for c in BANK},
         "question_hashes": {c["case_id"]: digest(c["raw_question"]) for c in BANK},
         "gap_hashes": {c["case_id"]: digest(c["active_gap"]) for c in BANK},
         "existing_claim_hashes": {c["case_id"]: digest(c["existing_claims"]) for c in BANK},
         "observation_hashes": {c["case_id"]: digest(c["new_observation"]) for c in BANK},
         "review_hash": sha(HERE / "BANK.json"),
         "request_hashes": {c["case_id"] + ":" + a: digest(request(c,a))
                            for c in BANK for a in ("A", "B", "C")},
         "rubric_hash": sha(HERE / "REVIEW_RUBRIC.md"),
         "gate": {"precision_min": .90, "recall_min": .85,
                  "unsupported_inference_max": .05, "nogain_silence_min": .90,
                  "duplicate_rate_max": .10,
                  "A_irrelevant_error_trigger": 5, "B_or_C_net_reduction_min": 4,
                  "B_duplicate_error_trigger": 4, "C_net_reduction_min": 3},
         "failure_policy": "One call per case/arm, zero retries and no best-of. Invalid/failed outputs retained, counted as misses; no semantic repair."}
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {"source_hashes": f["source_hashes"] == source_hashes(),
              "provider": f["provider"] == {
                  "host": urlsplit(CONFIG["base_url"]).hostname,
                  "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                  "max_retries": CONFIG["max_retries"]},
              "order": f["case_order"] == [c["case_id"] for c in order()],
              "bank": f["review_hash"] == sha(HERE / "BANK.json"),
              "requests": all(f["request_hashes"][c["case_id"] + ":" + a] == digest(request(c,a))
                              for c in BANK for a in ("A", "B", "C"))}
    (HERE / "gate.txt").write_text("\n".join(("PASS " if ok else "FAIL ") + key
                                                for key, ok in checks.items()) + "\n")
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
    for item in value["findings"]:
        if not isinstance(item, dict) or set(item) != {"statement", "evidence_refs"}:
            raise ValueError("finding_schema")
        if not isinstance(item["statement"], str) or not item["statement"].strip():
            raise ValueError("empty_statement")
        if item["evidence_refs"] != [case["new_observation"]["ref"]]:
            raise ValueError("ref_not_current_W")
    return value


def one_cell(client, case, arm):
    cell = case["case_id"] + ":" + arm
    req = request(case, arm)
    emit("model_request", cell=cell, request=req, request_hash=digest(req))
    started = time.monotonic()
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("model_response", cell=cell, response=raw,
             cache_usage=extract(raw), latency_seconds=time.monotonic() - started)
        if raw["choices"][0]["finish_reason"] != "stop":
            raise ValueError("abnormal_finish")
        value = validate(case, json.loads(raw["choices"][0]["message"]["content"]))
        emit("cell_outcome", cell=cell, output=value)
        return {"cell": cell, "output": value, "error": None}
    except Exception as exc:
        emit("cell_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
             latency_seconds=time.monotonic() - started)
        return {"cell": cell, "output": {"findings": []},
                "error": type(exc).__name__}


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
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(one_cell, client, c, a): (c, a) for c, a in tasks}
            for future in as_completed(futures):
                c, a = futures[future]
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
