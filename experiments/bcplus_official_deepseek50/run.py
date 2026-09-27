"""Fifty-question DeepSeek run with the vendored BC+ default search interface."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
import time

import httpx
from openai import OpenAI

from experiments.bcplus_native_deepseek50.native_client import Config
from experiments.bcplus_native_deepseek50.runner import Recorder, RecordedClient, summarize, sha, write_json
from .official_retrieval import ROOT, UPSTREAM, chat_tool_definition, make_searcher

HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/bcplus_native_deepseek50"
RUNS = HERE / "runs"
MAX_ROUNDS = 200


class SerializedOfficialSearch:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="official-bcplus-search")
        self.future = self.executor.submit(make_searcher)
        self.tool_definitions = chat_tool_definition(self.future.result()[1])

    def execute(self, name, args):
        if name != "search" or set(args) != {"query"} or not isinstance(args["query"], str):
            raise ValueError("Official search expects exactly a string query")
        handler = self.future.result()[1]
        return self.executor.submit(handler.execute_tool, name, args).result()

    def close(self):
        self.executor.shutdown()


def run_one(item, batch_id, config, retrieval, freeze, prompt_function):
    qid = item["qid"]
    directory = RUNS / batch_id / f"qid_{qid}"
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / "input.json", item)
    write_json(directory / "manifest.json", {
        "batch_id": batch_id, "qid": qid, "model": config.model,
        "retrieval": "vendored BC+ FAISS and SearchToolHandler, search only, k=5, snippet=512 tokens",
        "prompt_template": "QUERY_TEMPLATE_NO_GET_DOCUMENT",
        "freeze_sha256": sha(HERE / "FREEZE.json"), "gold_supplied": False,
    })
    recorder = Recorder(directory)
    http = httpx.Client(limits=httpx.Limits(max_connections=2, max_keepalive_connections=1))
    client = RecordedClient(OpenAI(api_key=config.api_key, base_url=freeze["transport_base_url"],
                                   timeout=config.timeout, max_retries=0, http_client=http), recorder)
    messages = [{"role": "user", "content": prompt_function(item["question"], "QUERY_TEMPLATE_NO_GET_DOCUMENT")}]
    answer, status = "", "RUN_FAILED"
    start = time.monotonic()
    try:
        for round_index in range(MAX_ROUNDS + 1):
            last = round_index == MAX_ROUNDS
            response = client.create(model=config.model, messages=messages,
                                     tools=retrieval.tool_definitions,
                                     tool_choice="none" if last else "auto",
                                     stream=False, **config.request_options())
            if len(response.choices) != 1:
                raise ValueError("Expected exactly one choice")
            choice = response.choices[0]
            message = choice.message
            if message.tool_calls:
                if last or len(message.tool_calls) > 8 or choice.finish_reason not in {"tool_calls", "stop"}:
                    raise ValueError("Invalid or excessive tool-call batch")
                ids = set()
                for call in message.tool_calls:
                    if not call.id or call.id in ids or call.type != "function" or call.function.name != "search":
                        raise ValueError("Invalid search tool-call structure")
                    ids.add(call.id)
                messages.append(message.model_dump(exclude_none=True))
                for call in message.tool_calls:
                    try:
                        arguments = json.loads(call.function.arguments)
                        recorder.emit("tool_start", name="search", arguments=arguments)
                        tool_start = time.monotonic()
                        wire_output = retrieval.execute("search", arguments)
                        parsed = json.loads(wire_output)
                        recorder.emit("tool_result", name="search", result=parsed,
                                      wire_output=wire_output, elapsed_seconds=time.monotonic()-tool_start)
                    except Exception as exc:
                        wire_output = f"Error executing search: {exc}"
                        recorder.emit("tool_error", name="search", error_type=type(exc).__name__,
                                      message=str(exc))
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": wire_output})
                continue
            if choice.finish_reason != "stop" or not message.content:
                raise ValueError(f"Incomplete final response: {choice.finish_reason}")
            answer = message.content
            status = "emergency_cap_forced_answer" if last else "natural_answer"
            break
    except Exception as exc:
        recorder.emit("run_error", error_type=type(exc).__name__, message=str(exc))
    finally:
        (directory / "answer.md").write_text(answer + ("\n" if answer else ""), encoding="utf-8")
        recorder.emit("run_end", status=status, elapsed_seconds=time.monotonic()-start)
        write_json(directory / "summary.json", summarize(recorder.events, status, time.monotonic()-start))
        recorder.render()
        client.close()
    return qid, status


def main():
    os.environ.setdefault("HF_ENDPOINT", "https://huggingface.co")
    os.environ.setdefault("HF_HOME", "/data/WSH/bcplus-hf-cache")
    freeze = json.loads((HERE / "FREEZE.json").read_text(encoding="utf-8"))
    inputs = json.loads((OLD / "ONLINE_INPUTS.json").read_text(encoding="utf-8"))
    if len(inputs) != 50 or [x["qid"] for x in inputs] != freeze["selected_qids"]:
        raise ValueError("Selection differs from freeze")
    for relative, expected in freeze["source_sha256"].items():
        if sha(ROOT / relative) != expected:
            raise ValueError(f"Source changed after freeze: {relative}")
    if RUNS.exists() and any(RUNS.iterdir()):
        raise ValueError("Frozen official batch already exists")
    config = Config.load()
    if config.model != "deepseek-flash" or config.base_url != freeze["model_base_url"] or config.request_options() != freeze["request_options"]:
        raise ValueError("DeepSeek config changed after freeze")
    prompt_function = runpy.run_path(str(UPSTREAM / "search_agent/prompts.py"))["format_query"]
    retrieval = SerializedOfficialSearch()
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    RUNS.mkdir(parents=True, exist_ok=True)
    write_json(RUNS / "BATCH_MANIFEST.json", {
        "batch_id": batch_id, "freeze_sha256": sha(HERE / "FREEZE.json"),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    results = []
    start = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=50, thread_name_prefix="official-bcplus-qid") as pool:
            futures = {pool.submit(run_one, item, batch_id, config, retrieval, freeze, prompt_function): item["qid"] for item in inputs}
            for future in as_completed(futures):
                qid = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = (qid, "RUN_FAILED")
                    print(f"qid={qid} worker_error={type(exc).__name__}:{exc}", flush=True)
                results.append(result)
                print(f"completed={len(results)}/50 qid={qid} status={result[1]}", flush=True)
    finally:
        retrieval.close()
        write_json(RUNS / "BATCH_END.json", {
            "batch_id": batch_id, "results": results,
            "elapsed_seconds": time.monotonic()-start,
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        })


if __name__ == "__main__":
    main()
