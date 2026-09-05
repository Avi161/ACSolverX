# Fixed-donor primitive completion: one trace-method checkpoint

Date: 5 September 2026.

Status: the primitive-completion interface and the trace restriction below
are proved. The primitive-completion problem is not decided. The proposed
nonconstant-trace method stops here; no character-component census follows.

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
pair and, through the verified corridor, stable AK(3). No witness is known
here. The bridge's literal nonconjugacy excludes $m=1$; its subsequent
$q\sim X$ source normalization also excludes $m=0$. Neither statement
excludes other integers, and the standard-AK3 fixed-donor theorem cannot be
transferred to this different retained donor without proof.

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
