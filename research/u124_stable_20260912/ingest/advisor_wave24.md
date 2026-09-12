# Wave 24 stable-AC legality audit (C39)

Source: ac-advisor `bc-45ac2360-af3e-5664-9c67-42bab955ca58`, 2026-09-12.
Coordinator recorded APPROVE. The 1,563,690-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun only
  aca_45; they do not independently enumerate all six rows.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(-1,0)` is for the six listed `|p|=1` rows, not every
  companion of `D` and not `p=0`.
- Observed minimum 9 is a C39 census fact, not a length theorem and
  not a comparison with C38/C29/C33.
- Disjointness is of donor/row presentation pairs, not companion words.
- Equal typed sizes to some C38 rows do not identify those censuses.
- Not the last unused listed donor. Exact-L1 `x` and `k≥5` remain
  outside C39.
- Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row y-combo `(-1,0)`, `L1=1`, `y ≡ D^{-1}`.
- 1,563,690 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
