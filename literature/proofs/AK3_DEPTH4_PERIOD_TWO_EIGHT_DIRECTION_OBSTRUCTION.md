# A second twisted four-cycle closes the known eight-direction span

## Status

There is an eighth exact source-coupled homogeneous direction outside the
previous seven-dimensional span.  It defeats all nine Result 153 mod-two
functionals.  A new four-point permutation quotient supplies a tenth
functional, and the ten functionals obstruct every integer coefficient
class in the known eight-direction affine family.

This is not a classification of the full homogeneous syzygy module.  The
period-two lift, the original free-group equation, stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 1. Exact eighth direction

Write $T=t^{-1}$ and use the forest basis

\[
A=t,\qquad B=X,\qquad G=U^{-1}t^{-1}.
\tag{1}
\]

Start the $L_0$-component with

\[
h_0=e_T+e_{TTct}.
\tag{2}
\]

Its boundary is orbit-balanced.  Exact rewriting in the complete
four-sheet Stallings cover gives six paths:

\[
\begin{aligned}
cTTcttcTTct
  &\xrightarrow{\ BgAbgBaGbA\ }tcTTct,\\
ctcTTTcttcT
  &\xrightarrow{\ gAB\ }ctcTctcT,\\
ctcTTTTcttcTTct
  &\xrightarrow{\ gABgAbgaB\ }ctcTcTctcT,\\
cTTcttcT
  &\xrightarrow{\ BgAbaGbA\ }tcT,\\
ctcTTTTcttcT
  &\xrightarrow{\ gABgAbgaBgA\ }ctcTctcTTct,\\
ctcTTTcttcTTct
  &\xrightarrow{\ gABaG\ }ctcTcTctcTTct.
\end{aligned}
\tag{3}
\]

Letters act successively from left to right.  As in Result 153, an
$A,a,B,b,G,g$ edge from $q$ to $q'$ contributes

\[
-e_q^{(4)},\quad e_{q'}^{(4)},\quad e_q^{(2)},\quad
-e_{q'}^{(2)},\quad -e_{Tq}^{(3)},\quad e_{Tq'}^{(3)}.
\tag{4}
\]

Equations (2)--(4) define $h=(h_0,0,h_2,h_3,h_4)$ exactly.  It has 35
support entries and coefficient norm

\[
\ell^1(h)=44.
\tag{5}
\]

Direct group-ring expansion proves

\[
\sum_{i=0}^4L_i h_i=0,
\tag{6}
\]

with component-image statistics

\[
(12,12),(0,0),(22,30),(20,26),(24,28).
\tag{7}
\]

Flattening the eight known homogeneous directions over \(\mathbb F_2\)
raises their rank from seven to eight.  Thus $h$ lies outside the previous
integer span.

Adding $h$ to the canonical first-layer lift gives

| quantity | value |
|---|---:|
| free residual length | 1204 |
| Schreier-kernel length | 212 |
| degree-two wedge support | 322 |
| degree-two coefficient \(\ell^1\)-norm | 566 |

All nine Result 153 mod-two obstruction bits vanish.

## 2. The new four-point quotient

Use the ordered wedge basis

\[
(01,02,03,12,13,23).
\tag{8}
\]

Over \(\mathbb F_2\), take

\[
c=(1\ 2),\qquad t=(0\ 1\ 3),
\tag{9}
\]

where point 2 is fixed by $t$.  The induced operator image has rank five,
and the covector

\[
\mu=(1,1,1,1,1,1)
\tag{10}
\]

annihilates every operator column.  The eighth residual maps to

\[
(-8,-7,3,-5,22,-4).
\tag{11}
\]

Its coordinate sum is one.  Thus (10) detects (11), and adjoining the
defect raises the operator rank from five to six.  The eighth first-layer
lift therefore fails at degree two.

## 3. Exhaustion of the eight-direction integer span

Let $a\in\mathbb Z^8$ be the coefficients of the eight exact homogeneous
directions.  Append \(\mu\) to the nine Result 153 functionals.  The
resulting ten-coordinate obstruction is an integer-valued quadratic
function of $a$.  Modulo two, it has period dividing four in every
coefficient.

The certificate determines the quadratic model from

\[
1+2\cdot8+\binom82=45
\tag{12}
\]

exact nonlinear replays at $0,e_i,2e_i,e_i+e_j$.  It validates the model
at 36 further points $3e_i$ and $3e_i+e_j$.

Evaluation on all

\[
4^8=65536
\tag{13}
\]

coefficient classes gives no zero row.  The deterministic table hash is

\[
\texttt{4d0ce8f4039c38823ffe3ec3e94fd7200465f1501b9dfe585406c21a8cd68f4b}.
\tag{14}
\]

Therefore every integer combination in the known eight-dimensional affine
family is obstructed at degree two.

## 4. Exact-quadratic discovery path

The first cyclic three-point test on $h$ gives defect $(-1,-41,6)$ and
signed value 46.  That is again only the integral cyclic quadratic $F$,
not a new prime-specific invariant.  In the eight-direction family, the
Hessian of $F$ still has rank five; its third radical vector is

\[
(1,0,0,0,0,0,0,1),
\tag{15}
\]

so the eighth direction is cyclically equivalent to the negative of the
first known direction.

Solving $F=0$ exactly inside the nine-bit mod-four locus gives, among
others,

\[
(0,0,0,6,-4,0,0,1).
\tag{16}
\]

For the identity four-cycle action from Result 153, the mod-two covector
$(1,0,1,1,0,1)$ has the signed integral lift

\[
\widetilde\lambda=(1,0,-1,1,0,1).
\tag{17}
\]

Direct integer calculation shows that $\widetilde\lambda$ annihilates all
30 projected operator columns.  Define the second integral quadratic by

\[
G(a)=\langle\widetilde\lambda,D_4(a)\rangle,
\tag{18}
\]

where $D_4(a)$ is the identity-four-cycle defect.  This $G$ has value 64
on (16).  When intersecting $G=0$ with $F=0$, the two noncommon radical
directions of $F$ cannot be frozen to a single congruence representative.
The restriction of the Hessian of $G$ to those directions is

\[
\begin{pmatrix}
1024&-1520\\
-1520&2272
\end{pmatrix},
\qquad \det=16128>0.
\tag{19}
\]

Solving that positive-definite binary quadratic exactly produces the
simultaneous zero

\[
(-48,-32,34,10,40,-26,-16,3).
\tag{20}
\]

The new action (9) maps its residual to

\[
(42488,20835,30527,-68819,-15282,-49672),
\tag{21}
\]

whose coordinate sum is $-39923\equiv1\pmod2$.  Thus (9) is not a
repackaging of either integral quadratic.  The complete mod-four table in
Section 3 closes the direct eighth direction, the simultaneous-quadric
escape, and every other coefficient class at once.

## 5. Frontier

The known homogeneous span is now eight-dimensional, and its complete
integer coefficient lattice is degree-two obstructed.  Any actual lift must
use a homogeneous direction outside this span.

The eighth direction already occurs at source-word depth four inside the
balanced $L_0$ two-source family.  The next theoretical target is therefore
the full finite-state syndrome of such balanced pairs under exact
Stallings-cover rewriting, not a deeper search in the eight known
directions.  A global result must show that the ten obstruction quadratics
have no common zero on every generator of the complete source-flow module,
or exhibit a ninth independent zero-syndrome direction.

## 6. Certificate

The checker

\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_eight\_direction\_obstruction\_certificate.py}
\]

reconstructs $h$ from (2)--(4), verifies (6), proves the rank-eight
independence statement, checks that (10) annihilates every operator column,
replays (11), builds and validates the quadratic model, and exhausts (13)
with hash (14).
