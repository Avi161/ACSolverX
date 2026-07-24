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

## Live lead

The strongest remaining direct mechanism is primitive-pair compression
before either old generator is removed.  Short templates produce the
floor-16 corridor above.  A broader visible-block pass returned only to
AK(3)'s floor-13 classical class, but that finite observation remains
unverified.

The target is a hidden-cancellation or longer \(F_4\) primitive pair whose
rank-two quotient has complete Aut-floor at most 12.  A primitive full
four-relator tuple would be an immediate stable solve.  At the
one-stabilization root, new defining words should lie outside the proved
signed double-coset gauge family; merely adding left or right powers of
\(x\) to this bare corridor cannot help.

AK(3) remains open.
