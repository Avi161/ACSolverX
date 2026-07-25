# Direct stable theory beyond the two-hop CoV null

Date: 2026-07-24

## Proven result 1: dual-source compression

The theorem in

```text
literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md
```

allows two stabilizing relations \(z^{-1}w_z,t^{-1}w_t\) to compress both
source relators before either old generator is removed.  A triangular pair
of unique-occurrence equations removes the two old generators in order.
More generally, if the two compressed source relators form a primitive pair
in \(F_4\), a proved rank-\(n\) stable ambient automorphism straightens and
removes them; the quotient pair is well-defined up to Aut(\(F_2\)).

The exact AK(3) data

```text
w_z = X
w_t = Xy
I_R = TZxYYY
I_S = TZtxYX
```

give

```text
y = XTZtx
x = TZZZtzt
```

and the stable endpoint

```text
XYXYxxxy | YYXYxxYXyxy
```

with complete Whitehead representative

```text
YYXXXyx | YYXXXYxyX
```

of total length 16.  The exact identities, both eliminations, endpoint, and
Aut-floor are pinned by
`tests/stable_ac/test_dual_source_compression.py`.

This is a new stable corridor, not a trivialization.

## Proven result 2: arbitrary relative conjugators

At the one-stabilization compression root, write

```text
A = xxxzXXXXZ
B = ZxzxZ
```

The theorem in

```text
literature/proofs/AK3_ARBITRARY_CONJUGATOR_PRIMITIVE_BARRIER.md
```

proves that no target

\[
 A cB^{\pm1}c^{-1}
 \quad\text{or}\quad
 B cA^{\pm1}c^{-1},
 \qquad c\in F(x,z),
\]

is primitive.

The proof is not a bounded conjugator census.  A Cayley-tree axis lemma
reduces the minimum over every relative conjugator to a finite product of
cyclic rotations.  All four signed cases have minimum cyclic length 10.
Their abelianization slopes are \(\pm(1,-1)\) or \(\pm(3,-1)\), while the
rank-two primitive-word classification would force lengths 2 or 4.

Thus no one arbitrary-conjugator multiplication from this compression orbit
creates the decisive primitive-relator shortcut.  The exact rotation table
is pinned by
`tests/stable_ac/test_arbitrary_conjugator_primitive_barrier.py`.

This remains local in the number of multiplications.  It does not bound the
Aut-floor of every child and is not a stable-AC obstruction.

## Proven result 3: an infinite twist family is pure gauge

At the same compression root, put \(v=zxz^{-1}\).  For arbitrary
\(p,q\in\mathbb Z\) and \(\epsilon\in\{+1,-1\}\), adjoin

\[
 t=x^pv^\epsilon x^q
\]

by reverse substitution-and-removal.  For \(\epsilon=+1\), compressing the
two source relators and eliminating \(z\) gives

\[
\begin{aligned}
 C_{p,q}&=x^3(x^qt^{-1}x^p)^4,\\
 E_{p,q}&=t^{-1}xtxt^{-1}x^{p+q-1}.
\end{aligned}
\]

After \(t\mapsto y\), the automorphism

\[
 x\mapsto x,\qquad y\mapsto x^pyx^q
\]

sends \(C_{p,q}\) literally to the first AK(3) relator and sends
\(E_{p,q}\) to a conjugate of a cyclic rotation of the second.  Thus the
positive family is a stable self-loop.  The negative family has an analogous
literal formula under \(y\mapsto x^py^{-1}x^q\), landing on the inverse
second relator.  Thus the entire signed two-parameter family has Aut-floor
\(13\).
The symbolic proof is in
`literature/proofs/AK3_TWIST_GAUGE_COLLAPSE.md`; its literal identities are
pinned by `tests/stable_ac/test_twist_gauge_collapse.py`.

This rules out the bare compress-and-remove corridor for every stabilizer
word in the infinite double-coset pair
\(\langle x\rangle(zxz^{-1})^{\pm1}\langle x\rangle\) as a source of orbit
escape.  There is no parameter bound in this conclusion; extra AC moves
after adjoining the same word are outside its scope.

This family is exhaustive for direct one-block elimination.  If a general
defining word \(t=w(x,v)\) permits recovery of \(v\) as a word in
\((x,t)\), then \((x,w)\) generates \(F(x,v)\) and is therefore a basis.
Nielsen's rank-two kernel theorem forces

\[
 w\in\langle x\rangle v^{\pm1}\langle x\rangle.
\]

Thus escaping this mechanism requires an intervening relator operation or
a compression that does not simply recover the old \(v\)-block in the new
basis.

## Proven result 4: power recovery via the source relator

The first non-gauge possibility is to use the power relator

\[
 x^3=v^4
\]

before recovering \(v\).  For the family \(t=v^k\), the theorem in
`literature/proofs/AK3_POWER_BEZOUT_CORRIDORS.md` gives an exact canonical
Euclidean corridor and an absolute obstruction for even \(k\).

For odd \(k\), a literal Euclidean sequence on

\[
 x^3v^{-4},\qquad t^{-1}v^k
\]

produces a one-\(v\) isolator.  After compressing
\(z^{-1}xv\) and removing \(z\), all powers with
\(|k|\equiv1\pmod4\) return to the floor-14 compression-root orbit, while
all powers with \(|k|\equiv3\pmod4\) land in the one floor-15 orbit

```text
YXXYx | YYYXYxyyyX
```

For even \(k\), recovery is impossible already in the abelianization of

\[
 \langle x,v,t\mid x^3v^{-4},t^{-1}v^k\rangle:
\]

an equality \(v=U(x,t)\) would require

\[
 3=4m+3kn,
\]

whose right side is even.  Thus no canonical Euclidean endpoint in this
unbounded family reaches floor at most \(12\).

The exact Euclidean products, endpoint identities, residue-class shears,
and two complete Aut representatives are pinned by
`tests/stable_ac/test_power_bezout_corridors.py`.

An ambient shear of the fresh generator strips arbitrary \(x\)-flanks from

\[
 t=x^pv^kx^q.
\]

Therefore the same canonical normal form applies throughout the
three-parameter family
\(\bigcup_k\langle x\rangle v^k\langle x\rangle\), not only to bare
powers.

This does not classify all recovery words.  Already for \(k=1\), replacing
the canonical \(U=t\) by the equal quotient word

\[
 U=t(t^{-4}x^3)=t^{-3}x^3
\]

is AC-realizable and yields a different endpoint of floor \(23\).  This
counterexample is pinned in the replay test.  Consequence-twisted
recoveries are therefore a live mechanism rather than part of the claimed
closure.

## Proven result 5: one infinite consequence direction

The first consequence-twisted family can also be closed without a parameter
bound.  For the \(k=1\) stabilization, compress the power relator to

\[
 R=x^3t^{-4}
\]

and let \(R'=t^{-4}x^3\) be its cyclic rotation.  Every recovery word

\[
 U_n=t(R')^n,\qquad n\in\mathbb Z,
\]

is AC-realizable before eliminating \(z\).

The symbolic Whitehead proof in
`literature/proofs/AK3_CONSEQUENCE_TWIST_FAMILY.md` gives the complete
Aut-floor

\[
 \mu(P_n)=
 \begin{cases}
 28(-n)+15,&n<0,\\
 14,&n=0,\\
 28n-5,&n>0.
 \end{cases}
\]

It checks all twelve second-kind Whitehead length changes as affine
functions of \(|n|\); none is negative.  Thus this entire infinite
direction climbs away from the compression root and never reaches floor
\(12\).  Exact endpoints and every symbolic length-change row are pinned by
`tests/stable_ac/test_consequence_twist_family.py`.

## Proven result 6: the full power-conjugated recovery direction

A mixed two-rotation consequence first produces the shorter recovery word

\[
 U_1=x^3tx^{-3}.
\]

This is not an isolated accident.  Put \(a=x^3\) and retain the compressed
power relator \(R=at^{-4}\).  For every \(m\in\mathbb Z\),

\[
 K_m=t^{-1}a^mta^{-m}
\]

is an ordered product of exactly \(2|m|\) conjugates of \(R^{\pm1}\).
Thus the entire recovery family

\[
 U_m=tK_m=a^mta^{-m}
\]

is AC-realizable before eliminating \(z\).

The proof in
`literature/proofs/AK3_CONJUGATED_RECOVERY_FAMILY.md` gives the complete
Aut-floor

\[
 \mu(P_m)=
 \begin{cases}
 3m+14,&m>0,\\
 14,&m=0,\\
 3(-m)+12,&m<0.
 \end{cases}
\]

After one parameter-dependent Nielsen shear, each endpoint has a fixed
nine-letter first relator and a second relator with one long pure
\(x\)-block.  The twelve Whitehead length changes are then symbolic:
four are \(1\), four are \(0\), and the other four are \(3m+5\) on the
positive branch or \(3|m|+3\) on the negative branch.  Hence all endpoints
are globally Aut-minimal and none reaches floor \(12\).  The exact
factorization, endpoints, floors, and symbolic table are pinned by
`tests/stable_ac/test_conjugated_recovery_family.py`.

## Proven result 7: one ordered two-parameter mixture

The two closed directions can be mixed in a fixed order.  With
\(R'=t^{-4}x^3\), define

\[
 U_{n,m}=t(R')^nK_m.
\]

For \(nm\ne0\), direct reduction exposes a corridor block \(S_n\) of
length \(7|n|\) and a power block \(x^{3m}\).  The endpoint is already
Whitehead-minimal: all twelve length changes can be counted symbolically
in the three sign regions.  The resulting floor is

\[
 \mu(P_{n,m})=28|n|+12|m|+15
 \qquad(nm\ne0).
\]

Together with the two axis theorems, this gives a complete piecewise
formula on all of \(\mathbb Z^2\), recorded in
`literature/proofs/AK3_MIXED_CONSEQUENCE_FAMILY.md`.  In particular, every
genuinely mixed endpoint has floor at least \(55\): these two consequence
directions add length rather than canceling in the displayed order.  The
two-dimensional signed replay and all-quadrant symbolic Whitehead table
are pinned by `tests/stable_ac/test_mixed_consequence_family.py`.

## Proven result 8: the reverse ordered mixture

Reversing the two blocks also admits a complete symbolic treatment.  Put

\[
 \widehat U_{n,m}=tK_m(R')^n.
\]

Off the coordinate axes, the endpoint is again already
Whitehead-minimal, but its exact floor depends on the sign quadrant:

\[
 \mu(\widehat P_{n,m})=
 \begin{cases}
 28|n|+18|m|+3,&n>0,\ m>0,\\
 28|n|+18|m|-1,&n>0,\ m<0,\\
 28|n|+18|m|+15,&n<0,\ m>0,\\
 28|n|+18|m|-13,&n<0,\ m<0.
 \end{cases}
\]

The \(n<0,m=-1\) line is a real cancellation stratum:
one middle \(x^3\)-block disappears and adjacent \(t\)-blocks merge.
Nevertheless, the smallest genuinely mixed floor is still \(33\), at
\((-1,-1)\).  The exact boundary reduction and five symbolic Whitehead
rows are proved in
`literature/proofs/AK3_REVERSE_MIXED_CONSEQUENCE_FAMILY.md` and replayed
by `tests/stable_ac/test_reverse_mixed_consequence_family.py`.

## Proven result 9: the full short recovery word equation

The consequence grammar can be removed entirely at bounded word length.
Every direct recovery is a solution of

\[
 U=t
 \quad\text{in}\quad
 \langle x,t\mid x^3=t^4\rangle.
\]

This torus-knot group is an amalgamated product of two infinite cyclic
groups.  Its central normal form gives an exact equality test.  Among all

\[
 258{,}280{,}324
\]

freely reduced words \(U\) of length at most \(17\), exactly \(40{,}503\)
represent \(t\).  The complete endpoint census proves

\[
 \mu(P(U))\ge14,
\]

with equality only for \(U=t\).  The only six endpoints of floor at most
\(23\) are already members of the proved power-conjugated or
fixed-rotation families.  Thus no unclassified short consequence syntax
hides a floor-\(12\) endpoint.

The amalgam normal-form proof and complete counts are in
`literature/proofs/AK3_RECOVERY_WORD_EQUATION_BARRIER.md`; the exact
enumerator and replay are
`experiments/stable_ac/rank3_compression/recovery_word_equation.py` and
`tests/stable_ac/test_recovery_word_equation.py`.

## Proven result 10: the arbitrary recovery word equation

The length bound can be removed.  For every freely reduced word satisfying

\[
U=t
\quad\text{in}\quad
\langle x,t\mid x^3=t^4\rangle,
\]

put \(e=xU\) and

\[
P(U)=
\left(x^3ex^{-4}e^{-1},\,t^{-1}exe^{-1}\right).
\]

The theorem in
`literature/proofs/AK3_ARBITRARY_RECOVERY_FLOOR_BARRIER.md` proves

\[
\boxed{\mu(P(U))\ge14}
\]

without a bound on \(|U|\), a consequence grammar, or an AC graph search.
The literal recovery \(U=t\) realizes equality.

The proof rewrites the endpoint as

\[
\left(X^3Y^{-4},\,T^{-1}Y\right)
\]

after an arbitrary basis automorphism, where \(Y\) is a conjugate of the
primitive word \(X\).  A free-tree axis estimate disposes of cyclic
lengths \(\|X\|\ge2\).  In the remaining length-one case, the amalgam
centralizers in \(\langle X,T\mid X^3=T^4\rangle\), a mod-\(4\) character,
and the integral weight \((X,T)\mapsto(4,3)\) force the second relator to
contribute at least five letters whenever the first can have length nine.

Thus arbitrary consequence twisting cannot push this direct one-source
recovery corridor below floor \(14\).  The exact endpoint rewriting,
sharpness witness, and bridge congruence are pinned by
`tests/stable_ac/test_arbitrary_recovery_floor_barrier.py`.

## Proven result 11: the whole direct recovery family is a classical self-loop

There is a stronger closure than the floor bound.  Keep the notation

\[
Y_U=(xU)x(xU)^{-1},\quad
S_U=t^{-1}Y_U,\quad
R=x^3t^{-4},\quad
A_U=x^3Y_U^{-4}.
\]

The restored and unrestored endpoints are

\[
P(U)=(A_U,S_U),\qquad Q(U)=(R,S_U).
\]

The theorem in
`literature/proofs/AK3_ARBITRARY_RECOVERY_SELF_LOOP.md` proves

\[
\boxed{
P(U)\sim_{\mathrm{AC1-3}}Q(U)
\sim_{\mathrm{AC1-3}}\operatorname{AK}(3)
}
\]

for every \(U=t\) in
\(\langle x,t\mid x^3=t^4\rangle\).

The first equivalence has an explicit four-factor certificate:

\[
A_U^{-1}R
=
\prod_{i=1}^4 t^iS_Ut^{-i}.
\]

For the second, \(U=t\) modulo the retained \(R\) implies
\(S_U=S_t\) modulo \(R\); a finite normal-closure factorization is exactly
a sequence of AC1--AC3 multiplications by conjugates of the other relator.
Finally, \(S_t\) is literally a conjugate of AK(3)'s braid relator.

Thus the direct recovery architecture does not merely fail to reach floor
\(12\): every endpoint returns to AK(3)'s classical AC class.  No unstable
ambient-automorphism principle is used.  The normal-closure diamond and
its exact identities are pinned by
`tests/stable_ac/test_arbitrary_recovery_self_loop.py`.

## Proven result 12: one arbitrary defining-relator catalyst

At the rank-three root, write

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1}.
\]

The theorem in
`literature/proofs/AK3_ONE_D_CATALYST_BARRIER.md` classifies one
multiplication targeting the future eliminator \(B\) by an arbitrarily
conjugated \(D^{\pm1}\).

A Cayley-tree bridge normal form makes the conjugator unbounded but
manageable.  If the axes are disjoint, the cyclically reduced product has
exact \(z\)-incidence

\[
\nu_z(B)+\nu_z(D)+2\nu_z(c)\ge3,
\]

so it cannot be a generator isolator.  Intersecting axes reduce to the 24
signed products of cyclic rotations.  Only four products have one
\(z^{\pm1}\), in two cyclic classes:

```text
ZTxtx
ZtxtX
```

They isolate

\[
z=t^{-1}xtx
\quad\text{or}\quad
z=txtx^{-1}.
\]

Substitution in the surviving \(D\) yields either the AK(3) braid relator
or a conjugate of it.  Since \(R\) is unchanged, both endpoints are
classically AC-equivalent to AK(3) and have complete Aut-floor \(13\).
Thus the full arbitrary-conjugator one-\(D\) catalyst is another self-loop,
not an orbit escape.  The complete 24-case residue, both substitution
identities, and both floors are pinned by
`tests/stable_ac/test_one_d_catalyst_barrier.py`.

## Live lead

The strongest remaining direct mechanism is primitive-pair compression
before either old generator is removed.  Short templates produce the
floor-16 corridor above.  A broader visible-block pass returned only to
AK(3)'s floor-13 classical class, but that finite observation remains
unverified.

The target is a hidden-cancellation or longer \(F_4\) primitive pair whose
rank-two quotient has complete Aut-floor at most 12.  A primitive full
four-relator tuple would be an immediate stable solve.  The entire
one-source mechanism which retains \(x^3=t^4\), chooses an arbitrary
quotient-equal recovery \(U=t\), and eliminates through \(z=xU\) is now
closed as a classical AC self-loop, with no word-length bound.

The remaining one-stabilization routes must leave at least one exact
hypothesis of the self-loop theorem.  The simplest one-\(D\) catalyst is
now closed even with an arbitrary conjugator when it targets the literal
\(B=z^{-1}xt\).  The next mixed one-source route is to replace \(B\) first
by an arbitrary quotient-equal \(B_U=z^{-1}xU\), then target \(B_U\) with
one \(D\)-factor.  Other routes use at least two defining-relator factors,
a changed retained relator or recovery equation, or a primitive eliminator
with several \(z\)-letters.  Using the braid relator during recovery is
another distinct option.  Dual-source primitive-pair compression before
either old generator is removed remains the broadest separate route.

AK(3) remains open.
