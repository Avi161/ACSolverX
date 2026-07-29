# Codex-line check: `origin/codex/proofs` at `813a6d1` (advanced from `b617123`)

Date: 2026-07-29, ~21:52 UTC. Read-only route-divergence analysis of the fable line
against the codex line's new commits. All quotations below are copy-pasted from files
read with `git show 813a6d1:<path>` (or, for the log, `git diff b617123..813a6d1 --
logs/29-07-2026.md`) without checking out the branch. Anything not directly quoted or
directly computed from the diff is marked `[INFERRED]`.

All six files named in the task exist at `813a6d1` and were read in full except the
2,851-line `.scratch/period_two_old_new_cut_load_certificate.py`, which was skimmed
(header, constants, dataclasses) only far enough to confirm what it computes.

---

## 1. What is the "old-new cut load certificate," and what does it actually certify?

It is **not** a new mathematical apparatus — it is a bookkeeping/verification harness
for one already-open step ("the old–new cut") inside their pre-existing "period-two"
combinatorial machinery, which is itself part of their depth-4/6 AC2-move census on
AK(3) (`experiments/stable_ac/depth4_period_two_*`, `AK3_DEPTH4_HANDOFF.md`,
`AK3_DIRECT_STABLE_THEORY.md` — read for context, not in the six named files). That
machinery defines a mod-2 bilinear pairing `𝔹(·,·)` between an "old" family of source
rows `A_{n,d}` (built from six row families: fixed, base, singleton, P, C, Q) and a
"new" 84-token collision-aggregated word mask `b_{n,d}`. The **open identity** they call
the "old–new cut" is the covariance/periodicity claim

> `𝔹(A_{n+1,d}, b_{n+1,d}) = 𝔹(A_{n,d}, b_{n,d})` (n≥0, d≥1)

(design doc §1, verbatim formula). Design doc §1 states plainly: *"The endpoint-potential
reduction has already reduced this claim to six family parities. The certificate will
materialize those parities as 9,408 source-fiber/cell loads carrying 17,760
old-occurrence histograms."*

**What "load" means:** their own term for one unit of verification work — a
"source-fiber/cell load" is one (integral-collision-aggregated old row fiber) × (one
threshold cell in an `(a,n)`/`(a,h,r)`/`(h,k,n)` parameter grid), and for every old
"occurrence" inside that load's footprint there is one "occurrence-load": a complete
84-bucket histogram of that occurrence's comparison outcome against every token of the
`b_{n,d}` mask. It is a compute/audit unit, not a physical or graph-theoretic load.

**What "cut" means:** `[INFERRED]` — not explicitly defined in the six files, but
consistently used as the name of the specific unresolved boundary/interface step in
their larger seven-family covariance proof: the comparison between the "old" (pre-
increment) row family and the "new" (post-increment, i.e. `d`- and `n`-shifted) token
mask that must be shown invariant as the induction advances one step. It is the name of
an open lemma, not a new construction.

**What it certifies (if/when it finishes):** design doc §7: *"If every check passes, the
manifest proves `𝔹(A_{n,d},b_{n,d})=1+[d=1]=[d>1] (n≥0, d≥1)`, and therefore the
positive-chamber old–new cut covariance identity."* This is a purely internal
combinatorial identity inside the period-two apparatus. As of `813a6d1` it is **not
finished** — see §6 below.

---

## 2. The intact-boundary pumping lemma

Not a claim about AC or AK(3) directly. It is a **word-combinatorics lemma about
canonical (shortlex) forms of powered/periodic words indexed by a multi-parameter
family**, used to make comparisons decidable "for all" exponents rather than only at
finitely sampled points.

Setup (§1, verbatim): a word `W(x) = b_0 r_1^{e_1(x)} b_1 ⋯ r_m^{e_m(x)} b_m` on an
**orthant** `𝒪 = x_0 + ℕ^k` — i.e. the family is indexed by a vector `x` of
nonnegative-integer offsets from a base point `x_0` (a genuine multi-index family, of
which "indexed by n" is the one-dimensional case), not a single word and not one scalar
`n`.

**Lemma 2.1 (verbatim statement):** given a tagged "intact boundary" for each changing
factor `r_j`, *"For `x ∈ 𝒪`, form `V(x)` from `V_0` by inserting exactly `δ_j(x)` further
copies of `r_j` at the selected `j`-boundary, for every changing factor. Then
`cv(W(x)) = V(x)`. The insertions may be performed in any order."* I.e., the canonical
(reduced) form of the whole parametrized word can be obtained by literally inserting
more copies of each periodic block at a fixed splice point, with no further
cancellation — that is the thing being "pumped": periodic sub-blocks of a word, inserted
at fixed intact splice points, as the exponent parameters grow.

Corollary 3.1 then lets shortlex comparisons between two such pumped families be decided
once and for all (by affine length, by identical block lists, or by a fixed first
mismatch letter) rather than case-by-case per exponent — this is the tool that turns
finite spot-checks into "all-power" (all-exponent) proofs.

Scope note (§0, verbatim): *"This proves the specialized word-theoretic lemma needed to
turn the threshold-three seed cells in the interrupted old--new checker into genuine
all-power cells. It does not assert that every concrete schema satisfies the
hypotheses, nor does it prove the six numerical family parities. Those are separate
finite application obligations."* And at the end (§5, verbatim): *"No claim about
`Q(A_{n,0})`, Andrews--Curtis, or stable Andrews--Curtis is made here."*

---

## 3. The endpoint potential — is it monotone, and which side does it bound?

**Short answer: no, it is not a monotone/inequality-producing potential at all, and it
does not produce a bound in either direction.** It computes an exact mod-2 **equality**
(a parity value), not an inequality. This is a materially different kind of tool from a
monotone potential function.

Mechanically (`period_two_old_new_cut_endpoint_potential.md` §2, verbatim): fix an
84-token mask `T = b_{n,d}`. For an oriented edge `e` of a "source tree" define
`ω_T(e) = 𝔹(η(e), T)` (an F₂-valued edge weight — the "activity" of that edge against
`T`). Choose a base vertex and define the **potential** `ψ_T(x) = Σ_{e∈[base,x]} ω_T(e)`
— a height function on tree vertices, valued in `𝔽₂ = {0,1}`, not a real-valued
monotone quantity. **Lemma 2.1 (forest Stokes, verbatim):**
`𝔹(η([x,y]),T) = ψ_T(x) + ψ_T(y)` — a discrete Stokes/telescoping identity: the
mod-2 pairing along any path between two tree vertices equals the sum (mod 2) of the two
endpoints' potentials, because the shared initial segment of the two base-paths cancels
in `𝔽₂`.

This is used to reduce 305 "interior" source-row positions to a handful of boundary
("endpoint") values (§0, verbatim): *"This note proves a collision-safe discrete-Stokes
reduction for the old (P,C,Q) rows. It reduces 305 source positions to one two-ray (P)
identity, one six-family (C) endpoint identity, and three paired (Q) rectangles. It does
not prove those endpoint-potential identities."*

So: **quantity** = an F₂ (parity) potential, not a scalar being monotonically tracked;
**moves** = edges of a fixed dependency/chronology "forest," not AC-moves or word-rewrite
moves; **direction** = neither upper nor lower — it is an exact telescoping equality
`𝔹(η([x,y]),T) = ψ_T(x)+ψ_T(y)`, used to *reduce the number of terms to check*, not to
*bound* anything. There is no upper/lower-bound question to answer here because no
inequality is produced. (Contrast explicitly noted in §4c below.)

---

## 4. Their scope note — is it still confined to a named ansatz?

Yes — if anything, more explicitly disclaimed than before, though the object of
disclaim has shifted from a single named bridge word to a named infinite **family**
(indexed by `n,d`) inside their fixed period-two construction. It has **not** become
class-wide. Verbatim scope statements, collected across the six files (each is a
standalone, independently-stated non-claim, not one repeated line):

- Design doc §1: *"This certificate is not, by itself, an AC or stable-AC
  trivialization of AK(3). It is one lemma in the current proof route. It must not
  assert the unproved formula `Q(A_(n,d))=[d=0]`, and it must not treat the `d=0`
  endpoint branch as closed."*
- Plan doc, Global Constraints: *"Do not assert `Q(A_(n,d))=[d=0]`; the certificate
  domain is exactly `n>=0, d>=1`."*
- `period_two_intact_boundary_pumping_lemma.md` §5: *"No claim about `Q(A_{n,0})`,
  Andrews--Curtis, or stable Andrews--Curtis is made here."*
- `period_two_old_new_cut_selector_theory.md` §0: *"This note does not prove or
  refute [`𝔹(A_{n+1,d},b_{n+1,d})=𝔹(A_{n,d},b_{n,d})`] ... No finite grid is used."*
  — and closing line: *"Nothing here proves or refutes Andrews--Curtis or stable
  Andrews--Curtis."*
- Log, 17:49:16 UTC entry: *"these reduce the old--new covariance route to concrete
  all-power schema checks plus one two-ray `P` identity, three paired `Q` rectangles,
  and a `C` endpoint value; they do not yet prove covariance, AC, or stable AC."*

Compared with the previous scope note quoted in the task (*"This proves a finite, exact
obstruction to the named ansatz. It is not an obstruction to a general AC1-AC3 path in
which the base rows move"*), the pattern is the same in kind: everything here is scoped
to their own named internal construction (the period-two `A_{n,d}`/`b_{n,d}` apparatus,
itself downstream of the MMS02-family depth-4/6 AC2 census on AK(3)), not to the general
AC or stable-AC move class. What has changed is generality **within** that construction:
they are now trying to prove an identity for an *infinite family* indexed by `(n,d)`
rather than one fixed bridge word — genuine progress in scope, but along one axis inside
a still-named, still-specific apparatus. It is explicitly not class-wide in the sense
our own `NOTES_FOR_CODEX_LINE.md` item 16 uses that term (an obstruction spanning
arbitrary presentations/paths).

---

## 5. Proof or disproof?

`[INFERRED]`, since none of the six files state a top-level goal in these terms —  but the
inference is well-supported by the surrounding depth-4/6 period-two apparatus (read for
context): the earlier checkpoints in that line prove statements of the shape "every row
reached from [a bounded move class] is nonprimitive" / "no target of this form is
primitive" (`AK3_SU2_FIXED_COMMUTATOR_OBSTRUCTION.md`,
`AK3_ARBITRARY_CONJUGATOR_PRIMITIVE_BARRIER.md`) — i.e. they are accumulating **negative
("barrier"/obstruction) results that rule out specific named routes to a trivialization**,
not constructing a trivializing AC-move sequence. The old-new-cut work is one lemma
feeding that same barrier-accumulation program (it is a step toward completing the
"seven-family covariance" identity that is itself part of bounding the MMS02/period-two
bridge ansatz). So: this route is **obstruction/negative-result-flavored — the same
general direction as a disproof would need (ruling out mechanisms), but explicitly not
yet a disproof of anything**, since every scope note in §4 disclaims AC/stable-AC
conclusions and the barriers proved so far are confined to named ansätze, not the whole
class. It is not proof-direction work (no trivializing sequence is being sought or
produced anywhere in these six files).

---

## 6. The "blocked" commits — is a route dead?

**No mathematical route was declared dead.** "Blocked" here is a purely **engineering/
resource** blockage, not a theory verdict.

From the log diff (verbatim, 21:03:00 UTC entry, commit `5bac6d9`): *"Preserved the
blocked full-record Task 5 attempt in the generator and tests: binding all 48,252
templates with repeated full-record JSON/SHA exceeded the 30-second guard, and the
process group/lock were verified gone. Revised the design, plan, and lessons to use
schema/cell tables plus compact witness interning and a measured slice gate; no
independent replay or theorem claim has yet occurred."*

Concretely: their proof-process guard (`scripts/run_proof_guarded.py`, new in this
range — a CPU-leak-safety harness analogous in spirit to our own
`experiments/lessons/parallel-runs-and-bound-direction.md` trap) caps every command at a
30-second wall-clock deadline. Serializing full JSON/SHA records for all 48,252
schema/cell identities one-at-a-time timed out against that cap. Commit `01dc3fe`
("Redesign pumping catalog for guarded replay") replaced the plan with a compact
schema-table + cell-table + witness-interning design (store each distinct witness once,
reference it by index from 48,252 identities) specifically to fit under the guard. The
final commit in range, `813a6d1` ("Resolve blocked catalog log commit"), only rewrites
one log-entry placeholder (`PENDING` → the real short SHA `5bac6d9`) — it is a
bookkeeping fix, not new work.

So: nothing about the old-new-cut covariance identity itself was shown false or
abandoned. As of `813a6d1`, Task 5 (independent verifier + full manifest) and Task 6
(materialized theorem artifact) of their plan are **not yet done** — the certificate is
still mid-construction, with the redesigned compact catalog approach adopted to get
past the timeout. This is worth recording precisely because a blocked *route* would be
valuable negative information for us; a blocked *test harness* is not.

---

## (a) Collision with R6 / R7 / R7c / R8 / R10

**No collision.** Concretely checked against the full file list touched in
`b617123..813a6d1`:

```
.scratch/period_two_intact_boundary_pumping_lemma.md
.scratch/period_two_old_new_cut_endpoint_potential.md
.scratch/period_two_old_new_cut_load_certificate.py
.scratch/period_two_old_new_cut_selector_theory.md
.scratch/test_period_two_old_new_cut_load_certificate.py
AGENTS.md
docs/superpowers/plans/2026-07-29-old-new-cut-load-certificate.md
docs/superpowers/plans/2026-07-29-proof-process-guard.md
docs/superpowers/specs/2026-07-29-old-new-cut-load-certificate-design.md
docs/superpowers/specs/2026-07-29-proof-process-guard-design.md
logs/29-07-2026.md
scripts/run_proof_guarded.py
tests/test_run_proof_guarded.py
```

Every one of these is either (i) word-combinatorics over free products / canonical
shortlex forms for their `A_{n,d}`/`b_{n,d}` period-two apparatus, or (ii) a generic
CPU-safety test-runner utility. None touches ribbon graphs, Neuwirth's criterion,
γ_N/defect, fake-surface complexity/cellular census, ranks 4–6 stably-trivial targets,
spikes, or K×I collapsibility — the objects R6/R7/R7c/R8/R10 are built from. No shared
object, no shared corpus, no shared code, no shared claim. This matches and extends the
"essentially nil" collision verdict already on record in `ROUTE_DIVERGENCE_LOG.md` for
their prior direction (`b617123`) — the new direction is a continuation of the *same*
disjoint MMS02/period-two word apparatus, not a pivot toward our territory.

## (b) Transfer to us — does their machinery bear on R7c's drop floor?

**No forced transfer — the two are answering structurally different kinds of
questions on unrelated objects, and I would flag a claimed transfer here as false.**

R7c's DROP FLOOR needs a tool that can **exclude a joint extremal event**: "the deletion
[`e_0`] is defect-reducing (`X⁻=1`) **and** all three insertions (`J_1`,`J_2`, plus the
spike loop `ℓ`) are simultaneously non-splitting (`X⁺=0`)," over ribbon-graph rotation
systems of a spiked 2-complex, in order to sharpen a pointwise **inequality**
(`defect(C') ≥ defect(ρ(C')) − 2`) into the DROP FLOOR (`defect(ρ(C'))≥4` whenever that
extremal drop occurs).

Codex's two "potential" tools, by contrast:

- The intact-boundary pumping lemma is a shortlex-comparison tool for periodic
  *words* under exponent growth — it has no notion of rotation systems, genus, or
  defect, and produces exact word-order facts, not inequalities on a combinatorial
  count.
- The endpoint potential (§3 above) computes an **exact F₂ equality** via a
  discrete-Stokes telescoping argument over a fixed dependency tree of *provenance/
  chronology* — it is not a monotone quantity, does not bound anything, and there is no
  analogue in it of "excluding a joint configuration of two independent binary events";
  it *sums* contributions along a path, it does not *rule out* a conjunction of two
  conditions.

The one point of genuine, non-forced resemblance is at the level of **proof strategy,
not tooling**: both efforts try to collapse an infinite/family-indexed claim to a small
number of finite boundary cases (their pumping lemma reduces "for all exponents" to a
base case plus affine growth; R7c's REDUCTION reduces "spiked thickenable ⇒ reduced
thickenable" to the single case `defect(ρ(C'))=2`). That is a shared shape of argument,
not a shared or reusable piece of machinery. Importing their apparatus into R7c would be
a category error: it operates on free-product word exponents, not on rotation-system
combinatorics, and it produces parities, not the specific `X⁻=1 ∧ X⁺=0` exclusion R7c
needs. Verdict: **unrelated; no transfer recommended.**

## (c) Transfer to them — what should we hand over?

Three corrections plus one strategic point, all already drafted in
`results/stable_ac/theory/fable/NOTES_FOR_CODEX_LINE.md` (items 10, 11, 12, 16) and
already logged as owed to them in `ROUTE_DIVERGENCE_LOG.md`'s prior entry — but **the
new commits `b617123..813a6d1` show no sign any of the four items have reached them
yet**: a full-diff grep for `Lackenby`, `Fagan`, `Qiu`, `Wang`, `AC1`, `AC2 ` returned
zero hits in the entire commit range. All four remain live and worth relaying:

1. **[CORRECTION] Literature-provenance problem** (item 10, verbatim): *"`literature/`
   is gitignored and ABSENT from cloud clones. Every 'Lackenby arXiv:2606.06122 Thm 1.3'
   citation in the fable line was carried in from an earlier session's context, not
   read. Only the ABSTRACT is sourced ... The theorem's NUMBER, its hypotheses, the
   definition of 'thickenable', whether relators are free-group elements or words, and
   the existence of a 'move (0)' at all are all UNVERIFIED. If your line cites any of
   these, re-verify before relying on them."* Directly relevant: the codex line's own
   CLAUDE.md-inherited trap file documents the identical structural risk (uncloned
   `literature/`), so if any codex proof text carries in a similarly unread citation
   about AC/AK(n)/stable-AC "known theorems," the same failure mode applies to them.
2. **[CORRECTION] Fagan–Qiu–Wang cellular/partial-census correction** (item 11,
   verbatim): *"Fagan–Qiu–Wang's census is CELLULAR and PARTIAL at complexity 5. The
   abstract's theorem is unqualified, but the authors' own README says 'acyclic
   cellular fake surfaces of complexity 1-4 and a partial classification of complexity
   5: surfaces without small disks'. 514 of the 5,389 certified targets come from that
   partial list."* Relevant if any codex representation-variety/Alexander-module
   rejection filter is cross-checked against complexity-5 fake-surface enumerations.
3. **[CORRECTION] AC1/AC2 move-numbering discrepancy** (item 12, verbatim):
   *"`FRAMING.md` had AC1 = multiply / AC2 = invert, contradicting every other file on
   this line. Now fixed to the project convention **AC1 = invert, AC2 = multiply**. If
   you imported any fable phrasing about 'AC2 graft images', it meant MULTIPLICATION,
   not inversion."* Worth flagging because the codex line's own prior scope note refers
   to "a general AC1-AC3 path in which the base rows move" — if that numbering was ever
   cross-checked against fable phrasing rather than the project's own convention, it is
   worth a one-line confirmation.
4. **[STRATEGIC] Class-wide obstruction = disproof, not a negative result** (item 16,
   verbatim): *"Since stable ACC is equivalent to 'every balanced trivial-group
   presentation reaches SOME thickenable presentation by stable AC moves', a proof that
   AK(3)'s stable class contains no thickenable member in any spelling disproves the
   stable AC conjecture. That is why Wall 5 bites and why no such bound is known — audit
   any candidate obstruction with maximum hostility."* Directly actionable for them: per
   §5 above, their whole program is accumulating barrier/obstruction results confined to
   named ansätze. This point tells them exactly what property such a result would need
   (class-wide, spelling-independent, applying to the whole stable-AC-move orbit rather
   than one bridge construction) to escalate from "another finite obstruction" to an
   actual disproof — i.e. it recalibrates how they should value their own obstruction
   work as it generalizes.

One additional, lower-priority item worth a mention: their new `run_proof_guarded.py`
CPU-safety harness (§6 above) independently reinvents the same category of fix as our
own `experiments/lessons/parallel-runs-and-bound-direction.md` trap (detached/duplicate
proof processes overheating a machine). Not a correction to their work, just a
convergent-engineering note they may find validating.

## (d) Divergence recommendation

**What we should deliberately NOT do:** do not build any tooling around free-product
canonical/shortlex word families, powered-block pumping over exponent orthants, or
mod-2 "activity"/collision-fiber bookkeeping for named bridge constructions — that is
now unambiguously codex's territory (period-two apparatus, extended in this range from
one fixed bridge to an `(n,d)`-indexed family of them). Do not spend effort trying to
adapt their endpoint-potential/Stokes machinery to R7c (see (b) above) — it is a
plausible-sounding but false transfer given what it actually computes (an exact parity
via telescoping, not an inequality-producing bound), and forcing it would cost audit
time for no payoff.

**Most complementary next step for us:** stay exactly on the geometric/topological
track already diverging cleanly from them, and specifically prioritize **R7c's own
open case**, since it needs no import from codex at all: settle the single remaining
case `defect(ρ(C'))=2` for the DROP FLOOR reduction, i.e. determine whether the joint
extremal event "`X⁻=1` and `X⁺=0` simultaneously" can occur over a base rotation of
defect exactly 2. `R7C_DROP_FLOOR.md` already names the concrete next instrument
(`experiments/stable_ac/fable/drop_floor_check.py`, "in flight" as of the file's last
edit) and the two caveats that travel with it (the R7 §S4 audit dependency, and that
non-negativity of the Neuwirth defect is verified-not-proved). That is a self-contained,
codex-independent next action, and it is also the item our own route log calls "the
single theorem to prove next" — closing it is worth more than any cross-line import
right now.
