/*
 * ak3.js — "AK(3) test" view for the AC-SolverX Path Explorer.
 *
 * window.ACXak3 = { init(), render(dataset), onShow() }
 *
 * Self-contained: fetches sample-data/ak3_test.json (the z=w word-choice sweep over AK(3), built by
 * website/tools/build_ak3_bundle.py) directly — it is NOT part of the main manifest/dataset pipeline,
 * because the AK(3) sweep is a word-choice study (a different shape from the presentation x arm
 * calibration the other tabs read). render(dataset) is therefore a no-op; the view redraws itself.
 *
 * Every record-derived string goes through ACXData.esc() before reaching an innerHTML sink.
 */
(function (global) {
  "use strict";

  var ACXData = global.ACXData;
  var ACXCharts = global.ACXCharts;
  var esc = (ACXData && ACXData.esc) ? ACXData.esc : function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };

  var BUNDLE_URL = "sample-data/ak3_test.json";
  var data = null;
  var initialized = false;
  var state = { form: "textbook", budget: "1000000" };
  var sort = { key: "mtl", dir: 1 };   // closest-to-trivial first
  var dom = null;

  function q(id) { return document.getElementById(id); }
  function cacheDom() {
    dom = {
      intro: q("ak3-intro"), banner: q("ak3-banner"), scope: q("ak3-scope"),
      form: q("ak3-form"), budget: q("ak3-budget"), stats: q("ak3-stats"),
      families: q("ak3-families"), table: q("ak3-table"), tableScope: q("ak3-table-scope"),
      chart: q("chart-ak3-mtl"),
    };
  }

  function key() { return state.form + "|" + state.budget; }
  function fmt(n) { return (n == null) ? "—" : Number(n).toLocaleString(); }

  // ---- draw -----------------------------------------------------------------------
  function draw() {
    if (!data || !dom) return;
    var k = key();
    var rows = (data.rows && data.rows[k]) || [];
    var sum = (data.summary && data.summary[k]) || { n: 0, solved: 0, exhausted: 0, best_mtl: null };
    var form = data.forms[state.form] || {};
    var trivial = data.trivial_len;

    if (dom.intro) dom.intro.textContent = data.note || "";

    // ---- headline banner: a solve is huge; otherwise state the plateau plainly -----
    var totalSolved = 0, totalRuns = 0;
    Object.keys(data.summary || {}).forEach(function (kk) {
      totalSolved += data.summary[kk].solved; totalRuns += data.summary[kk].n;
    });
    if (dom.banner) {
      if (totalSolved > 0) {
        var winners = [];
        Object.keys(data.rows).forEach(function (kk) {
          data.rows[kk].forEach(function (w) {
            if (w.solved) winners.push(esc(w.word) + " <span class=\"muted\">(" + esc(kk.split("|")[0]) + ")</span>");
          });
        });
        dom.banner.className = "ak3-banner ak3-solved";
        dom.banner.innerHTML = "<strong>🚨 AK(3) TRIVIALIZED</strong> by " + winners.length +
          " word choice(s): " + winners.slice(0, 8).join(", ") +
          " — verify the replayable path before believing it.";
      } else {
        dom.banner.className = "ak3-banner ak3-unsolved";
        dom.banner.innerHTML = "<strong>AK(3) not trivialized</strong> — " + totalSolved + " / " +
          totalRuns + " runs solved. The greedy search drives the total relator length down to a " +
          "<strong>plateau near " + (sum.best_mtl == null ? "?" : sum.best_mtl) + "</strong> (trivial = " +
          trivial + ") and gets stuck: the AK(3) “second hump.” Even the flagship theory words " +
          "(<code>xyx</code>, <code>yxy</code>, <code>x³</code>, <code>y⁴</code>, <code>wₖ</code>, " +
          "<code>w★</code>) fail at the full 1M-node budget.";
      }
    }

    // ---- scope line: which AK(3) form + relators -----------------------------------
    if (dom.scope) {
      dom.scope.innerHTML = esc(form.desc || "") +
        "  <span class=\"muted\">r₁=<code>" + esc(form.r1 || "") + "</code>, r₂=<code>" +
        esc(form.r2 || "") + "</code></span>";
    }

    // ---- stat cards ----------------------------------------------------------------
    if (dom.stats) {
      var cards = [
        { label: "Word choices", value: fmt(sum.n), sub: "z = w candidates tried" },
        { label: "Solved", value: String(sum.solved), cls: sum.solved ? "stat-ok" : "stat-muted",
          sub: sum.solved ? "AK(3) trivialized" : "none" },
        { label: "Exhausted budget", value: String(sum.exhausted), cls: "stat-err",
          sub: "ran out of nodes" },
        { label: "Closest to trivial", value: (sum.best_mtl == null ? "—" : String(sum.best_mtl)),
          cls: "stat-warn", sub: "min total length (trivial = " + trivial + ")" },
      ];
      dom.stats.innerHTML = cards.map(function (c) {
        return '<div class="stat-card' + (c.cls ? " " + c.cls : "") + '"><div class="stat-value">' +
          esc(c.value) + '</div><div class="stat-label">' + esc(c.label) + '</div>' +
          (c.sub ? '<div class="stat-sub">' + esc(c.sub) + '</div>' : "") + "</div>";
      }).join("");
    }

    // ---- family legend -------------------------------------------------------------
    if (dom.families) {
      var fams = data.families || {};
      var byFam = data.by_family || {};
      var order = Object.keys(fams).sort(function (a, b) { return fams[a].priority - fams[b].priority; });
      dom.families.innerHTML = "<h3>Word families <span class=\"muted\">(" +
        (data.n_words || "~95") + " unique words, grounded in the change-of-variables literature)</span></h3>" +
        '<div class="ak3-family-list">' + order.map(function (f) {
          return '<div class="ak3-family"><span class="tag tag-' + esc(f) + '">' + esc(f) +
            "</span> <span class=\"muted\">×" + (byFam[f] || 0) + "</span> " + esc(fams[f].desc) + "</div>";
        }).join("") + "</div>";
    }

    drawTable(rows, sum);
    drawChart(rows);
  }

  function drawTable(rows, sum) {
    if (!dom.table) return;
    if (dom.tableScope) {
      dom.tableScope.textContent = "(" + (data.forms[state.form] ? state.form : state.form) + " form · " +
        ((data.budget_labels && data.budget_labels[state.budget]) || state.budget + " nodes") +
        " · " + rows.length + " words · sorted by " + sort.key + ")";
    }
    var COLS = [
      { key: "word", label: "z = w", num: false },
      { key: "family", label: "family", num: false },
      { key: "z", label: "z-relator", num: false },
      { key: "mtl", label: "closest total len", num: true },
      { key: "nodes", label: "nodes", num: true },
      { key: "nps", label: "nodes/s", num: true },
      { key: "solved", label: "solved", num: true },
    ];
    var sorted = rows.slice().sort(function (a, b) {
      var av = a[sort.key], bv = b[sort.key];
      if (typeof av === "boolean") { av = av ? 1 : 0; bv = bv ? 1 : 0; }
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      if (av !== bv) return (av < bv ? -1 : 1) * sort.dir;
      return String(a.word) < String(b.word) ? -1 : 1;
    });
    var thead = "<thead><tr><th>#</th>" + COLS.map(function (c) {
      var mark = sort.key === c.key ? (sort.dir === -1 ? " ▾" : " ▴") : "";
      return '<th class="th-sort" data-sort="' + c.key + '">' + esc(c.label) + mark + "</th>";
    }).join("") + "</tr></thead>";
    var tbody = "<tbody>" + sorted.map(function (w, i) {
      var solvedCell = w.solved
        ? '<span class="ak3-ok">✓ len ' + esc(w.path_len) + "</span>"
        : '<span class="muted">—</span>';
      return "<tr" + (w.solved ? ' class="total-row"' : "") + "><td>" + (i + 1) +
        '</td><td><code>' + esc(w.word) + "</code></td><td><span class=\"tag tag-" + esc(w.family) +
        '">' + esc(w.family) + "</span></td><td><code>" + esc(w.z) + "</code></td><td>" +
        esc(w.mtl) + "</td><td>" + fmt(w.nodes) + "</td><td>" + fmt(w.nps) + "</td><td>" +
        solvedCell + "</td></tr>";
    }).join("") + "</tbody>";
    dom.table.innerHTML = thead + (sorted.length ? tbody
      : '<tbody><tr><td colspan="8">No runs recorded for this form/budget yet.</td></tr></tbody>');
  }

  function drawChart(rows) {
    if (!dom.chart || !ACXCharts || !ACXData || !ACXData.histogram) return;
    var vals = rows.map(function (w) { return w.mtl; }).filter(function (v) { return v != null; });
    var bins = ACXData.histogram(vals, 1);
    var color = (ACXCharts.cssVar ? ACXCharts.cssVar("--warn", "#ffb454") : "#ffb454");
    ACXCharts.histogram(dom.chart, bins, {
      color: color, xLabel: "smallest total relator length reached", yLabel: "word choices",
      title: "How close each word got",
      desc: "Trivial = " + (data ? data.trivial_len : 3) + "; a spike near 13 is the AK(3) plateau.",
    });
  }

  // ---- wiring ---------------------------------------------------------------------
  function wireSeg(el, attr, apply) {
    if (!el) return;
    el.addEventListener("click", function (e) {
      var btn = e.target.closest(".seg");
      if (!btn || !el.contains(btn)) return;
      var segs = el.querySelectorAll(".seg");
      for (var i = 0; i < segs.length; i++) segs[i].classList.toggle("active", segs[i] === btn);
      apply(btn.getAttribute(attr));
      draw();
    });
  }

  function wireTable() {
    if (!dom.table) return;
    dom.table.addEventListener("click", function (e) {
      var th = e.target.closest("th[data-sort]");
      if (!th) return;
      var k = th.getAttribute("data-sort");
      if (sort.key === k) sort.dir = -sort.dir;
      else { sort.key = k; sort.dir = (k === "word" || k === "family" || k === "z") ? 1 : (k === "mtl" ? 1 : -1); }
      draw();
    });
  }

  // ---- public API -----------------------------------------------------------------
  function init() {
    if (initialized) return;
    initialized = true;
    cacheDom();
    wireSeg(dom.form, "data-form", function (v) { state.form = v; });
    wireSeg(dom.budget, "data-budget", function (v) { state.budget = v; });
    wireTable();
    function onAk3(json) {
      if (!json) throw new Error("missing AK(3) bundle");
      data = json;
      draw();
    }
    function onAk3Err(err) {
      if (dom.banner) {
        dom.banner.className = "ak3-banner ak3-unsolved";
        dom.banner.textContent = "Could not load AK(3) results (" +
          (err && err.message ? err.message : err) + "). Run website/tools/build_ak3_bundle.py.";
      }
    }
    if (window.ACXLoad && ACXLoad.isFileProtocol()) {
      ACXLoad.loadOfflineBundle().then(function (b) { onAk3(b.ak3); }).catch(onAk3Err);
    } else {
      fetch(BUNDLE_URL)
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(onAk3)
        .catch(onAk3Err);
    }
  }

  function render() { /* self-contained: AK(3) data is fetched, not derived from the main dataset */ }
  function onShow() { if (data) draw(); }   // redraw so the chart sizes correctly when the tab shows

  global.ACXak3 = { init: init, render: render, onShow: onShow };
  if (typeof module !== "undefined" && module.exports) module.exports = global.ACXak3;
})(typeof window !== "undefined" ? window : globalThis);
