# Frozen execution state

Base: `3d754d160a02eae8900c4f6bb43ef4999bb530a2` (actual remote verified before work).

All calls are one-attempt. Exact requests, prefix hashes, prompts, labels and runtime hashes are stored in each stage FREEZE.json. The invocation HEADs below contain the respective frozen manifests.

|Stage|Invocation HEAD|UTC start|
|---|---|---|
|e0|`70bbb8a8c39a4b42ce6d7b0ba3ea3bb4c5bc8712`|2026-09-26T21:22:40.321940+00:00|
|acquisition|`259753b2d08e31f39792ff8b923c2fe91ec7c3a8`|2026-09-26T21:28:19.761686+00:00|
|need/development|`cdc04c315d8f072b11c73a9cf5b4c003bf5d5fc9`|2026-09-26T21:47:45.523211+00:00|
|need/b3_issue|`10a899eef71613faf5fbcd06d1208618ab442b85`|2026-09-26T21:55:08.944878+00:00|
|need/b3_need|`d6de77d1bf58739f2dc7a6acd1e3b70fd2161128`|2026-09-26T22:02:30.906781+00:00|
|need/b4|`f5c04c3fda5d28072b7214e490767200b43dfb69`|2026-09-26T22:04:49.494245+00:00|
|need/b5|`25cdcf3ecfeffd1327359c05e074abcb9482980a`|2026-09-26T22:08:08.957513+00:00|
|need/confirmation|`7abb9229be9e12bcd2ec7bec9f0d2275c40e28d1`|2026-09-26T22:11:29.424583+00:00|

Acquired QCH was committed as `bf65191` before offline semantic labels, committed as `bec930e`. B2 was only instantiated afterwards (`cdc04c3`). All raw stages and bounded amendments remain append-only.

Provider/model: DeepSeek / deepseek-flash. Primary temperature0, response_format=json_object, stream=false; max_tokens omitted; no tools in Need. Original Actor/U1 only for acquisition, GPU1 for frozen retrieval. No provider-default cap value is claimed as a historical configuration field.

Development6qid, confirmation10disjointqid. Primary16/27natural states. Each split12single-Claim controlled pairs. No retries, resampling, post-confirmation tuning or closure calls.

The default-exhaustion confirmation case remains in ITT. Strong-H one-gap coverage is insufficient. Formal final outcome is FAIL; see FINAL_CONCLUSION.md.
