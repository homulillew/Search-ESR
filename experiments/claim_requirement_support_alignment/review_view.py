"""Content-only review display; never opens KEY, raw responses or reasoning."""
from .common import *

def main():
 packets=read(P/'e1_support_alignment/review/PACKETS.json');groups={}
 for p in packets:
  value={k:p[k] for k in ('model_input','output','schema_valid','no_response')};key=digest(value)
  if key not in groups:groups[key]={'review_ids':[],**value}
  groups[key]['review_ids'].append(p['review_id'])
 result=[{'group_id':f'V{i:03}',**groups[key]} for i,key in enumerate(sorted(groups),1)]
 write(P/'e1_support_alignment/review/VIEW_GROUPS.json',result)
 print(json.dumps({'packets':len(packets),'distinct_identical_content_groups':len(result),'scope':'Exact input/output/schema identity only; all replicates remain in scoring.'}))
if __name__=='__main__':main()
