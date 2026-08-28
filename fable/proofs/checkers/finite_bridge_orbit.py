"""W1b: finite AC-graph decision for the MMS02 bridge over several groups.

Group-agnostic escalation of a5_bridge_orbit.py (see that file and
fable/proofs/W1_BRIDGE_FINITE_TEST.md for the soundness argument). Two
refinements, both orbit-preserving:

1. Generator-reduced conjugations: conj(i, g) for g in the generating set of
   H = <phi x, phi y, phi z> generates conj(i, h) for every h in H by
   composition (H finite, so inverses are positive powers).
2. Plain multiplications only: mult(i,j,s,c) = conj(i,c) o mult(i,j,s,1)
   o conj(i,c^{-1}), so mult with conjugated factor is derived. Successors
   per state: 3 inv + 9 conj + 12 mult = 24.

Groups: A5 (consistency cross-check against the full-move run), S5, A6,
PSL(2,7). For each: complete scan for homs killing A and B, conjugacy-class
grouping, exact BFS closure from (1,1,phi(zYX)), positive control
(trivializer image must be in the certified-trivial triple's orbit), then
the decision on (1,1,phi(Xyz)).

Any control failure voids that group's run; any surviving negative refutes
the bridge. All runs are complete finite closures under the wall-clock
guard, not budgeted searches.

Usage: python3 finite_bridge_orbit.py [a5|s5|a6|psl27]
"""
from __future__ import annotations

import hashlib
import json
import sys

import numpy as np
from numba import njit

WORD_A = "xzYXyxZXYxyZ"
WORD_B = "XyxZXYXyxzXYxy"
WORD_KXY = "zYX"
WORD_KPUB = "Xyz"


# ------------------------------------------------------------- group builder


def group_from_generators(gens, expect_order=None):
    """Close permutation generators (tuples) into element list + tables."""
    n = len(gens[0])
    ident = tuple(range(n))
    seen = {ident}
    order = [ident]
    frontier = [ident]
    while frontier:
        nxt = []
        for p in frontier:
            for g in gens:
                q = tuple(g[p[k]] for k in range(n))
                if q not in seen:
                    seen.add(q)
                    order.append(q)
                    nxt.append(q)
        frontier = nxt
    order.sort()
    if expect_order is not None:
        assert len(order) == expect_order, len(order)
    index = {p: i for i, p in enumerate(order)}
    m = len(order)
    mult = np.empty((m, m), dtype=np.int32)
    inv = np.empty(m, dtype=np.int32)
    for i, p in enumerate(order):
        q = [0] * n
        for k in range(n):
            q[p[k]] = k
        inv[i] = index[tuple(q)]
        for j, r in enumerate(order):
            mult[i, j] = index[tuple(p[r[k]] for k in range(n))]
    e = index[ident]
    assert all(mult[i, inv[i]] == e for i in range(m))
    return order, index, mult, inv, e


def make_group(name):
    if name == "a5":
        return group_from_generators(
            [(1, 2, 0, 3, 4), (1, 2, 3, 4, 0)], expect_order=60
        )
    if name == "s5":
        return group_from_generators(
            [(1, 0, 2, 3, 4), (1, 2, 3, 4, 0)], expect_order=120
        )
    if name == "a6":
        return group_from_generators(
            [(1, 2, 0, 3, 4, 5), (0, 2, 3, 4, 5, 1)], expect_order=360
        )
    if name == "psl27":
        # Action on the projective line over F7: points 0..6 and 7 = infinity.
        shift = tuple([(z + 1) % 7 for z in range(7)] + [7])
        neg_inv = [0] * 8
        neg_inv[7] = 0
        neg_inv[0] = 7
        for z in range(1, 7):
            neg_inv[z] = (-pow(z, 5, 7)) % 7  # z^{-1} = z^5 mod 7
        return group_from_generators(
            [shift, tuple(neg_inv)], expect_order=168
        )
    raise SystemExit(f"unknown group {name}")


def encode_word(word):
    m = {"x": 1, "y": 2, "z": 3}
    return np.array(
        [m[c.lower()] * (-1 if c.isupper() else 1) for c in word],
        dtype=np.int32,
    )


# ---------------------------------------------------------------- hom search


@njit(cache=True)
def _scan(mult, inv, e, word_a, word_b, cap):
    m = mult.shape[0]
    out = np.empty((cap, 3), dtype=np.int32)
    n = 0
    overflow = 0
    for gx in range(m):
        for gy in range(m):
            for gz in range(m):
                ok = True
                for word in (word_a, word_b):
                    val = e
                    for s in word:
                        if s == 1:
                            g = gx
                        elif s == -1:
                            g = inv[gx]
                        elif s == 2:
                            g = gy
                        elif s == -2:
                            g = inv[gy]
                        elif s == 3:
                            g = gz
                        else:
                            g = inv[gz]
                        val = mult[val, g]
                    if val != e:
                        ok = False
                        break
                if ok:
                    if n < cap:
                        out[n, 0] = gx
                        out[n, 1] = gy
                        out[n, 2] = gz
                        n += 1
                    else:
                        overflow += 1
    return out[:n], overflow


def conj_class_reps(homs, mult, inv):
    m = mult.shape[0]
    canon = {}
    for gx, gy, gz in homs:
        best = None
        for g in range(m):
            gi = inv[g]
            t = (
                int(mult[mult[g, gx], gi]),
                int(mult[mult[g, gy], gi]),
                int(mult[mult[g, gz], gi]),
            )
            if best is None or t < best:
                best = t
        canon.setdefault(best, 0)
        canon[best] += 1
    return sorted(canon), canon


def eval_word(word, gx, gy, gz, mult, inv, e):
    val = e
    table = {"x": gx, "y": gy, "z": gz}
    for ch in word:
        g = table[ch.lower()]
        if ch.isupper():
            g = inv[g]
        val = mult[val, g]
    return int(val)


# ------------------------------------------------------------------ BFS orbit


@njit(cache=True)
def _bfs(mult, inv, gens, m, start0, start1, start2, targets):
    """Closure under inv(i), conj(i, gen), mult(i,j,+-1,1). Returns
    (orbit_size, hit flags for each target state id)."""
    total = m * m * m
    visited = np.zeros(total, dtype=np.uint8)
    queue = np.empty(total, dtype=np.int32)
    m2 = m * m
    start = start0 * m2 + start1 * m + start2
    visited[start] = 1
    queue[0] = start
    head = 0
    tail = 1
    ng = gens.shape[0]
    t = np.empty(3, dtype=np.int64)
    while head < tail:
        s = queue[head]
        head += 1
        t[0] = s // m2
        t[1] = (s // m) % m
        t[2] = s % m
        for i in range(3):
            old = t[i]
            # inv
            t[i] = inv[old]
            ns = t[0] * m2 + t[1] * m + t[2]
            if visited[ns] == 0:
                visited[ns] = 1
                queue[tail] = ns
                tail += 1
            # conj by generators
            for gi in range(ng):
                c = gens[gi]
                t[i] = mult[mult[c, old], inv[c]]
                ns = t[0] * m2 + t[1] * m + t[2]
                if visited[ns] == 0:
                    visited[ns] = 1
                    queue[tail] = ns
                    tail += 1
            # plain right multiplications
            for j in range(3):
                if j == i:
                    continue
                for sgn in range(2):
                    g = t[j] if sgn == 0 else inv[t[j]]
                    t[i] = mult[old, g]
                    ns = t[0] * m2 + t[1] * m + t[2]
                    if visited[ns] == 0:
                        visited[ns] = 1
                        queue[tail] = ns
                        tail += 1
            t[i] = old
    hits = np.zeros(targets.shape[0], dtype=np.uint8)
    for k in range(targets.shape[0]):
        hits[k] = visited[targets[k]]
    return tail, hits


def run_group(name):
    order, index, mult, inv, e = make_group(name)
    m = mult.shape[0]
    homs, overflow = _scan(
        mult, inv, e, encode_word(WORD_A), encode_word(WORD_B), 1_000_000
    )
    assert overflow == 0, "hom buffer overflow; raise cap"
    reps, sizes = conj_class_reps(homs.tolist(), mult, inv)
    print(
        f"[{name}] |G|={m} homs={len(homs)} classes={len(reps)} "
        f"(incl. trivial)"
    )
    records = []
    m2 = m * m
    for rep in reps:
        gx, gy, gz = rep
        if rep == (e, e, e):
            continue
        kxy = eval_word(WORD_KXY, gx, gy, gz, mult, inv, e)
        kpub = eval_word(WORD_KPUB, gx, gy, gz, mult, inv, e)
        gens = np.array([gx, gy, gz], dtype=np.int32)
        targets = np.array(
            [gx * m2 + gy * m + gz, e * m2 + e * m + kpub],
            dtype=np.int64,
        )
        orbit, hits = _bfs(mult, inv, gens, m, e, e, kxy, targets)
        rec = {
            "group": name,
            "rep": [int(gx), int(gy), int(gz)],
            "class_size": sizes[rep],
            "kxy": kxy,
            "kpub": kpub,
            "orbit_size": int(orbit),
            "control_contains_trivializer": bool(hits[0]),
            "same_orbit_as_kpub": bool(hits[1]),
        }
        print(json.dumps(rec))
        records.append(rec)
    blob = json.dumps(records, sort_keys=True).encode()
    print(f"[{name}] digest sha256: {hashlib.sha256(blob).hexdigest()}")
    bad = [r for r in records if not r["control_contains_trivializer"]]
    neg = [
        r
        for r in records
        if r["control_contains_trivializer"] and not r["same_orbit_as_kpub"]
    ]
    if bad:
        print(f"[{name}] CONTROL FAILURE — move model unsound; no conclusion.")
        return 2
    if neg:
        print(f"[{name}] BRIDGE REFUTED by classes: {[r['rep'] for r in neg]}")
        return 1
    print(f"[{name}] obstruction BLIND (all classes connect).")
    return 0


if __name__ == "__main__":
    sys.exit(run_group(sys.argv[1] if len(sys.argv) > 1 else "a5"))
