"""EXP-26 -- the honest evaluation, on presentations no stage of this program has ever seen.

An independent audit showed the headline was contaminated: the recommended weight vector was
selected on the stratified 40-row slice, which contains 4 of the 7 rows later reported as
"held out". Removing every row any tuning stage read leaves **three** classes, and 1/3 -> 3/3 is
too thin a base for a recommendation.

Three is also the ceiling *within the benchmark*: the two training slices together cover 52 of its
60 ladder rows. But the benchmark's 60 rows were themselves drawn from
``data/ms640_solved.txt`` -- **640** solved Miller-Schupp presentations -- so the other **580 were
never in any slice, any sweep, any shortlist, or any report here.** They are exactly what is
needed, and they cost nothing but the searches.

Difficulty is taken from the baseline's own 10^6-node run (``results/benchmark/difficulty_bins.csv``,
the same source the benchmark's bins came from), so the rows can be stratified the same way and the
result is comparable to everything above. The evaluation is restricted to the **decidable band**
(bins 4-7): easier rows are solved by every ordering and harder ones by none, so neither can
separate two heuristics.

Nothing is selected here. The two orderings were fixed before this file was written; this only
scores them.

    python3 -m experiments.heuristic_search.exp26_clean_holdout
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, ROOT, bench66  # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.hsolve import (                  # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED,
)

MRL = 48
OUT = os.path.join(LOGS, "EXP26_clean_holdout.jsonl")
BINS_CSV = os.path.join(ROOT, "results", "benchmark", "difficulty_bins.csv")
MS640 = os.path.join(ROOT, "data", "ms640_solved.txt")

LENGTH_ONLY = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
ARMS = {
    "baseline (length)": LENGTH_ONLY,
    "recommended": RECOMMENDED,
    "lean (500 rec)": LEAN_SMALL_BUDGET,
}

_SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}


def _to_words(flat):
    """One ms640 line (flat ints, two equal halves, 0 = pad) -> (r1, r2) as strings."""
    half = len(flat) // 2
    return ("".join(_SYM[v] for v in flat[:half] if v != 0),
            "".join(_SYM[v] for v in flat[half:] if v != 0))


def clean_rows():
    """Decidable-band presentations from ms640 that no tuning stage in this program ever read."""
    seen_ids = {int(r["pres_id"]) for r in bench66() if r["source"] == "ladder"}

    bins = {}
    with open(BINS_CSV) as f:
        for r in csv.DictReader(f):
            try:
                bins[int(r["pres_id"])] = int(r["bin"])
            except (KeyError, ValueError):
                continue

    with open(MS640) as f:
        lines = [json.loads(l) for l in f if l.strip()]

    out = []
    for pid, flat in enumerate(lines):
        if pid in seen_ids:                 # in the benchmark -> possibly tuned on
            continue
        b = bins.get(pid)
        if b is None or b not in (4, 5, 6, 7):
            continue                        # keep only the band that can separate orderings
        r1, r2 = _to_words(flat)
        out.append({"name": f"ms{pid}", "pres_id": pid, "bin": b, "r1": r1, "r2": r2})
    return out


def main():
    rows = clean_rows()
    if not rows:
        raise SystemExit("no clean rows found -- check difficulty_bins.csv columns")
    import collections
    print(f"  {len(rows)} never-seen presentations in bins 4-7: "
          f"{dict(sorted(collections.Counter(r['bin'] for r in rows).items()))}", flush=True)

    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["arm"], r["name"], r["budget"]))

    with open(OUT, "a") as f:
        for budget in (500, 1000):
            for arm, cfg in ARMS.items():
                for row in rows:
                    if (arm, row["name"], budget) in done:
                        continue
                    res = search_fast(row["r1"], row["r2"], budget, cfg, MRL)
                    f.write(json.dumps({
                        "arm": arm, "name": row["name"], "pres_id": row["pres_id"],
                        "bin": row["bin"], "budget": budget, "mrl": MRL,
                        "solved": res["solved"], "nodes": res["nodes"],
                        "path_length": res["path_length"],
                        "min_total": res["min_total"]}) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    lines = ["# EXP-26 — the honest evaluation, on 580 never-seen presentations", "",
             f"`data/ms640_solved.txt` holds 640 solved Miller-Schupp presentations; the "
             f"benchmark's 60 ladder rows are drawn from it. The other 580 were never in any "
             f"slice, sweep, shortlist or report in this program. Restricted to the decidable band "
             f"(bins 4-7, graded by the baseline's own 10^6-node run) that leaves **{n} "
             "presentations**, and nothing here was selected on any of them — both orderings were "
             "fixed before this file existed.", "",
             "| budget | arm | solved |", "|---|---|---|"]

    summary = {}
    for budget in (500, 1000):
        for arm in ARMS:
            d = [r for r in data if r["arm"] == arm and r["budget"] == budget]
            if not d:
                continue
            s = sum(r["solved"] for r in d)
            summary[(budget, arm)] = s
            lines.append(f"| {budget} | {arm} | **{s}**/{len(d)} |")

    lines += ["", "## Against the contaminated figure", ""]
    for budget, rec in ((500, "lean (500 rec)"), (1000, "recommended")):
        b = summary.get((budget, "baseline (length)"))
        t = summary.get((budget, rec))
        if b is None or t is None:
            continue
        lines.append(f"- budget **{budget}**: baseline **{b}/{n}** → `{rec}` **{t}/{n}** "
                     f"(**{t - b:+d}**, {t/n:.0%} against {b/n:.0%})")
    lines += ["",
              "This replaces the three-class figure the audit left standing, and it is the number "
              "to quote: same decidable band, same caps, same orderings — on presentations that "
              "could not have leaked into the tuning, because they were never in any file this "
              "program read.", ""]

    lines += ["## Per bin", "",
              "| budget | arm | bin 4 | bin 5 | bin 6 | bin 7 |", "|---|---|---|---|---|---|"]
    for budget in (500, 1000):
        for arm in ARMS:
            cells = []
            for b in (4, 5, 6, 7):
                d = [r for r in data if r["arm"] == arm and r["budget"] == budget
                     and r["bin"] == b]
                cells.append(f"{sum(r['solved'] for r in d)}/{len(d)}" if d else "—")
            if any(c != "—" for c in cells):
                lines.append(f"| {budget} | {arm} | " + " | ".join(cells) + " |")

    both = [r for r in data if r["budget"] == 1000]
    solved_by = {a: {r["name"] for r in both if r["arm"] == a and r["solved"]} for a in ARMS}
    base, rec = solved_by["baseline (length)"], solved_by["recommended"]
    lines += ["", "## Does it ever lose?", "",
              f"At budget 1000 the recommended ordering solves **{len(rec - base)}** presentations "
              f"the baseline does not, and the baseline solves **{len(base - rec)}** it does not. "
              + ("A strict superset — it never trades a solve away."
                 if not (base - rec) else
                 f"So the gain is not free: {sorted(base - rec)[:6]} are lost."), ""]

    with open(os.path.join(LOGS, "EXP26_clean_holdout.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
