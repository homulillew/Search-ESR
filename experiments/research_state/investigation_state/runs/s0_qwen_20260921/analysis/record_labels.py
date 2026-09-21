"""Apply individually reviewed full-response judgments before pairing. No API calls."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review'
def read(p):return json.loads(p.read_text())
prefix={c['card_id']:c for c in map(json.loads,(v/'prefix_assessment.jsonl').read_text().splitlines())}
judgments=read(r/'analysis/manual_judgments.json');rows=[]
for c in map(json.loads,(v/'cards.jsonl').read_text().splitlines()):
 j=judgments[c['card_id']];c['labels']={k:'not_applicable' for k in c['labels']}
 c['labels'].update(j['labels']);c['labels']['regression']='unknown';c['analysis']=j['analysis']
 for k in c['labels']:c['label_evidence'][k]={'refs':j.get('refs',['question','task','n1','n2','n3']),'notes':'待配对后评价。' if k=='regression' else j['analysis']}
 for k in ['permitted_next_actions_before_output','original_constraints','evidence_boundaries']:c[k]=prefix[c['card_id']][k]
 rows.append(c)
(v/'annotations_first_pass.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
(v/'first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'private_key_opened_this_run':False,'evaluator':'single Codex-assisted; prior cases known, not blind or independent human gold','scope':'Full delivered content and every tool proposal; no private reasoning substituted. Source attribution N/A when no source identity assertion, not automatic yes.','sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
