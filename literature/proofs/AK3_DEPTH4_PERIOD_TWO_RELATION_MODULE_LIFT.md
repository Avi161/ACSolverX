# The exact period-two witness lifts through its relation module

## Status

The exact solution of the hardest depth-four recurrence in
\[
Q=\langle c,t\mid c^2=1\rangle=C_2*\mathbb Z
\]
lifts to a solution in the larger quotient
\[
F(c,t)/[N,N],
\qquad
N=\ker(F(c,t)\to Q)=\langle\!\langle c^2\rangle\!\rangle.
\]

Equivalently, the full first relation-module obstruction to lifting this
specific quotient witness vanishes. The corrected residual is a nontrivial
freely reduced word of length \(82\) in \([N,N]\), so this is not a solution
in \(F(c,t)\). The original depth-four class remains open.

## 1. The literal lift and its defect

Retain the exact quotient conjugators
\[
h_0=ct^{-2}ct^3,\qquad h_1=1,\qquad
h_2=ct^{-1}ct^3,\qquad h_3=t,
\tag{1}
\]
but now read them in the free group
\[
F=F(c,t).
\]
Use the original, unreduced source rows
\[
\begin{aligned}
A={}&t^{-1}c^4t^{-1}c^3t^{-1}c^4t^{-1}c^{-1}tc^{-4}tc^{-1},\\
B={}&t^{-1}c^4t^{-1}c^4t^{-1}c^{-1}tc^{-3}tc^{-1}.
\end{aligned}
\tag{2}
\]
Apply the recurrence
\[
\begin{aligned}
R&=Ah_0B^{-1}h_0^{-1},\\
S&=Bh_1R^{-1}h_1^{-1},\\
U&=Rh_2S^{-1}h_2^{-1},\\
Z&=U^{-1}h_3Sh_3^{-1}.
\end{aligned}
\tag{3}
\]
Direct free reduction gives
\[
\bigl(|R|,|S|,|U|,|Z|\bigr)=(49,63,116,177).
\tag{4}
\]
Modulo \(c^2=1\), the final word is \(t\). Hence
\[
D=Zt^{-1}\in N.
\tag{5}
\]
The word \(D\) is freely reduced of length \(178\).

## 2. The exact relation module

Kurosh rewriting for the free-product quotient gives
\[
M=N_{\mathrm{ab}}
\cong \mathbb Z[Q/\langle c\rangle].
\tag{6}
\]
For a \(C\)-vertex \(v=q\langle c\rangle\), write
\[
e_v=
\left[\widetilde q\,c^2\,\widetilde q^{-1}\right]\in M.
\tag{7}
\]
This is independent of replacing \(q\) by \(qc\), and left conjugation by
\(Q\) permutes the basis:
\[
g e_v=e_{gv}.
\]

Let \(T=t^{-1}\) in the vertex labels below. Exact Schreier rewriting of
(5) gives the following \(21\)-term vector:
\[
\begin{aligned}
d=[D]={}&
-4e_1-2e_t-2e_{cT}-e_{ct}
+2e_{Tct}+2e_{Tctt}+2e_{cTct}-5e_{ctcT}\\
&+2e_{cTTct}+2e_{cTctt}
-4e_{ctcTT}-2e_{ctcTTT}
-2e_{ctcTcT}-2e_{ctcTct}\\
&+2e_{ctcTTTct}+2e_{ctcTTctt}
+2e_{ctcTcTct}+2e_{ctcTTTTct}\\
&+2e_{ctcTcTctt}
+2e_{ctcTcTcTct}
+2e_{ctcTcTcTctt}.
\end{aligned}
\tag{8}
\]
Its coefficient sum is zero and its coefficient \(\ell^1\)-norm is \(48\).

## 3. Exact variation calculus

Work in the extension \(M\rtimes Q=F/[N,N]\), with \(M\) written
additively as a left \(Q\)-module. For elements with fixed \(Q\)-images,
\[
\delta(WV)=\delta W+\overline W\,\delta V,
\qquad
\delta(W^{-1})=-\overline W^{-1}\delta W.
\tag{9}
\]

Correct the four conjugators on the left:
\[
h_i\longmapsto n_i h_i,\qquad [n_i]=x_i\in M.
\tag{10}
\]
Also allow the target conjugator \(n_4\), so the target becomes
\[
n_4tn_4^{-1}
\]
and has module coordinate \((1-t)x_4\).

All unbarred row symbols in the formulas below denote their fixed images in
\(Q\). Since \(h_1=1\), exact application of (9) to (3) gives
\[
\delta R=(A-R)x_0,
\tag{11}
\]
\[
\delta S=-S(A-R)x_0+(B-S)x_1,
\tag{12}
\]
and
\[
\begin{aligned}
\delta Z={}&
-U^{-1}\delta R
+(h_2+U^{-1}h_3)\delta S\\
&+(1-X)x_2+(U^{-1}-t)x_3,
\end{aligned}
\tag{13}
\]
where
\[
X=h_2Sh_2^{-1},\qquad U=RX^{-1},\qquad U^{-1}Y=t.
\]

Therefore the exact lifting equation in \(M\) is
\[
d+L_0x_0+L_1x_1+L_2x_2+L_3x_3+L_4x_4=0,
\tag{14}
\]
with
\[
\begin{aligned}
L_0&=-U^{-1}(A-R)
     -(h_2+U^{-1}h_3)S(A-R),\\
L_1&=(h_2+U^{-1}h_3)(B-S),\\
L_2&=1-X,\\
L_3&=U^{-1}-t,\\
L_4&=t-1.
\end{aligned}
\tag{15}
\]
These are exact operators in \(\mathbb Z[Q]\), not a heuristic
linearization. Their reduced support sizes are respectively
\[
(6,4,2,2,2),
\tag{16}
\]
and every coefficient augmentation is zero.

## 4. An eight-term integral correction

The following finitely supported integral vectors solve (14):
\[
\begin{aligned}
x_0&=2e_{cT}-2e_{cTTct}-2e_{cTTctt},\\
x_1&=0,\\
x_2&=-2e_{cTct}-2e_{cTctt},\\
x_3&=-2e_1-e_{TTct},\\
x_4&=e_{Tct}.
\end{aligned}
\tag{17}
\]
Indeed, direct expansion in the basis (7) gives
\[
d+L_0x_0+L_2x_2+L_3x_3+L_4x_4=0.
\tag{18}
\]
The correction has eight nonzero basis entries and total coefficient
\(\ell^1\)-norm \(14\).

For a direct group-level realization, choose the lift
\[
r_v=\widetilde v\,c^2\,\widetilde v^{-1}\in N
\]
of every \(e_v\), form \(n_i\) as the ordered product of the powers
specified in (17), and replace \(h_i\) by \(n_i h_i\). Recompute (3) in
the free group and call its final row \(Z'\). Exact reduction verifies
\[
\left[
Z'\left(n_4tn_4^{-1}\right)^{-1}
\right]=0\in M.
\tag{19}
\]
Thus the residual in (19) belongs to \([N,N]\). It is freely reduced of
length \(82\), so these particular corrections do not yet solve the
free-group equation.

## 5. Consequence

The period-two witness is not merely soluble modulo \(c^2=1\). It survives
the complete relation module of that quotient:
\[
\boxed{\text{the witness lifts through }F/[N,N].}
\]

Consequently no obstruction depending only on the abelianized
\(c^2\)-relation kernel can close the hardest depth-four class. The next
honest layer is the derived defect
\[
[N,N]/[[N,N],N],
\]
or an equivalent nonabelian crossed-module invariant retaining commutators
between distinct \(C\)-vertex generators.

## 6. Exact certificate

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_lift\_certificate.py}
\]
replays the free reductions (3)--(5), the Schreier vector (8), all five
operators (15), the identity (18), and the direct corrected recurrence
(19), using integer dictionaries only.

This theorem is a blindness result and a sharper reduction, not a proof of
the Andrews--Curtis conjecture or of this depth-four class.
