# A parafree stable self-embedding corridor

Date: 2026-07-27

Status: **PROVEN**.  The simultaneous proper-extension obstruction of
Result 117 is realizable by a primitive stable deletion.  The resulting
proper endomorphism also gives an infinite stable self-embedding corridor
for AK(3).  This is not a proof of stable triviality.

## 1. A proper unimodular embedding of rank-two free groups

Let

\[
H=F(X,U),
\qquad
Q=F(x,y),
\tag{1.1}
\]

and put

\[
u=yxyx^{-1}y^{-1}=y[x,y].
\tag{1.2}
\]

Define

\[
\phi:H\longrightarrow Q,
\qquad
\phi(X)=x,
\qquad
\phi(U)=u.
\tag{1.3}
\]

The exponent vectors of \(x,u\) are \((1,0),(0,1)\), so they do not
commute.  Their subgroup

\[
K=\langle x,u\rangle
\tag{1.4}
\]

is a noncyclic two-generated subgroup of a free group, hence is free of
rank two and \((x,u)\) is a basis of \(K\).  Thus \(\phi\) is injective,
and

\[
\phi_{\mathrm{ab}}=I_2.
\tag{1.5}
\]

The subgroup is proper.  Map \(Q\) to \(S_3\) by

\[
x\longmapsto(23),
\qquad
y\longmapsto(12).
\tag{1.6}
\]

Then \(u\mapsto(23)\), so the image of \(K\) is
\(\langle(23)\rangle\), while the image of \(y\) is \((12)\).  Hence

\[
\boxed{K<Q.}
\tag{1.7}
\]

Equivalently, the Stallings core of \(K\) has three vertices and four
edges: an x-loop at the base vertex, a y-edge to a second vertex, an
x-edge to a third vertex, and a y-loop at the third vertex.

## 2. Every root-free one-relator quotient embeds

Let \(V\in H\) be root-free and write

\[
G(V)=H/\langle\!\langle V\rangle\!\rangle.
\tag{2.1}
\]

The target one-relator quotient has the Tietze presentation

\[
\begin{aligned}
Q/\langle\!\langle\phi(V)\rangle\!\rangle
\cong
\langle X,U,y\mid
V(X,U),\
U^{-1}yXyX^{-1}y^{-1}\rangle.
\end{aligned}
\tag{2.2}
\]

The second relator in (2.2), viewed as an equation over the coefficient
group \(G(V)\), has y-exponent sum one.  The one-relator torsion theorem
makes \(G(V)\) torsion-free because \(V\) is root-free.  Klyachko's
unimodular-equation theorem therefore injects the coefficient group:

\[
\boxed{
G(V)\hookrightarrow
Q/\langle\!\langle\phi(V)\rangle\!\rangle.
}
\tag{2.3}
\]

In subgroup language, for every root-free \(V\),

\[
\boxed{
K\cap\langle\!\langle\phi(V)\rangle\!\rangle_Q
=
\phi(\langle\!\langle V\rangle\!\rangle_H).
}
\tag{2.4}
\]

The induced map on first homology is also an isomorphism, because (1.5)
identifies the exponent lattices before quotienting by \([V]\).

## 3. Simultaneous application to the two AK relators

In the domain basis \((X,U)\), put

\[
A=X^3U^{-4},
\qquad
B=XUXU^{-1}X^{-1}U^{-1}.
\tag{3.1}
\]

Both words are root-free.  Apply (2.3)--(2.4) to both.  With

\[
a=\phi(A),
\qquad
b=\phi(B),
\tag{3.2}
\]

the maps

\[
G_{3,4}=H/\langle\!\langle A\rangle\!\rangle
\hookrightarrow
P_A=Q/\langle\!\langle a\rangle\!\rangle
\tag{3.3}
\]

and

\[
G_{2,3}=H/\langle\!\langle B\rangle\!\rangle
\hookrightarrow
P_B=Q/\langle\!\langle b\rangle\!\rangle
\tag{3.4}
\]

are simultaneous first-homology isomorphisms.

Both inclusions are proper.  For (3.3), map \(P_A\) to \(S_4\) by

\[
x\longmapsto(234),
\qquad
y\longmapsto(12).
\tag{3.5}
\]

Then \(u\mapsto(23)\), so \(x^3=u^4=1\) and the A-relation holds.  The
coefficient image

\[
\langle(234),(23)\rangle=S_{\{2,3,4\}}
\tag{3.6}
\]

fixes 1, whereas \(y\mapsto(12)\) moves 1.  Thus y does not lie in the
coefficient subgroup of \(P_A\).

For (3.4), use (1.6).  There \(u\mapsto x\mapsto(23)\), so
\(B(x,u)=B(x,x)=1\).  The coefficient image is
\(\langle(23)\rangle\), which does not contain \(y\mapsto(12)\).
Therefore

\[
\boxed{
G_{3,4}\lneq P_A,
\qquad
G_{2,3}\lneq P_B.
}
\tag{3.7}
\]

The two image relators normally generate \(Q\).  Indeed, A and B normally
generate \(H\), so the normal closure of \(a,b\) in \(Q\) contains K.
Modulo the normal closure of K, \(x=1\) and

\[
u=yxyx^{-1}y^{-1}=y,
\tag{3.8}
\]

so \(y=1\) as well.  Hence

\[
\boxed{
\langle\!\langle a,b\rangle\!\rangle_Q=Q.
}
\tag{3.9}
\]

It follows that b normally generates \(P_A\), and a normally generates
\(P_B\).

Thus the entire simultaneous proper-extension package in Result 117 can
hold for a proper unimodular embedding.

## 4. A primitive syllable-six realization

The embedding (1.3) is itself produced by one primitive stable deletion.
In

\[
H*\langle r\rangle=F(X,U,r),
\tag{4.1}
\]

put

\[
R=U^{-1}rXrX^{-1}r^{-1}.
\tag{4.2}
\]

The U-letter occurs exactly once, so R is primitive.  It is cyclically
reduced in the splitting \(H*\langle r\rangle\), with syllable sequence

\[
U^{-1}\mid r\mid X\mid r\mid X^{-1}\mid r^{-1}
\tag{4.3}
\]

and therefore

\[
\lambda(R)=6.
\tag{4.4}
\]

This is not secretly the two-source target from Result 117.  In the fixed
basis \((X,U,r)\),

\[
[R]=(0,-1,1),
\tag{4.5}
\]

whereas a word
\(r cA^\epsilon c^{-1}dB^\eta d^{-1}\) has exponent vector

\[
(3\epsilon+\eta,-4\epsilon-\eta,1),
\tag{4.6}
\]

whose old-factor part is \(\pm(4,-5)\) or \(\pm(2,-3)\).  Thus R cannot
be conjugate, or inverse after restoring the r-orientation, to a word of
that exact two-source form.

Solving \(R=1\) for U gives

\[
U=rXrX^{-1}r^{-1}.
\tag{4.7}
\]

After renaming \((X,r)=(x,y)\), this is exactly (1.2).  Thus the primitive
quotient map restricts to \(\phi\) on the old factor.  In particular,
even primitivity with cyclic syllable length greater than two, both exact
one-relator intersections, both proper torus extensions, identical first
homology, and opposite-source normal generation do not force \(K=Q\).

## 5. The stable AK corridor

Start with the stabilized AK tuple

\[
(A(X,U),B(X,U),r).
\tag{5.1}
\]

The old pair normally generates H.  Hence its normal closure in
\(H*\langle r\rangle\) contains

\[
[X,r]U^{-1}=XrX^{-1}r^{-1}U^{-1}.
\tag{5.2}
\]

By finitely many AC2 multiplications using conjugates of the two old
source rows, change the r-row to

\[
r[X,r]U^{-1}.
\tag{5.3}
\]

This is conjugate to R in (4.2).  After AC3 normalization, straighten the
primitive R and apply the stable substitution-and-removal composite,
deleting R with the U-generator.  Equation (4.7) sends the two survivors
to

\[
(\phi(A),\phi(B))
\tag{5.4}
\]

in the basis \((x,y)=(X,r)\).

### Theorem 5.1 (proper stable self-embedding)

The AK presentation is stably AC-equivalent to its image under the proper
injective unimodular endomorphism

\[
\phi(x)=x,
\qquad
\phi(y)=yxyx^{-1}y^{-1}.
\tag{5.5}
\]

The same construction can be repeated.  Therefore, for every \(n\ge0\),

\[
(A,B)\sim_{\mathrm{stable\ AC}}
(\phi^n(A),\phi^n(B)).
\tag{5.6}
\]

To justify repeatability in the ambient group, put

\[
y_n=\phi^n(y).
\tag{5.7}
\]

Then

\[
y_{n+1}=y_nxy_nx^{-1}y_n^{-1}
=(y_nx)y_n(y_nx)^{-1}.
\tag{5.8}
\]

Thus every \(y_n\) is conjugate to y.  The subgroup
\(\phi^n(F_2)=\langle x,y_n\rangle\) normally generates the ambient
\(F_2\), and \(\phi^n(A),\phi^n(B)\) normally generate that subgroup.
Their ambient normal closure is therefore all of \(F_2\), so the AC2
manufacture in (5.2)--(5.3) is available at every stage.

The image subgroups form a strictly descending chain

\[
F_2>\phi(F_2)>\phi^2(F_2)>\cdots.
\tag{5.9}
\]

Indeed, equality at any step would pull back through the injective
isomorphism onto \(\phi^n(F_2)\) and make \(\phi\) surjective, contrary to
(1.7).

This is not an ambient-automorphism self-loop: \(\phi\) is proper.  It is
also not a proof that AK(3) is stably trivial.  It supplies a genuinely new
infinite stable corridor and proves that the next two-source argument must
use the exact factorization by one conjugate of A and one conjugate of B.
The abstract simultaneous-extension data of Result 117 are insufficient.

## 6. The full conjugating-endomorphism family

The example is one member of a larger exact family.  For arbitrary
\(g\in F(x,y)\), define

\[
\phi_g(x)=x,
\qquad
\phi_g(y)=g y g^{-1}.
\tag{6.1}
\]

The two image vectors are \((1,0),(0,1)\), so the image subgroup is
noncyclic of rank two and \(\phi_g\) is injective.  It normally generates
\(F_2\), because its generators normally contain x and a conjugate of y.

For every root-free \(V\), the induced one-relator map is injective by the
same Klyachko argument: after adjoining a name U for \(g y g^{-1}\), the
relative relator

\[
U^{-1}g(X,y)y g(X,y)^{-1}
\tag{6.2}
\]

has y-exponent one.

There is also a stable realization for every g.  In
\(F(X,U,r)\), let

\[
R_g=U^{-1}g(X,r)r g(X,r)^{-1}.
\tag{6.3}
\]

It contains U once and is primitive.  Modulo the normal closure of A and
B, both X and U vanish, while \(g(1,r)\) is a power of r; hence \(R_g\)
maps to r.  Therefore \(R_gr^{-1}\) lies in the old-source normal closure,
and finite AC2 traffic changes the stabilized r-row to \(R_g\).  Deleting
U sends the survivors to

\[
(\phi_g(A),\phi_g(B)).
\tag{6.4}
\]

Whenever \(\phi_g\) is proper, this is another nonautomorphic stable
self-embedding corridor.  The explicit map (5.5) is the case \(g=yx\).
This family turns the next search into a theoretical design problem:
choose or exclude a conjugator g whose proper image exposes a new
primitive compression, rather than searching the AC graph blindly.

## 7. Internal relative conjugators cannot expose a primitive row

The whole family has a uniform first barrier.  Let

\[
V=A kB^\eta k^{-1}
\quad\hbox{or}\quad
V=B kA^\eta k^{-1},
\qquad k\in F(x,y),\quad \eta\in\{\pm1\}.
\tag{7.1}
\]

The axis-alignment theorem for the original AK sources proves that every
word in (7.1) is nonprimitive.  The possible exponent vectors are

\[
(4,-5),\qquad (2,-3),\qquad (-2,3),
\tag{7.2}
\]

according to the order and sign.  Each vector is primitive, so V is
root-free.

Now fix any g and put \(K_g=\phi_g(F_2)\).  If a relative conjugator
\(h\) lies in \(K_g\), write \(h=\phi_g(k)\).  The corresponding changed
image source is exactly

\[
\phi_g(A)h\phi_g(B)^\eta h^{-1}
=\phi_g(AkB^\eta k^{-1})
=\phi_g(V),
\tag{7.3}
\]

or the analogous expression with A and B exchanged.  By Section 6,
Klyachko gives an injection

\[
F_2/\langle\!\langle V\rangle\!\rangle
\hookrightarrow
F_2/\langle\!\langle\phi_g(V)\rangle\!\rangle.
\tag{7.4}
\]

If \(\phi_g(V)\) were primitive, the group on the right would be infinite
cyclic.  Hence the group on the left would be cyclic.  Its abelianization
is already infinite cyclic by (7.2), so it would be \(\mathbb Z\).
Normalize the resulting epimorphism \(F_2\to\mathbb Z\) by an ambient
automorphism.  Its kernel is then the normal closure of one basis element
P.  Thus \(\langle\!\langle V\rangle\!\rangle=
\langle\!\langle P\rangle\!\rangle\), and Magnus's normal-closure theorem
makes V conjugate to \(P^{\pm1}\), contrary to the axis-alignment result.

Therefore no one-source multiplication whose relative conjugator lies in
the image subgroup can create a primitive row.  This holds for every g,
with no word-length bound:

\[
\boxed{
h\in K_g
\Longrightarrow
\phi_g(A)h\phi_g(B)^\eta h^{-1}
\text{ and }
\phi_g(B)h\phi_g(A)^\eta h^{-1}
\text{ are nonprimitive}.}
\tag{7.5}
\]

Thus a primitive compression reached through a proper corridor must use
a conjugator outside \(K_g\), modify more than one source before the
test, or use another stabilizer.  The exact remaining one-step problem is
the geometry of the nontrivial double cosets \(K_g\backslash F_2/K_g\),
not the internal copy of the original arbitrary-conjugator problem.

## 8. The first proper corridor has no one-source exit at all

For the concrete map \(\phi=\phi_{yx}\), put

\[
a=\phi(A),\qquad b=\phi(B).
\tag{8.1}
\]

Free and cyclic reduction gives the exact representatives

\[
a=xxxyxYYYYXY,
\qquad |a|=11,
\tag{8.2}
\]

and

\[
b=xyxyXYxyxYXYXyxYXY,
\qquad |b|=18.
\tag{8.3}
\]

Here capital letters denote inverses.  Let \(L(P,Q)\) be the maximum
length of a common cyclic factor of P and Q.  The finite factor
certificate read directly from (8.2)--(8.3) is

\[
L(a,b^{-1})=3,
\qquad
\operatorname{Sub}_4(a)\cap\operatorname{Sub}_4(b^{-1})=\varnothing,
\tag{8.4}
\]

and

\[
L(a,b)=4,
\qquad
\operatorname{Sub}_5(a)\cap\operatorname{Sub}_5(b)=\varnothing.
\tag{8.5}
\]

For example the common length-three factors in (8.4) are
\(XYx,YXY,xyx,yxY\), while the common length-four factors in (8.5) are
\(YXYx,xyxY\).  The stated empty intersections certify maximality.

The Cayley-tree axis-alignment lemma used for Result 116 is unbounded in
the ambient conjugator:

\[
\min_{h\in F_2}\|P hQh^{-1}\|
=|P|+|Q|-2L(P,Q^{-1}).
\tag{8.6}
\]

Equations (8.2)--(8.5) therefore give

\[
\min_h\|a hbh^{-1}\|=11+18-2\cdot3=23,
\tag{8.7}
\]

and

\[
\min_h\|a hb^{-1}h^{-1}\|=11+18-2\cdot4=21.
\tag{8.8}
\]

The same minima hold with a and b exchanged.  Yet their exponent vectors
are \((4,-5)\), \((2,-3)\), and \((-2,3)\), so a primitive representative
would have cyclic length 9 or 5 by Osborne--Zieschang.  Thus every value
in (8.7)--(8.8) is too long:

\[
\boxed{
a hb^\eta h^{-1}
\text{ and }
b ha^\eta h^{-1}
\text{ are nonprimitive for every }h\in F_2,
\ \eta=\pm1.}
\tag{8.9}
\]

This closes all nontrivial double cosets as well as the internal ones for
the first proper self-embedding.  It does not yet prove the same inequality
for every \(\phi_g\) or every iterate of \(\phi\).  The normalized family
suggests a weighted bridge-length theorem, but that general statement
still requires a proof rather than a bounded census.

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.

## References

1. A. A. Klyachko, *A funny property of a sphere and equations over
   groups*, Comm. Algebra **21** (1993), 2555--2575.
