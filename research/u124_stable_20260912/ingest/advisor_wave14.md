# Wave 14 stable-AC legality audit (C30)

Source: ac-advisor `bc-528431a7-bf51-5c1d-865a-1a1fe541def1`, 2026-09-12.
Coordinator applied the REVISE below. MITM cells were not re-enumerated;
summary notes and tests were refreshed from the existing JSON.

## BLOCKERS (as filed)

None. The census and negative result are sound within the stated pool.

## WARNINGS / REVISE items applied

1. `|b|=1` follows from unimodularity with `D_ab=(0,-1)`: unique
   combination is `(a,b)=(pq,p)`. The range `L1 ∈ {2,…,7}` is for the
   eleven listed rows, not every conceivable unimodular companion.
2. Equality is free-reduce literal match against `{x, Yxy, yxY}`.
   Longer conjugates of `x`, cyclic conjugacy quotients, ambient Aut,
   and Tietze identifications remain untested.
3. `independent_checker=false` kept. Controls reuse the census
   implementation (`same_code_as_census`).

## ALLOWED CLAIMS

- Exact L1 completeness at `k=L1` is the C24.1 family `|a|` signed-D
  factors and one signed-C factor.
- `{x, Yxy, yxY}` is the complete freely reduced class of `x`
  conjugated by words of length at most one.
- Typed totals 43,999,487,350 / Cartesian 107,212 / MITM search-space
  43,999,380,138. Cartesian minima `[15,15,11]`.
- Five C7 floors aca_120, 34, 58, 81, 97. Aut-minimality is not a solve.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: REVISE (applied)
