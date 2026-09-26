# R2: completed two-decision diagnostic

The second decision adds 14 Actor calls, 7 Stop outputs, 7 tools, 27 observations and 27 Writer calls. Total: 28 Actors, 72 Writers, 21 tools. Cells whose raw status remains `active` reached the frozen horizon; they are not running jobs.

|Cell|Decision 1 → 2|First evidence|First necessary Claim|Strict Claim recovery|Original omitted fact recovered|
|---|---|---|---|---|---|
|DR01:G|search → search|1|1|True|True|
|DR01:H|find → search|2|2|True|True|
|DR02:H|search → stop|1|1|True|True|
|DR02:G|search → stop|1|1|True|True|
|DR03:G|search → search|1|1|True|True|
|DR03:H|find → find|1|1|True|False|
|DR04:H|find → stop|1|not recovered by 2|False|False|
|DR04:G|search → stop|1|1|True|True|
|DR05:G|search → stop|1|1|True|True|
|DR05:H|find → find|not recovered by 2|not recovered by 2|False|False|
|DR06:H|find → search|2|2|True|True|
|DR06:G|search → search|1|1|True|True|
|DR07:G|search → stop|1|1|True|True|
|DR07:H|find → stop|1|1|True|True|

|Cohort|Cases / qids|G strict recovery|H strict recovery|H count-only sensitivity|
|---|---|---|---|---|
|fresh|1 / 1|1/1|1/1|1/1|
|known_D3_D4|4 / 4|4/4|2/4|3/4|
|D3_D4_diagnostic|5 / 4|5/5|3/5|4/5|
|safety_D2|1 / 1|1/1|1/1|1/1|
|immediate_D1|1 / 1|1/1|1/1|1/1|
|all_diagnostic|7 / 5|7/7|5/7|6/7|

The D3/D4 mixed row is descriptive, not a fresh primary estimate. DR03 H counts source-grounded refutation; it does not recover the old 4-minute atom or reconcile the duration conflict. DR04 H fails the frozen date-qualified criterion but passes a count-only sensitivity. Sensitivities never replace the primary labels.

No H-only success. D3/D4 pairs: 3 both-success, 2 G-only, 0 both-fail. Count-only sensitivity: 4 both-success, 1 G-only. The evidence-level retrieval failure is DR05 H; the remaining strict failure is DR04 H admission scope. D2 and D1 stay outside the deferred denominator.

R1 local no-recovery with paired G success: DR01, DR05, DR06. Only DR05 remains an end-to-end local-path regression, after two insufficient Find windows on the correct document. A new source was not necessary: G recovered the fact from that same old document.

Need-bearing Find yield is 3/6 for D3/D4 (4/8 including controls). One of these is DR03 second-step corroboration of an already admitted duration, with an empty Writer. Excluding that repeated semantic information, first sufficient local-evidence yield is 2/6 (3/8 with controls). Open was never selected, so its yield is unmeasured.

There were no evidence-level premature Stops. DR04 H is one strict Claim-level premature Stop because the persistent count lacks the cutoff date; the Actor had enough raw evidence. The DR05 Actor explicitly rejected the unproven total-season inference and continued.
