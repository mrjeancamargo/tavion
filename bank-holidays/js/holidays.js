/*
 * IEHOL – Irish public (bank) holidays, school breaks and an annual-leave planner.
 * Rules: Organisation of Working Time Act 1997 (as amended) – see Citizens Information "Public holidays".
 *   https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/leave-and-holidays/public-holidays/
 * School breaks: Department of Education Circular 0018/2026.
 * Used by the planner in the browser and by tools/build_holidays.py (through Node).
 */
(function (root) {
  var NAMES = {
    newyear: "New Year's Day", brigid: "St Brigid's Day", patrick: "St Patrick's Day", easter: "Easter Monday", may: "May Bank Holiday",
    june: "June Bank Holiday", august: "August Bank Holiday", october: "October Bank Holiday", christmas: "Christmas Day", stephen: "St Stephen's Day"
  };
  var ORDER = ["newyear", "brigid", "patrick", "easter", "may", "june", "august", "october", "christmas", "stephen"];
  var DAY = 86400000;
  function d(y, m, day) { return new Date(Date.UTC(y, m - 1, day)); }
  function iso(dt) { return dt.toISOString().slice(0, 10); }
  function parse(s) { var p = s.split("-"); return d(+p[0], +p[1], +p[2]); }
  function add(dt, n) { return new Date(dt.getTime() + n * DAY); }
  function dow(dt) { return dt.getUTCDay(); } // 0 Sun .. 6 Sat

  // Easter Sunday (Anonymous Gregorian algorithm)
  function easterSunday(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, dd = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3),
      h = (19 * a + b - dd - g + 15) % 30, i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451),
      month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
    return d(y, month, day);
  }
  function firstMonday(y, m) { var x = d(y, m, 1); while (dow(x) !== 1) x = add(x, 1); return x; }
  function lastMonday(y, m) { var x = d(y, m + 1, 1); x = add(x, -1); while (dow(x) !== 1) x = add(x, -1); return x; }

  function publicHolidays(y) {
    var feb1 = d(y, 2, 1);
    var list = [
      ["newyear", d(y, 1, 1)],
      ["brigid", dow(feb1) === 5 ? feb1 : firstMonday(y, 2)],
      ["patrick", d(y, 3, 17)],
      ["easter", add(easterSunday(y), 1)],
      ["may", firstMonday(y, 5)], ["june", firstMonday(y, 6)], ["august", firstMonday(y, 8)], ["october", lastMonday(y, 10)],
      ["christmas", d(y, 12, 25)], ["stephen", d(y, 12, 26)]
    ];
    if (y < 2023) list.splice(1, 1); // St Brigid's Day public holiday from 2023
    return list.map(function (x) { var w = dow(x[1]); return { key: x[0], name: NAMES[x[0]], date: iso(x[1]), weekday: w, weekend: w === 0 || w === 6 }; });
  }

  // School breaks (Circular 0018/2026). Post-primary dates for February; primary schools may close only Thu–Fri.
  var SCHOOL = {
    "2026-27": [["October mid-term", "2026-10-26", "2026-10-30"], ["Christmas", "2026-12-23", "2027-01-05"], ["February mid-term", "2027-02-15", "2027-02-19"], ["Easter", "2027-03-22", "2027-04-02"]],
    "2027-28": [["October mid-term", "2027-10-25", "2027-10-29"], ["Christmas", "2027-12-23", "2028-01-05"], ["February mid-term", "2028-02-21", "2028-02-25"], ["Easter", "2028-04-10", "2028-04-21"]],
    "2028-29": [["October mid-term", "2028-10-30", "2028-11-03"], ["Christmas", "2028-12-23", "2029-01-05"], ["February mid-term", "2029-02-12", "2029-02-16"], ["Easter", "2029-03-26", "2029-04-06"]]
  };

  function isOff(dt, holSet, workDays) { return workDays.indexOf(dow(dt)) < 0 || !!holSet[iso(dt)]; }

  /*
   * plan(year, leave, opts) – best way to spend `leave` days of annual leave for the most consecutive days off.
   * opts: { workDays: [1,2,3,4,5], from: "YYYY-MM-DD" (skip dates before), maxBlock: 9 }
   * Builds candidate breaks (runs of working days bridged between days off) and picks the best non-overlapping set
   * with a knapsack over leave days (most days off; ties – fewer leave days, then earlier).
   */
  function plan(year, leave, opts) {
    opts = opts || {};
    var workDays = opts.workDays || [1, 2, 3, 4, 5], maxBlock = opts.maxBlock || 9;
    var hols = publicHolidays(year), holSet = {};
    hols.forEach(function (h) { holSet[h.date] = h.name; });
    var start = d(year, 1, 1), end = d(year, 12, 31), from = opts.from ? parse(opts.from) : start;
    if (from > start) start = from;
    var days = [];
    for (var x = start; x <= end; x = add(x, 1)) days.push({ dt: x, off: isOff(x, holSet, workDays), hol: holSet[iso(x)] || null });
    var n = days.length, cands = [];
    // candidate = take leave on working days i..j (consecutive), extend to the surrounding days off
    for (var i = 0; i < n; i++) {
      if (days[i].off) continue;
      var used = 0;
      for (var j = i; j < n && used < Math.min(leave, maxBlock); j++) {
        if (!days[j].off) used++;
        if (days[j].off) continue;
        if (j + 1 < n && !days[j + 1].off) continue; // must end next to a day off (or year end)
        if (i > 0 && !days[i - 1].off) continue;      // must start next to a day off
        var s = i, e = j;
        while (s > 0 && days[s - 1].off) s--;
        while (e < n - 1 && days[e + 1].off) e++;
        var hasHol = false; for (var k = s; k <= e; k++) if (days[k].hol) hasHol = true;
        cands.push({ s: s, e: e, leaveFrom: i, leaveTo: j, leave: used, total: e - s + 1, hol: hasHol });
      }
    }
    cands.sort(function (a, b) { return a.e - b.e || a.s - b.s; });
    // weighted interval scheduling with a leave budget
    var m = cands.length, L = leave, prev = cands.map(function (c, idx) { for (var p = idx - 1; p >= 0; p--) if (cands[p].e < c.s - 0) return p; return -1; });
    var best = [], choice = [];
    for (var a = 0; a <= m; a++) { best.push(new Array(L + 1).fill(0)); choice.push(new Array(L + 1).fill(false)); }
    for (a = 1; a <= m; a++) {
      var c = cands[a - 1];
      for (var b = 0; b <= L; b++) {
        var skip = best[a - 1][b], take = -1;
        if (c.leave <= b) take = best[prev[a - 1] + 1][b - c.leave] + c.total + (c.hol ? 0.01 : 0);
        if (take > skip) { best[a][b] = take; choice[a][b] = true; } else best[a][b] = skip;
      }
    }
    var picks = [], bb = L;
    for (a = m; a > 0;) { if (choice[a][bb]) { var cc = cands[a - 1]; picks.unshift(cc); bb -= cc.leave; a = prev[a - 1] + 1; } else a--; }
    var breaks = picks.map(function (p) {
      var hn = []; for (var k = p.s; k <= p.e; k++) if (days[k].hol) hn.push(days[k].hol);
      return { from: iso(days[p.s].dt), to: iso(days[p.e].dt), leaveFrom: iso(days[p.leaveFrom].dt), leaveTo: iso(days[p.leaveTo].dt), leave: p.leave, daysOff: p.total, holidays: hn };
    });
    var usedLeave = breaks.reduce(function (s, x) { return s + x.leave; }, 0), off = breaks.reduce(function (s, x) { return s + x.daysOff; }, 0);
    return { year: year, leave: leave, used: usedLeave, daysOff: off, breaks: breaks, ratio: usedLeave ? off / usedLeave : 0 };
  }

  // Long weekends: public holidays on Monday/Friday (3 days) and others.
  function yearSummary(y) {
    var hols = publicHolidays(y), weekendDays = 0;
    for (var x = d(y, 1, 1); x <= d(y, 12, 31); x = add(x, 1)) if (dow(x) === 0 || dow(x) === 6) weekendDays++;
    var weekday = hols.filter(function (h) { return !h.weekend; }).length;
    var longW = hols.filter(function (h) { return h.weekday === 1 || h.weekday === 5; }).length;
    return { year: y, holidays: hols, weekdayHolidays: weekday, weekendHolidays: 10 - weekday - (y < 2023 ? -1 : 0), longWeekends: longW, weekendDays: weekendDays, freeDays: weekendDays + weekday };
  }
  function nextHoliday(today) {
    var t = today ? parse(today) : d(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate());
    var y = t.getUTCFullYear(), all = publicHolidays(y).concat(publicHolidays(y + 1));
    for (var i = 0; i < all.length; i++) { var h = parse(all[i].date); if (h >= t) return { holiday: all[i], days: Math.round((h - t) / DAY) }; }
    return null;
  }
  // Annual leave (Organisation of Working Time Act): best of 4 working weeks (1,365+ hours), 1/3 week per 117-hour month, or 8% of hours (max 4 weeks).
  function annualLeave(hoursWorked, daysPerWeek, hoursPerDay, months117) {
    var week = daysPerWeek * hoursPerDay, maxH = 4 * week;
    var m1 = hoursWorked >= 1365 ? maxH : 0, m2 = Math.min(maxH, (months117 || 0) * week / 3), m3 = Math.min(maxH, hoursWorked * 0.08);
    var h = Math.max(m1, m2, m3);
    return { hours: Math.round(h * 10) / 10, days: hoursPerDay ? Math.round(h / hoursPerDay * 10) / 10 : 0, method: h === m1 ? 1 : h === m2 ? 2 : 3 };
  }
  function ics(years) {
    var lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Tavion//Irish public holidays//EN", "CALSCALE:GREGORIAN", "X-WR-CALNAME:Ireland public holidays"];
    years.forEach(function (y) { publicHolidays(y).forEach(function (h) {
      var s = h.date.replace(/-/g, ""), e = iso(add(parse(h.date), 1)).replace(/-/g, "");
      lines.push("BEGIN:VEVENT", "UID:" + s + "-" + h.key + "@tavion.ie", "DTSTAMP:" + s + "T000000Z", "DTSTART;VALUE=DATE:" + s, "DTEND;VALUE=DATE:" + e, "SUMMARY:" + h.name + " (public holiday)", "TRANSP:TRANSPARENT", "END:VEVENT");
    }); });
    lines.push("END:VCALENDAR");
    return lines.join("\r\n") + "\r\n";
  }
  var api = { NAMES: NAMES, ORDER: ORDER, SCHOOL: SCHOOL, easterSunday: function (y) { return iso(easterSunday(y)); }, publicHolidays: publicHolidays, plan: plan,
    yearSummary: yearSummary, nextHoliday: nextHoliday, annualLeave: annualLeave, ics: ics };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.IEHOL = api;
})(this);
