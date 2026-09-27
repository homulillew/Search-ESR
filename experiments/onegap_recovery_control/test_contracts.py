"""Offline tests for permission boundaries, paired isolation and failure counting."""
import copy
import unittest
from .harness import valid_output, read, accounting
from .score import calculate


class Contracts(unittest.TestCase):
    def setUp(self):
        self.s = read('e0_state_bank/STATES.json')['S06']
        self.output = {'focus_requirement_id': 'R4', 'one_gap': 'Verify whether the target book references Euler.',
                       'strategy': 'VERIFY_RELATION', 'hypothesis_ids_under_test': ['H1'],
                       'action': {'type': 'SEARCH', 'query': 'book Euler telephone telegraph', 'source_ref': None, 'pattern': None}}

    def test_state_authority_and_handle_validation(self):
        self.assertTrue(valid_output(self.output, self.s))
        for key in ('C', 'Q', 'R', 'covered', 'final_answer'):
            invalid = dict(self.output, **{key: []})
            self.assertFalse(valid_output(invalid, self.s))
        x = copy.deepcopy(self.output)
        x['action'] = {'type': 'FIND', 'source_ref': 'D999999', 'query': None, 'pattern': 'Euler'}
        self.assertFalse(valid_output(x, self.s))
        x['action'] = {'type': 'STOP', 'source_ref': None, 'query': None, 'pattern': None}
        self.assertFalse(valid_output(x, self.s))

    def test_pair_isolation(self):
        bank = read('e0_state_bank/STATES.json')
        for v in read('e0_state_bank/VARIANTS.json'):
            for key in ('Q', 'R', 'C'):
                self.assertEqual(v['state'][key], bank[v['state_id']][key])
            if v['condition'] == 'P1': self.assertEqual(v['state']['TraceView'], bank[v['state_id']]['TraceView'])

    def test_failures_remain_in_denominator(self):
        rows = []
        for i, condition in enumerate(('P0', 'P1', 'P2', 'P3')):
            rows.append({'id': 'S1__'+condition, 'state_id': 'S1', 'condition': condition,
                         'schema_valid': condition != 'P2', 'label': None if condition == 'P2' else 'ACCEPTABLE',
                         'tags': [], 'authority_violations': [], 'material_route_change': None,
                         'promising_response': 'local' if condition == 'P3' else None, 'action_type': 'SEARCH'})
        m = calculate(rows)
        self.assertEqual(m['nogain_escape_scheduled'], {'numerator': 0, 'denominator': 1, 'rate': 0})
        self.assertEqual(m['same_route_P2_conservative']['rate'], 1)
        self.assertEqual(m['gate'], 'FAIL')

    def test_cache_weighting_and_missing_usage(self):
        rows = [{'usage': {'prompt_tokens': 100, 'prompt_cache_hit_tokens': 50, 'prompt_cache_miss_tokens': 50}},
                {'usage': {'prompt_tokens': 900, 'prompt_cache_hit_tokens': 90, 'prompt_cache_miss_tokens': 810}},
                {'usage': None, 'failure': 'timeout'},
                {'usage': {'prompt_tokens': 30, 'prompt_cache_hit_tokens': 30, 'prompt_cache_miss_tokens': 30}}]
        a = accounting(rows)
        self.assertEqual(a['cache_hit_rate'], .14)
        self.assertEqual(a['planned_slots'], 4)
        self.assertEqual(a['usage_missing'], 1)
        self.assertEqual(a['usage_inconsistent'], 1)


if __name__ == '__main__': unittest.main()
