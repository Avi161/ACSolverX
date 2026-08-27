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

The other fourteen finite-action coordinates reduce to the crossed
derivatives \(R_{k,i}\).  Their entire differentiated-inversion source is
now evaluated, and the remaining ordered profiles plus finite-state terms
make the all-index target equivalent to the conservative 9,982-bit window
\(R_{k,i}\) with \(1\leq k\leq14\) and \(0\leq i\leq712\).  None of those
post-inversion remainder values is evaluated here.  Even simultaneous
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

### 5.1 No invariant-covector shortcut

Let \(\rho\) be one of the finite actions and let \(\lambda\) be its
invariant wedge covector.  Applying \(\lambda\) to the section cocycle (5.5)
does not produce an ordinary scalar cocycle.  If

\[
a_q^\lambda(f):=\lambda(\kappa_q(f)),
\tag{5.14}
\]

then the corrected composition law is

\[
\boxed{
a_{gh}^\lambda(f)+a_g^\lambda(hf)+a_h^\lambda(f)
=\lambda\!\left(
\overline\omega(g,h)\wedge\overline{ghf}
\right).}
\tag{5.15}
\]

Invariance removes the outer \(g\)-action but not the quotient-section
residual on the right.

This residual is active on the actual ray.  For the identity four-point
action

\[
\rho(c)=1,\qquad \rho(t)=(0\,1\,2\,3),
\tag{5.16}
\]

take the two tracked covectors corresponding to coordinates 6 and 7.  Since
\(\omega(c,c)=c^2\) projects linearly to \(E_0\), while

\[
\rho(y_{ii})0=\rho(t^{-(i+1)})0=(3,2,1,0)
\quad(i\bmod4),
\tag{5.17}
\]

the right side of (5.15) has the exact respective signatures

\[
(0,1,0,0),\qquad(1,0,1,0).
\tag{5.18}
\]

Thus \(Q\)-invariance alone neither kills nor cobounds the section/transport
term.  Cancellation may still occur after summing the complete literal AST,
but it must be evaluated there.

### 5.2 One exact two-step crossed derivative

Put

\[
E_i:=\Delta_i+\Delta_{i+1}=D_{i+2}-D_i.
\tag{5.19}
\]

Biadditivity and alternation of \(\beta_{14}\) reduce (5.10) to

\[
\boxed{
G_{i+1}+G_i
=u_{14}(E_i)+\beta_{14}(D_i,E_i).}
\tag{5.20}
\]

The pure-\(P\) right-deck recurrence gives

\[
\begin{aligned}
E_{i,0}
 &=e_{y_{i+2,i+2}}-e_{y_{ii}},&
E_{i,1}&=0,\\
E_{i,s}
 &=\sum_{\nu=1}^6\epsilon_\nu
 \left(
 \mathsf E_s(P_\nu^2)
 +(p_\nu^2-1)x^s_{\nu,i,i}
 \right),
 &&s=2,3,4,
\end{aligned}
\tag{5.21}
\]

where

\[
\mathsf E_s(P_\nu^2)
=\mathsf E_s(P_\nu)+p_\nu\mathsf E_s(P_\nu).
\tag{5.22}
\]

The doubled anchors cancel from \(E_i\), but remain in the old state \(D_i\).
The slot-zero component in (5.21) is the difference of two distinct powered
singleton vertices, so \(E_i\) is not an even direction and the separate
coefficient-period-two theorem does not apply.

There is a closed recursive formula for the complete residual in (5.20).
At a correction leaf of slot \(s\), put

\[
f=B_s+D_{i,s},\qquad e=E_{i,s}.
\tag{5.23}
\]

The linear increment is \(\delta a=e\).  For the ordered tensor coordinate
\(\Sigma\) from (5.4),

\[
\begin{aligned}
d\Sigma_f(e)
&:=\Sigma(f+e)-\Sigma(f)\\
&=\sum_x
 \left(f_xe_x+\binom{e_x}{2}\right)e_x\otimes e_x\\
&\quad{}+
 \sum_{x<y}
 \left(f_xe_y+e_xf_y+e_xe_y\right)e_x\otimes e_y.
\end{aligned}
\tag{5.24}
\]

This retains the merged shortlex section, fixed base, and doubled anchors
integrally.

For old node coordinates \(X=(q,a,A)\), \(Y=(r,b,B)\) and increments
\((\delta a,\delta A)\), \((\delta b,\delta B)\), let \(q\) act on module
vertices by \(q e_x=e_{\operatorname{cvert}(qx)}\) and diagonally on tensors.
Differentiating the exact crossed product gives

\[
\begin{aligned}
\delta c
 &=\delta a+q\delta b,\\
\delta C
 &=\delta A+q\delta B+\tau_q(\delta b)\\
&\quad{}+\delta a\otimes(qb)
 +a\otimes(q\delta b)
 +\delta a\otimes(q\delta b)\\
&\quad{}+(\delta a+q\delta b)\otimes o_{q,r}.
\end{aligned}
\tag{5.25}
\]

The fixed \(O_{q,r}\) has zero local derivative, while its associated
linear defect \(o_{q,r}\) remains explicitly in (5.25) and in every
downstream old state.  Literal leaves have zero increment but retain their
complete old coordinates.

For inversion, first use

\[
\begin{aligned}
\delta(-a)&=-\delta a,\\
\delta(-A+a\otimes a)
&=-\delta A+a\otimes\delta a+\delta a\otimes a
  +\delta a\otimes\delta a,
\end{aligned}
\tag{5.26}
\]

then multiply on the left by the fixed literal coordinate
\(\Lambda(q^{-1})\) using (5.25).  Conjugation is differentiated in the
literal order \(X\star Y\star\operatorname{Inv}(X)\).

Recursing (5.24)--(5.26) through the exact residual AST yields a root
increment \((1,0,\delta A_{\mathrm{root},i})\).  For the fourteen tracked
action/covector pairs \((\rho_k,\lambda_k)\), define

\[
\boxed{
R_{k,i}
:=\lambda_k\Pi_{\rho_k}(\delta A_{\mathrm{root},i})
=\lambda_k\Pi_{\rho_k}
 \left(M_B(D_{i+2})-M_B(D_i)\right).}
\tag{5.27}
\]

The exact all-index target is

\[
\boxed{R_{k,i}=0\qquad(1\leq k\leq14,\ i\geq0).}
\tag{5.28}
\]

Equations (5.20) and (5.27) prove that (5.28) is equivalent to
\(G_{i+1}=G_i\).  The current pure-\(P\) schemas supply the powered supports
and canonical vertices in (5.21).  Section 5.3 removes the shortlex,
base--direction, inverse, and one-vertex transport families from part of
the unbounded obstruction.  The analysis below evaluates the transported
ordered-section order-reversal sum and reduces the remaining exact
obligation to the 9,982 finite values in (5.77).

### 5.3 Weighted Green reduction and the order-reversal remainder

The untransported shortlex part of (5.24) admits a finite-action Green
formula, but its transported occurrence sum retains an order-reversal
correction.  Fix one tracked permutation action
\(\rho:Q\to\operatorname{Sym}(\Omega)\), with base point \(0\), and an
invariant covector
\(\lambda\in(\Lambda^2\mathbb F_2^\Omega)^*\).  Write

\[
 \pi_\rho(e_x)=e_{\rho(x)0},
 \qquad
 \Pi_\rho^\wedge:=\Lambda^2\pi_\rho,
 \qquad
 b_\lambda(u,v)=\lambda(u\wedge v),
\tag{5.29}
\]

and put

\[
 q_\lambda(v)
 =\sum_{\alpha<\beta}v_\alpha v_\beta\,
   \lambda(e_\alpha\wedge e_\beta).
\tag{5.30}
\]

Here and below every integral current is collision-aggregated first and
then reduced modulo two.  The relevant map on an intermediate tensor is
the ordered-half reader

\[
 \operatorname{Wdg}_\rho(A)
 :=\sum_{x<y}A_{xy}\,
 e_{\rho(x)0}\wedge e_{\rho(y)0}.
\tag{5.30a}
\]

It kills diagonals and reads the one canonical source-shortlex orientation.
It is not the characteristic-two quotient map
\(T(M)\to\Lambda^2M\): that quotient would send an antisymmetric
commutator tensor to twice its wedge and hence to zero.  It is also not
\(Q\)-equivariant, because a quotient action can reverse the source
shortlex order.

#### Lemma 5.1 (weighted Green identity)

For all integral finite currents \(f,e\),

\[
\boxed{
 \lambda\operatorname{Wdg}_\rho(d\Sigma_f(e))
 =b_\lambda(\pi_\rho f,\pi_\rho e)
  +q_\lambda(\pi_\rho e).}
\tag{5.31}
\]

#### Proof

The diagonal and binomial terms in (5.24) die under
\(\operatorname{Wdg}_\rho\).  For \(x\ne y\), set

\[
 w(x,y)=
 \lambda(e_{\rho(x)0}\wedge e_{\rho(y)0}).
\tag{5.32}
\]

In characteristic two, \(w(x,y)=w(y,x)\) and \(w(x,x)=0\).  The two
old--new summands in (5.24), summed over the one shortlex orientation of
each unordered pair, therefore aggregate fiberwise to
\(b_\lambda(\pi_\rho f,\pi_\rho e)\).  The new--new summand similarly
aggregates to \(q_\lambda(\pi_\rho e)\).  This proves (5.31). \(\square\)

For a fixed slot \(s\), the positive and negative occurrence counts do
have zero signed augmentation:

\[
 \sum_{o:s_o=s}p_o=0.
\tag{5.33}
\]

This does not cancel the transported leaf terms.  Although \(\lambda\) is
\(\rho(Q)\)-invariant, the ordered-half reader in (5.30a) is not
\(Q\)-equivariant.  Transport can reverse a pair of source-shortlex
vertices, and that reversal is exactly one of the section-cocycle terms
which Section 5.1 showed to be active.

More precisely, let

\[
 \operatorname{Inv}_q(f)
 :=\sum_{\substack{x<y\\
   \operatorname{key}(\operatorname{cvert}(qx))>
   \operatorname{key}(\operatorname{cvert}(qy))}}
 f_xf_y\,
 e_{\operatorname{cvert}(qx)}
 \wedge e_{\operatorname{cvert}(qy)}.
\tag{5.33a}
\]

The complete wedge-valued section defect is

\[
 \kappa_q(f)
 =\sum_x f_x\tau_q(x)+\operatorname{Inv}_q(f),
\tag{5.33b}
\]

and its exact increment is

\[
\boxed{
 d\kappa_{q,f}(e)
 =\sum_xe_x\tau_q(x)+d\operatorname{Inv}_{q,f}(e),}
\tag{5.33c}
\]

where

\[
 d\operatorname{Inv}_{q,f}(e)
 =\sum_{\substack{x<y\\
   \operatorname{key}(\operatorname{cvert}(qx))>
   \operatorname{key}(\operatorname{cvert}(qy))}}
 (f_xe_y+e_xf_y+e_xe_y)\,
 e_{\operatorname{cvert}(qx)}
 \wedge e_{\operatorname{cvert}(qy)}.
\tag{5.33d}
\]

The exact crossed-product derivative (5.25) contains the transported leaf
tensor and the one-vertex transport tensor, but it does not contain a
second copy of the full section defect (5.33c).  Thus the actual
ordered-section contribution is

\[
\boxed{
 \mathcal A_{\rho,\lambda}(q;f,e)
 =\lambda\operatorname{Wdg}_\rho(q\,d\Sigma_f(e))
  +\lambda\Pi_\rho^\wedge
   \left(\sum_xe_x\tau_q(x)\right).}
\tag{5.33e}
\]

Formula (5.33c) describes the change from the transported old ordering to
the canonical new ordering.  Adding all of \(d\kappa\) to (5.33e) would
double-count that representation change.  Lemma 5.1 removes the
untransported shortlex sum, but it does not by itself evaluate the
occurrence sum of the actual packages (5.33e).

The projected linear states entering the terms outside the actual section
package (5.33e) are finite-state.  This does not by itself make their
ordered-half pairings finite-state.  To state the valid linear recurrence
without confusing the right-deck action with the point action, lift \(\rho\)
to the finite group-image basis \(\mathbb F_2[\rho(Q)]\).  Right
multiplication by a powered endpoint is then a genuine permutation
operator; evaluation at the base point is applied only afterward.  For the
six pure-\(P\) source families, the exact path recurrence has the lifted
form

\[
 X_{\rho,\nu,s}(i)
 =H_i(T_{\rho,\nu})A_{\rho,\nu,s}
  +T_{\rho,\nu}^{\,i}C_{\rho,\nu,s},
\qquad
 H_i(T)=\sum_{h=0}^{i-1}T^h.
\tag{5.34}
\]

Each \(T_{\rho,\nu}\) is conjugate in the finite group image to the
appropriate image of the powered element.  If
\(m_\rho=\operatorname{ord}\rho(\gamma)\), then
\(T_{\rho,\nu}^{m_\rho}=1\).  Over \(\mathbb F_2\),

\[
 H_{i+2m_\rho}(T_{\rho,\nu})=H_i(T_{\rho,\nu}),
 \qquad
 T_{\rho,\nu}^{\,i+2m_\rho}=T_{\rho,\nu}^{\,i}.
\tag{5.35}
\]

Thus every projected old linear state and two-step increment is strictly
\(2m_\rho\)-periodic from \(i=0\).  Algebraic outer-product,
inverse-self, and \(o_{q,r}\)-linear tensors built after finite projection
inherit that period, but their actual ordered-half readouts need not: the
profiles (5.45cm) retain source shortlex before projection.  The fixed
\(O_{q,r}\) has zero derivative.  The one-vertex summand is controlled
below, while Sections 5.4--5.6 control the remaining ordered profiles.  The
eleven action orders in (5.2) give the joint projected-state bound

\[
 \operatorname{lcm}_\rho(2m_\rho)=40.
\tag{5.36}
\]

The first summand of (5.33c), the one-vertex transport term, can be
evaluated independently.  For a basis vertex, let
\(\overline\omega(q,x)\in M\) be the relation-module class of the
quotient-section defect between
\(\widehat q\,\widehat x\) and \(\widehat{qx}\).  The transport scalar is

\[
\boxed{
 \lambda\Pi_\rho^\wedge(\tau_q(e_x))
 =\lambda\!\left(
 e_{\rho(qx)0}\wedge
 \pi_\rho\overline\omega(q,x)
 \right).}
\tag{5.37}
\]

Indeed,
\(q r_xq^{-1}=\omega(q,x)r_{qx}\omega(q,x)^{-1}\);
the class-two conjugation cross term is precisely (5.37), with orientation
irrelevant after reduction modulo two.

Formula (5.37) cannot be inferred from the central finite point alone.  The
point
\(\rho(qx)0\) is finite-periodic, but
\(\pi_\rho\overline\omega(q,x)\) is not determined by that point.  One must
therefore retain the local raw bridge rather than infer the defect current
from a finite point.

For one actual correction occurrence with prefix \(q_o\) and atom \(v\),
the approved bridge has

\[
 \operatorname{red}(q_ovccv^{-1}q_o^{-1})=zccz^{-1},
 \qquad
 z=k_z\widehat x,
 \qquad
 x=\operatorname{cvert}(q_ov).
\tag{5.40}
\]

Its first-half Schreier events are exactly the event word of \(k_z\), and

\[
 q_or_vq_o^{-1}=k_zr_xk_z^{-1}.
\tag{5.41}
\]

Thus \(k_z\) is the terminal-normalized defect in (5.37), and, over
\(\mathbb F_2\),

\[
 \pi_\rho\overline{k_z}
 =\sum_{a\ {\rm a\ first\text{-}half\ event}}
   e_{\rho(\ell(a))0}.
\tag{5.42}
\]

Raw signs may be omitted in (5.42); collision fibers are summed modulo two.
The approved pure-\(P\) raw pump fixes the complete first-half label list
for all 84 nonzero-slot occurrence records once \(i\geq3\).  These are the
42 collision-first coordinate families in slots \(2,3,4\), each evaluated
at its two actual occurrence actions.  Their central labels run on the
lifted common-phase finite orbit whose core is conjugate to
\(\gamma^{-1}\).  Equations (5.37) and (5.40)--(5.42) therefore prove that every
nonzero-slot transport scalar is \(m_\rho\)-periodic for \(i\geq3\).
Since \(E_i=q_i+q_{i+1}\) modulo two and \(\tau_q\) is linear, the same is
true for the complete two-step nonzero-slot transport contribution.

The slot-zero transport family can be closed directly.  On the diagonal,

\[
 y_i:=y_{ii}
 =p^{-1}c\gamma^{-(i+1)}t
 =(\texttt{cTc})(\gamma^{-1})^{i+1}\texttt t.
\tag{5.43}
\]

The word \(\gamma^{-1}\) is freely reduced of length \(24\), begins in
\(\texttt T\), and ends in \(c\).  Thus every displayed seam in (5.43) is
reduced and \(y_i\) ends in \(\texttt t\), so no terminal-\(c\)
normalization occurs.  The six slot-zero occurrence prefixes have length
at most \(11\).  At \(i=0\), the next powered insertion lies after

\[
 |\texttt{cTc}|+|\gamma^{-1}|=3+24=27>11+1.
\tag{5.44}
\]

Reduction of a fixed prefix \(q_o\) against \(y_i\) cannot reach that
insertion.  Hence the first-half kernel factor \(k_z\) in (5.40) is
literally independent of \(i\) from \(i=0\), while the central point has
period \(m_\rho=\operatorname{ord}\rho(\gamma)\).  Therefore the complete
slot-zero transport contribution attached to

\[
 E_{i,0}=e_{y_{i+2,i+2}}+e_{y_{ii}}
 \quad\text{over }\mathbb F_2
\tag{5.45}
\]

is \(m_\rho\)-periodic from \(i=0\).  Together with the approved
84-record pump, this settles the entire one-vertex transport summand in
(5.33c): its slots \(2,3,4\) have joint period dividing \(20\) for
\(i\geq3\), and slot zero has that bound from \(i=0\).

The remaining order-reversal term can be isolated from the transported
ordered-half leaf by an exact pairwise identity.  The identity does not
cancel that term from the actual crossed derivative.

#### Lemma 5.1a (ordered-reader decomposition)

Put

\[
 \mathfrak G_{\rho,\lambda}(f,e)
 :=\lambda\operatorname{Wdg}_\rho(d\Sigma_f(e))
\tag{5.45a}
\]

and

\[
\mathfrak T_{\rho,\lambda}(q;e)
 :=\lambda\Pi_\rho^\wedge
 \left(\sum_x e_x\tau_q(x)\right),
 \qquad
 \mathfrak I_{\rho,\lambda}(q;f,e)
 :=\lambda\Pi_\rho^\wedge
 \left(d\operatorname{Inv}_{q,f}(e)\right).
\tag{5.45b}
\]

Then, for every quotient action \(q\),

\[
\boxed{
 \lambda\operatorname{Wdg}_\rho(q\,d\Sigma_f(e))
 +\lambda\Pi_\rho^\wedge(d\operatorname{Inv}_{q,f}(e))
 =\mathfrak G_{\rho,\lambda}(qf,qe)
 =\mathfrak G_{\rho,\lambda}(f,e).}
\tag{5.45c}
\]

Consequently the actual package (5.33e) is

\[
\boxed{
 \mathcal A_{\rho,\lambda}(q;f,e)
 =\mathfrak G_{\rho,\lambda}(f,e)
  +\mathfrak T_{\rho,\lambda}(q;e)
  +\mathfrak I_{\rho,\lambda}(q;f,e).}
\tag{5.45d}
\]

To prove the first equality in (5.45c), fix \(x<y\).  The coefficient of
the unordered pair \(\{qx,qy\}\) in \(d\Sigma_{qf}(qe)\) is

\[
 f_xe_y+e_xf_y+e_xe_y.
\]

If \(qx<qy\), the transported ordered-half tensor supplies this
coefficient and the inversion derivative supplies zero.  If \(qx>qy\),
the ordered-half reader supplies zero and the inversion derivative supplies
the same coefficient.  Collision aggregation is harmless because left
multiplication by \(q\) is a bijection of \(X\).  Both sides kill tensor
diagonals.  Summing the pairwise identity proves the first equality.

For the second equality, apply Lemma 5.1 to \((qf,qe)\).  Since
\(\pi_\rho(qf)=\rho(q)\pi_\rho(f)\), invariance of \(\lambda\) preserves
both \(b_\lambda\) and the unordered-pair quadratic form \(q_\lambda\).
Thus

\[
 \mathfrak G_{\rho,\lambda}(qf,qe)
 =b_\lambda(\pi_\rho f,\pi_\rho e)
  +q_\lambda(\pi_\rho e)
 =\mathfrak G_{\rho,\lambda}(f,e).
\]

Finally, (5.33e) is the first term of (5.45c) plus
\(\mathfrak T\).  Over \(\mathbb F_2\), (5.45c) rewrites that first term
as \(\mathfrak G+\mathfrak I\), proving (5.45d).  Equivalently, one may
use either of the equal representations

\[
 [q\,d\Sigma]+\mathfrak T
 \qquad\text{or}\qquad
 [d\Sigma_{qf}(qe)]+d\kappa.
\]

The hybrid expression \([q\,d\Sigma]+d\kappa\) is invalid because it
counts the change of ordering twice.  The inverse-self derivatives of a
negative correction leaf are the separate terms in (5.26), while the
base--direction products occur separately in (5.25); neither alters
(5.45d).

The active occurrence counts by slot are \((6,0,2,2,2)\).  Hence, for
\(f_s=B_s+D_{i,s}\) and \(e_s=E_{i,s}\),

\[
\boxed{
 \sum_{o:s_o=s}p_o\mathcal A_{\rho,\lambda}(q_o;f_s,e_s)
 =\sum_{o:s_o=s}p_o
  \left(
   \mathfrak T_{\rho,\lambda}(q_o;e_s)
   +\mathfrak I_{\rho,\lambda}(q_o;f_s,e_s)
  \right).}
\tag{5.45e}
\]

Here the equality is read after reduction modulo two, where the signs
\(p_o\) may be retained or omitted.  Equation (5.33), or equivalently the
even active occurrence count in every slot, kills the common Green scalar
after the \(\mathbb F_2\) readout.  The one-vertex term \(\mathfrak T\) is
already controlled, but the order-reversal term \(\mathfrak I\) remains.
This is exactly the unbounded old--new comparison isolated below.

The inversion remainder itself has a clean relative-action compression.
For quotient actions \(q,r\), pairwise inversion parity gives

\[
 \operatorname{Inv}_{qr}(f)
 =\operatorname{Inv}_q(rf)+q\operatorname{Inv}_r(f)
 \qquad\text{in }\Lambda^2M\otimes\mathbb F_2.
\tag{5.45f}
\]

Indeed, on one unordered source pair, the order is reversed by the
composition exactly when it is reversed by one, but not both, of the two
successive permutations.  The exterior target of the second term is
transported by \(q\).  Differentiating (5.45f) and using invariance of
\(\lambda\) gives

\[
 \mathfrak I_{\rho,\lambda}(qr;f,e)
 =\mathfrak I_{\rho,\lambda}(q;rf,re)
  +\mathfrak I_{\rho,\lambda}(r;f,e).
\tag{5.45g}
\]

For a positive/negative occurrence pair with actions \(q_+,q_-\), put
\(m=q_-q_+^{-1}\).  Taking \(q=m\) and \(r=q_+\) in (5.45g) yields

\[
\boxed{
 \mathfrak I(q_+;f,e)+\mathfrak I(q_-;f,e)
 =\mathfrak I(m;q_+f,q_+e).}
\tag{5.45h}
\]

The six exact anchored occurrence pairs therefore reduce to

| slot | \(q_+\) | \(q_-\) | \(m=q_-q_+^{-1}\) |
|---:|---|---|---|
| 0 | `tc` | `ctcTTTcttc` | `ctcTTTct` |
| 0 | `ctcTcTctc` | `ctcTTTTcttc` | `ctcTTTTctctctcTc` |
| 0 | `ctcTctc` | `cTTcttc` | `cTTctctcTc` |
| 2 | \(1\) | `ctcTcTctc` | `ctcTcTctc` |
| 3 | `ctcTTctt` | `t` | `TcttcTc` |
| 4 | `t` | \(1\) | `T` |

These are the same relative multipliers as the universal anchored
inversion records; (5.45h) applies them here to the unary derivative.

The three slot-zero terms vanish without a comparison.  The fixed
correction has
\(B_0=2e_{cT}-2e_{cTTct}-2e_{cTTctt}\) by (13) of
[`AK3_DEPTH4_PERIOD_TWO_PHI4_ESCAPE.md`](AK3_DEPTH4_PERIOD_TWO_PHI4_ESCAPE.md),
and (6.2) of
[`AK3_DEPTH4_PERIOD_TWO_PHI_INFINITY_HESSIAN.md`](AK3_DEPTH4_PERIOD_TWO_PHI_INFINITY_HESSIAN.md)
gives \(D_{i,0}=e_{y_i}+2e_T\).  Hence, after collision aggregation and
reduction modulo two,

\[
 f_0=e_{y_i},
 \qquad
 e_0=e_{y_{i+2}}+e_{y_i},
 \qquad
 f_0+e_0=e_{y_{i+2}}.
\tag{5.45i}
\]

Since the inversion quadratic of a singleton is zero,

\[
\boxed{
d\operatorname{Inv}_{q,f_0}(e_0)
 =\operatorname{Inv}_q(f_0+e_0)+\operatorname{Inv}_q(f_0)
 =0
 \qquad(q\in Q).}
\tag{5.45j}
\]

Thus only the slot-two, slot-three, and slot-four relative kernels in the
last three rows of the table survive.  They admit a smaller connector
normal form.

Let \(K_i\) be the diagonal connector chain

\[
 K_i=[x_{1,i},x_{3,i}]
     +[x_{3,i},x_{4,i}]
     +[x_{3,i},x_{5,i}]
     +[x_{2,i},x_{6,i}]
\tag{5.45k}
\]

from (3.1) of
[`AK3_PURE_P_INCREMENT_NORMAL_FORM.md`](AK3_PURE_P_INCREMENT_NORMAL_FORM.md),
and let \(K_{i,s}\) be its slot-\(s\) coefficient current.  Write
\(\overline F\) for collision aggregation of an integral current \(F\)
followed by coefficient reduction modulo two.  The integral six-family
collision identity (2.3) of that note, reduced only after collision
aggregation, gives

\[
\boxed{\overline D_{i,s}=K_{i,s}\qquad(s=2,3,4).}
\tag{5.45l}
\]

Indeed, the doubled family \(2/6\) path disappears modulo two, the
families \(1\) and \(3\) give the path
\([x_{1,i},x_{3,i}]\), and the remaining \(w,z,w\) terms are exactly the
three short connectors in (5.45k).  Therefore

\[
\boxed{\overline E_{i,s}=K_{i,s}+K_{i+2,s}.}
\tag{5.45m}
\]

The fixed correction parities from (13) of the escape note are

\[
 \overline B_2=0,\qquad
 \overline B_3=e_{\texttt{TTct}},\qquad
 \overline B_4=e_{\texttt{Tct}}.
\tag{5.45n}
\]

For the last three rows of the relative-action table, write

\[
\begin{aligned}
 (q_2,m_2)&=(1,\texttt{ctcTcTctc}),\\
 (q_3,m_3)&=(\texttt{ctcTTctt},\texttt{TcttcTc}),\\
 (q_4,m_4)&=(\texttt t,\texttt T),
\end{aligned}
\]

and define the connector inversion potentials

\[
 \Xi_{k,s}(i)
 :=\lambda_k\Pi_{\rho_k}^\wedge
   \operatorname{Inv}_{m_s}(q_sK_{i,s}).
\tag{5.45o}
\]

If
\(\operatorname{PInv}_m(u,v)
 :=\operatorname{Inv}_m(u+v)+\operatorname{Inv}_m(u)
   +\operatorname{Inv}_m(v)\),
then quadratic expansion, (5.45l), and (5.45m) give the exact surviving
source formula

\[
\boxed{
\begin{aligned}
 \mathfrak I_{\rho_k,\lambda_k}
 &(m_s;q_s(B_s+D_{i,s}),q_sE_{i,s})\\
 ={}&\Xi_{k,s}(i+2)+\Xi_{k,s}(i)\\
 &+\lambda_k\Pi_{\rho_k}^\wedge
  \operatorname{PInv}_{m_s}
  \left(q_s\overline B_s,\,
        q_s(K_{i,s}+K_{i+2,s})\right).
\end{aligned}}
\tag{5.45p}
\]

The last line is zero in slot two.  In slots three and four it pairs one
fixed base singleton with the two-step shell.  Moreover
\(K_i+K_{i+2}=(K_i+K_{i+1})+(K_{i+1}+K_{i+2})\), and each parenthesis is
the proved 42-edge increment current.  Hence the base term has uniformly
bounded support and contains no complete old ray.

Formula (5.45p) reduces the unbounded order problem to the three second
differences
\(\Xi_{k,s}(i+2)+\Xi_{k,s}(i)\).  It evaluates none of them and does not
improve the onset or finite verification window by itself.

The slot-four potential has a further exact boundary-distance form.  Use
the quotient-letter order \(T<c<t\), and say that a canonical vertex is
\(t\)-initial when its reduced word begins in \(t\).  Left multiplication
by \(T\) decreases length by one on a \(t\)-initial word and increases
length by one on every other word.  Removing or adding the same initial
letter preserves lexicographic order inside either class.  It follows
that, for \(x<y\), left multiplication by \(T\) reverses their shortlex
order exactly when

\[
 x\text{ is not \(t\)-initial},\qquad
 y\text{ is \(t\)-initial},\qquad
 |y|-|x|\in\{0,1\}.
\tag{5.45q}
\]

For a length gap at least three, the two possible unit length changes
cannot reverse order.  At gap two the transformed lengths tie, but the
first transformed word begins in \(T\), while the second begins in \(c\)
or \(t\), so the order is still preserved.  Canonical inputs do not end
in \(c\), and left multiplication changes only the initial seam; hence
the displayed \(Tx,Ty\) are already canonical.  This proves the
all-current identity

\[
\boxed{
 \operatorname{Inv}_T(h)
 =\sum_{\substack{x\ {\rm not}\ t\text{-initial}\\
                  y\ t\text{-initial}\\
                  |y|-|x|\in\{0,1\}}}
 h_xh_y\,e_{Tx}\wedge e_{Ty}.}
\tag{5.45r}
\]

Apply (5.45r) to \(h=tK_{i,4}\).  A vertex \(tv\) is not \(t\)-initial
exactly when \(v\) begins in \(T\); otherwise \(tw\) is \(t\)-initial.
Moreover

\[
 |tv|=|v|-1,\quad |tw|=|w|+1,\quad
 T(tv)=v,\quad T(tw)=w
\]

in the respective two cases.  Hence

\[
\boxed{
 \Xi_{k,4}(i)
 =\sum_{\substack{v,w\in\operatorname{supp}K_{i,4}\\
                  v\text{ begins in }T,\ w\text{ does not}\\
                  |v|-|w|\in\{1,2\}}}
 K_{i,4}(v)K_{i,4}(w)\,
 \lambda_k(e_{\rho_k(v)0}\wedge e_{\rho_k(w)0}).}
\tag{5.45s}
\]

Thus slot four has no residual lexical comparison: it is a weighted
incidence count across the exact distance-one and distance-two length
boundaries of the connector chain.  The incidence value is not evaluated
here.

The fixed-base part of slot four does vanish.  By (5.45n),

\[
 q_4\overline B_4=t\,e_{\texttt{Tct}}=e_{\texttt{ct}},
\tag{5.45t}
\]

so the translated base vertex is not \(t\)-initial and has length two.
For one 42-edge increment, the frozen canonical labels in
[`.scratch/period_two_diagonal_pure_p_raw_manifest.json`](../../.scratch/period_two_diagonal_pure_p_raw_manifest.json)
give the following exact minimum among its \(t\)-initial slot-four heads;
their independent replay and all-power pump are bound in
[`.scratch/period_two_diagonal_pure_p_raw_certificate.md`](../../.scratch/period_two_diagonal_pure_p_raw_certificate.md):

\[
\begin{array}{c|cccc}
i&0&1&2&\geq3\\ \hline
\min |tv|&29&53&77&101+24(i-3).
\end{array}
\]

The two-step shell is the xor of the increments at \(i\) and \(i+1\);
collisions can only delete rows.  A non-\(t\)-initial shell head is in the
same class as the base and cannot invert under \(T\).  A \(t\)-initial
shell head has length at least \(29\), so its gap from the base is greater
than one and (5.45q) again excludes inversion.  Therefore

\[
\boxed{
 \lambda_k\Pi_{\rho_k}^\wedge
  \operatorname{PInv}_{T}
  \left(e_{\texttt{ct}},\,t(K_{i,4}+K_{i+2,4})\right)
 =0
 \qquad(k=1,\ldots,14,\ i\geq0).}
\tag{5.45u}
\]

The source incidence \(\Xi_{k,4}(i+2)+\Xi_{k,4}(i)\) remains unevaluated.
In particular, unreduced common-phase fragments such as an initial
\(\texttt{tT}\) may cancel; their blockwise first letter cannot be used in
(5.45s).

The fully reduced labels nevertheless give a constant-size source
interface.  Index the three copies of
\(E=\texttt{aGbAAG}\) in
\(P_*=E^3\) by their zero-based forest positions.  For the slot-four heads
in one powered \(P_*\)-block at level \(h\geq1\), the canonical first-letter and
length data are

\[
\begin{array}{c|ccc}
\text{positions}&0,6,12&3,9,15&4,10,16\\ \hline
\text{first-letter class}&\text{not \(t\)-initial}&t\text{-initial}
 &t\text{-initial}\\
\text{length offsets from }24h&(5,13,21)&(5,13,21)&(6,14,22).
\end{array}
\tag{5.45v}
\]

Thus (5.45r) selects exactly

\[
 \mathcal P_4
 =\{(0,3),(0,4),(6,9),(6,10),(12,15),(12,16)\}.
\tag{5.45w}
\]

There are no other slot-four incidences.  The five \(P_1\) heads are all
non-\(t\)-initial, with length offsets
\(\{2,8,10,15,27\}\).  Against a \(P_*\) block at the same level none has
gap zero or one; against the next level the smallest possible gap is two.
Between successive \(P_*\)-blocks the smallest eligible gap is eight.
The component-2 \(w\), component-3 \(w\), and component-3 \(z\) connector
heads are non-\(t\)-initial; at the terminal level they have offsets
\(5,6,7\) relative to the next \(P_*\)-block and are longer than every
\(t\)-initial head in the last present block.  Hence they contribute no
pair in (5.45r).

For \(h\geq1\), let \(H_{h,r}\) be the canonical positive head at position
\(r\) of the level-\(h\) \(P_*\)-block, and put

\[
 C_{k,4}(h)
 :=\sum_{(r,s)\in\mathcal P_4}
 \lambda_k\!\left(
 e_{\rho_k(H_{h,r})0}\wedge e_{\rho_k(H_{h,s})0}
 \right).
\tag{5.45x}
\]

Invariance of \(\lambda_k\) permits the head labels in (5.45x) in place
of the \(T\)-translated output labels of (5.45r).  At level zero the common
initial \(\texttt a\)-edge of the \(P_1\) and \(P_*\) root paths cancels;
this changes only the fixed seed value of \(\Xi_{k,4}\).  Every later
block has the six incidences (5.45w).  When \(K_i\) is replaced by
\(K_{i+2}\), all old blocks and the fixed seed cancel, and the connector
exclusion above leaves

\[
\boxed{
 \Xi_{k,4}(i+2)+\Xi_{k,4}(i)
 =C_{k,4}(i+1)+C_{k,4}(i+2).}
\tag{5.45y}
\]

Thus the complete slot-four source remainder is twelve explicit
finite-action weights, not a growing old-ray sum.  Their evaluation is
sharpened below.

The repeated block gives an exact covariance description, but not a
general vanishing theorem.  In the forest basis put

\[
 A=t,\qquad
 D=AB^{-1}GA^{-1}=\texttt{tcTctcTc},\qquad
 \delta=GA^2B^{-1}GA^{-1}=\texttt{ctcTTctttcTctcTc}.
\tag{5.45z}
\]

Here \(\delta\) is the quotient endpoint action of one stored
\(E=\texttt{aGbAAG}\) copy.  If that copy starts at \(z\), its three
untransformed incidence vertices at positions \(0,3,4\) are

\[
 A^{-1}z,\qquad B^{-1}GA^{-1}z,\qquad AB^{-1}GA^{-1}z.
\]

Translate them simultaneously by the positive occurrence action \(q_4=A\).
By invariance of \(\lambda_k\), the two weights are unchanged, while the
translated positive heads are

\[
 z,\qquad Dz,\qquad ADz.
\tag{5.45aa}
\]

All products in (5.45aa)--(5.45ad) denote the left action on \(X\) followed
by canonicalization.

For \(h\geq1\), if \(z_0\) includes the fixed component root and
\(z_{h,j}=\delta^{3h+j}z_0\), then the six-pair formula (5.45x) is exactly

\[
\boxed{
 C_{k,4}(h)
 =\sum_{j=0}^2\lambda_k\!\left(
 e_{\rho_k(z_{h,j})0}\wedge e_{\rho_k(Dz_{h,j})0}
 +e_{\rho_k(z_{h,j})0}\wedge e_{\rho_k(ADz_{h,j})0}
 \right).}
\tag{5.45ab}
\]

This formula retains the side on which the powered endpoint acts.  In
particular, advancing one copy conjugates the position-dependent left
multipliers; it is not one common left translate of both heads.

There is a useful exact local reduction.  Put
\(\widetilde\lambda_k=\lambda_k\circ\Pi_{\rho_k}^{\wedge}\).  Since
\(L_4=A-1\), reduction modulo two gives in the infinite exterior module

\[
 L_4^{(2)}(e_{A^{-1}z}\wedge e_{Dz})
 =e_z\wedge e_{ADz}+e_{A^{-1}z}\wedge e_{Dz}.
\tag{5.45ac}
\]

Every \(\widetilde\lambda_k\) kills the left side.  Consequently

\[
\boxed{
 \widetilde\lambda_k(e_z\wedge e_{Dz}+e_z\wedge e_{ADz})
 =\widetilde\lambda_k((e_z+e_{A^{-1}z})\wedge e_{Dz}).}
\tag{5.45ad}
\]

The right side is a one-sided \(A\)-boundary, not the diagonal boundary
in (5.45ac), so cokernel annihilation does not force it to vanish.
Likewise, quotient-action invariance does not identify different copies:
the left multiplier at position \(r\) advances by
\(\alpha_r\delta\alpha_r^{-1}\), which depends on \(r\).  Thus neither
\(C_{k,4}(h)=0\) nor constancy in \(h\) follows from invariance alone.

Finite-action periodicity does follow.  Put

\[
 r_k=\operatorname{ord}(\rho_k(\delta^3)).
\]

The complete-cover factorization gives the load-bearing identity

\[
 \delta^3=\operatorname{ev}_L(P_*)
 =Z_3=b_3^{-1}\gamma^{-1}b_3.
\]

Thus \(\delta^3\) is conjugate to \(\gamma^{-1}\), and its permutation
order is the order already listed for \(\gamma\) in (5.2).

In the established coordinate order, the eleven actions support coordinate
groups

\[
 (1),(2),(3),(4),(5),(6,7),(8),(9),(10),(11,12),(13,14).
\]

Thus their orders in (5.2) expand across the fourteen covectors as

\[
 (r_1,\ldots,r_{14})
 =(2,4,1,1,2,4,4,1,4,1,5,5,4,4).
\tag{5.45ae}
\]

Equation (5.45ab) therefore proves

\[
 C_{k,4}(h+r_k)=C_{k,4}(h)\qquad(h\geq1).
\tag{5.45af}
\]

Combining (5.45af) with (5.45y) completely evaluates the slot-four source
term in the four order-one coordinates:

\[
\boxed{
 \Xi_{k,4}(i+2)+\Xi_{k,4}(i)=0
 \qquad(k\in\{3,4,8,10\},\ i\geq0).}
\tag{5.45ag}
\]

The remaining values can now be obtained by direct finite-action
substitution, without a source-forest census.  Put

\[
 p_{0,k}=\rho_k(\texttt{ct})0,\quad
 a_k=\rho_k(A),\quad d_k=\rho_k(D),\quad
 \eta_k=\rho_k(\delta),
\]

and, for a finite-action point \(p\), define

\[
 \phi_k(p)
 :=\lambda_k(e_p\wedge e_{d_kp}+e_p\wedge e_{a_kd_kp}).
\tag{5.45ah}
\]

Equation (5.45ab) becomes the finite orbit sum

\[
 C_{k,4}(h)
 =\sum_{j=0}^2\phi_k(\eta_k^{3h+j}p_{0,k}).
\tag{5.45ai}
\]

Substitution of the pinned eleven permutation actions and fourteen
covectors gives the following complete table.  Each \(C\)-row is indexed by
\(h\bmod r_k\), on the proved domain \(h\geq1\); the \(S\)-row is indexed by
\(i\bmod r_k\), where
\(S_{k,4}(i)=C_{k,4}(i+1)+C_{k,4}(i+2)\).

\[
\begin{array}{c|c|c|c}
k&r_k&C_{k,4}&S_{k,4}\\ \hline
1&2&(0,0)&(0,0)\\
2&4&(0,1,0,1)&(1,1,1,1)\\
3&1&(1)&(0)\\
4&1&(0)&(0)\\
5&2&(1,1)&(0,0)\\
6&4&(0,0,0,0)&(0,0,0,0)\\
7&4&(1,1,1,1)&(0,0,0,0)\\
8&1&(0)&(0)\\
9&4&(1,0,1,0)&(1,1,1,1)\\
10&1&(1)&(0)\\
11&5&(0,0,0,0,0)&(0,0,0,0,0)\\
12&5&(1,1,1,1,1)&(0,0,0,0,0)\\
13&4&(0,0,0,0)&(0,0,0,0)\\
14&4&(1,1,1,1)&(0,0,0,0).
\end{array}
\tag{5.45aj}
\]

For a structural check on the constant rows, whenever \(\rho_k(c)=1\),
the literal words give \(d_k=1\) and \(\eta_k=a_k\).  Then
\(\phi_k(p)=\lambda_k(e_p\wedge e_{a_kp})\) is constant along the powered
orbit by invariance.  This covers coordinates \(3,5,6,7,11,12\).  In the
only two nonzero source rows, the local orbit weights alternate: direct
substitution gives \(C_{2,4}=(0,1,0,1)\) and
\(C_{9,4}=(1,0,1,0)\).  The remaining pinned rows are the constant or zero
rows displayed in (5.45aj).  Terminal-\(c\) canonicalization does not alter
the table because every pinned \(\rho_k(c)\) fixes the distinguished point
zero.

Thus the slot-four source remainder is completely evaluated for every
index:

\[
\boxed{
 \bigl(S_{1,4}(i),\ldots,S_{14,4}(i)\bigr)
 =\texttt{01000000100000}
 \qquad(i\geq0).}
\tag{5.45ak}
\]

This is only the differentiated-inversion source contribution from slot
four.  It is not the complete crossed derivative \(R_{k,i}\).

The fixed-base polarization in slot three also vanishes.  Recall
\(\overline B_3=e_{\texttt{TTct}}\).  Direct canonical reduction gives

\[
 q_3\texttt{TTct}=\texttt{ctcT},
 \qquad
 \operatorname{cvert}(m_3\texttt{ctcT})=\texttt{Tct},
\tag{5.45al}
\]

of lengths four and three.  Put
\(\beta_i=K_i+K_{i+1}\).  The frozen occurrence-9 canonical records and
their approved all-power pump give

\[
 \min\{|x|:x\in\operatorname{supp}(q_3\beta_{i,3})\}
 =32+24i.
\tag{5.45am}
\]

The two-step shell is
\(q_3(K_{i,3}+K_{i+2,3})
  =q_3(\beta_{i,3}+\beta_{i+1,3})\);
collision aggregation can only delete equal rows.  Since
\(|m_3|=7\), (5.46b) lowers a shell length by at most eight.  Thus every
transformed shell head has length at least \(24\), while the transformed
base in (5.45al) has length three.  The base precedes every shell head
both before and after multiplication by \(m_3\).  Therefore

\[
\boxed{
 \lambda_k\Pi_{\rho_k}^{\wedge}
 \operatorname{PInv}_{m_3}
 \left(q_3\overline B_3,\,
       q_3(K_{i,3}+K_{i+2,3})\right)
 =0
 \qquad(k=1,\ldots,14,\ i\geq0).}
\tag{5.45an}
\]

Slot two has an exact constant-size source interface.  Here
\(m_2=B=\texttt{ctcTcTctc}\) and
\(B^{-1}=\texttt{cTctctcTc}\).  For a protected canonical vertex \(x\),
let \(\kappa_B(x)\) be the cancellation depth between its prefix and
\(B^{-1}\).  The stable slot-two rows at level \(h\geq1\) are the four
\(P_1\) rows \(a,b,c,d\) at positions \(1,9,10,13\), the three \(P_*\)
rows \(e,f,g\) at positions \(2,8,14\), and the sole terminal \(z\)-row.
Their complete canonical length data are

\[
\begin{array}{c|rrrrrrrr}
 &a&b&c&d&e&f&g&z\\ \hline
 |x|-24h&3&15&22&26&4&12&20&6\\
 \kappa_B(x)&0&1&1&9&9&9&9&9\\
 |Bx|-24h&12&22&29&17&-5&3&11&-3.
\end{array}
\tag{5.45ao}
\]

All these protected words are longer than \(B\), and their terminal
canonical branch is fixed, so
\(|Bx|=|x|+9-2\kappa_B(x)\).  The original within-level order is

\[
 a<e<f<b<g<c<d,
\]

whereas the transformed order is

\[
 e<f<g<a<d<b<c.
\]

Consequently the exact reversal sets are

\[
\begin{aligned}
 W_h={}&\{(a_h,e_h),(a_h,f_h),(a_h,g_h),
          (b_h,g_h),(b_h,d_h),(c_h,d_h)\},\\
 A_h={}&\{(b_h,e_{h+1}),(c_h,e_{h+1}),(c_h,f_{h+1})\},\\
 T_h={}&\{(b_h,z_{h+1}),(c_h,z_{h+1})\}.
\end{aligned}
\tag{5.45ap}
\]

There are no transformed-length ties.  Levels separated by at least two
cannot interact, and no other slot-two connector row exists.  The only
\(P_1/P_*\) common edge lies in slot four, so (5.45ao)--(5.45ap) are already
collision-first in slot two.

Put

\[
 \omega_k(x,y)
 :=\widetilde\lambda_k(e_{Bx}\wedge e_{By})
 =\widetilde\lambda_k(e_x\wedge e_y),
\qquad
 \omega_k(S):=\sum_{(x,y)\in S}\omega_k(x,y),
\tag{5.45aq}
\]

where the second equality is diagonal \(B\)-invariance.  Cancellation of
all shared old pairs between \(K_i\) and \(K_{i+2}\) now gives, for every
\(i\geq1\),

\[
\boxed{
 \Xi_{k,2}(i+2)+\Xi_{k,2}(i)
 =\omega_k(W_{i+1})+\omega_k(W_{i+2})
  +\omega_k(A_i)+\omega_k(A_{i+1})
  +\omega_k(T_i)+\omega_k(T_{i+2}).}
\tag{5.45ar}
\]

This is exactly \(6+6+3+3+2+2=22\) finite-action weights.  It is only the
slot-two inversion source, not the complete \(R_{k,i}\), and invariance
does not force its xor to vanish.  At \(i=0\), the stable terms
\(W_1,W_2,A_1,T_2\) remain valid; only the seed seam \(A_0\) and seed
terminal set \(T_0\) need a separate collision-aggregated finite table.

The stable slot-two weights can be evaluated directly in the pinned finite
actions.  It is essential to retain the canonical schema order

\[
 \text{fixed}_0\,\text{fixed}_1\,
 \text{core}^{\,3h}\,\text{fixed}_2;
\tag{5.45aw}
\]

point evaluation applies the rightmost factor first.  Substitution of the
eight row heads in (5.45ao) and the sets (5.45ap) into (5.45ar) gives the
following complete residue table for \(i\geq1\):

\[
\begin{array}{c|c|c}
k&r_k&S_{k,2}(i\bmod r_k)\\ \hline
1&2&(1,1)\\
2&4&(0,0,0,0)\\
3&1&(0)\\
4&1&(0)\\
5&2&(0,0)\\
6&4&(0,0,0,0)\\
7&4&(0,0,0,0)\\
8&1&(0)\\
9&4&(0,0,0,0)\\
10&1&(0)\\
11&5&(0,0,0,0,0)\\
12&5&(0,0,0,0,0)\\
13&4&(1,1,1,1)\\
14&4&(0,0,0,0).
\end{array}
\tag{5.45ax}
\]

For a structural check, the \(c\)-trivial actions turn every row into an
affine phase on the corresponding \(t\)-cycle, so the paired
\(W/A/T\)-terms cancel in coordinates \(3,5,6,7,11,12\).  The order-one
rows \(4,8,10\) cancel directly.  In the remaining finite orbits, exact
substitution leaves the constant survivors \(1,13\).  The old terminal
schema at exponent \(h\) already contains the base \(P_*\)-block and hence
represents the physical row \(z_{h+1}\) used by \(T_h\); applying a second
residue shift would be incorrect.

Hence the stable slot-two inversion source is

\[
\boxed{
 \bigl(S_{1,2}(i),\ldots,S_{14,2}(i)\bigr)
 =\texttt{10000000000010}
 \qquad(i\geq1).}
\tag{5.45ay}
\]

Equation (5.45ay) does not cover the seed seam \(A_0,T_0\), and it remains
only one component of the complete crossed derivative.

The seed can be evaluated separately from its canonical rows.  The exact
level-zero and terminal length ledger is

\[
\begin{array}{c|rrrrrrrr}
 &a_0&b_0&c_0&d_0&e_0&f_0&g_0&z_1\\ \hline
 |x|&3&15&22&26&4&12&20&30\\
 |Bx|&12&22&29&17&4&15&23&29.
\end{array}
\tag{5.45az}
\]

The protected full-depth \(B\)-cancellation in (5.45ao) does not apply to
the three level-zero \(P_*\) rows.  Their direct forms are

\[
 e_0=B^{-1}(GT)\texttt{ct},\quad
 f_0=B^{-1}(GT)\delta\texttt{ct},\quad
 g_0=B^{-1}(GT)\delta^2\texttt{ct},
\]

so multiplication by \(B\) gives the lengths \(4,15,23\) in (5.45az).
The old terminal schema at exponent zero is the physical \(z_1\); its
frozen output label has length \(29\).

The level-one transformed lengths for \(a_1,\ldots,g_1\) are

\[
 (36,46,53,41,19,27,35).
\]

Hence the exact seed reversal sets are

\[
\begin{aligned}
 A_0={}&\{(b_0,e_1),(c_0,e_1),(c_0,f_1),(g_0,e_1)\},\\
 T_0={}&\{(c_0,z_1)\}.
\end{aligned}
\tag{5.45ba}
\]

For the terminal tie, \(Bc_0\) and \(Bz_1\) both have length \(29\).
The latter begins \(\texttt{ctcTT}\), while the former begins
\(\texttt{ctcTc}\); since \(T<c\), one has \(Bz_1<Bc_0\), proving the
single reversal in \(T_0\).

Relative to the formal protected seed, (5.45ba) contributes the correction

\[
\begin{aligned}
 (\omega_k(g_0,e_1))_{k=1}^{14}
   &=\texttt{11101010100101},\\
 (\omega_k(b_0,z_1))_{k=1}^{14}
   &=\texttt{11111011100101},\\
 (\omega_k(g_0,e_1)+\omega_k(b_0,z_1))_{k=1}^{14}
   &=\texttt{00010001000000}.
\end{aligned}
\tag{5.45bb}
\]

Combining this correction with the stable formal value proves

\[
\boxed{
 \bigl(S_{1,2}(0),\ldots,S_{14,2}(0)\bigr)
 =\texttt{10010001000010}.}
\tag{5.45bc}
\]

Thus the complete slot-two inversion source is now the exact piecewise
all-index function

\[
\boxed{
 (S_{1,2}(i),\ldots,S_{14,2}(i))
 =
 \begin{cases}
 \texttt{10010001000010},&i=0,\\
 \texttt{10000000000010},&i\geq1.
 \end{cases}}
\tag{5.45bd}
\]

This still evaluates only the slot-two inversion source.

Finally, slot three has a sharper exact cancellation signature than the
generic band (5.46d).  Write

\[
 G=\texttt{ctcTTct},\qquad
 q_3=GA,\qquad m_3=G^{-1},\qquad m_3q_3=A.
\tag{5.45as}
\]

For \(u=\operatorname{cvert}(Av)\), the before/after labels in the
inversion test are \(\operatorname{cvert}(Gu)\) and \(u\).  Define

\[
 d(u)=\operatorname{LCP}(u,G^{-1})\in\{0,\ldots,7\}.
\tag{5.45at}
\]

On a protected word longer than seven, terminal-\(c\) deletion is inert and
\[
 |\operatorname{cvert}(Gu)|=|u|+7-2d(u).
\tag{5.45au}
\]

Pairs of equal depth retain their length difference and lexical order, so
they never reverse.  A reversing pair has distinct depths and pre-\(G\)
length gap at most fourteen.  Its exact truth is determined by the two
depths, the affine length offset, the first eight letters of each protected
word, and its terminal branch.  The eighth letter is required when depth
seven cancels the whole \(G^{-1}\) prefix.  More precisely, after a maximal
matched prefix of depth \(d\), reducedness forbids the next remainder
letter from being the inverse of the last matched letter, equivalently from
being the next residual \(G\)-letter.  Thus transformed words of unequal
depth differ at the first post-depth letter, and positions through
\(d+1\leq8\) suffice.

The complete semantic inventory consists of eleven powered families:
\(P_1\) positions \(2,4,6,7,11\), \(P_*\) positions
\(1,5,7,11,13,17\), and the three terminal families \(w_3,z_3,w_2\).
After collision aggregation, the two-step shell has 26 slot-three
coordinates.  Each shell coordinate sees at most two levels from each
powered family and the three terminal rows, giving at most

\[
 26(2\cdot11+3)+\binom{26}{2}=650+325=975
\tag{5.45av}
\]

prefiltered old--shell and shell--shell comparisons.  The strict depth,
length, and prefix tests in fact collapse this bound to a fixed
within-level graph.

Use the level variable \(n\geq1\), and name the five \(P_1\) families
\(a,b,c,d,e\) at positions \(2,4,6,7,11\), and the six \(P_*\) families
\(f,g,h,j,k,l\) at positions \(1,5,7,11,13,17\).  Their complete
protected signatures are

\[
\begin{array}{c|r|r|c|r}
x&|u_x|-24n&d(u_x)&\text{first eight letters}
  &|\operatorname{cvert}(Gu_x)|-24n\\ \hline
a&11&3&\texttt{TctcTctc}&12\\
b&9&3&\texttt{TctctcTc}&10\\
c&9&4&\texttt{TctttcTc}&8\\
d&16&7&\texttt{TcttcTcT}&9\\
e&28&3&\texttt{TctcTctt}&29\\
f&6&3&\texttt{TctcTTct}&7\\
g&6&0&\texttt{ttcTcTct}&13\\
h&14&3&\texttt{TctcTTct}&15\\
j&14&0&\texttt{ttcTcTct}&21\\
k&22&3&\texttt{TctcTTct}&23\\
l&22&0&\texttt{ttcTcTct}&29.
\end{array}
\tag{5.45bw}
\]

Every row ends in \(\texttt t\).  The output \(u_x\)-order is

\[
 f<g<b<c<a<h<j<d<k<l<e,
\]

while the input \(Gu_x\)-order before applying \(m_3=G^{-1}\) is

\[
 f<c<d<b<a<g<h<j<k<l<e.
\]

The length-\(29\) input tie \(l/e\) does not reverse: the respective
prefixes are \(\texttt{ctcTT}\) and \(\texttt{ctcTc}\), and \(T<c\).
Thus the exact within-level reversal graph is

\[
\begin{aligned}
 \mathcal W_n=\{&
 (g_n,b_n),(g_n,c_n),(g_n,a_n),(g_n,d_n),\\
 &(b_n,c_n),(b_n,d_n),(a_n,d_n),
 (h_n,d_n),(j_n,d_n)\}.
\end{aligned}
\tag{5.45bx}
\]

There is no cross-level reversal:

\[
 28<24+6,\qquad 29<24+7.
\tag{5.45by}
\]

The terminal families have the exact signatures

\[
\begin{array}{c|c|c|c}
 &|u|&|\operatorname{cvert}(Gu)|&d\\ \hline
 w_{3,i}=f_{i+1}&24i+30&24i+31&3\\
 z_{3,i}&24i+31&24i+34&2\\
 w_{2,i}&24i+32&24i+35&2.
\end{array}
\tag{5.45bz}
\]

Their order never reverses, and they remain strictly beyond the last
powered level.  The equality \(w_{3,i}=f_{i+1}\) is a semantic collision
and is merged before comparisons; it contributes no omitted pair.

Because the inversion input is \(Gu_x\) and its \(m_3\)-output is \(u_x\),
put

\[
 \theta_k(x,y)
 :=\widetilde\lambda_k(e_{u_x}\wedge e_{u_y}),
\qquad
 \theta_k(S):=\sum_{(x,y)\in S}\theta_k(x,y).
\tag{5.45ca}
\]

The \(u\)-labels in (5.45ca) are the output weights; the reversal predicate
itself remains the comparison between the input \(Gu\)-order and output
\(u\)-order.  All common old powered blocks cancel between the two
potentials; by (5.45bz) the terminal rows contribute no reversal, and the
collision \(w_{3,i}=f_{i+1}\) has already been merged.  Therefore, for
every \(i\geq0\),

\[
\boxed{
 \Xi_{k,3}(i+2)+\Xi_{k,3}(i)
 =\theta_k(\mathcal W_{i+1})
  +\theta_k(\mathcal W_{i+2}).}
\tag{5.45cb}
\]

This is exactly \(9+9=18\) finite-action weights.  There is no seed
exception: the unprotected level zero is common to both potentials and
cancels, while both surviving levels are at least one.  It remains only
to evaluate these eighteen weights in the pinned finite actions.

Put

\[
 C_{k,3}(n):=\theta_k(\mathcal W_n)\qquad(n\geq1),
 \qquad
 S_{k,3}(i):=C_{k,3}(i+1)+C_{k,3}(i+2).
\tag{5.45cc}
\]

The protected labels in (5.45bw) have the common exact form

\[
 u_x(n)=P_x\,\texttt{cTctttcT}^{\,3n}\texttt{ct},
\tag{5.45cd}
\]

where the seven prefixes needed by (5.45bx) are

\[
\begin{array}{c|c@{\qquad}c|c}
x&P_x&x&P_x\\ \hline
a&\texttt{TctcTctcT}&b&\texttt{TctctcT}\\
c&\texttt{TctttcT}&d&\texttt{TcttcTcTctttcT}\\
g&\texttt{ttcT}&h&\texttt{TctcTTctttcT}\\
j&\texttt{ttcTcTctttcT}&&
\end{array}
\tag{5.45ce}
\]

Direct substitution of these seven words and the nine pairs in
(5.45bx) into the pinned actions and covectors gives the complete table
below.  Each \(C\)-row is indexed by \(n\bmod r_k\), using positive
levels, and each \(S\)-row by \(i\bmod r_k\).

\[
\begin{array}{c|c|c|c}
k&r_k&C_{k,3}&S_{k,3}\\ \hline
1&2&(0,1)&(1,1)\\
2&4&(1,0,0,1)&(0,1,0,1)\\
3&1&(1)&(0)\\
4&1&(0)&(0)\\
5&2&(1,1)&(0,0)\\
6&4&(0,0,0,0)&(0,0,0,0)\\
7&4&(1,1,1,1)&(0,0,0,0)\\
8&1&(1)&(0)\\
9&4&(1,1,0,0)&(1,0,1,0)\\
10&1&(1)&(0)\\
11&5&(0,0,0,0,0)&(0,0,0,0,0)\\
12&5&(1,1,1,1,1)&(0,0,0,0,0)\\
13&4&(1,0,1,0)&(1,1,1,1)\\
14&4&(1,1,1,1)&(0,0,0,0).
\end{array}
\tag{5.45cf}
\]

The constant rows in (5.45cf) provide an internal orbit check.  The only
nonconstant source phases are coordinate 2, which is one on odd \(i\),
and coordinate 9, which is one on even \(i\); coordinates 1 and 13 are
constant one.  Therefore the exact slot-three source vector is

\[
\boxed{
 (S_{1,3}(i),\ldots,S_{14,3}(i))
 =
 \begin{cases}
 \texttt{10000000100010},&i\equiv0\pmod2,\\
 \texttt{11000000000010},&i\equiv1\pmod2.
 \end{cases}}
\tag{5.45cg}
\]

For clarity, define the complete differentiated-inversion source, but not
the complete crossed derivative, by

\[
 \mathcal S_{k}(i):=S_{k,2}(i)+S_{k,3}(i)+S_{k,4}(i).
\tag{5.45ch}
\]

Xoring (5.45ak), (5.45bd), and (5.45cg) yields the all-index identity

\[
\boxed{
 (\mathcal S_1(i),\ldots,\mathcal S_{14}(i))
 =
 \begin{cases}
 \texttt{01010001000000},&i=0,\\
 \texttt{00000000100000},&i\geq1\text{ odd},\\
 \texttt{01000000000000},&i\geq2\text{ even}.
 \end{cases}}
\tag{5.45ci}
\]

Thus the entire differentiated-inversion contribution is reduced to one
alternating coordinate after the seed: coordinate 9 on odd indices and
coordinate 2 on positive even indices.  The seed retains coordinates
2, 4, and 8.  Formula (5.45ci) is not the full \(R_{k,i}\): the remaining
one-vertex transport and ordered local derivative profiles must still be
combined before any constancy or AK(3) conclusion.

Define the post-inversion remainder

\[
 \mathcal N_{k,i}:=R_{k,i}+\mathcal S_k(i).
\tag{5.45cj}
\]

This definition removes exactly the differentiated section-order inversion
term in (5.45e), including all three surviving relative kernels and their
fixed-base polarizations.  It does not remove the ordered-half profiles of
the product and inverse terms in (5.25)--(5.26).

For source-labelled parity currents put

\[
 H_k(u,v)
 :=\sum_{x<y}u_xv_y\,
 \lambda_k\!\left(
 e_{\rho_k(x)0}\wedge e_{\rho_k(y)0}
 \right).
\tag{5.45ck}
\]

The two basic identities are

\[
 H_k(u,v)+H_k(v,u)=b_{\lambda_k}(\pi_ku,\pi_kv),
 \qquad
 H_k(v,v)=q_{\lambda_k}(\pi_kv).
\tag{5.45cl}
\]

Thus a product node with old linear states \(a,b\), increments
\(\delta a,\delta b\), left quotient \(q\), and fixed linear section defect
\(o_{q,r}\) retains the four ordered profiles

\[
\boxed{
\begin{aligned}
 &H_k(\delta a,qb),\qquad H_k(a,q\delta b),\\
 &H_k(\delta a,q\delta b),\qquad
 H_k(\delta a+q\delta b,o_{q,r}).
\end{aligned}}
\tag{5.45cm}
\]

At an inverse node, the self terms in (5.26) contribute

\[
 b_{\lambda_k}(\pi_ka,\pi_k\delta a)
 +q_{\lambda_k}(\pi_k\delta a),
\tag{5.45cn}
\]

before the subsequent fixed literal multiplication.  In particular, the
direction-square term is not killed by the ordered-half reader; replacing
that reader by the exterior quotient would incorrectly kill it.

The lifted finite-group states (5.34) determine the right sides of
(5.45cl) and (5.45cn), but they do not determine an individual
\(H_k(u,v)\) in (5.45cm): the strict source order \(x<y\) is applied before
finite projection.  Likewise the one-vertex value (5.37) is not determined
by the finite point \(\rho_k(x)0\).  Therefore neither a scalar projected
state nor a finite exterior tensor state proves period from \(i=3\).

The exact next structural alternative is either to pair the complete AST
xor of (5.45cm) into the finite-state combinations (5.45cl), or to retain
all four ordered profiles in the protected comparator catalog of Sections
5.4--5.6.  Until that evaluation is made, (5.45cj) supplies no smaller
window than the conservative onset 673 proved below.

Before the explicit reductions (5.45ao)--(5.45ci), a direct expansion of
the slot-two and slot-three kernels
contains the weighted prefix families

\[
\boxed{
 \sum_{0\leq h\leq i}w_{\alpha,k}(h)
 \left[
 \operatorname{cvert}(A_\alpha R_\alpha^hB_\alpha)
 <\operatorname{cvert}(A_\beta R_\beta^{\,i+\delta}B_\beta)
 \right],}
\tag{5.46}
\]

together with the same comparison after left multiplication by each fixed
occurrence prefix and \(\delta\in\{0,1,2\}\).  Equality and
terminal-\(c\) branches are retained.  The new--new part is bounded, but
the old--new sums run over the complete old \(P\)-ray.

After the relative-action compression, those formal prefix sums are
supported only at a bounded length boundary.  For a reduced multiplier
\(m\), put

\[
 \ell(m):=|m|+1.
\tag{5.46a}
\]

Reduced left multiplication changes the length of a canonical vertex by
at most \(|m|\).  If the whole vertex cancels, the final choice of the
canonical right-\(\langle c\rangle\) representative can remove at most one
additional terminal \(c\).  Therefore

\[
 \bigl||\operatorname{cvert}(mx)|-|x|\bigr|\leq\ell(m).
\tag{5.46b}
\]

If \(x<y\) and
\(|y|-|x|>2\ell(m)\), (5.46b) leaves
\(|\operatorname{cvert}(mx)|<
  |\operatorname{cvert}(my)|\);
the pair cannot invert.  Hence

\[
\boxed{
 \operatorname{supp}\operatorname{Inv}_m
 \subseteq
 \{(x,y):x<y,\ |y|-|x|\leq2\ell(m)\}.}
\tag{5.46c}
\]

For the two remaining multipliers,

\[
 |m_2|=9,\quad |m_3|=7,\qquad
 2\ell(m_2)=20,\quad2\ell(m_3)=16.
\tag{5.46d}
\]

Expanding
\(\Xi_{k,s}(i+2)+\Xi_{k,s}(i)\) against
\(K_{i+2,s}=K_{i,s}+(K_{i,s}+K_{i+2,s})\) cancels every old--old pair.
Only old--shell and shell--shell pairs remain.  On a protected old/shell
template pair with

\[
 |U(h)|=24h+\alpha,\qquad |V(i)|=24i+\beta,
\]

an old--new inversion can occur only if

\[
 |24(h-i)+\alpha-\beta|\leq2\ell(m_s).
\tag{5.46e}
\]

The interval of possible integers \(h-i\) has length
\(4\ell(m_s)/24<2\).  Thus every protected template pair contributes on
at most two affine boundary rays, rather than on a genuine prefix
\(0\leq h\leq i\).  Finite unprotected levels and shell--shell terms remain
a finite catalog of direct one-parameter families.  This boundary
localization removes the parity prefix summation from the relative
inversion remainder.  At that stage it did not evaluate the surviving rays
or improve the leaf-schema onset \(99\); the later exact source evaluations
(5.45bd) and (5.45cg) remove those inversion rays, while the full AST audit
in Section 5.6 supplies the conservative onset 673 for the remaining
ordered profiles.

The four-cell raw pumps do not classify these individual prefixes.
Sections 5.4--5.6 retain the direct-comparator theorem and the source-bound
onset as an independent conservative fallback.

### 5.4 Common-phase comparator theorem

The required comparator has a general eventual-period theorem.  Call

\[
 U(h)=\operatorname{cvert}(AR^hB),
 \qquad
 V(i)=\operatorname{cvert}(CS^{i+\delta}D)
\tag{5.47}
\]

protected beyond \((H,I)\) if \(R,S\) are nonempty cyclically reduced
words, the displayed power seams survive reduction for \(h\geq H\) and
\(i\geq I\), and the terminal-\(c\) branch of
\(\operatorname{cvert}\) is fixed on each template.  Fixed left
multiplication is normalized before this definition is applied; one may
not apply \(\operatorname{cvert}\) factorwise.

#### Theorem 5.2 (eventual semilinear comparator)

For protected templates (5.47), there are effectively computable
\(N_{\mathrm{cmp}}\) and \(\epsilon\in\{0,1\}\) such that, for
\(h,i\geq N_{\mathrm{cmp}}\),

\[
\boxed{
 [U(h)<_{\mathrm{sl}}V(i)]
 =
 [ah+\alpha<bi+\beta]
 +\epsilon[ah+\alpha=bi+\beta],}
\tag{5.48}
\]

where \(a=|R|\), \(b=|S|\), and \(\alpha,\beta\) include the fixed
offsets and terminal deletions.  The two terms on the right are disjoint.
The same conclusion holds after any two fixed left multipliers, after
splitting the finitely many boundary phases needed to obtain protected
templates.

#### Proof

Unequal lengths decide shortlex order and give the first term in (5.48).
On the equality line

\[
 ah+\alpha=bi+\beta,
\tag{5.49}
\]

put \(g=\gcd(a,b)\).  If \(g\nmid\beta-\alpha\), there is no equality
case.  Otherwise the nonnegative solutions form one arithmetic ray

\[
 (h,i)=(h_0+(b/g)t,\ i_0+(a/g)t).
\tag{5.50}
\]

Compare the two periodic interiors after their fixed prefixes.  If they
disagree, their first mismatch is fixed once both cores reach it.  If they
agree through an overlap of length \(a+b-g\), Fine--Wilf gives a common
primitive word with compatible phase.  Absorb that phase into the fixed
ends.  Once the repeated interiors also exceed the terminal window
\(|B|+|D|+a+b\), the lexical comparison is a single fixed boundary
comparison, or the two words are equal.  Hence the equality-line bit is
eventually the constant \(\epsilon\).  This proves (5.48).

A fixed left word cancels only a bounded prefix.  After that boundary is
shielded, its whole-word reduction and final
\(\operatorname{cvert}\) again have protected form.  This proves the last
assertion. \(\square\)

Equivalently, every comparator in Theorem 5.2 is semilinear outside finite
horizontal and vertical strips: it is one rational affine half-plane plus,
possibly, the tail of one arithmetic equality ray.

#### Theorem 5.3 (weighted prefix periodicity)

Let \(w(h,i)\in\mathbb F_2\) be eventually bi-periodic, with \(h\)-period
\(r\) and \(i\)-period \(s\).  Then

\[
 F(i)=\sum_{0\leq h\leq i}
 w(h,i)[U(h)<_{\mathrm{sl}}V(i)]
\tag{5.51}
\]

is ultimately periodic.  Its preperiod and a valid period are effectively
computable from the protected templates and \(r,s\).

#### Proof

In the stable range, the strict-length part is a periodic prefix cut at

\[
 M(i)=\min\!\left(
 i,\left\lfloor\frac{bi+\beta-\alpha-1}{a}\right\rfloor
 \right).
\tag{5.52}
\]

For fixed \(i\bmod s\), the prefix xor of an \(r\)-periodic sequence has
endpoint period dividing \(2r\).  Put
\(a'=a/g\), \(b'=b/g\).  One safe period for (5.52) is

\[
 P_{\mathrm{cut}}
 =\operatorname{lcm}\!\left(
 s,\ 2r,\
 a'\frac{2r}{\gcd(2r,b')}
 \right).
\tag{5.53}
\]

The third entry makes the affine floor advance by a multiple of \(2r\);
the second also covers the branch \(M(i)=i\).

If the equality ray (5.50) is present and \(\epsilon=1\), its weight has
\(t\)-period

\[
 T_{\mathrm{eq}}
 =\operatorname{lcm}\!\left(
 \frac r{\gcd(r,b')},
 \frac s{\gcd(s,a')}
 \right),
\tag{5.54}
\]

and hence \(i\)-period \(P_{\mathrm{eq}}=a'T_{\mathrm{eq}}\).
Thus

\[
 P=\operatorname{lcm}(P_{\mathrm{cut}},P_{\mathrm{eq}})
\tag{5.55}
\]

is valid after increasing the preperiod past the protected-normal-form,
Fine--Wilf, terminal-window, weight-period, and floor-branch thresholds.
Omit \(P_{\mathrm{eq}}\) when the equality correction is absent.
The finitely many values \(h<H\) contribute an eventually \(s\)-periodic
term.  This proves the theorem. \(\square\)

Every old path row in \(D_i\) has the finite-family form

\[
 \operatorname{cvert}\!\left(
 m_{\nu k}E(P_{\nu,<k})p_\nu^h r_\nu
 \right),
 \qquad
 0\leq h\leq i+\delta_{\nu k},
 \quad \delta_{\nu k}\in\mathbb Z\text{ fixed},
\tag{5.56}
\]

and cyclic reduction absorbs the fixed conjugating ends into a protected
template; finitely many negative-boundary cases are split off.  Every row
of the shell \(E_i\) is fixed or has protected
one-core exponent \(i+\delta\).  The fixed base and doubled anchors are
exponent-zero families.  Equality fibers are collision-aggregated before
quadratic evaluation, and negative occurrences only reverse or complement
the same finite comparator list.

This catalog also contains every ordered local profile in (5.45cm).  At a
fixed product node of the residual AST, the quotient words \(q,r\) and the
section-defect current \(o_{q,r}\) are fixed.  Expanding each old linear
state into its old path rows, base, anchors, and fixed literal current, and
each increment into its two-step shell, turns the four \(H_k\)-terms into a
finite sum of comparisons of the form (5.46).  The first two are old--shell
profiles, the third is shell--shell, and the fourth is shell--fixed.
Subsequent outer AST transports only add one of the finitely many fixed left
multipliers already allowed in Theorem 5.2.  At inverse nodes (5.45cn) is a
finite projected \(b/q\) expression; its subsequent fixed multiplication
again produces only the same four typed profile families through (5.25).
Thus the comparator maximum below covers the product, inverse, and
\(o_{q,r}\) terms as well as the differentiated section-order inversion
term.  It does not infer their values from projected linear states.

The finite-action weights in (5.46) are bi-periodic on the lifted
right-deck prefix states.  Theorems 5.2--5.3 therefore apply to every
old--new order-reversal term; the new--new terms require only finitely many
shell comparisons.  Taking the maximum preperiod and least common multiple
over this finite catalog independently proves

\[
\boxed{
 \text{For each }1\leq k\leq14,\quad
 (R_{k,i})_{i\geq0}\text{ is ultimately periodic}.}
\tag{5.57}
\]

The exact common-phase data sharpen the period.  The frozen quadratic
manifest and its independent replay bind all 46 signed source contexts,
including the inactive collision fibers, to 152 path and slot-zero schemas
with

\[
 R_0=\texttt{cTctttcT},
 \qquad |R_0|=8,
 \qquad p_{\mathrm{multiplier}}=3.
\tag{5.58}
\]

The integral collision identity (2.3), applied before reduction modulo
two, removes the canceled long families and leaves the \(P_1\) and
\(P_*\) rays plus endpoint-transported fixed connectors.  Internal old
levels reuse the same protected terminal schemas; the initial level,
fixed base, doubled anchors, and short connectors are finite boundary
families.  Hence every unbounded old and shell template gains
\(R_0^3\) per unit parameter and has length slope

\[
 a=b=3|R_0|=24.
\tag{5.59}
\]

Fixed left occurrence words and whole-word \(\operatorname{cvert}\) can
alter the protected threshold and length offset, but not this slope.
For coordinate \(k\), take the two weight periods in Theorem 5.3 to be
\(r=s=m_k:=\operatorname{ord}\rho_k(\gamma)\).  Then
\(g=24\) and \(a'=b'=1\), so (5.53)--(5.55) give

\[
 P_{\mathrm{cut}}\mid2m_k,
 \qquad
 P_{\mathrm{eq}}\mid m_k,
 \qquad
 \operatorname{per}(R_k)\mid2m_k
\tag{5.60}
\]

after the protected threshold.  With the action orders in (5.2),

\[
\boxed{
 \exists N\ \forall k\in\{1,\ldots,14\}\ \forall i\geq N:
 \quad R_{k,i+40}=R_{k,i}.}
\tag{5.61}
\]

At this point \(N\) is only effective: the terminal schemas bind the common
core and factor order, not every pairwise comparison cutoff.  Sections
5.5--5.6 instantiate a conservative source-bound value \(N=673\),
certifying the finite window \(0\leq i\leq712\).  Thus (5.61) is not period from
\(i=3\), and no period two, \(R_{k,i}=0\), lift, or AK(3) conclusion
follows.

### 5.5 Exact onset functional

The missing onset is a finite maximum, not an unspecified compactness
constant.  After normalizing either the identity action or one fixed
occurrence action \(q\), write every old branch and shell branch as

\[
\begin{aligned}
 |U_{\alpha,q}(h)|&=24h+\ell_{\alpha,q}
 &&(h\geq H_{\alpha\beta q}),\\
 |V_{\beta,q}(i)|&=24i+\ell_{\beta,q}
 &&(i\geq I_{\alpha\beta q}),
\end{aligned}
\tag{5.62}
\]

where the pairwise protection bases include the whole-word reduction,
terminal-\(c\), Fine--Wilf/common-root phase, and fixed-suffix lexical
windows.  Let \(\delta_\alpha\) be the exact old-domain offset in
\(0\leq h\leq i+\delta_\alpha\), and put

\[
 d_{\alpha\beta q}
 :=\frac{\ell_{\alpha,q}-\ell_{\beta,q}}{24}.
\tag{5.63}
\]

When \(d_{\alpha\beta q}\in\mathbb Z\), the only unbounded equality line is
\(h=i-d_{\alpha\beta q}\).  A conservative onset for this ordered pair is

\[
\begin{aligned}
 N_{\alpha\beta q}:=\max\Bigg\{&
 I_{\alpha\beta q},\
 H_{\alpha\beta q}+
   \max\!\left(
   \left\lceil d_{\alpha\beta q}\right\rceil,
   -\delta_\alpha,0\right),\\
 &1+
 \max_{0\leq h<H_{\alpha\beta q}}
 \left\lfloor
 \frac{|U_{\alpha,q}(h)|-\ell_{\beta,q}}{24}
 \right\rfloor
 \Bigg\},
\end{aligned}
\tag{5.64}
\]

with empty maxima omitted and negative entries clipped at zero.  The
second term places the moving length cut and every integral equality
offset inside the protected old branch and places the active domain cap
\(i+\delta_\alpha\) there as well.  The third ensures that each
permanently present unprotected old level is strictly shorter than the
growing shell; its remaining finite-action weight is then periodic
without further shortlex changes.

For a direct one-parameter pair, including an endpoint connector against a
shell row or two new shell rows, let
\(N^{\mathrm{dir}}_{\beta\gamma q}\) be its pairwise protected comparison
onset.  Take the maxima over every slot-compatible pair and over the
identity and actual occurrence prefixes:

\[
\boxed{
 N_{\mathrm{cat}}
 :=\max\!\left\{
 \max_{\alpha,\beta,q}N_{\alpha\beta q},\
 \max_{\beta,\gamma,q}N^{\mathrm{dir}}_{\beta\gamma q}
 \right\}.}
\tag{5.65}
\]

Once the catalog verifies all protected forms and collision branches,
\(N=N_{\mathrm{cat}}\) is valid in (5.61).  The required records are
exactly:

1. all \(P_1/P_*\) old block-position families, including the inactive
   collision fibers, the fixed base rows, and endpoint connectors;
2. the \(q_i\) and \(q_{i+1}\) shell families and both slot-zero
   singletons;
3. collision/equality, old-before-shell, and
   \(q\)-transported order for every occurrence prefix of the slot;
4. the \(q_i\)-versus-\(q_{i+1}\) new--new shell comparisons; and
5. every finite level \(0\leq h<H_{\alpha\beta q}\).

The existing 1,128-pair chord ledger and 4,560-pair direct ledger compare
the tokens inside one increment \(q_i\).  They do not contain the complete
old \(D_i\) prefix against the two-step shell \(E_i=q_i+q_{i+1}\), so they
cannot supply (5.65) by reuse.  Formula (5.65) is the exact next
certificate interface.  Section 5.6 supplies a conservative source-bound
onset without claiming the exact minimum of (5.65).

### 5.6 A source-bound onset of 673

The common-phase source formulas give a conservative numerical onset
without enumerating parameter values.  First record a uniform bound on
each normalized fixed side of every comparator:

\[
\begin{array}{c|r}
\text{fixed factor}&\text{length bound}\\ \hline
\text{occurrence prefix}&11\\
\text{stored-edge multiplier}&9\\
\text{proper }P_1/P_*\text{ path prefix}&17\cdot9=153\\
\text{powered-end cyclic/rephasing side}&18\cdot9+8=170\\
\text{connector }w/z\text{ material}&3\cdot9=27\\
\text{component root}&2
\end{array}
\tag{5.66}
\]

The generator-image lengths are
\((1,9,7,1,9,7)\) for \(A,B,G,a,b,g\), so both path evaluation and the
edge-rule multipliers satisfy the displayed bounds.  The longest \(P\)
block has 18 forest letters; a proper prefix has at most 17.  Cyclic
reduction removes matching end pairs, and common-reference rephasing adds
less than one copy of the length-eight primitive.  The connector words
have forest length at most three, and the component roots are
\(\texttt{ct}\) or the identity.  Assigning all possible material to one
side is deliberately redundant but proves

\[
\boxed{L\leq11+9+153+170+27+2=372.}
\tag{5.67}
\]

This inventory covers all 46 pre-collision path contexts, including the
inactive fibers.  Their module and two occurrence-label schemas give 138
common-phase schemas.  The two slot-zero module schemas and their twelve
occurrence-label schemas give the other 14.  Thus all 152 schemas in
(5.58), as well as the direct shell pairs formed from them, are covered.
The eight fixed-base module words have length at most six, and slot-zero
fixed sides are shorter than (5.67).  Whole-word quotient reduction and
\(\operatorname{cvert}\) can only shorten these raw bounds.

The ordered product profiles (5.45cm) require one additional fixed-AST
ledger.  Count unreduced literal mass in the fully expanded residual AST;
inversion preserves this mass, and correction leaves contribute zero.  The
literal word lengths are

\[
 (|A|,|B|,|h_0|,|h_1|,|h_2|,|h_3|,
   |\operatorname{TARGET}|)
 =(23,18,7,0,6,1,1).
\]

Expansion of every conjugation into conjugator, payload, and inverse
conjugator gives

\[
\begin{array}{c|c|r}
\text{node}&\text{literal-mass recurrence}&\text{mass}\\ \hline
r&23+18+2\cdot7&55\\
s&18+55+2\cdot0&73\\
u&55+73+2\cdot6&140\\
z&140+73+2\cdot1&215\\
\text{root}&215+1&216.
\end{array}
\tag{5.67a}
\]

The raw recursive expansion has 23 literal leaf occurrences, four of which
are quotient-empty copies of \(h_1\); equivalently (5.67a) contains 19
nonempty literal blocks.  The load-bearing datum is the total unreduced
mass 216, not the block count.  Therefore every fixed node quotient and
every composed ancestor transport has length at most 216.

For a product node, the section-defect word representing \(o_{q,r}\) has
length at most

\[
 |q|+|r|+|qr|\leq216+216+432=864,
\tag{5.67b}
\]

so each of its Schreier support labels has length at most 864.  Higher
products transport an existing tensor linearly; they do not concatenate a
second defect current or a second old fixed side onto one comparator leg.
All ancestor transports compose into the single 216-letter allowance.
Thus assigning the leaf-schema bound, a node quotient, one section defect,
and one ancestor transport to the same side gives the deliberately
redundant uniform bound

\[
 \boxed{L_{\rm AST}\leq372+216+864+216=1668<2000.}
\tag{5.67c}
\]

We henceforth use the round bound \(L=2000\).  Before multiplication by
those fixed AST words, every unbounded source-domain exponent offset is
nonnegative and at most

\[
 0\leq\delta_{\rm src}\leq d:=2.
\tag{5.68}
\]

The offsets zero and one are the exact one-step source offsets; reindexing
the \(q_{i+1}\) half of \(E_i=q_i+q_{i+1}\) adds at most one.  Negative
boundary cases have already been split into finite families.  This is not
a bound on the powered exponent visible after normalization: a fixed
multiplier can cancel complete 24-letter cores.  The estimates below
therefore retain a two-sided fixed-word allowance instead of treating
\(d\) as a normalized exponent bound.

Put

\[
 J(L):=\max\!\left(
 3,\left\lceil\frac{4L+72}{24}\right\rceil
 \right).
\tag{5.69}
\]

The repeated core has length \(24\).  The quantity \(4L+72\) contains all
four fixed sides of a pair, a complete common-core overlap of length 24,
and both terminal windows with total allowance \(48\).  Hence, once both
exponents are at least \(J(L)\), fixed-left multiplication, whole-word
reduction, relative core phase, the fixed suffix comparison, and the
terminal-\(c\) branch are all protected.  Adding further complete cores
cannot change the comparison.

The source offset contributes at most \(d\), while the two normalized
words can each lose or gain the fixed allowance on both sides.  Including
the possible terminal-\(c\) deletion gives the safe two-sided length
allowance \(4L+1\).  Therefore a level at the moving strict cut or equality
line satisfies

\[
 h\geq
 i-d-\left\lfloor\frac{4L+1}{24}\right\rfloor-1.
\tag{5.70}
\]

Define

\[
 N(L,d):=
 J(L)+d+
 \left\lfloor\frac{4L+1}{24}\right\rfloor+1.
\tag{5.71}
\]

Then \(i\geq N(L,d)\) puts every moving cut and equality level inside the
protected range \(h\geq J(L)\).  The finitely many old levels
\(h<J(L)\) have the raw upper bound

\[
 |U(h)|\leq24(J(L)-1+d)+2L,
\tag{5.72}
\]

whereas a protected shell word has

\[
 |V(i)|\geq24i-2L-1.
\tag{5.73}
\]

At \(i=N(L,d)\), the difference between (5.73) and (5.72) is

\[
24\left\lfloor\frac{4L+1}{24}\right\rfloor
+47-4L>0.
\tag{5.74}
\]

Indeed, if \(4L+1=24f+r\) with \(0\leq r<24\), the expression in
(5.74) is \(48-r>0\).

Thus every finite old level is permanently shorter than the shell.
Direct endpoint/shell, shell/shell, slot-zero, fixed-base, and transported
comparisons are already protected by the same \(N(L,d)\).

Substituting \(L=2000\) and \(d=2\) gives

\[
 J=\left\lceil\frac{8072}{24}\right\rceil=337,\qquad
 N=337+2+\left\lfloor\frac{8001}{24}\right\rfloor+1=673.
\tag{5.75}
\]

Combining (5.61) with this source-bound onset proves the concrete theorem

\[
\boxed{
 R_{k,i+40}=R_{k,i}
 \qquad(1\leq k\leq14,\ i\geq673).}
\tag{5.76}
\]

Consequently the all-index identities (5.28) are equivalent to the finite
set

\[
\boxed{
 R_{k,i}=0
 \qquad(1\leq k\leq14,\ 0\leq i\leq712).}
\tag{5.77}
\]

This is \(14\cdot713=9{,}982\) bits.  No value in (5.77) is evaluated
here.  In particular, (5.76) is not a period-two theorem and proves no lift
or AK(3) conclusion.

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
