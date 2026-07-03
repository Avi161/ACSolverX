/*
 * charts.js — pure SVG chart renderers for the AC-SolverX Path Explorer.
 *
 * window.ACXCharts = { stackedBar(el, spec), histogram(el, bins, opts) }
 *
 * Both functions are PURE: given a container element and a plain-data spec they set
 * el.innerHTML to a self-contained inline SVG and return. No module-level state, no
 * DOM measurement (clientWidth etc.) — the viewBox is fixed so charts render correctly
 * even while their view (`#view-analytics`) is `.hidden` (display:none has zero layout
 * size, which would break anything that measured the container).
 */
(function (global) {
  "use strict";

  // ---- shared layout constants ---------------------------------------------------
  var VB_W = 640, VB_H = 360;

  // Dark-theme chrome tokens (see website/SPEC.md "Design system"). Chart chrome
  // (axes/gridlines/tick text) is not data, so these are fixed here rather than
  // threaded through every call site.
  var COLOR_BORDER = "#243044";   // --border   : axis lines + gridlines
  var COLOR_TICK = "#9fb0c6";     // --text-dim : tick + axis labels
  var COLOR_MUTED = "#6b7c93";    // --muted    : "No data" note
  var COLOR_TEXT = "#e6edf6";     // --text     : value labels, legend text
  var COLOR_INK = "#0b1220";      // fixed dark ink for labels drawn ON TOP of a bright fill (both themes)
  var FONT = "system-ui,-apple-system,'Segoe UI',Roboto,sans-serif";

  // Chart chrome follows the active (light/dark) theme by reading :root CSS vars at
  // render time; bar/segment fills are supplied by the caller and stay as-is.
  function cssVar(name, fallback) {
    try {
      var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      return v || fallback;
    } catch (e) { return fallback; }
  }
  function refreshTheme() {
    COLOR_BORDER = cssVar("--border", "#243044");
    COLOR_TICK = cssVar("--text-dim", "#9fb0c6");
    COLOR_MUTED = cssVar("--muted", "#6b7c93");
    COLOR_TEXT = cssVar("--text", "#e6edf6");
  }

  // ---- small helpers ---------------------------------------------------------------
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /** Round a positive max up to a "nice" number (1/2/5 * 10^k) for gridlines. */
  function niceMax(v) {
    if (!(v > 0)) return 1;
    var exp = Math.floor(Math.log(v) / Math.LN10);
    var base = Math.pow(10, exp);
    var f = v / base;
    var niceF = f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10;
    return niceF * base;
  }

  /** Compact numeric formatting for axis/tick labels. */
  function fmtNum(n) {
    if (n == null || isNaN(n)) return "";
    if (Number.isInteger(n)) return String(n);
    var r = Math.round(n * 100) / 100;
    return String(r);
  }

  function svgOpen(w, h) {
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" width="100%" height="auto" ' +
      'preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" ' +
      'font-family="' + FONT + '">';
  }

  function emptyChart(w, h) {
    return svgOpen(w, h) +
      '<text x="' + (w / 2) + '" y="' + (h / 2) + '" text-anchor="middle" ' +
      'dominant-baseline="middle" fill="' + COLOR_MUTED + '" font-size="14">No data</text>' +
      '</svg>';
  }

  function setSvg(el, markup) {
    if (!el) return;
    el.innerHTML = markup;
  }

  // ---- stackedBar -------------------------------------------------------------------
  /**
   * spec = { categories:[{label, color?, segments:[{key,value,color,title}]}],
   *          legend:[{key,color,label}], yLabel }
   * One bar per category, segments stacked bottom-up in the order given. `color` on a
   * category is optional and only tints its x-axis label (e.g. an identity color) —
   * it never affects segment fills, which always come from `segments[].color`.
   */
  function stackedBar(el, spec) {
    refreshTheme();
    spec = spec || {};
    var categories = Array.isArray(spec.categories) ? spec.categories : [];
    var legend = Array.isArray(spec.legend) ? spec.legend : [];
    var yLabel = spec.yLabel || "";

    var totals = categories.map(function (c) {
      var segs = Array.isArray(c.segments) ? c.segments : [];
      var sum = 0;
      for (var i = 0; i < segs.length; i++) sum += (segs[i].value || 0);
      return sum;
    });
    var grandTotal = totals.reduce(function (a, b) { return a + b; }, 0);

    if (categories.length === 0 || grandTotal <= 0) {
      setSvg(el, emptyChart(VB_W, VB_H));
      return;
    }

    var legendH = legend.length ? 30 : 0;
    var margin = { top: 16 + legendH, right: 20, bottom: 54, left: 56 };
    var plotW = VB_W - margin.left - margin.right;
    var plotH = VB_H - margin.top - margin.bottom;

    var maxTotal = niceMax(Math.max.apply(null, totals.concat([1])));
    var yTickCount = 5;

    var n = categories.length;
    var bandW = plotW / n;
    var barW = Math.max(8, Math.min(72, bandW * 0.55));

    var parts = [];
    parts.push(svgOpen(VB_W, VB_H));

    // legend (top)
    if (legend.length) {
      var lx = margin.left;
      var ly = 14;
      for (var li = 0; li < legend.length; li++) {
        var lg = legend[li];
        parts.push('<rect x="' + lx + '" y="' + (ly - 9) + '" width="12" height="12" rx="2" fill="' + esc(lg.color) + '"></rect>');
        parts.push('<text x="' + (lx + 17) + '" y="' + ly + '" font-size="12" fill="' + COLOR_TEXT + '">' + esc(lg.label || lg.key) + '</text>');
        lx += 17 + (String(lg.label || lg.key).length * 6.5) + 22;
      }
    }

    // gridlines + y ticks
    for (var t = 0; t <= yTickCount; t++) {
      var yv = (maxTotal / yTickCount) * t;
      var y = margin.top + plotH - (yv / maxTotal) * plotH;
      parts.push('<line x1="' + margin.left + '" y1="' + y + '" x2="' + (margin.left + plotW) + '" y2="' + y +
        '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
      parts.push('<text x="' + (margin.left - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="11" fill="' + COLOR_TICK + '">' +
        fmtNum(Math.round(yv)) + '</text>');
    }
    // axis lines
    parts.push('<line x1="' + margin.left + '" y1="' + margin.top + '" x2="' + margin.left + '" y2="' + (margin.top + plotH) +
      '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
    parts.push('<line x1="' + margin.left + '" y1="' + (margin.top + plotH) + '" x2="' + (margin.left + plotW) + '" y2="' + (margin.top + plotH) +
      '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');

    // y axis label (rotated)
    if (yLabel) {
      var yaX = 14, yaY = margin.top + plotH / 2;
      parts.push('<text x="' + yaX + '" y="' + yaY + '" text-anchor="middle" font-size="11" fill="' + COLOR_TICK +
        '" transform="rotate(-90 ' + yaX + ' ' + yaY + ')">' + esc(yLabel) + '</text>');
    }

    // bars
    for (var ci = 0; ci < n; ci++) {
      var cat = categories[ci];
      var segs = Array.isArray(cat.segments) ? cat.segments : [];
      var cx = margin.left + bandW * ci + (bandW - barW) / 2;
      var yCursor = margin.top + plotH;
      var total = totals[ci];

      for (var si = 0; si < segs.length; si++) {
        var seg = segs[si];
        var val = seg.value || 0;
        var segH = maxTotal > 0 ? (val / maxTotal) * plotH : 0;
        var segY = yCursor - segH;
        var title = seg.title || ((seg.label || seg.key) + ": " + val);
        if (val > 0) {
          parts.push('<rect x="' + cx.toFixed(2) + '" y="' + segY.toFixed(2) + '" width="' + barW.toFixed(2) +
            '" height="' + Math.max(0, segH).toFixed(2) + '" fill="' + esc(seg.color) + '" rx="2">' +
            '<title>' + esc(cat.label) + ' — ' + esc(title) + '</title></rect>');
          // inline segment value label if tall enough to hold text — dark ink reads reliably
          // against the bright/mid-tone status fills (--ok/--err/etc) this draws on top of.
          if (segH >= 16) {
            parts.push('<text x="' + (cx + barW / 2).toFixed(2) + '" y="' + (segY + segH / 2 + 4).toFixed(2) +
              '" text-anchor="middle" font-size="10" fill="' + COLOR_INK + '">' + fmtNum(val) + '</text>');
          }
        }
        yCursor = segY;
      }

      // total value label above the bar
      var topY = margin.top + plotH - (total / maxTotal) * plotH;
      parts.push('<text x="' + (cx + barW / 2).toFixed(2) + '" y="' + (topY - 6).toFixed(2) +
        '" text-anchor="middle" font-size="11" fill="' + COLOR_TEXT + '">' + fmtNum(total) + '</text>');

      // category label (optional per-category color, e.g. arm identity color)
      parts.push('<text x="' + (margin.left + bandW * ci + bandW / 2).toFixed(2) + '" y="' + (margin.top + plotH + 20) +
        '" text-anchor="middle" font-size="11" fill="' + esc(cat.color || COLOR_TICK) + '">' + esc(cat.label) + '</text>');
    }

    parts.push('</svg>');
    setSvg(el, parts.join(""));
  }

  // ---- histogram --------------------------------------------------------------------
  /**
   * bins = [{x0, x1, count}] (see ACXData.histogram). opts = { color, xLabel, yLabel,
   * xTickFormat(x) }.
   */
  function histogram(el, bins, opts) {
    refreshTheme();
    opts = opts || {};
    bins = Array.isArray(bins) ? bins : [];
    var color = opts.color || COLOR_TICK;
    var xLabel = opts.xLabel || "";
    var yLabel = opts.yLabel || "";
    var xTickFormat = typeof opts.xTickFormat === "function" ? opts.xTickFormat : fmtNum;

    var maxCount = 0;
    for (var i = 0; i < bins.length; i++) if (bins[i].count > maxCount) maxCount = bins[i].count;

    if (bins.length === 0 || maxCount <= 0) {
      setSvg(el, emptyChart(VB_W, VB_H));
      return;
    }

    var margin = { top: 16, right: 20, bottom: 56, left: 56 };
    var plotW = VB_W - margin.left - margin.right;
    var plotH = VB_H - margin.top - margin.bottom;

    var niceCount = niceMax(maxCount);
    var yTickCount = 5;
    var n = bins.length;
    var bandW = plotW / n;
    var barW = Math.max(1, bandW - 2); // 2px gap between adjacent bars

    var parts = [];
    parts.push(svgOpen(VB_W, VB_H));

    // gridlines + y ticks
    for (var t = 0; t <= yTickCount; t++) {
      var yv = (niceCount / yTickCount) * t;
      var y = margin.top + plotH - (yv / niceCount) * plotH;
      parts.push('<line x1="' + margin.left + '" y1="' + y + '" x2="' + (margin.left + plotW) + '" y2="' + y +
        '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
      parts.push('<text x="' + (margin.left - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="11" fill="' + COLOR_TICK + '">' +
        fmtNum(Math.round(yv)) + '</text>');
    }
    // axis lines
    parts.push('<line x1="' + margin.left + '" y1="' + margin.top + '" x2="' + margin.left + '" y2="' + (margin.top + plotH) +
      '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
    parts.push('<line x1="' + margin.left + '" y1="' + (margin.top + plotH) + '" x2="' + (margin.left + plotW) + '" y2="' + (margin.top + plotH) +
      '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');

    if (yLabel) {
      var yaX = 14, yaY = margin.top + plotH / 2;
      parts.push('<text x="' + yaX + '" y="' + yaY + '" text-anchor="middle" font-size="11" fill="' + COLOR_TICK +
        '" transform="rotate(-90 ' + yaX + ' ' + yaY + ')">' + esc(yLabel) + '</text>');
    }

    // bars + x tick labels (thinned so labels don't overlap)
    var maxLabels = 10;
    var labelStride = Math.max(1, Math.ceil(n / maxLabels));
    // Value labels are shorter than x-tick labels (bare counts) but still need >=~16px of
    // band width apiece, or many-bin histograms (e.g. binSize 1 over 1..30) print a wall of
    // overlapping numbers. The <title> tooltip always carries the exact count regardless.
    var valueLabelStride = Math.max(1, Math.ceil(16 / bandW));

    for (var bi = 0; bi < n; bi++) {
      var b = bins[bi];
      var bx = margin.left + bandW * bi + (bandW - barW) / 2;
      var h = (b.count / niceCount) * plotH;
      var by = margin.top + plotH - h;
      var title = xTickFormat(b.x0) + "–" + xTickFormat(b.x1) + ": " + b.count;
      if (b.count > 0) {
        parts.push('<rect x="' + bx.toFixed(2) + '" y="' + by.toFixed(2) + '" width="' + barW.toFixed(2) +
          '" height="' + Math.max(0, h).toFixed(2) + '" fill="' + esc(color) + '" rx="2">' +
          '<title>' + esc(title) + '</title></rect>');
        if (bi % valueLabelStride === 0 || bi === n - 1) {
          parts.push('<text x="' + (bx + barW / 2).toFixed(2) + '" y="' + (by - 5).toFixed(2) +
            '" text-anchor="middle" font-size="10" fill="' + COLOR_TEXT + '">' + fmtNum(b.count) + '</text>');
        }
      } else {
        // still carry a tooltip anchor for empty bins so hovering the axis is not dead
        parts.push('<rect x="' + bx.toFixed(2) + '" y="' + (margin.top + plotH - 1) + '" width="' + barW.toFixed(2) +
          '" height="1" fill="transparent"><title>' + esc(title) + '</title></rect>');
      }
      if (bi % labelStride === 0 || bi === n - 1) {
        parts.push('<text x="' + (margin.left + bandW * bi + bandW / 2).toFixed(2) + '" y="' + (margin.top + plotH + 18) +
          '" text-anchor="middle" font-size="10" fill="' + COLOR_TICK + '">' + esc(xTickFormat(b.x0)) + '</text>');
      }
    }

    if (xLabel) {
      parts.push('<text x="' + (margin.left + plotW / 2) + '" y="' + (VB_H - 8) +
        '" text-anchor="middle" font-size="11" fill="' + COLOR_TICK + '">' + esc(xLabel) + '</text>');
    }

    parts.push('</svg>');
    setSvg(el, parts.join(""));
  }

  // ---- scatter ----------------------------------------------------------------------
  /** Compact tick label for large values: 1200 -> "1.2k", 34000 -> "34k". */
  function fmtCompact(n) {
    n = Math.round(n);
    if (n >= 1e6) return (Math.round(n / 1e5) / 10) + "M";
    if (n >= 1e3) return (Math.round(n / 100) / 10) + "k";
    return String(n);
  }

  /**
   * scatter(el, points, opts) — one dot per point on a SHARED square domain across both axes,
   * so the y=x diagonal is meaningful (used for "baseline vs arm nodes explored": a point below
   * the diagonal = the arm was cheaper). points = [{x, y, title?, color?}].
   * opts = { xLabel, yLabel, color, log (log10 both axes; default false), diagonal (default true) }.
   */
  function scatter(el, points, opts) {
    refreshTheme();
    opts = opts || {};
    points = Array.isArray(points) ? points : [];
    var color = opts.color || COLOR_TICK;
    var xLabel = opts.xLabel || "", yLabel = opts.yLabel || "";
    var useLog = !!opts.log;
    var drawDiag = opts.diagonal !== false;

    var pts = points.filter(function (p) {
      return p && p.x != null && p.y != null && !isNaN(p.x) && !isNaN(p.y);
    });
    if (pts.length === 0) { setSvg(el, emptyChart(VB_W, VB_H)); return; }

    var margin = { top: 16, right: 20, bottom: 56, left: 60 };
    var plotW = VB_W - margin.left - margin.right;
    var plotH = VB_H - margin.top - margin.bottom;

    // shared domain over ALL x and y values (square) so the diagonal is the identity line
    var all = [];
    for (var i = 0; i < pts.length; i++) { all.push(pts[i].x, pts[i].y); }
    var vmin = Math.min.apply(null, all), vmax = Math.max.apply(null, all);
    var dmin, dmax;
    if (useLog) {
      dmin = Math.log(Math.max(1, vmin)) / Math.LN10;
      dmax = Math.log(Math.max(10, vmax)) / Math.LN10;
      if (dmax <= dmin) dmax = dmin + 1;
    } else {
      dmin = 0; dmax = niceMax(vmax);
    }
    function tv(v) { return useLog ? Math.log(Math.max(1, v)) / Math.LN10 : v; }
    function px(v) { return margin.left + (tv(v) - dmin) / (dmax - dmin) * plotW; }
    function py(v) { return margin.top + plotH - (tv(v) - dmin) / (dmax - dmin) * plotH; }

    var parts = [svgOpen(VB_W, VB_H)];
    var ticks = 5;
    for (var t = 0; t <= ticks; t++) {
      var frac = t / ticks;
      var gx = margin.left + frac * plotW;
      var gy = margin.top + plotH - frac * plotH;
      parts.push('<line x1="' + margin.left + '" y1="' + gy + '" x2="' + (margin.left + plotW) + '" y2="' + gy +
        '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
      parts.push('<line x1="' + gx + '" y1="' + margin.top + '" x2="' + gx + '" y2="' + (margin.top + plotH) +
        '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
      var val = useLog ? Math.pow(10, dmin + frac * (dmax - dmin)) : (dmin + frac * (dmax - dmin));
      parts.push('<text x="' + (margin.left - 8) + '" y="' + (gy + 4) + '" text-anchor="end" font-size="10" fill="' + COLOR_TICK + '">' + esc(fmtCompact(val)) + '</text>');
      parts.push('<text x="' + gx + '" y="' + (margin.top + plotH + 16) + '" text-anchor="middle" font-size="10" fill="' + COLOR_TICK + '">' + esc(fmtCompact(val)) + '</text>');
    }
    // axis lines
    parts.push('<line x1="' + margin.left + '" y1="' + margin.top + '" x2="' + margin.left + '" y2="' + (margin.top + plotH) + '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
    parts.push('<line x1="' + margin.left + '" y1="' + (margin.top + plotH) + '" x2="' + (margin.left + plotW) + '" y2="' + (margin.top + plotH) + '" stroke="' + COLOR_BORDER + '" stroke-width="1"></line>');
    // y=x diagonal (bottom-left to top-right of the square domain)
    if (drawDiag) {
      parts.push('<line x1="' + margin.left + '" y1="' + (margin.top + plotH) + '" x2="' + (margin.left + plotW) + '" y2="' + margin.top +
        '" stroke="' + COLOR_TICK + '" stroke-width="1" stroke-dasharray="4 4" opacity="0.6"><title>y = x (equal cost)</title></line>');
    }
    // points
    for (var pi = 0; pi < pts.length; pi++) {
      var p = pts[pi];
      var title = p.title || (fmtCompact(p.x) + " vs " + fmtCompact(p.y));
      parts.push('<circle cx="' + px(p.x).toFixed(1) + '" cy="' + py(p.y).toFixed(1) + '" r="3" fill="' + esc(p.color || color) +
        '" opacity="0.75"><title>' + esc(title) + '</title></circle>');
    }
    // axis labels
    if (xLabel) parts.push('<text x="' + (margin.left + plotW / 2) + '" y="' + (VB_H - 6) + '" text-anchor="middle" font-size="11" fill="' + COLOR_TICK + '">' + esc(xLabel) + '</text>');
    if (yLabel) {
      var yaX = 14, yaY = margin.top + plotH / 2;
      parts.push('<text x="' + yaX + '" y="' + yaY + '" text-anchor="middle" font-size="11" fill="' + COLOR_TICK +
        '" transform="rotate(-90 ' + yaX + ' ' + yaY + ')">' + esc(yLabel) + '</text>');
    }
    parts.push('</svg>');
    setSvg(el, parts.join(""));
  }

  var ACXCharts = { stackedBar: stackedBar, histogram: histogram, scatter: scatter };

  global.ACXCharts = ACXCharts;
  if (typeof module !== "undefined" && module.exports) module.exports = ACXCharts;
})(typeof window !== "undefined" ? window : globalThis);
