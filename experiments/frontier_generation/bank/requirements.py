"""Question-only requirement map. No generated Frontier or historical answer labels."""
import json
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]
OLD = TOP.parent / 'goal_residual_control'
DESCRIPTIONS = {
 '546': [
  'Candidate has more than 300 century breaks by 30 January 2025.',
  'Candidate has more than three maximum breaks by 30 January 2025.',
  'Candidate turned professional between 1995 and 2006.',
  'Candidate jointly matches the ordered 2023 deciding-frame win, 4–3 win, 4–0 win and next loss, with the specified first and last opponent century-count bounds.'],
 '1094': [
  'One team in the candidate fixture was founded through discord between two parties.',
  'The opposing team in that same fixture changed identity through several iterations.',
  'The same early-21st-century fixture matches the first team scoring all its goals early and the other scoring later.',
  'Identify the player who took the 95th-minute free kick in that same qualifying fixture.'],
 '517': [
  'Candidate was born in the 1970s and the supplied birth year is consistent with the Goat zodiac clue.',
  'Candidate has a soldier father and a mother working at the barracks hospital.',
  'Candidate played a policeman in a 2005 film whose director was inspired to become a filmmaker by Iracema.',
  'Candidate appeared in a 2013 dramatic thriller whose director is known for writing/directing Kinsey.',
  'Establish the candidate actor’s popular name, with the identifying relations supported as of December 2023.'],
 '435': [
  'Candidate musician died at 66 and was a human-rights activist.',
  'Candidate’s career included 67 albums and a first album released in the 1970s.',
  'Candidate released an early-2000s song urging the sitting president to retire.',
  'Candidate asked why we sing and why there is art in a 2010s interview.',
  'Establish the album count attributable to the candidate’s Forbes Africa feature in May of a 2010s year; do not substitute a lifetime count or unrelated article date.'],
 '580': [
  'Candidate series matches the early-season-one sensitive-issue misunderstanding and friends persuading one lead to take the other on a date.',
  'Candidate series matches the late-season-three sacrifice by the male lead’s roommate.',
  'Candidate series matches the mid-season-four family-baby visit and reconnection with someone from the female lead’s past.',
  'Establish that the same candidate series has fewer than ten total seasons.'],
 '177': [
  'Candidate club’s season between 2011 and 2016 had three pairs of teams tied on points; candidate finished 6th–12th, tied another team and had goal difference 6–12.',
  'Candidate was based in the specified capital city as of 2023.',
  'Candidate won the relevant league between 1973 and 1983.',
  'A 2023 article jointly attributes fifteen trophies and thirteen new signings ahead of a season to the candidate.',
  'Establish the founding year and country of the club satisfying those identifying conditions.'],
 '1034': [
  'A 2022 article describes the candidate as a commercial model whose wealth mainly came from showbiz.',
  'A 2021 account gives three children in the candidate’s birth family, industry break during 2006–2010, and a child born in the United States.',
  'A 2020 article gives university entry during 2001–2007 for Business Administration.',
  'Candidate released a debut single during 2010–2015 and the 2020 article describes being hired as coordinator in 2012 then promoted to manager.',
  'Establish the birth name of the person jointly fitting the identifying article/career clues.'],
 '387': [
  'Identify Game A as a role-playing game released during 1983–1995 whose success funded further game development by the company’s founder.',
  'Link that company to Game B about a mammal blasting enemies, released about seven years later and before 1999.',
  'Identify the person behind Game B’s intro/end animation and connect them to normal 8×11-inch printing-paper animation and the wireless-keyboard PC account by 25 July 2013.',
  'The same company’s store added approximately 300–700 PC titles from publishers/developers during the specified 2015–2023 period.',
  'Establish the storage size of the identified animator’s gaming PC in the account available by 25 July 2013.'],
 '311': [
  'Candidate programme has one director and two writers.',
  'Candidate ran from January to December of an early-1990s year and produced 50–60 episodes in that year.',
  'The relevant episodes run for less than five minutes; retain any season/special scope or conflicting reports.',
  'Candidate aired on a three-character network name including a digit.',
  'Candidate was created in the country fitting three hosted World Cups by December 2023, only two of them soccer.',
  'Candidate has an educational purpose and characters including twins, a poet, a complainer and a living means of transport.',
  'Establish the Argentinian release title of the programme jointly fitting the original clues.'],
 '186': [
  'The candidate game’s developer has an amphibian name and a different original name when established in the early 1990s.',
  'Candidate game was released in November of an early-1990s year on DOS.',
  'Candidate game is single-player and shareware.',
  'Candidate game has three credited people, including two with the same surname; bind the identified game to all the clues.'],
}


def main():
    snapshots = json.load(open(OLD / 'bank/SNAPSHOTS.json'))
    questions = {s['qid']: s['question'] for s in snapshots}
    result = {qid: {'question': questions[qid],
                   'requirements': {f'R{i+1}': text for i, text in enumerate(ds)},
                   'closure_rule': 'All material identifying conditions and the requested relation must be jointly supported for the same candidate; provisional hypotheses and question premises are not evidence.',
                   'partial_coverage': 'A composite requirement remains unresolved when a necessary qualifier/subrelation is missing. A Need targeting a still-missing subrelation is valid; repeating only an already-supported subrelation is stale.',
                   'candidate_pivot': 'Discriminating or replacing a materially contradicted candidate is valid even when no individual requirement ID uniquely represents the pivot.'}
              for qid, ds in DESCRIPTIONS.items()}
    (TOP / 'bank/REQUIREMENT_MAP.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
