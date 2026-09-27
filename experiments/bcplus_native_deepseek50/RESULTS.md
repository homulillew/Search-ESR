# BC+ Random50 Comparison Set — native baseline

Branch: experiment/bcplus-native-deepseek50-baseline
Commit: 9688a98a943b98eee53d7772b74be9330b4ed4b1

Model: DeepSeek Flash (`deepseek-flash`)
Mode: thinking enabled (requested temperature 0; provider documents that temperature is ineffective in thinking mode)
Execution: 50 parallel independent sessions; one serialized local retrieval worker
Benchmark: BrowseComp-Plus
Baseline policy: native v000 Search + GetDocument
Sampling: random frozen 50; seed = 20260928
Dataset SHA256: `44b80cc9fcd9dd5a44aa09292c2165364b0c0e9df26c9cd6c11846165a0916b7`
Historical overlap: 2/50 (`1201`, `645`); no resampling

Correct: 46 / 50
Accuracy: 92.0% (deterministic plus blinded investigator review; no Qwen judge)
95% Wilson CI: [81.2%, 96.8%]

Natural answers: 50 / 50
Emergency-cap-forced answers: 0 / 50
Run/API failures: 0 / 50
Insufficient-evidence answers: 4 / 50 (explicit phrase heuristic)

GetDocument adoption: 50 / 50
Search calls: 1203 total; median 15; p90 45.1; max 117
GetDocument calls: 151 total; median 3; p90 5.1; max 9
Search-only answers: 0 / 50
Repeated Search trajectories: 1 / 50
Rounds >12: 16 / 50
Rounds >25: 5 / 50
Rounds >50: 2 / 50
Rounds >100: 0 / 50
Gold-string observed: 40 / 50 (heuristic only)
Correct given observed: 39 / 40
Answers with a citation marker: 49 / 50; with a URL: 46 / 50
Corrected URL audit: 3 / 50 answers contained 5 exact URLs not seen in tool metadata; 0 explicit invented docids detected
Median/p90/max tool rounds: 7.5 / 21.8 / 56
Total model requests: 641
Total prompt/completion tokens: 78191456 / 1180545
Total wall-clock seconds: 604.5
Estimated cost: ¥11.6578; unpriced responses: 0

The user stopped an earlier six-worker attempt after paid calls began and directed this complete 50-worker restart. Its records remain under `runs/20260927T215048.165192Z` and are excluded from this score. That attempt recorded 101 requests, 95 responses, and an additional estimated ¥1.1932 of priced usage; any in-flight requests without responses are not included in that estimate. This score and the ¥11.6578 estimate refer only to the formal restarted batch.

The first-pass citation regex overcounted unmatched URLs because it cut off parentheses in legitimate URLs. The corrected post-hoc citation audit found 5 unmatched exact URLs across 3 answers; these are unverified exact citations, not proof of fabricated sources. Answer accuracy is scored independently of citation fidelity.

The 50 qids are now the BC+ Random50 Comparison Set and are no longer fresh. Later comparisons must account for model, tools, prompt, termination cap, tokens and cost; a paired system difference alone does not isolate recoverability.
