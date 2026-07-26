# Every qW-inverse D-power pair merges into the floor-14 corridor

Date: 2026-07-26

Status: **PROVEN**. Put

\[
Q_k=qW^{-1}D^k,
\qquad k\in\mathbb Z.
\]

Then \((Q_k,D)\) is an actual based primitive pair in
\(F(x,t,z,q)\) for every integer k. The displayed simultaneous
straightener gives one k-independent literal rank-two presentation;
the quotient Aut-orbit is independent of the straightener. One
classical retained source factor, followed by a stable ambient
automorphism, identifies that presentation with the floor-14 sibling
already produced by the proved rank-three compression corridor.

More generally, every split word \(D^a qW^{-1}D^b\) is conjugate to
\(Q_{a+b}\), so all D-only traffic around one \(qW^{-1}\) block has
the same conclusion.

For the two first-tail rows \(k=\pm1\), sequentially deleting \(Q_k\)
leaves the D-image as the unique primitive displayed survivor. Thus
their immediate primitive-single second deletion is forced to use D
and merges into the old corridor.

This proves neither AK(3) nor stable AC. It closes a specific infinite
noninterleaved D-power mechanism without AC graph search.

## 1. A hidden primitive pair

At the fixed rank-four checkpoint, write

\[
\begin{aligned}
R&=x^3t^{-4},\\
A&=\beta(R)=qx^3q^{-1}t^{-4},\\
C&=\beta(xt)q=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1},
\end{aligned}
\tag{1.1}
\]

where

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,\quad
\beta(z)=z,\quad
\beta(q)=q.
\]

Define

\[
U=Rz^{-1}xt,
\qquad
S=\beta(U).
\tag{1.2}
\]

The factorization of W gives the literal identity

\[
\boxed{S=Wq^{-1}}.
\tag{1.3}
\]

Indeed,

\[
Wq^{-1}
=
\beta(R)z^{-1}\beta(xt)qq^{-1}
=
\beta(Rz^{-1}xt).
\]

Also

\[
E:=\beta^{-1}(D)
=
t^{-1}zq^{-1}xqz^{-1}.
\tag{1.4}
\]

In letter notation,

\[
U=\texttt{xxxTTTTZxt},
\qquad
E=\texttt{TzQxqZ}.
\]

### Lemma 1.1

The ordered based pair \((U,E)\) extends to a basis of
\(F(x,t,z,q)\).

### Proof

For a map row \((X_0,T_0,Z_0,Q_0)\), substitute

\[
x\mapsto X_0,\quad
t\mapsto T_0,\quad
z\mapsto Z_0,\quad
q\mapsto Q_0.
\]

Apply the following eleven second-kind Whitehead automorphisms in
order:

\[
\begin{array}{c|cccc}
&x&t&z&q\\
\hline
1&x&t&z&qz\\
2&x&t&xz&q\\
3&x&t&tzT&qT\\
4&x&t&zT&q\\
5&x&t&zT&q\\
6&x&t&zT&q\\
7&qxQ&t&zQ&q\\
8&x&tx&zx&q\\
9&x&t&z&qX\\
10&x&t&z&qX\\
11&Qx&t&zq&q
\end{array}
\tag{1.5}
\]

The exact based pair sequence is

\[
\begin{array}{c|l|l|c}
&\text{first word}&\text{second word}&
\text{ordinary total length}\\
\hline
0&\texttt{xxxTTTTZxt}&\texttt{TzQxqZ}&16\\
1&\texttt{xxxTTTTZxt}&\texttt{TQxq}&14\\
2&\texttt{xxxTTTTZt}&\texttt{TQxq}&13\\
3&\texttt{xxxTTTZ}&\texttt{QxqT}&11\\
4&\texttt{xxxTTZ}&\texttt{QxqT}&10\\
5&\texttt{xxxTZ}&\texttt{QxqT}&9\\
6&\texttt{xxxZ}&\texttt{QxqT}&8\\
7&\texttt{qxxxZ}&\texttt{xT}&7\\
8&\texttt{qxxZ}&\texttt{T}&5\\
9&\texttt{qxZ}&\texttt{T}&4\\
10&\texttt{qZ}&\texttt{T}&3\\
11&\texttt{Z}&\texttt{T}&2
\end{array}
\tag{1.6}
\]

There are no independent cyclic rotations in (1.6): these are actual
based elements. If \(\phi\) is the composite of (1.5), then

\[
\phi(U)=z^{-1},
\qquad
\phi(E)=t^{-1}.
\tag{1.7}
\]

The replay checks every row of (1.5) against the complete set of 504
rank-four second-kind Whitehead maps. As a separate literal
automorphism certificate, the inverse of \(\phi\) is

\[
\begin{aligned}
\phi^{-1}(x)&=x^3qz^{-1}t,\\
\phi^{-1}(t)&=zq^{-1}x^{-1}qz^{-1}t=E^{-1},\\
\phi^{-1}(z)&=t^{-1}x^{-1}zt^4x^{-3}=U^{-1},\\
\phi^{-1}(q)&=x^2qz^{-1}t.
\end{aligned}
\tag{1.8}
\]

Both compositions freely reduce to the identity on all four
generators. Hence (1.7) is a based primitive-pair certificate.
\(\square\)

## 2. The all-integer Nielsen shear

Set

\[
\theta=\phi\beta^{-1}.
\]

Equations (1.2), (1.4), and (1.7) give

\[
\theta(S)=z^{-1},
\qquad
\theta(D)=t^{-1}.
\tag{2.1}
\]

Its inverse has the compact original-checkpoint form

\[
\begin{aligned}
\theta^{-1}(x)&=qx^3z^{-1}t,\\
\theta^{-1}(t)&=zx^{-1}z^{-1}t=D^{-1},\\
\theta^{-1}(z)&=
t^{-1}qx^{-1}q^{-1}zt^4qx^{-3}q^{-1}=S^{-1},\\
\theta^{-1}(q)&=qx^2z^{-1}t.
\end{aligned}
\tag{2.2}
\]

Again, direct substitution verifies both inverse compositions.

By (1.3),

\[
Q_k=qW^{-1}D^k=S^{-1}D^k.
\tag{2.3}
\]

Therefore

\[
\theta(Q_k)=zt^{-k}.
\tag{2.4}
\]

Let

\[
\lambda_k:
\quad
z\mapsto zt^k,
\qquad
x\mapsto x,\quad
t\mapsto t,\quad
q\mapsto q.
\tag{2.5}
\]

Its inverse sends \(z\mapsto zt^{-k}\). From (2.1) and (2.4),

\[
\boxed{
\lambda_k\theta(Q_k)=z,
\qquad
\lambda_k\theta(D)=t^{-1}.
}
\tag{2.6}
\]

Thus \((Q_k,D)\) is an actual primitive pair for every
\(k\in\mathbb Z\). Notice that the argument is an identity in the free
group, not a finite census over k.

### Corollary 2.1 — every split D-tail also closes

For arbitrary \(a,b\in\mathbb Z\), put

\[
Q_{a,b}=D^a qW^{-1}D^b=D^aS^{-1}D^b.
\tag{2.7}
\]

Conjugating this relator by \(D^{-a}\) gives

\[
D^{-a}Q_{a,b}D^a
=
S^{-1}D^{a+b}
=
Q_{a+b}.
\tag{2.8}
\]

Thus \(([Q_{a,b}],[D])\) is the same primitive conjugacy-class pair as
\(([Q_{a+b}],[D])\), and it has the same deletion endpoint. This
closes every D-only left/right split around one \(qW^{-1}\) block, not
just right tails.

### Classical manufacture

Every member of the family is reachable from the literal checkpoint:

\[
(A,W,D,q)
\sim_{\mathrm{AC1-3}}
(A,W,D,qW^{-1}D^k).
\tag{2.9}
\]

Invert the W-row, right-multiply it into the q-row, and restore W. This
changes only the last row from q to \(qW^{-1}\). For \(k>0\),
right-multiply the last row by D exactly k times. For \(k<0\), first
invert D, multiply exactly \(|k|\) times, and restore D. For \(k=0\),
do nothing further. Hence A, W, and D remain literally unchanged while
the last row becomes \(Q_k\).

To manufacture \(Q_{a,b}\), first manufacture \(Q_{a+b}\) and then
conjugate only that changed relator by \(D^a\). Equation (2.8) supplies
the inverse AC3 reduction.

## 3. The pair quotient is independent of k

Apply the stable ambient automorphism \(\lambda_k\theta\) to the full
checkpoint tuple

\[
(A,W,D,Q_k).
\]

The stable ambient theorem applies because this checkpoint is stably
equivalent to AK(3), hence is a balanced presentation of the trivial
group.

Use AC1 on the D-row if desired, remove all z- and t-letters from the
A- and W-rows with the two basis relators in (2.6), and apply inverse
stabilization twice. Relabel the surviving q-coordinate as y.

For every integer k, the two remaining relators are literally

```text
xYxYxYXyXyXyXy
yXyXyXyxYYxxYxYxYXyXyXyXy
```

The k-independence is structural: \(\lambda_k\) differs from the
identity only by a t-power in the z-image, and both z and t are killed
in this quotient.

The rank-two automorphism

\[
\sigma:
\quad
x\mapsto x^{-1}yx^{-3},
\qquad
y\mapsto yx^{-3}
\tag{3.1}
\]

has inverse

\[
\sigma^{-1}:
\quad
x\mapsto yx^{-1},
\qquad
y\mapsto y(yx^{-1})^3.
\tag{3.2}
\]

After \(\sigma\) and independent cyclic conjugation/inversion, the
pair is

\[
\boxed{
r=\texttt{YXXXXyxxx},
\qquad
s=\texttt{YYXXXXyxxxYxyx}.
}
\tag{3.3}
\]

The complete rank-two Whitehead check has total floor 23 at (3.3).
This floor is not itself the closure: one ordinary AC source factor
still lowers the pair.

## 4. One classical factor reaches the old floor-14 orbit

The second word in (3.3) has the exact factorization

\[
s=YrYxyx.
\tag{4.1}
\]

Put

\[
c=Yr^{-1}y.
\]

Then

\[
cs=\texttt{YYxyx}=:b.
\tag{4.2}
\]

This left-looking cancellation is an ordinary right-source AC move.
Indeed,

\[
s^{-1}b=s^{-1}cs
\]

is a conjugate of \(r^{-1}\). Invert and conjugate the r-source,
right-multiply s by that relator, and restore r. Hence

\[
(r,s)
\sim_{\mathrm{AC1-3}}
(r,b).
\tag{4.3}
\]

Now apply the stable ambient signed relabel

\[
\omega:
\quad
x\mapsto y,
\qquad
y\mapsto x^{-1}.
\tag{4.4}
\]

Its raw images are

```text
xYYYYXyyy
xxyXy
```

and independent relator normalization gives the complete floor-14
representative

```text
YXXYx | YYYYXyyyx
```

The already proved rank-three compression theorem gives

\[
\mathrm{AK}(3)
\sim_{\mathrm{st}}
\left\langle x,y\ \middle|\
x^3yx^{-4}y^{-1},\
y^{-1}xyxy^{-1}
\right\rangle,
\tag{4.5}
\]

whose exact letter pair is

```text
xxxyXXXXY | YxyxY
```

The signed relabel \(x\mapsto y^{-1},y\mapsto x\) takes (4.5), after
independent relator normalization, to the same displayed floor-14
representative. This is Corollary 4.1 of
`literature/proofs/AK3_RANK3_COMPRESSION.md`.

Consequently the Q-D power-tail quotient does not land literally on
(4.5) by the classical factor alone. Rather,

\[
\boxed{
\text{one classical AC factor}
\;+\;
\text{stable ambient normalization}
}
\]

merges it into the previously certified floor-14 stable corridor.

## 5. The two first tails have a unique primitive second survivor

The all-k proof already supplies a D-deletion after deleting \(Q_k\).
For the two rows \(k=\pm1\), one can say more: no A- or W-image can
replace D as the second primitive-single deletion.

Choose the explicit four-block straighteners of \(Q_{\pm1}\) replayed
in the companion verifier. Their cyclic source-length chains are

\[
18\to15\to11\to8\to1
\quad(k=1),
\qquad
16\to13\to10\to5\to1
\quad(k=-1).
\tag{5.1}
\]

Every block has an explicit two-sided inverse. After killing the
terminal q-coordinate, complete rank-three Whitehead descents give:

\[
\begin{array}{c|c|l|l}
k&\text{survivor}&\text{strict cyclic length chain}&
\text{terminal}\\
\hline
1&A&41,30,23,19,13,9,7&\texttt{XXXXzzz}\\
1&W&60,45,39,34,24,19,18&
\texttt{TTZXtzTXZZZxxxxxtZ}\\
1&D&3,2,1&\texttt{X}\\
-1&A&22,19,17,15,13,11,9,7&\texttt{TTTTxxx}\\
-1&W&58,51,44,37,29,24,21,19,18,17,16&
\texttt{TXtXTZTxtzzzzXXX}\\
-1&D&35,30,26,22,18,14,12,10,8,6,4,2,1&
\texttt{T}
\end{array}
\tag{5.2}
\]

The replay checks every descent map against all 90 nonidentity
rank-three second-kind Whitehead automorphisms and checks that no such
map lowers any terminal. Whitehead peak reduction therefore makes the
displayed terminal lengths complete Aut-minima. The A- and W-images
have minima greater than one and are nonprimitive; both D-images have
minimum one.

The quotient Aut-orbit is independent of the chosen straightener of a
primitive relator. Hence this proves:

\[
\boxed{
\text{after deleting }Q_{\pm1},
\text{ the D-image is the unique primitive survivor.}
}
\tag{5.3}
\]

Applying its displayed descent and deleting it gives, for both signs,
the common pair (3.3), as independently replayed from the sequential
quotients.

## 6. Exact scope

This theorem proves:

- \((qW^{-1}D^k,D)\) is a based primitive pair for every integer k;
- every split \(D^a qW^{-1}D^b\) reduces by AC3 to that power family;
- its simultaneous stable deletion has one k-independent rank-two
  endpoint;
- that endpoint merges into the certified floor-14 compression
  corridor;
- for \(k=\pm1\), D is the only immediate primitive-single second
  deletion among the displayed survivors.

It does not prove:

- that the floor-14 sibling is classically AC-trivial;
- that AK(3) is stably AC-trivial;
- that the six nonprimitive first D-tail rows cannot participate in a
  primitive pair;
- that histories with another \(S^{\pm1}\) block behave like the
  one-block family;
- that longer histories changing A, W, or D before deletion close.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_qw_d_tail_compression_merge.py` checks:

- all 11 based pair steps against the complete rank-four Whitehead
  list and every row of (1.6);
- the compact inverses (1.8) and (2.2);
- the shear identity (2.6) at seven positive, negative, and zero
  sample exponents, with the all-integer conclusion supplied
  symbolically by (2.3)--(2.6);
- the split-tail conjugacy identity (2.8) at mixed-sign samples;
- literal k-independence of the full A/W quotient;
- the rank-two automorphisms and the floor-23 pair;
- the exact retained-source factor (4.2);
- both routes into the same complete floor-14 representative;
- the two four-block sequential source straighteners;
- all six survivor minima in (5.2);
- the exact two sequential deletion endpoints.
