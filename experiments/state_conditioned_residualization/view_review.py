"""First-pass view from packets only; no references, arm labels, or scores."""
import argparse
from .common import *
R=P/'e1_residualization/review'
def build():
 groups={}
 for p in read(R/'PACKETS.json'):
  inp=p['model_input'];base={'question':inp['Original Question'],'parent':inp['Parent Requirement'],'current_full_claims':p['current_full_claims_for_evaluation']}
  key=digest(base)
  if key not in groups:groups[key]={**base,'responses':[]}
  groups[key]['responses'].append({'review_id':p['review_id'],'available_claim_ids':[c['claim_id'] for c in inp.get('Current Verified Claims',inp.get('Supporting Claims',[]))],
   'prior_alignment':inp.get('Prior Alignment'),'output':p['output'],'no_response':p['no_response'],'schema_valid':p['schema_valid']})
 out=[{'group_id':f'V{i+1:02d}',**g} for i,g in enumerate(groups.values())];write(R/'VIEW_GROUPS.json',out)
 print('Groups',len(out),'responses',sum(len(g['responses']) for g in out))
def show(start,end):
 for g in read(R/'VIEW_GROUPS.json')[start-1:end]:
  print('\n##',g['group_id']);print('Q:',g['question']);print('PARENT:',g['parent'])
  for c in g['current_full_claims']:print(c['claim_id'],c['statement'])
  if not g['current_full_claims']:print('CURRENT CLAIMS EMPTY')
  for r in g['responses']:print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['build','show']);ap.add_argument('start',type=int,nargs='?',default=1);ap.add_argument('end',type=int,nargs='?',default=99);a=ap.parse_args();build() if a.mode=='build' else show(a.start,a.end)
