# Wave 26 stable-AC legality audit (C41)

Source: ac-advisor `bc-b9de5934-dde0-59e3-ac28-4ceaa5f71d2f`, 2026-09-12.
Coordinator recorded APPROVE. The 164,475-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Tests rerun the
  single row; they are not a second implementation.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(0,-1)` and `x ≡ C^{-1}` are abelianization facts on listed
  `C_ab=(-1,0)` row aca_71, not free equality and not every companion
  of `D`.
- `k=1` is blocked by cyclic length 11 (`|C|≥9`), not `|C|=9`.
- C31 orientation `R^+=C^{-1}`, `S=D` is asserted. C35 and C40
  orientations are not used.
- Observed minimum 11 is a C41 census fact, not a length theorem and
  not a comparison with C31/C36/C40.
- Completeness is all 164,475 typed tuples in this bounded pool.
- Equal typed size 164,475 does not identify other censuses.
- JSON summary key `hit_replay_outside_scanner` is capability, not a
  census hit.
- `mu_floor_r8` pending orbit replay is a disclosure, not a C8
  re-proof. Not a U124 solve. `0/124` is the campaign ledger.

## ALLOWED CLAIMS

- Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in abelianization.
- 164,475 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
