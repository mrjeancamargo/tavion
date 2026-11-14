"""
Builds the Work Permit Salary Checker app (tavion.ie/work-permit/).
Run from the repo root:   python tools/build_permit.py      (needs Node.js)
All thresholds come from work-permit/js/permit.js (DETE minimum annual remuneration from 1 March 2026).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, eur, lis, table, faq_ld, faq_html, key_facts, node, og_image

ENGINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work-permit", "js", "permit.js"))
CHECKED = "November 2026"
NODE = r"""
const P = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "q" ? P.qualifies(x.s, x.g) : x.k === "e" ? P.estimate2027(x.id, x.g) : x.k === "h" ? P.hourly(x.a, x.h) : null);
  process.stdout.write(JSON.stringify({ permits: P.PERMITS, res: res }));
});
"""
META = node(ENGINE, NODE, [])
PERMITS = {p["id"]: p for p in META["permits"]}
def run(q): return node(ENGINE, NODE, q)["res"]
def M(i): return PERMITS[i]["min"]
def hr(a, h=39): return round(a / (h * 52), 2)

SRC = {
    "dete_news": ("DETE – Revised roadmap for employment permit minimum annual remuneration (2 December 2025)", "https://enterprise.gov.ie/en/news-and-events/department-news/2025/december/20251202.html"),
    "dete_roadmap": ("DETE – Employment Permits Minimum Annual Remuneration: Outcome of the Roadmap Review 2025 (PDF)", "https://enterprise.gov.ie/en/publications/publication-files/employment-permits-minimum-annual-remuneration-outcome-of-the-roadmap-review-2025.pdf"),
    "gep": ("DETE – General Employment Permit", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/general-employment-permit/"),
    "csep": ("DETE – Critical Skills Employment Permit", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/critical-skills-employment-permit/"),
    "ict": ("DETE – Intra-Company Transfer Employment Permit", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/intra-company-transfer-employment-permit/"),
    "cfs": ("DETE – Contract for Services Employment Permit", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/contract-for-services-employment-permit/"),
    "dep": ("DETE – Dependant / Partner / Spouse Employment Permit", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/dependant-partner-spouse-employment-permit/"),
    "permits": ("DETE – Employment permits: all permit types", "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/"),
    "ci": ("Citizens Information – Employment permits", "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/"),
    "isd": ("Immigration Service Delivery – Immigration permission stamps", "https://www.irishimmigration.ie/registering-your-immigration-permission/information-on-registering/immigration-permission-stamps/"),
    "lewis": ("Lewis Silkin – Ireland's revised roadmap on MAR thresholds (December 2025)", "https://www.lewissilkin.com/en/insights/2025/12/11/irelands-revised-roadmap-on-minimum-annual-remuneration-thresholds-for-employment-permits"),
}

TABS = [("./", "Checker"), ("salary-thresholds.html", "2026 minimums"), ("general-employment-permit.html", "GEP"), ("critical-skills-permit.html", "Critical Skills"),
        ("renewals.html", "Renewals"), ("2027-increases.html", "2027"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Work permit salary checker</a><a href="salary-thresholds.html">2026 minimum salaries</a><a href="general-employment-permit.html">General Employment Permit</a>'
        '<a href="critical-skills-permit.html">Critical Skills permit</a><a href="care-workers.html">Care workers</a><a href="intra-company-transfer.html">Intra-Company Transfer</a>'
        '<a href="contract-for-services.html">Contract for Services</a><a href="graduate-rates.html">Graduate rates</a><a href="hourly-rate.html">Hourly rates</a><a href="what-counts.html">What counts as pay</a>'
        '<a href="renewals.html">Renewals</a><a href="2027-increases.html">2027 increases</a><a href="permits-and-stamps.html">Permits &amp; stamps</a><a href="fees.html">Fees</a>'
        '<a href="changing-employer.html">Changing employer</a><a href="by-salary.html">By salary</a><a href="faq.html">FAQ</a>')
app = App("work-permit", "Work Permit Salary Checker", "💼", None, "#4338ca", TABS, FOOT, SRC, None,
          "Is your salary above the new 2026 Irish work permit minimum? Free checker:", "Know someone on a work permit or renewing soon? Send them this.", "permit",
          f"Thresholds checked against the Department of Enterprise, Tourism and Employment (enterprise.gov.ie) in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>, not affiliated with DETE, ISD or the Government. Rules can change – always check enterprise.gov.ie before you apply. This is general information, not legal or immigration advice.")
CROSS = ["citizenship", "salary", "rent", "welfare"]

ROWS = [("General Employment Permit (GEP)", "gep", "general-employment-permit"),
        ("GEP – recent Irish graduate", "gep_grad", "graduate-rates"),
        ("GEP – healthcare assistants, home carers, care workers", "gep_care", "care-workers"),
        ("GEP – meat processing and horticulture operatives", "gep_agri", "care-workers"),
        ("Critical Skills (relevant degree, listed occupation)", "csep", "critical-skills-permit"),
        ("Critical Skills – recent graduate", "csep_grad", "graduate-rates"),
        ("Critical Skills (no degree, other occupations)", "csep_high", "critical-skills-permit"),
        ("Intra-Company Transfer – senior management / key personnel", "ict", "intra-company-transfer"),
        ("Intra-Company Transfer – trainee", "ict_trainee", "intra-company-transfer"),
        ("Contract for Services", "cfs", "contract-for-services")]
def row_vals(key):
    if key.endswith("_grad"):
        p = PERMITS[key[:-5]]; return p["grad"], None
    return PERMITS[key]["min"], PERMITS[key]["prev"]
def main_table(link=True):
    out = []
    for name, key, slug in ROWS:
        now, prev = row_vals(key)
        out.append([f'<a href="{slug}.html">{name}</a>' if link else name, f"<strong>{eur(now)}</strong>", eur(prev) if prev else "new", eur(hr(now), 2), eur(now / 12)])
    return table(["Permit", "From 1 March 2026", "Before", "Per hour (39 h)", "Per month"], out)

def cta(t="Check your own salary", p="Pick your permit and enter your pay.", q=""):
    return f'<div class="cta"><h2>{t}</h2><p>{p}</p><a class="btn" href="./{q}">Open the checker</a></div>'

def build_index():
    body = f"""<p class="lead">Is your pay high enough for an Irish employment permit – or for your renewal? The minimum salaries went up on 1 March 2026. Check yours in seconds. Free, no sign-up.</p>
<ul class="facts"><li>GEP {eur(M('gep'))}</li><li>Critical Skills {eur(M('csep'))}</li><li>Care roles {eur(M('gep_care'))}</li></ul>
<form id="permitForm" class="card" novalidate>
  <label for="permit" class="big-label">Your permit (or the one you're applying for)</label>
  <select id="permit"></select>
  <label class="check" id="gradRow" style="margin-top:10px"><input type="checkbox" id="graduate"><span>I graduated (Level 8 degree or higher) in the last 12 months <span class="muted small" id="gradNote"></span></span></label>
  <label for="salary" class="big-label" style="margin-top:14px">Your basic salary per year</label>
  <div class="money"><span>€</span><input id="salary" type="text" inputmode="decimal" autocomplete="off" placeholder="36,000"></div>
  <details id="adv" class="adv"><summary>Advanced options <span class="muted small">– health insurance, hours, board &amp; accommodation</span></summary><div class="adv-body">
    <label>Health insurance your employer pays for you (per year)<div class="money"><span>€</span><input id="health" type="text" inputmode="decimal" autocomplete="off" placeholder="0"></div></label>
    <label id="boardRow">Board and accommodation paid by the contractor (per year)<div class="money"><span>€</span><input id="board" type="text" inputmode="decimal" autocomplete="off" placeholder="0"></div></label>
    <label>Hours per week<input id="hours" type="number" min="1" max="60" inputmode="numeric" placeholder="39"></label>
    <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
  </div></details>
  <div class="btn-row"><button type="submit" class="btn primary">Check my salary</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>Minimum salaries from 1 March 2026</h2>
{main_table()}
<p class="muted small">Hourly and monthly figures are equivalents based on a 39-hour week. The rule is the yearly amount.</p>
<h2>What you need to know</h2>
<div class="card"><ol class="steps">
<li><strong>The minimums apply to new permits and renewals</strong> made on or after 1 March 2026 – even if your first permit was granted at the old rate.</li>
<li><strong>Only basic salary and employer-paid health insurance count.</strong> Bonuses, overtime and most allowances don't. <a href="what-counts.html">What counts →</a></li>
<li><strong>Recent graduates get a lower rate</strong> for GEP and Critical Skills permits. <a href="graduate-rates.html">Graduate rates →</a></li>
<li><strong>More increases are coming.</strong> From 2027 the minimums are reviewed every year in line with average earnings. <a href="2027-increases.html">What's planned →</a></li>
</ol></div>
<div class="cta"><h2>Renewing soon?</h2><p>What changes at renewal and when to apply.</p><a class="btn" href="renewals.html">Renewal rules</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Work Permit Salary Checker Ireland", "url": app.BASE, "applicationCategory": "BusinessApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Check whether your salary meets the Irish employment permit minimum annual remuneration from 1 March 2026 for General Employment, Critical Skills, Intra-Company Transfer and Contract for Services permits."}
    faqs = [("What is the minimum salary for a General Employment Permit in 2026?", f"{eur(M('gep'))} a year from 1 March 2026 ({eur(PERMITS['gep']['grad'])} for recent Irish graduates, {eur(M('gep_care'))} for healthcare assistants, home carers, care workers, meat processing and horticulture operatives)."),
            ("What is the minimum salary for a Critical Skills Employment Permit in 2026?", f"{eur(M('csep'))} a year with a relevant degree for an occupation on the Critical Skills list ({eur(PERMITS['csep']['grad'])} for recent graduates), or {eur(M('csep_high'))} for other eligible occupations.")]
    app.page("index.html", "Work Permit Salary Checker Ireland 2026 – Minimum Salary for GEP & Critical Skills",
             f"Free checker: is your pay above the Irish employment permit minimum from 1 March 2026? GEP {eur(M('gep'))}, Critical Skills {eur(M('csep'))}, care roles {eur(M('gep_care'))}, graduate rates and 2027 outlook.",
             body, active="Checker", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["js/permit.js", "js/calc.js"], h1="Work permit salary checker",
             sources=("dete_news", "gep", "csep", "ict", "cfs"), cross=CROSS, priority="0.9",
             share_text="Work permit minimum salaries went up in March 2026. Check if your pay is high enough (for renewals too):")

def build_thresholds():
    rises = [(n, row_vals(k)) for n, k, _ in ROWS if row_vals(k)[1]]
    body = f"""<p class="lead">Every Irish employment permit minimum salary from 1 March 2026, what it was before, and what it means per hour and per month.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"General Employment Permit: <strong>{eur(M('gep'))}</strong> (was €34,000) – <strong>{eur(PERMITS['gep']['grad'])}</strong> for recent Irish graduates.",
            f"Critical Skills with a relevant degree: <strong>{eur(M('csep'))}</strong> (was €38,000) – <strong>{eur(PERMITS['csep']['grad'])}</strong> for recent graduates.",
            f"Critical Skills without a relevant degree: <strong>{eur(M('csep_high'))}</strong> (was €64,000).",
            f"Intra-Company Transfer and Contract for Services: <strong>{eur(M('ict'))}</strong> (was €46,000). ICT trainees: {eur(M('ict_trainee'))}.",
            f"Healthcare assistants, home carers, care workers, meat processing and horticulture operatives: <strong>{eur(M('gep_care'))}</strong> (was €30,000) – €16.12 an hour.",
            "Most thresholds rose by about <strong>7.66%</strong>. They apply to <strong>new applications and renewals</strong> made on or after 1 March 2026."])}
{main_table()}
<div class="ad" data-slot="content"></div>
<h2>How much did each minimum go up?</h2>
{table(["Permit", "Before", "Now", "Increase"], [[n, eur(v[1]), eur(v[0]), f"{eur(v[0] - v[1])} ({(v[0] - v[1]) / v[1] * 100:.1f}%)"] for n, v in rises])}
<p>The Government had originally planned bigger jumps (about 15%) for 2026. After a review in 2025 the increase was cut to 7.66% for most permits, with yearly reviews from 2027. <a href="2027-increases.html">What's planned for 2027 →</a></p>
{cta()}"""
    faqs = [("What are the employment permit salary thresholds for 2026?", f"From 1 March 2026: GEP {eur(M('gep'))}, Critical Skills {eur(M('csep'))} (or {eur(M('csep_high'))} without a relevant degree), Intra-Company Transfer and Contract for Services {eur(M('ict'))}, care and agri-food roles {eur(M('gep_care'))}."),
            ("Do the new thresholds apply to renewals?", "Yes. Any new or renewal application made on or after 1 March 2026 must meet the new minimum.")]
    app.page("salary-thresholds.html", "Employment Permit Minimum Salary 2026 Ireland – All Thresholds (from 1 March)",
             f"All Irish work permit minimum salaries from 1 March 2026: GEP {eur(M('gep'))}, Critical Skills {eur(M('csep'))}, {eur(M('csep_high'))} without degree, ICT {eur(M('ict'))}, care workers {eur(M('gep_care'))}. Old vs new, hourly and monthly.",
             body, active="2026 minimums", jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("2026 minimum salaries", None)], h1="Employment permit minimum salaries 2026",
             sources=("dete_news", "dete_roadmap", "lewis"), cross=CROSS, priority="0.9")

def build_permit_pages():
    g = PERMITS["gep"]
    body = f"""<p class="lead">The General Employment Permit (GEP) is the most common Irish work permit. Here's the minimum salary from 1 March 2026 and the main rules.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Minimum salary: <strong>{eur(g['min'])} a year</strong> (was €34,000) – about {eur(hr(g['min']), 2)} an hour on a 39-hour week.",
            f"Recent graduates of an Irish college (Level 8 or higher, in the last 12 months): <strong>{eur(g['grad'])}</strong>.",
            f"Healthcare assistants, home carers, care workers, meat processing and horticulture operatives: <strong>{eur(M('gep_care'))}</strong>. <a href='care-workers.html'>Care roles →</a>",
            "First permit: up to <strong>2 years</strong>. Renewal: up to <strong>3 years</strong>. You can apply to renew within 4 months before it expires.",
            "You generally can't change employer in your first <strong>9 months</strong>. <a href='changing-employer.html'>Changing employer →</a>",
            "After <strong>5 years</strong> on GEPs you may be able to get Stamp 4 from the Department of Justice and work without a permit."])}
<h2>Other rules for a GEP</h2>{lis(["<strong>Labour Market Needs Test</strong>: in most cases the employer must first advertise the job (with the Department of Social Protection's employment service / EURES and one other online platform). Some roles are exempt, including jobs paying €68,911 or more.",
    "<strong>50:50 rule</strong>: at least half of the employer's staff must be EEA nationals when they apply (with some exceptions for start-ups).",
    "<strong>Ineligible occupations</strong>: some jobs can't get a GEP at all – check the Ineligible List of Occupations on enterprise.gov.ie.",
    "<strong>Family</strong>: spouses and partners of GEP holders can't get a Dependant permit – they need their own permission to work.",
    "<strong>Fees</strong>: €1,000 for a new permit over 6 months, €1,500 for a renewal over 6 months. Your employer can't take the cost from your pay. <a href='fees.html'>All fees →</a>"])}
<div class="ad" data-slot="content"></div>
<h2>Is my salary enough for a GEP?</h2>
<div class="chip-list">{"".join(f'<a href="salary-{s}.html">{eur(s)}</a>' for s in (33000, 34000, 35000, 36000, 37000, 38000, 40000))}<a href="by-salary.html">All salaries →</a></div>
{cta(q="?permit=gep")}"""
    faqs = [("What is the GEP minimum salary in 2026?", f"{eur(g['min'])} a year from 1 March 2026, or {eur(g['grad'])} for recent Irish graduates and {eur(M('gep_care'))} for care and agri-food roles."),
            ("How long is a General Employment Permit?", "Up to 2 years at first, then renewals for up to 3 years. After 5 years you may qualify for Stamp 4.")]
    app.page("general-employment-permit.html", f"General Employment Permit Minimum Salary 2026 – {eur(g['min'])} | Ireland GEP Rules",
             f"GEP minimum salary from 1 March 2026: {eur(g['min'])} ({eur(g['grad'])} for recent graduates, {eur(M('gep_care'))} for care roles). Labour market test, 50:50 rule, duration, renewals and Stamp 4.",
             body, active="GEP", jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("General Employment Permit", None)], h1="General Employment Permit: minimum salary and rules",
             sources=("gep", "dete_news"), cross=CROSS, priority="0.9")

    c = PERMITS["csep"]
    body = f"""<p class="lead">The Critical Skills Employment Permit (CSEP) is for jobs in short supply. It has a higher minimum salary but a faster route to Stamp 4 and family reunification.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Minimum with a <strong>relevant degree</strong> for a job on the Critical Skills Occupations List: <strong>{eur(c['min'])}</strong> (was €38,000).",
            f"Recent graduate (relevant degree in the last 12 months): <strong>{eur(c['grad'])}</strong>.",
            f"<strong>Any other eligible job</strong> (not on the Ineligible List) paying <strong>{eur(M('csep_high'))}</strong> or more (was €64,000). Without a degree you need relevant experience.",
            "The job offer must be for at least <strong>2 years</strong>. No Labour Market Needs Test is needed.",
            "After <strong>2 years</strong> you can apply to the Department of Justice for <strong>Stamp 4</strong> – no permit renewal needed.",
            "Your spouse or partner can join you straight away and can work without an employment permit."])}
<h2>Good to know</h2>{lis(["Public sector roles follow the pay rate in the public sector pay agreement instead.",
    "Only basic salary and employer-paid health insurance count – not bonuses. <a href='what-counts.html'>What counts →</a>",
    "The fee is €1,000 (90% refunded if refused). Apply at least 12 weeks before your start date.",
    "You're expected to stay with your first employer for at least 9 months. <a href='changing-employer.html'>Changing employer →</a>",
    "Time on Stamp 1 and Stamp 4 counts towards citizenship. <a href='../citizenship/stamp-4.html' data-track='cross_app' data-label='citizenship_from_permit'>Stamp 4 and citizenship →</a>"])}
<div class="ad" data-slot="content"></div>
<h2>GEP or Critical Skills?</h2>
{table(["", "General Employment", "Critical Skills"], [["Minimum salary", eur(M('gep')), f"{eur(c['min'])} (or {eur(M('csep_high'))})"], ["Labour Market Needs Test", "Usually yes", "No"],
    ["Job offer", "Any length", "At least 2 years"], ["Stamp 4", "After 5 years", "After 2 years"], ["Spouse can work", "Needs own permission", "Yes, without a permit"], ["Fee (new)", "€1,000", "€1,000"]])}
{cta(q="?permit=csep")}"""
    faqs = [("What is the Critical Skills minimum salary in 2026?", f"{eur(c['min'])} with a relevant degree for a listed occupation ({eur(c['grad'])} for recent graduates), or {eur(M('csep_high'))} for other eligible occupations, from 1 March 2026."),
            ("When can a Critical Skills holder get Stamp 4?", "After 2 years on the permit, by applying to the Department of Justice. A support letter from DETE is no longer needed.")]
    app.page("critical-skills-permit.html", f"Critical Skills Employment Permit Salary 2026 – {eur(c['min'])} / {eur(M('csep_high'))} | Ireland",
             f"Critical Skills permit minimum salary from 1 March 2026: {eur(c['min'])} with a relevant degree, {eur(c['grad'])} for recent graduates, {eur(M('csep_high'))} without. Stamp 4 after 2 years, family rules, GEP vs CSEP.",
             body, active="Critical Skills", jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("Critical Skills permit", None)], h1="Critical Skills Employment Permit: salary and rules",
             sources=("csep", "dete_news"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">Healthcare assistants, home carers, care workers, meat processing and horticulture operatives have a lower employment permit minimum – but it's rising faster than the others.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Minimum from 1 March 2026: <strong>{eur(M('gep_care'))} a year</strong> (was €30,000) – a 9% rise.",
            "DETE also sets a minimum hourly rate of <strong>€16.12</strong> for these roles.",
            "These are General Employment Permits, so the normal GEP rules apply (Labour Market Needs Test, 9-month rule, renewals).",
            f"The lower rate is being <strong>phased out by 2030</strong>, when these roles will need the full GEP minimum (now {eur(M('gep'))}).",
            "In 2027 the lower rate is expected to move to about <strong>92.5% of the GEP minimum</strong>, up from about 89% now."])}
{table(["Hours a week", "Hourly pay needed", "Monthly"], [[str(h), eur(hr(M('gep_care'), h), 2), eur(M('gep_care') / 12)] for h in (39, 40)])}
<div class="ad" data-slot="content"></div>
<h2>Working fewer hours?</h2><p>The minimum is a yearly amount. If your contract is for fewer than 39 hours, your hourly rate must be higher to reach {eur(M('gep_care'))}. <a href="hourly-rate.html">Hourly rates explained →</a></p>
<div class="callout warn">Renewing in 2027 or later? Your pay will likely need to rise by more than average earnings, as the gap to the full GEP rate closes. <a href="2027-increases.html">2027 outlook →</a></div>
{cta(q="?permit=gep_care")}"""
    faqs = [("What is the minimum salary for a healthcare assistant work permit in 2026?", f"{eur(M('gep_care'))} a year (€16.12 an hour) from 1 March 2026, up from €30,000."),
            ("Will the care worker permit minimum go up again?", "Yes. The lower rate is being phased out by 2030, so it's expected to rise faster than other thresholds each year.")]
    app.page("care-workers.html", f"Work Permit Minimum Salary for Care Workers & Healthcare Assistants 2026 – {eur(M('gep_care'))}",
             f"Healthcare assistants, home carers, care workers, meat and horticulture operatives: work permit minimum {eur(M('gep_care'))} (€16.12/hour) from 1 March 2026. Phased out by 2030 – what it means for renewals.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("Care and agri-food roles", None)], h1="Work permit minimum for care and agri-food workers",
             sources=("gep", "dete_news", "lewis"), cross=CROSS, priority="0.8")

    body = f"""<p class="lead">The Intra-Company Transfer permit lets multinationals move staff from an overseas branch to Ireland. Minimum salary and rules from 1 March 2026.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Senior management and key personnel: <strong>{eur(M('ict'))}</strong> a year (was €46,000). You must have worked for the overseas company for at least <strong>6 months</strong>.",
            f"Trainees: <strong>{eur(M('ict_trainee'))}</strong> (was €34,000). At least 1 month with the overseas company; training up to 12 months.",
            "First permit up to 2 years, with extensions up to a <strong>maximum of 5 years</strong> in total.",
            "Spouses and partners can't get a Dependant permit – they need their own permission to work.",
            "Fee: €1,000 for 6–24 months (90% refunded if refused)."])}
<div class="ad" data-slot="content"></div>
<p>Trainees can apply for a Critical Skills or General Employment Permit within their first 9 months. <a href="critical-skills-permit.html">Critical Skills →</a></p>
{cta(q="?permit=ict")}"""
    app.page("intra-company-transfer.html", f"Intra-Company Transfer Permit Salary 2026 Ireland – {eur(M('ict'))}",
             f"Intra-Company Transfer employment permit minimum from 1 March 2026: {eur(M('ict'))} for senior management and key personnel, {eur(M('ict_trainee'))} for trainees. Eligibility, duration and fees.",
             body, crumbs=[("Work permits", "./"), ("Intra-Company Transfer", None)], h1="Intra-Company Transfer permit: salary and rules", sources=("ict", "dete_news"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">The Contract for Services permit is for staff of a foreign company that has won a contract to provide services to an Irish business.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Minimum: <strong>{eur(M('cfs'))}</strong> a year (was €46,000).",
            "Basic salary must be at least the National Minimum Wage. <strong>Board and accommodation</strong> and health insurance paid by the contractor can count towards the minimum.",
            "You must have worked for the contractor for at least <strong>6 months</strong>. Subcontracted work isn't eligible.",
            "Permit for the contract period, up to 2 years at first, maximum 5 years in total. It doesn't give long-term residency rights.",
            "Fees: €1,000 new (6–24 months), €1,500 renewal (6–36 months)."])}
<div class="ad" data-slot="content"></div>
<p>After one year you may apply for another permit type, such as a Critical Skills or General Employment Permit.</p>
{cta(q="?permit=cfs")}"""
    app.page("contract-for-services.html", f"Contract for Services Employment Permit Salary 2026 – {eur(M('cfs'))} | Ireland",
             f"Contract for Services permit minimum from 1 March 2026: {eur(M('cfs'))}, including board and accommodation. Who qualifies, duration, renewals and fees.",
             body, crumbs=[("Work permits", "./"), ("Contract for Services", None)], h1="Contract for Services permit: salary and rules", sources=("cfs", "dete_news"), cross=CROSS, priority="0.6")

def build_guides():
    g, c = PERMITS["gep"], PERMITS["csep"]
    body = f"""<p class="lead">Just graduated? You can get a work permit at a lower minimum salary – but only for 12 months after you finish.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"General Employment Permit graduate rate: <strong>{eur(g['grad'])}</strong> instead of {eur(g['min'])}. For graduates of an <strong>Irish</strong> third-level institution (Level 8 or higher) in the 12 months before applying.",
            f"Critical Skills graduate rate: <strong>{eur(c['grad'])}</strong> instead of {eur(c['min'])}. For a <strong>relevant</strong> Level 8+ qualification from any recognised institution, in the 12 months before applying.",
            "There's no graduate rate for the €68,911 Critical Skills route, ICT, Contract for Services or care roles.",
            "Coming from Stamp 1G (Third Level Graduate Programme)? Line up your permit before your 1G ends so there's no gap."])}
{table(["Permit", "Graduate rate", "Standard rate", "Difference"], [["General Employment", eur(g['grad']), eur(g['min']), eur(g['min'] - g['grad'])], ["Critical Skills", eur(c['grad']), eur(c['min']), eur(c['min'] - c['grad'])]])}
<div class="ad" data-slot="content"></div>
<div class="callout warn">At renewal you're no longer a recent graduate, so your pay will normally need to meet the standard rate. <a href="renewals.html">Renewals →</a></div>
<p>Time on Stamp 1G counts towards citizenship (your Stamp 2 student years don't). <a href="../citizenship/stamp-1g.html" data-track="cross_app" data-label="citizenship_from_permit">Stamp 1G explained →</a></p>
{cta(q="?permit=gep&grad=1")}"""
    faqs = [("What is the graduate salary for a work permit in Ireland?", f"{eur(g['grad'])} for a General Employment Permit and {eur(c['grad'])} for a Critical Skills permit, if you graduated (Level 8+) in the 12 months before applying."),
            ("Does the graduate rate apply at renewal?", "Not normally – by then you're no longer within 12 months of graduating, so the standard minimum applies.")]
    app.page("graduate-rates.html", f"Work Permit Graduate Salary 2026 Ireland – {eur(g['grad'])} GEP / {eur(c['grad'])} Critical Skills",
             f"Recent graduates can get an Irish work permit at a lower salary: {eur(g['grad'])} (GEP) or {eur(c['grad'])} (Critical Skills) from 1 March 2026. Who qualifies and what happens at renewal.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("Graduate rates", None)], h1="Work permit graduate rates", sources=("gep", "csep", "dete_news"), cross=CROSS, priority="0.8")

    hrs = (20, 25, 30, 35, 37.5, 39, 40)
    body = f"""<p class="lead">Work permit minimums are yearly amounts. Here's the hourly pay you need to reach them, depending on your hours.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["The rule is the <strong>annual</strong> minimum. DETE's figures assume a <strong>39-hour week</strong>.",
            f"On 39 hours: GEP {eur(hr(M('gep')), 2)} an hour, Critical Skills {eur(hr(M('csep')), 2)}, care roles €16.12.",
            "If you work <strong>fewer hours</strong>, you need a <strong>higher hourly rate</strong> to reach the same yearly amount.",
            "Overtime doesn't count, so working extra hours won't get you over the line – your basic pay must."])}
{table(["Hours a week", "GEP " + eur(M('gep')), "Care roles " + eur(M('gep_care')), "Critical Skills " + eur(M('csep'))], [[f"{h:g}", eur(hr(M('gep'), h), 2), eur(hr(M('gep_care'), h), 2), eur(hr(M('csep'), h), 2)] for h in hrs])}
<div class="ad" data-slot="content"></div>
{cta("Check your hours", "Enter your salary and hours under Advanced options.")}"""
    app.page("hourly-rate.html", f"Work Permit Hourly Rate 2026 Ireland – GEP {eur(hr(M('gep')), 2)}/hour, Care €16.12",
             f"Hourly pay needed for an Irish work permit from 1 March 2026: GEP {eur(hr(M('gep')), 2)}, care roles €16.12, Critical Skills {eur(hr(M('csep')), 2)} on a 39-hour week. Table for part-time hours.",
             body, crumbs=[("Work permits", "./"), ("Hourly rates", None)], h1="Work permit minimum hourly rates", sources=("gep", "dete_news"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Not everything on your payslip counts towards the work permit minimum. Here's what does and doesn't.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts(["<strong>Counts:</strong> basic salary (which must be at least the National Minimum Wage) and <strong>health insurance</strong> your employer pays to a registered insurer.",
            "<strong>Doesn't count:</strong> bonuses, overtime, commission and most allowances.",
            "<strong>Contract for Services only:</strong> board and accommodation paid by the contractor can count too.",
            "Your <strong>payslips</strong> are checked at renewal – they must show the required pay."])}
{table(["Pay item", "Counts?"], [["Basic salary", "✅ Yes"], ["Employer-paid health insurance", "✅ Yes"], ["Board and accommodation", "Only for Contract for Services"], ["Bonus", "❌ No"], ["Overtime", "❌ No"], ["Commission", "❌ No"], ["Shift, travel or other allowances", "❌ Generally no"]])}
<div class="ad" data-slot="content"></div>
<div class="callout">Close to the line? Ask your employer whether health insurance they pay for you is included in the figure on your application.</div>
{cta()}"""
    app.page("what-counts.html", "What Counts as Salary for an Irish Work Permit? Bonuses, Overtime, Health Insurance",
             "For Irish employment permits only basic salary and employer-paid health insurance count towards the minimum. Bonuses and overtime don't. Board and accommodation counts for Contract for Services.",
             body, crumbs=[("Work permits", "./"), ("What counts as pay", None)], h1="What counts towards the work permit minimum", sources=("gep", "csep", "cfs"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Renewing your work permit after 1 March 2026? Your pay must meet the new minimum – even if your first permit was granted at the old rate.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts([f"Renewals made on or after 1 March 2026 must meet the new minimums – for example <strong>{eur(M('gep'))}</strong> for a GEP (was €34,000).",
            "Apply to renew within <strong>4 months before</strong> your permit expires, on Employment Permits Online.",
            "GEP renewals are for up to <strong>3 years</strong>. After 5 years with the same employer, a renewal can have no fee and no end date.",
            "<strong>Critical Skills</strong> holders don't renew – after 2 years they apply for Stamp 4.",
            "Your <strong>immigration permission</strong> (IRP) is separate – renew it at least a month before it expires.",
            "Graduate rate at first? At renewal you'll normally need the standard rate."])}
<h2>Renewal checklist</h2>{lis(["Check your basic pay against the new minimum (use the checker)", "If you're short, talk to your employer early – the pay rise must be in place and on your payslips",
    "Gather recent payslips showing basic pay clearly", "Apply within the 4-month window", "Renew your IRP registration with ISD as well",
    "Keep everything continuous – a gap in permission breaks your citizenship residence count"])}
<div class="ad" data-slot="content"></div>
<div class="callout warn">More increases are expected from 2027. If your pay is only just above the minimum, plan for your next renewal too. <a href="2027-increases.html">2027 outlook →</a></div>
{cta("Will your renewal pass?", "Check your salary against the new minimum.")}"""
    faqs = [("Do I need the new minimum salary to renew my work permit?", "Yes. Renewal applications made on or after 1 March 2026 must meet the new thresholds."),
            ("When can I renew my General Employment Permit?", "Within 4 months before it expires.")]
    app.page("renewals.html", "Work Permit Renewal Salary 2026 Ireland – Do You Need the New Minimum?",
             f"Renewing an Irish employment permit after 1 March 2026? Your pay must meet the new minimum ({eur(M('gep'))} for a GEP). When to apply, durations, Stamp 4 and a renewal checklist.",
             body, active="Renewals", jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("Renewals", None)], h1="Renewing your work permit", sources=("gep", "dete_news", "csep"), cross=CROSS, priority="0.9")

    est = run([{"k": "e", "id": i, "g": False} for i in ("gep", "gep_care", "csep", "csep_high", "ict")] + [{"k": "e", "id": "gep", "g": True}, {"k": "e", "id": "csep", "g": True}])
    body = f"""<p class="lead">Will work permit salary minimums go up again in 2027? Here's what the Government has said, and a rough idea of the numbers.</p>
<p class="updated">DETE roadmap · Checked {CHECKED}</p>
{key_facts(["From <strong>2027 to 2030</strong>, the minimums will be reviewed <strong>every year</strong> in line with changes in average weekly earnings published by the CSO.",
            "No 2027 figures have been officially announced yet.",
            "Average weekly earnings have risen by about <strong>4.9% a year</strong> on average since 2020 (between 3.1% and 7.6%).",
            "The lower rate for care and agri-food roles is being <strong>phased out by 2030</strong>. It's expected to reach about 92.5% of the GEP rate in 2027.",
            "Expect any increase to apply to <strong>renewals</strong> as well as new applications."])}
<h2>Illustration: if minimums rose 4.9%</h2>
{table(["Permit", "Now", "Rough 2027 estimate"], [["General Employment", eur(M('gep')), eur(est[0])], ["GEP – recent graduate", eur(PERMITS['gep']['grad']), eur(est[5])], ["Care and agri-food roles", eur(M('gep_care')), eur(est[1])],
    ["Critical Skills", eur(M('csep')), eur(est[2])], ["Critical Skills – recent graduate", eur(PERMITS['csep']['grad']), eur(est[6])], ["Critical Skills (no degree)", eur(M('csep_high')), eur(est[3])], ["ICT / Contract for Services", eur(M('ict')), eur(est[4])]])}
<p class="muted small">These are not official figures – just what the minimums would be with a 4.9% rise (and, for care roles, 92.5% of the GEP rate). We'll update this page when DETE announces the 2027 rates.</p>
<div class="ad" data-slot="content"></div>
{cta("Will you still qualify?", "The checker shows your 2027 headroom.")}"""
    faqs = [("Will work permit salary thresholds increase in 2027?", "They're expected to. From 2027 to 2030 they'll be reviewed each year in line with average weekly earnings. No 2027 figures have been announced yet."),
            ("How much could the GEP minimum be in 2027?", f"Not announced. If it rose by the recent average of 4.9%, it would be around {eur(est[0])}.")]
    app.page("2027-increases.html", "Work Permit Salary Increase 2027 Ireland – What's Planned for GEP & Critical Skills",
             f"Employment permit minimum salaries will be reviewed every year from 2027 in line with average earnings. What the roadmap says and rough 2027 estimates (GEP about {eur(est[0])}).",
             body, active="2027", jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("2027 increases", None)], h1="Work permit salary increases in 2027", sources=("dete_news", "dete_roadmap", "lewis"), cross=CROSS, priority="0.8")

    body = f"""<p class="lead">Which immigration stamp does each work permit give you, when can you move to Stamp 4, and does it count for citizenship?</p>
<p class="updated">DETE &amp; ISD · Checked {CHECKED}</p>
{table(["Permit", "Stamp while on it", "Route to Stamp 4", "Counts for citizenship?"], [
    ["General Employment", '<a href="../citizenship/stamp-1.html">Stamp 1</a>', "After 5 years", "✅ Yes"],
    ["Critical Skills", '<a href="../citizenship/stamp-1.html">Stamp 1</a>', "After 2 years", "✅ Yes"],
    ["Spouse of Critical Skills holder", '<a href="../citizenship/stamp-1g.html">Stamp 1G</a>', "After 5 years", "✅ Yes"],
    ["Intra-Company Transfer", "Stamp 1", "No – max 5 years", "✅ Yes"], ["Contract for Services", "Stamp 1", "No long-term residency rights", "✅ Yes"],
    ["Stamp 4 (after GEP / CSEP)", '<a href="../citizenship/stamp-4.html">Stamp 4</a>', "–", "✅ Yes"]])}
{key_facts(["An employment permit is <strong>not</strong> a residence permission. You must also register with immigration (ISD / GNIB) and keep your IRP valid.",
            "On <strong>Stamp 4</strong> you can work for any employer without a permit.",
            "You need <strong>5 years of reckonable residence</strong> (1,826 days) for Irish citizenship, including 1 year continuous before you apply. <a href='../citizenship/' data-track='cross_app' data-label='citizenship_from_permit'>Work out your date →</a>"])}
<div class="ad" data-slot="content"></div>
{cta()}"""
    app.page("permits-and-stamps.html", "Work Permits and Immigration Stamps Ireland – Stamp 1, 1G, 4 and Citizenship",
             "Which stamp each Irish employment permit gives (Stamp 1, Stamp 1G for CSEP spouses), when you can get Stamp 4 (2 or 5 years) and whether it counts towards citizenship.",
             body, crumbs=[("Work permits", "./"), ("Permits and stamps", None)], h1="Work permits, stamps and citizenship", sources=("gep", "csep", "isd"), cross=CROSS, priority="0.8")

    body = f"""<p class="lead">How much does an Irish employment permit cost? Fees by permit type, refunds, and who has to pay.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{table(["Permit", "New: 6 months or less", "New: up to 24 months", "Renewal"], [["General Employment", "€500", "€1,000", "€750 (≤6 months) / €1,500 (up to 3 years)"],
    ["Critical Skills", "–", "€1,000", "No renewal – apply for Stamp 4"], ["Intra-Company Transfer", "€500", "€1,000", "€500 / €1,000 / €1,500"], ["Contract for Services", "€500", "€1,000", "€750 / €1,500"], ["Dependant / Partner / Spouse", "Free", "Free", "Free"]])}
{key_facts(["If an application is refused, <strong>90% of the fee is refunded</strong> – to the applicant only.",
            "Your employer (or their agent) <strong>can't deduct the permit fee from your pay</strong> or ask you to pay it back.",
            "GEP holders with 5+ years with the same employer can get a renewal with <strong>no fee</strong> and no end date.",
            "Immigration registration (IRP) has its own separate fee."])}
<div class="ad" data-slot="content"></div>
{cta()}"""
    app.page("fees.html", "Work Permit Fees Ireland 2026 – GEP, Critical Skills, ICT Costs and Refunds",
             "Irish employment permit fees: €1,000 for a new GEP or Critical Skills permit, €1,500 for a GEP renewal, Dependant permits free. 90% refunded if refused; employers can't deduct it from pay.",
             body, crumbs=[("Work permits", "./"), ("Fees", None)], h1="Work permit fees", sources=("gep", "csep", "ict", "cfs", "dep"), cross=CROSS, priority="0.6")

    body = f"""<p class="lead">Can you change jobs on a work permit? Yes – but usually not in your first 9 months, and your new job must meet the minimum salary.</p>
<p class="updated">DETE · Checked {CHECKED}</p>
{key_facts(["You generally can't move to a new employer until <strong>9 months</strong> after you first started work in Ireland on a permit.",
            "After 9 months, your new employer applies for a <strong>new permit</strong>, and the new job must meet the current minimum salary.",
            "<strong>Made redundant?</strong> Tell DETE within 4 weeks. You have up to <strong>6 months</strong> to find a new job.",
            "Exceptions to the 9-month rule include redundancy and unforeseen changes that fundamentally change your job.",
            "If your employer only changes name or is taken over (transfer of undertakings), you don't need to start again."])}
<div class="ad" data-slot="content"></div>
<div class="callout">Moving to a higher-paid job? If it's €40,904+ with a relevant degree on the Critical Skills list – or €68,911+ in most jobs – you might qualify for a Critical Skills permit and Stamp 4 after 2 years. <a href="critical-skills-permit.html">Critical Skills →</a></div>
{cta("Check the new job's salary", "Does the offer meet the minimum?")}"""
    app.page("changing-employer.html", "Changing Employer on a Work Permit Ireland – 9-Month Rule and Redundancy",
             "Irish employment permit holders can usually change employer after 9 months with a new permit at the current minimum salary. Redundancy rules: tell DETE within 4 weeks, 6 months to find a job.",
             body, crumbs=[("Work permits", "./"), ("Changing employer", None)], h1="Changing employer on a work permit", sources=("gep", "csep"), cross=CROSS, priority="0.7")

SALARIES = list(range(30000, 50001, 1000)) + [55000, 60000, 65000, 69000, 70000]
def build_salary_pages():
    rows = []
    for s in SALARIES:
        qs, qg = run([{"k": "q", "s": s, "g": False}, {"k": "q", "s": s, "g": True}])
        uniq = [x for i, x in enumerate(qs) if x["permit"]["id"] != "gep_agri"]
        ok = [x for x in uniq if x["meets"]]
        names = ", ".join(x["permit"]["short"] for x in ok) or "none of the permits"
        rows.append([f'<a href="salary-{s}.html">{eur(s)}</a>', str(len(ok)) + " of " + str(len(uniq)), "✅" if s >= M("gep") else ("🎓 grad only" if s >= PERMITS["gep"]["grad"] else "❌"), "✅" if s >= M("csep") else ("🎓 grad only" if s >= PERMITS["csep"]["grad"] else "❌")])
        gep, csep = s - M("gep"), s - M("csep")
        facts = [f"On <strong>{eur(s)}</strong> a year you meet the minimum for: <strong>{names}</strong>.",
                 (f"General Employment Permit: ✅ {eur(gep)} above the {eur(M('gep'))} minimum." if gep >= 0 else f"General Employment Permit: ❌ <strong>{eur(-gep)} short</strong> of {eur(M('gep'))}" + (f" – but you'd meet the {eur(PERMITS['gep']['grad'])} graduate rate." if s >= PERMITS['gep']['grad'] else ".")),
                 (f"Critical Skills: ✅ {eur(csep)} above {eur(M('csep'))} (needs a relevant degree and a listed occupation)." if csep >= 0 else f"Critical Skills: ❌ {eur(-csep)} short of {eur(M('csep'))}" + (f" – but you'd meet the {eur(PERMITS['csep']['grad'])} graduate rate." if s >= PERMITS['csep']['grad'] else ".")),
                 f"That's {eur(s / 12)} a month, or about {eur(hr(s), 2)} an hour on a 39-hour week."]
        if s >= M("csep_high"): facts.append(f"At {eur(M('csep_high'))}+ most occupations can qualify for a Critical Skills permit, even without a degree.")
        tab = table(["Permit", "Minimum", "Standard", "Recent graduate"], [[f'<a href="{a["permit"]["slug"]}.html">{a["permit"]["short"]}</a>', eur(a["min"]), ("✅ " + eur(a["gap"]) + " over") if a["meets"] else ("❌ " + eur(-a["gap"]) + " short"),
                     (("✅" if b["meets"] else "❌") + " " + eur(b["min"])) if a["permit"]["grad"] else "–"] for a, b in zip(qs, qg) if a["permit"]["id"] != "gep_agri"])
        near = "".join(f'<a href="salary-{x}.html">{eur(x)}</a>' for x in SALARIES if x != s and abs(x - s) <= 3000)
        body = f"""<p class="lead">Is {eur(s)} enough for an Irish work permit? Here's every permit type against the minimums from 1 March 2026.</p>
<p class="updated">DETE thresholds · Checked {CHECKED}</p>
{key_facts(facts)}
{tab}
<div class="ad" data-slot="content"></div>
<p>Only basic salary and employer-paid health insurance count – not bonuses or overtime. <a href="what-counts.html">What counts →</a> · <a href="../salary/{s}-after-tax.html" data-track="cross_app" data-label="salary_from_permit">{eur(s)} after tax →</a></p>
{cta("Check with your details", "Add health insurance, hours or graduate status.", f"?salary={s}")}
<div class="chip-list">{near}<a href="by-salary.html">All salaries →</a></div>"""
        faqs = [(f"Is {eur(s)} enough for a General Employment Permit?", (f"Yes – it's {eur(gep)} above the {eur(M('gep'))} minimum from 1 March 2026." if gep >= 0 else f"No – it's {eur(-gep)} below the {eur(M('gep'))} minimum" + (f", though it meets the {eur(PERMITS['gep']['grad'])} rate for recent Irish graduates." if s >= PERMITS['gep']['grad'] else "."))),
                (f"Is {eur(s)} enough for a Critical Skills permit?", (f"Yes, if the job is on the Critical Skills list and you have a relevant degree – it's above the {eur(M('csep'))} minimum." if csep >= 0 else f"No – the minimum is {eur(M('csep'))}" + (f" ({eur(PERMITS['csep']['grad'])} for recent graduates, which {eur(s)} meets)." if s >= PERMITS['csep']['grad'] else ".")))]
        verdict = "Yes" if gep >= 0 else ("Graduates Only" if s >= PERMITS["gep"]["grad"] else "No")
        app.page(f"salary-{s}.html", f"Is {eur(s)} Enough for a Work Permit in Ireland? ({verdict} for GEP) – 2026",
                 f"{eur(s)} salary vs Irish employment permit minimums from 1 March 2026: GEP {eur(M('gep'))}, Critical Skills {eur(M('csep'))}, care roles {eur(M('gep_care'))}, graduate rates. Which permits you qualify for.",
                 body, active=None, jsonld=[faq_ld(faqs)], crumbs=[("Work permits", "./"), ("By salary", "by-salary.html"), (eur(s), None)], h1=f"Is {eur(s)} enough for a work permit?",
                 sources=("dete_news", "gep", "csep"), cross=CROSS, cross_over={"salary": f"../salary/{s}-after-tax.html"} if s <= 100000 else None)
    body = f"""<p class="lead">Which Irish work permits can you get on your salary? Pick yours for the full breakdown.</p>
<p class="updated">Thresholds from 1 March 2026 · Checked {CHECKED}</p>
{table(["Salary", "Permits you meet", "GEP", "Critical Skills"], rows)}
<p class="muted small">"Grad only" means you'd meet the lower rate for recent graduates (Level 8+, within 12 months).</p>
{cta()}"""
    app.page("by-salary.html", "Work Permit Minimum by Salary Ireland 2026 – €30,000 to €70,000",
             "Is your salary enough for an Irish work permit? Every salary from €30,000 to €70,000 checked against the GEP, Critical Skills, care, ICT and Contract for Services minimums from 1 March 2026.",
             body, crumbs=[("Work permits", "./"), ("By salary", None)], h1="Work permit minimum by salary", sources=("dete_news",), cross=CROSS, priority="0.7")

def build_faq():
    g, c = PERMITS["gep"], PERMITS["csep"]
    FAQ = [("What is the minimum salary for a work permit in Ireland in 2026?", f"From 1 March 2026 it's {eur(g['min'])} for a General Employment Permit and {eur(c['min'])} for a Critical Skills permit (with a relevant degree). Care and agri-food roles: {eur(M('gep_care'))}. ICT and Contract for Services: {eur(M('ict'))}."),
           ("When did the new thresholds start?", "1 March 2026. They apply to every new and renewal application made on or after that date."),
           ("I'm renewing – do I need the new minimum?", "Yes. Renewals made on or after 1 March 2026 must meet the new thresholds."),
           ("Is there a lower rate for graduates?", f"Yes: {eur(g['grad'])} for a GEP (Irish Level 8+ graduates) and {eur(c['grad'])} for Critical Skills (relevant Level 8+ degree), within 12 months of graduating."),
           ("Do bonuses or overtime count?", "No. Only basic salary and health insurance paid by your employer count (plus board and accommodation for Contract for Services)."),
           ("What's the hourly rate for a work permit?", f"About {eur(hr(g['min']), 2)} an hour for a GEP and €16.12 for care roles, on a 39-hour week. Work fewer hours and you need a higher hourly rate."),
           ("Can I work part-time on a work permit?", "The minimum is a yearly figure, so your annual basic pay must still reach it, whatever your hours."),
           ("Will the minimum go up in 2027?", "Probably. From 2027 to 2030 thresholds are reviewed every year in line with average earnings. No 2027 figures have been announced yet."),
           ("What is the Critical Skills minimum without a degree?", f"{eur(M('csep_high'))} a year, for occupations not on the Ineligible List. You'll need relevant experience."),
           ("Can my employer make me pay for the permit?", "No. Employers can't deduct the permit fee from your wages or ask you to pay it back."),
           ("When can I change employer?", "Usually after 9 months from when you first started work in Ireland on a permit, with a new permit at the current minimum."),
           ("Does a work permit count for citizenship?", "Yes – time on Stamp 1 (and later Stamp 4) counts as reckonable residence for citizenship."),
           ("Is this checker official?", "No – it's a free, independent tool based on DETE's published figures. Always check enterprise.gov.ie before you apply.")]
    app.page("faq.html", "Work Permit Salary FAQ Ireland 2026 – Minimums, Renewals, Graduates",
             "Irish work permit salary questions answered: 2026 minimums, renewals, graduate rates, hourly pay, what counts as salary, 2027 increases, fees and changing employer.",
             f'<p class="lead">Common questions about work permit minimum salaries.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ) + cta(),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Work permits", "./"), ("FAQ", None)], h1="Work permit salary FAQ", sources=("dete_news", "gep", "csep", "ci"), cross=CROSS, priority="0.8")

if __name__ == "__main__":
    build_index(); build_thresholds(); build_permit_pages(); build_guides(); build_salary_pages(); build_faq()
    og_image(os.path.join(app.root, "og.png"), "WORK PERMITS 2026", "Is your salary", "high enough?", f"GEP {eur(M('gep'))} · Critical Skills {eur(M('csep'))}", "New minimums from 1 March 2026",
             "tavion.ie/work-permit  ·  free, no sign-up", (165, 180, 252), (67, 56, 202), (20, 18, 60))
    app.update_sitemap()
    app.update_llms("- [Work Permit Salary Checker](https://tavion.ie/work-permit/): checks a salary against Irish employment permit minimum annual remuneration from 1 March 2026 (GEP, Critical Skills, ICT, Contract for Services, care roles, graduate rates), with renewal rules and 2027 outlook.",
                    "Work permits: key facts",
                    f"""- Employment permit minimum annual remuneration from 1 March 2026 (DETE), for new and renewal applications: General Employment Permit {eur(M('gep'))} (recent Irish graduates {eur(PERMITS['gep']['grad'])}); Critical Skills with relevant degree {eur(M('csep'))} (recent graduates {eur(PERMITS['csep']['grad'])}); Critical Skills other occupations {eur(M('csep_high'))}; Intra-Company Transfer and Contract for Services {eur(M('ict'))}; ICT trainee {eur(M('ict_trainee'))}; healthcare assistants, home carers, care workers, meat and horticulture operatives {eur(M('gep_care'))} (€16.12/hour).
- Previous rates: GEP €34,000, CSEP €38,000 / €64,000, ICT/CFS €46,000, care/agri €30,000. Most rose 7.66%.
- Only basic salary and employer-paid health insurance count (plus board and accommodation for Contract for Services); bonuses and overtime do not. Thresholds assume a 39-hour week.
- From 2027 to 2030 thresholds are reviewed annually in line with CSO average weekly earnings; lower-paid care/agri-food rates phased out by 2030. No 2027 figures announced as of {CHECKED}.
- Pages: [Checker](https://tavion.ie/work-permit/), [2026 minimums](https://tavion.ie/work-permit/salary-thresholds.html), [GEP](https://tavion.ie/work-permit/general-employment-permit.html), [Critical Skills](https://tavion.ie/work-permit/critical-skills-permit.html), [Renewals](https://tavion.ie/work-permit/renewals.html), [FAQ](https://tavion.ie/work-permit/faq.html). Source: enterprise.gov.ie.""")
    print("Built", len(app.files), "pages in", app.root)
