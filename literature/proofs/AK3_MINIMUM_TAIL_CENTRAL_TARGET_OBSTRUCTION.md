# Central-target Fox obstruction for the repositioned minimum tail

Date: 2026-07-25

Status: **PROVEN**. For the repositioned row-\((+,-,-)\) candidate, the
central target

\[
g=c^{-1},
\qquad
c=x^3=t^4,
\]

does not solve the exact Fox coset equation.

The proof is not a bounded search. An exact HNN decomposition identifies
the kernel of the left coefficient \(1+L\). The problem then descends to
the augmentation ideal of

\[
Q=\langle d,K\rangle,
\]

where a second folded \(C_3*C_4\) core proves that the resulting
four-term coset vector is nonzero.

This removes the simplest target which survived the binary \(S_4\)
sieve. It does not exclude every target in the inverse image of the
finite coset \((-I)\rho(P)\). The full Fox nonliftability question, the
nonabelian free-kernel equation, and AK(3) remain open.

## 1. The central-target equation

Retain the notation of
`AK3_MINIMUM_TAIL_BINARY_COSET_SIEVE.md`. Thus

\[
\begin{aligned}
R&=\mathbb Z[G],\\
P&=\langle K,H\rangle,
\qquad H=\gamma b\gamma^{-1},\\
q&=\gamma e^{-1}=c^{-1}L,\\
A_0&=(1+L)F_0+q,\\
A_U&=(1+L)(d-K),\\
F_0&=t^{-1}-d-dte^{-1}.
\end{aligned}
\tag{1.1}
\]

The target \(g=c^{-1}\) would require

\[
\pi_P(A_0)+\pi_P(A_U)u=-[Pc^{-1}]
\tag{1.2}
\]

for some \(u\in R\).

Because \(c\) is central and \(q=c^{-1}L\),

\[
A_0+c^{-1}
=(1+L)(F_0+c^{-1}).
\tag{1.3}
\]

Therefore (1.2) is equivalent to

\[
\pi_P\!\left(
(1+L)\bigl(F_0+c^{-1}+(d-K)u\bigr)
\right)=0.
\tag{1.4}
\]

The first task is to determine the kernel of the operator in (1.4).

## 2. The exact HNN structure

The evaluated equations imply the exact identities

\[
\boxed{
LKL^{-1}=HK^{-1},
\qquad
H=(LKL^{-1})K.
}
\tag{2.1}
\]

One direct derivation uses

\[
LK=\gamma b\beta,
\qquad
\beta K\beta^{-1}b^{-1}=C^{-1},
\qquad
K=\gamma C\gamma^{-1}.
\tag{2.2}
\]

Thus

\[
\begin{aligned}
LKL^{-1}K
&=
\gamma b\beta K\beta^{-1}b^{-1}\gamma^{-1}K\\
&=
\gamma bC^{-1}\gamma^{-1}\gamma C\gamma^{-1}\\
&=
\gamma b\gamma^{-1}
=H.
\end{aligned}
\tag{2.3}
\]

Put

\[
M=LKL^{-1}.
\tag{2.4}
\]

Then

\[
\boxed{
P=\langle K,M\rangle,
\qquad
J:=\langle P,L\rangle=\langle K,L\rangle.
}
\tag{2.5}
\]

The previous subgroup theorem gives the free basis \((K,H)\) for \(P\).
Replacing \(H\) by \(HK^{-1}=M\) is a Nielsen move, so

\[
P=F(K,M).
\tag{2.6}
\]

### 2.1 Folded core for \(J\)

In \(\Gamma=C_3*C_4\), a folded precover for
\(\bar J=\langle\bar K,\bar L\rangle\) has root \(3\) and partial factor
orbits

\[
x:(3\,0\,1),\ (2),
\qquad
t:(0\,1\,2\,3).
\tag{2.7}
\]

The singleton in (2.7) is a boundary incidence, not an \(x\)-loop. The
generator paths are

\[
\begin{aligned}
\bar K=xtx:
&
3&\to0\to1\to3,\\
\bar L=xtx^2t^3:
&
3&\to0\to1\to0\to3.
\end{aligned}
\tag{2.8}
\]

After trimming the dangling state \(2\), the core is a theta graph with
three edge-states and two factor vertices. Hence its rank is two. The
two paths in (2.8) are its two fundamental loops. Consequently

\[
\boxed{
\bar J\cong F(\bar K,\bar L).
}
\tag{2.9}
\]

Any relation between \(K,L\) in \(G\) would project to a relation
between \(\bar K,\bar L\). Thus

\[
\boxed{
J\cong F(K,L),
}
\tag{2.10}
\]

and the central projection is injective on \(J\).

Because \(P=F(K,M)\) and \(M=LKL^{-1}\), \(J\) has the exact HNN
presentation

\[
\boxed{
J=
\left\langle
P,L
\ \middle|\
LKL^{-1}=M
\right\rangle.
}
\tag{2.11}
\]

## 3. Kernel of \(1+L\)

Define

\[
\mathcal B:R\longrightarrow\mathbb Z[P\backslash G],
\qquad
\mathcal B(z)=\pi_P((1+L)z).
\tag{3.1}
\]

Since \(K,M=LKL^{-1}\in P\),

\[
\mathcal B(Kh)
=
[PKh]+[PLKh]
=
[Ph]+[PM Lh]
=
\mathcal B(h).
\tag{3.2}
\]

Therefore

\[
(K-1)R\subseteq\ker\mathcal B.
\tag{3.3}
\]

Factor the domain through

\[
R/(K-1)R
\cong
\mathbb Z[\langle K\rangle\backslash G].
\tag{3.4}
\]

For every \(h\in G\), the induced map is

\[
[\langle K\rangle h]
\longmapsto
[Ph]+[PLh].
\tag{3.5}
\]

This is well-defined by (2.4). On each component indexed by a left
coset of \(J\) in \(G\), (3.5) is the unsigned edge-incidence map of the
HNN Bass--Serre tree of (2.11):

\[
\begin{aligned}
\text{vertices}&=P\backslash J,\\
\text{edges}&=\langle K\rangle\backslash J,\\
[\langle K\rangle j]&\longmapsto[Pj]+[PLj].
\end{aligned}
\tag{3.6}
\]

Unsigned incidence is injective on finitely supported integral edge
chains of a tree. Indeed, a finite nonempty support has a leaf, and the
coefficient at that leaf cannot cancel.

Hence the factor map (3.5) is injective and

\[
\boxed{
\ker\mathcal B=(K-1)R.
}
\tag{3.7}
\]

## 4. Reduction to a second coset module

Apply (3.7) to (1.4). A solution would force

\[
-(F_0+c^{-1})
\in
(d-K)R+(K-1)R.
\tag{4.1}
\]

Since

\[
d-K=(d-1)-(K-1),
\tag{4.2}
\]

the right-hand side is

\[
(d-1)R+(K-1)R
=
I_Q,
\qquad
Q:=\langle d,K\rangle.
\tag{4.3}
\]

It is the augmentation right ideal of \(Q\), and

\[
R/I_Q\cong\mathbb Z[Q\backslash G].
\tag{4.4}
\]

Using (1.1), the image of the required element is

\[
\boxed{
\pi_Q(F_0+c^{-1})
=
[Qc^{-1}]
+[Qt^{-1}]
-[Q]
-[Qdte^{-1}].
}
\tag{4.5}
\]

It remains to prove that the four displayed cosets are distinct.

## 5. Folded core for \(Q=\langle d,K\rangle\)

The projected folded precover has state set

\[
\mathcal S=\{0,1,\ldots,13\},
\qquad
\text{root }0,
\tag{5.1}
\]

and partial positive factor actions

\[
\begin{aligned}
x:\;&(0\,1\,2),\ (3\,5\,6),\ (8\,10\,11),\\
t:\;&(1\,2\,3\,4),\ (5\,7\,8\,9),\ (11\,12\,13\,0).
\end{aligned}
\tag{5.2}
\]

The \(x\)-action is undefined on
\(\{4,7,9,12,13\}\), and the \(t\)-action is undefined on
\(\{6,10\}\). The edge-states incident to both factor colors are

\[
\{0,1,2,3,5,8,11\}.
\tag{5.3}
\]

The generator paths are

\[
\begin{aligned}
\bar K=xtx:
&
0&\to1\to2\to0,\\
\bar d=xt^2xt^2x^2t^3:
&
0&\to1\to3\to5\to8\to11\to0.
\end{aligned}
\tag{5.4}
\]

The trimmed core has seven edges and six factor vertices, hence rank
two. Orient its edges from the \(x\)-vertices to the \(t\)-vertices and
take

\[
\{e_0,e_1,e_3,e_5,e_8\}
\tag{5.5}
\]

as a spanning tree. The two loop chains are

\[
\begin{aligned}
[\bar K]&=e_1-e_2,\\
[\bar d]&=-e_0+e_1-e_3+e_5-e_8+e_{11}.
\end{aligned}
\tag{5.6}
\]

Their coefficients on the two non-tree edges \(e_2,e_{11}\) form
\(\operatorname{diag}(-1,1)\). They are therefore the two fundamental
loops. It follows that

\[
\boxed{
\bar Q\cong F(\bar d,\bar K),
\qquad
Q\cong F(d,K),
\qquad
Q\cap\langle c\rangle=1.
}
\tag{5.7}
\]

The last two statements follow because any relation, including a
nonzero central lift, would project to a nontrivial relation in the free
basis \((\bar d,\bar K)\).

## 6. The four cosets are distinct

Put

\[
A=c^{-1},
\qquad
B=t^{-1},
\qquad
C=1,
\qquad
D=dte^{-1}.
\tag{6.1}
\]

The exact \(G\)-normal forms are

\[
A=c^{-1},
\qquad
B=c^{-1}t^3,
\qquad
C=1,
\qquad
D=c^{-1}xt.
\tag{6.2}
\]

For left cosets, \(Qg=Qh\) if and only if \(gh^{-1}\in Q\). The six
differences have the following projected paths in (5.2):

\[
\begin{array}{c|c|c}
\text{difference}&\text{projected shadow}&\text{path from }0\\
\hline
AB^{-1}&t&0\to11\\
AC^{-1}&1&0\to0,\ \text{but }c^{-1}\notin Q\\
AD^{-1}&t^3x^2&0\to13,\ \text{\(x\) undefined}\\
BC^{-1}&t^3&0\to13\\
BD^{-1}&t^2x^2&0\to12,\ \text{\(x\) undefined}\\
CD^{-1}&t^3x^2&0\to13,\ \text{\(x\) undefined}.
\end{array}
\tag{6.3}
\]

None is an accepted based loop. In the one case with trivial projected
shadow, (5.7) excludes the nonzero central element. Thus

\[
\boxed{
QA,QB,QC,QD
\text{ are pairwise distinct.}
}
\tag{6.4}
\]

The vector (4.5) has four distinct basis elements with nonzero
coefficients. Hence it is nonzero, so

\[
F_0+c^{-1}\notin I_Q.
\tag{6.5}
\]

This contradicts the necessary condition (4.1).

### 6.1 Independent \(S_5\) certificate

There is also a smaller independent certificate for the last
nonmembership. Define

\[
\varphi:G\longrightarrow S_5
\tag{6.6}
\]

on \(\{0,1,2,3,4\}\) by

\[
\varphi(x)=(0\,1\,2),
\qquad
\varphi(t)=(1\,2\,3\,4).
\tag{6.7}
\]

Both defining powers are the identity. Exact evaluation gives

\[
\varphi(K)=(1\,3\,4\,2),
\qquad
\varphi(d)=(2\,3).
\tag{6.8}
\]

The subgroup

\[
Q_0=\langle\varphi(K),\varphi(d)\rangle
\tag{6.9}
\]

has order eight and fixes \(0\). Since

\[
dte^{-1}=c^{-1}xt,
\tag{6.10}
\]

the image of (4.5) in
\(\mathbb Z[Q_0\backslash S_5]\) is

\[
[Q_0t^{-1}]-[Q_0xt].
\tag{6.11}
\]

These two cosets differ. Indeed, if \(Q_0g=Q_0h\), then
\(g^{-1}(0)=h^{-1}(0)\), because every element of \(Q_0\) fixes \(0\).
Here

\[
(t^{-1})^{-1}(0)=0,
\qquad
(xt)^{-1}(0)=1.
\tag{6.12}
\]

Thus (6.11) is nonzero, independently confirming (6.5).

## 7. Conclusion and scope

Therefore

\[
\boxed{
-[Pc^{-1}]-\pi_P(A_0)
\notin
\pi_P(A_U)R.
}
\tag{7.1}
\]

The central target \(g=c^{-1}\) is impossible already in the
abelianized free-kernel equation.

The theorem also proves the reusable structural facts

\[
\ker\!\left(
z\mapsto\pi_P((1+L)z)
\right)
=(K-1)R
\tag{7.2}
\]

and

\[
Q=\langle d,K\rangle\cong F_2,
\qquad
Q\cap\langle c\rangle=1.
\tag{7.3}
\]

It does not exclude every exact target whose binary image lies in
\((-I)\rho(P)\), solve the nonabelian free-kernel equation, construct an
AC-inequivalent presentation, or resolve AK(3).

The identities, two folded cores, generator paths, rank certificates,
central injectivity, and six coset separations are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

AK(3) remains open.
