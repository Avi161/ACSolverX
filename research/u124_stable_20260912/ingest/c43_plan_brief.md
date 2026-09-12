# C43 proposed plan (pre-advisor, census not run)

Coordinator request for ac-advisor plan audit of the **preferred C43**:
aca_43 k=3 for defining word `x`. Do not treat this file as an APPROVE.
Census has not been run. This is **not** a cyclic pair-length descent
and must not be lumped with that proposal.

## Route

Single listed row **aca_43** only. Donor `D = YYXXyxx`, `D_ab=(0,-1)`,
cyclic length 7. Companion `YYxyXYxyXyX`, `C_ab=(-1,0)`, cyclic length
11. Unique x-combo `(0,-1)`, `L1=1`, so `x ≡ C^{-1}` **in abelianization**
(not free equality). Same combo for `{x, Yxy, yxY}`.

C34 skipped this row (`L1=1`). C33 already did `y ≡ D^{-1}` k=3 on this
donor/row with C35 orientation; leftover y is also `L1=1` and **must not
be re-run**. C43 is a different predicate.

## Scanner

- C31 orientation `R^+=C^{-1}`, `S=D`. Assert C31; reject C35 and C40
  (C41/C42 pattern). Replay bases `{R+:C^{-1}, R-:C, S+:D, S-:D^{-1}}`.
- Prefix/one-letter conjugators. Predicted unique-conjugate counts
  `(24,24,28,28)` (cheap conjugate census already checked; not the
  product census). Typed size `3*24^2*24 + 6*24*28*28 = 154368`.
- `k=1` blocked by `|C|=11` / `|C|≥9`, not `|C|=9`. Even k impossible
  (C24.1).
- Completeness is all 154,368 typed Cartesian tuple evaluations, not
  distinct reduced words, not `|F|^3`.
- Equality is free-reduce literal only.
- A hit is an ncl candidate, not a C12 primitive unless an explicit
  AC1–AC5 path exists. Persist factors/conjugators and replay outside
  the scanner. JSON capability flag is not a census hit.
- `independent_checker=false`. New files only:
  `code/c43_yyxxyxx_x_eq_cinv.py`, JSON, and
  `tests/u124_stable_20260912/test_c43_yyxxyxx_x_eq_cinv.py`.
  Do not edit `test_campaign.py`. Runtime assertions in the census
  script.

## Disjointness / do not lump

Donor/row presentation pairs. C28 touched aca_43 under depth-2 AC2.
C33 used C35 orientation and y-targets on this same pair (typed 162624,
counts `(28,28,24,24)`). Equal typed sizes do not identify censuses.
Not lumped with: C35 leftover y on aca_117; aca_56/57; C40 leftover y
on aca_16/95; C41 leftover y on aca_71; C42 leftover x on aca_38; other
`YYXXyxx` rows.

## Disclosures

aca_43 C16 escape / Family A floor (archival `P(2)`) is classification,
not a C16 rerun and not a U124 solve. Score remains 0/124 on a miss.

## Allowed claims after a miss

Unique listed-row x-combo `(0,-1)`, `L1=1`, `x ≡ C^{-1}` in
abelianization. Bounded typed-pool negative. Score 0/124.
