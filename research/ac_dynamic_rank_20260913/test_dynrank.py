import itertools
import json
import random
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dynrank as D          # noqa: E402
import verify as V           # noqa: E402


def random_state(rng, rank, max_len=6):
    words = []
    for _ in range(rank):
        while True:
            w = tuple(rng.choice([1, -1]) * rng.randint(1, rank) for _ in range(rng.randint(1, max_len)))
            if D.canonical(w):
                break
        words.append(w)
    return D.normalize(words)


def test_canonical_word_invariants():
    w = (1, 2, -1, -2)
    assert D.canonical(w) == D.canonical((2, -1, -2, 1)) == D.canonical(D.inverse(w))
    assert D.canonical((1, -1)) == ()
    assert D.canonical((2, 1, 1, -2)) == (-1, -1)   # inverse is lexicographically smaller


def brute_perm_min(words):
    n = len(words)
    best = None
    for p in itertools.permutations(range(1, n + 1)):
        perm = {g: p[g - 1] for g in range(1, n + 1)}
        cand = D.apply_relabel(words, perm, {g: 1 for g in perm})
        if best is None or cand < best:
            best = cand
    return best


def test_relabel_canonical_is_invariant_under_permutation_and_equals_brute_force():
    rng = random.Random(7)
    for _ in range(300):
        rank = rng.randint(2, 6)
        s = random_state(rng, rank)
        perm = list(range(1, rank + 1))
        rng.shuffle(perm)
        perm = {g: perm[g - 1] for g in range(1, rank + 1)}
        t = D.apply_relabel(s, perm, {g: 1 for g in perm})
        cs, p, sg = D.relabel_canonical(s)
        ct, _, _ = D.relabel_canonical(t)
        assert cs == ct                              # invariant under renaming
        assert brute_perm_min(cs) == brute_perm_min(s)   # and a genuine renaming of s
        # the recorded renaming reproduces the canonical form
        assert D.apply_relabel(s, p, sg) == cs


def test_define_then_eliminate_roundtrip():
    rng = random.Random(3)
    for _ in range(200):
        s = random_state(rng, rng.randint(2, 5), 7)
        for child, ev in D.defines(s):
            h = ev['h']
            # the defining relator h^-1 d sits somewhere in child; eliminating h from it restores s
            found = False
            for i, r in enumerate(child):
                if sum(abs(x) == h for x in r) == 1 and len(r) == 3:
                    back, _ = D.eliminate(child, i, h)
                    if D.normalize(back) == s:
                        found = True
                        break
            assert found


def test_product_matches_conjugate_multiplication():
    rng = random.Random(11)
    for _ in range(200):
        s = random_state(rng, rng.randint(2, 4), 6)
        for child, ev in D.products(s, cap=20):
            i, j, sign, k1, k2 = ev['i'], ev['j'], ev['sign'], ev['k1'], ev['k2']
            target = s[i]
            base = s[j] if sign == 1 else D.inverse(s[j])
            c = D.reduce(base[:k2] + D.inverse(target[:k1]))
            direct = D.canonical(target + D.inverse(c) + base + c)
            assert direct == ev['result']


def test_eliminate_solves_relator():
    s = D.normalize([(1, 2, -1, -2, 3), (3, 1, 1), (2, 3, -1)])
    child, ev = D.eliminate(s, 0, 3)          # relator 0 has one 3
    # substituting the image for 3 into relator 0 must kill it
    r = s[0]
    sub = []
    for x in r:
        sub.extend(ev['image'] if x == 3 else D.inverse(ev['image']) if x == -3 else (x,))
    assert D.canonical(tuple(sub)) == ()
    assert len(child) == 2 and all(abs(x) <= 2 for w in child for x in w)


def test_solved_rows_replay_and_tampering_is_caught():
    root = (D.parse('YYYYXyyyx'), D.parse('YYXYxYx'))     # ladder row 331, bin 2
    res = D.best_first(root, cap=8, ceiling=D.total_length(root) + 8, pops=2000, relabel=True)
    assert res['solved']
    path = json.loads(json.dumps(D.json_path(res['path'])))
    info = V.replay([list(w) for w in root], path, 2, D.json_relabel(res['root_relabel']))
    assert info['steps'] == res['path_length']
    assert info['defines'] >= 1 or info['eliminates'] >= 2
    # tamper: change one stored state
    bad = json.loads(json.dumps(path))
    bad[len(bad) // 2]['after'] = [[1, 2]]
    with pytest.raises(V.Failure):
        V.replay([list(w) for w in root], bad, 2, D.json_relabel(res['root_relabel']))
    # tamper: drop the last step so the path does not end empty
    with pytest.raises(V.Failure):
        V.replay([list(w) for w in root], path[:-1], 2, D.json_relabel(res['root_relabel']))


def test_control_arm_never_changes_rank():
    root = (D.parse('YYYXyyx'), D.parse('YYXYxYx'))
    res = D.best_first(root, cap=24, ceiling=10 ** 9, pops=300, allow_define=False,
                       allow_eliminate=True)
    assert res['max_rank'] == 2


def test_closure_small_case_is_closed_or_solved():
    root = (D.parse('YYXyx'), D.parse('Yx'))
    res = D.closure(root, cap=6, ceiling=D.total_length(root) + 2, max_states=10000)
    assert res['solved']
    V.replay([list(w) for w in root], json.loads(json.dumps(D.json_path(res['path']))), 2,
             D.json_relabel(res['root_relabel']))
    res = D.closure((D.parse('YXYxyx'), D.parse('YYYYxxx')), cap=6, ceiling=13, max_states=100000)
    assert res['closed'] and not res['solved']


def test_triangulate_and_tri_certificate_replays_from_rank_two_root():
    root = (D.parse('YYYXyyx'), D.parse('YYXYxYx'))          # ladder row 201, bin 2
    tri, steps = D.triangulate(root)
    assert all(len(w) <= 3 for w in tri) and len(tri) == 2 + len(steps)
    # substituting every definition back returns the root
    state = tri
    for step in reversed(steps):
        h = step['event']['h']
        i = next(k for k, r in enumerate(state) if len(r) == 3 and sum(abs(x) == h for x in r) == 1)
        back, _ = D.eliminate(state, i, h)
        state = D.normalize(back)
    assert state == D.normalize(root)
    res = D.best_first(tri, cap=8, ceiling=D.total_length(root) + 8, pops=2000,
                       allow_define=False, allow_eliminate=True, relabel=True)
    assert res['solved']
    path = (D.json_path(steps)
            + [{'event': {'kind': 'rename'}, 'relabel': D.json_relabel(res['root_relabel']),
                'after': [list(w) for w in res['root_key']]}]
            + D.json_path(res['path']))
    info = V.replay([list(w) for w in root], json.loads(json.dumps(path)), 2, None)
    assert info['defines'] == len(steps) and info['max_rank'] == len(tri)
