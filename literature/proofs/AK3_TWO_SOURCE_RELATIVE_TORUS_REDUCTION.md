# Two-source primitive targets and relative torus extensions

Date: 2026-07-27

Status: **PROVEN REDUCTION**.  A hypothetical genuine two-source primitive
target forces two simultaneous proper unimodular relative extensions of the
\((3,4)\)- and \((2,3)\)-torus-knot groups.  Their exclusion is not proved.

Let

\[
F=F_0*\langle r\rangle,
\qquad
F_0=F(x,y),
\tag{0.1}
\]

and put

\[
A=x^3y^{-4},
\qquad
B=xyxy^{-1}x^{-1}y^{-1}.
\tag{0.2}
\]

The normalized two-source target is

\[
W=r\,cA^\epsilon c^{-1}dB^\eta d^{-1},
\qquad
c,d\in F,
\qquad
\epsilon,\eta=\pm1.
\tag{0.3}
\]

Write \(\lambda(W)\) for the free-product syllable length of a cyclically
reduced conjugate of \(W\) in \(F_0*\langle r\rangle\).

## 1. Primitive quotient and old-factor embedding

Assume that \(W\) is primitive.  Let

\[
q:F\longrightarrow
Q=F/\langle\!\langle W\rangle\!\rangle\cong F_2,
\tag{1.1}
\]

and write

\[
K=q(F_0),
\qquad
a=q(A),
\qquad
b=q(B),
\qquad
s=q(r).
\tag{1.2}
\]

The \(r\)-exponent sum of \(W\) is one.  A cyclically reduced conjugate
therefore contains \(r\), so Freiheitssatz gives

\[
K\cong F_0.
\tag{1.3}
\]

The same exponent-one relation expresses \([r]\) in terms of \([x],[y]\),
and inclusion induces

\[
H_1(K;\mathbb Z)\xrightarrow{\ \cong\ }H_1(Q;\mathbb Z).
\tag{1.4}
\]

## 2. The two AK elements normally generate \(Q\)

For completeness, the AK pair normally generates \(F_0\).  In the quotient
by \(A,B\), the B-relation is the braid relation

\[
xyx=yxy.
\tag{2.1}
\]

With \(\Delta=xyx\), conjugation by \(\Delta\) interchanges \(x\) and
\(y\).  Conjugating \(x^3=y^4\) therefore gives \(y^3=x^4\).  Then

\[
y^3=x^4=x(x^3)=xy^4,
\tag{2.2}
\]

so \(x=y^{-1}\).  Equation (2.1) gives \(y^{-1}=y\), hence \(y^2=1\),
while \(x^3=y^4\) gives \(y^7=1\).  Thus \(x=y=1\), proving

\[
\langle\!\langle a,b\rangle\!\rangle_K=K.
\tag{2.3}
\]

Taking the inverse of the two-source part of (0.3) in the defining
relation expresses

\[
s=q(d)b^{-\eta}q(d)^{-1}
  q(c)a^{-\epsilon}q(c)^{-1}.
\tag{2.4}
\]

Thus \(s\in\langle\!\langle a,b\rangle\!\rangle_Q\).  Since
\(Q=\langle K,s\rangle\), (2.3) gives

\[
\boxed{
\langle\!\langle a,b\rangle\!\rangle_Q=Q.
}
\tag{2.5}
\]

This does not say that either element alone normally supplements \(K\).
The separate quotients give stronger information.

## 3. Killing the A-source

Put

\[
G_A=F_0/\langle\!\langle A\rangle\!\rangle
\cong G_{3,4}.
\tag{3.1}
\]

Let

\[
\rho_A:F\longrightarrow G_A*\langle r\rangle
\tag{3.2}
\]

kill \(A\) and fix \(r\), and write

\[
d_A=\rho_A(d),
\qquad
B_A=\rho_A(B).
\tag{3.3}
\]

These definitions allow arbitrary occurrences of \(r^{\pm1}\) in \(d\).
Killing \(a\) in (1.1) gives the exact relative presentation

\[
\boxed{
P_A:=Q/\langle\!\langle a\rangle\!\rangle_Q
\cong
\frac{G_A*\langle r\rangle}
{\langle\!\langle r\,d_AB_A^\eta d_A^{-1}
\rangle\!\rangle}.
}
\tag{3.4}
\]

The relative relator has r-exponent sum one.  The group \(G_A\) is
torsion-free.  Klyachko's theorem on unimodular equations over torsion-free
groups therefore injects the coefficient group:

\[
\boxed{G_A\hookrightarrow P_A.}
\tag{3.5}
\]

Equivalently, restricting the quotient map to \(K\) gives

\[
\boxed{
K\cap\langle\!\langle a\rangle\!\rangle_Q
=
\langle\!\langle a\rangle\!\rangle_K.
}
\tag{3.6}
\]

The coefficient inclusion is an isomorphism on first homology.  This
follows by quotienting the common isomorphism (1.4) by the primitive vector
\([A]=(3,-4)\).

The other source normally generates this entire extension.  Indeed,
\(B_A\) normally generates \(G_A\), because killing it gives the trivial
AK quotient.  Relation (3.4) also gives

\[
r=d_AB_A^{-\eta}d_A^{-1}.
\tag{3.7}
\]

Hence

\[
\boxed{P_A=\langle\!\langle B_A\rangle\!\rangle_{P_A}.}
\tag{3.8}
\]

## 4. Killing the B-source

Similarly, put

\[
G_B=F_0/\langle\!\langle B\rangle\!\rangle
\cong G_{2,3},
\tag{4.1}
\]

and let

\[
\rho_B:F\longrightarrow G_B*\langle r\rangle,
\qquad
c_B=\rho_B(c),
\qquad
A_B=\rho_B(A).
\tag{4.2}
\]

Then

\[
\boxed{
P_B:=Q/\langle\!\langle b\rangle\!\rangle_Q
\cong
\frac{G_B*\langle r\rangle}
{\langle\!\langle r\,c_BA_B^\epsilon c_B^{-1}
\rangle\!\rangle}.
}
\tag{4.3}
\]

Klyachko again gives

\[
\boxed{G_B\hookrightarrow P_B,}
\tag{4.4}
\]

and therefore

\[
\boxed{
K\cap\langle\!\langle b\rangle\!\rangle_Q
=
\langle\!\langle b\rangle\!\rangle_K.
}
\tag{4.5}
\]

This coefficient inclusion is also an isomorphism on first homology.
Since \(A_B\) normally generates \(G_B\) and

\[
r=c_BA_B^{-\epsilon}c_B^{-1}
\tag{4.6}
\]

in \(P_B\),

\[
\boxed{P_B=\langle\!\langle A_B\rangle\!\rangle_{P_B}.}
\tag{4.7}
\]

There is also a useful primitivity consequence.  The vectors of \(a,b\)
in \(H_1(Q)\) are primitive by (1.4).  If \(a\) were simple in the
rank-two free group \(Q\), it would therefore be primitive, making
\(P_A\cong\mathbb Z\).  This contradicts the embedded nonabelian group
\(G_A\).  Thus \(a\) is non-simple in \(Q\), and the same argument with
\(G_B\) shows that \(b\) is non-simple in \(Q\).

## 5. Surjective coefficient inclusion collapses the primitive quotient

Suppose first that \(G_A\hookrightarrow P_A\) is onto.  Then inclusion
induces

\[
K/\langle\!\langle a\rangle\!\rangle_K
\xrightarrow{\ \cong\ }
Q/\langle\!\langle a\rangle\!\rangle_Q.
\tag{5.1}
\]

The Collins--Zieschang classification gives a single Nielsen class of
two-generator one-relator presentations of \(G_{3,4}\).  Aligning the
domain and target relators turns \(K\hookrightarrow Q\) into an injective
endomorphism of \(F_2\) taking the standard \((3,4)\)-torus relator to
itself or its inverse.  Turner, applied directly or to the square, makes
that endomorphism an automorphism.  Hence

\[
G_A\twoheadrightarrow P_A
\quad\Longrightarrow\quad
K=Q.
\tag{5.2}
\]

The same argument using the single Nielsen class for \(G_{2,3}\) gives

\[
G_B\twoheadrightarrow P_B
\quad\Longrightarrow\quad
K=Q.
\tag{5.3}
\]

In fact, the weaker abstract hypotheses \(P_A\cong G_{3,4}\) or
\(P_B\cong G_{2,3}\) already align the relators and imply \(K=Q\).

## 6. The genuine two-source consequence

If \(K=Q\), identify \(Q\) with \(F_0\) through \(q|_{F_0}\).  The
quotient map fixes \(F_0\) and sends \(r\) to some \(u\in F_0\).  Its
kernel is both

\[
\langle\!\langle W\rangle\!\rangle_F
\quad\text{and}\quad
\langle\!\langle ru^{-1}\rangle\!\rangle_F.
\tag{6.1}
\]

Magnus's normal-closure theorem makes \(W\) conjugate to
\((ru^{-1})^{\pm1}\).  Therefore

\[
K=Q\quad\Longrightarrow\quad\lambda(W)\le2.
\tag{6.2}
\]

Combining Sections 3--6 proves the main reduction.

### Theorem 6.1

If the two-source word (0.3) is primitive and \(\lambda(W)>2\), then

\[
\boxed{
K<Q,
\qquad
G_{3,4}\lneq P_A,
\qquad
G_{2,3}\lneq P_B.
}
\tag{6.3}
\]

Both coefficient inclusions in (6.3) induce isomorphisms on first
homology.  Moreover, \(B_A\) normally generates \(P_A\), and \(A_B\)
normally generates \(P_B\).

Thus a genuine primitive target forces two simultaneous proper relative
extensions, not merely one exceptional one-relator presentation.

## 7. The combined relator and its marked mismatch

There is a second exact reduction which explains why Theorem 2.1 from the
one-source note does not immediately finish (0.3).  Put

\[
t=c^{-1}d,
\qquad
Z=A^\epsilon tB^\eta t^{-1},
\tag{7.1}
\]

so that

\[
W=r\,cZc^{-1}.
\tag{7.2}
\]

Let \(p:F\to F_0\) kill \(r\), and define

\[
t_0=p(t),
\qquad
Z_0=p(Z)=A^\epsilon t_0B^\eta t_0^{-1}.
\tag{7.3}
\]

In \(Q\), write

\[
z=q(Z),
\qquad
z_0=q(Z_0)\in K,
\qquad
N=\langle\!\langle z\rangle\!\rangle_Q.
\tag{7.4}
\]

Relation (7.2) gives \(q(r)\in N\), so

\[
Q=KN.
\tag{7.5}
\]

Also,

\[
\langle\!\langle W,Z\rangle\!\rangle_F
=
\langle\!\langle r,Z\rangle\!\rangle_F.
\tag{7.6}
\]

It follows that

\[
\boxed{
Q/N\cong F_0/\langle\!\langle Z_0\rangle\!\rangle
}
\tag{7.7}
\]

and

\[
\boxed{
K\cap N=\langle\!\langle z_0\rangle\!\rangle_K.
}
\tag{7.8}
\]

The common abelianization vector of \(z\) and \(z_0\) is

\[
\epsilon(3,-4)+\eta(1,-1),
\tag{7.9}
\]

namely \(\pm(4,-5)\) for equal signs and \(\pm(2,-3)\) for opposite
signs.  It is primitive.

The decisive mismatch is

\[
\boxed{z\text{ need not equal }z_0.}
\tag{7.10}
\]

The relator normally killed in \(Q\) is \(z\), while the relator normally
killed in \(K\) is \(z_0\).  Although (7.7)--(7.8) give the same abstract
one-relator quotient, they do not turn inclusion into an endomorphism
fixing one common non-simple word.  Turner therefore does not apply.

If \(t=c^{-1}d\in F_0\), then \(Z=Z_0\).  In that special case, admissible
one-relator Nielsen rigidity of the non-simple source \(Z_0\) invokes the
general bridge theorem and forces \(K=Q\).  Result 116 proves
non-simplicity for every such \(Z_0\), but not its admissible rigidity.

## 8. Source order, multiplication side, and the length hypothesis

Every cyclic placement of the three factors \(r\),
\(cA^\epsilon c^{-1}\), and \(dB^\eta d^{-1}\) is conjugate to (0.3) or
to the version with A and B interchanged.  Inversion reverses the source
order and changes the signs; the automorphism \(r\mapsto r^{-1}\) restores
the preferred r-orientation.  These operations preserve primitivity and
\(\lambda(W)\).

The condition \(\lambda(W)>2\) is essential.  If \(c,d\in F_0\), then
\(W=rU\) for \(U\in F_0\), so \(W\) is primitive.  Even the two-location
spelling \(c=1,d=r\) gives

\[
W=rA^\epsilon rB^\eta r^{-1}
\sim A^\epsilon rB^\eta,
\tag{8.1}
\]

whose cyclic syllable length is two and which is primitive because it
contains \(r\) exactly once.  Two displayed conjugates or two distinct
source vertices are therefore insufficient substitutes for the exact
cyclic syllable condition.

## 9. Remaining theorem

A genuine two-source primitive target must realize both proper extensions

\[
G_{3,4}\lneq P_A,
\qquad
G_{2,3}\lneq P_B,
\tag{9.1}
\]

with identical first homology and with the other AK source normally
generating the whole extension.  Klyachko injectivity and normal generation
do not by themselves imply surjectivity: a relation making a new generator
conjugate to a normal generator can define a proper Wirtinger-type
extension.

The next proof must exclude the simultaneous configuration (9.1), align
the marked relators \(z_0,z\), or use additional geometry of the two
relative equations.  AK(3), stable Andrews--Curtis, and Andrews--Curtis
remain open.

## References

1. A. A. Klyachko, *A funny property of a sphere and equations over
   groups*, Comm. Algebra **21** (1993), 2555--2575.
2. R. Fenn and C. Rourke, *Klyachko's methods and the solution of equations
   over torsion-free groups*, Enseign. Math. **42** (1996), 49--74.
