# Authorized H1/H2 continuation

Standing user authorization: `授权，后续你自己直接调用就行了不用我授权`.
All stages were frozen before calls and executed within their individual budgets,
with dependency-safe parallel API requests and max_retries=0. No further approval
was requested. Historical repair and run001 results remain unchanged.

| Stage | Calls | Peak parallel | Wall time | Cache hit rate | Outcome |
|---|---:|---:|---:|---:|---|
| H1, six reused prefixes ×2 | 93 | 12 | 300.03s | 29.87% | Interface gate passed; one retained Closure schema error |
| H2, eleven repair-held-out archived prefixes | 81 | 11 | 133.61s | 22.75% | Recovery signals, but unsupported temporal C; do not expand |

Total174 calls,406,169 input tokens,535,319 output tokens,941,488 total tokens;
108,158 cache-hit tokens and298,011 misses. Weighted cache hit rate **26.6288%**;
all174 usage records complete and consistent. No provider/HTTP failures, no
automatic retries, no replaced samples. Two non-H model schema-wrapper failures
were retained, one per stage. GPU0 retrieval was serialized and overlapped with
API work; GPU1's unrelated workload was untouched.

## What was established

- Repaired H interface:44/44 live H proposals valid;7 calls mechanically skipped.
  No H failure occurred live, so live failure-isolation effectiveness has no
  denominator. Earlier offline twelve-output replay proves the injected-failure
  continuation path;146 regression tests passed before H2.
- H1 factual boundary:14/14 new C supported. R1 NoGain reached the next Actor4/4;
  both q637 paths used DEPRIORITIZE rather than global REJECT.
- H2 local recovery:3/3 actual initial NoGain paths reached acquisition and2/3
  obtained gap-useful C. All4 Closure vetoes were followed by gap-directed
  acquisition;3/4 obtained useful C, with one of those also admitting unsupported C.
  One weak candidate was confirmed to a supported READY and final answer.
- H2 factual boundary:11/12 new C source-supported; q435 C5 overbinds a retrospective
  album count to an interview year. This is a strict source-support failure, not
  a gold-verified false number. Mechanical replay cannot catch semantic overreach.
- Wrong-H recovery is still inconclusive: the three eligible R2 H were weak
  candidates, not proven wrong seeds. One case had an Actor format failure.

## Research decision

**Retain the H contract/failure-isolation repair; do not expand the recovery
experiment yet.** The loop can continue, but maintaining a justified factual state
while it continues remains the stronger requirement. Prioritize temporal/relation
support in Grounding; separately diagnose local navigation and schema wrappers.
No runtime/role/tool tuning, new persistent state, hard mask or further live batch
was introduced after these results.

H2's 12/12 compatible-inspection result coexists with 1/12 new-useful-raw-evidence
yield. Appropriate documents, new window IDs, extra H and runtime Gain all fail
as substitutes for actual evidence progress. These small differing cohorts do not
establish a causal effect or end-to-end accuracy.

Reports and frozen raw artifacts:

- [H1 conclusion](h1_contract_continuation/FINAL_CONCLUSION.md)
- [H2 conclusion](h2_independent_recovery/FINAL_CONCLUSION.md)
- [q435 source-support failure](h2_independent_recovery/FAILURE_CASE_Q435.md)
- [H2 gate and metrics](h2_independent_recovery/GATE.json)
