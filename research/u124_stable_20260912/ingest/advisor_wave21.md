# Wave 21 stable-AC legality audit (C36)

Source: ac-advisor `bc-2d114b7d-c764-5fee-b063-a18eeca63581`, 2026-09-12.
Coordinator recorded APPROVE. The k=3 nine-config census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun only
  aca_21; they do not independently enumerate all seven rows.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(0,-1)` is for the listed `C_ab=(0,-1)` companions, not every
  unimodular companion of `D`.
- Observed minimum 9 is a C36 census fact, not a length theorem and
  not a comparison with C31.
- Disjointness is of donor/row presentation pairs, not companion words.
- Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row y-combo `(0,-1)`, `L1=1`; leftover x-combo
  `(-1,1)`, `L1=2`.
- 1,549,596 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
