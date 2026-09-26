"""Append an explicit review correction; preserve previously reported artifacts."""
from progress import *

defs=read(TOP/'analysis_v2/FACT_DEFINITIONS.json')
defs['ding_maximum_threshold']={'kind':'direct','belief_update':'A fifth career 147 in 2012/13 establishes more than three maximum breaks before 2023.','next_decision':'Retain that career condition, while continuing to verify the distinct 2023 match sequence.'}
write(TOP/'analysis_v2/FACT_DEFINITIONS.json',defs)
for st in ['one_step_acquisition_v2','three_round_loop_v2']:
 b=TOP/st;labels=read(b/'evidence_labels.json')
 # Split the old aggregate career tag into the two independently verifiable
 # thresholds for consistent marginal-yield accounting. The claim knowledge
 # mapping in G5 uses these same atomic tags.
 for row in labels.values():
  if 'ding_counts' in row['facts']:
   row['facts']=sorted(set(row['facts'])|{'ding_maximum_threshold'})
 labels['d16b2ded9977489d']={'facts':['ding_maximum_threshold'],'reason':'Review correction: 2012/13 4–3 and 4–0 do not establish the 2023 sequence, but fifth career 147 independently supports the more-than-three maximum-break threshold.','review_depth':'full_observation_rereview'}
 if st=='one_step_acquisition_v2':
  write(b/'evidence_labels_review_correction.json',labels)
  score(st,labels_override=labels,output_prefix='review_corrected_')
 else:write(b/'evidence_labels.json',labels)
