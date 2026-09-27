"""Group exact masked evaluation-context/output duplicates, without opening KEY."""
from .common import *
def main():
 packets=read(P/'e1_qualification/review/PACKETS.json');groups={}
 for p in packets:
  v={k:p[k] for k in ('evaluation_context','output','schema_valid')};key=digest(v)
  if key not in groups:groups[key]={'review_ids':[],**v}
  groups[key]['review_ids'].append(p['review_id'])
 out=[{'group_id':f'V{i:03}',**groups[k]} for i,k in enumerate(sorted(groups),1)]
 write(P/'e1_qualification/review/VIEW_GROUPS.json',out);print({'packets':len(packets),'groups':len(out),'no_denominator_deduplication':True})
if __name__=='__main__':main()
