# Frozen first-pass rubric

Read only the stage's review/PACKETS.json. Do not open KEY.json, Gold Masks,
selection reference, historical GoldO, provider raw/reasoning or aggregates until
JUDGMENTS.json has been committed. One familiar Codex reviewer; no independence
claim. Provider reasoning is never needed for primary semantic judgments.

E1 packet: input Q/Skeleton/Claims and generated JSON. For every fixed node,
judge whether its status follows from all current Claims, then whether cited
Claims make a substantive contribution and jointly justify the asserted status.
Requirement wording/name overlap does not establish a fact. Trace role, event,
date and same-entity bindings; never import geography or biography from memory.
F must cover all material conditions; P must cover a proper substantive subset;
U requires no citations. Different sufficient proof sets are accepted.

Write JUDGMENTS.json as an object keyed only by review_id. E1 value:
  {"node_judgments":{"R1":{"status_correct":true,
    "support_correct":true,"reason":"Prefix-only semantic judgment"}},
   "error_codes":[],"reason":"Overall judgment"}
Include every input ID. On missing output use null judgments with a mechanical
reason, not invented statuses. Mark ambiguity in the reason if relevant. Use
SCHEMAS.json taxonomy; semantic codes require observed content, not speculation
about hidden reasoning. task_requirement_as_fact requires unsupported promotion
specifically tracing to a Q/Skeleton predicate, not just any wrong F.

E2 packet: Q/D2/supplied status Mask and generated selection. Judge one useful,
local, unresolved ID that does not skip an obvious prerequisite, or STOP only
when supplied mask is all-full. Unknown entities can themselves be discovery
targets. Do not demand a unique favorite ID. E2 value:
  {"selection_appropriate_under_visible_mask":true,
   "error_codes":[],"reason":"Visible-mask judgment"}
Use null for no usable response/input. Gold-truth downstream/full errors are
computed only after this pass; the packet does not expose actual Claims.

Commit PACKETS/KEY/JUDGMENTS, run score seal_review, then score aggregate. Report
blind-reference disagreement without changing frozen Gold. A schema-invalid
response can receive qualitative reasons but never success credit in gates.
