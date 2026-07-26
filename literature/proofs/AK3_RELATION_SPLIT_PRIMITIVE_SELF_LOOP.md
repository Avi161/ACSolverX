# Relation-split primitive words are stable self-loops

Date: 2026-07-25

Status: **PROVEN**. If a relative-kernel automorphism \(\beta\) splits a
consequence \(U\) of a retained relator \(R\) by the stabilizer \(q\),
the primitive word

\[
W=\beta(U)q
\]

can be manufactured asymmetrically by classical AC moves. Nevertheless,
straightening and deleting \(W\) changes every untouched survivor only
by a consequence of \(R\), so the endpoint returns by classical AC
moves whenever the base tuple is a balanced trivial-group presentation.
For AK(3), this closes the direct construction of

\[
qx^3q^{-1}t^{-4}q.
\]

It does not close productions whose use of the other AK(3) relators
leaves survivors outside the endpoint congruence modulo \(R\).

## 1. Relative-kernel setup

Let \(X\) be a finite basis and put

\[
F=F(X)*\langle q\rangle.
\]

Let

\[
\rho:F\longrightarrow F(X)
\tag{1.1}
\]

fix \(X\) and kill \(q\). Assume that the balanced presentation

\[
\mathcal P
=\langle X\mid R,S_1,\ldots,S_m\rangle
\tag{1.2}
\]

presents the trivial group. Choose

\[
U\in\langle\!\langle R\rangle\!\rangle_{F(X)}
\tag{1.3}
\]

and an automorphism \(\beta\in\operatorname{Aut}(F)\) satisfying

\[
\beta(q)=q,
\qquad
\rho\beta=\rho.
\tag{1.4}
\]

Thus \(\beta\) is invisible after the stabilizer is killed.

Define the elementary automorphism

\[
\alpha_U(q)=Uq,
\qquad
\alpha_U(a)=a\quad(a\in X),
\tag{1.5}
\]

and put

\[
\phi=\beta\alpha_U,
\qquad
W=\phi(q)=\beta(U)q.
\tag{1.6}
\]

The word \(W\) is primitive because it is the image of the basis element
\(q\) under \(\phi\).

## 2. The universal loop theorem

### Theorem 2.1 (relation-split primitive self-loop)

Start with the stabilized relator tuple

\[
\mathcal T=(R,S_1,\ldots,S_m,q)
\tag{2.1}
\]

over \(F\). There is a classical AC sequence on this tuple that replaces
the \(R\)-slot by \(\beta(R)\) and the \(q\)-slot by
\(W=\beta(U)q\), leaving every \(S_i\)-slot unchanged.

Straighten the primitive relator \(W\) with \(\phi^{-1}\) and remove the
resulting generator-relator pair. The rank-\(|X|\) endpoint is

\[
\mathcal E=
\bigl(R,p(S_1),\ldots,p(S_m)\bigr),
\qquad
p=\rho\phi^{-1}.
\tag{2.2}
\]

It satisfies

\[
\boxed{
\mathcal E
\sim_{\mathrm{AC1-3}}
(R,S_1,\ldots,S_m).
}
\tag{2.3}
\]

Consequently the whole manufacture-and-delete construction is a stable
AC self-loop.

#### Proof

Because \(\ker\rho=\langle\!\langle q\rangle\!\rangle_F\), (1.4) gives

\[
R^{-1}\beta(R)\in\langle\!\langle q\rangle\!\rangle_F.
\tag{2.4}
\]

The fixed-relator normal-closure lemma therefore replaces the \(R\)-slot
by \(\beta(R)\), using conjugates of the \(q\)-relator and restoring that
source after every multiplication. All \(S_i\) stay fixed.

Because \(U\in\langle\!\langle R\rangle\!\rangle\),

\[
\beta(U)
\in
\langle\!\langle\beta(R)\rangle\!\rangle.
\tag{2.5}
\]

Hold the new \(\beta(R)\)-slot fixed and use the same lemma to replace
the \(q\)-slot by \(q\beta(U)\). Conjugating this target by \(q^{-1}\)
gives

\[
q^{-1}\bigl(q\beta(U)\bigr)q
=\beta(U)q
=W.
\tag{2.6}
\]

This proves the classical creation assertion.

Now apply \(\phi^{-1}\) to straighten \(W=\phi(q)\) to \(q\), and use
primitive-relator removal. The transformed retained slot is

\[
\phi^{-1}(\beta(R))
=\alpha_U^{-1}(R)
=R.
\tag{2.7}
\]

After setting \(q=1\), the other slots become \(p(S_i)\), proving (2.2).
The ambient straightening and deletion are stable AC operations; no
claim that an arbitrary ambient automorphism is classically AC is being
used here.

It remains to compare the endpoint classically. Let

\[
\lambda:F\longrightarrow
\overline F:=F(X)/\langle\!\langle R\rangle\!\rangle
\tag{2.8}
\]

send \(q\) to \(1\). Since
\(\alpha_U^{-1}(q)=U^{-1}q\) and \(U=1\) in \(\overline F\), one has

\[
\lambda\alpha_U^{-1}=\lambda.
\tag{2.9}
\]

Equation (1.4) also implies

\[
\lambda\beta^{-1}=\lambda.
\tag{2.10}
\]

Therefore

\[
\lambda\phi^{-1}
=\lambda\alpha_U^{-1}\beta^{-1}
=\lambda.
\tag{2.11}
\]

For each \(q\)-free survivor \(S_i\), (2.11) says precisely

\[
S_i^{-1}p(S_i)
\in
\langle\!\langle R\rangle\!\rangle_{F(X)}.
\tag{2.12}
\]

Hold the \(R\)-slot fixed and apply the normal-closure lemma to the
\(S_i\)-slots one at a time. This gives the classical equivalence (2.3)
without changing any already restored slot. \(\square\)

The theorem has no word-length bound and no search component. The
balanced trivial-presentation hypothesis is used only to invoke stable
ambient straightening and primitive deletion. The classical creation,
quotient identity, and endpoint return remain valid as algebraic
statements without it.

## 3. Exact AK(3) specialization

Use the rank-three AK(3) compression root, which is a balanced
presentation of the trivial group:

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{3.1}
\]

Add the stabilizing generator-relator pair \((q,q)\), and define

\[
\begin{aligned}
\beta(x)&=qxq^{-1},&
\beta(t)&=t,\\
\beta(z)&=z,&
\beta(q)&=q.
\end{aligned}
\tag{3.2}
\]

Then \(\rho\beta=\rho\), and free reduction gives

\[
\beta(R)=qx^3q^{-1}t^{-4}.
\tag{3.3}
\]

Take \(U=R\). Hence the primitive relator in (1.6) is exactly

\[
W=qx^3q^{-1}t^{-4}q.
\tag{3.4}
\]

### Proposition 3.1 (literal creation certificate)

The passage

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),B,D,W)
\tag{3.5}
\]

has the exact two-source-factor identity

\[
\boxed{
R^{-1}\beta(R)
=
\bigl(R^{-1}qR\bigr)
\bigl(t^4q^{-1}t^{-4}\bigr).
}
\tag{3.6}
\]

#### Proof

The right side freely reduces to

\[
t^4x^{-3}qx^3q^{-1}t^{-4}
=R^{-1}\beta(R).
\]

Thus two multiplications of the \(R\)-slot by conjugates of
\(q^{\pm1}\) replace \(R\) by \(\beta(R)\). The final target operation is

\[
q\longmapsto q\beta(R)
\longmapsto
q^{-1}\bigl(q\beta(R)\bigr)q
=\beta(R)q=W,
\tag{3.7}
\]

while \(B,D\) remain literal. \(\square\)

## 4. The primitive quotient and explicit return

For the \(\alpha_U,\beta\) above, with \(U=R\),

\[
\phi=\beta\alpha_U,
\qquad
\phi^{-1}=\alpha_U^{-1}\beta^{-1}.
\]

The straightening quotient \(p=\rho\phi^{-1}\) is

\[
\boxed{
\begin{aligned}
p(x)&=RxR^{-1},&
p(t)&=t,\\
p(z)&=z,&
p(q)&=R^{-1}.
\end{aligned}
}
\tag{4.1}
\]

Thus primitive deletion takes (3.5) to

\[
\begin{aligned}
R'&=R,\\
B'&=z^{-1}RxR^{-1}t,\\
D'&=t^{-1}zRxR^{-1}z^{-1}.
\end{aligned}
\tag{4.2}
\]

The endpoint return can be made completely literal:

\[
\boxed{
\begin{aligned}
B^{-1}B'
&=
\bigl((t^{-1}x^{-1})R(xt)\bigr)
\bigl(t^{-1}R^{-1}t\bigr),\\
D^{-1}D'
&=
\bigl((zx^{-1})R(xz^{-1})\bigr)
\bigl(zR^{-1}z^{-1}\bigr).
\end{aligned}
}
\tag{4.3}
\]

Each parenthesized factor is a conjugate of \(R\) or \(R^{-1}\). The
fixed-\(R\) lemma first replaces \(B'\) by \(B\) and then \(D'\) by
\(D\), or performs the inverse replacements. Hence

\[
(R,B',D')
\sim_{\mathrm{AC1-3}}
(R,B,D).
\tag{4.4}
\]

This gives an exact answer to the first production attempt left open by
the primitive-gate theorem: the primitive word is reachable, and the
production really is asymmetric before deletion, but the retained
relator absorbs the asymmetry afterward.

## 5. What is and is not closed

Theorem 2.1 closes every construction satisfying all of the following:

1. the stabilizing relator is \(q\);
2. a relative-kernel automorphism \(\beta\) with
   \(\beta(q)=q\) and \(\rho\beta=\rho\) is used to replace the retained
   \(R\) by \(\beta(R)\);
3. some \(U\in\langle\!\langle R\rangle\!\rangle\) is chosen and the
   primitive relator is \(W=\beta(U)q\);
4. at the pre-deletion checkpoint, the other survivor slots are the
   corresponding literal \(S_i\) (transient moves that are undone are
   harmless); and
5. the retained \(R\)-slot survives deletion.

It does not close:

- a history whose use of \(B\) or \(D\) leaves a survivor outside its
  baseline class modulo the retained \(R\);
- a history in which the surviving retained relator has a different
  normal closure;
- another primitive multi-\(q\) word not of the form \(\beta(U)q\) for
  such a relative automorphism and \(R\)-consequence \(U\);
- simultaneous primitive-pair compression.

The next non-self-loop attempt must cross one of those boundaries.
AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_relation_split_primitive_loop.py` checks:

- the exact two-factor creation identity (3.6);
- the target multiplication and conjugation (3.7);
- both compositions of \(\phi\) and \(\phi^{-1}\);
- every quotient image in (4.1);
- the endpoint spellings (4.2);
- both two-factor return identities in (4.3);
- a nontrivial \(U\), expressed as a product of two conjugates of
  \(R^{\pm1}\), together with its longer \(\beta(U)q\), automorphism
  inverse, and quotient images.
