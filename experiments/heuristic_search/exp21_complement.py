"""EXP-21 -- if you have twice the budget, run two DIFFERENT orderings rather than one twice as long.

EXP-17 and EXP-20 both showed that *dividing* a fixed budget loses: across relabels the alternates
never fire, and across orderings the halving costs more than the complementarity buys. Both are
statements about a fixed budget. Neither answers the question a user with more compute actually
faces: given 2B nodes, is it better to give one ordering 2B, or two orderings B each?

The local rule caps a single search at 1,000 nodes, so "one ordering at 2,000" cannot be measured
here. But the other half can, and it is the half with new information. Two facts point at it:

- At budget 1,000 the union of **all five** finalists is 19/24 -- exactly what the best single one
  reaches. The finalists are redundant with each other; they solve the same rows. So "run several
  of the best orderings" is worth nothing, which is not obvious in advance.
- Yet four rows the finalists all miss (``ms568``, ``ms573``, ``ms578``, ``ms583``) *are* solved at
  the same budget and cap by 13-18 other configs from the sweeps -- and one of them,
  ``L + 7.547*smaller-block + 1.164*imbal``, carries **no knot term at all**.

That is the shape of a real complement: not another good knot ordering, but one from a different
family. This measures how far a deliberately chosen complement gets, alongside the recommended
climb, on the decidable band.

The honest caveat, stated in the report as well: the complement was **chosen because it solved
those rows**, so its union with the recommended climb is an optimistic estimate on exactly those
rows. What the number can support is the weaker, still useful claim -- that a second ordering from
a different family reaches rows the first cannot, which redundancy among the finalists had hidden.

    python3 -m experiments.heuristic_search.exp21_complement
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

BUDGET = 1_000
MRL = 48
OUT = os.path.join(LOGS, "EXP21_complement.jsonl")

ORDERINGS = {
    "recommended (richer knot climb)": {"segments": [
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "complement: S+imbal, no knots": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "S": 7.547, "imbal": 1.164}}]},
    "complement: Bmax+Lmax": {"segments": [
        {"upto": 14, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmax": -3.272, "Lmax": 5.679}}]},
    "complement: Bmin+Lmax+S+xyimb": {"segments": [
        {"upto": 12, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmin": -0.186, "Lmax": 5.519, "S": 5.369,
                             "xyimb": 2.3}}]},
    "blocks (a finalist, for contrast)": {"segments": [
        {"upto": None, "w": {"L": 1.0, "Bmax": -2.185, "S": 5.668}}]},
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
            done.add((r["ordering"], r["name"]))

    with open(OUT, "a") as f:
        for label, cfg in ORDERINGS.items():
            for row in rows:
                if (label, row["name"]) in done:
                    continue
                res = search_fast(row["r1"], row["r2"], BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "ordering": label, "name": row["name"], "bin": bin_of(row["name"]),
                    "budget": BUDGET, "mrl": MRL, "solved": res["solved"],
                    "nodes": res["nodes"], "path_length": res["path_length"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    solved = {}
    for r in data:
        solved.setdefault(r["ordering"], set())
        if r["solved"]:
            solved[r["ordering"]].add(r["name"])

    rec = "recommended (richer knot climb)"
    base = solved.get(rec, set())
    lines = ["# EXP-21 — a second ordering from a *different family*, at full budget", "",
             f"Decidable band (bins 4–7, {n} rows), budget {BUDGET} each, cap {MRL}. Each ordering "
             "gets a full budget — this is the 'I have more compute' question, not the "
             "'divide what I have' question that EXP-17 and EXP-20 both answered no.", "",
             "## Alone", "", "| ordering | solved |", "|---|---|"]
    for label, s in sorted(solved.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"| {label} | {len(s)}/{n} |")

    lines += ["", f"## Paired with the recommended climb ({len(base)}/{n} alone)", "",
              "| second ordering | union | rows it adds |", "|---|---|---|"]
    for label, s in solved.items():
        if label == rec:
            continue
        add = sorted(s - base)
        lines.append(f"| {label} | **{len(base | s)}**/{n} | "
                     + (", ".join(f"`{a}`" for a in add) if add else "—") + " |")

    everything = set().union(*solved.values()) if solved else set()
    lines += ["", f"Union of all {len(solved)} orderings: **{len(everything)}/{n}**.", "",
              "## Reading", ""]
    best_pair = max(((len(base | s), l) for l, s in solved.items() if l != rec), default=(0, None))
    if best_pair[0] > len(base):
        lines += [f"A second ordering from a different family reaches **{best_pair[0]}/{n}** "
                  f"against the recommended climb's {len(base)} alone — rows the knot climb cannot "
                  "reach at any point in its 1,000 nodes. Note that at budget 1,000 the union of "
                  "all five *finalists* is 19/24, exactly the best single: the finalists are "
                  "redundant with each other, and the gain here comes from leaving that family, "
                  "not from adding more of it.", "",
                  "**The honest caveat.** These complements were selected *because* they solved "
                  "rows the finalists miss, so the union above is optimistic on exactly those "
                  "rows. What it supports is the qualitative claim — a different family reaches "
                  "different presentations — not the specific count as an out-of-sample estimate. "
                  "The actionable form: with 2× the compute, run the recommended climb and one "
                  "structurally different ordering at full budget each, rather than one ordering "
                  "twice as long or two at half.", ""]
    else:
        lines += ["No second ordering adds anything to the recommended climb at full budget — the "
                  "complementarity seen in the wider sweeps does not survive a like-for-like "
                  "comparison here.", ""]

    with open(os.path.join(LOGS, "EXP21_complement.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
