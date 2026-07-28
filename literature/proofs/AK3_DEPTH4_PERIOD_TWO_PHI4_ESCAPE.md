# A source-coupled lift defeats all three recorded degree-two bits

## Status

For the exact period-two relation-module equation
\[
d+\sum_{i=0}^4 L_i x_i=0,
\tag{1}
\]
there is an explicit 16-entry homogeneous syzygy involving the source
operator \(L_1\). Adding it to the canonical eight-entry solution makes all
three previously certified degree-two obstruction bits vanish:
\[
(\Phi_\infty,\Phi_3,\Phi_4)=(0,0,0).
\tag{2}
\]

This proves that the three functionals do not form a global obstruction on
the affine space of compactly supported first-layer solutions. It does not
prove global second-layer image membership of the resulting 112-term
degree-two residual, and it does not solve the free-group equation.

## 1. The exact syzygy

Retain
\[
Q=\langle c,t\mid c^2=1\rangle,
\qquad
M=\mathbb Z[Q/\langle c\rangle],
\]
write \(T=t^{-1}\), and let \(e_q\) denote the basis vector of the
\(C\)-vertex \(q\langle c\rangle\).

Define \(z=(z_0,\ldots,z_4)\in M^5\) by
\[
\begin{aligned}
z_0={}&0,\\
z_1={}&e_{ct},\\
z_2={}&-e_1+e_{ct}-e_{ctct},\\
z_3={}&-e_{TTctct}-e_{TTctcTct}
       +e_{TTctcTctt}-e_{TTctcTcttct},\\
z_4={}&-e_1-e_t+e_{ct}+e_{tct}+e_{Tctct}+e_{TctcTct}\\
     &{}-e_{TctcTctt}+e_{TctcTcttct}.
\end{aligned}
\tag{3}
\]
It has 16 support entries, coefficient \(\ell^1\)-norm 16, and component
augmentations
\[
(0,1,-1,-2,2).
\tag{4}
\]

Direct sparse expansion gives
\[
\sum_{i=0}^4 L_i z_i=0,
\tag{5}
\]
with individual image statistics
\[
\bigl(|\operatorname{supp}(L_i z_i)|,\|L_i z_i\|_1\bigr)
=
(0,0),(4,4),(6,6),(8,8),(12,12).
\tag{6}
\]
All integer coefficients cancel after collection.

Seven entries of (3) lie outside the original 242-variable one-hop set:
\[
\begin{gathered}
(1,ct),\quad(2,ctct),\quad(3,TTctcTcttct),\\
(4,tct),\quad(4,Tctct),\quad
(4,TctcTctt),\quad(4,TctcTcttct).
\end{gathered}
\tag{7}
\]
In particular this is a genuinely nonlocal, source-coupled syzygy. The three
previously recorded homogeneous directions have zero \(L_1\)-component, so
\(z\) is independent from their span modulo 2.

## 2. Exact forest construction

Put
\[
A=t,
\qquad B=X=ctcTcTctc,
\qquad G=U^{-1}t^{-1}=ctcTTct.
\tag{8}
\]
The last three operators are
\[
L_2=1-B,
\qquad L_3=(G-1)t,
\qquad L_4=A-1.
\tag{9}
\]
The binomial-forest theorem proves that
\(K=\langle A,B,G\rangle\cong F_3\) acts freely on
\(Q/\langle c\rangle\). Hence every \(K\)-orbit is a Cayley tree, and a
finitely supported source boundary has a finite \(L_2,L_3,L_4\) flow
exactly when its coefficient sum is zero on every orbit.

Let \(H=\ker(Q\to C_2)=F(p,q)\) and \(J=K\cap H\). The deterministic
Stallings core for the five Reidemeister--Schreier generators of \(J\) has
four vertices, and every vertex has transitions labelled
\(p,P,q,Q\). It is therefore a complete four-sheet cover of the rank-two
rose, proving \([H:J]=4\). Since \(B\) has odd parity, \(K\) maps onto
\(Q/H\), and hence \([Q:K]=[H:J]=4\).

The permutations
\[
c=(0\ 1)(2\ 3),
\qquad t=(1\ 2\ 3),
\tag{10}
\]
define a transitive four-state right action, and each of \(A,B,G\) fixes the
base state. Thus the base stabilizer contains \(K\); equality of the indices
proves that this is exactly the right \(K\)-coset action. Right multiplication
by \(c\) therefore leaves two \(K\)-orbits on \(Q/\langle c\rangle\):
\(\{0,1\}\) and \(\{2,3\}\).

The source column is
\[
L_1e_{ct}
=e_{tt}-e_{ctcTcttct}+e_{ctcTctt}-e_{ttct}.
\tag{11}
\]
Each orbit receives one positive and one negative term. Its exact orbit-sum
vector is therefore \((0,0)\).

Use lower-case letters for inverse basis elements. Direct replay of the two
Cayley-tree paths gives
\[
\begin{aligned}
e_{ctcTcttct}&\xrightarrow{\ aGbaGaGbAA\ }e_{tt},\\
e_{ttct}&\xrightarrow{\ aaBgA\ }e_{ctcTctt}.
\end{aligned}
\tag{12}
\]
Path letters in (12) are read left-to-right as successive left
multiplications; consequently the total acting group product is the reverse
of the displayed path word.

Converting the path edges using (9), and reversing the resulting source
boundary, reconstructs exactly the \(z_2,z_3,z_4\) in (3). Thus
\[
L_2z_2+L_3z_3+L_4z_4=-L_1e_{ct},
\]
which is an independent derivation of (5).

## 3. Nonlinear replay

Let \(x^{00}\) be the canonical eight-entry solution
\[
\begin{aligned}
x^{00}_0&=2e_{cT}-2e_{cTTct}-2e_{cTTctt},&
x^{00}_1&=0,\\
x^{00}_2&=-2e_{cTct}-2e_{cTctt},&
x^{00}_3&=-2e_1-e_{TTct},\\
x^{00}_4&=e_{Tct}.&&
\end{aligned}
\tag{13}
\]
Equation (5) makes \(x^{00}+z\) another exact integral solution of (1).

Lift each module basis element by
\(e_q\mapsto q c^2q^{-1}\), replay the complete nonlinear free-group
recurrence, and compare the final row with the corrected target. Exact free
reduction gives

| quantity | value |
|---|---:|
| free residual length | 322 |
| Schreier-kernel length | 70 |
| relation-module residual terms | 0 |
| degree-two wedge support | 112 |
| degree-two coefficient \(\ell^1\)-norm | 124 |

The full signed wedge sum is
\[
\sum_{v<w}a_{vw}=-10,
\tag{14}
\]
so \(\Phi_\infty=0\).

For the three-point action
\[
c=(1\ 2),\qquad t=(0\ 1\ 2),
\]
the exact signed wedge coordinates are
\[
(-1,-21,-10).
\tag{15}
\]
Their sum is \(-32\), so \(\Phi_3=0\).

For the four-point action
\[
c=(2\ 3),\qquad t=(0\ 1\ 2),
\]
the coordinates in the order
\((01),(02),(03),(12),(13),(23)\) are
\[
(6,6,5,6,-3,-4).
\tag{16}
\]
Their sum is 16, so \(\Phi_4=0\). Equations (14)--(16) prove (2).

## 4. Consequence and subsequent obstruction

Result (2) refutes the proposed global alternative that every compact
first-layer solution is detected by one of
\(\Phi_\infty,\Phi_3,\Phi_4\). It also supplies the first certified remote
syzygy using \(L_1\), rather than \(L_0\).

At this stage the stronger degree-two question was not decided. The residual
before a second-layer correction has 112 nonzero wedge terms, and
vanishing of three invariant linear functionals does not prove membership in
\[
\sum_{i=0}^4L_i(\Lambda^2M).
\tag{17}
\]
The subsequent cyclic three-point certificate decides (17) negatively for
this lift.  In the quotient \(c=1,\ t=(0\ 1\ 2)\), the projected wedge is
\((-1,-3,-3)\), whose coordinate sum is odd.  Thus the lift from this note
still fails at degree two even though it defeats all three earlier bits.

## 5. Certificate

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_phi4\_escape\_certificate.py}
\]

1. reconstructs (3) from the two paths (12);
2. checks the two source orbit sums and (5) over the integers;
3. verifies the seven remote entries (7);
4. replays the complete nonlinear recurrence; and
5. reproduces (14)--(16) and the obstruction tuple \((0,0,0)\).

An independent standalone implementation, not importing the committed
certificate helpers, returns the same paths, sparse images, residual
lengths, wedge statistics, and finite-action coordinates.

The period-two lift, the hardest source-depth-four class, stable
Andrews--Curtis, and Andrews--Curtis all remain open.
