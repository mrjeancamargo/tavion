"""
Builds the static pages of the Irish Rent Checker app (tavion.ie/rent/).

Run from the repo root:   python tools/build_rent.py
Needs Node.js: examples on the pages are computed by rent/js/rules.js – the same engine the
calculators use – so pages and calculators always agree.

When the law or inflation changes: update rent/js/rules.js (LATEST_CPI, COUNTIES, rules),
the CHECKED date and the text below, then re-run.
"""
import datetime, json, os, re, subprocess
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.join(REPO, "rent")
RULES_JS = os.path.join(ROOT, "js", "rules.js")
SITE = "https://tavion.ie/"
BASE = SITE + "rent/"
CHECKED = "November 2026"
TODAY = datetime.date.today()

SRC = {
    "rtb_rent": ("RTB – Setting and reviewing private rents from 1 March 2026", "https://rtb.ie/renting/setting-and-reviewing-private-rents-from-1-march-2026/"),
    "rtb_changes": ("RTB – Rental law changes from 1 March 2026", "https://rtb.ie/renting/rental-law-changes-from-1-march-2/"),
    "rtb_stay": ("RTB – A tenant's right to stay from 1 March 2026", "https://rtb.ie/renting/tenants-right-to-stay-in-a-rented-property-from-1-march-2026/"),
    "rtb_landlord_end": ("RTB – How a landlord can end a tenancy", "https://rtb.ie/renting/how-a-landlord-can-end-a-tenancy/"),
    "rtb_tenant_end": ("RTB – How a tenant can end a tenancy", "https://rtb.ie/renting/ending-a-tenancy/how-a-tenant-can-end-a-tenancy/"),
    "rtb_notice": ("RTB – Notice of Termination guides and templates", "https://rtb.ie/renting/ending-a-tenancy/notice-of-termination-guides/"),
    "rtb_guide_end": ("RTB – Ending a tenancy from 1 March 2026: landlord guide (PDF)", "https://rtb.ie/wp-content/uploads/2026/02/Ending-a-Tenancy-Landlord-Guide-1.pdf"),
    "rtb_guide_rent": ("RTB – Setting and reviewing rent from 1 March 2026: landlord guide (PDF)", "https://rtb.ie/wp-content/uploads/2026/02/Setting-and-Reviewing-Rent-Landlord-Guide.pdf"),
    "rtb": ("RTB – Residential Tenancies Board (rent calculator, rent register, disputes)", "https://rtb.ie/"),
    "ha_rpz": ("Housing Agency – Rent Pressure Zones", "https://www.housingagency.ie/affordable-and-cost-rental-housing/rent-pressure-zones/"),
    "ci_leave": ("Citizens Information – If your landlord wants you to leave", "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/if-your-landlord-wants-you-to-leave/"),
    "ci_tenant": ("Citizens Information – If a tenant wants to end a tenancy", "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/if-a-tenant-wants-to-end-a-tenancy/"),
    "ci_rent": ("Citizens Information – Rent increases", "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/rent-increases/"),
    "threshold": ("Threshold – free advice for renters (1800 454 454)", "https://threshold.ie/"),
    "cso_cpi": ("CSO – Consumer Price Index", "https://www.cso.ie/en/statistics/prices/consumerpriceindex/"),
    "act": ("Residential Tenancies Act 2004 (revised, as amended)", "https://revisedacts.lawreform.ie/eli/2004/act/27/revised/en/html"),
}

TABS = [("./", "Rent increase"), ("notice-period.html", "Notice period"), ("new-rules-2026.html", "2026 rules"),
        ("rent-pressure-zones.html", "RPZ areas"), ("tenant-rights.html", "Tenants"), ("landlord-guide.html", "Landlords"), ("faq.html", "FAQ")]

WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

# Towns: (slug, name, county key, in a pre-June-2025 RPZ local electoral area?)
TOWNS = [
    ("dublin-city", "Dublin City", "dublin", True), ("swords", "Swords", "dublin", True), ("tallaght", "Tallaght", "dublin", True),
    ("blanchardstown", "Blanchardstown", "dublin", True), ("dun-laoghaire", "Dún Laoghaire", "dublin", True), ("lucan", "Lucan", "dublin", True),
    ("clondalkin", "Clondalkin", "dublin", True), ("balbriggan", "Balbriggan", "dublin", True),
    ("naas", "Naas", "kildare", True), ("newbridge", "Newbridge", "kildare", True), ("maynooth", "Maynooth", "kildare", True),
    ("celbridge", "Celbridge", "kildare", True), ("leixlip", "Leixlip", "kildare", True), ("athy", "Athy", "kildare", True), ("kildare-town", "Kildare town", "kildare", True),
    ("navan", "Navan", "meath", True), ("ashbourne", "Ashbourne", "meath", True), ("trim", "Trim", "meath", True), ("ratoath", "Ratoath", "meath", True),
    ("drogheda", "Drogheda", "louth", True), ("dundalk", "Dundalk", "louth", True),
    ("bray", "Bray", "wicklow", True), ("greystones", "Greystones", "wicklow", True), ("wicklow-town", "Wicklow town", "wicklow", True), ("arklow", "Arklow", "wicklow", True),
    ("galway-city", "Galway City", "galway", True), ("tuam", "Tuam", "galway", True), ("ballinasloe", "Ballinasloe", "galway", True),
    ("kilkenny", "Kilkenny", "kilkenny", True), ("limerick-city", "Limerick City", "limerick", True), ("newcastle-west", "Newcastle West", "limerick", True),
    ("waterford-city", "Waterford City", "waterford", True), ("dungarvan", "Dungarvan", "waterford", True), ("tramore", "Tramore", "waterford", True),
    ("mullingar", "Mullingar", "westmeath", True), ("athlone", "Athlone", "westmeath", True),
    ("cork-city", "Cork City", "cork", True), ("ballincollig", "Ballincollig", "cork", True), ("carrigaline", "Carrigaline", "cork", True),
    ("kinsale", "Kinsale", "cork", True), ("bandon", "Bandon", "cork", True), ("cobh", "Cobh", "cork", True), ("fermoy", "Fermoy", "cork", True),
    ("mallow", "Mallow", "cork", True), ("midleton", "Midleton", "cork", True), ("macroom", "Macroom", "cork", True),
    ("bantry", "Bantry", "cork", False), ("skibbereen", "Skibbereen", "cork", False),
    ("killarney", "Killarney", "kerry", True), ("tralee", "Tralee", "kerry", False), ("listowel", "Listowel", "kerry", False),
    ("ennis", "Ennis", "clare", True), ("shannon", "Shannon", "clare", True), ("kilrush", "Kilrush", "clare", False),
    ("carlow", "Carlow", "carlow", True), ("tullow", "Tullow", "carlow", True),
    ("portlaoise", "Portlaoise", "laois", True), ("portarlington", "Portarlington", "laois", True),
    ("castlebar", "Castlebar", "mayo", True), ("westport", "Westport", "mayo", True), ("ballina", "Ballina", "mayo", False),
    ("tullamore", "Tullamore", "offaly", True), ("birr", "Birr", "offaly", False), ("edenderry", "Edenderry", "offaly", False),
    ("roscommon", "Roscommon town", "roscommon", False), ("sligo", "Sligo", "sligo", True),
    ("gorey", "Gorey", "wexford", True), ("wexford-town", "Wexford town", "wexford", False), ("enniscorthy", "Enniscorthy", "wexford", False), ("new-ross", "New Ross", "wexford", False),
    ("letterkenny", "Letterkenny", "donegal", False), ("buncrana", "Buncrana", "donegal", False), ("cavan", "Cavan", "cavan", False),
    ("monaghan", "Monaghan", "monaghan", False), ("longford", "Longford", "longford", False), ("carrick-on-shannon", "Carrick-on-Shannon", "leitrim", False),
    ("clonmel", "Clonmel", "tipperary", False), ("nenagh", "Nenagh", "tipperary", False), ("thurles", "Thurles", "tipperary", False),
]

# ---------------------------------------------------------------- engine
NODE = r"""
const R = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.kind === "rent" ? R.rentReview(x.inp) : x.kind === "notice" ? R.notice(x.inp) : null);
  process.stdout.write(JSON.stringify({ counties: R.COUNTIES, cpi: R.LATEST_CPI, lt: R.LANDLORD_TABLE, tt: R.TENANT_TABLE, res: res }, (k, v) => v === Infinity ? null : v));
});
"""
def engine(q):
    p = subprocess.run(["node", "-e", NODE, RULES_JS], input=json.dumps(q), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)

META = engine([])
COUNTIES, CPI = META["counties"], META["cpi"]

def rent(**inp):
    return engine([{"kind": "rent", "inp": inp}])["res"][0]

# ---------------------------------------------------------------- formatting
def eur(n, dp=2):
    return "€" + f"{n:,.{dp}f}"

def nice(isod):
    y, m, dd = map(int, isod.split("-"))
    dt = datetime.date(y, m, dd)
    return f"{dt.day} {dt.strftime('%B %Y')}"

def county_status(key):
    c = COUNTIES[key]
    if c.get("whole"):
        return "whole", f"All of County {c['name']} was already a Rent Pressure Zone before 20 June 2025."
    if c["lea"]:
        return "part", f"Parts of County {c['name']} were Rent Pressure Zones before 20 June 2025 ({', '.join(c['lea'])}). The rest of the county became one on 20 June 2025."
    return "new", f"County {c['name']} became a Rent Pressure Zone on 20 June 2025, when the whole country was designated."

def sources_block(keys):
    return ('<div class="sources"><h2 class="tl">Sources – check them yourself</h2><ul>' +
            "".join(f'<li><a href="{SRC[k][1]}" rel="noopener" target="_blank">{SRC[k][0]}</a></li>' for k in keys) + "</ul></div>")

def key_facts(items):
    return '<div class="facts-box"><h2 class="tl">Key facts</h2><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"

def lis(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a in pairs]}

def faq_html(pairs):
    return "".join(f'<details class="faq"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in pairs)

def table(head, rows):
    return ('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" +
            "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")

def notice_tables():
    lt = [(b, f"{dd} days") for _, dd, b in META["lt"]]
    tt = [(b, f"{dd} days") for _, dd, b in META["tt"]]
    return lt, tt

# ---------------------------------------------------------------- shell
def share_html(text, url, label):
    wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
    fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
    return (f'<h2>Share it</h2><p class="muted">Know a renter or landlord who should check this? Send it on.</p><div class="share">'
            f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
            f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

def page(filename, title, desc, body, active=None, jsonld=(), crumbs=None, slot="content", scripts=(), share_text=None, h1=None, sources=("rtb_rent", "rtb_changes", "ci_rent")):
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
                              "publisher": {"@type": "Organization", "name": "Tavion", "url": SITE, "logo": SITE + "images/logo.png"},
                              "citation": [SRC[k][1] for k in sources]}]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
    extra = "".join(f'<script src="{s}"></script>' for s in scripts)
    share = share_html(share_text or "Free Irish rent increase & notice period checker – updated for the March 2026 rules:", url, filename.replace(".html", ""))
    big = ["dublin", "cork", "galway", "limerick", "kildare", "meath", "louth", "wicklow", "waterford", "kilkenny"]
    footer_c = " · ".join(f'<a href="rent-increase-{k}.html">{COUNTIES[k]["name"]}</a>' for k in big)
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
<meta name="theme-color" content="#0f766e">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>🏠</b> Rent Checker</a><a class="small" href="../" data-track="apps_click" data-label="rent_header">More Tavion apps</a></div>
  <nav class="tabs" aria-label="Sections"><div class="wrap">{tabs}</div></nav>
</header>
<main class="wrap">
{crumb_html}
{('<h1>' + h1 + '</h1>') if h1 else ''}
{body}
{sources_block(sources)}
<div class="ad" data-slot="{slot}"></div>
{share}
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Rent pages"><a href="./">Rent increase calculator</a><a href="notice-period.html">Notice period calculator</a><a href="new-rules-2026.html">New rules from March 2026</a><a href="rent-pressure-zones.html">Rent Pressure Zones</a><a href="tenant-rights.html">Tenant rights</a><a href="landlord-guide.html">Landlord guide</a><a href="faq.html">FAQ</a></nav>
    <p>Rent rules by county: {footer_c} · <a href="rent-pressure-zones.html">all counties</a></p>
    <p>Information checked against the Residential Tenancies Board (RTB), Citizens Information and the Housing Agency in {CHECKED}. This is a free, independent tool from <a href="../">Tavion</a>. It is not affiliated with the RTB or the Government and is general information, not legal advice. For your own case use the official <a href="https://rtb.ie/" rel="noopener">RTB Rent Calculator and Notice of Termination templates</a>, or get free advice from <a href="https://threshold.ie/" rel="noopener">Threshold</a>.</p>
    <p>Also free: <a href="../mortgage/" data-track="cross_app" data-label="mortgage">🔑 Mortgage calculator – how much can I borrow?</a> · <a href="../salary/" data-track="cross_app" data-label="salary">💶 Take-home pay calculator</a></p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="rent_footer">More free apps from Tavion</a></p>
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

county_opts = "".join(f'<option value="{k}">{COUNTIES[k]["name"]}</option>' for k in sorted(COUNTIES, key=lambda k: COUNTIES[k]["name"]))

# ---------------------------------------------------------------- rent increase calculator
def build_index():
    ex = rent(rent=1500, lastSet=(TODAY.replace(year=TODAY.year - 1)).isoformat(), county="dublin", noticeDate=TODAY.isoformat())
    body = f"""<p class="lead">Check the maximum rent increase allowed in Ireland and the earliest date it can start – for tenants and landlords. Updated for the new rules from <strong>1 March 2026</strong>. Free, no sign-up.</p>
<ul class="facts"><li>Max 2% a year (or CPI if lower)</li><li>Once every 12 months</li><li>90 days' notice</li></ul>

<form id="rentForm" class="card" novalidate>
  <label for="county" class="big-label">Where is the property?</label>
  <select id="county" required><option value="">Choose a county…</option>{county_opts}</select>
  <div id="leaBox" class="row-card" hidden>
    <p class="small" style="margin:0 0 6px"><strong>Is the property in one of these areas?</strong> <span id="leaList"></span></p>
    <div class="seg two-seg"><label><input type="radio" name="inLea" value="yes"><span>Yes</span></label><label><input type="radio" name="inLea" value="no"><span>No</span></label><label><input type="radio" name="inLea" value="unsure" checked><span>Not sure</span></label></div>
    <p class="muted small" style="margin:6px 0 0">These areas were Rent Pressure Zones before 20 June 2025. <a href="https://www.housingagency.ie/affordable-and-cost-rental-housing/rent-pressure-zones/" target="_blank" rel="noopener">Check the map</a>.</p>
  </div>

  <label for="rent" class="big-label" style="margin-top:16px">Current rent per month</label>
  <div class="money"><span>€</span><input id="rent" type="text" inputmode="decimal" autocomplete="off" placeholder="1,500"></div>

  <label for="lastSet" class="big-label" style="margin-top:16px">When was the rent last set or increased?</label>
  <input type="date" id="lastSet">
  <p class="muted small" style="margin:6px 0 0">The date the current rent started – the last increase, or the start of the tenancy if it never changed.</p>

  <details id="adv" class="adv">
    <summary>Advanced options <span class="muted small">– new build, inflation, proposed rent, notice date…</span></summary>
    <div class="adv-body">
      <label>When did the tenancy start?<input type="date" id="tenancyStart"></label>
      <p class="muted small" style="margin:4px 0 0">Tenancies created on or after 1 March 2026 follow the new rules.</p>
      <label>Type of property<select id="ptype">
        <option value="standard">Standard private rental</option>
        <option value="newbuild">New apartment – construction started after 10 June 2025</option>
        <option value="ssa">Student specific accommodation</option>
        <option value="ahb">Approved Housing Body (AHB) or cost rental</option></select></label>
      <div class="two">
        <label>Date notice is (or was) served<input type="date" id="noticeDate"></label>
        <label>Date the new rent would start<input type="date" id="effective"></label>
      </div>
      <label>Inflation (CPI) since the rent was last set<select id="cpiMode">
        <option value="above">Above 2% a year – use the 2% cap (current situation)</option>
        <option value="known">I know the CPI change (from the RTB Rent Calculator)</option></select></label>
      <div id="cpiBox" hidden><label>CPI change over the period (%)<input id="cpi" type="number" step="0.01" inputmode="decimal" placeholder="e.g. 3.1"></label></div>
      <label>New rent asked for / proposed (optional)<div class="money"><span>€</span><input id="proposed" type="text" inputmode="decimal" placeholder="1,560"></div></label>
      <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
    </div>
  </details>

  <div class="btn-row"><button type="submit" class="btn primary">Check the maximum rent</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Everything is worked out on your device. Nothing is sent to us.</p>
</form>

<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>

<div class="card switch"><strong>Got a notice to leave – or need to give one?</strong> <a href="notice-period.html">Check the notice period and whether it's valid →</a></div>

<h2>How rent increases work in Ireland</h2>
<div class="card"><ol class="steps">
<li><strong>Once every 12 months.</strong> Rent can only be reviewed once a year – or after 24 months for the first review in an area that became a Rent Pressure Zone on 20 June 2025.</li>
<li><strong>2% a year, or inflation if lower.</strong> Since 1 March 2026 the cap uses the Consumer Price Index (CPI). Inflation is {CPI['pct']}% ({CPI['month']}), so the 2% cap applies, pro rata for the time since the rent was last set.</li>
<li><strong>90 days' written notice.</strong> The landlord must send the rent review notice to the tenant <em>and the RTB on the same day</em>, with the RTB Rent Calculator printout and 3 comparable rents from the RTB Rent Register.</li>
<li><strong>No resets for existing tenancies.</strong> Tenancies that started before 1 March 2026 can never be reset to market rent. Newer tenancies can reset at the start of the tenancy (in some cases) and at the end of each 6-year cycle.</li>
</ol></div>
<p>Example: rent of €1,500 last set 12 months ago in Dublin can rise to at most <strong>{eur(ex['maxRent'])}</strong> (+{eur(ex['maxIncrease'])}), from {nice(ex['earliest'])} at the earliest if notice is served today.</p>

<div class="cta"><h2>New rules from 1 March 2026</h2><p>6-year tenancies, limits on evictions and when rent can reset – explained simply.</p><a class="btn" href="new-rules-2026.html">Read the new rules</a></div>
"""
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Rent Increase Calculator", "url": BASE,
              "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "featureList": ["Maximum legal rent increase (2% or CPI)", "Earliest date a rent increase can start", "24-month first review rule for areas designated on 20 June 2025",
                              "New build CPI rule", "Check if a proposed rent increase is legal", "Notice of termination period checker"],
              "description": "Free calculator for the maximum rent increase allowed in Ireland under the rent control rules in force from 1 March 2026."}
    faqs = [("How much can my rent go up in Ireland?", f"By at most 2% a year, or by inflation (CPI) if that's lower, and only once every 12 months with 90 days' notice. With inflation at {CPI['pct']}% the 2% cap applies."),
            ("Is the whole of Ireland a Rent Pressure Zone?", "Yes. Since 20 June 2025 the whole country has been a Rent Pressure Zone, and since 1 March 2026 a national rent control system applies to all private tenancies.")]
    write("index.html", page("index.html", "Rent Increase Calculator Ireland 2026 – Maximum Legal Rent Increase (2% Cap)",
                             "Free Irish rent increase calculator: check the maximum legal rent increase (2% or CPI) and the earliest date it can start under the rules from 1 March 2026. For tenants and landlords.",
                             body, active="Rent increase", jsonld=[app_ld, faq_ld(faqs)], slot="calculator", scripts=["js/rules.js", "js/rent.js"],
                             h1="Rent increase calculator Ireland", sources=("rtb_rent", "rtb_guide_rent", "ha_rpz", "cso_cpi", "ci_rent", "rtb"),
                             share_text="Is your rent increase legal? Free checker for Ireland 🇮🇪 – 2% cap, 90 days' notice, new 2026 rules:"))

# ---------------------------------------------------------------- notice period calculator
def build_notice():
    lt, tt = notice_tables()
    reasons_l = [("first6", "Any reason – tenancy under 6 months"), ("sale", "Selling the property"), ("family", "Landlord or family member moving in"),
                 ("refurb", "Substantial refurbishment"), ("change", "Change of use"), ("unsuitable", "Property no longer suits tenant's needs"),
                 ("arrears", "Rent arrears"), ("breach", "Other breach by tenant"), ("asb", "Serious anti-social behaviour"), ("endterm", "End of Part 4 term (no reason)")]
    reasons_t = [("t-none", "Leaving – no reason needed"), ("t-breach", "Landlord broke their obligations"), ("t-danger", "Danger to life or the property")]
    opts_l = "".join(f'<option value="{k}">{v}</option>' for k, v in reasons_l)
    opts_t = "".join(f'<option value="{k}">{v}</option>' for k, v in reasons_t)
    body = f"""<p class="lead">How much notice does a landlord or tenant have to give in Ireland? Enter the tenancy dates and the reason to see the notice period, the earliest end date and whether the reason is allowed under the <strong>March 2026 rules</strong>.</p>
<ul class="facts"><li>Landlord: 90 to 224 days</li><li>Tenant: 28 to 112 days</li><li>Copy to RTB same day</li></ul>

<form id="noticeForm" class="card" novalidate>
  <fieldset><legend class="sm">Who is ending the tenancy?</legend>
    <div class="seg two-seg"><label><input type="radio" name="who" value="landlord" checked><span>Landlord</span></label><label><input type="radio" name="who" value="tenant"><span>Tenant</span></label></div>
  </fieldset>
  <div class="two">
    <label>Tenancy start date<input type="date" id="start"></label>
    <label>Date notice served<input type="date" id="served"></label>
  </div>
  <label id="reasonL">Reason<select id="reasonLandlord">{opts_l}</select></label>
  <label id="reasonT" hidden>Reason<select id="reasonTenant">{opts_t}</select></label>

  <details id="adv" class="adv">
    <summary>Advanced options <span class="muted small">– landlord size, hardship, check a notice…</span></summary>
    <div class="adv-body">
      <div id="llOnly">
        <label>How many tenancies does the landlord have?<select id="size"><option value="small">1–3 tenancies (small landlord)</option><option value="large">4 or more, or a company (large landlord)</option></select></label>
        <p class="muted small" style="margin:4px 0 0">Only matters for tenancies that started on or after 1 March 2026. Counted on the day the notice is served.</p>
        <label class="check"><input type="checkbox" id="hardship"><span>Selling to avoid undue financial or other hardship <small class="muted">(e.g. to buy a home to live in, repay a debt, insolvency arrangement)</small></span></label>
        <label class="check"><input type="checkbox" id="familyClose"><span>The person moving in is the landlord, their spouse/civil partner, parent or child</span></label>
        <label class="check"><input type="checkbox" id="copied" checked><span>The notice was sent to the RTB on the same day</span></label>
      </div>
      <label class="check"><input type="checkbox" id="ssa"><span>Student specific accommodation</span></label>
      <label>Termination date written on the notice (to check it)<input type="date" id="endDate"></label>
      <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
    </div>
  </details>
  <div class="btn-row"><button type="submit" class="btn primary">Check the notice period</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>

<h2>Notice periods a landlord must give</h2>
{table(["Tenancy length (when notice is served)", "Notice"], lt)}
<p class="muted small">Shorter notice: 28 days for rent arrears or other breaches (after a valid warning notice), 7 days for serious anti-social behaviour.</p>
<h2>Notice periods a tenant must give</h2>
{table(["Tenancy length", "Notice"], tt)}
<p class="muted small">Shorter notice: 28 days if the landlord breaches their obligations and doesn't fix it, 7 days if there's a danger to life or the structure. Student specific accommodation: 28 days.</p>

<h2>Is the notice valid? Checklist</h2>
<div class="card">{lis(["In writing (letter or email) – not a text or a phone call", "Signed by the landlord or their agent (or by the tenant)", "Shows the date it is served",
    "States the reason (always for landlords; for tenants only if leaving because of a breach or danger)", "Gives the termination date – with at least the right notice period",
    "Says the other side has <strong>90 days</strong> (no breach) or <strong>28 days</strong> (breach) to refer a dispute to the RTB",
    "Landlords: sent to the tenant <strong>and the RTB on the same day</strong> (since 1 March 2026), using the right RTB template",
    "Landlords: includes the statutory declaration or statement required for the reason"])}</div>
<div class="callout warn">Received a notice you think is invalid? You can refer a dispute to the RTB – within 90 days if the notice isn't for a breach, 28 days if it is. Free advice: Threshold, 1800 454 454.</div>
"""
    faqs = [("How much notice does a landlord have to give in Ireland?", "From 90 days (tenancy under 6 months) to 224 days (8 years or more): 90 days under 6 months, 152 days for 6 months to 1 year, 180 days for 1 to 7 years, 196 days for 7 to 8 years and 224 days for 8 years or more. 28 days for arrears or breaches, after a warning notice."),
            ("How much notice does a tenant have to give?", "28 days under 6 months, 35 days for 6 months to 1 year, 42 days for 1–2 years, 56 days for 2–4 years, 84 days for 4–8 years and 112 days for 8 years or more."),
            ("Can my landlord evict me to sell from March 2026?", "It depends on when your tenancy started and the landlord's size. For tenancies from 1 March 2026, a landlord with 4+ tenancies can't end it to sell. A landlord with 1–3 tenancies can only sell during the 6-year cycle to avoid undue hardship, otherwise at the end of the cycle. Tenancies that started before 1 March 2026 can still be ended for a sale.")]
    write("notice-period.html", page("notice-period.html", "Notice Period Calculator Ireland 2026 – Notice of Termination for Landlords & Tenants",
                                     "How much notice to end a tenancy in Ireland? Free calculator for landlord and tenant notice periods (90–224 days, 28–112 days), valid reasons and the 1 March 2026 rules.",
                                     body, active="Notice period", jsonld=[faq_ld(faqs)], slot="calculator", scripts=["js/rules.js", "js/notice.js"],
                                     crumbs=[("Rent Checker", "./"), ("Notice period", None)], h1="Notice period calculator Ireland",
                                     sources=("rtb_changes", "rtb_landlord_end", "rtb_tenant_end", "rtb_guide_end", "rtb_notice", "ci_leave", "ci_tenant", "threshold"),
                                     share_text="Got a notice to leave? Check if it's valid and how much notice you're owed – free, Irish rules from March 2026:"))

# ---------------------------------------------------------------- new rules explainer
def build_rules():
    body = f"""<p class="lead">On 1 March 2026 Ireland's rental rules changed. Here's what's different for tenants and landlords – and what stays the same for existing tenancies.</p>
<p class="updated">Checked against RTB guidance · {CHECKED}</p>
{key_facts(["The new rules apply to tenancies <strong>created on or after 1 March 2026</strong>. Existing tenancies keep the old termination rules.",
            "Rent can rise by <strong>2% a year, or CPI inflation if lower</strong>, once every 12 months – for all private tenancies, old and new.",
            "New tenancies have a <strong>6-year Tenancy of Minimum Duration</strong>. Landlords with 4+ tenancies can only end them for a tenant breach or if the property no longer suits.",
            "Rent can be reset to market rent only at the start of a new tenancy (not after a no-fault eviction) and at the end of each 6-year cycle.",
            "Every rent notice and Notice of Termination must be sent to the <strong>RTB on the same day</strong> as the tenant, or it's invalid."])}
<h2>Rent increases: old vs new tenancies</h2>
{table(["", "Annual increase", "Reset to market rent"], [
    ["Tenancy started before 1 March 2026", "2% or CPI if lower", "Never, while the tenancy continues"],
    ["Tenancy started from 1 March 2026", "2% or CPI if lower", "At the start of a new tenancy (not after a no-fault termination) and at the end of each 6-year cycle"],
    ["New apartment (construction started after 10 June 2025)", "In line with CPI – no 2% cap", "As above"],
    ["Student specific accommodation", "2% or CPI if lower (new SSA: CPI)", "Once every 3 years from 1 March 2029"],
    ["AHB and cost rental", "Not covered by rent control", "–"]])}
<h2>When can rent be reset to market rent at the start of a new tenancy?</h2>
<p>Only if the previous tenancy ended because the tenant left by choice, the tenant breached their obligations, or the property no longer suited the tenant's needs. Also for a first-ever letting, a home with no tenancy for 2 years (1 year for a protected structure), or after a substantial renovation where the home was offered back to the previous tenant. <strong>Not</strong> if the landlord ended the last tenancy in the previous 2 years to sell, move in a family member or change the use (a "no-fault termination") – including in the first 6 months.</p>
<p>The landlord must give a statement that the rent is not above market rent, backed by 3 comparable tenancies from the RTB Rent Register that began in the last 3 months.</p>
<div class="ad" data-slot="content"></div>
<h2>Ending a tenancy: who can do what</h2>
{table(["Tenancy", "Landlord with 1–3 tenancies", "Landlord with 4+ tenancies or a company"], [
    ["First 6 months (any tenancy)", "Any reason – notice to tenant and RTB same day", "Any reason – notice to tenant and RTB same day"],
    ["Started from 1 March 2026 – during the 6-year cycle", "Tenant breach · no longer suitable · sale to avoid undue hardship · landlord or close family moving in", "Tenant breach · no longer suitable – nothing else"],
    ["Started from 1 March 2026 – end of the 6-year cycle", "Also: sale · family (incl. wider family) · substantial refurbishment · change of use", "Tenant breach · no longer suitable – tenancy continues indefinitely"],
    ["Started before 1 March 2026", "Breach · not suitable · sale (within 9 months) · family · refurbishment · change of use", "Same 6 reasons (family use only for private landlords)"],
    ["Started before 11 June 2022", "Also: any reason at the end of the Part 4 term (all terms end by 11 June 2028)", "Same"]])}
<h2>Other changes</h2>
{lis(["<strong>Sales with tenants in place:</strong> the new owner steps into the landlord's shoes and the tenant keeps the rest of their cycle.",
      "<strong>Landlord size counts on the day notice is served.</strong> A small landlord must include a statement confirming they have 1–3 tenancies. Tenants can ask the RTB to confirm.",
      "<strong>Longer time to challenge a notice:</strong> 90 days to refer a dispute to the RTB where there's no breach (28 days for breaches).",
      "<strong>RTB Rent Register:</strong> new rents must be justified with 3 comparable rents."])}
<div class="cta"><h2>Check your situation</h2><p>Use the calculators to see exactly what applies to your tenancy.</p><a class="btn" href="notice-period.html">Notice period calculator</a></div>"""
    faqs = [("Do the March 2026 rental rules apply to my existing tenancy?", "The new termination rules (6-year minimum duration, limits for large landlords) only apply to tenancies created from 1 March 2026. The rent cap (2% or CPI if lower) applies to all private tenancies, and existing tenancies can't be reset to market rent."),
            ("What is a Tenancy of Minimum Duration?", "From 1 March 2026, new tenancies run in rolling 6-year cycles. After the first 6 months the tenant has security of tenure, and a small landlord can only end the tenancy for limited reasons during each cycle."),
            ("Who counts as a large landlord?", "A landlord with 4 or more tenancies, or any company landlord. It's counted on the day the Notice of Termination is served.")]
    body += "<h2>Questions</h2>" + faq_html(faqs)
    write("new-rules-2026.html", page("new-rules-2026.html", "New Rental Rules Ireland from 1 March 2026 Explained – Rent Caps, 6-Year Tenancies, Evictions",
                                      "The Irish rental rules from 1 March 2026 in plain English: national 2% rent cap, 6-year tenancies, limits on no-fault evictions, market rent resets, small vs large landlords.",
                                      body, active="2026 rules", jsonld=[faq_ld(faqs)], crumbs=[("Rent Checker", "./"), ("New rules 2026", None)],
                                      h1="New rental rules from 1 March 2026", sources=("rtb_changes", "rtb_rent", "rtb_stay", "rtb_guide_end", "rtb_guide_rent", "ci_leave"),
                                      share_text="The new rental rules from March 2026, explained simply:"))

# ---------------------------------------------------------------- RPZ + counties + towns
def build_places():
    rows = []
    for k in sorted(COUNTIES, key=lambda k: COUNTIES[k]["name"]):
        st, txt = county_status(k)
        c = COUNTIES[k]
        before = "Whole county" if st == "whole" else (", ".join(c["lea"]) if st == "part" else "–")
        rows.append([f'<a href="rent-increase-{k}.html">{c["name"]}</a>', before, "20 June 2025" if st != "whole" else "Before 2025"])
    body = f"""<p class="lead">Is your area a Rent Pressure Zone? Since <strong>20 June 2025 the whole of Ireland is</strong>. What still matters is whether your area was an RPZ <em>before</em> that date.</p>
<p class="updated">Checked against the Housing Agency and RTB · {CHECKED}</p>
{key_facts(["Every county in Ireland has been a Rent Pressure Zone since 20 June 2025, and from 1 March 2026 a national rent control system covers all private tenancies.",
            "Rent can rise by at most 2% a year, or CPI inflation if lower.",
            "<strong>Areas newly designated on 20 June 2025:</strong> for existing tenancies, the first rent review must wait <strong>24 months</strong> from when the rent was last set. After that, every 12 months.",
            "Areas designated before 20 June 2025 (all of Dublin, Kildare, Meath, Wicklow, Louth, Galway, Kilkenny, Limerick, Waterford, Westmeath and parts of other counties): reviews every 12 months."])}
<h2>Areas that were Rent Pressure Zones before 20 June 2025</h2>
{table(["County", "Already an RPZ before 20 June 2025", "Rest of county became RPZ"], rows)}
<p class="muted small">Local Electoral Area boundaries don't always follow town names. If you're near a boundary, check the Housing Agency's RPZ map or the RTB Rent Calculator.</p>
<h2>Rent rules by town</h2>
<div class="chip-list">{"".join(f'<a href="rent-increase-{s}.html">{n}</a>' for s, n, _, _ in sorted(TOWNS, key=lambda t: t[1]))}</div>"""
    write("rent-pressure-zones.html", page("rent-pressure-zones.html", "Rent Pressure Zones Ireland 2026 – Is My Area an RPZ? Full List by County",
                                           "Every area in Ireland has been a Rent Pressure Zone since 20 June 2025. See which areas were RPZs before, the 24-month first-review rule, and rent rules by county and town.",
                                           body, active="RPZ areas", crumbs=[("Rent Checker", "./"), ("Rent Pressure Zones", None)], h1="Rent Pressure Zones in Ireland",
                                           sources=("ha_rpz", "rtb_rent", "rtb_changes"), share_text="Is your area a Rent Pressure Zone? Full list for Ireland:"))

    ref = TODAY.isoformat()
    last = (TODAY.replace(year=TODAY.year - 2) + datetime.timedelta(days=60)).isoformat()  # an older rent date to show the 24-month rule

    def place_page(fname, place, county_key, in_lea, crumb_extra=None, extra_html=""):
        c = COUNTIES[county_key]
        st, ctext = county_status(county_key)
        before = True if st == "whole" else (bool(in_lea) if st == "part" else False)
        ex12 = rent(rent=1500, lastSet=(TODAY.replace(year=TODAY.year - 1)).isoformat(), county=county_key, inLea=before, noticeDate=ref)
        exOld = rent(rent=1500, lastSet=last, county=county_key, inLea=before, noticeDate=ref)
        status = (f"{place} was already a Rent Pressure Zone before 20 June 2025." if before else
                  f"{place} became a Rent Pressure Zone on 20 June 2025, when the whole country was designated.")
        rule = ("Rent can be reviewed once every 12 months." if before else
                "For tenancies that existed then, the <strong>first rent review must wait 24 months</strong> from when the rent was last set (until 20 June 2027 at the latest). After that, every 12 months.")
        if st == "part" and crumb_extra is None:  # county page for a county that was only partly an RPZ
            status = ctext
            rule = ("In those areas rent can be reviewed every 12 months. In the rest of the county, the <strong>first review of a tenancy that existed on 20 June 2025 must wait 24 months</strong> "
                    "from when the rent was last set. After that, every 12 months.")
        facts = [status, rule, f"The rent can go up by at most <strong>2% a year</strong> (or CPI inflation if lower – inflation is {CPI['pct']}% now), with 90 days' written notice copied to the RTB.",
                 f"Example: €1,500 a month last set 12 months ago → maximum <strong>{eur(ex12['maxRent'])}</strong>, from {nice(ex12['earliest'])} at the earliest (notice served today)."]
        q = f"?county={county_key}" + ("&lea=" + ("yes" if before else "no") if st == "part" else "")
        body = f"""<p class="lead">Rent increase rules and notice periods for {place}{'' if place.endswith(c['name']) else ', Co. ' + c['name']}: how much your rent can go up, when, and how much notice is needed to end a tenancy.</p>
<p class="updated">Updated for the 1 March 2026 rules · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="cta"><h2>Check a rent increase in {place}</h2><p>Enter the rent and the date it was last set.</p><a class="btn" href="./{q}" data-track="place_cta" data-label="{fname}">Open the rent calculator</a></div>
<h2>Rent examples in {place}</h2>
{table(["Current rent", "Last set", "Maximum new rent", "Earliest start"], [
    [eur(1500), "12 months ago", eur(ex12['maxRent']), nice(ex12['earliest'])],
    [eur(1500), nice(last), eur(exOld['maxRent']), nice(exOld['earliest'])],
])}
<p class="muted small">Assumes notice served today ({nice(ref)}) and inflation above 2% a year. {'The second example shows the 24-month first-review rule for areas designated on 20 June 2025.' if not before else ''}</p>
{extra_html}
<div class="ad" data-slot="content"></div>
<h2>Ending a tenancy in {place}</h2>
<p>Notice periods are the same everywhere in Ireland. A landlord must give 90 days (under 6 months) up to 224 days (8+ years); a tenant 28 to 112 days. For tenancies created from 1 March 2026, landlords with 4 or more tenancies can only end a tenancy for a tenant breach or if the property no longer suits the tenant. <a href="notice-period.html">Check a notice →</a></p>
<h2>Help in {c['name']}</h2>
{lis(["<a href='https://rtb.ie/' rel='noopener'>Residential Tenancies Board</a> – rent calculator, rent register, registering tenancies, disputes",
      "<a href='https://threshold.ie/' rel='noopener'>Threshold</a> – free advice for renters: 1800 454 454",
      f"<a href='https://www.citizensinformation.ie/' rel='noopener'>Citizens Information</a> – local Citizens Information Centres in {c['name']}"])}"""
        crumbs = [("Rent Checker", "./"), ("RPZ areas", "rent-pressure-zones.html")] + (crumb_extra or []) + [(place, None)]
        faqs = [(f"Is {place} a Rent Pressure Zone?", re.sub("<[^>]+>", "", status + " " + rule)),
                (f"How much can rent go up in {place}?", "By at most 2% a year, or inflation (CPI) if lower, once every 12 months" +
                 ("" if before else " (the first review of a tenancy that existed on 20 June 2025 must wait 24 months from when the rent was last set)") +
                 ", with 90 days' written notice sent to the tenant and the RTB on the same day.")]
        write(fname, page(fname, f"Rent Increase {place} 2026 – Rent Pressure Zone Rules, Max Rent & Notice",
                          f"Is {place} a Rent Pressure Zone? Rent increase rules in {place} from March 2026: max 2% a year, {'12' if before else '24'}-month review rule, notice periods and a free calculator.",
                          body, active="RPZ areas", jsonld=[faq_ld(faqs)], crumbs=crumbs, h1=f"Rent increase rules in {place}",
                          sources=("ha_rpz", "rtb_rent", "rtb_changes", "ci_rent"), share_text=f"Rent increase rules in {place} – free checker:"))

    for k, c in COUNTIES.items():
        towns = [t for t in TOWNS if t[2] == k]
        st, _ = county_status(k)
        extra = ""
        if st == "part":
            extra = f"<h2>Which parts of County {c['name']} were RPZs before 20 June 2025?</h2>" + lis(c["lea"]) + "<p class='muted small'>These are Local Electoral Areas – check the Housing Agency map if you're unsure which one you're in.</p>"
        if towns:
            extra += f"<h2>Towns in County {c['name']}</h2><div class='chip-list'>" + "".join(f'<a href="rent-increase-{s}.html">{n}</a>' for s, n, _, _ in towns) + "</div>"
        if st == "part":
            extra = "<p><strong>The examples above are for the parts of the county that became RPZs on 20 June 2025.</strong></p>" + extra
        place_page(f"rent-increase-{k}.html", f"County {c['name']}", k, st == "whole", extra_html=extra)
    for s, n, k, lea in TOWNS:
        place_page(f"rent-increase-{s}.html", n, k, lea, crumb_extra=[(f"Co. {COUNTIES[k]['name']}", f"rent-increase-{k}.html")])

# ---------------------------------------------------------------- tenants / landlords guides
def build_guides():
    body = f"""<p class="lead">Your rights as a tenant in Ireland – rent increases, notices to leave, deposits and where to get help. Updated for the 1 March 2026 rules.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Your rent can only go up once every 12 months, by 2% a year at most (or CPI if lower), with 90 days' written notice that is also sent to the RTB.",
            "After 6 months you have security of tenure – your landlord needs a legal reason to end the tenancy.",
            "A notice to leave must be in writing, signed, dated, give the reason and a termination date with the full notice period – otherwise you can challenge it.",
            "You have 90 days (28 for breach cases) to refer a notice dispute to the RTB.",
            "Deposits: a landlord can ask for at most 1 month's rent as deposit and 1 month in advance."])}
<h2>Tips: what to do when you get a rent increase</h2>
<div class="card"><ol class="steps">
<li><strong>Check the dates.</strong> Was the rent last set at least 12 months ago (24 for the first review in an area designated on 20 June 2025)? Are you getting 90 days' notice?</li>
<li><strong>Check the amount</strong> with our <a href="./">rent calculator</a> and the official RTB Rent Calculator.</li>
<li><strong>Check the notice</strong> includes the RTB Rent Calculator printout and 3 comparable rents from the RTB Rent Register, and that it was sent to the RTB.</li>
<li><strong>Dispute it</strong> with the RTB if it's too high or invalid – before the new rent starts, or within 28 days of getting the notice, whichever is later.</li>
</ol></div>
<h2>Tips: what to do when you get a Notice of Termination</h2>
<div class="card"><ol class="steps">
<li><strong>Don't panic and don't leave early</strong> – you can stay until the termination date, and an invalid notice doesn't end the tenancy.</li>
<li><strong>Check it</strong> with the <a href="notice-period.html">notice period calculator</a>: right reason for your tenancy and landlord size? Long enough notice? Sent to the RTB? Statutory declaration attached?</li>
<li><strong>Ask the RTB</strong> to confirm whether your landlord has 3 or fewer tenancies if they're relying on a small-landlord reason.</li>
<li><strong>Get free advice</strong> from Threshold (1800 454 454) and refer a dispute to the RTB within the deadline if you think the notice is invalid.</li>
<li><strong>If the reason doesn't happen</strong> – no sale, nobody moves in – the landlord may have to offer you the tenancy back. Tell the RTB.</li>
</ol></div>
<div class="ad" data-slot="content"></div>
<h2>Your rights in a rented home</h2>
{lis(["A rent book or written record of rent paid, and a copy of the tenancy agreement", "Privacy – the landlord can only enter with your permission, except in an emergency",
      "Repairs – the landlord must keep the property to minimum standards (heating, damp, safety)", "Your deposit back promptly at the end, minus only unpaid rent or damage beyond normal wear and tear",
      "No penalisation for contacting the RTB or asserting your rights", "Your tenancy must be registered with the RTB – you can check the public register"])}
<h2>Your responsibilities</h2>
{lis(["Pay rent on time", "Don't damage the property or cause anti-social behaviour", "Let the landlord in for repairs and inspections (by arrangement)", "Give the right notice when you leave"])}
<div class="cta"><h2>Check your rent increase</h2><p>Find the maximum legal rent and the earliest date it can start.</p><a class="btn" href="./">Rent increase calculator</a></div>"""
    write("tenant-rights.html", page("tenant-rights.html", "Tenant Rights Ireland 2026 – Rent Increases, Notices to Leave & What To Do",
                                     "Know your rights as a renter in Ireland: rent increase limits, notice periods, valid notices, deposits, disputes with the RTB and free help from Threshold. Updated for March 2026.",
                                     body, active="Tenants", crumbs=[("Rent Checker", "./"), ("Tenant rights", None)], h1="Tenant rights in Ireland",
                                     sources=("ci_leave", "ci_rent", "rtb_stay", "rtb_tenant_end", "threshold", "rtb"), share_text="Renting in Ireland? Know your rights – rent increases and notices explained:"))

    body = f"""<p class="lead">A plain-English guide for landlords: setting and reviewing rent, ending a tenancy correctly and the documents you need under the 1 March 2026 rules.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["Register every tenancy with the RTB and update the rent on your registration after each review.",
            "Review rent at most once every 12 months, by up to 2% a year (or CPI if lower), with at least 90 days' notice – sent to the tenant and the RTB on the same day.",
            "From 1 March 2026 a Notice of Termination that isn't sent to the RTB on the same day is invalid.",
            "Landlords with 4+ tenancies (or companies) can't end new tenancies (from 1 March 2026) to sell, refurbish or move family in.",
            "Use the RTB templates – they include the statutory declarations and statements each reason needs."])}
<h2>Reviewing rent: 5 steps</h2>
<div class="card"><ol class="steps">
<li><strong>Check the rules</strong> for your tenancy (when it started, new build, SSA, RPZ date).</li>
<li><strong>Calculate</strong> the maximum with the RTB Rent Calculator (or <a href="./">ours</a> for a quick check), and confirm the rent isn't above market rent with 3 comparables from the RTB Rent Register.</li>
<li><strong>Complete</strong> the RTB Notice of Rent Review template (Part D if you claim a substantial change exemption).</li>
<li><strong>Send</strong> it to the tenant and the RTB on the same day, at least 90 days before the new rent starts.</li>
<li><strong>Update</strong> the rent on your RTB tenancy registration.</li>
</ol></div>
<h2>Ending a tenancy: documents for each reason</h2>
{table(["Reason", "What you need"], [["First 6 months", "Statement"], ["Property no longer suits tenant's needs", "Statement"], ["Selling", "Statutory declaration"],
    ["Landlord or family moving in", "Statutory declaration"], ["Substantial refurbishment", "Statutory declaration + statement"], ["Change of use", "Statutory declaration + statement"],
    ["Rent arrears", "Warning notice to tenant and RTB (28 days to pay) first, then 28 days' notice"], ["Other breach", "Warning notice with reasonable time to fix, then 28 days' notice"],
    ["Serious anti-social behaviour", "7 days' notice, no warning needed"]])}
<div class="ad" data-slot="content"></div>
<h2>Common mistakes that make a notice invalid</h2>
{lis(["Not sending it to the RTB on the same day (from 1 March 2026)", "Too short a notice period – count from the tenancy length on the day you serve it",
      "Missing reason, signature, date of service or termination date", "Missing statutory declaration or statement", "Using a reason that isn't allowed for the tenancy or your landlord size",
      "Serving a 28-day arrears notice without a valid warning notice first"])}
<h2>Small landlord selling during a 6-year cycle</h2>
<p>A landlord with 1–3 tenancies can end a tenancy created from 1 March 2026 during the cycle to sell only to avoid undue financial or other hardship – where you, your spouse or civil partner need the proceeds for a home to live in, to repay a debt in full (or pay at least 15% of the asking price within 9 months, including tax or Fair Deal debt), or under a personal insolvency arrangement. Reaching retirement age on its own isn't hardship.</p>
<div class="cta"><h2>Check a notice before you send it</h2><p>See the notice period, earliest end date and whether your reason is allowed.</p><a class="btn" href="notice-period.html">Notice period calculator</a></div>"""
    write("landlord-guide.html", page("landlord-guide.html", "Landlord Guide Ireland 2026 – Rent Reviews, Notices of Termination & RTB Rules",
                                      "Guide for Irish landlords under the March 2026 rules: reviewing rent (2% cap, 90 days' notice, RTB), ending a tenancy correctly, statutory declarations and small vs large landlords.",
                                      body, active="Landlords", crumbs=[("Rent Checker", "./"), ("Landlord guide", None)], h1="Landlord guide: rent and notices",
                                      sources=("rtb_guide_rent", "rtb_guide_end", "rtb_changes", "rtb_notice", "rtb_rent", "act"), share_text="Landlords: the 2026 rules on rent reviews and notices, explained:"))

# ---------------------------------------------------------------- FAQ
def build_faq():
    FAQ = [
        ("How much can a landlord increase rent in Ireland in 2026?", f"By at most 2% a year, or by inflation (CPI) if lower, worked out pro rata from when the rent was last set. Inflation was {CPI['pct']}% in the 12 months to {CPI['month']}, so the 2% cap applies. Increases are allowed once every 12 months with 90 days' notice."),
        ("How often can rent be increased?", "Once every 12 months. In areas that only became Rent Pressure Zones on 20 June 2025, the first review for an existing tenancy must wait 24 months from when the rent was last set."),
        ("Is my area a Rent Pressure Zone?", "Yes – the whole of Ireland has been a Rent Pressure Zone since 20 June 2025. See which areas were RPZs before that date on our <a href='rent-pressure-zones.html'>RPZ page</a>."),
        ("If my rent hasn't gone up in years, can the landlord add 2% for every year?", "The cap is 2% a year pro rata over the time since the rent was last set, or the CPI change over that period if lower. So a rent unchanged for 3 years could rise by up to about 6% if inflation over those years was at least that much. Use the RTB Rent Calculator for the exact figure."),
        ("Can my landlord reset my rent to market rent?", "Not if your tenancy started before 1 March 2026. For tenancies from 1 March 2026, rent can be reset at the start of a new tenancy (unless the previous one ended with a no-fault termination) and at the end of each 6-year cycle."),
        ("Does the rent cap apply to new builds?", "Apartments where construction started after 10 June 2025 can increase in line with CPI with no 2% cap. They're still limited to once every 12 months."),
        ("How much notice does my landlord have to give for a rent increase?", "At least 90 days in writing, sent to you and the RTB on the same day. It must include the RTB Rent Calculator printout and 3 comparable rents from the RTB Rent Register."),
        ("How do I challenge a rent increase?", "Refer a dispute to the RTB before the new rent takes effect, or within 28 days of receiving the notice, whichever is later. Keep paying your current rent in the meantime."),
        ("How much notice does a landlord need to give to end a tenancy?", "90 days under 6 months, 152 days for 6–12 months, 180 days for 1–7 years, 196 days for 7–8 years and 224 days for 8+ years. Shorter for breaches (28 days) and serious anti-social behaviour (7 days)."),
        ("Can a landlord evict me to sell the house?", "If your tenancy started before 1 March 2026: yes, with a statutory declaration that they intend to sell within 9 months. If it started from 1 March 2026: a landlord with 4+ tenancies can't; a landlord with 1–3 tenancies can only during the 6-year cycle to avoid undue hardship, or at the end of the cycle."),
        ("Can a landlord evict me so a family member can move in?", "For tenancies before 1 March 2026, yes (private landlords). For tenancies from 1 March 2026, only small landlords, and during the cycle only for the landlord, spouse/civil partner, parent or child."),
        ("What is a no-fault eviction?", "When a landlord ends a tenancy to sell, move in a family member or change the use, rather than because of anything the tenant did. After a no-fault termination, the landlord can't reset the rent to market rent for the next tenancy."),
        ("Does a notice to leave have to be sent to the RTB?", "Yes. From 1 March 2026 a landlord must send the Notice of Termination to the tenant and the RTB on the same day, or it's invalid."),
        ("Is there a winter eviction ban?", "No. The temporary ban on no-fault evictions between November and March ended on 31 March 2023. Notices can be served at any time of year."),
        ("How much deposit can a landlord ask for?", "At most the equivalent of 1 month's rent as a deposit, and at most 1 month's rent in advance."),
        ("What if my landlord has 4 or more properties?", "For tenancies created from 1 March 2026 they're a large landlord: after 6 months they can only end your tenancy for a breach of your obligations or if the property no longer suits your needs. If they sell, the buyer takes over your tenancy."),
        ("Where can I get free help?", "Threshold (1800 454 454) gives free advice to renters. The RTB handles disputes, rent calculator and registration. Citizens Information explains your rights."),
        ("Is this calculator official?", "No. It's a free, independent tool from Tavion based on the RTB's published rules. For an exact figure use the official RTB Rent Calculator, and for legal advice speak to Threshold or a solicitor."),
    ]
    body = f"""<p class="lead">Answers to common questions about rent increases, Rent Pressure Zones and ending a tenancy in Ireland – for tenants and landlords.</p>
<p class="updated">Checked {CHECKED}</p>
{faq_html(FAQ)}
<div class="cta"><h2>Check your rent</h2><p>See the maximum legal increase and the earliest date it can start.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("faq.html", page("faq.html", "Rent FAQ Ireland 2026 – Rent Increases, RPZs, Evictions & Notice Periods",
                           "Answers about Irish rent increases, Rent Pressure Zones, the 2% cap, market rent resets, notice periods, evictions to sell, deposits and RTB disputes under the 2026 rules.",
                           body, active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Rent Checker", "./"), ("FAQ", None)], h1="Rent and tenancy FAQ",
                           sources=("rtb_rent", "rtb_changes", "ci_rent", "ci_leave", "ha_rpz", "threshold")))

# ---------------------------------------------------------------- og, sitemap, llms
def build_og():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (11, 15, 25)); dr = ImageDraw.Draw(im)
    for i in range(H):
        a = max(0, 1 - i / 520); dr.line([(0, i), (W, i)], fill=(int(11 + 10 * a), int(15 + 60 * a), int(25 + 50 * a)))
    def font(size, bold=True):
        for name in (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()
    dr.rounded_rectangle([70, 70, 430, 116], 23, fill=(15, 118, 110)); dr.text((92, 78), "NEW 2026 RULES", font=font(28), fill=(255, 255, 255))
    dr.text((70, 160), "Is your rent", font=font(92), fill=(241, 245, 249))
    dr.text((70, 262), "increase legal?", font=font(92), fill=(45, 212, 191))
    dr.text((70, 400), "Max rent · notice periods · your rights", font=font(40, False), fill=(148, 163, 184))
    dr.text((70, 452), "For tenants and landlords in Ireland", font=font(40, False), fill=(148, 163, 184))
    dr.text((70, 545), "tavion.ie/rent  ·  free, no sign-up", font=font(32), fill=(56, 189, 248))
    im.save(os.path.join(ROOT, "og.png"), optimize=True)

def update_sitemap(files):
    path = os.path.join(REPO, "sitemap.xml")
    xml = open(path, encoding="utf-8").read()
    xml = re.sub(r"\s*<url><loc>https://tavion\.ie/rent/[^<]*</loc>.*?</url>", "", xml)
    entries = "".join(f'\n  <url><loc>{BASE}{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>' for fn, pr in files)
    xml = xml.replace("\n</urlset>", entries + "\n</urlset>")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

def update_llms():
    path = os.path.join(REPO, "llms.txt")
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"\n- \[Irish Rent Checker\][^\n]*", "", txt)
    txt = re.sub(r"\n## Rent: key facts\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
    app = "\n- [Irish Rent Checker](https://tavion.ie/rent/): maximum legal rent increase (2% or CPI if lower) and earliest date, notice of termination periods and valid reasons under the 1 March 2026 rules; Rent Pressure Zone status by county and town; tenant and landlord guides with RTB sources."
    txt = re.sub(r"(\n- \[Irish Citizenship Calculator\][^\n]*)", lambda m: m.group(1) + app, txt, count=1)
    facts = f"""
## Rent: key facts

- Since 20 June 2025 the whole of Ireland is a Rent Pressure Zone; since 1 March 2026 a national rent control system applies to all private tenancies.
- Rent may rise once every 12 months by at most 2% a year (pro rata) or CPI inflation if lower; 90 days' written notice sent to tenant and RTB the same day. CPI: {CPI['pct']}% ({CPI['month']}).
- Areas first designated on 20 June 2025: first review of an existing tenancy only 24 months after rent was last set.
- New apartments (construction commenced after 10 June 2025): CPI increases, no 2% cap. AHB and cost rental: not covered.
- Tenancies from 1 March 2026: rolling 6-year Tenancy of Minimum Duration; landlords with 4+ tenancies or companies can only terminate for tenant breach or unsuitability; small landlords (1-3) can sell during a cycle only to avoid undue hardship.
- Landlord notice: 90 days (<6 months), 152 (6-12 months), 180 (1-7 years), 196 (7-8 years), 224 (8+ years); 28 days for breach after warning; 7 days for serious anti-social behaviour. Tenant notice: 28/35/42/56/84/112 days.
- Pages: [Rent increase calculator](https://tavion.ie/rent/), [Notice period calculator](https://tavion.ie/rent/notice-period.html), [New rules 2026](https://tavion.ie/rent/new-rules-2026.html), [Rent Pressure Zones](https://tavion.ie/rent/rent-pressure-zones.html), [FAQ](https://tavion.ie/rent/faq.html). Sources: rtb.ie, citizensinformation.ie, housingagency.ie.
"""
    txt = txt.replace("\n## Optional", facts + "\n## Optional", 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)

if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    build_index(); build_notice(); build_rules(); build_places(); build_guides(); build_faq(); build_og()
    files = [("index.html", "0.9"), ("notice-period.html", "0.9"), ("new-rules-2026.html", "0.9"), ("rent-pressure-zones.html", "0.8"),
             ("tenant-rights.html", "0.8"), ("landlord-guide.html", "0.8"), ("faq.html", "0.7")] + \
            [(f"rent-increase-{k}.html", "0.7") for k in COUNTIES] + [(f"rent-increase-{s}.html", "0.6") for s, _, _, _ in TOWNS]
    update_sitemap(files); update_llms()
    print("Built", len(files), "pages in", os.path.normpath(ROOT))
