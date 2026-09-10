"""Pins on ``benchmark/ladder/``: the shape of the graded pool and of the nested subsets.

These read the shipped CSV/JSON files; they do not rebuild the ladder (that needs the
pinned research-branch blobs) and they run no search.
"""
import csv
import hashlib
import json
import math
import os
from collections import Counter

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LADDER = os.path.join(ROOT, 'benchmark', 'ladder')
SIZES = (20, 40, 60, 100, 200, 300, 500)
LEVELS = range(1, 11)
EDGES = [1_000, 10_000, 31_623, 100_000, 316_228, 1_000_000]
TOP = 10_000_000
ALPHABET = set('xXyY')


def _rows(name):
    with open(os.path.join(LADDER, name), newline='') as fh:
        return list(csv.DictReader(fh))


def _json(name):
    with open(os.path.join(LADDER, name)) as fh:
        return json.load(fh)


@pytest.fixture(scope='module')
def pool():
    return _rows('ladder_all.csv')


@pytest.fixture(scope='module')
def manifest():
    return _json('ladder_manifest.json')


@pytest.fixture(scope='module')
def subsets():
    return {n: (_rows(f'ladder_{n}.csv'), _json(f'ladder_{n}.json')) for n in SIZES}


def test_pool_words_and_names(pool):
    names = [r['name'] for r in pool]
    assert len(names) == len(set(names))
    for r in pool:
        assert r['r1'] and r['r2'] and set(r['r1'] + r['r2']) <= ALPHABET, r['name']
        assert int(r['level']) in LEVELS, r['name']
        assert int(r['start_len']) == len(r['r1']) + len(r['r2']), r['name']


def test_levels_follow_the_greedy_bands(pool, manifest):
    E = manifest['E']
    assert 1_000_000 < E < TOP
    for r in pool:
        lvl = int(r['level'])
        if r['form'] in ('aca_initial', 'aca_best', 'ms_rep261') or r['source'] == 'ms_unsolved':
            assert lvl == 10 and r['solved_by'] == 'none', r['name']
            continue
        if r['greedy_solved'] == '0':
            assert lvl == 9 and r['greedy_run'] == 'unsolved@10M' and int(r['greedy_nodes']) == TOP, r['name']
            assert r['solved_by'] != 'none', r['name']   # every level-9 row is solved by something
            continue
        g = int(r['greedy_nodes'])
        edges = [0] + EDGES + [E, TOP + 1]
        assert edges[lvl - 1] <= g < edges[lvl], (r['name'], g, lvl)


def test_levels_seven_and_eight_split_at_E(pool, manifest):
    mid = sorted(int(r['greedy_nodes']) for r in pool
                 if r['form'] == 'autmin' and r['greedy_solved'] == '1'
                 and 1_000_000 <= int(r['greedy_nodes']) <= TOP)
    assert len(mid) == 60
    seven = [g for g in mid if g < manifest['E']]
    assert len(seven) == 30


def test_level_nine_is_the_28_greedy_residue(pool):
    nine = sorted(r['name'] for r in pool if r['level'] == '9')
    assert len(nine) == 28
    assert {'ac19_7284', 'ac19_16286', 'ac19_50841', 'ac19_51034'} <= set(nine)


def test_level_ten_forms(pool):
    ten = [r for r in pool if r['level'] == '10']
    forms = Counter(r['form'] for r in ten)
    assert forms == {'aca_initial': 124, 'aca_best': 124, 'ms_rep261': 261, 'ms_raw': 550}
    initial = [r['name'] for r in ten if r['form'] == 'aca_initial']
    assert sorted(initial, key=lambda n: int(n[4:])) == [f'aca_{i}' for i in range(124)]


def test_pairs_link_originals_to_their_representatives(pool):
    by_name = {r['name']: r for r in pool}
    originals = [r for r in pool if r['form'] == 'original']
    assert len(originals) >= 40
    for o in originals:
        rep = by_name[o['orbit']]
        assert rep['form'] == 'autmin' and rep['pair_id'] == rep['name'] == o['pair_id'], o['name']
        assert int(rep['level']) >= 7, o['name']       # the pairs are hard orbits (>= 1M greedy)
        assert int(o['level']) <= 4, o['name']         # their originals are easy for greedy
    assert sum(1 for o in originals if by_name[o['orbit']]['level'] == '9') >= 40
    pairs = _rows('ladder_pairs.csv')
    assert {p['orig_name'] for p in pairs} == {o['name'] for o in originals}
    for p in pairs:
        assert int(p['rep_level']) >= 7 and by_name[p['orig_name']]['orbit'] == p['pair_id']


def test_subsets_are_nested_and_sized(subsets):
    prev = None
    for n in SIZES:
        rows, meta = subsets[n]
        names = [r['name'] for r in rows]
        assert len(names) == len(set(names)) == meta['size']
        assert meta['requested_size'] == n and meta['per_level'] == n // 10 and meta['nested'] is True
        per_level = Counter(int(r['level']) for r in rows)
        for lvl in LEVELS:
            assert per_level[lvl] == meta['per_level_actual'][str(lvl)] <= n // 10, (n, lvl)
        if n <= 200:
            assert meta['size'] == n and all(per_level[lvl] == n // 10 for lvl in LEVELS)
        if prev is not None:
            assert set(prev) <= set(names), n
        prev = names


def test_subsets_carry_the_pool_rows_verbatim(pool, subsets):
    by_name = {r['name']: r for r in pool}
    for n in SIZES:
        for r in subsets[n][0]:
            assert r == by_name[r['name']], (n, r['name'])


def test_subsets_take_only_the_four_strata_and_no_trivial_root(subsets):
    allowed = {('ac19', 'original'), ('ac19', 'autmin'), ('ms640', 'ms_raw'), ('ms_unsolved', 'aca_initial')}
    for n in SIZES:
        for r in subsets[n][0]:
            assert (r['source'], r['form']) in allowed, (n, r['name'])
            if r['greedy_solved'] == '1':
                assert int(r['greedy_nodes']) > 1, (n, r['name'])


def test_subset_prefixes_are_spread_over_each_level(subsets):
    """Within a level, the k picks must not all sit at one end: the log-range they
    cover has to be at least half of the level's band once k >= 6 (levels 1-8)."""
    rows60 = subsets[60][0]
    for lvl in range(1, 9):
        gs = [math.log10(int(r['greedy_nodes'])) for r in rows60 if int(r['level']) == lvl
              and r['form'] == 'autmin']
        if len(gs) < 3:
            continue
        edges = [1] + EDGES + [subsets[60][1]['E'], TOP]
        band = math.log10(edges[lvl]) - math.log10(max(edges[lvl - 1], 2))
        assert max(gs) - min(gs) >= 0.4 * band, (lvl, gs)


def test_manifest_pins_every_source(manifest):
    for key, src in manifest['sources'].items():
        assert len(src['sha256']) == 64 and src['bytes'] > 0, key
        if src['commit'] is None:
            path = os.path.join(ROOT, src['path'])
            assert os.path.exists(path), key
            with open(path, 'rb') as fh:
                assert hashlib.sha256(fh.read()).hexdigest() == src['sha256'], key
    assert manifest['levels'][8]['rule'].startswith('plain greedy unsolved')
    assert manifest['E'] == manifest['levels'][7]['lo_nodes']


def test_subset_json_is_self_describing(subsets, manifest):
    for n in SIZES:
        meta = subsets[n][1]
        assert meta['E'] == manifest['E'] and meta['levels'] == manifest['levels']
        assert meta['subset'] == [r['name'] for r in subsets[n][0]]
        assert meta['sources'] == manifest['sources']


# --- the S20-hard variant (ladder_60_s20hard, ladder_100_s20hard) --------------
S20HARD_SIZES = (20, 40, 60, 100, 200, 300)
STRATA = {('ac19', 'original'), ('ac19', 'autmin'), ('ms640', 'ms_raw'), ('ms_unsolved', 'aca_initial')}


def _s20_cost(r):
    return int(r['s20_nodes']) if r['s20_solved'] == '1' else TOP + 1


@pytest.fixture(scope='module')
def s20hard():
    return {n: (_rows(f'ladder_{n}_s20hard.csv'), _json(f'ladder_{n}_s20hard.json')) for n in S20HARD_SIZES}


def test_every_eligible_row_below_level_ten_has_an_s20_grade(pool):
    for r in pool:
        if int(r['level']) < 10 and (r['source'], r['form']) in STRATA:
            assert r['s20_run'], r['name']
            if r['s20_solved'] == '1':
                assert int(r['s20_nodes']) >= 1, r['name']
            else:
                assert r['s20_run'] == 'unsolved@10M' and int(r['level']) == 9, r['name']
    ms_and_originals = [r for r in pool if r['form'] in ('ms_raw', 'original') and r['source'] != 'ms_unsolved']
    assert len(ms_and_originals) == 685
    assert all(r['s20_run'] == 'ladder100k' and r['s20_solved'] == '1' for r in ms_and_originals)


def test_s20hard_keeps_the_rows_hardest_for_s20_in_each_level(pool, s20hard, subsets):
    by_level = {}
    for r in pool:
        if (r['source'], r['form']) in STRATA and not (r['greedy_solved'] == '1' and int(r['greedy_nodes']) <= 1):
            by_level.setdefault(int(r['level']), []).append(r)
    prev = None
    for n in S20HARD_SIZES:
        rows, meta = s20hard[n]
        k = n // 10
        assert meta['variant'] == 's20hard' and meta['per_level'] == k and meta['nested'] is True
        assert meta['size'] == len(rows) == sum(meta['per_level_actual'].values())
        assert meta['size'] == (n if n <= 200 else 298), n     # level 9 holds 28 rows
        assert meta['subset'] == [r['name'] for r in rows]
        by_name = {r['name']: r for r in pool}
        for r in rows:
            assert r == by_name[r['name']], (n, r['name'])
        for lvl in range(1, 10):
            picks = [r for r in rows if int(r['level']) == lvl]
            assert len(picks) == min(k, len(by_level[lvl])) == meta['per_level_actual'][str(lvl)], (n, lvl)
            worst_pick = min(_s20_cost(r) for r in picks)
            rest = [r for r in by_level[lvl] if r['name'] not in {p['name'] for p in picks}]
            assert all(_s20_cost(r) <= worst_pick for r in rest), (n, lvl)   # nothing harder was left behind
        # level 10 has no S20 cost: the same rows as the spread ladder of that size
        ten = [r['name'] for r in rows if int(r['level']) == 10]
        assert ten == [r['name'] for r in subsets[n][0] if int(r['level']) == 10]
        if prev is not None:
            assert set(prev) <= {r['name'] for r in rows}
        prev = [r['name'] for r in rows]


def test_s20hard_level_nine_is_the_s20_residue_first(s20hard, pool):
    residue = sorted(r['name'] for r in pool if r['level'] == '9' and r['s20_solved'] == '0')
    assert len(residue) == 9
    for n in S20HARD_SIZES:
        picks = {r['name'] for r in s20hard[n][0] if r['level'] == '9'}
        if n // 10 <= len(residue):
            assert picks <= set(residue), n          # small subsets: only S20-unsolved rows
        else:
            assert set(residue) <= picks, n          # larger ones: the whole residue, then the solved
    # every S20-unsolved row on record is greedy-unsolved too, hence at level 9 (the user's rule)
    assert all(r['level'] == '9' and r['greedy_solved'] == '0'
               for r in pool if r['s20_solved'] == '0' and int(r['level']) < 10)
