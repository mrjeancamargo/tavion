// Shared helpers for the CAO app: ad units (up to two per page).
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

// "Will your points get you in?" box on course pages.
(function () {
  var f = document.getElementById("mini");
  if (!f) return;
  var cut = parseInt(f.getAttribute("data-cut"), 10), out = document.getElementById("miniOut"), inp = document.getElementById("miniPts");
  try { var p = localStorage.getItem("tavion_cao_pts"); if (p) inp.value = p; } catch (e) {}
  function check(track) {
    var v = parseInt(inp.value, 10);
    if (!isFinite(v)) { out.textContent = ""; return; }
    try { localStorage.setItem("tavion_cao_pts", v); } catch (e) {}
    var d = v - cut, msg;
    if (d >= 10) msg = "✅ Yes – " + d + " points above last year's cut-off (" + cut + ").";
    else if (d > 0) msg = "👍 Just – " + d + " above last year's " + cut + ". Points can rise, so keep a back-up below it.";
    else if (d === 0) msg = "👍 Exactly last year's cut-off (" + cut + "). Points can rise, so keep a back-up below it.";
    else if (d >= -20) msg = "🤞 Close – " + (-d) + " below last year's " + cut + ". Points can drop, so it's worth listing.";
    else msg = "📉 " + (-d) + " below last year's " + cut + ". Look at the similar and lower-points courses below.";
    out.textContent = msg;
    if (track && window.TAVION && TAVION.track) TAVION.track("course_check", { label: f.getAttribute("data-code"), score: v });
  }
  f.addEventListener("submit", function () { check(true); });
  inp.addEventListener("input", function () { check(false); });
  if (inp.value) check(false);
})();
