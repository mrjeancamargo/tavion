/*
 * IECAO – CAO points engine (Leaving Certificate, Irish CAO system).
 * Source: CAO "Irish Leaving Certificate Examination Points Calculation Grid"
 *   https://www.cao.ie/index.php?page=scoring&s=lcepointsgrid
 * Used by the calculator in the browser and by tools/build_cao.py (through Node), so both always agree.
 */
(function (root) {
  var HIGHER = { H1: 100, H2: 88, H3: 77, H4: 66, H5: 56, H6: 46, H7: 37, H8: 0 };
  var ORDINARY = { O1: 56, O2: 46, O3: 37, O4: 28, O5: 20, O6: 12, O7: 0, O8: 0 };
  var FOUNDATION = { F1: 20, F2: 12, F3: 0, F4: 0, F5: 0, F6: 0, F7: 0, F8: 0 }; // maths/Irish only, and only some colleges count it
  var LCVP = { Distinction: 66, Merit: 46, Pass: 28 };
  var MATHS_BONUS = 25;          // Higher Level Maths, H6 or better
  var MAX_POINTS = 625;          // 6 x H1 (600) + maths bonus (25)
  var MED = { minPoints: 480, hpatMax: 150, from: 2027 }; // UG medicine: LC points (no longer moderated above 550) + HPAT weighted to 150

  var SUBJECTS = ["English", "Irish", "Mathematics", "French", "German", "Spanish", "Italian", "Japanese", "Chinese (Mandarin)", "Russian", "Polish", "Lithuanian",
    "Portuguese", "Arabic", "Latin", "Ancient Greek", "Classical Studies", "Biology", "Chemistry", "Physics", "Physics and Chemistry", "Agricultural Science",
    "Applied Mathematics", "Computer Science", "Accounting", "Business", "Economics", "Geography", "History", "Politics and Society", "Religious Education",
    "Art", "Music", "Home Economics", "Physical Education", "Engineering", "Construction Studies", "Design and Communication Graphics", "Technology",
    "Agricultural Economics", "Hebrew Studies", "Other language", "Other subject"];

  function gradePoints(grade, subject, opts) {
    opts = opts || {};
    if (!grade) return 0;
    var g = String(grade).toUpperCase();
    var p = 0;
    if (HIGHER.hasOwnProperty(g)) {
      p = HIGHER[g];
      if (subject === "Mathematics" && p >= HIGHER.H6) p += MATHS_BONUS;
    } else if (ORDINARY.hasOwnProperty(g)) {
      p = ORDINARY[g];
    } else if (FOUNDATION.hasOwnProperty(g)) {
      p = opts.countFoundation ? FOUNDATION[g] : 0;
    }
    return p;
  }

  /*
   * subjects: [{subject:"English", grade:"H3"}, ...]  lcvp: "Distinction"|"Merit"|"Pass"|""
   * Best six results count (LCVP Link Modules can replace a sixth subject).
   */
  function calculate(subjects, lcvp, opts) {
    var rows = (subjects || []).filter(function (s) { return s && s.grade; }).map(function (s) {
      var pts = gradePoints(s.grade, s.subject, opts);
      var bonus = (s.subject === "Mathematics" && HIGHER.hasOwnProperty(String(s.grade).toUpperCase()) && HIGHER[String(s.grade).toUpperCase()] >= HIGHER.H6) ? MATHS_BONUS : 0;
      return { subject: s.subject || "Subject", grade: String(s.grade).toUpperCase(), points: pts, bonus: bonus, counted: false };
    });
    if (lcvp && LCVP[lcvp]) rows.push({ subject: "LCVP Link Modules", grade: lcvp, points: LCVP[lcvp], bonus: 0, counted: false, lcvp: true });
    var order = rows.slice().sort(function (a, b) { return b.points - a.points; });
    var total = 0, bonus = 0;
    order.slice(0, 6).forEach(function (r) { r.counted = true; total += r.points; bonus += r.bonus; });
    var dropped = order.slice(6).filter(function (r) { return r.points > 0; });
    var tips = [];
    var maths = rows.filter(function (r) { return r.subject === "Mathematics"; })[0];
    if (maths && /^O[1-2]$/.test(maths.grade)) tips.push("A H7 in Higher Maths is worth 37 points; a H6 is worth 71 with the 25-point bonus – more than an " + maths.grade + " in Ordinary (" + maths.points + ").");
    if (maths && maths.grade === "H7") tips.push("One grade higher in Higher Maths (H6) would add 34 points: 9 for the grade plus the 25-point bonus.");
    if (!lcvp && rows.length < 6) tips.push("Did you take LCVP? A Distinction in the Link Modules is worth 66 points and can count instead of a sixth subject.");
    return { total: total, bonus: bonus, rows: rows, counted: order.slice(0, 6), dropped: dropped, subjectsEntered: rows.length, max: MAX_POINTS, tips: tips };
  }

  // CAO points strings: "452", "590*", "#816", "AQA", "#AQA", "v300", "" ...
  function parsePoints(s) {
    if (s === null || s === undefined) return null;
    s = String(s).trim();
    if (!s) return null;
    var out = { raw: s, value: null, random: s.indexOf("*") >= 0, test: s.indexOf("#") >= 0, aqa: /AQA/i.test(s), newComp: /v/.test(s) };
    var m = s.match(/(\d{2,4})/);
    if (m) out.value = parseInt(m[1], 10);
    return out;
  }

  /*
   * Rate a course against an applicant's points, using the latest Round 1 cut-off.
   * Returns "safe" (10+ above), "likely" (0-9 above), "close" (up to 20 below), "reach" (more than 20 below), "aqa" or "special" (portfolio/HPAT-scale).
   */
  function chance(points, cut) {
    if (!cut) return "unknown";
    if (cut.aqa) return "aqa";
    if (cut.value === null) return "unknown";
    if (cut.value > MAX_POINTS) return "special";
    var d = points - cut.value;
    if (d >= 10) return "safe";
    if (d >= 0) return "likely";
    if (d >= -20) return "close";
    return "reach";
  }

  /*
   * Course finder. courses: compact rows from cao/data/courses.json
   *   [code, title, collegeCode, level, county, area, r1_2026, r1_2025, flags, slug]
   * filters: {area, county, level, college}
   * Returns the best matches: courses the points reach, closest cut-off first (they're usually the most sought-after you can get),
   * then a few "worth a try" courses just above the points.
   */
  function findCourses(points, courses, filters, limit) {
    filters = filters || {}; limit = limit || 15;
    var within = [], stretch = [];
    courses.forEach(function (c) {
      if (filters.area && c[5] !== filters.area) return;
      if (filters.county && c[4] !== filters.county) return;
      if (filters.level && String(c[3]) !== String(filters.level) && !(filters.level === "7" && c[3] === 6)) return;
      if (filters.college && c[2] !== filters.college) return;
      var cut = parsePoints(c[6] || c[7]);
      if (!cut || cut.value === null && !cut.aqa) return;
      if (cut.value > MAX_POINTS || cut.test) return; // portfolio / test / HPAT scores can't be compared with Leaving Cert points alone
      var v = cut.aqa ? 0 : cut.value;
      var row = { c: c, cut: cut, gap: points - v, chance: chance(points, cut) };
      if (v <= points) within.push(row); else if (v - points <= 30) stretch.push(row);
    });
    within.sort(function (a, b) { return a.gap - b.gap; });
    stretch.sort(function (a, b) { return (b.gap) - (a.gap); });
    var nStretch = Math.min(stretch.length, Math.max(3, limit - within.length));
    return { within: within.slice(0, limit), stretch: stretch.slice(0, Math.min(5, nStretch)), totalWithin: within.length };
  }

  var api = { HIGHER: HIGHER, ORDINARY: ORDINARY, FOUNDATION: FOUNDATION, LCVP: LCVP, MATHS_BONUS: MATHS_BONUS, MAX_POINTS: MAX_POINTS, MED: MED, SUBJECTS: SUBJECTS,
    gradePoints: gradePoints, calculate: calculate, parsePoints: parsePoints, chance: chance, findCourses: findCourses };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.IECAO = api;
})(this);
