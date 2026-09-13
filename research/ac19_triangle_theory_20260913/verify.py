"""Independent replay of every benchmark path and every theory claim.

Deliberately shares no search code with ``coupling_search.py``: words are
replayed with local free/cyclic reduction, each event is checked to be a single
normal-product substitution at fixed rank on the declared basis, and the
headline counts in a benchmark JSON are recomputed from its rows.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def free_reduce(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def inverse(word):
    return tuple(-x for x in reversed(word))


def cyclic_canonical(word):
    word = free_reduce(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = word[1:-1]
    if not word:
        return ()
    candidates = []
    for w in (word, inverse(word)):
        for k in range(len(w)):
            candidates.append(w[k:] + w[:k])
    return min(candidates)


def normalize(words):
    return tuple(sorted(cyclic_canonical(tuple(w)) for w in words))


def replay_event(state, event):
    """Replay one normal_product_substitution event with independent code."""
    assert event['kind'] == 'normal_product_substitution', event['kind']
    before = normalize(event['before'])
    assert before == state, 'path discontinuity'
    i = event['target']
    (factor,) = event['factors']
    j, sign, conj = factor['donor_index'], factor['sign'], tuple(factor['conjugator'])
    assert i != j
    donor = tuple(state[j]) if sign == 1 else inverse(tuple(state[j]))
    replacement = free_reduce(tuple(state[i]) + inverse(conj) + donor + conj)
    assert replacement == tuple(event['raw_target_after']), 'replacement differs'
    after = normalize(state[:i] + (replacement,) + state[i + 1:])
    assert after == normalize(event['after']), 'endpoint differs'
    return after


def replay_path(initial, events, rank, declared, cap):
    state = normalize(initial)
    for event in events:
        state = replay_event(state, event)
        assert len(state) == rank, 'rank changed'
        assert {abs(x) for w in state for x in w} <= declared, 'left declared basis'
        assert max(map(len, state)) <= cap, 'relator cap exceeded'
    return state


def verify_benchmark(path):
    report = json.loads(Path(path).read_text())
    checks = 0
    for row in report['rows']:
        tri = normalize(row['triangle_state'])
        rank = row['rank']
        declared = {abs(x) for w in tri for x in w}
        assert len(tri) == rank and declared == set(range(1, rank + 1)), row['name']
        assert all(len(w) <= 3 for w in tri) == row['all_relators_at_most_three']
        for arm in row['arms']:
            end = replay_path(tri, arm['events'], rank, declared, arm['relator_cap'])
            if arm['endpoint'] is not None:
                assert end == normalize(arm['endpoint']), (row['name'], arm['ordering'])
                assert (min(map(len, end)) == 1) == arm['unit_found'] or arm['unit_found'] is False
                if arm['unit_found']:
                    assert min(map(len, end)) == 1
                elif arm['bigon_found']:
                    assert min(map(len, end)) == 2
            else:
                assert not arm['events'] and not arm['bigon_found'] and not arm['unit_found']
            checks += 1
    s = report['summary']
    rows = report['rows']
    assert s['rows'] == len(rows)
    assert s['roots_digram_disjoint'] == sum(r['root_digram_disjoint'] for r in rows)
    assert s['rows_with_bigon'] == sum(any(a['bigon_found'] for a in r['arms']) for r in rows)
    assert s['rows_with_unit'] == sum(any(a['unit_found'] for a in r['arms']) for r in rows)
    assert s['rotation_products'] == sum(a['rotation_products'] for r in rows for a in r['arms'])
    assert s['heap_pops'] == sum(a['heap_pops'] for r in rows for a in r['arms'])
    return checks


def verify_theory():
    """Re-derive the two lemmas' machine checks with independent code."""
    import random
    random.seed(20260913)
    n = necessity = 0
    degenerate_only = True
    for _ in range(20000):
        r = random.randint(2, 4)
        words = []
        for _ in range(r):
            w = cyclic_canonical(tuple(random.choice([g, -g]) for g in random.choices(range(1, r + 1), k=3)))
            if len(w) != 3:
                break
            words.append(w)
        else:
            state = normalize(tuple(words))
            if len(state) != r or any(len(w) != 3 for w in state):
                continue
            n += 1
            # brute-force one-step products
            bigon = False
            for i, t in enumerate(state):
                for j, d in enumerate(state):
                    if i == j:
                        continue
                    for sign in (1, -1):
                        base = d if sign == 1 else inverse(d)
                        for k1 in range(3):
                            for k2 in range(3):
                                p = cyclic_canonical(t[k1:] + t[:k1] + base[k2:] + base[:k2])
                                assert (len(p) - 6) % 2 == 0, 'parity lemma violated'
                                if len(p) == 2:
                                    bigon = True
            # shared digram modulo inv2
            def digs(w):
                return {min((w[k], w[(k + 1) % 3]), (-w[(k + 1) % 3], -w[k])) for k in range(3)}
            shared = any(digs(state[i]) & digs(state[j])
                         for i in range(r) for j in range(i + 1, r))
            if bigon and not shared:
                necessity += 1
            if shared and not bigon and len(set(state)) == len(state):
                degenerate_only = False
    return {'states': n, 'necessity_violations': necessity,
            'sufficiency_failures_only_with_equal_relators': degenerate_only}


if __name__ == '__main__':
    theory = verify_theory()
    print('theory:', theory)
    assert theory['necessity_violations'] == 0
    assert theory['sufficiency_failures_only_with_equal_relators']
    for arg in sys.argv[1:]:
        print(arg, 'arm checks:', verify_benchmark(arg))
    print('PASS')
