import copy,json
from pathlib import Path
from runtime import TOP,view,item,validate,wr
from cache import ProgressCache,decision

def main():
    cs=json.loads((TOP/'bank/PRIMARY.json').read_text());c=copy.deepcopy(cs[0]);v=view(c)
    assert set(v)=={'Original Question','Verified Claims'}
    c['state']['working_hypothesis']='POISON';c['history']=['POISON'];c['state']['available_workspace']={'x':'POISON'};c['state']['attempts']=['POISON'];c['light_output']='POISON'
    assert view(c)==v and 'POISON' not in json.dumps(item(c,'Audit',1)['request'])
    assert (TOP/'prompts/L0.md').read_bytes()==(TOP.parent/'dynamic_progress/prompts/blocker.md').read_bytes()
    task=(TOP/'TASK.md').read_text();addition=task.split('# 28. Light Progress L1 Prompt')[1].split('```text\n')[1].split('```')[0]
    assert (TOP/'prompts/L1.md').read_text()==(TOP/'prompts/L0.md').read_text()+'\n'+addition
    for arm in ['L0','L1','Audit']:assert 'json' in item(c,arm,1)['request']['messages'][0]['content'].lower()
    reject={'confirmed':False,'blocking_gap':{'gap':'dummy','claim_refs':[]},'closure_support':[]}
    validate(reject,'Audit',1);validate({'confirmed':True,'blocking_gap':None,'closure_support':[{'relation':'dummy','claim_refs':[1]}]},'Audit',1)
    invalid=[dict(reject,confidence=0.5),dict(reject,confirmed=True),dict(reject,blocking_gap={'gap':'dummy','claim_refs':[2]})]
    for x in invalid:
        try:validate(x,'Audit',1)
        except Exception:pass
        else:raise AssertionError('Invalid schema accepted')
    cache=ProgressCache();cache.observe(c['question'],c['state']['verified_claims']);cache.put('light',{'resolved':True});cache.put('audit',reject)
    cache.observe(c['question'],c['state']['verified_claims'],hypothesis='new',workspace='new',attempts='new')
    assert cache.light and cache.audit==reject and not cache.audit_needed(True) and not decision(cache.light,cache.audit)
    cs2=copy.deepcopy(c['state']['verified_claims']);cs2[0]['statement']+=' changed'
    cache.observe(c['question'],cs2);assert cache.light is None and cache.audit is None and cache.audit_needed(True) and not cache.audit_needed(False)
    cache.put('audit',reject);cache.put('light',{'resolved':True});cache.observe(c['question']+' changed',cs2);assert cache.audit is None and cache.light is None
    cache.put('audit',reject);got=cache.get('audit');got['confirmed']=True;assert not cache.audit['confirmed']
    assert not decision(None,None)
    wr(TOP/'contract_checks.json',{'passed':True,'checks':['Q+Claim-only isolation including adversarial Hypothesis/history/Workspace/attempt/Light fields','L0 byte equality and L1 exact single addition','JSON literal in all system prompts','Audit boolean/schema/ref-range consistency','Q or Claim statement change invalidates both caches','Hypothesis/Workspace/attempt-only changes preserve both','Audit rejection reused; no same-state repeat-until-confirm','Cache values copied; failed output never STOP'],'production_controller_modified':False})
if __name__=='__main__':main()
