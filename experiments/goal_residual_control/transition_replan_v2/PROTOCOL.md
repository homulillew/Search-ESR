# transition_replan_v2

{
  "phase": "transition_replan_v2",
  "max_decisions": 1,
  "max_actions_per_decision": 2,
  "updater": "one call per actual source window, max 2 claims; sequential within each trajectory",
  "failure": "no retry; invalid updater/goal/actor terminates dependent branch as failed; other arms continue",
  "dynamic_requests": "exact context builder below committed before calls; every constructed request journaled before submission",
  "transition_order": [
    "T01",
    "T02",
    "T03",
    "T04",
    "T05",
    "T06",
    "T07",
    "T08",
    "T09",
    "T10",
    "T11",
    "T12",
    "T13",
    "T14",
    "T15",
    "T16",
    "T17",
    "T18",
    "T19",
    "T20"
  ],
  "arms": [
    "R0",
    "R1",
    "R2",
    "R3"
  ]
}

See root PROTOCOL and REVIEW_RUBRIC. Oracle state is used only in R2 and offline review. Adaptive hypotheses/claims/residuals are never manually repaired.
