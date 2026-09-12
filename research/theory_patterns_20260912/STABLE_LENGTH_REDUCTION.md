# What the shorter stable presentations prove

Let P=(R1,...,Rr) be a balanced presentation of the trivial group on r named
generators. Its length L is the sum of the lengths of **all** r relators.
The U124 inputs are known trivial-group presentations; whether their relator
tuples are AC-trivial is the unresolved question. These are different facts.

## The defining-word lemma

Let w be any word in the existing generators. Introduce a fresh generator z
and the relator D=z^-1*w. The resulting presentation is stably AC-equivalent
to P, without assuming the AC conjecture.

Proof. Group triviality means w lies in the normal closure of the old
relators. Thus w is a finite product of conjugates of old relators and their
inverses. Strictly stabilize by the new relator z, invert it, and append these
factors to obtain z^-1*w. To append a conjugated donor, temporarily invert
and conjugate that donor, multiply it into the recipient, and restore it.
Every operation is a standard AC move. Reverse the finite sequence for the
opposite direction. This proves existence of a finite stable path; it does
not provide a short normal-product expression or silently count that
expression as a single elementary move.

## Literal compression is an ordinary AC operation after that prefix

Suppose a relator has the form R=P*w*Q, where P and Q denote its surrounding
words. Replacing the displayed occurrence of w by z gives R'=P*z*Q and

    R^-1*R' = Q^-1*D^-1*Q.

For a negative occurrence, R=P*w^-1*Q and R'=P*z^-1*Q instead give

    R^-1*R' = Q^-1*z*D*z^-1*Q.

Each error is a single conjugated copy of D or D^-1. The restored-donor
procedure therefore implements each replacement using ordinary AC moves.
A cyclic cut before tokenization is an explicit relator conjugation. Repeating
this identity proves the entire compressed tuple equivalent, including when
blocks have negative signs or occur in different relators.

If M disjoint occurrences, each of length m=|w|, are compressed, then

    L_new = L + m + 1 - M*(m-1).

Here m+1 counts the full new defining relator. Each token saves m-1 letters.
Thus strict shortening occurs exactly when M*(m-1)>m+1 for the saved literal,
noncancelling tokenizations. Examples: a length-two block needs at least four
occurrences, while a length-four block needs at least two. Further free or
cyclic cancellation can only improve this bound, but must be recorded if used.

This proof applies recursively in a larger alphabet. Every new helper brings
its own defining relator, and all of them remain in the length sum. A strict
descent cannot continue indefinitely because total length is a nonnegative
integer. The implemented finite candidate set is not an optimizer over all
possible stable AC paths or all words with hidden cancellation.

## A real U124 example

For aca_59 the saved rank-two starting length is20. The audited helper
definition z=x*x gives the full presentation

    (Zxx, YZYzyz, YYYYxzzz).

Uppercase letters are inverses. The three lengths are3,6,8, totaling17.
The saved cyclic cuts and signed expansions reproduce the original two
relators exactly. This is a legitimate shorter stable presentation, not a
trivialization. Its literal subgroup has no cyclic complement, and testing
all90 rank-three Whitehead maps finds no strict total-length descent.

For aca_24, the original pair is

    (YYXXXYxx, YYYXXYXYx),

of total length17. Defining z=YYXX and using recorded cuts gives

    (ZYYXX, XYxxz, XYxYzY),

of total length16. A separately replayed21-elementary-move ordinary suffix,
including normalization, reaches

    (XXZYY, XXyxZ, XYzYZ),

of total length15. The first15-letter boundary occurs after17 suffix moves;
the last four only choose its canonical rotation. Donors are restored, and
the independent integer and string replay implementations agree at every
elementary state. The preceding defining-word step remains theorem-backed
rather than an emitted normal-product certificate.

## What is and is not measured

The final table keeps the archival initial length, the saved starting best,
the best rank-two length, and the best length at any rank separately. A
shorter intermediate tuple counts even if a later elimination produces a
longer rank-two endpoint. The all-rank minimum is only the best certified
boundary reached in this investigation, not a proved global minimum.

Compression alone does not demonstrate a smaller search tree or lower AC
distance. Adding generators also increases the move alphabet. In particular,
the production two-bit F2 engine cannot store these higher-rank tuples; these
experiments use explicit word lists and do not claim a production speedup.
Candidate words, word-image evaluations, heap pops, elementary moves, CPU
time and wall time are distinct quantities in the saved reports.

Proof conventions: `STABLE_CERTIFICATE_CONVENTIONS.md`.
Independent prefix audits: `stable_dictionary_independent_audit.md`,
`primitive_compression_independent_audit.md`,
`stable_rank3_ac_independent_audit.md`.
The generalized stabilization convention also appears in Section2 of
[Lackenby's thickenable-presentation paper](https://arxiv.org/abs/2606.06122).
