"""Run frozen V2 queries and mechanical D pairs through unchanged local Search."""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
V2 = ROOT / "experiments/variable_preserving_state/query_bias"
BANK = json.loads((HERE / "BANK.json").read_text())
CASES = {c["case_id"]: c for c in json.loads((V2 / "V2_CASES.json").read_text())}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
K = 5
MODEL_PATH = Path("/data/model/Qwen3-Embedding-8B")
INDEX_FILES = sorted((ROOT / "BCPlus/indexes/qwen3-embedding-8b").glob("*.pkl")) + [
    ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite",
    ROOT / "BCPlus/indexes/bcplus-qwen3-8b/metadata.json",
]
MODEL_METADATA = [MODEL_PATH / p for p in ("config.json", "tokenizer.json", "tokenizer_config.json",
                                         "model.safetensors.index.json")]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(BANK, key=lambda b: hashlib.sha256(b["search_id"].encode()).hexdigest())


def source_paths():
    return [HERE / p for p in ("PROTOCOL.md", "REVIEW_RUBRIC.md", "BANK.json", "prepare_bank.py",
                                "run.py", "analyze.py")] + [
        V2 / "V2_CASES.json", V2 / "results.json", V2 / "REVIEWS.json",
        ROOT / "BCPlus/scripts/search_bcplus.py", ROOT / "llm_chat/search_find_v3b_agent.py",
        ROOT / "llm_chat/search_find_agent.py", ROOT / "llm_chat/raw_windows.py",
        ROOT / "llm_chat/window_locator.py", ROOT / "llm_chat/window_units.py",
    ]


def validate_bank():
    from prepare_bank import despeculate
    v2_rows = json.loads((V2 / "results.json").read_text())["rows"]
    by_cell = {f"{r['case_id']}:{r['arm']}": r for r in v2_rows}
    assert len(BANK) == 71 and len(by_cell) == 48 and len(CASES) == 16
    assert len({b["search_id"] for b in BANK}) == len(BANK)
    for b in BANK:
        source = by_cell[b["source_cell"]]
        assert b["case_id"] == source["case_id"] and b["qid"] == CASES[b["case_id"]]["qid"]
        assert b["frozen_leaking_values"] == source["review"]["leaking_values"]
        assert b["query"] == (source["query"] if b["variant"] == "S"
                              else despeculate(source["query"], b["frozen_leaking_values"]))
        assert b["variant"] == "S" or b["frozen_leaking_values"]


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    doc = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "provider_model": {"retriever": "Qwen3-Embedding-8B", "path": str(MODEL_PATH),
                           "query_prefix": "Instruct: Given a web search query, retrieve relevant passages that answer the query\\nQuery:",
                           "v2_query_generator": "deepseek-flash", "max_retries": 0},
        "k": K, "search_backend": "OrthogonalSearchFindTools fresh workspace + BCPlusSearcher",
        "preview_budget_tokens": RawWindowBuilder.search_budget,
        "sample_count": len(BANK), "original_count": 48, "paired_D_count": 23,
        "case_ids": [b["search_id"] for b in BANK],
        "qid_checkpoints": {cid: [c["qid"], c["checkpoint"]] for cid, c in CASES.items()},
        "prefix_sha256": {cid: digest([c["raw_question"], c["visible_evidence"]]) for cid, c in CASES.items()},
        "testcard_sha256": {cid: digest(c["test_card_state"]) for cid, c in CASES.items()},
        "query_sha256": {b["search_id"]: digest(b["query"]) for b in BANK},
        "leaking_values_sha256": {b["search_id"]: digest(b["frozen_leaking_values"]) for b in BANK},
        "search_order": [b["search_id"] for b in order()],
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "model_metadata_sha256": {str(p): sha(p) for p in MODEL_METADATA},
        "index_sha256": {str(p.relative_to(ROOT)): sha(p) for p in INDEX_FILES},
        "tool_schema_sha256": digest({"search": {"query": "string", "k": K}}),
        "review_rubric_sha256": sha(HERE / "REVIEW_RUBRIC.md"),
        "gate": "diagnostic; no stop gate over S2",
        "failure_policy": "one Search per frozen S/D cell, max_retries=0, retain every backend/localizer failure",
    }
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    validate_bank()
    doc = json.loads(FREEZE.read_text())
    checks = {
        "sources": doc["source_sha256"] == {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "model_metadata": doc["model_metadata_sha256"] == {str(p): sha(p) for p in MODEL_METADATA},
        "index": doc["index_sha256"] == {str(p.relative_to(ROOT)): sha(p) for p in INDEX_FILES},
        "queries": all(doc["query_sha256"][b["search_id"]] == digest(b["query"]) for b in BANK),
        "order": doc["search_order"] == [b["search_id"] for b in order()],
        "rubric": doc["review_rubric_sha256"] == sha(HERE / "REVIEW_RUBRIC.md"),
        "k_and_count": doc["k"] == K and doc["sample_count"] == 71 and doc["paired_D_count"] == 23,
    }
    (HERE / "gate.txt").write_text("\n".join(("PASS " if v else "FAIL ") + k for k, v in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    from transformers import AutoTokenizer
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher = BCPlusSearcher()
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH), local_files_only=True, use_fast=True)
    try:
        for b in order():
            sid = b["search_id"]
            tools = OrthogonalSearchFindTools()
            tools.searcher = searcher
            tools.window_builder = RawWindowBuilder(tokenizer)
            emit("search_request", search_id=sid, query=b["query"], k=K,
                 query_sha256=digest(b["query"]))
            started = time.monotonic()
            try:
                result = tools.execute("search", {"query": b["query"], "k": K})
                audit = tools.audit_record()
                emit("search_result", search_id=sid, result=result, audit=audit,
                     latency_seconds=time.monotonic() - started)
                print(sid, "ok", len(result["results"]), flush=True)
            except Exception as exc:
                emit("search_error", search_id=sid, error_type=type(exc).__name__,
                     error=str(exc)[:500], latency_seconds=time.monotonic() - started)
                print(sid, "error", type(exc).__name__, flush=True)
            finally:
                tools.searcher = None
                tools.close()
    finally:
        searcher.close()


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
