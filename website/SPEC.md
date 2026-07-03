# AC-SolverX Path Explorer — build contract

You are building the **view layer** of a static, zero-build, dependency-free website. Two
load-bearing files already exist, are tested, and are FROZEN — code against them, do not edit them:

- `index.html` — the DOM. Every element id below already exists in it. Read it.
- `js/data.js` — the data spine (`window.ACXData`). Tested against real data. Read it. Use it; do
  not re-implement word/move/decoding logic.

Serve locally with `python -m http.server` from `website/` (fetch needs http, not file://).

The domain: each record is a solution path that trivializes a **stabilized** balanced presentation.
n_gen = 3. "Trivial" = **three length-1 relators** (total length 3) — NOT length 2. A step is a
**substitution supermove**: exactly one relator is replaced. States are canonical + reordered every
step, so relator slots are NOT stable — identify changes by content (data.js does this). The initial
state carries a **change of variables** `z = w`; `w` is generic (r1, r2, x, y, or arbitrary like
`xy`) and `data.js` decodes it. Do not hardcode the 4 fixed arms anywhere.

---

## `js/data.js` API you consume (already implemented — DO NOT reimplement)

```
ACXData.parseJsonl(text) -> records[]                 // tolerant JSONL/JSON-array
ACXData.buildDataset(records) -> Dataset              // merge both streams
ACXData.buildSteps(pathRecord) -> Solution            // render model for the player
ACXData.wordToStr(word) -> "Yx"                        // int-word -> letters; "ε" if empty
ACXData.wordToTokens(word) -> [{v,ch,gen,inverse}]     // for colored letter rendering
ACXData.armSymbol(arm) -> "r₁"|"r₂"|"x"|"y"|"g"|...
ACXData.histogram(values, binSize?) -> [{x0,x1,count}]
ACXData.countBy(items, fn) -> Map
```

**Dataset** = `{ items[], byKey:Map, byIdx:Map, arms[], datasets[], budgets[], counts:{total,solved,unsolved,withPath} }`
- `items[]`: one per (dataset, idx, arm, budget): `{ key, dataset, idx, arm, budget, solved, calib, path }`
  - `calib` = metrics record (may be null): `.nodes_explored .wall_time_s .path_len .revert_hits .nodes_per_sec .exhausted_budget .peak_rss_mb`
  - `path` = path record or null (present iff solved with a stored path)
- `byIdx`: `Map("dataset|idx" -> { dataset, idx, arms:Map(armName -> item) })` — **this powers the
  per-presentation arm selector** (which z=w choices exist for this presentation).

**Solution** (from `buildSteps(item.path)`):
```
{ arm, armSymbol, dataset, idx, name, nGen, pathLen, finalTrivial, pathVerified,
  stabilization: { generator:"z", arm, armSymbol, word:[...], wordStr:"xy",
                   text:"z = r₁" | "z = xy", textFull:"z = r₁ = YYXyx" | "z = xy" },
  steps: [ Step, ... ] }              // steps.length = states + 1 (index 0 = initial)
Step = { index, isInitial, isFinal, state:[relator[]], relatorStrings:["Yx","Zxy",...],
         totalLen, family:"stabilization"|"substitution", summary,
         change: null (initial) | {
            fromWord, toWord, fromStr:[...], toStr:[...],      // the substituted relator, old→new
            moveTuple:[slot,ra_rot,c_rot,c_inv], moveTupleText, movedSlotParent, wellFormed } }
```
Render each step's `relatorStrings` as the presentation `⟨x,y,z | …⟩`. On a non-initial step,
highlight the relator equal to `change.toStr[0]` as the **new** one and show `fromStr[0] → toStr[0]`.
Show `moveTupleText` as small "raw move" metadata only. NEVER invent a `B·C⁻¹` operand reconstruction.

---

## Module interfaces (how app.js wires everything)

Each JS module attaches ONE global and nothing else runs on load (no side effects except defining the
global). app.js calls them.

```
window.ACXCharts   = { stackedBar(el, spec), histogram(el, bins, opts) }         // charts.js — PURE
window.ACXViewer   = { init(), render(dataset) }                                  // viewer.js
window.ACXDashboard= { init(), render(dataset), onShow() }                        // dashboard.js
window.ACX (owned by app.js) = { dataset, reload(records), route() }              // app.js
```

- `init()` runs once (cache DOM, wire event listeners). `render(dataset)` (re)draws from a Dataset and
  may be called many times (initial load, after upload, after reset).
- app.js bootstrap (on DOMContentLoaded): fetch `sample-data/manifest.json` → `{files:[...], label}`;
  fetch each file; `ACXData.parseJsonl` each; concat; `ACXData.buildDataset`; store as `ACX.dataset`;
  call `ACXViewer.render` and `ACXDashboard.render`; update `#data-summary`/`#data-dot`; then `route()`.
- Router: on `hashchange` + initial, read `location.hash` (`#/solutions` default, `#/analytics`,
  `#/about`); show the matching `#view-*` (add/remove `.hidden`), set `.active` on the matching
  `#nav-tabs .tab`; when analytics becomes visible call `ACXDashboard.onShow()`.
- Upload (`#file-input` change, `#dropzone` drop): read ALL selected files (multiple!), parse+concat,
  rebuild dataset, re-render both views, set `#data-summary` to e.g. "Custom · N solutions", `#data-dot`
  to the custom color. `#reset-sample` reloads the manifest. `#toggle-upload` shows/hides `#upload-panel`.

---

## DOM ids already in index.html (bind to these; don't add/rename)

Header/data-bar: `#nav-tabs .tab[data-view]`, `#data-summary`, `#data-dot`, `#toggle-upload`,
`#upload-panel`, `#dropzone`, `#file-input`, `#upload-hint`, `#reset-sample`.
Views: `#view-solutions`, `#view-analytics`, `#view-about` (toggle `.hidden`).

**Solutions (viewer.js):** `#solutions-stats` (fill 4 `.stat-card`s: total, solved, unsolved, avg path
length), `#search-input`, `#filter-buttons .seg[data-filter=all|solved|unsolved]`, `#dataset-select`,
`#arm-filter`, `#presentations-grid`, `#grid-empty`, and the player:
`#player` (`.hidden` until a card is opened), `#player-title`, `#player-meta`, `#player-close`,
`#arm-selector` (fill one button per arm available for this presentation from `byIdx`), `#stab-banner`,
`#player-stage` (the big current-step view), controls `#player-first #player-prev #player-play
#player-next #player-last`, `#player-scrubber` (range), `#player-stepnum`, `#player-timeline` (ol; one
clickable row per step, jumps the player).

**Analytics (dashboard.js):** `#analytics-stats` (overview cards), `#dash-dataset`, `#dash-arm`,
`#dash-scope`, chart containers `#chart-solve-by-arm`, `#chart-pathlen-hist`, `#chart-nodes-solved`,
`#chart-time-hist`, `#chart-solve-by-dataset`, `#dash-table` (table), `#dash-table-scope`.

---

## Player interaction (viewer.js) — the "click and space through it" UX

- Opening a grid card opens `#player` for `(dataset, idx)`, defaulting to the first available arm (order
  r1,r2,x,y,g). Build the arm selector from `byIdx.get("dataset|idx").arms`; each button switches arm
  (re-run `buildSteps` on that arm's `path`, reset to step 0). Mark unsolved arms (no path) disabled with
  a hint. Highlight the active arm button.
- Transport: First/Prev/Play/Next/Last + a scrubber + "i / N" counter. Play auto-advances ~1 step/900ms,
  stops at the end, toggles the play button ▶/⏸.
- **Keyboard (only when player open AND solutions view active):** Space = play/pause, →/↓ = next, ←/↑ =
  prev, Home = first, End = last, Esc = close. `preventDefault` on those. Do not hijack keys while the
  user is typing in the search box.
- `#player-stage` shows: step index/summary; the presentation `⟨x,y,z | R…⟩` with each relator on its own
  line (monospace, colored letters via `wordToTokens`); on non-initial steps the changed relator badged
  "new" and a line `fromStr → toStr`; total length; the raw `moveTupleText` in a muted line; on the final
  step a success flourish "Trivial presentation reached ⟨x,y,z | x,y,z⟩". On the initial step show the
  `#stab-banner` text `stabilization.textFull` ("z = r₁ = YYXyx" / "z = xy").
- Timeline: every step as a compact row (index, summary, length); clicking jumps; the current step row is
  highlighted and scrolled into view.

## Charts (charts.js) — bounded, 2 pure functions, responsive SVG

Use inline SVG with a fixed `viewBox="0 0 W H"` (e.g. 640×360), `width:100%; height:auto;
preserveAspectRatio="xMidYMid meet"` so charts scale and work even if rendered while their view is
hidden (do NOT measure clientWidth). Axis labels, gridlines, value labels, and a native `<title>` tooltip
on each bar/bin. Empty-data → a centered "No data" note.

- `stackedBar(el, { categories:[{label, segments:[{key,value,color,title}]}], legend:[{key,color,label}], yLabel })`
- `histogram(el, bins/*[{x0,x1,count}]*/, { color, xLabel, yLabel, xTickFormat?(x) })`

## Dashboard charts (dashboard.js) — exact mappings

Filter `dataset` items by `#dash-dataset`/`#dash-arm` (default "all"); set `#dash-scope` to the active scope.
1. `#chart-solve-by-arm` — `stackedBar`, one category per arm; segments solved (green `--ok`) + unsolved
   (red `--err`). Counts from items.
2. `#chart-pathlen-hist` — `histogram` of `item.path`'s `path_len` over SOLVED items, binSize 1, color `--accent`.
3. `#chart-nodes-solved` — `histogram` of `calib.nodes_explored` over SOLVED items only (small values),
   color `--accent-2`. (Keep solved separate from unsolved: unsolved ≈ the budget cap, mixing misleads.)
4. `#chart-time-hist` — `histogram` of `calib.wall_time_s` over SOLVED items, color `--gen-z`.
5. `#chart-solve-by-dataset` — `stackedBar`, one category per dataset, solved/unsolved segments.
Overview cards `#analytics-stats`: total, solved, solve-rate %, arms count, datasets count. Table
`#dash-table`: a row per arm — arm, N, solved, solve %, median path_len, median nodes (solved), median
wall_time_s (solved). Label everything "loaded dataset"; never present the sample solve-rate as a project
result (the sample is mostly-easy). `#dash-table-scope`/`#dash-scope` reflect the active filters.

---

## Design system (css/styles.css) — dark, modern, calm. Own ALL styling.

Define these CSS custom properties on `:root` and use them everywhere (JS chart code reads the same hexes):

```
--bg:#0b0f17  --bg-elev:#131a26  --bg-card:#161f2e  --border:#243044
--text:#e6edf6  --text-dim:#9fb0c6  --muted:#6b7c93
--accent:#5b9dff  --accent-2:#7c5cff
--ok:#35d07f  --warn:#ffb454  --err:#ff6b6b
--gen-x:#5b9dff  --gen-y:#35d07f  --gen-z:#c792ea      /* letter colors; inverses render dimmer/italic */
--arm-r1:#5b9dff --arm-r2:#7c5cff --arm-x:#35d07f --arm-y:#ffb454 --arm-g:#ff6b9d
--radius:12px  --radius-sm:8px
--mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace
```
System UI font for chrome; `--mono` for relators/words/numbers. Cards: `--bg-card`, 1px `--border`,
`--radius`, subtle shadow. Sticky header + data-bar. Grid: responsive `auto-fill minmax(230px,1fr)`;
each card shows `#idx`, the presentation `⟨…⟩` preview (monospace, truncated), a solved/unsolved pill,
and a small hint of how many z=w arms exist. Solved pill green, unsolved red. Player is a prominent
panel; `#player-stage` large and central; controls a clean transport bar; scrubber styled. Segmented
controls, selects, buttons (`.btn .btn-ghost`), pills, `.stat-card`, `.chart-card`, `.data-table`,
`.timeline` rows (with a left rail + step dot; current row accented; final row green). Letter coloring:
`.tok-x/.tok-y/.tok-z` + an `.inv` modifier for inverses. Mobile-friendly (grid collapses, controls wrap,
no horizontal page scroll — wide tables/charts scroll inside their own container). Respect
`prefers-reduced-motion`. Keep it polished but not noisy.
```

## Amendment (2026-07-02) — provenance, non-redundant stats, move animation

This supersedes the "NEVER invent a `B·C⁻¹` operand reconstruction" line above in one
precise way: `data.js` now RECOVERS a factorization per step (`change.recon`, via
`ACXData.reconstructMove(parent, child, moveTuple)`) by replaying the actual move rule;
it is only non-null when the replay reproduces the child relator exactly (validated at
100% across all bundled paths). Inventing operands without that replay-check remains
forbidden — when `recon` is null the viewer falls back to plain old→new.

New data.js API: `SUBSET_LABELS / subsetLabel / subsetOfEntry` (provenance: 1190MS splits
into `original` idx<640 / `hard` idx≥640; registry records may override), `groupStats(ds,
{dataset, arm, subset})` (presentation-level, NON-redundant counts — powers the stat
cards), `itemPathLen`, `rollWord`, `minimalRotation`, `canonicalRelator`,
`compareRelators`, `spliceTrace`, `reconstructMove`. `buildDataset` additionally consumes
`{kind:"registry", dataset, idx, subset, n_gen, relators}` records
(`sample-data/registry_1190MS.jsonl` declares all 1190 presentations so never-attempted
ones appear as "Not attempted" cards and totals read over the full dataset).

New DOM ids: `#subset-filter` (solutions controls), `#dash-subset` (analytics controls),
`#player-speed` (Slow/Normal/Fast/Instant; value = duration multiplier, 0 = instant),
`#player-replay` (replay current step's animation; keyboard `R`). The solved segmented
control gained `data-filter="unattempted"`.

Viewer: stat cards re-render on every filter change from `groupStats` (Total under
dataset=1190MS is 1190 for ANY arm choice); cards carry subset badges + per-arm outcome
chips; the player animates each step in phases (roles → invert → rotate → splice →
one-pair-at-a-time cancellation → cyclic trim → canonical settle), driven entirely by
`change.recon`. Next during an animation lands it instantly; prev/scrub/jump are instant;
autoplay chains animations with one shared cancellation token.
