# Rank-3 and rank-n brute force

Add a generator `z` and the relator `Z.w` to a two-generator presentation, for every freely reduced word `w`,
and search each stabilised start with the ordinary best-first search. Ported from `origin/rank3/brute-force-baseline`
(commit `068ea77d`, `experiments/stable_ac/rank3/`). It answers one question: does knowing the right word for each
presentation make greedy cheaper? The sweep is `acx/ngen/sweep.py`; the search is `acx.search.search`, unchanged.

## What is searched

- **Start.** `<x, y, z | r1, r2, Z.w>` for `w` in `x, y` (rank 3); `<x, y, z1, z2 | r1, r2, Z1.w1, Z2.w2>` for every
  multiset of two words (rank 4); three words for rank 5. `extra` = 1, 2, 3 in `[rankn]`.
- **Words.** All freely reduced words of length `min_len..max_len` over `x, y, X, Y`, one of each pair `{w, w^-1}`:
  `2 * 3**(n-1)` of length `n`, fixed depth-first order (`reduced_words`). `inverse = true` searches `w^-1` instead
  (the same start up to renaming `z`; only heap ties can differ).
- **Control and null stabilisation.** Per row the 2-generator search and the start with empty words (`Z1, .., Zk`) run
  too and must agree on (solved, pops, path length); otherwise the row is refused.
- **Priority** is LENGTH. `S20_MK2` is defined for two generators only, so the sweep refuses it. The cap is the
  config's (`cap = 24`, an int, or `"none"`); it never decides a pop silently, because the cap counters
  (`acx.core.capcount`, [METHODS](METHODS.md)) record every dropped child and whether it would have been popped.
- **What a solve means.** A solved stabilised start certifies *stable* AC triviality of the row only after a lift
  that is not part of this port. The sweep reports "solved from the stabilised start"; it never writes an `ac_path` or
  a `stable_cert`.

## Run

```
python run.py --config configs/rank3_bf.toml                  # MS640, words of length 1-4, budget 1,000, cap 24
python run.py --config configs/rank3_bf.toml --rows 0:40      # a smoke, seconds
python run.py --config configs/rank4_bf.toml --rows 0:640:40  # a rank-4 slice (a full run is ~2 core-hours)
python -m acx.ngen.sweep --config configs/rank5_bf.toml --verify 100   # the same config without run.py
```

`[search]` is a `SearchConfig` (priority `length`, `budget <= 65535`, `1 + max_len <= cap`); `[rankn]` holds `extra`,
`min_len`, `max_len`, `inverse`, `sample`. Unknown keys and invalid values are errors at load.

Results go to `results/<name>/`: `config.json`, `rows/<id>.npz` (one atomic file per row, so a killed run resumes;
a file from another config is an error, never merged), `summary.json`, `summary.md`. A row file holds, per start,
`nodes`, `path_len` (-1 unsolved), `min_total` and the cap counters, plus the control and null records and a
deterministic sample of solved paths. **The row files are large; keep them out of git** (`results/*/rows/`).

`acx.ngen.sweep.verify(dir, recheck=N)` (also `--verify N`) checks: control equals null stabilisation (and their
cap counters, scores shifted by `extra`), shapes and ranges, cap-counter consistency, every stored path through
`acx.verify.replay`, and `N` random cells re-run on the other backend. Cost: about 30 ms per search (rank 3, budget
1,000); lengths 1-3 over MS640 (16,640 searches) take 3 minutes on this machine's free CPUs, lengths 1-4 about 8.
Length 10 (37.8 M searches) is a cluster job.

## Reproduction against the baseline's stored results

Budget 1,000, cap 24, MS640, fast backend; every cell compared with `results/stable_ac/rank3_bf/*.npz` on the branch
(`nodes`, `path_len`, `min_total`, `cap_dropped`, and the control's solved/pops/path length):

| slice | cells | solved | mismatches |
|---|---|---|---|
| control, 640 rows (also equal to the null stabilisation) | 640 | 554 | 0 |
| rank 3, lengths 1-3 | 16,640 | 11,438 | 0 |
| rank 3, length 4 | 34,560 | 23,696 | 0 |
| rank 3, lengths 1-2, `inverse = true` | 5,120 | - | 0 |
| rank 4, 16 rows (`--rows 7:640:40`) | 5,616 | 2,899 | 0 |
| rank 5, 16 rows (`--rows 0:640:40`) | 1,920 | 1,150 | 0 |

The summary tables agree too (solved by some word up to length 1/2/3/4: 403 / 472 / 516 / 540; a random word solves
60.1% / 68.4% / 69.8% / 68.6% of its starts; lost 151 / 82 / 38 / 18). The cap dropped a child in 4 of the 16,640 searches
of lengths 1-3 (the same 4 cells as the baseline, the same smallest dropped total) and could bind in none, as in the
baseline. The baseline's `cap_first_bind` is the conservative total-length test; acx's counters are exact
(strict full heap key, first-drop keys), so a baseline bind may be a tie that acx clears, and a baseline null
implies an acx null.

Published numbers of the baseline (MS640, budget 1,000, cap 24; `benchmark/rank3_bf/` holds its tables): control 554;
the oracle over lengths 1-10 solves 578 (24 gained, 0 lost); the best single word `yXYYYxyyy` solves 528; rank 4: 506
solved by some start, rank 5: 416; the cap dropped a child in 45,315 of 4,960,112 counted searches and could bind in none.

## Differences from the baseline

- The search is `acx.search` (spec and fast), not `solvern` / `solvern_fast`: the same canonical form, tie-break, move
  order and cap rule, pop for pop with cyclic reduction on. With `cyclic = false` acx re-reduces the untouched relators
  at every pop (the published baseline's behaviour), `solvern` kept them as stored; the sweep ships `cyclic = true`.
- Not ported: the 2,187-word block shards, the relator-subword arm (needs the change-of-variables word family), and
  the shortlex, cross-validation and class-view analyses.
