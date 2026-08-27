#!/usr/bin/env python3
"""Search two-definition, relative-basis block eliminations on aca_124.

The search is intentionally independent of cov.py.  For definitions
    z = u(x,y), t = v(x,y)
it replaces disjoint cyclic occurrences of u^{+-1}, then v^{+-1}, in the
two old relators.  A candidate is accepted only when
    (q1,q2,z,t)
is a Nielsen basis of F(x,y,z,t), with a replayable length-decreasing
Nielsen certificate.  Applying the inverse basis automorphism turns q1,q2
into x,y, so deleting them and x,y gives an exact rank-two target on z,t.
"""

from __future__ import annotations

import argparse
import csv
import json
from itertools import product
from pathlib import Path


INV = {1: -1, -1: 1, 2: -2, -2: 2, 3: -3, -3: 3, 4: -4, -4: 4}
CHAR = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z", 4: "t", -4: "T"}
PARSE = {v: k for k, v in CHAR.items()}


def red(word):
    out = []
    for a in word:
        if out and out[-1] == -a:
            out.pop()
        else:
            out.append(a)
    return tuple(out)


def inv(word):
    return tuple(-a for a in reversed(word))


def cyc(word):
    word = red(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = red(word[1:-1])
    return word


def parse(text):
    return tuple(PARSE[c] for c in text)


def text(word):
    return "".join(CHAR[a] for a in word)


def substitute(word, pattern, symbol):
    """Same cyclic nonoverlap convention as the repository CoV transform."""
    pattern = tuple(pattern)
    pattern_i = inv(pattern)
    word = tuple(word)
    n, size = len(word), len(pattern)
    if not word or not pattern or size > n:
        return red(word), 0
    used = [False] * n
    linear = []
    i = 0
    count = 0
    while i < n:
        if i + size <= n and not any(used[j] for j in range(i, i + size)):
            chunk = word[i:i + size]
            if chunk == pattern or chunk == pattern_i:
                s = symbol if chunk == pattern else -symbol
                for j in range(i, i + size):
                    used[j] = True
                linear.append((i, s))
                count += 1
                i += size
                continue
        i += 1
    seam_s = None
    seam_k = None
    if size >= 2:
        for k in range(1, size):
            prefix = size - k
            if prefix > n - k:
                continue
            if any(used[j] for j in range(prefix)) or any(used[j] for j in range(n-k, n)):
                continue
            chunk = word[n-k:] + word[:prefix]
            if chunk == pattern:
                seam_s = symbol
            elif chunk == pattern_i:
                seam_s = -symbol
            else:
                continue
            seam_k = k
            for j in range(prefix):
                used[j] = True
            for j in range(n-k, n):
                used[j] = True
            count += 1
            break
    out = []
    if seam_s is None:
        start, end = 0, n
    else:
        out.append(seam_s)
        start, end = size-seam_k, n-seam_k
    at = dict(linear)
    i = start
    while i < end:
        if i in at:
            out.append(at[i])
            i += size
        else:
            out.append(word[i])
            i += 1
    return red(out), count


def apply_move(words, trackers, move):
    kind = move[0]
    words = list(words)
    trackers = list(trackers)
    if kind == "mul":
        _, target, other, sign, side = move
        ow = words[other] if sign == 1 else inv(words[other])
        ot = trackers[other] if sign == 1 else inv(trackers[other])
        if side == "R":
            words[target] = red(words[target] + ow)
            trackers[target] = red(trackers[target] + ot)
        else:
            words[target] = red(ow + words[target])
            trackers[target] = red(ot + trackers[target])
    elif kind == "inv":
        _, target = move
        words[target] = inv(words[target])
        trackers[target] = inv(trackers[target])
    elif kind == "swap":
        _, left, right = move
        words[left], words[right] = words[right], words[left]
        trackers[left], trackers[right] = trackers[right], trackers[left]
    else:
        raise ValueError(move)
    return tuple(words), tuple(trackers)


def nielsen_basis(words):
    """Return (moves, inverse images) or None, by classical Nielsen reduction."""
    cur = tuple(red(w) for w in words)
    trackers = ((1,), (2,), (3,), (4,))
    moves = []
    while sum(map(len, cur)) > 4:
        old_total = sum(map(len, cur))
        best = None
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                for sign in (1, -1):
                    for side in ("L", "R"):
                        move = ("mul", i, j, sign, side)
                        nw, nt = apply_move(cur, trackers, move)
                        total = sum(map(len, nw))
                        key = (total, tuple(nw), move)
                        if total < old_total and (best is None or key < best[0]):
                            best = (key, nw, nt, move)
        if best is None:
            return None
        _, cur, trackers, move = best
        moves.append(move)
    if sorted(abs(w[0]) for w in cur if len(w) == 1) != [1, 2, 3, 4] or any(len(w) != 1 for w in cur):
        return None
    inverse = [None] * 4
    for w, tr in zip(cur, trackers):
        letter = w[0]
        inverse[abs(letter)-1] = tr if letter > 0 else inv(tr)
    return tuple(moves), tuple(inverse), cur


def apply_hom(word, images):
    out = []
    for a in word:
        image = images[abs(a)-1]
        out.extend(image if a > 0 else inv(image))
    return red(out)


def specialize_old(word):
    return red(a for a in word if abs(a) >= 3)


def cyclic_subwords(words, max_len):
    found = set()
    for word in words:
        word = cyc(word)
        n = len(word)
        doubled = word + word
        for size in range(2, min(max_len, n) + 1):
            for i in range(n):
                u = red(doubled[i:i+size])
                if len(u) != size or (len(u) > 1 and u[0] == -u[-1]):
                    continue
                found.add(max(u, inv(u)))
    return sorted(found, key=lambda u: (len(u), u))


def old_count(word, generator):
    return sum(abs(a) == generator for a in cyc(word))


def search_row(name, r1s, r2s, max_def_len):
    original = (parse(r1s), parse(r2s))
    candidates = cyclic_subwords(original, max_def_len)
    hits = []
    tested = bases = coupled = 0
    for u, v in product(candidates, repeat=2):
        if u == v:
            continue
        q1, n11 = substitute(original[0], u, 3)
        q2, n12 = substitute(original[1], u, 3)
        q1, n21 = substitute(q1, v, 4)
        q2, n22 = substitute(q2, v, 4)
        if n11+n12 == 0 or n21+n22 == 0:
            continue
        tested += 1
        cert = nielsen_basis((q1, q2, (3,), (4,)))
        if cert is None:
            continue
        bases += 1
        moves, inverse_images, endpoint = cert
        # Verify the inverse certificate without trusting the reducer.
        basis = (q1, q2, (3,), (4,))
        if tuple(apply_hom(w, inverse_images) for w in basis) != ((1,), (2,), (3,), (4,)):
            raise AssertionError("inverse basis replay failed")
        ex = specialize_old(inverse_images[0])
        ey = specialize_old(inverse_images[1])
        d1 = red((-3,) + apply_hom(u, (ex, ey, (3,), (4,))))
        d2 = red((-4,) + apply_hom(v, (ex, ey, (3,), (4,))))
        if not d1 or not d2:
            continue
        target = tuple(tuple((a-2 if a > 0 else a+2) for a in w) for w in (d1, d2))
        # Coupled means no compressed relator is a direct one-variable isolator.
        is_coupled = all(old_count(q, 1) != 1 and old_count(q, 2) != 1 for q in (q1, q2))
        coupled += int(is_coupled)
        hits.append({
            "name": name,
            "source": [r1s, r2s],
            "definitions": [text(u), text(v)],
            "substitution_counts": [n11+n12, n21+n22],
            "compressed": [text(q1), text(q2)],
            "coupled": is_coupled,
            "basis_moves": [list(m) for m in moves],
            "inverse_images": [text(w) for w in inverse_images],
            "solutions": [text(ex), text(ey)],
            "target": [text(w) for w in target],
            "source_raw": len(original[0])+len(original[1]),
            "target_raw": len(target[0])+len(target[1]),
        })
    return {"name": name, "candidate_words": len(candidates), "tested": tested,
            "relative_bases": bases, "coupled_relative_bases": coupled}, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--max-def-len", type=int, default=4)
    ap.add_argument("--only")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = []
    hits = []
    with open(args.data, newline="") as handle:
        for row in csv.DictReader(handle):
            if args.only and row["name"] not in set(args.only.split(",")):
                continue
            summary, found = search_row(row["name"], row["r1"], row["r2"], args.max_def_len)
            rows.append(summary)
            hits.extend(found)
            print(json.dumps(summary), flush=True)
    payload = {"schema": "two-block-relative-basis-v1", "max_def_len": args.max_def_len,
               "summaries": rows, "hits": hits}
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"rows": len(rows), "hits": len(hits),
                      "coupled": sum(h["coupled"] for h in hits),
                      "raw_descents": sum(h["target_raw"] < h["source_raw"] for h in hits)}))


if __name__ == "__main__":
    main()
