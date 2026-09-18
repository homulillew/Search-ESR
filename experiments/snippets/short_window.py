"""Build a query-centered view strictly inside a frozen parent block."""
import hashlib
from experiments.snippets.window import WindowSelector


def shorten(query, parent, cap, tokenizer):
    result=dict(parent)
    parent_id=result.pop('chunk_id',None)
    if parent['tokens']<=cap:
        result.update(method='unchanged_fits',anchor=None)
    else:
        selector=WindowSelector(tokenizer,budget=cap,overlap=0)
        units=selector.units(parent_id or 'fallback',parent['text'])
        view=selector.observe(query,parent['text'],units)
        result.update(text=view['text'],tokens=view['tokens'],
                      start_char=parent['start_char']+view['start_char'],
                      end_char=parent['start_char']+view['end_char'],
                      method='local_anchor_window',selection=view['selection'],stop=view['stop'],
                      anchor=view['anchor'])
        if result['anchor']:
            result['anchor']=dict(result['anchor'])
            for k in ('start_char','end_char'):result['anchor'][k]+=parent['start_char']
    result.update(parent_chunk_id=parent_id,allocated_cap=cap)
    result['view_id']=hashlib.sha256(f"short-v1:{parent_id}:{result['start_char']}:{result['end_char']}".encode()).hexdigest()[:24]
    return result
