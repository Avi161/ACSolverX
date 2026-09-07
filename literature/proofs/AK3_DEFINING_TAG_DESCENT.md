# A one-occurrence added relator does not enlarge AK3 reachability

## Scope

Work in the free group $F(x,y,t)$, with a fixed designated third relator.
An elementary relator AC move in this note is inversion, multiplication by
another relator or its inverse on either side, conjugation, or interchange
of the first two rows. There are no ambient basis changes, further
stabilizations, or interchanges involving the designated third row.

The condition below concerns the freely and cyclically reduced third row
at **every vertex** of the path. It is stronger than exponent sum one and
is not replaced by algebraic primitivity.

**Theorem.** Suppose an AC path from $(a,b,t)$ to $(a',b',t)$ has
$a,b,a',b'\in F(x,y)$, and at every vertex its designated third row is
conjugate to a word with exactly one occurrence of $t^{\pm1}$. Then there
is an ordinary rank-two AC path from $(a,b)$ to $(a',b')$.

For the initial pair $(\mathtt{xxxYYYY},\mathtt{xyxYXY})$ and endpoint
$(x,y)$ this says that such a stabilized AK3 trivialization would already
give an ordinary AK3 trivialization. It does not assert that either path
exists, that all primitive tags satisfy the hypothesis, or that arbitrary
stabilizations can be eliminated.

## The defining substitution

Write a qualifying third row in the form

\[
r={}^u(tc)^\varepsilon,
\qquad c\in F(x,y),\quad\varepsilon\in\{1,-1\},
\]

where ${}^u w=uwu^{-1}$ and $u$ may contain $t$. Define
$\theta_c:F(x,y,t)\to F(x,y)$ by fixing $x,y$ and setting
$\theta_c(t)=c^{-1}$. Its kernel is the normal closure of $r$.
The word $c$ is determined by that normal closure: equality with the normal
closure of $td$ implies, after applying $\theta_c$, that $c^{-1}d=1$.
Thus the projected pair $(\theta_c(R_1),\theta_c(R_2))$ is unambiguous.

Any AC move on the first two rows projects to an AC move. Donations from
the third row project to the identity operation, and conjugating words
are simply evaluated under $\theta_c$. Inversion or conjugation of the
third row preserves its normal closure, hence preserves $c$ and the
projected pair.

## Changing the defining row by a live base donor

Consider first a multiplication

\[
r'=rR_j={}^v(td)^\eta,
\qquad k=c^{-1}d,
\]

where $j$ is one of the first two row indices. Evaluating
$R_j=r^{-1}r'$ under the old and new substitutions gives the exact free
identities

\[
\theta_c(R_j)={} ^{\theta_c(v)}k^\eta,
\qquad
\theta_d(R_j)={} ^{\theta_d(u)}k^\varepsilon.
\]

Indeed, $\theta_c(r)=1$, $\theta_c(td)=c^{-1}d=k$,
$\theta_d(r')=1$, and $\theta_d(tc)=d^{-1}c=k^{-1}$.
Both projected donor rows are therefore conjugates of $k$ or $k^{-1}$,
even when the tag sign changes or the conjugating tails contain $t$.

Conjugate and, if necessary, invert the old projected row $j$ to make it
exactly $k$. Keep that live row fixed while changing the other projected
row. This can be done by a finite sequence of actual donations, not just
by appealing to equality in a quotient. Read the original other row
letter by letter and change its $\theta_c$-image blocks to their
$\theta_d$-images. Only $t,T=t^{-1}$ require changes:

\[
\begin{array}{c|c|c|c}
\text{letter}&\text{old block}&\text{new block}&\text{left multiplier}\\\hline
t&c^{-1}&d^{-1}=k^{-1}c^{-1}&k^{-1}\\
T&c&d=ck&{}^c k.
\end{array}
\]

At a current prefix $p\in F(x,y)$, use the displayed multiplier conjugated
by $p$. For example, replacing the local block $c$ by $ck$ is obtained by
left-donating ${}^{pc}k$ to the whole row. Conjugate/invert the donor as
needed and restore it after each donation. There is no self-donation:
only the row other than $j$ is changed during this stage. Free reduction
does not affect these identities; prefixes can be computed from the
unreduced block expression and then reduced.

The other row is now exactly its $\theta_d$-image. Conjugate/invert row
$j$ from $k$ to ${}^{\theta_d(u)}k^\varepsilon$, its required new value.
If $k=1$, then $c=d$, both projections coincide, and no correction is
necessary.

For a left multiplication $r'=R_jr$, applying the two substitutions gives
the same two donor formulas, since the appropriate tag evaluates to one.
For multiplication by $R_j^{-1}$, invert that base row first, use the
reviewed case, and invert it back. These inserted inversions leave the
designated tag unchanged, so they preserve the hypothesis.

## Concatenation and verification boundary

Apply the preceding finite projected transitions to every elementary
move. At each endpoint the tag is $t$, so $c=1$; the original and final
base rows are $t$-free. Their projections are therefore the stated
rank-two endpoints. Concatenation proves the theorem.

The focused test
`tests/stable_ac/test_ak3_defining_tag_descent.py` checks literal donor
identities, sign changes, conjugating tails involving $t$, and per-letter
corrections with a restored donor. It is a check of these formulas, not
an enumeration of AK3 paths or a proof of their existence.

This closes the one-occurrence mechanism only. A path can leave the
hypothesis by changing the designated row so that its cyclic reduction
has zero or multiple $t$-occurrences, by exchanging its role with another
row, or by using operations outside the stated move set. No lower bound
for those paths and no stable or ordinary AK3 resolution is claimed.
