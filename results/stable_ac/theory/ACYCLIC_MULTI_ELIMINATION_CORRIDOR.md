# Acyclic Multi-Elimination Corridor (AMEC)

Date: 2026-08-16

Status: **proved and independently replayed**. Sol advisor verdict under the
user-corrected gate: **APPROVE**.

AMEC is a new multi-stage solver macro, not a new stable-AC equivalence
principle. Its proof composes Lemma 11. Uppercase letters denote inverses.

## Theorem

Let

\[
P=\langle B,G\mid R\rangle
\]

be a balanced presentation of the trivial group, with
\(G=(g_1,\ldots,g_k)\). At stage \(i\), choose a fresh generator \(z_i\)
and a word \(u_i\) in the generators that currently survive.

1. By inverse Lemma 11, add \(D_i=z_i^{-1}u_i\).
2. Supply compressed relators whose re-expansion
   \(z_i^{\pm1}\mapsto u_i^{\pm1}\) recovers the current relators up to free
   reduction, cyclic orientation, and inversion. The displayed fresh-letter
   occurrences mechanically determine the AC1--AC3 substitution ledger.
3. In the resulting current tuple, designate a relator \(q_i\) having a
   cyclic orientation
   \[
   g_i^{-1}e_i,
   \]
   where \(e_i\) is free of \(g_i\).
4. Apply Lemma 11 forward, remove \(g_i\), and substitute \(e_i\) in every
   retained relator before checking stage \(i+1\).

After the declared acyclic order eliminates \(g_1,\ldots,g_k\), let \(S\)
be the actual retained tuple produced by these dynamic stages. Then

\[
P\sim_{SAC}\langle B,Z\mid S\rangle.
\]

The admissibility test is dynamic: each isolator is checked after all earlier
substitutions and free reductions. A static occurrence graph alone is not a
certificate.

### Proof

At each stage, inverse Lemma 11 preserves stable AC equivalence and triviality.
Replay that stage's certified visible ledger. The dynamic hypothesis puts
\(q_i\) in Lemma-11 form, so forward Lemma 11 removes \(g_i\) and substitutes
\(e_i\) in every retained relator. Induction follows the declared order and
produces exactly the recorded current tuple at every stage. No stable-AC
conclusion is assumed as a premise.

For \(k=1\), a non-inert definition gives the ordinary one-stabilizer CoV
corridor. Plain Lemma 11
\(\langle X,g\mid R,g^{-1}w\rangle\to\langle X\mid R[g\mapsto w]\rangle\)
is included literally up to an inert pair: add `z` with relator `Z`, use the
already-present `g^-1 w` as the eliminator, and delete the surviving inert
`z|Z` pair. AMEC therefore contains Lemma 11 and allows arbitrarily many
dependent stages.

## Bound

For an explicit normal witness

\[
v=\prod_j a_j\rho_{\lambda_j}^{\epsilon_j}a_j^{-1},
\]

use the model-explicit estimate

\[
A(W)=\sum_j\left(2|a_j|+1+2\mathbf1_{\epsilon_j=-1}\right)
\leq\sum_j(2|a_j|+3)
\]

in the atomic model with single-letter conjugations. If `c_visible` is the
length of the replayed compression ledger and `s_i` is the replay cost of the
substitutions performed during elimination \(i\), then a certificate-level
bound is

\[
C_{AMEC}\le c_{visible}+
\sum_{i=1}^k\bigl(A(W_{def,i})+2+s_i+A(W_{elim,i})+2\bigr),
\]

plus separately logged orientation and relabeling moves. There are \(2k\)
hidden Lemma-11 uses: \(k\) inverse additions and \(k\) eliminations.

The `aca_120` certificate below does not materialize the four normal
factorizations. Without those explicit witnesses, its cost is
witness-dependent and the proof supplies no effective input-visible numeric
bound. A rigorous uniform
fallback still exists: fix a prefix-free universal machine and a finite atomic
stable-AC alphabet. Breadth-first proof search from the certified endpoints
halts by the theorem, so

\[
d_{SAC}(P,Q)\le BB_U(c_U+|\operatorname{enc}(P,Q)|).
\]

This fallback is rigorous and noncomputable.

## Exact `aca_120` application

Start with

\[
P=\langle x,y\mid
\mathtt{YXXXYxx},\ \mathtt{YYYYXyyyx}\rangle.
\]

### Stage 1

Add \(z=xy\), with defining relator `Zxy`. Compress `YX` to `Z`:

\[
(\mathtt{YXXXYxx},\mathtt{YYYYXyyyx},\mathtt{Zxy})
\longrightarrow
(\mathtt{ZXXYxx},\mathtt{YYYZyyyx},\mathtt{Zxy}).
\]

The second relator has the cyclic form

\[
\mathtt{xYYYZyyy},
\]

so it isolates

\[
x=\mathtt{YYYzyyy}.
\]

Eliminating \(x\) gives

\[
(\mathtt{ZYYYZZYzzyyy},\mathtt{ZYYYzyyyy}).
\]

### Stage 2

Add \(t=y^3\), with defining relator `Tyyy`. Compress `YYY` to `T` and
`yyy` to `t`:

\[
(\mathtt{ZYYYZZYzzyyy},\mathtt{ZYYYzyyyy},\mathtt{Tyyy})
\longrightarrow
(\mathtt{ZTZZYzzt},\mathtt{ZTzty},\mathtt{Tyyy}).
\]

The first relator rotates to `YzztZTZZ`, so

\[
y=\mathtt{zztZTZZ}.
\]

Eliminate \(y\):

\[
(\mathtt{ZTztzztZTZZ},\mathtt{TzztZZZTZZ}).
\]

Finally relabel \(z\mapsto x\), \(t\mapsto y\):

\[
Q=\langle x,y\mid
\mathtt{XYxyxxyXYXX},\ \mathtt{YxxyXXXYXX}\rangle.
\]

The exact simultaneous Whitehead minima are

\[
\mu(P)=16,\qquad
\mu(Q)=15.
\]

The target minimum representative is

```text
YXXyxYx | YYYXyyxx
```

with witness `x -> Y`, `y -> yyx`. Since the minima differ, `P` and `Q` are
not in the same `Aut(F_2)` orbit.

All 40 valid seam substitutions and all 156 unrestricted one-step cyclic
product substitutions from `P` have minimum floor 19. The ordinary 50,000-node
search with relator cap 24 never goes below 16. The exhaustive one-stabilizer
CoV audit covers 104 cyclic words, 178,256 variant attempts, and 191 endpoint
orbits; its minimum is 16 and it has zero hits in `Q`'s orbit. Audit SHA-256:

```text
18fda8dc5e0a6ae60a8920ccd5bcc2b466d3962805932b41442ea3097948da8e
```

Thus the two-stage AMEC branch reaches a non-automorphic orbit that neither a
single substitution nor any audited one-stabilizer CoV action reaches.

## Domain and endpoint novelty

AMEC is logically applicable to every provenance-certified trivial input. The
identity corridor adds `Zx`, `Ty`, eliminates `x`, `y`, and relabels `z`, `t`
back to `x`, `y`. Those branches are automorphic and harmless. The action
family is not exhausted by automorphic branches: `aca_120` is an exact
counterexample.

## Verification

- Implementation: `experiments/stable_ac/supermoves/amec.py`
- Focused tests: `tests/stable_ac/test_amec.py`
- Independent certificate: `.scratch/aca120_two_block_certificate.json`
- Exhaustive one-stage audit: `.scratch/aca120_exhaustive_single_cov_allwords.json`

The implementation requires trusted triviality provenance, dynamically
re-expands every compressed relator, checks each current isolator, performs the
substitutions, and reproduces the endpoint word for word.
