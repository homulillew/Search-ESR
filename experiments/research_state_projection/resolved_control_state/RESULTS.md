# S1: single resolved control card, paired one-step comparison

The freeze was written after commit `e666537` and before any S1 call. `gate.txt` passes all seven checks. All 13 frozen R1 checkpoints received one contemporaneous B response (the exact Broad Plan + Qualification request) and one C response (the same original prefix + one resolved card). Arm order alternated. All 26 responses were valid; there were zero API errors, retries or tool executions. The 71 proposed tool calls were scored individually using only the checkpoint prefix, frozen projection and tool arguments. `semantic_scores.tsv` contains each manual judgment and reason; `semantic_scores.json` is the machine-readable copy.

| Measure | B: appended cards | C: single resolved card |
| --- | ---: | ---: |
| Direct gap action, at least one per checkpoint | 6/13 | 8/13 |
| Direct or partial gap action, at least one | 11/13 | 11/13 |
| Direct gap action, first call | 3/13 | 6/13 |
| Direct gap calls | 8/38 | 9/33 |
| Direct or partial gap calls | 22/38 | 22/33 |
| Repeats already supported fact | 2/38 | 0/33 |
| Unpromoted candidate inspected, `hypothesis_only` | 2/7 | 1/7 |
| Promoted target used, `inspectable` | 3/4 | 4/4 |
| Search / Find / Open calls | 28 / 8 / 2 | 22 / 10 / 1 |
| Search calls directly addressing gap | 5/28 | 4/22 |
| Search calls directly or partially addressing gap | 16/28 | 16/22 |

The direct-gap checkpoint change is four improvements (`546:17`, `1094:45`, `1094:53`, `1094:61`) and two regressions (`1094:34`, `1094:77`), for a **net two**. At `546:25`, B's Open(W13) revisits a visible opening-win report, while C searches for the later bracket; both arms also have at least one gap-directed call. At `1094:45`, C still Finds the unpromoted D34, but asks for the proposed fixture's goal timeline; this is a possible gap test, not proof of confirmation bias. At `1094:93`, C Opens W74 and Finds D53, an observed academy-team article unrelated to the proposed fixture. C therefore retains concrete source-routing errors despite improvements elsewhere.

## Frozen success gate

| Condition | Observed paired change | Decision |
| --- | --- | --- |
| A: at least two `hypothesis_only` checkpoints reduce unpromoted candidate inspection, fewer than two reverse | One reduction (`546:25`), zero reversals | **Fail** |
| B: no net loss in promoted target use | One gain (`1094:61`), zero losses | Pass |
| C: at least two net gains in direct gap alignment | Four gains, two losses, net two | Pass under the frozen single-reviewer rubric |
| D: gain is not generic Search-only behavior | C has six fewer Searches; 16 gap-relevant Searches in each arm; gained cells include targeted Find | Pass |

The conjunction fails because **A fails**. S1b, S2 and S3 are therefore stopped under the preregistered rule. The 2/7 → 1/7 descriptive reduction is only one paired change and does not isolate the effect of candidate-name salience: B and C also differ in Plan removal, card structure and gap/source wording. B/C are single samples on 13 checkpoints from two original questions; the semantic categories are one reviewer's query-intent judgments, and no returned evidence was observed. Inspection Precision and Evidence Yield cannot be calculated here.

## Provider cache telemetry

DeepSeek reported prompt-cache usage for all 26 responses. The token-weighted hit rate was 472,060 / 474,620 = **99.46%** for B and 468,864 / 472,672 = **99.19%** for C. `CACHE_USAGE.json` preserves each response's reported hit and miss counts. These rates describe provider telemetry; they are not an outcome measure of the research-state intervention.
