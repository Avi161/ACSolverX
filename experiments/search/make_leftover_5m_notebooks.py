"""Write the five AC19-leftover 5M notebooks (four greedy shards + s20_mk2).

    PYTHONPATH=. python3 -m experiments.search.make_leftover_5m_notebooks

One notebook per machine, five machines: the greedy arm's 88 rows stride-split
across four shard notebooks (CHUNKS=4, CHUNK_INDEX=k -> rows[k-1::4],
interleaved so difficulty spreads evenly; disjoint, union = 88) and the
s20_mk2 arm's 14 as the fifth. Every row runs crash-isolated -- see the Edge
Compact guards in ``run_leftovers_5m`` -- so a CPU-limit kill or a RAM
overload becomes a recorded, retried row instead of a dead session.

Cell contract, per the run plan: CONFIG, SETUP (clone/pull — Colab or a plain
GCE VM — Drive mount where available, ``ENGINE="hcompact"`` + ``HIGH_SPEEDUP``
asserted, row list re-derived from the 1M jsonl), SMOKE (always runs, tiny,
and GATES the long job — any failure stops Run All before MAIN), MAIN (the 5M
run + merged report).

``tests/test_leftovers_5m.py`` asserts the committed files are byte-identical
to this generator's output, and that MAIN cannot run without SMOKE.
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
NB_DIR = os.path.join(ROOT, "experiments", "notebooks", "leftovers_5m")
DEFAULT_BRANCH = "claude/ac19-leftover-solver-notebook-6yan6d"

# (filename stem, ARM, CHUNKS, CHUNK_INDEX)
VARIANTS = tuple(
    [(f"ac19_leftovers_5m_greedy_c{k}of4", "greedy", 4, k) for k in (1, 2, 3, 4)]
    + [("ac19_leftovers_5m_s20_mk2", "s20_mk2", 1, 1)])


def current_branch(default=DEFAULT_BRANCH):
    try:
        p = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return default
    name = p.stdout.strip()
    return default if (p.returncode != 0 or not name or name == "HEAD") else name


_ARM_BLURB = {
    "greedy": '''# THE QUESTION
#   88 orbits survived the greedy (total-length) arm's 1,000,000-node pass.
#   This notebook runs shard %(chunk_index)d of 4 -- rows [%(k0)d::4] of the
#   list, 22 rows -- at 5,000,000 nodes on its own machine. The four shard
#   notebooks are disjoint and together cover all 88; run them as four
#   parallel machines, with s20_mk2 as the fifth.''',
    "s20_mk2": '''# THE QUESTION
#   14 orbits survived the s20_mk2 (L + 20*S + 2*MK) arm's 1,000,000-node pass
#   -- the tail both orderings fail. This notebook runs all 14 at 5,000,000
#   nodes on its own machine.''',
}

CONFIG = '''# ===== AC19 LEFTOVERS @ 5M -- %(title)s -- CONFIG (edit ONLY this cell) =====
# Runtime: CPU, any machine type. One search runs at a time -- it is a
# ~25-30 GB memory event, not a compute one, so core count buys nothing here;
# what the machine needs is RAM headroom (see SETUP's check).
#
%(blurb)s
#
# THE ROW LIST IS THE REAL ONE
#   results/heuristic_search/ac19_autmin_screen/%(csv)s -- read off the 1M
#   jsonl (solved == false). SETUP re-derives it from that jsonl before
#   anything searches.
#
# EXPECT DAYS, AND EXPECT TO RESUME
#   ~500-800 nodes/s single-worker means a full-budget row takes ~2-3 h. The
#   jsonl is appended locally and mirrored whole-file to Drive (when mounted);
#   RESUME skips every finished row, and a wiped machine reseeds from the
#   mirror. Re-running this notebook never repeats finished work.

REPO_URL = "https://github.com/Avi161/ACSolverX.git"
BRANCH   = "%(branch)s"
REPO_DIR = "ACSolverX"
CLONE       = True
UPDATE_REPO = True           # git reset --hard, so a re-run pulls the latest push
MOUNT_DRIVE = True           # Colab only; a plain VM runs without a mirror

ARM         = "%(arm)s"
CHUNKS      = %(chunks)d
CHUNK_INDEX = %(chunk_index)d

NODE_BUDGET = 5_000_000      # the lift this notebook exists to run
MAX_RELATOR_LENGTH = 64      # the 5M stage runs a wider corridor than the 1M wave (48)

N_WORKERS = "auto"           # sizes by free RAM; resolves 1 at this budget
RESUME    = True             # rows already in the jsonl are skipped
RUN_MAIN  = True             # False = smoke only; MAIN also never starts if SMOKE failed
MAIN_LIMIT = None            # first-N rows only (testing); None = the whole shard
ROW_TIMEOUT_SECS = None      # per-row kill switch (crash-guarded); None = off

LOCAL_OUT_DIR = "results/heuristic_search/leftovers_5m"
DRIVE_OUT_DIR = "/content/drive/MyDrive/acsolverx/leftovers_5m_%(drive_tag)s"

print("config loaded:", ARM, "-- combined list, budget", f"{NODE_BUDGET:,}")
'''

SETUP = '''# ==================== SETUP (clone / pull / mount / engine) ================
# ENGINE=hcompact is required for HIGH_SPEEDUP: the packed arena (FNV-hashed
# nibble rows, open-addressing int32 table, all numba, ~79 B/state) is the
# production engine every wave of this screen ran. The Python solvers in
# experiments/search/ are its test oracle and fallback, NOT the fast path --
# at 5M they would OOM, so SETUP refuses to proceed without the engine.
ENGINE       = "hcompact"
HIGH_SPEEDUP = True
assert ENGINE == "hcompact", "ENGINE=hcompact required for HIGH_SPEEDUP"

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

def _find_root(start):
    d = start
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    return None

# Works on Colab AND on a plain GCE VM's Jupyter: an existing checkout above
# the cwd is used as-is; otherwise the repo is cloned under BASE.
BASE = "/content" if IN_COLAB else os.path.expanduser("~")
REPO_ROOT = None if IN_COLAB else _find_root(os.getcwd())
if REPO_ROOT is None:
    os.chdir(BASE)                       # anchor so re-runs never nest the clone
    if not os.path.isdir(REPO_DIR):
        if CLONE:
            sh(f"git clone --branch {BRANCH} --depth 1 {REPO_URL} {REPO_DIR}")
    elif UPDATE_REPO:
        sh(f"cd {REPO_DIR} && git fetch --depth 1 origin {BRANCH} && git reset --hard FETCH_HEAD")
    sh(f"cd {REPO_DIR} && git log -1 --oneline")
    REPO_ROOT = os.path.join(BASE, REPO_DIR)
sh(f"{sys.executable} -m pip -q install numba")

if IN_COLAB and MOUNT_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    os.makedirs(DRIVE_OUT_DIR, exist_ok=True)

os.chdir(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
print("repo root:", REPO_ROOT)

# a pull is NOT a reload -- drop stale module objects before importing
for _m in [m for m in sys.modules if m == "experiments" or m.startswith("experiments.")]:
    del sys.modules[_m]
importlib.invalidate_caches()

from experiments.search.run_leftovers_1m import ARMS, HAVE_HCOMPACT
from experiments.search.run_leftovers_5m import (
    load_rows_5m, out_path_5m, report_5m, resolve_workers, run_arm_5m,
    stride_chunk, unsolved_at_1m)

assert HAVE_HCOMPACT, ("packed-arena engine missing -- wrong branch or a stale "
                       "clone; ENGINE=hcompact is required for HIGH_SPEEDUP and "
                       "a 5M run on the Python fallback would OOM")

# warm the numba kernels in the parent, not in a worker's first row -- and
# confirm the arm actually CALLS the engine (no silent Python fallback): the
# fast path must be the one that runs, not merely the one that imports
import experiments.search.run_leftovers_1m as _r1m
_calls = []
_real = _r1m.greedy_search_hcompact
_r1m.greedy_search_hcompact = lambda *a, **k: (_calls.append(1), _real(*a, **k))[1]
try:
    _ = ARMS[ARM]["run"]("xyx", "yx", 20, 32)
finally:
    _r1m.greedy_search_hcompact = _real
assert _calls, "arm did not call greedy_search_hcompact -- silent fallback; stop"

_rows, _csv = load_rows_5m(ARM)
_derived = unsolved_at_1m(ARM)
assert sorted(r["name"] for r in _rows) == _derived, "row list drifted from the 1M jsonl"

_nw, _gb = resolve_workers(ARM, N_WORKERS, budget=NODE_BUDGET,
                           mrl=MAX_RELATOR_LENGTH)
print(f"arm={ARM}  rows={len(_rows)}  from {_csv}")
print(f"     verified against the 1M jsonl ({len(_derived)} unsolved there)")
print(f"ENGINE={ENGINE}  HIGH_SPEEDUP={HIGH_SPEEDUP}  workers={_nw} "
      f"(~{_gb:.1f} GB/search reserved)  budget={NODE_BUDGET:,}  cap={MAX_RELATOR_LENGTH}")

# RAM reality check, whatever the machine: a full-budget 5M row touches ~25-30 GB.
try:
    with open("/proc/meminfo") as _f:
        _avail = next(int(l.split()[1]) / 1048576 for l in _f
                      if l.startswith("MemAvailable:"))
    print(f"free RAM: {_avail:.1f} GB")
    if _avail < 28:
        print("!! WARNING: under ~28 GB free. A full-budget 5M row touches "
              "~25-30 GB and can OOM on this machine hours in; whatever the "
              "machine type, give it >= 32 GB of RAM. The smoke below will "
              "still pass; this is about the LONG job.")
except (OSError, StopIteration):
    pass
print("kernels warm -- setup done")
'''

SMOKE = '''# ==================== SMOKE (always runs; GATES the long job) =============
# 2 rows at 2,000 nodes, fresh every run, into a separate _smoke dir. This cell
# exercises the whole pipeline -- engine, row list, jsonl write, report -- and
# if ANYTHING here raises, Run All stops and MAIN below never starts. That is
# the point: a broken setup costs one minute here instead of a day there.
import os

_SMOKE_DIR = os.path.join(REPO_ROOT, LOCAL_OUT_DIR) + "_smoke"
_smoke_file = out_path_5m(ARM, _SMOKE_DIR, CHUNKS, CHUNK_INDEX,
                          budget=2_000, mrl=MAX_RELATOR_LENGTH)
if os.path.exists(_smoke_file):
    os.remove(_smoke_file)               # fresh: the smoke must actually search

run_arm_5m(ARM, _SMOKE_DIR, chunks=CHUNKS, chunk_index=CHUNK_INDEX,
           budget=2_000, mrl=MAX_RELATOR_LENGTH, n_workers=1, resume=False,
           limit=2, mirror_dir=None)

from experiments.search.run_leftovers_1m import read_rows
_srows = read_rows(_smoke_file)
assert len(_srows) == 2, f"smoke wrote {len(_srows)} rows, expected 2"
assert all(r["arm"] == ARM and r["budget"] == 2_000 for r in _srows), _srows
assert all(0 < r["nodes_explored"] <= 2_000 for r in _srows), _srows

_SMOKE_OK = True
print("SMOKE PASSED -- pipeline verified; MAIN may start")
'''

MAIN = '''# ==================== MAIN (the 5M run; gated by SMOKE) ====================
assert _SMOKE_OK, "smoke did not pass; refusing to start the long job"
import os

OUT_DIR = os.path.join(REPO_ROOT, LOCAL_OUT_DIR)
MIRROR  = DRIVE_OUT_DIR if (IN_COLAB and MOUNT_DRIVE) else None
if MIRROR is None:
    print("note: no Drive on this runtime -- the jsonl lives only on this "
          "machine; copy it off yourself when done (or rsync it periodically).")

if not RUN_MAIN:
    print("RUN_MAIN = False -- smoke only, the long job was not started")
else:
    # Every row runs crash-isolated in its own process (the Edge Compact
    # guards): an OOM, a CPU-limit kill or a timeout becomes a recorded error
    # row that resume retries later -- the session itself never dies with a row.
    out = run_arm_5m(ARM, OUT_DIR, chunks=CHUNKS, chunk_index=CHUNK_INDEX,
                     budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH,
                     n_workers=N_WORKERS, resume=RESUME, limit=MAIN_LIMIT,
                     row_timeout_secs=ROW_TIMEOUT_SECS, mirror_dir=MIRROR)
    print("jsonl:", out)
    c = report_5m(ARM, OUT_DIR, chunks=CHUNKS, budget=NODE_BUDGET,
                  mrl=MAX_RELATOR_LENGTH)
'''


def build(stem, arm, chunks, chunk_index, branch=None):
    branch = branch or current_branch()
    from experiments.search.run_leftovers_5m import SPEC_5M
    cfg = CONFIG % {
        "title": (f"GREEDY c{chunk_index}of{chunks}" if arm == "greedy"
                  else "S20_MK2"),
        "blurb": _ARM_BLURB[arm] % ({"chunk_index": chunk_index,
                                     "k0": chunk_index - 1}
                                    if arm == "greedy" else {}),
        "csv": SPEC_5M[arm]["csv"],
        "branch": branch,
        "arm": arm,
        "chunks": chunks,
        "chunk_index": chunk_index,
        "drive_tag": (f"greedy_c{chunk_index}of{chunks}" if arm == "greedy"
                      else "s20_mk2"),
    }
    cells = [cfg, SETUP, SMOKE, MAIN]
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


def path_for(stem):
    return os.path.join(NB_DIR, f"{stem}.ipynb")


def render(stem, arm, chunks, chunk_index, branch=None):
    return json.dumps(build(stem, arm, chunks, chunk_index, branch), indent=1) + "\n"


def main():
    os.makedirs(NB_DIR, exist_ok=True)
    stale = os.path.join(NB_DIR, "ac19_leftovers_5m_greedy.ipynb")
    if os.path.exists(stale):
        os.remove(stale)                 # the combined notebook is not the job
        print("removed", os.path.relpath(stale, ROOT))
    for stem, arm, chunks, idx in VARIANTS:
        with open(path_for(stem), "w") as f:
            f.write(render(stem, arm, chunks, idx))
        print("wrote", os.path.relpath(path_for(stem), ROOT))


if __name__ == "__main__":
    main()
