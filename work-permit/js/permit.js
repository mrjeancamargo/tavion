// Irish employment permit minimum annual remuneration (MAR) rules.
// Source: Department of Enterprise, Tourism and Employment (DETE), thresholds from 1 March 2026.
// Works in the browser (window.IEPERMIT) and in Node (module.exports) for the page builder.
(function (root) {
  "use strict";
  var HOURS_WEEK = 39, WEEKS = 52;          // DETE thresholds assume a 39-hour week
  var EFFECTIVE = "1 March 2026";
  var INDEX_AVG = 0.049;                     // average yearly rise in CSO average weekly earnings since 2020 (illustration only)
  var LOWER_GAP_2027 = 0.925;                // roadmap: lower-paid thresholds move to ~92.5% of the GEP threshold in 2027

  // id, name, short name, page slug, minimum now, minimum before 1 March 2026, graduate rate (or null)
  var PERMITS = [
    { id: "gep", name: "General Employment Permit", short: "GEP", slug: "general-employment-permit", min: 36605, prev: 34000, grad: 34009 },
    { id: "gep_care", name: "Healthcare assistant, home carer or care worker (GEP)", short: "GEP – care roles", slug: "care-workers", min: 32691, prev: 30000, grad: null, lower: true },
    { id: "gep_agri", name: "Meat processing or horticulture operative (GEP)", short: "GEP – meat / horticulture", slug: "care-workers", min: 32691, prev: 30000, grad: null, lower: true },
    { id: "csep", name: "Critical Skills Employment Permit (relevant degree)", short: "CSEP", slug: "critical-skills-permit", min: 40904, prev: 38000, grad: 36848 },
    { id: "csep_high", name: "Critical Skills Employment Permit (no degree, other occupations)", short: "CSEP – no degree", slug: "critical-skills-permit", min: 68911, prev: 64000, grad: null },
    { id: "ict", name: "Intra-Company Transfer (senior management / key personnel)", short: "ICT", slug: "intra-company-transfer", min: 49523, prev: 46000, grad: null },
    { id: "ict_trainee", name: "Intra-Company Transfer (trainee)", short: "ICT trainee", slug: "intra-company-transfer", min: 36605, prev: 34000, grad: null },
    { id: "cfs", name: "Contract for Services Employment Permit", short: "Contract for Services", slug: "contract-for-services", min: 49523, prev: 46000, grad: null }
  ];
  function get(id) { for (var i = 0; i < PERMITS.length; i++) if (PERMITS[i].id === id) return PERMITS[i]; return PERMITS[0]; }
  function r2(x) { return Math.round(x * 100) / 100; }
  function hourly(annual, hours) { return r2(annual / ((hours || HOURS_WEEK) * WEEKS)); }

  // Minimum that applies to this person
  function minimum(id, graduate) { var p = get(id); return graduate && p.grad ? p.grad : p.min; }

  // Rough 2027 illustration: standard thresholds indexed by the average earnings rise; lower-paid roles move to 92.5% of the GEP.
  function estimate2027(id, graduate, rise) {
    var k = 1 + (rise == null ? INDEX_AVG : rise), p = get(id);
    if (p.lower) return Math.round(get("gep").min * k * LOWER_GAP_2027 / 10) * 10;
    return Math.round(minimum(id, graduate) * k / 10) * 10;
  }

  // o: { permit, graduate, salary (basic, per year), health (employer-paid health insurance per year), board (Contract for Services: board & accommodation per year), hours }
  function check(o) {
    var p = get(o.permit), grad = !!(o.graduate && p.grad);
    var min = minimum(p.id, grad);
    var counted = Math.max(0, o.salary || 0) + Math.max(0, o.health || 0) + (p.id === "cfs" ? Math.max(0, o.board || 0) : 0);
    var hours = o.hours || HOURS_WEEK;
    var e27 = estimate2027(p.id, grad);
    return {
      permit: p, graduate: grad, min: min, counted: counted, meets: counted >= min, gap: counted - min,
      gapPct: min ? (counted - min) / min : 0, hours: hours,
      yourHourly: hourly(counted, hours), minHourly39: hourly(min), minHourlyYourHours: hourly(min, hours),
      est2027: e27, meets2027: counted >= e27, gap2027: counted - e27,
      monthly: Math.round(min / 12), weekly: r2(min / WEEKS)
    };
  }

  // Which permit minimums a salary meets (for the by-salary pages)
  function qualifies(salary, graduate) {
    return PERMITS.map(function (p) {
      var m = minimum(p.id, graduate);
      return { permit: p, min: m, meets: salary >= m, gap: salary - m };
    });
  }

  var api = { PERMITS: PERMITS, HOURS_WEEK: HOURS_WEEK, WEEKS: WEEKS, EFFECTIVE: EFFECTIVE, INDEX_AVG: INDEX_AVG,
    get: get, minimum: minimum, hourly: hourly, estimate2027: estimate2027, check: check, qualifies: qualifies };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.IEPERMIT = api;
})(this);
