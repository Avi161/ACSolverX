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
 * Budget note: baseline and all four z ∈ {r₁,r₂,x,y} arms are the same matched 500k run — the
 * per-idx nodes-explored comparison is on presentations BOTH solve, where nodes-to-solve is
 * budget-independent (both finish well under budget).
 */
(function (global) {
  "use strict";

  var ACXData = global.ACXData;
  var ACXCharts = global.ACXCharts;

  var DATASET = "1190MS";
  // Arm order/colors and median come from the shared canonical maps (ACXData/ACXCharts).
  function cssVar(name, fallback) {
    return (ACXCharts && ACXCharts.cssVar) ? ACXCharts.cssVar(name, fallback) : fallback;
  }
  function okColor() { return cssVar("--ok", "#35d07f"); }
  function errColor() { return cssVar("--err", "#ff6b6b"); }
  function armColor(a) { return ACXCharts.armColor(a); }
  var armSort = ACXData.armSort;
  function armLabel(a) { return a === "baseline" ? "baseline (2-gen)" : ((ACXData && ACXData.armSymbol) ? ACXData.armSymbol(a) : a); }
  // short form for chart category axes (the long form clips when labels are rotated)
  function armAxisLabel(a) { return a === "baseline" ? "baseline" : armLabel(a); }

  var dom = null, lastDataset = null, initialized = false;

  function q(id) { return document.getElementById(id); }

  function cacheDom() {
    dom = {
      stats: q("comparison-stats"),
      note: q("comparison-note"),
      verdict: q("cmp-verdict"),
      wordRanking: q("cmp-word-ranking"),
      chartOverlap: q("chart-cmp-overlap"),
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

  var median = ACXData.median;
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

  // ---- the verdict: data-derived answers to the headline questions -----------------
  // Every number here is set algebra over the loaded data (ACXData.armSolveSets) —
  // nothing is hardcoded, so uploaded runs rewrite the verdict.
  function drawVerdict(arms) {
    if (!dom.verdict) return;
    var zArms = arms.filter(function (a) { return a !== "baseline"; });
    var hasBaseline = arms.indexOf("baseline") !== -1;
    if (!zArms.length) {
      dom.verdict.textContent = "";
      dom.verdict.classList.add("hidden");
      if (dom.wordRanking) dom.wordRanking.textContent = "";
      if (dom.chartOverlap) dom.chartOverlap.textContent = "";
      return;
    }
    dom.verdict.classList.remove("hidden");

    var A = ACXData.armSolveSets(lastDataset, { dataset: DATASET, subset: "original", arms: zArms });
    var B = hasBaseline
      ? ACXData.armSolveSets(lastDataset, { dataset: DATASET, subset: "original", arms: ["baseline"] })
      : null;
    var baseSet = B ? B.sets.baseline : null;
    var zOnly = 0, baseOnly = 0;
    if (baseSet) {
      A.union.forEach(function (v) { if (!baseSet.has(v)) zOnly++; });
      baseSet.forEach(function (v) { if (!A.union.has(v)) baseOnly++; });
    }
    var ranked = zArms.slice().sort(function (a, b) { return A.sets[b].size - A.sets[a].size; });
    var best = ranked[0];
    // the hard set: what the reps say (computed, not asserted)
    var reps = ACXData.groupStats(lastDataset, { dataset: "ms_reps_unsolved" });

    function strong(v) { return "<strong>" + v + "</strong>"; }
    var rankTxt = ranked.map(function (a, i) {
      var t = armLabel(a) + " (" + A.sets[a].size + ")";
      return i === 0 ? strong(t) : t;
    }).join(", ");
    var parts = [];
    parts.push("<h3>Does <code>z = w</code> help?</h3>");
    var s1 = "On the " + strong(A.scopeTotal) + " directly-searched presentations (the original set): ";
    if (baseSet) s1 += "the 2-generator baseline solves " + strong(baseSet.size) + "; ";
    s1 += "the " + zArms.length + " z-words together solve " + strong(A.union.size) +
      " (" + strong(A.byK[0]) + " solved by none of them" +
      (A.byK[zArms.length] != null ? ", " + strong(A.byK[zArms.length]) + " by all " + zArms.length : "") + ").";
    parts.push("<p>" + s1 + "</p>");
    parts.push("<p>Best single word: " + rankTxt + ".</p>");
    if (baseSet) {
      var verdictLine = (zOnly === 0 && baseOnly > 0)
        ? "Every z-word solve is also a baseline solve, and " + strong(baseOnly) +
          " baseline solves have no z-word solve — on this easy set <em>z = w does not yet beat the baseline</em>."
        : "z = w uniquely solves " + strong(zOnly) + " the baseline cannot; the baseline uniquely solves " +
          strong(baseOnly) + "." + (zOnly > 0 ? " <em>z = w adds coverage the baseline lacks.</em>" : "");
      parts.push("<p>" + verdictLine + "</p>");
    }
    if (reps.total > 0) {
      parts.push("<p>The hard set was searched only via its " + strong(reps.total) + " class representatives: " +
        strong(reps.solved) + " solved, " + strong(reps.unsolvedSearched) + " budget-exhausted. " +
        "A baseline-vs-z comparison there is structurally out of scope for this bundle — the 2-generator " +
        "baseline was never run on the hard set. Cracking those classes is the open question.</p>");
    }
    dom.verdict.innerHTML = parts.join("");

    // ---- per-word ranking bars (accessible HTML, not SVG) ----
    if (dom.wordRanking) {
      var rows = ranked.map(function (a) { return { arm: a, n: A.sets[a].size, cls: "" }; });
      if (baseSet) rows.push({ arm: "baseline", n: baseSet.size, cls: " ranking-baseline" });
      rows.sort(function (r, s) { return s.n - r.n; });
      var maxN = Math.max.apply(null, rows.map(function (r) { return r.n; }).concat([1]));
      dom.wordRanking.innerHTML = rows.map(function (r) {
        var pctW = Math.max(2, Math.round(100 * r.n / maxN));
        return '<div class="ranking-row' + r.cls + '" role="img" aria-label="' +
          armLabel(r.arm) + " solved " + r.n + " of " + A.scopeTotal + '">' +
          '<span class="ranking-label">' + armLabel(r.arm) + "</span>" +
          '<span class="ranking-track"><span class="ranking-bar" style="width:' + pctW +
          '%;background:' + armColor(r.arm) + '"></span></span>' +
          '<span class="ranking-value">' + r.n + "</span></div>";
      }).join("");
    }

    // ---- solved-by-exactly-k chart ----
    if (dom.chartOverlap) {
      var C = { ok: okColor(), err: errColor() };
      ACXCharts.stackedBar(dom.chartOverlap, {
        categories: A.byK.map(function (n, k) {
          return {
            label: "k = " + k,
            segments: [{
              key: "n", value: n, color: k === 0 ? C.err : C.ok,
              title: n + " solved by exactly " + k + " word" + (k === 1 ? "" : "s"),
            }],
          };
        }),
        yLabel: "presentations",
        title: "Solved by exactly k of the z-words",
        desc: "How many of the original presentations are solved by exactly k of the four words; k=0 = solved by none.",
      });
    }
  }

  function draw() {
    if (!dom || !lastDataset) return;
    var m = armMap();
    var arms = armsPresent(m);

    if (dom.note) {
      var hasBaseline = arms.indexOf("baseline") !== -1;
      dom.note.textContent = hasBaseline
        ? "Head-to-head on the ORIGINAL 640 of MS(1190) — the only presentations both sides searched directly. Baseline and every z ∈ {r₁, r₂, x, y} arm are the same matched 500k run; node/path comparisons are over presentations BOTH arms solve, where they are budget-independent."
        : "No baseline loaded yet — showing z=w arms only. Run the baseline sweep + rebuild the bundle to enable the baseline comparison.";
    }

    drawVerdict(arms);

    // ---- coverage: solved/unsolved per arm ----
    var covCats = arms.map(function (a) {
      var its = m[a], s = its.filter(function (i) { return i.solved; }).length;
      return {
        label: armAxisLabel(a), color: armColor(a),
        segments: [
          { key: "solved", value: s, color: okColor(), title: "solved: " + s },
          { key: "unsolved", value: its.length - s, color: errColor(), title: "unsolved: " + (its.length - s) },
        ],
      };
    });
    ACXCharts.stackedBar(dom.chartCoverage, {
      categories: covCats,
      legend: [{ key: "s", color: okColor(), label: "Solved" }, { key: "u", color: errColor(), label: "Unsolved" }],
      yLabel: "presentations",
      title: "Coverage by arm on the original 640",
      desc: "Solved vs unsolved per arm, baseline and each z-word.",
    });

    // ---- median nodes per arm (solved) ----
    ACXCharts.stackedBar(dom.chartNodes, {
      categories: arms.map(function (a) {
        var med = median(m[a].filter(function (i) { return i.solved; }).map(nodesOf));
        return { label: armAxisLabel(a), color: armColor(a),
          segments: [{ key: "nodes", value: med || 0, color: armColor(a), title: "median nodes: " + (med == null ? "—" : med) }] };
      }),
      yLabel: "median nodes (solved)",
      title: "Median nodes explored per arm",
      desc: "Median search cost over each arm's solved presentations.",
    });

    // ---- median path length per arm (solved) ----
    ACXCharts.stackedBar(dom.chartPathlen, {
      categories: arms.map(function (a) {
        var med = median(m[a].filter(function (i) { return i.solved; }).map(pathOf));
        return { label: armAxisLabel(a), color: armColor(a),
          segments: [{ key: "plen", value: med || 0, color: armColor(a), title: "median path length: " + (med == null ? "—" : med) }] };
      }),
      yLabel: "median path length (solved)",
      title: "Median path length per arm",
      desc: "Median supermoves to trivialize over each arm's solved presentations.",
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
      color: armColor(selArm), log: true, diagonal: true,
      title: "Baseline vs arm nodes explored",
      desc: "One point per presentation both solve; below the diagonal the arm was cheaper.",
    });
    if (dom.scatterNote) {
      dom.scatterNote.textContent = pr.n
        ? (cheaper + " of " + pr.n + " cheaper under " + armLabel(selArm) + " (below the line) · median ratio " +
           (median(pr.nodeRatios) != null ? median(pr.nodeRatios).toFixed(2) + "×" : "—") + " (>1 = z=w explores more)")
        : "No presentations solved by both baseline and " + armLabel(selArm) + " yet.";
    }

    ACXCharts.scatter(dom.chartScatterPath, pr.pathPts, {
      xLabel: "baseline path length", yLabel: (armLabel(selArm) + " path length"),
      color: armColor(selArm), log: true, diagonal: true,
      title: "Baseline vs arm path length",
      desc: "One point per presentation both solve; below the diagonal the arm found a shorter path.",
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
      // Denominator from the loaded data, never a literal: the original-subset
      // presentation count (640 with the bundled registry).
      var origTotal = ACXData.groupStats(lastDataset, { dataset: DATASET, subset: "original" }).total;
      var zA = ACXData.armSolveSets(lastDataset, {
        dataset: DATASET, subset: "original",
        arms: arms.filter(function (a) { return a !== "baseline"; }),
      });
      var bestArm = zA.arms.slice().sort(function (a, b) { return zA.sets[b].size - zA.sets[a].size; })[0];
      var cards = [
        { label: "Baseline solved / " + (baseItems.length || origTotal || "—"), value: baseItems.length ? String(baseSolved) : "—" },
        { label: "z-words union solved / " + (zA.scopeTotal || "—"), value: zA.arms.length ? String(zA.union.size) : "—" },
        { label: "Best single word", value: bestArm ? armLabel(bestArm) + " (" + zA.sets[bestArm].size + ")" : "—" },
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
