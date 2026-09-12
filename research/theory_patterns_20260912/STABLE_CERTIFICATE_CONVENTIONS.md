# Stable AC composites used in this investigation

The user explicitly authorized stable AC during this run. Throughout this
document the input is a **known presentation of the trivial group**. This
hypothesis is essential to the construction below; unimodular abelianization
alone is insufficient. The Miller–Schupp inputs have that hypothesis by
[Miller–Schupp, Theorem1 and Lemma2](https://www2.hcmuaf.edu.vn/data/file/Some%20presentations%20of%20the%20trivial%20group.pdf),
and the saved AC/automorphism equivalences preserve their groups.

Ordinary certificates use relator inversion, right multiplication by another
relator, and conjugation by a signed generator. Strict stabilization adds a
fresh generator z and its relator z; its inverse deletes such a pair when z
does not occur in any other relator.

## Adding a defining relator is a finite stable AC composite

Let the current relators be R_1,...,R_n in the free group on the old
generators, and let w be an old-generator word. Triviality says their normal
closure is the whole free group. Consequently there is a finite identity

    w = product_j c_j^-1 R_(i_j)^e_j c_j,    e_j in {-1,1}.

Add the strict stabilization (z,z), invert its relator to z^-1, and append
those factors using the old relators as temporary conjugated/inverted donors.
Restore each donor after its use. The new relator becomes z^-1 w exactly.
Every conjugation expands into finitely many generator conjugations.

This is constructive even when a short normal-product identity is unavailable:
enumerate finite products of conjugated signed relators and freely reduce
until w is obtained. The stated hypothesis guarantees termination. This
argument proves finite realizability; it does not provide a useful uniform
time bound or license reporting an unexpanded macro as one elementary move.

## Compression and deletion

Retain D=z^-1 w. In another relator P w Q, append the conjugate
Q^-1 D^-1 Q to replace the displayed w by z. Inverse occurrences have the
corresponding inverse/conjugate witness. Literal factorization can be replaced
by a freely equal template, provided its expansion is checked exactly.

Suppose a relator is a^-1 e, where e contains no a. Use it to substitute
a=e in every other relator, retaining that defining relator. Call the other
resulting relators T_1,...,T_(n-1); they contain no a. The presentation on
the remaining generators is still trivial, so e is a finite product of
conjugates of the T_i. Append the inverse product to a^-1 e, leaving a^-1.
Invert it to a and delete the strict generator-relator pair. This is the
reverse defining-generator construction, with finite ordinary operations
before the strict destabilization.

It follows that the isolator construction is valid: introduce z=w(a,b),
replace verified w-blocks so that one relator contains exactly one a^±1,
solve that relator for a as a word in b,z, and eliminate a. No assertion that
(b,w) was originally a free basis is needed. Arbitrary unrelated Tietze
transformations are not being admitted as AC moves.

## Ambient automorphisms

For example, to effect the ambient Nielsen change a -> a b on every relator,
introduce z=a b^-1. Its defining relator is conjugate/inverse to the defining
equation a=z b. Substitute and eliminate old a, then name the surviving z
as the new a. The resulting relators are exactly the requested images.
Inversions and generator permutations have analogous defining-generator
realizations. Decomposing a free-group automorphism into Nielsen changes
therefore gives a finite stable AC realization on these trivial-group inputs.
An explicit inverse for each recorded ambient map is checked separately.

## What the files certify and what the clocks measure

An ordinary `moves` stream has been replayed at generator level. A stable
defining-word record instead certifies exact template expansions, isolation,
substitutions and recorded free-basis inverses, with the lemmas above providing
its stable AC realization. It is labelled **theorem-backed stable composite**;
its possibly very long normal-product expansion has not been emitted unless
an additional elementary certificate file explicitly says so.

For every recorded state, total presentation length is the sum of the freely
reduced lengths of **all** current relators. A rank3 state is never scored by
silently discarding its defining relator. Final comparisons additionally record
the rank2 endpoint and its full words. Algebraic template-check times and macro
counts are not elementary-move lengths or end-to-end expansion times.
