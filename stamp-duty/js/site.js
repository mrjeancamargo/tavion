// Shared helpers for the Stamp Duty app: ad units (up to two per page).
// The AdSense script itself is loaded site-wide by /assets/tavion.js.
(function () {
  // Paste AdSense ad unit slot IDs here once they are created (Ads > By ad unit in AdSense).
  var AD_SLOTS = {
    calculator: "",  // bottom of the calculator pages
    result: "",      // under the calculator result
    content: ""   // all other pages
  };

  function renderAd(el) {
    var slot = AD_SLOTS[el.getAttribute("data-slot") || "content"];
    var client = window.TAVION && window.TAVION.adsenseClient;
    if (!client || !slot) {
      if (/localhost|127\.0\.0\.1/.test(location.hostname)) {
        el.innerHTML = '<span class="ad-label">Advertisement</span><div class="ad-ph">Ad space</div>';
      } else {
        el.style.display = "none";
      }
      return;
    }
    el.innerHTML = '<span class="ad-label">Advertisement</span><ins class="adsbygoogle" style="display:block" data-ad-client="' +
      client + '" data-ad-slot="' + slot + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
    var ins = el.querySelector("ins");
    var check = function () {
      var st = ins.getAttribute("data-ad-status");
      if (st === "unfilled") { el.style.display = "none"; return true; }
      return st === "filled";
    };
    if (!check() && window.MutationObserver) {
      var mo = new MutationObserver(function () { if (check()) mo.disconnect(); });
      mo.observe(ins, { attributes: true, attributeFilter: ["data-ad-status"] });
    }
  }

  [].forEach.call(document.querySelectorAll(".ad[data-slot]"), renderAd);
})();
