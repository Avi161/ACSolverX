# Compressed cyclic-flow audit: PASS

All seven saved `corridor_pilot.json` paths and metrics pass. The pilot adds no
strict length gain and spends2709 new units. It imports no seed files.

The ordinary-AC ledger is checked independently. A root donor certifies
`h^-1 a^k`; both signs of `h` are expanded with conjugated donor factors.
If the original target expands to `E` using factor list`F`, and a packed
target expands to the same `E` using`G`, then the original target times
`F G^-1` equals the packed target. This justifies power collection without
deleting the root donor.

A derived Baumslag–Solitar relation has its full proof in the root and second
donor. Inverting, cyclically reducing and rotating that relation transports its
factor list as ordinary conjugation/inversion. Neither donor is the target.

For model `s^-1 a^m s=a^n`, set
`a_i=m,b_i=n` at a positive stable letter and `a_i=n,b_i=m` at a negative one.
For cyclic target blocks `s_i a^(e_i)` and signed integer flows`q_i`, the
simultaneous exponent update is

`e_i' = e_i - b_i q_i + a_(i+1) q_(i+1)`

with indices read cyclically. The compiler realizes this sequentially with
explicit conjugated donor corrections. At the first block, the incoming term
crosses the displayed cut, so the outer conjugating frame must also change.
The saved formula and final raw word account for that frame.

For any primitive word replacement`A→B` with correction`A^-1 B`, the power
compiler telescopes its conjugates to`A^-q B^q`. Negative powers invert the
correction and conjugate it by`A^-1` before the same construction. This is why
negative flow choices need more than just negating exponents. Final helper
packing is then appended as another exact normal-product identity.

Tiny known-trivial controls with root exponents±2 check six signed helper
expansions,50 power-packing lengths against exhaustive coefficients, two
derived BS models, and **54 compiled simultaneous flow choices**. Every
resulting full normal-product event independently replays. Both cyclic dynamic
programs agree with exhaustive enumeration of their finite flow boxes; six
truncated-budget controls return no falsely completed answer. No census search
is rerun.

The dynamic program's objective is the sum of shortest packed **individual
exponent blocks** within its declared flow range. It keeps stable-letter signs
fixed while scoring. Zero blocks can later permit stable-letter cancellation,
and cyclic/free reduction can reduce the final tuple further. Therefore its
optimum is not necessarily the shortest final cyclic word, the best candidate
over unbounded flows, or a global minimum of the presentation. This is a scope
limitation, not an invalid certificate: acceptance uses the replayed full tuple.

The work counter charges model/collection attempts and dynamic-program
transitions. It does not price every letter in a power, every factor emitted,
or the elementary expansion of those factors. An incomplete dynamic program
deliberately discards its partial best rather than treating a truncated pass
as complete. Negative pilot results are limited to that policy.

Reproduce with `verification_consequence_checks.py`; source hashes and detailed
results are in`verification_corridor.json`. No algebraic flow bug was found.
