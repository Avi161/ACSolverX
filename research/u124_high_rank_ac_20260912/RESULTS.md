# Fixed-rank AC substitution search from the U124 triangle systems

Every search in this directory preserves rank. No generator removal,
Lemma 11 removal, or destabilization is generated or used for scoring.

## Move neighborhood

For distinct relators `T` and `D`, a search edge replaces only `T` by

```
T c^-1 D^epsilon c,    epsilon in {+1,-1}.
```

All cyclic rotations of `T` and `D^epsilon` are enumerated. If `p` and `q`
are the prefixes cut from `T` and `D^epsilon`, respectively, the stored
conjugator is `c = free(q p^-1)`. The resulting cyclic class is exactly the
product of the two selected rotations. Every stored suffix event is therefore
an ordinary AC normal-product substitution; `verify.py` replays it directly.

A product of two length-three relators has even reduced length, so it cannot
create a unit in one move; it can create a bigon directly. The short-macro lane
retains every direct product of maximum length three. When such a direct product
does not shorten the state, it also permits the smallest longer escape: every
two-substitution path through exactly one length-four relator that returns to
maximum relator length three.

## Results

| Experiment | Denominator | Work | Result | CPU / wall |
|---|---:|---:|---|---:|
| Generic cap-4 best-first screen | 124 | 12,400 pops; 421,261 states; 18,719,560 rotation products | 0 retained bigons or units; 14 neutral score changes | 397.728 / 399.149 s |
| Exhaustive short-macro closure, instrumented | 124 | 658 states; 11,044,416 rotation products | 0 generated bigons, units, or terminals; 16 neutral score changes | 83.599 / 83.733 s |
| Focused continuation, cap 4, historical | aca_78, aca_80 | 500 pops per row; 44,028 states | 0 retained bigons or units | 35.133 / 35.203 s |
| Focused continuation, cap 5, instrumented | aca_78, aca_80 | 500 pops per row; 57,643 states | 0 generated bigons, units, or terminals | 42.840 / 42.898 s |

The short-macro closure is exhaustive for its finite declared neighborhood:
all 124 queues emptied, no row hit the 100-pop limit, and the largest component
had 72 states. It is not an exhaustive search of the infinite AC graph.
`all124_macro_v2_p100.json` pins the instrumented wrapper SHA-256
`366cc39a...`; its frozen search-engine dependency is `high_rank_ac_search.py`
at SHA-256 `d3e9ec72...`. The
seven generic panel files preserve exact replayable paths and timing records,
but their earlier executed runner snapshot was not retained; their recorded
script hash therefore cannot currently be reproduced from a saved source file.

The 16 neutral changes keep every relator at length three. Two of them,
`aca_78` and `aca_80`, produce a generator of global degree one, which motivated
the focused continuations. Neither focused search produced a length-two or
length-one relator. None of these negative bounded results is an obstruction to
AC triviality or evidence of a counterexample.

## Verification

`high_rank_ac_search_checks.py` checks the rotation-to-conjugator formula,
complete one-step generation under a declared cap, strict pop budgeting, the
shared-digram lookahead, the final-pop terminal case, and a planted two-donor
triangle slide. The independent `verify_results.py` pass checks all 124 generic
suffixes, all 124 macro suffixes, both focused continuations, fixed rank and
generator set at every event, and the absence of any event other than
`normal_product_substitution`. It also checks that the instrumented macro and
cap-5 runs generated no unit, bigon, or terminal state, including children that
were not retained by the heap.

The Python implementation spends most of its time enumerating equivalent
rotation products. A materially deeper campaign should first port this
high-rank neighborhood to packed words and index matching boundary segments.
