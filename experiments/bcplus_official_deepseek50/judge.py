"""Score the completed rerun with the official BC+ Qwen3-32B grader prompt."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import statistics
import time

import httpx
from openai import OpenAI

from experiments.bcplus_native_deepseek50.evaluate import wilson
from experiments.bcplus_native_deepseek50.runner import sha, write_json
from .official_retrieval import ROOT, UPSTREAM

HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/bcplus_native_deepseek50"
JUDGMENTS = HERE / "judgments"
OFFICIAL_GRADER = UPSTREAM / "scripts_evaluation/evaluate_run.py"


def grader_components():
    tree = ast.parse(OFFICIAL_GRADER.read_text(encoding="utf-8"), filename=str(OFFICIAL_GRADER))
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and
                      any(isinstance(t, ast.Name) and t.id == "GRADER_TEMPLATE" for t in n.targets))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and
                 n.name in {"create_judge_prompt", "parse_judge_response"}]
    namespace = {"re": re}
    exec(compile(ast.Module(body=[assignment, *functions], type_ignores=[]), str(OFFICIAL_GRADER), "exec"), namespace)
    return namespace["create_judge_prompt"], namespace["parse_judge_response"]


def credentials():
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value.strip().strip("\"'")
    return values["OPENAI_BASE_URL"], values["OPENAI_API_KEY"]


def batch_inputs():
    end = json.loads((HERE / "runs/BATCH_END.json").read_text(encoding="utf-8"))
    batch = HERE / "runs" / end["batch_id"]
    selection = json.loads((OLD / "SELECTION_FREEZE.json").read_text(encoding="utf-8"))
    if len(end["results"]) != 50 or len(selection["selected_qids"]) != 50:
        raise ValueError("All 50 frozen runs must finish before judging")
    if set(q for q, _ in end["results"]) != set(selection["selected_qids"]):
        raise ValueError("Batch qids differ from original selection")
    for qid in selection["selected_qids"]:
        path = batch / f"qid_{qid}"
        if not all((path / name).exists() for name in ("answer.md", "events.jsonl", "summary.json")):
            raise ValueError(f"Incomplete trajectory for {qid}")
    dataset = {str(record["query_id"]): record
               for line in (ROOT / "BCPlus/data/bcplus/qa.jsonl").open(encoding="utf-8")
               if (record := json.loads(line))}
    rows = []
    for qid in selection["selected_qids"]:
        path = batch / f"qid_{qid}"
        record = dataset[qid]
        rows.append({"qid": qid, "question": record["query"], "gold_answer": record["answer"],
                     "response": (path / "answer.md").read_text(encoding="utf-8").strip(),
                     "status": json.loads((path / "summary.json").read_text(encoding="utf-8"))["status"],
                     "answer_sha256": sha(path / "answer.md")})
    return end, rows


def prepare():
    if (HERE / "JUDGE_FREEZE.json").exists():
        raise ValueError("Judge freeze already exists")
    end, rows = batch_inputs()
    create_prompt, _ = grader_components()
    base_url, _ = credentials()
    freeze = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "batch_id": end["batch_id"],
        "batch_end_sha256": sha(HERE / "runs/BATCH_END.json"),
        "judge_source": str(OFFICIAL_GRADER.relative_to(ROOT)),
        "judge_source_sha256": sha(OFFICIAL_GRADER),
        "judge_script_sha256": sha(HERE / "judge.py"),
        "prompt_template_sha256": sha256(create_prompt("Q", "R", "A").encode()).hexdigest(),
        "model": "qwen3-32b",
        "official_model": "Qwen/Qwen3-32B",
        "provider_base_url": base_url,
        "transport": "OpenAI-compatible hosted API; official grader prompt and sampling settings, no local vLLM",
        "temperature": 0.7, "top_p": 0.8, "top_k": 20,
        "max_output_tokens": 4096, "enable_thinking": False,
        "max_retries": 0, "concurrency": 20, "timeout_seconds": 900,
        "http_max_connections": 20,
        "api_preflight": {"status": "passed", "example": "2+2 equivalence", "correct": True,
                          "prompt_tokens": 341, "completion_tokens": 76},
        "denominator": 50,
        "answer_sha256": {x["qid"]: x["answer_sha256"] for x in rows},
        "missing_or_unparseable_rule": "incorrect in the fixed denominator; no retry",
    }
    write_json(HERE / "JUDGE_FREEZE.json", freeze)


def judge_one(row, create_prompt, parse_response, client, freeze):
    qid = row["qid"]
    prompt = create_prompt(row["question"], row["response"], row["gold_answer"])
    record = {"qid": qid, "question": row["question"], "gold_answer": row["gold_answer"],
              "response": row["response"], "status": row["status"], "prompt": prompt,
              "requested_at_utc": datetime.now(timezone.utc).isoformat()}
    start = time.monotonic()
    if row["status"] == "RUN_FAILED" or not row["response"]:
        record["skip_reason"] = "incomplete or empty agent answer"
        record["parsed"] = {"correct": False, "parse_error": True}
    else:
        try:
            response = client.chat.completions.create(
                model=freeze["model"], messages=[{"role": "user", "content": prompt}],
                temperature=freeze["temperature"], top_p=freeze["top_p"],
                max_tokens=freeze["max_output_tokens"], stream=False,
                extra_body={"enable_thinking": False, "top_k": freeze["top_k"]},
            )
            record["raw_response"] = response.model_dump(mode="json")
            text = response.choices[0].message.content or "" if response.choices else ""
            record["judge_response"] = text
            record["parsed"] = parse_response(text)
        except Exception as exc:
            record["api_error"] = {"type": type(exc).__name__, "message": str(exc)}
            record["parsed"] = {"correct": False, "parse_error": True}
    record["elapsed_seconds"] = time.monotonic() - start
    record["correct_primary"] = record["parsed"].get("correct") is True and not record["parsed"].get("parse_error")
    write_json(JUDGMENTS / f"qid_{qid}.json", record)
    return qid, record["correct_primary"]


def run():
    freeze = json.loads((HERE / "JUDGE_FREEZE.json").read_text(encoding="utf-8"))
    end, rows = batch_inputs()
    if JUDGMENTS.exists() and any(JUDGMENTS.iterdir()):
        raise ValueError("Judgments already exist; a frozen batch cannot be rerun")
    if freeze["batch_id"] != end["batch_id"] or freeze["batch_end_sha256"] != sha(HERE / "runs/BATCH_END.json"):
        raise ValueError("Online batch changed after judge freeze")
    if freeze["judge_source_sha256"] != sha(OFFICIAL_GRADER) or freeze["judge_script_sha256"] != sha(HERE / "judge.py"):
        raise ValueError("Judge source changed after freeze")
    if {x["qid"]: x["answer_sha256"] for x in rows} != freeze["answer_sha256"]:
        raise ValueError("Answers changed after judge freeze")
    create_prompt, parse_response = grader_components()
    base_url, key = credentials()
    if base_url != freeze["provider_base_url"]:
        raise ValueError("Judge endpoint changed after freeze")
    JUDGMENTS.mkdir(parents=True)
    http = httpx.Client(limits=httpx.Limits(max_connections=20, max_keepalive_connections=20))
    client = OpenAI(api_key=key, base_url=base_url, timeout=900, max_retries=0, http_client=http)
    start = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=freeze["concurrency"]) as pool:
            futures = {pool.submit(judge_one, row, create_prompt, parse_response, client, freeze): row["qid"] for row in rows}
            for count, future in enumerate(as_completed(futures), 1):
                qid, correct = future.result()
                print(f"judged={count}/50 qid={qid} correct={correct}", flush=True)
    finally:
        client.close()
    records = [json.loads((JUDGMENTS / f"qid_{row['qid']}.json").read_text(encoding="utf-8")) for row in rows]
    correct = sum(x["correct_primary"] for x in records)
    errors = [x["qid"] for x in records if x["parsed"].get("parse_error")]
    old = {x["qid"]: x for x in json.loads((OLD / "PER_QUESTION.json").read_text(encoding="utf-8"))}
    changes = [{"qid": x["qid"], "new_run_qwen_correct": x["correct_primary"],
                      "old_run_investigator_correct": old[x["qid"]]["correct_primary"],
                      "gold_answer": x["gold_answer"],
                      "extracted_final_answer": x["parsed"].get("extracted_final_answer"),
                      "reasoning": x["parsed"].get("reasoning")}
                     for x in records if x["correct_primary"] != old[x["qid"]]["correct_primary"]]
    usage = [x["raw_response"].get("usage") or {} for x in records if "raw_response" in x]
    summary = {
        "score_kind": "Qwen3-32B primary judge using official BrowseComp-Plus prompt and parser, hosted OpenAI-compatible runtime",
        "correct": correct, "denominator": 50, "accuracy": correct/50,
        "wilson_95": wilson(correct, 50), "parse_or_api_error_qids": errors,
        "outcome_changes_vs_prior_run_and_judge": changes,
        "judge_prompt_tokens": sum(u.get("prompt_tokens", 0) for u in usage),
        "judge_completion_tokens": sum(u.get("completion_tokens", 0) for u in usage),
        "judge_wall_seconds": time.monotonic()-start,
        "judge_latency_median_seconds": statistics.median(x["elapsed_seconds"] for x in records),
        "batch_id": end["batch_id"],
    }
    write_json(HERE / "QWEN_RESULTS.json", summary)
    print(json.dumps({k: summary[k] for k in ("correct", "denominator", "accuracy", "parse_or_api_error_qids")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run"])
    args = parser.parse_args()
    prepare() if args.command == "prepare" else run()
