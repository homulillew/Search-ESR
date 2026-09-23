"""Frozen Stage A DeepSeek Evidence -> Closure diagnostic."""

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
    "You are reviewing whether one current research claim can be closed from only the visible evidence below. "
    "Use supported only if all parts of the claim follow from the excerpts. Use refuted only if an excerpt "
    "explicitly contradicts a material part. Otherwise use open; missing detail or one matching clue does not "
    "close a conjunction. Do not use outside knowledge, future material or a likely final answer. "
    "Reply in exactly four lines, replacing each bracketed description with your answer:\n"
    "Status: [one of supported, refuted, open]\n"
    "Evidence refs: [listed refs separated by commas, or none]\n"
    "Missing evidence: [brief text, or none]\n"
    "Reason: [one or two sentences]"
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def request(case):
    lines = [f"Original question constraint: {case['question_constraint']}",
             f"Current candidate: {case['candidate']}", f"Current claim: {case['claim']}",
             "Exact currently visible evidence:"]
    for item in case["visible_evidence"]:
        lines.append(f"[{item['ref']}] Document {item['doc_ref']}; observed title: {item['title']}\n{item['excerpt']}")
    return {"model": CONFIG["model"], "messages": [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n\n".join(lines)}], "stream": False}


def validate():
    assert len(CASES) == 29 and len({c["case_id"] for c in CASES}) == 29
    assert len({c["qid"] for c in CASES}) == 8
    assert sum(c["case_type"] == "stale_gap" for c in CASES) == 5
    assert all(c["review_label"] in ("supported", "refuted", "open") and
               c["visible_evidence"] and c["review_reason"] for c in CASES)
    for c in CASES:
        expected = hashlib.sha256(json.dumps(c["visible_evidence"], ensure_ascii=False,
                                            sort_keys=True).encode()).hexdigest()
        assert expected == c["visible_evidence_sha256"]
        r = request(c)
        assert all(term not in r["messages"][1]["content"] for term in
                   ("review_label", "stale_action_private", "review_reason"))


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate()
    sources = ["experiments/research_progress_frontier/closure_probe/case_specs.py",
               "experiments/research_progress_frontier/closure_probe/build_cases.py",
               "experiments/research_progress_frontier/closure_probe/review_cases.json",
               "experiments/research_progress_frontier/closure_probe/provenance.json",
               "experiments/research_progress_frontier/closure_probe/REVIEW_PROTOCOL.md",
               "experiments/research_progress_frontier/closure_probe/RUBRIC.json",
               "experiments/research_progress_frontier/closure_probe/run.py",
               "experiments/research_progress_frontier/closure_probe/analyze.py",
               "experiments/model_backend_deepseek/provider.json"]
    from case_specs import SOURCES
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "prompt_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(), "tools": None,
           "sample_count": len(CASES), "case_order": [c["case_id"] for c in order()],
           "case_qid_checkpoint": {c["case_id"]: [c["qid"], c["checkpoint"]] for c in CASES},
           "evidence_excerpt_sha256": {c["case_id"]: c["visible_evidence_sha256"] for c in CASES},
           "review_labels": {c["case_id"]: c["review_label"] for c in CASES},
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "history_sha256": {p: sha(ROOT / p) for p in SOURCES.values()},
           "request_sha256": {c["case_id"]: digest(request(c)) for c in CASES},
           "gate": json.loads((HERE / "RUBRIC.json").read_text())["stage_A_gate"],
           "failure_policy": "One response per case, no tools, zero SDK retries, no selective reruns or repairs; retain every error."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    from case_specs import SOURCES
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["history_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and
                          doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and
                          doc["timeout_seconds"] == CONFIG["timeout_seconds"] and doc["max_retries"] == 0,
              "prompt": doc["prompt_sha256"] == hashlib.sha256(SYSTEM.encode()).hexdigest(),
              "cases": doc["sample_count"] == len(CASES) == 29 and
                       doc["case_order"] == [c["case_id"] for c in order()] and
                       all(doc["review_labels"][c["case_id"]] == c["review_label"] and
                           doc["evidence_excerpt_sha256"][c["case_id"]] == c["visible_evidence_sha256"]
                           for c in CASES),
              "requests": all(doc["request_sha256"][c["case_id"]] == digest(request(c)) for c in CASES),
              "rubric": doc["gate"] == json.loads((HERE / "RUBRIC.json").read_text())["stage_A_gate"]}
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
