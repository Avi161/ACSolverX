# Wave 13 stable-AC legality audit (C28)

Source: ac-advisor `bc-e45cc08b-e7fd-51bf-a8a1-d87a69078813`, 2026-09-12.
Coordinator applied the REVISE below. The depth-2 neighbourhood was not
re-enumerated; summary notes and tests were refreshed from the existing
JSON.

## BLOCKERS (as filed)

None. Soundness of the finite neighbourhood is accepted.

## WARNINGS / REVISE items applied

1. Depth counts AC2 multiplications, not total elementary AC1–AC5
   moves. Applied: Expansion no longer says “two-move AC1–AC3 path.”
2. Unique counts are sums of row-local exact-spelling states; raw
   counts are second-step edges from deduplicated depth-1 parents with
   move-tuple multiplicity.
3. JSON is a single resumed deterministic census plus sampled
   same-implementation checks, not a second implementation or a fresh
   full replay of every row. `independent_checker=false` kept.
4. Best-table comparison covers a child or grandchild. Tests now pin
   36,312 / 19,066,394 / 7,166,262.

## ALLOWED CLAIMS

- C28.1: no row-local exact-spelling-unique cyclic-length drop, new
  one-occurrence, or new two-block–both at depth ≤ 2 on the 124
  archival initial rows or on parametric `P`/`Q`/Family A (`n=2..7`).
- No `canon_pair` hit on the 36 stored best spellings inside that
  neighbourhood.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: REVISE (applied)
