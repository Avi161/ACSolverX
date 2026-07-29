# LITERATURE STATUS — what this line's results actually rest on

STATUS: PROVENANCE LEDGER. Read this before citing any external theorem anywhere in
`results/stable_ac/theory/fable/`. It records, per external dependency, exactly what was
sourced verbatim, what was derived and checked against primary data, and what is
asserted on nobody's authority. Independent verification pass, 2026-07-29.

**Headline: `literature/` does not exist on disk in this session's clone.** It is
gitignored (`.gitignore:16`) and was never tracked, so a cloud clone starts without it.
Every citation in this line's documents that reads as if it came from
`literature/txt/lackenby_stable_ac_thickenable.txt` was in fact carried in from a
previous session's context, not read this session. That is exactly the failure mode the
project rule against "misremembered background facts" exists to prevent, so the ledger
below is the corrective.

## 1. Lackenby, arXiv:2606.06122 — UNSOURCED except for the abstract

Sourcing attempts, all recorded: arxiv.org, export.arxiv.org, ar5iv, alphaxiv,
www.arxiv.org, the author's Oxford page, semanticscholar.org, openreview.net — every one
proxy-blocked (`CONNECT tunnel failed, response 403`, or `Host not in allowlist`).
GitHub code search for the paper's LaTeX source: **no source mirror exists**
(`"thickenable" "Andrews-Curtis" language:tex` → 0 hits).

**SOURCED VERBATIM** — title and full abstract, from arXiv's own RSS feed mirrored at
`github.com/ehijano/rss_fetch` (`rss_data/math.GR/2026-06-04_math.GR.xml` and three
sibling files), corroborated by an independent mirror
(`github.com/Replikanti/agentis-colonies`), GUID `oai:arXiv.org:2606.06122v1`:

> **The stable Andrews-Curtis conjecture and thickenable presentations of the trivial
> group**
>
> "We establish an explicit upper bound on the number of stable Andrews-Curtis moves
> that convert thickenable balanced presentations of the trivial group to the standard
> one-generator presentation. We also present a proof that thickenable balanced
> presentations of the trivial group satisfy the (unstable) Andrews-Curtis conjecture."

**[UNVERIFIED] — every one of the following, without exception:**

| item | status |
|---|---|
| the statement of "Theorem 1.3" | not read; even the NUMBER is unconfirmed — the abstract carries no theorem numbering, so we cannot confirm the unstable result is Thm 1.3 rather than 1.2 or another |
| the definition of "thickenable" used for presentations | not read |
| whether relators are free-group elements or free-semigroup WORDS | not read — and this is the load-bearing distinction (see §3) |
| the existence, number, and scope of "move (0)" | **no source anywhere confirms the paper contains a move labelled (0) at all** |
| whether attaching words must be reduced / cyclically reduced | not read |
| Thm 1.2's bound `2^(2^(c ℓ²))`, Thm 2.6, Prop 2.5, Lemma 2.4, Thm 6.4 | not read this session |
| anything about AK(n) or Miller–Schupp being thickenable | not read; the abstract mentions neither |

**What the abstract DOES settle**, and it is not nothing: an **unstable** AC conclusion
is claimed, with hypothesis exactly "thickenable balanced presentations of the trivial
group". So the SHAPE of this line's transfer argument is real. Note the abstract's own
hedge — "we also *present a proof* that", not "we prove" — whose significance cannot be
assessed without the text.

**Vocabulary warning.** Several files in this line write "Lackenby's move (0)" as
established terminology (`spike_monotonicity.py`, `gateway_neighborhood.py`,
`R1E_DISCONNECTED_LINK.md`, `R1F_REDUCTION_AND_SPIKES.md`). The OPERATION those files
mean — free/cyclic reduction of a relator — is perfectly well defined and everything
measured about it stands. Only the ATTRIBUTION is unverified. Read "move (0)" throughout
this line as "free/cyclic reduction", and do not rely on the numbering.

## 2. Fagan–Qiu–Wang, arXiv:2412.12293 — abstract sourced; a live cellularity discrepancy

**SOURCED VERBATIM** — title, authors, abstract and version history, from
`github.com/MystenLabs/snowreads` (`data/abs/2412.12293.json`):

> **Stable Andrews-Curtis Conjecture via Fake Surfaces and Zeeman Conjecture** —
> Lucas Fagan, Yang Qiu, Zhenghan Wang
>
> "We propose an induction scheme that aims at establishing the stable Andrews-Curtis
> conjecture in the affirmative. The stable Andrews-Curtis conjecture is equivalent to
> the conjecture that every contractible fake surface is 3-deformable to a point. We
> prove that every contractible fake surface of complexity less than 6 is 3-deformable
> to a point by induction."

**There is a v2** (announced 2026-01-09, `oai:arXiv.org:2412.12293v2`) whose abstract is
character-identical to v1; the body may differ and neither was readable.

**THE DISCREPANCY, which every R6 result inherits.** The abstract's theorem is
*unqualified* — "every contractible fake surface of complexity less than 6". The census
it is built on is not. The authors' own repository README states, verbatim
(`github.com/lucasfagan/Fake-Surfaces` @ 7bcff60):

> "This repository contains the data for the classification of acyclic **cellular** fake
> surfaces of complexity 1-4 and a **partial** classification of complexity 5: surfaces
> without small disks."

(emphasis added), and the companion paper is titled *Classification of Cellular Fake
Surfaces* (arXiv:2406.09439 — a DIFFERENT paper from 2412.12293). So the visible data is
(a) cellular and (b) incomplete at complexity 5. Whether the theorem in the body carries
a cellularity hypothesis, and how the complexity-5 "no small disks" gap is closed, are
**[UNVERIFIED]**. Concretely: of this line's 5,389 targets, the 514 complexity-5 rows
come from a partial classification. **Do not propagate the unqualified form of the
theorem.**

Also corrected: despite its filename, the repository's
`Surface_presentation_convention.pdf` is about the CSV vertex/edge labelling convention
for 4-regular multigraphs, **not** about group presentations. It contains no
surface→presentation dictionary.

## 3. The dictionary — DERIVED AND DATA-CHECKED, not quoted

The (V+1 generators, V+1 relators, total length 3V+3) profile this line uses is **not** a
quotation from 2412.12293; it was derived here and checked against the authors'
published data. That check was re-run independently this session against
`fakesurfaces.csv` @ 7bcff60, all 5,389 rows, **zero failures**:

* number of disks D = V + 1 — 5,389/5,389
* total attaching-map length = 6V — 5,389/5,389
* every edge label 1..2V occurs exactly 3 times across the disk attaching maps (the
  triple-line condition) — 5,389/5,389
* row counts by complexity: 2, 17, 238, 4,618, 514

Collapsing a spanning tree of the 1-skeleton (V−1 edges of the 2V) then gives, as
arithmetic: generators = 2V − (V−1) = V+1; relators = D = V+1 (balanced); total relator
length = 6V − 3(V−1) = 3V+3. This is a DERIVATION plus a data check, and it is solid on
its own terms. What remains **[UNVERIFIED]** is whether the paper states this dictionary
in this form, whether it collapses a spanning tree rather than normalising some other
way, and whether the resulting relators are reduced or raw length-3V+3 spellings — that
last being the same reduced/unreduced question as §3 below.

## 4. The load-bearing gap, stated precisely

Route R7 hunts for a thickenable **unreduced spelling** in AK(3)'s class. Suppose one is
found. The inference "therefore AK(3) is AC-trivializable" has two joints:

* **Joint A — the hypothesis side. THIS IS THE RISK.** Does an unreduced spelling P′ of P
  discharge the theorem's "thickenable" hypothesis? If the paper's relators are
  free-group elements, then P′ and P are literally the same presentation and
  thickenability must be defined either as a property of the presentation (in which case
  a spelling-dependent 2-complex cannot establish it) or as "some spelling is
  thickenable" (in which case a hit does discharge it). **These readings have opposite
  consequences and the abstract cannot distinguish them.** If instead the framework
  requires (cyclically) reduced attaching words — a common convention, since a backtrack
  changes the 2-complex and its regular-neighbourhood analysis — a thickenable unreduced
  spelling never enters the theorem at all and R7's transfer step is void.
* **Joint B — the conclusion side. Probably safe.** If the move set is the standard one
  plus free reduction, a trivializing sequence for P′ projects to F_n: reduction becomes
  the identity there and AC1–AC3 project to AC1–AC3. Since P′ and P have the same image
  in F_n, P is AC-trivializable. The "unreduced ⇒ reduced" transfer is the benign
  direction — conditional only on the move set being standard.

So R7's experimental content (does a thickenable spelling EXIST?) is worth pursuing on
its own: the existence question is decided by machine-checked certificates that owe
nothing to the literature. It is only the final transfer to an AC-triviality claim that
is gated on Joint A. **A hit must be reported as "a thickenable spelling exists in
AK(3)'s class", never as "AK(3) is AC-trivial", until Joint A is resolved against the
source.**

## 5. Standing instruction for the next session

The first network-capable action of any future session should be to fetch and store,
under `literature/txt/` (which must then be committed with `git add -f`):

1. `arxiv.org/abs/2606.06122` — PDF only; no HTML version was indexed.
2. `arxiv.org/html/2412.12293v2` — the version whose body we have never seen.
3. `arxiv.org/html/2406.09439v3` — the companion classification paper, the cheapest way
   to pin the fake-surface→presentation dictionary as a quotation rather than a
   derivation.

Until then, every claim routed through §1 stays flagged, and the flags in the individual
theory files must not be quietly dropped.
