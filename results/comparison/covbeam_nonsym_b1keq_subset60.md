# Cost-matched α-sweep (charge α nodes per aut_canon call)

Derived from one greedy@1000-from-best_rep run per row (zero extra search). Replaces unreproducible wall-clock `node_eq_ms`.

| α | solves/60 | B_rem=0 rows |
|---:|---:|---:|
| 0 | **49**/60 | 0 |
| 1 | **45**/60 | 0 |
| 2 | **45**/60 | 15 |
| 5 | **43**/60 | 17 |
| 10 | **37**/60 | 23 |
| 15 | **28**/60 | 32 |
| 33 | **18**/60 | 42 |

Shipped `b1k_greedy` = 29/60; `b1k_heur` = 43/60 (neither charges CoV).

At large α the beam leaves no search budget — that is a statement about **this cost model**, not “the transform hurts”.
