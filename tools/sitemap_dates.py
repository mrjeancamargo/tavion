"""
Keeps sitemap <lastmod> dates honest.

Every builder rewrites all of its pages, so without this every page would claim
"changed today" on every rebuild – and Google learns to ignore dates that are always new.
This script hashes each page's real content (ignoring the build date stamps), compares it
with tools/data/page_hashes.json, and only moves a page's date forward when the content
actually changed. It also writes that same date into the page's JSON-LD "dateModified".

Run from the repo root after any build:   python tools/sitemap_dates.py
(The builders call it automatically.)
"""
import datetime, hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
SITEMAP = os.path.join(REPO, "sitemap.xml")
STORE = os.path.join(HERE, "data", "page_hashes.json")
SITE = "https://tavion.ie/"
DATE_LD = re.compile(r'"dateModified": "\d{4}-\d{2}-\d{2}"')

def path_for(url):
    rel = url[len(SITE):]
    if rel == "" or rel.endswith("/"): rel += "index.html"
    return os.path.join(REPO, *rel.split("/"))

AD_ID = re.compile(r"pub-\d{16}")

def fingerprint(html):
    # Ignore build dates and the AdSense publisher ID (swapping ad accounts isn't a content change).
    return hashlib.sha1(AD_ID.sub("pub-", DATE_LD.sub('"dateModified": ""', html)).encode("utf-8")).hexdigest()

def run(today=None, quiet=False):
    today = today or datetime.date.today().isoformat()
    store = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {}
    xml = open(SITEMAP, encoding="utf-8").read()
    changed = kept = 0

    def fix(m):
        nonlocal changed, kept
        url, old = m.group(1), m.group(2)
        p = path_for(url)
        if not os.path.exists(p): return m.group(0)
        html = open(p, encoding="utf-8").read()
        h = fingerprint(html)
        rec = store.get(url)
        if rec is None:
            # First time we see this page: trust the date already in the sitemap.
            date = old if old < today or old == today else today
            store[url] = {"h": h, "d": date}
        elif rec["h"] != h:
            store[url] = {"h": h, "d": today}; date = today; changed += 1
        else:
            date = rec["d"]; kept += 1
        # Same date in the page's structured data
        new_html = DATE_LD.sub(f'"dateModified": "{date}"', html)
        if new_html != html:
            with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(new_html)
        return m.group(0).replace(f"<lastmod>{old}</lastmod>", f"<lastmod>{date}</lastmod>")

    xml = re.sub(r"<url><loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", fix, xml)
    with open(SITEMAP, "w", encoding="utf-8", newline="\n") as f: f.write(xml)
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "w", encoding="utf-8", newline="\n") as f: json.dump(store, f, indent=0, sort_keys=True)
    if not quiet: print(f"sitemap dates: {changed} pages changed today, {kept} unchanged")

if __name__ == "__main__":
    run()
