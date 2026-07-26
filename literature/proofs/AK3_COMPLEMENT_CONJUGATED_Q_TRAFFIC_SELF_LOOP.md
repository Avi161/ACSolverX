# Complement-conjugated q-source traffic is a stable self-loop

Date: 2026-07-25

Status: **PROVEN** for every conjugator whose pullback lies in a
free-factor complement to the primitive recovery word \(U\). If

\[
F_0=F(K)*\langle U\rangle,
\qquad
\phi^{-1}(q)=U^{-1}q,
\]

then for every \(a\in F(K)\), \(c=\phi(a)\), and
\(\epsilon\in\{+1,-1\}\), the target

\[
Wc q^\epsilon c^{-1},
\qquad
W=\phi(q),
\]

is primitive. Deleting it and then the surviving conjugate of \(q\)
gives literally the same quotient as deleting \(W\) and then the
surviving \(U^{-1}\).

For AK(3), \(K=F(x,t)\). The choice \(a=t\) has \(c=t\), so this closes
both first nontrivial literal-conjugator branches

\[
Wtqt^{-1}
\quad\text{and}\quad
Wtq^{-1}t^{-1}.
\]

It does not cover conjugators whose pullback involves \(U\), and it does
not prove AK(3) stably AC-trivial.

## 1. Setup and the old double quotient

Let

\[
F_0=F(K)*\langle U\rangle,
\qquad
F=F_0*\langle q\rangle,
\tag{1.1}
\]

where \(U\) is a basis element of \(F_0\). Let

\[
\rho_q:F\longrightarrow F_0
\tag{1.2}
\]

kill \(q\), let

\[
\rho_U:F\longrightarrow F(K)*\langle q\rangle
\tag{1.3}
\]

kill \(U\), and let

\[
\lambda:F\longrightarrow F(K)
\tag{1.4}
\]

kill both \(U\) and \(q\).

Suppose \(\phi\in\operatorname{Aut}(F)\) satisfies

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q.
\tag{1.5}
\]

Assume the checkpoint

\[
\mathcal C=(A_1,\ldots,A_m,W,q)
\tag{1.6}
\]

is a balanced presentation of the trivial group. In particular, this
hypothesis holds when \(\mathcal C\) is reached from a stabilization of a
balanced trivial-group presentation by stable AC moves.

Straighten \(W\) by \(\phi^{-1}\) and delete the q-generator. The
surviving literal q-relator becomes \(U^{-1}\), so the endpoint is

\[
\bigl(
\rho_q\phi^{-1}(A_1),\ldots,
\rho_q\phi^{-1}(A_m),U^{-1}
\bigr).
\tag{1.7}
\]

Since \(U\) is a basis element, straighten and delete this last
generator-relator pair. The old double endpoint is

\[
\mathcal E_0
=
\bigl(
\lambda\phi^{-1}(A_1),\ldots,
\lambda\phi^{-1}(A_m)
\bigr).
\tag{1.8}
\]

Both deletions are valid in the balanced trivial-group setting.

## 2. The one-\(U\) automorphisms

Choose \(a\in F(K)\) and put

\[
c=\phi(a).
\tag{2.1}
\]

Define \(\delta_{a,+}\) to fix \(F(K)\) and \(q\), and set

\[
\delta_{a,+}(U)
=
qaU^{-1}qa^{-1}.
\tag{2.2}
\]

This is an automorphism because the displayed word contains
\(U^{-1}\) exactly once and its other letters avoid \(U\). Explicitly,

\[
\delta_{a,+}^{-1}(U)
=
qa^{-1}U^{-1}qa,
\tag{2.3}
\]

with \(F(K)\) and \(q\) again fixed.

Similarly, define \(\delta_{a,-}\) by

\[
\delta_{a,-}(U)
=
qaq^{-1}Ua^{-1},
\tag{2.4}
\]

fixing \(F(K)\) and \(q\). Its inverse is

\[
\delta_{a,-}^{-1}(U)
=
qa^{-1}q^{-1}Ua.
\tag{2.5}
\]

Direct substitution in (2.2)--(2.5) gives both compositions equal to
the identity.

### Theorem 2.1 (complement-conjugated q traffic)

For each \(\epsilon\in\{+1,-1\}\), classical AC moves change the
\(W\)-slot to

\[
T_{a,\epsilon}
=
Wc q^\epsilon c^{-1}
\tag{2.6}
\]

while restoring the source slot to literal \(q\). Both targets are
primitive. After deleting \(T_{a,\epsilon}\) and the surviving
q-generator-relator pair, the endpoint is literally
\(\mathcal E_0\).

#### Proof

Conjugate the q-source to \(cq^\epsilon c^{-1}\), using AC2 as well when
\(\epsilon=-1\), multiply it into the \(W\)-target, and reverse the
source conjugation and inversion. This gives (2.6).

For the positive orientation,

\[
\begin{aligned}
\phi^{-1}(T_{a,+})
&=
q\,a\,(U^{-1}q)\,a^{-1}\\
&=
qaU^{-1}qa^{-1}\\
&=
\delta_{a,+}(U).
\end{aligned}
\tag{2.7}
\]

For the negative orientation,

\[
\begin{aligned}
\phi^{-1}(T_{a,-})
&=
q\,a\,(U^{-1}q)^{-1}\,a^{-1}\\
&=
qaq^{-1}Ua^{-1}\\
&=
\delta_{a,-}(U).
\end{aligned}
\tag{2.8}
\]

Therefore

\[
T_{a,\epsilon}
=
(\phi\delta_{a,\epsilon})(U)
\tag{2.9}
\]

is primitive.

Straighten by

\[
(\phi\delta_{a,\epsilon})^{-1}
=
\delta_{a,\epsilon}^{-1}\phi^{-1}
\]

and delete \(U\). In the positive branch, the surviving q-relator maps
before deletion to

\[
\begin{aligned}
\delta_{a,+}^{-1}\phi^{-1}(q)
&=
\delta_{a,+}^{-1}(U^{-1}q)\\
&=
a^{-1}q^{-1}Ua.
\end{aligned}
\tag{2.10}
\]

After \(U\mapsto1\), this is \(a^{-1}q^{-1}a\).

In the negative branch,

\[
\begin{aligned}
\delta_{a,-}^{-1}\phi^{-1}(q)
&=
\delta_{a,-}^{-1}(U^{-1}q)\\
&=
a^{-1}U^{-1}qa.
\end{aligned}
\tag{2.11}
\]

After \(U\mapsto1\), this is \(a^{-1}qa\). Thus the surviving source is
a conjugate of \(q^{-\epsilon}\) in both cases. Conjugate it to
\(q^{-\epsilon}\), invert if necessary, and delete q.

It remains to identify the other survivors. Inspection on the basis
\(K\cup\{U,q\}\) gives

\[
\boxed{
\lambda\delta_{a,\epsilon}^{-1}
=
\lambda.
}
\tag{2.12}
\]

Indeed, both maps fix \(K\) and \(q\), while (2.3) and (2.5) map \(U\)
to a word that becomes trivial when \(U\) and \(q\) are killed. Hence
the final image of every \(A_i\) is

\[
\lambda\delta_{a,\epsilon}^{-1}\phi^{-1}(A_i)
=
\lambda\phi^{-1}(A_i).
\tag{2.13}
\]

This is literal equality with the old double endpoint (1.8), not merely
equality modulo a retained normal closure. \(\square\)

## 3. AK(3): the literal \(t\)-conjugator

Put

\[
\begin{aligned}
R&=x^3t^{-4},\\
p_0&=xt,\\
B&=z^{-1}p_0,\\
D&=t^{-1}zxz^{-1},\\
U&=RB.
\end{aligned}
\tag{3.1}
\]

As proved in the literal-q theorem, \(U\) is a basis element of
\(F(x,t,z)\). Thus

\[
F(x,t,z)=F(x,t)*\langle U\rangle.
\tag{3.2}
\]

Use

\[
\begin{aligned}
\alpha_U(q)&=Uq,\\
\beta(x)&=qxq^{-1},\\
\beta(t)&=t,\\
\beta(z)&=z,\\
\beta(q)&=q,
\end{aligned}
\qquad
\phi=\beta\alpha_U,
\qquad
W=\phi(q).
\tag{3.3}
\]

The source-slot exchange certificate reaches

\[
(\beta(R),W,D,q)
\tag{3.4}
\]

from the stabilization of \((R,B,D)\). Since

\[
\phi(t)=t,
\]

take

\[
a=t,
\qquad
c=t.
\tag{3.5}
\]

Theorem 2.1 proves both

\[
\boxed{
T_+=Wtqt^{-1},
\qquad
T_-=Wtq^{-1}t^{-1}
}
\tag{3.6}
\]

primitive. Their exact pullbacks are

\[
\phi^{-1}(T_+)=qtU^{-1}qt^{-1},
\qquad
\phi^{-1}(T_-)=qtq^{-1}Ut^{-1}.
\tag{3.7}
\]

After straightening and deleting \(U\), the surviving q-relators are

\[
t^{-1}q^{-1}t
\qquad\text{and}\qquad
t^{-1}qt,
\tag{3.8}
\]

respectively.

## 4. The exact rank-two endpoint

In the basis \(x,t,U\),

\[
z=p_0U^{-1}R.
\tag{4.1}
\]

The double quotient \(\lambda\phi^{-1}\) satisfies

\[
\lambda\phi^{-1}(\beta(R))=R
\tag{4.2}
\]

and

\[
\lambda\phi^{-1}(D)
=
E_R
:=
t^{-1}(p_0R)x(p_0R)^{-1}.
\tag{4.3}
\]

Thus both conjugated-q branches delete to

\[
(R,E_R).
\tag{4.4}
\]

The standard rank-two AK endpoint obtained by deleting
\(B=z^{-1}p_0\) is

\[
(R,E_0),
\qquad
E_0=t^{-1}p_0xp_0^{-1}.
\tag{4.5}
\]

There is an exact two-factor return:

\[
\boxed{
E_0^{-1}E_R
=
\bigl((p_0x^{-1})R(xp_0^{-1})\bigr)
\bigl(p_0R^{-1}p_0^{-1}\bigr).
}
\tag{4.6}
\]

Both factors are conjugates of \(R^{\pm1}\). The retained R-slot
therefore returns \(E_R\) to \(E_0\), and \((R,E_0)\) is the standard
rank-two AK(3) presentation. The new conjugated-q traffic is a stable
self-loop.

## 5. Boundary

The theorem closes

\[
W\longmapsto
W\phi(a)q^{\pm1}\phi(a)^{-1}
\qquad
(a\in F(K)).
\tag{5.1}
\]

It does not close:

- an arbitrary iteration of the one target multiplication (5.1);
- a conjugator \(c\) with \(\phi^{-1}(c)\notin F(K)\);
- a pullback conjugator involving \(U\);
- a changed spelling of the q-source;
- several interleaved q-dependent source factors;
- a target whose pullback has several essential \(U\)-occurrences;
- primitive-pair compression.

For AK(3), the literal conjugators \(x\) and \(z\) lie outside this
theorem because

\[
\phi^{-1}(x)=q^{-1}UxU^{-1}q,
\qquad
z=p_0U^{-1}R.
\tag{5.2}
\]

These exclusions are structural, not claims of non-primitivity.
AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_complement_conjugated_q_traffic.py` checks:

- both \(\delta_{t,\pm}\) and their inverses in the original basis;
- both pullback and transported-target identities;
- both conjugated q-relators after the first deletion;
- equality of each new double quotient with the old one on every basis
  generator;
- the exact endpoint (4.3);
- the two-factor rank-two return (4.6).
