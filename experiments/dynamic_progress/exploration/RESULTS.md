# Sole bounded exploration:one relation per blocker

Freeze391b951;24newcalls,12failure-enrichedprimarycheckpoints,6qids; bothoriginalBreplicatesreusedbaseline.9checkpointswithover-broadoutputs+all3resolvedcontrols. Onlythefrozenone-relationinstructionappended. No labels/extraevidence/gating/tools; noothersemanticexploration.

| Metric | baseline B | one-relation B |
|---|---:|---:|
| Correct completion |24/24|24/24|
| False closure |0/18|0/18|
| Correct closure |6/6|6/6|
| Valid blocker presence |18/18|18/18|
| Blocker precision |33/54=61.1%|44/50=88.0%|
| Over-broad outputs |16/24|4/24|
| Unsupported-premise outputs |0/24|0/24|
| Adequate outputs |7/24|19/24|
| Strict adequate outputs |4/24|13/24|
| Correct closure witness |3/6|3/6|
| Reasoning-token proxy |96,712|182,376|
| Meanelapsedseconds |20.26|37.50|

Localcriterionpassed:precision+26.9pp,coverage/closure/premisesnotworse. Still88%<original90%precisionthreshold. One-relationinstructiondoesnotconsistentlysplitclubhistoryorlongpersonprofilebundles. Theknown2023eventcanstillbewronglydeclaredmissing; excludedHijitusdateconflictsstillmislabelunidentifiedtargetstatus. Moreexplicitconstraintcost1.89×reasoningproxy,notan efficiencywin.

Thisfailure-selectedsampledoesnotincludeP17/P19,theprimaryfalseclosurecheckpoints. ItcannotdemonstratestoppingrepairorunlockP2/P3/P4. Positiveboundedmechanismevidence: gapgranularityispartlycontrollable. Unmeasured:Needquality,generatedvsoracleblocker,semanticmutationresponse,autonomousdeferredreactivation.
