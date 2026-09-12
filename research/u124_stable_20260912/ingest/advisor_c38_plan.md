# Wave plan audit (C38) — applied before census

Source: ac-advisor `bc-8deb495a-f702-565f-a5de-855fac0b82cd`, 2026-09-12.
Coordinator recorded APPROVE, then ran the k=3 nine-config census.

## BLOCKERS

None.

## WARNINGS preserved

1. Scanner bases are `(D^{-1}, D, C, C^{-1})` with asserted
   `C35_ORIENTATION`. `C31_ORIENTATION` is not used.
2. Combo `(-1,0)` and `L1=1` are for the seven listed rows (`p=±1`),
   not every companion of `D`.
3. Disjointness is of donor/row presentation pairs. Companion words
   `YYYYYYXXXYxx` and `YYYYYYYXXXYxx` also appear in `YXXyXYxxx`.
4. `c35.reconstruct_hit` is outside-scanner replay, not an independent
   implementation. `independent_checker=false`.
5. The 500,000 cap is per Cartesian cell. Predicted total 1,798,887 is
   not a completeness claim beyond this typed pool.
6. Not the last unused listed donor. Exact-L1 `x` is not part of C38.
7. Observed minima are C38 census statistics, not a comparison with
   C29/C33.

## ALLOWED CLAIMS

- Seven-row unique y-combo `(-1,0)`, `L1=1`, `y ≡ D^{-1}`.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: APPROVE
