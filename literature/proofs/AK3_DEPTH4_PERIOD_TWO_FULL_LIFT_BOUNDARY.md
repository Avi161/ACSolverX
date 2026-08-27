# Exact free-group lift boundary after the unary delta theorem

## Status

The proved identity

\[
u_{ij}=\delta_{ij}
\tag{0.1}
\]

does not construct a free-group lift and does not obstruct the complete
correction space.  It gives a sharp class-two sieve on the anchored
two-parameter family: every off-diagonal anchored correction fails the
full-wedge readout, while every diagonal correction clears that one bit.

The smallest constructive next obligation is to evaluate the other fourteen
finite-action unary coordinates on the diagonal family.  Even simultaneous
vanishing of all fifteen recorded bits would be only a necessary condition
for a class-two lift.  The full equation lives in an infinite exterior
module, and a literal lift must subsequently kill every higher nonabelian
defect.

No AK(3), stable Andrews--Curtis, or Andrews--Curtis conclusion is made.

## 1. Literal lift equation

Let

\[
Q=\langle c,t\mid c^2=1\rangle,
\qquad
N=\ker(F(c,t)\to Q),
\qquad
M=N_{\mathrm{ab}}.
\tag{1.1}
\]

The eight-term relation-module solution from
<code>AK3_DEPTH4_PERIOD_TWO_RELATION_MODULE_LIFT.md</code> is denoted

\[
x^{00}=(x^{00}_0,\ldots,x^{00}_4),
\qquad
d+\sum_{r=0}^4L_rx^{00}_r=0.
\tag{1.2}
\]

Put

\[
\mathcal H_{\mathrm{fin}}
:=\left\{
F=(f_0,\ldots,f_4)\in M^5:
\begin{array}{l}
f_r\text{ is finitely supported},\\
\sum_{r=0}^4L_rf_r=0
\end{array}
\right\}.
\tag{1.3}
\]

Thus every finitely supported first-layer solution is \(x^{00}+F\) with
\(F\in\mathcal H_{\mathrm{fin}}\).

For a module vertex \(v\), use the fixed representative

\[
r_v=\widetilde v c^2\widetilde v^{-1}\in N
\tag{1.4}
\]

and the canonical shortlex section

\[
\sigma(f)=\prod_v r_v^{\,f_v}.
\tag{1.5}
\]

An arbitrary lift of the module class \(x^{00}_r+f_r\) is not restricted to
this section.  It has the unique form

\[
n_r(F;\mathbf k)
=k_r\,\sigma(x^{00}_r+f_r),
\qquad
\mathbf k=(k_0,\ldots,k_4)\in[N,N]^5.
\tag{1.6}
\]

For \(r=0,1,2,3\), put

\[
h_r(F;\mathbf k)=n_r(F;\mathbf k)h_r.
\tag{1.7}
\]

Recompute the literal recurrence in \(F(c,t)\):

\[
\begin{aligned}
R_{F,\mathbf k}
 &=Ah_0(F;\mathbf k)B^{-1}h_0(F;\mathbf k)^{-1},\\
S_{F,\mathbf k}
 &=Bh_1(F;\mathbf k)R_{F,\mathbf k}^{-1}
   h_1(F;\mathbf k)^{-1},\\
U_{F,\mathbf k}
 &=R_{F,\mathbf k}h_2(F;\mathbf k)S_{F,\mathbf k}^{-1}
   h_2(F;\mathbf k)^{-1},\\
Z_{F,\mathbf k}
 &=U_{F,\mathbf k}^{-1}h_3(F;\mathbf k)S_{F,\mathbf k}
   h_3(F;\mathbf k)^{-1}.
\end{aligned}
\tag{1.8}
\]

The exact residual is

\[
\boxed{
\mathcal R(F;\mathbf k)
:=Z_{F,\mathbf k}
\bigl(n_4(F;\mathbf k)t n_4(F;\mathbf k)^{-1}\bigr)^{-1}
\in[N,N].}
\tag{1.9}
\]

Consequently the literal period-two lifting problem is exactly

\[
\boxed{
\exists F\in\mathcal H_{\mathrm{fin}},\
\exists\mathbf k\in[N,N]^5
\quad \mathcal R(F;\mathbf k)=1\text{ in }F(c,t).}
\tag{1.10}
\]

The canonical-section residual is

\[
\mathcal R_{\mathrm{can}}(F):=\mathcal R(F;\mathbf 1).
\tag{1.11}
\]

For \(F=0\), \(\mathcal R_{\mathrm{can}}(0)\) is the tracked nontrivial
freely reduced word of length 82.  Relation-module vanishing proves only
membership in \([N,N]\).

## 2. Exact forest parametrization of first-layer freedom

The operators \(L_2,L_3,L_4\) are the three oriented edge-boundary maps of
the two free Cayley-tree components.  Finite boundary injectivity implies
that every \(F\in\mathcal H_{\mathrm{fin}}\) is determined by its first two
sources \((f_0,f_1)\): the vertex chain

\[
b(F):=L_0f_0+L_1f_1
\tag{2.1}
\]

must have coefficient sum zero on each component, and then
\((f_2,f_3,f_4)\) is the unique finite forest flow with boundary \(-b(F)\).
Conversely every finite source pair with this balance condition produces one
element of \(\mathcal H_{\mathrm{fin}}\).

In particular,

\[
\ker_{\mathrm{fin}}(L_2,L_3,L_4)=0.
\tag{2.2}
\]

There is no pure forest-cycle freedom.  A global lift theorem or obstruction
must therefore be expressed on the complete balanced source-pair space, not
on a bounded list of previously found directions.

## 3. Full class-two equation

Since \(N\) is free on the Schreier generators \((r_v)_{v\in X}\),

\[
W:=\gamma_2N/\gamma_3N
=[N,N]/[[N,N],N]
\cong\Lambda^2M.
\tag{3.1}
\]

Let

\[
\Theta(F):=[\mathcal R_{\mathrm{can}}(F)]\in W
\tag{3.2}
\]

be the complete degree-two defect of the canonical first-layer section.
It is an integral affine-quadratic function of \(F\).  Second-layer
corrections contribute through five induced degree-two operator maps.  Write
the finite group-ring operator as

\[
L_r=\sum_{g\in Q}a_{r,g}g.
\tag{3.3}
\]

The quotient action on \(M\) induces the diagonal action

\[
g\cdot(m\wedge n)=(gm)\wedge(gn)
\tag{3.4}
\]

on \(W\cong\Lambda^2M\).  Define

\[
\boxed{
L_r^{(2)}(m\wedge n)
:=\sum_{g\in Q}a_{r,g}\,(gm\wedge gn).}
\tag{3.5}
\]

This is the exact second-layer variation operator: modulo
\(\gamma_3N=[[N,N],N]\), the group \(\gamma_2N\) is central in \(N\), so
conjugation by the inner \(N\)-part of a prefix is trivial; only its quotient
class \(g\in Q\) acts, with the same integral coefficient \(a_{r,g}\) as in
\(L_r\).  Therefore, if \(Y_r=[k_r]\in W\), direct variation of (1.9) gives

\[
\boxed{
[\mathcal R(F;\mathbf k)]
=\Theta(F)+\sum_{r=0}^4L_r^{(2)}Y_r.}
\tag{3.6}
\]

Conversely every \(Y_r\in W\) is represented by some \(k_r\in[N,N]\).
Write

\[
\mathcal I_2:=\sum_{r=0}^4\operatorname{im}L_r^{(2)}
\subseteq\Lambda^2M,
\qquad
\mathcal C_2:=\Lambda^2M/\mathcal I_2.
\tag{3.7}
\]

A lift through \(F(c,t)/\gamma_3N\) exists exactly when

\[
\boxed{
\exists F\in\mathcal H_{\mathrm{fin}}
\quad [\Theta(F)]=0\text{ in }\mathcal C_2.}
\tag{3.8}
\]

Equivalently, for some finitely supported second-layer variables \(Y_r\),

\[
\Theta(F)+\sum_{r=0}^4L_r^{(2)}Y_r=0
\qquad\text{in }\Lambda^2M.
\tag{3.9}
\]

The tracked syndrome is only a quotient of this cokernel class:

\[
S(F)=\Pi_{15}[\Theta(F)]\in\mathbb F_2^{15}.
\tag{3.10}
\]

Therefore \(S(F)=0\) is necessary but not sufficient for (3.8).  No theorem
shows that the fifteen recorded covectors detect all of \(\mathcal C_2\).
The known finite-dimensional obstruction spans and the remote syzygies prove
that a fixed bounded list of directions or covectors cannot be treated as a
global classification.

## 4. Exact diagonal sieve

Let \(D_{ij}=H(y_{ij})\) be the anchored directions from the unary ray, and
write the base-subtracted syndrome as

\[
U(D)=S(D)+S(0).
\tag{4.1}
\]

The base syndrome is

\[
S(0)=\texttt{111010110101011},
\qquad S_\infty(0)=1.
\tag{4.2}
\]

The independently replayed unary theorem is

\[
U_\infty(D_{ij})=u_{ij}=\delta_{ij}.
\tag{4.3}
\]

Hence

\[
\boxed{S_\infty(D_{ij})=1+\delta_{ij}.}
\tag{4.4}
\]

This gives two exact conclusions.

1. If \(i\ne j\), the fixed first-layer class \(F=D_{ij}\) has a nonzero
   cokernel readout.  No choice of \(\mathbf k\) can make
   \(\mathcal R(D_{ij};\mathbf k)\) trivial through class two, hence none can
   make it literally trivial.  This excludes that class only; it does not
   decide the existential problems (3.8) or (1.10).
2. If \(i=j\), that one readout vanishes.  No other class-two coordinate is
   thereby controlled.

For a diagonal direction, all fifteen recorded bits vanish precisely when

\[
\boxed{
\bigl(U_1(D_{ii}),\ldots,U_{14}(D_{ii})\bigr)
=\texttt{11101011010101}.}
\tag{4.5}
\]

The exact fixtures at \(i=0,1\) fail (4.5).  This is bounded exclusion of
two diagonal members only, not an induction or an all-index obstruction.

## 5. Smallest constructive next obligation

Put \(D_i:=D_{ii}\) and define the fourteen-coordinate sequence

\[
V_i:=\bigl(U_1(D_{ii}),\ldots,U_{14}(D_{ii})\bigr)
\in\mathbb F_2^{14}
\qquad(i\geq0).
\tag{5.1}
\]

On the diagonal, the source words are the already normalized pure-\(P\)
words \(\operatorname{red}(P_\nu^iC_\nu)\).  The finite permutation actions
alone do not prove that \(V_i\) is periodic.  For the eleven actions used by
the fourteen readouts, direct substitution gives the orders

\[
(2,4,1,1,2,4,1,4,1,5,4)
\tag{5.2}
\]

for the images of \(\gamma=g^3\); their least common multiple is 20.  Thus
every projected endpoint state has period dividing 20.  For a finite action
\(\rho\), the projected linear path currents satisfy

\[
\bar x_{\rho,\nu,i+20}
=\bar x_{\rho,\nu,i}+S_{\rho,\nu}
\tag{5.3}
\]

for fixed currents \(S_{\rho,\nu}\), and hence their coefficientwise mod-four
shadow has period dividing 80.  Any ordinary affine-quadratic polynomial of
those projected currents would inherit a period dividing 80.

The actual crossed evaluator does not factor through that shadow.  The
degree-two coordinate of its canonical correction section is

\[
\Sigma(f)
=\sum_x\binom{f_x}{2}e_x\otimes e_x+
\sum_{x<y}f_xf_y\,e_x\otimes e_y.
\tag{5.4}
\]

The first term needs coefficients modulo four.  The second depends on the
global source-forest shortlex order.  Put
\(\operatorname{key}(x)=(|x|,x)\).  Under a quotient action \(q\), the
transport defect contains both the one-vertex defects and the order-reversal
count.  For the projected module \(\bar V_\rho\), the exact section cocycle
has
\(\tau_q(x),\kappa_q(f)\in\Lambda^2\bar V_\rho\) and

\[
\kappa_q(f)
=\sum_xf_x\tau_q(x)+
\sum_{\operatorname{key}(x)<\operatorname{key}(y),\
       \operatorname{key}(\operatorname{cvert}(qx))>
       \operatorname{key}(\operatorname{cvert}(qy))}
   f_xf_y\,e_{\operatorname{cvert}(qx)}
          \wedge e_{\operatorname{cvert}(qy)}.
\tag{5.5}
\]

Finite point images do not determine (5.5).  The fixed-base--direction
products, inverse self terms, quotient-section defects, doubled anchors,
negative occurrences, terminal-\(c\) normalization, and final pre-wedge
diagonal cancellation must also remain.  Therefore neither period two nor
period 80 for \(V_i\) follows from (5.2)--(5.3).

There is an exact period-two proof object.  Put

\[
\Delta_i:=D_{i+1}-D_i.
\tag{5.6}
\]

The right-deck path recurrence gives

\[
\begin{aligned}
\Delta_{i,0}
 &=e_{y_{i+1,i+1}}-e_{y_{ii}},&
\Delta_{i,1}&=0,\\
\Delta_{i,s}
 &=\sum_{\nu=1}^6\epsilon_\nu
 \left(
 \mathsf E_s(P_\nu)
 +p_\nu x^s_{\nu,i,i}
 -x^s_{\nu,i,i}
 \right),
 &&s=2,3,4.
\end{aligned}
\tag{5.7}
\]

Let \(u_{14}\) be the base-subtracted fourteen-coordinate unary evaluator
and let

\[
\beta_{14}(D,E)
:=u_{14}(D+E)+u_{14}(D)+u_{14}(E)
\tag{5.8}
\]

be its alternating polarization.  Affine quadraticity gives

\[
\boxed{
G_i:=V_{i+1}+V_i
=u_{14}(\Delta_i)+\beta_{14}(D_i,\Delta_i).}
\tag{5.9}
\]

Consequently

\[
\boxed{V_{i+2}+V_i=G_{i+1}+G_i.}
\tag{5.10}
\]

The exact period-two target is therefore the fourteen all-index identities

\[
\boxed{G_{i+1}=G_i\qquad(i\geq0).}
\tag{5.11}
\]

Every term in (5.4)--(5.5) must be retained when expanding (5.9).  The
existing pure-\(P\) schemas prove the moving source words and module orders,
but they do not yet sum the complete section, transport, base, and inverse
terms in \(G_i\).

The exact finite data are

\[
\begin{aligned}
C_{14}&=\texttt{11101011010101},\\
V_0&=\texttt{01011110011011},\\
V_1&=\texttt{10111011000101}.
\end{aligned}
\tag{5.12}
\]

Thus the residual fourteen-bit values at \(i=0,1\) are respectively

\[
\texttt{10110101001110},
\qquad
\texttt{01010000010000},
\tag{5.13}
\]

both nonzero.  If (5.11) is proved, (5.10) makes \(V_i\) two-periodic and
(5.13) excludes every diagonal \(D_i\).  Until then, (5.13) excludes only
\(i=0,1\).

- If some \(i\) satisfies (4.5), freeze \(F=D_{ii}\) and solve the complete
  second-layer equation (3.9).  Only that full exterior-module equation
  reaches \(F/\gamma_3N\).
- If no \(i\) satisfies (4.5), the complete diagonal anchored ansatz is
  excluded, but arbitrary balanced source pairs remain.
- For sums of source directions, the mixed polarizations of \(\Theta\) are
  mandatory.  The unary delta theorem determines no such cross term.

If the diagonal ansatz fails, the next global formulation is the quadratic
cokernel equation (3.8) on the exact balanced source-pair parametrization of
Section 2.  A genuine obstruction must be a covector or structural theorem
on the full cokernel \(\mathcal C_2\) that detects every finite balanced
source pair.  The full-wedge covector cannot do this, because every
\(D_{ii}\) already kills it.

## 6. Literal and AK(3) boundaries

Solving (3.8) constructs a lift only through the class-two quotient.  The
residual then lies in \(\gamma_3N\), and (1.10) still requires its literal
free reduction to the identity, either by higher corrections or by a direct
word-level construction.

Even a literal solution of (1.10) proves only this named depth-four free-group
recurrence.  A separate theorem must connect that recurrence to the required
AK(3) Andrews--Curtis move or donor factorization.  In particular, the
active bridge

\[
(A,B,zYX)\sim_{\mathrm{AC}}(A,B,Xyz)
\tag{6.1}
\]

is not supplied here.  AK(3), stable Andrews--Curtis, and
Andrews--Curtis remain open.
