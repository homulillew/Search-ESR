import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
A={};FLAGS={'s':'stale','d':'drift','u':'unsupported_premise','o':'over_broad','p':'premature_stop','m':'missed_stop','b':'belief_error'}
def add(i,req,flags,reason):
    A[i]={'requirement_ids':req.split(),'valid':not any(k in flags for k in 'sduopm'),**{v:k in flags for k,v in FLAGS.items()},'reason':reason}
add('E25528f10d889','R1 R2 R3 R4 R5','o','Bundles modelling,family,education,music,career and birth name into the whole identification task.')
add('E5e5ee8c253f0','R1 R2 R3 R4 R5','o','Repeats all original identifying details and final birth-name request.')
add('E21d3d68f49fe','R4','ub','Assumes a new fixture/date and95minute event absent from visible history.')
add('Eb6d96b180fa6','R1 R2 R3 R4','o','Both club histories,goal timing,fixture identity and95minute taker remain bundled; no one current relation.')
add('E33f0ba48b81e','R1 R2 R3 R4 R5','uob','Repeats the whole profile and adds socialite as a target restriction not established for the unknown individual.')
add('E75a17649a591','R1 R2 R3 R4','o','Explicitly requests all four biographical clue sets together; whole-goal reconstruction rather than one frontier.')
add('Eb5527c36c08d','R1 R2 R3 R4 R5','o','Full multi-article profile and birth-name goal repeated.')
add('E3a2bf38d81fa','R5 R7','ub','Introduces TchouTchou1988/French/educational identity without prefix support and seeks its alias before qualifying it; proposed1988also does not establish the early1990s start clue.')
add('E1d35aa628b84','R1 R2 R4','o','Combines independent career counts with the match sequence as all remaining criteria, instead of one current unresolved relation.')
add('Edbac36611b9d','R4','','Specific conditional match-sequence verification after the observed opener.')
add('E156c3e3875c6','R4','','A bounded identifying article relation, without assuming BFC meets it.')
add('Edbd947895aab','R4','ub','Introduces a derby/date/score and assumes its95minute event without prefix evidence.')
add('E164aef663966','R3 R4 R5','','Targets subject identity in the specific2020education/career biography, a bounded subset rather than all family/wealth clues.')
add('Ea5ad8c7f1c0a','R2 R3 R4 R5 R6 R7','uob','Unobserved French/TF1/52episode/living-train target properties are assumed, and broad programme/title conditions remain bundled.')
add('E8d7a357eec7c','R1 R5','ub','Founding date is proposed conditionally, but the inserted2011–12Regionalliga season/rank/points/GD description is not observed and is treated as a qualifying premise.')
add('E7430430bbabd','R4','ub','Introduces an unqualified2006Milan derby and assumes its95minute event.')
add('Ea8319fd12006','R2 R3 R4 R5 R6 R7','uob','Assumes French/TF1/52episodes/living train without visible support and bundles programme identity with release title.')
add('E0cc07aa6bf7c','R5 R7','ub','Introduces a specific1993French educational programme and seeks its alias without any prefix qualification of that new candidate.')
if __name__=='__main__':
    b=TOP/'exploration';ctx=rd(b/'masked_contexts.json')
    for p in rd(b/'masked_packets.json'):
        if p['review_id'] in A:continue
        if p['output'] is None:
            add(p['review_id'],'','','Provider/contract failure; semantic flags not invented.');A[p['review_id']]['valid']=False
        elif p['output']['decision']=='stop':
            add(p['review_id'],'','' if ctx[p['context_id']]['complete'] else 'pb','Apply the frozen prefix-only closure label.')
    wr(b/'semantic_review.json',A);print('judgments',len(A))
