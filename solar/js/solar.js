// Solar panel payback engine for Ireland. Used by the calculator in the browser
// (window.IESOLAR) and by tools/build_solar.py (Node) so every page shows the same numbers.
// Generation: PVGIS 5.3 (SARAH-3), 1 kWp, 14% system losses, 35° tilt, south-facing, per county town.
// Grants: SEAI Solar PV scheme as published on seai.ie (checked November 2026).
(function (root) {
  "use strict";

  // kWh per kWp per year, and the monthly split (Jan–Dec), from PVGIS.
  var COUNTIES = {
    carlow: ["Carlow", 958, [36, 51, 84, 109, 122, 117, 114, 106, 86, 60, 42, 31]],
    cavan: ["Cavan", 889, [28, 45, 77, 105, 119, 111, 108, 100, 79, 58, 37, 23]],
    clare: ["Clare", 931, [33, 48, 82, 110, 120, 115, 109, 102, 82, 60, 41, 29]],
    cork: ["Cork", 972, [39, 51, 82, 110, 121, 119, 116, 108, 86, 61, 47, 32]],
    donegal: ["Donegal", 847, [24, 44, 75, 103, 117, 108, 104, 97, 73, 53, 32, 19]],
    dublin: ["Dublin", 982, [38, 54, 88, 110, 125, 117, 114, 104, 88, 65, 45, 34]],
    galway: ["Galway", 926, [32, 47, 81, 112, 124, 115, 109, 101, 79, 60, 39, 27]],
    kerry: ["Kerry", 909, [33, 48, 81, 110, 117, 111, 105, 100, 82, 58, 38, 27]],
    kildare: ["Kildare", 922, [32, 48, 80, 105, 121, 114, 110, 100, 82, 61, 40, 29]],
    kilkenny: ["Kilkenny", 956, [36, 51, 83, 108, 122, 116, 112, 107, 86, 61, 43, 31]],
    laois: ["Laois", 941, [35, 50, 82, 106, 120, 114, 112, 103, 85, 62, 42, 30]],
    leitrim: ["Leitrim", 880, [29, 44, 76, 103, 119, 110, 106, 99, 76, 57, 37, 23]],
    limerick: ["Limerick", 916, [34, 48, 81, 108, 116, 112, 106, 101, 81, 60, 41, 29]],
    longford: ["Longford", 909, [32, 47, 79, 106, 120, 111, 108, 101, 79, 60, 40, 26]],
    louth: ["Louth", 955, [34, 50, 84, 112, 125, 118, 112, 105, 84, 62, 42, 29]],
    mayo: ["Mayo", 887, [28, 44, 78, 107, 122, 113, 105, 99, 76, 57, 35, 23]],
    meath: ["Meath", 946, [33, 49, 82, 109, 124, 116, 112, 104, 84, 63, 42, 29]],
    monaghan: ["Monaghan", 895, [29, 46, 77, 106, 119, 112, 108, 100, 79, 58, 38, 24]],
    offaly: ["Offaly", 938, [35, 49, 82, 107, 122, 113, 110, 104, 83, 62, 42, 29]],
    roscommon: ["Roscommon", 929, [32, 49, 80, 108, 122, 114, 109, 103, 82, 61, 41, 27]],
    sligo: ["Sligo", 849, [26, 43, 74, 104, 118, 107, 101, 94, 73, 54, 33, 22]],
    tipperary: ["Tipperary", 913, [33, 48, 79, 103, 115, 111, 109, 104, 82, 58, 40, 30]],
    waterford: ["Waterford", 1047, [39, 54, 89, 117, 133, 131, 127, 117, 94, 66, 47, 33]],
    westmeath: ["Westmeath", 932, [34, 49, 81, 107, 121, 115, 110, 103, 82, 62, 42, 27]],
    wexford: ["Wexford", 1081, [38, 55, 91, 121, 140, 138, 133, 119, 98, 68, 45, 34]],
    wicklow: ["Wicklow", 1003, [36, 52, 87, 115, 132, 129, 119, 107, 91, 62, 41, 32]]
  };

  // Output compared with a south-facing roof at 35°, from PVGIS runs for the midlands.
  var FACING = {
    s: ["South", [0.936, 1, 0.991]],
    sw: ["South-east or south-west", [0.901, 0.935, 0.915]],
    ew: ["East or west (or split east/west)", [0.822, 0.788, 0.739]],
    nw: ["North-east or north-west", [0.740, 0.627, 0.546]],
    n: ["North", [0.712, 0.557, 0.444]]
  };
  var TILT = { shallow: ["Shallow (about 15°)", 0], standard: ["Standard pitched roof (30–40°)", 1], steep: ["Steep (about 50°)", 2], flat: ["Flat roof (panels laid flat)", -1] };
  var FLAT = 0.836;

  // How much of the solar power you use directly, at a system sized to your yearly use.
  var HOME = { out: ["Out most of the day", 0.30], mixed: ["Mixed – some days at home", 0.40], home: ["Home most days / work from home", 0.50] };

  var DEFAULTS = {
    unitRate: 0.33,        // € per kWh incl. 9% VAT – market average for a 24-hour urban plan, autumn 2026
    exportRate: 0.185,     // € per kWh – typical Clean Export Guarantee rate, November 2026
    standing: 280,         // € a year standing charge incl. VAT (used to turn a bill into kWh)
    priceRise: 1.5,        // % a year electricity prices rise (cautious)
    degradation: 0.5,      // % a year panels lose output
    inverterCost: 1000,    // € to replace the inverter in year 12
    years: 25,
    panelW: 440            // watts per panel (typical 2026 panel)
  };

  function grantFor(kWp, kWh, type) {
    if (type === "none") return { solar: 0, battery: 0, total: 0 };
    var k = Math.max(0, Math.min(kWp, 4));
    var solar = type === "welfare"
      ? 3350 * Math.min(k, 2) + 850 * Math.max(0, k - 2)
      : Math.min(1800, 700 * Math.min(k, 2) + 200 * Math.max(0, k - 2));
    if (type === "welfare") solar = Math.min(8400, solar);
    var battery = kWh >= 5 ? 600 : 0;
    return { solar: Math.round(solar), battery: battery, total: Math.round(solar) + battery };
  }

  // Typical installed price in 2026 (0% VAT on supply and fit for homes).
  function systemCost(kWp) { return Math.round((2400 + 1150 * kWp) / 50) * 50; }
  function batteryCost(kWh) { return kWh > 0 ? Math.round((1000 + 400 * kWh) / 50) * 50 : 0; }

  function factor(facing, tilt) {
    if (tilt === "flat") return FLAT;
    var f = FACING[facing] || FACING.s, t = TILT[tilt] || TILT.standard;
    return f[1][t[1]];
  }

  function usageFromBill(bill2m, rate, standing) {
    var yearly = bill2m * 6;
    return Math.max(1200, Math.round((yearly - standing) / rate));
  }

  function recommend(usage, yieldPerKwp) {
    var k = usage / yieldPerKwp;
    k = Math.round(k * 2) / 2;
    return Math.max(2, Math.min(6, k));
  }

  // Split one year's generation into: used directly, used later from the battery, exported.
  function split(gen, usage, occ, battKWh) {
    var r = gen / usage;
    var direct = gen * Math.min(0.9, occ / (0.4 + 0.6 * r));
    direct = Math.min(direct, usage * 0.55);
    var surplus = gen - direct, charged = 0;
    if (battKWh > 0) charged = Math.min(surplus * 0.85, battKWh * 0.9 * 230, (usage - direct) / 0.9);
    charged = Math.max(0, charged);
    var fromBatt = charged * 0.9;
    return { direct: direct, battery: fromBatt, exported: Math.max(0, surplus - charged) };
  }

  function amort(p, ratePct, years) {
    if (p <= 0 || !years) return 0;
    var i = ratePct / 100 / 12, n = years * 12;
    return (i ? p * i / (1 - Math.pow(1 + i, -n)) : p / n) * 12;
  }

  function calc(o) {
    var D = DEFAULTS, c = COUNTIES[o.county] || COUNTIES.dublin;
    var rate = o.unitRate > 0 ? o.unitRate : D.unitRate;
    var exportRate = o.exportRate >= 0 && o.exportRate !== null && o.exportRate !== undefined ? o.exportRate : D.exportRate;
    var usage = o.usage > 0 ? o.usage : usageFromBill(o.bill2m > 0 ? o.bill2m : 250, rate, D.standing);
    usage += o.extraKWh > 0 ? o.extraKWh : 0;
    var f = factor(o.facing || "s", o.tilt || "standard") * (1 - (o.shading || 0) / 100);
    var yieldK = c[1] * f;
    var kWp = o.kWp > 0 ? o.kWp : recommend(usage, yieldK);
    var battKWh = o.battKWh > 0 ? o.battKWh : 0;
    var occ = (HOME[o.home] || HOME.mixed)[1];
    var gen = yieldK * kWp;
    var cost = o.cost > 0 ? o.cost : systemCost(kWp);
    var bcost = battKWh ? (o.battCost > 0 ? o.battCost : batteryCost(battKWh)) : 0;
    var g = grantFor(kWp, battKWh, o.grant || "standard");
    var gross = cost + bcost;
    if (g.total > gross) { g.solar = Math.max(0, gross - g.battery); g.total = g.solar + g.battery; } // a grant can't be more than the bill
    var net = Math.max(0, gross - g.total);
    var rise = (o.priceRise === undefined || o.priceRise === null ? D.priceRise : o.priceRise) / 100;
    var deg = (o.degradation === undefined || o.degradation === null ? D.degradation : o.degradation) / 100;
    var inv = o.inverterCost === undefined || o.inverterCost === null ? D.inverterCost : o.inverterCost;
    var loanPay = o.loan ? amort(net, o.loanRate || 0, o.loanYears || 0) : 0;
    var cum = o.loan ? 0 : -net, series = [cum], payback = null, first = null, total = 0, repaid = 0;
    for (var y = 1; y <= D.years; y++) {
      var gy = gen * Math.pow(1 - deg, y - 1), s = split(gy, usage, occ, battKWh);
      var price = rate * Math.pow(1 + rise, y - 1);
      var saving = (s.direct + s.battery) * price + s.exported * exportRate;
      if (y === 12) saving -= inv;
      if (y === 1) first = { split: s, saving: saving, price: price };
      var pay = o.loan && y <= o.loanYears ? loanPay : 0;
      repaid += pay;
      var prev = cum;
      cum += saving - pay; total += saving;
      if (payback === null && !o.loan && cum >= 0 && prev < 0) payback = y - 1 + (-prev) / (cum - prev);
      series.push(cum);
    }
    if (!o.loan && net === 0) payback = 0;
    var s1 = first.split, used = s1.direct + s1.battery;
    var billBefore = usage * rate + D.standing;
    var billAfter = (usage - used) * rate + D.standing - s1.exported * exportRate;
    return {
      county: o.county, countyName: c[0], yieldPerKwp: Math.round(yieldK), kWp: kWp, panels: Math.ceil(kWp * 1000 / D.panelW),
      battKWh: battKWh, usage: Math.round(usage), gen: Math.round(gen), monthly: c[2].map(function (m) { return Math.round(m * f * kWp); }),
      direct: Math.round(s1.direct), fromBattery: Math.round(s1.battery), exported: Math.round(s1.exported),
      selfUse: Math.round(used / gen * 100), cover: Math.round(Math.min(1, used / usage) * 100),
      cost: cost, battCost: bcost, gross: gross, grant: g, net: net,
      saving1: Math.round(first.saving), importSaved: Math.round(used * rate), exportIncome: Math.round(s1.exported * exportRate),
      billBefore: Math.round(billBefore), billAfter: Math.round(Math.max(0, billAfter)),
      payback: payback === null ? null : Math.round(payback * 10) / 10,
      profit: Math.round(series[series.length - 1]), totalSavings: Math.round(total),
      roi: net > gross * 0.3 ? Math.round((total - net) / net * 100) : null,
      series: series.map(Math.round), loan: o.loan ? { yearly: Math.round(loanPay), monthly: Math.round(loanPay / 12), years: o.loanYears, rate: o.loanRate, total: Math.round(repaid) } : null,
      rate: rate, exportRate: exportRate, years: D.years, taxFree: s1.exported * exportRate <= 400
    };
  }

  var S = { COUNTIES: COUNTIES, FACING: FACING, TILT: TILT, HOME: HOME, DEFAULTS: DEFAULTS, grantFor: grantFor, systemCost: systemCost, batteryCost: batteryCost,
    factor: factor, usageFromBill: usageFromBill, recommend: recommend, calc: calc };
  if (typeof module !== "undefined" && module.exports) module.exports = S; else root.IESOLAR = S;
})(this);
