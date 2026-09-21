"""Evidence Pointer materialization and pointer-range contracts.

These are mechanical tests: they prove the harness recovers exact source bytes
from an address, and that no field a model could mis-copy exists in the path.
None of these tests calls a model, performs a search, or opens a window.
"""
from __future__ import annotations
from copy import deepcopy
import unittest

from experiments.research_state.evidence_pointer import contracts as ec


def window(text, ref='w_one', offset=0):
    return {'window_ref': ref, 'docid': 'doc-' + ref, 'document_sha256': 'a' * 64,
            'url': 'https://example.invalid/' + ref, 'title': '',
            'text': text, 'offset': offset, 'end_char': offset + len(text),
            'text_tokens': 20, 'title_tokens': 0}


def pointer(ref, start, end):
    return {'window_ref': ref, 'start': start, 'end': end}


class PointerRangeTests(unittest.TestCase):
    def test_full_range_and_zero_start_allowed(self):
        body = '0123456789'
        w = window(body)
        e = ec.materialize(pointer('w_one', 0, len(body)), w, '42', 0)
        self.assertEqual(e['text'], body)
        self.assertEqual(e['relative_start'], 0)
        self.assertEqual(e['relative_end'], 10)
        self.assertEqual(e['absolute_start'], 0)
        self.assertEqual(e['absolute_end'], 10)

    def test_empty_range_rejected(self):
        with self.assertRaises(ValueError):
            ec.check_pointer_selection({'observation': [window('abc')]},
                                       ec.seal({'pointers': [pointer('w_one', 3, 3)]}))

    def test_negative_rejected(self):
        sel = {'observation': [window('abc')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', -1, 2)]}))
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', 0, -1)]}))

    def test_reversed_rejected(self):
        with self.assertRaises(ValueError):
            ec.check_pointer_selection({'observation': [window('abc')]},
                                       ec.seal({'pointers': [pointer('w_one', 2, 1)]}))

    def test_out_of_range_rejected(self):
        sel = {'observation': [window('abc')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', 0, 99)]}))
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', 99, 100)]}))

    def test_bool_cannot_impersonate_int(self):
        sel = {'observation': [window('abc')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', True, 2)]}))
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal({'pointers': [pointer('w_one', 0, True)]}))

    def test_float_rejected(self):
        with self.assertRaises(ValueError):
            ec.check_pointer_selection({'observation': [window('abcdef')]},
                                       ec.seal({'pointers': [pointer('w_one', 0.0, 3.0)]}))

    def test_pointer_cannot_cross_window(self):
        two = [window('AAAA', 'w_a'), window('BBBB', 'w_b')]
        with self.assertRaises(ValueError):
            ec.check_pointer_selection({'observation': two},
                                       ec.seal({'pointers': [{'window_ref': 'w_a',
                                                              'start': 0, 'end': 8}]}))

    def test_invisible_window_rejected(self):
        with self.assertRaises(ValueError):
            ec.check_pointer_selection({'observation': [window('abc')]},
                                       ec.seal({'pointers': [pointer('w_secret', 0, 1)]}))

    def test_duplicate_pointer_rejected(self):
        sel = {'observation': [window('abcdef')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal(
                {'pointers': [pointer('w_one', 0, 2), pointer('w_one', 0, 2)]}))

    def test_more_than_two_rejected(self):
        sel = {'observation': [window('abcdef')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal(
                {'pointers': [pointer('w_one', 0, 1), pointer('w_one', 1, 2),
                              pointer('w_one', 2, 3)]}))

    def test_extra_pointer_field_rejected(self):
        sel = {'observation': [window('abc')]}
        with self.assertRaises(ValueError):
            ec.check_pointer_selection(sel, ec.seal(
                {'pointers': [{'window_ref': 'w_one', 'start': 0, 'end': 1, 'quote': 'a'}]}))

    def test_rationale_stays_outside_pointer(self):
        sel = {'observation': [window('abc')]}
        checked = ec.check_pointer_selection(sel, ec.seal(
            {'pointers': [], 'rationale': 'nothing load-bearing'}))
        self.assertEqual(checked['pointers'], [])
        self.assertEqual(checked['rationale'], 'nothing load-bearing')

    def test_addressing_unseen_text_is_impossible(self):
        """The address space is exactly the visible window body; there is no way to
        name a character the observation does not display."""
        body = 'visible text'
        w = window(body)
        e = ec.materialize(pointer('w_one', 0, len(body)), w, '1', 0)
        self.assertEqual(e['text'], body)
        with self.assertRaises(ValueError):
            ec.materialize(pointer('w_one', 0, len(body) + 1), w, '1', 0)


class ExactRecoveryTests(unittest.TestCase):
    """Every failure mode that invalidated the note batch must be structurally
    impossible here, because the text is sliced rather than copied."""

    BODY = ('First paragraph.\n\nSecond paragraph with £8\xa0million and '
            '“smart quotes” and ellipsis… and emoji 🎉 and 中文 тест  '
            '\t \xa0 trailing.\n\nThird.')

    def test_round_trip_every_hard_case(self):
        w = window(self.BODY)
        # Paragraph break, exactly where the note batch failed by flattening \n\n.
        e1 = ec.materialize(pointer('w_one', 0, self.BODY.index('Second') + 6), w, '7', 0)
        self.assertEqual(e1['text'], 'First paragraph.\n\nSecond')
        # NBSP, exactly where £8\xa0million was normalised to a space.
        e2 = ec.materialize(pointer('w_one', self.BODY.index('£8'), self.BODY.index('£8') + 10),
                            w, '7', 1)
        self.assertEqual(e2['text'], '£8\xa0million')
        # Smart quotes, exactly where " was rewritten as '.
        e3 = ec.materialize(pointer('w_one', self.BODY.index('“'), self.BODY.index('”') + 1),
                            w, '7', 2)
        self.assertEqual(e3['text'], '“smart quotes”')
        # All recovered bytes are identical to the source slice.
        for e in (e1, e2, e3):
            self.assertEqual(e['text'], self.BODY[e['relative_start']:e['relative_end']])

    def test_ellipsis_and_tabs_survive(self):
        w = window(self.BODY)
        span = self.BODY.index('ellipsis') + 8
        e = ec.materialize(pointer('w_one', span, span + 1), w, '7', 0)
        self.assertEqual(e['text'], '…')
        tab = self.BODY.index('\t')
        e2 = ec.materialize(pointer('w_one', tab, tab + 3), w, '7', 1)
        self.assertEqual(e2['text'], '\t \xa0')

    def test_repeated_identical_substring_resolves_to_the_requested_one(self):
        body = 'noise coin coin noise'
        w = window(body)
        first = ec.materialize(pointer('w_one', 6, 10), w, '7', 0)
        second = ec.materialize(pointer('w_one', 11, 15), w, '7', 1)
        self.assertEqual(first['text'], 'coin')
        self.assertEqual(second['text'], 'coin')
        self.assertNotEqual(first['relative_start'], second['relative_start'])

    def test_absolute_range_is_offset_plus_relative(self):
        body = 'abcdefgh'
        w = window(body, offset=9312)
        e = ec.materialize(pointer('w_one', 2, 6), w, '7', 0)
        self.assertEqual(e['absolute_start'], 9314)
        self.assertEqual(e['absolute_end'], 9318)
        self.assertEqual(w['text'][e['relative_start']:e['relative_end']], e['text'])

    def test_provenance_is_harvested_not_declared(self):
        body = 'source bytes'
        w = window(body, ref='w_proof', offset=500)
        e = ec.materialize(pointer('w_proof', 0, 5), w, '19', 0)
        self.assertEqual(e['evidence_id'], 'E1')
        self.assertEqual(e['attempt_id'], 'A0:19')
        self.assertEqual(e['docid'], 'doc-w_proof')
        self.assertEqual(e['document_sha256'], w['document_sha256'])
        self.assertEqual(e['url'], w['url'])
        # The reviewer supplies none of these: the pointer is an address only.
        self.assertEqual(set(pointer('w_proof', 0, 5)), {'window_ref', 'start', 'end'})

    def test_evidence_shape_is_closed(self):
        w = window('abc')
        e = ec.materialize(pointer('w_one', 0, 3), w, '1', 0)
        self.assertEqual(set(e), set(ec._STATE_FIELDS))
        bad = deepcopy(e)
        bad['statement'] = 'a semantic claim'
        with self.assertRaises(ValueError):
            ec.check_evidence(bad, [w])

    def test_empty_evidence_state_is_legal(self):
        msg = ec.state_message([], None)
        self.assertEqual(msg, {'kind': 'evidence_pointer_state', 'evidence': []})

    def test_show_window_only_annotates(self):
        body = '0123456789'
        view = ec.show_window(window(body), width=4)
        self.assertIn('char 0:4', view)
        self.assertIn('char 8:10', view)
        # Body characters survive annotation, in order, and are never rewritten.
        kept = [ln for ln in view.split('\n') if not ln.startswith('char ')]
        self.assertEqual(''.join(kept), body)
        # The annotation is not part of any state or request.
        self.assertNotIn('char ', ec.canonical(ec.state_message(
            [ec.materialize(pointer('w_one', 0, 3), window(body), '1', 0)], None)))


class TamperTests(unittest.TestCase):
    """Freezing a pointer must bind it to the exact source bytes."""

    def setUp(self):
        self.body = 'stable text here'
        self.w = window(self.body)
        self.obs = [self.w]
        self.e = ec.materialize(pointer('w_one', 7, 11), self.w, '3', 0)

    def test_text_change_rejected(self):
        bad = [deepcopy(self.w)]
        bad[0]['text'] = 'stable TEXT here'
        bad[0]['end_char'] = bad[0]['offset'] + len(bad[0]['text'])
        with self.assertRaises(ValueError):
            ec.check_evidence(self.e, bad)

    def test_hash_change_rejected(self):
        bad = [deepcopy(self.w)]
        bad[0]['document_sha256'] = 'b' * 64
        with self.assertRaises(ValueError):
            ec.check_evidence(self.e, bad)

    def test_offset_change_rejected(self):
        bad = [deepcopy(self.w)]
        bad[0]['offset'] = 999
        with self.assertRaises(ValueError):
            ec.check_evidence(self.e, bad)

    def test_window_removed_rejected(self):
        with self.assertRaises(ValueError):
            ec.check_evidence(self.e, [])

    def test_url_change_rejected(self):
        bad = [deepcopy(self.w)]
        bad[0]['url'] = 'https://example.invalid/other'
        with self.assertRaises(ValueError):
            ec.check_evidence(self.e, bad)

    def test_untampered_passes(self):
        self.assertIs(ec.check_evidence(self.e, self.obs), self.e)


if __name__ == '__main__':
    unittest.main()
