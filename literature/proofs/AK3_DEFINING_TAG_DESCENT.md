# A one-occurrence added relator does not enlarge AK3 reachability

## Scope

Work in the free group $F(x,y,t)$, with the extra generator $t$ fixed.
An elementary relator AC move in this note is inversion, multiplication by
another relator or its inverse on either side, conjugation, or interchange
of any two rows. There are no ambient basis changes or further
stabilizations.

The condition below requires at least one qualifying row at **every vertex**
of the path; its index may change. It is stronger than exponent sum one and
is not replaced by algebraic primitivity.

**Theorem.** Suppose an AC path from $(a,b,t)$ to $(a',b',t)$ has
$a,b,a',b'\in F(x,y)$, and at every vertex at least one of its rows is
conjugate to a word with exactly one occurrence of $t^{\pm1}$. Then there
is an ordinary rank-two AC path from $(a,b)$ to $(a',b')$.

For the initial pair $(\mathtt{xxxYYYY},\mathtt{xyxYXY})$ and endpoint
$(x,y)$ this says that such a stabilized AK3 trivialization would already
give an ordinary AK3 trivialization. It does not assert that either path
exists, that all primitive tags satisfy the hypothesis, or that arbitrary
stabilizations can be eliminated.

## The defining substitution

Temporarily designate a qualifying row as the third row and write it in the form

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

## Changing the anchor without changing the tuple

Suppose two rows qualify in the same tuple, ordered as

\[
(R,r,s),\qquad r={}^u(tc)^\varepsilon,\quad
s={}^v(td)^\eta,\quad k=c^{-1}d.
\]

Eliminating $r$ or $s$ gives respectively

\[
\bigl(\theta_c(R),{}^{\theta_c(v)}k^\eta\bigr),
\qquad
\bigl(\theta_d(R),{}^{\theta_d(u)}k^{-\varepsilon}\bigr).
\]

Normalize the second row of the first pair to $k$. The same per-letter
donations proved above change the first row to $\theta_d(R)$, while
restoring the donor after every use. Then conjugate and invert that donor
to the second row of the second pair. The sign is $-\varepsilon$, since
$\theta_d(tc)=d^{-1}c=k^{-1}$. If $k=1$, the two substitutions coincide
and both second rows are trivial. Thus different qualifying anchors
define the same ordinary AC class, up to permutation of the retained rows.

## Concatenation and verification boundary

For any elementary move other than a permutation, only one row changes.
If an unchanged row qualifies, use it as the anchor at both ends and
project the move directly. Otherwise, the every-vertex hypothesis forces
the changed row to qualify at both ends; apply the defining-row transition
proved above. A permutation transports the anchor and merely permutes the
retained rows. At shared vertices, the anchor-change argument connects
the choices made for successive edges by ordinary rank-two AC moves.

At each endpoint choose the row $t$, so $c=1$; the original and final
base rows are $t$-free. Their projections are therefore the stated
rank-two endpoints. Concatenation proves the theorem.

The focused test
`tests/stable_ac/test_ak3_defining_tag_descent.py` checks literal donor
identities, sign changes, anchor handoffs, conjugating tails involving $t$, and per-letter
corrections with a restored donor. It is a check of these formulas, not
an enumeration of AK3 paths or a proof of their existence.

This closes the one-occurrence mechanism only. A path can leave the
hypothesis at a vertex where all three cyclically reduced rows have zero
or multiple $t$-occurrences, or by using operations outside the stated move
set. Changing which qualifying row serves as anchor is covered. No lower bound
for those paths and no stable or ordinary AK3 resolution is claimed.

## Application to the two-live-row MMS02 gate

The same argument has a rank-one relative version. Let $G$ be any group.
If a relator AC path from $(g,t)$ to $(h,t)$ in $G*\langle t\rangle$
has, at every vertex, some row conjugate to $(tc)^{\pm1}$ with $c\in G$,
then $g$ is conjugate in $G$ to $h$ or $h^{-1}$. Here again the generator
$t$ is fixed and no ambient automorphisms or further stabilizations are
allowed.

Indeed, the retraction $\theta_c$ fixing $G$ and sending $t$ to $c^{-1}$
has kernel the normal closure of $tc$, for arbitrary $G$. All displayed
donor and overlap identities remain valid. There is now just one retained
row, so no other row needs per-letter transport: normalize its old value
to $k$, then restore its required new conjugate or inverse. When the anchor
does not change, the retained row is only conjugated or inverted, or
receives an identity donation. The same edge dichotomy and handoffs
therefore concatenate to conjugation/inversion of a single element of $G$.
No freeness or torsion-free assumption on $G$ is used.

Apply this to $G=Q_A$ and the gate $(q,t)\longrightarrow(B,t)$ in
[Section 6.18 of the MMS02 bridge](AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md#618-the-tagged-coefficient-can-be-removed-exactly).
Theorem 6.11 there excludes conjugacy of $q$ and $B$. Its height map,
also recorded in (117) and (507), has $\chi(q)=\chi(B)=-1$, excluding
conjugacy of $q$ with $B^{-1}$ as well. Consequently every successful
path in this relative gate has a vertex where **neither live row** is
conjugate to $(tc)^{\pm1}$ for any $c\in Q_A$.

Qualification here is tested in the actual free product
$Q_A*\langle t\rangle$, not on raw free-word representatives before
quotienting. The allowed restored $A,v$-donation macros project to identity
steps and cannot evade the conclusion. There is no bound on the number
of moves inside the qualifying region. Paths leaving that region, paths
changing the fixed base donors, the unrestricted MMS02 bridge, and stable
or ordinary AK3 remain undecided.
