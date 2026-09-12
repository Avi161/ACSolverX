"""Bounded exact-word controls for weighted free-reduction saturation."""
import itertools
import json
import unittest

import exchange_templates
import exchange_v2_geodesic as geodesic
import exchange_v2_probe
import search


class GeodesicChecks(unittest.TestCase):
    def test_exact_geodesics_against_small_complete_token_enumeration(self):
        images = {1: (1,), 2: (2,), 3: (1, 2, -1, -2)}
        known, evaluations = {}, 0
        for size in range(4):
            for tokens in itertools.product((1, -1, 2, -2, 3, -3), repeat=size):
                if search.reduced(tokens) != tokens:
                    continue
                evaluations += 1
                word = search.reduced(x for token in tokens for x in
                                      (images[token] if token > 0 else search.inverse(images[-token])))
                known.setdefault(word, tokens)
        self.assertEqual(evaluations, 187)
        for target in ((1, 2, 2, -1, -2), (1, 1, 2, -1, -2), (1, 2, -1, -2, 1)):
            result = geodesic.solve(target, {3: images[3]}, 1000)
            self.assertTrue(result['complete_geodesic'])
            self.assertEqual(len(result['template']), len(known[target]))
            self.assertLess(result['charged_units'], 1000)

    def test_elimination_objective_selects_a_longer_unique_occurrence(self):
        target, defining = (1, 1, 2), (1, 1, 1, 2, 2, 2)
        shortest = geodesic.solve(target, {3: defining}, 1000)
        isolated = geodesic.solve(target, {3: defining}, 1000, eliminate_generator=1)
        self.assertTrue(shortest['complete_geodesic'] and isolated['complete_geodesic'])
        self.assertEqual(shortest['template'], target)
        self.assertEqual(isolated['template'], (-1, 3, -2, -2))
        self.assertEqual(isolated['template_cost'], (1, 4))
        self.assertEqual(sum(abs(x) == 1 for x in shortest['template']), 2)
        self.assertEqual(sum(x == 1 for x in defining) - sum(x == -1 for x in defining), 3)
        self.assertEqual(sum(x == 1 for x in target) % 3, 2)

    def test_partial_saturation_and_partial_queries_never_claim_complete(self):
        for budget in (0, 1, 8, 30, 100, 150):
            result = geodesic.solve((1, 2, 2, -1, -2), {3: (1, 2, -1, -2)}, budget)
            self.assertLessEqual(result['charged_units'], budget)
            self.assertFalse(result['complete_geodesic'])
            images = {1: (1,), 2: (2,), 3: (1, 2, -1, -2)}
            self.assertEqual(exchange_templates._expand(result['template'], images), result['target'])

    def test_multiword_dictionary_and_large_integer_gaps(self):
        result = geodesic.solve((101, 307, 101, 307, -101, -307),
                                {10**20: (101, 307, -101), 10**20 + 1: (307, 101, -307)}, 1000)
        self.assertTrue(result['complete_geodesic'])
        self.assertEqual(result['automaton_states'], 9)
        self.assertLess(result['charged_units'], 1000)

    def test_complete_wrapper_replays_existing_event_schema(self):
        words = search.normalize(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))
        after, event, cost = exchange_v2_probe.compress(words, ((1, 2, -1, -2),), 1000,
                                                        eliminate_generator=1)
        self.assertEqual(search.length(after), 10)
        self.assertTrue(event['complete_all_exact_word_geodesics'])
        self.assertEqual(event['charged_units'], cost)
        self.assertEqual(sum(event['work_counts'].values()), cost)
        self.assertEqual(exchange_templates.replay(json.loads(json.dumps(event))), after)

    def test_probe_budget_and_rank_zero(self):
        words = search.normalize(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))
        options, cost = exchange_v2_probe.probe(words, 1000)
        self.assertLessEqual(cost, 1000)
        self.assertTrue(options)
        self.assertLess(search.length(options[0][0]), search.length(words))
        self.assertEqual(exchange_v2_probe.probe((), 1000), ([], 0))

    def test_reject_helper_letters_in_query_and_boolean_axis(self):
        with self.assertRaises(ValueError):
            geodesic.DictionaryGeodesic((1, 2), {3: (1, 2)}, eliminate_generator=True)
        engine = geodesic.DictionaryGeodesic((1, 2), {3: (1, 2)})
        with self.assertRaises(ValueError):
            engine.shortest((3,), geodesic.Meter(100))

    def test_repeated_truncated_saturation_clears_completion(self):
        engine = geodesic.DictionaryGeodesic((1, 2), {3: (1, 1, 1, 2, 2, 2)}, eliminate_generator=1)
        self.assertTrue(engine.saturate(geodesic.Meter(1000)))
        self.assertEqual(engine.shortest((1, 1, 2), geodesic.Meter(1000)), ((-1, 3, -2, -2), True))
        self.assertFalse(engine.saturate(geodesic.Meter(0)))
        self.assertFalse(engine.saturation_complete)
        self.assertFalse(engine.shortest((1, 1, 2), geodesic.Meter(1000))[1])


if __name__ == '__main__':
    unittest.main()
