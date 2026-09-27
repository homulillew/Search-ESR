# Qwen3-32B judgment audit

The frozen primary score is **34/50**. All 50 qids remain in the denominator.
Qwen judged 49 submitted final answers. `qid 283` had no final agent answer after
DeepSeek used all 65,536 completion tokens on reasoning in its first response;
the judge call was skipped and the question counted incorrect. The 49 judge
responses all parsed successfully and had no API error.

The 16 primary incorrect qids are 58, 160, 275, 283, 315, 366, 428, 471,
486, 715, 763, 936, 1036, 1090, 1119, and 1152. The full prompts, raw Qwen
responses, parsed decisions, and token usage are in `judgments/qid_*.json`.

## Borderline equivalence: qid 275

Gold: `Union Carbide and Carbon Corporation`. The agent's `Exact Answer` was
`Union Carbide Corporation`; its explanation also explicitly identified the
1917 name. Qwen marked this incorrect, reasoning that the two names represent
distinct entities. The [American Chemical Society's historical account](https://www.acs.org/education/whatischemistry/landmarks/carbonfibers.html)
states that the former changed its name to the latter in 1957. This is a
plausible judge false negative for an entity-identification question. It is
flagged for interpretation only: the official-prompt Qwen verdict remains
incorrect in the primary 34/50 score. Counting this alias as correct would
produce a non-primary sensitivity score of 35/50.

The earlier 46/50 figure used different agent outputs and an investigator
judge, so its 12-question difference from this score does not measure Qwen
judge bias or the effect of the retrieval tool alone.
