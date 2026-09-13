"""Cap-bounded Andrews-Curtis closure BFS -- fast numba engine.

Implements exactly the model spelled out in ``README.md`` and mirrored, slowly
and obviously, in ``capbfs_reference.py``:

  * a state is an unordered pair ``{r1, r2}`` of nonempty cyclically reduced
    cyclic words over ``F2``, each up to rotation and inversion;
  * the cap ``c`` bounds the length of EACH relator of EVERY state on a path;
  * a move replaces ``r_i`` by ``cyc_reduce(rot_a(r_i) . w . rot_p(r_j**e) . w**-1)``
    for a sign ``e``, rotation offsets ``a, p`` and a freely reduced connector
    ``w`` with ``2|w| <= c - |r_i| - |r_j|``, and is allowed iff the result has
    length in ``[1, c]``.

Representation
--------------
A letter is two bits: ``bit1`` = generator (0 = x, 1 = y), ``bit0`` = inverse
flag, so ``x = 0, X = 1, y = 2, Y = 3`` and inversion is ``code ^ 1``.  The
induced letter order is ``x < X < y < Y``, the same fixed order the reference
uses.  A word of length ``n <= 31`` is one int64: letter ``t`` sits at bits
``2*(n-1-t)`` (most significant letter first) and a sentinel ``1 << (2n)``
records the length.  Because the sentinel dominates, comparing two keys as
integers is exactly comparing ``(length, letters)`` lexicographically, which is
also the order in which a canonical pair is sorted.

That packing buys the two hot operations for O(1) register work:

  * rotate left by one letter: ``((b << 2) & mask) | (b >> 2(n-1))`` -- so the
    canonical form (min over the ``n`` rotations of ``w`` and the ``n`` of
    ``w**-1``) costs ``2n`` register ops instead of an O(n) Booth pass over a
    ``(n, 2)`` bool array plus its allocations;
  * free reduction of a concatenation: push letters into an accumulator,
    cancelling against ``acc & 3``.  The accumulator is exact for at most 32
    letters, which is what bounds the cap at ``MAX_CAP = 16``.

States live in an open-addressing table (linear probing, load factor 1/2) keyed
by the two int64 relator keys; everything -- move enumeration, reduction,
canonicalisation, dedup, parent/move recording -- happens in one nopython
kernel.

CLI
---
    python capbfs.py --r1 YXYxyx --r2 YYYYxxx --cap 12 --max-states 5000000 \
        --out out.json
    python capbfs.py --csv rows.csv --caps 8,10,12,14 --out out.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time

import numpy as np
from numba import njit

# --------------------------------------------------------------------------
# alphabet / packing
# --------------------------------------------------------------------------
MAX_LEN = 31                      # 2 bits per letter + sentinel bit <= 63

#: Largest admissible cap.  The unreduced product of a move,
#: ``rot_a(r_i) . w . rot_p(r_j^e) . w^-1``, is freely reduced letter by letter
#: into one int64 accumulator before it is cyclically reduced.  With an empty
#: connector it has up to ``|r_i| + |r_j| <= 2 * cap`` letters, and
#: ``_cyc_reduce`` reads its leading letter with a shift of ``2 * (len - 1)``
#: bits: 32 letters are exact (shift 62), 33 letters need a shift of 64, which
#: is undefined and on x86 wraps silently, so legal moves would be dropped.
#: Hence ``cap <= 16``.  Found by adversarial re-verification (README sec. 6);
#: every published number is at a cap <= 16.
MAX_CAP = 16

CHAR_TO_CODE = {"x": 0, "X": 1, "y": 2, "Y": 3}
CODE_TO_CHAR = {v: k for k, v in CHAR_TO_CODE.items()}

#: canonical key of the trivial presentation {x, y}
TRIVIAL_K1 = (1 << 2) | 0         # "x"
TRIVIAL_K2 = (1 << 2) | 2         # "y"


def str_to_bits(s):
    """``'xY'`` -> ``(bits, length)`` (no sentinel)."""
    bits = 0
    for ch in s:
        bits = (bits << 2) | CHAR_TO_CODE[ch]
    return bits, len(s)


def bits_to_str(bits, n):
    return "".join(CODE_TO_CHAR[(bits >> (2 * (n - 1 - t))) & 3] for t in range(n))


def key_len(key):
    n = 0
    while key > 1:
        key >>= 2
        n += 1
    return n


def key_to_str(key):
    n = key_len(key)
    return bits_to_str(key & ((1 << (2 * n)) - 1), n)


def pack_key(bits, n):
    return (1 << (2 * n)) | bits


# --------------------------------------------------------------------------
# word kernels
# --------------------------------------------------------------------------
@njit(cache=True, inline="always")
def _rotl(bits, n, k):
    """Rotate a packed word LEFT by ``k`` letters (``w[k:] + w[:k]``)."""
    if k == 0 or n <= 1:
        return bits
    return ((bits << (2 * k)) & ((1 << (2 * n)) - 1)) | (bits >> (2 * (n - k)))


@njit(cache=True, inline="always")
def _inv_bits(bits, n):
    """Packed ``w**-1``: reverse the letters and flip every inverse bit."""
    out = 0
    for s in range(n):
        out = (out << 2) | (((bits >> (2 * s)) & 3) ^ 1)
    return out


@njit(cache=True, inline="always")
def _push(acc, alen, bits, n):
    """Append the letters of ``bits`` to the accumulator, free-reducing."""
    for s in range(n - 1, -1, -1):
        code = (bits >> (2 * s)) & 3
        if alen > 0 and (acc & 3) == (code ^ 1):
            acc >>= 2
            alen -= 1
        else:
            acc = (acc << 2) | code
            alen += 1
    return acc, alen


@njit(cache=True, inline="always")
def _cyc_reduce(acc, alen):
    """Cyclically reduce an already freely reduced packed word."""
    while alen >= 2 and ((acc >> (2 * (alen - 1))) & 3) == ((acc & 3) ^ 1):
        acc = (acc >> 2) & ((1 << (2 * (alen - 2))) - 1)
        alen -= 2
    return acc, alen


@njit(cache=True, inline="always")
def _canon_key(bits, n):
    """Sentinel-packed canonical key: min over rotations of ``w`` and ``w**-1``."""
    mask = (1 << (2 * n)) - 1
    shift = 2 * (n - 1)
    best = bits
    b = bits
    for _ in range(n - 1):
        b = ((b << 2) & mask) | (b >> shift)
        if b < best:
            best = b
    b = _inv_bits(bits, n)
    if b < best:
        best = b
    for _ in range(n - 1):
        b = ((b << 2) & mask) | (b >> shift)
        if b < best:
            best = b
    return (1 << (2 * n)) | best


@njit(cache=True)
def canon_pair_keys(b1, n1, b2, n2):
    """Canonical key pair of the unordered state, sorted (shorter/lex-smaller first)."""
    k1 = _canon_key(b1, n1)
    k2 = _canon_key(b2, n2)
    if k1 > k2:
        return k2, k1
    return k1, k2


@njit(cache=True, inline="always")
def _hash2(k1, k2):
    h = np.uint64(k1) * np.uint64(0x9E3779B97F4A7C15)
    h ^= np.uint64(k2) * np.uint64(0xC2B2AE3D27D4EB4F)
    h ^= h >> np.uint64(31)
    h *= np.uint64(0x2545F4914F6CDD1D)
    h ^= h >> np.uint64(29)
    return np.int64(h & np.uint64(0x7FFFFFFFFFFFFFFF))


# --------------------------------------------------------------------------
# connectors
# --------------------------------------------------------------------------
def build_connectors(max_w):
    """All freely reduced words of length <= ``max_w``, shortest first.

    Returns ``(bits, lens, inv_bits, counts)`` where ``counts[W]`` is the number
    of connectors of length ``<= W`` (``2 * 3**W - 1``).  The order inside a
    length class is "extend the previous class on the right by x, X, y, Y",
    identical to ``capbfs_reference.connectors``, so connector indices mean the
    same thing in both engines.
    """
    max_w = max(0, int(max_w))
    bits = [np.zeros(1, np.int64)]
    lens = [np.zeros(1, np.int64)]
    invs = [np.zeros(1, np.int64)]
    last = np.full(1, -1, np.int64)
    prev_bits = np.zeros(1, np.int64)
    prev_inv = np.zeros(1, np.int64)
    codes = np.arange(4, dtype=np.int64)
    for L in range(1, max_w + 1):
        ok = (last[:, None] ^ 1) != codes[None, :]
        nb = ((prev_bits[:, None] << 2) | codes[None, :])[ok]
        ni = (prev_inv[:, None] | ((codes[None, :] ^ 1) << (2 * (L - 1))))[ok]
        nl = np.broadcast_to(codes[None, :], ok.shape)[ok]
        bits.append(nb)
        invs.append(ni)
        lens.append(np.full(nb.shape[0], L, np.int64))
        prev_bits, prev_inv, last = nb, ni, nl
    counts = np.empty(max_w + 1, np.int64)
    tot = 1
    counts[0] = 1
    for L in range(1, max_w + 1):
        tot += bits[L].shape[0]
        counts[L] = tot
    return (np.concatenate(bits), np.concatenate(lens),
            np.concatenate(invs), counts)


# --------------------------------------------------------------------------
# the BFS kernel
# --------------------------------------------------------------------------
@njit(cache=True)
def _bfs_kernel(start_k1, start_k2, cap, max_states,
                conn_bits, conn_len, conn_inv, conn_count, stop_when_solved):
    # ---- node storage -----------------------------------------------------
    capn = 1 << 12
    if capn > max_states:
        capn = max_states
    nk1 = np.empty(capn, np.int64)
    nk2 = np.empty(capn, np.int64)
    nl1 = np.empty(capn, np.int64)
    nl2 = np.empty(capn, np.int64)
    par = np.empty(capn, np.int64)
    mvi = np.empty(capn, np.int8)
    mve = np.empty(capn, np.int8)
    mva = np.empty(capn, np.int8)
    mvp = np.empty(capn, np.int8)
    mvw = np.empty(capn, np.int32)

    # ---- hash table -------------------------------------------------------
    tsize = 1 << 13
    tk1 = np.zeros(tsize, np.int64)
    tk2 = np.zeros(tsize, np.int64)
    tix = np.full(tsize, -1, np.int64)
    tmask = tsize - 1

    def_len1 = 0
    key = start_k1
    while key > 1:
        key >>= 2
        def_len1 += 1
    def_len2 = 0
    key = start_k2
    while key > 1:
        key >>= 2
        def_len2 += 1

    nk1[0] = start_k1
    nk2[0] = start_k2
    nl1[0] = def_len1
    nl2[0] = def_len2
    par[0] = -1
    mvi[0] = -1
    mve[0] = 0
    mva[0] = 0
    mvp[0] = 0
    mvw[0] = -1
    count = 1
    h = _hash2(start_k1, start_k2) & tmask
    tk1[h] = start_k1
    tk2[h] = start_k2
    tix[h] = 0

    solved_idx = -1
    if start_k1 == 4 and start_k2 == 6:
        solved_idx = 0
    min_total = def_len1 + def_len2
    head = 0
    level_end = 1
    popped = 0
    budget_hit = False
    # A start that is already trivial is "solved at level -1": nothing is
    # expanded, exactly as in the reference.
    stop = stop_when_solved and solved_idx >= 0

    while head < count and not stop:
        node = head
        popped += 1
        u0 = nk1[node]
        u1 = nk2[node]
        m0 = nl1[node]
        m1 = nl2[node]
        b0 = u0 & ((1 << (2 * m0)) - 1)
        b1 = u1 & ((1 << (2 * m1)) - 1)

        slack = cap - m0 - m1
        if slack < 0:
            nconn = 1
        else:
            w_max = slack // 2
            if w_max >= conn_count.shape[0]:
                w_max = conn_count.shape[0] - 1
            nconn = conn_count[w_max]

        for i in range(2):
            if i == 0:
                ri_b = b0
                ri_n = m0
                rj_b = b1
                rj_n = m1
                rj_key = u1
            else:
                ri_b = b1
                ri_n = m1
                rj_b = b0
                rj_n = m0
                rj_key = u0
            for e in range(2):
                if e == 0:
                    oj = rj_b
                else:
                    oj = _inv_bits(rj_b, rj_n)
                for a in range(ri_n):
                    a_bits = _rotl(ri_b, ri_n, a)
                    for wi in range(nconn):
                        w_b = conn_bits[wi]
                        w_n = conn_len[wi]
                        wi_b = conn_inv[wi]
                        if w_n == 0:
                            pre_acc = a_bits
                            pre_len = ri_n
                        else:
                            pre_acc, pre_len = _push(a_bits, ri_n, w_b, w_n)
                        for p in range(rj_n):
                            p_bits = _rotl(oj, rj_n, p)
                            acc, alen = _push(pre_acc, pre_len, p_bits, rj_n)
                            if w_n != 0:
                                acc, alen = _push(acc, alen, wi_b, w_n)
                            acc, alen = _cyc_reduce(acc, alen)
                            if alen < 1 or alen > cap:
                                continue
                            ck = _canon_key(acc, alen)
                            if ck > rj_key:
                                c1 = rj_key
                                c2 = ck
                                cl1 = rj_n
                                cl2 = alen
                            else:
                                c1 = ck
                                c2 = rj_key
                                cl1 = alen
                                cl2 = rj_n
                            # ---- find or insert -----------------------
                            slot = _hash2(c1, c2) & tmask
                            found = False
                            while True:
                                t1 = tk1[slot]
                                if t1 == 0:
                                    break
                                if t1 == c1 and tk2[slot] == c2:
                                    found = True
                                    break
                                slot = (slot + 1) & tmask
                            if found:
                                continue
                            if count >= max_states:
                                budget_hit = True
                                stop = True
                                break
                            if count == capn:
                                newcap = capn * 2
                                if newcap > max_states:
                                    newcap = max_states
                                t = np.empty(newcap, np.int64)
                                t[:count] = nk1
                                nk1 = t
                                t = np.empty(newcap, np.int64)
                                t[:count] = nk2
                                nk2 = t
                                t = np.empty(newcap, np.int64)
                                t[:count] = nl1
                                nl1 = t
                                t = np.empty(newcap, np.int64)
                                t[:count] = nl2
                                nl2 = t
                                t = np.empty(newcap, np.int64)
                                t[:count] = par
                                par = t
                                s = np.empty(newcap, np.int8)
                                s[:count] = mvi
                                mvi = s
                                s = np.empty(newcap, np.int8)
                                s[:count] = mve
                                mve = s
                                s = np.empty(newcap, np.int8)
                                s[:count] = mva
                                mva = s
                                s = np.empty(newcap, np.int8)
                                s[:count] = mvp
                                mvp = s
                                q = np.empty(newcap, np.int32)
                                q[:count] = mvw
                                mvw = q
                                capn = newcap
                            idx = count
                            nk1[idx] = c1
                            nk2[idx] = c2
                            nl1[idx] = cl1
                            nl2[idx] = cl2
                            par[idx] = node
                            mvi[idx] = i
                            mve[idx] = e
                            mva[idx] = a
                            mvp[idx] = p
                            mvw[idx] = wi
                            count += 1
                            if cl1 + cl2 < min_total:
                                min_total = cl1 + cl2
                            if c1 == 4 and c2 == 6 and solved_idx < 0:
                                solved_idx = idx
                            tk1[slot] = c1
                            tk2[slot] = c2
                            tix[slot] = idx
                            if 2 * count >= tsize:
                                ntsize = tsize * 2
                                ntk1 = np.zeros(ntsize, np.int64)
                                ntk2 = np.zeros(ntsize, np.int64)
                                ntix = np.full(ntsize, -1, np.int64)
                                nmask = ntsize - 1
                                for q2 in range(count):
                                    s2 = _hash2(nk1[q2], nk2[q2]) & nmask
                                    while ntk1[s2] != 0:
                                        s2 = (s2 + 1) & nmask
                                    ntk1[s2] = nk1[q2]
                                    ntk2[s2] = nk2[q2]
                                    ntix[s2] = q2
                                tk1 = ntk1
                                tk2 = ntk2
                                tix = ntix
                                tsize = ntsize
                                tmask = nmask
                        if stop:
                            break
                    if stop:
                        break
                if stop:
                    break
            if stop:
                break
        if stop:
            break
        head += 1
        if head == level_end:
            if stop_when_solved and solved_idx >= 0:
                stop = True
            else:
                level_end = count

    closed = (head >= count) and (not budget_hit)
    return (nk1[:count], nk2[:count], nl1[:count], nl2[:count], par[:count],
            mvi[:count], mve[:count], mva[:count], mvp[:count], mvw[:count],
            count, head, popped, solved_idx, min_total, closed, budget_hit)


# --------------------------------------------------------------------------
# python wrapper
# --------------------------------------------------------------------------
def _cyc_reduce_str(s):
    """Cyclic reduction on the xXyY alphabet (input normalisation only)."""
    out = []
    for c in s:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    while len(out) >= 2 and out[0] == out[-1].swapcase():
        out = out[1:-1]
    return "".join(out)


def bfs(r1, r2, cap, max_states=1_000_000, stop_when_solved=True,
        collect_states=False):
    """Cap-bounded AC BFS from ``{r1, r2}``.  Returns the result dict."""
    cap = int(cap)
    if cap < 1 or cap > MAX_CAP:
        raise ValueError(
            "cap must be in 1..%d: the packed accumulator is exact only while "
            "the unreduced product of a move has at most 32 letters" % MAX_CAP)
    s1, s2 = _cyc_reduce_str(r1), _cyc_reduce_str(r2)
    if not s1 or not s2:
        raise ValueError("initial presentation has an empty relator: %r %r" % (r1, r2))
    if max(len(s1), len(s2)) > cap:
        raise ValueError("initial presentation already exceeds the cap")
    b1, n1 = str_to_bits(s1)
    b2, n2 = str_to_bits(s2)
    k1, k2 = canon_pair_keys(b1, n1, b2, n2)

    w_max = max(0, (cap - 2) // 2)
    conn_bits, conn_len, conn_inv, conn_count = build_connectors(w_max)

    t0 = time.perf_counter()
    (nk1, nk2, nl1, nl2, par, mvi, mve, mva, mvp, mvw,
     count, head, popped, solved_idx, min_total, closed, budget_hit) = _bfs_kernel(
        int(k1), int(k2), cap, int(max_states),
        conn_bits, conn_len, conn_inv, conn_count, bool(stop_when_solved))
    seconds = time.perf_counter() - t0

    res = {
        "initial": [key_to_str(int(k1)), key_to_str(int(k2))],
        "cap": cap,
        "closed": bool(closed),
        "solved": bool(solved_idx >= 0),
        "states": int(count),
        "max_states": int(max_states),
        "min_total_length_seen": int(min_total),
        "frontier_size_at_stop": int(count - head),
        "seconds": seconds,
        "nodes_per_second": (popped / seconds) if seconds > 0 else 0.0,
        "popped": int(popped),
        "budget_exhausted": bool(budget_hit),
        "engine": "capbfs-numba",
    }
    if solved_idx >= 0:
        chain = []
        cur = int(solved_idx)
        while cur >= 0:
            chain.append(cur)
            cur = int(par[cur])
        chain.reverse()
        path = []
        for node in chain[1:]:
            wi = int(mvw[node])
            path.append({
                "i": int(mvi[node]),
                "j": 1 - int(mvi[node]),
                "e": 1 if int(mve[node]) == 0 else -1,
                "a": int(mva[node]),
                "p": int(mvp[node]),
                "w": bits_to_str(int(conn_bits[wi]), int(conn_len[wi])),
            })
        res["path"] = path
        res["path_states"] = [
            [key_to_str(int(nk1[n])), key_to_str(int(nk2[n]))] for n in chain
        ]
    if collect_states:
        res["_states"] = [
            (key_to_str(int(nk1[t])), key_to_str(int(nk2[t]))) for t in range(count)
        ]
        res["_state_keys"] = sorted("%s,%s" % st for st in res["_states"])
        res["_parents"] = [int(par[t]) for t in range(count)]
    return res


def state_key_strings(result):
    """Sorted ``'r1,r2'`` strings for every discovered state (needs ``collect_states``)."""
    return result["_state_keys"]


def json_ready(result):
    return {k: v for k, v in result.items() if not k.startswith("_")}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="cap-bounded Andrews-Curtis closure BFS")
    ap.add_argument("--r1")
    ap.add_argument("--r2")
    ap.add_argument("--cap", type=int, help="per-relator length cap, 1..%d" % MAX_CAP)
    ap.add_argument("--csv", help="batch mode: csv with name,r1,r2 columns")
    ap.add_argument("--caps", help="batch mode: comma separated caps, e.g. 8,10,12,14")
    ap.add_argument("--limit", type=int, default=0, help="batch mode: first N rows")
    ap.add_argument("--max-states", type=int, default=5_000_000)
    ap.add_argument("--no-stop-when-solved", action="store_true",
                    help="keep expanding after the trivial state is found")
    ap.add_argument("--out", help="output path (.json single / .jsonl batch)")
    args = ap.parse_args(argv)

    stop = not args.no_stop_when_solved

    if args.csv:
        if not args.caps:
            ap.error("--csv requires --caps")
        caps = [int(c) for c in args.caps.split(",") if c.strip()]
        rows = []
        with open(args.csv, newline="") as fh:
            for row in csv.DictReader(fh):
                rows.append((row.get("name", ""), row["r1"], row["r2"]))
                if args.limit and len(rows) >= args.limit:
                    break
        out = open(args.out, "w") if args.out else sys.stdout
        try:
            for name, r1, r2 in rows:
                for cap in caps:
                    try:
                        res = bfs(r1, r2, cap, args.max_states, stop)
                    except ValueError as exc:
                        res = {"initial": [r1, r2], "cap": cap, "error": str(exc)}
                    res["name"] = name
                    res["r1"] = r1
                    res["r2"] = r2
                    out.write(json.dumps(json_ready(res)) + "\n")
                    out.flush()
        finally:
            if args.out:
                out.close()
        return 0

    if not (args.r1 and args.r2 and args.cap):
        ap.error("give --r1 --r2 --cap, or --csv with --caps")
    res = json_ready(bfs(args.r1, args.r2, args.cap, args.max_states, stop))
    text = json.dumps(res, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
