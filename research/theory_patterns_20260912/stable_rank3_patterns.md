# A three-relator power-conjugacy corridor

Status: exact ordinary identities and two ordinary move segments independently
replayed by the adjacent tiny checker. The intervening rank-three basis change
is a theorem-backed stable AC composite on the known trivial-group inputs.
Its strict stabilization/normal-product expansion has not been emitted. This
is a BS entry theorem and includes explicit soluble subfamilies; it does not
solve `aca_24` or improve its certified total length 15.

The existing unimodular two-block and arbitrary-word substituted-kernel
methods already appear in `research/supermoves_20260908/SHORTCUT_CATALOGUE.md`.
They are not claimed as a new result here.

## The exact family

In the free group on x,y,z, let m,k,n be any integers and define

    D = z x^m y^n,
    I = z^-1 x^-m y x,
    C = z y^k z^-1 y x.

Zero and negative exponents are allowed; all displayed words denote their
free reductions. Ordinary AC operations, restoring I and C after donor use,
replace D by

    B = (x^-m z) y^k (z^-1 x^m) y^-n.                 (1)

Thus these three syntactically checkable relators expose a conjugacy of powers
in the genuine free basis x,y,t=x^-m z. No root extraction or nonprimitive
coordinate substitution occurs. In that basis the tuple is

    (t y^k t^-1 y^-n,
     t^-1 x^-2m y x,
     x^m t y^k t^-1 x^-m y x).                       (2)

Use the first relator in the third, then multiply the third by the inverse
of the second. The resulting tuple is

    (t y^k t^-1 y^-n,
     t^-1 x^-2m y x,
     x^m y^n x^m t).                                (3)

The elementary operations proving (1) do not require that the presented
group be trivial. The basis-change realization from (1) to (2) uses the
known-trivial-input stable convention in `STABLE_CERTIFICATE_CONVENTIONS.md`.
The abstract free-group automorphism itself is unconditional and has explicit
inverse: substitute old z=x^m t, with t=x^-m z.

The exponent matrix of (D,I,C), in column order x,y,z, is

    [m,     n,   1]
    [1-m,   1,  -1]
    [1,   k+1,   0].

Its determinant is k-n. Consequently any member presenting the trivial group
must have |k-n|=1. This is a necessary abelian condition, not a sufficient
triviality or AC assertion. In particular k=1,n=2 gives a BS(1,2) donor in (3).

## Explicit restored-donor identities

Use the convention that appending a signed donor J with conjugator q means
right-multiplication by q^-1 J^sign q. It is implemented by temporarily
inverting/conjugating J, multiplying the target, then restoring J.

Put Q=x^m y^n. Since D=zQ and I=z^-1 x^-m yx, appending Q^-1 I Q gives

    D1 = x^-m y x^(m+1) y^n.

Invert D1 and conjugate by y^-n to obtain

    K = x^-(m+1) y^-1 x^m y^-n.

Let A=z y^k z^-1 and Q2=x^m y^-n. The relation C=A yx and the exact identity

    (x^-1 y^-1)^-1 A = A^-1 C A

show that appending (A Q2)^-1 C (A Q2) to K replaces its displayed factor
x^-1 y^-1 by A. The result is exactly (1). This identity remains valid when
adjacent blocks cancel, so signed and zero parameters need no special parsing
exception.

For (2) -> (3), append the inverse of the first donor to the third with
conjugator y^n x^-m yx. This replaces t y^k t^-1 by y^n and gives
x^m y^n x^-m yx. Multiplying this by I^-1 then gives x^m y^n x^m t.
Every donor is restored. These operations use only inversion, multiplication
by a different relator, and conjugation by signed generators.

## Explicit soluble subfamilies

These are unconditional ordinary AC statements, not consequences of a
trivial-group assumption.

* If n=0 and |k|=1, (1) is a conjugate of y^k. Normalize it to y, clear y
  from I and C, and the latter two relators become z^-1 x^(1-m) and x.
  Clear x from the former and correct signs. This works for every integer m.
* If k=0 and |n|=1, (1) freely reduces to y^-n. The same cleanup works, with
  C becoming x after its y is removed. Again m is unrestricted.
* If m=0 and |k-n|=1, I=z^-1 yx lets one replace the final yx of C by z,
  obtaining z y^k. The other donor is D=z y^n. Invert D and append the
  modified C to D^-1; the result is y^(k-n). Normalize it to y, then clear
  y and z from the remaining two relators to obtain x and z. This covers
  arbitrary consecutive signed k,n.

For the third bullet, these operations are already in the original basis;
no stable coordinate change is needed. For nonzero m,k,n outside these
families, this note claims only the exact BS entry and normal form.

## Assessment of the actual `aca_24` seed

The root's recorded dictionary-plus-ordinary prefix supplies

    (XXZYY, XXyxZ, XYzYZ),       total 15, rank 3.

Here capital letters mean inverses. Invert and rotate the first relator,
rotate the second, and invert the third to get the family above at
(m,k,n)=(2,1,2):

    (zxxyy, ZXXyx, zyZyx).

The adjacent checker starts at the exact supplied seed, not at an assumed
oriented equivalent. Its 35 strict ordinary moves reach

    (XXzyZxxYY, ZXXyx, zyZyx),   total 19, rank 3.

The maximum sum of all three relator lengths over this fully expanded
ordinary segment is 27. The stable coordinate map old z=xx t gives

    (tyTYY, TXXXXyx, xxtyTXXyx), total 21, rank 3.

Eighteen further strict ordinary moves give (3), namely

    (tyTYY, TXXXXyx, xxyyxxt),   total 19, rank 3.

The maximum sum over that second expanded segment is 29. The possibly much
larger strict expansion and peak of the intervening stable ambient map are
not bounded here. The totals 21 and 19 retain all three relators, including
the relation descended from the added definition.

This does not beat 15, and no new solved input is claimed. It identifies a
real BS(1,2) entry after the new `aca_24` compression descent, rather than a
hypothetical family unrelated to the saved data.

## Why the rank-two BS terminal theorem does not finish this example

The two other relators in (3) each have exactly one stable letter t, but they
also contain the independent generator x. The quotient by the BS donor alone
is BS(k,n) free-product <x>, not a rank-two BS group. The rank-two theorem
requiring one companion with stable-letter exponent ±1 cannot simply be
applied to this three-generator tuple.

More precisely, for any tuple

    (t y^k t^-1 y^-n, t^-1 U(x,y), V(x,y)t),

ordinary substitution and theorem-backed defining-generator removal give the
exact two-generator endpoint

    (U y^k U^-1 y^-n, VU).

This is a checkable elimination identity, not a generic solution criterion.
For (3), U=x^-2m yx and V=x^m y^n x^m, so the second endpoint relator is
x^m y^n x^-m yx. Its persistent x occurrences are precisely what prevents
the usual one-variable terminal cleanup. No claim of impossibility or an
unbounded exclusion is made.

## Verification scope

`stable_rank3_patterns_check.py` replays both ordinary segments using a
separate stack decoder for all 216 triples m,k,n in {-2,-1,0,1,2,3}^3. It
checks the exact algebraic endpoints and both inverse compositions of the
coordinate maps. The exact `aca_24` run prints its two elementary move streams
and all-relator peaks. There is no heap search, panel scan, or heavy campaign.
The general proof is the displayed free-group identities; finite testing is
only an implementation and sign check. Independent mathematical review of
this new corridor remains pending.
