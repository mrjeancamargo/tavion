"""
Builds the Irish Social Welfare Rates app (tavion.ie/welfare/).
Run from the repo root:   python tools/build_welfare.py      (needs Node.js)
All rates come from welfare/js/welfare.js – the same engine the calculator uses.
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, eur, lis, table, faq_ld, faq_html, key_facts, node, og_image, TODAY

ENGINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "welfare", "js", "welfare.js"))
CHECKED = "November 2026"
CI = "https://www.citizensinformation.ie"
SRC = {
    "dsp27": ("Department of Social Protection – Budget 2027 factsheet (rates from January 2027)", "https://www.inou.ie/assets/files/pdf/budget_factsheet_2027_-_department_of_social_protection.pdf"),
    "gov27": ("gov.ie – Department of Social Protection: Budget 2027", "https://www.gov.ie/en/department-of-social-protection/publications/budget-2027/"),
    "ci_rates27": ("Citizens Information – Social welfare rates 2027", CI + "/en/money-and-tax/budgets/social-welfare-rates-announced-in-budget-2027/"),
    "ci_rates26": ("Citizens Information – Social welfare rates 2026", CI + "/en/money-and-tax/budgets/social-welfare-rates-announced-in-budget-2026/"),
    "ci_xmas": ("Citizens Information – Christmas Bonus", CI + "/en/social-welfare/irish-social-welfare-system/christmas-bonus/"),
    "mywelfare": ("MyWelfare.ie – apply for payments online", "https://services.mywelfare.ie/"),
    "ci_bts": ("Citizens Information – Back to School Clothing and Footwear Allowance", CI + "/en/social-welfare/families-and-children/back-to-school-clothing-and-footwear-allowance/"),
    "ci_hbp": ("Citizens Information – Household Benefits Package", CI + "/en/social-welfare/extra-social-welfare-benefits/household-benefits-package/"),
    "ci_travel": ("Citizens Information – Free Travel", CI + "/en/social-welfare/extra-social-welfare-benefits/free-travel/"),
}
PAGE_SRC = {
    "state-pension-contributory": "/en/social-welfare/older-and-retired-people/state-pension-contributory/",
    "state-pension-non-contributory": "/en/social-welfare/older-and-retired-people/state-pension-non-contributory/",
    "jobseekers-allowance": "/en/social-welfare/unemployed-people/jobseekers-allowance/",
    "jobseekers-benefit": "/en/social-welfare/unemployed-people/jobseekers-benefit/",
    "jobseekers-pay-related-benefit": "/en/social-welfare/unemployed-people/jobseekers-pay-related-benefit/",
    "jobseekers-transitional-payment": "/en/social-welfare/unemployed-people/jobseekers-transitional-payment/",
    "illness-benefit": "/en/social-welfare/disability-and-illness/illness-benefit/",
    "invalidity-pension": "/en/social-welfare/disability-and-illness/invalidity-pension/",
    "disability-allowance": "/en/social-welfare/disability-and-illness/disability-allowance/",
    "blind-pension": "/en/social-welfare/disability-and-illness/blind-persons-pension/",
    "disablement-benefit": "/en/social-welfare/disability-and-illness/disablement-benefit/",
    "carers-allowance": "/en/social-welfare/carers/carers-allowance/",
    "carers-benefit": "/en/social-welfare/carers/carers-benefit/",
    "carers-support-grant": "/en/social-welfare/carers/carers-support-grant/",
    "domiciliary-care-allowance": "/en/social-welfare/disability-and-illness/domiciliary-care-allowance/",
    "one-parent-family-payment": "/en/social-welfare/families-and-children/one-parent-family-payment/",
    "working-family-payment": "/en/social-welfare/families-and-children/working-family-payment/",
    "child-benefit": "/en/social-welfare/families-and-children/child-benefit/",
    "maternity-benefit": "/en/social-welfare/families-and-children/maternity-benefit/",
    "paternity-benefit": "/en/social-welfare/families-and-children/paternity-benefit/",
    "parents-benefit": "/en/social-welfare/families-and-children/parents-benefit/",
    "adoptive-benefit": "/en/social-welfare/families-and-children/adoptive-benefit/",
    "supplementary-welfare-allowance": "/en/social-welfare/supplementary-welfare-schemes/supplementary-welfare-allowance-scheme/",
    "fuel-allowance": "/en/social-welfare/extra-social-welfare-benefits/fuel-allowance/",
    "living-alone-increase": "/en/social-welfare/extra-social-welfare-benefits/living-alone-allowance/",
}
for k, path in PAGE_SRC.items():
    SRC["ci_" + k] = ("Citizens Information – " + k.replace("-", " ").title().replace("S ", "s ").replace("Jobseekers", "Jobseeker's").replace("Carers", "Carer's").replace("Parents", "Parent's"), CI + path)

NODE = r"""
const W = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "w" ? W.weekly(x.key, x.o) : x.k === "jprb" ? W.jprb(x.a, x.y) : x.k === "wfp" ? W.wfp(x.n, x.i) : x.k === "cb" ? W.childBenefitDates(x.y) : null);
  process.stdout.write(JSON.stringify({ P: W.PAYMENTS, X: W.XMAS, J: W.JPRB, WFP: W.WFP, res: res }));
});
"""
META = node(ENGINE, NODE, [])
P = META["P"]
def run(q): return node(ENGINE, NODE, q)["res"]

TABS = [("./", "Calculator"), ("rates-2027.html", "Rates 2027"), ("christmas-bonus.html", "Christmas Bonus"), ("payment-dates.html", "Payment dates"),
        ("all-payments.html", "All payments"), ("budget-2027.html", "Budget 2027"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Welfare calculator</a><a href="rates-2027.html">Rates 2027</a><a href="christmas-bonus.html">Christmas Bonus 2026</a><a href="child-benefit-payment-dates.html">Child Benefit dates</a>'
        '<a href="payment-dates.html">Payment dates</a><a href="christmas-payment-dates.html">Christmas payment dates</a><a href="fuel-allowance-payment-dates.html">Fuel Allowance dates</a><a href="lump-sum-payments.html">Bonus &amp; lump sums</a><a href="cost-of-disability-payment.html">€500 disability payment</a><a href="all-payments.html">All payments</a><a href="budget-2027.html">Budget 2027 changes</a><a href="faq.html">FAQ</a>')
app = App("welfare", "Social Welfare Ireland", "🤝", None, "#0369a1", TABS, FOOT, SRC, None,
          "Social welfare rates 2027 – what you'll get, the Christmas Bonus and payment dates:", "Know someone on a social welfare payment? Send them this.", "welfare",
          f"Rates checked against the Department of Social Protection's Budget 2027 figures and Citizens Information in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a> – not affiliated with the Department of Social Protection. Your entitlement depends on your circumstances; confirm with the Department or apply on <a href='https://services.mywelfare.ie/' rel='noopener'>MyWelfare.ie</a>.")

def rate_txt(p, y):
    v = p["r26"] if y == 2026 else p["r27"]
    if v is None: return "–"
    f = {"week": " a week", "month": " a month", "year": " a year", "once": " once-off"}[p["freq"]]
    return eur(v, 2 if v % 1 else 0) + f

def ci_src(k):
    return ["ci_" + k] if ("ci_" + k) in SRC else []

# ---------------------------------------------------------------- content for each payment
INFO = {
 "state-pension-contributory": dict(what="A weekly pension from age 66 for people with enough PRSI contributions.", who=["Aged 66 or over", "Paid PRSI for at least 10 years (520 contributions) and started paying before age 56 – the amount depends on your total or average contributions", "Not means-tested – you can work and have other income"], dur="Paid for life.", tip="Check your PRSI record on MyWelfare before you turn 66. You can apply up to 6 months before your 66th birthday.", rel=["state-pension-non-contributory", "living-alone-increase", "fuel-allowance"]),
 "state-pension-non-contributory": dict(what="A means-tested weekly pension from 66 for people who don't qualify for the contributory pension.", who=["Aged 66 or over", "Pass a means test (income, savings and property – not your home)", "Living in Ireland (habitual residence)"], dur="Paid for life, reviewed if your means change.", tip="Budget 2027 increases the agri-environmental and seaweed disregards from July 2027 – useful for farmers.", rel=["state-pension-contributory", "living-alone-increase", "fuel-allowance"]),
 "jobseekers-allowance": dict(what="A means-tested weekly payment for people who are unemployed or working 3 days a week or less.", who=["Aged 18 to 65", "Unemployed (or working no more than 3 days a week) and genuinely seeking work", "Pass a means test", "Under 25s get a reduced rate unless they have children or meet certain conditions"], dur="Paid as long as you're eligible.", tip="Your Christmas Bonus needs 12 months (312 days) on Jobseeker's Allowance.", rel=["jobseekers-benefit", "jobseekers-pay-related-benefit", "working-family-payment"]),
 "jobseekers-benefit": dict(what="A weekly payment based on your PRSI contributions if you're unemployed. Since 31 March 2025 most new claims get Jobseeker's Pay-Related Benefit instead.", who=["Under 66 and unemployed (or working 3 days a week or less)", "Enough PRSI contributions (at least 104 paid)", "Available for and genuinely seeking work"], dur="234 days (9 months) with 260+ PRSI contributions, or 156 days (6 months) with fewer.", tip="When it runs out you may move to means-tested Jobseeker's Allowance.", rel=["jobseekers-pay-related-benefit", "jobseekers-allowance", "illness-benefit"]),
 "jobseekers-pay-related-benefit": dict(what="Since 31 March 2025, people who lose their job get a payment linked to what they earned: up to 60% of average weekly earnings.", who=["Your first day of unemployment was on or after 31 March 2025", "At least 2 years (104 weeks) of PRSI paid", "Unemployed and seeking work"], dur="39 weeks with 5+ years of PRSI (60% → 55% → 50%), or 26 weeks at 50% with 2–5 years.", tip="The minimum is €125 a week. Use the table below to see your rate by earnings.", rel=["jobseekers-benefit", "jobseekers-allowance", "illness-benefit"]),
 "jobseekers-transitional-payment": dict(what="A payment for lone parents whose youngest child is aged 7 to 13, who don't have to be available for full-time work.", who=["Lone parent with a youngest child aged 7 to 13", "Pass a means test"], dur="Until your youngest child turns 14.", tip="From July 2027 you can earn €175 a week before it affects the payment (up from €165).", rel=["one-parent-family-payment", "working-family-payment", "child-benefit"]),
 "illness-benefit": dict(what="A weekly payment if you can't work because of illness and have enough PRSI contributions.", who=["Under 66 and unable to work because of illness, certified by a doctor", "Enough PRSI contributions (at least 104 paid)"], dur="Up to 2 years with 260+ contributions, or 6 months with fewer. Not paid for the first days of illness – check with your employer about sick pay.", tip="After 12 months you may get the Christmas Bonus. Long-term illness may move to Invalidity Pension.", rel=["invalidity-pension", "disability-allowance", "jobseekers-benefit"]),
 "invalidity-pension": dict(what="A weekly pension if you can't work because of a long-term illness or disability and have enough PRSI.", who=["Permanently incapable of work, or incapable for at least 12 months and likely to continue for 12 more", "At least 260 paid PRSI contributions"], dur="Paid until 66, when you move to State Pension (Contributory).", tip="Budget 2027 adds a once-off €500 Cost of Disability payment for long-term disability payments.", rel=["illness-benefit", "disability-allowance", "cost-of-disability-payment"]),
 "disability-allowance": dict(what="A means-tested weekly payment for people aged 16 to 66 with a disability expected to last at least a year.", who=["Aged 16 to 66", "Disability expected to last 12 months or more that substantially restricts work", "Pass a means test"], dur="Paid as long as you qualify.", tip="From July 2027 you can earn €175 a week from work before it affects your payment. €500 Cost of Disability payment in 2027.", rel=["invalidity-pension", "blind-pension", "cost-of-disability-payment"]),
 "blind-pension": dict(what="A means-tested weekly payment for people who are blind or have low vision.", who=["Aged 18 or over", "Blind or with low vision (certified)", "Pass a means test"], dur="Paid as long as you qualify.", tip="Earnings disregard rises to €175 a week from July 2027.", rel=["disability-allowance", "cost-of-disability-payment", "living-alone-increase"]),
 "disablement-benefit": dict(what="A payment if you have an injury or disease caused by your job (Occupational Injuries Scheme).", who=["Injured at work or have an occupational disease", "Loss of faculty assessed by a medical assessor"], dur="Depends on your assessment.", tip="Paid on top of most other payments.", rel=["illness-benefit", "invalidity-pension", "disability-allowance"]),
 "carers-allowance": dict(what="A means-tested weekly payment for people caring full-time for someone who needs care.", who=["Caring full-time for someone who needs full-time care", "Aged 18 or over", "Pass a means test – the income disregards rise from July 2027 (€1,150 single, €2,300 couple)"], dur="Paid as long as you're caring.", tip="You also get the Carer's Support Grant (€2,000 a year). Half-rate Carer's Allowance can be paid on top of another payment.", rel=["carers-benefit", "carers-support-grant", "domiciliary-care-allowance"]),
 "carers-benefit": dict(what="A weekly payment, based on PRSI, if you leave work to care for someone full-time.", who=["Left work to care full-time", "Enough PRSI contributions", "Aged 16 to 66"], dur="Up to 104 weeks per person cared for.", tip="Not means-tested. Carer's Leave protects your job for up to 104 weeks.", rel=["carers-allowance", "carers-support-grant", "illness-benefit"]),
 "carers-support-grant": dict(what="An annual grant of €2,000 for carers, paid on the first Thursday of June.", who=["Caring full-time for at least 6 months, or getting Carer's Allowance/Benefit or DCA", "Not means-tested"], dur="Once a year.", tip="Paid automatically if you get Carer's Allowance, Carer's Benefit or Domiciliary Care Allowance.", rel=["carers-allowance", "carers-benefit", "domiciliary-care-allowance"]),
 "domiciliary-care-allowance": dict(what="A monthly payment for a child under 16 with a severe disability who needs much more care than other children of the same age.", who=["Child under 16 with a severe disability expected to last at least 12 months", "Living at home with you", "Not means-tested"], dur="Until the child turns 16 (they may then apply for Disability Allowance).", tip="DCA gets a Christmas Bonus calculated on its weekly equivalent, separately from your other payments.", rel=["carers-allowance", "carers-support-grant", "child-benefit"]),
 "one-parent-family-payment": dict(what="A means-tested weekly payment for lone parents with a child under 7.", who=["Lone parent with your youngest child under 7", "Pass a means test", "Not living with a partner"], dur="Until your youngest child turns 7 (then Jobseeker's Transitional Payment).", tip="From July 2027 you can earn €175 a week before your payment is affected.", rel=["jobseekers-transitional-payment", "working-family-payment", "child-benefit"]),
 "working-family-payment": dict(what="A weekly top-up for employees on low pay with children: 60% of the gap between your family income and a threshold.", who=["Working at least 38 hours a fortnight", "At least one child", "Family income below the threshold for your family size"], dur="Paid for 52 weeks, then reviewed.", tip="Budget 2027 raises every threshold by €30 a week. If you get it, you can also get the Back to School allowance and you qualify for Fuel Allowance.", rel=["child-benefit", "one-parent-family-payment", "jobseekers-allowance"]),
 "child-benefit": dict(what="A monthly payment of €140 for every child under 16 (or under 18/19 in full-time education).", who=["Child under 16, or 16–18 in full-time education or with a disability", "Living in Ireland (habitual residence)", "Not means-tested and not taxed"], dur="Until 16, or until 18 in full-time education (not paid at 19).", tip="Twins get 1.5 times the rate per child, triplets or more double. A New Baby Grant is paid with the first month for babies born from 1 December 2024.", rel=["child-support-payment", "working-family-payment", "one-parent-family-payment"]),
 "child-support-payment": dict(what="The extra weekly amount for each child paid with your main social welfare payment (formerly 'Increase for a Qualified Child').", who=["You get a qualifying social welfare payment", "Your child is under 18 (or under 22 in full-time education)"], dur="Paid with your main payment.", tip="Budget 2027: +€6 a week per child – €64 (under 12) and €84 (12 and over) from January 2027.", rel=["child-benefit", "one-parent-family-payment", "working-family-payment"]),
 "maternity-benefit": dict(what="A weekly payment for 26 weeks while on maternity leave from work.", who=["Employed or self-employed with enough PRSI", "Taking maternity leave"], dur="26 weeks.", tip="Many employers top up your pay – check your contract.", rel=["paternity-benefit", "parents-benefit", "child-benefit"]),
 "paternity-benefit": dict(what="A weekly payment for 2 weeks of paternity leave.", who=["Parent of a child under 6 months (not the parent taking maternity or adoptive leave)", "Enough PRSI contributions"], dur="2 weeks.", tip="Take it within 6 months of the birth or adoption.", rel=["maternity-benefit", "parents-benefit", "child-benefit"]),
 "parents-benefit": dict(what="A weekly payment while on parent's leave in your child's first 2 years.", who=["Parent of a child under 2 (or within 2 years of adoption)", "Enough PRSI contributions"], dur="9 weeks per parent.", tip="Each parent can take their own weeks – they can't be transferred.", rel=["maternity-benefit", "paternity-benefit", "child-benefit"]),
 "adoptive-benefit": dict(what="A weekly payment for adopting parents on adoptive leave.", who=["Adopting a child", "Enough PRSI contributions"], dur="24 weeks.", tip="Adopting parents can also get Paternity and Parent's Benefit.", rel=["maternity-benefit", "parents-benefit", "child-benefit"]),
 "guardians-payment": dict(what="A weekly payment to someone looking after an orphaned child.", who=["Caring for a child whose parents have died (or one parent has died and the other has abandoned the child)"], dur="Until the child is 18, or 22 in full-time education.", tip="Contributory and non-contributory versions are paid at the same rate.", rel=["child-benefit", "bereaved-partners-pension", "one-parent-family-payment"]),
 "bereaved-partners-pension": dict(what="A weekly pension for the spouse or civil partner of someone who died, based on PRSI.", who=["Your spouse or civil partner died", "Enough PRSI contributions (yours or theirs)"], dur="Paid for life (moves to a higher rate at 66 and 80).", tip="A once-off Bereaved Parent Grant (€8,000) may also apply where a child is left without a parent.", rel=["guardians-payment", "state-pension-contributory", "living-alone-increase"]),
 "farm-assist": dict(what="A means-tested weekly payment for farmers on low incomes.", who=["Farming in Ireland", "Aged 18 to 66", "Pass a means test"], dur="Paid as long as you qualify.", tip="From July 2027 €7,500 of agri-environmental scheme income is disregarded (up from €5,000).", rel=["jobseekers-allowance", "state-pension-non-contributory", "working-family-payment"]),
 "supplementary-welfare-allowance": dict(what="A basic weekly payment if you have no income or not enough to live on, while you wait for another payment.", who=["Living in Ireland", "No or very low income", "Pass a means test"], dur="Usually short-term.", tip="Exceptional and urgent needs payments are also available through the Community Welfare Service.", rel=["jobseekers-allowance", "one-parent-family-payment", "fuel-allowance"]),
 "fuel-allowance": dict(what="A weekly payment during the heating season for people on long-term welfare payments who can't afford heating.", who=["Getting a qualifying long-term payment (or Working Family Payment)", "Living alone or only with other qualifying people", "Pass a means test – improved for single pensioners from 2027"], dur="28 weeks. The 2026/2027 season started in the week of Monday 28 September 2026 and runs to April 2027.", tip="€38 a week until Christmas, then €43 a week from the week of 4 January 2027 – €1,134 for the 2026/2027 season. <a href='fuel-allowance-payment-dates.html'>Fuel Allowance dates and lump sums →</a>", rel=["living-alone-increase", "state-pension-contributory", "working-family-payment"]),
 "living-alone-increase": dict(what="An extra weekly amount for people on certain payments who live alone.", who=["Getting a State Pension, Disability Allowance, Invalidity Pension, Blind Pension or certain other payments", "Living alone"], dur="Paid with your main payment.", tip="Budget 2027 raises it to €25 a week – the first increase in five years.", rel=["state-pension-contributory", "fuel-allowance", "disability-allowance"]),
 "cost-of-disability-payment": dict(what="A new once-off €500 payment for people getting a long-term disability payment, paid in the week starting <strong>15 February 2027</strong> with your normal payment.", who=["Getting Disability Allowance, Blind Pension, Invalidity Pension or Partial Capacity Benefit", "Paid automatically – you don't need to apply"], dur="Once-off lump sum, paid in the week starting 15 February 2027.", tip="It's paid on your usual payment day that week – a Wednesday payee gets it on Wednesday 17 February 2027.", rel=["disability-allowance", "invalidity-pension", "blind-pension"]),
}

TITLES = {
    "cost-of-disability-payment": ("€500 Disability Payment 2027 – Paid 15 Feb | Who Gets It (DCA & Carers?)",
        "When is the €500 Cost of Disability payment paid, and will you get it? Check which payments qualify, whether DCA and Carer's Allowance are included, and if you need to apply."),
    "fuel-allowance": ("Fuel Allowance 2026/2027 Ireland – €38, €43 from January | Who Qualifies & Lump Sums",
        "Fuel Allowance is €38 a week, rising to €43 from 4 January 2027. Season from 28 September 2026 to April 2027 (€1,134). Lump sums €532 and €602, who qualifies and the means test."),
    "child-benefit": ("Child Benefit Ireland 2026–2027 – €140 a Month, Payment Dates & Who Qualifies",
        "Child Benefit is €140 per child per month in 2026 and 2027, paid on the first Tuesday of each month. Twins, triplets, who qualifies and the payment dates."),
}
EXTRA_FAQ = {
    "illness-benefit": [("How does sick pay work in Ireland?", "If you've worked for your employer for at least 13 weeks, they must pay Statutory Sick Pay for up to 5 days a year: 70% of your normal pay, up to €110 a day, with a medical cert from day 1. From day 6 you can claim Illness Benefit from the Department of Social Protection if you have enough PRSI."),
                        ("Can I get sick pay from my job and Illness Benefit at the same time?", "Some employers have their own sick pay scheme that pays more than the legal minimum. Many of them top up Illness Benefit to your normal pay and ask you to sign the Illness Benefit over to them – check your contract or ask HR."),
                        ("When does Illness Benefit start?", "From day 6 of your illness if you were entitled to Statutory Sick Pay. If you've already used your 5 sick days this year, it starts from day 4 (after 3 waiting days)."),
                        ("Do you get the Christmas Bonus on Illness Benefit?", "Only if you've been getting Illness Benefit for 12 months or more.")],
    "disability-allowance": [("Do they check your bank account for Disability Allowance?", "Yes. Disability Allowance is means-tested, so the Department looks at your savings and income (and your partner's). You'll usually be asked for recent bank and credit union statements."),
                             ("How much savings can you have on Disability Allowance?", "The first €50,000 of savings, investments or property (not your own home) is ignored. Only capital above €50,000 is assessed as means."),
                             ("Can I get help to buy a bed or a couch on Disability Allowance?", "Ask your Community Welfare Officer (through your Intreo office) about an Exceptional Needs Payment – a once-off payment that can help with essential costs you can't meet from your weekly income. Many credit unions also offer low-cost 'It Makes Sense' loans to people on social welfare, which are a cheaper alternative to buy-now-pay-later plans."),
                             ("Will my partner's carer's payment stop when I reach 66?", "No. Carer's Allowance depends on the care you need, not on which payment you get. <a href='carers-allowance.html'>Carer's Allowance and the State Pension →</a>")],
    "carers-allowance": [("Can my spouse keep Carer's Allowance when I move to the State Pension?", "Yes. Carer's Allowance depends on the care the person needs, not on their payment, so it continues when the person cared for moves from Disability Allowance to the State Pension at 66. Because the means test counts the couple's combined income, a higher pension can reduce the Carer's Allowance rate – the first €2,000 a week of combined income is ignored (€2,300 from July 2027)."),
                         ("Can I get Carer's Allowance and my own State Pension?", "Yes. If you get another social welfare payment, such as your own State Pension, you can keep a half-rate Carer's Allowance on top, and you still get the €2,000 Carer's Support Grant."),
                         ("Do carers get the Christmas Bonus?", "Yes – Carer's Allowance, Carer's Benefit and half-rate Carer's Allowance all get the 100% Christmas Bonus in the week starting 7 December 2026.")],
    "cost-of-disability-payment": [("When is the €500 disability payment paid?", "In the week starting 15 February 2027, on your usual payment day, with your qualifying payment."),
                                   ("Do families on Domiciliary Care Allowance get the €500?", "No – as announced, it's for adults on long-term disability payments, and Domiciliary Care Allowance isn't on the list. DCA families do get the Christmas Bonus, and DCA rises to €380 a month from January 2027. <a href='domiciliary-care-allowance.html'>DCA rates →</a>"),
        ("Do carers get the €500 Cost of Disability payment?", "Not on Carer's Allowance alone – it's paid with Disability Allowance, Blind Pension, Invalidity Pension or Partial Capacity Benefit. Carers get the €2,000 Carer's Support Grant in June instead. <a href='carers-support-grant.html'>Carer's Support Grant →</a>"),
        ("Do I need to apply for the €500 Cost of Disability payment?", "No. It's paid automatically with your Disability Allowance, Blind Pension, Invalidity Pension or Partial Capacity Benefit.")],
    "fuel-allowance": [("When is Fuel Allowance paid?", "Weekly from the week of 28 September 2026 to April 2027, or as two lump sums: €532 in the week of 28 September 2026 and €602 in January 2027."),
                       ("Is there a Fuel Allowance bonus or €300 lump sum this year?", "No. Budget 2027 increased the weekly rate by €5 (to €43 from January) instead.")],
    "child-benefit": [("When is Child Benefit paid?", "On the first Tuesday of every month – Tuesday 1 December 2026 and Tuesday 5 January 2027."),
                      ("Is there a double Child Benefit payment in 2026?", "No. Budget 2027 has no double Child Benefit payment.")],
}

def payment_pages():
    for key, p in P.items():
        info = INFO[key]
        r27 = rate_txt(p, 2027); r26 = rate_txt(p, 2026)
        diff = (p["r27"] - p["r26"]) if (p["r26"] is not None and p["r27"] is not None) else None
        rows = []
        if p["freq"] == "week" and p["r27"] is not None:
            fams = [("Single", {}), ("With 1 child under 12", {"kidsUnder12": 1}), ("With 2 children (under 12 and 12+)", {"kidsUnder12": 1, "kids12": 1})]
            if p.get("iqa"): fams.append(("With a qualified adult + 2 children", {"adult": True, "kidsUnder12": 1, "kids12": 1}))
            res = run([{"k": "w", "key": key, "o": dict(o, year=2027)} for _, o in fams] + [{"k": "w", "key": key, "o": dict(o, year=2026)} for _, o in fams])
            n = len(fams)
            for i, (lab, _) in enumerate(fams):
                a, b = res[i], res[n + i]
                rows.append([lab, eur(b["weekly"], 2) if not b["missing"] and (i == 0 or p.get("qc")) else "–", eur(a["weekly"], 2), eur(a["monthly"]), eur(a["yearly"])])
        facts = ([f"<strong>{p['name']}</strong>: <strong>€500</strong>, paid once in the week starting <strong>15 February 2027</strong>."] if p["freq"] == "once" else [f"<strong>{p['name']}</strong> is <strong>{r27}</strong> from January 2027" + (f", up from {r26} in 2026 (+{eur(diff, 2 if diff % 1 else 0)})." if diff else ".")] if p["r27"] is not None else []) +                 [info["what"], "How long: " + info["dur"]]
        if p.get("xmas"):
            facts.append("You get the <strong>Christmas Bonus</strong> (100% of your weekly payment) in the week starting 7 December 2026" + (" if you've been getting it for 12 months or more." if p["xmas"] == "12m" else "."))
        elif p["freq"] == "week":
            facts.append("This payment does <strong>not</strong> get the Christmas Bonus.")
        extra = ""
        if p.get("r27_80"): extra += f"<p>Aged 80 or over: <strong>{eur(p['r27_80'], 2)}</strong> a week from January 2027.</p>"
        if p.get("r27_66"): extra += f"<p>Aged 66 or over: <strong>{eur(p['r27_66'], 2)}</strong> a week from January 2027.</p>"
        if p.get("u25"): extra += f"<p>Under 25 (in most cases): <strong>{eur(p['u25'], 2)}</strong> a week from January 2027.</p>"
        if p.get("iqa"): extra += f"<p>Increase for a Qualified Adult: <strong>{eur(p['iqa'], 2)}</strong> a week" + (f" ({eur(p['iqa66'], 2)} if your partner is 66 or over)" if p.get("iqa66") else "") + " from January 2027.</p>"
        if key == "jobseekers-pay-related-benefit":
            earn = [300, 400, 500, 600, 700, 750, 800, 1000]
            res = run([{"k": "jprb", "a": a, "y": 5} for a in earn] + [{"k": "jprb", "a": a, "y": 3} for a in earn])
            jrows = [[eur(a)] + [eur(x["amount"]) for x in res[i]] + [eur(res[len(earn) + i][0]["amount"])] for i, a in enumerate(earn)]
            extra += "<h2>Your Pay-Related Benefit by earnings</h2>" + table(["Average weekly earnings", "Weeks 1–13 (60%, max €450)", "Weeks 14–26 (55%, max €375)", "Weeks 27–39 (50%, max €300)", "2–5 yrs PRSI (50%, 26 wks)"], jrows)
            extra += "<p class='muted small'>Minimum €125 a week. Based on 5+ years of PRSI unless shown.</p>"
        if key == "working-family-payment":
            w = META["WFP"]["2027"]
            extra += "<h2>Working Family Payment thresholds 2027</h2>" + table(["Children", "Weekly income limit"], [[str(i + 1) + ("+" if i == 7 else ""), eur(v)] for i, v in enumerate(w)])
            ex = run([{"k": "wfp", "n": 2, "i": 600}])[0]
            extra += f"<p>Example: a family with 2 children and €600 a week income gets 60% of the €{w[1] - 600} gap = <strong>{eur(ex['weekly'], 2)} a week</strong>.</p>"
        if key == "child-benefit":
            extra += "<h2>Child Benefit by number of children</h2>" + table(["Children", "Per month", "Per year"], [[str(n), eur(140 * n), eur(140 * n * 12)] for n in range(1, 7)])
            extra += "<p><a href='child-benefit-payment-dates.html'>Child Benefit payment dates 2026 and 2027 →</a></p>"
        if key == "child-support-payment":
            extra += table(["Child's age", "2026", "2027"], [["Under 12", "€58", "€64"], ["12 and over", "€78", "€84"]])
        rel = "".join(f'<a href="{r}.html">{P[r]["name"]}</a>' for r in info["rel"] if r in P)
        cross = ["salary", "pension", "rent"] if p["cat"] in ("Jobseekers", "Families") else ["salary", "stamp", "rent"] if p["cat"] == "Pensions" else ["salary", "rent", "pension"]
        body = f"""<p class="lead">{p['name']} rates for 2026 and 2027, who qualifies, how long it's paid and the Christmas Bonus.</p>
<p class="updated">Budget 2027 rates · Checked {CHECKED}</p>
{key_facts(facts)}
{('<div class="hero-num"><div><span class="tl">Amount</span><strong>€500</strong></div><div><span class="tl">Paid</span><strong>Week of 15 Feb 2027</strong></div></div>') if p["freq"] == "once" else ('<div class="hero-num"><div><span class="tl">2026</span><strong>' + r26 + '</strong></div><div><span class="tl">From January 2027</span><strong>' + r27 + '</strong></div></div>')}
{extra}
{('<h2>What you get, by family (weekly)</h2>' + table(["Situation", "2026", "2027 per week", "2027 per month", "2027 per year"], rows) + '<p class="muted small">Includes the Child Support Payment (€64 under 12, €84 aged 12+ in 2027). 2026 family figures shown only where the 2026 rate is confirmed.</p>') if rows else ''}
<div class="ad" data-slot="content"></div>
<h2>Who can get {p['name']}?</h2>{lis(info['who'])}
<h2>How long is it paid?</h2><p>{info['dur']}</p>
<h2>Tip</h2><div class="callout">{info['tip']}</div>
{('<h2>Your questions about ' + p['name'] + '</h2>' + faq_html(EXTRA_FAQ[key])) if key in EXTRA_FAQ else ''}
<h2>How to apply</h2><p>Most payments can be claimed online on <a href="https://services.mywelfare.ie/" rel="noopener" target="_blank">MyWelfare.ie</a> with a verified MyGovID, or at your local Intreo Centre.</p>
<div class="cta"><h2>Work out your total</h2><p>Add a partner, children, Living Alone Increase and Fuel Allowance.</p><a class="btn" href="./?p={key}" data-track="welfare_page_cta" data-label="{key}">Open the calculator</a></div>
<h2>Related payments</h2><div class="chip-list">{rel}<a href="all-payments.html">All payments →</a></div>"""
        faqs = ([(f"How much is the {p['name']}?", "€500, paid once in the week starting 15 February 2027.")] if p["freq"] == "once" else [(f"How much is {p['name']} in 2027?", f"{r27} from January 2027" + (f", up {eur(diff, 2 if diff % 1 else 0)} from {r26} in 2026." if diff else "."))] if p["r27"] is not None else []) + [
                (f"Who qualifies for {p['name']}?", "; ".join(info["who"]) + "."),
                (f"Do you get the Christmas Bonus on {p['name']}?", ("Yes – 100% of your weekly payment, paid in the week starting 7 December 2026" + (", once you've been getting it for 12 months." if p['xmas'] == '12m' else ".")) if p.get("xmas") else "No, it isn't a qualifying payment for the Christmas Bonus.")]
        srcs = ci_src(key) + ["dsp27", "ci_rates27"] + (["ci_xmas"] if p.get("xmas") else []) + ["mywelfare"]
        faqs += EXTRA_FAQ.get(key, [])
        t, d = TITLES.get(key, (f"{p['name']} 2027 Rate Ireland – {r27} | Who Qualifies & Christmas Bonus",
                                f"{p['name']} is {r27} from January 2027 (Budget 2027). Who qualifies, how long it's paid, family rates and whether you get the Christmas Bonus."))
        app.page(f"{key}.html", t, d,
                 body, active="All payments", jsonld=[faq_ld(faqs)], crumbs=[("Welfare", "./"), ("All payments", "all-payments.html"), (p["name"], None)],
                 h1=f"{p['name']} rates 2026 and 2027", sources=srcs, cross=cross)

def build_index():
    opts = "".join(f'<option value="{k}">{p["name"]}</option>' for k, p in sorted(P.items(), key=lambda kv: kv[1]["name"]) if p["freq"] == "week" and p["r27"] is not None)
    body = f"""<p class="lead">How much will you get from social welfare in 2027? Pick your payment to see your weekly, monthly and yearly amount with Budget 2027 increases – plus your Christmas Bonus. Free, no sign-up.</p>
<ul class="facts"><li>+€10 a week from January 2027</li><li>Christmas Bonus week of 7 Dec</li><li>Child Support €64 / €84</li></ul>
<form id="wForm" class="card" novalidate>
  <label for="pay" class="big-label">Your payment</label>
  <select id="pay">{opts}</select>
  <fieldset style="margin-top:14px"><legend class="sm">Year</legend>
    <div class="seg two-seg"><label><input type="radio" name="year" value="2026"><span>2026</span></label><label><input type="radio" name="year" value="2027" checked><span>2027<small>Budget 2027</small></span></label></div></fieldset>
  <div class="two">
    <label>Children under 12<input id="k1" type="number" min="0" max="12" inputmode="numeric" placeholder="0"></label>
    <label>Children aged 12+<input id="k2" type="number" min="0" max="12" inputmode="numeric" placeholder="0"></label>
  </div>
  <details id="adv" class="adv"><summary>Advanced options <span class="muted small">– partner, age, living alone, Fuel Allowance…</span></summary><div class="adv-body">
    <label class="check"><input type="checkbox" id="adult"><span>I have a qualified adult (dependent partner) <small class="muted">– 2027 rates</small></span></label>
    <label class="check"><input type="checkbox" id="adult66"><span>My partner is 66 or over</span></label>
    <label>Your age<input id="age" type="number" min="16" max="110" inputmode="numeric" placeholder="e.g. 67"></label>
    <label class="check"><input type="checkbox" id="u25"><span>Under 25 (Jobseeker's Allowance / SWA reduced rate)</span></label>
    <label class="check"><input type="checkbox" id="alone"><span>I live alone (Living Alone Increase)</span></label>
    <label class="check"><input type="checkbox" id="fuel"><span>I get Fuel Allowance</span></label>
    <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
  </div></details>
  <div class="btn-row"><button type="submit" class="btn primary">Show what I'll get</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>Popular payments</h2>
<div class="stamp-grid">{"".join(f'<a class="stamp-card" href="{k}.html"><strong>{P[k]["name"]}</strong><p>{rate_txt(P[k], 2027)} in 2027</p></a>' for k in ("state-pension-contributory", "jobseekers-allowance", "carers-allowance", "disability-allowance", "one-parent-family-payment", "child-benefit", "illness-benefit", "fuel-allowance"))}</div>
<div class="cta"><h2>🎄 Christmas Bonus 2026</h2><p>A double payment in the week starting 7 December. See if you qualify and how much you'll get.</p><a class="btn" href="christmas-bonus.html">Check my Christmas Bonus</a></div>
<div class="cta"><h2>🔍 What else am I entitled to?</h2><p>Free eye test, dental check-up, hearing aid grant, tax credits – see what you might be missing in 1 minute.</p><a class="btn" href="what-am-i-entitled-to.html" data-track="cross_app" data-label="welfare_index_checker">Check what I could get</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Social Welfare Rates Calculator", "url": app.BASE, "applicationCategory": "UtilitiesApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Weekly social welfare rates for 2026 and 2027 (Budget 2027) with qualified adult, children, Living Alone Increase, Fuel Allowance and Christmas Bonus."}
    faqs = [("How much are social welfare payments going up in 2027?", "Most weekly payments rise by €10 from January 2027. The State Pension (Contributory) goes to €309.30, Jobseeker's Allowance to €264 and Carer's Allowance to €280."),
            ("When is the Christmas Bonus paid in 2026?", "In the week starting 7 December 2026, on the same day as your normal payment. It's 100% of your weekly payment (minimum €20).")]
    app.page("index.html", "Social Welfare Rates 2027 Ireland – Calculator: What Will I Get? + Christmas Bonus",
             "Free Irish social welfare calculator with Budget 2027 rates: State Pension, Jobseeker's, Carer's, Disability, One-Parent Family and more. Weekly, monthly and yearly amounts plus Christmas Bonus.",
             body, active="Calculator", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["js/welfare.js", "js/calc.js"], h1="Social welfare calculator 2027",
             sources=("dsp27", "gov27", "ci_rates27", "ci_xmas", "mywelfare"), cross=["salary", "pension", "rent", "mortgage"], priority="0.9",
             share_text="Social welfare rates 2027 calculator 🇮🇪 – see your new weekly rate and your Christmas Bonus:")

def build_hubs():
    cats = {}
    for k, p in P.items(): cats.setdefault(p["cat"], []).append(k)
    order = ["Pensions", "Jobseekers", "Illness & disability", "Carers", "Families", "Extras"]
    body = '<p class="lead">Every Irish social welfare payment with its 2027 rate. Tap one for who qualifies, family rates and the Christmas Bonus.</p>'
    for c in order:
        body += f"<h2>{c}</h2><div class='stamp-grid'>" + "".join(f'<a class="stamp-card" href="{k}.html"><strong>{P[k]["name"]}</strong><p>{rate_txt(P[k], 2027)}</p></a>' for k in cats.get(c, [])) + "</div>"
    body += "<h2>Other supports</h2><div class='stamp-grid'><a class='stamp-card' href='back-to-school-allowance.html'><strong>Back to School Clothing and Footwear Allowance</strong><p>€160 / €285 per child</p></a><a class='stamp-card' href='household-benefits-package.html'><strong>Household Benefits Package &amp; Free Travel</strong><p>For pensioners and people with disabilities</p></a><a class='stamp-card' href='christmas-bonus.html'><strong>Christmas Bonus</strong><p>100% double week, December 2026</p></a><a class='stamp-card' href='additional-needs-payment.html'><strong>Additional Needs Payment</strong><p>Help with essential once-off costs</p></a><a class='stamp-card' href='telephone-support-allowance.html'><strong>Telephone Support Allowance</strong><p>€2.50 a week if you live alone</p></a></div>"
    body += "<h2>PRSI benefits most people miss</h2><div class='stamp-grid'><a class='stamp-card' href='what-am-i-entitled-to.html'><strong>What am I entitled to?</strong><p>Free checker – 1 minute</p></a><a class='stamp-card' href='treatment-benefit.html'><strong>Treatment Benefit</strong><p>Free eye test, dental &amp; hearing aids</p></a><a class='stamp-card' href='free-eye-test.html'><strong>Free eye test &amp; glasses</strong><p>Every 2 years with PRSI</p></a><a class='stamp-card' href='free-dental-check.html'><strong>Free dental check-up</strong><p>Every year with PRSI</p></a><a class='stamp-card' href='hearing-aid-grant.html'><strong>Hearing aid grant</strong><p>€500 per aid</p></a><a class='stamp-card' href='what-does-prsi-cover.html'><strong>What PRSI pays for</strong><p>Class A and Class S</p></a></div>"
    app.page("all-payments.html", "All Social Welfare Payments Ireland 2027 – Rates for Every Payment",
             "A list of every Irish social welfare payment with Budget 2027 rates: pensions, jobseeker's, illness and disability, carer's, family payments, Fuel Allowance and more.",
             body, active="All payments", crumbs=[("Welfare", "./"), ("All payments", None)], h1="All social welfare payments", sources=("dsp27", "ci_rates27"), cross=["salary", "pension", "mortgage"], priority="0.8")

    rows = [[f'<a href="{k}.html">{p["name"]}</a>', rate_txt(p, 2026), rate_txt(p, 2027)] for k, p in sorted(P.items(), key=lambda kv: kv[1]["name"])]
    body = f"""<p class="lead">All social welfare rates for 2026 and 2027 in one table. Budget 2027 increases apply from January 2027.</p>
<p class="updated">Department of Social Protection Budget 2027 figures · Checked {CHECKED}</p>
{key_facts(["Most weekly payments rise by <strong>€10</strong> from the first payment in January 2027.", "State Pension (Contributory) passes €300 for the first time: <strong>€309.30</strong>.",
            "Child Support Payment rises €6 to <strong>€64</strong> (under 12) and <strong>€84</strong> (12+).", "Child Benefit stays at <strong>€140</strong> a month.",
            "Fuel Allowance rises to <strong>€43</strong> a week; Living Alone Increase to <strong>€25</strong>."])}
{table(["Payment", "2026", "2027"], rows)}
<p class="muted small">"–" means the 2026 figure isn't confirmed in the Department's Budget 2027 tables. Maximum personal rates; you may get a reduced rate depending on your PRSI or means.</p>"""
    app.page("rates-2027.html", "Social Welfare Rates 2027 Ireland – Full Table (2026 vs 2027)",
             "Every Irish social welfare rate for 2026 and 2027: State Pension €309.30, Jobseeker's €264, Carer's €280, Disability €264, One-Parent Family €264, Child Benefit €140 and more.",
             body, active="Rates 2027", crumbs=[("Welfare", "./"), ("Rates 2027", None)], h1="Social welfare rates 2027", sources=("dsp27", "ci_rates27", "ci_rates26"), cross=["salary", "pension"], priority="0.9")

    body = f"""<p class="lead">What changes for social welfare in Budget 2027 – the new rates, who benefits and when.</p>
<p class="updated">Announced 6 October 2026 · Checked {CHECKED}</p>
{key_facts(["<strong>€10 a week</strong> more on most payments from January 2027, including all State Pensions, Jobseeker's, Illness, Disability and Carer's payments.",
            "A <strong>€500 Cost of Disability payment</strong> in 2027 for people on a long-term disability payment.", "<strong>Child Support Payment +€6</strong> per child: €64 and €84.",
            "<strong>Fuel Allowance €43</strong> a week (+€5) from the week of 4 January 2027 – the January lump sum rises from €532 to €602; the income limit for a single person aged 66+ rises from €534 to €653.", "<strong>Living Alone Increase €25</strong> (+€3).",
            "Working Family Payment thresholds up <strong>€30</strong> a week.", "<strong>Christmas Bonus</strong> (100%) to almost 1.4 million people in December 2026.", "No change to Child Benefit (€140)."])}
<h2>From July 2027</h2>{lis(["Disability Allowance and Blind Pension earnings disregard up to €175 a week", "One-Parent Family Payment and Jobseeker's Transitional Payment earnings disregard up to €175",
    "Carer's Allowance income disregards up to €1,150 (single) and €2,300 (couple)", "Increase for a Qualified Adult income threshold from €310 to €340", "Farm Assist / State Pension (Non-Contributory): agri-environmental disregard €7,500"])}
<div class="cta"><h2>Your new rate</h2><p>See exactly what you'll get from January.</p><a class="btn" href="./">Open the calculator</a></div>
<p>Budget 2027 also changed income tax – <a href="../salary/budget-2027.html">see how your take-home pay changes</a>.</p>"""
    app.page("budget-2027.html", "Budget 2027 Social Welfare Changes – €10 Increase, Christmas Bonus, Fuel Allowance",
             "Budget 2027 social welfare: €10 a week more from January 2027, €500 Cost of Disability payment, Child Support Payment €64/€84, Fuel Allowance €43, Living Alone €25, Christmas Bonus.",
             body, active="Budget 2027", crumbs=[("Welfare", "./"), ("Budget 2027", None)], h1="Budget 2027: social welfare changes", sources=("dsp27", "gov27", "ci_rates27"), cross=["salary", "pension", "mortgage"], priority="0.9")

XMAS_Q = [("I moved from One-Parent Family Payment to Jobseeker's Transitional Payment – do I get the Christmas Bonus?", "Yes. Jobseeker's Transitional Payment is a qualifying payment in its own right, so there's no 12-month wait. You get 100% of your weekly payment in the week starting 7 December 2026."),
    ("I moved from Illness Benefit to Disability Allowance – will I get the Christmas Bonus?", "Yes. Disability Allowance qualifies straight away, as long as you're getting it in the week the bonus is paid. (Illness Benefit on its own only qualifies once you've been getting it for 12 months.)"),
    ("Do you get the Christmas Bonus on Supplementary Welfare Allowance?", "Only if you've been getting it for 12 months (364 days) or more. If you don't qualify, ask your Community Welfare Officer about an Exceptional Needs Payment to help with Christmas costs."),
    ("I moved from Supplementary Welfare Allowance to Jobseeker's Allowance – am I entitled to the Christmas Bonus?", "Jobseeker's Allowance qualifies once you've been getting it for 12 months (312 days). Whether earlier time on another payment can count depends on your claim history – check with your Intreo office."),
    ("Does Jobseeker's Benefit or Pay-Related Benefit get a double payment at Christmas?", "No. Jobseeker's Benefit and Jobseeker's Pay-Related Benefit don't get the Christmas Bonus. In previous years, though, payments due over Christmas and New Year were paid a week early, so you may get two weeks together before Christmas – that's not a bonus, and it means a gap in early January."),
    ("I'm on half-rate Carer's Allowance – how much is my Christmas Bonus?", "100% of the half-rate Carer's Allowance you're paid each week, on top of the bonus on your main payment. If your rate is being reviewed, the bonus is based on the rate you're being paid in the week it's issued – if a review later raises your rate, ask the Department whether the difference is paid."),
    ("I get two payments – do I get two bonuses?", "Yes. If you get two qualifying payments (for example One-Parent Family Payment and Domiciliary Care Allowance, or a half-rate Carer's Allowance with your main payment), you get a bonus for each."),
    ("How are payments paid around Christmas and New Year?", "The Christmas Bonus is paid with your normal payment in the week starting 7 December 2026. Payments due in Christmas week and New Year week are usually paid early, which often leaves a gap in early January. <a href='christmas-payment-dates.html'>Christmas payment dates 2026 →</a>")]

def build_xmas():
    qual = [k for k, p in P.items() if p.get("xmas")]
    rows = []
    res = run([{"k": "w", "key": k, "o": {"year": 2026}} for k in qual])
    for k, r in zip(qual, res):
        if r["missing"] or not r["xmas"].get("eligible"): continue
        rows.append([f'<a href="{k}.html">{P[k]["name"]}</a>', eur(r["xmas"]["amount"], 2), "After 12 months" if P[k]["xmas"] == "12m" else "Yes"])
    opts = "".join(f'<option value="{k}">{P[k]["name"]}</option>' for k in sorted(qual, key=lambda k: P[k]["name"]))
    body = f"""<p class="lead">The Christmas Bonus 2026 is a double payment – 100% of your normal weekly payment – paid in the week starting <strong>Monday 7 December 2026</strong>. Check if you qualify and how much you'll get.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts(["Paid in the week starting <strong>7 December 2026</strong>, on the same day as your normal payment – a Thursday payee gets it on Thursday 10 December.",
            "It's <strong>100%</strong> of your normal weekly payment, including increases for a partner and children. Minimum €20.", "You don't need to apply – it's paid automatically.",
            "Long-term payments only: pensions, Carer's, Disability, One-Parent Family, and Jobseeker's Allowance after 12 months (312 days).", "<strong>Fuel Allowance doesn't qualify</strong>. Two qualifying payments = two bonuses."])}
<form id="xForm" class="card" novalidate><label for="xPay" class="big-label">Your payment</label><select id="xPay">{opts}</select>
<label>Your weekly amount (optional – including partner and children)<div class="money"><span>€</span><input id="xAmt" type="text" inputmode="decimal" placeholder="leave blank for the maximum rate"></div></label>
<div class="btn-row"><button type="submit" class="btn primary">Check my Christmas Bonus</button></div></form>
<div id="xOut" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>Christmas Bonus 2026 by payment (maximum personal rate)</h2>
{table(["Payment", "Christmas Bonus", "Qualifies"], rows)}
<h2>Christmas Bonus: your questions</h2>{faq_html(XMAS_Q)}
<h2>Who doesn't get it</h2>{lis(["Fuel Allowance on its own", "Jobseeker's Benefit / Pay-Related Benefit", "Short-term Illness Benefit (under 12 months)", "Child Benefit (no Christmas double payment)", "Maternity, Paternity and Parent's Benefit"])}
<div class="cta"><h2>Your 2027 rate</h2><p>See what you'll get from January after the €10 increase.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("When is the Christmas Bonus 2026 paid?", "In the week starting Monday 7 December 2026, on the day you normally get your payment."),
            ("How much is the Christmas Bonus 2026?", "100% of your normal weekly social welfare payment, with a minimum of €20."),
            ("Do I need to apply for the Christmas Bonus?", "No. It's paid automatically if you're getting a qualifying long-term payment."),
            ("Is Child Benefit doubled at Christmas?", "No. Child Benefit isn't a qualifying payment for the Christmas Bonus.")] + XMAS_Q
    app.page("christmas-bonus.html", "Christmas Bonus 2026 Ireland – Date (Week of 7 December), Amount & Who Qualifies",
             "Social welfare Christmas Bonus 2026: a 100% double payment in the week starting 7 December 2026. Check if you qualify and how much you'll get, payment by payment.",
             body, active="Christmas Bonus", jsonld=[faq_ld(faqs)], slot="calculator", scripts=["js/welfare.js", "js/calc.js"], crumbs=[("Welfare", "./"), ("Christmas Bonus", None)],
             h1="🎄 Christmas Bonus 2026", sources=("ci_xmas", "dsp27", "gov27"), cross=["salary", "rent", "pension"], priority="0.9",
             share_text="🎄 Christmas Bonus 2026 – double payment in the week of 7 December. Check what you'll get:")

def build_dates():
    d26, d27 = run([{"k": "cb", "y": 2026}, {"k": "cb", "y": 2027}])
    def nice(s):
        dt = datetime.date.fromisoformat(s); return f"{dt.strftime('%A')} {dt.day} {dt.strftime('%B %Y')}"
    def short(s):
        dt = datetime.date.fromisoformat(s); return f"{dt.strftime('%a')} {dt.day} {dt.strftime('%B')}"
    rows = [[datetime.date.fromisoformat(a).strftime("%B"), nice(a), nice(b)] for a, b in zip(d26, d27)]
    nxt = next((x for x in d26 + d27 if datetime.date.fromisoformat(x) >= TODAY), d27[0])
    dec26 = next(x for x in d26 if x[5:7] == "12"); jan27 = d27[0]
    cb_faq = [("When is Child Benefit paid in December 2026?", f"On {nice(dec26)} – €140 per child. The next payment is {nice(jan27)}."),
              ("When is Child Benefit paid?", "On the first Tuesday of every month, into your bank account or at the post office."),
              ("Is there a double Child Benefit payment in 2026?", "No. Budget 2027 didn't include a double or extra Child Benefit payment, and Child Benefit isn't part of the Christmas Bonus. The double payments you may have seen were once-off measures in earlier budgets."),
              ("How much is Child Benefit in 2027?", "€140 per child per month – unchanged in Budget 2027. Twins get 1.5 times the rate per child, triplets and more get double."),
              ("Is Child Benefit paid early at Christmas?", f"No – the December payment is on the first Tuesday as normal ({nice(dec26)}), well before Christmas.")]
    body = f"""<p class="lead">Child Benefit is paid on the <strong>first Tuesday of every month</strong> – €140 per child. December 2026: <strong>{nice(dec26)}</strong>. All the dates for 2026 and 2027 are below.</p>
<p class="updated">Checked {CHECKED}</p>
<div class="earliest"><div class="tl">Next Child Benefit payment</div><div class="ed">{nice(nxt)}</div><div>€140 per child</div></div>
{key_facts([f"<strong>December 2026:</strong> {nice(dec26)}. <strong>January 2027:</strong> {nice(jan27)}.",
            "Child Benefit is <strong>€140 a month</strong> per child in 2026 and 2027 – no change in Budget 2027.", "Paid on the first Tuesday of each month into your bank account or at the post office.",
            "<strong>No double payment</strong> in 2026: Budget 2027 has no double Child Benefit, and Child Benefit doesn't get the Christmas Bonus.",
            "Twins get 1.5 times the rate per child; triplets and more get double."])}
{table(["Month", "2026", "2027"], rows)}
<p class="muted small">Calculated as the first Tuesday of each month. If a payment day falls on a public holiday the Department may pay on a different day – check your bank or the Department.</p>
<div class="ad" data-slot="content"></div>
<h2>Child Benefit questions</h2>{faq_html(cb_faq)}
<p>Also for families: <a href="child-support-payment.html">Child Support Payment</a> · <a href="working-family-payment.html">Working Family Payment</a> · <a href="back-to-school-allowance.html">Back to School Allowance</a> · <a href="one-parent-family-payment.html">One-Parent Family Payment</a> · <a href="payment-dates.html">All payment dates</a></p>"""
    app.page("child-benefit-payment-dates.html", f"Child Benefit Payment Dates Dec 2026 & 2027 – Next: {short(dec26)}",
             f"When is Child Benefit paid in December 2026? Next payment {short(dec26)}, then {short(jan27)}. See every 2027 date, how bank holidays move it and whether there's a Christmas double payment.",
             body, active="Payment dates", jsonld=[faq_ld(cb_faq)],
             crumbs=[("Welfare", "./"), ("Payment dates", "payment-dates.html"), ("Child Benefit dates", None)], h1="Child Benefit payment dates 2026 and 2027",
             sources=("ci_child-benefit", "dsp27"), cross=["salary", "mortgage", "rent"], priority="0.9")

    KEY = [["Week of 28 September 2026", "Fuel Allowance season starts (€38 a week). First lump sum (€532) for lump-sum payees"],
           [nice(dec26), "Child Benefit (€140 per child)"],
           ["Week starting Monday 7 December 2026", "<strong>Christmas Bonus</strong> (100% of your weekly payment) paid with your normal payment"],
           ["Friday 25 &amp; Saturday 26 December 2026", "Christmas Day and St Stephen's Day – payments due on a bank holiday are usually paid early"],
           ["Friday 1 January 2027", "New Year's Day – bank holiday"],
           ["Week of 4 January 2027", "<strong>Budget 2027 increases</strong> start (+€10 on most payments). Fuel Allowance rises to €43. January Fuel Allowance lump sum €602"],
           [nice(jan27), "Child Benefit (€140)"],
           ["Week starting 15 February 2027", "<strong>€500 Cost of Disability payment</strong> (Disability Allowance, Blind Pension, Invalidity Pension, Partial Capacity Benefit)"],
           ["April 2027", "Fuel Allowance season ends"],
           ["First Thursday of June 2027", "Carer's Support Grant (€2,000)"],
           ["July 2027", "Higher earnings disregards (€175 a week) and Carer's Allowance income limits"]]
    pd_faq = [("When are social welfare payments paid?", "Most weekly payments are paid on the same day every week – the day is on your payment notice and depends on the payment and how you're paid."),
              ("When is the Christmas Bonus 2026 paid?", "In the week starting Monday 7 December 2026, on your normal payment day."),
              ("When do the Budget 2027 increases start?", "From your first payment in January 2027 – the week of 4 January 2027."),
              ("When is the €500 disability payment paid?", "In the week starting 15 February 2027, with your Disability Allowance, Blind Pension, Invalidity Pension or Partial Capacity Benefit."),
              ("When is Fuel Allowance paid?", "Weekly with your main payment from the week of 28 September 2026 to April 2027, or as two lump sums (€532 in September and €602 in January)."),
              ("Are social welfare payments paid early at Christmas?", "Payments due on Christmas Day (Friday 25 December) or St Stephen's Day are usually paid early. The Department confirms the exact Christmas schedule in December – check gov.ie or MyWelfare.")]
    body = f"""<p class="lead">When is social welfare paid in Ireland? Every key date from the Christmas Bonus to the January increases, Fuel Allowance and the €500 disability payment.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Most weekly payments are paid on the <strong>same day every week</strong> – the day is shown on your payment notice.",
            "<strong>Christmas Bonus</strong>: week starting <strong>7 December 2026</strong>, with your normal payment. <a href='christmas-bonus.html'>Amounts →</a> · <a href='christmas-payment-dates.html'>Christmas and New Year payments →</a>",
            f"<strong>Child Benefit</strong>: first Tuesday of each month – {short(dec26)}, then {short(jan27)}. <a href='child-benefit-payment-dates.html'>All dates →</a>",
            "<strong>Budget 2027 increases</strong>: from the week of <strong>4 January 2027</strong> (+€10 on most payments).",
            "<strong>€500 Cost of Disability payment</strong>: week starting <strong>15 February 2027</strong>. <a href='cost-of-disability-payment.html'>Who gets it →</a>",
            "<strong>Fuel Allowance</strong>: €38 a week now, €43 from January. <a href='fuel-allowance-payment-dates.html'>Fuel Allowance dates →</a>"])}
<h2>Key social welfare dates 2026–2027</h2>{table(["Date", "What happens"], KEY)}
<div class="ad" data-slot="content"></div>
<h2>Questions about payment dates</h2>{faq_html(pd_faq)}
<p>Is there an autumn bonus or other lump sum this year? <a href="lump-sum-payments.html">All extra payments 2026–2027 →</a> · <a href="../salary/public-holidays.html">Bank holidays 2026 and 2027 →</a></p>"""
    app.page("payment-dates.html", "Social Welfare Payment Dates 2026–2027 Ireland – Christmas Bonus, January Increase, €500",
             "Social welfare payment dates in Ireland: Christmas Bonus week of 7 December 2026, Child Benefit dates, Budget 2027 increases from 4 January, €500 disability payment week of 15 February 2027, Fuel Allowance.",
             body, active="Payment dates", jsonld=[faq_ld(pd_faq)], crumbs=[("Welfare", "./"), ("Payment dates", None)], h1="Social welfare payment dates 2026–2027",
             sources=("ci_xmas", "ci_child-benefit", "ci_fuel-allowance", "dsp27"), cross=["salary", "rent"], priority="0.9")

    fa_faq = [("When does Fuel Allowance start in 2026?", "The 2026/2027 season started in the week of Monday 28 September 2026, paid on your usual payment day."),
              ("When is the Fuel Allowance lump sum paid?", "If you take it as two lump sums, the first (€532) was paid in the week of 28 September 2026 and the second (€602) is paid in January 2027."),
              ("How much is Fuel Allowance?", "€38 a week until the end of December 2026, then €43 a week from the week of 4 January 2027 – €1,134 for the 2026/2027 season."),
              ("Is there a €300 Fuel Allowance lump sum this year?", "No. Budget 2027 raised the weekly rate by €5 instead of paying a once-off lump sum like the €300 payments in some earlier years."),
              ("When does Fuel Allowance end?", "In April 2027, after 28 weeks."),
              ("What is the Fuel Allowance income limit for over-66s?", "€534 a week for a single person aged 66 or over, rising to €653 from January 2027.")]
    body = f"""<p class="lead">Fuel Allowance 2026/2027: when it's paid, how much, and the lump sum dates.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
<div class="hero-num"><div><span class="tl">Until December 2026</span><strong>€38</strong><span class="muted">a week</span></div><div><span class="tl">From 4 January 2027</span><strong>€43</strong><span class="muted">a week</span></div></div>
{key_facts(["The season started in the week of <strong>Monday 28 September 2026</strong> and lasts <strong>28 weeks</strong>, to April 2027.",
            "Paid <strong>weekly</strong> with your main payment, or as <strong>two lump sums</strong>: <strong>€532</strong> (week of 28 September 2026) and <strong>€602</strong> (January 2027).",
            "The rate rises from €38 to <strong>€43</strong> in the week beginning <strong>4 January 2027</strong> (Budget 2027). Season total: <strong>€1,134</strong>.",
            "<strong>No €300 lump sum</strong> this year – Budget 2027 raised the weekly rate instead.",
            "Income limit for a single person aged 66+: €534 a week, rising to <strong>€653</strong> from January 2027.",
            "Fuel Allowance <strong>doesn't</strong> get the Christmas Bonus. Only one Fuel Allowance is paid per household."])}
{table(["Period", "Weeks", "Weekly", "Total"], [["28 Sept – 31 Dec 2026", "14", "€38", "€532"], ["4 Jan – April 2027", "14", "€43", "€602"], ["<strong>Season 2026/2027</strong>", "28", "", "<strong>€1,134</strong>"]])}
<div class="ad" data-slot="content"></div>
<h2>Fuel Allowance questions</h2>{faq_html(fa_faq)}
<p><a href="fuel-allowance.html">Who qualifies for Fuel Allowance →</a> · <a href="household-benefits-package.html">Household Benefits Package →</a> · <a href="payment-dates.html">All payment dates →</a></p>"""
    app.page("fuel-allowance-payment-dates.html", "Fuel Allowance Payment Dates 2026/2027 – Next Lump Sum, €43 from January & No €300 Bonus?",
             "When is the next Fuel Allowance lump sum paid? See the January 2027 date, when the rate rises to €43, how much you get for the season and whether there's a €300 bonus this year.",
             body, active="Payment dates", jsonld=[faq_ld(fa_faq)], crumbs=[("Welfare", "./"), ("Payment dates", "payment-dates.html"), ("Fuel Allowance dates", None)], h1="Fuel Allowance payment dates 2026/2027",
             sources=("ci_fuel-allowance", "dsp27"), cross=["salary", "rent", "solar"], priority="0.9")

    ls_faq = [("Is there an autumn bonus in 2026?", "No. Budget 2027 didn't include an autumn double payment or autumn bonus."),
              ("Is there a double Child Benefit payment in 2026?", "No. Child Benefit stays at €140 a month with no double payment."),
              ("What extra social welfare payments are there this winter?", "The 100% Christmas Bonus (week of 7 December 2026) and the €500 Cost of Disability payment (week of 15 February 2027) for people on long-term disability payments."),
              ("Is there a cost-of-living lump sum in 2026?", "No general cost-of-living lump sum. Budget 2027 put the money into permanent increases instead: +€10 a week on most payments and +€5 on Fuel Allowance from January 2027.")]
    paid = [['<a href="christmas-bonus.html">Christmas Bonus</a>', "100% of your weekly payment (min €20)", "Week starting 7 December 2026", "Long-term payments"],
            ['<a href="cost-of-disability-payment.html">Cost of Disability payment</a>', "€500 once-off", "Week starting 15 February 2027", "Disability Allowance, Blind Pension, Invalidity Pension, Partial Capacity Benefit"],
            ['<a href="fuel-allowance-payment-dates.html">Fuel Allowance lump sum</a>', "€602", "January 2027", "Fuel Allowance lump-sum payees"],
            ['<a href="carers-support-grant.html">Carer&#39;s Support Grant</a>', "€2,000", "First Thursday of June 2027", "Carers"]]
    body = f"""<p class="lead">Is there an autumn bonus, a double Child Benefit or a Fuel Allowance lump sum this year? Here's what is – and isn't – being paid in 2026 and 2027.</p>
<p class="updated">Budget 2027 · Checked {CHECKED}</p>
<h2>Being paid</h2>{table(["Payment", "Amount", "When", "Who"], paid)}
<h2>Not being paid this year</h2>{lis(["<strong>Autumn bonus / autumn double payment</strong> – not in Budget 2027", "<strong>Double Child Benefit</strong> – not in Budget 2027", "<strong>€300 Fuel Allowance lump sum</strong> – replaced by a €5 weekly increase",
    "<strong>General cost-of-living lump sums</strong> – replaced by permanent weekly increases (+€10 from January 2027)"])}
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(ls_faq)}
<div class="cta"><h2>What will you get in 2027?</h2><p>Your weekly rate after the €10 increase.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("lump-sum-payments.html", "Social Welfare Bonus & Lump Sum Payments 2026–2027 – Autumn Bonus? Double Child Benefit?",
             "Extra social welfare payments 2026–2027: Christmas Bonus (week of 7 December), €500 Cost of Disability (week of 15 February 2027), Fuel Allowance lump sum. No autumn bonus or double Child Benefit this year.",
             body, active="Payment dates", jsonld=[faq_ld(ls_faq)], crumbs=[("Welfare", "./"), ("Payment dates", "payment-dates.html"), ("Bonus and lump sums", None)], h1="Social welfare bonus and lump sum payments 2026–2027",
             sources=("ci_xmas", "dsp27", "gov27", "ci_fuel-allowance"), cross=["salary", "rent", "pension"], priority="0.8")

def build_xmas_dates():
    q = [("When is the Christmas Bonus 2026 paid?", "In the week starting Monday 7 December 2026, on your normal payment day, together with your normal weekly payment."),
         ("Are social welfare payments paid early at Christmas?", "Usually, yes. In recent years payments due over Christmas and New Year were paid in advance, so many people got two weeks' payment together before Christmas and nothing in the first week of January. The Department confirms the 2026 schedule in December."),
         ("Will I get paid in the first week of January 2027?", "If your New Year payment is paid early in December (as in previous years), you may get nothing that week – plan your money for the gap. Your first payment at the new Budget 2027 rate (+€10) comes in January."),
         ("When is Child Benefit paid in December 2026?", "On Tuesday 1 December 2026, then Tuesday 5 January 2027. Child Benefit doesn't get a Christmas double payment."),
         ("What if I need help with Christmas costs?", "If you're on a low income and not getting the Christmas Bonus, apply for an Additional Needs Payment (it replaced the Exceptional Needs Payment) on MyWelfare.ie or through your Intreo office.")]
    body = f"""<p class="lead">How will social welfare be paid over Christmas and New Year 2026? The Christmas Bonus, payments paid early, the January gap and the first payments at the new 2027 rates.</p>
<p class="updated">Checked {CHECKED} · We'll update this page when the Department confirms the 2026 Christmas schedule</p>
{key_facts(["<strong>Week starting 7 December 2026:</strong> normal payment <strong>plus the 100% Christmas Bonus</strong> (a double payment) for long-term payments. <a href='christmas-bonus.html'>Do I qualify?</a>",
            "<strong>Christmas Day is Friday 25 December</strong>, St Stephen's Day Saturday 26 December and New Year's Day Friday 1 January 2027 – all public holidays.",
            "In previous years, payments due in Christmas week and New Year week were <strong>paid early</strong> – often two weeks together just before Christmas.",
            "That usually means <strong>no payment in the first week of January</strong>. Budget for the gap.",
            "Budget 2027 increases (+€10 on most payments) start in <strong>January 2027</strong>.",
            "The exact 2026 dates are confirmed by the Department in December – check gov.ie, MyWelfare or your post office."])}
<h2>What to expect, week by week</h2>
{table(["Week", "What usually happens", "Status"], [
    ["Week of 30 November", "Normal payment. Child Benefit on Tuesday 1 December", "✅ Confirmed"],
    ["Week of 7 December", "Normal payment <strong>+ Christmas Bonus</strong> (double payment)", "✅ Confirmed"],
    ["Week of 14 December", "Normal payment", "✅ Normal week"],
    ["Week of 21 December (Christmas)", "Normal payment, often <strong>plus the following week's payment in advance</strong>", "⏳ To be confirmed"],
    ["Week of 28 December (New Year)", "Often nothing – already paid in advance", "⏳ To be confirmed"],
    ["Week of 4 January 2027", "Payments resume at the <strong>new 2027 rates</strong>. Child Benefit Tuesday 5 January. Fuel Allowance rises to €43", "✅ Confirmed"]])}
<div class="callout warn">Planning tip: the double payment in early December and the early payment before Christmas have to stretch until the week of 4 January. Set some aside for early January.</div>
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(q)}
<p><a href="christmas-bonus.html">Christmas Bonus 2026: who qualifies and how much →</a> · <a href="payment-dates.html">All payment dates →</a> · <a href="lump-sum-payments.html">Other bonus and lump sum payments →</a></p>"""
    app.page("christmas-payment-dates.html", "Social Welfare Christmas Payment Dates 2026 Ireland – Bonus, Early Payments & January Gap",
             "Social welfare over Christmas 2026: Christmas Bonus in the week of 7 December, payments usually paid early before Christmas, the early-January gap and new 2027 rates from the week of 4 January.",
             body, active="Payment dates", jsonld=[faq_ld(q)], crumbs=[("Welfare", "./"), ("Payment dates", "payment-dates.html"), ("Christmas payment dates", None)],
             h1="Social welfare Christmas payment dates 2026", sources=("ci_xmas", "dsp27", "mywelfare"), cross=["salary", "rent", "pension"], priority="0.9",
             share_text="🎄 How social welfare is paid over Christmas 2026 – Christmas Bonus, early payments and the January gap:")

def build_extras():
    body = """<p class="lead">The Back to School Clothing and Footwear Allowance helps families on social welfare or low pay with school costs.</p>
""" + key_facts(["<strong>€160</strong> for each child aged 2 to 11 (extended to 2- and 3-year-olds in Budget 2026 – check eligibility).", "<strong>€285</strong> for each child aged 12 to 22 in full-time second-level education.",
                 "Paid automatically to many families in July; others apply from June to 30 September.", "You must get a qualifying payment (or be on low pay) and meet the income limits."]) + """
<p>Getting <a href="working-family-payment.html">Working Family Payment</a>, <a href="one-parent-family-payment.html">One-Parent Family Payment</a> or <a href="jobseekers-allowance.html">Jobseeker's Allowance</a>? You may qualify.</p>"""
    app.page("back-to-school-allowance.html", "Back to School Clothing and Footwear Allowance 2026–2027 – €160 / €285",
             "Back to School Clothing and Footwear Allowance in Ireland: €160 for younger children and €285 for children 12+, who qualifies and when it's paid.",
             body, active="All payments", crumbs=[("Welfare", "./"), ("All payments", "all-payments.html"), ("Back to School Allowance", None)], h1="Back to School Allowance",
             sources=("ci_bts",), cross=["salary", "rent"])
    body = """<p class="lead">Extra supports for pensioners, carers and people with disabilities on top of weekly payments.</p>
""" + key_facts(["The <strong>Household Benefits Package</strong> helps with electricity or gas costs and includes a free TV licence – for people aged 70+, or 66+ on certain payments, and others who qualify.",
                 "<strong>Free Travel</strong> lets you use public transport free – for everyone aged 66+ living in Ireland, and people on certain disability or carer payments.",
                 "<strong>Living Alone Increase</strong>: €25 a week from January 2027. <strong>Fuel Allowance</strong>: €43 a week in the season."]) + """
<p><a href="living-alone-increase.html">Living Alone Increase</a> · <a href="fuel-allowance.html">Fuel Allowance</a> · <a href="state-pension-contributory.html">State Pension</a></p>"""
    app.page("household-benefits-package.html", "Household Benefits Package & Free Travel Ireland – Who Qualifies",
             "Household Benefits Package (electricity/gas allowance and free TV licence) and Free Travel in Ireland: who qualifies, plus Living Alone Increase and Fuel Allowance rates for 2027.",
             body, active="All payments", crumbs=[("Welfare", "./"), ("All payments", "all-payments.html"), ("Household Benefits & Free Travel", None)], h1="Household Benefits Package and Free Travel",
             sources=("ci_hbp", "ci_travel", "dsp27"), cross=["stamp", "salary"])

    # scenario page: welfare vs work
    jobs = [(20, 14.94), (30, 14.94), (39, 14.94), (39, 17)]
    body = f"""<p class="lead">Would you be better off working? Compare Jobseeker's Allowance (€264 a week in 2027) with take-home pay from a job.</p>
{key_facts(["Jobseeker's Allowance is <strong>€264 a week</strong> from January 2027 (personal rate, aged 25+).", "A full-time job at the 2027 minimum wage (€14.94 × 39 hours) is €582.66 a week before tax.",
            "If you work at least 38 hours a fortnight and have children, you may get <strong>Working Family Payment</strong> on top of your wages.", "Use the take-home pay calculator to see your exact net pay."])}
{table(["Job", "Gross per week", "Compare with JA (€264)"], [[f"{h} hours at €{r}", eur(h * r, 2), ("+" if h * r > 264 else "") + eur(h * r - 264, 2) + " before tax"] for h, r in jobs])}
<div class="cta"><h2>Your take-home pay</h2><p>See your net pay after tax, USC and PRSI for any job.</p><a class="btn" href="../salary/?gross=14.94&amp;period=hour&amp;year=2027" data-track="cross_app" data-label="salary_from_welfare">Take-home pay calculator</a></div>"""
    app.page("jobseekers-vs-working.html", "Jobseeker's Allowance vs Working 2027 – Am I Better Off in a Job?",
             "Compare Jobseeker's Allowance (€264 a week in 2027) with minimum wage take-home pay (€14.94 an hour), plus Working Family Payment for parents in low-paid work.",
             body, active="All payments", crumbs=[("Welfare", "./"), ("Jobseeker's vs working", None)], h1="Jobseeker's Allowance vs working", sources=("dsp27", "ci_jobseekers-allowance", "ci_working-family-payment"), cross=["salary", "pension"])

def build_faq():
    FAQ = [("How much is the State Pension in 2027?", "€309.30 a week (Contributory) and €298 (Non-Contributory) from January 2027, with higher rates at 80."),
           ("How much is Jobseeker's Allowance in 2027?", "€264 a week for people aged 25 and over (€173.70 for most under-25s), plus €175.20 for a qualified adult and €64/€84 per child."),
           ("When do the Budget 2027 increases start?", "From your first payment in January 2027."),
           ("When is the Christmas Bonus 2026 paid?", "In the week starting 7 December 2026, with your normal payment. It's 100% of your weekly payment."),
           ("Is Child Benefit going up in 2027?", "No. Child Benefit stays at €140 a month per child."),
           ("How much is Carer's Allowance in 2027?", "€280 a week under 66 and €318 for carers aged 66 and over, plus the €2,000 Carer's Support Grant."),
           ("What is the Cost of Disability payment?", "A new once-off €500 payment for people on Disability Allowance, Blind Pension, Invalidity Pension or Partial Capacity Benefit, paid in the week starting 15 February 2027."),
           ("How much is Fuel Allowance in 2027?", "€43 a week from the week of 4 January 2027 (up from €38). For the 2026/2027 season that's €1,134 in total; lump-sum payees get €532 in September and €602 in January."),
           ("Is there an autumn bonus or double payment in 2026?", "No. Budget 2027 has no autumn double payment, double Child Benefit or Fuel Allowance lump sum. The extras are the 100% Christmas Bonus (week of 7 December 2026) and the €500 Cost of Disability payment (week of 15 February 2027)."),
           ("What is Jobseeker's Pay-Related Benefit?", "Since 31 March 2025, people who lose their job get up to 60% of their previous earnings (max €450 a week) for the first 13 weeks, falling to 55% and 50%."),
           ("Can I work and get social welfare?", "Sometimes. Jobseeker's payments allow work of up to 3 days a week; One-Parent Family Payment and Disability Allowance have earnings disregards (€175 a week from July 2027)."),
           ("How do I apply?", "Most payments can be claimed on MyWelfare.ie with a verified MyGovID, or at your local Intreo Centre."),
           ("Is this information official?", "No. It's a free, independent guide based on the Department of Social Protection's Budget 2027 figures and Citizens Information. Your entitlement depends on your circumstances.")]
    app.page("faq.html", "Social Welfare FAQ Ireland 2027 – Rates, Christmas Bonus, Payment Dates",
             "Answers about Irish social welfare in 2027: State Pension, Jobseeker's, Carer's Allowance, Child Benefit, Christmas Bonus 2026, Fuel Allowance and Budget 2027 changes.",
             f'<p class="lead">Common questions about social welfare payments in Ireland.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Welfare", "./"), ("FAQ", None)], h1="Social welfare FAQ", sources=("dsp27", "ci_rates27", "ci_xmas"), cross=["salary", "pension", "mortgage"])

# ---------------------------------------------------------------- PRSI extras: Treatment Benefit, PRSI, other supports, entitlement checker
GOV = "https://www.gov.ie/en/department-of-social-protection"
SRC.update({
    "gov_tb": ("gov.ie – Treatment Benefit Scheme (updated 13 October 2026)", GOV + "/services/treatment-benefit-scheme/"),
    "gov_prsi_classes": ("gov.ie – The different classes of PRSI", GOV + "/publications/the-different-classes-of-pay-related-social-insurance-prsi/"),
    "gov_prsi_family": ("gov.ie – PRSI and family employment (benefits covered by each class)", GOV + "/publications/prsi-and-family-employment/"),
    "gov_tsa": ("gov.ie – Telephone Support Allowance", GOV + "/services/telephone-support-allowance/"),
    "gov_anp": ("gov.ie – Additional Needs Payment (updated 7 October 2026)", GOV + "/services/additional-needs-payment/"),
})
TB_WHO = ["You need <strong>PRSI class A, E, P, H or S</strong> contributions – most employees (class A) and the self-employed (class S).",
          "<strong>Under 21:</strong> at least 39 paid contributions at any time.",
          "<strong>Aged 21–28:</strong> 39 paid contributions, plus 39 paid or credited in the <em>governing year</em> (2025 for claims in 2027; 2024 for claims in 2026) – or 26 paid in each of the second and third last years.",
          "<strong>Aged 29–65:</strong> at least <strong>260 paid contributions</strong> (about 5 years' work), plus the same governing-year test.",
          "<strong>66 and over:</strong> 260 paid contributions and enough in the years before you turned 66. Qualify at 60–65 and you <strong>keep it for life</strong>.",
          "Out of work or sick? Credited contributions from Jobseeker's Benefit or Illness Benefit can keep you covered."]
TB_SPOUSE = ("A <strong>spouse, civil partner or cohabitant</strong> who earns <strong>€100 a week or less</strong> and doesn't get a social welfare payment "
             "(Child Benefit, Carer's Benefit and a few others are fine) can claim on your PRSI as a dependant. You both fill in a dependant spouse form, which goes to the Treatment Benefit Section.")
TB_HOW = ["Book with an optician, dentist or hearing aid supplier that's <strong>on the Department's panel</strong> – ask when you book.",
          "Give them your <strong>PPS number and date of birth</strong>. They check online that you qualify <strong>before</strong> treatment.",
          "Sign the consent form. They claim the money from the Department – you only pay any balance.",
          "No application form, no MyWelfare – the provider does it."]
TB_CONTACT = "Treatment Benefit Section, Department of Social Protection, Letterkenny · 0818 300 600 · treatmentenquiries@welfare.ie"
MORE = '<p><a href="free-eye-test.html">Free eye test →</a> · <a href="free-dental-check.html">Free dental check-up →</a> · <a href="hearing-aid-grant.html">Hearing aid grant →</a> · <a href="what-am-i-entitled-to.html">What else am I entitled to? →</a></p>'

def build_prsi_extras():
    cr = [("Welfare", "./"), ("All payments", "all-payments.html")]
    # 1. Treatment Benefit hub
    q = [("What is Treatment Benefit?", "A PRSI benefit that pays for a free eye test, glasses or contact lenses, a free dental check-up, money towards a scale and polish, and up to €500 per hearing aid. Most people who work and pay PRSI qualify."),
         ("How do I know if I qualify for Treatment Benefit?", "Ask your optician, dentist or hearing aid supplier – they check online with your PPS number and date of birth before you're treated. From age 29 you need 260 paid PRSI contributions plus enough in the governing year."),
         ("Is the eye test free with PRSI?", "Yes. You get a free eye test once every second calendar year, and money towards glasses or contact lenses. Basic frames are free."),
         ("Is the dental check-up free with PRSI?", "Yes. One free oral examination every calendar year. The Department pays €50 towards a scale and polish, and the dentist can charge you no more than €15 on top."),
         ("How much is the hearing aid grant?", "Up to €500 per hearing aid (€1,000 for a pair) once every four calendar years, plus up to €100 towards one repair per aid."),
         ("Can my wife or husband use my PRSI?", "Yes, if they're your dependant – earning €100 a week or less and not getting most social welfare payments. You both complete a dependant spouse form."),
         ("Do I need a medical card for this?", "No. Treatment Benefit is based on PRSI, not on income. The medical card is a separate HSE scheme.")]
    rows = [['<a href="free-eye-test.html">Eye test</a>', "Free", "Every 2nd calendar year"],
            ['<a href="free-eye-test.html">Glasses or contact lenses</a>', "Basic frames free, or €42 towards dearer frames", "Every 2nd calendar year"],
            ['<a href="free-dental-check.html">Dental check-up</a>', "Free", "Every calendar year"],
            ['<a href="free-dental-check.html">Scale and polish</a>', "€50 paid – you pay at most €15 more", "Every calendar year"],
            ['<a href="hearing-aid-grant.html">Hearing aids</a>', "Up to €500 each (€1,000 a pair)", "Every 4 calendar years"],
            ['<a href="hearing-aid-grant.html">Hearing aid repair</a>', "Up to €100 per aid", "Once in 4 years"],
            ["Medical contact lenses", "Up to €500 per lens (ophthalmologist's recommendation)", "Every 2nd calendar year"],
            ["Hair replacement (cancer or alopecia)", "Up to €500", "Every calendar year"]]
    body = f"""<p class="lead">If you work and pay PRSI, you've already paid for a free eye test, a free dental check-up and up to €1,000 towards hearing aids. Most people never use them.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{table(["What you get", "How much", "How often"], rows)}
<h2>Who qualifies</h2>{lis(TB_WHO)}
<div class="ad" data-slot="content"></div>
<h2>Your spouse or partner</h2><p>{TB_SPOUSE}</p>
<h2>How to claim</h2>{lis(TB_HOW)}
<p class="muted">{TB_CONTACT}</p>
<div class="cta"><h2>What else are you entitled to?</h2><p>Answer a few questions – see the benefits, payments and tax credits you might be missing.</p><a class="btn" href="what-am-i-entitled-to.html" data-track="cross_app" data-label="tb_to_checker">Check in 1 minute</a></div>
<h2>Questions</h2>{faq_html(q)}"""
    app.page("treatment-benefit.html", "Treatment Benefit 2026 – Free Eye Test, Dental Check & €1,000 Hearing Aids with PRSI",
             "Treatment Benefit in Ireland: a free eye test every 2 years, free dental check-up every year, €50 towards a scale and polish and up to €500 per hearing aid. Who qualifies on PRSI and how to claim.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Treatment Benefit", None)], h1="Treatment Benefit: free eye test, dental and hearing aids",
             sources=("gov_tb",), cross=["taxrefund", "salary"], priority="0.8",
             share_text="If you pay PRSI you can get a free eye test, free dental check-up and up to €1,000 for hearing aids – most people never claim:")

    # 2. Eye test
    q = [("How often can I get a free eye test with PRSI?", "Once every second calendar year – for example once in 2026 and again in 2028."),
         ("Are glasses free with PRSI?", "Basic frames and lenses are free. If you choose more expensive frames, the Department pays €42 towards them and you pay the rest."),
         ("Can I get contact lenses instead of glasses?", "Yes – one pair of glasses or contact lenses (including disposables) every second calendar year, for sight only, not cosmetic lenses."),
         ("Is a driving licence eye test covered?", "No. Sight tests for driving licences or for computer screen (VDU) work aren't covered."),
         ("Can I claim tax relief on glasses?", "Routine eye tests and glasses don't get health expenses tax relief. Use Treatment Benefit instead.")]
    body = f"""<p class="lead">Your PRSI pays for a free eye test every two years and towards glasses or contact lenses. You just need an optician on the Department's panel.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{key_facts(["<strong>Free eye test</strong> once every second calendar year.", "<strong>Glasses</strong>: one pair (reading, distance, bifocal or varifocal) every second calendar year. <strong>Basic frames are free</strong>; €42 towards dearer frames.",
            "Or <strong>contact lenses</strong>, including disposables – for sight, not cosmetic reasons.",
            "<strong>Not covered:</strong> driving licence and computer-screen (VDU) eye tests.", "Medical contact lenses: up to €500 per lens with an ophthalmologist's recommendation."])}
<h2>Do you qualify?</h2>{lis(TB_WHO[:4])}<p><a href="treatment-benefit.html">Full rules, including over-66s and spouses →</a></p>
<div class="ad" data-slot="content"></div>
<h2>How to claim</h2>{lis(TB_HOW)}
<h2>Questions</h2>{faq_html(q)}
{MORE}"""
    app.page("free-eye-test.html", "Free Eye Test with PRSI Ireland 2026 – Free Glasses & Contact Lenses (Treatment Benefit)",
             "Get a free eye test every 2 years with PRSI in Ireland, plus free basic glasses or contact lenses. Who qualifies for Optical Benefit and how to claim at your optician.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Treatment Benefit", "treatment-benefit.html"), ("Free eye test", None)], h1="Free eye test and glasses with PRSI",
             sources=("gov_tb",), cross=["taxrefund", "salary"], priority="0.7")

    # 3. Dental
    q = [("Is the dental check-up free with PRSI?", "Yes – one oral examination every calendar year, paid in full by the Department."),
         ("How much is a scale and polish with PRSI?", "The Department pays €50 and your dentist can charge you at most €15 on top."),
         ("What about gum treatment?", "If clinically necessary, the Department pays €42 towards periodontal treatment instead of a scale and polish. There's no cap on the balance the dentist charges."),
         ("Are fillings covered by PRSI?", "No. Fillings and other treatment aren't covered by Treatment Benefit, but non-routine dental work such as crowns can get 20% tax relief."),
         ("Do all dentists do PRSI check-ups?", "No – only private dentists on the Department's panel. Ask when you book.")]
    body = f"""<p class="lead">Your PRSI pays for a free dental check-up every year and most of a scale and polish.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{key_facts(["<strong>Free oral examination</strong> once every calendar year.", "<strong>Scale and polish:</strong> the Department pays €50 – your dentist can charge you <strong>at most €15</strong> more.",
            "Or <strong>€42</strong> towards periodontal (gum) treatment if clinically necessary.", "Fillings, extractions and other work aren't covered – but <a href='../tax-refund/medical-expenses.html'>non-routine dental work gets 20% tax relief</a>.",
            "Only dentists on the Department's panel – ask when you book."])}
<h2>Do you qualify?</h2>{lis(TB_WHO[:4])}<p><a href="treatment-benefit.html">Full rules, including over-66s and spouses →</a></p>
<div class="ad" data-slot="content"></div>
<h2>How to claim</h2>{lis(TB_HOW)}
<h2>Questions</h2>{faq_html(q)}
{MORE}"""
    app.page("free-dental-check.html", "Free Dental Check-Up with PRSI Ireland 2026 – Scale & Polish for €15 (Treatment Benefit)",
             "Free dental check-up every year with PRSI in Ireland, and a scale and polish for at most €15. Who qualifies for Dental Benefit and how to claim.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Treatment Benefit", "treatment-benefit.html"), ("Free dental check-up", None)], h1="Free dental check-up with PRSI",
             sources=("gov_tb",), cross=["taxrefund", "salary"], priority="0.7")

    # 4. Hearing aids
    q = [("How much is the hearing aid grant in Ireland?", "Up to €500 per hearing aid – €1,000 for a pair – once every four calendar years, through Treatment Benefit."),
         ("Can I get hearing aid repairs paid for?", "Yes – one repair per aid in a four-year period, up to €100 per aid."),
         ("Do I need a medical card for a hearing aid grant?", "No. Treatment Benefit is based on your PRSI. Medical card holders can get hearing aids through the HSE instead."),
         ("Can I claim tax relief on the rest?", "Yes. Hearing aids qualify for 20% health expenses tax relief on the amount you pay yourself after the grant."),
         ("Where do I get the grant?", "From a hearing aid supplier with a contract with the Department. They check you qualify and claim the €500 for you.")]
    body = f"""<p class="lead">If you've paid PRSI, the Department pays up to €500 per hearing aid – €1,000 for a pair – every four years.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
<div class="hero-num"><div><span class="tl">Per hearing aid</span><strong>€500</strong><span class="muted">every 4 years</span></div><div><span class="tl">For a pair</span><strong>€1,000</strong><span class="muted">every 4 years</span></div></div>
{key_facts(["Up to <strong>€500 towards each hearing aid</strong>, once every four calendar years.", "Plus <strong>one repair per aid</strong> in four years, up to <strong>€100</strong> per aid.",
            "Only from suppliers with a contract with the Department – they check and claim for you.", "Pay more than €500? Claim <a href='../tax-refund/can-i-claim-hearing-aids.html'>20% tax relief</a> on what you paid yourself."])}
<h2>Do you qualify?</h2>{lis(TB_WHO)}
<div class="ad" data-slot="content"></div>
<h2>How to claim</h2>{lis(TB_HOW)}
<h2>Questions</h2>{faq_html(q)}
{MORE}"""
    app.page("hearing-aid-grant.html", "Hearing Aid Grant Ireland 2026 – €500 per Aid (€1,000 a Pair) with PRSI",
             "Hearing aid grant in Ireland: up to €500 per hearing aid (€1,000 a pair) every 4 years and €100 towards repairs through Treatment Benefit. Who qualifies and how to claim.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Treatment Benefit", "treatment-benefit.html"), ("Hearing aid grant", None)], h1="Hearing aid grant: €500 per aid",
             sources=("gov_tb",), cross=["taxrefund", "pension"], priority="0.7")

    # 5. What does PRSI pay for
    rows = [["State Pension (Contributory)", "✅", "✅"], ["Maternity, Paternity, Parent's and Adoptive Benefit", "✅", "✅"], ["Treatment Benefit (eye, dental, hearing)", "✅", "✅"],
            ["Invalidity Pension", "✅", "✅"], ["Partial Capacity Benefit", "✅", "✅"], ["Carer's Benefit", "✅", "✅ (from 2025)"], ["Widow's, Widower's or Surviving Civil Partner's Pension", "✅", "✅"],
            ["Guardian's Payment (Contributory)", "✅", "✅"], ["Jobseeker's Benefit", "✅", "Jobseeker's Benefit (Self-Employed)"], ["Benefit for 65 year olds", "✅", "✅"],
            ["Illness Benefit", "✅", "❌"], ["Occupational Injuries (accidents at work)", "✅", "❌"]]
    q = [("What does PRSI pay for in Ireland?", "Class A PRSI (most employees) covers every social insurance benefit: State Pension (Contributory), Jobseeker's Benefit, Illness Benefit, Maternity and Paternity Benefit, Treatment Benefit and more."),
         ("What benefits do self-employed people get from PRSI?", "Class S covers the State Pension (Contributory), Maternity, Paternity, Parent's and Adoptive Benefit, Treatment Benefit, Invalidity Pension, Partial Capacity Benefit, Carer's Benefit, Jobseeker's Benefit (Self-Employed) and others – but not Illness Benefit."),
         ("What PRSI class am I?", "Most employees earning €38 a week or more are Class A. Self-employed people with income of €5,000 or more a year are Class S. Your class is on your payslip."),
         ("How do I check my PRSI contributions?", "Log in to MyWelfare.ie with your MyGovID and request a statement of your social insurance record.")]
    body = f"""<p class="lead">Every week you pay PRSI, you're paying for benefits – a pension, sick pay, parent's leave pay, a free eye test. Here's what your class gets you.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{key_facts(["<strong>Class A</strong> – most employees (pay of €38 a week or more): covers <strong>all</strong> social insurance benefits and pensions.",
            "<strong>Class S</strong> – self-employed, farmers, some company directors (income €5,000+ a year): covers most benefits but <strong>not Illness Benefit</strong>.",
            "Easy to miss: <strong>Treatment Benefit</strong> – a <a href='free-eye-test.html'>free eye test</a>, <a href='free-dental-check.html'>free dental check-up</a> and <a href='hearing-aid-grant.html'>up to €1,000 for hearing aids</a>.",
            "Check your record any time on <strong>MyWelfare.ie</strong>."])}
<h2>What Class A and Class S cover</h2>{table(["Benefit", "Class A (employees)", "Class S (self-employed)"], rows)}
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(q)}
<div class="cta"><h2>How much PRSI do you pay?</h2><p>See your PRSI, tax and USC on any salary.</p><a class="btn" href="../salary/" data-track="cross_app" data-label="prsi_to_salary">Take-home pay calculator</a></div>"""
    app.page("what-does-prsi-cover.html", "What Does PRSI Pay For? Benefits by PRSI Class (A and S) Ireland 2026",
             "What your PRSI gets you in Ireland: Class A covers every benefit (pension, Illness, Jobseeker's, Maternity, Treatment Benefit); Class S self-employed cover explained.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("What PRSI pays for", None)], h1="What does PRSI pay for?",
             sources=("gov_prsi_family", "gov_prsi_classes", "gov_tb", "mywelfare"), cross=["salary", "pension", "taxrefund"], priority="0.7")

    # 6. Telephone Support Allowance
    q = [("How much is Telephone Support Allowance?", "€2.50 a week – €130 a year – on top of your main payment, Living Alone Increase and Fuel Allowance."),
         ("Do I need to apply for Telephone Support Allowance?", "No. It's paid automatically if you get a qualifying payment plus both the Living Alone Increase and Fuel Allowance."),
         ("I think I qualify but don't get it – what do I do?", "Contact the office that pays your main payment: Longford (0818 927 770) for Disability Allowance, Invalidity or Blind Pension; Sligo (0818 200 400) for the State Pension.")]
    body = f"""<p class="lead">An extra €2.50 a week for people who live alone and get Living Alone Increase and Fuel Allowance – paid automatically.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{key_facts(["<strong>€2.50 a week</strong> (€130 a year), on top of your main payment.", "You must get <strong>both</strong> the <a href='living-alone-increase.html'>Living Alone Increase</a> and <a href='fuel-allowance.html'>Fuel Allowance</a>.",
            "Plus one of: State Pension (Contributory or Non-Contributory), Bereaved Partner's Pension, Invalidity Pension, Disability Allowance, Blind Pension, Incapacity Supplement or Deserted Wife's Benefit.",
            "<strong>No form</strong> – it's paid automatically. Missing? Ring Longford (0818 927 770) or Sligo (0818 200 400)."])}
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(q)}
<p><a href="household-benefits-package.html">Household Benefits Package →</a> · <a href="what-am-i-entitled-to.html">What else am I entitled to? →</a></p>"""
    app.page("telephone-support-allowance.html", "Telephone Support Allowance Ireland – €2.50 a Week, Who Qualifies",
             "Telephone Support Allowance: €2.50 a week (€130 a year) for people living alone who get Living Alone Increase and Fuel Allowance. Paid automatically – who qualifies.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Telephone Support Allowance", None)], h1="Telephone Support Allowance",
             sources=("gov_tsa",), cross=["pension", "salary"], priority="0.6")

    # 7. Additional Needs Payment
    q = [("What is the Additional Needs Payment?", "A once-off payment from the Community Welfare Service for an essential cost you can't pay from your weekly income or savings – such as a big heating bill, a rent deposit or a funeral. It used to be called the Exceptional Needs Payment."),
         ("Can I get an Additional Needs Payment if I'm working?", "Yes. You don't need to be on social welfare – people working on a low income can qualify, however many hours they work."),
         ("How much is the Additional Needs Payment?", "There's no set rate. A Community Welfare Officer looks at your household income, savings, expenses and the cost you need help with."),
         ("How do I apply?", "Online at MyWelfare.ie, or with form SWA1 at any Intreo Centre or Branch Office. Phone 0818 607080 for help.")]
    body = f"""<p class="lead">Big bill you can't cover? The Additional Needs Payment helps with essential once-off costs – and you don't have to be on social welfare.</p>
<p class="updated">gov.ie · Checked {CHECKED}</p>
{key_facts(["For <strong>anyone on social welfare or a low income</strong> – working people can apply too.", "<strong>No set amount</strong>: a Community Welfare Officer looks at your income, savings and the cost.",
            "Apply on <strong>MyWelfare.ie</strong> or at an Intreo office (form SWA1). Help line: <strong>0818 607080</strong>.", "It replaced the <strong>Exceptional Needs Payment</strong>."])}
<h2>What it can help with</h2>{lis(["Heating and electricity bills", "Essential repairs, and replacing appliances or furniture", "A <strong>deposit</strong> for private rented accommodation", "Setting up a home for the first time",
    "Funeral costs", "Regular travel to hospital appointments or to visit relatives in hospital", "Prams, buggies, cots and child safety equipment", "Food, clothes and accommodation after an emergency such as a house fire"])}
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(q)}
<p><a href="supplementary-welfare-allowance.html">Supplementary Welfare Allowance →</a> · <a href="what-am-i-entitled-to.html">What else am I entitled to? →</a></p>"""
    app.page("additional-needs-payment.html", "Additional Needs Payment Ireland 2026 – Help with Bills, Deposits & Funerals (Exceptional Needs)",
             "Additional Needs Payment (formerly Exceptional Needs Payment): once-off help with heating bills, rent deposits, funerals and essential costs – for people on welfare or a low income. How to apply.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("Additional Needs Payment", None)], h1="Additional Needs Payment",
             sources=("gov_anp", "ci_supplementary-welfare-allowance"), cross=["rent", "salary"], priority="0.7")

    # 8. Entitlement checker (logic in welfare/js/entitled.js)
    qs = [("prsi", "Do you work and pay PRSI – or did in the last 2 years?"), ("spouse", "Does your spouse or partner pay PRSI while you earn €100 a week or less?"),
          ("rent", "Do you rent privately (not on HAP, RAS or Rent Supplement)?"), ("medical", "Have you paid for GP visits, prescriptions, a consultant or non-routine dental work since 2022?"),
          ("kids", "Do you have children under 18?"), ("lowpay", "Do you (or your partner) work at least 19 hours a week on a low income, with children?"),
          ("carer", "Do you care for someone full-time?"), ("age66", "Are you 66 or over?"), ("alone", "Do you live alone and get a pension or disability payment?"),
          ("bill", "Do you have a big essential cost you can't pay – a heating bill, deposit, funeral or appliance?")]
    form = "".join(f'<fieldset class="ent-q"><legend>{t}</legend><label><input type="radio" name="{k}" value="y"> Yes</label> <label><input type="radio" name="{k}" value="n" checked> No</label></fieldset>' for k, t in qs)
    q = [("What benefits am I entitled to in Ireland?", "It depends on your PRSI, family, age and income. Most workers can get a free eye test and dental check-up through Treatment Benefit; renters can claim the Rent Tax Credit; families get Child Benefit. Use the checker above to see yours."),
         ("What benefits do workers miss most often?", "Treatment Benefit (free eye test, dental check and hearing aid grant), the Rent Tax Credit, medical expenses tax relief and Working Family Payment for low-paid parents."),
         ("Is this checker official?", "No. It's a free, independent guide. Your entitlement depends on your full circumstances – confirm with the Department of Social Protection or Revenue.")]
    body = f"""<p class="lead">Answer 10 quick questions and see the benefits, payments and tax credits you might be missing – free, no sign-up, nothing stored.</p>
<form id="entForm" class="ent-form">{form}<button type="submit" class="btn">Show what I could get</button></form>
<div id="entOut" aria-live="polite"></div>
<div class="ad" data-slot="content"></div>
<h2>Questions</h2>{faq_html(q)}"""
    app.page("what-am-i-entitled-to.html", "What Am I Entitled To? Free Irish Benefits Checker 2026 – Welfare, PRSI & Tax Credits",
             "Free checker: answer 10 questions and see the Irish benefits you could be missing – free eye test and dental check with PRSI, Rent Tax Credit, Child Benefit, Working Family Payment, Carer's and more.",
             body, active="All payments", jsonld=[faq_ld(q)], crumbs=cr + [("What am I entitled to?", None)], h1="What am I entitled to?", scripts=["js/entitled.js"],
             sources=("gov_tb", "gov_anp", "gov_tsa", "dsp27", "ci_rates27"), cross=["taxrefund", "salary", "rent"], priority="0.9",
             share_text="Free checker: see the Irish benefits and tax credits you might be missing (most workers can get a free eye test and dental check):")

import re
# ---------------------------------------------------------------- engagement: next step + quick checks
from sitekit import quick_check
def _welfare_next(fn):
    if fn == "index.html": return None
    X = ("Your Christmas Bonus 2026", "Paid in the week of 7 December – check if you qualify", "christmas-bonus.html", "welfare_xmas")
    D = ("Christmas and New Year payment dates", "Early payments and the January gap", "christmas-payment-dates.html", "welfare_xmasdates")
    key = fn[:-5]
    C = ("What will you get from January 2027?", "Your rate with a partner, children, Living Alone and Fuel", "./" + ("?p=" + key if key in P else ""), "welfare_calc")
    L = ("Is there an autumn bonus or lump sum this year?", "What is – and isn't – being paid", "lump-sum-payments.html", "welfare_lumps")
    order = [X, C] if key in P else [X, D, C, L]
    return [i for i in order if i[2] != fn][:2]
app.next_for = _welfare_next
_XQ = quick_check("xmas_qualify", "Which payment do you get?", [
    ("State Pension", "✅ Yes – you get the 100% Christmas Bonus in the week of 7 December 2026, with your normal payment."),
    ("Disability / Carer's", "✅ Yes – Disability Allowance, Invalidity Pension, Carer's Allowance (including half-rate) and Carer's Benefit all get the Christmas Bonus."),
    ("One-Parent / JST", "✅ Yes – One-Parent Family Payment and Jobseeker's Transitional Payment both qualify straight away."),
    ("Jobseeker's Allowance", "⏳ Only if you've been getting it for 12 months (312 days) or more by the bonus week."),
    ("Jobseeker's Benefit", "❌ No – Jobseeker's Benefit and Pay-Related Benefit don't get the Christmas Bonus (but you may still get two weeks paid together before Christmas)."),
    ("Child Benefit only", "❌ No – Child Benefit doesn't get a Christmas double payment. December's payment is on Tuesday 1 December.")])
app.checks = {"christmas-payment-dates.html": _XQ, "payment-dates.html": _XQ, "lump-sum-payments.html": _XQ,
    "fuel-allowance-payment-dates.html": quick_check("fuel_qualify", "Are you 66 or over?", [
        ("Yes", "You can get Fuel Allowance without another payment if you pass the means test – €653 a week for a single person from January 2027 (€534 now). <a href='fuel-allowance.html'>Who qualifies →</a>"),
        ("No", "You need a qualifying long-term payment (such as Disability Allowance, One-Parent Family Payment, Carer's Allowance or Jobseeker's Allowance after 12 months) and to pass the means test. <a href='fuel-allowance.html'>Full list →</a>")])}

if __name__ == "__main__":
    build_index(); payment_pages(); build_hubs(); build_xmas(); build_xmas_dates(); build_dates(); build_extras(); build_prsi_extras(); build_faq()
    og_image(os.path.join(app.root, "og.png"), "BUDGET 2027", "Social welfare", "rates 2027", "State Pension · Jobseeker's · Carer's · Child Benefit", "Christmas Bonus 2026 · payment dates",
             "tavion.ie/welfare  ·  free, no sign-up", (125, 211, 252), (3, 105, 161), (5, 40, 60))
    app.update_sitemap()
    app.update_llms("- [Irish Social Welfare Rates 2027](https://tavion.ie/welfare/): Budget 2027 weekly rates for every payment (State Pension €309.30, Jobseeker's €264, Carer's €280, Disability €264), Christmas Bonus 2026, Child Benefit dates and a calculator.",
                    "Social welfare: key facts",
                    """- Budget 2027: +€10 a week on most payments from January 2027. State Pension (Contributory) €309.30 (€319.30 at 80+); Non-Contributory €298; Jobseeker's Allowance/Benefit, Illness Benefit, Disability Allowance, One-Parent Family Payment €264; Carer's Allowance €280 (€318 at 66+); Invalidity Pension €269.50; Maternity/Paternity/Parent's Benefit €309.
- Child Support Payment €64 (under 12) / €84 (12+); Child Benefit €140 a month (unchanged), first Tuesday of each month; Fuel Allowance €43; Living Alone Increase €25; €500 Cost of Disability payment in 2027.
- Christmas Bonus 2026: 100% of the weekly payment, minimum €20, week starting 7 December 2026, long-term payments only (not Fuel Allowance).
- Jobseeker's Pay-Related Benefit (unemployed from 31 March 2025): 60% of earnings up to €450 (weeks 1-13), 55% up to €375 (14-26), 50% up to €300 (27-39); minimum €125.
- Pages: [Calculator](https://tavion.ie/welfare/), [Rates 2027](https://tavion.ie/welfare/rates-2027.html), [Christmas Bonus](https://tavion.ie/welfare/christmas-bonus.html), [Child Benefit dates](https://tavion.ie/welfare/child-benefit-payment-dates.html), [All payments](https://tavion.ie/welfare/all-payments.html). Source: Department of Social Protection Budget 2027 factsheet, Citizens Information.""")
    print("Built", len(app.files), "pages in", app.root)
