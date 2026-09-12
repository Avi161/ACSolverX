# Wave 23 stable-AC legality audit (C38)

Source: ac-advisor `bc-b33b1c24-d252-591b-98b1-dde5316c00b8`, 2026-09-12.
Coordinator recorded APPROVE. The 1,798,887-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun only
  aca_48; they do not independently enumerate all seven rows.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(-1,0)` is for the seven listed `|p|=1` rows, not every
  companion of `D` and not `p=0`.
- Observed minimum 9 is a C38 census fact, not a length theorem and
  not a comparison with C29/C33.
- Disjointness is of donor/row presentation pairs, not companion words.
- Not the last unused listed donor. Exact-L1 `x` and `k≥5` remain
  outside C38.
- Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row y-combo `(-1,0)`, `L1=1`, `y ≡ D^{-1}`.
- 1,798,887 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
