"""Run the locked current-vs-exploratory prompt probe with parallel API/retrieval."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from openai import OpenAI
from transformers import AutoTokenizer
from llm_chat.client import Config
from llm_chat.observations import ObservationStore
from llm_chat.observed_agent import ObservedTools
from llm_chat.raw_windows import RawWindowBuilder
from experiments.run_rollout import Recorder, RecordedClient
from experiments.query_initialization.basis_packet.packet import query_token_count, build_packet, verbatim
from experiments.query_initialization.selector_verbatim.parallel_search import ParallelSearch
from experiments.query_initialization.exploratory_policy.policy import GUIDANCE, PROBE, system_prompt, schemas, request, action

BASE = Path(__file__).parent
PRIOR = ROOT / "experiments/query_initialization/selector_verbatim/runs/20260918T085353.300461Z"


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retrieval-workers", type=int, default=2)
    args = parser.parse_args()
    assert 1 <= args.workers <= 8 and 1 <= args.retrieval_workers <= 2
    config = Config.load()
    assert config.model == "qwen3.7-flash" and config.enable_thinking is False
    protocol = BASE / "PROTOCOL.md"
    assert protocol.exists(), "Freeze protocol before running"
    cases = [dict(qid=c["qid"], question=c["question"]["text"]) for c in json.loads((PRIOR / "tasks.json").read_text())]
    assert len(cases) == 20 and len({c["qid"] for c in cases}) == 20
    dataset = ROOT / "BCPlus/data/bcplus/qa.jsonl"
    locked = json.loads((PRIOR / "selection_lock.json").read_text())
    assert sha(dataset) == locked["dataset_sha256"]
    for case in cases:
        assert hashlib.sha256(case["question"].encode()).hexdigest() == locked["question_sha256"][case["qid"]]
    tokenizer = AutoTokenizer.from_pretrained("/data/model/Qwen3-Embedding-8B", local_files_only=True)
    metadata = json.loads((ROOT / "BCPlus/indexes/bcplus-qwen3-8b/metadata.json").read_text())
    prefix = metadata["query_prefix"]
    out = BASE / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out.mkdir(parents=True)
    dump(out / "tasks.json", cases)
    jobs = [(c, a, r) for c in cases for a in ("current", "exploratory") for r in (1, 2)]
    random.Random(20260925).shuffle(jobs)
    dump(out / "schedule.json", [dict(qid=c["qid"], arm=a, repeat=r) for c, a, r in jobs])
    # Freeze online behavior and its protocol; independent offline analysis is
    # archived separately when complete and cannot affect these requests.
    names = [str(p.relative_to(ROOT)) for p in BASE.iterdir()
             if p.name in ("run.py", "policy.py", "test_policy.py", "PROTOCOL.md", "README.md")]
    names += ["experiments/query_initialization/selector_verbatim/parallel_search.py",
              "experiments/query_initialization/basis_packet/packet.py",
              "experiments/query_initialization/single_entry/source_units.py",
              "experiments/run_rollout.py", "llm_chat/client.py", "llm_chat/agent.py",
              "llm_chat/observed_agent.py", "llm_chat/observations.py", "llm_chat/raw_windows.py",
              "llm_chat/window_locator.py", "llm_chat/window_units.py", "BCPlus/scripts/search_bcplus.py",
              "BCPlus/indexes/bcplus-qwen3-8b/metadata.json"]
    hashes = {}
    for name in names:
        destination = out / "source" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        hashes[name] = sha(ROOT / name)
    manifest = dict(version="exploratory_policy_v001", source_sha256=hashes,
        dataset_sha256=sha(dataset), tasks_sha256=sha(out / "tasks.json"),
        prior_run=str(PRIOR.relative_to(ROOT)), prior_tasks_sha256=sha(PRIOR / "tasks.json"),
        phase="known_question_development_ablation", arms=["current", "exploratory"], model_repeats=2,
        model=config.model, base_url=config.base_url, request_options=config.request_options(),
        system_prompts={a:system_prompt(config,a) for a in ("current", "exploratory")},
        guidance=GUIDANCE, shared_probe=PROBE, tools=schemas(), max_tokens=1536, timeout=120,
        sdk_retries=0, repair_limit=0, max_actions=2, query_max_tokens=1024, query_prefix=prefix,
        workers=args.workers, retrieval_workers=args.retrieval_workers, schedule_seed=20260925,
        k=6, window="baseline", window_tokens=400, total_window_budget=2400,
        session_observation_budget=4800, open_budget=1200, max_around_budget=2400,
        first_tool_choice="forced_search", second_tool_choice="auto", parallel_tool_calls=False,
        note="Prompt-only paired ablation. No Selector/Compiler or state schema. No final forced-answer request. Two model decisions only; evaluate second tool observations offline. Same known questions, not held-out generalization. Agent-assisted qualitative review is not human gold.")
    dump(out / "manifest.json", manifest)
    print("OUTPUT_DIR=" + str(out), flush=True)
    retrieval = ParallelSearch(args.retrieval_workers)
    old = json.loads((ROOT / "experiments/query_initialization/basis_packet/cases.json").read_text())
    try:
        preflight = retrieval.preflight([verbatim(build_packet(c["question"], c["basis_refs"])) for c in old[:3]])
        dump(out / "retrieval_preflight.json", preflight)
        print("RETRIEVAL_PREFLIGHT passed", flush=True)
    except BaseException:
        retrieval.close()
        raise

    def run(case, arm, repeat):
        sid = f"qid_{case['qid']}__{arm}__r{repeat}"
        folder = out / sid
        folder.mkdir()
        rec = Recorder(folder)
        store = ObservationStore(folder / "observations.sqlite")
        tools = ObservedTools(store)
        tools.window_builder = RawWindowBuilder(tokenizer)

        class Proxy:
            def search(self, query, k):
                response = retrieval.search(query, k)
                rec.emit("retrieval_worker", **{k:v for k,v in response.items() if k != "hits"})
                return response["hits"]

        tools.searcher = Proxy()
        client = RecordedClient(OpenAI(api_key=config.api_key, base_url=config.base_url, timeout=120, max_retries=0), rec)
        messages = [dict(role="system", content=system_prompt(config, arm)), dict(role="user", content=case["question"])]
        data = dict(session=sid, qid=case["qid"], arm=arm, repeat=repeat, status="pending", steps=[])
        dump(folder / "input.json", case)
        start = time.monotonic()
        stage = "api"
        try:
            for step_number in (1, 2):
                entry = dict(step=step_number, status="pending")
                data["steps"].append(entry)
                rec.emit("step_start", step=step_number)
                stage = "api"
                response = client.chat.completions.create(**request(config, messages, step_number))
                if not response.choices:
                    raise ValueError("API returned no choices")
                choice = response.choices[0]
                message = choice.message.model_dump(exclude_none=True)
                entry.update(assistant_message=message, finish_reason=choice.finish_reason)
                stage = "protocol"
                selected = action(message, choice.finish_reason, step_number)
                entry["action"] = selected
                messages.append(message)
                if selected is None:
                    entry["status"] = "answered" if message.get("content") else "refused"
                    data["status"] = entry["status"]
                    rec.emit("model_stopped", step=step_number, status=data["status"])
                    break
                if selected["name"] == "search":
                    count = query_token_count(selected["arguments"]["query"], tokenizer, prefix)
                    entry["query_tokens"] = count
                    if count > 1024:
                        raise ValueError("Query exceeds 1024 embedding tokens; no truncation or fallback")
                stage = "tool"
                rec.emit("tool_start", step=step_number, name=selected["name"], arguments=selected["arguments"])
                tool_start = time.monotonic()
                result = tools.execute(selected["name"], selected["arguments"])
                elapsed = time.monotonic() - tool_start
                views = result if isinstance(result, list) else [result]
                observed_tokens = sum(v["text_tokens"] + v["title_tokens"] for v in views)
                if observed_tokens > 2400:
                    raise ValueError("Observation exceeds per-action budget")
                entry.update(result=result, status="complete", elapsed_seconds=elapsed, observation_tokens=observed_tokens)
                rec.emit("tool_result", step=step_number, name=selected["name"], result=result, elapsed_seconds=elapsed)
                messages.append(dict(role="tool", tool_call_id=selected["tool_call_id"], content=json.dumps(result, ensure_ascii=False)))
            else:
                data["status"] = "complete"
        except Exception as exc:
            data.update(status=stage + "_error", error_type=type(exc).__name__, error_detail=str(exc).replace(config.api_key,"[redacted]"))
            if data["steps"]:
                data["steps"][-1]["status"] = data["status"]
            rec.emit("run_error", stage=stage, error_type=type(exc).__name__, detail=data["error_detail"])
        finally:
            dump(folder / "result.json", data)
            dump(folder / "messages.json", messages)
            dump(folder / "observations.json", store.events())
            dump(folder / "handoff.json", dict(schema_version="two_action_probe_v1", original_question=case,
                status=data["status"], messages_file="messages.json", observation_ledger="observations.sqlite",
                observed_window_refs=sorted(store.seen)))
            summary = {k:data[k] for k in ("session", "qid", "arm", "repeat", "status")}
            summary.update(elapsed_seconds=time.monotonic()-start,
                api_requests=sum(e["kind"] == "api_request" for e in rec.events),
                search_calls=sum(e["kind"] == "tool_start" and e["name"] == "search" for e in rec.events),
                open_calls=sum(e["kind"] == "tool_start" and e["name"] == "open" for e in rec.events))
            summary["usage"] = {k:sum((e["response"].get("usage") or {}).get(k,0) or 0 for e in rec.events if e["kind"] == "api_response") for k in ("prompt_tokens", "completion_tokens", "total_tokens")}
            dump(folder / "summary.json", summary)
            rec.render()
            tools.close()
            store.close()
            client.close()
        return summary

    results = []
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(run, *job) for job in jobs]):
                summary = future.result()
                results.append(summary)
                dump(out / "results.json", results)
                print("DONE", summary["session"], summary["status"], flush=True)
    finally:
        retrieval.close()
    print("FINISHED", out, flush=True)


if __name__ == "__main__":
    main()
