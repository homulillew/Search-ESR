from ...analysis.review_record import *
j=judgment
record('e1_development','01',[
j('R007',[[2,3],4,5,6,1],'Birth/place, population attribution, presentation and recording hiatus all retained; node7 restates already shared person identity. Extra referent nodes remain intelligible, not severe fragmentation.'),
j('R023',[2,2,3,4,1],'Birth and demographic clue form coherent identification unit; presentation and recording episode separate; death-year objective explicit.'),
j('R027',[2,2,3,4,1],'All numeric/temporal scopes preserved in four coherent task groups; person identity retained separately from final attribute.'),
j('R044',[2,[3,4],5,6,1],'P/L/C symbols only preserve Q referents; country location is explicit in Q; all three event/date scopes and death-year target retained.'),
j('R045',[[2,3],[4,5],6,7,8],'Eight nodes include identity/attribute and birthplace-country decomposition; clear repeated referents preserve relations across nodes without an invented identity.'),
j('R048',[[2,3],[4,5],[6,7,8],9,1],'Population source and presentation venue split across adjacent nodes but same place/country/person remains explicit. Nine nodes alone is not harmful split.',ambiguity='medium'),
j('R013',[[1,2],4,5,[6,7],8,9],'All charity, accident and interview/song relations retained. Artist\'s songs is a natural possessive resolution; it does not assert composition/authorship, so no critical I2 violation. Split artist/partner identity nodes remain connected.',ambiguity='medium',notes={'M4':'Possessive disambiguated to artist association, not a claim that artist wrote the song; register sensitivity, no primary corruption.'}),
j('R020',[1,2,3,4,5,6],'Complete coherent conditions. Artist\'s songs is consistent with natural Q possessive and does not add a composer role. Death and aviation timing unchanged.',ambiguity='medium',notes={'M4':'Same possessive-association ambiguity as R013; no asserted authorship.'}),
j('R025',[1,2,2,3,4,4],'Charity identity, death/accident episode, interview relation and song attribute are coherent distinct groups. Verbatim song possessive left open.'),
j('R029',[1,2,2,3,4,4],'Complete groups retain charity unrelatedness, exact timing/distance, partner interview and one-word adjective title.'),
j('R030',[[1,2,3],[4,5],[6,7],[8,9],10,11],'Eleven groups are fine-grained but city/accident and partner/interview links remain recoverable across adjacent nodes. No omitted prerequisite or changed participant.',ambiguity='medium'),
j('R049',[[1,2,3],4,5,6,7,8],'Charity relationship split into three connected clauses; remaining event/object groups retain all identity conditions and the title objective.')
])
