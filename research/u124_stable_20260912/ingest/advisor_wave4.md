# Wave 4 stable-AC legality audit

## BLOCKERS

1. **C19 is not a certified U124-row reduction.** The three elementary moves
   start at \(S_{n,-1}\), the C16 endpoint, not at an archival or best-table
   U124 representative. The incoming route still contains C16's two
   non-effective C0/Lemma-11 uses (and the cited C7/C1 transport). Until the
   complete incoming transport is materialized as legal AC1--AC5 moves, the
   drop cannot update `aca_124_best.csv` or be charged to a U124 row.
2. **The recorded Britton negative is not certified by the stated helper.**
   `britton_pinch` first compresses \(u^3\) and \(u^{-2}\) into runs and then
   requires both whole run exponents to have absolute value one. It also has no
   \(n\)-dependent associated-subgroup divisibility test. Thus
   `c19_donor_pinch = false` does not by itself prove the C5 preflight result,
   and the literal claim that no orientation contains
   \(u^{\pm1}x^k u^{\mp1}\) is false: \(D\) visibly contains \(u x^{-1}u^{-1}\)
   and cyclically contains \(u^{-1}x^{-1}u\).

## WARNINGS

- The **C5 refusal is nevertheless mathematically correct** for \(n\ge2\).
  With donor
  \(B=u^{-1}x^n u x^{-(n+1)}\), a valid Britton pinch must be
  \(u^{-1}x^{qn}u\) or \(u x^{q(n+1)}u^{-1}\). The two opposite-sign
  stable-letter boundaries of \(D=x^{-1}u^3x^{-1}u^{-2}\) have base exponent
  \(-1\), divisible by neither \(n\) nor \(n+1\). C5 therefore stalls for a
  divisibility reason, not because the syntactic subwords are absent.
- The all-\(n\) identity is stronger than the finite JSON check but is directly
  auditable. With `rot` meaning right rotation as in the code,
  \[
  \operatorname{rot}(E,n)=x^{-n}u^{-1}x^nu^{-2}xu^2,\qquad
  \operatorname{rot}(D,2)=u^{-2}x^{-1}u^3x^{-1}.
  \]
  Their product freely reduces, uniformly for \(n\ge2\), to
  \(x^{-n}u^{-1}x^nux^{-1}\), cyclically
  \(u^{-1}x^nux^{-(n+1)}\). The JSON independently records this for
  \(n=2,\ldots,7\).
- Two AC3 rotations followed by AC2 leave the first row as
  \(\operatorname{rot}(D,2)\). Calling it \(D\) is harmless only up to cyclic
  conjugacy; a literal return to the displayed \(D\) costs one restoring AC3.
- There is no hidden Tietze move in C19. Cyclic rotation is AC3, multiplication
  is AC2, and free cancellation is equality in the free group. C0/C1 enter
  only through the separately disclosed route to the C16 endpoint.
- `c19_product_pinch = true` merely sees the stable-letter pattern in the BS
  relator itself; it is not evidence that the companion \(D\) Britton-reduces.
- The scan and its negatives remain bounded to the recorded spellings and
  ranges. They do not prove an obstruction to another ordinary-AC continuation.

## ALLOWED CLAIMS

- **Yes:** C19 is a legal ordinary-AC cyclic-length reduction of the displayed
  C16 endpoint. Two AC3 rotations and one AC2 give a consecutive
  BS\((n,n+1)\) relator with stable letter \(u\).
- The cyclic totals are \(2n+13\) before and \(2n+10\) after, a drop of three.
  This follows uniformly from the displayed cancellation and is replayed in
  `tables/c16_escape_scan.json` for \(n=2,\ldots,7\).
- **No:** C19 may not be advertised as a U124 row reduction, best-table
  shortening, row removal, or solve unless the entire route from the recorded
  U124 representative to \(S_{n,-1}\), especially C16's two C0 obligations,
  is materialized.
- **Yes, with corrected reasoning:** C5 is correctly refused after swapping
  the new BS row into the donor role. \(D\) has \(u\)-exponent \(+1\), but
  neither potential boundary is an associated-subgroup word for \(n\ge2\).
- The second depth-1 child may be reported as a same-or-higher-length
  consecutive BS\((n+1,n)\) observation, not as descent.

There is no allowed claim of a U124 solve, certified best-table improvement,
row removal, or general Britton obstruction.

## VERDICT per theorem (APPROVE / REVISE / REJECT) with required wording changes

### C19 — REVISE

Keep the ordinary-AC endpoint reduction, length calculation, U124 disclaimer,
and “no hidden C0/C1 in C19” wording.

Replace:

> `no orientation of D has a pinch u^{±1} x^k u^{∓1}`

with:

> `D has opposite-sign stable-letter boundary subwords, but their intervening
> x-exponent is -1. For n≥2 it is divisible by neither n nor n+1, so neither
> boundary is a valid BS(n,n+1) Britton pinch and C5 does not fire.`

Do not cite `c19_donor_pinch = false` as the proof unless the checker is changed
to split stable-letter runs and test the appropriate \(n\) or \(n+1\)
divisibility. If a literal final pair is displayed with first row \(D\), add
the restoring AC3 or say explicitly “\(D\) up to cyclic conjugacy.”

## What would make a U124 solve from here

Materialize a legal AC1--AC5 path from each claimed recorded U124
representative through C7/C1/C16 to \(S_{n,-1}\), including explicit witnesses
for both C16 C0 uses. Then continue from
\(\langle D,B_{n,n+1}\rangle\) to the free basis with every orientation,
Britton substitution, multiplication, stabilization, and deletion expanded
as elementary moves. A corrected \(n\)-aware Britton checker could validate a
candidate continuation, but the present C5 refusal supplies no finish.
Independently replayed terminal certificates for all rows in the 124-row
upper-bound table, not this endpoint drop alone, would establish the campaign
goal.
