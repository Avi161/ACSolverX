# Positive-bridge primitive closure

Date: 2026-07-27

Status: **PROVEN**. Every positive-bridge target considered below is
nonprimitive.

Let

\[
F=F_0*\langle r\rangle,
\qquad F_0=F(x,y),
\tag{0.1}
\]

and let

\[
A=x^3y^{-4},
\qquad
B=xyxy^{-1}x^{-1}y^{-1}.
\tag{0.2}
\]

For \(V\in\{A,B\}\), \(\epsilon=\pm1\), and \(c\in F\), put

\[
W=r\,cV^\epsilon c^{-1}.
\tag{0.3}
\]

The zero-bridge case \(c\in\langle r\rangle F_0\) is already a stable
self-loop. This note determines the exact algebra forced by a hypothetical
primitive \(W\) when

\[
c\notin\langle r\rangle F_0.
\tag{0.4}
\]

The proof first converts a hypothetical primitive into a proper rank-two
normal-supplement problem inside a free group of rank two. The
Collins--Zieschang classification of one-relator presentations of torus-knot
groups and Turner's monomorphism-test theorem then force that subgroup to be
the whole free group, contradicting positive Bass--Serre bridge length.

## 1. The AK sources are non-simple and root-free

The exponent vectors in \(H_1(F_0;\mathbb Z)\) are

\[
[A]=(3,-4),
\qquad
[B]=(1,-1).
\tag{1.1}
\]

Both are primitive integer vectors.

The cyclic Whitehead graph of \(A\) on
\(\{x,x^{-1},y,y^{-1}\}\) is the four-cycle

\[
x-x^{-1}-y^{-1}-y-x,
\tag{1.2}
\]

and that of \(B\) is the four-cycle

\[
x-y^{-1}-x^{-1}-y-x.
\tag{1.3}
\]

They are connected and have no cut vertex. Whitehead's cut-vertex lemma
therefore makes both words non-simple in \(F_0\), hence nonprimitive.

They are also not proper powers. Indeed, if \(V=U^m\) with
\(|m|>1\), then \([V]=m[U]\), contradicting (1.1).

## 2. A hypothetical primitive gives a free quotient

Assume from now on that \(W\) is primitive. Let

\[
q:F\longrightarrow Q:=F/\langle\!\langle W\rangle\!\rangle.
\tag{2.1}
\]

Then \(Q\cong F_2\). Take a cyclically reduced conjugate \(R\) of \(W\).
Conjugation and cyclic reduction preserve the \(r\)-exponent sum, which is
one by (0.3), so \(R\) contains \(r\). Magnus's Freiheitssatz therefore
injects the subgroup on the omitted generators:

\[
q|_{F_0}:F_0\hookrightarrow Q.
\tag{2.2}
\]

Write

\[
K=q(F_0),
\qquad
v=q(V),
\qquad
s=q(r).
\tag{2.3}
\]

Thus \(K\cong F_2\) and \(v\) is non-simple in the free group \(K\).

In abelianization,

\[
[W]=[r]+\epsilon[V].
\tag{2.4}
\]

The coefficient of \([r]\) is one. Consequently the images of \([x]\) and
\([y]\) form a basis of \(H_1(Q;\mathbb Z)\), and (2.2) induces an
isomorphism

\[
H_1(K;\mathbb Z)\xrightarrow{\ \cong\ }H_1(Q;\mathbb Z).
\tag{2.5}
\]

In particular, (1.1) and (2.5) show that \(v\) is not a proper power in
\(Q\), not merely in \(K\).

## 3. Exact normal-supplement and intersection identities

The defining relation gives

\[
s=q(c)v^{-\epsilon}q(c)^{-1}.
\tag{3.1}
\]

Put

\[
N=\langle\!\langle v\rangle\!\rangle_Q.
\tag{3.2}
\]

Since \(Q=\langle K,s\rangle\) and \(s\in N\),

\[
\boxed{Q=KN.}
\tag{3.3}
\]

There is also an exact kernel-intersection identity. In \(F\),

\[
\langle\!\langle W,V\rangle\!\rangle_F
=
\langle\!\langle r,V\rangle\!\rangle_F.
\tag{3.4}
\]

Indeed, \(W\in\langle\!\langle r,V\rangle\!\rangle_F\), while the
identity \(W=r(cV^\epsilon c^{-1})\) gives
\(r=W(cV^{-\epsilon}c^{-1})\), so the reverse inclusion holds.
Therefore

\[
Q/N
\cong
F/\langle\!\langle W,V\rangle\!\rangle
\cong
F_0/\langle\!\langle V\rangle\!\rangle.
\tag{3.5}
\]

Restricting the quotient map to the embedded \(K\cong F_0\) gives

\[
\boxed{
K\cap N=\langle\!\langle v\rangle\!\rangle_K.
}
\tag{3.6}
\]

For \(V=A\), the quotient in (3.5) is the \((3,4)\)-torus-knot group.
For \(V=B\), it is the trefoil group \(B_3\), equivalently the
\((2,3)\)-torus-knot group.

## 4. The embedded old factor must be proper

The positive-bridge hypothesis now forces

\[
\boxed{K<Q.}
\tag{4.1}
\]

Suppose instead that \(K=Q\). Then (2.2) is an isomorphism. Compose \(q\)
with its inverse on \(K\) to obtain

\[
\theta:F\longrightarrow F_0,
\qquad
\theta|_{F_0}=\operatorname{id},
\qquad
\theta(r)=u\in F_0.
\tag{4.2}
\]

Its kernel is both

\[
\ker\theta=\langle\!\langle W\rangle\!\rangle_F
=\langle\!\langle ru^{-1}\rangle\!\rangle_F.
\tag{4.3}
\]

Magnus's normal-closure theorem makes \(W\) conjugate in \(F\) to
\((ru^{-1})^{\pm1}\). The latter has cyclic free-product syllable length
at most two in \(F_0*\langle r\rangle\).

On the other hand, choose the reduced double-coset normal form

\[
c=bda,
\qquad
b\in\langle r\rangle,
\quad a\in F_0,
\tag{4.4}
\]

where \(d\) is shortest in
\(\langle r\rangle cF_0\). Under (0.4), \(d\ne1\); its normal form starts
with an \(F_0\)-syllable, ends with a nontrivial
\(\langle r\rangle\)-syllable, and has even syllable length \(2\ell\) for
some \(\ell\ge1\). Conjugating \(W\) by \(b^{-1}\) gives

\[
r\,d\,(aV^\epsilon a^{-1})\,d^{-1}.
\tag{4.5}
\]

This is cyclically reduced in the free-product normal form and has syllable
length

\[
1+2\ell+1+2\ell=4\ell+2\ge6.
\tag{4.6}
\]

Cyclically reduced conjugates in a free product have the same syllable
length. Equations (4.3)--(4.6) contradict each other, proving (4.1).

## 5. Primitive-quotient reduction theorem

### Theorem 5.1

If the positive-bridge word (0.3) is primitive, then it determines a proper
subgroup \(K<Q\cong F_2\) and an element \(v\in K\) such that:

1. \(K\cong F_2\) and \(H_1(K;\mathbb Z)\to H_1(Q;\mathbb Z)\) is an
   isomorphism;
2. \(v\) is the image of \(A\) or \(B\), is non-simple in \(K\), and is
   not a proper power in \(Q\);
3. with \(N=\langle\!\langle v\rangle\!\rangle_Q\), \(Q=KN\);
4. \(K\cap N=\langle\!\langle v\rangle\!\rangle_K\); and
5. \(Q/N\cong F_0/\langle\!\langle V\rangle\!\rangle\), the corresponding
   torus-knot group.

Thus, proving that no such proper \(K<Q\) can occur for either AK source
rules out every positive-bridge primitive in one stroke.

## 6. Why Cohen--Lyndon alone does not finish the proof

It is tempting to combine \(Q=KN\) with Cohen--Lyndon asphericity and
replace a Cohen--Lyndon transversal by representatives in \(K\). That
replacement is invalid: the theorem supplies a particular transversal whose
relator conjugates freely generate \(N\), and an arbitrary transversal need
not retain that property.

The failure already occurs in rank two with a primitive source. In
\(Q=F(a,b)\), let

\[
K=\langle a,\ b[a,b]\rangle,
\qquad
v=a,
\qquad
N=\langle\!\langle a\rangle\!\rangle_Q.
\tag{6.1}
\]

Here \([a,b]=aba^{-1}b^{-1}\).
Modulo \(N\), the second generator of \(K\) maps to \(b\), so \(Q=KN\).
The Stallings core of \(K\) has three vertices and rank two, hence \(K<Q\).
Moreover, \(K\) is free on \(a,b[a,b]\), and killing \(a\) maps the second
basis element to \(b\). Hence this example also satisfies

\[
K\cap N=\langle\!\langle a\rangle\!\rangle_K.
\tag{6.2}
\]

Thus root-freeness, equal ranks, an isomorphism on first homology, and even
the exact intersection (3.6) do not suffice. Any completion must use
additional structure of the non-simple AK sources and their torus-knot
quotients.

## 7. Small torus relators have one Nielsen class

For coprime integers \(a,b>1\), put

\[
G_{a,b}=\langle X,Y\mid X^aY^b\rangle.
\tag{7.1}
\]

The Collins--Zieschang classification says that the Nielsen classes of
two-generator one-relator presentations of \(G_{a,b}\) are represented by

\[
v_{a,k}(X,Y^b)
\quad\text{and}\quad
v_{\ell,b}(X^a,Y),
\tag{7.2}
\]

where \(v_{m,n}\) is the primitive conjugacy class with exponent vector
\((m,n)\), and

\[
(k,a)=(\ell,b)=1,
\qquad 0<2k<a,
\qquad 0<2\ell<b.
\tag{7.3}
\]

Here Nielsen equivalence permits an automorphism of the ambient rank-two
free group, conjugation of the relator, and inversion of the relator.

For the two parameter pairs needed here, (7.2)--(7.3) collapse to one
class:

- for \((a,b)=(2,3)\), the first family is empty and the second has only
  \(\ell=1\), giving
  \(v_{1,3}(X^2,Y)\sim X^2Y^3\);
- for \((a,b)=(3,4)\), the only parameters are \(k=\ell=1\), and both
  \(v_{3,1}(X,Y^4)\) and \(v_{1,4}(X^3,Y)\) are conjugate to
  \(X^3Y^4\).

Consequently, if a relator \(u\) on a rank-two free basis presents
\(G_{2,3}\) or \(G_{3,4}\), then an automorphism sends \(u\) to a conjugate
of the corresponding standard relator or its inverse.

## 8. Exact normalization of the two AK sources

For \(A\), the basis inversion \(y\mapsto y^{-1}\) sends

\[
X^3Y^4\longmapsto A=x^3y^{-4}.
\tag{8.1}
\]

For \(B\), put

\[
a=xyx,
\qquad
b=xy.
\tag{8.2}
\]

This is a basis because

\[
x=b^{-1}a,
\qquad
y=a^{-1}b^2.
\tag{8.3}
\]

Direct free reduction gives

\[
B=ab^{-3}a.
\tag{8.4}
\]

The conjugate \(aBa^{-1}\) of (8.4) is

\[
aBa^{-1}=a^2b^{-3}.
\tag{8.5}
\]

After the basis inversion \(b\mapsto b^{-1}\), this is the standard
\((2,3)\)-torus relator. Thus both the domain copy of \(V\) and its image
\(v\in Q\), viewed as defining relators by (3.5)--(3.6), belong to the
single Nielsen class identified in Section 7.

For comparison, in the usual braid coordinates
\(\Delta=xyx\) and \(t=xy\), the braid relation gives
\(\Delta^2=t^3\), again identifying the \(B\)-quotient with
\(G_{2,3}\).

## 9. Turner rigidity forces \(K=Q\)

Choose free bases identifying both \(K\) and \(Q\) with \(F_2\), and let

\[
\iota:K\hookrightarrow Q
\tag{9.1}
\]

be the inclusion from Section 2. By Sections 7--8, precomposing \(\iota\)
with an automorphism of \(K\), postcomposing with an automorphism of \(Q\),
and then applying an inner automorphism produces an injective endomorphism

\[
\eta:F_2\hookrightarrow F_2
\tag{9.2}
\]

such that, for \((p,q)=(2,3)\) or \((3,4)\),

\[
\eta(R)=R^\delta,
\qquad
R=X^pY^q,
\qquad
\delta\in\{+1,-1\}.
\tag{9.3}
\]

The word \(R\) is non-simple. Indeed, every proper free factor of \(F_2\)
is cyclic and generated by a primitive element. If \(R=u^m\) lay in such
a factor, the primitive exponent vector \((p,q)\) would force
\(|m|=1\), making \(R\) primitive. Its one-relator quotient would then be
infinite cyclic, whereas \(G_{p,q}\) surjects onto the noncyclic group
\(C_p*C_q\).

Turner's monomorphism-test theorem states that a non-simple element of a
finitely generated free group is fixed by no nonautomorphic injective
endomorphism. If \(\delta=1\), apply the theorem directly to \(\eta\). If
\(\delta=-1\), then

\[
\eta^2(R)=\eta(R^{-1})=\eta(R)^{-1}=R,
\tag{9.4}
\]

so the theorem makes \(\eta^2\) an automorphism. Surjectivity of
\(\eta^2\) implies surjectivity of \(\eta\), hence \(\eta\) is an
automorphism in this case as well.

All maps used before and after \(\iota\) were automorphisms. Therefore
\(\iota\) is onto:

\[
\boxed{K=Q.}
\tag{9.5}
\]

This contradicts the positive-bridge conclusion \(K<Q\) in (4.1).

## 10. Positive-bridge closure theorem

### Theorem 10.1

Let \(F=F(x,y)*\langle r\rangle\), let \(V=A\) or \(B\), and let

\[
W=r\,cV^\epsilon c^{-1},
\qquad \epsilon=\pm1.
\tag{10.1}
\]

If \(c\notin\langle r\rangle F_0\), then \(W\) is not primitive in \(F\).

Equivalently, primitivity of (10.1) forces zero Bass--Serre bridge:

\[
\boxed{
W\text{ primitive}
\quad\Longrightarrow\quad
c\in\langle r\rangle F_0.
}
\tag{10.2}
\]

Together with the zero-bridge identity from the companion storage note,
every one-edge multiplication into the normalized primitive \(r\)-slot is
now closed: zero bridge is a literal stable self-loop, while positive bridge
cannot produce a deletable primitive relator.

This theorem closes one post-storage edge stratum. It does not close histories
with two or more intervening row changes, changed source relators, another
deleted slot, or loss of the normalized checkpoint. AK(3), stable
Andrews--Curtis, and Andrews--Curtis therefore remain open.

## References

1. D. J. Collins, *Presentations of the amalgamated free product of two
   infinite cycles*, Math. Ann. **237** (1978), 233--241.
2. H. Zieschang, *Generators of the free product with amalgamation of two
   infinite cyclic groups*, Math. Ann. **227** (1977), 195--221.
3. J. C. Dean, *Small Seifert-fibered Dehn surgery on hyperbolic knots*,
   Algebraic & Geometric Topology **3** (2003), 435--472, especially
   pp. 453--454.
4. E. C. Turner, *Test words for automorphisms of free groups*, Bull. London
   Math. Soc. **28** (1996), 255--263.
5. D. Zhao and Q. Zhang, *A note on test elements for monomorphisms of free
   groups*, arXiv:2408.13449, Proposition 3.1(2).
