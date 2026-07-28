# Pro-nilpotent blindness of the hardest depth-four equation

## 1. Scope

For the unresolved signature \((8,3,5,-3,5)\), use the target-adapted
basis

\[
c=yyX,\qquad t=\operatorname{Chr}(-4,7).
\]

Let

\[
K=\ker(\chi(c)=1,\chi(t)=0)
=\langle t_j=c^jtc^{-j}\mid j\in\mathbb Z\rangle
\tag{1}
\]

and let \(\sigma(t_j)=t_{j+1}\). The exact source kernel words are

\[
\begin{aligned}
a&=t_0^{-1}t_4^{-1}t_7^{-1}t_{11}^{-1}t_{10}t_6,\\
b&=t_0^{-1}t_4^{-1}t_8^{-1}t_7t_4.
\end{aligned}
\tag{2}
\]

After the zero-height gauge, the unresolved recurrence is

\[
\begin{aligned}
r&=aG_0\sigma^2(b^{-1})\sigma^{-3}(G_0^{-1}),\\
s&=bG_1\sigma(r^{-1})\sigma^{-2}(G_1^{-1}),\\
u&=rG_2\sigma(s^{-1})\sigma^{-1}(G_2^{-1}),\\
z&=\sigma^{-1}(u^{-1})G_3\sigma^{-1}(s)\sigma(G_3^{-1}).
\end{aligned}
\tag{3}
\]

The target condition is that \(z\) be conjugate in \(K\) to one positive
basis letter \(t_m\).

This note proves that (3) has a solution in every lower-central nilpotent
quotient of \(K\), with the solutions converging to one in the
pro-nilpotent completion of \(K\). This does not give a solution in the
free group \(K\) or in the original AK recurrence.

## 2. An explicit abelian solution

Identify

\[
K_{\mathrm{ab}}\cong\mathbb Z[X,X^{-1}],
\qquad t_j\longmapsto X^j.
\]

Put \(\alpha=P(a)\), \(\beta=P(b)\), and set
\(G_0=G_1=G_2=1\) at the abelian level. The first three lines of (3) give

\[
\rho=\alpha-X^2\beta,\qquad
\eta=\beta-X\rho,\qquad
\upsilon=\rho-X\eta.
\tag{4}
\]

Before choosing \(G_3\), the last line has polynomial

\[
F_0=-X^{-1}\upsilon+X^{-1}\eta.
\tag{5}
\]

The augmentations of \(a,b,r,s,u\) are respectively
\(-2,-1,-1,0,-1\), so

\[
F_0(1)=1.
\]

For any target index \(m\), define

\[
H_3=\frac{X^m-F_0}{1-X}.
\tag{6}
\]

The numerator vanishes at \(X=1\), hence \(H_3\) is an integral Laurent
polynomial. Choose a word \(G_3\in K\) with abelianization \(H_3\). Then

\[
P(z)=F_0+(1-X)H_3=X^m.
\tag{7}
\]

Thus (3) has the target solution modulo \(\gamma_2K\).

## 3. The graded correction lemma

Let

\[
L_n=\gamma_nK/\gamma_{n+1}K.
\]

The graded Lie ring \(L=\bigoplus L_n\) is the free Lie ring on the
countable basis \(\{t_j\}_{j\in\mathbb Z}\), and
\(\sigma(t_j)=t_{j+1}\).

### Lemma

For every \(n\ge2\),

\[
L_n=(1-\sigma)L_n+[L_{n-1},t_m].
\tag{8}
\]

### Proof

Because \(L\) is generated in degree one, Jacobi induction shows that
\(L_n\) is spanned by

\[
\{[v,t_j]\mid v\in L_{n-1},\ j\in\mathbb Z\}.
\tag{9}
\]

Fix one such bracket and put \(d=j-m\) and

\[
x=[\sigma^{-d}v,t_m].
\]

Then

\[
[v,t_j]=\sigma^d x.
\tag{10}
\]

For every integer \(d\), the difference \(\sigma^d x-x\) lies in
\((1-\sigma)L_n\), by the finite geometric-sum identity (read backwards
when \(d<0\)). Hence (10) belongs to

\[
(1-\sigma)L_n+[L_{n-1},t_m].
\]

The spanning statement (9) proves (8) integrally.
\(\square\)

## 4. Lifting through the lower-central tower

Fix \(G_0=G_1=G_2=1\), and let \(r,s,u\) be the resulting exact words
from the first three lines of (3). Put

\[
P=\sigma^{-1}(u^{-1}),\qquad Q=\sigma^{-1}(s),
\]

so the last line is the one-variable twisted expression

\[
F(g)=PgQ\sigma(g^{-1}).
\tag{11}
\]

Suppose, for some \(n\ge2\), that

\[
F(g)=ht_mh^{-1}\pmod{\gamma_nK}.
\tag{12}
\]

Choose arbitrary lifts to \(K/\gamma_{n+1}K\). Their error is an element

\[
E\in L_n.
\]

Changing \(g\) to \(gk\), with \(k\in\gamma_nK\), changes the error in
the central layer \(L_n\) by

\[
K-\sigma K\in(1-\sigma)L_n.
\tag{13}
\]

Indeed, modulo \(\gamma_{n+1}K\), both \(k\) and \(\sigma k\) are central,
so the extra factor in (11) is \(k\sigma(k^{-1})\).

Changing the target conjugator \(h\) to \(h\ell\), with
\(\ell\in\gamma_{n-1}K\), changes the target side in \(L_n\) by an
element of

\[
[L_{n-1},t_m].
\tag{14}
\]

Inner conjugation by the old \(h\) acts trivially on the central layer,
so there is no additional coefficient in (14).

By Lemma (8), corrections (13) and (14) span every possible error
\(E\). Choose \(k,\ell\) to cancel it. This lifts (12) from
\(K/\gamma_nK\) to \(K/\gamma_{n+1}K\).

The abelian solution (7) starts the induction. Hence:

### Theorem

For every \(N\ge1\), there exist \(G_3,h\in K/\gamma_{N+1}K\) such that,
with \(G_0=G_1=G_2=1\),

\[
z=ht_mh^{-1}
\]

in the free nilpotent quotient \(K/\gamma_{N+1}K\).

The correction to \(G_3\) at the \(n\)-th lift lies in \(\gamma_nK\),
while the correction to the target conjugator lies in
\(\gamma_{n-1}K\). The latter may change the chosen conjugator in the
previous quotient, but only by an element which centralizes \(t_m\) there,
so it does not change the previously established conjugacy equation.
The cumulative corrections have depths tending to infinity. They therefore
stabilize in every fixed lower-central quotient and define a solution of
(3) in the pro-nilpotent completion

\[
\widehat K_{\mathrm{nil}}
=\varprojlim_N K/\gamma_{N+1}K.
\tag{15}
\]

## 5. Consequence and limit

Every nilpotent image of \(K\) factors through one of the free nilpotent
groups above. The solution constructed there projects to it. Therefore no
obstruction obtained by evaluating the normalized equation (3) in a
nilpotent quotient of \(K\) can separate it from the target.

This is a local-solvability theorem, not a free-group solution. Residual
nilpotence says that a fixed nontrivial word survives in some nilpotent
quotient; it does not say that a compatible family of quotient solutions
comes from a single tuple of words in \(K\). The remaining obstruction can
therefore be genuinely non-nilpotent or can be a failure of algebraization
from the pro-nilpotent completion.

The exact Laurent-polynomial base (4)--(7) is replayed by

\[
\texttt{experiments/stable\_ac/depth4\_pronilpotent\_certificate.py}.
\]

The free-group equation (3), the source depth-four class, and the
Andrews--Curtis conjecture remain open.
