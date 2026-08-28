# The MMS02 published triple reduces to two one-relator gates

## Status

This note isolates the highest-value theory route to stable AK(3).  It
proves that either of two explicit normal-closure memberships is sufficient
to AC-trivialize the published MMS02 rank-three triple

\[
 T_{\rm pub}=(A,B,Xyz).
 \tag{1}
\]

The memberships are not evaluated here.  A positive gate would prove stable
AK(3) after composition with the independently replayed MMS02 corridor.  It
would not prove ordinary AK(3), because that corridor uses the rank-changing
Tietze/AC4--AC5 passage between the rank-three triple and AK(3).

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
an exact invariant or homomorphism detecting the named defect in the named
one-relator quotient.  A bounded search or failure to find a finite quotient
does neither.

## 4. Stable-AK(3) implication and strict nonclaims

The verified MMS02 corridor gives a stable equivalence between
$T_{\rm pub}$ and AK(3), while the triple $(A,B,zYX)$ is independently
AC-trivial at rank three.  Hence (7) would prove stable AK(3).

The logical gates remain separate:

1. neither $\mathsf G_A$ nor $\mathsf G_B$ is proved;
2. nontriviality of both defects would refute only these two sequential
   donor completions, not the unrestricted all-row bridge;
3. the fixed-base $A_5$ and Alexander obstructions do not apply to a path
   which moves $A$ and $B$;
4. no MMS02 statement evaluates the period-two class-two ledger or its
   literal higher lift; and
5. stable AK(3), ordinary AK(3), stable Andrews--Curtis, and
   Andrews--Curtis are not claimed.

The active priority is $\mathsf G_A$ first, because it has the shorter
displayed defect, followed by $\mathsf G_B$.  If both are disproved, the
next route is the unrestricted stable bridge
$T_{\rm pub}\sim(A,B,zYX)$ with all rows allowed to move.
