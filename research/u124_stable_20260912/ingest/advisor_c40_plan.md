# Wave plan audit (C40) — applied before census

Source: ac-advisor `bc-f97175b8-1db3-5ce4-8b91-4d5266b847e1`, 2026-09-12.
Coordinator applied the REVISE below, then ran the two-row k=3 census.

## BLOCKERS

None.

## WARNINGS / REVISE items applied

1. `k=1` is blocked by `|C|≥9` (cyclic lengths 9 and 11), not `|C|=9`.
2. Every `x ≡ C` statement is abelianization, not free equality.
3. Disjointness is relative to prior typed donor-family censuses.
   C28 already touched these rows under a different predicate.
4. New `C40_ORIENTATION` (`R^+=C`, `S=D`) is asserted. C35 and C31
   orientations are rejected. Witness replay bases are
   `{R+:C, R-:C^{-1}, S+:D, S-:D^{-1}}`.
5. Two listed rows only (`aca_16`, `aca_95`). Not a six-row
   `YYXXXyxx` census. `independent_checker=false`.
6. Observed minima are C40 census statistics, not a comparison with
   C35/C36/C38.

## ALLOWED CLAIMS

- Two-row unique x-combo `(0,1)`, `L1=1`, `x ≡ C` in abelianization.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: REVISE (applied before census)
