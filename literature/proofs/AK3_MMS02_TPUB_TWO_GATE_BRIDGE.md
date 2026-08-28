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
AC-equivalent once the two identity rows are retained.  Thus further
quotient obstructions cannot decide the bridge.  The remaining gate is the
literal relation-identity lift back through the normal closure of $A,B$.

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

## 6. Quotient reachability is automatic with two redundant rows

The unrestricted bridge cannot be disproved by extending the fixed-base
$A_5$ or Alexander tests to another quotient of the same deficiency-one
group.  The reason is a general redundant-row transfer lemma.

Write $\operatorname{Ncl}_G(S)$ for the normal closure of a subset $S$ in
$G$.

**Lemma 6.1 (two-row normal-generator transfer).**  Let $G$ be any group,
and let $g,h\in G$ satisfy

\[
 \operatorname{Ncl}_G(g)
 =G
 =\operatorname{Ncl}_G(h).
 \tag{30}
\]

Then the redundant triples are Andrews--Curtis equivalent in $G$:

\[
 \boxed{(1,1,g)\sim_{\rm AC}(1,1,h).}
 \tag{31}
\]

Here an elementary macro may multiply one entry by a conjugate of another
entry or its inverse.  Such a macro is a finite AC1--AC3 sequence: conjugate
the source, multiply it into the target, and restore the source, with two
source inversions when the negative sign is used.

**Proof.**  Choose finite normal-closure factorizations of $h$, $g^{-1}$,
and $g$ by conjugates of $g^{\pm1}$, $h^{\pm1}$, and $h^{\pm1}$,
respectively.  Build the required products in the two identity entries and
then use ordinary target multiplications:

\[
 \begin{aligned}
 (1,1,g)
 &\sim(h,1,g)
 \sim(h,g^{-1},g)
 \sim(h,g^{-1},1)\\
 &\sim(h,g^{-1},h)
 \sim(1,g^{-1},h)
 \sim(1,1,h).
 \end{aligned}
 \tag{32}
\]

The third arrow multiplies the third entry by the second, the fourth
multiplies it by the first, and the fifth multiplies the first by the
inverse of the third.  The last arrow appends the chosen factorization of
$g$ using the third entry.  Every other arrow appends one of the chosen
finite products while preserving its source.  Thus every arrow expands
into AC1--AC3 moves.  $\square$

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
statement for $\overline v$.  Lemma 6.1 therefore proves

\[
 \boxed{
 (1,1,\overline u)
 \sim_{\rm AC}
 (1,1,\overline v)
 \text{ in }G_-.
 }
 \tag{34}
\]

The same conclusion holds after every homomorphism out of $G_-$.  Hence no
AC invariant which factors only through the image triples in an $A_5$,
Alexander, metabelian, or other quotient of $G_-$ can obstruct the
unrestricted all-row bridge.  Those tests remain valid for fixed-base
ansatzes, where the first two entries are required to stay equal to one.

Equation (34) does not prove the free-group bridge.  Lifting a chosen path
from (34) to $F$ ends with rows $E_1,E_2,E_3$ satisfying

\[
 \begin{aligned}
 E_1,E_2&\in N,\\
 E_3v^{-1}&\in N.
 \end{aligned}
 \tag{35}
\]

but it need not end at the literal tuple $(A,B,v)$.  The exact remaining
gate is to choose and lift the normal-closure factorizations in (32) so that
the three $N$-valued identity residuals close by AC moves.  This is a
relation-identity lift problem.  Quotient reachability itself is complete,
and further quotient hunting cannot evaluate that lift.

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
4. Lemma 6.1 closes only quotient reachability and does not close the
   relation-identity lift in (35);
5. no MMS02 statement evaluates the period-two class-two ledger or its
   literal higher lift; and
6. stable AK(3), ordinary AK(3), stable Andrews--Curtis, and
   Andrews--Curtis are not claimed.

The active priority is now the unrestricted stable bridge
$T_{\rm pub}\sim_{\rm AC}(A,B,zYX)$ with all rows allowed to move.
