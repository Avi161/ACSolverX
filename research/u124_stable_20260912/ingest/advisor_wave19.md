# Wave 19 stable-AC legality audit (C34)

Source: ac-advisor `bc-08cfd81e-81dd-5f4f-98f5-8411144aafe6`, 2026-09-12.
Coordinator recorded APPROVE. MITM cells were not re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; planted controls reuse the census
  implementation (`same_code_as_census=true`). Tests independently
  check the algebra and rerun only aca_8/aca_72; they do not
  independently replay MITM.
- Observed Cartesian minimum 9 is a census fact, not a length theorem.
- MITM typed size is search-space, not enumerated products.
- The `2≤L1≤7` window is the eight listed rows, not every unimodular
  companion.
- Not a U124 solve.

## ALLOWED CLAIMS

- Bounded no-hit for the eight exact-L1 typed cells.
- Cartesian `59,884` products, minima `[9, 11, 17, 15]`; MITM
  search-space `69,587,713,197`; all-window typed total
  `69,587,773,081`.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
