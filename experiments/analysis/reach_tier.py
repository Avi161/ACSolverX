"""Freeze the stable-AC **reach** tier: 1 / 2 / 4 / 6 genuinely-unsolved problems.

The ladder (``benchmark_subsets.py``) asks *is the technique more efficient?* and
scores it with speedup ratios. It cannot ask the question the project exists to
answer, because every presentation in it is already solved. This tier asks *does
the technique get further?* and pairs 1:10 with the ladder -- subset_10 -> reach_1,
subset_60 -> reach_6.

Two metrics, neither a speedup:

* ``solved`` -- binary. Almost always 0, and worth the entire project if it flips.
* ``progress = min_relator_length - (|r1| + |r2|)`` -- how far **below its own starting
  length** the search ever got. Negative is progress; 0 means it never improved on the
  presentation it was handed.

``min_relator_length`` on its own was the first choice and it is **degenerate**: at a
1,000,000-node budget, **247 of the 261 sit exactly at their starting length**, so the
number mostly just re-reports how long the presentation was to begin with. Subtracting
the start is what turns it into a measurement.

The bar this sets is brutally clean. **Baseline greedy scores 0 on 247/261, and 0 on
AK(3)** -- whose ``min_relator_length`` is 13 (= its starting length) at a 1,000-node
budget and still 13 at 1,000,000. A technique that reaches ``progress < 0`` has done
something a million nodes of length-guided greedy provably cannot: gone *down* the far
side of the first hump.

Read ``progress`` carefully, though. Only 7 of the 126 classes have any, and they are
the **longest** presentations (25_17, 25_2, 25_3, 25_31, ...). Progress correlates with
having *slack to shed*, not with being close to a solution -- AK(3), at total length 13,
is already minimal and has nothing to give back. So it ranks *effort*, never *promise*.

No baseline run is needed to compare against this tier. Unsolved at 1M implies unsolved
at any smaller budget (a budget-B search is exactly the first B pops of a longer one),
and ``min_relator_length`` can only fall as the budget grows -- so the 1M numbers are a
*conservative* bar for a technique run at 50k. A 50k baseline would only lower it.

**The pool is the 126 ACA classes, not the 261 rows.** ``EQUIVALENCE_FINDING.md``
establishes that the 261 "unsolved classes" are at most **126 distinct problems** up
to ACA-equivalence (AC moves *together with* change of variables) -- 52% of that 1M
sweep was duplicated compute. Every merge ships a machine-checked certificate
(``verify_proofs.py``). Sampling the raw 261 would run the same problem twice; the
largest class has 8 members.

This dedup is the *opposite* call from the ladder's, and for the opposite reason.
On the ladder two Aut-equivalent presentations are two genuinely different *search
instances* (cost is not an orbit invariant -- 623 vs 636 differ 3.6x), so both are
kept. Here the unit counted is *problems cracked*: two coordinate systems on one
problem is one crack, so one representative is kept.

Which representative? Both candidates are recorded, because they disagree and the
disagreement is itself worth measuring:

* ``representative`` -- the class's Aut-minimal form from the sweep. EQUIVALENCE_FINDING
  argues this is strictly better-conditioned, since greedy is length-guided. Often
  shorter than any of the 261 rows, and often *not one of them*.
* ``best_known_member`` -- the member whose 1M run reached the lowest
  ``min_relator_length``, i.e. the coordinates from which greedy empirically got
  closest to trivial.

Nobody has run the Aut-minimal reps, so that claim is untested. Running both is a
free A/B and answers it.

**AK(3) is slot 0 at every size.** Its stable AC-triviality is **open** -- nobody has
established it (the Lisitsa/MMS02 chain does not stand; Shehper et al. found a
misprint in MMS02 p.10 that undermines it). Trivialising it at ``n_gen = 3`` is not a
benchmark number, it is the result.

**AK(3) is already in the 261, and it is alone.** MS rep ``13_1`` is Aut(F2)-equivalent
to AK(3), and its ACA class (id 113) is a **singleton** -- no other unsolved MS
presentation is the same problem. So AK(3)'s class is excluded from the sampled pool
(AK(3) represents it) and ``13_1`` is recorded as ``ak3_ms_coordinates``: the same
problem in a second coordinate system, a free A/B test for any CoV technique. At 1M
its ``min_relator_length`` is **13 -- equal to its starting length**. A million nodes
and the search never went *below* where it began. That is the two-hump wall.

Writes ``results/benchmark/reach/``::

    .venv/bin/python3 -m experiments.analysis.reach_tier
"""

import csv
import json
import os

from experiments.analysis.whitehead import canon_pair, canonical_form
from experiments.greedy_tests.fixtures.presentations import ak

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# the 126-class config: seam move set, Aut-minimal length cap 28, 250 pops/source
CLASSES_CSV = os.path.join(REPO, "results", "equivalence_classes", "sweep",
                           "classes_sweep_seam_28_250.csv")
UNSOLVED_JSONL = os.path.join(REPO, "results", "greedy_baseline",
                              "greedy_1000000_261_mrl48_cyc_all_07_09_26.jsonl")
NAMES_CSV = os.path.join(REPO, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
OUT_DIR = os.path.join(REPO, "results", "benchmark", "reach")

SIZES = (1, 2, 4, 6)          # pairs 1:10 with subsets 10/20/40/60
TRUTH_BUDGET = 1_000_000
COMPARE_BUDGET = 50_000


def _spread(items, k):
    """k items evenly spaced over the sorted range, endpoints included."""
    if len(items) <= k:
        return items
    if k == 1:
        return [items[(len(items) - 1) // 2]]
    idxs = []
    for i in range(k):
        j = round(i * (len(items) - 1) / (k - 1))
        while j in idxs:
            j += 1
        idxs.append(j)
    return [items[j] for j in sorted(idxs)]


def main():
    classes = list(csv.DictReader(open(CLASSES_CSV)))
    rows = [json.loads(l) for l in open(UNSOLVED_JSONL) if l.strip()]
    names = [r["name"] for r in csv.DictReader(open(NAMES_CSV))]
    if len(classes) != 126:
        raise SystemExit(f"expected the 126-class table, found {len(classes)} rows")
    if len(rows) != 261 or len(names) != 261:
        raise SystemExit(f"expected 261/261, got {len(rows)}/{len(names)}")
    if any(r["solved"] for r in rows):
        raise SystemExit("a row in ms_reps_unsolved is marked solved; it does not belong here")

    by_name = dict(zip(names, rows))
    covered = [m for c in classes for m in c["members"].split()]
    if sorted(covered) != sorted(names):
        raise SystemExit("the 126 classes do not partition the 261 exactly")

    ak3_r1, ak3_r2 = ak(3).to_strs()
    ak3_cf, _, _ = canonical_form(canon_pair(ak3_r1, ak3_r2))

    def progress(m):
        """How far below its OWN starting length the 1M search ever got. 0 = never."""
        r = by_name[m]
        return r["min_relator_length"] - (len(r["r1"]) + len(r["r2"]))

    def enrich(c):
        members = c["members"].split()
        # best coordinates = furthest below their own start, then closest to trivial
        best = min(members, key=lambda m: (progress(m), by_name[m]["min_relator_length"], m))
        rep_r1, rep_r2 = c["representative"].split(",")
        b = by_name[best]
        return {
            "aca_class_id": int(c["class_id"]),
            "n_members": int(c["n_members"]),
            "members": members,
            # the class's Aut-minimal form -- EQUIVALENCE_FINDING says run THIS
            "rep_r1": rep_r1,
            "rep_r2": rep_r2,
            "rep_total_length": int(c["rep_len"]),
            "rep_is_one_of_the_261": any(
                by_name[m]["r1"] == rep_r1 and by_name[m]["r2"] == rep_r2 for m in members),
            # the coordinates greedy empirically got furthest with
            "best_known_member": best,
            "best_known_r1": b["r1"],
            "best_known_r2": b["r2"],
            "baseline_start_length": len(b["r1"]) + len(b["r2"]),
            "baseline_min_relator_length": b["min_relator_length"],
            "baseline_progress": progress(best),
            "min_relator_at_1M": b["min_relator"],
            "baseline_solved": False,
            "abs_det": int(c["abs_det"]),
        }

    enriched = [enrich(c) for c in classes]
    ak3_cls = next(c for c in enriched if "13_1" in c["members"])

    # Stratify by min_relator_length, but tie-break on baseline_progress. 25_17 (progress
    # -3) and 22_11 (progress 0) sit on the same rung; take the one greedy actually moved.
    pool = sorted((c for c in enriched if c is not ak3_cls),
                  key=lambda c: (c["baseline_min_relator_length"], c["baseline_progress"],
                                 c["aca_class_id"]))

    # AK(3) itself has no run at any budget, but its bar is nailed down anyway: it is
    # Aut-equivalent to 13_1, whose 1M run reached min_relator_length 13 -- its own
    # starting length. AK(3) run locally at the 1,000-node cap reaches 13 too, in all
    # three of its coordinate systems. Budget-invariant across three orders of magnitude.
    ak3_row = {
        "slot": 0,
        "source": "AK(3)",
        "name": "AK(3)",
        "r1": ak3_r1,
        "r2": ak3_r2,
        "total_length": len(ak3_r1) + len(ak3_r2),
        "aca_class_id": ak3_cls["aca_class_id"],
        "n_members": ak3_cls["n_members"],
        "baseline_start_length": len(ak3_r1) + len(ak3_r2),
        "baseline_min_relator_length": ak3_cls["baseline_min_relator_length"],
        "baseline_progress": ak3_cls["baseline_progress"],
        "baseline_solved": False,
        "bar_to_beat": f"min_relator_length < {ak3_cls['baseline_min_relator_length']}",
        "aut_min_rep_r1": ak3_cls["rep_r1"],
        "aut_min_rep_r2": ak3_cls["rep_r2"],
        "aut_min_rep_total_length": ak3_cls["rep_total_length"],
        "note": ("stable AC-triviality is OPEN; a solve at n_gen=3 is THE RESULT, not a "
                 "metric. Baseline reached min_relator_length 13 = its start length, at "
                 "1,000 nodes AND at 1,000,000. Zero progress either way."),
    }

    def row(c, slot):
        return {
            "slot": slot,
            "source": "ms_reps_unsolved / ACA class",
            "name": c["best_known_member"],
            "r1": c["best_known_r1"],
            "r2": c["best_known_r2"],
            "total_length": len(c["best_known_r1"]) + len(c["best_known_r2"]),
            "aca_class_id": c["aca_class_id"],
            "n_members": c["n_members"],
            "baseline_start_length": c["baseline_start_length"],
            "baseline_min_relator_length": c["baseline_min_relator_length"],
            "baseline_progress": c["baseline_progress"],
            "baseline_solved": False,
            "bar_to_beat": f"min_relator_length < {c['baseline_min_relator_length']}",
            "members": " ".join(c["members"]),
            "aut_min_rep_r1": c["rep_r1"],
            "aut_min_rep_r2": c["rep_r2"],
            "aut_min_rep_total_length": c["rep_total_length"],
            "aut_min_rep_is_one_of_the_261": c["rep_is_one_of_the_261"],
        }

    os.makedirs(OUT_DIR, exist_ok=True)
    dup = sum(c["n_members"] for c in enriched) - len(enriched)
    print(f"pool: {len(classes)} ACA classes over the 261 rows "
          f"({dup} rows are duplicate problems -- EQUIVALENCE_FINDING.md)")
    print(f"AK(3) -> ACA class {ak3_cls['aca_class_id']} "
          f"(n_members={ak3_cls['n_members']}: {' '.join(ak3_cls['members'])}) "
          f"-- a SINGLETON: no other unsolved MS presentation is the same problem")
    movers = [c for c in enriched if c["baseline_progress"] < 0]
    print(f"sampled pool after removing it: {len(pool)} classes, "
          f"min_relator_length {pool[0]['baseline_min_relator_length']}"
          f"-{pool[-1]['baseline_min_relator_length']}")
    print(f"baseline progress < 0 (got below its own start) in only "
          f"{len(movers)}/{len(enriched)} classes -- and they are the LONGEST "
          f"presentations; progress ranks slack, not promise\n")

    def promote(chosen):
        """At each rung, prefer the class greedy actually MOVED on.

        ``_spread`` picks by index, so it can land mid-way through a run of classes that
        share a ``min_relator_length`` and miss the one with progress < 0 sitting at the
        front of it. Progress-makers are 7 of 126, so on a 5-slot spread that is what
        happens by default. Swapping each pick for the best-progress class *at its own
        rung* keeps the stratification exactly and costs nothing.
        """
        out, taken = [], set()
        for c in chosen:
            rung = [d for d in pool
                    if d["baseline_min_relator_length"] == c["baseline_min_relator_length"]
                    and d["aca_class_id"] not in taken]
            best = min(rung, key=lambda d: (d["baseline_progress"], d["aca_class_id"]))
            taken.add(best["aca_class_id"])
            out.append(best)
        return out

    for size in SIZES:
        picks = [ak3_row] + [row(c, i + 1)
                             for i, c in enumerate(promote(_spread(pool, size - 1)))]
        doc = {
            "size": len(picks),
            "pairs_with_subset": size * 10,
            "pool": "the 126 ACA classes (results/equivalence_classes/, machine-checked)",
            "truth_budget": TRUTH_BUDGET,
            "comparison_budget": COMPARE_BUDGET,
            "question": "does the technique get FURTHER? (not: is it faster)",
            "metrics": [
                "solved (binary)",
                "progress = min_relator_length - starting total length  (< 0 = went below "
                "where it started; 0 = never improved on what it was handed)",
            ],
            "the_bar": ("baseline greedy scores progress = 0 on 247 of the 261 -- and on "
                        "AK(3) -- at a 1,000,000-node budget. Any technique reaching "
                        "progress < 0 did something a million nodes of length-guided greedy "
                        "provably cannot."),
            "why_not_min_relator_length_alone": ("it is degenerate: 247/261 sit exactly at "
                                                 "their starting length, so the raw number "
                                                 "mostly re-reports how long the presentation "
                                                 "was to begin with. Subtract the start."),
            "read_progress_carefully": ("only 7 of the 126 classes have progress < 0, and they "
                                        "are the LONGEST presentations (25_17, 25_2, 25_3, "
                                        "25_31...). Progress correlates with having slack to "
                                        "shed, NOT with being close to a solution -- AK(3), at "
                                        "total length 13, is already minimal and has nothing to "
                                        "give back. It ranks effort, never promise."),
            "no_baseline_run_needed": ("unsolved at 1M implies unsolved at any smaller budget "
                                       "(a budget-B search is exactly the first B pops of a "
                                       "longer one), and min_relator_length can only fall as "
                                       "the budget grows. So these 1M numbers are a "
                                       "CONSERVATIVE bar for a technique run at 50k -- a 50k "
                                       "baseline would only lower it."),
            "no_speedup_ratio": ("every row is unsolved at 1M, so there is no baseline "
                                 "path_length and no speedup ratio. These rows must never "
                                 "enter the ladder's median/IQR."),
            "selection": ("AK(3) at slot 0 always. Remainder: the 126 ACA classes minus "
                          "AK(3)'s own class (113, a singleton = 13_1), spread evenly over "
                          "min_relator_length @1M, endpoints included, tie-broken on best "
                          "baseline_progress. One row per PROBLEM, not per presentation -- "
                          "the 261 rows are only 126 problems."),
            "two_coordinate_choices": ("Each row carries BOTH the class's Aut-minimal "
                                       "representative (aut_min_rep_*, which "
                                       "EQUIVALENCE_FINDING argues is better-conditioned "
                                       "because greedy is length-guided -- untested) and the "
                                       "best_known_member (the coordinates from which the 1M "
                                       "sweep actually got closest to trivial). Run both: it "
                                       "is a free A/B on that claim."),
            "ak3_ms_coordinates": {
                "name": "13_1",
                "r1": by_name["13_1"]["r1"],
                "r2": by_name["13_1"]["r2"],
                "total_length": len(by_name["13_1"]["r1"]) + len(by_name["13_1"]["r2"]),
                "baseline_min_relator_length": by_name["13_1"]["min_relator_length"],
                "baseline_progress": progress("13_1"),
                "aca_class_id": ak3_cls["aca_class_id"],
                "aut_min_rep": f'{ak3_cls["rep_r1"]},{ak3_cls["rep_r2"]}',
                "note": ("Aut(F2)-equivalent to AK(3): the same problem in Miller-Schupp "
                         "coordinates. NOT a separate problem -- run it alongside AK(3) as a "
                         "free A/B on whether a CoV technique reaches the same place from "
                         "different coordinates. At 1M its min_relator_length is 13, equal to "
                         "its starting length: the search never went BELOW where it began."),
            },
            "tier": picks,
        }
        with open(os.path.join(OUT_DIR, f"reach_tier_{size}.json"), "w") as f:
            json.dump(doc, f, indent=2)
        cols = ["slot", "source", "name", "r1", "r2", "total_length", "aca_class_id",
                "n_members", "baseline_start_length", "baseline_min_relator_length",
                "baseline_progress", "baseline_solved", "bar_to_beat",
                "aut_min_rep_r1", "aut_min_rep_r2", "aut_min_rep_total_length"]
        with open(os.path.join(OUT_DIR, f"reach_tier_{size}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(picks)

        d = [(p["name"], p["baseline_min_relator_length"], p["baseline_progress"])
             for p in picks[1:]]
        print(f"reach_{size} (with subset_{size * 10:<2}) -> AK(3) + {len(picks) - 1}: "
              + ("  ".join(f"{n}(mrl={m}, prog={p:+d})" for n, m, p in d) or "--"))

    print(f"\nAK(3)         r1={ak3_r1:<9} r2={ak3_r2:<9} |total|={len(ak3_r1)+len(ak3_r2)}")
    print(f"= MS 13_1     r1={by_name['13_1']['r1']:<9} r2={by_name['13_1']['r2']:<9} "
          f"|total|=13  min_relator_length@1M=13 (never went below its start)")
    print(f"= ACA rep 113 r1={ak3_cls['rep_r1']:<9} r2={ak3_cls['rep_r2']:<9} "
          f"|total|={ak3_cls['rep_total_length']}")
    print(f"\n-> {os.path.relpath(OUT_DIR, REPO)}/  ({len(SIZES)} json + {len(SIZES)} csv)")


if __name__ == "__main__":
    main()
