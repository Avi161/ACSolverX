# Wave plan audit (C37) — applied before census

Source: ac-advisor `bc-3486edfc-da65-5ba9-a71b-0397b5e07cec`, 2026-09-12.
Coordinator applied the REVISE below, then ran the exact-L1 census.

## BLOCKERS

None.

## WARNINGS / REVISE items applied

1. Two-factor hits persist ordered signed types, factors, conjugators,
   and an outside-scanner reconstruction/replay. `c26.cartesian_m_plus_one`
   is not used as the sole hit record.
2. Combo `(-1,1)` and `L1=2` are for the seven listed `C_ab=(0,-1)` rows,
   not every unimodular companion of `D`.
3. Per-row `n_products == n_typed_tuples`. Expected typed total 11,804.
4. `independent_checker=false`. Outside replay is same-code verification.
5. Products are typed Cartesian tuple evaluations, not distinct reduced
   words. Observed minima are C37 census statistics, not a comparison
   with C32.

## ALLOWED CLAIMS

- Seven-row unique combo `(-1,1)`, `L1=2`.
- Exact-L1 factors `D^{-1}` and `C`, both orders.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: REVISE (applied before census)
