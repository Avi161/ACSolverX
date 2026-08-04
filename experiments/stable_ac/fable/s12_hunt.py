"""S12 Stable Certificate Hunt — orchestrator instrument.

Implements the method of ``results/stable_ac/theory/fable/S12_CERTIFICATE_HUNT.md``:
stabilize ``k`` times, search the AC move graph, and decide orientable thickenability at
every state.  A hit (SPHERICAL, i.e. gamma_N = 0) is a Lackenby Thm 1.3 certificate: the
state is AC-trivializable, so the input is stably AC-trivial.

Move weights follow the measured flip rates of ``S6_MOVE_CLASSIFICATION.md``:

* the engine is the conjugated AC2 slide ``r_i <- cyclered(r_i * u r_j^{eps} u^{-1})`` —
  the only move measured to CREATE the certificate (73 creates / 1,863 pairs);
* free and cyclic reduction is applied always and never searched backwards (move (0)
  creates in 315/2,510 and destroys in 0/997, so spiked spellings cannot beat the reduced
  one);
* bare AC3 conjugation is NOT proposed (315 destroys / 0 creates in 3,507).

Decision stack, in order: the R1c-v2 cut-scheme solver (fast, certified), then the exact
factorial census under a cap, then UNDECIDED.  Nothing is ever converted into a NO — an
out-of-scope or over-budget state is recorded as undecided, exactly as the rest of this
project's solvers do.

One-sided by construction.  Silence is worth exactly the measured detection rate, so every
run carries a positive ladder of presentations that ARE AC-trivial (solved Miller-Schupp
instances from ``data/ms640_solved.txt``) put through the identical pipeline and budget.

CLI (all budgets small by default; see ``PROCESS_GUARD.md``):

    python -m experiments.stable_ac.fable.s12_hunt --nodes 40 --kstab 1 --limit 124
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import time
from pathlib import Path

import experiments.stable_ac.fable.neuwirth_cut_schemes as CS
from experiments.stable_ac.fable.neuwirth_rank_n import (
    build_link_n, census_size, gamma_N_factorial_n)

ALPHA = "abcdefghijklmnopqrstuvwxyz"
REPO = Path(__file__).resolve().parents[3]
U124_REF = "origin/cursor/heur-u124-s20mk2-a42e:data/ms_unsolved_reps/aca_124.csv"


# --------------------------------------------------------------------------- words

def inv(w: str) -> str:
    return "".join(c.swapcase() for c in reversed(w))


def freered(w: str) -> str:
    out: list[str] = []
    for c in w:
        if out and out[-1].swapcase() == c:
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyclered(w: str) -> str:
    w = freered(w)
    while len(w) >= 2 and w[0].swapcase() == w[-1]:
        w = freered(w[1:-1])
    return w


def canon(words) -> tuple:
    """Seen-set key on cyclically REDUCED forms (filed trap: harvest-dedup-on-reduced-forms).

    Each relator is replaced by the lexicographically least rotation of itself or its
    inverse, and the tuple is sorted, so relator order, rotation and inversion collapse.
    """
    out = []
    for w in words:
        w = cyclered(w)
        if not w:
            out.append("")
            continue
        cands = [w[i:] + w[:i] for i in range(len(w))]
        iw = inv(w)
        cands += [iw[i:] + iw[:i] for i in range(len(iw))]
        out.append(min(cands))
    return tuple(sorted(out))


# --------------------------------------------------------------------------- decide

UNDECIDED = "UNDECIDED"


def decide(words, census_cap: int = 200_000) -> dict:
    """R1c-v2 cut-scheme solver first, exact census as fallback.  Never returns a false NO."""
    words = tuple(w for w in words if w)
    gens = tuple(sorted(set("".join(words).lower())))
    if len(gens) < 2:
        return {"verdict": UNDECIDED, "method": "degenerate"}
    try:
        support = CS.classify_cut_support(words, gens)
        if support.kind != CS.UNSUPPORTED:
            d = CS.solve_cut_schemes(words, gens, support=support)
            return {"verdict": d.verdict,
                    "method": ("r1c_v2_nonplanar" if support.kind == CS.NONPLANAR
                               else "r1c_v2_solver")}
    except Exception as exc:                                   # fail closed, never a NO
        return {"verdict": UNDECIDED, "method": f"solver_exc:{type(exc).__name__}"}
    try:
        if census_size(build_link_n(words, gens), gens) > census_cap:
            return {"verdict": UNDECIDED, "method": "census_over_cap"}
        c = gamma_N_factorial_n(words, gens, cap_rotations=census_cap,
                                keep_accepting=False)
    except Exception as exc:
        return {"verdict": UNDECIDED, "method": f"census_exc:{type(exc).__name__}"}
    if c["status"] != "OK" or c["minimum_defect"] is None:
        return {"verdict": UNDECIDED, "method": "census_status"}
    return {"verdict": "SPHERICAL" if c["minimum_defect"] == 0 else "NOT_SPHERICAL",
            "method": "factorial_census", "defect": c["minimum_defect"]}


# --------------------------------------------------------------------------- search

def slides(words, gens, rng, max_rel, max_tot, k):
    """k sampled conjugated AC2 slides; bare AC3 is deliberately not proposed."""
    n = len(words)
    out = []
    for _ in range(k):
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j:
            continue
        rj = words[j]
        if not rj:
            continue
        if rng.random() < 0.5:
            rj = inv(rj)
        t = rng.randrange(len(rj))
        rj = rj[t:] + rj[:t]
        if rng.random() < 0.5:
            u = rng.choice(gens)
            if rng.random() < 0.5:
                u = u.upper()
            rj = freered(u + rj + inv(u))
        new = list(words)
        new[i] = cyclered(words[i] + rj)
        if not new[i] or len(new[i]) > max_rel:
            continue
        if sum(len(w) for w in new) > max_tot:
            continue
        out.append(tuple(new))
    return out


def hunt(base, kstab, nodes, rng, *, beam=6, branch=10, max_rel=None, max_tot=None,
         headroom=8, census_cap=200_000):
    """Length caps follow the project's harvest operator: a **per-relator** cap of
    ``root total + headroom``, and NO binding total cap.

    Two earlier revisions got this wrong in the same direction. An *absolute* cap gives a
    length-21 base far less room than a length-13 one. A *total* cap is worse still: with
    ``max_tot = root + 8`` almost every AC2 product overshoots and is rejected, so 372,000
    pops over the 124 classes produced only 17,698 distinct states — the search was
    revisiting 99.5% of the time. `stable_matched_contrast` caps per relator (root total
    + 4) and harvested 171,842 members from 1,000 pops; that is the operator to match."""
    base_tot = sum(len(w) for w in base)
    if max_rel is None:
        max_rel = base_tot + headroom
    if max_tot is None:
        max_tot = (len(base) + kstab) * max_rel
    gens = sorted(set("".join(base).lower()))
    words = list(base)
    for _ in range(kstab):
        z = next(c for c in ALPHA if c not in gens)
        gens.append(z)
        words.append(z)
    gens = tuple(sorted(gens))
    start = tuple(words)
    seen = {canon(start)}
    frontier = [start]
    stats = {"pops": 0, "decided": 0, "undecided": 0, "spherical": 0, "restarts": 0}
    # Decide the START state too.  Omitting it meant a root that already carries the
    # certificate was never reported — a silent false negative at every kstab, and at
    # kstab = 0 the root IS the input presentation.
    d0 = decide(start, census_cap)
    if d0["verdict"] == UNDECIDED:
        stats["undecided"] += 1
    else:
        stats["decided"] += 1
    if d0["verdict"] == "SPHERICAL":
        stats["spherical"] += 1
        return start, d0, stats
    # Pool ordered by total length (the classical AC search priority).  Two departures from
    # a plain length descent, both needed: reseed from a random VISITED state rather than
    # the root when the pool empties (reseeding from the root just re-derives `seen` states
    # and the hunt stalls at a few dozen pops), and take a uniformly random state a quarter
    # of the time so the search can climb out of a local length minimum.
    pool_cap = 4000
    visited = [start]
    while stats["pops"] < nodes:
        if not frontier:
            stats["restarts"] += 1
            frontier = [visited[rng.randrange(len(visited))] for _ in range(4)]
        frontier.sort(key=lambda w: sum(len(x) for x in w))
        del frontier[pool_cap:]
        idx = (rng.randrange(len(frontier)) if rng.random() < 0.25
               else rng.randrange(min(beam, len(frontier))))
        cur = frontier.pop(idx)
        stats["pops"] += 1
        for nb in slides(cur, gens, rng, max_rel, max_tot, branch):
            k = canon(nb)
            if k in seen:
                continue
            seen.add(k)
            d = decide(nb, census_cap)
            if d["verdict"] == UNDECIDED:
                stats["undecided"] += 1
            else:
                stats["decided"] += 1
            if d["verdict"] == "SPHERICAL":
                stats["spherical"] += 1
                return nb, d, stats
            frontier.append(nb)
            if len(visited) < 20_000:
                visited.append(nb)
    return None, None, stats


# --------------------------------------------------------------------------- data

def load_u124():
    txt = subprocess.run(["git", "show", U124_REF], capture_output=True, text=True,
                         cwd=str(REPO)).stdout
    if not txt.strip():
        raise SystemExit(f"could not read {U124_REF}; fetch the branch first")
    return [(r["name"], (r["r1"], r["r2"])) for r in csv.DictReader(txt.splitlines())]


def load_ladder(n, rng, lo=13, hi=25):
    """AC-trivial positive controls: solved Miller-Schupp instances."""
    m = {1: "x", -1: "X", 2: "y", -2: "Y"}
    out = []
    with open(REPO / "data" / "ms640_solved.txt") as fh:
        for line in fh:
            v = json.loads(line)
            half = len(v) // 2
            w = ("".join(m[c] for c in v[:half] if c),
                 "".join(m[c] for c in v[half:] if c))
            if all(len(x) >= 3 for x in w) and lo <= sum(len(x) for x in w) <= hi:
                out.append(w)
    rng.shuffle(out)
    return out[:n]


# --------------------------------------------------------------------------- main

def repeat_hunt(base, kstab, nodes, trials, seed, census_cap, headroom=4):
    """`trials` independent hunts on one presentation; returns (hits, rows)."""
    hits, rows = 0, []
    for t in range(trials):
        rng = random.Random(seed + 7919 * t + 104729 * kstab)
        st, d, s = hunt(base, kstab, nodes, rng, headroom=headroom,
                        census_cap=census_cap)
        rows.append({"trial": t, "hit": st is not None,
                     "state": list(st) if st else None, "stats": s})
        hits += st is not None
    return hits, rows


def cmd_target(args):
    """Deep, repeated hunt on ONE presentation, with a length-matched positive control.

    The control is the whole point: `trials` independent failures on AK(3) are worth
    exactly the detection rate the identical protocol achieves on presentations that are
    AC-trivial and of the same length.
    """
    target = tuple(args.target.split(","))
    L = sum(len(w) for w in target)
    rng = random.Random(args.seed)
    controls = [w for w in load_ladder(400, rng, lo=L, hi=L)][:args.controls]
    if len(controls) < args.controls:
        controls = load_ladder(args.controls, random.Random(args.seed),
                               lo=max(6, L - 2), hi=L + 2)[:args.controls]
    report = {"record": "s12_target_hunt", "args": vars(args), "target": list(target),
              "target_length": L, "by_depth": {}}
    for k in range(args.kmax + 1):
        c_hits = c_n = 0
        for w in controls:
            h, _ = repeat_hunt(w, k, args.nodes, args.control_trials, args.seed,
                               args.census_cap, args.headroom)
            c_hits += h
            c_n += args.control_trials
        t_hits, t_rows = repeat_hunt(target, k, args.nodes, args.trials, args.seed,
                                     args.census_cap, args.headroom)
        rate = c_hits / c_n if c_n else float("nan")
        report["by_depth"][k] = {
            "control_hits": c_hits, "control_trials": c_n, "control_rate": rate,
            "target_hits": t_hits, "target_trials": args.trials,
            "target_rows": [r for r in t_rows if r["hit"]],
        }
        print(f"  depth k={k}: control {c_hits}/{c_n} = {rate:.2f}   "
              f"TARGET {t_hits}/{args.trials}"
              + ("   *** HIT ***" if t_hits else ""))
        for r in t_rows:
            if r["hit"]:
                print(f"    HIT STATE: {r['state']}")
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nodes", type=int, default=40)
    ap.add_argument("--kstab", type=int, default=1)
    ap.add_argument("--limit", type=int, default=124)
    ap.add_argument("--ladder", type=int, default=15)
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--census-cap", type=int, default=200_000)
    ap.add_argument("--headroom", type=int, default=4,
                    help="per-relator cap = root total length + headroom "
                         "(the project harvest operator uses +4)")
    ap.add_argument("--out", default="results/stable_ac/fable/s12_hunt.json")
    ap.add_argument("--target", default=None,
                    help="comma-separated relators, e.g. xyxYXY,xxxYYYY for AK(3); "
                         "switches to the repeated deep-hunt mode with a matched control")
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--controls", type=int, default=4)
    ap.add_argument("--control-trials", type=int, default=8)
    ap.add_argument("--kmax", type=int, default=3)
    args = ap.parse_args()
    if args.target:
        return cmd_target(args)

    rng = random.Random(args.seed + 1000 * args.kstab)
    t0 = time.time()
    report = {"record": "s12_certificate_hunt", "args": vars(args), "rows": []}

    ladder = load_ladder(args.ladder, random.Random(args.seed))
    lad_hits = 0
    for w in ladder:
        st, d, s = hunt(w, args.kstab, args.nodes, rng, headroom=args.headroom,
                        census_cap=args.census_cap)
        hit = st is not None
        lad_hits += hit
        report["rows"].append({"set": "ladder", "base": list(w),
                               "length": sum(len(x) for x in w), "hit": hit,
                               "state": list(st) if st else None, "stats": s})
        print(f"  ladder L={sum(len(x) for x in w):2d} {str(w):40s} "
              f"{'HIT' if hit else '   '} dec={s['decided']:4d} und={s['undecided']:4d}")
    rate = lad_hits / len(ladder) if ladder else float("nan")
    print(f"\nPOSITIVE-LADDER DETECTION RATE (kstab={args.kstab}, nodes={args.nodes}): "
          f"{lad_hits}/{len(ladder)} = {rate:.2f}")

    hits = []
    for name, w in load_u124()[:args.limit]:
        st, d, s = hunt(w, args.kstab, args.nodes, rng, headroom=args.headroom,
                        census_cap=args.census_cap)
        row = {"set": "u124", "name": name, "base": list(w),
               "length": sum(len(x) for x in w), "hit": st is not None,
               "state": list(st) if st else None, "stats": s}
        report["rows"].append(row)
        if st is not None:
            hits.append(row)
            print(f"  *** SPHERICAL HIT {name}: {w} -> {st}  ({d['method']})")
    report["summary"] = {"ladder_detection_rate": rate, "ladder_hits": lad_hits,
                         "ladder_n": len(ladder), "u124_hits": len(hits),
                         "u124_n": min(args.limit, 124),
                         "elapsed_s": round(time.time() - t0, 1)}
    print(f"\nU124 HITS: {len(hits)} / {min(args.limit,124)}   "
          f"elapsed {time.time()-t0:.0f}s")
    if rate == 0:
        print("WARNING: detection rate on the positive ladder is 0 — the u124 null is "
              "UNINFORMATIVE and must not be reported as evidence.")
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
