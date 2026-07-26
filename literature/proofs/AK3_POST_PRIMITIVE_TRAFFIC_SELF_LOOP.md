# Post-primitive AC traffic commutes with deletion

Date: 2026-07-25

Status: **PROVEN**. Once a primitive relator \(W\) is fixed, every
classical AC1--AC3 history which never multiplies another relator into
the \(W\)-slot descends through primitive straightening and deletion.
Inverting or conjugating that slot is harmless. Using any current
conjugate of \(W^{\pm1}\) as a source becomes a no-op; every other move
remains the corresponding classical AC move on the quotient relators.

Consequently, arbitrary post-manufacture traffic away from the primitive
slot cannot make the AK(3) relation-split or source-slot constructions
escape their proved self-loops.

## 1. Quotient naturality

Let \(F\) be a free group, let

\[
\theta:F\longrightarrow H
\tag{1.1}
\]

be a homomorphism, and let

\[
\mathcal C=(A_1,\ldots,A_n,W)
\tag{1.2}
\]

be a relator tuple with

\[
\theta(W)=1.
\tag{1.3}
\]

Keep the \(W\)-slot distinguished.

### Lemma 1.1 (one-move naturality)

Apply one of the following moves:

1. invert any slot;
2. conjugate any slot by an arbitrary \(g\in F\);
3. right-multiply \(A_i\) by
   \(gA_j^\epsilon g^{-1}\), where the target is not the distinguished
   slot, \(i\ne j\), \(\epsilon\in\{\pm1\}\), and \(A_j\) may be the
   current conjugate or inverse of \(W\).

After applying \(\theta\), inversion or conjugation of a non-distinguished
slot is the corresponding AC2 or AC3 move in \(H\). The same moves on
the distinguished slot leave its image equal to \(1\) and induce no
quotient move. The third operation is the corresponding multiplication
by the conjugate of \(\theta(A_j)^\epsilon\) for a non-distinguished
source, and is a no-op for the distinguished source.

#### Proof

Homomorphisms preserve inversion, products, and conjugation:

\[
\begin{aligned}
\theta(A_i^{-1})
&=\theta(A_i)^{-1},\\
\theta(gA_ig^{-1})
&=\theta(g)\theta(A_i)\theta(g)^{-1},\\
\theta(A_i gA_j^\epsilon g^{-1})
&=
\theta(A_i)\theta(g)
\theta(A_j)^\epsilon\theta(g)^{-1}.
\end{aligned}
\tag{1.4}
\]

If \(A_j\) is a conjugate of \(W^{\pm1}\), (1.3) makes the last factor
the identity. Inversion and conjugation preserve that property for the
distinguished slot. \(\square\)

### Theorem 1.2 (history naturality)

Let \(\mathcal C'\) be obtained from \(\mathcal C\) by any finite
AC1--AC3 history in which no AC1 multiplication targets the
distinguished \(W\)-slot. AC2 inversion and AC3 conjugation of that slot
are allowed.
Normalize the distinguished slot back to \(W\) by AC2--AC3 if necessary,
then delete it after applying \(\theta\). Then

\[
\boxed{
\theta(\mathcal C'\setminus\{W\})
\sim_{\mathrm{AC1-3}}
(\theta(A_1),\ldots,\theta(A_n)).
}
\tag{1.5}
\]

#### Proof

Apply Lemma 1.1 move by move. Each move induces either one valid
classical AC move on the quotient tuple or the identity. Their finite
composition is a classical AC sequence. \(\square\)

The statement allows arbitrary conjugators, including words involving
the generator which will be deleted. It also allows arbitrary mutual
traffic among the non-\(W\) slots, arbitrary uses of the distinguished
slot as a source, and arbitrary inversions or conjugations of that slot.

## 2. Primitive deletion

Suppose now that the tuple is a balanced presentation of the trivial
group and

\[
W=\phi(q)
\tag{2.1}
\]

is primitive. Let

\[
\rho(q)=1,
\qquad
\theta=\rho\phi^{-1}.
\tag{2.2}
\]

Then \(\theta(W)=1\), and straightening \(W\) by \(\phi^{-1}\) followed
by removal of the \(q\)-generator-relator pair sends every other relator
\(A_i\) to \(\theta(A_i)\).

### Corollary 2.1 (post-primitive traffic closure)

Every finite AC1--AC3 history which does not multiply another relator
into the \(W\)-slot descends through primitive deletion to a classical
AC1--AC3 history on the immediate quotient endpoint.

#### Proof

Stable ambient straightening and primitive deletion are valid for the
balanced trivial-group presentation. The quotient map is exactly (2.2),
so Theorem 1.2 applies. \(\square\)

This is stronger than passive-target absorption. The other slots may
target one another arbitrarily. The distinguished slot may be inverted,
conjugated, and used as a source. The only forbidden operation is an AC1
multiplication which puts a nontrivial quotient relator into it.

## 3. AK(3) consequence

At the source-slot checkpoint from the preceding theorem, the tuple is

\[
\mathcal C
=
(\beta(R),W,D,q),
\tag{3.1}
\]

where

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1},\\
U&=RB,\\
W&=\beta(U)q,
\qquad
\beta(x)=qxq^{-1}.
\end{aligned}
\tag{3.2}
\]

For

\[
\phi=\beta\alpha_U,
\qquad
\theta=\rho\phi^{-1},
\tag{3.3}
\]

the immediate quotient endpoint is

\[
(R,D',U^{-1}),
\qquad
D'=t^{-1}zUxU^{-1}z^{-1}.
\tag{3.4}
\]

The source-slot theorem proves

\[
(R,D',U^{-1})
\sim_{\mathrm{AC1-3}}
(R,B,D).
\tag{3.5}
\]

Corollary 2.1 now gives the unbounded statement

\[
\boxed{
\begin{gathered}
\text{any finite AC1--AC3 history on }
\beta(R),D,q,\\
\text{with arbitrary uses, inversions, and conjugations of \(W\),}\\
\text{but no AC1 multiplication into the \(W\)-slot,}\\
\text{still deletes to the classical AK(3) class.}
\end{gathered}
}
\tag{3.6}
\]

No bound on the number of moves, conjugator length, or intermediate word
length is used.

## 4. Mixed exact replay

The independent verifier applies the following nontrivial history to
(3.1):

1. conjugate the \(W\)-slot by \(t\);
2. invert the conjugated \(W\)-slot;
3. multiply the \(q\)-slot by an \(x\)-conjugate of \(D\);
4. multiply the \(D\)-slot by a \(z\)-conjugate of the current
   distinguished source;
5. multiply the \(\beta(R)\)-slot by a \(t\)-conjugate of the modified
   \(q\)-slot;
6. invert the modified \(q\)-slot;
7. conjugate the modified \(D\)-slot by \(qx\).

The verifier computes the final free words first and only then applies
\(\theta\). Independently, it starts at (3.4), maps every conjugator
through \(\theta\), replays the four nontrivial quotient moves, and
checks literal equality of all three output relators. The first two moves
and the distinguished-source multiplication all become the predicted
no-ops because \(\theta(W)=1\).

## 5. Boundary

The theorem does not allow AC1 multiplication of another relator into
the \(W\)-slot. After such a move, the distinguished relator need not
remain in the primitive conjugacy class of \(W^{\pm1}\), so the fixed
\(\phi^{-1}\) straightening and deletion argument no longer applies.
AC2 and AC3 on that slot are allowed because they preserve its primitive
conjugacy class and can be undone before straightening.

It also does not classify:

- traffic before the fixed \(W\)-checkpoint;
- a later choice of a different primitive slot;
- AC4/AC5 moves not already included in the stable straightening and
  deletion composite;
- primitive-pair compression.

Thus post-manufacture traffic is not an escape. A new relative-
transvection route must change the primitive target itself or break an
earlier manufacture hypothesis. AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_post_primitive_traffic.py` checks:

- the exact source-slot checkpoint and quotient map;
- all seven post-manufacture moves in \(F(x,t,z,q)\);
- the predicted quotient no-op for a \(W\)-source move;
- literal equality between “move then quotient” and “quotient then
  move” for every surviving slot.
