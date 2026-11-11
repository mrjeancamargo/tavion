/*
 * Irish stamp duty, buying costs and Local Property Tax (LPT) engine.
 * Used by the calculators in the browser AND by tools/build_stamp.py (through Node).
 *
 * Sources (checked November 2026):
 *  - Revenue – Stamp duty on residential property: 1% up to €1m, 2% €1m–€1.5m, 6% above €1.5m (from 2 October 2024);
 *    new homes: charged on the price excluding VAT (13.5%); 10+ homes bought within 12 months: 15%; non-residential 7.5%
 *  - Revenue – LPT valuation bands and rates 2026–2030 (valuation date 1 November 2025) and Local Adjustment Factors 2026 / 2027
 */
(function (root) {
  "use strict";
  var VAT = 0.135;
  // [upper limit of band, basic annual LPT]
  var LPT_BANDS = [[240000, 95], [315000, 235], [420000, 333], [525000, 428], [630000, 523], [735000, 618], [840000, 713], [945000, 808],
    [1050000, 903], [1155000, 998], [1260000, 1094], [1365000, 1272], [1470000, 1535], [1575000, 1797], [1680000, 2060], [1785000, 2322],
    [1890000, 2585], [1995000, 2847], [2100000, 3110]];
  // Local Adjustment Factors (%), by local authority: [2026, 2027]
  var COUNCILS = {
    "carlow": ["Carlow County Council", "carlow", 15, 15], "cavan": ["Cavan County Council", "cavan", 15, 25], "clare": ["Clare County Council", "clare", 15, 15],
    "cork-city": ["Cork City Council", "cork", 12, 15], "cork-county": ["Cork County Council", "cork", 15, 15], "donegal": ["Donegal County Council", "donegal", 15, 15],
    "dublin-city": ["Dublin City Council", "dublin", 0, 0], "dun-laoghaire-rathdown": ["Dún Laoghaire-Rathdown County Council", "dublin", -15, -15],
    "fingal": ["Fingal County Council", "dublin", -5, -5], "south-dublin": ["South Dublin County Council", "dublin", -7.5, -7.5],
    "galway-city": ["Galway City Council", "galway", 15, 15], "galway-county": ["Galway County Council", "galway", 15, 15], "kerry": ["Kerry County Council", "kerry", 10, 10],
    "kildare": ["Kildare County Council", "kildare", 10, 10], "kilkenny": ["Kilkenny County Council", "kilkenny", 15, 15], "laois": ["Laois County Council", "laois", 15, 20],
    "leitrim": ["Leitrim County Council", "leitrim", 15, 25], "limerick": ["Limerick City and County Council", "limerick", 15, 15], "longford": ["Longford County Council", "longford", 15, 15],
    "louth": ["Louth County Council", "louth", 0, 0], "mayo": ["Mayo County Council", "mayo", 10, 10], "meath": ["Meath County Council", "meath", 0, 0],
    "monaghan": ["Monaghan County Council", "monaghan", 15, 15], "offaly": ["Offaly County Council", "offaly", 15, 15], "roscommon": ["Roscommon County Council", "roscommon", 15, 15],
    "sligo": ["Sligo County Council", "sligo", 15, 25], "tipperary": ["Tipperary County Council", "tipperary", 15, 15], "waterford": ["Waterford City and County Council", "waterford", 15, 15],
    "westmeath": ["Westmeath County Council", "westmeath", 15, 15], "wexford": ["Wexford County Council", "wexford", 15, 15], "wicklow": ["Wicklow County Council", "wicklow", 6, 6]
  };
  // Typical buying fees (estimates incl. VAT) – same figures as the mortgage app.
  var FEES = { solicitor: 3075, landRegistry: 975, mortgageReg: 175, searches: 300, valuation: 185, survey: 500, removals: 800, insurance: 450 };

  function r0(x) { return Math.round(x); }
  function r2(x) { return Math.round(x * 100) / 100; }

  /* Stamp duty on a residential purchase.
   * opts = { newBuild: price includes 13.5% VAT, bulk: 10+ homes in 12 months, nonResidential } */
  function stampDuty(price, opts) {
    opts = opts || {};
    var base = opts.newBuild ? price / (1 + VAT) : price, rows = [];
    if (opts.nonResidential) { rows.push({ rate: 0.075, on: base, tax: base * 0.075 }); }
    else if (opts.bulk) { rows.push({ rate: 0.15, on: base, tax: base * 0.15 }); }
    else {
      var a = Math.min(base, 1000000), b = Math.max(0, Math.min(base, 1500000) - 1000000), c = Math.max(0, base - 1500000);
      rows.push({ rate: 0.01, on: a, tax: a * 0.01 });
      if (b) rows.push({ rate: 0.02, on: b, tax: b * 0.02 });
      if (c) rows.push({ rate: 0.06, on: c, tax: c * 0.06 });
    }
    var total = rows.reduce(function (s, x) { return s + x.tax; }, 0);
    return { base: r0(base), vat: r0(price - base), rows: rows.map(function (x) { return { rate: x.rate, on: r0(x.on), tax: r0(x.tax) }; }),
             total: r0(total), effective: price ? r2(total / price * 100) : 0 };
  }

  /* Local Property Tax for a value and council. year: 2026 | 2027 */
  function lpt(value, council, year) {
    var c = COUNCILS[council], laf = c ? c[year === 2026 ? 2 : 3] : 0, band = null, basic;
    if (value > 2100000) {
      basic = Math.min(value, 1260000) * 0.000906 + Math.max(0, Math.min(value, 2100000) - 1260000) * 0.0025 + Math.max(0, value - 2100000) * 0.003;
    } else {
      for (var i = 0; i < LPT_BANDS.length; i++) if (value <= LPT_BANDS[i][0]) { band = i + 1; basic = LPT_BANDS[i][1]; break; }
    }
    var annual = basic * (1 + laf / 100);
    return { band: band, basic: r0(basic), laf: laf, annual: r0(annual), monthly: r2(annual / 12), council: c ? c[0] : "", year: year,
             lower: band ? (band === 1 ? 1 : LPT_BANDS[band - 2][0] + 1) : 2100001, upper: band ? LPT_BANDS[band - 1][0] : null };
  }

  /* Total cost of buying.
   * opts = { newBuild, mortgage (true), survey (true unless new build), solicitor (override), council, extras (removals, insurance), bulk } */
  function buyingCosts(price, opts) {
    opts = opts || {};
    var mortgage = opts.mortgage !== false;
    var sd = stampDuty(price, opts);
    var items = [
      ["Stamp duty", sd.total, "stamp"],
      ["Solicitor (incl. VAT and outlays)", opts.solicitor != null && opts.solicitor !== "" ? +opts.solicitor : FEES.solicitor, "legal"],
      ["Land Registry – registering the title", FEES.landRegistry, "legal"],
      ["Searches", FEES.searches, "legal"]
    ];
    if (mortgage) { items.push(["Land Registry – registering the mortgage", FEES.mortgageReg, "bank"]); items.push(["Bank valuation", FEES.valuation, "bank"]); }
    var survey = opts.survey == null ? !opts.newBuild : !!opts.survey;
    if (survey) items.push(["Structural survey", FEES.survey, "survey"]);
    if (opts.extras) { items.push(["Removals (estimate)", FEES.removals, "extra"]); items.push(["Home insurance – first year (estimate)", FEES.insurance, "extra"]); }
    var total = items.reduce(function (s, x) { return s + x[1]; }, 0);
    var out = { price: r0(price), stamp: sd, items: items.map(function (x) { return { name: x[0], amount: r0(x[1]), group: x[2] }; }), total: r0(total),
                pctOfPrice: price ? r2(total / price * 100) : 0, deposit10: r0(price * 0.1) };
    out.cashWithDeposit = out.deposit10 + out.total;
    if (opts.council) { out.lpt = lpt(price, opts.council, opts.year || 2027); }
    return out;
  }

  var API = { LPT_BANDS: LPT_BANDS, COUNCILS: COUNCILS, FEES: FEES, VAT: VAT, stampDuty: stampDuty, lpt: lpt, buyingCosts: buyingCosts };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IEPROP = API;
})(this);
