# The 1190 Miller–Schupp presentations as two tables

Built by `experiments/equivalence_classes/pipeline/make_ms1190_tables.py`. Regenerate with `python3 -m experiments.equivalence_classes.pipeline.make_ms1190_tables` — it is pure and deterministic, no search, ~1 s.

| file | rows | what it is |
|---|---|---|
| `solved_640_aut_orbits.csv` | 113 | the 640 trivial cells, one row per distinct **Aut(F₂) orbit** |
| `unsolved_124_aca_classes.csv` | 124 | the 550 unsolved cells, one row per **ACA class** |
| `ms1190_two_tables.csv` | 125 | both of the above in one sheet, side by side with a blank gutter column |

```
1190 cells  =  640 trivial  +  550 unsolved
                    |                |
              113 Aut orbits   261 rep names → 124 ACA classes
```

## Where the 1190 come from

`MS(n, w) = ⟨x, y | x⁻¹yⁿxy^−(n+1), x⁻¹w⟩` over the 170 zero-x-exponent words down the side of `ms_solved_grid.csv` and `n ∈ 1..7`. Those 170 × 7 canonical pairs are exactly the 1190 of `data/1190MS.txt` (set equality, established in `phase0_provenance.py`). The grid marks each cell `trivial` or gives it a rep name; that split is 640 / 550, and it is what the two tables partition. A cell is labelled `w@n` throughout.

## Table A — solved (640 cells → 113 rows)

Keyed by the **Aut(F₂)-minimal state**: peak-reduce to the orbit's minimal total length, then take the lex-min of the minimal level set (`lib/autcanon.aut_canon`). That is Whitehead's *complete* invariant of the orbit, so two cells share a row **iff** they are genuinely change-of-variables equivalent — the dedup drops nothing real.

| column | meaning |
|---|---|
| `aut_id` | `sol_000…sol_112`, ordered by orbit size descending |
| `rep_r1`, `rep_r2`, `rep_len` | the Aut-minimal representative and its total length |
| `n_cells` | how many of the 640 collapse here |
| `ms_r1`, `ms_r2` | the shortest actual MS presentation in the orbit (a concrete witness) |
| `cells` | every member, as `w@n` |

**640 → 113 is 5.7× redundancy, and there are no singletons** — the smallest orbit has 2 members, the largest 16. Orbit sizes are 2 (×56), 6 (×27), 10 (×14), 14 (×15), 16 (×1).

## Table B — unsolved (550 cells → 261 names → 124 rows)

Straight from `data/ms_unsolved_reps/aca_124.csv`, with the Aut columns computed the same way so the two sides are read on one ruler. `n_reps` counts the 261-rep names in the class, `n_cells` the underlying MS cells.

**All 124 ACA representatives are already Aut-minimal exactly as written** (124/124) — so `rep_r1`/`rep_r2` reproduce `r1`/`r2` here. The columns are kept anyway: they are what makes the two tables joinable, and the equality is a fact about the upstream reps rather than a formatting accident.

## What the two counts do and do not mean

The tables are quotiented by **different relations**, and the counts are not comparable to each other:

- Table A is quotiented by **Aut(F₂)** only — exact, decidable, and a wall.
- Table B is quotiented by **ACA** = AC moves *together with* change of variables, which is strictly coarser. 124 is an **upper bound** on the number of distinct problems, not a proven class count.

Only the per-row `rep_r1`/`rep_r2` is a like-for-like comparison across the two sides.

Aut(F₂) is the right dedup key for Table A even though it is **not** a set of AC moves: it preserves AC-*triviality* (`P` is AC-trivial ⟺ `φ(P)` is AC-trivial — `EQUIVALENCE_FINDING.md` §0), which is exactly the property the solved/unsolved split records. It does **not** follow that a row's members are AC-equivalent to its representative, and nothing here claims that.

## Checks that ran

- Cell accounting is asserted in the builder, not eyeballed: the rows sum to exactly 640 / 261 / 550, and the grid must present as 1190 = 640 + 550 or it raises.
- Every one of the 764 `aut_canon` calls ships a witnessing φ, and `autcanon.check` re-verifies `canon_pair(φ(P)) == rep` by pure substitution before the row is written.
- **The orbit partition is confirmed by a second, independently written implementation.** `experiments/analysis/whitehead.py` computes the same invariant by the same theory without a witness, and gives the **same 113-orbit partition of the 640, element for element**. Its *rep strings* differ, because the two modules canonicalise a relator differently (`words.canon_rel("YYXyx") = YYXyx`, `whitehead.canon_rel("YYXyx") = XYxyy`, its inverse-rotation) — feeding whitehead's rep back through `aut_canon` returns autcanon's rep on **640/640**, so this is a normal-form convention and not a disagreement.
- **0 Aut reps are shared between the two tables.** This is the check that carries information: a rep on both sides would mean an "unsolved" class is Aut-equivalent to a trivialized one and therefore already solved.
