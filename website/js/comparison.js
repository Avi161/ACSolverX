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
      chartScatterPath: q("chart-cmp-scatter-path"),
      scatterPathNote: q("comparison-scatter-path-note"),
      table: q("cmp-table"),
      tableNote: q("cmp-table-note"),
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

  // baseline-vs-arm join over presentations BOTH solve (via byIdx). Nodes-to-solve and path length
  // are budget-independent for solved cases, so this is the fair per-presentation comparison.
  function paired(arm) {
    var r = { n: 0, nodePts: [], pathPts: [], nodeCheaper: 0, pathShorter: 0,
              baseNodes: [], armNodes: [], basePath: [], armPath: [], nodeRatios: [], pathRatios: [] };
    var byIdx = lastDataset && lastDataset.byIdx;
    if (!byIdx) return r;
    byIdx.forEach(function (entry) {
      if (entry.dataset !== DATASET || !entry.arms) return;
      var base = entry.arms.get("baseline"), a = entry.arms.get(arm);
      if (!base || !a || !base.solved || !a.solved) return;
      var bn = nodesOf(base), an = nodesOf(a), bp = pathOf(base), ap = pathOf(a);
      if (bn == null || an == null || bp == null || ap == null) return;
      r.n++;
      r.nodePts.push({ x: bn, y: an, title: "idx " + entry.idx + ": baseline " + bn + " vs " + arm + " " + an });
      r.pathPts.push({ x: bp, y: ap, title: "idx " + entry.idx + ": baseline " + bp + " vs " + arm + " " + ap });
      r.baseNodes.push(bn); r.armNodes.push(an); r.basePath.push(bp); r.armPath.push(ap);
      if (an < bn) r.nodeCheaper++;
      if (ap < bp) r.pathShorter++;
      if (bn > 0) r.nodeRatios.push(an / bn);
      if (bp > 0) r.pathRatios.push(ap / bp);
    });
    return r;
  }

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
        ? "On the 640 solved MS(1190), all trivializable by the 2-gen baseline. Node/path comparison is over presentations BOTH arms solve. Baseline and r₁/r₂/x/y are the matched 500k run; g is the earlier 12k pass — nodes-to-solve and path length are budget-independent for solved cases."
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

    // ---- per-idx head-to-head: baseline vs selected arm (nodes + path scatters) ----
    if (dom.armSelect) {
      var opts = arms.filter(function (a) { return a !== "baseline"; });
      var cur = dom.armSelect.value;
      dom.armSelect.innerHTML = opts.map(function (a) { return '<option value="' + a + '">' + armLabel(a) + "</option>"; }).join("");
      if (cur && opts.indexOf(cur) !== -1) dom.armSelect.value = cur;
      else if (opts.length) dom.armSelect.value = opts.indexOf("r1") !== -1 ? "r1" : opts[0];
    }
    var selArm = dom.armSelect ? dom.armSelect.value : "r1";
    var pr = paired(selArm);
    var points = pr.nodePts, cheaper = pr.nodeCheaper;   // reused by the summary cards below

    ACXCharts.scatter(dom.chartScatter, pr.nodePts, {
      xLabel: "baseline nodes explored", yLabel: (armLabel(selArm) + " nodes explored"),
      color: ARM_COLORS[selArm] || "#5b9dff", log: true, diagonal: true,
    });
    if (dom.scatterNote) {
      dom.scatterNote.textContent = pr.n
        ? (cheaper + " of " + pr.n + " cheaper under " + armLabel(selArm) + " (below the line) · median ratio " +
           (median(pr.nodeRatios) != null ? median(pr.nodeRatios).toFixed(2) + "×" : "—") + " (>1 = z=w explores more)")
        : "No presentations solved by both baseline and " + armLabel(selArm) + " yet.";
    }

    ACXCharts.scatter(dom.chartScatterPath, pr.pathPts, {
      xLabel: "baseline path length", yLabel: (armLabel(selArm) + " path length"),
      color: ARM_COLORS[selArm] || "#5b9dff", log: true, diagonal: true,
    });
    if (dom.scatterPathNote) {
      dom.scatterPathNote.textContent = pr.n
        ? (pr.pathShorter + " of " + pr.n + " shorter under " + armLabel(selArm) + " (below the line) · median ratio " +
           (median(pr.pathRatios) != null ? median(pr.pathRatios).toFixed(2) + "×" : "—") + " (>1 = z=w path is longer)")
        : "No presentations solved by both baseline and " + armLabel(selArm) + " yet.";
    }

    // ---- head-to-head table: every z=w arm vs baseline on its both-solve set ----
    if (dom.table) {
      var nonBase = arms.filter(function (a) { return a !== "baseline"; });
      var rows = nonBase.map(function (a) {
        var p = paired(a);
        function pct(k) { return p.n ? Math.round(100 * k / p.n) + "%" : "—"; }
        function mr(rs) { return rs.length ? median(rs).toFixed(2) + "×" : "—"; }
        function m(xs) { return median(xs) == null ? "—" : median(xs); }
        return "<tr><td>" + armLabel(a) + "</td><td>" + p.n +
          "</td><td>" + m(p.baseNodes) + "</td><td>" + m(p.armNodes) +
          "</td><td>" + pct(p.nodeCheaper) + "</td><td>" + mr(p.nodeRatios) +
          "</td><td>" + m(p.basePath) + "</td><td>" + m(p.armPath) +
          "</td><td>" + pct(p.pathShorter) + "</td><td>" + mr(p.pathRatios) + "</td></tr>";
      }).join("");
      dom.table.innerHTML =
        "<thead><tr><th>arm (z=w)</th><th>both solve</th>" +
        "<th>base nodes</th><th>arm nodes</th><th>arm fewer</th><th>node ratio</th>" +
        "<th>base path</th><th>arm path</th><th>arm shorter</th><th>path ratio</th></tr></thead>" +
        "<tbody>" + (rows || "<tr><td colspan='10' class='muted'>No both-solve pairs — is the baseline loaded?</td></tr>") + "</tbody>";
    }
    if (dom.tableNote) {
      dom.tableNote.textContent = "Medians over presentations both the baseline and that arm solve. "
        + "“arm fewer / shorter” = share where z=w strictly beats the 2-gen baseline; ratio = median(arm ÷ baseline), >1 means z=w is worse.";
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
