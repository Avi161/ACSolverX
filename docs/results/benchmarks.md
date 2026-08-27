# Benchmarks — the ladder, the baseline reference, and the aut-min tier

## The subset ladder (shipped)

`benchmark/subsets/` holds the frozen 10/20/40/60 row lists, difficulty-binned and
deduplicated by `Aut(F₂)` class via `autcanon` — the automorphism-aware benchmark that
ships on this branch. How the rows were picked, the census they sit inside, and what the
arms columns mean: [`benchmark/README.md`](../../benchmark/README.md) and
[`benchmark/subsets/ARMS.md`](../../benchmark/subsets/ARMS.md).

## The 640-row GS-Sub baseline reference

The plain greedy (`config=None`), budget 10⁶, `mrl=24`, over all of
`data/ms640_solved.txt`: **640/640 solved**. The cost distribution is the Two-Hump shape,
measured:

- nodes min/median/mean/max = **3 / 11 / 4,963 / 574,959**; p75 = 125, p90 = 2,023.
- The cheap head: bins 0–3 hold 529 of 640 rows and **0.69%** of all nodes.
- The expensive tail: the top 6 rows carry **66.8%** of total node cost; the top 20 carry
  **86.2%**.
- At a 50,000-node budget the baseline still solves **628/640** — the last 12 rows are
  where all the cost lives.
- Cost is **not an orbit invariant**: the 640 rows collapse to 113 `Aut(F₂)` classes, and
  within class 106 the node cost spans 14,415 → 272,953 — **18.9×** across provably-the-same
  problem. Cost and certificate length also disagree past bin 7 (the most expensive row,
  574,959 nodes, has an 80-move path; a 59,710-node row has a 708-move path).

The full per-row table (`benchmark/BASELINE.md` + `difficulty_bins.csv`, 641 rows) lives on
`origin/claude/summer-results-docs-scoring-u6klsb` (PR #15) — a candidate for a later
fold-in; the CSV exceeded this branch's md-only artifact rule.

## Rows are not orbits

bench60's 60 rows are **45 Aut orbits** (class 106 appears 8×; 93 and 97 3×; four more
2×). And the easy bins saturate: a two-update model scored 318/331 against a fully trained
model's 331/331 on the rows one smoke covered — so **an arm difference can only show up in
bins 7–9: 18 rows, 11 orbits**. Any bench60 headline should be read per-row *and*
per-orbit, and any near-tie read against those 18 rows.

## Tier 2: the AC19 aut-min subset (not ported — retrieval paths)

The larger automorphism benchmark: one `Aut(F₂)`-minimal representative per orbit over the
full 156,762-row `AC19_extended.txt`, built with a numba-jitted twin of
`autcanon.aut_canon` and cross-checked against the slow original. It is the basis of the
69k-row screen in [`heuristic-search.md`](heuristic-search.md) — the strongest `s20_mk2`
validation. Everything needed to regenerate it is on
`origin/claude/abelianized-exponents-verify-1i6muh`:

| what | path on that branch |
|---|---|
| the fast canonicaliser | `experiments/stable_ac/cov/ladder/autcanon_fast.py` |
| the pipeline | `experiments/equivalence_classes/pipeline/make_ac19_extended_aut_min.py` |
| its cross-check test | `tests/stable_ac/test_autcanon_fast.py` |
| the screen's results | `results/heuristic_search/ac19_autmin_screen/SUMMARY.md` |
| the hard-100k residual | `results/heuristic_search/ac19_autmin_screen/HARD_RESIDUAL_100k.md` |
| the output CSV (3.5 MB, excluded here) | `data/AC19_extended_aut_min.csv` — regenerable from `data/AC19_extended.txt`, which ships on main |
