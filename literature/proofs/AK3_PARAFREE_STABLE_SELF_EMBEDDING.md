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
In particular, neither cyclic factor can cancel completely.

The Cayley-tree axis-alignment lemma used for Result 116 is unbounded in
the ambient conjugator.  In this non-complete-cancellation case, its
two-seam common-factor formula is

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

## 9. Exact external double-coset geometry at the first image

The external part of Section 8 has a sharper Stallings explanation.  The
folded core \(\Gamma_K\) of

\[
K=\langle x,yxyx^{-1}y^{-1}\rangle
\tag{9.1}
\]

has vertices \(0,1,2\), an x-loop at 0, the path

\[
0\mathrel{\mathop{\longrightarrow}^{y}}1
\mathrel{\mathop{\longrightarrow}^{x}}2,
\tag{9.2}
\]

and a y-loop at 2.  Its off-diagonal fiber product has, up to transposing
the two coordinates, only the undirected path

\[
(0,1)\mathrel{\mathop{\longrightarrow}^{x}}(0,2)
\mathrel{\mathop{\longrightarrow}^{y}}(1,2).
\tag{9.3}
\]

Thus its longest reduced path has length two, with labels xy and its
inverse YX.  There is no off-diagonal reduced common path of length three.

Let u,v be nontrivial elements of K and let \(h\notin K\).  If
\(\operatorname{Ax}(u)\) and \(h\operatorname{Ax}(v)\) shared three
edges, the common segment and its h-translate back would project to two
equal-labelled length-three paths in \(\Gamma_K\).  Equal starting
vertices would force \(h\in K\) by freeness of the Cayley-tree action;
distinct starting vertices contradict (9.3).  Hence

\[
\operatorname{diam}
\bigl(\operatorname{Ax}(u)\cap h\operatorname{Ax}(v)\bigr)\le2.
\tag{9.4}
\]

For the image sources a,b of Section 8, whose translation lengths are 11
and 18, disjoint axes add a positive bridge and intersecting axes can
cancel at most twice the overlap in (9.4).  Therefore every external
double coset satisfies

\[
\|a hb^\eta h^{-1}\|
\ge 11+18-2\cdot2=25,
\qquad h\notin K,\quad \eta=\pm1.
\tag{9.5}
\]

The bound is exact.  For the positive sign, \(h=y\notin K\) gives cyclic
length 25.  For the negative sign, \(h=xxYX\notin K\) also gives cyclic
length 25.  Membership failure is read directly in \(\Gamma_K\): y ends
at vertex 1, while xxYX is not readable from vertex 0.  Cyclic conjugacy,
inversion, and \(h\mapsto h^{-1}\) give the same exact minimum after
exchanging a and b.  Thus

\[
\boxed{
\min_{h\notin K}\|a hb^\eta h^{-1}\|
=\min_{h\notin K}\|b ha^\eta h^{-1}\|=25.}
\tag{9.6}
\]

This isolates the internal minima 23 and 21 from Section 8: all shorter
axis alignments occur inside K, where Result 121 supplies the general
quotient obstruction.  The fiber-product formulation is the right route
for a general \(g\), because it measures the self-overlap of the normalized
bridge rather than relying on a false reverse triangle inequality for
cyclic length.

## 10. A uniform barbell-piece bound closes the whole family

Normalize an arbitrary reduced conjugator as

\[
g=x^p c y^q,
\tag{10.1}
\]

where the maximal initial x-block and terminal y-block have been removed.
Right multiplication by \(y^q\) does not change \(gyg^{-1}\), and left
multiplication by \(x^p\) globally conjugates the image pair by \(x^p\).
If c is empty, \(\phi_g\) is an automorphism and Result 116 applies.

Suppose c is nonempty.  Then c begins in \(y^{\pm1}\), ends in
\(x^{\pm1}\), and has length \(n\ge2\).  The folded core \(\Gamma_c\)
of

\[
K_c=\langle x,cyc^{-1}\rangle
\tag{10.2}
\]

is a barbell: an x-loop at \(v_0\), a path of n edges labelled c from
\(v_0\) to \(v_n\), and a y-loop at \(v_n\).  The endpoint conditions and
reduction of c make this graph folded.

### Lemma 10.1 (uniform off-diagonal piece bound)

Every reduced path in the off-diagonal fiber product
\(\Gamma_c\times_R\Gamma_c\) has length at most \(3n\).

**Proof.**  Such a path projects to two reduced paths with the same label.
Write their successive positions on the bridge as \(i<j\).  This order is
preserved: equality would contradict determinism of the folded inverse
graph, while swapping across one edge would require a letter to equal its
inverse.

At an interior bridge vertex a reduced path cannot turn around.  The lower
coordinate can therefore use only the x-loop at \(v_0\), and the upper
coordinate only the y-loop at \(v_n\).  Each loop can occur in at most one
block.  If at least one projection uses no endpoint loop, it is monotone
on the bridge, so the common path has length at most n.

If both projections use their endpoint loops, the common label is
simultaneously a subword of

\[
c^{-1}x^k c
\quad\text{and}\quad
c y^\ell c^{-1},
\qquad k,\ell\ne0,
\tag{10.3}
\]

with either sign allowed in the two pure blocks.  The consecutive x-block
cannot meet the nonempty central y-block in the second word.  It must lie
inside one of that word's two c-flanks, so \(|k|\le n\).  The portions on
the two sides of the x-block lie in the two c-flanks of the first word and
have total length at most \(2n\).  The common path therefore has length at
most \(3n\). \(\square\)

Now put \(a_c=\phi_c(A)\), \(b_c=\phi_c(B)\).  No seam cancels in

\[
a_c=x^3cy^{-4}c^{-1},
\qquad \|a_c\|=2n+7,
\tag{10.4}
\]

or in the three conjugated-y blocks of \(b_c\), so

\[
\|b_c\|=6n+6.
\tag{10.5}
\]

If \(h\notin K_c\), an intersection of the axes of \(a_c\) and
\(hb_c^{\pm1}h^{-1}\) projects to an off-diagonal fiber-product path.
Lemma 10.1 and the standard tree product estimate give

\[
\|a_c h b_c^{\pm1}h^{-1}\|
\ge (2n+7)+(6n+6)-2(3n)
=2n+13\ge17.
\tag{10.6}
\]

The same estimate holds with the sources exchanged.  This exceeds the
Osborne--Zieschang primitive lengths 9 and 5.  If \(h\in K_c\), Result
121 gives nonprimitivity by the Klyachko--Magnus quotient argument.
Combining the internal and external cases proves

\[
\boxed{
\phi_g(A)h\phi_g(B)^\eta h^{-1}
\text{ and }
\phi_g(B)h\phi_g(A)^\eta h^{-1}
\text{ are nonprimitive}}
\tag{10.7}
\]

for every \(g,h\in F_2\) and \(\eta=\pm1\).  Since every iterate in
Section 5 still fixes x and sends y to a conjugate of y, (10.7) holds at
every depth of the descending stable corridor.  Thus the entire family of
Result 120 has no one-source primitive exit.  Any successful corridor use
must modify both sources before the primitive test, use more than one
row-changing edge, or change the stabilizer architecture.

## 11. The corridor maps reflect primitivity

The Klyachko argument is not limited to AK source products.

### Theorem 11.1 (primitivity reflection)

For every \(g\in F_2\) and every \(V\in F_2\),

\[
\phi_g(V)\text{ primitive in }F_2
\quad\Longrightarrow\quad
V\text{ primitive in }F_2.
\tag{11.1}
\]

**Proof.**  Since \(\phi_g\) is injective, a proper-power V would have
proper-power image, so (11.1)'s hypothesis makes V root-free.  Section 6
and Klyachko then embed

\[
G(V)=F_2/\langle\!\langle V\rangle\!\rangle
\hookrightarrow
F_2/\langle\!\langle\phi_g(V)\rangle\!\rangle
\cong\mathbb Z.
\tag{11.2}
\]

Thus \(G(V)\) is cyclic.  The map \(\phi_g\) is the identity on
abelianization, and a primitive image has primitive exponent vector.
Consequently \(H_1(G(V))\cong\mathbb Z\), so \(G(V)\cong\mathbb Z\).
Normalize the quotient epimorphism \(F_2\to\mathbb Z\) by an ambient
automorphism.  Its kernel is the normal closure of a basis element P.
Hence

\[
\langle\!\langle V\rangle\!\rangle
=\langle\!\langle P\rangle\!\rangle.
\tag{11.3}
\]

Magnus's normal-closure theorem makes V conjugate to \(P^{\pm1}\), proving
that V is primitive. \(\square\)

There is an immediate history-level consequence.  Start from
\((\phi_g(A),\phi_g(B))\) and perform any finite AC1--AC3 history in which
every conjugator lies in \(K_g=\phi_g(F_2)\).  Every row stays in \(K_g\),
and the isomorphism \(\phi_g:F_2\to K_g\) pulls the entire history back,
move by move, to a history from \((A,B)\).  If an image row becomes
primitive in the ambient free group, Theorem 11.1 makes its pulled-back
row primitive as well.

Thus the proper stable corridor creates no new primitive terminal through
purely internal traffic of any depth, not merely through the one-source
move closed in Result 121.  Any genuinely new two-row or longer exit must
use an ambient conjugator outside the current image subgroup, or an
ambient automorphism which moves that subgroup.

## 12. One external second edge is too long

Fix a proper normalized corridor with bridge c of length \(n\ge2\), and
write

\[
a=\phi_c(A),\qquad b=\phi_c(B),\qquad K=K_c.
\tag{12.1}
\]

First change the a-row using an internal conjugator:

\[
a_1=a h b^\epsilon h^{-1},
\qquad h\in K,\quad \epsilon=\pm1.
\tag{12.2}
\]

Then target the b-row using an external conjugator:

\[
b_1=b k a_1^\delta k^{-1},
\qquad k\notin K,\quad \delta=\pm1.
\tag{12.3}
\]

The row \(a_1\) lies in K.  Its exponent vector and elementary cyclic
length lower bound are

\[
[a_1]=
\begin{cases}
(4,-5),&\epsilon=1,\\
(2,-3),&\epsilon=-1,
\end{cases}
\qquad
\|a_1\|\ge
\begin{cases}
9,&\epsilon=1,\\
5,&\epsilon=-1.
\end{cases}
\tag{12.4}
\]

The b-axis has length \(6n+6\).  Since k is external, Lemma 10.1 bounds
its overlap with the translated \(a_1\)-axis by \(3n\).  The tree product
estimate therefore gives

\[
\|b_1\|
\ge (6n+6)+\|a_1\|-6n
=\|a_1\|+6.
\tag{12.5}
\]

The four cases are

\[
\begin{array}{c|c|c|c}
(\epsilon,\delta)&[b_1]&
\text{primitive length}&\text{lower bound from (12.5)}\\ \hline
(+,+)&(5,-6)&11&15\\
(+,-)&(-3,4)&7&15\\
(-,+)&(3,-4)&7&11\\
(-,-)&(-1,2)&3&11
\end{array}
\tag{12.6}
\]

Every lower bound is strictly too large for primitivity.  Hence no history
of the form (12.2)--(12.3) creates a primitive second row.

If k is internal instead, the two moves lift to the original AK pair by
Theorem 11.1; the corridor contributes no new terminal.  Thus, in the
orientation which first changes the A-image and then targets the B-image,
a genuinely new two-row primitive exit must already use an external
conjugator in the first edge.  The reverse target orientation is not
claimed closed by this estimate, because its fixed A-image axis is the
short one.

## 13. At the first image, both second-edge orientations close

Return to the concrete first image \(g=yx\), with subgroup K and source
lengths

\[
\|a\|=11,\qquad \|b\|=18.
\tag{13.1}
\]

First change the b-row internally:

\[
b_1=b h a^\epsilon h^{-1},
\qquad h\in K.
\tag{13.2}
\]

Result 122 applies to every h and both source orders, giving

\[
\|b_1\|\ge
\begin{cases}
23,&\epsilon=1,\\
21,&\epsilon=-1.
\end{cases}
\tag{13.3}
\]

Now target a with an external conjugator:

\[
a_1=a k b_1^\delta k^{-1},
\qquad k\notin K.
\tag{13.4}
\]

Result 123 bounds the overlap of any two K-axes across an external double
coset by two.  Hence

\[
\|a_1\|\ge
\begin{cases}
11+23-4=30,&\epsilon=1,\\
11+21-4=28,&\epsilon=-1.
\end{cases}
\tag{13.5}
\]

The exponent-vector audit is

\[
\begin{array}{c|c|c}
(\epsilon,\delta)&[a_1]&\text{primitive length}\\ \hline
(+,+)&(7,-9)&16\\
(+,-)&(-1,1)&2\\
(-,+)&(1,-1)&2\\
(-,-)&(5,-7)&12
\end{array}
\tag{13.6}
\]

so (13.5) excludes all four cases.  Section 12 already closes the opposite
orientation, where an internal a-change is followed by an external
b-change.  If both conjugators are internal, Theorem 11.1 pulls the
history back to the original AK pair.

Therefore, at the first proper image, any genuinely new two-row primitive
terminal must use an external conjugator on its first row-changing edge.
This is a reduction, not a closure of the first-external branch.  Once the
first changed row leaves K, the second axis no longer lies in the same
barbell core and requires a three-translate geometry.

## 14. Three-translate geometry closes every second AC2 edge

The needed three-translate geometry is still finite.  First record the
exact two-copy rotation minima at the first image:

\[
\begin{array}{c|c|c}
\text{source}&
\min\|srsr^{-1}\|&
\min\{\|srs^{-1}r^{-1}\|:\text{nontrivial}\}\\ \hline
a&18&16\\
b&20&26
\end{array}
\tag{14.1}
\]

The minima range over every ambient r.  They follow from the same cyclic
rotation audit as Section 8; the opposite-sign column excludes the exact
zero obtained when the two conjugates coincide inversely.

### Lemma 14.1 (three-axis cancellation)

Let \(u_1,u_2,u_3\) be hyperbolic isometries of a tree, with translation
lengths \(\ell_i\) and finite pairwise axis-intersection diameters
\(d_{ij}\).  If

\[
\ell_i>d_{ij}+d_{ik}
\qquad(\{i,j,k\}=\{1,2,3\}),
\]

then

\[
\|u_1u_2u_3\|
\ge \sum_i\ell_i-2\sum_{i<j}d_{ij}.
\]

**Proof.**  Mark one translation segment on each axis in cyclic product
order.  At either end of the i-th segment, cancellation can use only the
part lying in the intersection with the adjacent factor's axis, of length
at most \(d_{ij}\) or \(d_{ik}\).  The strict inequality leaves a
nonempty central part of every segment, so no factor disappears and
exposes a new seam.  Removing the two bounded end portions from every
segment gives the estimate. \(\square\)

Now suppose the first AC2 multiplication uses an external conjugator.
After absorbing intervening AC1 and AC3 moves into signs and conjugators,
the row tested after the second AC2 multiplication is a cyclic product of
three source conjugates.  Its type is either

\[
(a,b,b)
\quad\text{or}\quad
(a,a,b),
\tag{14.2}
\]

with arbitrary signs and cyclic order.  Associate to the three factors
the three translates of K containing their axes.  The first external edge
ensures that not all three translates coincide.

If all three translates are distinct, Result 123 bounds every pairwise
axis overlap by two.  Since the shortest factor has length 11, no factor
can disappear through its two seams, and Lemma 14.1 gives

\[
\|(a,b,b)\text{-product}\|\ge11+18+18-12=35,
\tag{14.3}
\]

and

\[
\|(a,a,b)\text{-product}\|\ge11+11+18-12=28.
\tag{14.4}
\]

If exactly two translates coincide, combine that adjacent pair after a
cyclic rotation.  A mixed a--b pair has length at least 21 by Result 122.
The remaining external factor then leaves length at least 35 in type
\((a,b,b)\), or 28 in type \((a,a,b)\).  For an equal-source pair, (14.1)
applies.  A nontrivial b--b pair leaves length at least

\[
20+11-4=27,
\tag{14.5}
\]

and a nontrivial a--a pair leaves length at least

\[
16+18-4=30.
\tag{14.6}
\]

If an opposite-sign equal-source pair cancels completely, the terminal is
only a conjugate of the remaining old source, hence is nonprimitive.

The largest primitive length allowed by abelianization is 11 for type
\((a,b,b)\), and 16 for type \((a,a,b)\).  Thus every nontrivial bound
(14.3)--(14.6) is strictly too large.

It remains to include histories whose first AC2 edge is internal.  Its
changed row has length at least 21 by Result 122.  If the second edge is
external, Result 123 gives terminal length at least

\[
21+11-4=28,
\tag{14.7}
\]

regardless of which row is targeted.  If the second edge is internal, the
effective relative geometry of both AC2 edges lies in one K-translate.
After absorbing AC1/AC3, each terminal conjugacy class is then a conjugate
or inverse of \(\phi(V)\) for a pulled-back history on the original AK
pair, by Theorem 11.1.

The row not targeted by the second AC2 move is also closed.  If both AC2
moves target the same row, the other row is an old nonprimitive source.
If the targets alternate, the other row is the one-AC2 row, nonprimitive
by Section 8.  The zero- and one-AC2 cases are respectively the old
sources and Result 122.

### Theorem 14.2 (two-AC2 corridor barrier)

Starting from the first proper image pair \((a,b)\), no history with at
most two AC2 row multiplications creates an ambient-primitive row unless
after absorbing AC1/AC3, all effective relative factor geometry lies in
one K-translate.  In that case every terminal conjugacy class is a
conjugate or inverse of the image of a terminal from an original-AK
history.  This allows arbitrary AC1 inversions and AC3 conjugations
between the two AC2 moves.

Thus the proper corridor supplies no new primitive row at two-AC2 depth.
A genuinely new use must have at least three row multiplications, move K
by an ambient automorphism, or change the stabilizer architecture.

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.

## References

1. A. A. Klyachko, *A funny property of a sphere and equations over
   groups*, Comm. Algebra **21** (1993), 2555--2575.
