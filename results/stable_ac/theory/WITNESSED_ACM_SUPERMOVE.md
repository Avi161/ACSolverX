# The Witnessed ACM Supermove

> **Rejected for the requested Lemma-11-like role.** Every witnessed target
> below is accompanied by the complete ordinary AC1--AC3 path that produces
> it. Consequently this is only a bounded batch of naive AC/Two-Hump
> substitution moves. It has no hidden normal-area step, generator removal,
> or structural advantage comparable to Lemma 11. The 124-class census proves
> validity and orbit escape only; it provides no evidence of improved length
> reduction or search power.

## Verdict

This move satisfies the basic operational domain:

- it applies directly to every presentation in `aca_124.csv`;
- it needs no thickenability or triangulation certificate;
- it is not a change-of-variables/CoV move and introduces no `z=w` isolator;
- every target has an explicit ordinary AC1--AC3 replay;
- its finite action bounds can be raised arbitrarily; and
- its action family contains targets outside the input `Aut(F_2)` orbit.

The mathematical transformation is the ACM move of Panteleev--Ushakov, made
finite and proof-carrying by retaining a normal-closure witness. This is not a
new equivalence theorem. The new deliverable here is the exact bounded action
constructor, atomic compiler, verifier, and 124-class census. It does **not**
satisfy the stronger requirement of a genuinely new, Lemma-11-like supermove.

## The presentation arrow

Lemma 11 is normally used by changing rank:

\[
\langle x,y\mid r_1,r_2\rangle
\longrightarrow
\langle x,y,z\mid r_1,r_2,z^{-1}w(x,y)\rangle
\longrightarrow\cdots\longrightarrow
\langle x,y\mid r'_1,r'_2\rangle.
\]

The witnessed ACM move instead stays at the original rank. Choose a target
relator `i`, signs \(\epsilon,\delta_k\in\{\pm1\}\), a word \(c\), and a finite
list \((j_k,h_k,\delta_k)\) with \(j_k\ne i\). Define

\[
r_i^\star=
\operatorname{red}\!\left(
c^{-1}r_i^\epsilon c
\prod_{k=1}^{m}h_k^{-1}r_{j_k}^{\delta_k}h_k
\right).
\]

Then the exact supermove is

\[
\boxed{
\langle X\mid r_1,\ldots,r_i,\ldots,r_n\rangle
\xRightarrow{\operatorname{WACM}(i,\epsilon,c;(j_k,\delta_k,h_k))}
\langle X\mid r_1,\ldots,r_i^\star,\ldots,r_n\rangle .}
\]

For rank two, targeting `r2`, this reads

\[
\boxed{
\langle x,y\mid r_1,r_2\rangle
\longrightarrow
\left\langle x,y\ \middle|\
r_1,
\operatorname{red}\!\left(
c^{-1}r_2^\epsilon c
\prod_{k=1}^{m}h_k^{-1}r_1^{\delta_k}h_k
\right)
\right\rangle .}
\]

Thus `m` is the width of the supermove. There is no fixed maximum: raising
`m` and the conjugator-length cap strictly enlarges the finite action family.

## Independent soundness proof

Let

\[
N_i=\langle\!\langle r_j:j\ne i\rangle\!\rangle_F.
\]

Modulo \(N_i\), every appended factor vanishes. Hence

\[
r_i^\star=c^{-1}r_i^\epsilon c\quad\text{in }F/N_i.
\]

Therefore \(r_i^\star\) is conjugate to \(r_i^{\pm1}\) in the quotient by
the other relators. This is exactly the ACM criterion.

There is also a direct ordinary-AC proof. First invert `ri` when
\(\epsilon=-1\), then conjugate it letter-by-letter by `c`. For every factor:

1. temporarily invert `r[jk]` when \(\delta_k=-1\);
2. conjugate `r[jk]` letter-by-letter by `hk`;
3. multiply it onto `ri`;
4. undo the conjugation by `hk^-1`;
5. undo the temporary inversion.

The borrowed relator is restored after each factor. Induction over the factor
list gives exactly \(r_i^\star\), not merely an isomorphic presentation.
Consequently every witnessed ACM output is ordinary-AC-equivalent to its
input and therefore also stable-AC-equivalent. The proof uses no triviality,
balance, or thickenability assumption.

## Exact replay bound

In this repository's convention, AC3 conjugates by one generator letter. The
compiler emits exactly

\[
N=
[\epsilon=-1]+|c|+
\sum_{k=1}^{m}
\left(2|h_k|+1+2[\delta_k=-1]\right)
\]

atomic AC1--AC3 moves. This is an exact length for the emitted replay and an
upper bound on the minimum AC distance.

If \(m\le M\) and \(|c|,|h_k|\le H\), then

\[
N\le 1+H+M(2H+3).
\]

Unlike the unknown normal-area term in Lemma 11, this cost is read directly
from the certificate. The width and word caps may be made as high as compute
allows; soundness is unaffected.

## Exact `aca_0` application

Take the stored presentation

\[
P_0=\langle x,y\mid
r_1=\mathtt{YXXyxYx},\quad
r_2=\mathtt{YYYYYYXyxyX}
\rangle,
\]

where `X=x^-1` and `Y=y^-1`. Target `r2` and choose

\[
\epsilon=1,\qquad c=1,\qquad
m=1,\qquad h_1=X,\qquad\delta_1=1.
\]

Since \(h_1=X=x^{-1}\), the appended factor is

\[
h_1^{-1}r_1h_1=xr_1X.
\]

Therefore

\[
\begin{aligned}
r_2^\star
&=\operatorname{red}(r_2xr_1X)\\
&=\operatorname{red}(
\mathtt{YYYYYYXyxyX}\,
\mathtt{x}\,
\mathtt{YXXyxYx}\,
\mathtt{X})\\
&=\mathtt{YYYYYYXyXyxY}.
\end{aligned}
\]

So the exact presentation jump is

\[
\boxed{
\langle x,y\mid
\mathtt{YXXyxYx},\mathtt{YYYYYYXyxyX}
\rangle
\longrightarrow
\langle x,y\mid
\mathtt{YXXyxYx},\mathtt{YYYYYYXyXyxY}
\rangle .}
\]

Its complete three-move replay is:

1. conjugate `r1` by `X`:
   `YXXyxYx -> xYXXyxY`;
2. multiply the temporary `r1` onto `r2`:
   `YYYYYYXyxyX -> YYYYYYXyXyxY`;
3. conjugate `r1` by `x`, restoring it:
   `xYXXyxY -> YXXyxYx`.

The complete Whitehead invariant is different:

| state | Aut floor | complete representative |
|---|---:|---|
| source | 18 | `YXXyxYx | YYYYYYXyxyX` |
| target | 18 | `YXXyxYx | YYYYYYYXyxx` |

Thus the target is rigorously outside the source `Aut(F_2)` orbit even though
the orbit floors happen to be equal. A second independent Whitehead
implementation also separates them.

## The 124-class census

The bounded preflight used

\[
M=3,\qquad H=1,\qquad\text{beam}=96,
\qquad\text{per-relator cap}=80.
\]

Results:

| quantity | result |
|---|---:|
| classes tested | 124 |
| classes with at least one action | 124 |
| classes with a certified non-automorphic action | 124 |
| distinct generated actions | 40,876 |
| atomic replay failures | 0 |

Certificate payload:

```text
results/stable_ac/theory/aca124_witnessed_acm.json
SHA-256: aaad3046ef5d19bb044b1dafcf4b517b59c4d8577f4ceed75d9eac7b40088ace
```

This census proves applicability and orbit escape, not progress toward
trivialization. The action policy should retain both automorphic and
non-automorphic targets and rank them by the solver heuristic.

## Finite versus complete modes

`bounded_acm_successors` has two modes:

- `beam_size=N`: a finite heuristic top-`N` action family at every width;
- `beam_size=None`: exhaustive enumeration of normalized certificates within
  the stated width and factor-conjugator caps, modulo target conjugacy and
  relator inversion.

The generator normalizes the source conjugator `c` to the empty word. This
does not lose target conjugacy classes when the conjugator cap is allowed to
increase, because

\[
c r_i^\star c^{-1}
=r_i^\epsilon
\prod_k(h_kc^{-1})^{-1}r_{j_k}^{\delta_k}(h_kc^{-1}).
\]

For presentations with declared but unused generators, pass the ambient
generator alphabet explicitly. Beam pruning and a relator-length cap are
heuristics and make no completeness claim.

## Verification

- focused tests: `7 passed`;
- independent word-algebra property check: `10,000/10,000` certificates;
- independent advisor audit: `19,208` additional generated certificates,
  formula/replay/count agreement;
- exhaustive bounded audit on the toy pair: all `12/12` cyclic keys retained;
- full 124 census: `40,876` actions replayed, zero failures;
- two independent Whitehead implementations separate the displayed
  `aca_0` source and target.

Implementation:

```text
experiments/stable_ac/supermoves/certified_acm.py
experiments/stable_ac/supermoves/aca124_acm_census.py
tests/stable_ac/test_certified_acm.py
```

Primary source: Panteleev and Ushakov, *Conjugacy Search Problem and the
Andrews--Curtis Conjecture*, Section 1.2 for ACM moves and Section 2 for their
different pseudo-conjugacy-graph search implementation.
