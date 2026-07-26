# Multi-source relation-split primitive words are stable self-loops

Date: 2026-07-25

Status: **PROVEN** for every balanced trivial-group presentation, every
retained relator subtuple, every consequence \(U\) of that subtuple, and
every relative-kernel automorphism \(\beta\) satisfying
\(\beta(q)=q\). The primitive word

\[
W=\beta(U)q
\]

can be manufactured using all retained sources, but its deletion returns
classically to the original presentation. For AK(3), this closes the
first genuinely \(B\)-coupled choice \(U=RB\), whose primitive word has
five \(q^{\pm1}\)-occurrences.

This does not close histories that fail to retain the normal closure of
every source used in \(U\).

## 1. A multi-source normal-closure lemma

### Lemma 1.1

Let

\[
L=\langle\!\langle A_1,\ldots,A_k\rangle\!\rangle_F
\]

be the normal closure of a relator subtuple in a free group \(F\). If

\[
V^{-1}V'\in L,
\tag{1.1}
\]

then

\[
(A_1,\ldots,A_k,V)
\sim_{\mathrm{AC1-3}}
(A_1,\ldots,A_k,V'),
\tag{1.2}
\]

with every \(A_i\)-slot restored after each source multiplication. Any
other relator slots can be left literal.

#### Proof

Choose a finite normal-closure factorization

\[
V^{-1}V'
=
\prod_{j=1}^{n}
g_jA_{i_j}^{\epsilon_j}g_j^{-1},
\qquad
\epsilon_j\in\{+1,-1\}.
\tag{1.3}
\]

For the \(j\)-th factor, invert the source \(A_{i_j}\) if necessary,
conjugate it by \(g_j\), right-multiply the \(V\)-slot, and undo the
source conjugation and inversion. These are AC1--AC3 moves. After all
factors, the target is

\[
V(V^{-1}V')=V'.
\]

No other slot changes. \(\square\)

## 2. Universal multi-source loop

Let \(X\) be a finite basis and let

\[
\mathcal P
=
\langle X\mid
R_1,\ldots,R_k,S_1,\ldots,S_m
\rangle
\tag{2.1}
\]

be a balanced presentation of the trivial group. Put

\[
F=F(X)*\langle q\rangle
\]

and let

\[
\rho:F\longrightarrow F(X)
\tag{2.2}
\]

fix \(X\) and kill \(q\).

Choose

\[
U\in
L:=
\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)}
\tag{2.3}
\]

and \(\beta\in\operatorname{Aut}(F)\) satisfying

\[
\beta(q)=q,
\qquad
\rho\beta=\rho.
\tag{2.4}
\]

Define

\[
\alpha_U(q)=Uq,
\qquad
\alpha_U(a)=a\quad(a\in X),
\tag{2.5}
\]

and

\[
\phi=\beta\alpha_U,
\qquad
W=\phi(q)=\beta(U)q.
\tag{2.6}
\]

### Theorem 2.1 (multi-source primitive self-loop)

There is a classical AC sequence

\[
\begin{aligned}
(&R_1,\ldots,R_k,S_1,\ldots,S_m,q)\\
&\sim_{\mathrm{AC1-3}}
(\beta(R_1),\ldots,\beta(R_k),S_1,\ldots,S_m,W).
\end{aligned}
\tag{2.7}
\]

Straighten \(W\) by \(\phi^{-1}\) and remove the primitive
generator-relator pair. The endpoint is

\[
\mathcal E
=
(R_1,\ldots,R_k,p(S_1),\ldots,p(S_m)),
\qquad
p=\rho\phi^{-1},
\tag{2.8}
\]

and

\[
\boxed{
\mathcal E
\sim_{\mathrm{AC1-3}}
(R_1,\ldots,R_k,S_1,\ldots,S_m).
}
\tag{2.9}
\]

#### Proof

For every \(i\),

\[
\rho(\beta(R_i))=R_i,
\]

so

\[
R_i^{-1}\beta(R_i)
\in
\langle\!\langle q\rangle\!\rangle_F.
\tag{2.10}
\]

Apply Lemma 1.1 with the one retained source \(q\) to replace the
\(R_i\)-slots one at a time by \(\beta(R_i)\), restoring \(q\) after
every factor. All \(S_j\) remain literal.

Because \(U\in L\),

\[
\beta(U)
\in
\langle\!\langle
\beta(R_1),\ldots,\beta(R_k)
\rangle\!\rangle_F.
\tag{2.11}
\]

Lemma 1.1 now replaces the \(q\)-slot by \(q\beta(U)\), using the
\(\beta(R_i)\)-slots as sources. Conjugating that target by \(q^{-1}\)
gives

\[
q^{-1}\bigl(q\beta(U)\bigr)q
=\beta(U)q
=W.
\tag{2.12}
\]

This proves (2.7).

Apply \(\phi^{-1}=\alpha_U^{-1}\beta^{-1}\). For every retained source,

\[
\phi^{-1}(\beta(R_i))
=\alpha_U^{-1}(R_i)
=R_i,
\tag{2.13}
\]

while \(\phi^{-1}(W)=q\). Stable ambient straightening followed by
primitive deletion is valid because (2.1) is a balanced presentation of
the trivial group. After deleting \(q\), the other slots are \(p(S_j)\),
which proves (2.8).

Let

\[
\lambda:F\longrightarrow F(X)/L
\tag{2.14}
\]

kill \(q\). Since \(U\in L\) and
\(\alpha_U^{-1}(q)=U^{-1}q\),

\[
\lambda\alpha_U^{-1}=\lambda.
\tag{2.15}
\]

Equation (2.4) gives

\[
\lambda\beta^{-1}=\lambda.
\tag{2.16}
\]

Consequently

\[
\lambda\phi^{-1}=\lambda,
\]

and, for every \(j\),

\[
S_j^{-1}p(S_j)\in L.
\tag{2.17}
\]

Use Lemma 1.1 with the retained \(R_i\)-subtuple to restore the
\(S_j\)-slots one at a time. This proves (2.9). \(\square\)

The theorem has no bound on the lengths of \(U,\beta\), or the
normal-closure factorizations.

## 3. A five-\(q\) AK(3) primitive word

At the rank-three compression root, put

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{3.1}
\]

Retain the two-source subtuple \((R,B)\), set

\[
U=RB,
\tag{3.2}
\]

and define

\[
\begin{aligned}
\beta(x)&=qxq^{-1},&
\beta(t)&=t,\\
\beta(z)&=z,&
\beta(q)&=q.
\end{aligned}
\tag{3.3}
\]

Then

\[
\begin{aligned}
\beta(R)&=qx^3q^{-1}t^{-4},\\
\beta(B)&=z^{-1}qxq^{-1}t,
\end{aligned}
\tag{3.4}
\]

and

\[
\boxed{
W=\beta(R)\beta(B)q
=
qx^3q^{-1}t^{-4}z^{-1}qxq^{-1}tq.
}
\tag{3.5}
\]

The displayed word is freely and cyclically reduced, has
\(q\)-exponent \(1\), and contains exactly five
\(q^{\pm1}\)-occurrences. It is primitive by (2.6).

### Proposition 3.1 (literal cross-coupled manufacture)

The replacements of both retained sources have exact two-factor
certificates:

\[
\boxed{
\begin{aligned}
R^{-1}\beta(R)
&=(R^{-1}qR)(t^4q^{-1}t^{-4}),\\
B^{-1}\beta(B)
&=((t^{-1}x^{-1})q(xt))(t^{-1}q^{-1}t).
\end{aligned}
}
\tag{3.6}
\]

After those four \(q\)-source factors, two target multiplications and one
conjugation give

\[
q
\longmapsto
q\beta(R)\beta(B)
\longmapsto
q^{-1}\bigl(q\beta(R)\beta(B)\bigr)q
=W.
\tag{3.7}
\]

Thus

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),\beta(B),D,W).
\tag{3.8}
\]

#### Proof

All identities are literal free reductions. The first line of (3.6) is
the one-source certificate. The second right side reduces to

\[
t^{-1}x^{-1}qxq^{-1}t
=B^{-1}\beta(B).
\]

Equations (3.7)--(3.8) follow by AC1 and AC3. \(\square\)

## 4. Primitive quotient and four-factor return

For \(U=RB\), the quotient \(p=\rho\phi^{-1}\) is

\[
\boxed{
\begin{aligned}
p(x)&=UxU^{-1},&
p(t)&=t,\\
p(z)&=z,&
p(q)&=U^{-1}.
\end{aligned}
}
\tag{4.1}
\]

Straightening (3.8) and deleting \(q\) gives

\[
(R,B,D'),
\qquad
D'=t^{-1}zUxU^{-1}z^{-1}.
\tag{4.2}
\]

The exact endpoint difference is

\[
\begin{aligned}
D^{-1}D'
&=
\bigl((zx^{-1})U(xz^{-1})\bigr)
\bigl(zU^{-1}z^{-1}\bigr)\\
&=
\bigl((zx^{-1})R(xz^{-1})\bigr)
\bigl((zx^{-1})B(xz^{-1})\bigr)\\
&\qquad
\bigl(zB^{-1}z^{-1}\bigr)
\bigl(zR^{-1}z^{-1}\bigr).
\end{aligned}
\tag{4.3}
\]

The last line is a product of four conjugates of the retained relators
\(R^{\pm1},B^{\pm1}\). Lemma 1.1 therefore gives

\[
(R,B,D')
\sim_{\mathrm{AC1-3}}
(R,B,D).
\tag{4.4}
\]

This is a genuinely cross-coupled production: \(B\) occurs inside the
primitive word and is a source in its manufacture. It is still a
self-loop because \(B\) survives, is coherently straightened, and its
normal closure remains available to absorb the quotient distortion.

## 5. Exact boundary

Theorem 2.1 closes any number of retained sources and any consequence of
their joint normal closure. Transient source/target moves are harmless if
the pre-deletion checkpoint has the literal
\(\beta(R_1),\ldots,\beta(R_k)\) retained subtuple and the other literal
\(S_j\)-slots.

It does not close:

- deletion of one of the sources whose normal closure is needed for
  \(U\);
- a pre-deletion retained subtuple with a different joint normal closure;
- a survivor outside its baseline class modulo the retained subtuple;
- a primitive word outside the family \(\beta(U)q\);
- primitive-pair compression.

Within the \(\beta(U)q\) family, an escape must not merely use \(B\) or
\(D\); it must cross at least one of the listed boundaries, such as
making the normal closure needed to undo that use unavailable after
primitive deletion. AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_multisource_primitive_loop.py` checks:

- both two-factor \(q\)-source identities (3.6);
- exact manufacture and the five \(q^{\pm1}\)-occurrence count;
- \(\phi,\phi^{-1}\), and all quotient images (4.1);
- the endpoint spelling (4.2);
- both forms of the four-factor return identity (4.3).
