# Four-cycle quotients close the known seven-direction span

## Status

There is a seventh exact source-coupled homogeneous direction outside the
previous six-dimensional span.  It defeats all six existing mod-two
functionals.  Two four-point permutation quotients supply three further
degree-two functionals, and the resulting nine functionals obstruct every
integer coefficient class in the known seven-direction affine family.

This is not a classification of the full homogeneous syzygy module.  The
period-two lift, the original free-group equation, stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 1. Exact construction of the seventh direction

Write $T=t^{-1}$, and use the forest basis

\[
A=t,\qquad B=X,\qquad G=U^{-1}t^{-1}.
\tag{1}
\]

Start the $L_0$-component with the balanced two-source vector

\[
d_0=e_T+e_{ttttct}.
\tag{2}
\]

Its boundary splits into six paired endpoints.  Exact rewriting in the
complete four-sheet Stallings cover gives the following paths, with letters
read from left to right as successive left actions:

\[
\begin{aligned}
ctcTTTcttcT
  &\xrightarrow{\ gAB\ }ctcTctcT,\\
cTTcttcttttct
  &\xrightarrow{\ BgAbaGaGbaGaGaGbaBgAgABgAgAgAA\ }tcttttct,\\
ctcTTTTcttcttttct
  &\xrightarrow{\ gABgAbaGaGbaGaGaGbaaB\ }ctcTcTctcT,\\
cTTcttcT
  &\xrightarrow{\ BgAbaGbA\ }tcT,\\
ctcTTTTcttcT
  &\xrightarrow{\ gABgAbgAAAAABgA\ }ctcTctcttttct,\\
ctcTTTcttcttttct
  &\xrightarrow{\ gABaG\ }ctcTcTctcttttct.
\end{aligned}
\tag{3}
\]

The remaining components $d_2,d_3,d_4$ are the signed edge flow of (3).
Explicitly, for an edge from $q$ to $q'$, an $A,a,B,b,G,g$ letter
adds respectively

\[
-e_q^{(4)},\quad e_{q'}^{(4)},\quad e_q^{(2)},\quad
-e_{q'}^{(2)},\quad -e_{Tq}^{(3)},\quad e_{Tq'}^{(3)}.
\tag{4}
\]

Equations (2)--(4) define $d=(d_0,0,d_2,d_3,d_4)$ without a radius
cutoff or a search choice.  It has 59 support entries and coefficient

\[
\ell^1(d)=80.
\tag{5}
\]

Direct group-ring expansion gives

\[
\sum_{i=0}^4L_i d_i=0,
\tag{6}
\]

with component-image statistics

\[
(12,12),(0,0),(26,38),(36,50),(41,56).
\tag{7}
\]

Flattening the seven known homogeneous directions over \(\mathbb F_2\)
raises the rank from six to seven.  Thus $d$ is not an integer combination
of the previous directions.

Adding $d$ to the canonical first-layer lift gives

| quantity | value |
|---|---:|
| free residual length | 2012 |
| Schreier-kernel length | 310 |
| degree-two wedge support | 1001 |
| degree-two coefficient \(\ell^1\)-norm | 2016 |

All six earlier mod-two obstruction bits vanish on this residual.

## 2. Two four-cycle quotients

Use the wedge basis

\[
(01,02,03,12,13,23)
\tag{8}
\]

for a four-point permutation module.

First take

\[
c=1,\qquad t=(0\ 1\ 2\ 3).
\tag{9}
\]

Over \(\mathbb F_2\), the induced operator image has rank four.  Its
annihilator is spanned by

\[
\lambda_0=(0,1,0,0,1,0),\qquad
\lambda_1=(1,0,1,1,0,1).
\tag{10}
\]

Second take the genuinely twisted action

\[
c=(1\ 2),\qquad t=(0\ 1\ 2\ 3).
\tag{11}
\]

Its induced operator image has rank five, and

\[
\lambda_2=(1,1,1,1,1,1)
\tag{12}
\]

annihilates every operator column.  The residual from the seventh direction
maps under (11) to

\[
(17,-8,-22,28,-4,14).
\tag{13}
\]

Its value under (12) is $25\equiv1\pmod2$.  Adjoining (13) therefore
raises the operator rank from five to six, proving directly that this
seventh first-layer lift does not survive degree two.

## 3. Exhaustion of the seven-direction integer span

Let $a\in\mathbb Z^7$ be the coefficients of the seven exact homogeneous
directions.  Combine the six previous functionals with (10) and (12):

\[
(\Phi_\infty,\Phi_3,\Phi_4,
  \Psi_{\rm cyc}^{(2)},\Phi_{S_3},\Phi_2,
  \lambda_0,\lambda_1,\lambda_2).
\tag{14}
\]

Every coordinate in (14) is an integer-valued quadratic function of $a$.
Modulo two, every such coordinate has period dividing four in each
variable.  Hence its complete integer coefficient behavior is determined
on \((\mathbb Z/4)^7\).

The certificate determines the quadratic model using

\[
1+2\cdot7+\binom72=36
\tag{15}
\]

exact nonlinear replays at $0,e_i,2e_i,e_i+e_j$.  It independently
validates the model at 28 further points $3e_i$ and $3e_i+e_j$.

Evaluation on all

\[
4^7=16384
\tag{16}
\]

coefficient classes gives no zero obstruction vector.  The deterministic
table hash is

\[
\texttt{0324d0c53b8247d06cb6f932b6859bc8bb319499290183ff71e6e979140353c2}.
\tag{17}
\]

Therefore every integer combination in the known seven-dimensional affine
family is obstructed at degree two.

## 4. Why the four-cycle step is structural

The earlier odd-prime sequence was not a sequence of unrelated invariants.
For the cyclic three-point action, the projected operator image over
\(\mathbb Z\) is exactly

\[
\ker(x-y+z).
\tag{18}
\]

Thus its degree-two defect is one integral quadratic $F(a)=x-y+z$, and

\[
F(a)\equiv0\pmod p\text{ for every prime }p
\quad\Longleftrightarrow\quad
F(a)=0.
\tag{19}
\]

The small coefficient vector

\[
(0,-1,1,1,0,0,1)
\tag{20}
\]

does satisfy $F=0$ exactly while killing the six previous mod-two bits.
It is detected by the first four-cycle action (9).  Intersecting that new
condition with $F=0$ leads to the exact escape

\[
(4,4,-6,2,-12,0,1).
\tag{21}
\]

The twisted action (11) maps it to

\[
(1309,268,138,-108,-1034,80),
\tag{22}
\]

whose coordinate sum is (653\equiv1\pmod2).  The complete mod-four
calculation in Section 3 closes both branches simultaneously.  This
explains why passing from a three-cycle to inequivalent four-cycle
representations is essential; merely trying larger primes in the same
cyclic representation cannot finish the span.

## 5. Frontier

The known homogeneous span is now seven-dimensional, and its complete
integer coefficient lattice is closed by degree-two quotients.  Any actual
degree-two lift must use a homogeneous direction outside this span.

The next global target is not another coefficient search in these seven
directions.  It is a structural description of all orbit-balanced

\[
L_0e_q+L_0e_r
\quad\text{and}\quad
L_1e_q+L_1e_r
\tag{23}
\]

source flows under exact Stallings-cover rewriting, followed by a proof that
the finite-quotient obstruction map has no zero on the resulting full
syzygy module.  The present result proves only the seven-direction slice.

## 6. Certificate

The checker

\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_seven\_direction\_obstruction\_certificate.py}
\]

reconstructs the direction from (2)--(4), verifies (6), checks the
rank-seven independence statement, proves that (10) and (12) annihilate the
appropriate operator images, replays (13), builds and validates the
quadratic model, and exhausts (16) with hash (17).
