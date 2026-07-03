/*
 * comparison.js — Comparison view for the AC-SolverX Path Explorer.
 *
 * window.ACXComparison = { init(), render(dataset), onShow() }
 *
 * "Is the z=w stabilized search more efficient than the 2-generator baseline?" — on the 640 solved
 * MS(1190), compares the baseline arm against each z=w word arm on coverage, node usage, and path
 * length, plus a per-idx scatter (baseline nodes vs arm nodes; a point below the y=x diagonal means
 * the arm solved that presentation with fewer nodes). Joins arms per presentation via dataset.byIdx.
 *
 * Budget note: baseline & r1/r2 are the matched 500k run; x/y/g come from the earlier 12k pass — the
 * per-idx nodes-explored comparison is on presentations BOTH solve, where nodes-to-solve is
 * budget-independent (both finish well under budget).
 */
(function (global) {
  "use strict";

  var ACXData = global.ACXData;
  var ACXCharts = global.ACXCharts;

  var DATASET = "1190MS";
  var COLOR_OK = "#35d07f", COLOR_ERR = "#ff6b6b";
  var ARM_COLORS = {
    baseline: "#9fb0c6", r1: "#5b9dff", r2: "#7c5cff", x: "#35d07f", y: "#ffb454",
    g: "#ff6b9d", xY: "#c792ea", yx: "#f78c6c", Xy: "#80cbc4",
  };
  var ARM_ORDER = ["baseline", "r1", "r2", "x", "y", "g", "xY", "yx", "Xy"];

  function armSort(a, b) {
    var ia = ARM_ORDER.indexOf(a), ib = ARM_ORDER.indexOf(b);
    ia = ia === -1 ? 99 : ia; ib = ib === -1 ? 99 : ib;
    return ia !== ib ? ia - ib : (a < b ? -1 : a > b ? 1 : 0);
  }
  function armLabel(a) { return a === "baseline" ? "baseline (2-gen)" : ((ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a); }

  var dom = null, lastDataset = null, initialized = false;

  function q(id) { return document.getElementById(id); }

  function cacheDom() {
    dom = {
      stats: q("comparison-stats"),
      note: q("comparison-note"),
      armSelect: q("comparison-arm"),
      chartCoverage: q("chart-cmp-coverage"),
      chartNodes: q("chart-cmp-nodes"),
      chartPathlen: q("chart-cmp-pathlen"),
      chartScatter: q("chart-cmp-scatter"),
      scatterNote: q("comparison-scatter-note"),
    };
  }

  function median(nums) {
    var vals = nums.filter(function (v) { return v != null && !isNaN(v); }).slice().sort(function (a, b) { return a - b; });
    var n = vals.length;
    if (n === 0) return null;
    var mid = Math.floor(n / 2);
    return n % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }
  function nodesOf(it) { return it && it.calib && it.calib.nodes_explored != null ? it.calib.nodes_explored : null; }
  function pathOf(it) { return it && it.path && it.path.path_len != null ? it.path.path_len : (it && it.calib && it.calib.path_len != null ? it.calib.path_len : null); }

  // arm -> array of items in DATASET
  function armMap() {
    var m = {};
    if (!lastDataset) return m;
    lastDataset.items.forEach(function (it) {
      if (it.dataset !== DATASET) return;
      (m[it.arm] || (m[it.arm] = [])).push(it);
    });
    return m;
  }

  function armsPresent(m) {
    return Object.keys(m).sort(armSort);
  }

  function draw() {
    if (!dom || !lastDataset) return;
    var m = armMap();
    var arms = armsPresent(m);

    if (dom.note) {
      var hasBaseline = arms.indexOf("baseline") !== -1;
      dom.note.textContent = hasBaseline
        ? "On the 640 solved MS(1190). Node/path comparison is over presentations BOTH arms solve. Baseline & r₁/r₂ are the 500k run; x/y/g are the 12k pass — nodes-to-solve is budget-independent for solved cases."
        : "No baseline loaded yet — showing z=w arms only. Run the baseline sweep + rebuild the bundle to enable the baseline comparison.";
    }

    // ---- coverage: solved/unsolved per arm ----
    var covCats = arms.map(function (a) {
      var its = m[a], s = its.filter(function (i) { return i.solved; }).length;
      return {
        label: armLabel(a), color: ARM_COLORS[a] || null,
        segments: [
          { key: "solved", value: s, color: COLOR_OK, title: "solved: " + s },
          { key: "unsolved", value: its.length - s, color: COLOR_ERR, title: "unsolved: " + (its.length - s) },
        ],
      };
    });
    ACXCharts.stackedBar(dom.chartCoverage, {
      categories: covCats,
      legend: [{ key: "s", color: COLOR_OK, label: "Solved" }, { key: "u", color: COLOR_ERR, label: "Unsolved" }],
      yLabel: "presentations",
    });

    // ---- median nodes per arm (solved) ----
    ACXCharts.stackedBar(dom.chartNodes, {
      categories: arms.map(function (a) {
        var med = median(m[a].filter(function (i) { return i.solved; }).map(nodesOf));
        return { label: armLabel(a), color: ARM_COLORS[a] || null,
          segments: [{ key: "nodes", value: med || 0, color: ARM_COLORS[a] || "#5b9dff", title: "median nodes: " + (med == null ? "—" : med) }] };
      }),
      yLabel: "median nodes (solved)",
    });

    // ---- median path length per arm (solved) ----
    ACXCharts.stackedBar(dom.chartPathlen, {
      categories: arms.map(function (a) {
        var med = median(m[a].filter(function (i) { return i.solved; }).map(pathOf));
        return { label: armLabel(a), color: ARM_COLORS[a] || null,
          segments: [{ key: "plen", value: med || 0, color: ARM_COLORS[a] || "#5b9dff", title: "median path length: " + (med == null ? "—" : med) }] };
      }),
      yLabel: "median path length (solved)",
    });

    // ---- per-idx scatter: baseline nodes vs selected arm nodes ----
    if (dom.armSelect) {
      var opts = arms.filter(function (a) { return a !== "baseline"; });
      var cur = dom.armSelect.value;
      dom.armSelect.innerHTML = opts.map(function (a) { return '<option value="' + a + '">' + armLabel(a) + "</option>"; }).join("");
      if (cur && opts.indexOf(cur) !== -1) dom.armSelect.value = cur;
      else if (opts.length) dom.armSelect.value = opts.indexOf("r1") !== -1 ? "r1" : opts[0];
    }
    var selArm = dom.armSelect ? dom.armSelect.value : "r1";
    var byIdx = lastDataset.byIdx;
    var points = [], cheaper = 0, ratios = [];
    if (byIdx) {
      byIdx.forEach(function (entry) {
        if (entry.dataset !== DATASET || !entry.arms) return;
        var base = entry.arms.get("baseline"), arm = entry.arms.get(selArm);
        if (!base || !arm || !base.solved || !arm.solved) return;
        var bn = nodesOf(base), an = nodesOf(arm);
        if (bn == null || an == null) return;
        points.push({ x: bn, y: an, title: "idx " + entry.idx + ": baseline " + bn + " vs " + selArm + " " + an });
        if (an < bn) cheaper++;
        if (bn > 0) ratios.push(an / bn);
      });
    }
    ACXCharts.scatter(dom.chartScatter, points, {
      xLabel: "baseline nodes explored", yLabel: (armLabel(selArm) + " nodes explored"),
      color: ARM_COLORS[selArm] || "#5b9dff", log: true, diagonal: true,
    });
    if (dom.scatterNote) {
      dom.scatterNote.textContent = points.length
        ? (points.length + " presentations both solve · " + cheaper + " cheaper under " + armLabel(selArm) +
           " (below the diagonal) · median node ratio " + (median(ratios) != null ? median(ratios).toFixed(2) + "×" : "—"))
        : "No presentations solved by both baseline and " + armLabel(selArm) + " yet.";
    }

    // ---- summary cards ----
    if (dom.stats) {
      var baseItems = m.baseline || [];
      var baseSolved = baseItems.filter(function (i) { return i.solved; }).length;
      var cards = [
        { label: "Arms compared", value: String(arms.length) },
        { label: "Baseline solved / " + (baseItems.length || 640), value: baseItems.length ? String(baseSolved) : "—" },
        { label: "Both-solve pairs (vs " + selArm + ")", value: String(points.length) },
        { label: selArm + " cheaper than baseline", value: points.length ? cheaper + " (" + Math.round(100 * cheaper / points.length) + "%)" : "—" },
      ];
      dom.stats.innerHTML = cards.map(function (c) {
        return '<div class="stat-card"><div class="stat-value">' + c.value +
          '</div><div class="stat-label">' + c.label + '</div></div>';
      }).join("");
    }
  }

  function init() {
    if (initialized) return;
    cacheDom();
    if (dom.armSelect) dom.armSelect.addEventListener("change", draw);
    global.addEventListener("resize", function () { onShow(); });
    initialized = true;
  }

  function render(dataset) {
    if (!initialized) init();
    lastDataset = dataset;
    draw();
  }

  function onShow() { if (lastDataset) draw(); }

  var ACXComparison = { init: init, render: render, onShow: onShow };
  global.ACXComparison = ACXComparison;
  if (typeof module !== "undefined" && module.exports) module.exports = ACXComparison;
})(typeof window !== "undefined" ? window : globalThis);
