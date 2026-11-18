/* "What am I entitled to?" checker – runs in the browser only, nothing is stored or sent. */
(function () {
  var form = document.getElementById("entForm"), out = document.getElementById("entOut");
  if (!form || !out) return;

  // [question, title, what you get, link, link text]
  var RULES = [
    ["prsi", "Free eye test and glasses", "A free eye test every 2 years and free basic glasses or contact lenses, through Treatment Benefit.", "free-eye-test.html", "How to claim"],
    ["prsi", "Free dental check-up", "A free check-up every year, and a scale and polish for €15 or less.", "free-dental-check.html", "How to claim"],
    ["prsi", "Hearing aid grant", "Up to €500 per hearing aid (€1,000 a pair) every 4 years.", "hearing-aid-grant.html", "Who qualifies"],
    ["spouse", "Treatment Benefit on your partner's PRSI", "As a dependant spouse or partner, you can get the free eye test, dental check-up and hearing aid grant too.", "treatment-benefit.html", "Spouse rules"],
    ["rent", "Rent Tax Credit", "Up to €1,000 a year back for 2026 (€1,150 for 2027) – and you can still claim for past years back to 2022.", "../tax-refund/rent-tax-credit.html", "Check what you're owed"],
    ["medical", "Medical expenses tax relief", "20% back on GP, consultant, prescription and non-routine dental costs for the last 4 years.", "../tax-refund/medical-expenses.html", "Work out your refund"],
    ["kids", "Child Benefit", "€140 a month for each child under 16 (under 18 in full-time education or with a disability).", "child-benefit.html", "Rates and dates"],
    ["lowpay", "Working Family Payment", "A weekly top-up for parents working at least 19 hours a week (38 a fortnight) on a low income.", "working-family-payment.html", "Do I qualify?"],
    ["carer", "Carer's Allowance and Carer's Support Grant", "A weekly carer's payment (means-tested) and the €2,000 Carer's Support Grant every June.", "carers-allowance.html", "Rates for 2027"],
    ["age66", "State Pension and Free Travel", "The State Pension at 66, free public transport, and the Household Benefits Package from 70 (or 66 on certain payments).", "household-benefits-package.html", "Free Travel and Household Benefits"],
    ["alone", "Living Alone Increase", "€25 a week extra from January 2027 if you live alone on a pension or disability payment.", "living-alone-increase.html", "Who qualifies"],
    ["alone", "Telephone Support Allowance", "€2.50 a week more if you also get Fuel Allowance – paid automatically.", "telephone-support-allowance.html", "Check yours"],
    ["bill", "Additional Needs Payment", "Once-off help with essential costs like heating bills, deposits and funerals – even if you're working.", "additional-needs-payment.html", "How to apply"]
  ];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var yes = {}, n = 0;
    RULES.forEach(function (r) { var el = form.querySelector('input[name="' + r[0] + '"]:checked'); yes[r[0]] = el && el.value === "y"; });
    var hits = RULES.filter(function (r) { return yes[r[0]]; });
    var html;
    if (!hits.length) {
      html = '<div class="callout">Nothing stood out from your answers. Check the <a href="all-payments.html">full list of payments</a>, or the <a href="../tax-refund/">tax refund checker</a> – most workers are owed something.</div>';
    } else {
      html = '<h2>You could get ' + hits.length + ' thing' + (hits.length > 1 ? "s" : "") + '</h2><div class="stamp-grid">' + hits.map(function (r) {
        n++;
        return '<a class="stamp-card" href="' + esc(r[3]) + '" data-track="entitled_click" data-label="' + esc(r[3]) + '"><strong>✅ ' + esc(r[1]) + '</strong><p>' + esc(r[2]) + '</p><p><u>' + esc(r[4]) + ' →</u></p></a>';
      }).join("") + '</div><p class="muted">A guide only – your entitlement depends on your full circumstances.</p>';
    }
    out.innerHTML = html;
    if (window.TAVION && TAVION.track) TAVION.track("entitled_result", { count: hits.length });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  });
})();
