# Degree-two lifting forces support escape

## Status

Fix the exact period-two witness and its relation-module lifting equation
\[
d+\sum_{i=0}^4L_i x_i=0
\qquad
\text{in }
M=N_{\mathrm{ab}}\cong\mathbb Z[Q/\langle c\rangle].
\tag{1}
\]
There is a canonical finite one-hop support for (1): allow a variable basis
element precisely when one term of its image under \(L_i\) lands on the
support of the original defect \(d\).

This note proves that every solution supported in that finite set is
obstructed in degree two. Consequently, any lift of the exact period-two
witness through
\[
F(c,t)/\gamma_3N
\]
must use a first-layer relation-module correction outside the one-hop
support.

This is a support-escape theorem, not a global impossibility theorem. A
solution with more distant first-layer support, a different period-two
witness, or a direct free-group solution remains possible.

## 1. The one-hop module system

Let
\[
Q=\langle c,t\mid c^2=1\rangle,\qquad
N=\ker(F(c,t)\to Q).
\]
Write \(e_v\) for the basis of
\[
M=N_{\mathrm{ab}}\cong\mathbb Z[Q/\langle c\rangle]
\]
indexed by \(C\)-vertices.

The literal lift of the quotient witness has a defect
\[
d\in M
\]
with \(21\) nonzero basis coefficients. The five exact lifting operators
have support sizes
\[
\bigl(|L_0|,|L_1|,|L_2|,|L_3|,|L_4|\bigr)
=(6,4,2,2,2).
\tag{2}
\]
Every \(L_i\) has group-ring augmentation zero.

Define the one-hop variable set
\[
\mathcal V=
\left\{
(i,g^{-1}v):
v\in\operatorname{supp}(d),\
g\in\operatorname{supp}(L_i)
\right\}.
\tag{3}
\]
After identifying repeated pairs, (3) contains exactly \(242\) variables.
Expanding their images in the \(C\)-vertex basis and including every output
row gives an integral matrix
\[
\mathcal A\in M_{449\times242}(\mathbb Z)
\tag{4}
\]
with \(880\) nonzero entries.

Exact row reduction gives
\[
\operatorname{rank}_{\mathbb F_p}(\mathcal A)=240
\qquad(p=2,3,5).
\tag{5}
\]
There is an integral particular solution \(x^{00}\), together with two
integral homogeneous solutions \(u_0,u_1\) whose reductions modulo \(2\)
are independent. Hence the mod-\(2\) kernel has dimension exactly two, and
every integral solution of (1) supported in \(\mathcal V\) belongs to one
of the four parity classes
\[
x^{ab}=x^{00}+a u_0+b u_1,
\qquad
(a,b)\in\mathbb F_2^2.
\tag{6}
\]

The rank claim is certificate-friendly: the mod-\(2\) rank \(240\) gives
the lower bound, while the two displayed independent null vectors give the
upper bound. The mod-\(3\) and mod-\(5\) ranks are independent audits.

## 2. Two global degree-two functionals

Put
\[
W=\gamma_2N/\gamma_3N\cong\Lambda^2M.
\]
Second-layer corrections \(y_i\in W\) change a corrected residual by
\[
\sum_{i=0}^4L_i y_i.
\tag{7}
\]
The same operators occur because inner conjugation by \(N\) is trivial on
\(\gamma_2N/\gamma_3N\).

### Full wedge augmentation

Reduce \(W\) modulo \(2\). For a finitely supported wedge vector, define
\[
\Phi_\infty
\left(
\sum_{v<w}a_{vw}\,e_v\wedge e_w
\right)
=
\sum_{v<w}a_{vw}\pmod2.
\tag{8}
\]
The group \(Q\) permutes the basis vertices. In characteristic two, the
orientation sign of a wedge disappears, so \(\Phi_\infty\) is
\(Q\)-invariant. Therefore
\[
\Phi_\infty(L_i y)
=\varepsilon(L_i)\Phi_\infty(y)=0.
\tag{9}
\]

### The three-point quotient

Let \(Q\) act on
\[
\Omega=\{0,1,2\}
\]
by
\[
c=(1\ 2),\qquad t=(0\ 1\ 2),
\tag{10}
\]
with base point \(0\), which is fixed by \(c\). This induces the module map
\[
M\otimes\mathbb F_2\longrightarrow\mathbb F_2[\Omega],
\qquad
e_{q\langle c\rangle}\longmapsto e_{q0}.
\tag{11}
\]
After applying \(\Lambda^2\), sum the three wedge coordinates:
\[
\Phi_3:
\Lambda^2\mathbb F_2[\Omega]\longrightarrow\mathbb F_2.
\tag{12}
\]
Again \(Q\) only permutes the three unordered pairs, so
\[
\Phi_3(L_i y)=0
\tag{13}
\]
for every \(i\) and every \(y\).

Both (8) and (12) are global functionals. They do not assume that a
second-layer correction has bounded support.

## 3. The four parity classes

Lift each representative \(x^{ab}\) to actual products of the Schreier
generators
\[
\widetilde v c^2\widetilde v^{-1}\in N,
\]
recompute the complete free-group recurrence, and rewrite its residual in
the free basis of \(N\). The results are:

| \((a,b)\) | free residual length | kernel length | \(\Phi_\infty\) | \(\Phi_3\) |
|---:|---:|---:|---:|---:|
| \((0,0)\) | 82 | 24 | 1 | 1 |
| \((1,0)\) | 442 | 104 | 0 | 1 |
| \((0,1)\) | 678 | 212 | 0 | 1 |
| \((1,1)\) | 614 | 178 | 1 | 0 |

No row has both obstruction values zero.

These values depend only on the parity class of the first-layer solution.
Changing an exponent by an even integer contributes no degree-one Magnus
term modulo \(2\); its degree-two contribution is diagonal and is killed by
both wedge functionals. Changing the order of chosen Schreier lifts changes
the degree-two residual by a term of the form (7), also killed by
(9) and (13).

It follows that every integral solution of (1) supported in
\(\mathcal V\) has a nonzero degree-two obstruction which no
\(y_0,\ldots,y_4\) can repair.

## 4. Support-escape theorem

Suppose the fixed exact period-two witness lifts through
\[
F(c,t)/\gamma_3N.
\]
Its first-layer correction solves (1). If that correction were supported
inside \(\mathcal V\), Section 1 would place it in one of the four classes
(6), while Section 3 would obstruct every possible second-layer correction.
This is a contradiction.

Therefore
\[
\boxed{
\text{every degree-two lift must use first-layer support outside }
\mathcal V.
}
\tag{14}
\]

This identifies the first necessary nonlocal phenomenon in the lifting
problem. A successful correction must create cancellation among module
rows which initially lie entirely outside the \(21\)-term defect support and
only later propagate back to it.

## 5. Exact certificate

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_degree\_two\_escape\_certificate.py}
\]
constructs (3)--(4), verifies all three ranks in (5), checks the particular
and homogeneous solutions, recomputes the four nonlinear free-group
residuals, and evaluates both global functionals.

The theorem does not exclude remote support and does not close the hardest
depth-four class.
