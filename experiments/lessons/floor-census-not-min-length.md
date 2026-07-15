# [2026-07-14] A length floor is not featureless — census its Aut-orbits [WORKS]

AK(3) at a 1,000,000-node budget reports `min_relator_length = 13 = start` — "zero
progress" — and that number was read as "the search saw nothing". The universal-CoV sweep
(`experiments/stable_ac/cov/ak_3_universal_test/`) showed the floor itself has structure the
metric cannot express: the 13-length states reached across 390 searches fall into TWO
Aut(F₂)-orbits — AK(3)'s own and `YYXXyx|YYYxyXX` — and the baseline's own move set visits
both. `min_relator_length` is blind to an orbit switch at the same length, so the discovery
cost nothing but was invisible for months of runs.

**Rule: when a search saturates at a length floor, run an orbit census on the floor states
(`min_pair` → `autcanon.aut_canon`, witnesses checked) before concluding "no progress".**
Same instrument as the ms640 equivalence work ([[search-the-aut-quotient-not-raw-length]]);
it applies to single-presentation searches too.

Second, independent trap from the same session: the ≤17 AC component of AK(3) enumerated to
EXACTLY 1,000 states — exactly the repo's pop cap. "EXHAUSTED at precisely the cap" is
indistinguishable from a truncation artifact by accounting alone (BFS and DFS both agreeing
proves nothing about the cap edge case). **Prove completeness by closure — every child of
every member lies inside the set — which no pop cap or traversal order can fake**
(`certify_classical.py`). The count was real, but only the closure check made it a proof.
