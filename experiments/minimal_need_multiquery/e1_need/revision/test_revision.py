"""Offline boundary checks for the new advancement guard."""
import copy
import unittest
from .run import gate


class GateTest(unittest.TestCase):
    def fixture(self):
        arms = {a: {'n': 18, 'strict_valid': n, 'p_plus_a_sum': 1, 'codes': {'W': 0}, 'valid_output': 18}
                for a, n in [('B0', 13), ('B3', 16)]}
        return arms, {'B3': {'n': 8, 'strict_valid': 7}}

    def test_boundary_pass_only_opens_fresh(self):
        arms, no_h = self.fixture()
        result = gate(arms, no_h)
        self.assertEqual(result['status'], 'PASS_TO_FRESH_E1')
        self.assertFalse(result['opens_E2'])

    def test_each_criterion_is_required(self):
        for field, value in [('n', 17), ('strict_valid', 15), ('p_plus_a_sum', 2), ('valid_output', 16)]:
            with self.subTest(field=field):
                arms, no_h = self.fixture()
                arms['B3'][field] = value
                self.assertEqual(gate(arms, no_h)['status'], 'STOP_E1_NO_MORE_REVISIONS')
        arms, no_h = self.fixture()
        arms['B0']['strict_valid'] = 14
        self.assertEqual(gate(arms, no_h)['status'], 'STOP_E1_NO_MORE_REVISIONS')
        arms, no_h = self.fixture()
        arms['B3']['codes']['W'] = 1
        self.assertEqual(gate(arms, no_h)['status'], 'STOP_E1_NO_MORE_REVISIONS')
        arms, no_h = self.fixture()
        no_h['B3']['strict_valid'] = 6
        self.assertEqual(gate(arms, no_h)['status'], 'STOP_E1_NO_MORE_REVISIONS')

    def test_failed_baseline_outputs_do_not_open_gate(self):
        arms, no_h = self.fixture()
        arms['B0']['valid_output'] = 16
        self.assertEqual(gate(arms, no_h)['status'], 'STOP_E1_NO_MORE_REVISIONS')


if __name__ == '__main__':
    unittest.main()
