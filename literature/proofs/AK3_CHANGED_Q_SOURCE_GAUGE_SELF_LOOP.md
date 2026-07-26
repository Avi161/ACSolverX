# A changed q-source carried by passive sources is a gauge

Date: 2026-07-26

Status: **PROVEN**. If a literal stabilizer source q is changed to
\(Q=qV\), where the q-free word \(V\) lies in the normal closure of
passive source relators that remain distinct, then deleting \(Q\) gives
the ordinary q-deletion endpoint modulo those passive sources.
Arbitrary target traffic from \(Q\), including later traffic into the
passive slots themselves, disappears in the deletion.

For the fixed AK(3) checkpoint, \(V=D\). Thus the nonliteral source
\(qD\), followed by arbitrary traffic from that source, is a classical
self-loop after deletion. This does not prove AK(3) stably
AC-trivial.

## 1. General retained-source gauge theorem

Let

\[
F=F(X)*\langle q\rangle
\]

and suppose a balanced trivial-group checkpoint has the ordered
relator tuple

\[
\mathcal C
=
(S_1,\ldots,S_k,A_1,\ldots,A_m,q).
\tag{1.1}
\]

Assume the passive sources \(S_i\) lie in \(F(X)\). Put

\[
L=
\langle\!\langle S_1,\ldots,S_k\rangle\!\rangle_{F(X)}
\tag{1.2}
\]

and choose a q-free word \(V\in L\). The passive slots remain literal
through the manufacture of \(Q\) and remain distinct until its deletion.

Using them as sources, the multi-source normal-closure lemma changes
the final slot from q to

\[
Q=qV.
\tag{1.3}
\]

This word is primitive. Indeed, the transvection

\[
\tau_V(q)=qV,
\qquad
\tau_V(a)=a\quad(a\in X)
\tag{1.4}
\]

has inverse

\[
\tau_V^{-1}(q)=qV^{-1},
\qquad
\tau_V^{-1}(a)=a\quad(a\in X).
\tag{1.5}
\]

After manufacturing \(Q\), keep it unchanged and use it as a source to
make arbitrary target changes

\[
\begin{aligned}
S_i&\longmapsto S_ig_i,
&
g_i&\in\langle\!\langle Q\rangle\!\rangle_F,\\
A_j&\longmapsto A_jh_j,
&
h_j&\in\langle\!\langle Q\rangle\!\rangle_F.
\end{aligned}
\tag{1.6}
\]

The \(g_i,h_j\) may have arbitrary finite factorizations, conjugators,
orientations, and word lengths.

### Theorem 1.1

Straightening and deleting \(Q\) from

\[
(S_1g_1,\ldots,S_kg_k,A_1h_1,\ldots,A_mh_m,Q)
\tag{1.7}
\]

produces an endpoint classically AC-equivalent to the endpoint obtained
by deleting the original literal q from (1.1).

#### Proof

All preceding changes are classical AC moves, so (1.7) remains a
balanced presentation of the trivial group. Since \(Q\) is primitive,
ambient straightening followed by destabilization is legal.

Let

\[
\rho:F\longrightarrow F(X)
\]

kill q and fix \(F(X)\). Straighten \(Q=\tau_V(q)\) by
\(\tau_V^{-1}\), then delete q. The resulting evaluation is

\[
\sigma_V:=\rho\tau_V^{-1},
\qquad
\sigma_V(q)=V^{-1},
\qquad
\sigma_V|_{F(X)}=\operatorname{id}.
\tag{1.8}
\]

In particular,

\[
\sigma_V(Q)=1.
\tag{1.9}
\]

Every \(g_i\) and \(h_j\) in (1.6) therefore vanishes:

\[
\sigma_V(S_ig_i)=S_i,
\qquad
\sigma_V(A_jh_j)=\sigma_V(A_j).
\tag{1.10}
\]

Let

\[
\pi:F(X)\longrightarrow F(X)/L.
\]

Because \(V\in L\), the two maps \(\pi\sigma_V\) and \(\pi\rho\) agree
on \(X\cup\{q\}\), hence on all of \(F\):

\[
\boxed{\pi\sigma_V=\pi\rho.}
\tag{1.11}
\]

Consequently,

\[
\rho(A_j)^{-1}\sigma_V(A_j)\in L
\tag{1.12}
\]

for every survivor. Thus the q-free passive relators return literally.
Hold those slots fixed and apply the multi-source normal-closure lemma
to the other slots one at a time. Equation (1.12) changes every
\(\sigma_V(A_j)\) back to \(\rho(A_j)\). The result is precisely the
ordinary-q deletion endpoint

\[
(S_1,\ldots,S_k,\rho(A_1),\ldots,\rho(A_m)).
\]

This proves the theorem. \(\square\)

## 2. Exact AK(3) qD branch

Put

\[
\begin{aligned}
R&=x^3t^{-4},&
p&=xt,\\
B&=z^{-1}p,&
D&=t^{-1}zxz^{-1},\\
U&=RB.
\end{aligned}
\tag{2.1}
\]

Let

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,
\qquad
\beta(z)=z,
\qquad
\beta(q)=q,
\tag{2.2}
\]

and

\[
W=\beta(U)q.
\tag{2.3}
\]

The fixed source-slot checkpoint is

\[
(\beta(R),W,D,q).
\tag{2.4}
\]

Use the passive D-slot once to change the final source by target
multiplication:

\[
q\longmapsto Q=qD.
\tag{2.5}
\]

Now allow arbitrary traffic from \(Q\) into any of the first three
slots, while \(Q\) remains unchanged, and delete \(Q\) first.
Theorem 1.1 already proves that the result returns to ordinary
q-deletion. The following calculation gives the exact intermediate
words and source factors.

The deletion map is

\[
\sigma_D(q)=D^{-1},
\qquad
\sigma_D(x)=x,
\qquad
\sigma_D(t)=t,
\qquad
\sigma_D(z)=z.
\tag{2.6}
\]

Define

\[
\begin{aligned}
R_D
&=\sigma_D(\beta(R))
=D^{-1}x^3Dt^{-4},\\
p_D
&=\sigma_D(\beta(p))
=D^{-1}xDt,\\
W_D
&=\sigma_D(W)
=R_Dz^{-1}p_DD^{-1}.
\end{aligned}
\tag{2.7}
\]

Every traffic multiplier from \(\langle\!\langle Q\rangle\!\rangle\)
maps to \(1\), including any multiplier placed in the D-slot. Thus
deletion gives exactly

\[
(R_D,W_D,D),
\tag{2.8}
\]

independently of that traffic.

## 3. Explicit retained-source return

The first survivor differs from \(R\) by two D-source factors:

\[
\boxed{
R^{-1}R_D
=
(R^{-1}D^{-1}R)(t^4Dt^{-4}).
}
\tag{3.1}
\]

Similarly,

\[
\boxed{
p^{-1}p_D
=
(p^{-1}D^{-1}p)(t^{-1}Dt).
}
\tag{3.2}
\]

Using \(U=Rz^{-1}p\), the second survivor satisfies

\[
\boxed{
U^{-1}W_D
=
\bigl(p^{-1}z(R^{-1}R_D)z^{-1}p\bigr)
\bigl(p^{-1}p_D\bigr)
D^{-1}.
}
\tag{3.3}
\]

After expanding (3.1) and (3.2), the right side of (3.3) is five
conjugates of \(D^{\pm1}\). Thus two D-source multiplications return
\(R_D\) to \(R\), and five return \(W_D\) to \(U\). The order is the
reverse of the displayed difference factors, with each factor
inverted.

Finally,

\[
\boxed{
U^{-1}B=B^{-1}R^{-1}B.
}
\tag{3.4}
\]

One retained-R source multiplication changes \(U\) back to \(B\).
Therefore

\[
\boxed{
(R_D,W_D,D)
\sim_{\mathrm{AC1-3}}
(R,B,D).
}
\tag{3.5}
\]

The changed source \(qD\) and every allowed finite history from it are
classical self-loops after the single destabilization.

## 4. Boundary

The general theorem requires:

- a balanced trivial-group checkpoint;
- q-free passive source relators that remain literal through the
  manufacture of \(Q\) and remain distinct until deletion;
- \(V\) in their joint normal closure;
- a changed source exactly \(Q=qV\), kept unchanged and deleted first;
- all later target multipliers, including those placed in a passive
  slot, only from
  \(\langle\!\langle Q\rangle\!\rangle\).

It does not cover q-dependent \(V\), loss of a needed passive slot,
non-Q traffic into that slot, a second change to \(Q\), traffic from
another source with nontrivial image under \(\sigma_V\), or
primitive-pair compression. Further return beyond the ordinary-q
endpoint also requires a separate baseline return certificate; Section
3 supplies it for AK(3).

AK(3) and stable AC remain open.

## 5. Independent replay

The dependency-free verifier
`tests/stable_ac/test_changed_q_source_gauge.py` checks:

- \(\tau_D,\tau_D^{-1}\) in both composition orders;
- representative products of conjugates of \(Q^{\pm1}\);
- the exact deletion images \(R_D,p_D,W_D\);
- both two-factor identities (3.1)--(3.2);
- the five-D-factor identity (3.3);
- the exact reverse return order;
- the final one-R-factor return (3.4).
