"""Model input boundaries. No historical obligations, reference labels or traces."""
import json
from .common import P, read, runtime_nodes
from .contracts import project_mask

def alignment_input(state,arm):
    return {'Original Question':state['question'],'Task Skeleton':runtime_nodes(str(state['qid']),arm),
            'Verified Claims':[{'claim_id':c['claim_id'],'statement':c['statement']} for c in state['claims']]}

def selection_input(state,mask):
    nodes=runtime_nodes(str(state['qid']),'A1')
    return {'Original Question':state['question'],'Task Skeleton':nodes,'Coverage Mask':project_mask(mask,nodes)}

def request_for(stage,payload):
    return {'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
      'messages':[{'role':'system','content':(P/'prompts'/f'{stage}.txt').read_text()},
                  {'role':'user','content':json.dumps(payload,ensure_ascii=False)}]}

def gold_mask(case_id):
    row=next(r for r in read(P/'e1_alignment/GOLD_MASKS.json') if r['case_id']==case_id and r['skeleton_arm']=='A1')
    return {'requirements':[{'requirement_id':rid,'status':v['status']} for rid,v in row['requirements'].items()]}
