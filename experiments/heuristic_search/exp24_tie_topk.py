"""EXP-24 -- the two search parameters that were never hyperparameters here.

Twenty-three experiments varied the heap *priority*. Two other knobs sat fixed the whole time,
inherited from the base solver rather than chosen, and both plausibly matter:

**The tie-break.** Every heap entry is ``(priority, tie * depth, key)``. Ties are not a corner
case for a structural ordering: knot counts and block counts are small integers, so a weighted sum
of them collides far more often than a length ordering's key does, and the tie-break silently
decides a large share of pops. ``tie = +1`` pops the shallowest of several equally-scored states,
``tie = -1`` the deepest. This is **not** the depth term EXP-11 ruled out -- it never changes a
score, so it never reorders states with different priorities. It only picks among exact ties, which
is a much lighter intervention and could plausibly survive where the score term did not.

**Child filtering (``topk``).** Every search so far expanded *all* children of a pop. Keeping only
the ``k`` shortest is classic beam filtering: it makes the search incomplete, but spends the budget
deeper along fewer lines. At a saturated climb a pop can generate thousands of children, almost all
of them immediately discarded by the priority anyway, so the trade is not obviously bad.

Both are swept across the orderings still in play, at both budgets, with the current settings
(``tie=+1``, ``topk=0``) present as the control so any gain is measured against what is actually
recommended today.

    python3 -m experiments.heuristic_search.exp24_tie_topk
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

MRL = 48
OUT = os.path.join(LOGS, "EXP24_tie_topk.jsonl")
TIES = (1, -1)
TOPKS = (0, 8, 16, 32, 64, 128)

ORDERINGS = {
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
    "recommended": {"segments": [
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "phased K8": {"segments": [{"upto": 16, "w": {"L": 1.0}},
                               {"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
}


def main():
    rows = [r for r in bench66() if r["source"] == "ladder" and bin_of(r["name"]) in (4, 5, 6, 7)]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["ordering"], r["tie"], r["topk"], r["name"], r["budget"]))

    total = len(ORDERINGS) * len(TIES) * len(TOPKS) * len(rows) * 2
    print(f"  {len(ORDERINGS)} orderings x {len(TIES)} ties x {len(TOPKS)} topk x "
          f"{len(rows)} rows x 2 budgets = {total} searches", flush=True)

    with open(OUT, "a") as f:
        for budget in (500, 1000):
            for label, cfg in ORDERINGS.items():
                for tie in TIES:
                    for topk in TOPKS:
                        for row in rows:
                            k = (label, tie, topk, row["name"], budget)
                            if k in done:
                                continue
                            res = search_fast(row["r1"], row["r2"], budget, cfg, MRL,
                                              tie=tie, topk=topk)
                            f.write(json.dumps({
                                "ordering": label, "tie": tie, "topk": topk,
                                "name": row["name"], "bin": bin_of(row["name"]),
                                "budget": budget, "mrl": MRL,
                                "solved": res["solved"], "nodes": res["nodes"],
                                "path_length": res["path_length"]}) + "\n")
                            f.flush()
                            os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)

    def score(label, tie, topk, budget):
        d = [r for r in data if r["ordering"] == label and r["tie"] == tie
             and r["topk"] == topk and r["budget"] == budget]
        return sum(r["solved"] for r in d) if d else None

    lines = ["# EXP-24 — the tie-break and child filtering, the two knobs never swept here", "",
             f"Decidable band (bins 4–7, {n} rows), cap {MRL}. `tie = +1` pops the shallowest of "
             "equally-scored states (what everything so far used), `-1` the deepest. `topk = 0` "
             "keeps every child (also what everything used); a positive value keeps only that many "
             "shortest children.", "",
             "The tie-break is **not** EXP-11's depth term: it never changes a state's score, so "
             "it cannot reorder states with different priorities — it only decides exact ties, "
             "which a structural ordering produces constantly.", ""]

    for budget in (500, 1000):
        lines += [f"## Budget {budget}", "",
                  "| ordering | tie | " + " | ".join(f"topk={k or 'all'}" for k in TOPKS) + " |",
                  "|---" * (len(TOPKS) + 2) + "|"]
        for label in ORDERINGS:
            ctrl = score(label, 1, 0, budget)
            for tie in TIES:
                cells = []
                for topk in TOPKS:
                    v = score(label, tie, topk, budget)
                    if v is None:
                        cells.append("—")
                    elif ctrl is not None and v > ctrl:
                        cells.append(f"**{v}**")
                    else:
                        cells.append(str(v))
                tag = " ← current" if tie == 1 else ""
                lines.append(f"| {label}{tag} | {tie:+d} | " + " | ".join(cells) + " |")
        lines.append("")

    # Verdicts, each against that ordering's own current setting.
    beat_tie, beat_topk = [], []
    for budget in (500, 1000):
        for label in ORDERINGS:
            ctrl = score(label, 1, 0, budget)
            if ctrl is None:
                continue
            v = score(label, -1, 0, budget)
            if v is not None and v > ctrl:
                beat_tie.append((budget, label, v, ctrl))
            for topk in TOPKS[1:]:
                for tie in TIES:
                    v = score(label, tie, topk, budget)
                    if v is not None and v > ctrl:
                        beat_topk.append((budget, label, tie, topk, v, ctrl))

    lines += ["## Verdict", ""]
    if beat_tie:
        lines += ["Flipping the tie-break to **deepest-first** beats the current setting in:", ""]
        for b, l, v, c in beat_tie:
            lines.append(f"- budget {b}, `{l}`: {v}/{n} against {c}/{n}")
        lines.append("")
    else:
        lines += ["**The tie-break does not want flipping.** Preferring the deepest of several "
                  "equally-scored states never beats preferring the shallowest, for any ordering "
                  "at either budget. The inherited `+1` was the right default — now measured "
                  "rather than assumed.", ""]
    if beat_topk:
        lines += [f"Child filtering beats keeping everything in {len(beat_topk)} of "
                  f"{len(ORDERINGS) * len(TIES) * (len(TOPKS) - 1) * 2} arms:", ""]
        for b, l, t, k, v, c in sorted(beat_topk, key=lambda x: -(x[4] - x[5]))[:8]:
            lines.append(f"- budget {b}, `{l}`, tie {t:+d}, topk {k}: {v}/{n} against {c}/{n}")
        lines.append("")
    else:
        lines += ["**Child filtering never helps.** Keeping only the shortest `k` children loses "
                  "at every width tried, for every ordering, at both budgets. The priority is "
                  "already doing the filtering — a child that a beam would cut is one the heap "
                  "was never going to pop anyway, so the beam only removes states the search "
                  "would have needed later. Completeness is free here; incompleteness is not.", ""]

    with open(os.path.join(LOGS, "EXP24_tie_topk.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
