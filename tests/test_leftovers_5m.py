"""The 5M stage: stride chunks, the derived row lists, and the five notebooks.

Same posture as ``test_leftovers_1m``: everything a Colab failure would make
expensive is checked on a laptop first, and no test runs a large search — the
budgets here never exceed 2,000 nodes.
"""
import json
import os
import subprocess
import sys

import pytest

from experiments.search import make_leftover_5m_notebooks as mk5
from experiments.search.run_leftovers_1m import ARMS, HAVE_HCOMPACT, est_gb
from experiments.search.run_leftovers_5m import (
    FLOOR_5M, NODE_BUDGET_5M, SPEC_5M, classify_5m, load_rows_5m, out_path_5m,
    report_5m, run_arm_5m, stride_chunk, unsolved_at_1m,
)
from experiments.search.run_leftovers_1m import read_rows, resolve_workers

ROOT = mk5.ROOT
ARM_NAMES = ("greedy", "s20_mk2")


# ------------------------------------------------------------------- row lists
@pytest.mark.parametrize("arm,n", [("greedy", 88), ("s20_mk2", 14)])
def test_the_row_list_is_the_arms_own_1m_unsolved_set(arm, n):
    rows, path = load_rows_5m(arm)
    assert len(rows) == n == SPEC_5M[arm]["n_rows"]
    names = [r["name"] for r in rows]
    assert len(set(names)) == len(names)
    assert all(r["r1"] and r["r2"] for r in rows)
    assert os.path.basename(path) == SPEC_5M[arm]["csv"]


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_shipped_csv_is_what_the_1m_jsonl_actually_left_unsolved(arm):
    """Derived, not trusted — the same discipline as every earlier wave."""
    rows, _ = load_rows_5m(arm)
    assert sorted(r["name"] for r in rows) == unsolved_at_1m(arm)


def test_the_14_are_a_subset_of_the_88():
    g = {r["name"] for r in load_rows_5m("greedy")[0]}
    s = {r["name"] for r in load_rows_5m("s20_mk2")[0]}
    assert s < g


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_the_csv_and_the_txt_name_list_agree(arm):
    from experiments.search.run_leftovers_1m import SCREEN_DIR
    rows, _ = load_rows_5m(arm)
    txt = os.path.join(SCREEN_DIR, SPEC_5M[arm]["csv"].replace(".csv", ".txt"))
    with open(txt) as fh:
        assert [ln.strip() for ln in fh if ln.strip()] == [r["name"] for r in rows]


# --------------------------------------------------------------- stride chunks
def test_stride_chunks_partition_the_list():
    """Disjoint, union = everything, and interleaved — not contiguous blocks."""
    rows, _ = load_rows_5m("greedy")
    chunks = [stride_chunk(rows, 4, k) for k in (1, 2, 3, 4)]
    assert [len(c) for c in chunks] == [22, 22, 22, 22]
    names = [r["name"] for c in chunks for r in c]
    assert sorted(names) == sorted(r["name"] for r in rows)
    assert len(set(names)) == 88
    # interleaved: chunk 1 holds rows 0, 4, 8, ... of the file order
    assert [r["name"] for r in chunks[0]] == [r["name"] for r in rows[0::4]]


def test_a_single_chunk_is_the_whole_list():
    rows, _ = load_rows_5m("s20_mk2")
    assert stride_chunk(rows, 1, 1) == rows


def test_bad_chunk_arguments_are_refused():
    rows, _ = load_rows_5m("s20_mk2")
    with pytest.raises(ValueError):
        stride_chunk(rows, 4, 0)
    with pytest.raises(ValueError):
        stride_chunk(rows, 4, 5)
    with pytest.raises(ValueError):
        stride_chunk(rows, 0, 1)


def test_chunk_tag_lands_in_the_filename_so_chunks_cannot_collide():
    a = out_path_5m("greedy", "/x", 4, 1)
    b = out_path_5m("greedy", "/x", 4, 2)
    assert a != b and "_c1of4_" in a and "_c2of4_" in b
    assert "_c" not in os.path.basename(out_path_5m("s20_mk2", "/x", 1, 1))


# --------------------------------------------------------------------- sizing
def test_five_million_resolves_one_worker_on_a_51gb_runtime():
    """The reason for four Colab files instead of four pool workers."""
    if not HAVE_HCOMPACT:
        pytest.skip("engine not on this branch")
    assert 25.0 <= est_gb(NODE_BUDGET_5M, 48) <= 45.0
    for arm in ARM_NAMES:
        n, _ = resolve_workers(arm, "auto", available_gb=51.0, cpu_count=8,
                               budget=NODE_BUDGET_5M)
        assert n == 1, arm


# ------------------------------------------------------------------- classify
def _row(name, solved, nodes):
    return {"name": name, "solved": solved, "nodes_explored": nodes}


def test_classify_floor_is_one_million_now():
    """Every input row failed at 1M, so a solve at or below 1M is impossible."""
    c = classify_5m([_row("fine", True, 3_000_000),
                     _row("cannot_happen", True, 900_000),
                     _row("never", False, NODE_BUDGET_5M)])
    assert c["solved_at_5m"] == ["fine", "cannot_happen"]
    assert c["solved_at_or_below_1m"] == ["cannot_happen"]
    assert c["unsolved_at_5m"] == ["never"]
    assert c["anytime"] == {1_000_000: 1, 2_000_000: 1, 5_000_000: 2}
    assert FLOOR_5M == 1_000_000


# ----------------------------------------------------------------- end to end
def test_the_pipeline_runs_chunked_resumes_and_merges(tmp_path, capsys):
    out_dir = str(tmp_path)
    for k in (1, 2):
        run_arm_5m("greedy", out_dir, chunks=4, chunk_index=k, budget=300,
                   mrl=24, n_workers=1, limit=2, log=lambda *a: None)
    # two chunks, two rows each, in chunk-tagged files
    for k in (1, 2):
        assert len(read_rows(out_path_5m("greedy", out_dir, 4, k, 300, 24))) == 2
    # resume adds nothing
    before = open(out_path_5m("greedy", out_dir, 4, 1, 300, 24)).read()
    run_arm_5m("greedy", out_dir, chunks=4, chunk_index=1, budget=300,
               mrl=24, n_workers=1, limit=2, log=lambda *a: None)
    assert open(out_path_5m("greedy", out_dir, 4, 1, 300, 24)).read() == before
    # the merged report sees both chunks and says which chunks are silent
    c = report_5m("greedy", out_dir, chunks=4, budget=300, mrl=24, log=print)
    text = capsys.readouterr().out
    assert c["n"] == 4
    assert "all chunks merged" in text
    assert "[3, 4]" in text          # chunks with no rows yet
    # a single-chunk report labels itself as progress, not a result
    report_5m("greedy", out_dir, chunks=4, chunk_index=1, budget=300, mrl=24,
              log=print)
    assert "progress, not a result" in capsys.readouterr().out


def test_the_report_shouts_on_a_sub_1m_solve(tmp_path, capsys):
    out_dir = str(tmp_path)
    rows = stride_chunk(load_rows_5m("s20_mk2")[0], 1, 1)
    with open(out_path_5m("s20_mk2", out_dir, 1, 1), "w") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"name": r["name"], "arm": "s20_mk2",
                                 "solved": True,
                                 "nodes_explored": 500_000 if i == 0
                                 else 3_000_000}) + "\n")
    report_5m("s20_mk2", out_dir, chunks=1, log=print)
    text = capsys.readouterr().out
    assert "which the 1M run says is impossible" in text


def test_the_floor_alarm_stands_down_at_a_different_cap(tmp_path, capsys):
    """At cap 64 the 1M floor (established at cap 48) does not apply: an early
    solve is the interesting outcome, not evidence of the wrong search."""
    out_dir = str(tmp_path)
    rows = load_rows_5m("s20_mk2")[0][:3]
    with open(out_path_5m("s20_mk2", out_dir, 1, 1, mrl=64), "w") as fh:
        for r in rows:
            fh.write(json.dumps({"name": r["name"], "arm": "s20_mk2",
                                 "solved": True,
                                 "nodes_explored": 400_000}) + "\n")
    report_5m("s20_mk2", out_dir, chunks=1, mrl=64, log=print)
    text = capsys.readouterr().out
    assert "impossible" not in text
    assert "Legitimate at cap 64" in text
    assert "wider corridor" in text


def test_a_complete_merged_run_writes_the_id_lists(tmp_path):
    out_dir = str(tmp_path)
    rows = load_rows_5m("s20_mk2")[0]
    with open(out_path_5m("s20_mk2", out_dir, 1, 1), "w") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"name": r["name"], "arm": "s20_mk2",
                                 "solved": i < 5,
                                 "nodes_explored": 3_000_000 if i < 5
                                 else NODE_BUDGET_5M}) + "\n")
    c = report_5m("s20_mk2", out_dir, chunks=1, log=lambda *a: None)
    assert len(c["solved_at_5m"]) == 5
    for stem, ids in (("solved_at_5m", c["solved_at_5m"]),
                      ("still_unsolved_5m", c["unsolved_at_5m"])):
        with open(os.path.join(out_dir, f"{stem}_s20_mk2.txt")) as fh:
            assert sorted(ln.strip() for ln in fh if ln.strip()) == sorted(ids)


# ------------------------------------------------------ Edge Compact crash guards
from experiments.search.run_leftovers_5m import (
    _done_ok, absorb_shard_rows, plan_memory)


def test_a_crashing_row_becomes_an_error_row_and_the_run_continues(tmp_path):
    """The fix for the crashed 5M sessions: a row that dies takes itself out,
    never the session. An invalid relator makes the child raise; the parent
    records it and moves on to the healthy row."""
    csv = tmp_path / "rows.csv"
    csv.write_text("name,r1,r2,min_relator_length\n"
                   "bad_row,zzZZ,qq,4\n"
                   "ac19_12445,YXXYxxyxx,YXyxYXXXyxx,17\n")
    out_dir = str(tmp_path)
    run_arm_5m("s20_mk2", out_dir, chunks=1, chunk_index=1, budget=300, mrl=24,
               n_workers=1, csv_path=str(csv), log=lambda *a: None)
    rows = {r["name"]: r for r in read_rows(out_path_5m("s20_mk2", out_dir, 1, 1,
                                                        300, 24))}
    assert set(rows) == {"bad_row", "ac19_12445"}
    assert rows["bad_row"].get("error"), "the crash must be recorded, not fatal"
    assert not rows["ac19_12445"].get("error"), "the healthy row must still run"


def test_error_rows_do_not_satisfy_resume(tmp_path):
    p = str(tmp_path / "x.jsonl")
    with open(p, "w") as fh:
        fh.write(json.dumps({"name": "a", "solved": False,
                             "error": "worker died"}) + "\n")
        fh.write(json.dumps({"name": "b", "solved": False,
                             "nodes_explored": 300}) + "\n")
    assert _done_ok(p) == {"b"}, "a crashed row must be retried, a finished one not"


def test_the_memory_guard_stops_a_row_before_the_oom_killer(tmp_path):
    """reserve_states far beyond the address-space cap: the child must fail with
    a clean MemoryError row while the parent (this test) stays alive."""
    if not HAVE_HCOMPACT:
        pytest.skip("engine not on this branch")
    out_dir = str(tmp_path)
    run_arm_5m("s20_mk2", out_dir, chunks=1, chunk_index=1, budget=300, mrl=24,
               n_workers=1, limit=1, mem_limit_bytes=6 * 2 ** 30,
               reserve_states=2_000_000_000, log=lambda *a: None)
    rows = read_rows(out_path_5m("s20_mk2", out_dir, 1, 1, 300, 24))
    assert len(rows) == 1
    assert rows[0].get("error") and "Memory" in rows[0]["error"]


def test_the_row_timeout_kills_the_row_not_the_session(tmp_path):
    out_dir = str(tmp_path)
    run_arm_5m("s20_mk2", out_dir, chunks=1, chunk_index=1, budget=500_000,
               mrl=48, n_workers=1, limit=1, row_timeout_secs=1.0,
               log=lambda *a: None)
    rows = read_rows(out_path_5m("s20_mk2", out_dir, 1, 1, 500_000, 48))
    assert len(rows) == 1
    assert rows[0].get("error") and "timeout" in rows[0]["error"]


def test_classify_dedupes_retried_error_rows_and_reports_them():
    c = classify_5m([
        {"name": "a", "solved": False, "error": "died"},
        {"name": "a", "solved": True, "nodes_explored": 3_000_000},  # the retry
        {"name": "b", "solved": False, "error": "died"},
        {"name": "b", "solved": False, "error": "died again"},
    ])
    assert c["n"] == 2
    assert c["solved_at_5m"] == ["a"]
    assert c["errored"] == ["b"]


def test_plan_memory_clips_the_reservation_to_the_machine():
    if not HAVE_HCOMPACT:
        pytest.skip("engine not on this branch")
    from experiments.search.greedy_compact import _RESERVE_SLACK, est_states
    default_n = int(est_states(NODE_BUDGET_5M) * _RESERVE_SLACK) + 4 * 49 ** 2
    # a big machine keeps the engine default
    _, big = plan_memory(available_gb=200.0, log=lambda *a: None)
    assert big == default_n
    # a small one gets a clipped reservation, never zero
    _, small = plan_memory(available_gb=20.0, log=lambda *a: None)
    assert 1024 <= small < default_n


def test_absorb_skips_error_rows(tmp_path):
    out = str(tmp_path / "combined.jsonl")
    shard = str(tmp_path / "c1.jsonl")
    with open(shard, "w") as fh:
        fh.write(json.dumps({"name": "ac19_1007", "solved": False,
                             "error": "worker died"}) + "\n")
        fh.write(json.dumps({"name": "ac19_13290", "solved": True,
                             "nodes_explored": 3_000_000}) + "\n")
    valid = {r["name"] for r in load_rows_5m("greedy")[0]}
    assert absorb_shard_rows(out, [shard], valid, log=lambda *a: None) == 1
    assert [r["name"] for r in read_rows(out)] == ["ac19_13290"]


# ------------------------------------------------------------------ notebooks
@pytest.fixture(scope="module")
def cells():
    out = {}
    for stem, arm, chunks, idx in mk5.VARIANTS:
        with open(mk5.path_for(stem)) as fh:
            nb = json.load(fh)
        out[stem] = ["".join(c["source"]) for c in nb["cells"]]
    return out


def test_the_five_shard_notebooks_are_the_job_and_no_combined_one_exists():
    assert len(mk5.VARIANTS) == 5
    assert [(c, i) for _, a, c, i in mk5.VARIANTS if a == "greedy"] == \
        [(4, 1), (4, 2), (4, 3), (4, 4)]
    listed = sorted(f for f in os.listdir(mk5.NB_DIR) if f.endswith(".ipynb"))
    assert listed == [f"ac19_leftovers_5m_greedy_c{k}of4.ipynb" for k in
                      (1, 2, 3, 4)] + ["ac19_leftovers_5m_s20_mk2.ipynb"], \
        "four greedy shards + s20_mk2; a combined greedy notebook is not the job"


@pytest.mark.parametrize("stem,arm,chunks,idx", mk5.VARIANTS)
def test_the_committed_notebook_is_what_the_generator_writes(stem, arm, chunks, idx):
    with open(mk5.path_for(stem)) as fh:
        assert fh.read() == mk5.render(stem, arm, chunks, idx)


@pytest.mark.parametrize("stem,arm,chunks,idx", mk5.VARIANTS)
def test_it_is_the_config_setup_smoke_main_pattern(cells, stem, arm, chunks, idx):
    src = cells[stem]
    assert len(src) == 4
    assert "CONFIG" in src[0].splitlines()[0]
    for cell, head in zip(src[1:], ("SETUP", "SMOKE", "MAIN")):
        assert head in cell.splitlines()[0], head
    for i, cell in enumerate(src):
        compile(cell, f"{stem}-cell{i}", "exec")


@pytest.mark.parametrize("stem,arm,chunks,idx", mk5.VARIANTS)
def test_config_pins_arm_chunk_budget_and_knobs(cells, stem, arm, chunks, idx):
    cfg = cells[stem][0]
    assert f'ARM         = "{arm}"' in cfg
    assert f"CHUNKS      = {chunks}" in cfg
    assert f"CHUNK_INDEX = {idx}" in cfg
    assert "NODE_BUDGET = 5_000_000" in cfg
    assert "MAX_RELATOR_LENGTH = 48" in cfg
    assert "ROW_TIMEOUT_SECS = None" in cfg
    assert SPEC_5M[arm]["csv"] in cfg
    # machine-neutral: no SKU baked in
    assert "e2-" not in cfg and "c4d-" not in cfg


def test_setup_carries_the_engine_knobs_and_bans_the_silent_fallback(cells):
    setup = cells[mk5.VARIANTS[0][0]][1]
    assert 'ENGINE       = "hcompact"' in setup
    assert "HIGH_SPEEDUP = True" in setup
    assert 'assert ENGINE == "hcompact", "ENGINE=hcompact required for HIGH_SPEEDUP"' in setup
    assert "assert HAVE_HCOMPACT" in setup
    # the arm must actually CALL the engine -- importable is not enough
    assert "greedy_search_hcompact" in setup and "silent fallback" in setup
    assert "_find_root" in setup and "git clone" in setup
    assert "drive.mount" in setup


def test_the_five_notebooks_share_everything_but_config(cells):
    stems = [v[0] for v in mk5.VARIANTS]
    assert len({tuple(cells[s][1:]) for s in stems}) == 1
    assert len({cells[s][0] for s in stems}) == 5


def test_each_notebook_gets_its_own_drive_dir(cells):
    dirs = {ln for stem, *_ in mk5.VARIANTS
            for ln in cells[stem][0].splitlines()
            if ln.startswith("DRIVE_OUT_DIR")}
    assert len(dirs) == 5


def test_the_branch_matches_the_branch_this_code_is_on(cells):
    try:
        head = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pytest.skip("git unavailable")
    if head.returncode != 0 or head.stdout.strip() == "HEAD":
        pytest.skip("no branch name to match")
    for stem, *_ in mk5.VARIANTS:
        assert f'BRANCH   = "{head.stdout.strip()}"' in cells[stem][0]


def _exec_cells(cells_list, ns_extra, upto):
    ns = {"__name__": "__main__"}
    for i, src in enumerate(cells_list[:upto]):
        exec(src, ns)
        if i == 0:
            ns.update(ns_extra)
    return ns


def _isolated(fn):
    cwd = os.getcwd()
    saved = {k: v for k, v in sys.modules.items()
             if k == "experiments" or k.startswith("experiments.")}
    try:
        return fn()
    finally:
        os.chdir(cwd)
        for k in [k for k in sys.modules
                  if k == "experiments" or k.startswith("experiments.")]:
            del sys.modules[k]
        sys.modules.update(saved)


def test_the_notebook_runs_end_to_end_smoke_then_main(cells, tmp_path):
    stem = "ac19_leftovers_5m_greedy_c3of4"
    ns = _isolated(lambda: _exec_cells(
        cells[stem],
        {"MOUNT_DRIVE": False, "LOCAL_OUT_DIR": str(tmp_path / "real"),
         "NODE_BUDGET": 2_500, "MAIN_LIMIT": 2, "MAX_RELATOR_LENGTH": 24},
        upto=4))
    assert ns["_SMOKE_OK"] is True
    rows = read_rows(ns["out"])
    assert len(rows) == 2
    assert "_c3of4_" in ns["out"] and "_mrl24" in ns["out"]
    assert all(not r.get("error") for r in rows)
    assert ns["c"] is not None and ns["c"]["n"] == 2


def test_main_refuses_to_start_without_the_smoke(cells, tmp_path):
    stem = "ac19_leftovers_5m_greedy_c1of4"

    def run():
        ns = _exec_cells(cells[stem],
                         {"MOUNT_DRIVE": False,
                          "LOCAL_OUT_DIR": str(tmp_path / "x")}, upto=2)
        exec(cells[stem][3], ns)              # MAIN without SMOKE
        return ns

    with pytest.raises((NameError, AssertionError)):
        _isolated(run)


def test_run_main_false_is_smoke_only(cells, tmp_path, capsys):
    stem = "ac19_leftovers_5m_s20_mk2"
    ns = _isolated(lambda: _exec_cells(
        cells[stem],
        {"MOUNT_DRIVE": False, "LOCAL_OUT_DIR": str(tmp_path / "real"),
         "RUN_MAIN": False, "MAX_RELATOR_LENGTH": 24},
        upto=4))
    assert ns["_SMOKE_OK"] is True
    assert "the long job was not started" in capsys.readouterr().out
    assert not os.path.exists(str(tmp_path / "real"))
