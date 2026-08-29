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


# ------------------------------------------------------------- shard absorption
from experiments.search.run_leftovers_5m import absorb_shard_rows


def test_absorb_folds_shard_rows_in_once_and_skips_foreign_names(tmp_path):
    """The combined notebook replaces the four shards; rows a shard already paid
    for must survive, appear once, and nothing outside the row list sneaks in."""
    out = str(tmp_path / "combined.jsonl")
    s1, s2 = str(tmp_path / "c1.jsonl"), str(tmp_path / "c2.jsonl")
    with open(s1, "w") as fh:
        fh.write(json.dumps({"name": "ac19_1007", "solved": False,
                             "nodes_explored": 5_000_000}) + "\n")
        fh.write(json.dumps({"name": "smoke_junk", "solved": False,
                             "nodes_explored": 2_000}) + "\n")
    with open(s2, "w") as fh:                     # duplicate of s1's row
        fh.write(json.dumps({"name": "ac19_1007", "solved": False,
                             "nodes_explored": 5_000_000}) + "\n")
        fh.write(json.dumps({"name": "ac19_13290", "solved": True,
                             "nodes_explored": 3_000_000}) + "\n")
    valid = {r["name"] for r in load_rows_5m("greedy")[0]}
    added = absorb_shard_rows(out, [s1, s2], valid, log=lambda *a: None)
    assert added == 2
    names = [r["name"] for r in read_rows(out)]
    assert names == ["ac19_1007", "ac19_13290"]
    # idempotent: a second absorb adds nothing
    assert absorb_shard_rows(out, [s1, s2], valid, log=lambda *a: None) == 0
    assert len(read_rows(out)) == 2


def test_absorbed_rows_are_skipped_by_the_run(tmp_path):
    out_dir = str(tmp_path)
    out = out_path_5m("greedy", out_dir, 1, 1, 300, 24)
    shard = str(tmp_path / "old_c1of4.jsonl")
    rows = load_rows_5m("greedy")[0]
    with open(shard, "w") as fh:
        fh.write(json.dumps({"name": rows[0]["name"], "arm": "greedy",
                             "solved": False, "nodes_explored": 300}) + "\n")
    absorb_shard_rows(out, [shard], {r["name"] for r in rows},
                      log=lambda *a: None)
    run_arm_5m("greedy", out_dir, chunks=1, chunk_index=1, budget=300, mrl=24,
               n_workers=1, limit=2, log=lambda *a: None)
    got = read_rows(out)
    assert len(got) == 2                          # 1 absorbed + 1 newly run
    assert [r["name"] for r in got][0] == rows[0]["name"]


# ------------------------------------------------------------------ notebooks
@pytest.fixture(scope="module")
def cells():
    out = {}
    for stem, arm in mk5.VARIANTS:
        with open(mk5.path_for(stem)) as fh:
            nb = json.load(fh)
        out[stem] = ["".join(c["source"]) for c in nb["cells"]]
    return out


def test_there_are_exactly_two_notebooks_one_per_cheap_cpu():
    assert mk5.VARIANTS == (("ac19_leftovers_5m_greedy", "greedy"),
                            ("ac19_leftovers_5m_s20_mk2", "s20_mk2"))
    listed = sorted(f for f in os.listdir(mk5.NB_DIR) if f.endswith(".ipynb"))
    assert listed == ["ac19_leftovers_5m_greedy.ipynb",
                      "ac19_leftovers_5m_s20_mk2.ipynb"], \
        "shard notebooks must be gone; the combined pair replaces them"


@pytest.mark.parametrize("stem,arm", mk5.VARIANTS)
def test_the_committed_notebook_is_what_the_generator_writes(stem, arm):
    with open(mk5.path_for(stem)) as fh:
        assert fh.read() == mk5.render(stem, arm)


@pytest.mark.parametrize("stem,arm", mk5.VARIANTS)
def test_it_is_the_config_setup_smoke_main_pattern(cells, stem, arm):
    src = cells[stem]
    assert len(src) == 4
    assert "CONFIG" in src[0].splitlines()[0]
    for cell, head in zip(src[1:], ("SETUP", "SMOKE", "MAIN")):
        assert head in cell.splitlines()[0], head
    for i, cell in enumerate(src):
        compile(cell, f"{stem}-cell{i}", "exec")


@pytest.mark.parametrize("stem,arm", mk5.VARIANTS)
def test_config_pins_the_combined_run(cells, stem, arm):
    cfg = cells[stem][0]
    assert f'ARM         = "{arm}"' in cfg
    assert "CHUNKS      = 1" in cfg
    assert "NODE_BUDGET = 5_000_000" in cfg
    assert "MAX_RELATOR_LENGTH = 48" in cfg
    assert "RUN_MAIN  = True" in cfg
    assert SPEC_5M[arm]["csv"] in cfg


def test_setup_carries_the_engine_and_high_speedup_knobs(cells):
    """The knobs name the fast path; a reader (or an agent) greps for them."""
    setup = cells[mk5.VARIANTS[0][0]][1]
    assert 'ENGINE       = "hcompact"' in setup
    assert "HIGH_SPEEDUP = True" in setup
    assert 'assert ENGINE == "hcompact", "ENGINE=hcompact required for HIGH_SPEEDUP"' in setup
    assert "assert HAVE_HCOMPACT" in setup
    assert "resolve_workers" in setup and "N_WORKERS" in setup
    # runs on a plain GCE VM too: the clone is not gated on Colab
    assert "_find_root" in setup and "git clone" in setup
    assert "del sys.modules[_m]" in setup


def test_the_two_notebooks_share_everything_but_config(cells):
    stems = [v[0] for v in mk5.VARIANTS]
    assert len({tuple(cells[s][1:]) for s in stems}) == 1
    assert len({cells[s][0] for s in stems}) == 2


def test_each_notebook_gets_its_own_drive_dir(cells):
    dirs = {ln for stem, _ in mk5.VARIANTS
            for ln in cells[stem][0].splitlines()
            if ln.startswith("DRIVE_OUT_DIR")}
    assert len(dirs) == 2


def test_the_branch_matches_the_branch_this_code_is_on(cells):
    try:
        head = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pytest.skip("git unavailable")
    if head.returncode != 0 or head.stdout.strip() == "HEAD":
        pytest.skip("no branch name to match")
    for stem, _ in mk5.VARIANTS:
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
    """CONFIG -> SETUP -> SMOKE -> MAIN in one namespace, the way a runtime
    does -- MAIN shrunk to 2 rows at a tiny budget via the CONFIG knobs."""
    stem = "ac19_leftovers_5m_greedy"
    ns = _isolated(lambda: _exec_cells(
        cells[stem],
        {"MOUNT_DRIVE": False, "LOCAL_OUT_DIR": str(tmp_path / "real"),
         "NODE_BUDGET": 2_500, "MAIN_LIMIT": 2, "MAX_RELATOR_LENGTH": 24},
        upto=4))
    assert ns["_SMOKE_OK"] is True
    rows = read_rows(ns["out"])
    assert len(rows) == 2
    assert all(r["budget"] == 2_500 and r["max_relator_length"] == 24
               for r in rows)
    assert ns["c"] is not None and ns["c"]["n"] == 2


def test_main_refuses_to_start_without_the_smoke(cells, tmp_path):
    """The gate itself: skipping SMOKE (as a crashed or cleared cell would)
    must stop MAIN before any long work."""
    stem = "ac19_leftovers_5m_greedy"

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
