#!/usr/bin/env python3
"""测量 LLM API 的输出速度（tokens/s）。

核心区分两个指标：
  - TTFT (time to first token)：发出请求到收到第一个 token 的延迟
  - 生成速度：首个 token 之后，纯输出的 tokens/s
  - 端到端速度：总输出 token 数 / 总耗时（含 TTFT）

用法:
  python3 bench_output_speed.py                      # 用环境变量里的默认模型/base_url
  python3 bench_output_speed.py --max-tokens 2000 --runs 5
  python3 bench_output_speed.py --model claude-sonnet-5 --base-url https://api.anthropic.com
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time

import anthropic

DEFAULT_PROMPT = (
    "从 1 数到 400，每行一个数字，只输出数字，不要任何其它文字、解释或标点。"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
                   help="模型名（默认读 $ANTHROPIC_MODEL）")
    p.add_argument("--base-url", default=os.environ.get("ANTHROPIC_BASE_URL"),
                   help="API base URL（默认读 $ANTHROPIC_BASE_URL）")
    p.add_argument("--max-tokens", type=int, default=1024, help="单次请求最大输出 token 数")
    p.add_argument("--runs", type=int, default=3, help="正式测量轮数")
    p.add_argument("--warmup", type=int, default=1, help="预热轮数（不计入统计）")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help="用于压测的 prompt")
    p.add_argument("--timeout", type=float, default=300, help="单次请求超时（秒）")
    return p.parse_args()


def one_run(client: anthropic.Anthropic, model: str, prompt: str, max_tokens: int,
            timeout: float) -> dict:
    """跑一次流式请求，返回计时与 token 数。"""
    t_start = time.perf_counter()
    first_token_time = None
    text_parts: list[str] = []

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        timeout=timeout,
    ) as stream:
        for delta in stream.text_stream:
            if first_token_time is None and delta:
                first_token_time = time.perf_counter()
            text_parts.append(delta)
        final = stream.get_final_message()

    t_end = time.perf_counter()

    output_tokens = final.usage.output_tokens if final.usage else None
    input_tokens = final.usage.input_tokens if final.usage else None
    stop_reason = final.stop_reason
    text = "".join(text_parts)

    if first_token_time is None:
        first_token_time = t_end  # 空输出，退化为端到端

    ttft = first_token_time - t_start
    gen_time = t_end - first_token_time
    total_time = t_end - t_start

    return {
        "ttft": ttft,
        "gen_time": gen_time,
        "total_time": total_time,
        "output_tokens": output_tokens or 0,
        "input_tokens": input_tokens,
        "stop_reason": stop_reason,
        "gen_tps": (output_tokens / gen_time) if (output_tokens and gen_time > 0) else 0.0,
        "e2e_tps": (output_tokens / total_time) if (output_tokens and total_time > 0) else 0.0,
        "text_preview": text[:40].replace("\n", "\\n"),
    }


def fmt_stats(values: list[float]) -> str:
    if not values:
        return "n/a"
    return (f"mean={statistics.mean(values):7.2f}  median={statistics.median(values):7.2f}"
            f"  min={min(values):7.2f}  max={max(values):7.2f}")


def main() -> int:
    args = parse_args()

    client = anthropic.Anthropic(base_url=args.base_url) if args.base_url else anthropic.Anthropic()
    # SDK 会自动读取 ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL

    print(f"模型      : {args.model}")
    print(f"base URL  : {args.base_url or os.environ.get('ANTHROPIC_BASE_URL', '(默认)')}")
    print(f"max_tokens: {args.max_tokens}   预热轮: {args.warmup}   测量轮: {args.runs}")
    print(f"prompt    : {args.prompt[:50]}{'...' if len(args.prompt) > 50 else ''}")
    print("-" * 88)

    # ---- 预热：建立连接、不计时 ----
    for i in range(args.warmup):
        try:
            r = one_run(client, args.model, args.prompt, args.max_tokens, args.timeout)
            print(f"[warmup {i+1}] 输出 {r['output_tokens']} tokens，"
                  f"端到端 {r['total_time']:.2f}s，stop={r['stop_reason']}")
        except Exception as e:  # noqa: BLE001
            print(f"[warmup {i+1}] 失败: {e}", file=sys.stderr)
    if args.warmup:
        print("-" * 88)

    # ---- 正式测量 ----
    results = []
    for i in range(args.runs):
        try:
            r = one_run(client, args.model, args.prompt, args.max_tokens, args.timeout)
            results.append(r)
            print(f"[run {i+1}] TTFT={r['ttft']*1000:7.0f}ms  生成={r['gen_time']:6.2f}s  "
                  f"总={r['total_time']:6.2f}s  out={r['output_tokens']:5d}  "
                  f"生成速度={r['gen_tps']:7.2f} tok/s  端到端={r['e2e_tps']:7.2f} tok/s  "
                  f"| {r['text_preview']}")
        except anthropic.APITimeoutError:
            print(f"[run {i+1}] 超时（{args.timeout}s）", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[run {i+1}] 失败: {type(e).__name__}: {e}", file=sys.stderr)

    print("=" * 88)
    if not results:
        print("没有成功完成的测量轮次，无法统计。", file=sys.stderr)
        return 1

    n = len(results)
    ttfts = [r["ttft"] for r in results]
    gens = [r["gen_tps"] for r in results]
    e2es = [r["e2e_tps"] for r in results]
    tokens = [r["output_tokens"] for r in results]

    print(f"成功轮数    : {n}/{args.runs}")
    print(f"输出 tokens : {fmt_stats([float(t) for t in tokens])}")
    print(f"TTFT        : {fmt_stats([t * 1000 for t in ttfts])}  (ms)")
    print(f"生成速度    : {fmt_stats(gens)}  tok/s   <-- 首个 token 之后的纯输出速度")
    print(f"端到端速度  : {fmt_stats(e2es)}  tok/s   <-- 含 TTFT")

    truncated = [r for r in results if r["stop_reason"] == "max_tokens"]
    if truncated:
        print(f"\n注意：{len(truncated)} 轮因 max_tokens={args.max_tokens} 被截断，"
              f"生成速度可能被低估（输出越长越接近稳定速率）。可加大 --max-tokens 重测。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
