"""The CI speed check (``benchmark/speed.py``): which workloads count as slower, and how they are timed."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("speed", Path(__file__).parents[1] / "benchmark" / "speed.py")
speed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(speed)


def test_only_a_workload_over_the_tolerance_is_slower():
    timings = [speed.Timing("same", 10, 10), speed.Timing("faster", 10, 7), speed.Timing("edge", 10, 11.5),
               speed.Timing("slower", 10, 11.6)]
    assert [t.name for t in speed.slower(timings, 0.15)] == ["slower"]
    assert "| slower | 10.00 | 11.60 | 1.16 | slower |" in speed.table(timings, 0.15)


def test_the_trees_are_timed_in_turn_and_the_fastest_run_is_kept(monkeypatch):
    calls, times = [], iter([5, 9, 4, 8, 6, 7] * 2 * len(speed.WORKLOADS))
    def fake(tree, config, rows, args):
        calls.append((tree, config, rows, *args))
        return next(times)
    monkeypatch.setattr(speed, "cpu_seconds", fake)
    timings = speed.measure("base", "head", repeat=3, log=lambda *_: None)
    assert [call[0] for call in calls[:6]] == ["base", "head"] * 3
    assert calls[6][1:] == ("configs/greedy_fast.toml", "0:640:20", "--set", "path=false")
    assert timings[0] == speed.Timing("greedy normal", 4, 7)
    assert [t.name for t in timings[-3:]] == ["rank3 normal", "rank4 normal", "rank5 normal"]
    assert [t.name for t in speed.measure("b", "h", 1, ["hybrid"], log=lambda *_: None)] == ["hybrid normal",
                                                                                         "hybrid fast"]
    times = iter([3, 4, 3, 4])
    same = speed.measure("tree", "tree", 1, ["hybrid"], log=lambda *_: None)    # a tree against itself: the noise
    assert [(t.base, t.head) for t in same] == [(3, 4), (3, 4)]


def test_every_config_is_timed():
    timed = {config for config, _, _ in speed.WORKLOADS.values()}
    configs = {f"configs/{p.name}" for p in (Path(__file__).parents[1] / "configs").glob("*.toml")}
    assert configs - timed == {"configs/smoke.toml", "configs/template.toml"}      # greedy again, with fewer pops


def test_main_fails_on_a_slower_head(monkeypatch, tmp_path):
    monkeypatch.setattr(speed, "measure", lambda *a, **k: [speed.Timing("hybrid normal", 1, 2.5)])
    summary = tmp_path / "summary.md"
    with pytest.raises(SystemExit, match="hybrid normal"):
        speed.main(["base", "head", "--summary", str(summary)])
    assert "| hybrid normal | 1.00 | 2.50 | 2.50 | slower |" in summary.read_text()


@pytest.mark.slow
def test_one_workload_runs_on_this_tree():
    root = str(Path(__file__).parents[1])
    assert speed.cpu_seconds(root, "configs/greedy_fast.toml", "0:2", ["--set", "path=false"]) > 0
