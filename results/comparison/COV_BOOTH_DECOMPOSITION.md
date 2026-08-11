# What the redundant slots actually are

Subset-60, budget 1,000, **6,177 candidate rows** over 60 presentations, at zero search nodes. Each level is the previous relation plus one more, so **new** attributes a drop to the relation that first catches it. Grouping is **within a presentation**, always. *bit-identical* = every member of the group returned the same `(solved, nodes_explored, path_length)`.

This table exists because an earlier pass reported `relabel_key`'s 4,561 drops as **renames**. The name of the key is the trap: `words.relabel_key` runs `canon_pair` *before* minimising over the 8 signed permutations, so nearly everything it merges was already identical after canonicalisation and has nothing to do with renaming `x` and `y`.

| level | kept | dropped | new | bit-identical |
|---|---:|---:|---:|---|
| exact string | 6,177 | 0 | 0 | — |
| + relator order swap `(r1,r2)→(r2,r1)` | 6,177 | 0 | 0 | — |
| + relator inversion `r → r⁻¹` | 6,157 | 20 | 20 | **20 / 20** |
| + cyclic reduction | 3,929 | 2,248 | 2,228 | **959 / 959** |
| + rotation (= full Booth `canon_pair`) | 2,078 | 4,099 | 1,851 | **1,053 / 1,053** |

**Relator order swap contributes nothing at all, and the single biggest component is cyclic reduction** — the same word with cancelling letters removed — not rotation and certainly not renaming.

Renaming is reported apart from the chain because it is a different relation, not a further weakening of it. It drops **23 slots** in the whole pool; **17** of those pairs are duplicates under Booth as well, leaving **6 slots** that renaming catches and nothing else does.

Every level is bit-identical without exception. The inversion row (20/20) is the empirical confirmation that the S-move set's optional-invert symmetry leaves the search unchanged; the rotation row (1053/1053) says the same for Booth. Contrast `relabel_key`, whose extra merges are renames *of a rotation* and are **not** bit-identical — 148 of its 784 groups disagree; see `COV_POOL_DEDUP_LADDER.md`.

No census here merges across presentations. Pooled globally, **195 Booth groups would span more than one presentation** — none are collapsed, because two presentations are different problems and each needs its own candidates.

Reproduce: `.venv/bin/python3 -m experiments.heuristic_search.runners.cov_booth_decomposition`
