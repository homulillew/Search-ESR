"""Test denominator/censoring boundaries, not historical score targets."""
import unittest
from unittest.mock import patch
from .common import project
from .e0 import summarize, temporal, temporal_summary

def row(case, gold, pred, arm='A1'):
    node={'requirement_id':'R1','gold_control':gold,'predicted_control':pred,'false_close':gold=='OPEN' and pred=='CLOSED'}
    return {'id':case,'case_id':case,'qid':'q','arm':arm,'replicate':1,'schema_valid':True,'nodes':[node],
      'false_close_ids':['R1'] if node['false_close'] else []}
class BoundaryTests(unittest.TestCase):
    def test_projection(self):
        self.assertEqual(project('unsupported'),project('partially_supported'))
        self.assertEqual(project('fully_supported'),'CLOSED')
        with self.assertRaises(ValueError):project('invalid')
    def test_four_successor_outcomes_and_censoring(self):
        for pair,outcome in [(('OPEN','OPEN'),'recovered_open'),(('CLOSED','CLOSED'),'became_justified'),(('OPEN','CLOSED'),'persistent_false_close'),(('CLOSED','OPEN'),'reopened_incorrectly')]:
            with patch('experiments.recoverable_control_equivalence.e0.read',return_value=[{'from':'a','to':'b','eligible':True}]):
                events=temporal([row('a','OPEN','CLOSED'),row('b',*pair)])['events']
            self.assertEqual(events[0]['outcome'],outcome)
            stats=temporal_summary(events)
            self.assertEqual(stats['safe_resolution_rate']['denominator'],1)
            self.assertEqual(stats['safe_resolution_rate']['numerator'],int(outcome in ('recovered_open','became_justified')))
            self.assertEqual(stats['recoverability_status'],'INSUFFICIENT_NATURAL_DENOMINATOR')
    def test_excluded_refinement_not_skipped(self):
        pairs=[{'from':'a','to':'b','eligible':False},{'from':'b','to':'c','eligible':True}]
        with patch('experiments.recoverable_control_equivalence.e0.read',return_value=pairs):
            events=temporal([row('a','OPEN','CLOSED'),row('b','OPEN','OPEN'),row('c','OPEN','OPEN')])['events']
        self.assertEqual(events[0]['outcome'],'right_censored_no_eligible_successor')
        self.assertIsNone(temporal_summary(events)['safe_resolution_rate']['value'])
    def test_empty_denominator_not_success(self):
        stats=temporal_summary([])
        self.assertIsNone(stats['safe_resolution_rate']['value'])
        self.assertIsNone(stats['median_recovery_steps'])
    def test_consecutive_states_not_edges(self):
        pairs=[{'from':'a','to':'b','eligible':True},{'from':'b','to':'c','eligible':True}]
        with patch('experiments.recoverable_control_equivalence.e0.read',return_value=pairs):
            events=temporal([row('a','OPEN','CLOSED'),row('b','OPEN','CLOSED'),row('c','OPEN','OPEN')])['events']
        self.assertEqual(events[0]['consecutive_false_close_observed_states'],2)
        self.assertEqual(events[0]['recovered_open_steps'],2)
if __name__=='__main__':unittest.main()
