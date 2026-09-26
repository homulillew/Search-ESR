# Cost, cache and decision latency

All costs include both decisions and every returned preview sent to U1. No price conversion is estimated. Tokens are provider usage, including reported reasoning within output tokens. Cache rate = total hit tokens / total input tokens, not an average of per-request rates.

## D3_D4_diagnostic

|Metric|G|H|
|---|---:|---:|
|Actor calls|10|10|
|Tool calls|7|8|
|Search|7|2|
|Find|0|6|
|Open|0|0|
|Writer calls|35|15|
|Input tokens|109,930|63,750|
|Output tokens|53,798|38,086|
|Total tokens|163,728|101,836|
|Cache hit tokens|61,056|30,976|
|Cache miss tokens|48,874|32,774|
|Reasoning tokens (part of output)|51,747|36,817|
|Weighted cache hit rate|55.54%|48.59%|
|Summed model request seconds|279.499|191.910|
|Tool execution seconds (excludes loading)|1.996|0.985|

H used 37.80% fewer tokens. Recovery quality is not equal; this does not pass the equal-recovery cost rule.

## all_diagnostic

|Metric|G|H|
|---|---:|---:|
|Actor calls|14|14|
|Tool calls|10|11|
|Search|10|3|
|Find|0|8|
|Open|0|0|
|Writer calls|50|22|
|Input tokens|147,434|84,860|
|Output tokens|76,698|53,073|
|Total tokens|224,132|137,933|
|Cache hit tokens|80,384|42,750|
|Cache miss tokens|67,050|42,110|
|Reasoning tokens (part of output)|73,709|51,182|
|Weighted cache hit rate|54.52%|50.38%|
|Summed model request seconds|391.978|264.998|
|Tool execution seconds (excludes loading)|2.618|1.175|

H used 38.46% fewer tokens. Recovery quality is not equal; this does not pass the equal-recovery cost rule.

## Total recorded usage

100 model calls: 232,294 input + 129,771 output = 362,065 tokens. Cache hit 123,134, miss 109,160; weighted hit rate **53.01%**. All 100 calls reported usage.

## Paired costs

|Case|G tokens|H tokens|G tools|H tools|Cheaper tokens|Cheaper tools|
|---|---:|---:|---:|---:|---|---|
|DR01|50,835|30,704|2|2|H_cheaper|tie|
|DR02|21,023|22,941|1|1|G_cheaper|tie|
|DR03|48,940|22,822|2|2|H_cheaper|tie|
|DR04|26,592|9,242|1|1|H_cheaper|tie|
|DR05|16,338|16,127|1|2|H_cheaper|G_cheaper|
|DR06|41,986|26,896|2|2|H_cheaper|tie|
|DR07|18,418|9,201|1|1|H_cheaper|tie|

## Interpretation

- Search normally exposes five previews and therefore five Writer calls. Find normally exposes one, sometimes none. Much of the token difference follows this fan-out; it is not evidence that local policy is generally more efficient at equal recovery quality.
- G first sufficient evidence and first necessary Claim are at decision 1 for all five D3/D4 cases. H has evidence at decisions 2/1/1/1/not-recovered for DR01–05; strict Claims at 2/1/1/not-recovered/not-recovered. Failures are censored at horizon 2, not silently omitted.
- H adds no action-count advantage: eight tools versus seven in D3/D4. DR01 and D2 DR06 need an extra recovery decision after an insufficient first Find. No faster local recovery was observed on this bank.
- Summed request durations are not end-to-end wall time. Four requests can run concurrently; cache state, completion length and scheduling are not controlled latency interventions. Tool timing excludes loading, registry restoration and model initialization.
- Per-qid correlation and known-case selection preclude independent-sample significance claims.
