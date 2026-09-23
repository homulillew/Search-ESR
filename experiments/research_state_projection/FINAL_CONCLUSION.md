# Selective Control-State Projection: final conclusion

This branch adds an append-only S0 diagnostic and a frozen, contemporaneous S1 B/C intervention to the qualification branch at `d7878c0`. Historical R1 results remain unchanged: Qualification failed its preregistered routing gate. S1 used 13 fixed prefixes from two questions, 26 valid one-step DeepSeek responses, 71 manually reviewed proposed tool calls, zero retries and no tool execution. B replayed Broad Plan + Qualification; C replaced those cards with one verification-gap/source-type/promoted-target card. All later stages stopped at the S1 gate. See `r1_gap_reanalysis/RESULTS.md`, `resolved_control_state/RESULTS.md`, `resolved_control_state/freeze.json` and the raw events and scores for the audit trail.

## Answers to the twelve research questions

1. **Did R1 Qualification improve gap alignment that the old metric missed?** The post-hoc S0 review does not establish that. Direct gap-directed calls were 6/36 under historical Broad Plan and 7/35 with Qualification, while checkpoints with any direct gap action stayed 6/13 in both arms. Checkpoints with any direct-or-partial action fell from 13/13 to 10/13. These single-reviewer labels diagnose mechanisms; they do not replace R1's failed preregistered result.

2. **Is `candidate_inspected` too coarse?** Yes for interpreting mechanism. R1's `546:25` includes a Find of D10 that repeats its visible opening result and a different Find that attempts to test later missing scores. The same D# inspection flag conceals different query purposes. S1 likewise includes a C Find of D34 aimed at the proposed match's missing goal timeline. Query intent still does not prove that the returned source would be suitable or useful.

3. **Is a single resolved card better than simply appending Qualification?** There is a limited directional signal: concurrent C increased directly aligned checkpoints from 6/13 to 8/13, first-call direct alignment from 3/13 to 6/13, and promoted-target use from 3/4 to 4/4. Four paired checkpoints improved direct alignment and two regressed. The frozen overall gate **failed**, so this study does not establish that the replacement is reliably better. The B/C contrast is the combined effect of removing the Broad Plan, changing card structure, omitting unpromoted handles and emphasizing the gap/source type.

4. **Did omission of unpromoted candidate handles reduce their inspection?** The descriptive count changed from 2/7 in B to 1/7 in C, but only `546:25` changed in the expected paired direction. The requirement was at least two such paired changes. At `1094:45`, C still inspected D34 with a gap-testing query. A causal omission effect is unproven.

5. **Was inspectable/promoted utilization preserved?** Yes within this sample: 3/4 in B and 4/4 in C, with the gain at `1094:61` and no paired loss. This measures proposed inspection only; no source was actually read in S1.

6. **Does explicit repetition of a candidate D# itself increase inspection?** Unknown. The intended candidate-salience ablation S1b was not run after the S1 gate failed. B/C change several control-card features together, so their inspection difference cannot isolate explicit naming.

7. **Should Control State store Candidate Status or Verification Gap?** The current experiment supports keeping the verification gap and required source type as *plausible, action-relevant fields*: C yielded more directly gap-aligned checkpoints without increasing all Searches. It does not prove an independent benefit of either field or justify persisting every model-generated gap. Keep evidence and tentative hypotheses in history; only prefix-supported source-for-gap judgments are candidates for projection into control state.

8. **Can DeepSeek construct a reliable Resolved Projection itself?** Unknown. S2 was not run. S1 used reviewer-authored projections, so there is no self-projection reliability estimate.

9. **What causes False Promotion most often?** Unknown for model self-projection, because S2 produced no judgments. Earlier prefix reviews identify plausible hazards, such as treating a single 95th-minute event as proof of the full club-history conjunction, but this study does not estimate their frequency. Do not persist an unreviewed model projection on this evidence.

10. **What is the main bottleneck: state projection, source routing, workspace salience, Search prior or localizer?** The observed bottleneck is mixed *action/source routing under a proposed control state*. At `1094:93`, C chose unrelated D53; at other cells C made more suitable gap tests. S1's Searches fell from 28 to 22, so a universal Search-only explanation does not fit these responses. The experiment did not manipulate workspace directory, execute local Find/Open results or isolate the individual projection fields; it cannot rank workspace salience, localizer and projection accuracy as causes.

11. **Enter Workspace Directory now?** No. The specified prerequisite was a reliable projected rollout that still selects the wrong D# despite a correct gap and source type. S3 did not run; one wrong D53 at S1 is a diagnostic, not the required rollout evidence.

12. **Any evidence for hard action gating?** No. Projection reliability and useful downstream evidence remain unmeasured. Search, Find and Open should remain available in any subsequent soft-state experiment.

## Decision

Stop at S1. The strongest supported lesson is that an inspection count does not identify whether an action tests a missing premise. A concise gap/source projection is promising in some checkpoints, but the prespecified unpromoted-candidate criterion was not met and two direct-alignment checkpoints regressed. The next mechanism test, if redesigned later, should isolate one card component at a time and measure returned source compatibility and useful evidence before making persistent state or action restrictions stronger.

The research target remains: **current gap → appropriate action → suitable source → useful evidence**. This one-step study observes only the proposed action and source handle, not the last two links.
