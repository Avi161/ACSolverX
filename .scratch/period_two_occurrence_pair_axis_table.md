# Verified paired-occurrence axis ledger

This ledger is reconstructed from the sixteen pinned occurrence triples in
the period-two Hessian data.  The independent guarded checker
`.scratch/period_two_h_circ_static_expansion_checker.py` validates every
free word, cyclic block cycle, c-count, t-height, proper-power flag, and
inverse-cyclic flag against a separately pinned eight-row dictionary.  The
checker has SHA-256
`d0631658c3c3e7594613e5ff24c4f58eef1e6e35ebc151b33245f9fb2cad7eb4`
and the paired-axis digest is
`3195cf72e33b9e53e7bd3b6f3c1649e7bae5742b2414827689263ca440f293c0`.
It makes no separation, noncancellation, lift, AK(3), stable-AC, or AC
claim.

## Conventions

Occurrences are numbered in the literal order $1,\ldots,16$, with raw
quotient prefixes $q_o$.  For the indicated positive/negative pair
$[a,b]$, set

\[
 g_{[a,b]}=q_a^{-1}q_b\in Q=C_2*\mathbb Z.
\]

Words use `c` for the order-two letter and `T` for $t^{-1}$.  Free
reduction cancels `cc`, `tT`, and `Tt`.  Cyclic reduction repeatedly also
cancels inverse first/last letters.  For a cyclically reduced word containing
`c`, rotate it to

\[
 c t^{e_1}c t^{e_2}\cdots c t^{e_r};
\]

the displayed t-block cycle is $(e_1,\ldots,e_r)$, up to cyclic rotation.
For a pure $t$-power, the convention is the singleton block cycle.  The
c-count is the number of `c` letters in the cyclically reduced word and the
t-height is the sum of its block exponents.  “Proper power” means a proper
power in $Q$, read here from the cyclic normal form.  “Inverse cyclic”
means cyclic equivalence in $Q$ to the inverse cyclic word, not merely an
equality of total t-height.

## Exact reductions

| paired interval | freely reduced $g_{[a,b]}$ | cyclically reduced representative | t-block cycle | c-count | t-height | proper power? | inverse cyclic? |
|---|---|---|---:|---:|---:|---|---|
| $[3,4]$ | `cTctcTTTcttc` | `ctcTTTct` | $(1,-3,1)$ | 3 | -1 | no | no |
| $[7,8]$ | `cTctcTTTcttc` | `ctcTTTct` | $(1,-3,1)$ | 3 | -1 | no | no |
| $[11,12]$ | `cTctcTTTcttc` | `ctcTTTct` | $(1,-3,1)$ | 3 | -1 | no | no |
| $[2,5]$ | `cTctcTctt` | `cTctcTctt` | $(-1,1,-1,2)$ | 4 | 1 | no | no |
| $[10,13]$ | `cTctcTctt` | `cTctcTctt` | $(-1,1,-1,2)$ | 4 | 1 | no | no |
| $[1,6]$ | `ctcTcTctc` | `cTcTctt` | $(-1,-1,2)$ | 3 | 0 | no | no |
| $[9,14]$ | `TTcttcTct` | `cttcTcT` | $(2,-1,-1)$ | 3 | 0 | no | no |
| $[15,16]$ | `T` | `T` | $(-1)$ | 0 | -1 | no | no |

For example, the first entry is

\[
q_3^{-1}q_4=(tc)^{-1}(ctcTTTcttc)
=\texttt{cTctcTTTcttc},
\]

whose cyclic endpoint cancellations give `ctcTTTct`.  The two nontrivial
forest-edge axes $[1,6]$ and $[9,14]$ have respectively the cycles
$(-1,-1,2)$ and $(2,-1,-1)$; these are rotations after choosing a
`c`-initial representative.  This records word-level normal forms only.
