# Single-occurrence length/rank bounds: PASS with normalization stated

Let a nonempty freely reduced balanced tuple have r generators/relators and
unimodular exponent matrix. Suppose generator g occurs once in a donor of
length ell and d times in the whole tuple. Isolating g gives a word of length
at most ell-1. Removing the donor and substituting in the d-1 remaining
occurrences, before any further cancellations, yields

`Delta L <= (d-1)(ell-2)-ell = (d-2)(ell-2)-2`.

This includes ell=1: the isolated word is empty and the bound is -d. There
is no ell=0 donor with a single occurrence. For d=1 the bound is -ell; for
d=2 it is -2. If both occurrences of a degree2 generator were in one row,
its exponent-matrix column would be even, contradicting determinant±1.
Thus every degree1 or degree2 generator supplies a strict removal.

Consequently absence of a strictly shortening single-occurrence removal
implies every generator has degree at least3 and L>=3r. At equality every
degree is3 and some donor has length at most3. No row is empty. A freely
reduced pure row of length2 or3 has exponent gcd2 or3 and is excluded by
unimodularity. Hence that short row has a single-occurrence pivot. Its bound
is `ell-4<0`, a contradiction. Therefore

`no strict removal => L >= 3r+1`.

For the stronger condition that no nonincreasing removal exists, suppose
L=3r+1. Degrees are at least3, so each is at most4. For r>=2 the average row
length is below4; the same short-row argument supplies a pivot with ell<=3
and d<=4. If ell>=2 the displayed bound is at most0; if ell=1 it is -d.
This contradicts the stronger condition. Rank1 is separate: a freely reduced
one-generator unimodular word is a signed singleton and removes strictly.
Thus

`no nonincreasing removal => L >= 3r+2`.

The empty tuple is excluded. Free reduction or normalization must be explicit:
the unreduced rank1 word `x x X` has determinant1 and literal length3 but no
literal single-occurrence pivot. It reduces to x, where the strict removal is
available. This is why the unqualified statement on arbitrary stored strings
would be false.

Twenty-one small normalized unimodular rank2 tuples exercise50 symbolic
eliminations, including14 degree1 and24 degree2 checks. Two signed rank1
singletons and the unreduced counterexample are checked separately. These
are word-accounting controls, not group-triviality tests. Unimodularity does
not replace the known-trivial input hypothesis needed for the Lemma11 stable
AC interpretation. No literature-priority claim is made.

Reproduce with `verification_degree_bound_checks.py`; results and source hashes
are in `verification_degree_bound.json`. No census search was run.
