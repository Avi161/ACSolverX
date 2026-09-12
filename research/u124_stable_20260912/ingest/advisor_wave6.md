# Wave 6 stable-AC legality audit (C21)

Source: ac-advisor `bc-3116365b-d7b3-59c4-aab3-3b77ec4b0a7a`, 2026-09-12.
Coordinator applied the REVISE below, then strengthened the parent-drop
census so claim 2 is an all-edge count, not a first-seen-parent report.

## BLOCKERS (as filed)

1. First-seen `seen_global` made `n_parent_drop` order-dependent.
   Applied: count drop edges per parent before the global unique filter.
   Result: `n_return_to_DB_edges = 10` for every `n=2..7` (each of the
   ten parents has a `canon_pair(D,B)` child). `n_parent_drop_edges = 10`
   for `n≥3` and `12` for `n=2`.
2. `n_return_to_c19_length` was length equality. Applied: also count
   `canon_pair` equality with `⟨D,B⟩`.

## WARNINGS

- Unique means global `canon_pair` (cyclic/inverse and slot order), not
  Aut-equivalence.
- Claim 3 is one valid associated-subgroup rewrite, not iterated Britton.
- The JSON is produced by the cited program.
- Incoming C16 still has two C0 uses. Not a U124 solve.

## ALLOWED CLAIMS

- Ten no-pinch children keep `D`; companion lengths `2n+6` (four) and
  `2n+8` (six), `n=2..7`.
- Globally unique AC2 grandchildren: 1580 at `n=2`, 3580 at `n=7`; none
  has cyclic total below `2n+10`.
- All-edge parent drops: ten returns to `⟨D,B⟩` per `n`; `n=2` has two
  extra edges into a length-16 class.
- Single valid `other` pinch leftovers: min length 9 (`n=2`) or 10
  (`n≥3`); Britton preflights, not AC.
- `I_S = u² x^{nδ} y⁻¹` has no `y^{±1}` orientation on the twelve
  tested parameters. Gate 2 as written is not immediate bare AC5.

## VERDICT: REVISE (applied)
