# Dependency audit for the period-two proof tail

## Scope and result

This is an independent dependency and finite-ledger audit of Sections
3.61--3.106a of
`AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md`.  It checks theorem
dependencies, scope gates, finite literal tables, and word reductions.  It
does not replace the proofs, evaluate the four remaining terms in the
six-term remote ledger, or assert a class-two obstruction.

The requested proof-tail core is Sections 3.61--3.105.  Sections
3.106--3.106a are included only as downstream packaging and one finite
color-cut evaluation; they are not used as support for any conclusion in
the requested core.

The original two read-only reviews split the range at Section 3.84 and
required formal remote quantifiers in Sections 3.100--3.101.  A fresh hostile
review on 30 August split the range again.  It approved Sections 3.61--3.84
but found one major scope promotion in the upper tail: the cell-relative
endpoint localization of Section 3.77 had been used as a support-independent
multiplier alphabet for every edge of the complete graph $G_u$.  Sections
3.84--3.85 and 3.92--3.95 now retain actual edge-dependent multiplier
families.  Equation (3.633) is cycle-specific on the complete graph, while
the uniform $B_*|C|$ refinement is explicitly conditional on endpoint
localization.  Independent re-review approved the correction and confirmed
that (3.624), (3.627), (3.630), (3.632), (3.639), and the six-term identity
remain valid.  A further independent forward-reference pass found that
Section 3.99 had re-promoted its endpoint schema when describing clustered
fixed loops.  That sentence and its downstream summary are now explicitly
limited to one endpoint-localized alphabet; general three-source loops retain
their actual edge-dependent lists.  This third checkpoint exhausts the
convergence budget and freezes the bounded-depth theorem with four
unevaluated terms.

## Dependency ledger

| Range | Primary antecedents | Audited conclusion |
| --- | --- | --- |
| 3.61--3.67 | paired-axis words and primitivity; free-tree geometry; balanced occurrence relation; malnormality; marked source map | Cross-slot geometry, collision-cycle closure, finite marked grammar, semilinear gates, and the torsion-template pullback are correctly conditional. |
| 3.68--3.75 | even finite source graph; two-tree forest theorem; finite boundary injectivity; quasi-isometry and tree Morse bounds; tied-bundle charge | Matching removal, unique Green filling, radius transfer, cell decomposition, leading-support separation, and anchored cells have no circular dependence. |
| 3.76--3.83 | literal chronology; terminal localization; remote multiplier rigidity; integral anchored lift; free-coordinate correlation; centralizer theorem | The finite endpoint germ, order-free baseline, target-incident branches, and other-cell corridors retain their stated finite/remote hypotheses and make no survival claim. |
| 3.84--3.92 | three-source double-coset equation; fixed-multiplier branch injectivity; height and anti-height quotients; free-group unique roots; cyclic centralizers | Each fixed actual branch telescopes as stated.  The number of multiplier families and the local degree of their union are source-dependent; every loop sieve is applied to a fixed actual list. |
| 3.93--3.98 | branch normal form with edge-dependent multipliers; graph boundary identity; target-word conjugacy; balanced polarization; affine cutoff | The graph-boundary plus odd-cycle split and frozen six-term ledger are exhaustive.  Odd height, conjugacy closure, and the power corridor are global; the uniform translation constant is only endpoint-localized.  No term parity is inferred. |
| 3.99--3.106a | terminal localization and remote rigidity; literal occurrence prefixes; four-state action; anchored source pair; Green half-tree formula; integral free-coordinate correlation | The canonical schema is finite only for the endpoint-localized cell class; general mixed loops retain actual edge-dependent multipliers.  Within that scope, the endpoint bipartite/chord forms, state filter, prefix shadows, and direct-shadow Green cut retain their remote/extremal hypotheses.  The balanced color cut is exactly evaluated by ten complete finite tables and the literal double-coset normal form, with no seventh residual category. |

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
$ /Users/avigyapaudel/.local/bin/python3.11 \
  scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  env UV_CACHE_DIR=.scratch/uv-cache PYTHONPYCACHEPREFIX=.scratch/pycache \
  uv run --with pytest python3 -m pytest -q \
  tests/stable_ac/test_ak_depth_four_period_two_full_lift_tail.py
...                                                                      [100%]
3 passed in 1.08s
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

The audit certifies the corrected dependency graph and the finite inputs
listed above.  Section 3.106a computes the existing color-cut term
$\mathcal C$ as one finite parity output; it does not prove that output
vanishes.  The audit does not compute
$\overline\kappa,\mathcal S,\mathcal T,\mathcal O$, prove
$[\Theta(F)]\ne0$ for arbitrary balanced $F$, solve the literal higher
lifting equation, classify all quotient solutions, prove the MMS02 bridge,
or prove stable or ordinary AK(3).  The three-checkpoint budget is exhausted:
this ledger is frozen as a publishable bounded-depth theorem, and only
soundness corrections or packaging changes remain in scope.
