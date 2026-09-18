import copy
import json
from experiments.observation_summary.summary import build_summary, request_with_summary, PREFIX


class CharTokenizer:
    def encode(self, text, **kwargs):
        return list(text)


def event(seq, new, repeat=False):
    return dict(sequence=seq, active=True, tool='search', result=[dict(window_ref='w_test', offset=10,end_char=20)],
        observations=[dict(window_ref='w_test',docid='1',new_chars=new,body_new_spans=[] if not new else [[10,20]],body_overlap_chars=10-new,repeated_window=repeat)])


def test_summary_records_zero_and_partial_without_mutating_inputs():
    events=[event(1,10),event(2,0,True)];before=copy.deepcopy(events)
    summary=build_summary(events,1,CharTokenizer(),2000)
    p=json.loads(summary['content'][len(PREFIX):])
    assert p['recent_search_new_source_chars']==[10,0]
    assert p['windows'][0]['new_body']==[]
    assert p['windows'][0]['repeated_window'] is True
    request={'messages':[{'role':'tool','content':'unchanged'}]}
    enriched=request_with_summary(request,summary)
    assert len(enriched['messages'])==2 and len(request['messages'])==1
    assert events==before
    assert build_summary(events,2,CharTokenizer()) is None


def test_summary_budget_reports_omission_and_keeps_totals():
    events=[event(1,10)];events[0]['observations']*=40;events[0]['result']*=40
    summary=build_summary(events,0,CharTokenizer(),1200)
    p=json.loads(summary['content'][len(PREFIX):])
    assert len(summary['content'])<=1200 and p['omitted_windows']>0
    assert len(p['windows'])+p['omitted_windows']==40
    assert p['latest_calls'][0]['new_source_chars']==400
