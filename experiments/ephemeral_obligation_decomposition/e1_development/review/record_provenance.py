from ...common import *
from ...source_units import validate
stage='e1_development';out=P/stage
reviews={r['review_id']:r for r in read(out/'review/FIRST_PASS.json')};key=read(out/'review/KEY.json');reverse={v:k for k,v in key.items()};cases=bank(stage)
# Explicit manual second-pass judgments after reading every D1 clause and anchor.
fully_reviewed=['R007','R048','R030','R049','R053','R021','R009','R008','R001','R036','R028','R032','R055','R034','R041','R019','R026','R040','R004','R012']
context_examples={'R007':[3,5],'R048':[2,3,7],'R053':[2,3,4,7],'R021':[2,3,4,5,7],'R008':[3], 'R001':[2,5,6,7], 'R036':[5,6,7], 'R032':[8], 'R034':[2], 'R041':[2,3,4,5], 'R019':[2,3,4,5,6], 'R026':[2,6,7,8,10], 'R040':[2,4,5,7,8]}
rows=[]
for job in read(out/'SCHEDULE.json'):
 r=read(out/'calls'/f"{job['id']}.result.json");rid=reverse[job['id']];v=validate(r['output'],job['arm'],cases[job['qid']]['source_units'])
 row={'id':job['id'],'review_id':rid,'arm':job['arm'],'mechanical':v,'semantic_pass_unchanged':True}
 if job['arm']=='D1':
  assert rid in fully_reviewed
  row['anchor_entailment']=[{'node':i+1,'label':'fully_supported','reason':'Cited exact spans express this requirement in their original-Q context; no new role equality, event date or relation is introduced. Source-unit addressing resolves original ellipsis/anaphora.', 'context_dependency_example':i+1 in context_examples.get(rid,[])} for i in range(len(r['output']['requirements']))]
  row['reason']='Manual comparison of every prose node against its displayed source spans; contextual support is not a claim that every excerpt is standalone.'
 elif job['arm']=='D2':
  rv=reviews[rid];row['grouping_fidelity']={'compatible_grouping':not(rv['harmful_merge'] or rv['harmful_split']), 'harmful_merge':rv['harmful_merge'],'harmful_split':rv['harmful_split'],'coverage_omission':not all(rv['coverage'].values()),'reason':rv['reason']}
 rows.append(row)
write(out/'review/SECOND_PASS.json',{'first_pass_commit':'f598e02','judgments':rows,'anchor_context_policy':'The original Q remains available. Source-unit addressing can resolve an original pronoun/ellipsis. Fully supported means no added semantic condition; it does not certify standalone fragments. Examples recorded, not an exhaustive context-dependency rate.'})
# Manually compared replicate structures, in development qid order.
labels={
'D0':['compatible_structure','compatible_structure','compatible_structure','same_structure','same_structure','same_structure','compatible_structure','one_valid_one_invalid','compatible_structure','one_valid_one_invalid'],
'D1':['compatible_structure','compatible_structure','compatible_structure','same_structure','same_structure','compatible_structure','compatible_structure','compatible_structure','compatible_structure','same_structure'],
'D2':['same_structure','same_structure','compatible_structure','compatible_structure','compatible_structure','same_structure','same_structure','same_structure','same_structure','same_structure']}
reasons={
'122':'Same person/place/country and three event scopes; extra identity/location nodes or split source attribution are compatible.',
'169':'Same charity, death/accident and partner-song relation; clause-level versus episode-level grouping preserves structure.',
'228':'Founder/game and education can be connected as one founder identity or separated; gift-building chain survives both.',
'261':'Both retain independent author-role quantifiers; table count and value may combine without role binding.',
'538':'Three referenced figures may share book-reference unit or be separated while keeping person-specific clues.',
'637':'Both maintain two separate patients and all timing; splitting case geography/biopsy clauses is compatible.',
'843':'Both retain game/DLC, thesis/advisor and credit objective; extra existence/credential nodes do not change identities.',
'922':'D0 R050 loses recipient-role specificity under frozen reference; D1 split courier clause and D2 identical groups preserve it.',
'971':'Both keep author/PhD/advisor and book/later-article chain; identity and advisor history split differently.',
'1259':'D0 R017 corrupts teammate-country comparison; D1/D2 preserve same semantic set and correct final event attributes.'}
pairs=[]
for arm,ls in labels.items():
 for q,label in zip(cases,ls):pairs.append({'qid':q,'arm':arm,'review_ids':[reverse[f'{arm}__Q{q}__R{r}'] for r in (1,2)],'label':label,'reason':reasons[q]})
write(out/'review/PAIRS.json',pairs)
