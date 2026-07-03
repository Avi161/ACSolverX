/*
 * viewer.js — Solutions view: presentation grid + animated path player.
 *
 * Consumes window.ACXData (js/data.js) for ALL word/move/decode/reconstruction logic;
 * never reimplements it. Owns: #solutions-stats, #search-input, #filter-buttons,
 * #dataset-select, #subset-filter, #arm-filter, #presentations-grid, #grid-empty, and
 * the whole #player subtree (arm selector, stab banner, stage, transport, speed,
 * replay, scrubber, timeline). See website/SPEC.md for the full contract.
 *
 * Two ideas dominate this file:
 *  - NON-REDUNDANT stats: the stat cards count PRESENTATIONS (via ACXData.groupStats),
 *    never (presentation × arm) rows — pick arm r1 on 1190MS and Total reads 1190.
 *  - The MOVE ANIMATION: each step's reconstructed factorization (change.recon) is
 *    replayed as a slow, human-paced sequence — pick operands → invert/rotate →
 *    splice at the cancelling boundary → pluck inverse pairs one at a time → cyclic
 *    trim → settle into the canonical next state. Every frame is derived from the
 *    verified reconstruction; nothing is invented. If recon is missing (foreign data),
 *    the player falls back to the instant old→new rendering.
 *
 * window.ACXViewer = { init(), render(dataset) }
 */
(function (global) {
  "use strict";

  const D = global.ACXData;
  const ARM_ORDER = ["r1", "r2", "x", "y", "g"];

  // Base durations (ms) at Normal speed; the speed select multiplies these.
  const DUR = {
    context: 1100, invert: 850, rotate: 850, splice: 1050,
    pluckMark: 340, pluckGap: 240, pluckPause: 260,
    cyclic: 780, result: 950, betweenSteps: 550,
  };

  // ---- module state ---------------------------------------------------------
  let dom = null;
  let initialized = false;
  let dataset = null;
  let gridData = null;         // reps_grid.json: the (n,w) map of the whole MS(1190) family
  let gridFetchStarted = false;

  const filters = { search: "", solved: "all", dataset: "all", subset: "all", arm: "all", layout: "grid" };

  const player = {
    entry: null,
    arm: null,
    solution: null,
    stepIndex: 0,
    playing: false,
  };

  // One animation at a time; navigating cancels it and the canceller re-renders.
  const anim = { token: null };
  function cancelAnim() {
    if (anim.token) anim.token.cancelled = true;
    anim.token = null;
  }
  function newToken() {
    cancelAnim();
    const t = { cancelled: false };
    anim.token = t;
    return t;
  }
  function speedMult() {
    const v = parseFloat(dom.speed.value);
    return isNaN(v) ? 1 : v; // 0 = instant
  }
  function wait(ms, token) {
    return new Promise(function (resolve) {
      setTimeout(function () { resolve(!token.cancelled); }, ms);
    });
  }

  // ---- tiny DOM helper (textContent-based -> safe against untrusted upload data) --
  function h(tag, opts, children) {
    const e = document.createElement(tag);
    if (opts) {
      for (const k in opts) {
        if (!Object.prototype.hasOwnProperty.call(opts, k)) continue;
        if (k === "class") e.className = opts[k];
        else if (k === "text") e.textContent = opts[k];
        else if (k === "html") e.innerHTML = opts[k]; // only ever used with literal, non-record strings
        else e.setAttribute(k, opts[k]);
      }
    }
    if (children) {
      const list = Array.isArray(children) ? children : [children];
      for (const c of list) {
        if (c == null) continue;
        e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      }
    }
    return e;
  }

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  // ---- generic helpers over ACXData ------------------------------------------
  function genLetters(nGen) {
    const out = [];
    for (let g = 1; g <= nGen; g++) out.push(D.letter(g));
    return out;
  }

  /** Colored letter spans for a word (array of signed ints). */
  function tokensNode(word) {
    const span = h("span", { class: "word-tokens" });
    for (const t of D.wordToTokens(word)) {
      const gen = t.gen === 1 ? "x" : t.gen === 2 ? "y" : t.gen === 3 ? "z" : "g";
      span.appendChild(h("span", { class: "tok-" + gen + (t.inverse ? " inv" : "") }, t.ch));
    }
    if (span.childNodes.length === 0) span.appendChild(h("span", { class: "tok-eps" }, "ε"));
    return span;
  }

  /** One letter tile (the animation's unit). */
  function tileNode(v) {
    const gen = Math.abs(v) === 1 ? "x" : Math.abs(v) === 2 ? "y" : Math.abs(v) === 3 ? "z" : "g";
    return h("span", { class: "tile tile-" + gen + (v < 0 ? " inv" : "") }, D.letter(v));
  }

  function armOrderFor(entry) {
    const order = [];
    for (const a of ARM_ORDER) if (entry.arms.has(a)) order.push(a);
    const extra = [];
    for (const a of entry.arms.keys()) if (order.indexOf(a) === -1) extra.push(a);
    extra.sort();
    return order.concat(extra);
  }

  /** Best item to represent a (dataset,idx) card: prefer a solved arm (has a stored path). */
  function pickDisplayItem(entry) {
    let withPath = null, first = null;
    for (const a of armOrderFor(entry)) {
      const it = entry.arms.get(a);
      if (!first) first = it;
      if (!withPath && it.path) withPath = it;
    }
    return withPath || first;
  }

  function entrySolved(entry) {
    for (const it of entry.arms.values()) if (it.solved) return true;
    return false;
  }

  /** solved | unsolved | unattempted — for the CURRENT arm filter. */
  function entryStatus(entry, arm) {
    if (arm && arm !== "all") {
      const it = entry.arms.get(arm);
      if (!it) return "unattempted";
      return it.solved ? "solved" : "unsolved";
    }
    if (entry.arms.size === 0) return "unattempted";
    return entrySolved(entry) ? "solved" : "unsolved";
  }

  // ---- DOM caching + wiring (init, runs once) --------------------------------
  function cacheDom() {
    dom = {
      viewSolutions: document.getElementById("view-solutions"),
      stats: document.getElementById("solutions-stats"),
      search: document.getElementById("search-input"),
      filterButtons: document.getElementById("filter-buttons"),
      datasetSelect: document.getElementById("dataset-select"),
      subsetFilter: document.getElementById("subset-filter"),
      armFilter: document.getElementById("arm-filter"),
      viewToggle: document.getElementById("view-toggle"),
      grid: document.getElementById("presentations-grid"),
      nwGrid: document.getElementById("nw-grid"),
      gridEmpty: document.getElementById("grid-empty"),

      player: document.getElementById("player"),
      playerTitle: document.getElementById("player-title"),
      playerMeta: document.getElementById("player-meta"),
      playerClose: document.getElementById("player-close"),
      armSelector: document.getElementById("arm-selector"),
      stabBanner: document.getElementById("stab-banner"),
      stage: document.getElementById("player-stage"),
      first: document.getElementById("player-first"),
      prev: document.getElementById("player-prev"),
      play: document.getElementById("player-play"),
      next: document.getElementById("player-next"),
      last: document.getElementById("player-last"),
      scrubber: document.getElementById("player-scrubber"),
      stepnum: document.getElementById("player-stepnum"),
      timeline: document.getElementById("player-timeline"),
      speed: document.getElementById("player-speed"),
      replay: document.getElementById("player-replay"),
    };
  }

  function wireControls() {
    dom.search.addEventListener("input", function () {
      filters.search = dom.search.value.trim();
      renderGrid();
    });

    dom.filterButtons.addEventListener("click", function (e) {
      const btn = e.target.closest(".seg");
      if (!btn || !dom.filterButtons.contains(btn)) return;
      filters.solved = btn.getAttribute("data-filter") || "all";
      for (const s of dom.filterButtons.querySelectorAll(".seg")) s.classList.toggle("active", s === btn);
      renderGrid();
    });

    dom.datasetSelect.addEventListener("change", function () {
      filters.dataset = dom.datasetSelect.value;
      rebuildSubsetOptions();
      renderGrid();
    });

    dom.subsetFilter.addEventListener("change", function () {
      filters.subset = dom.subsetFilter.value;
      renderGrid();
    });

    dom.armFilter.addEventListener("change", function () {
      filters.arm = dom.armFilter.value;
      renderGrid();
    });

    dom.grid.addEventListener("click", function (e) {
      const card = e.target.closest(".presentation-card");
      if (!card || !dom.grid.contains(card) || card.classList.contains("card-unattempted")) return;
      openPlayer(card.getAttribute("data-dataset"), card.getAttribute("data-idx"));
    });

    dom.viewToggle.addEventListener("click", function (e) {
      const btn = e.target.closest(".seg");
      if (!btn || !dom.viewToggle.contains(btn)) return;
      filters.layout = btn.getAttribute("data-layout") || "grid";
      for (const s of dom.viewToggle.querySelectorAll(".seg")) s.classList.toggle("active", s === btn);
      renderGrid();
    });

    dom.nwGrid.addEventListener("click", function (e) {
      const cell = e.target.closest(".nw-cell");
      if (!cell || !dom.nwGrid.contains(cell) || cell.classList.contains("nw-cell-dead")) return;
      openPlayer(cell.getAttribute("data-dataset"), cell.getAttribute("data-idx"));
    });
  }

  function wirePlayerControls() {
    dom.playerClose.addEventListener("click", closePlayer);

    dom.first.addEventListener("click", function () { stopPlaying(); gotoStep(0); dom.first.blur(); });
    dom.prev.addEventListener("click", function () { stopPlaying(); gotoStep(player.stepIndex - 1); dom.prev.blur(); });
    dom.next.addEventListener("click", function () { stopPlaying(); nextStep(); dom.next.blur(); });
    dom.last.addEventListener("click", function () {
      stopPlaying();
      if (player.solution) gotoStep(player.solution.steps.length - 1);
      dom.last.blur();
    });
    dom.play.addEventListener("click", function () { togglePlay(); dom.play.blur(); });
    dom.replay.addEventListener("click", function () { stopPlaying(); replayStep(); dom.replay.blur(); });

    dom.scrubber.addEventListener("input", function () {
      stopPlaying();
      gotoStep(Number(dom.scrubber.value));
    });

    dom.armSelector.addEventListener("click", function (e) {
      const btn = e.target.closest(".arm-btn");
      if (!btn || btn.disabled || !dom.armSelector.contains(btn)) return;
      selectArm(btn.getAttribute("data-arm"));
      btn.blur();
    });

    dom.timeline.addEventListener("click", function (e) {
      const row = e.target.closest(".timeline-row");
      if (!row || !dom.timeline.contains(row)) return;
      stopPlaying();
      gotoStep(Number(row.getAttribute("data-index")));
    });
  }

  function wireKeyboard() {
    document.addEventListener("keydown", function (e) {
      if (dom.player.classList.contains("hidden")) return;
      if (dom.viewSolutions.classList.contains("hidden")) return;
      const active = document.activeElement;
      const tag = active && active.tagName;
      if (active === dom.search || tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      switch (e.key) {
        case " ":
        case "Spacebar":
          e.preventDefault();
          togglePlay();
          break;
        case "ArrowRight":
        case "ArrowDown":
          e.preventDefault();
          stopPlaying();
          nextStep();
          break;
        case "ArrowLeft":
        case "ArrowUp":
          e.preventDefault();
          stopPlaying();
          gotoStep(player.stepIndex - 1);
          break;
        case "Home":
          e.preventDefault();
          stopPlaying();
          gotoStep(0);
          break;
        case "End":
          e.preventDefault();
          stopPlaying();
          if (player.solution) gotoStep(player.solution.steps.length - 1);
          break;
        case "r":
        case "R":
          e.preventDefault();
          stopPlaying();
          replayStep();
          break;
        case "Escape":
          e.preventDefault();
          closePlayer();
          break;
        default:
          return;
      }
    });
  }

  // ---- stat cards (NON-redundant: presentations, not presentation×arm rows) -----
  function renderStats() {
    clear(dom.stats);
    const g = D.groupStats(dataset, {
      dataset: filters.dataset, arm: filters.arm, subset: filters.subset,
    });
    const scope = [];
    if (filters.dataset !== "all") scope.push(filters.dataset);
    if (filters.subset !== "all") scope.push(D.subsetLabel(filters.subset));
    scope.push(filters.arm === "all" ? "all z-words" : "z = " + D.armSymbol(filters.arm));

    // "cell" mode: the unit is one (presentation × z-word) attempt. Total then counts the full
    // grid (e.g. 1190 × 8 = 9520). With a single arm, cells == presentations, so it reads 1190.
    const cellMode = filters.arm === "all";
    const nZ = filters.dataset !== "all" ? dataset.armsByDataset[filters.dataset] : null;
    const num = function (n) { return n.toLocaleString(); };
    let totalSub = scope.join(" · ");
    if (cellMode && nZ) totalSub = num(g.presentations) + " × " + nZ + " z-words";

    const cards = [
      { label: cellMode ? "Presentation × z-word" : "Presentations", value: num(g.total), sub: totalSub },
      { label: "Solved", value: num(g.solved), cls: "stat-ok", sub: g.attempted ? Math.round(100 * g.solved / g.attempted) + "% of searched" + (cellMode ? " cells" : "") : "" },
      { label: "Unsolved (searched)", value: num(g.unsolved), cls: "stat-err", sub: "budget exhausted" },
      { label: "Not attempted", value: num(g.notAttempted), cls: "stat-muted", sub: g.notAttempted ? (cellMode ? "z-word cells not yet run" : "awaiting a bigger run") : "" },
      { label: "Avg. path length", value: g.avgPathLen == null ? "—" : g.avgPathLen.toFixed(2), sub: cellMode ? "best z-word per presentation" : "" },
    ];
    for (const c of cards) {
      dom.stats.appendChild(h("div", { class: "stat-card" + (c.cls ? " " + c.cls : "") }, [
        h("div", { class: "stat-value" }, c.value),
        h("div", { class: "stat-label" }, c.label),
        c.sub ? h("div", { class: "stat-sub" }, c.sub) : null,
      ]));
    }
  }

  // ---- selects ------------------------------------------------------------
  function subsetsForDataset(dsName) {
    const seen = new Set();
    for (const entry of dataset.byIdx.values()) {
      if (dsName !== "all" && entry.dataset !== dsName) continue;
      if (entry.subset) seen.add(entry.subset);
    }
    return Array.from(seen);
  }

  function rebuildSubsetOptions() {
    const options = subsetsForDataset(filters.dataset);
    clear(dom.subsetFilter);
    dom.subsetFilter.appendChild(h("option", { value: "all" }, "All subsets"));
    for (const s of options) dom.subsetFilter.appendChild(h("option", { value: s }, D.subsetLabel(s)));
    if (options.indexOf(filters.subset) === -1) filters.subset = "all";
    dom.subsetFilter.value = filters.subset;
  }

  function renderSelects() {
    clear(dom.datasetSelect);
    dom.datasetSelect.appendChild(h("option", { value: "all" }, "All datasets"));
    for (const dsName of dataset.datasets) {
      dom.datasetSelect.appendChild(h("option", { value: dsName }, dsName));
    }
    // Default to MS(1190) so the headline numbers read over the full 1190 out of the box.
    filters.dataset = dataset.datasets.indexOf("1190MS") !== -1 ? "1190MS" : "all";
    dom.datasetSelect.value = filters.dataset;

    rebuildSubsetOptions();

    clear(dom.armFilter);
    dom.armFilter.appendChild(h("option", { value: "all" }, "All z-words"));
    for (const arm of dataset.arms) {
      dom.armFilter.appendChild(h("option", { value: arm }, D.armSymbol(arm)));
    }
    dom.armFilter.value = "all";
  }

  // ---- grid -----------------------------------------------------------------
  function matchesFilters(entry) {
    if (filters.dataset !== "all" && entry.dataset !== filters.dataset) return false;
    if (filters.subset !== "all" && entry.subset !== filters.subset) return false;

    if (filters.search) {
      const terms = filters.search.split(/[,\s]+/).filter(Boolean);
      if (terms.length) {
        const idxStr = String(entry.idx);
        const hit = terms.some(function (t) { return idxStr.indexOf(t) !== -1; });
        if (!hit) return false;
      }
    }

    if (filters.solved !== "all" && entryStatus(entry, filters.arm) !== filters.solved) return false;
    return true;
  }

  function buildCard(entry) {
    const status = entryStatus(entry, filters.arm);
    const arms = armOrderFor(entry);
    const attempted = entry.arms.size > 0;

    const pillText = status === "solved" ? "Solved" : status === "unsolved" ? "Unsolved" : "Not attempted";
    const head = h("div", { class: "card-head" }, [
      h("span", { class: "card-idx" }, "#" + entry.idx),
      h("span", { class: "pill pill-" + status }, pillText),
    ]);

    // Provenance badge — the "is this one of the hard 550?" answer, on every card.
    const badges = h("div", { class: "card-badges" }, [
      h("span", { class: "card-dataset" }, entry.dataset),
      entry.subset ? h("span", { class: "badge-subset badge-" + entry.subset }, D.subsetLabel(entry.subset)) : null,
    ]);

    let previewText = "No stored path";
    const item = pickDisplayItem(entry);
    if (item && item.path && item.path.states && item.path.states[0]) {
      const gens = genLetters(item.path.n_gen || 3);
      const rels = item.path.states[0].map(D.wordToStr).join(", ");
      previewText = "⟨" + gens.join(",") + " | " + rels + "⟩";
    } else if (entry.reg && Array.isArray(entry.reg.relators)) {
      const gens = genLetters(entry.reg.n_gen || 2);
      const rels = entry.reg.relators.map(D.wordToStr).join(", ");
      previewText = "⟨" + gens.join(",") + " | " + rels + "⟩";
    }

    let armsNode;
    if (attempted) {
      // Per-arm chips, colored by that arm's outcome — the at-a-glance redundancy-free view.
      armsNode = h("div", { class: "card-arms-hint" });
      armsNode.appendChild(document.createTextNode(arms.length + (arms.length === 1 ? " arm: " : " arms: ")));
      for (const a of arms) {
        const it = entry.arms.get(a);
        armsNode.appendChild(h("span", {
          class: "arm-chip " + (it && it.solved ? "arm-chip-ok" : "arm-chip-bad"),
          title: "z = " + D.armSymbol(a) + (it && it.solved ? " · solved" : " · unsolved"),
        }, D.armSymbol(a)));
      }
    } else {
      armsNode = h("div", { class: "card-arms-hint muted" },
        "Not searched yet — needs a bigger budget run.");
    }

    const opts = {
      class: "card presentation-card" + (attempted ? "" : " card-unattempted"),
      "data-dataset": entry.dataset,
      "data-idx": String(entry.idx),
    };
    if (attempted) { opts.role = "button"; opts.tabindex = "0"; }
    return h("div", opts, [head, badges, h("pre", { class: "card-preview" }, previewText), armsNode]);
  }

  function gridAvailable() {
    return !!gridData && !!dataset && dataset.datasets.indexOf(gridData.linked_dataset || "1190MS") !== -1;
  }

  function ensureGridData() {
    if (gridFetchStarted) return;
    gridFetchStarted = true;
    fetch("sample-data/reps_grid.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (g) { gridData = g; if (dataset) renderGrid(); })
      .catch(function () { gridData = null; });
  }

  function renderGrid() {
    renderStats(); // stats always mirror the current selection
    const canGrid = gridAvailable();
    dom.viewToggle.classList.toggle("hidden", !canGrid);
    const useGrid = canGrid && filters.layout === "grid";
    dom.nwGrid.classList.toggle("hidden", !useGrid);
    dom.grid.classList.toggle("hidden", useGrid);
    if (useGrid) { dom.gridEmpty.classList.add("hidden"); renderNwGrid(); }
    else renderCards();
  }

  function renderCards() {
    clear(dom.grid);
    const entries = Array.from(dataset.byIdx.values());
    entries.sort(function (a, b) {
      return a.dataset < b.dataset ? -1 : a.dataset > b.dataset ? 1 : a.idx - b.idx;
    });
    let shown = 0;
    for (const entry of entries) {
      if (!matchesFilters(entry)) continue;
      dom.grid.appendChild(buildCard(entry));
      shown++;
    }
    dom.gridEmpty.classList.toggle("hidden", shown !== 0);
  }

  // ---- (n,w) grid: the whole MS(1190) family as a spreadsheet ---------------------
  // Rows = word w, columns = n. Trivial cells trivialized in the original run (→ 1190MS
  // solved path); labelled cells reduce to that unsolved class (→ ms_reps_unsolved). The
  // dataset/subset/solved/search filters DIM non-matching cells; the arm is chosen in the
  // player. Clicking a cell whose target presentation was actually attempted opens it.
  function nwCellActive(cell) {
    if (filters.dataset === "ms_reps_unsolved" && cell.status === "trivial") return false;
    if (filters.subset === "original" && cell.status !== "trivial") return false;
    if (filters.subset === "reps" && cell.status === "trivial") return false;
    if (filters.subset === "hard") return false; // the hard 550 have no (n,w) grid cell
    if (filters.solved === "solved" && cell.status !== "trivial") return false;
    if (filters.solved === "unsolved" && cell.status === "trivial") return false;
    if (filters.solved === "unattempted") return false;
    if (filters.search) {
      const terms = filters.search.split(/[,\s]+/).filter(Boolean);
      const idxStr = cell.status === "trivial" ? String(cell.ms_idx) : String(cell.rep_idx);
      if (terms.length && !terms.some(function (t) { return idxStr.indexOf(t) !== -1; })) return false;
    }
    return true;
  }

  function renderNwGrid() {
    clear(dom.nwGrid);
    const g = gridData;
    const byWN = {};
    for (const c of g.cells) (byWN[c.w] || (byWN[c.w] = {}))[c.n] = c;

    const legend = h("div", { class: "nw-legend" }, [
      h("span", { class: "nw-swatch nw-trivial" }), h("span", { class: "nw-legend-t" }, "trivialized"),
      h("span", { class: "nw-swatch nw-rep" }), h("span", { class: "nw-legend-t" }, "unsolved class (cell shows the rep) — click any cell to open the player"),
    ]);
    dom.nwGrid.appendChild(legend);

    const table = h("table", { class: "nw-table" });
    const thead = h("thead"); const hr = h("tr");
    hr.appendChild(h("th", { class: "nw-corner" }, "w \\ n"));
    for (const n of g.nvals) hr.appendChild(h("th", { class: "nw-nhead" }, String(n)));
    thead.appendChild(hr); table.appendChild(thead);

    const tbody = h("tbody");
    let lastLen = -1;
    for (const w of g.words) {
      const groupStart = w.length !== lastLen;
      lastLen = w.length;
      const tr = h("tr", { class: groupStart ? "nw-group-start" : "" });
      tr.appendChild(h("th", { class: "nw-whead", title: "w = " + w + "  (len " + w.length + ")" }, w));
      for (const n of g.nvals) {
        const cell = byWN[w] && byWN[w][n];
        if (!cell) { tr.appendChild(h("td", { class: "nw-cell nw-empty" })); continue; }
        const trivial = cell.status === "trivial";
        const targetDs = trivial ? (g.linked_dataset || "1190MS") : g.dataset;
        const targetIdx = trivial ? cell.ms_idx : cell.rep_idx;
        const entry = dataset.byIdx.get(targetDs + "|" + targetIdx);
        const clickable = !!(entry && entry.arms.size > 0);
        const cls = ["nw-cell", trivial ? "nw-trivial" : "nw-rep"];
        if (!nwCellActive(cell)) cls.push("nw-dim");
        if (!clickable) cls.push("nw-cell-dead");
        const td = h("td", {
          class: cls.join(" "),
          title: trivial
            ? "MS(" + n + ", " + w + ") · trivialized · 1190MS #" + cell.ms_idx
            : "MS(" + n + ", " + w + ") → unsolved class " + cell.status + " · rep #" + cell.rep_idx + " · z ∈ {r₁, r₂, x, y}",
        }, trivial ? "" : cell.status);
        if (clickable) { td.setAttribute("data-dataset", targetDs); td.setAttribute("data-idx", String(targetIdx)); }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    dom.nwGrid.appendChild(h("div", { class: "nw-scroll" }, [table]));
  }

  // ---- player: opening / arm switching ---------------------------------------
  function buildArmSelector(entry) {
    clear(dom.armSelector);
    for (const arm of armOrderFor(entry)) {
      const item = entry.arms.get(arm);
      const attempted = !!item;
      const solvedArm = !!(item && item.path);
      // Attempted arms are always selectable (solved → the path player; unsolved → the
      // stabilized-start + search-cost view). Only never-run arms are disabled.
      const btn = h("button", {
        class: "arm-btn" + (solvedArm ? "" : attempted ? " arm-btn-unsolved" : ""),
        type: "button",
        "data-arm": arm,
      }, D.armSymbol(arm));
      if (!attempted) {
        btn.disabled = true;
        btn.title = "Not attempted under z = " + D.armSymbol(arm);
        btn.classList.add("arm-btn-disabled");
      } else if (!solvedArm) {
        btn.title = "Unsolved under z = " + D.armSymbol(arm) + " (search hit the node budget)";
      }
      dom.armSelector.appendChild(btn);
    }
  }

  function highlightArmButton(arm) {
    for (const btn of dom.armSelector.querySelectorAll(".arm-btn")) {
      btn.classList.toggle("active", btn.getAttribute("data-arm") === arm);
    }
  }

  function defaultArmFor(entry) {
    const order = armOrderFor(entry);
    for (const a of order) { const it = entry.arms.get(a); if (it && it.path) return a; }
    return order[0] || null;
  }

  function openPlayer(datasetName, idxStr) {
    const key = datasetName + "|" + idxStr;
    const entry = dataset.byIdx.get(key);
    if (!entry || entry.arms.size === 0) return;

    player.entry = entry;
    buildArmSelector(entry);
    dom.playerTitle.textContent = "#" + entry.idx + " · " + entry.dataset;
    dom.player.classList.remove("hidden");

    const arm = defaultArmFor(entry);
    selectArm(arm);

    // With a large grid the player sits far below; jump it into view on open.
    // (Instant, not smooth: smooth scroll inside the nested scroll container is unreliable.)
    dom.player.scrollIntoView({ block: "start" });
  }

  function renderPlayerMeta(item, arm) {
    clear(dom.playerMeta);
    const entry = player.entry;
    if (entry && entry.subset) {
      dom.playerMeta.appendChild(h("span", { class: "badge-subset badge-" + entry.subset }, D.subsetLabel(entry.subset)));
    }
    const parts = [];
    parts.push("z = " + D.armSymbol(arm));
    if (item && item.calib) {
      const c = item.calib;
      parts.push(c.solved ? "solved" : "unsolved");
      if (c.path_len != null) parts.push("path length " + c.path_len);
      if (c.nodes_explored != null) parts.push(c.nodes_explored.toLocaleString() + " nodes");
      if (c.wall_time_s != null) parts.push(c.wall_time_s + "s");
      if (c.budget_nodes != null) parts.push("budget " + c.budget_nodes.toLocaleString());
      if (c.exhausted_budget) parts.push("budget exhausted");
    } else if (item && item.path) {
      parts.push("solved");
      if (item.path.path_len != null) parts.push("path length " + item.path.path_len);
    }
    dom.playerMeta.appendChild(h("span", null, " " + parts.join(" · ")));
  }

  function selectArm(arm) {
    if (!player.entry || !arm) return;
    stopPlaying();
    cancelAnim();
    player.arm = arm;
    const item = player.entry.arms.get(arm);
    highlightArmButton(arm);
    renderPlayerMeta(item, arm);

    if (item && item.path) {
      player.solution = D.buildSteps(item.path);
      const n = player.solution.steps.length;
      dom.scrubber.min = "0";
      dom.scrubber.max = String(n - 1);
      dom.scrubber.disabled = false;
      setTransportDisabled(false);
      buildTimeline();
      gotoStep(0);
    } else {
      player.solution = null;
      dom.scrubber.min = "0";
      dom.scrubber.max = "0";
      dom.scrubber.value = "0";
      dom.scrubber.disabled = true;
      setTransportDisabled(true);
      dom.stepnum.textContent = "0 / 0";
      clear(dom.timeline);
      dom.stabBanner.classList.add("hidden");
      renderUnsolvedStage(item);
    }
  }

  function setTransportDisabled(disabled) {
    for (const btn of [dom.first, dom.prev, dom.play, dom.next, dom.last, dom.replay]) btn.disabled = disabled;
  }

  function renderUnsolvedStage(item) {
    clear(dom.stage);
    const box = h("div", { class: "stage-step stage-unsolved" });
    const entry = player.entry;
    const reg = entry && entry.reg;
    const arm = player.arm;

    // The change of variables z = w for this arm: stored on the record, else derived —
    // x→x, y→y, r₁/r₂→that base relator (matches experiments/.../stabilize.py).
    let zword = item && item.calib && item.calib.z_word;
    if (!zword && reg && Array.isArray(reg.relators)) {
      if (arm === "x") zword = [1];
      else if (arm === "y") zword = [2];
      else if (arm === "r1") zword = reg.relators[0];
      else if (arm === "r2") zword = reg.relators[1];
    }

    if (reg && Array.isArray(reg.relators) && zword) {
      const third = D.cyclicReduce([3].concat(D.invertWord(zword))); // z · w⁻¹
      const state = [reg.relators[0], reg.relators[1], third];
      box.appendChild(h("div", { class: "stage-summary" }, "Stabilized start · z = " + D.wordToStr(zword)));
      const pres = h("div", { class: "presentation" });
      pres.appendChild(h("div", { class: "presentation-line presentation-open" }, "⟨x, y, z |"));
      state.forEach(function (word, s) {
        const row = h("div", { class: "relator-row" + (s === 2 ? " changed" : "") });
        row.appendChild(tokensNode(word));
        if (s === 2) row.appendChild(h("span", { class: "change-note" }, "= z · w⁻¹"));
        pres.appendChild(row);
      });
      pres.appendChild(h("div", { class: "presentation-line presentation-close" }, "⟩"));
      box.appendChild(pres);
      box.appendChild(h("div", { class: "total-len" }, "Total length: " + D.stateTotalLen(state)));
    }

    box.appendChild(h("p", { class: "unsolved-note" },
      "No solution found under this change of variables — the search hit its node budget."));
    if (item && item.calib) {
      const c = item.calib, bits = [];
      if (c.nodes_explored != null) bits.push(c.nodes_explored.toLocaleString() + " nodes explored");
      if (c.budget_nodes != null) bits.push("budget " + c.budget_nodes.toLocaleString());
      if (c.wall_time_s != null) bits.push(c.wall_time_s + "s");
      if (bits.length) box.appendChild(h("p", { class: "unsolved-note muted" }, bits.join(" · ")));
    }
    dom.stage.appendChild(box);
  }

  // ---- timeline ---------------------------------------------------------------
  function buildTimeline() {
    clear(dom.timeline);
    const steps = player.solution.steps;
    for (const step of steps) {
      const row = h("li", { class: "timeline-row" + (step.isFinal ? " final" : ""), "data-index": String(step.index) }, [
        h("span", { class: "timeline-index" }, "#" + step.index),
        h("span", { class: "timeline-summary" }, step.summary),
        h("span", { class: "timeline-len" }, "len " + step.totalLen),
      ]);
      dom.timeline.appendChild(row);
    }
  }

  function updateTimelineActive(i) {
    const rows = dom.timeline.querySelectorAll(".timeline-row");
    let currentRow = null;
    for (const row of rows) {
      const isCurrent = Number(row.getAttribute("data-index")) === i;
      row.classList.toggle("current", isCurrent);
      if (isCurrent) currentRow = row;
    }
    if (currentRow) {
      const reduceMotion = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
      currentRow.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
    }
  }

  // ---- stage rendering (instant / settled view) -----------------------------------
  /** rot subscript formatting for the anatomy line, e.g. "rot₃". */
  function rotLabel(k) {
    const subs = { 0: "₀", 1: "₁", 2: "₂", 3: "₃", 4: "₄", 5: "₅", 6: "₆", 7: "₇", 8: "₈", 9: "₉" };
    let s = "";
    for (const ch of String(k)) s += subs[ch] || ch;
    return "rot" + s;
  }

  /** The one-line "what this move did": new = reduce( rotᵢ(A) · rotⱼ(B±) ). */
  function anatomyNode(recon) {
    const line = h("div", { class: "move-anatomy" });
    line.appendChild(h("span", { class: "anatomy-label" }, "this move: "));
    line.appendChild(tokensNode(recon.canonical));
    line.appendChild(h("span", { class: "anatomy-op" }, " = reduce( " + rotLabel(recon.iRot) + "("));
    line.appendChild(tokensNode(recon.ra));
    line.appendChild(h("span", { class: "anatomy-op" }, ") · " + rotLabel(recon.jRot) + "("));
    line.appendChild(tokensNode(recon.cBase));
    line.appendChild(h("span", { class: "anatomy-op" }, recon.cInv ? ")⁻¹ )" : ") )"));
    line.appendChild(h("span", { class: "anatomy-note" },
      recon.emittedSlot === recon.leaderSlot ? " — result replaces the first operand" : " — result replaces the second operand"));
    return line;
  }

  function renderStage(step) {
    clear(dom.stage);
    const solution = player.solution;
    const gens = genLetters(solution.nGen);

    const box = h("div", { class: "stage-step" });
    box.appendChild(h("div", { class: "stage-summary" }, step.summary));

    const presentation = h("div", { class: "presentation" });
    presentation.appendChild(h("div", { class: "presentation-line presentation-open" },
      "⟨" + gens.join(", ") + " |"));

    // Render STABLE slots (fixed rows), not the canonical `state` — so unchanged relators
    // hold their position and only the substituted one visibly changes.
    step.slots.forEach(function (slot) {
      const row = h("div", { class: "relator-row" + (slot.isChanged ? " changed" : "") });
      row.appendChild(tokensNode(slot.word));
      if (slot.isChanged && slot.toStr != null) {
        row.appendChild(h("span", { class: "badge badge-new" }, "new"));
        row.appendChild(h("span", { class: "change-note" }, [
          h("span", { class: "chg-from" }, slot.fromStr),
          document.createTextNode(" → "),
          h("span", { class: "chg-to" }, slot.toStr),
        ]));
      }
      presentation.appendChild(row);
    });
    presentation.appendChild(h("div", { class: "presentation-line presentation-close" }, "⟩"));
    box.appendChild(presentation);

    box.appendChild(h("div", { class: "total-len" }, "Total length: " + step.totalLen));

    if (step.change && step.change.recon && step.change.recon.ok) {
      box.appendChild(anatomyNode(step.change.recon));
      box.appendChild(h("div", { class: "raw-move muted" },
        "↻ Replay move (R) shows it slowly · raw tuple: " + (step.change.moveTupleText || "—")));
    } else if (step.change && step.change.moveTupleText) {
      box.appendChild(h("div", { class: "raw-move" }, "raw move: " + step.change.moveTupleText));
    }
    if (step.change && !step.change.wellFormed) {
      box.appendChild(h("div", { class: "raw-move muted" },
        "diff: removed [" + step.change.fromStr.join(", ") + "] added [" + step.change.toStr.join(", ") + "]"));
    }

    if (step.isFinal && solution.finalTrivial) {
      box.appendChild(h("div", { class: "final-flourish" },
        "Trivial presentation reached ⟨" + gens.join(", ") + " | " + gens.join(", ") + "⟩"));
    }

    dom.stage.appendChild(box);
  }

  /** Cancel any running animation, then land on step i. (User navigation entrypoint.) */
  function gotoStep(i) {
    cancelAnim();
    commitStep(i);
  }

  /** Commit step i instantly: scrubber, counter, banner, stage, timeline.
   *  Does NOT cancel animations — animation code calls this to land without
   *  cancelling its caller's token (the autoplay loop reuses one token across steps). */
  function commitStep(i) {
    if (!player.solution) return;
    const n = player.solution.steps.length;
    if (i < 0) i = 0;
    if (i > n - 1) i = n - 1;
    player.stepIndex = i;
    const step = player.solution.steps[i];

    dom.scrubber.value = String(i);
    dom.stepnum.textContent = (i + 1) + " / " + n;
    dom.stabBanner.textContent = player.solution.stabilization.textFull;
    dom.stabBanner.classList.toggle("hidden", !step.isInitial);

    renderStage(step);
    updateTimelineActive(i);
  }

  // ---- the move animation (in place, in the stable rows) --------------------------
  // The substitution supermove replays INSIDE the presentation, in the fixed rows: the
  // changed row (A) and its partner row (B) light up, rotate, glue into one word in row A,
  // then cancel inverse pairs one at a time until the new relator remains. Every other row
  // stays put. Frames come from step.change.recon (verified) + step.change.slots (the stable
  // -row map). Missing either → instant commit. The token cancels between/within phases;
  // whoever cancelled owns the next render, so the stage is never left stale.

  /** letter tiles wrapped in a span that lives inside a stable relator row. */
  function rowTiles(word) {
    const wrap = h("span", { class: "slot-tiles" });
    const tiles = word.map(function (v) { const t = tileNode(v); wrap.appendChild(t); return t; });
    return { wrap: wrap, tiles: tiles };
  }

  async function animateToStep(i, token) {
    const sol = player.solution;
    if (!sol) return;
    const steps = sol.steps;
    if (i < 1 || i > steps.length - 1) { gotoStep(i); return; }
    const step = steps[i];
    const recon = step.change && step.change.recon;
    const slots = step.change && step.change.slots;
    const mult = speedMult();
    if (!recon || !recon.ok || !slots || slots.b < 0 || mult === 0) {
      // Instant fallback — must NOT cancel the caller's token (autoplay reuses it).
      if (anim.token === token) anim.token = null;
      commitStep(i);
      return;
    }

    token = token || newToken();
    player.stepIndex = i;
    dom.scrubber.value = String(i);
    dom.stepnum.textContent = (i + 1) + " / " + steps.length + " ·  animating";
    dom.stabBanner.classList.add("hidden");
    updateTimelineActive(i);

    const gens = genLetters(sol.nGen);
    const parentSlots = steps[i - 1].slots;            // stable rows of the parent
    const A = slots.a, B = slots.b;                    // A changes; B is the partner (stays)
    const emittedIsLeader = recon.emittedSlot === recon.leaderSlot;
    const aRot = emittedIsLeader ? recon.rotA : recon.rotC;  // rotation shown in row A
    const bRot = emittedIsLeader ? recon.rotC : recon.rotA;  // rotation shown in row B
    const aIsFirstHalf = emittedIsLeader;              // in `splice`, does A supply the leading half?
    const dur = function (ms) { return Math.max(60, ms * mult); };

    // -- scaffold: the presentation drawn in its stable rows -------------------------
    clear(dom.stage);
    const box = h("div", { class: "stage-step anim-inplace" });
    box.appendChild(h("div", { class: "stage-summary" }, "Step " + i + " — " + step.summary));
    const pres = h("div", { class: "presentation" });
    pres.appendChild(h("div", { class: "presentation-line presentation-open" }, "⟨" + gens.join(", ") + " |"));
    const rows = parentSlots.map(function (slot, s) {
      const rt = rowTiles(slot.word);
      const row = h("div", {
        class: "relator-row anim-row" + (s === A ? " role-a" : "") + (s === B ? " role-b" : ""),
      }, [rt.wrap]);
      pres.appendChild(row);
      return { row: row, wrap: rt.wrap, tiles: rt.tiles };
    });
    pres.appendChild(h("div", { class: "presentation-line presentation-close" }, "⟩"));
    box.appendChild(pres);
    const narr = h("div", { class: "anim-narration" });
    box.appendChild(narr);
    dom.stage.appendChild(box);

    function setTiles(entry, word, roleCls) {
      clear(entry.wrap);
      entry.tiles = word.map(function (v) {
        const t = tileNode(v);
        if (roleCls) t.classList.add(roleCls);
        entry.wrap.appendChild(t);
        return t;
      });
    }

    // Phase 1 — the two rows in play, and where the result lands.
    narr.textContent = "Combine the two highlighted relators; the result replaces the top one.";
    if (!(await wait(dur(DUR.context), token))) return;

    // Phase 2 — rotate each operand (and invert the partner if the move used its inverse).
    narr.textContent = recon.cInv
      ? "Use the inverse of the partner (reverse it — free), then rotate so the ends meet."
      : "Rotate both relators so their touching ends are inverses.";
    setTiles(rows[A], aRot, "from-a");
    setTiles(rows[B], bRot, "from-b");
    if (!(await wait(dur(DUR.rotate), token))) return;

    // Phase 3 — glue B into A: row A becomes the whole splice; row B is consumed.
    const splice = recon.splice;
    const leadLen = recon.rotA.length;                 // splice[0..leadLen) = leader, rest = partner
    setTiles(rows[A], splice, null);
    rows[A].tiles.forEach(function (t, k) {
      const fromLeader = k < leadLen;                  // colour by SOURCE ROW
      t.classList.add((fromLeader === aIsFirstHalf) ? "from-a" : "from-b");
    });
    rows[A].wrap.classList.add("spliced");
    rows[B].row.classList.add("consumed");             // dim B — its copy moved into A
    const bdA = rows[A].tiles[leadLen - 1], bdB = rows[A].tiles[leadLen];
    if (bdA && bdB) { bdA.classList.add("will-cancel"); bdB.classList.add("will-cancel"); }
    narr.textContent = "Glue them into one word — the touching letters are inverses and cancel.";
    if (!(await wait(dur(DUR.splice), token))) return;
    if (bdA && bdB) { bdA.classList.remove("will-cancel"); bdB.classList.remove("will-cancel"); }

    // Phase 4 — pluck inverse pairs one at a time, in row A.
    let tiles = rows[A].tiles.slice();
    for (const ev of recon.events) {
      let t1, t2;
      if (ev.type === "free") {
        t1 = tiles[ev.pos]; t2 = tiles[ev.pos + 1];
        narr.textContent = "Cancel " + D.letter(ev.letters[0]) + "·" + D.letter(ev.letters[1]) + " …";
      } else {
        t1 = tiles[0]; t2 = tiles[tiles.length - 1];
        narr.textContent = "It's a cyclic word — cancel the two ends " +
          D.letter(ev.letters[0]) + "…" + D.letter(ev.letters[1]) + " too.";
        rows[A].wrap.classList.add("cyclic-mode");
      }
      if (!t1 || !t2) break; // defensive; recon is verified so this shouldn't happen
      t1.classList.add("plucking"); t2.classList.add("plucking");
      if (!(await wait(dur(DUR.pluckMark), token))) return;
      t1.classList.add("gone"); t2.classList.add("gone");
      if (!(await wait(dur(DUR.pluckGap), token))) return;
      t1.remove(); t2.remove();
      if (ev.type === "free") tiles.splice(ev.pos, 2);
      else { tiles.pop(); tiles.shift(); }
      if (!(await wait(dur(ev.type === "free" ? DUR.pluckPause : Math.max(0, DUR.cyclic - DUR.pluckMark - DUR.pluckGap)), token))) return;
    }

    // Phase 5 — the reduced word is the new relator; settle into the canonical child.
    rows[A].wrap.classList.add("result-glow");
    narr.textContent = "That reduced word is the new relator.";
    if (!(await wait(dur(DUR.result), token))) return;
    if (token.cancelled) return;
    if (anim.token === token) anim.token = null;
    commitStep(i);
  }

  /** Next: mid-animation → land it instantly; otherwise animate the next step. */
  function nextStep() {
    if (!player.solution) return;
    if (anim.token && !anim.token.cancelled) {
      gotoStep(player.stepIndex); // finish the running one instantly
      return;
    }
    const n = player.solution.steps.length;
    if (player.stepIndex >= n - 1) return;
    animateToStep(player.stepIndex + 1, newToken());
  }

  /** Replay the current step's move from its parent state (always animated). */
  function replayStep() {
    if (!player.solution || player.stepIndex < 1) return;
    const step = player.solution.steps[player.stepIndex];
    if (!step.change || !step.change.recon || !step.change.recon.ok) return;
    if (speedMult() === 0) dom.speed.value = "1"; // Replay explicitly asks for motion
    animateToStep(player.stepIndex, newToken());
  }

  // ---- transport: play/pause ----------------------------------------------------
  function setPlayingUi(isPlaying) {
    player.playing = isPlaying;
    dom.play.textContent = isPlaying ? "⏸" : "▶";
    dom.play.setAttribute("aria-label", isPlaying ? "Pause" : "Play");
  }

  function stopPlaying() {
    if (player.playing) setPlayingUi(false);
  }

  async function playLoop() {
    const token = newToken();
    setPlayingUi(true);
    while (player.playing && !token.cancelled && player.solution) {
      const n = player.solution.steps.length;
      if (player.stepIndex >= n - 1) break;
      const mult = speedMult();
      if (mult === 0) {
        gotoStep(player.stepIndex + 1);
        if (!(await wait(900, token))) break;
      } else {
        await animateToStep(player.stepIndex + 1, token);
        if (token.cancelled) break;
        if (!(await wait(Math.max(120, DUR.betweenSteps * mult), token))) break;
      }
    }
    if (!token.cancelled) setPlayingUi(false);
  }

  function togglePlay() {
    if (!player.solution) return;
    if (player.playing) { stopPlaying(); cancelAnim(); gotoStep(player.stepIndex); return; }
    if (player.stepIndex >= player.solution.steps.length - 1) gotoStep(0);
    playLoop();
  }

  function closePlayer() {
    stopPlaying();
    cancelAnim();
    dom.player.classList.add("hidden");
    player.entry = null;
    player.solution = null;
    player.arm = null;
    player.stepIndex = 0;
  }

  // ---- public API ---------------------------------------------------------------
  function init() {
    if (initialized) return;
    cacheDom();
    wireControls();
    wirePlayerControls();
    wireKeyboard();
    initialized = true;
  }

  function render(ds) {
    if (!initialized) init();
    dataset = ds;

    filters.search = "";
    filters.solved = "all";
    filters.subset = "all";
    filters.arm = "all";
    filters.layout = "grid";
    dom.search.value = "";
    for (const s of dom.filterButtons.querySelectorAll(".seg")) {
      s.classList.toggle("active", s.getAttribute("data-filter") === "all");
    }
    for (const s of dom.viewToggle.querySelectorAll(".seg")) {
      s.classList.toggle("active", s.getAttribute("data-layout") === "grid");
    }

    ensureGridData();
    renderSelects();
    renderGrid();
    closePlayer();
  }

  global.ACXViewer = { init: init, render: render };
})(typeof window !== "undefined" ? window : globalThis);
