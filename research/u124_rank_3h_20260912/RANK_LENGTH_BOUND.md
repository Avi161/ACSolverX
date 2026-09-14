# A rank bound after nonincreasing generator removal

Let `r` be the number of generators and relators in a balanced tuple. Let `L`
be its total freely and cyclically reduced length, including every defining
relator. Its exponent-sum matrix has one row per relator and one column per
generator. Assume this matrix has determinant `+1` or `−1`.

**Proposition.** If every possible substitution and removal using a generator
that occurs exactly once in a donor increases total length, then `L >= 4r`.

This is a free-word and integer-matrix statement. On the known trivial-group
U124 inputs, the substitutions are stable AC composites by Lemma 11. The
proposition does not infer group triviality from the determinant.

## Proof

Write `d(g)` for the total unsigned number of occurrences of a generator `g`.
If `g` occurs exactly once in a donor of length `l`, deleting that donor and
substituting its isolated word elsewhere gives

    change in L <= (d(g) − 2)(l − 2) − 2.

There are `d(g)−1` other occurrences, each replaced by at most `l−1` letters.
Subtracting the donor and these old occurrences proves the inequality; free
and cyclic cancellation can only improve it.

Consequently every occurring generator has degree at least three. Degree
one is removable. Degree two is removable if spread between two rows, and
otherwise its whole exponent column is even. Every row has length at least
three: empty rows make the determinant zero, length-one rows are removable,
and a cyclically reduced length-two row is either removable or a proper
square with an even exponent row.

Let `p` be the number of length-three rows, and `q` the number of length-four
rows. We need two parity observations.

1. Every odd exponent entry in a length-three row belongs to a generator of
   degree at least five. A pure cube is excluded by the determinant. In all
   other cases, an odd entry comes from a single occurrence, and the displayed
   inequality is nonpositive for degree at most four.
2. Every odd exponent entry in a length-four row belongs to a generator of
   degree at least four. A singleton of degree three is removable by the
   inequality. The only other possible odd count is three occurrences. If
   those are all its occurrences in the tuple, cyclic reduction with only
   one other letter forces their signs to agree. That whole exponent column
   is then divisible by three, contradicting the determinant hypothesis.

Over the field with two elements, all exponent rows are linearly independent.
The `p` length-three rows are supported on columns of degree at least five,
so there are at least `p` such columns. The `p+q` short rows are supported
on columns of degree at least four, so there are at least `p+q` such columns.
Summing generator degrees therefore gives

    L >= 3r + (p+q) + p = 3r + 2p + q.

The remaining rows have length at least five. Summing row lengths gives

    L >= 3p + 4q + 5(r−p−q) = 5r − 2p − q.

Adding the two inequalities proves `2L >= 8r`, as required.

There is also a constructive strengthening below the threshold: if `L < 4r`,
some pivot has the displayed **literal upper bound** at most zero. The proof
uses only positivity of those bounds, so the same counting contradiction
applies before testing any cancellation. Occurrence counters can select a
guaranteed nonincreasing removal immediately. At `L = 4r`, actual free-word
cancellation can matter; the rank-three length-twelve control in
`rank3_low_length_neutral_control.json` demonstrates that distinction.

## What this permits in U124

| Rank after all nonincreasing removals | Required total length |
|---:|---:|
| 4 | at least 16 |
| 5 | at least 20 |
| 6 | at least 24 |
| 10 | at least 40 |
| 11 | at least 44 |

The separate [rank-three argument](rank3_low_length.md) strengthens the bound
at rank three from twelve to thirteen. No sharpness is asserted.

At the current checkpoint every U124 incumbent has total length at most 21.
A strictly shorter endpoint, after all nonincreasing one-occurrence removals,
must therefore have rank at most five. This is **not an intermediate-rank
cutoff**: a path may pass through rank 10, 11 or higher and then return to a
shorter low-rank tuple. The successful rank-five detour for `aca_79` is a
concrete instance of that distinction.

Combining the general and rank-three bounds gives a useful small-length
corollary: **every normalized balanced unimodular tuple of total length at
most twelve can be reduced to rank at most two by nonincreasing
one-occurrence removals**. At rank at least four, use `L < 4r`; at rank three,
use the separate length-twelve proposition. Each step lowers rank, so the
process terminates. On known trivial-group inputs these are stable AC moves.
Consequently any strict shortening of a length-thirteen input, at any rank,
can be followed by such removals to obtain a rank-at-most-two presentation
of length at most twelve. This still gives no bound on the rank or length
needed along the path to that shorter tuple.

## Sharpness and an ordinary AC escape

The constant four is attained. With `[g,h]=g h g^-1 h^-1`, consider

    (g u^2, h v^2, u[h,g], v[g,h]).

This has rank four and total length sixteen. Every one of its four
one-occurrence removals gives length seventeen. It is nevertheless trivial:
the last two relations give `u=[g,h]` and `v=u^-1`; the first two then give
`g=u^-2` and `h=u^2`. These commute, so `u=1` and every generator is trivial.

There is a direct ordinary donor escape. Rotate `v[g,h]` to `[g,h]v` and
multiply it into `u[h,g]`. The inverse commutators cancel, leaving `uv`.
The total falls from sixteen to thirteen. Subsequent generator removals give

    (rank,length): (4,16) → (4,13) → (3,11) → (2,10) → (1,1) → (0,0).

The exact ledger and four adverse pivot checks are in `exchange_rank4_sharp.json`,
independently audited in `verification_sharp_rank4.json`. Disjoint copies on
separate generator sets give equality `L=4r` at every rank divisible by four.
This is a sharpness example for the removal bound, **not an AC counterexample**.
