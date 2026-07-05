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
    };
  }

  // ---- small stats helpers ---------------------------------------------------------
  var median = ACXData.median;
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
        { label: "Covered via reps", value: String(g.coveredViaReps), cls: "stat-warn", sub: g.coveredViaReps ? "searched via class rep · 0 solved" : "" },
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
        var sym = (ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a;
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
      var totalRow = "<tr class=\"total-row\"><td>Total</td><td>" + items.length + "</td><td>" + allSolved.length +
        "</td><td>" + fmtPct(pct(allSolved.length, items.length)) + "</td><td></td><td>" + fmtOr(tMedPath) +
        "</td><td>" + fmtOr(tMedNodes) + "</td><td>" + fmtOr(tMedTime, 3) + "</td></tr>";
      dom.dashTable.innerHTML =
        "<thead><tr><th>z = w</th><th>Searched</th><th>Solved</th><th>Solved %</th>" +
        "<th>Hard reps (solved/searched)</th>" +
        "<th>Median path len</th><th>Median nodes (solved)</th><th>Median wall time s (solved)</th></tr></thead>" +
        "<tbody>" + (rows.length ? rows.join("") : '<tr><td colspan="8">No data</td></tr>') + "</tbody>" +
        (rows.length ? "<tfoot>" + totalRow + "</tfoot>" : "");
    }
  }

  // ---- public API -------------------------------------------------------------------
  function init() {
    if (initialized) return;
    cacheDom();
    if (dom.dashDataset) dom.dashDataset.addEventListener("change", draw);
    if (dom.dashSubset) dom.dashSubset.addEventListener("change", draw);
    if (dom.dashArm) dom.dashArm.addEventListener("change", draw);
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
