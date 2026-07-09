"""Run identity: the jsonl filename, and what may and may not appear in it.

Two rules, both learned the hard way:

* the stem must encode **every knob that changes the computed result**, or two
  different experiments silently merge into one file (resume skips by
  ``pres_id``, not by configuration); and
* it must encode **nothing that varies per invocation**, above all the date, or
  a run continued the next day finds no prior rows and restarts from scratch.

The table below is the enforcement: flip an included knob, the prefix must move;
flip an excluded one, it must not.
"""

import os

import pytest

from experiments.run_baseline import (
    DEFAULT_CONFIG, _read_done, _resolve_paths, _run_prefix, _subset_tag,
)

BASE = dict(DEFAULT_CONFIG)

#: knobs that change the search result -> must appear in the run identity
INCLUDED = [
    ("MAX_RELATOR_LENGTH", 48),
    ("CYCLIC_REDUCE", False),
    ("SUBSET", (0, 5)),
]

#: knobs that change only what is stored or how fast -> must NOT appear
EXCLUDED = [
    ("use_min_relator", False),
    ("use_max_relator", False),
    ("use_max_relator_expanded", False),
    ("use_time", False),
    ("use_path", False),
    ("PATH_IN_SEPARATE_FILE", False),
    ("PATH_FORMAT", "strings"),
    ("HIGH_SPEEDUP", True),
    ("N_WORKERS", 8),
    ("GB_PER_PRES", 1.0),
    ("HEARTBEAT_EVERY_S", 90),
    ("HEARTBEAT_DEBUG", True),
    ("PROGRESS_EVERY", 1),
    ("RESUME", False),
    ("USE_WANDB", True),
    ("WANDB_PROJECT", "other"),
]


def _prefix(**over):
    return _run_prefix({**BASE, **over}, 10000, 640)


@pytest.mark.parametrize("key,value", INCLUDED, ids=[k for k, _ in INCLUDED])
def test_result_affecting_knobs_change_the_run_identity(key, value):
    assert _prefix(**{key: value}) != _prefix()


@pytest.mark.parametrize("key,value", EXCLUDED, ids=[k for k, _ in EXCLUDED])
def test_result_neutral_knobs_do_not_change_the_run_identity(key, value):
    """Resume must reuse rows written under a different toggle for these."""
    assert _prefix(**{key: value}) == _prefix()


def test_budget_and_n_pres_are_part_of_the_identity():
    cfg = dict(BASE)
    assert _run_prefix(cfg, 1000, 640) != _run_prefix(cfg, 5000, 640)
    assert _run_prefix(cfg, 1000, 640) != _run_prefix(cfg, 1000, 10)


def test_prefix_contains_no_date():
    from datetime import datetime

    today = datetime.now().strftime("%m_%d_%y")
    assert today not in _run_prefix(dict(BASE), 10000, 640)


def test_prefix_shape():
    assert _run_prefix(dict(BASE), 10000, 640) == "greedy_10000_640_mrl24_cyc_all_"
    cfg = {**BASE, "CYCLIC_REDUCE": False, "SUBSET": (3, 9)}
    assert _run_prefix(cfg, 50, 6) == "greedy_50_6_mrl24_noncyc_3-9_"


# -- _subset_tag -------------------------------------------------------------


def test_subset_tag_none_is_all():
    assert _subset_tag(None) == "all"


def test_subset_tag_tuple_is_a_range():
    assert _subset_tag((10, 20)) == "10-20"


def test_subset_tag_of_a_list_is_order_independent():
    assert _subset_tag([3, 1, 2]) == _subset_tag([1, 2, 3])
    assert _subset_tag([1, 2, 3]).startswith("ids")


def test_a_five_element_range_and_a_five_element_list_do_not_collide():
    """Both have n_pres=5, so only the tag can separate them."""
    assert _subset_tag((0, 5)) != _subset_tag([10, 20, 30, 40, 50])


# -- _resolve_paths ----------------------------------------------------------


def _seed(out_dir, name, n_rows):
    p = os.path.join(out_dir, name)
    with open(p, "w") as f:
        for i in range(n_rows):
            f.write('{"pres_id": %d, "solved": true}\n' % i)
    return p


def test_resume_reattaches_to_an_existing_file_from_another_day(out_dir):
    """The whole point of the jsonl: a run continued after midnight must not restart."""
    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir, "RESUME": True}
    prefix = _run_prefix(cfg, 10000, 640)
    _seed(out_dir, prefix + "01_01_20.jsonl", 4)

    out_path, paths_path, date, stem = _resolve_paths(cfg, 10000, 640)
    assert os.path.basename(out_path) == prefix + "01_01_20.jsonl"
    assert stem == prefix + "01_01_20"
    assert _read_done(out_path)[1] == 4


def test_resume_picks_the_file_with_the_most_rows(out_dir):
    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir, "RESUME": True}
    prefix = _run_prefix(cfg, 10000, 640)
    _seed(out_dir, prefix + "01_01_20.jsonl", 2)
    _seed(out_dir, prefix + "02_02_20.jsonl", 9)
    out_path, *_ = _resolve_paths(cfg, 10000, 640)
    assert os.path.basename(out_path) == prefix + "02_02_20.jsonl"


def test_resume_ignores_the_paths_sidecar_when_reattaching(out_dir):
    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir, "RESUME": True}
    prefix = _run_prefix(cfg, 10000, 640)
    _seed(out_dir, prefix + "01_01_20_paths.jsonl", 99)
    _seed(out_dir, prefix + "01_01_20.jsonl", 1)
    out_path, paths_path, _, _ = _resolve_paths(cfg, 10000, 640)
    assert out_path.endswith(prefix + "01_01_20.jsonl")
    assert paths_path.endswith(prefix + "01_01_20_paths.jsonl")


def test_resume_off_mints_a_fresh_dated_file(out_dir):
    from datetime import datetime

    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir, "RESUME": False}
    prefix = _run_prefix(cfg, 10000, 640)
    _seed(out_dir, prefix + "01_01_20.jsonl", 4)
    out_path, *_ = _resolve_paths(cfg, 10000, 640)
    today = datetime.now().strftime("%m_%d_%y")
    assert os.path.basename(out_path) == prefix + today + ".jsonl"


def test_a_different_budget_resolves_to_a_different_file(out_dir):
    """CLAUDE.md's multi-budget rule, at the level where it is actually implemented."""
    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir}
    a, _, _, _ = _resolve_paths(cfg, 1000, 640)
    b, _, _, _ = _resolve_paths(cfg, 5000, 640)
    assert a != b


def test_a_different_cap_or_cyclic_mode_resolves_to_a_different_file(out_dir):
    cfg = {**BASE, "LOCAL_OUT_DIR": out_dir}
    base, *_ = _resolve_paths(cfg, 1000, 640)
    cap, *_ = _resolve_paths({**cfg, "MAX_RELATOR_LENGTH": 32}, 1000, 640)
    cyc, *_ = _resolve_paths({**cfg, "CYCLIC_REDUCE": False}, 1000, 640)
    assert len({base, cap, cyc}) == 3


def test_out_dir_is_created(tmp_path):
    target = str(tmp_path / "nested" / "deep")
    cfg = {**BASE, "LOCAL_OUT_DIR": target}
    _resolve_paths(cfg, 10, 1)
    assert os.path.isdir(target)


def test_mount_drive_selects_the_drive_directory(tmp_path):
    drive = str(tmp_path / "drive")
    cfg = {**BASE, "MOUNT_DRIVE": True, "DRIVE_OUT_DIR": drive,
           "LOCAL_OUT_DIR": str(tmp_path / "local")}
    out_path, *_ = _resolve_paths(cfg, 10, 1)
    assert out_path.startswith(drive)
