# TRAP — `literature/` is gitignored, so cloud clones have NO papers at all

## What happened

Route R7's entire positive direction was built on "Lackenby arXiv:2606.06122 Thm 1.3:
thickenable balanced presentations of the trivial group satisfy the unstable ACC". Every
theory file in the fable line cites it; several cite section numbers, a "move (0)", and
neighbouring results (Thm 1.2's tower bound, Thm 2.6, Prop 2.5, Lemma 2.4, Thm 6.4) as
if from the text.

An independent verification pass found that **`/home/user/ACSolverX/literature/` does not
exist on disk**. It is gitignored (`.gitignore:16`) and was never tracked, so a cloud
clone starts without it. Nothing in this line had been read from the paper this session;
the citations were carried in from an earlier session's context and had acquired the
appearance of being sourced.

Worse, the paper is unreachable here: arxiv.org, export.arxiv.org, ar5iv, alphaxiv, the
author's own Oxford page, semanticscholar.org and openreview.net are all proxy-blocked
(403 / "Host not in allowlist"), and a GitHub code search found **no LaTeX source mirror**
(`"thickenable" "Andrews-Curtis" language:tex` → 0 hits). The abstract WAS recoverable,
verbatim, from arXiv's own RSS feed mirrored on GitHub (`github.com/ehijano/rss_fetch`,
`rss_data/math.GR/2026-06-04_math.GR.xml`), corroborated by a second mirror — so the
GitHub-mirror trick works for abstracts and metadata, just not for bodies.

## Why it is dangerous

A citation that is *carried* rather than *read* looks identical to a real one in the
prose, and gets more confident each time it is copied into a new file. Here it reached
the point where the number of a theorem ("Thm 1.3"), the existence of a move ("move (0)")
and the paper's convention on reduced words were all being used as load-bearing facts,
while none of the three had a source. The R7 route's key inference — that a thickenable
UNREDUCED spelling implies AC-trivializability — turns entirely on the paper's convention
about whether relators are free-group elements or words, which is precisely the kind of
detail an abstract cannot settle.

## The rules that follow

1. **A gitignored directory is not a shared artifact.** If a session's conclusions depend
   on a file under `literature/`, either commit the extract with `git add -f` or treat the
   dependency as unsourced in every later session. Do not assume the next clone has it.
2. **Re-verify a citation in the session that uses it, not in the session that found it.**
   Cheap test: `ls` the file you think you are citing before writing the sentence.
3. **When a body is unreachable, mirror-hunt the ABSTRACT anyway** — arXiv RSS feeds are
   mirrored on GitHub and give title, abstract, version history and announce dates
   verbatim. That is often enough to confirm the SHAPE of a dependency (here: that an
   unstable AC conclusion really is claimed for thickenable balanced trivial-group
   presentations) even when every hypothesis stays unverified.
4. **Separate the experiment from the transfer.** R7's existence question (is there a
   thickenable spelling?) is decided by machine-checked certificates and owes the
   literature nothing. Only the final step (therefore AC-trivial) is gated. Structuring
   the write-up that way means an unsourceable theorem costs you one inference, not the
   whole route.
5. **Check the data behind a cited theorem, not just the theorem.** The same pass found
   that Fagan–Qiu–Wang's census is explicitly **cellular** and **partial at complexity 5**
   ("surfaces without small disks", the authors' own README), while the abstract's theorem
   is unqualified — a discrepancy that 514 of this line's 5,389 certified targets inherit.

Ledger with the full sourcing record:
`results/stable_ac/theory/fable/LITERATURE_STATUS.md`.
