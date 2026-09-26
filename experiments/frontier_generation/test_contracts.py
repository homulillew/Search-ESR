import unittest, copy
from runtime import TOP, rd, view, item, decode, dg

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.bank=rd(TOP/'bank/CHECKPOINT_BANK.json')
    def test_views_have_only_authorized_keys(self):
        for c in self.bank:
            for arm in ['H','S','SH']:
                v=view(c,arm)
                expected={'Original Question','Mechanical Context'}
                if arm!='H':expected|={'Verified Claims','Working Hypothesis'}
                if arm!='S':expected|={'Chronological Research History'}
                self.assertEqual(set(v),expected)
                self.assertLessEqual(len(v['Mechanical Context']['recent_tool_attempts']),2)
                for a in v['Mechanical Context']['recent_tool_attempts']:self.assertEqual(set(a),{'tool','query','status'})
            self.assertEqual(view(c,'S')['Verified Claims'],[x['statement'] for x in c['state']['verified_claims']])
    def test_no_hidden_fields_reach_view(self):
        c=copy.deepcopy(self.bank[0]);baseline={a:dg(view(c,a)) for a in ['H','S','SH']}
        c.update(gold='SENTINEL',coverage='SENTINEL',previous_gap='SENTINEL')
        c['state'].update(available_workspace='SENTINEL',historical_active_gap='SENTINEL',hypothesis_provenance='SENTINEL')
        self.assertEqual(baseline,{a:dg(view(c,a)) for a in baseline})
    def test_paired_requests_identical_except_metadata(self):
        for c in self.bank:
            for a in ['H','S','SH']:
                self.assertEqual(item(c,a,1)['request'],item(c,a,2)['request'])
    def test_actual_state_history_hashes_and_coverage(self):
        labels=rd(TOP/'bank/COVERAGE.json');self.assertEqual(len(labels),24)
        for c in self.bank:
            self.assertEqual(dg(c['state']),c['state_sha256']);self.assertEqual(dg(c['history']),c['history_sha256'])
            self.assertIn(c['case_id'],labels)
    def test_contract_rejects_extra_keys_and_empty_act(self):
        def raw(s,finish='stop'):return {'choices':[{'finish_reason':finish,'message':{'content':s}}]}
        self.assertEqual(decode(raw('{"decision":"stop","need":""}'))['decision'],'stop')
        for s in ['{"decision":"act","need":" "}','{"decision":"stop","need":"why"}','{"decision":"act","need":"why","query":"x"}']:
            with self.assertRaises(Exception):decode(raw(s))
        with self.assertRaises(EOFError):decode(raw('{"decision":"stop","need":""}','length'))

if __name__=='__main__':unittest.main()
