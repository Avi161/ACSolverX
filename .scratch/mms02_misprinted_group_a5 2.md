# The MMS02 misprinted deficiency-one group has an `A5` quotient

Date: 2026-07-29

## The exact group

Apply the paper's deletion and eleven exact eliminations to the printed MMS02
Wirtinger list, with the erroneous relation

```text
x13 = x5 x12 x5^-1.
```

Before adjoining a final weight-one word, the resulting deficiency-one group is

\[
G_- = \langle x,y,z\mid r_1,r_2\rangle,
\]

with

```text
r1 = xzYXyxZXYxyZ
r2 = XyxZXYXyxzXYxy.
```

These words are imported directly from
`mms02_wirtinger_repair_checker.three_generator_descendant(corrected=False)`;
they are not a separately transcribed model.

## The finite quotient

Permutations act on `{0,1,2,3,4}`, with word multiplication evaluated from
left to right by composition. Define

```text
x -> (0,1,3,4,2)
y -> (0,2,3,1,4)
z -> (2,0,1,3,4).
```

Direct evaluation sends both `r1` and `r2` to the identity. The three images
generate exactly the set of all 60 even permutations. Hence

\[
\boxed{G_-\twoheadrightarrow A_5.}
\]

In particular, the misprinted deficiency-one presentation is not a
presentation of `Z`. This gives an exact reason that Shehper et al.'s Lemma 15
cannot be used to rescue the printed MMS02 corridor: that lemma requires the
common deficiency-one group to be `Z`.

The same checker independently abelianizes the Fox matrix. All three maximal
minors agree up to a Laurent unit and sign, with normalized polynomial

\[
\boxed{\Delta_-(t)=t^4-3t^3+5t^2-3t+1.}
\]

Thus the misprint changes not only a diagrammatic corridor but the Alexander
module of the deficiency-one group; `\Delta_-(1)=1` and
`|\Delta_-(-1)|=13`. No identification with a particular knot group is made.

## Two final-relator choices remain separated

The published choice and the short corrected-descendant choice are

```text
w0 = Xyz       (the paper's w=x^-1 y z),
w1 = zYX       (equivalently z=xy).
```

In the displayed quotient,

```text
w0 -> (2,0,4,1,3),
w1 -> (2,3,4,0,1).
```

Both are 5-cycles, but `w1` belongs to neither the `A5` conjugacy class of
`w0` nor that of `w0^-1`. Therefore `w0` and `w1` are neither conjugate nor
inverse-conjugate in `G_-`.

This excludes a repair that holds `r1,r2` fixed and changes only the final
relator by basic substitutions using `r1,r2`, conjugation, and inversion. It
does **not** obstruct a general AC or stable-AC path: such a path may move all
relators, stabilize, and change the intermediate quotient.

## Exact replay

Run

```text
python3 .scratch/mms02_misprinted_group_quotient.py
```

The checker imports the exact eliminated relators, searches permutation
degrees two through five, verifies both relators at the displayed witness,
proves that the generated subgroup equals all even permutations, and checks
the two conjugacy exclusions. It also computes the abelianized Fox matrix and
checks all three maximal minors coefficient by coefficient. The lower-degree
nulls are bounded diagnostics; the displayed degree-five witness alone proves
the quotient theorem.

No Andrews--Curtis or stable Andrews--Curtis conclusion is claimed.
