// Countdown + annual leave planner UI. Dates and rules live in holidays.js (window.IEHOL).
(function () {
  "use strict";
  var H = window.IEHOL, KEY = "tavion_hol_v1";
  var $ = function (id) { return document.getElementById(id); };
  function fmt(s, opts) { var p = s.split("-"); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])).toLocaleDateString("en-IE", Object.assign({ timeZone: "UTC" }, opts || { weekday: "short", day: "numeric", month: "short" })); }
  function todayIso() { var t = new Date(); return t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0"); }

  var nx = H.nextHoliday(todayIso()), cd = $("countdown");
  if (nx && cd) {
    cd.querySelector(".amt").textContent = nx.days === 0 ? "Today! 🎉" : nx.days + (nx.days === 1 ? " day" : " days");
    cd.querySelector("p").textContent = nx.holiday.name + " – " + fmt(nx.holiday.date, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  }

  var form = $("planForm"), out = $("result");
  if (!form) return;
  var q = new URLSearchParams(location.search);
  try { var s = JSON.parse(localStorage.getItem(KEY)); if (s) { if (s.leave) $("leave").value = s.leave; if (s.year) $("year").value = s.year; $("school").checked = !!s.school;
    if (s.work) [].forEach.call($("workDays").querySelectorAll("input"), function (i) { i.checked = s.work.indexOf(+i.value) >= 0; }); } } catch (e) {}
  if (q.get("leave")) $("leave").value = q.get("leave");
  if (q.get("year")) $("year").value = q.get("year");

  function schoolBreaks(year) {
    var out = [];
    Object.keys(H.SCHOOL).forEach(function (sy) { H.SCHOOL[sy].forEach(function (b) { if (b[1].slice(0, 4) == year || b[2].slice(0, 4) == year) out.push(b); }); });
    return out;
  }
  function render(scroll) {
    var leave = Math.max(1, Math.min(40, parseInt($("leave").value, 10) || 0)), year = +$("year").value;
    var work = [].filter.call($("workDays").querySelectorAll("input"), function (i) { return i.checked; }).map(function (i) { return +i.value; });
    try { localStorage.setItem(KEY, JSON.stringify({ leave: leave, year: year, work: work, school: $("school").checked })); } catch (e) {}
    if (!work.length) { out.innerHTML = '<p class="callout warn">Tick the days you normally work.</p>'; return null; }
    var from = year === new Date().getFullYear() ? todayIso() : null;
    var p = H.plan(year, leave, { workDays: work, from: from });
    var h = '<div class="pts-hero"><div class="tl">' + p.used + ' days of leave</div><div class="amt">' + p.daysOff + ' days off</div><p>' + (p.used ? (p.daysOff / p.used).toFixed(1) + " days off for every day of leave" : "No breaks left this year") + (from ? " · from today" : "") + "</p></div>";
    if (p.breaks.length) h += '<div class="table-wrap"><table><thead><tr><th>Time off</th><th>Book leave</th><th class="num">Leave</th><th class="num">Off</th></tr></thead><tbody>' + p.breaks.map(function (b) {
      return "<tr><td><strong>" + fmt(b.from) + " – " + fmt(b.to) + "</strong>" + (b.holidays.length ? "<br><small>" + b.holidays.join(", ") + "</small>" : "") + "</td><td>" + fmt(b.leaveFrom) + (b.leaveTo !== b.leaveFrom ? " – " + fmt(b.leaveTo) : "") + '</td><td class="num">' + b.leave + '</td><td class="num"><strong>' + b.daysOff + "</strong></td></tr>";
    }).join("") + "</tbody></table></div>";
    if (p.used < leave) h += '<p class="small muted">' + (leave - p.used) + " day(s) left over – use them for a longer summer break or bridge any week.</p>";
    if ($("school").checked) {
      var sb = schoolBreaks(year);
      h += '<h3>School holidays ' + year + '</h3><ul class="notes">' + sb.map(function (b) { return "<li><strong>" + b[0] + ":</strong> " + fmt(b[1]) + " – " + fmt(b[2]) + "</li>"; }).join("") + '</ul><p class="small"><a href="school-holidays.html">All school holiday dates →</a></p>';
    }
    h += '<div class="btn-row"><a class="btn" href="ireland-public-holidays.ics" download data-track="ics_download" data-label="planner">📆 Add bank holidays to your calendar</a></div>';
    h += '<p class="small">Your employer decides when leave is taken and must consult you at least a month before – ask early. <a href="annual-leave.html">Annual leave rules →</a></p>';
    out.innerHTML = h;
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
    return p;
  }
  form.addEventListener("input", function () { render(); });
  form.addEventListener("change", function () { render(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); var p = render(true); if (p && window.TAVION && TAVION.track) TAVION.track("leave_plan", { total: p.leave, score: p.daysOff, label: String(p.year) }); });
  render();
})();
