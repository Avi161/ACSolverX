"""One exhaustive pass per base family: the S5 spike ceiling, Theorem S10, and
Conjectures U / SR, all from full censuses on both sides.

Usage:  audit_r7_sweep.py <family> [cap]
families: red6 red7 red8 all4 all5 all6 rank3 ak3ish
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter

from audit_r7_core import Dict0, all_spikes, restrict, spike_layout, spike_words, gens_of
from audit_r7_checks import (bases_all, bases_reduced, canon_bases, cyc_reduced_words,
                             orders_key)


def sweep(bases, cap=60000, want_rows=False):
    out = dict(
        bases=0, bases_skipped=0, spikes=0, spikes_skipped=0,
        delta_gamma=Counter(), base_gamma=Counter(), spiked_gamma=Counter(),
        ceiling_violations=[], sr_violations=[], s10_violations=[],
        u_violations=[], pointwise_violations=[],
        unnested_zero_rows=0, nested_zero_rows=0,
        nested_restrict=Counter(), unnested_restrict=Counter(),
        spiked_gamma0=0, spiked_gamma0_with_unnested=0,
        per_base=[],
    )
    for words in bases:
        gens = gens_of(words)
        if len(gens) < 2:
            continue
        pre = Dict0(words, gens)
        if pre.census_size() > cap:
            out["bases_skipped"] += 1
            continue
        pre_hist = pre.histogram()
        gpre = min(pre_hist) // 2
        out["bases"] += 1
        out["base_gamma"][gpre] += 1
        best = None
        for (j, k, u) in all_spikes(words, gens):
            post_words = spike_words(words, j, k, u)
            post = Dict0(post_words, gens)
            if post.census_size() > cap:
                out["spikes_skipped"] += 1
                continue
            out["spikes"] += 1
            lay = spike_layout(words, j, k, u)
            s, d_p, h_q = lay["s"], lay["d_p"], lay["h_q"]
            gpost = None
            saw_zero = False
            saw_unnested_zero = False
            for op in post.compatible_orders():
                dpost = post.defect(op)
                if gpost is None or dpost < gpost:
                    gpost = dpost
                if dpost != 0:
                    continue
                saw_zero = True
                seq = op[s]
                M = len(seq)
                i_dp, i_hq = seq.index(d_p), seq.index(h_q)
                unnested = (i_hq - i_dp) % M == 1 or (i_dp - i_hq) % M == 1
                r = restrict(op, words, j, k, u)
                dr = pre.defect(r)
                if unnested:
                    saw_unnested_zero = True
                    out["unnested_zero_rows"] += 1
                    out["unnested_restrict"][dr] += 1
                    if dr != 0:
                        out["s10_violations"].append(
                            dict(base=words, spiked=post_words, restricted_defect=dr))
                else:
                    out["nested_zero_rows"] += 1
                    out["nested_restrict"][dr] += 1
            gpost //= 2
            out["spiked_gamma"][gpost] += 1
            out["delta_gamma"][gpost - gpre] += 1
            best = gpost if best is None else min(best, gpost)
            if gpost < gpre - 1:
                out["ceiling_violations"].append(
                    dict(base=words, spiked=post_words, gpre=gpre, gpost=gpost))
            if gpost == 0 and gpre > 0:
                out["sr_violations"].append(
                    dict(base=words, spiked=post_words, gpre=gpre))
            if saw_zero:
                out["spiked_gamma0"] += 1
                if saw_unnested_zero:
                    out["spiked_gamma0_with_unnested"] += 1
                else:
                    out["u_violations"].append(
                        dict(base=words, spiked=post_words, gpre=gpre))
        if want_rows:
            out["per_base"].append(dict(base=words, gamma_N=gpre,
                                        min_spiked_gamma_N=best))
    return out


FAMILIES = {
    "red6": lambda: canon_bases(bases_reduced(6)),
    "red7": lambda: canon_bases(bases_reduced(7)),
    "red8": lambda: canon_bases(bases_reduced(8)),
    "all4": lambda: canon_bases(bases_all(4)),
    "all5": lambda: canon_bases(bases_all(5)),
    "all6": lambda: canon_bases(bases_all(6)),
}


def rank3_family():
    import itertools
    A3 = ("x", "X", "y", "Y", "z", "Z")
    out = []
    for n1, n2, n3 in [(1, 1, 2), (1, 2, 2), (1, 1, 3), (2, 2, 2)]:
        for t in itertools.product(*[["".join(p) for p in itertools.product(A3, repeat=n)]
                                     for n in (n1, n2, n3)]):
            if set("".join(t).lower()) == {"x", "y", "z"}:
                out.append(t)
    return canon_bases(out)


FAMILIES["rank3"] = rank3_family
FAMILIES["ak3ish"] = lambda: [
    ("xxxYYYY", "xyxYXY"),
    ("YXYxyx", "YYYxxxx"),
    ("xxYYY", "xyxYXY"),
    ("YYXXyx", "YYYxyXX"),
    ("YYXXyx", "YYxyXXX"),
]


if __name__ == "__main__":
    fam = sys.argv[1]
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
    bases = FAMILIES[fam]()
    t0 = time.time()
    print(f"family {fam}: {len(bases)} canonical bases, cap {cap}", flush=True)
    r = sweep(bases, cap=cap, want_rows=True)
    el = time.time() - t0
    print(f"  bases used {r['bases']} (skipped {r['bases_skipped']}), "
          f"spikes {r['spikes']} (skipped {r['spikes_skipped']}), {el:.1f}s")
    print("  base gamma_N:", dict(sorted(r["base_gamma"].items())))
    print("  spiked gamma_N:", dict(sorted(r["spiked_gamma"].items())))
    print("  delta gamma_N:", dict(sorted(r["delta_gamma"].items())))
    print("  CEILING violations:", len(r["ceiling_violations"]), r["ceiling_violations"][:3])
    print("  SR violations:", len(r["sr_violations"]), r["sr_violations"][:3])
    print("  S10 violations:", len(r["s10_violations"]), r["s10_violations"][:3])
    print("  U violations:", len(r["u_violations"]), r["u_violations"][:3])
    print(f"  spiked complexes with gamma_N=0: {r['spiked_gamma0']}, "
          f"of which some unnested defect-0 witness: {r['spiked_gamma0_with_unnested']}")
    print(f"  unnested defect-0 rows {r['unnested_zero_rows']} "
          f"restrict to {dict(sorted(r['unnested_restrict'].items()))}")
    print(f"  nested   defect-0 rows {r['nested_zero_rows']} "
          f"restrict to {dict(sorted(r['nested_restrict'].items()))}")
    ct = Counter((b["gamma_N"], b["min_spiked_gamma_N"]) for b in r["per_base"]
                 if b["min_spiked_gamma_N"] is not None)
    print("  cross-tab (base, min spiked):", dict(sorted(ct.items())))
