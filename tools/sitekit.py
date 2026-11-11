"""
Shared page shell and helpers for Tavion app builders (welfare, auto-enrolment, ...).
Each app passes its own brand, tabs and footer links; the SEO tags, structured data,
sources box, cross-app links, share buttons and ad slot are the same everywhere.
"""
import datetime, json, os, re, subprocess
from urllib.parse import quote

SITE = "https://tavion.ie/"
TODAY = datetime.date.today()
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

# Every Tavion app, for "Try also" boxes and footers. (icon, name, blurb, path, label)
APPS = {
    "salary": ("💶", "Take-home pay calculator", "Net pay after tax, USC and PRSI – Budget 2027", "salary/", "salary"),
    "welfare": ("🤝", "Social welfare rates 2027", "What you'll get, Christmas Bonus and payment dates", "welfare/", "welfare"),
    "pension": ("🌱", "Auto-enrolment pension calculator", "MyFutureFund: what you pay and what you'll have", "auto-enrolment/", "pension"),
    "mortgage": ("🔑", "How much could I borrow?", "Mortgage, deposit and repayments", "mortgage/", "mortgage"),
    "stamp": ("🧾", "Stamp duty & property tax", "Buying costs and LPT by council", "stamp-duty/", "stamp"),
    "rent": ("🏠", "Rent increase checker", "Is your rent increase legal?", "rent/", "rent"),
    "citizenship": ("🛂", "Citizenship calculator", "When can you apply?", "citizenship/", "citizenship"),
}

def eur(n, dp=0):
    return ("−" if n < 0 else "") + "€" + f"{abs(n):,.{dp}f}"

def lis(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def table(head, rows, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<div class="table-wrap"><table{c}><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" +
            "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows) + "</tbody></table></div>")

def strip(s):
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").strip()

def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in pairs]}

def faq_html(pairs):
    return "".join(f'<details class="faq"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in pairs)

def key_facts(items):
    return '<div class="facts-box"><h2 class="tl">Key facts</h2><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"

def node(engine_path, script, q):
    p = subprocess.run(["node", "-e", script, engine_path], input=json.dumps(q), capture_output=True, text=True, check=True)
    return json.loads(p.stdout)

class App:
    def __init__(self, folder, name, logo, brand, theme, tabs, footer_nav, src, cross, share_default, share_intro, label, disclaimer):
        self.folder, self.name, self.logo, self.theme, self.tabs = folder, name, logo, theme, tabs
        self.footer_nav, self.SRC, self.cross, self.share_default, self.share_intro = footer_nav, src, cross, share_default, share_intro
        self.label, self.disclaimer = label, disclaimer
        self.BASE = SITE + folder + "/"
        self.root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", folder))
        self.files = []

    def sources(self, keys):
        return ('<div class="sources"><h2 class="tl">Sources – check them yourself</h2><ul>' +
                "".join(f'<li><a href="{self.SRC[k][1]}" rel="noopener" target="_blank">{self.SRC[k][0]}</a></li>' for k in keys) + "</ul></div>")

    def try_also(self, keys, overrides=None):
        overrides = overrides or {}
        items = []
        for k in keys:
            icon, t, d, path, lab = APPS[k]
            href = overrides.get(k, "../" + path)
            items.append(f'<a href="{href}" data-track="cross_app" data-label="{lab}"><b>{icon}</b><span><strong>{t}</strong>{d}</span></a>')
        return '<div class="try"><h2 class="tl">Try also</h2><div class="try-grid">' + "".join(items) + "</div></div>"

    def share(self, text, url, label):
        wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
        fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
        return (f'<h2>Share it</h2><p class="muted">{self.share_intro}</p><div class="share">'
                f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
                f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

    def page(self, filename, title, desc, body, active=None, jsonld=(), crumbs=None, slot="content", scripts=(), share_text=None, h1=None,
             sources=(), cross=None, cross_over=None, priority="0.6"):
        url = self.BASE if filename == "index.html" else self.BASE + filename
        on = ' class="on"'
        tabs = "".join(f'<a href="{href}"{on if label == active else ""}>{label}</a>' for href, label in self.tabs)
        crumb_html = ""
        if crumbs:
            crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs) + "</nav>"
            items = [{"@type": "ListItem", "position": i + 1, "name": strip(t), "item": (self.BASE + (h if h not in ("./", None) else "")) if h else url} for i, (t, h) in enumerate(crumbs)]
            jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
        jsonld = list(jsonld) + [{"@context": "https://schema.org", "@type": "WebPage", "name": strip(title), "url": url, "description": desc, "inLanguage": "en-IE",
                                  "dateModified": TODAY.isoformat(), "isPartOf": {"@type": "WebSite", "name": "Tavion", "url": SITE},
                                  "publisher": {"@type": "Organization", "name": "Tavion", "url": SITE, "logo": SITE + "images/logo.png"},
                                  "citation": [self.SRC[k][1] for k in sources]}]
        ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
        extra = "".join(f'<script src="{s}"></script>' for s in scripts)
        others = " · ".join(f'<a href="../{APPS[k][3]}" data-track="cross_app" data-label="{APPS[k][4]}">{APPS[k][0]} {APPS[k][1]}</a>' for k in APPS if k != self.label)
        html = f"""<!doctype html>
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
<meta property="og:image" content="{self.BASE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{self.theme}">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>{self.logo}</b> {self.name}</a><a class="small" href="../" data-track="apps_click" data-label="{self.label}_header">More Tavion apps</a></div>
  <nav class="tabs" aria-label="Sections"><div class="wrap">{tabs}</div></nav>
</header>
<main class="wrap">
{crumb_html}
{('<h1>' + h1 + '</h1>') if h1 else ''}
{body}
{self.try_also(cross, cross_over) if cross else ''}
{self.sources(sources) if sources else ''}
<div class="ad" data-slot="{slot}"></div>
{self.share(share_text or self.share_default, url, filename.replace(".html", ""))}
</main>
<footer>
  <div class="wrap">
    <nav aria-label="{self.name} pages">{self.footer_nav}</nav>
    <p>Also free from Tavion: {others}</p>
    <p>{self.disclaimer}</p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="{self.label}_footer">More free apps from Tavion</a></p>
  </div>
</footer>
<script src="js/site.js"></script>{extra}
</body>
</html>
"""
        os.makedirs(self.root, exist_ok=True)
        with open(os.path.join(self.root, filename), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        self.files.append((filename, priority))

    def update_sitemap(self):
        path = os.path.join(os.path.dirname(self.root), "sitemap.xml")
        xml = open(path, encoding="utf-8").read()
        xml = re.sub(r"\s*<url><loc>https://tavion\.ie/" + re.escape(self.folder) + r"/[^<]*</loc>.*?</url>", "", xml)
        xml = xml.replace("\n</urlset>", "".join(f'\n  <url><loc>{self.BASE}{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>'
                                                 for fn, pr in self.files) + "\n</urlset>")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(xml)

    def update_llms(self, app_line, section_title, facts_md):
        path = os.path.join(os.path.dirname(self.root), "llms.txt")
        txt = open(path, encoding="utf-8").read()
        name = re.match(r"- \[([^\]]+)\]", app_line).group(1)
        txt = re.sub(r"\n- \[" + re.escape(name) + r"\][^\n]*", "", txt)
        txt = re.sub(r"\n## " + re.escape(section_title) + r"\n.*?(?=\n## |\Z)", "", txt, flags=re.S)
        txt = re.sub(r"(\n- \[Irish Citizenship Calculator\][^\n]*)", lambda m: m.group(1) + "\n" + app_line, txt, count=1)
        txt = txt.replace("\n## Optional", f"\n## {section_title}\n\n{facts_md.strip()}\n\n## Optional", 1)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)

def og_image(path, badge, line1, line2, sub1, sub2, url, accent, badge_rgb, tint):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (11, 15, 25)); d = ImageDraw.Draw(im)
    for i in range(H):
        a = max(0, 1 - i / 520); d.line([(0, i), (W, i)], fill=(int(11 + tint[0] * a), int(15 + tint[1] * a), int(25 + tint[2] * a)))
    def font(size, bold=True):
        for n in (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
            try:
                return ImageFont.truetype(n, size)
            except OSError:
                continue
        return ImageFont.load_default()
    w = d.textlength(badge, font=font(28)) + 44
    d.rounded_rectangle([70, 70, 70 + w, 116], 23, fill=badge_rgb); d.text((92, 78), badge, font=font(28), fill=(255, 255, 255))
    d.text((70, 160), line1, font=font(88), fill=(241, 245, 249)); d.text((70, 262), line2, font=font(88), fill=accent)
    d.text((70, 400), sub1, font=font(40, False), fill=(148, 163, 184)); d.text((70, 452), sub2, font=font(40, False), fill=(148, 163, 184))
    d.text((70, 545), url, font=font(32), fill=(56, 189, 248))
    im.save(path, optimize=True)
