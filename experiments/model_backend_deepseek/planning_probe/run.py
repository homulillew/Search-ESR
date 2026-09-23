"""DeepSeek arm of the frozen same-prefix M1 planning probe."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_atria.planning_probe.run import (
    CASES, DIAGNOSTIC, approved_annotations, request,
)
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ATRIA_STUDY = ROOT / "experiments/model_backend_atria"
CONFIG = json.loads((STUDY / "provider.json").read_text())
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
BASELINES = json.loads((STUDY / "BASELINE_FINGERPRINTS.json").read_text())["sha256"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def check_baselines():
    return {p: sha(ROOT / p) == h for p, h in BASELINES.items()}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    approved_annotations()
    if not all(check_baselines().values()):
        raise AssertionError("Historical baseline fingerprint mismatch")
    if not json.loads((STUDY / "forced_choice_summary.json").read_text())["pass"]:
        raise AssertionError("M0 compatibility supplement failed")
    sources = ["experiments/model_backend_deepseek/planning_probe/run.py",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_atria/planning_probe/run.py",
               "experiments/model_backend_atria/planning_probe/analyze.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "model": CONFIG["model"], "base_url": CONFIG["base_url"],
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "thinking_mode": "provider default", "tools": None,
           "samples_per_cell": 1, "cases": CASES,
           "diagnostic_sha256": hashlib.sha256(DIAGNOSTIC.encode()).hexdigest(),
           "rubric_sha256": sha(ATRIA_STUDY / "planning_probe/EVALUATION_RULES.json"),
           "qwen_events_sha256": sha(ATRIA_STUDY / "planning_probe/events.jsonl"),
           "m0_summary_sha256": sha(STUDY / "protocol_summary.json"),
           "m0b_summary_sha256": sha(STUDY / "forced_choice_summary.json"),
           "baselines_sha256": sha(STUDY / "BASELINE_FINGERPRINTS.json"),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "messages_sha256": {f"{q}:{s}": digest(request(q, s)) for q, s in CASES},
           "failure_policy": "All 13 DeepSeek cells once, no selective retry; preserve errors"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"baselines": all(check_baselines().values()) and
              sha(STUDY / "BASELINE_FINGERPRINTS.json") == doc["baselines_sha256"],
              "sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "rubric": sha(ATRIA_STUDY / "planning_probe/EVALUATION_RULES.json") == doc["rubric_sha256"],
              "qwen_events": sha(ATRIA_STUDY / "planning_probe/events.jsonl") == doc["qwen_events_sha256"],
              "m0": sha(STUDY / "protocol_summary.json") == doc["m0_summary_sha256"],
              "m0b": sha(STUDY / "forced_choice_summary.json") == doc["m0b_summary_sha256"],
              "messages": all(digest(request(q, s)) == doc["messages_sha256"][f"{q}:{s}"]
                              for q, s in CASES),
              "provider": doc["model"] == CONFIG["model"] and
                          doc["base_url"] == CONFIG["base_url"] and
                          doc["timeout_seconds"] == CONFIG["timeout_seconds"],
              "sample_count": len(CASES) == 13 and doc["samples_per_cell"] == 1}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                              "kind": kind, **fields}, ensure_ascii=False) + "\n")
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
        for q, s in CASES:
            cell = f"{q}:{s}:{CONFIG['model']}"
            messages = request(q, s)
            params = {"model": CONFIG["model"], "messages": messages, "stream": False}
            emit("api_request", cell=cell, request=params, messages_sha256=digest(messages))
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
                emit("api_response", cell=cell, response=raw, cache_usage=extract(raw))
                print(cell, "response", flush=True)
            except Exception as exc:
                emit("api_error", cell=cell, error_type=type(exc).__name__,
                     http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
                print(cell, "error", type(exc).__name__, flush=True)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze":
        freeze()
    elif action == "gate":
        print(gate())
    elif action == "run":
        run()
    else:
        raise SystemExit("freeze|gate|run")
