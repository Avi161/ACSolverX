/*
 * baseline.js — Baseline view for the AC-SolverX Path Explorer.
 *
 * window.ACXBaseline = { init(), render(dataset), onShow() }
 *
 * Shows the 2-generator GS-Sub baseline (arm "baseline", n_gen=2) over the 640 solved MS(1190):
 * overview cards, nodes-explored + path-length histograms, and a minimal step browser for a
 * solved path. Deliberately does NOT route through data.js/viewer.js's z=w player (its decodeZWord
 * assumes a stabilized 3-generator presentation and would mis-label a plain 2-gen path) — it renders
 * the raw ⟨x,y | r₁,r₂⟩ states directly.
 */
(function (global) {
  "use strict";

  var ACXData = global.ACXData;
  var ACXCharts = global.ACXCharts;

  var COLOR_OK = "#35d07f", COLOR_ERR = "#ff6b6b", COLOR_ACCENT = "#5b9dff", COLOR_ACCENT2 = "#7c5cff";
  var LET = { 0: "ε", 1: "x", "-1": "X", 2: "y", "-2": "Y", 3: "z", "-3": "Z" };

  var dom = null, lastDataset = null, initialized = false;

  function q(id) { return document.getElementById(id); }

  function cacheDom() {
    dom = {
      stats: q("baseline-stats"),
      note: q("baseline-note"),
      chartNodes: q("chart-baseline-nodes"),
      chartPathlen: q("chart-baseline-pathlen"),
      pathSelect: q("baseline-path-select"),
      pathView: q("baseline-path-view"),
    };
  }

  function median(nums) {
    var vals = nums.filter(function (v) { return v != null && !isNaN(v); }).slice().sort(function (a, b) { return a - b; });
    var n = vals.length;
    if (n === 0) return null;
    var mid = Math.floor(n / 2);
    return n % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }
  function fmtOr(v) { return (v == null || isNaN(v)) ? "—" : String(v); }
  function word(rel) {
    if (!rel || !rel.length) return "ε";
    return rel.map(function (a) { return LET[a] != null ? LET[a] : "?"; }).join("");
  }
  function presentation(state) {
    return "⟨x,y | " + state.map(word).join(" , ") + "⟩";
  }

  function baselineItems() {
    if (!lastDataset) return [];
    return lastDataset.items.filter(function (it) { return it.arm === "baseline"; });
  }

  function renderPath(item) {
    if (!dom.pathView) return;
    if (!item || !item.path || !Array.isArray(item.path.states)) {
      dom.pathView.innerHTML = '<p class="hint">No stored path for this presentation.</p>';
      return;
    }
    var states = item.path.states, moves = item.path.moves || [];
    var rows = states.map(function (st, t) {
      var mv = moves[t];
      var moveTxt = mv ? ("move r" + (mv[0] + 1) + "  (rot " + mv[1] + "," + mv[2] + (mv[3] ? ", inv" : "") + ")") : "start";
      var last = t === states.length - 1;
      return '<li class="bl-step' + (last ? " bl-step-final" : "") + '">' +
        '<span class="bl-step-n">' + t + '</span>' +
        '<span class="bl-step-move">' + moveTxt + '</span>' +
        '<code class="bl-step-pres">' + presentation(st) + '</code></li>';
    });
    dom.pathView.innerHTML = '<ol class="bl-steps">' + rows.join("") + '</ol>';
  }

  function draw() {
    if (!dom || !lastDataset) return;
    var items = baselineItems();
    var solved = items.filter(function (i) { return i.solved; });
    var unsolved = items.filter(function (i) { return !i.solved; });

    if (dom.note) {
      var budgets = Array.from(new Set(items.map(function (i) { return i.budget; }))).sort(function (a, b) { return a - b; });
      dom.note.textContent = items.length
        ? ("2-generator GS-Sub baseline over the 640 solved MS(1190) · budget " +
           budgets.map(function (b) { return b >= 1000 ? (b / 1000) + "k" : b; }).join("/") +
           " nodes · the classical control for the z=w arms.")
        : "No baseline records loaded. Run run_greedy_sweep.py (arm baseline) and rebuild the bundle.";
    }

    // overview cards
    if (dom.stats) {
      var medNodes = median(solved.map(function (i) { return i.calib ? i.calib.nodes_explored : null; }));
      var medPath = median(solved.map(function (i) { return i.path ? i.path.path_len : (i.calib ? i.calib.path_len : null); }));
      var rate = items.length ? (100 * solved.length / items.length).toFixed(1) + "%" : "—";
      var cards = [
        { label: "Presentations", value: String(items.length) },
        { label: "Solved", value: String(solved.length) },
        { label: "Exhausted budget", value: String(unsolved.length) },
        { label: "Solve rate", value: rate },
        { label: "Median nodes (solved)", value: fmtOr(medNodes) },
        { label: "Median path length", value: fmtOr(medPath) },
      ];
      dom.stats.innerHTML = cards.map(function (c) {
        return '<div class="stat-card"><div class="stat-value">' + c.value +
          '</div><div class="stat-label">' + c.label + '</div></div>';
      }).join("");
    }

    // histograms (solved only — unsolved hit the node budget)
    var nodes = solved.filter(function (i) { return i.calib && i.calib.nodes_explored != null; })
      .map(function (i) { return i.calib.nodes_explored; });
    var nmin = nodes.length ? Math.min.apply(null, nodes) : 0, nmax = nodes.length ? Math.max.apply(null, nodes) : 0;
    var nbs = nmax > nmin ? (nmax - nmin) / 24 : undefined;
    ACXCharts.histogram(dom.chartNodes, ACXData.histogram(nodes, nbs), {
      color: COLOR_ACCENT2, xLabel: "nodes explored", yLabel: "solved presentations",
    });
    var plens = solved.filter(function (i) { return i.path && i.path.path_len != null; })
      .map(function (i) { return i.path.path_len; });
    ACXCharts.histogram(dom.chartPathlen, ACXData.histogram(plens, 1), {
      color: COLOR_ACCENT, xLabel: "path length (moves)", yLabel: "solved presentations",
    });

    // path browser (solved, with a stored path)
    if (dom.pathSelect) {
      var withPath = solved.filter(function (i) { return i.path && i.path.states; })
        .sort(function (a, b) { return a.idx - b.idx; });
      var cur = dom.pathSelect.value;
      dom.pathSelect.innerHTML = withPath.map(function (i) {
        return '<option value="' + i.idx + '">idx ' + i.idx + " · " +
          (i.path.path_len != null ? i.path.path_len + " moves" : "") + "</option>";
      }).join("");
      if (cur && withPath.some(function (i) { return String(i.idx) === cur; })) dom.pathSelect.value = cur;
      var sel = withPath.filter(function (i) { return String(i.idx) === dom.pathSelect.value; })[0] || withPath[0];
      renderPath(sel);
    }
  }

  function init() {
    if (initialized) return;
    cacheDom();
    if (dom.pathSelect) dom.pathSelect.addEventListener("change", function () {
      var items = baselineItems();
      var sel = items.filter(function (i) { return String(i.idx) === dom.pathSelect.value; })[0];
      renderPath(sel);
    });
    global.addEventListener("resize", function () { onShow(); });
    initialized = true;
  }

  function render(dataset) {
    if (!initialized) init();
    lastDataset = dataset;
    draw();
  }

  function onShow() { if (lastDataset) draw(); }

  var ACXBaseline = { init: init, render: render, onShow: onShow };
  global.ACXBaseline = ACXBaseline;
  if (typeof module !== "undefined" && module.exports) module.exports = ACXBaseline;
})(typeof window !== "undefined" ? window : globalThis);
