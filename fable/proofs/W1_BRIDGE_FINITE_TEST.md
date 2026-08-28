# W1: the A5 obstruction is blind for the full MMS02 bridge

Date: 2026-08-28 · Lane: `fable/proofs` · Checker: `checkers/a5_bridge_orbit.py`

## Statement

Let `F = F(x,y,z)`, uppercase = inverse, and

```text
A   = xzYXyxZXYxyZ
B   = XyxZXYXyxzXYxy
Kxy = zYX
Kpub= Xyz
```

(the MMS02 bridge data of `docs/AK3_PROMISE_LEDGER.md` §1 and
`.scratch/mms02_u_xy_bridge.md`; the bridge target is
`(A,B,Kxy) ~AC(1-3) (A,B,Kpub)`, and `(A,B,Kxy)` is certified AC-trivial).

**Theorem (proved by complete finite closure).** For every homomorphism
`φ: F → A5` with `φ(A) = φ(B) = 1`, the triples `(1,1,φ(Kxy))` and
`(1,1,φ(Kpub))` lie in the **same orbit** of the induced AC-move action on
`(im-related) A5³`. Consequently **no invariant computed through any A5
quotient of the misprinted base group can obstruct the bridge.** The known
fixed-base A5 no-go (`.scratch/mms02_u_xy_bridge.md`) is an artifact of
freezing the rows `A`, `B` as words: once they may move, A5 sees nothing.

## Soundness of the test

Fix `φ` with `φ(A)=φ(B)=1`, and let `H = ⟨φx, φy, φz⟩`. Under `φ`, every
stage of an AC1–AC3 history maps to a triple in `H³`, and the three
primitive moves map to:

- AC1 (invert row i) → `inv(i): t_i ← t_i^{-1}`;
- AC3 (conjugate row i by a word w) → `conj(i, φ(w))`, and closure under
  `conj(i, g)` for the three generator images generates conjugation by all
  of `H` (composition: `conj(i,g)∘conj(i,h) = conj(i,gh)`);
- AC2 (row i ← row i · row j) → `mult(i,j,+,1): t_i ← t_i·t_j`.

Conversely each generator of the computed closure lifts to an AC1–AC3
composite (`mult(i,j,s,c) = conj(i,c) ∘ mult(i,j,s,1) ∘ conj(i,c^{-1})`
after an AC1/AC3 dressing of row j). Hence an AC1–AC3 path between the two
triples forces their `φ`-images into one orbit of the computed action.
Left-multiplications and row swaps are derived moves and add nothing.

## Computation

Complete scan of `A5³` (216,000 triples) finds exactly **180 homomorphisms**
with `φ(A)=φ(B)=1`, in 7 conjugacy classes (one trivial). BFS closure of
the move action (complete enumeration, not budgeted search) from
`(1,1,φ(Kxy))` per class:

| class rep (element ids) | \|H\| | orbit size | control: trivializer in orbit | `(1,1,φ(Kpub))` in orbit |
|---|---:|---:|---|---|
| (1,1,1)    | 3  | 26      | yes | yes |
| (1,4,24)   | 60 | 215,999 | yes | yes |
| (1,28,15)  | 60 | 215,999 | yes | yes |
| (3,3,3)    | 2  | 7       | yes | yes |
| (16,16,16) | 5  | 124     | yes | yes |
| (17,17,17) | 5  | 124     | yes | yes |

The positive control uses the certified AC-triviality of `(A,B,Kxy)`
(134 primitive moves): its image orbit must contain `(φx,φy,φz)`, and does,
in every class — validating the move model before any negative could have
been read. The two surjective classes have orbit = all of `A5³` minus the
single frozen tuple `(1,1,1)`, i.e. over A5 the AC action on triples with
full normal closure is transitive: **no A5 invariant of any kind survives.**

Record digest (sha256 over the sorted JSON records):
`55675b1aa2fa9b5f1e4d73f3e1971bde446e03beaa7aa5f325eab560f031ea79`

Replay: `python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 fable/proofs/checkers/a5_bridge_orbit.py all`

## Scope and nonclaims

- This does **not** prove the bridge, and does not decide AK(3), stable AC,
  or AC. It removes the only known obstruction evidence against the bridge
  and shifts weight toward the bridge being provable (by search or by
  structure).
- Diagonal classes connect for the trivial reason `φ(Kxy) = g^{-1}`,
  `φ(Kpub) = g` (one AC1 image move); the surjective classes carry the
  content.
- Next escalation (W1b): the same complete-closure test over larger
  quotients of the misprinted group (PSL(2,7) etc.) using the
  generator-reduced move set (24 successors/state); any single failure
  refutes the bridge.
