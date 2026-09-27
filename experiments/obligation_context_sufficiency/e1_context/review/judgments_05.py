from .record_review import record
J={}
def add(ids,reason,fails=(),errors=(),ambiguity='low'):
 for n in ids:J[n]={'fails':list(fails),'errors':list(errors),'reason':reason,'ambiguity':ambiguity}
add([10,33,43,91,93,109,197,208], 'Repeats the full book-identification problem: illustration/object contents, rust-removal/music relations, and several independent biographical references. Referring to the other clues in shorthand still retains the whole task.', ['Local'],['whole_question_restatement'],'medium')
add([9,102,177,180], 'Discovers the unknown building through the generic donor/gift, complex and opening-time profile. No named donor is asserted and no final university name is separately extracted. Accept the inherited bounded building-identity boundary.',ambiguity='medium')
add([37,45], 'Combines founder/company/game revenue, alma-mater history, marital status, gift and building/opening branches into essentially the full identification task.', ['Local'],['whole_question_restatement'],'medium')
add([46,87], 'A bounded founder identity through company/game and education profile, excluding the independent spouse/gift/building branch. Unknown founder discovery is legitimate.',ambiguity='medium')
add([15], 'Moves March5,1945 from the covering Donovan memorandum to King Michaels letter. C1 explicitly dates the cover, not the enclosed letter.', ['ScopeFaithful'],['wrong_object_scope'])
add([35,72,79,140,145,210], 'C1 identifies the concrete letter but not its regained-region content. Extracting this local attribute is legitimate; memorandum dates, where used, remain attached to the memorandum.')
add([185], 'States that this King Michael letter was written roughly six months after his accession, although C only dates its covering memorandum. The candidate letter has not been verified against that Q timing relation.', ['ScopeFaithful'],['relation_strengthening'])
add([44,105,116,152], 'C4/C5 make Ding a candidate founder with the marriage clue, but do not establish a qualifying gift. Hardens him into the donor role, and bundles building identification with downstream university extraction.', ['Local','ScopeFaithful','NonDownstream'],['bundled_objectives','relation_strengthening','downstream_obligation','unresolved_referent'],'medium')
add([95,179], 'A local building profile, but it presupposes a qualifying foundational gift by Ding and spouse before that event/relation has been established. C4/C5 do not verify the gift; first test its existence for this candidate.', ['ScopeFaithful','NonDownstream'],['relation_strengthening','downstream_obligation','unresolved_referent'],'medium')
add([148], 'Asks the affiliation of an unestablished building/gift event and fixes Ding as its donor from only a partial founder/marriage profile.', ['ScopeFaithful','NonDownstream'],['relation_strengthening','downstream_obligation','unresolved_referent'])
add([138], 'Does not force a named donor, but combines unknown building identification with extraction of its final university affiliation before the qualifying gift/building is established.', ['Local','NonDownstream'],['bundled_objectives','downstream_obligation','unresolved_referent'],'medium')
record('05',J)
