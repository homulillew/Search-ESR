from .record_review import record
J={}
def add(ids,reason,fails=(),errors=(),ambiguity='low'):
 for n in ids:J[n]={'fails':list(fails),'errors':list(errors),'reason':reason,'ambiguity':ambiguity}
add([3,40,64,67,162,167,173,194], 'C identifies the base game, but no DLC. Discovers one DLC through its release relation and complementary religion/technology/nation mechanics. This is a coherent local identity profile.')
add([22,69,146,154,171,195], 'Discovers the author through a bounded academic promotion/education profile, without assuming a named candidate or adding the independent publication chain.')
add([82], 'The author academic-profile discovery includes supervisor biography as a complementary academic identity clue, but excludes the independent book/article objectives. Accept under the same inherited academic-profile boundary.',ambiguity='medium')
add([147], 'Bundles the author academic profile, supervisor biography, book and subsequent article into essentially the whole question. No local focus selected.', ['Local'],['whole_question_restatement'],'medium')
add([28], 'Courier identification/nickname would be a valid local goal, but the output imports Roosevelt as the recipient although Q/C name only the US President. External historical identity is not an allowed evidence source.', ['ScopeFaithful'],['outside_knowledge'])
add([48,89,150,159,212], 'The letter is identified but its final delivering official and recipient-given nickname are not. Identifying that official with the question nickname qualification is one bounded profile.')
add([151], 'Identifies the still-unknown final courier of the established letter. This is a meaningful unresolved role identity, even without separately testing the nickname.')
add([50], 'Transfers the recipient-nickname condition to the initial OSS handoff officer. C2 does not establish that this officer was the final delivering official, so the role arguments are changed.', ['ScopeFaithful'],['wrong_relation_arguments','relation_strengthening'])
add([5], 'Discovers the unknown DLC via its mechanics/timing and a short base-game/thesis association, without requiring the separate advisor biography. Accept as a bounded relational identity profile.',ambiguity='medium')
add([27,29,134], 'A bounded DLC/base-game identity relation from release timing and mechanics. Unknown entities may themselves be the target; no unverified named game is inserted.',ambiguity='medium')
add([12,184], 'Bundles the DLC release/mechanics with the thesis and advisor degrees/monograph chain, reproducing essentially all independent identifying branches of Q.', ['Local'],['whole_question_restatement'],'medium')
add([128], 'Combines the DLC mechanics/timing objective with the specified thesis and its described advisor qualification, rather than selecting a single current branch. Compressed reference to the described academic retains that independent branch.', ['Local'],['bundled_objectives'],'medium')
add([119], 'Says the requested DLC profile is indicated by the thesis, whereas Q only says the thesis concerns the base game. This adds an unverified source-to-DLC content relation.', ['ScopeFaithful'],['wrong_object_scope','relation_strengthening'],'medium')
record('04',J)
