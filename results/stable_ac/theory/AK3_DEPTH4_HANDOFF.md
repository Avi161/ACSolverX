# AK depth-four theory handoff

Date: 2026-07-28

Branch: `codex/proofs`

## Last complete theorem checkpoint

Commit `881ce85` proves Result 136: an exact quaternion representation
into \(SU(2)\) separates the final fixed-entry conjugacy-class product
from both orientations of the primitive target.  Consequently every
row reached from the first proper AK image with at most three AC2
multiplications is nonprimitive.

The standalone proof is
`literature/proofs/AK3_SU2_FIXED_COMMUTATOR_OBSTRUCTION.md`.
The complete stable-AC suite passed at that checkpoint:

```text
548 passed in 364.58s
```

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.  Do not
mark the goal complete.

## Verified next frontier

Direct signed source-leaf enumeration gives 82 canonical row multisets
at AC2 depth four.  Twenty-eight already occur through depth three, so
there are exactly 54 new classes.  All 54 have coprime exponent vectors
and therefore survive the abelian primitivity gate.

Killing the majority source divides them by the number of surviving
minority conjugates:

| row length | minority leaves | classes |
|---:|---:|---:|
| 5 | 1 | 10 |
| 7 | 2 | 14 |
| 7 | 3 | 14 |
| 8 | 3 | 16 |

Thus the new geometric problem has no four-minority case: 24 classes
use at most two minority conjugates, while 30 use exactly three.

## Verified low-minority closure

`.scratch/depth4_provenance_check.py` reproduces the 82/28/54 counts
and the 10/14/30 split, then closes all 24 one/two-minority classes in
the established quotients

\[
Q_A=C_3*C_4,
\qquad
Q_B=C_2*C_3.
\]

For one minority leaf, exact cyclic normal-form comparison suffices.  For
two minority leaves, the checker uses the finite Bass--Serre connector
normal form from the depth-three proof.  It streams reduced connectors
through the safe bound, cyclically rotates both signed source images,
and compares the exactly reduced product with every cyclic target
rotation.

The terminating prune is also exact.  If the two source images have
syllable length \(L\), a connector has length \(k\), and the target has
length \(T\), the raw word has length \(R=2L+2k\).  Reduction to the
target loses exactly \(R-T\) syllables.  Since the first connector is
internally reduced, any changed connector syllables occur at its two
boundary seams and each costs at least one unit of this loss.  Hence a
contiguous block of at least \(k-(R-T)\) connector syllables survives
unchanged in the cyclic target.  A connector branch is discarded when
no such cyclic target subword exists.  During the remaining exact word
reduction, monotone accumulated syllable loss gives a second safe early
exit.  In every case where the subword prune is nonvacuous here,
\(R-T\le4<L\), so neither source word can disappear and expose an
additional internal connector seam.

The ten one-minority records have no connector bound.  Their exact
target-length data are

| signature | quotient | minority length | target length |
|---|---|---:|---:|
| `(5,1,4,-1,-4)` | \(Q_B\) | 14 | 30 |
| `(5,1,4,-1,-2)` | \(Q_B\) | 14 | 22 |
| `(5,1,4,-1,0)` | \(Q_B\) | 14 | 14 |
| `(5,1,4,-1,2)` | \(Q_B\) | 14 | 6 |
| `(5,1,4,-1,4)` | \(Q_B\) | 14 | 2 |
| `(5,4,1,-4,-1)` | \(Q_A\) | 6 | 26 |
| `(5,4,1,-4,1)` | \(Q_A\) | 6 | 22 |
| `(5,4,1,-2,-1)` | \(Q_A\) | 6 | 14 |
| `(5,4,1,-2,1)` | \(Q_A\) | 6 | 10 |
| `(5,4,1,0,-1)` | \(Q_A\) | 6 | 2 |

The fourteen two-minority connector records are

| signature | quotient | minority length | target length | connector bound | candidate products certified |
|---|---|---:|---:|---:|---:|
| `(7,2,5,-2,-5)` | \(Q_B\) | 14 | 48 | 12 | 86,632 |
| `(7,2,5,-2,-3)` | \(Q_B\) | 14 | 40 | 8 | 20,776 |
| `(7,2,5,-2,-1)` | \(Q_B\) | 14 | 32 | 4 | 4,312 |
| `(7,2,5,-2,1)` | \(Q_B\) | 14 | 24 | 2 | 1,568 |
| `(7,2,5,-2,3)` | \(Q_B\) | 14 | 16 | 2 | 1,568 |
| `(7,2,5,-2,5)` | \(Q_B\) | 14 | 8 | 2 | 1,568 |
| `(7,2,5,0,-1)` | \(Q_B\) | 14 | 4 | 2 | 1,568 |
| `(7,5,2,-5,-2)` | \(Q_A\) | 6 | 34 | 13 | 14,108,688 |
| `(7,5,2,-5,2)` | \(Q_A\) | 6 | 26 | 9 | 391,824 |
| `(7,5,2,-3,-2)` | \(Q_A\) | 6 | 22 | 7 | 65,232 |
| `(7,5,2,-3,2)` | \(Q_A\) | 6 | 14 | 3 | 1,728 |
| `(7,5,2,-1,-2)` | \(Q_A\) | 6 | 10 | 2 | 648 |
| `(7,5,2,-1,0)` | \(Q_A\) | 6 | 6 | 2 | 648 |
| `(7,5,2,-1,2)` | \(Q_A\) | 6 | 2 | 2 | 648 |

None contains a target.  The deterministic record hashes are

```text
54-signature SHA-256:
f6bdbc8bcb71936ccef6703577a727cc263729a603d9200c17981ba2284a50dd

24-certificate SHA-256:
b01df11a74afcc40b0f930ad73a301dc766c145cbc35921605af79e5438ee59c
```

Focused verification plus the established depth-three regression:

```text
tests/stable_ac/test_ak_depth_four_barriers.py
tests/stable_ac/test_ak_depth_three_free_product_barrier.py
10 passed in 6.78s
```

These tests now include reachable positive controls in both quotients,
pruned/unpruned parity, admitted-prefix checks, and exhaustive parity
between the target-length reducer and ordinary reduction through
connector length two.  Constant-false mutations of either pruning
predicate, and a constant-`None` reducer mutation, are all detected.

## Exact three-conjugate SU(2) lemma

If \(C_\alpha\) is the \(SU(2)\) conjugacy class with quaternion angle
\(\alpha\in[0,\pi]\), the product of three copies has angle interval

\[
C_\alpha^3:
\begin{cases}
[0,3\alpha],&0\le\alpha\le\pi/3,\\
[0,\pi],&\pi/3\le\alpha\le2\pi/3,\\
[3\alpha-2\pi,\pi],&2\pi/3\le\alpha\le\pi.
\end{cases}
\]

This follows by composing the standard two-class interval twice.  In
scalar form, with minority scalar s and target scalar t, separation is
certified by either

\[
s>\frac12,
\qquad
t<4s^3-3s,
\]

or

\[
s<-\frac12,
\qquad
t>4s^3-3s.
\]

The proof and exact certificate replay are now in
`literature/proofs/AK3_SU2_THREE_CLASS_INTERVAL.md` and
`experiments/stable_ac/depth4_three_class_certificates.py`.

## Exact three-minority reduction

The numerical families below have now been converted to exact directed
rational-interval certificates.  A complementary bi-invariant metric
argument supplies 19 exact certificates; the three-class calculation
supplies five more.

When B is the majority source, impose \(B=1\) using equal-angle
quaternions with

\[
d=\frac{\cos^2\theta-1/2}{\sin^2\theta}.
\]

The two exact rational choices

\[
\cos^2\theta=\frac{37}{50}
\qquad\text{and}\qquad
\cos^2\theta=\frac25
\]

numerically separate 11 of the 15 three-minority signatures.  The four
not separated are

```text
(7,3,4,-1,-2)  vector (-5,6)
(8,3,5,-3, 5)  vector (-4,7)
(8,3,5,-1,-1)  vector (-4,5)
(8,3,5,-1, 3)  vector ( 0,1)
```

When A is the majority source, impose \(A=X^3Y^{-4}=1\) with
\(\angle X=\pi/3\), \(\angle Y=\pi/4\).  The rational axis dot
products

\[
m\in\left\{-\frac13,-\frac14,\frac8{15},\frac45\right\}
\]

numerically separate 13 of the 15 three-minority signatures.  The two
not separated are

```text
(8,5,3,-1,-1)  vector (-4,5)
(8,5,3,-1, 3)  vector ( 0,1)
```

Together the exact metric and three-class certificates close 24 of the
30 three-minority classes and leave precisely the six signatures shown
above.  The standalone metric proof is
`literature/proofs/AK3_DEPTH4_BIINVARIANT_METRIC_OBSTRUCTION.md`.

## Dependency-sensitive reduction for the hardest overlap

For the signature `(8,3,5,-3,5)`, put

\[
c=yyX,\qquad t=c^3(yX)=\operatorname{Chr}(-4,7).
\]

Then \((c,t)\) is a free basis.  The height map \(\chi(c)=1\),
\(\chi(t)=0\) has free kernel

\[
K=\langle t_j=c^jtc^{-j}\mid j\in\mathbb Z\rangle .
\]

Exact push-through identities and four Bezout steps show that every
hypothetical solution is gauge-equivalent to one with all four
conjugators in \(K\).  In shifted Schreier coordinates it must solve

\[
\begin{aligned}
r&=aG_0\sigma^2(b^{-1})\sigma^{-3}(G_0^{-1}),\\
s&=bG_1\sigma(r^{-1})\sigma^{-2}(G_1^{-1}),\\
u&=rG_2\sigma(s^{-1})\sigma^{-1}(G_2^{-1}),\\
z&=\sigma^{-1}(u^{-1})G_3\sigma^{-1}(s)\sigma(G_3^{-1}).
\end{aligned}
\]

The target condition is exactly that the cyclic reduction of \(z\) is
one positive basis letter \(t_m\).  If all four seams are axial
(pure powers of \(c\) before normalization), the expanded kernel word
has length 43 and at most nine cancellation pairs.  Its cyclic length is
therefore at least 25, sharply, so the entire axial stratum is excluded.

This does not close the signature.  Abelianizing \(K\) is provably blind:
the last seam contributes \((X^{-1}-1)G_3\), which can repair every
Laurent-polynomial discrepancy of augmentation one.  The remaining
problem is consequently the genuinely nonabelian gap-\(3,2,1,1\)
equation above.  The proof and replay are
`literature/proofs/AK3_DEPTH4_TARGET_BASIS_RIGIDITY.md` and
`experiments/stable_ac/depth4_target_basis_certificate.py`.

### Exact no-go results beyond the axial theorem

The four-local-triangle \(SU(2)\) angle relaxation retains the repeated
scalar angles \(r,s,u\) but forgets simultaneous matrix compatibility.
Its projection is exactly the flat three-\(A\), five-\(B\) interval.  In
angles normalized by \(\pi\), that common interval is

\[
\begin{aligned}
L(a,b)&=\max(0,3a-5b-2,5b-3a-4),\\
U(a,b)&=\min(1,3a+5b,8-3a-5b).
\end{aligned}
\]

Thus the local shared-angle relaxation supplies no new obstruction.  The
exact facet and vertex proof is
`literature/proofs/AK3_DEPTH4_SU2_DEPENDENCY_BLINDNESS.md`.

Coordinatewise shortest representatives in the four evolving cyclic
double cosets do not force axial seams.  The exact tuple with every ambient
conjugator equal to \(tctc^{-1}\) has four uniquely shortest nonaxial seams,
while its final cyclic kernel length is 57.  Any peak theorem must therefore
use the target condition or a coupled global complexity.  The exact length
proof is `literature/proofs/AK3_DEPTH4_MINIMAL_SEAM_COUNTEREXAMPLE.md`.

More strongly, the full infinite-kernel equation has a solution in every
lower-central nilpotent quotient and in the pro-nilpotent completion.  On
the graded free Lie ring,

\[
L_n=(1-\sigma)L_n+[L_{n-1},t_m],
\]

so the last seam and target conjugator repair every successive error after
the explicit Alexander-level solution.  Nilpotent obstructions are therefore
exhausted for this class.  This is local solvability, not a free-group
solution; the exact proof is
`literature/proofs/AK3_DEPTH4_PRONILPOTENT_BLINDNESS.md`.

### Period-two quotient: exact witness, so this quotient is blind

Impose \(c^2=1\) in the target basis. Then
\[
G=C_2*\mathbb Z,\qquad
H=\ker(G\to C_2)=F(p,q),
\]
where \(p=t,\ q=ctc\), and conjugation by \(c\) swaps \(p,q\).
The fixed rows are
\[
A=t^{-2}ct^{-2}ct^2c,\qquad
B=t^{-3}ctctc.
\]

The full quotient recurrence is exactly equivalent to the backward system
\[
\begin{aligned}
R^{-1}A&\in\operatorname{Cl}_H(B),\\
S^{-1}B&\in\operatorname{Cl}_H(R),\\
X,Y&\in\operatorname{Cl}_H(S),\\
e&\in\operatorname{Cl}_H(p)\cup\operatorname{Cl}_H(q),\\
R&=Ye^{-1}X.
\end{aligned}
\]

The elliptic-\(S\) branch is impossible. Eliminating its first two equations
would force
\[
A\in\operatorname{Cl}_H(c)
       \operatorname{Cl}_H(B)\operatorname{Cl}_H(B).
\]
In \(PSU(2)\cong SO(3)\), quaternion lifts
\[
C=(0,1,0,0),\qquad
T=\left(\frac{\sqrt2}{2},\frac12,\frac12,0\right)
\]
give \(C^2=-1\),
\[
\widetilde\rho(B)=-1,\qquad
\widetilde\rho(A)=
\left(\frac{\sqrt2}{2},0,0,-\frac{\sqrt2}{2}\right).
\]
The two \(B\)-classes vanish projectively, but \(A\) is not conjugate to the
half-turn \(c\): their lift scalar squares are \(1/2\) and \(0\).

The surviving hyperbolic branch nevertheless has an exact solution. In
\(H=F(p,q)\), with upper case denoting inverse, take
\[
h_0=QQppp,\qquad h_1=1,\qquad h_2=Qppp,\qquad h_3=p.
\]
Independent free reduction in \(C_2*\mathbb Z\) gives
\[
\begin{aligned}
R&=t^{-2}ctct^{-1}ctc,\\
S&=t^{-3}ct^2ct^{-1}ct^2,\\
U&=t^{-2}ct^2ct^{-1}c,\\
h_3Sh_3^{-1}&=Ut.
\end{aligned}
\]
Therefore the final row is
\[
Z=U^{-1}h_3Sh_3^{-1}=t
\]
literally. The witness lies in the equal-length hyperbolic alternative,
with \(\ell_T(S)=\ell_T(U)=6\).

Thus every invariant factoring through \(c^2=1\) is now proved blind to the
hardest class. The next problem is to measure the failure of this exact
quotient witness to lift to the original free group. The standalone proofs
and exact checkers are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_ELLIPTIC\_OBSTRUCTION.md},\\
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_WITNESS.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_elliptic\_certificate.py},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_witness.py}.
\end{gathered}
\]

### The first lift layer is also blind

Read the same four quotient conjugators in the original free group
\(F(c,t)\), and put
\[
N=\ker(F(c,t)\to C_2*\mathbb Z)
 =\langle\!\langle c^2\rangle\!\rangle.
\]
Using the unreduced original source rows, the lifted recurrence has
\[
\bigl(|R|,|S|,|U|,|Z|\bigr)=(49,63,116,177),
\]
and
\[
D=Zt^{-1}\in N,\qquad |D|=178.
\]

Kurosh rewriting identifies
\[
M=N_{\mathrm{ab}}\cong\mathbb Z[Q/\langle c\rangle].
\]
The defect \([D]\) has 21 basis terms, coefficient sum zero, and
coefficient \(\ell^1\)-norm \(48\). Correcting the four conjugators by
\(x_0,\ldots,x_3\in M\), and the target conjugator by \(x_4\), gives the
exact module equation
\[
[D]+L_0x_0+L_1x_1+L_2x_2+L_3x_3+L_4x_4=0,
\]
where
\[
\begin{aligned}
L_0&=-U^{-1}(A-R)
     -(h_2+U^{-1}h_3)S(A-R),\\
L_1&=(h_2+U^{-1}h_3)(B-S),\\
L_2&=1-X,\qquad
L_3=U^{-1}-t,\qquad
L_4=t-1.
\end{aligned}
\]

This equation has the explicit integral solution
\[
\begin{aligned}
x_0&=2e_{cT}-2e_{cTTct}-2e_{cTTctt},\\
x_1&=0,\\
x_2&=-2e_{cTct}-2e_{cTctt},\\
x_3&=-2e_1-e_{TTct},\\
x_4&=e_{Tct},
\end{aligned}
\]
where \(T=t^{-1}\) and \(e_v\) is the \(C\)-vertex basis element.
Lifting these vectors to actual products of conjugates of \(c^2\) and
recomputing the recurrence leaves a freely reduced residual of length \(82\)
inside \([N,N]\).

Thus the exact quotient witness lifts through \(F/[N,N]\). The next honest
obstruction is degree two,
\[
[N,N]/[[N,N],N],
\]
not the ordinary relation module. The proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_RELATION\_MODULE\_LIFT.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_lift\_certificate.py}.
\end{gathered}
\]

### Degree two forces nonlocal first-layer support

For the relation-module equation
\[
d+\sum_{i=0}^4L_i x_i=0,
\]
define the one-hop support by allowing \(e_v\) in \(x_i\) precisely when
some term of \(L_i e_v\) lands on the original \(21\)-term support of
\(d\). This gives \(242\) variables, \(449\) output rows, and an integral
matrix with \(880\) nonzero entries. Its rank is \(240\) over each of
\(\mathbb F_2,\mathbb F_3,\mathbb F_5\).

A particular integral solution and two independent homogeneous solutions
exhaust the four mod-\(2\) classes of all one-hop solutions. Two global
degree-two functionals are available:

1. the mod-\(2\) sum of all coordinates in \(\Lambda^2M\);
2. the same wedge sum after the three-point action
   \(c=(1\ 2),\ t=(0\ 1\ 2)\).

Both kill every \(L_i\)-image because all five operators have augmentation
zero. Direct nonlinear replay gives:

| parity class | free residual | kernel length | full wedge | three-point wedge |
|---:|---:|---:|---:|---:|
| \((0,0)\) | 82 | 24 | 1 | 1 |
| \((1,0)\) | 442 | 104 | 0 | 1 |
| \((0,1)\) | 678 | 212 | 0 | 1 |
| \((1,1)\) | 614 | 178 | 1 | 0 |

Thus no one-hop first-layer correction lifts through
\(F/\gamma_3N\). Any degree-two lift must introduce relation-module support
whose entire first image lies away from the original defect and cancels
nonlocally before returning. This is a support-escape theorem, not global
impossibility. The exact proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_DEGREE\_TWO\_ESCAPE.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_degree\_two\_escape\_certificate.py}.
\end{gathered}
\]

### Pure binomial remote cycles do not exist

The last three relation-module operators are
\[
L_2=1-X,\qquad L_3=U^{-1}-t,\qquad L_4=t-1.
\]
Their incidence graph on \(Q/\langle c\rangle\) is generated by
\[
t,\qquad X,\qquad G=U^{-1}t^{-1}.
\]
In the semidirect coordinates \(Q=F(p,q)\rtimes C_2\),
\[
t=p,\qquad X=(qPQp)c,\qquad G=(qPPq)c.
\]
The parity-kernel Reidemeister--Schreier images are
\[
p,\quad qPPqPqpQ,\quad qPQpqPqpQ,\quad
qPQppQPq,\quad qPQppQQp.
\]
Their deterministic Stallings core has four vertices and eight unoriented
edges, hence rank five. Therefore
\[
\langle t,X,G\rangle\cong F_3
\]
is torsion-free and acts freely on every \(C\)-vertex orbit. The incidence
graph is a disjoint union of Cayley trees, so
\[
L_2y_2+L_3y_3+L_4y_4=0
\]
has no nonzero finitely supported solution. Every remote homogeneous
syzygy must involve \(L_0\) or \(L_1\).

### An exact remote syzygy and the next four-point obstruction

There is a \(23\)-entry integral homogeneous syzygy \(w\) with
\[
\sum_iL_iw_i=0.
\]
It uses \(L_0\), has coefficient \(\ell^1\)-norm \(35\), and has exactly
four entries outside the one-hop set:
\[
(2,cTT),\quad(3,TTcTT),\quad
(3,TTctcTcT),\quad(4,TcTT).
\]
Adding it to the shortest first-layer lift produces a relation-module
solution whose nonlinear residual has free length \(476\), kernel length
\(124\), and \(170\) degree-two wedge terms. It clears both earlier bits:
\[
(\Phi_\infty,\Phi_3)=(0,0).
\]
Thus the support escape is real, and the two previous functionals are not
global across the full affine first-layer solution space.

This remote lift is detected by the four-point action
\[
c=(2\ 3),\qquad t=(0\ 1\ 2).
\]
In wedge-coordinate order
\((01),(02),(03),(12),(13),(23)\), its exact defect is
\[
(-5,4,-36,17,15,-18).
\]
The induced operator image has rank five over \(\mathbb F_2\), while
adjoining the defect raises the rank to six. Equivalently, the sum of the
six wedge coordinates is one. Hence this particular remote lift still
fails in degree two.

The exact proofs and checkers are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_BINOMIAL\_FOREST.md},\\
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_REMOTE\_SYZYGY.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_binomial\_forest\_certificate.py},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_remote\_syzygy\_certificate.py}.
\end{gathered}
\]

### A source-coupled syzygy kills all three recorded bits

There is a second exact homogeneous syzygy \(z\), now with
\[
z_1=e_{ct},
\]
16 support entries and coefficient \(\ell^1\)-norm 16.  The source column
\(L_1e_{ct}\) has sum zero on both binomial-forest orbits.  In the free
basis \(A=t,B=X,G=U^{-1}t^{-1}\), its two connecting paths are
\[
ctcTcttct\xrightarrow{\ aGbaGaGbAA\ }tt,
\qquad
ttct\xrightarrow{\ aaBgA\ }ctcTctt.
\]
The displayed letters are successive left actions, read left-to-right.
Their exact edge flow reconstructs \(z\) and verifies
\(\sum_iL_i z_i=0\).

Adding \(z\) to the canonical first-layer solution produces a residual of
free length 322, kernel length 70, and wedge support 112.  The full wedge
sum is \(-10\), the three-point vector is \((-1,-21,-10)\), and the
four-point vector is \((6,6,5,6,-3,-4)\). Therefore
\[
(\Phi_\infty,\Phi_3,\Phi_4)=(0,0,0).
\]
The three recorded functionals are not a global degree-two obstruction.
They do not decide global image membership of the complete 112-term residual
in \(\sum_iL_i(\Lambda^2M)\); the next section closes that question
negatively for this lift with a different quotient.

The exact proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_PHI4\_ESCAPE.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_phi4\_escape\_certificate.py}.
\end{gathered}
\]

### A cyclic three-point quotient obstructs that lift

Global image membership of the full 112-term residual for the preceding lift
is now closed negatively. Over \(\mathbb F_2\), use
\[
c=1,\qquad t=(0\ 1\ 2)
\]
on three points. The sum of the three wedge coordinates is \(Q\)-invariant
and annihilates every \(L_i\)-image because all five operators have
augmentation zero. The source-coupled residual maps exactly to
\[
(-1,-3,-3),
\]
whose sum is odd. Thus it does not lift through degree two. The induced
operator image has rank two, while adjoining the residual raises the rank
to three.

The four functionals
\(\Phi_\infty,\Phi_3,\Phi_4,\Psi_{\rm cyc}\) also separate all 16 exact
nonlinear replays in the mod-two affine span of the two one-hop directions
and the two known remote syzygies. This is not a global classification of
all compact homogeneous syzygies.

The proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_CYCLIC\_DEGREE\_TWO\_OBSTRUCTION.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_cyclic\_degree\_two\_obstruction\_certificate.py}.
\end{gathered}
\]

### A fifth direction escapes modulo two but fails modulo three

A second \(L_1\)-coupled homogeneous syzygy has 12 entries and source
component
\[
v_1=e_{TT}.
\]
Its two exact forest paths are
\[
1\xrightarrow{\ aaBgA\ }ctcTctcTT,
\qquad
ctcT\xrightarrow{\ aGaGbA\ }tcTT,
\]
with letters read left-to-right as successive left actions. The resulting
edge flow verifies \(\sum_iL_iv_i=0\).

The nonlinear residual has free length 276, kernel length 64, and wedge
support 79. Its full, nontrivial-three-point, four-point, and cyclic
coordinate sums all vanish modulo two. This zero four-bit vector is absent
from the preceding 16-class table, so \(v\) is outside the known
four-direction span modulo two.

The same cyclic action \(c=1,t=(0\ 1\ 2)\) detects the lift over
\(\mathbb F_3\), but odd-prime wedge signs require the invariant covector
\((1,-1,1)\).  Its value on the projected wedge \((-1,-3,-4)\) is
\(-2\equiv1\pmod3\).  This covector annihilates all 15 operator columns;
the operator rank is two and the augmented rank is three. Direct support
flattening also raises the known direction rank from four to five modulo
two. Thus the fifth direction still fails at degree two.

The exact proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_MOD3\_ESCAPE\_OBSTRUCTION.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_mod3\_escape\_obstruction\_certificate.py}.
\end{gathered}
\]

### Five mod-two functionals close the known integer span

Integral coefficient classes matter across the mod-two/mod-three hierarchy.
For example,
\[
x^{\rm int}=x^{00}+2z-v
\]
kills the four earlier mod-two bits and the signed cyclic mod-three bit. Its
residual has free length 542, kernel length 134, and wedge support 264.

The new three-point action
\[
c=(1\ 2),\qquad t=(0\ 1)
\]
maps this residual to \((7,-10,20)\), whose sum is odd. The operator image
has rank two and the augmented image rank three over \(\mathbb F_2\).

Class-two Magnus coordinates are integer-valued quadratic polynomials in
the five direction coefficients. Modulo two they therefore have period
dividing four in each coefficient. Exact replay of all
\(4^5=1024\) coefficient classes finds no zero row for
\[
(\Phi_\infty,\Phi_3,\Phi_4,
  \Psi_{\rm cyc}^{(2)},\Phi_{S_3}).
\]
The five directions have rank five modulo two. Thus every integer
combination in the known affine family is globally obstructed at degree two.
This does not classify homogeneous syzygies outside that span.

The exact proof and checker are
\[
\begin{gathered}
\texttt{literature/proofs/AK3\_DEPTH4\_PERIOD\_TWO\_FIVE\_DIRECTION\_OBSTRUCTION.md},\\
\texttt{experiments/stable\_ac/depth4\_period\_two\_five\_direction\_obstruction\_certificate.py}.
\end{gathered}
\]

## Exact continuation order

1. The 24 one/two-minority free-product certificates are complete.
2. The three-class \(SU(2)\) angle interval is proved exactly.
3. Exact metric and directed-interval certificates close 24 of the 30
   three-minority signatures.
4. Attack the six remaining signatures with invariants retaining both
   relators.  For the hardest overlap, the target-basis reduction above
   excludes all axial seams and isolates the exact nonabelian kernel
   equation.  Exact triple-class identities prove majority-killing
   representations intrinsically blind for five; an independent trace-
   polynomial argument proves full majority-killing \(SU(2)\) blindness
   for the sixth. The period-two quotient is also blind by an exact
   hyperbolic witness, and its complete relation-module lift obstruction
   vanishes. Degree two rules out every one-hop lift. Remote source-coupled
   syzygies defeat the first three recorded wedge bits, but a cyclic
   three-point quotient separates the new lift, and the four functionals
   jointly separate all 16 classes in the currently known four-direction
   span. A fifth source-coupled direction kills all four mod-two bits but is
   separated by the signed cyclic invariant modulo three. A new three-point
   action then separates all 1024 mod-four coefficient classes in the known
   five-direction integer span. The next exact problem is to construct a
   compact direction outside that span, or promote the five mod-two
   functionals to a theorem about the full homogeneous syzygy module.
5. Only after all 54 are closed may the ledger claim original-source
   depth-four closure; then repeat at the first proper image.
