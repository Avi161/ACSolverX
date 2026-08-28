"""Lift the 1M residuals to a 5,000,000-node budget — stride-chunked for Colab.

THE ROW LISTS
-------------
What survived the 1,000,000-node pass (``run_leftovers_1m``, results in
``results/heuristic_search/leftovers_1m/RESULTS.md``), shipped beside the 100k
lists with the presentations inline:

    unsolved_1m_baseline.csv    88 rows   greedy / total-length ordering
    unsolved_1m_s20_mk2.csv     14 rows   L + 20*S + 2*MK   (subset of the 88)

Both are ``solved == false`` read off the 1M jsonl, with each orbit's membership
joined back from the 100k lists so the schema stays the one every wave has used.
``tests/test_leftovers_5m.py`` re-derives them rather than trusting them.

STRIDE CHUNKING
---------------
88 single-worker rows at 5M is several Colab-days, so the greedy arm splits
across four notebooks the way the u124 campaign did: ``CHUNKS=4``,
``CHUNK_INDEX=k`` takes rows ``[k-1::4]`` — interleaved, not contiguous, so the
name-ordered difficulty gradient spreads evenly and no chunk is "the hard one".
22 rows per chunk, disjoint by construction, union = all 88. The s20_mk2 arm is
14 rows and runs as one notebook.

WHY ONE WORKER
--------------
The engine's own arena formula gives ~35 GB reserved per search at 5M, and the
hard tail discovers ~100 states per pop (measured: a 6M-state grow by 60,000
pops on ``ac19_7284``), so a full-budget row can genuinely touch ~40 GB. On a
51 GB runtime that is one worker — parallelism comes from the chunking, not the
pool. The dedup is already the memory trick: FNV-hashed nibble rows in an
open-addressing int32 table at ~79 B/state (``greedy_compact``). Anything
leaner means fingerprint-only visited sets, which make the search probabilistic
— a hash collision silently skips a state — and nothing in this screen's chain
of results is probabilistic. Not done here.

    PYTHONPATH=. python3 -m experiments.search.run_leftovers_5m \
        --arm greedy --chunks 4 --chunk-index 1 --smoke

THE SELF-CHECK MOVES TO 1,000,000
---------------------------------
Same engine, same cap, same config: a search at budget B is the first B pops of
any longer search, so a row that failed at 1,000,000 cannot come back solved at
or below 1,000,000 now. A row that does means the wrong search ran.
"""
from __future__ import annotations

import argparse
import json
import os
import time

from experiments.search.run_leftovers_1m import (
    ARMS, MAX_RELATOR_LENGTH, SCREEN_DIR, _beat, _done, _iter_results, _job,
    _mirror, _seed_from_mirror, est_gb, load_rows as _load_1m_rows, read_rows,
    resolve_arm, resolve_workers,
)

NODE_BUDGET_5M = 5_000_000
CHECKPOINTS_5M = (1_000_000, 2_000_000, 5_000_000)
FLOOR_5M = 1_000_000          # every input row failed at 1M; none may solve below

# arm -> (the 1M-unsolved CSV, its row count, default chunk count)
SPEC_5M = {
    "greedy": {"csv": "unsolved_1m_baseline.csv", "n_rows": 88, "chunks": 4},
    "s20_mk2": {"csv": "unsolved_1m_s20_mk2.csv", "n_rows": 14, "chunks": 1},
}


def load_rows_5m(arm, csv_path=None):
    """``([{name, r1, r2, ...}], path)`` — the arm's 1M-unsolved list, in file order."""
    key, _ = resolve_arm(arm)
    spec = SPEC_5M[key]
    path = csv_path or os.path.join(SCREEN_DIR, spec["csv"])
    rows, used = _load_1m_rows(key, csv_path=path)
    if csv_path is None and len(rows) != spec["n_rows"]:
        raise RuntimeError(
            f"{spec['csv']} has {len(rows)} rows, expected {spec['n_rows']} -- "
            f"stale clone; pull the branch before running.")
    return rows, used


def stride_chunk(rows, chunks, chunk_index):
    """Rows ``[chunk_index-1::chunks]`` — the u124 campaign's interleaved split.

    Interleaved rather than contiguous so a difficulty gradient in file order
    spreads across every chunk instead of concentrating in one. The chunks are
    disjoint and their union is the full list, both pinned by tests.
    """
    chunks = int(chunks)
    chunk_index = int(chunk_index)
    if chunks < 1:
        raise ValueError(f"chunks must be >= 1, got {chunks}")
    if not 1 <= chunk_index <= chunks:
        raise ValueError(f"chunk_index must be in [1, {chunks}], got {chunk_index}")
    return rows[chunk_index - 1::chunks]


def unsolved_at_1m(arm):
    """The arm's 1M leftovers re-derived from the 1M jsonl, sorted by name.

    The unsolved_1m CSVs are supposed to be exactly this; deriving it again is
    what lets a test (and a notebook's SETUP) check them instead of trusting them.
    """
    key, _ = resolve_arm(arm)
    path = os.path.join(
        os.path.dirname(SCREEN_DIR), "leftovers_1m",
        f"leftovers_1m_{key}_b1000000_mrl48.jsonl")
    rows = read_rows(path)
    if not rows:
        raise FileNotFoundError(f"1M jsonl missing or empty: {path}")
    return sorted(r["name"] for r in rows if not r.get("solved"))


def out_path_5m(arm, out_dir, chunks, chunk_index,
                budget=NODE_BUDGET_5M, mrl=MAX_RELATOR_LENGTH):
    key, _ = resolve_arm(arm)
    tag = f"_c{int(chunk_index)}of{int(chunks)}" if int(chunks) > 1 else ""
    return os.path.join(
        out_dir, f"leftovers_5m_{key}{tag}_b{budget}_mrl{mrl}.jsonl")


def classify_5m(rows, budget=NODE_BUDGET_5M, checkpoints=CHECKPOINTS_5M,
                floor=FLOOR_5M):
    """Split result rows; flag any solve at or below the 1M floor as impossible."""
    solved, unsolved, suspicious = [], [], []
    for r in rows:
        if r.get("solved") and int(r["nodes_explored"]) <= budget:
            solved.append(r["name"])
            if int(r["nodes_explored"]) <= floor:
                suspicious.append(r["name"])
        else:
            unsolved.append(r["name"])
    return {
        "n": len(rows),
        "solved_at_5m": solved,
        "unsolved_at_5m": unsolved,
        "solved_at_or_below_1m": suspicious,
        "anytime": {c: sum(1 for r in rows
                           if r.get("solved") and int(r["nodes_explored"]) <= c)
                    for c in checkpoints},
    }


def run_arm_5m(arm, out_dir, chunks=None, chunk_index=1, budget=NODE_BUDGET_5M,
               mrl=MAX_RELATOR_LENGTH, n_workers="auto", resume=True,
               csv_path=None, mirror_dir=None, limit=None, heartbeat_secs=60,
               log=print):
    """Run one arm's chunk to a chunk-tagged jsonl; append + whole-file mirror."""
    key, spec1m = resolve_arm(arm)
    if chunks is None:
        chunks = SPEC_5M[key]["chunks"]
    rows, used = load_rows_5m(key, csv_path=csv_path)
    rows = stride_chunk(rows, chunks, chunk_index)
    if limit:
        rows = rows[:int(limit)]

    os.makedirs(out_dir, exist_ok=True)
    out = out_path_5m(key, out_dir, chunks, chunk_index, budget, mrl)
    if resume:
        _seed_from_mirror(out, mirror_dir, log)
    seen = _done(out) if resume else set()
    todo = [r for r in rows if r["name"] not in seen]

    n_workers, per_gb = resolve_workers(key, n_workers, budget=budget, mrl=mrl)
    log(f"  arm     : {key} -- {spec1m['label']}")
    log(f"  rows    : {len(rows)} (chunk {chunk_index} of {chunks}, "
        f"stride split of {SPEC_5M[key]['n_rows']}) from {used}")
    log(f"  budget  : {budget:,} nodes, cap {mrl}")
    log(f"  workers : {n_workers} (~{per_gb:.1f} GB/search reserved)")
    log(f"  resume  : {len(seen)} row(s) already on disk, {len(todo)} to run")
    log(f"  -> {out}")

    t0 = time.time()
    last = t0
    jobs = [(key, r, budget, mrl, heartbeat_secs) for r in todo]
    done = 0
    if jobs:
        with open(out, "a") as fh:
            for rec in _iter_results(jobs, n_workers, log):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                done += 1
                last = _beat(rec, done, len(jobs), t0, last, heartbeat_secs,
                             out, mirror_dir, log)
    _mirror(out, mirror_dir)
    log(f"  {done} row(s) run in {time.time() - t0:,.0f}s; jsonl at {out}")
    return out


def report_5m(arm, out_dir, chunks=None, chunk_index=None, budget=NODE_BUDGET_5M,
              mrl=MAX_RELATOR_LENGTH, write_ids=True, log=print):
    """Report one chunk, or — with ``chunk_index=None`` — every chunk merged.

    The merged view is what the experiment answers; a single chunk's numbers are
    progress, not a result, and are labelled as such.
    """
    key, spec1m = resolve_arm(arm)
    if chunks is None:
        chunks = SPEC_5M[key]["chunks"]
    idxs = [chunk_index] if chunk_index is not None else range(1, int(chunks) + 1)
    rows, missing = [], []
    for i in idxs:
        p = out_path_5m(key, out_dir, chunks, i, budget, mrl)
        got = read_rows(p)
        rows.extend(got)
        if not got:
            missing.append(i)
    if not rows:
        log(f"no rows yet for {key} in {out_dir}")
        return None
    c = classify_5m(rows, budget=budget)
    expected = (SPEC_5M[key]["n_rows"] if chunk_index is None
                else len(stride_chunk(load_rows_5m(key)[0], chunks, chunk_index)))
    scope = ("all chunks merged" if chunk_index is None
             else f"chunk {chunk_index} of {chunks} ONLY -- progress, not a result")

    log("")
    log(f"=== {key} @ 5M -- {spec1m['label']}  [{scope}]")
    log(f"    rows complete        : {len(rows)}/{expected}"
        + ("" if len(rows) == expected else
           "   (PARTIAL -- these numbers are not final)")
        + (f"   [chunks with no rows yet: {missing}]" if missing and
           chunk_index is None else ""))
    n_solved = len(c["solved_at_5m"])
    pct = f"   ({100.0 * n_solved / len(rows):.1f}%)" if rows else ""
    log(f"    solved at {budget:>9,}  : {n_solved}{pct}")
    log(f"    still unsolved       : {len(c['unsolved_at_5m'])}")
    log("    anytime (free -- one search answers every budget below it):")
    for cp in sorted(c["anytime"]):
        log(f"      <= {cp:>9,} : {c['anytime'][cp]}")
    if c["solved_at_or_below_1m"]:
        if mrl == MAX_RELATOR_LENGTH:
            # same cap as the 1M run, so the prefix property applies exactly
            log(f"    !! {len(c['solved_at_or_below_1m'])} row(s) solved at or "
                f"below 1,000,000 nodes, which the 1M run says is impossible: "
                f"{c['solved_at_or_below_1m'][:5]}")
            log("       -> the search being run is not the one that built this "
                "list; stop and check the arm, the cap and the row list before "
                "reading anything above.")
        else:
            # a different cap is a different search space: the 1M floor was
            # established at cap 48, so an early solve here is legitimate --
            # and it is the interesting outcome, not an error
            log(f"    note: {len(c['solved_at_or_below_1m'])} row(s) solved at "
                f"or below 1,000,000 nodes. Legitimate at cap {mrl} (the 1M "
                f"floor holds only at cap {MAX_RELATOR_LENGTH}); these are "
                f"rows the wider corridor cracked cheaply.")

    if write_ids and chunk_index is None and len(rows) == expected:
        for stem, ids in (("solved_at_5m", c["solved_at_5m"]),
                          ("still_unsolved_5m", c["unsolved_at_5m"])):
            p = os.path.join(out_dir, f"{stem}_{key}.txt")
            with open(p, "w") as f:
                f.write("".join(n + "\n" for n in sorted(ids)))
            log(f"    {stem} ids -> {p}")
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", required=True, choices=sorted(SPEC_5M))
    ap.add_argument("--out-dir", default=os.path.join(
        os.path.dirname(SCREEN_DIR), "leftovers_5m"))
    ap.add_argument("--chunks", type=int, default=None)
    ap.add_argument("--chunk-index", type=int, default=1)
    ap.add_argument("--budget", type=int, default=NODE_BUDGET_5M)
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="2 rows at a 2,000-node budget -- proves the pipeline, "
                         "measures nothing")
    a = ap.parse_args(argv)
    budget, limit, out_dir = a.budget, a.limit, a.out_dir
    if a.smoke:
        budget, limit = 2_000, 2
        out_dir = out_dir + "_smoke"
    run_arm_5m(a.arm, out_dir, chunks=a.chunks, chunk_index=a.chunk_index,
               budget=budget, n_workers=a.workers, limit=limit)
    report_5m(a.arm, out_dir, chunks=a.chunks, chunk_index=a.chunk_index,
              budget=budget)


if __name__ == "__main__":
    main()
