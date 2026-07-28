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

## Result 54: arbitrary A--W products close in the D-then-Q order

The quotient theorem is proved in

```text
literature/proofs/AK3_ARBITRARY_AW_D_THEN_Q_CLOSURE.md
```

Perform an arbitrary A--W relative product, delete unchanged D first,
and then consider the unchanged Q-row. Because the edge changes neither
D nor the separately retained Q word, its image under the fixed D
quotient is literally the baseline image for every conjugator.

Exactly the two mixed rows

\[
Q_{-1,+1,\delta}=q^{-1}WD^\delta,
\qquad
\delta=\pm1,
\]

are primitive there. Use Result 47's fixed double quotient and write
the exact raw surviving A--W pair as \((a,w)\). For
\(c=\pi_\delta(u)\), the two target directions become

\[
(a c w^\sigma c^{-1},w),
\qquad
(a,w c a^\sigma c^{-1}).
\]

Each is classically AC-equivalent to the raw baseline \((a,w)\) by a
multiplication-by-conjugate sequence. A fixed rank-two ambient
coordinate places that baseline in the displayed floor-23 Aut-orbit,
so the full conclusion is stable: every such arbitrary-conjugator
D-then-mixed-Q branch returns to the old corridor.

This does not classify a newly primitive changed carrier after D
deletion, a primitive pair involving it and Q, the nonmixed Q rows, or
intervening traffic.

## Result 55: arbitrary A--D products satisfy a Fox exponent sieve

The unbounded obstruction is proved in

```text
literature/proofs/AK3_AD_RELATIVE_PRODUCT_FOX_SIEVE.md
```

Normalize either target direction and both carrier orientations to

\[
P_\sigma(c)=A\,cD^\sigma c^{-1}.
\]

At the abelian character \(x=t=1\), \(q=4z/3\), both A and D evaluate
to one. The conjugator derivative therefore disappears from the
abelianized Fox row, leaving

\[
\nabla P_\sigma(c)
=
(3q+\sigma\lambda z,-4-\sigma\lambda,0,0),
\qquad
\lambda=\overline c.
\]

Writing \(k=e_q(c)\) and \(n=e_q(c)+e_z(c)\), a common torus zero
exists whenever \(n\ne0\). When \(n=0\), a modular witness exists
except for

\[
(\sigma,k)=(+,1),\quad(-,0),\quad(-,1).
\]

A primitive word has a unimodular abelianized Fox row, so every detected
case is nonprimitive. Thus arbitrary A--D primitivity is confined to
those three normalized exponent classes. They are residual classes of
this character slice, not claimed primitive families.

## Result 56: the A--D sieve is noncommutatively exact

The induced-module refinement is proved in

```text
literature/proofs/AK3_AD_INDUCED_MODULE_SIEVE.md
```

Keep the full projection \(\pi:F(x,t,z,q)\to F(q,z)\), put
\(g=\pi(c)\), and set \(h=qz^{-1}\). The evaluated Fox row is

\[
(3q+\sigma gz,-4-\sigma g,0,0).
\]

If \(g\notin\langle h\rangle\), the subgroup \(\langle h,g\rangle\)
is freely based by \((h,g)\). Give it the character

\[
h\mapsto4/3,\qquad g\mapsto-4\sigma
\]

and induce the resulting one-dimensional right module to \(F(q,z)\).
Its base vector annihilates the Fox row, contradicting the
right-unimodularity forced by primitivity.

Thus \(g=h^m\). Result 55's modular argument on m leaves only

\[
\sigma=+1:\quad\pi(c)=h,
\qquad
\sigma=-1:\quad\pi(c)\in\{1,h\}.
\]

These are exact projection fibers, not primitive families. In
particular, every noncommuting q,z projection is now excluded even if
its exponent sums lie in one of Result 55's old residual classes.

## Result 57: finite quotients erase the A--D HNN index gap

The finite-quotient module barrier is proved in

```text
literature/proofs/AK3_AD_FINITE_QUOTIENT_MODULE_BARRIER.md
```

In every finite quotient of
\(BS(3,4)*\langle z\rangle\), the image of \(x\) has order coprime to
12. This is an exact, unbounded consequence of the conjugacy of
\(x^3\) and \(x^4\), not an inference from a finite group census.

For an arbitrary right module over the finite quotient, the four-state
relations therefore force

\[
vt=v,\qquad 3v(qz^{-1})=4v.
\]

Thus finite quotients erase the \(3\)-versus-\(4\) HNN index gap.
For each of the following three canonical literal representatives,
group-element invertibility and integer identities show that the
four-state vector collapses to zero:

\[
(\sigma,g)=(+1,qz^{-1}),\quad
(-1,1),\quad
(-1,qz^{-1}).
\]

This does not close Result 56's three projection fibers. A conjugator
whose projection is \(1\) or \(qz^{-1}\) can retain a kernel component
in a finite quotient, and that component can still be detected. The
result is a structural barrier to the finite-module route, not an
arbitrary-\(c\) obstruction.

## Result 58: a relative-free \(BS(3,4)\) module obstructs primitivity

The infinite-module construction is proved in

```text
literature/proofs/AK3_AD_BS34_MODULE_OBSTRUCTION.md
```

Put

\[
B=BS(3,4),\qquad G=B*\langle z\rangle,\qquad u=z^{-1}gz.
\]

If the natural homomorphism

\[
B*\langle s\rangle\longrightarrow G,
\qquad s\longmapsto u,
\]

which is the identity on \(B\), is injective, then the exact A--D Fox
row has a nonzero right-module annihilator. Indeed, the right affine
action

\[
r x=r+1,\qquad r y=\frac34r
\]

on \(\mathbb Q\) respects \(yx^3y^{-1}=x^4\). In the permutation
module of all \(\mathbb Q\)-valued functions, the indicator
\(w=\mathbf1_{4\mathbb Z}\) satisfies

\[
wx^4=w,\qquad wy(1+x+x^2)=w(1+x+x^2+x^3).
\]

The two nonzero vectors \(w\) and
\(w(1+x+x^2+x^3)=\mathbf1_{\mathbb Z}\) are linearly independent.
An automorphism can therefore send the first to \(-\sigma\) times the
second. The relative-free hypothesis makes this the action of \(u\).
Induction from \(\langle B,u\rangle\) to \(G\) preserves \(w\ne0\);
with \(v=wz^{-1}\), the three original four-state relations follow
with coefficients on the right.

Result 58 by itself proves nonprimitivity only under the displayed
injectivity hypothesis; at this stage, \(u\notin B\) had not yet been
shown sufficient. Its unresolved residue was every \(u\) for which
the homomorphism fails to be injective, including all \(u\in B\). For
the internal cases
\(g=zbz^{-1}\) in Result 56, the positive and negative \(h\)-fibers
have \(e_y(b)=1\), while the negative identity fiber has \(e_y(b)=0\).
All these internal cases have \(u=b\in B\) and remain unresolved.
Result 59 below determines the injectivity hypothesis exactly and
removes every noninternal element from this residue.

## Result 59: the relative-free condition is exact off the internal subgroup

The free-product theorem is proved in

```text
literature/proofs/RELATIVE_RANK_ONE_FREE_PRODUCT.md
```

For \(P=A*C\) and \(u\in P\), trim the optional \(A\)-syllables from
the two ends of the reduced normal form of \(u\). The homomorphism

\[
A*\langle s\rangle\longrightarrow P,
\qquad s\longmapsto u,
\]

which fixes \(A\), is injective exactly when this \(A\)-trimmed core
has infinite order. The proof is an unbounded normal-form argument:
nonzero powers of an infinite-order word beginning and ending in the
same free factor retain those endpoint factors, so the images of
successive \(s\)-syllables cannot cancel across the intervening
nontrivial \(A\)-syllables. The criterion is genuinely about the
trimmed core, not the order of \(u\) itself.

For the Result 58 application, \(B=BS(3,4)\) is torsion-free. Indeed,
the cyclic group generated by a torsion element fixes a vertex of the
HNN Bass--Serre tree, so that element lies in a conjugate of the
torsion-free vertex group \(\langle x\rangle\). The free product
\(G=B*\langle z\rangle\) is torsion-free by the same fixed-vertex
argument on its Bass--Serre tree.

Consequently, for \(u=z^{-1}gz\),

\[
B*\langle s\rangle\longrightarrow G,\qquad s\longmapsto u,
\]

is injective exactly when

\[
u\notin B
\quad\Longleftrightarrow\quad
g\notin zBz^{-1}.
\]

Result 58 therefore obstructs every noninternal element in each of
Result 56's three projection fibers. The exact remaining residue is
internal:

\[
\begin{array}{c|c}
\text{Result 56 fiber}&\text{unresolved internal class}\\ \hline
\sigma=+1,\ h\text{-fiber}&g=zbz^{-1},\ e_y(b)=1\\
\sigma=-1,\ h\text{-fiber}&g=zbz^{-1},\ e_y(b)=1\\
\sigma=-1,\ 1\text{-fiber}&g=zbz^{-1},\ e_y(b)=0.
\end{array}
\]

None of these three internal classes is claimed obstructed.

## Result 60: the internal module is an exact Bass--Serre flow quotient

The internal right-ideal calculation is recast in

```text
literature/proofs/AK3_AD_INTERNAL_BS34_FLOW_MODULE.md
```

Put

\[
H=\langle x\rangle,\qquad C=\langle x^4\rangle,
\]

and use the right-coset edge and vertex sets

\[
E=C\backslash B,\qquad V=H\backslash B.
\]

For \(v=Hg\), the four incoming and three outgoing half-stars are

\[
I(v)=\sum_{i=0}^{3}e_{x^ig},
\qquad
O(v)=\sum_{j=0}^{2}e_{yx^jg}.
\]

The cyclic right module defined by the first two internal relations is
exactly

\[
\mathbb Q[E]\big/\langle O(v)-I(v):v\in V\rangle.
\]

This is an isomorphism of right modules, not a chosen representation:
\(\mathbb Q[B]/(x^4-1)\mathbb Q[B]\cong\mathbb Q[C\backslash B]\),
and every translate of \(yR_3-R_4\) is one conservation vector.

For an internal element \(b\), the third relation imposes

\[
e_{bg}=-\sigma I(Hg)
\qquad(g\in B).
\]

At a fixed vertex, it therefore assigns the same value to every edge
in the image of the double coset \(CbHg\). This makes the full
double-coset geometry of \(b\), rather than only \(e_y(b)\), the exact
remaining invariant.

Two unbounded local double-coset families collapse the flow module.
If \(b\in H\), all four incoming edges at every vertex equal
\(-\sigma I(v)\), giving

\[
(1+4\sigma)I(v)=0.
\]

If \(b\in yH\), all three outgoing edges equal
\(-\sigma I(v)\), and conservation gives

\[
(1+3\sigma)I(v)=0.
\]

Over \(\mathbb Q\), both coefficients are nonzero for both signs, so
the corresponding quotient is zero. This proves only that the flow
module cannot obstruct these canonical double cosets; it does not
prove their relative products primitive.

The noncanonical flow residue is exact:

\[
\begin{array}{c|c}
e_y(b)=0&b\notin H\\
e_y(b)=1&b\notin yH.
\end{array}
\]

Its constraints are global on the Bass--Serre tree. No finite tree
ball is used to infer propriety or collapse.

There is nevertheless an exact component reduction. Put

\[
K_b=\langle H,b^{-1}Cb\rangle.
\]

A nonzero dual conserved edge current exists exactly when there is a
nonzero function \(s:K_b\backslash B\to\mathbb Q\) satisfying, for
every \(g\in B\),

\[
\sum_{i=0}^{3}s(K_bb^{-1}x^ig)=-\sigma s(K_bg),
\]

\[
\sum_{j=0}^{2}s(K_bb^{-1}yx^jg)=-\sigma s(K_bg).
\]

The subgroup \(K_b\) lies in \(\ker e_y\), so these equations have an
exact height grading: one is intralayer and the other interlayer in
each of the exponent-zero and exponent-one cases. They are not
ordinary Hecke recurrences, because left prefixing is not generally a
well-defined operation on \(K_b\backslash B\). Existence, cycles, and
collapse for these translated scalar systems remain open.

The first exponent-one stratum does simplify exactly. For a
one-stable-letter element \(b=x^ryx^s\), the double coset depends only
on \(r\bmod4\):

\[
CbH=Cx^ryH,\qquad r\in\{0,1,2,3\}.
\]

The value \(r=0\) is the canonical collapse. For \(r=1,2,3\),
\(K_b=H\). Writing \(u=y^{-1}xy\), the intralayer equation on

\[
\langle H,y^{-1}Hy\rangle
\cong H*_{\langle x^3\rangle}y^{-1}Hy
\]

is one of the three fixed-turn eigenvalue problems

\[
\sum_{j=0}^{2}s(Hu^{-r}x^jg)=-\sigma s(Hg),
\]

coupled to the preceding height by

\[
\sum_{i=0}^{3}s(Hy^{-1}x^{i-r}g)=-\sigma s(Hg).
\]

This replaces an arbitrary one-\(y\) word family by three exact
operators.

**Result 61 (noncanonical one-\(y\) propriety).** For
\(r=1,2,3\) and either sign \(\sigma\),

\[
(x^4-1)\mathbb Q[B]+(yR_3-R_4)\mathbb Q[B]
+(x^ry+\sigma R_4)\mathbb Q[B]
\]

is a proper right ideal.

The proof uses the actual Bass--Serre tree, not a finite truncation.
The dual relations at a vertex \(v\) are the sum of its four incoming
predecessors plus \(\sigma\delta_v\), and the sum of one fixed
nontrivial cyclic turn through each of its three outgoing successors
plus \(\sigma\delta_v\). If a finite linear combination of these
vectors equaled a basis vector, take a leaf of the convex hull of its
coefficient support. An outward turned target sees only the
fixed-turn relation at that leaf, so its coefficient vanishes. An
outward incoming predecessor, chosen to avoid the one possible
interior sibling contribution, then sees only the incoming relation,
so that coefficient also vanishes. This contradicts the choice of
leaf.

Linear-functional separation therefore produces a nonzero rational
solution of the scalar systems, and the exact reconstruction in
Result 60 produces a nonzero conserved edge current. The sole
one-positive-stable-letter exception is \(r=0\), where the turn fixes
the starting predecessor and the canonical module collapses.

This settles every double coset represented by a word with exactly one
positive stable letter. It does not yet settle arbitrary elements with
total \(y\)-exponent one, whose Britton normal form may contain several
positive and negative stable letters.

**Result 62 (positive--negative length-two exponent-zero propriety).**
Put \(a=yxy^{-1}\). For \(\ell=0,1,2,3\), \(r=1,2\), and either sign
\(\sigma\),

\[
(x^4-1)\mathbb Q[B]+(yR_3-R_4)\mathbb Q[B]
+(x^\ell a^r+\sigma R_4)\mathbb Q[B]
\]

is a proper right ideal.

Here \(K_{x^\ell a^r}=H\), but the direct leaf proof from Result 61 has an
adjacent-center collision. The replacement is a second tree
decomposition. With

\[
J_-=
\langle x,a\mid x^4=a^3\rangle
\cong\langle x\rangle*_{\langle x^4=a^3\rangle}\langle a\rangle,
\]

the intralayer scalar equation takes one fixed nonzero turn modulo
three in each of the four adjacent \(\langle a\rangle\)-blocks. It
admits a rational eigenfunction with either an arbitrary prescribed
\(H\)-vertex value or an arbitrary prescribed block sum. The
equivalent HNN presentation

\[
B=\langle J_-,y\mid yxy^{-1}=a\rangle
\]

then supplies a macro tree. For nonzero \(\ell\), the target port is no
longer one block sum, but it remains a nonzero functional on at most
three internal vertices. The fixed-turn eigenspace can realize any
prescribed value of such a functional: protect its at most three
support vertices and route every equation residual through a fresh
block outside their finite convex hull. Each new macro fiber therefore
receives exactly one realizable port datum from its parent edge, so the
local interpolation extends recursively to a nonzero global current.

This closes every \(b=x^\ell yx^ry^{-1}\), with \(\ell\bmod4\) and
\(r=1,2\), in the relevant negative exponent-zero fiber. It does not
include the inverse sign sequence \(y^{-1}x^ry\) or longer Britton
codes.

**Result 63 (negative--positive length-two flow collapse).** Put
\(u=y^{-1}xy\). For \(\ell=0,1,2,3\), \(r=1,2,3\), and either sign
\(\sigma\),

\[
(x^4-1)\mathbb Q[B]+(yR_3-R_4)\mathbb Q[B]
+(x^\ell u^r+\sigma R_4)\mathbb Q[B]
=\mathbb Q[B].
\]

Let \(K=\langle H,u^{-r}Cu^r\rangle\) and
\(h_r=u^{-r}xu^r\). Since \(u^4=x^3\) is central in
\(\langle x,u\rangle\), one has

\[
u^{-r}x^4u^r=h_r^4,
\qquad h_r^3=x^3.
\]

Both powers lie in \(K\), so \(h_r\in K\). All four terms in scalar
equation (36) are therefore the same coset, and with
\(\lambda=-\sigma\) it becomes

\[
4s(Ku^{-r}g)=\lambda s(Kg).
\]

Applying this equation successively
\(m=4/\gcd(4,r)\) times and using
\(u^{-rm}\in\langle u^4\rangle\leq K\) gives

\[
(4^m-\lambda^m)s(Kg)=0.
\]

The coefficient is nonzero over \(\mathbb Q\), so the scalar current
and hence the entire algebraic dual vanish. Linear functionals separate
points, so the flow quotient itself is zero.

This is only a failure of this module obstruction. It does not prove
the corresponding relative products primitive. Together, Results 62
and 63 completely classify the flow module on all exponent-zero
stable-letter-length-two double cosets: the positive--negative family
is proper, while the negative--positive family collapses.

**Result 64 (exact stencil folds and finite-interface transfer).**
Every internal element \(b\) has a finite pointed folded subgroup core
\(\Gamma_b\) representing \(K_b=\langle H,b^{-1}Cb\rangle\).  The
core alone does not decide the flow system, but its two decorated
stencils have exact fold indices

\[
\begin{aligned}
D_I(b)&=\{n:b^{-1}x^nb\in K_b\}=d_I\mathbb Z,
&d_I&\mid4,\\
D_O(b)&=\{n:b^{-1}yx^ny^{-1}b\in K_b\}=d_O\mathbb Z,
&d_O&\mid3.
\end{aligned}
\]

After equal targets are combined, (36)--(37) become

\[
\frac4{d_I}\sum_{r=0}^{d_I-1}s(K_bb^{-1}x^rg)
=-\sigma s(K_bg),
\]

\[
\frac3{d_O}\sum_{r=0}^{d_O-1}s(K_bb^{-1}yx^rg)
=-\sigma s(K_bg).
\]

Thus an incoming stencil has exactly \(1,2\), or \(4\) genuine ports,
and an outgoing stencil has \(1\) or \(3\).  If a stencil has one port
\(K_bag\) and \(a^m\in K_b\), iteration gives
\((q^m-(-\sigma)^m)s=0\), with \(q=4\) or \(3\).  This is an
unconditional scalar-collapse certificate.  Result 63 is its incoming
\(q=4\) instance.

The exact scalar system also has a conditional finite reduction which
separates open interpolation from closed monodromy.  Whenever its
decorated, representative-indexed coefficient hypergraph is
decomposed into a finite-rank core and exterior pieces whose finite
port traces are onto, restriction gives

\[
0\longrightarrow\prod_\alpha Z_\alpha
\longrightarrow \operatorname{Sol}_{b,\sigma}
\longrightarrow\ker M_{b,\sigma}\longrightarrow0.
\]

Here \(Z_\alpha\) is the zero-trace solution space of the exterior
piece and \(M_{b,\sigma}\) is the finite port-return map.  The
Cartesian product is forced because dual currents need not be finitely
supported.  Hence the flow ideal is proper exactly when an exterior
zero-trace mode or a return-kernel vector survives; it collapses when
all such modes vanish and the return map is injective.

On a one-dimensional closed port, the return block is
\(1-\prod_i\mu_i\); in higher dimension it is
\(I-T_m\cdots T_1\), so arbitrary folds are not automatically scalar.
Results 61--62 are open-tree instances: their local interpolation maps
are onto and a free root mode extends.  Result 63 is the scalar closed
case, with return coefficient \(4^m-\lambda^m\).

The finite reduction is conditional for longer Britton codes.  Two
separate missing lemmas are now explicit: finite rank of the
decorated, representative-indexed interface, and trace surjectivity of
each open block.  Neither follows from finite generation of \(K_b\).
Indeed \(b=y\) and \(b=xy\) both have \(K_b=H\), but the first
collapses while the second is proper.  The minimal length-three word
\(y^2xy^{-1}\) separately defeats the naive exposed-leaf proof.  No
new primitivity or Andrews--Curtis claim is made here.

**Result 65 (same-sign length-three outgoing collapse).**  Every
normalized sign-\((+,+,-)\) code is

\[
b_{\ell,p,r}=x^\ell yx^pyx^ry^{-1},
\quad
0\leq\ell<4,\quad 0\leq p<3,\quad r=1,2.
\]

Put \(a=yxy^{-1}\), \(u=y^{-1}xy\), and
\(z_r=a^{-r}xa^r\).  For all twenty-four codes,

\[
K_{b_{\ell,p,r}}
=\langle x,z_r\rangle
\cong\langle x,z_r\mid x^4=z_r^4\rangle.
\]

The key saturation is

\[
b_{\ell,p,r}^{-1}x^4b_{\ell,p,r}=z_r^3,
\qquad z_r^4=x^4:
\]

although the definition of \(K_b\) initially supplies only \(z_r^3\),
it therefore supplies \(z_r\) itself.  Exact line-of-groups normal
forms give the stencil indices

\[
d_I(b_{\ell,p,r})=4,
\qquad
d_O(b_{\ell,p,r})=
\begin{cases}
1,&\ell=0,\\
3,&\ell=1,2,3.
\end{cases}
\]

Because \(a^{-r}x^{-p}=z_r^{-p}a^{-r}\) and \(z_r\in K_b\), the
parameter \(p\) disappears from both exact scalar stencils.  The
twenty-four codes therefore represent only eight scalar systems,
indexed by \((\ell,r)\).

For \(\ell=0\), the outgoing equation folds to

\[
3s(K_ba^{-r}g)=-\sigma s(K_bg).
\]

Since \(a^{-3r}=x^{-4r}\in K_b\), three iterations give a nonzero
coefficient \(26\) or \(28\) times every value of \(s\).  Thus, for
\(p=0,1,2\), \(r=1,2\), and both signs,

\[
(x^4-1)\mathbb Q[B]+(yR_3-R_4)\mathbb Q[B]
+(yx^pyx^ry^{-1}+\sigma R_4)\mathbb Q[B]
=\mathbb Q[B].
\]

This closes all six \(\ell=0\) codes, representing two scalar systems,
including the minimal failed leaf geometry \(y^2xy^{-1}\), by scalar
collapse rather than interpolation.  The other eighteen codes
represent six systems with exact fold pair \((4,3)\), so neither
stencil is scalar and no outcome is claimed.
The collapse is a failure of the flow obstruction only, not a
primitivity or Andrews--Curtis theorem.

**Result 66 (affine coinduction is blind to every internal
exponent-one element).**  Let \(V\) be any \(\mathbb Q\)-vector space,
let \(A\in\operatorname{GL}(V)\), and give \(V^{\mathbb Q}\) the
right \(B\)-action

\[
(f\cdot x)(t)=f(t-1),
\qquad
(f\cdot y)(t)=A f(4t/3).
\]

For every \(b\in B\) with \(e_y(b)=1\) and both signs \(\sigma\), the
three internal module relations have only the zero solution in this
module.  The proof is uniform.  The first relation makes \(f\)
four-periodic and the four-term sum
\(S(t)=\sum_{k=0}^3f(t-k)\) one-periodic.  Since

\[
(f\cdot b)(t)=A f(4t/3+d_b)
\]

for some rational \(d_b\), comparing the third relation at \(t\) and
\(t+1\) forces \(4/3\)-periodicity.  The second and third relations
then reduce to

\[
f(v+d_b)=-3\sigma f(v).
\]

Some positive multiple of \(d_b\) lies in
\((4/3)\mathbb Z\), so iteration gives

\[
\bigl(1-(-3\sigma)^m\bigr)f(v)=0
\]

with a nonzero rational coefficient.  Hence \(f=0\).

This closes an entire tempting representation route, including every
seed function and every constant invertible \(y\)-twist.  It does not
prove the universal flow module collapses and gives no primitivity or
Andrews--Curtis conclusion.

**Result 67 (finite nilpotent/Magnus primitivity tests are blind).**
The proof is in
literature/proofs/AK3_AD_NILPOTENT_PRIMITIVITY_NO_GO.md.

For every relative conjugator \(c\),

\[
\operatorname{ab}(P_+(c))=(4,-5,0,0),
\qquad
\operatorname{ab}(P_-(c))=(2,-3,0,0).
\]

Both vectors are primitive.  More generally, any word with primitive
integral abelianization maps to a primitive element of every free
nilpotent quotient \(F_n/\gamma_{s+1}F_n\).  After choosing a basis
whose first member has the same abelianization as the word, substitute
the word for that member.  The resulting endomorphism is the identity
on abelianization.  Its image \(H\) satisfies
\(H\gamma_2=N\); commutator collection gives
\(\gamma_j\subseteq H\gamma_{j+1}\), hence \(H=N\).  Hopficity makes
the endomorphism an automorphism.

Consequently every \(P_\sigma(c)\) is primitive in every free
nilpotent quotient, including the concrete negative--positive
length-two flow-collapse families.  Since a finite-degree integral
Magnus expansion factors through a finite lower-central quotient,
ordinary degree-two and all fixed finite quotient-primitivity tests
on truncated Magnus images cannot obstruct this family.  Standard
finite free
lower-\(p\)-central and Zassenhaus quotients are blind for the same
Frattini-quotient reason.

This does not exclude a second Fox/Jacobian obstruction which retains
lift data rather than only the truncated word image.  It sharply
removes nilpotent quotient-primitivity tests, not finer induced-orbit
invariants or the full higher-order Fox route.

**Result 68 (exact infinite cross-incidence in the six remaining
length-three systems).**  After the \(p\)-reduction in Result 65, fix
\(\ell=1,2,3\) and \(r=1,2\).  With
\(h=a^{-r}\), the exact scalar equations simplify to

\[
\sum_{i=0}^{3}s(Khy^{-1}x^ig)=\lambda s(Kg),
\]

\[
\sum_{j=0}^{2}s(Khu^{-\ell}x^jg)=\lambda s(Kg).
\]

The first stencil is independent of \(\ell\), but the equations remain
indexed by \(H\backslash B\), not \(K\backslash B\).  For an incoming
port \(A_i(g)=Kb^{-1}x^ig\), all outgoing centers containing it are

\[
H\,y^{-1}bkb^{-1}x^ig,\qquad k\in K.
\]

For an outgoing port \(B_j(g)=Kb^{-1}yx^jg\), all incoming centers
containing it are

\[
H\,bkb^{-1}yx^jg,\qquad k\in K.
\]

Amalgam normal form also shows that distinct \(H\)-centers over the
same \(K\)-center have disjoint same-type stencils, apart from the
ordinary modulo-four or modulo-three permutation of one relation.
Thus all remaining collisions are genuinely cross-stencil.

In both formulas two parameters give the same center exactly when
they differ by

\[
K\cap b^{-1}\langle a\rangle b
=K\cap b^{-1}Hb
=\langle z_r^3\rangle.
\]

Hence every port belongs to an infinite opposite-stencil center family
indexed by \(\langle z_r^3\rangle\backslash K\).  The universal
adjacent collisions are only the \(k=1\) members.  Any interpolation
proof must solve all of these simultaneous compatibility conditions;
checking one adjacent center is not enough.  This is an exact
structural theorem, with no propriety, primitivity, or
Andrews--Curtis conclusion.

**Result 69 (all finite-dimensional characteristic-zero modules are
blind in the exponent-one internal fiber).**  Let \(V\) be
finite-dimensional over a characteristic-zero field, and let
\(X,Y\in\operatorname{GL}(V)\) satisfy \(YX^3Y^{-1}=X^4\).  If a row
vector \(v\) satisfies

\[
v(X^4-I)=0,
\qquad
v\bigl(YR_3(X)-R_4(X)\bigr)=0,
\]

then

\[
vX=v,\qquad vY=\frac43v.
\]

Indeed, similarity of \(X^3\) and \(X^4\) partitions the eigenvalues
of \(X\) into cycles satisfying
\(\lambda^{4^m-3^m}=1\).  The exponent is odd and is \(1\bmod3\), so
no nontrivial fourth or cube root of unity occurs.  Hence \(R_4(X)\)
and \(R_3(X)\) are invertible.  The two displayed relations then give
\(vX=v\), \(vYX=vY\), and \(3vY=4v\).

For every \(b\in B\) with \(e_y(b)=1\), it follows that
\(vb=(4/3)v\), while \(vR_4(X)=4v\).  Thus

\[
v(b+\sigma R_4(X))
=\left(\frac43+4\sigma\right)v
\]

forces \(v=0\) for both signs.  No finite-dimensional
characteristic-zero module can witness propriety anywhere in the
internal exponent-one fiber.  Since Result 61 already gives proper
ideals in that fiber, its currents—and any possible currents for
Result 68's six open systems—are intrinsically
infinite-dimensional.  This is a representation no-go, not a flow
collapse or primitivity theorem.

**Result 70 (exact three-phase correspondence for the six open
systems).**  Put

\[
c=x^4=z_r^4,\quad
C=\langle c\rangle,\quad
L=\langle z_r^3\rangle,\quad
K=\langle x\rangle*_{C}\langle z_r\rangle.
\]

On

\[
V=K\backslash B,\qquad
W=H\backslash B,\qquad
\Omega=L\backslash B,
\]

define

\[
p(Ld)=Kd,\quad
\rho(Hg)=Kg,\quad
q_I(Ld)=Hbd,\quad
q_O(Ld)=Hy^{-1}bd.
\]

The \(q_I\)-fibers have size four and the \(q_O\)-fibers size three.
If \(q_!\) denotes finite-fiber summation, the scalar-current space is
exactly

\[
\ker\mathcal A_{-\sigma},
\qquad
\mathcal A_\lambda(s)=
\bigl(q_{I!}p^*s-\lambda\rho^*s,\,
q_{O!}p^*s-\lambda\rho^*s\bigr).
\]

The Bass--Serre tree of
\(K/C\cong C_4*C_4\) is \((4,4)\)-biregular.  The infinite cross-index
set \(L\backslash K\) maps three-to-one onto its
\(\langle z_r\rangle\)-vertex set.  Since
\(C\cap L=\langle c^3\rangle\), right multiplication by \(c\)
cyclically permutes the three points above each vertex.  This
three-phase decoration is essential: forgetting it identifies
distinct equations.

The operator is row-finite but has infinite column incidence, and
\(p\) has infinite fibers.  Hence there is no pushforward \(p_!\) on
arbitrary currents and no valid finite return matrix obtained by
formal composition.  The exact unresolved question is whether
\(\ker\mathcal A_{\pm1}\) is nonzero.  This is a correspondence
reduction, not a propriety, collapse, primitivity, or
Andrews--Curtis theorem.

**Result 71 (one exact finite-support identity decides each open
system).**  Let

\[
\mathscr I_S=\mathbb Q[S\backslash B],
\qquad
\mathscr C_S=\mathbb Q^{S\backslash B}.
\]

The operator in Result 70 is the algebraic transpose of

\[
D_\lambda:\mathscr I_H^2\longrightarrow\mathscr I_K
\]

with rows

\[
D_\lambda([Hg],0)
=\sum_{i=0}^{3}[Kb^{-1}x^ig]-\lambda[Kg],
\]

\[
D_\lambda(0,[Hg])
=\sum_{j=0}^{2}[Kb^{-1}yx^jg]-\lambda[Kg].
\]

Hence

\[
\ker\mathcal A_\lambda
\cong(\operatorname{coker}D_\lambda)^\vee.
\]

Transitivity of the \(B\)-action reduces surjectivity of \(D_\lambda\)
to the single question \([K]\in\operatorname{im}D_\lambda\).  Written
coefficientwise, this is one identity for finitely supported
\(\alpha,\beta:H\backslash B\to\mathbb Q\):

\[
\begin{aligned}
&\sum_{Lk\in L\backslash K}\alpha(Hbkd)
+\sum_{Lk\in L\backslash K}\beta(Hy^{-1}bkd)\\
&\quad-\lambda\sum_{Hk\in H\backslash K}
\bigl(\alpha(Hkd)+\beta(Hkd)\bigr)
=\mathbf1_{\{Kd=K\}}
\qquad(d\in B).
\end{aligned}
\]

The sums are finite because the coefficient functions are finitely
supported, but every \(L\backslash K\) phase remains present.  If the
identity is impossible, linear separation of the cokernel constructs
a nonzero current; if it exists, the flow quotient collapses.  This is
the exact next proof target, not a decision of either side.

**Result 72 (the amalgam resolution makes that identity locally
finite).**  Put \(Z=\langle z\rangle\).  The Bass--Serre tree of

\[
K=H*_C Z
\]

gives an exact sequence

\[
0\longrightarrow\mathscr I_C
\longrightarrow\mathscr I_H\oplus\mathscr I_Z
\longrightarrow\mathscr I_K\longrightarrow0.
\]

Using it to lift \(D_\lambda\), then eliminating the
\(\mathscr I_H\)-coordinate through the unit \(-\lambda\), gives

\[
\operatorname{coker}D_\lambda
\cong\operatorname{coker}E_\lambda,
\]

where

\[
E_\lambda:\mathscr I_H\oplus\mathscr I_C\to\mathscr I_Z,
\]

\[
E_\lambda(\mu,\nu)
=(P_I-P_O)\mu
+(P_I\pi_H-\lambda\pi_Z)\nu,
\]

and

\[
P_I[Hg]=\sum_{i=0}^{3}[Zb^{-1}x^ig],
\qquad
P_O[Hg]=\sum_{j=0}^{2}[Zb^{-1}yx^jg].
\]

The class of \([K]\) corresponds to \([Z]\).  Therefore the exact
remaining question is \([Z]\in\operatorname{im}E_\lambda\).  In
coefficients this asks for finitely supported \(\mu,\nu\) satisfying

\[
\begin{aligned}
&\sum_{n=0}^{2}\mu(Hbz^nd)
-\sum_{n=0}^{2}\mu(Hy^{-1}bz^nd)\\
&\quad+\sum_{n=0}^{2}\sum_{q=0}^{3}
\nu(Cx^qbz^nd)
-\lambda\sum_{q=0}^{3}\nu(Cz^qd)
=\mathbf1_{\{Zd=Z\}}.
\end{aligned}
\]

This presentation is row- and column-finite: its two row types have
seven and five terms, and each \(Z\)-variable occurs in at most six
rows of the first type and sixteen of the second.  Thus the previous
infinite-column obstruction has been removed exactly, not truncated.
Membership of \([Z]\) is still open.

**Result 73 (all six remaining length-three flow systems are
proper).**  The right-\(B\)-equivariant bijection

\[
Z\backslash B\longrightarrow H\backslash B,
\qquad
Zd\longmapsto Ha^rd
\]

identifies the variables of Result 72 with the vertices of the
directed Bass--Serre tree of \(B\).  Under this identification, a
\((P_I-P_O)\)-row centered at \(v\) has coefficient \(+1\) at all
four incoming predecessors of \(v\), and coefficient \(-1\) at one
nontrivial phase predecessor across each of its three outgoing
successors.  A
\((P_I\pi_H-\lambda\pi_Z)\)-row indexed by an edge \(q\to v\) has
coefficient \(+1\) at all four incoming predecessors of \(v\), and
coefficient \(-\lambda\) at one nontrivial phase successor of \(q\).
The phases are nontrivial precisely because
\(\ell\in\{1,2,3\}\) and \(r\in\{1,2\}\).

If a finite combination of these rows equaled the target \([Z]\),
take the convex hull of the target, all supported vertex centers, and
both endpoints of every supported edge.  At any non-target leaf, an
outgoing phase target is reached only by the row centered at that
leaf, forcing its coefficient to vanish.  If the unique inward edge
terminates at the leaf, one of the other incoming predecessors,
excluding the sole possible sibling-turn collision, isolates its edge
coefficient.  If the edge starts at the leaf, its nontrivial outgoing
phase target isolates the same coefficient.  Thus no non-target leaf
can occur.  A finite nontrivial tree has two leaves, so the hull is the
single target vertex; the same outward argument then kills its only
possible vertex coefficient.  This contradiction proves

\[
[Z]\notin\operatorname{im}E_\lambda
\]

for every \(\ell=1,2,3\), \(r=1,2\), and
\(\lambda=\pm1\).  Hence \(D_\lambda\) is not surjective and
\(\ker\mathcal A_\lambda\ne0\).

Consequently, for all \(p=0,1,2\), both signs, and all eighteen
normalized length-three words \(b_{\ell,p,r}\) with
\(\ell\ne0\), the internal flow ideal is proper.  Result 65 gives
collapse for the six words with \(\ell=0\).  This decides the flow
quotient for the whole sign-\((+,+,-)\) stratum, not primitivity or
Andrews--Curtis equivalence.

**Result 74 (internal flow propriety is an A--D nonprimitivity
certificate).**  Let

\[
J_{b,\sigma}
=(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b+\sigma R_4)\mathbb Q[B].
\]

If \(J_{b,\sigma}\) is proper, its nonzero cyclic quotient has a
vector \(w\) annihilated by the three generators.  Induce this module
from \(B\) to \(G=B*\langle z\rangle\); freeness of
\(\mathbb Q[G]\) as a left \(\mathbb Q[B]\)-module preserves
\(w\ne0\).  With

\[
t=zxz^{-1},\qquad q=zy,\qquad
g=zbz^{-1},\qquad v=wz^{-1},
\]

the vector \(v\) annihilates

\[
v(t^4-1),\qquad
v\bigl(g+\sigma R_4(t)\bigr),\qquad
v\bigl(qR_3-R_4(t)z\bigr).
\]

These identities annihilate every coordinate of the literal
evaluated A--D Fox row

\[
\left(
qR_3+\sigma gt^{-1}z,\;
-R_4(t)-\sigma gt^{-1},\;
\sigma g(t^{-1}-1),\;
1-t^4
\right).
\]

Therefore, when an A--D relative product has evaluated internal
parameter \(g=zbz^{-1}\), propriety of \(J_{b,\sigma}\) proves that
relative product nonprimitive.  This applies to the proper families
in Results 61, 62, and 73.  Flow collapse has no converse implication:
it proves neither primitivity nor an AC reduction.

**Result 75 (the full positive--negative--positive length-three
stratum is proper).**  Let

\[
b_{\ell,p,q}
=x^\ell yx^py^{-1}x^qy,
\qquad
0\leq\ell<4,\quad p=1,2,\quad q=1,2,3.
\]

Writing \(a=yxy^{-1}\), one has
\(b=x^\ell a^px^qy\).  The centrality of
\(C=\langle x^4\rangle=\langle a^3\rangle\) in
\(\langle x,a\rangle\) gives

\[
b^{-1}Cb=y^{-1}Cy=\langle x^3\rangle,
\qquad K_b=H.
\]

Amalgam normal form gives the exact fold pair

\[
(d_I,d_O)=(4,3).
\]

In the ordinary Bass--Serre tree, the four incoming-row targets are
geodesic distance three from their center, one in each incoming
branch.  For \(\ell\ne0\), the three outgoing-row targets are
geodesic distance four, one in each outgoing branch.  For \(\ell=0\),
the middle stable letters cancel and those three targets have distance
two, still one in each outgoing branch.  The phases \(p=1,2\) and
\(q=1,2,3\), together with \(\ell\ne0\) in the length-four case,
make every internal turn nonbacktracking.

If a finite row combination equaled one target basis vector, take a
non-target leaf of the convex hull of its row centers and the target.
For \(\ell\ne0\), a distance-four outward target first isolates the
outgoing coefficient; a distance-three target in another incoming
branch then isolates the incoming coefficient, avoiding the sole
possible radius-four collision from the inward neighbor.  For
\(\ell=0\), distance three first isolates the incoming coefficient,
then a distance-two outgoing branch avoiding the sole possible
radius-three collision isolates the outgoing coefficient.  The same
argument handles the singleton hull.  Hence the target is outside the
finite-row image.

Therefore, for all twenty-four normalized words, both signs,

\[
(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b_{\ell,p,q}+\sigma R_4)\mathbb Q[B]
\ne\mathbb Q[B].
\]

By Result 74, the corresponding evaluated internal A--D relative
products are nonprimitive.  This closes the flow/Fox obstruction on
the whole sign-\((+,-,+)\) length-three stratum, not AC itself.

**Result 76 (the last exponent-one length-three stratum reduces to one
aggregate compatibility).**  For

\[
b_{\ell,p,q}=x^\ell y^{-1}x^pyx^qy,
\qquad
0\leq\ell<4,\quad p=1,2,3,\quad q=0,1,2,
\]

put

\[
t=b^{-1}xb,\quad w=b^{-1}(yxy^{-1})b,\quad
s=t^4=w^3.
\]

Normal form gives

\[
H\cap\langle t\rangle
=\langle t^{12}\rangle
=\langle x^9\rangle.
\]

The stronger Bass--Serre combination theorem, applied to
\(H\) and \(b^{-1}\langle x,yxy^{-1}\rangle b\), yields

\[
K_b=\langle x,s\mid x^9=s^3\rangle.
\]

Moreover

\[
K_b\cap\langle t\rangle=\langle t^4\rangle,
\qquad
K_b\cap\langle w\rangle=\langle w^3\rangle,
\]

so all thirty-six normalized codes have
\((d_I,d_O)=(4,3)\).

Put \(L=\langle s\rangle\) and
\(A_9=\langle x^9\rangle=\langle s^3\rangle\).  Resolving
\(K_b=H*_{A_9}L\) and eliminating the \(H\)-coordinate gives

\[
\operatorname{coker}D_\lambda
\cong\operatorname{coker}E_\lambda,
\]

\[
E_\lambda(\mu,\nu)
=(P_I-P_O)\mu
+(P_I\pi_H-\lambda\pi_L)\nu
\in\mathscr I_L.
\]

The bijection

\[
\Theta:L\backslash B\to C\backslash B,
\qquad Ld\mapsto Cbd,
\]

turns \(P_I-P_O\) into the ordinary conservation star.  A second row,
indexed by \(A_9d\), is the four-edge incoming star at \(Hd\) minus
\(\lambda\) times \(Cbd\), the terminal edge of its fixed
nonbacktracking length-three path.  Each remote target has three
\(A_9\)-phases.

Those two zero-sum phase modes are harmless in finite support.  The
equal-phase section

\[
j[Ld]=\frac13([A_9d]+[A_9sd]+[A_9s^2d])
\]

splits \(\nu=j(\alpha)+\delta\), with
\(\pi_L\delta=0\), and the \((9,3)\)-tree resolution gives

\[
\pi_H:\ker\pi_L
\overset{\cong}{\longrightarrow}\ker(\mathscr I_H\to\mathscr I_K).
\]

If the aggregate \(\alpha\) is zero and the resulting row combination
is zero, its edge coefficients say \(f(v)=\mu(q)\) on every directed
edge \(q\to v\).  These are constants on infinite
\((3,4)\)-biregular forest components, so finite support forces every
coefficient, including the zero modes, to vanish.

The exact residue is therefore aggregate-only.  A certificate exists
exactly when there are finite
\(\alpha\in\mathscr I_L\) and \(f,\mu\in\mathscr I_H\) such that

\[
f(v)-\mu(q)
=\mathbf1_{\{e=Cb\}}+\lambda\Theta(\alpha)(e)
\quad(e:q\to v)
\]

and

\[
\rho(f-\mu)=\varepsilon_L(\alpha).
\]

No membership conclusion is claimed.  These two equations are the
remaining length-three flow target, with the remote phases resolved
but their aggregate compatibility still open.

**Result 77 (ordinary weights, height martingales, and spherical
collapse cannot decide that aggregate).**  Write the two equations of
Result 76 as an edge equation and a \(K_b\)-fiber compatibility.  In
any weighted linear combination of them, cancellation of the aggregate
edge variable forces the edge weight to factor through

\[
Cg\longmapsto K_bb^{-1}g.
\]

Cancellation of the two compact potentials then gives exactly the
original two scalar current equations.  Thus a weighted separator
exists precisely when the missing current already exists; an
ordinary-tree extreme-edge weight cannot distinguish the other
members of the same infinite \(K_b\)-fiber.

Equivalently, a separator is a zero-divergence rational flow on the
original Bass--Serre tree—a finitely additive boundary charge—whose
incoming mass is constant on \(K_b\)-fibers and whose remote
\(b\)-edge cylinder has mass \(\lambda\) times that value.

Two broad ansatzes are forced to zero.  A height-radial flow satisfies

\[
c_{n+1}=\frac43c_n
\]

by conservation, but

\[
c_{n+1}=4\lambda c_n
\]

by the remote relation.  A current factoring through the larger
subgroup

\[
\langle H,b^{-1}\langle x,yxy^{-1}\rangle b\rangle
\]

also vanishes: both stencils become scalar, forcing simultaneously
the height factor \(4/3\) and the incompatible height-zero factor
\(\lambda/3\).  Any successful current must therefore retain
genuinely nonradial boundary modes of the internal \((9,3)\)-tree.
This rules out those compressions; it does not decide Result 76.

**Result 78 (an unbounded radius-one-gap nonprimitivity sieve).**
Consider a normalized Britton word beginning with a positive stable
letter,

\[
b=x^\ell yx^{r_1}y^{\epsilon_2}\cdots
x^{r_{n-1}}y^{\epsilon_n}.
\]

Assume its exact component subgroup and folds satisfy

\[
K_b=H,\qquad(d_I,d_O)=(4,3).
\]

The incoming targets are geodesic distance \(n\), one in each incoming
branch of the ordinary Bass--Serre tree.  If \(\ell\ne0\bmod4\), the
outgoing targets have distance \(n+1\), one in each outgoing branch.
If \(\ell=0\), \(n\ge2\), and \(\epsilon_2=-1\), the endpoint pinch
shortens them to distance \(n-1\), again one in each outgoing branch.

For any two such row systems on a directed tree, with radii differing
by one, a finite-certificate leaf argument is uniform.  At a
non-target leaf, an outward target of the longer row is beyond the
radius of every other supported center and kills its coefficient.
For the shorter row, only the longer row at the inward neighbor can
collide, and it reaches at most one outward branch; another branch
kills the shorter coefficient.  The singleton hull is handled in the
same order.

Hence the internal flow ideal is proper for every such \(b\), at
arbitrary stable-letter length and for both signs.  Result 74 turns
this into A--D Fox nonprimitivity whenever \(b\) is the evaluated
internal parameter.  Results 61, 62, and 75 are the first three
finite-length instances.  The theorem excludes words whose endpoint
pinch puts both stencils in the same branch family, any nontrivial
fold, and \(K_b\ne H\); it is not an AC theorem.

**Result 79 (the whole \(K_b=H\) stratum is classified).**  For a
Britton-reduced word

\[
b=x^{r_0}y^{\epsilon_1}x^{r_1}\cdots
x^{r_{n-1}}y^{\epsilon_n},
\qquad n\ge1,
\]

conjugate-peeling decides \(b^{-1}x^4b\in H\).  A positive stable
letter requires divisibility by \(4\) and sends the exponent
\(4k\mapsto3k\); a negative one requires divisibility by \(3\) and
sends \(3k\mapsto4k\).  At the first failed pinch, Britton's lemma
leaves a reduced core which no outer syllable can remove.  Starting
from exponent \(4\), every pinch succeeds exactly for the alternating
sign string

\[
(+,-,+,-,\ldots).
\]

Therefore

\[
K_b=H
\quad\Longleftrightarrow\quad
(\epsilon_1,\ldots,\epsilon_n)
=(+,-,+,-,\ldots).
\]

For every such word, \(d_I=4\).  Amalgam normal form at the initial
turn gives \(d_O=3\), except for the single-stable-letter endpoint
\(r_0=0\), where \(b\in yH\) and \(d_O=1\).  Result 78 therefore
gives the exact unbounded classification

\[
\begin{array}{c|c}
b\in H\text{ or }b\in yH&\text{flow collapse},\\
K_b=H,\ b\notin H\cup yH&\text{flow ideal proper}.
\end{array}
\]

By Result 74, every word in the second row obstructs its evaluated
internal A--D relative product from being primitive.  The canonical
collapse row has no converse primitivity conclusion.

**Result 80 (a cyclotomic current closes the last length-three
aggregate).**  Let

\[
b=x^\ell y^{-1}x^pyx^qy,
\qquad
\ell,q\in\mathbb Z,\quad p\in\{1,2,3\},\quad
\lambda\in\{\pm1\}.
\]

There is a right \(\mathbb Q[B]\)-module and a nonzero vector \(v\)
such that

\[
v(X^4-1)=0,\qquad
v(YR_3-R_4)=0,\qquad
v(b-\lambda R_4)=0.
\]

The construction is exact.  Over \(\mathbb C\), take countably
infinite eigenspaces \(V_\zeta\) for every root of unity \(\zeta\).
The fourth-power blocks

\[
D_c=\bigoplus_{\zeta^4=c}V_\zeta
\]

and third-power blocks

\[
\mathcal R_c=\bigoplus_{\eta^3=c}V_\eta
\]

have the same countable dimension.  A block isomorphism
\(Y_c:D_c\to\mathcal R_c\) satisfies \(YX^3=X^4Y\).  Finite
independent source/image prescriptions can therefore be imposed and
extended to a global invertible \(Y\).

Choose \(v=v_++v_-\) in the \(X\)-eigenspaces \(1,-1\) and prescribe

\[
vY=\frac43v_++z,\qquad z\in V_\omega,
\]

where \(\omega^3=1\ne\omega\).  Then

\[
vX^4=v,\qquad vYR_3=vR_4=4v_+.
\]

For odd \(p\), two independent vectors in each of the fourth-power
blocks \(c=1,-1\) absorb the parity
\((-1)^{\ell+q}\).  For \(p=2\), a vector in an eigenspace
\(\delta^4=-1\) supplies the factor \(\delta^2=\pm i\).  The
blockwise prescriptions give, in both cases,

\[
vb=4\lambda v_+=\lambda vR_4.
\]

Restricting scalars to \(\mathbb Q\) proves that

\[
(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b-\lambda R_4)\mathbb Q[B]
\]

is proper.

The same module gives the missing normalized current without a
duality shortcut.  Put \(m=4v_+\) and
\(K_b=\langle x,b^{-1}x^4b\rangle\).  The identities above make \(m\)
\(K_b\)-fixed.  For a rational linear functional \(\psi\) with
\(\psi(m)=1\),

\[
S(K_bg)=\psi(mg)
\]

is well-defined, satisfies both scalar equations (193)--(194), and
has \(S(K_b)=1\).  Therefore

\[
[K_b]\notin\operatorname{im}D_\lambda,
\qquad
[L]\notin\operatorname{im}E_\lambda.
\]

This decides all \(36\cdot2=72\) normalized
negative--positive--positive cases.  Result 74 turns their proper
flow ideals into evaluated A--D Fox nonprimitivity obstructions.  It
does not prove AC or stable AC.

**Result 81 (the canonical A--D literals are nonprimitive).**  Put

\[
h=qz^{-1}.
\]

The three literal representatives of Result 56's residual projection
fibers,

\[
P_+(h),\qquad P_-(h),\qquad P_-(1),
\]

are nonprimitive in \(F(x,t,z,q)\).  Explicit Whitehead
automorphisms send them, up to cyclic conjugacy, to

\[
\texttt{TTTTZTzxxxx},\qquad
\texttt{TTTTZtzxx},\qquad
\texttt{TTTzXZxxx}.
\]

Each transformed word lies in \(F(x,t,z)\) and uses all three
generators.  The first two Whitehead graphs contain the spanning
cycle

\[
t-x-X-z-T-Z-t,
\]

and the third contains

\[
t-T-Z-X-z-x-t.
\]

Thus each graph is connected with no cut vertex.  The Whitehead
cut-vertex lemma, together with Kurosh's theorem to exclude
primitivity appearing after adjoining the unused fourth generator,
proves nonprimitivity.

The same argument applies to the explicit nonliteral kernel lift

\[
c_0=zq^{-1}zxz^{-1}qz^{-1}
\]

in the negative identity fiber: a Whitehead automorphism sends
\(P_-(c_0)\) to the cyclic word

\[
\texttt{QQxqTxQXqttttqXXX},
\]

whose graph in \(F(q,t,x)\) contains the spanning cycle

\[
q-t-Q-x-X-T-q.
\]

This is a full free-group obstruction where the internal flow module
collapses and nilpotent quotient primitivity is blind.  It proves four
individual cases; by itself it does not give invariance under
arbitrary free-kernel insertions.  Result 83 closes those canonical
double-coset lifts by a different characteristic.

**Result 82 (an unbounded canonical-kernel family is
nonprimitive).**  The first Whitehead automorphism in Result 81 sends

\[
A\longmapsto R=x^3t^{-4},\qquad
D\longmapsto D,\qquad
h\longmapsto z^{-1}.
\]

It therefore sends \(P_\sigma(hA^n)\) to

\[
Rz^{-1}R^nD^\sigma R^{-n}z.
\]

For every \(n\ne0\) and both signs, this cyclic word has a Whitehead
graph containing the fixed spanning cycle

\[
t-T-Z-X-z-x-t.
\]

The \(n=0\) cases are Result 81.  Hence

\[
P_\sigma(hA^n)\text{ is nonprimitive}
\qquad(n\in\mathbb Z,\ \sigma=\pm1).
\]

The exact centralizer gauge

\[
P_\sigma(A^rcD^s)
=A^rP_\sigma(c)A^{-r}
\]

then proves the three-parameter theorem

\[
P_\sigma(A^rhA^nD^s)\text{ is nonprimitive}
\qquad(r,n,s\in\mathbb Z,\ \sigma=\pm1).
\]

It also propagates Result 81's \(c=1\) and \(c=c_0\) conclusions over
their \(\langle A\rangle\)-\(\langle D\rangle\) double orbits.  These
are unbounded kernel-insertion families, but they do not exhaust the
free evaluation kernel.

**Result 83 (finite-characteristic currents close every canonical
double-coset lift).**  The canonical flow quotient collapses over
\(\mathbb Q\), but not integrally.  Let

\[
J^{(k)}_{b,\sigma}
=(x^4-1)k[B]
+(yR_3-R_4)k[B]
+(b+\sigma R_4)k[B].
\]

If \(b\in yH\), then \(J^{(k)}_{b,\sigma}\) is proper whenever
\(\operatorname{char}k\) divides \(1+3\sigma\).  In particular,
\(\mathbb F_2\) works for both signs.  If \(b\in H\), the ideal is
proper whenever the characteristic divides \(1+4\sigma\):
\(\mathbb F_3\) works for \(\sigma=-1\), and \(\mathbb F_5\) for
\(\sigma=+1\).

The proof is a global tree current, not a finite truncation.  For
\(b\in yH\), assign a vertex function \(m\) and put

\[
F(e:u\to v)=-\sigma m(u).
\]

The three outgoing edge values sum to \(m(u)\) in the stated
characteristic.  The incoming condition is the recurrence

\[
m(v)=-\sigma\sum_{u\to v}m(u).
\]

Choose a negative directed end and let \(m(v)\) be one exactly when
the ray from \(v\) to that end always uses incoming predecessors.
Exactly one predecessor continues such a ray, so this \(0\)-\(1\)
function satisfies the recurrence over \(\mathbb F_2\).

For \(b\in H\), put instead

\[
F(e:u\to v)=-\sigma m(v).
\]

The four incoming values sum to \(m(v)\), and conservation becomes

\[
m(u)=-\sigma\sum_{u\to v}m(v).
\]

Choose a positive directed end.  Its \(0\)-\(1\) indicator satisfies
\(m(u)=\sum_{u\to v}m(v)\), which is the required recurrence for
\(\sigma=-1\) over \(\mathbb F_3\).  For the optional positive case
over \(\mathbb F_5\), multiply the indicator by
\((-\sigma)^\beta\), where \(\beta\) is a Busemann function increasing
toward the end.  Both constructions give nonzero algebraic currents,
hence proper ideals.

Result 74's Fox bridge uses only integral group-ring identities and
works over every field.  A primitive word would supply an integral
Fox Bezout identity which survives evaluation and reduction modulo
the chosen prime, contradicting the nonzero annihilator.  Because the
evaluated row depends on the conjugator only through
\(\rho(c)=zbz^{-1}\), this proves nonprimitivity for every free-kernel
lift in the three canonical residues relevant to Result 56:

\[
\begin{array}{c|c|c}
\sigma&b&\text{field}\\ \hline
+1&yH&\mathbb F_2\\
-1&yH&\mathbb F_2\\
-1&H&\mathbb F_3.
\end{array}
\]

Thus the canonical internal double cosets are closed completely.
The unresolved internal residue now consists only of noncanonical
double cosets not already covered by Results 61--86.

**Result 84 (characteristic five closes the negative--positive
length-two collapse).**  Let

\[
b=x^\ell y^{-1}x^ry,
\qquad
\ell\in\mathbb Z,\quad r\not\equiv0\pmod4.
\]

For both signs, the internal flow ideal is proper over
\(\overline{\mathbb F}_5\).  Use the cyclotomic block module of Result
80 in characteristic five.

For \(\sigma=+1\), choose \(0\ne v\in V_1\) and prescribe

\[
vY=3v.
\]

Then

\[
vX^4=v,\qquad
vYR_3=vR_4=4v,
\]

and

\[
vb=vX^\ell Y^{-1}X^rY=v=-vR_4.
\]

For \(\sigma=-1\), choose a primitive cube root \(\omega\), vectors

\[
0\ne v\in V_1,\qquad 0\ne z\in V_\omega,
\]

and a fourth root \(\zeta\) with \(\zeta^r=-1\).  Such a root exists
for every displayed \(r\): use \(\zeta=-1\) for odd \(r\), and a
square root of \(-1\) for \(r\equiv2\pmod4\).  For
\(0\ne a\in V_\zeta\), prescribe

\[
vY=3v+z,\qquad aY=v.
\]

The source and image pairs are independent inside the
\(D_1\)-to-\(\mathcal R_1\) block, so the prescription extends to the
global \(BS(3,4)\) action.  It gives

\[
vYR_3=vR_4=4v,\qquad
vb=aX^rY=4v=vR_4.
\]

Thus in either sign a nonzero vector annihilates all three ideal
generators.  The characteristic-free Fox bridge proves
\(P_\sigma(c)\) nonprimitive for every conjugator satisfying

\[
\rho(c)=zbz^{-1}
\]

with such a \(b\).  This closes every free-kernel lift of all twelve
normalized negative--positive length-two codes and both signs.  The
negative sign is the previously unresolved Result-56 residue.

**Result 85 (characteristic seven closes the first length-four
alternating family).**  Let

\[
b=x^\ell y^{-1}x^ryx^sy^{-1}x^ty,
\]

where \(r,t\not\equiv0\pmod4\) and
\(s\not\equiv0\pmod3\).  Then the negative-sign internal ideal is
proper over \(\overline{\mathbb F}_7\).

Choose \(v\in V_1\) and prescribe

\[
vY=6v+z,
\]

where \(z\) lies in a primitive cube-root eigenspace.  Then

\[
vYR_3=vR_4=4v.
\]

Choose \(a\in D_1\) with a full independent four-phase \(X\)-orbit
and prescribe \(aY=v\).

If \(r+t\not\equiv0\pmod4\), the sources

\[
v,\ a,\ aX^r,\ aX^{-t}
\]

are independent.  Choose \(u=u_2+u_4\) using fresh vectors in the two
primitive cube-root eigenspaces and prescribe

\[
(aX^r)Y=u,\qquad
(aX^{-t})Y=2uX^s.
\]

Since \(2^{-1}=4\) in characteristic seven,

\[
vb=uX^sY^{-1}X^tY=4aY=4v.
\]

If \(r+t\equiv0\pmod4\), choose
\(\eta^3=1\) with \(\eta^s=4\), take \(u\in V_\eta\), and prescribe

\[
(aX^r)Y=u.
\]

Now \(aX^r=aX^{-t}\) and \(uX^s=4u\), so the same endpoint
calculation gives \(vb=4v\).  The block lists are independent in both
cases.  Hence all

\[
4\cdot3\cdot2\cdot3=72
\]

normalized sign-\((-,+,-,+)\) codes are obstructed, and the
characteristic-free Fox bridge covers every free-kernel lift.

There is also an all-length side theorem.  Over \(\mathbb F_5\), the
one-line prescription \(vY=3v\), \(v\in V_1\), gives

\[
vb=3^{e_y(b)}v.
\]

Thus every height-zero internal parameter satisfies
\(v(b+R_4)=0\), and every corresponding positive-sign A--D product
is nonprimitive, without a Britton-length bound.

**Result 86 (every negative-start alternating height-zero word is
obstructed).**  Let

\[
b=x^\ell y^{-1}x^{r_1}yx^{s_1}y^{-1}\cdots
x^{s_{n-1}}y^{-1}x^{r_n}y,
\]

where \(4\nmid r_i\) and \(3\nmid s_i\).  This is the arbitrary-length
Britton-reduced sign string
\((-,+,-,+,\ldots,-,+)\).

Form the phase free product

\[
\Gamma_0=C_4*C_3
=\langle\alpha,\theta\mid\alpha^4=\theta^3=1\rangle
\]

and the reduced word

\[
\varpi=\alpha^{r_1}\theta^{s_1}\cdots
\theta^{s_{n-1}}\alpha^{r_n}.
\]

For \(H_0=\langle\theta,\varpi\rangle\), Kurosh gives

\[
H_0=\langle\theta\rangle*L.
\]

Quotienting by the first free factor shows that \(L\) is generated by
the image of \(\varpi\), hence is cyclic.  Since a cyclic Kurosh
factor is either free or contained in a conjugate finite factor,

\[
L\in\{\mathbb Z,C_2,C_3,C_4\}.
\]

It is nontrivial because
\(\varpi\notin\langle\theta\rangle\).  Choose
\(\overline{\mathbb F}_5\) for
\(\mathbb Z,C_2,C_4\), and \(\overline{\mathbb F}_7\) for \(C_3\).
In the chosen field there is a character

\[
\chi(\theta)=1,\qquad \chi(\varpi)=4.
\]

The induced right \(k[\Gamma_0]\)-module contains \(a\ne0\) with

\[
a\theta=a,\qquad a\varpi=4a.
\]

Embed its complete \(\alpha\)-spectral representation as
\(U\subset D_1\), and an independent copy of its
\(\theta\)-spectral representation as
\(W\subset\mathcal R_1\).  Infinite eigenvalue multiplicities allow
\(U\cap W=0\) with infinite complements.  Let \(Y:U\to W\) identify
the two copies and put \(v=aY\).  Then \(vX=v\) and
\(vY^{-1}=a\).

Using a fresh primitive cube-root vector, extend this block map by

\[
vY=\frac43v+z.
\]

It follows that

\[
vYR_3=vR_4=4v.
\]

The full right-action replay is now

\[
\begin{aligned}
vb
&=a\alpha^{r_1}\theta^{s_1}\cdots
\theta^{s_{n-1}}\alpha^{r_n}Y\\
&=a\varpi Y
=4v.
\end{aligned}
\]

Thus the negative-sign internal ideal is proper in characteristic
five or seven.  The induced-module construction satisfies every
spectral cycle simultaneously; no finite interpolation hypothesis is
left.  The Fox bridge proves \(P_-(c)\) nonprimitive for every
free-kernel lift with \(\rho(c)=zbz^{-1}\).  Together with Result
85's all-height-zero positive-sign theorem, both signs are obstructed
throughout this arbitrary-length family.  Nonalternating stable-sign
strings remain open.

**Result 87 (the full negative--negative--positive--positive stratum
is obstructed).**  Let

\[
b=x^\ell y^{-1}x^r y^{-1}x^s yx^t y,
\qquad 4\nmid s,
\]

with \(\ell,r,t\) arbitrary.  Over
\(k=\overline{\mathbb F}_5\), choose independent
\(v,a\in V_1\), a primitive cube-root vector
\(0\ne z\in V_\omega\), and \(0\ne d\in V_\gamma\), where
\(\gamma^4=1\) and \(\gamma^s=4=-1\).  Prescribe in the block
\(D_1\to\mathcal R_1\)

\[
vY=3v+z,
\qquad aY=v,
\qquad dY=a.
\]

Both the source and image lists are independent, so this extends to
an invertible BS\((3,4)\)-module action.  The baseline is

\[
vYR_3=4v=vR_4,
\]

and the complete word evaluation is

\[
\begin{aligned}
vb
&=vX^\ell Y^{-1}X^rY^{-1}X^sYX^tY\\
&=aX^rY^{-1}X^sYX^tY\\
&=dX^sYX^tY
=4aX^tY
=4v.
\end{aligned}
\]

Therefore the negative-sign internal ideal is proper.  The Fox
bridge obstructs \(P_-(c)\) for every free-kernel lift with
\(\rho(c)=zbz^{-1}\), while Result 85 obstructs \(P_+(c)\) because
\(e_y(b)=0\).  This closes both signs for the complete first
nonalternating height-zero stratum, with no restrictions on the
equal-sign exponents.

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
and changed-row-first deletion. Result 54 closes arbitrary A--W traffic
in the fixed D-then-mixed-Q order. Results 55--56 confine arbitrary
A--D primitive creation to three exact normalized projection fibers:
\(\pi(c)=qz^{-1}\) for the positive source and
\(\pi(c)\in\{1,qz^{-1}\}\) for the negative source. Results 58--59
obstruct every noninternal element of those fibers. Result 60 splits
their three internal classes into canonical double cosets
\(b\in H\) or \(b\in yH\), where this module collapses and a different
method is required, and noncanonical double cosets. Result 61 proves
the flow quotient nonzero for every noncanonical double coset with a
one-positive-stable-letter representative. Result 62 also closes the
entire positive--negative length-two exponent-zero family. Result 63
completes the flow-module classification at length two: the
negative--positive family makes this module collapse and therefore
requires a different invariant. Result 83 supplies that different
invariant on every canonical double coset, and Result 84 supplies it
on the complete negative--positive length-two family. Result 85 closes
the first negative-start alternating length-four family and every
positive-sign height-zero parameter. Result 86 extends the negative
alternating construction to arbitrary stable-letter length. Results 73--75 close the
positive--positive--negative and positive--negative--positive
exponent-one length-three strata and translate every proper internal
flow ideal back to an exact Fox nonprimitivity obstruction. Result 76
reduces the last negative--positive--positive stratum to one aggregate
compatibility after proving that its two zero-sum phases cannot form a
finite certificate, and Result 80 closes that aggregate by an exact
cyclotomic current. The immediate exact leads are therefore
z-dependent A--W conjugators, the
noncanonical module-collapse internal A--D fibers beyond Results
61--87, arbitrary W--D conjugators,
non-source deletion outside Result 54's D-then-mixed-Q order, or two row-changing edges
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
finite table. For arbitrary A--D relative products, the abelianized Fox
row now gives an unbounded exponent sieve: primitivity forces
\(e_q+e_z=0\), and on that hyperplane only
\((\sigma,e_q)=(+,1),(-,0),(-,1)\) escape the chosen character slice.
A different viable primitive-slot branch must therefore use
z-dependent A--W traffic, one of Result 60's canonical-collapse
internal A--D classes or a multi-syllable noncanonical class beyond
Results 61--63, arbitrary W--D relative traffic,
non-source deletion outside the arbitrary A--W/D-then-mixed-Q closure,
two row changes before deletion, another \(Wq^{-1}\) block, a
repeatedly changed source, alter W by traffic with nontrivial
first-deletion image, lose a needed carrier source, use traffic with
nontrivial deletion image, or draw from a source outside the retained
normal closure.

AK(3) remains open.
