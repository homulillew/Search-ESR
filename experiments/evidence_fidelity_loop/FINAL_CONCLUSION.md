# Evidence Fidelity: gated conclusion after E2

E1 used 44 historical observations across 12 qids and 88 paired DeepSeek calls. Its frozen review credited the full packet with three identity/time recoveries, 46/46 complete source support, and 35/37 required-finding recall. It also found four source-supported but off-Gap/redundant findings, so our stricter local combined precision gate failed at 42/46. The user then authorized a prospective E2 diagnostic under the original task's separate source-support precision definition. The E1 local failure and all its raw records remain unchanged; the interpretation amendment was recorded before E2 calls.

E2 tested all 46 actual E1-P Findings plus 22 genuine-W stress candidates in 136 new single calls. Both V0 and V1 accepted one false temporal join. V1's exact pointer made the missing time relation visible to an offline reviewer, but the pointer passed mechanical checks and the Harness would still commit it. Under mechanical Harness behavior, V1 source recall was 46/52 (88.5%, required ≥90%), exact-pointer sufficiency was 45/47 (95.7%, below the 97% Claim precision threshold), temporal false acceptance was 1/4 (25%, required ≤5%), and pointer validity was 47/51 (92.2%, required ≥98%). The frozen *offline-review-filtered* gate also fails, with recall 45/52. Four otherwise useful positive outputs misused the prohibited `date` metadata field. A separate q517 audit challenges E1's positive full-name label: `Peter Nzioki` as a title plus a filmography row does not itself establish the extra `King` alias. Frozen labels are preserved; this challenge is a sensitivity analysis. E3 and F3b did not run.

## Answers to the 22 research questions

| # | Conclusion from this branch |
|---:|---|
| 1 | Yes for the Forbes Africa source and 2014 Rangers table. The Peter King alias case is disputed after E2 review. |
| 2 | Frozen E1 labels give P 3/3 versus T 0/3; the robust signal is 2 clear fixes and one disputed identity fix. The M2/M3 denominator is tiny. |
| 3 | E1's frozen review marked no metadata overreach, but E2 exposed a plausible q517 alias overbind; four P findings were also off-Gap/redundant. Four V1 outputs misused `date` as an allowed metadata field. |
| 4 | Yes in one targeted temporal stress case: V0 accepted the unsupported “67 albums at the 2016 interview” join. The other 15 stress negatives were rejected. |
| 5 | V1 did **not** reduce the false temporal binding operationally: it accepted the same join with a mechanically valid pointer. An offline reviewer caught it. Identity and sequence had no V0 false accepts to improve. |
| 6 | Exact spans made one false relation auditable, but did not automatically prevent it. Requiring them for all Claims is premature with this pointer interface: only 47/51 raw `supported` outputs were mechanically valid. |
| 7 | Match results, biography details, and episode plot facts can be established by W text. Rangers' 2014 year needed its title; direct Forbes Africa source identity needed its URL. The q517 full `Peter King Nzioki` alias needs additional observed evidence beyond a `Peter Nzioki` title and filmography row. |
| 8 | Not tested; E3 was gated out. |
| 9 | Not tested; no `missing`-field experiment ran. |
| 10 | Not tested; pending-W-first rollout was gated out. |
| 11 | Not tested in a new runner; duplicate `(Gap,W)` handling remains open. |
| 12 | Not tested; immediate-stop runner was not changed. |
| 13 | Not tested; no new Useful-W-to-Valid-Claim conversion rate exists. |
| 14 | Not tested; no Group A paired rollout occurred. |
| 15 | Not tested in F3b. Historical retrieval-limited q546 and q1094 remain useful controls, but query/source/localizer attribution is not resolved here. |
| 16 | Packet truncation is a local mechanism and exact-pointer schema reliability is now an observed bottleneck. The main end-to-end bottleneck cannot be ranked against source acquisition, query generation, or localizer without E3–F3b. |
| 17 | The minimal Question–Claims–Gap–optional-Hypothesis state remains compatible with these results; sufficiency has not been proven by rollout. |
| 18 | No result calls for a persistent TestCard graph. |
| 19 | No. This gated branch gives no basis to enter multi-Gap Frontier. |
| 20 | No. It gives no basis for a longer rollout. |
| 21 | Yes: there is still insufficient evidence to start ESR-GRPO. |
| 22 | Yes: keep hard Search/Find/Open gating prohibited. |

## Interpretation and next admissible step

The full packet recovered two clear source/time bindings and one disputed actor alias while increasing tangential extraction. Exact pointers made one false temporal join inspectable to a reviewer, but the mechanically valid false pointer would still be committed; the current allowlist/offset interface also lost too many true Findings. The E2 freeze stops this branch before testing Gap closure or runner effects. A future E2b would need a *new* pre-call protocol that explicitly distinguishes date text in W from `title/url` metadata and requires complete actor-identity support; none of this study's outputs or labels should be replaced. No historical experiment result or backend was rewritten.
