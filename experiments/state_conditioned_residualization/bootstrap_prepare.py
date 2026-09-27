"""Evaluation-only accessibility audit and prefix registries; never model input."""
import re,sqlite3
from .common import *
BASE=ROOT/'experiments/belief_need_budget_locality_repair/acquisition/trajectories'
SOURCES={
 'G01':('F07',2,4),'G02':('F07',2,4),'G04':('F08',1,3),'G05':('F08',1,3),
 'G07':('F09',2,0),'G08':('F09',2,1),'G10':('F10',1,1),'G11':('F10',2,2),
 'G16':('F13',1,4),'G17':('F13',1,4),'G20':('F14',2,0)}
REASONS={
 'G01':'The paper identifies two named coauthors. This directly establishes the two-author facet for a concrete candidate, not the additional Baltic journal relation or final answer.',
 'G02':'The two named coauthors of the paper are new relative to C1 (a university profile). Additional Baltic journal publication remains unverified.',
 'G04':'Dated 2019 source explicitly says a games-company founder is married without children. New partial parent evidence, not evidence of a gift or target identity.',
 'G05':'The Ding source supplies a different candidate with the 2019 marital condition. Current Kwon candidate is not a fixed parent entity; no gift is established.',
 'G07':'A named musician, accidental death date and reported death city are new direct partial facts for the temporal/geographical parent. Aviation relation remains unestablished.',
 'G08':'The artist profile explicitly names partner Evita Manji, new relative to death-only C1. Interview/song relation remains unverified.',
 'G10':'Author biography names Alka Marwaha and her associate-professor post at University of Delhi, a concrete author/institution anchor for career verification. Does not establish the 2022 promotion or degree conjunction.',
 'G11':'The paper supplies author, title, journal and 2022 publication date/topic, new relative to the 2016 book claim. It can establish the later article facet and its six-year interval.',
 'G16':'Case presentation explicitly describes a 6-month history and the specified worsening walking/shoulder symptoms, plus a clinic in Pakistan. No nationality-to-report-country inference needed.',
 'G17':'The same concrete case is new relative to generic SPS Claims. It supplies the clinical history and explicit clinic location, not merely patient nationality.',
 'G20':'Steam lists the named DLC and 11 Oct 2016 release date, new relative to the generic EU4 context Claims. Base-game release interval needs additional evidence.'}
UNCERTAIN={
 'G13':'Historical discovery produced illustration/book background, telegraph history and Euler biography; no reviewed provenance establishes an actual book with the required illustration count/content. No exhaustive corpus absence claim.',
 'G14':'Euler birth fact is already known and does not establish a book-reference relation. Historical engineer biography/catalog candidates lack reviewed evidence connecting the required figures to this book.',
 'G15':'Historical trajectory admitted no Claim. Population portals and music lists do not demonstrate the precise 5.88% birthplace condition in reviewed provenance.',
 'G23':'Later Claim identifies the host university, not either teammate country. Team membership is already known; no reviewed provenance establishes their common country.',
 'G26':'Later Claim concerns North Transylvania, not letter composition or accession timing. March 5 is a transmission-memorandum date and cannot be promoted to composition date. No reviewed provenance establishes accession/date interval.'}
def main():
 states=read(P/'e0_reference/STATES.json');old={c['case_id']:c for c in read(ROOT/'experiments/dynamic_local_obligation/e0_reference/CASES.json')}
 db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
 refs=[];regs={}
 for s in states:
  if s['support_stratum']!='Z':continue
  cid=s['case_id'];snap=ROOT/old[cid]['snapshot'];snapshot=read(snap);respath=snap.with_name('RESULT.json');res=read(respath)
  tr=snapshot['transition'];round_n=0 if tr=='initial' else int(tr.split('_')[1])
  docs=set();windows=set()
  for dec in res['decisions']:
   if dec['step']<=round_n and dec['tool']:
    for w in dec['tool']['observations']:docs.add(w['doc_ref']);windows.add(w['window_ref'])
  regs[cid]={'documents':[d for d in res['registry']['documents'] if d['doc_ref'] in docs], 'windows':[w for w in res['registry']['windows'] if w['window_ref'] in windows]}
  row={'case_id':cid,'qid':s['qid'],'status':'accessible' if cid in SOURCES else 'uncertain','reason':REASONS.get(cid,UNCERTAIN.get(cid)),
   'audit_scope':'Bounded complete historical trajectory/provenance review plus corpus presence verification of positive sources; not exhaustive corpus search.',
   'snapshot':rel(snap),'snapshot_sha256':sha(snap),'trajectory':rel(respath),'trajectory_sha256':sha(respath),'source':None}
  if cid in SOURCES:
   fid,step,idx=SOURCES[cid];path=BASE/fid/f'decision{step}_tool.json';w=read(path)['observations'][idx]
   d=next(d for d in res['registry']['documents'] if d['doc_ref']==w['doc_ref']);txt,url=db.execute('SELECT text,url FROM documents WHERE docid=?',(d['docid'],)).fetchone()
   assert w['text'] in txt and hashlib.sha256(txt.encode()).hexdigest()==d['document_sha256']
   row['source']={'path':rel(path),'sha256':sha(path),'observation_index':idx,'docid':d['docid'],'document_sha256':d['document_sha256'],**w,'corpus_present':True}
  refs.append(row)
 db.close()
 # Placeholder was explicitly excluded from E1 freeze; replace it once at the E2 audit boundary.
 path=P/'e0_reference/ACCESSIBILITY_REFERENCE.json';assert read(path)['status']=='DEFERRED_UNTIL_P_GATE'
 path.write_text(json.dumps({'status':'COMPLETE_BEFORE_E2_CALLS','evaluation_only':True,'rows':refs,'counts':{'accessible':11,'uncertain':5,'known_unavailable':0},'accessible_qids':6},ensure_ascii=False,indent=2)+'\n')
 assert sum(r['status']=='accessible' for r in refs)==11 and len({r['qid'] for r in refs if r['status']=='accessible'})==6
 write(P/'e2_bootstrap/PREFIX_REGISTRIES.json',regs)
 write(P/'e2_bootstrap/ACCESSIBILITY_AUDIT.md','''# Oracle accessibility audit\n\nFrozen before E2 requests: 11 accessible states / 6 qids; 5 uncertain; 0 known unavailable. All 16 Z states retained. Historical future material is evaluation-only. Source paragraphs are verified against the corpus bytes, not assumed correct from Writer Claims. Accessibility means a new partial material fact or a concrete parent-relevant binding exists; it does not certify the final candidate or complete the parent. No exhaustive corpus absence inference is made.\n\nAudit limitations: this single reviewer knows historical trajectories. Unknowns are conservative bounded-provenance judgments, not corpus-unavailable labels. Positive status is fixed before query generation and cannot be changed based on retrieval.\n\nPrefix registries include every document/window actually emitted by the tool through the snapshot's round. A snapshot taken between Writer updates still follows a Search that exposed all five windows; no later-round window is imported. Registries are used only to preserve handles and compute repeat rates, not added to query prompts.\n''')
 print('accessible11 qids6 uncertain5; prefix registries saved')
if __name__=='__main__':main()
