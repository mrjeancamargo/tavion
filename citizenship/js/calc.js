/*
 * Irish naturalisation reckonable residence calculator.
 * Mirrors the counting method of ISD's own residency calculator:
 *  - counts days covered by reckonable permissions (stamps) in the 9 years (5 for spouses) up to the application date
 *  - Stamps 2 and 2A (and gaps / no permission) are not reckonable
 *  - the final year must be covered by permissions with no gaps
 * and adds the statutory absence check for the final year (70 days + 30 in exceptional circumstances, s.15C).
 * Everything runs in the browser; entries are kept only on this device (localStorage).
 */
(function () {
  "use strict";

  var STAMPS = [
    { v: "1",      label: "Stamp 1 – work / employment permit / business", reck: true },
    { v: "1A",     label: "Stamp 1A – trainee accountant", reck: true },
    { v: "1G",     label: "Stamp 1G – graduate or spouse of CSEP holder", reck: true },
    { v: "1H",     label: "Stamp 1H – NCHD doctor (multi-site permit)", reck: true },
    { v: "3",      label: "Stamp 3 – volunteer, minister, or joining family", reck: true },
    { v: "4",      label: "Stamp 4 – long-term, spouse of Irish citizen, refugee…", reck: true },
    { v: "4D",     label: "Stamp 4D – family of a UK citizen", reck: true, note: "Usually entered as Stamp 4 – confirm with ISD." },
    { v: "4EU",    label: "Stamp 4 EU FAM – family of an EU citizen", reck: true, note: "Residence under EU Treaty Rights – confirm with ISD." },
    { v: "5",      label: "Stamp 5 – without condition as to time", reck: true },
    { v: "0",      label: "Stamp 0 – temporary / independent means", reck: false },
    { v: "2",      label: "Stamp 2 – student (ILEP course)", reck: false },
    { v: "2A",     label: "Stamp 2A – student (non-ILEP course)", reck: false },
    { v: "IP",     label: "International protection applicant (asylum)", reck: false },
    { v: "NONE",   label: "No valid permission / waiting for renewal", reck: false }
  ];
  var BY = {}; STAMPS.forEach(function (s) { BY[s.v] = s; });

  var KEY = "tavion_citizenship_v1";
  var DAY = 86400000;

  // ---- date helpers (UTC day numbers) ----
  function toDay(str) { if (!str) return null; var p = str.split("-"); if (p.length !== 3) return null; var t = Date.UTC(+p[0], +p[1] - 1, +p[2]); return isNaN(t) ? null : Math.floor(t / DAY); }
  function toStr(d) { var x = new Date(d * DAY); return x.toISOString().slice(0, 10); }
  function nice(d) { return new Date(d * DAY).toLocaleDateString("en-IE", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }); }
  function todayDay() { var n = new Date(); return Math.floor(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()) / DAY); }
  function addYears(d, y) {
    var x = new Date(d * DAY), m = x.getUTCMonth(), day = x.getUTCDate();
    var t = new Date(Date.UTC(x.getUTCFullYear() + y, m, day));
    if (t.getUTCMonth() !== m) t = new Date(Date.UTC(x.getUTCFullYear() + y, m + 1, 0)); // 29 Feb -> 28 Feb
    return Math.floor(t.getTime() / DAY);
  }
  function fmt(n) { return n.toLocaleString("en-IE"); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  // ---- core calculation ----
  // state: { route: "standard"|"spouse", appDate: "YYYY-MM-DD", assume: bool, stamps: [{type, from, to}], trips: [{out, back}] }
  function compute(state, today) {
    var years = state.route === "spouse" ? 5 : 9;
    var target = state.route === "spouse" ? 1096 : 1826; // ISD: "1825 or 1826" / "1095 or 1096" – we use the safer figure
    var issues = [];

    var stamps = [];
    state.stamps.forEach(function (s, i) {
      var f = toDay(s.from), t = toDay(s.to);
      if (f === null && t === null) return;
      if (f === null || t === null) { issues.push({ level: "warn", text: "Permission " + (i + 1) + " is missing a start or end date, so it was skipped." }); return; }
      if (t < f) { issues.push({ level: "warn", text: "Permission " + (i + 1) + " ends before it starts, so it was skipped." }); return; }
      stamps.push({ i: i, type: s.type, f: f, t: t, meta: BY[s.type] || BY.NONE });
    });
    var trips = [];
    state.trips.forEach(function (tr, i) {
      var o = toDay(tr.out), b = toDay(tr.back);
      if (o === null && b === null) return;
      if (o === null) { issues.push({ level: "warn", text: "Trip " + (i + 1) + " has no departure date, so it was skipped." }); return; }
      if (b === null) b = Math.max(o, today); // still abroad
      if (b < o) { issues.push({ level: "warn", text: "Trip " + (i + 1) + " returns before it leaves, so it was skipped." }); return; }
      trips.push({ o: o, b: b });
    });

    var app = toDay(state.appDate) || today;
    var reck = stamps.filter(function (s) { return s.meta.reck; });
    if (!reck.length) return { empty: true, issues: issues, target: target, years: years };

    var min = Math.min.apply(null, stamps.map(function (s) { return s.f; }).concat(trips.map(function (t) { return t.o; }), [app])) - 1;
    var max = Math.max.apply(null, stamps.map(function (s) { return s.t; }).concat([app, today + 3660])) + 1;
    var N = max - min + 1;
    var perm = new Uint8Array(N), away = new Uint8Array(N);

    // Projection: assume the latest reckonable permission is renewed without gaps.
    var latest = reck.reduce(function (a, b) { return b.t > a.t ? b : a; });
    var project = !!state.assume && latest.t >= today; // only project a permission that is still current
    reck.forEach(function (s) {
      var end = (project && s === latest) ? max : s.t;
      for (var d = s.f; d <= end; d++) perm[d - min] = 1;
    });
    // A "day" excludes part of a day: travel days count as present, only full days abroad count as absent.
    trips.forEach(function (t) { for (var d = t.o + 1; d <= t.b - 1; d++) away[d - min] = 1; });

    var P = new Int32Array(N + 1), A = new Int32Array(N + 1), S = new Int32Array(N + 1), run = new Int32Array(N);
    for (var k = 0; k < N; k++) {
      P[k + 1] = P[k] + perm[k];
      A[k + 1] = A[k] + away[k];
      S[k + 1] = S[k] + (perm[k] && !away[k] ? 1 : 0);
      run[k] = perm[k] ? (k ? run[k - 1] : 0) + 1 : 0;
    }
    function sum(arr, a, b) { a = Math.max(a, min); b = Math.min(b, max); if (b < a) return 0; return arr[b - min + 1] - arr[a - min]; }

    function evaluate(D) {
      var ws = addYears(D, -years);
      var total = sum(P, ws, D);
      var inIreland = sum(S, ws, D);
      var cont = D >= min && D <= max ? run[D - min] : 0;
      var absYear = sum(A, D - 364, D);
      var absEarlier = sum(A, ws, D - 365);
      var ok = total >= target && cont >= 365 && absYear <= 70;
      return { D: D, ws: ws, total: total, inIreland: inIreland, cont: cont, absYear: absYear, absEarlier: absEarlier, ok: ok, okExceptional: !ok && total >= target && cont >= 365 && absYear <= 100 };
    }

    var res = evaluate(app);

    // When can they apply? If they qualify today, find when that run of eligibility began;
    // otherwise find the next date from today on which all conditions are met.
    var earliest = null, earliestExc = null, eligibleNow = evaluate(today).ok;
    if (eligibleNow) {
      var since = today;
      while (since - 1 > min && evaluate(since - 1).ok) since--;
      earliest = evaluate(since);
    } else {
      for (var D = today; D <= max - 1; D++) {
        var e = evaluate(D);
        if (e.ok) { earliest = e; break; }
        if (!earliestExc && e.okExceptional) earliestExc = e;
      }
    }

    // Per-permission breakdown within the window (overlaps counted once, oldest first).
    var seen = {}, breakdown = [];
    stamps.slice().sort(function (a, b) { return a.f - b.f; }).forEach(function (s) {
      var n = 0;
      if (s.meta.reck) {
        var end = (project && s === latest) ? Math.max(s.t, app) : s.t;
        for (var d = Math.max(s.f, res.ws); d <= Math.min(end, app); d++) if (!seen[d]) { seen[d] = 1; n++; }
      }
      breakdown.push({ s: s, counted: n, projected: project && s === latest && app > s.t });
    });

    // Gaps between reckonable permissions inside the window.
    var gaps = [], inGap = false, gs = 0;
    for (var g = Math.max(res.ws, min); g <= app; g++) {
      var covered = perm[g - min] === 1;
      if (!covered && !inGap && g > Math.min.apply(null, reck.map(function (s) { return s.f; }))) { inGap = true; gs = g; }
      if (covered && inGap) { inGap = false; gaps.push([gs, g - 1]); }
    }
    if (inGap) gaps.push([gs, app]);

    // Other warnings
    if (stamps.some(function (s) { return !s.meta.reck; })) issues.push({ level: "info", text: "Time on Stamp 0, 2, 2A, as an international protection applicant, or without a valid permission is not counted." });
    if (latest.t < today) issues.push({ level: "bad", text: "Your latest permission that counts expired on " + nice(latest.t) + ". Time without a valid permission is not reckonable – renew or register before applying." });
    else if (!project && app > latest.t) issues.push({ level: "bad", text: "Your latest permission ends on " + nice(latest.t) + ", before the application date. ISD expects you to apply while your current permission is still valid." });
    if (gaps.length) issues.push({ level: "warn", text: "There " + (gaps.length === 1 ? "is a gap" : "are " + gaps.length + " gaps") + " between your permissions: " + gaps.slice(0, 4).map(function (x) { return nice(x[0]) + " – " + nice(x[1]) + " (" + fmt(x[1] - x[0] + 1) + " days)"; }).join("; ") + (gaps.length > 4 ? "…" : "") + ". Gaps are not reckonable, and a gap in the final year breaks continuous residence." });
    var longTrip = trips.filter(function (t) { return t.b - t.o - 1 > 180; });
    if (longTrip.length) issues.push({ level: "warn", text: "You have " + longTrip.length + " trip(s) abroad longer than 6 months. ISD asks applicants who spent long periods abroad to explain them in detail." });
    if (res.absEarlier > 0) issues.push({ level: "info", text: "You were abroad for " + fmt(res.absEarlier) + " full days in the earlier years of the window. ISD's calculator counts your permission days, but the law refers to residence in Ireland, so long absences may be questioned." });
    var appMeta = latest.meta;
    if (appMeta.note) issues.push({ level: "info", text: appMeta.label.split(" – ")[0] + ": " + appMeta.note });

    return { project: project, eligibleNow: eligibleNow, res: res, earliest: earliest, earliestExc: earliestExc, breakdown: breakdown, issues: issues, target: target, years: years, app: app, today: today, latest: latest };
  }

  // ---- UI ----
  var state;
  function defaults() {
    return { route: "standard", appDate: toStr(todayDay()), assume: true, stamps: [{ type: "1", from: "", to: "" }], trips: [] };
  }
  function load() {
    try { var s = JSON.parse(localStorage.getItem(KEY)); if (s && s.stamps) return s; } catch (e) {}
    return defaults();
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  function stampOptions(sel) {
    var h = '<optgroup label="Counts towards citizenship">';
    STAMPS.forEach(function (s, i) {
      if (i === STAMPS.findIndex(function (x) { return !x.reck; })) h += '</optgroup><optgroup label="Does not count">';
      h += '<option value="' + s.v + '"' + (s.v === sel ? " selected" : "") + ">" + esc(s.label) + "</option>";
    });
    return h + "</optgroup>";
  }

  function renderRows() {
    var sh = "";
    state.stamps.forEach(function (s, i) {
      var meta = BY[s.type] || BY.NONE;
      sh += '<div class="row-card" data-i="' + i + '">' +
        '<div class="row-head"><strong>Permission ' + (i + 1) + '</strong>' +
        '<span class="pill ' + (meta.reck ? "yes" : "no") + '">' + (meta.reck ? "Counts" : "Doesn't count") + "</span>" +
        '<button type="button" class="link-btn" data-del-stamp="' + i + '" aria-label="Remove permission ' + (i + 1) + '">Remove</button></div>' +
        '<label>Stamp type<select data-f="type">' + stampOptions(s.type) + "</select></label>" +
        '<div class="two"><label>From<input type="date" data-f="from" value="' + esc(s.from) + '"></label>' +
        '<label>To (expiry)<input type="date" data-f="to" value="' + esc(s.to) + '"></label></div></div>';
    });
    document.getElementById("stamps").innerHTML = sh;

    var th = "";
    state.trips.forEach(function (t, i) {
      th += '<div class="row-card trip" data-t="' + i + '">' +
        '<div class="row-head"><strong>Trip ' + (i + 1) + '</strong><button type="button" class="link-btn" data-del-trip="' + i + '" aria-label="Remove trip ' + (i + 1) + '">Remove</button></div>' +
        '<div class="two"><label>Left Ireland<input type="date" data-f="out" value="' + esc(t.out) + '"></label>' +
        '<label>Returned<input type="date" data-f="back" value="' + esc(t.back) + '"></label></div></div>';
    });
    document.getElementById("trips").innerHTML = th || '<p class="muted small">No trips added. Add any time you spent outside Ireland, especially in the last 12 months.</p>';
  }

  function tile(label, val, goal, ok, sub) {
    return '<div class="tile ' + (ok ? "ok" : "bad") + '"><div class="tl">' + label + '</div><div class="tv">' + val + (goal ? '<span> / ' + goal + "</span>" : "") + '</div>' + (sub ? '<div class="ts">' + sub + "</div>" : "") + "</div>";
  }

  function renderResult(scroll) {
    var out = document.getElementById("result");
    var r = compute(state, todayDay());
    if (r.empty) {
      out.innerHTML = '<div class="verdict neutral"><h2>Add your permissions</h2><p>Enter at least one permission that counts (for example Stamp 1, 1G, 3 or 4) with its start and expiry dates.</p></div>' + issuesHtml(r.issues);
      return r;
    }
    var x = r.res, h = "";
    var routeTxt = state.route === "spouse" ? "3-year spouse / civil partner" : "5-year residence";

    if (x.ok) {
      h += '<div class="verdict good"><div class="big">✅</div><h2>You meet the residence requirement on ' + nice(r.app) + "</h2><p>Based on the " + routeTxt + " route and the dates you entered.</p></div>";
    } else {
      var why = [];
      if (x.total < r.target) why.push("you are <strong>" + fmt(r.target - x.total) + " days short</strong> of " + fmt(r.target) + " reckonable days");
      if (x.cont < 365) why.push("you only have <strong>" + fmt(x.cont) + " days</strong> of unbroken permission before this date (365 needed)");
      if (x.absYear > 70) why.push("you were abroad for <strong>" + x.absYear + " days</strong> in the year before (limit 70" + (x.absYear <= 100 ? ", or up to 100 in exceptional circumstances" : "") + ")");
      h += '<div class="verdict bad"><div class="big">⏳</div><h2>Not yet on ' + nice(r.app) + "</h2><p>On that date " + why.join("; ") + ".</p></div>";
    }

    if (r.earliest) {
      var e = r.earliest;
      h += '<div class="earliest"><div class="tl">' + (e.D <= r.today ? "You've been eligible since" : "Earliest date you can apply") + '</div><div class="ed">' + nice(e.D) + "</div>" +
        (e.D > r.today ? '<div class="ts">That\'s ' + fmt(e.D - r.today) + " days from today" + (r.project && e.D > r.latest.t ? ", assuming your permission is renewed with no gaps" : "") + ".</div>" : '<div class="ts">Apply while your current permission is valid and keep it renewed.</div>') +
        '<a class="btn small-btn" href="#" id="useEarliest">Check this date</a></div>';
      if (r.earliestExc && r.earliestExc.D < r.earliest.D) {
        h += '<div class="earliest warn"><div class="tl">Possibly sooner, with exceptional circumstances</div><div class="ed">' + nice(r.earliestExc.D) + '</div><div class="ts">From this date your absences in the final year are 100 days or fewer. Absences over 70 days are only accepted if ISD agrees they were due to exceptional circumstances (for example family, health, work or study reasons).</div></div>';
      }
    } else if (r.earliestExc) {
      h += '<div class="earliest warn"><div class="tl">Possible from (exceptional circumstances only)</div><div class="ed">' + nice(r.earliestExc.D) + '</div><div class="ts">Your absences in the final year are between 71 and 100 days. This is only allowed if ISD accepts exceptional circumstances.</div></div>';
    } else {
      h += '<div class="earliest warn"><div class="tl">Earliest date</div><div class="ed">Not found</div><div class="ts">With the dates entered you don\'t reach the requirement within the next 10 years. Check for gaps or non-reckonable stamps' + (state.assume ? "" : ', or tick "assume renewals"') + ".</div></div>";
    }

    h += '<div class="tiles">' +
      tile("Reckonable days", fmt(x.total), fmt(r.target), x.total >= r.target, "in the " + r.years + " years before " + nice(r.app)) +
      tile("Unbroken final year", fmt(Math.min(x.cont, 9999)), "365", x.cont >= 365, "days of continuous permission") +
      tile("Days abroad, final year", fmt(x.absYear), "70", x.absYear <= 70, "+30 in exceptional circumstances") +
      tile("Days physically in Ireland", fmt(x.inIreland), fmt(r.target), x.inIreland >= r.target, "stricter view, absences removed") +
      "</div>";

    h += '<h3>How your permissions were counted</h3><div class="table-wrap"><table><thead><tr><th>Permission</th><th>Dates</th><th>Days counted</th></tr></thead><tbody>';
    r.breakdown.forEach(function (b) {
      h += "<tr><td>" + esc(b.s.meta.label.split(" – ")[0]) + (b.s.meta.reck ? "" : ' <span class="pill no">not counted</span>') + "</td><td>" + nice(b.s.f) + " – " + nice(b.s.t) + (b.projected ? '<br><span class="muted small">+ assumed renewal to ' + nice(r.app) + "</span>" : "") + "</td><td>" + fmt(b.counted) + "</td></tr>";
    });
    h += "</tbody></table></div><p class=\"muted small\">Window counted: " + nice(x.ws) + " – " + nice(r.app) + ". Overlapping permissions are only counted once.</p>";

    h += issuesHtml(r.issues);
    h += '<div class="btn-row no-print"><button class="btn" type="button" onclick="window.print()">🖨️ Print / save as PDF</button>' +
      '<a class="btn wa" data-track="share" data-method="whatsapp" data-label="citizenship_result" target="_blank" rel="noopener" href="https://wa.me/?text=' + encodeURIComponent("I just worked out when I can apply for Irish citizenship with this free calculator 🇮🇪 https://tavion.ie/citizenship/") + '">Share on WhatsApp</a></div>';

    out.innerHTML = h;
    var ue = document.getElementById("useEarliest");
    if (ue) ue.onclick = function (ev) { ev.preventDefault(); state.appDate = toStr(r.earliest.D); document.getElementById("appDate").value = state.appDate; save(); renderResult(true); };
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
    return r;
  }

  function issuesHtml(issues) {
    if (!issues.length) return "";
    return '<h3>Things to check</h3><ul class="issues">' + issues.map(function (i) { return '<li class="' + i.level + '">' + esc(i.text) + "</li>"; }).join("") + "</ul>";
  }

  function bind() {
    var form = document.getElementById("calc");
    form.addEventListener("input", function (e) {
      var el = e.target, f = el.getAttribute("data-f");
      var row = el.closest("[data-i]"), trip = el.closest("[data-t]");
      if (row && f) { state.stamps[+row.getAttribute("data-i")][f] = el.value; if (f === "type") renderRows(); }
      else if (trip && f) state.trips[+trip.getAttribute("data-t")][f] = el.value;
      else if (el.name === "route") state.route = el.value;
      else if (el.id === "appDate") state.appDate = el.value;
      else if (el.id === "assume") state.assume = el.checked;
      save();
    });
    form.addEventListener("click", function (e) {
      var t = e.target, i;
      if ((i = t.getAttribute("data-del-stamp")) !== null) { state.stamps.splice(+i, 1); if (!state.stamps.length) state.stamps.push({ type: "1", from: "", to: "" }); }
      else if ((i = t.getAttribute("data-del-trip")) !== null) state.trips.splice(+i, 1);
      else if (t.id === "addStamp") {
        var last = state.stamps[state.stamps.length - 1], next = "";
        if (last && last.to) { var d = toDay(last.to); if (d !== null) next = toStr(d + 1); }
        state.stamps.push({ type: last ? last.type : "1", from: next, to: "" });
        if (window.TAVION && TAVION.track) TAVION.track("calc_add_permission", { count: state.stamps.length });
      }
      else if (t.id === "addTrip") state.trips.push({ out: "", back: "" });
      else if (t.id === "clearAll") { if (!confirmClear()) return; state = defaults(); syncTop(); document.getElementById("result").innerHTML = ""; }
      else return;
      save(); renderRows();
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var r = renderResult(true);
      if (window.TAVION && TAVION.track && !r.empty) {
        TAVION.track("calc_run", { route: state.route, result: r.res.ok ? "eligible" : "not_yet", permissions: state.stamps.length, trips: state.trips.length,
          days_to_eligible: r.earliest ? Math.max(0, r.earliest.D - r.today) : -1 });
      }
    });
  }
  var clearArmed = false;
  function confirmClear() {
    var b = document.getElementById("clearAll");
    if (clearArmed) { clearArmed = false; b.textContent = "Clear all"; return true; }
    clearArmed = true; b.textContent = "Tap again to clear everything";
    setTimeout(function () { clearArmed = false; b.textContent = "Clear all"; }, 4000);
    return false;
  }
  function syncTop() {
    document.getElementById("appDate").value = state.appDate;
    document.getElementById("assume").checked = !!state.assume;
    [].forEach.call(document.querySelectorAll('input[name="route"]'), function (r) { r.checked = r.value === state.route; });
    renderRows();
  }

  window.CitizenshipCalc = { compute: compute, STAMPS: STAMPS, toDay: toDay, nice: nice };

  if (document.getElementById("calc")) {
    state = load();
    if (!state.appDate) state.appDate = toStr(todayDay());
    syncTop(); bind();
    if (state.stamps.some(function (s) { return s.from && s.to; })) renderResult(false);
  }
})();
