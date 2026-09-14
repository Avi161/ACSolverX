"""Exact algebra and finite-work controls for donor commutator surgery."""
import json
from pathlib import Path

import donor_commutators as surgery
import verify


words = surgery.search.normalize(((1, 2), (2,)))
count = 0
for conjugator in surgery.contexts(words):
    for target, donor in ((0, 1), (1, 0)):
        for sign in (1, -1):
            after, event = surgery.replacement(words, target, donor, sign, conjugator)
            verify.verify_event(event, known_trivial=True)
            for letter in (1, 2):
                exponent = lambda word: word.count(letter) - word.count(-letter)
                assert exponent(words[target]) == exponent(event['raw_target_after'])
            count += 1
budgets = []
for budget in (0, 1, 12, 100, 1000):
    candidates, charged = surgery.probe(words, budget)
    assert 0 <= charged <= budget
    for after, events in candidates:
        current = words
        for event in events:
            assert event['before'] == current
            verify.verify_event(event, known_trivial=True)
            current = event['after']
        assert after == current
    budgets.append({'budget': budget, 'charged': charged, 'candidates': len(candidates)})
result = {'replacement_checks': count, 'budgets': budgets,
          'known_trivial_plant': '(xy,y): use y to clear xy to x',
          'source_sha256': surgery.search.sha(Path(surgery.__file__))}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
