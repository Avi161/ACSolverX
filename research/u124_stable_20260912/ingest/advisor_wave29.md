# Wave 29 stable-AC legality audit (C43)

Source: ac-advisor `bc-9126c338-edb6-5f7a-b124-ee6909eb5eef`, 2026-09-12.
Coordinator recorded APPROVE. The 154,368-product census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay. Identity checks re-run
  the single row; they are not a second implementation.
- “Products” are typed Cartesian tuple evaluations, not distinct
  freely reduced product words.
- Combo `(0,-1)` and `x ≡ C^{-1}` are abelianization facts on listed
  `C_ab=(-1,0)` row aca_43, not free equality and not every companion
  of `D`.
- `k=1` is blocked by cyclic length 11 (`|C|=11` / `|C|≥9`), not `|C|=9`.
- C31 orientation `R^+=C^{-1}`, `S=D` is asserted. C35 and C40
  orientations are not used. C33 (y, C35 orientation) was not re-run.
- Observed product-word free-length minimum 11 is a C43 census
  statistic: not a presentation-pair total, not a drop from BEST total
  18, and not a C10 finish.
- Completeness is all 154,368 typed tuples in this bounded pool.
- Equal typed size 154,368 does not identify C33’s 162,624.
- JSON `hit_replay_outside_scanner_capability` is capability, not a
  census hit. Actual hit replay is `null`. Not a U124 solve. `0/124`.
- C44 is a different predicate.

## ALLOWED CLAIMS

- Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in abelianization.
- 154,368 typed Cartesian products, equal to typed size, no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
