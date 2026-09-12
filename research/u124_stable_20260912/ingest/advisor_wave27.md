# Wave 27 stable-AC legality audit (C42)

Source: ac-advisor `bc-503ddbf7-eb10-5dc7-8bf7-f6e05e6e3209`, 2026-09-12.
Coordinator recorded APPROVE. The 183,924-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Identity checks are a
  new file and they re-enumerate all 183,924 products; they are not
  lightweight and not a second implementation.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(0,-1)` and `y ≡ C^{-1}` are abelianization facts on listed
  `C_ab=(0,-1)` row aca_38, not free equality and not every companion
  of `D`.
- `k=1` is blocked by cyclic length 11 (`|C|=11` / `|C|≥9`), not `|C|=9`.
- C31 orientation `R^+=C^{-1}`, `S=D` is asserted. C35 and C40
  orientations are not used.
- Companion `BS(4,5)` is classification, not a C15/C31 rerun.
- Observed minimum 11 is a C42 census fact, not a length theorem and
  not a comparison with C31/C36/C40/C41.
- Completeness is all 183,924 typed tuples in this bounded pool.
- Equal typed size 183,924 does not identify C40 aca_95.
- JSON `hit_replay_outside_scanner_capability` is capability, not a
  census hit. Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row y-combo `(0,-1)`, `L1=1`, `y ≡ C^{-1}` in abelianization.
- 183,924 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
