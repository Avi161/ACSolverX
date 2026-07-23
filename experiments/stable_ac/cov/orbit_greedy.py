"""Run the baseline greedy from mu-ladder orbits (``mu_ladder_big`` provenance).

Every row of a ``*_orbits.jsonl`` is a concrete 2-generator pair reached from
its class's original by a chain of subword-CoV hops (stabilize → substitute →
isolate → destabilize). So each orbit is a fresh *start* for the same question,
and the ladder already paid for it at zero search nodes.

**What a solve proves.** The chain is ``original ~st orbit`` and the search
gives ``orbit ~AC (x,y)``, so a solved orbit proves the original is *stably*
AC-trivial — NOT AC-trivial. AK(3) is the standing warning: stably trivial,
AC status open. For the same reason ``path_length`` here is the search's own
length from the transformed start and is **not** a certificate for the
original (``AUTOMORPHISMS_COV.md`` †); only ``solved`` and ``nodes_explored``
compare like for like.

**Control.** Rung 0 of every class IS the original pair, so the control is
derived from the same file and run at the SAME ``cap`` and budget — a CoV row
compared against a control at a different ``max_relator_length`` is not a
comparison (lesson: max-relator-length-is-inert).

**Relabels.** The ladder dedups by Aut-orbit, so each stored pair is one
representative of its orbit. The greedy reads *strings*, not orbits, and in
the one-hop sweep relabels supplied 14 of 17 unsolved→solved flips — so a
selected orbit enters as its ``relabels`` signed-permutation images, not as
one string.

Precedent for the whole idea: ``AUTOMORPHISMS_COV.md`` — one-hop CoV starts,
66 presentations, budget 100, **17 flips**.

CLI::

    python3 -m experiments.stable_ac.cov.orbit_greedy \\
        --orbits 'results/stable_ac/mu_scan/*_orbits.jsonl' \\
        --budget 100 --per-class 200 --strategy lowest
"""
import argparse
import glob
import json
import os
import sys
import time

from experiments import run_baseline
from experiments.equivalence_classes.lib import words

MAX_BUDGET = 1_000          # local ceiling; production budgets are the user's

DEFAULTS = dict(
    orbits="results/stable_ac/mu_scan/*_orbits.jsonl",
    budget=100,
    cap=48,                 # per-relator cap; starts longer than this are
                            # SKIPPED and counted (never silently dropped)
    per_class=200,
    strategy="lowest",      # lowest | spread | all
    relabels=8,             # 1 = the stored representative only
    cyclic_reduce=True,
    high_speedup=True,      # result-neutral (run_cov._search re-solves for path)
    out_dir="results/stable_ac/orbit_greedy",
)


def _repo_root(start=None):
    """Walk up to the dir holding experiments/ + data/ (never a dirname chain)."""
    root = os.path.abspath(start or os.getcwd())
    while root != "/" and not (os.path.isdir(os.path.join(root, "experiments"))
                               and os.path.isdir(os.path.join(root, "data"))):
        root = os.path.dirname(root)
    return root


# ---------------------------------------------------------------- orbit input

def load_orbits(paths):
    """All orbit rows from the given jsonl files, torn trailing line tolerated.

    Returns (rows, n_torn). Rows keep file order, which is the ladder's
    discovery order — deterministic.
    """
    rows, torn = [], 0
    for path in paths:
        with open(path) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    rows.append(json.loads(ln))
                except json.JSONDecodeError:
                    torn += 1          # only ever the last line of a live file
    return rows, torn


def select(rows, per_class, strategy):
    """Deterministic per-class selection of orbit rows to search.

    ``lowest`` : the ``per_class`` smallest mu (the moat rim).
    ``spread`` : ``per_class`` evenly spaced over the mu-sorted list, so every
                 mu band is represented — the A/B partner for ``lowest``, and
                 the only way to learn whether solvability tracks mu at all.
    ``all``    : everything.

    Rung 0 is the original and is never selected as an orbit; it becomes the
    control instead.
    """
    by_class = {}
    for r in rows:
        if r["rung"] == 0:
            continue
        by_class.setdefault(r["pres_id"], []).append(r)
    out = {}
    for pid, rs in by_class.items():
        rs = sorted(rs, key=lambda r: (r["mu"], r["pair"][0], r["pair"][1]))
        if strategy == "all" or per_class <= 0 or per_class >= len(rs):
            out[pid] = rs
        elif strategy == "lowest":
            out[pid] = rs[:per_class]
        elif strategy == "spread":
            step = len(rs) / per_class
            out[pid] = [rs[int(i * step)] for i in range(per_class)]
        else:
            raise ValueError(f"unknown strategy {strategy!r}")
    return out


def controls(rows):
    """{pres_id: (r1, r2)} from the rung-0 rows — the untransformed originals."""
    return {r["pres_id"]: (r["pair"][0], r["pair"][1])
            for r in rows if r["rung"] == 0}


def relabel_starts(pair, n):
    """Up to ``n`` signed-permutation images of ``pair``, deterministic order.

    n == 1 gives the stored representative unchanged (name ``id``), so a
    relabels=1 run is exactly 'one start per orbit'.
    """
    if n <= 1:
        return [("id", pair[0], pair[1])]
    out = []
    for name, img in words.SIGNED_PERMS[:n]:
        p = words.apply_pair(pair, img)
        out.append((name, p[0], p[1]))
    return out


# ------------------------------------------------------------- run identity

def _run_prefix(c, n_classes):
    """Every knob that changes the result, and none that doesn't.

    ``high_speedup`` is result-neutral (same pop order, path re-solved) so it
    stays out — a file must resume across the two modes.
    """
    cyc = "" if c["cyclic_reduce"] else "_nocyc"
    return (f"orbit_greedy_b{c['budget']}_cap{c['cap']}_{c['strategy']}"
            f"{c['per_class']}_rl{c['relabels']}_n{n_classes}{cyc}")


def _out_path(c, n_classes, root):
    d = os.path.join(root, c["out_dir"])
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, _run_prefix(c, n_classes) + ".jsonl")


def _done_keys(path):
    """({key}, n_solved) already on disk; repairs a torn trailing line first."""
    done, n_solved = set(), 0
    if not os.path.exists(path):
        return done, n_solved
    good, torn = [], False
    with open(path, "rb") as f:
        data = f.read()
    for ln in data.split(b"\n"):
        if not ln.strip():
            continue
        try:
            row = json.loads(ln)
        except json.JSONDecodeError:
            torn = True                # only the last line can be torn
            continue
        good.append(ln)
        done.add((row["kind"], row["pres_id"], row.get("rep_key", ""),
                  row.get("relabel", "")))
        n_solved += int(bool(row["solved"]))
    if torn:                           # repair BEFORE the first append
        with open(path, "wb") as f:
            f.write(b"\n".join(good) + (b"\n" if good else b""))
    return done, n_solved


def _rep_key(rep):
    return "|".join(rep) if isinstance(rep, (list, tuple)) else str(rep)


# ------------------------------------------------------------------- search

def _search(c, r1, r2):
    """run_cov._search's contract: fast search, re-solve a hit for its path.

    ``reserve_states`` is result-neutral (address space, lazily faulted) and
    only avoids the compact arena's grow-and-copy on every single search; the
    ~130 states per popped node is measured, not a guess.
    """
    hs = bool(c["high_speedup"])
    reserve = c["budget"] * 150
    stats = run_baseline.greedy_search(
        r1, r2, c["budget"], max_relator_length=c["cap"],
        cyclic_reduce=c["cyclic_reduce"], high_speedup=hs,
        reserve_states=reserve)
    if hs and stats["solved"]:
        stats = run_baseline.greedy_search(
            r1, r2, c["budget"], max_relator_length=c["cap"],
            cyclic_reduce=c["cyclic_reduce"], high_speedup=False)
    return stats


def _stat_fields(st):
    """The readout. ``min_total`` is the LOWEST total relator length the search
    reached (trivial = 2), i.e. how far the greedy actually reduced this start
    — the only progress signal available at a budget where nothing solves."""
    return {"solved": bool(st["solved"]),
            "nodes_explored": st["nodes_explored"],
            "path_length": st.get("path_length"),
            "min_total": st["min_relator_length"],
            "max_total": st["max_relator_length"]}


def _too_long(r1, r2, cap):
    return max(len(r1), len(r2)) > cap


def run(**overrides):
    c = dict(DEFAULTS, **{k: v for k, v in overrides.items() if v is not None})
    if c["budget"] > MAX_BUDGET:
        raise ValueError(f"budget {c['budget']} > local ceiling {MAX_BUDGET}")
    root = _repo_root()
    paths = sorted(glob.glob(os.path.join(root, c["orbits"]))
                   or glob.glob(c["orbits"]))
    if not paths:
        raise SystemExit(f"no orbit files matched {c['orbits']!r}")

    rows, torn = load_orbits(paths)
    ctrl = controls(rows)
    sel = select(rows, c["per_class"], c["strategy"])
    n_classes = len(ctrl)
    out_path = _out_path(c, n_classes, root)
    done, n_solved = _done_keys(out_path)

    n_starts = sum(len(v) for v in sel.values()) * max(1, c["relabels"])
    print(f"{len(rows)} orbit rows ({torn} torn) from {len(paths)} file(s) | "
          f"{n_classes} classes | {c['strategy']} {c['per_class']}/class x "
          f"{c['relabels']} relabels = {n_starts} starts", flush=True)
    print(f"-> {os.path.basename(out_path)} (resume: {len(done)} done, "
          f"{n_solved} solved)", flush=True)

    skipped = 0
    t0 = time.monotonic()
    n_new = 0
    with open(out_path, "a") as f:
        for pid in sorted(ctrl):
            # control first: a flip is only defined against a same-cap control
            key = ("control", pid, "", "")
            if key not in done:
                r1, r2 = ctrl[pid]
                if _too_long(r1, r2, c["cap"]):
                    skipped += 1
                else:
                    st = _search(c, r1, r2)
                    f.write(json.dumps({
                        "kind": "control", "pres_id": pid, "rung": 0,
                        "mu": len(r1) + len(r2), "rep_key": "", "relabel": "",
                        "r1": r1, "r2": r2, **_stat_fields(st),
                        "budget": c["budget"], "cap": c["cap"]}) + "\n")
                    f.flush()
                    n_new += 1

            for orow in sel.get(pid, []):
                rk = _rep_key(orow["rep"])
                for name, r1, r2 in relabel_starts(tuple(orow["pair"]),
                                                   c["relabels"]):
                    if ("orbit", pid, rk, name) in done:
                        continue
                    if _too_long(r1, r2, c["cap"]):
                        skipped += 1
                        continue
                    st = _search(c, r1, r2)
                    f.write(json.dumps({
                        "kind": "orbit", "pres_id": pid, "rung": orow["rung"],
                        "mu": orow["mu"], "rep_key": rk, "relabel": name,
                        "r1": r1, "r2": r2, **_stat_fields(st),
                        "budget": c["budget"], "cap": c["cap"]}) + "\n")
                    n_new += 1
                    n_solved += int(bool(st["solved"]))
                f.flush()
            el = time.monotonic() - t0
            print(f"  {pid}: {n_new} searched, {n_solved} solved, {el:.0f}s",
                  flush=True)

    if skipped:
        print(f"SKIPPED {skipped} start(s): a relator exceeded cap="
              f"{c['cap']} (raise --cap to include them)", flush=True)
    return out_path


# ------------------------------------------------------------------- report

def report(path):
    """Two censuses.

    FLIPS  — control unsolved, some orbit start solves. The headline when the
             budget is big enough for anything to solve at all.
    REDUCE — the lowest total relator length the greedy REACHED from any orbit
             start vs from the control. At budgets where nothing solves this
             is the only progress signal, and it is on the same scale as mu
             (both are total length; trivial = 2).
    """
    ctrl, orbits = {}, {}
    n_orbit = n_orbit_solved = 0
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if row["kind"] == "control":
                ctrl[row["pres_id"]] = row
            else:
                n_orbit += 1
                n_orbit_solved += int(bool(row["solved"]))
                orbits.setdefault(row["pres_id"], []).append(row)

    flips = {p: [r for r in rs if r["solved"]] for p, rs in orbits.items()
             if not ctrl.get(p, {}).get("solved", False)
             and any(r["solved"] for r in rs)}
    print(f"controls: {sum(bool(r['solved']) for r in ctrl.values())}"
          f"/{len(ctrl)} solved")
    print(f"orbit starts: {n_orbit_solved}/{n_orbit} solved "
          f"({100.0 * n_orbit_solved / n_orbit if n_orbit else 0:.1f}%)")
    print(f"FLIPS (control unsolved, an orbit start solves): {len(flips)}")
    for pid in sorted(flips):
        best = min(flips[pid], key=lambda r: r["nodes_explored"])
        print(f"  {pid}: {len(flips[pid])} solving start(s); best "
              f"{best['nodes_explored']} nodes at rung {best['rung']}, "
              f"mu {best['mu']}, relabel {best['relabel']}")

    print("\nREDUCTION: lowest total length the greedy reached "
          "(start -> reached; trivial = 2)")
    print(f"{'class':10s} {'ctrl':>14s} | {'best orbit start':>18s} | beats ctrl")
    n_better = 0
    for pid in sorted(ctrl):
        cr = ctrl[pid]
        rs = orbits.get(pid, [])
        if not rs:
            continue
        best = min(rs, key=lambda r: (r["min_total"], r["mu"]))
        n_beat = sum(1 for r in rs if r["min_total"] < cr["min_total"])
        n_better += int(best["min_total"] < cr["min_total"])
        flag = " <== LOWER" if best["min_total"] < cr["min_total"] else ""
        print(f"{pid:10s} {cr['mu']:5d} -> {cr['min_total']:<5d} | "
              f"{best['mu']:6d} -> {best['min_total']:<5d} "
              f"(rung {best['rung']}) | {n_beat:5d}/{len(rs)}{flag}")
    print(f"classes where an orbit start out-reduced the control: "
          f"{n_better}/{len(ctrl)}")
    return flips


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--orbits", default=DEFAULTS["orbits"])
    ap.add_argument("--budget", type=int, default=DEFAULTS["budget"])
    ap.add_argument("--cap", type=int, default=DEFAULTS["cap"])
    ap.add_argument("--per-class", type=int, default=DEFAULTS["per_class"])
    ap.add_argument("--strategy", default=DEFAULTS["strategy"],
                    choices=["lowest", "spread", "all"])
    ap.add_argument("--relabels", type=int, default=DEFAULTS["relabels"])
    ap.add_argument("--out-dir", default=DEFAULTS["out_dir"])
    ap.add_argument("--no-high-speedup", action="store_true")
    ap.add_argument("--report-only", metavar="JSONL")
    a = ap.parse_args(argv)
    if a.report_only:
        report(a.report_only)
        return 0
    path = run(orbits=a.orbits, budget=a.budget, cap=a.cap,
               per_class=a.per_class, strategy=a.strategy,
               relabels=a.relabels, out_dir=a.out_dir,
               high_speedup=not a.no_high_speedup)
    print()
    report(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
