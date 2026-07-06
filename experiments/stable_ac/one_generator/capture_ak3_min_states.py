#!/usr/bin/env python3
"""Capture the ACTUAL presentation AK(3) plateaus on (min_total_len=13) — "so we can see it".

The AK(3) sweep recorded the scalar `min_total_len` (=13, the plateau) but the old solver threw
away *which* presentation achieved it. The patched `greedy_nrel.solve_one` now returns
`min_total_state`. The flagship theory words already reach min_total_len=13 by the 100k screen (and
never below, even at 1M — order-invariant plateau), so a cheap 100k re-run recaptures the exact
plateau presentation. Writes one JSONL row per (form, word) to
`results/stable_ac/3_generators_w_choices/ak_3_test/ak3_min_states.jsonl`.

    python capture_ak3_min_states.py
"""
import json
import os

import greedy_nrel as gn
import ak3_words as aw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ak_3_test")
BUDGET = 100_000
# flagship theory words (reach the plateau) + a couple of controls for contrast
HERO = ["xyx", "yxy", "xxx", "yyyy", "Xyxy", "YXyxy", "x", "y"]


def word_ints(name):
    for e in aw.build_word_bank():
        if e["name"] == name:
            return e["w_ints"]
    # controls / not in bank: parse the string directly
    return aw.parse(name) if all(c in "xXyY" for c in name) else None


def main():
    os.makedirs(OUT, exist_ok=True)
    outp = os.path.join(OUT, "ak3_min_states.jsonl")
    gn.solve_one(aw.stabilize_with_word(aw.FORMS["textbook"], [1, 2, 1]),
                 n_gen=3, max_nodes=8)                       # warm numba
    rows = []
    for form in ("textbook", "rep"):
        base = aw.FORMS[form]
        for name in HERO:
            w = word_ints(name)
            if not w:
                continue
            sflat = aw.stabilize_with_word(base, w)
            blocked = [gn.null_revert_state(sflat, 3)]
            res, _ = gn.solve_one(sflat, n_gen=3, max_nodes=BUDGET, blocked_states=blocked)
            row = {"form": form, "word_name": name, "budget_nodes": BUDGET,
                   "solved": res["solved"], "min_total_len": res["min_total_len"],
                   "min_total_state": res["min_total_state"],
                   "min_total_state_str": res["min_total_state_str"],
                   "nodes_explored": res["nodes_explored"]}
            rows.append(row)
            st = "  |  ".join(res["min_total_state_str"])
            print(f"  {form:8} z={name:6} min_total_len={res['min_total_len']:2}  ->  ⟨x,y,z | {st}⟩")
    with open(outp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"\nwrote {os.path.relpath(outp, ROOT)}  ({len(rows)} rows)")
    # headline: the plateau-13 presentation(s)
    p13 = [r for r in rows if r["min_total_len"] == 13]
    if p13:
        r = p13[0]
        print(f"\nAK(3) plateau (min total length 13, trivial=3) is the presentation "
              f"⟨x,y,z | {'  |  '.join(r['min_total_state_str'])}⟩  "
              f"(e.g. {r['form']} form, z={r['word_name']}).")


if __name__ == "__main__":
    main()
