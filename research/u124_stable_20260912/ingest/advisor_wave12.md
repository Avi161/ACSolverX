# Wave 12 stable-AC legality audit (C27)

Source: ac-advisor `bc-24f3c03d-4ed0-593b-b911-62c877558c6d`, 2026-09-12.
Coordinator recorded APPROVE. The archival AC2 and k=4 censuses were not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay, not a second
  implementation. Status stays IDENTITY-CHECKED NEGATIVE.
- C27.1 is one AC2 modulo cyclic orientations, not arbitrary longer
  AC3–AC2 composites.
- Observed Cartesian minimum 11 is a census fact, not a length theorem.
- Not a U124 solve.

## ALLOWED CLAIMS

- C27.1: no unique depth-1 AC2 length drop / new one-occurrence /
  new two-block on the 124 archival initial rows (36 μ-floor spellings
  included) or on parametric `P`/`Q`/Family A (`n=2..7`).
- C27.2: the two k=4 extra-pair types on `Q'_{3,-1}` are complete for
  net `(1,-1)`; 5,128,200 typed products, no hit on `{y, Xyx, xyX}`.
- Score remains `0/124`.

## VERDICT: APPROVE
