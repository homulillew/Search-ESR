# S1 result: query mechanism changed, direct retrieval gate failed

All 120 frozen DeepSeek `deepseek-flash` requests returned valid one-query JSON. There were zero API, format, and retrieval failures, zero retries, and no query repair. The 96 main queries and 24 controls were committed at `e99c311` before any new embedding or FAISS search. The retriever, index, document representation, and top50 budget were unchanged. Prompt cache usage was 19,708 hit tokens / 30,157 miss tokens, a 39.52% hit rate.

| Arm | n | Direct @1 | @3 | @5 | @10 | @20 | @50 | MRR@50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S0 | 24 | 15 | 20 | 21 | 22 | 23 | 23 | 0.7405 |
| S1 | 24 | 19 | 21 | 23 | 23 | 23 | 23 | 0.8542 |
| S2 | 24 | 18 | 20 | 23 | 23 | 23 | 23 | 0.8229 |
| S3 | 24 | 19 | 21 | 23 | 23 | 23 | 23 | 0.8542 |

S3–S0 Direct Recall@5 is **+2/24 = +8.33 percentage points**. S0's 87.5% baseline leaves only 12.5 points of headroom, so the registered ceiling fallback applies. First canonical sufficient rank improved in 5/24 cells, tied in 19/24, worsened in 0/24; the improved cells span five qids (186, 311, 435, 546, 177). This is below the fallback requirement of improvement in at least half the cells. The full S1 gate is **not met**. S1 candidate grounding alone gave 5 improvements and no regressions; S2 relative to S1 had one rank regression and no improvements, while S3 repaired that regression and improved two ranks relative to S2. There is no evidence here that adding the second and third facts systematically helps beyond candidate grounding.

The registered canonical gain overstates actual evidence gain for q186: S0 top3 already contained an unregistered page that explicitly answered its episode Gap. With that post-retrieval alternative considered descriptively, q435 C01 is the only clean top5 rescue identified in the two apparent canonical rescues. The frozen primary counts remain as above; see [SOURCE_AUDIT.md](SOURCE_AUDIT.md).

## Query mechanism and strata

Candidate-name inclusion rose from 15/24 S0 queries to 24/24 S1/S3 queries. In the C stratum, where the fixed Gap usually did not name the candidate, it rose from 1/8 to 8/8. The lexical raw-question clue-load diagnostic fell from 0.1841 to 0.0729 overall (C: 0.345 to 0.071). Relation-anchor coverage was already 23/24 under S0 and 24/24 under S3. Mean query length fell from 11.67 to 9.58 words. These are mechanical measurements with the definitions and per-query values in `QUERY_ANALYSIS.json`; they establish wording change, not better evidence by themselves.

The case-type ceiling is material. B had S0 Direct@5 7/8 and S3 8/8, but B06 already had an alternative answer source at S0 rank 3. C rose from 6/8 to 7/8, entirely due to q435 C01; C12 remained below top50. D was 8/8 in both arms. q186 B06's canonical rank improved 13→1 through the longer game name. q435 C01 improved 9→4 when Oliver Mtukudzi was named. q546 C11 improved 3→1 and q177 D03 2→1 without changing their top5 success. q1094 B04 stayed rank 4 and C12 stayed >50. The full paired table and actual queries are in `CASE_ANALYSIS.md`.

Frozen ProgressHit@5 was identical to DirectHit@5 for every main arm, so there was no observed early bridge-only top5 success to convert in this static test. The bridge labels also have an audit limitation described in `SOURCE_AUDIT.md`; no closed-loop inference follows from them.

## Gate and interpretation

The mechanism-direction and control checks passed, but the primary direct-retrieval gate did not. The two canonical top5 rescues came from two qids, and one was already answerable through another retrieved source. This is not a robust 12–16-cell cohort of premature downstream Gaps for S2, nor a successful S1 basis for S3. Both stages therefore stop at their prescribed gates. The result supports candidate grounding as a query-shaping mechanism in some cells, while leaving general State sufficiency and automatic State admission unproven.
