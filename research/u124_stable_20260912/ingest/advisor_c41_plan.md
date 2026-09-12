# Wave plan audit (C41) — applied before census

Source: ac-advisor `bc-04343dbd-e6a3-54d4-bb0f-4b063caa4a7a`, 2026-09-12.
Coordinator recorded APPROVE, then ran the single-row k=3 census.

## BLOCKERS

None.

## WARNINGS preserved

1. Single listed row `aca_71` only. Combo `(0,-1)` is for this
   `C_ab=(-1,0)` companion, not every companion of `D`.
2. `x ≡ C^{-1}` is abelianization, not free equality.
3. `k=1` is blocked by cyclic length 11 (`|C|≥9`), not `|C|=9`.
4. Orientation is C31: `R^+=C^{-1}`, `S=D`. C35 and C40 orientations
   are rejected. Witness replay bases are
   `{R+:C^{-1}, R-:C, S+:D, S-:D^{-1}}`.
5. Completeness is all 164,475 typed tuples in this bounded pool, not
   distinct reduced words and not `|F|^3`.
6. Disjointness is relative to prior typed donor-family censuses. C28
   already touched this row under a different predicate. Not lumped with
   aca_38, aca_56, aca_57, or C40.
7. Equal typed size 164,475 does not identify other censuses.
8. `mu_floor_r8` pending orbit replay is a disclosure, not a C8 re-proof.
9. Leftover `y` (`L1=2`) is not part of C41. `independent_checker=false`.
10. Observed minima are C41 census statistics, not a comparison with
    C31/C36/C40.

## ALLOWED CLAIMS

- Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in abelianization.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: APPROVE
