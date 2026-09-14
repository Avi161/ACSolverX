"""Small exact powers, hidden definitions and budget controls."""
from copy import deepcopy
import json
import unittest

import exchange_root
import exchange_templates
import search


PLANTED = search.normalize(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))


class RootChecks(unittest.TestCase):
    def test_conjugated_powers_and_all_divisors(self):
        q = (101, 307, -101)
        target = search.reduced(q * 6)
        roots = exchange_root.roots(target)
        self.assertEqual([p for _, p in roots], [2, 3, 6])
        for root, power in roots:
            self.assertEqual(search.reduced(root * power), target)
        self.assertEqual(roots[-1][0], q)
        self.assertEqual(exchange_root.roots(()), [])
        self.assertEqual(exchange_root.roots((1, 2, -1, -2)), [])

    def test_hidden_commutator_is_reconstructed_exactly(self):
        plans, cost = exchange_root.discover(PLANTED, 333)
        self.assertEqual(cost, 333)
        plan = next(p for p in plans if p['defining_word'] == (1, 2, -1, -2))
        witness = plan['witnesses'][0]
        self.assertTrue(exchange_root.replay_root(json.loads(json.dumps(witness))))
        target = (1, 2, 2, -1, -2)
        root, power = exchange_root.roots(search.reduced(target + (2,)))[0]
        self.assertEqual((root, power), ((1, 2, -1), 2))
        self.assertEqual(search.reduced(root + (-2,)), plan['defining_word'])
        self.assertEqual(len({p['defining_word'] for p in plans}), len(plans))
        self.assertTrue(all(p['defining_word'] <= search.inverse(p['defining_word']) for p in plans))

    def test_forced_template_and_complete_tuple_are_replayed(self):
        plans, _ = exchange_root.discover(PLANTED, 333)
        plan = next(p for p in plans if p['defining_word'] == (1, 2, -1, -2))
        after, event, cost = exchange_root.compile_plan(PLANTED, plan, 150)
        self.assertEqual(search.length(after), 10)
        self.assertEqual(event['rows'][event['root_template_witness']['input_index']]['template'],
                         event['root_template_witness']['template'])
        self.assertEqual(exchange_templates.replay(json.loads(json.dumps(event))), after)
        self.assertEqual(sum(event['work_counts'].values()), cost)

    def test_budgets_include_failed_root_tests(self):
        for budget in (0, 1, 5, 17, 40):
            _, charged = exchange_root.discover(PLANTED, budget)
            self.assertEqual(charged, budget)
            _, charged = exchange_root.probe(PLANTED, budget)
            self.assertLessEqual(charged, budget)
        options, charged = exchange_root.probe(PLANTED, 1000)
        self.assertLessEqual(charged, 1000)
        self.assertTrue(options)
        self.assertLess(search.length(options[0][0]), 10)

    def test_larger_contexts_and_rank_are_not_rejected(self):
        words = search.normalize(PLANTED + tuple((10**20 + i,) for i in range(9)))
        _, cost = exchange_root.discover(words, 30, contexts=((), (1, 2), (-1, 2, 1)))
        self.assertEqual(cost, 30)
        self.assertEqual(len(words), 11)

    def test_corrupt_root_identity_is_rejected(self):
        plans, _ = exchange_root.discover(PLANTED, 333)
        witness = deepcopy(plans[0]['witnesses'][0])
        witness['root'] = (1,)
        with self.assertRaises(AssertionError):
            exchange_root.replay_root(witness)


if __name__ == '__main__':
    unittest.main()
