"""CLI: run Prover9 on Andrews-Curtis triviality instances (ESCAPE_PLAN.md T6 pilot).

Encodes each (name, r1, r2) presentation via ``encode.build_ig_problem`` (Lisitsa
IG scheme), runs ``/opt/homebrew/bin/prover9 -f`` under a per-instance timeout,
classifies the outcome, and appends one jsonl row per instance to
``results/stable_ac/atp/<--out or default>.jsonl``. The full Prover9 stdout
(proof object included, when found) is saved next to it under
``results/stable_ac/atp/runs/<name>.{p9,out}``.

CPU only; this module never touches the numba solver stack. From the repo root::

    .venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 \\
        --pres ms0 YYXyx Yx --timeout-s 60

    .venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 \\
        --ms640 0 --timeout-s 60

    .venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 \\
        --pres ak3 xxxYYYY xyxYXY --timeout-s 600

    .venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 \\
        --csv data/ms_unsolved_reps/aca_124.csv --csv-smallest 3 --timeout-s 600

IMPORTANT (ESCAPE_PLAN.md "Advisor reconciliation" item 1): a Prover9
"THEOREM PROVED" here is a LEAD, never a solve claim. The proof object is a
first-order refutation trace, not yet a Definition 2.1 move sequence -- turning
it into one (and replaying it through ``verify_results.py``) is a separate,
not-yet-built step. See README.md.
"""

import argparse
import ast
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

from experiments.stable_ac.atp.encode import ENCODING, build_ig_problem

PROVER9_BIN = "/opt/homebrew/bin/prover9"

# Integer encoding of data/ms640_solved.txt, matching experiments/run_baseline.py:
# 1=x, -1=X, 2=y, -2=Y, 0=pad.
_INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}

# Prover9's own assign(max_seconds, ...) is set a few seconds below the requested
# wall budget so it always self-terminates (exit code 4, clean SEARCH FAILED
# report) comfortably before the outer subprocess-level kill -- avoids ever
# hard-killing Prover9 mid-write of its own statistics/proof output.
_MAX_SECONDS_RESERVE_S = 5


def find_repo_root(start):
    """Walk up until a dir holds both experiments/ and data/ (repo rule)."""
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root (experiments/ + data/) above {start}")
        d = parent


REPO_ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))


def _git_commit():
    """HEAD of the checkout this module runs from; None outside a git repo.

    Provenance only, stamped into every row -- NOT part of any resume identity.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def load_ms640_row(idx, path=None):
    """Decode row ``idx`` of data/ms640_solved.txt into (r1, r2) strings."""
    path = path or os.path.join(REPO_ROOT, "data", "ms640_solved.txt")
    with open(path) as f:
        for i, line in enumerate(f):
            if i != idx:
                continue
            vals = ast.literal_eval(line.strip())
            half = len(vals) // 2
            r1 = "".join(_INT_TO_CHAR[v] for v in vals[:half] if v != 0)
            r2 = "".join(_INT_TO_CHAR[v] for v in vals[half:] if v != 0)
            return r1, r2
    raise IndexError(f"row {idx} not found in {path}")


def load_csv_smallest(path, n):
    """Load a name,r1,r2[,...] CSV and return the n rows with smallest |r1|+|r2|."""
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            r1, r2 = row["r1"], row["r2"]
            rows.append((row["name"], r1, r2, len(r1) + len(r2)))
    rows.sort(key=lambda t: t[3])
    return [(name, r1, r2) for name, r1, r2, _ in rows[:n]]


def _decode(x):
    if x is None:
        return ""
    if isinstance(x, bytes):
        return x.decode(errors="replace")
    return x


def _append_jsonl(path, row):
    """Append one JSON line, single write() syscall -- POSIX-atomic under
    O_APPEND for a line this short, safe for concurrent instances writing the
    same file (each pilot instance is an independent process)."""
    line = (json.dumps(row) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def run_one(name, r1, r2, timeout_s, work_dir):
    """Encode + run Prover9 on one presentation; return the jsonl row dict."""
    prover9_max_seconds = max(1, int(timeout_s) - _MAX_SECONDS_RESERVE_S)
    problem_text = build_ig_problem(name, r1, r2, timeout_s=prover9_max_seconds)

    os.makedirs(work_dir, exist_ok=True)
    in_path = os.path.join(work_dir, f"{name}.p9")
    out_path = os.path.join(work_dir, f"{name}.out")
    with open(in_path, "w") as f:
        f.write(problem_text)

    started = time.time()
    killed = False
    try:
        proc = subprocess.run(
            [PROVER9_BIN, "-f", in_path],
            capture_output=True, text=True, timeout=timeout_s,
        )
        exit_code = proc.returncode
        stdout = proc.stdout
    except subprocess.TimeoutExpired as e:
        exit_code = None
        stdout = _decode(e.stdout)
        killed = True
    wall_s = time.time() - started

    with open(out_path, "w") as f:
        f.write(stdout)

    proved = "THEOREM PROVED" in stdout
    if proved:
        status = "proved"
    elif killed:
        status = "timeout"
    elif exit_code == 4:
        status = "timeout"          # Prover9's own max_seconds exhausted
    elif exit_code == 2:
        status = "exhausted"        # sos empty: search space exhausted, no proof
    else:
        status = "error"

    return {
        "name": name,
        "r1": r1,
        "r2": r2,
        "encoding": ENCODING,
        "timeout_s": timeout_s,
        "prover9_max_seconds": prover9_max_seconds,
        "status": status,
        "wall_s": round(wall_s, 3),
        "prover9_exit": exit_code,
        "prover9_killed": killed,
        "problem_file": os.path.relpath(in_path, REPO_ROOT),
        "output_file": os.path.relpath(out_path, REPO_ROOT),
        "proof_file": os.path.relpath(out_path, REPO_ROOT) if proved else None,
        "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
        "git_commit": _git_commit(),
    }


def build_arg_parser():
    p = argparse.ArgumentParser(
        description="Run Prover9 on Andrews-Curtis triviality instances "
                     "(Lisitsa IG encoding, ESCAPE_PLAN.md T6 pilot).")
    p.add_argument("--pres", nargs=3, action="append", default=[],
                    metavar=("NAME", "R1", "R2"),
                    help="one presentation, repeatable")
    p.add_argument("--ms640", type=int, action="append", default=[],
                    metavar="IDX", help="row index into data/ms640_solved.txt, "
                    "repeatable; named ms<IDX>")
    p.add_argument("--ms640-path", default=None)
    p.add_argument("--csv", default=None,
                    help="name,r1,r2 CSV (e.g. data/ms_unsolved_reps/aca_124.csv)")
    p.add_argument("--csv-smallest", type=int, default=None,
                    help="pick the N smallest |r1|+|r2| rows from --csv "
                         "(default: all rows)")
    p.add_argument("--timeout-s", type=int, default=600,
                    help="per-instance wall-clock timeout in seconds (default 600)")
    p.add_argument("--out", default=None,
                    help="jsonl output path (default "
                         "results/stable_ac/atp/prover9_pilot.jsonl)")
    p.add_argument("--work-dir", default=None,
                    help="dir for .p9/.out files (default "
                         "results/stable_ac/atp/runs)")
    p.add_argument("--skip-existing", action="store_true",
                    help="skip a (name, encoding) already present in --out")
    return p


def _collect_presentations(args):
    presentations = list(args.pres)
    for idx in args.ms640:
        r1, r2 = load_ms640_row(idx, args.ms640_path)
        presentations.append((f"ms{idx}", r1, r2))
    if args.csv:
        n = args.csv_smallest if args.csv_smallest is not None else 10 ** 9
        presentations.extend(load_csv_smallest(args.csv, n))
    return presentations


def _already_done(out_path):
    done = set()
    if not os.path.exists(out_path):
        return done
    with open(out_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((row.get("name"), row.get("encoding")))
    return done


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    presentations = _collect_presentations(args)
    if not presentations:
        build_arg_parser().error("no presentations given: use --pres / --ms640 / --csv")

    out_path = args.out or os.path.join(
        REPO_ROOT, "results", "stable_ac", "atp", "prover9_pilot.jsonl")
    work_dir = args.work_dir or os.path.join(
        REPO_ROOT, "results", "stable_ac", "atp", "runs")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    skip = _already_done(out_path) if args.skip_existing else set()

    for name, r1, r2 in presentations:
        if (name, ENCODING) in skip:
            print(f"[{name}] skip (already in {out_path})", flush=True)
            continue
        print(f"[{name}] r1={r1} r2={r2} timeout={args.timeout_s}s ...", flush=True)
        row = run_one(name, r1, r2, args.timeout_s, work_dir)
        print(f"[{name}] status={row['status']} wall_s={row['wall_s']} "
              f"exit={row['prover9_exit']}", flush=True)
        _append_jsonl(out_path, row)

    return 0


if __name__ == "__main__":
    sys.exit(main())
