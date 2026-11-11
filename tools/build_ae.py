"""
Builds the Auto-Enrolment (MyFutureFund) app (tavion.ie/auto-enrolment/).
Run from the repo root:   python tools/build_ae.py      (needs Node.js)
All figures come from auto-enrolment/js/ae.js (+ salary/js/tax.js for take-home pay).
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, eur, lis, table, faq_ld, faq_html, key_facts, node, og_image, TODAY

ENGINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "auto-enrolment", "js", "ae.js"))
CHECKED = "November 2026"
YEAR = 2026
SALARIES = list(range(20000, 100001, 5000)) + [120000, 150000]
AGES = [23, 25, 30, 35, 40, 45, 50, 55, 60]
SRC = {
    "ci": ("Citizens Information – Auto-enrolment pension – MyFutureFund", "https://www.citizensinformation.ie/en/money-and-tax/personal-finance/pensions/auto-enrolment/"),
    "mff": ("MyFutureFund – official site (NAERSA)", "https://myfuturefund.ie/"),
    "mff_guide": ("MyFutureFund – participant handbook", "https://myfuturefund.ie/participant-guide"),
    "mff_faq": ("MyFutureFund – participant FAQ", "https://myfuturefund.ie/participant-faq"),
    "rte_opt": ("RTÉ – Opt-out window opens for auto-enrolment pension scheme", "https://www.rte.ie/news/2026/0701/1581154-pension-auto-enrolment/"),
    "it_opt": ("Irish Times – Workers can opt out of auto-enrolment from July", "https://www.irishtimes.com/your-money/2026/06/01/workers-signed-up-to-states-auto-enrolment-pension-scheme-can-opt-out-from-next-month/"),
    "pensions": ("Pensions Authority – pension information", "https://www.pensionsauthority.ie/"),
}
NODE = r"""
const A = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "c" ? A.contributions(x.s, x.y) : x.k === "p" ? A.project(x.o) : x.k === "i" ? A.payImpact(x.s, x.y) : x.k === "e" ? A.eligibility(x.o) : null);
  process.stdout.write(JSON.stringify({ stages: A.stageYears(), res: res }));
});
"""
META = node(ENGINE, NODE, [])
STG = META["stages"]
def run(q): return node(ENGINE, NODE, q)["res"]
def pct(x): return f"{x * 100:g}%"

TABS = [("./", "Calculator"), ("contribution-rates.html", "Rates by year"), ("by-salary.html", "By salary"), ("opt-out.html", "Opt out"),
        ("am-i-enrolled.html", "Am I enrolled?"), ("retirement.html", "At 66"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Auto-enrolment calculator</a><a href="contribution-rates.html">Contribution rates by year</a><a href="by-salary.html">By salary</a><a href="by-age.html">By age</a>'
        '<a href="opt-out.html">Opting out</a><a href="am-i-enrolled.html">Am I enrolled?</a><a href="vs-workplace-pension.html">vs workplace pension</a><a href="retirement.html">Taking it at 66</a><a href="faq.html">FAQ</a>')
app = App("auto-enrolment", "Auto-Enrolment Pension", "🌱", None, "#15803d", TABS, FOOT, SRC, None,
          "Auto-enrolment (MyFutureFund) calculator – what you pay, what's added and what you could have at 66:", "Know someone who's just been auto-enrolled? Send them this.", "pension",
          f"Rules checked against Citizens Information and MyFutureFund (NAERSA) in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>, not affiliated with NAERSA or the Government. Projections are illustrations, not guarantees – investments can go down as well as up. This is not financial advice.")
CROSS = ["salary", "welfare", "mortgage", "rent"]
STAGE_ROWS = [[f"{s['from']}–{s['to']}" if s["to"] else f"{s['from']} onwards", pct(s["employee"]), pct(s["employer"]), pct(s["state"]), pct(s["employee"] + s["employer"] + s["state"])] for s in STG]

def build_index():
    body = f"""<p class="lead">You've been auto-enrolled in MyFutureFund – or will be. See what comes out of your pay, what your employer and the State add, and what you could have at 66. Free, no sign-up.</p>
<ul class="facts"><li>You 1.5% · Employer 1.5% · State 0.5%</li><li>Rising to 6% / 6% / 2%</li><li>Ages 23–60, €20,000+</li></ul>
<form id="aeForm" class="card" novalidate>
  <label for="salary" class="big-label">Your gross salary per year</label>
  <div class="money"><span>€</span><input id="salary" type="text" inputmode="decimal" autocomplete="off" placeholder="40,000"></div>
  <label for="age" class="big-label" style="margin-top:14px">Your age</label>
  <input id="age" type="number" min="16" max="70" inputmode="numeric" placeholder="30">
  <details id="adv" class="adv"><summary>Advanced options <span class="muted small">– growth, pay rises, charges, enrolment date…</span></summary><div class="adv-body">
    <label class="check"><input type="checkbox" id="payroll"><span>I already pay into a pension through my employer's payroll</span></label>
    <label>When were you (or will you be) enrolled?<input id="enrol" type="month" value="2026-01"></label>
    <div class="three">
      <label>Investment growth (% a year)<input id="growth" type="number" step="0.5" min="0" max="10" placeholder="4"></label>
      <label>Pay rise (% a year)<input id="payRise" type="number" step="0.5" min="0" max="10" placeholder="2.5"></label>
      <label>Charges (% a year)<input id="charge" type="number" step="0.1" min="0" max="3" placeholder="0.5"></label>
    </div>
    <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
  </div></details>
  <div class="btn-row"><button type="submit" class="btn primary">Show my pension</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>How MyFutureFund works</h2>
<div class="card"><ol class="steps">
<li><strong>You're enrolled automatically</strong> if you're 23–60, earn €20,000+ a year and don't pay into a pension through payroll. It started on 1 January 2026.</li>
<li><strong>For every €3 you pay, your employer adds €3 and the State €1</strong> – €7 in your fund. Contributions are on pay up to €80,000.</li>
<li><strong>Rates rise every 3 years</strong>: 1.5% now, 3% from 2029, 4.5% from 2032 and 6% from 2035.</li>
<li><strong>You can opt out</strong> only in months 7–8 after joining (and after each rate rise). After that you can pause contributions.</li>
<li><strong>You get it at 66</strong>: up to 25% tax-free, the rest taxed as income.</li>
</ol></div>
<h2>Contribution rates by year</h2>{table(["Years", "You", "Employer", "State", "Total"], STAGE_ROWS)}
<div class="cta"><h2>Should you opt out?</h2><p>What you'd lose, and when you can.</p><a class="btn" href="opt-out.html">Opting out explained</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Auto-Enrolment (MyFutureFund) Pension Calculator", "url": app.BASE, "applicationCategory": "FinanceApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Calculate your MyFutureFund auto-enrolment contributions, the employer and State top-up, the effect on take-home pay and a projected pension pot at 66."}
    faqs = [("How much is taken from my pay for auto-enrolment?", "1.5% of your gross pay from 2026 to 2028, rising to 3% in 2029, 4.5% in 2032 and 6% from 2035. Your employer matches it and the State adds a third of your contribution."),
            ("Can I opt out of MyFutureFund?", "Yes, but only in months 7 and 8 after you're enrolled (and after each rate increase). You get your own contributions back; you'll be re-enrolled after 2 years if you're still eligible.")]
    app.page("index.html", "Auto-Enrolment Pension Calculator Ireland – MyFutureFund: What You Pay & Your Pot at 66",
             "Free MyFutureFund calculator: what auto-enrolment takes from your pay, what your employer and the State add, how your take-home pay changes and your projected pension at 66.",
             body, active="Calculator", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["../salary/js/tax.js", "js/ae.js", "js/calc.js"], h1="Auto-enrolment pension calculator",
             sources=("ci", "mff", "mff_guide"), cross=CROSS, priority="0.9",
             share_text="Auto-enrolled in MyFutureFund? This free calculator shows what comes out of your pay and what you'll have at 66:")

def build_rates():
    ex = run([{"k": "c", "s": 40000, "y": y} for y in (2026, 2029, 2032, 2035)])
    body = f"""<p class="lead">MyFutureFund contribution rates rise every three years until 2035. Here's what you, your employer and the State pay each year.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts(["<strong>2026–2028:</strong> you 1.5%, employer 1.5%, State 0.5% (3.5% in total).", "<strong>2029–2031:</strong> 3% / 3% / 1%.", "<strong>2032–2034:</strong> 4.5% / 4.5% / 1.5%.",
            "<strong>2035 onwards:</strong> 6% / 6% / 2% – 14% of your pay going into your pension.", "Contributions are on gross pay up to <strong>€80,000</strong> a year. You can't pay more or less than the set rate."])}
{table(["Years", "You", "Employer", "State", "Total"], STAGE_ROWS)}
<h2>Example: €40,000 salary</h2>
{table(["Year", "You pay", "Employer", "State", "Total a year", "You pay per month"], [[str(c['year']) + "+", eur(c['employee']), eur(c['employer']), eur(c['state']), eur(c['total']), eur(c['employee'] / 12, 2)] for c in ex])}
<div class="ad" data-slot="content"></div>
<p>After each increase you can opt out within months 7–8 and get back the extra you paid. <a href="opt-out.html">How opting out works →</a></p>
<div class="cta"><h2>Your figures</h2><p>See every year for your own salary.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("contribution-rates.html", "Auto-Enrolment Contribution Rates 2026–2035 Ireland – 1.5% Rising to 6%",
             "MyFutureFund contribution rates by year: 1.5% (2026–2028), 3% (2029–2031), 4.5% (2032–2034) and 6% from 2035, matched by your employer, plus the State top-up.",
             body, active="Rates by year", crumbs=[("Auto-enrolment", "./"), ("Contribution rates", None)], h1="Auto-enrolment contribution rates by year", sources=("ci", "mff"), cross=CROSS, priority="0.9")

def build_salary_pages():
    rows = []
    for s in SALARIES:
        imp, p30 = run([{"k": "i", "s": s, "y": YEAR}, {"k": "p", "o": {"salary": s, "age": 30, "startYear": YEAR}}])
        c = imp["contributions"]
        rows.append([f'<a href="salary-{s}.html">{eur(s)}</a>', eur(c["employee"] / 12, 2), eur((c["employer"] + c["state"]) / 12, 2), eur(p30["pot"])])
        stages = run([{"k": "c", "s": s, "y": y} for y in (2026, 2029, 2032, 2035)])
        pots = run([{"k": "p", "o": {"salary": s, "age": a, "startYear": YEAR}} for a in (25, 35, 45, 55)])
        facts = [f"On <strong>{eur(s)}</strong> you pay <strong>{eur(c['employee'] / 12, 2)} a month</strong> ({eur(c['employee'])} a year) into MyFutureFund in 2026.",
                 f"Your employer adds {eur(c['employer'])} and the State {eur(c['state'])} – <strong>{eur(c['employer'] + c['state'])}</strong> a year on top of yours.",
                 (f"Your take-home pay falls from {eur(imp['netBefore'])} to <strong>{eur(imp['netAfter'])}</strong> a year." if imp["netBefore"] else ""),
                 f"From 2035 you'll pay {eur(stages[3]['employee'] / 12, 2)} a month and {eur(stages[3]['total'])} a year will go in, in total.",
                 f"Starting at 30, you could have around <strong>{eur(p30['pot'])}</strong> at 66 (about {eur(p30['potToday'])} in today's money) – an illustration assuming 4% growth, 0.5% charges and 2.5% pay rises."]
        if s > (80000): facts.insert(2, "Contributions stop at €80,000 of pay, so they're the same as on €80,000.")
        hint = ""
        if s >= 50000:
            hint = f'<div class="callout">On {eur(s)} you could borrow up to <strong>{eur(s * 4)}</strong> for a home as a first-time buyer. <a href="../mortgage/borrow-{min(150000, (s // 5000) * 5000)}.html" data-track="cross_app" data-label="mortgage_from_ae">See what you could buy →</a></div>'
        if imp["higherRate"]:
            hint += '<div class="callout warn">You pay tax at 40%. A workplace pension with tax relief can be better value than MyFutureFund\'s 25% State top-up – <a href="vs-workplace-pension.html">compare</a> before you decide.</div>'
        body = f"""<p class="lead">How much will auto-enrolment cost you on a salary of {eur(s)}? What you pay, what's added, and what you could have at 66.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts([f for f in facts if f])}
<div class="hero-num"><div><span class="tl">You pay (2026)</span><strong>{eur(c['employee'] / 12, 2)}</strong><span class="muted">a month</span></div><div><span class="tl">Added for you</span><strong>{eur((c['employer'] + c['state']) / 12, 2)}</strong><span class="muted">a month</span></div></div>
<h2>Contributions on {eur(s)} by year</h2>
{table(["From", "You / month", "Employer / year", "State / year", "Total / year"], [[str(x['year']), eur(x['employee'] / 12, 2), eur(x['employer']), eur(x['state']), eur(x['total'])] for x in stages])}
{hint}
<div class="ad" data-slot="content"></div>
<h2>What you could have at 66 on {eur(s)}</h2>
{table(["Start age", "Projected pot at 66", "In today's money", "Tax-free lump sum (25%)"], [[str(a), eur(p['pot']), eur(p['potToday']), eur(p['lumpSum'])] for a, p in zip((25, 35, 45, 55), pots)])}
<p class="muted small">Illustration only: 4% growth a year, 0.5% charges, 2.5% pay rises, 2% inflation. Real returns vary and can be negative.</p>
<div class="cta"><h2>Your exact figures</h2><p>Change your age, growth and pay rises.</p><a class="btn" href="./?salary={s}">Open the calculator</a></div>
<div class="chip-list">{"".join(f'<a href="salary-{x}.html">{eur(x)}</a>' for x in SALARIES if x != s and abs(x - s) <= 15000)}<a href="by-salary.html">All salaries →</a></div>"""
        faqs = [(f"How much is auto-enrolment on {eur(s)}?", f"{eur(c['employee'] / 12, 2)} a month ({eur(c['employee'])} a year) from 2026 to 2028, rising to {eur(stages[3]['employee'] / 12, 2)} a month from 2035."),
                (f"How much does my employer pay on {eur(s)}?", f"{eur(c['employer'])} a year from 2026, plus {eur(c['state'])} from the State.")]
        app.page(f"salary-{s}.html", f"Auto-Enrolment on {eur(s)} – {eur(c['employee'] / 12, 2)} a Month | MyFutureFund Ireland",
                 f"MyFutureFund on a {eur(s)} salary: you pay {eur(c['employee'] / 12, 2)} a month in 2026, your employer and the State add {eur((c['employer'] + c['state']) / 12, 2)}. Rates to 2035 and your projected pot at 66.",
                 body, active="By salary", jsonld=[faq_ld(faqs)], crumbs=[("Auto-enrolment", "./"), ("By salary", "by-salary.html"), (eur(s), None)],
                 h1=f"Auto-enrolment on a {eur(s)} salary", sources=("ci", "mff"), cross=CROSS, cross_over={"salary": f"../salary/{min(s, 200000)}-after-tax.html" if s <= 100000 else "../salary/"})
    body = f"""<p class="lead">What MyFutureFund costs you and adds for you at every salary, plus a projected pot at 66 if you start at 30.</p>
<p class="updated">2026 rates · Checked {CHECKED}</p>
{table(["Salary", "You pay / month", "Employer + State / month", "Pot at 66 (start at 30)"], rows)}
<p class="muted small">Illustration: 4% growth, 0.5% charges, 2.5% pay rises. Contributions are capped at €80,000 of pay.</p>"""
    app.page("by-salary.html", "Auto-Enrolment by Salary Ireland 2026 – What You Pay Each Month",
             "MyFutureFund auto-enrolment contributions for every salary from €20,000 to €150,000: what you pay each month, what your employer and the State add, and a projected pot.",
             body, active="By salary", crumbs=[("Auto-enrolment", "./"), ("By salary", None)], h1="Auto-enrolment by salary", sources=("ci", "mff"), cross=CROSS, priority="0.8")

def build_age_pages():
    rows = []
    for a in AGES:
        pr = run([{"k": "p", "o": {"salary": s, "age": a, "startYear": YEAR}} for s in (30000, 45000, 60000, 80000)])
        rows.append([f'<a href="age-{a}.html">{a}</a>', str(66 - a)] + [eur(p["pot"]) for p in pr])
        facts = [f"If you're <strong>{a}</strong> you have <strong>{66 - a} years</strong> of contributions before you can take your fund at 66.",
                 f"On €45,000 you could build around <strong>{eur(pr[1]['pot'])}</strong> ({eur(pr[1]['potToday'])} in today's money).",
                 f"About {eur(pr[1]['lumpSum'])} of that could be taken tax-free at 66."]
        if a >= 55: facts.append("With fewer years to go, the employer and State top-up still add €4 for every €3 you pay – it's still worth knowing before you opt out.")
        if a == 60: facts.append("60 is the oldest age for automatic enrolment. Over 60 you can still opt in up to 66.")
        body = f"""<p class="lead">Auto-enrolment at age {a}: how much you could have at 66 on different salaries.</p>
{key_facts(facts)}
{table(["Salary", "Pot at 66", "In today's money", "Your contributions", "Employer + State"], [[eur(s), eur(p['pot']), eur(p['potToday']), eur(p['employee']), eur(p['employer'] + p['state'])] for s, p in zip((30000, 45000, 60000, 80000), pr)])}
<p class="muted small">Illustration only: 4% growth, 0.5% charges, 2.5% pay rises, 2% inflation.</p>
<div class="ad" data-slot="content"></div>
<p>Also see your <a href="../welfare/state-pension-contributory.html">State Pension (€309.30 a week from 2027)</a> – MyFutureFund is paid on top.</p>
<div class="cta"><h2>Your own projection</h2><p>Your salary, your age, your assumptions.</p><a class="btn" href="./?age={a}">Open the calculator</a></div>"""
        app.page(f"age-{a}.html", f"Auto-Enrolment at {a} – How Much Will I Have at 66? MyFutureFund Ireland",
                 f"Starting auto-enrolment at {a}: projected MyFutureFund pot at 66 on €30,000, €45,000, €60,000 and €80,000 salaries, with the employer and State top-up.",
                 body, active=None, crumbs=[("Auto-enrolment", "./"), ("By age", "by-age.html"), (f"Age {a}", None)], h1=f"Auto-enrolment at age {a}", sources=("ci", "mff_guide"), cross=CROSS)
    body = f"""<p class="lead">How much could you have at 66 depending on the age you start?</p>
{table(["Start age", "Years", "€30,000", "€45,000", "€60,000", "€80,000"], rows)}
<p class="muted small">Projected pot at 66. Illustration only: 4% growth, 0.5% charges, 2.5% pay rises.</p>"""
    app.page("by-age.html", "Auto-Enrolment Pot by Age – MyFutureFund Projections Ireland",
             "How much could auto-enrolment give you at 66? MyFutureFund projections by starting age (23 to 60) and salary.",
             body, crumbs=[("Auto-enrolment", "./"), ("By age", None)], h1="Auto-enrolment by age", sources=("ci", "mff_guide"), cross=CROSS, priority="0.7")

def build_guides():
    body = f"""<p class="lead">Can you opt out of MyFutureFund, when, and what happens to your money? The rules in plain English.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts(["You must stay in for at least <strong>6 months</strong>. You can then opt out during <strong>months 7 and 8</strong>. Joined on 1 January 2026? Your window was July–August 2026.",
            "If you opt out you get back <strong>your own contributions</strong>. The employer and State money stays in your fund, invested, until you're 66.",
            "You're <strong>re-enrolled automatically after 2 years</strong> if you're still eligible.",
            "After month 8 you can't opt out, but you can <strong>pause (suspend)</strong> contributions at any time – for at least 12 months. Employer and State contributions stop too.",
            "After each rate increase (2029, 2032, 2035) there's another opt-out window 6 months later, refunding the extra you paid.", "You can cancel an opt-out within 48 hours."])}
<h2>How to opt out or pause</h2>{lis(["Log in to the MyFutureFund portal with a verified MyGovID", "Or contact NAERSA for a paper form (01 568 9555)", "Your employer can't make you opt out or pause"])}
<div class="ad" data-slot="content"></div>
<h2>Before you opt out – think about this</h2>{lis(["For every €3 you pay, €4 more is added by your employer and the State – opting out means turning that down",
    "If money is tight, pausing keeps what's already there invested", "If you're a 40% taxpayer, a workplace pension with tax relief may suit you better – <a href='vs-workplace-pension.html'>compare</a>",
    "If you have a pension through payroll in your job, you weren't auto-enrolled for that job"])}
<div class="cta"><h2>What would you give up?</h2><p>See exactly what's added for you each month.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("opt-out.html", "How to Opt Out of Auto-Enrolment (MyFutureFund) – Windows, Refunds, Pausing",
             "Opting out of MyFutureFund: you can leave in months 7–8 after enrolment, get your own contributions back and are re-enrolled after 2 years. How to pause and what you lose.",
             body, active="Opt out", crumbs=[("Auto-enrolment", "./"), ("Opting out", None)], h1="Opting out of auto-enrolment", sources=("ci", "mff_faq", "rte_opt", "it_opt"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">Have you been automatically enrolled in MyFutureFund? Here's who is, who isn't and who can choose to join.</p>
{key_facts(["You're auto-enrolled if you're an <strong>employee aged 23 to 60</strong>, earn <strong>€20,000 or more a year</strong> across all jobs (or over €5,000 in a 13-week period) and <strong>don't pay into a pension through payroll</strong> for that job.",
            "Around 770,000 workers were enrolled on 1 January 2026 and more than 800,000 by mid-2026.", "Not auto-enrolled? Employees aged 18 up to 66 can <strong>opt in</strong> through the MyFutureFund portal.",
            "Changing jobs? You stay in MyFutureFund – NAERSA handles it.", "Start paying into a workplace pension through payroll? MyFutureFund contributions stop automatically."])}
<h2>Not covered</h2>{lis(["Self-employed people (no employer)", "Employees already in a payroll pension for that job", "Under 23 or over 60 (unless you opt in)", "Earning under €20,000 (unless you opt in)"])}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Check yourself</h2><p>Enter your age and salary.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("am-i-enrolled.html", "Am I Auto-Enrolled? MyFutureFund Eligibility Ireland – Age 23–60, €20,000",
             "Who is auto-enrolled in MyFutureFund: employees aged 23–60 earning €20,000+ without a payroll pension. Who isn't, and how to opt in from 18 to 66.",
             body, active="Am I enrolled?", crumbs=[("Auto-enrolment", "./"), ("Am I enrolled?", None)], h1="Am I auto-enrolled?", sources=("ci", "mff", "it_opt"), cross=CROSS, priority="0.8")

    imp = run([{"k": "i", "s": s, "y": 2027} for s in (30000, 45000, 60000, 90000)])
    body = f"""<p class="lead">MyFutureFund or a workplace pension (or PRSA) with tax relief – which gives you more?</p>
{key_facts(["MyFutureFund contributions get <strong>no tax relief</strong>. Instead the State adds €1 for every €3 you pay – equal to 25% of the total of €4.",
            "Workplace and personal pensions get tax relief at your <strong>highest rate – 20% or 40%</strong>.",
            "For a <strong>20% taxpayer</strong>, the State top-up is roughly as good or better. For a <strong>40% taxpayer</strong>, tax relief is usually worth more – especially with an employer who contributes more than 1.5%.",
            "Compare employer contributions too: many workplace schemes pay more than MyFutureFund's matching rate."])}
{table(["Salary (2027)", "You pay (1.5%)", "State top-up (MyFutureFund)", "Tax relief on the same amount"], [[eur(s), eur(i['contributions']['employee']), eur(i['stateTopUp']), eur(i['reliefEquivalent']) + (" (40%)" if i['higherRate'] else " (20%)")] for s, i in zip((30000, 45000, 60000, 90000), imp)])}
<div class="ad" data-slot="content"></div>
<p>See your marginal tax rate in the <a href="../salary/">take-home pay calculator</a>.</p>"""
    app.page("vs-workplace-pension.html", "MyFutureFund vs Workplace Pension – State Top-Up or Tax Relief? Ireland",
             "Auto-enrolment's 25% State top-up compared with 20% or 40% tax relief on a workplace pension or PRSA. Which is better at your salary?",
             body, crumbs=[("Auto-enrolment", "./"), ("vs workplace pension", None)], h1="MyFutureFund vs a workplace pension", sources=("ci", "mff_faq", "pensions"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">When and how can you get your MyFutureFund money – and how is it taxed?</p>
{key_facts(["You can access your fund at <strong>State Pension age – currently 66</strong>.", "Early access only in cases of <strong>ill-health retirement</strong>.",
            "Your fund grows <strong>tax-free</strong>. At retirement you can take up to <strong>25% as a tax-free lump sum</strong> (within Revenue limits); the rest is taxed as income under the rules at the time.",
            "If you stop working, move abroad or opt out, your savings <strong>stay invested</strong> and you can still take them at 66.",
            "MyFutureFund is paid <strong>on top of</strong> your State Pension (€309.30 a week Contributory from 2027)."])}
<div class="ad" data-slot="content"></div>
<p><a href="../welfare/state-pension-contributory.html">State Pension (Contributory) rates →</a> · <a href="by-age.html">What could you have at 66? →</a></p>"""
    app.page("retirement.html", "Taking Your MyFutureFund at 66 – Lump Sum, Tax and Early Access",
             "Accessing auto-enrolment savings: from age 66, up to 25% tax-free lump sum, the rest taxed, early access only for ill-health, savings stay invested if you stop working.",
             body, active="At 66", crumbs=[("Auto-enrolment", "./"), ("Taking it at 66", None)], h1="Taking your MyFutureFund at 66", sources=("mff_guide", "ci"), cross=CROSS, priority="0.7")

    FAQ = [("What is MyFutureFund?", "Ireland's auto-enrolment pension scheme, started on 1 January 2026 and run by NAERSA. You, your employer and the State all pay in."),
           ("How much do I pay?", "1.5% of gross pay (up to €80,000) in 2026–2028, 3% from 2029, 4.5% from 2032 and 6% from 2035."),
           ("How much does my employer pay?", "The same as you. The State adds €1 for every €3 you pay."),
           ("Do I get tax relief?", "No – instead the State top-up is worth 25% of the total of you plus the State. Contributions come from your pay after tax."),
           ("When can I opt out?", "In months 7 and 8 after enrolment, and after each rate increase. You get your own contributions back."),
           ("What if I opted out?", "You'll be re-enrolled automatically after 2 years if you're still eligible."),
           ("Can I pause contributions?", "Yes, after 6 months, for at least 12 months. Employer and State contributions pause too."),
           ("What happens if I change jobs?", "You stay in MyFutureFund; NAERSA handles the move."),
           ("I have two jobs – what happens?", "Eligibility counts earnings across all jobs. You may be enrolled for each job without a payroll pension."),
           ("When can I get my money?", "At State Pension age (66), or earlier only for ill-health retirement."),
           ("Is it worth it?", "For most people on standard tax, €7 goes in for every €3 you pay. Higher-rate taxpayers should compare it with a workplace pension."),
           ("Is this calculator official?", "No – it's a free, independent tool. Projections are illustrations; check your real fund in the MyFutureFund portal.")]
    app.page("faq.html", "Auto-Enrolment FAQ Ireland – MyFutureFund Questions Answered",
             "MyFutureFund auto-enrolment questions answered: contributions, employer and State top-up, tax, opting out, pausing, changing jobs and getting your money at 66.",
             f'<p class="lead">Common questions about auto-enrolment.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Auto-enrolment", "./"), ("FAQ", None)], h1="Auto-enrolment FAQ", sources=("ci", "mff_faq", "mff_guide"), cross=CROSS)

if __name__ == "__main__":
    build_index(); build_rates(); build_salary_pages(); build_age_pages(); build_guides()
    og_image(os.path.join(app.root, "og.png"), "MYFUTUREFUND", "Auto-enrolment", "pension calculator", "What you pay · what's added · your pot at 66", "Opt-out windows · rates to 2035",
             "tavion.ie/auto-enrolment  ·  free, no sign-up", (134, 239, 172), (21, 128, 61), (5, 50, 20))
    app.update_sitemap()
    app.update_llms("- [Auto-Enrolment Pension Calculator](https://tavion.ie/auto-enrolment/): MyFutureFund contributions (you, employer, State), effect on take-home pay, projected pot at 66, opt-out windows and eligibility.",
                    "Auto-enrolment: key facts",
                    """- MyFutureFund (Ireland's auto-enrolment pension) started 1 January 2026, run by NAERSA. Auto-enrolled: employees aged 23-60 earning €20,000+ a year (or €5,000+ in 13 weeks) without a payroll pension. Opt-in: employees 18-66.
- Contributions on gross pay up to €80,000: 2026-2028 1.5% employee / 1.5% employer / 0.5% State; 2029-2031 3/3/1; 2032-2034 4.5/4.5/1.5; 2035+ 6/6/2. No tax relief; State top-up equals 25%.
- Opt out only in months 7-8 after enrolment (and after each rate increase); own contributions refunded; re-enrolled after 2 years. Pause (suspend) any time after 6 months for at least 12 months.
- Access at State Pension age (66); early only for ill-health; up to 25% tax-free lump sum, remainder taxed as income.
- Pages: [Calculator](https://tavion.ie/auto-enrolment/), [Rates by year](https://tavion.ie/auto-enrolment/contribution-rates.html), [By salary](https://tavion.ie/auto-enrolment/by-salary.html), [Opt out](https://tavion.ie/auto-enrolment/opt-out.html), [FAQ](https://tavion.ie/auto-enrolment/faq.html). Source: Citizens Information, myfuturefund.ie.""")
    print("Built", len(app.files), "pages in", app.root)
