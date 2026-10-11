"""Benchmarks and curated data: every shipped file loads and has its expected row count.

Provenance (verbatim copies, checked by git blob hash; LADDER.md and README_aca_124.md also carry
a provenance note): ``benchmark/ladder/`` from
``origin/claude/ac19-theorem-strength-8v1wp6`` (no ``ladder_all.csv``, no scripts, no runs);
``data/AC19_extended_aut_min.csv`` and ``benchmark/splits/splits_ac1m_hard_aut.json`` from
``origin/cursor/heur-12h-anti-overfit-a42e``; ``data/AC1M_aut_min.csv.gz`` from
``origin/claude/vigilant-babbage-nnbuj0``; ``data/ms_unsolved_reps/aca_124_*`` from
``origin/cursor/u124-stable-ac-1b54``; ``data/equivalence_classes/certificates.json`` from
``origin/codex/proofs``; ``benchmark/difficulty_bins.csv`` from
``origin/claude/summer-results-docs-scoring-u6klsb``.
"""
import collections
import csv
import gzip
import json
import os

import pytest

from acx import data
from acx.search import search
from acx.verify.replay import abs_det

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LADDER = "benchmark/ladder"
SPLIT = "benchmark/splits/splits_ac1m_hard_aut.json"

# Nested ladder panels. The 99 / 188 / 268 / 377 sizes are population caps (see LADDER.md).
LADDER_SIZES = {20: 20, 40: 40, 60: 60, 100: 99, 200: 188, 300: 268, 500: 377}
S20HARD_SIZES = {20: 20, 40: 40, 60: 60, 100: 99, 200: 188, 300: 268}


def path(rel):
    return os.path.join(ROOT, rel)


def read_csv(rel):
    with open(path(rel), newline="") as f:
        return list(csv.DictReader(f))


def read_json(rel):
    with open(path(rel)) as f:
        return json.load(f)


@pytest.mark.parametrize("name,n", [("bench10", 10), ("bench20", 20), ("bench40", 40), ("bench60", 60)])
def test_benchmark_subsets(name, n):
    assert len(data.load_csv(name)) == n


def test_ms640_full():
    assert len(data.load("ms640")) == 640


@pytest.mark.parametrize("size", sorted(LADDER_SIZES))
def test_ladder_panel(size):
    rows = data.load_csv(f"{LADDER}/ladder_{size}.csv")
    assert len(rows) == LADDER_SIZES[size]
    assert {int(r.meta["level"]) for r in rows} <= set(range(1, 11))


@pytest.mark.parametrize("size", sorted(S20HARD_SIZES))
def test_ladder_s20hard_panel(size):
    assert len(data.load_csv(f"{LADDER}/ladder_{size}_s20hard.csv")) == S20HARD_SIZES[size]


def test_ladder_200_level_counts():
    levels = collections.Counter(int(r["level"]) for r in read_csv(f"{LADDER}/ladder_200.csv"))
    assert [levels[k] for k in range(1, 11)] == [20] * 8 + [19, 9]


def test_ladder_subsets_nest():
    names = [{r["name"] for r in read_csv(f"{LADDER}/ladder_{k}.csv")} for k in sorted(LADDER_SIZES)]
    assert all(a <= b for a, b in zip(names, names[1:]))


@pytest.mark.parametrize("rel,n", [
    (f"{LADDER}/unsolved_124.csv", 124),
    (f"{LADDER}/unsolved_all_forms.csv", 1059),
    (f"{LADDER}/originals_45.csv", 45),
    ("data/ms_unsolved_reps/aca_124_initial.csv", 124),
    ("data/ms_unsolved_reps/aca_124_reduced.csv", 124),
    ("data/ms_unsolved_reps/aca_124_best.csv", 124),
    ("data/AC19_extended_aut_min.csv", 72779),
    ("benchmark/difficulty_bins.csv", 640),
])
def test_csv_row_count(rel, n):
    assert len(data.load_csv(rel)) == n


def test_difficulty_bins_cover_ms640():
    rows = data.load_csv("benchmark/difficulty_bins.csv")
    assert {r.id for r in rows} == {str(i) for i in range(640)}


def test_ladder_pairs_table():
    rows = read_csv(f"{LADDER}/ladder_pairs.csv")
    assert len(rows) == 45 and len({r["orig_name"] for r in rows}) == 45


def test_ladder_manifest_pool_size():
    assert read_json(f"{LADDER}/ladder_manifest.json")["rows"] == 73464


def test_certificates_cover_unsolved_classes():
    classes = read_json("data/equivalence_classes/certificates.json")["classes"]
    assert len(classes) == 124
    assert sum(c["size"] for c in classes) == 261


def test_ac1m_aut_min_rows():
    with gzip.open(path("data/AC1M_aut_min.csv.gz"), "rt") as f:
        assert sum(1 for _ in csv.DictReader(f)) == 71283


def test_ac1m_hard_aut_train_and_holdout():
    holdout = data.load_split(SPLIT, "holdout")
    train = data.load_split(SPLIT, "train")
    assert (len(holdout), len(train)) == (60, 120)
    assert not {r.id for r in holdout} & {r.id for r in train}


@pytest.mark.parametrize("part", ["holdout", "train"])
def test_ac1m_hard_aut_rows_match_ac1m_lines(part):
    rows = data.load_split(SPLIT, part)
    lines = data.load("ac1m", ids=[r.id for r in rows])
    assert [r.pres for r in rows] == [r.pres for r in lines]


def test_certificates_summary_edge_types():
    s = read_json("data/equivalence_classes/certificates.json")["summary"]
    assert (s["presentations"], s["classes"], s["edges"]) == (261, 124, 137)
    assert s["cv_edges"] + s["ac_edges"] == s["edges"]


def test_u124_best_is_initial_with_36_shorter_rows():
    total = {k: sum(len(r["r1"]) + len(r["r2"]) for r in read_csv(f"data/ms_unsolved_reps/aca_124_{k}.csv"))
             for k in ("initial", "best")}
    assert (total["initial"], total["best"]) == (2446, 2356)
    reduced = read_csv("data/ms_unsolved_reps/aca_124_reduced.csv")
    assert sum(r["reduced"] == "yes" for r in reduced) == 36


def level_of(g, edge=2253802):
    bands = [1000, 10000, 31623, 100000, 316228, 1000000, edge, 10000001]
    return next(k + 1 for k, hi in enumerate(bands) if g < hi)


@pytest.mark.parametrize("size", sorted(LADDER_SIZES))
def test_ladder_levels_follow_recorded_greedy_nodes(size):
    for r in read_csv(f"{LADDER}/ladder_{size}.csv"):
        if r["greedy_solved"] == "1":
            assert level_of(int(r["greedy_nodes"])) == int(r["level"]), r["name"]
        else:
            assert int(r["level"]) >= 9, r["name"]


def test_ladder_rows_equal_their_source_rows():
    autmin = {r["name"]: (r["r1"], r["r2"]) for r in read_csv("data/AC19_extended_aut_min.csv")}
    ms640 = data.load("ms640")
    for r in read_csv(f"{LADDER}/ladder_500.csv"):
        if r["source"] == "ac19":
            assert autmin[r["name"]] == (r["r1"], r["r2"]), r["name"]
        else:
            assert ms640[int(r["name"].split("_")[1])].pres.strs == (r["r1"], r["r2"]), r["name"]


def test_every_loaded_presentation_is_balanced():
    for rel in ("ladder/ladder_500.csv", "ladder/unsolved_all_forms.csv", "../data/ms_unsolved_reps/aca_124_best.csv"):
        assert all(abs_det(r.pres) == 1 for r in data.load_csv(f"benchmark/{rel}")), rel
    assert all(abs_det(r.pres) == 1 for r in data.load_split(SPLIT, "holdout") + data.load_split(SPLIT, "train"))


def test_search_reproduces_recorded_ladder_pops():
    """The spec backend, at each row's recorded cap, pops exactly the recorded greedy node count."""
    rows = [r for r in read_csv(f"{LADDER}/ladder_60.csv") if r["greedy_solved"] == "1" and int(r["greedy_nodes"]) <= 1000]
    assert len(rows) >= 5
    for r in rows:
        res = search([r["r1"], r["r2"]], cap=int(r["greedy_cap"]), budget=1001)
        assert (res.solved, res.pops) == (True, int(r["greedy_nodes"])), r["name"]
