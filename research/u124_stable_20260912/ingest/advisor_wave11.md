# Wave 11 stable-AC legality audit (C26)

Source: ac-advisor `bc-a2ce8114-fc6d-5421-a212-b2e73f257e99`, 2026-09-12.
Coordinator applied the REVISE below. The eight-cell window was not
re-enumerated; summary fields, notes, and planted controls were
refreshed with `--annotate-existing`.

## BLOCKERS (as filed)

1. “Min length 7” overstated the Cartesian census.
   Applied: observed minima 11 and 13; every enumerated Cartesian
   product has length at least 11. MITM cells still report no min_len.
2. All-cell and MITM-only cardinalities must stay distinct.
   Applied: `n_typed_tuples_total` = 33,815,630,588;
   `n_cartesian_products_enumerated` = 38,940;
   `n_typed_tuples_mitm` = 33,815,591,648 (search space, not products).
3. Controls did not exercise arity 5/6 or recursive 3+3.
   Applied: same-code planted hits/misses for arity 4–6, recursive
   `L=3,R=3`, a cancellation-heavy empty 5-fold, and Cartesian/MITM
   agreement on a tiny pool. Still `independent_checker=false`.

## WARNINGS

- JSON is produced by the cited program, not a second implementation.
- MITM typed sizes are not product enumerations.
- `L1≥8` and `k=L1+2t` remain open.
- Not a U124 solve.

## ALLOWED CLAIMS

- C26.1: exact-L1 type pattern `|a|` copies of `R^{sign(a)}` and one
  `S^{-1}` on every `Q'_{n,δ}`.
- C26.2: no prefix/one-letter exact-L1 hit on `{y, Xyx, xyX}` in the
  `2≤L1≤7` window.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
