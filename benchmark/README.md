# `benchmark/` — the frozen evaluation set

Fixed row lists for scoring a search technique, so two techniques are compared on the same presentations rather than on whichever ones each happened to run.

All rows come from [`data/ms640_solved.txt`](../data/ms640_solved.txt); `pres_id` is the **line index** into that file (0-based, verified). Every row is solved by the baseline greedy at a 10⁶-node budget, so a technique that fails one has failed a solvable problem.

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
