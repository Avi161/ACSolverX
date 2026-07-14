# [2026-07-13] "The search has converged" — the ceiling was never tested [TRAP]

## What happened

`EQUIVALENCE_FINDING.md` shipped the claim:

> **More budget is not the answer.** 30 → 250 nodes per source, with the cap raised from 26 to 28,
> bought exactly **one** further merge. The search has converged: the remaining classes are far
> apart in the ACA graph, not merely out of reach.

It was wrong, and the same document contained the refutation. Its own follow-up list named
"a bigger `Aut`-minimal length cap" as **the measured limiter** — while the bullet above declared
the search converged. Both could not be true.

Re-running the ACA search over the 126 class reps at `max_total = 34` found a new merge in 28
minutes on one core:

```
21_3  ==  21_29        both singletons in the 126   ->  125 classes
```

The two roots meet at Aut-minimal total length **30**. The production sweep ran at `max_total = 28`.
**The merge was not out of budget — it was outside the search space.** No budget at cap 28 could
ever have reached it.

## Why the convergence study missed it

Five configurations were run and all agreed, which is why the number was believed. Look at what
they varied:

| varied | values tried |
|---|---|
| move set | `seam`, `full` |
| seed sources | bare, `+ms` (550 bridges), `+jsonl` (783 recorded states) |
| budget | 30, 60, 120, 250 /source |
| **`max_total` ceiling** | **26, 28. And nothing else, ever.** |

Four knobs, five runs, unanimous agreement — and the one knob that mattered was held nearly fixed.
**Agreement across configurations is only evidence of convergence in the dimensions those
configurations actually span.** Five runs that all share a blind spot agree *because* of the blind
spot, not despite it.

## The rules

- **Before reporting a search converged, list the knobs and state which ones the evidence
  actually varied.** "Five configs agree" means nothing about a parameter all five held fixed.
  If a knob was not swept, the honest claim is "converged in budget", not "converged".
- **Budget and ceiling are different knobs and they fail differently.** More budget = more pops of
  the *same* space, so it saturates and its saturation is real evidence. A higher ceiling = a
  *bigger space*, so it can expose states that were previously unreachable **at any budget**.
  Saturating the first tells you nothing about the second.
- **A doc that contradicts itself is telling you where the bug is.** "The cap is the measured
  limiter" and "the search has converged" sat ~300 lines apart in one file for weeks. Grep your own
  conclusions against your own follow-up list.

## And a second-order trap: a higher ceiling is not monotonically better

Cap 40 *contains* the length-30 meeting point and **still missed the merge**. A wider cap lets far
more children past the phase-1 prefilter, so it managed 3,703 pops against cap 34's 5,123 in the
same wall clock. Raising a ceiling costs pops/second; the useful cap is the one that just barely
contains the target.

**Tune the ceiling, do not maximise it.** The next rung to try is the *smallest* one that still
contains the known merge — `seam` at `max_total = 30`.

## What did NOT work (worth as much, so nobody re-runs them)

Seven other arms ran alongside cap-34, all at 1,000 nodes/source for 28 minutes, all returning
exactly **126**:

- **Level-set expansion** (`search/levelset.py`). `aut_search` documents its own single
  incompleteness — it expands ONE representative per Aut-class, and `children(φ(P)) ⊄ φ(children(P))`
  for length-changing φ, so it sees a *subset* of each class's true out-edges. Closing that hole
  (expanding every member of the minimal level set) fired on 203 of 2,383 nodes and found **zero**
  additional merges. The incompleteness is real and empirically inert.
- The **`full` move set** at cap 28 and 32 — confirming the original finding that it buys nothing.
- **`+jsonl`** (the 783 recorded 1M-node states) at cap 30.
- **Production config at 4× budget** (`seam`, cap 28, 1,000/source) — 126, as the convergence study
  correctly predicted. Budget really had saturated. That was never the issue.

## Evidence

- `results/equivalence_classes/EQUIVALENCE_FINDING.md` §3b
- `results/equivalence_classes/probe/probe_seam_34_1000.json` — the merge and both path certificates
- `experiments/equivalence_classes/verify/verify_new_merge.py` — replays them by pure substitution
- `experiments/equivalence_classes/pipeline/run_probe.py` — reproduces every arm
