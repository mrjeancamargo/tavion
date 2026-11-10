"""
Builds the static pages of the Irish Mortgage Calculator app (tavion.ie/mortgage/).

Run from the repo root:   python tools/build_mortgage.py
Needs Node.js: every figure comes from mortgage/js/mortgage.js (which uses salary/js/tax.js
for take-home pay), the same engine the calculator uses.

When rules, rates or rents change: update RULES / RENT / FHS in mortgage/js/mortgage.js,
the CHECKED date below, then re-run.
"""
import datetime, json, os, re, subprocess
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.join(REPO, "mortgage")
ENGINE = os.path.join(ROOT, "js", "mortgage.js")
SITE = "https://tavion.ie/"
BASE = SITE + "mortgage/"
CHECKED = "November 2026"
TODAY = datetime.date.today()

INCOMES = list(range(30000, 150001, 5000))
LOANS = list(range(150000, 700001, 25000))
RATES = [3.0, 3.5, 4.0, 4.5, 5.0]
TERMS = [20, 25, 30, 35]

SRC = {
    "cbi": ("Central Bank of Ireland – Mortgage measures", "https://www.centralbank.ie/financial-system/financial-stability/macro-prudential-policy/mortgage-measures"),
    "cbi_bridge": ("Central Bank – Amendment for home bridging loans (April 2026)", "https://www.centralbank.ie/news/article/press-release-targeted-amendment-to-mortgage-measures-home-bridging-loans-8-april-2026"),
    "cbi_rates": ("RTÉ – Central Bank mortgage rate figures (August 2026)", "https://www.rte.ie/news/business/2026/1014/1595354-central-bank-mortgage-figures/"),
    "htb": ("Citizens Information – Help to Buy scheme", "https://www.citizensinformation.ie/en/housing/owning-a-home/help-with-buying-a-home/help-to-buy-scheme/"),
    "htb_rev": ("Revenue – Help to Buy incentive", "https://www.revenue.ie/en/property/help-to-buy-incentive/index.aspx"),
    "htb_b27": ("RTÉ – Help to Buy increased by €5,000 (Budget 2027)", "https://www.rte.ie/news/business/2026/1006/1594234-housing-budget-2027/"),
    "fhs": ("First Home Scheme – property price ceilings", "https://www.firsthomescheme.ie/about-the-scheme/property-price-ceilings/"),
    "fhs_ci": ("Citizens Information – First Home Scheme", "https://www.citizensinformation.ie/en/housing/owning-a-home/help-with-buying-a-home/first-home-scheme/"),
    "stamp": ("Revenue – Stamp duty on residential property", "https://www.revenue.ie/en/property/stamp-duty/property/residential-property.aspx"),
    "ccpc": ("CCPC – Mortgages (compare lenders and costs)", "https://www.ccpc.ie/consumers/money/mortgages/"),
    "rtb_index": ("RTB – Rent Index Q1 2026 (average rents by county)", "https://rtb.ie/wp-content/uploads/2026/09/RTB-Rent-Index-Q1-2026.pdf"),
    "lahl": ("Local Authority Home Loan", "https://localauthorityhomeloan.ie/"),
    "ci_buying": ("Citizens Information – Buying a home", "https://www.citizensinformation.ie/en/housing/owning-a-home/buying-a-home/"),
}

TABS = [("./", "Calculator"), ("how-much-can-i-borrow.html", "Borrowing"), ("repayments.html", "Repayments"), ("costs-of-buying.html", "Costs"),
        ("schemes.html", "HTB &amp; FHS"), ("moving-home.html", "Movers"), ("faq.html", "FAQ")]
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

# ---------------------------------------------------------------- engine
NODE = r"""
const M = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.kind === "calc" ? M.calc(x.inp) : x.kind === "pay" ? M.payment(x.loan, x.rate, x.term) : x.kind === "stamp" ? M.stampDuty(x.price, x.nb) : null);
  process.stdout.write(JSON.stringify({ rules: M.RULES, rent: M.RENT, fhs: M.FHS, names: M.COUNTY_NAMES, fees: M.FEES, res: res }));
});
"""
def engine(q):
    p = subprocess.run(["node", "-e", NODE, ENGINE], input=json.dumps(q), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)

META = engine([])
RULES, RENT, FHS, NAMES, FEES = META["rules"], META["rent"], META["fhs"], META["names"], META["fees"]

def batch(q):
    return engine(q)["res"]

# ---------------------------------------------------------------- formatting / shell
def eur(n, dp=0):
    return ("−" if n < 0 else "") + "€" + f"{abs(n):,.{dp}f}"

def lis(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def table(head, rows, cls=""):
    return (f'<div class="table-wrap"><table{(" class=" + chr(34) + cls + chr(34)) if cls else ""}><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) +
            "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")

def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a in pairs]}

def faq_html(pairs):
    return "".join(f'<details class="faq"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in pairs)

def key_facts(items):
    return '<div class="facts-box"><h2 class="tl">Key facts</h2><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"

def sources_block(keys):
    return ('<div class="sources"><h2 class="tl">Sources – check them yourself</h2><ul>' +
            "".join(f'<li><a href="{SRC[k][1]}" rel="noopener" target="_blank">{SRC[k][0]}</a></li>' for k in keys) + "</ul></div>")

def try_also(items):
    return '<div class="try"><h2 class="tl">Try also</h2><div class="try-grid">' + "".join(
        f'<a href="{h}" data-track="cross_app" data-label="{lab}"><b>{icon}</b><span><strong>{t}</strong>{d}</span></a>' for icon, t, d, h, lab in items) + "</div></div>"

CROSS = [("💶", "Take-home pay calculator", "Your net pay after tax, USC and PRSI", "../salary/", "salary"),
         ("🏠", "Rent increase checker", "Is your rent increase legal?", "../rent/", "rent")]

def share_html(text, url, label):
    wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
    fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
    return (f'<h2>Share it</h2><p class="muted">Know someone saving for a home? Send them this.</p><div class="share">'
            f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
            f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

def page(filename, title, desc, body, active=None, jsonld=(), crumbs=None, slot="content", scripts=(), share_text=None, h1=None, sources=("cbi", "stamp", "htb"), cross=True):
    url = BASE if filename == "index.html" else BASE + filename
    on = ' class="on"'
    tabs = "".join(f'<a href="{href}"{on if label == active else ""}>{label}</a>' for href, label in TABS)
    crumb_html = ""
    if crumbs:
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs) + "</nav>"
        items = [{"@type": "ListItem", "position": i + 1, "name": t, "item": (BASE + (h if h not in ("./", None) else "")) if h else url} for i, (t, h) in enumerate(crumbs)]
        jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "WebPage", "name": re.sub("&amp;", "&", title), "url": url, "description": desc, "inLanguage": "en-IE",
                              "dateModified": TODAY.isoformat(), "isPartOf": {"@type": "WebSite", "name": "Tavion", "url": SITE},
                              "publisher": {"@type": "Organization", "name": "Tavion", "url": SITE, "logo": SITE + "images/logo.png"},
                              "citation": [SRC[k][1] for k in sources]}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
    extra = "".join(f'<script src="{s}"></script>' for s in scripts)
    share = share_html(share_text or "Free Irish mortgage calculator – how much you can borrow, deposit, stamp duty and repayments:", url, filename.replace(".html", ""))
    pop = " · ".join(f'<a href="borrow-{a}.html">{eur(a)}</a>' for a in (40000, 50000, 60000, 70000, 80000, 100000, 120000))
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
<meta name="theme-color" content="#b45309">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>🔑</b> Mortgage Calculator</a><a class="small" href="../" data-track="apps_click" data-label="mortgage_header">More Tavion apps</a></div>
  <nav class="tabs" aria-label="Sections"><div class="wrap">{tabs}</div></nav>
</header>
<main class="wrap">
{crumb_html}
{('<h1>' + h1 + '</h1>') if h1 else ''}
{body}
{try_also(CROSS) if cross else ''}
{sources_block(sources)}
<div class="ad" data-slot="{slot}"></div>
{share}
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Mortgage pages"><a href="./">Mortgage calculator</a><a href="how-much-can-i-borrow.html">How much can I borrow?</a><a href="repayments.html">Repayment tables</a><a href="costs-of-buying.html">Costs of buying</a><a href="schemes.html">Help to Buy &amp; First Home Scheme</a><a href="first-time-buyers.html">First-time buyers</a><a href="moving-home.html">Moving home</a><a href="central-bank-rules.html">Central Bank rules</a><a href="faq.html">FAQ</a></nav>
    <p>How much can I borrow on: {pop}</p>
    <p>By county: {" · ".join(f'<a href="mortgage-{k}.html">{NAMES[k]}</a>' for k in ("dublin", "cork", "galway", "limerick", "kildare", "meath", "wicklow", "louth", "waterford"))} · <a href="counties.html">all counties</a></p>
    <p>Figures checked against the Central Bank of Ireland, Revenue, Citizens Information and the RTB in {CHECKED}. This is a free, independent tool from <a href="../">Tavion</a>, not financial advice and not a mortgage offer. Lenders decide what they'll lend – speak to a lender or an authorised mortgage broker, and compare costs on <a href="https://www.ccpc.ie/consumers/money/mortgages/" rel="noopener">ccpc.ie</a>.</p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="mortgage_footer">More free apps from Tavion</a></p>
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

county_opts = "".join(f'<option value="{k}"{" selected" if k == "dublin" else ""}>{NAMES[k]}</option>' for k in sorted(NAMES, key=lambda k: NAMES[k]))
R = RULES

# ---------------------------------------------------------------- calculator
def build_index():
    ex = batch([{"kind": "calc", "inp": {"incomes": [60000], "savings": 40000, "county": "dublin"}}])[0]
    body = f"""<p class="lead">How much can you borrow for a mortgage in Ireland? See your maximum mortgage, the price you can afford, the deposit, stamp duty and fees you need, and your monthly repayments – using the Central Bank rules. Free, no sign-up.</p>
<ul class="facts"><li>4× income (first-time buyers)</li><li>3.5× income (movers)</li><li>10% deposit</li><li>Help to Buy €35k</li></ul>

<form id="mortForm" class="card" novalidate>
  <fieldset><legend class="sm">Are you…</legend>
    <div class="seg two-seg"><label><input type="radio" name="buyer" value="ftb" checked><span>First-time buyer<small>Never owned a home</small></span></label><label><input type="radio" name="buyer" value="mover"><span>Moving home<small>Own / owned a home</small></span></label></div>
  </fieldset>
  <fieldset style="margin-top:12px"><legend class="sm">Buying…</legend>
    <div class="seg two-seg"><label><input type="radio" name="who" value="1" checked><span>On my own<small>Sole applicant</small></span></label><label><input type="radio" name="who" value="2"><span>With someone<small>Joint applicants</small></span></label></div>
  </fieldset>
  <label for="inc1" class="big-label" style="margin-top:16px">Your gross salary per year</label>
  <div class="money"><span>€</span><input id="inc1" type="text" inputmode="decimal" autocomplete="off" placeholder="55,000"></div>
  <div id="inc2Box" hidden><label for="inc2" class="big-label" style="margin-top:12px">Their gross salary per year</label>
  <div class="money"><span>€</span><input id="inc2" type="text" inputmode="decimal" autocomplete="off" placeholder="45,000"></div></div>
  <label for="savings" class="big-label" style="margin-top:16px">Savings for the deposit and costs</label>
  <div class="money"><span>€</span><input id="savings" type="text" inputmode="decimal" autocomplete="off" placeholder="40,000"></div>
  <label>Where are you buying?<select id="county">{county_opts}</select></label>

  <details id="adv" class="adv">
    <summary>Advanced options <span class="muted small">– price, new build, Help to Buy, bonus, rate, selling a home…</span></summary>
    <div class="adv-body">
      <label>House price you're looking at (optional)<div class="money"><span>€</span><input id="price" type="text" inputmode="decimal" placeholder="350,000"></div></label>
      <label class="check"><input type="checkbox" id="newBuild"><span>It's a new build (or self-build)</span></label>
      <label class="check"><input type="checkbox" id="apartment"><span>It's an apartment</span></label>
      <div id="ftbOnly">
        <label class="check"><input type="checkbox" id="htb"><span>Use <strong>Help to Buy</strong> <small class="muted">– up to €35,000 (10% of price) back on tax paid, new homes ≤ €500,000</small></span></label>
        <label id="htbTaxRow" hidden>Income tax + DIRT you paid in the last 4 years (optional – we estimate it)<div class="money"><span>€</span><input id="htbTax" type="text" inputmode="decimal" placeholder="from Revenue myAccount"></div></label>
        <label class="check"><input type="checkbox" id="fhs"><span>Use the <strong>First Home Scheme</strong> <small class="muted">– the State takes up to 30% equity (20% with Help to Buy) to bridge the gap</small></span></label>
      </div>
      <div id="moverBox" class="row-card" hidden>
        <strong>Your current home</strong>
        <div class="seg two-seg" style="margin-top:8px"><label><input type="radio" name="selling" value="yes" checked><span>Selling it</span></label><label><input type="radio" name="selling" value="no"><span>Keeping it</span></label></div>
        <div class="two">
          <label>Value now<div class="money"><span>€</span><input id="curVal" type="text" inputmode="decimal" placeholder="350,000"></div></label>
          <label>Mortgage left<div class="money"><span>€</span><input id="curMort" type="text" inputmode="decimal" placeholder="150,000"></div></label>
        </div>
      </div>
      <div class="two">
        <label>Bonus / overtime / commission per year (you)<div class="money"><span>€</span><input id="var1" type="text" inputmode="decimal" placeholder="0"></div></label>
        <label id="var2Row" hidden>Bonus / overtime (them)<div class="money"><span>€</span><input id="var2" type="text" inputmode="decimal" placeholder="0"></div></label>
      </div>
      <label>How much of it lenders count (%)<input id="varPct" type="number" min="0" max="100" step="5" inputmode="numeric" placeholder="50"></label>
      <label class="check" id="jointRow" hidden><input type="checkbox" id="joint" checked><span>Married or civil partners (taxed jointly – used for take-home pay)</span></label>
      <div class="two">
        <label>Interest rate (%)<input id="rate" type="number" min="0" max="15" step="0.05" inputmode="decimal" placeholder="{R['avgRate']}"></label>
        <label>Term (years)<input id="term" type="number" min="5" max="35" step="1" inputmode="numeric" placeholder="30"></label>
      </div>
      <div class="two">
        <label>Other loan repayments per month (car, credit card)<input id="debts" type="number" min="0" step="10" inputmode="decimal" placeholder="0"></label>
        <label>You can save per month<input id="mSave" type="number" min="0" step="50" inputmode="decimal" placeholder="0"></label>
      </div>
      <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
    </div>
  </details>
  <div class="btn-row"><button type="submit" class="btn primary">Show what I can afford</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Everything is worked out on your device. Nothing is sent to us – and it's not a credit check.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>

<h2>How mortgage limits work in Ireland</h2>
<div class="card"><ol class="steps">
<li><strong>Income limit (LTI).</strong> First-time buyers can borrow up to <strong>4 times</strong> their gross income; second and subsequent buyers (movers) up to <strong>3.5 times</strong>. Couples add their incomes together.</li>
<li><strong>Deposit (LTV).</strong> You need at least a <strong>10% deposit</strong> for a home you'll live in (30% for buy-to-let). Help to Buy can count towards it.</li>
<li><strong>Exceptions.</strong> Lenders can go above these limits for up to 15% of their home lending – so some people get more, but don't count on it.</li>
<li><strong>Costs on top.</strong> Stamp duty (1% up to €1m), solicitor, valuation, survey and Land Registry fees – usually €8,000–€10,000 on a €350,000 home.</li>
</ol></div>
<p>Example: a single first-time buyer earning €60,000 with €40,000 saved can borrow up to <strong>{eur(ex['maxLoanLTI'])}</strong> and buy a home of about <strong>{eur(ex['maxPrice'])}</strong> in Dublin, paying about <strong>{eur(ex['monthly'])} a month</strong> over 30 years at {R['avgRate']}% – {eur(ex['rentDiff'])} less than the average new rent in Dublin.</p>
<div class="cta"><h2>How much could you borrow?</h2><p>See the maximum mortgage for every salary from €30,000 to €150,000.</p><a class="btn" href="how-much-can-i-borrow.html">Borrowing by salary</a></div>
"""
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Mortgage Calculator", "url": BASE, "applicationCategory": "FinanceApplication",
              "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "featureList": ["Maximum mortgage under Central Bank rules (4x / 3.5x income, 90% LTV)", "Sole and joint applicants, first-time buyers and movers",
                              "Help to Buy (€35,000) and First Home Scheme", "Deposit, stamp duty and fees – total cash needed", "Monthly repayments, interest and rate-rise test",
                              "Repayment vs take-home pay and vs average rent by county", "Equity from selling your current home"],
              "description": "Free Irish mortgage affordability calculator: how much you can borrow, the deposit and costs you need, and monthly repayments."}
    faqs = [("How much can I borrow for a mortgage in Ireland?", "First-time buyers can borrow up to 4 times their gross annual income and second and subsequent buyers up to 3.5 times, with at least a 10% deposit. Couples combine their incomes."),
            ("How much deposit do I need to buy a house in Ireland?", "At least 10% of the price for a home you'll live in, plus around €8,000–€10,000 for stamp duty and fees on a typical home. Help to Buy can count towards the deposit on a new home.")]
    write("index.html", page("index.html", "Mortgage Calculator Ireland 2026 – How Much Can I Borrow? Deposit, Stamp Duty & Repayments",
                             "Free Irish mortgage calculator: how much you can borrow (4x / 3.5x income), the house price you can afford, deposit, stamp duty, fees, Help to Buy and monthly repayments. No sign-up.",
                             body, active="Calculator", jsonld=[app_ld, faq_ld(faqs)], slot="calculator",
                             scripts=["../salary/js/tax.js", "js/mortgage.js", "js/calc.js"], h1="Mortgage calculator Ireland",
                             sources=("cbi", "cbi_rates", "htb_b27", "fhs", "stamp", "rtb_index", "ccpc"),
                             share_text="Free Irish mortgage calculator 🏡 How much you can borrow, the deposit and costs you need, and your repayments:"))

# ---------------------------------------------------------------- borrowing by income
def build_borrow():
    q = []
    for a in INCOMES:
        q.append({"kind": "calc", "inp": {"incomes": [a], "savings": 10**7, "county": "dublin"}})            # FTB – income-limited
        q.append({"kind": "calc", "inp": {"buyer": "mover", "incomes": [a], "savings": 10**7, "county": "dublin"}})
    res = batch(q)
    rows = []
    for i, a in enumerate(INCOMES):
        f, m = res[2 * i], res[2 * i + 1]
        lf, lm = a * R["lti"]["ftb"], a * R["lti"]["mover"]
        pf = lf / 0.9
        rows.append([f'<a href="borrow-{a}.html">{eur(a)}</a>', eur(lf), eur(pf), eur(pf * 0.1), eur(f["monthly"]) if False else "", eur(lm)])
    # monthly repayments for the max loans
    pays = batch([{"kind": "pay", "loan": a * R["lti"]["ftb"], "rate": R["avgRate"], "term": 30} for a in INCOMES])
    for i in range(len(rows)):
        rows[i][4] = eur(pays[i])
    body = f"""<p class="lead">How much you can borrow for a mortgage in Ireland at every income, under the Central Bank's limits. Couples: use your combined income.</p>
<p class="updated">Central Bank rules checked {CHECKED} · repayments at {R['avgRate']}% over 30 years</p>
{key_facts(["First-time buyers can borrow up to <strong>4× gross income</strong>; second and subsequent buyers up to <strong>3.5×</strong>.",
            "You need at least a <strong>10% deposit</strong>, so the most you can spend is the mortgage plus your deposit (and Help to Buy on a new home).",
            "Couples combine incomes: two people on €45,000 each can borrow up to <strong>€360,000</strong> as first-time buyers.",
            "Lenders can lend above the limits for up to 15% of their loans – so some borrowers get 4.5× income."])}
{table(["Income", "Max mortgage (FTB, 4×)", "Max price (with 10% deposit)", "Deposit needed", f"Monthly at {R['avgRate']}%", "Max mortgage (mover, 3.5×)"], rows)}
<div class="cta"><h2>Your own figures</h2><p>Add your savings, partner's income, Help to Buy and costs.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("how-much-can-i-borrow.html", page("how-much-can-i-borrow.html", "How Much Can I Borrow for a Mortgage in Ireland? 2026 Table by Salary",
                                             "How much can you borrow in Ireland? Maximum mortgage for every income from €30,000 to €150,000 for first-time buyers (4x) and movers (3.5x), with deposit and repayments.",
                                             body, active="Borrowing", crumbs=[("Mortgage", "./"), ("How much can I borrow?", None)], h1="How much can I borrow? Every income",
                                             sources=("cbi", "cbi_rates", "ccpc")))

    for i, a in enumerate(INCOMES):
        lf, lm = a * 4, a * 3.5
        pf, pm = lf / 0.9, lm / 0.9
        pays = batch([{"kind": "pay", "loan": lf, "rate": r, "term": t} for r in (3.0, R["avgRate"], 4.5) for t in (25, 30, 35)] +
                     [{"kind": "pay", "loan": lm, "rate": R["avgRate"], "term": 30}, {"kind": "stamp", "price": pf, "nb": False}])
        ex = batch([{"kind": "calc", "inp": {"incomes": [a], "savings": pf * 0.1 + 20000, "county": "dublin"}},
                    {"kind": "calc", "inp": {"incomes": [a / 2, a / 2], "savings": pf * 0.1 + 20000, "county": "dublin", "joint": True}}])
        single, couple = ex
        grid = [[f"{r}%"] + [eur(pays[j * 3 + k]) for k in range(3)] for j, r in enumerate((3.0, R["avgRate"], 4.5))]
        cash = pf * 0.1 + pays[10] + sum(FEES[k] for k in FEES)
        facts = [f"On <strong>{eur(a)}</strong> a first-time buyer can borrow up to <strong>{eur(lf)}</strong> (4× income) and buy a home up to about <strong>{eur(pf)}</strong> with a 10% deposit of {eur(pf * 0.1)}.",
                 f"A second or subsequent buyer (mover) on {eur(a)} can borrow up to <strong>{eur(lm)}</strong> (3.5×) – up to about {eur(pm)} with a 10% deposit.",
                 f"Repayments on {eur(lf)}: about <strong>{eur(pays[4])} a month</strong> over 30 years at {R['avgRate']}% (the average new mortgage rate, {R['rateMonth']}).",
                 f"Cash you'd need at {eur(pf)}: about <strong>{eur(cash)}</strong> – deposit, stamp duty ({eur(pays[10])}) and fees."]
        if single.get("netMonthly"):
            facts.append(f"That repayment is about {round(pays[4] / single['netMonthly'] * 100)}% of a single person's take-home pay on {eur(a)} ({eur(single['netMonthly'])} a month).")
        body = f"""<p class="lead">How much can you borrow on a salary of {eur(a)} in Ireland? Your maximum mortgage, the house price you could afford, the deposit and the monthly repayments.</p>
<p class="updated">Central Bank rules · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="hero-num"><div><span class="tl">First-time buyer</span><strong>{eur(lf)}</strong><span class="muted">max mortgage</span></div><div><span class="tl">Mover</span><strong>{eur(lm)}</strong><span class="muted">max mortgage</span></div></div>
<h2>Monthly repayments on {eur(lf)}</h2>
{table(["Rate", "25 years", "30 years", "35 years"], grid)}
<p class="muted small">Total interest over 30 years at {R['avgRate']}%: about {eur(pays[4] * 360 - lf)}.</p>
<div class="ad" data-slot="content"></div>
<h2>Buying on {eur(a)}: single or as a couple?</h2>
<p>A couple with a <strong>combined</strong> income of {eur(a)} has the same limit ({eur(lf)}), but more take-home pay, because two people each get tax credits and lower rates. A couple each earning {eur(a)} could borrow up to <strong>{eur(lf * 2)}</strong>.</p>
{table(["", "Single on " + eur(a), "Couple, " + eur(a / 2) + " each"], [
    ["Max mortgage (FTB)", eur(lf), eur(lf)],
    ["Take-home pay / month", eur(single.get('netMonthly') or 0), eur(couple.get('netMonthly') or 0)],
    ["Repayment share of take-home", f"{single.get('repaymentShare', 0):.0f}%", f"{couple.get('repaymentShare', 0):.0f}%"]])}
<h2>Can I borrow more than 4× {eur(a)}?</h2>
<p>Possibly. Lenders can approve a share of mortgages above the limits (an "exception"), typically up to about 4.5× income – {eur(a * 4.5)} on your salary. Exceptions are limited and go to borrowers with strong finances. Bonus, overtime and commission may be partly counted. Clearing other loans and showing a strong savings record helps.</p>
<div class="cta"><h2>Your exact figures</h2><p>Add savings, a partner's income, Help to Buy and stamp duty.</p><a class="btn" href="./?inc1={a}" data-track="borrow_page_cta" data-label="{a}">Calculate with my details</a></div>
<h2>Other salaries</h2><div class="chip-list">{"".join(f'<a href="borrow-{x}.html">{eur(x)}</a>' for x in INCOMES if x != a and abs(x - a) <= 20000)}<a href="how-much-can-i-borrow.html">All →</a></div>"""
        faqs = [(f"How much can I borrow on {eur(a)} in Ireland?", f"Up to {eur(lf)} as a first-time buyer (4× income) or {eur(lm)} as a second or subsequent buyer (3.5×), with at least a 10% deposit."),
                (f"What house can I afford on {eur(a)}?", f"About {eur(pf)} as a first-time buyer, with a {eur(pf * 0.1)} deposit plus around {eur(pays[10] + sum(FEES.values()))} for stamp duty and fees."),
                (f"What are the repayments on a {eur(lf)} mortgage?", f"About {eur(pays[4])} a month over 30 years at {R['avgRate']}%, or {eur(pays[5])} over 35 years.")]
        write(f"borrow-{a}.html", page(f"borrow-{a}.html", f"How Much Can I Borrow on {eur(a)} in Ireland? Mortgage, Deposit & Repayments 2026",
                                       f"On {eur(a)} you can borrow up to {eur(lf)} as a first-time buyer (4x) or {eur(lm)} as a mover (3.5x). House price, deposit, stamp duty and monthly repayments.",
                                       body, active="Borrowing", jsonld=[faq_ld(faqs)], crumbs=[("Mortgage", "./"), ("Borrowing", "how-much-can-i-borrow.html"), (eur(a), None)],
                                       h1=f"How much can I borrow on {eur(a)}?", sources=("cbi", "cbi_rates", "stamp"),
                                       share_text=f"How much you can borrow on {eur(a)} in Ireland:"))

# ---------------------------------------------------------------- repayments
def build_repay():
    q = [{"kind": "pay", "loan": L, "rate": r, "term": 30} for L in LOANS for r in RATES]
    res = batch(q)
    rows = [[f'<a href="repayments-{L}.html">{eur(L)}</a>'] + [eur(res[i * len(RATES) + j]) for j in range(len(RATES))] for i, L in enumerate(LOANS)]
    body = f"""<p class="lead">Monthly mortgage repayments in Ireland for loans from €150,000 to €700,000 at different interest rates, over 30 years.</p>
<p class="updated">Average new mortgage rate: {R['avgRate']}% ({R['rateMonth']}, Central Bank) · Checked {CHECKED}</p>
{table(["Mortgage"] + [f"{r}%" for r in RATES], rows)}
<p class="muted small">Capital and interest repayments, monthly, 30-year term. Your lender's rate depends on the LTV, the fixed period and whether you have a green (BER A/B) home.</p>
<div class="cta"><h2>Work out your own</h2><p>Any amount, rate and term – plus deposit and costs.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("repayments.html", page("repayments.html", "Mortgage Repayments Ireland 2026 – Monthly Payment Table €150k to €700k",
                                  "Monthly mortgage repayments in Ireland for €150,000 to €700,000 at 3% to 5% over 30 years. See the repayment on your mortgage amount.",
                                  body, active="Repayments", crumbs=[("Mortgage", "./"), ("Repayments", None)], h1="Mortgage repayment table",
                                  sources=("cbi_rates", "ccpc")))
    for L in LOANS:
        res = batch([{"kind": "pay", "loan": L, "rate": r, "term": t} for r in RATES for t in TERMS])
        grid = [[f"{r}%"] + [eur(res[i * len(TERMS) + j]) for j in range(len(TERMS))] for i, r in enumerate(RATES)]
        avg = batch([{"kind": "pay", "loan": L, "rate": R["avgRate"], "term": t} for t in (25, 30, 35)] + [{"kind": "pay", "loan": L, "rate": R["avgRate"] + 2, "term": 30}])
        need_ftb, need_mover = L / 4, L / 3.5
        facts = [f"Repayments on a <strong>{eur(L)} mortgage</strong> are about <strong>{eur(avg[1])} a month</strong> over 30 years at {R['avgRate']}% (the average new rate, {R['rateMonth']}).",
                 f"Over 35 years it's {eur(avg[2])} a month; over 25 years {eur(avg[0])}.",
                 f"Total interest over 30 years: about {eur(avg[1] * 360 - L)}. If rates rose by 2 points, the payment would be about {eur(avg[3])}.",
                 f"To borrow {eur(L)} you need a gross income of at least <strong>{eur(need_ftb)}</strong> as a first-time buyer (4×) or {eur(need_mover)} as a mover (3.5×)."]
        body = f"""<p class="lead">What are the monthly repayments on a {eur(L)} mortgage in Ireland? See every rate and term, the income you'd need and the total interest.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(facts)}
<h2>Monthly repayments on {eur(L)}</h2>
{table(["Rate"] + [f"{t} years" for t in TERMS], grid)}
<div class="ad" data-slot="content"></div>
<h2>{eur(L)} mortgage vs renting</h2>
<p>The average new rent in Ireland is {eur(RENT['national'])} a month (RTB, Q1 2026) – {eur(abs(RENT['national'] - avg[1]))} {'more' if RENT['national'] > avg[1] else 'less'} than repaying {eur(L)} over 30 years. In Dublin the average is {eur(RENT['dublin'])}.</p>
<div class="cta"><h2>Can you afford {eur(L)}?</h2><p>Check against your income, savings and costs.</p><a class="btn" href="./?price={round(L / 0.9, -3):.0f}">Open the calculator</a></div>
<div class="chip-list">{"".join(f'<a href="repayments-{x}.html">{eur(x)}</a>' for x in LOANS if x != L and abs(x - L) <= 100000)}<a href="repayments.html">All →</a></div>"""
        faqs = [(f"What are the repayments on a {eur(L)} mortgage in Ireland?", f"About {eur(avg[1])} a month over 30 years at {R['avgRate']}%, {eur(avg[2])} over 35 years and {eur(avg[0])} over 25 years."),
                (f"What income do I need for a {eur(L)} mortgage?", f"At least {eur(need_ftb)} gross a year for a first-time buyer, or {eur(need_mover)} for a second or subsequent buyer, under the Central Bank's limits.")]
        write(f"repayments-{L}.html", page(f"repayments-{L}.html", f"{eur(L)} Mortgage Repayments Ireland – Monthly Payment, Income Needed",
                                           f"Repayments on a {eur(L)} mortgage in Ireland: about {eur(avg[1])} a month over 30 years at {R['avgRate']}%. Every rate and term, income needed and total interest.",
                                           body, active="Repayments", jsonld=[faq_ld(faqs)], crumbs=[("Mortgage", "./"), ("Repayments", "repayments.html"), (eur(L), None)],
                                           h1=f"{eur(L)} mortgage repayments", sources=("cbi_rates", "cbi", "rtb_index")))

# ---------------------------------------------------------------- counties
def build_counties():
    rows = []
    for k in sorted(NAMES, key=lambda k: NAMES[k]):
        house, apt = FHS[k]
        rows.append([f'<a href="mortgage-{k}.html">{NAMES[k]}</a>', eur(RENT[k]), eur(house), eur(apt)])
        price = house
        ex = batch([{"kind": "calc", "inp": {"incomes": [price * 0.9 / 4], "savings": price * 0.1 + 12000, "county": k, "price": price}},
                    {"kind": "pay", "loan": price * 0.9, "rate": R["avgRate"], "term": 30}, {"kind": "stamp", "price": price, "nb": False}])
        c, pay, stamp = ex
        diff = RENT[k] - pay
        facts = [f"The average rent for a new tenancy in County {NAMES[k]} is <strong>{eur(RENT[k])} a month</strong> (RTB Rent Index, Q1 2026).",
                 f"Buying a {eur(price)} home with a 10% deposit means a {eur(price * 0.9)} mortgage: about <strong>{eur(pay)} a month</strong> over 30 years at {R['avgRate']}% – "
                 + (f"<strong>{eur(diff)} less than the average rent</strong>." if diff > 0 else f"{eur(-diff)} more than the average rent."),
                 f"To borrow {eur(price * 0.9)} a first-time buyer needs a gross income of about <strong>{eur(price * 0.9 / 4)}</strong> (single or combined).",
                 f"First Home Scheme price ceiling in County {NAMES[k]}: {eur(house)} for houses{'' if apt == house else ', ' + eur(apt) + ' for apartments'}."]
        if k == "cork":
            facts.append("Cork City Council area: €500,000 First Home Scheme ceiling.")
        if k == "galway":
            facts.append("Galway City Council area: €475,000 First Home Scheme ceiling.")
        body = f"""<p class="lead">Buying a home in County {NAMES[k]}? Mortgage, deposit and repayments compared with the average rent, plus Help to Buy and First Home Scheme limits.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(facts)}
<h2>Example: buying a {eur(price)} home in {NAMES[k]}</h2>
{table(["", "Amount"], [["Price", eur(price)], ["10% deposit", eur(price * 0.1)], ["Mortgage (90%)", eur(price * 0.9)], ["Stamp duty (1%)", eur(stamp)],
    ["Solicitor, valuation, survey, Land Registry (estimate)", eur(sum(FEES.values()))], ["<strong>Cash needed</strong>", "<strong>" + eur(price * 0.1 + stamp + sum(FEES.values())) + "</strong>"],
    ["Monthly repayment (30 yrs, " + str(R['avgRate']) + "%)", eur(pay)], ["Average new rent in " + NAMES[k], eur(RENT[k])]])}
<p class="muted small">If it's a new home under €500,000, Help to Buy could give a first-time buyer up to {eur(min(35000, price * 0.1))} towards the deposit.</p>
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Your figures for {NAMES[k]}</h2><p>See what you can borrow and the total cash you need.</p><a class="btn" href="./?county={k}">Open the calculator</a></div>
<p>Renting in {NAMES[k]} while you save? <a href="../rent/rent-increase-{k}.html">Check the rent increase rules for {NAMES[k]} →</a></p>"""
        faqs = [(f"How much do I need to buy a house in {NAMES[k]}?", f"For a {eur(price)} home: a 10% deposit of {eur(price * 0.1)} plus about {eur(stamp + sum(FEES.values()))} in stamp duty and fees, and a gross income of about {eur(price * 0.9 / 4)} for a first-time buyer."),
                (f"Is it cheaper to buy or rent in {NAMES[k]}?", f"Repaying a {eur(price * 0.9)} mortgage costs about {eur(pay)} a month over 30 years at {R['avgRate']}%, compared with an average new rent of {eur(RENT[k])} (RTB, Q1 2026). Buying also has upfront costs, insurance and maintenance.")]
        write(f"mortgage-{k}.html", page(f"mortgage-{k}.html", f"Mortgage Calculator {NAMES[k]} 2026 – Deposit, Repayments vs Rent",
                                         f"Buying in County {NAMES[k]}: deposit, stamp duty and repayments on a {eur(price)} home vs the average rent of {eur(RENT[k])}. First Home Scheme and Help to Buy limits.",
                                         body, active=None, jsonld=[faq_ld(faqs)], crumbs=[("Mortgage", "./"), ("Counties", "counties.html"), (NAMES[k], None)],
                                         h1=f"Buying a home in County {NAMES[k]}", sources=("rtb_index", "fhs", "fhs_ci", "cbi", "stamp")))
    body = f"""<p class="lead">Average rents and First Home Scheme price ceilings in every county – and what it costs to buy instead of rent.</p>
<p class="updated">RTB Rent Index Q1 2026 · First Home Scheme ceilings 2026 · Checked {CHECKED}</p>
{table(["County", "Average new rent / month", "FHS ceiling – house", "FHS ceiling – apartment"], rows)}
<p class="muted small">Counties with city councils (Cork, Galway) have higher ceilings in the city area.</p>"""
    write("counties.html", page("counties.html", "Mortgage vs Rent by County Ireland 2026 – Average Rents & First Home Scheme Ceilings",
                                "Buying vs renting in every Irish county: average new rents (RTB Q1 2026), First Home Scheme price ceilings, deposits and mortgage repayments.",
                                body, crumbs=[("Mortgage", "./"), ("Counties", None)], h1="Buying vs renting in every county", sources=("rtb_index", "fhs", "fhs_ci")))

# ---------------------------------------------------------------- guides
def build_guides():
    st = batch([{"kind": "stamp", "price": p, "nb": nb} for p in (300000, 400000, 500000, 1200000, 1800000) for nb in (False, True)])
    fees = [["Solicitor (incl. VAT)", "€2,500 – €3,700"], ["Land Registry (title + mortgage)", "about €975 + €175"], ["Searches", "about €300"],
            ["Bank valuation", "€150 – €200"], ["Structural survey (second-hand)", "€400 – €650"], ["Mortgage protection insurance", "required – monthly premium"],
            ["Home insurance", "required by lenders – about €300 – €600 a year"]]
    body = f"""<p class="lead">What does it really cost to buy a home in Ireland? Deposit, stamp duty, legal fees and everything else – so you know how much cash you need.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["You need at least a <strong>10% deposit</strong> – €35,000 on a €350,000 home.",
            "Stamp duty is <strong>1%</strong> up to €1 million, 2% from €1m to €1.5m and 6% above €1.5m. On a new home it's charged on the price excluding VAT.",
            "Budget about <strong>€5,000 – €6,000</strong> for solicitor, Land Registry, searches, valuation and survey.",
            "Total: on a €350,000 second-hand home you'll need roughly <strong>€44,000</strong> in cash."])}
<h2>Stamp duty examples</h2>
{table(["Price", "Second-hand", "New build (VAT incl.)"], [[eur(p), eur(st[i * 2]), eur(st[i * 2 + 1])] for i, p in enumerate((300000, 400000, 500000, 1200000, 1800000))])}
<h2>Fees</h2>
{table(["Cost", "Typical amount"], fees)}
<div class="ad" data-slot="content"></div>
<h2>Tips to cut the cash you need</h2>
{lis(["<strong>Help to Buy</strong> (new homes): up to €35,000 back on tax you've paid – it counts towards your deposit. <a href='schemes.html'>How it works</a>",
      "<strong>Get 3 quotes</strong> from solicitors – fixed fees vary by over €1,000", "<strong>Ask about cashback</strong> – some lenders pay 2–3% of the mortgage at drawdown, but compare the rate first",
      "<strong>Green mortgages</strong> – lower rates for homes with a BER of B3 or better", "Movers: your <strong>equity</strong> counts towards the deposit – <a href='moving-home.html'>see the movers guide</a>"])}
<div class="cta"><h2>Your total cash needed</h2><p>Deposit + stamp duty + fees, worked out for your price.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("costs-of-buying.html", page("costs-of-buying.html", "Costs of Buying a House in Ireland 2026 – Deposit, Stamp Duty, Solicitor & Fees",
                                       "Every cost of buying a home in Ireland: 10% deposit, stamp duty (1%/2%/6%), solicitor, Land Registry, valuation, survey and insurance – and the total cash you need.",
                                       body, active="Costs", crumbs=[("Mortgage", "./"), ("Costs of buying", None)], h1="The real cost of buying a home",
                                       sources=("stamp", "ccpc", "ci_buying", "cbi")))

    rows = [[NAMES[k], eur(FHS[k][0]), eur(FHS[k][1])] for k in sorted(NAMES, key=lambda k: NAMES[k])]
    body = f"""<p class="lead">Help to Buy and the First Home Scheme can bridge the gap between your mortgage and the price of a new home. Here's how much they give and who qualifies.</p>
<p class="updated">Updated for Budget 2027 · Checked {CHECKED}</p>
{key_facts(["<strong>Help to Buy</strong>: a refund of income tax and DIRT you paid in the last 4 years – up to <strong>€35,000</strong> (from 7 October 2026, previously €30,000) or 10% of the price, whichever is lower.",
            "Help to Buy is for <strong>first-time buyers of new homes or self-builds costing €500,000 or less</strong>, with a mortgage of at least 70% of the price. Extended to 31 December 2029.",
            "<strong>First Home Scheme</strong>: the State and participating banks take an equity stake of up to <strong>30%</strong> (20% if you also use Help to Buy) in a new home, within local price ceilings.",
            "Both count towards closing the gap – but you still need at least a 10% deposit (Help to Buy can make up part of it)."])}
<h2>Help to Buy: how much could you get?</h2>
{lis(["The lowest of: €35,000, 10% of the purchase price, or the income tax + DIRT you paid in the previous 4 tax years", "You must be a first-time buyer (all applicants) and live in the home",
      "The home must be newly built (or a self-build) and cost no more than €500,000", "Your mortgage must be at least 70% of the price", "Apply through Revenue myAccount before you sign the contract"])}
<h2>First Home Scheme price ceilings</h2>
{table(["County", "House", "Apartment"], rows)}
<p class="muted small">Cork City: €500,000. Galway City: €475,000. Ceilings are reviewed twice a year – check firsthomescheme.ie.</p>
<div class="ad" data-slot="content"></div>
<h2>How the First Home Scheme works</h2>
<p>You buy the home with your mortgage and deposit; the scheme pays the remaining gap (up to 30% of the price) in exchange for an equal share in the home. You can buy it back at any time. No charge applies for the first 5 years; after that a service charge applies on the equity you haven't bought back. You must borrow the maximum your lender will offer.</p>
<p>Not buying a new home? The <a href="https://localauthorityhomeloan.ie/" rel="noopener">Local Authority Home Loan</a> lends to first-time buyers on lower incomes, for new and second-hand homes.</p>
<div class="cta"><h2>See what the schemes do for you</h2><p>Tick Help to Buy and the First Home Scheme in the calculator.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("How much is Help to Buy in 2026?", "Up to €35,000 for contracts signed from 7 October 2026 (Budget 2027), up from €30,000 – limited to 10% of the price and the income tax and DIRT you paid in the previous 4 years."),
            ("Can I use Help to Buy and the First Home Scheme together?", "Yes. If you use both, the First Home Scheme's equity share is capped at 20% instead of 30%.")]
    body += "<h2>Questions</h2>" + faq_html(faqs)
    write("schemes.html", page("schemes.html", "Help to Buy €35,000 & First Home Scheme 2026 – How Much You Get, Price Ceilings",
                               "Help to Buy rises to €35,000 (Budget 2027) for new homes up to €500,000. First Home Scheme equity up to 30% and price ceilings by county. Who qualifies and how much.",
                               body, active="HTB &amp; FHS", jsonld=[faq_ld(faqs)], crumbs=[("Mortgage", "./"), ("Help to Buy & First Home Scheme", None)],
                               h1="Help to Buy and the First Home Scheme", sources=("htb", "htb_rev", "htb_b27", "fhs", "fhs_ci", "lahl")))

    ex = batch([{"kind": "calc", "inp": {"buyer": "mover", "incomes": [70000, 50000], "savings": 10000, "currentValue": 350000, "currentMortgage": 150000, "county": "dublin"}}])[0]
    body = f"""<p class="lead">Trading up, trading down or moving for space? How much a second-time buyer can borrow, how your equity counts, and what to do if you're not selling first.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Second and subsequent buyers can borrow up to <strong>3.5× gross income</strong> (first-time buyers 4×), with at least a <strong>10% deposit</strong>.",
            "Your <strong>equity</strong> – what your home is worth minus your mortgage and selling costs – usually becomes your deposit.",
            "Selling costs: estate agent fees (around 1–1.5% + VAT) and a solicitor for the sale.",
            "From April 2026, short-term <strong>bridging loans</strong> (up to 18 months, repaid from the sale) are exempt from the income limit – useful for buying before you sell.",
            "If you're in negative equity, you're exempt from the deposit (LTV) limit but not the income limit."])}
<h2>Example: trading up</h2>
<p>A couple earning {eur(70000)} and {eur(50000)} with a home worth {eur(350000)} and {eur(150000)} left on the mortgage have about <strong>{eur(ex['equity'])}</strong> equity after selling costs. With €10,000 savings they can borrow up to <strong>{eur(ex['maxLoanLTI'])}</strong> (3.5×) and buy up to about <strong>{eur(ex['maxPrice'])}</strong>, repaying about {eur(ex['monthly'])} a month.</p>
<div class="ad" data-slot="content"></div>
<h2>Selling first, buying first, or keeping your home?</h2>
{table(["Option", "What to know"], [["Sell first", "Clearest position for the lender; you may need to rent in between."],
    ["Buy first with a bridging loan", "Exempt from the income limit since April 2026 if the term is 18 months or less and it's repaid from the sale. LTV still applies."],
    ["Keep your current home", "Your existing mortgage counts against affordability; the new loan is still capped at 3.5× income. If you rent the old home out you'll need a buy-to-let mortgage (70% LTV)."],
    ["Trading down", "Your equity may cover most of the price; you might not need a mortgage at all."]])}
<h2>Tips for movers</h2>
{lis(["Get a valuation from 2–3 agents before you decide what to buy", "Ask your lender about <strong>porting</strong> your mortgage – and compare it with switching",
      "Check if your fixed rate has an <strong>early repayment charge</strong>", "Movers can't use Help to Buy, but some can use the First Home Scheme in limited cases"])}
<div class="cta"><h2>Your trade-up figures</h2><p>Choose "Moving home" in the calculator and add your current home.</p><a class="btn" href="./?buyer=mover">Open the calculator</a></div>"""
    write("moving-home.html", page("moving-home.html", "Mover Mortgage Ireland 2026 – Trading Up, Equity, Bridging Loans & How Much You Can Borrow",
                                   "Second-time buyers in Ireland: borrow up to 3.5x income, use your equity as a deposit, selling costs, bridging loans (April 2026 change) and keeping your old home.",
                                   body, active="Movers", crumbs=[("Mortgage", "./"), ("Moving home", None)], h1="Moving home: mortgages for second-time buyers",
                                   sources=("cbi", "cbi_bridge", "ccpc", "stamp")))

    body = f"""<p class="lead">A step-by-step guide for first-time buyers in Ireland – from saving the deposit to getting the keys.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Borrow up to <strong>4× your gross income</strong> (combined, if buying with someone) with at least a <strong>10% deposit</strong>.",
            "New home? <strong>Help to Buy</strong> gives up to €35,000 and the <strong>First Home Scheme</strong> up to 30% equity.",
            "Lenders want to see 6–12 months of steady saving and rent payments, and few other debts.",
            "You'll pay stamp duty (1%) and around €5,000–€6,000 in fees on top of the deposit."])}
<h2>10 steps to buying your first home</h2>
<div class="card"><ol class="steps">
<li><strong>Check what you can borrow</strong> with the <a href="./">calculator</a>.</li><li><strong>Save the deposit</strong> – 10%, plus costs. Show regular savings on your statements.</li>
<li><strong>Clear short-term debts</strong> and avoid new loans or buy-now-pay-later.</li><li><strong>Check your credit report</strong> with the Central Credit Register (free).</li>
<li><strong>Get approval in principle</strong> from a lender or broker – usually valid 6 months.</li><li><strong>Apply for Help to Buy</strong> in Revenue myAccount if buying new.</li>
<li><strong>Go sale agreed</strong> and pay a booking deposit.</li><li><strong>Get a valuation and survey</strong>; your solicitor checks the title.</li>
<li><strong>Get mortgage protection and home insurance</strong>, then loan offer and contracts.</li><li><strong>Drawdown and closing</strong> – stamp duty is paid and you get the keys.</li>
</ol></div>
<div class="ad" data-slot="content"></div>
<h2>Tips from people who've done it</h2>
{lis(["Use the <strong>Rent Tax Credit</strong> while you rent – up to €1,000 a year (€1,150 in 2027). <a href='../salary/'>See your take-home pay</a>",
      "Keep an eye on your <a href='../rent/'>rent increases</a> – they can't be more than 2% a year", "Joint applicants: both incomes count, and both must be first-time buyers for Help to Buy",
      "Gifts from family count towards the deposit, with a gift letter (gifts over the €400,000 Group A threshold may have tax)"])}"""
    write("first-time-buyers.html", page("first-time-buyers.html", "First-Time Buyer Guide Ireland 2026 – Deposit, Borrowing, Help to Buy, Steps",
                                         "First-time buyers in Ireland: how much you can borrow (4x income), saving the 10% deposit, Help to Buy €35,000, First Home Scheme, approval in principle and the 10 steps to buying.",
                                         body, crumbs=[("Mortgage", "./"), ("First-time buyers", None)], h1="First-time buyer guide",
                                         sources=("cbi", "htb", "fhs_ci", "ci_buying", "ccpc")))

    body = f"""<p class="lead">The Central Bank of Ireland's mortgage measures limit how much you can borrow and how much deposit you need. Here they are in plain English.</p>
<p class="updated">Checked against the Central Bank in {CHECKED}</p>
{table(["", "First-time buyer", "Second / subsequent buyer", "Buy-to-let"], [
    ["Loan-to-income limit", "4× gross income", "3.5× gross income", "Exempt"], ["Loan-to-value limit", "90% (10% deposit)", "90% (10% deposit)", "70% (30% deposit)"],
    ["Lender allowance above limits", "15% of lending", "15% of lending", "10% of lending"]])}
<h2>Exemptions</h2>
{lis(["Switching your mortgage to another lender – exempt from both limits", "Restructuring for arrears – exempt", "Negative equity buyers – exempt from LTV only",
      "Bridging loans for a home (April 2026): exempt from the income limit if 18 months or less with no capital repayments, repaid from the sale. LTV still applies"])}
<h2>What lenders also check</h2>
{lis(["Repayment capacity – your spending, savings record and other debts", "Employment – usually out of probation, steady income", "Credit history on the Central Credit Register",
      "Age and term – most lenders want the mortgage repaid by around 68–70"])}
<div class="cta"><h2>Apply the rules to you</h2><p>See your limit, deposit and repayments.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("central-bank-rules.html", page("central-bank-rules.html", "Central Bank Mortgage Rules Ireland 2026 – 4x Income, 10% Deposit, Exceptions",
                                          "The Central Bank of Ireland mortgage measures explained: 4x income for first-time buyers, 3.5x for movers, 90% LTV, 15% allowances, and the April 2026 bridging loan change.",
                                          body, crumbs=[("Mortgage", "./"), ("Central Bank rules", None)], h1="Central Bank mortgage rules", sources=("cbi", "cbi_bridge")))

def build_faq():
    p300 = batch([{"kind": "pay", "loan": 300000, "rate": R["avgRate"], "term": 30}])[0]
    FAQ = [
        ("How much can I borrow for a mortgage in Ireland?", "First-time buyers up to 4× gross income and second and subsequent buyers up to 3.5×. Couples combine their incomes. Lenders can go above this for a limited number of borrowers."),
        ("How much deposit do I need?", "At least 10% of the price for a home you'll live in, and 30% for buy-to-let. You also need money for stamp duty and fees."),
        ("Does bonus or overtime count?", "Lenders may count some of your regular bonus, overtime or commission – often around half of the average of the last 2 years, if it's guaranteed or consistent. It varies by lender."),
        ("Can I get a mortgage on my own?", "Yes – a sole applicant can borrow up to 4× their income as a first-time buyer. Help to Buy and the First Home Scheme help close the gap on new homes."),
        ("Does my partner need to be on the mortgage?", "Only if you want their income counted. Joint applicants are both responsible for the full loan."),
        ("What is a second and subsequent buyer?", "Anyone who has owned a home before. The limit is 3.5× income instead of 4×. Some people who've been through divorce or insolvency may be treated as first-time buyers – ask your lender."),
        ("What happens to my equity when I move?", "Your equity (home value minus mortgage and selling costs) usually becomes your deposit for the next home."),
        ("Can I buy before I sell?", "Yes, with a bridging loan. Since April 2026, bridging loans of up to 18 months repaid from the sale are exempt from the income limit, but the 90% LTV limit still applies."),
        ("How much is stamp duty?", "1% of the price up to €1 million, 2% between €1m and €1.5m, and 6% above €1.5m. On new homes it's charged on the price excluding VAT."),
        ("What is the average mortgage rate in Ireland?", f"{R['avgRate']}% for new mortgages in {R['rateMonth']} (fixed rates averaged {R['avgFixed']}%), according to the Central Bank."),
        ("What are the repayments on €300,000?", f"About {eur(p300)} a month over 30 years at {R['avgRate']}%. <a href='repayments-300000.html'>See every rate and term</a>."),
        ("How long can a mortgage be?", "Up to 35 years with most lenders, usually ending by age 68–70."),
        ("Is it cheaper to buy than rent?", f"Often, month to month: the average new rent is {eur(RENT['national'])} (RTB, Q1 2026). But buying has upfront costs, insurance and maintenance. <a href='counties.html'>Compare by county</a>."),
        ("How much is Help to Buy now?", "Up to €35,000 from 7 October 2026 (Budget 2027) for first-time buyers of new homes up to €500,000."),
        ("Do I need mortgage protection insurance?", "Yes, lenders require it for a home loan (with a few exceptions, such as age or health). You also need home insurance."),
        ("What is approval in principle?", "A lender's provisional offer based on your income and savings, usually valid for 6 months. You need it before going sale agreed."),
        ("Is this calculator a mortgage offer?", "No. It's a free, independent estimate based on the Central Bank rules and published rates. Only a lender can approve a mortgage."),
    ]
    body = f"""<p class="lead">Answers to the questions people ask most about getting a mortgage in Ireland.</p>
<p class="updated">Checked {CHECKED}</p>{faq_html(FAQ)}
<div class="cta"><h2>See your numbers</h2><p>What you can borrow, the cash you need and your repayments.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("faq.html", page("faq.html", "Mortgage FAQ Ireland 2026 – Borrowing, Deposit, Stamp Duty, Help to Buy",
                           "Answers about Irish mortgages: how much you can borrow, deposits, bonus income, sole and joint applicants, movers, bridging loans, stamp duty, rates and Help to Buy.",
                           body, active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Mortgage", "./"), ("FAQ", None)], h1="Mortgage FAQ",
                           sources=("cbi", "cbi_rates", "stamp", "htb_b27", "ccpc")))

# ---------------------------------------------------------------- og, sitemap, llms
def build_og():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (11, 15, 25)); d = ImageDraw.Draw(im)
    for i in range(H):
        a = max(0, 1 - i / 520); d.line([(0, i), (W, i)], fill=(int(11 + 60 * a), int(15 + 30 * a), int(25 + 5 * a)))
    def font(size, bold=True):
        for name in (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()
    d.rounded_rectangle([70, 70, 470, 116], 23, fill=(180, 83, 9)); d.text((92, 78), "IRELAND · 2026 RULES", font=font(28), fill=(255, 255, 255))
    d.text((70, 160), "How much can", font=font(92), fill=(241, 245, 249))
    d.text((70, 262), "I borrow?", font=font(92), fill=(251, 191, 36))
    d.text((70, 400), "Mortgage · deposit · stamp duty · repayments", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 452), "Help to Buy · First Home Scheme · movers", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 545), "tavion.ie/mortgage  ·  free, no sign-up", font=font(32), fill=(56, 189, 248))
    im.save(os.path.join(ROOT, "og.png"), optimize=True)

def update_sitemap(files):
    path = os.path.join(REPO, "sitemap.xml")
    xml = open(path, encoding="utf-8").read()
    xml = re.sub(r"\s*<url><loc>https://tavion\.ie/mortgage/[^<]*</loc>.*?</url>", "", xml)
    xml = xml.replace("\n</urlset>", "".join(f'\n  <url><loc>{BASE}{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>' for fn, pr in files) + "\n</urlset>")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

def update_llms():
    path = os.path.join(REPO, "llms.txt")
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"\n- \[Irish Mortgage Calculator\][^\n]*", "", txt)
    txt = re.sub(r"\n## Mortgages: key facts\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
    app = "\n- [Irish Mortgage Calculator](https://tavion.ie/mortgage/): how much you can borrow under Central Bank rules (4x FTB / 3.5x movers, 10% deposit), price you can afford, deposit, stamp duty and fees, Help to Buy and First Home Scheme, mover equity, repayments vs take-home pay and vs average rent by county."
    txt = re.sub(r"(\n- \[Irish Citizenship Calculator\][^\n]*)", lambda m: m.group(1) + app, txt, count=1)
    facts = f"""
## Mortgages: key facts

- Central Bank limits: first-time buyers 4x gross income, second and subsequent buyers 3.5x; 90% loan-to-value (10% deposit) for homes, 70% for buy-to-let; lenders may exceed limits for 15% of lending (10% BTL). April 2026: bridging loans up to 18 months exempt from the income limit.
- Average new mortgage rate {R['avgRate']}% ({R['rateMonth']}); fixed {R['avgFixed']}%.
- Help to Buy: up to €35,000 from 7 October 2026 (Budget 2027), max 10% of price, new homes up to €500,000, mortgage at least 70%, until end-2029. First Home Scheme: equity up to 30% (20% with Help to Buy), price ceilings €375,000–€500,000 by area.
- Stamp duty: 1% up to €1m, 2% €1m–€1.5m, 6% above €1.5m (VAT-exclusive price on new homes).
- Average new rent (RTB Q1 2026): national €{RENT['national']:,}, Dublin €{RENT['dublin']:,}, Cork €{RENT['cork']:,}, Galway €{RENT['galway']:,}, Limerick €{RENT['limerick']:,}.
- Pages: [Calculator](https://tavion.ie/mortgage/), [How much can I borrow by salary](https://tavion.ie/mortgage/how-much-can-i-borrow.html), [Repayment tables](https://tavion.ie/mortgage/repayments.html), [Costs of buying](https://tavion.ie/mortgage/costs-of-buying.html), [Help to Buy & First Home Scheme](https://tavion.ie/mortgage/schemes.html), [Movers](https://tavion.ie/mortgage/moving-home.html), [By county](https://tavion.ie/mortgage/counties.html), [FAQ](https://tavion.ie/mortgage/faq.html).
"""
    txt = txt.replace("\n## Optional", facts + "\n## Optional", 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)

if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    build_index(); build_borrow(); build_repay(); build_counties(); build_guides(); build_faq(); build_og()
    files = [("index.html", "0.9"), ("how-much-can-i-borrow.html", "0.9"), ("repayments.html", "0.8"), ("costs-of-buying.html", "0.8"), ("schemes.html", "0.8"),
             ("moving-home.html", "0.8"), ("first-time-buyers.html", "0.8"), ("central-bank-rules.html", "0.7"), ("counties.html", "0.7"), ("faq.html", "0.7")] + \
            [(f"borrow-{a}.html", "0.6") for a in INCOMES] + [(f"repayments-{L}.html", "0.6") for L in LOANS] + [(f"mortgage-{k}.html", "0.6") for k in NAMES]
    update_sitemap(files); update_llms()
    print("Built", len(files), "pages in", os.path.normpath(ROOT))
