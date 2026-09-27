"""Whitelist historical Q/Claims; never use GoldO to author alignment labels."""
from .common import *
def main():
 assert git('cat-file','-t','81caa52')=='commit'
 out=[]
 for c in read(HIST/'e0_reference/CASES.json'):
  assert c['belief']['question']==questions()[str(c['qid'])]['question']
  claims=[{'claim_id':x['claim_id'],'statement':x['statement']} for x in c['claims']]
  assert len({x['claim_id'] for x in claims})==len(claims)
  out.append({k:c[k] for k in ('case_id','state_id','qid','type')}|{'question':c['belief']['question'],'claims':claims,'claims_sha256':digest(claims)})
 write(P/'e0_reference/STATES.json',out)
 write(P/'e0_reference/STATE_SOURCE.json',{'source':rel(HIST/'e0_reference/CASES.json'),'sha256':sha(HIST/'e0_reference/CASES.json'),'states':len(out),'unique_qids':len({x['qid'] for x in out}),'fields_used_for_alignment':['question','claims'],'historical_gold_obligation_not_exported':True,'Oracle_frozen_before_state_read':'81caa52c6895aa59a9133c2e98189dea39a4d68a'})
if __name__=='__main__':main()
