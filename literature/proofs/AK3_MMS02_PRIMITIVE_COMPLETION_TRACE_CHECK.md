# Fixed-donor primitive completion: an integral obstruction

Date: 5 September 2026.

Status: fixed-$\overline A$-donor primitive completion is excluded for every
integer by the integral obstruction below. This does not obstruct changing
both rows, stabilization, the MMS02 bridge, or AK(3). The earlier trace
method and bounded probe are retained with their original scopes.

## Exact constructive criterion

Use the pinned words and the presented group
$Q_A=\langle x,y\mid\overline A\rangle$ from the
[MMS02 bridge](AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md#3-exact-rank-two-word-problems).
Its abelianization sends $x$ to $1$ and $y$ to $0$, and sends $\overline B$
to $-1$. A primitive word representing a conjugate of $\overline B$ therefore
has exponent vector $(-1,m)$ for some integer $m$. The
[rank-two primitive classification](https://arxiv.org/pdf/0802.2731) makes
its conjugacy class that of $Xy^m$. Consequently fixed-$\overline A$-donor
primitive completion is equivalent to

\[
 \overline B\sim Xy^m\quad\hbox{in }Q_A
 \qquad\hbox{for some }m\in\mathbb Z.
\]

An inverse-oriented replacement is inverted first. A conjugacy witness and
a normal-closure certificate would supply restored-donor moves replacing
$\overline B$ by $Xy^m$. Substituting $x=y^m$ then sends $\overline A$ to
$y$, since its exponent vector is $(0,1)$. Further donor moves give
$(y,Xy^m)$ and then $(y,X)$, proving ordinary AC triviality of this rank-two
pair and, through the verified corridor, stable AK(3). The theorem below
shows that no such witness exists. Previously, the bridge's literal
nonconjugacy excluded $m=1$, and its subsequent $q\sim X$ normalization
also excluded $m=0$. The all-integer proof is independent of transferring
the standard-AK3 fixed-donor theorem to this different retained donor.

## Why the proposed nonconstant-trace argument stops

Let $\rho:Q_A\to\mathrm{SL}_2(\mathbb C)$ be any representation. Write
$a=y$, $b=xyX$. The
[literal HNN presentation](AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md#4-gate-a-is-nontrivial-by-magnus-rewriting)
gives $\phi(a)=b$ and $\phi(b)=b^2a^{-1}bab^{-1}$, where $\phi$ is induced
by conjugation by $x$. Put $z=\operatorname{tr}\rho(a)=\operatorname{tr}\rho(b)$
and $c=\operatorname{tr}\rho(ab)$. The determinant-one trace identities give

\[
 K:=\operatorname{tr}\rho([b,a^{-1}])=2z^2+c^2-z^2c-2.
\]

Cyclic invariance and $b^2=zb-I$ yield

\[
 \begin{aligned}
 z=\operatorname{tr}\rho(\phi(b))
   &=\operatorname{tr}\rho(ba^{-1}ba)=z^2-K,\\
 c=\operatorname{tr}\rho(\phi(ab))
   &=\operatorname{tr}\rho(b^2a^{-1}ba)=z^2-z.
 \end{aligned}
\]

Eliminating $K,c$ gives

\[
 0=z^2+c^2-z^2c+z-2=-(z-2)(z-1)(z+1).
\]

Thus $\operatorname{tr}\rho(y)\in\{2,1,-1\}$ for every such representation.
In particular it is constant on each irreducible character component.
The source normalization gives $t_0=t_1=\operatorname{tr}\rho(X)$ for
$t_m=\operatorname{tr}\rho(Xy^m)$, and Cayley--Hamilton gives
$t_{m+1}=zt_m-t_{m-1}$ for all integers $m$. The intended comparison of
degrees in a *varying* $z$ therefore has no honest component on which to run.
This does not assert any equality between $\operatorname{tr}\rho(B)$ and
$t_m$, classify the three constant-trace cases, or decide primitive completion.

## Bounded symbolic control

The [one-checkpoint probe](../../experiments/stable_ac/mms02_primitive_trace_probe.py)
uses $x=\operatorname{diag}(s,s^{-1})$ and

\[
 y=\begin{pmatrix}
 1-s^2d&1\\ d(1-s^2)-s^2d^2&1+d
 \end{pmatrix}.
\]

It computes all four entries of $\overline A-I$, rather than treating the
determinant and initial trace conditions as a representation certificate.
Those conditions hold identically, but $s=2,d=0$ does not kill $\overline A$.
The [independent controls](../../tests/stable_ac/test_mms02_primitive_trace_probe.py)
compare direct rational matrix evaluation with the Laurent coefficients and
check the polynomial elimination. They check finite calculations, not the
universal theorem in place of its proof above. No representation census was
run; this checkpoint stops the nonconstant-trace method rather than extending it.

## One bounded constructive free-word probe

The primitive-completion criterion also permits an exact positive-certificate
probe without representations. Use the bridge's embedded stages
$j_n(w)=x^{-n}wx^n$ and $j_n(w)=j_{n+1}(\phi(w))$. Put

\[
 d_0=\phi(b)=\mathtt{bbAbaB},\quad
 \delta=\mathtt{bAbABaBB},\quad
 u_3=d_0\delta^{-1},\quad H=\phi^3(a).
\]

The literal height scan gives $\overline B=j_3(u_3)X$. For a conjugator
$c=j_3(N)$, moving all coefficients to stage four gives

\[
 c^{-1}\overline Bc=j_4(\phi(N)^{-1}\phi(u_3)N)X,
 \qquad Xy^m=j_4(H^m)X.
\]

The free base embeds, so equality is exactly the free-word test
$\phi(N)^{-1}\phi(u_3)N=H^m$. Since $H$ has exponent vector $(0,4)$,
the left word determines the only possible integer $m$; if its first
exponent is nonzero or its second is not divisible by four, none exists.
The remaining test uses freely reduced powers, including zero and negative
powers. Thus each tested $N$ covers all integers, not a selected range of $m$.

The single [probe](../../experiments/stable_ac/mms02_primitive_completion_probe.py)
checked exactly the first 1,000 freely reduced words in breadth-first order
with alphabet $a,b,A,B$, including the empty word, at stage three only.
The [saved artifact](../../results/stable_ac/theory/mms02_primitive_completion_stage3_20260905.json)
contains every candidate: **no completion was found**. Before the scan,
the raw $\overline B$ word was independently transported to stage three.
For $m=2,0,-2$, the control coefficient $b d_0^m a^{-1}$ with $N=b$
gives $H^m$ exactly; all three controls passed. A truncated monodromy was
rejected. The [independent replay](../../tests/stable_ac/test_mms02_primitive_completion_probe.py)
also checks the full base relator and every saved candidate.

This ends the registered finite probe. By itself it proves no exclusion for other
stage-three conjugators, other stages, or the all-integer primitive-completion
criterion. No larger scan follows. The independent theorem below decides
that criterion; the literal bridge and both AK(3) gates remain unresolved.

## All integer primitive completions are excluded

**Theorem (fixed-donor primitive-completion obstruction).** For every
$m\in\mathbb Z$, the elements $\overline B$ and $Xy^m$ are not conjugate in
$Q_A$. Thus no sequence keeping $\overline A$ as a fixed donor, up to its
restored conjugations and inversions, can replace $\overline B$ by a
primitive word. This is not an obstruction to moves changing both rows or
using additional live stabilization rows.

### Descent of arbitrary conjugators

Retain $F_0=F(a,b)$, $\phi$, $j_n$, $d_0$, and $u_3$ above. Literal reduction
gives

\[
 u_3=d_0^2ab^{-1},\qquad
 J:=\phi(F_0)=\langle b,a^{-1}ba\rangle.
\]

Indeed $d_0=b^2(a^{-1}ba)b^{-1}$ and
$a^{-1}ba=b^{-2}d_0b$. Suppose $c^{-1}\overline Bc=Xy^m$.
If $c$ has height $k$, replacing it by $c(Xy^m)^k$ preserves the equality
and gives height zero. The kernel of height is $\bigcup_{n\ge0}j_n(F_0)$.
Choose $c=j_M(N)$ with $M\ge3$. The embedded stage $M+1$ gives

\[
 \phi(N)^{-1}\phi^{M-2}(u_3)N=\phi^M(a)^m.
\]

All factors other than $N$ lie in $J$, so $N\in J$. Writing $N=\phi(N_1)$
lowers its stage by one. Repeating while $M\ge3$ gives $c=j_2(L)$.
At stage three the equality is now

\[
 \phi(L)^{-1}u_3L=d_0^m.
\]

It follows that $L\in u_3^{-1}J=b a^{-1}J$, so write
$L=b a^{-1}\phi(P)$. Substituting and using injectivity of $\phi$ gives

\[
 \phi(P)^{-1}abP=b^m.
\]

In turn $abP\in J$, so $P=b^{-1}a^{-1}\phi(Q)$. Another substitution and
application of injectivity give the necessary free-group equation

\[
 \boxed{\phi(Q)^{-1}abQ=a^m.}
\tag{PC}
\]

This descent uses arbitrary finite conjugators and stages; it is not a
consequence of the bounded probe. For orientation checking, if
$E_b(P)=\phi(P)^{-1}abP b^{-m}$ and
$E_a(Q)=\phi(Q)^{-1}abQ a^{-m}$, the substitutions above give the literal
identities $\phi(L)^{-1}u_3L d_0^{-m}=\phi(E_b(P))$ and
$E_b(P)=\phi(E_a(Q))$.

### An integral Fox obstruction

Equation (PC) is equivalent to $\phi(Q)=abQ a^{-m}$. Abelianizing in
$F_0$ gives $[Q]=(m-1,2-m)$. Let $F(a,b),G(a,b)$ be the abelianized left
Fox derivatives of $Q$ with respect to $a,b$, respectively, in
$\mathbb Z[a^{\pm1},b^{\pm1}]$. Define

\[
 f(t)=F(t,t^2),\qquad g(t)=G(t,t^2),\qquad
 S_n(t)=\frac{t^n-1}{t-1}\quad(n\in\mathbb Z).
\]

Every $S_n$ is a finite Laurent polynomial, including when $n\le0$.
The chain rule, $\partial_a\phi(a)=0$, and
$\partial_a\phi(b)=a^{-1}b^2(b-1)$ after abelianization give

\[
 abF=a^{-1}b^2(b-1)G(b,b^2)-1+b^{3-m}S_m(a).
\]

Evaluating at $(a,b)=(t,t^2)$ yields

\[
 f(t)=(t^2-1)g(t^2)-t^{-3}+t^{3-2m}S_m(t).
\]

The fundamental Fox identity at the same evaluation is
$(t-1)f(t)+(t^2-1)g(t)=t^{3-m}-1$. Eliminating $f$ gives

\[
 \boxed{(t^2-1)g(t^2)+(t+1)g(t)=S_{3-2m}(t)+t^{-3}.}
\tag{M}
\]

The right side never vanishes. For $m\le2$ its least exponent is $-3$;
for $m\ge4$ its least exponent is $3-2m\le-5$. Both are odd. If a nonzero
Laurent polynomial $g$ has nonnegative least exponent, the left side has
no negative exponents. Otherwise let its least exponent be $\ell<0$.
The left side then has least exponent $2\ell$, with nonzero coefficient
from $-g(t^2)$ alone. This even exponent rules out every $m\ne3$.
The case $g=0$ is already impossible because the right side is nonzero.

For $m=3$, the right side is $-t^{-2}-t^{-1}$. The least-exponent argument
forces $\ell=-1$, and degree $-2$ forces $g_{-1}=1$. The coefficient at
degree $-1$ on the left is then $g_{-1}=1$: the first summand has only
even exponents, and $g_{-2}=0$. It cannot equal the coefficient $-1$ on
the right. Thus (M), hence (PC), has no solution for any integer $m$.
This proves the theorem.

### Independent controls and terminal scope

The [literal and Fox controls](../../tests/stable_ac/test_mms02_primitive_completion_obstruction.py)
check the two coset substitutions, the pinned source coefficient, and an
independent direct Fox scan of
$\phi(Q)a^mQ^{-1}b^{-1}a^{-1}$. For words with exponent vector
$(m-1,2-m)$, its evaluated $a$-derivative equals $t^3$ times the difference
between the two sides of (M). Finite test cases verify these calculations;
the arbitrary-stage descent and least-exponent proof supply the universal
quantifiers.

The exceptional coefficient argument is genuinely integral. For $m=3$
and $g=t^{-1}$ the difference in (M) is $2+2t^{-1}$, nonzero over
$\mathbb Z$ but zero over $\mathbb F_2$. The control prevents silently
promoting a mod-two computation to this proof.

The terminal result is precisely the fixed-$\overline A$ primitive-completion
obstruction. It closes that entire criterion without new conjugator stages,
trace components, or residual categories. It does not prove that
$(\overline A,\overline B)$ is AC-nontrivial, prevent intermediate changes
to $\overline A$, or resolve stable AK(3), ordinary AK(3), or the MMS02 bridge.
