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
S20HARD_SIZES = (20, 40, 60, 100, 200, 300)
# the strata that feed the panels; ('ac19', 'original') is in the pool but not a stratum
STRATA = {('ac19', 'autmin'), ('ms640', 'ms_raw')}
# level populations cap the top: levels 6/7/8/9/10 hold 39/30/30/19/9 rows
EXPECTED_SIZE = {20: 20, 40: 40, 60: 60, 100: 99, 200: 188, 300: 268, 500: 377}
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
        assert r['source'] != 'ms_unsolved' and r['solved_by'] != 'none', r['name']   # only solvable rows
        if r['greedy_solved'] == '0':
            assert r['greedy_run'] == 'unsolved@10M' and int(r['greedy_nodes']) == TOP, r['name']
            assert lvl == (9 if r['s20_solved'] == '1' else 10), r['name']
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


LEVEL_TEN = {'ac19_65753', 'ac19_16286', 'ac19_59576', 'ac19_7284', 'ac19_27254',
             'ac19_28131', 'ac19_44381', 'ac19_50841', 'ac19_51034'}


def test_levels_nine_and_ten_are_the_28_greedy_residue(pool):
    nine = [r for r in pool if r['level'] == '9']
    ten = [r for r in pool if r['level'] == '10']
    assert len(nine) == 19 and all(r['s20_solved'] == '1' for r in nine)
    assert {r['name'] for r in ten} == LEVEL_TEN and all(r['s20_solved'] == '0' for r in ten)
    assert all(r['solved_by'].startswith('K3p_') for r in ten)   # only the cascades solve level 10


def test_unsolved_classes_are_off_the_ladder(pool):
    u124 = _rows('unsolved_124.csv')
    every = _rows('unsolved_all_forms.csv')
    assert [r['name'] for r in u124] == [f'aca_{i}' for i in range(124)]
    assert Counter(r['form'] for r in every) == {'aca_initial': 124, 'aca_best': 124, 'ms_rep261': 261, 'ms_raw': 550}
    assert [r for r in every if r['form'] == 'aca_initial'] == u124
    names = {r['name'] for r in pool}
    for r in every:
        assert r['level'] == 'unsolved' and r['solved_by'] == 'none' and r['source'] == 'ms_unsolved', r['name']
        assert r['name'] not in names, r['name']
        assert r['r1'] and r['r2'] and set(r['r1'] + r['r2']) <= ALPHABET, r['name']


def test_pairs_link_originals_to_their_representatives(pool):
    by_name = {r['name']: r for r in pool}
    originals = [r for r in pool if r['form'] == 'original']
    assert len(originals) >= 40
    for o in originals:
        rep = by_name[o['orbit']]
        assert rep['form'] == 'autmin' and rep['pair_id'] == rep['name'] == o['pair_id'], o['name']
        assert int(rep['level']) >= 7, o['name']       # the pairs are hard orbits (>= 1M greedy)
        assert int(o['level']) <= 4, o['name']         # their originals are easy for greedy
    assert sum(1 for o in originals if by_name[o['orbit']]['level'] in ('9', '10')) >= 40
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
        assert meta['size'] == sum(meta['per_level_actual'].values()) == EXPECTED_SIZE[n]
        assert per_level[10] == min(n // 10, 9) and per_level[9] == min(n // 10, 19)
        if prev is not None:
            assert set(prev) <= set(names), n
        prev = names


def test_subsets_carry_the_pool_rows_verbatim(pool, subsets):
    by_name = {r['name']: r for r in pool}
    for n in SIZES:
        for r in subsets[n][0]:
            assert r == by_name[r['name']], (n, r['name'])


def test_subsets_take_only_the_two_strata_and_no_trivial_root(subsets):
    for n in SIZES:
        for r in subsets[n][0]:
            assert (r['source'], r['form']) in STRATA, (n, r['name'])
            if r['greedy_solved'] == '1':
                assert int(r['greedy_nodes']) > 1, (n, r['name'])


def test_no_panel_carries_a_dataset_original(subsets, s20hard):
    """The 45 ``form == 'original'`` rows are in the pool and in originals_45.csv but
    never on a panel: they are the originals of the 33 orbits greedy cannot solve at
    10M, not a sample of AC19_extended.txt, and round-robin would give them 12-20% of
    a panel while scoring their orbits twice (LADDER.md)."""
    for n in SIZES:
        assert not [r for r in subsets[n][0] if r['form'] == 'original'], n
    for n in S20HARD_SIZES:
        assert not [r for r in s20hard[n][0] if r['form'] == 'original'], n


def test_originals_ship_as_their_own_panel(pool, manifest):
    originals = _rows('originals_45.csv')
    in_pool = [r for r in pool if r['form'] == 'original']
    by_name = {r['name']: r for r in pool}
    assert len(originals) == 45 == manifest['originals']['rows']
    assert {r['name'] for r in originals} == {r['name'] for r in in_pool}
    assert len({r['orbit'] for r in originals}) == 33 == manifest['originals']['orbits']
    for r in originals:
        assert r == by_name[r['name']], r['name']          # pool rows verbatim
        assert r['source'] == 'ac19' and int(r['level']) <= 4, r['name']
    assert {p['orig_name'] for p in _rows('ladder_pairs.csv')} == {r['name'] for r in originals}


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
                assert r['s20_run'] == 'unsolved@10M' and int(r['level']) == 10, r['name']
    ms_and_originals = [r for r in pool if r['form'] in ('ms_raw', 'original') and r['source'] != 'ms_unsolved']
    assert len(ms_and_originals) == 685
    assert all(r['s20_run'] == 'ladder100k' and r['s20_solved'] == '1' for r in ms_and_originals)
    for r in pool:   # the originals keep their S20 grade even though they are off the panels
        if r['form'] == 'original':
            assert r['s20_run'] == 'ladder100k' and r['s20_solved'] == '1', r['name']


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
        assert meta['size'] == EXPECTED_SIZE[n], n
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
        # level 10 has no S20 cost (S20_MK2 never solves it): the spread ladder's rows
        ten = [r['name'] for r in rows if int(r['level']) == 10]
        assert ten == [r['name'] for r in subsets[n][0] if int(r['level']) == 10] and set(ten) <= LEVEL_TEN
        if prev is not None:
            assert set(prev) <= {r['name'] for r in rows}
        prev = [r['name'] for r in rows]


def test_s20hard_level_nine_is_sorted_by_s20_cost(s20hard, pool):
    nine = {r['name']: int(r['s20_nodes']) for r in pool if r['level'] == '9'}
    assert len(nine) == 19
    for n in S20HARD_SIZES:
        picks = [r for r in s20hard[n][0] if r['level'] == '9']
        costs = [int(r['s20_nodes']) for r in picks]
        assert costs == sorted(costs, reverse=True) and len(picks) == min(n // 10, 19), n
    # every S20-unsolved row on record is greedy-unsolved too, hence at level 10
    assert all(r['level'] == '10' and r['greedy_solved'] == '0' for r in pool if r['s20_solved'] == '0')
