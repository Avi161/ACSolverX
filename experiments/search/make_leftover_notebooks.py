"""Write the two AC19-leftover Colab notebooks from one template.

    PYTHONPATH=. python3 -m experiments.search.make_leftover_notebooks

The two notebooks are one template under two configs -- same SETUP, same RUN,
same REPORT, and only the CONFIG cell differs (arm, row list, Drive dir). They
are separate files rather than one notebook with two sections because that is
how this experiment has always been run: the 100k pass that produced the leftover
counts was four parallel Colabs, one arm each, with separate Drive directories
("can run together" -- HARD_RESIDUAL_100k.md). At a 1M budget that parallelism is
worth more, not less, and the arms have very different memory profiles, so
pinning them to one runtime would size both by the greedier one.

Generating them keeps the shared three-quarters from drifting apart by hand;
``tests/test_leftovers_1m.py`` re-runs this and asserts the committed notebooks
are byte-identical to its output.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

ROOT = _ROOT
NB_DIR = os.path.join(ROOT, "experiments", "notebooks", "leftovers_1m")
DEFAULT_BRANCH = "claude/ac19-leftover-solver-notebook-6yan6d"


def current_branch(default=DEFAULT_BRANCH):
    """The branch this file is on -- the notebook must clone the code it ships with."""
    try:
        p = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return default
    name = p.stdout.strip()
    return default if (p.returncode != 0 or not name or name == "HEAD") else name


ARM_CELLS = {
    "greedy": '''# ===== AC19 LEFTOVERS @ 1M -- GREEDY -- CONFIG (edit ONLY this cell) =========
# Runtime: **CPU, High-RAM**. Nothing here touches a GPU; the search is numpy +
# numba on one core per worker, and RAM is the binding constraint, not cores.
#
# THE QUESTION
#   The ~70k AC19 aut-min screen ran this arm (total-length ordering) at 1,000,
#   then 10,000, then escalated its 831 misses to 100,000. 222 orbits survived
#   even that. This notebook asks how many of those 222 a 1,000,000-node budget
#   solves.
#
# THE ROW LIST IS THE REAL ONE
#   results/heuristic_search/ac19_autmin_screen/unsolved_100k_baseline.csv -- 222
#   rows, presentations inline, read off the 100k jsonl that ships beside it
#   (609/831 solved, 222 not). No derivation and no join; the tests re-derive the
#   CSV from that jsonl rather than trusting it.
#
#   222 vs the 221 in RESULTS.md: RESULTS.md scores over the 70,723 orbits both
#   arms searched at 10k, and exactly one greedy failure (ac19_33435) sits outside
#   that intersection because s20_mk2 never searched it. 222 = orbits this arm
#   actually failed; 221 = the common denominator. Set COMMON_DENOMINATOR = True
#   to drop that one row and quote 221 instead.

REPO_URL = "https://github.com/Avi161/ACSolverX.git"
BRANCH   = "%(branch)s"
REPO_DIR = "ACSolverX"
CLONE       = True
UPDATE_REPO = True           # git reset --hard, so Restart -> Run All pulls latest
MOUNT_DRIVE = True           # jsonl mirrored to Drive; the run resumes from it

ARM = "greedy"               # total-length ordering -- the screen's `baseline` arm

# False -> all 222 rows this arm failed. True -> the 221 on the common denominator.
COMMON_DENOMINATOR = False

NODE_BUDGET = 1_000_000      # the lift this notebook exists to run
MAX_RELATOR_LENGTH = 48      # the cap every wave of this screen has used

# "auto" sizes the pool by FREE RAM, not by core count. Measured on ac19_420 from
# this list: 2.71 GB by 200,000 pops at ~1050 nodes/s, growing with what the
# search DISCOVERS rather than what it pops, so a 1M-node search wants ~16 GB.
# On a 51 GB high-RAM runtime that is 3 workers. Oversubscribing does not make a
# slow run, it makes an OOM that loses the session.
N_WORKERS = "auto"
RESUME    = True             # rows already in the jsonl are skipped

# EXPECT A LONG RUN, AND EXPECT TO RESUME IT. A row that uses its whole budget
# takes ~16 min, so 222 of them at 3 workers is on the order of 20 hours. Colab
# will disconnect first -- that is fine and planned for: reopen, Run All, and
# RESUME picks up from the Drive-mirrored jsonl. Nothing is recomputed.

LOCAL_OUT_DIR = "results/heuristic_search/leftovers_1m"
DRIVE_OUT_DIR = "/content/drive/MyDrive/acsolverx/leftovers_1m_greedy"

# Proves the whole pipeline in about a minute -- clone, import, search, jsonl,
# resume, report -- at a budget that measures nothing, into a separate _smoke
# directory so its rows can never be mistaken for the real run's. Run it once,
# read the table, then set False.
SMOKE_RUN = True

print("config loaded:", ARM)
''',
    "s20_mk2": '''# ===== AC19 LEFTOVERS @ 1M -- S20_MK2 -- CONFIG (edit ONLY this cell) ========
# Runtime: **CPU, High-RAM**. Nothing here touches a GPU; the search is numpy +
# numba on one core per worker, and RAM is the binding constraint, not cores.
#
# THE QUESTION
#   The ~70k AC19 aut-min screen ran this arm (priority = L + 20*S + 2*MK) at
#   1,000, then 10,000, then escalated its 259 misses to 100,000. 39 orbits
#   survived even that. This notebook asks how many of those 39 a 1,000,000-node
#   budget solves.
#
# THE ROW LIST IS THE REAL ONE
#   results/heuristic_search/ac19_autmin_screen/unsolved_100k_s20_mk2.csv -- 39
#   rows, presentations inline, read off the 100k jsonl that ships beside it
#   (220/259 solved, 39 not). No derivation and no join; the tests re-derive the
#   CSV from that jsonl rather than trusting it.
#
#   These 39 are a strict subset of the greedy arm's 222: s20_mk2 recovers 182 of
#   length's failures and loses none the other way. They are the genuinely hard
#   tail -- both orderings fail on all 39.
#
#   The arm is s20_mk2 and nothing else. The former `RECOMMENDED` vector
#   (L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb) was withdrawn as overfit;
#   run_leftovers_1m refuses it by name.

REPO_URL = "https://github.com/Avi161/ACSolverX.git"
BRANCH   = "%(branch)s"
REPO_DIR = "ACSolverX"
CLONE       = True
UPDATE_REPO = True           # git reset --hard, so Restart -> Run All pulls latest
MOUNT_DRIVE = True           # jsonl mirrored to Drive; the run resumes from it

ARM = "s20_mk2"              # priority(r1, r2) = L + 20*S + 2*MK

# No row of this arm sits outside the 70,723-orbit intersection, so this changes
# nothing here; it is kept so both notebooks read the same below cell 0.
COMMON_DENOMINATOR = False

NODE_BUDGET = 1_000_000      # the lift this notebook exists to run
MAX_RELATOR_LENGTH = 48      # the cap every wave of this screen has used

# "auto" sizes the pool by FREE RAM, not by core count. THIS ARM IS THE HUNGRY
# ONE and the runtime must be High-RAM.
#
# It does NOT run heuristics.greedy_search_h: that solver keeps a parent map and a
# move map keyed by string tuples so it can rebuild certificates, and it measured
# 1.64 GB by 12,288 pops on a row from this screen -- past 100 GB at 1M. It runs
# LeanHeuristicSolver instead, the same memory-lean solver the greedy arm uses
# with the heap ordering swapped. Measured on ac19_7284 from this list: 1.17 GB by
# 25,600 pops at ~330 nodes/s, so ~46 GB at 1M.
#
# That is still more than the greedy arm's ~16 GB, because the orderings go
# different places -- s20_mk2 prefers thicker blocks, so it queues longer relators
# and a wider frontier. On a 51 GB high-RAM runtime it fits ONE worker. A standard
# (non-high-RAM) runtime has ~13 GB and cannot run this arm at 1M at all; SETUP
# prints the worker count it resolved, so check that line before walking away.
# 39 rows at ~50 min each is on the order of a day and a half, resumable.
N_WORKERS = "auto"
RESUME    = True             # rows already in the jsonl are skipped

LOCAL_OUT_DIR = "results/heuristic_search/leftovers_1m"
DRIVE_OUT_DIR = "/content/drive/MyDrive/acsolverx/leftovers_1m_s20_mk2"

# Proves the whole pipeline in about a minute -- clone, import, search, jsonl,
# resume, report -- at a budget that measures nothing, into a separate _smoke
# directory so its rows can never be mistaken for the real run's. Run it once,
# read the table, then set False.
SMOKE_RUN = True

print("config loaded:", ARM)
''',
}

SETUP = '''# ==================== SETUP (clone / pull / install / mount) ==============
import os, sys, subprocess, importlib

def sh(cmd):
    print("$", cmd)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.stdout: print(p.stdout[-2000:])
    if p.returncode != 0 and p.stderr: print("STDERR:", p.stderr[-2000:])

try:
    import google.colab  # noqa
    IN_COLAB = True
except Exception:
    IN_COLAB = False
print("Colab:", IN_COLAB)

if IN_COLAB:
    BASE = "/content"
    os.chdir(BASE)                       # anchor so re-runs never nest the clone
    if not os.path.isdir(REPO_DIR):
        if CLONE:
            sh(f"git clone --branch {BRANCH} --depth 1 {REPO_URL} {REPO_DIR}")
    elif UPDATE_REPO:
        sh(f"cd {REPO_DIR} && git fetch --depth 1 origin {BRANCH} && git reset --hard FETCH_HEAD")
    sh(f"cd {REPO_DIR} && git log -1 --oneline")
    # numpy ships with the Colab image; numba is the one thing the solver adds.
    # Nothing here needs torch or jax -- this is a CPU search, not a policy.
    sh("pip -q install numba")
    if MOUNT_DRIVE:
        from google.colab import drive
        drive.mount("/content/drive")
        os.makedirs(DRIVE_OUT_DIR, exist_ok=True)
    REPO_ROOT = os.path.join(BASE, REPO_DIR)
else:
    # local: walk up from cwd to the repo root (dir holding experiments/ + data/)
    REPO_ROOT = os.getcwd()
    while REPO_ROOT != "/" and not (
        os.path.isdir(os.path.join(REPO_ROOT, "experiments"))
        and os.path.isdir(os.path.join(REPO_ROOT, "data"))
    ):
        REPO_ROOT = os.path.dirname(REPO_ROOT)

# run from repo root so "results/..." and "import experiments..." resolve
os.chdir(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
print("repo root:", REPO_ROOT)

# SETUP's `git reset --hard` rewrites the .py files on disk, but Python keeps the
# OLD module objects in sys.modules for the life of the runtime -- so the RUN
# cell would silently reuse stale code (a pull is NOT a reload). Drop them so the
# next import reads what SETUP just fetched.
for _m in [m for m in sys.modules if m == "experiments" or m.startswith("experiments.")]:
    del sys.modules[_m]
importlib.invalidate_caches()

from experiments.search.run_leftovers_1m import (
    ARMS, load_rows, report, resolve_workers, run_arm, unsolved_at_100k)

# Warm the numba kernels here rather than inside a worker: the first call into
# each @njit function compiles it (~30-60 s), and paying that once in the parent
# keeps it out of every worker's first row and out of the throughput estimate.
_spec = ARMS[ARM]
_ = _spec["run"]("xyx", "yx", 20, 32)

_rows, _csv = load_rows(ARM, common_denominator=COMMON_DENOMINATOR)

# The row list is only trustworthy if it is what the 100k run actually left
# behind, so check it against that jsonl here rather than after a day of search.
_derived = set(unsolved_at_100k(ARM))
_have = {r["name"] for r in _rows}
assert _have <= _derived, sorted(_have - _derived)[:5]
assert len(_derived) == _spec["n_rows"], (len(_derived), _spec["n_rows"])

_nw, _gb = resolve_workers(ARM, N_WORKERS)
print(f"arm={ARM}  rows={len(_rows)}  from {_csv}")
print(f"     verified against the 100k jsonl ({len(_derived)} unsolved there)")
print(f"workers={_nw} (~{_gb:.0f} GB/search reserved)  budget={NODE_BUDGET:,}  "
      f"cap={MAX_RELATOR_LENGTH}")
if IN_COLAB and _nw < 2:
    print("NOTE: only one worker fits in this runtime's free RAM. "
          "Runtime -> Change runtime type -> High-RAM before the real run.")
print("kernels warm -- setup done")
'''

RUN = '''# ==================== RUN =================================================
# Appends to a local jsonl and mirrors the WHOLE file to Drive as it goes -- never
# appends to a mount, which is what silently truncates a jsonl when a Colab
# session drops. RESUME reads that jsonl back, so Restart -> Run All continues
# instead of restarting; rows already on disk are skipped. Expect to use this.
import os

OUT_DIR = os.path.join(REPO_ROOT, LOCAL_OUT_DIR)
MIRROR  = DRIVE_OUT_DIR if (IN_COLAB and MOUNT_DRIVE) else None

budget, limit = NODE_BUDGET, None
if SMOKE_RUN:
    # Same code path, same arm, same row list -- only smaller. It proves the
    # clone, the import, the search, the jsonl, the resume and the report; it
    # measures nothing, and its rows go to a separate directory so they can never
    # be mistaken for the real run's.
    budget, limit = 2_000, 2
    OUT_DIR = OUT_DIR + "_smoke"
    MIRROR = None
    print(f"SMOKE_RUN: {limit} rows at budget {budget:,} -> {OUT_DIR}")
else:
    print(f"FULL RUN: budget {budget:,} over {len(_rows)} rows; "
          f"rows already in the jsonl are skipped")

out = run_arm(
    ARM, OUT_DIR,
    budget=budget,
    mrl=MAX_RELATOR_LENGTH,
    n_workers=N_WORKERS,
    resume=RESUME,
    common_denominator=COMMON_DENOMINATOR,
    limit=limit,
    mirror_dir=MIRROR,
)
print("jsonl:", out)
'''

REPORT = '''# ==================== REPORT =============================================
# A fourth cell because the table has a different lifetime from the run: it reads
# the jsonl off disk, so re-printing it is free and never re-searches, and it
# still prints something readable while the run is only part-done. Run it against
# a partial jsonl as often as you like.
#
# It answers the question the notebook exists for -- how many of this arm's 100k
# leftovers the 1,000,000-node budget solved -- plus the anytime curve at 250k and
# 500k, which costs nothing: a row solved after N pops was solved at every budget
# above N, so one search already answers all of them.
#
# It also prints a loud warning if any row comes back solved at or below 100,000
# nodes. Every row here failed at 100,000 in the run that built the list, so that
# cannot happen unless the search being run is not that search -- wrong arm, wrong
# cap, or a row list from somewhere else.
#
# Two id lists are written beside the jsonl:
#   solved_at_1m_<arm>.txt        what the extra budget bought
#   still_unsolved_1m_<arm>.txt   what survives even 1,000,000 nodes
c = report(ARM, OUT_DIR, budget=budget, mrl=MAX_RELATOR_LENGTH,
           common_denominator=COMMON_DENOMINATOR)
'''


def build(arm, branch=None):
    branch = branch or current_branch()
    cells = [ARM_CELLS[arm] % {"branch": branch}, SETUP, RUN, REPORT]
    return {
        "cells": [{"cell_type": "code", "execution_count": None, "metadata": {},
                   "outputs": [], "source": src.splitlines(keepends=True)}
                  for src in cells],
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (ipykernel)",
                           "language": "python", "name": "python3"},
            "language_info": {"codemirror_mode": {"name": "ipython", "version": 3},
                              "file_extension": ".py",
                              "mimetype": "text/x-python", "name": "python",
                              "nbconvert_exporter": "python",
                              "pygments_lexer": "ipython3", "version": "3.12.13"},
            "accelerator": "None",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def path_for(arm):
    return os.path.join(NB_DIR, f"ac19_leftovers_1m_{arm}.ipynb")


def render(arm, branch=None):
    return json.dumps(build(arm, branch), indent=1) + "\n"


def main():
    os.makedirs(NB_DIR, exist_ok=True)
    for arm in ARM_CELLS:
        p = path_for(arm)
        with open(p, "w") as f:
            f.write(render(arm))
        print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
