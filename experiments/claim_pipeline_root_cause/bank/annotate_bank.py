"""Transcribe the single-reviewer source-only E0 review. No model call."""
import json
from pathlib import Path
from build_inventory import save, sha
B = Path(__file__).resolve().parent

# Index is the already frozen mechanical selection order, never a selection filter.
# Atoms are local, NEW, Gap-useful commitments, not final-answer criteria.
REVIEWS = [
('cross_entity attribution_modality', [], 'Scott is a different subject; possible named buildings are counterfactual. No evidence about Ding or his spouse.', False),
('temporal', [], 'Death at 66 repeats C. More than 60 over a 45-year career does not establish the exact count in the specified May feature.', True),
('identity_entity temporal', [('Peter King / Peter King Nzioki Mwania was born in 1978.', 'birth_date: 25 May 1978')], 'Name alias and birth date are explicit; no cross-person transfer is required.', False),
('source_document', [], 'Observed document title alone does not bind this advertisement/OCR window to the requested illustration/telephone conjunction. Other advertised books cannot inherit the container title.', False),
('conjunction_sequence cross_entity', [], 'Opening Ding–Ma 4–3 result repeats C. Other players’ results do not extend Ding’s later sequence.', True),
('qualifier_quantifier temporal', [
('The D4 case describes a sixteen-year-old male with classic FOP features.', 'a sixteen-year-old male patient with the classic features of FOP'),
('The D4 patient presented with upper-back pain and swelling two months after a biopsy there.', 'A sixteen-year-old male patient was brought to our emergency room with the complaints of pain and swelling in his upper back, in which a biopsy had been performed two months before.'),
('The D4 patient developed shoulder/neck stiffness at nine and further swellings over the next four years, followed by restricted movement.', 'At the age of 9, the patient developed tender stiffness')], 'Local D4 case relations are explicit. They do not establish both target reports, publication country or their common global identity.', False),
('attribution_modality temporal', [], 'Visible transmission/cover-memo date and realignment date repeat C; actual enclosed-letter date is absent. A footnote about handwriting supplies no date value.', True),
('cross_entity identity_entity', [], 'The Milan split forming Internazionale repeats C; it cannot establish PSG/Lille history.', True),
('temporal attribution_modality', [], 'The retrospective album count and the 2016 interview are already in C. Their adjacency does not date that count to the interview or identify a May feature.', True),
('role source_document', [('Peter Nzioki’s filmography lists Policeman 1 in The Constant Gardener (2005).', '| 2005 | The Constant Gardener | Policeman 1 |')], 'Visible page title binds the filmography subject. No Iracema director appears in this window.', False),
('conjunction_sequence temporal', [], 'This biography window covers earlier career years, not the requested 2023 match sequence. Unrelated match scores cannot fill that sequence.', False),
('attribution_modality temporal', [('King Michael’s letter thanks Red Army help in regaining North Transylvania.', 'North Transylvania')], 'Preserve the letter’s speaker and reported appreciation. No actual letter-date value is visible.', False),
('source_document qualifier_quantifier', [
('D10 is titled Examination of Prospective Teachers’ Creative Comparisons for the Concept of Science Education.', 'Examination of Prospective Teachers'),
('D10 lists Zeynel Abidin Yılmaz and Mehmet Diyaddin Yaşar as authors.', 'Zeynel Abidin YILMAZ, Mehmet Diyaddin YAŞAR'),
('D10 explicitly gives publication on 31 December 2022.', 'Published: 31 .12 .2022')], 'Header establishes local title/authors/date; it does not establish six tables or the 13.53% value.', False),
('source_document temporal', [], 'Listed dated publications are 2023/2024; the last item has no visible date. No visible 13.53%/six-table relation or in-range target identification.', False),
('qualifier_quantifier temporal', [('The report says Rangers signed 13 new players ahead of the 2022/23 season.', 'Rangers have signed 13 new players ahead of the 2022/23')], 'Article content explicitly supplies the season/count. Scraped page date is a separate field, not the season.', False),
('qualifier_quantifier temporal', [('The table lists Rangers International (Enugu) with eight league championships, including 2023–24.', '| Rangers International (Enugu) | 8 |')], 'A new scoped league-total update is useful. It is not fifteen all-competition trophies as of a 2023 article, nor a founding year.', False),
('role attribution_modality', [
('Christian Ribeiro describes himself as a former professional footballer turned property investor.', "I'm Christian Ribeiro, a former pro footballer turned property investor"),
('Ribeiro names property developer Jay Puddy as his business partner.', 'my business partner and property developer Jay Puddy')], 'Useful candidate-local retirement/business lead; property investor is not chartered surveyor, retirement age is not shirt number, and partnership date is absent.', False),
('role cross_entity', [], 'Hockey and skateboarding business examples do not identify the requested footballer. No role/identity transfer.', False),
('identity_entity temporal', [('Albino Frog Software was formerly named Night Sky and was officially established in Florida in October 1993 after using that name.', 'Albino Frog Software, Inc. (formerly Night Sky)')], 'The company-name relation is explicit. Do not assign an exact renaming day or infer a different game release date.', False),
('role qualifier_quantifier', [
('Galacta was released in November 1992 on DOS.', 'November 1992 on DOS'),
('Galacta is listed as shareware with one offline player.', 'Number of Offline Players\n1 Player'),
('Galacta’s DOS credits list Sean Michael Puckett, Rocco Caputo and Terri L. Puckett in the displayed roles.', 'Credits (DOS version)')], 'Credits include design/testing and personal acknowledgments. Do not turn all three credited people into programmers.', False),
('attribution_modality identity_entity', [], 'Competing attributions and another poet’s dates do not establish Arinimaal’s birth, husband-as-poet or beauty-derived predecessor name. Dry-well account duplicates C.', True),
('attribution_modality identity_entity', [], 'This is attribution debate, not the requested biographical relations. A poet’s name in proximity does not establish spouse or shared birth dates.', False),
('qualifier_quantifier source_document', [
('Nwando Achebe authored The Female King of Colonial Nigeria.', 'author: Nwando Achebe'),
('The book was published in February 2011.', 'Published: February 2011'),
('The book concerns Ahebi Ugbabe, an Igbo woman who became king in colonial Nigeria and learned many languages.', 'an Igbo woman, Ahebi Ugbabe, who became king in colonial Nigeria')], 'Local book/subject relations are useful. Only ruler, page count, degree and course-book conjunction are not established.', False),
('attribution_modality source_document', [], 'The review concerns English succession and unrealized possibilities; it does not establish the non-English multilingual queen book. A counterfactual reign is not an actual reign.', False),
('role temporal', [
('The Adventures of Hijitus was directed by Manuel García Ferré.', 'director: Manuel García Ferré'),
('Its writers include Manuel García Ferré, Inés Geldstein and Néstor D’Alessandro.', "writer: * Manuel García Ferré, * Inés Geldstein, * Néstor D'Alessandro"),
('The series first aired on Canal 13 on 7 August 1967.', 'The series first aired on 7 August 1967, on Canal 13')], 'Explicit program-level roles and broadcast relation; metadata page date is separate.', False),
('identity_entity source_document', [], 'Children’s music/song text does not establish the requested television program or its native title.', False),
('role qualifier_quantifier', [], 'An animator’s light table/workstation does not establish paper dimensions or which game’s intro/end animation used it.', False),
('role', [('Dodrill says his workstation doubles as his gaming PC and describes a wireless keyboard setup.', 'My main workstation (which also doubles as my gaming PC)')], 'The interview subject and workstation/keyboard relation are explicit.', False),
('identity_entity attribution_modality', [], 'An album review mentions the late Sophie’s influence, not a partner interview or the specified song statement.', False),
('identity_entity attribution_modality', [], 'Other musicians and posthumous albums do not establish Sophie’s partner identity or statement.', False),
('source_document role', [], 'A paper’s detector-method section does not identify its authors or author ordering.', False),
('source_document role', [], 'Simulation methods and citations do not identify the paper’s second author.', False),
('cross_entity role', [], 'Evangelista’s family businesses and her own US stay do not establish her degree or a US-born child.', False),
('identity_entity role', [('The article describes Heart Evangelista as both singer and model.', 'TV host, singer, model, philanthropist')], 'Both occupations bind to the same explicitly named subject.', False),
('conjunction_sequence role', [('Insouciance (season 1 episode 2) has Gretchen’s friends convince Jimmy to take her on a date.', "Jimmy is convinced by Gretchen's friends to take her out on a date.")], 'Episode identity, season and plot are visible together.', False),
('conjunction_sequence temporal', [('Not a Great Bet (season 4 episode 7) has Gretchen go home for the birth of her brother’s baby.', 'Gretchen goes home for the birth of her brother')], 'One season-four plot relation is explicit, not the season-one/three conjunction.', False),
]

def main():
    packets=json.loads((B/'selection.json').read_text())['packets']
    assert len(packets)==len(REVIEWS)==36
    rows=[]
    related_no_new = {4, 11, 14, 22, 27, 31, 32, 33}
    for index,(p,(families,atoms,reason,duplicate)) in enumerate(zip(packets,REVIEWS),1):
        w=p['Observation'][0]; required=[]
        for i,(statement,anchor) in enumerate(atoms,1):
            start=w['text'].index(anchor)
            required.append({'atom_id':p['packet_id']+f'_U{i}','statement':statement,
                'support':[{'window_ref':w['window_ref'],'field':'text','start':start,'end':start+len(anchor),'anchor':anchor}],
                'scope':'local commitment; not completion of all question conditions'})
        rows.append({'packet_id':p['packet_id'],'families':families.split(),
            'stratum':'positive' if atoms else 'duplicate_no_new' if duplicate else 'relevant_no_new' if index in related_no_new else 'ambiguous_negative',
            'required_atoms':required,'duplicate_relevant':duplicate,
            'expect_postdedup_silence':not atoms,'correct_silence_primary_eligible':duplicate or index in related_no_new,
            'reason':reason,'reviewer':'Codex single reviewer; source-only support, Gap/C only usefulness/dedup',
            'reviewed_full_observation':True,'gold_or_future_used':False})
    save(B/'annotations.json',{'selection_sha256':sha(B/'selection.json'),'packets':rows,'optional_atoms_in_recall_denominator':False})

if __name__=='__main__':main()
