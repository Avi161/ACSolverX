# AK(3) quotient-B length-gap design

Date: 2026-07-25

## Objective

Turn the quotient-\(B\) obstruction for one evaluated countermodel into a
necessary Bass--Serre length theorem for all six feasible prefix-\(DB\)
three-cross rows.

## Quotient equation

Use the \(DBD\) representative and put

\[
A=\pi(D_p)\in\Gamma=C_3*C_4.
\]

After quotienting the unevaluated history by the original
\(B=z^{-1}p\), the first target becomes \(A\), the second target becomes
a conjugate of \(A^\eta\), and the third target becomes, up to conjugacy,

\[
W_m(h)=AhA^mh^{-1},
\qquad
m=\eta\theta.
\]

If the actual final orientation satisfies

\[
D_2^\delta\sim z^{-1}e,
\]

then, with \(b=e^{-1}p\),

\[
b\sim W_m(h)^{-\delta}.
\]

Thus cyclic length of \(\bar b\) must belong to the spectrum of \(W_m\).

## Bass--Serre spectra

The element \(A\) has cyclic syllable length \(6\).

For disjoint axes at distance \(d\ge1\), both signs give

\[
\ell_{\mathrm{cyc}}(W_m)=12+2d\ge14.
\]

For intersecting axes, enumerate six rotations of the first \(A\), six
rotations of \(A^m\), and the overcomplete vertex-twist set

\[
\{1,X,X^2,T,T^2,T^3\}.
\]

The exact \(216\)-case distributions are

\[
\begin{array}{c|rrrrr}
m&0&6&8&10&12\\ \hline
-1&18&0&40&28&130\\
+1&0&52&0&42&122.
\end{array}
\]

Therefore

\[
\begin{aligned}
m=-1:\quad&
\ell_{\mathrm{cyc}}(\bar b)\in\{0,8,10,12\}
\text{ or }\ge14,\\
m=+1:\quad&
\ell_{\mathrm{cyc}}(\bar b)\in\{6,10,12\}
\text{ or }\ge14.
\end{aligned}
\]

The minimum \(m=1\) stratum has exactly two projected conjugacy classes:

\[
L_1=TXT^2X^2T^3X^2,
\qquad
L_2=TX^2T^3X^2T^2X.
\]

The unique weight-two \(G\)-conjugacy class above each \(L_j\) is
represented by \(\lambda_j=c^{-3}\widetilde L_j\). For a route satisfying
the necessary quotient equation, in either same-orientation row,

\[
b^{-\delta}\sim_G\lambda_j,
\qquad
[e]_G=[p\,g\lambda_j^\delta g^{-1}]_G.
\]

The old non-braid killer solves the last two evaluated equations in both
classes. The first evaluated equation and literal free-kernel liftability
remain unresolved.

## Length-zero closure

The four \(m=-1\) rows all have

\[
\operatorname{wt}(e)=7,
\qquad
\operatorname{wt}(b)=0.
\]

If \(\ell_{\mathrm{cyc}}(\bar b)=0\), then \(b=c^k\) in
\(G=\langle x,t\mid x^3=t^4\rangle\). Weight gives \(12k=0\), so
\(b=1\) and \(e=p\). The evaluated first target is \(D_p\), and the
survivor is conjugate to \(D_p^\eta\). This is a classical AK(3)
self-loop.

Hence every non-braid liftable \(m=-1\) route must cross quotient cyclic
length at least \(8\). Every \(m=+1\) route has quotient cyclic length at
least \(6\).

## Scope

The length gap is necessary, not sufficient. It does not classify the
length-\(8+\) commutator rows or the length-\(6+\) same-orientation rows.
It is not an AC obstruction.

The replay extends the existing countermodel test with both exact
intersecting-axis distributions, the six-row arithmetic table, the two
minimum same-orientation classes, and their last-two-equation
countermodels. No AC graph search is used. AK(3) remains open.
