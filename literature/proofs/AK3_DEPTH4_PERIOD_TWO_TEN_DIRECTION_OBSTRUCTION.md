# A five-cycle quotient closes the known ten-direction span

## Status

There is a tenth exact source-coupled homogeneous direction outside the
previous nine-dimensional span.  It defeats all eleven Result 155 mod-two
functionals.  A five-point cyclic action supplies two further functionals,
and the resulting thirteen functionals obstruct every integer coefficient
class in the known ten-direction affine family.

This is not a classification of the full homogeneous syzygy module.  The
period-two lift, the original free-group equation, stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 1. Exact tenth direction

Write $T=t^{-1}$ and use the forest basis

\[
A=t,\qquad B=X,\qquad G=U^{-1}t^{-1}.
\tag{1}
\]

Start the $L_0$-component with

\[
k_0=e_{cT}+e_{TcTTT}.
\tag{2}
\]

Its orbit-balanced boundary has the exact Stallings-cover paths

\[
\begin{aligned}
cTTct&\xrightarrow{\ BgAb\ }1,\\
ctcTTTTct&\xrightarrow{\ gABgAbaGaGaGbaBgA\ }ctcTctcTcTTT,\\
ctcTTTcttcTcTTT&\xrightarrow{\ gABaG\ }ctcTcTctcTcTTT,\\
ctcTTTct&\xrightarrow{\ gAB\ }ctcT,\\
cTTcttcTcTTT&\xrightarrow{\ BgAbgAgAB\ }ctcTcT,\\
ctcTTTTcttcTcTTT&\xrightarrow{\ gABgAbgAgABaGbaGaGbA\ }tcTcTTT.
\end{aligned}
\tag{3}
\]

The signed edge-flow rule from Results 153--155 reconstructs
$k=(k_0,0,k_2,k_3,k_4)$ with 43 support entries and

\[
\ell^1(k)=56.
\tag{4}
\]

Direct group-ring expansion proves

\[
\sum_{i=0}^4L_i k_i=0,
\tag{5}
\]

with component-image statistics

\[
(12,12),(0,0),(22,32),(28,36),(32,40).
\tag{6}
\]

Flattening the ten known directions over \(\mathbb F_2\) raises their rank
from nine to ten.  Adding $k$ to the canonical lift gives

| quantity | value |
|---|---:|
| free residual length | 1208 |
| Schreier-kernel length | 204 |
| degree-two wedge support | 640 |
| degree-two coefficient \(\ell^1\)-norm | 1116 |

All eleven Result 155 mod-two obstruction bits vanish.

## 2. The five-cycle quotient

On five points, take

\[
c=1,\qquad t=(0\ 1\ 2\ 3\ 4).
\tag{7}
\]

Use the wedge basis

\[
(01,02,03,04,12,13,14,23,24,34).
\tag{8}
\]

The induced operator image over \(\mathbb F_2\) has rank eight.  Its
two-dimensional annihilator has basis

\[
\begin{aligned}
\omega_0&=(0,1,1,0,0,1,1,0,1,0),\\
\omega_1&=(1,0,0,1,1,0,0,1,0,1).
\end{aligned}
\tag{9}
\]

The tenth residual maps to

\[
(-6,9,0,-14,0,-2,12,2,-4,1).
\tag{10}
\]

Both covectors in (9) take value one modulo two on (10).  Adjoining the
defect raises the operator rank from eight to nine, so the tenth lift fails
at degree two.

## 3. Exhaustion of the ten-direction integer span

Append (9) to the eleven Result 155 functionals.  The resulting
thirteen-coordinate obstruction is an integer-valued quadratic function of
the ten direction coefficients, with period dividing four modulo two.

The certificate determines the quadratic model from

\[
1+2\cdot10+\binom{10}{2}=66
\tag{11}
\]

exact nonlinear replays and validates it at 55 further points.  Evaluation
on all

\[
4^{10}=1048576
\tag{12}
\]

coefficient classes gives no zero row.  The deterministic table hash is

\[
\texttt{9c695ef0446c0033cc193f0e6f562633128b09bb4664e6a15d99f53e3f011707}.
\tag{13}
\]

Therefore every integer combination in the known ten-dimensional affine
family is obstructed at degree two.

## 4. Frontier

The known homogeneous span is now ten-dimensional.  Its complete integer
coefficient lattice is closed by thirteen mod-two functionals drawn from
actions on at most five points.

The next target is the full syndrome automaton of balanced two-source
$L_0$ flows.  A global theorem must either show that these thirteen
quadratics have no common zero on every exact source-flow generator or
produce an eleventh independent zero-syndrome direction.  The present
result proves only the ten-direction slice.

## 5. Certificate

The checker

\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_ten\_direction\_obstruction\_certificate.py}
\]

reconstructs $k$ from (2)--(3), verifies (5), proves rank ten, checks the
two cokernel covectors and rank jump, builds and validates the quadratic
model, and exhausts (12) with hash (13).
