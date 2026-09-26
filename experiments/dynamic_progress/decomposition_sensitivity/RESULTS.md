# FULL vs BLOCKER sensitivity

12mechanicallyselectedprimaryStates,10qids,2calls each. FULL24correctedfirstaccepted inferences; BLOCKER24originalBoutputs reused, notresampled. SameQ+Claims; originalFULL24HTTP400failuresretainedinP1. Technicalformat/executiondifference disclosed. Fullrequirementsareofflineevaluationonly, notpersistent runtime state.

| Metric | BLOCKER | FULL |
|---|---:|---:|
| Correct completion |22/24|22/24|
| False closure |2/22|1/22|
| Correct closure |2/2|1/2|
| Valid blocker presence |20/22|21/22|
| No valid blocker when unresolved |2/22|1/22|
| Blocker precision |42/53=79.2%|168/177=94.9%|
| Invented-requirement outputs |1/24|4/24|
| Over-broad outputs |8/24|0/24|
| False evidence promotion |0/24|3/24|
| Adequate outputs |12/24|17/24|
| Completion agreement across pairs |12/12|10/12|
| Input tokens |20,922|15,810|
| Output tokens |76,805|191,303|
| Reasoning-token proxy |72,730|182,915|
| Meanelapsedseconds |15.20|35.61|
| Cache hit rate |70.97%|50.20%|

FULLhasreal local benefits in blockergranularity/coverage, butnotbettercompletionoverall: it tradesoneavoidedfalseclosureforonemissedtrueclosure. Reasoningproxy2.52×,output2.49×. TworesolvedslotsareonlyonecheckpointP11; noconfidentresolvedgeneralization. Largerlistdenominators andmanualRsegmentationmean precisionratiosareunit-sensitive.

P17FULLreplicatesdisagree: one listsquantity/S1/S3/season-positiongaps; theotherreturnsresolvedwithonlyacandidatesourcename,omittingallfourreviewedmaterialfamilies. P11replicatesdisagreebecauseone demandsallbackgroundcluesdespitesufficientidentity+scopedcount. These failures opposeadoptinganinitialpermanentchecklist. Supportedlocalcandidatenamesarenotautomaticallyfalsepromotion; onlyclaimsofqualifiedrequestedidentitywithoutthebindingsareflagged. Allunitreviewsavailableinthepairedartifact.

Omissioncomparisonusesmissing**allvalidblockers**,notpenalizingBLOCKERforfailingtoexhausteveryclue. FULLadditionallyclaimscompleteness; itsP17falseclosureomitsmaterialfamilies, recordedexplicitly. Frozenacceptableblockerswerenonexhaustive, so this is not anexhaustivenessrecallbenchmark.

Conclusion: FULLimproveslocalprecisiononthissmallsensitivitybutincreasescostandclosureinstability. No runtime requirementtableintroduced; a futuretemporarydecompositionstudywouldneednewgatesandheldoutvalidation.
