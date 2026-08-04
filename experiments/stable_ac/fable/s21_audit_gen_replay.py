"""S21 adversarial audit — (a) build AC-trivial defect-4 controls OUTSIDE the Miller-Schupp
ladder, and (b) replay one control hit chain end to end.

NEW FILE (audit).  Nothing under experiments/ or ac_solver/ is modified; `s12_hunt` is
imported read-only.

MODE `gen`
    Random AC walk from the standard presentation ("x","y") using exactly the s12 move
    family (conjugated AC2 slide + free/cyclic reduction, plus AC1 inversion).  Every state
    reached is AC-trivial BY CONSTRUCTION and carries an explicit witness chain.  We keep
    states matched to AK(3) on:
        total length 13, relator shape [6,7], exact rank-2 census defect 4,
        and NO unit abelianised row (the axis on which all 640 solved-ladder members,
        hence all five S21 controls, differ from AK(3)).

MODE `replay`
    A parent-tracking clone of `s12_hunt.hunt` with the identical RNG call order, so the
    chain that produced a reported hit can be recovered, every step re-verified as a
    genuine AC move, and the defect logged along the chain (the T-S19 discipline:
    log the property along the chain, not only at the leaf).
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from experiments.stable_ac.fable.s12_hunt import (
    ALPHA, canon, cyclered, decide, freered, inv, slides, UNDECIDED)
from experiments.stable_ac.fable.neuwirth_rank_n import (
    build_link_n, census_size, gamma_N_factorial_n)

REPO = Path(__file__).resolve().parents[3]


def gens_of(words):
    return tuple(sorted(set("".join(words).lower())))


def ab_rows(words, gens=("x", "y")):
    return [[sum((1 if c == g else -1 if c == g.upper() else 0) for c in w) for g in gens]
            for w in words]


def has_unit_row(words):
    return any(sorted(map(abs, r)) == [0, 1] for r in ab_rows(words))


def exact_defect(words, cap=2_000_000):
    g = gens_of(words)
    try:
        if census_size(build_link_n(words, g), g) > cap:
            return None
        c = gamma_N_factorial_n(words, g, cap_rotations=cap, keep_accepting=False)
    except Exception:
        return None
    return c["minimum_defect"] if c["status"] == "OK" else None


# --------------------------------------------------------------------------- gen

def ac_step(words, rng, max_rel):
    """One AC move from the project's own family; returns (new_words, description)."""
    n = len(words)
    i, j = rng.randrange(n), rng.randrange(n)
    if rng.random() < 0.12:
        new = list(words)
        new[i] = inv(new[i])
        return tuple(new), f"AC1 invert r{i}"
    if i == j:
        return None, None
    rj = words[j]
    if not rj:
        return None, None
    eps = 1
    if rng.random() < 0.5:
        rj, eps = inv(rj), -1
    u = ""
    if rng.random() < 0.6:
        u = rng.choice("xy")
        if rng.random() < 0.5:
            u = u.upper()
        rj = freered(u + rj + inv(u))
    new = list(words)
    new[i] = cyclered(words[i] + rj)
    if not new[i] or len(new[i]) > max_rel:
        return None, None
    return tuple(new), f"AC2/AC3 r{i} <- cyclered(r{i} * {u or 'e'} r{j}^{eps} {inv(u) or 'e'})"


def verify_chain(chain):
    """Independently re-check every step of an AC chain: each state must be obtainable
    from its predecessor by r_i <- cyclered(r_i * u r_j^eps u^-1) (u a word of length <= 3)
    or by r_i <- r_i^-1 (up to cyclic reduction)."""
    ok = []
    for a, b in zip(chain, chain[1:]):
        good = False
        for i in range(len(a)):
            if tuple(cyclered(x) for x in b) == tuple(
                    cyclered(inv(x) if k == i else x) for k, x in enumerate(a)):
                good = True
                break
        if not good:
            for i in range(len(a)):
                for j in range(len(a)):
                    if i == j:
                        continue
                    for eps in (1, -1):
                        rj = a[j] if eps == 1 else inv(a[j])
                        for t in range(len(rj) + 1):
                            rr = rj[t:] + rj[:t]
                            for u in [""] + list("xXyY") + [p + q for p in "xXyY"
                                                            for q in "xXyY"]:
                                cand = list(a)
                                cand[i] = cyclered(a[i] + freered(u + rr + inv(u)))
                                if tuple(cyclered(x) for x in cand) == tuple(
                                        cyclered(x) for x in b):
                                    good = True
                                    break
                            if good:
                                break
                        if good:
                            break
                    if good:
                        break
                if good:
                    break
        ok.append(good)
    return ok


def cmd_gen(args):
    rng = random.Random(args.seed)
    found, seen = [], set()
    keys = set()
    for _ in range(args.walks):
        words = ("x", "y")
        chain = [words]
        for _ in range(args.steps):
            nxt, _d = ac_step(words, rng, args.max_rel)
            if nxt is None:
                continue
            words = nxt
            chain.append(words)
            tot = sum(len(w) for w in words)
            shape = sorted(len(w) for w in words)
            if tot != args.total or shape != args.shape:
                continue
            k = canon(words)
            if k in keys:
                continue
            keys.add(k)
            if args.no_unit_row and has_unit_row(words):
                continue
            d = exact_defect(words, args.cap)
            if d != args.defect:
                continue
            rec = {"words": list(words), "shape": shape, "total": tot,
                   "rank2_defect": d, "abelian_rows": ab_rows(words),
                   "unit_row": has_unit_row(words), "chain": [list(c) for c in chain]}
            found.append(rec)
            print(f"  FOUND {words}  ab={rec['abelian_rows']}  defect={d}  "
                  f"chain_len={len(chain)}")
            if len(found) >= args.want:
                break
        if len(found) >= args.want:
            break
    out = {"record": "s21_audit_ctlgen", "args": vars(args), "found": found}
    Path(REPO / args.out).write_text(json.dumps(out, indent=1))
    print(f"found {len(found)}; wrote {args.out}")


# --------------------------------------------------------------------------- replay

def hunt_tracked(base, kstab, nodes, rng, *, beam=6, branch=10, max_rel=None, max_tot=None,
                 headroom=8, census_cap=200_000):
    """Verbatim clone of s12_hunt.hunt with parent tracking; identical RNG call order."""
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
    parent = {start: None}
    stats = {"pops": 0, "decided": 0, "undecided": 0, "spherical": 0, "restarts": 0}
    d0 = decide(start, census_cap)
    if d0["verdict"] == UNDECIDED:
        stats["undecided"] += 1
    else:
        stats["decided"] += 1
    if d0["verdict"] == "SPHERICAL":
        stats["spherical"] += 1
        return start, d0, stats, parent
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
            parent.setdefault(nb, cur)
            d = decide(nb, census_cap)
            if d["verdict"] == UNDECIDED:
                stats["undecided"] += 1
            else:
                stats["decided"] += 1
            if d["verdict"] == "SPHERICAL":
                stats["spherical"] += 1
                return nb, d, stats, parent
            frontier.append(nb)
            if len(visited) < 20_000:
                visited.append(nb)
    return None, None, stats, parent


def cmd_replay(args):
    base = tuple(args.target.split(","))
    rng = random.Random(args.seed + 7919 * args.trial + 104729 * args.kstab)
    st, d, s, parent = hunt_tracked(base, args.kstab, args.nodes, rng,
                                    headroom=args.headroom, census_cap=args.census_cap)
    print("root         :", base, " exact rank-2 defect =", exact_defect(base, args.cap))
    print("reported hit :", st, d, s)
    if st is None:
        print("no hit reproduced")
        return
    chain = []
    node = st
    while node is not None:
        chain.append(node)
        node = parent.get(node)
    chain.reverse()
    print(f"chain length {len(chain)} (root -> hit)")
    steps = verify_chain(chain)
    rows = []
    for idx, w in enumerate(chain):
        dd = exact_defect(w, args.cap)
        rows.append({"i": idx, "words": list(w), "total": sum(len(x) for x in w),
                     "defect": dd})
        print(f"  [{idx:2d}] len={sum(len(x) for x in w):3d} defect={dd}  {w}")
    print("every step a legitimate AC move:", all(steps), steps)
    print("hit exact defect (independent census):", exact_defect(st, args.cap))
    out = {"record": "s21_audit_replay", "args": vars(args), "root": list(base),
           "hit": list(st), "chain": rows, "steps_verified": steps,
           "all_steps_ac": all(steps), "stats": s}
    Path(REPO / args.out).write_text(json.dumps(out, indent=1))
    print("wrote", args.out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["gen", "replay"], default="gen")
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--walks", type=int, default=400)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--max-rel", type=int, default=9)
    ap.add_argument("--total", type=int, default=13)
    ap.add_argument("--shape", type=int, nargs=2, default=[6, 7])
    ap.add_argument("--defect", type=int, default=4)
    ap.add_argument("--no-unit-row", action="store_true")
    ap.add_argument("--want", type=int, default=3)
    ap.add_argument("--cap", type=int, default=2_000_000)
    # replay
    ap.add_argument("--target", default="YYXyx,YXYXXyxx")
    ap.add_argument("--trial", type=int, default=5)
    ap.add_argument("--nodes", type=int, default=8000)
    ap.add_argument("--kstab", type=int, default=0)
    ap.add_argument("--headroom", type=int, default=4)
    ap.add_argument("--census-cap", type=int, default=200_000)
    ap.add_argument("--out", default="results/stable_ac/fable/s21_audit_gen.json")
    args = ap.parse_args()
    args.shape = sorted(args.shape)
    (cmd_gen if args.mode == "gen" else cmd_replay)(args)


if __name__ == "__main__":
    main()
