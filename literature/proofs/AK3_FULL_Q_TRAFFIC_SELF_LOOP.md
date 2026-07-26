# Full q-source target traffic closes; literal-z targets are nonprimitive

Date: 2026-07-25

Status: **PROVEN** in two parts.

First, at the fixed AK(3) source-slot checkpoint, every target

\[
Wv,
\qquad
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,z,q)},
\]

is a stable self-loop when the distinct q-source slot is restored
literally: delete q first, then delete the primitive recovery word
\(U\). This has no restriction on z-occurrences, conjugators, signs,
factor count, or word length.

Second, the four exact one-conjugate targets

\[
Wz^\delta q^\epsilon z^{-\delta},
\qquad
\delta,\epsilon\in\{+1,-1\},
\]

are nonprimitive. Explicit Whitehead automorphisms take them to
cyclically reduced words whose graphs contain spanning cycles on all
eight signed basis vertices. This rules out target-first primitive
deletion for those four words, while the source-first theorem still
closes their stable branches.

Neither result proves AK(3) stably AC-trivial.

## 1. The four exact words

Put

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
U&=RB,\\
D&=t^{-1}zxz^{-1},
\end{aligned}
\tag{1.1}
\]

and use

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,
\qquad
\beta(z)=z,
\qquad
\beta(q)=q.
\tag{1.2}
\]

At the source-slot checkpoint,

\[
W=\beta(U)q
=
qxxxq^{-1}t^{-4}z^{-1}qxq^{-1}tq.
\tag{1.3}
\]

The four literal-z conjugator targets are

\[
T_{\delta,\epsilon}
=
Wz^\delta q^\epsilon z^{-\delta}.
\tag{1.4}
\]

In reduced letters:

\[
\begin{array}{c|c}
(\delta,\epsilon)&T_{\delta,\epsilon}\\
\hline
(+,+)&\texttt{qxxxQTTTTZqxQtqzqZ}\\
(+,-)&\texttt{qxxxQTTTTZqxQtqzQZ}\\
(-,+)&\texttt{qxxxQTTTTZqxQtqZqz}\\
(-,-)&\texttt{qxxxQTTTTZqxQtqZQz}
\end{array}
\tag{1.5}
\]

Each word is freely and cyclically reduced of length \(18\).

## 2. Exact Whitehead reductions

Define the automorphism

\[
\alpha(x)=q^{-1}xq,
\qquad
\alpha(t)=t,
\qquad
\alpha(z)=z,
\qquad
\alpha(q)=q.
\tag{2.1}
\]

Its inverse sends \(x\mapsto qxq^{-1}\) and fixes \(t,z,q\). Applying
\(\alpha\) to (1.5) gives strict reductions:

\[
\begin{array}{c|c|c}
(\delta,\epsilon)&\alpha(T_{\delta,\epsilon})&\text{length}\\
\hline
(+,+)&\texttt{xxxTTTTZxtqzqZ}&14\\
(+,-)&\texttt{xxxTTTTZxtqzQZ}&14\\
(-,+)&\texttt{xxxTTTTZxtqZqz}&14\\
(-,-)&\texttt{xxxTTTTZxtqZQz}&14
\end{array}
\tag{2.2}
\]

For the \(\delta=+1\) pair, define a second automorphism

\[
\begin{aligned}
\sigma(x)&=x,\\
\sigma(t)&=x^{-1}tx,\\
\sigma(z)&=zx,\\
\sigma(q)&=x^{-1}q.
\end{aligned}
\tag{2.3}
\]

An explicit inverse is

\[
\begin{aligned}
\sigma^{-1}(x)&=x,\\
\sigma^{-1}(t)&=xtx^{-1},\\
\sigma^{-1}(z)&=zx^{-1},\\
\sigma^{-1}(q)&=xq.
\end{aligned}
\tag{2.4}
\]

The second strict reductions are

\[
\begin{aligned}
P_+
&:=
\sigma\alpha(T_{+,+})
=
\texttt{xxTTTTZtqzqXZ},\\
P_-
&:=
\sigma\alpha(T_{+,-})
=
\texttt{xxTTTTZtqzxQZ}.
\end{aligned}
\tag{2.5}
\]

Both have length \(13\) and are freely and cyclically reduced.

For the negative-z conjugator pair, put

\[
\begin{aligned}
N_+
&:=
\alpha(T_{-,+})
=
\texttt{xxxTTTTZxtqZqz},\\
N_-
&:=
\alpha(T_{-,-})
=
\texttt{xxxTTTTZxtqZQz}.
\end{aligned}
\tag{2.6}
\]

Both have length \(14\) and are freely and cyclically reduced.

## 3. The two spanning-cycle certificates

For a cyclic word \(w\), use the Whitehead graph on

\[
x,X,t,T,z,Z,q,Q.
\]

Every cyclic adjacent pair \(ab\) contributes the undirected edge from
\(a^{-1}\) to \(b\).

### Positive-z conjugator pair

The words \(P_+\) and \(P_-\) have the same undirected edge set:

\[
\begin{aligned}
\{&
Q\!-\!X,\ Q\!-\!z,\ T\!-\!X,\ T\!-\!q,\ T\!-\!t,\\
&X\!-\!x,\ Z\!-\!q,\ Z\!-\!t,\ Z\!-\!x,\
t\!-\!z,\ x\!-\!z
\}.
\end{aligned}
\tag{3.1}
\]

It contains the spanning cycle

\[
\boxed{
Q-X-x-Z-q-T-t-z-Q.
}
\tag{3.2}
\]

### Negative-z conjugator pair

The words \(N_+\) and \(N_-\) also have a common edge set:

\[
\begin{aligned}
\{&
Q\!-\!Z,\ Q\!-\!z,\ T\!-\!X,\ T\!-\!q,\ T\!-\!t,\\
&X\!-\!t,\ X\!-\!x,\ Z\!-\!t,\ Z\!-\!x,\
q\!-\!z,\ x\!-\!z
\}.
\end{aligned}
\tag{3.3}
\]

It contains the spanning cycle

\[
\boxed{
Q-Z-x-X-t-T-q-z-Q.
}
\tag{3.4}
\]

A graph containing a cycle through every vertex is connected, and
deleting any vertex leaves a path through all the remaining vertices.
Thus both graphs are connected and have no cut vertex.

## 4. Nonprimitivity theorem

### Theorem 4.1

\[
\boxed{
T_{\delta,\epsilon}
\text{ is nonprimitive for all }
\delta,\epsilon\in\{+1,-1\}.
}
\tag{4.1}
\]

#### Proof

Whitehead's cut-vertex lemma says that the Whitehead graph of a
cyclically reduced primitive word of length greater than one is either
disconnected or has a cut vertex. The terminal words in (2.5) and
(2.6) have length greater than one, while (3.2) and (3.4) prove their
graphs connected with no cut vertex. They are therefore nonprimitive.

Automorphisms preserve primitivity. Equations (2.2), (2.5), and (2.6)
then prove the four original targets nonprimitive. \(\square\)

The cut-vertex criterion is the same classical Whitehead theorem used
in the multi-q seam classification:
J. H. C. Whitehead, “On Certain Sets of Elements in a Free Group,”
*Proceedings of the London Mathematical Society* s2-41 (1936), 48--56,
<https://doi.org/10.1112/plms/s2-41.1.48>.

## 5. Full q-normal-closure traffic closes

The target obstruction does not obstruct stable deletion in the other
order. Let

\[
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,z,q)}
\tag{5.1}
\]

be arbitrary. The single-source normal-closure replacement lemma uses
the surviving literal q-slot and changes the checkpoint to

\[
(\beta(R),Wv,D,q).
\tag{5.2}
\]

For completeness, write

\[
v=\prod_{i=1}^{m}c_iq^{\epsilon_i}c_i^{-1},
\qquad
\epsilon_i\in\{+1,-1\}.
\]

For each factor, conjugate the q-source relator by \(c_i\), invert it
when \(\epsilon_i=-1\), multiply the target on the right by that source,
and undo the inversion and conjugation on the source slot. These are
AC3, AC2, AC1, and their inverses. Iteration produces \(Wv\) while
restoring the source relator to the literal word q. Thus (5.2) holds for
every element of the full normal closure, not merely for the displayed
sample conjugates.

The q-slot is restored literally after the source multiplications.
Delete this generator-relator pair first. Let

\[
\rho_q:F(x,t,z,q)\longrightarrow F(x,t,z)
\tag{5.3}
\]

kill q. Since \(\rho_q\beta\) is the identity and
\(\rho_q(v)=1\),

\[
\boxed{
\begin{aligned}
\rho_q(\beta(R))&=R,\\
\rho_q(Wv)&=U,\\
\rho_q(D)&=D.
\end{aligned}
}
\tag{5.4}
\]

Thus the first deletion gives

\[
(R,U,D).
\tag{5.5}
\]

The recovery word is primitive. Indeed, with \(p=xt\), define

\[
\nu(z)=U=Rz^{-1}p,
\qquad
\nu(x)=x,
\qquad
\nu(t)=t.
\tag{5.6}
\]

Its inverse is

\[
\nu^{-1}(z)=pz^{-1}R,
\qquad
\nu^{-1}(x)=x,
\qquad
\nu^{-1}(t)=t.
\tag{5.7}
\]

Straighten \(U\) by \(\nu^{-1}\) and delete z. Since
\(\nu^{-1}(z)\) becomes \(pR\) after \(z\mapsto1\), the endpoint is

\[
(R,E_R),
\qquad
E_R=t^{-1}(pR)x(pR)^{-1}.
\tag{5.8}
\]

Let

\[
E_0=t^{-1}pxp^{-1}.
\tag{5.9}
\]

The exact difference is

\[
\boxed{
E_0^{-1}E_R
=
\bigl((px^{-1})R(xp^{-1})\bigr)
\bigl(pR^{-1}p^{-1}\bigr).
}
\tag{5.10}
\]

Two retained-\(R\) source factors return \(E_R\) to \(E_0\).
Therefore:

\[
\boxed{
(\beta(R),Wv,D,q)
\sim_{\mathrm{stable\ AC}}
(R,E_0)
\quad
\text{for every }
v\in\langle\!\langle q\rangle\!\rangle_F.
}
\tag{5.11}
\]

There is no restriction on z-occurrences, conjugators, orientations,
factor count, or word length. In particular, all four nonprimitive
targets in Theorem 4.1 are stable self-loops by source-first deletion.

## 6. Boundary

Theorem 4.1 excludes target-first primitive-single deletion for exactly

\[
Wz^\delta q^\epsilon z^{-\delta},
\qquad
\delta,\epsilon\in\{+1,-1\}.
\]

The stable closure (5.11) requires:

- a distinct final q-source slot restored to the literal relator q;
- a target of the form \(Wv\) with \(\rho_q(v)=1\);
- the fixed source-slot checkpoint.

It does not close a changed final q-source, a multiplier with nontrivial
q-kill, a different checkpoint, or primitive-pair compression.

Nonprimitivity is not preserved by subsequent AC1 target traffic, so
the four-word obstruction remains a local deletion-order gate rather
than a stable-AC obstruction. AK(3) and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_full_q_traffic_self_loop.py` checks:

- representative products of q-normal-closure factors with z-dependent
  and q-dependent conjugators and both source orientations;
- the q-first images (5.4);
- \(\nu,\nu^{-1}\), the second deletion, and the exact return (5.10);
- all four initial words and their length \(18\);
- both automorphisms and their explicit inverses;
- every word identity and strict length drop in Section 2;
- both exact common edge sets;
- both spanning cycles, connectedness, and absence of cut vertices.
