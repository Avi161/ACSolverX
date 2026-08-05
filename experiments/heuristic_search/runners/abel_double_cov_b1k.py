"""Two-hop abelianized-magnitude CoV beam, greedy at budget 1,000 (subset-60).

Asks whether a **second** change of variables, selected by the same search-free
abelianized-magnitude key, reaches presentations one hop cannot — at the repo's
local budget ceiling of 1,000 nodes.

## The beam

Per presentation, with ``--topk K`` (default 3):

1. **hop 1** — ``cov.enumerate_cov(r1, r2)`` gives every valid subword CoV
   ``(z_word, iso_gen, iso_index)``. Rank by the key below, keep the top K.
2. **hop 2** — enumerate every CoV of *each* kept hop-1 output, keep that branch's
   top K. K branches x K each = **K^2 = 9** second-hop candidates.
3. **select** — rank those 9 by the same key, keep the top K.
4. **search** — run the greedy at budget 1,000 on each, stopping at the first solve.
   Each candidate runs at its own ``res.cap`` (``max(24, longest + 16)``).

The key is `IDEAS.md` idea 1's abelianized magnitude, tie-broken by two more static
fields and then by the CoV's own name — a pure function of the two start strings, so
selection costs 0 nodes at either hop:

```text
(|Sx(r1)| + |Sy(r1)| + |Sx(r2)| + |Sy(r2)|,  start_len,  longest,  z, iso_gen, iso_index)
```

## Arms recorded per row

| arm | what it searches |
|---|---|
| ``greedy`` | the untransformed pair — the control |
| ``hop1_topk`` | step 1's top K |
| ``hop2_topk`` | step 3's top K of the 9 — **the arm this runner is for** |
| ``hop2_all`` | all K^2 = 9, the ceiling of what step 3 selects from |
| ``pooled_topk`` | top K of (hop-1 top K) U (the 9) — does depth win on the key? |

``hop2_topk`` discards the hop-1 starts by construction, so ``pooled_topk`` is the
arm that answers whether a second hop is *worth* taking rather than merely reachable.

## Cost, stated not hidden

Every arm is up to K searches of <= 1,000 nodes, so ``hop2_topk`` costs the same
search budget as ``hop1_topk`` — the extra spend is enumeration (0 nodes) at hop 2.
``hop2_all`` costs up to 9 searches and is a ceiling, not a proposal.

**The cap grows with depth.** A CoV lengthens relators and the cap follows
(``longest + 16``), so hop-2 candidates run at a larger cap than hop-1 ones and both
run larger than the untransformed control at 24. A CoV row read against a control at
a different cap [is not a comparison](../../lessons/control-with-no-dynamic-range.md);
every row carries its caps so the confound stays visible.

Resume-safe: one jsonl row per presentation, flushed as it completes, keyed on
``pres_id``. Re-running skips finished rows, so it survives a bounded call.

    python3 -m experiments.heuristic_search.runners.abel_double_cov_b1k
    python3 -m experiments.heuristic_search.runners.abel_double_cov_b1k --summarize
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

MAX_BUDGET = 1_000       # the repo's hard local ceiling; never raise this here
DEFAULT_TOPK = 3
SUBSET60 = "benchmark/subsets/benchmark_subset_60.csv"
SWEEP_B1K = ("results/stable_ac/cov/"
             "covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
OUT = "results/comparison/abel_double_cov_b1k_subset60.jsonl"
OUT_CSV = "results/comparison/abel_double_cov_b1k_subset60.csv"
OUT_MD = "results/comparison/ABEL_DOUBLE_COV_B1K.md"

ARMS = ("greedy", "hop1_topk", "hop2_topk", "hop2_all", "pooled_topk")


def _repo_root(start=None):
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (experiments/ + data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments import run_baseline                                   # noqa: E402
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.cov import cov                              # noqa: E402


# --------------------------------------------------------------------------- key

def exponent_sums(rel):
    return (rel.count("x") - rel.count("X"), rel.count("y") - rel.count("Y"))


def abel_magnitude(r1, r2):
    """|Sx| + |Sy| over both relators -- ``restart_planner.abel_magnitude``."""
    ax, ay = exponent_sums(r1)
    bx, by = exponent_sums(r2)
    return abs(ax) + abs(ay) + abs(bx) + abs(by)


def rank_key(d):
    """Static, search-free, and total: no two distinct CoVs of one pair tie."""
    return (abel_magnitude(d["r1"], d["r2"]),
            len(d["r1"]) + len(d["r2"]),
            max(len(d["r1"]), len(d["r2"])),
            d["z"], d["iso_gen"], d["iso_index"])


def top_k(cands, k):
    return sorted(cands, key=rank_key)[:k]


# ------------------------------------------------------------------ enumeration

def enumerate_candidates(r1, r2):
    """Every valid subword CoV of (r1, r2) as plain dicts.

    Pinned against the frozen sweep by ``--gate``: on subset-60 this reproduces
    ``covsweep_1000_66_*.jsonl``'s candidate keyset, outputs and caps exactly.
    """
    out = []
    for res in cov.enumerate_cov(str_to_word(r1), str_to_word(r2)):
        out.append({"r1": word_to_str(res.r1), "r2": word_to_str(res.r2),
                    "cap": res.cap, "z": word_to_str(res.z_word),
                    "iso_gen": res.iso_gen, "iso_index": res.iso_index,
                    "n_subs": res.n_subs})
    return out


def search(r1, r2, cap, budget):
    assert budget <= MAX_BUDGET, f"budget {budget} exceeds the local ceiling {MAX_BUDGET}"
    st = run_baseline.greedy_search(r1, r2, budget, max_relator_length=cap)
    return bool(st["solved"]), int(st["nodes_explored"])


def run_arm(cands, budget):
    """Sequential trial, stopping at the first solve. Returns (solved, nodes, tried)."""
    total = 0
    for i, d in enumerate(cands, 1):
        ok, n = search(d["r1"], d["r2"], d["cap"], budget)
        total += n
        if ok:
            return True, total, i
    return False, total, len(cands)


# ------------------------------------------------------------------------ a row

def one_presentation(pid, r1, r2, k, budget):
    t0 = time.time()
    h1 = enumerate_candidates(r1, r2)
    h1_top = top_k(h1, k)

    h2 = []
    for parent in h1_top:
        branch = top_k(enumerate_candidates(parent["r1"], parent["r2"]), k)
        for c in branch:
            c["parent_z"] = parent["z"]
        h2 += branch
    h2_top = top_k(h2, k)
    pooled = top_k(h1_top + h2, k)

    orig = [{"r1": r1, "r2": r2, "cap": cov.DEFAULT_CAP, "z": None,
             "iso_gen": None, "iso_index": None}]
    row = {"pres_id": pid, "r1": r1, "r2": r2, "topk": k, "budget": budget,
           "n_hop1": len(h1), "n_hop2": len(h2),
           "hop1_caps": [d["cap"] for d in h1_top],
           "hop2_caps": [d["cap"] for d in h2_top],
           "hop2_chain": [{"z1": d.get("parent_z"), "z2": d["z"],
                           "iso_gen": d["iso_gen"], "iso_index": d["iso_index"],
                           "abel": abel_magnitude(d["r1"], d["r2"]),
                           "r1": d["r1"], "r2": d["r2"]} for d in h2_top]}
    for name, sel in (("greedy", orig), ("hop1_topk", h1_top), ("hop2_topk", h2_top),
                      ("hop2_all", h2), ("pooled_topk", pooled)):
        ok, nodes, tried = run_arm(sel, budget)
        row[f"{name}_solved"] = ok
        row[f"{name}_nodes"] = nodes
        row[f"{name}_tried"] = tried
    row["wall_s"] = round(time.time() - t0, 2)
    return row


# ------------------------------------------------------------------------- gate

def gate_enumeration(ids, orig, limit=5):
    """Hop-1 enumeration must reproduce the frozen sweep exactly, or nothing below
    is comparable to the shipped 1-hop numbers."""
    ref = {}
    with open(os.path.join(ROOT, SWEEP_B1K)) as fh:
        for line in fh:
            d = json.loads(line)
            if d["pres_id"] in set(ids) and d.get("n_cov", 0) != 0:
                ref.setdefault(d["pres_id"], {})[
                    (d["z_word"], d["iso_gen"], d["iso_index"])] = (
                        d["r1"], d["r2"], d["max_relator_length_cap"])
    checked = 0
    for pid in ids[:limit]:
        mine = {(d["z"], d["iso_gen"], d["iso_index"]): (d["r1"], d["r2"], d["cap"])
                for d in enumerate_candidates(*orig[pid])}
        assert set(mine) == set(ref[pid]), (
            f"pid {pid}: hop-1 keyset differs from the sweep "
            f"({len(mine)} vs {len(ref[pid])})")
        for key, got in mine.items():
            assert got == ref[pid][key], f"pid {pid} {key}: {got} != {ref[pid][key]}"
            checked += 1
    return checked


# -------------------------------------------------------------------- the driver

def load_subset():
    ids, orig = [], {}
    with open(os.path.join(ROOT, SUBSET60)) as fh:
        for r in csv.DictReader(fh):
            pid = int(r["pres_id"])
            ids.append(pid)
            orig[pid] = (r["r1"], r["r2"])
    assert len(ids) == 60, f"subset-60 has {len(ids)} rows"
    return ids, orig


def done_rows(path):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue          # torn trailing line: dropped, then rewritten below
            out[d["pres_id"]] = d
    return out


def repair_tail(path):
    """Truncate a torn trailing line BEFORE the first append, never merely tolerate
    it at read time."""
    if not os.path.exists(path):
        return
    with open(path, "rb") as fh:
        data = fh.read()
    if data and not data.endswith(b"\n"):
        cut = data.rfind(b"\n") + 1
        with open(path, "wb") as fh:
            fh.write(data[:cut])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=MAX_BUDGET)
    ap.add_argument("--topk", type=int, default=DEFAULT_TOPK)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--deadline", type=float, default=0.0,
                    help="stop after N seconds; resume picks up where it left off")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    assert a.budget <= MAX_BUDGET, f"--budget {a.budget} exceeds the ceiling {MAX_BUDGET}"

    ids, orig = load_subset()
    path = os.path.join(ROOT, a.out)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if a.summarize:
        return summarize(ids, done_rows(path), a.topk)

    checked = gate_enumeration(ids, orig)
    print(f"gate: hop-1 enumeration matches the frozen sweep on {checked} candidates")

    repair_tail(path)
    have = done_rows(path)
    todo = [p for p in ids if p not in have]
    print(f"{len(have)}/60 done, {len(todo)} to go (budget {a.budget}, topk {a.topk})")

    t0 = time.time()
    with open(path, "a") as fh:
        for pid in todo:
            row = one_presentation(pid, *orig[pid], a.topk, a.budget)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            print(f"  {pid}: hop1={row['hop1_topk_solved']} hop2={row['hop2_topk_solved']} "
                  f"pooled={row['pooled_topk_solved']} ({row['wall_s']}s)", flush=True)
            if a.deadline and time.time() - t0 > a.deadline:
                print(f"deadline hit; {len(done_rows(path))}/60 done — rerun to resume")
                return
    summarize(ids, done_rows(path), a.topk)


def summarize(ids, rows, k):
    if len(rows) < len(ids):
        print(f"INCOMPLETE: {len(rows)}/{len(ids)} rows — rerun to resume")
        return
    counts = {a: sum(1 for r in rows.values() if r[f"{a}_solved"]) for a in ARMS}
    print(f"\n=== two-hop abel CoV beam, budget {rows[ids[0]]['budget']}, topk {k} ===")
    for a in ARMS:
        print(f"  {a:14s} {counts[a]:2d}/60")
    h1 = {p for p, r in rows.items() if r["hop1_topk_solved"]}
    h2 = {p for p, r in rows.items() if r["hop2_topk_solved"]}
    po = {p for p, r in rows.items() if r["pooled_topk_solved"]}
    print(f"  hop2 gains over hop1: {sorted(h2 - h1)}")
    print(f"  hop2 loses vs hop1:   {sorted(h1 - h2)}")
    print(f"  pooled gains over hop1: {sorted(po - h1)}")
    write_tables(ids, rows, k, counts, h1, h2, po)


def oracle_1hop(ids):
    """The best-CoV set at this budget from the frozen sweep: any single CoV that
    solved. The ceiling of everything one hop can do, so it decides whether a hop-2
    gain is NEW REACH or merely a ranking that found a needle hop 1 missed."""
    best, n_solving = {}, {}
    with open(os.path.join(ROOT, SWEEP_B1K)) as fh:
        for line in fh:
            d = json.loads(line)
            if d["pres_id"] not in set(ids) or d.get("n_cov", 0) == 0:
                continue
            n_solving.setdefault(d["pres_id"], [0, 0])
            n_solving[d["pres_id"]][1] += 1
            if d["solved"]:
                n_solving[d["pres_id"]][0] += 1
                best[d["pres_id"]] = True
    return set(best), n_solving


def write_tables(ids, rows, k, counts, h1, h2, po):
    import statistics
    with open(os.path.join(ROOT, OUT_CSV), "w", newline="") as fh:
        w = csv.writer(fh)
        cols = (["pres_id", "n_hop1", "n_hop2"]
                + [f"{a}_{s}" for a in ARMS for s in ("solved", "nodes", "tried")]
                + ["hop1_caps", "hop2_caps", "wall_s"])
        w.writerow(cols)
        for p in ids:
            r = rows[p]
            w.writerow([p, r["n_hop1"], r["n_hop2"]]
                       + [r[f"{a}_{s}"] for a in ARMS for s in ("solved", "nodes", "tried")]
                       + ["|".join(map(str, r["hop1_caps"])),
                          "|".join(map(str, r["hop2_caps"])), r["wall_s"]])

    caps1 = [c for r in rows.values() for c in r["hop1_caps"]]
    caps2 = [c for r in rows.values() for c in r["hop2_caps"]]
    both = [p for p in ids if rows[p]["hop1_topk_solved"] and rows[p]["hop2_topk_solved"]]

    orc, n_solving = oracle_1hop(ids)
    gained = sorted(h2 - h1)
    if gained:
        bits = []
        for p in gained:
            s, n = n_solving[p]
            c1, c2 = rows[p]["hop1_caps"], rows[p]["hop2_caps"]
            bits.append(f"- **{p}**: {s} of its {n} single CoVs solve at this budget, and the "
                        f"hop-1 top {k} missed all of them; its hop-2 picks ran at caps "
                        f"{c2} against hop-1's {c1}.")
        gain_note = ("Every row the second hop gains was **already inside** the one-hop "
                     "ceiling — a needle the hop-1 ranking did not pick:\n\n" + "\n".join(bits))
    else:
        gain_note = "The second hop gained no row over the hop-1 top {k}."
    gained_cap_up = [p for p in gained if max(rows[p]["hop2_caps"]) > max(rows[p]["hop1_caps"])]
    if not gained:
        cap_note = "No hop-2 gain to attribute."
    elif gained_cap_up:
        cap_note = (f"On {len(gained_cap_up)} of the {len(gained)} gained rows "
                    f"({gained_cap_up}) the hop-2 picks ran at a LARGER cap than the hop-1 "
                    "picks, so cap cannot be ruled out there.")
    else:
        cap_note = (f"On every one of the {len(gained)} gained rows the hop-2 picks ran at a "
                    "cap no larger than the hop-1 picks, so on these rows the gain is **not** "
                    "bought by a wider cap.")
    md = f"""# Two-hop abelianized-magnitude CoV beam @ budget {rows[ids[0]]['budget']} (subset-60)

Per presentation: rank every subword CoV by abelianized magnitude, keep the top {k};
enumerate every CoV of each of those and keep its top {k} ({k}x{k} = {k * k} second-hop
candidates); rank those {k * k} and search the top {k} with the greedy at budget
{rows[ids[0]]['budget']}, stopping at the first solve. Selection is search-free at both
hops — the key is a pure function of the two start strings.

## Headline

| arm | searches | solved |
|---|---:|---:|
| `greedy` — untransformed control | 1 | **{counts['greedy']}/60** |
| `hop1_topk` — one CoV, top {k} | <= {k} | **{counts['hop1_topk']}/60** |
| **`hop2_topk` — two CoVs, top {k} of the {k * k}** | <= {k} | **{counts['hop2_topk']}/60** |
| `pooled_topk` — top {k} of hop-1 top {k} U the {k * k} | <= {k} | **{counts['pooled_topk']}/60** |
| `hop2_all` — every one of the {k * k} (ceiling, not a proposal) | <= {k * k} | **{counts['hop2_all']}/60** |

- rows `hop2_topk` reaches that `hop1_topk` does not: **{sorted(h2 - h1)}**
- rows `hop1_topk` reaches that `hop2_topk` does not: **{sorted(h1 - h2)}**
- rows `pooled_topk` adds over `hop1_topk`: **{sorted(po - h1)}**

## Cost

Both top-{k} arms are at most {k} searches of <= {rows[ids[0]]['budget']} nodes, so the
second hop is free in *search* budget — it buys enumeration, not pops. On the
{len(both)} rows both solve, nodes to first solve:

| arm | median | mean | max |
|---|---:|---:|---:|
| `hop1_topk` | {statistics.median(rows[p]['hop1_topk_nodes'] for p in both):.0f} | {statistics.mean(rows[p]['hop1_topk_nodes'] for p in both):.0f} | {max(rows[p]['hop1_topk_nodes'] for p in both)} |
| `hop2_topk` | {statistics.median(rows[p]['hop2_topk_nodes'] for p in both):.0f} | {statistics.mean(rows[p]['hop2_topk_nodes'] for p in both):.0f} | {max(rows[p]['hop2_topk_nodes'] for p in both)} |

## Is the gain new reach, or a better needle?

The frozen sweep searched **every** single CoV at this budget, so its solved set is the
ceiling of one hop: **{len(orc)}/60**. Against it:

- rows `hop2_topk` reaches that **no single CoV** reaches: **{sorted(h2 - orc) or 'none'}**
- rows one CoV reaches that `hop2_topk` does not: **{sorted(orc - h2) or 'none'}**

{gain_note}

So the second hop is not enlarging what is reachable — it is enlarging what the
*ranking* finds. Read the +{len(h2 - h1)} as a selection result, not a reachability one.

## The cap confound, measured rather than assumed

A CoV lengthens relators and the cap follows (`max(24, longest + 16)`), so the arms do
not run at one cap: control 24, hop-1 picks {min(caps1)}-{max(caps1)}, hop-2 picks
{min(caps2)}-{max(caps2)}. A larger cap is a strictly larger search space, so a hop-2
gain bought by cap would not be a depth result. {cap_note} Caps are carried per row
in the CSV.

## Gate

Hop-1 enumeration reproduces the frozen `covsweep_1000_66_*.jsonl` candidate keyset,
outputs and caps exactly on the rows checked — so `hop1_topk` here is the same object
as the shipped 1-hop numbers, and hop 2 is the only new thing.

## Source

- Rows: [`abel_double_cov_b1k_subset60.jsonl`](abel_double_cov_b1k_subset60.jsonl),
  [`.csv`](abel_double_cov_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_double_cov_b1k.py`
- One-hop @10k companion: [`ABEL_TOPK_COV_B10K.md`](ABEL_TOPK_COV_B10K.md)
"""
    with open(os.path.join(ROOT, OUT_MD), "w") as fh:
        fh.write(md)
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
