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

The full Fox equation is now reduced to a single cyclic-submodule problem
in \(\mathbb Z[P\backslash G]\), where \(P\cong F_2\) is center-free and
infinite-index. The binary \(S_4\) lift repairs the first quotient's loss
of central sign: the identity and \(g=\gamma e^{-1}\) targets are now
excluded, while every surviving finite image lies in
\((-I)\rho(P)\). The simplest surviving exact target is \(g=c^{-1}\).
The next exact test is

\[
-[Pc^{-1}]-\pi_P(A_0)
\stackrel{?}{\in}
\pi_P(A_U)\mathbb Z[G].
\]

A second finite representation with a disjoint target-orbit condition
would prove Fox nonliftability. Otherwise the nine-edge folded core now
provides the exact infinite coset normal form needed for a direct
coloring or module-membership proof. Fox success would still leave the
nonabelian basis-letter equation. Even a liftable non-braid survivor
would refute only this direct fixed-\(R\) finish, not stable AC.

Other remaining routes can use four or more cross events, fail
restoration, change the retained relator or recovery equation, produce a
primitive eliminator with several \(z\)-letters, use the braid relator
during recovery, or compress both source relators before either old
generator is removed.

AK(3) remains open.
