"""The exhaustive CoV sweep on MS640 (``results/stable_ac/cov_all/``): its stored numbers, its manifest, and the checks
that acx accepts the rows it ships.

The sweep ran on its own branch: the control and every start of the family ``suballpxyb8`` (114,682 searches per budget)
at 100, 10,000 and 100,000 nodes. Only the 100,000 file is here, because it holds every start's transform. A search at a
smaller budget is the first pops of a larger one, so that file also answers 100 and 1,000 (and 10,000).
"""
import csv
import gzip
import hashlib
import json
import os
import random
import re
from collections import Counter, defaultdict
from typing import NamedTuple

import pytest
from conftest import ROOT

from acx.core.config import SearchConfig
from acx.core.words import Presentation, parse
from acx.cov import apply_steps
from acx.search import search

STUDY = os.path.join(ROOT, "results", "stable_ac", "cov_all")
STEM = "cov_all_suballpxyb8_ms640_"
ROWS_FILE = STEM + "b100000.jsonl.gz"
README = os.path.join(STUDY, "README.md")
BUDGETS = (100, 1_000, 10_000, 100_000)

# budget: (presentations the control solves, presentations some start solves), of 640
HEADLINE = {100: (455, 555), 1_000: (554, 604), 10_000: (606, 626), 100_000: (634, 640)}
# budget: share of a random start that is cheaper / equal / dearer than the control / unsolved, in percent
RANDOM_START = {100: (26.2, 9.5, 31.6, 32.7), 1_000: (30.9, 9.6, 41.8, 17.7),
                10_000: (33.0, 9.6, 48.2, 9.2), 100_000: (33.7, 9.6, 52.4, 4.2)}
# budget: searches solved of 114,682
ROWS_SOLVED = {100: 90_234, 1_000: 101_108, 10_000: 106_843, 100_000: 111_878}
# budget: the best start of each presentation is the control / in its Aut(F2) orbit / outside it / none solves
BEST_START = {100: (0, 269, 286, 85), 1_000: (1, 304, 299, 36), 10_000: (3, 323, 300, 14), 100_000: (3, 329, 308, 0)}
# budget: presentations the control fails and some start solves
RESCUED = {100: 100, 1_000: 50, 10_000: 20, 100_000: 6}
# budget: (control, some start) solves on subset 60, the rows of benchmark/subsets/benchmark_subset_60.csv
SUBSET_60 = {100: (17, 34), 1_000: (29, 45), 10_000: (40, 52), 100_000: (54, 60)}
# run budget: (CPU-hours of search, mean nodes over all the starts of a presentation)
COST = {100: (1.086, 5_328.4), 10_000: (49.767, 164_758.7), 100_000: (335.237, 657_198.0)}


def study_path(name):
    return os.path.join(STUDY, name)


def load_json(name):
    with open(study_path(name)) as f:
        return json.load(f)


def summary(run=100_000):
    """The statistics file of the run at ``run`` nodes (the 100,000 file holds the figures of every smaller budget)."""
    return load_json(f"{STEM}b{run}_summary.json")


def sha256_and_size(stream):
    """The sha256 (hex) and the byte count of what ``stream`` yields."""
    digest, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1 << 20), b""):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def read_rows():
    """The rows of the shipped 100,000 file, one at a time."""
    with gzip.open(study_path(ROWS_FILE), "rt") as f:
        for line in f:
            yield json.loads(line)


class Start(NamedTuple):
    """What the statistics need of a row (the whole file is 88 MB of JSON)."""
    pres_id: int
    is_control: bool
    solved: bool
    nodes: int
    in_orbit: bool      # aut_canon_cov == aut_canon_orig: by acx's typing the solve carries back to an AC path
    one_pattern: bool
    cap: int            # the relator cap the search ran at
    longest: int        # the longer relator of the start, as written


class Scan(NamedTuple):
    starts: list        # every row of the file as a ``Start``
    with_path: list     # the rows that keep their ``path_moves`` (a 2% sample), whole


@pytest.fixture(scope="module")
def scan():
    """One pass over the file."""
    starts, with_path = [], []
    for row in read_rows():
        starts.append(Start(row["pres_id"], row["is_control"], row["solved"], row["nodes_explored"],
                            row["aut_canon_cov"] == row["aut_canon_orig"], bool(row["is_one_pattern"]),
                            row["max_relator_length_cap"], max(len(row["r1"]), len(row["r2"]))))
        if "path_moves" in row:
            with_path.append(row)
    return Scan(starts, with_path)


def solving_starts(starts, budget):
    """``{pres_id: [the searches that solved it within budget]}``."""
    solving = defaultdict(list)
    for s in starts:
        if s.solved and s.nodes <= budget:
            solving[s.pres_id].append(s)
    return solving


def kind(start):
    """How a solve is typed: the control, a start in the row's Aut(F2) orbit, or one outside it."""
    if start.is_control:
        return "control"
    return "in orbit" if start.in_orbit else "outside"


# ---- the stored numbers --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("budget", BUDGETS)
def test_headline_numbers_per_budget(budget):
    per_budget = summary()["per_budget"][str(budget)]
    control, oracle = HEADLINE[budget]
    assert per_budget["control"]["solved"] == control
    assert per_budget["oracle_all"]["solved"] == oracle
    assert per_budget["oracle_one"]["solved"] == oracle
    assert per_budget["solved_only_via_non_one_pattern_start"]["count"] == 0


@pytest.mark.parametrize("budget", BUDGETS)
def test_a_random_start_against_the_control(budget):
    shares = summary()["per_budget"][str(budget)]["random_start_vs_control_mean_fraction"]
    got = [100 * shares[k] for k in ("cheaper", "equal", "dearer", "fail")]
    assert got == pytest.approx(RANDOM_START[budget], abs=0.06)       # the table prints one decimal


@pytest.mark.parametrize("run", COST)
def test_what_each_run_cost(run):
    cpu_hours, mean_nodes = COST[run]
    assert summary(run)["cpu_hours"] == cpu_hours
    assert summary(run)["total_cov_nodes_per_presentation"]["mean"] == mean_nodes


def per_presentation():
    with open(study_path(STEM + "b100000_per_presentation.csv")) as f:
        return list(csv.DictReader(f))


def test_per_presentation_table_sums():
    table = per_presentation()
    starts = [int(row["cov_starts"]) for row in table]
    assert len(table) == 640
    assert sum(int(row["control_solved"]) for row in table) == 634
    assert sum(starts) == 114_042
    assert sum(int(row["cov_solved_starts"]) for row in table) == 111_244
    assert (min(starts), max(starts)) == (5, 10_740)


def test_the_100_000_file_holds_every_search_and_a_sample_of_the_paths(scan):
    controls = [s for s in scan.starts if s.is_control]
    unsolved = [s for s in scan.starts if not s.solved]
    assert len(scan.starts) == 114_682
    assert (len(controls), sum(s.solved for s in controls)) == (640, 634)
    assert sum(s.one_pattern for s in scan.starts) == 14_051
    assert (len(unsolved), len({s.pres_id for s in unsolved})) == (2_804, 140)      # searches, presentations
    assert len(scan.with_path) == 2_263
    assert all(row["solved"] for row in scan.with_path)


@pytest.mark.parametrize("budget", BUDGETS)
def test_searches_solved_per_budget(scan, budget):
    assert sum(s.solved and s.nodes <= budget for s in scan.starts) == ROWS_SOLVED[budget]


def test_starts_in_the_orbit(scan):
    cov = [s for s in scan.starts if not s.is_control]
    assert sum(s.in_orbit for s in cov) == 7_206
    assert sum(s.in_orbit for s in cov if s.solved) == 6_856
    assert sum(not s.in_orbit for s in cov if s.solved) == 104_388


def test_the_caps_the_searches_ran_at(scan):
    """The control ran at cap 24; a start at its longer relator plus 16 (at least 24), so 24 to 91."""
    cov = [s for s in scan.starts if not s.is_control]
    assert {s.cap for s in scan.starts if s.is_control} == {24}
    assert all(s.cap == max(24, s.longest + 16) for s in cov)
    assert (min(s.cap for s in cov), max(s.cap for s in cov)) == (24, 91)
    assert sum(s.cap > 24 for s in cov) == 109_336


@pytest.mark.parametrize("budget", BUDGETS)
def test_subset_60_is_bench60(scan, budget):
    with open(os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.csv")) as f:
        subset = {int(row["pres_id"]) for row in csv.DictReader(f)}
    solving = {pid: group for pid, group in solving_starts(scan.starts, budget).items() if pid in subset}
    control = sum(any(s.is_control for s in group) for group in solving.values())
    assert (control, len(solving)) == SUBSET_60[budget]


@pytest.mark.parametrize("budget", BUDGETS)
def test_the_best_start_of_each_presentation_by_kind(scan, budget):
    """The cheapest search that solved a presentation (the control wins a tie), by acx's typing of its solve."""
    solving = solving_starts(scan.starts, budget)
    kinds = Counter(kind(min(group, key=lambda s: (s.nodes, not s.is_control))) for group in solving.values())
    unsolved = 640 - len(solving)
    assert (kinds["control"], kinds["in orbit"], kinds["outside"], unsolved) == BEST_START[budget]


@pytest.mark.parametrize("budget", BUDGETS)
def test_a_row_the_control_fails_has_a_solving_start_in_its_orbit(scan, budget):
    solving = solving_starts(scan.starts, budget).values()
    rescued = [group for group in solving if not any(s.is_control for s in group)]
    assert len(rescued) == RESCUED[budget]
    assert all(any(s.in_orbit for s in group) for group in rescued)


# ---- the manifest --------------------------------------------------------------------------------------------------

RAW_SUFFIXES = (".jsonl", ".jsonl.gz", ".npz")
# every raw file of the sweep -> is it in this checkout? Only the 100,000 file is.
RAW_FILES = {
    STEM + "b100.jsonl.gz": False,
    STEM + "b100.jsonl": False,
    STEM + "b10000.jsonl.gz": False,
    STEM + "b10000.jsonl": False,
    STEM + "b100000.jsonl.gz": True,
    STEM + "b100000.jsonl": False,
}


def manifest_files():
    return {entry["path"]: entry for entry in load_json("MANIFEST.json")["files"]}


def test_the_manifest_names_the_source_and_every_raw_file():
    manifest = load_json("MANIFEST.json")
    assert manifest["source"]["branch"] == "cov/all-subsets-sweep"
    assert manifest["source"]["commit"].startswith("fb84a588") and len(manifest["source"]["commit"]) == 40
    assert manifest["source"]["dir"] == "results/stable_ac/cov_all"
    assert manifest["s3"] == "s3://acsolver-u124-205558941715/cov_all/b<budget>/results/"
    assert {entry["path"]: entry["in_repo"] for entry in manifest["files"]} == RAW_FILES


def test_the_raw_files_that_are_here_are_the_listed_ones():
    files = manifest_files()
    for name in os.listdir(STUDY):
        if name.endswith(RAW_SUFFIXES):
            assert name in files, f"{name} is a raw file the manifest does not list"
    for path, entry in files.items():
        if os.path.exists(study_path(path)):                       # shipped, or fetched from the source commit
            with open(study_path(path), "rb") as f:
                assert sha256_and_size(f) == (entry["sha256"], entry["bytes"]), path
        else:
            assert not entry["in_repo"], f"{path} is listed as shipped but is missing"


def test_the_uncompressed_form_is_the_gunzip_of_the_shipped_file():
    """The S3-only ``.jsonl`` of the 100,000 run is the shipped file unpacked: same hash, same size."""
    entry = manifest_files()[STEM + "b100000.jsonl"]
    with gzip.open(study_path(ROWS_FILE), "rb") as f:
        assert sha256_and_size(f) == (entry["sha256"], entry["bytes"])


# ---- acx accepts the rows ------------------------------------------------------------------------------------------


def readme_snippet():
    """The one Python block of the README (its "Verify with acx" part)."""
    with open(README) as f:
        blocks = re.findall(r"```python\n(.*?)```", f.read(), re.S)
    assert len(blocks) == 1
    return blocks[0]


def test_the_readme_snippet_checks_the_sampled_certificates_and_the_control_paths(monkeypatch):
    """2,251 CoV certificates (the transform, then the path on the start it made) and 12 control paths replay."""
    monkeypatch.chdir(ROOT)
    namespace = {}
    exec(readme_snippet(), namespace)                               # noqa: S102
    assert namespace["checked"] == Counter(control=12, cov=2_251)


def certificate_steps(row):
    return ({"op": "define", "word": parse(row["z_word"])},
            {"op": "substitute", "rels": (tuple(row["r1_substituted"]), tuple(row["r2_substituted"]))},
            {"op": "eliminate", "gen": parse(row["iso_gen"])[0], "target": row["iso_index"] + 1,
             "expr": tuple(row["iso_expr"])})


@pytest.mark.slow
def test_every_transform_rebuilds_the_start_it_searched():
    """``apply_steps`` re-derives ``r1, r2`` from the original and the recorded transform, on all 114,042 CoV rows."""
    rebuilt = 0
    for row in read_rows():
        if not row["is_control"]:
            image = apply_steps(Presentation.parse(row["r1_orig"], row["r2_orig"]), certificate_steps(row))
            assert image.rels == Presentation.parse(row["r1"], row["r2"]).rels, (row["pres_id"], row["z_word"])
            rebuilt += 1
    assert rebuilt == 114_042


@pytest.mark.slow
def test_rows_searched_again_with_acx_reproduce_the_stored_search(scan):
    """100 random solved rows (the control and CoV starts) of at most 20,000 pops, searched with the row's own cap:
    ``acx.search`` pops as many states and finds as long a path as the sweep did."""
    cheap = [i for i, s in enumerate(scan.starts) if s.solved and s.nodes <= 20_000]
    chosen = set(random.Random(0).sample(cheap, 100))
    for i, row in enumerate(read_rows()):
        if i in chosen:
            config = SearchConfig(priority="length", backend="fast", cap=row["max_relator_length_cap"],
                                  budget=row["node_budget"], cyclic=row["cyclic_reduce"], capture_path=False)
            result = search(Presentation.parse(row["r1"], row["r2"]), config)
            assert (result.solved, result.pops, result.path_length) == (True, row["nodes_explored"], row["path_length"])


@pytest.mark.slow
@pytest.mark.parametrize("cap", [64, "none"])
def test_the_six_control_failures_stay_unsolved_at_any_cap(cap):
    """The control fails rows 634 to 639 at 100,000 pops and cap 24 (the table); cap 64 or none does not rescue them."""
    failed = [row for row in per_presentation() if row["control_solved"] == "0"]
    assert [int(row["pres_id"]) for row in failed] == list(range(634, 640))
    config = SearchConfig(priority="length", backend="fast", cap=cap, budget=100_000, capture_path=False)
    for row in failed:
        assert not search(Presentation.parse(row["r1_orig"], row["r2_orig"]), config).solved
