# Four shortest nonaxial seams in the hardest depth-four recurrence

## 1. Scope

Work in the target-adapted basis \(F=\langle c,t\rangle\), with the source
rows \(A,B\) and recurrence

\[
\begin{aligned}
R&=Ah_0B^{-1}h_0^{-1},\\
S&=Bh_1R^{-1}h_1^{-1},\\
U&=Rh_2S^{-1}h_2^{-1},\\
Z&=U^{-1}h_3Sh_3^{-1}.
\end{aligned}
\tag{1}
\]

This note disproves the target-independent claim that choosing all four
conjugators shortest in their evolving cyclic double cosets forces an axial
or trivial seam.

Set

\[
H=tctc^{-1}=t_0t_1\in K
\tag{2}
\]

and take

\[
h_0=h_1=h_2=h_3=H.
\]

## 2. Exact row reductions

The source rows \(A,B\) are cyclically reduced, have ordinary
\(\{c,t\}\)-lengths 23 and 18, and have primitive abelianization vectors.
Direct free reduction in (1) gives

\[
\begin{array}{c|rrrr}
 &R&S&U&Z\\ \hline
|\cdot|_F&45&71&116&195,\\
|\kappa(\cdot)|_K&13&22&35&61.
\end{array}
\tag{3}
\]

The rows \(R,S,U\) begin and end in \(t^{-1}\), so they are cyclically
reduced. Their primitive abelianization vectors show that none is a proper
power.

The normalized kernel seams are

\[
\begin{aligned}
G_0&=\sigma^5H=t_5t_6,\\
G_1&=\sigma^3H=t_3t_4,\\
G_2&=\sigma^2H=t_2t_3,\\
G_3&=\sigma^{-1}H=t_{-1}t_0.
\end{aligned}
\tag{4}
\]

Every seam is nontrivial and uses two distinct kernel generators.

## 3. Exact double-coset minima

Let \(p,q\in\mathbb Z\). Complete boundary reduction gives the following
equalities, not estimates.

For the first seam,

\[
|A^pHB^q|=
\begin{cases}
23|p|+4+18|q|,&q\ge0,\\
23|p|+18|q|,&q<0.
\end{cases}
\tag{5}
\]

For the second seam,

\[
|B^pHR^q|=18|p|+4+45|q|.
\tag{6}
\]

For the third seam,

\[
|R^pHS^q|=
\begin{cases}
45|p|+4+71|q|,&p\le0,\\
45p-4+71|q|,&p>0,\ q\le0,\\
45p+71q-36,&p>0,\ q>0.
\end{cases}
\tag{7}
\]

For the fourth seam,

\[
|U^pHS^q|=
\begin{cases}
116|p|+4+71|q|,&p\le0,\\
116p-4+71|q|,&p>0,\ q\le0,\\
116p-75,&p>0,\ q=1,\\
116p+71q-178,&p>0,\ q\ge2.
\end{cases}
\tag{8}
\]

For (8), put \(R_0=\operatorname{red}(RH)\). Then

\[
U=R_0S^{-1}H^{-1}
\]

and, for \(p,q>0\),

\[
U^pHS^q=U^{p-1}R_0S^{q-1}.
\tag{9}
\]

The boundary between \(U^{p-1}\) and \(R_0\) does not cancel, so (9)
gives the last two rows of (8).

Each of (5)--(8) has unique global minimum 4 at

\[
(p,q)=(0,0).
\]

Therefore \(H\) is the unique shortest representative in each of

\[
\langle A\rangle H\langle B\rangle,\quad
\langle B\rangle H\langle R\rangle,\quad
\langle R\rangle H\langle S\rangle,\quad
\langle U\rangle H\langle S\rangle.
\tag{10}
\]

## 4. The output is not the target

The exact kernel word \(z\) from the normalized recurrence has length 61.
Exactly two inverse pairs cancel cyclically. The remaining first and last
letters are both \(t_0^{-1}\), so no further cyclic cancellation occurs and

\[
|\operatorname{cyc}_K(z)|=57.
\tag{11}
\]

It is therefore not one positive basis letter.

## 5. Consequence

Equations (4)--(10) prove that four simultaneous cyclic-double-coset
minima do not force a trivial seam, a companion-power seam, or even a seam
supported on one kernel axis. Complete centralizers identify the legal
double-coset gauge but do not classify its shortest representatives.

This counterexample does not use the target hypothesis. A viable
peak-reduction theorem must instead be target-conditioned, use a coupled
global complexity, or prove a large-overlap dichotomy with a separate
finite exceptional analysis.

The unrestricted equation, source depth four, and the Andrews--Curtis
conjecture remain open.
