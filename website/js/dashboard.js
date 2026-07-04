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
  // Hardcoded to the exact hexes in SPEC.md rather than read from CSS custom
  // properties, so charts render identically even before/without css/styles.css.
  var COLOR_OK = "#35d07f";      // --ok
  var COLOR_ERR = "#ff6b6b";     // --err
  var COLOR_ACCENT = "#5b9dff";  // --accent
  var COLOR_ACCENT2 = "#7c5cff"; // --accent-2
  var COLOR_GENZ = "#c792ea";    // --gen-z
  var ARM_COLORS = {
    r1: "#5b9dff", // --arm-r1
    r2: "#7c5cff", // --arm-r2
    x: "#35d07f",  // --arm-x
    y: "#ffb454",  // --arm-y
    g: "#ff6b9d",  // --arm-g
  };
  var ARM_ORDER = ["r1", "r2", "x", "y", "g"];

  function armSort(a, b) {
    var ia = ARM_ORDER.indexOf(a), ib = ARM_ORDER.indexOf(b);
    ia = ia === -1 ? 99 : ia; ib = ib === -1 ? 99 : ib;
    if (ia !== ib) return ia - ib;
    return a < b ? -1 : a > b ? 1 : 0;
  }

  // ---- state ----------------------------------------------------------------------
  var dom = null;
  var lastDataset = null;
  var initialized = false;

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
      chartSolveByDataset: q("chart-solve-by-dataset"),
      dashTable: q("dash-table"),
      dashTableScope: q("dash-table-scope"),
    };
  }

  // ---- small stats helpers ---------------------------------------------------------
  function median(nums) {
    var vals = nums.filter(function (v) { return v != null && !isNaN(v); }).slice().sort(function (a, b) { return a - b; });
    var n = vals.length;
    if (n === 0) return null;
    var mid = Math.floor(n / 2);
    return n % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }
  function pct(part, whole) { return whole > 0 ? (part / whole) * 100 : 0; }
  /**
   * ACXData.histogram's default bin width is range/12 — fine for roughly-uniform data
   * (path length) but nodes_explored / wall_time_s are typically heavily right-skewed
   * (most presentations solve almost instantly, a long tail takes much longer), so 12
   * wide bins collapse ~90%+ of the mass into a single bar. Pick a finer, still-generic
   * (no dataset-specific thresholds) bin width so the shape near the skew is visible;
   * the bucketing itself still happens entirely inside ACXData.histogram.
   */
  function binSizeFor(values, targetBins) {
    var vals = values.filter(function (v) { return v != null && !isNaN(v); });
    if (!vals.length) return undefined;
    var min = Math.min.apply(null, vals), max = Math.max.apply(null, vals);
    var range = max - min;
    return range > 0 ? range / (targetBins || 24) : undefined;
  }
  function fmtPct(p) { return p.toFixed(1) + "%"; }
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
    var dataset = lastDataset;
    var dsVal = dom.dashDataset ? dom.dashDataset.value || "all" : "all";
    var armVal = dom.dashArm ? dom.dashArm.value || "all" : "all";
    var subVal = dom.dashSubset ? dom.dashSubset.value || "all" : "all";

    var items = filterItems(dataset, dsVal, armVal, subVal);
    var solved = items.filter(function (i) { return i.solved; });
    var unsolved = items.filter(function (i) { return !i.solved; });

    var armsInScope = Array.from(new Set(items.map(function (i) { return i.arm; }))).sort(armSort);
    var datasetsInScope = Array.from(new Set(items.map(function (i) { return i.dataset; }))).sort();

    var scopeText = "Loaded dataset · dataset: " + (dsVal === "all" ? "all" : dsVal) +
      (subVal === "all" ? "" : " · subset: " + (ACXData.subsetLabel ? ACXData.subsetLabel(subVal) : subVal)) +
      " · arm: " + (armVal === "all" ? "all" : armVal) + " · N=" + items.length +
      " — sample stats, not a project-wide result";
    if (dom.dashScope) dom.dashScope.textContent = scopeText;
    if (dom.dashTableScope) dom.dashTableScope.textContent = "(loaded dataset · N=" + items.length + ")";

    // ---- overview cards --------------------------------------------------------
    if (dom.analyticsStats) {
      // "Runs" are (presentation × arm) rows; distinct presentations counted separately
      // so nothing here double-reads as a presentation count.
      var distinct = new Set(items.map(function (i) { return i.dataset + "|" + i.idx; })).size;
      var solveRate = pct(solved.length, items.length);
      var cards = [
        { label: "Runs in scope (presentation × arm)", value: String(items.length) },
        { label: "Solved runs", value: String(solved.length) },
        { label: "Run solve rate", value: fmtPct(solveRate) },
        { label: "Distinct presentations", value: String(distinct) },
        { label: "Arms in scope", value: String(armsInScope.length) },
      ];
      dom.analyticsStats.innerHTML = cards.map(function (c) {
        return '<div class="stat-card"><div class="stat-value">' + c.value +
          '</div><div class="stat-label">' + c.label + '</div></div>';
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
        color: ARM_COLORS[a] || null,
        segments: [
          { key: "solved", value: e.solved, color: COLOR_OK, title: "solved: " + e.solved },
          { key: "unsolved", value: e.unsolved, color: COLOR_ERR, title: "unsolved: " + e.unsolved },
        ],
      };
    });
    ACXCharts.stackedBar(dom.chartSolveByArm, {
      categories: armCategories,
      legend: [
        { key: "solved", color: COLOR_OK, label: "Solved" },
        { key: "unsolved", color: COLOR_ERR, label: "Unsolved" },
      ],
      yLabel: "presentations",
    });

    // ---- chart 2: path length histogram (solved items with a stored path) -----
    var pathLens = solved.filter(function (i) { return i.path && i.path.path_len != null; })
      .map(function (i) { return i.path.path_len; });
    var pathLenBins = ACXData.histogram(pathLens, 1);
    ACXCharts.histogram(dom.chartPathlenHist, pathLenBins, {
      color: COLOR_ACCENT, xLabel: "path length (moves)", yLabel: "solved presentations",
    });

    // ---- chart 3: nodes explored histogram (solved only) -----------------------
    var nodes = solved.filter(function (i) { return i.calib && i.calib.nodes_explored != null; })
      .map(function (i) { return i.calib.nodes_explored; });
    var nodesBins = ACXData.histogram(nodes, binSizeFor(nodes, 24));
    ACXCharts.histogram(dom.chartNodesSolved, nodesBins, {
      color: COLOR_ACCENT2, xLabel: "nodes explored", yLabel: "solved presentations",
    });

    // ---- chart 4: wall time histogram (solved only) -----------------------------
    var times = solved.filter(function (i) { return i.calib && i.calib.wall_time_s != null; })
      .map(function (i) { return i.calib.wall_time_s; });
    var timeBins = ACXData.histogram(times, binSizeFor(times, 24));
    ACXCharts.histogram(dom.chartTimeHist, timeBins, {
      color: COLOR_GENZ, xLabel: "wall time (s)", yLabel: "solved presentations",
      xTickFormat: function (x) { return (Math.round(x * 1000) / 1000) + "s"; },
    });

    // ---- chart 5: solved vs unsolved by dataset ---------------------------------
    var byDataset = new Map();
    datasetsInScope.forEach(function (d) { byDataset.set(d, { solved: 0, unsolved: 0 }); });
    items.forEach(function (i) {
      var e = byDataset.get(i.dataset);
      if (!e) { e = { solved: 0, unsolved: 0 }; byDataset.set(i.dataset, e); }
      if (i.solved) e.solved++; else e.unsolved++;
    });
    var datasetCategories = datasetsInScope.map(function (d) {
      var e = byDataset.get(d);
      return {
        label: d,
        segments: [
          { key: "solved", value: e.solved, color: COLOR_OK, title: "solved: " + e.solved },
          { key: "unsolved", value: e.unsolved, color: COLOR_ERR, title: "unsolved: " + e.unsolved },
        ],
      };
    });
    ACXCharts.stackedBar(dom.chartSolveByDataset, {
      categories: datasetCategories,
      legend: [
        { key: "solved", color: COLOR_OK, label: "Solved" },
        { key: "unsolved", color: COLOR_ERR, label: "Unsolved" },
      ],
      yLabel: "presentations",
    });

    // ---- per-arm table -----------------------------------------------------------
    if (dom.dashTable) {
      var rows = armsInScope.map(function (a) {
        var armItems = items.filter(function (i) { return i.arm === a; });
        var armSolved = armItems.filter(function (i) { return i.solved; });
        var medPathLen = median(armSolved.filter(function (i) { return i.path; }).map(function (i) { return i.path.path_len; }));
        var medNodes = median(armSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.nodes_explored; }));
        var medTime = median(armSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.wall_time_s; }));
        var sym = (ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a;
        return "<tr><td>" + sym + "</td><td>" + armItems.length + "</td><td>" + armSolved.length +
          "</td><td>" + fmtPct(pct(armSolved.length, armItems.length)) + "</td><td>" + fmtOr(medPathLen) +
          "</td><td>" + fmtOr(medNodes) + "</td><td>" + fmtOr(medTime, 3) + "</td></tr>";
      });
      // TOTAL — aggregate across every arm in scope ("total together").
      var allSolved = items.filter(function (i) { return i.solved; });
      var tMedPath = median(allSolved.filter(function (i) { return i.path; }).map(function (i) { return i.path.path_len; }));
      var tMedNodes = median(allSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.nodes_explored; }));
      var tMedTime = median(allSolved.filter(function (i) { return i.calib; }).map(function (i) { return i.calib.wall_time_s; }));
      var totalRow = "<tr class=\"total-row\"><td>Total</td><td>" + items.length + "</td><td>" + allSolved.length +
        "</td><td>" + fmtPct(pct(allSolved.length, items.length)) + "</td><td>" + fmtOr(tMedPath) +
        "</td><td>" + fmtOr(tMedNodes) + "</td><td>" + fmtOr(tMedTime, 3) + "</td></tr>";
      dom.dashTable.innerHTML =
        "<thead><tr><th>z = w</th><th>N</th><th>Solved</th><th>Solved %</th>" +
        "<th>Median path len</th><th>Median nodes (solved)</th><th>Median wall time s (solved)</th></tr></thead>" +
        "<tbody>" + (rows.length ? rows.join("") : '<tr><td colspan="7">No data</td></tr>') + "</tbody>" +
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
    var DATASET_LABELS = { "1190MS": "MS(1190) — full family", "ms_reps_unsolved": "Unsolved-class reps (261)" };
    populateSelect(dom.dashDataset, dataset.datasets.slice().sort(), dsVal, function (d) {
      return DATASET_LABELS[d] || d;
    });
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
