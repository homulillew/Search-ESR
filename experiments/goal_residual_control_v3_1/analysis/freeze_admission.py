import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_replay';bank=read(b/'BANK.json');gold=read(b/'GOLD_ADMISSION_ATOMS.json')
assert len(bank)==len(gold)==55
assert {r['packet_id'] for r in bank}=={r['packet_id'] for r in gold}
mode=read(TOP/'structured_transport_canary/metrics.json')['mode'];items=[]
for i,r in enumerate(bank):
    for arm in (['Uc','U1'] if i%2==0 else ['U1','Uc']):
        chat=copy.deepcopy(r['old_request'])
        if arm=='U1':
            chat['messages'][0]['content']=(TOP/'prompts/state_updater_gap_conditioned.md').read_text()
            v=json.loads(chat['messages'][1]['content']);v['Current Research Gap']=r['current_actor_gap']
            chat['messages'][1]['content']=json.dumps(v,ensure_ascii=False,indent=2)
        it=make_item(r['packet_id'],r['qid'],arm,'state_updater',chat,mode)
        if arm=='Uc':assert it['request']['messages']==r['old_request']['messages']
        items.append(it)
freeze(b,items,{'U0_archived':55,'Uc':55,'U1':55,'qid_clusters':10,'mode':mode,'current_gap':'exact generating Actor output','review_atoms_pre_call':True})
f=read(b/'freeze.json')
for p in [Path(__file__),TOP/'analysis/annotate_atoms.py',TOP/'structured_transport_canary/metrics.json']:
    f['files'][str(p.relative_to(ROOT))]=sha(p)
write(b/'freeze.json',f)
