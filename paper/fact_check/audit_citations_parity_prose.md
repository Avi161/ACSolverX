# Citation / Parity / Prose Audit — "The Hump, Not the Cap"

Scope: `paper/` — `paper.tex`, `paper.md`, `sections/*.tex`, `sections/*.md`, `refs.bib`,
`paper.log`/`paper.blg`, `paper.pdf`. Read-only audit; no paper content, figures, or tables
were modified. `build/build_paper.py` was **not** re-run — `paper.log`/`paper.blg` were
already present from the last build (mtimes match `paper.pdf`, both `2026-07-06 20:44`), so
those were read directly per the task's "read paper.log if present" instruction.

## Verdicts

| Gate | Verdict |
|---|---|
| Gate 1 — Citations | **PASS** (one non-blocking hygiene flag, see below) |
| Gate 2 — MD/TeX parity | **PASS** |
| Gate 3 — Prose wording law + anonymization | **PASS** |

**No true violations requiring a fix were found.** One repository-hygiene issue in
`refs.bib` is flagged (harmless today, fragile going forward) — see Gate 1 §"Flag".

---

## Gate 1 — Citations

### Key existence (cite ↔ bib)

Extracted every `\cite{...}` key from `paper.tex` + `sections/*.tex` (18 distinct keys) and
every `@type{key,...}` from `refs.bib` (18 entries). `diff` of the two sorted key lists is
empty — **exact 1:1 match, zero orphans, zero missing keys**:

```
akbulut1985ac, andrews1965ac, bowman2006fast, bridson2015complexity, fagan2026twohump,
freedman2010poincare, gompf2010fibered, gukov2021unknot, havas2003bfs, lishak2017balanced,
lisitsa2024newtrivializations, lisitsa2025ak3, lisitsa_zenodo, miasnikov1999genetic,
miller1999ms, myasnikov2002ac, shehper2024hard, zhang2025aidriven
```

### Required fields per type

Checked all 18 entries against required fields (article: author/title/journal-or-eprint/
year; inproceedings: author/title/booktitle/year; incollection: same as inproceedings;
misc: author/title/year/howpublished-or-note). All 18 have their required fields present in
`refs.bib`, and — more importantly — the **compiled PDF's rendered References section**
(extracted via `pdftotext -layout paper.pdf`) shows all 18 entries fully and correctly
formatted (author lists, titles, venues, volumes/pages or arXiv IDs, years), confirming the
fields actually reach the typeset output.

### `shehper2024hard` v2 explicit

Satisfied redundantly:
- `refs.bib:31` — `note = {v2}` (renders as "... arXiv:2408.15332, 2025. v2." in the PDF).
- `sections/E_misprint.tex:26-27` — "This gap was first reported by \cite{shehper2024hard}
  (v2, Appendix F), which rescinded the stable-triviality claim its own v1 had made."
- `sections/E_misprint.tex:58` — "written between the v1 and v2 revisions of
  \cite{shehper2024hard}".

### `lisitsa2025ak3` first substantive mention carries the inherited-premise caveat

The paper's very first citation of this key, `sections/01_intro.tex:28`, already carries it
verbatim: "A parallel automated-deduction paper \cite{lisitsa2025ak3}, written between those
two versions, builds its stable-triviality conclusion on the same, now-rescinded premise and
has not been revised."

Within the three files the task named specifically:
- `sections/02_background.tex:68` — narrowly scoped ("an independent Prover9 derivation of
  the same equivalence is archived in \cite{lisitsa2025ak3,lisitsa_zenodo}"), no
  triviality claim asserted here, so no caveat is needed at this specific sentence.
- `sections/04_results.tex:31` — likewise narrowly scoped (cites the independently published
  *plain-AC* trivialization, not a stable-triviality claim).
- `sections/E_misprint.tex:51,57-59` — gives the fullest restatement: "Its authoring paper
  \cite{lisitsa2025ak3}, however, was written between the v1 and v2 revisions of
  \cite{shehper2024hard} and justifies P25's stable triviality by citing the same,
  now-rescinded Theorem 1.4; it has not since been revised or corrected."

No citation of `lisitsa2025ak3` anywhere asserts or leans on its stable-triviality
conclusion without the caveat attached somewhere in context. **Verdict: satisfied.**

### Compiled-PDF undefined-citation check

`paper.log` contains zero hits for `undefined`, `Citation .* undefined`, or
`Reference .* undefined`. Independently, `pdftotext -layout paper.pdf` was diffed for stray
`??` or "undefined" markers in the rendered text — none found; every in-text citation
resolves to an author-year form (e.g. "Shehper et al. [2025]") and the References section
lists all 18 works completely. **No undefined citations in the compiled PDF.**

### Flag (non-blocking): invalid in-entry BibTeX comments in `refs.bib`

`paper.blg` (a real bibtex run, not stale — same mtime as `paper.pdf`) logs **8 parser
errors**, one each for `fagan2026twohump`, `shehper2024hard`, `andrews1965ac`,
`akbulut1985ac`, `miller1999ms`, `lisitsa2025ak3`, `lisitsa_zenodo`, `zhang2025aidriven`:

```
You're missing a field name---line 20 of file refs.bib
 :   % Verified 2026-07-06: arXiv:2606.21611 (v1, submitted 19 Jun 2026) is a standalone
(Error may have been on previous line)
I'm skipping whatever remains of this entry
```

Cause: each of these 8 entries has a trailing `% Verified ...` provenance comment placed
*inside* the entry's brace-delimited field list (after the last field's comma, before the
closing `}`). BibTeX does not recognize `%` as a comment character inside an entry (only
between entries), so it errors on it.

**Impact today: none.** In every one of the 8 cases the comment sits strictly after all
real fields and before the closing brace (verified by inspecting each entry directly), so
"skipping whatever remains of this entry" discards nothing — confirmed empirically by the
fully-correct, complete rendering of all 18 references in the compiled PDF.

**Why it's still worth fixing:** it is fragile. Any future edit that adds a field *after*
one of these comment blocks, or moves the comment earlier in the entry, would cause bibtex
to silently truncate that entry (drop the trailing fields) with only a `.blg` warning that
is easy to miss (`build_paper.py`'s own problem-detection regexes check tectonic's stdout/
stderr for `undefined`/`^!`/"Citation... undefined", not the separate `.blg` bibtex log, so
this class of error would not fail the build script even if it started actually dropping
fields).

**Recommended fix (not applied — read-only per scope):** move the 8 `% Verified ...`
provenance notes out of the field list, either to a comment line *between* entries (outside
the closing `}`) or into a `note=`/`annote=` field value.

---

## Gate 2 — MD/TeX parity

### (a) Section + appendix heading sequence

Extracted every `\section`/`\subsection` from `sections/*.tex` in `\input` order (per
`paper.tex`) and every `#`/`##`/`###` heading from `paper.md`. Sequence and titles match
exactly: Introduction → Background {2.1–2.4} → Methods {3.1–3.7} → Results {4.1–4.8} →
Limitations → Conclusion → Appendix A {7 subsecs} → B {6} → C {6} → D {4} → E {3} → F → G.
The only difference is numbering *style* (md hardcodes "4.8" in the heading text; LaTeX
auto-numbers `\subsection{...}` with no literal digit in source) — expected/structural, not
a mismatch. `paper.md`'s trailing `## References` heading matches the auto-generated
"References" heading LaTeX's `plainnat` style produces in the compiled PDF (confirmed via
`pdftotext`). **Match.**

### (b) Figure count (8 raster in md vs 9 floats in tex)

`grep -c '\begin{figure}'` over `sections/*.tex` gives 8 outer float environments, but one of
them (`sections/04_results.tex:67`, the arms figure) wraps **two** `\begin{subfigure}` blocks
(`arms_bar`, `arms_subset`), each independently labeled (`fig:arms-a`, `fig:arms-b`) and
captioned in the compiled PDF as "Figure 2(a)"/"Figure 2(b)". Counting each subfigure as its
own float unit alongside the standalone figures gives **9**: tikz-overview, arms-a, arms-b,
campaign_floor, cap_hump, two_floors, ak3_plateau, hard_ties, rl_gap.

`grep -c '!\[Figure'` over `paper.md` gives exactly **8** embedded raster PNGs: `arms_bar`,
`arms_subset`, `campaign_floor`, `cap_hump`, `two_floors`, `ak3_plateau`, `hard_ties`,
`rl_gap` — the same 8 that carry `\includegraphics` in the tex source.

The 9th tex float (the TikZ pipeline-overview diagram, `sections/01_intro.tex:55-99`,
`\label{fig:overview}`) has no raster counterpart in `paper.md`. Confirmed: `paper.md:19`
carries a text note instead — `_(Schematic — see Figure 1 in the compiled PDF.)_` — followed
by a full caption paragraph (`paper.md:21`) describing it in prose. **Confirmed as
specified.**

### (c) Table count

6 `\begin{table}` environments in `sections/*.tex` (`tab:wordbank`, `tab:litchecks`,
`tab:arms`, `tab:lanes`, `tab:certs`, `tab:floorcensus`) match Tables 1–6 in `paper.md`
exactly, same order, same captions. **Match.**

### (d) Number-diff between `paper.md` body and concatenated tex body

**Methodology.** Extracted all `[0-9][0-9,\.]*` tokens from `paper.md`'s body (excluding the
`## References` section, which mirrors `refs.bib` bibliographic metadata with no counterpart
in `sections/*.tex`'s literal source — LaTeX generates it from `\bibliography{refs}` at
compile time) and from `sections/*.tex` concatenated. As instructed, filtered LaTeX-only
layout numbers from the tex side: content inside `\begin{tikzpicture}...\end{tikzpicture}`,
`p{...}` column specs, `\resizebox{...}{...}`, `\setlength{...}{...}`, `\hspace{...}`,
`\vspace{...}`, `\includegraphics[...]` options, and (same category, not explicitly listed
but clearly the same kind of artifact) `\begin{subfigure}{0.48\textwidth}` width fractions.
Un-braced the `{,}` thousands-grouping idiom (`16{,}870` → `16,870`) identically on both
sides before extraction, since both masters use it interchangeably with plain commas.
Normalized by stripping commas/trailing periods. Diffed the two token sets (both exact
multiset and, since the task's own closing sentence frames the target as "a number in one
master but not the other," a distinct-value set difference).

A first pass restricted to literally `sections/*.tex` (per the task's literal wording)
produced 26 md-only and 21 tex-only distinct values. Inspecting them showed nearly all of
this to be a scope artifact: **Tables 1–6's actual cell content lives in `tables/out/*.tex`**
(`\input`-ed from `sections/*.tex`, e.g. `sections/03_methods.tex:92`
`\input{tables/out/table3_wordbank}`), not literally inside the 14 `sections/*.tex` files —
so numbers that live only in a table cell (e.g. `25,000`-node budget note, `300k`/`800k`
shorthand, the Zenodo ID `14567743`, `arXiv:2408.15332`) appeared "md-only" purely because
`paper.md` inlines the table text directly while the tex source only inlines a file
reference. Re-running with `tables/out/*.tex` included in the tex-side extraction (the fair,
apples-to-apples comparison, since that content **is** part of the compiled document) cut
this down to **16 md-only and 14 tex-only distinct values**, every one of which is a
well-understood structural or methodological artifact rather than a real content
difference:

**MD-only (16), all expected:**
- 15 are heading-number literals: `2.1, 2.2, 2.3, 3.1–3.6, 4.1–4.5, 4.7` — `paper.md`
  hardcodes subsection numbers in its `###` heading text; LaTeX auto-numbers
  `\subsection{...}` from no literal digit in source. (`2.4`, `3.7`, `4.6`, `4.8` do *not*
  appear in this list because those four are, separately, hardcoded as literal `\S4.6`/
  `\S4.8`-style backreferences inside the tex prose itself, e.g.
  `sections/04_results.tex:143` "Lane E is \S4.6.")
- 1 is `18` — from `paper.md`'s numeric-citation-bracket style (`[18]` for Zhang et al. in
  `paper.md:51`); tex cites by named key (`\cite{zhang2025aidriven}`), never by bracket
  number, so `18` as a literal digit-string exists only on the md side.

**TEX-only (14), all expected:**
- 11 are years embedded in `\cite{...}` bib-key names themselves (e.g. `\cite{fagan2026twohump}`
  contains the literal substring `2026`; `\cite{myasnikov2002ac}` contains `2002`): `1965,
  1999, 2002, 2003, 2006, 2010, 2015, 2017, 2021, 2025, 2026`. These are a byproduct of the
  repo's `author+year+topic` bib-key naming convention, not paper content — `paper.md` never
  writes a bare year next to these citations (it uses `[N]` brackets), so they have no md
  counterpart by construction of the citation styles, not by omission.
- `215`, `8614`, `8814` are regex tokenization artifacts, not real numbers: they come from
  the histogram set-notation `$\{13\!:\!88,14\!:\!2,15\!:\!7\}$` etc. in the **figure caption**
  `sections/C_tables.tex:126-127`, which (unlike its restatement in prose,
  `sections/04_results.tex:105-106`, and unlike `paper.md`'s equivalent caption text at
  `paper.md:463`, both of which insert a space/`\ ` after each comma) has no separator between
  a pair's value and the next pair's key, so the naive comma-stripping regex spuriously
  merges e.g. `88,14` → `8814` and `2,15` → `215`. This is an artifact of my own extraction
  regex's inability to distinguish a thousands-separator comma from a set/list-separator
  comma, confirmed by manual inspection of the exact source spans — it does not reflect an
  actual number in the paper, and the real underlying digits (`13,14,15,86,87,88,2,7,9`) are
  all already present and shared on both sides regardless.

**Verdict: zero real content-number differences.** Every one of the 30 apparent
discrepancies resolves to a named, benign structural/methodological cause (`tables/out/`
`\input` scope, heading auto-numbering, citation style, bib-key naming, or a regex
false-merge) — none is a number that actually appears as content in one master and is
genuinely missing from the other.

### CAPTIONS fenced block leak check

`sections/04_results.md:37-53` contains a ` ```CAPTIONS ... ``` ` fenced block holding raw
`\caption{...}` text for all 9 figures — evidently a source-authoring artifact used by
whatever assembles `paper.md` from the section `.md` files (e.g. to extract captions
programmatically). Grepped `paper.md` for both the literal string `CAPTIONS` and for
fragments of the raw caption text (`\caption{\textbf{fig:`) — **zero hits in either case**.
This fenced block is unique to `sections/04_results.md` (no other `sections/*.md` file has
one) and is correctly excluded from the assembled `paper.md`. **Confirmed: no leak.**

---

## Gate 3 — Prose wording law + anonymization

All greps run over `paper.md` + `sections/*.tex` + `sections/*.md` + `refs.bib`.

### Banned (all zero true hits)

| Pattern | Hits | Verdict |
|---|---|---|
| `two classes` / `two floor classes` | 0 | Clean. Paper consistently uses "two canonical (signed-relabel) representatives" (e.g. `paper.md:28`, `sections/01_intro.tex:118`, `sections/04_results.tex:213`). Conclusion's "two-floor result" (`paper.md:256`) is a different phrase describing the same finding correctly (one floor length, two representatives) — not a match for the banned pattern and not a mischaracterization. |
| `presentation of AK(3)` (F context) | 0 | Clean. `F` is described identically everywhere as "a 2-generator presentation AC-equivalent to AK(3)" (`sections/04_results.tex:221`, `sections/B_certificates.tex:70`, `sections/C_tables.tex:78`, `sections/D_reproducibility.tex` note, `paper.md:219,363,431`). No instance of "presentation(s) of AK(3)" found anywhere (checked case-insensitively, singular and plural); "presentations of the trivial group" (the allowed phrase) is used throughout instead. |
| `/[0-9,]+ solves/` | 0 | Clean. Every "N solve(s)" construction is phrased "N solve attempts" or "N of M attempts/words/probes solve" throughout (Tables 3/4, §4.2–4.5, Appendix C/F). Manually reviewed every remaining bare occurrence of "solves" (`grep -n solves`): all have a genuine subject that solves something with a **nonzero** count or a real system as subject — "the same system solves 155/155," "it solves all 155 of 155," "solves the resulting fresh candidates" (subject = the harvest pipeline), "solves none" (Lane B, a legitimate zero-subject phrasing that is not of the banned "N solves" numeral-prefixed form) — none is a bare 0-count number directly followed by "solves." |
| `falsified` (applied to the cap) | 0 | Clean. Every mention of the cap correctly uses "not the binding constraint in the tested range" (`paper.md:31,209,211`; `sections/04_results.tex:187,196`; `sections/F_cap.tex:36`). |
| `our prior work` / `we previously` / `our earlier` / `our system` | 0 | Clean. `fagan2026twohump`/`shehper2024hard` are always referred to in third person ("prior work~\cite{fagan2026twohump}", "Fagan et al.", "Shehper et al."). The only first-person "our ..." possessives found (`sections/02_background.tex:25` "our audit probes"; `sections/03_methods.tex:35` "our reproduction") refer to *this* paper's own methods, not to the cited prior works — correct usage, not a violation. |
| Identity leaks (ACSolverX, github.com, MyDrive, /content/drive, week_, SURF, 610model, Obsidian, Caltech, Zurich, Temple, Zero Latency) | 0 | Clean across all of `paper.md`, `sections/*.tex`, `sections/*.md`, `refs.bib`. |
| `Anonymous Author(s)` present, no real names | — | Confirmed. `paper.tex:37-39`: `\author{Anonymous Author(s)\\ Affiliation\\ \texttt{email}\\}`, under the default (non-`preprint`) `neurips_2025` style — review mode intact, no real author names or institutions anywhere in the author block. |

### Required (all present)

| Requirement | Location(s) |
|---|---|
| "within the searched budgets" (or equivalent) in abstract AND §1 or §4 | `sections/00_abstract.tex` (line-wrapped as "...succeeding, within the\nsearched budgets..."; confirmed present after whitespace-normalizing) and `paper.md:7`; also §1 `sections/01_intro.tex:48` "all of which fail within the searched budgets"; repeated in §4 (`sections/04_results.tex:60,110`) and §5. |
| 634/640 cap-semantics sentence | `sections/03_methods.tex:38-40` / `paper.md:63`: "Under the per-relator cap, 634 of the 640 known-solvable MS(1190) presentations solve at 10^6 nodes; the remaining 6 (indices 634–639) solve only under the original sum cap." Exact semantics required (634 under per-relator L=24; 6 only under sum cap) present verbatim, repeated in `sections/04_results.tex:51-52`. |
| "by construction of the harvest pipeline" | `sections/03_methods.tex:129-130`, `sections/05_limitations.tex:39`, `paper.md:107,183,248` (4 occurrences). |
| "zero-shot" framing for RL lane | `sections/03_methods.tex:139-140`, `sections/04_results.tex:177`, `sections/05_limitations.tex:19,24`, `sections/06_conclusion.tex:38`, `sections/01_intro.tex:95`(fig caption), `sections/C_tables.tex:181` — consistently framed as "explicitly an out-of-distribution probe of a fixed policy, not an in-principle negative result about reinforcement learning." |
| Anonymized code-release statement | `sections/01_intro.tex:129` / `paper.md:31`: "Code, data, and all certificates will be released on acceptance." Repeated in `sections/06_conclusion.tex:55`, `sections/D_reproducibility.tex:15`, `sections/G_checklist.tex:34,83` (the checklist item explicitly notes "withheld only during anonymized review"). |
| Broader impacts sentence | `sections/G_checklist.tex:57-63` (checklist item 10): "This is a pure-mathematics search on the Andrews–Curtis conjecture, with no foreseeable negative societal impact identified. The practical benefit is methodological: ..." |

**Verdict: Gate 3 PASS, zero true violations.**

---

## Summary

| Gate | Verdict | True violations (file:line) |
|---|---|---|
| 1 — Citations | **PASS** | None. (Non-blocking flag: `refs.bib` lines 20,34,52,64,79,194,209,225 — trailing `%`-comments sit inside 8 entries' field lists, causing 8 harmless-today-but-fragile BibTeX parser errors logged in `paper.blg`; recommend relocating those comments outside the entry braces or into a `note=` field.) |
| 2 — MD/TeX parity | **PASS** | None. |
| 3 — Prose wording law + anonymization | **PASS** | None. |

No fixes are required before this preprint's citation, parity, or prose/anonymization
checks would block submission. The one item worth a follow-up commit is the `refs.bib`
in-entry-comment hygiene fix noted above (cosmetic/robustness only, not a content defect).
