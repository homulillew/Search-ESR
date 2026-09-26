from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'f1_state_sufficiency'
a=json.load(open(p/'semantic_review.json'))
for group in (p/'masked_brief.txt').read_text().split('\n\n'):
    lines=group.splitlines();new=[l for l in lines if l.startswith('M') and l.split()[0] not in a]
    if new:
        header=[l for l in lines if not l.startswith('M')]
        print('\n'.join(header+new)+'\n')
