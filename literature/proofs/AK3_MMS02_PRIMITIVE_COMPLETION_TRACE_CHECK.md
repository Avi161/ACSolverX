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

## Opposite donor: a stopping control, not a second obstruction

For the other donor, use the literal presentation and embedded free base
from Section 5 of the [bridge note](AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md):
\[
 Q_B=F(x,y)/\langle\!\langle\overline B\rangle\!\rangle,
 \quad a=xY,\quad t=y,\quad F_0=F(a,b),
 \quad \phi_0(a)=b,\quad \phi_0(b)=d=a^{-1}bab^{-1}.
\]
Here $b=tat^{-1}$, $j_n(w)=t^{-n}wt^n$, and
$j_n(w)=j_{n+1}(\phi_0(w))$. Unlike the fixed-$\overline A$ calculation,
the induced endomorphism of $F_0^{\mathrm{ab}}$ has square zero.

The raw substitution $x=at,y=t$ in
$\overline A^{-1}=\mathtt{(xYxYXyyXYxyXy)^{-1}}$ gives height $-1$ and
stage-three coefficient $d\phi_0(d)d^{-1}=\phi_0^2(abA)$. Therefore
\[
 \overline A^{-1}=j_1(u)t^{-1},\qquad u=aba^{-1}.
\tag{OB1}
\]
Every primitive class of height $-1$ in $F(a,t)$ is represented by
$t^{-1}a^m$, for an integer $m$. Thus opposite-donor primitive completion
asks whether $\overline A^{-1}\sim t^{-1}a^m$ for some $m$.

This condition is equivalent to the literal free-group equation
\[
 \phi_0(c)^{-1}u c=a^m,\qquad c\in F_0.
\tag{OB2}
\]
Indeed, normalize a conjugator to height zero by right multiplication by
a power of the target, then write it as $j_M(N)$ with $M\ge1$. Its equation
in the embedded stage $M+1$ is
$\phi_0(N)^{-1}\phi_0^M(u)N=\phi_0^M(a)^m$.
Every other factor belongs to $\operatorname{im}\phi_0$, forcing $N$ into
that image and lowering the conjugator's stage. Descending to stage zero
gives (OB2); substitution proves the converse.

### All solvable images are vacuous for this comparison

**Proposition.** The height kernel $N=\ker(Q_B\to\mathbb Z)$ is perfect.
Every homomorphism from $Q_B$ to a solvable group factors through height;
in particular it gives identical images to $\overline A^{-1}$ and $t^{-1}a^m$
for every integer $m$.

**Proof.** We have $N=\bigcup_{n\ge0}j_n(F_0)$. Since
$\phi_0^2(F_0)\subseteq F_0'$, every element satisfies
\[
 j_n(w)=j_{n+2}(\phi_0^2(w))\in[N,N].
\]
Thus $N=[N,N]$. The cyclic quotient and perfectness give $Q_B'=N$.
A perfect subgroup of a solvable group is trivial, proving the factorization.
Both endpoints have height $-1$. $\square$

### A canonical metabelian-base solution fails literally

Let $M=F_0/F_0''$, distinct from the defect $K$ in the bridge note.
The induced map $\phi_0^2$ sends $M$ into $M'$ and kills $M'$, so
$\phi_0^4$ is the trivial endomorphism of $M$. For any integer $m$, put
\[
 T_m(Q)=u^{-1}\phi_0(Q)a^m,\qquad
 L=\prod_{i=0}^3\phi_0^i(u^{-1}),\qquad
 R=\phi_0^3(a^m)\phi_0^2(a^m)\phi_0(a^m)a^m.
\]
Then $T_m^4$ is constant on $M$, and its value $Q_m=LR$ is a fixed point.
Consequently (OB2) has a solution in this metabelian base for every integer.
In the literal free group, however,
\[
 T_m(Q_m)=L\,\phi_0^4(u^{-1}a^m)\,R.
\tag{OB3}
\]
The inserted word is nontrivial: $u^{-1}a^m$ has exponent vector $(m,-1)$,
and $\phi_0$ is injective. Hence $T_m(Q_m)\ne Q_m$ for every integer $m$.
This rejects these canonical candidates only, not other literal solutions.

The [independent controls](../../tests/stable_ac/test_mms02_opposite_donor_control.py)
replay the raw relator and target height scans, reject a corrupted monodromy,
and verify (OB3) at negative, zero, and positive slopes. Direct integral Fox
scans of its nonempty defect vanish for both generators, witnessing its
membership in $F_0''$ in those controls. The general conclusions above follow
from the endomorphism and injectivity arguments, not from finite enumeration.

The induced map on $M$ is not injective; $M$ is not an embedded HNN base to
which the earlier Britton argument can be applied. These quotient controls
alone do not decide literal (OB2). No further solvable-image census or derived
residual tower follows: the next section instead resolves the literal equation
by a free-word count.

## Opposite-donor primitive completion is excluded literally

**Theorem.** Equation (OB2) has no solution $c\in F(a,b)$ for any integer
$m$. Thus $\overline A^{-1}$ is not conjugate to $t^{-1}a^m$ in $Q_B$ for
any integer $m$, and no primitive replacement of $\overline A$ is possible
while retaining $\overline B$ as the fixed donor.

For a freely reduced word $w\in F(a,b)$, let $n_b(w)$ count occurrences
of $b$ and $b^{-1}$, without signs. Introduce the free basis $(a,q)$ with
$q=ba$; this local $q$ is not the bridge's source word $Xy$. Its images are
\[
 \phi_0(a)=b,\qquad \phi_0(q)=a^{-1}ba.
\tag{OB4}
\]
Write a nontrivial reduced word $c$ in alternating block form
\[
 c=a^{k_0}q^{\ell_1}a^{k_1}\cdots q^{\ell_s}a^{k_s},
\tag{OB5}
\]
where all $\ell_i$ and interior $k_i$ are nonzero; either endpoint $k_i$
may be zero. Pure $a$-powers are the case $s=0$.

Expanding $q=ba$ does not cancel any of its contributed $b$-letters.
At a positive-to-negative $q$-block boundary, the intervening $a$-power
is $a\,a^{k_i}a^{-1}=a^{k_i}\ne1$; at a negative-to-positive boundary
it is also $a^{k_i}\ne1$. Same-sign boundaries can remove an $a$-power
but cannot cancel the adjacent, equally signed $b$-letters. End powers
of $a$ remove no $b$-letters either. Therefore
\[
 n_b(c)=\sum_{i=1}^s|\ell_i|.
\tag{OB6}
\]
Using (OB4), the image of (OB5) is
\[
 b^{k_0}a^{-1}b^{\ell_1}a b^{k_1}\cdots
 a^{-1}b^{\ell_s}a b^{k_s}.
\]
This expression is already freely reduced after omitting zero endpoint
powers: every interior $k_i$ and every $\ell_i$ is nonzero. Thus
\[
 n_b(\phi_0(c))=\sum_{i=0}^s|k_i|+\sum_{i=1}^s|\ell_i|
 \ge n_b(c).
\tag{OB7}
\]
Moreover every nonempty image starts with $b$, $b^{-1}$, or $a^{-1}$,
never with $a$, and contains a $b$-letter.

Now rearrange (OB2) as
\[
 c=a b^{-1}a^{-1}\phi_0(c)a^m.
\tag{OB8}
\]
For $c\ne1$, its displayed prefix cannot cancel against $\phi_0(c)$,
by the first-letter observation. The final $a^m$ can cancel only terminal
$a$-letters and cannot cross a $b$-letter to reach the prefix. Hence
\[
 n_b(c)=1+n_b(\phi_0(c))\ge1+n_b(c),
\]
a contradiction. If $c=1$, the right side of (OB8) still contains exactly
one $b^{-1}$, also a contradiction. This proves the theorem.

The [focused controls](../../tests/stable_ac/test_mms02_opposite_donor_control.py)
check both count identities and the prefix boundary on signed block examples.
A can-fail control changes $u$ to $b a^{-1}$: then $c=a,m=0$ satisfies
$c=u^{-1}\phi_0(c)$ because the prefix's $b^{-1}$ does cancel. Thus the
argument depends on the exact pinned prefix, not on an arbitrary coefficient.

**Terminal scope.** Together with the fixed-$\overline A$ theorem above,
this excludes primitive completion in both fixed-donor directions for the
specific pair $(\overline A,\overline B)$. The proof uses arbitrary
conjugators and all integer slopes, with no word-length or HNN-stage bound.
It does not exclude changing both rows before completion, supply an AC
invariant, or resolve the MMS02 bridge, stable AK(3), or ordinary AK(3).

## One changed donor: an invertible free-base model

The preceding exclusions retain one of the original rows. Instead make
the single ordinary AC move
\[
 (\overline A,\overline B)\longmapsto
 (R,\overline B),\qquad R=\overline A\overline B.
\]
This section considers only that product, not a family of donor powers.
Pin the words
\[
 \overline A=xYxYXyyXYxyXy,\qquad
 \overline B=XyyXYXyxYYxy,
\]
where capitals denote inverse letters. Use the free basis
$a=x y^{-2},t=y$, with inverse $x=at^2,y=t$. Write
$a_i=t^iat^{-i}$. Scanning literal heights gives
\[
 \overline A=(a_0a_1a_0^{-2}a_{-1}a_0^{-1})t,
 \qquad
 \overline B=(a_{-2}^{-2}a_{-5}^{-1}a_{-4}^{2})t^{-1}.
\tag{CD1}
\]
Consequently the height-zero relator $R$ is
\[
 a_0a_1a_0^{-2}a_{-1}a_0^{-1}a_{-1}^{-2}a_{-4}^{-1}a_{-3}^2.
\tag{CD2}
\]
Set $b_i=a_{i-4}$. Solving (CD2) for its unique occurrence of $b_5$
gives
\[
 b_5=w=b_4^{-1}b_1^{-2}b_0b_3^2b_4b_3^{-1}b_4^2.
\tag{CD3}
\]

**Theorem (changed-donor model).** The one-relator quotient
$Q_R=F(a,t)/\langle\!\langle R\rangle\!\rangle$ is
$H\rtimes_\phi\langle t\rangle$, where $H=F(b_0,b_1,b_2,b_3,b_4)$ and
\[
 \phi(b_i)=b_{i+1}\ (0\leq i<4),\qquad \phi(b_4)=w.
\tag{CD4}
\]
In particular this base is embedded and the monodromy is an automorphism.

**Proof.** Define
\[
 \psi(b_i)=b_{i-1}\ (1\leq i\leq4),\qquad
 \psi(b_0)=b_0^2b_3b_4b_3^{-2}b_2b_3^{-1}b_2^{-2}.
\tag{CD5}
\]
Free substitution gives $\phi\psi(b_i)=\psi\phi(b_i)=b_i$ for all five
generators. Thus (CD4) defines an automorphism of the free group, whose
mapping-torus presentation has its usual embedded base. In that
presentation, the first four conjugation relations eliminate $b_0$ through
$b_3$ in favor of $a=b_4$ and $t$, giving $b_i=t^{i-4}at^{4-i}$.
The fifth relation is precisely (CD2), solved as (CD3). These are
reversible defining substitutions, so the resulting presentation is $Q_R$.
This proves the assertion without assuming an unverified HNN injection.
$\square$

In right normal forms, $(c,n)=ct^n$, simplify (CD1) using (CD3)--(CD5):
\[
 \overline A=(L,1),\quad L=b_1^{-2}b_0b_3^2,
 \qquad
 \overline B=(b_3b_2^{-1}b_3^2b_4^{-1}b_3^{-1},-1).
\tag{CD6}
\]
Their product is the identity, as required by the retained donor $R$.

### The single constructive obligation

The abelianization of $Q_R$ is generated by the height of $t$: the
relator $R$ has exponent sums $(-1,0)$ in $(a,t)$. A primitive word with
height one is conjugate in $F(a,t)$ to $a^m t$ for some integer $m$, by
the rank-two primitive conjugacy classification used above. Since
$\overline B^{-1}=\overline A$ in $Q_R$, primitive completion of the
other row while retaining $R$ is therefore equivalent to
\[
 \boxed{h^{-1}L\phi(h)=b_4^m,
 \qquad h\in H,\quad m\in\mathbb Z.}
\tag{CD7}
\]
Indeed, any conjugator in $Q_R$ can be made height zero by right
multiplication by a power of its height-one target $a^m t$, without
changing the conjugacy. Conjugating $(L,1)$ by that base element gives
$(h^{-1}L\phi(h),1)$, proving both directions of (CD7). Equality to a
conjugate of a primitive word is sufficient: a conjugate is itself
primitive, and the difference lifts to a finite normal product of the
retained donor $R$.

A solution of (CD7) would give the desired primitive-completion route;
no solution or exclusion is proved here. The earlier fixed-donor
exclusions do not apply to this newly retained product. Allow exactly
one subsequent theory checkpoint to evaluate (CD7). If it does not
yield an evaluation, freeze this route rather than introducing a new
quotient ladder, bounded conjugator census, or residual category.
This model alone does not resolve the MMS02 bridge or either AK3 gate.

The three [literal control tests](../../tests/stable_ac/test_mms02_changed_donor_model.py)
passed. They check both free-basis compositions, the unreduced height
scans, all ten automorphism/inverse compositions, the original retained
relator, both coefficients in (CD6), and the conjugacy formula. Corrupting
the final monodromy image or reversing the solved defining relation makes
the corresponding check fail. These controls verify the model, not a
solution of (CD7); no conjugator search has been run.

### Terminal evaluation: the complete A5 check is vacuous

The one permitted follow-up checkpoint tested all homomorphisms
$Q_R\to A_5$, up to a complete covering set under $S_5$ conjugation.
Choose $a$ from the identity, a double transposition, a three-cycle,
and a five-cycle, and let $t$ range through all 60 even permutations.
These 240 pairs cover every possible pair of images: $S_5$ conjugation
preserves $A_5$ and its internal conjugacy relation. This is a covering
set, not a claim that its entries are distinct orbits.

For each pair set $x=at^2,y=t$ and evaluate the pinned raw words. Use
the pair only if $R=\overline A\overline B$ evaluates to the identity.
Then compare $\overline A$ with $a^m t$ by actual $A_5$ conjugacy, not
just element order. Testing $m$ modulo 30 covers every integer slope,
since each possible order of $a$ divides 30. A true solution of (CD7)
would pass every such comparison; the converse is not asserted.

The [complete saved table](../../results/stable_ac/theory/mms02_changed_donor_a5_check_20260906.json)
has exactly 65 valid representative pairs:

- All 60 pairs with $a=1$ are valid. They have $\overline A=t$,
  $\overline B=t^{-1}$, and $a^mt=t$ for every $m$.
- There are five valid pairs with $a$ the fixed five-cycle. In each,
  $t^2=1$, $tat^{-1}=a^{-1}$, and
  $\overline A=\overline B=at$. Their image is the dihedral group of
  order ten.
- No pair with $a$ a double transposition or a three-cycle is valid.

In the dihedral cases the identity
\[
 a^k(at)a^{-k}=a^{2k+1}t
\]
shows that every $a^m t$ passes: solve $2k+1=m$ modulo five. These
conjugators already lie in $\rho(H)$, so restricting the comparison from
$A_5$ to the image of the free base gives no extra information. Thus every
homomorphism $Q_R\to A_5$ has cyclic or order-ten dihedral image, and this
entire finite test imposes no restriction on (CD7).

**Vacuity audit.** Both original rows are killed only by the trivial
representative map; there are 64 nontrivial valid images. Nevertheless
all maps are vacuous for this conjugacy test. In each dihedral case an
artificial identity target fails comparison with every $a^m t$, whereas
the actual target passes every slope. Separately, the controls distinguish
a five-cycle from its square, which have the same order but are not
conjugate in $A_5$. These controls detect vacuity and conjugacy errors;
they are not evidence that (CD7) has a solution.

All seven combined model and [finite-table verification tests](../../tests/stable_ac/test_mms02_changed_donor_a5_check.py)
passed. The final test independently evaluates every saved pair point by
point, checks the full covering set and all residues, and verifies the
cyclic/dihedral classification and both vacuity controls. The recorder
was run once; the verification does not call its table generator.

**Frozen.** The single subsequent checkpoint is spent. Equation (CD7)
remains unsolved, and this changed-donor route is now frozen without a
new finite group, nilpotent layer, conjugator census, or residual category.
The MMS02 bridge, stable AK3, and ordinary AK3 remain unresolved.
