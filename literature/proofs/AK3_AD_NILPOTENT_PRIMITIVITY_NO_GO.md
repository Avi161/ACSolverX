# AK(3) A--D nilpotent primitivity no-go

## Statement

Let

\[
F=F(x,t,z,q),
\qquad
A=qx^3q^{-1}t^{-4},
\qquad
D=t^{-1}zxz^{-1},
\]

and, for arbitrary \(c\in F\) and \(\sigma\in\{+1,-1\}\), put

\[
P_\sigma(c)=A\,cD^\sigma c^{-1}.
\tag{1}
\]

For every \(s\geq1\), the image of \(P_\sigma(c)\) in the free
nilpotent quotient

\[
N_{4,s}=F/\gamma_{s+1}F
\tag{2}
\]

is primitive.  Thus no obstruction whose criterion is failure of the
word image to be primitive in one finite lower-central quotient can
exclude an A--D product.

The reason is general.

**Nilpotent primitivity lemma.**  If \(w\in F_n\) has primitive
integral abelianization, then its image is primitive in
\(F_n/\gamma_{s+1}F_n\) for every \(s\geq1\).

## 1. The A--D abelianizations

Conjugation does not affect abelianization, so (1) gives

\[
\operatorname{ab}(P_\sigma(c))
=\operatorname{ab}(A)+\sigma\operatorname{ab}(D).
\]

In the coordinate order \((x,t,z,q)\),

\[
\operatorname{ab}(A)=(3,-4,0,0),
\qquad
\operatorname{ab}(D)=(1,-1,0,0).
\]

Consequently

\[
\operatorname{ab}(P_+(c))=(4,-5,0,0),
\qquad
\operatorname{ab}(P_-(c))=(2,-3,0,0).
\tag{3}
\]

Both vectors are primitive over \(\mathbb Z\), independently of
\(c\).

## 2. Primitive abelianization implies nilpotent primitivity

Let \(w\in F_n\) have primitive abelianization and put
\(N=F_n/\gamma_{s+1}F_n\).  Complete the exponent vector of \(w\) to
a basis of \(\mathbb Z^n\).  Nielsen surjectivity

\[
\operatorname{Aut}(F_n)\longrightarrow\operatorname{GL}_n(\mathbb Z)
\]

provides a free basis \(a_1,\ldots,a_n\) whose first member has the
same abelianization as \(w\).  Use the same notation for their images
in \(N\).

By the relative freeness of \(N\), the assignments

\[
\phi(a_1)=w,
\qquad
\phi(a_i)=a_i\quad(2\leq i\leq n)
\tag{4}
\]

define an endomorphism \(\phi:N\to N\).  It induces the identity on
\(N_{\mathrm{ab}}\).  Let \(H=\phi(N)\).  Then

\[
H\gamma_2N=N.
\tag{5}
\]

We claim that (5) forces \(H=N\).  Modulo
\(\gamma_{j+1}N\), every weight-\(j\) commutator is unchanged if each
of its entries is replaced by an \(H\)-representative modulo
\(\gamma_2N\): inserting one error from \(\gamma_2N\) raises the
weight to at least \(j+1\).  Hence

\[
\gamma_jN\subseteq H\gamma_{j+1}N
\qquad(j\geq2).
\tag{6}
\]

Starting with (5) and applying (6) gives

\[
N=H\gamma_2N=H\gamma_3N=\cdots
=H\gamma_{s+1}N=H.
\]

Thus \(\phi\) is surjective.  Finitely generated nilpotent groups are
Hopfian, so \(\phi\) is an automorphism.  Equation (4) shows that
\(w=\phi(a_1)\) is primitive in \(N\).  This proves the lemma.

Combining the lemma with (3) proves the theorem for every \(c\) and
both signs.

## 3. Magnus and finite-\(p\) consequences

The integral Magnus expansion modulo terms of degree \(s+1\) factors
through \(F_n/\gamma_{s+1}F_n\).  Therefore a truncated-Magnus
criterion which obstructs a word only when its nilpotent image is
nonprimitive cannot exclude \(P_\sigma(c)\).  In particular, the
plain degree-two quotient-primitivity test, and the analogous test in
every fixed finite lower-central Magnus truncation, are blind to the
whole A--D family.  A finer invariant of the orbit under only those
nilpotent automorphisms induced from \(\operatorname{Aut}(F_n)\) is
not ruled out here.

The same conclusion holds in the standard finite free
lower-\(p\)-central quotients \(F_n/P_kF_n\) and Zassenhaus quotients
\(F_n/D_kF_n\).  For either finite free \(p\)-group \(G\),

\[
G/\Phi(G)\cong\mathbb F_p^n.
\]

The vectors in (3) are nonzero modulo every prime \(p\).  Complete
either vector to a basis over \(\mathbb F_p\) and define the analogue
of (4) in \(G\).  The resulting endomorphism is invertible on the
Frattini quotient.  Burnside's basis theorem makes it surjective, and
finiteness makes it an automorphism.  Thus these standard finite
\(p\)-truncations are blind as well.

This argument does **not** rule out second Fox or Jacobian constraints
which retain lift data rather than only the truncated image of the
word.  Such data need not factor through (2).

## 4. Check on a flow-collapse family

The no-go applies nonvacuously to the internal residue.  Use the
quotient map

\[
\rho(x)=x,\qquad
\rho(t)=zxz^{-1},\qquad
\rho(z)=z,\qquad
\rho(q)=zy,
\]

and let \(\pi:F\to F(q,z)\) kill \(x,t\).  Put

\[
b_0=y^{-1}xy,
\qquad
c_0=zq^{-1}zxz^{-1}qz^{-1}.
\]

Then

\[
\rho(c_0)=zy^{-1}xyz^{-1}=zb_0z^{-1},
\qquad
\pi(c_0)=1.
\]

Thus \(P_-(c_0)\) lies in the negative identity-projection internal
fiber, and its \(b_0\) is the \(r=1,\ell=0\) negative--positive
length-two flow-collapse case of Section 13 in
AK3_AD_INTERNAL_BS34_FLOW_MODULE.md.

Nevertheless (3) gives

\[
\operatorname{ab}(P_-(c_0))=(2,-3,0,0).
\]

For an explicit comparison basis in \(F(x,t)\), put

\[
a_1=(xt^{-1})^2t^{-1},
\qquad
a_2=xt^{-1}.
\]

Starting from the basis \((xt^{-1},t)\), swap, invert the first
member, and multiply it twice on the left by the second; this proves
that \((a_1,a_2)\) is a free basis.  Its first exponent vector is
\((2,-3)\).  In every \(N_{4,s}\),
\(P_-(c_0)a_1^{-1}\in\gamma_2N_{4,s}\), so the automorphism (4)
exhibits the image of this concrete flow-collapse word as primitive.

This is a no-go theorem for quotient-primitivity tests in nilpotent
and ordinary truncated-Magnus targets, not a primitivity theorem in
the original free group and not an Andrews--Curtis reduction.
