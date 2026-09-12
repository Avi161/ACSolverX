# Theory wave 3 (coordinator recovery)

The assigned theory agent timed out before the first model turn. Its
transcript is empty (`messages: []`); nothing was recovered from that
run. Contents below are coordinator identities from
`code/c16_escape_scan.py`. Not a U124 solve.

## C19. δ=−1 C16-endpoint AC2 produces consecutive BS(n,n+1) — IDENTITY-CHECKED

**Hypotheses.** `n ≥ 2`, and the pair is the C16 endpoint

```
D = x⁻¹ u³ x⁻¹ u⁻²           compact XuuuXUU
E = u⁻¹ xⁿ u⁻² x u² x⁻ⁿ      compact U xⁿ UU x uu x⁻ⁿ
```

i.e. `S_{n,−1}`.

**Identity.** One AC3 on each row (rotate `E` by `n`, rotate `D` by 2)
followed by AC2 replacing `E` by the product:

```
cyc( rot(E, n) · rot(D, 2) )  =  x⁻ⁿ u⁻¹ xⁿ u x⁻¹
```

which is cyclically `u⁻¹ xⁿ u x⁻(n+1)`, consecutive BS(n,n+1) with
stable letter `u`. Checked `n=2..7`: `tables/c16_escape_scan.json` `c19`.

**Length.** Cyclic total `2n+13 → 2n+10` (drop 3), uniformly. This is an
ordinary elementary length drop **on the C16 endpoint**, not on a stored
U124 spelling. Reaching `S_{n,−1}` from an archival `P_{n,−1}` still uses
C7 then C1 then C16 (two C0 uses). Do not update `aca_124_best.csv`.

**C5 does not finish.** After C19 the pair is `⟨ D, BS(n,n+1)_u ⟩`. The
u-exponent of `D` is `+1`, so C5’s exponent hypothesis holds if `BS` is
read as the donor. Britton still fails: no orientation of `D` contains a
pinch `u^{±1} x^k u^{∓1}` (`c19_donor_pinch = false`). Same stall shape
as C15, different donor.

**Second depth-1 child (same length).** Replacing `D` instead yields a
consecutive BS(n+1,n) with stable `u`, companion `E` unchanged, cyclic
length unchanged. Recorded in the scan; not a descent.

**Why this is not C16.1.** C16.1 uses an illegal-on-minus rotation of
`D⁻¹` and returns `P_{n,+1}`. C19 uses a legal rotation of `D` against
`E` and stays on the minus branch. The `δ=+1` depth-1 neighbourhood
contains the C16.1 loop (control: `S_plus_matches_P`) and no extra
length-drop family.

**Falsify.** Exhibit `n≥2` where `cyc(rot(E,n)·rot(D,2))` is not
cyclically BS(n,n+1), or where the cyclic total does not drop by 3.

## Named negatives from the same scan

### N1. Swapped-letter C16 on `S` and on the five stored endpoints — does not fire

Magnus with conjugating letter `u` and content `x`: 0 fires on all
`S_{n,±1}` (`n=2..7`) and on the five stored C16 endpoints. A second
C16 corridor with roles swapped is not available on these spellings.

### N2. Tag family depth-1 with the MS relator held fixed — does not interchange tags

`P` companion `y^{-(n+1)} x^{-1} y^n x` and the claimed Aut-form `S`
companion `y^{-n} x^{-2} y^{-1} x^2 y^n x^δ` are not related by AC2
against a rotation of the MS relator `y⁻¹ x⁻³ y^δ x²` (`n=2..7`, both
signs). Interchanging those tags, if possible, needs a longer product
or a different donor.

### N3. Five stored C16 endpoints are not BS donors

x-exponents of `Â`: aca_16: +2; aca_43: −3; aca_67: +1; aca_87: +3;
aca_90: +1. None is a 4-run HNN/BS donor. Depth-1 AC2: two raw-length
drops (aca_16, aca_67) that do not create BS or one-occurrence; not
promoted to a theorem.

### N4. Factorization of `D` makes the missing BS visible

Free identities, not AC moves:

```
x⁻¹ u³ x⁻¹ u⁻²  =  (x⁻¹ u³ x)(x⁻² u⁻²)  =  x⁻² (x u³ x⁻¹) u⁻²
```

The inner factor `x u³ x⁻¹` would become `u²` if a BS(3,2) relation in
stable `x` were present; it is not. That is C17 H1 failing, written as
a splitting.

## Redirect

On `δ=−1`, C19 is the first elementary progress after C16. Next legal
questions: a pinch-creating AC3/AC2 on `D` that makes Britton fire
against the new BS(n,n+1) companion, without the illegal `ρ`; or a
theorem that treats `D` (u-exp `+1`, two x-letters) as a C4/C12-style
companion of that BS. Do not spend effort on `δ=+1` isolators through
`x^n` (C16.1 loop). The five stored hits remain a separate, non-BS
donor class.
