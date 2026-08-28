"""W4b: harvest fresh rank-2 stable representatives of AK(3)'s class from the
MMS02 corridor states, and profile each as a new search basin.

Mechanism: any rank-3 state (r1, r2, r3) in Tpub's AC orbit with a relator
containing exactly one z^{±1} occurrence Tietze-eliminates z (substitution +
removal, a stable-AC composite per PROOFS.tex as used throughout the repo),
giving a rank-2 pair STABLY AC-equivalent to Tpub, hence to AK(3) through the
corridor. A greedy solve of any harvested pair proves AK(3) stably AC-trivial;
mu <= 12 for any harvested pair trips the MU_CRITERION tripwire (presumed bug
until independently reproduced).

This driver:
  1. re-derives low states of Tpub's orbit by a 1,000-node greedy (budget law);
  2. for each state on the path to the minimum and the minimum itself,
     eliminates z wherever some relator isolates it (single occurrence),
     with a mechanical consistency check (the solved relator must vanish
     under its own substitution);
  3. reports each distinct harvested rank-2 pair with mu (aut_canon,
     certificate-checked) and a 1,000-node greedy profile.

All searches <= 1,000 nodes; aut_canon is the certified slow implementation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.stable_ac.solvern import Pres, search_n, str_to_word

WORD_A = "xzYXyxZXYxyZ"
WORD_B = "XyxZXYXyxzXYxy"
TPUB = (WORD_A, WORD_B, "Xyz")
BUDGET = 1000


def reduce_str(s):
    out = []
    for ch in s:
        if out and out[-1] != ch and out[-1].lower() == ch.lower():
            out.pop()
        else:
            out.append(ch)
    return "".join(out)


def cyc_reduce_str(s):
    s = reduce_str(s)
    while len(s) >= 2 and s[0] != s[-1] and s[0].lower() == s[-1].lower():
        s = reduce_str(s[1:-1])
    return s


def invert(s):
    return s[::-1].swapcase()


def solve_for(rel, gen):
    """If rel contains exactly one gen^{±1}, return the word w with gen = w
    (over the other letters). Else None."""
    hits = [i for i, ch in enumerate(rel) if ch.lower() == gen]
    if len(hits) != 1:
        return None
    i = hits[0]
    rot = rel[i:] + rel[:i]          # starts with gen^{±1}
    head, rest = rot[0], rot[1:]
    w = invert(rest) if head.islower() else rest
    assert all(ch.lower() != gen for ch in w)
    return w


def substitute(rel, gen, w):
    out = []
    for ch in rel:
        if ch.lower() == gen:
            out.append(w if ch.islower() else invert(w))
        else:
            out.append(ch)
    return cyc_reduce_str("".join(out))


def eliminate(state, gen="z"):
    """All rank-2 pairs from eliminating gen via each isolating relator."""
    pairs = []
    for i, rel in enumerate(state):
        w = solve_for(rel, gen)
        if w is None:
            continue
        assert substitute(rel, gen, w) == "", "inconsistent elimination"
        rest = [substitute(r, gen, w) for j, r in enumerate(state) if j != i]
        if any(ch.lower() == gen for r in rest for ch in r):
            continue
        if all(r for r in rest):
            pairs.append((tuple(sorted(rest, key=lambda r: (len(r), r))), i, w))
    return pairs


def profile_pair(pair, seen, out):
    if pair in seen:
        return
    seen.add(pair)
    t, rep, phi = aut_canon(pair)
    assert check(pair, rep, phi), f"aut_canon certificate FAILED for {pair}"
    rels = tuple(tuple(int(g) for g in str_to_word(s)) for s in pair)
    stats = search_n(Pres(2, rels), BUDGET)
    rec = {
        "pair": list(pair),
        "total": sum(len(r) for r in pair),
        "mu": t,
        "canon": list(rep),
        "greedy_solved": stats["solved"],
        "greedy_min_total": stats["min_relator_length"],
        "greedy_path_length": stats["path_length"],
    }
    out.append(rec)
    print(json.dumps(rec))
    if t <= 12 or stats["solved"]:
        print("TRIPWIRE: potential stable solve of AK(3)'s class — "
              "presumed bug until independently reproduced. Quarantine.")


def main():
    rels = tuple(tuple(int(g) for g in str_to_word(s)) for s in TPUB)
    stats = search_n(Pres(3, rels), BUDGET)
    print(json.dumps({"tpub_min_total": stats["min_relator_length"],
                      "tpub_solved": stats["solved"]}))
    min_state = tuple(stats["min_relator"])
    print(json.dumps({"min_state": list(min_state)}))

    seen, out = set(), []
    for st in [min_state]:
        for pair, idx, w in eliminate(st):
            print(json.dumps({"from": list(st), "solved_row": idx,
                              "z_equals": w}))
            profile_pair(pair, seen, out)
    if not out:
        print("no isolating relator at the minimum state; nothing harvested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
