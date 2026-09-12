# Wave 3 stable-AC legality audit

## BLOCKERS

1. **Nothing in C16--C18 solves a U124 row.** The coordinator records
   `solved_u124 = 0`. C16 reaches a longer, non-terminal endpoint; C16.1 is a
   same-\(n\) loop only on the \(+\) branch and does not fire on the five stored
   hits; C17's U124 divisibility hypothesis fails; C18's H1 scan has no hit on
   the three tested spelling families.
2. **C16 is non-effective.** Gate 1 and Gate 2 each use C0/Lemma 11 once.
   The checked identities and the seven-multiplication elementary core do not
   supply either unbounded normal-closure witness. Thus C16 proves conditional
   existential stable transport, not an elementary AC1--AC5 certificate.
   The rise \(n+12\to2n+13\) in length/\(\mu\) is not progress. The corridor
   measure \(\nu\) proves termination of C16 only; it is not a well-founded
   descent charged to U124.
3. **C17's stated elementary move bound is wrong.** Replacing a block
   \(u^e=(u^M)^{e/M}\) requires \(|e|/M\) AC2 uses of the donor (and similarly
   with \(N\) for shear-up), not one AC2 for the whole powered block. There are
   two displayed blocks. The shear remains Lemma-11-free, finite, and
   effective, but not `<= 2|c|` AC2.
4. **C17 stops at an uncertified C4 obligation.** A one-occurrence terminal is
   not itself a solve. The Nielsen descent and companion cleanup must be
   expanded into legal moves before C17 can trivialize any presentation.
   Reciprocal BS(3,2) triviality is unavailable.
5. **C18 overstates the replayed Euclidean scope.** The replay checks
   \(k=m+1,2m+1,3m+1\), where repeated subtraction reaches exponent \(1\).
   It does not provide a full alternating elementary Euclidean construction
   for every coprime pair. `gcd(k,m)=1` is a lattice prerequisite for the
   two-row mechanism, but the stated general sufficiency is not established
   by the supplied cyclic identity.

## WARNINGS

- The C16.1 generator shift \((x,y)\mapsto(u,x)\) is a Nielsen relabel, not an
  ordinary AC move. The catalogue correctly flags stable transport through
  C1. Consequently the \(+\)-branch loop is an identity-checked,
  non-effective stable loop, not an elementary ordinary-AC loop.
- The coordinator confirms the C16.1 \(\rho\)-rotation for
  \(\delta=+1\), and confirms its absence for \(\delta=-1\). Applying \(\rho\)
  on the minus branch is illegal; its apparent shortening must remain
  forbidden.
- Calling `aca_16`, `aca_43`, `aca_67`, `aca_87`, and `aca_90` **C16
  instances** is accurate in the limited theorem-hypothesis sense: some
  explicit AC1/AC3 orientation has H2 and H3, and the coordinator verified the
  Gate-1/Gate-2 substitutions. It does not mean that C16.1 applies, that
  length descends, or that any of the five is solved. All five fail the
  C16.1 \(\rho\)-rotation.
- For \(S_{n,+1}\), C17's H3 already fails because \(3\nmid2\). The exact
  two-state orbit \(\{(c,2),(c+1,3)\}\) explains only this two-shear
  recognizer's stall. It is not a theorem explaining all 122,842 Britton
  rejects and is not an obstruction to other BS-like rewrites.
- C18's displayed Euclid identity is cyclic, not literal; every use needs the
  corresponding AC1/AC3 orientation around AC2. Radix gives \(O(\log m)\)
  stored state but still \(\Theta(m)\) elementary multiplications. A freshly
  adjoined \(t^{-1}x^k\) followed by deletion is only a round trip.
- The C18 `1764/0` result is exact only for rotations/inversions of the rows of
  the three spellings \(Q,Q',S\), \(n=2,\ldots,8\), both signs and both tested
  power letters. It says nothing about other AC- or stable-AC-reachable
  spellings or about the five extra C16 endpoints.
- The Aut-canonical form of \(S\), its \(\mu\), and separation of the
  \(P,Q',S\) Aut orbits are `aut_canon` facts. They are not ordinary AC paths;
  stable transport through such an automorphism requires C1 and inherits
  C1's non-effectiveness.
- The inventor's cyclic-complement `0/12` and overgroup `0/36` numbers were
  explicitly not rerun by the coordinator. They are not independent replay
  evidence and cannot be upgraded to catalogue negatives.
- Earlier blockers remain: the 14/14 CoV hops are identities rather than
  elementary certificates; Prop A is non-effective; C12's Aut step is
  non-effective; \(\mu=13\) is never a removal; 124 is an upper bound, not an
  exact class count; and failure of any bounded search is not an obstruction.

## ALLOWED CLAIMS

- C16's free-group identities, Magnus H2/H3 tests, Gate substitutions, and
  \(c\)-free output row replay on the recorded finite ranges. Conditional on
  C0/C2, these give non-effective stable equivalences.
- The five named best-table pairs meet C16's oriented hypotheses and have
  verified substitutions. Their endpoints are longer and non-terminal, and
  none admits the recorded C16.1 tail.
- C16.1 gives the same-\(n\), \(\delta=+1\) stable loop after citing C1 for the
  generator shift. For \(\delta=-1\), only absence of that particular legal
  rotation is proved.
- C17's literal shear identities are Lemma-11-free and admit an effective
  repeated-AC2 expansion. Its positive control reaches a C4 obligation.
  U124 \(S_{n,+1}\) fails H3, while \(S_{n,-1}\) fails the BS-donor shape.
- C18's tested \(k=qm+1\) cyclic subtraction chains isolate \(x\); its radix
  encoding compresses state, not proof length. The finite `1764/0` H1 report
  is a spelling-local negative only.

There is no allowed claim of a U124 trivialization, row removal, elementary
certificate, ordinary ambient-Aut move, or mathematical obstruction here.

## VERDICT per theorem (APPROVE / REVISE / REJECT) with required wording changes

### C16 — APPROVE

The catalogue accurately labels the result identity-checked and
non-effective, identifies both C0 uses, says the elementary core alone is
bounded, records the length/\(\mu\) rise, and denies a U124 descent or solve.
The five stored hits may remain labelled C16 instances with those caveats.

### C16.1 — APPROVE

The catalogue correctly cites C1 for the Nielsen generator shift, limits the
loop to \(\delta=+1\), forbids the illegal minus-branch \(\rho\) shortening,
and explicitly says that the five stored C16 hits do not receive this tail.

### C17 — REVISE

Replace:

> `are ordinary AC1–AC3 displayed-block substitutions (Lemma-11-free).`

with:

> `are finite ordinary AC1–AC3 displayed-block substitutions
> (Lemma-11-free); a block u^{±e} requires |e|/M donor multiplications for
> shear-down, or |e|/N for shear-up.`

Replace:

> `Certificate growth. Shear: <= 2|c| AC2, effective.`

with:

> `Certificate growth. If e_j is the inner exponent before step j and
> d_j=M for shear-down or N for shear-up, the shear uses
> 2 sum_j |e_j|/d_j AC2 moves, plus explicit AC1/AC3 orientations; this is
> finite and effective. The C4 tail remains uncertified.`

Replace the sentence attributing all 122,842 rejects to the orbit with:

> `For each displayed S_{n,+1} state, the two-shear orbit explains why this
> recognizer cannot lower the flank. It neither classifies nor explains all
> 122,842 Britton rejects and is not an obstruction to other BS-like moves.`

### C18 — REVISE

Replace:

> `Euclid by AC2 against x^{-m}c_0^{-1} is a cyclic identity and isolates x
> iff H3. Necessity of H3 is the abelian lattice, not a search.`

with:

> `Each displayed subtraction against an AC1/AC3 orientation of c_0x^m is a
> cyclic, not literal, identity. The replay proves isolation for the tested
> k=qm+1 chains. No full elementary Euclidean expansion for every coprime
> (k,m) is supplied, so gcd(k,m)=1 is presently a lattice prerequisite for
> this two-row route, not an audited sufficient criterion in that generality.`

Replace:

> `Two C0 uses unbounded.`

with:

> `A one-auxiliary defining-power round trip has two non-effective C0 uses;
> a radix chain has a C0-based installation and removal for each auxiliary
> defining row, in addition to its Theta(m) elementary multiplications.`

## What would make a U124 solve from here

For each claimed row, provide a legal path from its recorded representative to
the standard free basis, with every AC1--AC5 move replayed. Any C0/C1 segment
must either materialize the needed normal-closure witnesses or remain an
explicitly cited non-effective existence step; it may not be counted as an
elementary certificate. From C16, this additionally requires a genuine
well-founded U124 descent beyond the longer endpoint. A C17 finish requires
both a legal route that overcomes the failed \(3\nmid2\) gate and an expanded
C4 tail. A C18 finish requires H1 and H2 on a legally reached spelling plus a
complete Euclidean and auxiliary-deletion expansion. Only independently
replayed terminal paths for all rows covered by the 124-row upper-bound table
would establish the campaign goal.
