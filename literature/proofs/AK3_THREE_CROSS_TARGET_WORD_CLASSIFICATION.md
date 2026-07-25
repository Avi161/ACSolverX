# Complete target-word classification for exactly three AK(3) cross events

Date: 2026-07-25

Status: **PROVEN** under the fixed-\(R\), final one-\(z\)-eliminator, and
source-restoration hypotheses of the one-way and two-cross theorems.
All eight length-three target words are classified for arbitrary event
conjugators, either multiplication side, intermediate orientations, and
fixed-\(R\) quotient gauges. Six target words are self-loops. The remaining
two reduce to explicit weight-\(\pm1\) killer equations; their literal
untwisted signed-seam subcorridors are also self-loops. Arbitrary
bridge/twist geometry in those two corridors remains open. This theorem
does not trivialize AK(3).

## 1. Setup and target words

Put

\[
R=x^3t^{-4},
\qquad
G=\langle x,t\mid R\rangle,
\qquad
H=G*\langle z\rangle,
\tag{1.1}
\]

and

\[
p=xt,
\qquad
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1}.
\tag{1.2}
\]

As before,

\[
\begin{array}{c|cc}
&\sigma_z&\operatorname{wt}\\ \hline
B&-1&7\\
D&0&1,
\end{array}
\qquad
\operatorname{wt}(x)=4,\quad
\operatorname{wt}(t)=3,\quad
\operatorname{wt}(z)=0.
\tag{1.3}
\]

A target word is a word of length three in the alphabet
\(\{B,D\}\): its \(i\)-th letter records which current slot is targeted
at event \(i\). The other current slot supplies the signed conjugate used
as source.

Whole-target inversion is absorbed into the adjacent source sign, a
reversal of multiplication side, and final orientation. Whole-target
conjugation is absorbed into the arbitrary event conjugator. Fixed-\(R\)
gauges vanish in \(H\). Thus the quotient equations below cover the
canonical shadows of arbitrary such histories.

The eight target words split as follows:

| target word | conclusion |
|---|---|
| \(BBB,DDD\) | one-way theorem: self-loop |
| \(BBD,BDD,DDB\) | Sections 2--4: self-loop |
| \(BDB\) | strict three-cross theorem: self-loop |
| \(DBB,DBD\) | six-row killer equations |

\[
\tag{1.4}
\]

The strict word \(DBD\) and its untwisted closure are proved in
`literature/proofs/AK3_THREE_CROSS_KILLER_REDUCTION.md`.
It remains to prove the three new closed words and classify \(DBB\).

## 2. The word \(BBD\) closes

Let signed conjugates of \(D^\epsilon,D^\eta\) successively target the
\(B\)-slot, producing \(B_1,B_2\), and then let a signed conjugate of
\(B_2^\theta\) target \(D\), producing \(D_1\):

\[
\epsilon,\eta,\theta\in\{1,-1\}.
\tag{2.1}
\]

### 2.1 Delete the source \(B_2\)

If \(B_2\), the source of the third event, is the final isolator,
evaluation kills the third-event factor in \(D_1\). The surviving
\(D\)-slot returns to its baseline evaluated shadow. The first two events
are one-way passive-\(D\) traffic targeting \(B_2\), so the one-way
theorem returns the endpoint to AK(3).

### 2.2 Delete the target \(D_1\)

Suppose instead that

\[
I=aD_1^\delta a^{-1}=z^{-1}e.
\tag{2.2}
\]

Quotient by the original \(D\):

\[
K_D
=
H/\langle\!\langle D\rangle\!\rangle
\cong
\langle G,z\mid zxz^{-1}=t\rangle.
\tag{2.3}
\]

Both earlier source factors disappear, so

\[
B_1=B_2=B
\tag{2.4}
\]

in \(K_D\), and \(D_1\) is conjugate to \(B^\theta\).
Stable-letter exponent gives

\[
\delta=\theta.
\tag{2.5}
\]

The length-one HNN classification therefore gives

\[
[e]_G=e_n=t^{-n}px^n
\tag{2.6}
\]

for some \(n\in\mathbb Z\).

Weight now fixes the parameter. Before evaluation,

\[
\operatorname{wt}(B_2)=7+\epsilon+\eta
\tag{2.7}
\]

and

\[
\operatorname{wt}(D_1)
=
1+\theta(7+\epsilon+\eta).
\tag{2.8}
\]

Using (2.5),

\[
\operatorname{wt}(e)
=
7+\epsilon+\eta+\theta.
\tag{2.9}
\]

Since \(\operatorname{wt}(e_n)=7+n\),

\[
\boxed{
n=\epsilon+\eta+\theta.
}
\tag{2.10}
\]

Let

\[
C=B_2[z\mapsto e],
\qquad
Q=D[z\mapsto e].
\tag{2.11}
\]

The equation \(D_1[z\mapsto e]=1\) makes \(C\) conjugate to
\(Q^{-\theta}\), independent of multiplication side. The exact HNN
endpoint identity gives

\[
[Q]_G
=
\left[t^{-n}D_pt^n\right]_G,
\qquad
D_p=t^{-1}pxp^{-1}.
\tag{2.12}
\]

The fixed-\(R\) lemma followed by AC1/AC3 returns \((R,C)\) classically to
\((R,D_p)\), and one more AC3 move returns it to
\(\operatorname{AK}(3)\).

## 3. The word \(BDD\) closes

Let \(D^\epsilon\) first target \(B\), producing \(B_1\). Then let
\(B_1^\eta\) and \(B_1^\theta\) successively target the \(D\)-slot,
producing \(D_1,D_2\). Their exponents are

\[
\sigma_z(B_1)=-1,
\qquad
\sigma_z(D_2)=-\eta-\theta\in\{0,\pm2\}.
\tag{3.1}
\]

Thus \(D_2\), the third target, cannot be a one-\(z\) isolator. If
\(B_1\), the passive source of the last two events, is the final isolator,
both source factors evaluate to one and \(D_2[z\mapsto e]\) returns to the
baseline \(D[z\mapsto e]\) shadow.

What remains is the first one-way \(D\)-source event targeting \(B_1\),
with \(B_1\) deleted and the \(D\)-survivor restored. The one-way theorem
closes it.

## 4. The word \(DDB\) closes

Let \(B^\epsilon,B^\eta\) successively target \(D\), producing
\(D_1,D_2\), and then let \(D_2^\theta\) target \(B\), producing \(B_1\).
The source of the third event has exponent

\[
\sigma_z(D_2)=-\epsilon-\eta\in\{0,\pm2\}.
\tag{4.1}
\]

It cannot be a one-\(z\) isolator. Suppose the third target is the final
isolator:

\[
I=aB_1^\delta a^{-1}=z^{-1}e.
\tag{4.2}
\]

Quotient by the original \(B\). This sets \(z=p\) and returns \(G\):

\[
K_B
=
H/\langle\!\langle B\rangle\!\rangle
\cong G.
\tag{4.3}
\]

Both earlier source factors disappear, so \(D_1=D_2=D_p\) in this
quotient. Hence for some \(g\in G\),

\[
p^{-1}[e]_G
=
gD_p^{\theta\delta}g^{-1}.
\tag{4.4}
\]

Put

\[
m=gD_p^{\theta\delta}g^{-1}.
\tag{4.5}
\]

Equation (4.4) gives \([e]_G=[pm]_G\), so the evaluated original
\(B\)-shadow is

\[
[B[z\mapsto e]]_G
=[e^{-1}p]_G
=m^{-1}.
\tag{4.6}
\]

Let

\[
C=D_2[z\mapsto e].
\tag{4.7}
\]

The identity \(B_1[z\mapsto e]=1\) makes \(C^\theta\) conjugate to the
inverse of (4.6). Therefore

\[
[C]_G
\ \text{is conjugate to}\
m^\theta,
\tag{4.8}
\]

which is a conjugate of \(D_p^\delta\). The fixed-\(R\) lemma and AC1/AC3
again return \((R,C)\) classically to AK(3).

## 5. The word \(DBB\) reaches the second killer equation

Let \(B^\epsilon\) target \(D\), producing \(D_1\). Then let
\(D_1^\eta,D_1^\theta\) successively target \(B\), producing
\(B_1,B_2\).

### 5.1 Delete the source \(D_1\)

If \(D_1\) is the final isolator, both later source factors evaluate to
one. The survivor returns to the baseline \(B\)-shadow, and the first
one-way \(B\)-source event closes the endpoint.

### 5.2 Delete the target \(B_2\)

Suppose instead that

\[
I=aB_2^\delta a^{-1}=z^{-1}e.
\tag{5.1}
\]

The exponent recurrence is

\[
\begin{aligned}
\sigma_z(D_1)&=-\epsilon,\\
\sigma_z(B_1)&=-1-\epsilon\eta,\\
\sigma_z(B_2)&=-1-\epsilon(\eta+\theta).
\end{aligned}
\tag{5.2}
\]

The all-positive and all-negative rows have absolute final exponent \(3\).
The other six rows have absolute exponent \(1\), forcing

\[
\delta=-\sigma_z(B_2).
\tag{5.3}
\]

The weight recurrence is

\[
\begin{aligned}
\operatorname{wt}(D_1)&=1+7\epsilon,\\
\operatorname{wt}(B_1)&=7+\eta(1+7\epsilon),\\
\operatorname{wt}(B_2)
&=7+(\eta+\theta)(1+7\epsilon).
\end{aligned}
\tag{5.4}
\]

Let

\[
C=D_1[z\mapsto e].
\tag{5.5}
\]

Then

\[
\operatorname{wt}(e)
=
\delta\operatorname{wt}(B_2),
\qquad
\operatorname{wt}(C)
=
\operatorname{wt}(D_1)
+\sigma_z(D_1)\operatorname{wt}(e).
\tag{5.6}
\]

The complete table is:

| \((\epsilon,\eta,\theta)\) | \(\sigma_z(B_2)\) | \(\delta\) | \(\operatorname{wt}(e)\) | \(\sigma_z(D_1)\) | \(\operatorname{wt}(C)\) |
|---|---:|---:|---:|---:|---:|
| \((+,+,+)\) | \(-3\) | -- | -- | \(-1\) | blocked |
| \((+,+,-)\) | \(-1\) | \(1\) | \(7\) | \(-1\) | \(1\) |
| \((+,-,+)\) | \(-1\) | \(1\) | \(7\) | \(-1\) | \(1\) |
| \((+,-,-)\) | \(1\) | \(-1\) | \(9\) | \(-1\) | \(-1\) |
| \((-,+,+)\) | \(1\) | \(-1\) | \(5\) | \(1\) | \(-1\) |
| \((-,+,-)\) | \(-1\) | \(1\) | \(7\) | \(1\) | \(1\) |
| \((-,-,+)\) | \(-1\) | \(1\) | \(7\) | \(1\) | \(1\) |
| \((-,-,-)\) | \(-3\) | -- | -- | \(1\) | blocked |

\[
\tag{5.7}
\]

The endpoint \((R,C)\) presents the trivial group, so

\[
\langle\!\langle C\rangle\!\rangle_G=G.
\tag{5.8}
\]

Thus \(C\) is a weight-\(\pm1\) killer of the \((3,4)\)-torus-knot group.
As in the strict \(DBD\) corridor, killer does not imply meridian, so
(5.8) does not close the arbitrary bridge/twist case.

## 6. The untwisted \(DBB\) corridor returns

Use the literal signed-seam operator

\[
\mathcal P(U,V)
=
\{\operatorname{cyc}(uv):
u\text{ is a signed cyclic rotation of }U,\
v\text{ is a signed cyclic rotation of }V\}
\tag{6.1}
\]

modulo signed cyclic rotation. No relative bridge, vertex-stabilizer
twist, or literal intermediate \(R\)-gauge is admitted.

Form

\[
\begin{aligned}
\mathcal D_1&=\mathcal P(D,B),\\
\mathcal Q&=
\{(D_1,B_1):D_1\in\mathcal D_1,\
  B_1\in\mathcal P(B,D_1)\},\\
\mathcal T_{DBB}&=
\{(D_1,B_1,B_2):(D_1,B_1)\in\mathcal Q,\
  B_2\in\mathcal P(B_1,D_1),\
  \nu_z(B_2)=1\}.
\end{aligned}
\tag{6.2}
\]

The complete finite reduction gives

\[
\boxed{
|\mathcal D_1|=16,\qquad
|\mathcal Q|=416,\qquad
|\mathcal T_{DBB}|=522,
}
\tag{6.3}
\]

with \(69\) distinct final target classes. For every triple, orient and
rotate \(B_2=z^{-1}e\). Then

\[
\boxed{
D_1[z\mapsto e]
\ \text{is freely conjugate to}\
D_p^{\pm1}.
}
\tag{6.4}
\]

Thus every literal untwisted \(DBB\) seam history is a classical AK(3)
self-loop after deletion. The dependency-free verifier

```text
tests/stable_ac/test_three_cross_target_words.py
```

reconstructs (6.2), pins all counts in (6.3), and checks all \(522\)
instances of (6.4).

## 7. Complete exactly-three target-word conclusion

The one-way theorem closes \(BBB,DDD\). Sections 2--4 close
\(BBD,BDD,DDB\). The strict theorem closes \(BDB\) and reduces \(DBD\)
to its six-row killer equation. Section 5 reduces \(DBB\) to the second
six-row killer equation. Section 6 and the strict theorem close the
literal untwisted subcorridors of both killer words.

Therefore every exactly-three-cross target word is classified. Under the
stated restoration hypotheses, a genuinely new endpoint must occur in
one of

\[
\boxed{
DBB,\qquad DBD,
}
\tag{7.1}
\]

must lie in one of six sign rows with tail weight \(5,7,\) or \(9\), and
must use a nontrivial relative bridge, vertex-stabilizer twist, or literal
intermediate \(R\)-gauge. Its survivor is necessarily a
weight-\(\pm1\) killer of \(G\).

The theorem does not cover four or more cross events, restoration failure,
a changed retained relator, a multi-\(z\) primitive eliminator, another
stabilization, or dual-source primitive-pair compression.

AK(3) remains open.
