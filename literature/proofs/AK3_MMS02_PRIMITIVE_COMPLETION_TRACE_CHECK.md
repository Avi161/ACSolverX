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

This ends the registered finite probe. It proves no exclusion for other
stage-three conjugators, other stages, or the all-integer primitive-completion
criterion. No larger scan follows from this negative result; the literal
bridge and both AK(3) gates remain unresolved.
