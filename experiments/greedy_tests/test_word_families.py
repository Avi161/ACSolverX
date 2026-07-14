"""A1/A2/A3 z-word family builders (``experiments/stable_ac/word_families.py``).

Pure string processing -- no numba, no search, nothing above budget applies here.
"""

import pytest

from experiments.stable_ac.word_families import (
    A1_DEFAULT_WORDS, a2_raw_count, build_a1, build_a2, build_a3, build_family,
    free_reduce_str,
)

REL2 = ["xXyY", "xy"]              # a 2-generator input, alphabet {x, y}
REL3 = ["xyzXYZ", "xy", "yz"]      # a 3-generator input, alphabet {x, y, z}


# -- free_reduce_str -----------------------------------------------------------


@pytest.mark.parametrize("s,expected", [
    ("xX", ""),
    ("xyYX", ""),
    ("xyXx", "xy"),      # 'Xx' cancels, leaving 'xy' -- verified by hand, not "xyXx" unchanged
    ("xyYx", "xx"),      # 'yY' cancels, leaving 'xx'
    ("", ""),
    ("xyz", "xyz"),      # nothing to cancel
])
def test_free_reduce_str_hand_cases(s, expected):
    assert free_reduce_str(s) == expected


def test_free_reduce_str_is_idempotent():
    for s in ("xyXx", "xXyYxy", "XYZzyx"):
        once = free_reduce_str(s)
        assert free_reduce_str(once) == once


# -- build_a1 --------------------------------------------------------------


def test_a1_default_words_are_reduced_nonempty_and_in_alphabet():
    words = build_a1(REL2)
    assert all(w == free_reduce_str(w) for w in words)
    assert all(w for w in words)
    assert all(c.lower() in {"x", "y"} for w in words for c in w)


def test_a1_dedups_order_preserving():
    words = build_a1(REL2, words=["x", "xy", "x", "y", "xy"])
    assert words == ["x", "xy", "y"]


def test_a1_default_word_count_matches_the_curated_list():
    # every default word is already reduced and non-empty, so nothing is dropped
    assert len(build_a1(REL2)) == len(A1_DEFAULT_WORDS)


def test_a1_rejects_a_generator_outside_the_relator_alphabet():
    with pytest.raises(AssertionError):
        build_a1(REL2, words=["z"])


def test_a1_words_none_uses_the_default():
    assert build_a1(REL2, words=None) == build_a1(REL2)


# -- build_a2 ----------------------------------------------------------------


@pytest.mark.parametrize("relators", [
    ["xyx", "yxy"],
    ["xXyY"],
    ["xy", "yx", "xyx"],
])
def test_a2_raw_count_is_sum_of_squared_lengths(relators):
    assert a2_raw_count(relators) == sum(len(r) ** 2 for r in relators)


def test_a2_output_is_reduced_nonempty_and_deduped():
    words = build_a2(["xyx", "yxy"])
    assert all(w == free_reduce_str(w) for w in words)
    assert all(w for w in words)
    assert len(words) == len(set(words))


def test_a2_is_deterministic_across_calls():
    a = build_a2(["YYYxyXYX", "YYXyx"])
    b = build_a2(["YYYxyXYX", "YYXyx"])
    assert a == b


def test_a2_max_words_caps_to_exactly_max_words_evenly_spaced_including_endpoints():
    full = build_a2(["YYYxyXYX", "YYXyx"])
    capped = build_a2(["YYYxyXYX", "YYXyx"], max_words=5)
    assert len(capped) == 5
    assert capped[0] == full[0] and capped[-1] == full[-1]
    assert all(w in full for w in capped)


def test_a2_max_words_above_the_deduped_count_is_a_noop():
    full = build_a2(["xyx", "yxy"])
    assert build_a2(["xyx", "yxy"], max_words=len(full) + 10) == full


def test_a2_drop_len1_removes_length_one_words():
    with_len1 = build_a2(["xyx", "yxy"])
    without = build_a2(["xyx", "yxy"], drop_len1=True)
    assert any(len(w) == 1 for w in with_len1)
    assert all(len(w) != 1 for w in without)
    assert set(without) == {w for w in with_len1 if len(w) != 1}


# -- build_a3 ----------------------------------------------------------------


def test_a3_respects_the_grid_size_upper_bound():
    grid = (0.25, 0.5, 0.75, 1.0)
    words = build_a3(["YYYxyXYX", "YYXyx"], grid=grid)
    assert len(words) <= len(grid) ** 2


def test_a3_words_are_free_reduced_and_nonempty():
    words = build_a3(["YYYxyXYX", "YYXyx"])
    assert all(w == free_reduce_str(w) for w in words)
    assert all(w for w in words)


def test_a3_dedups():
    words = build_a3(["YYYxyXYX", "YYXyx"])
    assert len(words) == len(set(words))


def test_a3_uses_only_the_first_two_relators():
    pair = build_a3(["YYYxyXYX", "YYXyx"])
    triple = build_a3(["YYYxyXYX", "YYXyx", "zzz"])
    assert pair == triple


# -- alphabet restriction ------------------------------------------------------


def test_builders_never_emit_a_generator_outside_the_input_alphabet():
    for w in build_a1(REL2) + build_a2(REL2) + build_a3(REL2):
        assert all(c.lower() in {"x", "y"} for c in w), f"{w!r} escapes {{x, y}}"


# -- modularity: unchanged on a 3-relator/3-generator input --------------------


def test_builders_work_unchanged_on_a_three_relator_input():
    alphabet = {"x", "y", "z"}
    for builder in (build_a1, build_a2, build_a3):
        words = builder(REL3)
        assert words, f"{builder.__name__} produced nothing on a 3-relator input"
        for w in words:
            assert w == free_reduce_str(w)
            assert all(c.lower() in alphabet for c in w)


# -- build_family dispatch -----------------------------------------------------


def test_build_family_dispatches_to_each_builder():
    cfg = {"A1_WORDS": None, "A2_MAX_WORDS": None, "A2_DROP_LEN1": False,
           "A3_GRID": (0.25, 0.5, 0.75, 1.0)}
    assert build_family("A1", REL2, cfg) == build_a1(REL2)
    assert build_family("A2", REL2, cfg) == build_a2(REL2)
    assert build_family("A3", REL2, cfg) == build_a3(REL2)


def test_build_family_passes_through_cfg_knobs():
    cfg = {"A2_MAX_WORDS": 3, "A2_DROP_LEN1": True}
    assert build_family("A2", ["xyx", "yxy"], cfg) == \
        build_a2(["xyx", "yxy"], max_words=3, drop_len1=True)


def test_build_family_raises_on_unknown_family():
    with pytest.raises(ValueError):
        build_family("A4", REL2, {})
