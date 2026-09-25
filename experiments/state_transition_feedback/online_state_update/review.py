"""Single-reviewer semantic labels of the frozen T3 proposals; no proposal edits."""
import json,sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
sys.path.insert(0,str(TOP))
from common import read,write

# (source-supported, decision-relevant, target-leak, duplicate, over-specific, reason)
LABELS={
 'U1_B01':[
  (1,1,0,0,0,'Observed biography states name, birth date, and both parental occupations.'),
  (1,1,0,0,0,'Observed biography states the 2005 film debut, director, and The Fifth Estate credit.')],
 'U1_B03':[
  (0,1,0,0,1,'Observation supports age and broad album career, but not all question clues asserted by “matching the question’s clues”.'),
  (1,0,0,0,0,'Age 66 and January 2019 are observed; after the proposed binding this adds little next-decision information.')],
 'U1_B04':[
  (1,1,0,0,0,'Match article explicitly states Messi took the free kick in PSG versus Lille.'),
  (1,1,0,0,0,'Match identity and 4–3 result appear in the observed article.')],
 'U1_B05':[
  (1,1,0,0,0,'Observed writer list has three people; this contradicts the question’s two-writer clue.'),
  (1,1,0,0,0,'Canal 13 and 1967–1996 dates in the observation contradict the original network and run-period clues.')],
 'U1_B06':[
  (1,1,0,0,0,'Game name, November 1992 DOS release, shareware, one offline player, and named credits are observed.'),
  (1,1,0,0,0,'Observed publisher is Albino Frog Software; the amphibian name matches the clue.')],
 'U1_B07':[
  (0,1,0,0,1,'Wealthy family is observed, but the inference that most wealth could not come from showbiz is not established.'),
  (1,1,0,0,0,'The source dates her start to roughly 23 years before 2021, inconsistent with a 2006–2010 break.')],
 'U1_C01':[(1,1,0,0,0,'The source explicitly names Oliver Mtukudzi and age 66; the claim is limited to the age clue.')],
 'U1_C03':[(1,1,0,0,0,'The source explicitly names Oliver Mtukudzi, age 66, and more than 60 albums.')],
 'U1_C05':[
  (1,1,0,0,0,'Observed article states Rangers, Enugu, NPFL, and 13 new players.'),
  (1,0,0,0,0,'Seven-time champions is observed but does not resolve the frozen 2016-winner Gap or original founding question.')],
 'U1_C06':[
  (1,1,0,0,0,'Observed source URL names youretheworst, and episode text matches the plot clue.'),
  (1,1,0,0,0,'Episode number, Gretchen, baby, and Heidi are stated in observed text.')],
 'U1_C07':[
  (1,1,0,0,0,'Observed text and URL link the season-four episode, plot, and series.'),
  (1,1,0,0,0,'Source URL identifies the series; observed cast and plot identify Gretchen and Jimmy.')],
 'U1_C11':[(0,1,0,0,1,'The article date is 2 October 2023, but the source does not explicitly date the match itself to that day.')],
}

def main():
    outputs={x['case_id']:x for x in read(BASE/'corrected/OUTPUTS.json')}
    cases={x['case_id']:x for x in read(TOP/'transition_bank/BANK.json')}
    out=[]
    for cid in cases:
        row=outputs[cid]
        props=(row['output'] or {'claims':[]})['claims']
        assert len(props)==len(LABELS[cid]),cid
        reviews=[]
        for i,(p,label) in enumerate(zip(props,LABELS[cid])):
            support,relevance,leak,duplicate,over,reason=label
            reviews.append({'proposal_index':i,'statement':p['statement'],
              'decision_effect':p['decision_effect'],'source_supported':bool(support),
              'decision_relevant':bool(relevance),'target_leak':bool(leak),
              'duplicate':bool(duplicate),'over_specific':bool(over),'reason':reason})
        oracle_recovered=any(r['source_supported'] and r['decision_relevant'] and
          r['decision_effect']=='candidate_binding' and
          # Lexical alias audit below is deliberately explicit, including the URL series name.
          any(alias.lower() in r['statement'].lower() for alias in {
           'U1_B01':['Peter King','Peter Nzioki'],'U1_B03':['Mtukudzi'],
           'U1_B04':['PSG','Paris Saint-Germain'],'U1_B05':['The Adventures of Hijitus'],
           'U1_B06':['Galacta'],'U1_B07':['Heart Evangelista'],
           'U1_C01':['Mtukudzi'],'U1_C03':['Mtukudzi'],
           'U1_C05':['Rangers'],'U1_C06':["You're the Worst"],
           'U1_C07':["You're the Worst"],'U1_C11':['Ding Junhui']}[cid])
          for r in reviews)
        out.append({'case_id':cid,'qid':cases[cid]['qid'],'model_error':row['error'],
          'proposals':reviews,'oracle_binding_recovered':oracle_recovered})
    write(BASE/'REVIEWS.json',out)
    print('T3 reviewed',sum(len(x['proposals']) for x in out),'proposals')

if __name__=='__main__':main()
