"""Complete the frozen Qwen baseline and DeepSeek M4 evidence probe."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.client import Config
from experiments.model_backend_atria.evidence_update.run import INSTRUCTION, cases, request
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OLD = ROOT / "experiments/model_backend_atria"
CONFIG = json.loads((STUDY / "provider.json").read_text())
BASELINES = json.loads((STUDY / "BASELINE_FINGERPRINTS.json").read_text())["sha256"]
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def prior_qwen_cells():
    events = [json.loads(line) for line in (OLD / "evidence_update/events.jsonl").open()]
    return [e["cell"] for e in events if e["kind"] in ("api_response", "api_error")
            and e["cell"].endswith(":qwen3.7-flash")]


def cells():
    return [(c, arm, model) for c in cases() for arm in ("E0", "E1")
            for model in ("qwen3.7-flash", CONFIG["model"])]


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    if not all(sha(ROOT / p) == h for p, h in BASELINES.items()):
        raise AssertionError("Baseline changed")
    qwen = Config.load()
    if qwen.model != "qwen3.7-flash":
        raise ValueError("Qwen model changed")
    prior = prior_qwen_cells()
    if len(prior) != 2:
        raise ValueError("Expected exactly two completed Qwen baseline cells")
    sources = ["experiments/model_backend_deepseek/evidence_update/run.py",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/cache_usage.py",
               "experiments/model_backend_atria/evidence_update/run.py",
               "experiments/model_backend_atria/evidence_update/analyze.py",
               "experiments/search_find_v3b/orthogonal_search/run_partial.py",
               "llm_chat/client.py"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "model_order": [qwen.model, CONFIG["model"]], "arm_order": ["E0", "E1"],
           "prior_qwen_cells": prior, "samples_per_cell": 1,
           "tools": None, "stream": False, "sampling_overrides": {}, "max_retries": 0,
           "qwen_host": urlsplit(qwen.base_url).hostname, "qwen_timeout_seconds": qwen.timeout,
           "deepseek_host": urlsplit(CONFIG["base_url"]).hostname,
           "deepseek_timeout_seconds": CONFIG["timeout_seconds"],
           "thinking_mode": "provider default",
           "instruction_sha256": hashlib.sha256(INSTRUCTION.encode()).hexdigest(),
           "case_file_sha256": sha(OLD / "evidence_update/cases.json"),
           "rubric_sha256": sha(OLD / "evidence_update/EVALUATION_RULES.json"),
           "old_events_sha256": sha(OLD / "evidence_update/events.jsonl"),
           "m2_summary_sha256": sha(STUDY / "natural_action_probe/mechanical_summary.json"),
           "baseline_fingerprints_sha256": sha(STUDY / "BASELINE_FINGERPRINTS.json"),
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "messages_sha256": {f"{c['case_id']}:{arm}": digest(request(c, arm))
                               for c in cases() for arm in ("E0", "E1")},
           "failure_policy": "Reuse two completed Qwen cells; once each for 14 remaining Qwen and 16 DeepSeek; preserve failures"}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    qwen = Config.load()
    checks = {"baseline": all(sha(ROOT / p) == h for p, h in BASELINES.items()) and
              sha(STUDY / "BASELINE_FINGERPRINTS.json") == doc["baseline_fingerprints_sha256"],
              "sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "case": sha(OLD / "evidence_update/cases.json") == doc["case_file_sha256"],
              "rubric": sha(OLD / "evidence_update/EVALUATION_RULES.json") == doc["rubric_sha256"],
              "instruction": hashlib.sha256(INSTRUCTION.encode()).hexdigest() == doc["instruction_sha256"],
              "old_events": sha(OLD / "evidence_update/events.jsonl") == doc["old_events_sha256"]
                            and prior_qwen_cells() == doc["prior_qwen_cells"],
              "m2": sha(STUDY / "natural_action_probe/mechanical_summary.json") == doc["m2_summary_sha256"],
              "messages": all(digest(request(c, arm)) == doc["messages_sha256"][f"{c['case_id']}:{arm}"]
                              for c in cases() for arm in ("E0", "E1")),
              "providers": qwen.model == "qwen3.7-flash" and
                urlsplit(qwen.base_url).hostname == doc["qwen_host"] and
                qwen.timeout == doc["qwen_timeout_seconds"] and
                urlsplit(CONFIG["base_url"]).hostname == doc["deepseek_host"] and
                CONFIG["timeout_seconds"] == doc["deepseek_timeout_seconds"]}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    qwen = Config.load()
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    skip = set(prior_qwen_cells())
    with OpenAI(api_key=qwen.api_key, base_url=qwen.base_url,
                timeout=qwen.timeout, max_retries=0) as qc, \
         OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as dc:
        for c, arm, model in cells():
            cell = f"{c['case_id']}:{arm}:{model}"
            if cell in skip:
                emit("reused_prior_qwen_cell", cell=cell, source="model_backend_atria/evidence_update/events.jsonl")
                continue
            messages = request(c, arm)
            params = {"model": model, "messages": messages, "stream": False}
            emit("api_request", cell=cell, request=params, messages_sha256=digest(messages))
            try:
                raw = (qc if model == qwen.model else dc).chat.completions.create(**params).model_dump(mode="json")
                emit("api_response", cell=cell, response=raw,
                     cache_usage=extract(raw) if model == CONFIG["model"] else None)
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
        gate()
        print("PASS")
    elif action == "run":
        run()
    else:
        raise SystemExit("freeze|gate|run")
