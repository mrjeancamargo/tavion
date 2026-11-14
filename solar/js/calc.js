// Solar panel calculator UI. Numbers come from solar.js (window.IESOLAR). Nothing leaves the device.
(function () {
  "use strict";
  var S = window.IESOLAR, KEY = "tavion_solar_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("solarForm"), out = $("result");
  function num(v) { var n = parseFloat(String(v == null ? "" : v).replace(/[€,\s%c]/g, "")); return isFinite(n) ? n : 0; }
  function val(id) { var e = $(id); return e ? e.value : ""; }
  function opt(id) { var v = val(id); return v === "" ? null : num(v); }
  function radio(name) { var r = form.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ""; }
  function eur(n) { return (n < 0 ? "−" : "") + "€" + Math.abs(Math.round(n)).toLocaleString("en-IE"); }
  function kwh(n) { return Math.round(n).toLocaleString("en-IE") + " kWh"; }
  function yrs(p) { return p === null ? "over 25 years" : p < 1 ? "under a year" : (p.toFixed(1).replace(/\.0$/, "")) + " years"; }

  var FIELDS = ["county", "bill", "facing", "size", "usage", "unitRate", "exportRate", "cost", "battSize", "battCost", "tilt", "shading", "priceRise", "inverterCost", "extraKWh", "loanRate", "loanYears"];
  var RADIOS = ["battery", "home", "grant"];
  function save() {
    var st = { adv: $("adv").open, loan: $("loan").checked };
    FIELDS.forEach(function (k) { st[k] = val(k); }); RADIOS.forEach(function (k) { st[k] = radio(k); });
    try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
  }
  function load() {
    var st = null; try { st = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    var q = new URLSearchParams(location.search);
    if (st) {
      FIELDS.forEach(function (k) { if (st[k] && $(k)) $(k).value = st[k]; });
      RADIOS.forEach(function (k) { var r = form.querySelector('input[name="' + k + '"][value="' + st[k] + '"]'); if (r) r.checked = true; });
      $("loan").checked = !!st.loan; if (st.adv) $("adv").open = true;
    }
    if (q.get("county") && S.COUNTIES[q.get("county")]) $("county").value = q.get("county");
    if (q.get("kwp")) $("size").value = q.get("kwp");
    if (q.get("battery")) { var b = form.querySelector('input[name="battery"][value="' + (q.get("battery") === "no" ? "0" : q.get("battery")) + '"]'); if (b) b.checked = true; }
    if (q.get("bill")) $("bill").value = num(q.get("bill"));
    $("loanBox").hidden = !$("loan").checked;
  }

  function inputs() {
    var battery = radio("battery"), battSize = opt("battSize");
    return {
      county: val("county"), bill2m: num(val("bill")), facing: val("facing"), kWp: num(val("size")),
      battKWh: battery === "0" ? 0 : (battSize || num(battery)), home: radio("home"), grant: radio("grant") || "standard",
      usage: opt("usage"), unitRate: opt("unitRate") ? opt("unitRate") / 100 : null, exportRate: opt("exportRate") !== null ? opt("exportRate") / 100 : null,
      cost: opt("cost"), battCost: opt("battCost"), tilt: val("tilt") || "standard", shading: num(val("shading")),
      priceRise: opt("priceRise"), inverterCost: opt("inverterCost"), extraKWh: opt("extraKWh"),
      loan: $("loan").checked, loanRate: opt("loanRate") === null ? 3.5 : opt("loanRate"), loanYears: opt("loanYears") || 7
    };
  }

  // ---- Payback chart (inline SVG, no library) ----
  function chart(r, alt) {
    var W = cw(), H = W < 500 ? 230 : 280, L = 50, R = 10, T = 22, B = 30, n = r.series.length - 1;
    var all = r.series.concat(alt ? alt.series : []);
    var min = Math.min(0, Math.min.apply(null, all)), max = Math.max(0, Math.max.apply(null, all));
    var step = niceStep((max - min) / 5); min = Math.floor(min / step) * step; max = Math.ceil(max / step) * step;
    var x = function (i) { return L + (W - L - R) * i / n; }, y = function (v) { return T + (H - T - B) * (max - v) / (max - min); };
    var g = "";
    for (var v = min; v <= max + 1; v += step) g += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v) + '" y2="' + y(v) + '" class="' + (v === 0 ? "zero" : "grid") + '"/><text x="' + (L - 8) + '" y="' + (y(v) + 4) + '" class="ax" text-anchor="end">' + short(v) + "</text>";
    for (var i = 0; i <= n; i += (W < 500 ? 10 : 5)) g += '<text x="' + x(i) + '" y="' + (H - 12) + '" class="ax" text-anchor="middle">' + (i === 0 ? "Now" : "Yr " + i) + "</text>";
    function path(s) { return s.map(function (v, i) { return (i ? "L" : "M") + x(i).toFixed(1) + " " + y(v).toFixed(1); }).join(" "); }
    var line = path(r.series);
    var area = line + " L" + x(n) + " " + y(0) + " L" + x(0) + " " + y(0) + " Z";
    var clipUp = '<clipPath id="up"><rect x="0" y="0" width="' + W + '" height="' + y(0) + '"/></clipPath><clipPath id="down"><rect x="0" y="' + y(0) + '" width="' + W + '" height="' + H + '"/></clipPath>';
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" class="chart" role="img" aria-label="Payback chart: money you are ahead or behind each year for 25 years">' + "<defs>" + clipUp + "</defs>" + g +
      '<path d="' + area + '" class="a-up" clip-path="url(#up)"/><path d="' + area + '" class="a-down" clip-path="url(#down)"/>';
    if (alt) svg += '<path d="' + path(alt.series) + '" class="l-alt"/>';
    svg += '<path d="' + line + '" class="l-main"/>';
    if (r.payback !== null && r.payback > 0 && r.payback <= n) {
      var px = x(r.payback);
      svg += '<line x1="' + px + '" x2="' + px + '" y1="' + T + '" y2="' + y(0) + '" class="pb"/><circle cx="' + px + '" cy="' + y(0) + '" r="6" class="pb-dot"/>' +
        '<text x="' + Math.min(px + 8, W - 150) + '" y="' + (T + 14) + '" class="pb-t">Paid back: ' + yrs(r.payback) + "</text>";
    }
    svg += '<line id="hoverLine" x1="0" x2="0" y1="' + T + '" y2="' + (H - B) + '" class="hover" style="display:none"/><circle id="hoverDot" r="5" class="hover-dot" style="display:none"/>';
    svg += '<rect x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (H - T - B) + '" fill="transparent" id="hitArea"/></svg>';
    return { svg: svg, x: x, y: y, n: n, W: W };
  }
  // Draw at the real pixel width so the labels stay readable on phones.
  function cw() { return Math.max(280, Math.min(760, (out.clientWidth || 340) - 38)); }
  function niceStep(raw) { var p = Math.pow(10, Math.floor(Math.log10(raw || 1))), f = raw / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p; }
  function short(v) { return (v < 0 ? "−" : "") + "€" + (Math.abs(v) >= 1000 ? (Math.abs(v) / 1000).toFixed(Math.abs(v) % 1000 ? 1 : 0).replace(/\.0$/, "") + "k" : Math.abs(v)); }

  function bars(r) {
    var M = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"], NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var use = r.usage / 12, max = Math.max(use, Math.max.apply(null, r.monthly)) * 1.15, W = cw(), H = W < 500 ? 170 : 200, L = 4, B = 24, bw = (W - 2 * L) / 12;
    var s = '<svg viewBox="0 0 ' + W + " " + H + '" class="chart bars" role="img" aria-label="Solar generation by month compared with your monthly use">';
    r.monthly.forEach(function (m, i) {
      var h = (H - B - 10) * m / max, xx = L + i * bw + bw * 0.15;
      s += '<rect x="' + xx + '" y="' + (H - B - h) + '" width="' + bw * 0.7 + '" height="' + h + '" rx="4" class="bar"><title>' + NAMES[i] + ": " + m + ' kWh</title></rect><text x="' + (xx + bw * 0.35) + '" y="' + (H - 8) + '" class="ax" text-anchor="middle">' + M[i] + "</text>";
    });
    var uy = H - B - (H - B - 10) * use / max;
    s += '<line x1="' + L + '" x2="' + (W - L) + '" y1="' + uy + '" y2="' + uy + '" class="use"/></svg><p class="small muted" style="margin:2px 0 0">Dashed line: your use, about ' + Math.round(use) + " kWh a month.</p>";
    return s;
  }

  var last = null;
  function render() {
    save();
    var o = inputs();
    if (!o.county) { out.innerHTML = ""; return null; }
    var r = S.calc(o), alt = null;
    if (r.battKWh) { var o2 = JSON.parse(JSON.stringify(o)); o2.battKWh = 0; o2.kWp = r.kWp; alt = S.calc(o2); }
    var h = "";
    if (o.loan) {
      var diff = r.saving1 - r.loan.yearly;
      h += '<div class="net-hero"><div class="tl">With a ' + r.loan.years + "-year loan at " + r.loan.rate + '%</div><div class="amt">' + (diff >= 0 ? "+" : "") + eur(Math.abs(diff) / 12) + '</div><p>' + (diff >= 0 ? "a month better off from day one" : "a month more than you save, while you repay") + " · repayments " + eur(r.loan.monthly) + " vs savings " + eur(r.saving1 / 12) + " a month · then about " + eur(r.saving1) + " a year saved · " + eur(r.profit) + " ahead after 25 years</p></div>";
    } else {
      h += '<div class="net-hero"><div class="tl">Your solar panels pay for themselves in</div><div class="amt">' + yrs(r.payback) + "</div><p>then save about <strong>" + eur(r.saving1) + "</strong> a year · " + eur(r.profit) + " ahead after 25 years</p></div>";
    }
    h += '<div class="periods sol"><div><b>' + r.kWp + ' kWp</b><span>' + r.panels + " panels</span></div><div><b>" + eur(r.net) + "</b><span>cost after grant</span></div><div><b>" + eur(r.grant.total) + "</b><span>SEAI grant</span></div>" +
      "<div><b>" + eur(r.saving1) + "</b><span>saved in year 1</span></div><div><b>" + kwh(r.gen) + "</b><span>made a year</span></div><div><b>" + r.cover + "%</b><span>of your power</span></div></div>";
    var c = chart(r, alt);
    h += '<div class="card"><div class="tl">Payback over 25 years</div><p class="small muted" style="margin:4px 0 0">Below the line you\'re still paying off the panels; above it, it\'s profit. Tap the chart to see any year.</p>' + c.svg +
      '<p id="hoverText" class="hover-text">' + (r.payback !== null ? "Year " + Math.ceil(r.payback) + ": you're in profit." : "") + '</p><ul class="legend"><li><i class="c-net"></i>' + (r.battKWh ? "With " + r.battKWh + " kWh battery" : "Your solar") + "</li>" + (alt ? '<li><i class="c-alt"></i>Without battery (' + yrs(alt.payback) + ")</li>" : "") + "</ul></div>";
    h += '<div class="card"><div class="tl">Where your solar power goes (year 1)</div><div class="stack"><span class="c-net" style="width:' + (r.direct / r.gen * 100).toFixed(1) + '%"></span><span class="c-pen" style="width:' + (r.fromBattery / r.gen * 100).toFixed(1) + '%"></span><span class="c-usc" style="width:' + (r.exported / r.gen * 100).toFixed(1) + '%"></span></div>' +
      '<ul class="legend"><li><i class="c-net"></i>Used in your home ' + kwh(r.direct) + "</li>" + (r.fromBattery ? '<li><i class="c-pen"></i>Stored and used later ' + kwh(r.fromBattery) + "</li>" : "") + '<li><i class="c-usc"></i>Sold to the grid ' + kwh(r.exported) + "</li></ul></div>";
    h += '<div class="card"><div class="tl">Your electricity bill (a year)</div><dl class="dl" style="margin-top:8px"><dt>Now</dt><dd>' + eur(r.billBefore) + "</dd><dt>Power you no longer buy</dt><dd>−" + eur(r.importSaved) + "</dd><dt>Paid for power you export</dt><dd>−" + eur(r.exportIncome) +
      '</dd><dt><strong>With solar</strong></dt><dd><strong>' + eur(r.billAfter) + '</strong></dd></dl><p class="small muted" style="margin:8px 0 0">At ' + (r.rate * 100).toFixed(1).replace(/\.0$/, "") + "c a kWh to buy and " + (r.exportRate * 100).toFixed(1).replace(/\.0$/, "") + "c to sell. The standing charge stays.</p></div>";
    h += '<div class="card"><div class="tl">What you\'d make each month in ' + r.countyName + "</div>" + bars(r) + '<p class="small muted" style="margin:4px 0 0">Summer months make 4–5 times more than December. <a href="solar-in-winter.html">Solar in winter →</a></p></div>';
    h += '<h2>The numbers</h2><div class="table-wrap"><table class="sumtab"><tbody>' +
      "<tr><th scope=\"row\">Panels (" + r.kWp + " kWp)</th><td>" + eur(r.cost) + "</td></tr>" + (r.battKWh ? '<tr><th scope="row">Battery (' + r.battKWh + " kWh)</th><td>" + eur(r.battCost) + "</td></tr>" : "") +
      '<tr><th scope="row">SEAI solar grant</th><td>−' + eur(r.grant.solar) + "</td></tr>" + (r.grant.battery ? '<tr><th scope="row">SEAI battery grant</th><td>−' + eur(r.grant.battery) + "</td></tr>" : "") +
      '<tr class="total"><th scope="row">You pay</th><td>' + eur(r.net) + "</td></tr>" +
      '<tr><th scope="row">Saved over 25 years</th><td>' + eur(r.totalSavings) + "</td></tr>" + (r.roi !== null ? '<tr><th scope="row">Return on what you pay</th><td>' + r.roi + "%</td></tr>" : "") +
      "</tbody></table></div>";
    var tips = [];
    if (r.grant.total === 0 && o.grant === "none") tips.push(["warn", "No grant included. Most homes built and occupied before 2025 qualify for up to €1,800. <a href='seai-solar-grant.html'>Check the grant →</a>"]);
    else tips.push(["ok", "Apply to SEAI and get your grant offer <strong>before</strong> any work starts, or you won't get the " + eur(r.grant.total) + ". <a href='how-to-apply.html'>How to apply, step by step →</a>"]);
    if (alt) {
      var d = (alt.payback || 99) - (r.payback || 99);
      tips.push([d >= 0 ? "ok" : "warn", d >= 0 ? "The battery shortens your payback by " + yrs(d) + "." : "The battery adds about " + yrs(-d) + " to your payback (" + yrs(alt.payback) + " without it) but you'd use " + (r.selfUse - alt.selfUse) + "% more of your own power. <a href='battery-grant.html'>Is a battery worth it? →</a>"]);
    } else if (r.exported > r.gen * 0.5) tips.push(["", "You'd sell over half of your solar power for " + (r.exportRate * 100).toFixed(1) + "c. A battery or running the dishwasher and washing machine in the day keeps more of it. <a href='battery-grant.html'>Battery grant (€600) →</a>"]);
    if (!r.taxFree) tips.push(["warn", "Your export income is over €400 a year – the tax-free limit for 2026 (rising to €600 in 2027). <a href='solar-income-tax.html'>Tax on solar income →</a>"]);
    if (o.grant === "standard") tips.push(["", "Getting Fuel Allowance, Working Family Payment or One-Parent Family Payment? You may get up to €9,000 instead. <a href='free-solar-panels.html'>Higher grants →</a>"]);
    tips.push(["", "Paying for it? A low-cost Home Energy Upgrade Loan runs from about 3–4%. Tick “Paying with a loan” in the advanced options to compare. <a href='home-energy-upgrade-loan.html'>Loans →</a>"]);
    h += '<ul class="issues">' + tips.map(function (t) { return '<li class="' + t[0] + '">' + t[1] + "</li>"; }).join("") + "</ul>";
    h += '<div class="res-actions"><a class="btn" href="solar-panels-' + r.county + '.html">Solar in ' + r.countyName + '</a><a class="btn" href="how-to-apply.html">How to get the grant</a></div>';
    h += '<p class="muted small">Estimate only. Generation from PVGIS (EU Joint Research Centre) for ' + r.countyName + " with " + Math.round(S.factor(o.facing, o.tilt) * 100) + "% for your roof" + (o.shading ? " and " + o.shading + "% shading" : "") +
      ". Prices rise " + (o.priceRise === null ? S.DEFAULTS.priceRise : o.priceRise) + "% a year, panels lose 0.5% a year and the inverter is replaced in year 12. Get at least 3 quotes from SEAI-registered companies.</p>";
    out.innerHTML = h;
    hookHover(r, c);
    last = r;
    return r;
  }

  function hookHover(r, c) {
    var hit = $("hitArea"), line = $("hoverLine"), dot = $("hoverDot"), txt = $("hoverText");
    if (!hit) return;
    function move(ev) {
      var svg = hit.ownerSVGElement, rect = svg.getBoundingClientRect();
      var px = ((ev.touches ? ev.touches[0].clientX : ev.clientX) - rect.left) * c.W / rect.width;
      var i = Math.max(0, Math.min(c.n, Math.round((px - c.x(0)) / (c.x(1) - c.x(0)))));
      var v = r.series[i];
      line.setAttribute("x1", c.x(i)); line.setAttribute("x2", c.x(i)); line.style.display = "";
      dot.setAttribute("cx", c.x(i)); dot.setAttribute("cy", c.y(v)); dot.style.display = "";
      txt.innerHTML = (i === 0 ? "Today" : "After year " + i) + ": <strong>" + (v >= 0 ? eur(v) + " ahead" : eur(-v) + " still to pay off") + "</strong>";
    }
    hit.addEventListener("mousemove", move); hit.addEventListener("click", move);
    hit.addEventListener("touchstart", move, { passive: true }); hit.addEventListener("touchmove", move, { passive: true });
  }

  function band(b) { return b < 150 ? "<150" : b < 250 ? "150-250" : b < 350 ? "250-350" : "350+"; }
  form.addEventListener("input", render);
  form.addEventListener("change", function (e) { if (e.target.id === "loan") $("loanBox").hidden = !$("loan").checked; render(); });
  form.addEventListener("submit", function (e) {
    e.preventDefault(); var r = render(); if (!r) return;
    if (window.TAVION && TAVION.track) TAVION.track("solar_calc", { county: r.county, kwp: String(r.kWp), battery: r.battKWh ? "yes" : "no", bill_band: band(num(val("bill"))), advanced: $("adv").open ? "yes" : "no", loan: $("loan").checked ? "yes" : "no" });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  $("resetAdv").addEventListener("click", function () {
    ["usage", "unitRate", "exportRate", "cost", "battSize", "battCost", "shading", "priceRise", "inverterCost", "extraKWh", "loanRate", "loanYears"].forEach(function (k) { $(k).value = ""; });
    $("tilt").value = "standard"; $("shading").value = "0"; $("loan").checked = false; $("loanBox").hidden = true;
    var g = form.querySelector('input[name="grant"][value="standard"]'); if (g) g.checked = true;
    render();
  });
  load();
  render();
})();
