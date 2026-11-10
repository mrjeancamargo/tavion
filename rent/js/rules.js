/*
 * Irish rent control & notice period rules (Residential Tenancies Act 2004, as amended,
 * including the changes that apply from 1 March 2026).
 * Used by the calculators in the browser AND by tools/build_rent.py (through Node).
 *
 * Sources (checked November 2026):
 *  - RTB: Setting and reviewing private rents from 1 March 2026; Setting and Reviewing Rent – Landlord Guide (Feb 2026)
 *  - RTB: Rental law changes from 1 March 2026; Ending a Tenancy – Landlord Guide (Feb 2026); How a landlord / tenant can end a tenancy
 *  - Housing Agency: Rent Pressure Zones (areas designated before the all-Ireland designation of 20 June 2025)
 *  - CSO: Consumer Price Index (September 2026: CPI +4.1% in 12 months)
 */
(function (root) {
  "use strict";
  var DAY = 86400000;
  var NEW_RULES = "2026-03-01";          // new tenancy rules start
  var ALL_RPZ = "2025-06-20";            // whole country became a Rent Pressure Zone
  var JUNE_2022 = "2022-06-11";          // tenancies from this date: unlimited duration after 6 months
  var DEC_2016 = "2016-12-24";           // 6-year Part 4 cycles start for tenancies from this date
  var NEW_BUILD = "2025-06-10";          // construction commenced after this date: CPI only, no 2% cap
  var LATEST_CPI = { pct: 4.1, month: "September 2026" };  // update from cso.ie when you rebuild

  // Areas that were Rent Pressure Zones BEFORE 20 June 2025 (Housing Agency).
  // whole: true = the whole county / local authority. Otherwise only the listed Local Electoral Areas.
  var COUNTIES = {
    carlow: { name: "Carlow", lea: ["Carlow", "Tullow"] },
    cavan: { name: "Cavan", lea: [] },
    clare: { name: "Clare", lea: ["Ennis", "Shannon"] },
    cork: { name: "Cork", lea: ["Cork City", "Ballincollig–Carrigaline", "Bandon–Kinsale", "Cobh", "Fermoy", "Macroom", "Mallow", "Midleton"] },
    donegal: { name: "Donegal", lea: [] },
    dublin: { name: "Dublin", whole: true },
    galway: { name: "Galway", whole: true },
    kerry: { name: "Kerry", lea: ["Killarney"] },
    kildare: { name: "Kildare", whole: true },
    kilkenny: { name: "Kilkenny", whole: true },
    laois: { name: "Laois", lea: ["Portlaoise", "Graiguecullen–Portarlington"] },
    leitrim: { name: "Leitrim", lea: [] },
    limerick: { name: "Limerick", whole: true },
    longford: { name: "Longford", lea: [] },
    louth: { name: "Louth", whole: true },
    mayo: { name: "Mayo", lea: ["Castlebar", "Westport"] },
    meath: { name: "Meath", whole: true },
    monaghan: { name: "Monaghan", lea: [] },
    offaly: { name: "Offaly", lea: ["Tullamore"] },
    roscommon: { name: "Roscommon", lea: ["Athlone (Roscommon side, e.g. Monksland)"] },
    sligo: { name: "Sligo", lea: ["Sligo–Strandhill", "Sligo–Drumcliffe"] },
    tipperary: { name: "Tipperary", lea: [] },
    waterford: { name: "Waterford", whole: true },
    westmeath: { name: "Westmeath", whole: true },
    wexford: { name: "Wexford", lea: ["Gorey"] },
    wicklow: { name: "Wicklow", whole: true }
  };

  // ---------- dates (all UTC day numbers)
  function d(s) { if (!s) return null; if (typeof s === "number") return s; var p = String(s).split("-"); return Math.floor(Date.UTC(+p[0], +p[1] - 1, +p[2]) / DAY); }
  function iso(n) { return new Date(n * DAY).toISOString().slice(0, 10); }
  function addMonths(n, m) { var dt = new Date(n * DAY), y = dt.getUTCFullYear(), mo = dt.getUTCMonth() + m, day = dt.getUTCDate();
    var last = new Date(Date.UTC(y, mo + 1, 0)).getUTCDate(); return Math.floor(Date.UTC(y, mo, Math.min(day, last)) / DAY); }
  function addYears(n, y) { return addMonths(n, 12 * y); }
  function today() { var t = new Date(); return Math.floor(Date.UTC(t.getFullYear(), t.getMonth(), t.getDate()) / DAY); }
  function months(a, b) { // whole months from a to b
    var A = new Date(a * DAY), B = new Date(b * DAY);
    var m = (B.getUTCFullYear() - A.getUTCFullYear()) * 12 + B.getUTCMonth() - A.getUTCMonth();
    if (B.getUTCDate() < A.getUTCDate()) m--; return m; }
  function r2(x) { return Math.round(x * 100) / 100; }

  // Was the area already an RPZ before 20 June 2025?
  function rpzBefore(county, inLea) {
    var c = COUNTIES[county]; if (!c) return null;
    if (c.whole) return true;
    if (!c.lea.length) return false;
    return inLea === true ? true : inLea === false ? false : null; // null = unknown
  }

  /*
   * RENT INCREASE
   * inp = { rent, lastSet: "YYYY-MM-DD", tenancyStart, county, inLea (true/false/null),
   *         type: "standard" | "newbuild" | "ssa" | "ahb", effective: "YYYY-MM-DD" (date new rent starts, optional),
   *         noticeDate: "YYYY-MM-DD" (date notice served, optional, default today),
   *         cpi: number|null (CPI % change from last set to new rent date; null = assume above 2% a year),
   *         proposed: number (new rent asked for, optional) }
   */
  function rentReview(inp) {
    var out = { ok: true, notes: [], warnings: [] };
    var rent = +inp.rent || 0, last = d(inp.lastSet), start = d(inp.tenancyStart) || last, notice = d(inp.noticeDate) || today();
    if (inp.type === "ahb") {
      out.ok = false; out.excluded = true;
      out.notes.push("Rent control rules don't apply to Approved Housing Body (AHB) or cost rental tenancies. Your rent is set under the AHB or cost rental scheme's own rules.");
      return out;
    }
    if (!rent || last === null) { out.ok = false; out.warnings.push("Enter your current rent and the date it was last set or increased."); return out; }

    var before = rpzBefore(inp.county, inp.inLea);
    var gap = 12, rule24 = false;
    // Newly designated on 20 June 2025: first review 24 months after the rent was last set.
    if (before === false && last < d(ALL_RPZ)) { gap = 24; rule24 = true; }
    if (before === null && last < d(ALL_RPZ)) out.warnings.push("Not sure if your area was a Rent Pressure Zone before 20 June 2025? If it wasn't, the first review must wait 24 months instead of 12. Check the RTB's RPZ map.");
    var earliestByGap = addMonths(last, gap);
    var earliestByNotice = notice + 90;
    var earliest = Math.max(earliestByGap, earliestByNotice);
    var eff = d(inp.effective) || earliest;
    if (eff < earliestByGap) out.warnings.push("The new rent can't take effect before " + iso(earliestByGap) + " – rent can only be reviewed once every " + gap + " months.");
    if (eff < earliestByNotice) out.warnings.push("The tenant must get at least 90 days' notice: a notice served on " + iso(notice) + " can't increase the rent before " + iso(earliestByNotice) + ".");

    var days = Math.max(0, eff - last), years = days / 365;
    var capPct2 = 2 * years;                       // 2% a year, pro rata
    var cpi = (inp.cpi === null || inp.cpi === undefined || inp.cpi === "") ? null : +inp.cpi;
    var pctAllowed, basis;
    if (inp.type === "newbuild") {
      var c = cpi === null ? LATEST_CPI.pct * years : cpi;
      pctAllowed = Math.max(0, c); basis = cpi === null ? "cpi-estimate" : "cpi";
      out.notes.push("New homes where construction started after 10 June 2025 can increase in line with inflation (CPI) – there is no 2% cap.");
    } else if (cpi === null) {
      pctAllowed = capPct2; basis = "2pct";
      out.notes.push("CPI inflation is currently above 2% (" + LATEST_CPI.pct + "% in the 12 months to " + LATEST_CPI.month + "), so the 2% a year cap applies.");
    } else {
      pctAllowed = Math.max(0, Math.min(capPct2, cpi)); basis = cpi < capPct2 ? "cpi" : "2pct";
    }
    out.maxPct = r2(pctAllowed);
    out.maxIncrease = r2(rent * pctAllowed / 100);
    out.maxRent = r2(rent + out.maxIncrease);
    out.basis = basis; out.years = r2(years); out.days = days;
    out.earliest = iso(earliest); out.earliestByGap = iso(earliestByGap); out.earliestByNotice = iso(earliestByNotice);
    out.effective = iso(eff); out.gapMonths = gap; out.rule24 = rule24; out.rpzBefore = before;
    out.newRules = start >= d(NEW_RULES);
    if (inp.proposed) {
      var p = +inp.proposed;
      out.proposed = p; out.proposedPct = r2((p - rent) / rent * 100);
      out.proposedOk = p <= out.maxRent + 0.005 && eff >= earliestByGap && eff >= earliestByNotice;
      out.overBy = r2(Math.max(0, p - out.maxRent));
    }
    if (inp.type === "ssa") out.notes.push("Student Specific Accommodation follows the same 2%/CPI cap. A reset to market rent is only allowed once every 3 years, from 1 March 2029.");
    if (out.newRules) out.notes.push("Your tenancy started on or after 1 March 2026: the rent can be reset to market rent at the end of each 6-year tenancy cycle (small landlords) – but not in between.");
    else out.notes.push("Your tenancy started before 1 March 2026, so the rent can never be reset to market rent while it continues – only the annual capped increase.");
    return out;
  }

  /*
   * RENT AT THE START OF A NEW TENANCY (from 1 March 2026)
   * prevEnd: "tenant-left" | "tenant-breach" | "not-suitable" | "no-fault" | "first-letting" | "vacant-2y" | "renovated" | "unknown"
   */
  function newTenancyRent(prevEnd) {
    var reset = { "tenant-left": true, "tenant-breach": true, "not-suitable": true, "first-letting": true, "vacant-2y": true, "renovated": true, "no-fault": false };
    return { marketReset: reset[prevEnd] === undefined ? null : reset[prevEnd] };
  }

  // ---------- NOTICE PERIODS
  var LANDLORD_TABLE = [[6, 90, "less than 6 months"], [12, 152, "6 months to less than 1 year"], [84, 180, "1 year to less than 7 years"], [96, 196, "7 years to less than 8 years"], [Infinity, 224, "8 years or more"]];
  var TENANT_TABLE = [[6, 28, "less than 6 months"], [12, 35, "6 months to less than 1 year"], [24, 42, "1 year to less than 2 years"], [48, 56, "2 to less than 4 years"], [96, 84, "4 to less than 8 years"], [Infinity, 112, "8 years or more"]];
  function look(table, m) { for (var i = 0; i < table.length; i++) if (m < table[i][0]) return { days: table[i][1], band: table[i][2] }; }

  var REASONS = {
    // landlord
    "first6": { who: "landlord", label: "Ending the tenancy in the first 6 months (any reason)", doc: "Statement (included in the RTB template)" },
    "arrears": { who: "landlord", label: "Rent arrears", short: 28, doc: "A rent arrears warning notice (tenant + RTB, same day, at least 28 days to pay) must come first", breach: true },
    "breach": { who: "landlord", label: "Other breach of tenant obligations", short: 28, doc: "A warning notice with a reasonable time to fix the breach must come first", breach: true },
    "asb": { who: "landlord", label: "Serious anti-social behaviour or damage threatening the property", short: 7, doc: "No warning notice needed", breach: true },
    "unsuitable": { who: "landlord", label: "Property no longer suits the tenant's needs (e.g. number of bedrooms)", doc: "Statement" },
    "sale": { who: "landlord", label: "Landlord is selling the property", doc: "Statutory declaration" },
    "family": { who: "landlord", label: "Landlord or a family member needs to live there", doc: "Statutory declaration" },
    "refurb": { who: "landlord", label: "Substantial refurbishment or renovation", doc: "Statutory declaration + statement (and planning permission if needed)" },
    "change": { who: "landlord", label: "Changing the use of the property", doc: "Statutory declaration + statement" },
    "endterm": { who: "landlord", label: "End of a Part 4 term – no reason needed (tenancies before 11 June 2022 only)", doc: "None beyond a valid notice" },
    // tenant
    "t-none": { who: "tenant", label: "Tenant leaving – no reason needed" },
    "t-breach": { who: "tenant", label: "Landlord broke their obligations and didn't fix it", short: 28 },
    "t-danger": { who: "tenant", label: "Danger to life, serious injury or the structure of the property", short: 7 }
  };

  /*
   * inp = { who: "landlord"|"tenant", start, served (default today), reason, landlordSize: "small"|"large",
   *         hardship: bool (small landlord sale during cycle), familyClose: bool (spouse/partner, parent, child),
   *         endDate (termination date written on the notice, optional), copiedRtb: bool|null, ssa: bool }
   */
  function notice(inp) {
    var o = { allowed: true, why: [], todo: [], warnings: [] };
    var start = d(inp.start), served = d(inp.served) || today();
    if (start === null) { o.allowed = false; o.warnings.push("Enter the date the tenancy started."); return o; }
    var R = REASONS[inp.reason] || REASONS[inp.who === "tenant" ? "t-none" : "sale"];
    var m = months(start, served);
    o.monthsAtService = m; o.reasonLabel = R.label;
    o.regime = start >= d(NEW_RULES) ? "new" : start >= d(JUNE_2022) ? "2022" : start >= d(DEC_2016) ? "2016" : "old";
    o.under6 = m < 6;

    // cycle (6-year Tenancy of Minimum Duration / Part 4 term)
    if (o.regime === "new") { // rolling 6-year Tenancies of Minimum Duration
      var n = 1, ce = addYears(start, 6);
      while (ce <= served) { n++; ce = addYears(start, 6 * n); }
      o.cycleEnd = iso(ce); o.cycleNo = n;
    } else if (o.regime === "2016") {
      // One 6-year Part 4 term; a Further Part 4 term only if the first one ended before 11 June 2022.
      // After the last term ends, the tenancy has unlimited duration.
      var te = addYears(start, 6);
      if (te < d(JUNE_2022)) te = addYears(start, 12);
      o.cycleEnd = iso(te); o.termOver = te <= served;
    }

    var days;
    if (inp.who === "tenant") {
      var t = look(TENANT_TABLE, m); days = t.days; o.band = t.band;
      if (R.short) { days = R.short; o.band = "shorter notice for this reason"; }
      if (inp.ssa && !R.short) { days = 28; o.band = "student specific accommodation"; }
      if (inp.reason === "t-breach") o.todo.push("First write to your landlord about the problem and give them a reasonable time to fix it (often 14 days).");
      o.todo.push("Your notice must be in writing (letter or email), signed by you, show the date it's served and the date the tenancy ends.");
      if (R.short) o.todo.push("State the reason in the notice.");
      o.todo.push("Tell the landlord they have " + (R.short ? "28" : "90") + " days from receiving it to refer a dispute to the RTB if they think it's invalid.");
    } else {
      var l = look(LANDLORD_TABLE, m); days = l.days; o.band = l.band;
      if (R.short) { days = R.short; o.band = "shorter notice for this reason"; }
      var reason = inp.reason, large = inp.landlordSize === "large";
      // which reasons are allowed
      if (reason === "first6") {
        if (!o.under6) { o.allowed = false; o.why.push("The tenancy is " + m + " months old. After 6 months the landlord needs one of the legal reasons."); }
      } else if (R.breach || reason === "unsuitable") {
        // always allowed
      } else if (o.under6) {
        o.why.push("In the first 6 months a landlord can end a tenancy for any reason – this one is fine, but the notice must state the reason.");
      } else if (o.regime === "new") {
        if (large) { o.allowed = false; o.why.push("For tenancies that started on or after 1 March 2026, a landlord with 4 or more tenancies (or a company) can only end the tenancy for a breach by the tenant or because the property no longer suits the tenant's needs. Selling, family use, refurbishment and change of use are not allowed – a sale must be with the tenant in place."); }
        else {
          var atEnd = d(inp.endDate) ? d(inp.endDate) >= d(o.cycleEnd) : false;
          if (reason === "sale") {
            if (inp.hardship) o.why.push("A small landlord (1–3 tenancies) can sell during the 6-year cycle only to avoid undue financial or other hardship (e.g. to buy a home to live in, repay a debt or pay at least 15% of the asking price within 9 months, or under a personal insolvency arrangement).");
            else if (atEnd) o.why.push("Selling is allowed at the end of the 6-year tenancy cycle (" + o.cycleEnd + ").");
            else { o.allowed = false; o.endAt = o.cycleEnd; o.why.push("During the 6-year cycle a small landlord can only sell to avoid undue hardship. Otherwise the termination date must be on or after the end of the cycle: " + o.cycleEnd + "."); }
          } else if (reason === "family") {
            if (inp.familyClose || atEnd) o.why.push(atEnd ? "At the end of the cycle the landlord or a wider family member (e.g. grandparent, grandchild, sibling) can move in." : "During the cycle only the landlord, their spouse or civil partner, parent or child (including step-, foster and adopted) can move in.");
            else { o.allowed = false; o.endAt = o.cycleEnd; o.why.push("During the 6-year cycle only a close family member (spouse/civil partner, parent or child) can move in. Wider family can only from the end of the cycle: " + o.cycleEnd + "."); }
          } else if (reason === "refurb" || reason === "change") {
            if (atEnd) o.why.push("Allowed at the end of the 6-year tenancy cycle.");
            else { o.allowed = false; o.endAt = o.cycleEnd; o.why.push("Refurbishment and change of use are only allowed at the end of the 6-year cycle – the termination date must be on or after " + o.cycleEnd + "."); }
          } else if (reason === "endterm") { o.allowed = false; o.why.push("'No reason' terminations at the end of a term only apply to tenancies that started before 11 June 2022."); }
          o.todo.push("Small landlords must include a statement confirming they have 1–3 tenancies, sent to the tenant and the RTB on the same day.");
        }
      } else { // before 1 March 2026
        if (reason === "endterm") {
          if (o.regime === "2022") { o.allowed = false; o.why.push("Tenancies that started on or after 11 June 2022 are of unlimited duration – there's no end of term."); }
          else if (o.regime === "2016" && o.termOver) { o.allowed = false; o.why.push("The tenancy's Part 4 term ended on " + o.cycleEnd + " and it is now of unlimited duration, so the landlord needs one of the 6 legal reasons."); }
          else if (o.regime === "2016") {
            var endOk = d(inp.endDate) && d(inp.endDate) >= d(o.cycleEnd);
            o.endAt = o.cycleEnd;
            o.why.push("For tenancies that started before 11 June 2022 the landlord can end the tenancy for any reason at the end of the current Part 4 term (" + o.cycleEnd + "). The notice must be served before the term ends." + (d(inp.endDate) && !endOk ? " Your termination date is before the end of the term." : ""));
            if (d(inp.endDate) && !endOk) o.allowed = false;
          } else o.why.push("Tenancies from before 24 December 2016 had 4-year Part 4 terms and later 'Further Part 4' terms – check the exact term dates with the RTB.");
        } else if (reason === "family") {
          o.why.push("Allowed for tenancies that started before 1 March 2026, whatever the landlord's size. Only private landlords (not companies) can use this reason.");
        } else if (reason === "sale") {
          o.why.push("Allowed for tenancies that started before 1 March 2026 – the landlord must intend to enter into a contract to sell within 9 months of the termination date. Selling 10 or more homes in one development has extra restrictions.");
        } else {
          o.why.push("This reason is allowed for tenancies that started before 1 March 2026.");
        }
      }
      if (R.doc) o.todo.push("Required with the notice: " + R.doc + ".");
      o.todo.push("The notice must be in writing, signed by the landlord or agent, show the date it's served, the reason and the termination date.");
      o.todo.push("It must say the tenant has " + (R.breach ? "28" : "90") + " days from receiving it to refer a dispute to the RTB.");
      o.todo.push("From 1 March 2026 the landlord must send the notice to the tenant and the RTB on the same day – otherwise it's invalid. Use the RTB template for the reason.");
      if (reason === "arrears") o.todo.push("The arrears warning notice must go to the tenant and the RTB on the same day, giving at least 28 days to pay. Only if the arrears aren't paid can the 28-day Notice of Termination be served.");
      if (["sale", "family", "refurb", "change"].indexOf(reason) >= 0) o.todo.push("If the reason doesn't happen (e.g. no sale, the family member doesn't move in), the landlord may have to offer the tenancy back. Tenants can refer this to the RTB.");
    }
    o.days = days;
    var earliest = served + days;
    if (o.endAt && d(o.endAt) > earliest) earliest = d(o.endAt);
    o.earliestEnd = iso(earliest); o.served = iso(served);
    if (inp.endDate) {
      var e = d(inp.endDate);
      o.endDate = iso(e);
      o.endDateOk = e >= earliest;
      if (!o.endDateOk) o.warnings.push("The termination date on the notice (" + iso(e) + ") is too early. It must be on or after " + iso(earliest) + ". A notice with the wrong date may be invalid.");
    }
    if (inp.who === "landlord" && inp.copiedRtb === false) { o.warnings.push("The notice wasn't sent to the RTB. From 1 March 2026 a landlord's Notice of Termination that isn't sent to the RTB on the same day is invalid."); }
    return o;
  }

  var API = { COUNTIES: COUNTIES, LATEST_CPI: LATEST_CPI, REASONS: REASONS, LANDLORD_TABLE: LANDLORD_TABLE, TENANT_TABLE: TENANT_TABLE,
              rentReview: rentReview, notice: notice, newTenancyRent: newTenancyRent, rpzBefore: rpzBefore, iso: iso, d: d, today: today,
              DATES: { NEW_RULES: NEW_RULES, ALL_RPZ: ALL_RPZ, JUNE_2022: JUNE_2022, NEW_BUILD: NEW_BUILD } };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IERENT = API;
})(this);
