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

## Proven result 13: arbitrary recovery followed by one catalyst

The literal-\(B\) hypothesis can also be removed.  Let

\[
U=t\pmod{\langle\!\langle x^3t^{-4}\rangle\!\rangle},
\qquad
w=xU,\qquad
B_U=z^{-1}w.
\]

The theorem in
`literature/proofs/AK3_MIXED_RECOVERY_ONE_D_SELF_LOOP.md` allows one
arbitrary-relative-conjugator \(D^{\pm1}\)-multiplication to target this
arbitrary \(B_U\).

The axis bridge again removes the unrestricted conjugator.  In the
intersecting-axis residue, reducing three \(z\)-incidences to one forces the
unique \(Zz\) seam.  The two complete symbolic templates are

\[
z^{-1}t^{-1}wx,
\qquad
z^{-1}twx^{-1}.
\]

They isolate \(e_+=t^{-1}wx\) and \(e_-=twx^{-1}\).  If

\[
S_0(U)=t^{-1}wxw^{-1}
\]

is the unrestored direct endpoint, substitution in \(D\) gives the exact
free identities

\[
D[z=e_+]=t^{-1}S_0(U)t,
\qquad
D[z=e_-]=tS_0(U)t^{-1}.
\]

Thus the catalyst merely conjugates the direct survivor.  The arbitrary
recovery self-loop theorem already gives
\((x^3t^{-4},S_0(U))\sim_{\mathrm{AC1-3}}\operatorname{AK}(3)\), so every
endpoint in this mixed unbounded family also returns classically to AK(3).
The two seam templates and exact conjugation identities are pinned by
`tests/stable_ac/test_mixed_recovery_one_d_self_loop.py`.

## Proven result 14: reversing the catalyst target is also a self-loop

The cyclic isolator classification in Proven result 13 is symmetric in
factor order, but the survivor after elimination is not.  The theorem in

```text
literature/proofs/AK3_MIXED_RECOVERY_REVERSE_TARGET_SELF_LOOP.md
```

therefore treats the missing role separately: \(D\) is the target of one
arbitrary-relative-conjugator \(B_U^{\pm1}\)-multiplication, the modified
\(D\)-slot is removed, and the restored \(B_U=z^{-1}w\) slot survives.

The bridge and forced-seam argument again gives exactly

\[
e_+=t^{-1}wx,
\qquad
e_-=twx^{-1}.
\]

Substitution in the surviving \(B_U\) gives

\[
\begin{aligned}
C_+
&=e_+^{-1}w
=w^{-1}S_0(U)^{-1}w,\\
C_-
&=e_-^{-1}w
=(t^{-1}w)^{-1}S_0(U)(t^{-1}w),
\end{aligned}
\]

where \(S_0(U)=t^{-1}wxw^{-1}\).  Hence both endpoints differ from the
direct recovery endpoint only by AC1/AC3 moves and return classically to
AK(3).  This has no recovery-length or conjugator-length bound.  The two
exact conjugacy identities and the signed cyclic residue are pinned by
`tests/stable_ac/test_mixed_recovery_reverse_target_self_loop.py`.

## Proven result 15: every post-catalyst \(R\)-gauge tail

The two one-\(D\) theorems classify the immediate eliminator, but a later
sequence of \(R\)-source moves could alter both the future isolator and its
survivor before deletion.  The quotient-shadow theorem in

```text
literature/proofs/AK3_POST_CATALYST_R_GAUGE_SELF_LOOP.md
```

closes this unbounded suffix without a seam census.

For a general fixed relator \(R\in F(X)\), put

\[
G=F(X)/\langle\!\langle R\rangle\!\rangle .
\]

Then

\[
F(X,z)/\langle\!\langle R\rangle\!\rangle
\cong G*\langle z\rangle .
\]

If two isolator shadows \(z^{-1}e\) and \(z^{-1}e_0\) are equal in this free
product, then \(e=e_0\) in \(G\).  Evaluation at \(z=e\) therefore agrees
with evaluation at \(z=e_0\).  Any two quotient-equal survivor shadows
evaluate to the same word modulo \(R\), and the fixed-relator
normal-closure lemma turns that equality into classical AC equivalence.

Consequently, after arbitrary recovery and one classified \(B_U/D\) cross
multiplication in either target role, an arbitrary finite suffix preserving
both non-\(R\) quotient shadows cannot change the eliminated endpoint's
classical AC class.  This includes arbitrarily many multiplications by
arbitrarily conjugated \(R^{\pm1}\)-factors on the isolator, the survivor,
or both.  Taking the recovery prefix to be literal closes the collected
\(D\)-then-\(R\) order for both target roles.

The exact evaluation identity is unbounded.  A cancellation-heavy replay
over all 61 recoveries through length 9, both catalyst signs, both target
roles, and gauge factors with \(z\)-containing conjugators is pinned by
`tests/stable_ac/test_post_catalyst_r_gauge_self_loop.py`.

## Proven result 16: the quotient one-\(D\) theorem

Pre-twisting the \(D\)-slot by fixed-\(R\) moves appears to escape the
literal free-group catalyst theorem.  The quotient theorem in

```text
literature/proofs/AK3_QUOTIENT_ONE_D_CATALYST_SELF_LOOP.md
```

closes that gap and every other fixed-\(R\) ordering with exactly one
\(B/D\) cross multiplication when the cross target is the relator finally
eliminated.

Project to

\[
H=
\langle x,t\mid x^3=t^4\rangle*\langle z\rangle .
\]

Every fixed-\(R\) gauge factor vanishes in \(H\).  The Bass--Serre
classification of the remaining cross product must retain a residual
vertex twist:

\[
UhVh^{-1},
\qquad
h\in
\langle x,t\mid x^3=t^4\rangle
\ \text{or}\
h\in\langle z\rangle .
\]

Axes sharing an edge give the literal rotation residue.  Axes sharing only
a vertex give two \(2\times4\) forcing tables for \(G\)-vertex twists and
four exponent solutions per sign for \(\langle z\rangle\)-vertex twists.
Every one-\(z\) result is still one of

\[
\operatorname{cyc}(z^{-1}t^{-1}xtx),
\qquad
\operatorname{cyc}(z^{-1}txtx^{-1}).
\]

The quotient tails have weights \(8\) and \(6\), so they are nontrivial.
Free-product conjugacy therefore upgrades the cyclic classification of a
normalized final isolator \(z^{-1}e\) to the exact equality
\(e=e_\pm\) modulo \(R\).  Evaluating the restored survivor and applying
the fixed-relator normal-closure lemma returns the endpoint classically to
AK(3), in either target role.

Thus arbitrary fixed-\(R\) gauge moves may occur on either slot, before and
after the unique cross event, with unbounded \(z\)-containing conjugators,
provided the cross-target slot becomes the final one-\(z\) isolator.
The exact quotient normal form, four literal witnesses, sixteen forced
\(G\)-vertex twists, eight \(z^k\)-vertex solutions, and sample pre-gauges
are pinned by
`tests/stable_ac/test_quotient_one_d_catalyst_barrier.py`.

## Proven result 17: passive-source absorption

The remaining one-cross role is governed by the more general theorem in

```text
literature/proofs/AK3_PASSIVE_SOURCE_ELIMINATION_SELF_LOOP.md
```

Let \(I_0=z^{-1}e_0\) be a baseline source isolator in
\(H=G*\langle z\rangle\), and let \(I=z^{-1}e\) be the eventual
isolator.  If their quotient shadows have the same normal closure \(L\),
then evaluation at \(z=e\) kills \(L\) and forces \(e=e_0\) in \(G\).
Consequently, every finite history which changes the other relator only by
source factors from \(L\), fixed-\(R\) gauges, conjugation, and inversion
returns after deletion to the baseline endpoint up to classical AC1--AC3.

For AK(3), take

\[
I_0=B=z^{-1}xt,
\qquad
J_0=D=t^{-1}zxz^{-1}.
\]

Thus any finite number of passive \(B\)-source multiplications into the
\(D\)-slot, with arbitrary conjugators and fixed-\(R\) gauges, disappears
when the final \(B\)-type isolator is removed.  The survivor returns to

\[
D[z\mapsto xt]
=t^{-1}xtxt^{-1}x^{-1},
\]

a conjugate of the AK(3) braid relator.  This closes the realizable
source-eliminated branch of the exactly-one-cross theorem and all its
finite passive-source iterations.

The opposite role is vacuous in the one-\(z\) corridor:
\(D=t^{-1}zxz^{-1}\) has \(z\)-exponent zero, preserved by
fixed-\(R\) gauges, conjugation, and inversion, whereas a normalized
one-\(z\) isolator has exponent \(\pm1\).  The representative multi-factor
evaluation identities and this exponent obstruction are pinned by
`tests/stable_ac/test_passive_source_elimination.py`.

## Proven result 18: every one-way cross history returns

The theorem in

```text
literature/proofs/AK3_ONE_WAY_CROSS_TRAFFIC_SELF_LOOP.md
```

closes every finite history in which one of the \(B/D\) slots remains a
passive source and all cross events target the other slot, whenever a
one-\(z\) eliminator is produced and a surviving source shadow is restored
up to conjugation and inversion, or an eliminated source preserves its
baseline quotient normal closure.

For passive \(D\)-source traffic targeting \(B\), quotient by \(D\):

\[
H/\langle\!\langle D\rangle\!\rangle
\cong
\langle G,z\mid zxz^{-1}=t\rangle .
\]

This is an HNN extension of \(G\).  Britton's lemma embeds \(G\), and the
length-one Collins conjugacy theorem forces every normalized final
\(B\)-target \(z^{-1}e\) into the complete family

\[
[e]_G=e_n=t^{-n}(xt)x^n,
\qquad n\in\mathbb Z.
\]

Substitution gives the exact endpoint identity

\[
D[z\mapsto e_n]
=t^{-n}D[z\mapsto xt]t^n.
\]

Thus the HNN parameter produces only a relator conjugation.  For exactly
two \(D\)-source factors with signs \(\epsilon,\eta\), weight forces
\(n=\epsilon+\eta\), so the four signed rows give only \(e_2,e_0,e_{-2}\).

For passive \(B\)-source traffic targeting \(D\), quotient by \(B\), which
sets \(z=xt\) and returns \(G\).  If a final target \(z^{-1}e\) maps to
\(aD(xt)^\delta a^{-1}\), then the surviving \(B\)-slot maps to
\(aD(xt)^{-\delta}a^{-1}\).  It is already a conjugate or inverse of the
AK(3) braid endpoint.  An even number of \(B\)-source factors cannot
produce a one-\(z\) \(D\)-target when each source spelling is a conjugate
of \(B^{\pm1}\), because its \(z\)-exponent remains even.

Together with passive-source absorption for the source-eliminated role,
these quotient arguments close both directions and both choices of the
eliminated slot.  The exact seam recurrences, signed two-\(D\) table,
endpoint conjugacies, reverse-direction survivor formula, and parity
obstruction are pinned by
`tests/stable_ac/test_one_way_cross_traffic.py`.

## Proven result 19: alternating two-cross feedback also returns

The theorem in

```text
literature/proofs/AK3_TWO_CROSS_FEEDBACK_SELF_LOOP.md
```

closes the minimal coupled history: first \(D^\epsilon\) targets \(B\),
producing \(B_1\), then \(B_1^\eta\) targets \(D\), producing \(D_1\).
Suppose the second target normalizes after orientation
\(\delta\) to \(z^{-1}e\).

Quotient by the original \(D\), not the modified survivor.  The first
cross disappears, \(B_1=B\), and \(D_1\) becomes a conjugate of
\(B^\eta\) in

\[
K_D=\langle G,z\mid zxz^{-1}=t\rangle .
\]

Stable-letter exponent forces

\[
\delta=\eta.
\]

The length-one HNN theorem then gives

\[
[e]_G=e_n=t^{-n}(xt)x^n,
\]

and torus weight forces

\[
n=\epsilon+\eta.
\]

After evaluation, write \(C=B_1[z\mapsto e]\) for the survivor and
\(Q=D[z\mapsto e]\).  The identity \(D_1[z\mapsto e]=1\) forces \(C\) to
be conjugate to \(Q^{-\eta}\).  Since

\[
[Q]_G
=
\left[t^{-n}D(xt)t^n\right]_G,
\]

the fixed-\(R\) lemma followed by AC1/AC3 returns \((R,C)\) classically to
AK(3).

The reverse alternating order cannot eliminate its second target: its
\(z\)-exponent is \(0\) or \(\pm2\).  Eliminating the first target/source
in either order absorbs the later event and reduces to the one-way
theorem.  Together with Proven result 18, every exactly-two-cross route
with a final one-\(z\) eliminator is closed under the stated restoration
hypotheses.  The four sign rows, survivor classes, endpoint conjugacies,
and opposite-order exponent obstruction are pinned by
`tests/stable_ac/test_two_cross_feedback.py`.

## Proven result 20: three-cross routes reach the killer frontier

The theorem in

```text
literature/proofs/AK3_THREE_CROSS_KILLER_REDUCTION.md
```

analyzes both strictly alternating target orders with three cross events.
For

\[
D\to B_1,\qquad B_1\to D_1,\qquad D_1\to B_2,
\]

the third target has stable-letter exponent

\[
\sigma_z(B_2)=-1-\eta\theta\in\{0,-2\}.
\]

It cannot be a one-\(z\) eliminator.  If its source \(D_1\) is eliminated
instead, the third event vanishes under evaluation and Proven result 19
closes the endpoint.

For the reverse order

\[
B\to D_1,\qquad D_1\to B_1,\qquad B_1\to D_2,
\]

the final target exponent is

\[
\sigma_z(D_2)=-\epsilon-\theta-\epsilon\eta\theta.
\]

The all-positive and all-negative rows have absolute exponent \(3\).
Exactly six sign rows have absolute exponent \(1\).  Torus weight pins the
corresponding tail weights to \(5,7,\) or \(9\), and after evaluation every
survivor \(C=B_1[z\mapsto e]\) has weight \(\pm1\).  Since \((R,C)\)
presents the trivial group, \(C\) is a weight-\(\pm1\) normal generator,
or killer, of

\[
G=\langle x,t\mid x^3=t^4\rangle.
\]

This is the first branch not closed by quotient exponent and weight.
Killer does not imply meridian: nontrivial torus-knot groups have
infinitely many inequivalent pseudo-meridians (Silver--Whitten--Williams,
Theorem 1.2 and Corollary 1.3).

The literal untwisted signed-seam subcorridor is nevertheless closed
completely.  The finite certificate enumerates \(16\) first targets,
\(416\) intermediate pairs, \(522\) one-\(z\) triples, and \(69\) final
target classes.  Every evaluated survivor has the single signed cyclic
class of

\[
D_p=t^{-1}(xt)x(xt)^{-1}.
\]

The arithmetic table and complete seam certificate are independently
replayed by
`tests/stable_ac/test_three_cross_killer_reduction.py`.

## Proven result 21: all three-cross target words are classified

The theorem in

```text
literature/proofs/AK3_THREE_CROSS_TARGET_WORD_CLASSIFICATION.md
```

classifies the eight length-three words recording which \(B/D\) slot is
targeted at each cross event:

| target word | conclusion |
|---|---|
| \(BBB,DDD\) | one-way self-loop |
| \(BBD,BDD,DDB\) | quotient/exponent self-loop |
| \(BDB\) | strict-order self-loop |
| \(DBB,DBD\) | six-row killer equation |

For \(BBD\), quotient by the original \(D\).  The first two events vanish,
the HNN family returns, and weight pins

\[
n=\epsilon+\eta+\theta.
\]

Evaluation makes the survivor a conjugate of
\(D(e_n)^{-\theta}\), hence of \(D_p^{\pm1}\).

For \(BDD\), the third target has even \(z\)-exponent.  Deleting its
source erases both later events and leaves the first one-way self-loop.

For \(DDB\), the third source has even \(z\)-exponent.  Quotient by the
original \(B\), which sets \(z=xt\); evaluation of the final target makes
the actual survivor a conjugate of \(D_p^{\pm1}\).

The remaining non-strict word \(DBB\) has exactly six exponent-feasible
rows.  Their tail weights are \(5,7,\) or \(9\), and their survivor is a
weight-\(\pm1\) killer of \(G\).  Its literal untwisted seam census has
the same exact \(16/416/522/69\) counts as the strict \(DBD\) corridor and
again only the signed cyclic class of \(D_p\).

The arithmetic and all \(522\) untwisted substitutions are independently
replayed by `tests/stable_ac/test_three_cross_target_words.py`.

## Proven result 22: the final target choice is redundant

The theorem in

```text
literature/proofs/AK3_FINAL_TARGET_SWITCH_DUALITY.md
```

is an abstract final-event duality.  If the current slots are \(A,B\) and
the final cross targets \(A\), its target class has a representative

\[
T_A=A\,uB^\theta u^{-1}.
\]

The cyclic conjugate

\[
T_B=B^\theta u^{-1}Au
\]

is the target of a legal final cross with the other slot designated as
target.  Therefore the identical one-\(z\) isolator \(z^{-1}e\) can be
obtained with either target choice.

After evaluation,

\[
[A_e]_G=[u_eB_e^{-\theta}u_e^{-1}]_G.
\]

The two possible survivors are conjugate up to inversion in the
fixed-\(R\) quotient, so the fixed-relator lemma gives

\[
(R,A_e)\sim_{\mathrm{AC1-3}}(R,B_e).
\]

This is unbounded in the relative conjugator and independent of
multiplication side.  Consequently target words pair by their final
letter:

\[
BBB\leftrightarrow BBD,\quad
BDD\leftrightarrow BDB,\quad
DBB\leftrightarrow DBD,\quad
DDB\leftrightarrow DDD.
\]

In particular, \(DBB\) and \(DBD\) are one arbitrary bridge/twist killer
mechanism, not two.  The factor switch and evaluated survivor identities
are independently replayed by
`tests/stable_ac/test_final_target_switch_duality.py`.

## Proven result 23: central quotient plus weight decides conjugacy

The theorem in

```text
literature/proofs/AK3_CENTRAL_QUOTIENT_CONJUGACY_CRITERION.md
```

gives an exact non-abelian finish test inside

\[
G=\langle x,t\mid x^3=t^4\rangle.
\]

Put \(c=x^3=t^4\).  It is central, has weight \(12\), and

\[
G/\langle c\rangle\cong C_3*C_4.
\]

For all \(U,V\in G\),

\[
U\sim_GV
\iff
\operatorname{wt}(U)=\operatorname{wt}(V)
\quad\text{and}\quad
\bar U\sim_{C_3*C_4}\bar V.
\]

Indeed, quotient conjugacy lifts to
\(U=c^kgVg^{-1}\), and equal weight forces \(12k=0\).  Conjugacy in
\(C_3*C_4\) is decided exactly by cyclic reduction of its alternating
normal form followed by cyclic-rotation comparison.

Every feasible prefix-\(DB\) survivor already has weight
\(s\in\{\pm1\}\).  Hence

\[
\bar C\sim\overline{D_p^s}
\]

is sufficient and exact for concluding \(C\sim_GD_p^s\), after which the
fixed-\(R\) lemma returns the endpoint classically to AK(3).

Failure of the quotient test is not AC inequivalence: it rules out only
this direct fixed-\(R\) conjugacy finish.  Central shifts, negative
controls, and representative HNN endpoints for \(-12\le n\le12\) are
independently replayed by
`tests/stable_ac/test_central_quotient_conjugacy_criterion.py`.

## Proven result 24: the evaluated prefix-\(DB\) equations have a non-braid killer

The theorem in

```text
literature/proofs/AK3_PREFIX_DB_EVALUATED_COUNTERMODEL.md
```

shows that the central-quotient finish criterion does not hold
automatically.  If \(e\) is the final tail, put

\[
b=e^{-1}p,\qquad d=t^{-1}exe^{-1}.
\]

After evaluation, every \(DBD\) representative satisfies

\[
K=d\alpha b^\epsilon\alpha^{-1},\qquad
C=b\beta K^\eta\beta^{-1},\qquad
1=K\gamma C^\theta\gamma^{-1}.
\]

For the feasible row \((\epsilon,\eta,\theta)=(1,1,-1)\), there is an
exact solution in \(G\) with

\[
\operatorname{wt}(e)=7,\qquad
\operatorname{wt}(C)=1,
\]

whose survivor projects to

\[
\bar C=X^2T^3X^2\sim XT^{-1}
\]

in \(C_3*C_4\).  The lifted survivor \(C\) normally generates \(G\), but
its projected cyclic length is \(2\), while the projected cyclic lengths of
\(D_p^{\pm1}\) are \(6\).  It is therefore not conjugate to
\(D_p^{\pm1}\).

This is a countermodel to the evaluated equations, weights, and killer
condition, not a realized stable history.  Evaluation proves only that
the oriented unevaluated target lies in
\(\langle\!\langle z^{-1}e\rangle\!\rangle\); a legal deletion requires
its conjugacy class to contain the cyclically reduced length-two
representative \(z^{-1}e\).

The explicit solution is in fact nonliftable.  Here \(\delta=-1\).
Quotienting by the original \(B=z^{-1}p\) would force
\(b=e^{-1}p\) to be conjugate to a commutator \([D_p,h]\).
In \(C_3*C_4\), \(\bar b\) has cyclic length \(4\), whereas the complete
Bass--Serre edge/vertex reduction gives commutator lengths
\(0,8,10,12\), or at least \(14\).  The exact normal forms,
cyclic-length separation, and \(216\)-case commutator sieve are
independently replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

## Proven result 25: quotient-B imposes a cyclic-length gap

The theorem in

```text
literature/proofs/AK3_QUOTIENT_B_LENGTH_GAP.md
```

applies the quotient-\(B\) sieve to all six feasible prefix-\(DB\) rows.
Put

\[
A=\overline{D_p}\in C_3*C_4,
\qquad
b=e^{-1}p,
\qquad
m=\eta\theta.
\]

Every literal one-\(z\) lift must satisfy

\[
\bar b\sim
\left(AhA^mh^{-1}\right)^{-\delta}
\]

for some \(h\in C_3*C_4\).  The complete Bass--Serre axis trichotomy
gives

\[
\begin{aligned}
m=-1:\quad&
\ell_{\mathrm{cyc}}(\bar b)\in\{0,8,10,12\}
\text{ or }\ell_{\mathrm{cyc}}(\bar b)\ge14,\\
m=1:\quad&
\ell_{\mathrm{cyc}}(\bar b)\in\{6,10,12\}
\text{ or }\ell_{\mathrm{cyc}}(\bar b)\ge14.
\end{aligned}
\]

The four \(m=-1\) rows all have
\(\operatorname{wt}(e)=7\) and \(\operatorname{wt}(b)=0\).
If their quotient length is zero, central weight forces \(b=1\), hence
\(e=p\), and the survivor is conjugate to \(D_p^\eta\).  Therefore the
zero-length branch is a classical self-loop, and every non-braid
commutator-row lift has quotient length at least \(8\).  The two
same-orientation rows begin at length \(6\).

That minimum length-six stratum consists of exactly two projected
conjugacy classes \(L_1,L_2\).  The unique weight-two \(G\)-conjugacy
class above each \(L_j\) is represented by \(\lambda_j\), and the
necessary quotient equation forces

\[
b^{-\delta}\sim_G\lambda_j,
\qquad
[e]_G=[p\,g\lambda_j^\delta g^{-1}]_G.
\]

The previous non-braid killer solves the last two evaluated equations for
both \(L_j\), so minimum quotient length alone does not close these rows.
The first evaluated cross equation and literal free-kernel liftability
remain.

The intersecting-axis spectra are exact \(216\)-case reductions; disjoint
axes at distance \(d\ge1\) give the unbounded formula \(12+2d\).
Both spectra, the complete sign table, and the two minimum classes are
replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

## Proven result 26: minimum-tail repositioning defeats the evaluated first-cross barrier

The theorem in

```text
literature/proofs/AK3_MINIMUM_TAIL_REPOSITIONING_COUNTERMODEL.md
```

first applies the exact first-cross conjugacy test

\[
d^{-1}K\sim_Gb^\epsilon
\]

to the four minimum-tail representatives displayed in Result 25. An
exhaustive relative-axis overcensus in \(C_3*C_4\) gives respective
minimum product lengths

\[
12,\quad14,\quad16,\quad14,
\]

while \(b^\epsilon\) has length \(6\). Those four fixed representatives
therefore fail for every remaining conjugator.

The failure is not invariant under repositioning the tail relative to the
fixed word \(p=xt\). In the dual row
\((\epsilon,\eta,\theta)=(+,-,-)\), put

\[
C_0=c^{-2}x^2t^3x^2,
\qquad
s=xtx^{-1},
\]

and define

\[
\begin{aligned}
C&=sC_0^{-1}s^{-1},&
\rho&=s(xt^{-1})s^{-1},\\
\gamma&=xt^{-1}x^{-1},&
\beta&=x,\\
b&=C\rho C\rho^{-1},&
e&=pb^{-1},\\
d&=t^{-1}exe^{-1},&
K&=\gamma C\gamma^{-1},\qquad \alpha=t.
\end{aligned}
\]

Amalgam normal form verifies all three evaluated equations exactly:

\[
K=d\alpha b\alpha^{-1},
\qquad
C=b\beta K^{-1}\beta^{-1},
\qquad
1=K\gamma C^{-1}\gamma^{-1}.
\]

Here

\[
\operatorname{wt}(e)=9,\quad
\operatorname{wt}(b)=-2,\quad
\operatorname{wt}(C)=-1.
\]

The survivor \(C\) is a conjugate of the non-braid killer \(C_0^{-1}\),
while \(\bar b^{-1}\) is exactly the minimum length-six class \(L_1\).
Thus even the first evaluated equation does not force the braid class.

The candidate also passes the synchronized quotient-\(B\) test. For

\[
\Phi=(r_e,r_p):G*\langle z\rangle\to G\times G,
\]

\[
\operatorname{im}\Phi
=
\{(g,gn):n\in\langle\!\langle b\rangle\!\rangle_G\}.
\]

In this candidate

\[
G/\langle\!\langle b\rangle\!\rangle_G\cong C_2,
\]

so the normal closure of \(b\) is the even-weight subgroup. This permits
the evaluated bridges to interpolate to

\[
h_0=xtx^{-1},
\qquad
D_ph_0D_ph_0^{-1}=b^{-1}.
\]

What remains is a genuinely nonabelian free-kernel equation. With
\(q=ze^{-1}\),

\[
N=\ker r_e
=
F\{q_g=gqg^{-1}:g\in G\}.
\]

Arbitrary lifts of the three evaluated bridges introduce
\(U,V,W\in N\), and semidirect expansion gives an explicit
\(n_3(U,V,W)\) recorded in the proof. Literal liftability is exactly the
condition that \(n_3\) be conjugate in \(N\) to one negative basis
letter. The \(G\)-valued lift \(U=V=W=1\) has cyclic kernel length \(7\),
not \(1\), but this excludes only that point. Scalar augmentation already
matches the required basis letter. The full
\(N_{\rm ab}\cong\mathbb Z[G]\) Fox equation is explicit in the proof but
remains unchecked; finite quotient group algebras give the next exact
sieve before the nonabelian equation.

The four relative-axis overcensuses, repositioned equations,
synchronized bridge arithmetic, quotient-\(B\) identity, and literal
Schreier length are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.
The hand proof that the relevant normal closure is the even-weight
subgroup supplies the remaining synchronization step.

## Proven result 27: the Fox equation is an infinite coset-module problem

The theorem in

```text
literature/proofs/AK3_MINIMUM_TAIL_FOX_COSET_SIEVE.md
```

reduces the full abelianized free-kernel equation for the repositioned
candidate. Over

\[
R=\mathbb Z[G],
\]

write

\[
\Xi=A_0+A_Uu+A_Vv+A_Ww.
\]

If

\[
H_0=\gamma b\gamma^{-1},
\qquad
P=\langle K,H_0\rangle,
\]

then the two bridge coefficients satisfy

\[
\boxed{
A_VR+A_WR
=
\sum_{p\in P}(p-1)R
=I_P.
}
\]

Consequently the full three-variable Fox equation is solvable exactly
when

\[
\boxed{
\pi_P(A_0)+\pi_P(A_U)u=-[Pg]
}
\]

for some \(u\in R\) and \(g\in G\), inside the right permutation module

\[
R/I_P\cong\mathbb Z[P\backslash G].
\]

The subgroup \(P\) is now classified. After simultaneous conjugation it
is generated by the projected elements \(C\) and
\(\rho C\rho^{-1}\). Both have Bass--Serre translation length \(2\),
while their product \(b\) has length \(6\). Their axes are therefore
disjoint at distance one. Tree ping-pong, injectivity of the central
projection on the generated subgroup, and Euler characteristic give

\[
\boxed{
P\cong F_2,
\qquad
P\cap\langle c\rangle=1,
\qquad
[G:P]=\infty.
}
\]

Thus the coset module is genuinely infinite; the Fox problem does not
collapse to scalar augmentation.

An exact finite quotient supplies the first target restriction:

\[
x\mapsto(1\,2\,3),
\qquad
t\mapsto(0\,1\,2\,3)
\]

maps \(G\) onto \(S_4\) and \(P\) onto

\[
P_0=\operatorname{Stab}_{S_4}(3)\cong S_3.
\]

In the four-coset module, with cosets indexed by \(g^{-1}(3)\),

\[
\overline{A_0}=(0,-2,0,1),
\qquad
\overline{A_U}=(2,0,0,-2).
\]

The right orbit of \(\overline{A_U}\) spans twice the augmentation
lattice. Therefore the finite Fox equation is solvable only when the
target residue lies in \(P_0\). This is a genuine restriction, but not a
nonlift certificate: the identity and all six residues in \(P_0\)
survive.

The axis lengths, subgroup images, coefficient vectors, and target
parity are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

## Result 28: the binary \(S_4\) lift removes two Fox targets

The exact refinement is proved in

```text
literature/proofs/AK3_MINIMUM_TAIL_BINARY_COSET_SIEVE.md
```

The projected subgroup \(\pi(P)\le C_3*C_4\) has a nine-edge folded
core. Its partial factor actions are

\[
\begin{array}{c|c}
x & (0\,1\,2),\ (5\,8\,9)\\
t & (1\,2\,4\,5),\ (8\,9\,11\,12),
\end{array}
\]

with the remaining incidences forming the core boundary. The core has
rank two. Its two fundamental chains recover the exponent sums
\((m,n)\) in the free basis \((K,H_0)\), and central weight gives the
exact lift criterion

\[
w\in P
\iff
\pi(w)\text{ is an accepted based loop and }
\operatorname{wt}(w)=-m-2n.
\]

In particular,

\[
L,\gamma e^{-1}\notin P,
\qquad
\gamma e^{-1}=c^{-1}L.
\]

Thus left multiplication by \(L\) cannot be treated as an action on
\(P\backslash G\).

The previous projective quotient lifts to

\[
\rho(x)=
\begin{pmatrix}0&1\\2&1\end{pmatrix},
\qquad
\rho(t)=
\begin{pmatrix}0&1\\1&1\end{pmatrix}
\quad\text{in }GL_2(\mathbb F_3),
\]

where both defining powers equal \(-I\). For \(\ell=(1,2)\),

\[
\rho(P)=\operatorname{Stab}(\ell),
\qquad
\ell\rho(A_U)=0,
\qquad
\ell\rho(A_0)=\ell.
\]

The induced functional on \(\mathbb F_3[P\backslash G]\) proves that
every Fox target must satisfy

\[
\boxed{
\rho(g)\in(-I)\rho(P).
}
\]

This removes the identity target and the natural target
\(g=\gamma e^{-1}\). The central target \(g=c^{-1}\) survives, so the
binary lift is still a target sieve rather than a nonlift certificate.

## Result 29: the central target is Fox-obstructed

The exact obstruction is proved in

```text
literature/proofs/AK3_MINIMUM_TAIL_CENTRAL_TARGET_OBSTRUCTION.md
```

The evaluated identities sharpen the subgroup geometry:

\[
H=(LKL^{-1})K,
\qquad
P=\langle K,LKL^{-1}\rangle.
\]

A four-state folded core proves

\[
J:=\langle P,L\rangle=\langle K,L\rangle\cong F_2.
\]

Thus \(J\) is the HNN extension of \(P\) which identifies
\(\langle K\rangle\) with
\(\langle LKL^{-1}\rangle\). The operator

\[
\mathcal B(z)=\pi_P((1+L)z)
\]

becomes unsigned edge incidence on the HNN Bass--Serre forest after
quotienting its domain by \((K-1)R\). Leaf peeling gives the exact
kernel

\[
\boxed{
\ker\mathcal B=(K-1)R.
}
\]

For \(g=c^{-1}\), the Fox equation would therefore force

\[
-(F_0+c^{-1})
\in
(d-K)R+(K-1)R
=
I_Q,
\qquad
Q=\langle d,K\rangle.
\]

A second folded core proves

\[
Q\cong F_2,
\qquad
Q\cap\langle c\rangle=1,
\]

and separates the four cosets in

\[
\pi_Q(F_0+c^{-1})
=
[Qc^{-1}]+[Qt^{-1}]-[Q]-[Qdte^{-1}].
\]

This vector is nonzero. Consequently

\[
\boxed{
-[Pc^{-1}]-\pi_P(A_0)
\notin
\pi_P(A_U)\mathbb Z[G].
}
\]

The central target is impossible at the Fox level. Other exact targets
over the surviving binary residue remain open.

## Result 30: every minimum-tail Fox target is obstructed

The all-target theorem is proved in

```text
literature/proofs/AK3_MINIMUM_TAIL_ALL_TARGET_FOX_OBSTRUCTION.md
```

For an arbitrary target \(g\), the exact equation is

\[
\mathcal B\bigl(F_0+(d-K)u\bigr)
=-[Pg]-[Pc^{-1}L],
\qquad
\mathcal B(z)=\pi_P((1+L)z).
\]

The HNN forest gives a complete image classification. A target can pass
the first equation only when

\[
g=jc^{-1},
\qquad
j\in J=\langle K,L\rangle,
\qquad
\exp_L(j)\equiv0\pmod2.
\]

For every such target, unsigned incidence has one alternating odd-path
preimage \(z_g\) modulo \((K-1)R\). Choosing its edge representatives in
\(Jc^{-1}\) gives

\[
\operatorname{supp}(z_gc)\subset J.
\]

The residual equation in
\(\mathbb Z[Q\backslash G]\), \(Q=\langle d,K\rangle\), would require

\[
\pi_Q(z_g)c=\pi_Q(F_0)c
=[Qt^3]-[Qc]-[Qxt].
\]

The based folded fiber product of the projected \(Q\)- and \(J\)-cores
has nine edges, eight factor vertices, and rank two. Its two chord loops
are \(\bar K\) and

\[
\bar h=t x t^2x^2t^2x t x t^2x^2t^3.
\]

Their unique \(Q\)- and \(J\)-lifts agree exactly, so the central
lift-defect vanishes on \(\bar Q\cap\bar J\). Consequently

\[
Qc\notin QJ.
\]

The \(Q\)-core also separates \(Qc\) from \(Qt^3\) and \(Qxt\).
Therefore the coefficient \(-1\) at \(Qc\) cannot be supplied by any
moving path.

An independent \(S_5\) certificate gives the same support obstruction:
for the exact images \(Q_0,J_0\),

\[
|Q_0|=8,\qquad |J_0|=20,\qquad
\sigma(t^{-1})\notin Q_0J_0.
\]

Thus

\[
\boxed{
\text{no }g\in G\text{ solves the repositioned minimum-tail Fox
equation.}
}
\]

This closes that candidate and the entire target residue left by
Results 27--29. It does not close other stable histories or AK(3).

## Result 31: one signed-HNN Fox factorization covers every row

The master lemma is proved in

```text
literature/proofs/AK3_SIGNED_HNN_FOX_MASTER_LEMMA.md
```

For the general signed history

\[
D_1=D\,uB^\epsilon u^{-1},\qquad
B_1=B\,vD_1^\eta v^{-1},\qquad
D_2=D_1\,wB_1^\theta w^{-1},
\]

the abelianized free-kernel recurrence factors as

\[
\Xi=A_0+A_U\mathbf u+A_V\mathbf v+A_W\mathbf w,
\]

where, with \(m=\eta\theta\),

\[
\begin{aligned}
A_0&=(1+mL)F_\epsilon+M_\theta\mathbf j,\\
A_U&=(1+mL)(d-K),\\
A_V&=-mL(K-1)\beta^{-1},\\
A_W&=K-1.
\end{aligned}
\]

The group element \(L\) has one of four explicit spellings according to
\((\eta,\theta)\). The two bridge coefficients always generate

\[
A_VR+A_WR
=I_P,
\qquad
P=\langle K,LKL^{-1}\rangle.
\]

If \(J=\langle K,L\rangle\cong F(K,L)\), the residual operator is

\[
\mathcal B_m(z)=\pi_P((1+mL)z).
\]

Modulo \((K-1)R\), this is edge incidence on the HNN Bass--Serre
forest:

- \(m=+1\): unsigned incidence, with zero bipartite signed sum as its
  exact image criterion;
- \(m=-1\): oriented incidence, with zero ordinary component sum as its
  exact image criterion.

Both are injective on finite-support edge chains. Therefore

\[
\boxed{
\ker\mathcal B_+
=\ker\mathcal B_-
=(K-1)R.
}
\]

An independent \(S_3\) semidirect-product replay checks all eight sign
rows, and a separate finite-tree replay checks both incidence signs.

This shows exactly which part of Result 30 is uniform. The HNN
factorization and path uniqueness are sign-independent; the later
support-versus-\(QJ\) obstruction is not. Extending the all-target
closure to another row requires a candidate-specific evaluated solution
and a new \(Q\)-\(J\) double-coset certificate.

## Result 32: the multi-\(z\) escape has a literal-kernel gate

The primitive-gate theorem is proved in

```text
literature/proofs/AK3_MULTI_Z_PRIMITIVE_GATE.md
```

Let

\[
\rho:F(X)*\langle q\rangle\longrightarrow F(X)
\]

kill \(q\). If a primitive word \(W\) satisfies \(\rho(W)=1\)
literally, then

\[
\boxed{W\text{ is conjugate to }q^{\pm1}.}
\]

Indeed, \(\langle\!\langle W\rangle\!\rangle\) lies in
\(\langle\!\langle q\rangle\!\rangle\); the corresponding quotients are
free groups of the same finite rank, so Hopficity makes the natural
surjection an isomorphism. The normal closures coincide, and Magnus's
normal-closure theorem finishes the proof.

Thus a genuinely new primitive multi-\(q\) eliminator for AK(3) must
specialize in \(F(x,t)\) to a nontrivial consequence of the retained
relator

\[
R=x^3t^{-4}.
\]

For exponent-\(\pm1\) candidates, the smallest possible
\(q^{\pm1}\)-occurrence count after the one-\(q\) stratum is three.
Split the fixed reduced spelling
\(R=xxxTTTT=A_kB_k\) at any of its six internal seams and put

\[
V_k=qA_kq^{-1}B_kq.
\]

Exact Whitehead graphs and an explicit automorphism prove

\[
\boxed{V_k\text{ is primitive}\iff k=3,}
\qquad
V_3=qx^3q^{-1}t^{-4}q.
\]

This is an exact classification of the six consecutive seam splits,
not of all three-\(q\) words and not by minimum total word length.

For every seam, the evaluated Fox row is

\[
\left(
\partial_xR,\partial_tR,1-A_k+R
\right),
\]

so the primitive member has free-kernel coordinate \(2-x^3\) in
\(\mathbb Z[\langle x,t\mid R\rangle]\).

Writing \(V_3=\phi(q)\), coherent transport is an exact self-loop:
the straightening quotient \(p=\rho\phi^{-1}\) satisfies
\(p(\phi(U))=U\) for every \(q\)-free survivor \(U\). But on
untransported generators,

\[
p(x)=RxR^{-1},\qquad p(t)=t,\qquad p(q)=R^{-1}.
\]

The induced rank-two endomorphism is not an automorphism. Therefore this
result does not close the multi-\(q\) route. It isolates the next
production problem: create \(V_3\) by classical AC moves while leaving a
survivor outside the coherent \(\phi\)-orbit.

## Result 33: direct relation-splitting production is a stable self-loop

The universal closure theorem is proved in

```text
literature/proofs/AK3_RELATION_SPLIT_PRIMITIVE_SELF_LOOP.md
```

Let
\(\langle X\mid R,S_1,\ldots,S_m\rangle\) be a balanced trivial-group
presentation, let \(\rho:F(X)*\langle q\rangle\to F(X)\) kill \(q\),
choose

\[
U\in\langle\!\langle R\rangle\!\rangle_{F(X)},
\]

and take
\(\beta\in\operatorname{Aut}(F(X,q))\) with

\[
\beta(q)=q,\qquad \rho\beta=\rho.
\]

Put

\[
\alpha_U(q)=Uq,\qquad
\phi=\beta\alpha_U,\qquad
W=\phi(q)=\beta(U)q.
\]

The fixed-\(q\) lemma replaces \(R\) by \(\beta(R)\). Since
\(\beta(U)\in\langle\!\langle\beta(R)\rangle\!\rangle\), a second
fixed-relator application and one conjugation give a classical AC
sequence

\[
(R,S_1,\ldots,S_m,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),S_1,\ldots,S_m,W).
\]

After straightening \(W\) by \(\phi^{-1}\) and deleting it, the endpoint
is

\[
\bigl(R,p(S_1),\ldots,p(S_m)\bigr),
\qquad
p=\rho\phi^{-1}.
\]

Modulo the retained \(R\), both \(\alpha_U^{-1}\) and \(\beta^{-1}\)
become invisible after \(q=1\). Hence

\[
p(S_i)=S_i
\pmod{\langle\!\langle R\rangle\!\rangle}
\]

for every survivor. The fixed-\(R\) lemma returns the endpoint
classically to the original tuple.

For AK(3), take \(U=R\) and

\[
\beta(x)=qxq^{-1},\qquad
\beta(t)=t,\qquad
\beta(z)=z.
\]

Then \(W=V_3\). Its direct creation has the literal certificate

\[
R^{-1}\beta(R)
=
(R^{-1}qR)(t^4q^{-1}t^{-4}),
\]

and primitive deletion produces

\[
B'=z^{-1}RxR^{-1}t,
\qquad
D'=t^{-1}zRxR^{-1}z^{-1}.
\]

Each of \(B^{-1}B'\) and \(D^{-1}D'\) is an explicit product of two
conjugates of \(R^{\pm1}\). Thus the obvious asymmetric production of
\(V_3\) is reachable but returns exactly to the rank-three AK(3) root.

## Result 34: retained multi-source primitive production also closes

The multi-source theorem is proved in

```text
literature/proofs/AK3_MULTISOURCE_PRIMITIVE_SELF_LOOP.md
```

Let

\[
\langle X\mid
R_1,\ldots,R_k,S_1,\ldots,S_m
\rangle
\]

be a balanced trivial-group presentation. If

\[
U\in
L=
\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle,
\]

and \(\beta(q)=q,\ \rho\beta=\rho\), then

\[
W=\beta(U)q
\]

can be manufactured after replacing every \(R_i\) by \(\beta(R_i)\).
Straightening \(W\) returns those retained sources literally to \(R_i\).
For \(p=\rho(\beta\alpha_U)^{-1}\),

\[
p(S_j)=S_j\pmod L,
\]

so the multi-source normal-closure lemma returns every other survivor by
classical AC moves.

This strictly extends Result 33: \(U\) may couple several defining
relators. For AK(3), take

\[
U=RB,
\qquad
\beta(x)=qxq^{-1}.
\]

The resulting primitive word is

\[
\boxed{
W
=
qx^3q^{-1}t^{-4}z^{-1}qxq^{-1}tq.
}
\]

It is freely and cyclically reduced, has \(q\)-exponent one, and has
exactly five \(q^{\pm1}\)-occurrences. Both \(R\) and \(B\) have literal
two-factor \(q\)-source certificates, so

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),\beta(B),D,W).
\]

Primitive deletion produces

\[
(R,B,D'),
\qquad
D'=t^{-1}z(RB)x(RB)^{-1}z^{-1}.
\]

The difference \(D^{-1}D'\) is an explicit product of four conjugates of
\(R^{\pm1},B^{\pm1}\). Thus this first genuinely \(B\)-coupled
five-\(q\) construction is also a stable self-loop.

## Result 35: deleting the source slot still recovers its normal closure

The source-slot exchange theorem is proved in

```text
literature/proofs/AK3_SOURCE_SLOT_PRIMITIVE_EXCHANGE_SELF_LOOP.md
```

Let

\[
L_0
=
\langle\!\langle R_1,\ldots,R_{k-1}\rangle\!\rangle
\]

and suppose

\[
R_k^{-1}U\in L_0.
\]

Thus \(U\) is quotient-equal to the source \(R_k\) which will be
replaced. After the relative \(\beta\)-transport, the multi-source lemma
changes the \(\beta(R_k)\)-slot to \(\beta(U)\), and the untouched
stabilizer changes it once more to

\[
W=\beta(U)q.
\]

This time \(W\) occupies the \(R_k\)-slot and the \(q\)-relator survives.
Straightening and primitive deletion send that surviving relator to

\[
U^{-1}.
\]

Modulo \(L_0\), this is \(R_k^{-1}\). The other retained sources replace
it by \(R_k^{-1}\), one inversion recovers \(R_k\), and the recovered
full source subtuple absorbs every remaining survivor distortion.

For AK(3), let \(R_k=B\), \(L_0=\langle\!\langle R\rangle\!\rangle\),
and \(U=RB\). The literal target moves are

\[
\beta(B)
\longmapsto
\beta(R)\beta(B)
\longmapsto
\beta(R)\beta(B)q=W.
\]

Deletion produces

\[
(R,D',U^{-1}),
\]

but

\[
\boxed{U^{-1}R=B^{-1}.}
\]

One multiplication and inversion recover \(B\); the earlier four-factor
\((R,B)\)-certificate returns \(D'\) to \(D\). Thus even targeting and
deleting the \(B\)-source with the five-\(q\) primitive word is a stable
self-loop.

## Result 36: all traffic away from a fixed primitive slot descends

The quotient-naturality theorem is proved in

```text
literature/proofs/AK3_POST_PRIMITIVE_TRAFFIC_SELF_LOOP.md
```

Let \(W=\phi(q)\) be the fixed primitive slot and put

\[
\theta=\rho\phi^{-1},
\qquad
\rho(q)=1.
\]

Then \(\theta(W)=1\). Every AC1--AC3 move commutes with \(\theta\)
provided no AC1 multiplication targets the \(W\)-slot:

- inversion and conjugation remain the corresponding quotient moves;
- inversion or conjugation of \(W\) itself is a quotient no-op and can
  be normalized before deletion;
- multiplication by a non-\(W\) source remains the corresponding
  quotient multiplication;
- multiplication by any current conjugate of \(W^{\pm1}\) becomes a
  no-op.

By induction, any finite post-manufacture history without AC1 into \(W\)
descends to a classical AC history on the immediate primitive quotient.
There is no bound on the number of moves, conjugators, or intermediate
word lengths.

Applied to the AK(3) source-slot checkpoint

\[
(\beta(R),W,D,q),
\]

this means arbitrary mutual traffic among \(\beta(R),D,q\), with
arbitrary uses, inversions, and conjugations of \(W\), still deletes to a
tuple classically equivalent to

\[
(R,D',U^{-1})
\sim_{\mathrm{AC1-3}}
(R,B,D).
\]

An independent seven-move replay uses all three move types, inversion and
conjugation of \(W\), a conjugator containing \(q\), a modified source,
and the changed \(W\)-slot as a source. “Move then quotient” and
“quotient then move” agree literally.

## Result 37: coherent retained traffic into the primitive slot closes

The primitive-target theorem is proved in

```text
literature/proofs/AK3_PRIMITIVE_SLOT_RETAINED_TRAFFIC_SELF_LOOP.md
```

Let \(W=\phi(q)\), let \(\phi(R_1),\ldots,\phi(R_k)\) be retained source
slots, and assume the whole checkpoint is a balanced presentation of the
trivial group (as it is when reached from a stabilization by stable AC
moves). Put

\[
L=\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)}.
\]

For every \(q\)-free \(V\in L\), retained-source AC moves can target the
primitive slot and produce

\[
W_V=W\phi(V)=\phi(qV).
\]

The right transvection

\[
\delta_V(q)=qV
\]

is an automorphism, so \(W_V=(\phi\delta_V)(q)\) is primitive. Its
straightening returns every retained source literally. Modulo \(L\),
\(\delta_V^{-1}\) is invisible, hence every new survivor quotient is
equal to the old one modulo the retained sources. The multi-source lemma
returns the endpoint classically.

For the AK(3) source-slot checkpoint, take \(V=R\). One AC1 move gives

\[
\boxed{
W_R=W\beta(R)=\phi(qR).
}
\]

This freely and cyclically reduced word has four positive and three
negative \(q\)-letters. The new deletion quotient is

\[
(R,D_R',U^{-1}R^{-1}),
\]

and

\[
(U^{-1}R^{-1})R^2=B^{-1}.
\]

Thus two \(R\)-source moves and inversion recover \(B\).
Moreover \((D')^{-1}D_R'\) is an explicit product of two conjugates of
\(R^{\pm1}\), after which the old source-slot certificate returns to the
rank-three AK(3) root.

## Result 38: both literal q-source orientations close

The two-sign theorem is proved in

```text
literature/proofs/AK3_LITERAL_Q_SOURCE_TRAFFIC_SELF_LOOP.md
```

Let \(U\) be primitive in the unstabilized free group and suppose a
balanced trivial-group checkpoint has

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q,
\]

together with a surviving literal \(q\)-relator. Both q-dependent
primitive-slot targets

\[
Wq
\qquad\text{and}\qquad
Wq^{-1}
\]

are primitive. In a basis containing \(U\), the positive branch uses

\[
\delta_+(q)=qU^{-1}q,
\qquad
\delta_+(U)=q,
\]

while the negative branch uses the involution \(\delta_-\) swapping
\(q\) and \(U\). Thus

\[
Wq^{\pm1}=(\phi\delta_\pm)(q).
\]

After deletion, the surviving q-slot becomes \(U^{-1}\) in the positive
branch and \(U\) in the negative branch. Modulo
\(\langle\!\langle U\rangle\!\rangle\), both new straightening maps equal
the old one. The surviving source therefore returns every other slot to
the original \(W\)-deletion endpoint.

For AK(3),

\[
U=RB=x^3t^{-4}z^{-1}xt
\]

is primitive because it contains \(z^{-1}\) exactly once. The positive
endpoint is

\[
(R,D_+,U^{-1}),
\]

and \((D')^{-1}D_+\) is exactly two conjugates of the surviving
\(U^{\pm1}\)-relator. The negative branch has an exact six-factor
return. Hence both first literal-q target multiplications return to the
rank-three AK(3) root.

## Result 39: coherent complement conjugators close

The complement-conjugator theorem is proved in

```text
literature/proofs/AK3_COMPLEMENT_CONJUGATED_Q_TRAFFIC_SELF_LOOP.md
```

Write

\[
F_0=F(K)*\langle U\rangle
\]

with \(U\) primitive, and suppose the balanced trivial-group checkpoint
has

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q.
\]

For any \(a\in F(K)\), put \(c=\phi(a)\). Both conjugated-source targets

\[
Wcqc^{-1},
\qquad
Wcq^{-1}c^{-1}
\]

are primitive. Their pullbacks contain the basis letter \(U^{\pm1}\)
exactly once:

\[
qaU^{-1}qa^{-1},
\qquad
qaq^{-1}Ua^{-1}.
\]

Straightening and deleting that U-coordinate leaves a conjugate of
\(q^{-1}\) or \(q\), which also deletes. If \(\lambda\) kills \(U\) and
\(q\), both one-U automorphisms satisfy

\[
\lambda\delta_{a,\pm}^{-1}=\lambda.
\]

Thus the final endpoint is literally the old double quotient
\(\lambda\phi^{-1}\), not merely equivalent modulo a source.

For AK(3), use

\[
F(x,t,z)=F(x,t)*\langle U\rangle.
\]

The choice \(a=t\) has \(c=\phi(t)=t\), proving both nontrivial literal
targets

\[
Wtqt^{-1},
\qquad
Wtq^{-1}t^{-1}
\]

primitive self-loops. Both delete to

\[
\left(R,\;t^{-1}(xtR)x(xtR)^{-1}\right),
\]

whose second relator differs from the standard rank-two AK relator
\(t^{-1}(xt)x(xt)^{-1}\) by exactly two conjugates of \(R^{\pm1}\).

## Result 40: arbitrary z-free q-source traffic closes

The unique-z theorem is proved in

```text
literature/proofs/AK3_Z_FREE_Q_TRAFFIC_SELF_LOOP.md
```

At the fixed AK source-slot checkpoint, write

\[
W=\beta(R)z^{-1}\beta(xt)q.
\]

For every finite z-free q-source history, its total target multiplier is
an arbitrary

\[
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}.
\]

Then

\[
Wv
=
\beta(R)z^{-1}\bigl(\beta(xt)qv\bigr)
\]

contains \(z^{-1}\) exactly once and is primitive. The explicit
orientation-reversing automorphism sends \(z\) to \(Wv\) and fixes
\(x,t,q\). After deleting z, the q-relator remains literal and also
deletes.

The double quotient is independent of \(v\): since \(v\) vanishes under
\(q\mapsto1\), the inverse automorphism sends

\[
z\longmapsto xtR.
\]

Consequently every such history gives

\[
\left(R,\;t^{-1}(xtR)x(xtR)^{-1}\right),
\]

which returns to the standard rank-two AK endpoint by two conjugates of
\(R^{\pm1}\).

This closes arbitrary products of z-free conjugates of
\(q^{\pm1}\), with no bound on their number, word length, conjugators, or
q-occurrences. In particular, both literal \(x\)-conjugator branches are
self-loops.

## Result 41: the full q-source normal closure closes

The source-first theorem and its literal-z target obstruction are proved
in

```text
literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md
```

At the same fixed source-slot checkpoint, let

\[
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,z,q)}
\]

be arbitrary. The q-source traffic lemma gives

\[
(\beta(R),Wv,D,q)
\]

with the final q-slot restored literally. Delete that source slot first.
Killing q sends the remaining tuple exactly to

\[
(R,U,D),
\qquad
U=Rz^{-1}xt,
\]

independently of \(v\). The word \(U\) is primitive via

\[
z\longmapsto Rz^{-1}xt,
\qquad
\nu^{-1}(z)=xtz^{-1}R.
\]

Straightening and deleting \(U\) gives

\[
(R,E_R),
\qquad
E_R=t^{-1}(xtR)x(xtR)^{-1}.
\]

With \(E_0=t^{-1}(xt)x(xt)^{-1}\), the exact identity

\[
E_0^{-1}E_R
=
\bigl((xtx^{-1})R(xt^{-1}x^{-1})\bigr)
\bigl((xt)R^{-1}(xt)^{-1}\bigr)
\]

returns \(E_R\) to \(E_0\) by two retained-\(R\) source factors.
Therefore every finite target history in the full normal closure of the
restored q-source is a stable self-loop, with no restriction on
z-occurrences, conjugators, signs, factor count, or word length.

There is nevertheless a sharp local obstruction to deleting the changed
target first. All four exact words

\[
Wz^\delta q^\epsilon z^{-\delta},
\qquad
\delta,\epsilon\in\{+1,-1\},
\]

are nonprimitive. Explicit Whitehead reductions give two terminal common
graphs containing spanning cycles on all eight signed basis vertices, so
the cut-vertex lemma applies. This nonprimitivity does not obstruct the
source-first deletion above. Result 41 supersedes Result 40's z-free
restriction for stable closure, but not Result 40's stronger assertion
that its changed target itself is primitive.

## Result 42: passive-source changes to the q-slot are gauges

The changed-source theorem is proved in

```text
literature/proofs/AK3_CHANGED_Q_SOURCE_GAUGE_SELF_LOOP.md
```

Let \(S_1,\ldots,S_k\) be q-free passive source slots, put

\[
L=\langle\!\langle S_1,\ldots,S_k\rangle\!\rangle,
\]

and take \(V\in L\). Change the literal stabilizer source to

\[
Q=qV
\]

while leaving the passive sources literal through this manufacture. The
word \(Q\) is primitive. Straightening and deleting it evaluates

\[
q\longmapsto V^{-1}.
\]

Modulo \(L\), this is exactly ordinary q-deletion. Moreover, every
subsequent target multiplier in
\(\langle\!\langle Q\rangle\!\rangle\) vanishes in that quotient.
This includes later \(Q\)-traffic into the passive slots themselves:
they return literally after deletion and restore every other survivor
to the ordinary-q endpoint by classical AC moves. This covers arbitrary
finite \(Q\)-source traffic, provided \(Q\) itself is not changed again
and is deleted first.

For AK(3), keep \(D=t^{-1}zxz^{-1}\) passive and take \(Q=qD\). Deletion
gives

\[
(R_D,W_D,D),
\]

where

\[
R_D=D^{-1}x^3Dt^{-4},
\qquad
W_D=R_Dz^{-1}(D^{-1}xDt)D^{-1}.
\]

Two explicit D-source factors return \(R_D\) to \(R\), five return
\(W_D\) to \(U=RB\), and the identity

\[
U^{-1}B=B^{-1}R^{-1}B
\]

returns \(U\) to \(B\) by one R-source factor. Thus the first nonliteral
source \(qD\), including arbitrary traffic from it into the other
slots, gives no new classical endpoint.

## Result 43: coherently transported q-source changes are gauges

The transported-source theorem is proved in

```text
literature/proofs/AK3_TRANSPORTED_Q_SOURCE_GAUGE_SELF_LOOP.md
```

Let \(R_1,\ldots,R_k\) be q-free retained sources, let \(V\) lie in
their joint normal closure, and suppose

\[
\beta(q)=q,
\qquad
\rho\beta=\rho.
\]

At a checkpoint carrying the coherent source slots \(\beta(R_i)\), the
q-dependent word

\[
Q=\beta(qV)=q\beta(V)
\]

is primitive and can be manufactured from those sources. Straightening
and deleting \(Q\) uses

\[
\sigma=\rho\delta_V^{-1}\beta^{-1}.
\]

It returns every coherent carrier \(\beta(R_i)\) literally to \(R_i\).
Modulo their joint normal closure, \(\sigma\) agrees with ordinary
q-deletion, while all later traffic from
\(\langle\!\langle Q\rangle\!\rangle\) vanishes. Thus this entire
coherently transported q-dependent source family is a retained-source
gauge.

For AK(3), take \(V=R\). The source

\[
Q=q\beta(R)=\beta(qR)
\]

deletes, independently of arbitrary later \(Q\)-source traffic, to

\[
\left(
R,\;
RBR^{-1},\;
t^{-1}zRxR^{-1}z^{-1}
\right).
\]

One AC3 conjugation returns the middle relator to \(B\). The exact
difference of the last relator from \(D\) is

\[
\bigl((zx^{-1})R(xz^{-1})\bigr)
\bigl(zR^{-1}z^{-1}\bigr),
\]

so two retained-R factors return it to \(D\). Hence \(q\beta(R)\) gives
no new classical endpoint.

## Result 44: every signed qW changed source cancels with W

The two-source cancellation theorem is proved in

```text
literature/proofs/AK3_QW_SOURCE_PAIR_CANCELLATION_SELF_LOOP.md
```

At the fixed source-slot checkpoint, write

\[
A=\beta(R),
\qquad
C=\beta(xt)q,
\qquad
W=Az^{-1}C.
\]

For every sign pair,

\[
Q_{\eta,\epsilon}=q^\eta W^\epsilon,
\qquad
\eta,\epsilon\in\{+1,-1\},
\]

contains z exactly once and is primitive. Explicit triangular
z-coordinate automorphisms straighten all four words. Deleting
\(Q_{\eta,\epsilon}\) first sends the surviving W-slot uniformly to

\[
q^{-\eta\epsilon}.
\]

Thus a second literal q-deletion is available, after inversion when
necessary. Before that second deletion, the D-slot has form

\[
t^{-1}E_sxE_s^{-1},
\qquad
E_s=Cq^{\eta\epsilon}A.
\]

Killing q sends \(A\mapsto R\) and \(E_s\mapsto(xt)R\), independently
of both signs. Every branch therefore reaches

\[
\left(
R,\;
t^{-1}(xtR)x(xtR)^{-1}
\right).
\]

The standard two retained-R factors return this to the rank-two AK
endpoint. Arbitrary later traffic from
\(\langle\!\langle Q_{\eta,\epsilon}\rangle\!\rangle\), including
traffic into any survivor slot, vanishes in the first deletion. Hence
all four incoherent source products \(q^\eta W^\epsilon\) are
self-loops.

## Result 45: coherent qW tails transfer and close

The transported-tail theorem is proved in

```text
literature/proofs/AK3_QW_TRANSPORTED_TAIL_SELF_LOOP.md
```

Let \(V\) be any q-free, z-free consequence of R in \(F(x,t)\). The
longer changed sources

\[
Q_{\eta,\epsilon,V}
=
q^\eta W^\epsilon\beta(V)
\]

still contain z exactly once and are primitive. Their first deletion
transfers the coherent right tail into the surviving W-slot:

\[
W\longmapsto
\bigl(\beta(V)q^\eta\bigr)^{-\epsilon}.
\]

This transferred word is primitive via the left q-coordinate

\[
\ell_{V,\eta}(q)=Vq^\eta
\]

followed by \(\beta\). Delete it next. The exact second
straightening-and-deletion map has the essential inner-letter image

\[
\rho\theta_{\eta,V}^{-1}(x)
=
V^\eta xV^{-\eta}.
\]

Consequently every W-orientation gives

\[
\left(
R,\;
t^{-1}(pH_{V,\eta})x(pH_{V,\eta})^{-1}
\right),
\qquad
H_{V,\eta}=V^{-\eta}RV^\eta.
\]

The word \(H_{V,\eta}\) is one conjugate of R. Therefore the exact
difference from the standard rank-two AK relator is a product of just
two conjugates of \(R^{\pm1}\), independent of the length or
normal-closure factorization of V. For \(V=R\), all four sign branches
land at the familiar \(E_R\) endpoint.

Arbitrary later traffic from
\(\langle\!\langle Q_{\eta,\epsilon,V}\rangle\!\rangle\) into any
survivor vanishes in the first deletion. Thus the entire coherent
z-free tail family is a two-deletion self-loop.

## Result 46: the first z-dependent D-tail has two primitive rows

The exact rank-four Whitehead classification is proved in

```text
literature/proofs/AK3_Z_DEPENDENT_D_TAIL_PRIMITIVITY.md
```

For

\[
Q_{\eta,\epsilon,\delta}
=
q^\eta W^\epsilon D^\delta,
\qquad
\eta,\epsilon,\delta\in\{+1,-1\},
\]

exactly two of the eight sign rows are primitive:

\[
\boxed{
qW^{-1}D,
\qquad
qW^{-1}D^{-1}.
}
\]

Explicit strict Whitehead descents of 12 and 13 steps take these words
to \(q^{-1}\) and \(z^{-1}\), respectively. Every move is replayed
against the complete dependency-free rank-four list of second-kind
Whitehead automorphisms.

For each of the other six rows, explicit Whitehead moves produce a
cyclically reduced terminal word whose Whitehead graph contains a
spanning cycle through all eight signed basis vertices. Each graph is
therefore connected and has no cut vertex. Whitehead's cut-vertex lemma
proves all six rows nonprimitive.

This closes primitive-single deletion for six of the eight first
z-dependent D-tails. Since every component of a primitive pair is
individually primitive, it also excludes any direct primitive pair
containing one of those six unchanged rows. It does not yet compute the
stable deletion endpoints of the two primitive exceptions or classify
pair creation after an AC product changes a row.

## Result 47: every qW-inverse D-power pair merges into the floor-14 corridor

The structural pair-compression theorem is proved in

```text
literature/proofs/AK3_QW_D_POWER_TAIL_COMPRESSION_MERGE.md
```

Put

\[
S=Wq^{-1}
=
\beta(Rz^{-1}xt).
\]

A based eleven-step Whitehead certificate proves that the ordered pair

\[
\left(
Rz^{-1}xt,\;
\beta^{-1}(D)
\right)
\]

extends to a basis. After restoring \(\beta\), one obtains an
automorphism \(\theta\) satisfying

\[
\theta(S)=z^{-1},
\qquad
\theta(D)=t^{-1}.
\]

For every integer k,

\[
Q_k=qW^{-1}D^k=S^{-1}D^k.
\]

The triangular shear \(z\mapsto zt^k\) therefore sends
\((\theta(Q_k),\theta(D))\) exactly to \((z,t^{-1})\). Thus
\((Q_k,D)\) is a based primitive pair for all
\(k\in\mathbb Z\), with no bound or finite census.

More generally,

\[
D^a qW^{-1}D^b
\]

is conjugate to \(qW^{-1}D^{a+b}\). Thus every D-only left/right split
around one \(qW^{-1}\) block has the same pair quotient.

Deleting this pair from the full checkpoint tuple gives one
k-independent rank-two pair. Its complete Whitehead floor is 23.
One ordinary retained-source AC factor lowers it, and a stable ambient
signed relabel maps it to

```text
YXXYx | YYYYXyyyx
```

the exact floor-14 representative already proved to occur in the
rank-three compression corridor. The classical factor alone does not
identify the endpoints; the final ambient step is stable.

For the two first powers \(k=\pm1\), complete rank-three survivor
classification proves more: after deleting \(Q_k\), the D-image is the
unique primitive survivor. The two exceptional primitive-single rows
from Result 46 therefore have no alternative second primitive-single
branch at that checkpoint.

This closes all D-only traffic around one \(qW^{-1}\) block and the
immediate primitive-single second deletion of the two first powers by
merging them into a previously certified stable corridor. The six
nonprimitive sign rows are already excluded from direct primitive
pairs. What remains open is pair creation after a row-changing AC
product, longer histories changing a displayed survivor, or histories
containing another \(Wq^{-1}\) block.

## Result 48: all integer D-tail primitivity is classified

The unbounded classification is proved in

```text
literature/proofs/AK3_ALL_INTEGER_D_TAIL_PRIMITIVITY.md
```

For every sign pair and every integer k,

\[
\boxed{
q^\eta W^\epsilon D^k
\text{ is primitive}
\quad\Longleftrightarrow\quad
k=0
\ \text{or}\
(\eta,\epsilon)=(+1,-1).
}
\]

The four \(k=0\) rows are unique-z coordinates. The entire
\((+,-)\) row is primitive by Result 47's based
\((Wq^{-1},D)\) coordinate and triangular Nielsen shear.

For each of the other three orientations with \(k\ne0\), one common
rank-four Whitehead automorphism produces a fixed length-13 boundary
block followed by \(D^k\). Five explicit Whitehead-graph cycles cover
the three orientations and both signs of k. Each cycle visits all
eight signed basis vertices. Repeating \(D\) or \(D^{-1}\) preserves
every cycle edge and only adds block-seam edges, so the connected
no-cut-vertex obstruction holds for every nonzero power, not merely a
finite sweep.

More generally,

\[
D^a q^\eta W^\epsilon D^b
\]

is primitive exactly when \(a+b=0\) or
\((\eta,\epsilon)=(+1,-1)\), since conjugation by \(D^{-a}\) reduces
it to the right-tail row with exponent \(a+b\).

Because every member of a primitive pair is individually primitive,
the negative rows cannot be paired directly with any unchanged
relator. The next genuine gate must first use an AC2 product to change
one row and then test whether the new row or pair is primitive.

## Result 49: cyclic one-edge D-tail creation has no new endpoint

The complete one-AC2-edge classification is proved in

```text
literature/proofs/AK3_D_TAIL_ONE_EDGE_PRIMITIVE_CREATION.md
```

At each of the six nonprimitive first D-tail checkpoints, exhaust one
AC2 multiplication between signed cyclic representatives of Q and one
of A, W, D, in both target directions. Arbitrary relative conjugators
between the two factors are not part of this finite image.

There are 12,992 literal representatives after quotienting the
redundant target inversion, or 25,984 if that orientation is indexed
separately. They give 9,480 direction-tagged child states and 4,720
global changed-word classes. A Whitehead-graph gate followed by
complete descent under all 504 rank-four second-kind maps leaves
exactly six primitive child classes, occurring in 28 states.

Complete labeled-tuple transport gives two different counts:

- 30 direct primitive-pair incidences, split as 18 copies of the
  known floor-23 compression orbit and 12 of the floor-27 qW
  backtrack orbit;
- 32 sequential primitive-single continuations, split as 20 copies
  of floor 23 and 12 of floor 27.

The extra two sequential branches occur when a mixed-sign D-target
child is deleted and the original Q becomes primitive only in the
quotient. Its direct rank-four pair has minimum 28, not 2. This is an
alignment issue: independently conjugated primitive conjugacy classes
do not make the literal product alignment into a based primitive pair.

Thus every direct primitive-pair deletion in this cyclic image, and
every sequential deletion which removes the changed primitive row
first, returns to a known endpoint orbit. None reaches a new rank-two
orbit or floor at most 12. Still open are arbitrary relative
conjugators, alternate first-deletion orders, an edge solely among the
carriers A, W, D while retaining the nonprimitive Q, and two
row-changing edges before deletion.

## Result 50: cyclic carrier edges return only to AK(3)

The complete carrier-edge classification is proved in

```text
literature/proofs/AK3_CARRIER_EDGE_PRIMITIVE_CREATION.md
```

At each of the six nonprimitive D-tail checkpoints, exhaust the
signed-cyclic image of one relator multiplication between two of A, W,
D, in both target directions.

The quotient model contains 5,544 literal representatives, or 11,088
if redundant target inversion is separately indexed. It has 4,104
checkpoint-direction-child states and 342 global child classes.

All 186 A--W classes are primitive by an explicit unique-z coordinate.
None of the 58 A--D classes is primitive. Exactly four of the 98 W--D
classes are primitive. Complete pair descent proves that none of these
primitive children forms a direct primitive pair.

After changed-row-first deletion, 2,268 of the 2,280 primitive-child
states have no primitive rank-three survivor. The other 12 are the
single A-block cancellation

\[
H=\operatorname{can}(A^{-1}W)=C^{-1}z.
\]

The straightener \(z\mapsto Cz\), followed by \(\beta^{-1}\), maps
every sign row uniformly to

\[
(R,E,q^\eta R^\epsilon E^\delta),
\qquad
R=x^3t^{-4},
\quad
E=t^{-1}xtxt^{-1}x^{-1}.
\]

The last word has exactly one \(q^{\pm1}\). Deleting it leaves the same
literal pair \((R,E)\) in all signs and both directions, with canonical
representative

```text
XXXXYYY | XYxYXy
```

at floor 13: the original rank-two AK(3) orbit `13_1`. The ambient
straightening and primitive deletions make this a stable self-loop;
this is not a claim of a classical rank-two AC identification. Thus
the entire finite carrier-edge stratum has no new endpoint and none of
floor at most 12.

## Result 51: unchanged-primitive-first carrier orders close

The source-first and non-source theorem is proved in

```text
literature/proofs/AK3_UNCHANGED_PRIMITIVE_FIRST_CLOSURE.md
```

For an edge

\[
T\longmapsto TuS^\sigma u^{-1}
\]

with an unchanged primitive source S, deleting S first kills the
conjugated factor exactly. This is quotient naturality and holds for
every relative conjugator u, with no word-length bound. At the current
checkpoints it covers Q targeted by W or D and the four carrier orders

\[
A\leftarrow W,\quad
A\leftarrow D,\quad
W\leftarrow D,\quad
D\leftarrow W.
\]

Within the signed-cyclic carrier image, the only non-source
unchanged-primitive-first choices are D-first after an A--W edge and
W-first after an A--D edge. Their complete rank-three image has 2,928
labeled states:

\[
2{,}184\text{ have no primitive survivor},\qquad
744\text{ have Q as the unique primitive survivor}.
\]

The positives occur exactly in the two mixed
\((\eta,\epsilon)=(-,+)\) rows. After Q deletion, the carrier edge
descends in Result 47's fixed double-deletion coordinate to a
multiplication by a conjugate from the known floor-23 baseline pair.
This is a short classical AC sequence. Arbitrary straightener outputs
are Aut-equivalent to those fixed-coordinate representatives, so the
conclusion for the whole image is stable rather than a classical
identification of every displayed pair.

There are 154 distinct normalized final pairs in each target direction.
The two sets are disjoint. Complete Aut-minima are at least 19 when A
was targeted and at least 14 when W was targeted. No endpoint has floor
at most 12.

Thus every unchanged-primitive-first order in the signed-cyclic carrier
stratum is closed. The source-first part is stronger and already covers
arbitrary relative conjugators; the non-source arbitrary-conjugator
family remains open.

## Result 52: z-free A--W relative conjugators are unbounded self-loops

The unbounded theorem is proved in

```text
literature/proofs/AK3_Z_FREE_AW_RELATIVE_CONJUGATOR_SELF_LOOP.md
```

Let \(H=F(x,t,q)\). For arbitrary \(u\in H\) and
\(\sigma=\pm1\), consider either normalized target direction

\[
W\longmapsto WuA^\sigma u^{-1},
\qquad
A\longmapsto AuW^\sigma u^{-1}.
\]

Each changed row contains exactly one z-letter and is therefore
primitive. The two directions require different literal straighteners:
the A-target direction replaces u by \(u^{-1}\) and leaves the old W-row
as a conjugate of \(A^{\pm1}\), which relator inversion and conjugation
restore to A.

In both directions, changed-row deletion reduces the surviving tuple
to

\[
(A,D_V,q^\eta V^{-\epsilon}D_V^\delta),
\qquad
D_V=t^{-1}(CVA)x(CVA)^{-1},
\]

with \(V\) a conjugate of \(A^{\pm1}\). Because
\(V\in\langle\!\langle A\rangle\!\rangle\), the fixed-source
normal-closure lemma gives the classical rank-three reduction

\[
(A,D_V,q^\eta V^{-\epsilon}D_V^\delta)
\sim_{\rm AC}
(A,D_0,q),
\qquad
D_0=t^{-1}CxC^{-1}.
\]

Stable q-deletion leaves

\[
(R,E)=(\texttt{xxxTTTT},\texttt{TxtxTX}),
\]

the floor-13 AK(3) orbit. Thus this entire unbounded z-free family is a
stable self-loop in both target directions and for all six checkpoints.

For \(n\ge1\), the family \(u=q^n\) gives pairwise distinct primitive
children of cyclic length \(22+2n\); the members with \(n\ge2\) go
strictly beyond the finite cyclic census. The z-free hypothesis cannot
be removed wholesale: already \(u=xz\) in the positive W-target branch
gives a nonprimitive word with complete rank-four Whitehead minimum 14.

## Result 53: arbitrary Q--carrier relative products add no primitive class

The seam-robust theorem is proved in

```text
literature/proofs/AK3_SEAM_ROBUST_RELATIVE_PRODUCT_CLOSURE.md
```

For each of the six nonprimitive D-tail Q-rows, a row-specific
automorphism makes every linear cut of the transformed cyclic word
contain a Hamiltonian cycle on all eight signed basis vertices.

Now take an arbitrary relative product between that Q-row and A, W, or
D. In the transformed Cayley tree, split the two factor axes:

- if they are disjoint, shortest-bridge normal form leaves a full
  linear-cut Q-graph inside the child Whitehead graph, so the child is
  connected with no cut vertex and is nonprimitive;
- if they intersect, basing both factors at an intersection vertex
  reduces the child to a finite product of signed cyclic rotations in
  the transformed basis.

The six complete transformed rotation tables map back to exactly Result
49's six primitive changed conjugacy classes, with the same checkpoint
and carrier labels. There is no additional primitive class for an
arbitrary-length conjugator.

Because only the changed target row differs, conjugating or inverting
it to the Result 49 representative makes the full labeled tuple one of
the already transported states. Hence the exact class-state and endpoint
counts remain:

\[
\begin{array}{c|c}
\text{direct primitive-pair endpoints}&
18\mathcal F_{23}+12\mathcal F_{27}\\
\text{changed-row-first sequential endpoints}&
20\mathcal F_{23}+12\mathcal F_{27}.
\end{array}
\]

The relative-conjugator witness set is infinite, so the old finite
literal multiplicities do not extend. The primitive class and endpoint
classification does.

## Live lead

The direct relation-splitting manufacture of
\[
V_3=qx^3q^{-1}t^{-4}q
\]
is now closed. In fact the same theorem closes every arbitrarily long
\(\beta(U)q\) with \(U\in\langle\!\langle R\rangle\!\rangle\) and
\(\rho\beta=\rho\). A productive use must leave at least one survivor
outside its baseline class modulo the retained \(R\), or must change the
normal closure of the retained \(R\)-slot. Merely leaving the survivors
untransported is insufficient: after deletion their apparent asymmetry
is absorbed by \(R\)-source AC moves.

Merely cross-coupling retained sources is now closed as well. Targeting
and deleting a quotient-equal source slot also fails: the surviving
stabilizer relator becomes \(U^{-1}\) and recovers the deleted normal
generator. Within the relative-transvection family, the next minimal
branch cannot be post-manufacture traffic which avoids target
multiplication into the primitive slot: all such traffic descends through
deletion. Result 38 also closes multiplication by the surviving literal
\(q^{\pm1}\)-slot, despite its q-dependent pullback. Result 39 closes
every coherent conjugator pulled back from a complement to \(U\), and
Result 41 closes
the full normal closure of the restored literal q-source, including
arbitrary z-dependent traffic. Result 42 also closes every changed source
\(qV\) carried by passive q-free sources that remain distinct; in
particular, \(qD\) is a gauge. Result 43 closes the coherent q-dependent
extension \(q\beta(V)=\beta(qV)\); in particular, \(q\beta(R)\) is also a
gauge. Result 44 closes the first incoherent pair source
\(q^\eta W^\epsilon\) in all four orientations, even with arbitrary
later traffic from that changed source. Result 45 closes every longer
pair source with a coherent z-free tail
\(q^\eta W^\epsilon\beta(V)\). Result 46 classifies the first
z-dependent tails \(q^\eta W^\epsilon D^\delta\): six sign rows are
nonprimitive, while exactly \(qW^{-1}D^{\pm1}\) survive the
primitive-single gate. Result 47 closes their immediate second
primitive-single gate: D is the unique primitive displayed survivor,
and both signs merge into the old floor-14 compression corridor. More
structurally,
\((qW^{-1}D^k,D)\) is a based primitive pair with the same quotient for
every integer k. Result 48 classifies every signed integer D-tail and
every D-only left/right split: outside zero total power, only the
positive inverse-W orientation is primitive. Result 49 exhausts the
signed-cyclic image of one multiplication between each nonprimitive
first D-tail and one carrier, in both target directions. Primitive rows
and pairs do occur, but all 30 direct pair deletions and all 32
changed-row-first sequential branches return to the known floor-23
compression or floor-27 backtrack orbits. Result 50 closes the
signed-cyclic carrier-carrier image as well: it has no direct primitive
pair, and its only 12 changed-row-first second deletions are one
A-block cancellation returning exactly to AK(3)'s floor-13 orbit. The
signed-cyclic alternate first-deletion order is closed by Result 51 as
well; source-first deletion is even insensitive to arbitrary relative
conjugators. Result 52 additionally closes every changed-row-first A--W
edge whose normalized relative conjugator is z-free. Result 53 closes
arbitrary relative conjugators on every Q--carrier edge for direct-pair
and changed-row-first deletion. The immediate exact leads are therefore
z-dependent A--W conjugators, arbitrary A--D or W--D conjugators,
non-source deletion, or two row-changing edges
before deletion. Longer branches may use additional \(Wq^{-1}\) blocks,
alter W by traffic with nontrivial first-deletion image, delete or alter
a needed carrier, change the fixed checkpoint, or choose a different
primitive slot. The exact Fox coordinate remains a necessary free-kernel
certificate.

Primitive-pair compression before either old generator is removed also
remains open. Short templates produce the floor-16 corridor above. A
broader visible-block pass returned only to AK(3)'s floor-13 classical
class, but that finite observation remains unverified.

The target is a hidden-cancellation or longer \(F_4\) primitive pair whose
rank-two quotient has complete Aut-floor at most 12.  A primitive full
four-relator tuple would be an immediate stable solve.  The entire
one-source mechanism which retains \(x^3=t^4\), chooses an arbitrary
quotient-equal recovery \(U=t\), and eliminates through \(z=xU\) is now
closed as a classical AC self-loop, with no word-length bound.

The remaining one-stabilization routes must leave at least one exact
hypothesis of the self-loop theorems.  The simplest one-\(D\) catalyst is
closed even with an arbitrary conjugator when it targets the literal
\(B=z^{-1}xt\).  More strongly, after arbitrary recovery, the complete
one-\(D\), one-\(z\)-elimination stratum is closed for both target/source
roles.

Every fixed-\(R\) ordering with exactly one \(B/D\) cross multiplication
and a final one-\(z\) eliminator is now closed.  If the cross target is
eliminated, the quotient axis theorem returns it to one of two standard
catalyst endpoints.  If the restored source is eliminated, passive-source
absorption closes the \(B\)-source branch and the \(D\)-source branch is
impossible by \(z\)-exponent.

Every one-way history and every exactly-two-cross alternating history with
a final one-\(z\) eliminator and the stated restoration condition is now
closed.  The complete three-event classification and final-target
duality leave exactly one killer mechanism: prefix \(DB\), followed by
either final target choice.  A genuinely new exactly-three-cross endpoint
must use one of its six sign rows and nontrivial relative bridge,
vertex-twist, or literal \(R\)-gauge geometry.  The two target spellings
give the same classical endpoint class, and both literal untwisted
corridors return exactly to \(D_p\).  Weight plus cyclic conjugacy in
\(C_3*C_4\) is now an exact decision procedure for whether any resulting
survivor is conjugate to \(D_p^{\pm1}\) in the retained torus-knot
quotient.

The evaluated quotient equation is not enough: it has a weight-one killer
solution outside the conjugacy classes of \(D_p^{\pm1}\), but the
quotient-\(B\) commutator sieve proves that explicit solution nonliftable.
The quotient-\(B\) theorem puts every non-braid commutator row at quotient
cyclic length at least \(8\), and both same-orientation rows at length at
least \(6\).

At the minimum same-orientation length, the first evaluated cross equation
is no longer a barrier.  A repositioned non-braid killer in the dual row
satisfies all three evaluated equations and the exact synchronized
\(z=e,p\) quotient shadow.  The literal \(G\)-bridge lift fails, but only
because its word in the free evaluation kernel has cyclic length \(7\)
instead of \(1\).  The immediate frontier is the explicit three-variable
equation \(n_3(U,V,W)\): either make it conjugate to a negative Schreier
basis letter, producing a genuine one-\(z\) target, or find an invariant
excluding every \(U,V,W\).

The full Fox equation for the repositioned minimum-tail candidate is now
closed for every target. The HNN forest supplies the unique path for
each target that passes its component/parity criterion, but all such
paths have support in \(QJ\) after the central translation. A fixed
coset outside \(QJ\) obstructs the residual module equation. There is
therefore no nonabelian basis-letter equation left to solve in this
candidate.

The signed master lemma now supplies the same exact HNN reduction in
every sign row. The four \(m=-1\) rows do not occur at the global
minimum quotient-\(B\) length six, and the old literal representatives
in the other length-six row \((-,+,+)\) fail the first evaluated
equation. A row-to-row extension therefore starts by constructing a
repositioned evaluated \((-,+,+)\) candidate; only then is there a
concrete \(Q\)-\(J\) support vector to decide.

Other remaining routes can use four or more cross events, fail
restoration, change the retained relator or recovery equation, produce a
primitive eliminator with several \(z\)-letters, use the braid relator
during recovery, or compress both source relators before either old
generator is removed.

The multi-\(z\) phrase is no longer unconstrained. Literal free-kernel
candidates collapse to conjugates of the stabilizer, the natural
three-letter split family has one exact primitive member, and its direct
relation-splitting production is a stable self-loop. Even arbitrary
consequences of a retained multi-source subtuple close. The open branch
must lose a needed source normal closure without having the surviving
stabilizer restore it, or change the survivor quotient class; bare
asymmetry, retained-source cross-coupling, and quotient-equal source
deletion are insufficient. Arbitrary later AC1--AC3 traffic is also
insufficient when it comes from the restored literal q-source, even when
its conjugators involve \(z\). Passive-source changes \(qV\) do not help
either while their q-free carrier sources survive, and coherent
transported changes \(q\beta(V)\) are gauges as well. Even the first
incoherent products \(q^\eta W^\epsilon\) cancel against the surviving
W-slot, and arbitrary coherent z-free tails merely transfer into a
second deletable source. Among the first z-dependent D-tails, only
\(qW^{-1}D^{\pm1}\) are primitive, and their forced immediate
primitive-single second deletions merge into the old floor-14 sibling.
In fact every signed D-only split has now been classified: outside
zero total D-power, only the positive inverse-W orientation is
primitive, and its pair quotient is the old floor-14 route. The
signed-cyclic image of one product between any of the six nonprimitive
first D-tails and A, W, or D is also closed in both target directions
for direct pair deletion and changed-row-first sequential deletion.
The signed-cyclic carrier-carrier image is closed too: no direct pair
is primitive, and its only changed-row-first continuation is the
A-block cancellation returning to AK(3) itself. All signed-cyclic
unchanged-primitive-first orders are now closed too. Source-first
deletion is a quotient gauge for every relative conjugator;
signed-cyclic non-source deletion either stops or returns by a short
classical sequence in a fixed deletion coordinate, hence stably to the
old floor-23 corridor. Even arbitrary z-free A--W conjugators are now
closed under changed-row-first deletion; they collapse by the retained
A-normal closure and a second stable q-deletion. Arbitrary Q--carrier
relative conjugators add no primitive class either: seam-robust
transformed Q-rows force every primitive case back into Result 49's
finite table. A different viable primitive-slot branch must use
z-dependent A--W traffic, arbitrary A--D or W--D relative traffic,
non-source deletion, two row changes before deletion, another
\(Wq^{-1}\) block, a repeatedly changed source, alter W by traffic with
nontrivial first-deletion image, lose a needed carrier source, use
traffic with nontrivial deletion image, or draw from a source outside
the retained normal closure.

AK(3) remains open.
