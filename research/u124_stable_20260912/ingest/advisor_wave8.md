# Wave 8 stable-AC legality audit (C23)

Source: ac-advisor `bc-15d99e7d-2617-5fe2-8084-2ec9faf17a4b`, 2026-09-12.
Coordinator applied the REVISE below, then strengthened C23.3’s predicate
to free or cyclic equality with `D^{±1}` (`same_cyclic`) and re-ran.

## BLOCKERS (as filed)

1. C23.3 claimed cyclic conjugacy while `cyc_reduce` only peels ends.
   Applied: check `same_cyclic` against `D` and `D⁻¹`.
2. “What this does not rule out” mixed C23.2’s four-factor remainder with
   C23.3’s depth. Applied: C23.2 four or more factors; C23.3 depth ≥ 3.
3. Prefix set is both spellings `R^{±1}`, `S^{±1}`. Applied.

## WARNINGS

- JSON is produced by the cited program, not a second implementation.
- “Degenerate” means a mutually inverse factor pair, which freely reduces
  to a conjugate of `R^δ`.
- Extra depth or longer conjugators remain open. Not a U124 solve.

## ALLOWED CLAIMS

- C23.1: exactly nine signed-typed patterns, 3+6+0, uniform in `n≥2`.
- C23.2: 1,529,400 products, min length 7, no `ξ^{±1}`.
- C23.3: enumerated F3 depth-2 products; min non-generator length 8;
  no free/cyclic `D^{±1}` under the strengthened predicate.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
