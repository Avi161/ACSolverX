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
  const ARM_ORDER = ["r1", "r2", "x", "y"];
  const REPS_DATASET = "ms_reps_unsolved";
  // Arms hidden from the z=w views: baseline is the 2-generator control (own tab) — routing it
  // through buildSteps would mis-decode generator y as the stabilizer z.
  const HIDDEN_ARMS = new Set(["baseline"]);
  // Human-readable dataset names for selects (option VALUES stay the raw ids — filters key on them).
  const datasetLabel = (ds) => D.datasetLabel(ds);

  // Base durations (ms) at Normal speed; the speed select multiplies these.
  // Rotation is PER-SLOT (rotateStep + rotateStepGap per tick, whole phase capped at
  // rotateCap) so a k-slot rotation reads as k countable steps, never one fast glide.
  const DUR = {
    context: 900, invert: 950,
    rotateStep: 240, rotateStepGap: 90, rotateCap: 3000, rotateSkip: 350,
    splice: 1100,
    pluckMark: 320, pluckGap: 220, pluckPause: 240,
    cyclic: 900, result: 900, betweenSteps: 800, phaseGap: 450,
  };
  const GAP = 4;                                  // px gap between tiles (matches .slot-tiles/.rot-strip CSS)
  const RING_W = 84;                              // ring inset width + gap, reserved per row
  const EASE = "cubic-bezier(0.22, 1, 0.36, 1)";  // decisive start, soft landing
  const SVG_NS = "http://www.w3.org/2000/svg";

  // ---- module state ---------------------------------------------------------
  let dom = null;
  let initialized = false;
  let dataset = null;
  let gridData = null;         // reps_grid.json: the (n,w) map of the whole MS(1190) family
  let gridFetchStarted = false;

  const filters = {
    search: "", solved: "all", dataset: "all", subset: "all", arm: "all", layout: "cards",
    sort: "default", group: false,
  };
  const CARD_BATCH = 60; // cards appended per IntersectionObserver tick (incremental render)

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
    for (const a of entry.arms.keys()) {
      if (order.indexOf(a) === -1 && !HIDDEN_ARMS.has(a)) extra.push(a);
    }
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
    // hidden arms (the 2-gen baseline) don't count as solved in the z=w views
    for (const it of entry.arms.values()) if (it.solved && !HIDDEN_ARMS.has(it.arm)) return true;
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
      sortSelect: document.getElementById("sort-select"),
      groupToggle: document.getElementById("group-toggle"),
      clearFilters: document.getElementById("clear-filters"),
      showingCount: document.getElementById("showing-count"),
      grid: document.getElementById("presentations-grid"),
      nwGrid: document.getElementById("nw-grid"),
      gridEmpty: document.getElementById("grid-empty"),

      overlay: document.getElementById("player-overlay"),
      backdrop: document.getElementById("player-backdrop"),
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
    // Debounced: every keystroke used to rebuild the full card list synchronously.
    let searchTimer = null;
    dom.search.addEventListener("input", function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () {
        filters.search = dom.search.value.trim();
        renderGrid();
      }, 150);
    });

    dom.sortSelect.addEventListener("change", function () {
      filters.sort = dom.sortSelect.value;
      renderGrid();
    });

    dom.groupToggle.addEventListener("change", function () {
      filters.group = dom.groupToggle.checked;
      renderGrid();
    });

    // Full reset — render() puts every filter, the sort, and the grouping back to
    // their defaults and re-renders (same code path as a fresh dataset load).
    dom.clearFilters.addEventListener("click", function () { render(dataset); });

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
      // an open player follows the filter — picking "z = x" switches the shown run too
      if (player.entry && filters.arm !== "all" && player.entry.arms.has(filters.arm) &&
          player.arm !== filters.arm) {
        selectArm(filters.arm);
      }
    });

    function activateCard(card) {
      // A rep-covered hard card opens its class representative's player — that run is
      // the search that covers it; the card itself has no direct runs to show.
      const repIdx = card.getAttribute("data-rep-idx");
      if (repIdx != null) openPlayer(REPS_DATASET, repIdx);
      else openPlayer(card.getAttribute("data-dataset"), card.getAttribute("data-idx"));
    }
    dom.grid.addEventListener("click", function (e) {
      // a rollup card's "members" chevron expands in place — it must not open the player
      const chevron = e.target.closest(".rollup-chevron");
      if (chevron && dom.grid.contains(chevron)) {
        e.stopPropagation();
        toggleRollupMembers(chevron);
        return;
      }
      const card = e.target.closest(".presentation-card");
      if (!card || !dom.grid.contains(card) || card.classList.contains("card-unattempted")) return;
      activateCard(card);
    });
    // cards carry role="button" — give keyboard users the activation a real button would have
    dom.grid.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar") return;
      const chevron = e.target.closest(".rollup-chevron");
      if (chevron && dom.grid.contains(chevron)) {
        e.preventDefault();
        e.stopPropagation();
        toggleRollupMembers(chevron);
        return;
      }
      const card = e.target.closest(".presentation-card");
      if (!card || !dom.grid.contains(card) || card.classList.contains("card-unattempted")) return;
      e.preventDefault();
      activateCard(card);
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
    dom.nwGrid.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar") return;
      const cell = e.target.closest(".nw-cell");
      if (!cell || !dom.nwGrid.contains(cell) || cell.classList.contains("nw-cell-dead")) return;
      e.preventDefault();
      openPlayer(cell.getAttribute("data-dataset"), cell.getAttribute("data-idx"));
    });
  }

  function wirePlayerControls() {
    dom.playerClose.addEventListener("click", closePlayer);
    dom.backdrop.addEventListener("click", closePlayer);

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
    // Enter/Space on a focused row = click. stopPropagation keeps the document-level
    // Space-toggles-play shortcut from ALSO firing on the same keystroke.
    dom.timeline.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar") return;
      const row = e.target.closest(".timeline-row");
      if (!row || !dom.timeline.contains(row)) return;
      e.preventDefault();
      e.stopPropagation();
      stopPlaying();
      gotoStep(Number(row.getAttribute("data-index")));
    });
  }

  function wireKeyboard() {
    document.addEventListener("keydown", function (e) {
      if (dom.overlay.classList.contains("hidden")) return;
      if (dom.viewSolutions.classList.contains("hidden")) return;
      const active = document.activeElement;
      const tag = active && active.tagName;

      // Focus trap: while the modal is open, Tab cycles inside it (before the input
      // guard below — the scrubber/speed controls are inputs and must stay trapped).
      if (e.key === "Tab") {
        const focusables = dom.overlay.querySelectorAll(
          "button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex='-1'])");
        if (!focusables.length) return;
        const first = focusables[0], last = focusables[focusables.length - 1];
        if (!dom.overlay.contains(active)) { e.preventDefault(); first.focus(); }
        else if (e.shiftKey && active === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && active === last) { e.preventDefault(); first.focus(); }
        return;
      }

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

  // ---- stat cards (NON-redundant: presentations, never presentation×arm rows) -----
  function renderStats() {
    clear(dom.stats);
    // excludeArms: "All z-words" must aggregate the z-word arms ONLY — a baseline-only
    // solve (hidden from this view) must not read as solved here (620, not 634, on the 640).
    const g = D.groupStats(dataset, {
      dataset: filters.dataset, arm: filters.arm, subset: filters.subset,
      excludeArms: HIDDEN_ARMS,
    });
    const scope = [];
    if (filters.dataset !== "all") scope.push(datasetLabel(filters.dataset));
    if (filters.subset !== "all") scope.push(D.subsetLabel(filters.subset));
    scope.push(filters.arm === "all" ? "all z-words" : "z = " + D.armSymbol(filters.arm));
    const num = function (n) { return n.toLocaleString(); };

    const cards = [
      { label: "Presentations", value: num(g.total), sub: scope.join(" · ") },
      { label: "Solved", value: num(g.solved), cls: "stat-ok", sub: g.attempted ? Math.round(100 * g.solved / g.attempted) + "% of searched" : "" },
      { label: "Unsolved (searched)", value: num(g.unsolvedSearched), cls: "stat-err", sub: "budget exhausted" },
      g.coveredViaReps > 0
        ? {
          label: "Covered via reps", value: num(g.coveredViaReps), cls: "stat-warn",
          sub: "searched via class rep · " +
            D.groupStats(dataset, { dataset: REPS_DATASET }).solved + " solved",
        }
        : null,
      { label: "Not attempted", value: num(g.notAttempted), cls: "stat-muted", sub: g.notAttempted ? "no direct run or rep link" : "" },
      { label: "Avg. path length", value: g.avgPathLen == null ? "—" : g.avgPathLen.toFixed(2), sub: "best path per presentation" },
    ].filter(Boolean);
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
      dom.datasetSelect.appendChild(h("option", { value: dsName }, datasetLabel(dsName)));
    }
    // Default to MS(1190) so the headline numbers read over the full 1190 out of the box.
    filters.dataset = dataset.datasets.indexOf("1190MS") !== -1 ? "1190MS" : "all";
    dom.datasetSelect.value = filters.dataset;

    rebuildSubsetOptions();

    clear(dom.armFilter);
    dom.armFilter.appendChild(h("option", { value: "all" }, "All z-words"));
    for (const arm of dataset.arms) {
      if (HIDDEN_ARMS.has(arm)) continue; // baseline lives in its own tab
      dom.armFilter.appendChild(h("option", { value: arm }, "z = " + D.armSymbol(arm)));
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
        // Match by idx, or by unsolved-class name — "13_1" finds the rep AND every hard
        // MS(1190) presentation in that class.
        const strs = [String(entry.idx)];
        if (entry.reg && entry.reg.class_name) strs.push(String(entry.reg.class_name).toLowerCase());
        if (entry.reg && entry.reg.name) strs.push(String(entry.reg.name).toLowerCase());
        const hit = terms.some(function (t) {
          const tl = t.toLowerCase();
          return strs.some(function (s) { return s.indexOf(tl) !== -1; });
        });
        if (!hit) return false;
      }
    }

    if (filters.solved !== "all" && entryStatus(entry, filters.arm) !== filters.solved) return false;
    return true;
  }

  /** A presentation with no direct run whose annotated class representative WAS searched. */
  function viaRep(entry) {
    return entry.arms.size === 0 && entry.reg && entry.reg.rep_idx != null &&
      dataset && !!dataset.byIdx.get(REPS_DATASET + "|" + entry.reg.rep_idx);
  }

  function buildCard(entry) {
    const status = entryStatus(entry, filters.arm);
    const arms = armOrderFor(entry);
    const attempted = entry.arms.size > 0;
    const covered = viaRep(entry);

    const pillText = status === "solved" ? "Solved" : status === "unsolved" ? "Unsolved"
      : covered ? "Searched via rep" : "Not attempted";
    const pillCls = covered && status === "unattempted" ? "viarep" : status;
    const head = h("div", { class: "card-head" }, [
      h("span", { class: "card-idx" }, "#" + entry.idx),
      h("span", { class: "pill pill-" + pillCls }, pillText),
    ]);

    // Provenance badge — the "is this one of the hard 550?" answer, on every card;
    // rep-covered cards also carry their unsolved-class name.
    const className = entry.reg && (entry.reg.class_name || entry.reg.name);
    const badges = h("div", { class: "card-badges" }, [
      h("span", { class: "card-dataset" }, entry.dataset),
      entry.subset ? h("span", { class: "badge-subset badge-" + entry.subset }, D.subsetLabel(entry.subset)) : null,
      className ? h("span", { class: "card-class-chip", title: "unsolved AC-class " + className }, "class " + className) : null,
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
        const won = !!(it && it.solved);
        // glyph + color: solved/unsolved must survive color-blindness and grayscale
        armsNode.appendChild(h("span", {
          class: "arm-chip " + (won ? "arm-chip-ok" : "arm-chip-bad"),
          title: "z = " + D.armSymbol(a) + (won ? " · solved" : " · unsolved"),
        }, (won ? "✓" : "✕") + D.armSymbol(a)));
      }
    } else if (covered) {
      // outcome computed from the rep's actual runs, never asserted
      const repEntry = dataset.byIdx.get(REPS_DATASET + "|" + entry.reg.rep_idx);
      let repT = 0, repS = 0;
      if (repEntry) for (const it of repEntry.arms.values()) { repT++; if (it.solved) repS++; }
      armsNode = h("div", { class: "card-arms-hint" },
        "Searched via class representative " + (className || "#" + entry.reg.rep_idx) + " — " +
        (repS ? repS + "/" + repT + " z-words solved it." :
          "unsolved under all " + (repT || 4) + " z-words (budget exhausted).") +
        " Click to open the representative.");
    } else {
      armsNode = h("div", { class: "card-arms-hint muted" },
        "Not searched yet — needs a bigger budget run.");
    }

    const clickable = attempted || covered;
    const opts = {
      class: "card presentation-card" + (clickable ? "" : " card-unattempted"),
      "data-dataset": entry.dataset,
      "data-idx": String(entry.idx),
    };
    // A covered card opens its class REPRESENTATIVE's player (the rep is what was searched).
    if (covered) opts["data-rep-idx"] = String(entry.reg.rep_idx);
    if (clickable) { opts.role = "button"; opts.tabindex = "0"; }
    return h("div", opts, [head, badges, h("pre", { class: "card-preview" }, previewText), armsNode]);
  }

  // ---- class rollup card (grouped mode: one card per unsolved class) ---------------
  /** item = { rollup: rep_idx, members: [hard 1190MS entries] } */
  function buildClassRollupCard(item) {
    const repEntry = dataset.byIdx.get(REPS_DATASET + "|" + item.rollup);
    const reg = repEntry && repEntry.reg;
    const firstReg = item.members[0] && item.members[0].reg;
    const name = (reg && reg.name) || (firstReg && firstReg.class_name) || ("#" + item.rollup);
    const classSize = reg && Array.isArray(reg.nw_cells) ? reg.nw_cells.length : item.members.length;

    let armsTotal = 0, armsSolved = 0;
    if (repEntry) for (const it of repEntry.arms.values()) { armsTotal++; if (it.solved) armsSolved++; }

    const head = h("div", { class: "card-head" }, [
      h("span", { class: "card-idx" }, "class " + name),
      h("span", { class: "pill pill-" + (armsSolved ? "solved" : "viarep") },
        armsSolved ? "Rep solved" : "Searched via rep"),
    ]);
    const badges = h("div", { class: "card-badges" }, [
      h("span", { class: "card-dataset" }, "1190MS"),
      h("span", { class: "badge-subset badge-hard" }, D.subsetLabel("hard")),
      h("span", { class: "card-class-chip" },
        item.members.length + (item.members.length === classSize ? "" : " of " + classSize) + " members"),
    ]);

    let previewText = "";
    if (reg && Array.isArray(reg.relators)) {
      const gens = genLetters(reg.n_gen || 2);
      previewText = "⟨" + gens.join(",") + " | " + reg.relators.map(D.wordToStr).join(", ") + "⟩";
    }

    const hint = h("div", { class: "card-arms-hint" },
      "One unsolved class standing for " + item.members.length + " hard presentation" +
      (item.members.length === 1 ? "" : "s") + ". Its representative was searched under z ∈ {r₁, r₂, x, y}" +
      (armsSolved ? " — " + armsSolved + "/" + armsTotal + " solved." :
        " — 0/" + (armsTotal || 4) + " solved at 500k nodes.") + " Click to open the representative.");

    const chevron = h("button", {
      class: "rollup-chevron", type: "button", "aria-expanded": "false",
      title: "List the hard MS(1190) presentations in this class",
    }, "▸ show members");
    const membersBox = h("div", { class: "rollup-members hidden" });

    const card = h("div", {
      class: "card presentation-card rollup-card",
      role: "button", tabindex: "0",
      "data-rep-idx": String(item.rollup),
      "data-dataset": "1190MS", "data-idx": String(item.members[0].idx),
    }, [head, badges, previewText ? h("pre", { class: "card-preview" }, previewText) : null,
      hint, chevron, membersBox]);
    // lazy member chips: built on first expand (toggleRollupMembers reads this)
    card._rollupMembers = item.members;
    return card;
  }

  function toggleRollupMembers(chevron) {
    const card = chevron.closest(".rollup-card");
    if (!card) return;
    const box = card.querySelector(".rollup-members");
    if (!box) return;
    const open = box.classList.contains("hidden");
    if (open && !box.childNodes.length && Array.isArray(card._rollupMembers)) {
      for (const m of card._rollupMembers) {
        box.appendChild(h("span", {
          class: "rollup-member-chip",
          title: "MS(1190) #" + m.idx + " — covered by this class representative",
        }, "#" + m.idx));
      }
    }
    box.classList.toggle("hidden", !open);
    chevron.setAttribute("aria-expanded", String(open));
    chevron.textContent = (open ? "▾ hide members" : "▸ show members");
  }

  function gridAvailable() {
    return !!gridData && !!dataset && dataset.datasets.indexOf(gridData.linked_dataset || "1190MS") !== -1;
  }

  function ensureGridData() {
    if (gridFetchStarted) return;
    gridFetchStarted = true;
    if (window.ACXLoad && ACXLoad.isFileProtocol()) {
      var bundle = ACXLoad.getCachedOfflineBundle();
      if (bundle && bundle.repsGrid) {
        gridData = bundle.repsGrid;
        if (dataset) renderGrid();
      }
      return;
    }
    fetch("sample-data/reps_grid.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (g) { gridData = g; if (dataset) renderGrid(); })
      .catch(function () { gridData = null; });
  }

  function renderGrid() {
    renderStats(); // stats always mirror the current selection
    const canGrid = gridAvailable();
    // .invisible (not .hidden) reserves the toggle's space, so the late reps_grid.json
    // arrival doesn't shift the controls row (the old load-time layout flash).
    dom.viewToggle.classList.toggle("invisible", !canGrid);
    const useGrid = canGrid && filters.layout === "grid";
    dom.nwGrid.classList.toggle("hidden", !useGrid);
    dom.grid.classList.toggle("hidden", useGrid);
    if (useGrid) {
      dom.gridEmpty.classList.add("hidden");
      if (dom.showingCount) dom.showingCount.textContent = "";
      renderNwGrid();
    } else {
      renderCards();
    }
  }

  // ---- sorting -----------------------------------------------------------------
  /** Best (smallest) solved path length over the arms in the current arm scope. */
  function bestPathLen(entry) {
    let best = null;
    for (const it of entry.arms.values()) {
      if (HIDDEN_ARMS.has(it.arm)) continue;
      if (filters.arm !== "all" && it.arm !== filters.arm) continue;
      if (!it.solved) continue;
      const l = D.itemPathLen(it);
      if (l != null && (best == null || l < best)) best = l;
    }
    return best;
  }
  /** Cheapest solve (nodes explored) over the arms in the current arm scope. */
  function bestNodes(entry) {
    let best = null;
    for (const it of entry.arms.values()) {
      if (HIDDEN_ARMS.has(it.arm)) continue;
      if (filters.arm !== "all" && it.arm !== filters.arm) continue;
      if (!it.solved || !it.calib || it.calib.nodes_explored == null) continue;
      if (best == null || it.calib.nodes_explored < best) best = it.calib.nodes_explored;
    }
    return best;
  }
  function statusRank(entry) {
    const s = entryStatus(entry, filters.arm);
    if (s === "solved") return 0;
    if (s === "unsolved") return 1;
    return viaRep(entry) ? 2 : 3;
  }
  /** Sort value for a list item (entry or class rollup). Missing values sort last. */
  function sortValue(item) {
    if (item.rollup != null) return filters.sort === "status" ? 2 : Infinity;
    switch (filters.sort) {
      case "pathlen-asc":
      case "pathlen-desc": { const v = bestPathLen(item); return v == null ? Infinity : v; }
      case "nodes-asc": { const v = bestNodes(item); return v == null ? Infinity : v; }
      case "status": return statusRank(item);
      default: return 0;
    }
  }
  function applySort(list) {
    if (filters.sort === "default") return list;
    const desc = filters.sort === "pathlen-desc";
    return list
      .map(function (e, i) { return { e: e, i: i, v: sortValue(e) }; })
      .sort(function (A, B) {
        const aMiss = !isFinite(A.v), bMiss = !isFinite(B.v);
        if (aMiss !== bMiss) return aMiss ? 1 : -1; // no-value items always sink
        if (A.v !== B.v) return desc ? B.v - A.v : A.v - B.v;
        return A.i - B.i; // stable
      })
      .map(function (x) { return x.e; });
  }

  // ---- incremental card rendering (batched via IntersectionObserver) --------------
  const gridState = { list: [], cursor: 0, observer: null, sentinel: null };

  function appendCardBatch() {
    const frag = document.createDocumentFragment();
    const end = Math.min(gridState.cursor + CARD_BATCH, gridState.list.length);
    for (let i = gridState.cursor; i < end; i++) {
      const item = gridState.list[i];
      frag.appendChild(item.rollup != null ? buildClassRollupCard(item) : buildCard(item));
    }
    gridState.cursor = end;
    dom.grid.appendChild(frag);
    // keep the sentinel at the tail while there is more to render
    if (!gridState.sentinel) {
      gridState.sentinel = h("div", { id: "grid-sentinel", "aria-hidden": "true" });
      gridState.observer = new IntersectionObserver(function (ents) {
        for (const en of ents) {
          if (en.isIntersecting && gridState.cursor < gridState.list.length) appendCardBatch();
        }
      }, { rootMargin: "800px" });
    }
    if (gridState.cursor < gridState.list.length) {
      dom.grid.appendChild(gridState.sentinel);
      gridState.observer.observe(gridState.sentinel);
    } else {
      gridState.observer.unobserve(gridState.sentinel);
      if (gridState.sentinel.parentNode) gridState.sentinel.parentNode.removeChild(gridState.sentinel);
    }
  }

  function renderCards() {
    clear(dom.grid);
    const all = Array.from(dataset.byIdx.values());
    all.sort(function (a, b) {
      return a.dataset < b.dataset ? -1 : a.dataset > b.dataset ? 1 : a.idx - b.idx;
    });

    // Build the display list: matching entries, with the hard rep-covered ones
    // optionally collapsed into one rollup item per unsolved class (261 max).
    const list = [];
    const rollups = new Map(); // rep_idx -> rollup item
    let matched = 0, groupedMembers = 0;
    for (const entry of all) {
      if (!matchesFilters(entry)) continue;
      matched++;
      if (filters.group && entry.dataset === "1190MS" && viaRep(entry)) {
        let r = rollups.get(entry.reg.rep_idx);
        if (!r) {
          r = { rollup: entry.reg.rep_idx, members: [] };
          rollups.set(entry.reg.rep_idx, r);
          list.push(r); // positioned where its first member appeared
        }
        r.members.push(entry);
        groupedMembers++;
        continue;
      }
      list.push(entry);
    }

    // "of M" = the dataset/subset scope, before search/status/arm narrowing.
    let scopeTotal = 0;
    for (const entry of dataset.byIdx.values()) {
      if (filters.dataset !== "all" && entry.dataset !== filters.dataset) continue;
      if (filters.subset !== "all" && entry.subset !== filters.subset) continue;
      scopeTotal++;
    }
    if (dom.showingCount) {
      let txt = matched === scopeTotal
        ? "Showing all " + scopeTotal.toLocaleString() + " presentations"
        : "Showing " + matched.toLocaleString() + " of " + scopeTotal.toLocaleString() + " presentations";
      if (groupedMembers) txt += " · " + groupedMembers + " hard grouped into " + rollups.size + " classes";
      dom.showingCount.textContent = txt;
    }

    gridState.list = applySort(list);
    gridState.cursor = 0;
    appendCardBatch();
    dom.gridEmpty.classList.toggle("hidden", list.length !== 0);
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
    // the hard presentations ARE the non-trivial cells (shown as their class rep)
    if (filters.subset === "hard" && cell.status === "trivial") return false;
    if (filters.solved === "solved" && cell.status !== "trivial") return false;
    if (filters.solved === "unsolved" && cell.status === "trivial") return false;
    if (filters.solved === "unattempted") return false;
    if (filters.search) {
      const terms = filters.search.split(/[,\s]+/).filter(Boolean);
      // Non-trivial cells also match their class label ("13_1") so class search works here too.
      const strs = cell.status === "trivial"
        ? [String(cell.ms_idx)]
        : [String(cell.rep_idx), String(cell.status).toLowerCase()];
      if (terms.length && !terms.some(function (t) {
        const tl = t.toLowerCase();
        return strs.some(function (s) { return s.indexOf(tl) !== -1; });
      })) return false;
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
      h("span", { class: "nw-swatch nw-rep" }), h("span", { class: "nw-legend-t" },
        "unsolved class (cell shows the rep; the hard presentations live in these cells) — click any cell to open the player"),
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
        if (clickable) {
          td.setAttribute("data-dataset", targetDs);
          td.setAttribute("data-idx", String(targetIdx));
          td.setAttribute("tabindex", "0");
          td.setAttribute("role", "button");
          td.setAttribute("aria-label", td.getAttribute("title"));
        }
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
    // The active Change-of-variables filter wins: opening a card while "z = x" is
    // selected must open the z = x run, not the first solved arm in ARM_ORDER.
    if (filters.arm !== "all" && entry.arms.has(filters.arm)) return filters.arm;
    const order = armOrderFor(entry);
    for (const a of order) { const it = entry.arms.get(a); if (it && it.path) return a; }
    return order[0] || null;
  }

  // ---- deep links: #/solutions?open=<dataset>:<idx>&arm=<arm> --------------------
  // replaceState (not location.hash=) so no hashchange fires and the router never loops.
  function syncHashOpen() {
    if (!player.entry) return;
    const h = "#/solutions?open=" + encodeURIComponent(player.entry.dataset) + ":" + player.entry.idx +
      (player.arm ? "&arm=" + encodeURIComponent(player.arm) : "");
    try { history.replaceState(null, "", h); } catch (e) { /* sandboxed iframe etc. */ }
  }
  function syncHashClosed() {
    // strip only our own ?open=… query — never clobber a navigation to another view
    if (/^#\/?solutions\?/.test(location.hash || "")) {
      try { history.replaceState(null, "", "#/solutions"); } catch (e) { /* ignore */ }
    }
  }

  /** Router entry: reopen a deep-linked presentation (called by app.js after render). */
  function openFromHash(datasetName, idxStr, arm) {
    if (!dataset) return;
    const entry = dataset.byIdx.get(datasetName + "|" + idxStr);
    if (!entry || entry.arms.size === 0) return;
    openPlayer(datasetName, idxStr);
    if (arm && entry.arms.has(arm) && player.arm !== arm) selectArm(arm);
  }

  function openPlayer(datasetName, idxStr) {
    const key = datasetName + "|" + idxStr;
    const entry = dataset.byIdx.get(key);
    if (!entry || entry.arms.size === 0) return;

    player.opener = document.activeElement; // restore focus here on close
    player.entry = entry;
    buildArmSelector(entry);
    const repName = entry.dataset === REPS_DATASET && entry.reg && entry.reg.name;
    dom.playerTitle.textContent = repName
      ? "#" + entry.idx + " · class " + repName + " · representative"
      : "#" + entry.idx + " · " + datasetLabel(entry.dataset);
    dom.overlay.classList.remove("hidden");
    document.body.classList.add("modal-open");
    dom.overlay.scrollTop = 0;

    const arm = defaultArmFor(entry);
    selectArm(arm);
    dom.playerClose.focus();
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
      if (c.nodes_per_sec != null) parts.push(c.nodes_per_sec.toLocaleString() + " nodes/s");
      if (c.revert_hits != null) parts.push(c.revert_hits.toLocaleString() + " revert hits");
    } else if (item && item.path) {
      parts.push("solved");
      if (item.path.path_len != null) parts.push("path length " + item.path.path_len);
    }
    dom.playerMeta.appendChild(h("span", null, " " + parts.join(" · ")));
    // A class representative stands for every hard MS(1190) presentation in its class.
    if (entry && entry.dataset === REPS_DATASET && entry.reg && Array.isArray(entry.reg.nw_cells)) {
      dom.playerMeta.appendChild(h("span", { class: "muted" },
        " · represents " + entry.reg.nw_cells.length + " hard MS(1190) presentation" +
        (entry.reg.nw_cells.length === 1 ? "" : "s") + " (one per (n, w) cell of class " +
        (entry.reg.name || "?") + ")"));
    }
  }

  function selectArm(arm) {
    if (!player.entry || !arm) return;
    stopPlaying();
    cancelAnim();
    player.arm = arm;
    const item = player.entry.arms.get(arm);
    highlightArmButton(arm);
    renderPlayerMeta(item, arm);
    syncHashOpen();

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
      const row = h("li", {
        class: "timeline-row" + (step.isFinal ? " final" : ""),
        "data-index": String(step.index),
        // keyboard access: rows act as buttons (Enter/Space handled in wirePlayerControls)
        tabindex: "0", role: "button",
        "aria-label": "Step " + step.index + ": " + step.summary + " — total length " + step.totalLen,
      }, [
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
      if (isCurrent) row.setAttribute("aria-current", "step");
      else row.removeAttribute("aria-current");
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

  /** The one-line "what this move did": new = reduce( rotᵢ(A) · rotⱼ(B±) ).
   *  Operands are wrapped in chips tinted like their rows (A = the replaced row, B = partner),
   *  so the equation and the animation share one visual vocabulary. */
  function anatomyNode(recon) {
    const emittedIsLeader = recon.emittedSlot === recon.leaderSlot;
    const leaderCls = emittedIsLeader ? "opnd-a" : "opnd-b";
    const partnerCls = emittedIsLeader ? "opnd-b" : "opnd-a";
    const line = h("div", { class: "move-anatomy" });
    line.appendChild(h("span", { class: "anatomy-label" }, "this move: "));
    line.appendChild(tokensNode(recon.canonical));
    line.appendChild(h("span", { class: "anatomy-op" }, " = reduce( "));
    line.appendChild(h("span", { class: "anatomy-opnd " + leaderCls }, [
      h("span", { class: "anatomy-op" }, rotLabel(recon.iRot) + "("),
      tokensNode(recon.ra),
      h("span", { class: "anatomy-op" }, ")"),
    ]));
    line.appendChild(h("span", { class: "anatomy-op" }, " · "));
    line.appendChild(h("span", { class: "anatomy-opnd " + partnerCls }, [
      h("span", { class: "anatomy-op" }, rotLabel(recon.jRot) + "("),
      tokensNode(recon.cBase),
      h("span", { class: "anatomy-op" }, recon.cInv ? ")⁻¹" : ")"),
    ]));
    line.appendChild(h("span", { class: "anatomy-op" }, " )"));
    line.appendChild(h("span", { class: "anatomy-note" },
      " — the result replaces the A-tinted operand's row"));
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
        "↻ Replay move (R) shows it slowly · the solver recorded this move as (slot, rotation of A, " +
        "rotation of B, B-inverted): " + (step.change.moveTupleText || "—")));
    } else if (step.change && step.change.moveTupleText) {
      box.appendChild(h("div", { class: "raw-move" },
        "the solver recorded this move as (slot, rotation of A, rotation of B, B-inverted): " +
        step.change.moveTupleText));
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

  // ---- the move animation v2 (rings + tiles hybrid, in the stable rows) -----------
  // The substitution supermove replays INSIDE the presentation, in the fixed rows. The two
  // operand rows carry a RING INSET — the relator drawn as the cyclic word it really is —
  // and the phases make each sub-operation visible:
  //   Roles   → the two rows light up (A gets replaced, B is only read)
  //   Invert  → (if used) the partner's tiles mirror + case-flip in place
  //   Rotate  → tiles slide with wrap-around; on the ring, the CUT marker rotates while the
  //             letters stay put (rotation = choosing where to cut the ring open)
  //   Splice  → partner tiles fly into row A; a persistent seam marks where the halves met
  //   Cancel  → inverse pairs pluck one at a time, zipping shut at the seam; cyclic
  //             cancellations draw a wrap-around arc between the word's two ends
  //   Settle  → the reduced word glows and lands as the new relator
  // Frames come from step.change.recon (verified) + step.change.slots (the stable-row map).
  // Missing either → instant commit. The token cancels between/within phases; whoever
  // cancelled owns the next render, so the stage is never left stale.

  /** letter tiles wrapped in a span that lives inside a stable relator row. */
  function rowTiles(word) {
    const wrap = h("span", { class: "slot-tiles" });
    const tiles = word.map(function (v) { const t = tileNode(v); wrap.appendChild(t); return t; });
    return { wrap: wrap, tiles: tiles };
  }

  /** Replace a row's tiles with `word` (optionally tagged with a from-a/from-b role class). */
  function setTiles(entry, word, roleCls) {
    clear(entry.wrap);
    entry.tiles = word.map(function (v) {
      const t = tileNode(v);
      if (roleCls) t.classList.add(roleCls);
      entry.wrap.appendChild(t);
      return t;
    });
  }

  function genKey(v) {
    const a = Math.abs(v);
    return a === 1 ? "x" : a === 2 ? "y" : a === 3 ? "z" : "g";
  }

  /** One-clause meaning per phase — surfaces as the chip's tooltip (pedagogy at point of use). */
  const PHASE_GLOSS = {
    Roles: "Pick the two operand relators: row A gets replaced, row B is the partner (only read).",
    Invert: "The move uses B's INVERSE: read it backwards and case-flip every letter.",
    Rotate: "Slide each ring's cut marker — relators are cyclic, rotating never changes the word.",
    Splice: "Glue the rotated words: B's tiles fly into row A, the seam marks where they met.",
    Cancel: "Adjacent inverse pairs vanish one at a time, zipping shut at the seam.",
    Settle: "The reduced word takes row A; the presentation settles into its canonical form.",
  };

  /** Phase chips strip — the pipeline map ("where am I in this move?"). */
  function phaseChipsNode(names) {
    const wrap = h("div", { class: "phase-chips", role: "list", "aria-label": "Move animation phases" });
    for (const n of names) {
      wrap.appendChild(h("span", {
        class: "chip", "data-phase": n, role: "listitem", title: PHASE_GLOSS[n] || n,
      }, n));
    }
    return wrap;
  }
  function setPhase(chipsEl, name) {
    let seen = false;
    for (const c of chipsEl.querySelectorAll(".chip")) {
      const isCur = c.getAttribute("data-phase") === name;
      if (isCur) seen = true;
      c.classList.toggle("chip-active", isCur);
      c.classList.toggle("chip-done", !seen && !isCur);
    }
  }

  /** Tile size so the widest word of this step (the splice) fits on one line. */
  function computeTileSize(maxLen) {
    const stageW = dom.stage.clientWidth || 800;
    const avail = Math.max(160, stageW - RING_W - 90);
    return Math.max(12, Math.min(30, Math.floor(avail / Math.max(1, maxLen)) - GAP));
  }

  /** The relator as a RING: letters fixed on a circle, a cut marker in the gap before
   *  letter 0. Rotation never moves the letters — it rotates the CUT (the word is cyclic;
   *  rotating = choosing where to cut it open to write the linear row). */
  function ringSvgNode(word) {
    const n = word.length;
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("class", "ring-svg");
    svg.setAttribute("aria-hidden", "true");
    const track = document.createElementNS(SVG_NS, "circle");
    track.setAttribute("cx", "50"); track.setAttribute("cy", "50"); track.setAttribute("r", "38");
    track.setAttribute("class", "ring-track");
    svg.appendChild(track);
    const letters = document.createElementNS(SVG_NS, "g");
    const fs = n <= 8 ? 15 : n <= 14 ? 11.5 : n <= 20 ? 9.5 : 8;
    word.forEach(function (v, q) {
      const ang = -Math.PI / 2 + (q * 2 * Math.PI) / Math.max(1, n);
      const t = document.createElementNS(SVG_NS, "text");
      t.setAttribute("x", String(50 + 38 * Math.cos(ang)));
      t.setAttribute("y", String(50 + 38 * Math.sin(ang)));
      t.setAttribute("font-size", String(fs));
      t.setAttribute("class", "rtok rtok-" + genKey(v) + (v < 0 ? " rtok-inv" : ""));
      t.textContent = D.letter(v);
      letters.appendChild(t);
    });
    svg.appendChild(letters);
    const cut = document.createElementNS(SVG_NS, "g");
    cut.setAttribute("class", "ring-cut");
    const a0 = -Math.PI / 2 - Math.PI / Math.max(1, n); // the gap before letter 0
    const line = document.createElementNS(SVG_NS, "line");
    line.setAttribute("x1", String(50 + 29 * Math.cos(a0)));
    line.setAttribute("y1", String(50 + 29 * Math.sin(a0)));
    line.setAttribute("x2", String(50 + 47 * Math.cos(a0)));
    line.setAttribute("y2", String(50 + 47 * Math.sin(a0)));
    cut.appendChild(line);
    const dot = document.createElementNS(SVG_NS, "circle");
    dot.setAttribute("cx", String(50 + 47 * Math.cos(a0)));
    dot.setAttribute("cy", String(50 + 47 * Math.sin(a0)));
    dot.setAttribute("r", "2.6");
    cut.appendChild(dot);
    svg.appendChild(cut);
    return svg;
  }

  /** Rotate the ring's CUT marker to match roll(word, k): counterclockwise by k slots. */
  function setRingCut(svg, k, n, ms) {
    const cut = svg.querySelector(".ring-cut");
    if (!cut || n < 1) return;
    cut.style.transformOrigin = "50px 50px";
    cut.style.transition = "transform " + ms + "ms " + EASE;
    cut.style.transform = "rotate(" + (-k * 360 / n) + "deg)";
  }

  /** Sliding rotation in the row: a doubled-strip carousel that ticks ONE SLOT at a time,
   *  wrapping in from the left — k discrete slides with a breather between them, so the eye
   *  can count the rotation instead of parsing one fast glide. advanceCut(t, ms) (optional)
   *  is called once per tick so the ring's cut marker steps in lockstep with the tiles. */
  async function slideRotate(entry, word, k, tile, stepMs, gapMs, token, roleCls, advanceCut) {
    const n = word.length;
    const kk = n > 0 ? ((k % n) + n) % n : 0;
    if (kk === 0 || n < 2) return await wait(gapMs, token); // this row sits still — caller narrates why
    const slotW = tile + GAP;
    const viewport = h("span", { class: "rot-viewport" });
    viewport.style.width = (n * slotW - GAP) + "px";
    const strip = h("span", { class: "rot-strip" });
    for (const v of word.concat(word)) {
      const t = tileNode(v);
      if (roleCls) t.classList.add(roleCls);
      strip.appendChild(t);
    }
    viewport.appendChild(strip);
    clear(entry.wrap);
    entry.wrap.appendChild(viewport);
    strip.style.transform = "translateX(" + (-n * slotW) + "px)";  // window shows copy 2 ≡ word
    void strip.offsetWidth;                                        // commit start before transitioning
    for (let t = 1; t <= kk; t++) {
      strip.style.transition = "transform " + stepMs + "ms " + EASE;
      strip.style.transform = "translateX(" + (-(n - t) * slotW) + "px)"; // one slot right
      if (advanceCut) advanceCut(t, stepMs);
      if (!(await wait(stepMs + (t < kk ? gapMs : 40), token))) return false;
    }
    setTiles(entry, D.rollWord(word, kk), roleCls);
    return true;
  }

  /** The partner is used INVERTED: read backwards with every letter inverted. Tiles mirror
   *  around the row's center while flipping edge-on (the letter swaps while invisible). */
  async function flipInvert(entry, word, tile, ms, token, roleCls) {
    const n = word.length;
    if (n < 1) return await wait(ms, token);
    const slotW = tile + GAP;
    const half = Math.max(60, ms / 2);
    entry.tiles.forEach(function (t, q) {
      t.style.transition = "transform " + half + "ms ease-in";
      t.style.transform = "translateX(" + (((n - 1 - 2 * q) * slotW) / 2) + "px) rotateX(90deg)";
    });
    if (!(await wait(half, token))) return false;
    entry.tiles.forEach(function (t, q) {
      const v = -word[q]; // mirroring handles the reversal; each tile just inverts its letter
      t.textContent = D.letter(v);
      t.classList.toggle("inv", v < 0);
      t.style.transition = "transform " + half + "ms ease-out";
      t.style.transform = "translateX(" + ((n - 1 - 2 * q) * slotW) + "px) rotateX(0deg)";
    });
    if (!(await wait(half + 40, token))) return false;
    setTiles(entry, D.invertWord(word), roleCls);
    return true;
  }

  /** Glue the two rotated operands into row A with a FLIP merge: every tile of the spliced
   *  word flies in from where its source tile sat (partner tiles cross rows). Returns the
   *  persistent seam element marking where the halves met. */
  function spliceFlip(rowA, rowB, recon, aIsFirstHalf, ms) {
    const splice = recon.splice;
    const leadLen = recon.rotA.length;
    const leaderRow = aIsFirstHalf ? rowA : rowB;
    const partnerRow = aIsFirstHalf ? rowB : rowA;
    const srcRects = splice.map(function (_, k) {
      const fromLeader = k < leadLen;
      const src = fromLeader ? leaderRow.tiles[k] : partnerRow.tiles[k - leadLen];
      return src ? src.getBoundingClientRect() : null;
    });
    clear(rowA.wrap);
    const seam = h("span", { class: "splice-seam", title: "the two halves meet here" });
    rowA.tiles = splice.map(function (v, k) {
      const t = tileNode(v);
      const fromLeader = k < leadLen;
      t.classList.add((fromLeader === aIsFirstHalf) ? "from-a" : "from-b"); // colour by SOURCE ROW
      if (k === leadLen) rowA.wrap.appendChild(seam);
      rowA.wrap.appendChild(t);
      return t;
    });
    rowA.wrap.classList.add("spliced");
    rowA.tiles.forEach(function (t, k) {  // FLIP: start at the source position...
      const src = srcRects[k];
      if (!src) return;
      const dst = t.getBoundingClientRect();
      const dx = src.left - dst.left, dy = src.top - dst.top;
      if (dx || dy) t.style.transform = "translate(" + dx + "px," + dy + "px)";
    });
    void rowA.wrap.offsetWidth;
    rowA.tiles.forEach(function (t) {     // ...then fly home
      t.style.transition = "transform " + ms + "ms " + EASE;
      t.style.transform = "";
    });
    return seam;
  }

  /** The word is CYCLIC: its two ends are adjacent "around the back". A dashed arc over the
   *  row connects last → first tile so the wrap-around cancellation reads as what it is. */
  function showCyclicArc(wrap, firstTile, lastTile) {
    const old = wrap.querySelector(".cyclic-arc");
    if (old) old.remove();
    if (!firstTile || !lastTile) return null;
    const w = Math.max(40, wrap.scrollWidth);
    const x1 = lastTile.offsetLeft + lastTile.offsetWidth / 2;
    const x2 = firstTile.offsetLeft + firstTile.offsetWidth / 2;
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "cyclic-arc");
    svg.setAttribute("width", String(w));
    svg.setAttribute("height", "26");
    svg.setAttribute("viewBox", "0 0 " + w + " 26");
    svg.setAttribute("aria-hidden", "true");
    const p = document.createElementNS(SVG_NS, "path");
    p.setAttribute("d", "M " + x1 + " 24 C " + x1 + " 4, " + x2 + " 4, " + x2 + " 24");
    p.setAttribute("class", "cyclic-arc-path");
    svg.appendChild(p);
    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("x", String((x1 + x2) / 2));
    label.setAttribute("y", "10");
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("class", "cyclic-arc-label");
    label.textContent = "cyclic ↻";
    svg.appendChild(label);
    wrap.appendChild(svg);
    return svg;
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
    const aIsFirstHalf = emittedIsLeader;              // in `splice`, does A supply the leading half?
    const dur = function (ms) { return Math.max(60, ms * mult); };
    const tile = computeTileSize(recon.splice.length); // widest the row ever gets = the splice

    // -- scaffold: equation card + phase chips + the presentation in its stable rows ----
    clear(dom.stage);
    const box = h("div", { class: "stage-step anim-inplace" });
    box.style.setProperty("--tile-size", tile + "px");
    box.appendChild(h("div", { class: "stage-summary" }, "Step " + i + " — " + step.summary));
    box.appendChild(anatomyNode(recon));               // the move equation, visible from the START
    const phases = ["Roles"].concat(recon.cInv ? ["Invert"] : []).concat(["Rotate", "Splice", "Cancel", "Settle"]);
    const chips = phaseChipsNode(phases);
    box.appendChild(chips);
    const pres = h("div", { class: "presentation" });
    pres.appendChild(h("div", { class: "presentation-line presentation-open" }, "⟨" + gens.join(", ") + " |"));
    const rows = parentSlots.map(function (slot, s) {
      const rt = rowTiles(slot.word);
      const isOp = s === A || s === B;
      const ring = h("span", { class: "ring-inset" + (isOp ? "" : " ring-spacer") });
      if (isOp) ring.appendChild(ringSvgNode(slot.word));
      const row = h("div", {
        class: "relator-row anim-row" + (s === A ? " role-a" : s === B ? " role-b" : " row-idle"),
      }, [ring, rt.wrap]);
      pres.appendChild(row);
      return { row: row, wrap: rt.wrap, tiles: rt.tiles, ring: ring };
    });
    pres.appendChild(h("div", { class: "presentation-line presentation-close" }, "⟩"));
    box.appendChild(pres);
    const narr = h("div", { class: "anim-narration" });
    box.appendChild(narr);
    dom.stage.appendChild(box);

    const rowA = rows[A], rowB = rows[B];
    const rowL = emittedIsLeader ? rowA : rowB;        // shows the leader:  ra  → roll(ra, iRot)
    const rowP = emittedIsLeader ? rowB : rowA;        // shows the partner: cBase → c → roll(c, jRot)
    const clsL = rowL === rowA ? "from-a" : "from-b";
    const clsP = rowP === rowA ? "from-a" : "from-b";
    rowA.tiles.forEach(function (t) { t.classList.add("from-a"); });
    rowB.tiles.forEach(function (t) { t.classList.add("from-b"); });

    function ringCutOf(rowEntry, k, n, ms) {
      const svg = rowEntry.ring && rowEntry.ring.querySelector(".ring-svg");
      if (svg && n > 0) setRingCut(svg, k, n, ms);
    }
    function swapRing(rowEntry, word) {
      if (!rowEntry.ring || rowEntry.ring.classList.contains("ring-spacer")) return;
      clear(rowEntry.ring);
      rowEntry.ring.appendChild(ringSvgNode(word)); // CSS ring-in animation fades it in
    }

    // -- Roles: which two rows are in play, and where the result lands ---------------
    setPhase(chips, "Roles");
    narr.textContent = "Combine the highlighted rows: A (blue edge) is replaced by the result; B (purple) is the partner — only read, it survives.";
    if (!(await wait(dur(DUR.context), token))) return;

    // -- Invert (only when the move uses the partner's inverse) ----------------------
    if (recon.cInv) {
      setPhase(chips, "Invert");
      narr.textContent = "The move uses the partner's INVERSE: read it backwards and invert every letter (case flips).";
      swapRing(rowP, recon.c);
      if (!(await flipInvert(rowP, recon.cBase, tile, dur(DUR.invert), token, clsP))) return;
    }

    // -- Rotate: the ring's cut ticks one slot at a time; the row slides in lockstep -----
    setPhase(chips, "Rotate");
    const nL = recon.ra.length, nP = recon.c.length;
    const iEff = nL > 0 ? ((recon.iRot % nL) + nL) % nL : 0;
    const jEff = nP > 0 ? ((recon.jRot % nP) + nP) % nP : 0;
    const anyRot = iEff !== 0 || jEff !== 0;
    narr.textContent = anyRot
      ? "Relators are CYCLIC — rotating only moves the cut, one slot per tick (watch the rings). Slide until the touching ends are inverses."
      : "No rotation needed — the touching ends are already inverses.";
    if (anyRot) {
      // Per-tick duration shrinks for large rotations so the whole phase stays ≤ rotateCap,
      // but the motion always stays DISCRETE — never a single smooth glide.
      const stepFor = function (ticks) {
        return ticks ? Math.min(dur(DUR.rotateStep), dur(DUR.rotateCap) / ticks) : 0;
      };
      const gapMs = dur(DUR.rotateStepGap);
      const slid = await Promise.all([
        slideRotate(rowL, recon.ra, iEff, tile, stepFor(iEff), gapMs, token, clsL,
          function (t, ms) { ringCutOf(rowL, t, nL, ms); }),
        slideRotate(rowP, recon.c, jEff, tile, stepFor(jEff), gapMs, token, clsP,
          function (t, ms) { ringCutOf(rowP, t, nP, ms); }),
      ]);
      if (!slid[0] || !slid[1]) return;
    } else if (!(await wait(dur(DUR.rotateSkip), token))) {
      return;
    }
    if (!(await wait(dur(DUR.phaseGap), token))) return; // breather: let the rotation register

    // -- Splice: partner tiles fly into row A; the seam marks the join ----------------
    setPhase(chips, "Splice");
    narr.textContent = "Cut both rings open at their marks and glue the words — the letters at the seam are inverses.";
    rows.forEach(function (r) { r.ring.classList.add("ring-out"); }); // stale rings would lie
    rowB.row.classList.add("consumed");
    rowB.row.appendChild(h("span", { class: "copied-note" }, "copied ↑"));
    const seam = spliceFlip(rowA, rowB, recon, aIsFirstHalf, dur(DUR.splice));
    const leadLen = recon.rotA.length;
    const bdA = rowA.tiles[leadLen - 1], bdB = rowA.tiles[leadLen];
    if (bdA && bdB) { bdA.classList.add("will-cancel"); bdB.classList.add("will-cancel"); }
    if (seam && rowA.row.scrollWidth > rowA.row.clientWidth) {
      seam.scrollIntoView({ inline: "center", block: "nearest" });
    }
    if (!(await wait(dur(DUR.splice) + 60, token))) return;
    rowA.tiles.forEach(function (t) { t.style.transition = ""; }); // hand transforms back to CSS
    if (!(await wait(dur(DUR.phaseGap), token))) return; // breather: see the seam before it zips

    // -- Cancel: inverse pairs pluck one at a time, zipping shut at the seam ----------
    setPhase(chips, "Cancel");
    let tiles = rowA.tiles.slice();
    let arc = null;
    for (const ev of recon.events) {
      let t1, t2;
      if (ev.type === "free") {
        t1 = tiles[ev.pos]; t2 = tiles[ev.pos + 1];
        narr.textContent = "Adjacent inverses cancel: " + D.letter(ev.letters[0]) + "·" +
          D.letter(ev.letters[1]) + " — the word zips shut at the seam.";
      } else {
        t1 = tiles[tiles.length - 1]; t2 = tiles[0];
        narr.textContent = "The word is CYCLIC — around the back, its two ends are adjacent: " +
          D.letter(ev.letters[0]) + " and " + D.letter(ev.letters[1]) + " cancel too.";
        rowA.row.classList.add("cyclic-active");
        arc = showCyclicArc(rowA.wrap, tiles[0], tiles[tiles.length - 1]);
        if (!(await wait(dur(DUR.cyclic), token))) return; // a beat to read the arc
      }
      if (!t1 || !t2) break; // defensive; recon is verified so this shouldn't happen
      t1.classList.add("will-cancel"); t2.classList.add("will-cancel");
      if (!(await wait(dur(DUR.pluckMark), token))) return;
      t1.classList.remove("will-cancel"); t2.classList.remove("will-cancel");
      t1.classList.add("plucking"); t2.classList.add("plucking");
      if (!(await wait(dur(DUR.pluckGap), token))) return;
      t1.classList.add("gone"); t2.classList.add("gone");
      if (!(await wait(dur(DUR.pluckPause), token))) return;
      t1.remove(); t2.remove();
      if (ev.type === "free") tiles.splice(ev.pos, 2);
      else { tiles.pop(); tiles.shift(); }
    }
    if (arc) arc.remove();
    rowA.row.classList.remove("cyclic-active");
    if (seam) seam.classList.add("seam-done");

    // -- Settle: the reduced word is the new relator --------------------------------
    setPhase(chips, "Settle");
    rowA.wrap.classList.add("result-glow");
    narr.textContent = recon.canonChanged
      ? "That reduced word is the new relator (written in its canonical rotation)."
      : "That reduced word is the new relator.";
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
    const wasOpen = !!player.entry;
    stopPlaying();
    cancelAnim();
    dom.overlay.classList.add("hidden");
    document.body.classList.remove("modal-open");
    player.entry = null;
    player.solution = null;
    player.arm = null;
    player.stepIndex = 0;
    if (wasOpen) {
      syncHashClosed();
      // hand focus back to the card/cell that opened the modal (if still rendered)
      if (player.opener && document.contains(player.opener)) player.opener.focus();
      player.opener = null;
    }
  }

  // ---- public API ---------------------------------------------------------------
  function init() {
    if (initialized) return;
    cacheDom();
    wireControls();
    wirePlayerControls();
    wireKeyboard();
    // The speed choice survives reloads (Replay's Instant→Normal bump is not persisted).
    try {
      const saved = localStorage.getItem("acx-speed");
      if (saved && dom.speed.querySelector('option[value="' + saved + '"]')) dom.speed.value = saved;
    } catch (e) { /* storage unavailable (private mode) — keep the markup default */ }
    dom.speed.addEventListener("change", function () {
      try { localStorage.setItem("acx-speed", dom.speed.value); } catch (e) { /* ignore */ }
    });
    initialized = true;
  }

  function render(ds) {
    if (!initialized) init();
    dataset = ds;

    filters.search = "";
    filters.solved = "all";
    filters.subset = "all";
    filters.arm = "all";
    filters.layout = "cards";
    filters.sort = "default";
    filters.group = false;
    dom.search.value = "";
    if (dom.sortSelect) dom.sortSelect.value = "default";
    if (dom.groupToggle) dom.groupToggle.checked = false;
    for (const s of dom.filterButtons.querySelectorAll(".seg")) {
      s.classList.toggle("active", s.getAttribute("data-filter") === "all");
    }
    for (const s of dom.viewToggle.querySelectorAll(".seg")) {
      s.classList.toggle("active", s.getAttribute("data-layout") === "cards");
    }

    ensureGridData();
    renderSelects();
    renderGrid();
    closePlayer();
  }

  global.ACXViewer = { init: init, render: render, openFromHash: openFromHash, closePlayer: closePlayer };
})(typeof window !== "undefined" ? window : globalThis);
