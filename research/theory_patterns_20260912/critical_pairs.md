# Certified overlap completion: tested experimental mechanism

This is a proof-producing use of the classical critical-pair construction,
not a claimed new theorem about all balanced presentations. It derives useful
multi-use donor substitutions without searching the presentation graph.

## Exact algebra

Retain a relator R. Every oriented rule L -> M records a finite list
of signs e_i in {-1,1} and words c_i satisfying the free-group identity

    L^-1 M = product_i c_i^-1 R^e_i c_i.

To replace P L Q by P M Q, append the same factors with conjugators c_i Q.
Temporarily invert/conjugate R, multiply the other relator, and restore R
after each factor. This is a sequence of ordinary AC1/AC2/AC3 operations.

Initial rules cut cyclic conjugates of R or R^-1 into L^-1 M. Suppose two
overlapping occurrences in w reduce to u and v, with ledgers A=w^-1 u and
B=w^-1 v. Further reductions give U=u C and V=v D. The exact critical
equation has ledger

    U^-1 V = C^-1 A^-1 B D.

If both endpoints have a common suffix s, removing it replaces each
conjugator c by c s^-1. A common prefix cancels without changing the ledger.
Each accepted derived rule is independently checked by expanding its ledger
and comparing freely reduced words before it can be used.

Every rule strictly decreases shortlex order (length first, then lexicographic
order). Thus reduction with any finite collected rule set terminates. The
bounded completion itself can stop at a critical-pair, rule, factor, word or
CPU limit. It does not claim confluence, completeness, a solution of the word
problem, or an AC trivialization when its output remains nonterminal.

## A checked example

For R=YXYxyx and S=XYXyy, the exponent determinant is -1. The seed rules
leave S unchanged. Completion with at most400 nontrivial critical pairs
exposes the generator X in56 elementary moves; generator elimination then
finishes at (x,y). The full path is in `critical_pairs_checks.json`.
This is a planted mechanism check, not a new hard presentation solved.

`check_critical_pairs.py` checks282 initial/derived rules,192 context
derivations,268 overlapping branches and196 replayed paths, including resource
stops and a deliberately invalid rule. All checks pass in about0.07seconds
on this local run. `ac_words.py` separately has an independent kernel audit.

## U124 development result

The preselected20-row structural panel was tested with both donor choices,
400 critical pairs per donor, a0.1CPU-second cap per donor and100 recipient
rewrite steps. This is algebraic work; no heap nodes were explored. It is not
a compute-equivalent comparison to a1,000-pop S20 run.

The procedure derived2,419 rules in0.691seconds wall/0.686seconds CPU, but
only four recipient rewrite steps were used. It produced **zero strict total
length reductions and zero certified solves**. The exact prefixes and bounds
are preserved in `critical_pairs_panel.json`. This is evidence against this
bounded fixed-donor configuration as a useful root prepass for that panel,
not a general impossibility result. It remains experimental.
