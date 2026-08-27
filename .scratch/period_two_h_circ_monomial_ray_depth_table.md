# Static \(\mathbf H^\circ\) monomial and left-ray-depth ledger

Status: **[unverified]** mechanical transcription for the next filtration
audit; no theorem in the proof note depends on this table.

This is a source transcription of (3.55) and (3.70)--(3.74) in
`literature/proofs/AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md`, using the
pinned literal occurrence actions in
`experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py`.
It is not a computation and makes no noncancellation, lift, AC, or stable-AC
claim.

Conventions: words are reduced words of \(Q=C_2*\mathbb Z\), `T` means
\(t^{-1}\), \(\nu_t\) is the t-height, and \(c(m)\) is the number of
\(c\)-syllables in the displayed reduced word.  If a normalized left
\(t\)-ray has depth \(d\), direct free-product reduction gives the safe
one-sided estimate

\[
 \operatorname{dep}(m\mathcal O)\le d+c(m).
\]

Removing an initial \(t\)-power and applying the endpoint \(H\)-normalization
can only lower the c-syllable count.  The estimate is deliberately only a
support bound: it neither proves that the bound is attained nor relates a
term's left ray to the target ray of a full bilinear bucket.

## Derived nonzero monomials

| Entry | Signed monomial \(a m\) | reduced \(m\) | \(\nu_t(m)\) | \(c(m)\) | safe left-ray bound | static reading |
|---|---:|---|---:|---:|---|---|
| \(H^\circ_{04}\) | \(+c\) | `c` | 0 | 1 | \(\le d+1\) | bound permits increase |
| \(H^\circ_{04}\) | \(-cTTctttcTct\) | `cTTctttcTct` | 1 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{04}\) | \(+cTctctcTct\) | `cTctctcTct` | 1 | 5 | \(\le d+5\) | bound permits increase |
| \(H^\circ_{04}\) | \(-cTTcttttcTct\) | `cTTcttttcTct` | 2 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{04}\) | \(+cTctcTct\) | `cTctcTct` | 0 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{04}\) | \(-cTTcttct\) | `cTTcttct` | 1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{14}\) | \(+c\) | `c` | 0 | 1 | \(\le d+1\) | bound permits increase |
| \(H^\circ_{14}\) | \(-TTctcTct\) | `TTctcTct` | -1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{14}\) | \(+cTctcTct\) | `cTctcTct` | 0 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{14}\) | \(-T\) | `T` | -1 | 0 | \(\le d\) | can preserve; no increase by this bound |
| \(H^\circ_{20}\) | \(-1\) | `1` | 0 | 0 | \(\le d\) | can preserve; no increase by this bound |
| \(H^\circ_{20}\) | \(+cTctcTTTcttc\) | `cTctcTTTcttc` | -1 | 5 | \(\le d+5\) | bound permits increase |
| \(H^\circ_{20}\) | \(-cTcttc\) | `cTcttc` | 1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{20}\) | \(+cTctctcTTTcttc\) | `cTctctcTTTcttc` | 0 | 6 | \(\le d+6\) | bound permits increase |
| \(H^\circ_{21}\) | \(-cTcttc\) | `cTcttc` | 1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{21}\) | \(+cTctctcTctt\) | `cTctctcTctt` | 2 | 5 | \(\le d+5\) | bound permits increase |
| \(H^\circ_{23}\) | \(-cTctcTctt\) | `cTctcTctt` | 1 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{23}\) | \(+cTctctcTct\) | `cTctctcTct` | 1 | 5 | \(\le d+5\) | bound permits increase |
| \(H^\circ_{24}\) | \(+1\) | `1` | 0 | 0 | \(\le d\) | can preserve; no increase by this bound |
| \(H^\circ_{24}\) | \(-cTctctcTct\) | `cTctctcTct` | 1 | 5 | \(\le d+5\) | bound permits increase |
| \(H^\circ_{30}\) | \(-TTcttcTctc\) | `TTcttcTctc` | 0 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{30}\) | \(+TTcTcttc\) | `TTcTcttc` | -1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{30}\) | \(-TTctcTctc\) | `TTctcTctc` | -1 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{30}\) | \(+TTcTTcttc\) | `TTcTTcttc` | -2 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{31}\) | \(-TTcttcTctc\) | `TTcttcTctc` | 0 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{31}\) | \(+TTctctt\) | `TTctctt` | 1 | 2 | \(\le d+2\) | bound permits increase |
| \(H^\circ_{32}\) | \(-TTcttcTc\) | `TTcttcTc` | -1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{32}\) | \(+TTctcTctc\) | `TTctcTctc` | -1 | 4 | \(\le d+4\) | bound permits increase |
| \(H^\circ_{34}\) | \(+TTcttcTc\) | `TTcttcTc` | -1 | 3 | \(\le d+3\) | bound permits increase |
| \(H^\circ_{34}\) | \(-1\) | `1` | 0 | 0 | \(\le d\) | can preserve; no increase by this bound |

The slot-four entries in the first ten rows use (3.55), which survives the
second gauge because \(Q^{\mathrm{out}}_0=Q^{\mathrm{out}}_1=0\).  The
remaining entries are the direct expansions in (3.72); the zero entries are
\(H^\circ_{22}=H^\circ_{33}=0\) and row four is zero by (3.73).

## [unverified] Derived rows zero and one, columns zero through three

These entries are not printed in (3.72), but follow directly from (3.40)
and the pinned 16 occurrences.  For every row below, the displayed integral
coefficient already combines identical reduced words.  The compact
parenthetical annotations are \((\nu_t,c)\).  A term with c-count \(c\)
has the same safe left-ray bound \(\operatorname{dep}(m\mathcal O)\le d+c\)
used above.

| Entry | [unverified] signed reduced monomials \(a\,m\), each annotated \((\nu_t(m),c(m))\) |
|---|---|
| \(H^\circ_{00}\) | \(+3\cdot1\) \((0,0)\); \(-3\cdot\texttt{cTctcTTTcttc}\) \((-1,5)\); \(+\texttt{cTctcTcTctc}\) \((-1,6)\); \(-\texttt{cTctcTTTTcttc}\) \((-2,5)\); \(+\texttt{cTctcTctc}\) \((0,5)\); \(-\texttt{cTcTTcttc}\) \((-1,4)\); \(-\texttt{cTTcttcTctc}\) \((0,5)\); \(+\texttt{cTTcTcttc}\) \((-1,4)\); \(-\texttt{cTTcttctc}\) \((1,4)\); \(+\texttt{cTTctttcTTTcttc}\) \((0,5)\); \(+\texttt{cTcttc}\) \((1,3)\); \(-\texttt{cTctctcTTTcttc}\) \((0,6)\); \(-\texttt{cTTctttctc}\) \((2,4)\); \(+\texttt{cTTcttttcTTTcttc}\) \((1,5)\) |
| \(H^\circ_{01}\) | \(-2\cdot\texttt{cTctcTctt}\) \((1,4)\); \(+\texttt{cTctcTctc}\) \((0,5)\); \(-\texttt{ct}\) \((1,1)\); \(+2\cdot\texttt{cTTcttctt}\) \((2,3)\); \(-\texttt{cTTcttctc}\) \((1,4)\); \(+\texttt{cTTctttcTctt}\) \((2,4)\); \(+\texttt{cTcttc}\) \((1,3)\); \(-\texttt{cTctctcTctt}\) \((2,5)\); \(-\texttt{cTTctttctc}\) \((2,4)\); \(+\texttt{cTTcttttcTctt}\) \((3,4)\) |
| \(H^\circ_{02}\) | \(-\texttt{cTctcTcTctc}\) \((-1,6)\); \(+\texttt{cTTcttcTctc}\) \((0,5)\) |
| \(H^\circ_{03}\) | \(+\texttt{cTctcTTctt}\) \((0,4)\); \(-\texttt{c}\) \((0,1)\); \(-\texttt{cTTctctt}\) \((1,3)\); \(+\texttt{cTTctttcTct}\) \((1,4)\); \(+\texttt{cTctcTctt}\) \((1,4)\); \(-\texttt{cTctctcTct}\) \((1,5)\); \(-\texttt{cTTcttctt}\) \((2,3)\); \(+\texttt{cTTcttttcTct}\) \((2,4)\); \(-\texttt{cTctcTct}\) \((0,4)\); \(+\texttt{cTTcttct}\) \((1,3)\) |
| \(H^\circ_{10}\) | \(+2\cdot1\) \((0,0)\); \(-2\cdot\texttt{cTctcTTTcttc}\) \((-1,5)\); \(+\texttt{cTctcTcTctc}\) \((-1,6)\); \(-\texttt{cTctcTTTTcttc}\) \((-2,5)\); \(+\texttt{cTctcTctc}\) \((0,5)\); \(-\texttt{cTcTTcttc}\) \((-1,4)\); \(-\texttt{TTTctc}\) \((-2,2)\); \(+\texttt{TTcTTTcttc}\) \((-3,3)\); \(-\texttt{Tc}\) \((-1,1)\); \(+\texttt{TTctcTTTcttc}\) \((-2,4)\) |
| \(H^\circ_{11}\) | \(+2\cdot1\) \((0,0)\); \(-2\cdot\texttt{cTctcTctt}\) \((1,4)\); \(+\texttt{cTctcTctc}\) \((0,5)\); \(-\texttt{ct}\) \((1,1)\); \(-\texttt{Tc}\) \((-1,1)\); \(+\texttt{TTctcTctt}\) \((0,3)\) |
| \(H^\circ_{12}\) | \(-\texttt{cTctcTcTctc}\) \((-1,6)\); \(+\texttt{TTTctc}\) \((-2,2)\) |
| \(H^\circ_{13}\) | \(+\texttt{cTctcTTctt}\) \((0,4)\); \(-\texttt{c}\) \((0,1)\); \(-\texttt{TTcTctt}\) \((-1,2)\); \(+\texttt{TTctcTct}\) \((-1,3)\); \(-\texttt{cTctcTct}\) \((0,4)\); \(+\texttt{T}\) \((-1,0)\) |

The raw chronological pairs retained before reduction are, respectively,
\((3,4),(3,7),(3,8),(3,11),(3,12),(4,7),(4,8),(4,11),(4,12),
(7,8),(7,11),(7,12),(8,11),(8,12),(11,12)\) for \(H^\circ_{00}\),
and all ordered cross-slot pairs \(o<p\) prescribed by (3.40) for the
remaining entries.  The diagonal constants are \(n_0=3\) and \(n_1=2\).
This paragraph records the derivation route, not an executed verification.

## [unverified] c-count-zero candidates across the full displayed \(\mathbf H^\circ\) matrix

These are the only c-count-zero monomials in the entries derived above and
in the already displayed rows two and three; row four vanishes.  They are
candidates for depth preservation under the coarse bound only.

| Entry | signed pure \(t\)-power monomial | \(\nu_t\) | bound |
|---|---:|---:|---|
| \(H^\circ_{00}\) | \(+3\cdot1\) | 0 | \(\le d\) |
| \(H^\circ_{10}\) | \(+2\cdot1\) | 0 | \(\le d\) |
| \(H^\circ_{11}\) | \(+2\cdot1\) | 0 | \(\le d\) |
| \(H^\circ_{13}\) | \(+T\) | -1 | \(\le d\) |
| \(H^\circ_{14}\) | \(-T\) | -1 | \(\le d\) |
| \(H^\circ_{20}\) | \(-1\) | 0 | \(\le d\) |
| \(H^\circ_{24}\) | \(+1\) | 0 | \(\le d\) |
| \(H^\circ_{34}\) | \(-1\) | 0 | \(\le d\) |

## Maximal-terminal-ray audit boundary

For the displayed non-slot-four columns (columns \(0\) through \(3\)) in
rows two and three, `1` occurs in \(H^\circ_{20}\) and
\(H^\circ_{34}\).  Those monomials have c-syllable bound zero and therefore
can preserve a maximal terminal-ray depth.  Every other displayed
non-slot-four monomial has positive c-syllable bound, so this coarse bound
permits an increase of up to the number shown in the table.

That is only a syntactic warning, not evidence that such an increase occurs
in a Hessian contribution.  The rows-zero-and-one non-slot-four expansions
are not available in the cited displayed formulas, and neither the height
nor this left-multiplier bound controls collisions, the Green-flow support,
the target bucket, or the affine unary term.  In particular, the table does
not establish a leading-term or maximal-ray separation statement.
