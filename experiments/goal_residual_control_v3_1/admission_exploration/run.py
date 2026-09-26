import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_exploration'
if sys.argv[1]=='prepare':
 bank=read(TOP/'admission_replay/BANK.json');gold={r['packet_id']:r for r in read(TOP/'admission_replay/GOLD_ADMISSION_ATOMS.json')}
 chosen=[p for p in bank if gold[p['packet_id']]['atoms']]
 for q in sorted({p['qid'] for p in bank},key=int):
  empty=[p for p in bank if p['qid']==q and not gold[p['packet_id']]['atoms']]
  chosen.append(min(empty,key=lambda p:digest(['U2-empty-controls-20260926',p['packet_id']])))
 assert len(chosen)==27 and len({p['packet_id'] for p in chosen})==27
 chosen.sort(key=lambda p:digest(['U2-order-20260926',p['packet_id']]))
 write(b/'selection.json',[{'packet_id':p['packet_id'],'qid':p['qid'],'stratum':'useful_atom' if gold[p['packet_id']]['atoms'] else 'empty_control'} for p in chosen])
 u1={r['case_id']:r for r in read(TOP/'admission_replay/requests.json') if r['arm']=='U1'}
 items=[]
 for p in chosen:
  old=u1[p['packet_id']];req=copy.deepcopy(old['request'])
  req['messages'][0]['content']+='\n\n'+(b/'AMENDMENT.txt').read_text()
  it={**old,'arm':'U2','request':req,'request_sha256':digest(req)};items.append(it)
 write(b/'requests.json',items)
elif sys.argv[1]=='freeze':
 items=read(b/'requests.json');freeze(b,items,{'kind':'adaptive exploratory diagnostic only','U2_calls':27,'original_gate':'failed; unchanged','comparison':'archived Uc/U1 on same 27','mode':'json_mode_fallback'})
 f=read(b/'freeze.json')
 paths=[b/'run.py',b/'AMENDMENT.txt']+list((TOP/'admission_replay').glob('*.json'))
 for p in paths:f['files'][str(p.relative_to(ROOT))]=sha(p)
 write(b/'freeze.json',f)
else:
 gate(b);batch(b,'U2',read(b/'requests.json'))
