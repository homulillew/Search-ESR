import json
import unittest
from unittest.mock import patch
from .selection import selection_metrics
from .run import authorization
from experiments.skeleton_state_alignment.run import parse_response

class SelectionBoundaryTests(unittest.TestCase):
    def sample(self,selection,input_mask):
        job={'id':'x','case_id':'g','request':{'model':'deepseek-flash','messages':[{}, {'content':json.dumps({'Task Skeleton':[{'requirement_id':'R1'},{'requirement_id':'R2'}],'Control Mask':input_mask})}]},'stage':'e1_selection'}
        row={'id':'x','case_id':'g','valid_output':True,'output':{'selection':selection}}
        refs={'g':{'acceptable_active_ids':['R1'],'invalid_supported_ids':['R2'],'blocked_or_downstream_ids':[],'other_invalid_ids':[],'stop_allowed':False}}
        return selection_metrics([row],{'x':job},refs)['metrics'],job
    def test_gold_closed_and_input_closed_distinct(self):
        m,_=self.sample('R1',{'R1':'CLOSED','R2':'OPEN'})
        self.assertEqual(m['selected_closed']['numerator'],0)
        self.assertEqual(m['selected_input_closed']['numerator'],1)
    def test_false_stop_vs_input_mask_stop_distinct(self):
        m,_=self.sample('STOP',{'R1':'CLOSED','R2':'CLOSED'})
        self.assertEqual(m['false_stop']['numerator'],1)
        self.assertEqual(m['input_mask_false_stop']['numerator'],0)
    def test_reused_transport_parser_accepts_new_stage(self):
        _,job=self.sample('R1',{'R1':'OPEN','R2':'CLOSED'})
        raw={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':'{"selection":"R1"}'}}]}
        self.assertTrue(parse_response(200,json.dumps(raw),job)['valid_output'])
        raw['choices'][0]['message']['content']='{"selection":"R1","reason":"extra"}'
        self.assertFalse(parse_response(200,json.dumps(raw),job)['valid_output'])
    def test_no_inherited_authorization(self):
        with patch('pathlib.Path.exists',return_value=False):
            with self.assertRaises(PermissionError):authorization()
if __name__=='__main__':unittest.main()
