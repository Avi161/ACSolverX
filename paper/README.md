# Stable-AC Preprint

NeurIPS-format preprint (anonymized review mode) covering the stable Andrews–Curtis
experiment campaigns of 2026-06-29 → 2026-07-06 (`experiments/`, `results/`).

## Deliverables

- `paper.md` — full markdown draft (readable standalone, embeds `figures/out/*.png`).
- `paper.tex` — NeurIPS 2025 LaTeX master (`neurips_2025.sty`, anonymized/review mode;
  switch to `\usepackage[preprint]{neurips_2025}` to deanonymize).
- `paper.pdf` — compiled output (tectonic).
- `refs.bib` — bibliography (web-verified entries; `% TODO` marks any unresolved).

## Build

```bash
# figures + tables (regenerated from raw JSONL result streams — never hand-edited)
"$REPO_ROOT/.venv/bin/python" paper/figures/make_figures.py --all
"$REPO_ROOT/.venv/bin/python" paper/tables/make_tables.py

# compile
python paper/build/build_paper.py     # runs tectonic paper/paper.tex
```

`$REPO_ROOT` = the main checkout (its `.venv` has matplotlib; a worktree does not
carry `.venv`).

## Provenance policy

Every number in the paper is machine-derived from the raw result streams:

- `figures/out/figure_digest.json` — every plotted value, emitted by `make_figures.py`.
- `tables/out/tables_digest.json` — every printed cell, emitted by `make_tables.py`.
- `fact_check/claims.tsv` + `fact_check/report.md` — an independent recomputation
  (`fact_check/recompute.py`) of every numeric claim in the final text, straight from
  the raw JSONL/gz (not from the digests). 100% match is a release gate.

Authoritative sources when local copies disagree:
`results/stable_ac/ak3_stable_proof/archive/*.jsonl.gz` + `collect_summary.json`
(campaign totals); `results/stable_ac/3_generators_w_choices/ms640/` (z=w arms —
NOT the stale `results/solved640/` snapshot).
