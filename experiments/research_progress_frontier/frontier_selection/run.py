"""Frozen Stage B clean-Progress-View Frontier diagnostic."""

import hashlib
import json
import subprocess
import sys
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
CASES = json.loads((HERE / "review_cases.json").read_text())
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
SYSTEM = (
    "You are choosing the one research gap to work on next from a clean progress view. "
    "A question constraint is not automatically an open gap. Use the claim statuses: do not reselect a closed "
    "claim, and do not commit to a downstream answer detail that depends on an unverified candidate. "
    "Prefer a genuinely open question that can distinguish candidates, unlock a next step, or use a suitable observed source. "
    "Choose exactly one listed G# and answer in exactly four lines:\n"
    "Active gap: [one G#]\nWhy now: [one sentence]\n"
    "Expected source type: [one concise source type]\nKnown suitable source: [one listed D# or none]"
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def request(case):
    claims = "\n".join(f"{cid}: {status} — {claim}" for cid, status, claim in case["claims"])
    gaps = "\n".join(f"{gid}: {question}" for gid, question in case["gap_options"])
    directory = "\n".join(f"{d['doc_ref']} — {d['observed_title']}" for d in case["source_directory"])
    user = (f"Original question:\n{case['original_question']}\n\n"
            f"Current candidate hypotheses:\n{case['candidate_hypotheses']}\n\n"
            f"Claim status:\n{claims}\n\n"
            f"Candidate research questions:\n{gaps}\n\n"
            f"Available observed source directory:\n{directory}")
    return {"model": CONFIG["model"], "messages": [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}], "stream": False}


def validate():
    stage_a = json.loads((STUDY / "closure_probe/results.json").read_text())["summary"]
    if not stage_a["stage_A_pass"]:
        raise ValueError("Stage A did not pass")
    if len(CASES) != 8 or len({c["qid"] for c in CASES}) != 8:
        raise ValueError("Expected eight qids exactly once")
    for case in CASES:
        gaps = {g[0] for g in case["gap_options"]}
        if not case["original_question"] or len(gaps) != 4 or \
           set(case["acceptable_active_gaps"]) & set(case["unacceptable_closed_gaps"]) or \
           set(case["acceptable_active_gaps"]) & set(case["unsupported_hypothesis_gaps"]):
            raise ValueError(case["case_id"])
        content = request(case)["messages"][1]["content"]
        if any(term in content for term in ("acceptable_active_gaps", "review_reason", "preferred_source_types")):
            raise ValueError("Private reviewer field leaked")


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate()
    sources = ["experiments/research_progress_frontier/frontier_selection/case_specs.py",
               "experiments/research_progress_frontier/frontier_selection/build_cases.py",
               "experiments/research_progress_frontier/frontier_selection/review_cases.json",
               "experiments/research_progress_frontier/frontier_selection/source_aliases.json",
               "experiments/research_progress_frontier/frontier_selection/EXPERIMENT_PLAN.md",
               "experiments/research_progress_frontier/frontier_selection/RUBRIC.json",
               "experiments/research_progress_frontier/frontier_selection/run.py",
               "experiments/research_progress_frontier/frontier_selection/analyze.py",
               "experiments/model_backend_deepseek/provider.json"]
    history = ["experiments/research_progress_frontier/closure_probe/review_cases.json",
               "experiments/research_progress_frontier/closure_probe/results.json",
               "experiments/research_progress_frontier/closure_probe/freeze.json",
               "experiments/research_state_qualification/qualification_upper_bound/review_packets.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "prompt_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(), "tool_schema": None,
           "sample_count": len(CASES), "case_order": [c["case_id"] for c in order()],
           "qid_checkpoint": {c["case_id"]: c["qid"] for c in CASES},
           "review_labels": {c["case_id"]: {k: c[k] for k in
                             ("acceptable_active_gaps", "unacceptable_closed_gaps",
                              "unsupported_hypothesis_gaps", "preferred_source_types")} for c in CASES},
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "history_sha256": {p: sha(ROOT / p) for p in history},
           "request_sha256": {c["case_id"]: digest(request(c)) for c in CASES},
           "gate": json.loads((HERE / "RUBRIC.json").read_text())["gate"],
           "failure_policy": "One response per case, no tools, zero SDK retries, no selective reruns or repairs."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["history_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and
                          doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and
                          doc["timeout_seconds"] == CONFIG["timeout_seconds"] and doc["max_retries"] == 0,
              "prompt": doc["prompt_sha256"] == hashlib.sha256(SYSTEM.encode()).hexdigest(),
              "cases": doc["sample_count"] == len(CASES) == 8 and
                       doc["case_order"] == [c["case_id"] for c in order()] and
                       all(doc["review_labels"][c["case_id"]]["acceptable_active_gaps"] ==
                           c["acceptable_active_gaps"] for c in CASES),
              "requests": all(doc["request_sha256"][c["case_id"]] == digest(request(c)) for c in CASES),
              "rubric": doc["gate"] == json.loads((HERE / "RUBRIC.json").read_text())["gate"]}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields},
                             ensure_ascii=False) + "\n")
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
        for case in order():
            cid = case["case_id"]
            params = request(case)
            emit("api_request", case_id=cid, request=params, request_sha256=digest(params))
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
                emit("api_response", case_id=cid, response=raw, cache_usage=extract(raw))
                print(cid, "response", flush=True)
            except Exception as exc:
                emit("api_error", case_id=cid, error_type=type(exc).__name__,
                     http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
                print(cid, "error", type(exc).__name__, flush=True)


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
