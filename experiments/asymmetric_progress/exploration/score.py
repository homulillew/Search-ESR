import sys
from pathlib import Path
T=Path(__file__).resolve().parents[1];sys.path.insert(0,str(T/'analysis'))
import score as s

def main():
 rows=s.rd(T/'exploration/exploration_outputs.json');baseline=s.rd(T/'exploration/baseline.json')
 for b in baseline:s.LOOK[('exploration_baseline',b['result']['id'])]=b['review']
 m={'baseline':s.armmetrics('exploration_baseline',[b['result'] for b in baseline]),'materiality_audit':s.armmetrics('exploration',rows),'formal_gate_override':False,'posthoc_selected':True}
 s.wr(T/'exploration/metrics.json',m)
 allrows=[];stages={}
 for stage in ['canary','primary','challenge','exploration']:
  rs=s.rd(T/stage/(stage+'_outputs.json'));stages[stage]=s.cost(rs);allrows+=rs
 s.wr(T/'analysis/cost_all.json',{'all_actual_submissions':s.cost(allrows),'by_stage':stages,'reasoning_is_subset_of_output':True,'logical_runtime_costs':'primary/metrics.json and challenge/metrics.json policies; do not confuse conditional paths with offline full sampling.'})
 print('Exploration and total costs scored; formal gates unchanged.')
if __name__=='__main__':main()
