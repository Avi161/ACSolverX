# Five finite quotients obstruct the known five-direction span

## Status

The five currently certified homogeneous first-layer directions generate no
degree-two lift, for any integer coefficients. A new three-point action over
\(\mathbb F_2\) completes the separation of every coefficient class in that
known span.

This is a global second-layer obstruction on one five-dimensional family. It
is not a classification of the complete homogeneous syzygy module and does
not solve the period-two or original free-group equation.

## 1. An integral combination escapes the first five bits

Let
\[
u_0,u_1,w_0,z,v
\]
be, respectively, the two one-hop directions, the 23-entry
\(L_0\)-coupled direction, the 16-entry \(L_1e_{ct}\)-coupled direction,
and the 12-entry \(L_1e_{TT}\)-coupled direction.

The first-layer solution
\[
x^{\rm int}=x^{00}+2z-v
\tag{1}
\]
has 36 support entries and coefficient \(\ell^1\)-norm 58. Exact nonlinear
replay gives

| quantity | value |
|---|---:|
| free residual length | 542 |
| Schreier-kernel length | 134 |
| relation-module residual terms | 0 |
| degree-two wedge support | 264 |
| degree-two coefficient \(\ell^1\)-norm | 602 |

Its full wedge sum is \(-2\). The earlier finite-action images are
\[
\begin{aligned}
\Omega_3 &: (24,-55,9),\\
\Omega_4 &: (0,1,19,10,-8,-14),\\
\Omega_{\rm cyc} &: (-3,-5,-2).
\end{aligned}
\tag{2}
\]
The full sum and the three coordinate sums in (2) are even. Moreover the
signed cyclic mod-three invariant is
\[
-3-(-5)+(-2)=0.
\tag{3}
\]
Thus (1) defeats all four earlier mod-two functionals and the signed cyclic
mod-three functional. This demonstrates why integral coefficient classes,
not merely the five basis directions, must be checked.

## 2. A new three-point action

Over \(\mathbb F_2\), let \(Q\) act on \(\{0,1,2\}\) by
\[
c=(1\ 2),
\qquad
t=(0\ 1),
\tag{4}
\]
with base point 0. Since \(c0=0\), this induces a module map from
\(M\otimes\mathbb F_2\) to the three-point permutation module.

Let \(\Phi_{S_3}\) be the sum of the three wedge coordinates. In
characteristic two, wedge orientation signs disappear, and the \(Q\)-action
permutes the unordered pairs. Hence \(\Phi_{S_3}\) is invariant. Since all
five \(L_i\) have augmentation zero, it annihilates every possible
second-layer image.

The residual from (1) maps exactly to
\[
(7,-10,20).
\tag{5}
\]
Its coordinate sum is 17, so
\[
\Phi_{S_3}=1\quad\text{in }\mathbb F_2.
\tag{6}
\]
The induced operator image has rank two; adjoining (5) raises the rank to
three. Thus (1) still fails at degree two.

## 3. Exhaustion of the known integer span

Write a general solution in the known affine family as
\[
x(a)=x^{00}+a_0u_0+a_1u_1+a_2w_0+a_3z+a_4v,
\qquad a\in\mathbb Z^5.
\tag{7}
\]
Direct support flattening shows that the five homogeneous directions have
rank five modulo two.

Every class-two Magnus coordinate of (7) is an integer-valued polynomial of
degree at most two in \(a_0,\ldots,a_4\). Reducing such a polynomial modulo
two has period dividing four in each variable: in the standard
integer-valued quadratic basis, the only nonlinear terms are
\(a_i a_j\) and \(\binom{a_i}{2}\), both periodic modulo two under
\(a_i\mapsto a_i+4\). Therefore it is exact to enumerate
\[
(\mathbb Z/4)^5,
\tag{8}
\]
not merely a bounded sample of integer coefficients.

For every one of the \(4^5=1024\) classes in (8), the certificate replays
the nonlinear residual and evaluates
\[
(\Phi_\infty,\Phi_3,\Phi_4,
  \Psi_{\rm cyc}^{(2)},\Phi_{S_3}).
\tag{9}
\]
No row of (9) is zero. The deterministic table hash is
\[
\texttt{6910f180e44cfc215ccf5fc2d668498993673484b829e7210d436551e194c1d5}.
\tag{10}
\]

Consequently every integer solution in (7) is obstructed at degree two by
at least one of the five mod-two functionals. The mod-three functional is no
longer needed for the final span theorem, although it remains the separator
for the individual \(v\)-lift.

## 4. Consequence and frontier

The obstruction hierarchy now has a precise finite-dimensional closure:

1. the first four directions occupy 16 mod-two classes, separated by four
   functionals;
2. the fifth direction raises the direction rank to five and defeats those
   four functionals;
3. \(\Phi_{S_3}\) separates every one of the 1024 mod-four coefficient
   classes in the resulting integer span.

Any degree-two lift of the exact period-two witness must therefore use a
homogeneous first-layer direction outside the known five-dimensional span.
Alternatively, a global proof could show that the five finite-quotient
functionals already separate the complete syzygy module.

The 165 exactly rewritten single-column \(L_1e_q\) sources through word
depth eight contain no escape from the combined mod-two/mod-three tests, but
that is bounded evidence only and is not part of the obstruction theorem.

## 5. Certificate

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_five\_direction\_obstruction\_certificate.py}
\]
replays (1), reproduces (2)--(6), verifies the operator rank jump, certifies
the five direction rank, and exhausts (8) with the hash (10).

The period-two witness, the hardest source-depth-four class, stable
Andrews--Curtis, and Andrews--Curtis remain open.
