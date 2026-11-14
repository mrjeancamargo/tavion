"""
Builds the Solar Panel Calculator app (tavion.ie/solar/).
Run from the repo root:   python tools/build_solar.py      (needs Node.js)
Every figure on the generated pages comes from solar/js/solar.js, the same engine the calculator uses.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, eur, lis, table, faq_ld, faq_html, key_facts, node, og_image

ENGINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solar", "js", "solar.js"))
CHECKED = "November 2026"
NODE = r"""
const S = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "c" ? S.calc(x.o) : x.k === "g" ? S.grantFor(x.kWp, x.kWh || 0, x.t || "standard") : x.k === "sc" ? { s: S.systemCost(x.kWp), b: S.batteryCost(x.kWh || 0) } : null);
  process.stdout.write(JSON.stringify({ counties: S.COUNTIES, facing: S.FACING, d: S.DEFAULTS, res: res }));
});
"""
META = node(ENGINE, NODE, [])
COUNTIES = META["counties"]
DEF = META["d"]
def run(q): return node(ENGINE, NODE, q)["res"]
def calc(**o): return run([{"k": "c", "o": o}])[0]
def yrs(p): return "over 25 years" if p is None else f"{p:g} years"
SIZES = [2, 3, 4, 5, 6, 8]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULLM = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
RANKED = sorted(COUNTIES, key=lambda k: -COUNTIES[k][1])
AVG = round(sum(v[1] for v in COUNTIES.values()) / len(COUNTIES))

SRC = {
    "seai_pv": ("SEAI – Solar electricity grant (solar PV)", "https://www.seai.ie/grants/home-energy-grants/individual-grants/solar-electricity-grant"),
    "seai_oss": ("SEAI – National Home Energy Upgrade Scheme (One Stop Shop)", "https://www.seai.ie/grants/home-energy-grants/one-stop-shop"),
    "seai_biz": ("SEAI – Commercial solar PV (Non-Domestic Microgen Grant)", "https://seai.ie/grants/business-grants/commercial-solar-pv"),
    "it_batt": ("Irish Times – €600 grant for solar panel batteries (Sept 2026)", "https://www.irishtimes.com/politics/2026/09/25/grant-of-600-for-solar-panel-batteries-set-to-be-announced-in-budget/"),
    "oct26": ("Solarinfo – SEAI grant changes from 6 October 2026", "https://www.solarinfo.ie/blog/seai-grant-changes-october-2026"),
    "pvgis": ("EU Joint Research Centre – PVGIS solar data", "https://re.jrc.ec.europa.eu/pvg_tools/en/"),
    "esbn": ("ESB Networks – Connect a micro-generator (NC6)", "https://esbnetworks.ie/new-connections/generator-connections/micro-generators"),
    "cru": ("CRU – Microgeneration and the Clean Export Guarantee", "https://cru.ie/consumer-information/microgeneration"),
    "ceg": ("Solarinfo – Export rates by supplier (checked 4 Nov 2026)", "https://www.solarinfo.ie/microgeneration"),
    "rev": ("Revenue – Tax manual 07-01-44: microgeneration exemption", "https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-07/07-01-44.pdf"),
    "b27": ("PwC – Budget 2027 key measures", "https://www.pwc.ie/issues/budget/key-measures.html"),
    "vat": ("DLA Piper – 0% VAT on solar panels for homes from 1 May 2023", "https://dlapiper.com/insights/publications/vat-monthly-alert-series/2023/vat-monthly-alert-april-2023/supply-and-installation-of-solar-panels-for-private-dwellings"),
    "plan": ("gov.ie – Solar planning exemptions", "https://www.gov.ie/en/publication/00203-solar-planning-exemptions"),
    "si493": ("S.I. No. 493 of 2022 – Exempted Development (No. 3) Regulations", "https://www.irishstatutebook.ie/eli/2022/si/493/made/en/pdf"),
    "scis": ("gov.ie – Solar Capital Investment Scheme (TAMS 3)", "https://www.gov.ie/en/service/6ab0f-solar-capital-investment-scheme"),
    "heul": ("Bonkers.ie – Home Energy Upgrade Loan Scheme explained", "https://www.bonkers.ie/guides/personal-finance/what-is-the-home-energy-upgrade-loan-scheme/"),
    "ptsb": ("PTSB – Home Energy Upgrade Loan rates (January 2026)", "https://www.ptsb.ie/about-us/notices/2026/january/ptsb-launches-market-leading-rate-and-reductions-on-sbci-home-energy-upgrade-loans/"),
    "prices": ("Selectra – Electricity prices in Ireland", "https://selectra.ie/energy/guides/electricity-prices-ireland"),
}

TABS = [("./", "Calculator"), ("seai-solar-grant.html", "Grant"), ("how-to-apply.html", "How to apply"), ("battery-grant.html", "Battery"),
        ("selling-electricity.html", "Selling power"), ("by-county.html", "By county"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Solar panel calculator</a><a href="seai-solar-grant.html">SEAI solar grant</a><a href="how-to-apply.html">How to apply</a><a href="claim-grant-payment.html">Claiming the grant</a>'
        '<a href="battery-grant.html">Battery grant</a><a href="one-stop-shop.html">One Stop Shop</a><a href="free-solar-panels.html">Free and higher grants</a><a href="selling-electricity.html">Selling electricity</a>'
        '<a href="solar-income-tax.html">Tax on solar income</a><a href="solar-panel-cost.html">Cost</a><a href="are-solar-panels-worth-it.html">Is it worth it?</a><a href="by-county.html">By county</a>'
        '<a href="system-sizes.html">System sizes</a><a href="roof-direction.html">Roof direction</a><a href="solar-in-winter.html">Solar in winter</a><a href="planning-permission.html">Planning</a>'
        '<a href="choosing-an-installer.html">Choosing an installer</a><a href="home-energy-upgrade-loan.html">Loans</a><a href="farm-solar-grant.html">Farm grant</a><a href="business-solar-grant.html">Business grant</a><a href="faq.html">FAQ</a>')
app = App("solar", "Solar Panel Calculator", "☀️", None, "#b45309", TABS, FOOT, SRC, None,
          "Thinking about solar panels? This free calculator shows your payback, the SEAI grant and what you'd save:", "Know someone pricing solar panels? Send them this before they sign.", "solar",
          f"Grant rules checked against SEAI in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>, not affiliated with SEAI, ESB Networks or any installer. Savings are estimates, not guarantees – always get quotes from SEAI-registered companies.")
CROSS = ["mortgage", "stamp", "salary", "taxrefund"]
STD = dict(bill2m=250, home="mixed")


# ---------- static SVG charts for content pages ----------
def payback_svg(series, payback, alt=None, label=""):
    W, H, L, R, T, B = 480, 250, 62, 12, 24, 34
    n = len(series) - 1
    vals = series + (alt or [])
    lo, hi = min(0, min(vals)), max(0, max(vals))
    raw = (hi - lo) / 5 or 1
    p = 10 ** len(str(int(raw))) / 10
    step = next(m * p for m in (1, 2, 2.5, 5, 10) if raw <= m * p)
    lo, hi = (lo // step) * step, -((-hi) // step) * step
    x = lambda i: L + (W - L - R) * i / n
    y = lambda v: T + (H - T - B) * (hi - v) / (hi - lo)
    def short(v):
        a = abs(v)
        return ("−" if v < 0 else "") + "€" + (f"{a / 1000:g}k" if a >= 1000 else f"{a:g}")
    g, v = "", lo
    while v <= hi + 1:
        g += f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="{"zero" if v == 0 else "grid"}"/><text x="{L - 8}" y="{y(v) + 4:.1f}" class="ax" text-anchor="end">{short(v)}</text>'
        v += step
    for i in range(0, n + 1, 10):
        g += f'<text x="{x(i):.1f}" y="{H - 12}" class="ax" text-anchor="middle">{"Now" if i == 0 else "Yr " + str(i)}</text>'
    path = lambda s: " ".join(("L" if i else "M") + f"{x(i):.1f} {y(val):.1f}" for i, val in enumerate(s))
    line = path(series)
    area = f"{line} L{x(n):.1f} {y(0):.1f} L{x(0):.1f} {y(0):.1f} Z"
    cid = "c" + str(abs(hash(label)) % 100000)
    svg = (f'<svg viewBox="0 0 {W} {H}" class="chart static" role="img" aria-label="Payback chart {label}"><defs><clipPath id="{cid}u"><rect x="0" y="0" width="{W}" height="{y(0):.1f}"/></clipPath>'
           f'<clipPath id="{cid}d"><rect x="0" y="{y(0):.1f}" width="{W}" height="{H}"/></clipPath></defs>{g}'
           f'<path d="{area}" class="a-up" clip-path="url(#{cid}u)"/><path d="{area}" class="a-down" clip-path="url(#{cid}d)"/>')
    if alt: svg += f'<path d="{path(alt)}" class="l-alt"/>'
    svg += f'<path d="{line}" class="l-main"/>'
    if payback and payback <= n:
        px = x(payback)
        svg += (f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{T}" y2="{y(0):.1f}" class="pb"/><circle cx="{px:.1f}" cy="{y(0):.1f}" r="6" class="pb-dot"/>'
                f'<text x="{min(px + 8, W - 190):.1f}" y="{T + 14}" class="pb-t">Paid back: {payback:g} years</text>')
    return svg + "</svg>"

def month_svg(monthly, use=None):
    W, H, L, B = 480, 210, 4, 28
    mx = max(monthly + ([use] if use else [])) * 1.12
    bw = (W - 2 * L) / 12
    s = f'<svg viewBox="0 0 {W} {H}" class="chart bars static" role="img" aria-label="Solar generation by month">'
    for i, m in enumerate(monthly):
        h = (H - B - 10) * m / mx
        xx = L + i * bw + bw * 0.15
        s += f'<rect x="{xx:.1f}" y="{H - B - h:.1f}" width="{bw * 0.7:.1f}" height="{h:.1f}" rx="4" class="bar"><title>{FULLM[i]}: {m} kWh</title></rect>'
        s += f'<text x="{xx + bw * 0.35:.1f}" y="{H - 8}" class="ax" text-anchor="middle">{MONTHS[i][0]}</text><text x="{xx + bw * 0.35:.1f}" y="{H - B - h - 5:.1f}" class="ax" text-anchor="middle" style="font-size:13px">{m}</text>'
    if use:
        uy = H - B - (H - B - 10) * use / mx
        s += f'<line x1="{L}" x2="{W - L}" y1="{uy:.1f}" y2="{uy:.1f}" class="use"/>'
    s += "</svg>"
    if use:
        s += f'<p class="small muted" style="margin:2px 0 0">Dashed line: a typical home uses about {use} kWh a month.</p>'
    return s

def chart_card(title, svg, note="", legend=None):
    lg = ""
    if legend:
        lg = '<ul class="legend">' + "".join(f'<li><i class="{c}"></i>{t}</li>' for c, t in legend) + "</ul>"
    return f'<div class="card"><div class="tl">{title}</div>{svg}{lg}{("<p class=" + chr(34) + "small muted" + chr(34) + " style=" + chr(34) + "margin:4px 0 0" + chr(34) + ">" + note + "</p>") if note else ""}</div>'


def county_options(sel="dublin"):
    return "".join(f'<option value="{k}"{" selected" if k == sel else ""}>{COUNTIES[k][0]}</option>' for k in sorted(COUNTIES))

GRANT_ROWS = []
for k in (1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6):
    g = run([{"k": "g", "kWp": k}])[0]
    GRANT_ROWS.append([f"{k:g} kWp", eur(g["solar"]), eur(g["solar"] + 600)])

# ---------- Calculator ----------
def build_index():
    ex = calc(county="dublin", **STD)
    exb = calc(county="dublin", battKWh=5, **STD)
    body = f"""<p class="lead">Are solar panels worth it for your home? Pick your county, enter your electricity bill and see your payback, the SEAI grant and what you'd save every year. Free, no sign-up.</p>
<ul class="facts"><li>SEAI grant up to €1,800</li><li>+ €600 battery grant</li><li>0% VAT</li><li>Paid ~18.5c for power you sell</li></ul>
<form id="solarForm" class="card" novalidate>
  <label for="county" class="big-label">Your county</label>
  <select id="county">{county_options()}</select>
  <label for="bill" class="big-label" style="margin-top:14px">Your electricity bill every 2 months</label>
  <div class="money"><span>€</span><input id="bill" type="text" inputmode="decimal" autocomplete="off" placeholder="250" value="250"></div>
  <label for="facing" style="margin-top:14px">Which way does your roof face?</label>
  <select id="facing"><option value="s">South</option><option value="sw">South-east or south-west</option><option value="ew">East or west</option><option value="nw">North-east or north-west</option><option value="n">North</option></select>
  <fieldset style="margin-top:14px"><legend class="sm">Add a battery?</legend><div class="seg three-seg">
    <label><input type="radio" name="battery" value="0" checked><span>No</span></label>
    <label><input type="radio" name="battery" value="5"><span>5 kWh<small>€600 grant</small></span></label>
    <label><input type="radio" name="battery" value="10"><span>10 kWh<small>€600 grant</small></span></label>
  </div></fieldset>
  <fieldset style="margin-top:14px"><legend class="sm">Is someone home during the day?</legend><div class="seg three-seg">
    <label><input type="radio" name="home" value="out"><span>Rarely<small>out all day</small></span></label>
    <label><input type="radio" name="home" value="mixed" checked><span>Some days</span></label>
    <label><input type="radio" name="home" value="home"><span>Most days<small>or WFH</small></span></label>
  </div></fieldset>
  <label for="size" style="margin-top:14px">System size</label>
  <select id="size"><option value="">Recommended for my bill</option>{"".join(f'<option value="{k}">{k} kWp (about {-(-k * 1000 // DEF["panelW"])} panels)</option>' for k in (2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 10))}</select>
  <details id="adv" class="adv"><summary>Advanced options <span class="muted small">– your own quote, prices, roof angle, shading, loan…</span></summary><div class="adv-body">
    <div class="two">
      <label>Yearly use (kWh)<input id="usage" type="number" min="500" max="30000" step="100" placeholder="from your bill"></label>
      <label>Extra use – EV or heat pump (kWh)<input id="extraKWh" type="number" min="0" max="20000" step="100" placeholder="0"></label>
      <label>Price you pay (c/kWh)<input id="unitRate" type="number" step="0.1" min="5" max="80" placeholder="{DEF['unitRate'] * 100:g}"></label>
      <label>Export rate (c/kWh)<input id="exportRate" type="number" step="0.1" min="0" max="50" placeholder="{DEF['exportRate'] * 100:g}"></label>
      <label>Your quote for the panels (€)<input id="cost" type="number" step="50" min="0" placeholder="typical price"></label>
      <label>Battery quote (€)<input id="battCost" type="number" step="50" min="0" placeholder="typical price"></label>
      <label>Battery size (kWh)<input id="battSize" type="number" step="0.5" min="0" max="30" placeholder="as picked above"></label>
      <label>Roof angle<select id="tilt"><option value="standard">Standard pitch (30–40°)</option><option value="shallow">Shallow (about 15°)</option><option value="steep">Steep (about 50°)</option><option value="flat">Flat roof</option></select></label>
      <label>Shading<select id="shading"><option value="0">None</option><option value="5">A little (5%)</option><option value="10">Some (10%)</option><option value="20">A lot (20%)</option></select></label>
      <label>Price rise (% a year)<input id="priceRise" type="number" step="0.5" min="-5" max="15" placeholder="{DEF['priceRise']:g}"></label>
      <label>Inverter replacement, year 12 (€)<input id="inverterCost" type="number" step="50" min="0" placeholder="{DEF['inverterCost']}"></label>
    </div>
    <fieldset style="margin-top:14px"><legend class="sm">Grant</legend>
      <label class="radio"><input type="radio" name="grant" value="standard" checked><span>Standard SEAI grant<small>Up to €1,800 + €600 battery. Home built and occupied before 2025.</small></span></label>
      <label class="radio"><input type="radio" name="grant" value="welfare"><span>Enhanced grant – qualifying welfare payment<small>Up to €8,400 + €600 battery (up to 4 kWp).</small></span></label>
      <label class="radio"><input type="radio" name="grant" value="none"><span>No grant<small>New home (2025+), already had a solar grant, or you skip it.</small></span></label>
    </fieldset>
    <label class="check"><input type="checkbox" id="loan"><span>Paying with a loan</span></label>
    <div id="loanBox" class="two" hidden>
      <label>Interest rate (%)<input id="loanRate" type="number" step="0.05" min="0" max="20" placeholder="3.5"></label>
      <label>Years<input id="loanYears" type="number" step="1" min="1" max="15" placeholder="7"></label>
    </div>
    <button type="button" class="btn small-btn" id="resetAdv">Reset advanced options</button>
  </div></details>
  <div class="btn-row"><button type="submit" class="btn primary">Show my payback</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your device. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>Solar panels in Ireland: the short version</h2>
<div class="card"><ol class="steps">
<li><strong>A typical home</strong> with a €250 bill every 2 months suits a {ex['kWp']:g} kWp system ({ex['panels']} panels). In Dublin it makes about {ex['gen']:,} kWh a year and pays back in about <strong>{yrs(ex['payback'])}</strong>.</li>
<li><strong>The SEAI grant</strong> is €700 per kWp for the first 2 kWp and €200 per kWp up to 4 kWp – <strong>€1,800</strong> max. Since October 2026 there's also <strong>€600</strong> for a battery of 5 kWh or more. <a href="seai-solar-grant.html">Grant details →</a></li>
<li><strong>Apply before any work starts.</strong> Then you have 8 months to install, get a BER and submit the paperwork. <a href="how-to-apply.html">Step by step →</a></li>
<li><strong>You're paid for what you don't use</strong> – about 15–19.5c per kWh under the Clean Export Guarantee, and up to €400 a year is tax-free (€600 from 2027). <a href="selling-electricity.html">Export rates →</a></li>
<li><strong>A battery</strong> lets you use more of your own power, but with the €600 grant a 5 kWh battery takes this example from {yrs(ex['payback'])} to {yrs(exb['payback'])}. <a href="battery-grant.html">Is a battery worth it? →</a></li>
</ol></div>
<h2>Payback by county (4 kWp, no battery)</h2>
{table(["County", "kWh per kWp", "Saved in year 1", "Payback"], [[f'<a href="solar-panels-{k}.html">{COUNTIES[k][0]}</a>', str(COUNTIES[k][1]), eur(r['saving1']), yrs(r['payback'])] for k, r in zip(RANKED[:8], run([{"k": "c", "o": dict(county=k, kWp=4, **STD)} for k in RANKED[:8]]))])}
<p><a href="by-county.html">All 26 counties →</a></p>
<div class="cta"><h2>Getting quotes?</h2><p>What to ask, red flags, and how to check a company is SEAI-registered.</p><a class="btn" href="choosing-an-installer.html">Choosing an installer</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Solar Panel Calculator Ireland", "url": app.BASE, "applicationCategory": "UtilitiesApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Calculate solar panel payback, SEAI grant, savings and export income for any Irish county, with or without a battery."}
    faqs = [("How long do solar panels take to pay back in Ireland?", f"For a typical home with a 4 kWp system and the €1,800 SEAI grant, about {yrs(ex['payback'])} in Dublin. It ranges from about 5 to 8 years depending on your county, roof and how much power you use in the day."),
            ("How much is the SEAI solar grant?", "€700 per kWp for the first 2 kWp and €200 per kWp for the next 2 kWp, up to €1,800 for 4 kWp or more. A battery of 5 kWh or more gets a further €600, so up to €2,400 in total.")]
    app.page("index.html", "Solar Panel Calculator Ireland 2026 – Payback, SEAI Grant & Savings by County",
             "Free solar panel calculator for Ireland: payback years, SEAI grant (€1,800 + €600 battery), yearly savings and export income for your county, with a 25-year payback graph.",
             body, active="Calculator", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["js/solar.js", "js/calc.js"], h1="Solar panel calculator",
             sources=("seai_pv", "pvgis", "ceg", "prices"), cross=CROSS, priority="0.9",
             share_text="Thinking about solar panels? This free calculator shows the payback, SEAI grant and savings for your county:")


# ---------- Grants ----------
def build_grants():
    body = f"""<p class="lead">How much is the SEAI solar panel grant, who gets it, and what changed in October 2026.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["<strong>€700 per kWp</strong> for the first 2 kWp, then <strong>€200 per kWp</strong> up to 4 kWp. Maximum <strong>€1,800</strong>.",
            "<strong>New:</strong> a flat <strong>€600 battery grant</strong> for a battery of 5 kWh or more – up to <strong>€2,400</strong> with panels.",
            "<strong>Who:</strong> homeowners, private landlords, owner management companies and approved housing bodies. The home needs an MPRN and must be <strong>built and occupied before 2025</strong> (it was before 2021 until 6 October 2026).",
            "<strong>One grant per home:</strong> you can't get it if solar PV was already grant-funded at that MPRN.",
            "<strong>Apply first:</strong> you must have your grant offer before any work starts. You then have <strong>8 months</strong> to finish and submit the paperwork.",
            "The grant is <strong>paid pro rata</strong> – e.g. €1,500 for 2.5 kWp. You get the rate in force on the day you apply."])}
<h2>Grant by system size</h2>
{table(["System", "Solar grant", "With a 5 kWh+ battery"], GRANT_ROWS)}
<p class="muted small">The grant stops growing at 4 kWp, but bigger systems can still be worth it if you use a lot of power (EV, heat pump).</p>
<h2>Higher grants</h2>
{lis(["<strong>Qualifying welfare payment</strong> (Fuel Allowance, Working Family Payment, One-Parent Family Payment, Domiciliary Care Allowance and some others): up to <strong>€8,400</strong> for panels and <strong>€9,000</strong> with a battery. <a href='free-solar-panels.html'>Who qualifies →</a>",
      "<strong>Warmer Homes Scheme</strong> and <strong>medically vulnerable</strong> households: solar up to 4 kWp plus a 5 kWh battery, fully funded.",
      "<strong>Dublin RAS tenancies</strong> (pilot): landlords can get up to €9,000 for solar and battery."])}
<div class="ad" data-slot="content"></div>
<h2>What changed in 2026</h2>
{lis(["The grant stayed at <strong>€1,800</strong> for 2026 – a planned cut to €1,500 didn't go ahead.",
      "From <strong>6 October 2026</strong>: homes built before 2025 qualify (was before 2021), the €600 battery grant started, and fully-funded solar + battery was added for Warmer Homes.",
      "Grant levels for 2027 haven't been announced as a cut – but SEAI can change rates, and you get the amount in force <strong>when you apply</strong>. An approved offer locks it in for 8 months."])}
<h2>Individual grant or One Stop Shop?</h2>
<p>Doing just solar? Apply yourself (the <strong>individual grant</strong>) – it's simpler. Doing a full retrofit to a B2 BER (insulation, heat pump and solar)? A <a href="one-stop-shop.html">One Stop Shop</a> takes the grants off the price up front and manages it all.</p>
<div class="cta"><h2>How much would you get?</h2><p>Your grant, cost and payback for your county.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("How much is the solar panel grant in Ireland?", "Up to €1,800 for solar panels (€700 per kWp for 2 kWp, then €200 per kWp up to 4 kWp), plus €600 for a battery of 5 kWh or more."),
            ("Is my house too new for the solar grant?", "Homes built and occupied before 2025 qualify since 6 October 2026. Homes built in 2025 or later don't."),
            ("Can I get the grant if I already have solar panels?", "Not for panels – one solar PV grant per MPRN. You can apply for the €600 battery grant for a battery added to an existing system.")]
    app.page("seai-solar-grant.html", "SEAI Solar Panel Grant 2026 – €1,800 + €600 Battery Grant, Who Qualifies",
             "SEAI solar PV grant 2026: €700/kWp up to 2 kWp, €200/kWp to 4 kWp, max €1,800, plus a new €600 battery grant. Homes built before 2025 now qualify. Amounts by size.",
             body, active="Grant", jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("SEAI solar grant", None)], h1="SEAI solar panel grant 2026",
             sources=("seai_pv", "oct26", "it_batt"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">How to get the SEAI solar panel grant, in the right order. Get one step wrong – like starting work before your offer – and you lose the grant.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
<div class="card"><ol class="steps">
<li><strong>Get 3 quotes from SEAI-registered solar PV companies.</strong> Only registered companies qualify. Ask how much the system will make a year, the total price, warranties and whether your roof suits solar. <a href="choosing-an-installer.html">What to ask →</a></li>
<li><strong>Apply online to SEAI</strong> (it takes about 10 minutes). You need your MPRN (on your electricity bill), the company you picked and the system size. Your <strong>Letter of Offer</strong> comes by email.</li>
<li><strong>Check the offer before work starts.</strong> The grant is only paid for the size, company and amount in the letter. To change anything, email SEAI <strong>before</strong> works begin.</li>
<li><strong>Your installer tells ESB Networks</strong> (the NC6 form). This takes at least 4 weeks (20 working days), so it's done before the install.</li>
<li><strong>The installation.</strong> Usually 1–2 days. Keep the safety file your installer gives you.</li>
<li><strong>Book a post-works BER.</strong> Every applicant needs one, done by an SEAI-registered BER assessor. Book it as soon as you have an install date.</li>
<li><strong>Your installer uploads the paperwork</strong> and SEAI pays the grant – usually within 4–6 weeks. <a href="claim-grant-payment.html">The claim, in detail →</a></li>
</ol></div>
<div class="callout warn"><strong>The 3 mistakes that cost people the grant:</strong> starting work before the offer, the BER not being published, and going over the 8 months.</div>
<div class="ad" data-slot="content"></div>
<h2>What you need to apply</h2>
{lis(["Your <strong>MPRN</strong> – the 11-digit number on your electricity bill", "Your PPS number and contact details", "The name of your SEAI-registered solar company", "The system size (kWp) and whether you're adding a battery",
      "Your bank details (yours or the solar company's) for the payment"])}
<h2>Panels and battery together</h2>
<p>Doing both? Apply once – there's no need for two applications. Already applied for panels? Make a new application for the battery; you don't change the first one. You can't apply for anything already installed.</p>
<h2>Owner management companies (apartments)</h2>
<p>The OMC or its property management agent applies, with written authorisation from the OMC. Contact SEAI (solarpv@seai.ie or 01 808 2100) for the forms.</p>
<div class="cta"><h2>See your grant</h2><p>Grant, cost and payback for your home.</p><a class="btn" href="./">Open the calculator</a></div>"""
    howto = {"@context": "https://schema.org", "@type": "HowTo", "name": "How to apply for the SEAI solar panel grant", "totalTime": "P2M",
             "step": [{"@type": "HowToStep", "position": i + 1, "name": s} for i, s in enumerate(["Get quotes from SEAI-registered companies", "Apply online to SEAI and get your Letter of Offer",
                      "Check the offer before work starts", "Installer submits the NC6 form to ESB Networks", "Install the panels", "Get a post-works BER", "Installer uploads documents; SEAI pays the grant"])]}
    app.page("how-to-apply.html", "How to Apply for the SEAI Solar Grant – Step by Step (2026)",
             "Apply for the SEAI solar panel grant in 7 steps: quotes, online application, Letter of Offer, NC6, installation, post-works BER and payment. Mistakes that cost you the grant.",
             body, active="How to apply", jsonld=[howto], crumbs=[("Solar", "./"), ("How to apply", None)], h1="How to apply for the solar panel grant",
             sources=("seai_pv", "esbn"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">Panels are on the roof – now how do you get your money? What SEAI needs, who sends it and how long it takes.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["You don't fill in a claim form yourself: your <strong>solar company uploads the documents</strong> to SEAI.",
            "Your <strong>post-works BER</strong> must be <strong>published</strong> on the National BER Register before SEAI pays.",
            "SEAI pays into your bank account (or the company's) usually <strong>4–6 weeks</strong> after it has everything.",
            "It all has to be done within <strong>8 months</strong> of your grant offer, or the offer expires."])}
<h2>The documents SEAI needs</h2>
<ul class="todo">
<li>Declaration of Works – signed by the installer</li><li>Inspection, Test and Commissioning Certificate</li><li>Safe Electric (RECI) certificate</li>
<li>ESB Networks NC6 form</li><li>Post-works BER – published by your BER assessor</li><li>Invoice describing the work</li><li>Photos of the installation (listed on the Declaration of Works)</li></ul>
<div class="ad" data-slot="content"></div>
<h2>Why grant payments get delayed</h2>
{lis(["<strong>The BER isn't published yet.</strong> Book the assessor for right after the install and ask them to publish it straight away.",
      "<strong>Missing documents.</strong> Ask your company to upload everything within 1–3 days of the install, and check in your SEAI portal.",
      "<strong>Wrong bank details.</strong> Check them in the portal – they must be yours (the applicant) or the solar company's.",
      "<strong>The job doesn't match the offer</strong> – a bigger system or a different company, without SEAI's approval first.",
      "<strong>An inspection.</strong> SEAI inspects some homes. If rework is needed, payment follows about 2 weeks after it's done."])}
<h2>Check where your claim is</h2>
<p>Log in to the SEAI online portal to see the status of your request for payment. Questions: <strong>01 808 2100</strong> or <strong>solarpv@seai.ie</strong>. Technical questions: 01 277 6977.</p>
<h2>Keep these for later</h2>
<p>Keep all invoices, receipts and certificates. SEAI can inspect your home in future, and you'll need them for your BER and when you sell the house.</p>
<div class="cta"><h2>Haven't applied yet?</h2><p>Do it in the right order.</p><a class="btn" href="how-to-apply.html">How to apply</a></div>"""
    faqs = [("How long does the SEAI solar grant take to be paid?", "Usually 4 to 6 weeks after your solar company uploads all the documents and your post-works BER is published."),
            ("Do I need a BER for the solar grant?", "Yes. Every applicant needs a post-works BER by an SEAI-registered assessor, and it must be published before the grant is paid.")]
    app.page("claim-grant-payment.html", "How to Claim the SEAI Solar Grant Payment – Documents, BER & Delays",
             "Getting your SEAI solar grant paid: the documents your installer uploads, the post-works BER, the 8-month deadline, 4–6 week payment and why payments get delayed.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Claiming the grant", None)], h1="Claiming your solar grant payment", sources=("seai_pv",), cross=CROSS, priority="0.8")

    ex = run([{"k": "c", "o": dict(county="dublin", kWp=4, battKWh=b, home=h, bill2m=250)} for b in (0, 5, 10) for h in ("out", "mixed", "home")])
    rows = [[f"{b} kWh" if b else "No battery", lab] + [f"{r['selfUse']}%", eur(r['net']), eur(r['saving1']), yrs(r['payback'])] for (b, lab), r in zip([(b, l) for b in (0, 5, 10) for l in ("Rarely home", "Some days", "Most days")], ex)]
    a, b = ex[1], ex[4]
    body = f"""<p class="lead">SEAI now gives €600 towards a home battery. Is it worth adding one to your solar panels?</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["Flat <strong>€600 grant</strong> for a battery of <strong>5 kWh or more</strong>. Smaller batteries get nothing.",
            "Available since <strong>6 October 2026</strong>, for homes built and occupied before 2025.",
            "Apply with your panels in <strong>one application</strong>, or on its own for a battery added to <strong>existing panels</strong>.",
            "Must be fitted by an <strong>SEAI-registered solar PV company</strong>, with the grant offer in place before work starts.",
            f"A battery stores power you'd otherwise sell for ~{DEF['exportRate'] * 100:g}c and uses it in the evening instead of buying at ~{DEF['unitRate'] * 100:g}c."])}
{chart_card("Dublin, 4 kWp, €250 bill: with and without a 5 kWh battery", payback_svg(b["series"], b["payback"], a["series"], "battery"), f"Without a battery: {yrs(a['payback'])}. With a 5 kWh battery (€{b['battCost']:,} less €600): {yrs(b['payback'])}.", [("c-net", "With 5 kWh battery"), ("c-alt", "Without battery")])}
<h2>Battery or not: Dublin, 4 kWp</h2>
{table(["Battery", "Home in the day", "Own power used", "You pay", "Year 1 saving", "Payback"], rows)}
<div class="ad" data-slot="content"></div>
<h2>A battery makes most sense if…</h2>
{lis(["You're <strong>out during the day</strong> – without a battery you'd sell most of your power cheaply", "You have a <strong>big system</strong> (5 kWp+) or lots of summer surplus",
      "You're on a <strong>night-rate or EV tariff</strong> – in winter you can charge the battery cheaply at night (not counted in our numbers)", "You want some backup power (needs a backup-capable inverter – ask)"])}
<h2>…and less sense if</h2>
{lis(["You're home all day and already use most of your solar", "Your system is small (2–3 kWp)", "Your quote is well over €3,000 for 5 kWh"])}
<div class="cta"><h2>Your own numbers</h2><p>Try your bill with and without a battery.</p><a class="btn" href="./?battery=5">Open the calculator</a></div>"""
    faqs = [("Is there a grant for solar batteries in Ireland?", "Yes. Since 6 October 2026 SEAI gives a flat €600 for a home battery of 5 kWh or more, fitted by an SEAI-registered solar company."),
            ("Can I get the battery grant if I already have solar panels?", "Yes. You can apply for the €600 battery grant on its own for a battery added to an existing solar PV system, as long as the work hasn't started.")]
    app.page("battery-grant.html", "SEAI Solar Battery Grant €600 – Is a Home Battery Worth It? (2026)",
             "SEAI's new €600 grant for a 5 kWh+ home battery: who qualifies, how to apply with or after your panels, and payback with and without a battery.",
             body, active="Battery", jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Battery grant", None)], h1="Solar battery grant (€600)", sources=("seai_pv", "it_batt", "oct26"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">The One Stop Shop route – the National Home Energy Upgrade Scheme – manages a whole-home upgrade, solar included, and takes the grants off your bill up front.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["A <strong>One Stop Shop</strong> is an SEAI-registered company that does everything: home energy assessment, grant application, contractors, project management and the final BER.",
            "The grants are <strong>deducted from your price up front</strong> – you don't wait for SEAI to pay you.",
            "It's for a <strong>complete upgrade</strong>: the home must reach at least a <strong>B2 BER</strong>. Homes need to be built and occupied <strong>before 2011</strong> with a BER of B3 or lower.",
            "Solar PV gets the same grant as on its own: <strong>up to €1,800</strong>. The bigger money is for insulation and heat pumps.",
            "Low-cost finance is available – see the <a href='home-energy-upgrade-loan.html'>Home Energy Upgrade Loan</a>."])}
<h2>One Stop Shop or individual grant?</h2>
{table(["", "Individual solar grant", "One Stop Shop"], [["What's covered", "Solar panels (+ battery)", "Whole home: insulation, windows, heat pump, solar"],
       ["Who applies", "You, online", "The One Stop Shop"], ["Grant paid", "To you after the work", "Off the price up front"], ["BER target", "None (post-works BER needed)", "At least B2"],
       ["Home age", "Built before 2025", "Built before 2011"], ["Best for", "Just adding solar", "A deep retrofit, all at once"]])}
<div class="ad" data-slot="content"></div>
<h2>How the One Stop Shop process works</h2>
<div class="card"><ol class="steps">
<li><strong>Find a One Stop Shop</strong> on SEAI's list and ask for a home energy assessment.</li>
<li><strong>Get a plan and quote</strong> showing the works, the BER you'll reach and the grants deducted.</li>
<li><strong>The One Stop Shop applies</strong> for the grants on your behalf.</li>
<li><strong>The works are done</strong>, usually by several trades it manages.</li>
<li><strong>A final BER</strong> confirms you've reached B2 or better, and you pay the balance.</li></ol></div>
<h2>Is it worth it just for solar?</h2>
<p>Usually not – for panels only, the <a href="how-to-apply.html">individual grant</a> is quicker and the grant is the same. The One Stop Shop pays off when you're also doing insulation or a heat pump, because you don't have to fund all the grants and wait to be repaid.</p>
<div class="cta"><h2>Just thinking about solar?</h2><p>See the payback first.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("one-stop-shop.html", "SEAI One Stop Shop Solar Panels – National Home Energy Upgrade Scheme Explained",
             "Getting solar panels through an SEAI One Stop Shop: grants deducted up front, B2 BER target, homes built before 2011, and when the individual €1,800 grant is better.",
             body, crumbs=[("Solar", "./"), ("One Stop Shop", None)], h1="One Stop Shop: solar as part of a home upgrade", sources=("seai_oss", "seai_pv"), cross=CROSS, priority="0.8")

    ex = calc(county="dublin", kWp=4, grant="welfare", **STD)
    body = f"""<p class="lead">Some households can get solar panels and a battery fully paid, or a grant of up to €9,000. Here's who qualifies.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["<strong>Enhanced solar grant:</strong> €3,350 per kWp for the first 2 kWp, then €850 per kWp up to 4 kWp – up to <strong>€8,400</strong>, or <strong>€9,000 with a 5 kWh battery</strong>.",
            "For homeowners who live in the home and get a <strong>qualifying Department of Social Protection payment</strong>. SEAI checks this with the DSP directly.",
            "<strong>Warmer Homes Scheme:</strong> solar up to 4 kWp and a 5 kWh battery are now offered as standard, <strong>fully funded</strong>.",
            "<strong>Medically vulnerable:</strong> the fully-funded scheme now covers up to 4 kWp plus a 5 kWh battery.",
            f"On the enhanced grant a 4 kWp system in Dublin costs you about <strong>{eur(ex['net'])}</strong> and pays back in about <strong>{yrs(ex['payback'])}</strong>."])}
<h2>Qualifying payments</h2>
{lis(["Fuel Allowance (National Fuel Scheme)", "Working Family Payment", "One-Parent Family Payment", "Domiciliary Care Allowance",
      "Jobseeker's Allowance – for over 6 months with a child under 7 (send the child's birth certificate)", "Disability Allowance – for over 6 months with a child under 7 (send the child's birth certificate)",
      "Carer's Allowance – living with the person you care for (send the Carer's Allowance Confirmation Form)"])}
<p class="muted small">In most cases the homeowner must get the payment – the exception is Carer's Allowance. If your payment only just started, wait 5–6 weeks after the first one before applying.</p>
<div class="ad" data-slot="content"></div>
<h2>Enhanced grant by size</h2>
{table(["System", "Enhanced grant", "With a battery"], [[f"{k:g} kWp", eur(g['solar']), eur(g['solar'] + 600)] for k, g in zip((2, 2.5, 3, 4), run([{"k": "g", "kWp": k, "t": "welfare"} for k in (2, 2.5, 3, 4)]))])}
<h2>Renters</h2>
<p>Renters can't apply themselves, but <strong>landlords can</strong> – private landlords qualify for the standard grant. In Dublin, landlords with a long-term tenant on the <strong>Rental Accommodation Scheme</strong> (Dublin City, DLR, Fingal or South Dublin councils) can get <strong>up to €9,000</strong> in a pilot – contact the council first for a letter confirming it.</p>
<p>See what you'd get on other payments: <a href="../welfare/fuel-allowance.html" data-track="cross_app" data-label="welfare_from_solar">Fuel Allowance</a> · <a href="../welfare/working-family-payment.html" data-track="cross_app" data-label="welfare_from_solar">Working Family Payment</a></p>
<div class="cta"><h2>See your payback</h2><p>Pick “Enhanced grant” in the advanced options.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("Can I get free solar panels in Ireland?", "Yes, if you qualify for the Warmer Homes Scheme or the scheme for the medically vulnerable: solar up to 4 kWp and a 5 kWh battery are fully funded. Homeowners on a qualifying welfare payment can get up to €9,000."),
            ("Who gets the €9,000 solar grant?", "Homeowners living in the home who get a qualifying payment such as Fuel Allowance, Working Family Payment or One-Parent Family Payment: up to €8,400 for panels plus €600 for a battery.")]
    app.page("free-solar-panels.html", "Free Solar Panels Ireland 2026 – €9,000 Grant for Welfare Recipients & Warmer Homes",
             "Who gets free or near-free solar in Ireland: the enhanced €8,400 + €600 battery grant for welfare recipients, fully-funded Warmer Homes solar, medically vulnerable and Dublin RAS landlords.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Free and higher grants", None)], h1="Free solar panels and higher grants", sources=("seai_pv", "oct26"), cross=["welfare", "salary", "rent", "taxrefund"], priority="0.9")


# ---------- Selling power + tax ----------
SUPPLIERS = [("SSE Airtricity", "19.50", "Quarterly bill credit"), ("Electric Ireland", "19.50", "Each bill"), ("Pinergy", "18.50", "Monthly bill credit"), ("Bord Gáis Energy", "18.50", "Quarterly bill credit"),
             ("Energia", "18.50", "Every 2 months"), ("Flogas", "18.50", "Every 2 months"), ("Yuno Energy", "17.16", "Twice a year"), ("PrePayPower", "15.89", "Twice a year"), ("EcoPower", "15.20", "Quarterly")]

def build_export():
    ex = calc(county="dublin", kWp=4, **STD)
    body = f"""<p class="lead">You get paid for the solar power you don't use. How much each supplier pays, how you get set up and how you're paid.</p>
<p class="updated">Rates checked 4 November 2026 · Suppliers can change them at any time</p>
{key_facts(["Under the <strong>Clean Export Guarantee (CEG)</strong> every supplier must pay you for power you export. They set their own rate – about <strong>15c to 19.5c per kWh</strong> in November 2026.",
            "You need a <strong>smart meter</strong> (ESB Networks fits one free) and your installer's <strong>NC6 form</strong> to ESB Networks.",
            "Payment is usually a <strong>credit on your bill</strong>.",
            "Up to <strong>€400 a year is tax-free</strong> (2024–2028), rising to <strong>€600 from 2027</strong> under Budget 2027. <a href='solar-income-tax.html'>Tax rules →</a>",
            f"A 4 kWp system in Dublin exports about {ex['exported']:,} kWh a year – about <strong>{eur(ex['exportIncome'])}</strong> at {DEF['exportRate'] * 100:g}c."])}
<h2>Export rates by supplier (November 2026)</h2>
{table(["Supplier", "c per kWh", "How you're paid", "4 kWp in Dublin / year"], [[n, r + "c", p, eur(ex['exported'] * float(r) / 100)] for n, r, p in SUPPLIERS])}
<p class="muted small">Standard rates, not regulated. Some suppliers offer higher rates on special solar plans, often with a higher unit price – compare the whole plan, not just the export rate. Pinergy cut its rate from 25c to 18.5c on 1 August 2026.</p>
<div class="ad" data-slot="content"></div>
<h2>How to start getting paid</h2>
<div class="card"><ol class="steps">
<li><strong>Your installer submits the NC6</strong> to ESB Networks (systems up to 6 kW single-phase or 11 kW three-phase). Larger systems use the NC7.</li>
<li><strong>ESB Networks fits or sets up a smart meter</strong> that measures exports in 30-minute blocks.</li>
<li><strong>ESB tells your supplier</strong> export metering is live.</li>
<li><strong>Your supplier starts paying</strong> – check your bill shows an export credit. If not after a few months, call them.</li></ol></div>
<h2>Sell or use it yourself?</h2>
<p>Every kWh you use yourself saves about {DEF['unitRate'] * 100:g}c; every kWh you sell earns about {DEF['exportRate'] * 100:g}c. So run the washing machine, dishwasher and immersion when the sun's out, or add a <a href="battery-grant.html">battery</a>.</p>
<div class="cta"><h2>Your export income</h2><p>See it for your county and bill.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("How much do you get paid for solar export in Ireland?", "About 15c to 19.5c per kWh in November 2026. SSE Airtricity and Electric Ireland pay 19.5c; Bord Gáis, Energia, Flogas and Pinergy 18.5c."),
            ("How do I get paid for my solar panels?", "Your installer submits an NC6 form to ESB Networks, you get a smart meter, and your supplier credits your bill for every kWh you export.")]
    app.page("selling-electricity.html", "Selling Solar Electricity to the Grid Ireland 2026 – Export Rates by Supplier",
             "Clean Export Guarantee rates November 2026: SSE and Electric Ireland 19.5c, Bord Gáis, Energia, Flogas, Pinergy 18.5c. How to get set up (NC6, smart meter) and get paid.",
             body, active="Selling power", jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Selling electricity", None)], h1="Selling your solar power to the grid", sources=("ceg", "cru", "esbn"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">Do you pay tax on the money your supplier pays for solar exports? Usually not – here's the limit.</p>
<p class="updated">Revenue · Checked {CHECKED}</p>
{key_facts(["Up to <strong>€400 a year</strong> of microgeneration income is <strong>exempt</strong> from income tax, USC and PRSI for 2024 to 2028.",
            "Budget 2027 raises this to <strong>€600 a year from 2027</strong> (subject to the Finance Act).",
            "It's for <strong>individuals</strong> generating at their <strong>sole or main home</strong>. Rental properties and businesses don't get it.",
            "Under the limit? You <strong>don't need to declare</strong> it on a tax return.",
            "Over the limit? Declare the amount over it – PAYE workers through myAccount (Income Tax Return), self-employed on Form 11."])}
<h2>Will you go over the limit?</h2>
{table(["System (Dublin)", "Exported a year", "Export income", "Tax-free?"], [[f"{k} kWp", f"{r['exported']:,} kWh", eur(r['exportIncome']), "Yes" if r['exportIncome'] <= 400 else ("Yes from 2027" if r['exportIncome'] <= 600 else "Partly")] for k, r in zip((3, 4, 6, 8), run([{"k": "c", "o": dict(county="dublin", kWp=k, **STD)} for k in (3, 4, 6, 8)]))])}
<div class="ad" data-slot="content"></div>
<p>Most homes stay under the limit. Big systems with no battery are the ones that go over – and a battery reduces exports.</p>
<div class="cta"><h2>Owed a tax refund?</h2><p>Rent credit, medical expenses, working from home and more.</p><a class="btn" href="../tax-refund/" data-track="cross_app" data-label="taxrefund_from_solar">Check my refund</a></div>"""
    faqs = [("Do I pay tax on solar panel income in Ireland?", "Not on the first €400 a year (2024–2028), rising to €600 from 2027 under Budget 2027. Income above that is taxed and must be declared."),
            ("Do I need to declare solar export income?", "Only if it's over the tax-free limit. Below it, Revenue says there's no need to put it on a tax return.")]
    app.page("solar-income-tax.html", "Tax on Solar Panel Income Ireland – €400 Tax-Free, €600 from 2027",
             "Solar export income is tax-free up to €400 a year (2024–2028), rising to €600 from 2027 under Budget 2027. Who qualifies and how to declare anything over it.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Tax on solar income", None)], h1="Tax on solar panel income", sources=("rev", "b27"), cross=["taxrefund", "salary", "welfare", "mortgage"], priority="0.8")


# ---------- Cost, worth it, sizes, county ----------
def build_money():
    sc = run([{"k": "sc", "kWp": k, "kWh": 0} for k in SIZES] + [{"k": "sc", "kWp": 0, "kWh": b} for b in (5, 10)])
    gr = run([{"k": "g", "kWp": k} for k in SIZES])
    body = f"""<p class="lead">How much do solar panels cost in Ireland in 2026, before and after the grant?</p>
<p class="updated">Typical installed prices · {CHECKED}</p>
{key_facts(["A typical <strong>4 kWp</strong> system costs about <strong>{eur(sc[2]['s'])}</strong> installed, or <strong>{eur(sc[2]['s'] - 1800)}</strong> after the €1,800 grant.",
            "There's <strong>0% VAT</strong> on supplying and fitting solar panels on homes since 1 May 2023 – as long as one company supplies and installs them.",
            f"A <strong>5 kWh battery</strong> adds about {eur(sc[6]['b'])} ({eur(sc[6]['b'] - 600)} after the €600 grant).",
            "Quotes vary a lot – get at least 3 from SEAI-registered companies."])}
<h2>Cost by system size</h2>
{table(["System", "Panels", "Typical price", "SEAI grant", "You pay"], [[f'<a href="{k}kwp-solar-system.html">{k} kWp</a>', str(-(-k * 1000 // DEF['panelW'])), eur(s['s']), eur(g['solar']), eur(s['s'] - g['solar'])] for k, s, g in zip(SIZES, sc, gr)])}
<h2>Battery prices</h2>
{table(["Battery", "Typical price", "Grant", "You pay"], [["5 kWh", eur(sc[6]['b']), "€600", eur(sc[6]['b'] - 600)], ["10 kWh", eur(sc[7]['b']), "€600", eur(sc[7]['b'] - 600)]])}
<p class="muted small">Typical market prices used by our calculator; your quote may be higher or lower. Put your own quote into the calculator's advanced options.</p>
<div class="ad" data-slot="content"></div>
<h2>What pushes the price up</h2>
{lis(["Scaffolding, a high or complex roof, or a split east/west array", "Premium panels or inverters, optimisers for shading", "A battery, EV charger or hot-water diverter", "Upgrading your fuse board or a long cable run"])}
<h2>Paying for it</h2>
<p>Cash, a <a href="home-energy-upgrade-loan.html">Home Energy Upgrade Loan</a> (from about 3–4%), or adding it to your mortgage. <a href="../mortgage/" data-track="cross_app" data-label="mortgage_from_solar">Mortgage calculator →</a></p>
<div class="cta"><h2>Got a quote?</h2><p>Put it in the calculator to see your real payback.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("How much do solar panels cost in Ireland?", f"About {eur(sc[2]['s'])} for a typical 4 kWp system installed in 2026, or {eur(sc[2]['s'] - 1800)} after the €1,800 SEAI grant."),
            ("Is there VAT on solar panels in Ireland?", "No – since 1 May 2023 there's 0% VAT on supplying and installing solar panels on homes, when one business supplies and installs them.")]
    app.page("solar-panel-cost.html", "Solar Panel Cost Ireland 2026 – Prices by Size, After the Grant (0% VAT)",
             f"How much solar panels cost in Ireland in 2026: about {eur(sc[2]['s'])} for 4 kWp, {eur(sc[2]['s'] - 1800)} after the SEAI grant. Prices by size, batteries and 0% VAT.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Cost", None)], h1="How much do solar panels cost?", sources=("seai_pv", "vat"), cross=CROSS, priority="0.9")

    res = run([{"k": "c", "o": dict(county=k, kWp=4, **STD)} for k in RANKED] + [{"k": "c", "o": dict(county=k, kWp=4, battKWh=5, **STD)} for k in RANKED])
    nb, wb = res[:26], res[26:]
    d = calc(county="dublin", kWp=4, **STD)
    body = f"""<p class="lead">Are solar panels worth it in Ireland? For most homes, yes – here's the honest maths, including when they aren't.</p>
<p class="updated">PVGIS data · SEAI grant · {CHECKED}</p>
{key_facts([f"A typical 4 kWp system pays back in <strong>{yrs(min(r['payback'] for r in nb))}</strong> (sunniest county) to <strong>{yrs(max(r['payback'] for r in nb))}</strong> (least sunny).",
            f"Panels last 25–30 years, so you could be <strong>{eur(d['profit'])}</strong> ahead over 25 years in Dublin (with the inverter replaced once).",
            "It's worth it most when you <strong>use power during the day</strong>, have a <strong>south, south-east or south-west roof</strong> and pay a high unit rate.",
            "It's less worth it with a <strong>north roof</strong>, heavy shading, very low use, or if you'll move house in a few years."])}
{chart_card("4 kWp in Dublin: 25 years", payback_svg(d['series'], d['payback'], label="worth"), "Green = profit. You pay off the panels first, then the savings keep coming.")}
<h2>Payback in every county (4 kWp, €250 bill)</h2>
{table(["County", "No battery", "With 5 kWh battery", "25-year gain"], [[f'<a href="solar-panels-{k}.html">{COUNTIES[k][0]}</a>', yrs(a['payback']), yrs(b['payback']), eur(a['profit'])] for k, a, b in zip(RANKED, nb, wb)])}
<div class="ad" data-slot="content"></div>
<h2>Other benefits</h2>
{lis(["A better <strong>BER</strong> – solar typically lifts a home by about one BER band step, helping its value and green mortgage rates", "Protection from future price rises", "Lower carbon emissions"])}
<div class="cta"><h2>Worth it for you?</h2><p>Your county, your bill, your roof.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("Are solar panels worth it in Ireland?", f"For most homes, yes. A 4 kWp system with the SEAI grant typically pays back in {yrs(min(r['payback'] for r in nb))} to {yrs(max(r['payback'] for r in nb))} and lasts 25+ years."),
            ("Does Ireland get enough sun for solar panels?", f"Yes. Panels work from daylight, not heat. Ireland averages about {AVG} kWh per kWp a year – a 4 kWp system makes about {AVG * 4:,} kWh, roughly what a typical home uses.")]
    app.page("are-solar-panels-worth-it.html", "Are Solar Panels Worth It in Ireland? Payback by County 2026",
             "Honest maths on solar panels in Ireland: payback by county with and without a battery, 25-year savings, and when solar isn't worth it.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Is it worth it?", None)], h1="Are solar panels worth it in Ireland?", sources=("pvgis", "seai_pv", "ceg"), cross=CROSS, priority="0.9")

    # system size pages
    rows = []
    for k in SIZES:
        r, rb = run([{"k": "c", "o": dict(county="dublin", kWp=k, **STD)}, {"k": "c", "o": dict(county="dublin", kWp=k, battKWh=5, **STD)}])
        lo, hi = round(COUNTIES[RANKED[-1]][1] * k), round(COUNTIES[RANKED[0]][1] * k)
        rows.append([f'<a href="{k}kwp-solar-system.html">{k} kWp</a>', str(r['panels']), f"{lo:,}–{hi:,} kWh", eur(r['net']), yrs(r['payback'])])
        suits = {2: "a small home or apartment using under 2,500 kWh a year", 3: "a smaller home using 2,500–3,500 kWh", 4: "a typical 3-bed home using 3,500–4,500 kWh – the most popular size",
                 5: "a bigger home, or one with a heat pump", 6: "a large home, or one with an EV and heat pump – about the most a standard single-phase house can connect with an NC6", 8: "a large home with an EV, heat pump and battery (may need a three-phase supply or an NC7 application)"}[k]
        body = f"""<p class="lead">How much does a {k} kWp solar system produce in Ireland, what does it cost and how long does it take to pay back?</p>
{key_facts([f"A {k} kWp system is about <strong>{r['panels']} panels</strong> of {DEF['panelW']} W, needing roughly {round(k * 5)} m² of roof.",
            f"It makes about <strong>{lo:,}–{hi:,} kWh a year</strong> depending on your county ({round(COUNTIES['dublin'][1] * k):,} kWh in Dublin).",
            f"Typical price <strong>{eur(r['cost'])}</strong>, SEAI grant <strong>{eur(r['grant']['solar'])}</strong> – you pay about <strong>{eur(r['net'])}</strong>.",
            f"In Dublin with a €250 bill it pays back in about <strong>{yrs(r['payback'])}</strong> ({yrs(rb['payback'])} with a 5 kWh battery).",
            f"Best for {suits}."])}
{chart_card(f"{k} kWp in Dublin: month by month", month_svg([round(m * k) for m in COUNTIES['dublin'][2]], round(r['usage'] / 12)), "kWh made each month in an average year.")}
{chart_card(f"{k} kWp payback, Dublin", payback_svg(r['series'], r['payback'], rb['series'], f"{k}kwp"), "", [("c-net", "No battery"), ("c-alt", "With 5 kWh battery")])}
<div class="ad" data-slot="content"></div>
<h2>{k} kWp in each county</h2>
{table(["County", "kWh a year", "Payback"], [[f'<a href="solar-panels-{c}.html">{COUNTIES[c][0]}</a>', f"{round(COUNTIES[c][1] * k):,}", yrs(x['payback'])] for c, x in zip(RANKED, run([{"k": "c", "o": dict(county=c, kWp=k, **STD)} for c in RANKED]))])}
<div class="chip-list">{"".join(f'<a href="{s}kwp-solar-system.html">{s} kWp</a>' for s in SIZES if s != k)}<a href="system-sizes.html">Which size? →</a></div>
<div class="cta"><h2>Your numbers</h2><p>{k} kWp with your bill and county.</p><a class="btn" href="./?kwp={k}">Open the calculator</a></div>"""
        faqs = [(f"How much does a {k}kW solar system produce in Ireland?", f"About {lo:,} to {hi:,} kWh a year depending on the county – {round(COUNTIES['dublin'][1] * k):,} kWh in Dublin, on a south-facing roof."),
                (f"How many panels is a {k}kW system?", f"About {r['panels']} panels of {DEF['panelW']} watts.")]
        app.page(f"{k}kwp-solar-system.html", f"{k}kW Solar System Ireland – Output, Cost After Grant & Payback",
                 f"A {k} kWp solar system in Ireland: {r['panels']} panels, {lo:,}–{hi:,} kWh a year, about {eur(r['net'])} after the SEAI grant, payback about {yrs(r['payback'])}.",
                 body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("System sizes", "system-sizes.html"), (f"{k} kWp", None)], h1=f"{k} kWp solar system", sources=("pvgis", "seai_pv"), cross=CROSS)
    body = f"""<p class="lead">What size solar system do you need? Match it to the electricity you use in a year.</p>
{key_facts(["Rule of thumb: <strong>yearly kWh ÷ {AVG}</strong> = kWp. A home using 3,800 kWh suits about 4 kWp.", "Your yearly use is on your bills – or roughly your 2-monthly bill × 6, less the standing charge, divided by the unit rate.",
            "The grant maxes out at 4 kWp, but going bigger can still pay if you have an EV or heat pump.", "Most single-phase homes can connect up to about 6 kW with an NC6 form."])}
{table(["Size", "Panels", "kWh a year", "You pay (after grant)", "Payback (Dublin)"], rows)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Not sure?</h2><p>The calculator recommends a size from your bill.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("system-sizes.html", "What Size Solar System Do I Need? Ireland – 2kW to 8kW Compared",
             "Choosing a solar system size in Ireland: 2, 3, 4, 5, 6 and 8 kWp compared by panels, yearly output, cost after the SEAI grant and payback.",
             body, crumbs=[("Solar", "./"), ("System sizes", None)], h1="What size solar system do I need?", sources=("pvgis", "seai_pv"), cross=CROSS, priority="0.8")


def build_counties():
    cards, rows = [], []
    for k in RANKED:
        name, y, mon = COUNTIES[k]
        r, rb, r6 = run([{"k": "c", "o": dict(county=k, kWp=4, **STD)}, {"k": "c", "o": dict(county=k, kWp=4, battKWh=5, **STD)}, {"k": "c", "o": dict(county=k, kWp=6, **STD)}])
        rank = RANKED.index(k) + 1
        diff = round((y / AVG - 1) * 100)
        cards.append(f'<a href="solar-panels-{k}.html"><strong>{name}</strong><span>{y} kWh/kWp · {yrs(r["payback"])}</span></a>')
        rows.append([f'<a href="solar-panels-{k}.html">{name}</a>', str(rank), str(y), f"{round(y * 4):,}", yrs(r['payback'])])
        best, worst = FULLM[mon.index(max(mon))], FULLM[mon.index(min(mon))]
        body = f"""<p class="lead">Solar panels in {name}: how much they make, what you'd save and how long they take to pay back – with the SEAI grant.</p>
<p class="updated">PVGIS (EU JRC) · SEAI grant · {CHECKED}</p>
{key_facts([f"{name} gets about <strong>{y} kWh per kWp</strong> a year on a south-facing roof – <strong>{rank}{'st' if rank == 1 else 'nd' if rank == 2 else 'rd' if rank == 3 else 'th'} of 26 counties</strong>, {abs(diff)}% {'above' if diff >= 0 else 'below'} the Irish average.",
            f"A <strong>4 kWp</strong> system makes about <strong>{round(y * 4):,} kWh</strong> a year and costs about <strong>{eur(r['net'])}</strong> after the €1,800 grant.",
            f"With a €250 bill every 2 months it saves about <strong>{eur(r['saving1'])}</strong> in year 1 and pays back in <strong>{yrs(r['payback'])}</strong> ({yrs(rb['payback'])} with a 5 kWh battery).",
            f"Over 25 years that's about <strong>{eur(r['profit'])}</strong> ahead.",
            f"Best month: {best} ({round(max(mon) * 4)} kWh). Worst: {worst} ({round(min(mon) * 4)} kWh)."])}
{chart_card(f"4 kWp in {name}: payback", payback_svg(r['series'], r['payback'], rb['series'], k), "", [("c-net", "No battery"), ("c-alt", "With 5 kWh battery")])}
{chart_card(f"4 kWp in {name}: kWh each month", month_svg([round(m * 4) for m in mon], round(r['usage'] / 12)))}
<div class="ad" data-slot="content"></div>
<h2>Different sizes in {name}</h2>
{table(["System", "kWh a year", "You pay", "Saved year 1", "Payback"], [[f"{s} kWp", f"{x['gen']:,}", eur(x['net']), eur(x['saving1']), yrs(x['payback'])] for s, x in zip((3, 4, 6), run([{"k": "c", "o": dict(county=k, kWp=s, **STD)} for s in (3, 4, 6)]))])}
<h2>Roof direction in {name}</h2>
{table(["Roof faces", "kWh a year (4 kWp)", "Payback"], [[META['facing'][f][0], f"{x['gen']:,}", yrs(x['payback'])] for f, x in zip(("s", "sw", "ew", "n"), run([{"k": "c", "o": dict(county=k, kWp=4, facing=f, **STD)} for f in ("s", "sw", "ew", "n")]))])}
<h2>Getting solar in {name}</h2>
<p>Use an <strong>SEAI-registered</strong> solar company (SEAI keeps a searchable list) and apply for the grant before work starts. <a href="how-to-apply.html">How to apply →</a> · <a href="choosing-an-installer.html">Choosing an installer →</a></p>
<div class="chip-list">{"".join(f'<a href="solar-panels-{c}.html">{COUNTIES[c][0]}</a>' for c in RANKED[max(0, rank - 4):rank + 3] if c != k)}<a href="by-county.html">All counties →</a></div>
<div class="cta"><h2>Your home in {name}</h2><p>Your bill, roof and battery.</p><a class="btn" href="./?county={k}">Open the calculator</a></div>"""
        faqs = [(f"Are solar panels worth it in {name}?", f"Yes for most homes. A 4 kWp system makes about {round(y * 4):,} kWh a year in {name} and pays back in about {yrs(r['payback'])} with the SEAI grant."),
                (f"How much do solar panels produce in {name}?", f"About {y} kWh per kWp a year on a south-facing roof, so about {round(y * 4):,} kWh for a 4 kWp system.")]
        app.page(f"solar-panels-{k}.html", f"Solar Panels {name} 2026 – Output, Savings & Payback with SEAI Grant",
                 f"Solar panels in {name}: {y} kWh per kWp a year, a 4 kWp system makes {round(y * 4):,} kWh and pays back in about {yrs(r['payback'])} after the €1,800 SEAI grant.",
                 body, active="By county", jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("By county", "by-county.html"), (name, None)], h1=f"Solar panels in {name}", sources=("pvgis", "seai_pv"), cross=CROSS)
    body = f"""<p class="lead">How much solar power each county makes, and how long a typical system takes to pay back.</p>
<p class="updated">PVGIS 5.3 (SARAH-3, 2005–2023) · south-facing, 35° · {CHECKED}</p>
{key_facts([f"<strong>{COUNTIES[RANKED[0]][0]}</strong> is the sunniest county for solar ({COUNTIES[RANKED[0]][1]} kWh per kWp) and <strong>{COUNTIES[RANKED[-1]][0]}</strong> the least ({COUNTIES[RANKED[-1]][1]}).",
            f"The average is <strong>{AVG} kWh per kWp</strong>. The south-east coast does best; the north-west does worst.", "Even the least sunny county pays back well within the life of the panels."])}
<div class="county-grid">{''.join(cards)}</div>
<h2>Ranked</h2>
{table(["County", "Rank", "kWh per kWp", "4 kWp makes", "Payback"], rows)}
<div class="ad" data-slot="content"></div>"""
    app.page("by-county.html", "Solar Panels by County Ireland – Output & Payback in All 26 Counties",
             f"Solar output and payback in every Irish county from PVGIS data: {COUNTIES[RANKED[0]][0]} is sunniest ({COUNTIES[RANKED[0]][1]} kWh/kWp), {COUNTIES[RANKED[-1]][0]} least ({COUNTIES[RANKED[-1]][1]}).",
             body, active="By county", crumbs=[("Solar", "./"), ("By county", None)], h1="Solar panels by county", sources=("pvgis",), cross=CROSS, priority="0.8")


# ---------- Practical guides ----------
def build_guides():
    fac = META["facing"]
    body = f"""<p class="lead">Does your roof have to face south? No – but it makes a difference. Here's how much each direction makes.</p>
<p class="updated">PVGIS (EU JRC), midlands · {CHECKED}</p>
{table(["Roof faces", "Shallow 15°", "Standard 35°", "Steep 50°"], [[fac[f][0]] + [f"{v * 100:.0f}%" for v in fac[f][1]] for f in ("s", "sw", "ew", "nw", "n")])}
<p class="muted small">Compared with a south-facing roof at 35° (100%). Panels laid flat on a flat roof make about 84%; most flat-roof installs tilt them, so they do better.</p>
{key_facts(["<strong>South</strong> is best, but <strong>south-east or south-west</strong> loses only about 6–7%.", "<strong>East/west</strong> loses about 20% – but spreads output across morning and evening, when you're more likely to be home, so you use more of it.",
            "<strong>North-facing</strong> roofs make about 55–70%. On a shallow roof it can still pay; on a steep one it usually doesn't.", "Shading matters more than direction – a chimney or tree shadow can cut output a lot. Ask about optimisers."])}
<div class="ad" data-slot="content"></div>
<h2>Payback by roof direction (4 kWp, Dublin)</h2>
{table(["Roof faces", "kWh a year", "Payback"], [[fac[f][0], f"{x['gen']:,}", yrs(x['payback'])] for f, x in zip(("s", "sw", "ew", "nw", "n"), run([{"k": "c", "o": dict(county="dublin", kWp=4, facing=f, **STD)} for f in ("s", "sw", "ew", "nw", "n")]))])}
<div class="cta"><h2>Your roof</h2><p>Pick your direction and angle in the calculator.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("Do solar panels work on an east-west roof in Ireland?", "Yes. East or west roofs make about 80% of a south roof, and spread the power over the morning and evening."),
            ("Are solar panels worth it on a north-facing roof?", "Rarely. A north roof makes about 55–70% of a south roof. On a shallow pitch it can still pay back; on a steep one usually not.")]
    app.page("roof-direction.html", "Solar Panels on East-West or North-Facing Roofs Ireland – How Much Less?",
             "How roof direction and angle affect solar output in Ireland (PVGIS): south 100%, south-east/west ~93%, east/west ~79%, north ~56%. Payback for each.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Roof direction", None)], h1="Which way should solar panels face?", sources=("pvgis",), cross=CROSS, priority="0.7")

    d = COUNTIES["dublin"][2]
    body = f"""<p class="lead">Do solar panels work in an Irish winter? Yes, but much less. Here's what to expect month by month.</p>
<p class="updated">PVGIS (EU JRC) · {CHECKED}</p>
{chart_card("4 kWp in Dublin: kWh each month", month_svg([round(m * 4) for m in d], 300), "A typical home uses about 300 kWh a month.")}
{key_facts([f"In Dublin, 4 kWp makes about <strong>{round(d[11] * 4)} kWh in December</strong> but <strong>{round(d[4] * 4)} kWh in May</strong> – nearly {round(d[4] / d[11])} times more.",
            f"<strong>April to September</strong> makes about {round(sum(d[3:9]) / sum(d) * 100)}% of the year's power.", "Panels work on cloudy days – from daylight, not heat. Cold weather actually helps them run efficiently.",
            "In winter you'll still buy most of your power, so payback is based on the whole year, not just summer."])}
<h2>Every county, December vs June (4 kWp)</h2>
{table(["County", "December", "June", "Whole year"], [[f'<a href="solar-panels-{k}.html">{COUNTIES[k][0]}</a>', f"{round(COUNTIES[k][2][11] * 4)} kWh", f"{round(COUNTIES[k][2][5] * 4)} kWh", f"{round(COUNTIES[k][1] * 4):,} kWh"] for k in RANKED])}
<div class="ad" data-slot="content"></div>
<h2>Getting more from solar in winter</h2>
{lis(["A battery on a night-rate tariff can charge cheaply at night in winter", "Snow slides off tilted panels quickly; you don't need to clean them", "A hot-water diverter is less useful in winter – there's little surplus"])}
<div class="cta"><h2>See your year</h2><p>Monthly output for your county.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("Do solar panels work in winter in Ireland?", f"Yes, but they make far less: about {round(d[11] * 4)} kWh in December from a 4 kWp system in Dublin, compared with {round(d[4] * 4)} kWh in May."),
            ("Do solar panels work on cloudy days?", "Yes. They work from daylight, so they still produce on cloudy days – just less than in full sun.")]
    app.page("solar-in-winter.html", "Do Solar Panels Work in Winter in Ireland? Output Month by Month",
             f"Solar panels in an Irish winter: a 4 kWp system makes about {round(d[11] * 4)} kWh in December vs {round(d[4] * 4)} kWh in May. Monthly output for every county.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Solar in winter", None)], h1="Do solar panels work in winter?", sources=("pvgis",), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Do you need planning permission for solar panels in Ireland? For most homes, no.</p>
<p class="updated">gov.ie · S.I. 493/2022 · {CHECKED}</p>
{key_facts(["Since <strong>October 2022</strong>, rooftop solar on <strong>houses</strong> is exempt from planning permission with <strong>no limit on the roof area</strong> – including in Solar Safeguarding Zones near airports.",
            "There are conditions on how the panels sit – for example, keeping a gap from the edge of the roof and not sticking up too far from the roof. A registered installer will design to these.",
            "<strong>Free-standing panels</strong> in the garden are exempt up to <strong>25 m²</strong>, with conditions (e.g. not in front of the house).",
            "You <strong>do</strong> need permission for a <strong>protected structure</strong>, and usually in an <strong>Architectural Conservation Area</strong> – check with your council.",
            "Apartments, businesses, farms and other buildings have their own exemptions and limits."])}
<div class="ad" data-slot="content"></div>
<h2>Check before you start</h2>
{lis(["Is your house a protected structure? Your council's Record of Protected Structures will say.", "Are you in an Architectural Conservation Area? Ask the council's planning department.",
      "In an apartment or managed estate? You'll need the owner management company's permission for a shared roof.", "Want panels on a shed or ground mount? Check the 25 m² and placement rules."])}
<p>The rules are in the <a href="https://www.irishstatutebook.ie/eli/2022/si/493/made/en/pdf" rel="noopener" target="_blank">Exempted Development (No. 3) Regulations 2022</a>. If in doubt, ask your council for a Section 5 declaration.</p>
<div class="cta"><h2>Good to go?</h2><p>See your payback.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("Do I need planning permission for solar panels in Ireland?", "Not for rooftop panels on most houses – since October 2022 there's no area limit. Protected structures and many Architectural Conservation Areas still need permission."),
            ("Can I put solar panels in my garden without planning?", "Yes, free-standing panels are exempt up to 25 m², subject to conditions such as not placing them in front of the house.")]
    app.page("planning-permission.html", "Do I Need Planning Permission for Solar Panels in Ireland? (2026)",
             "Planning permission for solar panels in Ireland: rooftop panels on houses are exempt with no area limit since 2022; ground panels up to 25 m². When you still need permission.",
             body, jsonld=[faq_ld(faqs)], crumbs=[("Solar", "./"), ("Planning permission", None)], h1="Planning permission for solar panels", sources=("plan", "si493"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Picking the right solar company matters more than picking the right panel. What to ask, and the red flags.</p>
{key_facts(["Only <strong>SEAI-registered solar PV companies</strong> qualify for the grant – check the SEAI register before you sign.", "Get <strong>at least 3 quotes</strong> and compare the price per kWp and the expected kWh a year.",
            "Get a <strong>written contract</strong> with the works, price, timing, payment terms and warranties.", "Talk to previous customers and check reviews."])}
<h2>Questions to ask every installer</h2>
<ul class="todo"><li>How many kWh will it make a year – and how did you work that out?</li><li>What's the total price, including scaffolding, VAT (0%) and any fuse board work?</li>
<li>Which panels and inverter, and what are the warranties? (Panels typically 25 years on output; inverters 5–12)</li><li>Will you submit the NC6 to ESB Networks and upload all the SEAI paperwork?</li>
<li>Is my roof and electricity use suitable? Any shading?</li><li>What ongoing service or maintenance is needed, and what does it cost?</li><li>Is the battery or inverter backup-capable, if I want that?</li></ul>
<div class="ad" data-slot="content"></div>
<h2>Red flags</h2>
{lis(["Pressure to sign today or a 'today only' discount", "Asking you to start before your SEAI grant offer arrives", "A big deposit up front (more than about 25%)",
      "Payback claims far shorter than our calculator shows", "Not registered with SEAI, or vague about who does the install", "No written quote with a model number for the panels and inverter"])}
<p>SEAI doesn't approve or guarantee any company's work – your contract is with the company.</p>
<div class="cta"><h2>Compare a quote</h2><p>Put the price into the advanced options.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("choosing-an-installer.html", "Choosing a Solar Panel Installer in Ireland – Questions to Ask & Red Flags",
             "How to pick a solar PV installer in Ireland: SEAI registration, 3 quotes, questions to ask, warranties, the NC6 and red flags to avoid.",
             body, crumbs=[("Solar", "./"), ("Choosing an installer", None)], h1="Choosing a solar installer", sources=("seai_pv",), cross=CROSS, priority="0.7")

    ex = calc(county="dublin", kWp=4, loan=True, loanRate=3.5, loanYears=7, **STD)
    body = f"""<p class="lead">You can borrow for solar panels at a low rate under the Government-backed Home Energy Upgrade Loan Scheme.</p>
<p class="updated">SBCI scheme · Checked {CHECKED}</p>
{key_facts(["Loans of <strong>€5,000 to €75,000</strong> for home energy upgrades that also get an <strong>SEAI grant</strong> – solar PV included.",
            "Rates from about <strong>3% to 4.15%</strong> depending on the lender and the amount (e.g. PTSB from January 2026: 4.15% under €15,000, down to 2.99% for €50,000+).",
            "Lenders include <strong>AIB, Bank of Ireland, PTSB</strong> and some credit unions.", "The scheme is open until <strong>31 December 2026</strong> or until it's fully used – check with your lender.",
            f"Example: {eur(ex['net'])} over 7 years at 3.5% is about <strong>{eur(ex['loan']['monthly'])} a month</strong>, against about {eur(ex['saving1'] / 12)} a month saved in Dublin."])}
<p class="muted small">Note: the minimum loan is €5,000, so it suits solar with a battery or bigger upgrades. For smaller amounts, compare a credit union or green personal loan.</p>
<div class="ad" data-slot="content"></div>
{chart_card("4 kWp in Dublin, 7-year loan at 3.5%", payback_svg(ex['series'], None, label="loan"), "Savings minus repayments, added up. With a loan you're ahead almost from the start, and well ahead once it's repaid.")}
<div class="cta"><h2>Loan or cash?</h2><p>Tick “Paying with a loan” in the advanced options.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("home-energy-upgrade-loan.html", "Home Energy Upgrade Loan for Solar Panels – Rates & How It Works (2026)",
             "The SBCI Home Energy Upgrade Loan for solar panels: €5,000–€75,000 at about 3–4%, from AIB, Bank of Ireland, PTSB and credit unions. Repayments vs savings.",
             body, crumbs=[("Solar", "./"), ("Loans", None)], h1="Home Energy Upgrade Loan for solar", sources=("heul", "ptsb"), cross=["mortgage", "salary", "stamp", "taxrefund"], priority="0.7")

    body = f"""<p class="lead">Farmers can get a 60% grant for solar panels on farm buildings under TAMS 3.</p>
<p class="updated">Department of Agriculture · Checked {CHECKED}</p>
{key_facts(["The <strong>Solar Capital Investment Scheme (SCIS)</strong> under TAMS 3 pays <strong>60%</strong> of eligible costs.",
            "It has its own investment ceiling of <strong>€90,000</strong>, separate from other TAMS 3 schemes.", "Systems up to <strong>62 kW</strong> are supported; batteries are eligible too.",
            "Applications are in tranches – the 2026 tranches close on 6 March, 5 June, 4 September and <strong>4 December 2026</strong>.",
            "It's for the farm. Your farmhouse can still get the standard SEAI home grant (€1,800 + €600 battery)."])}
<div class="ad" data-slot="content"></div>
<h2>Is farm solar worth it?</h2>
<p>Farms with daytime use – milking, cooling, pumping – use most of their solar directly, so payback is often faster than for homes. Size it to your daytime load; extra exports earn the Clean Export Guarantee rate.</p>
<p>Apply through the Department of Agriculture's agfood.ie system, usually with your adviser.</p>
<div class="cta"><h2>Your farmhouse</h2><p>See the home grant and payback.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("farm-solar-grant.html", "Farm Solar Grant Ireland 2026 – TAMS 3 Solar Capital Investment Scheme (60%)",
             "Solar panels for farms: the TAMS 3 Solar Capital Investment Scheme pays 60% up to a €90,000 investment ceiling, systems up to 62 kW. 2026 tranche dates.",
             body, crumbs=[("Solar", "./"), ("Farm solar grant", None)], h1="Farm solar grant (TAMS 3)", sources=("scis",), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Businesses, schools, sports clubs and community groups can get SEAI grants for solar – currently at a boosted rate.</p>
<p class="updated">SEAI · Checked {CHECKED}</p>
{key_facts(["The <strong>Non-Domestic Microgen Grant</strong> supports solar PV for businesses, farms, schools, community centres and non-profits – systems up to 1,000 kWp.",
            "From <strong>7 October 2026 to 6 July 2027</strong> it's temporarily boosted to <strong>45% of eligible costs</strong>, with per-kWp rates doubled.",
            "The maximum grant rises from €162,600 to <strong>€325,200</strong>. You get the lower of the per-kWp amount or 45% of the invoiced cost.",
            "Applications made before 7 October 2026 aren't increased.", "Use an SEAI-registered non-domestic solar PV company and get approval before work starts."])}
<div class="ad" data-slot="content"></div>
<h2>Why act before July 2027</h2>
<p>The 45% rate is for new applications for about 9 months. Businesses with high daytime use – shops, offices, cold rooms – usually see the fastest payback. Larger systems need an NC7 or other ESB Networks connection application.</p>
<div class="cta"><h2>For your home</h2><p>See the household grant and payback.</p><a class="btn" href="./">Open the calculator</a></div>"""
    app.page("business-solar-grant.html", "SEAI Business Solar Grant 2026 – 45% Until July 2027 (Non-Domestic Microgen)",
             "SEAI Non-Domestic Microgen Grant for business solar PV: boosted to 45% of costs and up to €325,200 from 7 October 2026 to 6 July 2027. Who qualifies.",
             body, crumbs=[("Solar", "./"), ("Business solar grant", None)], h1="Business solar grant", sources=("seai_biz", "oct26"), cross=CROSS, priority="0.7")

    d = calc(county="dublin", kWp=4, **STD)
    FAQ = [("How much is the SEAI solar grant in 2026?", "€700 per kWp for the first 2 kWp, then €200 per kWp up to 4 kWp – up to €1,800. Plus €600 for a battery of 5 kWh or more."),
           ("Does my house qualify for the solar grant?", "If it has an MPRN, was built and occupied before 2025, and hasn't had a solar PV grant before. Homeowners and private landlords can apply."),
           ("Can I start the work and apply later?", "No. You must have your SEAI grant offer before any work starts, or you won't get the grant."),
           ("How long do I have to finish the install?", "8 months from your grant offer, including the post-works BER and paperwork."),
           ("How long does the grant take to be paid?", "Usually 4–6 weeks after your company uploads the documents and your BER is published."),
           ("How long do solar panels take to pay back?", f"About {yrs(d['payback'])} for a typical 4 kWp system in Dublin with the grant – roughly 5 to 8 years across Ireland."),
           ("How many solar panels do I need?", "Match the system to your yearly use: kWh ÷ about 930 = kWp. A typical home using 3,700 kWh suits about 4 kWp – 9 or 10 panels."),
           ("Do solar panels work in Ireland's weather?", f"Yes. Ireland averages about {AVG} kWh per kWp a year. Panels work from daylight, including cloudy days, though winter output is much lower."),
           ("Is a battery worth it?", "It helps you use more of your own power. With the €600 grant it can pay off, especially if you're out during the day or on a night-rate tariff. Try both in the calculator."),
           ("Will I be paid for the power I export?", "Yes, about 15–19.5c per kWh under the Clean Export Guarantee, credited on your bill. You need a smart meter and an NC6 form."),
           ("Is solar export income taxed?", "Not up to €400 a year (2024–2028), rising to €600 from 2027."),
           ("Is there VAT on solar panels?", "No – 0% VAT on supply and installation on homes since May 2023."),
           ("Do I need planning permission?", "Not for rooftop panels on most houses. Protected structures and many Architectural Conservation Areas need permission."),
           ("Do solar panels improve my BER?", "Yes – you need a post-works BER for the grant anyway, and solar usually improves the rating."),
           ("Can renters get solar panels?", "Renters can't apply, but landlords can, and a Dublin pilot gives up to €9,000 for RAS tenancies."),
           ("What if I move house?", "The panels stay with the house and usually add to its appeal and BER. Payback is shorter than most people stay in a home."),
           ("How long do solar panels last?", "25–30 years, losing about 0.5% output a year. The inverter usually needs replacing once, around year 10–15."),
           ("Do I need to clean solar panels?", "Rarely in Ireland – rain does most of it. Check now and then for leaves or bird mess."),
           ("Can I add a battery later?", "Yes, and you can claim the €600 battery grant for it as long as you apply before it's installed."),
           ("Is this calculator official?", "No – it's a free, independent tool using PVGIS data and SEAI's published grant rules. Always get quotes from SEAI-registered companies.")]
    app.page("faq.html", "Solar Panels Ireland FAQ 2026 – Grants, Payback, Batteries, Tax & More",
             "Solar panel questions answered for Ireland: SEAI grant, eligibility, payback, panel numbers, batteries, export payments, tax, VAT, planning and BER.",
             f'<p class="lead">Your solar panel questions answered.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Solar", "./"), ("FAQ", None)], h1="Solar panels: questions answered", sources=("seai_pv", "ceg", "rev", "plan"), cross=CROSS)


if __name__ == "__main__":
    build_index(); build_grants(); build_export(); build_money(); build_counties(); build_guides()
    og_image(os.path.join(app.root, "og.png"), "SOLAR · IRELAND", "Solar panel", "payback calculator", "SEAI grant €1,800 + €600 battery", "Savings & payback for your county",
             "tavion.ie/solar  ·  free, no sign-up", (252, 211, 77), (180, 83, 9), (60, 35, 5))
    app.update_sitemap()
    app.update_llms("- [Solar Panel Calculator](https://tavion.ie/solar/): solar PV payback, SEAI grant, savings and export income for every Irish county, with grant, battery, export, tax and planning guides.",
                    "Solar panels: key facts",
                    f"""- SEAI solar PV grant (homes): €700/kWp for the first 2 kWp, €200/kWp up to 4 kWp, max €1,800. €600 battery grant for 5 kWh+ (from 6 Oct 2026). Homes built and occupied before 2025 (was pre-2021). Apply and get the offer before work; 8 months to complete; post-works BER required; paid 4-6 weeks after documents.
- Enhanced grant for qualifying welfare recipients: €3,350/kWp to 2 kWp, €850/kWp to 4 kWp, max €8,400, €9,000 with battery. Warmer Homes: solar + battery fully funded.
- Clean Export Guarantee rates Nov 2026: 15.2c-19.5c/kWh (SSE Airtricity, Electric Ireland 19.5c). Export income tax-free up to €400/yr (2024-2028), €600 from 2027 (Budget 2027).
- 0% VAT on solar supply and installation for homes since 1 May 2023. Rooftop solar on houses exempt from planning with no area limit since Oct 2022.
- PVGIS yield (south, 35°): {COUNTIES[RANKED[0]][0]} {COUNTIES[RANKED[0]][1]} to {COUNTIES[RANKED[-1]][0]} {COUNTIES[RANKED[-1]][1]} kWh/kWp/yr; average {AVG}.
- Pages: [Calculator](https://tavion.ie/solar/), [SEAI grant](https://tavion.ie/solar/seai-solar-grant.html), [How to apply](https://tavion.ie/solar/how-to-apply.html), [Battery grant](https://tavion.ie/solar/battery-grant.html), [Export rates](https://tavion.ie/solar/selling-electricity.html), [By county](https://tavion.ie/solar/by-county.html), [FAQ](https://tavion.ie/solar/faq.html).""")
    print("Built", len(app.files), "pages in", app.root)
