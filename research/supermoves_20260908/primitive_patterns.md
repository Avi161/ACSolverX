# Primitive-donor and unimodular-block supermoves

All claims below concern ordinary elementary Andrews--Curtis moves on an
ordered pair: invert a relator, multiply one relator on either side by the
other, and conjugate a relator by an arbitrary free-group word.  A swap can be
implemented by the usual Nielsen word in inversions and multiplications, or
kept as a macro that the certificate compiler expands.

The compiler convention is `C_c(r)=c^-1 r c`.  Thus left conjugation by `g`
is encoded as `C_(g^-1)`.

## 1. Exact row subtraction for two-block relators

Let

```text
R = a^m b^n,       S = a^p b^q.
```

The integer row operation `(p,q) <- (p,q)-(m,n)` has the following ordinary
AC realization, with `R` restored at the end:

```text
invert R
S <- R S
invert R
C_(b^-n)(S)
```

Indeed, just before the conjugation,

```text
S = R^-1 S = b^-n a^-m a^p b^q
  = b^-n a^(p-m) b^q,
```

so `C_(b^-n)`, namely left conjugation by `b^n`, gives
`a^(p-m)b^(q-n)`.  The symmetric operation on `R` uses the same four moves
with the relators interchanged and encoded conjugator `b^-q`.  Row addition is
subtraction after replacing the source row by its negative.  To negate a block
row, invert its relator and then apply `C_(b^-n)`:

```text
(a^m b^n)^-1 = b^-n a^-m  ->  a^-m b^-n.
```

Thus every signed integer elementary row operation has an explicit ordinary
AC expansion and every intermediate relator can be returned to two-block
form.  Zero exponents and negative exponents require no special convention;
the displayed free reductions remain valid.

### Euclidean termination

If `mq-np = +/-1`, the exponent matrix

```text
M = [[m,n],[p,q]]
```

lies in `GL(2,Z)`.  Apply signed row negations so the two nonzero entries in
the first column have convenient signs, then repeatedly subtract the row with
smaller absolute first entry from the other (repeating a unit subtraction
rather than assuming multiplication by an integer is one AC move).  Ordinary
Euclid terminates with first column `(epsilon,0)`, up to swapping rows, because
`gcd(m,p)=1`.  The determinant condition then makes the lower-right entry
`delta=+/-1`.  The matrix is `[[epsilon,t],[0,delta]]`; repeated subtraction
of signed row 2 from row 1 removes `t`.  Negate rows if necessary.  This gives
the identity matrix, and the expanded row operations give an ordinary AC path
from `(a^m b^n,a^p b^q)` to `(a,b)`.

For a deterministic compiler, use Euclidean division only as a scheduling
optimization: emit `abs(k)` copies of the unit row-subtraction macro for a
quotient `k`, negating the source before and after when the required sign is
addition.  Re-canonicalize a negated row by the explicit conjugation above.
This avoids treating `row_i <- row_i-k row_j` as an elementary AC move.

Recognition should accept cyclic rotations and inverses of each block word.
Rotate to a boundary between the two maximal blocks; if an inverse is chosen,
record the inversion and conjugation witnesses rather than silently changing
the relator.  The determinant test is then exact over signed integers.

## 2. Transport through an ambient free-basis automorphism

Let `(u,v)` be a free basis of `F(a,b)`, and let `phi(a)=u`, `phi(b)=v`.
Applying `phi` to every word in the preceding certificate preserves each move:
inversion and multiplication are literal, while conjugation by `w` becomes
conjugation by `phi(w)`.  Therefore a block pair

```text
(u^m v^n, u^p v^q),       mq-np=+/-1,
```

is carried by ordinary AC moves to `(u,v)`.  Finish by expanding a Nielsen
factorization of the basis `(u,v)` back to `(a,b)`.  Nielsen generators are
relator inversions, swaps, and left/right multiplication, hence are ordinary
AC moves.  This last step is essential: a simultaneous ambient automorphism
must not itself be emitted as an AC move.

A recognizer therefore needs constructive data, not only a claim that `u` is
primitive: a complementary word `v` and a Nielsen/Whitehead reduction witness
for `(u,v)`.  The row-subtraction portion can then be transported mechanically.

## 3. Stronger primitive-donor elimination theorem

The two-block condition on the companion is unnecessary.

**Theorem.**  Suppose `(u,v)` is a free basis and `W` is any reduced word in
`u^+/-1,v^+/-1`.  If the exponent sum of `v` in `W` is `+/-1`, then `(u,W)` is
ordinary-AC trivial, constructively.

Write an occurrence as `W=A u^epsilon B`.  It can be deleted while restoring
the donor relator `u`:

* If `epsilon=+1`, temporarily apply `C_(A^-1)` to make the donor
  `A u A^-1`, invert it,
  and left-multiply `W`; free reduction gives
  `(A u A^-1)^-1 A u B = AB`.
* If `epsilon=-1`, temporarily apply `C_(A^-1)` to make the donor
  `A u A^-1` and
  left-multiply `W`; free reduction gives
  `(A u A^-1) A u^-1 B = AB`.

Undo the donor inversion when used and undo its conjugation after the
multiplication.  Repeating strictly decreases the number of `u` letters, so it
terminates.  The remaining word is `v^e`, where `e` is the original exponent
sum of `v`; by hypothesis it is `v` or `v^-1`.  Invert if needed, then Nielsen
reduce `(u,v)` to `(a,b)` as above.

This gives a useful compiler contract:

1. provide a basis witness `(u,v)` and parse the companion in that alphabet;
2. scan deterministically (for example, delete the leftmost `u^+/-1`);
3. emit the conjugate-donor deletion macro with the current prefix `A`;
4. verify that the residue is exactly `v^+/-1` after free reduction;
5. append the inverse Nielsen witness for the basis.

The condition is also forced by abelianization for a normally generating pair
with primitive first relator: in `(u,v)` coordinates, the determinant of the
two exponent rows `(1,0)` and `(e_u,e_v)` is `e_v`, hence must be `+/-1`.
Thus, among pairs whose first relator is primitive, this construction covers
every possible normally generating companion.

## 4. One-occurrence donors of arbitrary length

If a cyclically reduced donor contains `a` exactly once (with either sign), all
other letters are powers of `b`, so after choosing a cyclic cut it has form

```text
b^r a^epsilon b^s.
```

Conjugation/rotation and, when needed, inversion put it in
`a b^(epsilon*(r+s))` form up to a harmless signed choice of basis.  It is
primitive, with explicit complement `b`; elementary Nielsen subtraction of
the terminal `b` power reduces the basis to `(a,b)`.  The symmetric statement
holds when `b` occurs exactly once.

Consequently donors of lengths 5, 6, 7, and arbitrarily large length are
recognized uniformly: no finite pattern table is needed.  Once the companion
is rewritten in the donor/complement basis, exponent sum `+/-1` in the
complement triggers the elimination theorem.  For example, every
`u=a b^(d-1)` supplies a length-`d` donor family, and the companion may have
arbitrarily many alternating `u` and `b` syllables.

### Cheap mid-search specialization

For a normalized donor `u=a b^k` with complement `v=b`, no general basis
parser is needed.  Rewrite the companion by the literal inverse substitution
`a -> u v^-k`, `A -> v^k U`, leaving `b,B` as `v,V`, and freely reduce in the
`u,v` alphabet.  Its `v` exponent is equivalently

```text
exp_b(W) - k exp_a(W).
```

Hence the abelianization determinant already tests whether that exponent is
`+/-1`.  If it passes, the leftmost-occurrence deletion loop compiles a
certificate directly.  Signed variants (`a^-1 b^k`, or a unique `b`) are
handled by first recording the same inversion/rotation/signed-permutation
witness used to normalize the donor.  This makes the family suitable as an
`O(total word length)` recognizer after each selected search child; it need
not invoke a general Whitehead search.

## 5. Boundaries and genuinely separate families

* Primitive recognition alone is insufficient unless the compiler also
  obtains a complement and a basis-reduction witness.
* Exponent sum `+/-1` is a test in the donor/complement coordinates, not
  necessarily the exponent of a visible original generator.
* The deletion theorem is broader than unimodular two-block row reduction;
  the latter remains valuable because it supplies a very small certificate
  without expanding an arbitrary companion into basis coordinates.
* Relators such as proper powers cannot be primitive.  A determinant of
  absolute value other than one is an immediate abelianization obstruction to
  normal generation and must be rejected before certificate generation.
* A simultaneous automorphism of both relators is transport notation only.
  Certificates must contain the transported conjugators and the terminal
  Nielsen moves explicitly.

## 6. A distinct nonprimitive torus-donor family

Let `R=a^p b^q`, with `gcd(p,q)=1` and `pq != 0`.  When
`|p|,|q|>1` this donor is nonprimitive, so the following rule is separate from
primitive-donor elimination.  It is conditional; determinant one alone is not
sufficient for an arbitrary companion.

In the quotient by `R`, `a^p=b^-q`.  Every local use of this equality has an
ordinary AC expansion which restores `R`.  If `W=A a^p B`, temporarily make
the donor `D=A R A^-1` (encoded as `C_(A^-1)`), invert it, and left-multiply:

```text
D^-1 W = A b^-q a^-p A^-1 A a^p B = A b^-q B.
```

Undo the donor inversion and conjugation.  The other signed directions
`a^-p -> b^q`, `b^q -> a^-p`, and `b^-q -> a^p` follow by choosing the
appropriate conjugate of `R` or `R^-1`; a compiler should construct and freely
reduce the proposed multiplier, accepting it only when the requested local
replacement results.  Reversing a recorded rewrite macro is also valid.

The quotient is the amalgamated product

```text
<a> *_(a^p=b^-q) <b>.
```

With `z=a^p=b^-q`, choose fixed residue transversals modulo `|p|` and `|q|`.
Scan maximal alternating syllables, divide each exponent into a residue and a
power of `z`, collect the central powers, and merge adjacent same-generator
syllables.  This gives the unique reduced amalgam normal form
`z^k t_1...t_l`.  Collection is constructive: extracting a central power uses
the signed replacement macros above, while crossing it past the other factor
uses two such rewrites (change its representation, merge in the cyclic factor,
then change it back).  Record each unit rewrite; integer division is a schedule,
not a single work unit.

Choose a deterministic shortest Bezout pair `(r,s)` with
`p*s-q*r=+/-1`, and put `V=a^r b^s`.  If the recorded canonical normal forms
of an arbitrary companion `W` and either signed Bezout target `V` agree, then
`(R,W)` is ordinary-AC trivial: normalize `W`, reverse the normalization path
of `V`, and finish with the two-block Euclidean certificate.  This strictly
contains visible two-block companions, including words with separated donor
conjugates and central-power crossings.

Cheap mid-search specializations are useful before full normalization:

* If all but one alternating syllable are exact multiples of `p` or `q`,
  rewrite those syllables and merge; test the resulting two-block word.
* Explore a small charged cone of signed relation rewrites, testing every
  child with the two-block recognizer.  Each hit already has a certificate.

Require a full normal-form match or an explicit replayed rewrite trace.
Abelianized exponent equality is only a prefilter.  In particular, do not
claim that every determinant-one companion of a torus donor belongs to this
family.  For AC19 screening: detect a cyclic/inverse coprime two-block donor,
check determinant `+/-1`, try the exceptional-syllable reduction, then full
normalization, and only then a bounded rewrite cone.  Charge every inspected
occurrence and rewrite and independently replay the expanded elementary path.
