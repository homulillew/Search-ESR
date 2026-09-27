"""V2 public evidence projection and ref schema; all semantic prompts remain original."""
import copy
from pathlib import Path
import jsonschema
from .. import harness as original
from ..harness import ROOT,read,save,digest,file_hash,canonical

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CLAIM_ROLES={'a0_current_reader','a1_no_c_reader','a2_evidence_formulator','g1_evidence_inventory'}
E1_ROLES={'a0_current_reader','a1_no_c_reader','a2_selector','a2_evidence_formulator'}
FIELDS=('window_ref','doc_ref','title','url','text')

def semantic_evidence_view(window):
    result={k:copy.deepcopy(window[k]) for k in FIELDS}
    if 'date' in window:result['date']=copy.deepcopy(window['date'])
    return result

def project_payload(role,payload):
    allowed={
        'a0_current_reader':{'OneGap','C','Observation'},
        'a1_no_c_reader':{'OneGap','Observation'},
        'a2_selector':{'OneGap','C','Observation'},
        'a2_evidence_formulator':{'Evidence'},
        'g1_evidence_inventory':{'Evidence'},
        'g0_current_grounding':{'candidate','Evidence'},
        'g1_candidate_coverage':{'candidate','SourceCommitmentInventory'},
    }
    if set(payload)!=allowed[role]:raise ValueError('unexpected role input domain')
    result=copy.deepcopy(payload)
    for key in ['Observation','Evidence']:
        if key in result:result[key]=[semantic_evidence_view(w) for w in result[key]]
    return result

def ref_array(schema,role):
    field='facts' if role=='g1_evidence_inventory' else 'findings'
    return schema['properties'][field]['items']['properties']['evidence_refs']

def schema_for(role,payload=None):
    schema=read(HERE/'schemas'/f'{role}.json')
    if role in CLAIM_ROLES and payload is not None:
        ws=payload.get('Observation',payload.get('Evidence',[]))
        refs=sorted({w['window_ref'] for w in ws})
        # Enum is based only on public handles; no label or private ID enters it.
        items=ref_array(schema,role)['items']
        if refs:items['enum']=refs
        else:items['not']={}  # no legal ref if no evidence; empty findings remains valid
    return schema

def request(role,payload,config):
    public=project_payload(role,payload)
    data=original.request(role,public,config)
    prompt=(BASE/'prompts'/f'{role}.txt').read_text()
    data['messages'][0]['content']=prompt+'\nReturn one JSON object matching this schema:\n'+canonical(schema_for(role,public))
    return data

def validate_membership(role,value,payload):
    # Original check still independently rejects W-shaped but unobserved handles.
    return original.validate(role,value,payload)

def validate(role,value,payload):
    jsonschema.Draft202012Validator(schema_for(role,payload)).validate(value)
    return validate_membership(role,value,payload)
