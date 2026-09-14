# Rank-increasing stable compression: gain, bounds, and lookahead

The statements below concern balanced presentations of the trivial group and
count the freely reduced lengths of **all** current relators. Uppercase letters
denote inverses. The stable-certificate interpretation is exactly that of
[`STABLE_CERTIFICATE_CONVENTIONS.md`](../theory_patterns_20260912/STABLE_CERTIFICATE_CONVENTIONS.md).
These are compression statements, not new solves of any census row.

## 1. Exact gain, including the defining relator

Let the current rank be `r`, total length `L`, and let `w` be a nonempty freely
reduced word of length `m` in the current generators. Introduce a fresh `z`
with defining relator `D = Z w`. Choose `T` pairwise nonoverlapping occurrences
of `w` or its inverse across the **preexisting** relators, including any older
helper relators. Replace these by `z` or `Z`, retaining `D` unchanged. Cyclic
occurrences are allowed after choosing a cut in each cyclically reduced relator.
The resulting length and net gain are exactly

\[
 L'=L+(m+1)-T(m-1),\qquad
 \Delta=L-L'=T(m-1)-(m+1)=(T-1)(m-1)-2.
\]

Each replacement removes `m` letters and inserts one; the new defining
relator costs `m+1`. There is no hidden free cancellation: a fresh letter
cannot cancel with an old letter, and adjacent opposite new letters would
come from adjacent `w w^-1` or `w^-1 w`, impossible in a reduced input. Also
`Z w` is reduced. The defining relator's own displayed `w` is **not** an extra
replacement opportunity: replacing it using itself would erase the donor.

For `m=1` the gain is always `-2`. For `m>=2`, strict gain requires

| Defining length | Minimum number of selected occurrences |
|---|---:|
| `m=2` | 4 |
| `m=3` | 3 |
| `m>=4` | 2 |

The neutral cases are exactly `(m,T)=(2,3)` and `(3,2)`. In particular, the
two-occurrence gain is `m-3`. Reapplying the calculation at a later rank is
legitimate, but the next tuple need not contain any word meeting this threshold.
Additional reductions or basis changes can give further gains; the formula
then describes the literal boundary before those operations.

## 2. A fixed tuple cannot support unlimited strict rank increases

Suppose `k` successive completed compressions each increase rank by one and
decrease total length by at least one. Starting at `(r0,L0)` gives
`r_k=r0+k` and `L_k<=L0-k`. Thus even without algebraic hypotheses, integer
length gives `k<=L0`.

If the exponent-sum matrix has full rank `r_k` over the rationals, every
relator is nonempty, so `L_k>=r_k`. Consequently

\[
 k\le\left\lfloor\frac{L_0-r_0}{2}\right\rfloor.
\]

Equivalently, the nonnegative potential `L-r` decreases by at least two at
every strict compression. This latter proof also permits intervening
length-nonincreasing operations at fixed rank and the implementation's strict
singleton deletions: such a deletion removes one generator and at least one
letter, so it cannot increase `L-r`.

If there are no intervening rank decreases and the final tuple has no
one-letter relators, then `L_k>=2r_k`, improving the bound to

\[
 k\le\left\lfloor\frac{L_0-2r_0}{3}\right\rfloor.
\]

For trivial-group inputs the exponent matrix is unimodular, a stronger
hypothesis than rational full rank. A tuple with `r` relators all of length
two has every row sum even modulo two, so its exponent matrix annihilates
the all-ones vector modulo two and cannot be unimodular. A singleton-free
trivial-group tuple therefore satisfies `L>=2r+1`, giving

\[
 k\le\left\lfloor\frac{L_0-2r_0-1}{3}\right\rfloor.
\]

Here “singleton-free” means no one-letter **relator**. If instead it means
every generator occurs at least twice in the entire tuple, the same length
lower bound follows by counting columns; unimodularity again rules out every
column having exactly two occurrences. Do not use either singleton-free bound
through unrestricted deletions without adjusting the rank accounting.

If neutral/uphill compressions are admitted, strict descent alone no longer
bounds their number. A fixed accepted-boundary length ceiling `B` still gives
`r<=B`, or `r<=floor((B-1)/2)` at singleton-free trivial-group boundaries.
These are bounds for a fixed input/ceiling, not a universal rank bound over
arbitrarily long input presentations. Every definition temporarily increases
length by `m+1` before substitution, and its elementary realization may rise
much further: “strict compression” refers to the completed macro boundary.

**Arbitrarily long finite chains do exist.** For any integer `k>=1`, start
with the singleton-free trivial pair

\[
 ((xy)^{4^k}x,\;xy).
\]

Define `h1=(xy)^2`, and then `h_j=h_(j-1)^4` for `j=2,...,k`, compressing
all four-letter blocks in the first relator at each step. Its new-token
occurrence count at step `j` is `T_j=2*4^(k-j)`. Every defining word has
length four, so the gain is `3*T_j-5>=1`; the last step gains exactly one.
The final tuple has `k` defining relators of length five, the relator
`h_k^2 x` of length three, and `xy` of length two: rank `k+2`, total length
`5k+5`. Its initial length was `2*4^k+3`. Triviality follows directly from
`xy=1` and the first relator becoming `x`. This explicit family proves that
rank3, rank4, rank5, and arbitrarily high finite-rank strict chains are
possible. It says nothing about whether a particular short hard input admits
the next step, and it uses increasingly long starting words as `k` grows.

## 3. Two verified lookahead examples

All words in this table are freely and cyclically reduced. Every displayed
tuple has no one-letter relator and has exponent determinant `+1` or `-1`.

| Case | Relator tuple | Rank | Total length |
|---|---|---:|---:|
| Neutral start | `(xyXXYxxyXXYxx, xxy)` | 2 | 16 |
| Define `z=xyX`, replace twice | `(ZxyX, zXYxzXYxx, xxy)` | 3 | 16 |
| Define `u=zXYx`, replace twice | `(UzXYx, ZxyX, uux, xxy)` | 4 | 15 |
| Uphill start | `(xxyyyXYxxyyyXYY, xyy)` | 2 | 18 |
| Define `z=xx`, replace twice | `(Zxx, zyyyXYzyyyXYY, xyy)` | 3 | 19 |
| Define `u=zyyyXY`, replace twice | `(UzyyyXY, Zxx, uuY, xyy)` | 4 | 16 |

Triviality is independent of the determinant check. In the first example,
`xxy=1` gives `y=x^-2`, and substituting in the first relator gives exactly
`x`. In the second, `xyy=1` gives `x=y^-2`, and the first relator becomes
`Y`. Thus the stable definition theorem applies in both cases.

The second step can therefore be profitable after a neutral or uphill first
step, including a net improvement after repaying the uphill cost. These
examples **do not** show that the first step was needed. Directly defining
`z=xyXXYx` in the first starting tuple gives `(ZxyXXYx, zzx, xxy)`, length13.
Directly defining `z=xxyyyXY` in the second gives `(ZxxyyyXY, zzY, xyy)`,
length14. Both beat the two-definition endpoint.

Verification used the existing `red`, `inv`, `cyclic`, and `tokenize` functions on these
two examples only, with independent permutation-formula determinants. It
asserted reduction, exact occurrence/gain counts, exact expansion back to
each previous tuple, and both stated quotient substitutions. No census search
was run for this note.

## 4. A two-step bypass theorem for pure literal compression

**Theorem.** Suppose a first literal compression defines `z=w`, uses `T>=1`
occurrences, and has gain `Delta1<=0`. A second literal compression, with no
intervening operations other than cyclic rotations, defines another fresh
generator `u=v` and has positive gain `Delta2`. Then a single literal
compression available in the original tuple has gain at least
`Delta1+Delta2`. The result concerns total length, not equality of endpoint
tuples or subsequent search opportunities.

**Proof.** Write `q=|v|`, and let `H` be the second step's selected occurrence
count. Positive gain implies `q>=2` and `H>=2`. There are two cases.

1. **`v` contains no `z` or `Z`.** Its selected occurrences in the compressed
   old relators lie outside the replaced `w` blocks and lift unchanged to the
   original tuple. Any selected occurrences in the new relator `Z w` lie
   inside its displayed `w`. Lift all of those disjoint occurrences into one
   of the first step's `T` original `w` blocks, reversing orientations if that
   block is `w^-1`. They remain disjoint from the other lifted occurrences.
   Thus the original tuple supports `H` replacements of the same word `v`,
   giving gain exactly `Delta2`, at least `Delta1+Delta2`.

2. **`v` contains `s>=1` occurrences of `z` or `Z`.** It cannot have one
   occurrence in `Z w` and another in a compressed old relator. Any subword
   of the cyclic word `Z w` of length at least two that contains `Z` includes
   a neighbor of `Z`; expanding `Z` to `w^-1` creates an adjacent inverse pair
   at that seam. The expansion of every subword of a compressed old relator
   is freely reduced, since it is a subword of the original reduced relator.
   The same argument applies to inverse occurrences. Also `Z w` contains
   only one fresh letter, so it cannot supply two disjoint occurrences itself.
   Since `H>=2`, all selected occurrences must lie in the compressed old
   relators. Expand `z=w` in `v` to obtain an old-generator word `V` of length
   `q+s(m-1)`; these expansions are reduced and remain disjoint. Directly
   compressing these `H` copies of `V` in the original tuple has gain

   \[
   \Delta_{direct}=\Delta_2+(H-1)s(m-1)\ge\Delta_2
                  \ge\Delta_1+\Delta_2.
   \]

This proves the claim. The hypothesis `T>=1` is essential to the first
case's lifting argument; adding an unrelated unused definition is outside
this statement. The theorem does not by itself prove a bypass for arbitrary
longer sequences of definitions. ∎

**Limitation.** An intervening Whitehead/Nielsen change or AC relator operation
can change the defining relator and destroy the literal expansion invariant
used in the proof. A new profitable pattern may then expand with cancellation
or fail to lift to disjoint original substrings. The theorem neither excludes
nor establishes useful uphill lookahead in that wider move set. A negative
literal screen, especially a bounded candidate screen, is not an obstruction
to stable AC shortening.

## 5. Certificate scope

The precise source is **Lemma11 (Substitution and Removal)** in
Shehper et al., *What makes math problems hard for reinforcement learning:
A case study*,
Section9.1, page43; its local text starts at
[`math_ml_paper_2408.15332.txt:2499`](/Users/avigyapaudel/Documents/surf/ACSolverX/literature/txt/math_ml_paper_2408.15332.txt:2499).
For a trivial-group presentation with a relator `y^-1 w`, where `w` avoids
`y`, it allows substitution of `w` for `y` in every other relator and removal
of that generator/relator pair, up to stable AC equivalence. Applying the
lemma in reverse certifies defining-word addition and compression. Its
statement permits arbitrary finite rank; the cost issue below is explicitly
identified after its proof.

For a known trivial presentation, the normal closure of the old relators is
the entire old free group. Hence `w` is a finite product of conjugates of signed
old relators. Strictly stabilize by `(z,z)`, invert its relator, and append this
normal product to obtain `Z w`, restoring each donor after use. Each literal
replacement then has the explicit donor-conjugation witness stated in the
certificate conventions. This proves finite stable AC realizability at every
rank, since defining-generator addition preserves the presented trivial group.

Knowing only unimodular abelianization does not supply the required normal
product. Nor does its existence give a useful expansion-size or runtime bound.
Until an explicit elementary move stream is emitted and replayed, the above
paths are **theorem-backed stable composites**, not fully expanded elementary
certificates. Their compression, rank bounds, and small-example verification
do not claim an ordinary rank-two AC solve.

## 6. A stronger proved macro: batch definitions and triangular removal

The following is a sufficient algebraic move at arbitrary rank, including
rank10 or rank11. Whether searching for its witnesses improves the current
census frontier is a separate, untested research question in this note.

1. Add finitely many helpers `h_i=w_i`, with each `w_i` using only the original
   generators and earlier helpers. Retain all defining relators. Substitute
   checked blocks, or accept templates whose expansions freely equal the
   previous relators. Exact expansion supplies a check of these substitutions;
   Lemma11 supplies finite stable realizability of each addition.
2. Choose distinct relator slots and distinct pivot generators `a_1,...,a_p`
   such that the assigned relator contains its pivot exactly once, with either
   sign. Rotate/invert it to the form `a_i^-1 e_i`, where `e_i` avoids `a_i`.
3. Draw an edge `i -> j` when `e_i` contains `a_j` with either sign. If this
   dependency graph is acyclic, eliminate sinks first, using Lemma11 at
   each removal, and substitute in **every** remaining relator and definition.

**Proof of the removal criterion.** A sink's right-hand side uses none of the
other pivots. Substituting it therefore preserves the single occurrence of
every remaining pivot in its assigned donor. Remove that sink, and repeat
on the smaller DAG. Induction yields an explicit substitution expression for
each removed generator in the surviving generators, and every rank decrease
is justified by Lemma11 on the current trivial presentation. No invertibility
claim about an exponent matrix is used. Starting with rank `r`, adding `q`
helpers and removing `p` pivots ends at rank `r+q-p`. Recompute the full final
words and length; the resulting gain has no occurrence-count shortcut in
general because the substitutions can either cancel or expand considerably.

The dependency test is only sufficient. A directed cycle means this particular
elimination order is not certified; it does not prove the equations cannot be
solved by another sequence. A useful search can try different row/pivot
matchings in the graph whose edges record **exactly one letter occurrence**.
An inverse pair of “add helper, remove the same helper unchanged” is valid
but unproductive; compare complete resulting tuples before calling it progress.

**Why signed exponent matrices do not suffice.** The word `xxyXY` has exponent
vector `(1,0)` but is not primitive in `F(x,y)`. Its one-relator quotient has
relation `y x y^-1=x^2` and surjects onto the nonabelian group `S3` by
`x=(123)`, `y=(12)`. A primitive one-relator quotient of `F2` would be infinite
cyclic, so such a surjection is impossible. Even the full pair
`(xxyXY,xy)` is a trivial-group presentation with unimodular exponent matrix:
`xy=1` makes its first relator `x`. Thus triviality and a unit pivot exponent
do not make a proposed donor a one-occurrence isolator or a primitive word.

## 7. Complementary search direction: partial-basis extraction

Instead of always minimizing the length of the **whole** tuple, choose a
relator or small subtuple and seek an explicitly recorded ambient automorphism
that sends those words, after cyclic conjugation, to distinct signed
generators. Apply that automorphism to the whole tuple, then clear and delete
the resulting singleton donors. The legality follows from the recorded basis
change and strict singleton deletion; a basis change may increase total length
yet make the subsequent deletion profitable. This falls outside the two-step
literal bypass theorem.

Only a witnessed free-basis image is accepted. A full-rank or unimodular
exponent submatrix is not a witness, as the example above demonstrates.
If `r-1` selected relators of a rank-`r` trivial presentation become distinct
generators, these deletions leave a rank-one trivial presentation. Its one
freely reduced relator must be the surviving generator or its inverse, since
its exponent is `+1` or `-1`. This gives a sufficient **solve** gate once the
actual automorphisms and deletions are certified; no hard input is asserted
to meet it here. Testing single-relator or small-subtuple Whitehead descent
with the existing cut machinery is a concrete candidate-generation strategy,
not a claim of complete primitive-subtuple detection or measured new coverage.
