"""Paired one-action F1 Frontier intervention with real Orthogonal tools."""

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from BCPlus.scripts.search_bcplus import BCPlusSearcher
from llm_chat.raw_windows import Window
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
BANK = json.loads((HERE / "BANK.json").read_text())
ACTOR_PROMPT = (STUDY / "prompts/actor.md").read_text()
SELECTOR_PROMPT = (STUDY / "prompts/frontier_selector.md").read_text()
SQLITE = ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite"
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sources():
    return [HERE / x for x in ("PROTOCOL.md", "REVIEW_RUBRIC.md", "build_bank.py", "BANK.json", "run.py")] + \
        [STUDY / f"prompts/{x}.md" for x in ("actor", "frontier_selector")] + \
        [ROOT / x for x in (
            "experiments/evidence_fidelity_loop/evidence_packet/BANK.json",
            "experiments/minimal_research_loop/verify_necessity/CANDIDATES.json",
            "experiments/minimal_research_loop/verify_necessity/ANNOTATIONS.json",
            "llm_chat/search_find_agent.py", "llm_chat/search_find_v3b_agent.py",
            "llm_chat/raw_windows.py", "llm_chat/window_locator.py",
            "BCPlus/scripts/search_bcplus.py", "experiments/model_backend_deepseek/provider.json",
            "experiments/model_backend_deepseek/protocol.py",
            "experiments/model_backend_deepseek/cache_usage.py",
            "BCPlus/indexes/bcplus-qwen3-8b/metadata.json")]


def arm_order(i):
    return ("A0", "A1") if i % 2 == 0 else ("A1", "A0")


def selector_request(case):
    view = {"Question": case["raw_question"], "Committed Claims": case["committed_claims"],
            "Open Gaps": case["open_gaps"], "Workspace": case["workspace"],
            "Working Hypothesis": case["working_hypothesis"]}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SELECTOR_PROMPT},
        {"role": "user", "content": json.dumps(view, ensure_ascii=False)}], "stream": False}


def actor_request(case, arm, chosen=None):
    gaps = case["open_gaps"] if arm == "A0" else [g for g in case["open_gaps"] if g["gap_id"] == chosen]
    assert len(gaps) == len(case["open_gaps"]) if arm == "A0" else len(gaps) == 1
    view = {"Question": case["raw_question"], "Committed Claims": case["committed_claims"],
            "Open Gaps" if arm == "A0" else "Selected Gap": gaps,
            "Workspace": case["workspace"], "Working Hypothesis": case["working_hypothesis"]}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SEARCH_FIND_PROMPT + "\n\n" + ACTOR_PROMPT},
        {"role": "user", "content": json.dumps(view, ensure_ascii=False)}],
        "tools": SEARCH_FIND_TOOLS, "tool_choice": "auto", "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 24 and len({c["qid"] for c in BANK}) == 10
    assert CONFIG["model"] == "deepseek-flash" and CONFIG["max_retries"] == 0
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "provider": {"host": urlsplit(CONFIG["base_url"]).hostname,
                        "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                        "max_retries": 0},
           "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in sources()},
           "corpus_sqlite_sha256": sha(SQLITE),
           "tool_schema_sha256": digest(SEARCH_FIND_TOOLS), "retriever": "BCPlusSearcher",
           "index": str(SQLITE.relative_to(ROOT)), "search_default_k": 5,
           "prompt_hashes": {"actor": digest(ACTOR_PROMPT), "selector": digest(SELECTOR_PROMPT),
                             "tool_system": digest(SEARCH_FIND_PROMPT)},
           "case_order": [c["case_id"] for c in BANK],
           "arm_order": {c["case_id"]: arm_order(i) for i, c in enumerate(BANK)},
           "selector_request_hashes": {c["case_id"]: digest(selector_request(c)) for c in BANK},
           "A0_actor_request_hashes": {c["case_id"]: digest(actor_request(c, "A0")) for c in BANK},
           "prefix_hashes": {c["case_id"]: {k: digest(c[k]) for k in
              ("raw_question", "committed_claims", "open_gaps", "workspace", "working_hypothesis", "review")}
              for c in BANK},
           "source_window_hashes": {c["case_id"]: c["provenance"]["source_window_sha256"] for c in BANK},
           "sample_count": 48, "horizon_actor_decisions": 1,
           "gate": {"A0_failure_min": 5, "net_useful_improvement_min": 4,
                    "reverse_worsening_max": 1, "useful_rate_no_decline": True, "no_gain_no_increase": True},
           "failure_policy": "One selector call in A1 and one Actor call per arm; exactly one tool execution; max_retries=0; preserve all failures without replacement."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": doc["source_hashes"] == {str(p.relative_to(ROOT)): sha(p) for p in sources()},
              "corpus": doc["corpus_sqlite_sha256"] == sha(SQLITE),
              "provider": doc["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname,
                  "model": CONFIG["model"], "timeout_seconds": CONFIG["timeout_seconds"],
                  "max_retries": CONFIG["max_retries"]},
              "schema": doc["tool_schema_sha256"] == digest(SEARCH_FIND_TOOLS),
              "case_order": doc["case_order"] == [c["case_id"] for c in BANK],
              "selector_requests": all(doc["selector_request_hashes"][c["case_id"]] == digest(selector_request(c)) for c in BANK),
              "A0_requests": all(doc["A0_actor_request_hashes"][c["case_id"]] == digest(actor_request(c, "A0")) for c in BANK)}
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **data):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                              **data}, ensure_ascii=False) + "\n")
        out.flush()


def call(client, req, cell, stage):
    emit(stage + "_request", cell=cell, request=req, request_hash=digest(req))
    began = time.monotonic()
    raw = client.chat.completions.create(**req).model_dump(mode="json")
    emit(stage + "_response", cell=cell, response=raw, cache_usage=extract(raw),
         latency_seconds=time.monotonic() - began)
    return raw["choices"][0]


def restore(tools, case):
    provenance = case["provenance"]
    with sqlite3.connect(f"{SQLITE.as_uri()}?mode=ro", uri=True) as db:
        full, url = db.execute("select text,url from documents where docid=?",
                               (provenance["corpus_docid"],)).fetchone()
    obs = case["workspace"]["observed_windows"][0]
    assert hashlib.sha256(full.encode()).hexdigest() == provenance["corpus_text_sha256"]
    assert full[provenance["source_offset"]:provenance["source_offset"] + len(obs["text"])] == obs["text"]
    key = tools._windows().register(provenance["corpus_docid"], full, url)
    assert tools.handles.document(key) == ("D1", True)
    tools._windows().windows["W1"] = Window(provenance["corpus_docid"], key[1],
      provenance["source_offset"], provenance["source_offset"] + len(obs["text"]))
    assert tools.handles.window("W1") == ("W1", True)
    tools.discovery_previews["D1"] = "W1"
    return tools.handles.snapshot()


def observations(name, result):
    if name == "search":
        return [{"window_ref": x["preview_ref"], "doc_ref": x["doc_ref"],
                 "title": x["title"], "url": x["url"], "text": x["preview"]}
                for x in result.get("results", []) if "preview_ref" in x]
    if name == "find":
        return [{"window_ref": x["window_ref"], "doc_ref": result["doc_ref"],
                 "text": x["text"]} for x in result.get("matches", [])]
    if name == "open" and result.get("text"):
        return [{"window_ref": result["window_ref"], "doc_ref": result["doc_ref"],
                 "text": result["text"]}]
    return []


def one(client, searcher, case, arm):
    cell = case["case_id"] + ":" + arm
    tools = OrthogonalSearchFindTools()
    chosen = None
    outcome = {"cell": cell, "selected_gap": None, "action": None,
               "result": None, "observations": [], "error": None}
    try:
        snap = restore(tools, case)
        tools.searcher = searcher
        emit("cell_start", cell=cell, initial_handles=snap)
        if arm == "A1":
            choice = call(client, selector_request(case), cell, "selector")
            if choice["finish_reason"] != "stop":
                raise ValueError("selector_finish")
            selected = json.loads(choice["message"]["content"])
            if not isinstance(selected, dict) or set(selected) != {"gap_id"} or \
                    selected["gap_id"] not in {g["gap_id"] for g in case["open_gaps"]}:
                raise ValueError("selector_schema")
            chosen = selected["gap_id"]
            outcome["selected_gap"] = chosen
            emit("selector_choice", cell=cell, gap_id=chosen)
        choice = call(client, actor_request(case, arm, chosen), cell, "actor")
        parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                                       allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
        if error or len(parsed) != 1:
            raise ValueError("actor_exactly_one_tool:" + str(error or len(parsed)))
        action = {"name": parsed[0]["name"], "arguments": parsed[0]["arguments"]}
        outcome["action"] = action
        emit("tool_start", cell=cell, action=action)
        result = tools.execute(action["name"], action["arguments"])
        outcome["result"] = result
        outcome["observations"] = observations(action["name"], result)
        emit("tool_result", cell=cell, action=action, result=result,
             observations=outcome["observations"], audit=tools.audit_record())
    except Exception as exc:
        outcome["error"] = type(exc).__name__ + ":" + str(exc)[:250]
        emit("cell_error", cell=cell, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
    finally:
        emit("cell_end", cell=cell, outcome=outcome, final_handles=tools.handles.snapshot())
        tools.close()
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
        searcher = BCPlusSearcher()
        try:
            for i, case in enumerate(BANK):
                for arm in arm_order(i):
                    value = one(client, searcher, case, arm)
                    outcomes[value["cell"]] = value
                    print(value["cell"], "ok" if value["error"] is None else value["error"], flush=True)
        finally:
            searcher.close()
    assert len(outcomes) == 48
    (HERE / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze": freeze()
    elif action == "gate": gate(); print("PASS")
    elif action == "run": run()
    else: raise SystemExit("freeze|gate|run")
