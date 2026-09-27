"""Only Q and candidate units; never imports KEY/results or aggregates."""
import argparse
from ..common import *
def show(stage,start,end):
    packets=read(P/stage/'review/PACKETS.json')
    cases=bank(stage);qs=list(cases)
    for q in qs[start:end]:
        question=cases[q]['question']
        print('\nQUESTION',q,question)
        ref=read(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json')[q]
        print('FROZEN REFERENCE:', ' | '.join(x['id']+': '+x['description'] for x in ref['material_units']))
        for r in packets:
            if r['question']!=question:continue
            print('\n'+r['review_id'])
            for i,unit in enumerate(r['candidate_task_units']):print(str(i+1)+'.',unit)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=STAGES);p.add_argument('start',type=int);p.add_argument('end',type=int);a=p.parse_args();show(a.stage,a.start,a.end)
