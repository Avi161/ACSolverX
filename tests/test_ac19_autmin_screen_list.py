"""The rebuilt orbit list, and the proof that it is the SAME list.

Every leftover CSV in ``results/heuristic_search/ac19_autmin_screen/`` names
orbits ``ac19_<n>`` from a list that was built off-repo and never committed.
``make_ac19_autmin_screen`` recovers it. Recovering "a" list is easy and
useless; these tests hold it to recovering "the" list -- same names, same
representatives, same members as the 1,000+ rows already on disk.
"""
import csv
import os

import pytest

from experiments.search import make_ac19_autmin_screen as build

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORBITS = build.OUT


def _orbits():
    if not os.path.exists(ORBITS):
        pytest.skip("orbit list not built; run make_ac19_autmin_screen --write")
    with open(ORBITS) as fh:
        return list(csv.DictReader(fh))


def test_the_dataset_decodes_to_the_documented_word_alphabet():
    assert build.decode("[-2, -2, -1, 2, 1, 0, 0, 0, -2, 1, 0, 0, 0, 0, 0, 0]") \
        == ("YYXyx", "Yx")
    assert build.decode("[0, 0, 0, 0]") == ("", "")


def test_orbits_are_indexed_by_their_first_dataset_member():
    rows = build.group(["b", "a", "b", "c", "a", "b"])
    assert [r["rep"] for r in rows] == ["b", "a", "c"]
    assert [r["members"] for r in rows] == [[0, 2, 5], [1, 4], [3]]


def test_the_csv_projection_matches_the_shipped_column_layout():
    rows = build.as_csv_rows([{"name": "ac19_0", "rep": ("xy", "Yx"),
                               "members": [0, 4, 9]}])
    assert list(rows) == [{"name": "ac19_0", "r1": "xy", "r2": "Yx",
                           "n_members": 3, "members": "0 4 9"}]
    assert build.FIELDS == ("name", "r1", "r2", "n_members", "members")


def test_verify_rejects_a_list_that_disagrees_with_a_shipped_row():
    """The cross-check has to be able to fail, or it proves nothing."""
    known = build.shipped_residues()
    assert known, "no shipped residue rows to check against"
    name, (_, row) = next(iter(sorted(known.items())))
    wrong = [{"name": name, "rep": (row["r1"] + "x", row["r2"]),
              "members": [0]}]
    with pytest.raises(SystemExit, match="does not reproduce"):
        build.verify(wrong, log=lambda _: None)


def test_verify_rejects_a_list_that_is_missing_a_shipped_row():
    with pytest.raises(SystemExit, match="does not reproduce"):
        build.verify([], log=lambda _: None)


def test_the_shipped_residues_are_a_subset_of_the_rebuilt_list():
    rows = {r["name"]: r for r in _orbits()}
    known = build.shipped_residues()
    missing = [n for n in known if n not in rows]
    assert not missing, f"{len(missing)} shipped rows absent: {missing[:5]}"
    for name, (source, want) in known.items():
        got = rows[name]
        assert (got["r1"], got["r2"]) == (want["r1"], want["r2"]), \
            f"{name} from {source}"
        assert got["n_members"] == want["n_members"], f"{name} from {source}"
        assert got["members"] == want["members"], f"{name} from {source}"


def test_the_rebuilt_list_is_the_screen_the_campaign_docs_describe():
    rows = _orbits()
    assert len(rows) == 72_779, "the screen is 72,779 Aut(F2) orbits"
    assert sum(int(r["n_members"]) for r in rows) == 156_762
    assert [r["name"] for r in rows[:3]] == ["ac19_0", "ac19_1", "ac19_2"]
    assert len({r["name"] for r in rows}) == len(rows)
    assert len({(r["r1"], r["r2"]) for r in rows}) == len(rows), \
        "one row per orbit means one representative per row"


def test_every_representative_is_its_own_aut_canonical_form():
    """Sampled, not exhaustive: full canonicalization is ~8 core-minutes."""
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    rows = _orbits()
    for row in rows[::7000]:
        assert aut_canon((row["r1"], row["r2"]))[1] == (row["r1"], row["r2"]), \
            row["name"]


def test_the_three_joint_survivors_come_off_this_list_unchanged():
    rows = {r["name"]: r for r in _orbits()}
    survivors = os.path.join(
        ROOT, "results", "heuristic_search", "ac19_hybrid_10m",
        "joint_survivors.csv")
    with open(survivors) as fh:
        for want in csv.DictReader(fh):
            got = rows[want["name"]]
            assert (got["r1"], got["r2"]) == (want["r1"], want["r2"])
            assert got["members"] == want["members"]


def test_the_cross_check_never_includes_the_file_it_is_checking():
    """`--write` drops the rebuilt list into the same directory the residues
    live in, and `--dataset-rows` drops a 156,762-row list beside it.
    Counting either as evidence would make `verify` pass on anything."""
    assert os.path.exists(ORBITS), "build the list first"
    known = build.shipped_residues()
    assert len(known) == 865, len(known)
    assert len(known) < 72_779
    with open(ORBITS) as fh:
        assert len(list(csv.DictReader(fh))) == 72_779
