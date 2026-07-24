"""EXP-25 -- relabels at FULL budget, on the rows where it can actually show.

Three experiments have circled this and none has answered it:

- **EXP-17** gave the eight signed-permutation relabels a *divided* budget (1000/k each) and lost
  monotonically, because a divided search that succeeds almost always succeeds on the first string.
- **EXP-12** gave them a *full* budget each, but on the 124 unsolved classes -- where nothing solves
  under any ordering, so the arm had no dynamic range and could only report zero.
- **EXP-21** gave a *full* budget to different **orderings**, and that did gain (+4 rows, ~+1.18
  cross-validated). But it varied the ordering, not the starting string.

So the one combination that matters is untested: **the same ordering, run from all eight relabels,
at full budget each, on the decidable band.** This is the version the repo's own history predicts
should work -- relabels supplied 14 of 17 unsolved->solved flips in the one-hop CoV sweep -- and it
is the cheapest thing a user with spare compute can do, since it needs no new ordering and no
tuning.

A relabel renames the generators. It preserves the AC-class and every orbit-level invariant, so it
is the *same problem*; but the greedy reads strings, so each image is a different search. That is
why this can gain at all, and also why a gain is not a mathematical result -- it is a statement
about the solver's sensitivity to presentation.

Reported as: how many of the 24 decidable rows are solved by the identity relabel alone (which is
what every number in this program used), against how many are solved by *at least one* of the
eight. The marginal rows are named.

    python3 -m experiments.heuristic_search.exp25_relabels_full
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402
from experiments.equivalence_classes.lib import words              # noqa: E402

BUDGET = 1_000
MRL = 48
OUT = os.path.join(LOGS, "EXP25_relabels_full.jsonl")

ORDERINGS = {
    "recommended": {"segments": [
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
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
            done.add((r["ordering"], r["name"], r["relabel"]))

    n_starts = sum(1 for _ in words.SIGNED_PERMS)
    print(f"  {len(rows)} rows x {n_starts} relabels x {len(ORDERINGS)} orderings at FULL "
          f"budget {BUDGET}", flush=True)

    with open(OUT, "a") as f:
        for label, cfg in ORDERINGS.items():
            for row in rows:
                seen_pairs = set()
                for perm_name, img in words.SIGNED_PERMS:
                    a, b = words.apply_pair((row["r1"], row["r2"]), img)
                    if (a, b) in seen_pairs:
                        continue            # a symmetric pair is fixed by some permutations
                    seen_pairs.add((a, b))
                    if (label, row["name"], perm_name) in done:
                        continue
                    res = search_fast(a, b, BUDGET, cfg, MRL)
                    f.write(json.dumps({
                        "ordering": label, "name": row["name"], "bin": bin_of(row["name"]),
                        "relabel": perm_name, "identity": perm_name == "x->x,y->y",
                        "budget": BUDGET, "mrl": MRL, "solved": res["solved"],
                        "nodes": res["nodes"], "path_length": res["path_length"]}) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    lines = ["# EXP-25 — the same ordering from all eight relabels, at full budget each", "",
             f"Decidable band (bins 4–7, {n} rows), budget {BUDGET} **each**, cap {MRL}. A relabel "
             "renames the generators: same AC-class, same orbit invariants, *different string* — "
             "and the greedy reads strings. This is the combination EXP-17 (divided budget), "
             "EXP-12 (no dynamic range) and EXP-21 (varied the ordering, not the string) each left "
             "untested.", "",
             "| ordering | identity relabel only | any of the 8 | gain | rows added |",
             "|---|---|---|---|---|"]

    detail = {}
    for label in ORDERINGS:
        d = [r for r in data if r["ordering"] == label]
        ident = {r["name"] for r in d if r["identity"] and r["solved"]}
        anyr = {r["name"] for r in d if r["solved"]}
        add = sorted(anyr - ident)
        detail[label] = (ident, anyr, add)
        lines.append(f"| {label} | {len(ident)}/{n} | **{len(anyr)}**/{n} | "
                     f"**{len(anyr) - len(ident):+d}** | "
                     + (", ".join(f"`{a}`" for a in add) if add else "—") + " |")

    lines += ["", "## Verdict", ""]
    rec_i, rec_a, rec_add = detail.get("recommended", (set(), set(), []))
    if rec_add:
        lines += [f"Running the recommended ordering from all eight relabels solves "
                  f"**{len(rec_a)}/{n}** against **{len(rec_i)}/{n}** from the presentation as "
                  f"written — **{len(rec_a) - len(rec_i)} extra rows** for 8× the compute and no "
                  "new tuning. The repo's earlier finding (relabels supplied 14 of 17 flips in the "
                  "one-hop sweep) reproduces here on a different tier and a different ordering.", "",
                  "This is the cheapest available win for someone with spare compute: no new "
                  "ordering, no re-tuning, and the eight searches are embarrassingly parallel. It "
                  "is also *not* a mathematical result — a relabel is the same problem, so what it "
                  "measures is the solver's sensitivity to how a presentation happens to be "
                  "written.", ""]
    else:
        lines += [f"Relabels add **nothing** at full budget on this tier: "
                  f"{len(rec_a)}/{n} from all eight against {len(rec_i)}/{n} from the identity "
                  "alone. The repo's 14-of-17 flip result came from a different setting (one-hop "
                  "CoV starts at a smaller budget), and it does not transfer to the tuned ordering "
                  "here — this ordering appears insensitive to how the presentation is written, "
                  "which is a mildly reassuring property in itself.", ""]

    # Which relabel does the work, when one does?
    lines += ["## Which relabel solves, when the identity does not", "",
              "| ordering | row | relabel that solved it | nodes |", "|---|---|---|---|"]
    any_row = False
    for label in ORDERINGS:
        ident, _, add = detail[label]
        for nm in add:
            for r in data:
                if r["ordering"] == label and r["name"] == nm and r["solved"]:
                    lines.append(f"| {label} | `{nm}` | `{r['relabel']}` | {r['nodes']} |")
                    any_row = True
                    break
    if not any_row:
        lines.append("| — | — | — | — |")

    with open(os.path.join(LOGS, "EXP25_relabels_full.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
