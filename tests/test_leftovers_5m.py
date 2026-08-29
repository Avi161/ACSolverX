"""The 5M stage: stride chunks, the derived row lists, and the five notebooks.

Same posture as ``test_leftovers_1m``: everything a Colab failure would make
expensive is checked on a laptop first, and no test runs a large search — the
budgets here never exceed 2,000 nodes.
"""
import json
import time
import os
import re
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
from experiments.search.run_leftovers_1m import MAX_RELATOR_LENGTH as FLOOR_CAP
from experiments.search.run_leftovers_5m import MRL_5M
from experiments.search.greedy_compact import est_states

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
    with open(out_path_5m("s20_mk2", out_dir, 1, 1, mrl=FLOOR_CAP), "w") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"name": r["name"], "arm": "s20_mk2",
                                 "solved": True,
                                 "nodes_explored": 500_000 if i == 0
                                 else 3_000_000}) + "\n")
    report_5m("s20_mk2", out_dir, chunks=1, mrl=FLOOR_CAP, log=print)
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
    default_n = (int(est_states(NODE_BUDGET_5M) * _RESERVE_SLACK)
                 + 4 * (MRL_5M + 1) ** 2)
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
    assert f"MAX_RELATOR_LENGTH = {MRL_5M}" in cfg
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


# ---------------------------------------------------------------------------
# The remote path: one rented high-RAM box instead of five crashy Colab shards.
# At 5M a row reserves ~34.7 GB on ONE core, so a 51 GB runtime runs one row at
# a time no matter how many cores it has. Buying RAM buys workers.
# ---------------------------------------------------------------------------
REMOTE_SH = os.path.join(ROOT, "experiments", "search", "run_remote.sh")


def _remote(*args, **env):
    e = dict(os.environ, SRC=ROOT, **env)
    return subprocess.run(["bash", REMOTE_SH, *args], capture_output=True,
                          text=True, env=e, timeout=300)


def test_the_remote_script_is_valid_shell():
    p = subprocess.run(["bash", "-n", REMOTE_SH], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr


def test_the_run_detaches_so_an_ssh_drop_cannot_kill_the_campaign():
    """A rented box WILL drop the connection; the job must outlive the shell."""
    src = open(REMOTE_SH).read()
    assert "setsid nohup" in src
    assert "< /dev/null" in src


def test_plan_prices_an_offer_before_you_rent_it():
    """The point of a spot market is choosing the box BEFORE paying for it."""
    out = _remote("plan", PLAN_GB="512", PLAN_CORES="64").stdout
    assert "offer" in out and "64 cores, 512 GB RAM" in out
    want, _ = resolve_workers("greedy", "auto", 512, 64, 5_000_000, MRL_5M,
                              track_path=TRACK_PATH)
    assert f"{want} workers" in out, out


def test_more_ram_buys_more_workers_and_less_wall_clock():
    def hours(gb, cores):
        out = _remote("plan", PLAN_GB=str(gb), PLAN_CORES=str(cores)).stdout
        line = [l for l in out.splitlines() if "total wall clock" in l][0]
        return float(line.split(":")[1].strip().split()[0])

    small, big = hours(64, 8), hours(512, 64)
    assert big < small / 5, f"512 GB bought no speedup: {small} -> {big}"


def test_plan_refuses_a_box_with_no_engine(monkeypatch):
    """A silent Python fallback at 5M is a hundreds-of-GB code path."""
    assert 'raise SystemExit("STOP: hcompact missing' in open(REMOTE_SH).read()


def test_plan_says_when_the_box_is_too_small_for_a_full_reserve():
    tiny = _remote("plan", PLAN_GB="16", PLAN_CORES="4").stdout
    big = _remote("plan", PLAN_GB="512", PLAN_CORES="64").stdout
    assert "CLIPPED" in tiny, tiny
    assert "(full)" in big, big


@pytest.mark.parametrize("sub", ["plan", "smoke", "run", "tail", "report"])
def test_every_documented_subcommand_exists(sub):
    src = open(REMOTE_SH).read()
    assert f"{sub})" in src.split("case ")[-1]


# --- the cap-in-the-filename bug, closed at the CLI ------------------------
def test_one_mrl_flag_feeds_both_the_run_and_the_report(tmp_path, capsys):
    """RUN at cap 64 + REPORT at the default 48 read different files, so a
    finished run reported 'no rows yet'. This campaign hit that twice."""
    from experiments.search.run_leftovers_5m import main

    out = tmp_path / "o"
    main(["--arm", "s20_mk2", "--budget", "2000", "--mrl", "40",
          "--limit", "2", "--workers", "1", "--out-dir", str(out)])
    txt = capsys.readouterr().out
    # the report must find what the run wrote -- not "0/14"
    assert "mrl40" in txt, txt
    assert "rows complete        : 2/" in txt, txt
    assert len(list(out.glob("*_mrl40.jsonl"))) == 1, list(out.iterdir())


def test_a_spot_preemption_resumes_without_a_human():
    """A Spot VM WILL be preempted inside a 14 h run. With termination-action
    STOP the disk survives, so booting again must restart the campaign, and
    RESUME then skips every row already on disk."""
    src = open(REMOTE_SH).read()
    assert "install-service" in src
    assert "WantedBy=multi-user.target" in src      # starts on boot
    assert "Restart=on-failure" in src
    assert "systemctl enable --now ac19.service" in src


def test_run_and_the_service_execute_the_very_same_job_script():
    """Two copies of the command line would drift; a Spot restart would then
    run something other than what `run` ran."""
    src = open(REMOTE_SH).read()
    assert src.count("write_job") == 4       # def + run + service + job_only
    # the long-run command line exists once, inside write_job. (`smoke` has its
    # own short foreground invocation -- that one is meant to differ.)
    assert src.count("--budget $BUDGET") == 1


# ---------------------------------------------------------------------------
# Dynamic worker allocation: cores + RAM, re-decided before every launch.
# ---------------------------------------------------------------------------
from experiments.search.run_leftovers_5m import (          # noqa: E402
    RamGovernor, run_rows_dynamic, _peak_rss_gb, _rss_gb)


def _gov(**kw):
    kw.setdefault("budget", 5_000_000)
    kw.setdefault("mrl", 48)
    return RamGovernor(**kw)


def test_a_bigger_box_gets_more_workers_with_no_config_change():
    small = _gov(cpu_cap=8).capacity([], free_gb=64)
    big = _gov(cpu_cap=64).capacity([], free_gb=512)
    assert big > small * 5, (small, big)


def test_workers_never_exceed_the_core_count():
    """Each search is single-threaded -- there is no prange in the engine --
    so more workers than cores buys nothing and costs context switches."""
    assert _gov(cpu_cap=4).capacity([], free_gb=4096) == 4


def test_an_explicit_worker_count_is_a_ceiling_not_a_target():
    assert _gov(cpu_cap=64, max_workers=3).capacity([], free_gb=512) == 3


def test_one_row_always_runs_even_when_the_estimate_says_no_room():
    """The estimate is linear and worst-case; a real row is usually far
    cheaper. Stalling forever on an estimate is worse than trying."""
    assert _gov(cpu_cap=8).capacity([], free_gb=1.0) == 1


def test_memory_a_live_row_has_not_claimed_yet_is_still_reserved():
    """The overcommit trap: a row that just started has touched almost nothing,
    so free RAM looks enormous. Admitting on that number invites a crowd that
    then grows into each other."""
    g = _gov(cpu_cap=64)
    fresh = g.capacity([0.1, 0.1, 0.1], free_gb=200)     # 3 rows barely started
    grown = g.capacity([g.worst] * 3, free_gb=200)       # 3 rows fully grown
    assert fresh < grown, (fresh, grown)


def test_it_learns_from_what_rows_actually_cost_and_widens():
    """Most rows solve long before the budget and never approach the reserve."""
    g = _gov(cpu_cap=64)
    before = g.capacity([], free_gb=512)
    for _ in range(5):
        g.note(3.0)                       # measured peaks, far under worst case
    after = g.capacity([], free_gb=512)
    assert g.predict_gb() < g.worst
    assert after > before * 2, (before, after)


def test_a_prediction_never_exceeds_the_worst_case():
    """A row that has not solved yet can still grow into the full reserve."""
    g = _gov(cpu_cap=8)
    for _ in range(5):
        g.note(10_000.0)
    assert g.predict_gb() == g.worst


def test_one_cheap_sample_does_not_widen_the_gate():
    g = _gov(cpu_cap=64)
    g.note(0.5)
    assert g.predict_gb() == g.worst, "widened on a single observation"


def test_rows_report_what_they_actually_peaked_at(tmp_path):
    """Without a measurement the governor can only ever use the worst case."""
    out = run_arm_5m("s20_mk2", str(tmp_path), chunks=1, chunk_index=1,
                     budget=2_000, mrl=48, limit=2, n_workers=1,
                     log=lambda *a: None)
    rows = read_rows(out)
    assert rows and all(r.get("peak_rss_gb", 0) > 0 for r in rows), rows


def test_the_dynamic_path_really_runs_rows_at_the_same_time(monkeypatch):
    """Concurrency observed directly -- wall clock alone cannot tell overlap
    from fast rows, so this records each row's live interval and asserts they
    genuinely coincide."""
    import experiments.search.run_leftovers_5m as m

    spans, real = [], m._RowProc

    class Spy(real):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.span = [time.time(), None]
            spans.append(self.span)

        def _settle(self):
            self.span[1] = time.time()
            return super()._settle()

    monkeypatch.setattr(m, "_RowProc", Spy)
    rows = [{"name": f"r{i}", "r1": "XYXYXY", "r2": "YXYXYX"} for i in range(4)]
    g = _gov(budget=200_000, cpu_cap=4)
    recs = list(m.run_rows_dynamic("greedy", rows, 200_000, 48, 3600, None,
                                   None, None, g, log=lambda *a: None))
    assert len(recs) == 4
    assert g.capacity([], free_gb=64) > 1, "governor never allowed a second row"
    peak = max(sum(a <= t < (b or a) for a, b in spans)
               for t, _ in spans)
    assert peak > 1, f"rows never overlapped: {spans}"


def test_a_crashing_row_cannot_take_down_the_rows_beside_it():
    """The old fixed pool had no per-row isolation -- on a wide box one OOM
    took every row in flight with it."""
    rows = [{"name": "bad", "r1": "zzZZ", "r2": "qq"},
            {"name": "ok1", "r1": "XYXYXY", "r2": "YXYXYX"},
            {"name": "ok2", "r1": "XYXYXY", "r2": "YXYXYX"}]
    g = _gov(budget=20_000, cpu_cap=4)
    recs = {r["name"]: r for r in
            run_rows_dynamic("greedy", rows, 20_000, 48, 3600, None, None,
                             None, g, log=lambda *a: None)}
    assert set(recs) == {"bad", "ok1", "ok2"}
    assert recs["bad"].get("error")
    assert not recs["ok1"].get("error") and not recs["ok2"].get("error")


def test_rss_probes_return_real_numbers_on_this_machine():
    assert _peak_rss_gb() > 0
    assert _rss_gb() > 0
    assert _rss_gb(pid=999999999) is None


def test_a_row_already_big_tightens_the_gate_for_the_next_one():
    """Three cheap early rows must not widen admission right before the
    expensive ones arrive -- every row on these lists failed at 1M."""
    g = _gov(cpu_cap=64)
    for _ in range(5):
        g.note(3.0)                       # early rows solved cheap
    wide = g.capacity([3.0], free_gb=512)
    tight = g.capacity([30.0], free_gb=512)   # one in flight is already huge
    assert tight < wide, (wide, tight)


def test_the_1m_floor_keys_off_the_cap_that_built_the_list_not_the_default():
    """The floor says 'no row on these lists solves under 1M'. That is a claim
    about the cap-48 search that BUILT them. When the 5M default moved to 64,
    a check written as `mrl == MAX_RELATOR_LENGTH` would have inverted: silent
    at 48 where it must shout, shouting at 64 where an early solve is the
    interesting result."""
    assert FLOOR_CAP == 48, "the 1M baseline cap moved; the floor claim moves too"
    assert MRL_5M == 64
    src = open(os.path.join(ROOT, "experiments", "search",
                            "run_leftovers_5m.py")).read()
    assert "if mrl == MAX_RELATOR_LENGTH:" in src, "floor check re-keyed to the default"


def test_the_wider_cap_is_what_the_5m_stage_actually_runs():
    """One constant, everywhere the stage takes a default."""
    import inspect
    # classify_5m works on already-loaded rows, so it has no cap to default
    from experiments.search.run_leftovers_5m import (
        run_arm_5m, report_5m as r5, plan_memory as pm)
    for fn in (run_arm_5m, r5, pm):
        assert inspect.signature(fn).parameters["mrl"].default == MRL_5M, fn


# ---------------------------------------------------------------------------
# Solution paths. `path_length` alone is not the result -- the move sequence is
# the certificate, and it cannot be recovered after the fact: the arena is
# overwritten, so a finished run without it can only be re-run.
# ---------------------------------------------------------------------------
from experiments.search.run_leftovers_5m import TRACK_PATH          # noqa: E402

# Two cases. The oracle is pure Python with a full parent dict, so the
# field-for-field gate uses a pair that solves in a handful of nodes; the
# engine-only checks use a real 1M-list row, where hcompact is fast enough.
_EASY = ("XYXYy", "YXYXX", 4_000, 3)
_REAL = ("YYXYYXXXyX", "YYXYXXXYYXXXX", 200_000, 58)


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_the_engine_path_matches_the_python_oracle_field_for_field():
    """The reused fast path must produce the SAME certificate as the reference
    solver, not merely a plausible one."""
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from experiments.heuristic_search.core.hsolve import greedy_search_h
    from experiments.search.run_leftovers_1m import S20_MK2

    r1, r2, b, plen = _EASY
    fast = greedy_search_hcompact(r1, r2, b, max_relator_length=48,
                                  config=S20_MK2, track_path=True)
    ref = greedy_search_h(r1, r2, b, 48, config=S20_MK2, keep_path=True)
    assert fast["solved"] and ref["solved"]
    for k in ("nodes_explored", "path_length", "min_relator_length",
              "max_relator_length", "max_relator_length_expanded",
              "path", "path_moves"):
        assert fast[k] == ref[k], k
    assert fast["path_length"] == plen
    assert len(fast["path"]) == plen + 1


@pytest.fixture(scope="module")
def solved_real():
    """The one expensive search in this file, run once and shared. Every row on
    these lists needs >100k nodes by construction -- they are the hard ones."""
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from experiments.search.run_leftovers_1m import S20_MK2
    r1, r2, b, _ = _REAL
    return r1, r2, greedy_search_hcompact(r1, r2, b, max_relator_length=48,
                                          config=S20_MK2, track_path=True)


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_the_recorded_moves_actually_replay_into_the_recorded_path(solved_real):
    """A path nobody can replay is not a certificate."""
    from experiments.search.greedy_baseline import moves_to_states, str_to_move

    r1, r2, got = solved_real
    replay = moves_to_states(r1, r2, [str_to_move(m) for m in got["path_moves"]])
    assert [list(x) for x in replay] == [list(x) for x in got["path"]]
    assert sorted(len(w) for w in got["path"][-1]) == [1, 1], "not the trivial pair"


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_tracking_does_not_perturb_the_search():
    """Same nodes, same answer -- the certificate is a side channel, not a
    different search. Otherwise every earlier wave's numbers stop splicing."""
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from experiments.search.run_leftovers_1m import S20_MK2

    r1, r2, _, _ = _REAL
    kw = dict(max_relator_length=48, config=S20_MK2)
    # 30k nodes: does not solve, but min/max/expanded are order-sensitive, so
    # any divergence in the frontier shows up here -- cheaply.
    on = greedy_search_hcompact(r1, r2, 30_000, track_path=True, **kw)
    off = greedy_search_hcompact(r1, r2, 30_000, track_path=False, **kw)
    for k in ("nodes_explored", "min_relator_length", "max_relator_length",
              "max_relator_length_expanded", "solved"):
        assert on[k] == off[k], k
    assert off["path"] == [] and off["path_moves"] == []


@pytest.mark.skipif(not HAVE_HCOMPACT, reason="engine not on this branch")
def test_not_tracking_allocates_nothing_for_paths():
    from experiments.heuristic_search.core.hcompact import HCompactSolver
    lean = HCompactSolver("XYX", "YX", max_nodes=2_000, max_relator_length=32)
    full = HCompactSolver("XYX", "YX", max_nodes=2_000, max_relator_length=32,
                          track_path=True)
    assert lean.parent.size == 1 and lean.pmove.size == 4
    assert full.parent.size == full.states_cap
    assert full.bytes_reserved() > lean.bytes_reserved()


def test_the_sizing_counts_the_path_arrays():
    """If est_gb ignored them the governor would admit rows that do not fit."""
    plain = est_gb(5_000_000, 64)
    with_path = est_gb(5_000_000, 64, track_path=True)
    assert with_path > plain
    n = int(est_states(5_000_000) * 1.5) + 4 * 65 ** 2
    assert abs((with_path - plain) - n * 8 / 2 ** 30) < 0.01


def test_the_campaign_captures_paths_by_default():
    assert TRACK_PATH is True


def test_a_finished_row_carries_its_path_into_the_jsonl(tmp_path):
    """The record is the deliverable; a path that never reaches disk is lost."""
    out = run_arm_5m("s20_mk2", str(tmp_path), chunks=1, chunk_index=1,
                     budget=2_000, mrl=48, limit=2, n_workers=1,
                     log=lambda *a: None)
    rows = read_rows(out)
    assert rows
    for r in rows:
        assert "path" in r and "path_moves" in r
        if r["solved"]:
            assert len(r["path"]) == r["path_length"] + 1
            assert len(r["path_moves"]) == r["path_length"]


def test_the_job_runs_every_row_not_just_the_first_chunk():
    """Without explicit chunk flags run_leftovers_5m falls back to the arm's
    default chunk count (4 for greedy) and runs 22 of 88 rows, then prints
    CAMPAIGN COMPLETE. The 4-way split is for four Colabs, not one box."""
    src = open(REMOTE_SH).read()
    assert "--chunks 1 --chunk-index 1" in src
    # and the report must read the same file the run writes
    assert "chunks=1, chunk_index=1" in src


def test_single_box_chunking_really_is_every_row():
    from experiments.search.run_leftovers_5m import load_rows_5m
    for arm, n in (("greedy", 88), ("s20_mk2", 14)):
        rows = load_rows_5m(arm)[0]
        assert len(stride_chunk(rows, 1, 1)) == n


# ---------------------------------------------------------------------------
# The generated job script. Checking the WRAPPER's syntax is not enough: the
# job is written by an unquoted heredoc, so anything executable in the template
# runs at generation time and its output lands in the job as bare shell. That
# shipped once -- a backtick around a word ran the `report` function and spliced
# its multi-line output in, killing the job on line 8 under set -e, which
# systemd then crash-looped.
# ---------------------------------------------------------------------------
def test_the_generated_job_is_valid_shell(tmp_path):
    out = tmp_path / "j"
    r = _remote("job", OUT=str(out))
    assert r.returncode == 0, r.stderr
    job = out / "_job.sh"
    assert job.exists(), r.stdout
    chk = subprocess.run(["bash", "-n", str(job)], capture_output=True, text=True)
    assert chk.returncode == 0, f"{chk.stderr}\n--- job ---\n{job.read_text()}"


def test_the_generated_job_has_no_spliced_command_output(tmp_path):
    """Every line of the template's commentary must still be commentary."""
    out = tmp_path / "j"
    _remote("job", OUT=str(out))
    body = (out / "_job.sh").read_text().splitlines()
    for i, line in enumerate(body[1:], start=2):     # line 1 is the shebang
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        assert not t.startswith("no rows yet"), f"line {i} is spliced output: {t}"
    assert "run_leftovers_5m --arm" in "\n".join(body)
    assert "--chunks 1 --chunk-index 1" in "\n".join(body)


def test_the_job_heredoc_executes_nothing_at_generation_time():
    src = open(REMOTE_SH).read()
    body = src.split('cat > "$OUT/_job.sh" <<JOB', 1)[1].split("\nJOB\n", 1)[0]
    assert "`" not in body, "a backtick in the job heredoc runs at generation time"
    # $( ) is only allowed escaped, so it lands in the job rather than running
    for hit in re.finditer(r"(?<!\\)\$\(", body):
        raise AssertionError(f"unescaped $( in the job heredoc at {hit.start()}")


def test_plan_sizes_the_way_the_run_actually_sizes():
    """plan told the operator 41.6 GB while the run header said 45.1 -- same
    worker count by luck, but a plan that disagrees with the run is a lie."""
    out = _remote("plan", PLAN_GB="250", PLAN_CORES="32").stdout
    want = est_gb(5_000_000, MRL_5M, track_path=TRACK_PATH)
    assert f"{want:.1f} GB per row" in out, out
    assert "paths captured" in out
