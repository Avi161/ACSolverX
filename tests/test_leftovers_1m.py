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
    ARMS, COMMON_DENOMINATOR_EXCLUDED, HAVE_HCOMPACT, NODE_BUDGET, S20_MK2,
    SCREEN_DIR, _in_search_heartbeat, classify, est_gb, greedy_search_h_lean,
    load_rows, out_path, read_rows, report, resolve_arm, resolve_workers,
    run_arm, unsolved_at_100k,
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


def test_the_reservation_is_the_engines_own_arena_formula():
    """Sizing the pool and sizing the arena must be the SAME number, not two
    guesses that drift. With the arena engine, `est_gb` is its reservation."""
    if not HAVE_HCOMPACT:
        pytest.skip("packed-arena engine not on this branch")
    from experiments.search.greedy_compact import (
        _RESERVE_SLACK, est_states, row_width)
    n = max(1024, int(est_states(NODE_BUDGET) * _RESERVE_SLACK)) + 4 * 49 ** 2
    assert est_gb(NODE_BUDGET, 48) == pytest.approx(
        n * (row_width(48) + 31) / 2 ** 30 + 0.6)
    assert 6.0 <= est_gb(NODE_BUDGET, 48) <= 10.0


def test_the_reservation_scales_with_the_budget():
    """A 2,000-node smoke must not reserve the 1M footprint and drop to 1 worker."""
    assert est_gb(2_000, 48) < est_gb(NODE_BUDGET, 48)
    assert resolve_workers("greedy", "auto", available_gb=51.0, cpu_count=8,
                           budget=2_000)[0] == 8


def test_both_arms_fit_several_workers_on_a_51gb_high_ram_runtime():
    """The whole point of the arena engine: 1 worker became 6."""
    for arm in ARM_NAMES:
        n, gb = resolve_workers(arm, "auto", available_gb=51.0, cpu_count=8)
        assert n == max(1, int((51.0 - 2.0) // gb))
        if HAVE_HCOMPACT:
            assert n >= 5, (arm, n, gb)


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
    saved = {k: v for k, v in sys.modules.items()
             if k == "experiments" or k.startswith("experiments.")}
    try:
        ns = _exec_notebook(cells[arm], tmp_path)
    finally:
        os.chdir(cwd)
        # Undo ONLY what the notebook's SETUP purges. A blanket
        # `sys.modules.clear()` also drops stdlib entries, and re-importing
        # `multiprocessing.connection` afterwards yields a second module object
        # whose `rebuild_connection` is not the one ForkingPickler expects --
        # which broke a later pool test, not this one. Test isolation that
        # reaches past its own subject is not isolation.
        for k in [k for k in sys.modules
                  if k == "experiments" or k.startswith("experiments.")]:
            del sys.modules[k]
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


# ------------------------------------------------------ progress from inside a row
#
# A row at this budget is 25-80 minutes. Without a callback reaching into the
# search, the run prints nothing for that whole time and a working session is
# indistinguishable from a hung one. These pin that it reports, that it is
# rate-limited by wall clock rather than by node count, and -- the part that
# actually broke -- that the arms forward it to the solver at all.


def test_the_heartbeat_reports_progress_rate_and_eta():
    lines = []
    hb = _in_search_heartbeat("ac19_420", 1_000_000, every=0.0, log=lines.append)
    hb(250_000)
    assert len(lines) == 1
    assert "ac19_420" in lines[0]
    assert "250,000/1,000,000" in lines[0] and "25.0%" in lines[0]
    assert "n/s" in lines[0] and "min left" in lines[0]


def test_the_heartbeat_is_gated_by_wall_clock_not_by_node_count():
    """It fires every 1024 pops -- roughly once a second -- so without the gate
    a 1M-node row would print about a thousand lines."""
    lines = []
    hb = _in_search_heartbeat("r", 1_000_000, every=3600.0, log=lines.append)
    for n in range(1024, 200_000, 1024):
        hb(n)
    assert lines == []


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_each_arm_forwards_the_progress_callback_to_its_solver(arm):
    """The bug this pins: the arm wrappers dropped `progress`, so the callback
    existed and was never called."""
    seen = []
    ARMS[arm]["run"]("XyyxYYY", "XyxxyXX", 3_000, 24, progress=seen.append)
    assert seen, "solver never called progress"
    assert all(n % 1024 == 0 for n in seen)


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_a_real_run_prints_progress_from_inside_the_row(arm, tmp_path, capsys):
    """End to end: a single row long enough to cross the gate must report while
    it is still running, not only when it finishes."""
    run_arm(arm, str(tmp_path), budget=5_000, mrl=24, n_workers=1, limit=1,
            heartbeat_secs=0.0, log=lambda *a: None)
    out = capsys.readouterr().out
    assert "nodes (" in out and "n/s" in out, out[-400:]


# ------------------------------------------------- resuming onto a wiped runtime
#
# Colab recycles /content -- the clone and the results directory with it -- while
# Drive survives. RESUME reads the LOCAL jsonl, so without seeding it back the
# session re-runs every row it already paid for.


def test_resume_seeds_the_local_jsonl_back_from_the_drive_mirror(tmp_path, capsys):
    local, drive = tmp_path / "local", tmp_path / "drive"
    local.mkdir(), drive.mkdir()
    run_arm("greedy", str(local), budget=300, mrl=24, n_workers=1, limit=2,
            mirror_dir=str(drive), log=lambda *a: None)
    out = out_path("greedy", str(local), 300, 24)
    mirrored = os.path.join(str(drive), os.path.basename(out))
    assert len(read_rows(mirrored)) == 2

    os.remove(out)                      # the VM recycle
    run_arm("greedy", str(local), budget=300, mrl=24, n_workers=1, limit=2,
            mirror_dir=str(drive), log=print)
    assert "seeded 2 row(s) back from the Drive mirror" in capsys.readouterr().out
    assert len(read_rows(out)) == 2, "should have resumed, not re-run"


def test_a_local_jsonl_ahead_of_the_mirror_is_not_clobbered(tmp_path):
    """The mirror is written from local, so local is normally the newer of the
    two; seeding must never walk it backwards."""
    local, drive = tmp_path / "local", tmp_path / "drive"
    local.mkdir(), drive.mkdir()
    run_arm("greedy", str(local), budget=300, mrl=24, n_workers=1, limit=1,
            mirror_dir=str(drive), log=lambda *a: None)
    out = out_path("greedy", str(local), 300, 24)
    run_arm("greedy", str(local), budget=300, mrl=24, n_workers=1, limit=3,
            mirror_dir=None, log=lambda *a: None)          # local pulls ahead
    assert len(read_rows(out)) == 3
    run_arm("greedy", str(local), budget=300, mrl=24, n_workers=1, limit=3,
            mirror_dir=str(drive), log=lambda *a: None)
    assert len(read_rows(out)) == 3


def test_a_missing_or_unreadable_mirror_does_not_stop_the_run(tmp_path):
    run_arm("greedy", str(tmp_path), budget=300, mrl=24, n_workers=1, limit=1,
            mirror_dir=str(tmp_path / "never" / "mounted"), log=lambda *a: None)
    assert len(read_rows(out_path("greedy", str(tmp_path), 300, 24))) == 1


def test_progress_from_pool_workers_reaches_the_parent(tmp_path):
    """The bug the single-worker arm hid.

    A spawn worker is a fresh interpreter whose ``sys.stdout`` is the real fd 1 --
    under Colab that is the kernel log, not the cell output -- so a worker's own
    print is invisible in the notebook. The single-worker arm ran in the parent
    and reported fine; the three-worker arm went silent. Workers must hand their
    lines back over the queue and let the PARENT print them.
    """
    lines = []
    run_arm("greedy", str(tmp_path), budget=6_000, mrl=24, n_workers=2, limit=2,
            heartbeat_secs=0.0, log=lines.append)
    beats = [ln for ln in lines if "nodes (" in ln and "n/s" in ln]
    assert beats, f"no in-search progress reached the parent: {lines}"
    assert len(read_rows(out_path("greedy", str(tmp_path), 6_000, 24))) == 2


def test_the_worker_log_falls_back_to_print_in_the_parent(capsys):
    """`_job` runs in-process on the single-worker path, where there is no queue."""
    from experiments.search import run_leftovers_1m as r
    assert r._WORKER_LOG_Q is None
    r._worker_log("hello from the parent")
    assert "hello from the parent" in capsys.readouterr().out


# --------------------------------------------------- the packed-arena engine
#
# Swapping the engine under a run that has already produced published numbers is
# only legitimate if it is the SAME search. hcompact argues that from its layout;
# these check it against the Python solvers on the rows this experiment actually
# runs, which is the claim that matters here.


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_arena_engine_agrees_with_the_python_solver_on_real_rows(arm):
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from experiments.heuristic_search.core.hsolve import LENGTH_ONLY
    cfg = LENGTH_ONLY if arm == "greedy" else S20_MK2
    for row in load_rows(arm)[0][:3]:
        fast = greedy_search_hcompact(row["r1"], row["r2"], 800,
                                      max_relator_length=48, config=cfg)
        slow = greedy_search_h_lean(row["r1"], row["r2"], 800, 48, config=cfg)
        for k in ("solved", "nodes_explored", "path_length",
                  "min_relator_length", "max_relator_length_expanded"):
            assert fast[k] == slow[k], (arm, row["name"], k)


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_the_greedy_arm_still_reproduces_the_length_baseline_exactly():
    """The control gate: whatever engine runs it, the greedy arm IS the baseline."""
    from experiments.search.greedy_baseline import greedy_search
    for row in load_rows("greedy")[0][:3]:
        got = ARMS["greedy"]["run"](row["r1"], row["r2"], 800, 48)
        want = greedy_search(row["r1"], row["r2"], 800, 48, high_speedup=True)
        assert (got["solved"], got["nodes_explored"]) == \
               (want["solved"], want["nodes_explored"]), row["name"]


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_the_engine_is_what_the_arms_actually_call():
    """A fallback that silently stays selected would quietly cost 10x."""
    import experiments.search.run_leftovers_1m as r
    calls = []
    real = r.greedy_search_hcompact

    def spy(*a, **kw):
        calls.append(kw.get("config"))
        return real(*a, **kw)

    r.greedy_search_hcompact = spy
    try:
        ARMS["greedy"]["run"]("xyx", "yx", 50, 24)
        ARMS["s20_mk2"]["run"]("xyx", "yx", 50, 24)
    finally:
        r.greedy_search_hcompact = real
    assert len(calls) == 2
    assert calls[1] == S20_MK2
    assert calls[0]["segments"][0]["w"] == {"L": 1.0}


def test_the_shipped_docs_describe_the_engine_that_actually_runs():
    """Docs drifting behind a swapped engine is how someone plans capacity for 1
    worker and 50 min/row when the run does 6 and 20. The engine port shipped
    once with this file and the README still saying hcompact was absent."""
    readme = open(os.path.join(mk.NB_DIR, "README.md")).read()
    runner = open(os.path.join(ROOT, "experiments", "search",
                               "run_leftovers_1m.py")).read()
    docstring = runner[:runner.index('"""', 3)]
    for text, what in ((readme, "README"), (docstring, "runner docstring")):
        if HAVE_HCOMPACT:
            assert "hcompact" in text, what
            assert "not on this branch" not in text, (
                f"{what} still says the engine is absent while the code uses it")
        # the withdrawn vector may be named as prose, never recommended
        assert "config=RECOMMENDED" not in text, what


def test_the_readme_quotes_the_engines_real_measured_cost():
    """The numbers a reader sizes a runtime from must be the engine's, not the
    superseded Python solver's."""
    if not HAVE_HCOMPACT:
        pytest.skip("engine not on this branch")
    readme = open(os.path.join(mk.NB_DIR, "README.md")).read()
    assert "802 n/s" in readme and "7.6 GB" in readme
    # est_gb is the source of truth; the README must not contradict it
    assert f"{est_gb(NODE_BUDGET, 48):.1f} GB" in readme
    # the worker count in the cost table must be the one resolve_workers gives
    # for the runtime the table names, not a number left over from a prior engine
    workers = resolve_workers("s20_mk2", "auto", available_gb=51.0, cpu_count=8)[0]
    assert f"**{workers}** |" in readme, (
        f"README cost table does not show {workers} workers on 51 GB")
