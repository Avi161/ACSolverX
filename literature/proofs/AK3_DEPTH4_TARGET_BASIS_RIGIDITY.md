# Target-basis rigidity for the last depth-four overlap

## 1. Scope

This note studies the unresolved legal recurrence

\[
\begin{aligned}
R&=A h_0B^{-1}h_0^{-1},\\
S&=B h_1R^{-1}h_1^{-1},\\
U&=R h_2S^{-1}h_2^{-1},\\
Z&=U^{-1}h_3Sh_3^{-1},
\end{aligned}
\tag{1}
\]

for the signature \((8,3,5,-3,5)\). The target is

\[
T=\operatorname{Chr}(-4,7)=yyXyyXyyXyX.
\]

The results below do not decide whether \(Z\) can be conjugate to \(T\).
They normalize every hypothetical solution to a nonabelian equation in
the infinite cyclic-cover kernel and prove a sharp obstruction for the
entire axial stratum.

## 2. Target-adapted basis

Put

\[
c=yyX,\qquad d=yX,\qquad t=c^3d=T.
\]

The pair \(c,d\) is a free basis, with

\[
y=cd^{-1},\qquad x=d^{-1}cd^{-1}.
\]

Replacing \(d\) by \(t=c^3d\) is a Nielsen move, so \((c,t)\) is a free
basis and

\[
y=ct^{-1}c^3,\qquad x=t^{-1}c^4t^{-1}c^3.
\tag{2}
\]

Direct reduction gives

\[
\begin{aligned}
A={}&t^{-1}c^4t^{-1}c^3t^{-1}c^4t^{-1}c^{-1}tc^{-4}tc^{-1},\\
B={}&t^{-1}c^4t^{-1}c^4t^{-1}c^{-1}tc^{-3}tc^{-1}.
\end{aligned}
\tag{3}
\]

Their literal \(\{c,t\}\)-lengths are 23 and 18, and their alternating
syllable lengths in

\[
F=\langle c\rangle*\langle t\rangle
\]

are 12 and 10. Their abelian coordinates, together with those forced by
(1), are

\[
\begin{array}{c|rrrrrr}
 &A&B&R&S&U&Z\\ \hline
[\cdot]&(5,-2)&(3,-1)&(2,-1)&(1,0)&(1,-1)&(0,1).
\end{array}
\tag{4}
\]

Thus the primitive target is the single factor letter \(t\).

Eliminating \(U\) from (1) also isolates the repeated-class decoration:

\[
Z=(h_2Sh_2^{-1})R^{-1}(h_3Sh_3^{-1}).
\tag{5}
\]

Equivalently, there must be intermediate conjugacy classes satisfying

\[
\begin{aligned}
\mathcal C(R)&\cap\mathcal C(A)\mathcal C(B^{-1})\ne\varnothing,\\
\mathcal C(S)&\cap\mathcal C(B)\mathcal C(R^{-1})\ne\varnothing,\\
\mathcal C(t)&\cap\mathcal C(S)\mathcal C(R^{-1})\mathcal C(S)
\ne\varnothing.
\end{aligned}
\tag{6}
\]

The two outer factors in the last line must be conjugates of the same
intermediate row \(S\). This is exactly the information erased by the
flat nine-boundary fatgraph (eight source leaves plus the target).

## 3. Infinite cyclic-cover coordinates

Define

\[
\chi(c)=1,\qquad\chi(t)=0,
\]

and let

\[
K=\ker\chi
=\left\langle t_j=c^jtc^{-j}\mid j\in\mathbb Z\right\rangle.
\tag{7}
\]

The group \(K\) is free on the displayed basis, and conjugation by \(c\)
induces the shift

\[
\sigma(t_j)=t_{j+1}.
\]

Every \(w\in F\) has a unique form

\[
w=\kappa(w)c^{\chi(w)},\qquad \kappa(w)\in K.
\]

Scanning (3) at successive \(c\)-heights gives

\[
\begin{aligned}
a:=\kappa(A)&=
t_0^{-1}t_4^{-1}t_7^{-1}t_{11}^{-1}t_{10}t_6,\\
b:=\kappa(B)&=
t_0^{-1}t_4^{-1}t_8^{-1}t_7t_4.
\end{aligned}
\tag{8}
\]

Write \(h_i=g_ic^{k_i}\), with \(g_i\in K\). The exact kernel
recurrences are

\[
\begin{aligned}
r={}&a\,\sigma^5(g_0)\,
       \sigma^{k_0+2}(b^{-1})\,\sigma^2(g_0^{-1}),\\
s={}&b\,\sigma^3(g_1)\,
       \sigma^{k_1+1}(r^{-1})\,\sigma(g_1^{-1}),\\
u={}&r\,\sigma^2(g_2)\,
       \sigma^{k_2+1}(s^{-1})\,\sigma(g_2^{-1}),\\
z={}&\sigma^{-1}(u^{-1})\,\sigma^{-1}(g_3)\,
       \sigma^{k_3-1}(s)\,g_3^{-1}.
\end{aligned}
\tag{9}
\]

The target condition becomes

\[
Z\sim_F t
\quad\Longleftrightarrow\quad
\operatorname{cyc}_K(z)=t_m
\text{ for some }m\in\mathbb Z.
\tag{10}
\]

Only the positive letter can occur, because the total \(t\)-exponent of
\(Z\) is \(+1\).

## 4. Zero-height gauge

### Proposition

If (1) has a solution with \(Z\sim t\), it has an equivalent solution
with

\[
h_0,h_1,h_2,h_3\in K.
\tag{11}
\]

### Proof

At the four stages, multiplying a conjugator on the right by a power of
the row being conjugated leaves that conjugate unchanged. Multiplication
on the left by a power of the other row conjugates the newly formed row;
the same conjugation can be pushed through all later stages by changing
the later conjugators. The final \(Z\) changes only by conjugacy.

The available changes in the four heights are generated successively by

\[
(5,3),\qquad(3,2),\qquad(2,1),\qquad(1,1).
\]

Each pair has gcd one. Bezout therefore makes the current height zero at
each stage without disturbing the previously normalized conjugators.
This proves (11).

The same push-through identities allow shortest representatives in the
four cyclic double cosets

\[
\langle A\rangle h_0\langle B\rangle,\quad
\langle B\rangle h_1\langle R\rangle,\quad
\langle R\rangle h_2\langle S\rangle,\quad
\langle U\rangle h_3\langle S\rangle.
\tag{12}
\]

No displayed row is a proper power because its abelianization vector is
primitive, so the shown cyclic groups are the complete centralizers.
This normalization does not yet give a uniform length bound.

After (11), shifted kernel variables put (9) into the form

\[
\begin{aligned}
r&=aG_0\sigma^2(b^{-1})\sigma^{-3}(G_0^{-1}),\\
s&=bG_1\sigma(r^{-1})\sigma^{-2}(G_1^{-1}),\\
u&=rG_2\sigma(s^{-1})\sigma^{-1}(G_2^{-1}),\\
z&=\sigma^{-1}(u^{-1})G_3\sigma^{-1}(s)\sigma(G_3^{-1}).
\end{aligned}
\tag{13}
\]

Thus the unavoidable nonabelian seam gaps are \(3,2,1,1\).

## 5. Sharp obstruction for axial seams

### Theorem

If every conjugator is a pure companion power,

\[
h_i=c^{k_i}\qquad(0\le i\le3),
\]

then

\[
\left|\operatorname{cyc}_K\kappa(Z)\right|\ge25.
\tag{14}
\]

Hence \(Z\) cannot be conjugate to the one-letter target \(t\).

### Proof

Put \(w[q]=\sigma^q(w)\). Setting every \(g_i=1\) in (9) gives the cyclic
eight-block word

\[
\begin{aligned}
&b[k_2]\,
b[k_0+k_1+k_2+3]\,
a^{-1}[k_1+k_2+1]\,
b[k_0+1]\\
&\qquad a^{-1}[-1]\,
b[k_3-1]\,
b[k_0+k_1+k_3+2]\,
a^{-1}[k_1+k_3].
\end{aligned}
\tag{15}
\]

Write

\[
\begin{aligned}
B(q)&=b[q]
=t_q^{-1}t_{q+4}^{-1}t_{q+8}^{-1}t_{q+7}t_{q+4},\\
D(q)&=a^{-1}[q]
=t_{q+6}^{-1}t_{q+10}^{-1}t_{q+11}t_{q+7}t_{q+4}t_q.
\end{aligned}
\tag{16}
\]

Exact suffix--prefix comparison gives only

\[
\begin{array}{c|c|c}
\text{boundary}&\text{condition}&\text{cancelled pairs}\\ \hline
B(q)\mid B(r)&r=q+4&1\\
B(q)\mid D(r)&r=q-2&1\\
D(q)\mid B(r)&r=q&2.
\end{array}
\tag{17}
\]

No block disappears: a length-five \(B\)-block loses at most three
letters and a length-six \(D\)-block at most three. Hence no secondary
boundary forms.

Around (15), the conditions group as

\[
\begin{array}{c|c|c}
P&k_0+k_1=1&2\\
Q&k_0=0&3\\
R_0&k_0=k_1+k_2&2\\
S_0&k_3=0&2\\
T_0&k_2=k_1+k_3&2.
\end{array}
\tag{18}
\]

At most nine pairs cancel. If \(Q\) fails, the total is at most eight.
If \(Q\) holds and \(P\) fails, it is at most nine. If both hold, then
\(k_0=0,k_1=1\); the last three conditions cannot all hold, because
\(R_0,S_0\) give \(k_2=-1,k_3=0\), while \(T_0\) would give \(k_2=1\).
The bound nine is attained at \(k_i=0\).

The word (15) contains

\[
5|b|+3|a^{-1}|=5\cdot5+3\cdot6=43
\]

letters. Its cyclic length is therefore at least

\[
43-2\cdot9=25.
\]

The exact linear-consistency replay is
experiments/stable_ac/depth4_target_basis_certificate.py.

## 6. Why first-order Alexander data is blind

Abelianize \(K\) with \(P(t_j)=X^j\). From (8),

\[
\begin{aligned}
\alpha=P(a)&=-1-X^4-X^7-X^{11}+X^{10}+X^6,\\
\beta=P(b)&=-1-X^8+X^7.
\end{aligned}
\]

The exact abelianized recurrences end with

\[
P_Z=F+(X^{-1}-1)P(g_3),
\qquad F(1)=1.
\]

For any target index \(m\), take

\[
P(g_3)=\frac{X^m-F}{X^{-1}-1}.
\tag{19}
\]

The numerator vanishes at \(X=1\), so (19) is a Laurent polynomial, and
every Laurent polynomial is represented in \(K_{\mathrm{ab}}\). Thus
the full first homology of the cyclic cover, including signed support
and extremal coefficients, can always be repaired by the final seam.
This does not construct a free-group solution; it proves that only
nonabelian order can obstruct one.

## 7. Exact remaining problem

The unrestricted equation is now precisely (13): do there exist
\(G_0,G_1,G_2,G_3\in K\) whose cyclic reduction is one positive basis
letter?

Theorem (14) separates every axial solution by a margin of 24 letters.
The zero-height proposition removes all companion drift. Arbitrary
kernel seams cannot be gauged away, however, and the Alexander module is
blind. A closing proof therefore needs a peak-reduction or pumping lemma
for the repeated gap-\(3,2,1,1\) seams, or an explicit noncrossing
matching yielding concrete \(G_i\).

The signature, source depth four, and the Andrews--Curtis conjecture
remain open.
