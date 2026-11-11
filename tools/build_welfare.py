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
        '<a href="payment-dates.html">Payment dates</a><a href="all-payments.html">All payments</a><a href="budget-2027.html">Budget 2027 changes</a><a href="faq.html">FAQ</a>')
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
 "fuel-allowance": dict(what="A weekly payment during the heating season for people on long-term welfare payments who can't afford heating.", who=["Getting a qualifying long-term payment (or Working Family Payment)", "Living alone or only with other qualifying people", "Pass a means test – improved for single pensioners from 2027"], dur="28 weeks, from late September to April.", tip="€43 a week from January 2027 – over €1,200 for the season.", rel=["living-alone-increase", "state-pension-contributory", "working-family-payment"]),
 "living-alone-increase": dict(what="An extra weekly amount for people on certain payments who live alone.", who=["Getting a State Pension, Disability Allowance, Invalidity Pension, Blind Pension or certain other payments", "Living alone"], dur="Paid with your main payment.", tip="Budget 2027 raises it to €25 a week – the first increase in five years.", rel=["state-pension-contributory", "fuel-allowance", "disability-allowance"]),
 "cost-of-disability-payment": dict(what="A new once-off €500 payment in 2027 for people getting a long-term disability payment.", who=["Getting a long-term disability payment (details from the Department in 2027)"], dur="Once-off lump sum in 2027.", tip="The first ever Cost of Disability payment – further design will be co-designed with disabled people.", rel=["disability-allowance", "invalidity-pension", "blind-pension"]),
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
        facts = ([f"<strong>{p['name']}</strong> is <strong>{r27}</strong> from January 2027" + (f", up from {r26} in 2026 (+{eur(diff, 2 if diff % 1 else 0)})." if diff else ".")] if p["r27"] is not None else []) +                 [info["what"], "How long: " + info["dur"]]
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
<div class="hero-num"><div><span class="tl">2026</span><strong>{r26}</strong></div><div><span class="tl">From January 2027</span><strong>{r27}</strong></div></div>
{extra}
{('<h2>What you get, by family (weekly)</h2>' + table(["Situation", "2026", "2027 per week", "2027 per month", "2027 per year"], rows) + '<p class="muted small">Includes the Child Support Payment (€64 under 12, €84 aged 12+ in 2027). 2026 family figures shown only where the 2026 rate is confirmed.</p>') if rows else ''}
<div class="ad" data-slot="content"></div>
<h2>Who can get {p['name']}?</h2>{lis(info['who'])}
<h2>How long is it paid?</h2><p>{info['dur']}</p>
<h2>Tip</h2><div class="callout">{info['tip']}</div>
<h2>How to apply</h2><p>Most payments can be claimed online on <a href="https://services.mywelfare.ie/" rel="noopener" target="_blank">MyWelfare.ie</a> with a verified MyGovID, or at your local Intreo Centre.</p>
<div class="cta"><h2>Work out your total</h2><p>Add a partner, children, Living Alone Increase and Fuel Allowance.</p><a class="btn" href="./?p={key}" data-track="welfare_page_cta" data-label="{key}">Open the calculator</a></div>
<h2>Related payments</h2><div class="chip-list">{rel}<a href="all-payments.html">All payments →</a></div>"""
        faqs = ([(f"How much is {p['name']} in 2027?", f"{r27} from January 2027" + (f", up {eur(diff, 2 if diff % 1 else 0)} from {r26} in 2026." if diff else "."))] if p["r27"] is not None else []) + [
                (f"Who qualifies for {p['name']}?", "; ".join(info["who"]) + "."),
                (f"Do you get the Christmas Bonus on {p['name']}?", ("Yes – 100% of your weekly payment, paid in the week starting 7 December 2026" + (", once you've been getting it for 12 months." if p['xmas'] == '12m' else ".")) if p.get("xmas") else "No, it isn't a qualifying payment for the Christmas Bonus.")]
        srcs = ci_src(key) + ["dsp27", "ci_rates27"] + (["ci_xmas"] if p.get("xmas") else []) + ["mywelfare"]
        app.page(f"{key}.html", f"{p['name']} 2027 Rate Ireland – {r27} | Who Qualifies & Christmas Bonus",
                 f"{p['name']} is {r27} from January 2027 (Budget 2027). Who qualifies, how long it's paid, family rates and whether you get the Christmas Bonus.",
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
<div class="cta"><h2>🎄 Christmas Bonus 2026</h2><p>A double payment in the week starting 7 December. See if you qualify and how much you'll get.</p><a class="btn" href="christmas-bonus.html">Check my Christmas Bonus</a></div>"""
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
    body += "<h2>Other supports</h2><div class='stamp-grid'><a class='stamp-card' href='back-to-school-allowance.html'><strong>Back to School Clothing and Footwear Allowance</strong><p>€160 / €285 per child</p></a><a class='stamp-card' href='household-benefits-package.html'><strong>Household Benefits Package &amp; Free Travel</strong><p>For pensioners and people with disabilities</p></a><a class='stamp-card' href='christmas-bonus.html'><strong>Christmas Bonus</strong><p>100% double week, December 2026</p></a></div>"
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
            "<strong>Fuel Allowance €43</strong> a week (+€5) – over €1,200 for the season; better means test for single pensioners.", "<strong>Living Alone Increase €25</strong> (+€3).",
            "Working Family Payment thresholds up <strong>€30</strong> a week.", "<strong>Christmas Bonus</strong> (100%) to almost 1.4 million people in December 2026.", "No change to Child Benefit (€140)."])}
<h2>From July 2027</h2>{lis(["Disability Allowance and Blind Pension earnings disregard up to €175 a week", "One-Parent Family Payment and Jobseeker's Transitional Payment earnings disregard up to €175",
    "Carer's Allowance income disregards up to €1,150 (single) and €2,300 (couple)", "Increase for a Qualified Adult income threshold from €310 to €340", "Farm Assist / State Pension (Non-Contributory): agri-environmental disregard €7,500"])}
<div class="cta"><h2>Your new rate</h2><p>See exactly what you'll get from January.</p><a class="btn" href="./">Open the calculator</a></div>
<p>Budget 2027 also changed income tax – <a href="../salary/budget-2027.html">see how your take-home pay changes</a>.</p>"""
    app.page("budget-2027.html", "Budget 2027 Social Welfare Changes – €10 Increase, Christmas Bonus, Fuel Allowance",
             "Budget 2027 social welfare: €10 a week more from January 2027, €500 Cost of Disability payment, Child Support Payment €64/€84, Fuel Allowance €43, Living Alone €25, Christmas Bonus.",
             body, active="Budget 2027", crumbs=[("Welfare", "./"), ("Budget 2027", None)], h1="Budget 2027: social welfare changes", sources=("dsp27", "gov27", "ci_rates27"), cross=["salary", "pension", "mortgage"], priority="0.9")

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
<h2>Who doesn't get it</h2>{lis(["Fuel Allowance on its own", "Jobseeker's Benefit / Pay-Related Benefit", "Short-term Illness Benefit (under 12 months)", "Child Benefit (no Christmas double payment)", "Maternity, Paternity and Parent's Benefit"])}
<div class="cta"><h2>Your 2027 rate</h2><p>See what you'll get from January after the €10 increase.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("When is the Christmas Bonus 2026 paid?", "In the week starting Monday 7 December 2026, on the day you normally get your payment."),
            ("How much is the Christmas Bonus 2026?", "100% of your normal weekly social welfare payment, with a minimum of €20."),
            ("Do I need to apply for the Christmas Bonus?", "No. It's paid automatically if you're getting a qualifying long-term payment."),
            ("Is Child Benefit doubled at Christmas?", "No. Child Benefit isn't a qualifying payment for the Christmas Bonus.")]
    app.page("christmas-bonus.html", "Christmas Bonus 2026 Ireland – Date (Week of 7 December), Amount & Who Qualifies",
             "Social welfare Christmas Bonus 2026: a 100% double payment in the week starting 7 December 2026. Check if you qualify and how much you'll get, payment by payment.",
             body, active="Christmas Bonus", jsonld=[faq_ld(faqs)], slot="calculator", scripts=["js/welfare.js", "js/calc.js"], crumbs=[("Welfare", "./"), ("Christmas Bonus", None)],
             h1="🎄 Christmas Bonus 2026", sources=("ci_xmas", "dsp27", "gov27"), cross=["salary", "rent", "pension"], priority="0.9",
             share_text="🎄 Christmas Bonus 2026 – double payment in the week of 7 December. Check what you'll get:")

def build_dates():
    d26, d27 = run([{"k": "cb", "y": 2026}, {"k": "cb", "y": 2027}])
    def nice(s):
        dt = datetime.date.fromisoformat(s); return f"{dt.strftime('%A')} {dt.day} {dt.strftime('%B %Y')}"
    rows = [[datetime.date.fromisoformat(a).strftime("%B"), nice(a), nice(b)] for a, b in zip(d26, d27)]
    nxt = next((x for x in d26 + d27 if datetime.date.fromisoformat(x) >= TODAY), d27[0])
    body = f"""<p class="lead">Child Benefit is paid on the <strong>first Tuesday of every month</strong>. Here are all the payment dates for 2026 and 2027.</p>
<p class="updated">Checked {CHECKED}</p>
<div class="earliest"><div class="tl">Next Child Benefit payment</div><div class="ed">{nice(nxt)}</div><div>€140 per child</div></div>
{key_facts(["Child Benefit is <strong>€140 a month</strong> per child in 2026 and 2027 – no change in Budget 2027.", "Paid on the first Tuesday of each month into your bank account or at the post office.",
            "Twins get 1.5 times the rate per child; triplets and more get double.", "There's no Christmas double payment of Child Benefit."])}
{table(["Month", "2026", "2027"], rows)}
<p class="muted small">Calculated as the first Tuesday of each month. If a payment day falls on a public holiday the Department may pay on a different day – check your bank or the Department.</p>
<div class="ad" data-slot="content"></div>
<p>Also for families: <a href="child-support-payment.html">Child Support Payment</a> · <a href="working-family-payment.html">Working Family Payment</a> · <a href="back-to-school-allowance.html">Back to School Allowance</a> · <a href="one-parent-family-payment.html">One-Parent Family Payment</a></p>"""
    app.page("child-benefit-payment-dates.html", "Child Benefit Payment Dates 2026 & 2027 Ireland – First Tuesday of Every Month",
             f"Child Benefit payment dates for 2026 and 2027: paid on the first Tuesday of every month at €140 per child. Next payment: {nice(nxt)}.",
             body, active="Payment dates", jsonld=[faq_ld([("When is Child Benefit paid?", "On the first Tuesday of every month."), ("How much is Child Benefit in 2027?", "€140 per child per month – unchanged in Budget 2027.")])],
             crumbs=[("Welfare", "./"), ("Payment dates", "payment-dates.html"), ("Child Benefit dates", None)], h1="Child Benefit payment dates 2026 and 2027",
             sources=("ci_child-benefit", "dsp27"), cross=["salary", "mortgage", "rent"], priority="0.9")

    body = f"""<p class="lead">When are social welfare payments paid in Ireland – and what happens around Christmas, the New Year and bank holidays?</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Most weekly payments are paid on the <strong>same day every week</strong> – the day is shown on your payment notice (it depends on the payment and how you're paid).",
            "<strong>Child Benefit</strong>: first Tuesday of each month. <a href='child-benefit-payment-dates.html'>All dates</a>.",
            "<strong>Christmas Bonus</strong>: week starting 7 December 2026, with your normal payment.",
            "<strong>New rates</strong>: Budget 2027 increases start from your first payment in January 2027.",
            "<strong>Bank holidays</strong> (Christmas Day Friday 25 December, St Stephen's Day Saturday 26 December, New Year's Day Friday 1 January 2027): payments due on a bank holiday are usually paid early. The Department publishes the exact Christmas schedule – check gov.ie or your post office."])}
<h2>Key dates</h2>{table(["Date", "What happens"], [["Week of 7 December 2026", "Christmas Bonus (100%) paid with your normal payment"], ["Tuesday 1 December 2026", "Child Benefit"],
    ["Friday 25 December 2026", "Christmas Day – bank holiday"], ["Friday 1 January 2027", "New Year's Day – bank holiday"], ["First payment in January 2027", "Budget 2027 increases start (+€10 on most payments)"],
    ["Tuesday 5 January 2027", "Child Benefit (€140)"], ["Late September 2027", "Fuel Allowance season begins"]])}
<div class="ad" data-slot="content"></div>
<p>All Irish bank holidays: <a href="../salary/public-holidays.html">bank holidays 2026 and 2027 →</a></p>"""
    app.page("payment-dates.html", "Social Welfare Payment Dates 2026–2027 Ireland – Christmas, New Year & Bank Holidays",
             "When social welfare is paid in Ireland: weekly payment days, Child Benefit dates, Christmas Bonus week of 7 December 2026, bank holiday changes and when Budget 2027 rates start.",
             body, active="Payment dates", crumbs=[("Welfare", "./"), ("Payment dates", None)], h1="Social welfare payment dates", sources=("ci_xmas", "ci_child-benefit", "dsp27"), cross=["salary", "rent"], priority="0.8")

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
           ("What is the Cost of Disability payment?", "A new once-off €500 payment in 2027 for people on a long-term disability payment."),
           ("How much is Fuel Allowance in 2027?", "€43 a week during the season – over €1,200 in total."),
           ("What is Jobseeker's Pay-Related Benefit?", "Since 31 March 2025, people who lose their job get up to 60% of their previous earnings (max €450 a week) for the first 13 weeks, falling to 55% and 50%."),
           ("Can I work and get social welfare?", "Sometimes. Jobseeker's payments allow work of up to 3 days a week; One-Parent Family Payment and Disability Allowance have earnings disregards (€175 a week from July 2027)."),
           ("How do I apply?", "Most payments can be claimed on MyWelfare.ie with a verified MyGovID, or at your local Intreo Centre."),
           ("Is this information official?", "No. It's a free, independent guide based on the Department of Social Protection's Budget 2027 figures and Citizens Information. Your entitlement depends on your circumstances.")]
    app.page("faq.html", "Social Welfare FAQ Ireland 2027 – Rates, Christmas Bonus, Payment Dates",
             "Answers about Irish social welfare in 2027: State Pension, Jobseeker's, Carer's Allowance, Child Benefit, Christmas Bonus 2026, Fuel Allowance and Budget 2027 changes.",
             f'<p class="lead">Common questions about social welfare payments in Ireland.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Welfare", "./"), ("FAQ", None)], h1="Social welfare FAQ", sources=("dsp27", "ci_rates27", "ci_xmas"), cross=["salary", "pension", "mortgage"])

if __name__ == "__main__":
    build_index(); payment_pages(); build_hubs(); build_xmas(); build_dates(); build_extras(); build_faq()
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
