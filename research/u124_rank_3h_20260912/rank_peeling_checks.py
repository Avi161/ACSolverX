"""Known-trivial chain controls, including sparse and high-rank labels."""
import json
from pathlib import Path

import rank_peeling as peeling
import verify


rows = []
for rank in (1, 2, 6, 11):
    labels = tuple(10 ** 9 + 101 * i for i in range(rank))
    words = peeling.search.normalize(tuple((a, b) for a, b in zip(labels, labels[1:]))
                                     + ((labels[-1],),))
    after, events, charged, complete = peeling.descend(words, 1000)
    assert after == () and complete and charged == rank
    current = words
    for event in json.loads(json.dumps(events)):
        assert tuple(map(tuple, event['before'])) == current
        verify.verify_event(event, known_trivial=True)
        current = tuple(map(tuple, event['after']))
    rows.append({'rank': rank, 'initial_length': peeling.search.length(words),
                 'final_length': 0, 'charged': charged, 'events': events})
for budget in (0, 1, 3, 5):
    after, events, charged, complete = peeling.descend(words, budget)
    assert charged <= budget
    assert not complete
result = {'source_sha256': peeling.search.sha(Path(peeling.__file__)),
          'known_triviality': 'Each chain ends in a singleton; successive substitution clears it.',
          'budget_checks': 4, 'rows': rows}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'ranks': [r['rank'] for r in rows], 'budget_checks': 4}))
