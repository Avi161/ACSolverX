# Retained-donor dictionary audit: PASS

The virtual donor tokens are exact aliases for retained nontarget relators.
They introduce no generators or defining relators into the presentation. If
the current expanded template is P D^s Q, multiplying the target on the right
by Q^-1 D^-s Q gives P Q. Deleting tokens from left to right leaves every later
suffix unchanged, so the original template suffix is the correct Q at each
step. Independent replay verifies the full product of these corrections.

The weighted automaton uses cost `(old-letter token count,total token count)`.
This is an additive nonnegative lexicographic objective, so the existing
saturation and exact-target geodesic argument applies. A completed query is
optimal for that fixed free-group dictionary objective. It does not establish
a shortest quotient-group word, nor does its first coordinate necessarily
equal the resulting target length after donor deletion and free reduction.

The independent plant has donor a and target b a b a b^-1 a. Its exact
dictionary optimum is `(3,6)`: every token image is one letter, and the target
has three surviving b letters and six total letters. Eight exact spelling
choices confirm attainment of both lower bounds. Deleting the donor tokens
then reduces the three old b tokens to the single letter b. This verifies the
additional-cancellation distinction directly on a known-trivial balanced pair.

A second plant checks multiple retained donors, signed aliases, and generator
IDs above10²⁵. The independent dispatcher checks all virtual token images,
donor indices, exact expansion, deletion order, signs, suffix conjugators,
stripped result, objective costs and work metadata. Four corrupted variants
are rejected. The resulting certificates are ordinary AC composites from
their selected source, with unchanged rank and retained donors; no Lemma11
hypothesis is needed for this suffix operation itself.

All ten saved pilot records independently replay and add zero strict gains
beyond their imported seeds. Their new probe costs exclude historical seed
discovery. A source already reached by stable moves still has a stable full
lineage; an ordinary suffix alone does not change that provenance.

No algebraic or correction-sign bug was found. Reproduce with
`verification_donor_relative_checks.py`; full events, pilot costs and hashes
are in `verification_donor_relative.json`. No census search was rerun.
