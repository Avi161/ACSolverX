# Wave plan audit (C39) — applied before census

Source: ac-advisor `bc-4f336ced-0b01-527a-9a86-56499f963348`, 2026-09-12.
Coordinator recorded APPROVE, then ran the k=3 nine-config census.

## BLOCKERS

None.

## WARNINGS preserved

1. Scanner bases are `(D^{-1}, D, C, C^{-1})` with asserted
   `C35_ORIENTATION`. `C31_ORIENTATION` is not used.
2. Combo `(-1,0)` and `L1=1` are for the six listed rows (`p=±1`),
   not every companion of `D`.
3. Disjointness is of donor/row presentation pairs. Companion words
   `YYYYYYXXXYxx` and `YYYYYYYXXXYxx` also appear in C38.
4. `c35.reconstruct_hit` is outside-scanner replay, not an independent
   implementation. `independent_checker=false`.
5. The 500,000 cap is per Cartesian cell. Predicted total 1,563,690 is
   not a completeness claim beyond this typed pool.
6. Not the last unused listed donor. Exact-L1 `x` is not part of C39.
7. Observed minima are C39 census statistics, not a comparison with
   C38/C29/C33. Equal typed sizes to some C38 rows do not identify
   those censuses.
8. Planted hit/miss control exercises the witness-recording branch.

## ALLOWED CLAIMS

- Six-row unique y-combo `(-1,0)`, `L1=1`, `y ≡ D^{-1}`.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: APPROVE
