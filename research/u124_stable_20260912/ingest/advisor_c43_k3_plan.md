# Wave plan audit (C43 k=3) — proposed, census not run

Coordinator proposed plan for ac-advisor. **Not an APPROVE.** Preferred
C43 is aca_43 k=3 for defining word `x`. This is not the parallel
length-descent proposal and must not be lumped with it.

## Proposed route

Single listed row **aca_43** only. Donor `D = YYXXyxx`, `D_ab=(0,-1)`,
cyclic length 7. Companion `YYxyXYxyXyX`, `C_ab=(-1,0)`, cyclic length
11. Unique x-combo `(0,-1)`, `L1=1`, so `x ≡ C^{-1}` **in abelianization**
(not free equality). Same combo for `{x, Yxy, yxY}`.

C34 skipped this row (`L1=1`). C33 already did `y ≡ D^{-1}` k=3 on this
donor/row with C35 orientation; leftover y is also `L1=1` and **must not
be re-run**. C43 is a different predicate.

## Scanner (C41/C42 REVISE items pre-applied)

1. Single listed row `aca_43` only. Combo `(0,-1)` is for this
   `C_ab=(-1,0)` companion, not every companion of `D`.
2. `x ≡ C^{-1}` is abelianization, not free equality.
3. `k=1` is blocked by cyclic length 11 (`|C|=11` / `|C|≥9`), not `|C|=9`.
4. Orientation is C31: `R^+=C^{-1}`, `S=D`. Equality is asserted and
   C35/C40 orientations are rejected (C41 pattern). Replay bases are
   `{R+:C^{-1}, R-:C, S+:D, S-:D^{-1}}`. Scanner bases
   `(C^{-1}, C, D, D^{-1})`.
5. Completeness is all 154,368 typed tuples in this bounded pool, not
   distinct reduced words and not `|F|^3`. Predicted counts `(24,24,28,28)`.
6. Disjointness is relative to prior typed donor-family censuses. C28
   already touched this row under a different predicate. C33 used C35
   orientation and y-targets (typed 162624). Not lumped with C35 leftover
   y on aca_117, aca_56/57, C40 leftover y, C41 leftover y, C42 leftover x,
   or other `YYXXyxx` rows.
7. Equal typed size 154,368 does not identify C33’s 162,624 on this row.
8. aca_43 C16 / Family A floor (archival `P(2)`) is a disclosure, not a
   C16 re-proof.
9. Leftover y (`L1=1`, `y ≡ D^{-1}`) was C33. Do not re-run C33.
   `independent_checker=false`.
10. JSON `hit_replay_outside_scanner_capability` is capability, not a
    census hit. Observed minima are C43 census statistics, not a
    comparison with C31/C33/C35.
11. New files only: `code/c43_yyxxyxx_x_eq_cinv.py`, JSON, and a **third
    new file** `tests/u124_stable_20260912/test_c43_yyxxyxx_x_eq_cinv.py`
    (C42 REVISE: do not edit `test_campaign.py`). Runtime assertions also
    live in the C43 script.

## Allowed claims after a miss

- Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in abelianization.
- Bounded typed-pool negative, or an explicit ncl witness if persisted.
- Score remains `0/124`.

## VERDICT: pending ac-advisor
