"""Tiny independent checks for length-first helper-alias ties."""
from itertools import product
import json
from pathlib import Path

import exchange_v3_aliases as aliases
import verify


HERE = Path(__file__).resolve().parent


def main():
    images = {2: (2,), 5: (5,), 9: (2, 5, -2)}
    engine = aliases.AliasGeodesic((2, 5), {9: images[9]})
    verify.require(engine.saturate(aliases.Meter(1000)), 'tiny alias saturation incomplete')
    represented = {}
    for length in range(3):
        for tokens in product((2, -2, 5, -5, 9, -9), repeat=length):
            expanded = verify.image(tokens, images)
            represented.setdefault(expanded, []).append(tokens)
    cost = lambda tokens: (len(tokens), sum(abs(x) in (2, 5) for x in tokens))
    queries = 0
    for length in range(3):
        for target in product((2, -2, 5, -5), repeat=length):
            if verify.free(target) != target:
                continue
            tokens, complete = engine.shortest(target, aliases.Meter(1000))
            verify.require(complete and verify.image(tokens, images) == target, 'alias query incomplete or invalid')
            verify.require(cost(tokens) == min(map(cost, represented[target])), 'alias query differs from exhaustive shortest-length alternatives')
            queries += 1
    tokens, complete = engine.shortest((2, 5), aliases.Meter(1000))
    verify.require(cost(tokens) == (2, 1), 'equal-length helper preference absent')
    initial = verify.normalized(((2, 5, 5, -2, -5), (2, 2, 5, -2, -5)))
    checked = []
    for budget in (40, 1000):
        endpoint, event, charged = aliases.compress(initial, ((2, 5, -2, -5),), budget)
        verify.require(event is not None and verify.verify_event(json.loads(json.dumps(event)), known_trivial=True) == verify.words(endpoint), 'alias full template event differs')
        verify.require(charged <= budget, 'alias compile budget exceeded')
        checked.append({'budget': budget, 'charged': charged, 'complete': event['complete_all_exact_word_geodesics'], 'event': event})
    verify.require(engine.saturate(aliases.Meter(0)) is False and engine.shortest((2, 5), aliases.Meter(1000))[1] is False, 'alias reused saturation keeps stale completion')
    result = {'status': 'PASS', 'exact_queries_against_exhaustive_tokens': queries, 'neutral_alias_template': tokens,
              'neutral_alias_cost': cost(tokens), 'planted_events': checked, 'resaturation_completion_reset': True,
              'known_triviality_proof': 'The commutator plant is the independently established (abbAB,aabAB) trivial pair.',
              'source_sha256': verify.sha(HERE / 'exchange_v3_aliases.py'), 'engine_sha256': verify.sha(HERE / 'exchange_v2_geodesic.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0}
    (HERE / 'verification_v3_aliases.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'exact_queries': queries, 'neutral_alias_cost': cost(tokens), 'compiled_budgets': [r['budget'] for r in checked]}, indent=2))


if __name__ == '__main__':
    main()
