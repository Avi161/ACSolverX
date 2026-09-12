# Wave 22 stable-AC legality audit (C37)

Source: ac-advisor `bc-d740bc7a-f6bc-50fb-a049-dd863cd645fc`, 2026-09-12.
Coordinator recorded APPROVE. The 11,804-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun only
  aca_21; they do not independently enumerate all seven rows.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(-1,1)` is for the listed `C_ab=(0,-1)` companions, not every
  unimodular companion of `D`.
- Observed minimum 11 is a C37 census fact, not a length theorem and
  not a comparison with C32.
- Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row x-combo `(-1,1)`, `L1=2`.
- Exact-L1 factors `D^{-1}` and `C`, both orders.
- 11,804 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
