# Wave 15 stable-AC legality audit (C29)

Source: ac-advisor `bc-e43cb290-58a0-5657-a22c-04dec777397b`, 2026-09-12.
Coordinator recorded APPROVE. The k=3 nine-config census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay plus planted control,
  not a second implementation. Status stays IDENTITY-CHECKED NEGATIVE.
- Observed minimum 7 is a census fact, not a length theorem.
- A hit would be a normal-closure candidate, not a C12 primitive.
- Not a U124 solve.

## ALLOWED CLAIMS

- C29.1: unique combo of `y` against `(D,C)` is `(-1,0)`, `L1=1`;
  even `k` impossible; `k=1` blocked by `|D|=7`.
- C29.2: nine-config typed Cartesian pool is complete for `k=3`;
  1,650,843 products, equal to typed size, no hit on `{y, Xyx, xyX}`.
- Free identity `D · Xyx = YXXyxx` is not an AC2.
- Five C7 floors aca_120, 34, 58, 81, 97 remain unsolved.
- Score remains `0/124`.

## VERDICT: APPROVE
