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

Sections 6.6--6.8 give an equivalent common-kill target and close both its
ambient-automorphism-only and one-projected-multiplication subcases.  This
does not add another sequential cleanup category: within this low-depth
common-kill mechanism, a successful path must use at least two base-row
multiplications visible after projection or alter the kill row.

Section 6.9 independently proves that the exact word-realized presentation
complex of $T_{\rm pub}$ is not thickenable.  This closes the direct
thickenability route for this one complex only.  Thickenability is not known
to be invariant under Andrews--Curtis moves, so the unrestricted bridge and
stable AK(3) remain open.

Section 6.10 closes and freezes the next finite thickenability class: none
of the four tail-free boundary-cancelling moves by a cyclic conjugate of
$v^{\pm1}$ produces a thickenable complex.  Arbitrary surviving conjugator
tails and multi-move paths remain outside that theorem.

Section 6.11 gives a separate stable reduction.  One fresh tagged row lets
the certified $A$-branch run while retaining $rt$; the same two-factor
$B$-donor macro applied to $rt$ then reaches $B_t$.  Each direct sequential
cleanup order fails at its first substitution.  The remaining sufficient
object at this endpoint is one named interleaved relative Peiffer class, not
another sequential ledger.

Section 6.12 proves that the normalized source and target of that relative
class are literally identical in every nilpotent quotient.  This evaluates
all lower-central shadows at once but does not supply a literal Peiffer lift.

Section 6.13 executes the first legal no-self-donor interchange.  It proves
that the middle first-row cleanup and the final second-row cleanup are
impossible at their respective checkpoints.  This closes one interchange
mechanism, not unrestricted interleaving.

Section 6.14 evaluates the first nonnilpotent layer.  The Gate-A metabelian
module is $\mathbb Z[1/2]$, where the discrepancy survives but conjugates
$q$ exactly to $B$.  The complete tagged pair is therefore AC-equivalent in
the universal quotient obtained by metabelianizing the Gate-A factor.

Section 6.15 proves that this canonical quotient conjugator does not lift
unchanged to the Gate-A group.  Its exact defect is a nontrivial element of
$Q_A''$, detected by one Britton pinch test.  Other conjugators, Peiffer
corrections, and full relative paths remain open.

Section 6.16 evaluates the entire $Q_A''$-correction coset of that canonical
conjugator.  A second-derived direct limit turns the correction equation into
one Laurent Mahler equation, whose coefficients at four named degrees are
inconsistent.  This closes that correction coset only; other metabelian
conjugators and full relative paths remain open.

Section 6.17 classifies those other metabelian conjugators.  The centralizer
of $q$ in $Q_A/Q_A''$ is exactly $\langle q\rangle$, and its powers commute
with $q$ already in $Q_A$.  Thus every possible literal conjugator has the
same correction equation from Section 6.16.  The words $q$ and $B$ are not
conjugate in $Q_A$, but multi-row relative paths remain open.

Section 6.18 removes the coefficient $r$ from the tagged source exactly.
Modulo $q$ and $v$, both $A$ and $r$ reduce to $x$, so $r$ is already in
the normal closure of the three fixed/current donor rows.  The remaining
relative problem is precisely the tagged normal-generator gate
$(q,t)\to(B,t)$ in $Q_A*\langle t\rangle$.

Section 6.19 identifies the first derived defect module for that gate.  The
kernel created by restoring $Q_A''$ is a free product of its conjugates with
no extra Kurosh free factor, so its abelianization is the induced module from
$L=Q_A''/Q_A'''$.  The canonical quotient path has residual $([E],0)$ in
the identity-coset summand.  Arbitrary tame lifts of quotient AC loops,
including transformations which project to the identity loop, may still
move or cancel that residual.

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

### 6.7. The ambient-automorphism-only common-kill route is closed

Use the free basis $(x,y,v)$ of $F$.  The quotient which kills $v$ is the
retraction

\[
 \begin{aligned}
 \pi_v:F(x,y,z)&\longrightarrow F(x,y),&
 \pi_v(z)&=Yx.
 \end{aligned}
 \tag{62}
\]

The two unordered pairs of conjugacy classes at the endpoints of (61) are
represented by

```text
P       = (xYxYXyyXYxyXy, XyyXYXyxYYxy)
P_phi   = (XXyxYxy, YxYXyxYxxYXyXYxyX)
```

Run exact Whitehead descent on each pair, quotienting only independent
cyclic conjugation, inversion, and row order.  There are twelve nonidentity
second-kind Whitehead automorphisms in rank two.  The complete strict
descents terminate at

```text
min(P)     = (XXYYXyxYxy, XYXYXyxYxyy), total 21
min(P_phi) = (XXYxY, XXYxyXYYYXyxxY), total 19
```

At each displayed endpoint, all twelve second-kind automorphisms have
nondecreasing total cyclic length.  Whitehead's theorem therefore makes
21 and 19 the exact orbit minima.  In particular,

\[
 \boxed{[P]_{\operatorname{Aut}(F_2)}\neq
 [P_\phi]_{\operatorname{Aut}(F_2)}.}
 \tag{63}
\]

This has one precise bridge consequence.  Any ambient automorphism of the
free factor $F(x,y)$ extends to $F(x,y,v)$ while fixing $v$.  More
generally, an automorphism $\theta$ satisfying
$\theta(\operatorname{Ncl}(v))=\operatorname{Ncl}(v)$ descends to an
automorphism of $F/\operatorname{Ncl}(v)$: the maps induced by $\theta$ and
$\theta^{-1}$ are mutual inverses.  Independent base-row conjugations,
inversions, and permutations do not change the unordered conjugacy-class
pair, while cleanup by conjugates of $v$ disappears under $\pi_v$.
Equation (63) therefore rules out a common-kill bridge consisting only of
such a stable ambient automorphism, base-row normalizations, and $v$-donor
cleanup.

It does not rule out (61).  A successful common-kill path may use a genuine
AC multiplication between its two live base rows, or an unrestricted path
may alter the $v$-row.  Those are exactly outside the Aut-orbit comparison.
The focused checker enumerates all twelve Whitehead maps, replays both
strict descents, and verifies the no-descent condition at both minima.

### 6.8. One projected base-row multiplication is still insufficient

Write $P=(p_0,p_1)$ and $P_\phi=(q_0,q_1)$ for the pairs in Section
6.7.  Up to independent row conjugation and inversion, one multiplication
changing row $i$ has the form

\[
 \begin{aligned}
 p_i^\alpha g p_j^\beta g^{-1},&p_j,\\
 \{i,j\}=\{0,1\},&\alpha,\beta\in\{1,-1\}.
 \end{aligned}
 \tag{64}
\]

The relative conjugator $g\in F_2$ is arbitrary.  It disappears from
abelianization and does not change the untouched row $p_j$.

Using rows for exponent vectors, the source and target matrices are

\[
 \begin{aligned}
 S&=\begin{pmatrix}0&1\\-1&1\end{pmatrix},&
 T&=\begin{pmatrix}0&1\\1&-2\end{pmatrix}.
 \end{aligned}
 \tag{65}
\]

Choose the changed row, the signs $\alpha,\beta$, the assignment of the
two target rows, and their two orientations.  This gives exactly
$2\mathbin\cdot4\mathbin\cdot2\mathbin\cdot4=64$ oriented cases and 32
distinct required ambient matrices

\[
 M=C^{-1}T',
 \tag{66}
\]

where $C$ is the exponent matrix after (64) and $T'$ is the oriented,
assigned target matrix.  Every $M$ is unimodular.  The kernel of
$\operatorname{Aut}(F_2)\longrightarrow\operatorname{GL}_2(\mathbb Z)$
is the inner automorphism group.  Therefore, for fixed $M$, the cyclic
conjugacy class of the image of the untouched row is independent of the
chosen automorphism lifting $M$.

Exact Nielsen decompositions of all 32 matrices give the following complete
cyclic-length table.  The second column records which target row is assigned
to the untouched source slot.

| changed source | assigned target | possible untouched-image lengths | target length |
|---|---:|---:|---:|
| $p_0$ | $q_0$ | $11,13,15,17$ | $7$ |
| $p_0$ | $q_1$ | $13,15,19$ | $17$ |
| $p_1$ | $q_0$ | $11,13,15,17$ | $7$ |
| $p_1$ | $q_1$ | $11,15,19$ | $17$ |

No row has matching cyclic length.  Hence the untouched row cannot be
conjugate to either orientation of its assigned target row in any of the 64
cases.  This contradiction is independent of $g$.

Simultaneous ambient automorphisms commute past the unique multiplication
after replacing $g$ by its image, so all such automorphisms may be composed
and placed after (64).  Independent row normalizations are already absorbed
by the signs, target assignments, and cyclic classes above.  Steps using
the $v$-row only as a donor disappear after $\pi_v$.  We have therefore
proved the exact bounded mechanism theorem

\[
 \boxed{
 \begin{gathered}
 \text{No common-kill path with exactly one quotient-visible base-row}\
 \text{multiplication, ambient automorphisms preserving }
 \operatorname{Ncl}(v),\
 \text{base-row normalizations, and }v\text{-donor cleanup closes (61).}
 \end{gathered}}
 \tag{67}
\]

The conjugator in that one multiplication is unrestricted.  Equation (67)
does not exclude a path with two or more quotient-visible base-row
multiplications, a path which alters the $v$-row by a base-row donor, an
ambient map which does not preserve $\operatorname{Ncl}(v)$, or a more
general stable path retaining an auxiliary stabilization row.  The
common-kill low-depth ledger stops here; increasing the multiplication count
would create another bounded category rather than evaluate the open
interleaved Peiffer problem.

### 6.9. The exact published complex is not thickenable

Apply the harmless generator renaming $y\mapsto z$, $z\mapsto t$ so that the
six germs have the solver labels $x,X,z,Z,t,T$.  The three exact cyclic words
become

```text
xtZXzxTXZxzT
XzxTXZXzxtXZxz
Xzt
```

No free or cyclic reduction is made.  Reading the 29 cyclic corners gives
the following complete parallel-class table in the original germ labels.

| support edge | multiplicity |
|---|---:|
| $Xz$ | 4 |
| $ZY$ | 2 |
| $yX$ | 4 |
| $xy$ | 6 |
| $Yx$ | 6 |
| $XZ$ | 4 |
| $zx$ | 1 |
| $YX$ | 1 |
| $Yz$ | 1 |

The underlying simple graph is obtained from a $K_4$ on
$\{X,Y,x,z\}$ by subdividing the edge $Xx$ with $y$ and adjoining a second
$X$--$Y$ path subdivided by $Z$.  Fixing the least neighbour first at every
vertex leaves

\[
 (4-1)!(4-1)!(3-1)!(3-1)!=144
 \tag{68}
\]

macro rotation systems.  Direct face tracing finds exactly four spherical
systems.  They are the two choices for the side of the $X$--$Y$ edge which
contains the $X$--$Z$--$Y$ ear, together with their global reflections.

The parallel expansion has no hidden rotations.  For every support edge
$ab$ except $XY$, deleting $a,b$ leaves the simple support connected.  The
class-block argument of `AK3_RANK3_RIGID_THICKENABILITY.md`, Theorem 3.1,
therefore forces every repeated $ab$-class to be one cyclic interval at
both endpoints, with reversed linear orders.  Deleting $X,Y$ disconnects
the support, but the $XY$ class has multiplicity one, so its block and order
conditions are vacuous.  Thus expanding the four macro rotations by
all-different class ranks gives every spherical rotation of the exact
multigraph.

The proof of the three-pipe signed-rank criterion in
`AK3_RANK3_RIGID_THICKENABILITY.md`, Theorem 4.1, uses the rigid support only
to supply this complete finite list of injective slot schemes.  Its phase
lemma and constraint-cycle propagation therefore apply unchanged to the
four schemes just obtained.

Run the three-pipe phase equations on all four slot schemes.  The exact
positive-germ degrees are $13,10,6$, so there are 780 phase triples per
scheme.  The exact exhaustion is

\[
 \begin{array}{c|r}
 \text{macro schemes}&4\\
 \text{scheme--phase pairs}&3{,}120\\
 \text{component seeds}&18{,}720\\
 \text{closed component assignments}&96\\
 \text{complete cross-relator combinations}&0.
 \end{array}
 \tag{69}
\]

The scheme, phase, and seed budgets are reached exactly.  Although 96
individual constraint-cycle assignments close, no scheme--phase pair closes
all three relator cycles, so no global rank partition and no compatible
spherical rotation survives.

**Theorem 6.3 (exact-complex thickenability boundary).**  The canonical
word-realized presentation complex of
$T_{\rm pub}=(A,B,Xyz)$ is not thickenable.

**Proof.**  The link is connected.  The block argument above and the
144-state macro enumeration prove that the four schemes in (69) cover every
spherical rotation.  The signed-rank criterion is necessary and sufficient
inside each scheme, and the exhaustive search finds none compatible with
the generator-end reversal.  The Euler-only Neuwirth criterion therefore
rules out an orientable PL thickening.  The presented group is trivial by
the published Tietze reduction and the literal normal-closure proof
(33a)--(33b), so a regular neighbourhood cannot be nonorientable: its
orientation character would give a nontrivial homomorphism of its
fundamental group to $\mathbb Z/2$.  Hence no PL thickening exists.
$\square$

The focused certificate independently reconstructs the corner table,
enumerates the 144 macro systems and four spherical survivors, and checks
the signed-rank budgets.  It also replays the generalized rank solver on an
affordable 17,280-order factorial fixture.  The implementation is

```text
experiments/stable_ac/thickenable/mms02_tpub_neuwirth_certificate.py
```

with focused checks in

```text
tests/stable_ac/test_mms02_tpub_neuwirth_certificate.py
```

Theorem 6.3 is not an obstruction to the unrestricted bridge.  The
Neuwirth potential and exact-complex thickenability are not Andrews--Curtis
invariants in this argument.  A later AC-equivalent representative may be
thickenable.  Thus Theorem 6.3 neither proves nor disproves the bridge,
stable AK(3), ordinary AK(3), stable Andrews--Curtis, or Andrews--Curtis.

### 6.10. Tail-free boundary donor moves are also nonthickenable

Let $\operatorname{cyc}(w)$ denote the freely and cyclically reduced word
representing $w$, and let

\[
 \mathcal C_v=\{Xyz,yzX,zXy,ZYx,YxZ,xZY\}
 \tag{70}
\]

be the cyclic shifts of $v$ and $v^{-1}$.  Define the pinned-seam class
$\mathcal P_\partial$ as follows.  Choose $R=A$ or $R=B$, replace that row
by $Rc$ for one $c\in\mathcal C_v$, and retain the result exactly when

\[
 |\operatorname{cyc}(Rc)|<|R|+3.
 \tag{71}
\]

Each replacement is one AC multiplication by a conjugate of the third row,
followed only by row conjugation and literal free equality.  The definition
is deliberately narrow: no letters of an arbitrary conjugator may survive
outside the three donor letters.

Inspecting the two cyclic seams gives exactly four outputs.

| changed row | cyclic donor | exact reduced row |
|---|---|---|
| $A$ | `yzX` | `zYXyxZXYxyZyz` |
| $A$ | `zXy` | `xzYXyxZXYxyXy` |
| $B$ | `ZYx` | `xZXYXyxzXYxyZ` |
| $B$ | `YxZ` | `XyxZXYXyxzXYxxZ` |

The other eight products have cyclic length $|R|+3$ and are outside
$\mathcal P_\partial$.  The four displayed words are the exact inputs to
the occurrence dictionaries below; no further reduction or occurrence
identification is made.

Three of the four supports have the same rigidity property used in Section
6.9: deleting the endpoints of every repeated support class leaves the
simple support connected.  Their repeated classes are therefore reversed
blocks, and normalized face tracing supplies every spherical macro scheme.

For the row `xzYXyxZXYxyXy`, the doubled $XY$ class is the unique exception.
Deleting $X,Y$ leaves three components: the edge $xy$ and the two isolated
vertices $z,Z$.  Keep both $XY$ slots while collapsing every other repeated
class to one block.  At $X$ and $Y$ the two neighbour multisets each have
$12=(5-1)!/2!$ cyclic orders.  The other four vertices have one order each,
and the two $XY$ slots have two endpoint pairings.  Thus

\[
 12\mathbin\cdot12\mathbin\cdot2=288
 \tag{72}
\]

partial-expansion schemes exhaust the nonblock case.  Exact face tracing
retains twelve spherical schemes.

The complete signed-rank results are:

| changed row and donor | support-rotation budget | spherical schemes | scheme--phase pairs | component seeds | closed component assignments | complete combinations |
|---|---:|---:|---:|---:|---:|---:|
| $A$, `yzX` | 864 | 2 | 1,848 | 11,088 | 96 | 0 |
| $A$, `zXy` | 288 | 12 | 9,240 | 120,120 | 338 | 0 |
| $B$, `ZYx` | 16 | 2 | 1,512 | 12,096 | 40 | 0 |
| $B$, `YxZ` | 144 | 4 | 3,528 | 38,808 | 120 | 0 |

Every scheme, phase, and seed budget is reached.  In each row, some
individual relator-cycle assignments close, but no scheme--phase pair closes
all three cycles.  Hence no global rank partition survives.

**Theorem 6.4 (pinned-seam donor boundary).**  Every exact presentation
complex in $\mathcal P_\partial$ is nonthickenable.

**Proof.**  The three rigid cases are complete by the connected-deletion
block argument.  Equation (72) is complete for the sole nonblock class, so
the retained twelve schemes cover every spherical rotation there.  The
three-pipe signed-rank criterion is necessary and sufficient on each listed
scheme, and the exhaustive table has no compatible survivor.  Each
presentation is AC-equivalent to $T_{\rm pub}$ and hence presents the trivial
group.  The Euler-only Neuwirth criterion and the orientation-character
argument from Theorem 6.3 rule out all PL thickenings. $\square$

The exact finite certificate and focused replay are

```text
experiments/stable_ac/thickenable/mms02_tpub_boundary_donor_certificate.py
tests/stable_ac/test_mms02_tpub_boundary_donor_certificate.py
```

The class $\mathcal P_\partial$ is now frozen.  Its negative verdict does
not cover a donor conjugate with a surviving tail, an unshortened cyclic
donor product, a base-row multiplication, two or more moves, or a retained
stabilization row.  Exact-complex thickenability is still not an AC
invariant.  Theorem 6.4 therefore does not obstruct the unrestricted bridge
and proves none of stable AK(3), ordinary AK(3), stable Andrews--Curtis, or
Andrews--Curtis.

### 6.11. One tagged stabilization isolates the interleaved gate

Write ${}^g w=gwg^{-1}$ and use the commutator convention
$[a,b]=aba^{-1}b^{-1}$.  The pinned words satisfy the literal identities

\[
 \begin{aligned}
 rC&=x,&qu&=vh,\\
 C&=({}^xq)({}^{x^2}q^{-1})({}^{x^2}v)({}^xq^{-1}),\\
 K^{-1}&=C({}^uC^{-1}),&
 D^{-1}&=({}^hr)({}^{hX}r^{-1}).
 \end{aligned}
 \tag{73}
\]

The last line is the factorwise form of the two certified donor branches.
Introduce a fresh stabilization generator and row $t$, write
$F_t=F(x,y,z,t)$, and put

\[
 \begin{aligned}
 s&=rt,&D(w)&={}^h[X,w],&B_t&=qD(rt)^{-1}.
 \end{aligned}
 \tag{74}
\]

There is a literal finite path

\[
 (r,q,v,t)
 \sim_{\mathrm{AC}}(r,q,v,rt)
 \sim_{\mathrm{AC}}(A,q,v,rt)
 \sim_{\mathrm{AC}}(A,B_t,v,rt).
 \tag{75}
\]

For the first arrow, conjugate the $r$-row by $t^{-1}$, multiply it into
the $t$-row, and restore the $r$-row.  The second arrow is the certified
$A$-branch and leaves the tagged row literal.  The final arrow uses

\[
 D(rt)^{-1}=({}^h(rt))({}^{hX}(rt)^{-1}),
 \tag{76}
\]

so it uses only the current $rt$-row as donor.

The commutator interchange identity

\[
 [X,rt]=[X,r]({}^r[X,t])
 \tag{77}
\]

gives

\[
 \begin{aligned}
 D(rt)&=D({}^{hr}[X,t]),\\
 B_t&=L_tB,&L_t&={}^{qhr}[X,t]^{-1}.
 \end{aligned}
 \tag{78}
\]

Thus (75) has exactly two visible cleanup residuals: $L_t$ in the second
row and $r$ in the fourth row.  Both direct first cleanup substitutions are
false.

First clean $B_t$.  Replacing it by $B$ while the other three rows remain
fixed would require

\[
 \mathsf T_B:
 L_t\in\operatorname{Ncl}_{F_t}(A,v,rt).
 \tag{79}
\]

In the quotient on the right, $rt=1$ gives $t=r^{-1}$.  Since conjugation
and inversion do not affect triviality, (79) would force
$[X,r^{-1}]=1$, equivalently $[X,r]=1$, in

\[
 Q_A=\langle x,y,z\mid A,v\rangle.
\]

Section 4 proves that $D=h[X,r]h^{-1}$ is nontrivial in this quotient.
Therefore $\mathsf T_B$ is false.

Now restore the tagged row first.  Replacing $rt$ by $t$ while
$A,B_t,v$ remain fixed would require

\[
 \mathsf T_t:
 r\in\operatorname{Ncl}_{F_t}(A,B_t,v).
 \tag{80}
\]

Kill $v$ and use the Section 4 Magnus group
$Q_A=\langle x,y\mid\overline A\rangle$.  Equation $B_t=1$ is equivalent
to

\[
 \begin{aligned}
 [X,t]&={}^{g^{-1}}B,&g&=qhr=X^2r.
 \end{aligned}
 \tag{81}
\]

Because $[X,t]=Xtxt^{-1}$, this is the HNN relation

\[
 \begin{aligned}
 t x t^{-1}&=w,\\
 w&=x({}^{g^{-1}}B)=r^{-1}x^2yx^{-2}r.
 \end{aligned}
 \tag{82}
\]

The last word is conjugate to $y$.  In the Magnus decomposition of Section
4, $x$ is the stable letter and $y=a$ lies in the embedded free base, so
both $\langle x\rangle$ and $\langle w\rangle$ are infinite cyclic.
Britton's lemma embeds $Q_A$ in the HNN extension (82).  Moreover $r$ is
nontrivial in $Q_A$, since $[X,r]$ is nontrivial there.  Hence $r$ remains
nontrivial after imposing $B_t=1$, and $\mathsf T_t$ is false.

**Theorem 6.5 (tagged stable reduction).**  The canonical one-tag path
reaches the relative Peiffer problem

\[
 (A,B_t,v,rt)\longrightarrow(A,B,v,t),
 \tag{83}
\]

whose positive closure is sufficient for the stable bridge.  Neither
of the two direct sequential basic-substitution orders from the displayed
endpoint can begin: each fails at its first substitution.

The common tempting shortcut is invalid.  The identities
$q=B_tD(rt)$ and $K\in\operatorname{Ncl}(q,v)$ show only

\[
 r=AK\in\operatorname{Ncl}(A,B_t,v,rt),
 \tag{84}
\]

which uses the $rt$-row while trying to replace that same row.  It is not a
basic substitution.  The remaining sufficient object at this canonical
endpoint is the genuinely interleaved relative Peiffer class (83), modulo
the two failed direct first substitutions.  No necessity is claimed: another
stabilized path may bypass this endpoint.  No Hall--Witt cancellation of its
higher interchange terms is proved here.

The dependency-free replay
`tests/stable_ac/test_ak3_mms02_tagged_buffer.py` checks every literal identity
in (73), (77)--(78), and (81)--(82), including both quotient substitutions.
The Magnus and HNN injectivity arguments remain the proof-theoretic steps.

Theorem 6.5 does not close (83).  A positive interleaved closure would prove
the stable MMS02 bridge and stable AK(3); the two negative sequential gates
prove neither.  Ordinary AK(3), stable Andrews--Curtis, and Andrews--Curtis
remain open.

### 6.12. Every nilpotent shadow of the tagged class vanishes

Undo the final donor macro in (75), using the current $rt$-row.  This gives

\[
 (A,B_t,v,rt)\sim_{\mathrm{AC}}(A,q,v,rt).
 \tag{85}
\]

Consequently the endpoint-local problem (83) is equivalent to the relative
two-row problem

\[
 (q,rt)\longrightarrow(B,t)
 \text{ over fixed }(A,v).
 \tag{86}
\]

Let

\[
 Q_A=\langle x,y,z\mid A,v\rangle
     \cong\langle x,y\mid\overline A\rangle
\]

and write $\gamma_nQ_A$ for its lower central series.  In the abelianization
of $F(x,y)$, the exact exponent vectors are

\[
 \begin{aligned}
 [\overline A]_{\mathrm{ab}}&=(0,1),&
 [\overline r]_{\mathrm{ab}}&=(0,1).
 \end{aligned}
 \tag{87}
\]

Thus $Q_A^{\mathrm{ab}}\cong\mathbb Z$ is generated by $x$, while both $y$ and
$r$ lie in $\gamma_2Q_A$.  Since $Q_A$ is generated by $x,y$, its derived
subgroup is normally generated by $[x,y]$.  But $y\in\gamma_2Q_A$, so

\[
 [x,y]\in[Q_A,\gamma_2Q_A]=\gamma_3Q_A.
\]

It follows that

\[
 \gamma_2Q_A=\gamma_3Q_A=\gamma_nQ_A
 \text{ for }n\geq2.
 \tag{88}
\]

In particular, $r$ lies in every term of the lower central series.  So does
$D=h[X,r]h^{-1}$.

Now put $G_t=Q_A*\langle t\rangle$.  The inclusion $Q_A\to G_t$ carries
$\gamma_nQ_A$ into $\gamma_nG_t$.  Hence every homomorphism from $G_t$ to a
nilpotent group kills both $r$ and $D$.  Since $B=qD^{-1}$, the two rows in
(86) have the literal same images:

\[
 q=B\text{ and }rt=t.
 \tag{89}
\]

The relator $\overline A$ becomes trivial after $y=1$, so there is an exact
retraction $G_t\to F(x,t)$ fixing $x,t$ and killing $y$.  In every nilpotent
quotient the image of $y$ is already trivial.  Hence the map induced by the
inclusion of $F(x,t)$ is surjective, and the retraction supplies its inverse.

**Theorem 6.6 (nilpotent invisibility).**  The normalized relative source
and target in (86) agree in every nilpotent quotient of $G_t$.  More exactly,
for every $c\geq1$,

\[
 G_t/\gamma_{c+1}G_t\cong F(x,t)/\gamma_{c+1}F(x,t),
 \tag{90}
\]

and both ordered pairs in (86) have image $(x^{-1},t)$.  Hence no invariant
determined only by the boundary-word images in finite lower-central quotients
can distinguish this tagged endpoint.

Section 4 proves $D\ne1$ in $Q_A$, while (88) places $D$ in every
$\gamma_nQ_A$.  Thus the Gate-A Magnus group is not residually nilpotent,
and the literal discrepancy survives precisely beyond all its nilpotent
shadows.  Theorem 6.6 is not a Peiffer lift and does not close (83).  It
does not evaluate a lower-central or augmentation filtration of the relative
free crossed module: such a calculation would first require explicit
$2$-cell lifts of $r$ and $D$ and the relative move action.  It proves none
of relative crossed-module or Peiffer class-two closure, literal higher
lifting, the MMS02 bridge, stable AK(3), ordinary AK(3), stable
Andrews--Curtis, or Andrews--Curtis.

### 6.13. The first legal interchange blocks two checkpoint cleanups

Continue with the normalized relative pair (86), keeping $A,v$ fixed.  For
a variable row $P$, define

\[
 \begin{aligned}
 C(P,v)&=({}^xP)({}^{x^2}P^{-1})({}^{x^2}v)({}^xP^{-1}),\\
 K(P,v)&=[u,C(P,v)].
 \end{aligned}
 \tag{91}
\]

Thus $K=K(q,v)$ and (73) gives $r=AK$.  Put

\[
 \begin{aligned}
 \Delta&=D(A),&
 \Theta&={}^{hA}[X,K],&
 W&=Kt,\\
 J&={}^{hA}[X,W],&
 \Xi&={}^{hAK}[X,t].
 \end{aligned}
 \tag{92}
\]

The identity $[X,ab]=[X,a]({}^a[X,b])$ gives

\[
 \begin{aligned}
 D(r)&=\Delta\Theta,&
 D(rt)&=\Delta J,&
 J&=\Theta\Xi.
 \end{aligned}
 \tag{93}
\]

Define

\[
 \begin{aligned}
 p_*&=q\Theta^{-1},&
 q_0&=qJ^{-1},&
 \Lambda&={}^q\Xi^{-1}.
 \end{aligned}
 \tag{94}
\]

Then

\[
 \begin{aligned}
 B&=p_*\Delta^{-1},&
 B_t&=q_0\Delta^{-1},&
 q_0&=\Lambda p_*.
 \end{aligned}
 \tag{95}
\]

Since $AK=r$, the last multiplier is exactly the old tagged discrepancy,

\[
 \Lambda={}^{qhr}[X,t]^{-1}=L_t.
 \tag{96}
\]

There is now a literal finite interchange which never uses a row as its own
donor:

\[
 (q,rt)\longrightarrow(q,W)\longrightarrow(q_0,W)
 \longrightarrow(q_0,\Omega t).
 \tag{97}
\]

The first arrow uses $rt=AW$.  For the second arrow, the exact factorization

\[
 J^{-1}=({}^{hA}W)({}^{hAX}W^{-1})
 \tag{98}
\]

uses only the other row $W$.  For the last arrow put

\[
 \begin{aligned}
 K_0&=K(q_0,v),&
 \Omega&=K_0^{-1}K(q_0J,v).
 \end{aligned}
 \tag{99}
\]

Because $q_0J=q$, one has $K=K_0\Omega$ and $W=K_0\Omega t$.
Formula (91) writes $K_0$ as a finite product of conjugates of
$q_0^{\pm1}$ and $v^{\pm1}$, so those two donor rows remove $K_0$.

Two checkpoint-local direct continuations fail.  At the middle pair
$(q_0,W)$, one has

\[
 q_0B^{-1}=\Lambda({}^{p_*}\Delta).
\]

Because ${}^{p_*}\Delta\in\operatorname{Ncl}(A)$, replacing $q_0$ directly
by $B$ would force

\[
 \Lambda\in\operatorname{Ncl}(A,v,W)
 =\operatorname{Ncl}(A,v,rt),
\]

contrary to $\mathsf T_B$.  In particular, even the preliminary replacement
$q_0=\Lambda p_*$ by $p_*$ is impossible.  At the final pair, replacing
$\Omega t$ by $t$
would require $\Omega\in\operatorname{Ncl}(A,v,q_0)$.  But
$q_0=B_t\Delta$ with $\Delta\in\operatorname{Ncl}(A)$, so $\mathsf T_t$
and $r=AK$ imply

\[
 K\notin\operatorname{Ncl}(A,v,q_0).
\]

Since $K=K_0\Omega$ and $K_0\in\operatorname{Ncl}(q_0,v)$, this proves

\[
 \boxed{\Omega\notin\operatorname{Ncl}(A,v,q_0).}
 \tag{100}
\]

**Theorem 6.7 (one-interchange boundary).**  The legal interchange (97)
trades the higher commutator $\Theta$ for the exact pair
$(\Lambda,\Omega)$.  The first-row cleanup is impossible at the middle
checkpoint $(q_0,W)$, and the second-row cleanup is impossible at the final
checkpoint $(q_0,\Omega t)$.  No assertion is made about cleaning the first
row after the third arrow changes the available donor row.  This closes this
one-interchange mechanism only, not the relative Peiffer class (83).

There is also no fixed-donor Hall--Witt shortcut.  After killing $A,v$ one
has $\Delta=1$, $r=K$, and $\Theta=D(r)\ne1$ by Section 4.  Therefore no
commutator rewriting which keeps the donor normal closure
$\operatorname{Ncl}(A,v,t)$ fixed can absorb $\Theta$.  Further
interleavings which alter both live rows and hence the available donor normal
closure remain open.  Freeze the bounded tagged ledger here: a subsequent
checkpoint must either construct a genuine continuation or control the full
relative Peiffer class, not introduce another finite alternation category.

### 6.14. The full factorwise metabelian shadow closes

The nilpotent collapse in Theorem 6.6 does not kill the first metabelian
boundary discrepancy.  Nevertheless, that discrepancy becomes an exact
conjugator, so the complete relative pair is AC-equivalent after the Gate-A
factor is metabelianized.

Put

\[
 \begin{aligned}
 M&=Q_A'/Q_A'',&
 \Lambda&=\mathbb Z[T,T^{-1}],
 \end{aligned}
\]

where $T$ acts on $M$ by conjugation by $x$.  The infinite cyclic cover of
the one-relator presentation has generators $y_i=x^iyx^{-i}$.  Abelianizing
the height row (10) gives

\[
 (-T-T^2+2T-1+T+1)[y]=(2T-T^2)[y]=0.
\]

There is one translate orbit of generators and one translate orbit of this
relation.  Since $T$ is a unit,

\[
 \boxed{
 M\cong\Lambda/(2-T)\cong\mathbb Z[1/2],
 }
 \tag{101}
\]

with $T$ acting as multiplication by $2$.  Thus
$Q_A/Q_A''=M\rtimes\langle x\rangle$.  Write its elements as $(m,k)=mx^k$;
then

\[
 (m,k)(n,l)=(m+2^kn,k+l).
 \tag{102}
\]

Taking $[y]=1$ in $\mathbb Z[1/2]$, the exact reduced words give

\[
 \begin{aligned}
 q&=(1/2,-1),&
 r&=(3,0),\\
 D&=(-3/4,0),&
 B&=(7/8,-1).
 \end{aligned}
 \tag{103}
\]

Indeed, $\overline r=xy^2x^{-1}y^{-1}$ gives $2T-1=3$.  Also
$[X,r]=(T^{-1}-1)r$, while conjugation by $h=YX$ contributes another
$T^{-1}$, giving $D=T^{-1}(T^{-1}-1)r=-3/4$.  Finally
$B=qD^{-1}$ gives the last coordinate in (103).

The surviving discrepancy is exactly a conjugation:

\[
 D^{-1}qD
 =(3/4,0)(1/2,-1)(-3/4,0)
 =(7/8,-1)=B.
\]

Hence

\[
 \boxed{{}^{D^{-1}}q=B\text{ in }Q_A/Q_A''.}
 \tag{104}
\]

Let

\[
 \widehat G_t=(Q_A/Q_A'')*\langle t\rangle.
\]

Conjugate the first row by $D^{-1}$ and use (104).  The word $B$ normally
generates $Q_A$: this is exactly the triviality of the presentation
$(A,B,v)$ already certified in Section 6.  Hence its image normally generates
$Q_A/Q_A''$, and a finite product of conjugates of $B^{\pm1}$ removes $r$
from the second row.  Therefore

\[
 \boxed{
 (q,rt)\sim_{\mathrm{AC}}(B,rt)
 \sim_{\mathrm{AC}}(B,t)
 \text{ in }\widehat G_t.
 }
 \tag{105}
\]

**Theorem 6.8 (factorwise metabelian closure).**  The entire normalized
relative pair (86), not merely its boundary words, is AC-equivalent after
killing $Q_A''$.  Consequently every quotient of $G_t$ whose restriction to
$Q_A$ is metabelian, including every metabelian quotient of $G_t$, sees the
same AC class.

This is a positive shadow only.  It does not lift the conjugacy (104) to
$Q_A$, evaluate the relative free crossed module, or close (83).  No
obstruction factoring through $\widehat G_t$ can distinguish the pair.  To
promote the specific path (105), one would have to lift it
through $Q_A''$ with legal Peiffer moves; another full relative path remains
possible.  The MMS02 bridge, stable AK(3), and ordinary AK(3) remain open.

### 6.15. The canonical metabelian conjugator has a literal defect

The quotient conjugacy (104) has one exact lift defect in $Q_A$:

\[
 E:=D^{-1}qDB^{-1}
   =D^{-1}qD^2q^{-1}.
 \tag{106}
\]

Equation (104) places $E$ in $Q_A''$.  It is not the identity.  Use the
ascending HNN model of Section 4, with free base $F_0=F(a,b)$ and
$xwx^{-1}=\varphi(w)$.  Conjugating the defect $D$ by $x^2$ gives the base
word already reduced in (16):

\[
 \begin{aligned}
 \delta:=x^2Dx^{-2}
 &=ba^{-1}ba^{-1}b^{-1}ab^{-2}.
 \end{aligned}
 \tag{107}
\]

Since $x^2qx^{-2}=bx^{-1}$, conjugating (106) by $x^2$ gives

\[
 x^2Ex^{-2}
 =\delta^{-1}b x^{-1}\delta^2x b^{-1}.
 \tag{108}
\]

The image subgroup $\varphi(F_0)$ is generated by

\[
 \begin{aligned}
 \varphi(a)&=b,&
 \varphi(b)&=b^2a^{-1}bab^{-1}.
 \end{aligned}
\]

Both generators have zero $a$-exponent, whereas

\[
 \begin{aligned}
 \operatorname{exp}_a(\delta)&=-1,&
 \operatorname{exp}_a(\delta^2)&=-2.
 \end{aligned}
 \tag{109}
\]

Therefore $\delta^2\notin\varphi(F_0)$.  The only possible HNN pinch in
(108) is $x^{-1}\delta^2x$, and the subgroup-membership test shows that it
is not a pinch.  Equation (108) is Britton reduced with stable letters, so
$E\ne1$ in $Q_A$.

**Theorem 6.9 (literal defect of the quotient conjugator).**  The element
$E$ is a nontrivial member of $Q_A''$.  Thus the specific first arrow in
(105), conjugation of $q$ by $D^{-1}$, does not lift unchanged from
$Q_A/Q_A''$ to $Q_A$.

This theorem does not rule out a different conjugator, a correction to
$D^{-1}$ by an element of $Q_A''$, a multi-row Peiffer lift of (105), or a
different full relative path.  It closes only the unchanged lift of the
canonical metabelian conjugator.  No further list of candidate conjugators
is opened; the remaining object is the full relative Peiffer class (83).

### 6.16. The whole displayed metabelian correction coset is obstructed

The correction left open by Theorem 6.9 is an infinite set, but its first
nonabelian derived quotient has an exact direct-limit model.  Put

\[
 \begin{aligned}
 F_0&=F(a,b),&
 F_n&=x^{-n}F_0x^n,&
 j_n(w)&=x^{-n}wx^n.
 \end{aligned}
\]

The inclusions satisfy $j_n(w)=j_{n+1}(\varphi(w))$.  Since the
abelianization of $Q_A$ is generated by $x$, its kernel is $Q_A'$, and

\[
 Q_A'=\bigcup_{n\geq0}F_n
      =\mathop{\mathrm{colim}}(F_0,\varphi).
 \tag{110}
\]

Every finite set of elements lies in one $F_n$.  Taking two derived
subgroups therefore commutes with this increasing union and gives

\[
 L:=Q_A''/Q_A'''
 \cong
 \mathop{\mathrm{colim}}
 \left(F_0'/F_0'',\varphi_*\right).
 \tag{111}
\]

Let

\[
 \begin{aligned}
 R_0&=\mathbb Z[\mathsf a^{\pm1},\mathsf b^{\pm1}],&
 \alpha(\mathsf a)&=\mathsf b,&
 \alpha(\mathsf b)&=\mathsf b^2.
 \end{aligned}
\]

The abelianized left Fox vector identifies $F_0'/F_0''$ with the free
$R_0$-module generated by $e$, where

\[
 \partial_{\mathrm{ab}}e=(1-\mathsf b,\mathsf a-1).
\]

Using $\varphi(a)=b$ and $\varphi(b)=d=b^2a^{-1}bab^{-1}$, the Fox
determinant of the two images is

\[
 s=\mathsf a^{-1}\mathsf b^2(1-\mathsf b).
\]

Thus the transition in (111) is the semilinear map

\[
 \psi(f)=s\alpha(f).
 \tag{112}
\]

The defect has a finite-stage representative which can be evaluated
exactly.  Conjugating (108) once and twice gives

\[
 \begin{aligned}
 \epsilon:=x^3Ex^{-3}
 &=\varphi(\delta)^{-1}d\delta^2d^{-1},\\
 \zeta:=x^4Ex^{-4}&=\varphi(\epsilon)\in F_0'.
 \end{aligned}
 \tag{113}
\]

Here the exponent vectors of $\epsilon$ and $\zeta$ are respectively
$(-2,1)$ and $(0,0)$.  Direct Fox differentiation gives

\[
 \begin{aligned}
 \partial_{\mathrm{ab}}\zeta
 &=f(1-\mathsf b,\mathsf a-1),&
 f&=\mathsf a^{-1}
   (-\mathsf b^{10}+\mathsf b^{12}-\mathsf b^{14}).
 \end{aligned}
 \tag{114}
\]

Consequently $[E]\in L$ is represented by $f$ at stage four.  It is
nonzero: $\alpha(f)=-\mathsf b^{19}+\mathsf b^{23}-\mathsf b^{27}$,
and every later $\alpha$-iterate is nonzero because
$\mathsf b\mapsto\mathsf b^2$ is injective on
$\mathbb Z[\mathsf b^{\pm1}]$; the intervening factors
$\alpha^i(s)$ are nonzero in the Laurent domain.

Now take the complete correction coset of the displayed quotient
conjugator.  If $c=nD^{-1}$ with $n\in Q_A''$, then
$cqc^{-1}=B$ is equivalent, using $D^{-1}qD=EB$, to

\[
 E=n^{-1}({}^{B}n).
 \tag{115}
\]

In $L$ this is the twisted-coboundary equation

\[
 [E]=(B-1)[n].
 \tag{116}
\]

It remains to evaluate its image, rather than enumerate corrections.
The exact decompositions

\[
 \begin{aligned}
 q&=j_1(a)x^{-1},&
 D&=j_2(\delta),\\
 B&=j_3(u)x^{-1},&
 u&=d\delta^{-1}
 \end{aligned}
 \tag{117}
\]

give $\operatorname{ab}(u)=\mathsf a\mathsf b^3$.  Represent an arbitrary
class $[n]$ by $g\in R_0$ at a stage $m\geq4$.  Moving both terms of
$(B-1)[n]$ to stage $m+1$ gives the coefficient

\[
 \mathsf b^{7\cdot2^{m-3}}g-s\alpha(g).
 \tag{118}
\]

Indeed, conjugation by the base part of $B$ contributes
$\alpha^{m-2}(\mathsf a\mathsf b^3)
=\mathsf b^{7\cdot2^{m-3}}$, while the unchanged class moves through one
transition (112).

Equality in the direct limit can now be tested after one application of
$\alpha$.  More explicitly, put

\[
 \begin{aligned}
 S_0&=\mathbb Z[\mathsf b^{\pm1}],&
 \tau(k)&=\mathsf b^3(1-\mathsf b^2)k(\mathsf b^2).
 \end{aligned}
\]

Then $\alpha\psi=\tau\alpha$, the map $\alpha:R_0\to S_0$ is onto,
$\ker\alpha\subseteq\ker\psi$, and $\tau$ is injective.  Hence $\alpha$
induces an isomorphism between the direct limit in (111) and
$\mathop{\mathrm{colim}}(S_0,\tau)$.  In particular, a same-stage
difference dies exactly when its $\alpha$-image is zero: a nonzero image
survives every injective $\tau$-iterate, while a zero image is killed by
the next $\psi$-transition.

Every $[n]\in L$ has a representative $g$ at some stage $m\geq4$.
Put $h=\alpha(g)$ and $Q=2^{m-2}$.  Equations (112), (114), and (118)
turn (116), for that arbitrary stage, into the necessary and sufficient
Laurent equation

\[
 \begin{aligned}
 \mathsf b^{7Q}h(\mathsf b)
 &+\mathsf b^3(\mathsf b^2-1)h(\mathsf b^2)\\
 &=-\mathsf b^{11Q-3}
 \prod_{i=1}^{m-3}(1-\mathsf b^{2^i})
 (1-\mathsf b^{2Q}+\mathsf b^{4Q}).
 \end{aligned}
 \tag{119}
\]

Equation (119) has no Laurent-polynomial solution.  To see this, let
$\ell$ and $d_+$ be the least and greatest exponents of a nonzero $h$.
The right side has least exponent $11Q-3$ and greatest exponent $16Q-5$.
Its exponents are odd, while the second term on the left also has only odd
exponents.  Comparison at every even exponent first shows that $h$ has
only odd exponents.  Comparing the two extreme exponents then forces

\[
 \begin{aligned}
 \ell&=\frac{11Q}{2}-3,&
 d_+&=8Q-5.
 \end{aligned}
 \tag{120}
\]

At the possible lower collision $\ell=7Q-3$, the whole left side starts
strictly above $11Q-3$; at the possible upper collision $d_+=7Q-5$, the
two leading coefficients add.  Thus neither collision changes (120).

Set $z=\mathsf b^2$ and

\[
 \begin{aligned}
 h(\mathsf b)&=\mathsf b^{11Q/2-3}G(z),&
 P_Q(z)&=\prod_{j=0}^{m-4}(1-z^{2^j}).
 \end{aligned}
\]

After division by the lowest monomial, (119) becomes

\[
 z^{3Q/4}G(z)+(z-1)G(z^2)
 =-P_Q(z)(1-z^Q+z^{2Q}).
 \tag{121}
\]

In fact $P_Q$ divides $G$.  Put
$R_i(z)=\prod_{j=0}^{i-1}(1-z^{2^j})$.  If $R_i$ divides $G$, then

\[
 R_i(z^2)=R_i(z)\frac{1-z^{2^i}}{1-z}.
\]

Divide (121) by $R_i$.  For $i<m-3$, both the second term and the right
side are divisible by $1-z^{2^i}$; hence so is $G/R_i$, because $z$ is
coprime to that factor.  Induction gives $R_{m-3}=P_Q\mid G$.

Write $G=P_QH$.  Since

\[
 P_Q(z^2)=P_Q(z)\frac{1-z^{Q/2}}{1-z},
\]

equation (121) reduces exactly to

\[
 z^{3Q/4}H(z)-(1-z^{Q/2})H(z^2)
 =-1+z^Q-z^{2Q}.
 \tag{122}
\]

Let $p=Q/4$ and write $H(z)=\sum_i h_i z^i$.  Comparing the coefficients
at degrees $0,2p,4p$ in succession gives

\[
 \begin{aligned}
 h_0&=1,&
 h_p&=1,&
 h_{2p}&=1.
 \end{aligned}
 \tag{123}
\]

At degree $6p$, the first two contributions $h_{3p}$ and $-h_{3p}$
cancel, leaving $h_{2p}=1$.  The right side of (122) has coefficient zero
there.  This contradiction proves that (119), hence (116), has no
solution.

**Theorem 6.10 (second-derived correction-coset obstruction).**  There is
no $n\in Q_A''$ for which $nD^{-1}$ conjugates $q$ to $B$ in $Q_A$.
Equivalently, the whole coset $Q_A''D^{-1}$ is disjoint from the set of
literal conjugators from $q$ to $B$.

This theorem closes the full $Q_A''$-correction fiber of the particular
metabelian conjugator in (104).  It does not classify all conjugators in
$Q_A/Q_A''$, rule out a lift based on another metabelian conjugator, rule
out a multi-row Peiffer lift of (105), or obstruct a different full
relative path.  The unrestricted MMS02 bridge, stable AK(3), and ordinary
AK(3) remain open.

### 6.17. All literal conjugators are obstructed

The remaining metabelian conjugator classes have an exact classification.
Let $H=Q_A/Q_A''$ with the coordinates (102).  An element $(m,k)$ commutes
with $q=(1/2,-1)$ exactly when

\[
 m+2^{k-1}=\frac12+\frac m2,
\]

or equivalently $m=1-2^k$.  The elements with these coordinates form the
cyclic group generated by $q$:

\[
 \begin{aligned}
 C_H(q)&=\{(1-2^k,k):k\in\mathbb Z\}=\langle q\rangle,&
 (1-2^k,k)&=q^{-k}.
 \end{aligned}
 \tag{124}
\]

Put $c_0=D^{-1}$.  Equation (104) says $c_0qc_0^{-1}=B$ in $H$.  Hence
every conjugator from $q$ to $B$ in $H$ is of the form

\[
 c_0q^j=D^{-1}q^j
 \text{ for }j\in\mathbb Z.
 \tag{125}
\]

Indeed, if $cqc^{-1}=B$, then $c_0^{-1}c$ centralizes $q$; the converse is
immediate.  Now suppose a literal conjugator $c\in Q_A$ existed.  Its image
in $H$ has the form (125), so for some $n\in Q_A''$ and $j\in\mathbb Z$,

\[
 c=nD^{-1}q^j.
\]

Powers of $q$ commute with $q$ already in $Q_A$, not merely in $H$.
Therefore

\[
 \begin{aligned}
 cqc^{-1}
 &=nD^{-1}q^j q q^{-j}Dn^{-1}\\
 &=nD^{-1}qDn^{-1}\\
 &=nEBn^{-1}.
 \end{aligned}
 \tag{126}
\]

If this were $B$, the same calculation as (115) would give
$E=n^{-1}({}^{B}n)$.  Theorem 6.10 proves that no such $n$ exists.

**Theorem 6.11 (literal nonconjugacy).**  The elements $q$ and $B$ are not
conjugate in $Q_A$.  Equivalently, no lift of any metabelian quotient
conjugator supplies the first arrow of (105) as one literal conjugation.

This exhausts literal conjugators, not relative Andrews--Curtis paths.  A
multi-row Peiffer lift may change both live rows, and another full path need
not project to the particular quotient path (105).  The interleaved relative
class (83), the unrestricted MMS02 bridge, stable AK(3), and ordinary AK(3)
remain open.

### 6.18. The tagged coefficient can be removed exactly

There is one further simplification of the normalized source (86) which
does not open another cleanup ledger.  Work first in the quotient of
$F(x,y,z)$ by $q=Xy$ and $v=Xyz$.  The two equations give $y=x$ and $z=1$.
Direct free reduction then gives

\[
 \begin{aligned}
 A&\longmapsto x,&
 r&\longmapsto x.
 \end{aligned}
\]

Therefore

\[
 \begin{aligned}
 rA^{-1}&\in\operatorname{Ncl}_{F(x,y,z)}(q,v),&
 r&\in\operatorname{Ncl}_{F(x,y,z)}(A,q,v).
 \end{aligned}
 \tag{127}
\]

Choose any finite normal-closure factorization of $r^{-1}$ by conjugates of
$A^{\pm1},q^{\pm1},v^{\pm1}$.  The standard donor macro appends its factors
to the tagged row while restoring every donor.  Hence

\[
 (A,q,v,rt)\sim_{\mathrm{AC}}(A,q,v,t).
 \tag{128}
\]

Combining (85) and (128), the endpoint-local problem (83) is equivalent to

\[
 (A,q,v,t)\longrightarrow(A,B,v,t).
 \tag{129}
\]

Equivalently, after passing to the relative ambient group, its exact open
core is

\[
 \boxed{
 (q,t)\longrightarrow(B,t)
 \text{ in }Q_A*\langle t\rangle.
 }
 \tag{130}
\]

**Theorem 6.12 (tagged normal-generator reduction).**  Closure of the
canonical relative class (83) is equivalent to closure of the tagged gate
(130).  Both $q$ and $B$ normally generate $Q_A$, while Theorem 6.11 proves
that they are not conjugate there.

The final sentence does not turn literal nonconjugacy into tagged-pair
inequivalence.  Arbitrary Andrews--Curtis paths may multiply the first row
by conjugates of the tag row, move the tag row, and later cancel the added
stable-letter syllables.  No tag-rigidity or destabilization theorem is
proved.  The gate (130), the unrestricted MMS02 bridge, stable AK(3), and
ordinary AK(3) remain open.

### 6.19. The first tagged defect module is induced without a free summand

The correct linear ambient object for (130) is not $L$ alone.  Put

\[
 \begin{aligned}
 H&=Q_A/Q_A'',&
 \overline G&=H*\langle t\rangle,\\
 G_t&=Q_A*\langle t\rangle,&
 N_t&=\ker(G_t\longrightarrow\overline G),\\
 L&=Q_A''/Q_A''',&
 \mathcal M&=N_t/[N_t,N_t].
 \end{aligned}
 \tag{131}
\]

Give $L$ its left $H$-module structure by conjugation.  There is an exact
left $\mathbb Z[\overline G]$-module isomorphism

\[
 \boxed{
 \mathcal M\cong
 \mathbb Z[\overline G]\otimes_{\mathbb Z[H]}L.
 }
 \tag{132}
\]

Here $\mathbb Z[\overline G]$ is a right $\mathbb Z[H]$-module by
multiplication.  To prove (132), use the Bass--Serre tree $T$ of
$G_t=Q_A*\langle t\rangle$.  The quotient graph $N_t\backslash T$ has

\[
 \begin{aligned}
 \text{first vertices}&=\overline G/H,&
 \text{tag vertices}&=\overline G/\langle t\rangle,&
 \text{edges}&=\overline G.
 \end{aligned}
\]

With the natural incidence maps, this is exactly the Bass--Serre tree of
$\overline G=H*\langle t\rangle$.  In particular, it is a tree, not merely
a connected graph.  The Kurosh decomposition of $N_t$ therefore has no
free factor from the quotient graph.  Its only nontrivial vertex groups are
the conjugates of $Q_A''$ at the first vertices:

\[
 N_t
 \cong
 \mathop{\ast}_{gH\in\overline G/H}gQ_A''g^{-1}.
 \tag{133}
\]

Abelianizing (133) gives the direct sum of the conjugate copies of $L$.
The $\overline G$-action permutes the cosets and uses the $H$-conjugation
action inside a fixed copy.  This is exactly the induced module (132).

The identity-coset factor in (133) also proves that the natural map

\[
 L\longrightarrow\mathcal M
\]

is injective.  Hence the nonzero class $[E]\in L$ from Section 6.16 remains
nonzero in $\mathcal M$.

Now follow the canonical path in $\overline G$: conjugate the first entry
$q$ by $D^{-1}$ and leave the tag $t$ fixed.  Its literal lift in $G_t$
ends at $(EB,t)$, so its complete first-derived residual is

\[
 \boxed{\kappa_0=([E],0)\in\mathcal M^2.}
 \tag{134}
\]

**Theorem 6.13 (induced tagged defect module).**  The first derived kernel
for the tagged gate (130) is the induced module (132), with no additional
Kurosh free summand, and the canonical quotient path has the nonzero residual
(134).

Nonzero $\kappa_0$ does not yet obstruct the full tagged gate.  Another
quotient path differs from the canonical path by an Andrews--Curtis loop at
$(B,t)$ in $\overline G$, but a quotient loop has no canonical affine action
on $\mathcal M^2$.  One must choose a tame lift of every operator move, and
different lifts by $N_t$ can add vertical defects.  This includes tame
transformations which project to the identity quotient loop.

Fix the literal lift producing $\kappa_0$.  Define $\mathcal D$ to be the
set of all first-derived defects obtained by composing that lift with every
tame full-group transformation whose projection is an Andrews--Curtis loop
at $(B,t)$ in $\overline G$.  Thus $\mathcal D$ uses the full preimage of the
quotient-loop stabilizer, not one chosen section of it.  A full path for
(130) forces $0\in\mathcal D$; proving $0\notin\mathcal D$ would obstruct
(130).  Conversely, $0\in\mathcal D$ would close only this first-derived
obstruction, not construct a full path.

The exact next obligation is to evaluate the complete lifted defect set
$\mathcal D$, not another finite move ledger.  It must retain both the
quotient stabilizer and the vertical kernel of the tame operator action.
The relative Peiffer class, the MMS02 bridge, stable AK(3), and ordinary
AK(3) remain open.

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
6. the exact $T_{\rm pub}$ complex and all four pinned-seam donor neighbours
   are nonthickenable, but this does not obstruct another AC-equivalent
   thickenable representative;
7. the one-tag path reaches (83), and both direct first cleanup substitutions
   fail, but its interleaved relative Peiffer class remains open;
8. the normalized tagged source and target agree in every nilpotent quotient,
   but this boundary-image equality is not a crossed-module or Peiffer lift;
9. the first legal no-self-donor interchange blocks the middle first-row
   cleanup and final second-row cleanup at their respective checkpoints, but
   the first row after the third arrow and unrestricted interleaving remain
   open;
10. the full factorwise metabelian image of the tagged pair is AC-equivalent,
    but this quotient path is not itself a Peiffer lift;
11. the canonical metabelian conjugator has a nontrivial literal defect, its
    complete $Q_A''$-correction coset is obstructed, and the metabelian
    centralizer classification rules out every literal conjugator from $q$
    to $B$, but multi-row Peiffer lifts and full relative paths remain open;
12. the coefficient $r$ can be removed from the tagged source, so the exact
    open core is $(q,t)\to(B,t)$, but literal nonconjugacy does not decide this
    two-row Andrews--Curtis orbit;
13. the first derived tagged kernel is the induced module from
    $Q_A''/Q_A'''$ and the canonical quotient path has residual $([E],0)$,
    but the complete defect set over all tame lifts of quotient AC loops has
    not been evaluated;
14. no MMS02 statement evaluates the period-two class-two ledger or its
   literal higher lift; and
15. stable AK(3), ordinary AK(3), stable Andrews--Curtis, and
   Andrews--Curtis are not claimed.

The active priority is the interleaved relative class (83), together with
the unrestricted rank-three bridge
$T_{\rm pub}\sim_{\rm AC}(A,B,zYX)$.  No further sequential or pinned-donor
ledger is opened.
