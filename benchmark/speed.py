"""Speed check: the CPU seconds of each pipeline on two source trees, timed in turn, and which got slower.

    python benchmark/speed.py BASE_TREE HEAD_TREE [--only NAME ...] [--repeat 3] [--confirm 9] [--tolerance 0.02]
                              [--summary FILE]

Each workload is a config of ``configs/`` run with ``run.py`` on a slice of its benchmark, once as is (``normal``:
paths kept, decoded and replayed) and once with ``path = false`` (``fast``). The time is the rows' CPU seconds from
``summary.json`` (``core_seconds`` for the rank-n sweep), so start-up and compilation are left out. The trees are
timed in turn (in alternating order), ``repeat`` times each, and the fastest time of each is kept. A workload over
``1 + tolerance`` times its base time is timed ``confirm`` more rounds, since three runs on a CI runner varied by up to
5% on identical code (10% for RL), and the check fails when it is still over.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

# name: (config, rows, modes); each slice takes 1.5 to 9 CPU seconds a run on a CI runner. Rank-n has no path switch.
BOTH, NORMAL = ("normal", "fast"), ("normal",)
WORKLOADS = {
    "greedy": ("configs/greedy_fast.toml", "0:640:10", BOTH),
    "s20_mk2": ("configs/s20_mk2_fast.toml", "0:640:8", BOTH),
    "ladder": ("configs/ladder.toml", "0:200:20", BOTH),
    "spec": ("configs/baseline_spec.toml", "464,537", BOTH),
    "aut": ("configs/aut.toml", "0:60:4", BOTH),
    "cov": ("configs/cov.toml", "0:60:8", BOTH),
    "ngen_sac": ("configs/ngen_sac.toml", "0:60:8", BOTH),
    "hybrid": ("configs/hybrid.toml", "0:640", BOTH),
    "rl": ("configs/rl.toml", "0:30:3", BOTH),
    "rank3": ("configs/rank3_bf.toml", "0:640:160", NORMAL),
    "rank4": ("configs/rank4_bf.toml", "0:320:80", NORMAL),
    "rank5": ("configs/rank5_bf.toml", "0:128:64", NORMAL),
}
MODE_SETS = {"normal": [], "fast": ["--set", "path=false"]}


class Timing(NamedTuple):
    name: str
    base: float
    head: float
    rounds: int                                                 # runs of each tree, the fastest kept

    @property
    def ratio(self):
        return self.head / self.base if self.base else float("inf")


def slower(timings, tolerance):
    """The timings whose head takes more than ``1 + tolerance`` times the base."""
    return [t for t in timings if t.ratio > 1 + tolerance]


def table(timings, tolerance):
    """A markdown table of the timings, each marked ok or slower."""
    lines = ["| workload | base CPU s | head CPU s | head / base | runs | |", "|---|---:|---:|---:|---:|---|"]
    for t in timings:
        mark = "slower" if t in slower(timings, tolerance) else "ok"
        lines.append(f"| {t.name} | {t.base:.2f} | {t.head:.2f} | {t.ratio:.3f} | {t.rounds} | {mark} |")
    return "\n".join(lines)


def cpu_seconds(tree, config, rows, args):
    """The rows' CPU seconds of one ``run.py`` run of ``config`` on ``rows`` in ``tree``."""
    with tempfile.TemporaryDirectory() as out:
        env = {**os.environ, "NUMBA_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "PYTHONHASHSEED": "0"}
        command = [sys.executable, "run.py", "--config", config, "--out", out, "--rows", rows, "--set", "workers=1",
                   *args]
        subprocess.run(command, cwd=tree, env=env, check=True, capture_output=True)
        summary = json.loads(next(Path(out).glob("*/summary.json")).read_text())
    return summary.get("cpu_seconds") or summary["core_seconds"]


def measure(base, head, repeat, names=None, tolerance=0.02, confirm=9, log=print):
    """The fastest of ``repeat`` runs of each workload (all, or those in ``names``) and mode on each tree, the trees
    timed in turn; a workload over ``1 + tolerance`` is timed ``confirm`` more rounds before it counts."""
    timings = []
    for name in names or WORKLOADS:
        config, rows, modes = WORKLOADS[name]
        for mode in modes:
            best = [float("inf"), float("inf")]                  # base, head (which may be the same tree)
            def time_rounds(first, last):                       # odd rounds time the head first
                for r in range(first, last):
                    for i in (0, 1) if r % 2 == 0 else (1, 0):
                        best[i] = min(best[i], cpu_seconds((base, head)[i], config, rows, MODE_SETS[mode]))
            time_rounds(0, repeat)
            timing = Timing(f"{name} {mode}", *best, repeat)
            if slower([timing], tolerance) and confirm:
                log(f"{timing.name}: {timing.ratio:.3f} after {repeat} runs; timing {confirm} more")
                time_rounds(repeat, repeat + confirm)
                timing = Timing(timing.name, *best, repeat + confirm)
            timings.append(timing)
            log(f"{timing.name}: {best[0]:.2f} -> {best[1]:.2f} s ({timing.ratio:.3f})")
    return timings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--confirm", type=int, default=9, help="more runs for a workload over the tolerance")
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--only", nargs="+", choices=WORKLOADS, help="these workloads only (default: all)")
    parser.add_argument("--summary", help="append the markdown table to this file (CI: $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)
    timings = measure(args.base, args.head, args.repeat, args.only, args.tolerance, args.confirm)
    report = table(timings, args.tolerance)
    print(report)
    if args.summary:
        with open(args.summary, "a") as f:
            f.write(f"## Speed against the base\n\n{report}\n")
    bad = slower(timings, args.tolerance)
    if bad:
        sys.exit(f"slower than the base by more than {args.tolerance:.0%}: {', '.join(t.name for t in bad)}")


if __name__ == "__main__":
    main()
