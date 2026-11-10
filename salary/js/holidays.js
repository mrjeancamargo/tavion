// Annual leave calculator (Organisation of Working Time Act 1997, section 19).
// Entitlement = the greatest of: 4 working weeks (1,365+ hours in the leave year),
// 1/3 working week per month with 117+ hours, or 8% of hours worked (max 4 working weeks).
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("leave"), out = $("lv_out");
  function num(v) { var n = parseFloat(String(v || "").replace(/[€,\s]/g, "")); return isFinite(n) ? n : 0; }
  function r1(n) { return Math.round(n * 10) / 10; }
  function eur(n) { return "€" + n.toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  function calc() {
    var hw = num($("lv_hours").value) || 39, dw = Math.min(7, num($("lv_days").value) || 5);
    var months = +$("lv_months").value || 12, rate = num($("lv_rate").value), total = num($("lv_total").value);
    var monthHours = hw * 52 / 12;
    var worked = total || monthHours * months;
    var weekCap = hw * 4; // 4 working weeks, in hours

    var methods = [];
    // 1. Working week: 4 weeks if 1,365 hours worked in the leave year
    methods.push({ name: "Working week method", hours: worked >= 1365 ? weekCap : 0,
      why: worked >= 1365 ? "You worked at least 1,365 hours, so you get 4 working weeks." : "Needs at least 1,365 hours in the leave year." });
    // 2. Calendar month: 1/3 working week for each month with 117+ hours
    var avgMonth = total ? total / months : monthHours, qualMonths = avgMonth >= 117 ? months : 0;
    methods.push({ name: "Calendar month method", hours: Math.min(weekCap, qualMonths * hw / 3),
      why: avgMonth >= 117 ? qualMonths + " month" + (qualMonths > 1 ? "s" : "") + " with 117+ hours × ⅓ of a working week." : "Needs at least 117 hours in a month (you average " + Math.round(avgMonth) + ")." });
    // 3. Hours worked: 8%, capped at 4 working weeks
    methods.push({ name: "Hours worked method", hours: Math.min(weekCap, worked * 0.08),
      why: "8% of " + Math.round(worked).toLocaleString("en-IE") + " hours worked" + (worked * 0.08 > weekCap ? " (capped at 4 working weeks)." : ".") });

    var best = methods.reduce(function (a, b) { return b.hours > a.hours ? b : a; });
    var dayHours = hw / dw, days = best.hours / dayHours, weeks = best.hours / hw;
    var h = '<div class="net-hero"><div class="tl">Your annual leave</div><div class="amt">' + r1(days) + ' days</div><p>' + r1(best.hours) + ' hours · ' + r1(weeks) + ' working weeks</p></div>';
    if (rate) h += '<div class="better"><div class="em">💶</div><p>Holiday pay worth <strong class="n">' + eur(best.hours * rate) + '</strong> at ' + eur(rate) + ' an hour.</p></div>';
    h += '<div class="table-wrap"><table><thead><tr><th>Method</th><th class="num">Hours</th><th class="num">Days</th></tr></thead><tbody>' +
      methods.map(function (m) { return '<tr' + (m === best ? ' class="total"' : '') + '><th scope="row">' + m.name + '<br><span class="muted small" style="font-weight:400">' + m.why + '</span></th><td class="num">' + r1(m.hours) + '</td><td class="num">' + r1(m.hours / dayHours) + '</td></tr>'; }).join("") +
      '</tbody></table></div>';
    var phDay = hw / 5;
    h += '<div class="card"><div class="tl">Public holidays</div><p style="margin:6px 0 0">You also get <strong>10 public holidays</strong> a year' + (hw * 5 < 40 ? ' – but only if you work at least 40 hours in the 5 weeks before each one (you work about ' + Math.round(hw * 5) + ').' : '.') +
      ' If one falls on a day you don\'t normally work, you get one-fifth of your weekly pay: <strong>' + r1(phDay) + ' hours' + (rate ? ' (' + eur(phDay * rate) + ')' : '') + '</strong>.</p></div>';
    h += '<p class="muted small">This is the legal minimum – your contract may give you more. Leave year months worked: ' + months + '.</p>';
    out.innerHTML = h;
    if (window.TAVION && TAVION.track) TAVION.track("leave_calc", { label: r1(days) + " days", method: best.name });
  }
  form.addEventListener("submit", function (e) { e.preventDefault(); calc(); out.scrollIntoView({ behavior: "smooth", block: "start" }); });
})();
