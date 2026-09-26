"""Exact response contracts. No wrapper normalization or fallback mappings."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from jsonschema import Draft202012Validator
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
def schema(kind):
    filename={'research_actor':'ACTION_RESPONSE_SCHEMA.json','goal_reviewer':'GOAL_RESPONSE_SCHEMA.json','state_updater':'UPDATER_RESPONSE_SCHEMA.json'}[kind]
    folder=STUDY/'research_decision_v2' if kind=='research_actor' else HERE
    return json.loads((folder/filename).read_text())

def validate_object(obj,kind,workspace=None):
    Draft202012Validator(schema(kind)).validate(obj)
    if kind=='research_actor' and obj['decision']=='act':
        if not obj['gap'].strip():raise ValueError('empty_gap')
        for a in obj['actions']:
            if 'query' in a and not a['query'].strip():raise ValueError('empty_query')
        if workspace is not None:
            docs={d['doc_ref'] for d in workspace['known_documents']}
            wins={w['window_ref'] for w in workspace['observed_windows']}
            for a in obj['actions']:
                if a['tool']=='find' and a['doc_ref'] not in docs:raise ValueError('unknown_prebatch_document')
                if a['tool']=='open' and a['window_ref'] not in wins:raise ValueError('unknown_prebatch_window')
    if kind=='goal_reviewer' and obj['resolved']!=(not obj['residual'].strip()):raise ValueError('goal_inconsistent')
    if kind=='state_updater':
        if any(not c.strip() for c in obj['claims_to_add']):raise ValueError('empty_claim')
        if obj['hypothesis_update']['action']=='set' and not obj['hypothesis_update']['statement'].strip():raise ValueError('empty_hypothesis')
    return obj

def parse(raw,kind,workspace=None):
    if raw['choices'][0]['finish_reason']!='stop':raise ValueError('abnormal_finish')
    return validate_object(json.loads(raw['choices'][0]['message']['content']),kind,workspace)

def build():
    actions=[]
    for t in SEARCH_FIND_TOOLS:
        f=t['function'];s=copy.deepcopy(f['parameters'])
        s['properties']={'tool':{'const':f['name']},**s['properties']};s['required']=['tool']+s['required']
        if f['name']=='search':s['required'].append('k')
        actions.append(s)
    stop={'type':'object','properties':{'decision':{'const':'stop'},'gap':{'const':''},'actions':{'type':'array','maxItems':0}},'required':['decision','gap','actions'],'additionalProperties':False}
    act={'type':'object','properties':{'decision':{'const':'act'},'gap':{'type':'string','minLength':1,'pattern':'\\S'},'actions':{'type':'array','minItems':1,'maxItems':2,'items':{'oneOf':actions}}},'required':['decision','gap','actions'],'additionalProperties':False}
    actor={'$schema':'https://json-schema.org/draft/2020-12/schema','oneOf':[stop,act]}
    goal={'type':'object','properties':{'resolved':{'type':'boolean'},'residual':{'type':'string'}},'required':['resolved','residual'],'additionalProperties':False}
    updater={'type':'object','properties':{'claims_to_add':{'type':'array','maxItems':2,'items':{'type':'string','minLength':1,'pattern':'\\S'}},'hypothesis_update':{'type':'object','properties':{'action':{'enum':['keep','set','clear']},'statement':{'type':'string'}},'required':['action','statement'],'additionalProperties':False}},'required':['claims_to_add','hypothesis_update'],'additionalProperties':False}
    for path,obj in [(STUDY/'research_decision_v2/ACTION_RESPONSE_SCHEMA.json',actor),(HERE/'GOAL_RESPONSE_SCHEMA.json',goal),(HERE/'UPDATER_RESPONSE_SCHEMA.json',updater)]:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    examples=[
     {'decision':'act','gap':'Which observatory is described by the remaining historical clues?','actions':[{'tool':'search','query':'observatory mountain founded historical measurements','k':5}]},
     {'decision':'act','gap':'When was the instrument installed at the candidate observatory?','actions':[{'tool':'find','doc_ref':'D3','query':'instrument installation year'}]},
     {'decision':'act','gap':'What does the surrounding passage say about the instrument installation?','actions':[{'tool':'open','window_ref':'W1','direction':'around'}]},
     {'decision':'act','gap':'Which records can establish the observatory instrument history?','actions':[{'tool':'search','query':'observatory instrument installation history','k':5},{'tool':'search','query':'observatory annual report equipment commissioning','k':5}]},
     {'decision':'stop','gap':'','actions':[]}]
    contract='''\n\nEXACT RESPONSE SERIALIZATION CONTRACT (examples illustrate formatting only)
The complete response must be one JSON object matching the schema below.
Use exactly the lowercase action discriminator "tool". Never use "type", "name", or an "arguments" wrapper for an action.
Search requires exactly tool, query, k. k must be an integer from 1 to 10 (use 5 when choosing the default).
Find requires exactly tool, doc_ref, query. Open requires exactly tool, window_ref, direction; direction is before, after, or around.
No additional keys are allowed. Do not emit Markdown fences or text outside JSON.
STOP means decision=stop, gap="", actions=[]. ACT means a nonempty gap and one or two actions.
All D#/W# arguments must already exist in the supplied workspace before either action executes. A Search→Find batch referencing a new document from that Search is invalid. Two independent searches or inspections of two already available documents are legal.
The Tool schema in the input describes available tools and their parameter semantics. Your response uses the flat objects in THIS contract, not an OpenAI function-call wrapper.

Full JSON Schema:
'''+json.dumps(actor,ensure_ascii=False,indent=2)+'\n\nComplete formatting examples (D3 and W1 are hypothetical existing handles, not targets for this task):\n'+ '\n\n'.join(json.dumps(e,ensure_ascii=False,indent=2) for e in examples)+'\n'
    (HERE/'actor_contract.md').write_text(contract)
    (HERE/'research_actor.md').write_text((STUDY/'prompts/research_actor.md').read_text()+contract)
    # Goal prompt is reused verbatim, not rewritten. Updater adds serialization-only examples.
    u='\n\nExact JSON examples for the existing output contract (format only):\n'
    for h in [{'action':'keep','statement':''},{'action':'set','statement':'The candidate observatory may be the one described.'},{'action':'clear','statement':''}]:
        u+=json.dumps({'claims_to_add':[],'hypothesis_update':h},indent=2)+'\n'
    u+='Required keys and allowed values are specified by this schema; no additional keys or surrounding text:\n'+json.dumps(updater,indent=2)+'\n'
    (HERE/'state_updater.md').write_text((STUDY/'prompts/state_updater.md').read_text()+u)

if __name__=='__main__':build()
