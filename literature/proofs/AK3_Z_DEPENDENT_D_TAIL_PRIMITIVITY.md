# The first z-dependent D-tail has exactly two primitive sign rows

Date: 2026-07-26

Status: **PROVEN**. Among the eight changed sources

\[
Q_{\eta,\epsilon,\delta}
=
q^\eta W^\epsilon D^\delta,
\qquad
\eta,\epsilon,\delta\in\{+1,-1\},
\]

exactly

\[
\boxed{
qW^{-1}D,
\qquad
qW^{-1}D^{-1}
}
\]

are primitive. Explicit rank-four Whitehead descents take them to basis
letters. The other six words reduce to cyclic words whose Whitehead
graphs contain spanning cycles on all eight signed basis vertices, so
Whitehead's cut-vertex lemma proves them nonprimitive.

This is a free-group primitivity classification, not AC graph search.
It does not yet decide the primitive deletion endpoints of the two
exceptional rows, and it does not prove AK(3) stably AC-trivial.

## 1. The eight exact words

At the fixed source-slot checkpoint, put

\[
\begin{aligned}
A&=\beta(R)=q x^3q^{-1}t^{-4},\\
C&=\beta(xt)q=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{1.1}
\]

The freely reduced changed sources are:

\[
\begin{array}{c|c|c|l}
\eta&\epsilon&\delta&Q_{\eta,\epsilon,\delta}\\
\hline
+&+&+&\texttt{qqxxxQTTTTZqxQtqTzxZ}\\
+&+&-&\texttt{qqxxxQTTTTZqxQtqzXZt}\\
+&-&+&\texttt{TqXQzttttqXXXQTzxZ}\\
+&-&-&\texttt{TqXQzttttqXXXQzXZt}\\
-&+&+&\texttt{xxxQTTTTZqxQtqTzxZ}\\
-&+&-&\texttt{xxxQTTTTZqxQtqzXZt}\\
-&-&+&\texttt{QQTqXQzttttqXXXQTzxZ}\\
-&-&-&\texttt{QQTqXQzttttqXXXQzXZt}
\end{array}
\tag{1.2}
\]

Here the first column uses \(+\) and \(-\) for \(\eta=+1\) and
\(\eta=-1\), respectively.

## 2. Primitive certificate for qW^{-1}D

Each row below lists all four generator images. Define the following
second-kind Whitehead automorphisms:

\[
\begin{array}{c|cccc}
&x&t&z&q\\
\hline
a&Qxq&t&zq&q\\
b&Txt&t&Tzt&Tq\\
c&x&Xt&z&qx\\
d&x&t&z&Zq\\
e&Txt&t&Tzt&qt\\
f&x&t&Xz&Xqx\\
g&Zxz&tz&z&qz\\
h&Tx&t&Tz&qt
\end{array}
\tag{2.1}
\]

Uppercase letters denote inverses. Starting from the cyclic reduction
of \(qW^{-1}D\), apply

\[
\boxed{
a,\ b,\ b,\ b,\ b,\ c,\ d,\ e,\ f,\ g,\ f,\ h.
}
\tag{2.2}
\]

After each map, freely and cyclically reduce and choose a cyclic
orientation. The exact length sequence is

\[
\boxed{
18,15,14,13,12,11,10,9,8,6,4,2,1.
}
\tag{2.3}
\]

The terminal word is \(q^{-1}\). Each map in (2.1) is a Whitehead
automorphism; cyclic conjugation and inversion preserve primitivity.
Reversing the sequence therefore proves \(qW^{-1}D\) primitive.

## 3. Primitive certificate for qW^{-1}D^{-1}

Define:

\[
\begin{array}{c|cccc}
&x&t&z&q\\
\hline
a'&Qxq&Qtq&zq&q\\
b'&txT&t&tzT&qT\\
c'&Qxq&Qt&Qzq&q\\
d'&x&Xtx&zx&Xq\\
e'&Zx&Zt&z&Zq\\
f'&Zxz&Zt&z&Zq\\
g'&Txt&t&Tz&Tq\\
h'&x&Xt&zx&Xq
\end{array}
\tag{3.1}
\]

Apply

\[
\boxed{
a',\ b',\ b',\ b',\ c',\ d',\ d',\ d',\
e',\ f',\ g',\ h',\ h'.
}
\tag{3.2}
\]

The exact length sequence is

\[
\boxed{
16,13,12,11,10,9,8,7,6,5,4,3,2,1.
}
\tag{3.3}
\]

The terminal word is \(z^{-1}\). This proves
\(qW^{-1}D^{-1}\) primitive.

## 4. The six nonprimitive rows

All six begin with the Whitehead automorphism

\[
\alpha:
\quad
x\mapsto q^{-1}xq,
\quad
t\mapsto t,
\quad
z\mapsto zq,
\quad
q\mapsto q.
\tag{4.1}
\]

The row \((+,+,-)\) then uses

\[
\mu:
\quad
x\mapsto txt^{-1},
\quad
t\mapsto t,
\quad
z\mapsto tzt^{-1},
\quad
q\mapsto qt^{-1},
\tag{4.2}
\]

and the row \((-,-,-)\) uses

\[
\nu:
\quad
x\mapsto x,
\quad
t\mapsto x^{-1}tx,
\quad
z\mapsto zx,
\quad
q\mapsto x^{-1}qx.
\tag{4.3}
\]

After free and cyclic reduction, the terminal words and spanning cycles
are:

\[
\begin{array}{c|l|l}
(\eta,\epsilon,\delta)&\text{terminal word}&\text{spanning cycle}\\
\hline
(+,+,+)&
\texttt{TTTTQZxtqTzxZqxxx}&
Q-T-X-t-z-q-Z-x-Q\\
(+,+,-)&
\texttt{TTTTQtZxqzXZqxxx}&
Q-t-T-Z-X-q-z-x-Q\\
(-,+,+)&
\texttt{TTTTQZxtqTzxZQxxx}&
Q-T-X-Z-q-x-z-t-Q\\
(-,+,-)&
\texttt{TTTTQZxtqzXZtQxxx}&
Q-T-X-Z-q-x-z-t-Q\\
(-,-,+)&
\texttt{TTTTQZxtqqzXZtxxx}&
Q-q-T-X-Z-x-z-t-Q\\
(-,-,-)&
\texttt{TTTTQZtqqTxzxZxx}&
Q-T-X-z-t-x-Z-q-Q
\end{array}
\tag{4.4}
\]

The first, third, fourth, and fifth rows use only \(\alpha\). The second
uses \(\mu\alpha\), and the sixth uses \(\nu\alpha\).

For a cyclic word, every adjacent pair \(uv\) contributes the undirected
Whitehead edge from \(u^{-1}\) to \(v\). Each cycle in (4.4) visits all
eight vertices

\[
x,X,t,T,z,Z,q,Q.
\]

Deleting any vertex leaves a path through the other seven. Thus every
terminal graph is connected and has no cut vertex.

Whitehead's cut-vertex lemma says that the graph of a cyclically reduced
primitive word of length greater than one is disconnected or has a cut
vertex. Every terminal word in (4.4) has length \(16\) or \(17\), so
none is primitive. Automorphisms preserve primitivity; the six original
words are therefore nonprimitive.

## 5. Boundary and next lead

The classification decides whether the changed source itself supports a
primitive-single deletion. It does not:

- compute the stable deletion endpoints of
  \(qW^{-1}D^{\pm1}\);
- prove those two primitive branches productive or self-looping;
- classify primitive pairs after an AC product changes one of the
  displayed rows;
- classify longer or interleaved z-dependent source histories.

An unchanged nonprimitive row cannot belong to a primitive pair,
because each component of a basis pair is itself primitive. Thus the
six negative rows are also excluded from direct primitive-pair
deletion. A later AC product can change a row before the pair test and
lies outside this classification.

The two primitive exceptions are the next exact stable-AC candidates.
Their proof certificates are complete, but the whole surviving tuple
must be transported through a chosen straightening before any endpoint
claim is valid.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_z_dependent_d_tail_primitivity.py` checks:

- all eight freely reduced source words;
- every map in (2.1) and (3.1) against the complete rank-four
  second-kind Whitehead list;
- every strict length drop and terminal basis letter;
- the six nonprimitive terminal words;
- the exact common and row-specific reductions;
- every Whitehead graph edge set;
- every displayed spanning cycle, connectedness, and absence of cut
  vertices.
