# Stage D: One-step useful evidence gain

The eight cases were selected before Stage C calls and remained fixed. The Stage D pre-call freeze names commit `f212a78`; its offline gate passed 8/8 checks. A first launch failed **before any case** because the retriever did not fit available GPU memory. `setup_failure.json` records that event. The same frozen runner then completed with `BCPLUS_DEVICE=cpu`; this uses the existing index, model and backend code but changes the retriever's device-dependent precision from GPU float16 to CPU float32. No case was replaced or retried. All seven retrieval calls and three semantic Verify calls completed without error.

The free Actor's already frozen Stage C-B first action was executed once per case. The nominal 2/2/2/2 Search/Find/Open/Verify selection became **2 Search, 2 Find, 3 Open, 1 Verify**, because one closure case chose Open. One Find response had two calls; only its first call was executed under the frozen one-step rule. No new Actor call or post-observation action occurred.

| Executed retrieval | Suitable source | Useful new evidence | Local gap progress |
| --- | ---: | ---: | ---: |
| Search | 1/2 | 1/2 | 1/2 |
| Find | 2/2 | 1/2 | 1/2 |
| Open | 3/3 | 2/3 | 2/3 |
| **All** | **6/7** | **4/7** | **4/7** |

The additional closure-case Open had a suitable existing source but returned `document_complete` with the already observed W13 text. Excluding that redundant action, the six nominal Search/Find/Open cases yielded suitable sources **5/6** and useful evidence **4/6**. These counts are local task outcomes, not full-question accuracy.

Specific observations:

- Search for the snooker match sequence returned only old D11 metadata plus new biography/2025-event previews, giving no new sequence evidence. Search for Lille name history returned new D43, whose preview directly states the Lille club mergers; it narrowed that gap without proving the whole fixture hypothesis.
- Find in D17 returned W32 with Ding's 2003 professional start and century/maximum-break totals. Find in the suitable D11 tournament table returned W19 at the final rather than the requested 4-0 match. The latter is one RP9 local query/window miss. The unexecuted second Find call is not counted.
- Open after W38 returned W49 with later PSG–Lille scoring context and a 94:25 Messi free kick; this is useful for the *candidate fixture* but does not settle the unverified club-identity condition. Open around W14 returned W19 with neighboring dated tournament rows, including a local 4-0 result. Neither observation establishes the full original multi-hop answer.

The frozen two closure claims were both supported by their existing W excerpts. V0 free Actor called Verify for **1/2** and obtained **1/2** correct local closures, while its other action was one redundant Open. V1 harness-triggered Verify called for **2/2** and returned **2/2** correct local closures, with no additional corpus retrieval. Where both arms ran Verify on W42, both returned supported with the correct ref. This two-case comparison demonstrates an invocation gap; it is too small to estimate a population effect.

The two Find records, including ActiveGap, target D, exact query, returned W and yield, are in `results.json`. One of two Find calls failed to yield evidence. The contingent localizer study requires repeated misses plus a separate full-document audit, so its trigger is not met here. The seven retrieval cells derive from only qids 546 and 1094, with multiple related checkpoints. DeepSeek reported verifier cache hits/misses of 256/1,285 prompt tokens (weighted hit rate 16.61%).
