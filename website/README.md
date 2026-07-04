# AC-SolverX · Path Explorer

A static, zero-build website for browsing and replaying **substitution-supermove**
solution paths that trivialize **stabilized** balanced group presentations — the
change-of-variables (`z = w`) construction used by AC-SolverX. It ships a small sample
dataset, and can load any of your own Colab/local sweep output instead.

No build step, no framework, no external network calls — plain HTML/CSS/JS that runs
straight off disk via a local static server.

Highlights:

- **Slow-motion move player (rings + tiles)** — every substitution supermove replays in
  human-paced phases (Roles → Invert → Rotate → Splice → Cancel → Settle, tracked by phase
  chips). Each operand row carries a **ring inset** drawing the relator as the cyclic word
  it is: rotation moves the *cut marker*, never the letters, while the row's tiles slide
  with wrap-around; splicing flies the partner's tiles across with a persistent **seam**
  marking the join; inverse pairs then zip shut at the seam (cyclic cancellations draw a
  wrap-around arc). Speed control (Slow/Normal/Fast/Instant), **↻ Replay move** (`R`),
  Space/arrow keys. The shown factorization is *reconstructed* by re-running the move
  rule and only displayed when it reproduces the stored next state exactly (100% of
  bundled paths verified).
- **Provenance on every card** — MS(1190) is split into **Original 640** (idx 0–639, run
  locally under 8 `z = w` arms) and **Hard 550** (idx 640–1189, registered via
  `sample-data/registry_1190MS.jsonl` but not attempted yet). Cards, filters, the player
  header and Analytics all carry the subset.
- **Non-redundant totals** — stat cards count *presentations*, not (presentation × arm)
  rows: with dataset 1190MS and any single arm selected, Total reads 1190 with
  solved / unsolved-searched / not-attempted breakdown.

## Running it

```bash
cd website
python -m http.server 8000
```

Then open <http://localhost:8000> in a browser.

The site must be served over `http://`, not opened as a `file://` URL — the sample
data is loaded with `fetch()`, which browsers block for local files.

## Loading your own results

Click **"Load your own results…"** in the header, then drop in the JSONL files from a
sweep — any number at once, e.g.:

```
paths_<run>.jsonl
calibration_<run>.jsonl
```

Both are plain JSONL (one JSON object per line). Drop them **together** (or select
both with the file picker) — records are auto-classified by shape and merged on
`(dataset, idx, arm, budget_nodes)`, so a path record and its matching calibration
record become one item regardless of file order or how many files you split them
across. Click **"Reset to sample data"** to go back to the bundled dataset.

## Data model

Each row in the explorer is one *(dataset, idx, arm, budget)* combination — one
attempt to trivialize a given presentation under one **change of variables**:

- **Two record streams**, merged by key:
  - *Path records* (`paths_*.jsonl`) — carry `states` and `moves`: the full solution
    path, if one was found.
  - *Calibration records* (`calibration_*.jsonl`) — carry `solved`, `nodes_explored`,
    `wall_time_s`, and other search metrics, whether or not a path was kept.
- **Arms** are the different choices of the defining word `w` in the change of
  variables `z = w(x, y)` — e.g. `z = r1`, `z = r2`, `z = x`, `z = y`, or an arbitrary
  word. The same presentation can be attempted under several arms; the player lets
  you switch between them for a given presentation.
- **Substitution supermove**: each step of a path replaces exactly one relator with
  the freely- and cyclically-reduced splice of two (rotated) relators — a composite of
  classical Andrews–Curtis moves taken as one atomic move. States are stored canonical
  and reordered at every step, so a relator's position is not stable across
  steps — the explorer identifies the changed relator by content, not by slot.
- **Goal**: with `n_gen = 3`, the trivial presentation is **three length-one
  relators** (total length 3) — `⟨x, y, z | x, y, z⟩` — not the length-2 goal of the
  classical 2-generator Miller–Schupp problem.

See `SPEC.md` for the exact record/module contracts, and the in-app **About** tab for
the reader-facing explanation.

## Credit

Inspired by the [Miller–Schupp Path Viewer](https://github.com/Avi161/miller-schupp-path-viewer).
Part of *AC-SolverX* ("The Two-Hump Problem").
