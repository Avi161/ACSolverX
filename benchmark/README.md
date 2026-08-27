# `benchmark/` — the frozen evaluation set

Fixed row lists for scoring a search technique, so two techniques are compared on the same presentations rather than on whichever ones each happened to run.

All rows come from [`data/ms640_solved.txt`](../data/ms640_solved.txt); `pres_id` is the **line index** into that file (0-based, verified). Every row is solved by the baseline greedy at a 10⁶-node budget, so a technique that fails one has failed a solvable problem. The recommended heap ordering for searching these rows is `S20_MK2` — see [`experiments/search/HEURISTICS.md`](../experiments/search/HEURISTICS.md).

## The census these rows sit inside

Stated once here; every other mention in this repository should point at this block rather than restate it.

| step | count | what the step is |
|---|---|---|
| Miller–Schupp presentations | **1,190** | `data/1190MS.txt`, verified set-equal to the 170 × 7 grid |
| solved | **640** | `data/ms640_solved.txt` — the pool these benchmark subsets draw from |
| unsolved | **550** | 550 *distinct* canonical presentations |
| distinct rep names among them | **261** | the 550 cells carry only 261 names |
| under exact `Aut(F₂)` (Whitehead) | **168** | **exact** — no change of variables does better |
| after AC-move search modulo `Aut(F₂)` | **124** | **upper bound**; caps 30–36, unanimous across five arms |

Three things about this chain that are easy to get wrong:

- **Read 124 as *distinct problems*, never as *AC-classes*.** It is an upper bound from a bounded search, unanimous across five arms but not proven converged — not a count of equivalence classes.
- **550 → 261 is not an `Aut(F₂)` result.** Only 159 of the 550 cells are `Aut`-equivalent to the rep they are named after, and the reps average 2.74 letters shorter than their cells. That collapse came from somebody else's bounded search; the exact automorphism step is 261 → 168.
- **The 640/550 split is what makes these subsets meaningful:** every benchmark row is drawn from the 640, so a technique that fails one has failed a problem known to be solvable.

Derivation and machine-checked merges: `results/equivalence_classes/EQUIVALENCE_FINDING.md` on the research branches.

## `subsets/` — the efficiency ladder

| file | what |
|---|---|
| `benchmark_subset_{10,20,40,60}.{csv,json}` | the row lists — presentation, difficulty bin, `Aut(F₂)` class, and the baseline's cost |
| `benchmark_subset_{10,20,40,60}_arms.{csv,json}` | what each technique costs on those rows — see [`ARMS.md`](subsets/ARMS.md) |
| `subset_coverage.png` | where each ladder rung's picks land across the ten bins |
| [`ARMS.md`](subsets/ARMS.md) | the arms columns, the heuristic's formula, and what the numbers do and do not say |

## How the rows were picked

Difficulty is `log10(nodes_explored)` at the 1M budget, cut into ten equal-width bins — each bin costs **3.37×** the one below, spanning 3 nodes to ~575,000. Each subset takes an equal number per bin, so subset-60 is 6 per bin. The bin edges travel inside each `.json` (the `bins` key), so a file is readable without any other table.

Within a bin, picks first **minimise `Aut(F₂)`-equivalent pairs**: two presentations in the same class are one problem in two coordinate systems, and sampling both over-weights it. Subset-60 spans 45 distinct classes of the 640's 113; the residual duplicates are forced by bins 7–9, which do not contain enough classes. Subject to that, picks spread evenly over path length.

Search cost is **not** an orbit invariant even so — `pres_id` 623 and 636 are the same class and cost 59,710 vs 213,882 nodes — so a forced duplicate is still a genuinely different search instance.

**The four subsets are not nested** (`nested: false`). Subset-20 is not subset-10 plus ten; each is independently balanced. Never assume a result on the smaller one carries.

## Who reads them

The 20 ids in [`tests/test_greedy_heuristic.py`](../tests/test_greedy_heuristic.py) are `benchmark_subset_20.json` in file order, pinned by a test against the file.
