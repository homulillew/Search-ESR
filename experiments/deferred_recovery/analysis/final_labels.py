import json
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
ps=json.load(open(TOP/'r2/WRITER_REVIEW_PACKETS.json'));out=[]
contrib={('DR01:H',2):[0],('DR03:G',0):[0],('DR06:H',4):[0]}
for p in ps:
 key=(p['cell'],p['wave']);o=p['output'];ids=contrib.get(key,[])
 reason=('Literal season-specific5/11/21minutes retained; contrary evidence, no fabricated reconciliation.' if key==('DR03:G',0) else
  'Actual educational-purpose statement newly admitted after global fallback.' if key==('DR01:H',2) else
  'Source-bound1993conflict newly admitted; retained1992not overwritten.' if key==('DR06:H',4) else
  'Visible heading names Oscarabus; Claim is literal but does not add educational-purpose support.' if key==('DR01:G',2) else
  'Cast-only excerpt still lacks total upper bound; empty Claim is appropriate, prior unsupported Hypothesis remains.' if key==('DR05:H',0) else
  'No new active-Need relation; empty or literally source-supported proposal. All emitted statements checked against full Observation.')
 out.append({'cell':p['cell'],'round':1,'wave':p['wave'],'source_review_id':p['observation_review_id'],
 'claims':[{'index':i,'statement':t,'source_supported':True,'necessary_recovery_contribution':i in ids} for i,t in enumerate(o['claims_to_add'])],
 'hypothesis_unsupported_promotion':False,'reason':reason,'strict_recovery_contribution':bool(ids),'reviewer':'single Codex offline'})
wr(TOP/'r2/WRITER_LABELS.json',out)
final={}
for cid in [f'DR{i:02}' for i in range(1,8)]:
 for arm in ['G','H']:
  key=cid+':'+arm;strict=key not in ['DR04:H','DR05:H'];old=strict and key!='DR03:H';lenient=strict or key=='DR04:H'
  reasons={
  'DR01:G':'R1French-source education Claim retained; R2extra search adds no new sufficient education support.',
  'DR01:H':'R1Find no_match; R2ordinarySearch returns same French support and U1writes it.',
  'DR02:G':'1998old-source date and new-sourceMay7date preserved; GameB bound satisfied.',
  'DR02:H':'1998date preserved after Search; no local action needed.',
  'DR03:G':'Old4minute report preserved together with contrary5/21and5/11/21reports. Source-grounded qualification evidence recovered; runtime disagreement itself remains unresolved.',
  'DR03:H':'5/21minute contrary evidence preserved, sufficient for source-grounded refutation of strictunder5. Original4minute report NOT recovered. Report separately from same-fact recovery.',
  'DR04:G':'Dated sixthmaximum2016Claim proves>3bycutoff;2024latestmaximum reinforces it.',
  'DR04:H':'Visible source had dated4th2011/5th2013/6th2016. Claims retain only undated7maximum count. Strict temporal scope absent; count-only sensitivity passes. ActorStop had sufficient visible raw evidence, so not an evidence-level premature stop.',
  'DR05:G':'Explicit total5seasons in W re-admitted and retained.',
  'DR05:H':'TwoFinds on correct document both return cast excerpts. Lowerbound5Claim does not prove upperbound10. Unsupported upperboundHypothesis persists, but Actor correctly seeks more evidence on decision2. Horizon exhausted, not prematureStop.',
  'DR06:G':'PlayDOS1993conflict preserved with source scope alongside1992; no adjudicated finalrelease date.',
  'DR06:H':'Find first merely reconfirms1992, then Search recovers1993and Writer retains it. No observed premature closure.',
  'DR07:G':'July24PC Gamer5TBstatement retained beforecutoff.',
  'DR07:H':'Same date/specification relation recovered byFind and retained.'}
  final[key]={'strict_need_claim_recovery':strict,'lenient_count_recovery':lenient,'old_omitted_fact_recovered':old,'reason':reasons[key],
   'scope_note':'Recovery means grounded information usable for current Need; not complete Original Question resolution or adjudication of conflicting sources.', 'reviewer':'single Codex offline'}
wr(TOP/'analysis/FINAL_CASE_LABELS.json',final)
