# Every one-way \(B/D\) cross history is an AK(3) self-loop

Date: 2026-07-25

Status: **PROVEN** for every finite fixed-\(R\) history in which one
non-\(R\) slot stays a passive source and every \(B/D\) cross event targets
the other slot, provided the route ends by removing a one-\(z\) generator
isolator and any surviving passive source has its baseline quotient shadow
restored up to conjugation and inversion, while any eliminated passive
source has its baseline quotient normal closure restored. This includes an
arbitrary number of source factors and arbitrary conjugators. It does not
trivialize AK(3).

## 1. The two quotient shadows

Put

\[
R=x^3t^{-4},
\qquad
G=\langle x,t\mid R\rangle,
\qquad
H=G*\langle z\rangle,
\tag{1.1}
\]

and write

\[
p=xt,
\qquad
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1}.
\tag{1.2}
\]

The rank-three tuple \((R,B,D)\) presents the trivial group and is stably
AC-equivalent to AK(3).

An \(R\)-gauge factor vanishes in \(H\). If a source slot remains passive,
every spelling used as a source is required to lie in the normal closure
of its baseline quotient shadow. Quotienting by that normal closure erases
every source multiplication, independent of:

- the side on which it is multiplied;
- its orientation;
- the length or letters of its conjugator; and
- the number of source factors.

Whole-target conjugation and inversion remain visible only as conjugacy
and inversion in the source quotient.

If the passive source survives the final deletion, its own final quotient
shadow must be a conjugate or inverse of the baseline source shadow. Mere
membership in, or generation of, the same normal closure is insufficient
to identify the surviving relator.

If the passive source is itself the final isolator, its normal closure must
equal the baseline source normal closure. This is the distinct hypothesis
which lets evaluation kill every earlier source factor.

The two source directions have different quotient geometry.

## 2. Passive \(D\)-source: an HNN extension

Let

\[
K_D
=
H/\langle\!\langle D\rangle\!\rangle.
\tag{2.1}
\]

The relation \(D=1\) is exactly

\[
zxz^{-1}=t,
\tag{2.2}
\]

so

\[
K_D
\cong
\langle G,z\mid zxz^{-1}=t\rangle.
\tag{2.3}
\]

The group

\[
G=
\langle x\rangle
*_{\langle x^3\rangle=\langle t^4\rangle}
\langle t\rangle
\tag{2.4}
\]

contains infinite cyclic subgroups \(\langle x\rangle\) and
\(\langle t\rangle\). Thus (2.3) is the HNN extension of \(G\) identifying
\(\langle x\rangle\) with \(\langle t\rangle\) by \(x^n\mapsto t^n\).
Britton's lemma gives an injection

\[
G\hookrightarrow K_D.
\tag{2.5}
\]

In particular, equality between two \(x,t\)-words in \(K_D\) is already
equality in \(G\).

## 3. Complete HNN classification of the final \(B\)-target

Start with the \(B\)-slot as target. Allow an arbitrary finite sequence of:

1. left or right multiplication by conjugates of source spellings whose
   shadows lie in \(\langle\!\langle D\rangle\!\rangle_H\);
2. fixed-\(R\) gauge moves;
3. whole-target conjugation; and
4. whole-target inversion.

Suppose the final target normalizes by AC1/AC3 to a one-\(z\) isolator

\[
I=z^{-1}e,
\qquad e\in F(x,t).
\tag{3.1}
\]

All source and gauge factors vanish in \(K_D\). Hence \(\pi(I)\) is
conjugate in \(K_D\) to \(B^\delta\), where
\(\delta\in\{1,-1\}\).

The stable-letter exponent homomorphism

\[
\sigma_z:K_D\longrightarrow\mathbb Z
\tag{3.2}
\]

is well defined because (2.2) has exponent zero. Since

\[
\sigma_z(I)=-1,\qquad
\sigma_z(B)=-1,\qquad
\sigma_z(B^{-1})=1,
\tag{3.3}
\]

we must have \(\delta=1\).

The word \(z^{-1}p\) is cyclically reduced of stable-letter length one.
Its conjugate \(z^{-1}e\) has the same translation length and already has
one stable letter, so it is cyclically reduced as well. The length-one case
of the Collins conjugacy theorem reduces their conjugacy, after fixing the
cyclic position of \(z^{-1}\), to a conjugator \(g\in G\):

\[
g^{-1}(z^{-1}p)g=z^{-1}e.
\]

For the Britton normal form on the left to begin with \(z^{-1}\), the
element \(g\) must lie in the incident associated subgroup
\(\langle x\rangle\). Write \(g=x^n\). Then

\[
z^{-1}[e]_G
=
x^{-n}(z^{-1}p)x^n
\quad\text{in }K_D.
\tag{3.4}
\]

Relation (2.2) gives

\[
x^{-n}z^{-1}=z^{-1}t^{-n}.
\tag{3.5}
\]

Substituting (3.5) in (3.4) and using the injection (2.5) yields

\[
\boxed{
[e]_G=e_n:=t^{-n}px^n,
\qquad n\in\mathbb Z.
}
\tag{3.6}
\]

Conversely,

\[
z^{-1}e_n
=
x^{-n}(z^{-1}p)x^n
\tag{3.7}
\]

in \(K_D\), so (3.6) is the complete family rather than only a necessary
condition.

This source quotient avoids any claim that three arbitrary axes can be
classified pairwise. All cross factors disappear before the HNN conjugacy
problem is solved.

## 4. Every HNN tail conjugates the same endpoint

Let

\[
D_e=t^{-1}exe^{-1},
\qquad
D_n=t^{-1}e_nxe_n^{-1},
\qquad
D_p=t^{-1}pxp^{-1}.
\tag{4.1}
\]

Equation (3.6) gives

\[
[D_e]_G=[D_n]_G.
\tag{4.2}
\]

The fixed-relator normal-closure lemma therefore gives

\[
(R,D_e)\sim_{\mathrm{AC1-3}}(R,D_n).
\tag{4.3}
\]

The defining word \(e_n=t^{-n}px^n\) has the exact free-group identity

\[
\begin{aligned}
D_n
&=t^{-1}(t^{-n}px^n)x(t^{-n}px^n)^{-1}\\
&=t^{-n}(t^{-1}pxp^{-1})t^n\\
&=t^{-n}D_pt^n.
\end{aligned}
\tag{4.4}
\]

One AC3 move now gives

\[
(R,D_n)\sim_{\mathrm{AC3}}(R,D_p).
\tag{4.5}
\]

If the surviving \(D\)-slot has also undergone fixed-\(R\) gauges,
conjugation, or inversion and its final quotient shadow is restored in
that signed-conjugate orbit, its evaluated shadow is respectively equal,
conjugate, or inverse to \(D_e\) in \(G\). The fixed-relator lemma followed
by AC3/AC1 still gives (4.5).

Finally, if

\[
S=xtxt^{-1}x^{-1}t^{-1}
\tag{4.6}
\]

is the AK(3) braid relator, then

\[
D_p=t^{-1}St.
\tag{4.7}
\]

Consequently every endpoint in the passive-\(D\)-source direction is
classically AC-equivalent to AK(3).

## 5. The exact two-\(D\)-factor table

For the displayed two-event product with source signs
\(\epsilon,\eta\in\{1,-1\}\), no intermediate whole-target inversion, and
arbitrary source conjugators, extend the torus-knot weight by

\[
\operatorname{wt}(x)=4,\qquad
\operatorname{wt}(t)=3,\qquad
\operatorname{wt}(z)=0.
\tag{5.1}
\]

Then

\[
\operatorname{wt}(B)=7,
\qquad
\operatorname{wt}(D)=1.
\tag{5.2}
\]

Conjugation and fixed-\(R\) gauges preserve this weight. Therefore a final
target \(z^{-1}e\) has

\[
\operatorname{wt}(e)=7+\epsilon+\eta.
\tag{5.3}
\]

On the other hand,

\[
\operatorname{wt}(e_n)
=-3n+7+4n
=7+n.
\tag{5.4}
\]

Equations (3.6), (5.3), and (5.4) force

\[
n=\epsilon+\eta.
\tag{5.5}
\]

The complete table is

| \((\epsilon,\eta)\) | quotient tail | survivor |
|---|---|---|
| \((+,+)\) | \(e_2=t^{-2}px^2\) | \(t^{-2}D_pt^2\) |
| \((+,-)\) | \(e_0=p\) | \(D_p\) |
| \((-,+)\) | \(e_0=p\) | \(D_p\) |
| \((-,-)\) | \(e_{-2}=t^2px^{-2}\) | \(t^2D_pt^{-2}\) |

\[
\tag{5.6}
\]

These rows are realizable by exact seam recurrences. If the current target
is \(z^{-1}e_n\), the positive signed rotation

\[
xz^{-1}t^{-1}z
\tag{5.7}
\]

of \(D\) gives, after cyclic reduction,

\[
z^{-1}t^{-1}e_nx
=z^{-1}e_{n+1}.
\tag{5.8}
\]

The negative signed rotation

\[
x^{-1}z^{-1}tz
\tag{5.9}
\]

gives

\[
z^{-1}te_nx^{-1}
=z^{-1}e_{n-1}.
\tag{5.10}
\]

Thus the HNN parameter is exactly the signed seam displacement.

## 6. Passive \(B\)-source: eliminating \(z\) in the source quotient

Now reverse the traffic direction: the \(B\)-slot is the passive source and
every cross event targets the \(D\)-slot.

Quotienting by the source gives

\[
K_B
=
H/\langle\!\langle B\rangle\!\rangle
\cong G,
\qquad
z=p.
\tag{6.1}
\]

Suppose the final \(D\)-target normalizes to

\[
I=z^{-1}e.
\tag{6.2}
\]

All passive source factors and \(R\)-gauges vanish in \(K_B\). Therefore
for some \(a\in G\) and \(\delta\in\{1,-1\}\),

\[
p^{-1}[e]_G
=
aD_p^\delta a^{-1}.
\tag{6.3}
\]

Put

\[
m=aD_p^\delta a^{-1}.
\tag{6.4}
\]

Equation (6.3) is

\[
[e]_G=[p\,m]_G.
\tag{6.5}
\]

The restored \(B\)-survivor evaluates to

\[
B[z\mapsto e]=e^{-1}p.
\tag{6.6}
\]

Using (6.5),

\[
[B[z\mapsto e]]_G
=m^{-1}
=aD_p^{-\delta}a^{-1}.
\tag{6.7}
\]

The fixed-relator normal-closure lemma, AC3, and AC1 now give

\[
\left(R,B[z\mapsto e]\right)
\sim_{\mathrm{AC1-3}}
(R,D_p)
\sim_{\mathrm{AC3}}
\operatorname{AK}(3).
\tag{6.8}
\]

Fixed-\(R\) gauges, conjugation, or inversion of the surviving \(B\)-slot,
with its final quotient shadow restored in that signed-conjugate orbit,
again change (6.7) only by equality in \(G\), conjugacy, or inversion.

There is also a useful parity obstruction. The \(z\)-exponents are

\[
\sigma_z(D)=0,\qquad \sigma_z(B)=-1.
\tag{6.9}
\]

Target inversion changes the sign but not the parity of its exponent.
After \(k\) passive \(B^{\pm1}\)-source factors, every \(D\)-target has
\(z\)-exponent congruent to \(k\pmod2\). Hence an even number of such
events, in particular exactly two, cannot produce a one-\(z\) target.
Every odd history which does produce one is covered by (6.1)--(6.8).

## 7. If the passive source is eliminated

The preceding sections eliminate the modified target. The other possible
role is already determined by the passive-source absorption theorem.

If the passive \(B\)-source is the final one-\(z\) isolator and its quotient
normal closure equals the baseline \(B\)-normal closure, every factor it
contributed to the \(D\)-survivor vanishes after evaluation, and the
endpoint returns to \((R,D_p)\).

If the passive \(D\)-source is proposed as the final one-\(z\) isolator,
there is no endpoint: its quotient shadow has \(z\)-exponent zero, whereas
a normalized one-\(z\) isolator has exponent \(1\) or \(-1\).

Thus both choices of the eliminated slot are settled in both one-way
traffic directions.

## 8. Combined theorem and scope

Every finite one-way \(B/D\) cross history is a classical AK(3) self-loop
after a final one-\(z\) substitution-and-removal, provided:

1. \(R=x^3t^{-4}\) stays fixed in normal closure;
2. one non-\(R\) slot remains the passive source at every cross event;
3. every source spelling used lies in that passive source's final quotient
   normal closure;
4. every cross event targets the other slot; and
5. if the passive source survives, its final quotient shadow is a conjugate
   or inverse of its baseline shadow;
6. if the passive source is eliminated, its final quotient normal closure
   equals its baseline quotient normal closure; and
7. all other moves are fixed-\(R\) gauges, whole-relator conjugations, or
   inversions.

The stable deletion is the substitution-and-removal composite on the
rank-three trivial-group presentation, not a bare AC5 move. The conclusion
about its rank-two endpoint is classical AC equivalence.

The theorem does not cover alternating target roles, a temporary source
outside its final normal closure, an unrestored surviving source, a changed
source normal closure at deletion, a changed retained relator, a
multi-\(z\) primitive eliminator, another stabilization, or dual-source
primitive-pair compression.

AK(3) remains open.
