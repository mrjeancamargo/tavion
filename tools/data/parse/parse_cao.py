"""Parse CAO 2027 course lists + 2023-2026 points into one JSON dataset."""
import re, html, json, os, sys, glob, openpyxl
D = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s.replace("<br>", " | ")))).strip()

colleges, courses = {}, {}
for f in sorted(glob.glob(os.path.join(D, "c27", "*.html"))):
    cc = os.path.basename(f)[:2]
    t = open(f, encoding="utf-8", errors="replace").read()
    m = re.search(r"<h2>(.*?)</h2>", t[t.find("maincontent"):])
    colleges[cc] = clean(m.group(1))
    body = t[t.find("course-list"):]
    body = body[:body.find("</ul>")]
    level = None
    for part in re.split(r"(<h4>.*?</h4>|<li class='course-card'>)", body):
        if part.startswith("<h4>"):
            level = 8 if "Level 8" in part else 7
            continue
        m = re.search(r"<a href=\"([^\"]*)\"[^>]*>\s*<span class='course-code'>(\w+)</span></a>&nbsp;<span class='course-title'>(.*)", part, re.S)
        if not m:
            m2 = re.search(r"<span class='course-code'>(\w+)</span>.*?<span class='course-title'>(.*)", part, re.S)
            if not m2: continue
            url, code, rest = "", m2.group(1), m2.group(2)
        else:
            url, code, rest = m.groups()
        tip = re.search(r"title='(.*?)'>", rest, re.S)
        note = ""
        if tip:
            bits = [clean(b) for b in tip.group(1).split("<br>")]
            note = " | ".join(b for b in bits[1:] if b)
        title_html = re.sub(r"<span data-tooltip.*", "", rest, flags=re.S)
        restricted = "(Restricted)" in title_html
        title = clean(title_html.replace("<i>(Restricted)</i>", ""))
        campus = ""
        if " · " in title:
            title, campus = title.rsplit(" · ", 1)
        tags = re.findall(r"\[([^\]]+)\]", title)
        title = re.sub(r"\s*\[[^\]]+\]", "", title).strip()
        courses[code] = {"code": code, "title": title, "college": cc, "level": level, "campus": campus.strip(), "tags": tags,
                         "restricted": restricted, "note": note, "url": url, "points": {}, "category": "", "offered2027": True}

def parse_pts(v):
    if v is None: return None
    s = str(v).strip()
    return s or None

# 2026 from the CAO web lists (R1, R2)
for fn, lvl in (("l8.html", 8), ("l76.html", 7)):
    t = open(os.path.join(D, fn), encoding="utf-8-sig", errors="replace").read()
    for line in html.unescape(t).splitlines():
        m = re.match(r"^([A-Z]{2}\d{3})\s+(.*)$", line)
        if not m: continue
        code = m.group(1)
        left, right = line[:82], line[82:]
        title = left[7:].strip()
        r = right.split()
        r1 = r[0] if len(r) > 0 else None
        r2 = r[1] if len(r) > 1 else None
        c = courses.get(code)
        if not c:
            camp = re.findall(r"\[([^\]]+)\]", title)
            c = courses[code] = {"code": code, "title": re.sub(r"\s*\[[^\]]+\]", "", title).strip(), "college": code[:2], "level": lvl, "campus": "",
                                 "tags": camp, "restricted": False, "note": "", "url": "", "points": {}, "category": "", "offered2027": False}
        c["points"]["2026"] = {"r1": r1, "r2": r2}

for y in (2025, 2024, 2023):
    wb = openpyxl.load_workbook(os.path.join(D, f"CAOPointsCharts{y}.xlsx"), read_only=True)
    ws = wb.worksheets[0]
    hdr = None
    for row in ws.iter_rows(values_only=True):
        if row and row[0] and str(row[0]).startswith("CATEGORY"):
            hdr = [str(h).strip() if h else "" for h in row]; continue
        if not hdr or not row[2]: continue
        d = dict(zip(hdr, row))
        code = str(d["Course Code"]).strip()
        rec = {"r1": parse_pts(d.get("R1 Points")), "r1r": parse_pts(d.get("R1 Random")), "r2": parse_pts(d.get("R2 Points")),
               "eos": parse_pts(d.get("EOS Points")), "mid": parse_pts(d.get("EOS Mid") or d.get("EOS Midpoints")), "test": bool(d.get("Test Interview"))}
        c = courses.get(code)
        if not c:
            c = courses[code] = {"code": code, "title": str(d["Course Title"]).strip(), "college": code[:2], "level": int(d["Course Level"] or 8), "campus": "",
                                 "tags": [], "restricted": False, "note": "", "url": "", "points": {}, "category": "", "offered2027": False}
        c["points"][str(y)] = rec
        if not c["category"] and d.get("CATEGORY (ISCED Description)"): c["category"] = str(d["CATEGORY (ISCED Description)"]).strip()
        if c["level"] in (6, 7) or (c["level"] == 7 and d.get("Course Level")): c["level"] = int(d["Course Level"])
        if c["level"] == 7 and int(d["Course Level"] or 7) == 6: c["level"] = 6

json.dump({"colleges": colleges, "courses": sorted(courses.values(), key=lambda c: c["code"])}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
cs = list(courses.values())
print(len(colleges), "colleges;", len(cs), "courses;", sum(c["offered2027"] for c in cs), "offered 2027;",
      sum("2026" in c["points"] for c in cs if c["offered2027"]), "of those with 2026 pts;", sum(bool(c["category"]) for c in cs if c["offered2027"]), "with category")
