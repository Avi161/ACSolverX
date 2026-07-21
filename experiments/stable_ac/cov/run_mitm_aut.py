"""T5 — Aut-quotient meet-in-the-middle (MITM) diagnostic runner.

For each target presentation ``P = (r1, r2)`` this runs the shipped Aut-quotient
search (``experiments/equivalence_classes/search/aut_search.py:aut_multi_search``)
with exactly two sources — ``P`` and the TRIVIAL presentation ``(x, y)`` — and
``stop_when_merged=True``, so the search halts the instant the two sources land in
one union-find component. It sweeps the Aut-minimal-length CEILING (``max_total``,
the *binding* knob per ``experiments/lessons/ceiling-not-budget-was-binding.md``),
not just the node budget: a higher ceiling is a bigger search space, not more pops
of the same one.

What a verified merge certifies (state this exactly)
----------------------------------------------------
A merge means the target's Aut(F2)-class connects to TRIVIAL's Aut(F2)-class in the
ACA graph — a chain of "change of variables, then an AC move", each edge preserving
AC-triviality. By the **stable ambient automorphism principle**
(``literature/proofs/PROOFS.tex``, Theorem "Stable ambient automorphism principle",
``thm:stable``) a balanced presentation of the trivial group is *stably*
AC-equivalent to every automorphic image of itself, so an ACA path from the target
to ``(x, y)`` certifies **STABLE AC-triviality of the target**.

It is NOT sufficient for 2-generator (unstable) AC-triviality: the *unstable*
pairwise ambient principle is not a theorem — mms02 asserts it without proof and
Panteleev–Ushakov conjecture it false even for presentations of 1
(``experiments/lessons/ambient-principle-unstable-is-not-a-theorem.md``). This
runner therefore never claims unstable AC-triviality from a merge, and in
particular never announces AK(3) settled on a merge alone.

Independent verification (advisor reconciliation item 1)
--------------------------------------------------------
Every TRIVIAL-connecting merge is replayed through TWO independent stacks before
any solve language is emitted:
  1. ``verify_certificates.py:replay_path`` — replays each ``(move, phi, rep)``
     step through the repo's numba canonicaliser, checking every ``phi`` is a
     genuine automorphism by Nielsen reduction; and
  2. ``verify_new_merge.py:replay`` — the same replay in the pure-Python word
     algebra of ``lib/words.py`` (``replay_move`` / ``apply_hom`` / ``canon_pair``),
     which shares no implementation with the search.
Both stacks must land BOTH paths on the recorded meeting class, or ``verify_ok`` is
False and the merge is flagged for inspection, never announced as a solve.

CPU only. From the repo root::

    .venv/bin/python3 -m experiments.stable_ac.cov.run_mitm_aut --shortest 5
"""

import argparse
import csv
import json
import os
import time

from experiments.equivalence_classes.search.aut_search import aut_multi_search
from experiments.equivalence_classes.verify import verify_certificates as vc
from experiments.equivalence_classes.verify import verify_new_merge as vnm
from experiments.run_baseline import _persist, _repair_jsonl


def _repo_root():
    """Repo root by walking up until experiments/ + data/ appear (never a dirname
    chain, which encodes this file's depth and repoints silently when it moves)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()

# The Akbulut–Kirby AK(3) literal (never carried in aca_124.csv), always a target
# unless --no-ak3. A merge here would be a STABLE result only; AK(3) is OPEN and is
# never announced settled on this tool alone (advisor item 1).
AK3 = ("AK3", "xxxYYYY", "xyxYXY")
TRIVIAL = ("TRIVIAL", "x", "y")
ACA_124_CSV = os.path.join(ROOT, "data", "ms_unsolved_reps", "aca_124.csv")

DEFAULT_CEILINGS = [26, 28, 30]   # local ladder; production sweeps higher on Colab
DEFAULT_NPS = 1000                # nodes_per_source; > 1000 needs ACSOLVERX_ALLOW_BIG=1
DEFAULT_MOVE_CAP = 48             # aut_search's per-relator move cap (fixed, not swept)
DEFAULT_OUT_DIR = os.path.join(ROOT, "results", "stable_ac", "mitm")


def _require_nps_allowed(nps):
    """Local-safety guard, mirroring run_nocov: nodes_per_source > 1000 needs
    ACSOLVERX_ALLOW_BIG=1. Production budgets belong on Colab."""
    if nps > 1000 and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(
            f"refusing nodes_per_source {nps} > 1000: local runs stay small; "
            f"set ACSOLVERX_ALLOW_BIG=1 to confirm a production (Colab) run")


def _run_filename(ceiling, nps):
    """Date-less filename identity: the two knobs that change every row's result
    (the ceiling and the per-source budget) and nothing else."""
    return f"mitm_aut_ceil{ceiling}_nps{nps}.jsonl"


_GIT_COMMIT = False   # False = unresolved (None is a valid answer)


def _git_commit():
    """HEAD of this checkout; None outside a git repo. Provenance only — never
    part of the resume identity."""
    global _GIT_COMMIT
    if _GIT_COMMIT is False:
        import subprocess
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True, text=True, timeout=10)
            _GIT_COMMIT = out.stdout.strip() or None
        except Exception:
            _GIT_COMMIT = None
    return _GIT_COMMIT


def load_targets(names=None, shortest=None, include_ak3=True, csv_path=ACA_124_CSV):
    """Target list ``[(name, r1, r2), ...]``.

    ``names`` selects those aca_124 rows by name; else ``shortest`` takes the N
    rows of smallest total relator length; else every row. AK(3) is prepended
    unless ``include_ak3`` is False.
    """
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    if names:
        wanted = set(names)
        selected = [r for r in rows if r["name"] in wanted]
    elif shortest is not None:
        selected = sorted(rows, key=lambda r: len(r["r1"]) + len(r["r2"]))[:shortest]
    else:
        selected = rows
    targets = [(r["name"], r["r1"], r["r2"]) for r in selected]
    if include_ak3:
        targets = [AK3] + targets
    return targets


def _read_done(out_path):
    """Names already written to ``out_path`` (the per-file resume key), tolerating
    an unrepaired torn FINAL line so resume never crashes on it."""
    done = set()
    if not os.path.exists(out_path):
        return done
    with open(out_path) as f:
        lines = [ln.strip() for ln in f]
    for i, ln in enumerate(lines):
        if not ln:
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            if i == len(lines) - 1:
                print(f"    WARNING: ignoring a truncated final line in "
                      f"{os.path.basename(out_path)}", flush=True)
                break
            raise
        done.add(row["name"])
    return done


def _verify_connecting_merges(merges, roots_of, name_to_idx, name_to_pair,
                              target_name):
    """Replay every TRIVIAL-connecting merge through BOTH independent stacks.

    Returns ``(verify_ok, connecting)``. A merge connects the target to TRIVIAL
    when its two source names are exactly ``{target_name, "TRIVIAL"}`` (with two
    sources, that is every merge). ``verify_ok`` is True only if, for every such
    merge, BOTH paths land on the recorded meeting class (``at``) under BOTH the
    numba replay (``verify_certificates.replay_path``, from the search's own
    Aut-canonical root) and the pure-Python replay (``verify_new_merge.replay``,
    recomputed from the ORIGINAL presentation pair). An empty ``connecting`` (a
    dsu merge with no naming evidence) is treated as unverifiable → False.
    """
    connecting = [m for m in merges
                  if {m["a"], m["b"]} == {target_name, "TRIVIAL"}]
    if not connecting:
        return False, connecting
    ok = True
    for m in connecting:
        at = tuple(m["at"])
        for side in ("a", "b"):
            nm = m[side]
            path = m[f"path_{side}"]
            steps = [(tuple(s[0]), s[1], tuple(s[2])) for s in path]
            # stack 1: numba canonicaliser, starting from the search's aut-rep root
            errs = []
            aut_rep = roots_of[name_to_idx[nm]][1]
            end1 = vc.replay_path(aut_rep, steps, f"{nm}.{side}", errs)
            # stack 2: pure-Python words substitution, from the ORIGINAL pair
            try:
                end2 = vnm.replay(name_to_pair[nm], path)
            except Exception:
                end2 = None
            if errs or end1 != at or end2 != at:
                ok = False
    return ok, connecting


def run_target(name, r1, r2, ceiling, nps, move_cap=DEFAULT_MOVE_CAP,
               time_limit=None):
    """One target × (ceiling, nps). Returns the jsonl row dict.

    ``merged`` means the TARGET's component contains TRIVIAL specifically — decided
    from the returned union-find, never from "some merge happened".
    """
    sources = [(name, r1, r2), TRIVIAL]
    name_to_idx = {s[0]: i for i, s in enumerate(sources)}
    name_to_pair = {s[0]: (s[1], s[2]) for s in sources}

    dsu, merges, stats, roots_of = aut_multi_search(
        sources, nodes_per_source=nps, max_total=ceiling, move_cap=move_cap,
        stop_when_merged=True, time_limit=time_limit)

    merged = dsu.find(name_to_idx[name]) == dsu.find(name_to_idx["TRIVIAL"])
    row = {
        "name": name, "r1": r1, "r2": r2,
        "ceiling": ceiling, "nodes_per_source": nps,
        "merged": merged,
        "n_merges": len(merges),
        "states": stats["states"],
        "popped": stats["popped"],
        "capped": stats["capped"],
        "timed_out": stats["timed_out"],
        "components": stats["components"],
        "seconds": stats["seconds"],
        "verify_ok": None,
        "git_commit": _git_commit(),
    }
    if merged:
        verify_ok, connecting = _verify_connecting_merges(
            merges, roots_of, name_to_idx, name_to_pair, name)
        row["verify_ok"] = verify_ok
        # the full merge dict(s) with both paths, on a TRIVIAL-connecting merge
        row["merge"] = connecting[0] if connecting else None
        if len(connecting) > 1:
            row["merges_all"] = connecting
    return row


def _print_target(row):
    """Progress line. Solve language ONLY on a verified merge — a merged-but-
    unverified row is flagged, never announced (advisor item 1)."""
    tag = (f"    {row['name']:8} ceil={row['ceiling']} "
           f"nps={row['nodes_per_source']}: ")
    if row["merged"] and row["verify_ok"]:
        print(tag + f"MERGED & VERIFIED — Aut-class connects to TRIVIAL "
              f"(stable-AC-trivial) | states={row['states']} "
              f"popped={row['popped']}", flush=True)
    elif row["merged"]:
        print(tag + f"*** MERGED BUT UNVERIFIED — NOT a solve, flag & inspect "
              f"(verify_ok={row['verify_ok']}) | states={row['states']}",
              flush=True)
    else:
        print(tag + f"no merge | states={row['states']} popped={row['popped']} "
              f"capped={row['capped']} timed_out={row['timed_out']}", flush=True)


def run_mitm(targets, ceiling, nps, out_dir=DEFAULT_OUT_DIR, resume=True,
             move_cap=DEFAULT_MOVE_CAP, time_limit=None, progress=True):
    """Sweep every target at one (ceiling, nps) into one date-less jsonl.

    Crash-safe (fsync per row via ``_persist``), resumable by target ``name``
    (``_repair_jsonl`` first, before any append). Returns the output path.
    """
    _require_nps_allowed(nps)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, _run_filename(ceiling, nps))

    _repair_jsonl(out_path)
    done = _read_done(out_path) if resume else set()
    todo = [t for t in targets if t[0] not in done]
    print(f"=== mitm_aut | ceiling={ceiling} | nps={nps} | {len(targets)} targets"
          f" | {len(done)} done, {len(todo)} to run | -> {out_path}", flush=True)
    if not todo:
        print("    nothing to do (all done).", flush=True)

    with open(out_path, "a") as f:
        for name, r1, r2 in todo:
            t0 = time.time()
            row = run_target(name, r1, r2, ceiling, nps, move_cap=move_cap,
                             time_limit=time_limit)
            row["wall_seconds"] = round(time.time() - t0, 3)
            f.write(json.dumps(row) + "\n")
            _persist(f)
            if progress:
                _print_target(row)
    return out_path


def main():
    ap = argparse.ArgumentParser(
        description="T5 Aut-quotient meet-in-the-middle diagnostic (target vs TRIVIAL)")
    ap.add_argument("--names", type=str, default=None,
                    help="comma-separated aca_124 names to target")
    ap.add_argument("--shortest", type=int, default=None,
                    help="target the N shortest aca_124 reps by total relator length")
    ap.add_argument("--no-ak3", action="store_true",
                    help="exclude the AK(3) literal from the targets")
    ap.add_argument("--ceilings", type=str, default=None,
                    help="comma-separated max_total ceiling ladder (default 26,28,30)")
    ap.add_argument("--nps", type=int, default=DEFAULT_NPS,
                    help="nodes_per_source (default 1000; > 1000 needs ACSOLVERX_ALLOW_BIG=1)")
    ap.add_argument("--out-dir", type=str, default=DEFAULT_OUT_DIR)
    ap.add_argument("--time-limit", type=float, default=None,
                    help="per-target wall-clock ceiling in seconds")
    args = ap.parse_args()

    names = [s for s in args.names.split(",") if s] if args.names else None
    shortest = args.shortest
    if names is None and shortest is None:
        shortest = 5          # the pilot default: AK(3) + 5 shortest aca_124 reps
    ceilings = ([int(c) for c in args.ceilings.split(",") if c]
                if args.ceilings else list(DEFAULT_CEILINGS))

    _require_nps_allowed(args.nps)   # fail fast, before any file I/O or search
    targets = load_targets(names=names, shortest=shortest,
                           include_ak3=not args.no_ak3)
    print(f"targets ({len(targets)}): {[t[0] for t in targets]}", flush=True)
    print(f"ceilings: {ceilings} | nps: {args.nps}", flush=True)
    for ceiling in ceilings:
        run_mitm(targets, ceiling, args.nps, out_dir=args.out_dir,
                 time_limit=args.time_limit)


if __name__ == "__main__":
    main()
