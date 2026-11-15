// Work permit salary checker UI. Rules live in permit.js (window.IEPERMIT).
(function () {
  "use strict";
  var P = window.IEPERMIT, KEY = "tavion_permit_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("permitForm"), out = $("result");
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function eur(n, dp) { dp = dp || 0; return (n < 0 ? "−" : "") + "€" + Math.abs(n).toLocaleString("en-IE", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  var F = ["permit", "salary", "health", "board", "hours"];

  var sel = $("permit");
  sel.innerHTML = P.PERMITS.map(function (p) { return '<option value="' + p.id + '">' + p.name + '</option>'; }).join("");

  try { var s = JSON.parse(localStorage.getItem(KEY)); if (s) { F.forEach(function (k) { if (s[k]) $(k).value = s[k]; }); $("graduate").checked = !!s.graduate; if (s.health || s.board || s.hours) $("adv").open = true; } } catch (e) {}
  var q = new URLSearchParams(location.search);
  if (q.get("permit") && P.PERMITS.some(function (p) { return p.id === q.get("permit"); })) sel.value = q.get("permit");
  if (q.get("salary")) $("salary").value = Number(num(q.get("salary"))).toLocaleString("en-IE");
  if (q.get("grad") === "1") $("graduate").checked = true;

  function sync() {
    var p = P.get(sel.value);
    $("gradRow").style.display = p.grad ? "" : "none";
    $("gradNote").textContent = p.grad ? "Graduate rate: " + eur(p.grad) + " instead of " + eur(p.min) + "." : "";
    $("boardRow").style.display = p.id === "cfs" ? "" : "none";
  }

  function render() {
    sync();
    var st = { graduate: $("graduate").checked }; F.forEach(function (k) { st[k] = $(k).value; }); try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
    var sal = num($("salary").value);
    if (!sal) { out.innerHTML = ""; return null; }
    var hours = num($("hours").value) || 39;
    var r = P.check({ permit: sel.value, graduate: $("graduate").checked, salary: sal, health: num($("health").value), board: num($("board").value), hours: hours });
    var p = r.permit, h = "";
    var close = r.meets && r.gapPct < 0.05;
    var cls = !r.meets ? "bad" : close || !r.meets2027 ? "warn" : "good";
    h += '<div class="verdict-box ' + cls + '"><h2>' + (r.meets ? "✅ Your pay meets the minimum" : "❌ Your pay is below the minimum") + '</h2><p>The minimum for a <strong>' + p.name + '</strong>' +
      (r.graduate ? ' at the graduate rate' : '') + ' is <strong>' + eur(r.min) + '</strong> a year from ' + P.EFFECTIVE + '. ' +
      (r.meets ? 'You\'re ' + eur(r.gap) + ' above it.' : 'You\'re <strong>' + eur(-r.gap) + ' short</strong> – at this pay a new permit or renewal wouldn\'t meet the salary rule.') + '</p></div>';
    h += '<div class="net-hero"><div class="tl">' + (r.meets ? "Above the minimum by" : "Short of the minimum by") + '</div><div class="amt">' + eur(Math.abs(r.gap)) + '</div><p>a year · ' + eur(Math.abs(r.gap) / 12) + ' a month</p></div>';
    h += '<div class="periods" style="grid-template-columns:repeat(3,1fr)"><div><b>' + eur(r.min) + '</b><span>minimum / year</span></div><div><b>' + eur(r.monthly) + '</b><span>minimum / month</span></div><div><b>' + eur(r.minHourly39, 2) + '</b><span>per hour (39 h week)</span></div></div>';
    if (r.counted !== sal) h += '<p class="muted small">Pay counted: ' + eur(r.counted) + ' (basic salary ' + eur(sal) + ' plus health insurance' + (p.id === "cfs" ? ' and board &amp; accommodation' : '') + ' paid by your employer). Bonuses and overtime don\'t count.</p>';
    if (hours !== 39) h += '<div class="card"><div class="tl">Your hours</div><p class="small" style="margin:6px 0 0">The minimum is a yearly amount, so on <strong>' + hours + ' hours a week</strong> you need at least <strong>' + eur(r.minHourlyYourHours, 2) + ' an hour</strong> to reach ' + eur(r.min) +
      '. You\'re on about ' + eur(r.yourHourly, 2) + ' an hour. <a href="hourly-rate.html">Hourly rates explained →</a></p></div>';
    h += '<div class="card"><div class="tl">Will you still qualify in 2027?</div><p class="small" style="margin:6px 0 0">From 2027 the minimums are reviewed each year in line with average earnings. If they rise by about ' + (P.INDEX_AVG * 100).toFixed(1) + '% (the recent average)' + (p.lower ? ', and lower-paid roles move closer to the standard rate as planned' : '') +
      ', this minimum would be around <strong>' + eur(r.est2027) + '</strong>. ' + (r.meets2027 ? 'Your pay would still be above it.' : '<strong>Your pay would fall ' + eur(-r.gap2027) + ' short</strong> – worth raising with your employer before your renewal.') +
      ' This is an estimate, not an official figure. <a href="2027-increases.html">What\'s planned →</a></p></div>';
    var rows = P.qualifies(r.counted, $("graduate").checked).filter(function (x, i, a) { return i === 0 || x.permit.slug + x.min !== a[i - 1].permit.slug + a[i - 1].min; }).map(function (x) {
      return '<tr><th scope="row"><a href="' + x.permit.slug + '.html">' + x.permit.short + '</a></th><td>' + eur(x.min) + '</td><td>' + (x.meets ? '✅ ' + eur(x.gap) + ' over' : '❌ ' + eur(-x.gap) + ' short') + '</td></tr>';
    }).join("");
    h += '<h2>Your pay against every permit</h2><div class="table-wrap"><table class="sumtab"><thead><tr><th>Permit</th><th>Minimum</th><th>' + eur(r.counted) + '</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
    var tips = [];
    if (!r.meets) tips.push(["bad", "Below the minimum? Your employer needs to raise your basic pay before applying or renewing. Health insurance they pay for you can count towards it. <a href='what-counts.html'>What counts as pay →</a>"]);
    if (p.id === "gep" && !r.graduate) tips.push(["", "Graduated from an Irish college (Level 8 or higher) in the last 12 months? The GEP minimum is " + eur(p.grad) + ". <a href='graduate-rates.html'>Graduate rates →</a>"]);
    if (p.id === "gep" && r.counted >= 40904) tips.push(["ok", "On " + eur(r.counted) + " you could meet the Critical Skills minimum if your job is on the Critical Skills list and you have a relevant degree – that permit leads to Stamp 4 after 2 years. <a href='critical-skills-permit.html'>Critical Skills →</a>"]);
    if (r.counted >= 68911 && p.id !== "csep_high") tips.push(["ok", "On €68,911 or more, most jobs can qualify for a Critical Skills permit, even without a degree. <a href='critical-skills-permit.html'>See how →</a>"]);
    tips.push(["", "Renewing? The new minimums apply to renewals too. <a href='renewals.html'>Renewal rules →</a>"]);
    tips.push(["", "Time on a work permit (Stamp 1) counts towards Irish citizenship. <a href='../citizenship/' data-track='cross_app' data-label='citizenship_from_permit'>When can I apply? →</a>"]);
    tips.push(["", "What's " + eur(sal) + " after tax? <a href='../salary/?gross=" + Math.round(sal) + "' data-track='cross_app' data-label='salary_from_permit'>See your take-home pay →</a>"]);
    h += '<ul class="issues">' + tips.map(function (t) { return '<li class="' + t[0] + '">' + t[1] + '</li>'; }).join("") + '</ul>';
    h += '<p class="muted small">Based on DETE minimum annual remuneration from ' + P.EFFECTIVE + '. Your permit can still be refused for other reasons (for example the Labour Market Needs Test or the 50:50 rule). Always check enterprise.gov.ie before you apply.</p>';
    out.innerHTML = h;
    if (window.TAVION && TAVION.next) TAVION.next(out, [{ t: "When can you apply for Irish citizenship?", s: "Time on Stamp 1 counts – work out your date", href: "../citizenship/", label: "permit_to_citizenship" }, { t: "Your take-home pay on " + eur(sal), s: "After tax, USC and PRSI", href: "../salary/?gross=" + Math.round(sal), label: "permit_to_salary" }]);
    return r;
  }
  function band(x) { return x < 33000 ? "<33k" : x < 37000 ? "33-37k" : x < 41000 ? "37-41k" : x < 50000 ? "41-50k" : x < 69000 ? "50-69k" : "69k+"; }
  form.addEventListener("input", function () { render(); });
  form.addEventListener("change", function () { render(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); var r = render(); if (!r) return;
    if (window.TAVION && TAVION.track) TAVION.track("permit_calc", { permit: r.permit.id, salary_band: band(r.counted), result: r.meets ? "meets" : "below", graduate: r.graduate ? "yes" : "no" });
    out.scrollIntoView({ behavior: "smooth", block: "start" }); });
  ["salary", "health", "board"].forEach(function (id) { var el = $(id); el.addEventListener("input", function () { var raw = el.value.replace(/[^\d]/g, ""); el.value = raw ? Number(raw).toLocaleString("en-IE") : ""; }); });
  $("resetAdv").addEventListener("click", function () { ["health", "board", "hours"].forEach(function (k) { $(k).value = ""; }); render(); });
  render();
})();
