from ...common import *
from ...source_units import validate
stage='e2_fresh';out=P/stage
reviews={r['review_id']:r for r in read(out/'review/FIRST_PASS.json')};key=read(out/'review/KEY.json');reverse={v:k for k,v in key.items()};cases=bank(stage)
rows=[]
for job in read(out/'SCHEDULE.json'):
 r=read(out/'calls'/f"{job['id']}.result.json");rid=reverse[job['id']];v=validate(r['output'],job['arm'],cases[job['qid']]['source_units'])
 row={'id':job['id'],'review_id':rid,'arm':job['arm'],'mechanical':v,'semantic_pass_unchanged':True}
 if job['arm']=='D2':
  rv=reviews[rid];row['grouping_fidelity']={'compatible_grouping':not(rv['harmful_merge'] or rv['harmful_split']), 'harmful_merge':rv['harmful_merge'],'harmful_split':rv['harmful_split'],'coverage_omission':not all(rv['coverage'].values()),'reason':rv['reason']}
 rows.append(row)
write(out/'review/SECOND_PASS.json',{'first_pass_commit':'4117df1','judgments':rows,'D1':'Not run in fresh confirmation, as frozen.'})
labels={
'D0':['compatible_structure','same_structure','compatible_structure','compatible_structure','compatible_structure','compatible_structure','compatible_structure','same_structure','compatible_structure','same_structure','compatible_structure','compatible_structure'],
'D2':['compatible_structure','same_structure','same_structure','same_structure','same_structure','same_structure','compatible_structure','compatible_structure','same_structure','same_structure','compatible_structure','same_structure']}
reasons={
'968':'Insect identity clues may combine or split; both preserve harvesting project and quoted speaker/article relation.',
'548':'Same founding/death, acquisition, network and launch chain; D0 both resolve later to local2021 antecedent, D2 both leave source wording.',
'523':'Both preserve actor→family-series→producer chain; D0 biography grouped versus split remains coherent under frozen referent rubric.',
'1142':'Same country tally-year and organization-report chain; D0 adds redundant anaphora objectives without changing substantive structure.',
'294':'Same family, childhood, translation and death conditions; D0 childhood split is compatible, D2 source groups equivalent.',
'1096':'Both keep first/corresponding roles separate and preserve ranking/keyword scopes; D0 bibliographic and affiliation clauses split differently.',
'836':'Same series/showrunner-company/comedian/Nurse chain; D2 puts series constraints with performance versus own group, still compatible.',
'128':'Same two-article chain; D2 first-article unique-athlete clause may combine or remain separate.',
'1158':'Same movie-star clues and first-soap target; D0 explicit first-soap referent and split birth/career are compatible refinements.',
'805':'Both preserve distinct author/translator and identical temporal/academic roles; no change in semantic grouping.',
'160':'Same poem-book textual identity and award/nominator relations; D2 nomination can join award episode, D0 target may be separate.',
'1027':'Same racer conditions, independent event/date scopes and first-race-age target; D0 explicit first-race referent is compatible.'}
pairs=[]
for arm,ls in labels.items():
 for q,label in zip(cases,ls):pairs.append({'qid':q,'arm':arm,'review_ids':[reverse[f'{arm}__Q{q}__R{r}'] for r in (1,2)],'label':label,'reason':reasons[q]})
write(out/'review/PAIRS.json',pairs)
