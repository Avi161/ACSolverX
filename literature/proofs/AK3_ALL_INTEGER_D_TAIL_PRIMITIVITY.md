# Complete primitivity classification for all integer D-tails

Date: 2026-07-26

Status: **PROVEN**. For

\[
Q_{\eta,\epsilon,k}
=
q^\eta W^\epsilon D^k,
\qquad
\eta,\epsilon\in\{+1,-1\},
\quad
k\in\mathbb Z,
\]

the exact criterion is

\[
\boxed{
Q_{\eta,\epsilon,k}\text{ is primitive}
\quad\Longleftrightarrow\quad
k=0
\ \text{or}\
(\eta,\epsilon)=(+1,-1).
}
\tag{0.1}
\]

The positive direction uses explicit free-group coordinates. The
negative direction uses one Whitehead automorphism and five symbolic
spanning cycles, so there is no power bound and no AC graph search.

## 1. Notation

At the fixed rank-four checkpoint,

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
C&=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{1.1}
\]

Uppercase letters in displayed words denote inverses.

## 2. The two positive mechanisms

### 2.1. Every zero-power row is primitive

If \(k=0\), then

\[
Q_{\eta,\epsilon,0}=q^\eta W^\epsilon.
\]

Each such word contains exactly one occurrence of \(z^{\pm1}\). Write
it as

\[
Lz^\delta R,
\qquad
\delta\in\{+1,-1\},
\qquad
L,R\in F(x,t,q).
\]

The map fixing \(x,t,q\) and sending

\[
z\mapsto Lz^\delta R
\]

is an automorphism. For \(\delta=+1\), its inverse sends

\[
z\mapsto L^{-1}zR^{-1};
\]

for \(\delta=-1\), its inverse sends

\[
z\mapsto Rz^{-1}L.
\]

Thus all four zero-power rows are primitive. This is also the
unique-z coordinate used in Result 44.

### 2.2. The positive inverse-W row is primitive for every k

Put

\[
S=Wq^{-1}.
\tag{2.1}
\]

The based primitive-pair theorem in
`AK3_QW_D_POWER_TAIL_COMPRESSION_MERGE.md` supplies an automorphism
\(\theta\) with

\[
\theta(S)=z^{-1},
\qquad
\theta(D)=t^{-1}.
\tag{2.2}
\]

For \((\eta,\epsilon)=(+1,-1)\),

\[
Q_{+,-,k}
=
qW^{-1}D^k
=
S^{-1}D^k,
\]

so

\[
\theta(Q_{+,-,k})=zt^{-k}.
\]

The triangular shear

\[
z\mapsto zt^k
\]

fixing \(x,t,q\) sends this word to z. Hence
\(Q_{+,-,k}\) is primitive for every integer k.

## 3. One common map for every negative row

Consider the second-kind Whitehead automorphism

\[
\alpha:
\quad
x\mapsto q^{-1}xq,
\qquad
t\mapsto t,
\qquad
z\mapsto zq,
\qquad
q\mapsto q.
\tag{3.1}
\]

Its inverse is

\[
x\mapsto qxq^{-1},
\qquad
t\mapsto t,
\qquad
z\mapsto zq^{-1},
\qquad
q\mapsto q.
\tag{3.2}
\]

Direct substitution followed by free and cyclic reduction gives, for
the three remaining sign orientations,

\[
\alpha(Q_{\eta,\epsilon,k})
\sim_{\mathrm{cyc}}
B_{\eta,\epsilon}D^k,
\tag{3.3}
\]

where

\[
\begin{array}{c|c}
(\eta,\epsilon)&B_{\eta,\epsilon}\\
\hline
(+,+)&\texttt{qxxxTTTTQZxtq}\\
(-,+)&\texttt{QxxxTTTTQZxtq}\\
(-,-)&\texttt{QQTXzqttttXXX}
\end{array}
\tag{3.4}
\]

For \(k\ne0\), every word on the right of (3.3) is freely and
cyclically reduced and has length

\[
13+4|k|>1.
\tag{3.5}
\]

## 4. Five spanning cycles cover all nonzero powers

For a cyclic word, each adjacent pair \(uv\) contributes the
undirected Whitehead edge from \(u^{-1}\) to v. For \(|k|=1\), the
following cycles occur in the Whitehead graphs of the words in (3.3):

\[
\begin{array}{c|c|l}
(\eta,\epsilon)&\operatorname{sign}(k)&
\text{spanning cycle}\\
\hline
(+,+)&-&x-Q-z-t-T-q-Z-X-x\\
(+,+)&+&x-Q-T-X-t-z-q-Z-x\\
(-,+)&\pm&x-X-Z-q-T-Q-t-z-x\\
(-,-)&-&x-X-Z-q-Q-T-t-z-x\\
(-,-)&+&x-T-X-Z-q-Q-t-z-x
\end{array}
\tag{4.1}
\]

Every displayed cycle visits all eight signed basis vertices

\[
x,X,t,T,z,Z,q,Q.
\]

For \(|k|>1\), repeat the same \(D\) or \(D^{-1}\) block. Every edge
present for \(|k|=1\) remains present:

- all internal B-edges remain;
- the B-to-first-D seam remains;
- all internal D-edges remain;
- the last-D-to-B cyclic seam remains.

The repetitions only add D-to-D seam edges. Therefore the appropriate
spanning cycle in (4.1) remains a subgraph for every nonzero k.

Deleting any vertex from a spanning cycle leaves a path through the
other seven vertices. Hence every graph is connected and has no cut
vertex.

Whitehead's cut-vertex lemma says that the graph of a cyclically
reduced primitive word of length greater than one is disconnected or
has a cut vertex. Equations (3.5) and (4.1) therefore prove every word
in (3.3) nonprimitive. Since \(\alpha\) is an automorphism, the three
original sign rows are nonprimitive for every \(k\ne0\).

Combining Sections 2--4 proves (0.1).

## 5. Left/right D-splits and primitive-pair consequence

For arbitrary \(a,b\in\mathbb Z\),

\[
D^{-a}
\left(
D^a q^\eta W^\epsilon D^b
\right)
D^a
=
q^\eta W^\epsilon D^{a+b}.
\tag{5.1}
\]

Conjugacy preserves primitivity. Therefore the full split-tail
criterion is

\[
\boxed{
D^a q^\eta W^\epsilon D^b
\text{ is primitive}
\quad\Longleftrightarrow\quad
a+b=0
\ \text{or}\
(\eta,\epsilon)=(+1,-1).
}
\tag{5.2}
\]

Thus the classification includes all D-only left/right traffic around
one signed qW block.

If two conjugacy classes form a primitive pair, an automorphism sends
each component to a conjugate of a distinct basis letter. In
particular, each component is individually primitive.

Consequently, every negative row in Sections 3--4 is automatically
excluded from any direct primitive pair with A, W, D, or any other
unchanged relator. No separate pair census is needed.

This does not exclude a one-edge creation branch: an AC2 product can
first replace a negative row or another survivor by a different word,
which must then be tested for primitivity or pair primitivity.

## 6. Scope

The theorem classifies exactly one \(W^{\pm1}\) block followed by a
pure integer D-power, including arbitrary D-only left/right splits. It
does not classify:

- an AC2 product changing the Q-row or another survivor before
  deletion;
- histories with another \(Wq^{-1}\)-type block;
- traffic changing A, W, or D;
- left/right traffic outside the retained D-power subgroup.

AK(3) and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_all_integer_d_tail_primitivity.py` checks:

- explicit unique-z coordinate maps and inverses for all four
  zero-power rows;
- the based \((S,D)\) coordinate and triangular shears at positive,
  negative, and zero sample powers;
- the exact common automorphism and all three boundary blocks in
  (3.4);
- free/cyclic reduction and the length formula (3.5);
- every edge of all five spanning cycles;
- connectedness and absence of cut vertices;
- symbolic edge persistence under repeated positive and negative
  D-blocks.
- the split-tail identity (5.1) for all sign rows at mixed-sign
  samples.

The all-integer conclusion is the symbolic argument of Sections 2 and
4; the finite samples exercise the literal implementation of those
identities.
