# The inverse four-cycle closes the known nine-direction span

## Status

There is a ninth exact source-coupled homogeneous direction outside the
previous eight-dimensional span.  It defeats all ten Result 154 mod-two
functionals.  The inverse-cycle partner of an earlier four-point action
supplies an eleventh functional, and the eleven functionals obstruct every
integer coefficient class in the known nine-direction affine family.

This is not a classification of the full homogeneous syzygy module.  The
period-two lift, the original free-group equation, stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 1. Exact ninth direction

Write $T=t^{-1}$ and use the forest basis

\[
A=t,\qquad B=X,\qquad G=U^{-1}t^{-1}.
\tag{1}
\]

Start the $L_0$-component with

\[
j_0=e_{TT}+e_{tcTct}.
\tag{2}
\]

Its boundary is orbit-balanced.  Exact rewriting in the complete
four-sheet Stallings cover gives

\[
\begin{aligned}
cTTcttcTT
  &\xrightarrow{\ BgAbgABgAA\ }tctcTct,\\
ctcTTTcttcTT
  &\xrightarrow{\ gAB\ }ctcTctcTT,\\
ctcTTTTcttcTT
  &\xrightarrow{\ gABgAbgaB\ }ctcTcTctcTT,\\
cTTcttctcTct
  &\xrightarrow{\ BgAbaGaGbGaGaGbA\ }tcTT,\\
ctcTTTcttctcTct
  &\xrightarrow{\ gAB\ }ctcTctctcTct,\\
ctcTTTTcttctcTct
  &\xrightarrow{\ gABgAbaGaGbGbAB\ }ctcTcTctctcTct.
\end{aligned}
\tag{3}
\]

Letters act successively from left to right.  The signed edge-flow rule
from Results 153--154 reconstructs

\[
j=(j_0,0,j_2,j_3,j_4)
\tag{4}
\]

with 43 support entries and coefficient norm

\[
\ell^1(j)=58.
\tag{5}
\]

Direct group-ring expansion proves

\[
\sum_{i=0}^4L_i j_i=0,
\tag{6}
\]

with component-image statistics

\[
(12,12),(0,0),(24,34),(26,38),(29,38).
\tag{7}
\]

Flattening the nine known homogeneous directions over \(\mathbb F_2\)
raises their rank from eight to nine.  Thus $j$ lies outside the previous
integer span.

Adding $j$ to the canonical first-layer lift gives

| quantity | value |
|---|---:|
| free residual length | 1578 |
| Schreier-kernel length | 262 |
| degree-two wedge support | 535 |
| degree-two coefficient \(\ell^1\)-norm | 1096 |

All ten Result 154 mod-two obstruction bits vanish.

## 2. The inverse four-cycle quotient

Use the ordered wedge basis

\[
(01,02,03,12,13,23).
\tag{8}
\]

Over \(\mathbb F_2\), take

\[
c=(1\ 2),\qquad t=(0\ 3\ 2\ 1).
\tag{9}
\]

The $t$-cycle in (9) is inverse to the cycle in the first twisted
four-point action of Result 153, but the pair with the fixed involution $c$
has a different cokernel syndrome.  Its induced operator image has rank
five, and

\[
\nu=(1,1,1,1,1,1)
\tag{10}
\]

annihilates every operator column.  The ninth residual maps to

\[
(26,-8,-18,-4,-3,4).
\tag{11}
\]

The coordinate sum is $-3\equiv1\pmod2$.  Hence (10) detects (11), and
adjoining the defect raises the operator rank from five to six.

## 3. Exhaustion of the nine-direction integer span

Let $a\in\mathbb Z^9$ be the coefficients of the nine exact homogeneous
directions.  Append \(\nu\) to the ten Result 154 functionals.  The
resulting eleven-coordinate obstruction is an integer-valued quadratic
function of $a$.  Modulo two, it has period dividing four in every
coefficient.

The certificate determines the quadratic model from

\[
1+2\cdot9+\binom92=55
\tag{12}
\]

exact nonlinear replays at $0,e_i,2e_i,e_i+e_j$.  It validates the model
at 45 further points $3e_i$ and $3e_i+e_j$.

Evaluation on all

\[
4^9=262144
\tag{13}
\]

coefficient classes gives no zero row.  The deterministic table hash is

\[
\texttt{117d932505b8cca90d7cedbbfee21edce90a99998620e75d97703f25c4777af9}.
\tag{14}
\]

Therefore every integer combination in the known nine-dimensional affine
family is obstructed at degree two.

## 4. Frontier

The known homogeneous span is now nine-dimensional, and its complete
integer coefficient lattice is degree-two obstructed.  Any actual lift must
use a homogeneous direction outside this span.

The seventh, eighth, and ninth directions all come from balanced two-source
$L_0$ flows of bounded word depth.  Their succession suggests that the
correct global object is the syndrome automaton of the exact Stallings-cover
rewrite: source-pair orbit type, path-flow class, and the eleven quadratic
bits should be tracked together.  The next target is either a finite-state
proof that no zero-syndrome generator survives, or a tenth independent
direction demonstrating that the present quotient family is still
incomplete.

## 5. Certificate

The checker

\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_nine\_direction\_obstruction\_certificate.py}
\]

reconstructs $j$ from (2)--(4), verifies (6), proves the rank-nine
independence statement, checks that (10) annihilates every operator column,
replays (11), builds and validates the quadratic model, and exhausts (13)
with hash (14).
