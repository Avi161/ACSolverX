# Route divergence log — keeping the fable line complementary to codex

Checked every 30 minutes (an automated monitor fetches `origin/codex/proofs` and reports
new commits with the files they touch). Each entry records what the codex line is doing,
what this line is doing, and where the two could collide.

## 2026-07-29 ~21:50 UTC — codex at `813a6d1` (full analysis: `CODEX_CHECK_813a6d1.md`)

**Their apparatus changed; their scope did not.** New work is a *period-two old–new cut
load certificate* plus an *intact-boundary pumping lemma*, *endpoint potential* and
*selector theory* — 6,686 insertions across `.scratch/` and `docs/superpowers/`. Substance:

* the **load certificate** is a verification harness for ONE open lemma inside their
  existing depth-4/6 AC2 period-two census on AK(3), certifying the mod-2 covariance
  identity `B(A_{n+1,d}, b_{n+1,d}) = B(A_{n,d}, b_{n,d})`. "Load" = one unit of
  verification work (source-fibre × cell); it is not a new mathematical object.
* the **pumping lemma** is word combinatorics, not an AC claim: for powered words indexed
  by an orthant `x_0 + N^k`, inserting more copies of a periodic block at an "intact"
  splice point reproduces the true shortlex-reduced form — converting finite spot-checks
  into all-exponent statements.
* the **endpoint potential** is **NOT a monotone or bound-producing potential.** It is a
  discrete-Stokes telescoping identity over F_2: `psi_T(x) = sum omega_T(e)` along tree
  edges, giving `B(eta([x,y]), T) = psi_T(x) + psi_T(y)` **exactly**. It computes a parity
  *equality*, so the upper-vs-lower-bound question does not even apply to it.

**Scope, verbatim, and still ansatz-confined:** *"This certificate is not, by itself, an AC
or stable-AC trivialization of AK(3). It is one lemma in the current proof route."* and
*"Nothing here proves or refutes Andrews--Curtis or stable Andrews--Curtis."* The
generalisation is along the `(n,d)` axis **inside** their fixed named construction; it has
not become class-wide.

**Their three "blocked" commits are ENGINEERING, not a dead route.** Serializing full
JSON/SHA for 48,252 templates exceeded their own 30-second CPU guard, so they moved to a
compact schema/witness table. Their log: *"no independent replay or theorem claim has yet
occurred."* No route was declared mathematically dead — so nothing is freed up for us.

**Collision: NONE**, verified against the full file list of `b617123..813a6d1` — no ribbon
graphs, no γ_N, no fake surfaces, no collapsibility anywhere in the range.

**Transfer to us: NONE, and the near-miss is worth recording as a trap avoided.** Their
potential looked, from the commit titles alone, like exactly the tool R7c needs. It is not.
R7c must EXCLUDE a joint extremal event (`X⁻ = 1 ∧ X⁺ = 0`) in rotation-system
combinatorics; their machinery ESTABLISHES an exact parity by telescoping. Different
objects, and — more decisively — different shapes of question: equality versus exclusion.
The only resemblance is strategy-level (both reduce an infinite family to finite boundary
cases), which is not reusable tooling. **Do not import it.**

**Transfer to them: still undelivered.** A grep of the whole commit range for
Lackenby / Fagan / Qiu / Wang / AC1 / AC2 returns zero hits, so `NOTES_FOR_CODEX_LINE.md`
items 10, 11, 12 and 16 have not reached them. Item 16 is the one that matters most as
their obstruction program generalises: **a class-wide thickenability obstruction would be a
DISPROOF of stable ACC, not a negative result.** Relaying it requires the user to merge
this branch — cloud sessions cannot push to their branch.

**Divergence decision.** Free-product / shortlex / pumping tooling is now unambiguously
theirs; this line will not build any. Our complementary next step is unchanged and
independent of everything above: close R7c's single remaining case, `defect(ρ(C')) = 2`.

## 2026-07-29 ~16:45 UTC — codex at `b617123`

**Their direction: ALGEBRAIC OBSTRUCTION THEORY on the MMS02 Wirtinger corridor.**
Recent commits — *Refresh covariance certificate hashes*, *Narrow the MMS bridge and
seven-family defect*, *Filter MMS02 bridge symmetries by Alexander module*, *Certify the
rank-three sign quarantine*, *Isolate the MMS02 rank-three bridge*, *Repair the MMS02
Wirtinger corridor*. The tools are:

* **representation varieties** — an `A5` representation variety used as a decidable
  rejection filter (it rejects 2,523 of the 2,527 automorphisms in the depth-3 Nielsen
  ball outright);
* **Alexander modules** — used to reject the surviving involutions;
* **Nielsen balls** of bounded elementary length in a frozen alphabet, enumerated exactly;
* **formal identity certification** — the seven-family covariance work, proving all-power
  identities like `Q(b_{n+1,d}) = Q(b_{n,d}) = 1` with accompanying checkers and manifest
  hashes.

Their own scope note, which is exactly the right one to respect: *"This proves a finite,
exact obstruction to the named ansatz. It is not an obstruction to a general AC1–AC3 path
in which the base rows move."* So they are bounding **named bridge ansätze** in the
rank-3 MMS02 corridor, not the AC class itself.

**Our direction: GEOMETRIC / TOPOLOGICAL, and disjoint from all of that.**

| | codex line | fable line |
|---|---|---|
| object | words in F(x,y,z), the MMS02 bridge rows | the presentation 2-complex and its thickenings |
| tools | A5 representation variety, Alexander module, Nielsen balls, formal identity certificates | Neuwirth's criterion / γ_N, ribbon-graph defect calculus, fake surfaces, collapsibility |
| target | finite exact obstructions to named bridge ansätze | a thickenable / 3-deformable / collapsible witness, or a class-wide obstruction |
| direction of proof | negative (rule out a mechanism) | positive (produce a certificate), with the negative recognised as the DISPROOF |

**Collision surface: essentially nil, and the one contact point is trivial.** The only
place our machinery touches theirs is the abelianised relation matrix — R6 uses `|det| = 1`
as a necessary check on the 5,389 certified targets, which is the crudest shadow of the
Alexander module they are using seriously. There is no shared code, no shared corpus, and
no shared claim.

**Where we deliberately diverge further.** Their obstruction toolkit is the natural one for
separating AK(3) from standard by an invariant. We are NOT going to duplicate that. Ours
is the complementary half: certificates that would settle AK(3) affirmatively —

* **R7 / γ\***: spelling space, the spike ceiling, and the implication *spiked thickenable
  ⇒ reduced thickenable*;
* **R8**: AK(3)'s fake-surface complexity — if ≤ 5 the Fagan–Qiu–Wang theorem settles it;
* **R10 / Zeeman**: is AK(3)'s `K × I` collapsible? A collapsing sequence is a complete,
  replayable positive certificate;
* **R6**: meet-in-the-middle against certified stably-trivial targets at ranks 4–6.

**What we should hand them, and have** (`NOTES_FOR_CODEX_LINE.md` items 10–18): the
literature-provenance correction (their citations may share our unsourced Lackenby
dependency), the FQW cellular/partial-census correction, the AC1/AC2 numbering fix, and
the strategic point that a class-wide thickenability obstruction is the DISPROOF rather
than a negative result — which is directly relevant to how they should value their own
obstruction work.

**What we would want from them.** Their Alexander-module and representation-variety
filters are exactly the kind of tool that could give a *spelling-independent* lower bound
on γ_N if one exists (R7's Q1). If they ever produce an invariant that is constant on a
whole AC class rather than on a named ansatz, that is the object this line has been unable
to construct, and it should be relayed immediately in both directions.
