"""Transcription of the single reviewer's pre-call Q-only reference judgments.

Descriptions and grouping guidance are evaluation constraints, not a gold node
sequence. Full-unit anchors are copied by address without rewriting the source.
"""
from .common import *

# importance, source-unit numbers, semantic requirement. All written before calls.
DATA = {
'122': {
 'units':[
 ('critical',[1],'Identify a person born in 1948–1952 in the described birthplace.'),
 ('material',[1],'Birthplace population increased 5.88% during 2010–2020 according to an official website of its country.'),
 ('material',[2],'That person made an important presentation in 1990 at a prominent cultural center of the same country.'),
 ('material',[3],'The same person did not record any material between 1986 and 1994.'),
 ('critical',[1],'Obtain the year of death of that described person.')],
 'invariants':[('temporal',[1,2,3],'Birth range, population interval, presentation year and no-recording interval belong to their respective events.'),('numeric',[1],'5.88% is population increase, not a birth/death statistic.'),('ownership',[1,2],'Birthplace and cultural center refer to the same country; the presentation belongs to the person.')],
 'dependencies':[([1,2,3,4],[5],'Identify the described person before assigning their death year.')],
 'forbidden':['Inventing a person, death date, birthplace, cultural center or recording medium.','Moving population dates onto the person; converting no material recorded into no performances.'],
 'target':'Year of death of the question-described person.',
 'grouping':'Birthplace demographic clue and person biography can be separate; coherent birth/place identification can combine them. Presentation and no-recording are distinct episodes.'},
'169': {
 'units':[
 ('critical',[1,2],'Musical artist first name matches part of an unrelated charity name; charity registered in 2000–2010 inclusive.'),
 ('material',[3],'Artist died in a city 20–30 miles inclusive from that country’s deadliest aviation accident site, as ranked by 2023.'),
 ('material',[4],'That accident occurred 15 years before the artist’s accidental death.'),
 ('critical',[5],'Artist’s partner at the time of death gave an interview saying the artist became a direct reference to one of their songs after death.'),
 ('material',[6],'The referenced song title is a single word and an adjective.'),
 ('critical',[7],'Identify the title of the song connected to that interview/reference relation.')],
 'invariants':[('relation_argument',[1,2,5],'Charity shares part of its name with artist first name but is unrelated. Interview speaker is the partner at death, artist is posthumous reference.'),('role_identity',[5],'Retain ambiguous possessive their songs rather than inventing definite authorship if it changes the question relation.'),('temporal',[2,3,4,5],'Registration range belongs to charity, 2023 qualifies accident ranking, 15 years separates accident and death, song reference follows death.'),('numeric',[3,4,6],'Preserve 20–30 inclusive miles, 15 years and one adjective word.')],
 'dependencies':[([4],[6],'Preserve the described interview/song relationship as the referent for the requested song title.')],
 'forbidden':['Named artist/partner/song supplied from outside Q.','Treating question-required interview existence as already verified by research.','Making charity about or founded by the artist.'],
 'target':'Title of the described one-word adjective song.',
 'grouping':'Charity identity, death/accident relation, and interview/song relation are separable episodes. Title grammar may accompany song target. Clear cross-node pronouns are allowed.'},
'228': {
 'units':[
 ('critical',[1],'Identify company founder through its online-video-games division’s game released in 2000–2010 inclusive, among top earning at least until 2019.'),
 ('material',[1],'Founder graduated from a university founded in 1930–1970 inclusive.'),
 ('material',[2],'Founder and spouse had no children from their marriage up to 2019.'),
 ('critical',[2],'The pair made a foundational gift to construct a building within a larger complex.'),
 ('material',[3],'As of 2019 the building was scheduled to open in 2018–2021 inclusive and belonged to a university.'),
 ('critical',[4],'Determine which university the described gift-funded building was part of as of 2023.')],
 'invariants':[('role_identity',[1,3,4],'Founder’s alma mater and gift-building university are not established as the same or different.'),('ownership',[1,2],'Game release is attributed to company division; gift to founder and spouse; building belongs to larger complex.'),('temporal',[1,2,3,4],'2019 qualifies earning/childlessness/schedule knowledge; planned 2018–2021 opening is not actual opening; 2023 qualifies requested affiliation.')],
 'dependencies':[([4,5],[6],'Identify the donated building before assigning its university affiliation.')],
 'forbidden':['Equating alma mater with the building university.','Turning planned opening into actual completion.','Inventing donor, game, university or building names.'],
 'target':'University affiliation of the gift-funded building as of 2023.',
 'grouping':'Company/game, founder education, marriage, gift/building are separable relations; gift and planned building opening may be one coherent building-identification unit.'},
'261': {
 'units':[
 ('material',[3],'Target research paper was written between 2012 and 2022.'),
 ('critical',[4],'Exactly two people wrote the target paper.'),
 ('critical',[4],'One target-paper author has another paper in Journal of Baltic Science Education written in 2016–2023.'),
 ('critical',[5],'One target-paper author was Harran University academic staff as of 2023.'),
 ('material',[6],'Target paper has six tables in total.'),
 ('material',[6],'One target-paper table has one emotion at 13.53 percent.'),
 ('critical',[7],'Obtain the name of the described target research paper.')],
 'invariants':[('role_identity',[4,5],'JBSE-author role and Harran-author role may be same or different; neither equality nor inequality is specified.'),('temporal',[3,4,5],'2012–2022 belongs to target paper, 2016–2023 to another JBSE paper, as-of 2023 to affiliation.'),('numeric',[4,6],'Two authors, six total tables, 13.53 percent emotion preserve their objects.'),('ownership',[4,6],'JBSE is the OTHER paper; tables and percentage belong to target paper.')],
 'dependencies':[([1,2,3,4,5,6],[7],'Preserve the question-described paper identification before its requested name.')],
 'forbidden':['Harran author equals JBSE author.','Harran author differs from JBSE author.','Target paper necessarily published in JBSE.'],
 'target':'Name of the question-described paper.',
 'grouping':'Publication/authorship, JBSE relation, Harran relation and table contents are separable; table count and emotion value may combine. Grouping roles alone does not assert equality; explicit co-binding does.'},
'538': {
 'units':[
 ('material',[1],'Book contains 130–140 illustrations and descriptions of objects including telephone and telegraph.'),
 ('critical',[2],'Book gives rust-cleaning method using either substance named in a Three Dog Night song OR oil whose name matches a country song.'),
 ('material',[3],'Book references a mechanical engineer born in early 1800s.'),
 ('material',[3],'Book references a scientist whose father was a poet.'),
 ('material',[3],'Book references a well-known L. E. figure born in early 1700s in a central European country.'),
 ('critical',[1],'Identify title of the described book as of December 2023.')],
 'invariants':[('relation_argument',[2],'Alternative rust-cleaning substances and their respective music clues must retain OR and correct associations.'),('ownership',[3],'Poet is scientist’s father, not mechanical engineer by assumption; initials and early-1700s birth describe the third figure.'),('numeric',[1],'130–140 is book illustration/description count.'),('temporal',[1,3],'December 2023 is query as-of, not book publication date; early 1800s vs early 1700s remain on respective people.')],
 'dependencies':[([1,2,3,4,5],[6],'Book identity conditions must be retained for title request.')],
 'forbidden':['Resolving L. E., engineer, scientist, songs or ingredients using outside knowledge.','AND replacing alternative substances.','Attaching poet father or initials to wrong referenced figure.'],
 'target':'Book title as of December 2023.',
 'grouping':'Content/count, cleaning method, and referenced people are different content relations. Related references may share a book-reference unit if each person and clue remains distinct.'},
'637': {
 'units':[
 ('critical',[1,2],'Identify two cases reported in different years of the 2010s sharing one disorder.'),
 ('material',[3],'First case country was the largest country of its dominant religion in the world at its establishment.'),
 ('material',[4],'First patient had six months of progressive pain in multiple body parts causing walking and shoulder-movement difficulty.'),
 ('critical',[5],'Second patient had upper-body pain and swelling at a biopsy site two months after that procedure.'),
 ('material',[6],'Second patient had stiffness when younger, followed four years later by swelling.'),
 ('critical',[7],'Obtain scientific name of the disorder shared by the two described case reports.')],
 'invariants':[('ownership',[3,4,5,6],'Country and progressive pain belong to first case; biopsy and childhood sequence belong to second.'),('temporal',[1,3,4,5,6],'Reports are different years within 2010s; country size at establishment; half-year history, two-month post-biopsy, four-year childhood sequence remain separate.'),('relation_argument',[2,7],'Same diagnosis across both reports, not merely similar symptoms.')],
 'dependencies':[([1,2,3,4,5],[6],'Identify the described reports and their common disorder before assigning scientific diagnosis name.')],
 'forbidden':['Supplying a disorder name from outside Q.','Moving symptom chronology from one patient to another.','Biopsy proves causation rather than preceding symptoms.'],
 'target':'Scientific name of the disorder shared by both cases.',
 'grouping':'Conditions within each case can combine; the two clinical histories should not collapse into an undifferentiated patient.'},
'843': {
 'units':[
 ('critical',[1],'Identify DLC for a strategy game released more than three years after base game release.'),
 ('critical',[2],'Base game is subject of 2023 American-university master’s thesis on postcolonialism.'),
 ('material',[2],'Thesis advisor completed two degrees at a California university and published a 2020 video-game monograph.'),
 ('critical',[3],'DLC changes religion and technology mechanics and adds mechanics for a specific playable European nation.'),
 ('critical',[4],'Obtain full name of the third credited content designer of that DLC.')],
 'invariants':[('ownership',[2],'Thesis concerns game, not established as DLC; degrees and monograph belong to advisor, not student.'),('temporal',[1,2],'DLC delay exceeds three years; thesis year 2023; monograph year 2020.'),('numeric',[2,4],'Two degrees; third content designer, not third overall credit or designer of base game.')],
 'dependencies':[([1,2,3,4],[5],'Identify question-described DLC before looking up its third content-designer credit.')],
 'forbidden':['Naming game, DLC or designer from outside Q.','Thesis about DLC as opposed to base game.','Third developer rather than third credited content designer.'],
 'target':'Full name of third credited content designer for the identified DLC.',
 'grouping':'DLC identity/mechanics, thesis identity, advisor identity, and credit attribute are distinguishable objectives. Advisor clues can remain within thesis-identification if scope stays clear.'},
'922': {
 'units':[
 ('critical',[1],'Identify letter written in first half of twentieth century by one country’s ruler to another ruler.'),
 ('critical',[1],'Official delivered letter and recipient gave that official a nickname after a body part.'),
 ('material',[2],'Letter was written roughly six months after its author came to power.'),
 ('critical',[3],'In that letter author refers to their country having regained a region.'),
 ('critical',[4],'Obtain name of the region mentioned in that letter.')],
 'invariants':[('temporal',[1,2],'First-half twentieth-century writing and roughly six months after accession both qualify letter, no memorandum exists in Q.'),('relation_argument',[1],'Recipient nicknames delivery official, not author or official nicknaming recipient.'),('ownership',[3],'Regained region belongs to author’s country as stated in letter, not recipient’s country.')],
 'dependencies':[([1,2,3,4],[5],'Identify described letter and its regained-region content before giving region name.')],
 'forbidden':['Introducing memorandum or its date from historical evidence.','Naming rulers, official or region using outside knowledge.','Reversing nickname giver/receiver or whose country regained territory.'],
 'target':'Name of region the identified letter says author’s country regained.',
 'grouping':'Letter identity/date can combine; courier/nickname relation and letter-content relation can be separate. No arbitrary demand for one node per time modifier.'},
'971': {
 'units':[
 ('critical',[1],'Indian author promoted associate professor to professor in 2022 at university of both undergraduate and graduate study.'),
 ('critical',[2],'Author’s Canadian-university PhD supervised by Iranian professor.'),
 ('material',[2],'Advisor wanted to be writer, switched to mathematics at end of high school, earned doctorate in Minnesota.'),
 ('critical',[3],'Author published mathematics/ancient-liberation-technique book 20 years after completing PhD.'),
 ('critical',[3],'Author subsequently published a similar-topic journal article six years after that book.'),
 ('critical',[4],'Obtain title of that described later journal article.')],
 'invariants':[('ownership',[1,2],'Undergraduate/graduate university equals promotion university; Canadian PhD belongs to author; Minnesota doctorate and career aspiration to advisor.'),('temporal',[1,2,3],'Promotion 2022; advisor switch end-high-school; book 20 years after author PhD; article six years after book.'),('relation_argument',[3,4],'Final title is later ARTICLE not book; topic similarity and same author preserved.')],
 'dependencies':[([5],[6],'Described later journal article identity/existence must remain before requested article title.')],
 'forbidden':['Naming author, advisor, universities, book, religion or article from outside Q.','Book title substituted for article title.','Treating article existence required by question as a current research evidence claim.'],
 'target':'Title of the described journal article six years after the book.',
 'grouping':'Author career, advisor identity, book and later article are distinct referents. Book-to-article timing can be a coherent publication relation while retaining both identities.'},
'1259': {
 'units':[
 ('material',[1],'Annual prestigious programming-contest world final among university teams.'),
 ('critical',[2],'In target edition championship-winning team included an Australian coder.'),
 ('critical',[3],'That coder earned bronze, silver, gold, silver in four consecutive IOIs in that order.'),
 ('critical',[4],'The coder’s two other teammates share the same country with each other.'),
 ('critical',[5],'Obtain winning edition’s year and its host university.')],
 'invariants':[('relation_argument',[2,4],'Same-country comparison is teammate1 versus teammate2, not either versus Australian coder.'),('role_identity',[2,4],'Two other teammates are distinct from coder; their country is unspecified and need not be Australia.'),('numeric',[3],'Four consecutive IOIs and bronze/silver/gold/silver order must remain.'),('ownership',[5],'Requested university hosts winning edition; not necessarily winning team’s own university.')],
 'dependencies':[([1,2,3,4],[5],'Identify winning edition through described coder/team before giving year and host university.')],
 'forbidden':['Naming coder or contest using outside knowledge.','Other teammates necessarily Australian.','Host university equated to team university.'],
 'target':'Winning contest edition year and that edition’s host university.',
 'grouping':'Coder medal identity, teammate-country relation, winning event and final requested attributes are separable; two final attributes may share event-target unit.'}
}
DATA.update({
'968':{
 'units':[
 ('critical',[1],'Identify an insect enjoyed in African countries and a local delicacy in northern South Africa.'),
 ('material',[2],'Insect burrows underground to pupate.'),
 ('material',[3],'Insect is over-harvested and can be very expensive.'),
 ('critical',[4],'An early-2010s harvesting project for that insect aimed to benefit both eaters and sellers.'),
 ('critical',[5],'Identify a 2010s article quoting someone saying that insect is a good source of protein and identify that speaker.')],
 'invariants':[('ownership',[5],'Protein statement belongs to quoted speaker, not automatically article author or project founder.'),('temporal',[4,5],'Early 2010s project versus broader 2010s article date.'),('relation_argument',[1,4],'Project concerns same insect, and benefits consumers and sellers.')],
 'dependencies':[([1,2,3,4],[5],'Identify the described insect/project and article statement before assigning speaker identity.')],
 'forbidden':['Naming insect/project/speaker from outside Q.','Equating quoted speaker with article author.'],
 'target':'Person quoted about insect protein in the described article.',
 'grouping':'Insect ecological/market identity, harvesting project, article quote attribution are distinct objectives.'},
'548':{
 'units':[
 ('critical',[1],'Company founded in same year a former Director General and Minister died of cancer.'),
 ('critical',[2],'Company fully acquired a platform, significantly increasing its global community.'),
 ('material',[3],'Company network reached over 70 countries as of 2021.'),
 ('critical',[4],'A few years later the company launched its platform for operational transparency; retain relative timing without inventing an exact year.'),
 ('critical',[5],'Identify company name matching these conditions.')],
 'invariants':[('temporal',[1,3,4],'Founding year equals official’s death year; 2021 qualifies network extent; later launch has no explicit exact year.'),('role_identity',[2,4],'Acquired platform and later launched platform are not explicitly identified as equal or different.'),('ownership',[1,2,4],'Cancer death describes former official; acquisition and launch describe company.'),('numeric',[3],'Network over 70 countries, not exactly 70.')],
 'dependencies':[([1,2,3,4],[5],'Identify company through founding/acquisition/network/launch relations before its name.')],
 'forbidden':['Named company/platform/official or exact death/launch year invented.','Hardening vague few-years-later antecedent beyond Q.','Assuming acquired platform is necessarily the later launched platform.'],
 'target':'Name of described company.',
 'grouping':'Founding/death coincidence, acquisition, network reach and later launch are distinct episodes; naming target can accompany identification. Temporal antecedent of few years later is ambiguous; preserve wording.'},
'523':{
 'units':[
 ('material',[1],'Person A began acting young and rapidly became a household sensation.'),
 ('critical',[2],'A starred in a family-life series airing from late twentieth century until a year between YouTube founding and first iPad release.'),
 ('material',[3],'By 2023 A appeared in a true-life media-personality series and another about a country’s healthcare system.'),
 ('critical',[4,5],'A attended international school founded 2001, with separate pre-primary and high-school campuses as of 2020.'),
 ('material',[6],'A married in same year Joe Biden was sworn in as US president.'),
 ('critical',[7],'Identify film production company that produced the described family-life series.')],
 'invariants':[('ownership',[2,3,7],'Requested producer belongs to family-life series, not either later-mentioned series.'),('temporal',[2,4,5,6],'School founded 2001; campuses as of 2020; acting appearances as of 2023; series ending between named product milestones; marriage matches inauguration.'),('numeric',[5],'Two school campuses with specified distinct education levels.')],
 'dependencies':[([2],[6],'Retain identification of the described family-life series before its production-company name.')],
 'forbidden':['Supplying actor, series, producer or calendar dates for product/inauguration milestones from outside Q.','Conflating the three described shows.'],
 'target':'Film production company for the identified family-life series.',
 'grouping':'Actor career, family-life series, other shows, school and marriage are separable relations; school’s two source units should remain semantically connected.'},
'1142':{
 'units':[
 ('critical',[1],'A December 1–15 inclusive press release before 2023 reports country vaccine totals as of December 5: 16,201,670 received, 7,583,134 administered.'),
 ('critical',[2],'Same-year organization annual report: nearly 2.2 million members/supporters contributed over $49 million, contributed services 12% of total revenue.'),
 ('critical',[3],'Following-year annual report credits organization role rescinding prior administration’s plan to open most of 22 million NPR-A acres to oil/gas drilling.'),
 ('material',[3],'Following-year contributed services declined from 12% to 10%, described as by 2%.'),
 ('critical',[4,5],'Give name only, without titles, of emeritus board member in the following report year.')],
 'invariants':[('temporal',[1,2,3,4],'Press release and first annual report share year; second report and requested board member follow the next year; December 5 is tally date not necessarily release date.'),('numeric',[1,2,3],'Preserve vaccine count roles, nearly/over qualifiers, 12-to-10%, most of 22 million acres.'),('ownership',[1,2,3],'Vaccine statistics describe a country; donations/members/services and intervention describe organization, not vice versa.')],
 'dependencies':[([2,3,4],[5],'Identify relevant organization and following-year report before assigning emeritus board member.')],
 'forbidden':['Equating vaccine country with organization home country.','Inventing country, organization, report year or member name.','Contributed services 10% attributed to initial report.'],
 'target':'Emeritus board member in following-year annual report; name only, no titles.',
 'grouping':'Vaccine-release year identification and organizational annual-report identification are independent episodes; two organization reports can be coherent comparison if year roles are preserved.'},
'294':{
 'units':[
 ('critical',[1],'Person was third of five children of mother Johanna and father Christian.'),
 ('material',[2],'As child hid to read, making a clay candlestick to study at night in the secret place.'),
 ('material',[3],'During financial difficulty took translation work to earn extra income.'),
 ('material',[4],'Died wealthy after 1820 and before 1880, endpoints excluded.'),
 ('critical',[1],'Obtain full name of the person meeting these conditions.')],
 'invariants':[('role_identity',[1],'Johanna is mother and Christian father; person is third child, not parent.'),('temporal',[3,4],'Financial struggles earlier in career do not imply poor at death; death after 1820 before 1880.'),('numeric',[1],'Third out of five children.')],
 'dependencies':[([1,2,3,4],[5],'Retain identity conditions of described person before assigning full name.')],
 'forbidden':['Naming person or exact death year from outside Q.','Inclusive endpoints substituted for explicit after/before.','Translation employment conflated with childhood study.'],
 'target':'Full name of described third child.',
 'grouping':'Family identity, childhood reading, translation work and death circumstances are distinct biography episodes.'},
'1096':{
 'units':[
 ('critical',[1],'Identify two-author article published in 2019–2021 inclusive.'),
 ('material',[2],'First author participated in a 2018 Aalborg conference.'),
 ('critical',[3],'Corresponding author’s university affiliation at publication was among world top 130 for 2024 QS ranking announced in 2023.'),
 ('critical',[4],'Article discusses image-related phenomenon previously addressed from Systemic Functional Linguistics perspective.'),
 ('critical',[5],'Authors propose different framework for identifying new elements; this framework appears in first keyword.'),
 ('critical',[6],'Obtain the article’s second keyword.')],
 'invariants':[('role_identity',[2,3],'First author and corresponding author are not stated same or different.'),('temporal',[1,2,3],'Conference 2018; article 2019–2021; affiliation at publication; 2024 ranking in 2023.'),('ownership',[4,5,6],'First keyword names proposed framework, not automatically SFL; requested second keyword is distinct ordinal position.'),('numeric',[1,3,5,6],'Two authors, top130, first versus second keyword retain objects.')],
 'dependencies':[([1,2,3,4,5],[6],'Identify article through author/content/framework clues before retrieving second keyword.')],
 'forbidden':['Equating first and corresponding author roles.','Second keyword inferred to be the framework/SFL.','Inventing article/authors/university/keyword.'],
 'target':'Second keyword in question-described article.',
 'grouping':'Article bibliographic identity, first-author conference, corresponding-author affiliation and phenomenon/framework are separable; adjacent content/framework clues may combine.'},
'836':{
 'units':[
 ('critical',[1,2],'Identify horror series aired in 2000–2015 inclusive with fewer than ten episodes as of December 31 2023.'),
 ('critical',[3],'One series showrunner founded a talent management company.'),
 ('critical',[4],'An interracial comedian released first stand-up special under that same company in early 2020s.'),
 ('material',[5],'Comedian born 14 years before series aired.'),
 ('critical',[1],'Obtain full name of performer of Nurse role in that series.')],
 'invariants':[('role_identity',[1,3,4],'Nurse performer, showrunner/company founder and comedian are distinct described roles without required equality or inequality.'),('temporal',[1,2,4,5],'Series airing interval, episode cutoff, special early2020s, birth 14 years before airing keep scopes.'),('ownership',[3,4],'Comedian special under same company founded by showrunner, not necessarily comedian-owned.')],
 'dependencies':[([1,2,3,4],[5],'Identify described series before naming Nurse performer.')],
 'forbidden':['Equating comedian with Nurse performer or showrunner.','Converting under company into founded company.','Supplying series/person/company names from outside Q.'],
 'target':'Full name of Nurse performer in identified series.',
 'grouping':'Series identity, showrunner-company and comedian-special relations can be separate; same-company linkage must remain.'},
'128':{
 'units':[
 ('critical',[1],'November2019 article by media company founded in1960s compares scoring methods for different types of one sport.'),
 ('critical',[2],'Exactly one professional athlete is named throughout that article.'),
 ('critical',[3],'January2020 article by media company originating in1950s concerns that same athlete.'),
 ('material',[4],'Second article includes excerpts from an interview the athlete gave.'),
 ('critical',[5],'Give athlete hometown according to the 2020 article.')],
 'invariants':[('temporal',[1,3],'1960s company publishes November2019 article; 1950s company publishes January2020 article.'),('ownership',[1,2,3,4,5],'One-named-athlete condition belongs to first article; interview excerpts and requested hometown attribution to second.'),('relation_argument',[2,3],'Athlete in second article is same as uniquely named athlete in first, not unspecified similar athlete.')],
 'dependencies':[([1,2,3,4],[5],'Identify the same athlete and second article before reporting its hometown attribution.')],
 'forbidden':['Switching company founding decades between articles.','Making hometown birthplace without support.','Claiming interview conducted by second media company when only excerpts specified.'],
 'target':'Athlete hometown as stated in January2020 article.',
 'grouping':'Two article identities are distinct referents connected by athlete; one may combine each article with its associated conditions.'},
'1158':{
 'units':[
 ('critical',[1],'Identify movie star born1987 with acting career starting2010.'),
 ('material',[2],'As of2022 eight award nominations and four wins in2017,2019,2021,2022.'),
 ('critical',[3],'Star first name shared by two of the Bible’s twelve disciples.'),
 ('material',[4],'Older sibling also movie star as of2023.'),
 ('critical',[5],'Name first soap opera the star acted in.')],
 'invariants':[('ownership',[1,4,5],'Birth/career/soap opera refer to target star, sibling movie-star status belongs to older sibling.'),('numeric',[2,3],'Eight nominations, four wins, two of twelve disciples.'),('temporal',[1,2,4],'Born1987; career2010; award totals as of2022 and four win years; sibling status2023.')],
 'dependencies':[([1,2,3,4],[5],'Identify target star before assigning first soap opera.')],
 'forbidden':['Supplying disciple/star/sibling/show names from outside Q.','First soap opera assumed to be in2010 without Q stating that link.'],
 'target':'Name of star’s first soap opera.',
 'grouping':'Biographical identity, awards, first-name relation, sibling relation and debut soap attribute are coherent separate objectives.'},
'805':{
 'units':[
 ('critical',[1],'Identify semi-autobiography centered on protagonist body part.'),
 ('critical',[2],'Initially published in author native language; later translated by another award-winning writer, translator and journalist.'),
 ('material',[3],'That translator received notable translation grant in2000–2020 inclusive.'),
 ('material',[4],'Original author holds PhD.'),
 ('critical',[5],'Author’s MS dissertation received best-dissertation title in2005–2010 inclusive.'),
 ('material',[6],'Author master’s university founded August11 in1960–1990 inclusive.'),
 ('critical',[7],'Obtain original author’s real full name.')],
 'invariants':[('role_identity',[2,3,4,5,6],'Original author and another translator are distinct; grant and writer/translator/journalist awards belong to translator; academic credentials to original author.'),('temporal',[2,3,5,6],'Native publication precedes translation; grant2000–2020; dissertation distinction2005–2010; university founded August11 during1960–1990.'),('ownership',[6],'Specified university is master’s university, not necessarily doctorate institution.')],
 'dependencies':[([1,2,4,5,6],[7],'Retain described book’s original author identity before real full name; translator is a linked clue not answer.')],
 'forbidden':['Translator treated as original author or receives author academic record.','Doctoral university equated to master’s university.','Naming author/book/translator/body part externally.'],
 'target':'Real full name of the original semi-autobiography author.',
 'grouping':'Book/publication, translator identity/grant, author credentials and master’s university are distinct linked referents; one person’s related academic conditions may group coherently.'},
'160':{
 'units':[
 ('critical',[1,3],'Identify poem contained in a poetry collection, with one-word non-English title.'),
 ('critical',[4],'Poem final line exactly two words that are identical to collection title.'),
 ('material',[5],'Collection is author’s fourth poetry book.'),
 ('critical',[6],'Collection won2010–2020 inclusive award from independent literary press.'),
 ('material',[7],'Nomination for that award came from another well-known author born mid1900s holding folklore PhD.'),
 ('critical',[2],'Give both poem name and book name.')],
 'invariants':[('role_identity',[5,7],'Nominator is another author, not collection author; folklore PhD/birth clue belong to nominator.'),('numeric',[3,4,5],'One-word poem title differs from two-word last line/book title; fourth poetry collection.'),('ownership',[4,6,7],'Last line equals book title, award belongs to book, nomination supplied by other author.'),('temporal',[6,7],'2010–2020 belongs to award; mid1900s to nominator birth.')],
 'dependencies':[([1,2,3,4,5],[6],'Retain poem/collection identity and their textual relation before naming both.')],
 'forbidden':['Poem title equated with two-word last line.','Folklore PhD assigned to collection author.','Award given to poem alone instead of book.'],
 'target':'Both poem name and its poetry-collection title.',
 'grouping':'Poem/title-last-line/book-title relation is coherent; collection ordinal/award and nominator identity may separate. One-word versus two-word scopes must stay explicit.'},
'1027':{
 'units':[
 ('critical',[1],'Identify American racer born in August and cremated after death.'),
 ('material',[2],'First title won in1935–1940 inclusive.'),
 ('material',[3],'Earned pole position in a1950s race.'),
 ('material',[4],'Attended high school founded1800–1810 inclusive.'),
 ('material',[5],'Drove father’s car at age5.'),
 ('critical',[6],'Determine age at first race participation.')],
 'invariants':[('temporal',[2,3,4,5,6],'First title interval,1950s pole race,school founding interval,age5 driving and unknown first-race age remain distinct.'),('ownership',[4,5],'Founding dates describe high school; car belongs to father.'),('relation_argument',[2,3,5,6],'First title, pole position, driving father’s car and first race are not stated to be same event.')],
 'dependencies':[([1,2,3,4,5],[6],'Identify described racer before attributing first-race age.')],
 'forbidden':['First-race age set to5 based only on driving car.','First title or pole race treated as first race.','Naming racer from outside Q.'],
 'target':'Age at racer’s first race participation.',
 'grouping':'Racer identity, first-title event, pole-position event, school relation and childhood driving are distinct episodes; final first-race attribute may not inherit another event’s age/date.'}
})

def build():
    cases=bank();assert set(DATA)==set(cases)
    out={}
    for q,d in DATA.items():
        units=cases[q]['source_units']
        def spans(ns):return [{'unit':units[i-1]['unit'],'text':units[i-1]['text']} for i in sorted(set(ns))]
        ms=[dict(id=f'M{i+1}',importance=imp,weight={'critical':2,'material':1,'minor':0}[imp],source_spans=spans(ns),description=desc) for i,(imp,ns,desc) in enumerate(d['units'])]
        inv=[dict(id=f'I{i+1}',type=typ,description=desc,source_spans=spans(ns)) for i,(typ,ns,desc) in enumerate(d['invariants'])]
        deps=[]
        for i,(up,down,desc) in enumerate(d['dependencies']):
            deps.append(dict(id=f'K{i+1}',upstream=[f'M{x}' for x in up],downstream=[f'M{x}' for x in down],description=desc,source_spans=spans([n for x in up+down for n in d['units'][x-1][1]])))
        out[q]=dict(qid=q,question_sha256=cases[q]['question_sha256'],material_units=ms,critical_invariants=inv,dependency_checkpoints=deps,forbidden_inferences=d['forbidden'],answer_target={'description':d['target'],'source_spans':ms[-1]['source_spans']},grouping_guidance=d['grouping'])
    write(P/'e0_reference/REFERENCE_TASK_STRUCTURE.json',out)
if __name__=='__main__':build()
