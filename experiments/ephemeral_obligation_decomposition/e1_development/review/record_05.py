from ...analysis.review_record import *
j=judgment
record('e1_development','05',[
j('R003',[1,2,3,4,5,6],'Author and advisor roles, both doctorates, promotion, book and later article all retain source scopes; article referent preserved separately from title.'),
j('R024',[1,2,3,4,5,6],'Six coherent groups preserve Canadian author PhD versus Minnesota advisor doctorate; book/article timing and title target intact.'),
j('R026',[[1,2,3],[4,5],[6,7,8],9,10,11],'Eleven nodes are more granular but all relations retain named anonymous roles; advisor history does not move to author. Both publication referents retained.'),
j('R037',[1,2,3,4,5,6],'Complete six-objective skeleton with distinct described article and its title; question-required article existence is legitimate task semantics.'),
j('R040',[[1,2],3,[4,5],6,7,8],'Advisor history split into career and doctorate units while referent remains explicit. Article identity and six-year relation precede requested title.'),
j('R046',[[1,2],3,4,5,6,7],'All identity and temporal requirements retained. Separate Indian-author node is redundant rather than harmful fragmentation.'),
j('R004',[1,2,3,4,[5,6]],'Teammate nationality comparison stays between other two teammates; medal order and winning edition’s host university preserved.'),
j('R012',[1,2,3,4,[5,6]],'Six coherent units preserve contest, winning team, coder medals, teammate relation and both final attributes.'),
j('R015',[1,2,4,3,[5,6]],'Reorders coder/teammate requirements without changing meaning; other teammates share country with each other, not assigned Australian nationality.'),
j('R017',[1,[2,3],4,5,[2,6]],'Node5 changes other teammates from same country with each other to same country as coder. This strengthens nationality relation and changes its arguments. Remaining event, medal and host-year structure retained.',missing=['M4'],violations=[violation('I1',['relation_argument'],[5],'same country as the coder introduces coder as the comparison argument absent from Q.')],invented=[{'nodes':[5],'reason':'Invented equality between teammates’ country and Australian coder’s country.'}],notes={'M4':'Corrupted condition receives zero coverage despite stronger condition logically implying a shared teammate country.'}),
j('R042',[1,2,3,4,[5,6]],'Separate final year and host-university spans remain connected to same winning edition; no role/nationality inference.'),
j('R056',[1,2,3,4,[5,6]],'Noun-phrase final attributes clearly request year and host of same winning edition. All descriptive conditions preserved verbatim.')
])
