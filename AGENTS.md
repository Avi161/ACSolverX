# ACSolverX agent instructions

### [2026-09-05] Use the proved fixed-donor primitive criterion

[WORKS] Section 6 of `literature/proofs/AK3_ARBITRARY_CONJUGATOR_PRIMITIVE_BARRIER.md`
excludes every primitive recipient from either fixed-donor quotient of
standard AK3, using all primitive slopes, not a search bound. Do not
repeat such donor-only primitive searches. The criterion does not apply
after changing both rows or stabilizing, and coprime exponent sums alone
do not imply primitivity.

### [2026-09-05] Eliminate a proposed tag symbolically before probing

[WORKS] For the AK3 half-twist tag `h=yyyXXXXz`, the product
`s*h=xxxYXXXXz` defines `y=XXXXzxxx`. Under this substitution the
retained `h` is exactly the substituted `s^-1`, so the apparent
stabilized shortcut is only a basis change of the original pair.
Sol's literal return check avoided an unnecessary descent probe.
Before exploring a tagged elimination, substitute into every retained
row and check for this immediate return, not only for shorter words.

### [2026-09-05] Identify the terminal presentation after a strict reduction

[WORKS] The length-fourteen target in
`literature/proofs/AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md` Section 6.89
has a trefoil marking that returns explicitly to standard AK3 in Section
6.90. A strict decrease in one sufficient representative is genuine but
need not simplify the unresolved mathematical problem. Check structural
identifications and retain literal return certificates before extending
another short-target family.

### [2026-09-05] Validate PDF downloads before rendering

[TRAP] The eScholarship dissertation endpoint returned an empty file with
a successful curl status. Check nonzero byte count before rendering; use
an identified primary-source alternative when available. Valid local link
graphs after a transcribed geometric move do not certify the 3-deformation.

### [2026-09-05] Pure power consequences cannot be live rows

[TRAP] The boundary continuation proposed realizing `C^2` and `C^5`
as literal donors. Any balanced trivial-group presentation has a unimodular
exponent matrix, so even one proper-power row is impossible at every
stabilized rank. Keep generator tags or non-power terms in a power-based
AC construction; never promote group consequences to live relators.

### [2026-09-05] Formal return maps are not AC invariants

[WORKS] Tracking generators through the closed boundary corridor exposes
an injective free-group substitution, but does not encode its live donor
operations. Keep the chosen word map separate from the presentation move
sequence; determinant one proves neither surjectivity nor an AC obstruction.

Read `.agents/instructions/core.md` before any work. Then read every route that applies below; referenced Markdown is not discovered automatically.

| Task | Also read |
| --- | --- |
| AC/stable-AC proof, theorem, claim, or substantive plan | `.agents/instructions/ac-theory.md`, `.agents/instructions/process-safety.md` |
| Any computational proof, checker, census, search, test, process cleanup, or long run | `.agents/instructions/process-safety.md` |
| Experiment, benchmark, CoV, notebook, certificate, or result | `.agents/instructions/experiments.md` |
| Commit, staging, branch, checkpoint, or push | `.agents/instructions/git-checkpoints.md` |
| A prior lesson, failure mode, or topic | `.agents/instructions/lessons/README.md` |

Implementation, documentation, and mechanical subagents use `gpt-5.6-terra` (or Luna only if it is available). `gpt-5.6-sol` is read-only: use xhigh for every substantive proof or plan review; reserve ultra for final theorem claims, long-experiment authorization, or unresolved soundness. No subagent may run proof, search, or test computation.

Configuration edits require immediate readback. Record user corrections only in the current dated lesson file under `.agents/instructions/lessons/`, never here. The AC final goal is a correct proof-resolution result; a bounded failure, null search, failed preflight, or intermediate theorem is neither evidence against AC/stable AC nor a final resolution. Follow the routed process and push rules exactly.

## Latest user-directed role boundary

### [2026-09-05] First-principles ownership

[TRAP] Delegating the first-principles choice of AK3 strategy to Sol conflicts
with the user's current allocation of roles. Astra owns mathematical ideas,
strategy, and synthesis. Sol and Terra execute explicitly specified checks,
certificate inspection, or implementation; do not ask them to originate the
research direction. This latest user instruction supersedes earlier strategic
delegation defaults. This lesson is recorded here under the user's replacement
AGENTS.md protocol.

### [2026-09-05] Stable ambient hypotheses

[TRAP] The draft preimage-shift lemma generalized a stable ambient
substitution beyond the trivial-group hypothesis of the cited theorem.
Before promoting a word identity to stable AC, explicitly carry the
balanced trivial-presentation hypothesis through every ambient substitution
and generator-removal step. Free-word replay alone does not check this gate.

### [2026-09-05] Multi-hunk proof-note patches

[TRAP] A proof-note patch failed because its final context omitted text on
the same line. After a context-mismatch error, recheck the literal context
and retry only the intended hunks; do not assume earlier hunks were applied.

### [2026-09-05] Preserve final Magnus height

[TRAP] In the second boundary transport, the draft intermediate word
`ABubbU` accidentally retained an inverse stable letter after the final
height-one factor had cancelled it. The correct word is `ABubb`.
When reconstructing Magnus blocks, freely reduce the full product including
the final stable-letter power before recording or testing donor factors.

### [2026-09-05] Literal peripheral coordinates and small checks

[TRAP] An exploratory meridian calculation reversed `(XY)^-1`: it is
`yx`, not `xy`. A failed finite representation exposed the mismatch;
the corrected source substitution is pinned in the boundary tests.
Verify each proposed peripheral coordinate literally before importing a
knot-group theorem. The guarded Python runtime has no `sympy`; for a
two-by-two finite-field check use exact integer arithmetic, not a new
dependency. Locate optional filenames with `rg --files` before passing
globs to zsh, which rejects an unmatched glob before the command runs.

### [2026-09-05] Check constructive corridors for return cycles

[TRAP] The boundary-automorphism corridor shortened a live coefficient
but its defining-row elimination returned exactly to the original
length-15 pair. Before extending a promising stabilized reformulation,
compare its eliminated endpoint to prior certified representatives and
pin an explicit equivalence if it returns. Preserve the valid identities,
but freeze a demonstrated return cycle instead of counting coefficient
shortening as another net presentation reduction.

### [2026-09-05] Proof-only dependencies and literal data shape

[TRAP] Importing `rank3_whitehead.py` loads `one_edge.py` and then
`acmoves.py`, requiring NumPy and Numba even for pure word reductions.
The standard proof runtime lacks NumPy; the bundled runtime has NumPy
but lacks Numba. Check this chain before launching a probe; do not install
packages or repeatedly switch runtimes for a pure combinatorial check.
`LinkData.vertex_darts` is a dictionary keyed by germ, not a sequence of
stars: access `vertex_darts[v]` explicitly when inspecting degrees.

### [2026-09-05] Separate peripheral tests from AC obstructions

[WORKS] In `AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md` Sections 6.91--6.92,
an explicit knot marking permits a finite-field centralizer test for
peripherality. First check the actual relator and the meridian marking;
then use the image of its whole peripheral subgroup, not just one
meridian conjugacy class. A finite representation can classify these
fixed elements without distinguishing their AC orbits. Do not turn this
geometric witness into another finite-quotient obstruction ledger.

### [2026-09-05] Check original adjunction hypotheses

[TRAP] McDermott §4.2 introduces surjectivity results with an injectivity
framing, but the original Cohen--Rourke Main Theorem (p. 128) assumes only
a torsion-free coefficient group and surjectivity of the natural map.
The initial `logs/05-09-2026.md` audit incorrectly promoted that framing
to a separate theorem hypothesis; Sol caught it and the original source
confirmed the correction. Read the cited theorem itself before recording
its exact hypotheses, even when only excluding an application.

### [2026-09-05] Use literal anchors for TeX proof edits

[TRAP] A TeX-containing `rg` pattern failed with a repetition-quantifier
error, and a patch against a guessed wrapped sentence did not match
`AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md`. Use `rg -F -e` for literal TeX
searches and a read-back, unique heading as an insertion anchor; do not
guess line wrapping in the long proof document.

### [2026-09-05] Do not assume a bundled symbolic algebra package

[TRAP] SymPy is absent from both the proof Python and the bundled Python.
The attempted version-glob package path also failed under zsh's no-match
rule. Use a guarded `importlib.util.find_spec` probe, not guessed package
paths, before designing a dependency-based symbolic calculation. For the
small MMS02 trace checkpoint, exact standard-library sparse Laurent
arithmetic sufficed; no package installation or larger computation was needed.

### [2026-09-05] Determine the power exponent before searching it

[WORKS] `mms02_primitive_completion_probe.py` uses the embedded stage-four
free group and the target's exponent vector `(0,4)` to determine the only
possible integer power for each conjugator. This checks all integer powers
without an exponent cutoff. Verify the actual base relation, signed-power
controls, and the entire saved candidate prefix independently; retain the
conjugator and stage bounds when reporting a negative result.

### [2026-09-05] Descend conjugators before adding stages

[WORKS] The equation in `AK3_MMS02_PRIMITIVE_COMPLETION_TRACE_CHECK.md`
forces each high-stage conjugator coefficient into `im(phi)`, allowing
descent to stage two and two explicit coset substitutions. This converted
an unbounded primitive-completion problem into an integral Fox equation,
whose least-exponent contradiction covers every integer. Before increasing
stage or word caps, check whether the exact equation forces image membership;
retain an integral-versus-mod-two control for coefficient contradictions.

### [2026-09-05] Check the whole height kernel before lifting quotient tests

[WORKS] For the opposite MMS02 donor, `phi0^2(F0)` lies in `F0'`, making
the ascending union's height kernel perfect. Every solvable image is then
cyclic and cannot distinguish the proposed primitive endpoints. The
metabelian-base fixed point has a nonempty literal free-group defect;
never apply embedded-base arguments after the induced monodromy loses
injectivity, or extend a solvable ledger already made vacuous by this kernel.

### [2026-09-05] Count literal letters after adapting the free basis

[WORKS] In the opposite-donor MMS02 equation, the basis `a,q=ba` sends
monodromy to `a -> b, q -> Aba`. Alternating blocks prove that monodromy
cannot decrease the unsigned b-letter count, while the exact required
prefix adds one. This closes all slopes without a quotient tower. Prove
the block cancellations universally and include a changed-prefix positive
control; a count inequality for one pinned coefficient is not an AC invariant.

### [2026-09-05] Resolve filenames and publication versions before auditing

[TRAP] Guessed paths `literature/sources` and `AK3_FULL_LIFT_BOUNDARY.md`
did not exist; `rg --files` locates the actual depth-four audit and boundary
note. The audit was already complete. Also distinguish Lisitsa's original
preprint claim from the corrected final journal abstract, which expressly
does not claim stable AK3. Locate authoritative paths first and check version
status before repeating an audit or attributing an obsolete conclusion.

### [2026-09-06] Replay positive controls through their final live rows

[WORKS] `test_ak2_primitive_donor_transcript.py` upgrades the AK2
quotient-only primitive control to a full ordinary AC transcript ending
at literal `(x,y)`. The symbols `p,z` denote words in the original
generators; they need not be charged as ambient automorphism moves.
Keep restored-donor factors and replay cleanup in original coordinates.
An unsuccessful transfer of this certificate to AK3 is not a new obstruction.

### [2026-09-06] Transferred moves must donate the actual current row

[WORKS] The full AK2 cleanup remains legal on AK3 only when its donor is
the actual `d=YYxYxxYxY`, not the AK2 coordinate word `z=Y(xY)^3`.
The exact resulting rows have lengths 121 and 93, so this transfer is
frozen. A fixed-donor exclusion does not exclude this both-row replay;
check its real endpoint once before deciding whether it offers progress.

### [2026-09-06] Strategy correction: target a constructive three-deformation

[TRAP] Successive donor exclusions and failed transfers did not produce
an AK3 bridge. The user explicitly requested a new first-principles route.
Root now owns an explicit presentation-complex prism construction, aiming
at a verifiable collapse certificate rather than another quotient residual.
Verify the complex and the three-deformation implication first; bounded
collapse failure is neither noncollapsibility nor an AK3 obstruction.

### [2026-09-06] Certify geometric simplifications with global incidence

[WORKS] `AK3_PRISM_COLLAPSE_WORKING.md` gives a three-operation tetrahedral
fold with a strict simplex-count decrease. Its final edge collapse needs
degree exactly two in the entire input complex, not just in the pictured
tetrahedron. Save expansions as well as collapses and independently replay
global cofaces; a terminal monotone reduction is not a general obstruction.

### [2026-09-06] Edge contractions need the full link condition

[TRAP] A common-neighbor test alone accepts every edge of a tetrahedron
boundary, although identifying one would destroy its sphere topology.
`AK3_PRISM_COLLAPSE_WORKING.md` requires common link edges as well as
vertices, and gives explicit dimension-three expansions and collapses.
Credit the classical contraction theorem; novelty of an AK3 application
does not make its underlying local move a new theorem.

### [2026-09-06] A smaller complex can return to the same AK3 presentation

[WORKS] The prism corridor reaches a 19-vertex complex, but its recorded
tree presentation and 58 defining deletions give `(a^2 B)^3 a^4, b a B a B a`.
The basis `x=a^2 B, y=A` returns exactly to standard AK3 after one relator
conjugation. Freeze this corridor: fewer simplices alone do not justify
another search when the terminal presentation explicitly returns.

### [2026-09-06] Rebuild the quotient after a genuine donor change

[WORKS] Retaining `R=Abar Bbar` changes the MMS02 quotient to an explicit
rank-five free-by-cyclic model, unlike either original fixed-donor model.
Check the monodromy and its inverse literally before claiming an embedded
base. The resulting primitive gate has one subsequent evaluation checkpoint;
do not turn a new presentation model into an expanding quotient ledger.

### [2026-09-06] Changed-donor budget spent: A5 gives no restriction

[WORKS] The complete 240-pair A5 covering table for `R=Abar Bbar` has
only cyclic and order-ten dihedral images. Every primitive slope passes,
even when conjugators are restricted to the image of the free base.
The preceding one-checkpoint allowance is [SUPERSEDED] by this completed
evaluation: freeze this changed-donor route, with CD7 still unsolved.
Do not extend to another finite group, nilpotent layer, or word census.

### [2026-09-06] Check local type before invoking fake-surface complexity

[TRAP] The certified 19-vertex prism endpoint has five triangles at edge
`(0,2)` and is not a closed fake surface. A small simplicial vertex count
is not fake-surface complexity. Check the local-type hypothesis first;
one failed edge incidence ends this applicability audit without reopening
the frozen deformation corridor or implying an AK3 obstruction.

### [2026-09-06] Prefer subgroup structure for primitivity reflection

[WORKS] `AK3_PARAFREE_STABLE_SELF_EMBEDDING.md` Sections 7 and 11
do not need Klyachko or Magnus to reflect primitivity through an injection.
An ambient primitive element in a subgroup is a distinguished loop in its
Schreier graph and belongs to a spanning-tree basis. Check this elementary
free-factor argument before importing quotient-embedding machinery;
retain that machinery only where actual quotient embeddings are asserted.
After replacing a proof, search the whole document for the removed
dependency names: the final review caught a stale Section 10 attribution.

### [2026-09-06] Separate stable-substitution scope from family-specific bounds

[WORKS] In `AK3_PARAFREE_STABLE_SELF_EMBEDDING.md` Section 6, the
tag-replacement construction needs only `u(1,r)=r`, not conjugacy of u
to r. Collect X-letters by their preceding signed r-height to expose
the exact old-donor product. This broadens the legal construction, but
does not extend the later external-conjugator bounds beyond their
stated conjugating family or justify a new search ledger.

### [2026-09-06] Preflight transitive dependencies before bounded checks

[TRAP] The inverse-substitution preflight failed before enumeration because
`rank3_whitehead` imports `one_edge`, then `acmoves`, then unavailable NumPy.
Use the standard-library Whitehead helpers in `mms02_terminal_hnn_certificate`
for this small rank-two check; validate imports and controls before spending
the single enumeration budget. Do not install a numerical stack for word reduction.

### [2026-09-06] Separate basis screening from primitive containment

[WORKS] The 82-quotient AK3 overgroup certificate leaves only K and F2,
but nonprimitive members of a chosen K basis do not exclude other primitive
elements of K. Close that gap with the sign-restricted directed-cycle proof
on the saved core, not an unbounded basis enumeration. The resulting theorem
excludes this fixed-pair inverse-substitution criterion only, not stable AK3.

### [2026-09-06] Extract the full consequence of a complete overgroup list

[WORKS] For the fixed AK3 pair, H=K or F2 classifies every endomorphism
whose image contains both rows: an automorphism or eta precomposed with
an automorphism. A basis preimage under eta is automatic, not an AC
certificate. Separate that algebraic factorization from legal stable
transport; do not spend another search budget rediscovering such preimages.

### [2026-09-06] Prove immersion before using an axis picture as a core

[WORKS] The standard AK3 conjugation--Nielsen barrier uses a maximal
axis intersection or shortest bridge. Distinct outgoing labels and overlap
shorter than both periods certify the barbell/wedge/theta is already folded.
Do not infer a subgroup theorem from an axis sketch without this check;
keep initial conjugations followed by Nielsen moves separate from interleaving.
