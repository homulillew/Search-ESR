# E2 Exact Support Verification

This prospective stage follows the user-approved E1 gate interpretation in `../E1_GATE_AMENDMENT.md`. The original E1 local freeze and failed combined gate remain unchanged. E2 isolates complete source support and reports full Claim eligibility separately.

Part A contains **all 46 actual E1-P findings**, including four supported but off-Gap findings. Part B contains 22 newly worded candidate statements against authentic historical W packets: four each temporal join (S1), identity join (S2), sequence join (S3), partial conjunction (S4), and three each metadata+body valid (S5), two-span valid (S6). All statements, source packets, truth labels, and reasons are frozen before the first E2 request.

V0 and V1 receive exactly the same input Q, active Gap, relevant Claims, candidate Finding, and full packet. V0 returns whole-packet supported/insufficient with reason. V1 returns the same verdict plus zero to two exact text offsets and a `title`/`url` metadata allowlist. The two prompts are frozen separately. No tools are available. Each of 68 paired cells receives one response from `deepseek-flash`, ordered by hash of case ID with alternating arm order. `max_retries=0` and every failure is retained.

Mechanics validate current W, integer offsets, bounds, one or two spans on `supported`, no pointers on `insufficient`, and metadata allowlist. Invalid V1 output rejects without repair. A single semantic reviewer separately judges whether pointed text plus named metadata really establishes the entire Finding. Truth and gate are in `BANK.json`, `REVIEW_RUBRIC.md`, and `freeze.json`.
