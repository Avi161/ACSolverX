# The reference run — GS-Sub greedy on all 640

Every number in [`README.md`](README.md), [`subsets/ARMS.md`](subsets/ARMS.md) and [`../experiments/search/HEURISTICS.md`](../experiments/search/HEURISTICS.md) is scored against one run. This is that run.

| | |
|---|---|
| solver | `greedy_search` — [`experiments/search/greedy_baseline.py`](../experiments/search/greedy_baseline.py), `config=None` |
| rows | all 640 of [`data/ms640_solved.txt`](../data/ms640_solved.txt), `pres_id` = 0-based line index |
| `node_budget` | 1,000,000 |
| `max_relator_length` | 24 |
| `cyclic_reduce` | `True` |
| per-row table | [`difficulty_bins.csv`](difficulty_bins.csv) |

**640 / 640 solved, 0 unsolved.** That is what makes the file a benchmark rather than a sample: a technique that fails a row here has failed a problem the baseline provably solves, so a miss is always the technique's and never the instance's.

## The numbers

| | |
|---|---|
| solved | 640 / 640 |
| nodes: min / median / mean / max | 3 / 11 / 4,963.0 / 574,959 |
| nodes: p25 / p75 / p90 / p99 | 6 / 125 / 2,023 / 78,774 |
| path: min / median / mean / max | 2 / 9 / 36.77 / 708 |
| total nodes over all 640 | 3,176,297 |

**Read the median, not the mean.** At 4,963 the mean sits above the 75th percentile — 451× the median — because six rows carry it. Half of all 640 presentations are solved in **11 nodes or fewer**; the mean describes none of them. Every mean in this repository's tables has the same defect and the same fix.

## Where the cost is

Difficulty is `log10(nodes_explored)`, cut into ten equal-width bins — each **3.37×** the one below. This is the table the subsets stratify over.

| bin | nodes | rows | share |
|---|---|---|---|
| 0 | 3 – 10 | 317 | 49.5% |
| 1 | 10 – 34 | 89 | 13.9% |
| 2 | 34 – 115 | 63 | 9.8% |
| 3 | 115 – 389 | 60 | 9.4% |
| 4 | 389 – 1,313 | 31 | 4.8% |
| 5 | 1,313 – 4,432 | 26 | 4.1% |
| 6 | 4,432 – 14,958 | 28 | 4.4% |
| 7 | 14,958 – 50,482 | 14 | 2.2% |
| 8 | 50,482 – 170,367 | 6 | 0.9% |
| 9 | 170,367 – 574,959 | 6 | 0.9% |

The distribution is the **Two-Hump** shape the paper is named for, measured: bins 0–3 hold 529 of 640 rows and **0.69%** of all nodes spent, while the top six rows alone hold **66.8%** and the top twenty hold **86.2%**. A technique evaluated on random rows is evaluated on bin 0 and reports almost nothing — which is why [`subsets/`](subsets/) samples equally *per bin* instead.

At a 50,000-node budget the baseline still takes **628 / 640**; the whole benchmark's difficulty lives in the twelve rows that need more. The `*_at_50k` columns of [`difficulty_bins.csv`](difficulty_bins.csv) carry that cheaper run for comparison.

## Cost and certificate length are different quantities

They are not proportional, and past bin 7 they stop agreeing on the ordering entirely:

| `pres_id` | nodes | path | |
|---|---|---|---|
| 635 | 574,959 | 80 | most expensive to find, near-shortest certificate in the tail |
| 634 | 574,348 | 80 | |
| 623 | 59,710 | **708** | 9.6× cheaper to find, 8.9× longer certificate |

So "hard" needs saying which way. A search ordering tuned on nodes is not thereby tuned on path length, and the two hardest presentations in the benchmark have certificates shorter than rows from bin 6.

## The expensive rows are few orbits

Two presentations in the same `Aut(F₂)` class are one problem in two coordinate systems — same orbit under change of variables, decided by the complete Whitehead invariant in [`experiments/equivalence_classes/`](../experiments/equivalence_classes/). The 640 rows fall into **113** classes, and the **twelve most expensive rows (bins 8–9) are only three of them**:

| `aut_class` | rows in MS-640 | Aut-min total | nodes | path |
|---|---|---|---|---|
| 106 | 14 — `616`–`625`, `636`–`639` | 22 | 14,415 – 272,953 | 489 – 708 |
| 108 | 2 — `634`, `635` | 23 | 574,348 – 574,959 | 80 |
| 97 | 14 — `590`–`597`, `600`, `603`–`605`, `610`, `613` | 20 | 3,340 – 61,366 | 231 – 337 |

`634` and `635` differ only by `yyxx` → `XXyy` in `r2` and share the Aut-minimal representative `XXXYYxxy | XXXXXXXYxxxxxxy`, so they are the same problem twice — yet cost 574,348 and 574,959 nodes.

**Search cost is not an orbit invariant.** Class 106 spans 14,415 to 272,953 nodes — **18.9×** across presentations that are provably the same problem. A forced duplicate in a subset is therefore still a genuinely different search instance, and an Aut class is not a unit of difficulty.

> `aut_orbit_size` in the CSV is the size of the Whitehead **minimal level set**, not the number of MS-640 rows in the class. Class 106 has `aut_orbit_size = 8` and 14 rows here. Do not read it as a member count.

## What this run does not contain

**No move sequences.** 1M-node runs use `high_speedup=True`, the memory-lean solver, which reports `solved` / `nodes_explored` / `path_length` and the min/max relator stats but returns `path` and `path_moves` **empty** — see the `greedy_search` docstring. `path_length` is a true length, not an estimate; only the witnessing derivation is absent.

To recover the derivation for a row, re-run that row alone with the full solver:

```python
from experiments.search.greedy_baseline import greedy_search, moves_to_states, str_to_move

r1, r2 = "YYYYYYYXyyyyyyx", "YYYXXyyx"           # pres_id 635
s = greedy_search(r1, r2, node_budget=1_000_000, max_relator_length=24)
s["path_length"], len(s["path_moves"])            # path_moves now populated

moves = [str_to_move(m) for m in s["path_moves"]]     # 'target_jsign_k1_k2' -> tuple
moves_to_states(r1, r2, moves) == s["path"]           # replays the derivation
```

`moves_to_states` takes **parsed tuples**, not the compact strings — `path_moves` stores strings, so `str_to_move` is required. Dropping it fails with `ValueError: too many values to unpack`, since a 4-character move string iterates as characters.

Budget accordingly: the tail rows are the ones whose certificates you want and also the ones the lean solver exists for.

The two solvers agree exactly on the statistics they both report. Verified on `pres_id` 0, 300 and 500 — identical `solved` / `nodes_explored` / `path_length`, with `path` and `path_moves` empty under `high_speedup=True` and replaying correctly under the full solver.

## Reproducing the table

`ms640_solved.txt` stores each presentation the way the rest of `data/` does — one flat integer list of length `2 * 24`, two zero-padded relators, `x → 1`, `y → 2`, `x⁻¹ → -1`, `y⁻¹ → -2`. The solver takes `x, X, y, Y` **strings**, so decode first:

```python
from experiments.search.greedy_baseline import greedy_search

LETTER = {1: "x", -1: "X", 2: "y", -2: "Y"}

def decode(line):
    a = eval(line); half = len(a) // 2
    return ("".join(LETTER[c] for c in a[:half] if c),
            "".join(LETTER[c] for c in a[half:] if c))

rows = [decode(l) for l in open("data/ms640_solved.txt")]     # pres_id = index
for pres_id, (r1, r2) in enumerate(rows):
    s = greedy_search(r1, r2, node_budget=1_000_000,
                      max_relator_length=24, cyclic_reduce=True,
                      high_speedup=True)
    ...   # s["solved"], s["nodes_explored"], s["path_length"]
```

`decode` reproduces the `r1` / `r2` columns of [`difficulty_bins.csv`](difficulty_bins.csv) exactly on all 640 rows.

The three settings above are load-bearing. `max_relator_length` bounds what the search will hold, so raising it changes `nodes_explored` on every row; `cyclic_reduce` changes canonicalisation and so changes the state graph itself. A table produced under different settings is a different baseline and cannot be compared row-wise with this one.

Two consistency checks back this table:

- **Against the subsets.** `difficulty_bins.csv` agrees with all four shipped subsets on every shared column (`nodes_1M`, `path_1M`, `bin`, `aut_class`, `r1`, `r2`) across their 130 rows — 0 mismatches.
- **Against a re-run.** 21 rows spanning bins 0–8, re-solved from `data/ms640_solved.txt` through the snippet above, reproduce their `nodes_explored` and `path_length` exactly — 0 mismatches, up to `pres_id` 610 at 61,366 nodes. The search is deterministic, so this is an equality check and not a tolerance.
