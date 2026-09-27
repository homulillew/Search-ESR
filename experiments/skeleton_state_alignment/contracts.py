"""Fail-closed output contracts and symmetric, status-only E2 projection."""
from .common import STATUSES

def alignment_errors(value, nodes, claims):
    errors=[]
    if not isinstance(value,dict) or set(value)!={'requirements'}:
        return ['top_level_contract']
    rows=value['requirements']
    if not isinstance(rows,list):return ['requirements_not_list']
    expected={n['requirement_id'] for n in nodes}
    claim_ids={c['claim_id'] for c in claims}; seen=[]
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'requirement_id','status','supported_by'}:
            errors.append('node_contract');continue
        rid=row['requirement_id'];status=row['status'];refs=row['supported_by']
        if not isinstance(rid,str) or rid not in expected:errors.append('unknown_requirement_id')
        else:seen.append(rid)
        if not isinstance(status,str) or status not in STATUSES:errors.append('unknown_status')
        if not isinstance(refs,list) or any(not isinstance(r,str) for r in refs):
            errors.append('support_not_string_list');continue
        if len(refs)!=len(set(refs)):errors.append('duplicate_support')
        if not set(refs)<=claim_ids:errors.append('unknown_claim_id')
        if status=='unsupported' and refs:errors.append('unsupported_nonempty')
        if status in STATUSES[:2] and not refs:errors.append('supported_empty')
    if len(seen)!=len(set(seen)):errors.append('duplicate_requirement_id')
    if set(seen)!=expected or len(rows)!=len(expected):errors.append('requirement_id_coverage')
    return sorted(set(errors))

def selection_errors(value,nodes):
    if not isinstance(value,dict) or set(value)!={'selection'}:return ['top_level_contract']
    v=value['selection']
    return [] if isinstance(v,str) and v in {'STOP',*(n['requirement_id'] for n in nodes)} else ['invalid_requirement_id']

def validate_output(value,job):
    request=job.get('request')
    if request is None:return False
    import json
    payload=json.loads(request['messages'][1]['content'])
    if job['stage']=='e1_alignment':
        return not alignment_errors(value,payload['Task Skeleton'],payload['Verified Claims'])
    return not selection_errors(value,payload['Task Skeleton'])

def project_mask(value,nodes):
    """Caller validates the entire source mask first; never repair bad predictions."""
    rows={r['requirement_id']:r for r in value['requirements']}
    if set(rows)!={n['requirement_id'] for n in nodes}:raise ValueError('mask ID mismatch')
    return {'requirements':[{'requirement_id':n['requirement_id'],'status':rows[n['requirement_id']]['status']} for n in nodes]}

def residual(value):
    return [r['requirement_id'] for r in value['requirements'] if r['status']!='fully_supported']
