from pathlib import Path
import json,sqlite3,hashlib
p=Path('/data/WSH/Search-ESR/experiments/query_initialization/single_entry/runs/20260918T072839.341275Z')
pool=json.loads((p/'review_pool.json').read_text())
db=sqlite3.connect('file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
# Post-run, pooled positive leads. Each quote supports a useful local entry,
# not the conjunction of the whole BC+ question or a final answer.
specs=[
('119','45549', [['built his first elevator probably in 236 BC','The Roman Colosseum, completed in 80 AD, had roughly 25 elevators'],['The first electric elevator was built by Werner von Siemens in 1880 in Germany.']], '识别机器的历史线索；不证明 Thanksgiving 事故。'),
('119','33431',[['The first passenger elevator got off to a slow start. Installed in 1857','Powered by a steam engine']], '乘客电梯与蒸汽动力的历史入口。'),
('127','30042',[['The Yidan Prize was founded in 2016 by Dr. Charles Chen Yidan, the core founder of Tencent Holdings Limited.']], '符合奖项设立年代和科技公司创办者关系的候选入口；尚未证明就是题目所指奖项。'),
('127','38298',[['Founder, Yidan Prize;','Core Founder, Tencent','Dr Charles CHEN Yidan established the Yidan Prize Foundation in 2016']], '支持奖项候选及创办者关系；未核实文章作者。'),
('416','41839',[['Machine Learning for High-Throughput Stress Phenotyping in Plants','Arti Singh1,Baskar Ganapathysubramanian2,Asheesh Kumar Singh3,Soumik Sarkar2'],['extracting patterns and features from this large corpus of data requires the use of machine learning (ML) tools to enable data assimilation and feature identification for stress phenotyping']], '论文主题、作者或摘要提供研究入口，不要求窗口包含致谢答案。'),
('416','96700',[['Hyperspectral band selection using genetic algorithm and support vector machines for early identification of charcoal rot disease in soybean stems']], '题名对应早期识别、光谱、监督学习与搜索算法；原文致谢另经核对。'),
('416','6722',[['Arti Singh','2013 Women in Triticum Early Career Award','post-doctoral fellow at the Semiarid Prairie Agricultural Research Centre']], '与论文第一作者对应的农业研究奖及履历入口。'),
('499','69120',[['Verity was erected in 2012','responded to the town\'s tourism drive']], '作品、展示年与旅游动机；没有核实额外 4500 游客。'),
('499','41589',[["this conception of artistic merit has found its ultimate expression, in the shape of the gigantic and arrestingly hideous Verity.", "economic ambitions of Ilfracombe's tourism officials"], ["This indifference to Verity's appearance", "significant impact to the tourism industry"]], '作品争议和当地旅游背景，未单独证明游客数量。'),
('499','8925',[['Hirst responded to North Devon Council\'s tourism drive for Ilfracombe','there was much argument and debate before Verity was allowed to visit'], ["An extra 5000 people visited within the first month of Verity's arrival."]], '作品争议及旅游背景；原文 5000 人满足题目的超过 4500 人。'),
('556','84412',[['Victor Mhleli Ntoni was born in Langa in 1947','In 1975 they performed a Royal Command Performance'], ['Victor Mhleli Ntoni', 'Born:\n1947', 'In 1975 they performed a Royal Command Performance']], '人物、成长地点及皇家演出形成后续搜索入口；不确认论文致谢人。'),
('598','20111',[['Afrigo Band is a musical band in Uganda.','The band was formed by a group of eight musicians'], ['Afrigo Band', 'In November 2015, the band celebrated its 40th anniversary with a sold-out concert at Hotel Africana, in Kampala.']], '八名创始成员或 2015 四十周年音乐会的乐队入口；不等于全部约束核实。'),
]
annotations=[]
for q,id,alternatives,note in specs:
 t=db.execute('select text from documents where docid=?',(id,)).fetchone()[0]
 assert id in pool[q]['documents']
 alts=[]
 for quotes in alternatives:
  proofs=[]
  for quote in quotes:
   assert quote in t,(id,quote)
   spans=[];start=0
   while (a:=t.find(quote,start))>=0:
    spans.append([a,a+len(quote)]);start=a+len(quote)
   proofs.append(dict(quote=quote,source_spans=spans))
  alts.append(proofs)
 annotations.append(dict(qid=q,docid=id,kind='question_supported_entry_lead',document_sha256=hashlib.sha256(t.encode()).hexdigest(),proof_alternatives=alts,note=note))
(p/'entry_evidence_annotations.json').write_text(json.dumps(dict(stage='post_run_pooled_manual_positive_leads',method='Limited positive annotations with exact source spans, not exhaustive qrels. Review was not blinded. Gold inspected offline only after all API generation; never sent to generator. Candidate leads do not prove intended identity or final answer.',pooled_qid_docs=sum(len(v['documents']) for v in pool.values()),positive_qid_docs=len(annotations),annotations=annotations),ensure_ascii=False,indent=2))
lookup={(a['qid'],a['docid']):a for a in annotations};rows=[]
for folder in sorted(p.glob('qid_*')):
 summary=json.loads((folder/'summary.json').read_text());h=json.loads((folder/'handoff.json').read_text());hits=[]
 for attempt in h['search_attempts']:
  for rank,w in enumerate(attempt['result'],1):
   a=lookup.get((summary['qid'],w['docid']))
   if a is None:continue
   assert a['document_sha256']==w['document_sha256']
   ranges=[[w['offset'],w['end_char']]]+([w['title_span']] if w['title_span'] else [])
   visible=any(all(any(any(lo<=x and y<=hi for lo,hi in ranges) for x,y in proof['source_spans']) for proof in option) for option in a['proof_alternatives'])
   hits.append(dict(docid=w['docid'],rank=rank,window_ref=w['window_ref'],visible=visible))
 rows.append(dict(session=folder.name,qid=summary['qid'],arm=summary['arm'],repeat=summary['repeat'],verified_lead_document=bool(hits),visible_lead_evidence=any(h['visible'] for h in hits),hits=hits))
aggs={a:{key:sum(r['arm']==a and bool(r[key]) for r in rows) for key in ['verified_lead_document','visible_lead_evidence']} for a in ['minimal','entry_v1']}
byqid={q:{a:dict(document=sum(r['qid']==q and r['arm']==a and r['verified_lead_document'] for r in rows),visible=sum(r['qid']==q and r['arm']==a and r['visible_lead_evidence'] for r in rows)) for a in ['minimal','entry_v1']} for q in sorted(pool,key=int)}
(p/'entry_evidence_recheck.json').write_text(json.dumps(dict(method='Post-run positive-lead lower bounds, not recall, accuracy or full relevance assessment. Zero means no annotated lead, not irrelevant results. Each arm has 40 attempts. Candidate identity is not confirmed by one matching clue.',aggregates=aggs,by_qid=byqid,sessions=rows),ensure_ascii=False,indent=2))
print(json.dumps(dict(aggregates=aggs,by_qid={q:r for q,r in byqid.items() if any(x['document'] for x in r.values())}),ensure_ascii=False,indent=2))
