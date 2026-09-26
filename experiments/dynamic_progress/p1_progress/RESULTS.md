# P1 results

## Transport and denominators

Original frozen batch216HTTPrequests:96Baccepted (one schema failure),96R+24FULL rejectedHTTP400 beforeinference because their prompt lacked the literalwordJSON. This was an experimenter transport defect. Originalfailure-inclusive R and FULL havezero validoutputs; no semanticcomparison can be inferred from those rejections.

Correction frozen separately: append only `Return JSON.` to user serialization for those120rejections. Rsystemprompt byte-identical;QandnumberedClaims unchanged; all120corrected requests accepted withvalidoutputs. No acceptedBresponse, timeout, lengthfailure or semantic error resampled. SDKretry0; **120additionalHTTPsubmissions were made**, not silently calledzeroattempts. Originalrecordsanddenominatorsretained. Comparisons involving R/FULL below are transport-corrected diagnostics with sequentialexecution and formatting difference, not an undisturbed randomized experiment.

## Primary:24checkpoints/10qids,48slots perarm

| Metric | old R, corrected diagnostic | B, original | B gate |
|---|---:|---:|---:|
| Correct completion |45/48|44/48|descriptive|
| False closure |3/42=7.1%|4/42=9.5%|≤4/42,pass|
| Correct closure |6/6|6/6|6/6,pass|
| Valid blocker presence |38/42=90.5%|36/42=85.7%|≥36/42,pass|
| Blocker precision |62/82=75.6%|76/103=73.8%|≥90%,**fail**|
| Over-broad outputs |16/48|16/48|descriptive|
| Invented-requirement outputs |3/48|3/48|descriptive|
| Unsupported-premise outputs |4/48|2/48|descriptive|
| False evidence promotion |3/48|2/48|descriptive|
| Adequate whole outputs |23/48|23/48|includesabsenceofinvalidunits|

Bhas9statuserrors,3semantic-referenceerrors; strictadequate16/48. Closurewitness adequate3/10predictedclosures (3/6correctclosures); count-onlywitnessesoftenomitidentitybasis. RwitnessN/A. Completionreplicateagreement B24/24vsR23/24, butBstablefalseclosuresappearinthe2q580checkpointsP17/P19. Stability is not correctness. Bothadequateunresolvedpairs B7/21vsR8/21; bothcorrectresolvedpairs3/3each. Repeatedqid/Statevariantsnotindependenttrials.

B's2unsupportedpremiseoutputs: P14imports1978→HorsecalendarrelationnotinClaims; P24includesLiverpool–Milanamongverified95minuteeventswhenClaims onlysupportscoringpattern. Bothareseparatefromlocalization/retrievalfailures. NearclosureP19lacksEdgar'sroommaterole; P17hasonlyoneepisodeplotandnopreciseseriescount.

A post-hoc descriptive sensitivity excusesonlyover-breadth: B96/103=93.2%units avoidothercontenterrors. This illustrates that the main precisionfailure concerns usablegapgranularity; it **does not change the frozen gate**, fixclosure/status/witnesserrors or demonstrate goodNeedgeneration.

## Challenge:separatehistoricaldiagnostic

| Metric | historical Direct S | corrected R | B |
|---|---:|---:|---:|
| Correct completion |33/48|43/48|45/48|
| False closure |15/42|5/42|0/42|
| Correct closure |6/6|6/6|4/6|
| Valid blocker presence |N/A|34/42|41/42|
| Blocker precision |N/A|52/70|85/116|
| Failed output |0|0|1|

Direct is the48archivedSFrontierresponses, regradedunderthisstudy'spre-callmaterialitylabels withoutresampling. B improves completion by25percentagepoints, whileoverdemandsonthegamechronologyproduce2missedclosures(C04), andC22hasoneunrepairedmissingclosure-ref schemafailure. HistoricalDirectcomparisonisnoncontemporaneousandtopic-exposed. Itdoesnotoverridefailedfresh-primaryprecisionorold-R'sslightlybetterprimarycompletion.

Decision: P1 gate failed; formal P2/P3/P4 notrun. No inferenceaboutOracleSelector, retrievalprecision, evidenceyield orautonomousrecovery.
