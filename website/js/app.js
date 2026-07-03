/*
 * app.js — bootstrap, hash router, and multi-file upload for the Path Explorer.
 *
 * Owns window.ACX = { dataset, reload(records), route() }. Does not touch the DOM ids
 * belonging to viewer.js/dashboard.js beyond what SPEC.md assigns to app.js (data-bar +
 * upload panel + view/tab switching). Never reimplements data.js's parse/merge/decode logic.
 */
(function () {
  "use strict";

  var VIEW_NAMES = ["solutions", "analytics", "baseline", "comparison", "about"];
  var SAMPLE_DIR = "sample-data/";

  var ACX = { dataset: null, reload: reload, route: route };
  window.ACX = ACX;

  // ---- data summary / status dot -------------------------------------------------

  function setStatus(text, colorVar) {
    var summaryEl = document.getElementById("data-summary");
    var dotEl = document.getElementById("data-dot");
    if (summaryEl) summaryEl.textContent = text;
    if (dotEl) dotEl.style.backgroundColor = "var(" + colorVar + ")";
  }

  // ---- dataset (re)build -----------------------------------------------------------

  /** Rebuild the dataset from a flat list of raw records and re-render both views. */
  function reload(records) {
    var dataset = ACXData.buildDataset(records || []);
    ACX.dataset = dataset;
    if (window.ACXViewer) ACXViewer.render(dataset);
    if (window.ACXDashboard) ACXDashboard.render(dataset);
    if (window.ACXBaseline) ACXBaseline.render(dataset);
    if (window.ACXComparison) ACXComparison.render(dataset);
    return dataset;
  }

  // ---- router ------------------------------------------------------------------

  function route() {
    var raw = (location.hash || "").replace(/^#\/?/, "");
    var name = VIEW_NAMES.indexOf(raw) !== -1 ? raw : "solutions";

    var views = document.querySelectorAll(".view[id^='view-']");
    for (var i = 0; i < views.length; i++) {
      var v = views[i];
      v.classList.toggle("hidden", v.id !== "view-" + name);
    }

    var tabs = document.querySelectorAll("#nav-tabs .tab");
    for (var j = 0; j < tabs.length; j++) {
      var t = tabs[j];
      t.classList.toggle("active", t.getAttribute("data-view") === name);
    }

    if (name === "analytics" && window.ACXDashboard && typeof ACXDashboard.onShow === "function") {
      ACXDashboard.onShow();
    }
    if (name === "baseline" && window.ACXBaseline && typeof ACXBaseline.onShow === "function") {
      ACXBaseline.onShow();
    }
    if (name === "comparison" && window.ACXComparison && typeof ACXComparison.onShow === "function") {
      ACXComparison.onShow();
    }
  }

  // ---- sample data loading (initial load + "reset to sample") --------------------

  function fetchText(url) {
    return fetch(url).then(function (resp) {
      if (!resp.ok) throw new Error(url + " -> HTTP " + resp.status);
      return resp.text();
    });
  }

  function loadSample() {
    return fetch(SAMPLE_DIR + "manifest.json")
      .then(function (resp) {
        if (!resp.ok) throw new Error("manifest.json -> HTTP " + resp.status);
        return resp.json();
      })
      .then(function (manifest) {
        var label = (manifest && manifest.label) || "Sample data";
        var files = (manifest && manifest.files) || [];
        return Promise.all(files.map(function (f) { return fetchText(SAMPLE_DIR + f); }))
          .then(function (texts) {
            var records = [];
            for (var i = 0; i < texts.length; i++) records = records.concat(ACXData.parseJsonl(texts[i]));
            var dataset = reload(records);
            setStatus(label + " · " + dataset.counts.withPath + " solutions", "--ok");
          });
      })
      .catch(function (err) {
        reload([]); // keep the views (empty-state rendered) instead of a blank page
        setStatus("Could not load sample data (" + (err && err.message ? err.message : err) + ")", "--err");
      });
  }

  // ---- upload (multi-file) --------------------------------------------------------

  function readFilesAsText(fileList) {
    var files = Array.prototype.slice.call(fileList || []);
    return Promise.all(files.map(function (f) {
      return typeof f.text === "function" ? f.text() : new Promise(function (resolve, reject) {
        var reader = new FileReader();
        reader.onload = function () { resolve(reader.result); };
        reader.onerror = function () { reject(reader.error); };
        reader.readAsText(f);
      });
    })).then(function (texts) { return { files: files, texts: texts }; });
  }

  function handleUpload(fileList) {
    var files = Array.prototype.slice.call(fileList || []);
    if (!files.length) return;
    var hintEl = document.getElementById("upload-hint");
    readFilesAsText(files)
      .then(function (result) {
        var records = [];
        for (var i = 0; i < result.texts.length; i++) records = records.concat(ACXData.parseJsonl(result.texts[i]));
        var dataset = reload(records);
        setStatus("Custom · " + dataset.counts.withPath + " solutions", "--accent-2");
        if (hintEl) {
          var names = files.map(function (f) { return f.name; }).join(", ");
          hintEl.textContent = "Loaded " + files.length + " file(s) (" + names + ") — " +
            dataset.counts.total + " records merged.";
        }
      })
      .catch(function (err) {
        setStatus("Could not read uploaded files (" + (err && err.message ? err.message : err) + ")", "--err");
      })
      .finally(function () {
        var fileInput = document.getElementById("file-input");
        if (fileInput) fileInput.value = ""; // allow re-selecting the same file(s) later
      });
  }

  function wireUpload() {
    var toggleBtn = document.getElementById("toggle-upload");
    var panel = document.getElementById("upload-panel");
    var dropzone = document.getElementById("dropzone");
    var fileInput = document.getElementById("file-input");
    var resetBtn = document.getElementById("reset-sample");

    if (toggleBtn && panel) {
      toggleBtn.addEventListener("click", function () { panel.classList.toggle("hidden"); });
    }
    if (fileInput) {
      fileInput.addEventListener("change", function (e) { handleUpload(e.target.files); });
    }
    if (dropzone) {
      dropzone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropzone.classList.add("dragover");
      });
      dropzone.addEventListener("dragleave", function () { dropzone.classList.remove("dragover"); });
      dropzone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer) handleUpload(e.dataTransfer.files);
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        var hintEl = document.getElementById("upload-hint");
        if (hintEl) hintEl.textContent = "Select both streams at once — they merge automatically.";
        loadSample();
      });
    }
  }

  // ---- theme (light / dark) ------------------------------------------------------
  // The document's data-theme is set pre-paint by a tiny inline script in <head>
  // (from localStorage) to avoid a flash; here we sync the button and handle toggles.

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("acx-theme", theme); } catch (e) { /* private mode */ }
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var dark = theme === "dark";
      btn.textContent = dark ? "☀ Light" : "☾ Dark";
      btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    }
    // Chart chrome colors are read from CSS vars at render time -> redraw to recolor.
    if (ACX.dataset) {
      if (window.ACXDashboard) ACXDashboard.render(ACX.dataset);
      if (window.ACXBaseline) ACXBaseline.render(ACX.dataset);
      if (window.ACXComparison) ACXComparison.render(ACX.dataset);
    }
  }

  function wireTheme() {
    applyTheme(currentTheme());
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  }

  // ---- bootstrap ------------------------------------------------------------------

  document.addEventListener("DOMContentLoaded", function () {
    if (window.ACXViewer) ACXViewer.init();
    if (window.ACXDashboard) ACXDashboard.init();
    if (window.ACXBaseline) ACXBaseline.init();
    if (window.ACXComparison) ACXComparison.init();
    wireUpload();
    wireTheme();
    window.addEventListener("hashchange", route);

    loadSample().finally(function () { route(); });
  });
})();
