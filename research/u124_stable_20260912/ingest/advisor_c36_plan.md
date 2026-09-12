# Wave plan audit (C36) — applied before census

Source: ac-advisor `bc-f914cba4-8987-50d2-b42a-87d62c2020b1`, 2026-09-12.
Coordinator applied the REVISE below, then ran the k=3 census.

## BLOCKERS

None.

## WARNINGS / REVISE items applied

1. Combo `(0,-1)` is for companions with `C_ab=(0,-1)`, in particular
   the seven listed BS rows, not every unimodular companion of this donor.
2. Orientation is C31’s: `R^+ = C^{-1}`, `S = D`. The C35 scanner default
   is overwritten/asserted; C35 metadata is not reused blindly.
3. Disjointness is of donor/row presentation pairs, not of the companion
   word set (those overlap C31/C15). C28 touched these rows under a
   different depth-2 AC2 predicate.
4. A hit is verified outside the scanner by reconstructing conjugates from
   (base, conjugator) and replaying the product. That is still
   `independent_checker=false`.
5. Observed minimum length is a C36 census statistic, not a theorem and
   not a comparison with C31.

## ALLOWED CLAIMS

- All seven listed companions are consecutive `BS(m,m+1)`; no exceptional
  row. Unique positive-y combo `(0,-1)`.
- Even `k` impossible; `k=1` blocked by cyclic length; k=3 nine configs.
- Deferred `x` combo is uniformly `(-1,1)`, `L1=2`.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: REVISE (applied before census)
