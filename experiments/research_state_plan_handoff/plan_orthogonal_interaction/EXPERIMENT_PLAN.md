# P2: receding-horizon broad plan × Search harness

The four checkpoint IDs and their order come only from the historical
DeepSeek M3 `SELECTION.json`. P0 is unchanged v3a Search; P1 is unchanged
Orthogonal Search. The historical no-plan M3 P0/P1 cells are H0 and are not
resampled. For each checkpoint, one new H1 continuation runs in each harness
arm for at most four Actor decisions. Tools remain search/find/open in both.

At decision 1, the historical no-tool M1 broad plan on that exact prefix is
reused as the Planner result. At later decisions, the Planner receives the
current real history plus the original no-tool M1 diagnostic instruction and
produces a new broad plan. This is a receding-horizon card, not a fixed plan
repeated for four decisions. The Actor receives only the latest card appended
to current history, never prior cards or Planner internal output. The card
is omitted from subsequent history while the Actor response and real tool
observations are retained. Every Planner/Actor response and failure is logged.

The primary interaction contrasts P1H0 versus P1H1 next-decision Inspect
(Find/Open) after a no-gain Search. Count no-gain Search responses and
decision transitions explicitly; a parallel call in the same batch cannot
react to that batch's observation. Report plan realization, actual D# source
compatibility, useful evidence, invalid batches, natural stops, and Search
persistence separately. One run per cell; no selective retry.
