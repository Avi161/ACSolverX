| Family | Count | Description | Theory grounding |
|---|---|---|---|
| relhalf | 17 | Relator halves/rotations/inverses of the target's relators | Dumb baseline (no theorem) |
| wk | 17 | y^-k x^-1 y x y isolation words | Thm 6/7 (arXiv:2408.15332) |
| wstar | 5 | y^-1 x y x^-1, plus automorphism images | Thm 3 (arXiv:2408.15332) |
| conj | 14 | Short conjugates g x g^-1, g y g^-1 | Dumb baseline (no theorem) |
| comm | 6 | Commutators and doubles | Dumb baseline (no theorem) |
| ms | 3 | MS(n,w) library words | Miller-Schupp family |
| brute | 33 | All freely-reduced words of length ≤3 | Exhaustive enumeration (no theorem) |
| control | 2 | The target's own relators r1, r2 | Sanity control (z=r_i) |
| Total | 97 |  |  |

*Note: Counts for the 7 literature-grounded families (95 words total) come from word_bank.json's by_family; the 2 control words (z=r1, z=r2) are added at runtime and counted here from runs/ak3_rep_100000.jsonl's family={'control'} rows.*

*Note: Verification: family counts sum to 97, matching the 97-row ak3_rep_100000.jsonl (one row per word per form) (match).*
