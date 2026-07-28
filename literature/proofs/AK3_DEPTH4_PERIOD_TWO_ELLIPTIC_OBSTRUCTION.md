# The elliptic intermediate branch is impossible in the period-two quotient

## Status

This note proves an exact obstruction for the hardest unresolved depth-four
Andrews--Curtis recurrence after imposing the relation \(c^2=1\).

If the second intermediate row \(S\) is elliptic in the Bass--Serre tree of
\[
G=\langle c,t\mid c^2=1\rangle=C_2*\mathbb Z,
\]
then the first two recurrence equations already have no solution. Therefore
every solution of the full period-two recurrence, if one exists, must have
hyperbolic \(S\).

This does not decide the remaining hyperbolic branch and does not close the
original free-group depth-four class.

## 1. Fixed rows and the backward equations

Let
\[
H=\ker(G\longrightarrow C_2)
\]
be the even-\(c\)-parity subgroup. The fixed source rows in this quotient are
\[
A=t^{-2}ct^{-2}ct^2c,\qquad B=t^{-3}ctctc.
\tag{1}
\]

The first two equations of the exact backward class system are
\[
R^{-1}A\in\operatorname{Cl}_H(B),\qquad
S^{-1}B\in\operatorname{Cl}_H(R),
\tag{2}
\]
where \(\operatorname{Cl}_H(w)\) denotes the \(H\)-conjugacy class of \(w\).

The parity and exponent data imply that an elliptic \(S\) is
\(H\)-conjugate to \(c\). In particular \(S^2=1\).

## 2. Exact elimination of the elliptic row

### Lemma

Equations (2) admit a solution with elliptic \(S\) if and only if
\[
A\in
\operatorname{Cl}_H(c)\,
\operatorname{Cl}_H(B)\,
\operatorname{Cl}_H(B).
\tag{3}
\]
The three conjugates on the right of (3) are independent.

### Proof

Suppose (2) holds. Write
\[
B_0=R^{-1}A\in\operatorname{Cl}_H(B)
\]
and choose \(h\in H\) such that
\[
S^{-1}B=hRh^{-1}.
\]
Then
\[
\begin{aligned}
A
 &=RB_0\\
 &=\bigl(h^{-1}S^{-1}h\bigr)
   \bigl(h^{-1}Bh\bigr)B_0.
\end{aligned}
\]
The first factor lies in \(\operatorname{Cl}_H(c)\), and the final two lie
in \(\operatorname{Cl}_H(B)\), proving necessity.

Conversely, suppose
\[
A=C B_1 B_0
\]
with \(C\in\operatorname{Cl}_H(c)\) and
\(B_0,B_1\in\operatorname{Cl}_H(B)\). Choose \(h\in H\) with
\[
B_1=h^{-1}Bh
\]
and set
\[
S=hC^{-1}h^{-1},\qquad R=CB_1.
\]
Because \(C^2=1\), the row \(S\) is elliptic and
\[
R^{-1}A=B_0,\qquad
hRh^{-1}=S^{-1}B.
\]
Thus (2) holds. Since \(C,B_0,B_1\) were chosen independently, no hidden
conjugator correlation remains in (3). \(\square\)

## 3. A projective quaternion representation

Use unit quaternions modulo their central signs:
\[
PSU(2)=SU(2)/\{\pm1\}\cong SO(3).
\]
Put \(r=\sqrt2/2\), and choose quaternion lifts
\[
C=(0,1,0,0),\qquad
T=\left(r,\frac12,\frac12,0\right).
\tag{4}
\]
Both are unit quaternions and \(C^2=-1\). Hence
\[
\rho(c)=[C],\qquad \rho(t)=[T]
\tag{5}
\]
defines a homomorphism \(G\to PSU(2)\): the projective image of \(C\) has
order two.

Exact quaternion multiplication gives
\[
\widetilde\rho(B)=(-1,0,0,0)
\tag{6}
\]
and
\[
\widetilde\rho(A)=(r,0,0,-r).
\tag{7}
\]
Thus \(\rho(B)=1\) in \(PSU(2)\).

For a projective unit quaternion, the square of the scalar coordinate is
independent of the choice of lift and is invariant under conjugacy.
Every conjugate of \(\rho(c)\) is a half-turn and has scalar square \(0\).
Equation (7), however, gives
\[
\operatorname{scal}(\widetilde\rho(A))^2=\frac12.
\tag{8}
\]
Therefore \(\rho(A)\) is not conjugate to \(\rho(c)\).

## 4. Obstruction theorem

If (3) held, applying \(\rho\) and using \(\rho(B)=1\) would give
\[
\rho(A)\in\operatorname{Cl}_{PSU(2)}(\rho(c)).
\]
This contradicts (8). Hence (3) is impossible, so the first two backward
equations admit no solution with elliptic \(S\).

Consequently every solution of the complete period-two recurrence must lie
in the hyperbolic-\(S\) branch. In the Bass--Serre notation this leaves only
\[
\ell_T(S)\equiv2\pmod4,\qquad \ell_T(S)>0.
\]

## 5. Exact certificate

The project-local checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_elliptic\_certificate.py}
\]
performs all quaternion arithmetic in
\(\mathbb Q(\sqrt2)\), verifies \(C^2=-1\), verifies that \(T\) is unit,
and reproduces (6)--(8) without floating-point arithmetic.

The conclusion is deliberately limited: the elliptic branch is closed; the
hyperbolic period-two equation remains open.
