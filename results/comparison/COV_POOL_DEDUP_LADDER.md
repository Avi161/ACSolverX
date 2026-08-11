# The CoV pool dedup ladder — what is provably redundant

Subset-60, budget 1,000, **6,177 candidate rows** over 60 presentations, regrouped from the frozen sweep at zero search nodes. *bit-identical* = every member of the group returned the same `(solved, nodes_explored, path_length)`.

| grouping | kept | dropped | groups ≥2 | members | bit-identical |
|---|---:|---:|---:|---:|---|
| exact string | 6,177 | 0 | 0 | 0 | — |
| pure relabel (8 signed perms, literal) | 6,154 | 23 | 23 | 46 | **23 / 23** |
| Booth (cyclic reduction + rotation + relator order) | 2,078 | 4,099 | 1,053 | 5,152 | **1,053 / 1,053** |
| Booth or pure relabel (union) | 2,072 | 4,105 | 1,047 | 5,152 | **1,047 / 1,047** |
| relabel_key (the shipped dedup) | 1,616 | 4,561 | 784 | 5,345 | 636 / 784 |

Reproduce: `.venv/bin/python3 -m experiments.heuristic_search.runners.cov_pool_dedup_ladder`
