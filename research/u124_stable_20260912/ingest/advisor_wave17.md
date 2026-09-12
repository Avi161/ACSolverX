# Wave 17 stable-AC legality audit (C32)

Source: ac-advisor `bc-f92b6329-ef8a-543a-a716-5beaf006d3da`, 2026-09-12.
Coordinator applied the REVISE below. The eight Cartesian cells were not
re-enumerated; wording was aligned with C30.

## BLOCKERS (as filed)

None.

## WARNINGS / REVISE items applied

1. C32 now states the C30 free-equality limitation: equality was tested
   after free reduction only against `{x, Yxy, yxY}`. No cyclic-reduction
   or conjugacy quotient, ambient Aut(F₂), or Tietze identification was
   used; freely reduced longer conjugates of `x` remain untested.
2. `independent_checker=false` kept. Tests independently check the algebra
   and rerun only aca_23/aca_32; they do not independently replay all
   eight census cells.

## ALLOWED CLAIMS

- Unique x-combo against `D_ab=(1,-1)` is `b=p+q`, `a=(p+q)q`.
- All eight stored cells are Cartesian; 51,412 enumerated typed tuples,
  not a claim of 51,412 distinct reduced words.
- Observed minima `[13,11,13,13,15,15,17,17]` and lower bound 11 are
  census facts.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: REVISE (applied)
