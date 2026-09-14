# Rank-three unimodular tuples of length at most twelve

**Proposition.** Let `P` be a freely and cyclically reduced balanced tuple on
three occurring generators. If its exponent-sum matrix has determinant
`+-1` and its total length is at most 12, some row contains exactly one
occurrence of a generator whose substitution and removal does not increase
the total cyclically reduced length.

This is a combinatorial statement about free words and exponent sums.
Calling the resulting move a theorem-backed stable AC transition additionally
requires the presentation to be known trivial, as in Lemma 11. Unimodularity
is not used as a substitute for that hypothesis.

## Preliminary reductions

For a generator of total unsigned degree `d` appearing once in a donor of
length `l`, literal substitution and deletion give the upper bound

\[
\Delta L\leq(d-2)(l-2)-2. \tag{1}
\]

Indeed, remove the donor's `l` letters and replace the other `d-1`
occurrences by a word of length `l-1`; free and cyclic reduction only lower
the result. Suppose, for a contradiction, that every possible one-occurrence
removal increases length.

Every generator then has degree at least three. Degree one is immediately
removable by (1). If a degree-two generator occurs in two rows, (1) again
applies. If both occurrences are in one row, its entire exponent column is
even, contradicting unimodularity.

Every row has length at least three. An empty row gives determinant zero;
a length-one row is removable. A cyclically reduced length-two row either
has two distinct singleton generators and is removable by (1), or is a
proper square whose exponent row is even.

A length-three row cannot be a cube, since its exponent row would be
divisible by three. It cannot contain all three generators once, since (1)
would require each of their degrees to be at least five. Consequently it
has the form `g h^2` after cyclic rotation, row inversion and signed
generator choices. Its singleton `g` has degree at least five.

There is at most one length-three row. Two such rows with different
singleton generators require degrees at least `5+5+3=13`. With the same
singleton generator, their exponent rows are identical modulo two.

If there were no length-three row, the only possibility at total length
at most twelve would be three length-four rows. Their exponent rows all
annihilate `(1,1,1)` modulo two, so the determinant is even. Therefore the
only possible remaining row lengths are `(3,4,4)` or `(3,4,5)`, and we
normalize the first row to

\[
R_1=g h^2.
\]

All these signed permutations and cyclic changes preserve the existence
and length change of a one-occurrence removal.

## Total length eleven

The degree vector must be `(d_g,d_h,d_k)=(5,3,3)`. Only one occurrence of
`h` remains outside `R_1`, and it lies in a length-four row. Equation (1)
gives `Delta L<=0`, the required contradiction.

## Total length twelve

The possible degree vectors are `(6,3,3)`, `(5,3,4)` and `(5,4,3)`.
Write `R_2` for the length-four row and `R_3` for the length-five row.
A row whose three unsigned generator counts are all even has an even
exponent row and is excluded throughout.

### Degrees `(6,3,3)`

The sole remaining `h` must lie in `R_3`; otherwise its length-four
removal satisfies (1). Thus `R_2` contains only `g,k`. It cannot have
one `k`, since `d_k=3` would give a nonincreasing length-four removal.
Zero or two occurrences give an even exponent row. The only remaining
form is `g^epsilon k^(+-3)`. All three `k` occurrences then lie in this
row, making the exponent column divisible by three. This is impossible.

### Degrees `(5,3,4)`

Again the sole remaining `h` must lie in `R_3`. The only possible
length-four count patterns are `g^3 k` and `g k^3`.

In the first case, normalize `R_2=g^(3 epsilon) k`. The third row has
counts `(1,1,3)`, with exponent vector `(sigma,tau,u)`, where
`sigma,tau=+-1` and `u` is odd. The determinant is

\[
2\sigma-\tau-6\epsilon u,
\]

whose absolute value is at least three.

In the second case, normalize `R_2=g^epsilon k^3`. The third row has
counts `(3,1,1)` and exponent vector `(v,tau,sigma)`, with `v` odd and
`tau,sigma=+-1`. Its determinant is

\[
6v-3\tau-2\epsilon\sigma.
\]

Absolute value one forces `v=tau=epsilon*sigma=+-1`. Invert `R_3` if
necessary so that `v=tau=1` and `sigma=epsilon`. Since the row is
cyclically reduced and has two positive and one negative `g`, its two
other letters must separate the negative `g` from the positive pair.
Thus, up to cyclic rotation, it is exactly one of

\[
g^2hGk^\epsilon,\qquad g^2k^\epsilon Gh.
\]

Solving these for `h` gives respectively

\[
h=G^2k^{-\epsilon}g,\qquad h=gk^{-\epsilon}G^2.
\]

In both cases `g h^2` becomes cyclically reduced length three: its
cyclic class is that of `k^-epsilon G k^-epsilon`. The length-four row
does not contain `h`, so deleting `R_3` leaves total length at most seven.
This is a strict decrease.

### Degrees `(5,4,3)`

The length-four row cannot contain exactly one `k`, by (1). If it contains
three, all `k` occurrences lie in a single cyclic triple, giving an exponent
column divisible by three. Even-count patterns are also impossible. This
leaves only the patterns `g^3 h` and `g h k^2`.

For `g^3 h`, write the exponent vector of `R_2` as `(3 epsilon,delta,0)`.
The third row has counts `(1,1,3)`, so its `k` exponent `u` is odd. The
determinant is `u(delta-6 epsilon)`, never `+-1`.

Consider `g h k^2`. Write the exponent rows as

\[
(1,2,0),\quad(\epsilon,\delta,2\eta),\quad(v,\tau,\sigma),
\]

where `epsilon,delta,tau,sigma=+-1`, `eta` is `0,+-1`, and `v` is
`+-1` or `+-3`. The determinant is

\[
(\delta-2\epsilon)\sigma+2\eta(2v-\tau). \tag{2}
\]

If `eta=0`, unimodularity forces `delta=epsilon`. The two oppositely
signed `k` letters must be separated in a cyclically reduced row. After
inverting the row if necessary, it has the form

\[
R_2=g k^\alpha h k^{-\alpha},\qquad\alpha=\pm1.
\]

Its singleton `h` gives `h=k^-alpha G k^alpha`. The two adjacent copies
of `h` in `R_1` cancel their intervening conjugators, so `R_1` becomes
length at most five. The third row has one `h`, and substitution increases
its length from five to at most seven. Deleting `R_2` therefore leaves
total length at most `5+7=12`, a nonincrease.

If `eta=+-1`, invert `k` to make `eta=1`. Simultaneously inverting `g,h`
and, when needed, inverting/rotating `R_1` allows `epsilon=1` while keeping
`R_1=g h^2`. Equation (2) becomes

\[
(\delta-2)\sigma+4v-2\tau.
\]

For either `delta=+-1`, absolute value one forces `v=tau=sigma=+-1`.
Invert `R_3` to make all three positive. Its cyclic shape is again
`g^2 h G k` or `g^2 k G h`, by the same separation argument above.
Removing its singleton `h` sends `R_1` to cyclic length three. The
length-four row contains one `h`, so it becomes length at most seven.
The resulting total is at most ten, a strict decrease.

Every possible case contradicts the assumption that all removals increase
length. This proves the proposition. In particular, a rank-three normalized
unimodular tuple with no nonincreasing one-occurrence removal has total
length **at least thirteen**. No claim of sharpness at thirteen is made.

## Independent finite word check

`rank3_low_length.py` implements free reduction, cyclic canonicalization,
the integer determinant and literal one-occurrence substitution directly;
it does not call the search or removal implementation. The five residual
unsigned count cases above are expanded into all freely and cyclically
reduced signed words, modulo row inversion and cyclic rotation. This gives
532 candidate presentations, of which 76 are unimodular. All 76 have a
replayed nonincreasing removal. The program performs 92 removal candidate
checks, for 624 combined presentation/removal checks. The full witnesses are
saved in `rank3_low_length.json` using the gapped basis `(101,307,10^20)`.

This finite check confirms the residual word classifications and actual
cancellations; the proof explains why no other length-at-most-twelve
configuration needs enumeration. These are combinatorial test tuples, not
a claim that every unimodular example is known to present the trivial group.

## A neutral removal can be necessary

The statement cannot replace "nonincreasing" by "strictly decreasing".
Consider the cyclically reduced length-twelve tuple

\[
(g h^2,\quad g k h K,\quad g^3 H k).
\]

Its determinant is `-1`, and it is known trivial: the first row gives
`g=h^-2`, the second gives `k h K=h^2`, and the third gives `k=h^7`.
The latter commutes with `h`, so `h=h^2` and all generators are trivial.

There are exactly five singleton-removal choices. Removing `g` via the
first row gives total length 13. Removing `g` or `h` via the second gives
length 12 in either case. Removing `h` or `k` via the third gives lengths
16 and 13. All five substitutions are saved with gapped generator IDs in
`rank3_low_length_neutral_control.json`. Thus this tuple has no strict
singleton removal but has two neutral ones. This establishes the need for
the nonincreasing formulation; it does not establish sharpness of the
length-thirteen lower bound for tuples without any nonincreasing removal.
