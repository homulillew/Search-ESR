# three_round_loop_v2

{
  "phase": "three_round_loop_v2",
  "max_decisions": 3,
  "max_actions_per_decision": 2,
  "updater": "one call per actual source window, max 2 claims; sequential within each trajectory",
  "failure": "no retry; invalid updater/goal/actor terminates dependent branch as failed; other arms continue",
  "dynamic_requests": "exact context builder below committed before calls; every constructed request journaled before submission",
  "selection": [
    {
      "qid": "546",
      "snapshot_id": "T01_POST"
    },
    {
      "qid": "1094",
      "snapshot_id": "T02_POST"
    },
    {
      "qid": "517",
      "snapshot_id": "T03_POST"
    },
    {
      "qid": "435",
      "snapshot_id": "T19_POST"
    },
    {
      "qid": "580",
      "snapshot_id": "T14_PRE"
    },
    {
      "qid": "177",
      "snapshot_id": "T06_POST"
    },
    {
      "qid": "1034",
      "snapshot_id": "T07_POST"
    },
    {
      "qid": "311",
      "snapshot_id": "T08_POST"
    },
    {
      "qid": "186",
      "snapshot_id": "T09_POST"
    },
    {
      "qid": "387",
      "snapshot_id": "T10_POST"
    }
  ],
  "arms": [
    "L0",
    "L1",
    "L2"
  ],
  "stop": "L2 immediate resolved goal review; all Actor stops independently scored; horizon censoring is not a stop"
}

See root PROTOCOL and REVIEW_RUBRIC. Oracle state is used only in R2 and offline review. Adaptive hypotheses/claims/residuals are never manually repaired.
