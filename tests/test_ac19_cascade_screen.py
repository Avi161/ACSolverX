"""The screen-wide cascade pass, and the certification split it turns on.

The one thing this file exists to hold down: a path that changes basis is not
an AC certificate. ``cascade_heuristics``' ``s40_gen`` arm pushes Nielsen
images into the same heap as AC substitutions, so it can and does "solve" rows
that are not AC-solved. Everything else here is bookkeeping around that line.
"""
import csv
import json
import os

import pytest

from experiments.equivalence_classes.lib.words import canon_pair
from experiments.search import run_ac19_cascade_screen as screen
from experiments.search.cascade_heuristics import search as cascade
from experiments.search.hybrid_10m import PREFIX_BUDGET, SEARCH_CAP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S20_10K = os.path.join(ROOT, "results", "heuristic_search",
                       "ac19_autmin_screen", "unsolved_10k_s20_mk2.csv")

# Two rows off the shipped 10k s20_mk2 leftover list, both unsolved by
# s20_mk2 at 10,000 nodes. The first is recognized by ``bs_collapse`` and
# yields a substitution-only certificate; the second is only reachable
# through a basis change.
AC_ROW = {"name": "ac19_10379", "r1": "YXXyx", "r2": "YYYYYXyyyxyxxx"}


def _rows():
    with open(S20_10K) as fh:
        return list(csv.DictReader(fh))


def _replay(row):
    """The certificate itself, re-derived: the run record only fingerprints it."""
    got = cascade((row["r1"], row["r2"]), budget=PREFIX_BUDGET, cap=SEARCH_CAP,
                  starter_budget=500, rewrite_budget=1000, intermediate_cap=None)
    assert got["solved"]
    return got["states"], got["steps"]


def test_the_two_pinned_rows_are_really_on_the_shipped_leftover_list():
    by_name = {r["name"]: r for r in _rows()}
    got = by_name[AC_ROW["name"]]
    assert (got["r1"], got["r2"]) == (AC_ROW["r1"], AC_ROW["r2"])
    assert int(got["nodes_explored"]) == 10_000


def test_a_substitution_only_certificate_replays_to_a_terminal_pair():
    record = screen.run_row(dict(AC_ROW, n_members=1))
    assert record["solved"] is True
    assert record["certificate"] == "ac"
    assert record["winner"] == "rewrite"
    assert record["aut_assisted"] is False
    assert record["certificate_rejected"] is None
    assert "error" not in record
    assert record["nodes_explored"] <= PREFIX_BUDGET
    assert record["certificate_moves"] > 0
    assert len(record["certificate_sha256"]) == 64
    # the record is a fingerprint, so re-derive the path to check the claim
    states, steps = _replay(AC_ROW)
    assert all(s["kind"] == "substitution" for s in steps)
    ok, why = screen.certify_path(AC_ROW["r1"], AC_ROW["r2"], states, steps)
    assert (ok, why) == (True, "")
    assert screen._fingerprint(steps) == record["certificate_sha256"]


def test_certify_refuses_a_path_that_changes_basis():
    states, steps = _replay(AC_ROW)
    poisoned = list(steps)
    poisoned[0] = {"kind": "automorphism", "images": {"x": "xy", "y": "y"}}
    ok, why = screen.certify_path(AC_ROW["r1"], AC_ROW["r2"], states, poisoned)
    assert ok is False and "basis change" in why


def test_certify_refuses_a_path_that_stops_short_of_terminal():
    states, steps = _replay(AC_ROW)
    ok, why = screen.certify_path(AC_ROW["r1"], AC_ROW["r2"],
                                  states[:-1], steps[:-1])
    assert ok is False and "terminal" in why


def test_certify_refuses_a_path_whose_replay_diverges():
    states, steps = _replay(AC_ROW)
    states = [list(s) for s in states]
    states[1] = ["x", "y"]
    ok, why = screen.certify_path(AC_ROW["r1"], AC_ROW["r2"], states, steps)
    assert ok is False and "differs" in why


def test_certify_refuses_a_path_that_does_not_start_at_the_canonical_input():
    states, steps = _replay(AC_ROW)
    assert list(states[0]) == list(canon_pair(AC_ROW["r1"], AC_ROW["r2"]))
    ok, why = screen.certify_path("xyX", "yyx", states, steps)
    assert ok is False and "canonical input" in why


def test_an_aut_assisted_solve_is_recorded_but_never_counted_as_solved():
    """Whatever ``s40_gen`` wins, it does not win an AC certificate."""
    found = None
    for row in _rows():
        result = cascade((row["r1"], row["r2"]), budget=PREFIX_BUDGET,
                         cap=SEARCH_CAP, starter_budget=500,
                         rewrite_budget=1000, intermediate_cap=None)
        if result["solved"] and result["winner"] == "s40_gen":
            found = row
            break
    assert found is not None, "the shipped list must contain an s40_gen solve"
    record = screen.run_row(found)
    assert record["aut_assisted"] is True
    assert record["solved"] is False
    assert record["certificate"] == "aut_assisted"
    assert record["certificate_sha256"] is None
    assert record["certificate_moves"] is None
    assert any(s["kind"] == "automorphism"
               for s in cascade((found["r1"], found["r2"]), budget=PREFIX_BUDGET,
                                cap=SEARCH_CAP, starter_budget=500,
                                rewrite_budget=1000,
                                intermediate_cap=None)["steps"])


def test_the_report_splits_ac_from_aut_assisted(tmp_path):
    path = screen.out_path(str(tmp_path), 1, 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        for rec in (
            {"name": "a", "solved": True, "aut_assisted": False,
             "winner": "rewrite", "seconds": 0.2},
            {"name": "b", "solved": False, "aut_assisted": True,
             "winner": "s40_gen", "seconds": 0.2},
            {"name": "c", "solved": False, "aut_assisted": False,
             "winner": None, "seconds": 0.2},
        ):
            fh.write(json.dumps(rec) + "\n")
    got = screen.report(str(tmp_path), chunks=1, chunk_index=1, log=lambda _: None)
    assert got["rows"] == 3
    assert got["ac"] == 1 and got["aut_assisted"] == 1 and got["unsolved"] == 1
    assert got["by_winner"] == {"rewrite": 1}


def test_the_report_refuses_a_run_that_wrote_a_rejected_certificate(tmp_path):
    path = screen.out_path(str(tmp_path), 1, 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(json.dumps(
            {"name": "a", "solved": False, "aut_assisted": False,
             "certificate_rejected": "path does not end on a terminal pair",
             "winner": None, "seconds": 0.2}) + "\n")
    with pytest.raises(SystemExit, match="failed replay"):
        screen.report(str(tmp_path), chunks=1, chunk_index=1, log=lambda _: None)


def test_resume_reads_finished_rows_and_skips_errors_and_torn_lines(tmp_path):
    path = tmp_path / "partial.jsonl"
    path.write_text(
        json.dumps({"name": "good", "solved": False}) + "\n"
        + json.dumps({"name": "died", "error": "boom"}) + "\n"
        + '{"name": "torn", "solved":\n')
    assert set(screen.read_done(str(path))) == {"good"}


def test_chunks_partition_the_list_exactly():
    rows = [{"name": f"ac19_{i}"} for i in range(1000)]
    for chunks in (1, 3, 7, 64):
        parts = [screen.stride_chunk(rows, chunks, i)
                 for i in range(1, chunks + 1)]
        assert sum(len(p) for p in parts) == len(rows)
        assert {r["name"] for p in parts for r in p} == {r["name"] for r in rows}
        assert max(len(p) for p in parts) - min(len(p) for p in parts) <= 1
    with pytest.raises(ValueError):
        screen.stride_chunk(rows, 4, 5)


def test_the_worker_guard_fails_closed(monkeypatch):
    monkeypatch.setattr(screen.resource, "setrlimit",
                        lambda *a: (_ for _ in ()).throw(ValueError("unsupported")))
    with pytest.raises(SystemExit, match="address-space limit"):
        screen._init_worker(1 << 30)


def test_plan_reports_the_measured_cost_not_a_guess():
    info = screen.plan(log=lambda _: None)
    assert info["budget_per_row"] == PREFIX_BUDGET == 501
    assert info["cap"] == SEARCH_CAP == 255
    assert info["seconds_per_row_measured"] == screen.SECONDS_PER_ROW
    assert info["peak_rss_gb_per_worker_measured"] < 1.0
    # the whole point of this pass: it fits where the 10M hybrid cannot
    assert info["gb_needed_for_n_workers"]["8"] < 32


def test_a_row_that_blows_up_comes_back_as_an_error_not_an_exception():
    record = screen.run_row({"name": "bad", "r1": "x" * 300, "r2": "y"})
    assert record["error"]
    assert record["name"] == "bad"
    assert "traceback" in record


def _run_record(tmp_path, row):
    path = screen.out_path(str(tmp_path), 1, 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = screen.run_row(row)
    with open(path, "w") as fh:
        fh.write(json.dumps(record) + "\n")
    return record


def test_certify_regenerates_the_certificate_and_matches_the_digest(tmp_path):
    record = _run_record(tmp_path, dict(AC_ROW, n_members=1))
    target = screen.certify(str(tmp_path), chunks=1, chunk_index=1,
                            names=[AC_ROW["name"]], log=lambda _: None)
    with open(target) as fh:
        certificates = [json.loads(line) for line in fh]
    assert len(certificates) == 1
    got = certificates[0]
    assert got["certified"] is True
    assert got["certificate_sha256"] == record["certificate_sha256"]
    assert len(got["path_moves"]) == record["certificate_moves"]
    assert got["path"][-1] in (["x", "Y"], ["x", "y"], ["X", "y"], ["X", "Y"],
                               ["y", "x"], ["Y", "x"], ["y", "X"], ["Y", "X"])


def test_certify_refuses_a_row_whose_digest_no_longer_reproduces(tmp_path):
    record = _run_record(tmp_path, dict(AC_ROW, n_members=1))
    path = screen.out_path(str(tmp_path), 1, 1)
    record["certificate_sha256"] = "0" * 64
    with open(path, "w") as fh:
        fh.write(json.dumps(record) + "\n")
    with pytest.raises(SystemExit, match="different certificate"):
        screen.certify(str(tmp_path), chunks=1, chunk_index=1,
                       names=[AC_ROW["name"]], log=lambda _: None)


def test_certify_refuses_a_name_this_run_did_not_solve(tmp_path):
    _run_record(tmp_path, dict(AC_ROW, n_members=1))
    with pytest.raises(SystemExit, match="not solved in this run"):
        screen.certify(str(tmp_path), chunks=1, chunk_index=1,
                       names=["ac19_0"], log=lambda _: None)


def test_residues_write_the_two_lists_in_the_shipped_schema(tmp_path):
    orbits = {r["name"]: r for r in screen.load_rows()}
    picks = [n for n in ("ac19_44381", "ac19_51034") if n in orbits]
    assert len(picks) == 2
    path = screen.out_path(str(tmp_path), 1, 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(json.dumps(
            {"name": picks[0], "r1": orbits[picks[0]]["r1"],
             "r2": orbits[picks[0]]["r2"], "solved": False,
             "aut_assisted": False, "nodes_explored": 501,
             "min_relator_length": 19, "winner": None, "seconds": 0.2}) + "\n")
        fh.write(json.dumps(
            {"name": picks[1], "r1": orbits[picks[1]]["r1"],
             "r2": orbits[picks[1]]["r2"], "solved": False,
             "aut_assisted": True, "nodes_explored": 17,
             "min_relator_length": 17, "winner": "s40_gen", "seconds": 0.2}) + "\n")
    written = screen.residues(str(tmp_path), chunks=1, chunk_index=1,
                              log=lambda _: None)
    assert [os.path.basename(p) for p in written] == [
        "unsolved_cascade501_b501.csv", "aut_assisted_cascade501_b501.csv"]
    with open(written[0]) as fh:
        rows = list(csv.DictReader(fh))
    assert [r["name"] for r in rows] == [picks[0]]
    assert rows[0]["members"] == orbits[picks[0]]["members"]
    assert list(rows[0]) == ["name", "r1", "r2", "n_members", "members",
                             "nodes_explored", "min_relator_length"]
    with open(written[1]) as fh:
        assert [r["name"] for r in csv.DictReader(fh)] == [picks[1]]


# --- the launcher, which is where a campaign actually gets started ---------
REMOTE_SH = os.path.join(ROOT, "experiments", "search", "run_remote.sh")


def _remote(*args, **env):
    import subprocess
    e = dict(os.environ, SRC=ROOT, **env)
    return subprocess.run(["bash", REMOTE_SH, *args], capture_output=True,
                          text=True, env=e, timeout=600)


def test_the_screen_campaign_plans_without_the_big_ram_planner():
    """The hcompact planner would price a reservation this stage never makes,
    and on a small box it refuses outright. SCREEN=1 routes past it."""
    got = _remote("plan", CAMPAIGN="ac19_cascade_screen")
    assert got.returncode == 0, got.stderr
    assert '"rows": 72779' in got.stdout
    assert '"budget_per_row": 501' in got.stdout
    assert "319.0 GiB per lane" in got.stdout       # the contrast, on the page


def test_the_screen_job_runs_the_screen_runner_not_the_5m_runner(tmp_path):
    got = _remote("job", CAMPAIGN="ac19_cascade_screen", OUT=str(tmp_path))
    assert got.returncode == 0, got.stderr
    job = (tmp_path / "_job.sh").read_text()
    assert "run_ac19_cascade_screen run" in job
    assert 'if [ "1" = 1 ]; then' in job            # SCREEN baked at write time
    import subprocess
    assert subprocess.run(["bash", "-n", str(tmp_path / "_job.sh")]).returncode == 0


def test_the_hybrid_job_runs_the_entry_point_that_also_certifies(tmp_path):
    got = _remote("job", CAMPAIGN="ac19_hybrid_10m", OUT=str(tmp_path))
    assert got.returncode == 0, got.stderr
    job = (tmp_path / "_job.sh").read_text()
    assert "run_ac19_hybrid_10m run" in job
    assert 'elif [ "1" = 1 ]; then' in job


def test_an_unknown_campaign_still_refuses_to_start():
    got = _remote("plan", CAMPAIGN="ac19_not_a_campaign")
    assert got.returncode == 2
    assert "unknown CAMPAIGN" in got.stderr
    assert "ac19_cascade_screen" in got.stderr and "ac19_hybrid_10m" in got.stderr


# --- the control arm, which is what makes the headline readable ------------
def test_the_control_arm_never_lets_a_basis_change_into_the_heap():
    """`ac501` is `s40_gen` with one door shut. If a Nielsen image can still
    reach the path, the control controls for nothing."""
    checked = 0
    for row in _rows()[:40]:
        got = screen.search_row((row["r1"], row["r2"]), "ac501")
        assert all(s["kind"] == "substitution" for s in got["steps"])
        record = screen.run_row(row, "ac501")
        assert record["aut_assisted"] is False
        assert record["arm"] == "ac501"
        assert record["certificate"] in (None, "ac")
        checked += 1
    assert checked == 40


def test_the_two_arms_share_a_budget_a_cap_and_a_priority():
    """One knob apart, or the comparison means nothing."""
    assert screen.ARMS == ("cascade501", "ac501")
    assert screen.S40 == {"s_weight": 40.0, "mk_weight": 0.0, "w_weight": 0.0}
    got = screen.search_row(("YXXyx", "YYYYYXyyyxyxxx"), "ac501")
    assert got["nodes_explored"] <= PREFIX_BUDGET


def test_each_arm_writes_its_own_file():
    a = screen.out_path("/o", 1, 1, "cascade501")
    b = screen.out_path("/o", 1, 1, "ac501")
    assert a != b
    assert a.endswith("ac19_cascade_screen_cascade501_b501_mrl255.jsonl")
    assert b.endswith("ac19_cascade_screen_ac501_b501_mrl255.jsonl")


def test_an_unknown_arm_is_refused_at_both_layers():
    with pytest.raises(ValueError, match="unknown arm"):
        screen.search_row(("xyX", "yyx"), "s20_mk2")
    with pytest.raises(SystemExit, match="unknown arm"):
        screen.run("/o", arm="s20_mk2", log=lambda _: None)


def test_the_ladder_feeds_each_rung_the_rung_belows_leftovers(monkeypatch, tmp_path):
    """A rung must run the residue, not the screen again. Running every rung
    over all 72,779 rows would cost four screens and change no answer."""
    seen = []

    def fake_run(out_dir, *, arm, budget, rows_csv, workers, chunks,
                 chunk_index, log):
        seen.append((budget, rows_csv))

    counts = iter([{"rows": 100, "ac": 90, "aut_assisted": 0, "unsolved": 10},
                   {"rows": 10, "ac": 8, "aut_assisted": 0, "unsolved": 2},
                   {"rows": 2, "ac": 2, "aut_assisted": 0, "unsolved": 0}])
    monkeypatch.setattr(screen, "run", fake_run)
    monkeypatch.setattr(screen, "report", lambda *a, **k: next(counts))
    monkeypatch.setattr(screen, "residues",
                        lambda *a, **k: [f"resid_b{k['budget']}.csv", "aut.csv"])

    got = screen.ladder(str(tmp_path), arm="ac501", rungs=(501, 1000, 10_000),
                        log=lambda _: None)
    assert seen == [(501, None), (1000, "resid_b501.csv"),
                    (10_000, "resid_b1000.csv")]
    assert [r["budget"] for r in got] == [501, 1000, 10_000]


def test_the_ladder_stops_as_soon_as_nothing_is_left(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(screen, "run",
                        lambda out_dir, **k: seen.append(k["budget"]))
    monkeypatch.setattr(screen, "report", lambda *a, **k: {
        "rows": 5, "ac": 5, "aut_assisted": 0, "unsolved": 0})
    monkeypatch.setattr(screen, "residues", lambda *a, **k: ["u.csv", "a.csv"])
    screen.ladder(str(tmp_path), rungs=(501, 1000, 10_000, 100_000),
                  log=lambda _: None)
    assert seen == [501], "a finished ladder must not run the rungs above it"


def test_the_ladder_stops_where_the_cheap_pass_stops():
    assert screen.LADDER[0] == PREFIX_BUDGET == 501
    assert screen.LADDER[-1] == screen.MAX_BUDGET == 100_000
    # cascade_heuristics refuses anything past this, and past it the
    # hcompact campaigns are the right tool anyway
    with pytest.raises(ValueError, match="outside 1..100000"):
        screen.search_row(("xyX", "yyx"), "ac501", 100_001)
