# Historical baseline and source boundary

Base remote HEAD: `e613916b8384a0b6c88b8511982393af5480cd83`. The prior branch showed Single Query@10 36/40, dual 5+5 36/40, oracle-document Find 33/40 useful, and diagnostic Top1/Top2 Find 24/40 versus 26/40. Neither document policy passed its deployment gate, and A1 was not run. This branch does not revise those outcomes.

SC0 draws target Gaps and sufficient doc IDs from frozen U1, and source text from earlier historical observation packets. Known future observations in the same replay establish event order where available. Where a target window was not observed, `target_first_seen_event` is null and `right_censored_after_prior` is true; this records the temporal limit honestly. Source support and exact quoted substrings are verified mechanically. The bank is not a claim that every prior W belongs to one continuous original trajectory; each case identifies its own historical replay or packet cutoff.
