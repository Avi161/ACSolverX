"""Per-presentation rename dedup: keep only the lex-min of each 8-relabel class.

**Zero search nodes.** A regrouping of the frozen subset-60 sweep at budget 1,000,
read through ``abel_topk_cov_b1k.load()``. Companion to
``cov_pool_dedup_ladder``, which asks the same question pooled; this one asks it
*one presentation at a time*, which is how the filter would actually be applied.

The algorithm
-------------

For a single presentation, take its CoV candidates, map each to the canonical
representative of its class under the 8 signed permutations of ``{x, y}``
(``words.SIGNED_PERMS`` — the length-preserving Whitehead automorphisms of the
first kind), and keep only one member per class. Nothing else: no rotation, no
cyclic reduction, no ``canon_pair``. That is the group the search-invariance
argument actually covers, so every drop is provably free.

Two readings of "the 8 relabelings" — relator order fixed, or ``(r1, r2)``
allowed to swap — are both reported. On this pool they agree exactly, so the
ambiguity does not matter here.

What it finds
-------------

The yield is almost nil: 58 of the 60 presentations have **zero** rename
duplicates. The whole effect is two presentations, every class is a pair, and
all of them are bit-identical. A pure rename has to match the *literal* string,
and in this pool collisions essentially only surface after rotation — which is
why Booth (``canon_pair``) cuts 4,099 slots where renaming cuts 23.

The ``booth`` and ``union`` columns are carried alongside so the per-presentation
cost of choosing one key over another is visible in one table.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_relabel_per_pres
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

OUT_MD = "results/comparison/COV_RELABEL_PER_PRES.md"


def relabel_key_ordered(d):
    """8 signed permutations, literal image, relator order held fixed.

    The strict reading of "the 8 relabelings". ``pure_relabel_key`` is this plus
    a permitted ``(r1, r2)`` swap; on this pool the two agree exactly.
    """
    return min((W.apply_hom(d["r1"], img), W.apply_hom(d["r2"], img))
               for _, img in W.SIGNED_PERMS)


def per_presentation(cov):
    """One row per presentation: class counts under each key, and rename detail."""
    out = []
    for p in sorted(cov, key=lambda q: -len(cov[q])):
        rows = cov[p]
        g_ord = _groups_by_key(rows, relabel_key_ordered)
        g_rel = _groups_by_key(rows, pure_relabel_key)
        g_bth = _groups_by_key(rows, booth_key)
        g_uni = _groups_by_union(rows, [booth_key, pure_relabel_key])
        g_shp = _groups_by_key(rows, shipped_key)
        multi = [g for g in g_rel if len(g) > 1]
        out.append({
            "pres": p,
            "covs": len(rows),
            "ordered": len(g_ord),
            "relabel": len(g_rel),
            "booth": len(g_bth),
            "union": len(g_uni),
            "shipped": len(g_shp),
            "rename_groups": len(multi),
            "rename_members": sum(len(g) for g in multi),
            "rename_ident": sum(1 for g in multi
                                if len({triple(d) for d in g}) == 1),
            "bridges": len(g_bth) - len(g_uni),
        })
    return out


def main():
    ids60, _bins, _auts, cov, _control = R.load()
    assert len(ids60) == 60
    rows = per_presentation(cov)
    tot = {k: sum(r[k] for r in rows)
           for k in ("covs", "ordered", "relabel", "booth", "union", "shipped",
                     "rename_groups", "rename_members", "rename_ident", "bridges")}
    hits = [r for r in rows if r["rename_groups"]]

    print(f"subset-60 @ budget {R.BUDGET}: {tot['covs']} cov rows over {len(ids60)} "
          f"presentations\n")
    print(f"{'pres':>6}{'covs':>6}{'relabel':>9}{'booth':>7}{'union':>7}"
          f"{'shipped':>9}   renames")
    for r in rows:
        mark = (f"  -{r['covs'] - r['relabel']} "
                f"({r['rename_ident']}/{r['rename_groups']} bit-identical)"
                if r["rename_groups"] else "")
        print(f"{r['pres']:>6}{r['covs']:>6}{r['relabel']:>9}{r['booth']:>7}"
              f"{r['union']:>7}{r['shipped']:>9}{mark}")
    print(f"\n{'TOTAL':>6}{tot['covs']:>6}{tot['relabel']:>9}{tot['booth']:>7}"
          f"{tot['union']:>7}{tot['shipped']:>9}")
    print(f"\npresentations with any rename duplicate: {len(hits)} / {len(ids60)}")
    print(f"relator order fixed vs. swap allowed: {tot['ordered']} vs {tot['relabel']} "
          f"classes ({'identical' if tot['ordered'] == tot['relabel'] else 'DIFFER'})")

    frac = 100.0 * (tot["covs"] - tot["relabel"]) / tot["covs"]
    bfrac = 100.0 * (tot["covs"] - tot["union"]) / tot["covs"]
    md = [
        "# Rename dedup, one presentation at a time\n",
        f"Subset-60, budget {R.BUDGET:,}, **{tot['covs']:,} candidate rows** over "
        f"{len(ids60)} presentations, regrouped from the frozen sweep at zero search "
        f"nodes. `relabel` = keep only the lex-min representative of each class under "
        f"the 8 signed permutations of `{{x, y}}` — literal images, no rotation and no "
        f"cyclic reduction. `booth` = `words.canon_pair`. `union` = connected "
        f"components of *share a key under either*. `shipped` = `words.relabel_key`, "
        f"which canonicalises before renaming and is therefore coarser than the "
        f"provable line.\n",
        f"**The rename filter is nearly inert.** {len(ids60) - len(hits)} of the "
        f"{len(ids60)} presentations have zero rename duplicates. The entire yield is "
        f"{tot['covs'] - tot['relabel']} slots ({frac:.2f}%) in "
        f"{len(hits)} presentations, every class is a pair, and all "
        f"{tot['rename_ident']}/{tot['rename_groups']} of them are bit-identical — "
        f"same `solved`, `nodes_explored`, `path_length`. A pure rename must match "
        f"the *literal* string; in this pool collisions essentially only surface "
        f"after rotation, which is why Booth cuts {tot['covs'] - tot['booth']:,} "
        f"where renaming cuts {tot['covs'] - tot['relabel']}.\n",
        f"Both readings of \"the 8 relabelings\" agree: relator order held fixed gives "
        f"{tot['ordered']:,} classes, order allowed to swap gives {tot['relabel']:,}.\n",
        f"The **6 union-bridges** — pairs where a rename links two Booth classes — are "
        f"localised here rather than inferred: "
        + ", ".join(f"{r['bridges']} in pres {r['pres']} "
                    f"({r['booth']} → {r['union']})"
                    for r in rows if r["bridges"]) +
        ". Every other presentation has `booth == union`.\n",
        "| pres | covs | relabel | booth | union | shipped | renames dropped |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        drop = (f"**{r['covs'] - r['relabel']}** "
                f"({r['rename_ident']}/{r['rename_groups']} bit-identical)"
                if r["rename_groups"] else "—")
        md.append(f"| {r['pres']} | {r['covs']} | {r['relabel']} | {r['booth']} | "
                  f"{r['union']} | {r['shipped']} | {drop} |")
    md.append(f"| **total** | **{tot['covs']:,}** | **{tot['relabel']:,}** | "
              f"**{tot['booth']:,}** | **{tot['union']:,}** | "
              f"**{tot['shipped']:,}** | **{tot['covs'] - tot['relabel']}** |")
    md.append("")
    md.append(
        f"As a generation-time filter the rename key is free but saves {frac:.2f}%. "
        f"Keying on the **union** is equally provable — every group bit-identical — "
        f"and saves {bfrac:.2f}% ({tot['union']:,} searches kept of {tot['covs']:,}). "
        f"`relabel_key` keeps only {tot['shipped']:,}, but its extra merges are renames "
        f"*of a rotation* and are not bit-identical; see "
        f"`COV_POOL_DEDUP_LADDER.md`.\n")
    md.append(f"Reproduce: `.venv/bin/python3 -m "
              f"experiments.heuristic_search.runners.cov_relabel_per_pres`\n")

    path = os.path.join(R.ROOT, OUT_MD)
    with open(path, "w") as fh:
        fh.write("\n".join(md))
    print(f"wrote {OUT_MD}")
    return rows, tot


if __name__ == "__main__":
    main()
