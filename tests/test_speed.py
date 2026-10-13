"""The CI speed check (``benchmark/speed.py``): which workloads count as slower or faster, how they are timed, and
the table a pull request gets."""
import importlib.util
import itertools
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("speed", Path(__file__).parents[1] / "benchmark" / "speed.py")
speed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(speed)


def test_only_a_workload_over_the_tolerance_is_slower():
    timings = [speed.Timing("same", 10, 10, 3), speed.Timing("faster", 10, 7, 3), speed.Timing("edge", 10, 10.2, 3),
               speed.Timing("slower", 10, 10.3, 9)]
    assert [t.name for t in speed.slower(timings, 0.02)] == ["slower"]
    table = speed.table(timings, 0.02)
    assert "| slower | 10.00 | 10.30 | 3.0% slower | 9 | **slower** |" in table
    assert "| faster | 10.00 | 7.00 | 42.9% faster | 3 | faster |" in table
    assert "| edge | 10.00 | 10.20 | 2.0% slower | 3 | within 2% |" in table


def test_a_change_reads_as_percent_faster_or_slower():
    assert speed.Timing("a", 12, 10, 3).change == "20.0% faster"                  # 12 / 10: a fifth more speed
    assert speed.Timing("b", 10, 10.15, 3).change == "1.5% slower"
    assert speed.Timing("c", 10, 10, 3).change == "same"


def fake_runs(monkeypatch, base, head):
    """Time each tree's runs from its list in order (a number: every run); return the trees in the order run."""
    calls = []
    runs = {tree: iter(t) if isinstance(t, list) else itertools.repeat(t) for tree, t in (("base", base),
                                                                                         ("head", head))}
    def fake(tree, config, rows, args):
        calls.append(tree)
        return next(runs[tree])
    monkeypatch.setattr(speed, "cpu_seconds", fake)
    return calls


def test_a_workload_over_the_limit_is_timed_again_and_noise_clears(monkeypatch):
    calls = fake_runs(monkeypatch, 10, [10.5] * 3 + [10.1] * 6 + [10] * 3)  # 5% over in 3 rounds, then 1%
    [hybrid, _] = speed.measure("base", "head", 3, ["hybrid"], tolerance=0.02, confirm=6, log=lambda *_: None)
    assert hybrid == speed.Timing("hybrid normal", 10, 10.1, 9) and not speed.slower([hybrid], 0.02)
    assert calls[:18] == ["base", "head", "head", "base"] * 4 + ["base", "head"]


def test_a_real_slowdown_still_fails_after_the_second_timing(monkeypatch):
    fake_runs(monkeypatch, 10, [10.5] * 18)
    timings = speed.measure("base", "head", 3, ["hybrid"], tolerance=0.02, confirm=6, log=lambda *_: None)
    assert [(t.ratio, t.rounds) for t in speed.slower(timings, 0.02)] == [(1.05, 9), (1.05, 9)]


def test_a_workload_that_looks_faster_is_timed_again(monkeypatch):
    fake_runs(monkeypatch, [10.5] * 3 + [10] * 9, 10)                         # the base is slow 3 times: noise
    timings = speed.measure("base", "head", 3, ["hybrid"], tolerance=0.02, confirm=6, log=lambda *_: None)
    assert timings == [speed.Timing("hybrid normal", 10, 10, 9), speed.Timing("hybrid fast", 10, 10, 3)]
    fake_runs(monkeypatch, 10, 8)                                             # a real speed-up is confirmed
    timings = speed.measure("base", "head", 3, ["hybrid"], tolerance=0.02, confirm=6, log=lambda *_: None)
    assert [(t.change, t.rounds) for t in timings] == [("25.0% faster", 9)] * 2


def test_a_workload_within_the_limit_is_timed_once(monkeypatch):
    calls = fake_runs(monkeypatch, 10, [10.1] * 6)
    timings = speed.measure("base", "head", 3, ["hybrid"], tolerance=0.02, confirm=6, log=lambda *_: None)
    assert len(calls) == 12 and [t.rounds for t in timings] == [3, 3]


def test_the_trees_are_timed_in_turn_and_the_fastest_run_is_kept(monkeypatch):
    calls, times = [], iter([5, 9, 8, 4, 6, 7] * 2 * len(speed.WORKLOADS))   # base 5, 4, 6; head 9, 8, 7
    def fake(tree, config, rows, args):
        calls.append((tree, config, rows, *args))
        return next(times)
    monkeypatch.setattr(speed, "cpu_seconds", fake)
    timings = speed.measure("base", "head", repeat=3, confirm=0, log=lambda *_: None)
    assert [call[0] for call in calls[:6]] == ["base", "head", "head", "base", "base", "head"]
    assert calls[6][1:] == ("configs/greedy_fast.toml", speed.WORKLOADS["greedy"][1], "--set", "path=false")
    assert timings[0] == speed.Timing("greedy normal", 4, 7, 3)
    assert [t.name for t in timings[-3:]] == ["rank3 normal", "rank4 normal", "rank5 normal"]
    assert [t.name for t in speed.measure("b", "h", 1, ["hybrid"], confirm=0, log=lambda *_: None)] == [
        "hybrid normal", "hybrid fast"]
    times = iter([3, 4, 3, 4])
    same = speed.measure("tree", "tree", 1, ["hybrid"], confirm=0, log=lambda *_: None)    # a tree against itself
    assert [(t.base, t.head) for t in same] == [(3, 4), (3, 4)]


def test_every_config_is_timed():
    timed = {config for config, _, _ in speed.WORKLOADS.values()}
    configs = {f"configs/{p.name}" for p in (Path(__file__).parents[1] / "configs").glob("*.toml")}
    assert configs - timed == {"configs/smoke.toml", "configs/template.toml"}      # greedy again, with fewer pops


def test_main_fails_on_a_slower_head(monkeypatch, tmp_path):
    monkeypatch.setattr(speed, "measure", lambda *a, **k: [speed.Timing("hybrid normal", 1, 1.03, 9)])
    summary, saved = tmp_path / "summary.md", tmp_path / "hybrid.json"
    with pytest.raises(SystemExit, match="hybrid normal"):                  # the default limit is 2%
        speed.main(["base", "head", "--summary", str(summary), "--json", str(saved)])
    assert "| hybrid normal | 1.00 | 1.03 | 3.0% slower | 9 | **slower** |" in summary.read_text()
    assert speed.load([saved]) == [speed.Timing("hybrid normal", 1, 1.03, 9)]   # saved for the pull request's table


def test_the_report_joins_the_jobs_in_workload_order(tmp_path, capsys):
    jobs = {"rank.json": [speed.Timing("rank3 normal", 2, 2, 3)],
            "greedy.json": [speed.Timing("greedy fast", 1, 1.01, 3), speed.Timing("greedy normal", 2.4, 2, 9)]}
    for name, timings in jobs.items():
        speed.save(timings, tmp_path / name)
    speed.main(["--report", *(str(tmp_path / name) for name in jobs)])
    report = capsys.readouterr().out
    rows = [line.split(" | ")[0] for line in report.splitlines() if line.startswith("| ") and "CPU" not in line]
    assert rows == ["| greedy normal", "| greedy fast", "| rank3 normal"]
    assert ("No pipeline is more than 2% slower. 1 pipeline is more than 2% faster: greedy normal (20.0% faster)."
            in report)
    failing = speed.report([speed.Timing("aut fast", 1, 1.05, 12), speed.Timing("cov fast", 1, 1.03, 12)], 0.02)
    assert "**2 pipelines are more than 2% slower, so the check fails:** aut fast (5.0% slower), cov fast" in failing


@pytest.mark.slow
def test_one_workload_runs_on_this_tree():
    root = str(Path(__file__).parents[1])
    assert speed.cpu_seconds(root, "configs/greedy_fast.toml", "0:2", ["--set", "path=false"]) > 0
