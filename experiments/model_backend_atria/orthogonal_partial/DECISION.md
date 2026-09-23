# M3 gate decision: skip partial rollout

M3 requires at least a moderate M1 or M2 model signal before executing
Atria in the v3a × Orthogonal two-arm partial rollout. M1 had a nominal
7/13 all-attempt scope advantage, but five Atria-only cells lacked a parsed
Qwen scope because of Qwen timeouts, unexpected tool calls, or a bare
answer. Among seven pairs with both scopes parsed, only two differed, both
Qwen premature Stops. That is a weak/mixed semantic signal under the
pre-registered threshold, not a clean >=4/13 planning improvement.

M2 cannot validate an Atria policy effect: 12/13 Atria tool-enabled calls
failed at the provider layer, and its sole valid response was a two-Find
batch on a prefix where Atria had planned corpus. No Atria M1-document
cell returned a natural action. Running four-round Atria rollouts would
multiply that unresolved provider failure and would not identify the
Model × Harness interaction. Accordingly M3 has no freeze and no API events.
Proceed to the separately registered M4 no-tool evidence-utilization probe.
