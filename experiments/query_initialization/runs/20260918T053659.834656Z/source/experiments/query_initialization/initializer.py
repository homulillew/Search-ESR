"""Initial-query generation and deterministic validation, isolated from production."""
import json
import re
import unicodedata
from pathlib import Path
from llm_chat.agent import AGENT_PROMPT, TOOLS

PROMPT_FILE = Path(__file__).with_name('INITIALIZER_PROMPT.md')
REPAIR = ('The previous output did not satisfy the output contract. Correct the listed validation errors using only the original question. '
          'Do not introduce candidate guesses or new factual restrictions. Return only the corrected JSON object. '
          'A missing second defensible direction may remain omitted.')


def prompt():
    return re.search(r'```text\n(.*?)\n```', PROMPT_FILE.read_text(), re.S).group(1)


def normalize(query):
    return ' '.join(unicodedata.normalize('NFKC', query).casefold().split())


def validate(value, question, count):
    errors=[]
    if not isinstance(value,dict) or set(value)!={'directions'}:
        return ['Root must have exactly the field directions']
    ds=value['directions']
    if not isinstance(ds,list) or len(ds)>count:
        return [f'directions must be a list with at most {count} items']
    seen=set()
    for i,d in enumerate(ds):
        prefix=f'directions[{i}]'
        if not isinstance(d,dict) or set(d)!={'goal','source_clues','query'}:
            errors.append(prefix+' must have exactly goal, source_clues, query');continue
        for field,limit in [('goal',256),('query',512)]:
            if not isinstance(d[field],str) or not d[field].strip() or len(d[field])>limit:
                errors.append(f'{prefix}.{field} must be nonempty text <= {limit} characters')
        if isinstance(d['query'],str):
            norm=normalize(d['query'])
            if norm in seen:errors.append(prefix+'.query duplicates another query')
            seen.add(norm)
        cs=d['source_clues']
        if not isinstance(cs,list) or not 1<=len(cs)<=3:
            errors.append(prefix+'.source_clues must contain 1 to 3 exact quotations');continue
        for j,c in enumerate(cs):
            if not isinstance(c,str) or not c.strip() or c not in question:
                errors.append(f'{prefix}.source_clues[{j}] is not an exact nonempty substring of the original question')
    return errors


def parse(content, question, count):
    try:value=json.loads(content)
    except (TypeError,ValueError):return None,['Response is not a valid JSON object']
    return value,validate(value,question,count)


def checked_response(response):
    if not response.choices:raise ValueError('API returned no choices')
    choice=response.choices[0]
    if choice.finish_reason not in {'stop','tool_calls'}:raise ValueError('Incomplete API response: '+str(choice.finish_reason))
    return choice.message


def generate(client,config,question,arm):
    count=2 if arm=='C' else 1
    common=dict(model=config.model,stream=False,max_tokens=1536,**config.request_options())
    if arm=='A':
        r=client.chat.completions.create(**common,messages=[{'role':'system','content':config.system_prompt+'\n\n'+AGENT_PROMPT},{'role':'user','content':question}],tools=TOOLS,tool_choice='auto')
        m=checked_response(r);calls=m.tool_calls or []
        first=next((c for c in calls if c.function.name=='search'),None)
        if first is None:return dict(status='no_search',directions=[],repairs=0,initial_valid=False,original_tool_calls=len(calls))
        try:args=json.loads(first.function.arguments)
        except (TypeError,ValueError):return dict(status='invalid',directions=[],repairs=0,initial_valid=False,errors=['Invalid first search arguments'])
        q=args.get('query') if isinstance(args,dict) else None
        if not isinstance(q,str) or not q.strip() or len(q)>16000:
            return dict(status='invalid',directions=[],repairs=0,initial_valid=False,errors=['Invalid first search query'])
        return dict(status='valid',directions=[dict(goal=None,source_clues=[],query=q)],repairs=0,initial_valid=True,original_k=args.get('k',5),original_tool_calls=len(calls))
    messages=[{'role':'system','content':prompt()},{'role':'user','content':json.dumps(dict(question=question,requested_directions=count),ensure_ascii=False)}]
    m=checked_response(client.chat.completions.create(**common,messages=messages))
    value,errors=parse(m.content,question,count);initial_valid=not errors;initial_errors=list(errors);repairs=0
    if errors:
        repairs=1
        messages += [{'role':'assistant','content':m.content or ''},{'role':'user','content':json.dumps(dict(instruction=REPAIR,validation_errors=errors),ensure_ascii=False)}]
        m=checked_response(client.chat.completions.create(**common,messages=messages));value,errors=parse(m.content,question,count)
    if errors:return dict(status='invalid',directions=[],repairs=repairs,initial_valid=initial_valid,initial_errors=initial_errors,errors=errors)
    ds=value['directions'];status='no_direction' if not ds else 'underfilled' if len(ds)<count else 'valid'
    for d in ds:
        d['clue_locations']=[[match.start() for match in re.finditer(re.escape(c),question)] for c in d['source_clues']]
        d['long_query_warning']=len(d['query'])>240
    return dict(status=status,directions=ds,repairs=repairs,initial_valid=initial_valid,initial_errors=initial_errors)
