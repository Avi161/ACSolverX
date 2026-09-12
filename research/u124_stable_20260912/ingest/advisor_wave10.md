# Wave 10 stable-AC legality audit (C25)

Source: ac-advisor `bc-6b5c9329-7cb2-518d-8742-631db2b72f32`, 2026-09-12.
Coordinator applied the REVISE below. Three-factor censuses were not
re-enumerated.

## BLOCKERS (as filed)

1. C25.3 treated an ncl hit as a C12/C22.6 path.
   Applied: “normal-closure candidate” only; C12 still needs C1 and
   an AC-reachable primitive relator; C22.6’s conjugator is not a donor.
2. C22.6 is a row-1 identity; only five companions are `P_{m,+1}` row 2.
   Applied: recorded in catalogue and `c15_p_row2`.
3. Counts mixed with `|F|^k` language; negative targets were in the
   wrong abelian class. Applied: nine-config Cartesian after per-type
   dedup; inversion `(f1,f2,f3)↦(f3^{-1},f2^{-1},f1^{-1})`.
4. C25.2 lumped all `k=1` as a length block.
   Applied: abelian-legal `k=1` only for `(n,δ)=(2,-1)`; elsewhere
   `k=1` is abelian-impossible.

## WARNINGS

- JSON is same-code replay, not a second implementation.
- `min_len≥7` is a census, not a length theorem.
- A future ncl hit still needs an explicit AC1–AC5 path.
- Not a U124 solve.

## ALLOWED CLAIMS

- C25.1: `x≡ξ` abelianly; even `k` out; 3-factor misses `x`; `X` by inversion.
- C25.2: `L1=|n+2δ|+1` for all `n≥2`.
- C25.3: `y` and `Xyx` have `L1=1` on C15; `|B|=2m+3`; 3-factor miss
  on the positive class.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
