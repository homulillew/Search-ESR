import json
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
ps=json.load(open(TOP/'r1/WRITER_REVIEW_PACKETS.json'))
# Explicit new necessary Claim contributions. All other emitted Claims were read and judged
# literally supported but do not independently recover the active frozen requirement.
contrib={('DR01:G',2):[0],('DR02:G',0):[0],('DR02:G',1):[0],('DR02:H',0):[0],
('DR03:G',0):[0],('DR03:G',3):[0],('DR03:H',0):[1],('DR04:G',0):[1],
('DR04:G',1):[0],('DR05:G',0):[0],('DR06:G',4):[0],('DR07:G',0):[0],('DR07:H',0):[0]}
reason={('DR04:H',0):'Both facts are literally supported. Undated7maximum Claim omits the pre-cutoff milestone necessary for strict date-qualified recovery; count-only sensitivity succeeds.',
('DR05:H',0):'Claim is a supported lower bound. Hypothesis promotes highest mentioned season into unsupported total upper bound.',
('DR03:H',0):'Duration5/21 is grounded contrary evidence for the Need, not rediscovery of original4minute claim; characters also supported.',
('DR03:G',3):'Source-scoped5/21duration preserves contrary evidence alongside4minute listing; clearing candidate records conflict.',
('DR03:G',4):'No new Claim; hypothesis reintroduced from Argentine-title correspondence despite retained duration conflict. Candidate persistence risk, not an erased Claim.',
('DR01:G',1):'New Argentine broadcast dates are source-supported but do not recover educational purpose.',
('DR02:G',4):'ZZT1991fact is source-supported and relevant to another original requirement, but not this Recovery Need. Hypothesis remains a provisional candidate.',
('DR05:G',2):'Plot statement is supported but repeats an already known requirement; not additional recovery.',
('DR06:G',3):'Version1.1in1993 retained with proper scope; not substituted for initial-release conflict.',
('DR06:H',0):'Empty proposal from existing1992corroboration; new source-window trace is kept. Not a duplicate-Claim failure.'}
out=[]
for p in ps:
 key=(p['cell'],p['wave']);o=p['output'];ids=contrib.get(key,[])
 out.append({'cell':p['cell'],'round':0,'wave':p['wave'],'source_review_id':p['observation_review_id'],
  'claims':[{'index':i,'statement':t,'source_supported':True,'necessary_recovery_contribution':i in ids} for i,t in enumerate(o['claims_to_add'])],
  'hypothesis_unsupported_promotion':key==('DR05:H',0),
  'reason':reason.get(key,'Exact required relation admitted with observed scope.' if ids else 'No new required relation; any emitted Claim is supported by this observed source.'),
  'strict_recovery_contribution':bool(ids),'reviewer':'single Codex offline; no independent-review claim'})
(TOP/'r1/WRITER_LABELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('reviewed',len(out),'Writer outputs')
