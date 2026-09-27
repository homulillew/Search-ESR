"""One blinded candidate at a time; immutable human judgments, no model/scoring calls."""
import argparse,json,sys
from .contracts import HERE,BASE,read,save,digest,file_hash

RUN=HERE/'run002'
OUT=HERE/'review'

def paths():return sorted((RUN/'review/source').glob('*.json'))
def freeze_labels(stage):
    folder=OUT/stage;fs=sorted(folder.glob('*.json'))
    if len(fs)!=len(paths()):raise ValueError('incomplete '+stage)
    dest=OUT/(stage+'_FREEZE.json')
    if not dest.exists():save(dest,{'files':{str(f.relative_to(HERE)):file_hash(f) for f in fs}})
    for path,sha in read(dest)['files'].items():
        if file_hash(HERE/path)!=sha:raise ValueError('frozen review changed')

def observe(packet):
    obs=packet['Observation'];key=digest(obs);receipt=OUT/'seen_sources'/(key+'.json')
    if receipt.exists():return {'Observation_previously_displayed':read(receipt),'Observation_sha256':key}
    save(receipt,{'first_review_id':packet['review_id'],'source_packet_path':str((RUN/'review/source'/(packet['review_id']+'.json')).relative_to(HERE)),'sha256':key})
    return {'Observation':obs,'Observation_sha256':key}

def atom_info(rid):
    mapping={m['review_id']:m for m in read(RUN/'review/private_mapping.json')}
    ann={a['packet_id']:a for a in read(BASE/'bank/annotations.json')['packets']}
    return ann[mapping[rid]['packet_id']]['required_atoms']

def next_packet(stage):
    if stage in ['relevance','atoms']:freeze_labels('source')
    if stage=='atoms':
        freeze_labels('relevance')
        for f in paths():
            rid=f.stem;dest=OUT/'atoms'/(rid+'.json')
            if dest.exists():continue
            if not read(OUT/'source'/(rid+'.json'))['source_supported'] or not read(OUT/'relevance'/(rid+'.json'))['gap_relevant'] or not atom_info(rid):
                save(dest,{'review_id':rid,'covered_atom_ids':[],'reason':'Frozen rule: no source support, no relevance, or no frozen useful atoms.'})
    pending=[f for f in paths() if not (OUT/stage/f.name).exists()]
    if not pending:
        freeze_labels(stage);print(json.dumps({'stage':stage,'complete':True,'count':len(paths())}));return
    f=pending[0];p=read(f)
    output={'stage':stage,'remaining':len(pending),'review_id':p['review_id'],'Candidate':p['Candidate']}
    if stage=='atoms':output['required_atoms']=atom_info(p['review_id'])
    else:
        output.update(observe(p))
        if stage=='relevance':
            rp=read(RUN/'review/relevance'/f.name);output.update(OneGap=rp['OneGap'],C=rp['C'])
    print(json.dumps(output,ensure_ascii=False,indent=2))

def record(stage,value):
    if (OUT/(stage+'_FREEZE.json')).exists():raise ValueError('review already frozen')
    rid=value['review_id']
    if not (RUN/'review/source'/(rid+'.json')).exists():raise ValueError('unknown blinded ID')
    needed={'source':['source_supported','semantic_strengthening','strengthening_type','ambiguous_relation'],
        'relevance':['gap_relevant','duplicate_with_C','gap_useful_if_supported','duplicate_group'],
        'atoms':['covered_atom_ids']}[stage]
    if not all(k in value for k in needed) or not value.get('reason'):raise ValueError('incomplete human label')
    save(OUT/stage/(rid+'.json'),value)

def combine():
    for s in ['source','relevance','atoms']:freeze_labels(s)
    labels={}
    for f in paths():
        pieces=[read(OUT/s/f.name) for s in ['source','relevance','atoms']]
        merged={k:v for piece in pieces for k,v in piece.items()}
        merged['reason']=' | '.join(piece['reason'] for piece in pieces);merged.pop('review_id')
        labels[f.stem]=merged
    save(OUT/'LABELS.json',labels)
    print('Combined',len(labels),'blinded judgments.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['next','record','combine']);ap.add_argument('stage',nargs='?',choices=['source','relevance','atoms']);args=ap.parse_args()
    if not read(RUN/'COMPLETENESS_GATE.json')['complete']:raise ValueError('incomplete E1: scoring forbidden')
    if args.action=='next':next_packet(args.stage)
    elif args.action=='record':record(args.stage,json.load(sys.stdin));next_packet(args.stage)
    else:combine()

if __name__=='__main__':main()
