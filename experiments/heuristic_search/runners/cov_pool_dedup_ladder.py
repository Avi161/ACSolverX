"""How much of the subset-60 CoV pool is a *provably* redundant copy of another candidate.

**Zero search nodes.** Every number is a regrouping of the frozen subset-60 sweep
at budget 1,000, read through ``abel_topk_cov_b1k.load()`` — the same gated
loader, the same 60 presentations, the same 6,177 candidate rows. Nothing here
calls the solver.

The question
------------

The shipped dedup keys on ``words.relabel_key`` and takes the pool 6,177 -> 1,616.
That is a *decision* to treat two candidates as the same start. This file asks the
narrower, falsifiable version: how many of the dropped slots are redundant as a
matter of fact — the search that was skipped would have returned the identical
triple ``(solved, nodes_explored, path_length)`` — and how many are merely
AC-equivalent, a different string the solver would genuinely have walked
differently.

Five groupings, each applied *within* a presentation
----------------------------------------------------

```text
exact         the raw (r1, r2) strings
relabel       PURE relabel: the literal letterwise image under one of the 8
              signed permutations, relator order allowed to swap. No rotation,
              no cyclic reduction. This is the group the symmetry argument
              actually covers.
booth         words.canon_pair: cyclic reduction + least rotation + relator order
union         connected components of (booth OR pure relabel) -- the full set of
              pairs the symmetry argument covers
shipped       words.relabel_key, which runs canon_pair *before* minimising over
              the 8 permutations, so it is strictly coarser than `union`
```

For every grouping the script reports how many slots survive, how many are
dropped, and — the point of the file — what fraction of the multi-member groups
are **bit-identical**: all members agreeing exactly on ``solved``,
``nodes_explored`` and ``path_length``. A grouping whose groups are 100%
bit-identical is a free dedup. One whose groups disagree is a judgement call.

Why `union` and not `shipped` is the provable line: a signed permutation is a
letterwise bijection and Booth canonicalisation is a rotation of the same word,
so both map the search tree isomorphically. Their composition-with-rotation
(`shipped`) does not — a rename *of a rotation* is a different starting string,
and the heap's third key reads packed state bytes.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_pool_dedup_ladder
"""

import os

from experiments.equivalence_classes.lib import words as W
from experiments.heuristic_search.runners import abel_topk_cov_b1k as R

OUT_MD = "results/comparison/COV_POOL_DEDUP_LADDER.md"


def pure_relabel_key(d):
    """Literal image under the 8 signed permutations; relator order may swap.

    No ``canon_pair``, so no rotation and no cyclic reduction — unlike
    ``words.relabel_key``, which canonicalises first and is therefore coarser.
    """
    best = None
    for _, img in W.SIGNED_PERMS:
        a, b = W.apply_hom(d["r1"], img), W.apply_hom(d["r2"], img)
        cand = min((a, b), (b, a))
        if best is None or cand < best:
            best = cand
    return best


def booth_key(d):
    return W.canon_pair(d["r1"], d["r2"])


def shipped_key(d):
    return W.relabel_key((d["r1"], d["r2"]))


def exact_key(d):
    return (d["r1"], d["r2"])


def triple(d):
    return (bool(d["solved"]), d["nodes_explored"], d["path_length"])


def _groups_by_key(rows, keyfn):
    by = {}
    for d in rows:
        by.setdefault(keyfn(d), []).append(d)
    return list(by.values())


def _groups_by_union(rows, keyfns):
    """Connected components of "share a key under any of `keyfns`"."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a

    for keyfn in keyfns:
        first = {}
        for i, d in enumerate(rows):
            k = keyfn(d)
            if k in first:
                union(first[k], i)
            else:
                first[k] = i

    comp = {}
    for i in range(len(rows)):
        comp.setdefault(find(i), []).append(rows[i])
    return list(comp.values())


def census(cov, grouper):
    """kept / dropped / multi-member groups / members / bit-identical groups."""
    kept = dropped = ngrp = nmem = ident = 0
    for p in cov:
        for g in grouper(cov[p]):
            kept += 1
            dropped += len(g) - 1
            if len(g) > 1:
                ngrp += 1
                nmem += len(g)
                if len({triple(d) for d in g}) == 1:
                    ident += 1
    return {"kept": kept, "dropped": dropped, "groups": ngrp,
            "members": nmem, "ident": ident}


LADDER = [
    ("exact string", lambda rows: _groups_by_key(rows, exact_key)),
    ("pure relabel (8 signed perms, literal)",
     lambda rows: _groups_by_key(rows, pure_relabel_key)),
    ("Booth (cyclic reduction + rotation + relator order)",
     lambda rows: _groups_by_key(rows, booth_key)),
    ("Booth or pure relabel (union)",
     lambda rows: _groups_by_union(rows, [booth_key, pure_relabel_key])),
    ("relabel_key (the shipped dedup)",
     lambda rows: _groups_by_key(rows, shipped_key)),
]


def main():
    ids60, _bins, _auts, cov, _control = R.load()
    total = sum(len(cov[p]) for p in cov)
    assert len(ids60) == 60

    rows = [(name, census(cov, g)) for name, g in LADDER]

    hdr = f"{'grouping':<52}{'kept':>7}{'dropped':>9}{'grps>=2':>9}{'members':>9}  bit-identical"
    print(f"subset-60 @ budget {R.BUDGET}: {total} candidate rows over {len(ids60)} presentations\n")
    print(hdr)
    for name, c in rows:
        pct = f"{c['ident']}/{c['groups']}" if c["groups"] else "-"
        print(f"{name:<52}{c['kept']:>7,}{c['dropped']:>9,}{c['groups']:>9,}"
              f"{c['members']:>9,}  {pct}")

    md = [f"# The CoV pool dedup ladder — what is provably redundant\n",
          f"Subset-60, budget {R.BUDGET:,}, **{total:,} candidate rows** over {len(ids60)} "
          f"presentations, regrouped from the frozen sweep at zero search nodes. "
          f"*bit-identical* = every member of the group returned the same "
          f"`(solved, nodes_explored, path_length)`.\n",
          "| grouping | kept | dropped | groups ≥2 | members | bit-identical |",
          "|---|---:|---:|---:|---:|---|"]
    for name, c in rows:
        pct = f"{c['ident']:,} / {c['groups']:,}" if c["groups"] else "—"
        if c["groups"] and c["ident"] == c["groups"]:
            pct = f"**{pct}**"
        md.append(f"| {name} | {c['kept']:,} | {c['dropped']:,} | {c['groups']:,} | "
                  f"{c['members']:,} | {pct} |")
    md.append("")
    md.append(f"Reproduce: `.venv/bin/python3 -m "
              f"experiments.heuristic_search.runners.cov_pool_dedup_ladder`\n")

    path = os.path.join(R.ROOT, OUT_MD)
    with open(path, "w") as fh:
        fh.write("\n".join(md))
    print(f"\nwrote {OUT_MD}")
    return rows


if __name__ == "__main__":
    main()
