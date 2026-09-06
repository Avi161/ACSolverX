"""Sweep the whole AC19 Aut-min screen with the 501-node cascade prefix.

WHY THIS RUNNER EXISTS
----------------------
``experiments/search/hybrid_10m.py`` is a three-row instrument. It pins the
prefix to one exact signature -- normalization 0 nodes, rewrite 1 node, s40_gen
500 nodes and unsolved -- and raises if a row deviates, because a prefix solve
there could serialize an ``Aut(F2)`` move as if it were an AC substitution.
That pin is right for the three joint survivors and wrong for a screen: it
fires on 125 of the 259 rows already on disk. This runner keeps the same
501-node cascade and drops the pin, replacing it with an explicit split.

    solved            AC-trivialized. Substitution-only, replayed move by move
                      through ``moves_to_states`` and required to land on a
                      terminal pair. This is the repo's certification standard
                      and the only column that means what the campaign means.

    aut_assisted      Solved only by also changing basis. The cascade's
                      ``s40_gen`` arm pushes Nielsen images into the same heap
                      as AC substitutions, so its path may contain steps of
                      kind ``automorphism``. Such a path proves AC-triviality
                      of an automorphic image, not of the presentation. It is
                      recorded, never counted as solved, and never certified.

    unsolved          The prefix ran out at 501 nodes.

WHAT IT COSTS
-------------
Measured over the whole screen, 3 workers on 4 cores, cap 255: 72,779 rows in
11.0 minutes wall and 0.55 core-hours -- 0.027 s per row, 0.18 GiB peak RSS
per worker. (The 0.204 s/row figure from the shipped hard lists is the tail,
not the screen; almost every orbit settles in a handful of nodes.) Unlike the
10M hybrid, which plans a 319 GiB reservation at cap 255 and cannot run on a
small box at all. ``plan`` prints both so the comparison is on the page
rather than in someone's memory.

    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen plan
    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen smoke
    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen run \
        --workers auto --chunks 1 --chunk-index 1
    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen report
"""
from __future__ import annotations

import argparse
import csv
import json
import functools
import multiprocessing as mp
import os
import resource
import sys
import time
import traceback

from experiments.equivalence_classes.lib.words import canon_pair
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.search.hybrid_10m import (
    PREFIX_BUDGET, SEARCH_CAP, STARTER_BUDGET,
)

ARM = "cascade501"
CAMPAIGN = "ac19_cascade_screen"
REWRITE_BUDGET = 1000
INTERMEDIATE_CAP = None

# Two arms, one knob apart.
#
#   cascade501  the shipped cascade: basis normalization, the BS rewrite, then
#               `s40_gen`, whose heap holds Nielsen images alongside AC
#               substitutions.
#   ac501       the control. `mixed_search` with the SAME priority (L + 40*S),
#               the same 501 nodes and the same cap 255, and one difference:
#               no Nielsen image ever enters the heap.
#
# Without the control the headline is unreadable. A row the cascade marks
# `aut_assisted` is not a row with no AC path -- it is a row where the
# cheapest path the heap reached used a basis change. Only running the same
# search with that door shut says which it is.
ARMS = ("cascade501", "ac501")
S40 = dict(s_weight=40.0, mk_weight=0.0, w_weight=0.0)

# The ladder. 501 is the prefix `hybrid_10m` pins; the rungs above it are the
# same search with more rope, each run over the rung below's residue rather
# than over the whole screen. `cascade_heuristics.search` refuses a budget
# past 100,000, which is also where this pass stops being the cheap one --
# past it the hcompact campaigns (1M/5M/10M) take over.
LADDER = (PREFIX_BUDGET, 1_000, 10_000, 100_000)
MAX_BUDGET = 100_000

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROWS_CSV = os.path.join(ROOT, "results", "heuristic_search",
                        "ac19_autmin_screen", "ac19_autmin_orbits.csv")
DEFAULT_OUT = os.path.join(ROOT, "results", "heuristic_search", CAMPAIGN)

# Measured, not assumed: see the module docstring. The worker ceiling is the
# observed peak with a wide margin, so a runaway row dies instead of the box.
SECONDS_PER_ROW = 0.027
PEAK_RSS_GB_PER_WORKER = 0.18
WORKER_RLIMIT_GB = 2.0


def out_path(out_dir, chunks, chunk_index, arm=ARM, budget=PREFIX_BUDGET):
    stem = f"{CAMPAIGN}_{arm}_b{budget}_mrl{SEARCH_CAP}"
    if chunks and chunks > 1:
        stem += f"_part{chunk_index}of{chunks}"
    return os.path.join(out_dir, stem + ".jsonl")


def load_rows(path=None):
    """The screen list, or a residue CSV a higher rung was pointed at."""
    path = path or ROWS_CSV
    if not os.path.exists(path):
        raise SystemExit(
            f"{path} is missing. Build it first:\n"
            "  PYTHONPATH=. python3 -m experiments.search."
            "make_ac19_autmin_screen --write")
    with open(path) as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"{path} is empty")
    return rows


def stride_chunk(rows, chunks, chunk_index):
    """Interleave rather than slice, so every chunk gets the same difficulty mix."""
    if not chunks or chunks <= 1:
        return rows
    if not 1 <= chunk_index <= chunks:
        raise ValueError(f"chunk index {chunk_index} outside 1..{chunks}")
    return rows[chunk_index - 1::chunks]


def read_done(path):
    if not os.path.exists(path):
        return {}
    done = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue                       # a torn final line; it gets redone
            if not record.get("error"):
                done[record["name"]] = record
    return done


def certify_path(r1, r2, states, steps):
    """Replay a substitution-only path and demand it end on a terminal pair.

    Returns ``(ok, reason)``. Anything but ``(True, "")`` must not be written
    as a solve.
    """
    if any(step.get("kind") != "substitution" for step in steps):
        return False, "path contains a basis change"
    if len(states) != len(steps) + 1:
        return False, "state and step counts disagree"
    state = list(canon_pair(r1, r2))
    if state != list(states[0]):
        return False, "path does not start at the canonical input"
    for step, expected in zip(steps, states[1:]):
        try:
            state = list(moves_to_states(state[0], state[1],
                                         [str_to_move(step["move"])])[-1])
        except Exception as exc:               # a malformed move is a failure
            return False, f"move replay raised {type(exc).__name__}: {exc}"
        if state != list(expected):
            return False, "replayed state differs from the recorded state"
    if not (len(state[0]) == len(state[1]) == 1
            and state[0].lower() != state[1].lower()):
        return False, f"path does not end on a terminal pair: {state}"
    return True, ""


def _fingerprint(steps):
    """Identify a certificate without storing it.

    The screen-wide jsonl already costs 57 MB with no paths in it at all;
    carrying every path would be several times that, and it is not what this
    repo commits anyway -- ``ac19_autmin_screen/`` ships residues, not the
    screen. So a solved row records the digest of its move sequence, and
    ``certify`` regenerates the certificate itself for any named subset. The
    search is deterministic, so the digest either comes back or the run was
    not the run it claims to be.
    """
    import hashlib
    joined = "\n".join(step["move"] for step in steps)
    return hashlib.sha256(joined.encode()).hexdigest()


def search_row(pair, arm=ARM, budget=PREFIX_BUDGET):
    """Run one arm on one pair and return a cascade-shaped result dict."""
    if not 1 <= budget <= MAX_BUDGET:
        raise ValueError(f"budget {budget} outside 1..{MAX_BUDGET}")
    if arm == "cascade501":
        from experiments.search.cascade_heuristics import search as cascade
        # The prefix keeps its pinned shape at every rung: the extra rope goes
        # to the final S20 component, not to `s40_gen`, so a rung is a strict
        # extension of the rung below and not a different search.
        return cascade(pair, budget=budget, cap=SEARCH_CAP,
                       starter_budget=STARTER_BUDGET,
                       rewrite_budget=REWRITE_BUDGET,
                       intermediate_cap=INTERMEDIATE_CAP)
    if arm != "ac501":
        raise ValueError(f"unknown arm {arm!r}; choose from {ARMS}")
    from experiments.search.heuristic_1k import mixed_search
    got = mixed_search(pair, "s20", budget=budget, cap=SEARCH_CAP, **S40)
    # `mixed_search` returns steps already tagged 'substitution'; wrap it in
    # the cascade's shape so one record schema covers both arms.
    return dict(got, attempts=[dict(component="ac_s40",
                                    nodes=got["nodes_explored"],
                                    solved=got["solved"])],
                winner=("ac_s40" if got["solved"] else None),
                min_total_length_seen=got["min_total_length_seen"])


def run_row(row, arm=ARM, budget=PREFIX_BUDGET):
    """One orbit. Never raises: a failure comes back as an ``error`` record."""
    started = time.time()
    record = {"name": row["name"], "r1": row["r1"], "r2": row["r2"],
              "n_members": int(row.get("n_members", 1) or 1),
              "budget": budget, "cap": SEARCH_CAP, "arm": arm,
              "campaign": CAMPAIGN}
    try:
        result = search_row((row["r1"], row["r2"]), arm, budget)
    except Exception as exc:
        record.update(error=f"{type(exc).__name__}: {exc}",
                      traceback=traceback.format_exc()[-2000:],
                      seconds=round(time.time() - started, 4))
        return record

    steps = result["steps"]
    aut_assisted = bool(result["solved"]) and any(
        step.get("kind") == "automorphism" for step in steps)
    certified, reason = (False, "not solved")
    if result["solved"] and not aut_assisted:
        certified, reason = certify_path(
            row["r1"], row["r2"], result["states"], steps)

    record.update(
        solved=bool(certified),
        aut_assisted=aut_assisted,
        winner=result["winner"],
        certificate=("ac" if certified else "aut_assisted" if aut_assisted else None),
        certificate_moves=len(steps) if certified else None,
        certificate_rejected=(reason if result["solved"] and not aut_assisted
                              and not certified else None),
        nodes_explored=int(result["nodes_explored"]),
        attempts=result["attempts"],
        best_state=list(result["best_state"]),
        min_relator_length=int(result["min_total_length_seen"]),
        max_relator_length_seen=int(result["max_relator_length_seen"]),
        certificate_sha256=(_fingerprint(steps) if certified else None),
        seconds=round(time.time() - started, 4),
        peak_rss_gb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                          / 2 ** 20, 3),
    )
    # A rejected certificate is a bug in the search, not a quiet "unsolved".
    if record["certificate_rejected"]:
        record["error"] = ("substitution-only path failed replay: "
                           + record["certificate_rejected"])
    return record


def _init_worker(rlimit_bytes):
    try:
        resource.setrlimit(resource.RLIMIT_AS, (rlimit_bytes, rlimit_bytes))
    except (ValueError, OSError) as exc:
        # Fail closed, exactly as the 5M worker does: an unguarded worker on a
        # shared box is how a campaign takes the box down with it.
        raise SystemExit(f"cannot enforce worker address-space limit: {exc}")
    try:
        os.nice(5)
    except OSError:
        pass


def plan(log=print):
    rows = load_rows() if os.path.exists(ROWS_CSV) else []
    n = len(rows) or 72_779
    cores = os.cpu_count() or 1
    core_hours = n * SECONDS_PER_ROW / 3600
    info = {
        "rows": n,
        "budget_per_row": PREFIX_BUDGET,
        "cap": SEARCH_CAP,
        "seconds_per_row_measured": SECONDS_PER_ROW,
        "core_hours": round(core_hours, 2),
        "wall_hours_on_this_box": round(core_hours / max(1, cores - 1), 2),
        "cores_here": cores,
        "peak_rss_gb_per_worker_measured": PEAK_RSS_GB_PER_WORKER,
        "worker_rlimit_gb": WORKER_RLIMIT_GB,
        "gb_needed_for_n_workers": {
            str(w): round(w * WORKER_RLIMIT_GB + 1.0, 1) for w in (2, 4, 8, 16)},
    }
    log(json.dumps(info, indent=2))
    log("\n  For contrast, the 10M hybrid at this same cap 255 plans a")
    log("  2,140,262,144-state reservation = 319.0 GiB per lane. That stage")
    log("  is a big-memory job; this screen is not.")
    return info


def run(out_dir=DEFAULT_OUT, *, arm=ARM, budget=PREFIX_BUDGET, rows_csv=None,
        workers="auto", chunks=1, chunk_index=1, limit=None, resume=True,
        log=print):
    if arm not in ARMS:
        raise SystemExit(f"unknown arm {arm!r}; choose from {ARMS}")
    if not 1 <= budget <= MAX_BUDGET:
        raise SystemExit(f"budget {budget} outside 1..{MAX_BUDGET}; past that "
                         "the hcompact campaigns take over")
    rows = stride_chunk(load_rows(rows_csv), chunks, chunk_index)
    if limit:
        rows = rows[:int(limit)]
    os.makedirs(out_dir, exist_ok=True)
    path = out_path(out_dir, chunks, chunk_index, arm, budget)
    done = read_done(path) if resume else {}
    todo = [r for r in rows if r["name"] not in done]
    n_workers = (max(1, (os.cpu_count() or 2) - 1) if workers == "auto"
                 else max(1, int(workers)))
    log(f"  campaign : {CAMPAIGN} / {arm} at {budget:,} nodes")
    log(f"  input    : {rows_csv or ROWS_CSV}")
    log(f"  rows     : {len(rows):,} in this chunk, {len(done):,} already done, "
        f"{len(todo):,} to run")
    log(f"  workers  : {n_workers} (rlimit {WORKER_RLIMIT_GB} GB each)")
    log(f"  out      : {path}")
    if not todo:
        log("  nothing to do")
        return path

    rlimit = int(WORKER_RLIMIT_GB * 2 ** 30)
    started = time.time()
    written = 0
    ctx = mp.get_context("fork")
    with open(path, "a") as fh:
        if n_workers == 1:
            _init_worker(rlimit)
            stream = (run_row(r, arm, budget) for r in todo)
        else:
            pool = ctx.Pool(n_workers, initializer=_init_worker,
                            initargs=(rlimit,))
            stream = pool.imap_unordered(
                functools.partial(run_row, arm=arm, budget=budget),
                todo, chunksize=16)
        try:
            for record in stream:
                fh.write(json.dumps(record) + "\n")
                written += 1
                if written % 2000 == 0:
                    fh.flush()
                    rate = written / max(1e-9, time.time() - started)
                    left = (len(todo) - written) / max(1e-9, rate) / 60
                    log(f"  {written:,}/{len(todo):,}  "
                        f"{rate:.1f} rows/s  ~{left:.0f} min left")
        finally:
            if n_workers > 1:
                pool.close()
                pool.join()
        fh.flush()
    log(f"  wrote {written:,} rows in {(time.time() - started) / 60:.1f} min")
    return path


def report(out_dir=DEFAULT_OUT, *, arm=ARM, budget=PREFIX_BUDGET, chunks=1, chunk_index=None, log=print):
    records = _all_records(out_dir, chunks, chunk_index, arm, budget)
    total = len(records)
    ac = [r for r in records.values() if r.get("solved")]
    aut = [r for r in records.values() if r.get("aut_assisted")]
    rejected = [r for r in records.values() if r.get("certificate_rejected")]
    by_winner = {}
    for r in ac:
        by_winner[r["winner"]] = by_winner.get(r["winner"], 0) + 1
    seconds = sum(r.get("seconds", 0.0) for r in records.values())
    log(f"  rows scored          : {total:,}")
    log(f"  AC-certified solves  : {len(ac):,} "
        f"({100.0 * len(ac) / total:.2f}%)   by winner: {by_winner or '{}'}")
    log(f"  aut-assisted only    : {len(aut):,} "
        f"({100.0 * len(aut) / total:.2f}%)  NOT AC certificates")
    log(f"  rejected certificates: {len(rejected):,}   (must be 0)")
    log(f"  unsolved             : "
        f"{total - len(ac) - len(aut):,}")
    log(f"  cost                 : {seconds / 3600:.2f} core-hours "
        f"({seconds / max(1, total):.3f} s/row)")
    if rejected:
        raise SystemExit("a substitution-only path failed replay; do not "
                         "publish this run until that is understood")
    return {"rows": total, "ac": len(ac), "aut_assisted": len(aut),
            "unsolved": total - len(ac) - len(aut), "by_winner": by_winner,
            "core_hours": round(seconds / 3600, 3)}


def certify(out_dir=DEFAULT_OUT, *, arm=ARM, budget=PREFIX_BUDGET, chunks=1,
            chunk_index=None, names=None, limit=None, log=print):
    """Regenerate full certificates for solved rows and re-verify each one.

    Re-runs the deterministic search, replays the moves through
    ``moves_to_states``, and refuses to write anything whose digest differs
    from the one the campaign recorded. Default subset: every solved row that
    also appears on a shipped hard list, which is the set anyone will ask
    about. ``--names`` or ``--limit`` widen or narrow it.
    """
    from experiments.search.make_ac19_autmin_screen import shipped_residues

    records = _all_records(out_dir, chunks, chunk_index, arm, budget)
    solved = {n: r for n, r in records.items() if r.get("solved")}
    if names:
        wanted = [n for n in names if n in solved]
        missing = [n for n in names if n not in solved]
        if missing:
            raise SystemExit(f"not solved in this run: {missing[:10]}")
    else:
        hard = set(shipped_residues())
        wanted = sorted(n for n in solved if n in hard) or sorted(solved)
    if limit:
        wanted = wanted[:int(limit)]
    target = os.path.join(
        out_dir, f"{CAMPAIGN}_{arm}_b{budget}_certificates.jsonl")
    os.makedirs(out_dir, exist_ok=True)
    done = {r["name"] for r in read_done(target).values() if r.get("certified")}
    written = 0
    with open(target, "a") as fh:
        for name in wanted:
            if name in done:
                continue
            expected = solved[name]
            result = search_row((expected["r1"], expected["r2"]), arm, budget)
            if not result["solved"]:
                raise SystemExit(f"deterministic re-run did not solve {name}")
            ok, why = certify_path(expected["r1"], expected["r2"],
                                   result["states"], result["steps"])
            if not ok:
                raise SystemExit(f"certificate for {name} failed replay: {why}")
            digest = _fingerprint(result["steps"])
            if digest != expected.get("certificate_sha256"):
                raise SystemExit(
                    f"re-run of {name} produced a different certificate "
                    f"({digest[:12]} vs recorded "
                    f"{str(expected.get('certificate_sha256'))[:12]})")
            fh.write(json.dumps({
                "name": name, "r1": expected["r1"], "r2": expected["r2"],
                "certified": True, "winner": result["winner"],
                "nodes_explored": int(result["nodes_explored"]),
                "certificate_sha256": digest,
                "path": result["states"],
                "path_moves": [step["move"] for step in result["steps"]],
            }) + "\n")
            fh.flush()
            written += 1
    log(f"  certified {written:,} row(s) into {target}")
    return target


def residues(out_dir=DEFAULT_OUT, *, arm=ARM, budget=PREFIX_BUDGET, chunks=1, chunk_index=None, log=print):
    """Write the lists the next stage reads: what this pass did NOT settle.

    Committing the 57 MB run jsonl is not the house pattern; committing the
    residues is. Two files, both in the shipped screen-list schema so any
    existing runner can take them as input.
    """
    records = _all_records(out_dir, chunks, chunk_index, arm, budget)
    orbits = {r["name"]: r for r in load_rows()}   # always the full screen
    groups = {
        f"unsolved_{arm}_b{budget}.csv":
            [r for r in records.values()
             if not r.get("solved") and not r.get("aut_assisted")],
        f"aut_assisted_{arm}_b{budget}.csv":
            [r for r in records.values() if r.get("aut_assisted")],
    }
    written = []
    for filename, rows in groups.items():
        path = os.path.join(out_dir, filename)
        rows.sort(key=lambda r: int(r["name"].split("_")[1]))
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=(
                "name", "r1", "r2", "n_members", "members",
                "nodes_explored", "min_relator_length"))
            w.writeheader()
            for r in rows:
                orbit = orbits[r["name"]]
                w.writerow({"name": r["name"], "r1": r["r1"], "r2": r["r2"],
                            "n_members": orbit["n_members"],
                            "members": orbit["members"],
                            "nodes_explored": r["nodes_explored"],
                            "min_relator_length": r["min_relator_length"]})
        log(f"  wrote {path} ({len(rows):,} rows)")
        written.append(path)
    return written


def ladder(out_dir=DEFAULT_OUT, *, arm=ARM, rungs=LADDER, workers="auto",
           chunks=1, chunk_index=1, log=print):
    """Walk the budget ladder, each rung over the rung below's leftovers.

    This is the shape the campaign actually wants: almost every orbit falls
    at 501 nodes, a thin tail needs 1k to 100k, and what survives 100,000 is
    the short list worth a big-RAM box at 1M and beyond. Running every rung
    over the whole screen instead would multiply the cost by the number of
    rungs and change no answer -- a search at budget B is the first B pops of
    any longer search, so a row solved at 501 is solved at 100,000.
    """
    previous, summary = None, []
    for budget in rungs:
        log(f"\n=== rung: {budget:,} nodes ===")
        run(out_dir, arm=arm, budget=budget, rows_csv=previous,
            workers=workers, chunks=chunks, chunk_index=chunk_index, log=log)
        got = report(out_dir, arm=arm, budget=budget, chunks=chunks,
                     chunk_index=chunk_index, log=log)
        written = residues(out_dir, arm=arm, budget=budget, chunks=chunks,
                           chunk_index=chunk_index, log=log)
        summary.append(dict(got, budget=budget))
        previous = written[0]                       # the unsolved list
        if got["unsolved"] == 0:
            log(f"  nothing left after {budget:,} nodes; ladder ends here")
            break
    log("\n=== ladder ===")
    log(f"  {'budget':>9}  {'in':>7}  {'AC':>7}  {'aut':>7}  {'left':>7}")
    for row in summary:
        log(f"  {row['budget']:>9,}  {row['rows']:>7,}  {row['ac']:>7,}  "
            f"{row['aut_assisted']:>7,}  {row['unsolved']:>7,}")
    log(f"\n  {summary[-1]['unsolved']:,} rows survive {rungs[-1]:,} nodes. "
        "Those are the ones a big-RAM box runs at 1M and beyond.")
    return summary


def _all_records(out_dir, chunks, chunk_index, arm=ARM, budget=PREFIX_BUDGET):
    paths = ([out_path(out_dir, chunks, i, arm, budget)
              for i in range(1, (chunks or 1) + 1)]
             if chunk_index is None and chunks and chunks > 1
             else [out_path(out_dir, chunks, chunk_index or 1, arm, budget)])
    records = {}
    for p in paths:
        records.update(read_done(p))
    if not records:
        raise SystemExit(f"no records under {out_dir}")
    return records


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("plan", "smoke", "run", "report",
                                       "certify", "residues", "ladder"))
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--arm", default=ARM, choices=ARMS)
    ap.add_argument("--budget", type=int, default=PREFIX_BUDGET,
                    help=f"nodes per row, 1..{MAX_BUDGET} (ladder: "
                         + ", ".join(f"{b:,}" for b in LADDER) + ")")
    ap.add_argument("--rows-csv", default=None,
                    help="run a residue CSV instead of the whole screen")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--chunks", type=int, default=1)
    ap.add_argument("--chunk-index", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--names", default=None,
                    help="certify: comma-separated row names")
    args = ap.parse_args(argv)
    if args.command == "plan":
        plan()
    elif args.command == "smoke":
        run(args.out_dir + "_smoke", arm=args.arm, budget=args.budget,
            rows_csv=args.rows_csv, workers=1, chunks=1, chunk_index=1,
            limit=args.limit or 25, resume=False)
        report(args.out_dir + "_smoke", arm=args.arm, budget=args.budget,
               chunks=1, chunk_index=1)
    elif args.command == "ladder":
        ladder(args.out_dir, arm=args.arm, workers=args.workers,
               chunks=args.chunks, chunk_index=args.chunk_index)
    elif args.command == "run":
        run(args.out_dir, arm=args.arm, budget=args.budget,
            rows_csv=args.rows_csv, workers=args.workers, chunks=args.chunks,
            chunk_index=args.chunk_index, limit=args.limit,
            resume=not args.no_resume)
        report(args.out_dir, arm=args.arm, budget=args.budget,
               chunks=args.chunks, chunk_index=args.chunk_index)
        if not args.limit:
            residues(args.out_dir, arm=args.arm, budget=args.budget,
                     chunks=args.chunks, chunk_index=args.chunk_index)
    else:
        index = None if args.chunks > 1 else args.chunk_index
        if args.command == "report":
            report(args.out_dir, arm=args.arm, budget=args.budget,
                   chunks=args.chunks, chunk_index=index)
        elif args.command == "certify":
            print(certify(args.out_dir, arm=args.arm, budget=args.budget,
                          chunks=args.chunks, chunk_index=index,
                          names=args.names.split(",") if args.names else None,
                          limit=args.limit))
        else:
            residues(args.out_dir, arm=args.arm, budget=args.budget,
                     chunks=args.chunks, chunk_index=index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
