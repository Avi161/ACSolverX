# The MMS02 published triple reduces to two one-relator gates

## Status

This note isolates the highest-value theory route to stable AK(3).  It
proves that either of two explicit normal-closure memberships is sufficient
to AC-trivialize the published MMS02 rank-three triple

\[
 T_{\rm pub}=(A,B,Xyz).
 \tag{1}
\]

Sections 4--5 prove that both memberships are false by exact Magnus--HNN
normal forms.  This closes the two sequential donor completions and leaves
the unrestricted all-row bridge as the active route.  It does not disprove
the bridge or stable AK(3).  Any positive unrestricted bridge would still
not prove ordinary AK(3), because the verified MMS02 corridor uses the
rank-changing Tietze/AC4--AC5 passage between the rank-three triple and
AK(3).

Section 6 proves that quotient reachability for the unrestricted path is
automatic: after killing $A,B$, any two normal generators become
AC-equivalent once one identity row is retained.  Thus further
quotient obstructions cannot decide the bridge.  The remaining gate is the
Peiffer/basic-substitution closure of one explicit pair of lift residuals
in the normal closure of $A,B$.

## 1. Pinned words and verified first legs

Use uppercase letters for inverses and put

```text
A = xzYXyxZXYxyZ
B = XyxZXYXyxzXYxy
r = xyxZXY
q = Xy
v = Xyz
u = zYX
C = yxzXY
h = YX
K = [u,C]
D = h[X,r]h^-1.
```

The exact literal identities are

\[
 \boxed{
 \begin{aligned}
 A&=rK^{-1},\\
 B&=qD^{-1}.
 \end{aligned}
 }
 \tag{2}
\]

The independent donor certificate proves three separate rank-three facts:

\[
 \begin{aligned}
 (r,q,v)&\sim_{\rm AC}(x,y,z),\\
 (r,q,v)&\sim_{\rm AC}(A,q,v),\\
 (r,q,v)&\sim_{\rm AC}(r,B,v).
 \end{aligned}
 \tag{3}
\]

The last two paths are independent branches with common start; they are not
concatenated.

## 2. Two sufficient gates

Let $\langle\!\langle W\rangle\!\rangle$ denote normal closure in
$F(x,y,z)$.  Consider

\[
 \begin{aligned}
 \mathsf G_A:&
 &D&\in\langle\!\langle A,v\rangle\!\rangle,\\
 \mathsf G_B:&
 &K&\in\langle\!\langle B,v\rangle\!\rangle.
 \end{aligned}
 \tag{4}
\]

If $\mathsf G_A$ holds, write $D^{-1}$ as a finite product of conjugates of
$A^{\pm1}$ and $v^{\pm1}$.  Starting from the first donor endpoint
$(A,q,v)$, use the current first and third rows as donors to multiply that
product into the second row.  Identity (2) changes it from $q$ to $B$ and
gives

\[
 (A,q,v)\sim_{\rm AC}(A,B,v)=T_{\rm pub}.
 \tag{5}
\]

The same argument with the second donor endpoint proves

\[
 \mathsf G_B
 \Longrightarrow
 (r,B,v)\sim_{\rm AC}(A,B,v)=T_{\rm pub}.
 \tag{6}
\]

Combining either (5) or (6) with (3) proves

\[
 \boxed{
 \mathsf G_A\text{ or }\mathsf G_B
 \Longrightarrow
 T_{\rm pub}\sim_{\rm AC}(x,y,z).
 }
 \tag{7}
\]

Every normal-closure factor supplies a literal sequence of row conjugations,
inversions, and right multiplications, so (7) is constructive once the
factorization is displayed.

## 3. Exact rank-two word problems

Quotienting by $v=Xyz$ sets $z=Yx$.  Literal substitution and free
reduction give

```text
A_bar = xYxYXyyXYxyXy
D_bar = YXyyXYxyxY
B_bar = XyyXYXyxYYxy
K_bar = YxYXyxYYxyXyyyXY.
```

Therefore the two gates in (4) are exactly

\[
 \boxed{
 \begin{aligned}
 \mathsf G_A
 &\Longleftrightarrow
 \overline D=1
 \text{ in }
 Q_A=\langle x,y\mid xYxYXyyXYxyXy\rangle,\\
 \mathsf G_B
 &\Longleftrightarrow
 \overline K=1
 \text{ in }
 Q_B=\langle x,y\mid XyyXYXyxYYxy\rangle,
 \end{aligned}
 }
 \tag{8}
\]

where the defect words are respectively `YXyyXYxyxY` and
`YxYXyxYYxyXyyyXY`.

Equation (8) is the theory-first resume point.  A proof of triviality must
produce a normal-closure factorization.  A proof of nontriviality must give
an exact invariant or normal form detecting the named defect in the named
one-relator quotient.  A bounded search or failure to find a finite quotient
does neither.

## 4. Gate A is nontrivial by Magnus rewriting

The relator and defect of $Q_A$ have zero $x$-exponent.  Put

\[
 y_i:=x^iyx^{-i}.
 \tag{9}
\]

Scanning the relator at its successive $x$-heights gives

\[
 xYxYXyyXYxyXy
 \longmapsto
 y_1^{-1}y_2^{-1}y_1^2y_0^{-1}y_1y_0.
 \tag{10}
\]

Write $a=y_0$, $b=y_1$, and $d=y_2$.  The Magnus base group is

\[
 B_A=
 \left\langle a,b,d
 \mathrel{\big|}
 b^{-1}d^{-1}b^2a^{-1}ba
 \right\rangle.
 \tag{11}
\]

The relator contains $d$ exactly once and gives

\[
 \boxed{
 d^{-1}=ba^{-1}b^{-1}ab^{-2}.
 }
 \tag{12}
\]

Thus $B_A\cong F(a,b)$.  The standard Magnus decomposition is the
ascending HNN extension with stable letter $x$ and associated map

\[
 \begin{aligned}
 xax^{-1}&=b,\\
 xbx^{-1}&=d=b^2a^{-1}bab^{-1}.
 \end{aligned}
 \tag{13}
\]

The base embeds by the Magnus--Britton theorem.  Equivalently, the subgroup
$\langle b,d\rangle$ is free on the displayed generators by the
Freiheitssatz, so (13) identifies the free base $\langle a,b\rangle$ with
that subgroup.

The same height scan sends the defect to

\[
 YXyyXYxyxY
 \longmapsto
 y_0^{-1}y_{-1}^2y_{-2}^{-1}y_{-1}y_0^{-1}.
 \tag{14}
\]

Conjugating by $x^2$ shifts every index by two.  Hence the defect is trivial
in $Q_A$ exactly when the base word

\[
 d^{-1}b^2a^{-1}bd^{-1}
 \tag{15}
\]

is trivial.  Substitute (12) twice and freely reduce:

\[
 \begin{aligned}
 d^{-1}b^2a^{-1}bd^{-1}
 &=(ba^{-1}b^{-1}ab^{-2})b^2a^{-1}b
   (ba^{-1}b^{-1}ab^{-2})\\
 &\longrightarrow
 ba^{-1}ba^{-1}b^{-1}ab^{-2}.
 \end{aligned}
 \tag{16}
\]

The final word in (16) is freely reduced and nonempty in $F(a,b)$.  Base
injectivity proves

\[
 \boxed{
 \begin{aligned}
 \overline D&\ne1\text{ in }Q_A,\\
 \mathsf G_A&\text{ is false}.
 \end{aligned}
 }
 \tag{17}
\]

This closes only the S1 sequential completion.  It is not a negative result
about $T_{\rm pub}$, because S2 and unrestricted all-row paths do not factor
through $Q_A$.

## 5. Gate B is nontrivial after one Nielsen change

For $Q_B$, use the free basis

\[
 \begin{aligned}
 a&:=xY,\\
 t&:=y,\\
 x&=at.
 \end{aligned}
 \tag{18}
\]

Substitution followed by free reduction sends the relator to

\[
 t^{-1}a^{-1}ta^{-1}t^{-2}a^{-1}tat^{-1}at^2.
 \tag{19}
\]

Its $t$-exponent is zero.  With

\[
 a_i:=t^iat^{-i},
 \tag{20}
\]

the height scan, shifted upward by two, is

\[
 a_1^{-1}a_2^{-1}a_0^{-1}a_1a_0.
 \tag{21}
\]

Write again $a=a_0$, $b=a_1$, and $d=a_2$.  The Magnus base is

\[
 B_B=
 \left\langle a,b,d
 \mathrel{\big|}
 b^{-1}d^{-1}a^{-1}ba
 \right\rangle,
 \tag{22}
\]

and its one-occurrence relation gives

\[
 \boxed{
 \begin{aligned}
 d^{-1}&=ba^{-1}b^{-1}a,\\
 d&=a^{-1}bab^{-1}.
 \end{aligned}
 }
 \tag{23}
\]

Thus $B_B\cong F(a,b)$ and embeds in the ascending HNN extension with

\[
 \begin{aligned}
 tat^{-1}&=b,\\
 tbt^{-1}&=d=a^{-1}bab^{-1}.
 \end{aligned}
 \tag{24}
\]

The same Nielsen substitution reduces the defect to

\[
 t^{-1}at^{-1}a^{-1}tat^{-1}ata^{-1}t^2a^{-1}t^{-1}.
 \tag{25}
\]

Its shifted Magnus word is

\[
 ba^{-1}bab^{-1}a_3^{-1}.
 \tag{26}
\]

Let $\varphi:F(a,b)\hookrightarrow F(a,b)$ be the associated monomorphism
from (24), so $\varphi(a)=b$ and $\varphi(b)=d$.  Since
$a_3=tdt^{-1}=\varphi(d)$, equations (23)--(24) give

\[
 \begin{aligned}
 a_3^{-1}
 &=\varphi(d^{-1})\\
 &=db^{-1}d^{-1}b\\
 &=a^{-1}bab^{-1}a^{-1}b^{-1}ab.
 \end{aligned}
 \tag{27}
\]

Substitution in (26) produces the base word

\[
 ba^{-1}bab^{-1}a^{-1}bab^{-1}a^{-1}b^{-1}ab.
 \tag{28}
\]

It is freely reduced and nonempty.  Base injectivity therefore proves

\[
 \boxed{
 \begin{aligned}
 \overline K&\ne1\text{ in }Q_B,\\
 \mathsf G_B&\text{ is false}.
 \end{aligned}
 }
 \tag{29}
\]

This closes only the S2 sequential completion.  Together with (17), it
shows that neither verified first-leg donor branch can be completed while
holding its new row and $v$ as the two donor families.

Sections 6.2--6.4 construct two finite symbolic lift endpoints and then
disprove both strategies which restore the active base row first.  The
remaining MMS02 gate is an interleaved Peiffer/basic-substitution closure;
it is not another quotient-reachability problem.

## 6. Quotient reachability is automatic with one redundant row

The unrestricted bridge cannot be disproved by extending the fixed-base
$A_5$ or Alexander tests to another quotient of the same deficiency-one
group.  The reason is a general redundant-row transfer lemma.

Write $\operatorname{Ncl}_G(S)$ for the normal closure of a subset $S$ in
$G$.

**Lemma 6.1 (one-row normal-generator transfer).**  Let $G$ be any group,
and let $g,h\in G$ satisfy

\[
 \operatorname{Ncl}_G(g)
 =G
 =\operatorname{Ncl}_G(h).
 \tag{30}
\]

Then the redundant pairs are Andrews--Curtis equivalent in $G$:

\[
 \boxed{(1,g)\sim_{\rm AC}(1,h).}
 \tag{31}
\]

Here an elementary macro may multiply one entry by a conjugate of another
entry or its inverse.  Such a macro is a finite AC1--AC3 sequence: conjugate
the source, multiply it into the target, and restore the source, with two
source inversions when the negative sign is used.

**Proof.**  Choose finite normal-closure factorizations of $h$ and
$g^{-1}$ by conjugates of $g^{\pm1}$ and $h^{\pm1}$, respectively.  Build
$h$ in the identity entry from the $g$-entry, then append the chosen
factorization of $g^{-1}$ to the second entry:

\[
 (1,g)
 \sim(h,g)
 \sim(h,1)
 \sim(1,h).
 \tag{32}
\]

The last arrow swaps the two entries.  A swap is the standard six-step
sequence multiply--invert--multiply--invert--multiply--invert.  Thus every
arrow expands into AC1--AC3 moves.  $\square$

Apply the lemma to

\[
 \begin{aligned}
 F&=F(x,y,z),\\
 N&=\operatorname{Ncl}_F(A,B),\\
 G_-&=F/N.
 \end{aligned}
 \tag{33}
\]

Let $\overline u$ and $\overline v$ be the images of $u=zYX$ and
$v=Xyz$.  The verified trivialization of $(A,B,u)$ gives
$\operatorname{Ncl}_{G_-}(\overline u)=G_-$.  The published
reduction of $(A,B,v)$ to the AK(3) presentation, together with the
elementary fact that AK(3) presents the trivial group, gives the same
statement for $\overline v$.  It remains only to make that elementary
triviality fact literal.

For completeness, the last fact has a short normal-closure proof.  Write

\[
 \begin{aligned}
 R&=x^3y^{-4},\\
 S&=xyxYXY,\\
 \Delta&=xyx.
 \end{aligned}
\]

The two literal defects

\[
 \begin{aligned}
 \Delta x\Delta^{-1}y^{-1}&=S,\\
 \Delta y\Delta^{-1}x^{-1}&=xS^{-1}x^{-1}.
 \end{aligned}
 \tag{33a}
\]

show that conjugation by $\Delta$ exchanges $x$ and $y$ modulo
$\operatorname{Ncl}(S)$.  Thus $R=1$ and its $\Delta$-conjugate give

\[
 \begin{aligned}
 x^3&=y^4,\\
 y^3&=x^4.
 \end{aligned}
 \tag{33b}
\]

Consequently

\[
 \begin{aligned}
 x^9&=y^{12}=x^{16},\\
 y^9&=x^{12}=y^{16}.
 \end{aligned}
\]

so $x^7=y^7=1$.  Now
$y=y^8=(y^4)^2=x^6=x^{-1}$.  Substitution in the braid relation gives
$x=x^{-1}$, hence $x^2=1$.  The coprime relations $x^2=x^7=1$ force
$x=1$, and then $y=1$.  Every step is a product, inverse, conjugate, or
power of the two displayed relator defects, so it expands to a finite
normal-closure factorization.

The dependency-free verifier
`tests/stable_ac/test_ak3_normal_closure_certificate.py` expands every
factor as a conjugate of $R^{\pm1}$ or $S^{\pm1}$, checks every displayed
equality defect, and checks that the final left sides are literally $x,y$
while the right sides are empty.  All three focused checks pass.

Lemma 6.1 therefore proves

\[
 \boxed{
 \begin{aligned}
 (1,1,\overline u)
 &\sim_{\rm AC}(\overline v,1,\overline u)\\
 &\sim_{\rm AC}(\overline v,1,1)\\
 &\sim_{\rm AC}(1,1,\overline v)
 \text{ in }G_-.
 \end{aligned}
 }
 \tag{34}
\]

The same conclusion holds after every homomorphism out of $G_-$.  Hence no
AC invariant which factors only through the image triples in an $A_5$,
Alexander, metabelian, or other quotient of $G_-$ can obstruct the
unrestricted all-row bridge.  Those tests remain valid for fixed-base
ansatzes, where the first two entries are required to stay equal to one.

Equation (34) does not prove the free-group bridge.  It does sharpen the
lift gate.  Use the first identity row as the active buffer and lift the
two normal-closure factorizations in (32) to words of $F$.  The second base
row remains literally equal to $B$ throughout, and the lifted path has the
form

\[
 \begin{aligned}
 (A,B,u)&\sim_{\rm AC}(E_A,B,V_A),\\
 \rho_A:=E_AA^{-1}&\in N,\\
 \sigma_A:=V_Av^{-1}&\in N.
 \end{aligned}
 \tag{35a}
\]

Using the second identity row instead gives the symmetric branch

\[
 \begin{aligned}
 (A,B,u)&\sim_{\rm AC}(A,E_B,V_B),\\
 \rho_B:=E_BB^{-1}&\in N,\\
 \sigma_B:=V_Bv^{-1}&\in N.
 \end{aligned}
 \tag{35b}
\]

Thus one base row can stay literally fixed, and each branch has exactly two
$N$-valued lift residuals.  It need not end at the literal tuple
$(A,B,v)$.  The exact remaining gate is to choose one branch and its two
normal-closure factorizations so that its two residuals close by AC moves.
This is a relation-identity lift problem.  Quotient reachability itself is
complete, and further quotient hunting cannot evaluate that lift.

### 6.2. Finite symbolic lift to the two residual rows

The two factorizations used above can be made finite without printing an
enormous flattened product.  A conjugate-product straight-line expression
is generated by

\[
 \mathcal E::=r^{\pm1}\mid \mathcal E\mathcal E
 \mid \mathcal E^{-1}\mid q\mathcal E q^{-1},
 \tag{36}
\]

where every leaf $r$ is one named relator and every coefficient $q$ is a
literal word, itself allowed a finite straight-line spelling.  Its
evaluation is a finite word of $F$.  For a set $J$ of leaf names, let
$\pi_J\mathcal E$ delete every leaf outside $J$ while retaining the
ordered products, inverses, and literal conjugators.

**Lemma 6.2 (factorwise projection).**  For every finite expression
$\mathcal E$,

\[
 \operatorname{ev}(\mathcal E)
 \operatorname{ev}(\pi_J\mathcal E)^{-1}
 \in\operatorname{Ncl}_F\{r:r\notin J\}.
 \tag{37}
\]

**Proof.**  Induct on (36).  A retained leaf gives the identity and a
deleted leaf gives that leaf.  Products use the usual prefix conjugation,
while inverse and conjugate nodes preserve the indicated normal closure.
Every node therefore expands to a finite ordered product of conjugates.
$\square$

Track the complete 134-primitive-move replay of $(A,B,u)$ by expressions
$\mathcal E_1,\mathcal E_2,\mathcal E_3$ in the starting leaves
$A,B,u$.  Its literal terminal rows are $(Z,Y,X)$.  Hence

\[
 \operatorname{ev}(
 \mathcal E_3\mathcal E_2^{-1}\mathcal E_1^{-1})
 =Xyz=v.
 \tag{38}
\]

Put

\[
 H=\operatorname{ev}\left(
 \pi_{\{u\}}(
 \mathcal E_3\mathcal E_2^{-1}\mathcal E_1^{-1})\right).
 \tag{39}
\]

Then $H\in\operatorname{Ncl}_F(u)$ and Lemma 6.2 gives
$Hv^{-1}\in N$.

For the reverse normal-generation certificate, first use the literal
substitution defects

\[
 \begin{aligned}
 zXy&=zvz^{-1},\\
 ZYx&=v^{-1}.
 \end{aligned}
 \tag{40}
\]

The exact normalization of the two substituted rows followed by all
fifty-three published $h_i$ moves ends at the literal AK(3) relators
$R,S$.  Compose that replay with the verified finite $R,S$-factorizations
of $x$ and $y$.  Equation (40), including the identity

\[
 u^{-1}=xyZ=(xy)v^{-1}(xy)^{-1}xyXy,
 \tag{41}
\]

then gives one finite expression $\mathcal U$ in the leaves $A,B,v$ with
$\operatorname{ev}(\mathcal U)=u^{-1}$.  Define

\[
 K=\operatorname{ev}(\pi_{\{v\}}\mathcal U).
 \tag{42}
\]

Thus $K\in\operatorname{Ncl}_F(v)$ and
$u^{-1}K^{-1}\in N$.

For a conjugate-product expression for $K$, write $K[W]$ for the finite
expression obtained by replacing every $v^{\pm1}$ leaf by
$W^{\pm1}$ without changing its literal conjugators.  Set

\[
 \begin{aligned}
 H_A&=AH,&E_A&=uK[H_A],\\
 H_B&=BH,&E_B&=uK[H_B].
 \end{aligned}
 \tag{43}
\]

The build--kill--swap macros now give the literal AC paths

\[
 \begin{aligned}
 (A,B,u)&\sim_{\rm AC}(H_A,B,u)
 \sim_{\rm AC}(H_A,B,E_A)
 \sim_{\rm AC}(E_A,B,H_A),\\
 (A,B,u)&\sim_{\rm AC}(A,H_B,u)
 \sim_{\rm AC}(A,H_B,E_B)
 \sim_{\rm AC}(A,E_B,H_B).
 \end{aligned}
 \tag{44}
\]

Moreover, (39)--(42) imply

\[
 \boxed{
 \begin{aligned}
 E_A&\in N,&H_Av^{-1}&\in N,\\
 E_B&\in N,&H_Bv^{-1}&\in N.
 \end{aligned}
 }
 \tag{45}
\]

because $H_A,H_B$ both equal $v$ modulo $N$, so $K[H_A]$ and
$K[H_B]$ both equal $u^{-1}$ modulo $N$.  This identifies the abstract
endpoints in (35a)--(35b) by finite symbolic straight-line expressions and
evaluates their two residual categories.  The dependency-free checker
`tests/stable_ac/test_ak3_mms02_relation_lift_certificate.py` replays every
primitive and published move, verifies the exact defects in (40), composes
the AK(3) normal-closure certificates, checks both factorwise projections,
validates the structural substitution nodes, and enforces a finite DAG-node
budget.  Together with the AK(3) normal-closure checker, all four focused
tests pass.  The checker does not flatten $K[H_A],K[H_B]$ or replay their
donor-restoring AC macros; their finite expansions follow from the induction
in Lemma 6.2 and the standard conjugate-donor macro used in Lemma 6.1.

Equation (45) is not the bridge.  It does not provide AC moves changing
$(E_A,B,H_A)$ or $(A,E_B,H_B)$ to $(A,B,v)$.  The remaining gate is the
Peiffer/basic-substitution closure of one displayed pair of $N$-valued
residuals.

### 6.3. One residual restoration is enough

The two-residual endpoint does not require two independent closing
memberships.  For the first branch, consider

\[
 \mathsf C_A:
 E_AA^{-1}\in\operatorname{Ncl}_F(B,H_A).
 \tag{46a}
\]

If $\mathsf C_A$ holds, the basic substitution principle first replaces
$E_A$ by $A$ while preserving $B,H_A$.  Equation (45) then replaces
$H_A$ by $v$ using $A,B$.  Therefore

\[
 \mathsf C_A\Longrightarrow
 (E_A,B,H_A)\sim_{\rm AC}(A,B,H_A)
 \sim_{\rm AC}(A,B,v).
 \tag{46b}
\]

The symmetric sufficient gate is

\[
 \mathsf C_B:
 E_BB^{-1}\in\operatorname{Ncl}_F(A,H_B).
 \tag{46c}
\]

and gives $(A,E_B,H_B)\sim_{\rm AC}(A,B,v)$.

Both gates have the same defect word.  Indeed, quotienting the first gate
by $B,H_A$ sets $H_A=AH=1$.  Hence $A^{-1}=H$, while
$K[H_A]=K[1]=1$ and $E_A=u$.  The second branch is identical with
$A,B$ exchanged.  Consequently

\[
 \boxed{
 \begin{aligned}
 \mathsf C_A
 &\Longleftrightarrow
 d=1\text{ in }Q_A^{\rm cl}
 :=\langle x,y,z\mid B,AH\rangle,\\
 \mathsf C_B
 &\Longleftrightarrow
 d=1\text{ in }Q_B^{\rm cl}
 :=\langle x,y,z\mid A,BH\rangle,\\
 d&:=uH.
 \end{aligned}
 }
 \tag{47}
\]

The projected expression gives a freely reduced $H$ of length $337$ and
a freely reduced $d$ of length $340$.  Its exponent vector is zero.  Thus
each closing gate is now one exact deficiency-one word problem.  A
normal-closure factorization for either occurrence of $d$ proves the
MMS02 bridge and hence stable AK(3); nontriviality closes only that branch.

### 6.4. Both restoration gates fail in the Alexander relation module

The two word problems in (47) have canonical epimorphisms to the infinite
cyclic group.  Their generator weights are

\[
 \begin{aligned}
 \phi_A(x),\phi_A(y),\phi_A(z)&=(2,2,3),\\
 \phi_B(x),\phi_B(y),\phi_B(z)&=(2,1,2).
 \end{aligned}
 \tag{48}
\]

Let $\Lambda=\mathbb Z[t,t^{-1}]$.  Abelianize the Fox derivatives using
the appropriate weight in (48).  If a word $w$ lies in the normal closure
of two relators $r_1,r_2$, then

\[
 \partial_\phi w
 \in\Lambda\partial_\phi r_1+\Lambda\partial_\phi r_2.
 \tag{49}
\]

Indeed, a conjugate $q r_i^\epsilon q^{-1}$ contributes
$\epsilon t^{\phi(q)}\partial_\phi r_i$.  Thus failure of the row-span
condition proves nonmembership in the free group.

Use the $x,y$ columns of the two Fox rows.  Their determinant $D_A$ for
$Q_A^{\rm cl}$ is nonzero and has Laurent span $21$.  The Cramer numerator
$N_{A,\alpha}$ for the defect row is nonzero and has span $19$.  A nonzero
Laurent multiple of $D_A$ cannot have smaller span.  Hence $D_A$ does not
divide $N_{A,\alpha}$ in $\Lambda$.

For $Q_B^{\rm cl}$, exact Laurent long division in the same two columns
leaves the remainder

\[
 \begin{aligned}
 R_B={}&8t^{-14}+3t^{-13}-12t^{-12}-3t^{-11}
 +12t^{-10}+2t^{-9}\\
 &+9t^{-8}+4t^{-7}-7t^{-6}+17t^{-5}+13t^{-4}.
 \end{aligned}
 \tag{50}
\]

It is nonzero, so its Cramer numerator is not divisible by $D_B$.  Equation
(49) proves

\[
 \boxed{\mathsf C_A\text{ is false and }\mathsf C_B\text{ is false}.}
 \tag{51}
\]

The focused checker
`tests/stable_ac/test_ak3_mms02_residual_alexander_gates.py` derives $H$
from the primitive transcript, verifies the weighted Fox fundamental
identity for all five rows, performs both exact divisions, checks the
Cramer reconstruction identities, and pins the nonzero remainder (50).

Equation (51) closes only the strategy which restores the active base row
first and then cleans the kill row.  An unrestricted closure may interleave
both residual rows, and the MMS02 bridge remains open.

### 6.5. The sequential cleanup ledger is exhausted

For completeness, name the two gates in the opposite cleanup order:

\[
 \begin{aligned}
 \mathsf K_{A,1}:&\ H_Av^{-1}\in\operatorname{Ncl}_F(E_A,B),&
 \mathsf K_{A,2}:&\ E_AA^{-1}\in\operatorname{Ncl}_F(B,v),\\
 \mathsf K_{B,1}:&\ H_Bv^{-1}\in\operatorname{Ncl}_F(A,E_B),&
 \mathsf K_{B,2}:&\ E_BB^{-1}\in\operatorname{Ncl}_F(A,v).
 \end{aligned}
 \tag{52}
\]

The A-active kill-first order needs both $\mathsf K_{A,1}$ and
$\mathsf K_{A,2}$.  Exact SLP Fox evaluation gives

\[
 \begin{aligned}
 \mathsf K_{A,1}&\text{ is false},\\
 \mathsf K_{A,2}&\text{ passes the Alexander row-span test}.
 \end{aligned}
 \tag{53}
\]

The first verdict uses cyclic weights $(1,1,1)$ and the nonzero Cramer
remainder

\[
 R_{A,1}=t^2-5+14t^{-1}-9t^{-2}-2t^{-3}
 +7t^{-4}-4t^{-5}+t^{-6}.
 \tag{54}
\]

Thus the A-active kill-first order is impossible; the pass in (53) is only
a necessary-filter pass and is not a membership claim.

For the B-active kill-first order, it is enough to test the second gate.
With cyclic weights $(1,0,1)$, its $x,y$ minor is $2-t$ and exact division
leaves

\[
 R_{B,2}=-3664388358890479647198t^{-33}.
 \tag{55}
\]

Hence $\mathsf K_{B,2}$ is false, independently of the unevaluated
$\mathsf K_{B,1}$.

There are now no further sequential cleanup orders.  In either active
branch, a completion which restores each residual row once and never alters
it again must restore the base row first or the kill row first.  Equations
(51), (53), and (55) close both choices in both branches.  The exact bounded
conclusion is

\[
 \boxed{\text{Every two-substitution sequential completion of the two
 residual endpoints is impossible.}}
 \tag{56}
\]

The checker `tests/stable_ac/test_ak3_mms02_kill_first_alexander.py`
evaluates the endpoint SLP directly, without expanding $K$, and pins the
two nonzero remainders.  Equation (56) does not obstruct a completion which
alters the two residual rows repeatedly or interleaves their Peiffer
transformations.  That genuinely interleaved relation-identity problem is
the sole remaining MMS02 closure category.

### 6.6. A common-kill normalization of the unrestricted bridge

There is a second exact normalization which does not enlarge the sequential
cleanup ledger.  Let $\phi\in\operatorname{Aut}(F)$ be the signed
permutation

\[
 \begin{aligned}
 \phi(x)&=Z,&\phi(y)&=Y,&\phi(z)&=X.
 \end{aligned}
 \tag{57}
\]

It is an involution and sends the two kill words to one another:

\[
 \begin{aligned}
 \phi(u)&=v,&\phi(v)&=u.
 \end{aligned}
 \tag{58}
\]

Its base-row images are the literal words

```text
phi(A) = ZXyzYZxzyZYx
phi(B) = zYZxzyzYZXzyZY
```

Apply $\phi$ to every row and every conjugator in the certified
134-primitive path

\[
 (A,B,u)\sim_{\rm AC}(Z,Y,X).
 \tag{59}
\]

Since $\phi(Z)=x$, $\phi(Y)=y$, and $\phi(X)=z$, this gives the literal
classical path

\[
 \boxed{(\phi(A),\phi(B),v)\sim_{\rm AC}(x,y,z).}
 \tag{60}
\]

Both $(A,B,u)$ and $(\phi(A),\phi(B),v)$ are therefore classically
AC-equivalent to the standard basis.  Consequently the unrestricted bridge
has the equivalent common-third-row formulation

\[
 \boxed{
 (A,B,v)\sim_{\rm AC}(A,B,u)
 \Longleftrightarrow
 (A,B,v)\sim_{\rm AC}(\phi(A),\phi(B),v).}
 \tag{61}
\]

Equation (61) is a target normalization, not a fixed-$v$ theorem: an
intermediate path may alter all three rows.  It neither repairs any failed
sequential gate in Sections 6.3--6.5 nor proves the bridge.  It does isolate
an alternative unrestricted target whose kill row is already the literal
published word $v$.

## 7. Stable-AK(3) implication and strict nonclaims

The verified MMS02 corridor gives a stable equivalence between
$T_{\rm pub}$ and AK(3), while the triple $(A,B,zYX)$ is independently
AC-trivial at rank three.  Hence (7) would prove stable AK(3).

The logical gates remain separate:

1. $\mathsf G_A$ and $\mathsf G_B$ are both disproved;
2. their nontriviality refutes only the two sequential donor completions,
   not the unrestricted all-row bridge;
3. the fixed-base $A_5$ and Alexander obstructions do not apply to a path
   which moves $A$ and $B$;
4. Lemma 6.1 closes quotient reachability and Section 6.2 gives two finite
   symbolic residual endpoints, but neither result closes the residuals;
5. the finite cleanup ledger closes every completion which restores each
   residual exactly once, but not an interleaved Peiffer closure which may
   alter the rows repeatedly;
6. no MMS02 statement evaluates the period-two class-two ledger or its
   literal higher lift; and
7. stable AK(3), ordinary AK(3), stable Andrews--Curtis, and
   Andrews--Curtis are not claimed.

The active priority is now the unrestricted stable bridge
$T_{\rm pub}\sim_{\rm AC}(A,B,zYX)$ with all rows allowed to move.
