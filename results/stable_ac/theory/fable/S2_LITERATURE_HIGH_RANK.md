# S2 — literature verification for the high-rank / triangulation line

Session: `claude/stable-ac-conjecture-stabilization-rwo9as` (fable line; must be merged into
`fable/proof` by the user). Task A2 of `S0_HIGH_RANK_PLAN.md`. Written 2026-08-04.
This file only ADDS; it edits nothing. Where it contradicts an existing file, the
contradiction is stated explicitly in §7 so a human can adjudicate.

## 0. Verification vocabulary used below

The task asked for three statuses. One extra distinction turned out to be necessary,
because a genuinely new channel opened this session:

| tag | meaning |
|---|---|
| **VERIFIED-FROM-SOURCE** | I opened the artifact myself, in this session, on this disk or through a working transport, and the quotation below is copied out of it. The file path / URL is given. |
| **SOURCE-RELAYED** | The `WebSearch` tool's answer synthesiser demonstrably read the primary PDF (`arxiv.org/pdf/2606.06122`) and relayed body text — definitions, lemma statements, move lists — that is not in the abstract and not in any indexed snippet I could otherwise reach. **I never opened the file.** I cannot rule out paraphrase or synthesiser error, so this is *not* verbatim. Treated as a strong secondary channel, not as source. |
| **SECONDARY-ONLY** | A restatement by someone else (another agent line in this repo, or a third-party page). |
| **UNVERIFIABLE-THIS-SESSION** | Nothing reachable settled it. |

**Network reality this session** (differs from
`experiments/lessons/cloud-session-network-and-push-constraints.md` — see §8):

* **BLOCKED**: `WebFetch` on *every* URL tried (arxiv.org/abs, arxiv.org/pdf,
  ar5iv.labs.arxiv.org, alphaxiv.org, huggingface.co/papers, api.semanticscholar.org) →
  HTTP 403. `curl` to arxiv.org, export.arxiv.org, and even example.com →
  `CONNECT tunnel failed, response 403`.
* **WORKS**: `git clone` over HTTPS to github.com (arbitrary public repos);
  `raw.githubusercontent.com`; the GitHub MCP `search_code` tool (searches all of GitHub,
  though `get_file_contents` is allow-listed to `avi161/acsolverx` only); and **`WebSearch`,
  including its ability to read the body of a proxy-blocked arXiv PDF** (new — §8).
* `literature/` in this clone contains only `literature/fake_surfaces/` (3 files, tracked
  via `git add -f`). `git ls-tree` across **all** fetched branches
  (`origin/codex/proofs`, `origin/research/w5/stable-ac-escape`,
  `origin/cursor/heur-u124-s20mk2-a42e`, `origin/claude/ac-stable-ac-conjecture-ijfzgz`)
  confirms **`literature/txt/lackenby_stable_ac_thickenable.txt` is not tracked anywhere**.
  The Lackenby text is genuinely absent from the repo.

---

## Q1. Lackenby, arXiv:2606.06122 — Theorems 1.1/1.2/1.3 and "thickenable"

**Status: abstract VERIFIED-FROM-SOURCE; everything else SOURCE-RELAYED + SECONDARY-ONLY,
with two mutually independent channels agreeing on every overlapping point.**

### 1.1 What I opened myself

`git clone --filter=blob:none --sparse https://github.com/ehijano/rss_fetch`, file
`rss_data/math.GR/2026-06-04_math.GR.xml`, read off disk this session. Verbatim:

> `<title>`The stable Andrews-Curtis conjecture and thickenable presentations of the
> trivial group`</title>`
> `<description>`arXiv:2606.06122v1 Announce Type: new
> Abstract: We establish an explicit upper bound on the number of stable Andrews-Curtis
> moves that convert thickenable balanced presentations of the trivial group to the
> standard one-generator presentation. We also present a proof that thickenable balanced
> presentations of the trivial group satisfy the (unstable) Andrews-Curtis conjecture.
> `</description>`
> `<guid isPermaLink="false">`oai:arXiv.org:2606.06122v1`</guid>`
> `<dc:creator>`Marc Lackenby`</dc:creator>` — categories math.GR, math.GT; CC BY 4.0.

**Version check (new, and worth having):** the mirror runs to `2026-08-03`, i.e. yesterday,
and a grep over every math.GR/math.GT feed file finds only `2606.06122v1`, 8 occurrences,
no `replace` announcement. **There is no v2.** Any future session citing "v1" is safe.

**No LaTeX source mirror exists.** GitHub code search for `"2606.06122"`,
`"Lackenby" "thickenable"`, `"Andrews-Curtis" "Lackenby" language:tex`, and
`"Andrews-Curtis" extension:tex` returns only the RSS mirrors, two unrelated agent-log
repos, and `ammedmar/ac_paper`. This reproduces the earlier session's finding.

### 1.2 What the search backend relayed out of the PDF (SOURCE-RELAYED)

`WebSearch` queries loaded with many in-document technical terms caused the synthesiser to
read `https://arxiv.org/pdf/2606.06122` and return body text. Generic queries returned only
the abstract; the technical ones returned the following, across four separate calls:

* **Definition of thickenable.** "A group presentation P is thickenable if its associated
  2-complex K embeds in some 3-manifold. Its regular neighbourhood N(K) admits a natural
  handle structure, where each i-cell of K thickens to an i-handle" — and when K comes from
  a balanced presentation of the trivial group, "N(K) is a compact contractible 3-manifold,
  and by Perelman's solution to the 3-dimensional Poincaré conjecture, N(K) is therefore a
  3-ball."
* **The move list.** "(0) remove or introduce xi xi^(-1) or xi^(-1) xi in some relation rj;
  (1) replace some ri by ri^(-1); (2) replace some ri by ri rj or rj ri for some j ≠ i;
  (3) replace some ri by xj ri xj^(-1) or xj^(-1) ri xj for some j"; and "(4) add a
  generator x(n+1) and a relation x(n+1), or the reverse … provided the remaining relations
  do not include the letters x(n+1) or x(n+1)^(-1)". Stable ACC = reduce to ⟨x₁|x₁⟩ with
  (0)–(4).
* **Move (4⁺).** "given any word w of length at most 2 in the generators x₁,…,xₙ and their
  inverses, one introduces a new generator x_{n+1} and a new relation x_{n+1}w⁻¹, or the
  reverse of this operation, provided the remaining relations do not include the letters
  x_{n+1} or x_{n+1}⁻¹. While words w of any length could theoretically be allowed without
  changing the group, restricting to length at most 2 avoids having infinitely many possible
  moves from an algorithmic perspective."
* **Lemma 3.1 (the triangulation lemma — see Q3).** "for a balanced thickenable presentation
  of the trivial group with n generators and length ℓ, there is a sequence of at most
  5ℓ(n+1) moves of type (0)-(4⁺) taking P to a thickenable **triangular** presentation with
  at most ℓ generators and ℓ relations or to the standard one-generator presentation." A
  second call gave the coarser form "at most 5ℓ² moves".
* **Proof architecture.** "The approach involves subdividing the presentation complex so
  that each 2-cell is a triangle, then capping off with a triangulated 3-ball to form a
  triangulation of the 3-sphere"; "the number of tetrahedra in the triangulated 3-ball is at
  most twice the number of relations"; "Any two triangulations of a compact 3-manifold
  differ by a sequence of Pachner moves, and in the case of the 3-sphere, there are good
  bounds on the number of moves required, due to Mijatovic and King"; "the upper bound on
  the number of stable Andrews-Curtis moves is a double exponential function. A broader set
  of moves can be expressed in terms of stable Andrews-Curtis moves, but doing so increases
  the number of moves exponentially." The stated obstacle: "Pachner moves modify the Euler
  characteristic of the 2-skeleton of the triangulation, whereas stable Andrews-Curtis moves
  leave the Euler characteristic of the presentation 2-complex unchanged."
* **Relator convention.** "In the paper, the relations in a presentation are viewed as
  elements of the free semigroup generated by the generators and their inverses."

### 1.3 The independent in-repo channel (SECONDARY-ONLY)

`origin/codex/proofs` contains notes written in a session that *did* have
`literature/txt/lackenby_stable_ac_thickenable.txt` on disk. They are a different channel
from the search backend and were written before it. Two files restate Theorem 1.3 in the
same words:

* `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md:17` —
  > **Thm 1.3 (unstable ACC):** "Any thickenable balanced presentation of the trivial group
  > can be converted to a standard presentation using Andrews-Curtis moves."
* `literature/proofs/AK3_NEUWIRTH.md:448` —
  > "Lackenby's Theorem 1.3 states that every thickenable balanced presentation of the
  > trivial group can be converted to a standard presentation by Andrews–Curtis moves,
  > **without stabilization**."
  (its reference list cites "arXiv:2606.06122v1, Theorem 1.3, Remark 1.4, and Section 3.1")

and `.claude/agents/ac-advisor.md:46–52` records the surrounding results:

* **Thm 1.1** — Bridson (rank ≥ 4) and Lishak (rank 2) lower bounds: AC-trivializable
  presentations of length ≤ 24(ℓ+1) needing a tower of 2s of height log₂ ℓ; both survive
  stabilization.
* **Thm 1.2** — thickenable balanced presentation of 1 of total length ℓ has
  `SAC(P) ≤ 2^(2^(cℓ²))` with `c = 2·10⁶`. Route: Perelman ⇒ N(K) is a 3-ball; triangulate
  (t ≤ 2ℓ tetrahedra); Mijatović's Pachner bound `a·t²·2^(b·t²)` (a ≤ 6·10⁶, b ≤ 5·10⁴);
  auxiliary-trees device to track presentations through Pachner moves keeping χ = 1;
  convert to stable AC.
* **Thm 2.6 / Prop 2.5 / Lemma 2.4 / Lemma 2.2** — with moves (0)–(6) the budget is a
  *single* exponential `2^(kℓ²)`, `k ≤ 7·10⁵`, and intermediate length stays `≤ 2^(kℓ²)`;
  re-expressing in pure stable AC costs the second exponential (Prop 2.5: `4^(12Lm+3)`;
  advisor elsewhere quotes `4^(m+3)` for the (0)–(4⁺) collapse, Prop 2.1). Lemma 2.4: each
  Nielsen move ≤ 10ℓ+3 moves of type (0)–(4⁺).
* **Thm 6.4** — end-at-standard collapse of a Q*-derivation; needs the standard endpoint;
  does **not** license the unstable pairwise automorphism principle.
* **Open questions the paper states**: polynomial Pachner bound for S³; a simple stable-move
  route to thickenability ("deemed remote"); Magnus's trivial-group recognition problem;
  **an effective bound for Thm 1.3** — i.e. Thm 1.3 carries *no* move bound.

The two channels agree on: the definition of thickenable, Perelman ⇒ 3-ball, the (4⁺) move
with |w| ≤ 2 and *why* it is capped, Lemma 3.1 as a triangulation step, §3.3 capping with a
triangulated ball, Mijatović, the double exponential, and the free-semigroup convention.
I found **no point on which they disagree.**

### 1.4 Direct answers to the four sub-questions

1. **Does "thickenable + presents the trivial group" ⇒ AC-trivializable?** Yes, that is
   exactly the shape of the result, and the abstract (source-verified) states it in the
   unqualified form "thickenable balanced presentations of the trivial group satisfy the
   (unstable) Andrews-Curtis conjecture".
2. **Is balancedness required?** **Yes.** It is in the abstract's hypothesis, in both codex
   restatements, and in Lemma 3.1's own statement as relayed. The S-line must never drop it.
   (It is automatic for us: AC1–AC5 preserve balance.)
3. **Is there a rank restriction — does it hold at rank 9?** **No rank restriction was found
   in any channel.** The abstract says "presentations", not "two-generator presentations";
   Lemma 3.1 as relayed is stated for "n generators and length ℓ" with n a free parameter;
   neither codex restatement mentions rank. Bridson-vs-Lishak in Thm 1.1 shows the paper is
   comfortable ranging over ranks. **Confidence: high but not source-verified.** This is the
   single most important negative finding for the S-line, because rank 9 is where we live.
4. **Is the conclusion unstable AC-trivial or stably AC-trivial?** **Unstable** — Thm 1.3
   gives AC-triviality using (0)–(3) only, no stabilization ("without stabilization",
   `AK3_NEUWIRTH.md:448`). Thm 1.2 separately gives the explicit *stable* bound. This is the
   stronger of the two readings and it is the one the S-line wants: a thickenable P_Δ at
   rank 9 would be AC-trivializable *at rank 9*, and `P ~st P_Δ` then gives P stably
   AC-trivial. That chain (S0 §3) is sound **given** Thm 1.3 as restated.

### 1.5 A gap in `LITERATURE_STATUS.md` that this pass closes, and one it does not

* `LITERATURE_STATUS.md` §1 flags: "**no source anywhere confirms the paper contains a move
  labelled (0) at all**". It does. The relayed move list gives (0) explicitly, and it is
  free *insertion or deletion* of `xᵢxᵢ⁻¹` inside a relation — i.e. free reduction in both
  directions, **not** cyclic reduction. Files in this line that gloss "move (0)" as
  "free/cyclic reduction" are over-reading it by the cyclic part. [SOURCE-RELAYED]
* `LITERATURE_STATUS.md` §4 **Joint A** ("is an unreduced spelling in the theorem's scope?")
  now leans **favourably**: relations are free-semigroup words in §§1–5, and move (0) exists,
  so an unreduced spelling is a *bona fide* presentation of the framework and is joined to
  its reduction by (0)-moves. If a thickenable unreduced spelling P′ exists, Thm 1.3 applies
  to P′ and the (0)-moves carry the conclusion to P. **This is now a two-channel inference,
  not a source read — keep the flag, downgrade the alarm.**

---

## Q2. "Lemma 11" — which paper, what statement

**Status: VERIFIED-FROM-SOURCE.** It is **not Lackenby's.**

Lemma 11 is **Lemma \ref{lem:substitution}, "Substitution and Removal", of
arXiv:2408.15332** (Shehper, Medina-Mardones, Fagan, Lewandowski, Gruen, Qiu, Kucharski,
Wang, Gukov, *What makes math problems hard for reinforcement learning: a case study*).
I cloned the authors' own LaTeX source, `github.com/ammedmar/ac_paper` @ `d86984d`
(2025-01-11, the v2 era), and read `sec/stable.tex`. Lines 28–30, verbatim:

> \begin{lemma}[Substitution and Removal]\label{lem:substitution}
>     Let $P=\langle x_1,\ldots, x_n, y \mid r_1,\ldots, r_n, y^{-1}w\rangle$ be a
>     presentation of the trivial group, where $w$ is a word in $x_1,\ldots,x_n$. Then
>     $P'=\langle x_1,\ldots, x_n \mid r_1',\ldots, r_n'\rangle$ is stably AC-equivalent to
>     $P$, where $r_i'$ is $r_i$ with all occurrences of $y$ replaced by $w$.
> \end{lemma}

The proof (same file, lines 31–33) is the one this line has been paraphrasing: substitute,
observe $\widetilde P$ trivial ⇒ $P'$ trivial ⇒ $w = w_1 (r_{i_1}')^{\pm1}w_1^{-1}\cdots
w_m (r_{i_m}')^{\pm1}w_m^{-1}$, "**Note that $m$ may be much larger than $n$**", then
(AC1)–(AC3) turn $y^{-1}w$ into $y$ and (AC5) removes it.

**The number.** The paper numbers every environment off one shared `theorem` counter
(`aux/usualcmds.tex:2–21`, no section prefix). Counting numbered environments in document
order — `sec/conjecture.tex:57` Definition (Substitution) = 1; `sec/search.tex` 165, 187,
217, 227, 232, 264, 289, 301 = 2–9; `sec/reinforcement.tex:165` = 10 — puts
`lem:substitution` at **11**. So "Lemma 11" is correct for this source snapshot. (The codex
line files it as "§9"; in this snapshot `sec/stable.tex` is **§8**. Trivial discrepancy,
almost certainly a version difference; do not cite a section number for it.)

**The cost claim in FRAMING trap 6 is right, and is the authors' own words** —
`sec/stable.tex:38`, verbatim:

> "For substitution, the number of AC moves constituting the supermove is a linear function
> of the lengths of the relators (see \cref{sec:AC}). In contrast, **our proof of
> \cref{lem:substitution} does not yield a similar result** for the *substitution and
> removal* move due to the absence of a bound on $m$. Finding this bound, or discovering an
> alternative proof of the lemma that establishes such a bound on the number of AC moves
> packaged into this supermove, would be very useful."

**Consequences for the S-line.**

* Lemma 11 is *exactly* the S0 §1 **(S-a) free-definition move**, in the removal direction.
  (S-a) says a stabilized `z` may be redefined to any `w`; Lemma 11 says a generator defined
  by `y⁻¹w` may be eliminated. Same mechanism, same proof (write `w` as a product of
  conjugates of relators), same sharp hypothesis: **the group must be trivial**. So S0's
  (S-a) is not new — it should be cited as Lemma 11 of arXiv:2408.15332 rather than
  re-proved as though novel. (Re-proving it for self-containment is fine; claiming it is
  not.)
* The move count is **unbounded, not exponential**. FRAMING trap 6 bundles "Lemma 11 /
  Lackenby (4⁺)" together as "cost exponentially many elementary moves". Two different
  facts: Lackenby's (4⁺) → stable-AC conversion is *exponential* (`4^(m+3)` / `4^(12Lm+3)`);
  Lemma 11's packaged count is **not known to be bounded at all** (no bound on `m` — the
  authors call finding one an open problem). S0 trap T-S5 has the same conflation.
  The operational rule is unchanged and correct: never quote a move count across it.

---

## Q3. Is the triangular normal form known?

**Status: SOURCE-RELAYED (Lackenby) + SECONDARY-ONLY (classical). The answer is YES, twice
over. The S-line must cite, not claim novelty.** This is the most consequential finding in
this file.

### 3.1 Lackenby already does it — Lemma 3.1

Relayed from the PDF (§1.2 above): "for a balanced thickenable presentation of the trivial
group with n generators and length ℓ, there is a sequence of at most 5ℓ(n+1) moves of type
(0)-(4⁺) taking P to a thickenable **triangular** presentation with at most ℓ generators and
ℓ relations or to the standard one-generator presentation", and the proof strategy is
"subdividing the presentation complex so that each 2-cell is a triangle". The codex line
independently records "Lackenby Lemma 3.1: reduce to relators of length ≥ 3 first"
(`NEUWIRTH_FEASIBILITY.md:149`) and "§3.3: subdivide 2-cells to triangles, cone the boundary
S² over a vertex avoiding length-1/2 cycles — Lemma 3.2" (`:70`). Two channels, same lemma.

**What is and is not the same as the S0 Triangulation Lemma.**

| | Lackenby Lemma 3.1 | S0 §1 (S-b) Triangulation Lemma |
|---|---|---|
| hypothesis | balanced, trivial group, **thickenable** | balanced, trivial group, **any** |
| moves | (0)–(4⁺) | AC4 + AC1–AC3 only, no destabilization |
| conclusion | **thickenable** triangular presentation | triangular presentation |
| terminal rank | ≤ ℓ generators, ℓ relations | n + Σᵢ max(0, len(rᵢ)−3) |
| move count | ≤ 5ℓ(n+1) | not counted (correctly) |

The differences are real — Lackenby's version *carries thickenability along*, which is the
whole point of his proof and is strictly stronger than ours, and ours applies to
non-thickenable inputs, which his does not claim. But the **transformation itself is his**,
and "every balanced presentation of 1 is stably AC-equivalent to a triangular one" is a
weakening of his Lemma 3.1 in the hypothesis and a weakening in the move set. **Write A1 up
as "Lemma 3.1 without the thickenability hypothesis and inside AC4+AC1–AC3", not as a new
lemma.**

### 3.2 The construction is classical, and "triangular presentation" is standard terminology

Relayed by `WebSearch` from arXiv:1501.02418 (Ken'ichi Yoshida, *Stable presentation length
of 3-manifold groups*):

> "A triangular presentation of a group can be obtained by dividing a k-gon of a
> presentation complex into k−2 triangles, resulting in a presentation where each relator
> has word length equal to 2 or 3. If a group has no 2-torsion, we can assume that each
> relator has length 3." … "the presentation length (also known as **Delzant's T-invariant**)
> is defined as the minimum over all presentations of Σ max(0, |relator| − 2) … the minimal
> number of triangles in a presentation complex."

Arithmetic check against S0: dividing a k-gon into k−2 triangles introduces k−3 diagonals
(new generators) and replaces 1 relator by k−2, i.e. **+(k−3) generators and +(k−3)
relators — balance-preserving**, and it reproduces S0's N = n + Σᵢ (|rᵢ|−3) exactly. So S0's
count is right and its construction is the polygon triangulation, under a name that has been
in the literature at least since Delzant's T-invariant. Matveev's complexity theory uses the
same object (`arXiv:math/0412187`, *Complexity and T-invariant of Abelian and Milnor groups,
and complexity of 3-manifolds*).

### 3.3 A live lead this turns up

`LITERATURE_STATUS.md` §3 records the Fagan–Qiu–Wang dictionary as (V+1 generators, V+1
relators, total relator length 3V+3). Average relator length is **exactly 3**. So the
fake-surface census that R6 targets *is* (up to relators of length < 3) a census of
**triangular presentations**, and Fagan–Qiu–Wang's induction scheme for stable ACC is
already a triangular-presentation programme. The S-line and R6 are looking at the same
normal form from two directions; that should be checked before either claims independence.
[DERIVED here from §3 of the ledger; not read from 2412.12293.]

### 3.4 What is NOT known, and is where the S-line's novelty must live

Nothing found asserts, for **non-thickenable** inputs, anything about *which* triangulation
to pick, or that the triangulation family contains a thickenable member. The open, unowned
questions are:

* the **γ_N profile of the triangulation family** of a fixed hard presentation (S0 §2's
  cheap-census observation) — no prior art found;
* whether AK(3)'s rank-9 triangulations contain a thickenable member — Lackenby explicitly
  makes **no** claim about AK(n) or MS presentations being thickenable (codex advisor,
  `:51`), and "anything known thickenable would already be settled by Thm 1.3";
* Lackenby lists "a simple stable-move route to thickenability" among his **open questions**
  and calls it *remote*. The S-line is attacking a problem its own primary source calls
  hard. That is not a reason to stop; it is a reason not to expect a short proof, and a
  reason to make the experiment (does a thickenable triangulation exist?) the deliverable
  rather than the transfer theorem.

---

## Q4. The bounded-stabilization hierarchy, AK(3) at rank ≥ 3, searches at rank ≥ 4

**Status: UNVERIFIABLE-THIS-SESSION in the strong sense that repeated targeted searching
found no literature on the hierarchy at all — which is itself the answer worth recording.**

* **Is `~^{(k)}` (≤ k stabilizations) studied? Is it known to be strict?** No paper found.
  Searches for the hierarchy, for "one stabilization", and for `AC_k`-style bounded-
  stabilization results returned only the standard stable/unstable dichotomy. The nearest
  things in the literature are different objects:
  * **Gilman–Myasnikov, arXiv:2506.23031v2, *Andrews-Curtis groups*** (abstract
    VERIFIED-FROM-SOURCE from the RSS mirror, `rss_data/math.GR/2025-07-02_math.GR.xml`):
    studies `AC_k(G)` = the permutation group induced by AC transformations on
    `N_k(G) ⊂ G^k`, and the epimorphism `λ: FAC_k(G) → AC_k(G)`; proves λ is an isomorphism
    for non-elementary torsion-free hyperbolic G. **`AC_k` there indexes the tuple length,
    not a stabilization budget.** Do not let the notation collide with S0 §4's `~^{(k)}`.
  * **Borovik–Lubotzky–Myasnikov, *The Finitary Andrews-Curtis Conjecture*** (2005;
    arXiv:1103.1295) — describes connected components of AC graphs of *finite* groups;
    conclusion is "a computation in finite groups cannot lead to a counterexample". Not a
    stabilization hierarchy. [SECONDARY-ONLY]
* **AK(3) at rank 3, 4, …** Nothing found. AK(3) is universally discussed at rank 2.
* **Any published search at rank ≥ 4?** None found. Havas–Ramsay 2003 (*Breadth-first search
  and the Andrews–Curtis conjecture*, IJAC 13(1) 61–68) is rank 2 (length ≤ 12 trivializable;
  at 13, trivializable or AC-equivalent to AK(3)); Miasnikov's genetic algorithms, Lisitsa's
  ATP work, Shehper et al. and the Two-Hump campaign are all rank 2 (plus the 3-generator
  MMS families as *inputs*, not as a searched space). The only rank-4 result found is a
  **lower bound**: Bridson's tower bounds "beginning in rank 4" (arXiv:1504.04187 area) —
  and per the bound-direction lesson, a lower bound on trivialization length says nothing
  about a search having been run. [SECONDARY-ONLY]
* **FRAMING R4's provenance claim, "No computational method has ever searched AC4/AC5 space
  directly (Lisitsa 2025 challenge)".** The *challenge* is real and I have Lisitsa's abstract
  VERBATIM from the RSS mirror (`rss_data/math.GR/2025-02-03_math.GR.xml`), last sentence:
  > "We conclude by proposing a challenge to develop computational methods for searching
  > stable AC-transformations."
  That supports "as of Jan 2025 the author of the leading ATP work considered such methods
  to be wanting". It does **not** support the absolute "no computational method has ever".
  **Downgrade the phrasing wherever it is used.**
* **A conflict inside that same abstract, flagged loudly.** Lisitsa's abstract opens:
  > "Recent work by Shehper et al. (2024) demonstrated that the well-known Akbulut-Kirby
  > AK(3) balanced presentation of the trivial group is stably AC-equivalent to the trivial
  > presentation. This result eliminates AK(3) as a potential counterexample to the stable
  > Andrews-Curtis conjecture."
  **That is wrong for the current version of Shehper et al., and I can prove it from source
  this session.** From `github.com/ammedmar/ac_paper` @ `d86984d`:
  * `app/mms.tex:19` — of the length-25 presentation, "which is AC-equivalent to $\AK(3)$.
    Note, however, that unlike any presentation AC-equivalent to a correct Wirtinger
    presentation, **these presentations are not necessarily stably AC-trivial**."
  * `sec/stable.tex:40` footnote — "$\AK(3)$ — the shortest potential counterexample for the
    standard Andrews–Curtis conjecture **is also a potential counterexample for the stable
    Andrews–Curtis conjecture**."
  * `app/mms.tex:3–10` — the misprint is in the 13th relator of the Wirtinger presentation,
    written as $x_{13}=x_5x_{12}x_5^{-1}$; $W'$ is not a Wirtinger presentation of any knot
    diagram (removing different relators gives different groups — the braid group $B_3$ vs
    $\mathbb Z$), so MMS Theorem 1.4's family is not known to present the trivial group.
  So **FRAMING trap 1 is confirmed from source**, and Lisitsa's framing sentence reflects
  arXiv:2408.15332v1 before the v2 correction. AK(3)'s stable AC-triviality is **open**, and
  the S-line's headline target stands.

---

## Q5. Thickenability of complexes whose 2-cells are all triangles

**Status: SECONDARY-ONLY throughout. No genericity result and no sparsity-based obstruction
found; the complexity landscape, however, is much better than this line has assumed.**

* **Definition drift to watch.** Lackenby (relayed): thickenable = "its associated 2-complex
  K embeds in **some** 3-manifold". The combinatorics literature (Fulek–Tóth, relayed):
  "A 2-dimensional simplicial complex is thickenable if it embeds in some **orientable**
  3-dimensional manifold." Neuwirth's own framing is *closed orientable*. Three inequivalent
  hypotheses. Any solver we build must state which one it decides, and a positive under the
  weaker one does not automatically discharge Lackenby's — **check before citing across**.
* **Complexity — the big correction to this line's working assumptions.**
  **Fulek & Tóth**, *Atomic Embeddability, Clustered Planarity, and Thickenability*
  (arXiv:1907.13086; **JACM 2022**) give a **polynomial-time** algorithm for atomic
  embeddability, prove atomic embeddability and thickenability are polynomially equivalent
  (a poly-time reduction each way), and thereby settle c-planarity in polynomial time; a
  toroidal generalization is NP-complete. Separately, **Carmesin announced that
  thickenability can be tested in polynomial time** (his *Embedding simply connected
  2-complexes in 3-space* series, arXiv:1709.04642 ff.). So the S0 §2 premise — that the
  census cost is the thing that shrinks with triangulation — is *true but not the binding
  constraint*: thickenability is poly-time decidable in general. What triangulation buys is
  a small, easily-implemented instance, not an escape from intractability.
  **Note also that `NEUWIRTH_FEASIBILITY.md:5` on the codex branch attributes this paper to
  "Fulek & Kynčl". The authors are Fulek and Csaba D. Tóth.** [SECONDARY-ONLY, but the
  arXiv/JACM listing is unambiguous across several independent search results.]
* **Neuwirth / Casler / special spines.** Neuwirth 1968 (*An algorithm for the construction
  of 3-manifolds from 2-complexes*, Proc. Camb. Phil. Soc. 64, 603–613) gives "necessary and
  sufficient conditions for the canonical 2-complex which corresponds to a group
  presentation to be a spine … of a connected closed orientable 3-manifold" plus an
  effective algorithm; the criterion runs through the **Whitehead / link graph**, "obtained
  from the intersection of the presentation complex with the boundary of a regular
  neighbourhood of the base point", which "embeds in the 2-sphere and has a planar embedding
  on this sphere". Casler's theorem (every closed 3-manifold has a special spine) is the
  companion existence statement. A geometric re-proof of Neuwirth exists (*Geometric proof of
  Neuwirth's theorem…*, Math. Notes). None of these is a statement about the *frequency* of
  thickenability. [SECONDARY-ONLY]
* **Is thickenability generic for sparse link graphs?** **No result found in either
  direction.** No genericity theorem, no sparsity-based obstruction, no random-model study.
  The nearest empirical literature is the cyclic-presentation spine census (G. Williams,
  *3-manifold spine cyclic presentations with seldom seen Whitehead graphs*,
  arXiv:2408.17125 — abstract VERIFIED-FROM-SOURCE from
  `rss_data/math.GR/2024-09-01_math.GR.xml`), whose whole framing — "the Whitehead graphs
  have not previously been observed in this context" — is evidence that realizable Whitehead
  graphs are *catalogued and rare*, i.e. mildly **against** a genericity heuristic. Treat
  "sparse link ⇒ probably thickenable" as an untested prior, and do not let it justify
  skipping the positive-ladder calibration that
  `experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md` requires.
* **A structural note the S-line should use.** At rank N with all relators of length 3 the
  link graph has 2N vertices (germs) and 3N edges, so it is 3-regular *on average*, but
  Lackenby's Lemma 3.1 output is "at most ℓ generators and ℓ relations", i.e. his triangular
  presentations sit in the same regime. Whatever γ_N behaviour we measure there is being
  measured on the class his proof passes through — a real point of contact and a reason to
  design the ladder around presentations his lemma would produce.

---

## 6. What the S-line may and may not cite

| claim | may cite as | must NOT do |
|---|---|---|
| "thickenable balanced presentations of the trivial group satisfy the unstable ACC" | Lackenby arXiv:2606.06122v1, **abstract** — verbatim, source-verified from the arXiv RSS mirror | attach a theorem number as if read; write "Thm 1.3" without the `[not source-verified]` flag |
| Thm 1.3's exact wording, incl. "without stabilization" | two agreeing secondary restatements (`codex/proofs:experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md:17`, `codex/proofs:literature/proofs/AK3_NEUWIRTH.md:448`) | quote it inside quotation marks as Lackenby's own words |
| **no rank restriction** in Thm 1.3 | as an *absence of evidence* across three channels; the S-line's rank-9 use is licensed **provisionally** | state "Lackenby proves it for all ranks" as fact |
| balancedness is required | yes — abstract, source-verified | drop it anywhere |
| Thm 1.2 bound `2^(2^(cℓ²))`, c = 2·10⁶ | SECONDARY-ONLY (codex advisor) | use the constant in any published-facing arithmetic |
| definition "thickenable = presentation 2-complex embeds in some 3-manifold" | SOURCE-RELAYED + secondary; safe to *use*, flag when *quoting* | silently substitute "orientable" or "closed orientable" |
| move (0) exists and is free insert/delete of `xx⁻¹` inside a relation | SOURCE-RELAYED; supersedes the `LITERATURE_STATUS.md` §1 "no source confirms move (0)" flag | keep calling it "free/**cyclic** reduction" and attribute the cyclic part to Lackenby |
| relators are free-semigroup words in §§1–5 | SOURCE-RELAYED + codex advisor | import §6 statements into the §§1–5 framework (§6 uses free-**group** elements and drops move (0)) |
| move (4⁺), with len(w) ≤ 2, capped only for finiteness | SOURCE-RELAYED + codex advisor, in near-identical words | cost a (4⁺) path in stable AC moves without the `4^(m+3)` / `4^(12Lm+3)` conversion |
| **Lemma 11 = Substitution and Removal** | **arXiv:2408.15332, `sec/stable.tex:28–30` of `github.com/ammedmar/ac_paper`@`d86984d` — VERIFIED, quotable verbatim** | attribute it to Lackenby; call S0's (S-a) new |
| Lemma 11's packaged move count | **unbounded** — the authors' own open problem, `sec/stable.tex:38`, quotable | call it "exponential" (that is (4⁺)→stable-AC, a different fact) |
| triangular normal form / polygon triangulation | **prior art**: Lackenby Lemma 3.1 (SOURCE-RELAYED) and the classical triangular presentation / Delzant T-invariant (SECONDARY) | present A1 as a new lemma; the novelty claim must be narrowed to "without the thickenability hypothesis, inside AC4+AC1–AC3" |
| terminal rank N = n + Σ max(0, len(rᵢ)−3) | our own arithmetic, and it agrees with the k-gon→(k−2)-triangles count | claim the count as a citation |
| AK(3) is a potential counterexample to the **stable** ACC (i.e. still open) | **VERIFIED from source**: `ac_paper` `sec/stable.tex:40` footnote and `app/mms.tex:19` | cite Lisitsa's abstract sentence "eliminates AK(3) as a potential counterexample to the stable AC conjecture" — it reflects 2408.15332**v1** and is contradicted by the current source |
| thickenability is poly-time decidable | Fulek & **Tóth**, arXiv:1907.13086 / JACM 2022 (SECONDARY); Carmesin announcement (SECONDARY) | cite it as "Fulek & Kynčl"; assume decidability is the bottleneck |
| "no computational method has ever searched AC4/AC5 space" | soften to: Lisitsa arXiv:2501.18601 **closes by proposing exactly that as a challenge** (abstract verbatim, source-verified) | keep the absolute form |
| bounded-stabilization hierarchy `~^{(k)}` | **nothing found; treat S0 §4 F1–F3 as unowned open questions** | assume Gilman–Myasnikov's `AC_k` is the same object (it indexes tuple length) |
| sparse link ⇒ thickenability generic | **nothing found either way** | use it as a prior that licenses skipping calibration |

---

## 7. Corrections this pass proposes to existing files (NOT applied — this file edits nothing)

1. `FRAMING.md` trap 6 — "Lemma 11 / Lackenby (4⁺) conversions cost exponentially many
   elementary moves". Lemma 11 is **Shehper et al. arXiv:2408.15332**, not Lackenby, and its
   cost is **unbounded**, not exponential. Same conflation in `S0_HIGH_RANK_PLAN.md` T-S5.
2. `FRAMING.md` trap 7 — "Lackenby §6 switches frameworks (free semigroup, no move (0))"
   reads as if §6 *adopts* the free semigroup. Per the codex advisor and the relayed text it
   is the reverse: §§1–5 use free-semigroup **words** *with* move (0); **§6** switches to
   free-**group** elements and drops move (0), where thickenability is not even well defined.
3. `LITERATURE_STATUS.md` §1 — the row "no source anywhere confirms the paper contains a move
   labelled (0) at all" can be retired to "move (0) confirmed via a second channel; it is
   free insertion/deletion of `xx⁻¹`, **not** cyclic reduction".
4. `LITERATURE_STATUS.md` §4 Joint A — leans favourable (free-semigroup relators + move (0)),
   still not source-verified.
5. `S0_HIGH_RANK_PLAN.md` §1 (S-a) — should cite Lemma 11 of arXiv:2408.15332; §1 (S-b) and
   task A1 — should cite Lackenby Lemma 3.1 and the classical triangular presentation, and
   restate the novelty as the *removal of the thickenability hypothesis* plus the γ_N
   programme.
6. `codex/proofs:experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md:5` —
   "Fulek & Kynčl" should be **Fulek & Tóth**. (Codex branch; for the user to relay.)

## 8. Lesson candidate for `experiments/lessons/`

**`WebSearch` can read a PDF that every fetch transport 403s — if you load the query with
in-document jargon.** `WebFetch` and `curl` returned 403 for arxiv.org, ar5iv, alphaxiv,
huggingface, and semanticscholar, exactly as
`cloud-session-network-and-push-constraints.md` records. But `WebSearch`'s answer synthesiser
fetched `arxiv.org/pdf/2606.06122` and returned **body text** — the definition of
thickenable, the (0)–(4)/(4⁺) move list with its rationale, Lemma 3.1's statement with its
constant, the Mijatović/King citation, the Euler-characteristic obstruction, and the
free-semigroup convention. The trigger is query composition: *generic* queries
("2606.06122 Theorem 1.1 statement") returned only the abstract, four times running;
*jargon-dense* queries ("regular neighbourhood handle structure Perelman Pachner Mijatovic
(4+) triangular") returned body text. Corroborate every relayed passage against a second
independent channel before it becomes load-bearing — here the codex branch's notes, written
from a real read, agreed on every overlapping point, which is what makes the relay usable at
all. And the earlier lesson's line "Only WebSearch (indexed snippets) … work" understates the
channel: it is not snippets, it is a reader.

Secondary lesson: **the arXiv RSS GitHub mirror is a version oracle, not just an abstract
oracle.** `ehijano/rss_fetch` is current to within a day; grepping every math.GR/math.GT feed
for an arXiv id enumerates v1/v2/… announcements, so "is there a newer version I have never
seen?" is answerable offline. Sparse-clone it (`--filter=blob:none --sparse` +
`sparse-checkout set rss_data/math.GR rss_data/math.GT`) rather than fetching single files:
`raw.githubusercontent.com` 404s on paths you have not enumerated and the GitHub API
`get_file_contents` is allow-listed to this repo only.
