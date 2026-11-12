/*
 * IEREF – "Am I owed a tax refund?" engine for Irish PAYE workers.
 * Figures from Revenue "Tax rates, bands and reliefs" charts (2022–2026) and Budget 2027 (6 October 2026).
 *   https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx
 * Used by the checker in the browser and by tools/build_taxrefund.py (through Node), so both always agree.
 * Estimates are "up to" amounts: a credit can only give back Income Tax you actually paid that year.
 */
(function (root) {
  var YEARS = [2022, 2023, 2024, 2025, 2026];          // years you can still claim (four-year rule) as at late 2026
  var DEADLINE = { year: 2022, date: "2026-12-31" };     // claims for 2022 must be made by 31 December 2026
  var NEXT = 2027;
  var CREDITS = {
    personal:      { 2022: 1700, 2023: 1775, 2024: 1875, 2025: 2000, 2026: 2000, 2027: 2125 },
    employee:      { 2022: 1700, 2023: 1775, 2024: 1875, 2025: 2000, 2026: 2000, 2027: 2125 },
    rent:          { 2022: 500,  2023: 500,  2024: 1000, 2025: 1000, 2026: 1000, 2027: 1150 },  // single; jointly assessed couple x2
    homeCarer:     { 2022: 1600, 2023: 1700, 2024: 1800, 2025: 1950, 2026: 1950, 2027: 2050 },
    spccc:         { 2022: 1650, 2023: 1650, 2024: 1750, 2025: 1900, 2026: 1900 },
    incapChild:    { 2022: 3300, 2023: 3300, 2024: 3500, 2025: 3800, 2026: 3800 },
    dependent:     { 2022: 245,  2023: 245,  2024: 245,  2025: 305,  2026: 305 },
    blind:         { 2022: 1650, 2023: 1650, 2024: 1650, 2025: 1950, 2026: 1950 },
    age:           { 2022: 245,  2023: 245,  2024: 245,  2025: 245,  2026: 245 },          // single; couple 490
    mortgageMax:   { 2022: 0,    2023: 1250, 2024: 1250, 2025: 1250, 2026: 625 },
    landlordMax:   { 2022: 0,    2023: 0,    2024: 600,  2025: 800,  2026: 1000, 2027: 1000 }
  };
  var BAND = { 2022: 36800, 2023: 40000, 2024: 42000, 2025: 44000, 2026: 44000, 2027: 46500 };  // single person, 20% band
  var RULES = {
    standardRate: 0.20, higherRate: 0.40,
    homeCarerIncomeLimit: 7200,          // full credit below this; reduced by half the excess
    remoteWorkingShare: 0.30, remoteAllowancePerDay: 3.20,
    tuitionDisregardFT: 3000, tuitionDisregardPT: 1500, tuitionMaxPerCourse: 7000,
    rentARoom: { 2022: 14000, 2023: 14000, 2024: 14000, 2025: 14000, 2026: 14000, 2027: 16000 },
    microGen: { 2022: 200, 2023: 200, 2024: 400, 2025: 400, 2026: 400, 2027: 600 },
    guideDog: 825, smallBenefit: 1500, smallBenefitCount: 5,
    cycleToWork: { bike: 1250, ebike: 1500, cargo: 3000 },
    over65Exempt: { single: 18000, couple: 36000 },
    pensionAgeLimits: [[30, 0.15], [40, 0.20], [50, 0.25], [55, 0.30], [60, 0.35], [999, 0.40]], pensionEarningsCap: 115000
  };

  function r0(n) { return Math.round(n); }
  function marginal(o) { return o.higherRate ? RULES.higherRate : RULES.standardRate; }
  function yearsFrom(o) { return (o.years && o.years.length ? o.years : YEARS).filter(function (y) { return YEARS.indexOf(y) >= 0; }); }

  // Rent Tax Credit for one year: lower of 20% of rent paid and the year's cap (doubled for jointly assessed couples).
  function rentCredit(year, rentPerYear, couple) {
    var cap = (CREDITS.rent[year] || 0) * (couple ? 2 : 1);
    return r0(Math.min(rentPerYear * RULES.standardRate, cap));
  }
  // Remote Working Relief: ((bills × days ÷ days in year) − employer allowance) × 30%, relieved at your marginal rate.
  function remoteWorking(year, bills, days, allowance, rate) {
    var diy = (year % 4 === 0) ? 366 : 365;
    var allowable = Math.max(0, (bills * days / diy - (allowance || 0)) * RULES.remoteWorkingShare);
    return { allowable: r0(allowable), refund: r0(allowable * (rate || RULES.standardRate)) };
  }
  function tuition(fees, partTime, courses) {
    var capped = Math.min(fees, RULES.tuitionMaxPerCourse * Math.max(1, courses || 1));
    return r0(Math.max(0, capped - (partTime ? RULES.tuitionDisregardPT : RULES.tuitionDisregardFT)) * RULES.standardRate);
  }
  function homeCarer(year, carerIncome) {
    var full = CREDITS.homeCarer[year] || 0, over = Math.max(0, (carerIncome || 0) - RULES.homeCarerIncomeLimit);
    return r0(Math.max(0, full - over / 2));
  }
  function mortgageInterest(year, increase) {
    if (year === 2026) return r0(Math.min(increase * 0.5, 3125) * RULES.standardRate);
    return r0(Math.min(increase, 6250) * RULES.standardRate) * (CREDITS.mortgageMax[year] ? 1 : 0);
  }
  function flatRate(amount, rate, years) { return r0(amount * rate * years); }

  /*
   * check(o) – o: answers from the checker. Every amount is per year unless noted.
   * Returns { items: [{key, name, perYear, years, total, note, page}], total, deadlineDays }
   */
  function check(o) {
    o = o || {}; var rate = marginal(o), ys = yearsFrom(o), items = [];
    function add(key, name, perYearFn, note, page, yrs) {
      var list = (yrs || ys).map(function (y) { return { year: y, amount: perYearFn(y) }; }).filter(function (x) { return x.amount > 0; });
      var total = list.reduce(function (s, x) { return s + x.amount; }, 0);
      if (total > 0) items.push({ key: key, name: name, byYear: list, total: total, note: note, page: page });
    }
    if (o.rentMonthly > 0 && !o.hap) add("rent", "Rent Tax Credit", function (y) { return rentCredit(y, o.rentMonthly * 12, o.couple); },
      "20% of rent you paid, up to €" + (CREDITS.rent[2026] * (o.couple ? 2 : 1)).toLocaleString("en-IE") + " a year (2024–2026).", "rent-tax-credit.html");
    if (o.studentRentMonthly > 0) add("rentChild", "Rent Tax Credit – your child's college rent", function (y) { return rentCredit(y, o.studentRentMonthly * (o.studentMonths || 9), o.couple); },
      "Parents paying rent for a student child (under 23 when the course started) can claim.", "rent-tax-credit-students.html");
    var health = (o.medical || 0) + (o.dental || 0) + (o.glutenFree || 0) + (o.prescriptions || 0) + (o.therapy || 0);
    if (health > 0) add("health", "Health expenses (doctor, consultant, medicines, non-routine dental, physio, gluten-free food…)", function () { return r0(health * RULES.standardRate); },
      "20% back on what you paid and weren't refunded by insurance.", "medical-expenses.html");
    if (o.nursingHome > 0) add("nursing", "Nursing home fees", function () { return r0(o.nursingHome * rate); }, "Relief at your highest rate of tax.", "nursing-home-fees.html");
    if (o.wfhDays > 0 && o.wfhBills > 0) add("wfh", "Remote Working Relief", function (y) { return remoteWorking(y, o.wfhBills, o.wfhDays, (o.wfhAllowance || 0) * o.wfhDays, rate).refund; },
      "30% of electricity, heating and broadband for the days you worked from home.", "remote-working-relief.html");
    if (o.flatRate > 0) add("fre", "Flat-rate expenses for your job", function () { return r0(o.flatRate * rate); }, "A fixed allowance for your job's tools, uniform or fees.", "flat-rate-expenses.html");
    if (o.tuitionFees > 0) add("tuition", "Third-level tuition fees", function () { return tuition(o.tuitionFees, o.tuitionPT, o.tuitionCourses); }, "20% of fees above €3,000 (€1,500 part-time).", "tuition-fees.html");
    if (o.homeCarer && o.couple) add("homecarer", "Home Carer Tax Credit", function (y) { return homeCarer(y, o.carerIncome); }, "For a jointly assessed couple where one cares for a child, someone 65+ or someone incapacitated.", "home-carer-tax-credit.html");
    if (o.singleParent && !o.couple) add("spccc", "Single Person Child Carer Credit", function (y) { return CREDITS.spccc[y] || 0; }, "Only if you weren't already getting it.", "single-person-child-carer-credit.html");
    if (o.incapChild) add("incap", "Incapacitated Child Tax Credit", function (y) { return CREDITS.incapChild[y] || 0; }, "Per child with a permanent disability.", "incapacitated-child-tax-credit.html");
    if (o.dependent) add("dependent", "Dependent Relative Tax Credit", function (y) { return CREDITS.dependent[y] || 0; }, "For supporting an elderly or incapacitated relative (income limits apply).", "dependent-relative-tax-credit.html");
    if (o.blind) add("blind", "Blind Person's Tax Credit", function (y) { return CREDITS.blind[y] || 0; }, "Only if not already on your tax credit certificate.", "blind-tax-credit.html");
    if (o.over65) add("age", "Age Tax Credit", function (y) { return (CREDITS.age[y] || 0) * (o.couple ? 2 : 1); }, "Usually automatic – check it's on your certificate.", "age-tax-credit.html");
    if (o.guideDog) add("dog", "Guide or assistance dog allowance", function () { return r0(RULES.guideDog * RULES.standardRate); }, "€825 allowance, worth €165 a year.", "guide-dog-allowance.html");
    if (o.mortgageIncrease > 0) add("mortgage", "Mortgage Interest Tax Credit", function (y) { return mortgageInterest(y, o.mortgageIncrease); },
      "20% of the rise in interest since 2022 (mortgage €80,000–€500,000 at end of 2022).", "mortgage-interest-tax-credit.html", [2023, 2024, 2025, 2026].filter(function (y) { return ys.indexOf(y) >= 0; }));
    if (o.landlord) add("landlord", "Residential Premises Rental Income Relief (landlords)", function (y) { return CREDITS.landlordMax[y] || 0; }, "Up to €600 (2024), €800 (2025), €1,000 (2026) – capped at 20% of rental profit.", "landlord-rental-income-relief.html", [2024, 2025, 2026].filter(function (y) { return ys.indexOf(y) >= 0; }));
    if (o.emergencyTax) items.push({ key: "emergency", name: "Emergency tax refund", byYear: [], total: 0, note: "Often hundreds of euro – Revenue works it out when you file a return for that year.", page: "emergency-tax-refund.html", unknown: true });
    if (o.unemployed) items.push({ key: "unemployed", name: "Refund after losing your job", byYear: [], total: 0, note: "Claim tax and USC back 4 weeks after becoming unemployed (8 if getting Jobseeker's Benefit).", page: "unemployed-tax-refund.html", unknown: true });
    if (o.taxableWelfare) items.push({ key: "welfare", name: "Check tax on your social welfare payment", byYear: [], total: 0, note: "Some payments (Illness Benefit, Jobseeker's Benefit, Maternity Benefit…) are taxed – an end-of-year review can show a refund or underpayment.", page: "social-welfare-tax.html", unknown: true });
    items.sort(function (a, b) { return b.total - a.total; });
    var total = items.reduce(function (s, x) { return s + x.total; }, 0);
    var now = o.today ? new Date(o.today) : new Date();
    var dl = Math.ceil((new Date(DEADLINE.date + "T23:59:59") - now) / 86400000);
    return { items: items, total: total, deadlineDays: dl, years: ys, rate: rate };
  }

  var api = { YEARS: YEARS, NEXT: NEXT, DEADLINE: DEADLINE, CREDITS: CREDITS, BAND: BAND, RULES: RULES,
    rentCredit: rentCredit, remoteWorking: remoteWorking, tuition: tuition, homeCarer: homeCarer, mortgageInterest: mortgageInterest, flatRate: flatRate, check: check };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.IEREF = api;
})(this);
