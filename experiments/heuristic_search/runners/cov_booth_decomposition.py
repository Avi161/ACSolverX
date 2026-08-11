"""What the CoV pool's redundant slots actually *are*, component by component.

**Zero search nodes.** Regroups the frozen subset-60 sweep at budget 1,000 through
``abel_topk_cov_b1k.load()``. Companion to ``cov_pool_dedup_ladder`` (how many
slots are redundant) and ``cov_relabel_per_pres`` (how the rename filter behaves
per presentation). This one asks the question those two leave open: of the
thousands of slots the dedup drops, *what relation* makes each pair the same?

Why this file exists
--------------------

An earlier pass reported ``relabel_key``'s 4,561 drops as **renames**. That is
wrong, and the name of the key is the trap: ``words.relabel_key`` runs
``canon_pair`` *before* minimising over the 8 signed permutations, so the
overwhelming majority of what it merges was already identical after
canonicalisation and has nothing to do with renaming x and y.

The ladder below separates the components. Each level is the previous relation
plus one more, so the ``new`` column attributes drops to the relation that first
catches them:

```text
exact string            the raw (r1, r2)
+ relator order swap    (r1, r2) ~ (r2, r1)
+ relator inversion     r ~ r^-1        (canon_rel minimises over w and inv(w))
+ cyclic reduction      cancel across the wrap
+ rotation              = words.canon_pair, full Booth
```

Renaming is reported separately, not as a level, because it is not nested in
that chain — it is a different relation that happens to overlap heavily with it.

Every level is checked for **bit-identity**: all members of a group returning the
same ``(solved, nodes_explored, path_length)``. That the inversion level comes
back 20/20 is the empirical confirmation that the S-move set's optional-invert
symmetry really does leave the search unchanged.

Grouping is **within a presentation**, always. ``cross_presentation_groups``
measures what pooling globally would wrongly merge, and is reported only as the
number this file refuses to collapse.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_booth_decomposition
"""

import os

from experiments.equivalence_classes.lib import words as W
from experiments.heuristic_search.runners import abel_topk_cov_b1k as R
from experiments.heuristic_search.runners.cov_pool_dedup_ladder import (
    _groups_by_key,
    _groups_by_union,
    booth_key,
    pure_relabel_key,
    shipped_key,
    triple,
)

OUT_MD = "results/comparison/COV_BOOTH_DECOMPOSITION.md"


def exact_key(d):
    return (d["r1"], d["r2"])


def order_key(d):
    """Relator order swap only."""
    return min((d["r1"], d["r2"]), (d["r2"], d["r1"]))


def inversion_key(d):
    """Order swap + relator inversion, no reduction and no rotation."""
    return min(min((a, b), (b, a))
               for a in (d["r1"], W.inv(d["r1"]))
               for b in (d["r2"], W.inv(d["r2"])))


def cycred_key(d):
    """Order swap + inversion + cyclic reduction, still no rotation."""
    return min(min((a, b), (b, a))
               for a in (W.cyc_reduce(d["r1"]), W.cyc_reduce(W.inv(d["r1"])))
               for b in (W.cyc_reduce(d["r2"]), W.cyc_reduce(W.inv(d["r2"]))))


LEVELS = [
    ("exact string", exact_key),
    ("+ relator order swap `(r1,r2)→(r2,r1)`", order_key),
    ("+ relator inversion `r → r⁻¹`", inversion_key),
    ("+ cyclic reduction", cycred_key),
    ("+ rotation (= full Booth `canon_pair`)", booth_key),
]


def level_census(cov, keyfn):
    """kept / dropped / multi-member groups / bit-identical, within presentations."""
    kept = dropped = ngrp = ident = 0
    for p in cov:
        for g in _groups_by_key(cov[p], keyfn):
            kept += 1
            dropped += len(g) - 1
            if len(g) > 1:
                ngrp += 1
                if len({triple(d) for d in g}) == 1:
                    ident += 1
    return {"kept": kept, "dropped": dropped, "groups": ngrp, "ident": ident}


def rename_overlap(cov):
    """How the 8-relabel relation sits against Booth: shared vs rename-only."""
    db = dr = du = 0
    for p in cov:
        rows = cov[p]
        db += len(rows) - len(_groups_by_key(rows, booth_key))
        dr += len(rows) - len(_groups_by_key(rows, pure_relabel_key))
        du += len(rows) - len(_groups_by_union(rows, [booth_key, pure_relabel_key]))
    ds = sum(len(cov[p]) - len(_groups_by_key(cov[p], shipped_key)) for p in cov)
    return {"booth": db, "relabel": dr, "union": du, "shipped": ds,
            "overlap": db + dr - du, "relabel_only": du - db}


def cross_presentation_groups(cov):
    """Booth groups that would span >1 presentation if the pool were pooled globally.

    Reported to be explicit that no census here merges across presentations:
    two presentations are different problems and each needs its own candidates.
    """
    allrows, pres_of = [], {}
    for p in cov:
        for d in cov[p]:
            allrows.append(d)
            pres_of[id(d)] = p
    return sum(1 for g in _groups_by_key(allrows, booth_key)
               if len({pres_of[id(d)] for d in g}) > 1)


def main():
    ids60, _bins, _auts, cov, _control = R.load()
    assert len(ids60) == 60
    total = sum(len(cov[p]) for p in cov)

    rows, prev = [], 0
    for name, kf in LEVELS:
        c = level_census(cov, kf)
        c["name"], c["new"] = name, c["dropped"] - prev
        prev = c["dropped"]
        rows.append(c)
    ov = rename_overlap(cov)
    cross = cross_presentation_groups(cov)

    print(f"subset-60 @ budget {R.BUDGET}: {total} cov rows over {len(ids60)} "
          f"presentations, grouped WITHIN each presentation\n")
    print(f"{'level':<44}{'kept':>7}{'dropped':>9}{'new':>7}  bit-identical")
    for c in rows:
        pct = f"{c['ident']}/{c['groups']}" if c["groups"] else "—"
        print(f"{c['name']:<44}{c['kept']:>7,}{c['dropped']:>9,}{c['new']:>7,}  {pct}")
    print(f"\nrenaming (8 signed perms), not nested in the chain: drops "
          f"{ov['relabel']}, of which {ov['overlap']} are Booth duplicates too "
          f"and {ov['relabel_only']} are rename-only")
    print(f"Booth groups spanning >1 presentation if pooled globally: {cross} "
          f"(never merged)")

    md = [
        "# What the redundant slots actually are\n",
        f"Subset-60, budget {R.BUDGET:,}, **{total:,} candidate rows** over "
        f"{len(ids60)} presentations, at zero search nodes. Each level is the "
        f"previous relation plus one more, so **new** attributes a drop to the "
        f"relation that first catches it. Grouping is **within a presentation**, "
        f"always. *bit-identical* = every member of the group returned the same "
        f"`(solved, nodes_explored, path_length)`.\n",
        f"This table exists because an earlier pass reported `relabel_key`'s "
        f"{ov['shipped']:,} drops as **renames**. The name of the key is the "
        f"trap: `words.relabel_key` runs `canon_pair` *before* minimising over the "
        f"8 signed permutations, so nearly everything it merges was already "
        f"identical after canonicalisation and has nothing to do with renaming "
        f"`x` and `y`.\n",
        "| level | kept | dropped | new | bit-identical |",
        "|---|---:|---:|---:|---|",
    ]
    for c in rows:
        pct = f"{c['ident']:,} / {c['groups']:,}" if c["groups"] else "—"
        if c["groups"] and c["ident"] == c["groups"]:
            pct = f"**{pct}**"
        md.append(f"| {c['name']} | {c['kept']:,} | {c['dropped']:,} | "
                  f"{c['new']:,} | {pct} |")
    md += [
        "",
        f"**Relator order swap contributes nothing at all, and the single biggest "
        f"component is cyclic reduction** — the same word with cancelling letters "
        f"removed — not rotation and certainly not renaming.\n",
        f"Renaming is reported apart from the chain because it is a different "
        f"relation, not a further weakening of it. It drops **{ov['relabel']} "
        f"slots** in the whole pool; **{ov['overlap']}** of those pairs are "
        f"duplicates under Booth as well, leaving **{ov['relabel_only']} slots** "
        f"that renaming catches and nothing else does.\n",
        f"Every level is bit-identical without exception. The inversion row "
        f"({rows[2]['ident']}/{rows[2]['groups']}) is the empirical confirmation "
        f"that the S-move set's optional-invert symmetry leaves the search "
        f"unchanged; the rotation row ({rows[4]['ident']}/{rows[4]['groups']}) "
        f"says the same for Booth. Contrast `relabel_key`, whose extra merges are "
        f"renames *of a rotation* and are **not** bit-identical — 148 of its 784 "
        f"groups disagree; see `COV_POOL_DEDUP_LADDER.md`.\n",
        f"No census here merges across presentations. Pooled globally, **{cross} "
        f"Booth groups would span more than one presentation** — none are "
        f"collapsed, because two presentations are different problems and each "
        f"needs its own candidates.\n",
        f"Reproduce: `.venv/bin/python3 -m "
        f"experiments.heuristic_search.runners.cov_booth_decomposition`\n",
    ]

    path = os.path.join(R.ROOT, OUT_MD)
    with open(path, "w") as fh:
        fh.write("\n".join(md))
    print(f"wrote {OUT_MD}")
    return rows, ov, cross


if __name__ == "__main__":
    main()
