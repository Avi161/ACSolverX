"""Tiny algebraic controls for the cancellation-aware dictionary exchange."""
from copy import deepcopy
import json
import unittest

import exchange_templates as exchange
import lemma11
import search
import whitehead


PLANTED = search.normalize(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))
COMMUTATOR = (1, 2, -1, -2)


class ExchangeChecks(unittest.TestCase):
    def test_nonliteral_template_crosses_whole_tuple_plateau(self):
        fixed, steps, charged, complete = whitehead.descend(PLANTED, 8)
        self.assertEqual((fixed, steps, charged, complete), (PLANTED, [], 4, True))
        literal, literal_event = search.compress(PLANTED, COMMUTATOR)
        self.assertEqual(search.length(literal), 12)
        self.assertEqual(literal_event['uses'], 1)
        after, event, cost = exchange.compress_dictionary(PLANTED, (COMMUTATOR,), 100)
        self.assertEqual((search.length(after), cost), (10, 74))
        self.assertEqual(event['templates'][0], (3, 2, 3))
        self.assertTrue(event['graph_complete'])
        self.assertEqual(exchange.replay(json.loads(json.dumps(event))), after)
        self.assertTrue(all(not lemma11.single_occurrences(w) for w in PLANTED))

    def test_planted_exact_triviality_and_sequential_removals(self):
        first, second = (1, 2, 2, -1, -2), (1, 1, 2, -1, -2)
        self.assertEqual(search.reduced(COMMUTATOR + (2,) + COMMUTATOR), first)
        self.assertEqual(search.reduced((1,) + COMMUTATOR), second)
        after, event, _ = exchange.compress_dictionary(PLANTED, (COMMUTATOR,), 100)
        i = next(i for i, w in enumerate(after) if w == (-3, -1))
        after, removal1 = lemma11.remove_one(after, i, 1)
        self.assertEqual(after, search.normalize(((-3, -3, 2, 3, -2), (-3, -3, -2))))
        i = next(i for i, w in enumerate(after) if w == (-3, -3, -2))
        after, removal2 = lemma11.remove_one(after, i, 2)
        self.assertEqual(after, ((-3,),))
        after, removal3 = lemma11.remove_one(after, 0, 3)
        self.assertEqual(after, ())
        for removal in (removal1, removal2, removal3):
            lemma11.replay_removal(removal)

    def test_multiple_definitions_and_all_old_helper_rows_are_kept(self):
        words = search.normalize(((1, 2, 1, 2, 1), (1, 2, 1, 2, 1, 2, 1), (9001,)))
        after, event, charged = exchange.compress_dictionary(words, ((1, 2), (2, 1)), 150)
        self.assertEqual(event['helpers'], (9002, 9003))
        self.assertEqual(len(after), 5)
        self.assertEqual([r['input_index'] for r in event['rows']], [0, 1, 2])
        self.assertEqual(sum(event['work_counts'].values()), charged)
        self.assertEqual(exchange.replay(event), after)

    def test_every_small_budget_and_partial_graph_replay(self):
        for budget in range(16):
            after, event, cost = exchange.compress_dictionary(PLANTED, (COMMUTATOR,), budget)
            self.assertLessEqual(cost, budget)
            if event is None:
                self.assertLess(budget, 3)
            else:
                self.assertEqual(exchange.replay(event), after)
                self.assertEqual(cost, budget)
                self.assertFalse(event['graph_complete'])

    def test_arbitrary_rank_and_integer_gaps(self):
        ids = tuple(10**20 + 17*i for i in range(11))
        words = search.normalize(tuple((g,) for g in ids))
        after, event, cost = exchange.compress_dictionary(words, ((ids[0], ids[-1]),), 40)
        self.assertEqual(len(after), 12)
        self.assertEqual(event['helpers'], (ids[-1]+1,))
        self.assertEqual(exchange.replay(event), after)
        self.assertLessEqual(cost, 40)

    def test_corrupt_expansion_or_missing_row_is_rejected(self):
        _, event, _ = exchange.compress_dictionary(PLANTED, (COMMUTATOR,), 100)
        changed = deepcopy(event)
        changed['rows'][0]['template'] = (3,)
        with self.assertRaises(AssertionError):
            exchange.replay(changed)
        changed = deepcopy(event)
        changed['rows'].pop()
        with self.assertRaises(AssertionError):
            exchange.replay(changed)

    def test_invalid_arguments(self):
        for budget in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                exchange.compress_dictionary(PLANTED, (COMMUTATOR,), budget)
        with self.assertRaises(ValueError):
            exchange.compress_dictionary(PLANTED, ((77, 77),), 100)
        with self.assertRaises(ValueError):
            exchange.compress_dictionary(PLANTED, ((1, -1),), 100)


if __name__ == '__main__':
    unittest.main()
