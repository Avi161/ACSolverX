"""The rank-3 study carried in results/stable_ac/rank3_bf/: the manifest of its raw files, the numbers the docs quote
(read from its stored summaries), and its agreement with this branch's own runs (results/rank3_bf, ms640_length_fast).
The study is the source branch's results folder minus the raw per-search files; see its README.md."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
from conftest import ROOT

STUDY = Path(ROOT, "results", "stable_ac", "rank3_bf")
OURS = Path(ROOT, "results", "rank3_bf", "summary.json")
LENGTH_RUN = Path(ROOT, "results", "ms640_length_fast", "summary.json")
RAW_SUFFIXES = (".npz", ".jsonl", ".jsonl.gz")


def load(path):
    with open(path) as f:
        return json.load(f)


def stored(name):
    return load(STUDY / name)


def run_summary(path):
    if not path.exists():
        pytest.skip(f"{path} is not shipped")
    return load(path)


def manifest_files():
    return stored("MANIFEST.json")["files"]


def test_manifest_schema_and_source_commit():
    manifest = stored("MANIFEST.json")
    assert set(manifest) == {"source", "s3", "files"}
    assert manifest["source"]["branch"] == "rank3/brute-force-baseline"
    assert manifest["source"]["commit"].startswith("f2d53ced") and len(manifest["source"]["commit"]) == 40
    assert manifest["source"]["dir"] == "results/stable_ac/rank3_bf"
    assert manifest["s3"] == "s3://acsolver-u124-205558941715/cov_all/rank3_bf/"
    for entry in manifest["files"]:
        assert set(entry) == {"path", "bytes", "sha256", "in_repo"}
        assert entry["path"].endswith(RAW_SUFFIXES) and entry["bytes"] > 0
        assert re.fullmatch("[0-9a-f]{64}", entry["sha256"]) and entry["in_repo"] is False
    assert len(manifest["files"]) == 102 and sum(e["bytes"] for e in manifest["files"]) == 70_549_382


def test_no_listed_raw_file_is_committed():
    """The raw files are fetched on demand (README.md), so git must not track any; .gitignore keeps a fetched one out."""
    try:
        tracked = subprocess.run(["git", "ls-files", "--", str(STUDY)], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    listed = {f"results/stable_ac/rank3_bf/{e['path']}" for e in manifest_files()}
    assert not listed & set(tracked)
    assert not [p for p in tracked if p.endswith(RAW_SUFFIXES)]


def test_a_fetched_raw_file_matches_its_manifest_entry():
    for entry in manifest_files():
        path = STUDY / entry["path"]
        if path.exists():
            assert path.stat().st_size == entry["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_stored_summaries_hold_the_numbers_the_docs_quote():
    b1000 = stored("rank3_bf_ms640_b1000_cap24_summary.json")["views"]["1000"]
    b10000 = stored("rank3_bf_ms640_b10000_cap24_summary.json")["views"]["10000"]
    assert (b1000["control_solved"], b10000["control_solved"]) == (554, 606)
    assert [(v["oracle"][-1]["max_len"], v["oracle"][-1]["solved_by_some_word"]) for v in (b1000, b10000)] == [
        (10, 578), (7, 608)]
    assert stored("rankn_bf_ms640_b1000_cap24_r4_summary.json")["solved_by_some_combo"] == 506
    assert stored("rankn_bf_ms640_b1000_cap24_r5_summary.json")["solved_by_some_combo"] == 416
    total = stored("cap/cap_counters_cap24.json")["total"]
    assert (total["searches"], total["cap_dropped_a_child"], total["cap_could_bind"]) == (40_098_032, 2_331_711, 0)


# length: (solved by some word, gained over the control, control rows lost by every word) at budget 1,000.
STORED_L1_4 = {1: (403, 0, 151), 2: (472, 0, 82), 3: (516, 0, 38), 4: (540, 4, 18)}


@pytest.mark.parametrize("length", STORED_L1_4)
def test_our_rank3_run_agrees_with_the_stored_budget_1000_summary(length):
    """Reads only ``control_solved``, each bucket's ``solved`` and its ``oracle`` counts, not the comparison columns."""
    ours = run_summary(OURS)
    view = stored("rank3_bf_ms640_b1000_cap24_summary.json")["views"]["1000"]
    row, oracle = view["by_length"][length - 1], view["oracle"][length - 1]
    bucket = ours["buckets"][f"L{length}"]
    assert ours["control_solved"] == view["control_solved"] == 554
    assert bucket["solved"] == pytest.approx(row["solve_rate"], abs=5e-5)
    assert (bucket["oracle"]["solved_by_some"], bucket["oracle"]["gained_over_control"],
            bucket["oracle"]["control_solved_lost_by_every"]) == STORED_L1_4[length]
    assert (oracle["solved_by_some_word"], oracle["gained_over_control"],
            oracle["control_solved_lost_by_every_word"]) == STORED_L1_4[length]


def test_stored_budget_10000_control_is_our_length_run():
    """The study's control is the plain LENGTH greedy at cap 24: its 606 solves and 576,053 pops are ms640_length_fast."""
    with open(STUDY / "rank3_bf_ms640_b10000_cap24_per_presentation.csv") as f:
        rows = list(csv.DictReader(f))
    solved = [r for r in rows if r["control_solved"] == "1"]
    stored_control = (len(solved), sum(int(r["control_nodes"]) for r in rows),
                      sum(int(r["control_nodes"]) for r in solved), sum(int(r["control_path_length"]) for r in solved))
    run = run_summary(LENGTH_RUN)
    assert stored_control == (run["solved"], run["cost"]["total"], run["cost"]["on_solved"],
                              run["path_length"]["ac_path"]["sub_moves"]["sum"]) == (606, 576_053, 236_053, 12_103)
