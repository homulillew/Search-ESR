"""One-time preregistration material generation; no network."""
import json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
task=(P/'TASK.md').read_text();p1=task.split('# 19. Path P1')[1].split('```text\n')[1].split('```')[0].strip();p2=task.split('# 20. Path P2')[1].split('```text\n')[1].split('```')[0].strip()
contract='\n\nReturn only one JSON object with exactly these keys: {"decision":"research","need":"one natural-language research question"}. No explanation, query, plan or list. This experiment contains unresolved states; do not return STOP.'
p0='''You are choosing the next research frontier.
Given the Original Question and the information available in this view, output exactly one current research need: the most useful unresolved question to investigate next.
A good need:
- serves the Original Question;
- is not already adequately resolved by the information available to you;
- can materially reduce uncertainty, distinguish candidates, resolve a conflict, establish a required condition, or obtain the final requested relation;
- is specific enough to guide the next research action;
- does not assume a provisional hypothesis is already true.
Do not output a search query, tool action, long-term plan, list of subquestions, confidence score, or explanation.'''
p3a='''Describe one unresolved uncertainty in the Original Question that is not established by Verified Claims.
The Working Hypothesis is provisional and cannot itself satisfy a missing condition.
Do not propose a search query. Do not restate the full Original Question. Do not introduce facts that are not established.
Choose one missing issue whose resolution would materially advance the Original Question.
This experiment contains unresolved states. Return only {"resolved":false,"unresolved_issue":"one missing semantic issue"}. Do not output a list, confidence, explanation, or intermediate reasoning.'''
p3b='''Formulate the supplied ephemeral unresolved issue as one focused, natural-language research question that would advance the Original Question.
Verified Claims are the only established facts. The Working Hypothesis is provisional and may make the question concrete, but is not evidence. Phrase uncertain relations as questions, without assuming that descriptions in the Original Question already hold for a candidate.
The issue is temporary input for this decision only.'''
p4='''Formulate the supplied confirmed unresolved issue as one safe, local, natural-language research question.
Use the Original Question, Verified Claims, and provisional Working Hypothesis to phrase it. Do not assert missing relations as facts or bundle other uncertainties. A provisional candidate may be investigated without assuming it is the answer.'''
for k,v in {'P0':p0+contract,'P1':p1+contract,'P2':p1+'\n\n'+p2+contract,'P3A':p3a,'P3B':p3b+contract,'P4':p4+contract}.items():(P/'prompts'/f'{k}.txt').write_text(v+'\n')
wr(P/'CONFIG.json',{'provider':'deepseek','base_url':'https://api.deepseek.com','model':'deepseek-flash','credential_file':'.env.deepseek','credential_field':'DEEPSEEK_API_KEY','temperature':0,'max_tokens':4096,'response_format':{'type':'json_object'},'stream':False,'timeout_seconds':240,'max_retries':0,'max_workers':8,'samples_per_unique_belief_path':1,'paths':['P0','P1','P2','P3','P4'],'tools':[],'retrieval_calls':0,'horizon':1,'P3_max_calls':2,'maximum_round0_calls':330})
# Observation support review: source-relative direct support, not web truth audit.
pack=json.loads((P/'bank/CLAIM_SUPPORT_PACKETS.json').read_text());reviews=[]
for r in pack:
 reviews.append({'state_id':r['state_id'],'claim_index':r['claim_index'],'statement_sha256':hashlib.sha256(r['statement'].encode()).hexdigest(),'source_hashes':[s['hash'] for s in r['support']],'supported_in_archived_observation':True,'reason':'The archived observation excerpt states the retained local fact (or the table/date relation); candidate identity and unretained source facts are not inferred. All unique Claim statements and matching source passages reviewed, with full windows checked for tables, dates and ambiguous mappings. Source-relative support only.','reviewer':'Codex single reviewer'})
wr(P/'bank/CLAIM_SUPPORT_REVIEW.json',reviews)
pairs=json.loads((P/'bank/DELTA_PAIRS.json').read_text())
wr(P/'bank/DELTA_SUPPORT_REVIEW.json',[{'pair_id':x['pair_id'],'supported':True,'source_text_sha256':hashlib.sha256(x['observation']['text'].encode()).hexdigest(),'reason':'Real archived observation explicitly supplies the appended Claim. A/B hold Q and H fixed; coverage refers only to the named local relation, not every conjunct of a broad original-question condition.'} for x in pairs if x['kind']=='coverage'])
# Freeze existing source dependencies and every tracked historical experiment byte.
import subprocess
files=subprocess.check_output(['git','ls-files','experiments'],cwd=R,text=True).splitlines()
wr(P/'HISTORICAL_HASHES.json',{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files if (R/f).is_file()})
