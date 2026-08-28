# W1 (corrected): every base-killing quotient is blind to the MMS02 bridge

Date: 2026-08-28 · Lane: `fable/proofs` · Checkers: `checkers/a5_bridge_orbit.py`,
`checkers/finite_bridge_orbit.py` · Status: **corrected after ac-advisor BLOCK** —
the original framing of this note claimed a decisive finite test; that test was
theorem-forced and carried no information about the bridge. This revision states
the actual theorem and retracts the earlier inferences.

## Data

`F = F(x,y,z)`, uppercase = inverse:

```text
A   = xzYXyxZXYxyZ
B   = XyxZXYXyxzXYxy
Kxy = zYX      (Txy = (A,B,Kxy) is certified AC-trivial, 134 primitive moves)
Kpub= Xyz      (Tpub = (A,B,Kpub) trivialization = the open bridge)
```

## Theorem (vacuity / blindness; ac-advisor's lemma, verified here)

Let `H` be ANY group (finite or infinite) and `φ: F → H` a homomorphism with
`φ(A) = φ(B) = 1`. Put `g = φ(Kxy)`, `h = φ(Kpub)`. Then `(1,1,g)` and
`(1,1,h)` lie in the same orbit of the induced AC1–AC3 move action on `H³`.

*Proof.* Both `⟨x,y,z | A,B,Kxy⟩` and `⟨x,y,z | A,B,Kpub⟩` present the trivial
group (the first by the certified AC-trivialization; the second because its
Tietze corridor ends at AK(3), which presents 1). Hence
`H/⟨⟨g⟩⟩ = H/⟨⟨h⟩⟩ = 1`, i.e. `⟨⟨g⟩⟩_H = ⟨⟨h⟩⟩_H = H`. Now chain:
`(1,1,g) → (g,1,g)` by one AC2 image move; holding `t₁ = g`, right
multiplications of `t₃` by conjugates of `t₁` sweep `t₃` through
`g·⟨⟨g⟩⟩ = H`, reaching `(g,1,h)`; then multiplications of `t₁` by conjugates
of `t₃ = h` sweep `t₁` through `g·⟨⟨h⟩⟩ = H ∋ 1`, reaching `(1,1,h)`. Every
element of a normal closure is a finite product of conjugates, so the chain is
finite. ∎

**Consequence.** The finite-quotient method — indeed any quotient-orbit method
that kills the base rows `A, B` — can NEVER refute the bridge, over any group.
The published fixed-base A5 no-go (`.scratch/mms02_u_xy_bridge.md`) cannot be
extended to moving bases by any such quotient: with the base rows free to
move, the only datum a base-killing quotient sees is the normal closure of the
third entry, and that is forced to be everything on both sides. This closes
the finite-quotient METHOD for the bridge. It does not close promise-ledger
route 1 (per the ledger's own rule that failure to find a quotient closes
nothing), and it says nothing about the bridge's truth.

## What the computations now mean

The complete closures over A5 (180 homs, 7 classes), S5, PSL(2,7), and A6 all
returned "connected", as the theorem forces. They are retained only as
machine regression pins of the theorem's conclusion and of the move-model
implementation (digests: A5 full-move `55675b1a…`, A5 reduced-move
`4f19e7c0…`, S5 `644de0a9…`, PSL(2,7) `570f5de0…`, A6 `08ca5fbf…`; the two
independent A5 move-set implementations agree class-by-class). The
positive-control design ("certified-trivial triple's image orbit must contain
the trivializer") is itself vacuous here for the same reason and is NOT
evidence the move model is correct; a future regression should add an
adversarial control (a deliberately incomplete move set asserted to fail).

One computational observation with no bearing on the bridge: over PSL(2,7)
the surjective-class orbits have size 8,918 out of 168³ — the ambient
AC-action on triples is far from transitive there, unlike A5's
"everything minus the frozen identity tuple". The forced connectivity of the
two bridge tuples is therefore not a triviality of the ambient graph; it is
exactly the theorem's chain.

## Retractions

1. RETRACTED: "removes the only known obstruction evidence against the
   bridge" — the test could not have produced obstruction evidence; nothing
   was removed.
2. RETRACTED: "shifts weight toward the bridge being provable / upgrades the
   case for search budget" — a null that is guaranteed by a theorem carries
   zero evidential weight. The case for a Tpub search rests solely on the
   independent greedy profile in `W1C_TPUB_PREFLIGHT.md` (29 → 14 total
   length inside 1,000 nodes), which is genuine empirical data.
3. The `PROGRAM.md` W1 premise "`G_mis` is nontrivial, so finite quotients
   bite on the bridge" was FALSE as stated: the third entry normally
   generates the image in both endpoint triples, which is the only datum such
   a quotient sees. Corrected in `PROGRAM.md`.

## The published theorem that retires the whole method

Borovik–Lubotzky–Myasnikov, *The Finitary Andrews–Curtis Conjecture*
(Progress in Math. 248, 2005), Thm 1.1: for finite `G` and
`k ≥ max{d_G(G), 2}`, the components of the AC-graph on normally generating
k-tuples are exactly the preimages of the components over `Ab(G)`. Hence for
every perfect image the graph is connected, and for every finite image the
only surviving datum is abelian. For the non-base-killing variant
(`orbit(φA,φB,φKxy) ∋ (φA,φB,φKpub)`, arbitrary `φ`): both triples
abelianize to rows of unimodular 3×3 integer matrices (both presentations
present the trivial group), and any two such matrices are connected by
elementary row operations and sign flips, so the abelian datum also always
passes. **No finite quotient of any kind can refute the bridge.** BLM
2005 state this as their purpose: finite-group computation cannot produce an
AC counterexample. (Threshold wording `d_G` vs `w(G)` should be pinned
against the paper before external citation; every reading clears our case.)
The vacuity theorem above extends the base-killing case to infinite images
as well. What remains for refuting the bridge: infinite-quotient and
genuinely noncommutative invariants (Alexander/Fox-module obstructions —
which the repo's 2026-07-29 lesson already found catching what finite scans
miss — and Quinn-type invariants).

## Scope and nonclaims

No bridge, AK(3), stable AC, or AC claim. The theorem is a method-closure
(blindness) result only.
