"""Transcribe explicit single-reviewer judgments; never infer entailment."""
from experiments.evidence_gap_gold_obligation.common import *
PACKETS={p['review_id']:p for p in read(P/'e1_gap/review/PACKETS.json')}
def record(part, judgments):
 labels=[]
 for num,spec in judgments.items():
  rid=f'R{num:03d}';p=PACKETS[rid];reason=spec['reason'];bad=spec.get('bad_refs',{})
  labels.append({'review_id':rid,'support_correct':spec.get('support_correct',not bad),
   'support_refs':[{'claim_id':c,'correct':c not in bad,'reason':bad.get(c,'Reviewed against its own claim scope and frozen reference; relevant support/allowed identity anchor, without strengthening.')} for c in (p['output'] or {}).get('supported_by',[])],
   'missing_label':spec.get('missing_label','correct'),'evidence_needed_correct':spec.get('evidence_needed_correct',True),
   'evidence_level':spec.get('evidence_level',True),'candidate_specific_unsupported':spec.get('candidate_specific_unsupported',False),
   'errors':spec.get('errors',[]),'reason':reason})
 write(P/f'e1_gap/review/PART{part}.json',labels)
