# Variable-Preserving Research State: final conclusion

## Decision

V1 supports **Explicit Unknown → less unsupported persistent binding** on the
frozen 30-case bank. V2 does **not** support the next link, **less unsupported
binding → materially less confirmatory query bias**. The V2 gate failed, so
V3 Evidence-to-Binding and V4 Actor causal probe were not run. Do not promote
TestCard into the formal Harness or launch a rollout from this branch.

| Measure | C0 Claim | C1 natural TestCard | C2 provenance TestCard |
| --- | ---: | ---: | ---: |
| V1 cases | 30 | 30 | 30 |
| Premature specificity or failed cell | 30/30 | 2/30 | 1/30 |
| Unsupported reviewed bindings | 65/66 | 1/218 | 1/124 |
| Mean requirement coverage | 0.0% | 94.4% | 98.9% |
| Item testability | 97.1% | 98.1% | 100% |
| Unknown preservation | 67.4% | 96.7% | 98.3% |
| Mean claims/tests | 2.20 | 1.77 | 1.47 |
| Mean known / unknown fields | 0 / 0 | 7.27 / 5.70 | 4.10 / 2.97 |
| Mean completion tokens / latency | 8,243 / 35.0 s | 6,503 / 28.7 s | 8,101 / 35.4 s |
| Failed cells | 2 | 1 | 0 |

The C0 binding denominator is proposition-level; C1/C2 denominators are
known-field-level. Compare those rates cautiously. C0 coverage uses the frozen
strict rule that an unsupported answer assertion is not itself a supported
test path. The paired premature-case comparison is more comparable: 28 C1
and 29 C2 cases improved versus C0, with zero reverse worsenings. One C1
failure was an interrupted in-flight request, never retried; two C0 calls
ended with abnormal length. Among received V1 responses, no schema error
occurred. These 30 cells are correlated siblings from 11 questions and were
reviewed by one prefix-only reviewer; no population significance is claimed.

| V2 one-query measure | Q0 Gap only | Q1 Claim | Q2 natural TestCard |
| --- | ---: | ---: | ---: |
| Unsupported exact-value leakage | 7/16 | 9/16 | 7/16 |
| Confirmation-biased query | 7/16 | 8/16 | 7/16 |
| Gap alignment | 14/16 | 15/16 | 15/16 |
| Expected source-type alignment | 15/16 | 16/16 | 16/16 |
| Unknown targeting | 14/16 | 15/16 | 15/16 |
| Mean completion tokens / latency | 5,211 / 24.2 s | 5,314 / 24.1 s | 6,508 / 30.0 s |

Q2 versus Q1 reduced leakage in 3 paired cases and increased it in 1 (net
2), below the frozen net-6 gate. Even treating the two borderline exact
club/team-name labels differently cannot bridge that gap. All 48 V2 calls
returned valid JSON. Query examples show why the gate matters: `Jazz
Jackrabbit`, `You're the Worst`, named snooker opponents and `Oliver Mtukudzi`
for a prefix whose explicit H was Miriam Makeba appeared across arms. The
TestCard's own unknown fields did not consistently prevent the query actor
from adding parameter-memory candidates. V2 did not execute Search, so no
retrieval yield or answer correctness is inferred.

## Required questions

1. **C0 replication:** Yes in the sense of the pre-registered prefix-only
   rubric: all 28 valid C0 cells asserted at least one unresolved relation or
   exact value as a factual Claim, plus two retained failures. This is a new
   normalized, contemporaneous probe, not a replication of the old 18/37
   frequency estimate.
2. **Natural TestCard and unsupported binding:** Yes at the representation
   level. C1 had one unsupported relation among 218 reviewed fields and one
   interrupted failure; 28 paired cases improved against C0. Its substantive
   error conflated an observed publisher with the unverified developer.
3. **Extra provenance benefit:** Small and insufficient under the frozen rule.
   C2 turned observed `Dust: An Elysian Tail` into unobserved Game B in one of
   124 reviewed bindings,
   no failed cell, and 98.3% unknown preservation versus C1's 96.7%. It did
   not reach the required 5-point binding-rate, two-failure, or 10-point
   unknown-preservation advantage.
4. **Representation choice:** C1. It is simpler and averaged 6,503 completion
   tokens and 28.7 seconds, versus C2's 8,101 and 35.4 seconds. This is the
   V1/V2 diagnostic choice, not an approval for persistent Harness state.
5. **Coverage:** C1 94.4%; C2 98.9%, both above the 70% gate. The main C1/C2
   coverage miss was omitting a check of the program's Argentine release name.
6. **Burden:** C2 cost about 25% more completion tokens and 23% more latency
   than C1 in V1 without material quality gain. There were no received-response
   schema failures; one C1 call failed to complete because the process was
   interrupted. Q2 also cost more tokens/latency than Q1 in V2.
7. **Does explicit unknown change query?** Occasionally, but not enough:
   3 improvements, 1 worsening, net 2; the gate required net 6. Q2 leakage
   equaled Q0 at 7/16.
8. **Concrete Claim confirmation bias:** Q1 was 8/16 versus Q2 7/16 and Q0
   7/16. This descriptive one-case difference does not establish a robust
   mechanism.
9. **Unknown-targeting:** Q2 and Q1 were both 15/16; Q0 was 14/16. Natural
   TestCard did not uniquely improve it.
10. **Binder precision:** Unmeasured. V3 was stopped by the V2 gate.
11. **No-Evidence unknown preservation online:** Unmeasured; V1 measures only
    static representation, not update behavior.
12. **Conflict recovery:** Unmeasured; no binder/verifier calls were made.
13. **Effect of explicit provisional H:** Not isolated. All relevant arms saw
    the same provisional H. In one query case the actor switched from the
    supplied Miriam hypothesis to Oliver based on information absent from the
    prefix; provisional labeling alone was insufficient there.
14. **SemanticGap versus acquisition wording:** Not isolated. All three arms
    used the same normalized SemanticGap. It removed a known confound but
    cannot by itself explain the V1 differences.
15. **Actor action benefit:** Unmeasured. V2 measured one query string only;
    V4 was not run, and no Search/Find/Open action occurred.
16. **Current bottleneck:** In the observed chain, query generation or use of
    Test state is the immediate bottleneck: clean unknown fields did not
    reliably constrain the next query. Source retrieval, localizer, online
    Evidence Binding and action choice were not tested here; no ranking among
    those downstream components is justified. V1 also retained a small
    semantic Test generation error rate.
17. **Short rollout:** No. The query-control link failed, so a 4–8 decision
    rollout would be premature in this branch.
18. **ESR-GRPO:** Do not enter. The causal chain through query and binding is
    not established.
19. **Hard Search/Find/Open gating:** Still prohibited. The study provides no
    evidence for safe hard action masks.

## Failure taxonomy and next research question

V1 directly observed VP1 unsupported binding and VP2 evidence/hypothesis
promotion. V2 observed VP11 confirmation-biased queries, including in Q2
after a clean TestCard. VP3 and VP4 were controlled by normalizing the Gap and
making provisional H explicit. VP5 occurred in the program-release-name
cases. VP6 appeared as overextended tests; VP7/VP8 were rare under this
review. VP9/VP10 (binding updates) and VP12 (Actor ignoring state in action
choice) remain untested.

The next useful diagnostic is a separate **query actor intervention**: hold
the same prefix and TestCard fixed while testing whether an explicit
query-generation constraint can distinguish a temporary search hypothesis
from a value written into persistent state. It requires a new protocol and
freeze. The current branch establishes the first link only:

`Explicit Unknown → Less Unsupported Binding`.

It does not establish:

`Less Unsupported Binding → Less Confirmatory Query Bias → Safe Evidence Binding`.

The persistent state rule remains: a concrete value can be committed only
from a question anchor, observed evidence, or an explicit provisional H at
its stated status. A temporary query guess is not a persistent binding.
