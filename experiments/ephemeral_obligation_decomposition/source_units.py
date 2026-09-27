"""Mechanical verbatim address space; no semantic/gold splitting."""
import re
import unicodedata
def normalize(s): return ' '.join(unicodedata.normalize('NFC', s).split())
def split_units(q):
    # Bullet items (including inline '- X') remain intact. Other text splits at
    # semicolons and punctuation followed by whitespace then a capital/digit.
    bullets = [m.start() for m in re.finditer(r'(?<!\S)[-•]\s+(?=\S)', q)]
    limits = [0] + bullets + [len(q)]
    pieces = []
    for a, b in zip(limits, limits[1:]):
        if a == b: continue
        cuts = [a]
        if a not in bullets:
            for m in re.finditer(r';(?=\s)|[.!?][\"”\']?(?=\s+[A-Z0-9“\"])', q[a:b]):
                end = a + m.end()
                before = q[a:end]
                # Fixed orthographic exceptions; never derived from references.
                if re.search(r'\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|e\.g|i\.e)\.$', before): continue
                if re.search(r'(?:\b[A-Z]\.)+$', before): continue
                cuts.append(end)
        cuts.append(b)
        for lo, hi in zip(cuts, cuts[1:]):
            while lo < hi and q[lo].isspace(): lo += 1
            while hi > lo and q[hi-1].isspace(): hi -= 1
            if lo < hi: pieces.append((lo, hi))
    out = [dict(unit=f'Q{i+1}', start=a, end=b, text=q[a:b]) for i,(a,b) in enumerate(pieces)]
    assert ''.join(''.join(u['text'].split()) for u in out) == ''.join(q.split())
    return out
def span_check(span, units):
    if not isinstance(span, dict) or set(span) not in ({'unit','text'}, {'unit','text','occurrence'}): return {'valid':False, 'reason':'span_schema'}
    if not isinstance(span['text'], str) or not normalize(span['text']): return {'valid':False,'reason':'empty_span'}
    lookup = {u['unit']:u for u in units}
    if not isinstance(span['unit'], str) or span['unit'] not in lookup: return {'valid':False,'reason':'unknown_unit'}
    source, needle = normalize(lookup[span['unit']]['text']), normalize(span['text'])
    starts = [i for i in range(len(source)) if source.startswith(needle, i)]
    occ = span.get('occurrence', 1)
    if not starts: return {'valid':False,'reason':'not_exact_normalized_substring'}
    if len(starts)>1 and 'occurrence' not in span: return {'valid':False,'reason':'ambiguous_occurrence'}
    if type(occ) is not int or not 1<=occ<=len(starts): return {'valid':False,'reason':'invalid_occurrence'}
    return {'valid':True,'normalized_start':starts[occ-1],'normalized_end':starts[occ-1]+len(needle),'occurrences':len(starts)}
def validate(v, arm, units):
    errors=[]; spans=[]
    if not isinstance(v,dict) or set(v)!={'requirements'} or not isinstance(v['requirements'],list) or not 1<=len(v['requirements'])<=12:
        return {'schema_valid':False,'anchors_valid':False if arm!='D0' else None,'valid':False,'errors':['root_schema'],'spans':[]}
    keys={'D0':{'requirement'},'D1':{'requirement','source_spans'},'D2':{'source_spans'}}[arm]
    for i,r in enumerate(v['requirements']):
        if not isinstance(r,dict) or set(r)!=keys:
            errors.append(f'{i}:requirement_schema');continue
        if arm!='D2' and (not isinstance(r['requirement'],str) or not r['requirement'].strip()): errors.append(f'{i}:empty_requirement')
        if arm!='D0':
            if not isinstance(r['source_spans'],list) or not r['source_spans']:errors.append(f'{i}:empty_spans');continue
            for s in r['source_spans']:spans.append({'requirement_index':i,**span_check(s,units)})
    av=all(s['valid'] for s in spans) and bool(spans) if arm!='D0' else None
    return {'schema_valid':not errors,'anchors_valid':av,'valid':not errors and av is not False,'errors':errors,'spans':spans}
