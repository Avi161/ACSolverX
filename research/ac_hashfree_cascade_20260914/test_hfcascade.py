"""Focused tests for the hash-free cascade and its independent verifier."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_hashfree_cascade_20260914 import hfcascade as hf  # noqa: E402
from research.ac_hashfree_cascade_20260914 import verify  # noqa: E402
from experiments.equivalence_classes.lib.words import canon_pair, apply_hom  # noqa: E402


class Syllables(unittest.TestCase):
    def test_cyclic_merge(self):
        self.assertEqual(hf.syllables('xxYYx'), [('x', 3), ('y', -2)])
        self.assertEqual(hf.from_syllables([('y', -2), ('x', 3)]), 'YYxxx')
        self.assertEqual(hf._merge([('x', 1), ('y', 0), ('x', -1), ('y', 2)]), [('y', 2)])

    def test_conjugation_forms(self):
        forms = hf.conjugation_forms('YXXyx')            # y^-1 x^-2 y x
        self.assertIn(('y', 1, 'x', 1, -2), forms)          # y x y^-1 x^-2
        self.assertEqual(hf.conjugation_forms('YYXXyx'), [])   # y^-2 x^-2 y x: no opposite pair
        self.assertIn(('x', 2, 'y', -2, 1), hf.conjugation_forms('YYXXyxx'))

    def test_pinch_rule_is_a_relation_consequence(self):
        # every rule use must be a single rotation product; check on the n=3 BS family
        r = hf.solve(('YXXyx', 'YYYYXyyyx'), budget=200)
        self.assertTrue(r['solved'])
        self.assertEqual(r['stage'], 'C')
        verify.replay(('YXXyx', 'YYYYXyyyx'), r['steps'], r['states'])


class Stages(unittest.TestCase):
    def test_primitive_deletion(self):
        r = hf.solve(('YYXyx', 'Yx'), budget=50)
        self.assertTrue(r['solved'])
        self.assertEqual(verify.replay(('YYXyx', 'Yx'), r['steps'], r['states']), ('Y', 'X'))

    def test_one_occurrence_gate_finishes_from_a_child(self):
        r = hf.solve(('YYXyx', 'YXXyx'), budget=100, width=4)
        self.assertTrue(r['solved'])
        verify.replay(('YYXyx', 'YXXyx'), r['steps'], r['states'])

    def test_beam_is_hash_free_and_bounded(self):
        r = hf.solve(('YYXXXyX', 'YXYxyXXX'), budget=60, width=4)
        self.assertFalse(r['solved'])
        self.assertEqual(r['units'], 60)

    def test_one_occurrence_finisher_is_cheap(self):
        pair = ('YXXyx', 'YYYYYYYYXyyyyyyyx')         # BS(1,2) donor, n = 7 companion
        r = hf.solve(pair, budget=1000, engine='fast', score='length', nielsen=True)
        self.assertTrue(r['solved'])
        self.assertEqual(r['stage'], 'C')
        self.assertLessEqual(r['units'], 300)
        verify.replay(pair, r['steps'], r['states'])

    def test_units_never_exceed_budget_on_solves(self):
        for pair in (('YXXyx', 'YYYYYYYYXyyyyyyyx'), ('YXXyXyx', 'YYXyxxyXX')):
            r = hf.solve(pair, budget=1000)
            if r['solved']:
                self.assertLessEqual(r['units'], 1000)
                verify.replay(pair, r['steps'], r['states'])

    def test_sorted_closed_set_matches_hashed_control(self):
        for pair in (('YXXYxYxx', 'YYYxxYXYx'), ('YXyxYXXyx', 'YYXyXXXyxYX')):
            a = hf.solve(pair, budget=1000, engine='bestfirst', score='length', closed_set='sorted')
            b = hf.solve(pair, budget=1000, engine='bestfirst', score='length', closed_set='hash')
            self.assertTrue(a['solved'])
            self.assertEqual((a['units'], a['path_length']), (b['units'], b['path_length']))
            verify.replay(pair, a['steps'], a['states'])

    def test_memoryless_variants_run_and_stay_in_budget(self):
        pair = ('YXXYxYxx', 'YYYxxYXYx')
        for cfg in (dict(engine='bestfirst', frontier_dedup=True, ancestors=50),
                    dict(engine='beam', width=4, ancestors=50)):
            r = hf.solve(pair, budget=120, score='length', **cfg)
            self.assertLessEqual(r['units'], 120)
            if r['solved']:
                verify.replay(pair, r['steps'], r['states'])

    def test_fast_engine_agrees_with_pure_python_engine(self):
        for pair in (('YXXYxYxx', 'YYYxxYXYx'), ('YYXXXXyx', 'YYXXXYXXyXX')):
            a = hf.solve(pair, budget=1000, engine='bestfirst', score='length', closed_set='sorted', nielsen=True,
                         gates=True)
            b = hf.solve(pair, budget=1000, engine='fast', score='length', nielsen=True, gate_when='generated')
            self.assertTrue(a['solved'] and b['solved'])
            # the fast engine deduplicates at pop time, so its depth tie-break can differ slightly
            self.assertLess(abs(a['units'] - b['units']), 0.2 * a['units'] + 5)
            verify.replay(pair, b['steps'], b['states'])
        c = hf.solve(('YYXXXXYX', 'YYYXYXyyX'), budget=1000, engine='fast', score='length', nielsen=True, perms=True)
        self.assertTrue(c['solved'])
        verify.replay(('YYXXXXYX', 'YYYXYXyyX'), c['steps'], c['states'])

    def test_nontrivial_group_is_not_solved(self):
        # <x,y | x^2, y> is Z/2: abelianisation det 2, every stage must fail cleanly
        r = hf.solve(('xx', 'y'), budget=100)
        self.assertFalse(r['solved'])


class Hybrid(unittest.TestCase):
    def test_hybrid_solves_rank_two_rows_like_the_fast_engine(self):
        from research.ac_hashfree_cascade_20260914 import hfhybrid as HY
        for pair in (('YXXYxYxx', 'YYYxxYXYx'), ('YYXXXXyx', 'YYXXXYXXyXX'), ('YXXyx', 'YYYYYYYYXyyyyyyyx')):
            r = HY.solve(pair, budget=1000)
            self.assertTrue(r['solved'])
            self.assertTrue(r['explicit_rank2'])
            self.assertEqual(HY.verify_hybrid(pair, r['steps']), ('Y', 'X'))

    def test_hybrid_uses_dynamic_rank_on_a_hard_row_and_certificate_replays(self):
        from research.ac_hashfree_cascade_20260914 import hfhybrid as HY
        pair = ('YXXXyxx', 'YYXyXYxyxYXXyx')          # rank-two search needs ~9,500 units
        r = HY.solve(pair, budget=1000)
        self.assertTrue(r['solved'])
        self.assertLessEqual(r['units'], 1000)
        self.assertEqual(HY.verify_hybrid(pair, r['steps']), ('Y', 'X'))
        self.assertGreaterEqual(r['max_rank'], 3)
        bad = [dict(s) for s in r['steps']]
        idx = next(i for i, s in enumerate(bad) if s['kind'] == 'dyn')
        bad[idx] = dict(bad[idx], after=[[1, 2]] * len(bad[idx]['after']))
        with self.assertRaises((HY.DV.Failure, HY.SV.Failure)):
            HY.verify_hybrid(pair, bad)


class Verifier(unittest.TestCase):
    def test_tampering_is_caught(self):
        pair = ('YXXyx', 'YYYYXyyyx')
        r = hf.solve(pair, budget=200)
        steps = [dict(s) for s in r['steps']]
        steps[-1] = {'kind': 'substitution', 'move': '1_1_0_0'}
        with self.assertRaises(verify.Failure):
            verify.replay(pair, steps, r['states'])
        bad = {'kind': 'automorphism', 'images': {'x': 'xx', 'y': 'y'}}
        with self.assertRaises(verify.Failure):
            verify.replay(pair, [bad] + r['steps'], None)

    def test_canonical_forms_agree_with_repository(self):
        for w in ('xyXY', 'YYXyx', 'xxyXXY', 'yXyXX'):
            self.assertEqual(canon_pair(w, 'x')[0] if len(w) == 1 else canon_pair(w, 'xyxyxyxyxyxyxy')[0],
                             verify.canon_pair(w, 'xyxyxyxyxyxyxy')[0])


if __name__ == '__main__':
    unittest.main()


class ACMoveCount(unittest.TestCase):
    """`acmoves.count` must agree with the repository's own certificate decoder.

    The count asserts that a hybrid certificate costs one ordinary AC substitution
    per `substitution` step plus one per Nielsen image, and nothing for a signed
    permutation.  The decoder is the authority: it transports the basis change back
    through the path and replays the result to (x, y) without canonicalisation.
    """

    def _check(self, pair):
        from research.ac_hashfree_cascade_20260914 import hfhybrid, acmoves
        res = hfhybrid.solve(pair, budget=1000)
        self.assertTrue(res['solved'], pair)
        self.assertTrue(res['explicit_rank2'], pair)
        formula = acmoves.count(res['steps'])
        decoded = acmoves.decode_counts(pair, res['steps'])
        self.assertEqual(formula['ac_moves'], decoded['multiply'], pair)
        self.assertEqual(formula['ac_moves'],
                         formula['substitution'] + formula['nielsen'], pair)

    def test_matches_decoder_on_search_rows(self):
        for pair in (('YXyXXXyx', 'YYXXyXYXyxYxxxyyX'),   # 156 AC moves, 3 Nielsen, 1 perm
                     ('YXXXyxYxx', 'YYYxxYYXXX'),           # 154 AC moves, 3 Nielsen, 2 perms
                     ('YXXXyxYxx', 'YYXYxxxYXXX')):
            with self.subTest(pair=pair):
                self._check(pair)

    def test_terminal_and_short_rows(self):
        from research.ac_hashfree_cascade_20260914 import acmoves
        self.assertEqual(acmoves.count([])['ac_moves'], 0)
        for pair in (('X', 'YYXyx'), ('YX', 'YYYXyXXyx')):
            with self.subTest(pair=pair):
                self._check(pair)

    def test_stable_certificate_has_no_rank_two_count(self):
        from research.ac_hashfree_cascade_20260914 import acmoves
        c = acmoves.count([{'kind': 'substitution', 'move': '1_1_0_0'},
                           {'kind': 'dyn', 'event': 'define', 'relabel': None, 'after': ()}])
        self.assertTrue(c['stable'])
        self.assertIsNone(c['ac_moves'])
