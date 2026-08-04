"""s22_audit_numbers.py — READ-ONLY re-check of the numbers quoted in S22_FINAL_ANSWER.md.

New file (S22 adversarial audit). Runs NO search, spends NO search nodes, decides NO state:
it only re-counts rows in artifacts already on disk. Nothing is written.

Usage:  python3 -m experiments.stable_ac.fable.s22_audit_numbers
"""

import gzip
import json
import os

ART = os.path.join(os.path.dirname(__file__), "..", "..", "..", "results", "stable_ac", "fable")
ART = os.path.normpath(ART)


def rows(name):
    path = os.path.join(ART, name)
    if not os.path.exists(path):
        print(f"  !! MISSING {name}")
        return
    op = gzip.open if name.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def defect_of(r):
    for k in ("minimum_defect", "defect", "min_defect"):
        if k in r and r[k] is not None:
            return r[k]
    return None


def main():
    print("== decided pools: rows and gamma_N histograms ==")
    total_nonthick = 0
    for name in (
        "s4b_decided.jsonl.gz",
        "s4b_control_decided.jsonl.gz",
        "s4b_ctrl2_decided.jsonl.gz",
        "s4b_ctrl2_full_decided.jsonl.gz",
    ):
        hist, n = {}, 0
        for r in rows(name):
            n += 1
            d = defect_of(r)
            g = None if d is None else d // 2
            hist[g] = hist.get(g, 0) + 1
        print(f"  {name}: rows={n} gamma_N hist={dict(sorted(hist.items(), key=lambda kv: (kv[0] is None, kv[0])))}")
        if name == "s4b_decided.jsonl.gz":
            total_nonthick += n

    print("\n== s17 edge list: transition matrix, parents, boundary crossings ==")
    mat, parents1, kids0, par0 = {}, set(), 0, set()
    n_edges = 0
    depths = {}
    ranks1 = {}
    for e in rows("s17_transition_edges.jsonl.gz"):
        dp, dc = e.get("parent_defect"), e.get("child_defect")
        if dp is None or dc is None:
            continue
        gp, gc = dp // 2, dc // 2
        n_edges += 1
        mat[(gp, gc)] = mat.get((gp, gc), 0) + 1
        if gp == 1:
            parents1.add(e.get("parent"))
            depths[e.get("depth")] = depths.get(e.get("depth"), 0) + 1
            ranks1[e.get("parent_rank")] = ranks1.get(e.get("parent_rank"), 0) + 1
        if gp == 0:
            par0.add(e.get("parent"))
        if gc == 0:
            kids0 += 1
    print(f"  edges with both endpoints decided: {n_edges}")
    rowtot = {}
    for (gp, gc), c in sorted(mat.items()):
        rowtot[gp] = rowtot.get(gp, 0) + c
    for gp in sorted(rowtot):
        cells = {gc: c for (p, gc), c in sorted(mat.items()) if p == gp}
        print(f"   from gamma_N={gp}: {cells}  row total {rowtot[gp]}")
    print(f"  distinct gamma_N=1 parents: {len(parents1)}   parent ranks: {dict(sorted(ranks1.items()))}")
    print(f"  gamma_N=1 edges by chain depth: {dict(sorted((k, v) for k, v in depths.items() if k is not None))}")
    print(f"  distinct gamma_N=0 parents: {len(par0)}")
    print(f"  edges landing on gamma_N=0 child: {kids0}")
    down = sum(c for (gp, gc), c in mat.items() if gp == 0 and gc > 0)
    up = sum(c for (gp, gc), c in mat.items() if gp > 0 and gc == 0)
    tries_down = rowtot.get(0, 0)
    tries_up = n_edges - rowtot.get(0, 0)
    print(f"  boundary crossings: DOWN {down} of {tries_down} ({100.0*down/max(tries_down,1):.1f}%)"
          f"   UP {up} of {tries_up}")

    print("\n== s18 defect-4 ladder: hits by rung ==")
    p = os.path.join(ART, "s18_defect4_ladder.json")
    if os.path.exists(p):
        d = json.load(open(p))
        t, h = {}, {}
        for r in d["rows"]:
            k = r["depth_k"]
            t[k] = t.get(k, 0) + 1
            if r["hit"]:
                h[k] = h.get(k, 0) + 1
        print(f"  trials by depth_k (rank ceiling = 2 + k): {dict(sorted(t.items()))}")
        print(f"  hits   by depth_k: {dict(sorted(h.items()))}")
        print(f"  pooled: {sum(h.values())}/{sum(t.values())}")

    print("\n== s17 json: rank-5 flip census (SPLIT vs AC2 arms) ==")
    p = os.path.join(ART, "s17_transition_table.json")
    if os.path.exists(p):
        d = json.load(open(p))
        f = d["depth1_flip_census_rank5"]
        for arm in ("split_matrix_gamma_N", "ac2_control_matrix_gamma_N"):
            m = f[arm]
            r1 = m.get("1", {})
            print(f"  {arm}: from gamma_N=1 -> {r1}  total {sum(r1.values())}  creations {r1.get('0', 0)}")
            r0 = m.get("0", {})
            if r0:
                dest = sum(v for k, v in r0.items() if k != "0")
                print(f"      from gamma_N=0 -> {r0}  destruction {dest}/{sum(r0.values())}"
                      f" = {100.0*dest/sum(r0.values()):.1f}%")


if __name__ == "__main__":
    main()
