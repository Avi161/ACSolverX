# Audit 2: the explicit commutator and the \(a\)-versus-\(r\) test

## Verdict

The explicit commutator is correct:

\[
z_0=yx^{-1}=[r,x]=r^{-1}xrx^{-1}
\qquad\text{in }G_b.
\]

However, \(a\) is neither conjugate nor inverse-conjugate to \(r\) in
\(H=G_b\).  A quotient onto \(S_4\) separates them: the image of \(a\) is a
4-cycle, whereas the image of \(r\) is a transposition.

Thus the proposed commutator does not solve the Result 134 residue by
transporting the \(r\)-entry to the fixed entry \(a\).

## 1. Direct verification of the commutator

Put

\[
g=yx,\qquad u=gyg^{-1},\qquad \Delta=xux,\qquad r=\Delta^{-1}g.
\]

The defining relator \(b\) is the braid relation

\[
xux=uxu.
\]

It implies the standard half-twist identity

\[
\Delta x\Delta^{-1}
=xux\,x\,x^{-1}u^{-1}x^{-1}
=xuxu^{-1}x^{-1}
=u.
\]

Since \(r^{-1}=g^{-1}\Delta\), it follows that

\[
\begin{aligned}
[r,x]
&=g^{-1}\Delta x\Delta^{-1}g x^{-1}\\
&=g^{-1}ugx^{-1}\\
&=yx^{-1}=z_0.
\end{aligned}
\]

This uses exactly the convention
\([v,w]=v^{-1}wvw^{-1}\) used in Result 134.

## 2. Correct mapping-torus coordinate and the index trap

Use normal forms \(ft^m\), with \(t=x\), \(y=z_0t\), and
\(tft^{-1}=\Phi(f)\).  Direct semidirect multiplication gives

\[
\begin{aligned}
g&=z_0t^2,\\
u&=(z_0z_2z_1^{-1})t,\\
\Delta&=(z_1z_3z_2^{-1})t^3,\\
r&=\Phi^{-3}(z_2z_3^{-1}z_1^{-1}z_0)t^{-1}.
\end{aligned}
\]

After applying the verified inverse monodromy three times and freely
reducing,

\[
r=r_0t^{-1},
\]

where, in generator numbering \(1=z_0,\ldots,4=z_3\),

\[
r_0=
(3,-4,-2,1,-2,-1,2,-1,2,4,-3,2,-3,-1).
\tag{1}
\]

Direct pair multiplication verifies

\[
[r_0t^{-1},t]=(z_0,0).
\]

The previously proposed short coordinate
\((-1,-1,2,-3)\) is wrong.  Its first raw Magnus index \(-1\) came from a
positive \(y\) at height \(-1\), hence represents \(z_{-1}\), not
\(z_0^{-1}\).  Eliminating \(z_{-1}\) through \(\Phi^{-1}\) is essential and
produces the longer word (1).

## 3. Exact twisted-conjugacy equation

Recall

\[
a=qt^{-1},
\]

with

\[
q=(3,-4,-2,1,3,-2,3,-4,-3,-1,2,4,-3,2,-3,-1).
\]

Let a possible conjugator be \(s=wt^n\).  The normal-form multiplication
rule gives

\[
sas^{-1}
=w\Phi^n(q)\Phi^{-1}(w^{-1})t^{-1}.
\]

Consequently

\[
\boxed{
a\sim_H r
\iff
\exists\,w\in F_4,\ n\in\mathbb Z:
\quad
r_0=w\Phi^n(q)\Phi^{-1}(w^{-1}).
}
\tag{2}
\]

This is a \(\Phi^{-1}\)-twisted-conjugacy problem, with the additional
\(\Phi\)-orbit parameter on \(q\).

Inverse-conjugacy is already impossible from the height homomorphism
\(H\to\mathbb Z\): \(a\) and \(r\) have height \(-1\), whereas \(r^{-1}\)
has height \(+1\).

## 4. An exact \(S_4\) obstruction

Compose permutations right-to-left and define

\[
X=(0\,1\,2\,3),\qquad
Y=(0\,1\,3\,2).
\]

Send \(x\mapsto X\), \(y\mapsto Y\).  If \(G=YX\), then direct permutation
multiplication gives

\[
U=GYG^{-1}=X.
\]

Therefore \(XUX=UXU\), so the assignment respects \(b\) and defines a
homomorphism

\[
\rho:G_b\longrightarrow S_4.
\]

In fact \(X,Y\) generate all of \(S_4\).  The relevant images are

\[
\begin{aligned}
\rho(\Delta)&=X^3=X^{-1},\\
\rho(a)&=(0\,3\,2\,1),\\
\rho(r)&=(2\,3),\\
\rho(z_0)&=(0\,2\,3).
\end{aligned}
\]

The commutator identity remains visible:

\[
[\rho(r),X]=\rho(z_0).
\]

But a 4-cycle cannot be conjugate to a transposition in \(S_4\).  Hence
\(\rho(a)\not\sim\rho(r)\), proving

\[
\boxed{a\not\sim_H r.}
\]

Since \(r^{-1}\) is also a transposition in this quotient, the same quotient
also separates the two elements if “inverse-conjugate” is interpreted as
\(a\sim r^{-1}\); the height argument already ruled this out internally.

The obstruction can be read directly on equation (2).  Under \(\rho\),

\[
\rho(t)=X,\qquad \rho(q)=1,\qquad
\rho(r_0)=(0\,1\,3).
\]

If (2) held and \(W=\rho(w)\), then

\[
\rho(r_0)=W X^{-1}W^{-1}X.
\]

Multiplication on the right by \(X^{-1}\) would give

\[
\rho(r)=\rho(r_0)X^{-1}=W X^{-1}W^{-1}.
\]

The right side is a conjugate of the 4-cycle \(X^{-1}\), while the left side
is the transposition \((2\,3)\), a contradiction.  Thus the finite quotient
is also an exact invariant for the free-group twisted equation, with no
bounds on \(w\) or \(n\).

## Status

- Identity \(z_0=[r,x]\): **proved**.
- Correct kernel coordinate of \(r\): **verified by direct semidirect
  multiplication**.
- Exact free-group equation for \(a\sim r\): **proved**.
- \(a\sim r\): **disproved by an explicit \(S_4\) quotient**.
- \(a\sim r^{-1}\): **disproved by height, and independently by the same
  quotient**.
- Result 134 residual equation itself: **still open**; nonconjugacy only
  closes this proposed transport of the explicit commutator.
