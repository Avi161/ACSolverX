# Conference paper draft

`avi.tex` is the paper (it mirrors Truett's Overleaf project: `avi.tex`, `figures/`, `appendix/`). It started as the
version pasted into the project thread on 5 Nov 2026. Figures go
in `figures/`. This branch (`paper`) was cut from `ryan-replication`, so it also carries the Elliot Steffen and Ryan
Zang replications and their results (`docs/ELLIOT_REPLICATION.md`, `docs/RYAN_REPLICATION.md`).

No pull request for this branch. Never add solutions to the 10,115 SAIR ACC challenges here.

## Appendix

All appendices live in one file, `appendix/appendix.tex`: one unnumbered section titled "Appendix", whose parts are
subsections lettered A, B, C (A is bench60). `avi.tex` pulls it in just before the bibliography with
`\input{appendix/appendix}`. Point to a part from the main text with `Appendix~\ref{app:<name>}`, which prints
"Appendix A". Figure paths inside it are relative to `avi.tex`.

## Figures

Five figures are in `figures/`: `bench60_g.png` and `bench60_path.png` from the 27 Oct internal
writeup, and `units_paths.png`, `stable_rank3_words.png`, `cov_images.png` uploaded by Truett on 5 Nov.

`units_paths.png` shows LENGTH, S20_MK2 and the hybrid only, not the dual and triple searches that its table lists.

Missing: `stable_ranks_split.png` (in Overleaf, not uploaded yet).

## Open issues in `avi.tex`

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
