# Unified Global Retrieval protocol

For each newly opened semantic Gap, test document routing by one full-corpus Orthogonal Search (top five), followed only if the preregistered U1 gate passes by Find in the selected document. Search selects documents; Find selects windows. Historical D/W are private evaluator data and are never supplied to the Query Writer.

## U1 bank and comparison

Forty diagnostic cells from genuine BC+ documents and frozen historical observations: 12 A, 8 B, 12 C, 8 D, covering at least ten qids. A is a previously observed but uncommitted fact; B is a previously discovered document with required evidence outside its observed W; C requires a new document; D has a related but insufficient old document. A cell is a checkpoint plus a distinct semantic Gap. Multiple cells per qid or document are correlated and cannot be treated as independent trials. Diagnostic one-window checkpoints are reconstructed historical observation prefixes, not complete trajectories. Their candidate set H contains precisely the observed document at that checkpoint; this limits H's external validity.

Before any model call, freeze all inputs and private truth, source content verification, hashes, case order, and this protocol. DeepSeek `deepseek-flash`, zero retries, one query-writing call per cell. No invalid JSON repair or query rewriting. Freeze all returned queries, including failures, before retrieval.

G searches the unchanged 100,195-document FAISS IP index at k=5. H embeds the same query once and scores only the historical candidate docids with the same cosine inner product. H is a diagnostic candidate-set restriction, not a deployed tool. Both arms share exact query embedding and scoring; no Find in U1. Report recall@1/3/5, MRR, type-specific old/new recall, Type D rank competition, and seen/unseen composition. Invalid calls count as misses. Interpret qid clusters and repeated target documents explicitly.

Pure G advances only if A/B old-source recall@5 ≥90%, C/D new-source recall@5 ≥85%, overall sufficient-document recall@5 ≥88%, and no qid with at least two cells has zero recall. If G old <90% and H old ≥90%, run U1b; otherwise stop. If old is good but new is poor, stop. U1b uses full corpus G plus a frozen deterministic rank prior from H, `1/(60+rank_G)+0.95/(60+rank_H)`; unreturned ranks contribute zero. The constant 0.95 lets a first-ranked historical document compete for fifth place without automatically displacing the first-ranked global document. U1b advances only with ≥10 percentage point A/B gain, ≤5 point C/D loss, and no worse D escape.

## U2 and U3 boundaries

U2 only if U1 or U1b passes. Reuse frozen queries. Independently Find top1 and top2, maximum parallel tools two, with the existing Find backend. Review every returned W for useful and fully sufficient evidence. Gate: A≥85%, B≥85%, C≥75%, overall useful-window hit≥80%. Top2 is selected only if its hit rate improves by at least ten points and its useful-evidence-per-tool-call decrease is at most five percentage points, frozen here.

U3 only if U2 passes: 8–10 qids including 387, 517, 435, 177, 580, 1094, 546; two retrieval decisions per Gap (Search then frozen Find policy). No Claim policy changes or final-answer accuracy claim. Unrun stages receive a `NOT_RUN.md` explaining the gate.

All failed calls and raw responses are preserved. No retries, best-of, prompt repair, source-title hints, backend modification, hard action gates, or history-based scope router.
