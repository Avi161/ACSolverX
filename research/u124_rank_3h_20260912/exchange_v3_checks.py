"""Neutral-alias objective and exact saved-word reproduction controls."""
import json
import unittest

import exchange_templates
import exchange_v3_aliases as aliases
import search


DEFINITION = (1, 2, -1, -2)
SAVED_95 = ((-2, -2, -1, -1, -1, 2, 1, 1),
            (-2, -2, 1, 2, 1, 2, -1, -2, 1, 2, -1))


class AliasChecks(unittest.TestCase):
    def test_equal_length_prefers_more_helper_tokens(self):
        target = (1, -2, -2, -1, -1, -1, 2, 1)
        result = aliases.solve(target, {3: DEFINITION}, 1000)
        self.assertTrue(result['complete_geodesic'])
        self.assertEqual(result['template_cost'], (8, 6))
        self.assertEqual(result['template'], (-2, -3, -2, -3, -1, -1, 2, 1))
        self.assertEqual(len(result['template']), len(target))
        self.assertEqual(exchange_templates._expand(result['template'], {1: (1,), 2: (2,), 3: DEFINITION}), target)

    def test_selected_orientation_shortens_further_than_saved_neutral_alias(self):
        after, event, charged = aliases.compress(SAVED_95, (DEFINITION,), 1000)
        self.assertEqual(search.length(after), 17)
        self.assertTrue(event['complete_all_exact_word_geodesics'])
        self.assertEqual(tuple(map(len, event['templates'])), (7, 5))
        self.assertEqual(event['helper_uses'], {3: 5})
        self.assertEqual(charged, 505)
        self.assertEqual(exchange_templates.replay(json.loads(json.dumps(event))), after)

    def test_450_unit_partial_run_has_same_verified_template_without_optimality_claim(self):
        after, event, charged = aliases.compress(SAVED_95, (DEFINITION,), 450)
        self.assertEqual((search.length(after), charged), (17, 450))
        self.assertFalse(event['complete_all_exact_word_geodesics'])
        self.assertEqual(exchange_templates.replay(event), after)
        self.assertEqual(sum(event['work_counts'].values()), charged)

    def test_probe_preserves_budget(self):
        for budget in (0, 1, 2, 5, 30, 450):
            candidates, charged = aliases.probe(SAVED_95, budget)
            self.assertLessEqual(charged, budget)
            for _, events in candidates:
                exchange_templates.replay(events[0])

    def test_rank11_and_large_labels(self):
        ids = tuple(10**20 + i * 17 for i in range(11))
        words = search.normalize(tuple((g,) for g in ids))
        after, event, charged = aliases.compress(words, ((ids[0], ids[-1], -ids[0], -ids[-1]),), 40)
        self.assertEqual(len(after), 12)
        self.assertLessEqual(charged, 40)
        self.assertEqual(exchange_templates.replay(event), after)

    def test_truncated_resaturation_resets_alias_engine_flag(self):
        engine = aliases.AliasGeodesic((1, 2), {3: DEFINITION})
        self.assertTrue(engine.saturate(aliases.Meter(1000)))
        self.assertFalse(engine.saturate(aliases.Meter(0)))
        self.assertFalse(engine.shortest((1, 2), aliases.Meter(1000))[1])


if __name__ == '__main__':
    unittest.main()
