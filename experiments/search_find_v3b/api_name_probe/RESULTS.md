# Final tool-name alias probe result

The four frozen S2 checkpoint comparisons have one complete alias
continuation each. Before paid calls, the original gate passed **31/31**.
The user interrupted the running process after two completed cells and part
of the third. The partial `1094:77:AL` attempt remains in `events.jsonl` with
an explicit interruption event. `RESUME_AFTER_INTERRUPTION.md` and
`freeze_resume.json` document a mechanically selected completion of the two
unfinished cells; its pre-call gate passed **10/10** and events are in
`events_resume.jsonl`. The partial attempt is excluded from outcome counts.
No completed cell was rerun or selected by outcome.

Across the four complete alias cells, the provider returned **28 Global
`search` calls**, **one `open`**, and **zero `search_document` calls**. qid
546 seq9 stopped after two Searches and an Open; qid 1094 seq69, seq77 and
seq93 each used the four-decision horizon with Search only. There were no
undeclared calls, malformed arguments, tool errors or API failures in the
four complete cells. Global Search still discovered **14 new documents** and
returned **126 old-document hits**. The original S2 comparison had Find in
2/4 cells (none useful); this alias arm had valid local action in **0/4**,
new local windows **0**, useful local evidence **0**. It used **928,670**
prompt tokens and **968,489** total tokens, compared with S2's **970,518**
and **1,030,088** in the same four selected prefixes. Workload and stopping
differences prevent a per-decision efficiency interpretation.

Unlike the scoped arm, this probe preserved Find's exact `(doc_ref, query)`
argument schema and backend. The alias was declared and coherent in the
model-facing prompt. The observed result offers **no support** for the
claim that changing `find` to `search_document` makes this model use local
verification. A single sample per checkpoint cannot prove a zero effect,
and this name change also mechanically changes prompt and descriptions, but
there is no positive evidence that warrants further API variants or a
10–20-question cohort.

The combined evidence is bounded: the earlier scoped interface had a
different failure, 27 missing-scope argument calls; this alias had valid
syntax but was not selected. The `search` action pattern is persistent,
yet a simple local name change did not solve it. This is the planned stop
point for the Search–Find branch.
