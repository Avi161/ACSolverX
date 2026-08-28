"""The AC19-leftover 1M notebooks and their runner, checked before Colab sees them.

A Colab run of this shape fails expensively: a wrong BRANCH clones the wrong code
and dies an hour in, a wrong row list runs the wrong experiment to completion, and
an OOM from oversubscribed workers loses the whole session. Everything here is
about catching those on a laptop instead.

Node budgets stay tiny on purpose -- a search at budget B is exactly the first B
pops of any longer search, so a bigger budget in a test buys a slower suite and
never different behaviour. The 1,000,000-node run is what Colab is for; nothing
in this file runs it.
"""
import json
import os
import subprocess
import sys

import pytest

from experiments.search import make_leftover_notebooks as mk
from experiments.search.greedy_baseline import greedy_search
from experiments.search.heuristics import greedy_search_h
from experiments.search.run_leftovers_1m import (
    ARMS, COMMON_DENOMINATOR_EXCLUDED, NODE_BUDGET, S20_MK2, SCREEN_DIR,
    classify, greedy_search_h_lean, load_rows, out_path, read_rows, report,
    resolve_arm, resolve_workers, run_arm, unsolved_at_100k,
)

ROOT = mk.ROOT
ARM_NAMES = ("greedy", "s20_mk2")


@pytest.fixture(scope="module")
def cells():
    """``{arm: [cell sources]}`` for the two committed notebooks."""
    out = {}
    for arm in ARM_NAMES:
        with open(mk.path_for(arm)) as fh:
            nb = json.load(fh)
        out[arm] = ["".join(c["source"]) for c in nb["cells"]]
    return out


# ------------------------------------------------------------------- notebooks
@pytest.mark.parametrize("arm", ARM_NAMES)
def test_it_is_the_four_cell_config_setup_run_report_pattern(cells, arm):
    src = cells[arm]
    assert len(src) == 4
    assert src[0].lstrip().startswith("# ===== AC19 LEFTOVERS @ 1M")
    assert "edit ONLY this cell" in src[0]
    for cell, head in zip(src[1:], ("SETUP", "RUN", "REPORT")):
        assert head in cell.splitlines()[0], head
    for i, cell in enumerate(src):
        compile(cell, f"{arm}-cell{i}", "exec")


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_committed_notebook_is_what_the_generator_writes(arm):
    """One template, two configs. Hand-editing one notebook is the drift this stops."""
    with open(mk.path_for(arm)) as fh:
        on_disk = fh.read()
    assert on_disk == mk.render(arm), (
        f"{os.path.relpath(mk.path_for(arm), ROOT)} is out of date -- regenerate "
        f"with `python3 -m experiments.search.make_leftover_notebooks`")


def test_the_two_notebooks_differ_only_in_their_config_cell(cells):
    a, b = cells["greedy"], cells["s20_mk2"]
    assert a[1:] == b[1:], "SETUP/RUN/REPORT have drifted apart between the arms"
    assert a[0] != b[0]


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_branch_matches_the_branch_this_code_is_on(cells, arm):
    """A mismatch clones the wrong code and fails on Colab, not here."""
    try:
        head = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pytest.skip("git unavailable")
    if head.returncode != 0:
        pytest.skip("not a git checkout")
    branch = head.stdout.strip()
    if branch == "HEAD":
        pytest.skip("detached HEAD (CI checkout of a merge ref); no branch to match")
    assert f'BRANCH   = "{branch}"' in cells[arm][0], \
        f"notebook clones a different branch than {branch!r}"


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_setup_carries_the_contracts_that_make_a_restart_continue(cells, arm):
    setup = cells[arm][1]
    assert "del sys.modules[_m]" in setup          # a pull is not a reload
    assert "invalidate_caches" in setup
    assert "reset --hard FETCH_HEAD" in setup
    assert "os.chdir(BASE)" in setup               # never nest the clone
    # numpy is on the Colab image; torch/jax are a different experiment entirely
    assert "pip -q install numba" in setup
    assert "pip -q install torch" not in setup
    assert "pip -q install numpy" not in setup


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_drive_output_lands_under_mydrive(cells, arm):
    """The mount root itself is not writable."""
    assert '"/content/drive/MyDrive/' in cells[arm][0]


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_config_asks_for_a_high_ram_cpu_runtime(cells, arm):
    cfg = cells[arm][0]
    assert "CPU, High-RAM" in cfg
    with open(mk.path_for(arm)) as fh:
        nb = json.load(fh)
    assert nb["metadata"].get("accelerator") != "GPU"


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_config_pins_this_experiments_budgets_and_arm(cells, arm):
    cfg = cells[arm][0]
    assert f'ARM = "{arm}"' in cfg
    assert "NODE_BUDGET = 1_000_000" in cfg
    assert "MAX_RELATOR_LENGTH = 48" in cfg
    assert "COMMON_DENOMINATOR = False" in cfg
    assert "SMOKE_RUN = True" in cfg, "a notebook must ship smoke-first"


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_config_names_its_row_list_and_that_lists_size(cells, arm):
    """A reader must be able to tell which experiment this is from cell 0 alone."""
    cfg = cells[arm][0]
    spec = ARMS[arm]
    assert spec["csv"] in cfg
    assert str(spec["n_rows"]) in cfg
    assert "100,000" in cfg or "100k" in cfg


# ------------------------------------------------------------------------ arms
def test_s20_mk2_is_l_plus_20s_plus_2mk_and_nothing_else():
    assert S20_MK2 == {"segments": [
        {"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}


def test_the_withdrawn_recommended_vector_is_refused_by_name():
    for bad in ("RECOMMENDED", "recommended", "s20", "mk20", "s20_mk20_l"):
        with pytest.raises(ValueError, match="withdrawn|not run by this experiment"):
            resolve_arm(bad)
    with pytest.raises(KeyError):
        resolve_arm("no_such_arm")


def test_nothing_this_experiment_ships_reaches_for_recommended(cells):
    """Importable from heuristics.py on a main-cut branch; the easiest wrong turn."""
    files = [mk.path_for(a) for a in ARM_NAMES] + [
        os.path.join(ROOT, "experiments", "search", "run_leftovers_1m.py"),
        os.path.join(ROOT, "experiments", "search", "make_leftover_notebooks.py"),
    ]
    for path in files:
        with open(path) as fh:
            text = fh.read()
        for line in text.splitlines():
            if "RECOMMENDED" not in line:
                continue
            # only ever as prose about the withdrawal, never as an import or a config
            assert not line.strip().startswith(("from ", "import ")), path
            assert "config=RECOMMENDED" not in line, path


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_each_arm_calls_a_shipped_search_entry_point(arm):
    """Nothing about the search is re-implemented here."""
    fn = ARMS[arm]["run"]
    st = fn("xyx", "yx", 200, 24)
    assert set(st) >= {"solved", "nodes_explored", "path_length"}
    assert isinstance(st["solved"], bool)
    assert 0 < st["nodes_explored"] <= 200


# ------------------------------------------------------------------- row lists
@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_row_list_is_the_arms_own_100k_unsolved_set(arm):
    rows, path = load_rows(arm)
    spec = ARMS[arm]
    assert len(rows) == spec["n_rows"]
    assert os.path.basename(path) == spec["csv"]
    names = [r["name"] for r in rows]
    assert len(set(names)) == len(names)
    assert all(r["r1"] and r["r2"] for r in rows)


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_shipped_csv_is_what_the_100k_jsonl_actually_left_unsolved(arm):
    """The CSVs are re-derived here, not trusted -- they are the whole experiment."""
    rows, _ = load_rows(arm)
    assert sorted(r["name"] for r in rows) == unsolved_at_100k(arm)


@pytest.mark.parametrize("arm,solved,total", [("greedy", 609, 831),
                                              ("s20_mk2", 220, 259)])
def test_the_100k_jsonl_is_the_run_the_docs_describe(arm, solved, total):
    path = os.path.join(ROOT, "results", "heuristic_search",
                        "hsearch_ac19_hard100k", ARMS[arm]["jsonl"])
    rows = read_rows(path)
    assert len(rows) == total
    assert sum(1 for r in rows if r["solved"]) == solved
    assert all(r["budget"] == 100_000 and r["mrl"] == 48 for r in rows)
    assert all(r["nodes_explored"] == 100_000 for r in rows if not r["solved"])


def test_the_39_are_a_strict_subset_of_the_222():
    """s20_mk2 recovers 182 of the greedy arm's failures and loses none."""
    g = {r["name"] for r in load_rows("greedy")[0]}
    s = {r["name"] for r in load_rows("s20_mk2")[0]}
    assert s < g
    assert len(g - s) == 183          # 182 recovered + the one off-denominator row


def test_the_common_denominator_drops_exactly_the_one_off_intersection_row():
    """221 and 222 are both right; which one is being quoted must be explicit."""
    full, _ = load_rows("greedy")
    common, _ = load_rows("greedy", common_denominator=True)
    dropped = {r["name"] for r in full} - {r["name"] for r in common}
    assert dropped == {"ac19_33435"} == set(COMMON_DENOMINATOR_EXCLUDED["greedy"])
    assert len(common) == ARMS["greedy"]["n_common"] == 221
    # the heuristic arm has no such row, so the flag is a no-op there
    assert (len(load_rows("s20_mk2", common_denominator=True)[0])
            == len(load_rows("s20_mk2")[0]) == 39)


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_csv_and_the_txt_name_list_agree(arm):
    """Both ship; a run that reads one and a reader that reads the other must agree."""
    rows, _ = load_rows(arm)
    txt = os.path.join(SCREEN_DIR, ARMS[arm]["csv"].replace(".csv", ".txt"))
    with open(txt) as fh:
        names = [ln.strip() for ln in fh if ln.strip()]
    assert names == [r["name"] for r in rows]


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_a_supplied_leftover_list_selects_rows_in_the_order_given(arm):
    all_rows, _ = load_rows(arm)
    want = [all_rows[4]["name"], all_rows[0]["name"]]
    rows, _ = load_rows(arm, ids=want)
    assert [r["name"] for r in rows] == want


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_a_leftover_id_outside_the_arms_own_rows_is_refused(arm):
    with pytest.raises(KeyError, match="must be a subset"):
        load_rows(arm, ids=["ac19_not_a_real_id"])


def test_a_row_from_the_other_arms_list_is_refused():
    """The 39 are inside the 222, but the 222 are not inside the 39."""
    only_greedy = ({r["name"] for r in load_rows("greedy")[0]}
                   - {r["name"] for r in load_rows("s20_mk2")[0]})
    with pytest.raises(KeyError, match="must be a subset"):
        load_rows("s20_mk2", ids=[sorted(only_greedy)[0]])


# -------------------------------------------------------------------- workers
def test_workers_are_bounded_by_free_ram_not_by_core_count():
    n, per = resolve_workers("s20_mk2", "auto", available_gb=200.0, cpu_count=64)
    assert n == int((200.0 - 2.0) // per)         # RAM, not the 64 cores
    n, _ = resolve_workers("s20_mk2", "auto", available_gb=5000.0, cpu_count=4)
    assert n == 4                                  # cores, once RAM is not binding


def test_one_worker_is_always_allowed_even_when_ram_looks_too_small():
    for arm in ARM_NAMES:
        n, _ = resolve_workers(arm, "auto", available_gb=1.0, cpu_count=8)
        assert n == 1


def test_the_heuristic_arm_reserves_more_than_the_greedy_one():
    """Same solver, different orderings -- and the orderings go different places.
    s20_mk2 prefers thicker blocks, so it queues longer relators and a wider
    frontier: measured ~46 GB at 1M against the greedy arm's ~16 GB."""
    _, g = resolve_workers("greedy", 1)
    _, s = resolve_workers("s20_mk2", 1)
    assert s > g
    assert 10.0 <= g <= 24.0
    assert 30.0 <= s <= 60.0


def test_the_heuristic_arm_gets_one_worker_on_a_51gb_high_ram_runtime():
    """The reservation is only useful if it actually bites on the target box."""
    assert resolve_workers("s20_mk2", "auto", available_gb=51.0, cpu_count=8)[0] == 1
    assert resolve_workers("greedy", "auto", available_gb=51.0, cpu_count=8)[0] == 3


def test_an_explicit_worker_count_is_taken_literally():
    n, _ = resolve_workers("greedy", 3, available_gb=1.0, cpu_count=1)
    assert n == 3


# ------------------------------------------------------- the prefix-property split
def _row(name, solved, nodes):
    return {"name": name, "solved": solved, "nodes_explored": nodes}


def test_classify_reads_the_smaller_budgets_off_the_same_run():
    """One search answers every budget below it, so the anytime curve is free."""
    rows = [
        _row("quick", True, 150_000),
        _row("slow", True, 700_000),
        _row("never", False, NODE_BUDGET),
    ]
    c = classify(rows)
    assert c["solved_at_1m"] == ["quick", "slow"]
    assert c["unsolved_at_1m"] == ["never"]
    assert c["anytime"] == {100_000: 0, 250_000: 1, 500_000: 1, 1_000_000: 2}
    assert c["n"] == 3


def test_a_row_solved_under_100k_is_flagged_as_impossible():
    """Every row of this experiment failed at 100,000; one that does not means the
    search being run is not the search that built the list."""
    c = classify([_row("cannot_happen", True, 40_000), _row("fine", True, 400_000)])
    assert c["solved_at_or_below_100k"] == ["cannot_happen"]
    assert classify([_row("fine", True, 400_000)])["solved_at_or_below_100k"] == []


def test_every_row_lands_in_exactly_one_bucket():
    rows = [_row(f"r{i}", i % 3 != 0, (i * 37_000) % 900_001) for i in range(60)]
    c = classify(rows)
    assert len(c["solved_at_1m"]) + len(c["unsolved_at_1m"]) == len(rows)


# ------------------------------------------------- the lean heuristic solver
#
# The s20_mk2 arm cannot run heuristics.greedy_search_h at 1M (it measured 1.64 GB
# by 12,288 pops), so it runs LeanHeuristicSolver instead. That is only legitimate
# if it is the SAME search -- which is what these check, pop for pop, rather than
# arguing it from the key encoding.
_EQUIV_BUDGET = 800


@pytest.mark.parametrize("r1,r2", [
    ("xyx", "yx"),
    ("XyyxYYY", "XyxxyXX"),
    ("xyxYXY", "xxxYYYY"),
    ("XyyxYYY", "XyxxYXX"),
])
def test_the_lean_heuristic_solver_pops_exactly_like_greedy_search_h(r1, r2):
    lean = greedy_search_h_lean(r1, r2, _EQUIV_BUDGET, 24, config=S20_MK2)
    heavy = greedy_search_h(r1, r2, _EQUIV_BUDGET, 24, config=S20_MK2)
    for k in ("solved", "nodes_explored", "path_length", "min_relator_length",
              "max_relator_length", "max_relator_length_expanded"):
        assert lean[k] == heavy[k], k


def test_the_lean_heuristic_solver_agrees_on_the_real_rows_too():
    """Same check, on presentations from the list this experiment actually runs."""
    for row in load_rows("s20_mk2")[0][:3]:
        lean = greedy_search_h_lean(row["r1"], row["r2"], _EQUIV_BUDGET, 48,
                                    config=S20_MK2)
        heavy = greedy_search_h(row["r1"], row["r2"], _EQUIV_BUDGET, 48,
                                config=S20_MK2)
        assert (lean["solved"], lean["nodes_explored"]) == \
               (heavy["solved"], heavy["nodes_explored"]), row["name"]


def test_the_lean_solver_leaves_nothing_in_the_pair_cache():
    """Every state is scored exactly once here, so an entry left behind is a leak
    that would grow to one per discovered state over a 1M-node search."""
    from experiments.search import heuristics as heur
    heur._STATE_CACHE.clear()
    greedy_search_h_lean("XyyxYYY", "XyxxyXX", 400, 24, config=S20_MK2)
    assert heur._STATE_CACHE == {}


def test_the_ordering_is_the_only_thing_that_differs_between_the_arms():
    """The baseline config through the lean heuristic solver IS the greedy arm."""
    for row in load_rows("greedy")[0][:2]:
        h = greedy_search_h_lean(row["r1"], row["r2"], _EQUIV_BUDGET, 48,
                                 config=None)
        g = greedy_search(row["r1"], row["r2"], _EQUIV_BUDGET, 48,
                          high_speedup=True)
        assert (h["solved"], h["nodes_explored"]) == \
               (g["solved"], g["nodes_explored"]), row["name"]


# ----------------------------------------------------------------- end to end
@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_pipeline_runs_writes_resumes_and_reports(arm, tmp_path, capsys):
    """The smoke path the notebook ships with, at a budget that measures nothing."""
    out_dir = str(tmp_path / arm)
    path = run_arm(arm, out_dir, budget=300, mrl=24, n_workers=1, limit=2,
                   log=lambda *a: None)
    rows = read_rows(path)
    assert len(rows) == 2
    assert {r["arm"] for r in rows} == {arm}
    assert all(r["budget"] == 300 and 0 < r["nodes_explored"] <= 300 for r in rows)

    # RESUME: the same call again must add nothing and re-run nothing
    before = open(path).read()
    run_arm(arm, out_dir, budget=300, mrl=24, n_workers=1, limit=2,
            log=lambda *a: None)
    assert open(path).read() == before

    c = report(arm, out_dir, budget=300, mrl=24, log=lambda *a: None)
    assert c["n"] == 2
    for stem, ids in (("solved_at_1m", c["solved_at_1m"]),
                      ("still_unsolved_1m", c["unsolved_at_1m"])):
        with open(os.path.join(out_dir, f"{stem}_{arm}.txt")) as fh:
            assert [ln.strip() for ln in fh if ln.strip()] == ids


def test_the_report_shouts_when_a_row_solves_under_100k(tmp_path, capsys):
    """A silent wrong-arm run is the expensive failure this catches."""
    out_dir = str(tmp_path)
    with open(out_path("s20_mk2", out_dir), "w") as fh:
        for i, r in enumerate(load_rows("s20_mk2")[0]):
            fh.write(json.dumps({"name": r["name"], "arm": "s20_mk2",
                                 "solved": True,
                                 "nodes_explored": 500 if i == 0 else 400_000}) + "\n")
    report("s20_mk2", out_dir, log=print)
    text = capsys.readouterr().out
    assert "which the 100k run says is impossible" in text
    assert "not the one that built this list" in text


def test_a_clean_full_run_reports_without_warnings(tmp_path, capsys):
    out_dir = str(tmp_path)
    rows = load_rows("s20_mk2")[0]
    with open(out_path("s20_mk2", out_dir), "w") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({
                "name": r["name"], "arm": "s20_mk2",
                "solved": i < 10, "nodes_explored": 300_000 if i < 10
                else NODE_BUDGET}) + "\n")
    c = report("s20_mk2", out_dir, log=print)
    text = capsys.readouterr().out
    assert len(c["solved_at_1m"]) == 10
    assert len(c["unsolved_at_1m"]) == len(rows) - 10
    assert "impossible" not in text and "PARTIAL" not in text
    assert f"{len(rows)}/{len(rows)}" in text


def test_report_before_any_run_says_so_instead_of_raising(tmp_path):
    assert report("greedy", str(tmp_path), log=lambda *a: None) is None
    assert read_rows(str(tmp_path / "nothing_here.jsonl")) == []


def test_report_reads_the_same_cap_the_run_wrote(tmp_path):
    """``mrl`` is in the jsonl filename; defaulting it in one and not the other
    made a finished run report as empty."""
    out_dir = str(tmp_path)
    run_arm("greedy", out_dir, budget=300, mrl=24, n_workers=1, limit=1,
            log=lambda *a: None)
    assert report("greedy", out_dir, budget=300, mrl=24,
                  log=lambda *a: None)["n"] == 1
    assert report("greedy", out_dir, budget=300, mrl=48,
                  log=lambda *a: None) is None


def test_a_partial_jsonl_reports_but_says_it_is_partial(tmp_path, capsys):
    out_dir = str(tmp_path)
    path = os.path.join(
        out_dir, f"leftovers_1m_greedy_b{NODE_BUDGET}_mrl48.jsonl")
    with open(path, "w") as fh:
        fh.write(json.dumps({"name": "ac19_420", "arm": "greedy", "solved": False,
                             "nodes_explored": NODE_BUDGET}) + "\n")
        fh.write("{truncated\n")                   # a half-written last line
    c = report("greedy", out_dir, log=print)
    text = capsys.readouterr().out
    assert c["n"] == 1                             # the broken line is not a row
    assert "PARTIAL" in text
    assert "impossible" not in text


# ------------------------------------------------- the notebook, actually run
#
# Everything above reads the notebook as text. This executes the real cell
# sources in order, in one namespace, the way Colab does -- which is the only
# thing that catches a CONFIG name the RUN cell does not define, an import SETUP
# purged, or a cell that only looks right. It runs the smoke path, so the search
# it does is two rows at a budget that measures nothing.


def _exec_notebook(cells, tmp_path):
    """CONFIG -> SETUP -> RUN -> REPORT, in one namespace, as Colab does."""
    ns = {"__name__": "__main__"}
    exec(cells[0], ns)
    ns["MOUNT_DRIVE"] = False
    # absolute, so the RUN cell's os.path.join keeps it out of the repo
    ns["LOCAL_OUT_DIR"] = str(tmp_path)
    exec(cells[1], ns)                       # SETUP: purges experiments.* here
    exec(cells[2], ns)                       # RUN: SMOKE_RUN is True as shipped
    exec(cells[3], ns)                       # REPORT
    return ns


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_notebook_runs_end_to_end_on_its_smoke_path(arm, cells, tmp_path):
    cwd = os.getcwd()
    saved = dict(sys.modules)
    try:
        ns = _exec_notebook(cells[arm], tmp_path)
    finally:
        os.chdir(cwd)
        sys.modules.clear()
        sys.modules.update(saved)

    assert ns["SMOKE_RUN"] is True, "the notebook must ship smoke-first"
    assert ns["budget"] == 2_000 and ns["limit"] == 2
    assert ns["OUT_DIR"].endswith("_smoke"), \
        "smoke rows must not land in the real run's directory"
    assert ns["MIRROR"] is None, "the smoke must not touch Drive"

    rows = read_rows(ns["out"])
    assert len(rows) == 2
    assert {r["arm"] for r in rows} == {arm}
    assert all(r["budget"] == 2_000 and 0 < r["nodes_explored"] <= 2_000
               for r in rows)
    # SETUP checked the row list against the 100k jsonl before searching anything
    assert len(ns["_rows"]) == ARMS[arm]["n_rows"]
    assert ns["c"]["n"] == 2
    # nothing in this list is solvable in 2,000 nodes -- they all survived 100,000
    assert ns["c"]["solved_at_1m"] == []
    assert ns["c"]["solved_at_or_below_100k"] == []
