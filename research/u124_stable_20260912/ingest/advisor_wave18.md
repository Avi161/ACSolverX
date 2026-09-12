# Wave 18 stable-AC legality audit (C33)

Source: ac-advisor `bc-541c9054-fe41-5aab-aeb7-12f9e94a4b0d`, 2026-09-12.
Coordinator recorded APPROVE. The k=3 nine-config census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; planted control and census share an
  implementation. Tests spot-check identities and stored JSON; they do
  not independently enumerate the census.
- Observed minimum 7 is a per-row census fact, not a length theorem
  and not a comparison with C29.
- “Not a re-run of C29” means a disjoint donor/row pool. C33 imports
  C29/C25 machinery; it is not independent code.
- Not a U124 solve.

## ALLOWED CLAIMS

- C33.1 is C29.1’s identity on two unused donors: unique y-combo
  `(-1,0)`, `L1=1`, `R^+ = D^{-1}`.
- 1,737,522 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
