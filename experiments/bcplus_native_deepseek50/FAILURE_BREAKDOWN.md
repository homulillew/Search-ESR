# Failure breakdown

Mechanically identifiable, overlapping post-hoc labels:

{
  "run_or_api_failure": 0,
  "gold_string_not_observed_heuristic": 3,
  "gold_string_observed_but_answer_wrong": 1,
  "search_repetition": 1,
  "document_not_read": 0,
  "very_long_trajectory_gt_50_rounds": 2,
  "emergency_cap_reached": 0,
  "explicit_insufficient_evidence": 2
}

Candidate fixation, premature answer, conflicting evidence, and other causal labels require separate qualitative review. These labels do not change accuracy.

## Four primary incorrect answers

| QID | Outcome | Post-hoc interpretation |
| --- | --- | --- |
| 870 | Said the corpus did not establish the husband; gold was Jim Hibbert. | Likely retrieval miss or failed connection of author and spouse. 56 tool rounds, 93 Searches. |
| 54 | Selected *The Patience Stone*; gold was *China in Ten Words*. | Wrong candidate selection with a stated caveat about unmatched biographical clues. 55 tool rounds, 108 Searches. |
| 875 | Declined to identify the shared name; gold was Kevin Anderson. | Insufficient-evidence answer despite the gold string appearing in an observation. The string observation is only a heuristic and may refer to another context. |
| 763 | Selected Magnolia Grove; gold was the Gingras Trading Post State Historic Site. | Wrong site selection based on partly unverified clues. 41 tool rounds, 117 Searches. |

There were no API/run failures. Three invalid `get_document` argument calls returned tool errors within otherwise completed trajectories. They did not trigger retries or change the denominator.
