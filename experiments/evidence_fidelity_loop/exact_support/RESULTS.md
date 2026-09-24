# E2 Exact Support Verification result

The stage-specific pre-call freeze contains all 46 actual E1-P Findings and 22 authentic-W stress candidates across ten qids. V0 and V1 received identical inputs and separate frozen prompts. All 136 DeepSeek responses were retained; there were no API errors, retries, or repaired outputs. `events.jsonl` holds exact requests and responses; `REVIEWS.json` holds the independent semantic review of every V1 pointer.

| Measure | V0 whole packet | V1 with mechanical Harness rules |
|---|---:|---:|
| Source-support precision | 50/51 = 98.0% | 46/47 = 97.9% |
| Exact-pointer sufficiency among mechanically accepted | — | 45/47 = 95.7% |
| Source-support recall | 50/52 = 96.2% | 46/52 = 88.5% |
| Stress negatives rejected (S1–S4) | 15/16 | 15/16 |
| Full Claim-eligibility precision, descriptive | 46/51 = 90.2% | 42/47 = 89.4% |
| Mechanical pointer validity among V1 `supported` | — | 47/51 = 92.2% |
| Offline reviewer filtered acceptance, diagnostic only | — | 45/45 precision, 45/52 recall |

V0 falsely accepted one temporal join: the retrospective's “67 albums later” appears beside a quoted 2016 Forbes Africa interview, but does not establish that Mtukudzi had 67 albums *at the time of that interview*. V1 also returned `supported` with a **mechanically valid** pointer to that ambiguous sentence. The offline reviewer identified the missing temporal binding, but the Harness performs no semantic judgment and would still commit it. Thus V1 did **not** operationally reduce this false accept. The other S1–S4 stress negatives were rejected by both arms. V0 had only one clear false accept, below the frozen five-error superiority trigger.

V1 lost four genuinely source-supported positives because it listed `date` in `source_metadata_used`, whose frozen allowlist is only `title` and `url`. The dates are present in W text and could have been pointed to as spans; the outputs are still mechanically invalid under the frozen schema. Six additional V1 `insufficient` outputs incorrectly retained nonempty metadata lists. One mechanically valid positive pointer pointed only to “Nzioki” and “his mother” while claiming the full `Peter King Nzioki` identity, so semantic review rejected it. Two q517 full-name cases were rejected outright by both verifiers; `LABEL_SENSITIVITY.md` documents why their frozen positive truth is debatable.

The frozen E2 offline-review-filtered gate **fails** on recall (86.5% < 90%) and pointer validity (92.2% < 98%). More importantly, under the specified mechanical Harness behavior, exact-pointer sufficiency is only 45/47 (95.7%, below the 97% Claim precision threshold), source recall is 46/52 (88.5%), and temporal false acceptance is 1/4 (25%, above 5%). Six V1 `insufficient` outputs also violated the empty-metadata schema, though they were rejected. Even if the two q517 labels were corrected in a post-call sensitivity analysis, pointer validity still fails. Therefore E3, runner changes, and F3b remain unrun. Exact pointers exposed an unsupported temporal join to the **reviewer** but did not stop the mechanically valid false Claim; the current offset/metadata interface is not reliable enough for admission.

Provider telemetry: 17,152 prompt cache-hit tokens and 91,684 prompt cache-miss tokens across E2 calls (15.8% hit share of these two fields).
