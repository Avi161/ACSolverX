# A short-word recovery barrier in the AK(3) torus-knot quotient

Date: 2026-07-24

Status: **PROVEN** for every freely reduced recovery word of length at
most \(17\).  This is a bounded theorem, not a solution of stable AK(3).

## 1. Replace consequence syntax by a word equation

At the \(k=1\) compression root, put

\[
 a=x^3,\qquad R=x^3t^{-4}.
\]

The retained quotient is

\[
 G=\langle x,t\mid x^3=t^4\rangle.
\tag{1.1}
\]

Let \(U(x,t)\) be any freely reduced word satisfying

\[
 U=t\quad\text{in }G.
\tag{1.2}
\]

Then \(t^{-1}U\) belongs to the normal closure of \(R\).  By definition it
is a finite ordered product of conjugates of \(R^{\pm1}\).  Retain \(R\),
multiply those conjugates into the compressed relator

\[
 B_0=z^{-1}xt,
\]

and restore \(R\) after every temporary conjugation or inversion.  This
gives

\[
 B_U=z^{-1}xU
\]

by a signed AC sequence.

Restore the original power relator using
\(D=t^{-1}zxz^{-1}\), and remove \(z\) through

\[
 z=e_U:=xU.
\]

Thus every solution of (1.2) gives the stable endpoint

\[
 P(U)=
\left(
x^3e_Ux^{-4}e_U^{-1},\
t^{-1}e_Uxe_U^{-1}
\right)
\tag{1.3}
\]

with

\[
\mathrm{AK}(3)\sim_{\mathrm{st}}P(U).
\tag{1.4}
\]

This formulation contains every fixed rotation/conjugate syntax studied
above and is strictly broader than those particular families.

## 2. Exact normal form in \(G\)

The group (1.1) is the amalgamated product

\[
\langle x\rangle
*_{\langle x^3\rangle=\langle t^4\rangle}
\langle t\rangle.
\tag{2.1}
\]

Put

\[
c=x^3=t^4.
\]

The element \(c\) is central: it commutes with \(x\) because \(c=x^3\),
and with \(t\) because \(c=t^4\).

Choose coset representatives

\[
\{1,x,x^2\}
\quad\text{and}\quad
\{1,t,t^2,t^3\}
\]

for the amalgamated subgroup in the two cyclic factors.  The normal-form
theorem for amalgamated free products gives a unique expression

\[
c^k s_1s_2\cdots s_r,
\tag{2.2}
\]

where:

- each \(x\)-syllable is \(x\) or \(x^2\);
- each \(t\)-syllable is \(t,t^2\), or \(t^3\); and
- consecutive syllables come from different cyclic factors.

To update (2.2) by one input letter, combine it with the final syllable
when they lie in the same factor, divide its exponent by \(3\) or \(4\),
move the quotient into the central exponent \(k\), and retain the
nonzero residue.  This is exactly the algorithm in

`experiments/stable_ac/rank3_compression/recovery_word_equation.py`.

Consequently,

\[
U=t\text{ in }G
\iff
\operatorname{NF}(U)=(0;(t,1)).
\tag{2.3}
\]

This is an exact equality test, not a bounded relator-rewrite heuristic.

## 3. Complete length-\(17\) census

There are

\[
\sum_{\ell=1}^{17}4\cdot3^{\ell-1}
=258{,}280{,}324
\tag{3.1}
\]

freely reduced nonempty words over \(x^{\pm1},t^{\pm1}\) of length at
most \(17\).  Applying (2.3) gives exactly \(40{,}503\)
recovery words:

| \(|U|\) | recoveries \(U=t\) in \(G\) |
|---:|---:|
| 1 | 1 |
| 6 | 4 |
| 7 | 2 |
| 8 | 16 |
| 9 | 38 |
| 10 | 68 |
| 11 | 114 |
| 12 | 308 |
| 13 | 788 |
| 14 | 1,748 |
| 15 | 4,040 |
| 16 | 10,028 |
| 17 | 23,348 |

There are no recovery words of lengths \(2,3,4,\) or \(5\).

The implementation performs this exhaustive test by splitting a word
into two freely reduced halves.  It indexes the normal form of every
right half and, for a left half \(L\), joins exactly the states

\[
\operatorname{NF}(L^{-1}t),
\]

excluding inverse cancellation at the seam.  This meet-in-the-middle
join is equivalent to testing all words in (3.1), not a sampling or beam
search.

For each of the \(40{,}503\) recovery words, construct (1.3), relabel \(t\) as
\(y\), and apply all rank-two Whitehead descents.  Whitehead's
strict-reduction theorem makes the resulting total cyclic length the
complete Aut(\(F_2\))-floor.

The minimum floor at each represented word length is:

| \(|U|\) | minimum \(\mu(P(U))\) |
|---:|---:|
| 1 | 14 |
| 6 | 23 |
| 7 | 15 |
| 8 | 29 |
| 9 | 33 |
| 10 | 25 |
| 11 | 30 |
| 12 | 24 |
| 13 | 18 |
| 14 | 29 |
| 15 | 29 |
| 16 | 36 |
| 17 | 29 |

### Theorem 3.1

For every freely reduced word \(U\) of length at most \(17\) satisfying
\(U=t\) in \(G\),

\[
\mu(P(U))\ge14.
\tag{3.2}
\]

Equality occurs only for the literal recovery

\[
U=t.
\tag{3.3}
\]

In particular, no such recovery reaches the length-\(12\) theorem.

## 4. The complete low-floor stratum

Only six of the \(40{,}503\) endpoints have floor at most \(23\):

| floor | \(|U|\) | recovery \(U\) |
|---:|---:|---|
| 14 | 1 | \(t\) |
| 15 | 7 | \(x^{-3}tx^3\) |
| 17 | 7 | \(x^3tx^{-3}\) |
| 18 | 13 | \(x^{-6}tx^6\) |
| 20 | 13 | \(x^6tx^{-6}\) |
| 23 | 6 | \(t^{-3}x^3\) |

The first five entries lie on the already proved power-conjugated family
\(x^{3m}tx^{-3m}\).  The last lies on the fixed-rotation family.
Therefore the entire low-floor stratum through recovery length \(17\)
contains no mechanism not already covered by the infinite symbolic
theorems.

The smallest endpoint floor outside the literal root is \(15\), not
\(12\).  The best recovery at length \(12\) has floor \(24\).

## 5. Scope

The theorem classifies all raw freely reduced spellings \(U\) of length
at most \(17\), regardless of how many rotations, conjugates, inverse
blocks, or cancellations produced them.  It is broader than a bounded
search over a chosen consequence grammar.

It does not rule out:

- a recovery word of length at least \(18\) with floor at most \(12\);
- a route that changes the retained source relator before recovery;
- a nontrivial use of the defining relator \(D\); or
- a stabilization mechanism that does not eliminate \(z\) through one
  relator of the form \(z^{-1}xU\).

## 6. Independent replay

`tests/stable_ac/test_recovery_word_equation.py` checks:

1. the amalgam normal form against the defining relation and its inverse;
2. the complete list of shortest nonliteral recoveries;
3. all \(40{,}503\) recovery counts through length \(17\);
4. every endpoint floor;
5. the unique floor-\(14\) minimum and complete floor-\(\le23\) list; and
6. the minimum floor at every represented recovery length.

The replay is a word-equation census, not an AC graph search, and uses no
local search-node budget.
