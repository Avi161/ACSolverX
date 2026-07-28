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

## 14. The cascade counterexample is a universal row-braid self-loop

The failure of a three-axis length estimate comes from an exact group
identity.  For arbitrary elements u,v of any group, the following legal
AC1--AC3 sequence uses exactly two AC2 moves:

\[
\begin{aligned}
(u,v)
&\longmapsto(u^{-1},v)
\longmapsto(u^{-1}v,v)
\longmapsto(vu^{-1},v)\\
&\longmapsto(uv^{-1},v)
\longmapsto(uv^{-1},uvu^{-1})\\
&\longmapsto(uv^{-1}uvu^{-1},uvu^{-1})\\
&\longmapsto(v^{-1}uv,uvu^{-1}).
\end{aligned}
\tag{14.1}
\]

The last step conjugates the first row by \(u^{-1}\), using

\[
u^{-1}(uv^{-1}uvu^{-1})u=v^{-1}uv.
\tag{14.2}
\]

Thus

\[
\boxed{
(u,v)\sim_{\mathrm{AC}}
(v^{-1}uv,\;uvu^{-1}).}
\tag{14.3}
\]

Both terminal rows are conjugates of their respective source rows.
Consequently (14.3) preserves the primitivity status of each displayed
row and can never expose a primitive row from the AK sources or any of
their image pairs.

There is nevertheless a genuinely proper formal map behind the loop.  On
the free row-symbol group \(F(U,V)\), define

\[
\Theta(U)=V^{-1}UV,
\qquad
\Theta(V)=UVU^{-1}.
\tag{14.4}
\]

Its abelianization is the identity.  The two images do not commute, so
they generate a rank-two free subgroup and \(\Theta\) is injective.  But

\[
\|\Theta([U,V])\|=12,
\qquad
\|[U,V]\|=4.
\tag{14.5}
\]

An automorphism of \(F_2\) sends the commutator to a conjugate of
\([U,V]^{\pm1}\), so (14.5) proves that \(\Theta\) is proper.

This distinction is essential.  The proper endomorphism acts on formal
row symbols, while its evaluation at a concrete pair merely conjugates
the two row values individually.  Iterating (14.3) gives an infinite
classical AC corridor but never changes either relator conjugacy class.
The audit counterexample to the false three-axis estimate is exactly one
instance of this row-braid corridor.

## 15. The row-braid corridor descends strictly

Let \(F_{\rm row}=F(U,V)\) and let \(\Theta\) be (14.4).  Since \(\Theta\)
is injective and proper,

\[
F_{\rm row}>
\Theta(F_{\rm row})>
\Theta^2(F_{\rm row})>\cdots
\tag{15.1}
\]

is a strictly descending chain.  Indeed, equality at depth n would pull
back through the isomorphism from \(F_{\rm row}\) onto
\(\Theta^n(F_{\rm row})\) and make \(\Theta\) surjective.

Now let u,v be any noncommuting elements of a free group.  Their subgroup
\(H=\langle u,v\rangle\) has rank two, so evaluation

\[
\operatorname{ev}_{u,v}:F_{\rm row}\longrightarrow H
\tag{15.2}
\]

is an isomorphism.  Applying it to (15.1) yields

\[
\langle u,v\rangle>
\langle\Theta(u),\Theta(v)\rangle>
\langle\Theta^2(u),\Theta^2(v)\rangle>\cdots.
\tag{15.3}
\]

Every pair in (15.3) is classically AC-equivalent to the preceding pair
by (14.3).  At the same time, induction in (14.4) shows

\[
\Theta^n(u)\sim u,
\qquad
\Theta^n(v)\sim v
\tag{15.4}
\]

for all n, where \(\sim\) denotes conjugacy.

The AK source rows are noncommuting because their exponent vectors have
determinant one.  Hence (15.3) gives a strict infinite classical corridor
for AK(3) and for every proper stable image constructed earlier.  It is
not a primitive compression: (15.4) fixes both relator conjugacy classes.
It proves instead that strict descent of the subgroup generated by the
displayed relators cannot serve as a progress invariant for
Andrews--Curtis dynamics.

## 16. Two multiplications cannot expose a primitive at the first image

Return to

\[
A=x^3y^{-4},\qquad B=xyxy^{-1}x^{-1}y^{-1}
\tag{16.1}
\]

and to the first proper image under
\(\phi(x)=x,\ \phi(y)=yxyx^{-1}y^{-1}\):

\[
a=\texttt{xxxyxYYYYXY},\qquad
b=\texttt{xyxyXYxyxYXYXyxYXY}.
\tag{16.2}
\]

Call a conjugate of \(A^{\pm1}\) or \(B^{\pm1}\), respectively of
\(a^{\pm1}\) or \(b^{\pm1}\), a source leaf.  AC1 reverses a row and
flips all its leaf signs, AC3 conjugates all its leaves together, and AC2
concatenates the leaf lists of two rows.  It follows by induction that
after at most two AC2 moves every row has at most three leaves.  A
three-leaf row has two leaves of one source and one of the other.  Up to
inverting the complete row, its signed multiset is one of exactly

\[
2A+B,\quad 2A-B,\quad A-A+B,\quad
A+2B,\quad A+B-B,\quad -A+2B.
\tag{16.3}
\]

The same list holds with \(A,B\) replaced by \(a,b\).  Their
abelianization vectors and the corresponding signed Christoffel
representatives are

\[
\begin{array}{c|c|c}
\text{case}&\text{vector}&P\\ \hline
2A+B&(7,-9)&\texttt{YYxYxYxYYxYxYxYx}\\
2A-B&(5,-7)&\texttt{YYxYxYYxYxYx}\\
A-A+B&(1,-1)&\texttt{Yx}\\
A+2B&(5,-6)&\texttt{YYxYxYxYxYx}\\
A+B-B&(3,-4)&\texttt{YYxYxYx}\\
-A+2B&(-1,2)&\texttt{yyX}
\end{array}
\tag{16.4}
\]

Osborne--Zieschang implies that if a three-leaf row in a case of
(16.4) were primitive, it would be conjugate to the displayed \(P\).
This can be excluded before choosing any of the relative conjugators.
Use \(1,2,3,4,5,32\) for the cycle types identity, transposition,
3-cycle, 4-cycle, 5-cycle, and a disjoint 3-cycle and 2-cycle.  The
following table gives homomorphisms to symmetric groups.  Each certificate
lists \((x,y)\), followed after the semicolon by the cycle types of its
two source images and \(P\).

\[
\begin{array}{c|c|c}
\text{case}&\text{original certificate}&\text{first-image certificate}\\ \hline
2A+B&S_4:(234),(12);(1,2,4)&S_4:(234),(12);(1,2,4)\\
2A-B&S_5:(345),(1234);(1,32,4)&S_5:(345),(1234);(1,2,4)\\
A-A+B&S_4:(234),(12);(1,2,4)&S_4:(234),(12);(1,2,4)\\
A+2B&S_5:(12345),(13542);(3,1,5)&S_5:(345),(1234);(1,2,5)\\
A+B-B&S_5:(345),(1235);(1,2,5)&S_5:(2345),(1254);(4,1,32)\\
-A+2B&S_4:(1234),(1243);(4,1,2)&S_4:(1234),(1243);(4,1,2)
\end{array}
\tag{16.5}
\]

Here a conjugated source leaf maps to an arbitrary element in the
corresponding permutation conjugacy class.  In the first three rows of
(16.5), all but one nontrivial factor vanish and its type differs from
the type of \(P\).  In the fourth row the original certificate leaves
one 3-cycle, while the image certificate leaves a product of two
transpositions; neither can be a 5-cycle.  In the fifth row the original
certificate again leaves a product of two transpositions, while the
image certificate leaves one 4-cycle; these cannot have types \(5\) and
\(32\), respectively.  The last row leaves a 4-cycle rather than a
transposition.  Thus no product of the required three conjugacy classes
can be conjugate to \(P\).

Rows with one leaf are nonprimitive.  For \(A\), the quotient
\(\langle x,y\mid x^3y^{-4}\rangle\) maps onto the nonabelian group
\(S_3\) by sending x to a 3-cycle and y to a transposition, whereas the
quotient by a primitive is infinite cyclic; \(B\) is excluded by its
cyclic length six and primitive vector length two.  Result 125 reflects
these obstructions to \(a,b\).  A two-leaf row contains one leaf of each
source and is nonprimitive by Results 116 and 124.

### Theorem 16.1 (depth-two closure)

No AC1--AC3 history starting at either \((A,B)\) or the first proper
image \((a,b)\), and containing at most two AC2 multiplications, reaches
a primitive row.  In particular the external-first branch left open in
Section 13 is closed.  Three or more multiplications, later stable
images, and other conjugating embeddings are not claimed closed.

## 17. Virtually free quotients close depth three at the AK source

After three AC2 moves, a row not already covered by Section 16 has four
or five source leaves.  The leaf recursion gives exactly eighteen new
signed multisets up to total inversion.  Write \((c_A,c_B)\) for their
signed coefficient pair.  They are

\[
\begin{array}{c|c}
\text{unsigned multiplicities}&(c_A,c_B)\\ \hline
(3,1)&(-3,-1),(-3,1),(-1,-1),(-1,1)\\
(1,3)&(-1,-3),(-1,-1),(-1,1),(-1,3)\\
(3,2)&(-3,-2),(-3,2),(-1,-2),(-1,0),(-1,2)\\
(2,3)&(-2,-3),(-2,-1),(-2,1),(-2,3),(0,-1).
\end{array}
\tag{17.1}
\]

Every vector

\[
(p,q)=(3c_A+c_B,-4c_A-c_B)
\tag{17.2}
\]

in (17.1) is primitive.  Hence a primitive terminal would be conjugate
to the signed Christoffel word \(P_{p,q}\).

Two infinite quotients retain the minority leaves.  First,

\[
Q_A=\langle X,Y\mid X^3,Y^4\rangle=C_3*C_4,
\qquad x\mapsto X,\quad y\mapsto Y.
\tag{17.3}
\]

It kills A, while

\[
\overline B=XYXY^3X^2Y^3
\tag{17.4}
\]

is cyclically reduced of syllable length six.  Second,

\[
Q_B=\langle s,t\mid s^2,t^3\rangle=C_2*C_3,
\qquad x\mapsto t^2s,\quad y\mapsto st^2.
\tag{17.5}
\]

Both \(xyx\) and \(yxy\) map to s, so (17.5) kills B.  The image

\[
\overline A=(t^2s)^3(ts)^4
\tag{17.6}
\]

is cyclically reduced of syllable length fourteen.

### Lemma 17.1 (finite connector normal form)

Let \(G=G_0*G_1\), and let \(u,v,p\) be cyclically reduced hyperbolic
elements.  If p is conjugate to a product of a conjugate of u and a
conjugate of v, then it is conjugate to

\[
u_0 c v_0c^{-1},
\tag{17.7}
\]

where \(u_0,v_0\) are cyclic syllable rotations of \(u,v\).  If the two
axes intersect, c may be chosen with syllable length at most one.  If
they are disjoint at vertex distance D in the Bass--Serre tree, c may be
chosen with syllable length at most \(D+1\), and

\[
\|p\|_{\rm syl}
=\|u\|_{\rm syl}+\|v\|_{\rm syl}+2D.
\tag{17.8}
\]

#### Proof

Use the line graph of the Bass--Serre tree and a base edge e.  A reduced
group word c has syllable length \(d(e,ce)\), and the axis of a
cyclically reduced hyperbolic word passes through e.  Edges on that axis
are reached by powers followed by syllable prefixes; changing the base
edge to one of them cyclically rotates the word.

For arbitrary conjugates of u and v, choose closest edges on their
axes and conjugate the whole product so that the first chosen edge is
e.  If the axes share an edge, the connector is trivial.  If they meet
only at a vertex, incident chosen edges differ by one syllable.  If they
are disjoint, closest vertices at distance D have incident axis edges
at line-graph distance \(D+1\).  This proves the connector bounds.
The usual disjoint-axis product formula in a tree gives (17.8).
There is no hidden vertex-group twist because edge stabilizers are
trivial; a vertex twist is exactly the one-syllable connector already
allowed.  \(\square\)

For the four-leaf cases, kill the majority source.  The candidate
syllable lengths are

\[
\begin{array}{c|c|c|c}
\text{multiplicities}&\text{quotient}&
\|\text{minority}\|_{\rm syl}&\|P_{p,q}\|_{\rm syl}\\ \hline
(3,1)&Q_A&6&20,16,8,4\\
(1,3)&Q_B&14&26,18,10,2.
\end{array}
\tag{17.9}
\]

Conjugacy preserves cyclic syllable length, so all eight cases are
impossible.

For five leaves, the majority again vanishes and exactly two signed
minority conjugates remain.  Lemma 17.1 makes the check finite:

\[
\begin{array}{c|c|c|c}
(c_A,c_B)&Q&\|P_{p,q}\|_{\rm syl}&
\text{safe connector bound}\\ \hline
(-3,-2),(-3,2),(-1,-2),(-1,0),(-1,2)
&Q_A&22,14,10,6,2&7,3,2,2,2\\
(-2,-3),(-2,-1),(-2,1),(-2,3),(0,-1)
&Q_B&40,32,24,16,4&8,4,2,2,2.
\end{array}
\tag{17.10}
\]

The first row uses two signed copies of (17.4), the second two signed
copies of (17.6).  Exhausting all syllable rotations, all reduced
connectors through the displayed bounds, and then exact cyclic
reduction finds no conjugate of the corresponding \(P_{p,q}\) in any
of the ten cases.  This is a finite normal-form certificate, verified
independently in
\(\texttt{tests/stable_ac/test\_ak\_depth\_three\_free\_product\_barrier.py}\);
it is not an AC graph search.

### Theorem 17.2 (AK depth-three closure)

No AC1--AC3 history starting at the original AK pair and containing at
most three AC2 multiplications reaches a primitive row.  Rows with at
most three leaves are covered by Section 16, and (17.9)--(17.10) cover
all eighteen four- and five-leaf possibilities.  The first proper image
is still closed only through two multiplications; depth four at the
source also remains open.

## 18. One exact depth-three residue at the first image

The same quotients lift to the first image for a simpler reason than
surjectivity of \(\phi\).  The word

\[
\phi(y)=(yx)y(yx)^{-1}
\tag{18.1}
\]

is conjugate to y.  Thus \(Q_A\) kills
\(a=x^3\phi(y)^{-4}\).  Exact cyclic normal forms give

\[
\|\overline b\|_{Q_A}=18.
\tag{18.2}
\]

The quotient \(Q_B\) also kills b directly, and

\[
\|\overline a\|_{Q_B}=2.
\tag{18.3}
\]

Apply the eighteen provenance cases of (17.1).  The connector certificate
closes sixteen immediately.  In the four-leaf case
\((c_a,c_b)=(-1,3)\), both the signed minority and the Christoffel
candidate have \(Q_B\)-length two and are conjugate there.  A separate
\(S_5\) certificate closes it: under

\[
x\mapsto(12345),\qquad y\mapsto(12453),
\tag{18.4}
\]

a maps to a 3-cycle, b maps to the identity, and the candidate y maps
to a 5-cycle.  Hence the required product cannot be conjugate to the
candidate.

Exactly one provenance case remains:

\[
\text{unsigned multiplicities }(2,3),\qquad
(c_a,c_b)=(0,-1).
\tag{18.5}
\]

It can only come from alternating row targets.  For arbitrary source
rows u,v, every such history, up to row exchange, terminal inversion,
and terminal conjugacy, has the complete form

\[
\begin{aligned}
X&=u^\sigma h_0v^\tau h_0^{-1},\\
Y&=v^{-1}h_1Xh_1^{-1},\\
Z&=X^{-1}h_2Yh_2^{-1},
\end{aligned}
\qquad \sigma,\tau\in\{\pm1\},
\tag{18.6}
\]

with endpoint \(([Z],[Y])\).  Conversely every choice in (18.6) is
realized by a legal three-AC2 alternating history.  To derive it, write

\[
\begin{aligned}
P&=u^\alpha h_0v^\beta h_0^{-1},\\
Q&=v^\gamma h_1P^\delta h_1^{-1},\\
R&=P^\epsilon h_2Q^\zeta h_2^{-1}.
\end{aligned}
\]

The leaf vector of R is

\[
\bigl(\alpha(\epsilon+\zeta\delta),
\ \beta(\epsilon+\zeta\delta)+\zeta\gamma\bigr).
\tag{18.7}
\]

It equals \((0,-1)\) precisely when
\(\epsilon=-\zeta\delta\) and \(\gamma=-\zeta\).
Absorbing the resulting cyclic rotations and dependent conjugations
gives (18.6).  The dependence matters: the identical X occurs inside Y
and as \(X^{-1}\) in Z.

Now put \(u=a,\ v=b\).  Result 130 already excludes Y, which has at most
three leaves.  Since

\[
[Z]_{\rm ab}=-[b]_{\rm ab}=(-1,1),
\tag{18.8}
\]

Z is primitive exactly when it is conjugate to the signed Christoffel
word \(yx^{-1}\).  Therefore the whole first-image depth-three residue
is the single equation

\[
\boxed{
X^{-1}h_2
\bigl(b^{-1}h_1Xh_1^{-1}\bigr)
h_2^{-1}
=k(yx^{-1})k^{-1},
\quad
X=a^\sigma h_0b^\tau h_0^{-1}.}
\tag{18.9}
\]

All four variables \(h_0,h_1,h_2,k\) range over \(F(x,y)\), and both
signs are allowed.  In \(Q_B\), (18.9) becomes a product of a conjugate
of \(a^{-1}\) and a conjugate of a; that quotient genuinely admits the
candidate, so the virtually free argument cannot close (18.9).

### Theorem 18.1 (sharp first-image depth-three reduction)

Seventeen of the eighteen new depth-three provenance classes at the
first proper image cannot contain a primitive row.  The remaining class
contains a primitive row if and only if (18.9) has a solution.  No
solution or obstruction is asserted here.

## 19. Every nilpotent quotient erases the last residue

### Lemma 19.1 (braid collapse in nilpotent groups)

If elements r,s of a nilpotent group satisfy

\[
rsr=srs,
\tag{19.1}
\]

then \(r=s\).

#### Proof

Abelianizing (19.1) gives \(r=s\) modulo \(\gamma_2\).  Suppose
\(d=rs^{-1}\in\gamma_n\).  Modulo \(\gamma_{n+1}\), d is central and
\(r=ds\).  Substitution in (19.1) gives

\[
d^2s^3=ds^3,
\]

so \(d\in\gamma_{n+1}\).  Induction puts d in every term of the lower
central series.  A nilpotent group has some
\(\gamma_{c+1}=1\), hence \(d=1\).  \(\square\)

Now let N be any nilpotent quotient of

\[
G_b=F(x,y)/\langle\!\langle b\rangle\!\rangle.
\tag{19.2}
\]

Put

\[
u=\phi(y)=(yx)y(yx)^{-1},\qquad g=yx.
\tag{19.3}
\]

The relation \(b=B(x,u)=1\) is exactly

\[
xux=uxu.
\tag{19.4}
\]

Lemma 19.1 gives \(x=u\) in N.  Since \(u=gyg^{-1}\),

\[
y=g^{-1}xg.
\tag{19.5}
\]

Moreover

\[
a=x^3u^{-4}=x^{-1}.
\tag{19.6}
\]

The primitive candidate in (18.9) therefore satisfies

\[
\begin{aligned}
yx^{-1}
&=g^{-1}xgx^{-1}\\
&=g^{-1}\bigl(a^{-1}gag^{-1}\bigr)g.
\end{aligned}
\tag{19.7}
\]

Thus it is conjugate to a product of a conjugate of \(a^{-1}\) and a
conjugate of a in every nilpotent quotient of \(G_b\).

### Theorem 19.2 (nilpotent blindness)

No nilpotent quotient of \(G_b\), of any class or exponent, can obstruct
the projected form of (18.9).  The quotient does not merely fail to
separate the two sides: (19.7) supplies a solution uniformly.  Any
successful obstruction must retain non-nilpotent information in the
braid subgroup.

## 20. The last residue is a free-group twisted equation

Send both x and y to \(1\in\mathbb Z\), put \(t=x\), and define

\[
z_i=t^iyt^{-(i+1)}.
\tag{20.1}
\]

Then \(tz_it^{-1}=z_{i+1}\), and Magnus rewriting gives

\[
b=
z_1z_3z_2^{-1}z_3z_4^{-1}
z_2^{-1}z_1z_2^{-1}z_0^{-1}.
\tag{20.2}
\]

The bottom and top letters occur once.  Solving (20.2) for \(z_4\)
defines

\[
\begin{aligned}
\Phi(z_0)&=z_1,\\
\Phi(z_1)&=z_2,\\
\Phi(z_2)&=z_3,\\
\Phi(z_3)&=
z_2^{-1}z_1z_2^{-1}z_0^{-1}
z_1z_3z_2^{-1}z_3.
\end{aligned}
\tag{20.3}
\]

This endomorphism of \(F_4=F(z_0,z_1,z_2,z_3)\) is an automorphism.  An
explicit inverse is

\[
\begin{aligned}
\Phi^{-1}(z_0)&=
z_0z_2z_1^{-1}z_2z_3^{-1}z_1^{-1}z_0z_1^{-1},\\
\Phi^{-1}(z_1)&=z_0,\qquad
\Phi^{-1}(z_2)=z_1,\qquad
\Phi^{-1}(z_3)=z_2.
\end{aligned}
\tag{20.4}
\]

Direct free reduction verifies both compositions.  Tietze elimination
of all other \(z_i\) therefore gives

\[
\boxed{
G_b\cong F_4\rtimes_\Phi\langle t\rangle.}
\tag{20.5}
\]

The candidate is especially simple:

\[
yx^{-1}=z_0.
\tag{20.6}
\]

The other fixed entry rewrites as

\[
a=q\,t^{-1},
\tag{20.7}
\]

where

\[
\begin{aligned}
q={}&
z_2z_3^{-1}z_1^{-1}z_0z_2z_1^{-1}z_2z_3^{-1}\\
&{}\cdot
z_2^{-1}z_0^{-1}z_1z_3z_2^{-1}z_1z_2^{-1}z_0^{-1}.
\end{aligned}
\tag{20.8}
\]

Write an arbitrary element of the mapping torus as \(w t^n\), with
\(w\in F_4\).  The fixed-entry commutator from (19.7) has kernel
coordinate

\[
C(w,n)=
\Phi(q^{-1})\,
\Phi(w)\,
\Phi^{n+1}(q)\,
w^{-1}.
\tag{20.9}
\]

Two kernel elements are conjugate in the mapping torus precisely when
one is conjugate in \(F_4\) to a \(\Phi\)-iterate of the other.
Consequently the projected residue from (18.9) is exactly

\[
\boxed{
C(w,n)\sim_{F_4}\Phi^j(z_0^\eta)
\quad\text{for some }w\in F_4,\ n,j\in\mathbb Z,
\eta\in\{\pm1\}.}
\tag{20.10}
\]

The sign records whether X in (18.6) is conjugate to a or to
\(a^{-1}\): replacing the fixed entry by its inverse turns the
commutator into a conjugate of the inverse orientation.

This is a twisted conjugacy equation in a rank-four free group, with no
remaining arbitrary one-relator quotient.

The abelianized monodromy, with columns corresponding to
\((z_0,z_1,z_2,z_3)\), is

\[
M=
\begin{pmatrix}
0&0&0&-1\\
1&0&0&2\\
0&1&0&-3\\
0&0&1&2
\end{pmatrix}.
\tag{20.11}
\]

It satisfies

\[
\det(M-I)=1,
\qquad
\det(\lambda I-M)=(\lambda^2-\lambda+1)^2.
\tag{20.12}
\]

Abelianizing (20.10) gives

\[
(M-I)\overline w
+(M^{n+1}-M)\overline q
=\eta M^j e_0.
\tag{20.13}
\]

Since \(M-I\) is unimodular, (20.13) has an integral solution
\(\overline w\) for every n, j, and \(\eta\).  Thus the ordinary
Alexander module cannot obstruct the residue.

Even the full braid quotient is blind.  Map \(G_b\) to
\(B_3=\langle \sigma_1,\sigma_2\mid
\sigma_1\sigma_2\sigma_1=\sigma_2\sigma_1\sigma_2\rangle\) by
\(x\mapsto\sigma_1,\ y\mapsto\sigma_2\).  Then
\(\phi(y)\mapsto\sigma_1\), so b dies and \(a\mapsto\sigma_1^{-1}\).
For \(\Delta=\sigma_1\sigma_2\sigma_1\), conjugation by \(\Delta\)
swaps the two braid generators.  Hence

\[
\begin{aligned}
a^{-1}\Delta a\Delta^{-1}&=\sigma_1\sigma_2^{-1},\\
\Delta(\sigma_1\sigma_2^{-1})\Delta^{-1}
&=\sigma_2\sigma_1^{-1}.
\end{aligned}
\tag{20.14}
\]

The last word is the image of \(yx^{-1}\).

### Theorem 20.1 (exact free-by-cyclic reduction)

The projected first-image depth-three residue is equivalent to the
rank-four free-group equation (20.10).  Its abelianization and the
natural full braid quotient both admit solutions.  Any closure must use
nonabelian information in the free kernel together with the explicit
monodromy \(\Phi\).

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.

## References

1. A. A. Klyachko, *A funny property of a sphere and equations over
   groups*, Comm. Algebra **21** (1993), 2555--2575.
2. R. P. Osborne and H. Zieschang, *Primitives in the free group on two
   generators*, Invent. Math. **63** (1981), 17--24.
