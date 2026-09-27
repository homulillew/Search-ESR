# E1 development result

## Material Passport

10 exposed unique questions; 60 planned/sent/returned; DeepSeek deepseek-flash;
single Codex semantic reviewer, first pass committed at f598e02 before unmask.

| Arm | Strict | Material coverage (macro) | RelationErr | RoleErr | TemporalErr | Dependency recall | Severe broad | Stability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D0 | 18/20 (90%) | 97.78% | 1/20 (5%) | 0 | 0 | 100% | 0 | 8/10 (80%) |
| D1 | 20/20 (100%) | 100% | 0 | 0 | 0 | 100% | 0 | 10/10 (100%) |
| D2 | 20/20 (100%) | 100% | 0 | 0 | 0 | 100% | 0 | 10/10 (100%) |

D2 primary gate and mechanism comparison gate PASS. Comparison uses the
registered absolute corruption ≤5% alternative; observed reduction is 5pp,
not the alternative 10pp improvement. Coverage does not decline. E2 is eligible.

D0 R017/Q1259 changes two teammates sharing a country into sharing country
with the Australian coder; critical relation corruption and invented equality.
D0 R050/Q922 broadens original recipient wording to another party; frozen
reference scores partial critical coverage. This judgment has high ambiguity;
accepting that ellipsis would raise D0 strict to 19/20 and stability to 9/10,
without altering D2 or E1 gate. No semantic-label changes were made.

D1 and D2 match on strict/fidelity; no demonstrated D2 advantage over D1.
All 60 schema-valid; all 40 anchored outputs exact-span-valid. D1 node-level
anchors support their prose in original-Q context; short anaphoric excerpts
are not certified standalone. No harmful merges/splits in primary review.
Q228 D2 coarse founder grouping is a recorded borderline case, accepted under
coherent referent guidance. Alternative valid splits are explicitly permitted.

This is question semantics, a different task from choosing one next obligation
from current Claims. The high scores cannot be interpreted as a 40–50pp causal
improvement over historical Dynamic-O. No downstream control benefit tested.
