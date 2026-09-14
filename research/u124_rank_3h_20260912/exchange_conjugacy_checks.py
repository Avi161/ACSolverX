"""Tiny exact conjugator-coset and opposite-sign exchange controls."""
from copy import deepcopy
import json
import unittest

import exchange_conjugacy as conjugacy
import exchange_templates
import search


DEFINITION = (1, 2, -1, -2)
ROW = search.reduced(DEFINITION + (1,) + search.inverse(DEFINITION) + (2,))
PLANTED = search.normalize((ROW, (1,) + ROW))


class ConjugacyChecks(unittest.TestCase):
    def test_noncyclic_source_conjugates_its_centralizer_root(self):
        source = (11, 7, 7, -11)
        chosen = (13, 17, -13)
        target = search.reduced(chosen + source + search.inverse(chosen))
        coset = conjugacy.conjugator_coset(source, target)
        self.assertEqual(coset['centralizer_root'], (11, 7, -11))
        self.assertEqual(coset['centralizer_exponent'], 2)
        for k in range(-2, 3):
            w = search.reduced(coset['base_conjugator'] + conjugacy._power(coset['centralizer_root'], k))
            self.assertEqual(search.reduced(w + source + search.inverse(w)), target)

    def test_cyclic_rotation_and_inverse_are_distinguished(self):
        coset = conjugacy.conjugator_coset((1, 2, 1, 2), (2, 1, 2, 1))
        self.assertEqual(coset['rotation_cut'], 1)
        self.assertEqual(coset['base_conjugator'], (-1,))
        self.assertEqual(coset['centralizer_root'], (1, 2))
        self.assertIsNone(conjugacy.conjugator_coset(DEFINITION, search.inverse(DEFINITION)))
        self.assertIsNone(conjugacy.conjugator_coset((1,), (1, 1)))
        with self.assertRaises(ValueError):
            conjugacy.conjugator_coset((), ())

    def test_hidden_definition_and_forced_template_replay(self):
        plans, cost = conjugacy.discover(PLANTED, 500)
        self.assertEqual(cost, 500)
        plan = next(p for p in plans if p['defining_word'] == DEFINITION)
        self.assertTrue(conjugacy.replay_conjugacy(json.loads(json.dumps(plan['witnesses'][0]))))
        after, event, charged = conjugacy.compile_plan(PLANTED, plan, 200)
        self.assertEqual(exchange_templates.replay(json.loads(json.dumps(event))), after)
        self.assertEqual(sum(event['work_counts'].values()), charged)
        self.assertEqual(search.reduced(((1,) + ROW) + search.inverse(ROW)), (1,))
        self.assertEqual(search.reduced(tuple(x for x in ROW if abs(x) != 1)), (2,))

    def test_budget_includes_context_failures_and_centralizer_choices(self):
        for budget in (0, 1, 5, 31, 99):
            _, charged = conjugacy.discover(PLANTED, budget)
            self.assertEqual(charged, budget)
            _, charged = conjugacy.probe(PLANTED, budget)
            self.assertLessEqual(charged, budget)
        options, charged = conjugacy.probe(PLANTED, 1000)
        self.assertEqual(charged, 1000)
        self.assertLess(search.length(options[0][0]), search.length(PLANTED))

    def test_long_contexts_arbitrary_rank_and_large_labels(self):
        words = search.normalize(PLANTED + tuple((10**30 + i,) for i in range(9)))
        _, charged = conjugacy.discover(words, 40, contexts=((), (1, 2, -1), (2, 2), (-1,)))
        self.assertEqual((len(words), charged), (11, 40))

    def test_corrupted_conjugator_and_nonprimitive_root_are_rejected(self):
        plans, _ = conjugacy.discover(PLANTED, 500)
        witness = deepcopy(plans[0]['witnesses'][0])
        witness['coset']['base_conjugator'] = ()
        with self.assertRaises(AssertionError):
            conjugacy.replay_conjugacy(witness)
        witness = deepcopy(plans[0]['witnesses'][0])
        witness['coset']['centralizer_root'] *= 2
        with self.assertRaises(AssertionError):
            conjugacy.replay_conjugacy(witness)


if __name__ == '__main__':
    unittest.main()
