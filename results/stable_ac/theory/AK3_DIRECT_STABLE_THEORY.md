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

## Live lead

The strongest remaining direct mechanism is primitive-pair compression
before either old generator is removed.  Short templates produce the
floor-16 corridor above.  A broader visible-block pass returned only to
AK(3)'s floor-13 classical class, but that finite observation remains
unverified.

The target is a hidden-cancellation or longer \(F_4\) primitive pair whose
rank-two quotient has complete Aut-floor at most 12.  A primitive full
four-relator tuple would be an immediate stable solve.  At the
one-stabilization root, the most concrete next mechanism is precisely the
newly exposed nonuniqueness: multiply a canonical recovery word by
controlled consequences of the compressed source relators before
eliminating \(z\).  Separate routes use defining words with at least two
alternating \(v\)-syllables or use the braid relator during recovery.

AK(3) remains open.
