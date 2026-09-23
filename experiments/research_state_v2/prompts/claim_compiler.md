Define the minimum set of testable Claims needed to resolve the current ActiveGap. Claims are not summaries of the latest observation. Every Claim must contribute to the ActiveGap, be anchored to the original task, be testable using concrete evidence, and avoid assuming an unverified relationship as fact. Prefer fewer Claims. Return 0–3 Claims; an empty set is valid when existing Claims suffice.

Return JSON: {"claims":[{"statement":"...","question_anchor_ids":["Q1"],"hypothesis_id":"none","why_needed_for_gap":"..."}]}.
