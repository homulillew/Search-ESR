# F3 single-Gap paired rollout

Six distinct qids start at source-observed historical checkpoints. Two retain
exact v3a Search/Find chat prefixes and four use exact older observed W text
with a normalized checkpoint wrapper because those runs predate v3a handles.
The normalized cases map the historical corpus document to D1 and exact
window to W1; this change of handle namespace is disclosed. All source text
is an exact contiguous corpus slice. Per qid, both arms get identical tools,
source state, question, seed verified factual Claims, semantic Gap, and four
Actor decisions. The arm order alternates.

R0 uses the historical chat prefix and real subsequent tool messages. R1
uses the latest compact Question, verified Claims, Active Gap, Workspace and
latest tool result. A compact view includes relevant observed W text and D
titles. Initial Claims come from F2-verified Findings on already visible W;
the Actor does not see a Claim in R0. The same reader, verifier and Gap
Reviewer run privately in both arms after every new W. All use one
`deepseek-flash` call, zero retries. Any invalid output or failure is logged
and the cell stops; no replacement sample. No future trajectory, gold,
post-checkpoint tool result or answer enters the prompt.

Orthogonal Search, unchanged Find/Open and original tool schema are used for
both arms. A search preview is one W; every newly returned W is read once.
No next Gap is generated. Natural resolution stops the cell. Primary paired
gate: at least three net case-level Gap-resolution or useful-evidence wins,
committed Claim precision >=95%, premature close <=10%.
