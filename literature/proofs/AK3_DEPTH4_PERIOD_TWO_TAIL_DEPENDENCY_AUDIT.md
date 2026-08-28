# Dependency audit for the period-two proof tail

## Scope and result

This is an independent dependency and finite-ledger audit of Sections
3.61--3.105 of
`AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md`.  It checks theorem
dependencies, scope gates, finite literal tables, and word reductions.  It
does not replace the proofs, evaluate the six-term remote ledger, or assert a
class-two obstruction.

Two separate read-only reviews split the range at Section 3.84.  Neither
review found a circular dependency, a bounded-evidence upgrade, or a formal
algebra defect.  The second review identified executable inputs in Sections
3.89, 3.92, and 3.102--3.104 and required formal remote quantifiers in
Sections 3.100--3.101.  Equation (3.658a) now states
$|u|_K>U_E$ and $u\notin\mathcal E_{s,E}$, and the finite inputs have a
focused independent replay.

## Dependency ledger

| Range | Primary antecedents | Audited conclusion |
| --- | --- | --- |
| 3.61--3.67 | paired-axis words and primitivity; free-tree geometry; balanced occurrence relation; malnormality; marked source map | Cross-slot geometry, collision-cycle closure, finite marked grammar, semilinear gates, and the torsion-template pullback are correctly conditional. |
| 3.68--3.75 | even finite source graph; two-tree forest theorem; finite boundary injectivity; quasi-isometry and tree Morse bounds; tied-bundle charge | Matching removal, unique Green filling, radius transfer, cell decomposition, leading-support separation, and anchored cells have no circular dependence. |
| 3.76--3.83 | literal chronology; terminal localization; remote multiplier rigidity; integral anchored lift; free-coordinate correlation; centralizer theorem | The finite endpoint germ, order-free baseline, target-incident branches, and other-cell corridors retain their stated finite/remote hypotheses and make no survival claim. |
| 3.84--3.92 | three-source double-coset equation; branch injectivity; height and anti-height quotients; free-group unique roots; cyclic centralizers | Branch telescopes and the loop sieve are formal once the finite paired-word height/dihedral rows are verified. |
| 3.93--3.98 | branch normal form; graph boundary identity; target-word conjugacy; balanced polarization; affine cutoff | The graph-boundary plus odd-cycle split and the frozen six-term ledger are exhaustive at the named target coordinate, but no term parity is inferred. |
| 3.99--3.105 | terminal localization and remote rigidity; literal occurrence prefixes; four-state action; anchored source pair; Green half-tree formula | The endpoint alphabet, bipartite boundary, chord form, state filter, prefix shadows, and direct-shadow Green cut are valid under the remote/extremal hypotheses now repeated in Section 3.101. |

One terminology nuance is harmless but retained: the simple-cycle
decomposition in Section 3.68 uses the multigraph convention, so a parallel
edge pair may form a two-cycle.  No later argument applies the length-three
lower bound to that graph.  The length-three bound in Section 3.98 applies
instead to the separate loopless simple graph from Section 3.93.

## Focused executable replay

The independent test
`tests/stable_ac/test_ak_depth_four_period_two_full_lift_tail.py` rebuilds
the finite inputs from the pinned residual AST and the quotient reducer.  It
checks:

1. all eight paired words in (3.445)--(3.446);
2. the complete sixteen-prefix semilinear ledger (3.247);
3. all eight marked source images in (3.469);
4. the height, anti-height, and parity data of $g_0,g_1$ used in
   (3.599), (3.617), and (3.620);
5. the complete duplicate-prefix classes (3.674) and shadow identities
   (3.675)--(3.676);
6. the sixteen four-state prefix values and both paired-generator actions
   in (3.670)--(3.671); and
7. every one of the $2^5=32$ coefficient rows in the contracted path-degree
   table (3.685).

Fresh focused output:

```text
$ UV_CACHE_DIR=.scratch/uv-cache PYTHONPYCACHEPREFIX=.scratch/pycache \
  uv run --with pytest python3 -m pytest -q \
  tests/stable_ac/test_ak_depth_four_period_two_full_lift_tail.py
...                                                                      [100%]
3 passed in 1.13s
```

The pre-existing witness, AST/operator, and source-action fixtures were also
replayed selectively:

```text
......                                                                   [100%]
6 passed, 15 deselected in 1.08s
```

Those six checks cover the quotient witness replay, the independent literal
occurrence table, reconstruction of all five signed occurrence operators,
and the six source-action classes.

## Exact audit boundary

The audit certifies dependency consistency and the finite inputs listed
above.  It does not compute
$\overline\kappa,\mathcal S,\mathcal T,\mathcal C,\mathcal O$, prove
$[\Theta(F)]\ne0$ for arbitrary balanced $F$, solve the literal higher
lifting equation, classify all quotient solutions, prove the MMS02 bridge,
or prove stable or ordinary AK(3).
