"""Capability boundaries for an experimental Q/R/C/H/T view.

No production object is migrated or modified. Source storage and receipts are
mechanical logs, not semantic state or model-assigned requirement coverage.
"""
import copy
import re
import unicodedata
from .common import digest

TAGS={'excerpt_mismatch','unsupported_inference','entity_binding_unproven','relation_change',
      'argument_change','temporal_scope_expansion','modality_expansion','quantifier_expansion',
      'conditional_scope_expansion','cross_source_composition','other'}
STRATEGIES={'IDENTIFY_CANDIDATE','VERIFY_RELATION','VERIFY_ATTRIBUTE','DISCRIMINATE_CANDIDATES',
            'LOCATE_SOURCE','LOCALIZE_IN_SOURCE','CROSS_CHECK_CONFLICT','OTHER'}
GAINS={'NEW_CLAIM','HYPOTHESIS_UPDATE','CANDIDATE_ELIMINATION','SOURCE_LOCALIZATION','CONFLICT_RESOLUTION'}

def nonempty(x): return isinstance(x,str) and bool(x.strip())
def fields(x,keys): return isinstance(x,dict) and set(x)==set(keys)

def validate_writer(v):
    return (fields(v,{'candidate_claims','followup_source_refs'})
            and isinstance(v['candidate_claims'],list) and isinstance(v['followup_source_refs'],list)
            and all(fields(c,{'statement','source_id','supporting_excerpt'})
                    and all(nonempty(c[k]) for k in c) for c in v['candidate_claims'])
            and all(fields(c,{'source_ref','reason'}) and all(nonempty(x) for x in c.values()) for c in v['followup_source_refs']))

def excerpt_check(candidate,source):
    return (candidate['source_id']==source['source_id'] and nonempty(candidate['supporting_excerpt'])
            and any(candidate['supporting_excerpt'] in source['source_observation'].get(k,'') for k in ('text','title')))

def validate_admission(v):
    return (fields(v,{'verdict','error_tags'}) and v['verdict'] in ('ADMIT','REJECT')
            and isinstance(v['error_tags'],list) and all(isinstance(x,str) and x in TAGS for x in v['error_tags'])
            and len(v['error_tags'])==len(set(v['error_tags']))
            and (not v['error_tags'] if v['verdict']=='ADMIT' else bool(v['error_tags'])))

def family(action):
    return (action['focus_requirement_id'],action['strategy'],tuple(sorted(action['focus_hypothesis_ids'])))

def validate_actor(v,view):
    if v=={'action':{'type':'REQUEST_CLOSURE_AUDIT'}}:return True
    if not fields(v,{'focus_requirement_id','strategy','focus_hypothesis_ids','one_useful_gap','probe','action','expected_gain'}):return False
    if v['focus_requirement_id'] not in {r['requirement_id'] for r in view['R']} or v['strategy'] not in STRATEGIES or v['expected_gain'] not in GAINS:return False
    ids=v['focus_hypothesis_ids']
    if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids) or len(ids)!=len(set(ids)) or not set(ids)<={h['hypothesis_id'] for h in view['H'] if h['status']=='active'}:return False
    if not nonempty(v['one_useful_gap']) or not nonempty(v['probe']):return False
    a=v['action']
    if not fields(a,{'type','query','source_ref','pattern'}):return False
    sources=view['TraceView']['available_sources']
    docs={s['doc_ref'] for s in sources if s.get('doc_ref')}
    windows={s['window_ref'] for s in sources if s.get('window_ref')}
    if a['type']=='SEARCH':return nonempty(a['query']) and len(a['query'])<=16000 and a['source_ref'] is None and a['pattern'] is None
    if a['type']=='FIND':return a['source_ref'] in docs and nonempty(a['query']) and len(a['query'])<=16000 and a['pattern'] is None
    if a['type']=='OPEN':return a['source_ref'] in windows and a['query'] is None and a['pattern'] in ('before','after','around')
    return False

def tool_action(v):
    a=v['action']
    if a['type']=='SEARCH':return 'search',{'query':a['query'],'k':5}
    if a['type']=='FIND':return 'find',{'doc_ref':a['source_ref'],'query':a['query']}
    if a['type']=='OPEN':return 'open',{'window_ref':a['source_ref'],'direction':a['pattern']}
    raise ValueError('Not an acquisition action')

def canonical_hypothesis(s):
    words=re.findall(r'[^\W_]+',unicodedata.normalize('NFKC',s).casefold())
    stop={'the','a','an','may','might','could','be','is','as','perhaps','possibly','likely','candidate',
          'person','player','author','relevant','referenced','described','answer','in','question','it','that','this'}
    return ' '.join(sorted(w for w in words if w not in stop))

def validate_closure(v,requirements,claims):
    # Task27 permits overall-only READY. Its implied all-covered judgment must
    # be scored, not silently rejected/repaired to hide an unsafe model closure.
    if v=={'overall':'READY_TO_ANSWER'}:return True
    if not fields(v,{'requirements','overall'}) or v['overall'] not in ('CONTINUE','READY_TO_ANSWER') or not isinstance(v['requirements'],list):return False
    expected={r['requirement_id'] for r in requirements};seen=[];known={c['claim_id'] for c in claims if c['status']=='active'}
    for r in v['requirements']:
        if not fields(r,{'requirement_id','status','supporting_claim_ids','missing'}):return False
        if r['requirement_id'] not in expected or r['status'] not in ('COVERED','OPEN'):return False
        ids=r['supporting_claim_ids']
        if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids) or len(ids)!=len(set(ids)) or not set(ids)<=known:return False
        if r['status']=='COVERED' and (not ids or r['missing'] is not None):return False
        if r['status']=='OPEN' and not nonempty(r['missing']):return False
        seen.append(r['requirement_id'])
    return len(seen)==len(set(seen)) and set(seen)==expected and (v['overall']=='READY_TO_ANSWER')==all(r['status']=='COVERED' for r in v['requirements'])

class MinimalLoopState:
    """A state owner accepts validated operations; model outputs never mutate it."""
    def __init__(self,Q,R):
        if not nonempty(Q) or not R:raise ValueError('Q and coarse requirements required')
        self._Q=Q;self._R=copy.deepcopy(R);self._anchor=digest([Q,R])
        self._C=[];self._H=[];self._T=[];self._sources={};self._pending=set();self._inspected=set()
        self._decisions={};self._used_admissions=set();self._closure=None;self._closure_count=0
        self._evidence_version=0

    def _invariant(self): assert digest([self._Q,self._R])==self._anchor

    def register_source(self,source):
        self._invariant();sid=source['source_id']
        if sid in self._sources and self._sources[sid]!=source:raise ValueError('Source identity reuse')
        self._sources[sid]=copy.deepcopy(source)

    def view(self):
        recent=self._T[-3:];streak=0;last_family=None
        for t in reversed(self._T):
            if t.get('kind')!='acquisition':continue
            f=tuple(t['probe_family'][:2])+ (tuple(t['probe_family'][2]),)
            if t['gain'] or (last_family is not None and f!=last_family):break
            last_family=f;streak+=1
        return copy.deepcopy({'Q':self._Q,'R':self._R,'C':self._C,'H':self._H,
            'TraceView':{'recent_actions':recent,'current_no_gain_streak':streak,
              'strategy_shift_required':streak>=2,'recent_probe_families':[t['probe_family'] for t in recent if 'probe_family' in t],
              'visited_source_refs':sorted(self._inspected),'pending_followup_sources':sorted(self._pending),
              'available_sources':[{'source_ref':sid,**{k:v for k,v in s.get('historical_refs',{}).items()},
                                    'title':s['source_observation'].get('title','')} for sid,s in self._sources.items()]}})

    def record_actor(self,output):
        self._invariant();v=self.view()
        if not validate_actor(output,v):raise ValueError('ACTOR_SCHEMA_OR_AUTHORITY_VIOLATION')
        if output=={'action':{'type':'REQUEST_CLOSURE_AUDIT'}}:return 'REQUEST_CLOSURE_AUDIT'
        if v['TraceView']['strategy_shift_required']:
            prior=next(t for t in reversed(self._T) if t.get('kind')=='acquisition')
            if list(family(output))[:2]==prior['probe_family'][:2] and list(family(output)[2])==prior['probe_family'][2]:
                raise ValueError('POLICY_VIOLATION')
        token=digest([len(self._decisions),output]);self._decisions[token]=copy.deepcopy(output)
        return token

    def admit(self,candidate,verdict,receipt_id):
        """Admission endpoint, called only by the Admission runner, never Actor/H."""
        self._invariant()
        if receipt_id in self._used_admissions:raise ValueError('Duplicate admission receipt')
        self._used_admissions.add(receipt_id)
        source=self._sources.get(candidate.get('source_id'))
        if source is None or not fields(candidate,{'statement','source_id','supporting_excerpt'}) or not all(nonempty(v) for v in candidate.values()):return None
        if not excerpt_check(candidate,source) or not validate_admission(verdict) or verdict['verdict']!='ADMIT':return None
        if any(c['statement']==candidate['statement'] and c['source_refs']==[candidate['source_id']] for c in self._C):return None
        cid=f'C{len(self._C)+1}'
        self._C.append({'claim_id':cid,'statement':candidate['statement'],'source_refs':[candidate['source_id']],
                        'supporting_excerpts':[candidate['supporting_excerpt']],'status':'active'})
        self._evidence_version+=1;self._closure=None
        return cid

    def hypothesis_operations(self,operations):
        self._invariant();trial=copy.deepcopy(self._H);changes=[]
        if not fields(operations,{'operations'}) or not isinstance(operations['operations'],list):raise ValueError('H schema')
        for op in operations['operations']:
            if not fields(op,{'type','hypothesis_id','statement','status','basis_refs'}) or op['status'] not in ('active','deprioritized','rejected'):raise ValueError('H schema')
            refs=op['basis_refs']
            if not isinstance(refs,list) or not refs or any(not isinstance(r,str) for r in refs) or not set(refs)<=self._sources.keys():raise ValueError('H basis must be observed')
            if op['type']=='ADD':
                if op['hypothesis_id'] is not None or not nonempty(op['statement']) or op['status']!='active':raise ValueError('H ADD')
                if not canonical_hypothesis(op['statement']):raise ValueError('H empty content')
                if any(canonical_hypothesis(h['statement'])==canonical_hypothesis(op['statement']) for h in trial):continue
                hid=f'H{len(trial)+1}';trial.append({'hypothesis_id':hid,'statement':op['statement'],'status':'active','basis_refs':list(refs)});changes.append(hid)
            elif op['type']=='UPDATE':
                old=next((h for h in trial if h['hypothesis_id']==op['hypothesis_id']),None)
                if old is None or op['statement'] is not None:raise ValueError('H UPDATE')
                if old['status']!=op['status']:
                    old.update(status=op['status'],basis_refs=list(refs));changes.append(old['hypothesis_id'])
            else:raise ValueError('H operation')
        if sum(h['status']=='active' for h in trial)>6:raise ValueError('Active H capacity')
        self._H=trial
        return changes

    def finish_acquisition(self,token,before,source_refs_seen=(),followups=()):
        self._invariant();a=self._decisions.pop(token)
        if not set(source_refs_seen)<=self._sources.keys() or not set(followups)<=self._sources.keys():raise ValueError('Unknown observation/followup')
        if a['action']['type'] in ('FIND','OPEN'):self._inspected.update(source_refs_seen);self._pending.difference_update(source_refs_seen)
        new_follow=set(followups)-self._pending-self._inspected;self._pending.update(new_follow)
        oldc={c['claim_id'] for c in before['C']};delta=[c['claim_id'] for c in self._C if c['claim_id'] not in oldc]
        oldh={h['hypothesis_id']:h for h in before['H']}
        hdelta=[h['hypothesis_id'] for h in self._H if h['hypothesis_id'] not in oldh or h['status']!=oldh[h['hypothesis_id']]['status']]
        hgain=any(h['hypothesis_id'] not in oldh or (oldh[h['hypothesis_id']]['status']=='active' and h['status'] in ('rejected','deprioritized')) for h in self._H)
        row={'kind':'acquisition','step':1+sum(t.get('kind')=='acquisition' for t in self._T),
             'focus_requirement_id':a['focus_requirement_id'],'strategy':a['strategy'],'probe':a['probe'],
             'query':a['action']['query'],'tool':a['action']['type'],'probe_family':[family(a)[0],family(a)[1],list(family(a)[2])],
             'source_refs_seen':list(source_refs_seen),'claim_delta_ids':delta,'hypothesis_delta_ids':hdelta,
             'new_followup_source_refs':sorted(new_follow),'gain':bool(delta or hgain or new_follow)}
        self._T.append(row);return copy.deepcopy(row)

    def closure_input(self):
        return copy.deepcopy({'Q':self._Q,'R':self._R,'C':[c for c in self._C if c['status']=='active']})

    def record_closure(self,result):
        self._invariant()
        if self._closure_count>=2:raise ValueError('Closure budget exhausted')
        self._closure_count+=1
        if not validate_closure(result,self._R,self._C):raise ValueError('Closure contract')
        self._closure={'result':copy.deepcopy(result),'evidence_version':self._evidence_version}
        if result['overall']=='CONTINUE':
            self._T.append({'kind':'closure_feedback','open_requirements':[{'requirement_id':r['requirement_id'],'missing':r['missing']} for r in result['requirements'] if r['status']=='OPEN']})

    def answer_input(self):
        self._invariant()
        if self._closure is None or self._closure['evidence_version']!=self._evidence_version or self._closure['result']['overall']!='READY_TO_ANSWER':raise ValueError('No valid current closure')
        active=[c for c in self._C if c['status']=='active']
        refs={r for c in active for r in c['source_refs']}
        return copy.deepcopy({'Q':self._Q,'C':active,'supporting_sources':{r:self._sources[r] for r in refs},'closure_result':self._closure['result']})
