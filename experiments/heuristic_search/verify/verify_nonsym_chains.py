"""Replay ``best_chain_hops`` through pure-Python ``cov.py`` + slow aut_canon.

Independent of ``autcanon_fast`` used by the climb (fast-vs-slow cross-check).

    PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_nonsym_chains \\
        results/comparison/covbeam_nonsym_b1kfull_subset60.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.cov import cov  # noqa: E402


def _orbit_slow(pair):
    mu, rep, _ = aut_canon((str(pair[0]), str(pair[1])))
    return int(mu), [str(rep[0]), str(rep[1])]


def replay_hops(r1_orig, r2_orig, hops, best_rep, best_mu):
    """Re-derive best_rep from orig through recorded (z, iso_gen, iso_index)."""
    errs = []
    mu0, start = _orbit_slow((r1_orig, r2_orig))
    cur = tuple(start)
    if hops and list(hops[0]["parent_pair"]) != list(start):
        # First hop parent must be Aut-min of the original.
        errs.append(
            f"first parent {hops[0]['parent_pair']} != start Aut-min {start}")
    for i, h in enumerate(hops):
        if list(h["parent_pair"]) != list(cur):
            errs.append(
                f"hop {i}: parent {h['parent_pair']} != current Aut-min {list(cur)}")
            break
        if int(h["n_subs"]) <= 1:
            errs.append(f"hop {i}: n_subs={h['n_subs']} ≤ 1")
        branches = cov.cov_branches(
            str_to_word(cur[0]), str_to_word(cur[1]),
            str_to_word(h["z"]),
            default_cap=24, cap_headroom=cov.CAP_HEADROOM,
            reject_len=cov.REJECT_LEN,
            allow_defining_iso=False, iso_gen=h["iso_gen"])
        hit = [b for b in branches if b.iso_index == int(h["iso_index"])]
        if not hit:
            errs.append(
                f"hop {i}: no branch z={h['z']} iso_gen={h['iso_gen']} "
                f"iso_index={h['iso_index']}")
            break
        concrete = [word_to_str(hit[0].r1), word_to_str(hit[0].r2)]
        if concrete != list(h["concrete_pair"]):
            errs.append(
                f"hop {i}: concrete {concrete} != recorded {h['concrete_pair']}")
            break
        if int(hit[0].n_subs) != int(h["n_subs"]):
            errs.append(
                f"hop {i}: n_subs {hit[0].n_subs} != recorded {h['n_subs']}")
        mu, rep = _orbit_slow(concrete)
        if rep != list(h["rep"]) or mu != int(h["mu"]):
            errs.append(
                f"hop {i}: slow aut_canon ({mu},{rep}) != recorded "
                f"({h['mu']},{h['rep']})")
            break
        cur = tuple(rep)
    if list(cur) != list(best_rep):
        errs.append(f"final Aut-min {list(cur)} != best_rep {best_rep}")
    mu_f, _ = _orbit_slow(best_rep)
    if mu_f != int(best_mu):
        errs.append(f"best_mu {best_mu} != slow |best_rep| {mu_f}")
    return errs


def verify_file(path, names=None):
    fails = []
    n = n_desc = 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if names and str(r["pres_id"]) not in names:
                continue
            n += 1
            hops = r.get("best_chain_hops") or []
            if r.get("descended"):
                n_desc += 1
            errs = replay_hops(
                r["r1"], r["r2"], hops, r["best_rep"], r["best_mu"])
            if errs:
                fails.append(f"ms{r['pres_id']}: " + "; ".join(errs[:3]))
            else:
                print(f"  ms{r['pres_id']}: OK "
                      f"(μ {r['mu_in']}→{r['best_mu']}, hops={len(hops)})",
                      flush=True)
    return n, n_desc, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jsonl")
    ap.add_argument("--names", nargs="*", default=None)
    args = ap.parse_args()
    names = set(args.names) if args.names else None
    n, n_desc, fails = verify_file(args.jsonl, names=names)
    print(f"checked {n} rows ({n_desc} descenders); fails={len(fails)}")
    for x in fails[:20]:
        print("  FAIL", x)
    if fails:
        sys.exit(1)
    print("ALL NONSYM CHAINS REPLAY")


if __name__ == "__main__":
    main()
