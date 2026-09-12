# Wave plan audit (C42) — applied before census

Source: ac-advisor `bc-690b9e1e-9e82-5393-8bf1-a95c0d279bd0`, 2026-09-12.
Coordinator applied the REVISE below, then ran the single-row k=3 census.

## BLOCKERS

Resolved: “new files only” for the census is
`code/c42_yyxxxyxx_y_eq_cinv.py` plus its JSON. Identity checks are a
**third new file**
`tests/u124_stable_20260912/test_c42_yyxxxyxx_y_eq_cinv.py`,
not an edit of `test_campaign.py`. Runtime assertions also live in the
C42 script. No pytest-coverage claim.

## WARNINGS / REVISE items applied

1. Single listed row `aca_38` only. Combo `(0,-1)` is for this
   `C_ab=(0,-1)` companion, not every companion of `D`.
2. `y ≡ C^{-1}` is abelianization, not free equality.
3. `k=1` is blocked by cyclic length 11 (`|C|=11` / `|C|≥9`), not `|C|=9`.
4. Orientation is C31: `R^+=C^{-1}`, `S=D`. Equality is asserted and
   C35/C40 orientations are rejected (C41 pattern, not C36’s weaker
   check). Replay bases are `{R+:C^{-1}, R-:C, S+:D, S-:D^{-1}}`.
5. Completeness is all 183,924 typed tuples in this bounded pool, not
   distinct reduced words and not `|F|^3`.
6. Disjointness is relative to prior typed donor-family censuses. C28
   already touched this row under a different predicate. Not lumped with
   C40, C41, aca_56, or aca_57.
7. Equal typed size 183,924 does not identify C40 aca_95.
8. Companion is consecutive `BS(4,5)`; that is classification, not a
   C15/C31 rerun.
9. Leftover `x` (`L1=2`) is not part of C42. `independent_checker=false`.
10. JSON `hit_replay_outside_scanner` boolean is capability, not a
    census hit. Observed minima are C42 census statistics, not a
    comparison with C31/C36/C40/C41.

## ALLOWED CLAIMS

- Unique listed-row y-combo `(0,-1)`, `L1=1`, `y ≡ C^{-1}` in abelianization.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: REVISE (applied before census)
