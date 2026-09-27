"""Summarize the frozen official-search run after Qwen judgments complete."""
from collections import Counter
import json
from pathlib import Path
import statistics

from experiments.bcplus_native_deepseek50.evaluate import (
    api_concurrency_points, distribution, estimate_cost, percentile,
)
from experiments.bcplus_native_deepseek50.runner import write_json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def qrels(path):
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 4:
            result.setdefault(parts[0], set()).add(parts[2])
    return result


def main():
    end = json.loads((HERE / "runs/BATCH_END.json").read_text(encoding="utf-8"))
    judge = json.loads((HERE / "QWEN_RESULTS.json").read_text(encoding="utf-8"))
    batch = HERE / "runs" / end["batch_id"]
    positives = qrels(ROOT / "BCPlus/upstream/topics-qrels/qrel_evidence.txt")
    rows = []
    all_events = []
    tool_latencies = []
    for directory in sorted(batch.glob("qid_*"), key=lambda p: int(p.name[4:])):
        qid = directory.name[4:]
        summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
        judgment = json.loads((HERE / "judgments" / f"qid_{qid}.json").read_text(encoding="utf-8"))
        events = [json.loads(line) for line in (directory / "events.jsonl").open(encoding="utf-8")]
        all_events.extend(events)
        docids = {str(hit["docid"]) for event in events if event["kind"] == "tool_result"
                  for hit in event["result"] if hit.get("docid") is not None}
        relevant = positives.get(qid, set())
        recall = len(docids & relevant)/len(relevant) if relevant else None
        tool_latencies.extend(event["elapsed_seconds"] for event in events if event["kind"] == "tool_result")
        rows.append({"qid": qid, "status": summary["status"], "correct_qwen": judgment["correct_primary"],
                     "search_calls": summary["search_calls"], "tool_rounds": summary["tool_round_count"],
                     "unique_search_queries": summary["unique_search_queries"],
                     "exact_duplicate_queries": summary["exact_duplicate_queries"],
                     "retrieved_docids": sorted(docids), "evidence_recall": recall,
                     "api_requests": summary["api_requests"], "prompt_tokens": summary["prompt_tokens"],
                     "completion_tokens": summary["completion_tokens"],
                     "elapsed_seconds": summary["elapsed_seconds"],
                     "answer": judgment["response"], "gold_answer": judgment["gold_answer"],
                     "judge_extracted_final_answer": judgment["parsed"].get("extracted_final_answer")})
    if len(rows) != 50:
        raise ValueError("Expected exactly 50 questions")
    points = [point for directory in batch.glob("qid_*")
              for point in api_concurrency_points([json.loads(line) for line in
                  (directory / "events.jsonl").open(encoding="utf-8")])]
    active = peak = 0
    for _, change in sorted(points, key=lambda x: (x[0], x[1])):
        active += change
        peak = max(peak, active)
    cost = estimate_cost(all_events)
    available_recalls = [r["evidence_recall"] for r in rows if r["evidence_recall"] is not None]
    cache_valid = [json.loads((batch / f"qid_{r['qid']}" / "summary.json").read_text(encoding="utf-8")) for r in rows]
    hit = sum(s["cache_hit_tokens"] for s in cache_valid)
    cache_input = sum(s["cache_input_tokens"] for s in cache_valid)
    status_counts = dict(Counter(r["status"] for r in rows))
    skipped = [r["qid"] for r in rows if r["status"] == "RUN_FAILED" or not r["answer"]]
    actual_judge_errors = [qid for qid in judge["parse_or_api_error_qids"] if qid not in skipped]
    result = {
        "batch_id": end["batch_id"],
        "primary_judge": judge["score_kind"],
        "correct": judge["correct"], "denominator": 50, "accuracy": judge["accuracy"],
        "wilson_95": judge["wilson_95"],
        "judge_skipped_no_agent_answer_qids": skipped,
        "judge_actual_parse_or_api_error_qids": actual_judge_errors,
        "status_counts": status_counts,
        "search_calls": distribution([r["search_calls"] for r in rows]),
        "tool_rounds": distribution([r["tool_rounds"] for r in rows]),
        "api_requests": distribution([r["api_requests"] for r in rows]),
        "elapsed_seconds": distribution([r["elapsed_seconds"] for r in rows]),
        "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "completion_tokens": sum(r["completion_tokens"] for r in rows),
        "peak_api_concurrency": peak,
        "tool_error_count": sum(e["kind"] == "tool_error" for e in all_events),
        "tool_latency_median_seconds": statistics.median(tool_latencies) if tool_latencies else None,
        "tool_latency_p95_seconds": percentile(tool_latencies, 95),
        "evidence_recall_mean": statistics.mean(available_recalls) if available_recalls else None,
        "evidence_recall_qids": len(available_recalls),
        "cache_hit_rate_on_consistent_usage": hit/cache_input if cache_input else None,
        "cache_usage_missing_or_inconsistent_records": sum(s["cache_usage_missing_or_inconsistent_records"] for s in cache_valid),
        "deepseek_cost_estimate": cost,
        "judge_prompt_tokens": judge["judge_prompt_tokens"],
        "judge_completion_tokens": judge["judge_completion_tokens"],
        "agent_batch_wall_seconds": end["elapsed_seconds"],
        "comparison_old_run": "46/50 by deterministic plus investigator review under different Search/GetDocument conditions; not a paired judge-only comparison",
    }
    write_json(HERE / "RESULTS.json", result)
    write_json(HERE / "PER_QUESTION.json", rows)
    incorrect = [r["qid"] for r in rows if not r["correct_qwen"]]
    lines = [
        "# BC+ official-search DeepSeek Flash rerun",
        "",
        f"Primary Qwen3-32B answer accuracy: **{result['correct']}/50 = {100*result['accuracy']:.1f}%**.",
        f"95% Wilson interval: {100*result['wilson_95'][0]:.1f}%–{100*result['wilson_95'][1]:.1f}%.",
        f"Incorrect qids: {', '.join(incorrect) if incorrect else 'none'}.",
        f"Judge skipped for missing agent answer: {', '.join(skipped) if skipped else 'none'}. Judge parse/API errors on submitted answers: {', '.join(actual_judge_errors) if actual_judge_errors else 'none'}.",
        "",
        "## Protocol",
        "",
        "Same frozen 50 questions as the prior run. Vendored BC+ `FaissSearcher` uses Qwen3-Embedding-8B and the official corpus. The vendored `SearchToolHandler` exposes search only, fixed top 5, with 512-token snippets using the Qwen3-0.6B tokenizer. The agent receives the upstream `QUERY_TEMPLATE_NO_GET_DOCUMENT` prompt. DeepSeek Flash thinking mode uses 50 independent sessions; the retriever is serialized. No API retries, question replacement, or best-of selection.",
        "",
        "Qwen3-32B uses the upstream grader prompt and parser, temperature 0.7, top_p 0.8, top_k 20, max output 4096, thinking disabled. It runs through a hosted OpenAI-compatible endpoint because the unquantized model does not fit the available local GPUs; this runtime differs from upstream vLLM.",
        "",
        "The DeepSeek adapter translates the upstream Responses tool schema into Chat Completions and uses the provider beta endpoint for strict tool calls. The Tevatron encoder uses SDPA attention because FlashAttention2 is unavailable on this host. These transport/runtime details are recorded in `FREEZE.json`.",
        "",
        "## Run statistics",
        "",
        f"Statuses: {status_counts}. Peak API concurrency: {peak}. Agent wall time: {end['elapsed_seconds']:.1f}s.",
        f"Search calls: {result['search_calls']['total']} total, median {result['search_calls']['median']:.1f}/question. Tool rounds: median {result['tool_rounds']['median']:.1f}, p90 {result['tool_rounds']['p90']:.1f}, max {result['tool_rounds']['max']}.",
        f"DeepSeek tokens: {result['prompt_tokens']:,} input, {result['completion_tokens']:,} output. Estimated DeepSeek cost: ¥{cost['estimated_cny']:.4f} (usage-based estimate, not billed amount).",
        f"Official evidence-qrel mean recall across {len(available_recalls)} qids: {100*result['evidence_recall_mean']:.1f}%" if available_recalls else "Evidence-qrel recall unavailable.",
        "",
        "The earlier Search/GetDocument run scored 46/50 by a different judge. Its tool access and scoring differ, so the two percentages do not isolate a single causal effect.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"accuracy={result['correct']}/50 cost_estimate_cny={cost['estimated_cny']:.4f}")


if __name__ == "__main__":
    main()
