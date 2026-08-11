"""Compare the four shipped CoV top-3 arms on all 640 ms640 presentations at 100,000.

**Zero search nodes.** Reads the four frozen result files in
``results/stable_ac/cov/cov_top3/`` and reports them against each other and
against the untransformed baseline the runs embed. Nothing here calls the solver.

The four arms
-------------

```text
abel            abeltop3_100000_..._08_10_26.jsonl        rule "abel"
abel_len_rd_s   abel_len_rd_stop3_100000_..._08_11_26.jsonl   rule "abel_len_rd_s"
len             lentop3_100000_..._08_10_26.jsonl         rule "len"
len_rd_s        len_rd_stop3_100000_..._08_11_26.jsonl    rule "len_rd_s"
```

The two ``_s`` files are the arms run on Colab on 2026-08-11; the other two
shipped on 08-10. All four cover the same 640 presentations at ``k = 3``,
``max_relator_length 24``, cyclic reduction on, family ``subnc2pxysb``, and all
four embed the same baseline column, which ``main`` asserts rather than assumes.

Three accountings, kept apart on purpose
----------------------------------------

``rank1``      nodes spent by the first pick alone.
``deployed``   cumulative nodes up to and including the first *solving* rank --
               what a deployment that stopped on success would spend.
``as-run``     cumulative nodes over all three ranks, which is what these runs
               actually burned: the recorded runs do **not** early-stop, so all
               three candidates execute even after rank 1 solves. "stop3" in the
               filenames does not mean early-stop in the recorded data.

Reporting only one of the three misleads, and in opposite directions for the two
families -- see `price-the-untransformed-route`. The ``_s`` arms are markedly
*dearer* as-run and *cheaper* deployed.

    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_arm_compare
"""

import collections
import json
import os
import statistics as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RES = os.path.join(ROOT, "results", "stable_ac", "cov", "cov_top3")
OUT_MD = "results/stable_ac/cov/cov_top3/ARM_COMPARE_100K.md"

ARMS = [
    ("abel", "abeltop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl"),
    ("abel_len_rd_s", "abel_len_rd_stop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_11_26.jsonl"),
    ("len", "lentop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl"),
    ("len_rd_s", "len_rd_stop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_11_26.jsonl"),
]
PAIRS = [("abel", "abel_len_rd_s"), ("len", "len_rd_s")]


def load(path):
    by = collections.defaultdict(list)
    with open(path) as fh:
        for line in fh:
            d = json.loads(line)
            by[d["pres_id"]].append(d)
    for v in by.values():
        v.sort(key=lambda r: r["rank"])
    return by


def first_solving(v):
    """The row a stop-on-success deployment would stop at, else the last row."""
    return next((r for r in v if r["solved"]), v[-1])


def arm_stats(by):
    solved = {p for p, v in by.items() if any(r["solved"] for r in v)}
    plen = [min(r["path_length"] for r in v if r["solved"])
            for p, v in by.items() if p in solved]
    return {
        "n": len(by),
        "rank1": sum(1 for v in by.values() if v[0]["solved"]),
        "top3": len(solved),
        "rank1_nodes": sum(v[0]["nodes_explored"] for v in by.values()),
        "deployed": sum(first_solving(v)["cum_nodes"] for v in by.values()),
        "as_run": sum(v[-1]["cum_nodes"] for v in by.values()),
        "med_plen": int(st.median(plen)) if plen else 0,
        "unsolved": sorted(set(by) - solved),
        "hours": sum(r["time_seconds"] for v in by.values() for r in v) / 3600.0,
        "solved_set": solved,
    }


def baseline_of(by):
    return {p: (v[0]["base_solved"], v[0]["base_nodes_explored"],
                v[0]["base_path_length"]) for p, v in by.items()}


def main():
    data, base = {}, None
    for arm, fn in ARMS:
        by = load(os.path.join(RES, fn))
        b = baseline_of(by)
        if base is None:
            base = b
        else:
            assert b == base, f"{arm} embeds a different baseline column"
        data[arm] = by

    S = {arm: arm_stats(by) for arm, by in data.items()}
    b_solved = sum(1 for v in base.values() if v[0])
    b_nodes = sum(v[1] for v in base.values())
    b_plen = int(st.median([v[2] for v in base.values() if v[0]]))
    budget = next(iter(data["abel"].values()))[0]["base_node_budget"]

    print(f"baseline column identical across all four arms: {b_solved}/640 solved "
          f"@ {budget:,} budget, {b_nodes:,} nodes, median path {b_plen}\n")
    print(f"{'arm':<16}{'rank1':>7}{'top3':>7}{'rank1 nodes':>13}{'deployed':>11}"
          f"{'as-run':>12}{'med path':>10}  unsolved")
    for arm, _ in ARMS:
        s = S[arm]
        print(f"{arm:<16}{s['rank1']:>7}{s['top3']:>7}{s['rank1_nodes']:>13,}"
              f"{s['deployed']:>11,}{s['as_run']:>12,}{s['med_plen']:>10}  "
              f"{s['unsolved'] or '—'}")

    print("\nwhat S changes, within a rule family:")
    deltas = {}
    for plain, s_arm in PAIRS:
        A, B, sa, sb = data[plain], data[s_arm], S[plain], S[s_arm]
        differ = sum(1 for p in A
                     if (A[p][0]["r1"], A[p][0]["r2"]) != (B[p][0]["r1"], B[p][0]["r2"]))
        d = {
            "gain": sorted(sb["solved_set"] - sa["solved_set"]),
            "loss": sorted(sa["solved_set"] - sb["solved_set"]),
            "differ": differ,
            "r1_pct": 100.0 * (sb["rank1_nodes"] - sa["rank1_nodes"]) / sa["rank1_nodes"],
            "dep_pct": 100.0 * (sb["deployed"] - sa["deployed"]) / sa["deployed"],
            "run_pct": 100.0 * (sb["as_run"] - sa["as_run"]) / sa["as_run"],
        }
        deltas[s_arm] = d
        print(f"  {plain} -> {s_arm}: rank1 {sa['rank1']}->{sb['rank1']}, "
              f"top3 {sa['top3']}->{sb['top3']} (gain {d['gain'] or '—'}, "
              f"loss {d['loss'] or '—'}), rank-1 pick differs on {differ}/640")
        print(f"     rank1 nodes {sa['rank1_nodes']:,} -> {sb['rank1_nodes']:,} "
              f"({d['r1_pct']:+.1f}%), deployed {sa['deployed']:,} -> "
              f"{sb['deployed']:,} ({d['dep_pct']:+.1f}%), as-run "
              f"{sa['as_run']:,} -> {sb['as_run']:,} ({d['run_pct']:+.1f}%)")

    md = [
        f"# The four CoV top-3 arms at budget {100000:,}, all 640 ms640 presentations\n",
        f"Zero search nodes — a regrouping of four frozen result files in this "
        f"directory, from "
        f"[`cov_top3_arm_compare.py`](../../../../experiments/stable_ac/cov/run/cov_top3_arm_compare.py). "
        f"The `_s` arms ran on Colab on 2026-08-11; `abel` and `len` shipped on "
        f"08-10. All four cover the same 640 presentations at `k = 3`, "
        f"`max_relator_length 24`, cyclic reduction on, and all four embed the "
        f"**same** baseline column (asserted, not assumed).\n",
        f"Three accountings are kept apart because they point in opposite "
        f"directions. **rank1** is the first pick alone; **deployed** is "
        f"cumulative nodes up to and including the first *solving* rank — what a "
        f"deployment stopping on success would spend; **as-run** is all three "
        f"ranks, which is what these runs actually burned. The recorded runs do "
        f"**not** early-stop: all three candidates execute even after rank 1 "
        f"solves, so `stop3` in the filenames does not mean early-stop in the "
        f"data.\n",
        "| arm | rank 1 | top 3 | rank-1 nodes | deployed | as-run | median path | unsolved |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for arm, _ in ARMS:
        s = S[arm]
        md.append(f"| `{arm}` | {s['rank1']} / {s['n']} | **{s['top3']} / {s['n']}** | "
                  f"{s['rank1_nodes']:,} | {s['deployed']:,} | {s['as_run']:,} | "
                  f"{s['med_plen']} | {', '.join(map(str, s['unsolved'])) or '—'} |")
    md.append(f"| *baseline, untransformed* | — | {b_solved} / 640 | — | "
              f"{b_nodes:,} | — | {b_plen} | — |")
    md += [
        "",
        f"**On the abel arm `S` buys no solves at all, and that was predicted.** "
        f"Shipped `abel` already solves {S['abel']['rank1']}/640 at rank 1 at this "
        f"budget, so there is no solve headroom for any abel-first arm to take — "
        f"`RESULTS.md` said so before this run. What `S` does move is cost: the "
        f"rank-1 bill falls **{S['abel']['rank1_nodes']:,} → "
        f"{S['abel_len_rd_s']['rank1_nodes']:,} nodes "
        f"({deltas['abel_len_rd_s']['r1_pct']:+.1f}%)**, and it gets there by "
        f"changing the rank-1 pick on **{deltas['abel_len_rd_s']['differ']} of 640** "
        f"presentations. Over half the picks change and the solve set does not "
        f"move — the same 640, not merely the same count.\n",
        f"**On the length arm `S` buys exactly one row.** Rank 1 is unchanged at "
        f"{S['len']['rank1']}/640, but top-3 goes **{S['len']['top3']} → "
        f"{S['len_rd_s']['top3']}**, recovering presentation "
        f"{deltas['len_rd_s']['gain'][0] if deltas['len_rd_s']['gain'] else '—'}. "
        f"Only {', '.join(map(str, S['len_rd_s']['unsolved']))} remains unsolved "
        f"on that arm. The rank-1 bill goes the wrong way "
        f"({deltas['len_rd_s']['r1_pct']:+.1f}%) while deployed improves "
        f"({deltas['len_rd_s']['dep_pct']:+.1f}%).\n",
        f"**Priced as it was actually run, `abel_len_rd_s` is much the dearest "
        f"arm**: {S['abel_len_rd_s']['as_run']:,} nodes against `abel`'s "
        f"{S['abel']['as_run']:,} ({deltas['abel_len_rd_s']['run_pct']:+.1f}%), "
        f"{S['abel_len_rd_s']['hours']:.1f} h of wall clock against "
        f"{S['abel']['hours']:.1f} h. This is the budget-1,000 finding at scale: "
        f"`S` fills slots 2 and 3 with near-copies of the rank-1 pick, and on the "
        f"rows where rank 1 already solved, those near-copies still run and still "
        f"cost. The arm is cheaper only if the deployment actually stops on "
        f"success, and these runs did not.\n",
        f"**No escapes.** The untransformed baseline solves {b_solved}/640 at its "
        f"own {budget:,}-node budget, so nothing here is a solvability win over "
        f"the baseline; the win is cost and path length. Note the budgets are not "
        f"matched — the baseline had {budget:,} per presentation, each CoV "
        f"candidate 100,000 — so the honest comparison is nodes actually spent, "
        f"which is the column above: `abel_len_rd_s` reaches the same 640/640 for "
        f"{S['abel_len_rd_s']['deployed']:,} deployed nodes against the baseline's "
        f"{b_nodes:,}, and with a shorter median path "
        f"({S['abel_len_rd_s']['med_plen']} vs {b_plen}).\n",
        f"Reproduce: `.venv/bin/python3 -m "
        f"experiments.stable_ac.cov.run.cov_top3_arm_compare`\n",
    ]
    path = os.path.join(ROOT, OUT_MD)
    with open(path, "w") as fh:
        fh.write("\n".join(md))
    print(f"\nwrote {OUT_MD}")
    return S, deltas


if __name__ == "__main__":
    main()
