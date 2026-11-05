# Conference paper draft

`main.tex` is the paper as Truett had it on 5 Nov 2026 (pasted into the project thread, saved verbatim). Figures go
in `figures/`. This branch (`paper`) was cut from `ryan-replication`, so it also carries the Elliot Steffen and Ryan
Zang replications and their results (`docs/ELLIOT_REPLICATION.md`, `docs/RYAN_REPLICATION.md`).

No pull request for this branch. Never add solutions to the 10,115 SAIR ACC challenges here.

## Layout

Compile `main.tex`. It only holds the title and the order of the parts; the text lives in one file per part, pulled
in with `\input`, so editing any of these files changes the paper:

| file | holds |
|---|---|
| `preamble.tex` | packages, theorem styles, macros |
| `sections/01_ac_benchmarks.tex` | Section 1 start: benchmarks (MS640, bench60 short form, AC19_autmin, ladder100) |
| `sections/02_ac_methods.tex` | units, time per unit, AC search methods, scores |
| `sections/03_ac_hybrid_checks.tex` | pinch replacements, filters, finishing checks |
| `sections/04_stable.tex` | Section 2: stable AC moves, rank 3 / 4 / 5 |
| `sections/05_cov.tex` | one-shot change of variables, every image |
| `appendix/A_bench60.tex` | bench60 in full: the selection rule, the bin table, the figure |
| `references.tex` | bibliography |

To move more detail out of the main text: cut it from its section file, paste it into a new `appendix/B_<name>.tex`
that starts with `\section{...}\label{app:<name>}`, add `\input{appendix/B_<name>}` after the other appendix
lines in `main.tex`, and leave a one-line pointer (`Appendix~\ref{app:<name>}`) where the text was.

## Figures

All five figures `main.tex` uses are in `figures/`: `bench60_g.png` and `bench60_path.png` from the 27 Oct internal
writeup, and `units_paths.png`, `stable_rank3_words.png`, `cov_images.png` uploaded by Truett on 5 Nov.

`units_paths.png` shows LENGTH, S20_MK2 and the hybrid only, not the dual and triple searches that its table lists.

## Open issues in `main.tex`

- Three references point at nothing: `fig:stable_split` and `tab:stable_ranks` (the rank 4 / rank 5 figure and table)
  and `sec:hybrid`.
- The paragraph "The best image passes LENGTH at every budget, but the margin falls from 100 to 6 ..." appears twice in
  the CoV section, once saying a random image is worse than P (at 10^4) and once saying it is often cheaper (at 10^3).
  Keep one.
- The "every image" part covers MS640 only. The 3 Nov sweep also ran bench60 and ladder100 (best image, then LENGTH:
  640/640, 60/60, 97/100 at 10^5), and every one of those solves also comes from an image in the Aut(F2) orbit of P,
  so they are AC paths, not only stable certificates.
- Ryan Zang's CoV-gate search (`results/ryan_full_1e6/`) is not in the paper yet.
- "We compare the three methods" in the Scores paragraph now covers six rows.
- The Elliot (dual / triple) numbers in both score tables were checked against `results/elliot_cost/COST_TABLE.md`
  and `results/elliot_100k/SUMMARY_TABLE.md`: they all match.
