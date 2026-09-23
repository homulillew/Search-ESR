# Qwen vs DeepSeek Search–Find backend intervention

## Scope and protocol

The treatment is `deepseek-flash` on `https://api.deepseek.com`; the fixed
historical baseline is `qwen3.7-flash`. The 13 prefixes, prefix-only labels,
M1/M4 instructions, Search/Find/Open schema, retriever, and evidence excerpts
are unchanged. Atria records remain historical, not DeepSeek observations.
Each DeepSeek cell was requested once with zero SDK retries. All raw responses,
errors, validation results, and cache usage are retained in stage event files.

M0 default-thinking mode passed ordinary chat, automatic Search, a two-call
batch, and the strict synthetic validator. Named `tool_choice` returned HTTP
400 because this mode does not support forced named tools. A separately frozen
M0b request with thinking disabled returned one valid named Search. M1–M5 used
the provider's default thinking mode and automatic tool choice where tools
were present. No real tool ran in M0–M2. The M0 failure remains in its events.

**Order deviation:** M4's fixed batch began after M2 and before M3. The M3
entry condition was initially misread as requiring a policy gain; the original
task allows an M1 *or* M2 signal, and M1 qualified. The four M3 cells were
selected and frozen from M1/M2 before M4 responses were semantically reviewed.
M3 then ran before M5. This timing deviation limits a claim of exact adherence
to the planned stage order, even though M3 selection did not use M4 outcomes.

## Results

| Probe | Fixed Qwen baseline | DeepSeek observation | Interpretation |
| --- | --- | --- | --- |
| M1 explicit planning, 13 prefixes | 10 responses, 3 timeouts; acceptable scope 5/13; need 5/10; source type 7/10 | 13 responses; acceptable scope 13/13; need 13/13; source type 13/13 | Stronger explicit planning, with provider timeouts separated from Qwen's semantic errors. On 10 both-response prefixes, scope was 5/10 vs 10/10. Exact paired McNemar p=0.0078 on all 13, descriptive given small n. |
| M1 document target | 1/4 correct among document plans | 1/4 correct among document plans | No target-selection gain; compatible scope alone is insufficient. |
| M2 natural next decision, 13 prefixes | 16 Search calls and 1 Find call across valid responses; document plan realized 0/4 | 32 Search calls, 0 Find; 12 multi-tool Search batches and 1 stop; document plan realized 0/4 | Explicit planning did not transfer into local tool use. DeepSeek's parallel tool behavior is a provider/model interaction, not a schema error. |
| M3 four selected checkpoints × two harness arms, at most four decisions | Orthogonal: 23 Search, 1 Find, 3 Open; 9 no-gain Search decisions, next-decision Find 0, next-decision Search 5 | Orthogonal: 27 Search, 2 Find, 1 Open; 11 no-gain Search decisions, next-decision Find 2, next-decision Search 7 | Orthogonal Search prompted some delayed Find use, but Search persistence remained and neither DeepSeek Find yielded the requested decisive evidence. |
| M4 eight oracle evidence cases, E1 | Relation 7/8; calibrated non-stop 3/8; single-reviewer belief update 1/8 | Relation 7/8; calibrated non-stop 8/8; single-reviewer belief update 6/8 | The main gain is keeping the full question unresolved after partial evidence. Exact four-way relation classification did not improve. |
| M5 native qid 546/1094, 12-decision cap | Historical v3a qid 1094 used 28 Search calls and had 62 D# handles in its first 12 decisions; no Find/Open | qid 546: first request HTTP 503, no trajectory. qid 1094: 7 Search, 3 Find, 2 Open; 51 D# handles; horizon without answer | The qid 1094 action mix changed. This is descriptive: historical Qwen used v3a and a different horizon, whereas DeepSeek used Orthogonal Search. The 503 is a provider failure, not a semantic failure. |

M3 DeepSeek P0 used 30 Search and 2 Find; P1 used 27 Search, 2 Find, 1
Open. P1's two Find responses were a Ding Junhui career-results span and an
unrelated stoppage-time football list. Neither establishes the target match
sequence or free-kick taker. M3's no-gain decisions contain at least one
Search response with no new D#; another call in the same batch may gain a
document. Calls in that batch are not credited as reactions to the no-gain.

M4 belief-update scores are a single Codex review under the frozen rubric,
with one reason for each E1 model cell in `evidence_update/semantic_scores.json`.
Both models have 0/8 explicit unsupported overrides under that narrower rule.
The historical M4 parser expected a colon after `Did the candidate change?`,
but the frozen instruction omitted it; `observed_candidate_changed` in the
DeepSeek summary parses the optional colon for both models. The single-reviewer
scores read the raw answers and should not be treated as an independently
blinded evaluation.

## DeepSeek prompt-cache telemetry

Hit rate is `sum(prompt_cache_hit_tokens) /
sum(prompt_cache_hit_tokens + prompt_cache_miss_tokens)` over responses with
consistent provider-reported usage. This is a token-weighted *DeepSeek-only*
description; it is not a cross-model cost or quality comparison. Error requests
have unknown usage and are excluded, never counted as zero-hit responses.

| Stage | Responses | API errors | Cache hit tokens | Cache miss tokens | Weighted hit rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| M0 | 3 | 1 | 0 | 1,411 | 0.0% |
| M0b | 1 | 0 | 0 | 361 | 0.0% |
| M1 | 13 | 0 | 277,120 | 84,285 | 76.7% |
| M2 | 13 | 0 | 358,016 | 113,367 | 76.0% |
| M3 | 26 | 0 | 1,064,320 | 76,854 | 93.3% |
| M4 | 16 | 0 | 311,040 | 4,133 | 98.7% |
| M5 | 12 | 1 | 220,032 | 27,308 | 89.0% |
| **Total** | **84** | **2** | **2,230,528** | **307,719** | **87.9%** |

All 84 successful responses reported both fields consistently. The cache is
automatic and best-effort; there was no deliberate warm-up. Repeated long
prefixes and possible provider-side activity outside this experiment can affect
the observed hit rate. Per-response usage is in `CACHE_USAGE_FINAL.json` and
in each raw event's `usage` field.

## Mechanism conclusion

DeepSeek improved explicit need/source/scope descriptions and single-reviewer
handling of partial evidence, especially avoiding premature stop. The
planning-to-action gap remained: M2 issued no Find, and M3 still searched after
most no-gain decisions. Model capability affects evidence interpretation, but
this intervention does not show that a stronger model alone repairs Search
persistence or document routing. M5's 503 and 12-decision horizon prevent a
claim about final-answer accuracy or qid 546 native behavior.

DeepSeek protocol details: [Chat Completion API](https://api-docs.deepseek.com/api/create-chat-completion/),
[Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/), and
[Context Caching](https://api-docs.deepseek.com/guides/kv_cache/).
