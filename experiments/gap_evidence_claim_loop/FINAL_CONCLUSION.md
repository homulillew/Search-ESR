# Gap → Evidence → Claim: final conclusion

The stage gates led from 41 historical W transitions (F1), through 53 Claim
proposals (F2), to six paired short rollouts (F3). F1 and F2 passed their
frozen gates. F3 failed: useful raw W increased, but true Claim-based Gap
closure did not, one R1 Claim lacked exact temporal support, and two R1
closures were premature. These are small, single-reviewer mechanism probes,
not a final answer-accuracy cohort.

## Answers to the 21 research questions

1. **Observation-only uptake:** Yes. A emitted 67 Gap-irrelevant facts in 110
   Findings (39.1% overall precision). Many were true facts from the W but
   did not advance its Active Gap.
2. **Gap relevance:** Yes in F1. Adding a semantic Gap reduced irrelevant
   output to 1/46 in B; C produced 0/38. B and C cut 31 and 32 paired
   irrelevant cases against A.
3. **Does Gap manufacture answers?** The frozen F1 review found no unsupported
   inference, but its strict post hoc audit identified one overreach:
   “Season 4 episode 7” was promoted to “midway through the season” without
   a season length. F3 also exposed an unsupported temporal binding. These
   are risks; the design does not identify the Gap as their sole cause.
4. **Existing Claims and duplication:** C removed all four duplicate Finding
   case errors seen under B. The four challenge cells reuse source-supported
   W text, so this is a narrow controlled result.
5. **High-precision Finding extraction:** F1-C scored 38/38 precision and
   29/32 required-atom recall under frozen labels. The stricter audit makes
   precision 37/38 (97.4%) without changing the frozen primary result.
   Dynamic F3 Claim precision fell to 11/12 (91.7%).
6. **NoGain silence:** B and C each returned `findings=[]` in all 8/8 E6
   NoGain cells; A did so in only 2/8.
7. **Multiple useful facts:** C found 29/32 required atoms in F1, so no
   severe aggregate loss there. F3 missed a direct May Forbes Africa W and
   a season-one episode W until it was retrieved again. Dynamic coverage is
   a material weakness.
8. **Relation traps:** F1 did not accept its labelled relation traps, and
   F2-V rejected all 15 stress proposals. F3 still exposed identity binding
   to an unnamed filmography W and a 2016 quote falsely tied to a later
   album count. Avoidance is not robust across a live loop.
9. **Verifier protection:** In F2, V rejected 15/15 negative proposals and
   admitted 37/38 labelled positives; D mechanically admitted every
   proposal. In F3, Verifier admitted one unsupported temporal Claim and
   gave opposite decisions on byte-identical Peter King windows. This
   curated-bank protection did not generalize perfectly.
10. **Minimal Claim record:** `{claim_id, statement, evidence_refs, version}`
    is enough to represent a verified factual belief without open/unknown
    lifecycle fields. F3 shows that field simplicity alone does not ensure
    safe admission, consistency across sources, or closure. Keep the schema
    minimal while admission and reading are repaired.
11. **Gap Reviewer calibration:** It correctly closed both `580` arms once
    the season-one and season-three facts were committed. It closed `435`
    before the required Forbes Africa relation was committed, `177:R1`
    without a committed season year, and `517:R0` on an overbound identity
    Claim. Each arm had 2 premature closes among 3 declared closes.
12. **Useful Evidence/Retrieval:** R1 increased useful W per retrieval action
    from 6/32 (18.8%) to 10/38 (26.3%); actions yielding any useful W rose
    from 4/32 to 6/38. These are descriptive: the paired net +3 drops to +2
    when the interrupted `177:R0` pair is excluded, and the exact pair
    tie-break was specified during analysis.
13. **Active Gap resolution:** No increase. Both arms truly resolved 1/6
    Gaps using committed Claims. More raw evidence did not become more
    completed research states.
14. **Redundant retrieval:** No reduction. Retrievals that produced no new
    W handle rose from 6/32 (R0) to 12/38 (R1). In `580:R1`, the Actor
    repeated a known W before its useful fact was extracted.
15. **Current error location:** Source selection and query formulation
    dominate `546` and much of `1094`; Find/localizer landed on biography
    or unrelated spans in `546`; evidence reading missed direct W in `435`
    and `580` and lost the table year in `177`; Verifier mishandled time in
    `435` and disagreed on identity in `517`; Gap Reviewer closed prematurely.
    These are distinct failures, not one Find problem.
16. **TestCard persistence:** No result here requires a persistent TestCard,
    slot graph or Claim template. A temporary natural-language expansion of
    a complex semantic Gap may still help, but this branch did not test it.
17. **Claim definition:** Use “verified, committed factual belief” as the
    intended definition. Treat a model Finding as temporary until its exact
    source supports every stated identity, date, quantity and relation.
18. **Multi-Gap Frontier:** Not yet. The single-Gap loop failed Claim
    precision and closure gates; more simultaneous Gaps would confound those
    failures.
19. **Longer rollout:** Not yet. First enforce an actual action budget and
    immediate stop, preserve source identity in evidence reading, and test
    Verifier stability and closure fidelity. The current runner executed 11
    queued retrievals after a first resolved verdict.
20. **ESR-GRPO:** No. This branch does not supply a reliable reward or State
    transition target for reinforcement learning.
21. **Hard action gating:** Still prohibited. Search, Find and Open should
    remain available; the observed errors do not justify a hard mask.

## State boundary and next research decision

Persist the original Question, one semantic Active Gap, and only Claims whose
exact observed W supports the full statement. Keep raw observations and D/W
handles in Workspace/WorldLedger. A candidate, an unresolved condition, a
query argument and a verifier's ungrounded inference remain outside
persistent Claim State. Optional Working Hypotheses remain provisional.

The evidence-to-Claim boundary has a stronger signal than the full loop:
Gap conditioning selected more relevant facts, and a separate verifier
blocked all curated negative proposals. The live loop shows the remaining
bottleneck is conversion from useful W to a safe, sufficient Claim and a
calibrated Gap closure. The most informative next diagnostic is one-W source
identity/temporal binding and closure review under a strict one-action
budget. Do not expand Research State fields or begin multi-Gap planning yet.

## Interpretation limits

F1's 41 cells include related observations and four controlled duplicate
probes. F2 negatives were reviewer-authored over authentic W, not a random
runtime distribution. F3 used two exact v3a chat prefixes and four older
checkpoints wrapped as exact W snapshots. R0's long chat and R1's compact
view differ in presentation as well as State. One R0 cell was interrupted
and never retried. The F3 runner executed precommitted calls after first
closure, violating the intended immediate stop. The same single reviewer
also saw live progress before arm-masked W review. Therefore the F3 numbers
identify failure modes and directional evidence yield, not a clean estimate
of the causal effect of persistent State.
