# Wave 20 stable-AC legality audit (C35)

Source: ac-advisor `bc-c0eb0d61-c0c1-5ad6-a1e7-71c765b2cbd6`, 2026-09-12.
Coordinator recorded APPROVE. The k=3 nine-config census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun only
  aca_117; they do not independently enumerate all six rows.
- “Last unused length-7 donor” is restricted to the listed
  shared-donor inventory (four length-7 donors: C29, C33 two, C35).
- A hit would be a free-group normal-closure witness, not AC
  reachability.
- Observed minimum 7 is a C35 census fact, not a theorem and not a
  comparison with C29/C33/C34.
- Not a U124 solve.

## ALLOWED CLAIMS

- Unique x-combo `(-1,0)`, `L1=1`, `R^+ = D^{-1}` on the six listed
  rows; pair-matrix unimodularity, all `q=-1`.
- 579,870 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
