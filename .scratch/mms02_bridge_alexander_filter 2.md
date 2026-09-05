# Alexander-module filter for MMS02 bridge symmetries

Date: 2026-07-29

## Scope

Let

\[
G_-=\langle x,y,z\mid A,B\rangle
\]

be the exact deficiency-one group obtained from the printed MMS02 relator,
with

```text
A = xzYXyxZXYxyZ,
B = XyxZXYXyxzXYxy.
```

This note gives an exact obstruction to two tempting ambient-free-group
automorphism bridges between the kill words `zYX` and `Xyz`.  It does not
obstruct a general AC path, because a general path may move all three rows and
need not preserve the normal closure of `A,B`.

## The cyclic Alexander module

Abelianization sends each of `x,y,z` to the same generator `t`.  Delete the
`x` column of the abelianized Fox matrix and write `a,b` for the remaining
`y,z` generators.  The first row is

\[
(2-t-t^{-1})a-b=0.
\]

Thus

\[
b=(2-t-t^{-1})a.
\]

Substitution into the second Fox row gives

\[
t^{-3}(t^4-3t^3+5t^2-3t+1)a=0.
\]

Since `t` is a Laurent unit,

\[
\boxed{
G_-'/G_-''\cong
\mathbb Z[t^{\pm1}]/(t^4-3t^3+5t^2-3t+1).
}
\]

For any exponent-zero word `w`, its module class is obtained directly from
its abelianized Fox derivatives as

\[
[w]=\partial_y(w)+(2-t-t^{-1})\partial_z(w)\pmod\Delta.
\]

If an ambient free-group automorphism preserves the normal closure of `A,B`,
the classes of the substituted relators must vanish in this module.

## First false symmetry: rejected by abelianization

The odd automorphism of the displayed `A5` quotient first suggested

```text
x -> xY,
y -> Y,
z -> zy.
```

This is an involution of the ambient free group, but its three exponent sums
are `(0,-1,2)`.  In `G_-^ab`, the classes of `x,y,z` are equal.  Therefore an
endomorphism of `G_-` must send them to equal exponent sums.  This candidate
does not descend to `G_-`.

## Second false symmetry: rejected by the Alexander module

A bounded Nielsen enumeration found the more convincing involution

```text
psi(x) = y,
psi(y) = x,
psi(z) = zyX.
```

Its three exponent sums are all one.  It also preserves both relators in
every homomorphism from `G_-` to `S_n` for `2 <= n <= 5`, and sends `zYX` to
the conjugacy-or-inverse-conjugacy orbit of `Xyz` in all 272 such
homomorphisms.  Those bounded observations are not used in the obstruction.

The exact Fox calculation gives

\[
\begin{aligned}
[\psi(A)]&=t^2-3t+2,\\
[\psi(B)]&=-t^3+t-1
\end{aligned}
\qquad\text{in }G_-'/G_-''.
\]

Both representatives are nonzero: they have degree below the degree-four
monic polynomial `Delta`, so neither is divisible by `Delta`.  Consequently

\[
\boxed{
\psi(A),\psi(B)\notin\langle\!\langle A,B\rangle\!\rangle,
}
\]

and `psi` does not descend to an endomorphism of `G_-`.

This is an exact example where every available small permutation quotient
misses failure of normal-closure preservation, while the Alexander module
detects it immediately.

## Consequence for the bridge search

The reciprocal polynomial and the two `A5` five-cycle classes do not supply
an amphichiral automorphism bridge.  Future fixed-base automorphism candidates
must first satisfy:

1. equal exponent sums on the images of `x,y,z`; and
2. zero Alexander-module class for the images of both `A` and `B`.

Passing these conditions would still be necessary, not sufficient.  The
unrestricted equation

```text
(A,B,zYX) ~AC (A,B,Xyz)
```

remains open.

## Replay

```text
python3 .scratch/mms02_bridge_alexander_filter.py
python3 .scratch/test_mms02_bridge_alexander_filter.py
```

The checker imports the exact eliminated relators, derives both Fox rows,
eliminates the `z` module generator through the unit coefficient in the first
row, reconstructs `Delta`, and replays both candidate substitutions.
