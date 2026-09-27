"""Offline guard for the JSON-mode requirement observed in this batch's HTTP400.

This does not mutate frozen requests, load credentials, or send requests.
Integrate it before freezing any separately authorized future execution.
"""
from experiments.need_premise_audit.common import P, read

def check(request):
    if request.get('response_format',{}).get('type')=='json_object':
        text='\n'.join(m.get('content','') for m in request.get('messages',[]) if isinstance(m.get('content',''),str))
        if 'json' not in text.lower():
            raise ValueError('JSON mode requires json in prompt text according to the archived provider HTTP400; reject before network.')
    return True

if __name__=='__main__':
    jobs=read(P/'e1_checker/SCHEDULE.json')
    rejected=[]
    for job in jobs:
        try:check(job['request'])
        except ValueError:rejected.append(job['id'])
    print({'scheduled':len(jobs),'would_block_before_network':len(rejected),'all_blocked_are_V0':all(x.startswith('V0__') for x in rejected)})
