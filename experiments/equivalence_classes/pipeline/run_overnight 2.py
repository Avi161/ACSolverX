"""Overnight production ladder over the 126 class reps: the seam ceilings the probe never ran.

`run_probe.py` is the LOCAL probe -- hard-capped at 1,000 nodes/source, ~28-minute arms. This is
its PRODUCTION counterpart, for the follow-up the finding itself names (EQUIVALENCE_FINDING.md
section 3b): `seam` at `max_total` 30 and 32 (the never-run rungs of the ladder), plus 34
continued past the ~4% of budget the probe's time limit allowed, run for a night instead of to a
28-minute wall clock.

A budget above 1,000 nodes/source refuses to run unless ``ACSOLVERX_ALLOW_BIG=1`` -- the same
convention as `stable_ac/nocov/run_nocov.py`. Production budgets are user-authorized only
(2026-07-13: the user explicitly requested this 9-hour overnight ladder).

What a long unattended run needs beyond `run_probe.py`:

* **A rolling checkpoint.** `aut_multi_search` returns its merges only when it finishes, so a
  crash at hour 8 would lose every merge found -- exactly the defect of
  `experiments/lessons/heavy-mode-defers-solved-rows.md` (a computed result must reach disk).
  Every `--ckpt-every` pops the live merges, partition and counters are snapshotted to
  ``probe_<tag>.checkpoint.json``. The snapshot rides the same module-global `children` seam
  the levelset probe swaps, so `aut_search.py` itself stays untouched.

* **A memory guard on CURRENT rss** (``ps -o rss=``, never ``ru_maxrss`` -- the high-water mark
  never comes back down, see `experiments/lessons/gb-per-pres-sized-from-measured-memory.md`).
  Past ``--soft-gb`` the phase-1 memo is dropped: it is a pure cache, so clearing it costs
  recompute time and nothing else. Past ``--hard-gb`` the arm checkpoints and stops itself,
  keeping everything found so far. Four parallel arms on a 16 GB machine is the sizing case.

* **`roots` in the output** -- each source's raw canonical pair, Aut-minimal rep and the phi
  connecting them -- so any merge is verifiable by pure substitution without re-running
  Whitehead on the roots.

Usage (one arm; the ladder is four of these in parallel):

    ACSOLVERX_ALLOW_BIG=1 python3 run_overnight.py --tag overnight_seam30 \
        --max-total 30 --budget 1000000 --time 30600

Writes: results/equivalence_classes/probe/probe_<tag>.json  (run_probe schema + `roots`)
"""
import argparse
import gc
import json
import os
import subprocess
import sys
import time


# The repo root, found by walking up rather than by counting directory levels. A dirname chain
# encodes this file's depth and silently repoints at the wrong directory the moment it moves.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

import experiments.equivalence_classes.search.aut_search as aut_search  # noqa: E402
from experiments.equivalence_classes.search.aut_search import aut_key, aut_multi_search  # noqa: E402
from experiments.equivalence_classes.lib.acmoves import canon  # noqa: E402
from experiments.equivalence_classes.pipeline.run_probe import OUT, TRIVIAL, load_sources  # noqa: E402


class _MemAbort(Exception):
    """Raised out of the children seam when rss crosses --hard-gb; main keeps the checkpoint."""


def _rss_gb():
    """CURRENT resident set in GB. macOS ps reports KB; ru_maxrss would never decrease."""
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return int(out) / (1024 ** 2)
    except Exception:
        return 0.0


def _ser_merges(merges):
    return [{"kind": m["kind"], "a": m["a"], "b": m["b"], "at": list(m["at"]),
             "len_a": len(m["path_a"]), "len_b": len(m["path_b"]),
             "path_a": [[list(s[0]), s[1], list(s[2])] for s in m["path_a"]],
             "path_b": [[list(s[0]), s[1], list(s[2])] for s in m["path_b"]]}
            for m in merges]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--moves", choices=("seam", "full"), default="seam")
    ap.add_argument("--max-total", type=int, required=True)
    ap.add_argument("--budget", type=int, default=1_000_000)
    ap.add_argument("--time", type=float, default=30_600)
    ap.add_argument("--max-states", type=int, default=1_000_000)
    ap.add_argument("--ckpt-every", type=int, default=2000,
                    help="pops between checkpoint snapshots (rides the children seam)")
    ap.add_argument("--soft-gb", type=float, default=2.2,
                    help="rss above this drops the phase-1 memo (pure cache, safe to clear)")
    ap.add_argument("--hard-gb", type=float, default=2.8,
                    help="rss above this stops the arm, keeping its results")
    args = ap.parse_args()

    if args.budget > 1000 and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        sys.exit("budget > 1000 nodes/source is a PRODUCTION run: set ACSOLVERX_ALLOW_BIG=1. "
                 "Local searches stay under the 1,000-node cap (CLAUDE.md).")

    classes, sources, _ = load_sources(False)
    n_reps = len(classes)
    rep_names = {f"C{c['class_id']}" for c in classes}
    triv_idx = next(i for i, (n, _, _) in enumerate(sources) if n == TRIVIAL)

    print(f"[{args.tag}] sources={len(sources)} ({n_reps} class reps + TRIVIAL)")
    print(f"[{args.tag}] moves={args.moves} max_total={args.max_total} budget={args.budget} "
          f"time={args.time}s max_states={args.max_states} "
          f"guard=soft {args.soft_gb}GB / hard {args.hard_gb}GB", flush=True)

    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    ckpt_path = os.path.join(OUT, f"probe_{args.tag}.checkpoint.json")
    snap = {}          # last snapshot -- the final payload if the memory guard stops the arm

    def partition_of(dsu):
        comps = {}
        for i in range(len(sources)):
            comps.setdefault(dsu.find(i), []).append(sources[i][0])
        rc = [sorted(n for n in v if n in rep_names) for v in comps.values()]
        rc = [c for c in rc if c]
        solved = sorted(n for n in comps[dsu.find(triv_idx)] if n in rep_names)
        return rc, solved

    # --- the checkpoint + memory guard, riding the same module-global `children` seam the
    # levelset probe swaps. It is called exactly once per pop, from aut_multi_search's own
    # frame, so the live dsu/merges/counters are one sys._getframe away -- read-only.
    real_children = aut_search.children
    calls = [0]

    def guarded_children(*a, **kw):
        calls[0] += 1
        if calls[0] % args.ckpt_every == 0:
            rss = _rss_gb()
            try:
                loc = sys._getframe(1).f_locals
                rc, solved = partition_of(loc["dsu"])
                snap.update({
                    "pops": loc["popped"], "states": len(loc["st_rep"]),
                    "n_classes": len(rc), "new_merges": [c for c in rc if len(c) > 1],
                    "solved": solved, "merges": _ser_merges(loc["merges"]),
                })
                tmp = ckpt_path + ".tmp"
                with open(tmp, "w") as f:
                    json.dump({"tag": args.tag, "elapsed": round(time.time() - t0, 1),
                               "rss_gb": round(rss, 2), **snap}, f)
                os.replace(tmp, ckpt_path)
            except Exception as e:      # a failed snapshot must never kill the search
                print(f"[{args.tag}] checkpoint skipped: {e!r}", flush=True)
            if rss > args.soft_gb and len(aut_search._MEMO1) > 100_000:
                print(f"[{args.tag}] rss {rss:.2f}GB > soft {args.soft_gb}GB: dropping phase-1 "
                      f"memo ({len(aut_search._MEMO1)} entries)", flush=True)
                aut_search._MEMO1.clear()
                gc.collect()
                # Re-measure: the memo usually IS the memory. Judging the hard limit on the
                # pre-clear reading escalated a mitigated condition and stopped an arm 6h early.
                rss = _rss_gb()
                print(f"[{args.tag}] rss after memo drop: {rss:.2f}GB", flush=True)
            if rss > args.hard_gb:
                raise _MemAbort(f"rss {rss:.2f}GB > hard {args.hard_gb}GB")
        return real_children(*a, **kw)

    aut_search.children = guarded_children

    def progress(pops, states, comps_n):
        el = time.time() - t0
        print(f"[{args.tag}] {pops:>9} pops {states:>9} states {comps_n:>4} comps "
              f"{el:>7.0f}s ({pops / max(el, 1e-9):.1f}/s) rss={_rss_gb():.2f}GB", flush=True)

    mem_abort = None
    dsu = merges = stats = roots_of = None
    try:
        dsu, merges, stats, roots_of = aut_multi_search(
            sources, nodes_per_source=args.budget, max_total=args.max_total,
            seam_only=(args.moves == "seam"), max_states=args.max_states,
            progress=progress, time_limit=args.time)
    except _MemAbort as e:
        mem_abort = str(e)
        print(f"[{args.tag}] MEMORY GUARD STOP: {e} -- keeping the last checkpoint's results",
              flush=True)

    elapsed = time.time() - t0
    if mem_abort is None:
        rc, solved = partition_of(dsu)
        payload = {"pops": stats["popped"], "states": stats["states"],
                   "n_classes": len(rc), "new_merges": [c for c in rc if len(c) > 1],
                   "solved": solved, "merges": _ser_merges(merges)}
        stats_out = {**stats, "seconds": round(elapsed, 1)}
    else:
        payload = snap or {"pops": 0, "states": 0, "n_classes": n_reps,
                           "new_merges": [], "solved": [], "merges": []}
        stats_out = {"popped": payload["pops"], "states": payload["states"], "capped": False,
                     "timed_out": False, "seconds": round(elapsed, 1)}
    stats_out["mem_abort"] = mem_abort

    # roots: recomputed rather than taken from the search, so they exist on the abort path too.
    # aut_key is deterministic and memoised; on the 127 sources this is seconds.
    roots = {}
    for name, r1, r2 in sources:
        p = canon(r1, r2)
        _, rep, phi = aut_key(p)
        roots[name] = {"raw": list(p), "aut_rep": list(rep), "phi": phi}

    print(f"\n{'=' * 66}")
    print(f"[{args.tag}] pops={payload['pops']} states={payload['states']} {elapsed:.0f}s"
          f"{'  [STATE CAP]' if mem_abort is None and stats['capped'] else ''}"
          f"{'  [TIME LIMIT]' if mem_abort is None and stats.get('timed_out') else ''}"
          f"{'  [MEM GUARD]' if mem_abort else ''}")
    print(f"[{args.tag}] CLASSES over the {n_reps} : {payload['n_classes']}   (baseline {n_reps})")
    print(f"[{args.tag}] *** NEW MERGES *** : {len(payload['new_merges'])}  "
          f"{payload['new_merges']}")
    print(f"[{args.tag}] SOLVED (hit trivial): {len(payload['solved'])}  {payload['solved']}")

    path = os.path.join(OUT, f"probe_{args.tag}.json")
    with open(path, "w") as f:
        json.dump({
            "tag": args.tag,
            "config": {"moves": args.moves, "max_total": args.max_total,
                       "budget": args.budget, "time_limit": args.time,
                       "max_states": args.max_states, "sources": len(sources)},
            "stats": stats_out,
            "n_classes": payload["n_classes"],
            "new_merges": payload["new_merges"],
            "solved": payload["solved"],
            "merges": payload["merges"],
            "roots": roots,
        }, f, indent=1)
    print(f"[{args.tag}] wrote {path}", flush=True)
    try:
        os.remove(ckpt_path)           # the final json supersedes the rolling checkpoint
    except OSError:
        pass


if __name__ == "__main__":
    main()
