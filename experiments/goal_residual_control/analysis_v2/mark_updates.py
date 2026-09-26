"""Record explicit single-Codex-reviewer packet decisions, never production repairs."""
from update_queue import *
import sys
p=TOP/'analysis_v2/UPDATER_LABELS.json';labels=read(p) if p.exists() else {};rows={r['review_id']:r for r in queue()}
for uid in sys.argv[1:]:
 r=rows[uid];o=r['proposal'];assert o is not None
 labels[uid]={'claims':[{'source_supported':True,'atomic':True,'unsupported_join':False,'candidate_overpromotion':False,'incidental':False,'reason':'The literal returned Observation supports this factual claim.'} for c in o['claims_to_add']],'hypothesis_reason':'Provisional candidate retained/set, or no substantive hypothesis change; no Claim-level identification inferred.'}
write(p,labels)
