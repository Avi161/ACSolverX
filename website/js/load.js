/*
 * load.js — file://-safe sample-data loader for the Path Explorer.
 *
 * fetch() is blocked on file://; offline_bundle.js (built by tools/build_offline_bundle.py)
 * is injected via a dynamic <script> tag instead. HTTP serving keeps using fetch().
 */
(function (global) {
  "use strict";

  var BUNDLE_URL = "sample-data/offline_bundle.js?v=4";
  var bundlePromise = null;
  var cachedBundle = null;

  function isFileProtocol() {
    return global.location && global.location.protocol === "file:";
  }

  function loadOfflineBundle() {
    if (cachedBundle) return Promise.resolve(cachedBundle);
    if (bundlePromise) return bundlePromise;

    bundlePromise = new Promise(function (resolve, reject) {
      var prev = document.getElementById("acx-offline-bundle");
      if (prev) prev.remove();
      delete global.__ACX_OFFLINE__;

      var s = document.createElement("script");
      s.id = "acx-offline-bundle";
      s.src = BUNDLE_URL;
      s.onload = function () {
        var b = global.__ACX_OFFLINE__;
        delete global.__ACX_OFFLINE__;
        if (!b || !Array.isArray(b.records)) {
          reject(new Error("offline_bundle.js missing records — run website/tools/build_offline_bundle.py"));
          return;
        }
        cachedBundle = b;
        resolve(b);
      };
      s.onerror = function () {
        reject(new Error("failed to load " + BUNDLE_URL + " — run website/tools/build_offline_bundle.py"));
      };
      document.head.appendChild(s);
    });

    return bundlePromise;
  }

  function getCachedOfflineBundle() {
    return cachedBundle;
  }

  global.ACXLoad = {
    isFileProtocol: isFileProtocol,
    loadOfflineBundle: loadOfflineBundle,
    getCachedOfflineBundle: getCachedOfflineBundle,
  };
})(window);
