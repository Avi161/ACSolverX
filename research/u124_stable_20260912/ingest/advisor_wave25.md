# Wave 25 stable-AC legality audit (C40)

Source: ac-advisor `bc-b92cee0e-03e9-560b-ba5d-730767401d96`, 2026-09-12.
Coordinator recorded APPROVE. The 332,199-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests check both
  rows’ algebra and rerun only aca_16; they do not independently
  enumerate aca_95.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(0,1)` and `x ≡ C` are abelianization facts on the two listed
  `C_ab=(1,0)` rows, not free equality and not every companion of `D`.
- `k=1` is blocked by `|C|≥9` (lengths 9 and 11), not `|C|=9`.
- C40 orientation `R^+=C`, `S=D` is asserted. C35 and C31 orientations
  are not used.
- Observed minima 9 and 11 are C40 census facts, not a length theorem
  and not a comparison with C35/C36/C38.
- Disjointness is relative to prior typed donor-family censuses. C28
  already touched these rows under a different predicate.
- Not a six-row `YYXXXyxx` census. Remaining mixed rows stay outside
  C40. Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Two-row unique x-combo `(0,1)`, `L1=1`, `x ≡ C` in abelianization.
- 332,199 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
