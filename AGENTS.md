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
