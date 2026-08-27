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
| \(H^\circ_{20}\) | \(+cTctctcTTTcttc\) | `cTctctcTTTcttc` | 0 | 5 | \(\le d+5\) | bound permits increase |
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

## Not available from the displayed proof slice

| Entries | Status |
|---|---|
| \(H^\circ_{00},H^\circ_{01},H^\circ_{02},H^\circ_{03}\) | No explicit monomial expansion appears in (3.55) or (3.70)--(3.74). |
| \(H^\circ_{10},H^\circ_{11},H^\circ_{12},H^\circ_{13}\) | No explicit monomial expansion appears in (3.55) or (3.70)--(3.74). |

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
