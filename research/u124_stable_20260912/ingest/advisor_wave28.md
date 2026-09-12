# Wave 28 stable-AC legality audit (C44)

Source: ac-advisor `bc-b1336162-debb-5b48-b631-e4102487d149`, 2026-09-12.
Coordinator applied the REVISE wording below. The 5,521,175 unique d2
states were not re-enumerated.

## BLOCKERS

None.

## WARNINGS / REVISE items applied

- Bounded negative only; not a counterexample; not full depth-3.
- Depth counts AC2 macro-steps, not elementary moves.
- μ-floor rows stay `mu_floor_best_relative`; not ordinary archival
  certificates.
- C26–C42 ncl product-word “min 11” is not a pair total.
- C44 starts from `aca_111` BEST total 24 and finds no drop. The
  pathless 10M INITIAL-table observed total 23 is neither a C44 state
  nor a certified reduction.
- `aca_115`: 12 equal-total depth-2 states, not a claim that each
  spelling equals the input pair.
- 116,608 are row-local unique corridor children.
- Allowed scope: no listed BEST input or C44-enumerated state reached
  cyclic total ≤ 12.
- `independent_checker=false`. Identity checks are a new file.
- C43 is the leftover aca_43 ncl scanner, not this census.

## ALLOWED CLAIMS

- Complete bounded negative for the specified row-local equal-total
  depth-2 corridor on the listed BEST inputs.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
