from pathlib import Path
import json
p=Path('/data/WSH/Search-ESR/experiments/query_initialization/single_entry/runs/20260918T072839.341275Z')
issues={}
def add(key, **kw): issues.setdefault(key,{}).update(kw)
add('1172__entry_v1__r1',errors=['原题限定上映于 2008–2011（含端点），query 写成 released 2008，无依据收窄为精确年份。'],missing_refs=['q2'])
for a in ['entry_v1','minimal']:
 for r in [1,2]:
  if a=='minimal' or r==2:
   add(f'119__{a}__r{r}',missing_refs=['q1','q2'] if a=='entry_v1' else [])
add('116__entry_v1__r1',ambiguities=['to two immigrants who died ... 的 who 可错误指向父母，而原题死亡信息属于目标人物。'],missing_refs=['q3'])
add('116__entry_v1__r2',ambiguities=['to two immigrants who won an Oscar ... 的关系从句可错误附着于父母；原题所有后续经历属于目标人物。'])
add('116__minimal__r2',missing_refs=['q1'])
for r in [1,2]:
 add(f'127__entry_v1__r{r}',ambiguities=['创办科技公司的个人与服役作者之间缺少清楚的从句边界，served as military officer 容易错接主体。'])
add('67__entry_v1__r1',missing_refs=['q1'])
add('81__entry_v1__r1',missing_refs=['q4'])
add('81__entry_v1__r2',ambiguities=['between 2013 and 2023 未保留原题 after/before 的开区间。'],missing_refs=['q4'])
add('265__minimal__r1',ambiguities=['between 1969 and 1981 未保留原题 after/before 的开区间。'])
add('265__minimal__r2',missing_refs=['q3','q4','q8','q9'])
add('499__entry_v1__r2',missing_refs=['q4'])
add('499__minimal__r2',missing_refs=['q2'])
for r in [1,2]: add(f'556__entry_v1__r{r}',missing_refs=['q3'])
for a in ['entry_v1','minimal']:
 add(f'611__{a}__r2',ambiguities=['没有明确 debut、final match 均限定同一赛制，容易解读为整个生涯的首末场。'])
for r in [1,2]:add(f'650__entry_v1__r{r}',ambiguities=['两个 between 区间都省略 exclusive at the endpoints。'])
add('650__minimal__r1',ambiguities=['2001-2009 和 1995-2005 都未表达原题排除端点。'])
for a,r in [('entry_v1',1),('minimal',1),('minimal',2)]:
 add(f'694__{a}__r{r}',ambiguities=['Best Individual Sport Coverage 2016 article 的 2016 可能附着于奖项，原题限定文章年份。'])
add('1172__minimal__r1',missing_refs=['q2','q16','q18'])
add('1172__minimal__r2',missing_refs=['q2'])
add('416__entry_v1__r2',ambiguities=['以 AND 拼接两篇不同论文的描述，没有表达共同作者关系；不能清楚确定主搜索对象。'],entry_notes=['并置两个来源，单入口不够明确。'])
add('416__minimal__r1',ambiguities=['将第二篇论文的 neural network 与最后一篇的 supervised learning/search algorithm 拼成一个 paper 的关键词串，未保留论文间的区别。'])
for a,r in [('entry_v1',1),('entry_v1',2),('minimal',2)]:
 add(f'1196__{a}__r{r}',ambiguities=['about a decade ago 丢失原题 As of 2023 的时间锚点，独立 query 的相对日期不清。'])
add('950__minimal__r1',missing_refs=['q2'])
rows=[]
for folder in sorted(p.glob('qid_*')):
 h=json.loads((folder/'handoff.json').read_text());s=json.loads((folder/'summary.json').read_text());i=h['plan']['intents'][0];issue=issues.get(folder.name.removeprefix('qid_'),{})
 rows.append(dict(session=folder.name,qid=s['qid'],arm=s['arm'],repeat=s['repeat'],question=h['question']['text'],query=i['query'],basis_refs=i['basis_refs'],explicit_errors=issue.get('errors',[]),ambiguities=issue.get('ambiguities',[]),missing_basis_refs=issue.get('missing_refs',[]),entry_notes=issue.get('entry_notes',[])))
aggs={a:dict(attempts=sum(s['arm']==a for s in rows),explicit_error_sessions=sum(s['arm']==a and bool(s['explicit_errors']) for s in rows),ambiguous_sessions=sum(s['arm']==a and bool(s['ambiguities']) for s in rows),missing_basis_sessions=sum(s['arm']==a and bool(s['missing_basis_refs']) for s in rows)) for a in ['minimal','entry_v1']}
(p/'semantic_review.json').write_text(json.dumps(dict(method='Post-run manual review by coding assistant; not blinded, no external judge. Definite errors, interpretive ambiguities and provenance gaps are separate. All 80 queries compared to full original questions; no-error label is not a guarantee of semantic correctness.',aggregates=aggs,sessions=rows),ensure_ascii=False,indent=2))
print(json.dumps(aggs,indent=2))
