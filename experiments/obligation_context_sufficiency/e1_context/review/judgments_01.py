from .record_review import record
J={}
def add(ids,reason,fails=(),errors=(),ambiguity='low'):
 for n in ids:J[n]={'fails':list(fails),'errors':list(errors),'reason':reason,'ambiguity':ambiguity}
add([8,65,85,103,118,130,136,196], 'Restates essentially the complete person-identification problem across birth/census, presentation and recording-history branches. Same historical boundary: naming one person does not make all independent clues local.', ['Local'],['whole_question_restatement'],'medium')
add([32,81], 'C7 identifies the first clinical case, but neither report country nor its founding-era religion/size qualification is established. Checking this one country relation is local; Pakistani nationality alone does not settle reporting location.',ambiguity='medium')
add([73], 'A bounded metadata/country profile of the identified first report: publication year/country and the question-required founding condition remain unverified. No new diagnosis or unbound case is assumed.',ambiguity='medium')
add([49,55,88,122], 'C7 and C9 identify the relevant clinical reports and diagnoses. Their publication years and different-year/2010s relation are not supplied; this is one unresolved temporal comparison.')
add([107], 'C7 and C9 already explicitly report FOP for the two matching clinical presentations; re-establishing their shared diagnosis does not add an unresolved qualifier.', ['Unresolved'],['already_supported'])
add([70,135,142,160,187,189,191,213], 'Requests the shared diagnosis of the two described reports with no report identified in Claims. Under the inherited referent rule, first identify a case/report or explicitly test a candidate-case relation; the final diagnostic attribute jumps over that dependency.', ['NonDownstream'],['downstream_obligation','unresolved_referent'],'medium')
add([2,20,31,34,38,68,139,188], 'C2 explicitly identifies the won ICPC edition/team, while host university is absent. Asking that event attribute is a grounded, local unresolved obligation.')
add([13,18,63,155,158], 'C2 identifies the advisor but establishes neither the two California degrees nor the 2020 video-game monograph. These complementary qualifications form one bounded advisor profile.')
add([76], 'C3-C7 already identify Rights of Man through its timing and religion/technology/Ottoman mechanics. Re-identifying that described DLC repeats an established local relation.', ['Unresolved'],['already_supported'],'medium')
add([182], 'C8 gives ordered credits and C9 explicitly names the third designer. This obligation is already supported.', ['Unresolved'],['already_supported'])
add([211], 'C4 and C7 already identify the Ottoman nation/empire and its new mechanics; this repeats the established nation attribute.', ['Unresolved'],['already_supported'],'medium')
record('01',J)
