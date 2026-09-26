from progress import *
labels=read(TOP/'analysis_v2/EVIDENCE_LABELS.json');defs=read(TOP/'analysis_v2/FACT_DEFINITIONS.json')
defs.update(dean_paper={'kind':'direct','belief_update':'Dean Dodrill animates on normal 8x11 printing paper.','next_decision':'Verify the Game B intro/end credit and company chain.'},goat_years={'kind':'decision','belief_update':'The observed Goat-year calendar lists 1979, not May 1978.','next_decision':'Resolve the birth-year conflict before closing Peter King identification.'},milan_candidate={'kind':'decision','belief_update':'The 2005 Milan–Liverpool final has Milan leading 3–0 at half time.','next_decision':'Inspect this alternative match for the 95th-minute free kick and club history.'})
M={'3c905f79d81732a6':'heart_exclusion','42a2a0e9fc4209db':'messi95 messi_timing','cd8bf9c8b0aa0e64':'dean_pc dean_paper','8b9af0139dd61ded':'peter_police','25cdbb840d252971':'goat_years','40eb23fc122f1ee9':'goat_years','aa5d4f149ea90381':'goat_years','ca9344d6796ab4b9':'goat_years','ebe40c503fd24c3e':'goat_years','fbfd981e380a8efd':'goat_years','14210a953b268596':'milan_candidate','3571365e3bec9a89':'milan_candidate'}
for w in read(TOP/'transition_replan_v2/EVIDENCE_CATALOG.json'):
 eid=w['evidence_id']
 if eid in labels:continue
 ts=M.get(eid,'').split();labels[eid]={'facts':ts,'reason':' '.join(defs[t]['belief_update'] for t in ts) if ts else 'No novel original-goal relation established in returned passage.' if w['in_primary_pool'] else 'Outside frozen primary pool; title/topic screen and selected full-text follow-up found no qualifying relation. Alternative-source sensitivity is non-exhaustive.','review_depth':'full_observation' if ts or w['in_primary_pool'] else 'title_topic_screen'}
write(TOP/'analysis_v2/EVIDENCE_LABELS.json',labels);write(TOP/'analysis_v2/FACT_DEFINITIONS.json',defs)
k=read(TOP/'transition_replan_v2/ONLINE_KNOWLEDGE_REVIEW.json');score('transition_replan_v2',k['knowledge'],k['closure'])
