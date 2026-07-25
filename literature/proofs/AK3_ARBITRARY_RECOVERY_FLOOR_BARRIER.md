# An unbounded direct-recovery floor barrier for AK(3)

Date: 2026-07-24

Status: **PROVEN** for every direct one-source recovery word.  There is
no word-length bound and no consequence-grammar hypothesis.  This closes
one stable-AC mechanism; it does not solve stable AK(3).

## 1. Statement

Put

\[
H=\langle x,t\mid x^3=t^4\rangle .
\tag{1.1}
\]

Let \(U(x,t)\) be any freely reduced word satisfying

\[
U=t\quad\text{in }H,
\tag{1.2}
\]

and define

\[
e=xU,\qquad
P(U)=
\left(
x^3ex^{-4}e^{-1},\
t^{-1}exe^{-1}
\right).
\tag{1.3}
\]

For a pair \(Q=(Q_1,Q_2)\) of words in \(F(x,t)\), write

\[
\mu(Q)=
\min_{\phi\in\operatorname{Aut}(F(x,t))}
\left(
\|\phi(Q_1)\|+\|\phi(Q_2)\|
\right),
\tag{1.4}
\]

where \(\|w\|\) is cyclically reduced word length.

### Theorem 1.1

For every solution of (1.2),

\[
\boxed{\mu(P(U))\ge14.}
\tag{1.5}
\]

The bound is sharp: the literal recovery \(U=t\) has
\(\mu(P(t))=14\).

The theorem is unbounded in \(|U|\).  Its proof gives a lower bound for
every automorphic image directly; it does not use a recovery-word census
or a bounded AC graph.

## 2. Stable realization of every recovery word

At the one-source \(k=1\) compression root, retain

\[
R=x^3t^{-4}
\]

and compress the other source relator to

\[
B_0=z^{-1}xt.
\]

Equation (1.2) says that \(t^{-1}U\) belongs to the normal closure of
\(R\).  Express it as a finite ordered product of conjugates of
\(R^{\pm1}\).  Conjugating or inverting the retained relator temporarily,
multiplying it into \(B_0\), and restoring it after each multiplication is
a signed AC sequence.  It changes \(B_0\) to

\[
B_U=z^{-1}xU.
\]

Restore the original power relator using
\(D=t^{-1}zxz^{-1}\), then eliminate \(z\) through

\[
z=e=xU.
\]

The resulting rank-two presentation is exactly (1.3).  Hence

\[
\operatorname{AK}(3)\sim_{\mathrm{st}}P(U)
\tag{2.1}
\]

for every solution of (1.2).  The rest of the proof concerns the complete
Aut(\(F_2\))-floor of these endpoints.

## 3. Three structural lemmas

### Lemma 3.1: centralizers in the quotient

In \(H\),

\[
C_H(x)=\langle x\rangle,\qquad
C_H(t)=\langle t\rangle,\qquad
\langle x\rangle\cap\langle t\rangle
=\langle x^3\rangle=\langle t^4\rangle .
\tag{3.1}
\]

#### Proof

Use the amalgam decomposition

\[
H=\langle x\rangle
*_{\langle x^3\rangle=\langle t^4\rangle}
\langle t\rangle .
\tag{3.2}
\]

The intersection assertion is the normal-form theorem for amalgamated
free products.  In the Bass--Serre tree, \(x\notin\langle x^3\rangle\)
fixes exactly the vertex stabilized by \(\langle x\rangle\).  An element
commuting with \(x\) must preserve this fixed set, hence belongs to
\(\langle x\rangle\).  The same argument applies to
\(t\notin\langle t^4\rangle\).  This proves (3.1). \(\square\)

The identical conclusions hold after replacing the basis
\((x,t)\) by any basis \((X,T)\).

### Lemma 3.2: axes of distinct primitive conjugates

Let \(F=F(a,b)\) act on its Cayley tree.  Let \(X\) be cyclically reduced,
primitive, and of length \(L\).  If \(Y\ne X\) is conjugate to \(X\), let
\(s\) be the length of the part of
\(\operatorname{Ax}(X)\cap\operatorname{Ax}(Y)\) on which the translation
directions of \(X\) and \(Y\) agree.  Then

\[
s\le L-1
\tag{3.3}
\]

and

\[
\|X^3Y^{-4}\|\ge7L-2s\ge5L+2.
\tag{3.4}
\]

If \(L=2\), the stronger estimate

\[
\|X^3Y^{-4}\|\ge14
\tag{3.5}
\]

holds.  If \(L=1\), distinct axes are disjoint; if their distance is
\(d\), then

\[
\|X^3Y^{-4}\|=7+2d.
\tag{3.6}
\]

#### Proof

The oriented label on \(\operatorname{Ax}(X)\) is the bi-infinite
periodic word \(X^\infty\).  Because a primitive element is not a proper
power, its cyclic word has least period \(L\).  If the two axes shared
\(L\) edges with agreeing translation directions, those \(L\) labels
would fix the phase of both periodic words.  At either end, the next edge
with the prescribed label is unique in the Cayley tree.  The axes would
therefore agree forever in both directions.  Conjugate translations of
the same length and direction on one axis are equal, contrary to
\(Y\ne X\).  Thus (3.3) holds.

For two hyperbolic isometries of a tree, concatenate fundamental
translation segments on their axes.  When the axes are disjoint, the
bridge is traversed twice and contributes twice its length.  When they
intersect, free cancellation can remove only the portion where the two
translation directions agree, and removes at most twice the length of
that portion.  Applied to \(X^3\) and \(Y^{-4}\), this gives

\[
\|X^3Y^{-4}\|\ge3L+4L-2s.
\]

Together with (3.3), this is (3.4).

If \(L=2\), a cyclically reduced primitive word uses the two basis
letters, with signs, exactly once each.  One oriented edge therefore
already fixes its phase in the two-letter period.  Distinct conjugate axes
cannot share even one edge with agreeing translation directions, so
\(s=0\) and (3.5) follows.

If \(L=1\), normalize \(X=a^{\pm1}\).  Two \(a\)-axes in the Cayley tree
are either identical or disjoint.  In the latter case the usual
tree-product path consists of three \(X\)-edges, the bridge, four
\(Y^{-1}\)-edges, and the reverse bridge.  It is reduced, proving
(3.6). \(\square\)

### Lemma 3.3: a basis mate of a fixed generator

If \((x,T)\) is a basis of \(F(x,z)\), then

\[
T=x^p z^\varepsilon x^q
\tag{3.7}
\]

for some \(p,q\in\mathbb Z\) and
\(\varepsilon\in\{1,-1\}\).

#### Proof

Let an automorphism fixing \(x\) send \(z\) to \(T\).  Its
abelianization matrix has second column \((n,\varepsilon)\), where
\(\varepsilon=\pm1\).  The elementary automorphism

\[
x\longmapsto x,\qquad z\longmapsto x^n z^\varepsilon
\]

has the same matrix.  Nielsen's rank-two kernel theorem says that the
kernel of
\(\operatorname{Aut}(F_2)\to\operatorname{GL}(2,\mathbb Z)\) consists of
inner automorphisms.  The quotient of the two automorphisms is therefore
conjugation by a word centralizing \(x\), hence by a power of \(x\).
This gives (3.7). \(\square\)

## 4. Uniform lower bound

Fix an arbitrary

\[
\phi\in\operatorname{Aut}(F(x,t))
\]

and put

\[
X=\phi(x),\qquad T=\phi(t),\qquad E=\phi(e),\qquad
Y=EXE^{-1}.
\tag{4.1}
\]

The first relator in (1.3) has the exact free-group rewriting

\[
x^3ex^{-4}e^{-1}=x^3(exe^{-1})^{-4}.
\]

Thus the transformed pair is

\[
\phi(P(U))=
\left(X^3Y^{-4},\,T^{-1}Y\right).
\tag{4.2}
\]

Transport (1.1) through \(\phi\).  In

\[
H_\phi=\langle X,T\mid X^3=T^4\rangle,
\tag{4.3}
\]

equations \(U=t\) and \(e=xU\) give

\[
E=XT
\quad\text{and hence}\quad
Y=(XT)X(XT)^{-1}.
\tag{4.4}
\]

The free-group elements \(X\) and \(Y\) are distinct.  Otherwise (4.4)
would make \(XT\) centralize \(X\) in \(H_\phi\).  Lemma 3.1 would give
\(XT\in\langle X\rangle\), and then \(T\in\langle X\rangle\).  But \(T\)
also belongs to the other amalgam factor, so Lemma 3.1 would force
\(T\in\langle T^4\rangle\), which is impossible.

The second word in (4.2) is also nontrivial.  If \(T^{-1}Y=1\) in the
free group, then \(T=Y\).  But \(Y\), being conjugate to \(X\), has the
same abelianization as \(X\), whereas the abelianizations of the basis
elements \(X,T\) are independent.

A common inner automorphism does not change either cyclic length.  Use
one to make \(X\) cyclically reduced, and let

\[
L=\|X\|.
\]

Because \(X\) is primitive, \(L\ge1\).

### Case 1: \(L\ge3\)

Lemma 3.2 gives

\[
\|X^3Y^{-4}\|\ge5L+2\ge17.
\]

The nontrivial second word adds at least one, so

\[
\|\phi(P(U)_1)\|+\|\phi(P(U)_2)\|\ge18.
\tag{4.5}
\]

### Case 2: \(L=2\)

The length-two refinement in Lemma 3.2 gives

\[
\|X^3Y^{-4}\|\ge14.
\]

Again the second word is nontrivial, so

\[
\|\phi(P(U)_1)\|+\|\phi(P(U)_2)\|\ge15.
\tag{4.6}
\]

### Case 3: \(L=1\)

After a signed permutation of the ambient basis, assume \(X=x\), and
write the other ambient basis letter as \(z\).  Let \(d\ge1\) be the
distance between the distinct axes of \(x\) and \(Y\).  Lemma 3.2 gives

\[
\|x^3Y^{-4}\|=7+2d.
\tag{4.7}
\]

Suppose, seeking a contradiction, that the total length in (4.2) is at
most \(13\).  Since the second word is nontrivial, (4.7) implies

\[
d\le2.
\tag{4.8}
\]

We now normalize the bridge without changing the total cyclic length.
Write the free conjugator \(E\) in its double coset as

\[
E=x^a g x^b,
\]

where \(g\) is the shortest representative of
\(\langle x\rangle E\langle x\rangle\).  Conjugate the entire pair by
\(x^{-a}\).  This fixes \(x\), replaces \(T\) by another basis mate of
\(x\), and replaces \(E\) by \(gx^{a+b}\).  The right power centralizes
\(x\), so after this simultaneous normalization

\[
Y=gxg^{-1},\qquad |g|=d,
\tag{4.9}
\]

and \(g\) neither starts nor ends with \(x^{\pm1}\).

Lemma 3.3 gives

\[
T=x^p z^\varepsilon x^q,
\qquad \varepsilon=\pm1.
\tag{4.10}
\]

By (4.8), the reduced bridge has the form

\[
g=z^{\delta d},
\qquad \delta=\pm1.
\tag{4.11}
\]

The quotient identity (4.4) remains true after the simultaneous inner
normalization.  The two words \(g\) and \(xT\) conjugate \(x\) to the same
element in \(H_\phi\).  Lemma 3.1 therefore gives an integer \(k\) such
that

\[
g=xT x^k
\quad\text{in }H_\phi.
\tag{4.12}
\]

Consider the homomorphism

\[
\tau:H_\phi\longrightarrow\mathbb Z/4,\qquad
\tau(x)=0,\quad\tau(T)=1.
\tag{4.13}
\]

It is well-defined because \(x^3=T^4\).  Equation (4.10) gives
\(\tau(z)=\varepsilon\).  Applying \(\tau\) to (4.11)--(4.12) yields

\[
\delta d\varepsilon\equiv1\pmod4.
\tag{4.14}
\]

Thus \(d=2\) is impossible.  For \(d=1\), equation (4.14) forces
\(\delta=\varepsilon\), so

\[
g=z^\varepsilon.
\tag{4.15}
\]

There are now two expressions for this element:

\[
z^\varepsilon=x^{-p}Tx^{-q}
\quad\text{freely from (4.10),}
\tag{4.16}
\]

and

\[
z^\varepsilon=xTx^k
\quad\text{in }H_\phi
\tag{4.17}
\]

from (4.12).

Use the homomorphism

\[
\omega:H_\phi\longrightarrow\mathbb Z,\qquad
\omega(x)=4,\quad\omega(T)=3.
\tag{4.18}
\]

Applying it to (4.16)--(4.17) gives

\[
k=-p-q-1.
\tag{4.19}
\]

Substitute (4.19) into (4.17) and compare with (4.16).  After multiplying
on the left and right by powers of \(x\), one obtains

\[
T x^{p+1}=x^{p+1}T.
\tag{4.20}
\]

By Lemma 3.1,

\[
x^{p+1}\in
\langle x\rangle\cap C_{H_\phi}(T)
=\langle x\rangle\cap\langle T\rangle
=\langle x^3\rangle.
\]

Consequently,

\[
p\equiv-1\pmod3,
\tag{4.21}
\]

and in particular \(p\ne0\).

Using (4.9), (4.10), and (4.15), the second relator in (4.2) is the
freely and cyclically reduced word

\[
\begin{aligned}
T^{-1}Y
&=x^{-q}z^{-\varepsilon}x^{-p}
  z^\varepsilon xz^{-\varepsilon},\\
\|T^{-1}Y\|
&=|p|+|q|+4
\ge5.
\end{aligned}
\tag{4.22}
\]

The first relator has length \(7+2d=9\).  Hence the total is at least

\[
9+5=14,
\]

contradicting the assumption that it was at most \(13\).

All three cases therefore give

\[
\|\phi(P(U)_1)\|+\|\phi(P(U)_2)\|\ge14.
\]

Since \(\phi\) was arbitrary, Theorem 1.1 follows.

## 5. Sharpness

For \(U=t\), the endpoint (with \(t\) displayed as \(y\)) is

```text
xxxxyXXXXYX | YxyxYX
```

Apply the basis automorphism

\[
x\longmapsto y^{-1},\qquad y\longmapsto yx.
\]

The cyclically reduced images are

```text
YYYxyyyyX | XYxYX
```

of lengths \(9\) and \(5\).  Thus

\[
\mu(P(t))\le14.
\]

Theorem 1.1 gives the reverse inequality, so

\[
\mu(P(t))=14.
\tag{5.1}
\]

## 6. Scope

The theorem closes every route which:

1. keeps the compressed source relation \(x^3=t^4\);
2. replaces the literal recovery \(t\) by an arbitrary equal quotient
   word \(U\);
3. eliminates \(z\) directly through \(z=xU\); and
4. then minimizes the resulting rank-two pair by an arbitrary ambient
   automorphism.

There is no restriction on \(|U|\), on the number or ordering of
conjugates of \(x^3t^{-4}\), or on cancellation inside \(U\).

The theorem does **not** rule out a stable trivialization that changes the
retained source relator before recovery, interleaves the defining relator
nontrivially, uses a defining word with several alternating old-generator
syllables, uses the braid relator during recovery, or follows a different
stabilization architecture.  In particular, it is not a proof or
disproof of the Andrews--Curtis conjecture or of stable AC for AK(3).
