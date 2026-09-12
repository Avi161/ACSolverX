# Wave plan audit (C43 k=3) — applied before census

Source: ac-advisor `bc-1189b697-33f5-573c-b057-dfa55406863e`, 2026-09-12.
Coordinator recorded APPROVE, then the single-row k=3 census.

C43 is this leftover ncl on aca_43. C44 is the BEST-pair cyclic-length
descent and is a different predicate.

## BLOCKERS

None.

## WARNINGS preserved

1. Single listed row `aca_43` only. Combo `(0,-1)` is for this
   `C_ab=(-1,0)` companion, not every companion of `D`.
2. `x ≡ C^{-1}` is abelianization, not free equality.
3. `k=1` is blocked by cyclic length 11 (`|C|=11` / `|C|≥9`), not `|C|=9`.
4. Orientation is C31: `R^+=C^{-1}`, `S=D`. C35 and C40 orientations
   are rejected. Witness replay bases are
   `{R+:C^{-1}, R-:C, S+:D, S-:D^{-1}}`.
5. Completeness is all 154,368 typed tuples in this bounded pool, not
   distinct reduced words and not `|F|^3`. Predicted counts `(24,24,28,28)`.
6. Disjointness is relative to prior typed donor-family censuses. C28
   already touched this row under a different predicate. C33 used C35
   orientation and y-targets. C44 later used a length-descent predicate.
   Not lumped with leftover y, aca_56/57, C40–C42 leftovers, or C44.
7. Equal typed size 154,368 does not identify C33’s 162,624 on this row.
8. aca_43 C16 / Family A floor is a disclosure, not a C16 re-proof.
9. Leftover y (`L1=1`) was C33. Do not re-run C33.
   `independent_checker=false`.
10. JSON `hit_replay_outside_scanner_capability` is capability, not a
    census hit. Observed minima are C43 census statistics, not a
    comparison with C31/C33/C35.
11. Do not report a miss until the census JSON exists. A hit is an ncl
    candidate until an explicit AC1–AC5 path exists.

## ALLOWED CLAIMS

- Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in abelianization.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: APPROVE
