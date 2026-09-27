"""Load the vendored BC+ FAISS retriever and tool handler without unrelated backends.

The upstream searchers package eagerly imports BM25/Pyserini, which requires a
JVM even when the FAISS backend is selected.  Loading the FAISS module as an
isolated package preserves its source and behavior while avoiding that import.
The upstream OpenAI client likewise eagerly imports all searcher types, so its
SearchToolHandler class is compiled verbatim from the vendored source AST.
"""
import ast
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "BCPlus/upstream"


def official_classes():
    package_name = "_bcplus_official_faiss"
    if package_name not in sys.modules:
        package = ModuleType(package_name)
        package.__path__ = [str(UPSTREAM / "searcher/searchers")]
        sys.modules[package_name] = package
    faiss_module = importlib.import_module(f"{package_name}.faiss_searcher")
    # The vendored Tevatron defaults to FlashAttention2, unavailable with this
    # host's Torch/CUDA build. SDPA computes the same attention operation and
    # lets the upstream FAISS searcher and DenseModel.encode_query run intact.
    if not getattr(faiss_module, "_bcplus_sdpa_compat", False):
        original_model_arguments = faiss_module.ModelArguments

        def model_arguments_sdpa(*args, **kwargs):
            result = original_model_arguments(*args, **kwargs)
            result.attn_implementation = "sdpa"
            return result

        faiss_module.ModelArguments = model_arguments_sdpa
        faiss_module._bcplus_sdpa_compat = True

    source = UPSTREAM / "search_agent/openai_client.py"
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SearchToolHandler")
    isolated = ast.Module(body=[node], type_ignores=[])
    namespace = {"AutoTokenizer": AutoTokenizer, "json": json}
    exec(compile(isolated, str(source), "exec"), namespace)
    return faiss_module.FaissSearcher, namespace["SearchToolHandler"]


def make_searcher():
    FaissSearcher, SearchToolHandler = official_classes()
    args = SimpleNamespace(
        index_path=str(ROOT / "BCPlus/indexes/qwen3-embedding-8b/corpus.shard*.pkl"),
        model_name="/data/model/Qwen3-Embedding-8B",
        normalize=True,
        pooling="eos",
        torch_dtype="float16",
        dataset_name="Tevatron/browsecomp-plus-corpus",
        task_prefix="Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:",
        max_length=8192,
    )
    searcher = FaissSearcher(args)
    handler = SearchToolHandler(searcher, snippet_max_tokens=512, k=5, include_get_document=False)
    return searcher, handler


def chat_tool_definition(handler):
    """Translate only the Responses API envelope to Chat Completions format."""
    definitions = handler.get_tool_definitions()
    assert len(definitions) == 1 and definitions[0]["name"] == "search"
    original = definitions[0]
    return [{"type": "function", "function": {
        "name": original["name"],
        "description": original["description"],
        "parameters": original["parameters"],
        "strict": original["strict"],
    }}]
