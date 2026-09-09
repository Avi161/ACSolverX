"""A/B throughput bench for ``hcompact``-shaped search engines.

Compares two engines that expose the same ``greedy_search_hcompact`` /
``HCompactSolver`` surface: by default the frozen reference
(``hcompact_baseline``, a verbatim copy of ``hcompact.py`` at commit
``5d047da5``) against whatever the working copy of ``hcompact.py`` currently
is (``candidate``). The frozen copy never changes, so every run of this
script is comparing "candidate today" against a fixed yardstick rather than
against a moving target.

WHY A FRESH SUBPROCESS PER MEASUREMENT
---------------------------------------
Two engines timed in the same process would share one numba JIT cache and one
page-fault history; the second one timed always looks faster for reasons that
have nothing to do with the code. Each measurement here is a fresh
interpreter: pin the CPU, warm up (a 2,000-node call, well under where numba
compiles), then time exactly one solve. Engines alternate A,B,A,B,... across
reps for a given row (rather than all of A's reps then all of B's) so that
any drift over the run's wall-clock span -- another agent's job landing on
this box, thermal throttling, whatever -- lands on both engines equally
rather than biasing whichever one runs first or last.

WHAT "MATCHES" MEANS HERE
--------------------------
Both engines are asked for a bit-identical search (see gates.py for the
proof); this script additionally computes a sha256 "record fingerprint" of
each run's full returned dict (JSON, keys sorted) and reports, per row,
whether the two engines' fingerprints agree. A mismatch here means either
this box is not looking at the "identical search" invariant gates.py checks,
or the two engine modules given to --engines are not actually equivalent --
either way it is loud, not a silent difference in the timing numbers.

USAGE
-----
    PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/bench.py \\
        --rows aca_0,aca_1 --budget 20000 --reps 2 --out /tmp/bench.json

Run from the repository root (every module here inserts the repo root into
``sys.path`` itself by walking up from ``__file__``, but the CSV path and the
subprocess's cwd are resolved the same way, so running from ROOT with
``PYTHONPATH=.`` is the supported invocation).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Locate the repo root the same way hcompact.py / hsolve.py do: walk up from
# this file until a directory holding both "experiments" and "data" is found.
# Works regardless of where perf_lab/ ends up nested, and regardless of cwd.
# ---------------------------------------------------------------------------
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
ROOT = _d
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

THIS_FILE = os.path.abspath(__file__)
CSV_PATH = os.path.join(ROOT, "results", "stable_ac", "fable", "aca_124.csv")

ENGINE_MODULES = {
    "baseline": "experiments.heuristic_search.core.perf_lab.hcompact_baseline",
    "candidate": "experiments.heuristic_search.core.hcompact",
    # hcompact_baseline imports the LIVE greedy_baseline / hfast kernels, so
    # a kernel change moves both engines and the A/B cannot see it. "frozen"
    # is the same engine text importing frozen copies of those kernels
    # (perf_lab/frozen/, at 9b98e313): the yardstick for kernel work.
    "frozen": "experiments.heuristic_search.core.perf_lab.frozen.hcompact_frozen",
    # "current" is the build the campaign runs today (a1d1be23: 2-bit rows,
    # the allocation-free expansion kernel, the uint64-indexed hash), engine
    # and kernels all frozen verbatim under perf_lab/frozen2/. Every ratio
    # reported after that commit is candidate over this.
    "current": "experiments.heuristic_search.core.perf_lab.frozen2.hcompact_frozen2",
}


def purge_numba_cache(root=None):
    """Delete numba's on-disk cache (*.nbi / *.nbc) under experiments/.

    numba keys a cached function on ITS OWN source file's stamp and bytecode
    (numba/core/caching.py: ``get_source_stamp`` and ``_index_key``); callees
    compiled into it from OTHER files are not tracked. So after an edit to
    greedy_baseline.py or hfast.py, every ``cache=True`` caller in an
    unchanged file -- ``_run_chunk_h`` in hcompact.py, the replay kernels in
    phase_split.py, the frozen engines -- silently reloads machine code with
    the OLD kernel linked in, and a measurement or gate then exercises code
    that is not in the working tree. Both bench.py and gates.py purge before
    doing anything; the cost is one recompilation per process, which the
    bench's warm-up call already excludes from the timed run.
    """
    root = root or ROOT
    n = 0
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "experiments")):
        if os.path.basename(dirpath) != "__pycache__":
            continue
        for fn in filenames:
            if fn.endswith((".nbi", ".nbc")):
                try:
                    os.unlink(os.path.join(dirpath, fn))
                    n += 1
                except OSError:
                    pass
    return n

DEFAULT_ROWS = "aca_0,aca_1,aca_3,aca_4,aca_5,aca_8"

WARMUP_BUDGET = 2000
TIMED_START_MARK = "PERF_LAB_TIMED_START"
TIMED_END_MARK = "PERF_LAB_TIMED_END"


# ---------------------------------------------------------------------------
# Row loading
# ---------------------------------------------------------------------------
def load_rows(names, csv_path=CSV_PATH):
    """``{name: (r1, r2)}`` for the requested rows, read from the real-row CSV."""
    table = {}
    with open(csv_path, newline="") as f:
        for rec in csv.DictReader(f):
            table[rec["name"]] = (rec["r1"], rec["r2"])
    missing = [n for n in names if n not in table]
    if missing:
        raise SystemExit(f"rows not found in {csv_path}: {missing}")
    return [(n, table[n][0], table[n][1]) for n in names]


def read_vmhwm_kib():
    """Peak resident set size (VmHWM) of the CURRENT process, in KiB, or None."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def sha256_of_dict(d):
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Runner mode: this is what each fresh subprocess actually executes. Kept in
# the same file (rather than a separate script) so there is exactly one
# source of truth for "how a measurement is taken".
# ---------------------------------------------------------------------------
def cmd_runner(args):
    try:
        os.sched_setaffinity(0, {args.cpu})
    except (AttributeError, OSError) as e:
        print(f"WARN: could not pin to cpu {args.cpu}: {e}", file=sys.stderr)

    import importlib
    mod = importlib.import_module(args.engine_module)
    greedy_search_hcompact = mod.greedy_search_hcompact
    HCompactSolver = mod.HCompactSolver

    from experiments.search.run_leftovers_1m import S20_MK2
    assert args.config == "S20_MK2"
    config = S20_MK2

    # Warm-up: excludes numba's first-call compilation from the timed run.
    greedy_search_hcompact(args.r1, args.r2, WARMUP_BUDGET,
                           max_relator_length=args.mrl, config=config,
                           track_path=False)

    print(TIMED_START_MARK, flush=True)
    t0 = time.perf_counter()
    result = greedy_search_hcompact(args.r1, args.r2, args.budget,
                                    max_relator_length=args.mrl, config=config,
                                    track_path=False)
    t1 = time.perf_counter()
    print(TIMED_END_MARK, flush=True)
    seconds = t1 - t0

    peak_kib = read_vmhwm_kib()
    peak_gib = (peak_kib / (1024.0 ** 2)) if peak_kib is not None else None

    # A second solver, constructed identically but never solved, to report
    # the layout costs without paying for (or perturbing) the timed search.
    sizer = HCompactSolver(args.r1, args.r2, max_nodes=args.budget,
                           max_relator_length=args.mrl, config=config,
                           track_path=False)

    out = {
        "row": args.row,
        "engine_module": args.engine_module,
        "seconds": seconds,
        "nodes_explored": result["nodes_explored"],
        "pops_per_second": (result["nodes_explored"] / seconds
                            if seconds > 0 else float("inf")),
        "peak_rss_gib": peak_gib,
        "bytes_per_state": sizer.bytes_per_state(),
        "bytes_reserved": sizer.bytes_reserved(),
        "solved": result["solved"],
        "fingerprint": sha256_of_dict(result),
    }
    with open(args.result_path, "w") as f:
        json.dump(out, f)


def extract_widen_lines(stdout_text):
    """"rows widen" lines printed strictly between the timed-run markers."""
    if TIMED_START_MARK not in stdout_text or TIMED_END_MARK not in stdout_text:
        return []
    mid = stdout_text.split(TIMED_START_MARK, 1)[1].split(TIMED_END_MARK, 1)[0]
    return [ln for ln in mid.splitlines() if "rows widen" in ln]


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_one(engine_key, engine_module, row_name, r1, r2, budget, mrl, cpu,
           tmp_dir, timeout):
    result_path = os.path.join(
        tmp_dir, f"result_{engine_key}_{row_name}_{os.getpid()}_{time.time_ns()}.json")
    cmd = [sys.executable, THIS_FILE, "--runner",
          "--engine-module", engine_module,
          "--row", row_name, "--r1", r1, "--r2", r2,
          "--budget", str(budget), "--mrl", str(mrl), "--cpu", str(cpu),
          "--config", "S20_MK2", "--result-path", result_path]
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True,
                          text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"subprocess failed for engine={engine_key} row={row_name} "
            f"(rc={proc.returncode}):\n--- stdout ---\n{proc.stdout}\n"
            f"--- stderr ---\n{proc.stderr}")
    with open(result_path) as f:
        data = json.load(f)
    os.unlink(result_path)
    data["engine_key"] = engine_key
    data["widen_lines"] = extract_widen_lines(proc.stdout)
    return data


def median(xs):
    return statistics.median(xs)


def fmt_rate(x):
    return f"{x:,.1f}"


def main_bench(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", default=DEFAULT_ROWS,
                    help="comma-separated row names from aca_124.csv")
    ap.add_argument("--budget", type=int, default=200_000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--mrl", type=int, default=64)
    ap.add_argument("--cpu", type=int, default=1,
                    help="core to pin each subprocess to (os.sched_setaffinity)")
    ap.add_argument("--out", default=None, help="JSON output path")
    ap.add_argument("--engines", default="baseline,candidate",
                    help="comma list of engine keys from "
                         f"{sorted(ENGINE_MODULES)} (order sets the A,B,... "
                         "alternation)")
    ap.add_argument("--timeout", type=float, default=600.0,
                    help="per-subprocess timeout, seconds")
    args = ap.parse_args(argv)

    row_names = [s.strip() for s in args.rows.split(",") if s.strip()]
    rows = load_rows(row_names)

    engine_keys = [s.strip() for s in args.engines.split(",") if s.strip()]
    for k in engine_keys:
        if k not in ENGINE_MODULES:
            raise SystemExit(f"unknown engine {k!r}; choose from {sorted(ENGINE_MODULES)}")

    tmp_dir = os.path.join(ROOT, "experiments", "heuristic_search", "core",
                           "perf_lab", ".bench_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    runs = []   # flat list of every measurement, in execution order
    purged = purge_numba_cache()
    print(f"bench: rows={row_names} budget={args.budget} reps={args.reps} "
         f"mrl={args.mrl} cpu={args.cpu} engines={engine_keys} "
         f"(purged {purged} stale numba cache files first)")
    t_start = time.time()
    for row_name, r1, r2 in rows:
        for rep in range(args.reps):
            for engine_key in engine_keys:
                module = ENGINE_MODULES[engine_key]
                data = run_one(engine_key, module, row_name, r1, r2,
                               args.budget, args.mrl, args.cpu, tmp_dir,
                               args.timeout)
                data["rep"] = rep
                runs.append(data)
                print(f"  [{row_name}] rep {rep} {engine_key:10s} "
                     f"{data['seconds']:8.3f}s  {fmt_rate(data['pops_per_second']):>12s} pops/s  "
                     f"peak {data['peak_rss_gib']:.3f} GiB  "
                     f"solved={data['solved']}"
                     + (f"  widen x{len(data['widen_lines'])}" if data['widen_lines'] else ""))
    wall = time.time() - t_start
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    # ---------------------------------------------------------- aggregation
    per_row_engine = {}
    for r in runs:
        per_row_engine.setdefault((r["row"], r["engine_key"]), []).append(r)

    aggregate = {}
    mismatches = []
    for row_name, _, _ in rows:
        row_agg = {}
        fingerprints = {}
        for engine_key in engine_keys:
            recs = per_row_engine.get((row_name, engine_key), [])
            if not recs:
                continue
            pops = [r["pops_per_second"] for r in recs]
            rss = [r["peak_rss_gib"] for r in recs]
            fps = sorted(set(r["fingerprint"] for r in recs))
            fingerprints[engine_key] = fps
            if len(fps) > 1:
                mismatches.append(
                    f"{row_name}/{engine_key}: fingerprint NOT stable across "
                    f"{len(recs)} reps ({len(fps)} distinct values) -- the "
                    f"search is not deterministic under this harness")
            row_agg[engine_key] = {
                "median_pops_per_second": median(pops),
                "min_pops_per_second": min(pops),
                "max_pops_per_second": max(pops),
                "median_peak_rss_gib": median(rss),
                "min_peak_rss_gib": min(rss),
                "max_peak_rss_gib": max(rss),
                "bytes_per_state": recs[0]["bytes_per_state"],
                "bytes_reserved": recs[0]["bytes_reserved"],
                "solved": recs[0]["solved"],
                "fingerprint": fps[0] if len(fps) == 1 else fps,
            }
        ref = ("baseline" if "baseline" in row_agg
               else "frozen" if "frozen" in row_agg
               else "current" if "current" in row_agg else None)
        if ref is not None and "candidate" in row_agg:
            row_agg["ratio_candidate_over_baseline_median_pops_per_second"] = (
                row_agg["candidate"]["median_pops_per_second"]
                / row_agg[ref]["median_pops_per_second"])
            row_agg["ratio_reference_engine"] = ref
        if len(fingerprints) > 1:
            all_fp_sets = list(fingerprints.values())
            if any(s != all_fp_sets[0] for s in all_fp_sets[1:]):
                mismatches.append(
                    f"{row_name}: engines disagree -- fingerprints "
                    f"{fingerprints} (candidate is NOT reproducing the same "
                    f"search as baseline on this row)")
        aggregate[row_name] = row_agg

    # ---------------------------------------------------------------- print
    print()
    print(f"wall clock: {wall:.1f}s for {len(runs)} subprocess measurements")
    print()
    header = f"{'row':10s} {'engine':10s} {'median pops/s':>16s} {'min':>16s} {'max':>16s} {'peak RSS GiB':>14s} {'B/state':>9s}"
    print(header)
    print("-" * len(header))
    for row_name, _, _ in rows:
        row_agg = aggregate[row_name]
        for engine_key in engine_keys:
            if engine_key not in row_agg:
                continue
            e = row_agg[engine_key]
            print(f"{row_name:10s} {engine_key:10s} "
                 f"{fmt_rate(e['median_pops_per_second']):>16s} "
                 f"{fmt_rate(e['min_pops_per_second']):>16s} "
                 f"{fmt_rate(e['max_pops_per_second']):>16s} "
                 f"{e['median_peak_rss_gib']:>14.3f} "
                 f"{e['bytes_per_state']:>9.1f}")
        if "ratio_candidate_over_baseline_median_pops_per_second" in row_agg:
            ratio = row_agg["ratio_candidate_over_baseline_median_pops_per_second"]
            print(f"{'':10s} {'ratio':10s} {ratio:>16.4f}  (candidate / "
                  f"{row_agg['ratio_reference_engine']}, median pops/s)")
    print()

    if mismatches:
        print("=" * 70)
        print("FINGERPRINT MISMATCH -- the two engines are NOT producing the")
        print("same search on every row. Do not trust the speed comparison")
        print("above until this is resolved:")
        for m in mismatches:
            print(f"  - {m}")
        print("=" * 70)
    else:
        print("record fingerprints agree on every row / every rep: the two "
             "engines are searching identically, so the timing numbers above "
             "compare like for like.")

    out_obj = {
        "args": vars(args),
        "wall_seconds": wall,
        "runs": runs,
        "aggregate": aggregate,
        "fingerprint_mismatches": mismatches,
    }
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out_obj, f, indent=2)
        print(f"\nwrote {args.out}")

    return 1 if mismatches else 0


def build_arg_parser():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--runner", action="store_true", help=argparse.SUPPRESS)
    return ap


def main():
    # Dispatch on --runner without disturbing the main parser's --help text.
    pre = build_arg_parser()
    pre_args, _ = pre.parse_known_args()
    if pre_args.runner:
        rp = argparse.ArgumentParser()
        rp.add_argument("--runner", action="store_true")
        rp.add_argument("--engine-module", required=True)
        rp.add_argument("--row", required=True)
        rp.add_argument("--r1", required=True)
        rp.add_argument("--r2", required=True)
        rp.add_argument("--budget", type=int, required=True)
        rp.add_argument("--mrl", type=int, required=True)
        rp.add_argument("--cpu", type=int, required=True)
        rp.add_argument("--config", required=True)
        rp.add_argument("--result-path", required=True)
        args = rp.parse_args()
        cmd_runner(args)
        return 0
    return main_bench()


if __name__ == "__main__":
    sys.exit(main())
