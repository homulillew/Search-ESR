"""Question-only Oracle construction; must run/commit before opening state bank.

Only the prior question bank, Q-only reference and fixed replicate-1 D1/D2
outputs are read. No historical Claims or Gold Obligation are accessed here.
"""
from .common import *
from experiments.ephemeral_obligation_decomposition.source_units import span_check
# Each entry: descriptive label (non-authoritative), exact original spans.
ORACLE={
'122':[
 ('Person birth condition',[(1,'a person who was born between 1948 and 1952 in a place')]),
 ('Birthplace demographic condition',[(1,'a place in which the population increased by 5.88% between 2010 and 2020 according to one official website of the country in which it is located.')]),
 ('Presentation episode',[(2,None)]),('Recording hiatus',[(3,None)]),
 ('Requested death year',[(1,"I'm looking for the year of death of a person")])],
'169':[
 ('Charity and first-name relation',[(1,None),(2,None)]),
 ('Death city and aviation-site relation',[(3,None)]),
 ('Accident-to-death interval',[(4,None)]),
 ('Partner interview and song-reference relation',[(5,None)]),
 ('Song-title form',[(6,None)]),('Requested song title',[(7,None)])],
'228':[
 ('Founder-company-game identification',[(1,'A specific person who is the founder of a company whose online video games division released a video game in a specific year between 2000 and 2010, both years inclusive, which, at least until 2019, was considered one of the top-earning games of all time')]),
 ('Founder education',[(1,'graduated from a university founded between 1930 and 1970, both years inclusive.')]),
 ('Marriage and childlessness',[(2,'This person and their spouse, who, up to 2019, had no children from the marriage')]),
 ('Gift-funded building',[(2,'This person and their spouse'),(2,'made a foundational gift for the construction of a building that was part of a larger complex.')]),
 ('Planned opening and affiliation',[(3,None)]),
 ('Requested building university',[(4,None)])],
'261':[
 ('Target-paper writing interval',[(3,None)]),
 ('Target-paper author count',[(4,'Two people wrote it.')]),
 ('Author and another JBSE paper',[(4,'One has another research paper in the Journal of Baltic Science Education written between 2016 and 2023.')]),
 ('Author and Harran affiliation',[(5,None)]),
 ('Target-paper table count',[(6,'There are six tables in this research paper in total and each of them has specific information.')]),
 ('Table emotion percentage',[(6,'In one of the tables, one of the emotions is at 13.53 percent.')]),
 ('Requested paper name',[(7,None)])],
'538':[
 ('Book illustration and object content',[(1,'a book that contains between 130 and 140 illustrations and descriptions of various objects, including the telephone and telegraph')]),
 ('Alternative rust-cleaning method',[(2,None)]),
 ('Book and referenced engineer',[(3,'it references'),(3,'a mechanical engineer born in the early 1800s')]),
 ('Book and referenced scientist',[(3,'it references'),(3,'a scientist whose father was a poet')]),
 ('Book and referenced L. E. figure',[(3,'it references'),(3,'a well-known figure born in the early 1700s in a central European country, with the initials L. E.')]),
 ('Requested book title',[(1,'As of December, 2023, what is the title of a book')])],
'637':[
 ('Two reports and their dates',[(1,None)]),('Shared disorder relation',[(2,None)]),
 ('First-case country condition',[(3,None)]),('First-case clinical course',[(4,None)]),
 ('Second-case biopsy and symptoms',[(5,None)]),('Second-case childhood course',[(6,None)]),
 ('Requested scientific disorder name',[(7,None)])],
'843':[
 ('DLC and game release interval',[(1,None)]),
 ('Game and postcolonialism thesis',[(2,"A Master's thesis was written on the theme of postcolonialism in this game for an American University in 2023")]),
 ('Thesis advisor and credentials',[(2,'that was advised by an academic who completed two degrees at a California University and published a 2020 monograph on the subject of video games.')]),
 ('DLC mechanics',[(3,None)]),('Requested third designer',[(4,None)])],
'922':[
 ('Letter identity and writing period',[(1,'A letter was written in the first half of the twentieth century from a ruler of one country to another')]),
 ('Courier and recipient-given nickname',[(1,'delivered by an official who was nicknamed after a body part by its recipient.')]),
 ('Letter-to-accession interval',[(2,None)]),('Letter and regained-region statement',[(3,None)]),
 ('Requested region name',[(4,None)])],
'971':[
 ('Author career and degree university',[(1,None)]),
 ('Author PhD and advisor relation',[(2,'They had pursued their PhD abroad at a Canadian university under the guidance of an Iranian professor')]),
 ('Advisor background',[(2,'who dreamt of becoming a writer but switched to mathematics at the end of high school and got their doctorate in Minnesota.')]),
 ('Author book and PhD interval',[(3,'The author published a book connecting mathematics to an ancient technique for liberation 20 years after completing their PhD')]),
 ('Later related journal article',[(3,'then published a journal article on a similar topic six years after publishing the book.')]),
 ('Requested article title',[(4,None)])],
'1259':[
 ('Annual university programming final',[(1,None)]),('Winning team and Australian coder',[(2,None)]),
 ('Coder medal sequence',[(3,None)]),('Other teammates country relation',[(4,None)]),
 ('Requested winning year',[(5,'Could you tell me the year associated with the competition title')]),
 ('Requested host university',[(5,'and the name of the host university for the year he won that title?')])]
}
def main():
 qs=questions();refs=read(PREV/'e0_reference/REFERENCE_TASK_STRUCTURE.json');out={}
 for q,entries in ORACLE.items():
  nodes=[];units=qs[q]['source_units'];assert refs[q]['question_sha256']==qs[q]['question_sha256']
  for i,(label,anchors) in enumerate(entries):
   ss=[{'unit':f'Q{u}','text':units[u-1]['text'] if text is None else text} for u,text in anchors]
   assert all(span_check(s,units)['valid'] for s in ss),(q,label)
   nodes.append({'requirement_id':f'R{i+1}','label':label,'source_spans':ss})
  out[q]={'qid':q,'question_sha256':qs[q]['question_sha256'],'requirements':nodes}
 write(P/'e0_addressability/ORACLE_RUNTIME_SKELETON.json',out)
 sources={}
 for arm in ('D1','D2'):
  output={}
  for q,c in qs.items():
   src=PREV/'e1_development/calls'/f'{arm}__Q{q}__R1.result.json';r=read(src);assert r['valid_output']
   nodes=[{'requirement_id':f'R{i+1}',**n} for i,n in enumerate(r['output']['requirements'])]
   assert all(span_check(s,c['source_units'])['valid'] for n in nodes for s in n['source_spans'])
   output[q]={'qid':q,'question_sha256':c['question_sha256'],'requirements':nodes,'source':rel(src),'source_sha256':sha(src),'replicate':1}
   sources[rel(src)]=sha(src)
  write(P/f'e0_addressability/RUNTIME_SKELETON_{arm}.json',output)
 write(P/'e0_reference/QUESTIONS.json',list(qs.values()))
 sources[rel(PREV/'e0_reference/DEV_QUESTIONS.json')]=sha(PREV/'e0_reference/DEV_QUESTIONS.json')
 sources[rel(PREV/'e0_reference/REFERENCE_TASK_STRUCTURE.json')]=sha(PREV/'e0_reference/REFERENCE_TASK_STRUCTURE.json')
 write(P/'e0_addressability/SKELETON_FREEZE.json',{'base_sha':git('rev-parse','HEAD'),'historical_Claims_or_GoldO_read_in_this_preparation':False,'single_reviewer_prior_familiarity':'Reviewer has worked on the broader repository; no claim of erased memory or independent reviewer. Current construction reads Q-only files and fixed prior decomposition outputs.','Oracle_rule':'Q-only coherent objectives using prior material-unit reference; two report dates/shared-disorder split, final year/host attributes split by Q semantics, no checkpoint-specific edits. Labels non-authoritative; source spans and Q resolve meaning.','runtime_selection':'Replicate1 for both D1 diagnostic and D2 primary, no best-of or repairs.','read_only_sources':sources,'files':{rel(p):sha(p) for p in sorted((P/'e0_addressability').glob('*.json'))}})
 write(P/'e0_addressability/ORACLE_CONSTRUCTION.md','''# Q-only Oracle construction

Oracle uses only original Q, frozen prior Task Structure reference and original
Source Units. It is committed before opening current historical Claims or GoldO.
The reviewer has prior repository familiarity; this is an auditable construction
order, not an assertion of a previously unexposed human reviewer.

One coherent identity/relation/attribute objective per node; complementary
conditions stay together. Prior material units guide scope without imposing an
exact node sequence. Q637 report timing and common-disorder relation are separate;
Q1259 final year and host-university attributes are separate. Q922 retains the
original recipient ellipsis rather than adding a ruler identity in generated prose.
All nodes have exact source spans; labels only identify objectives and add no facts.

Runtime D2 and diagnostic D1 use prior replicate1 in original output order. No
post-hoc splitting, merging, repairing or selecting the better replicate.
''')
if __name__=='__main__':main()
