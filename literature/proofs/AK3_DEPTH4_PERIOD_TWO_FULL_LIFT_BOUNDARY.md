# Exact free-group lift boundary after the unary delta theorem

## Status

The proved identity

\[
u_{ij}=\delta_{ij}
\tag{0.1}
\]

does not construct a free-group lift and does not obstruct the complete
correction space.  Together with the coordinate-four theorem of Section
5.8, it gives a sharp class-two obstruction on the entire anchored
two-parameter family: every off-diagonal anchored correction fails the
full-wedge readout, and every diagonal anchored correction fails the fourth
finite-action readout.

The other fourteen finite-action coordinates reduce to the crossed
derivatives \(R_{k,i}\).  Their entire differentiated-inversion source is
now evaluated.  Literal-stream flattening absorbs every remaining product,
inverse, transport, and quotient-section ordered profile into one weighted
cut form.  The all-index target is therefore equivalent to the conservative
2,380-bit window \(R_{k,i}\) with \(1\leq k\leq14\) and
\(0\leq i\leq169\).  Section 5.7 proves the 167 coordinate-four values
\(R_{4,i}=0\) for \(3\leq i\leq169\), and Section 5.8 closes the three
coordinate-four seeds.  Thus all 170 coordinate-four values vanish and
exactly 2,210 values in the other thirteen coordinates remain unevaluated.
Section 3.1 now replaces that finite shadow by a universal
relative-displacement quotient of the full class-two cokernel.  It is
integrally of infinite free rank with additional infinite two-torsion, and
its mod-two reduction gives the next exact gate for arbitrary balanced
source-pair corrections.  Even simultaneous
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

### 3.1 Infinite relative-displacement quotient

Put \(H=\langle c\rangle\), so \(X=Q/H\), and reduce the exterior module
modulo two:

\[
 \overline W:=\Lambda^2\mathbb Z[X]\otimes\mathbb F_2.
\tag{3.11}
\]

Its basis is the set of unordered two-element subsets of \(X\).  Define the
relative-displacement index set

\[
 \mathscr D:=
 \left(
  (H\backslash Q/H)\setminus\{H\}
 \right)\big/\left(D\sim D^{-1}\right).
\tag{3.12}
\]

For two distinct vertices, put

\[
 \boxed{
 \Xi_0(e_{qH}\wedge e_{rH})
 :=\delta_{[Hq^{-1}rH]_\pm}
 \in\mathbb F_2^{(\mathscr D)}.}
\tag{3.13}
\]

This is well defined.  Changing the representatives of \(qH\) and \(rH\)
changes \(q^{-1}r\) only inside its \(H\)-double coset; diagonal left
translation leaves that double coset unchanged; and swapping the two
vertices replaces it by its inverse.  Conversely, equality of the
unoriented double cosets constructs a diagonal \(Q\)-translation between
the two unordered pairs.  Hence (3.13) is exactly the coinvariant map and

\[
 \boxed{
 \overline W_Q\cong\mathbb F_2^{(\mathscr D)}.}
\tag{3.14}
\]

The index set is explicit and infinite.  Every nontrivial \(H\)-double
coset has a unique reduced representative

\[
 t^{n_0}c\,t^{n_1}c\cdots c\,t^{n_k},
 \qquad n_j\ne0,
\tag{3.15}
\]

and inversion sends the exponent sequence
\((n_0,\ldots,n_k)\) to \((-n_k,\ldots,-n_0)\).  Working modulo two removes
the only orientation caveat: an orbit stabilizer which exchanges the two
vertices acts by minus one integrally but by one on \(\overline W\).

There is a stronger integral form.  Let \(\mathscr D_2\) be the set of
two-element inversion orbits \(\{D,D^{-1}\}\), and let \(\mathscr D_1\) be
the set of nonidentity inversion-fixed double cosets.  Then

\[
 \boxed{
 W_Q\cong
 \bigoplus_{\mathscr D_2}\mathbb Z
 \ \oplus\
 \bigoplus_{\mathscr D_1}\mathbb Z/2.}
\tag{3.15a}
\]

Choose one orientation \(D^+\) in every member of \(\mathscr D_2\).  If
\(D=Hq^{-1}rH\), the integral coinvariant map is

\[
 \Xi_{\mathbb Z}(e_{qH}\wedge e_{rH})
 =
 \begin{cases}
  +z_{\{D,D^{-1}\}},&D=D^+,\\
  -z_{\{D,D^{-1}\}},&D^{-1}=D^+,\\
  \bar z_D\in\mathbb Z/2,&D=D^{-1}.
 \end{cases}
\tag{3.15b}
\]

There are no further relations.  The free factor \(H\) is malnormal in
\(C_2*\mathbb Z\), so the pointwise stabilizer of two distinct vertices is
trivial.  A setwise stabilizer can only be the unique endpoint swap.  Such
a swap exists exactly when \(D=D^{-1}\), and it imposes only
\(z_D=-z_D\).  In the exponent normal form (3.15), this fixed-point
condition is

\[
 (n_0,\ldots,n_k)=(-n_k,\ldots,-n_0).
\tag{3.15c}
\]

In particular, a self-inverse sequence has an even number of \(t\)-blocks;
an odd number would force its nonzero middle exponent to equal its
negative.

For \(L_r=\sum_g a_{r,g}g\), diagonal \(Q\)-invariance gives

\[
\begin{aligned}
 \Xi_0(L_r^{(2)}w)
 &=\sum_g a_{r,g}\Xi_0(gw)\\
 &=\varepsilon(L_r)\Xi_0(w)=0,
 \qquad 0\le r\le4,
\end{aligned}
\tag{3.16}
\]

because all five exact operators have augmentation zero.  Therefore
\(\Xi_{\mathbb Z}\) and \(\Xi_0\) both descend through every second-layer
correction.  Integrally this gives the surjection

\[
 \boxed{
 \Xi_{\mathbb Z}:\mathcal C_2\twoheadrightarrow W_Q
 \cong
 \bigoplus_{\mathscr D_2}\mathbb Z
 \oplus
 \bigoplus_{\mathscr D_1}\mathbb Z/2.}
\tag{3.17}
\]

The one-block sequences \((n)\), paired with \((-n)\), give infinitely
many free summands, while the anti-palindromic two-block sequences
\((n,-n)\) give infinitely many inversion-fixed summands.  Thus
\(\mathcal C_2\) has a quotient of infinite free rank and also a quotient
with infinite \(\mathbb Z/2\)-rank.

Reducing the free coordinates modulo two and retaining the
inversion-fixed torsion coordinates recovers the surjective quotient

\[
 \boxed{
 \Xi:\mathcal C_2\twoheadrightarrow
 \mathbb F_2^{(\mathscr D)},
 \qquad
 \Xi([w])=\Xi_0(w\bmod2).}
\tag{3.17a}
\]

In particular, \(\mathcal C_2\) has an infinite-dimensional
characteristic-two quotient.  Every candidate first-layer correction must
satisfy the exact necessary condition

\[
 \boxed{
 \Xi_{\mathbb Z}(\Theta(F))=0,
 \qquad\text{hence}\qquad
 \Xi(\Theta(F))=0.}
\tag{3.18}
\]

The fifteen tracked bits factor through this single vector-valued
obstruction.  Indeed, an invariant finite-action pair weight is constant on
each diagonal \(Q\)-orbit of unordered pairs, so it is a scalar functional
of (3.13).  The full-wedge bit is the augmentation which sums every
\(\mathscr D\)-coordinate.  Thus \(\Xi\) strictly organizes and refines the
existing finite shadows; it is not another bounded point-action quotient.

Equation (3.18) is not sufficient for (3.8).  A global class-two
obstruction would follow from proving
\(\Xi_{\mathbb Z}(\Theta(F))\ne0\) for every finite balanced source pair;
the stronger mod-two claim \(\Xi(\Theta(F))\ne0\) would also suffice.  If a
balanced source pair kills the mod-two histogram, its signed integral
buckets, and then its complete class in \(\mathcal C_2\), must still be
evaluated.  Neither alternative is decided here.

### 3.2 Complete balanced-source expansion

The forest parametrization in Section 2 gives an exact anchored generating
family for
the complete source-pair space, including the formerly unused \(f_1\)
source.  Let \(\mathcal T_0,\mathcal T_1\) be the two forest components and,
for \(r\in\{0,1\}\), define

\[
 \lambda_r(v):=
 \sum_{x\in\mathcal T_0}[e_x](L_re_v).
\tag{3.19}
\]

Every \(L_r\) has total augmentation zero, so the two component sums of
\(L_re_v\) are \((\lambda_r(v),-\lambda_r(v))\).  Keep the slot-zero anchor
\(a=T\), for which \(\lambda_0(a)=1\).  For a source atom \((r,v)\), form
the source pair

\[
 s^{r,v}_j
 :=[j=r]e_v-[j=0]\lambda_r(v)e_a,
 \qquad j\in\{0,1\}.
\tag{3.20}
\]

Its boundary \(L_0s^{r,v}_0+L_1s^{r,v}_1\) is component-balanced.  Let
\(H_r(v)\in\mathcal H_{\mathrm{fin}}\) be (3.20) completed by the unique
finite forest flow in slots \(2,3,4\).  For \(r=0\), this is the anchored
direction \(H(v)\) used in the unary theorem.

If \(F\in\mathcal H_{\mathrm{fin}}\) has source pair \((f_0,f_1)\), its
balance condition is exactly

\[
 \sum_{r=0}^1\sum_v f_r(v)\lambda_r(v)=0.
\tag{3.21}
\]

The source pair of the finite sum
\(\sum_{r,v}f_r(v)H_r(v)\) equals \((f_0,f_1)\): the only additional source
is the anchor coefficient given by the negative of (3.21).  Both sides
have the same boundary, and finite forest boundary injectivity makes their
forest flows equal.  Therefore

\[
 \boxed{
 F=\sum_{r=0}^1\sum_v f_r(v)H_r(v).}
\tag{3.22}
\]

This is an integral identity of all five correction slots, not merely a
spanning statement modulo two.

Put

\[
\begin{aligned}
 q_\Xi(F)&:=\Xi(\Theta(F)),&
 C_\Xi&:=q_\Xi(0),\\
 U_\Xi(D)&:=q_\Xi(D)+C_\Xi,&
 B_\Xi(D,E)&:=q_\Xi(D+E)+q_\Xi(D)+q_\Xi(E)+C_\Xi.
\end{aligned}
\tag{3.23}
\]

Universal affine quadraticity and the tensor-diagonal propagation theorem
apply before every exterior readout, not only before the fifteen scalar
ones.  Consequently \(q_\Xi\) factors through
\(\mathcal H_{\mathrm{fin}}/2\mathcal H_{\mathrm{fin}}\), while \(B_\Xi\)
is biadditive and alternating.  Choose any total order on the source atoms
\(\alpha=(r,v)\), and write
\(\bar f_\alpha=f_r(v)\bmod2\).  Equations (3.22)--(3.23) give the exact
finite expansion

\[
\boxed{
\begin{aligned}
 q_\Xi(F)
 ={}&C_\Xi
 +\sum_\alpha \bar f_\alpha U_\Xi(H_\alpha)\\
 &+\sum_{\alpha<\beta}
   \bar f_\alpha\bar f_\beta
   B_\Xi(H_\alpha,H_\beta).
\end{aligned}}
\tag{3.24}
\]

The already excluded anchored family is detected by this stronger map:

\[
 \boxed{q_\Xi(D_{ij})\ne0\qquad(i,j\geq0).}
\tag{3.25}
\]

For \(i\ne j\), the full-wedge functional of \(q_\Xi(D_{ij})\) is one by
(4.4).  For \(i=j\), Section 5.8 and the base vector give

\[
 S_4(D_{ii})
 =U_4(D_{ii})+S_4(0)
 =V_{i,4}+(C_{14})_4
 =1+0=1.
\tag{3.25a}
\]

Since both scalar readouts factor through \(\Xi\), (3.25) follows.

Equation (3.24) also identifies why (3.25) does not settle (3.18).
Different translated wedges can occupy the same relative-displacement
bucket, and the mixed terms \(B_\Xi(H_\alpha,H_\beta)\) may cancel the
unary buckets.  For example, whenever the displayed vertices are distinct,

\[
 \Xi_0\left(
 e_H\wedge e_{gH}
 +e_{qH}\wedge e_{qgH}
 \right)=0,
\tag{3.26}
\]

because both wedges have the same relative double coset.  No existing
theorem excludes such bucket-paired tensors from the pulled-back mixed
polarization.  The exact next obligation is therefore to prove
noncancellation in at least one \(\mathscr D\)-coordinate for every finite
coefficient set in (3.24), or to construct a balanced coefficient set for
which the complete vector vanishes.

### 3.3 Exact vector-valued mixed kernel

The relative-displacement quotient packages the complete mixed
polarization, but it does not remove source shortlex.  Use the
collision-aggregated atomic-token universe \(\mathscr P\), literal
chronology \(<_\chi\), central labels \(\ell(p)\), and exact local tensors
\(T_p\) from Lemma 5.1b.  For an arbitrary intermediate tensor, define the
ordered-half histogram

\[
 W_\Xi(T):=
 \sum_{x<_{\rm sl}y}T_{x,y}\,
 \delta_{[Hx^{-1}yH]_\pm}
 \pmod2.
\tag{3.27}
\]

This map is only a bookkeeping reader on an intermediate tensor.  On the
final diagonal-free antisymmetric residual tensor it agrees with \(\Xi\);
it is not \(Q\)-equivariant term by term before that final cancellation.
Put

\[
\begin{aligned}
 \zeta_\Xi(p)&:=W_\Xi(T_p),\\
 K_\Xi(p,q)&:=
 [\ell(p)<_{\rm sl}\ell(q)]\,
 \delta_{[H\ell(p)^{-1}\ell(q)H]_\pm},
 \qquad p<_\chi q,
\end{aligned}
\tag{3.28}
\]

with \(K_\Xi(p,q)=0\) when the two labels agree.  For any zero-linear
endpoint with activity mask \(a\), the literal-stream theorem applied
coordinatewise in \(\mathbb F_2^{(\mathscr D)}\) gives

\[
 \boxed{
 \Phi_\Xi(a)
 =\sum_p a(p)\zeta_\Xi(p)
 +\sum_{p<_\chi q}a(p)a(q)K_\Xi(p,q).}
\tag{3.29}
\]

If \(a\) is the fixed base mask and \(d\) is the toggle mask of a
homogeneous direction \(D\), polarization of (3.29) gives the exact unary
formula

\[
\boxed{
\begin{aligned}
 U_\Xi(D)
 ={}&\sum_p d(p)\zeta_\Xi(p)\\
 &+\sum_{p<_\chi q}
 \bigl(
  a(p)d(q)+d(p)a(q)+d(p)d(q)
 \bigr)K_\Xi(p,q).
\end{aligned}}
\tag{3.30}
\]

For two homogeneous directions with toggle masks \(d,e\), polarizing once
more cancels every base and one-token term:

\[
\boxed{
 B_\Xi(D,E)
 =\sum_{p<_\chi q}
 \bigl(d(p)e(q)+e(p)d(q)\bigr)K_\Xi(p,q).}
\tag{3.31}
\]

Thus local bridges, one-vertex transport defects, and terminal
normalization remain mandatory in the unary term (3.30), through
\(\zeta_\Xi\) and the base--direction cuts.  The one-token terms and every
fixed base, raw, or quotient-section leg cancel from the bilinear Hessian
(3.31).  The pairwise effects of transported sections and inverses survive
exactly in the ordered kernel \(K_\Xi\).  It includes within-occurrence
canonical-section inversion, with decreasing chronology in a negative
occurrence, and every external occurrence comparison.

It would be unsound to apply diagonal \(Q\)-invariance of \(\Xi\) to the
individual transported section tensors and replace (3.31) by an unordered
relative cross-correlation.  The ordered-half reader (3.27) is not
\(Q\)-equivariant on those intermediate tensors.  The nonzero proved value

\[
 B_\infty(H(TTT),H(cTTT))=1
\tag{3.32}
\]

is a concrete guard: any order-free occurrence formula which forces every
homogeneous mixed polarization to vanish contradicts this scalar
functional of \(\Xi\).

Combining (3.22) and (3.31) gives every mixed bucket in (3.24) without a
bounded source census.  It replaces the four equality, six inversion, and
66 external scalar kernels by one exact double-coset-valued ordered cut.
It does not evaluate that cut or prove bucket noncancellation.

### 3.4 Free buckets are shortlex-free

The integral refinement separates the genuinely ordered part of the mixed
Hessian from its free relative-displacement coordinates.  Fix one oriented
representative \(\Delta^+\) of a non-self-inverse double-coset pair and
define, on an arbitrary integral tensor,

\[
 \mathcal R_{\Delta^+}(T):=
 \sum_{Hx^{-1}yH=\Delta^+}T_{x,y}.
\tag{3.33}
\]

Unlike the ordered-half reader (3.27), this is diagonally
\(Q\)-invariant on every intermediate tensor.  On a final diagonal-free
antisymmetric tensor it is exactly the chosen free \(\mathbb Z\)-coordinate
of \(\Xi_{\mathbb Z}\).  For finite module currents \(f,g\) and \(m\in Q\),
put

\[
 \mathcal C_{\Delta^+}(f,g;m)
 :=
 \sum_{x,y}f(x)g(y)
 [H\widetilde x^{-1}m\widetilde yH=\Delta^+].
\tag{3.34}
\]

The value is independent of the representatives \(\widetilde x,\widetilde
y\).  Let the sixteen exact correction occurrences be
\((s_o,\epsilon_o,q_o)\), in literal order, and put

\[
 m_{op}:=q_o^{-1}q_p.
\tag{3.35}
\]

For integral homogeneous directions \(F,G\), write
\(B_{\Xi_{\mathbb Z},\Delta^+}(F,G)\) for the \(\Delta^+\)-coordinate of
the four-corner polarization of
\(\Xi_{\mathbb Z}(\Theta)\).  Then

\[
\boxed{
\begin{aligned}
B_{\Xi_{\mathbb Z},\Delta^+}(F,G)
={}&
\sum_{s=0}^4 n_s
\left(
 \mathcal C_{\Delta^+}(F_s,G_s;1)
 +\mathcal C_{\Delta^+}(G_s,F_s;1)
\right)\\
&+\sum_{o<p}\epsilon_o\epsilon_p
\left(
 \mathcal C_{\Delta^+}(F_{s_o},G_{s_p};m_{op})
 +\mathcal C_{\Delta^+}(G_{s_o},F_{s_p};m_{op})
\right),
\end{aligned}}
\tag{3.36}
\]

where

\[
 (n_0,n_1,n_2,n_3,n_4)=(3,2,1,1,1).
\tag{3.37}
\]

To prove (3.36), use the complete conjugated canonical-section mixed tensor
at each occurrence, not a bare section tensor.  Its positive jet is
\(\Gamma_+(F_s,G_s)\), while its inverse jet is

\[
 \Gamma_-(F_s,G_s)
 =-\Gamma_+(F_s,G_s)
  +F_s\otimes G_s+G_s\otimes F_s.
\tag{3.38}
\]

Each slot has equally many positive and negative occurrences, with common
count (3.37).  Applying the \(Q\)-invariant reader
\(\mathcal R_{\Delta^+}\) removes the absolute occurrence transports, so
the two \(\Gamma_+\)-terms cancel in every polarity pair and leave the
symmetrized outer term in the first line of (3.36).  The external mixed
tensor between occurrences \(o<p\) retains its integral sign
\(\epsilon_o\epsilon_p\); left normalization by \(q_o^{-1}\) gives the
relative multiplier (3.35) and the second line of (3.36).  Propagated
tensor diagonals lie in the trivial double coset and contribute nothing.
Fixed-base and one-vertex terms have zero mixed polarization.  The exact
sixteen-occurrence tensor theorem ensures that no local mixed term has been
omitted.

For an inversion-fixed double coset, no invariant oriented reader such as
(3.33) exists: its endpoint swap reverses the integral wedge orientation.
Summing both tensor orientations kills a final antisymmetric pair modulo
two, so one must retain the ordered-half reader (3.27).  Consequently all
source-shortlex and section-inversion difficulty in the mixed Hessian is
confined to the \(\mathbb Z/2\)-buckets.  The free buckets are not thereby
evaluated; (3.36) leaves unbounded relative cross-correlations of the
complete balanced source currents.  Unary local and base terms also remain
separate.

### 3.5 Fox--Hessian matrix and adjoint identity

The 120 external occurrence pairs in (3.36) assemble into one finite
group-ring matrix.  With involution \(g^*=g^{-1}\), put

\[
 \mathcal L_s:=
 \sum_{o:s_o=s}\epsilon_oq_o=L_s
\tag{3.39}
\]

and define

\[
 \boxed{
 \mathbf H_{st}
 :=
 n_s\delta_{st}\,1
 +\sum_{\substack{o<p\\s_o=s,\ s_p=t}}
 \epsilon_o\epsilon_p\,q_o^{-1}q_p.}
\tag{3.40}
\]

The equality in (3.39) is the exact signed-occurrence first-derivative
theorem.  The matrix satisfies

\[
 \boxed{
 \mathbf H_{st}+\mathbf H_{ts}^*
 =\mathcal L_s^*\mathcal L_t.}
\tag{3.41}
\]

Indeed, the strict pairs with \(o<p\) occur in \(\mathbf H_{st}\), while
those with \(p<o\) occur in \(\mathbf H_{ts}^*\).  If \(s\ne t\), these
partition every term of \(\mathcal L_s^*\mathcal L_t\).  If \(s=t\), the
terms with \(o=p\) contribute \(2n_s\,1\); the two diagonal terms
\(n_s\,1\) in (3.40) supply exactly that coefficient.

Extend (3.34) linearly in a group-ring kernel:

\[
 \mathcal C_{\Delta^+}(f,g;P)
 :=\sum_m [P]_m\mathcal C_{\Delta^+}(f,g;m).
\tag{3.42}
\]

Then (3.36) becomes

\[
\boxed{
B_{\Xi_{\mathbb Z},\Delta^+}(F,G)
=\sum_{s,t}
\left(
 \mathcal C_{\Delta^+}(F_s,G_t;\mathbf H_{st})
 +\mathcal C_{\Delta^+}(G_s,F_t;\mathbf H_{st})
\right).}
\tag{3.43}
\]

Thus all literal chronology of the free mixed buckets is stored in the
fixed \(5\times5\) matrix \(\mathbf H\).

The adjoint identity proves that (3.43) is an exterior class, not that it
vanishes.  In the diagonal \(Q\)-coinvariant tensor module, put

\[
 \mathcal T_{\mathbf H}(F,G)
 :=
 \sum_{s,t}
 \left(
  F_s\otimes\mathbf H_{st}G_t
  +G_s\otimes\mathbf H_{st}F_t
 \right).
\tag{3.44}
\]

Coinvariants give
\([hA\otimes B]=[A\otimes h^*B]\).  If \(\tau\) swaps the two tensor
factors, (3.41) therefore gives

\[
\begin{aligned}
[\mathcal T_{\mathbf H}+\tau\mathcal T_{\mathbf H}]
={}&
\left[
 \left(\sum_s\mathcal L_sF_s\right)
 \otimes
 \left(\sum_t\mathcal L_tG_t\right)
\right]\\
&+
\left[
 \left(\sum_s\mathcal L_sG_s\right)
 \otimes
 \left(\sum_t\mathcal L_tF_t\right)
\right].
\end{aligned}
\tag{3.45}
\]

For homogeneous directions every displayed first-derivative sum is zero.
Hence

\[
 \boxed{
 [\tau\mathcal T_{\mathbf H}]
 =-[\mathcal T_{\mathbf H}].}
\tag{3.46}
\]

This is the exact antisymmetry needed for the free integral buckets.
Identifying the \(\Delta^+\) and \((\Delta^+)^{-1}\) readers while using
(3.41) would falsely turn antisymmetry into vanishing.  The oriented
coordinates in (3.43) can be nonzero.  The remaining free-bucket problem is
therefore the restriction of this fixed Fox--Hessian form to the complete
anchored generating family (3.22), together with the affine unary term.

### 3.6 Kernel gauge and the terminal slot-four row

The displayed chronological matrix is not itself the invariant object on
homogeneous directions.  Put \(R=\mathbb Z[Q]\) and
\(M=\mathbb Z[Q/\langle c\rangle]\).  The row \(\mathcal L\) acts on
\(M^5\); put

\[
 \mathcal K_M
 :=\ker\!\left(
   \mathcal L=(\mathcal L_0,\ldots,\mathcal L_4):
   M^5\longrightarrow M\right).
\tag{3.47}
\]

and define the additive gauge subgroup

\[
 \mathcal G
 :=\mathcal L^*\operatorname{Mat}_{1\times5}(R)
  +\operatorname{Mat}_{5\times1}(R)\mathcal L
 \subseteq\operatorname{Mat}_5(R).
\tag{3.48}
\]

If

\[
 \mathbf A=\mathcal L^*\mathbf P+\mathbf Q\mathcal L\in\mathcal G,
\tag{3.49}
\]

then for \(F,G\in\mathcal K_M\), diagonal tensor coinvariance gives

\[
\begin{aligned}
 \sum_{s,t}[F_s\otimes \mathcal L_s^*P_tG_t]
 &=\left[\left(\sum_s\mathcal L_sF_s\right)
       \otimes\left(\sum_tP_tG_t\right)\right]=0,\\
 \sum_{s,t}[F_s\otimes Q_s\mathcal L_tG_t]
 &=\sum_s\left[F_s\otimes
       Q_s\left(\sum_t\mathcal L_tG_t\right)\right]=0.
\end{aligned}
\tag{3.50}
\]

The same calculation with \(F\) and \(G\) exchanged proves that every
matrix in \(\mathcal G\) vanishes in the symmetrized tensor (3.44).
Consequently the restricted free-bucket Hessian depends only on

\[
 \boxed{[\mathbf H]_{\mathcal K_M}
 \in\operatorname{Mat}_5(R)/\mathcal G.}
\tag{3.51}
\]

If one also wants to retain the ambient adjoint identity (3.41), the exact
skew gauge family

\[
 \mathbf H\longmapsto
 \mathbf H+\mathcal L^*\mathbf P-\mathbf P^*\mathcal L
\tag{3.52}
\]

does so.  No assertion is made that (3.52) exhausts all skew elements of
\(\mathcal G\).

There is one useful one-sided representative.  Occurrences \(15,16\) are
the final two occurrences, both in slot four, with signs \(+1,-1\) and raw
actions \(q_{15}=t,q_{16}=1\).  Hence (3.40) gives

\[
 \mathbf H_{4t}=0\quad(t\ne4),\qquad
 \mathbf H_{44}=1-t^{-1}=-\mathcal L_4^*.
\tag{3.53}
\]

For the standard row vector \(\mathbf e_4\), set

\[
 \widehat{\mathbf H}:=\mathbf H+\mathcal L^*\mathbf e_4.
\]

This changes no value on \(\mathcal K_M\times\mathcal K_M\) by (3.50), and

\[
 \boxed{\widehat{\mathbf H}_{4t}=0\qquad(0\leq t\leq4).}
\tag{3.54}
\]

The remaining fourth column is also explicit.  For \(s\ne4\), (3.41) and
\(\mathbf H_{4s}=0\) give

\[
 \boxed{
 \widehat{\mathbf H}_{s4}
 =\mathcal L_s^*(\mathcal L_4+1)
 =\mathcal L_s^*t\quad(0\leq s\leq3),\qquad
 \widehat{\mathbf H}_{44}=0.}
\tag{3.55}
\]

Hence the gauged tensor has no slot-four first leg:

\[
 \mathcal T_{\widehat{\mathbf H}}(F,G)
 =\sum_{s=0}^3\sum_{t=0}^4
 \left(
  F_s\otimes\widehat{\mathbf H}_{st}G_t
  +G_s\otimes\widehat{\mathbf H}_{st}F_t
 \right).
\tag{3.56}
\]

Its surviving fourth-column part is a boundary pairing.  Homogeneity and
coinvariance give

\[
\begin{aligned}
 \sum_{s=0}^3[F_s\otimes\mathcal L_s^*tG_4]
 &=
 \left[\left(\sum_{s=0}^3\mathcal L_sF_s\right)
       \otimes tG_4\right]\\
 &=[-\mathcal L_4F_4\otimes tG_4]
  =[F_4\otimes\mathcal L_4G_4].
\end{aligned}
\tag{3.57}
\]

Thus the symmetrized fourth-column contribution is exactly

\[
 [F_4\otimes\mathcal L_4G_4
   +G_4\otimes\mathcal L_4F_4],
\tag{3.58}
\]

which need not vanish.  On finitely supported currents,
\(\mathcal L_4=t-1\) is injective because \(t\) acts freely on
\(Q/\langle c\rangle\).  Let

\[
 (t-1)_{\mathrm{fin}}^{-1}:
 \operatorname{im}\!\left(
  (t-1):M_{\mathrm{fin}}\longrightarrow M_{\mathrm{fin}}\right)
 \longrightarrow M_{\mathrm{fin}}
\]

denote the inverse on this image.  For a homogeneous \(F\), the required
right side lies in the image because it equals \((t-1)F_4\).  Thus

\[
 F_4=-(t-1)_{\mathrm{fin}}^{-1}
       \sum_{s=0}^3\mathcal L_sF_s,
\tag{3.59}
\]

but this inverse is the finite prefix-sum operator on \(t\)-orbits, not
multiplication by an element of \(R\).  It replaces the finite matrix by
arbitrarily long finite path prefixes.

Thus the terminal slot-four row is gauge-null.  No further triangularization
follows from this one-sided gauge.  Further elimination by
\(\mathcal L^*\mathbf P\) requires the corresponding column classes modulo
\(\operatorname{im}\mathcal L^*\) to vanish; allowing
\(\mathbf Q\mathcal L\) introduces coupled row and column changes.  Neither
the required divisibility nor a full triangular gauge follows from (3.41).

This gauge theorem is also a precise boundary on the present argument.
Equation (3.41) proves skew-adjointness of the restriction but neither
nondegeneracy nor metabolicity.  The known nonzero full-wedge mixed value
may be carried entirely by inversion-fixed \(\mathbb Z/2\)-buckets and is
therefore not a free-bucket witness.  A free obstruction still requires an
explicit nonzero oriented bucket on the anchored generators (3.22), or a
new leading-double-coset separation theorem for their exact forest flows.

### 3.7 Exact source pullback by half-tree cuts

The nonlocal inverse in (3.59) is one part of the full forest Green map.
Let \(\mathcal S_{\mathrm{fin}}\) be the finite source pairs
\(f=(f_0,f_1)\) for which

\[
 b(f):=\mathcal L_0f_0+\mathcal L_1f_1
\tag{3.60}
\]

has coefficient sum zero on each of the two forest components.  Use the
stored oriented edges

\[
 E_2(v):Bv\longrightarrow v,\qquad
 E_3(v):tv\longrightarrow U^{-1}v,\qquad
 E_4(v):v\longrightarrow tv.
\tag{3.61}
\]

Delete \(E_s(v)\) from its tree and let
\(\mathcal C^+_{s,v}\) be the half-tree containing its head.  The unique
finite Green flow with boundary \(b\) has coefficients

\[
 \boxed{
 \mathfrak G_s(b)(v)
 =\sum_{x\in\mathcal C^+_{s,v}}b(x)
 =-\sum_{x\in\mathcal C^-_{s,v}}b(x)
 \qquad(s=2,3,4).}
\tag{3.62}
\]

Indeed, summing the boundary over the head half-tree cancels every internal
edge and retains the coefficient of \(E_s(v)\).  The second equality is
component balance.  Formula (3.62) is finite because \(b\) is finitely
supported.  It also shows that \(\mathfrak G(b)\) is supported inside the
componentwise finite convex hull of \(\operatorname{supp}b\): outside that
hull the head side contains either none or all of the supported vertices.

Define

\[
 \boxed{
 \mathfrak J(f_0,f_1)
 :=
 \bigl(f_0,f_1,
       -\mathfrak G_2(b(f)),
       -\mathfrak G_3(b(f)),
       -\mathfrak G_4(b(f))\bigr).}
\tag{3.63}
\]

Then \(\mathfrak J\) is \(\mathbb Z\)-linear,
\(\mathcal L\mathfrak J(f)=0\), and source projection makes

\[
 \mathfrak J:\mathcal S_{\mathrm{fin}}
 \stackrel{\cong}{\longrightarrow}\mathcal H_{\mathrm{fin}}
\tag{3.64}
\]

a bijection.  Surjectivity is the forest parametrization of Section 2;
injectivity follows immediately from the first two coordinates.  In
particular, for the anchored atom \(H_r(v)\), its three forest coordinates
are obtained from (3.62) using the boundary of (3.20), without choosing an
endpoint pairing or a path decomposition.

The free-bucket Hessian now pulls back to an exact source-only ledger.  For
an oriented non-self-inverse double coset \(\Delta^+\), put

\[
 \widehat B_{\Delta^+}(f,g)
 :=
 B_{\Xi_{\mathbb Z},\Delta^+}
   (\mathfrak J(f),\mathfrak J(g)).
\]

Equations (3.43), (3.54), and (3.63) give

\[
\boxed{
\begin{aligned}
 \widehat B_{\Delta^+}(f,g)
 =\sum_{s=0}^3\sum_{t=0}^4
 \bigl(
 &\mathcal C_{\Delta^+}
   (\mathfrak J_s(f),\mathfrak J_t(g);
    \widehat{\mathbf H}_{st})\\
 +&\mathcal C_{\Delta^+}
   (\mathfrak J_s(g),\mathfrak J_t(f);
    \widehat{\mathbf H}_{st})
 \bigr).
\end{aligned}}
\tag{3.65}
\]

For \(s\geq2\), every coefficient in (3.65) is the explicit cut sum

\[
 \mathfrak J_s(f)(v)
 =-\sum_{x\in\mathcal C^+_{s,v}}
   (\mathcal L_0f_0+\mathcal L_1f_1)(x).
\tag{3.66}
\]

Writing
\(\widehat{\mathbf H}_{st}=\sum_mh_{st}(m)m\), the only candidate buckets
in one value of (3.65) are therefore the finite set

\[
 \left\{
 \begin{array}{c|c}
 D=H\widetilde v^{-1}m\widetilde wH&
 \begin{gathered}
 0\leq s\leq3,\quad0\leq t\leq4,\quad h_{st}(m)\ne0,\\
 \mathfrak J_s(f)(v)\mathfrak J_t(g)(w)\ne0
 \ \text{or}\
 \mathfrak J_s(g)(v)\mathfrak J_t(f)(w)\ne0,\\
 D\ne H,\qquad D\ne D^{-1}
 \end{gathered}
 \end{array}
 \right\}.
\tag{3.67}
\]

This is an exact elimination of arbitrary forest pairings, not a
group-ring matrix pullback.  The map \(\mathfrak J\) is only
\(\mathbb Z\)-linear on the balanced finite source space; the forest Green
map is not being asserted \(Q\)-equivariant.  In particular, a notation
such as \(\mathfrak J^*\mathbf H\mathfrak J\) would be false as an identity
of matrices over \(R\).

The finite candidate set (3.67) does not yet supply a leading term.
Distinct cut pairs can occupy the same double-coset bucket, component
balance can cancel extremal cuts, and forest distance is not automatically
double-coset length or source shortlex.  The next free-bucket obligation is
to prove a separation or noncancellation lemma for this exact cut ledger;
the affine unary term remains separate.

### 3.8 Forest-diagonal-free occurrence gauge

The two remaining edge slots each occur exactly once positively and once
negatively.  Put

\[
 (a_2,b_2)=(1,6),\qquad (a_3,b_3)=(9,14).
\tag{3.68}
\]

Thus

\[
 \mathcal L_s=q_{a_s}-q_{b_s},\qquad
 \mathbf H_{ss}
 =1-q_{a_s}^{-1}q_{b_s}
 =q_{a_s}^{-1}\mathcal L_s
 \quad(s=2,3).
\tag{3.69}
\]

Let \(\mathbf Q^{\mathrm{out}}\) be the column with

\[
 Q^{\mathrm{out}}_2=-q_1^{-1},\qquad
 Q^{\mathrm{out}}_3=-q_9^{-1},\qquad
 Q^{\mathrm{out}}_0=Q^{\mathrm{out}}_1
 =Q^{\mathrm{out}}_4=0,
\]

and define a second restricted representative

\[
 \boxed{
 \mathbf H^\circ
 :=\widehat{\mathbf H}
   +\mathbf Q^{\mathrm{out}}\mathcal L.}
\tag{3.70}
\]

The added matrix belongs to the gauge subgroup (3.48), so it changes no
free-bucket Hessian value on \(\mathcal K_M\).  It need not preserve the
ambient adjoint identity (3.41).

For \(s=2,3\), direct cancellation in the occurrence definition (3.40)
gives the exact outside-interval row

\[
 \boxed{
 \mathbf H^\circ_{st}
 =
 -q_{a_s}^{-1}
  \sum_{\substack{p<a_s\\s_p=t}}\epsilon_pq_p
 -q_{b_s}^{-1}
  \sum_{\substack{p>b_s\\s_p=t}}\epsilon_pq_p
 +\mathcal L_s^*\delta_{t4}.}
\tag{3.71}
\]

Indeed, subtracting \(q_{a_s}^{-1}\mathcal L_t\) cancels the diagonal
term and every slot-\(t\) occurrence in the closed chronology interval
\([a_s,b_s]\).  Only occurrences strictly before the positive endpoint or
strictly after the negative endpoint survive.  Formula (3.71) includes the
additional fourth-column term from the earlier gauge.

Expanding the two rows with the pinned occurrence table yields

\[
\begin{array}{lll}
 \mathbf H^\circ_{20}
  =-q_6^{-1}(q_7-q_8+q_{11}-q_{12}),&
 \mathbf H^\circ_{21}
  =-q_6^{-1}(q_{10}-q_{13}),&
 \mathbf H^\circ_{22}=0,\\[2mm]
 \mathbf H^\circ_{23}
  =-q_6^{-1}\mathcal L_3,&
 \mathbf H^\circ_{24}
  =\mathcal L_2^*-q_6^{-1}\mathcal L_4,&\\[2mm]
 \mathbf H^\circ_{30}
  =-q_9^{-1}(q_3-q_4+q_7-q_8),&
 \mathbf H^\circ_{31}
  =-q_9^{-1}(q_2-q_5),&
 \mathbf H^\circ_{32}
  =-q_9^{-1}\mathcal L_2,\\[2mm]
 \mathbf H^\circ_{33}=0,&
 \mathbf H^\circ_{34}
  =\mathcal L_3^*-q_{14}^{-1}\mathcal L_4.&
\end{array}
\tag{3.72}
\]

The prior row identity remains

\[
 \boxed{
 \mathbf H^\circ_{22}=\mathbf H^\circ_{33}=0,\qquad
 \mathbf H^\circ_{4t}=0\quad(0\leq t\leq4).}
\tag{3.73}
\]

In particular, the complete forest--forest block is

\[
 \boxed{
 (\mathbf H^\circ_{st})_{2\leq s,t\leq4}
 =
 \begin{pmatrix}
 0&-q_6^{-1}\mathcal L_3&
   \mathcal L_2^*-q_6^{-1}\mathcal L_4\\
 -q_9^{-1}\mathcal L_2&0&
   \mathcal L_3^*-q_{14}^{-1}\mathcal L_4\\
 0&0&0
 \end{pmatrix}.}
\tag{3.74}
\]

Every entry in rows two and three has augmentation zero, and row four
vanishes.  Thus every same-slot forest self-correlation has been removed;
the remaining forest-first terms are finite differences coupling distinct
forest slots or a forest slot to a source slot.  Equation (3.65) remains
valid with \(\widehat{\mathbf H}\) replaced by \(\mathbf H^\circ\).

This normal form reduces the fixed occurrence support but does not separate
relative double cosets.  Green-cut pairs from different rows can still land
in the same bucket, so (3.73)--(3.74) prove neither a leading term nor
free-bucket noncancellation.

### 3.9 Augmentation chords and double Green adjunction

The augmentation-zero conclusion in Section 3.8 has an exact geometric
meaning.  Let

\[
 P=\sum_mp_m m\in R,\qquad \varepsilon(P)=0,
\]

and in the left-Cayley tree of \(Q=C_2*\mathbb Z\) let \([1,m]\) be the
oriented reduced-word geodesic from \(1\) to \(m\), traversing word letters
rightmost first under the left action.  Define

\[
 \Gamma(P):=\sum_mp_m[1,m].
\tag{3.75}
\]

Since \(\partial[1,m]=e_m-e_1\),

\[
 \boxed{\partial\Gamma(P)=P.}
\tag{3.76}
\]

For an oriented double coset \(\Delta\), define the elementary bucket
kernel

\[
 \kappa_\Delta^P(x,y)
 :=\sum_mp_m
 [H\widetilde x^{-1}m\widetilde yH=\Delta].
\tag{3.77}
\]

If \(\gamma_P(u,u')\) is the coefficient of the oriented Cayley edge
\([u,u']\) in \(\Gamma(P)\), finite Stokes gives

\[
\boxed{
\begin{aligned}
 \kappa_\Delta^P(x,y)
 =\sum_{[u,u']}\gamma_P(u,u')
 \bigl(
 &[H\widetilde x^{-1}u'\widetilde yH=\Delta]\\
 -&[H\widetilde x^{-1}u\widetilde yH=\Delta]
 \bigr).
\end{aligned}}
\tag{3.78}
\]

This is independent of the representatives of \(x,y\): changing either
representative is absorbed by the outer \(H\)-factors.  Consequently

\[
 \boxed{
 \mathcal C_\Delta(f,g;P)
 =\sum_{x,y}f(x)g(y)\kappa_\Delta^P(x,y)}
\tag{3.79}
\]

is a finite signed sum of bucket changes along the fixed chord chain
\(\Gamma(P)\).  For a kernel with nonzero augmentation, the scalar term
\(\varepsilon(P)1\) must first be split off; (3.75)--(3.78) apply only to
the augmentation-zero remainder.

There is a dual exact removal of the forest flow.  Fix one root in each
forest component.  For an edge cochain \(\omega\), define its tree
potential by the signed path sum

\[
 \psi_\omega(z)
 :=\left\langle[\operatorname{root},z],\omega\right\rangle.
\tag{3.80}
\]

Then \(\delta\psi_\omega=\omega\).  If \(b\) is finite and
component-balanced, \(\partial\mathfrak G(b)=b\), and
\(\mathfrak J_s=-\mathfrak G_s(b)\), summation by parts gives

\[
 \boxed{
 \sum_v\mathfrak J_s(v)\omega(E_s(v))
 =-\sum_zb(z)\psi_\omega(z).}
\tag{3.81}
\]

Here \(\omega\) is extended by zero on the other two forest-edge labels.
Changing a component root adds a constant to \(\psi_\omega\), which is
killed by component balance.

Apply (3.81) to the cochain

\[
 \omega^{g,P}_{s,\Delta}(E_s(x))
 :=\sum_y g(y)\kappa_\Delta^P(x,y).
\]

For the source pair \(f\), with boundary \(b(f)\), this yields the
one-flow identity

\[
 \boxed{
 \mathcal C_\Delta(\mathfrak J_s(f),g;P)
 =-\sum_zb(f)(z)
   \psi^{g,P}_{s,\Delta}(z).}
\tag{3.82}
\]

If the second current is also a forest flow, define the rectangle potential

\[
\begin{aligned}
 \Psi^P_{st,\Delta}(z,z')
 :=\sum_{\substack{E_s(x)\in[\operatorname{root},z]\\
                   E_t(y)\in[\operatorname{root},z']}}
 \sigma_z(E_s(x))\sigma_{z'}(E_t(y))
 \kappa_\Delta^P(x,y),
\end{aligned}
\]

where each \(\sigma\) records agreement with the stored edge orientation.
Applying (3.81) in both variables makes the two minus signs cancel:

\[
 \boxed{
 \mathcal C_\Delta
  (\mathfrak J_s(f),\mathfrak J_t(g);P)
 =\sum_{z,z'}b(f)(z)b(g)(z')
  \Psi^P_{st,\Delta}(z,z').}
\tag{3.83}
\]

All sums are finite.  The source boundaries have finite support, the root
paths to their vertices are finite, and \(\Gamma(P)\) is fixed and finite.
The induced edge cochain need not have globally finite support.

Every kernel in rows two and three of \(\mathbf H^\circ\) satisfies the
augmentation hypothesis, and row four is zero.  Thus (3.78), (3.82), and
(3.83) replace every forest-first term in the pulled-back Hessian by exact
source-boundary path and chord incidences.  Source-first terms and the
affine unary term remain.  No sign or path decomposition is hidden, but the
rectangle sums can still collide in one double-coset bucket; their
noncancellation is the next unresolved boundary.

The Cayley chord chain in (3.75) and the stored \(A,B,G\)-forest are
different chain complexes.  In particular, \(P\mathfrak J_t(g)\) is not
itself a stored-forest boundary, and only the total relation
\(\sum_{t=2}^4\mathcal L_t\mathfrak J_t(g)=-b(g)\) may be used.  The
distinct left factors in (3.72) prevent factoring that total here.
Likewise, swapping the two tensor variables exchanges \(\Delta\) with
\(\Delta^{-1}\) and adjoints the kernel; the two oriented free buckets must
not be identified.

### 3.10 Laminar augmentation and the source bi-kernel

In fact the chord hypothesis holds for every entry of the matrix.  Pair
each positive occurrence with the matching later negative occurrence in
the same correction block.  The eight signed intervals are

\[
\begin{aligned}
 \mathscr I_0&=\{[3,4],[7,8],[11,12]\},&
 \mathscr I_1&=\{[2,5],[10,13]\},\\
 \mathscr I_2&=\{[1,6]\},&
 \mathscr I_3&=\{[9,14]\},&
 \mathscr I_4&=\{[15,16]\}.
\end{aligned}
\tag{3.84}
\]

The left endpoint of every interval has sign \(+1\), the right endpoint
has sign \(-1\), and the family is laminar.  Its only proper containments
are

\[
 [1,6]\supset[2,5]\supset[3,4],
 \qquad
 [9,14]\supset[10,13]\supset[11,12].
\]

For a diagonal entry, the signed occurrence sum in its slot is zero, so

\[
\begin{aligned}
 \varepsilon(\mathbf H_{ss})
 &=n_s+
   \sum_{\substack{o<p\\s_o=s_p=s}}\epsilon_o\epsilon_p\\
 &=n_s+
   \frac{
    \left(\sum_{s_o=s}\epsilon_o\right)^2
    -\sum_{s_o=s}\epsilon_o^2}{2}
 =n_s-n_s=0.
\end{aligned}
\tag{3.85}
\]

For \(s\ne t\), split the ordered occurrence sum into a pair of intervals,
one from \(\mathscr I_s\) and one from \(\mathscr I_t\).  If they are
disjoint, either the later signed pair contributes \(1-1=0\) or no ordered
pair occurs.  If one contains the other, the outer positive endpoint sees
both inner signs, or both inner endpoints see the outer negative endpoint;
the contribution is again \(1-1=0\).  Therefore

\[
 \boxed{
 \varepsilon(\mathbf H_{st})=0
 \qquad(0\leq s,t\leq4).}
\tag{3.86}
\]

Every \(\mathcal L_s\) also has augmentation zero.  Both gauge additions in
(3.54) and (3.70) therefore preserve (3.86), giving

\[
 \boxed{
 \varepsilon(\mathbf H^\circ_{st})=0
 \qquad(0\leq s,t\leq4).}
\tag{3.87}
\]

Thus the chord formula (3.78) applies to every nonzero mixed-Hessian
kernel, with no scalar identity remainder.

This gives a complete two-source presentation.  Let
\(\sigma^{r,v}\) be the anchored source pair (3.20), and put

\[
 j^{r,v}:=\mathfrak J(\sigma^{r,v})=H_r(v).
\]

For an oriented free bucket \(\Delta^+\), define the absolute source
bi-kernel

\[
\boxed{
\begin{aligned}
 \mathscr K^{\Delta^+}_{rr'}(v,w)
 :=\sum_{s=0}^3\sum_{t=0}^4
 \bigl(
 &\mathcal C_{\Delta^+}
  (j^{r,v}_s,j^{r',w}_t;\mathbf H^\circ_{st})\\
 +&\mathcal C_{\Delta^+}
  (j^{r',w}_s,j^{r,v}_t;\mathbf H^\circ_{st})
 \bigr).
\end{aligned}}
\tag{3.88}
\]

For every two balanced finite source pairs \(f,g\), equations
(3.22), (3.64), and bilinearity give

\[
\boxed{
 B_{\Xi_{\mathbb Z},\Delta^+}
  (\mathfrak J(f),\mathfrak J(g))
 =
 \sum_{r,r'=0}^1\sum_{v,w}
 f_r(v)g_{r'}(w)
 \mathscr K^{\Delta^+}_{rr'}(v,w).}
\tag{3.89}
\]

Every entry of \(\mathscr K\) has the exact source-boundary form already
proved: source--source terms use the direct chord kernel (3.78), terms with
one forest leg use one Green potential as in (3.82) or its
second-variable analogue, and terms with two forest legs use the rectangle
potential (3.83).  Row four is zero.  Hence no explicit forest-flow
coefficient remains in the mixed free-bucket Hessian.

This is a \(2\times2\) bi-kernel indexed by the absolute source vertices,
not a matrix over \(R\).  The map \(\mathfrak J\) is not \(Q\)-equivariant,
and its potentials have arbitrarily long finite root paths.  Consequently
\(\mathscr K^{\Delta^+}_{rr'}(v,w)\) need not be a function of
\(v^{-1}w\), and no finite group-ring Schur complement, metabolic
decomposition, or vanishing theorem follows.

There is nevertheless one exact nonvanishing dichotomy.  Put

\[
 F_*=H_0(TTT),\qquad G_*=H_0(cTTT).
\]

The proved full-wedge value \(B_\infty(F_*,G_*)=1\), together with
(3.15a)--(3.17), gives the finite identity

\[
\boxed{
 1=
 \sum_{\{\Delta,\Delta^{-1}\}\in\mathscr D_2}
  \bigl(
   B_{\Xi_{\mathbb Z},\Delta^+}(F_*,G_*)\bmod2
  \bigr)
 +\sum_{\Delta\in\mathscr D_1}
  B_{\Xi,\Delta}(F_*,G_*)
 \quad\text{in }\mathbb F_2.}
\tag{3.90}
\]

Thus this anchored pair has either a nonzero oriented free bucket or a
nonzero inversion-fixed \(\mathbb Z/2\)-bucket.  The next subsection
evaluates both parts for this pair.  It does not decide global
noncancellation for arbitrary balanced sources.

### 3.11 First explicit free relative bucket

Keep \(H=\langle c\rangle\), write \(T=t^{-1}\), and orient every
non-self-inverse double-coset pair by choosing the representative of
minimum word-length and then minimum integer-word tuple between the class
and its inverse.  With this convention, the class \(HTH\) is the positive
orientation.  The anchored directions from (3.90) satisfy

\[
\boxed{
 B_{\Xi_{\mathbb Z},HTH}
 \bigl(H_0(TTT),H_0(cTTT)\bigr)=-1.}
\tag{3.91}
\]

In particular, the mixed free-bucket Hessian is not the zero form on the
balanced source space.

Here is the exact finite verification after the preceding theory
reductions.  Collision aggregation of the complete sixteen-occurrence
mixed tensor gives 505 supported ordered word pairs with integral
\(\ell^1\)-mass 2353.  Exact \(H\)-double-coset reduction gives 238
oriented free coordinates with nonzero integral coefficient.  Modulo two,
exactly 51 buckets are odd: 49 free buckets and two self-inverse buckets.
The latter have canonical word representatives

\[
 \texttt{tttcTTT},\qquad \texttt{ttctcTcTT},
\]

so their total parity is zero.  The free parity is therefore one, as
required independently by (3.90), and the particular \(HTH\)-coordinate
is the integer \(-1\) in (3.91).

Two fail-closed replays establish the ledger.  The derived projection
starts from the production mixed wedge.  A separate four-corner replay
constructs the two anchored source-flow directions, evaluates the four
residual AST coordinates at
\((0,0),(F_*,0),(0,G_*),(F_*,G_*)\), and then forms the signed mixed
tensor and double-coset ledger without calling the production symbolic
mixed-tensor or mixed-wedge functions, or the first checker.  It shares
only the pinned quotient/module algebra, source-flow construction, and
direct AST-coordinate interpreter.  Both routes give ledger digest

\[
 \texttt{87941b50f9d3b1fe8b6844a5235141a9f938550c186ff3160de295a43ddfeb90}.
\]

The [derived projection checker](../../.scratch/period_two_anchored_relative_bucket_checker.py)
and [direct four-corner replay](../../.scratch/period_two_anchored_relative_bucket_independent_replay.py)
have digests respectively
\(\texttt{04c4f8a6f9b760a49fec74242936e944a6930a02a3ac0f72d3c98db4629c9652}\)
and
\(\texttt{a2d9fd8647fa187e2d7586a547b2b30ca33d6dc9912d023a71cf6e967328e2ae}\).
Every imported certificate source is pinned by SHA-256 before evaluation.

Equation (3.91) proves one explicit nonzero free relative bucket and rules
out the possibility that the known anchored full-wedge witness is carried
only by torsion.  It does not prove that every nonzero balanced source has
a surviving free bucket, that the affine defect cannot cancel this mixed
value, that the full class-two lift equation is obstructed, or any
AK(3), stable Andrews--Curtis, or Andrews--Curtis conclusion.

### 3.12 Literal origin of the free witness

The \(HTH\)-coordinate has a sharper occurrence-level description.  Before
collecting double cosets, its complete wedge support consists of fourteen
ordered vertex pairs.  The integral production subtotals are

\[
 \boxed{
 B_{HTH}^{\mathrm{positive\ internal}}=-5,\qquad
 B_{HTH}^{\mathrm{external}}=4,\qquad
 B_{HTH}^{\mathrm{negative\ internal}}
 =B_{HTH}^{\mathrm{propagated\ diagonal}}=0.}
\tag{3.92}
\]

Thus their sum is the coefficient \(-1\) in (3.91).  Thirteen of the
fourteen ordered-pair coefficients are even.  The unique odd row is

\[
 \boxed{
 (e_{TT}\wedge e_{TTT})\text{ with coefficient }-1.}
\tag{3.93}
\]

It comes from exactly one external occurrence term.  In one-based literal
order, occurrence \(3\) has slot zero, sign \(+1\), and action \(tc\);
occurrence \(16\) has slot four, sign \(-1\), and identity action.  For
arbitrary homogeneous directions \(F,G\), this occurrence pair contributes

\[
 \boxed{
 \mathcal E_{3,16}(F,G)
 =-(tc\,F_0)\otimes G_4-(tc\,G_0)\otimes F_4.}
\tag{3.94}
\]

For \(F=F_*\) and \(G=G_*\),

\[
 G_{*,0}(cTTT)=1,\qquad
 F_{*,4}(TTT)=1,\qquad
 tc(cTTT)=TT.
\]

Hence the second term of (3.94) contains
\(-e_{TT}\otimes e_{TTT}\), proving the odd row in (3.93).
The complete external loop has been replayed with literal occurrence
indices and agrees coefficient-for-coefficient with the production
external subtotal; the
[provenance checker](../../.scratch/period_two_anchored_relative_bucket_hth_provenance.py)
has SHA-256
\(\texttt{f700ee1495342d83f9cfdc4ec703ef12288de2f6bc563ffbd4a9ad0f02f9b354}\),
and its fourteen-row ledger has digest
\(\texttt{5a47688c050b8fe7efb09e7a99381f6e0d891fea91a6ac01c6999be4029f4f42}\).

Formula (3.94) is the local seed for a possible leading-bucket theorem:
it couples a genuine source atom to the terminal \(t\)-forest flow.  It is
not itself such a theorem.  For general sources the remaining occurrences
can occupy the same double coset, and the affine unary tensor can also
contribute.  Any global noncancellation argument must separate the
slot-zero--terminal term simultaneously from those collisions; the single
odd row cannot be transported by an unproved \(Q\)-equivariance of the
Green map.

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

The exact fixtures at \(i=0,1\) fail (4.5).  At this point that is only a
bounded exclusion; Section 5.8 upgrades it to an all-index coordinate-four
obstruction for the complete diagonal family.

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

both nonzero.  The complete fourteen-coordinate identity (5.11) remains
open.  Section 5.8 proves its fourth coordinate, which is already enough to
exclude every diagonal \(D_i\), because the fourth target bit differs from
both seed bits.

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
obligation to the 2,380 finite values in (5.77).  Sections 5.7--5.8
subsequently evaluate all 170 coordinate-four values and leave the exact
2,210-value remainder.

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

There is, however, an exact global pairing at the resolution of the literal
kernel stream.  It uses associativity of the complete typed coordinate, not
a finite-state value for any individual profile in (5.45cm).

#### Lemma 5.1b (literal-stream flattening)

For an arbitrary tensor \(T\), define its coordinate-\(k\) ordered-half
readout by

\[
 W_k(T):=
 \sum_{x<_{\rm sl}y}T_{x,y}\,
 \lambda_k\!\left(
  e_{\rho_k(x)0}\wedge e_{\rho_k(y)0}
 \right)\pmod2.
\tag{5.45co}
\]

Let \(\mathscr P\) be the fixed decorated atomic-token universe obtained by
fully expanding the literal residual stream.  It contains every raw kernel
event emitted at a fixed literal position and every correction coordinate
\(p=(o,v)\).  Its order \(<_\chi\) is literal AST order, raw-letter order
inside a fixed block, increasing module shortlex inside a positive
correction occurrence, and decreasing module shortlex inside a negative
occurrence.  Write \(\ell(p)\) for the central canonical label of an atom.
Thus, at a correction coordinate,

\[
 \ell(o,v)=\operatorname{cvert}(q_ov).
\]

Let \(T_p\) be the exact local tensor of that one atomic block, including
its actual occurrence prefix and polarity, and put

\[
 \varrho_k(p):=W_k(T_p),
 \qquad
 w_k(x,y):=
 \lambda_k\!\left(
  e_{\rho_k(x)0}\wedge e_{\rho_k(y)0}
 \right).
\tag{5.45cp}
\]

The value \(\varrho_k(p)\) is coordinate-specific.  It is not the scalar
full-wedge raw-mirror weight.  For a fixed raw event it is read from its
one-event local tensor; for a correction atom it retains the complete local
bridge, one-vertex transport, inverse, and terminal-normalization data.

For an integral homogeneous endpoint \(F\), let \(a_F(p)\) be the parity
of the collision-aggregated activity of \(p\).  Fixed raw-event tokens have
activity one.  Define

\[
\boxed{
\begin{aligned}
 \Phi_k(a_F):={}&
 \sum_{p\in\mathscr P}a_F(p)\varrho_k(p)\\
 &+\sum_{p<_\chi q}a_F(p)a_F(q)\,
   w_k(\ell(p),\ell(q))
   [\ell(p)<_{\rm sl}\ell(q)].
\end{aligned}}
\tag{5.45cq}
\]

On the zero-linear residual domain,

\[
 \boxed{
  \lambda_k\Pi_{\rho_k}\bigl(M_B(F)\bigr)=\Phi_k(a_F).}
\tag{5.45cr}
\]

Indeed, after each active correction coordinate is replaced by its exact
atomic kernel block, every atom has coordinate
\((1,\pm e_{\ell(p)},T_p)\).  Multiplying these coordinates in literal
chronology gives the sum of the local tensors and, for each
\(p<_\chi q\), the cross tensor
\(e_{\ell(p)}\otimes e_{\ell(q)}\), with integral signs.  Applying
\(W_k\) gives (5.45cq).  Multiple integral copies reduce to activity parity:
same-coordinate copy terms are diagonal, while every cross multiplicity is
the product of the two parities.  Negative signs disappear modulo two, but
negative correction occurrences still reverse \(<_\chi\).  A finite-action
collision has wedge weight zero.

The expansion is the exact `_KernelStream` expansion of the typed product.
Consequently quotient-section events, fixed literals, transport bridges,
inverse blocks, and the local tensors \(T_p\) are all present.  No recursive
\(o_{q,r}\)-term has been discarded.  The residual's linear coordinate is
zero, so its final tensor is diagonal-free and antisymmetric before the
wedge readout.  Inverting the second endpoint adds neither a self term nor
an endpoint cross term because that endpoint also has zero linear
coordinate.  This proves (5.45cr).  The assertion is not made for an
arbitrary activity outside the zero-linear residual domain.

Now put

\[
 a_i:=a_{D_i},\qquad e_i:=a_{D_{i+2}}+a_{D_i}.
\]

Fixed raw-event tokens have \(e_i(p)=0\).  Polarizing (5.45cq) proves the
complete crossed-derivative identity

\[
\boxed{
\begin{aligned}
 R_{k,i}={}&\sum_p e_i(p)\varrho_k(p)\\
 &+\sum_{p<_\chi q}
 w_k(\ell(p),\ell(q))
 [\ell(p)<_{\rm sl}\ell(q)]\\
 &\qquad\cdot
 \bigl(a_i(p)e_i(q)+e_i(p)a_i(q)+e_i(p)e_i(q)\bigr).
\end{aligned}}
\tag{5.45cs}
\]

Thus the product and inverse profiles (5.45cm)--(5.45cn) need not cancel
node by node.  Their complete xor, including every fixed-defect leg, is
exactly the literal-stream weighted cut (5.45cs).  The local weights
\(\varrho_k\) are controlled separately by (5.37)--(5.45): the approved
84-record first-half pump handles slots two through four from index three,
and the slot-zero locality argument handles that slot from index zero.
Every moving leg in the remaining unbounded order tests is the central
label of one of the sixteen correction occurrences; the other leg may be
one of the finite fixed raw or quotient-section events bounded in Section
5.6.  The moving legs therefore return to the leaf-schema comparator
catalog of Sections 5.4--5.6.

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
(5.45bd) and (5.45cg) remove those inversion rays.  Lemma 5.1b then flattens
the remaining recursive profiles back to the leaf catalog, and Section 5.6
supplies the sound two-sided onset 130.

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

Lemma 5.1b replaces the recursive ordered profiles by the literal-stream
form (5.45cs).  Every unbounded pair there compares two central labels from
the sixteen correction occurrences.  Expanding the old activity into its
old path rows, base, anchors, and fixed current, and the toggle into its
two-step shell, gives exactly the old--shell, shell--shell, and fixed--shell
comparisons of the form (5.46).  Fixed literal and quotient-section events
are exponent-zero families.  No product-node quotient, section-defect
support, or ancestor transport remains on a moving label after flattening.
The local one-token weights \(\varrho_k\) are not inferred from this comparison
catalog; they are the separately controlled raw-pump terms identified after
(5.45cs).

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
5.5--5.6 instantiate a conservative source-bound value \(N=130\),
certifying the finite window \(0\leq i\leq169\).  Thus (5.61) is not period from
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

### 5.6 A source-bound onset of 130

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

The fixed leg of (5.45cs) also includes the raw literal and implicit
quotient-section events.  Their source bound is exact.  Expanding every
conjugation into conjugator, payload, and inverse conjugator gives the
successive unreduced fixed-literal masses

\[
 55,\quad 73,\quad 140,\quad 215,\quad 216
\tag{5.67a}
\]

for \(R,S,U,Z\), and the root, respectively.  Correction blocks have
quotient identity, so they add no quotient letters to this fixed stream.
Every fixed raw or quotient-section event label is a Schreier prefix of the
216-letter stream (possibly after the single event deletion in the raw
rule), and therefore has length at most \(216<372\).  Thus the 152 schemas
cover every moving leg, while this finite event list supplies every fixed
leg of a fixed--shell comparison under the same bound \(L=372\).

Lemma 5.1b shows that no recursive AST quotient, section-defect support, or
ancestor transport remains on a moving comparison leg.  The complete local
effect of those words is in \(\varrho_k(p)\), already controlled by the raw pump;
the pair term uses only the central labels covered by (5.67).  We therefore
use \(L=372\).  Before multiplication by those fixed leaf words, every
unbounded source-domain exponent offset is
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

Substituting \(L=372\) and \(d=2\) gives

\[
 J=\left\lceil\frac{1560}{24}\right\rceil=65,\qquad
 N=65+2+\left\lfloor\frac{1489}{24}\right\rfloor+1=130.
\tag{5.75}
\]

Combining (5.61) with this source-bound onset proves the concrete theorem

\[
\boxed{
 R_{k,i+40}=R_{k,i}
 \qquad(1\leq k\leq14,\ i\geq130).}
\tag{5.76}
\]

Consequently the all-index identities (5.28) are equivalent to the finite
set

\[
\boxed{
 R_{k,i}=0
 \qquad(1\leq k\leq14,\ 0\leq i\leq169).}
\tag{5.77}
\]

This is \(14\cdot170=2{,}380\) bits.  Sections 5.7--5.8 prove
\(R_{4,i}=0\) for every \(i\geq0\), so the exact unevaluated part of
(5.77) has

\[
 13\cdot170=2{,}210
\tag{5.77a}
\]

values.  The complete fourteen-coordinate period-two theorem still
requires those 2,210 values.  The coordinate-four result alone excludes
the anchored family, but proves no lift or AK(3) conclusion.

### 5.7 Coordinate-four new--new covariance

The fourth readout has an additional exact simplification.  Its permutation
action and invariant covector are

\[
 \rho_4(c)=(1\ 2),\qquad \rho_4(t)=(0\ 1),\qquad
 \lambda_4=\lambda_{01}+\lambda_{02}+\lambda_{12}.
 \tag{5.78}
\]

If \(\operatorname{col}_4(x):=\rho_4(x)0\), its pair weight is therefore

\[
 w_4(x,y)=[\operatorname{col}_4(x)\ne\operatorname{col}_4(y)].
 \tag{5.79}
\]

Let \(Q_4(q_i)\) denote the coordinate-four new--new term of the one-step
pure-\(P\) shell.  The deterministic matching of Section 5 of the
pure-\(P\) normal-form note expresses it as the sum of (5.79) over the
crossing pairs of its 48 label-preserving chords.  The sole repeated chord
label is nested, so it contributes no crossing.

Every nonzero-slot chord label in the frozen common-phase catalog has the
exact form

\[
 x_C(i)=\operatorname{cvert}
 \bigl(L_C P_C^{\,i+\epsilon_C}R_C\bigr),
 \tag{5.80}
\]

where \(P_C\) is conjugate to \(R_0^3\) and
\(R_0=\texttt{cTctttcT}\).  Direct substitution in (5.78) gives

\[
 \rho_4(R_0^3)=1,
 \qquad \rho_4(P_C)=1.
 \tag{5.81}
\]

The terminal branch creates no seed exception.  The canonical source
records in each of the cells \(i=0,1,2,i\geq3\), and the protected
continuation of the last cell, end in \(\texttt t\); hence terminal-
\(\texttt c\) deletion is inactive.  It follows from (5.80)--(5.81) that

\[
 \operatorname{col}_4(x_C(i+1))
 =\operatorname{col}_4(x_C(i))
 \qquad(i\geq0).
 \tag{5.82}
\]

The slot-zero labels satisfy the independent all-index identity

\[
 y_i=(\texttt{cTc})(\gamma^{-1})^{i+1}\texttt t.
 \tag{5.83}
\]

Since \(R_0^3\) is conjugate to \(\gamma^{-1}\), (5.81) also gives
\(\rho_4(\gamma)=1\).  The actual slot-zero chord labels are

\[
 x_{o,\delta}(i)
 =\operatorname{cvert}(q_o y_{i+\delta}),
 \qquad
 o\in\{3,4,7,8,11,12\},\quad \delta\in\{0,1\}.
 \tag{5.83a}
\]

Each \(q_o\) is fixed and has length at most 11, whereas
\(|y_0|=28\), and every \(y_r\) ends in \(\texttt t\).  Thus the fixed
left prefix cannot cancel the whole powered word and terminal-\(\texttt c\)
deletion is inactive.  Equations (5.81), (5.83), and (5.83a) give

\[
 \operatorname{col}_4(x_{o,\delta}(i+1))
 =\operatorname{col}_4(x_{o,\delta}(i))
 \qquad(i\geq0)
 \tag{5.83b}
\]

for all twelve translated slot-zero tokens.

The frozen chord assignment, occurrence order, and crossing set are the
same in all four exhaustive cells.  Equations (5.79), (5.82), and (5.83b)
therefore identify every crossing weight term by term across consecutive
indices.  Thus

\[
 \boxed{Q_4(q_{i+1})=Q_4(q_i)\qquad(i\geq0).}
 \tag{5.84}
\]

The local part also has an exact stable reduction.  For a correction record
\((o,v)\), let \(\operatorname{FH}(q_o,v)\) be the first-half labels of its
approved raw branch.  In coordinate four, (5.37) and (5.42) specialize to

\[
 \varrho_4(o,v)
 =\sum_{\alpha\in\operatorname{FH}(q_o,v)}
 [\operatorname{col}_4(\alpha)
   \ne\operatorname{col}_4(\tau_o(v))].
 \tag{5.85}
\]

For each of the 84 nonzero-slot records, the raw pump fixes the complete
first-half list in the protected cell \(i\geq3\).  Its central label
advances by a conjugate of \(\gamma^{-1}\), whose \(\rho_4\)-image is
trivial.  Thus every summand in (5.85), and hence the collision-aggregated
nonzero-slot xor, is constant.  The separate slot-zero locality proof is
valid from \(i=0\).  Consequently

\[
 \boxed{L_4(q_i)=L_4(q_3)\qquad(i\geq3).}
 \tag{5.86}
\]

This cannot be extended to the seed cells by substituting the scalar raw
bit.  For example, the protected slot-two
\(\texttt{long\_p1}\) record at negative occurrence 6 has first-half labels
\(\texttt{ctcTcTct}\) and \(\texttt{ctcTcT}\).  Both are source-noncentral,
but the second has the same coordinate-four color as the central label,
whereas the first does not.  Hence this record has scalar raw bit zero and
\(\varrho_4=1\).  Its positive occurrence partner has an empty first half
and contributes zero.  Thus neither the source-noncentral-implies-
bichromatic shortcut nor pointwise occurrence-pair cancellation is valid.

The local all-index question is now exactly the three seam bits

\[
\boxed{
\begin{aligned}
 L_4(q_0)+L_4(q_1),\qquad
 L_4(q_1)+L_4(q_2),\qquad
 L_4(q_2)+L_4(q_3).
\end{aligned}}
\tag{5.87}
\]

Equation (5.84) evaluates no new--new seed value, and (5.87) evaluates none
of the local seams.  The old--shell polarization also remains: equality of
the projected shell colors does not determine its source-shortlex cut.
Hence (5.84)--(5.87) do not prove \(R_{4,i}=0\), period two for \(V_i\), a
lift, or AK(3).

The remaining polarization nevertheless has a finite chronological form.

#### Lemma 5.4 (equal-label chord polarization)

Let \(a,e:\mathscr P\to\mathbb F_2\) be two activity masks.  Suppose the
active atoms of \(e\) are paired into chords \((r,s)\), with
\(r<_{\chi}s\) and \(\ell(r)=\ell(s)\).  Then

\[
\boxed{
 \beta_k(a,e)
 =\sum_{(r,s)}
   \sum_{r<_{\chi}p<_{\chi}s}
   a(p)w_k(\ell(p),\ell(r)).
}
\tag{5.88}
\]

This includes fixed raw and quotient-section atoms in \(a\), and it does
not require the supports of \(a\) and \(e\) to be disjoint.

Indeed, the local \(\varrho_k\)-terms cancel in the polarization.  Fix one
chord with common label \(x\).  An \(a\)-atom before both endpoints or after
both endpoints contributes twice with the same shortlex predicate and
cancels.  For \(r<_{\chi}p<_{\chi}s\), the two endpoint contributions are

\[
 w_k(x,\ell(p))
 \bigl([x<_{\rm sl}\ell(p)]+[\ell(p)<_{\rm sl}x]\bigr).
\tag{5.89}
\]

This equals \(w_k(x,\ell(p))\) when the labels differ and is zero when they
agree.  Endpoint overlaps also have equal labels and weight zero.  This
proves (5.88).

By bilinearity,

\[
 \beta_k(a,E_i)=\beta_k(a,q_i)+\beta_k(a,q_{i+1}).
\tag{5.89a}
\]

Apply the lemma separately to the two frozen 48-chord matchings \(M_i\)
and \(M_{i+1}\) on the right side.  Alternatively, splice the two incident
chords through every atomic copy canceled in
\(E_i=q_i+q_{i+1}\); discard the resulting alternating cycles and retain
the descended label-preserving pairing of \(\operatorname{supp}E_i\).
The literal union of the two matchings is not itself a pairing of that
support.  Let

\[
 P_a(t):=\sum_{p<_{\chi}t}a(p)e_{\operatorname{col}_4(\ell(p))},
 \qquad
 u_c:=\sum_{d\ne c}e_d
 \quad(c=0,1,2).
\tag{5.90}
\]

For a chord \(C=(r_C,s_C)\) of color \(c_C\), (5.88) becomes

\[
 u_{c_C}\mathbin{\cdot}\bigl(P_a(r_C)+P_a(s_C)\bigr).
\tag{5.91}
\]

The possible inclusion of the left endpoint in the prefix xor is harmless,
because \(u_{c_C}\cdot e_{c_C}=0\).

Corresponding chord types in \(M_i\) and \(M_{i+1}\) have the same color by
(5.82)--(5.83b), and their two endpoint occurrence numbers are identical in
the frozen topology; their cell-qualified atomic IDs are different.  Pair
their contributions in (5.91).  At either endpoint occurrence, the complete
chronological prefix strictly before that occurrence appears twice and
cancels.  Consequently every fixed atom outside the two endpoint occurrence
blocks, every complete intervening occurrence activity vector, and every
occurrence-prefix base cancels identically.  Old fixed correction or base
atoms inside an endpoint occurrence remain in its local prefix.

For occurrence \(o\), let

\[
 P_{a,o}(v_0)
 :=\sum_{\substack{v\ {\rm before}\ v_0\\
                    {\rm inside\ occurrence}\ o}}
 a(o,v)e_{\operatorname{col}_4(\tau_o(v))},
\tag{5.92}
\]

using increasing module shortlex in a positive occurrence and decreasing
module shortlex in a negative occurrence.  Let \(v_{C,o}(j)\) be the module
coordinate of chord \(C\)'s endpoint in occurrence \(o\) in the matching
\(M_j\).  The transported endpoint color

\[
 c_C=\operatorname{col}_4(\tau_o(v_{C,o}(j)))
\tag{5.92a}
\]

is independent of the endpoint occurrence and of \(j\).  Put

\[
 \Delta P_{a,o,C}(i)
 :=P_{a,o}(v_{C,o}(i))+P_{a,o}(v_{C,o}(i+1)).
\tag{5.93}
\]

Taking \(a=a_{i+1}\), the exact old--shell polarization is now

\[
\boxed{
 \beta_4(a_{i+1},E_i)
 =\sum_{C=1}^{48}u_{c_C}\mathbin{\cdot}
 \left(
  \Delta P_{a_{i+1},o_C^-,C}(i)
  +\Delta P_{a_{i+1},o_C^+,C}(i)
 \right).
}
\tag{5.94}
\]

Here \(o_C^-,o_C^+\) denote the two endpoint occurrences in chronological
order, not their polarities.

There is one further exact cancellation.  Define the shift-prefix seam

\[
 \Theta_{o,C}(i)
 :=\Delta P_{a_{i+1},o,C}(i)
   +P_{q_i,o}(v_{C,o}(i)),
\tag{5.94a}
\]

where \(P_{q_i,o}\) is (5.92) with old activity \(a\) replaced by the
one-step shell activity \(q_i\).  Since \(q_i=a_i+a_{i+1}\),

\[
\boxed{
 \Theta_{o,C}(i)
 =P_{a_i,o}(v_{C,o}(i))
  +P_{a_{i+1},o}(v_{C,o}(i+1)).
}
\tag{5.94aa}
\]

The sum of the added local \(q_i\)-prefix terms is zero.  Work
collision-first, so the two occurrences in each polarity pair carry the
same slot mask \(e_s\).  The chord endpoints in either occurrence run
exactly once through its active coordinates.  For the positive occurrence,
module chronology is increasing; for its negative partner it is
decreasing.  Their combined local self-prefix is therefore

\[
\begin{aligned}
 &\sum_{v<x}e_s(v)e_s(x)
   w_4(\tau_{o^{\rm pos}}(v),\tau_{o^{\rm pos}}(x))\\
 &\quad+
 \sum_{v>x}e_s(v)e_s(x)
   w_4(\tau_{o^{\rm neg}}(v),\tau_{o^{\rm neg}}(x)).
\end{aligned}
\tag{5.94ab}
\]

Diagonal invariance and symmetry of \(w_4\) turn (5.94ab) into

\[
 \sum_{v<x}e_s(v)e_s(x)
 \bigl(w_4(v,x)+w_4(x,v)\bigr)=0.
\tag{5.94ac}
\]

This applies to the three edge-slot pairs \((1,6),(9,14),(15,16)\) and
separately to the three slot-zero pairs
\((3,4),(7,8),(11,12)\).  A collision deletes both polarity copies and
does not disturb the argument.

All chronology strictly before an endpoint occurrence was already canceled
between the corresponding \(M_i\) and \(M_{i+1}\) endpoints in deriving
(5.94).  Thus (5.94ab)--(5.94ac) introduce no relative-order kernel or
enclosed-block term: only the within-occurrence prefixes (5.92) are being
modified.  Substitution in (5.94) proves

\[
\boxed{
 \beta_4(a_{i+1},E_i)
 =\sum_{C=1}^{48}u_{c_C}\mathbin{\cdot}
 \left(
  \Theta_{o_C^-,C}(i)+\Theta_{o_C^+,C}(i)
 \right).
}
\tag{5.94b}
\]

The aggregate seam can now be evaluated without evaluating its 48 rows
separately.  Let \(f_{j,s}\) be the collision-aggregated old correction mask
\(B_s+D_{j,s}\) inside one occurrence of slot \(s\), and let
\(e_{j,s}=q_{j,s}\).  Repeating the positive/reverse-negative calculation
with old mask \(f_{j,s}\) and shell mask \(e_{j,s}\) gives

\[
 \mathcal H^{\rm loc}_{4,s}(f_j;M_j)
 =b_4(\pi_4f_{j,s},\pi_4e_{j,s}).
\tag{5.94c}
\]

The local tensor data inside a correction atom belong to
\(\varrho_4\), not to (5.94c).  Fixed raw and quotient-section atoms are
external blocks already canceled before (5.92), while fixed base and anchor
correction coordinates are included in \(f_{j,s}\).

Put \(Q_s:=\pi_4e_{j,s}\).  Equations (5.82)--(5.83b), applied
occurrence by occurrence after collision aggregation, make \(Q_s\)
independent of \(j\).  Slots \(2,3,4\) each have one polarity pair, while
slot zero has three; all four multiplicities are odd.  Slot one has no
shell activity.  Since

\[
 f_{i,s}+f_{i+1,s}
 =(B_s+D_{i,s})+(B_s+D_{i+1,s})
 =e_{i,s},
\tag{5.94d}
\]

the two natural-side sweeps in (5.94b) give

\[
\begin{aligned}
 \beta_4(a_{i+1},E_i)
 &=\sum_{s\in\{0,2,3,4\}}
   \left(
    b_4(\pi_4f_{i,s},Q_s)
    {}+b_4(\pi_4f_{i+1,s},Q_s)
   \right)\\
 &=\sum_{s\in\{0,2,3,4\}}b_4(Q_s,Q_s)=0.
\end{aligned}
\tag{5.94e}
\]

The final equality uses alternation of \(b_4\).  Thus

\[
\boxed{\beta_4(a_{i+1},E_i)=0\qquad(i\geq0).}
\tag{5.94f}
\]

Finally, the one-step decomposition and bilinearity give

\[
\begin{aligned}
 R_{4,i}
 ={}&L_4(q_{i+1})+L_4(q_i)\\
 &+Q_4(q_{i+1})+Q_4(q_i)
 +\beta_4(a_{i+1},E_i).
\end{aligned}
\tag{5.95}
\]

Using (5.84) and (5.94f),

\[
\boxed{
 R_{4,i}
 =L_4(q_{i+1})+L_4(q_i).
}
\tag{5.96}
\]

Combining (5.86) and (5.96) proves the first complete family of crossed
derivative values:

\[
\boxed{R_{4,i}=0\qquad(i\geq3).}
\tag{5.97}
\]

Through (5.97), the coordinate-four all-index target is exactly the three
lower local seams in (5.87).  They are evaluated next; (5.97) alone proves
no all-index period two, lift, or AK(3) conclusion.

### 5.8 Coordinate-four seed seams and the anchored-family obstruction

Write \(L_{4,\ne0}(q_i)\) and \(L_{4,0}(q_i)\) for the nonzero-slot and
slot-zero parts of the local term in (5.85).  The frozen collision-first
raw manifest has 42 active nonzero-slot coordinates: nine in slot two,
fifteen in slot three, and eighteen in slot four.  Each coordinate occurs
at exactly the prescribed polarity pair

\[
 \{1,6\},\qquad \{9,14\},\qquad \{15,16\},
\tag{5.98}
\]

so its 84 records are precisely the occurrence records required by
(5.85), with no virtual-row multiplicity.

The source-bound finite projection
<code>.scratch/period_two_coordinate4_local_seams_checker.py</code>
applies the authoritative rightmost-first action (5.78) to every central
and first-half label.  It is bound to the independently replayed raw
manifest of SHA-256
<code>6f83559c4edfb27575beac7df28a774732a92dd81738656036278da00ddde9ef</code>
and to the exact Section 5.7 source interval of SHA-256
<code>749ab9456dc3fb2adce711baaa757151c3dddd5f37f9ca29246f0615f792ff8c</code>.
The evaluator SHA-256 is
<code>54a55bd29758506e916b90a05dfb319ef56bf7df0ead5179139f8cb0b9b708d9</code>.
Its four exhaustive cell values are

\[
\begin{array}{c|cccc}
 i&0&1&2&i\geq3\\ \hline
 L_{4,\ne0}(q_i)&0&0&0&0.
\end{array}
\tag{5.99}
\]

This is a projection of the literal first-half lists, not the scalar raw
bit.  The evaluator compares its word action with the existing finite-wedge
point action, checks every coordinate pair in (5.98), and checks all 84
protected-cell pumps.  In the protected cell the first-half lists agree
after one increment and every central color agrees; the source-bound
horizon induction and (5.81) then extend the last column of (5.99) to every
\(i\geq3\).  The three consecutive nonzero-slot seams are all zero.

Slot zero requires no finite evaluation.  Equations (5.43)--(5.45) make
each of its six first-half factors independent of \(i\), while (5.81)
makes the corresponding central color independent of \(i\).  Hence each
slot-zero occurrence weight in (5.85) is constant.  The one-step shell has
the two consecutive slot-zero atoms \(e_{y_i}+e_{y_{i+1}}\), so

\[
 L_{4,0}(q_i)=0\qquad(i\geq0).
\tag{5.100}
\]

Combining (5.99)--(5.100) with (5.96) closes the three seams in (5.87):

\[
 \boxed{L_4(q_i)=0,\qquad R_{4,i}=0\qquad(i\geq0).}
\tag{5.101}
\]

By the definition of the crossed derivative,
\(R_{4,i}=V_{i+2,4}+V_{i,4}\).  Thus \(V_{i,4}\) is two-periodic.  The
fixtures (5.12) have

\[
 V_{0,4}=V_{1,4}=1,
 \qquad (C_{14})_4=0,
\tag{5.102}
\]

so \(V_{i,4}=1\) for every \(i\geq0\), and no diagonal \(D_{ii}\) satisfies
(4.5).  Together with the full-wedge exclusion (4.4) for \(i\ne j\), this
excludes every member of the complete anchored family \(D_{ij}\) through
the necessary class-two syndrome.

This is not an obstruction to arbitrary balanced source-pair corrections.
Those remain governed by the full quadratic cokernel equation (3.8), and
even a solution there would still require the literal higher-defect step
(1.10).

For sums of source directions, the mixed polarizations of \(\Theta\) are
mandatory.  The unary delta theorem determines no such cross term.

With the anchored ansatz excluded, the next global formulation is the
quadratic cokernel equation (3.8) on the exact balanced source-pair
parametrization of Section 2.  A genuine obstruction must be a covector or
structural theorem on the full cokernel \(\mathcal C_2\) that detects every
finite balanced source pair.  The full-wedge covector cannot do this,
because every \(D_{ii}\) already kills it.

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
