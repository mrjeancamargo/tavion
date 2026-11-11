"""
Builds the static pages of the Stamp Duty, Buying Costs & LPT app (tavion.ie/stamp-duty/).

Run from the repo root:   python tools/build_stamp.py
Needs Node.js: figures come from stamp-duty/js/property.js – the same engine the calculators use.
When rates or Local Adjustment Factors change: update property.js and CHECKED, then re-run.
"""
import datetime, json, os, re, subprocess
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.join(REPO, "stamp-duty")
ENGINE = os.path.join(ROOT, "js", "property.js")
SITE = "https://tavion.ie/"
BASE = SITE + "stamp-duty/"
CHECKED = "November 2026"
TODAY = datetime.date.today()

PRICES = list(range(100000, 1000001, 25000)) + list(range(1100000, 2000001, 100000)) + [2500000, 3000000]

SRC = {
    "rev_sd": ("Revenue – Stamp duty", "https://www.revenue.ie/en/property/stamp-duty/index.aspx"),
    "rev_lpt_bands": ("Revenue – LPT valuation bands and rates 2026–2030", "https://www.revenue.ie/en/property/local-property-tax/valuing-your-property/valuation-bands-rates.aspx"),
    "rev_lpt_2026": ("Revenue – LPT: what you need to do for 2026", "https://www.revenue.ie/en/property/local-property-tax/what-to-do/valuing-your-property.aspx"),
    "rev_lpt_calc": ("Revenue – LPT calculator", "https://lpt.revenue.ie/lpt-web/reckoner/lpt.html"),
    "rev_lpt": ("Revenue – Local Property Tax", "https://www.revenue.ie/en/property/local-property-tax/index.aspx"),
    "ci_sd": ("Citizens Information – Stamp duty on property", "https://www.citizensinformation.ie/en/money-and-tax/tax/housing-taxes-and-reliefs/stamp-duty-on-property/"),
    "ci_lpt": ("Citizens Information – Local Property Tax", "https://www.citizensinformation.ie/en/housing/owning-a-home/home-owner-supports/local-property-tax/"),
    "ccpc": ("CCPC – Costs of buying a home", "https://www.ccpc.ie/consumers/money/mortgages/"),
    "ppr": ("Property Price Register", "https://www.propertypriceregister.ie/"),
}
TABS = [("./", "Stamp duty"), ("lpt.html", "Property tax"), ("prices.html", "By price"), ("lpt-bands.html", "LPT bands"), ("lpt-councils.html", "Councils"),
        ("guide.html", "Guide"), ("faq.html", "FAQ")]
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

NODE = r"""
const P = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "sd" ? P.stampDuty(x.p, x.o) : x.k === "lpt" ? P.lpt(x.v, x.c, x.y) : x.k === "cost" ? P.buyingCosts(x.p, x.o) : null);
  process.stdout.write(JSON.stringify({ bands: P.LPT_BANDS, councils: P.COUNCILS, fees: P.FEES, res: res }));
});
"""
def engine(q):
    p = subprocess.run(["node", "-e", NODE, ENGINE], input=json.dumps(q), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)
META = engine([])
BANDS, COUNCILS, FEES = META["bands"], META["councils"], META["fees"]
def run(q): return engine(q)["res"]

def eur(n, dp=0): return ("−" if n < 0 else "") + "€" + f"{abs(n):,.{dp}f}"
def lis(items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
def table(head, rows): return ('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" +
                               "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")
def faq_ld(pairs): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a in pairs]}
def faq_html(pairs): return "".join(f'<details class="faq"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in pairs)
def key_facts(items): return '<div class="facts-box"><h2 class="tl">Key facts</h2><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"
def sources_block(keys): return ('<div class="sources"><h2 class="tl">Sources – check them yourself</h2><ul>' +
                                 "".join(f'<li><a href="{SRC[k][1]}" rel="noopener" target="_blank">{SRC[k][0]}</a></li>' for k in keys) + "</ul></div>")
def pslug(p): return f"stamp-duty-{p}.html"
def band_range(i):
    lo = 1 if i == 0 else BANDS[i - 1][0] + 1
    return lo, BANDS[i][0]

def try_also(price=None):
    q = f"?price={price}" if price else ""
    items = [("🔑", "How much could I borrow?", "Mortgage, deposit and repayments", f"../mortgage/{q}", "mortgage"),
             ("💶", "Take-home pay calculator", "Your net pay after tax, USC, PRSI", "../salary/", "salary"),
             ("🏠", "Rent increase checker", "Renting while you save? Know your rights", "../rent/", "rent")]
    return '<div class="try"><h2 class="tl">Try also</h2><div class="try-grid">' + "".join(
        f'<a href="{h}" data-track="cross_app" data-label="{lab}"><b>{i}</b><span><strong>{t}</strong>{d}</span></a>' for i, t, d, h, lab in items) + "</div></div>"

def share_html(text, url, label):
    wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
    fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
    return (f'<h2>Share it</h2><p class="muted">Know someone buying a home? Send them this.</p><div class="share">'
            f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
            f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

def page(filename, title, desc, body, active=None, jsonld=(), crumbs=None, slot="content", scripts=(), share_text=None, h1=None, sources=("rev_sd", "ci_sd"), price=None):
    url = BASE if filename == "index.html" else BASE + filename
    on = ' class="on"'
    tabs = "".join(f'<a href="{href}"{on if label == active else ""}>{label}</a>' for href, label in TABS)
    crumb_html = ""
    if crumbs:
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs) + "</nav>"
        items = [{"@type": "ListItem", "position": i + 1, "name": t, "item": (BASE + (h if h not in ("./", None) else "")) if h else url} for i, (t, h) in enumerate(crumbs)]
        jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "description": desc, "inLanguage": "en-IE",
                              "dateModified": TODAY.isoformat(), "isPartOf": {"@type": "WebSite", "name": "Tavion", "url": SITE},
                              "publisher": {"@type": "Organization", "name": "Tavion", "url": SITE, "logo": SITE + "images/logo.png"}, "citation": [SRC[k][1] for k in sources]}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
    extra = "".join(f'<script src="{s}"></script>' for s in scripts)
    share = share_html(share_text or "Free Irish stamp duty & buying costs calculator – plus Local Property Tax 2026/2027:", url, filename.replace(".html", ""))
    pop = " · ".join(f'<a href="{pslug(p)}">{eur(p)}</a>' for p in (250000, 300000, 350000, 400000, 450000, 500000, 600000))
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
<meta name="theme-color" content="#be123c">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>🧾</b> Stamp Duty &amp; LPT</a><a class="small" href="../" data-track="apps_click" data-label="stamp_header">More Tavion apps</a></div>
  <nav class="tabs" aria-label="Sections"><div class="wrap">{tabs}</div></nav>
</header>
<main class="wrap">
{crumb_html}
{('<h1>' + h1 + '</h1>') if h1 else ''}
{body}
{try_also(price)}
{sources_block(sources)}
<div class="ad" data-slot="{slot}"></div>
{share}
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Stamp duty pages"><a href="./">Stamp duty &amp; buying costs</a><a href="lpt.html">LPT calculator</a><a href="prices.html">Stamp duty by price</a><a href="lpt-bands.html">LPT bands 2026–2030</a><a href="lpt-councils.html">LPT by council</a><a href="guide.html">Stamp duty &amp; LPT guide</a><a href="faq.html">FAQ</a></nav>
    <p>Stamp duty on: {pop}</p>
    <p>Also free: <a href="../mortgage/" data-track="cross_app" data-label="mortgage">🔑 Mortgage calculator</a> · <a href="../salary/" data-track="cross_app" data-label="salary">💶 Take-home pay</a> · <a href="../rent/" data-track="cross_app" data-label="rent">🏠 Rent checker</a></p>
    <p>Figures checked against Revenue in {CHECKED}. A free, independent tool from <a href="../">Tavion</a>, not affiliated with Revenue. Fees are typical estimates – get quotes. For your exact LPT use <a href="https://lpt.revenue.ie/lpt-web/reckoner/lpt.html" rel="noopener">Revenue's LPT calculator</a>.</p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="stamp_footer">More free apps from Tavion</a></p>
  </div>
</footer>
<script src="js/site.js"></script>{extra}
</body>
</html>
"""

def write(name, html):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

council_opts = "".join(f'<option value="{k}">{v[0]}</option>' for k, v in sorted(COUNCILS.items(), key=lambda kv: kv[1][0]))

# ---------------------------------------------------------------- calculators
def build_index():
    c = run([{"k": "cost", "p": 350000, "o": {}}])[0]
    body = f"""<p class="lead">How much stamp duty will you pay, and what does buying a home in Ireland really cost? Stamp duty, solicitor, Land Registry, valuation and survey – plus your first Local Property Tax bill. Free, no sign-up.</p>
<ul class="facts"><li>1% up to €1m</li><li>2% €1m–€1.5m</li><li>6% above €1.5m</li><li>New homes: price ex-VAT</li></ul>
<form id="sdForm" class="card" novalidate>
  <label for="price" class="big-label">Purchase price</label>
  <div class="money"><span>€</span><input id="price" type="text" inputmode="decimal" autocomplete="off" placeholder="350,000"></div>
  <fieldset style="margin-top:14px"><legend class="sm">Type of home</legend>
    <div class="seg two-seg"><label><input type="radio" name="kind" value="second" checked><span>Second-hand</span></label><label><input type="radio" name="kind" value="new"><span>New build<small>price incl. 13.5% VAT</small></span></label></div>
  </fieldset>
  <details id="adv" class="adv">
    <summary>Advanced options <span class="muted small">– mortgage, survey, solicitor fee, LPT, moving costs…</span></summary>
    <div class="adv-body">
      <label class="check"><input type="checkbox" id="mortgage" checked><span>Buying with a mortgage <small class="muted">(adds valuation and mortgage registration)</small></span></label>
      <label class="check"><input type="checkbox" id="survey" checked><span>Get a structural survey</span></label>
      <label class="check"><input type="checkbox" id="extras"><span>Include removals and first-year home insurance</span></label>
      <label class="check"><input type="checkbox" id="bulk"><span>Buying 10 or more homes within 12 months <small class="muted">(15% rate)</small></span></label>
      <label>Solicitor's quote (incl. VAT and outlays)<div class="money"><span>€</span><input id="solicitor" type="text" inputmode="decimal" placeholder="{FEES['solicitor']:,}"></div></label>
      <label>Council (for your Local Property Tax)<select id="council"><option value="">Choose your council…</option>{council_opts}</select></label>
      <label>Deposit you'll put down (%)<input id="depPct" type="number" min="0" max="100" step="1" inputmode="numeric" placeholder="10"></label>
      <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
    </div>
  </details>
  <div class="btn-row"><button type="submit" class="btn primary">Calculate stamp duty &amp; costs</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>How stamp duty works on a home in Ireland</h2>
<div class="card"><ol class="steps">
<li><strong>1%</strong> on the first €1,000,000 of the price.</li><li><strong>2%</strong> on the part between €1,000,000 and €1,500,000.</li>
<li><strong>6%</strong> on anything above €1,500,000 (since 2 October 2024).</li>
<li><strong>New homes:</strong> stamp duty is charged on the price <em>excluding</em> the 13.5% VAT – so a €454,000 new home pays stamp duty on €400,000.</li>
<li><strong>Who pays:</strong> the buyer, through their solicitor, using Revenue's eStamping after the deed is signed – late filing means interest and penalties.</li></ol></div>
<p>Example: on a €350,000 second-hand home, stamp duty is <strong>{eur(c['stamp']['total'])}</strong> and total buying costs are about <strong>{eur(c['total'])}</strong> – plus a 10% deposit of {eur(c['deposit10'])}.</p>
<div class="cta"><h2>And your property tax?</h2><p>LPT 2026–2030 bands and every council's rate.</p><a class="btn" href="lpt.html">LPT calculator</a></div>"""
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Stamp Duty & Buying Costs Calculator", "url": BASE, "applicationCategory": "FinanceApplication",
              "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "featureList": ["Stamp duty at 1%, 2% and 6%", "New build VAT-exclusive calculation", "Solicitor, Land Registry, searches, valuation and survey", "Total cash needed with deposit", "First Local Property Tax bill"],
              "description": "Free calculator for stamp duty and the total costs of buying a home in Ireland."}
    faqs = [("How much is stamp duty on a house in Ireland?", "1% of the price up to €1 million, 2% on the part from €1 million to €1.5 million and 6% above €1.5 million. A €350,000 home pays €3,500."),
            ("Do first-time buyers pay stamp duty in Ireland?", "Yes. There is no stamp duty exemption for first-time buyers in Ireland – everyone pays 1% up to €1 million.")]
    write("index.html", page("index.html", "Stamp Duty Calculator Ireland 2026 – Total Costs of Buying a House",
                             "Free Irish stamp duty calculator: 1% up to €1m, 2% to €1.5m, 6% above. Plus solicitor, Land Registry, valuation and survey fees, total cash needed and your first LPT bill.",
                             body, active="Stamp duty", jsonld=[app_ld, faq_ld(faqs)], slot="calculator", scripts=["js/property.js", "js/calc.js"], h1="Stamp duty &amp; buying costs calculator",
                             sources=("rev_sd", "ci_sd", "ccpc", "rev_lpt_bands"), share_text="Free stamp duty calculator for Ireland 🏡 – stamp duty, fees and the total cash you need to buy:"))

    rows = []
    for i, (top, basic) in enumerate(BANDS):
        lo, hi = band_range(i)
        rows.append([f'<a href="lpt-band-{i + 1}.html">Band {i + 1}</a>', f"{eur(lo)} – {eur(hi)}", eur(basic)])
    rows.append(['<a href="lpt-band-over-2-1-million.html">Over €2.1m</a>', "Above €2,100,000", "0.0906% / 0.25% / 0.3% on slices"])
    body = f"""<p class="lead">Work out your Local Property Tax for 2026 and 2027 using the new valuation bands and your council's local adjustment.</p>
<ul class="facts"><li>Value on 1 Nov 2025</li><li>Fixed until 2030</li><li>19 bands</li></ul>
<form id="lptForm" class="card" novalidate>
  <label for="lptVal" class="big-label">Your home's value on 1 November 2025</label>
  <div class="money"><span>€</span><input id="lptVal" type="text" inputmode="decimal" autocomplete="off" placeholder="400,000"></div>
  <label>Council<select id="lptCouncil">{council_opts}</select></label>
  <fieldset style="margin-top:14px"><legend class="sm">Year</legend>
    <div class="seg two-seg"><label><input type="radio" name="lptYear" value="2026"><span>2026</span></label><label><input type="radio" name="lptYear" value="2027" checked><span>2027</span></label></div></fieldset>
  <div class="btn-row"><button type="submit" class="btn primary">Calculate my LPT</button></div>
</form>
<div id="lptOut" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>LPT valuation bands 2026–2030</h2>
{table(["Band", "Value on 1 November 2025", "Basic annual LPT"], rows)}
<p class="muted small">Your council can raise the basic rate by up to 25% or cut it by up to 15% (the Local Adjustment Factor). <a href="lpt-councils.html">See every council →</a></p>"""
    faqs = [("How is LPT calculated for 2026?", "Your home's value on 1 November 2025 sets your band for 2026 to 2030. Each band has a basic annual charge (€95 to €3,110), adjusted up or down by your council's Local Adjustment Factor."),
            ("Do I have to revalue my home for LPT?", "The valuation date was 1 November 2025; that value applies until 2030. If you bought or built after that, you value the home as at 1 November 2025.")]
    write("lpt.html", page("lpt.html", "LPT Calculator 2026 & 2027 – Local Property Tax Bands Ireland",
                           "Calculate your Local Property Tax for 2026 and 2027: new valuation bands from €95 to €3,110, homes over €2.1m, and every council's Local Adjustment Factor.",
                           body, active="Property tax", jsonld=[faq_ld(faqs)], slot="calculator", scripts=["js/property.js", "js/calc.js"],
                           crumbs=[("Stamp duty", "./"), ("LPT calculator", None)], h1="Local Property Tax calculator 2026–2027",
                           sources=("rev_lpt_bands", "rev_lpt_2026", "rev_lpt_calc", "ci_lpt"), share_text="Local Property Tax 2026/2027 – check your band and your council's rate:"))

# ---------------------------------------------------------------- price pages
def build_prices():
    q = []
    for p in PRICES:
        q += [{"k": "cost", "p": p, "o": {}}, {"k": "cost", "p": p, "o": {"newBuild": True, "survey": False}}, {"k": "lpt", "v": p, "c": "dublin-city", "y": 2027}]
    res = run(q)
    rows = []
    for i, p in enumerate(PRICES):
        sh, nb = res[3 * i], res[3 * i + 1]
        rows.append([f'<a href="{pslug(p)}">{eur(p)}</a>', eur(sh["stamp"]["total"]), eur(nb["stamp"]["total"]), eur(sh["total"]), eur(sh["cashWithDeposit"])])
    body = f"""<p class="lead">Stamp duty and total buying costs at every price from €100,000 to €3 million, for second-hand and new homes.</p>
<p class="updated">Checked against Revenue · {CHECKED}</p>
{table(["Price", "Stamp duty (second-hand)", "Stamp duty (new, VAT incl.)", "All buying costs", "Cash needed incl. 10% deposit"], rows)}
<p class="muted small">Buying costs include stamp duty, solicitor, Land Registry, searches, valuation and survey (estimates).</p>"""
    write("prices.html", page("prices.html", "Stamp Duty by House Price Ireland 2026 – Table €100k to €3m",
                              "Stamp duty and total costs of buying at every price in Ireland, €100,000 to €3,000,000, for second-hand and new build homes.",
                              body, active="By price", crumbs=[("Stamp duty", "./"), ("By price", None)], h1="Stamp duty by house price"))
    for i, p in enumerate(PRICES):
        sh, nb, l = res[3 * i], res[3 * i + 1], res[3 * i + 2]
        sd = sh["stamp"]
        brk = " + ".join(f"{int(r['rate'] * 100)}% of {eur(r['on'])}" for r in sd["rows"])
        items = "".join(f"<tr><th scope='row'>{x['name']}</th><td>{eur(x['amount'])}</td></tr>" for x in sh["items"])
        facts = [f"Stamp duty on a <strong>{eur(p)}</strong> second-hand home in Ireland is <strong>{eur(sd['total'])}</strong> ({brk}).",
                 f"On a {eur(p)} <strong>new</strong> home (13.5% VAT included) it's <strong>{eur(nb['stamp']['total'])}</strong>, because stamp duty is charged on the price excluding VAT ({eur(nb['stamp']['base'])}).",
                 f"Total buying costs are about <strong>{eur(sh['total'])}</strong> ({sh['pctOfPrice']}% of the price). With a 10% deposit you need about <strong>{eur(sh['cashWithDeposit'])}</strong> in cash.",
                 (f"Local Property Tax: band {l['band']}, " if l['band'] else "Local Property Tax: above €2.1m, ") + f"basic {eur(l['basic'])} a year (before your council's adjustment)."]
        body = f"""<p class="lead">How much stamp duty do you pay on a {eur(p)} house in Ireland, and what are the total costs of buying?</p>
<p class="updated">Checked against Revenue · {CHECKED}</p>
{key_facts(facts)}
<div class="hero-num"><div><span class="tl">Second-hand</span><strong>{eur(sd['total'])}</strong><span class="muted">stamp duty</span></div><div><span class="tl">New build</span><strong>{eur(nb['stamp']['total'])}</strong><span class="muted">stamp duty</span></div></div>
<h2>Total costs of buying a {eur(p)} home</h2>
<div class="table-wrap"><table class="sumtab"><tbody>{items}<tr class="total"><th scope="row">Total buying costs</th><td>{eur(sh['total'])}</td></tr>
<tr><th scope="row">10% deposit</th><td>{eur(sh['deposit10'])}</td></tr><tr class="total"><th scope="row">Cash needed</th><td>{eur(sh['cashWithDeposit'])}</td></tr></tbody></table></div>
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Can you afford {eur(p)}?</h2><p>See the income you need, your mortgage and monthly repayments.</p><a class="btn" href="../mortgage/?price={p}" data-track="cross_app" data-label="mortgage_price_{p}">How much could I borrow?</a></div>
<p>A first-time buyer needs a gross income of about <strong>{eur(p * 0.9 / 4)}</strong> (single or combined) to borrow 90% of {eur(p)}. <a href="../mortgage/">Check in the mortgage calculator →</a></p>
<div class="chip-list">{"".join(f'<a href="{pslug(x)}">{eur(x)}</a>' for x in PRICES if x != p and abs(x - p) <= max(75000, p * 0.15))}<a href="prices.html">All prices →</a></div>"""
        faqs = [(f"How much is stamp duty on {eur(p)} in Ireland?", f"{eur(sd['total'])} on a second-hand home ({brk}). On a new home at {eur(p)} including VAT it's {eur(nb['stamp']['total'])}."),
                (f"What are the total costs of buying a {eur(p)} house?", f"About {eur(sh['total'])} in stamp duty and fees, plus a deposit – about {eur(sh['cashWithDeposit'])} in cash with a 10% deposit.")]
        write(pslug(p), page(pslug(p), f"Stamp Duty on {eur(p)} Ireland – {eur(sd['total'])} + Total Buying Costs 2026",
                             f"Stamp duty on a {eur(p)} house in Ireland is {eur(sd['total'])} ({eur(nb['stamp']['total'])} on a new build). Total buying costs about {eur(sh['total'])}; cash needed {eur(sh['cashWithDeposit'])} with a 10% deposit.",
                             body, active="By price", jsonld=[faq_ld(faqs)], crumbs=[("Stamp duty", "./"), ("By price", "prices.html"), (eur(p), None)],
                             h1=f"Stamp duty on {eur(p)}", sources=("rev_sd", "ci_sd", "ccpc"), price=p,
                             share_text=f"Stamp duty and all the costs of buying a {eur(p)} home in Ireland:"))

# ---------------------------------------------------------------- LPT bands and councils
def build_lpt_pages():
    rows = []
    keys = sorted(COUNCILS, key=lambda k: COUNCILS[k][0])
    for i, (top, basic) in enumerate(BANDS):
        lo, hi = band_range(i)
        rows.append([f'<a href="lpt-band-{i + 1}.html">Band {i + 1}</a>', f"{eur(lo)} – {eur(hi)}", eur(basic), eur(basic * 0.85), eur(basic * 1.25)])
        mid = (lo + hi) // 2
        res = run([{"k": "lpt", "v": mid, "c": k, "y": 2027} for k in keys])
        crow = [[f'<a href="lpt-{k}.html">{COUNCILS[k][0]}</a>', f"{COUNCILS[k][3]:+g}%", eur(r["annual"]), eur(r["monthly"], 2)] for k, r in zip(keys, res)]
        facts = [f"LPT <strong>band {i + 1}</strong> covers homes valued at <strong>{eur(lo)} to {eur(hi)}</strong> on 1 November 2025.",
                 f"The basic annual charge is <strong>{eur(basic)}</strong> ({eur(basic / 12, 2)} a month) for 2026 to 2030.",
                 f"After your council's adjustment it ranges from {eur(basic * 0.85)} (−15%) to {eur(basic * 1.25)} (+25%) in 2027."]
        body = f"""<p class="lead">How much Local Property Tax do you pay in band {i + 1} ({eur(lo)} – {eur(hi)})? Your charge in every council for 2027.</p>
<p class="updated">Revenue valuation bands 2026–2030 · Checked {CHECKED}</p>
{key_facts(facts)}
<h2>Band {i + 1} LPT by council (2027)</h2>
{table(["Council", "Adjustment", "Per year", "Per month"], crow)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Check your own LPT</h2><p>Enter your value and council.</p><a class="btn" href="lpt.html">LPT calculator</a></div>
<div class="chip-list">{"".join(f'<a href="lpt-band-{j + 1}.html">Band {j + 1}</a>' for j in range(len(BANDS)) if j != i and abs(j - i) <= 3)}<a href="lpt-bands.html">All bands →</a></div>
<p>Buying a home in this price range? <a href="{pslug(min(PRICES, key=lambda x: abs(x - mid)))}">See the stamp duty and buying costs →</a></p>"""
        faqs = [(f"How much is LPT in band {i + 1}?", f"The basic charge for band {i + 1} ({eur(lo)} to {eur(hi)}) is {eur(basic)} a year, adjusted by your council by between −15% and +25%.")]
        write(f"lpt-band-{i + 1}.html", page(f"lpt-band-{i + 1}.html", f"LPT Band {i + 1} ({eur(lo)}–{eur(hi)}) – {eur(basic)} a Year | Property Tax 2026–2030",
                                             f"Local Property Tax band {i + 1}: homes worth {eur(lo)} to {eur(hi)} pay {eur(basic)} a year before council adjustments. See the 2027 charge in every council.",
                                             body, active="LPT bands", jsonld=[faq_ld(faqs)], crumbs=[("Stamp duty", "./"), ("LPT bands", "lpt-bands.html"), (f"Band {i + 1}", None)],
                                             h1=f"LPT band {i + 1}: {eur(lo)} – {eur(hi)}", sources=("rev_lpt_bands", "rev_lpt_calc", "ci_lpt")))
    # over 2.1m
    ex = run([{"k": "lpt", "v": v, "c": "dublin-city", "y": 2027} for v in (2500000, 3000000, 4000000, 5000000)])
    body = f"""<p class="lead">Homes worth more than €2.1 million aren't in a band – LPT is a percentage of the declared value.</p>
{key_facts(["0.0906% on the first €1,260,000", "0.25% on the part between €1,260,000 and €2,100,000", "0.3% on the part above €2,100,000", "You must declare the exact market value on your LPT return."])}
{table(["Value", "Basic annual LPT"], [[eur(v), eur(r['basic'])] for v, r in zip((2500000, 3000000, 4000000, 5000000), ex)])}
<p class="muted small">Your council's adjustment then applies (for example −15% in Dún Laoghaire-Rathdown).</p>"""
    write("lpt-band-over-2-1-million.html", page("lpt-band-over-2-1-million.html", "LPT on Homes Over €2.1 Million Ireland – How It's Calculated 2026",
                                                 "Local Property Tax on homes over €2.1m in Ireland: 0.0906% up to €1.26m, 0.25% to €2.1m and 0.3% above, with examples.",
                                                 body, active="LPT bands", crumbs=[("Stamp duty", "./"), ("LPT bands", "lpt-bands.html"), ("Over €2.1m", None)],
                                                 h1="LPT on homes over €2.1 million", sources=("rev_lpt_bands",)))
    body = f"""<p class="lead">All 19 Local Property Tax bands for 2026 to 2030, with the lowest and highest charge after council adjustments.</p>
<p class="updated">Valuation date 1 November 2025 · Checked {CHECKED}</p>
{key_facts(["Your band is set by your home's value on <strong>1 November 2025</strong> and stays the same until 2030 – even if the value changes or you improve the home.",
            "Basic charges run from <strong>€95</strong> (up to €240,000) to <strong>€3,110</strong> (€1,995,001 – €2,100,000).",
            "Councils can change the basic rate by −15% to +25% each year."])}
{table(["Band", "Value", "Basic / year", "Lowest (−15%)", "Highest (+25%)"], rows)}
<p><a href="lpt-band-over-2-1-million.html">Homes over €2.1 million →</a></p>"""
    write("lpt-bands.html", page("lpt-bands.html", "LPT Bands 2026–2030 Ireland – All 19 Valuation Bands & Charges",
                                 "All Local Property Tax valuation bands for 2026 to 2030: from €95 a year (up to €240,000) to €3,110, plus the rules for homes over €2.1m and council adjustments.",
                                 body, active="LPT bands", crumbs=[("Stamp duty", "./"), ("LPT bands", None)], h1="LPT valuation bands 2026–2030",
                                 sources=("rev_lpt_bands", "rev_lpt_2026", "ci_lpt")))
    crows = []
    for k in keys:
        name, county, l26, l27 = COUNCILS[k]
        crows.append([f'<a href="lpt-{k}.html">{name}</a>', f"{l26:+g}%", f"{l27:+g}%"])
        res = run([{"k": "lpt", "v": BANDS[i][0] - 1000, "c": k, "y": y} for i in range(len(BANDS)) for y in (2026, 2027)])
        brow = []
        for i in range(len(BANDS)):
            lo, hi = band_range(i)
            brow.append([f'<a href="lpt-band-{i + 1}.html">{i + 1}</a>', f"{eur(lo)} – {eur(hi)}", eur(res[2 * i]["annual"]), eur(res[2 * i + 1]["annual"])])
        change = "no change" if l26 == l27 else ("up from" if l27 > l26 else "down from") + f" {l26:+g}% in 2026"
        facts = [f"{name}'s Local Adjustment Factor is <strong>{l27:+g}%</strong> for 2027 ({change}).",
                 f"A home in band 3 ({eur(315001)} – {eur(420000)}) pays <strong>{eur(res[5]['annual'])}</strong> a year in 2027.",
                 f"A home in band 1 (up to {eur(240000)}) pays {eur(res[1]['annual'])} a year in 2027."]
        body = f"""<p class="lead">How much Local Property Tax will you pay in the {name} area? Every band for 2026 and 2027.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts(facts)}
{table(["Band", "Value on 1 Nov 2025", "2026", "2027"], brow)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Buying in {county.title()}?</h2><p>Mortgage, deposit and repayments vs the average rent.</p><a class="btn" href="../mortgage/mortgage-{county}.html" data-track="cross_app" data-label="mortgage_county">Mortgage calculator for {county.title()}</a></div>"""
        write(f"lpt-{k}.html", page(f"lpt-{k}.html", f"LPT {name} 2026 & 2027 – Local Property Tax Rates ({l27:+g}%)",
                                    f"Local Property Tax in the {name} area: {l27:+g}% Local Adjustment Factor for 2027. Annual and monthly LPT for every band in 2026 and 2027.",
                                    body, active="Councils", crumbs=[("Stamp duty", "./"), ("Councils", "lpt-councils.html"), (name, None)],
                                    h1=f"Local Property Tax – {name}", sources=("rev_lpt_bands", "rev_lpt_calc")))
    body = f"""<p class="lead">Every council's Local Adjustment Factor for Local Property Tax in 2026 and 2027.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts(["Councils can change the basic LPT rate by up to <strong>+25%</strong> or <strong>−15%</strong>.",
            "For 2027, Cavan, Leitrim and Sligo apply the maximum +25%; Laois +20%. Dún Laoghaire-Rathdown has the biggest cut at −15%.",
            "Dublin City, Louth and Meath charge the basic rate (0%)."])}
{table(["Council", "2026", "2027"], crows)}"""
    write("lpt-councils.html", page("lpt-councils.html", "LPT by Council 2026 & 2027 – Local Adjustment Factors for All 31 Councils",
                                    "Local Property Tax Local Adjustment Factors for every Irish council in 2026 and 2027 – from −15% in Dún Laoghaire-Rathdown to +25% in Cavan, Leitrim and Sligo.",
                                    body, active="Councils", crumbs=[("Stamp duty", "./"), ("Councils", None)], h1="LPT rates by council", sources=("rev_lpt_bands",)))

# ---------------------------------------------------------------- guide + FAQ
def build_guide():
    body = f"""<p class="lead">Everything buyers and homeowners need to know about stamp duty and Local Property Tax in Ireland.</p>
<p class="updated">Checked {CHECKED}</p>
<h2 id="stamp">Stamp duty</h2>
{lis(["Residential rates: <strong>1%</strong> up to €1m, <strong>2%</strong> from €1m to €1.5m, <strong>6%</strong> above €1.5m", "New homes: charged on the price excluding 13.5% VAT",
      "Buying 10 or more homes within 12 months: <strong>15%</strong>", "Non-residential property and sites without a building agreement: 7.5%",
      "There's <strong>no first-time buyer exemption</strong>", "Transfers between spouses or civil partners are exempt",
      "A gift of a home is charged on its market value", "Your solicitor files the return and pays through Revenue's eStamping – late payment means interest and penalties"])}
<h2 id="costs">Other costs when you buy</h2>
{lis([f"Solicitor: about {eur(FEES['solicitor'])} including VAT and outlays (get 3 quotes)", f"Land Registry: about {eur(FEES['landRegistry'])} for the title + {eur(FEES['mortgageReg'])} for the mortgage",
      f"Searches: about {eur(FEES['searches'])}", f"Bank valuation: about {eur(FEES['valuation'])}", f"Structural survey: about {eur(FEES['survey'])} (recommended for second-hand homes)",
      "Mortgage protection and home insurance – required by lenders"])}
<div class="ad" data-slot="content"></div>
<h2 id="lpt">Local Property Tax</h2>
{lis(["LPT is an annual tax on homes, paid to Revenue and used by your council", "Your band comes from the value on <strong>1 November 2025</strong> and applies for 2026–2030",
      "The person who owns the home on <strong>1 November</strong> pays the next year's LPT. Buy in December 2026 and the seller pays LPT for 2027",
      "Pay in one go, by direct debit, or spread through salary, pension or social welfare deductions", "You may be able to defer LPT if your income is low – check Revenue's deferral rules",
      "Some homes are exempt, for example homes with pyrite or mica damage that qualify, or a home empty for 12 months because the owner is in long-term care"])}
<div class="cta"><h2>Work out your costs</h2><p>Stamp duty, fees and the cash you need for your price.</p><a class="btn" href="./">Stamp duty calculator</a></div>"""
    write("guide.html", page("guide.html", "Stamp Duty & Local Property Tax Guide Ireland 2026 – Rates, Exemptions, Who Pays",
                             "Stamp duty and Local Property Tax in Ireland explained: rates, new build VAT rule, exemptions, who pays LPT when you buy, payment options and deferral.",
                             body, active="Guide", crumbs=[("Stamp duty", "./"), ("Guide", None)], h1="Stamp duty and LPT guide",
                             sources=("rev_sd", "ci_sd", "rev_lpt", "ci_lpt", "rev_lpt_2026")))
    FAQ = [("How much is stamp duty in Ireland?", "1% on residential property up to €1 million, 2% on the part between €1 million and €1.5 million, and 6% above €1.5 million."),
           ("Do first-time buyers pay stamp duty?", "Yes – Ireland has no first-time buyer exemption from stamp duty."),
           ("Is stamp duty charged on VAT for new homes?", "No. On a new home, stamp duty is charged on the price excluding the 13.5% VAT."),
           ("Who pays stamp duty – the buyer or seller?", "The buyer. Your solicitor pays it to Revenue through eStamping after you sign the deed."),
           ("Can stamp duty be added to my mortgage?", "Not normally – lenders lend against the property price, so stamp duty and fees come from your own savings."),
           ("How much does it cost to buy a house in Ireland on top of the price?", "Typically 2–3% of the price for stamp duty and fees – about €8,700 on a €350,000 second-hand home – plus at least a 10% deposit."),
           ("How much is LPT in 2026?", "From €95 a year (homes up to €240,000) to €3,110 (up to €2.1 million) before your council's adjustment of −15% to +25%."),
           ("Do I pay LPT in the year I buy?", "The owner on 1 November pays the following year's LPT. If you buy after 1 November, the seller is liable for the next year."),
           ("Does LPT go up if I extend my home?", "No. Your band is based on the value on 1 November 2025 and is fixed until 2030."),
           ("Is this calculator official?", "No. It's a free, independent tool based on Revenue's published rates. Fees are estimates – get quotes from a solicitor.")]
    body = f"""<p class="lead">Questions about stamp duty, buying costs and Local Property Tax in Ireland.</p><p class="updated">Checked {CHECKED}</p>{faq_html(FAQ)}"""
    write("faq.html", page("faq.html", "Stamp Duty & LPT FAQ Ireland 2026",
                           "Answers about stamp duty in Ireland (rates, first-time buyers, new builds, who pays) and Local Property Tax (bands, councils, when you buy).",
                           body, active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Stamp duty", "./"), ("FAQ", None)], h1="Stamp duty and LPT FAQ",
                           sources=("rev_sd", "ci_sd", "rev_lpt", "ci_lpt")))

# ---------------------------------------------------------------- og / sitemap / llms
def build_og():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (11, 15, 25)); d = ImageDraw.Draw(im)
    for i in range(H):
        a = max(0, 1 - i / 520); d.line([(0, i), (W, i)], fill=(int(11 + 60 * a), int(15 + 5 * a), int(25 + 20 * a)))
    def font(size, bold=True):
        for name in (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()
    d.rounded_rectangle([70, 70, 380, 116], 23, fill=(190, 18, 60)); d.text((92, 78), "IRELAND 2026", font=font(28), fill=(255, 255, 255))
    d.text((70, 160), "Stamp duty &", font=font(92), fill=(241, 245, 249))
    d.text((70, 262), "buying costs", font=font(92), fill=(251, 113, 133))
    d.text((70, 400), "Stamp duty · solicitor · fees · total cash", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 452), "Local Property Tax 2026 & 2027 by council", font=font(40, False), fill=(148, 163, 184))
    d.text((70, 545), "tavion.ie/stamp-duty  ·  free, no sign-up", font=font(32), fill=(56, 189, 248))
    im.save(os.path.join(ROOT, "og.png"), optimize=True)

def update_sitemap(files):
    path = os.path.join(REPO, "sitemap.xml")
    xml = open(path, encoding="utf-8").read()
    xml = re.sub(r"\s*<url><loc>https://tavion\.ie/stamp-duty/[^<]*</loc>.*?</url>", "", xml)
    xml = xml.replace("\n</urlset>", "".join(f'\n  <url><loc>{BASE}{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>' for fn, pr in files) + "\n</urlset>")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

def update_llms():
    path = os.path.join(REPO, "llms.txt")
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"\n- \[Irish Stamp Duty & LPT Calculator\][^\n]*", "", txt)
    txt = re.sub(r"\n## Stamp duty & LPT: key facts\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
    app = "\n- [Irish Stamp Duty & LPT Calculator](https://tavion.ie/stamp-duty/): stamp duty (1% / 2% / 6%, new homes ex-VAT), total costs of buying a home, and Local Property Tax 2026-2027 by band and council."
    txt = re.sub(r"(\n- \[Irish Citizenship Calculator\][^\n]*)", lambda m: m.group(1) + app, txt, count=1)
    l27 = ", ".join(f"{v[0]} {v[3]:+g}%" for k, v in sorted(COUNCILS.items(), key=lambda kv: kv[1][0]))
    facts = f"""
## Stamp duty & LPT: key facts

- Residential stamp duty: 1% up to €1,000,000; 2% from €1m to €1.5m; 6% above €1.5m. New homes: charged on the price excluding 13.5% VAT. 10+ homes in 12 months: 15%. No first-time buyer exemption.
- Typical buying costs on a €350,000 second-hand home: about €8,700 (stamp duty €3,500, solicitor ~€3,075, Land Registry ~€1,150, searches, valuation, survey) plus a 10% deposit.
- LPT 2026-2030: band set by value on 1 November 2025; 19 bands from €95 (up to €240,000) to €3,110 (€1,995,001-€2,100,000); over €2.1m: 0.0906% / 0.25% / 0.3% on slices. Councils adjust by -15% to +25%.
- LPT Local Adjustment Factors 2027: {l27}.
- Pages: [Stamp duty calculator](https://tavion.ie/stamp-duty/), [LPT calculator](https://tavion.ie/stamp-duty/lpt.html), [Stamp duty by price](https://tavion.ie/stamp-duty/prices.html), [LPT bands](https://tavion.ie/stamp-duty/lpt-bands.html), [LPT by council](https://tavion.ie/stamp-duty/lpt-councils.html), [FAQ](https://tavion.ie/stamp-duty/faq.html).
"""
    txt = txt.replace("\n## Optional", facts + "\n## Optional", 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)

if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    build_index(); build_prices(); build_lpt_pages(); build_guide(); build_og()
    files = [("index.html", "0.9"), ("lpt.html", "0.9"), ("prices.html", "0.8"), ("lpt-bands.html", "0.8"), ("lpt-councils.html", "0.8"), ("guide.html", "0.7"), ("faq.html", "0.7"),
             ("lpt-band-over-2-1-million.html", "0.5")] + [(pslug(p), "0.6") for p in PRICES] + [(f"lpt-band-{i + 1}.html", "0.6") for i in range(len(BANDS))] + \
            [(f"lpt-{k}.html", "0.6") for k in COUNCILS]
    update_sitemap(files); update_llms()
    print("Built", len(files), "pages in", os.path.normpath(ROOT))
