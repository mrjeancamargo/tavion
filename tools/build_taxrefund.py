"""
Builds the Tax Refund Checker app (tavion.ie/tax-refund/).
Run from the repo root:   python tools/build_taxrefund.py      (needs Node.js)
Figures come from tax-refund/js/refund.js (Revenue charts 2022-2026 + Budget 2027); jobs from tools/data/flat-rate-expenses.csv (Revenue).
"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, eur, lis, table, faq_ld, faq_html, key_facts, node, og_image

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.normpath(os.path.join(HERE, "..", "tax-refund", "js", "refund.js"))
CHECKED = "November 2026"
NODE = r"""
const R = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "check" ? R.check(Object.assign({today: "2026-11-12"}, x.o)) : x.k === "rent" ? R.rentCredit(x.y, x.r, x.c) :
    x.k === "wfh" ? R.remoteWorking(x.y, x.b, x.d, 0, x.rate) : x.k === "tuition" ? R.tuition(x.f, x.pt, 1) : x.k === "carer" ? R.homeCarer(x.y, x.i) : null);
  process.stdout.write(JSON.stringify({ C: R.CREDITS, RULES: R.RULES, YEARS: R.YEARS, BAND: R.BAND, res }));
});
"""
def run(q=()): return node(ENGINE, NODE, list(q))
M = run(); C, RULES, YEARS = M["C"], M["RULES"], M["YEARS"]
def q(*a): return run(list(a))["res"]

RV = "https://www.revenue.ie/en/"
P = RV + "personal-tax-credits-reliefs-and-exemptions/"
J = RV + "jobs-and-pensions/"
SRC = {
    "charts": ("Revenue – Tax rates, bands and reliefs 2022–2026", P + "tax-relief-charts/index.aspx"),
    "four": ("Revenue – Four year rule", P + "four-year-rule/index.aspx"),
    "rent": ("Revenue – Rent Tax Credit", P + "land-and-property/rent-credit/index.aspx"),
    "rent_amt": ("Revenue – Rent Tax Credit: how much can you claim?", P + "land-and-property/rent-credit/how-much-claim.aspx"),
    "rent_cond": ("Revenue – Rent Tax Credit: qualifying conditions", P + "land-and-property/rent-credit/qualifying-conditions.aspx"),
    "rent_child": ("Revenue – Rent Tax Credit: property used by your child", P + "land-and-property/rent-credit/used-by-child.aspx"),
    "health": ("Revenue – Health expenses", P + "health-and-age/health-expenses/index.aspx"),
    "health_q": ("Revenue – What are qualifying health expenses?", P + "health-and-age/health-expenses/what-are-qualifying-expenses.aspx"),
    "health_claim": ("Revenue – How do you claim health expenses?", P + "health-and-age/health-expenses/how-do-you-claim-health-expenses.aspx"),
    "dental": ("Revenue – Dental expenses", P + "health-and-age/health-expenses/dental-expenses.aspx"),
    "diet": ("Revenue – Additional diet expenses for coeliacs and diabetics", P + "health-and-age/health-expenses/additional-diet-expenses-for-coeliacs-and-diabetics.aspx"),
    "nursing": ("Revenue – Nursing home and additional nursing care expenses", P + "health-and-age/health-expenses/nursing-home-and-additional-nursing-care-expenses.aspx"),
    "child_health": ("Revenue – Additional health care expenses for a child", P + "health-and-age/health-expenses/additional-health-care-expenses-for-a-child.aspx"),
    "kidney": ("Revenue – Additional expenses for a kidney patient", P + "health-and-age/health-expenses/additional-expenses-for-a-kidney-patient.aspx"),
    "carer_emp": ("Revenue – Employing a carer", P + "health-and-age/employing-a-carer/index.aspx"),
    "wfh": ("Revenue – Remote working relief", J + "eworking/index.aspx"),
    "wfh_calc": ("Revenue – How to calculate allowable remote working costs", J + "eworking/calculate-allowable-remote-working-costs.aspx"),
    "wfh_costs": ("Revenue – What remote working costs can you claim?", J + "eworking/what-costs-can-you-claim-for.aspx"),
    "fre": ("Revenue – Flat Rate Expenses", P + "income-and-employment/flat-rate-expenses/index.aspx"),
    "fre_csv": ("Revenue – Flat rate expense allowance list 2021–2026 (CSV)", P + "documents/flat-rate-expenses.csv"),
    "fre_claim": ("Revenue – How to claim a flat rate expense allowance", P + "income-and-employment/flat-rate-expenses/how-to-claim-an-fre-allowance.aspx"),
    "tuition": ("Revenue – Tuition fees paid for third-level education", P + "education/tuition-fees-paid-for-third-level-education/index.aspx"),
    "language": ("Revenue – Foreign language and IT courses", P + "education/foreign-language-and-it-courses/index.aspx"),
    "homecarer": ("Revenue – Home Carer Tax Credit", P + "health-and-age/home-carer-credit/index.aspx"),
    "homecarer_rates": ("Revenue – Home Carer Tax Credit rates", P + "health-and-age/home-carer-credit/home-carer-tax-credit-rates.aspx"),
    "spccc": ("Revenue – Single Person Child Carer Credit", P + "children/single-person-child-carer-credit/index.aspx"),
    "incap": ("Revenue – Incapacitated Child Tax Credit", P + "children/incapacitated-child-credit/index.aspx"),
    "dependent": ("Revenue – Dependent Relative Tax Credit", P + "health-and-age/dependant-relative-tax-credit/index.aspx"),
    "age": ("Revenue – Age Tax Credit", P + "health-and-age/age-tax-credit/index.aspx"),
    "exempt65": ("Revenue – Exemption limits for people aged 65 and over", P + "marital-and-civil-status/exemption-and-marginal-relief/exemption-limits.aspx"),
    "blind": ("Revenue – Blind Tax Credit", P + "health-and-age/blind-tax-credit/index.aspx"),
    "dogs": ("Revenue – Assistance Dog Allowance", P + "health-and-age/assistance-dogs/index.aspx"),
    "mortgage": ("Revenue – Mortgage Interest Tax Credit", P + "land-and-property/mortgage/index.aspx"),
    "rprir": ("Revenue – Residential Premises Rental Income Relief", P + "land-and-property/rprir/index.aspx"),
    "rentaroom": ("Revenue – Rent-a-Room Relief", P + "land-and-property/rent-a-room-relief/index.aspx"),
    "microgen": ("Revenue – Tax and Duty Manual 07-01-44: microgeneration exemption (PDF)", RV + "tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-07/07-01-44.pdf"),
    "pension": ("Revenue – Tax relief limits on pension contributions", J + "pension/relief/tax-relief-limits.aspx"),
    "cycle": ("Revenue – Cycle to Work Scheme", J + "taxation-of-employer-benefits/cycle-to-work-scheme.aspx"),
    "benefits": ("Revenue – Non-taxable employer benefits", J + "taxation-of-employer-benefits/non-taxable-employer-benefits.aspx"),
    "emergency": ("Revenue – How to get a refund of Emergency Tax", J + "emergency-tax/get-refund-emergency-tax.aspx"),
    "unemployed": ("Revenue – Tax and USC refund if you are unemployed", J + "periods-of-unemployment/how-to-claim-a-tax-and-usc-refund-if-you-are-unemployed.aspx"),
    "dsp": ("Revenue – Taxation of social welfare payments", J + "taxation-of-social-welfare-payments/index.aspx"),
    "dsp_exempt": ("Revenue – Tax-exempt social welfare payments", J + "taxation-of-social-welfare-payments/tax-exempt-dsp-benefits.aspx"),
    "dsp_taxed": ("Revenue – Taxable social welfare payments", J + "taxation-of-social-welfare-payments/no-declaration-needed.aspx"),
    "return": ("Revenue – PAYE Income Tax Return", J + "end-of-year-process/paye-income-tax-return.aspx"),
    "insurance": ("Revenue – Medical insurance relief from 1 January 2026", P + "health-and-age/medical-insurance-premiums/trs-from-010126.aspx"),
    "myaccount": ("Revenue – myAccount", "https://www.ros.ie/myaccount-web/sign_in.html"),
    "budget": ("Chartered Accountants Ireland – Budget 2027 income tax measures", "https://www.charteredaccountants.ie/budget-updates/budget-2027/news/budget-2027-income-tax-measures"),
    "budget_h": ("Chartered Accountants Ireland – Budget 2027 housing measures", "https://www.charteredaccountants.ie/budget-updates/budget-2027/news/budget-2027-housing-and-property-measures"),
    "ci": ("Citizens Information – Tax credits and reliefs", "https://www.citizensinformation.ie/en/money-and-tax/tax/income-tax-credits-and-reliefs/"),
}

TABS = [("./", "Checker"), ("deadline-2022.html", "31 Dec deadline"), ("medical-expenses.html", "Medical"), ("rent-tax-credit.html", "Rent credit"),
        ("remote-working-relief.html", "Work from home"), ("flat-rate-expenses.html", "Your job"), ("all-reliefs.html", "All reliefs"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Tax refund checker</a><a href="deadline-2022.html">Claim 2022 by 31 December</a><a href="how-to-claim.html">How to claim in myAccount</a><a href="all-reliefs.html">All credits &amp; reliefs</a>'
        '<a href="medical-expenses.html">Medical expenses</a><a href="can-i-claim.html">Can I claim…?</a><a href="rent-tax-credit.html">Rent Tax Credit</a><a href="remote-working-relief.html">Remote working</a>'
        '<a href="flat-rate-expenses.html">Flat-rate expenses by job</a><a href="tax-credits-by-year.html">Tax credits 2022–2027</a><a href="budget-2027.html">Budget 2027 changes</a><a href="faq.html">FAQ</a>')
app = App("tax-refund", "Tax Refund Checker", "💸", None, "#0f766e", TABS, FOOT, SRC, None,
          "Am I owed a tax refund? Free checker for rent, medical, working from home and more – claims for 2022 close on 31 December:",
          "Most people never claim. Send this to someone who rents, works from home or paid a medical bill.", "taxrefund",
          f"Rules and amounts checked against Revenue in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>, not affiliated with Revenue. "
          "Estimates are the most you could get back – a credit can't refund more Income Tax than you paid that year. This is not tax advice.")
CROSS = ["salary", "welfare", "rent", "mortgage"]

def r2(n): return eur(n)
STEPS_PREV = ["Sign in to <strong>myAccount</strong> on revenue.ie.", "Click <strong>Review your tax for the previous 4 years</strong> under PAYE Services.",
              "Request a <strong>Statement of Liability</strong> for the year, then click <strong>Complete Income Tax Return</strong>.",
              "In <strong>Tax Credits &amp; Reliefs</strong>, add the credit or relief and submit. Refunds usually arrive within about five working days."]
STEPS_NOW = ["Sign in to <strong>myAccount</strong>.", "Click <strong>Manage your tax for the current year</strong> under PAYE Services.", "Choose <strong>Add new credits</strong> (or Claim tax credits) and select it – your tax credits update straight away."]
def how_to(extra=None, now=True):
    h = '<h2>How to claim</h2><div class="card"><div class="tl">For 2022–2025 (and 2026 after the year ends)</div><ol class="steps">' + "".join(f"<li>{s}</li>" for s in STEPS_PREV) + "</ol>"
    if now: h += '<div class="tl" style="margin-top:12px">For this year (2026)</div><ol class="steps">' + "".join(f"<li>{s}</li>" for s in STEPS_NOW) + "</ol>"
    if extra: h += f'<p class="small" style="margin-bottom:0">{extra}</p>'
    return h + "</div>"
DEADLINE_BOX = '<div class="callout warn">⏰ <strong>Claims for 2022 close on 31 December 2026.</strong> After that, any 2022 refund is lost for good. <a href="deadline-2022.html">What you can still claim for 2022 →</a></div>'
CTA = '<div class="cta"><h2>What else are you owed?</h2><p>Answer a few quick questions – rent, health, work from home, your job – and see your total.</p><a class="btn" href="./">Check my refund</a></div>'

# ---------- Checker ----------
def build_index():
    ex = q({"k": "check", "o": {"rentMonthly": 1400, "medical": 900, "wfhDays": 100, "wfhBills": 2600, "flatRate": 0}})[0]
    body = f"""<p class="lead">Rent, doctor and dentist bills, working from home, your job's uniform, college fees… Most people are owed money back from Revenue and never claim it. Answer a few questions to see roughly how much – for the last four years. Free, no sign-up.</p>
<ul class="facts"><li>Back to 2022</li><li>2022 closes 31 Dec 2026</li><li>Refunds in ~5 days</li></ul>
{DEADLINE_BOX}
<form id="refForm" class="card" novalidate>
  <fieldset><legend>About you</legend>
    <div class="seg"><label><input type="radio" name="status" value="single" checked><span>Single</span></label><label><input type="radio" name="status" value="couple"><span>Married / civil partners<small>jointly assessed</small></span></label></div>
    <label class="check"><input type="checkbox" id="higherRate"><span>I pay tax at 40% <small>– single and earning over about €44,000</small></span></label>
  </fieldset>
  <fieldset><legend>🏠 Your home</legend>
    <label>Rent you pay per month (€) <input id="rentMonthly" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label class="check"><input type="checkbox" id="hap"><span>My rent is paid through HAP, Rent Supplement or RAS</span></label>
    <label>Rent you pay for a child at college, per month (€) <input id="studentRentMonthly" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label class="check"><input type="checkbox" id="mortgage"><span>My mortgage interest went up since 2022 <small>(mortgage €80k–€500k at end of 2022)</small></span></label>
    <label id="mortgageRow" hidden>About how much more interest a year than in 2022 (€) <input id="mortgageIncrease" type="number" inputmode="decimal" min="0" placeholder="2,000"></label>
    <label class="check"><input type="checkbox" id="landlord"><span>I'm a landlord renting out a home long-term</span></label>
  </fieldset>
  <fieldset><legend>🩺 Health (per year, what you paid yourself)</legend>
    <div class="two"><label>Doctor, consultant, hospital, tests (€)<input id="medical" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label>Prescriptions and medicines (€)<input id="prescriptions" type="number" inputmode="decimal" min="0" placeholder="0"></label></div>
    <div class="two"><label>Braces, crowns, root canal, implants (€)<input id="dental" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label>Physio, chiropractor, counselling (€)<input id="therapy" type="number" inputmode="decimal" min="0" placeholder="0"></label></div>
    <label>Gluten-free or diabetic food (coeliac / diabetic) (€)<input id="glutenFree" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label>Nursing home fees you paid (€)<input id="nursingHome" type="number" inputmode="decimal" min="0" placeholder="0"></label>
  </fieldset>
  <fieldset><legend>💻 Work</legend>
    <div class="two"><label>Days a year you work from home<input id="wfhDays" type="number" inputmode="numeric" min="0" max="366" placeholder="0"></label>
    <label>Electricity + heating + broadband a year (€)<input id="wfhBills" type="number" inputmode="decimal" min="0" placeholder="2,400"></label></div>
    <label>Your job (for flat-rate expenses)<select id="job"><option value="">Not on the list / not sure</option></select></label>
    <label class="check"><input type="checkbox" id="emergencyTax"><span>I was on emergency tax at some point</span></label>
    <label class="check"><input type="checkbox" id="unemployed"><span>I lost my job or stopped working this year</span></label>
    <label class="check"><input type="checkbox" id="taxableWelfare"><span>I got Illness, Jobseeker's, Maternity or Carer's payments</span></label>
  </fieldset>
  <details class="adv"><summary>More: family, college, age <span class="muted small">– carers, single parents, 65+</span></summary><div class="adv-body">
    <label>College tuition fees you paid per year (€) <input id="tuitionFees" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label class="check"><input type="checkbox" id="tuitionPT"><span>Part-time course</span></label>
    <label class="check"><input type="checkbox" id="homeCarer"><span>One of us stays home caring for a child, someone 65+ or someone with a disability</span></label>
    <label id="carerIncomeRow" hidden>The carer's own income a year (€) <input id="carerIncome" type="number" inputmode="decimal" min="0" placeholder="0"></label>
    <label class="check"><input type="checkbox" id="singleParent"><span>I'm a single parent (not living with a partner)</span></label>
    <label class="check"><input type="checkbox" id="incapChild"><span>I have a child with a permanent disability</span></label>
    <label class="check"><input type="checkbox" id="dependent"><span>I support an elderly or incapacitated relative</span></label>
    <label class="check"><input type="checkbox" id="over65"><span>I am (or my spouse is) 65 or over</span></label>
    <label class="check"><input type="checkbox" id="blind"><span>I am (or my spouse is) registered blind</span></label>
    <label class="check"><input type="checkbox" id="guideDog"><span>I have a guide or assistance dog</span></label>
  </div></details>
  <div class="btn-row"><button type="submit" class="btn primary">Show what I'm owed</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your phone. Nothing is sent to us. We never ask for your PPS number.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>The most-missed refunds</h2>
<div class="card"><ol class="steps">
<li><strong>Rent Tax Credit</strong> – up to {r2(C['rent']['2026'])} a year ({r2(C['rent']['2026'] * 2)} for a couple), back to 2022. Parents paying a student's rent can claim too. <a href="rent-tax-credit.html">More</a></li>
<li><strong>Medical expenses</strong> – 20% back on GP, consultant, prescriptions, physio, braces, crowns, IVF, even gluten-free food for coeliacs. <a href="medical-expenses.html">More</a></li>
<li><strong>Working from home</strong> – 30% of your electricity, heating and broadband for days at home, at your top rate of tax. <a href="remote-working-relief.html">More</a></li>
<li><strong>Your job</strong> – nurses, teachers, shop staff, builders, hotel staff and 60+ other jobs get a flat-rate expense every year. <a href="flat-rate-expenses.html">Find your job</a></li>
<li><strong>Emergency tax</strong> and <strong>losing a job</strong> – often hundreds back. <a href="emergency-tax-refund.html">More</a></li>
</ol></div>
<p>Example: renting at €1,400 a month, €900 a year in medical bills and 100 days working from home could add up to about <strong>{r2(ex['total'])}</strong> over 2022–2026.</p>
<div class="chip-list"><a href="can-i-claim.html">Can I claim…?</a><a href="deadline-2022.html">2022 deadline</a><a href="how-to-claim.html">How to claim</a><a href="budget-2027.html">Budget 2027</a><a href="social-welfare-tax.html">Tax on welfare</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Tax Refund Checker Ireland", "url": app.BASE, "applicationCategory": "FinanceApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Check which Irish tax credits and reliefs you can claim back for 2022–2026 – Rent Tax Credit, medical expenses, remote working relief, flat-rate expenses and more – with an estimate of your refund."}
    faqs = [("Am I owed a tax refund in Ireland?", "Many PAYE workers are. The most common unclaimed refunds are the Rent Tax Credit, medical and non-routine dental expenses, remote working relief and flat-rate expenses for your job. You can claim back four years."),
            ("What is the deadline to claim 2022 tax back?", "31 December 2026. Under the four-year rule, claims for 2022 must be made by then or the refund is lost.")]
    app.page("index.html", "Am I Owed a Tax Refund? Free Irish Tax Refund Checker 2022–2026",
             "Free Revenue tax refund checker: Rent Tax Credit, medical and dental expenses, working from home, flat-rate expenses for your job, emergency tax and more. Claim 2022 before 31 December 2026.",
             body, active="Checker", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["js/refund.js", "js/jobs.js", "js/check.js"], h1="Am I owed a tax refund?",
             sources=("charts", "four", "rent", "health_q", "wfh"), cross=CROSS, priority="1.0",
             share_text="Most people are owed tax back and never claim. This free checker shows what you could get – 2022 claims close 31 December:")

# ---------- Relief guide pages ----------
def credits_row(key, mult=1):
    return [eur(C[key][str(y)] * mult) if str(y) in C[key] else "–" for y in (2022, 2023, 2024, 2025, 2026, 2027)]

def build_guides():
    rent_ex = q({"k": "rent", "y": 2025, "r": 1200 * 12, "c": False}, {"k": "rent", "y": 2022, "r": 1200 * 12, "c": False})
    wfh_ex = q({"k": "wfh", "y": 2025, "b": 2400, "d": 150, "rate": 0.2}, {"k": "wfh", "y": 2025, "b": 2400, "d": 150, "rate": 0.4})
    tu = q({"k": "tuition", "f": 3000, "pt": False}, {"k": "tuition", "f": 6000, "pt": False}, {"k": "tuition", "f": 4000, "pt": True})
    hc = q({"k": "carer", "y": 2026, "i": 0}, {"k": "carer", "y": 2026, "i": 9000})
    G = []  # (file, title, desc, h1, lead, facts, extra_html, sources, faqs, howto_extra, active)
    G.append(("rent-tax-credit.html", "Rent Tax Credit Ireland – Claim Up to €1,000 a Year Back to 2022 (€1,150 in 2027)",
              "Rent Tax Credit explained: 20% of rent paid, up to €1,000 a year (€2,000 for couples) for 2024–2026, €500 for 2022–2023 and €1,150 from 2027. Who qualifies and how to claim back to 2022.",
              "Rent Tax Credit", "If you rent your home, you can get up to €1,000 a year back in tax – and claim back to 2022.",
              [f"20% of the rent you paid, up to <strong>{eur(C['rent']['2026'])} a year</strong> for 2024, 2025 and 2026 ({eur(C['rent']['2026'] * 2)} for a jointly assessed couple).",
               f"<strong>{eur(C['rent']['2022'])}</strong> a year for 2022 and 2023 ({eur(C['rent']['2022'] * 2)} for couples).",
               f"<strong>Budget 2027:</strong> rises to <strong>{eur(C['rent']['2027'])}</strong> ({eur(C['rent']['2027'] * 2)} for couples) for 2027 and 2028.",
               "Your tenancy must be registered with the RTB where registration is required. Digs and rent-a-room count too (not if the landlord is a relative).",
               "<strong>Not available</strong> if your rent is paid through HAP, Rent Supplement or RAS, or your landlord is an Approved Housing Body.",
               "It can only reduce Income Tax you paid – not USC or PRSI.", f"Example: €1,200 a month = {eur(rent_ex[0])} for 2025 and {eur(rent_ex[1])} for 2022."],
              table(["", "2022", "2023", "2024", "2025", "2026", "2027"], [["Single"] + credits_row("rent"), ["Couple"] + credits_row("rent", 2)]) +
              '<h2>Rent credit by monthly rent</h2><div class="chip-list">' + "".join(f'<a href="rent-tax-credit-{m}.html">€{m:,} a month</a>' for m in RENTS) + "</div>" +
              '<p>Paying rent for a son or daughter at college? <a href="rent-tax-credit-students.html">Parents can claim too →</a> · Is your rent going up? <a href="../rent/" data-track="cross_app" data-label="rent_from_refund">Check if the increase is legal →</a></p>',
              ("rent", "rent_amt", "rent_cond", "charts", "budget_h"),
              [("How much is the Rent Tax Credit?", "Up to €1,000 a year for 2024–2026 (€2,000 for a jointly assessed couple), €500 for 2022 and 2023, and €1,150 from 2027."),
               ("Can I claim the Rent Tax Credit for previous years?", "Yes, back to 2022 – but 2022 claims must be made by 31 December 2026."),
               ("Can I get the Rent Tax Credit if I'm on HAP?", "No. Supported tenants on HAP, Rent Supplement or RAS can't claim, even if you pay a top-up.")], "You'll need your landlord's name, address and RTB number (if registered) and the rent you paid.", "Rent credit"))
    G.append(("rent-tax-credit-students.html", "Rent Tax Credit for Parents of Students – Claim Your Child's College Rent",
              "Parents paying rent for a student child at college can claim the Rent Tax Credit: up to €1,000 a year, digs included, child under 23 when the course started.",
              "Rent Tax Credit for students' parents", "Paying for your son or daughter's room near college? You can claim the Rent Tax Credit on it.",
              ["Parents can claim if the rented room is used by their child to attend an <strong>approved course</strong> (the same list as tuition fee relief).",
               "The child must have been <strong>under 23</strong> at the start of the tax year their course began.", "<strong>Digs and rent-a-room</strong> arrangements qualify for 2022–2028.",
               "It doesn't count if you, or your child, are related to the landlord.", "Students' accommodation must be registered with the RTB where required (including student-specific accommodation).",
               f"The same cap applies: up to {eur(C['rent']['2026'])} a year ({eur(C['rent']['2026'] * 2)} for a couple), shared with any other rent you claim."],
              '<p>Also see <a href="tuition-fees.html">tax relief on college fees</a> and the <a href="../cao/" data-track="cross_app" data-label="cao_from_refund">CAO points calculator</a>.</p>',
              ("rent_child", "rent"), [("Can parents claim rent tax credit for students?", "Yes, if the child was under 23 when the approved course started and the landlord isn't related to you.")], None, "Rent credit"))
    G.append(("medical-expenses.html", "Medical Expenses Tax Relief Ireland – Get 20% Back (GP, Consultant, Physio, IVF, Dental)",
              "Claim 20% back on medical expenses in Ireland: GP and consultant visits, prescriptions, physio, IVF, non-routine dental, gluten-free food and more, back to 2022.",
              "Medical expenses tax relief", "Every doctor's visit, prescription and physio session you paid for can give you 20% back – for the last four years.",
              ["You get <strong>20% back</strong> on health expenses you paid yourself (40% for nursing homes).", "It covers your own bills and those you paid for <strong>anyone</strong> – a child, partner or parent.",
               "Only the part not paid back by health insurance, the HSE or compensation counts.", "Keep receipts for <strong>six years</strong>. You don't send them in unless Revenue asks.",
               "You must have paid Income Tax that year to get a refund.", "Spent €2,000 on health in a year? That's <strong>€400 back</strong> – €1,600 over four years."],
              '<h2>What you can claim</h2>' + lis(["GP and consultant fees", "Prescribed drugs and medicines", "Physiotherapy, chiropractor, osteopath (if referred)", "Psychologist or psychotherapist (if a registered practitioner, or referred)",
              "IVF", "Maternity care", "Diagnostic tests and scans", "Non-routine dental: crowns, braces, root canal, implants", "Gluten-free food for coeliacs; diabetic products", "Hearing aids and medical appliances",
              "Podiatry and chiropody", "Ambulance", "Treatment abroad (and travel if it isn't available here)", "Pharmacy consultations under the Common Conditions Service"]) +
              '<h2>What you can\'t claim</h2>' + lis(["Routine dental care (cleaning, fillings, extractions)", "Routine eye tests, glasses and contact lenses", "Cosmetic procedures", "Anything paid back by your health insurer"]) +
              '<p><a href="can-i-claim.html">Can I claim…? Check a specific treatment →</a></p>',
              ("health", "health_q", "health_claim"), [("How much do you get back on medical expenses in Ireland?", "20% of what you paid, at the standard rate. Nursing home fees get relief at your highest rate (up to 40%)."),
              ("Can I claim medical expenses for my family?", "Yes – for anyone, as long as you paid the bill.")], "You no longer need a Med 1 form. For non-routine dental, ask your dentist for a Med 2 and keep it.", "Medical"))
    G.append(("non-routine-dental.html", "Dental Tax Relief Ireland – Braces, Crowns, Root Canal & Implants (Med 2)",
              "Claim 20% back on non-routine dental treatment: crowns, veneers, braces, root canal, implants, gum treatment and surgical wisdom teeth removal. Routine care doesn't qualify.",
              "Dental expenses tax relief", "Braces, crowns, root canals and implants qualify for 20% back. Cleaning and fillings don't.",
              ["Claim <strong>20%</strong> of non-routine dental treatment.", "Your dentist gives you a <strong>Med 2</strong> form – keep it; don't send it unless asked.", "Treatment abroad qualifies if the dentist is qualified in that country (they complete the Med 2).",
               "Braces for children count – the parent who paid claims.", "€5,000 of orthodontics = <strong>€1,000 back</strong>."],
              '<div class="two"><div class="card"><div class="tl">✅ Qualifies</div>' + lis(["Crowns and veneers", "Root canal (endodontics)", "Braces / orthodontics", "Implants, including bone grafts", "Bridgework", "Gum treatment (periodontal)", "Surgical removal of impacted wisdom teeth", "Inlays, gold or fibreglass posts"]) +
              '</div><div class="card"><div class="tl">❌ Doesn\'t qualify</div>' + lis(["Scaling and cleaning", "Fillings", "Extractions (non-surgical)", "Dentures and repairs"]) + "</div></div>",
              ("dental", "health_claim"), [("Can I claim tax back on braces?", "Yes – orthodontic treatment is non-routine dental care and gets 20% relief."), ("Can I claim for fillings?", "No – fillings are routine dental care.")], "Add it under the Non-Routine Dental heading.", "Medical"))
    G.append(("coeliac-gluten-free-tax-relief.html", "Gluten-Free Food Tax Relief for Coeliacs Ireland – Claim 20% Back",
              "Coeliacs can claim 20% tax relief on gluten-free food with a doctor's letter. Supermarket receipts and loyalty statements count. Diabetic products qualify too.",
              "Gluten-free food tax relief (coeliacs)", "If you're coeliac, the gluten-free food you buy counts as a health expense – 20% back.",
              ["You need a <strong>letter from your doctor</strong> stating the condition and dietary needs – upload it through MyEnquiries in myAccount.",
               "Claim food <strong>specifically manufactured to be gluten-free</strong>.", "Keep receipts – most supermarkets can give loyalty-card customers a statement of gluten-free purchases.",
               "Store receipts in the <strong>Receipts Tracker</strong> in myAccount.", "Add the total to your health expenses claim. €1,500 a year on gluten-free food = €300 back, €1,200 over four years.",
               "Diabetics can claim diabetic products their doctor recommends in the same way."], "", ("diet", "health_claim"),
              [("Can coeliacs claim tax relief on gluten-free food?", "Yes – with a doctor's letter, you can claim 20% of gluten-free food specifically manufactured to be gluten-free.")], "Include it in your health expenses on your Income Tax Return.", "Medical"))
    G.append(("diabetic-tax-relief.html", "Diabetes Tax Relief Ireland – Diabetic Products, Medicines & Appliances",
              "Tax relief for diabetics in Ireland: diabetic food products recommended by your doctor, medicines and appliances – 20% back as health expenses.",
              "Tax relief for diabetes", "Diabetic products your doctor recommends, plus medicines and appliances you paid for, can give you 20% back.",
              ["Diabetic food products count if your doctor recommends them – you need a <strong>doctor's letter</strong>.", "Prescribed medicines and medical appliances you paid for qualify.",
               "Only what you paid yourself counts – not what the HSE (for example the Long-Term Illness Scheme) or insurance covered.", "Keep receipts for six years."], "", ("diet", "health_q"),
              [("Can diabetics claim tax back?", "Yes – on diabetic products recommended by a doctor and other qualifying health expenses you paid, at 20%.")], None, "Medical"))
    G.append(("nursing-home-fees.html", "Nursing Home Fees Tax Relief Ireland – Relief at 40%",
              "Tax relief on nursing home fees is at your highest rate (up to 40%) where the home has 24-hour nursing care. Fair Deal contributions and loan repayments explained.",
              "Nursing home fees tax relief", "Paying for a parent's nursing home? You can get relief at your top rate – up to 40%.",
              ["Relief is at your <strong>highest rate of tax</strong> (up to 40%), not 20%.", "The home must provide <strong>24-hour on-site nursing care</strong>.", "You can claim what you paid yourself – not the part paid by the HSE (Fair Deal).",
               "Fair Deal loan repayments can be claimed when repaid (by you, or the executor).", "€20,000 paid at 40% = up to <strong>€8,000 back</strong> a year."],
              '<p>Also see <a href="home-care-tax-relief.html">employing a carer at home</a> and the <a href="dependent-relative-tax-credit.html">Dependent Relative Tax Credit</a>.</p>', ("nursing", "health_claim"),
              [("What tax relief can I get on nursing home fees?", "Relief at your highest rate (up to 40%) on fees you paid to a nursing home with 24-hour nursing care.")], "You can also claim during the year as a real-time credit.", "Medical"))
    G.append(("home-care-tax-relief.html", "Tax Relief for Employing a Carer – Up to €75,000 at 40%",
              "Employing a carer for someone totally incapacitated? Claim tax relief at your highest rate on up to €75,000 a year per person. Also home nursing as a health expense.",
              "Employing a carer: tax relief", "If you employ someone to care for an incapacitated relative (or yourself), you can deduct up to €75,000 a year.",
              ["Relief at your <strong>highest rate</strong> on the lower of the actual cost or <strong>€75,000</strong> per incapacitated person.", "The person cared for must be <strong>totally incapacitated</strong> by physical or mental disability.",
               "Qualified home nursing on a doctor's advice can instead be claimed as a <strong>health expense</strong>.", "You'll have employer obligations if you employ the carer directly."], "", ("carer_emp", "nursing"),
              [("Can I get tax relief for paying a carer?", "Yes – up to €75,000 a year per incapacitated person, at your highest rate.")], None, None))
    G.append(("child-health-expenses.html", "Tax Relief on Speech Therapy, Educational Psychologist & Child Hospital Costs",
              "Claim 20% back on speech and language therapy, educational psychological assessments, and the extra travel, accommodation and phone costs of a seriously ill child.",
              "Health expenses for children", "Speech therapy, an educational psychologist's assessment and the extra costs of a seriously ill child all qualify.",
              ["<strong>Speech and language therapy</strong> by a qualified therapist – 20% back.", "<strong>Educational psychologist assessments</strong> – 20% back.",
               "For a child with a <strong>life-threatening illness or permanent disability</strong> (including child cancer patients): travel to hospital, overnight accommodation near the hospital and phone costs.",
               "A child is under 18, or over 18 in full-time education.", "Car travel is claimed per kilometre (24c a km for 2023–2025)."], "", ("child_health", "health_claim"),
              [("Can I claim tax back on speech therapy?", "Yes – speech and language therapy for a child by a qualified therapist qualifies for 20% relief.")], None, "Medical"))
    G.append(("kidney-patient-tax-relief.html", "Tax Relief for Kidney Patients – Dialysis Travel and Home Dialysis Costs",
              "Kidney patients can claim travel to dialysis per kilometre and flat-rate relief on electricity, laundry and phone for home dialysis.",
              "Kidney patients: extra tax relief", "Dialysis patients can claim more than standard health expenses.",
              ["Hospital dialysis: travel to and from hospital, <strong>24c a km</strong> by car (2023–2025), with no limit on journeys.", "Home dialysis: flat-rate relief for electricity, laundry and protective clothing, and phone (for 2025: €3,614, €2,410 and €390).",
               "Claimed as part of your health expenses."], "", ("kidney",), [], None, "Medical"))
    G.append(("remote-working-relief.html", "Remote Working Relief Ireland – Claim 30% of Electricity, Heating & Broadband",
              "Working from home? Claim 30% of your electricity, heating and broadband for the days you worked from home, at your highest rate of tax. Calculator and examples.",
              "Remote working relief", "Working from home some days? You can claim back part of your electricity, heating and broadband bills.",
              ["You can claim <strong>30%</strong> of electricity, heating and broadband, for the share of the year you worked from home.",
               "Formula: ((bills × days at home ÷ 365) − employer allowance) × 30%, relieved at your <strong>highest rate</strong> of tax.",
               "Only count real remote working days – not weekends, holidays, annual leave or bringing work home in the evening.",
               f"If your employer pays the tax-free <strong>€{RULES['remoteAllowancePerDay']:.2f} a day</strong>, that's taken off.", "Shared bills? Split them by what each person paid.",
               f"Example: €2,400 of bills and 150 days at home = {eur(wfh_ex[0]['allowable'])} allowable – <strong>{eur(wfh_ex[0]['refund'])} back</strong> at 20% or {eur(wfh_ex[1]['refund'])} at 40%.",
               "Laptops, desks and chairs you bought don't qualify."],
              '<h2>By days a week</h2><div class="chip-list">' + "".join(f'<a href="remote-working-{d}-days.html">{d} day{"s" if d > 1 else ""} a week</a>' for d in range(1, 6)) + "</div>",
              ("wfh", "wfh_calc", "wfh_costs"), [("How much can I claim for working from home in Ireland?", "30% of electricity, heating and broadband costs, apportioned by the days you worked from home, at your highest tax rate."),
              ("Do I need receipts for remote working relief?", "Yes – upload your bills to the Receipts Tracker in myAccount.")], "Upload your bills to the Receipts Tracker in myAccount, then claim on your Income Tax Return.", "Work from home"))
    G.append(("tuition-fees.html", "Tuition Fees Tax Relief Ireland – 20% Back on College Fees",
              "Tax relief on third-level tuition fees: 20% of fees (including the student contribution) above €3,000 full-time or €1,500 part-time, up to €7,000 per course.",
              "Tuition fees tax relief", "Paying college fees for yourself or your children? You can get 20% back on the part above the first €3,000.",
              ["20% relief on tuition fees <strong>including the student contribution</strong>, up to <strong>€7,000 per course</strong> per year.",
               "The first <strong>€3,000</strong> (full-time) or <strong>€1,500</strong> (part-time) of each claim isn't relieved – but it's only taken off once, however many students you pay for.",
               "So with two children in college, the second child's contribution gets full relief.", "Levies, registration and sports centre charges don't count. Fees covered by a grant (SUSI) don't count.",
               f"Examples: one full-time student, €3,000 = {eur(tu[0])}; €6,000 of fees = <strong>{eur(tu[1])}</strong>; part-time €4,000 = {eur(tu[2])}.",
               "<strong>Budget 2027:</strong> the disregard is being cut to match the Student Contribution – check the final rules for 2027."],
              '<p>Also: <a href="foreign-language-it-courses.html">foreign language and IT courses</a> · <a href="rent-tax-credit-students.html">rent for a student</a> · <a href="../cao/" data-track="cross_app" data-label="cao_from_refund">CAO points calculator</a></p>',
              ("tuition", "budget"), [("Can I claim tax back on college fees?", "Yes – 20% on fees above €3,000 (full-time) or €1,500 (part-time), up to €7,000 per course."),
              ("Can I claim for two children in college?", "Yes, and the €3,000 disregard applies only once, so the second child's fees get full 20% relief.")], None, None))
    G.append(("foreign-language-it-courses.html", "Tax Relief on Foreign Language and IT Courses Ireland",
              "20% tax relief on approved foreign language and IT courses costing €315–€1,270 that end with a certificate of competence.",
              "Foreign language and IT courses", "Short approved courses in a foreign language or IT can get 20% back.",
              ["Course fees between <strong>€315 and €1,270</strong>, at 20%.", "Must be on the approved list, under two years and end with a certificate of competence (not attendance).",
               "Irish and English courses don't qualify.", "One course per person per year. Fees paid by a grant or employer don't count."], "", ("language",), [], None, None))
    G.append(("home-carer-tax-credit.html", "Home Carer Tax Credit 2026 – €1,950 (€2,050 in 2027): Who Qualifies",
              "Home Carer Tax Credit: €1,950 for 2026 and €2,050 from 2027 for married or civil partners where one cares for a child, someone 65+ or someone with a disability.",
              "Home Carer Tax Credit", "If one of you stays at home to care for children or a relative, you could be owed up to €1,950 a year – back to 2022.",
              [f"Worth up to <strong>{eur(C['homeCarer']['2026'])}</strong> for 2026 and <strong>{eur(C['homeCarer']['2027'])}</strong> from 2027 (Budget 2027).",
               "For <strong>married couples or civil partners</strong> who are jointly assessed.", "The person cared for must be a child you get Child Benefit for, someone 65+, or someone permanently incapacitated.",
               f"Full credit if the carer earns under <strong>€{RULES['homeCarerIncomeLimit']:,}</strong> (not counting Carer's Allowance/Benefit); reduced by half of the excess above that.",
               f"Example: carer earns €9,000 in 2026 → credit of {eur(hc[1])}.", "You can't claim it and the increased rate band for two earners on the same income – Revenue gives whichever is better."],
              table(["", "2022", "2023", "2024", "2025", "2026", "2027"], [["Max credit"] + credits_row("homeCarer")]) + '<p>Getting Carer\'s Allowance? <a href="../welfare/carers-allowance.html">2027 rates →</a></p>',
              ("homecarer", "homecarer_rates", "charts", "budget"), [("How much is the Home Carer Tax Credit?", "€1,950 for 2026 and €2,050 for 2027. Earlier years: €1,600 (2022), €1,700 (2023), €1,800 (2024), €1,950 (2025).")], None, None))
    G.append(("single-person-child-carer-credit.html", "Single Person Child Carer Credit 2026 – €1,900 + Wider Tax Band",
              "Single parents can claim the Single Person Child Carer Credit (€1,900 for 2025 and 2026) and a €4,000 wider standard rate band. Who qualifies and back-claims.",
              "Single Person Child Carer Credit", "Single parents get an extra tax credit and a wider 20% tax band. If you never claimed it, you can go back to 2022.",
              [f"Worth <strong>{eur(C['spccc']['2026'])}</strong> a year for 2025 and 2026 ({eur(C['spccc']['2022'])} in 2022–2023, {eur(C['spccc']['2024'])} in 2024).",
               "Plus a standard rate band €4,000 wider than a single person's (€48,000 in 2026).", "You must not be married, in a civil partnership or <strong>cohabiting</strong>.",
               "Your child must live with you for most of the year and be under 18, or in full-time education.", "The main carer can give it up to the other parent (secondary claimant)."],
              table(["", "2022", "2023", "2024", "2025", "2026"], [["Credit"] + credits_row("spccc")[:5]]), ("spccc", "charts"), [], None, None))
    G.append(("incapacitated-child-tax-credit.html", "Incapacitated Child Tax Credit 2026 – €3,800 a Year",
              "Incapacitated Child Tax Credit: €3,800 a year for 2025–2026 for a child with a permanent disability. Who qualifies and how to claim back four years.",
              "Incapacitated Child Tax Credit", "If your child has a permanent physical or mental disability, you could claim €3,800 a year – and backdate it four years.",
              [f"<strong>{eur(C['incapChild']['2026'])}</strong> a year for 2025 and 2026 ({eur(C['incapChild']['2022'])} for 2022–2023, {eur(C['incapChild']['2024'])} for 2024).",
               "For a child under 18 who is permanently incapacitated, or over 18 and unable to maintain themselves (incapacitated before 21, or while in full-time education).",
               "A doctor's certificate is needed with your first claim.", "Four years backdated could be worth over <strong>€14,000</strong>."],
              '<p>Also: <a href="../welfare/domiciliary-care-allowance.html">Domiciliary Care Allowance</a> · <a href="child-health-expenses.html">child health expenses</a></p>', ("incap", "charts"), [], None, None))
    G.append(("dependent-relative-tax-credit.html", "Dependent Relative Tax Credit 2026 – €305 a Year",
              "Dependent Relative Tax Credit: €305 for 2025 and 2026 (€245 for 2022–2024) if you support an elderly or incapacitated relative whose income is under €18,548.",
              "Dependent Relative Tax Credit", "Supporting an elderly or incapacitated relative? There's a small credit you can claim back four years.",
              [f"<strong>{eur(C['dependent']['2026'])}</strong> for 2025 and 2026; €245 for 2022–2024.", "Your relative's income must be under <strong>€18,548</strong> (2026), including welfare and pensions.",
               "Also for a widowed parent (incapacitated or not).", "The relative doesn't have to live in Ireland.", "If several people support them, the credit is shared."], "", ("dependent",), [], None, None))
    G.append(("age-tax-credit.html", "Age Tax Credit – €245 (€490 for Couples) at 65+", "The Age Tax Credit is €245 single or €490 for couples when you or your spouse turn 65. Check it's on your tax credit certificate.",
              "Age Tax Credit", "Turned 65? Make sure the Age Tax Credit is on your tax credits.", ["<strong>€245</strong> single, <strong>€490</strong> married or civil partners.", "Due from the year you or your spouse turn 65.",
              "It should be given automatically – but if Revenue doesn't have your date of birth, it may be missing. Check your Tax Credit Certificate.",
              'If your income is under <strong>€18,000</strong> (single) or <strong>€36,000</strong> (couple), you may pay no Income Tax at all – <a href="over-65-tax-exemption.html">see the over-65 exemption</a>.'], "", ("age", "exempt65"), [], None, None))
    G.append(("over-65-tax-exemption.html", "Over 65 Tax Exemption Ireland – No Income Tax Under €18,000 / €36,000",
              "People aged 65+ pay no Income Tax if income is under €18,000 (single) or €36,000 (couple), plus €575 per child for the first two. Marginal relief explained.",
              "Income Tax exemption at 65+", "If you're 65 or over and your income is under the limit, you pay no Income Tax at all.",
              ["Single, 65+: no Income Tax if total income is <strong>€18,000</strong> or less.", "Married or civil partners (either 65+): <strong>€36,000</strong> or less.",
               "Limits rise by €575 for each of the first two dependent children and €830 for each extra child.", "Just over the limit? <strong>Marginal relief</strong> may lower your bill.", "USC and PRSI rules are separate."],
              '<p>State Pension rates: <a href="../welfare/state-pension-contributory.html">Contributory</a> · <a href="../welfare/state-pension-non-contributory.html">Non-Contributory</a></p>', ("exempt65",), [], None, None))
    G.append(("blind-tax-credit.html", "Blind Person's Tax Credit 2026 – €1,950", "Blind Person's Tax Credit: €1,950 for 2025 and 2026 (€3,900 if both spouses are blind). Also the €825 guide dog allowance.",
              "Blind Person's Tax Credit", "If you or your spouse are blind or severely visually impaired, claim €1,950 a year – back four years.",
              [f"<strong>{eur(C['blind']['2026'])}</strong> for 2025 and 2026 (€1,650 for 2022–2024).", "<strong>€3,900</strong> if both spouses or civil partners are blind.",
               "Plus an €825 allowance for a trained guide dog.", "Needs confirmation from an ophthalmologist with your first claim."], "", ("blind", "charts"), [], None, None))
    G.append(("guide-dog-allowance.html", "Guide Dog and Assistance Dog Tax Allowance – €825", "Claim an €825 allowance (worth €165) for a guide dog or ADEu-accredited assistance dog, including autism assistance dogs.",
              "Guide and assistance dog allowance", "If you need a guide dog or assistance dog, you can claim an €825 allowance every year.",
              ["<strong>€825</strong> a year at 20% – worth <strong>€165</strong>.", "Assistance dogs (including autism assistance dogs) from an Assistance Dogs Europe accredited organisation qualify.",
               "Send the supplier's letter with your first claim."], "", ("dogs",), [], None, None))
    G.append(("mortgage-interest-tax-credit.html", "Mortgage Interest Tax Credit – Up to €1,250 for 2023–2025, €625 for 2026",
              "Mortgage Interest Tax Credit: 20% of the increase in interest since 2022, up to €1,250 a year for 2023–2025 and €625 for 2026. Mortgage €80,000–€500,000 at end of 2022.",
              "Mortgage Interest Tax Credit", "If your mortgage interest went up after 2022, you can claim part of the increase back.",
              ["20% of the <strong>increase</strong> in interest paid compared with 2022.", "Up to <strong>€1,250</strong> a year for 2023, 2024 and 2025.", "For 2026: 50% of the increase, capped at €3,125 – worth up to <strong>€625</strong>.",
               "Your mortgage balance must have been between <strong>€80,000 and €500,000</strong> on 31 December 2022, on your main home.", "Your Local Property Tax must be up to date.",
               "Your lender confirms the interest figures – you enter them in myAccount."],
              '<p>Buying or switching? <a href="../mortgage/" data-track="cross_app" data-label="mortgage_from_refund">Mortgage calculator →</a></p>', ("mortgage", "charts"), [], None, None))
    G.append(("landlord-rental-income-relief.html", "Landlord Tax Relief Ireland – Residential Premises Rental Income Relief (€1,000)",
              "Residential Premises Rental Income Relief for landlords: up to €600 (2024), €800 (2025) and €1,000 (2026 and 2027), capped at 20% of rental profit.",
              "Landlords: Residential Premises Rental Income Relief", "Individual landlords renting out homes long-term get up to €1,000 a year off their tax bill.",
              ["Up to <strong>€600</strong> for 2024, <strong>€800</strong> for 2025 and <strong>€1,000</strong> for 2026 and 2027.", "Capped at 20% of your rental profit.", "Only one relief per year however many properties you have.",
               "The tenancy must be registered with the RTB; clawback applies if you stop renting within 4 years.", "Not refundable on its own – it reduces Income Tax on your rental income."],
              '<p>Rent increase rules: <a href="../rent/" data-track="cross_app" data-label="rent_from_refund">Rent checker →</a></p>', ("rprir",), [], None, None))
    G.append(("rent-a-room-relief.html", "Rent-a-Room Relief 2026 – €14,000 Tax-Free (€16,000 in 2027)",
              "Rent a room in your home and earn up to €14,000 a year tax-free (Income Tax, USC and PRSI). Rising to €16,000 from 2027. Rules and what doesn't count.",
              "Rent-a-Room Relief", "Letting a room in your own home? Up to €14,000 a year is tax-free – rising to €16,000 in 2027.",
              ["Up to <strong>€14,000</strong> a year is free of Income Tax, USC and PRSI.", "<strong>Budget 2027:</strong> rises to <strong>€16,000</strong> from 1 January 2027.",
               "Go over the limit and the <strong>whole amount</strong> is taxed.", "It must be your home (owned or rented with permission) and lets of more than 28 days.",
               "Doesn't apply to rent from your own child, your employer, or short-term guests (Airbnb-type).", "You must still declare it on a tax return."], "", ("rentaroom", "budget_h"), [], None, None))
    G.append(("solar-microgeneration-tax.html", "Solar Panel Export Tax Ireland – €400 Tax-Free (€600 from Budget 2027)",
              "Money from selling solar electricity back to the grid is tax-free up to €400 a year (2024–2026), rising to €600 under Budget 2027. Income Tax, USC and PRSI.",
              "Tax on solar panel export payments", "Getting paid for the electricity your solar panels export? Most households pay no tax on it.",
              ["Up to <strong>€400 a year</strong> of profit from exporting electricity is free of Income Tax, USC and PRSI (2024 onwards).", "<strong>Budget 2027</strong> increases this to <strong>€600</strong>.",
               "Applies to electricity generated at your <strong>home</strong> from renewable sources, such as solar panels.", "If you're under the limit and have no other reason to file, you don't need a tax return for it.",
               "Over the limit? Declare the excess on your tax return."], '<p>Thinking of solar? Ask about SEAI grants – and see how much your bills fall.</p>', ("microgen", "budget"), [], None, None))
    G.append(("pension-tax-relief.html", "Pension Tax Relief Ireland – Age Limits 15% to 40%", "Tax relief on pension contributions at your highest rate, up to 15% of earnings under 30 rising to 40% at 60+, on earnings up to €115,000. AVCs and PRSAs.",
              "Pension tax relief", "Paying into a pension or AVC gets you relief at your highest rate of tax.",
              ["Relief at your <strong>marginal rate</strong> (20% or 40%).", "Limits by age: under 30: 15% · 30–39: 20% · 40–49: 25% · 50–54: 30% · 55–59: 35% · 60+: 40% of earnings.", "Earnings are capped at <strong>€115,000</strong>.",
               "Paid an AVC or PRSA yourself (not through payroll)? Claim the relief on your tax return.", "Auto-enrolment (MyFutureFund) has no tax relief – the State adds a top-up instead."],
              '<p><a href="../auto-enrolment/vs-workplace-pension.html">MyFutureFund vs a workplace pension →</a></p>', ("pension",), [], None, None))
    G.append(("cycle-to-work.html", "Cycle to Work Scheme Ireland – €1,250, €1,500 E-bike, €3,000 Cargo", "Cycle to Work Scheme limits: €1,250 for a bike, €1,500 for an e-bike and €3,000 for a cargo bike, tax-free through your employer.",
              "Cycle to Work Scheme", "Your employer can buy you a bike tax-free and you pay it back from your gross pay.",
              ["Limits: <strong>€1,250</strong> for a bike, <strong>€1,500</strong> for an e-bike, <strong>€3,000</strong> for a cargo bike – including safety gear.", "You save Income Tax, USC and PRSI on the cost.",
               "Your employer must buy it – if you buy it and get reimbursed, the exemption doesn't apply.", "New bikes only; employers don't have to take part.", "Budget 2027 announced a review of the scheme."], "", ("cycle", "budget"), [], None, None))
    G.append(("small-benefit-exemption.html", "Small Benefit Exemption 2026 – Up to €1,500 in Vouchers Tax-Free", "Employers can give up to five non-cash benefits (like vouchers) worth up to €1,500 a year in total, tax-free. What counts.",
              "Small Benefit Exemption", "A Christmas voucher from work can be tax-free – up to €1,500 a year.",
              ["Up to <strong>five</strong> non-cash benefits a year worth up to <strong>€1,500</strong> in total (from 2025).", "Vouchers can't be exchanged for cash.", "Cash bonuses are always taxed.",
               "Employers report these to Revenue – you can see them under 'Expenses/Benefits' in myAccount."], "", ("benefits",), [], None, None))
    G.append(("emergency-tax-refund.html", "Emergency Tax Refund Ireland – How to Get It Back", "On emergency tax? How to get off it and get the overpaid tax and USC back – from your employer, Revenue, or with a tax return for a past year.",
              "Getting an emergency tax refund", "Emergency tax takes far more than you owe. Here's how to get it all back.",
              ["Emergency tax applies when your employer doesn't have a Revenue Payroll Notification for you – usually a new job or no PPS number given.",
               "Fix it: register the job in myAccount and give your employer your PPS number.", "Once your employer gets a <strong>cumulative</strong> notification, the overpaid tax and USC is refunded in your next pay.",
               "Left the job? Claim directly from Revenue.", "<strong>Past years:</strong> file an Income Tax Return for that year and Revenue refunds what's due."],
              '<p>See what you should take home: <a href="../salary/" data-track="cross_app" data-label="salary_from_refund">take-home pay calculator →</a></p>', ("emergency", "return"), [], None, None))
    G.append(("unemployed-tax-refund.html", "Tax Refund When Unemployed Ireland – Claim Tax and USC Back", "Lost your job? Claim a tax and USC refund from Revenue 4 weeks after becoming unemployed (8 weeks on Jobseeker's Benefit), or immediately if on emergency tax.",
              "Tax refund if you're unemployed", "If you stop working part-way through the year, you've probably paid too much tax.",
              ["Claim in myAccount: <strong>Claim unemployment repayment</strong>.", "<strong>4 weeks</strong> after becoming unemployed if you have no other taxable income.", "<strong>8 weeks</strong> after if you get Jobseeker's Benefit (it's taxable).",
               "<strong>Immediately</strong> if you were on emergency tax or are leaving Ireland for good.", "Jobseeker's Benefit counts when the refund is worked out."],
              '<p><a href="../welfare/jobseekers-benefit.html">Jobseeker\'s Benefit rates →</a> · <a href="../welfare/jobseekers-pay-related-benefit.html">Pay-Related Benefit →</a></p>', ("unemployed",), [], None, None))
    G.append(("health-insurance-tax-relief.html", "Health Insurance Tax Relief 2026 – €200 Adult, €100 Child", "Health insurance tax relief is given at source: 20% on up to €1,000 per adult (€200) and €500 per child (€100) from 2026.",
              "Health insurance tax relief", "Relief on health insurance is taken off your premium automatically – but your claims are different.",
              ["Relief at source: 20% of up to <strong>€1,000</strong> per adult (€200) and <strong>€500</strong> per child (€100).", "If your employer pays your premium, you may need to claim it yourself.",
               "Claim the medical bills your insurer didn't cover as <a href='medical-expenses.html'>health expenses</a>."], "", ("insurance",), [], None, None))
    G.append(("social-welfare-tax.html", "Is My Social Welfare Payment Taxable? Ireland – Full List", "Which social welfare payments are taxed: Illness Benefit, Jobseeker's Benefit, Maternity Benefit, State Pension, Carer's Allowance – and which are tax-free.",
              "Tax on social welfare payments", "Some welfare payments are taxed, and they can create a refund or a bill at the end of the year.",
              ["Taxable payments are subject to Income Tax only – <strong>not USC or PRSI</strong>.", "If the payment is your only income, your tax credits usually cover it.",
               "With a job as well, Revenue reduces your credits to collect the tax – check your end-of-year Statement of Liability.",
               "Jobseeker's Benefit: the first €13 a week is tax-free.", "Child Benefit, Jobseeker's Allowance, Disability Allowance, Fuel Allowance, Working Family Payment and Back to School allowance are <strong>tax-free</strong>."],
              '<div class="two"><div class="card"><div class="tl">Taxable</div>' + lis(['<a href="../welfare/illness-benefit.html">Illness Benefit</a>', '<a href="../welfare/jobseekers-benefit.html">Jobseeker\'s Benefit</a>', '<a href="../welfare/maternity-benefit.html">Maternity Benefit</a>',
              '<a href="../welfare/paternity-benefit.html">Paternity Benefit</a>', '<a href="../welfare/parents-benefit.html">Parent\'s Benefit</a>', '<a href="../welfare/carers-allowance.html">Carer\'s Allowance</a>',
              '<a href="../welfare/invalidity-pension.html">Invalidity Pension</a>', '<a href="../welfare/one-parent-family-payment.html">One-Parent Family Payment</a>', '<a href="../welfare/state-pension-contributory.html">State Pension</a>']) +
              '</div><div class="card"><div class="tl">Tax-free</div>' + lis(['<a href="../welfare/child-benefit.html">Child Benefit</a>', '<a href="../welfare/jobseekers-allowance.html">Jobseeker\'s Allowance</a>', '<a href="../welfare/disability-allowance.html">Disability Allowance</a>',
              '<a href="../welfare/fuel-allowance.html">Fuel Allowance</a>', '<a href="../welfare/working-family-payment.html">Working Family Payment</a>', '<a href="../welfare/domiciliary-care-allowance.html">Domiciliary Care Allowance</a>',
              '<a href="../welfare/back-to-school-allowance.html">Back to School allowance</a>', '<a href="../welfare/farm-assist.html">Farm Assist</a>']) + "</div></div>",
              ("dsp", "dsp_exempt", "dsp_taxed"), [("Is Illness Benefit taxable?", "Yes – it's subject to Income Tax (not USC or PRSI). Any child dependant part is exempt."), ("Is Child Benefit taxable?", "No – Child Benefit is tax-free.")], None, None))
    app._guides = G
    for (fn, title, desc, h1, lead, facts, extra, srcs, faqs, howx, active) in G:
        body = f"""<p class="lead">{lead}</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts(facts)}
{DEADLINE_BOX if fn not in ('solar-microgeneration-tax.html', 'cycle-to-work.html', 'small-benefit-exemption.html', 'rent-a-room-relief.html', 'health-insurance-tax-relief.html') else ''}
{extra}
<div class="ad" data-slot="content"></div>
{how_to(howx) if fn not in ('cycle-to-work.html', 'small-benefit-exemption.html', 'social-welfare-tax.html', 'health-insurance-tax-relief.html', 'unemployed-tax-refund.html') else ''}
{faq_html(faqs) if faqs else ''}
{CTA}"""
        app.page(fn, title, desc, body, active=active, jsonld=[faq_ld(faqs)] if faqs else [], crumbs=[("Tax refunds", "./"), ("All reliefs", "all-reliefs.html"), (h1, None)], h1=h1,
                 sources=srcs, cross=CROSS, priority="0.8")

# ---------- Can I claim...? ----------
CLAIMS = [  # slug, item, yes/no/maybe, answer, related page
    ("gp-visits", "GP visits", "yes", "GP fees you paid yourself qualify for 20% relief.", "medical-expenses.html"),
    ("consultant-fees", "consultant fees", "yes", "Consultant fees qualify for 20% relief – minus anything your health insurer paid back.", "medical-expenses.html"),
    ("prescriptions", "prescriptions", "yes", "Drugs and medicines prescribed by a doctor qualify, including what you pay under the Drugs Payment Scheme.", "medical-expenses.html"),
    ("physiotherapy", "physiotherapy", "yes", "Physio qualifies if a practitioner referred or advised you to have it. Same for chiropractors, osteopaths and bone setters.", "medical-expenses.html"),
    ("chiropractor", "a chiropractor", "yes", "Yes, if a doctor referred or advised it – it's treated like physiotherapy.", "medical-expenses.html"),
    ("counselling", "counselling or psychotherapy", "maybe", "Yes if the psychologist or psychotherapist is a registered practitioner, or you were referred by one for a diagnostic procedure.", "medical-expenses.html"),
    ("ivf", "IVF", "yes", "IVF is a qualifying health expense – 20% back on what you paid.", "medical-expenses.html"),
    ("maternity-care", "maternity care", "yes", "Routine and maternity care during pregnancy qualifies.", "medical-expenses.html"),
    ("scans-and-tests", "scans and blood tests", "yes", "Diagnostic procedures recommended by a practitioner qualify.", "medical-expenses.html"),
    ("braces", "braces (orthodontics)", "yes", "Orthodontic treatment is non-routine dental – 20% back. Ask for a Med 2.", "non-routine-dental.html"),
    ("crowns", "crowns", "yes", "Crowns are non-routine dental care and qualify.", "non-routine-dental.html"),
    ("root-canal", "a root canal", "yes", "Root canal treatment (endodontics) qualifies as non-routine dental.", "non-routine-dental.html"),
    ("dental-implants", "dental implants", "yes", "Implants, including bone grafting, qualify as non-routine dental.", "non-routine-dental.html"),
    ("wisdom-teeth", "wisdom teeth removal", "maybe", "Only surgical extraction of impacted wisdom teeth qualifies. A normal extraction doesn't.", "non-routine-dental.html"),
    ("veneers", "veneers", "yes", "Veneers are listed by Revenue as non-routine dental care.", "non-routine-dental.html"),
    ("fillings", "fillings", "no", "Fillings are routine dental care and don't qualify.", "non-routine-dental.html"),
    ("dental-cleaning", "scale and polish", "no", "Scaling and cleaning are routine dental care and don't qualify.", "non-routine-dental.html"),
    ("dentures", "dentures", "no", "Providing or repairing dentures is routine dental care and doesn't qualify.", "non-routine-dental.html"),
    ("glasses", "glasses or contact lenses", "no", "Routine eye care, including eye tests and glasses, doesn't qualify.", "medical-expenses.html"),
    ("eye-test", "an eye test", "no", "Routine eye tests don't qualify.", "medical-expenses.html"),
    ("laser-eye-surgery", "laser eye surgery", "maybe", "It isn't on Revenue's excluded list as routine care, but cosmetic procedures are excluded. Check with Revenue before claiming.", "medical-expenses.html"),
    ("hearing-aids", "hearing aids", "yes", "Hearing aids are medical appliances and qualify (conditions apply).", "medical-expenses.html"),
    ("gluten-free-food", "gluten-free food", "yes", "Coeliacs can claim gluten-free food with a doctor's letter.", "coeliac-gluten-free-tax-relief.html"),
    ("diabetic-products", "diabetic products", "yes", "Diabetic products recommended by your doctor qualify, with a doctor's letter.", "diabetic-tax-relief.html"),
    ("speech-therapy", "speech and language therapy", "yes", "For a child, by a qualified speech and language therapist.", "child-health-expenses.html"),
    ("educational-psychologist", "an educational psychologist assessment", "yes", "Assessments for a child by an educational psychologist qualify.", "child-health-expenses.html"),
    ("podiatry", "podiatry or chiropody", "yes", "Qualifies if advised by a practitioner.", "medical-expenses.html"),
    ("acupuncture", "acupuncture", "maybe", "Only when it's provided by a registered practitioner (such as a doctor).", "medical-expenses.html"),
    ("ambulance", "an ambulance", "yes", "Transport by ambulance qualifies.", "medical-expenses.html"),
    ("nursing-home", "nursing home fees", "yes", "Yes, at your highest rate of tax, if the home has 24-hour nursing care.", "nursing-home-fees.html"),
    ("treatment-abroad", "treatment abroad", "yes", "Yes, if the practitioner is registered in that country. Travel and accommodation also count if the treatment isn't available here.", "medical-expenses.html"),
    ("botox", "Botox or cosmetic surgery", "no", "Cosmetic procedures are excluded, unless the surgery corrects a health problem.", "medical-expenses.html"),
    ("pharmacy-consultation", "a pharmacy consultation", "yes", "Consultations and medicines under the Common Conditions Service at participating pharmacies qualify.", "medical-expenses.html"),
    ("health-insurance", "health insurance premiums", "no", "Not as a health expense – relief is already given at source on the premium.", "health-insurance-tax-relief.html"),
    ("gym-membership", "gym membership", "no", "Gym membership isn't a health expense, even if recommended.", "medical-expenses.html"),
]
ANS = {"yes": ("✅ Yes", "good"), "no": ("❌ No", "bad"), "maybe": ("⚠️ Sometimes", "neutral")}
def build_claims():
    rows = []
    for slug, item, yn, ans, rel in CLAIMS:
        lab, cls = ANS[yn]
        rows.append([f'<a href="can-i-claim-{slug}.html">{item[0].upper() + item[1:]}</a>', lab])
        others = [c for c in CLAIMS if c[0] != slug and c[4] == rel][:8]
        ex = "" if yn == "no" else f"<p>Example: €1,000 spent on {item} = <strong>€200 back</strong> – or <strong>€800</strong> if you claim the same each year for four years.</p>"
        body = f"""<div class="verdict {cls}"><h2>{lab}</h2><p>{ans}</p></div>
{ex}
<div class="ad" data-slot="content"></div>
<h2>The rules</h2>
{lis(["Relief is 20% of what you paid that wasn't refunded by insurance, the HSE or compensation.", "The care must be given or advised by a registered practitioner.", "Keep receipts for six years – you don't send them unless asked.", "You can claim back four years: 2022 closes on 31 December 2026."])}
{how_to(None)}
<h2>Can I also claim…</h2><div class="chip-list">{"".join(f'<a href="can-i-claim-{c[0]}.html">{c[1]}</a>' for c in others)}<a href="can-i-claim.html">Full list →</a></div>
{CTA}"""
        title = f"Can I Claim Tax Back on {item[0].upper() + item[1:]}? Ireland – {lab[2:]}"
        app.page(f"can-i-claim-{slug}.html", title, f"Can you claim tax relief on {item} in Ireland? {ans} How much you get back and how to claim through myAccount.",
                 body, active="Medical", jsonld=[faq_ld([(f"Can I claim tax back on {item} in Ireland?", ans)])], crumbs=[("Tax refunds", "./"), ("Can I claim…?", "can-i-claim.html"), (item, None)],
                 h1=f"Can I claim tax back on {item}?", sources=("health_q", "dental", "health_claim"), cross=CROSS, priority="0.6")
    body = f"""<p class="lead">Quick answers: which health costs can you claim 20% back on?</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{table(["Treatment or cost", "Can you claim?"], rows)}
<div class="ad" data-slot="content"></div>{CTA}"""
    app.page("can-i-claim.html", "Can I Claim Tax Back On…? Medical & Dental Expenses A–Z Ireland",
             "Can you claim tax relief on braces, physio, IVF, glasses, counselling, gluten-free food, fillings or GP visits? Quick yes/no answers from Revenue's rules.",
             body, active="Medical", crumbs=[("Tax refunds", "./"), ("Can I claim…?", None)], h1="Can I claim tax back on…?", sources=("health_q", "dental"), cross=CROSS, priority="0.8")

# ---------- Flat-rate expenses by job ----------
def load_jobs():
    rows = list(csv.reader(open(os.path.join(HERE, "data", "flat-rate-expenses.csv"), encoding="utf-8-sig")))[1:]
    jobs = {}
    for r in rows:
        if not r or not r[0].strip(): continue
        head = re.sub(r"\s+", " ", r[0]).strip().rstrip(":").strip()
        sub = re.sub(r"\s+", " ", r[1]).strip()
        vals = {}
        for i, y in enumerate((2026, 2025, 2024, 2023, 2022, 2021)):
            v = r[2 + i].strip().replace(",", "")
            vals[y] = int(float(v)) if re.match(r"^\d+(\.\d+)?$", v) else None
        jobs.setdefault(head, []).append({"sub": sub, "vals": vals, "note": r[8].strip() if len(r) > 8 else ""})
    return jobs

def job_slug(h):
    s = h.lower()
    s = re.sub(r"\(.*?\)", "", s).replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:50].strip("-")

def build_jobs():
    jobs = load_jobs()
    index_rows, js = [], []
    for head, subs in sorted(jobs.items()):
        slug = job_slug(head)
        best = max((s["vals"][2026] or 0) for s in subs)
        four = sum(max((s["vals"][y] or 0) for s in subs) for y in (2022, 2023, 2024, 2025))
        index_rows.append([f'<a href="flat-rate-expenses-{slug}.html">{head}</a>', eur(best) if best else "–"])
        for s in subs:
            if s["vals"][2026]: js.append([head + (" – " + s["sub"] if s["sub"] else ""), s["vals"][2026], f"flat-rate-expenses-{slug}.html"])
        rows = [[s["sub"] or head] + [eur(s["vals"][y]) if s["vals"][y] else "–" for y in (2026, 2025, 2024, 2023, 2022)] for s in subs]
        facts = [f"<strong>{head}</strong> can claim a flat-rate expense of up to <strong>{eur(best)} a year</strong> (2026) for the cost of tools, uniforms, fees or similar." if best else f"Flat-rate expense amounts for {head}.",
                 f"That's worth <strong>{eur(best * 0.2)}</strong> a year at 20% tax, or <strong>{eur(best * 0.4)}</strong> at 40%." if best else "",
                 f"Never claimed? For 2022–2025 you could get back up to <strong>{eur(four * 0.2)}</strong> (20%) or <strong>{eur(four * 0.4)}</strong> (40%), plus 2026." if four else "",
                 "You must claim it <strong>every year</strong> – it isn't automatic.", "2022 claims close on <strong>31 December 2026</strong>."]
        notes = [s["note"] for s in subs if s["note"]]
        body = f"""<p class="lead">Flat-rate expenses for {head.lower() if not head[:3].isupper() else head}: how much you can claim each year and how much tax that gives back.</p>
<p class="updated">Revenue flat rate expense list · Checked {CHECKED}</p>
{key_facts([f for f in facts if f])}
{table(["Category", "2026", "2025", "2024", "2023", "2022"], rows)}
{('<p class="muted small">' + " ".join(notes) + '</p>') if notes else ''}
<div class="ad" data-slot="content"></div>
{how_to("Choose 'Your job – Flat Rate Expenses' and pick your job from the list.")}
<p>Also check: <a href="remote-working-relief.html">working from home</a> · <a href="medical-expenses.html">medical expenses</a> · <a href="rent-tax-credit.html">Rent Tax Credit</a> · <a href="../salary/" data-track="cross_app" data-label="salary_from_refund">your take-home pay</a></p>
{CTA}"""
        app.page(f"flat-rate-expenses-{slug}.html", f"Flat Rate Expenses for {head[:60]} – {eur(best)} a Year | Ireland" if best else f"Flat Rate Expenses for {head[:60]} | Ireland",
                 f"Flat-rate expenses for {head}: {eur(best)} a year in 2026, worth up to {eur(best * 0.4)} back. Amounts for 2022–2026 and how to claim back four years in myAccount." if best else f"Flat-rate expense amounts for {head}, 2022–2026.",
                 body, active="Your job", jsonld=[faq_ld([(f"How much are flat rate expenses for {head}?", f"{eur(best)} a year for 2026 (worth {eur(best * 0.2)} at 20% or {eur(best * 0.4)} at 40%). You must claim it each year.")])] if best else [],
                 crumbs=[("Tax refunds", "./"), ("Flat-rate expenses", "flat-rate-expenses.html"), (head[:40], None)], h1=f"Flat-rate expenses: {head}", sources=("fre", "fre_csv", "fre_claim"), cross=CROSS, priority="0.6")
    body = f"""<p class="lead">Over 60 jobs get a flat-rate expense every year for tools, uniforms, registration fees and similar – without receipts. But you have to claim it.</p>
<p class="updated">Revenue flat rate expense list 2021–2026 · Checked {CHECKED}</p>
{key_facts(["A fixed yearly deduction agreed between Revenue and your trade or profession – no receipts needed.", "Relief is at your highest rate of tax (20% or 40%).",
            "Claim it in myAccount for each year – it doesn't happen automatically.", "Go back four years: 2022 claims close on 31 December 2026.", "Nurses, teachers, shop assistants, builders, hotel and bar staff, healthcare professionals and many more."])}
<input type="search" id="filter" class="filter-input" placeholder="Find your job (e.g. nurse, teacher, shop)" aria-label="Find your job">
{table(["Job", "Up to (2026)"], index_rows, "all")}
<div class="ad" data-slot="content"></div>
{how_to("Choose 'Your job – Flat Rate Expenses'.")}{CTA}"""
    app.page("flat-rate-expenses.html", "Flat Rate Expenses Ireland 2026 – Every Job & Amount (Nurses, Teachers, Shop Staff…)",
             "Flat rate expenses list for every job in Ireland: nurses, teachers, shop assistants, building trades, hotel staff and more – amounts for 2022–2026 and how to claim four years back.",
             body, active="Your job", crumbs=[("Tax refunds", "./"), ("Flat-rate expenses", None)], h1="Flat-rate expenses by job", sources=("fre", "fre_csv", "fre_claim"), cross=CROSS, priority="0.9",
             scripts=["js/filter.js"])
    with open(os.path.join(app.root, "js", "jobs.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// Flat-rate expenses by job (Revenue list, 2026 amounts) – generated by tools/build_taxrefund.py\nwindow.IEJOBS = " + json_dumps(js) + ";\n")

def json_dumps(x):
    import json
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))

# ---------- Rent amounts & remote working days ----------
RENTS = list(range(600, 2501, 100))
def build_rent_pages():
    for m in RENTS:
        res = q(*[{"k": "rent", "y": y, "r": m * 12, "c": c} for c in (False, True) for y in YEARS])
        single, couple = res[:5], res[5:]
        body = f"""<p class="lead">Paying €{m:,} a month in rent? Here's how much Rent Tax Credit you can claim for each year – and in total if you've never claimed.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts([f"€{m:,} a month is <strong>€{m * 12:,}</strong> a year. 20% of that is {eur(m * 12 * 0.2)}, so you get the <strong>{'full credit' if m * 12 * 0.2 >= C['rent']['2026'] else eur(m * 12 * 0.2)}</strong> each year (2024–2026).",
            f"Single: up to <strong>{eur(sum(single))}</strong> for 2022–2026 if you never claimed.", f"Jointly assessed couple: up to <strong>{eur(sum(couple))}</strong>.",
            f"From 2027 the maximum rises to {eur(C['rent']['2027'])} ({eur(C['rent']['2027'] * 2)} for couples).", "You can't get back more Income Tax than you paid in a year."])}
{table(["Year", "Single", "Couple"], [[str(y), eur(s), eur(c)] for y, s, c in zip(YEARS, single, couple)] + [["<strong>Total</strong>", f"<strong>{eur(sum(single))}</strong>", f"<strong>{eur(sum(couple))}</strong>"]])}
{DEADLINE_BOX}
<div class="ad" data-slot="content"></div>
{how_to("You'll need your landlord's details and RTB registration number.")}
<div class="chip-list">{"".join(f'<a href="rent-tax-credit-{x}.html">€{x:,}</a>' for x in RENTS if x != m and abs(x - m) <= 400)}<a href="rent-tax-credit.html">Rent Tax Credit guide</a></div>
<p>Is your landlord putting the rent up? <a href="../rent/" data-track="cross_app" data-label="rent_from_refund">Check the increase is legal →</a></p>{CTA}"""
        app.page(f"rent-tax-credit-{m}.html", f"Rent Tax Credit on €{m:,} a Month – Up to {eur(sum(single))} Back (2022–2026)",
                 f"Rent Tax Credit if you pay €{m:,} a month: {eur(single[-1])} a year single, {eur(couple[-1])} for a couple. Up to {eur(sum(single))} back for 2022–2026.",
                 body, active="Rent credit", crumbs=[("Tax refunds", "./"), ("Rent Tax Credit", "rent-tax-credit.html"), (f"€{m:,} a month", None)], h1=f"Rent Tax Credit on €{m:,} a month",
                 sources=("rent_amt", "charts"), cross=CROSS, priority="0.6")
    for d in range(1, 6):
        days = d * 46  # ~46 working weeks a year
        res = q(*[{"k": "wfh", "y": 2025, "b": b, "d": days, "rate": r} for b in (1800, 2400, 3000, 3600) for r in (0.2, 0.4)])
        rows = [[eur(b), eur(res[i * 2]["allowable"]), eur(res[i * 2]["refund"]), eur(res[i * 2 + 1]["refund"])] for i, b in enumerate((1800, 2400, 3000, 3600))]
        body = f"""<p class="lead">Working from home {d} day{"s" if d > 1 else ""} a week? Here's roughly how much Remote Working Relief you can claim.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts([f"{d} day{'s' if d > 1 else ''} a week is about <strong>{days} days</strong> a year (allowing for holidays and leave).", "You claim 30% of electricity, heating and broadband for that share of the year.",
            f"With €2,400 of bills: <strong>{eur(res[2]['refund'])}</strong> back a year at 20% tax, or <strong>{eur(res[3]['refund'])}</strong> at 40%.", "Claim each year back to 2022 – 2022 closes on 31 December 2026."])}
{table(["Yearly bills", "Allowable amount", "Back at 20%", "Back at 40%"], rows)}
<div class="ad" data-slot="content"></div>
{how_to("Upload your bills to the Receipts Tracker first.")}
<div class="chip-list">{"".join(f'<a href="remote-working-{x}-days.html">{x} day{"s" if x > 1 else ""} a week</a>' for x in range(1, 6) if x != d)}<a href="remote-working-relief.html">Full guide</a></div>{CTA}"""
        app.page(f"remote-working-{d}-days.html", f"Remote Working Relief for {d} Day{'s' if d > 1 else ''} a Week – How Much Back? Ireland",
                 f"Working from home {d} day{'s' if d > 1 else ''} a week: about {days} days a year. With €2,400 of bills you get {eur(res[2]['refund'])} back at 20% or {eur(res[3]['refund'])} at 40%.",
                 body, active="Work from home", crumbs=[("Tax refunds", "./"), ("Remote working", "remote-working-relief.html"), (f"{d} days a week", None)], h1=f"Remote working relief: {d} day{'s' if d > 1 else ''} a week",
                 sources=("wfh_calc", "wfh_costs"), cross=CROSS, priority="0.6")

# ---------- Hubs, deadline, years, budget, FAQ ----------
def build_hubs():
    groups = [("🏠 Home and rent", ["rent-tax-credit.html", "rent-tax-credit-students.html", "mortgage-interest-tax-credit.html", "landlord-rental-income-relief.html", "rent-a-room-relief.html", "solar-microgeneration-tax.html"]),
              ("🩺 Health", ["medical-expenses.html", "non-routine-dental.html", "coeliac-gluten-free-tax-relief.html", "diabetic-tax-relief.html", "nursing-home-fees.html", "home-care-tax-relief.html", "child-health-expenses.html", "kidney-patient-tax-relief.html", "health-insurance-tax-relief.html"]),
              ("💼 Work", ["remote-working-relief.html", "flat-rate-expenses.html", "emergency-tax-refund.html", "unemployed-tax-refund.html", "pension-tax-relief.html", "cycle-to-work.html", "small-benefit-exemption.html", "social-welfare-tax.html"]),
              ("👪 Family, education and age", ["home-carer-tax-credit.html", "single-person-child-carer-credit.html", "incapacitated-child-tax-credit.html", "dependent-relative-tax-credit.html", "tuition-fees.html", "foreign-language-it-courses.html", "age-tax-credit.html", "over-65-tax-exemption.html", "blind-tax-credit.html", "guide-dog-allowance.html"])]
    G = {g[0]: g for g in app._guides}
    G["flat-rate-expenses.html"] = ("flat-rate-expenses.html", "", "Fixed yearly allowances for tools, uniforms and fees for over 60 jobs – nurses, teachers, shop staff, builders, hotel staff and more.", "Flat-rate expenses by job")
    html = "".join(f"<h2>{t}</h2>" + '<ul class="course-list">' + "".join(f'<li><span><a href="{f}">{G[f][3]}</a><small>{G[f][2][:150]}</small></span></li>' for f in fs) + "</ul>" for t, fs in groups)
    body = f"""<p class="lead">Every tax credit, relief and exemption a PAYE worker in Ireland might be missing – in plain English, with Revenue's rules.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>{DEADLINE_BOX}{html}<div class="ad" data-slot="content"></div>{CTA}"""
    app.page("all-reliefs.html", "Every Tax Credit and Relief in Ireland 2026 – Full List for PAYE Workers",
             "The full list of Irish tax credits and reliefs: rent, medical, dental, remote working, flat-rate expenses, home carer, single parent, tuition fees, nursing home, landlords, solar and more.",
             body, active="All reliefs", crumbs=[("Tax refunds", "./"), ("All reliefs", None)], h1="Every tax credit and relief", sources=("charts", "ci"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">The four-year rule means anything you're owed for 2022 must be claimed by <strong>31 December 2026</strong>. After that it's gone.</p>
<p class="updated">Revenue four-year rule · Checked {CHECKED}</p>
{key_facts(["You can claim refunds for the <strong>last four years</strong> only.", "Claims for <strong>2022</strong> must be made by <strong>31 December 2026</strong>.", "Claims for 2023 close on 31 December 2027, and so on.",
            "Completing a 2022 Income Tax Return in myAccount takes about 15 minutes – refunds usually arrive in about five working days."])}
<h2>What you can still claim for 2022</h2>
{table(["Credit or relief", "2022 amount"], [["Rent Tax Credit", f"up to {eur(C['rent']['2022'])} ({eur(C['rent']['2022'] * 2)} couple)"], ["Medical expenses", "20% of what you paid"], ["Remote working relief", "30% of bills for days at home"],
    ["Flat-rate expenses", "depends on your job"], ["Home Carer Tax Credit", f"up to {eur(C['homeCarer']['2022'])}"], ["Single Person Child Carer Credit", eur(C['spccc']['2022'])], ["Incapacitated Child Tax Credit", eur(C['incapChild']['2022'])],
    ["Tuition fees", "20% above €3,000"], ["Dependent Relative", eur(C['dependent']['2022'])], ["Emergency tax overpaid", "whatever was overpaid"]])}
<div class="ad" data-slot="content"></div>
{how_to("Pick 2022 when you request the Statement of Liability.", now=False)}{CTA}"""
    app.page("deadline-2022.html", "Claim Your 2022 Tax Refund Before 31 December 2026 – Four-Year Rule Ireland",
             "Deadline: tax refunds for 2022 must be claimed by 31 December 2026 under Revenue's four-year rule. What you can claim for 2022 – rent, medical, remote working – and how.",
             body, active="31 Dec deadline", crumbs=[("Tax refunds", "./"), ("2022 deadline", None)], h1="Claim 2022 before 31 December 2026", sources=("four", "return", "charts"), cross=CROSS, priority="0.9",
             share_text="Reminder: any tax refund for 2022 must be claimed by 31 December 2026 or it's gone. Check what you're owed:")

    body = f"""<p class="lead">Step-by-step: how to claim a tax refund in Revenue's myAccount, for this year and the last four.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts(["You need a <strong>myAccount</strong> login (PPS number, date of birth, and a verified email and phone).", "Past years: request a <strong>Statement of Liability</strong>, then complete an <strong>Income Tax Return</strong> and add credits.",
            "This year: <strong>Manage your tax for the current year</strong> – claims update your tax credits straight away.", "Keep receipts for six years. Use the Receipts Tracker in myAccount.", "Most refunds arrive in about <strong>five working days</strong>."])}
{how_to()}
<div class="ad" data-slot="content"></div>
<h2>Tips</h2>{lis(["Do one return per year – start with 2022 before 31 December.", "A Statement of Liability on its own also shows any refund from overpaid tax or emergency tax.", "Married or civil partners: the assessable spouse usually files the joint return.",
    "Never pay a 'tax refund agent' a share of your refund for something you can do yourself in 15 minutes."])}{CTA}"""
    app.page("how-to-claim.html", "How to Claim a Tax Refund in myAccount – Step by Step (Ireland)",
             "How to claim tax back in Revenue myAccount: request a Statement of Liability, complete your Income Tax Return and add credits for the last four years – or claim in real time for 2026.",
             body, crumbs=[("Tax refunds", "./"), ("How to claim", None)], h1="How to claim a tax refund in myAccount", sources=("return", "health_claim", "myaccount"), cross=CROSS, priority="0.9")

    keys = [("Personal (single)", "personal", 1), ("Personal (married)", "personal", 2), ("Employee (PAYE)", "employee", 1), ("Rent (single)", "rent", 1), ("Rent (couple)", "rent", 2), ("Home Carer", "homeCarer", 1),
            ("Single Person Child Carer", "spccc", 1), ("Incapacitated Child", "incapChild", 1), ("Dependent Relative", "dependent", 1), ("Blind Person", "blind", 1), ("Age (single)", "age", 1)]
    rows = [[n] + [eur(C[k][str(y)] * m) if str(y) in C[k] else "–" for y in (2022, 2023, 2024, 2025, 2026, 2027)] for n, k, m in keys]
    rows.append(["20% band (single)"] + [eur(M["BAND"][str(y)]) for y in (2022, 2023, 2024, 2025, 2026, 2027)])
    body = f"""<p class="lead">Irish tax credits for every year you can still claim, plus 2027 from Budget 2027.</p>
<p class="updated">Revenue charts · Budget 2027 · Checked {CHECKED}</p>
{table(["Credit", "2022", "2023", "2024", "2025", "2026", "2027"], rows)}
<p class="muted small">2027 figures are from Budget 2027 (6 October 2026) and become law with the Finance Act. – means not yet announced or not available.</p>
<div class="ad" data-slot="content"></div>{CTA}"""
    app.page("tax-credits-by-year.html", "Tax Credits Ireland 2022 to 2027 – Every Year in One Table",
             "Irish tax credits for 2022, 2023, 2024, 2025, 2026 and 2027: personal, employee, rent, home carer, single person child carer, incapacitated child, dependent relative, blind and age.",
             body, crumbs=[("Tax refunds", "./"), ("Tax credits by year", None)], h1="Tax credits 2022–2027", sources=("charts", "budget", "budget_h"), cross=CROSS, priority="0.8")

    body = f"""<p class="lead">What Budget 2027 changes for your tax from 1 January 2027.</p>
<p class="updated">Budget 2027 (6 October 2026) · Checked {CHECKED}</p>
{key_facts([f"Personal, employee and earned income credits up €125 to <strong>{eur(C['personal']['2027'])}</strong>.", f"Standard rate band up €2,500 to <strong>{eur(M['BAND']['2027'])}</strong> (single).",
            f"Rent Tax Credit up to <strong>{eur(C['rent']['2027'])}</strong> ({eur(C['rent']['2027'] * 2)} for couples) for 2027 and 2028.", f"Home Carer Tax Credit up to <strong>{eur(C['homeCarer']['2027'])}</strong>.",
            "Rent-a-Room limit up to <strong>€16,000</strong>.", "Solar export (microgeneration) exemption up from €400 to <strong>€600</strong>.", "USC 2% band extended to €30,300.",
            "Help to Buy maximum up to €35,000 (from 7 October 2026)."])}
<p>See your new take-home pay: <a href="../salary/" data-track="cross_app" data-label="salary_from_refund">Budget 2027 pay calculator →</a> · Welfare: <a href="../welfare/budget-2027.html">Budget 2027 welfare changes →</a></p>
<div class="ad" data-slot="content"></div>{CTA}"""
    app.page("budget-2027.html", "Budget 2027 Tax Changes Ireland – Credits, Rent Credit €1,150, Rent-a-Room €16,000",
             "Budget 2027 tax changes: tax credits up €125 to €2,125, 20% band €46,500, Rent Tax Credit €1,150, Home Carer €2,050, Rent-a-Room €16,000, solar export €600.",
             body, crumbs=[("Tax refunds", "./"), ("Budget 2027", None)], h1="Budget 2027 tax changes", sources=("budget", "budget_h", "charts"), cross=CROSS, priority="0.8")

    FAQ = [("How far back can I claim a tax refund in Ireland?", "Four years. Right now you can claim 2022–2025 (and 2026 in real time). 2022 closes on 31 December 2026."),
           ("How long does a Revenue tax refund take?", "Usually about five working days after you submit an Income Tax Return in myAccount."),
           ("Do I need to send receipts?", "No – keep them for six years in case Revenue asks. The Receipts Tracker in myAccount is the easiest place."),
           ("Can I claim the Rent Tax Credit and medical expenses together?", "Yes – you can claim every credit and relief you qualify for."),
           ("Can I get a refund if I didn't pay tax?", "No – credits and reliefs only give back Income Tax you actually paid."),
           ("Do I need an accountant or tax agent?", "No. Most PAYE claims take about 15 minutes in myAccount. Be wary of agents who take a percentage."),
           ("What if I was on emergency tax?", "Your employer refunds it once they get a cumulative notification, or you file a return for that year."),
           ("Is working from home relief 20%?", "No – you can claim 30% of electricity, heating and broadband for the days you worked from home, at your highest tax rate."),
           ("Can I claim for my partner's or child's medical bills?", "Yes – if you paid them."),
           ("Does this checker contact Revenue?", "No. It runs on your phone and nothing is sent anywhere.")]
    app.page("faq.html", "Tax Refund FAQ Ireland – How Far Back, How Long, Receipts, Emergency Tax",
             "Tax refund questions answered: how far back you can claim, how long refunds take, receipts, emergency tax, working from home and the 2022 deadline.",
             f'<p class="lead">Common tax refund questions, answered simply.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ) + CTA,
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Tax refunds", "./"), ("FAQ", None)], h1="Tax refund FAQ", sources=("four", "return", "health_claim"), cross=CROSS, priority="0.8")

if __name__ == "__main__":
    build_guides(); build_index(); build_claims(); build_jobs(); build_rent_pages(); build_hubs()
    og_image(os.path.join(app.root, "og.png"), "REVENUE REFUNDS", "Am I owed", "a tax refund?", "Rent · medical · work from home · your job", "2022 claims close 31 December 2026",
             "tavion.ie/tax-refund  ·  free, no sign-up", (94, 234, 212), (15, 118, 110), (5, 60, 55))
    app.update_sitemap()
    app.update_llms("- [Tax Refund Checker](https://tavion.ie/tax-refund/): which Irish tax credits and reliefs you can claim back for 2022-2026 (rent, medical, dental, remote working, flat-rate expenses by job, carers, tuition) with estimates.",
                    "Tax refunds: key facts",
                    f"""- Four-year rule: refunds can be claimed for the last four years; 2022 claims close 31 December 2026. Claim in Revenue myAccount (Review your tax for the previous 4 years > Statement of Liability > Income Tax Return).
- Rent Tax Credit: 20% of rent, max €500 (2022-2023), €1,000 (2024-2026), €1,150 (2027-2028 per Budget 2027); double for jointly assessed couples. Not for HAP/RAS/Rent Supplement. Parents can claim for a student child.
- Health expenses: 20% relief (nursing homes at marginal rate). Includes GP, consultant, prescriptions, physio (referred), IVF, non-routine dental (crowns, braces, root canal, implants; Med 2), gluten-free food for coeliacs and diabetic products (doctor's letter). Not routine dental, eye tests, glasses, cosmetic.
- Remote working relief: 30% of electricity, heating and broadband x days worked at home / days in year, minus employer €3.20/day allowance, at marginal rate.
- Flat-rate expenses: fixed yearly allowances for ~68 job categories (Revenue list); must be claimed each year.
- Other: Home Carer credit €1,950 (2026), €2,050 (2027); SPCCC €1,900; Incapacitated Child €3,800; Dependent Relative €305; Mortgage Interest credit up to €1,250 (2023-25) / €625 (2026); landlords RPRIR €1,000 (2026); Rent-a-Room €14,000 (€16,000 from 2027); microgeneration €400 (€600 per Budget 2027); tuition 20% above €3,000 disregard.
- Pages: [Checker](https://tavion.ie/tax-refund/), [All reliefs](https://tavion.ie/tax-refund/all-reliefs.html), [2022 deadline](https://tavion.ie/tax-refund/deadline-2022.html), [Flat-rate expenses by job](https://tavion.ie/tax-refund/flat-rate-expenses.html), [Can I claim…?](https://tavion.ie/tax-refund/can-i-claim.html). Source: revenue.ie.""")
    print("Built", len(app.files), "pages in", app.root)
