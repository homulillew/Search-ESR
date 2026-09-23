# Stage B: Closure → Frontier

Stage A passed before these eight one-per-qid clean Progress Views were frozen at commit `c9d31a8`. The Stage B freeze/gate checks pass. DeepSeek returned all eight single responses with no API errors, tools, retries or repairs.

All **8/8** selected G# values belonged to the pre-call acceptable ActiveGap sets. Closed-gap reselection was **0/8**. Source type was compatible with the selected gap in **8/8** reviewer checks; all eight known-source handles existed or were `none`, and the reviewer judged the chosen handle/none reasonable. The low-ambiguity subset was **6/6** acceptable with no closed-gap or premature choice.

There was **1/8 premature downstream narrowing**. In qid `1094`, the selected G3 (find a fixture connecting the split-founded club, opponent and goal chronology) was acceptable, but the explanation narrowed the unverified opponent to an **Inter–Milan fixture**. The current prefix supports an Inter founding split and a separate PSG–Lille late kick; it does not identify that Inter–Milan match. `frontier_387` also used the unsupported phrase “PC-storage answer” in its rationale, without changing its G2 selection. Both are preserved in raw events and `semantic_scores.json`; a correct G# alone does not certify the entire reason.

The preregistered gate passes: acceptable 100% ≥75%, closed reselection 0% ≤10%, premature downstream 12.5% ≤15%. This is a reviewer-authored clean state upper bound on eight qids, not a test of the model building the closure table or a live long-history planner. The four options per case made the task constrained. The model chose G2 in every case except `1094` G3, which limits evidence about choosing among multiple equally acceptable gaps. DeepSeek reported zero cache-hit tokens and 3,916 miss tokens across all eight responses.

Stage C may now test whether the selected progress information maps to Search, Find, Open, Verify and Submit, with the free Verify arm kept separate from semantic verification capability.
