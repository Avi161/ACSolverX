"""Write the five AC19-leftover 5M Colab notebooks from one template.

    PYTHONPATH=. python3 -m experiments.search.make_leftover_5m_notebooks

Four stride chunks of the greedy arm's 88 rows (CHUNKS=4, CHUNK_INDEX=1..4 --
the u124 campaign's split, interleaved so difficulty spreads evenly) plus one
notebook for the s20_mk2 arm's 14. Five files because at a 5,000,000-node budget
the engine's arena reserves ~35 GB per search, so each runtime fits ONE worker
and the parallelism has to come from Colab sessions, not the pool.

Same contract as ``make_leftover_notebooks``: one template, per-notebook CONFIG,
and ``tests/test_leftovers_5m.py`` asserts the committed files are byte-identical
to this generator's output.
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
    + [("ac19_leftovers_5m_s20_mk2", "s20_mk2", 1, 1)]
)


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
#   This notebook runs chunk %(chunk_index)d of 4 -- rows [%(k0)d::4] of the
#   name-ordered list, 22 rows -- at 5,000,000 nodes. The four chunk notebooks
#   are disjoint and together cover all 88; run them as four parallel Colab
#   sessions with separate Drive dirs, exactly like the u124 campaign.''',
    "s20_mk2": '''# THE QUESTION
#   14 orbits survived the s20_mk2 (L + 20*S + 2*MK) arm's 1,000,000-node pass
#   -- the tail both orderings fail. This notebook runs all 14 at 5,000,000
#   nodes as a single session; at one worker per runtime there is nothing to
#   gain from splitting a list this small.''',
}

CONFIG = '''# ===== AC19 LEFTOVERS @ 5M -- %(title)s -- CONFIG (edit ONLY this cell) =====
# Runtime: **CPU, High-RAM**. Nothing here touches a GPU.
#
%(blurb)s
#
# THE ROW LIST IS THE REAL ONE
#   results/heuristic_search/ac19_autmin_screen/%(csv)s -- read off the 1M jsonl
#   (solved == false), orbit membership joined from the 100k lists. SETUP
#   re-derives it from that jsonl before searching anything.
#
# MEMORY, AND WHY ONE WORKER
#   The engine's arena formula reserves ~35 GB per search at 5M, and the hard
#   tail discovers ~100 states per pop, so a full-budget row can touch ~40 GB.
#   N_WORKERS="auto" will resolve 1 on a 51 GB runtime -- that is correct, not
#   a bug. The dedup is already the memory trick (FNV-hashed nibble rows in an
#   open-addressing table, ~79 B/state); anything leaner would be
#   fingerprint-only and probabilistic, which this screen does not do.
#
# EXPECT DAYS, AND EXPECT TO RESUME
#   ~500-800 nodes/s single-worker means a row that uses its whole budget takes
#   ~2-3 h. Colab will disconnect first -- reopen, Run All, and RESUME picks up
#   from the Drive-mirrored jsonl; a wiped /content reseeds from Drive. Nothing
#   already recorded is recomputed.

REPO_URL = "https://github.com/Avi161/ACSolverX.git"
BRANCH   = "%(branch)s"
REPO_DIR = "ACSolverX"
CLONE       = True
UPDATE_REPO = True           # git reset --hard, so Restart -> Run All pulls latest
MOUNT_DRIVE = True           # jsonl mirrored to Drive; the run resumes from it

ARM         = "%(arm)s"
CHUNKS      = %(chunks)d
CHUNK_INDEX = %(chunk_index)d

NODE_BUDGET = 5_000_000      # the lift this notebook exists to run
MAX_RELATOR_LENGTH = 48      # the cap every wave of this screen has used

N_WORKERS = "auto"           # resolves 1 at this budget; see MEMORY above
RESUME    = True             # rows already in the jsonl are skipped

LOCAL_OUT_DIR = "results/heuristic_search/leftovers_5m"
DRIVE_OUT_DIR = "/content/drive/MyDrive/acsolverx/leftovers_5m_%(drive_tag)s"

# Proves the whole pipeline in about a minute -- clone, import, search, jsonl,
# resume, report -- at a budget that measures nothing, into a separate _smoke
# directory. Run it once, read the table, then set False.
SMOKE_RUN = True

print("config loaded:", ARM, "chunk", CHUNK_INDEX, "of", CHUNKS)
'''

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
    sh("pip -q install numba")
    if MOUNT_DRIVE:
        from google.colab import drive
        drive.mount("/content/drive")
        os.makedirs(DRIVE_OUT_DIR, exist_ok=True)
    REPO_ROOT = os.path.join(BASE, REPO_DIR)
else:
    REPO_ROOT = os.getcwd()
    while REPO_ROOT != "/" and not (
        os.path.isdir(os.path.join(REPO_ROOT, "experiments"))
        and os.path.isdir(os.path.join(REPO_ROOT, "data"))
    ):
        REPO_ROOT = os.path.dirname(REPO_ROOT)

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
    load_rows_5m, report_5m, resolve_workers, run_arm_5m, stride_chunk,
    unsolved_at_1m)

assert HAVE_HCOMPACT, ("packed-arena engine missing -- wrong branch or a stale "
                       "clone; a 5M run on the Python fallback would OOM")

# warm the numba kernels in the parent, not in a worker's first row
_ = ARMS[ARM]["run"]("xyx", "yx", 20, 32)

_rows, _csv = load_rows_5m(ARM)
_chunk = stride_chunk(_rows, CHUNKS, CHUNK_INDEX)

# the row list must be exactly what the 1M run left unsolved -- checked here,
# against the 1M jsonl on this branch, before a single node is searched
_derived = unsolved_at_1m(ARM)
assert sorted(r["name"] for r in _rows) == _derived, "row list drifted from the 1M jsonl"

_nw, _gb = resolve_workers(ARM, N_WORKERS, budget=NODE_BUDGET)
print(f"arm={ARM}  chunk={CHUNK_INDEX}/{CHUNKS}  rows={len(_chunk)} of {len(_rows)}  from {_csv}")
print(f"     verified against the 1M jsonl ({len(_derived)} unsolved there)")
print(f"engine=hcompact  workers={_nw} (~{_gb:.1f} GB/search reserved)  "
      f"budget={NODE_BUDGET:,}  cap={MAX_RELATOR_LENGTH}")
print("kernels warm -- setup done")
'''

RUN = '''# ==================== RUN =================================================
# Appends to a local jsonl and mirrors the WHOLE file to Drive as it goes; RESUME
# reads it back (and reseeds a wiped /content from Drive), so Restart -> Run All
# continues instead of restarting. Expect to use this several times at 5M.
import os

OUT_DIR = os.path.join(REPO_ROOT, LOCAL_OUT_DIR)
MIRROR  = DRIVE_OUT_DIR if (IN_COLAB and MOUNT_DRIVE) else None

budget, limit = NODE_BUDGET, None
if SMOKE_RUN:
    budget, limit = 2_000, 2
    OUT_DIR = OUT_DIR + "_smoke"
    MIRROR = None
    print(f"SMOKE_RUN: {limit} rows at budget {budget:,} -> {OUT_DIR}")
else:
    print(f"FULL RUN: budget {budget:,} over the {len(_chunk)} rows of "
          f"chunk {CHUNK_INDEX}/{CHUNKS}; rows already in the jsonl are skipped")

out = run_arm_5m(
    ARM, OUT_DIR,
    chunks=CHUNKS,
    chunk_index=CHUNK_INDEX,
    budget=budget,
    mrl=MAX_RELATOR_LENGTH,
    n_workers=N_WORKERS,
    resume=RESUME,
    limit=limit,
    mirror_dir=MIRROR,
)
print("jsonl:", out)
'''

REPORT = '''# ==================== REPORT =============================================
# Free to re-run; reads the jsonl off disk and never searches. Prints THIS
# chunk's progress, then the merged view across whatever chunks have rows in
# OUT_DIR so far -- the merged table is the experiment's answer, and it also
# flags (loudly) any row solved at or below 1,000,000 nodes, which the 1M run
# says is impossible for these lists.
c_chunk = report_5m(ARM, OUT_DIR, chunks=CHUNKS, chunk_index=CHUNK_INDEX,
                    budget=budget)
c_all = report_5m(ARM, OUT_DIR, chunks=CHUNKS, budget=budget)
'''


def build(stem, arm, chunks, chunk_index, branch=None):
    branch = branch or current_branch()
    from experiments.search.run_leftovers_5m import SPEC_5M
    cfg = CONFIG % {
        "title": (f"GREEDY c{chunk_index}of{chunks}" if arm == "greedy"
                  else "S20_MK2"),
        "blurb": _ARM_BLURB[arm] % {"chunk_index": chunk_index,
                                    "k0": chunk_index - 1},
        "csv": SPEC_5M[arm]["csv"],
        "branch": branch,
        "arm": arm,
        "chunks": chunks,
        "chunk_index": chunk_index,
        "drive_tag": (f"greedy_c{chunk_index}of{chunks}" if arm == "greedy"
                      else "s20_mk2"),
    }
    cells = [cfg, SETUP, RUN, REPORT]
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
    for stem, arm, chunks, idx in VARIANTS:
        with open(path_for(stem), "w") as f:
            f.write(render(stem, arm, chunks, idx))
        print("wrote", os.path.relpath(path_for(stem), ROOT))


if __name__ == "__main__":
    main()
