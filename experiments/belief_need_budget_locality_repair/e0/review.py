"""Explicit single-reviewer semantic coding of fixed calibration outputs."""
import sys,json,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,rd,save,sha
from e0.run import metrics
BASE=P/'e0';cases={r['calibration_id']:r for r in rd(BASE/'CASES.json')}
# Every available output read alongside its identical old QCH; no inferred labels.
notes={
'E8192':[
('C01','W','Rank, goal difference and equal-points counterpart are separately investigable; bundled season test.'),
('C02','P','With empty Claims/H, binds the Q-described animator PC/date to Jazz2 through an asserted animation relation.'),
('C03','','Tests one missing employment transition; university and name Claims do not answer it.'),
('C05','WPIH','Adds global uniqueness and assumes the candidate satisfies all plots despite missing sensitive-issue/lead bindings.'),
('C07','','Known Rangers row lacks the other equal-points club; asks one local relation.'),
('C08','P','Empty Claims/H do not ground the proposed Jazz2 animator-to-described-PC binding.'),
('C09','P','Asserts unprovided 1979-to-Goat mapping and seeks a conflicting birthdate before establishing zodiac relation.'),
('C11','','One second-round score; other subsequent matches left for later.'),
('C12','','One university-entry/date/course relation, not a whole biography.')],
'E16384':[
('C01','W','Independent rank, goal difference and shared points conditions bundled.'),
('C02','','A proposed game can anchor one animation-credit lookup; does not assert the game satisfies every Q clue.'),
('C03','','Tests the missing employment transition, keeps candidate compatibility as a question.'),
('C05','','Explicitly tests whether the known generic assumption has the still-missing sensitive-issue/time relation.'),
('C07','','Only points counterpart remains in this query; C2 already gives Rangers points/rank/GD.'),
('C08','','Tests one possible game animation-credit relation; does not claim whole-route identity.'),
('C09','','Directly asks the missing zodiac classification of the Claim-named actor.'),
('C10','W','Full multi-match sequence with opponent totals; local selection still fails after completion.'),
('C11','W','Two independently checkable subsequent match results bundled.'),
('C12','','One candidate employment-transition test, still absent from Claims.')],
'E32768':[
('C01','WP','Wh-form presupposes a season satisfying several independent candidate-specific table conditions.'),
('C02','W','Animator identification restates game/company/RPG/financial/release-chain conditions instead of isolating one bridge.'),
('C03','','Missing employment transition framed as a question.'),
('C04','WPH','Broad alternative discovery imports Canal13 from the contradicted Hijitus route and asserts that channel for the target.'),
('C05','P','Presupposes the generic observed assumption was about the Q-sensitive issue; existence of this relation is the gap.'),
('C06','W','Asks three subsequent match results, not one local relation.'),
('C07','','One points-counterpart question; known 8th/58 context supported by C2.'),
('C08','','No-H discovery via one store/title-count event in the specified interval; other game/person clues omitted.'),
('C09','P','Zodiac query is local, but inserts Kenyan nationality not present in this QCH. Father serving in Kenyan Army is not actor nationality.'),
('C10','W','Full multi-match sequence plus opponent totals remains broad.'),
('C11','','One next-match score question anchored by observed opening match.'),
('C12','','University entry interval/course relation is unestablished in C1-C2.')],
'EDEFAULT':[
('C01','P','Presupposes that the observed signing report was the 2023 article; year/source binding only comes from tentative H/Q. Asking whether a 2023 article reported the facts would be safe.'),
('C02','P','Turns as-of25July2013 into a source dated exactly that day; no Claim establishes such a source.'),
('C03','','Safe missing coordinator appointment/date question; source qualifier remains part of the test.'),
('C04','W','Alternative identification bundles broadcast era, network form, purpose and character ensemble.'),
('C05','','Tests the missing sensitive-issue/time relation in the known scene; surrounding upset/date facts are context.'),
('C06','W','Whole multi-round record of a Claim-named player, not one match/fact.'),
('C07','','Founding year/country is a single requested founding event absent from C1-C2.'),
('C08','WP','Whole animator/company/game chain and exact July25 reporting event; date of mention is not established by Q-as-of wording.'),
('C09','P','Asserts unprovided 1979 zodiac mapping while proposing a birthdate correction.'),
('C10','W','Full multi-match sequence and opponent totals, despite locality guard.'),
('C11','W','All subsequent match results/opponents instead of a single next match.'),
('C12','','Local university-entry/course relation, no full-candidate fit assertion.')]
}
rows=[];summary={}
for arm,n in notes.items():
 manual={cid:(flags,why) for cid,flags,why in n};out=rd(BASE/arm/'OUTPUTS.json');s=[]
 for r in out:
  cid=r['id'];c=cases[cid]
  if r['output']:
   flags,why=manual[cid];d={k:k in flags for k in ['S','P','W','I','H']};d.update(V=not any(k in flags for k in ['S','I','H']),A=True,strict_valid=not flags,reason=why)
  else:d={**{k:None for k in ['V','S','P','W','I','H','A']},'strict_valid':False,'reason':'No final JSON; execution failure, semantic dimensions unassessable.'}
  row={'calibration_id':cid,'case_id':c['case_id'],'qid':c['qid'],'old_arm':c['old_arm'],'budget_arm':arm,'output':r['output'],'final_output_exists':r['final_output_exists'],'final_valid_JSON':r['final_valid_JSON'],**d};rows.append(row);s.append(row)
 summary[arm]={a:{'n':len(z:=[r for r in s if r['old_arm']==a]),'strict':sum(r['strict_valid'] for r in z),'final_output_exists':sum(r['final_output_exists'] for r in z),'semantic_validity_given_output':sum(r['strict_valid'] for r in z)/sum(r['final_output_exists'] for r in z) if any(r['final_output_exists'] for r in z) else None,'P':sum(r['P'] is True for r in z),'W':sum(r['W'] is True for r in z)} for a in ['P1','P5']}
save(BASE/'SEMANTIC_REVIEW.json',rows);save(BASE/'SEMANTIC_METRICS.json',summary)
old=[]
for cid,c in cases.items():
 r=rd(ROOT/c['old_result_path']);u=r['usage'];raw=json.loads(rd(ROOT/c['old_response_path'])['body']);reason=u.get('completion_tokens_details',{}).get('reasoning_tokens');content=raw['choices'][0]['message'].get('content') or ''
 old.append({'id':cid,'final_valid_JSON':False,'final_output_exists':bool(content.strip()),'schema_valid':False,'finish_reason':raw['choices'][0]['finish_reason'],'token_accounting':{'input':u['prompt_tokens'],'output':u['completion_tokens'],'reasoning':reason,'final':u['completion_tokens']-reason if reason is not None else None,'hit':u.get('prompt_cache_hit_tokens'),'miss':u.get('prompt_cache_miss_tokens')},'historical_result':c['old_result_path'],'reuse_only':True})
save(BASE/'E4096_REUSED.json',old);save(BASE/'E4096_METRICS.json',metrics(old,4096))
print(json.dumps(summary,indent=2))
