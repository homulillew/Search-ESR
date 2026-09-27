"""Readable grouping derived solely from masked first-pass packets."""
import argparse
from experiments.recoverable_control_equivalence.common import P,read,write,digest
R=P/'e1_selection/review'
def build():
    groups={}
    for packet in read(R/'PACKETS.json'):
        key=digest(packet['input'])
        if key not in groups:groups[key]={'input':packet['input'],'responses':[]}
        groups[key]['responses'].append({k:packet[k] for k in ('review_id','selection','no_response')})
    values=[{'group_id':f'V{i+1:02d}',**g} for i,g in enumerate(groups.values())]
    write(R/'VIEW_GROUPS.json',values)
    print('Masked input groups',len(values),'responses',sum(len(g['responses']) for g in values))
def show(start,end):
    for g in read(R/'VIEW_GROUPS.json')[start-1:end]:
        print('\n##',g['group_id']);p=g['input'];print('QUESTION:',p['Original Question'])
        print('MASK:',p['Control Mask'])
        for n in p['Task Skeleton']:print(n['requirement_id'], n.get('label',''), ' | '.join(s['text'] for s in n.get('source_spans',[])))
        print('RESPONSES:',g['responses'])
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['build','show']);parser.add_argument('start',type=int,nargs='?',default=1);parser.add_argument('end',type=int,nargs='?',default=999)
    a=parser.parse_args();build() if a.mode=='build' else show(a.start,a.end)
