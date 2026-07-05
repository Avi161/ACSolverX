/*
 * dashboard.js — Analytics view for the AC-SolverX Path Explorer.
 *
 * window.ACXDashboard = { init(), render(dataset), onShow() }
 *
 * Reads the currently loaded Dataset (see js/data.js ACXData.buildDataset) filtered by
 * the #dash-dataset/#dash-arm selects, and draws the five charts + overview cards +
 * per-arm table described in website/SPEC.md "Dashboard charts — exact mappings".
 *
 * Everything here is the LOADED dataset (sample or uploaded) — never the project's
 * own claimed results. All stat/label copy says so explicitly per SPEC.
 */
(function (global) {
  "use strict";

  var ACXData = global.ACXData;
  var ACXCharts = global.ACXCharts;

  // ---- design tokens (see website/SPEC.md "Design system") ----------------------
  // Arm order/colors and median are the shared canonical ones (ACXData / ACXCharts) —
  // this file deliberately defines none of its own.
  function cssVar(name, fallback) {
    return (ACXCharts && ACXCharts.cssVar) ? ACXCharts.cssVar(name, fallback) : fallback;
  }
  function themeColors() {
    return {
      ok: cssVar("--ok", "#35d07f"),
      err: cssVar("--err", "#ff6b6b"),
      accent: cssVar("--accent", "#5b9dff"),
      accent2: cssVar("--accent-2", "#7c5cff"),
      genz: cssVar("--gen-z", "#c792ea"),
    };
  }
  var armColor = function (a) { return ACXCharts.armColor(a); };
  var armSort = ACXData.armSort;

  // ---- state ----------------------------------------------------------------------
  var dom = null;
  var lastDataset = null;
  var initialized = false;
  var datasetDefaultApplied = false;

  function q(id) { return document.getElementById(id); }

  function cacheDom() {
    dom = {
      dashDataset: q("dash-dataset"),
      dashSubset: q("dash-subset"),
      dashArm: q("dash-arm"),
      dashScope: q("dash-scope"),
      analyticsStats: q("analytics-stats"),
      chartSolveByArm: q("chart-solve-by-arm"),
      chartPathlenHist: q("chart-pathlen-hist"),
      chartNodesSolved: q("chart-nodes-solved"),
      chartTimeHist: q("chart-time-hist"),
      dashTable: q("dash-table"),
      dashTableScope: q("dash-table-scope"),
      hardSection: q("hard-section"),
      hardStats: q("hard-stats"),
      chartHardClasssize: q("chart-hard-classsize"),
      chartHardRelators: q("chart-hard-relators"),
      hardClassTable: q("hard-class-table"),
    };
  }

  // ---- small stats helpers ---------------------------------------------------------
  var median = ACXData.median;
  var esc = ACXData.esc;
  function pct(part, whole) { return whole > 0 ? (part / whole) * 100 : 0; }
  function fmtPct(p) { return p.toFixed(1) + "%"; }
  /** Compact tick label for the log-binned node histogram (1200 -> 1.2k). */
  function fmtCompact(n) {
    n = Math.round(n);
    if (n >= 1e6) return (Math.round(n / 1e5) / 10) + "M";
    if (n >= 1e3) return (Math.round(n / 100) / 10) + "k";
    return String(n);
  }
  function fmtOr(v, digits) {
    if (v == null || isNaN(v)) return "—";
    return typeof digits === "number" ? v.toFixed(digits) : String(v);
  }

  // ---- option population (selects keep their current value if still valid) --------
  function populateSelect(sel, values, currentValue, labelFn) {
    if (!sel) return;
    // first option is the fixed "all" option already in index.html — keep it, replace the rest.
    var first = sel.options.length ? sel.options[0] : null;
    var desired = values.slice();
    var existing = [];
    for (var i = 1; i < sel.options.length; i++) existing.push(sel.options[i].value);
    var same = existing.length === desired.length && existing.every(function (v, i) { return v === desired[i]; });
    if (!same) {
      sel.innerHTML = "";
      if (first) sel.appendChild(first);
      for (var j = 0; j < desired.length; j++) {
        var opt = document.createElement("option");
        opt.value = desired[j];
        opt.textContent = labelFn ? labelFn(desired[j]) : desired[j];
        sel.appendChild(opt);
      }
    }
    var wanted = currentValue || "all";
    var has = wanted === "all" || desired.indexOf(wanted) !== -1;
    sel.value = has ? wanted : "all";
  }

  // ---- filtering --------------------------------------------------------------------
  function itemSubset(dataset, it) {
    var entry = dataset.byIdx && dataset.byIdx.get(it.dataset + "|" + it.idx);
    return entry ? entry.subset : null;
  }

  function filterItems(dataset, dsVal, armVal, subVal) {
    return dataset.items.filter(function (it) {
      return (dsVal === "all" || it.dataset === dsVal) &&
        (armVal === "all" || it.arm === armVal) &&
        (subVal === "all" || itemSubset(dataset, it) === subVal);
    });
  }

  // ---- draw ---------------------------------------------------------------------------
  function draw() {
    if (!dom || !lastDataset) return;
    var C = themeColors(); // resolve theme colors at draw time (light/dark both correct)
    var dataset = lastDataset;
    var dsVal = dom.dashDataset ? dom.dashDataset.value || "all" : "all";
    var armVal = dom.dashArm ? dom.dashArm.value || "all" : "all";
    var subVal = dom.dashSubset ? dom.dashSubset.value || "all" : "all";

    var items = filterItems(dataset, dsVal, armVal, subVal);
    var solved = items.filter(function (i) { return i.solved; });
    var unsolved = items.filter(function (i) { return !i.solved; });

    var armsInScope = Array.from(new Set(items.map(function (i) { return i.arm; }))).sort(armSort);

    var scopeText = "Loaded dataset · dataset: " + (dsVal === "all" ? "all" : dsVal) +
      (subVal === "all" ? "" : " · subset: " + (ACXData.subsetLabel ? ACXData.subsetLabel(subVal) : subVal)) +
      " · arm: " + (armVal === "all" ? "all" : armVal) + " · " + items.length + " direct runs" +
      " — charts cover direct runs only (the hard 550 are covered via class reps, not run one by one)";
    if (dom.dashScope) dom.dashScope.textContent = scopeText;
    if (dom.dashTableScope) dom.dashTableScope.textContent = "(loaded dataset · " + items.length + " direct runs)";

    // ---- overview cards: PRESENTATION-framed (groupStats v2), never run rows -----
    if (dom.analyticsStats) {
      // Same rule as the Solutions view: with the arm scope on "All z-words", a
      // baseline-only solve must not read as solved (620, not 634, on the 640) —
      // the baseline gets its own scope via the arm select and its own tab.
      var g = ACXData.groupStats(dataset, {
        dataset: dsVal, arm: armVal, subset: subVal,
        excludeArms: armVal === "baseline" ? null : ["baseline"],
      });
      var cards = [
        { label: "Presentations", value: g.total.toLocaleString(), sub: items.length.toLocaleString() + " direct runs in scope" },
        { label: "Solved", value: String(g.solved), cls: "stat-ok", sub: g.attempted ? Math.round(100 * g.solved / g.attempted) + "% of searched" : "" },
        { label: "Unsolved (searched)", value: String(g.unsolvedSearched), cls: "stat-err", sub: "budget exhausted" },
        {
          label: "Covered via reps", value: String(g.coveredViaReps), cls: "stat-warn",
          sub: g.coveredViaReps
            ? "searched via class rep · " +
              ACXData.groupStats(dataset, { dataset: "ms_reps_unsolved" }).solved + " solved"
            : "",
        },
        { label: "Not attempted", value: String(g.notAttempted), cls: "stat-muted" },
      ];
      dom.analyticsStats.innerHTML = cards.map(function (c) {
        return '<div class="stat-card' + (c.cls ? " " + c.cls : "") + '"><div class="stat-value">' + c.value +
          '</div><div class="stat-label">' + c.label + '</div>' +
          (c.sub ? '<div class="stat-sub">' + c.sub + '</div>' : "") + '</div>';
      }).join("");
    }

    // ---- chart 1: solved vs unsolved by arm ------------------------------------
    var byArm = new Map();
    armsInScope.forEach(function (a) { byArm.set(a, { solved: 0, unsolved: 0 }); });
    items.forEach(function (i) {
      var e = byArm.get(i.arm);
      if (!e) { e = { solved: 0, unsolved: 0 }; byArm.set(i.arm, e); }
      if (i.solved) e.solved++; else e.unsolved++;
    });
    var armCategories = armsInScope.map(function (a) {
      var e = byArm.get(a);
      var sym = (ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a;
      return {
        label: sym,
        color: armColor(a),
        segments: [
          { key: "solved", value: e.solved, color: C.ok, title: "solved: " + e.solved },
          { key: "unsolved", value: e.unsolved, color: C.err, title: "unsolved: " + e.unsolved },
        ],
      };
    });
    ACXCharts.stackedBar(dom.chartSolveByArm, {
      categories: armCategories,
      legend: [
        { key: "solved", color: C.ok, label: "Solved" },
        { key: "unsolved", color: C.err, label: "Unsolved" },
      ],
      yLabel: "presentations",
      title: "Solved vs unsolved by change of variables",
      desc: "One stacked bar per z-word; green solved, red unsolved runs.",
    });

    // ---- chart 2: path length histogram (solved items with a stored path) -----
    var pathLens = solved.filter(function (i) { return i.path && i.path.path_len != null; })
      .map(function (i) { return i.path.path_len; });
    var pathLenBins = ACXData.histogram(pathLens, 1);
    ACXCharts.histogram(dom.chartPathlenHist, pathLenBins, {
      color: C.accent, xLabel: "path length (moves)", yLabel: "solved presentations",
      title: "Solution path length distribution",
      desc: "Substitution supermoves per solved presentation.",
    });

    // ---- chart 3: nodes explored histogram (solved only, log 1-2-5 bins) --------
    var nodes = solved.filter(function (i) { return i.calib && i.calib.nodes_explored != null; })
      .map(function (i) { return i.calib.nodes_explored; });
    var nodesBins = ACXData.histogram(nodes, null, { log: true });
    ACXCharts.histogram(dom.chartNodesSolved, nodesBins, {
      color: C.accent2, xLabel: "nodes explored (log bins)", yLabel: "solved presentations",
      xTickFormat: fmtCompact,
      title: "Search cost on solved presentations",
      desc: "Nodes expanded before a solution, in logarithmic bins.",
    });

    // ---- chart 4: wall time histogram (solved only, log 1-2-5 bins) -------------
    var times = solved.filter(function (i) { return i.calib && i.calib.wall_time_s != null; })
      .map(function (i) { return i.calib.wall_time_s; });
    var timeBins = ACXData.histogram(times, null, { log: true });
    ACXCharts.histogram(dom.chartTimeHist, timeBins, {
      color: C.genz, xLabel: "wall time (s, log bins)", yLabel: "solved presentations",
      xTickFormat: function (x) { return x >= 1 ? Math.round(x) + "s" : x + "s"; },
      title: "Wall-clock time per solved presentation",
      desc: "Seconds of search, in logarithmic bins.",
    });

    // ---- per-arm table -----------------------------------------------------------
    if (dom.dashTable) {
      // Hard-class reps coverage per arm, from the FULL loaded dataset (the reps live in
      // their own dataset, so the scope filter would hide them when viewing 1190MS).
      var repsByArm = {};
      dataset.items.forEach(function (i) {
        if (i.dataset !== "ms_reps_unsolved") return;
        var e = repsByArm[i.arm] || (repsByArm[i.arm] = { n: 0, solved: 0 });
        e.n++; if (i.solved) e.solved++;
      });
      function repsCell(a) {
        var e = repsByArm[a];
        return e ? e.solved + "/" + e.n : "—";
      }
      var rows = armsInScope.map(function (a) {
        var armItems = items.filter(function (i) { return i.arm === a; });
        var armSolved = armItems.filter(function (i) { return i.solved; });
        var medPathLen = median(armSolved.filter(function (i) { return i.path; }).map(function (i) { return i.path.path_len; }));
        var medNodes = median(armSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.nodes_explored; }));
        var medTime = median(armSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.wall_time_s; }));
        var sym = esc((ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a);
        return "<tr><td>" + sym + "</td><td>" + armItems.length + "</td><td>" + armSolved.length +
          "</td><td>" + fmtPct(pct(armSolved.length, armItems.length)) + "</td><td>" + repsCell(a) +
          "</td><td>" + fmtOr(medPathLen) +
          "</td><td>" + fmtOr(medNodes) + "</td><td>" + fmtOr(medTime, 3) + "</td></tr>";
      });
      // TOTAL — aggregate across every arm in scope ("total together").
      var allSolved = items.filter(function (i) { return i.solved; });
      var tMedPath = median(allSolved.filter(function (i) { return i.path; }).map(function (i) { return i.path.path_len; }));
      var tMedNodes = median(allSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.nodes_explored; }));
      var tMedTime = median(allSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.wall_time_s; }));
      var totalRow = "<tr class=\"total-row\"><td>Total (direct runs)</td><td>" + items.length + "</td><td>" + allSolved.length +
        "</td><td>" + fmtPct(pct(allSolved.length, items.length)) + "</td><td></td><td>" + fmtOr(tMedPath) +
        "</td><td>" + fmtOr(tMedNodes) + "</td><td>" + fmtOr(tMedTime, 3) + "</td></tr>";
      dom.dashTable.innerHTML =
        "<thead><tr><th>z = w</th><th>Searched</th><th>Solved</th><th>Solved %</th>" +
        "<th>Hard reps (solved/searched)</th>" +
        "<th>Median path len</th><th>Median nodes (solved)</th><th>Median wall time s (solved)</th></tr></thead>" +
        "<tbody>" + (rows.length ? rows.join("") : '<tr><td colspan="8">No data</td></tr>') + "</tbody>" +
        (rows.length ? "<tfoot>" + totalRow + "</tfoot>" : "");
    }

    drawHardSet();
  }

  // ---- hard set: the unsolved classes (always ms_reps_unsolved, filter-independent) --
  var hardSort = { key: "size", dir: -1 };

  function hardRows() {
    var rows = [];
    if (!lastDataset || !lastDataset.byIdx) return rows;
    lastDataset.byIdx.forEach(function (entry) {
      if (entry.dataset !== "ms_reps_unsolved" || !entry.reg) return;
      var r = {
        idx: entry.idx,
        name: entry.reg.name || String(entry.idx),
        size: Array.isArray(entry.reg.nw_cells) ? entry.reg.nw_cells.length : 0,
        len1: entry.reg.relators && entry.reg.relators[0] ? entry.reg.relators[0].length : 0,
        len2: entry.reg.relators && entry.reg.relators[1] ? entry.reg.relators[1].length : 0,
        armsTotal: 0, solved: 0, exhausted: 0,
        times: [], reverts: [], nps: [],
      };
      entry.arms.forEach(function (it) {
        r.armsTotal++;
        if (it.solved) r.solved++;
        var c = it.calib;
        if (!c) return;
        if (c.exhausted_budget) r.exhausted++;
        if (c.wall_time_s != null) r.times.push(c.wall_time_s);
        if (c.revert_hits != null) r.reverts.push(c.revert_hits);
        if (c.nodes_per_sec != null) r.nps.push(c.nodes_per_sec);
      });
      r.totalLen = r.len1 + r.len2;
      r.medTime = median(r.times);
      r.medRevert = median(r.reverts);
      r.medNps = median(r.nps);
      rows.push(r);
    });
    return rows;
  }

  function drawHardSet() {
    if (!dom.hardSection) return;
    var rows = hardRows();
    dom.hardSection.classList.toggle("hidden", rows.length === 0);
    if (!rows.length) return;

    // ---- aggregate cards: the never-surfaced perf fields, aggregated at last ----
    var totalMembers = 0, totalRuns = 0, totalExhausted = 0, solvedClasses = 0;
    var allTimes = [], allReverts = [], allNps = [];
    rows.forEach(function (r) {
      totalMembers += r.size; totalRuns += r.armsTotal; totalExhausted += r.exhausted;
      if (r.solved > 0) solvedClasses++;
      Array.prototype.push.apply(allTimes, r.times);
      Array.prototype.push.apply(allReverts, r.reverts);
      Array.prototype.push.apply(allNps, r.nps);
    });
    var fmtS = function (v) { return v == null ? "—" : (Math.round(v * 10) / 10).toLocaleString(); };
    var cards = [
      { label: "Unsolved classes", value: String(rows.length), cls: solvedClasses ? "stat-ok" : "stat-warn", sub: solvedClasses + " solved" },
      { label: "Hard presentations covered", value: totalMembers.toLocaleString(), sub: "members across all classes" },
      { label: "Rep runs", value: totalRuns.toLocaleString(), cls: "stat-err", sub: totalExhausted.toLocaleString() + " hit the node budget" },
      { label: "Median wall time (s)", value: fmtS(median(allTimes)), sub: "per exhausted 500k-node run" },
      { label: "Median revert hits", value: fmtS(median(allReverts)), sub: "null-move reverts per run" },
      { label: "Median nodes/sec", value: fmtS(median(allNps)), sub: "search throughput" },
    ];
    dom.hardStats.innerHTML = cards.map(function (c) {
      return '<div class="stat-card' + (c.cls ? " " + c.cls : "") + '"><div class="stat-value">' + c.value +
        '</div><div class="stat-label">' + c.label + '</div>' +
        (c.sub ? '<div class="stat-sub">' + c.sub + '</div>' : "") + '</div>';
    }).join("");

    // ---- charts: class sizes + rep total relator length ----
    var C = themeColors();
    ACXCharts.histogram(dom.chartHardClasssize,
      ACXData.histogram(rows.map(function (r) { return r.size; }), 1), {
        color: cssVar("--warn", "#ffb454"), xLabel: "class size (hard members)", yLabel: "classes",
        title: "Unsolved class sizes",
        desc: "How many hard presentations each unsolved class stands for.",
      });
    ACXCharts.histogram(dom.chartHardRelators,
      ACXData.histogram(rows.map(function (r) { return r.totalLen; }), 2), {
        color: C.accent2, xLabel: "|r₁| + |r₂| of the representative", yLabel: "classes",
        title: "Representative total relator length",
        desc: "Combined relator length of each class representative.",
      });

    // ---- sortable class table (row click opens the rep in the player) ----
    var sorted = rows.slice().sort(function (a, b) {
      var av = a[hardSort.key], bv = b[hardSort.key];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      if (av !== bv) return (av < bv ? -1 : 1) * hardSort.dir;
      return a.idx - b.idx;
    });
    var COLS = [
      { key: "name", label: "class" }, { key: "size", label: "members" },
      { key: "len1", label: "|r₁|" }, { key: "len2", label: "|r₂|" },
      { key: "solved", label: "z-words solved" }, { key: "exhausted", label: "exhausted" },
      { key: "medTime", label: "med wall s" }, { key: "medRevert", label: "med reverts" },
      { key: "medNps", label: "med nodes/s" },
    ];
    var thead = "<thead><tr>" + COLS.map(function (c) {
      var mark = hardSort.key === c.key ? (hardSort.dir === -1 ? " ▾" : " ▴") : "";
      return '<th class="th-sort" data-sort="' + c.key + '">' + c.label + mark + "</th>";
    }).join("") + "</tr></thead>";
    var tbody = "<tbody>" + sorted.map(function (r) {
      return '<tr class="hard-row" data-rep-idx="' + r.idx + '" title="open representative #' + r.idx + '">' +
        "<td>" + esc(r.name) + "</td><td>" + r.size + "</td><td>" + r.len1 + "</td><td>" + r.len2 +
        "</td><td>" + r.solved + "/" + r.armsTotal + "</td><td>" + r.exhausted +
        "</td><td>" + fmtS(r.medTime) + "</td><td>" + fmtS(r.medRevert) +
        "</td><td>" + fmtS(r.medNps) + "</td></tr>";
    }).join("") + "</tbody>";
    dom.hardClassTable.innerHTML = thead + tbody;
  }

  function wireHardTable() {
    if (!dom.hardClassTable) return;
    dom.hardClassTable.addEventListener("click", function (e) {
      var th = e.target.closest("th[data-sort]");
      if (th) {
        var key = th.getAttribute("data-sort");
        if (hardSort.key === key) hardSort.dir = -hardSort.dir;
        else { hardSort.key = key; hardSort.dir = key === "name" ? 1 : -1; }
        drawHardSet();
        return;
      }
      var row = e.target.closest("tr[data-rep-idx]");
      if (row) {
        // deep-link into the Solutions player (route() opens it once the view shows)
        location.hash = "#/solutions?open=ms_reps_unsolved:" + row.getAttribute("data-rep-idx");
      }
    });
  }

  // ---- public API -------------------------------------------------------------------
  function init() {
    if (initialized) return;
    cacheDom();
    if (dom.dashDataset) dom.dashDataset.addEventListener("change", draw);
    if (dom.dashSubset) dom.dashSubset.addEventListener("change", draw);
    if (dom.dashArm) dom.dashArm.addEventListener("change", draw);
    wireHardTable();
    global.addEventListener("resize", function () { onShow(); });
    initialized = true;
  }

  function render(dataset) {
    if (!initialized) init();
    lastDataset = dataset;
    var dsVal = dom.dashDataset ? dom.dashDataset.value : "all";
    var subVal = dom.dashSubset ? dom.dashSubset.value : "all";
    var armVal = dom.dashArm ? dom.dashArm.value : "all";
    populateSelect(dom.dashDataset, dataset.datasets.slice().sort(), dsVal, function (d) {
      return (ACXData && ACXData.datasetLabel) ? ACXData.datasetLabel(d) : d;
    });
    // First render defaults to MS(1190) (like Solutions) so the headline reads over the
    // 1190 — "all" would double-count the hard presentations and their class reps.
    if (!datasetDefaultApplied) {
      datasetDefaultApplied = true;
      if ((dsVal === "all" || !dsVal) && dataset.datasets.indexOf("1190MS") !== -1) {
        dom.dashDataset.value = "1190MS";
      }
    }
    populateSelect(dom.dashSubset, (dataset.subsets || []).slice().sort(), subVal, function (s) {
      return (ACXData && ACXData.subsetLabel) ? ACXData.subsetLabel(s) : s;
    });
    populateSelect(dom.dashArm, dataset.arms.slice().sort(armSort), armVal, function (a) {
      return (ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a;
    });
    draw();
  }

  function onShow() {
    if (!lastDataset) return;
    draw();
  }

  var ACXDashboard = { init: init, render: render, onShow: onShow };

  global.ACXDashboard = ACXDashboard;
  if (typeof module !== "undefined" && module.exports) module.exports = ACXDashboard;
})(typeof window !== "undefined" ? window : globalThis);
