# MMS02 Wirtinger repair attack

## Result

No bridge to AK(3) was found. No word was promoted to a bridge candidate, because
none reached AK(3) with an exact AC1-AC5 replay.

The useful conclusion is sharper than a failed search. For the paper's word
`w=Xyz`, the corrected descendant is exactly AC-trivial, while the misprinted
descendant is exactly the published length-25 pair and reaches AK(3) by the 53
published `h_i` moves. Consequently, connecting the two descendants by ordinary
AC moves is equivalent to AC-trivializing AK(3); correcting the Wirtinger corridor
does not supply a shortcut around the open problem.

All computations here are exact free-group computations. Every discovery command
was bounded to at most 30 seconds. The full AK(3) search, the full Task 5
certificate, and any unbounded enumeration were not run.

## Source check

- MMS02, PDF pp. 10-11, prints `r13` as
  `x13=x5 x12 x5^-1`, deletes `r12`, and uses the stated elimination order.
- Shehper et al., pp. 45-46 and Appendix F p. 54, identify that `x5` corridor as
  the misprint and give the corrected diagram corridor `x13=x4 x12 x4^-1`.
- Shehper et al., Appendix F p. 54, state that the misprinted `w=Xyz` descendant
  is the length-25 pair connected to AK(3), and list its 53 `h_i` moves.
- Shehper et al., pp. 46-47, prove AC-triviality for the corrected Wirtinger
  presentations and for the specific descendants covered by their recursive
  substitution-and-removal construction. That statement does not imply ordinary
  AC-triviality for every arbitrary direct-removal word `w=zU^-1` below.

The displayed MMS02 pages 10-11 and Shehper pages 45 and 54 were also rendered
and inspected visually. The exact corridor reconstruction in
`.scratch/mms02_wirtinger_repair_checker.py` agrees with those passages.

## Corrected pair and direct-removal normal form

The corrected three-generator pair is

```text
R1 = yZXzYXyZxz
R2 = YxyZxzYXyZxZXz
```

Its exponent-sum rows in `(x,y,z)` are

```text
R1: (-1, 1,  0)
R2: ( 1, 0, -1)
```

so its abelianization identifies all three meridians. A direct removal of `z`
has the exact form

```text
w = z U^-1,       z = U(x,y),       exp(U) in {0,2},
```

because `exp(w)=1-exp(U)` must equal `+1` or `-1`. After substitution the pair is

```text
D1(U) = y U^-1 X U Y X y U^-1 x U
D2(U) = Y x y U^-1 x U Y X y U^-1 x U^-1 X U.
```

The same parametrization was checked for direct removal of `x` or `y`, followed
by the canonical renaming of the two surviving generators.

## Exact corrected-versus-misprinted relation at `w=Xyz`

Here `w=Xyz` gives `z=Yx`. The corrected descendant is

```text
C = yXyXYxYXyXyxYx | YxyXyxYxYXyXyyXYx.
```

Starting from its exact cyclic/inverse/order normalization, the following six
Definition-2.1 moves reach the trivial basis:

```text
(2,+1,0,11)  (2,-1,0,0)  (2,+1,1,2)
(2,-1,0,0)   (2,-1,1,0)  (2,-1,1,0)
```

The independently replayed states are

```text
YXyXYxYxyXyxYx | YYxYxyXyXYxYXyXyx
YYx             | YXyXYxYxyXyxYx
YYx             | YYxYXyXyx
YYx             | YYYx
Y               | YYx
Y               | Yx
Y               | X
```

The attack checker expands these six quotient-normalized moves, including the
initial normalization, to 45 literal primitive AC1, AC2, and AC3 operations and
replays every word equality. No AC4 or AC5 is needed for this two-generator
trivialization.

For the misprinted corridor, the same substitution gives

```text
Mraw = xYxYXyyXYxyXy | XyyXYXyxYYxy.
```

Invert both rows and rotate the first by one letter to obtain exactly the
published pair

```text
P = XYxYXyxYYxyXy | YXyyXYxyxYYx.
```

The 53 Appendix-F moves replay from this exact spelling to

```text
xxxYYYY | xyxYXY = AK(3).
```

Thus, writing `T=(x|y)` for the trivial basis,

```text
C ~AC T,       M ~AC P ~AC AK(3),
```

and therefore

```text
C ~AC M    if and only if    T ~AC AK(3).
```

This is the exact relation between the repaired and published descendants. A
bridge between them would be an AC-trivialization of AK(3), not merely a repair
of the MMS02 Tietze corridor.

## Theory-led near miss: `U=xx`

The most economical structural lead is

```text
U = xx,        w = zXX,        exp(w) = -1.
```

It produces

```text
D_z(xx) = yXYXyx | YxyxYXyXX.
```

The first row is a cyclic conjugate of the inverse AK braid relator
`xyxYXY`. This reduces a row-locked bridge to the conjugacy of the second row
with the AK power relator `p=xxxYYYY` in

```text
B3 = <x,y | xyx=yxy>.
```

That reduced route is impossible. Under the standard homomorphism

```text
x -> [[ 1, 1], [ 0, 1]]
y -> [[ 1, 0], [-1, 1]],
```

the two relevant words have images

```text
q=YxyxYXyXX -> [[ 1,-2], [-1,3]],   trace 4
p=xxxYYYY    -> [[13, 3], [ 4,1]],   trace 14.
```

The inverse of `p` also has trace 14. Therefore `q` is conjugate to neither
`p` nor `p^-1` in `B3`. This rules out the route that fixes the braid row and
changes only the other row; it is not an obstruction to a general AC path that
moves both rows.

## A fixed-relator exchange obstruction in `A5`

There is also a finite obstruction to repairing only `r13` while all retained
Wirtinger relators and `w=Xyz` remain fixed. Remove `r12` and `r13`, add `w`, and
perform exact unique-occurrence eliminations. Renaming the three surviving
generators `(x11,x12,x14)` as `(k,l,n)` gives two common relators

```text
lnkNKNknknKNLnkNKNknknKNllnkNKNKnknKNLnkNKNknknKN
nkNKNknknKNLLnkNKNKnknKNlnkNKNKnknKNLLnkNKNknknKNll
```

and sends the corrected and misprinted versions of `r13` to the probes

```text
nkNKnknKNLnkNKNknknKNLnkNKNKnknKNl
knKNLnkNKNKnkn
```

respectively. In `A5`, set

```text
k = (0 1 2 3 4),
n = (0 2 4 3 1),
l = n^-1.
```

Both common relators vanish. The corrected probe has cycle type `(3)`, while the
misprinted probe has cycle type `(5)`. The checker proves that `k,n` generate all
60 even permutations, so this is literally an `A5` quotient, not merely a
subgroup of order 60.

Hence the two probes are neither conjugate nor inverse-conjugate in this fixed
common-relator quotient. This excludes a corridor repair consisting only of
conjugating or inverting `r13` while leaving every retained relator fixed. It is
not an obstruction to general AC or stable-AC paths, which may move the other
relators and change the quotient during the path.

## Bounded discovery

### Exact bounded direct-removal sweep

For each eliminated generator `g` in `{x,y,z}`, the sweep enumerated every
freely reduced `U` of length at most 10 on the other two generators with
`exp(U)` equal to 0 or 2. There were 29,793 words per elimination choice,
89,379 total.

- No descendant was exactly AK(3), even after cyclic rotation, row inversion,
  and row reordering.
- Among descendants of initial total length at most 17, there were respectively
  5 (`z` removal), 5 (`x` removal), and 6 (`y` removal). None belongs to the
  complete 1,000-state AK(3) AC component under total-length ceiling 17.
- For `z` removal, enumeration through `|U| <= 12` found only `U=1` and `U=xx`
  whose first row is the AK braid cyclic class. Their second-row traces in the
  braid quotient are 2 and 4, respectively, versus 14 for the AK power row.
- Exact Whitehead normal forms for the shortest descendants and for the
  published `U=Yx` descendant differed from the AK(3) normal form. This is only
  an Aut(F2)-orbit exclusion, not an AC obstruction.

These are bounded negatives only. They do not exclude longer `U`, words with
multiple occurrences of the eliminated generator, descendants whose AC path
rises above length 17, or paths that alter both relators substantially.

## Smallest remaining word equation

Within the only short structural reduction found, the remaining equation is:

```text
find freely reduced U with exp(U) in {0,2} such that

  cyc(D1(U)) = cyc((xyxYXY)^epsilon),       epsilon in {+1,-1},

and

  D2(U) is conjugate in B3 to (xxxYYYY)^delta,
  where delta is forced by the total exponent.
```

The bounded solutions of the first equation through `|U| <= 12` are exactly
`U=1` and `U=xx`, and both fail the second equation by the trace calculation.
Once the first row is allowed to move as well, the remaining problem is the
full AC-equivalence equation `D_g(U) ~AC AK(3)`. The exact replay proves ordinary
AC-triviality only for the published corrected descendant `U=Yx` (and any other
descendant supplied with its own replay or simple-conjugation reduction). For a
general direct-removal word, substitution and removal supplies only the stable
relation inherited from the corrected Wirtinger presentation. Thus a general
bridge would establish stable AC-triviality of AK(3), and it would establish
ordinary AC-triviality only when the selected descendant is independently known
to be ordinarily AC-trivial.

## Replay artifact and honest limits

`.scratch/mms02_wirtinger_repair_attack_checker.py` independently verifies:

1. the corrected and misprinted three-generator descendants from the existing
   corridor checker;
2. both `w=Xyz` substitutions;
3. the corrected six-move path, expanded into literal primitive AC1-AC3 moves;
4. the exact normalization from the misprinted descendant to published `P`;
5. all 53 published `h_i` moves ending at the literal AK(3) pair.

`.scratch/mms02_killer_quotient_scan.py` imports the exact exchange quotient and
probe words from the corridor checker, evaluates the displayed `A5` witness,
and certifies both common relators, the two cycle types, and equality of the
generated image with the 60 even permutations.

The checker does not expand the original fourteen-generator Tietze elimination
into an elementary AC4-AC5 trace; that reconstruction remains the responsibility
of the supplied corridor checker and the substitution-removal theorem. No bridge
was claimed, so no hostile bridge review was triggered.

Two exploratory commands failed closed without affecting the result: direct
`importlib` loading hit Python 3.9 dataclass module registration, and `sympy` was
not installed. The successful checks use `runpy`, integer 2-by-2 matrices, and
the independent primitive replay above.
