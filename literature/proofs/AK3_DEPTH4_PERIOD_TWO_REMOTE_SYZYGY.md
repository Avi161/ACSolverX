# A remote lift syzygy escapes two obstructions but meets a four-point one

## Status

For the exact period-two relation-module equation
\[
d+\sum_{i=0}^4L_i x_i=0,
\tag{1}
\]
there is an explicit finitely supported homogeneous syzygy which leaves the
canonical one-hop support and changes the two previously certified
degree-two obstruction bits from \((1,1)\) to \((0,0)\).

Thus the support escape required by the degree-two theorem actually occurs,
and the two earlier wedge functionals are not global obstructions across
the complete affine space of first-layer solutions.

The resulting remote lift is nevertheless obstructed by a new four-point
mod-\(2\) wedge functional. This does not obstruct every remote syzygy and
does not decide whether the period-two witness lifts through
\(F(c,t)/\gamma_3N\).

## 1. The exact homogeneous syzygy

Retain
\[
M=N_{\mathrm{ab}}\cong\mathbb Z[Q/\langle c\rangle],
\qquad
Q=C_2*\mathbb Z,
\]
and let \(e_v\) denote the \(C\)-vertex basis. Put \(T=t^{-1}\).

Define \(w=(w_0,\ldots,w_4)\) by
\[
\begin{aligned}
w_0={}&e_{cT}-e_{cTT}+2e_{cTTct},\\
w_1={}&0,\\
w_2={}&2e_1+3e_{cT}-2e_{cTT}+e_{cTct}+2e_{cTTct},\\
w_3={}&2e_{TT}+e_{TTcT}+2e_{TTct}-e_{TTcTT}
+e_{TTcTct}\\
&+e_{TTcTTct}+2e_{TTctcT}-e_{TTctcTcT},\\
w_4={}&-3e_T-e_{TcT}+e_{TcTT}-e_{TcTct}-e_{TcTTct}\\
&-2e_{TctcT}+e_{TctcTcT}.
\end{aligned}
\tag{2}
\]
It has \(23\) nonzero basis entries and coefficient \(\ell^1\)-norm \(35\).

Exact expansion under the five lifting operators gives
\[
\sum_{i=0}^4L_iw_i=0.
\tag{3}
\]
The individual images have support size and coefficient norm
\[
\bigl(|L_iw_i|,\|L_iw_i\|_1\bigr)
=
(15,20),(0,0),(10,20),(16,22),(14,20).
\tag{4}
\]
All \(62\) signed output coefficients in (4) cancel after collection.

## 2. Exact support escape

Let \(\mathcal V\) be the \(242\)-variable one-hop set from the support
escape theorem. Exactly four entries of (2) lie outside \(\mathcal V\):
\[
(2,cTT),\qquad
(3,TTcTT),\qquad
(3,TTctcTcT),\qquad
(4,TcTT).
\tag{5}
\]

Let \(x^{00}\) be the eight-entry first-layer solution
\[
\begin{aligned}
x^{00}_0&=2e_{cT}-2e_{cTTct}-2e_{cTTctt},\\
x^{00}_1&=0,\\
x^{00}_2&=-2e_{cTct}-2e_{cTctt},\\
x^{00}_3&=-2e_1-e_{TTct},\\
x^{00}_4&=e_{Tct}.
\end{aligned}
\]
By (3),
\[
x^{\mathrm{rem}}=x^{00}+w
\tag{6}
\]
is another exact integral solution of (1).

Lift (6) to products of the free kernel generators
\[
\widetilde v c^2\widetilde v^{-1},
\]
recompute the full nonlinear free-group recurrence, and compare its final
row with the correspondingly conjugated target. The residual has
\[
\begin{array}{c|c}
\text{free-group length}&476\\
\text{Schreier-kernel length}&124\\
\text{relation-module vector}&0\\
\text{degree-two wedge support}&170\\
\text{degree-two coefficient sum}&8.
\end{array}
\tag{7}
\]

The full infinite wedge augmentation is therefore zero modulo \(2\).
Under the earlier three-point quotient, the three wedge coordinates have
parities
\[
(0,1,1),
\]
whose sum is also zero. Hence
\[
\bigl(\Phi_\infty,\Phi_3\bigr)(x^{\mathrm{rem}})=(0,0).
\tag{8}
\]

This proves that neither \(\Phi_\infty\) nor \(\Phi_3\) is constant on the
global affine solution space of (1). The support-escape conclusion was
sharp: leaving \(\mathcal V\) can remove both local obstruction bits.

## 3. A four-point separator

Let \(Q\) act on
\[
\Omega_4=\{0,1,2,3\}
\]
by
\[
c=(2\ 3),\qquad
t=(0\ 1\ 2),
\tag{9}
\]
with base point \(0\), fixed by \(c\). This gives
\[
M\otimes\mathbb F_2\longrightarrow\mathbb F_2[\Omega_4],
\qquad
e_{q\langle c\rangle}\longmapsto e_{q0}.
\tag{10}
\]

Order the six wedge coordinates by
\[
(01),(02),(03),(12),(13),(23).
\]
The exact integral image of the degree-two residual in (7) is
\[
(-5,4,-36,17,15,-18).
\tag{11}
\]
Modulo \(2\), (11) is
\[
(1,0,0,1,1,0),
\]
whose coordinate sum is \(1\).

Define
\[
\Phi_4:\Lambda^2\mathbb F_2[\Omega_4]\to\mathbb F_2
\]
to be the sum of the six coordinates. The \(Q\)-action permutes unordered
pairs, so \(\Phi_4\) is invariant. Since every \(L_i\) has group-ring
augmentation zero,
\[
\Phi_4(L_i y)=0
\tag{12}
\]
for every possible second-layer correction \(y\).

Thus (11) proves
\[
\Phi_4(x^{\mathrm{rem}})=1.
\tag{13}
\]
As an independent linear-algebra audit, the five induced operator maps on
\(\Lambda^2\mathbb F_2[\Omega_4]\) have combined rank \(5\) in dimension
\(6\), while adjoining (11) raises the rank to \(6\).

Therefore this particular remote first-layer lift does not extend through
\(F(c,t)/\gamma_3N\).

## 4. Consequence

The remote vector (2) proves that nonlocal homogeneous cancellation is real
and can defeat a fixed finite list of degree-two functionals. The
four-point action proves that this first escape is still insufficient.

The new exact frontier is:

1. find another finitely supported homogeneous syzygy whose addition also
   kills \(\Phi_4\), then solve the full degree-two equation; or
2. prove that some family of finite \(Q\)-set wedge functionals detects
   every compactly supported first-layer solution.

The binomial-forest theorem further forces every such syzygy to involve
\(L_0\) or \(L_1\); pure \(L_2,L_3,L_4\) cycles do not exist.

## 5. Exact certificate

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_remote\_syzygy\_certificate.py}
\]
verifies (2)--(8), constructs the four-point action (9), reproduces
(11), and checks the rank jump \(5\to6\).

The result concerns one explicit remote lift. The full lifting problem and
the original depth-four Andrews--Curtis class remain open.
