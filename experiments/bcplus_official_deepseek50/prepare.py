"""Freeze the official-tool rerun after offline and API preflight."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from experiments.bcplus_native_deepseek50.native_client import Config
from experiments.bcplus_native_deepseek50.runner import write_json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/bcplus_native_deepseek50"


def digest(path):
    h = sha256()
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main():
    if (HERE / "FREEZE.json").exists():
        raise ValueError("Freeze already exists")
    selection = json.loads((OLD / "SELECTION_FREEZE.json").read_text(encoding="utf-8"))
    inputs = json.loads((OLD / "ONLINE_INPUTS.json").read_text(encoding="utf-8"))
    if len(inputs) != 50 or [x["qid"] for x in inputs] != selection["selected_qids"]:
        raise ValueError("Frozen selection and online inputs differ")
    if digest(OLD / "ONLINE_INPUTS.json") != selection["selected_questions_sha256"]:
        raise ValueError("Online inputs hash differs from original freeze")
    config = Config.load()
    if config.model != "deepseek-flash" or config.request_options() != {
        "temperature": 0, "extra_body": {"thinking": {"type": "enabled"}}
    }:
        raise ValueError("Unexpected DeepSeek model options")
    paths = [
        "experiments/bcplus_official_deepseek50/run.py",
        "experiments/bcplus_official_deepseek50/official_retrieval.py",
        "experiments/bcplus_native_deepseek50/native_client.py",
        "experiments/bcplus_native_deepseek50/runner.py",
        "BCPlus/upstream/search_agent/openai_client.py",
        "BCPlus/upstream/search_agent/prompts.py",
        "BCPlus/upstream/searcher/searchers/faiss_searcher.py",
        "BCPlus/upstream/searcher/searchers/base.py",
        "BCPlus/upstream/scripts_evaluation/evaluate_run.py",
    ]
    index_files = sorted((ROOT / "BCPlus/indexes/qwen3-embedding-8b").glob("corpus.shard*.pkl"))
    if len(index_files) != 4:
        raise ValueError("Expected four official index shards")
    freeze = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Rerun the same 50 frozen questions with the vendored BrowseComp-Plus default search-only tool and official answer prompt",
        "selected_qids": selection["selected_qids"],
        "selection_freeze_sha256": digest(OLD / "SELECTION_FREEZE.json"),
        "online_inputs_sha256": digest(OLD / "ONLINE_INPUTS.json"),
        "dataset_sha256": selection["dataset_sha256"],
        "retriever": "BrowseComp-Plus FaissSearcher + SearchToolHandler",
        "retriever_model": "Qwen/Qwen3-Embedding-8B (local identical-weight copy)",
        "corpus": "Tevatron/browsecomp-plus-corpus",
        "corpus_revision": "b27b02bc3e45511b8b82a13e6f90ce761df726f6",
        "corpus_rows_preflight": 100195,
        "index_sha256": {str(p.relative_to(ROOT)): digest(p) for p in index_files},
        "tool_names": ["search"],
        "search_k": 5,
        "snippet_max_tokens": 512,
        "snippet_tokenizer": "Qwen/Qwen3-0.6B",
        "query_template": "QUERY_TEMPLATE_NO_GET_DOCUMENT",
        "system_prompt": None,
        "model_provider": "DeepSeek",
        "model_base_url": config.base_url,
        "transport_base_url": "https://api.deepseek.com/beta",
        "model": config.model,
        "request_options": config.request_options(),
        "api_workers_initial": 50,
        "api_workers_max": 50,
        "retrieval_workers": 1,
        "concurrency_rule": "fixed for all unsent questions; no retries or replacement",
        "http_max_connections_per_client": 2,
        "http_max_keepalive_connections_per_client": 1,
        "timeout_seconds": config.timeout,
        "sdk_max_retries": 0,
        "semantic_retries": 0,
        "max_tool_rounds_emergency_cap": 200,
        "max_tool_calls_per_round": 8,
        "attention_implementation": "sdpa (FlashAttention2 unavailable on host; same upstream model/query encoder)",
        "provider_transport_difference": "Official BC+ tool schema translated from Responses envelope to DeepSeek Chat Completions envelope; strict mode via DeepSeek beta URL",
        "retrieval_preflight": {"status": "passed", "top5_docids": ["26354", "56938", "12704", "22369", "74715"]},
        "strict_mode_api_preflight": {"status": "passed", "model": "deepseek-flash", "tool_called": "search", "prompt_tokens": 299, "completion_tokens": 39},
        "source_sha256": {relative: digest(ROOT / relative) for relative in paths},
    }
    write_json(HERE / "FREEZE.json", freeze)


if __name__ == "__main__":
    main()
