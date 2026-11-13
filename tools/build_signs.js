// Builds driving/signs.html (road signs study page) from SIGNS and SIGN_INFO in driving/js/questions.js.
// Run from the repo root:  node tools/build_signs.js
// The sign cards are written as static HTML so search engines can read them.
const fs = require("fs"), path = require("path");
global.window = global;
require(path.join(__dirname, "../driving/js/questions.js"));

const GROUPS = [
  ["regulatory", "Regulatory signs", "Red circles and the STOP and YIELD signs give orders. A red slash means something is prohibited."],
  ["speed", "Speed limit signs", "A number in a red ring is the maximum speed in km/h. It's a limit, not a target."],
  ["mandatory", "Mandatory signs", "Blue circles tell you what you must do."],
  ["warning", "Warning signs", "Yellow diamonds with black symbols warn you about hazards ahead."]
];
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

let sections = "";
for (const [type, title, intro] of GROUPS) {
  const cards = SIGN_INFO.filter(s => s.type === type).map(s =>
    `<button type="button" class="sign-card" data-type="${type}" aria-label="${esc(s.name)}"><span class="sign-pic">${SIGNS[s.k]}</span>` +
    `<span class="sign-name">${esc(s.name)}</span><span class="sign-meaning">${esc(s.meaning)}</span><span class="sign-hint">Tap to reveal</span></button>`).join("\n");
  sections += `<section class="sign-group" data-group="${type}"><h2>${title}</h2><p class="muted">${intro}</p><div class="sign-grid">\n${cards}\n</div></section>\n`;
}

const html = `<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-adsense-account" content="ca-pub-1290266452162223">
<script src="/assets/tavion.js"></script>
<title>Irish Road Signs and Meanings – Learn for the Theory Test</title>
<meta name="description" content="Learn Irish road signs and their meanings for the driver theory test: stop, yield, speed limits, mandatory and warning signs. Quiz yourself, then practise sign questions free.">
<link rel="canonical" href="https://tavion.ie/driving/signs.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://tavion.ie/driving/signs.html">
<meta property="og:title" content="Irish Road Signs and Meanings – Theory Test Practice">
<meta property="og:description" content="Learn every common Irish road sign, quiz yourself, then practise sign questions. Free, no sign-up.">
<meta property="og:image" content="https://tavion.ie/driving/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/style.css">
<script src="js/config.js"></script>
<script src="js/questions.js"></script>
<script src="js/q/rules.js"></script>
<script src="js/q/signs.js"></script>
<script src="js/q/risk.js"></script>
<script src="js/q/safe.js"></script>
<script src="js/q/vulnerable.js"></script>
<script src="js/q/control.js"></script>
<script src="js/q/moto.js"></script>
<script src="js/q/tractor.js"></script>
<script src="js/q/truck.js"></script>
<script src="js/q/bus.js"></script>
<script src="js/q/heavy.js"></script>
<script src="js/app.js"></script>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="index.html"><b>L</b> Theory Test Practice</a><a href="index.html" class="small">Home</a></div></header>
<main class="wrap">
  <h1>Irish road signs and their meanings</h1>
  <p class="lead">Learn the signs you'll see in the theory test. Turn on quiz mode to hide the meanings and test yourself, then practise real sign questions.</p>
  <div class="sign-tools">
    <label class="toggle"><input type="checkbox" id="quiz"> Quiz mode – hide meanings</label>
    <div class="chips" id="chips">
      <button type="button" class="chip on" data-f="all">All</button>
      <button type="button" class="chip" data-f="regulatory">Regulatory</button>
      <button type="button" class="chip" data-f="speed">Speed</button>
      <button type="button" class="chip" data-f="mandatory">Mandatory</button>
      <button type="button" class="chip" data-f="warning">Warning</button>
    </div>
  </div>
${sections}
  <div class="card" style="margin-top:24px">
    <h2 style="margin-top:0">Practise sign questions</h2>
    <p class="muted">Practise questions on signs, road markings and traffic lights, with the answer explained after each one.</p>
    <div class="btn-row">
      <button class="btn primary" data-practice="car" data-track="signs_practice" data-label="car">🚗 Car &amp; Tractor</button>
      <button class="btn" data-practice="motorcycle" data-track="signs_practice" data-label="motorcycle">🏍️ Motorcycle</button>
    </div>
  </div>
  <p class="muted small">Signs on this page are simplified drawings to help you learn. Always check the official Rules of the Road for the full set of Irish traffic signs.</p>
  <div class="ad" id="ad"></div>
</main>
<footer><div class="wrap"><p>Independent practice site, not affiliated with the RSA. <a href="privacy.html">Privacy &amp; cookies</a> · <a href="../">More free apps from Tavion</a></p></div></footer>
<script>
(function () {
  var quiz = document.getElementById("quiz");
  try { quiz.checked = localStorage.getItem("signs_quiz") === "1"; } catch (e) {}
  function applyQuiz() {
    document.body.classList.toggle("quiz", quiz.checked);
    document.querySelectorAll(".sign-card.shown").forEach(function (c) { c.classList.remove("shown"); });
    try { localStorage.setItem("signs_quiz", quiz.checked ? "1" : "0"); } catch (e) {}
  }
  quiz.addEventListener("change", function () { applyQuiz(); if (quiz.checked && window.TAVION && TAVION.track) TAVION.track("signs_quiz_mode", {}); });
  applyQuiz();
  document.querySelectorAll(".sign-card").forEach(function (c) {
    c.addEventListener("click", function () { if (document.body.classList.contains("quiz")) c.classList.toggle("shown"); });
  });
  document.getElementById("chips").addEventListener("click", function (e) {
    var b = e.target.closest(".chip"); if (!b) return;
    document.querySelectorAll(".chip").forEach(function (x) { x.classList.toggle("on", x === b); });
    var f = b.getAttribute("data-f");
    document.querySelectorAll(".sign-group").forEach(function (g) { g.style.display = (f === "all" || g.getAttribute("data-group") === f) ? "" : "none"; });
  });
  document.querySelectorAll("[data-practice]").forEach(function (b) {
    b.addEventListener("click", function () { DTT.startPractice(b.getAttribute("data-practice"), "signs"); });
  });
  DTT.renderAd("ad", "home");
})();
</script>
</body>
</html>
`;
fs.writeFileSync(path.join(__dirname, "../driving/signs.html"), html);
console.log("Wrote driving/signs.html with", SIGN_INFO.length, "signs");
