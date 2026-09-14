"""Exact known-trivial controls for replacing a dictionary after elimination."""
import json
from pathlib import Path

import dictionary_exchange as exchange
import verify


words = exchange.search.normalize(((-3, 1, 2), (1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))
rows = []
for budget in (0, 1, 10, 100, 1000):
    candidates, charged = exchange.probe(words, budget)
    assert charged <= budget
    for after, events in candidates:
        current = words
        for event in json.loads(json.dumps(events)):
            assert tuple(map(tuple, event['before'])) == current
            verify.verify_event(event, known_trivial=True)
            current = tuple(map(tuple, event['after']))
        assert after == current
    rows.append({'budget': budget, 'charged': charged, 'candidates': len(candidates),
                 'best_length': min([exchange.search.length(words)] + [exchange.search.length(a) for a, _ in candidates])})
result = {'source_sha256': exchange.search.sha(Path(exchange.__file__)), 'rows': rows,
          'known_triviality': 'Writing c=[x,y], the old rows are cyc and xc. Thus x=c^-1, y=c^-2, so c=[x,y]=1. The new row defines z=xy.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(rows))
