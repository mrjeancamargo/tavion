"""
Builds the static pages of the Irish Take-Home Pay app (tavion.ie/salary/).

Run from the repo root:   python tools/build_salary.py
Needs Node.js: every figure on the pages is computed by salary/js/tax.js (the same engine the
calculator uses), so the static salary pages and the calculator always agree.

When a new Budget is announced: add the new year to YEARS in salary/js/tax.js, update
CURRENT / NEXT below and the BUDGET_CHANGES text, then re-run this script.
"""
import datetime, json, os, re, subprocess
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.join(REPO, "salary")
TAX_JS = os.path.join(ROOT, "js", "tax.js")
SITE = "https://tavion.ie/"
BASE = SITE + "salary/"
CHECKED = "November 2026"
TODAY = datetime.date.today().isoformat()
CURRENT, NEXT, PREV = 2026, 2027, 2025          # tax years shown on the pages
REVENUE = "https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx"
CI_LEAVE = "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/leave-and-holidays/annual-leave/"
WRC = "https://www.workplacerelations.ie/"

TABS = [("./", "Calculator"), ("budget-2027.html", "Budget 2027"), ("salaries.html", "Salaries"),
        ("tax-rates.html", "Tax rates"), ("holidays.html", "Annual leave"), ("public-holidays.html", "Bank holidays"),
        ("faq.html", "FAQ")]

AMOUNTS = list(range(15000, 100001, 1000)) + list(range(105000, 200001, 5000))
POPULAR = [25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 70000, 80000, 100000]
BUDGET_TABLE = [20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 70000, 80000, 100000, 120000, 150000]

WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

# ---------------------------------------------------------------- run the JS engine
NODE_SCRIPT = r"""
const T = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const reqs = JSON.parse(raw);
  process.stdout.write(JSON.stringify({ years: T.YEARS, results: reqs.map(r => T.calc(r)) }, (k, v) => v === Infinity ? null : v));
});
"""
_cache = {}
def run_engine(reqs):
    p = subprocess.run(["node", "-e", NODE_SCRIPT, TAX_JS], input=json.dumps(reqs), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)

def calc_many(reqs):
    keys = [json.dumps(r, sort_keys=True) for r in reqs]
    todo = [r for r, k in zip(reqs, keys) if k not in _cache]
    if todo:
        out = run_engine(todo)
        for r, res in zip(todo, out["results"]):
            _cache[json.dumps(r, sort_keys=True)] = res
    return [_cache[k] for k in keys]

def calc(year, gross, status="single", **kw):
    r = dict(year=year, gross=gross, status=status); r.update(kw)
    return calc_many([r])[0]

YEARS = run_engine([])["years"]

# ---------------------------------------------------------------- formatting
def eur(n, dp=0):
    s = f"{abs(n):,.{dp}f}"
    return ("-" if n < 0 else "") + "€" + s

def eur2(n):
    return eur(n, 2)

def signed(n, dp=0):
    return ("+" if n >= 0 else "−") + eur(abs(n), dp)

def pct(r):
    return f"{r * 100:g}%"

def per(annual, hours=39, days=5):
    return dict(year=annual, month=annual / 12, fortnight=annual / 26, week=annual / 52, day=annual / (days * 52), hour=annual / (hours * 52))

def slug(a):
    return f"{a}-after-tax.html"

def kfmt(a):
    return f"€{a // 1000}k" if a % 1000 == 0 else eur(a)

# ---------------------------------------------------------------- public holidays
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(y, mo, da)

def first_monday(y, m):
    d = datetime.date(y, m, 1)
    return d + datetime.timedelta(days=(7 - d.weekday()) % 7)

def last_monday(y, m):
    d = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=d.weekday())

def public_holidays(y):
    feb1 = datetime.date(y, 2, 1)
    brigid = feb1 if feb1.weekday() == 4 else first_monday(y, 2)
    return [("New Year's Day", datetime.date(y, 1, 1)), ("St Brigid's Day", brigid), ("St Patrick's Day", datetime.date(y, 3, 17)),
            ("Easter Monday", easter(y) + datetime.timedelta(days=1)), ("May Bank Holiday", first_monday(y, 5)),
            ("June Bank Holiday", first_monday(y, 6)), ("August Bank Holiday", first_monday(y, 8)),
            ("October Bank Holiday", last_monday(y, 10)), ("Christmas Day", datetime.date(y, 12, 25)),
            ("St Stephen's Day", datetime.date(y, 12, 26))]

def nice_date(d):
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B %Y')}"

# ---------------------------------------------------------------- page shell
def share_html(text, url, label):
    wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
    fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
    return (f'<h2>Share it</h2><p class="muted">Know someone starting a new job or checking their payslip? Send them this.</p><div class="share">'
            f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
            f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

def key_facts(items):
    """A short, answer-first summary block. Search engines and AI assistants quote these."""
    return '<div class="facts-box"><h2 class="tl">Key facts</h2><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"

def page(filename, title, desc, body, active=None, jsonld=(), crumbs=None, slot="content", scripts=(), share_text=None, h1=None):
    url = BASE if filename == "index.html" else BASE + filename
    on = ' class="on"'
    tabs = "".join(f'<a href="{href}"{on if label == active else ""}>{label}</a>' for href, label in TABS)
    crumb_html = ""
    if crumbs:
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(
            f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs) + "</nav>"
        items = [{"@type": "ListItem", "position": i + 1, "name": t, "item": (BASE + (h if h not in ("./", None) else "")) if h else url}
                 for i, (t, h) in enumerate(crumbs)]
        jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "description": desc,
                              "inLanguage": "en-IE", "dateModified": TODAY, "isPartOf": {"@type": "WebSite", "name": "Tavion", "url": SITE},
                              "publisher": {"@type": "Organization", "name": "Tavion", "url": SITE, "logo": SITE + "images/logo.png"},
                              "about": {"@type": "Thing", "name": "Income tax, USC and PRSI in Ireland"}}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
    footer_sal = " · ".join(f'<a href="{slug(a)}">{kfmt(a)}</a>' for a in POPULAR)
    extra = "".join(f'<script src="{s}"></script>' for s in scripts)
    share = share_html(share_text or "Free Irish take-home pay calculator – see your net pay after tax, USC and PRSI for 2026 and 2027:", url, filename.replace(".html", ""))
    return f"""<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-adsense-account" content="ca-pub-1290266452162223">
<script src="/assets/tavion.js"></script>
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tavion">
<meta property="og:locale" content="en_IE">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#5b3fd1">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>€</b> Take-Home Pay</a><a class="small" href="../" data-track="apps_click" data-label="salary_header">More Tavion apps</a></div>
  <nav class="tabs" aria-label="Sections"><div class="wrap">{tabs}</div></nav>
</header>
<main class="wrap">
{crumb_html}
{('<h1>' + h1 + '</h1>') if h1 else ''}
{body}
<div class="ad" data-slot="{slot}"></div>
{share}
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Take-home pay pages"><a href="./">Take-home pay calculator</a><a href="budget-2027.html">Budget 2027</a><a href="salaries.html">All salaries</a><a href="tax-rates.html">Tax rates 2025–2027</a><a href="minimum-wage.html">Minimum wage</a><a href="holidays.html">Annual leave calculator</a><a href="public-holidays.html">Bank holidays</a><a href="faq.html">FAQ</a></nav>
    <p>After tax: {footer_sal}</p>
    <p>Figures checked against Revenue's tax charts and Budget 2027 (announced 6 October 2026) in {CHECKED}. This is a free, independent tool from <a href="../">Tavion</a> and is not affiliated with Revenue or the Government of Ireland. Results are estimates for a full tax year – your payslip can differ (for example with benefit-in-kind, health insurance, emergency tax or a mid-year start). Official source: <a href="{REVENUE}" rel="noopener">revenue.ie</a>.</p>
    <p>Also free: <a href="../mortgage/" data-track="cross_app" data-label="mortgage">🔑 Mortgage calculator – how much can I borrow?</a> · <a href="../rent/" data-track="cross_app" data-label="rent">🏠 Rent increase checker</a> · <a href="../stamp-duty/" data-track="cross_app" data-label="stamp">🧾 Stamp duty calculator</a></p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="salary_footer">More free apps from Tavion</a></p>
  </div>
</footer>
<script src="js/site.js"></script>{extra}
</body>
</html>
"""

def write(name, html):
    path = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

def lis(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a in pairs]}

def faq_html(pairs):
    return "".join(f'<details class="faq"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in pairs)

Y = lambda y: YEARS[str(y)]

# ---------------------------------------------------------------- calculator (index)
def build_index():
    n26, n27 = calc(CURRENT, 45000), calc(NEXT, 45000)
    body = f"""<p class="lead">Enter your salary to see your take-home pay after income tax, USC and PRSI – per year, month, fortnight, week, day and hour. Updated for <strong>Budget 2027</strong>. Free, no sign-up, nothing leaves your phone.</p>
<ul class="facts"><li>2025 · 2026 · 2027 tax years</li><li>Single, married &amp; one-parent</li><li>Medical card USC</li></ul>

<form id="calc" class="card" novalidate>
  <label for="gross" class="big-label">Your gross pay (before tax)</label>
  <div class="money-row">
    <div class="money"><span>€</span><input id="gross" type="text" inputmode="decimal" autocomplete="off" placeholder="45,000" aria-describedby="grossHelp"></div>
    <select id="period" aria-label="Pay period">
      <option value="year">per year</option><option value="month">per month</option><option value="fortnight">per fortnight</option>
      <option value="week">per week</option><option value="day">per day</option><option value="hour">per hour</option>
    </select>
  </div>
  <p id="grossHelp" class="muted small" style="margin:6px 0 0">Your salary or wages before anything is taken off.</p>

  <fieldset style="margin-top:18px">
    <legend class="sm">Tax year</legend>
    <div class="seg" id="yearSeg" role="radiogroup" aria-label="Tax year">
      <label><input type="radio" name="year" value="{PREV}"><span>{PREV}<small>Last year</small></span></label>
      <label><input type="radio" name="year" value="{CURRENT}" checked><span>{CURRENT}<small>This year</small></span></label>
      <label><input type="radio" name="year" value="{NEXT}"><span>{NEXT}<small>Budget 2027</small></span></label>
    </div>
  </fieldset>

  <details id="adv" class="adv">
    <summary>Advanced options <span class="muted small">– married, medical card, pension, rent…</span></summary>
    <div class="adv-body">
      <fieldset>
        <legend class="sm">Your situation</legend>
        <label class="radio"><input type="radio" name="status" value="single" checked><span>Single<small>Not married or in a civil partnership</small></span></label>
        <label class="radio"><input type="radio" name="status" value="parent"><span>Single parent<small>You get the Single Person Child Carer Credit (main carer of a child)</small></span></label>
        <label class="radio"><input type="radio" name="status" value="married1"><span>Married / civil partners – one income<small>Jointly assessed, only you earn</small></span></label>
        <label class="radio"><input type="radio" name="status" value="married2"><span>Married / civil partners – both working<small>Jointly assessed, you both earn</small></span></label>
        <label class="radio"><input type="radio" name="status" value="widowed"><span>Widowed or surviving civil partner<small>No dependent children</small></span></label>
        <p class="muted small">Married but taxed separately (individual or separate assessment)? Choose <strong>Single</strong> – each of you is taxed on your own income.</p>
      </fieldset>

      <div id="partnerBox" class="row-card" hidden>
        <label for="partnerGross">Your partner's gross pay per year</label>
        <div class="money"><span>€</span><input id="partnerGross" type="text" inputmode="decimal" placeholder="30,000"></div>
        <div class="two">
          <label>Partner's age<input id="partnerAge" type="number" min="16" max="100" inputmode="numeric" placeholder="35"></label>
          <label class="check" style="margin-top:30px"><input type="checkbox" id="partnerMedicalCard"><span>Partner has a full medical card</span></label>
        </div>
      </div>

      <div class="two">
        <label>Your age<input id="age" type="number" min="16" max="100" inputmode="numeric" placeholder="35"></label>
        <label>Employment<select id="employment"><option value="employee">Employee (PAYE)</option><option value="self">Self-employed</option></select></label>
      </div>

      <label class="check"><input type="checkbox" id="medicalCard"><span>I have a full medical card<small class="muted"> – reduced USC if income is €60,000 or less (GP visit card doesn't count)</small></span></label>

      <div class="two">
        <label>Pension contribution (% of salary)<input id="pensionPct" type="number" min="0" max="40" step="0.5" inputmode="decimal" placeholder="0"></label>
        <label>Rent you pay per month (€)<input id="rent" type="number" min="0" step="10" inputmode="decimal" placeholder="0"></label>
      </div>
      <p class="muted small" style="margin-top:4px">Rent gets the Rent Tax Credit: 20% of rent paid, up to €{Y(CURRENT)['credits']['rentSingle']:,} ({CURRENT}) or €{Y(NEXT)['credits']['rentSingle']:,} ({NEXT}) per person.</p>

      <label class="check" id="homeCarerRow"><input type="checkbox" id="homeCarer"><span>My spouse/partner cares for a child, an older person or a person with a disability at home<small class="muted"> – Home Carer Tax Credit</small></span></label>

      <div class="three">
        <label>Blind people (you/partner)<select id="blind"><option value="0">None</option><option value="1">One</option><option value="2">Both</option></select></label>
        <label>Incapacitated children<input id="incap" type="number" min="0" max="10" inputmode="numeric" placeholder="0"></label>
        <label>Dependent relatives<input id="depRel" type="number" min="0" max="10" inputmode="numeric" placeholder="0"></label>
      </div>

      <div class="two">
        <label>Hours you work per week<input id="hours" type="number" min="1" max="80" step="0.5" inputmode="decimal" placeholder="39"></label>
        <label>Days you work per week<input id="days" type="number" min="1" max="7" step="0.5" inputmode="decimal" placeholder="5"></label>
      </div>
      <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
    </div>
  </details>

  <div class="btn-row"><button type="submit" class="btn primary">Calculate my take-home pay</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Everything is calculated on your device. Nothing is sent to us.</p>
</form>

<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>

<h2>How your take-home pay is worked out</h2>
<div class="card"><ol class="steps">
<li><strong>Income tax (PAYE).</strong> 20% on income up to your standard rate band ({eur(Y(CURRENT)['band']['single'])} for a single person in {CURRENT}, {eur(Y(NEXT)['band']['single'])} in {NEXT}) and 40% on the rest. Your tax credits are then taken off the tax.</li>
<li><strong>Universal Social Charge (USC).</strong> 0.5%, 2%, 3% and 8% bands on your gross income. You pay no USC if your income is {eur(13000)} or less.</li>
<li><strong>PRSI.</strong> {pct(Y(CURRENT)['prsi']['jan'])} of your earnings in {CURRENT} (rising to {pct(Y(CURRENT)['prsi']['oct'])} from 1 October {CURRENT}) if you earn more than €352 a week.</li>
<li><strong>What's left</strong> is your take-home (net) pay. We split it into months, weeks, days and hours using your working hours.</li>
</ol></div>

<h2>Example: {eur(45000)} salary</h2>
<p>A single PAYE worker on {eur(45000)} takes home <strong>{eur(n26['net'])} a year ({eur(n26['net'] / 12)} a month)</strong> in {CURRENT}. Under Budget 2027 that becomes <strong>{eur(n27['net'])} ({eur(n27['net'] / 12)} a month)</strong> – {signed(n27['net'] - n26['net'])} a year. <a href="{slug(45000)}">See the full €45,000 breakdown →</a></p>
<div class="chip-list">{"".join(f'<a href="{slug(a)}">{kfmt(a)}</a>' for a in POPULAR)}<a href="salaries.html">All salaries →</a></div>

<div class="cta"><h2>What does Budget 2027 mean for you?</h2><p>See how much better off you'll be from January 2027 at every salary.</p><a class="btn" href="budget-2027.html">Budget 2027 changes</a></div>
"""
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Take-Home Pay Calculator", "url": BASE,
              "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "featureList": ["Income tax, USC and PRSI for 2025, 2026 and 2027", "Single, single parent, married one income and two incomes (joint assessment)",
                              "Medical card and over-70 USC rates", "Pension relief and Rent Tax Credit", "Net pay per year, month, fortnight, week, day and hour",
                              "Better-off comparison with the previous and next Budget"],
              "description": "Free Irish salary after tax calculator. Work out net pay after PAYE income tax, USC and PRSI for 2025, 2026 and Budget 2027."}
    faq = [("How much tax do I pay on €45,000 in Ireland?",
            f"A single PAYE employee on €45,000 pays {eur2(n26['incomeTax'])} income tax, {eur2(n26['usc'])} USC and {eur2(n26['prsi'])} PRSI in {CURRENT}, taking home {eur2(n26['net'])} a year."),
           ("What are the income tax rates in Ireland for 2027?",
            f"20% up to {eur(Y(NEXT)['band']['single'])} for a single person ({eur(Y(NEXT)['band']['married'])} for a married couple with one income) and 40% above that. Personal and employee tax credits are {eur(Y(NEXT)['credits']['personal'])} each.")]
    write("index.html", page("index.html", f"Take-Home Pay Calculator Ireland {CURRENT} & {NEXT} – Salary After Tax, USC & PRSI",
                             f"Free Irish salary calculator updated for Budget 2027: see your net pay after income tax, USC and PRSI per year, month, week, day and hour. Single, married, medical card and more.",
                             body, active="Calculator", jsonld=[app_ld, faq_ld(faq)], slot="calculator", scripts=["js/tax.js", "js/calc.js"],
                             h1="Take-home pay calculator Ireland",
                             share_text="Free Irish take-home pay calculator 🇮🇪 Updated for Budget 2027 – see exactly what you'll get per month and week:"))

# ---------------------------------------------------------------- one page per salary
def build_salary_pages():
    reqs = []
    for a in AMOUNTS:
        for y in (PREV, CURRENT, NEXT):
            for st in ("single", "parent", "married1"):
                reqs.append(dict(year=y, gross=a, status=st))
        reqs.append(dict(year=CURRENT, gross=a, status="single", medicalCard=True))
        reqs.append(dict(year=NEXT, gross=a, status="single", medicalCard=True))
    calc_many(reqs)

    for idx, a in enumerate(AMOUNTS):
        s = {y: calc(y, a) for y in (PREV, CURRENT, NEXT)}
        cur, nxt, prv = s[CURRENT], s[NEXT], s[PREV]
        pc, pn = per(cur["net"]), per(nxt["net"])
        diff = nxt["net"] - cur["net"]
        hourly = a / (39 * 52)

        rows = "".join(f"<tr><th scope=\"row\">{lab}</th><td>{eur2(pc[k])}</td><td>{eur2(pn[k])}</td><td class=\"{'up' if pn[k] - pc[k] >= 0 else 'down'}\">{signed(pn[k] - pc[k], 2)}</td></tr>"
                       for k, lab in (("year", "Per year"), ("month", "Per month"), ("fortnight", "Per fortnight"), ("week", "Per week"), ("day", "Per day (5-day week)"), ("hour", "Per hour (39-hour week)")))

        def brk(r):
            return [eur2(r["gross"]), eur2(r["taxBeforeCredits"]), "−" + eur2(r["creditsTotal"]), eur2(r["incomeTax"]), eur2(r["usc"]), eur2(r["prsi"]),
                    eur2(r["incomeTax"] + r["usc"] + r["prsi"]), eur2(r["net"]), f"{r['effectiveRate']:.1f}%", f"{r['marginalRate']:g}%"]
        labels = ["Gross salary", "Income tax before credits", "Tax credits", "Income tax (PAYE)", "USC", "PRSI", "Total deductions", "Take-home pay", "Effective tax rate", "Marginal rate (next €1)"]
        b = [brk(prv), brk(cur), brk(nxt)]
        total_cls = ' class="total"'
        brows = "".join(f"<tr{total_cls if l == 'Take-home pay' else ''}><th scope=\"row\">{l}</th><td>{b[0][i]}</td><td>{b[1][i]}</td><td>{b[2][i]}</td></tr>" for i, l in enumerate(labels))

        situ = []
        for st, lab in (("single", "Single"), ("parent", "Single parent"), ("married1", "Married, one income")):
            c1, c2 = calc(CURRENT, a, st), calc(NEXT, a, st)
            situ.append(f"<tr><th scope=\"row\">{lab}</th><td>{eur(c1['net'] / 12)}</td><td>{eur(c2['net'] / 12)}</td><td class=\"up\">{signed((c2['net'] - c1['net']) / 12)}</td></tr>")
        m1, m2 = calc(CURRENT, a, medicalCard=True), calc(NEXT, a, medicalCard=True)
        situ.append(f"<tr><th scope=\"row\">Single, full medical card</th><td>{eur(m1['net'] / 12)}</td><td>{eur(m2['net'] / 12)}</td><td class=\"up\">{signed((m2['net'] - m1['net']) / 12)}</td></tr>")

        near = [x for x in AMOUNTS if x != a and abs(x - a) <= (5000 if a < 100000 else 15000)]
        near = sorted(near, key=lambda x: abs(x - a))[:6]
        near_html = "".join(f'<a href="{slug(x)}">{kfmt(x)}</a>' for x in sorted(near))

        band_note = ("All of your income is taxed at 20% because it is below the standard rate band." if a <= Y(CURRENT)["band"]["single"]
                     else f"Income above {eur(Y(CURRENT)['band']['single'])} ({CURRENT}) is taxed at 40%. In {NEXT} the 40% rate starts at {eur(Y(NEXT)['band']['single'])}.")
        facts = [f"<strong>{eur(a)} a year after tax in Ireland is {eur(cur['net'])}</strong> in {CURRENT} for a single PAYE employee – {eur(pc['month'])} a month or {eur(pc['week'])} a week.",
                 f"In {NEXT}, after Budget 2027, it is <strong>{eur(nxt['net'])}</strong> ({eur(pn['month'])} a month) – {signed(diff)} a year, {signed(diff / 12)} a month.",
                 f"Deductions in {CURRENT}: income tax {eur(cur['incomeTax'])}, USC {eur(cur['usc'])}, PRSI {eur(cur['prsi'])}. Effective rate {cur['effectiveRate']:.1f}%.",
                 f"{eur(a)} a year is about {eur2(hourly)} an hour (39-hour week) or {eur(a / 12)} a month before tax."]
        body = f"""<p class="lead">How much is {eur(a)} after tax in Ireland? Here's your take-home pay after income tax, USC and PRSI for {PREV}, {CURRENT} and {NEXT} (Budget 2027).</p>
<p class="updated">Updated for Budget 2027 · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="hero-num"><div><span class="tl">{CURRENT} take-home</span><strong>{eur(pc['month'])}</strong><span class="muted">a month</span></div><div><span class="tl">{NEXT} take-home</span><strong>{eur(pn['month'])}</strong><span class="muted">a month</span></div></div>

<h2>{eur(a)} after tax per month, week, day and hour</h2>
<div class="table-wrap"><table><thead><tr><th>Single, PAYE</th><th>{CURRENT}</th><th>{NEXT}</th><th>Change</th></tr></thead><tbody>{rows}</tbody></table></div>

<h2>Tax breakdown on {eur(a)}</h2>
<div class="table-wrap"><table><thead><tr><th></th><th>{PREV}</th><th>{CURRENT}</th><th>{NEXT}</th></tr></thead><tbody>{brows}</tbody></table></div>
<p class="muted small">{band_note} PRSI in {CURRENT} is {pct(Y(CURRENT)['prsi']['jan'])}, rising to {pct(Y(CURRENT)['prsi']['oct'])} from 1 October, so we use a weighted figure for the full year.</p>

<div class="ad" data-slot="salary"></div>

<h2>{eur(a)} after tax for married couples, single parents and medical card holders</h2>
<div class="table-wrap"><table><thead><tr><th>Monthly take-home</th><th>{CURRENT}</th><th>{NEXT}</th><th>Change</th></tr></thead><tbody>{''.join(situ)}</tbody></table></div>
<p class="muted small">Married figures assume joint assessment with only one partner earning. For two incomes, pension contributions, rent credit and more, use the <a href="./?gross={a}">full calculator</a>.</p>

<div class="cta"><h2>Your exact take-home pay</h2><p>Add your partner's income, pension, rent, medical card and working hours.</p><a class="btn" href="./?gross={a}" data-track="salary_page_cta" data-label="{a}">Calculate with my details</a></div>

<h2>Other salaries near {eur(a)}</h2>
<div class="chip-list">{near_html}<a href="salaries.html">All salaries →</a></div>
"""
        faqs = [(f"How much is {eur(a)} after tax in Ireland?",
                 f"A single PAYE employee earning {eur(a)} takes home {eur2(cur['net'])} a year in {CURRENT} ({eur2(pc['month'])} a month, {eur2(pc['week'])} a week) after {eur2(cur['incomeTax'])} income tax, {eur2(cur['usc'])} USC and {eur2(cur['prsi'])} PRSI."),
                (f"How much is {eur(a)} a year per month after tax in Ireland?",
                 f"{eur2(pc['month'])} a month in {CURRENT}, and {eur2(pn['month'])} a month in {NEXT} after Budget 2027."),
                (f"Will I be better off in {NEXT} on {eur(a)}?",
                 f"Yes – a single person on {eur(a)} takes home {eur2(diff)} more in {NEXT} ({eur2(diff / 12)} a month), because of the wider tax band, higher tax credits and the wider 2% USC band, partly offset by higher PRSI." if diff > 0
                 else f"No – a single person on {eur(a)} takes home {eur2(-diff)} less in {NEXT} because of the PRSI increase."),
                (f"What is {eur(a)} a year per hour?",
                 f"About {eur2(hourly)} an hour before tax for a 39-hour week, or {eur2(pc['hour'])} an hour after tax in {CURRENT}.")]
        body += "<h2>Questions about a " + eur(a) + " salary</h2>" + faq_html(faqs)
        prev_a = AMOUNTS[idx - 1] if idx else None
        next_a = AMOUNTS[idx + 1] if idx + 1 < len(AMOUNTS) else None
        body += '<div class="pager">' + (f'<a class="btn" href="{slug(prev_a)}">← {eur(prev_a)}</a>' if prev_a else "<span></span>") + \
                (f'<a class="btn" href="{slug(next_a)}">{eur(next_a)} →</a>' if next_a else "") + "</div>"
        write(slug(a), page(slug(a), f"{eur(a)} After Tax Ireland {CURRENT} & {NEXT} – {eur(pc['month'])} a Month Take-Home",
                            f"{eur(a)} after tax in Ireland is {eur(cur['net'])} a year ({eur(pc['month'])} a month, {eur(pc['week'])} a week) in {CURRENT}, and {eur(nxt['net'])} in {NEXT} after Budget 2027. Full income tax, USC and PRSI breakdown.",
                            body, active="Salaries", jsonld=[faq_ld(faqs)], slot="content",
                            crumbs=[("Take-home pay", "./"), ("Salaries", "salaries.html"), (eur(a), None)],
                            h1=f"{eur(a)} after tax in Ireland",
                            share_text=f"What {eur(a)} a year really comes to after tax in Ireland – {eur(pc['month'])} a month:"))

    # hub
    rows = []
    for a in AMOUNTS:
        c, n = calc(CURRENT, a), calc(NEXT, a)
        rows.append(f"<tr><td><a href=\"{slug(a)}\">{eur(a)}</a></td><td>{eur(c['net'])}</td><td>{eur(c['net'] / 12)}</td><td>{eur(n['net'] / 12)}</td><td class=\"up\">{signed((n['net'] - c['net']) / 12)}</td></tr>")
    body = f"""<p class="lead">Take-home pay for every salary from €15,000 to €200,000 in Ireland, for a single PAYE employee. Tap a salary for the full breakdown.</p>
<p class="updated">Updated for Budget 2027 · Checked {CHECKED}</p>
{key_facts([f"These figures are for a single PAYE employee with the standard personal and employee tax credits.",
            f"{CURRENT}: 20% tax up to {eur(Y(CURRENT)['band']['single'])}, credits {eur(Y(CURRENT)['credits']['personal'] + Y(CURRENT)['credits']['employee'])}. {NEXT}: 20% up to {eur(Y(NEXT)['band']['single'])}, credits {eur(Y(NEXT)['credits']['personal'] + Y(NEXT)['credits']['employee'])}.",
            "Married, single parent, medical card or pension? Use the calculator for your own figures."])}
<div class="table-wrap"><table class="sticky"><thead><tr><th>Salary</th><th>Net {CURRENT} / year</th><th>Net {CURRENT} / month</th><th>Net {NEXT} / month</th><th>Change / month</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"""
    write("salaries.html", page("salaries.html", f"Salary After Tax Ireland {CURRENT} & {NEXT} – Take-Home Pay Table €15k to €200k",
                                f"Irish take-home pay table: net pay per year and month for every salary from €15,000 to €200,000 in {CURRENT} and {NEXT} (Budget 2027), after income tax, USC and PRSI.",
                                body, active="Salaries", crumbs=[("Take-home pay", "./"), ("Salaries", None)], h1="Salary after tax in Ireland: every salary",
                                share_text="Take-home pay for every salary in Ireland, 2026 vs 2027:"))

# ---------------------------------------------------------------- Budget 2027
def build_budget():
    rows = []
    for a in BUDGET_TABLE:
        cells = [f'<td><a href="{slug(a)}">{eur(a)}</a></td>']
        for st in ("single", "married1"):
            c, n = calc(CURRENT, a, st), calc(NEXT, a, st)
            d = n["net"] - c["net"]
            cells.append(f'<td class="up">{signed(d)}</td><td class="up">{signed(d / 12, 2)}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    c, n = Y(CURRENT), Y(NEXT)
    ex = calc(NEXT, 45000)["net"] - calc(CURRENT, 45000)["net"]
    changes = [
        ("Standard rate band (single)", eur(c["band"]["single"]), eur(n["band"]["single"])),
        ("Standard rate band (married, one income)", eur(c["band"]["married"]), eur(n["band"]["married"])),
        ("Standard rate band (married, two incomes – max)", eur(c["band"]["married"] + c["band"]["secondMax"]), eur(n["band"]["married"] + n["band"]["secondMax"])),
        ("Standard rate band (single parent)", eur(c["band"]["parent"]), eur(n["band"]["parent"])),
        ("Personal tax credit (single)", eur(c["credits"]["personal"]), eur(n["credits"]["personal"])),
        ("Personal tax credit (married)", eur(c["credits"]["married"]), eur(n["credits"]["married"])),
        ("Employee (PAYE) tax credit", eur(c["credits"]["employee"]), eur(n["credits"]["employee"])),
        ("Earned Income tax credit", eur(c["credits"]["earned"]), eur(n["credits"]["earned"])),
        ("Home Carer tax credit", eur(c["credits"]["homeCarer"]), eur(n["credits"]["homeCarer"])),
        ("Rent Tax Credit (single / couple)", f'{eur(c["credits"]["rentSingle"])} / {eur(c["credits"]["rentCouple"])}', f'{eur(n["credits"]["rentSingle"])} / {eur(n["credits"]["rentCouple"])}'),
        ("USC 2% band ends at", eur(c["usc"][1][0]), eur(n["usc"][1][0])),
        ("Employee PRSI", f'{pct(c["prsi"]["jan"])} → {pct(c["prsi"]["oct"])} from 1 Oct', f'{pct(n["prsi"]["jan"])} → {pct(n["prsi"]["oct"])} from 1 Oct'),
        ("National minimum wage (per hour)", eur2(c["minWage"]), eur2(n["minWage"])),
    ]
    crow = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td><strong>{d}</strong></td></tr>" for a, b, d in changes)
    facts = [f"Budget 2027 was announced on <strong>6 October 2026</strong>. The income tax and USC changes apply from <strong>1 January 2027</strong>.",
             f"The 40% tax rate now starts at <strong>{eur(n['band']['single'])}</strong> for a single person (up {eur(n['band']['single'] - c['band']['single'])}).",
             f"Personal, employee and earned income tax credits each rise by <strong>€125 to {eur(n['credits']['personal'])}</strong>.",
             f"The USC 2% band is widened to <strong>{eur(n['usc'][1][0])}</strong> so a full-time minimum wage worker stays out of the 3% band.",
             f"A single worker on {eur(45000)} takes home about <strong>{signed(ex)} a year ({signed(ex / 12)} a month)</strong> in {NEXT}.",
             f"Employee PRSI is already set to rise to {pct(n['prsi']['oct'])} from 1 October {NEXT}, which takes back some of the gain."]
    body = f"""<p class="lead">What Budget 2027 means for your pay packet: every income tax, USC and PRSI change, and how much better off you'll be from January 2027.</p>
<p class="updated">Checked against Budget 2027 tax tables · {CHECKED}</p>
{key_facts(facts)}
<h2>How much better off will I be in 2027?</h2>
<div class="table-wrap"><table><thead><tr><th rowspan="2">Salary</th><th colspan="2">Single</th><th colspan="2">Married, one income</th></tr><tr><th>Per year</th><th>Per month</th><th>Per year</th><th>Per month</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="muted small">Compared with {CURRENT}. PAYE employees, standard credits, PRSI weighted for the October rate rise each year.</p>
<div class="cta"><h2>Check your own figure</h2><p>Pick {NEXT} in the calculator to see your exact take-home pay and the change from {CURRENT}.</p><a class="btn" href="./?year={NEXT}">Open the calculator</a></div>
<div class="ad" data-slot="content"></div>
<h2>Budget 2027 income tax, USC and PRSI changes</h2>
<div class="table-wrap"><table><thead><tr><th></th><th>{CURRENT}</th><th>{NEXT}</th></tr></thead><tbody>{crow}</tbody></table></div>
<h2>What hasn't changed</h2>
{lis(["Income tax rates stay at 20% and 40%", "USC rates stay at 0.5%, 2%, 3% and 8% (with an extra 3% for self-employed income over €100,000)",
      "You still pay no USC if your income is €13,000 or less", "Reduced USC for full medical card holders and people aged 70+ earning €60,000 or less – the medical card concession is extended to the end of 2027",
      "Single Person Child Carer credit (€1,900), Age credit (€245 / €490), Blind person's credit (€1,950) and Incapacitated child credit (€3,800)"])}
<p class="muted small">Sources: Department of Finance Budget 2027; Revenue; KPMG Budget 2027 tax tables. Credits not mentioned in Budget 2027 are assumed unchanged.</p>"""
    faqs = [("When do the Budget 2027 tax changes start?", "The income tax and USC changes apply from 1 January 2027. The PRSI rate rises from 4.35% to 4.5% on 1 October 2027."),
            ("How much will I get from Budget 2027?", f"A single PAYE worker on €45,000 takes home about {eur(ex)} more a year ({eur2(ex / 12)} a month). Most full-time workers gain between €200 and €600 a year."),
            ("What are the tax bands for 2027 in Ireland?", f"The 20% rate applies up to {eur(n['band']['single'])} for a single person, {eur(n['band']['parent'])} for a single parent, {eur(n['band']['married'])} for a married couple with one income and up to {eur(n['band']['married'] + n['band']['secondMax'])} for a married couple with two incomes. Income above that is taxed at 40%."),
            ("What is the minimum wage in 2027?", f"€14.94 an hour from 1 January 2027, up from €14.15.")]
    body += "<h2>Budget 2027 questions</h2>" + faq_html(faqs)
    write("budget-2027.html", page("budget-2027.html", "Budget 2027 Ireland Tax Changes – How Much Better Off Will You Be?",
                                   f"Budget 2027 explained: tax band up to €46,500, tax credits up €125, wider USC 2% band. See how much more you'll take home from January 2027 at every salary.",
                                   body, active="Budget 2027", jsonld=[faq_ld(faqs)], crumbs=[("Take-home pay", "./"), ("Budget 2027", None)],
                                   h1="Budget 2027: what it means for your take-home pay",
                                   share_text="Budget 2027 – see how much more you'll take home from January:"))

# ---------------------------------------------------------------- tax rates
def build_rates():
    ys = [PREV, CURRENT, NEXT]
    def row(label, fn):
        return f"<tr><th scope=\"row\">{label}</th>" + "".join(f"<td>{fn(Y(y))}</td>" for y in ys) + "</tr>"
    head = "<thead><tr><th></th>" + "".join(f"<th>{y}</th>" for y in ys) + "</tr></thead>"
    bands = "".join([
        row("Single / widowed (no children)", lambda d: eur(d["band"]["single"])),
        row("Single parent (SPCCC)", lambda d: eur(d["band"]["parent"])),
        row("Married / civil partners – one income", lambda d: eur(d["band"]["married"])),
        row("Married / civil partners – two incomes", lambda d: f'{eur(d["band"]["married"])} + up to {eur(d["band"]["secondMax"])}')])
    cr = [("Personal – single", "personal"), ("Personal – married / civil partners", "married"), ("Widowed (no dependent children)", "widowed"),
          ("Employee (PAYE)", "employee"), ("Earned Income (self-employed)", "earned"), ("Home Carer (max)", "homeCarer"),
          ("Single Person Child Carer", "spccc"), ("Age (65+) – single", "age"), ("Age (65+) – married", "ageMarried"), ("Blind person", "blind"),
          ("Incapacitated child", "incapChild"), ("Dependent relative", "depRelative"), ("Rent Tax Credit – single (max)", "rentSingle"), ("Rent Tax Credit – couple (max)", "rentCouple")]
    credits = "".join(row(l, (lambda k: lambda d: eur(d["credits"][k]))(k)) for l, k in cr)
    def usc_rows():
        out = []
        for i, rate in enumerate(["0.5%", "2%", "3%", "8%"]):
            def f(d, i=i):
                lo = 0 if i == 0 else d["usc"][i - 1][0]
                hi = d["usc"][i][0]
                return f"{eur(lo)} – {eur(hi)}" if hi else f"Over {eur(lo)}"
            out.append(row(rate, f))
        return "".join(out)
    prsi = "".join([row("Employee PRSI (Class A) Jan–Sep", lambda d: pct(d["prsi"]["jan"])), row("From 1 October", lambda d: pct(d["prsi"]["oct"])),
                    row("Minimum wage (per hour)", lambda d: eur2(d["minWage"]))])
    facts = [f"Income tax in Ireland is 20% up to the standard rate band and 40% above it. In {CURRENT} the single person's band is {eur(Y(CURRENT)['band']['single'])}; in {NEXT} it's {eur(Y(NEXT)['band']['single'])}.",
             f"A single PAYE employee gets {eur(Y(CURRENT)['credits']['personal'] + Y(CURRENT)['credits']['employee'])} of tax credits in {CURRENT} and {eur(Y(NEXT)['credits']['personal'] + Y(NEXT)['credits']['employee'])} in {NEXT}.",
             "USC is charged on gross income at 0.5%, 2%, 3% and 8%. Income of €13,000 or less is exempt.",
             f"Employee PRSI is {pct(Y(CURRENT)['prsi']['jan'])} in {CURRENT}, rising to {pct(Y(CURRENT)['prsi']['oct'])} on 1 October {CURRENT} and {pct(Y(NEXT)['prsi']['oct'])} on 1 October {NEXT}. No PRSI if you earn €352 a week or less."]
    body = f"""<p class="lead">Irish income tax bands, tax credits, USC and PRSI rates for {PREV}, {CURRENT} and {NEXT} side by side.</p>
<p class="updated">Checked against Revenue and Budget 2027 · {CHECKED} · <a href="rates.json">Download as JSON</a></p>
{key_facts(facts)}
<h2 id="bands">Income tax bands (20% rate)</h2>
<div class="table-wrap"><table>{head}<tbody>{bands}</tbody></table></div>
<p class="muted small">Income above the band is taxed at 40%. For two-income couples the increase is the lower of the second income or the maximum shown, and can't be moved between spouses.</p>
<h2 id="credits">Tax credits</h2>
<div class="table-wrap"><table>{head}<tbody>{credits}</tbody></table></div>
<p class="muted small">The Employee credit can't be more than 20% of your employment income. The Rent Tax Credit is 20% of rent paid, up to the maximum. Credits not mentioned in Budget 2027 are shown unchanged.</p>
<div class="ad" data-slot="content"></div>
<h2 id="usc">Universal Social Charge (USC)</h2>
<div class="table-wrap"><table>{head}<tbody>{usc_rows()}</tbody></table></div>
{lis(["No USC if your total income is <strong>€13,000 or less</strong> a year",
      "Full medical card holders and people aged <strong>70 or over</strong> with income of <strong>€60,000 or less</strong> pay a maximum of 2% (0.5% on the first €12,012, 2% on the rest). A GP visit card doesn't qualify",
      "Self-employed income over <strong>€100,000</strong> has an extra 3% (11% in total)"])}
<h2 id="prsi">PRSI and minimum wage</h2>
<div class="table-wrap"><table>{head}<tbody>{prsi}</tbody></table></div>
{lis(["No employee PRSI if you earn <strong>€352 a week or less</strong>", "Between €352.01 and €424 a week you get a PRSI credit of up to €12 a week",
      "Employees aged 66 or over don't pay PRSI", "Self-employed (Class S): same rate on all income over €5,000, minimum €650 a year"])}
<div class="cta"><h2>See what it means for you</h2><p>Put these rates to work on your own salary.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("tax-rates.html", page("tax-rates.html", f"Irish Tax Rates {PREV}, {CURRENT} & {NEXT} – Tax Bands, Credits, USC & PRSI",
                                 f"Irish income tax bands, tax credits, USC bands and PRSI rates for {PREV}, {CURRENT} and {NEXT} (Budget 2027) in one table. Single, married, single parent.",
                                 body, active="Tax rates", crumbs=[("Take-home pay", "./"), ("Tax rates", None)], h1=f"Irish tax rates and credits {PREV}–{NEXT}",
                                 share_text=f"All the Irish tax rates for {CURRENT} and {NEXT} in one place:"))
    with open(os.path.join(ROOT, "rates.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"source": BASE + "tax-rates.html", "checked": CHECKED, "currency": "EUR",
                   "notes": "usc: list of [upper limit of band, rate]; last band has no upper limit (null). prsi: employee Class A rate January-September and from 1 October.",
                   "uscExemptAtOrBelow": 13000, "uscReducedRateIncomeLimit": 60000, "years": YEARS}, f, indent=1)

# ---------------------------------------------------------------- minimum wage
def build_minwage():
    rows = []
    for y in (PREV, CURRENT, NEXT):
        w = Y(y)["minWage"]
        for h in (39, 30, 20):
            g = w * h * 52
            r = calc(y, round(g, 2))
            rows.append(f"<tr><td>{y}</td><td>{eur2(w)}</td><td>{h}</td><td>{eur(g)}</td><td>{eur2(r['net'] / 52)}</td><td>{eur(r['net'] / 12)}</td></tr>")
    ft26 = calc(CURRENT, round(Y(CURRENT)["minWage"] * 39 * 52, 2)); ft27 = calc(NEXT, round(Y(NEXT)["minWage"] * 39 * 52, 2))
    facts = [f"The national minimum wage is <strong>{eur2(Y(CURRENT)['minWage'])} an hour in {CURRENT}</strong> and <strong>{eur2(Y(NEXT)['minWage'])} from 1 January {NEXT}</strong>.",
             f"Full-time (39 hours) on minimum wage in {NEXT} is {eur(Y(NEXT)['minWage'] * 39 * 52)} a year – about <strong>{eur2(ft27['net'] / 52)} a week after tax</strong> (vs {eur2(ft26['net'] / 52)} in {CURRENT}).",
             "Under-18s, 18-year-olds and 19-year-olds can be paid 70%, 80% and 90% of the full rate."]
    body = f"""<p class="lead">Ireland's minimum wage for {PREV}, {CURRENT} and {NEXT}, and what it comes to after tax per week and month.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(facts)}
<h2>Minimum wage take-home pay</h2>
<div class="table-wrap"><table><thead><tr><th>Year</th><th>Per hour</th><th>Hours / week</th><th>Gross / year</th><th>Net / week</th><th>Net / month</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="muted small">Single PAYE employee, working all year. Part-time workers on low hours often pay no income tax because their tax credits cover it, and no PRSI if they earn €352 a week or less.</p>
<h2>Minimum wage by age ({NEXT})</h2>
<div class="table-wrap"><table><thead><tr><th>Age</th><th>% of minimum wage</th><th>Per hour {CURRENT}</th><th>Per hour {NEXT}</th></tr></thead><tbody>
<tr><td>Under 18</td><td>70%</td><td>{eur2(Y(CURRENT)['minWage'] * .7)}</td><td>{eur2(Y(NEXT)['minWage'] * .7)}</td></tr>
<tr><td>Age 18</td><td>80%</td><td>{eur2(Y(CURRENT)['minWage'] * .8)}</td><td>{eur2(Y(NEXT)['minWage'] * .8)}</td></tr>
<tr><td>Age 19</td><td>90%</td><td>{eur2(Y(CURRENT)['minWage'] * .9)}</td><td>{eur2(Y(NEXT)['minWage'] * .9)}</td></tr>
<tr><td>20 and over</td><td>100%</td><td>{eur2(Y(CURRENT)['minWage'])}</td><td>{eur2(Y(NEXT)['minWage'])}</td></tr></tbody></table></div>
<div class="cta"><h2>Paid by the hour?</h2><p>Enter your hourly rate and hours to see your weekly take-home pay.</p><a class="btn" href="./?gross={Y(NEXT)['minWage']}&amp;period=hour&amp;year={NEXT}">Calculate hourly pay</a></div>"""
    faqs = [(f"What is the minimum wage in Ireland in {NEXT}?", f"{eur2(Y(NEXT)['minWage'])} an hour from 1 January {NEXT}, up from {eur2(Y(CURRENT)['minWage'])} in {CURRENT}."),
            ("How much is minimum wage per week after tax in Ireland?", f"For a 39-hour week, about {eur2(ft26['net'] / 52)} in {CURRENT} and {eur2(ft27['net'] / 52)} in {NEXT} for a single PAYE employee.")]
    body += "<h2>Questions</h2>" + faq_html(faqs)
    write("minimum-wage.html", page("minimum-wage.html", f"Minimum Wage Ireland {NEXT} (€14.94) – Take-Home Pay per Week After Tax",
                                    f"Ireland's minimum wage is €14.15 in {CURRENT} and €14.94 from January {NEXT}. See take-home pay per week and month after tax for full-time and part-time hours.",
                                    body, jsonld=[faq_ld(faqs)], crumbs=[("Take-home pay", "./"), ("Minimum wage", None)], h1=f"Minimum wage Ireland {CURRENT} and {NEXT}",
                                    share_text="Minimum wage in Ireland – what it comes to per week after tax:"))

# ---------------------------------------------------------------- annual leave + public holidays
def ph_table(y):
    rows = "".join(f"<tr><td>{n}</td><td>{nice_date(d)}</td></tr>" for n, d in public_holidays(y))
    return f'<div class="table-wrap"><table><thead><tr><th>Public holiday</th><th>{y}</th></tr></thead><tbody>{rows}</tbody></table></div>'

def build_holidays():
    body = f"""<p class="lead">Work out how many days of paid annual leave you're entitled to in Ireland – full-time, part-time or zero-hours – and what you're owed for public holidays.</p>
<p class="updated">Based on the Organisation of Working Time Act 1997 · Checked {CHECKED}</p>
{key_facts(["Full-time workers get at least <strong>4 working weeks</strong> of paid annual leave a year (20 days on a 5-day week).",
            "Part-time workers get <strong>8% of the hours they work</strong>, up to 4 working weeks.",
            "You also get <strong>10 public holidays</strong> a year. Part-time workers need to have worked 40 hours in the 5 weeks before.",
            "Leave builds up from your first day. You're paid for unused leave when you leave a job."])}
<form id="leave" class="card" novalidate>
  <fieldset>
    <legend>Your working pattern</legend>
    <div class="two">
      <label>Hours you work per week<input id="lv_hours" type="number" min="1" max="80" step="0.5" inputmode="decimal" value="39"></label>
      <label>Days you work per week<input id="lv_days" type="number" min="1" max="7" step="0.5" inputmode="decimal" value="5"></label>
    </div>
    <div class="two">
      <label>Months worked this leave year<select id="lv_months">{"".join(f'<option value="{m}"{" selected" if m == 12 else ""}>{m} month{"s" if m > 1 else ""}</option>' for m in range(1, 13))}</select></label>
      <label>Hourly rate (optional, €)<input id="lv_rate" type="number" min="0" step="0.01" inputmode="decimal" placeholder="{Y(CURRENT)['minWage']}"></label>
    </div>
    <label>Or, if your hours vary: total hours worked this leave year (optional)<input id="lv_total" type="number" min="0" step="1" inputmode="decimal" placeholder="e.g. 1,200"></label>
  </fieldset>
  <div class="btn-row"><button type="submit" class="btn primary">Calculate my annual leave</button></div>
</form>
<div id="lv_out" aria-live="polite"></div>

<h2>How annual leave is calculated in Ireland</h2>
<p>The law gives you whichever of these three methods works out best for you:</p>
<div class="card"><ol class="steps">
<li><strong>Working week method:</strong> 4 working weeks in a leave year in which you work at least 1,365 hours (unless it's a year you change job).</li>
<li><strong>Calendar month method:</strong> one-third of a working week for each month in which you work at least 117 hours.</li>
<li><strong>Hours worked method:</strong> 8% of the hours you work in a leave year, up to a maximum of 4 working weeks.</li>
</ol></div>
<p class="muted small">The leave year usually runs from April to March or January to December – check your contract. Hours on annual leave, maternity leave and certain other leave count as hours worked.</p>

<div class="ad" data-slot="content"></div>

<h2 id="public-holidays">Public holiday entitlement</h2>
<p>For each public holiday you're entitled to <strong>one</strong> of these, chosen by your employer:</p>
{lis(["A paid day off on the day", "A paid day off within a month", "An extra day of annual leave", "An extra day's pay"])}
<p>Full-time workers qualify straight away. Part-time workers qualify if they've worked at least <strong>40 hours in the 5 weeks</strong> before the public holiday. If a public holiday falls on a day you don't normally work, you get one-fifth of your weekly pay.</p>
<p>There are 10 public holidays in Ireland. <a href="public-holidays.html">See all the dates for {CURRENT} and {NEXT} →</a></p>
"""
    faqs = [("How many days annual leave am I entitled to in Ireland?", "At least 4 working weeks a year if you work full-time – 20 days on a 5-day week. Part-time workers get 8% of the hours they work, up to 4 working weeks. Your contract can give you more."),
            ("Do part-time workers get annual leave in Ireland?", "Yes. Part-time workers get 8% of the hours they work as paid leave, up to 4 working weeks. For example, 1,000 hours worked gives 80 hours of leave."),
            ("Am I paid for public holidays if I'm part-time?", "Yes, if you've worked at least 40 hours in the 5 weeks before the public holiday. If it's a day you don't normally work, you get one-fifth of your weekly pay."),
            ("Do I get paid for unused annual leave when I leave a job?", "Yes. When you leave, your employer must pay you for any annual leave you've built up and not taken, and for a public holiday that falls in your last week if you worked 4 weeks before it.")]
    body += "<h2>Annual leave questions</h2>" + faq_html(faqs)
    write("holidays.html", page("holidays.html", "Annual Leave Calculator Ireland – Holiday Entitlement for Full & Part-Time Workers",
                                "Free Irish annual leave calculator: work out your holiday entitlement in days and hours (4 weeks, 8% of hours or the month method), holiday pay and public holiday entitlement.",
                                body, active="Annual leave", jsonld=[faq_ld(faqs), {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Annual Leave Calculator",
                                "url": BASE + "holidays.html", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
                                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}],
                                crumbs=[("Take-home pay", "./"), ("Annual leave", None)], scripts=["js/holidays.js"], h1="Annual leave calculator Ireland",
                                share_text="Free annual leave calculator for Ireland – check how many holidays you're owed:"))

    ph_cur, ph_next = public_holidays(CURRENT), public_holidays(NEXT)
    weekend = [f"{n} ({nice_date(d)})" for n, d in ph_cur + ph_next if d.weekday() >= 5]
    data = [{"name": n, "date": d.isoformat()} for n, d in ph_cur + ph_next]
    facts = [f"Ireland has <strong>10 public holidays</strong> a year.",
             f"The next public holidays are listed below – Christmas Day {CURRENT} is on a {datetime.date(CURRENT, 12, 25).strftime('%A')}.",
             f"St Brigid's Day is the first Monday in February, or 1 February if that's a Friday – in {NEXT} it's {nice_date(ph_next[1][1])}.",
             "When a public holiday falls at the weekend there's no automatic day off on Monday – you get your normal public holiday benefit instead (often a paid day off or an extra day's leave)."]
    body = f"""<p class="lead">All the bank holidays (public holidays) in Ireland for {CURRENT} and {NEXT}, and what you're entitled to on each one.</p>
<p class="updated">Checked {CHECKED}</p>
<div id="nextPh" class="earliest" hidden></div>
{key_facts(facts)}
<h2>Bank holidays {CURRENT}</h2>{ph_table(CURRENT)}
<h2>Bank holidays {NEXT}</h2>{ph_table(NEXT)}
<p class="muted small">Weekend public holidays: {"; ".join(weekend) if weekend else "none"}. Good Friday is not a public holiday, although many businesses close.</p>
<div class="ad" data-slot="content"></div>
<h2>What you're entitled to</h2>
<p>For each public holiday your employer gives you one of: a paid day off on the day, a paid day off within a month, an extra day of annual leave, or an extra day's pay. Part-time workers need 40 hours worked in the previous 5 weeks. <a href="holidays.html#public-holidays">More on public holiday pay →</a></p>
<div class="cta"><h2>How much annual leave do you get?</h2><p>Work out your holiday entitlement in days and hours.</p><a class="btn" href="holidays.html">Annual leave calculator</a></div>
<script>
(function(){{var H={json.dumps(data)};var t=new Date();t.setHours(0,0,0,0);
for(var i=0;i<H.length;i++){{var p=H[i].date.split("-"),d=new Date(+p[0],+p[1]-1,+p[2]);if(d>=t){{var n=Math.round((d-t)/864e5),el=document.getElementById("nextPh");
el.innerHTML='<div class="tl">Next bank holiday</div><div class="ed">'+H[i].name+'</div><div>'+d.toLocaleDateString("en-IE",{{weekday:"long",day:"numeric",month:"long",year:"numeric"}})+' · '+(n===0?'today':n===1?'tomorrow':'in '+n+' days')+'</div>';el.hidden=false;break;}}}}}})();
</script>"""
    ph_faq = [(f"What are the bank holidays in Ireland in {y}?", "; ".join(f"{n}: {nice_date(d)}" for n, d in public_holidays(y)) + ".") for y in (CURRENT, NEXT)]
    ph_faq.append(("How many public holidays are there in Ireland?", "There are 10 public holidays a year, including St Brigid's Day, which was added in 2023."))
    events = [faq_ld(ph_faq)]
    write("public-holidays.html", page("public-holidays.html", f"Bank Holidays Ireland {CURRENT} & {NEXT} – All 10 Public Holiday Dates",
                                       f"All Irish bank holidays for {CURRENT} and {NEXT}: New Year's Day, St Brigid's Day, St Patrick's Day, Easter Monday, May, June, August and October bank holidays, Christmas and St Stephen's Day.",
                                       body, active="Bank holidays", jsonld=events, crumbs=[("Take-home pay", "./"), ("Bank holidays", None)],
                                       h1=f"Bank holidays in Ireland {CURRENT} and {NEXT}",
                                       share_text=f"All the Irish bank holidays for {CURRENT} and {NEXT}:"))

# ---------------------------------------------------------------- FAQ
def build_faq():
    c, n = Y(CURRENT), Y(NEXT)
    x = calc(CURRENT, 40000)
    FAQ = [
        ("How is take-home pay calculated in Ireland?", f"Your employer deducts three things from your gross pay: income tax (PAYE) at 20% and 40% minus your tax credits, the Universal Social Charge (USC), and PRSI. What's left is your net or take-home pay. For example, a single person on €40,000 takes home {eur2(x['net'])} a year in {CURRENT}."),
        ("What is the 40% tax threshold in Ireland?", f"{eur(c['band']['single'])} for a single person in {CURRENT}, rising to {eur(n['band']['single'])} in {NEXT}. It's {eur(c['band']['married'])} ({eur(n['band']['married'])} in {NEXT}) for a married couple with one income and {eur(c['band']['parent'])} ({eur(n['band']['parent'])}) for a single parent."),
        ("What tax credits does everyone get?", f"A single PAYE employee gets the Personal credit ({eur(c['credits']['personal'])}) and the Employee credit ({eur(c['credits']['employee'])}) – {eur(c['credits']['personal'] + c['credits']['employee'])} a year in {CURRENT} and {eur(n['credits']['personal'] + n['credits']['employee'])} in {NEXT}. Self-employed people get the Earned Income credit instead of the Employee credit."),
        ("What is joint assessment?", f"Married couples and civil partners can be taxed together. You share a bigger 20% band ({eur(c['band']['married'])}, plus up to {eur(c['band']['secondMax'])} more if you both work) and both personal credits. It usually saves tax when one partner earns much more than the other. Choose 'Married' in the calculator's advanced options."),
        ("Do medical card holders pay less USC?", "Yes. If you have a full medical card (not a GP visit card) and your income is €60,000 or less, you pay a maximum USC rate of 2%: 0.5% on the first €12,012 and 2% on the rest. The same applies if you're 70 or over. The medical card concession runs to the end of 2027."),
        ("Who doesn't pay USC?", "Anyone whose total income for the year is €13,000 or less pays no USC. Social welfare payments are also exempt from USC."),
        ("Who doesn't pay PRSI?", "Employees earning €352 a week or less pay no PRSI, and people aged 66 or over don't pay employee PRSI. Between €352 and €424 a week you get a PRSI credit that reduces what you pay."),
        ("Why does PRSI change in October?", f"The government is increasing PRSI by stages to fund pensions: {pct(c['prsi']['jan'])} to {pct(c['prsi']['oct'])} on 1 October {CURRENT}, and {pct(n['prsi']['jan'])} to {pct(n['prsi']['oct'])} on 1 October {NEXT}. The calculator uses a weighted average for the whole year."),
        ("How does a pension contribution reduce my tax?", "Contributions to an occupational pension or PRSA get tax relief at your highest rate (20% or 40%), within age-related limits (15% of earnings under 30 up to 40% at 60+, on earnings up to €115,000). They don't reduce USC or PRSI."),
        ("What is the Rent Tax Credit?", f"If you rent your home, you can claim 20% of the rent you pay, up to {eur(c['credits']['rentSingle'])} a person ({eur(c['credits']['rentCouple'])} for a jointly assessed couple) in {CURRENT}, rising to {eur(n['credits']['rentSingle'])} ({eur(n['credits']['rentCouple'])}) in {NEXT}. Claim it in Revenue's myAccount."),
        ("Why is my payslip different from the calculator?", "Common reasons: emergency tax (Revenue doesn't have your details yet), starting the job mid-year, benefit-in-kind such as a company car or health insurance, salary sacrifice, overtime, or tax credits split differently between spouses. Check your tax credit certificate in Revenue's myAccount."),
        ("What is emergency tax?", "If your employer doesn't have a Revenue Payroll Notification for you, you're taxed at 40% with no credits and higher USC. Register your job in Revenue's myAccount to fix it – overpaid tax is refunded through your next payslips."),
        ("What is the difference between gross and net pay?", "Gross pay is your salary before deductions. Net pay (take-home pay) is what's paid into your bank account after income tax, USC, PRSI and things like pension contributions."),
        ("Is this calculator official?", "No. It's a free, independent tool from Tavion based on Revenue's published rates and the Budget. Your actual tax is worked out by Revenue and your employer."),
    ]
    body = f"""<p class="lead">Answers to common questions about tax, USC, PRSI and take-home pay in Ireland.</p>
<p class="updated">Checked {CHECKED}</p>
{faq_html(FAQ)}
<div class="cta"><h2>Work out your pay</h2><p>See your take-home pay per month, week and hour.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("faq.html", page("faq.html", f"Irish Tax FAQ {CURRENT}/{NEXT} – Income Tax, USC, PRSI & Take-Home Pay Explained",
                           "Answers about Irish income tax, tax credits, USC, PRSI, joint assessment, medical card USC, Rent Tax Credit, pensions and emergency tax.",
                           body, active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Take-home pay", "./"), ("FAQ", None)], h1="Tax and take-home pay FAQ"))

# ---------------------------------------------------------------- og image
def build_og():
    path = os.path.join(ROOT, "og.png")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (11, 15, 25))
    d = ImageDraw.Draw(im)
    for i in range(H):  # soft violet glow
        a = max(0, 1 - i / 520)
        d.line([(0, i), (W, i)], fill=(int(11 + 40 * a), int(15 + 22 * a), int(25 + 70 * a)))
    def font(size, bold=True):
        for name in (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()
    d.rounded_rectangle([70, 70, 330, 116], 23, fill=(91, 63, 209))
    d.text((92, 78), "BUDGET 2027", font=font(28), fill=(255, 255, 255))
    d.text((70, 160), "Take-Home Pay", font=font(92), fill=(241, 245, 249))
    d.text((70, 262), "Calculator Ireland", font=font(92), fill=(167, 139, 250))
    d.text((70, 400), "Net pay after income tax, USC & PRSI", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 452), "per year · month · week · day · hour", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 545), "tavion.ie/salary  ·  free, no sign-up", font=font(32), fill=(56, 189, 248))
    im.save(path, optimize=True)

# ---------------------------------------------------------------- site-wide files (sitemap, llms.txt)
def update_sitemap(files):
    path = os.path.join(REPO, "sitemap.xml")
    with open(path, encoding="utf-8") as f:
        xml = f.read()
    xml = re.sub(r"\s*<url><loc>https://tavion\.ie/salary/[^<]*</loc>.*?</url>", "", xml)
    entries = "".join(f'\n  <url><loc>{BASE}{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>' for fn, pr in files)
    xml = xml.replace("\n</urlset>", entries + "\n</urlset>")
    xml = re.sub(r"(<loc>https://tavion\.ie/</loc><lastmod>)[^<]*", r"\g<1>" + TODAY, xml)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

def write_llms():
    """llms.txt: a plain-text map of the site for AI assistants and answer engines (llmstxt.org)."""
    c, n = Y(CURRENT), Y(NEXT)
    ex = {a: (calc(CURRENT, a), calc(NEXT, a)) for a in (30000, 40000, 50000, 60000, 80000, 100000)}
    lines = [
        "# Tavion", "",
        "> Free, simple web apps for everyday life in Ireland. No sign-up, nothing to install. Made in Ireland.", "",
        "## Apps", "",
        "- [Irish Take-Home Pay Calculator](https://tavion.ie/salary/): salary after income tax, USC and PRSI for 2025, 2026 and 2027 (Budget 2027); single, single parent, married one/two incomes (joint assessment), medical card USC, pension, Rent Tax Credit. Net pay per year, month, fortnight, week, day and hour.",
        "- [Driver Theory Test Practice](https://tavion.ie/driving/): free Irish driver theory test practice for car and motorcycle, 40-question mock exams.",
        "- [Irish Citizenship Calculator](https://tavion.ie/citizenship/): reckonable residence days and earliest naturalisation application date from IRP stamps.", "",
        "## Take-home pay: key pages", "",
        "- [Budget 2027 tax changes](https://tavion.ie/salary/budget-2027.html): what changed from 1 January 2027 and how much better off you are at each salary",
        "- [Irish tax rates 2025-2027](https://tavion.ie/salary/tax-rates.html): tax bands, credits, USC and PRSI side by side ([JSON](https://tavion.ie/salary/rates.json))",
        "- [Salary after tax table](https://tavion.ie/salary/salaries.html): net pay for every salary from €15,000 to €200,000",
        "- [Minimum wage](https://tavion.ie/salary/minimum-wage.html): €14.15 (2026), €14.94 (2027) and take-home pay",
        "- [Annual leave calculator](https://tavion.ie/salary/holidays.html): statutory annual leave and public holiday entitlement",
        f"- [Bank holidays {CURRENT} and {NEXT}](https://tavion.ie/salary/public-holidays.html)",
        "- [Tax FAQ](https://tavion.ie/salary/faq.html)", "",
        "## Take-home pay: key facts", "",
        f"- Income tax: 20% up to {eur(c['band']['single'])} (single, {CURRENT}) / {eur(n['band']['single'])} ({NEXT}); 40% above. Married one income {eur(c['band']['married'])} / {eur(n['band']['married'])}; single parent {eur(c['band']['parent'])} / {eur(n['band']['parent'])}.",
        f"- Personal and Employee credits: {eur(c['credits']['personal'])} each in {CURRENT}; {eur(n['credits']['personal'])} each in {NEXT}.",
        f"- USC {CURRENT}: 0.5% to €12,012; 2% to {eur(c['usc'][1][0])}; 3% to €70,044; 8% above. {NEXT}: 2% band to {eur(n['usc'][1][0])}. Exempt at €13,000 or less. Full medical card or 70+ with income ≤ €60,000: max 2%.",
        f"- Employee PRSI: {pct(c['prsi']['jan'])} ({CURRENT}, {pct(c['prsi']['oct'])} from 1 Oct); {pct(n['prsi']['jan'])} ({NEXT}, {pct(n['prsi']['oct'])} from 1 Oct). None at €352/week or less.",
    ] + [f"- {eur(a)} after tax (single PAYE): {eur(p[0]['net'])}/year ({eur(p[0]['net'] / 12)}/month) in {CURRENT}; {eur(p[1]['net'])}/year ({eur(p[1]['net'] / 12)}/month) in {NEXT}. Details: https://tavion.ie/salary/{slug(a)}" for a, p in ex.items()] + [
        "", "## Optional", "",
        "- [IT services](https://tavion.ie/services.html)", "- [Privacy](https://tavion.ie/privacy.html)", ""]
    with open(os.path.join(REPO, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    # Other apps add their own sections to llms.txt – put them back.
    import sys
    sys.path.insert(0, HERE)
    if os.path.isdir(os.path.join(REPO, "rent")):
        import build_rent
        build_rent.update_llms()
    if os.path.isdir(os.path.join(REPO, "mortgage")):
        import build_mortgage
        build_mortgage.update_llms()
    if os.path.isdir(os.path.join(REPO, "stamp-duty")):
        import build_stamp
        build_stamp.update_llms()

if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    build_index(); build_salary_pages(); build_budget(); build_rates(); build_minwage(); build_holidays(); build_faq(); build_og()
    files = [("index.html", "0.9"), ("budget-2027.html", "0.9"), ("salaries.html", "0.8"), ("tax-rates.html", "0.8"), ("minimum-wage.html", "0.7"),
             ("holidays.html", "0.8"), ("public-holidays.html", "0.8"), ("faq.html", "0.7")] + [(slug(a), "0.6") for a in AMOUNTS]
    update_sitemap(files); write_llms()
    print("Built", len(files), "pages in", os.path.normpath(ROOT))
