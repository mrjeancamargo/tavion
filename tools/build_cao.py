"""
Builds the CAO Points app (tavion.ie/cao/): calculator + course finder, one page per course (2027 courses),
per college, county, subject area and points band, plus guides (HEAR/DARE, medicine/HPAT, portfolios, QQI FET, dates).
Run from the repo root:   python tools/build_cao.py      (needs Node.js)
Data: tools/data/cao.json (from the CAO 2027 course search and CAO points lists 2023-2026, see tools/data/README.md).
Points rules come from cao/js/cao.js (same engine as the calculator).
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, lis, table, faq_ld, faq_html, key_facts, node, og_image, TODAY

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.normpath(os.path.join(HERE, "..", "cao", "js", "cao.js"))
DATA = json.load(open(os.path.join(HERE, "data", "cao.json"), encoding="utf-8"))
CHECKED = "November 2026"
PY = "2026"   # latest points year
NODE = r"""
const C = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  process.stdout.write(JSON.stringify({ H: C.HIGHER, O: C.ORDINARY, F: C.FOUNDATION, L: C.LCVP, bonus: C.MATHS_BONUS, max: C.MAX_POINTS, med: C.MED,
    res: q.map(x => C.calculate(x.s, x.l)) }));
});
"""
def eng(q=()): return node(ENGINE, NODE, list(q))
E = eng()

SRC = {
    "pts": ("CAO – Points required for entry 2026 (Round 1 and 2)", "https://www.cao.ie/index.php?page=points&p=2026"),
    "pts_l8": ("CAO – Level 8 points 2026", "https://www2.cao.ie/points/l8.php"),
    "pts_l76": ("CAO – Level 7/6 points 2026", "https://www2.cao.ie/points/l76.php"),
    "courses": ("CAO – Course search (2027 courses)", "https://www.cao.ie/courses.php"),
    "grid": ("CAO – Leaving Certificate points calculation grid", "https://www.cao.ie/index.php?page=scoring&s=lcepointsgrid"),
    "dates": ("CAO – Timetable of events 2027", "https://www.cao.ie/index.php?page=timetableevents&bb=importantdates"),
    "access": ("CAO – Access routes (HEAR and DARE)", "https://www.cao.ie/index.php?page=accessroutes"),
    "accesscollege": ("AccessCollege.ie – HEAR and DARE (official)", "https://accesscollege.ie/"),
    "med": ("CAO – Undergraduate entry to medicine 2027 (PDF)", "https://www2.cao.ie/downloads/documents/2027/UGMedEntry2027.pdf"),
    "medpage": ("CAO – Entry to medicine", "https://www.cao.ie/index.php?page=medentry"),
    "fet": ("CAO – QQI FET/FETAC scoring scheme (PDF)", "https://www2.cao.ie/fetac/FETAC_scoring.pdf"),
    "fetpage": ("CAO – QQI FET/FETAC applicants", "https://www.cao.ie/index.php?page=scoring&s=fetac"),
    "tests": ("CAO – Test and interview dates", "https://www.cao.ie/index.php?page=testandinterviews&bb=importantdates"),
    "mature": ("CAO – Mature applicants", "https://www.cao.ie/index.php?page=mature"),
    "ci": ("Citizens Information – Applying for third-level education (CAO)", "https://www.citizensinformation.ie/en/education/third-level-education/applying-to-college/"),
    "grants": ("SUSI – Student grants", "https://susi.ie/"),
}

# ---------- Colleges ----------
# code: (short name, slug, type, home county, town, official website)
COL = {
    "AC": ("American College Dublin", "american-college-dublin", "Private college", "Dublin", "Dublin city centre", "https://www.amcd.ie/"),
    "AD": ("NCAD", "ncad", "College of art and design", "Dublin", "Thomas Street, Dublin 8", "https://www.ncad.ie/"),
    "AU": ("ATU", "atu", "Technological university", "Galway", "Galway, Mayo, Sligo and Donegal", "https://www.atu.ie/"),
    "BY": ("IBAT College Dublin", "ibat", "Private college", "Dublin", "Dublin city centre", "https://www.ibat.ie/"),
    "CK": ("UCC", "ucc", "University", "Cork", "Cork city", "https://www.ucc.ie/"),
    "CM": ("Marino Institute of Education", "marino", "College of education", "Dublin", "Marino, Dublin 9", "https://www.mie.ie/"),
    "CT": ("CCT College Dublin", "cct", "Private college", "Dublin", "Dublin city centre", "https://www.cct.ie/"),
    "DB": ("DBS", "dbs", "Private college", "Dublin", "Dublin city centre", "https://www.dbs.ie/"),
    "DC": ("DCU", "dcu", "University", "Dublin", "Glasnevin and Drumcondra, Dublin", "https://www.dcu.ie/"),
    "DK": ("DkIT", "dkit", "Institute of technology", "Louth", "Dundalk", "https://www.dkit.ie/"),
    "DL": ("IADT", "iadt", "Institute of art, design and technology", "Dublin", "Dún Laoghaire", "https://iadt.ie/"),
    "DN": ("UCD", "ucd", "University", "Dublin", "Belfield, Dublin 4", "https://www.ucd.ie/"),
    "DS": ("Dorset College", "dorset-college", "Private college", "Dublin", "Dublin city centre", "https://www.dorset.ie/"),
    "GB": ("Galway Business School", "galway-business-school", "Private college", "Galway", "Galway city", "https://www.gbs.ie/"),
    "GC": ("Griffith College", "griffith-college", "Private college", "Dublin", "Dublin and Cork", "https://www.griffith.ie/"),
    "GY": ("University of Galway", "university-of-galway", "University", "Galway", "Galway city", "https://www.universityofgalway.ie/"),
    "ID": ("ICD Business School", "icd-business-school", "Private college", "Dublin", "Dublin city centre", "https://www.icd.ie/"),
    "LM": ("UL", "ul", "University", "Limerick", "Castletroy, Limerick", "https://www.ul.ie/"),
    "MH": ("Maynooth University", "maynooth-university", "University", "Kildare", "Maynooth", "https://www.maynoothuniversity.ie/"),
    "MI": ("Mary Immaculate College", "mic", "College of education and liberal arts", "Limerick", "Limerick and Thurles", "https://www.mic.ul.ie/"),
    "MT": ("MTU", "mtu", "Technological university", "Cork", "Cork and Kerry", "https://www.mtu.ie/"),
    "MU": ("St Patrick's Pontifical University", "st-patricks-pontifical-university", "Pontifical university", "Kildare", "Maynooth", "https://www.maynoothcollege.ie/"),
    "NC": ("NCI", "nci", "Private college (not-for-profit)", "Dublin", "IFSC, Dublin 1", "https://www.ncirl.ie/"),
    "RC": ("RCSI", "rcsi", "University of medicine and health sciences", "Dublin", "St Stephen's Green, Dublin 2", "https://www.rcsi.com/"),
    "SC": ("Setanta College", "setanta-college", "Private college (sport and coaching)", "Tipperary", "Thurles and online", "https://www.setantacollege.com/"),
    "SE": ("SETU", "setu", "Technological university", "Waterford", "Waterford, Carlow, Wexford and Kilkenny", "https://www.setu.ie/"),
    "TR": ("Trinity College Dublin", "trinity", "University", "Dublin", "College Green, Dublin 2", "https://www.tcd.ie/"),
    "TU": ("TU Dublin", "tu-dublin", "Technological university", "Dublin", "Grangegorman, Tallaght and Blanchardstown", "https://www.tudublin.ie/"),
    "US": ("TUS", "tus", "Technological university", "Limerick", "Limerick, Athlone, Clonmel, Thurles and Ennis", "https://tus.ie/"),
}
CAMPUS_COUNTY = [("Castlebar", "Mayo"), ("Killybegs", "Donegal"), ("Letterkenny", "Donegal"), ("Letterfrack", "Galway"), ("Mountbellew", "Galway"), ("Sligo", "Sligo"),
                 ("Shannon College", "Clare"), ("Shannon", "Clare"), ("Ennis", "Clare"), ("Thurles", "Tipperary"), ("Clonmel", "Tipperary"), ("Athlone", "Westmeath"),
                 ("Kerry", "Kerry"), ("Carlow", "Carlow"), ("Wexford", "Wexford"), ("Waterford", "Waterford"), ("Botanic", "Dublin"), ("Online", "Online"),
                 ("Galway", "Galway"), ("Limerick", "Limerick"), ("Cork", "Cork"), ("CCAD", "Cork"), ("NMCI", "Cork"), ("Clonakilty", "Cork"), ("Dublin", "Dublin")]

def county_of(c):
    camp = c["campus"]
    for k, v in CAMPUS_COUNTY:
        if k.lower() in camp.lower(): return v
    if c["college"] == "TU": return "Dublin"
    if c["college"] in ("GC",) and not camp: return "Dublin"
    return COL[c["college"]][3]

# ---------- Subject areas ----------
AREAS = collections.OrderedDict([
    ("business", ("Business, accounting and finance", "💼", "Business degrees are the biggest group on the CAO list – from general business and commerce to accounting, finance, marketing, HR and supply chain. Many lead to exemptions from professional exams (ACCA, CPA, Chartered Accountants Ireland), so check the official course page if that matters to you.")),
    ("computing", ("Computing and IT", "💻", "Computer science, software development, cyber security, data science, games and AI. Points range from the 200s at technological universities to the 500s for the most popular university degrees, but the job you end up in often depends more on what you build than where you studied.")),
    ("engineering", ("Engineering and manufacturing", "⚙️", "Civil, mechanical, electrical, biomedical and many more. Most engineering degrees need a minimum grade in Higher Level Maths – usually H4 at universities – so check the entry requirements, not just the points. Common-entry engineering lets you pick a branch after first year.")),
    ("construction", ("Architecture and construction", "🏗️", "Architecture, quantity surveying, construction management, property, planning and the building trades. Architecture courses often ask for a portfolio or test; construction management and surveying are in high demand in Ireland's housing push.")),
    ("health", ("Medicine, nursing and health", "🩺", "Medicine, nursing, pharmacy, physiotherapy, radiography, dentistry and more. Medicine uses the HPAT test as well as points, and many health courses need Garda vetting. Nursing has a separate quota for mature and QQI FET applicants.")),
    ("science", ("Science and maths", "🔬", "Biology, chemistry, physics, environmental science, maths and statistics. Common-entry science (choose your subject after first year) is a popular route with lower points than the specialist degrees.")),
    ("teaching", ("Teaching and education", "🍎", "Primary teaching (B.Ed), second-level teaching with a subject, early childhood and special education. Primary teaching needs minimum grades in Irish, English and Maths as well as points.")),
    ("social-care", ("Social care and childcare", "🤝", "Social care, youth work, early childhood care and social work. These courses usually need Garda vetting and include work placements.")),
    ("social-science", ("Psychology, social science and media", "🧠", "Psychology, sociology, politics, journalism and communications. Psychology degrees are among the higher-points courses; if you miss out, an arts degree with psychology can be a route in.")),
    ("law", ("Law", "⚖️", "Law (LLB), law with a language, business or criminology. A law degree is not required to become a solicitor or barrister in Ireland, but it makes the route shorter.")),
    ("arts", ("Arts, humanities and languages", "📚", "Arts (choose your subjects at registration), history, English, philosophy, languages and international pathways. Arts is one of the most flexible degrees on the list, often with a year abroad.")),
    ("creative", ("Art, design, music and film", "🎨", "Fine art, design, animation, music, film, photography and drama. Many of these courses use a portfolio or audition, and points over 625 on the CAO list mean the portfolio is part of the score.")),
    ("hospitality-sport", ("Sport, hospitality and tourism", "🏅", "Sport science, coaching, physical education, culinary arts, hotel management and tourism. Practical courses with strong links to employers.")),
    ("agriculture", ("Agriculture, food and veterinary", "🌾", "Agriculture, agri-business, food science, horticulture, forestry and veterinary medicine. Veterinary medicine at UCD is one of the highest-points courses in the country.")),
])
ISCED = {"Business and administration": "business", "Information and Communication Technologies (ICTs)": "computing", "Engineering and engineering trades": "engineering",
         "Manufacturing and processing": "engineering", "Architecture and construction": "construction", "Health": "health", "Biological and related sciences": "science",
         "Physical sciences": "science", "Mathematics and statistics": "science", "Environment": "science",
         "Interdisciplinary programmes and qualifications involving natural sciences, Mathematics and statistics": "science", "Education": "teaching", "Welfare": "social-care",
         "Social and behavioural sciences": "social-science", "Journalism and information": "social-science", "Law": "law", "Humanities (except languages)": "arts",
         "Languages": "arts", "Arts": "creative", "Personal services": "hospitality-sport", "Transport services": "hospitality-sport", "Hygiene and occupational health services": "health",
         "Agriculture": "agriculture", "Forestry": "agriculture", "Veterinary": "agriculture",
         "Interdisciplinary programmes and qualifications involving agriculture, forestry and veterinary": "agriculture"}
KEYWORDS = [("teach|education|b\\.?ed", "teaching"), ("nurs|midwif|medic|pharm|physio|health|radiog|dental|therap|paramedic", "health"), ("law|llb", "law"),
            ("comput|software|data|cyber|digital|games|\\bit\\b|ai\\b|artificial", "computing"), ("engineer|mechatron|manufactur|robot", "engineering"),
            ("architect|construct|survey|built|property|planning", "construction"), ("music|art|design|film|animation|media|photo|drama|theatre|fashion", "creative"),
            ("sport|coach|culinary|hotel|hospitality|tourism|fitness|beauty|exercise", "hospitality-sport"), ("agri|food|horticult|equine|forest|vet", "agriculture"),
            ("psycholog|social science|sociolog|politic|journal|communica", "social-science"), ("social care|childhood|youth|community", "social-care"),
            ("science|biolog|chemi|physic|math|environment", "science"), ("business|account|financ|market|commerce|management|economic", "business"),
            ("arts|history|english|language|irish|philosoph|theolog", "arts")]

def area_of(c):
    if c["category"] in ISCED:
        a = ISCED[c["category"]]
        if a == "creative" and re.search(r"\b(arts|humanities|liberal)\b", c["title"], re.I) and not re.search(r"design|music|fine|art and|animation|portfolio", c["title"], re.I): return "arts"
        return a
    t = c["title"].lower()
    for pat, a in KEYWORDS:
        if re.search(pat, t): return a
    return "arts"

def tc(s): return " ".join(w if w in ("and", "IT") else w[0].upper() + w[1:] for w in s.split(" "))

def low(s): return s.lower().replace(" it", " IT")

def slugify(s):
    s = s.lower().replace("&", " and ").replace("`", "").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def pp(s):
    """Parse a CAO points string -> dict(value, random, test, aqa)."""
    if s in (None, ""): return None
    s = str(s).strip()
    m = re.search(r"(\d{2,4})", s)
    return {"raw": s, "value": int(m.group(1)) if m else None, "random": "*" in s, "test": "#" in s, "aqa": "AQA" in s.upper()}

def show(s):
    p = pp(s)
    if not p: return "–"
    if p["aqa"]: return "AQA"
    return s.replace("#", "#").strip()

def latest(c):
    """Most recent Round 1 points with its year."""
    for y in ("2026", "2025", "2024", "2023"):
        r = c["points"].get(y, {})
        if r.get("r1"): return y, pp(r["r1"])
    return None, None

LEVELNAME = {8: "Level 8 honours degree", 7: "Level 7 ordinary degree", 6: "Level 6 higher certificate"}
def level_name(c): return LEVELNAME.get(c["level"], "Level 7/6")

# ---------- Prepare course records ----------
COURSES = []
for c in DATA["courses"]:
    if not c["offered2027"]: continue
    c = dict(c)
    c["area"] = area_of(c); c["county"] = county_of(c)
    c["slug"] = f'{c["code"].lower()}-{slugify(c["title"])[:60].strip("-")}-{COL[c["college"]][1]}.html'
    c["note"] = " | ".join(x for x in c["note"].split(" | ") if x and x.strip() != c["title"] and not x.endswith(" Campus") and x != c["campus"])
    c["ly"], c["lp"] = latest(c)
    COURSES.append(c)
BY_CODE = {c["code"]: c for c in COURSES}
NONPORT = [c for c in COURSES if c["lp"] and c["lp"]["value"] and c["lp"]["value"] <= 625 and not c["lp"]["test"]]  # Leaving Cert points only

app = App("cao", "CAO Points", "🎓", None, "#4338ca",
          [("./", "Calculator"), ("points-table.html", "Points table"), ("colleges.html", "Colleges"), ("subjects.html", "Courses by subject"),
           ("courses-by-points.html", "By points"), ("dates-2027.html", "Dates 2027"), ("hear-dare.html", "HEAR & DARE"), ("faq.html", "FAQ")],
          ('<a href="./">CAO points calculator</a><a href="points-table.html">CAO points table</a><a href="all-courses.html">All 2027 courses</a><a href="colleges.html">Colleges</a>'
           '<a href="counties.html">By county</a><a href="subjects.html">By subject</a><a href="courses-by-points.html">By points</a><a href="points-changes-2026.html">2026 points changes</a>'
           '<a href="dates-2027.html">CAO dates 2027</a><a href="hear-dare.html">HEAR &amp; DARE</a><a href="medicine-hpat.html">Medicine &amp; HPAT</a><a href="portfolio-courses.html">Portfolio courses</a>'
           '<a href="qqi-fet.html">QQI FET points</a><a href="faq.html">FAQ</a>'),
          SRC, None, "Free CAO points calculator – see your points and the courses they could get you:", "Doing the Leaving Cert in 2027? Send this to a friend (or a parent).", "cao",
          f"Points and course lists from the CAO, checked {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>, not affiliated with the CAO or any college. "
          "Last year's points are a guide only – they change every year with demand. Always check entry requirements on the college's own course page and in the CAO Handbook.")
CROSS = ["salary", "rent", "welfare", "pension"]

def course_link(c, text=None):
    return f'<a href="{c["slug"]}">{text or c["code"] + " " + c["title"]}</a>'

def cut_cell(c, y=PY, k="r1"):
    return show(c["points"].get(y, {}).get(k))

def course_rows(cs, college=True):
    rows = []
    for c in cs:
        r = [f'<span class="code">{c["code"]}</span>', course_link(c, c["title"])]
        if college: r.append(COL[c["college"]][0] + (f' · {c["campus"]}' if c["campus"] else ""))
        r += [str(c["level"]), cut_cell(c), cut_cell(c, "2025")]
        rows.append(r)
    head = ["Code", "Course"] + (["College"] if college else []) + ["Level", "2026", "2025"]
    return head, rows

def ctable(cs, college=True):
    h, r = course_rows(cs, college)
    return table(h, r)

def sort_pts(cs, rev=True):
    return sorted(cs, key=lambda c: (c["lp"]["value"] if c["lp"] and c["lp"]["value"] else (0 if not rev else -1)), reverse=rev)

POINTS_NOTE = ('<p class="muted small">Round 1 points. <strong>*</strong> not everyone on this score got a place (random selection) · <strong>#</strong> test, interview, portfolio or audition – '
               'scores over 625 include the portfolio or HPAT · <strong>AQA</strong> all qualified applicants got an offer · – no points (new course or no offers in that round).</p>')

# ---------- Compact data for the calculator ----------
def write_json():
    rows = [[c["code"], c["title"], c["college"], c["level"], c["county"], c["area"], c["points"].get("2026", {}).get("r1") or "",
             c["points"].get("2025", {}).get("r1") or "", "".join(sorted({"P" if any(t in ("Portfolio", "Audition", "Interview") for t in c["tags"]) else "",
             "M" if any("HPAT" in t for t in c["tags"]) else "", "R" if c["restricted"] else ""})), c["slug"]] for c in COURSES]
    meta = {"colleges": {k: v[0] for k, v in COL.items()}, "areas": {k: v[0] for k, v in AREAS.items()}, "year": PY, "checked": CHECKED}
    os.makedirs(os.path.join(app.root, "data"), exist_ok=True)
    with open(os.path.join(app.root, "data", "courses.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": meta, "courses": rows}, f, ensure_ascii=False, separators=(",", ":"))

# ---------- Calculator (index) ----------
GRADES = [f"H{i}" for i in range(1, 9)] + [f"O{i}" for i in range(1, 9)] + ["F1", "F2"]
def build_index():
    ex = eng([{"s": [{"subject": "English", "grade": "H3"}, {"subject": "Irish", "grade": "H4"}, {"subject": "Mathematics", "grade": "H5"}, {"subject": "French", "grade": "O2"},
                     {"subject": "Biology", "grade": "H4"}, {"subject": "Business", "grade": "H3"}, {"subject": "Geography", "grade": "H5"}], "l": ""}])["res"][0]
    body = f"""<p class="lead">Enter your Leaving Cert grades (or the grades you're aiming for) to see your CAO points – maths bonus and LCVP included – and the 2027 courses that last year's points say you could get. Free, no sign-up.</p>
<ul class="facts"><li>H1 = 100 · O1 = 56</li><li>+25 for Higher Maths H6+</li><li>{len(COURSES):,} courses for 2027</li></ul>
<form id="caoForm" class="card" novalidate>
  <label class="big-label">Your subjects and grades</label>
  <p class="muted small" style="margin:0 0 10px">Your best six count. Add a seventh or eighth – we'll pick the best six for you.</p>
  <div id="subjects"></div>
  <div class="btn-row" style="margin-top:4px"><button type="button" class="btn small-btn" id="addSubj">+ Add a subject</button></div>
  <label for="lcvp" style="margin-top:12px">LCVP Link Modules (if you took them)
    <select id="lcvp"><option value="">I didn't do LCVP</option><option>Distinction</option><option>Merit</option><option>Pass</option></select></label>
  <label class="check"><input type="checkbox" id="found"><span>Count Foundation Level grades (F1 = 20, F2 = 12) <small>– only some colleges do</small></span></label>
  <div class="btn-row"><button type="submit" class="btn primary">Show my points &amp; courses</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your phone. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<div class="ad" data-slot="result"></div>
<h2>How CAO points work</h2>
<div class="card"><ol class="steps">
<li><strong>Your best six subjects count</strong>, from one sitting of the Leaving Cert. Maximum 625.</li>
<li><strong>Higher Level</strong>: H1 100, H2 88, H3 77, H4 66, H5 56, H6 46, H7 37. <strong>Ordinary</strong>: O1 56, O2 46, O3 37, O4 28, O5 20, O6 12.</li>
<li><strong>Higher Level Maths</strong>: +25 bonus points for H6 or above, so a H6 is worth 71.</li>
<li><strong>LCVP</strong> Link Modules can count as a sixth subject: Distinction 66, Merit 46, Pass 28.</li>
<li><strong>Points aren't everything</strong>: you must also meet the course's minimum entry requirements (for example a H4 in Maths for engineering).</li>
</ol></div>
<p>Example: H3 English, H4 Irish, H5 Maths, O2 French, H4 Biology, H3 Business, H5 Geography = <strong>{ex['total']} points</strong> (best six, including the {ex['bonus']}-point maths bonus). <a href="points-table.html">Full points table →</a></p>
<h2>Find courses</h2>
<div class="chip-list">{"".join(f'<a href="subject-{k}.html">{v[1]} {v[0]}</a>' for k, v in AREAS.items())}</div>
<div class="chip-list">{"".join(f'<a href="courses-with-{n}-points.html">{n} points</a>' for n in BANDS)}</div>
<div class="cta"><h2>CAO closes 1 February 2027</h2><p>Apply by 20 January 2027 for the €35 discounted fee.</p><a class="btn" href="dates-2027.html">All 2027 CAO dates</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "CAO Points Calculator Ireland", "url": app.BASE, "applicationCategory": "EducationalApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": "Calculate Leaving Certificate CAO points (with the Higher Level Maths bonus and LCVP) and see which 2027 CAO courses your points could get, using 2026 points."}
    faqs = [("How are CAO points calculated?", "Your best six Leaving Cert subjects from one sitting count. H1 is worth 100 points and O1 56. Higher Level Maths at H6 or above gets 25 bonus points, so the maximum is 625."),
            ("How many points do I need for college?", f"It depends on the course: in 2026 Round 1 cut-offs ranged from all qualified applicants (no minimum points) to {max(c['lp']['value'] for c in NONPORT)} for courses without a test or portfolio. Enter your grades to see courses within reach.")]
    app.page("index.html", "CAO Points Calculator 2027 – Your Points & the Courses They Get You | Ireland",
             "Free CAO points calculator for the Leaving Cert 2027: best six subjects, maths bonus and LCVP, then see 10–15 courses your points could get using 2026 CAO points.",
             body, active="Calculator", jsonld=[ld, faq_ld(faqs)], slot="calculator", scripts=["js/cao.js", "js/calc.js"], h1="CAO points calculator 2027",
             sources=("grid", "pts", "courses"), cross=CROSS, priority="1.0",
             share_text="Free CAO points calculator – put in your grades and see which courses you could get:")

def build_points_table():
    H, O = E["H"], E["O"]
    rows = []
    for i in range(1, 9):
        h, o = f"H{i}", f"O{i}"
        hm = H[h] + (E["bonus"] if H[h] >= H["H6"] else 0)
        rows.append([h, str(H[h]), str(hm), o, str(O[o])])
    exs = [("All H1s, including Higher Maths", [("English", "H1"), ("Irish", "H1"), ("Mathematics", "H1"), ("French", "H1"), ("Biology", "H1"), ("Chemistry", "H1")], ""),
           ("Mixed Higher and Ordinary", [("English", "H4"), ("Irish", "O2"), ("Mathematics", "O1"), ("French", "H5"), ("Business", "H4"), ("Geography", "H5")], ""),
           ("Higher Maths H6 instead of Ordinary O1", [("English", "H4"), ("Irish", "O2"), ("Mathematics", "H6"), ("French", "H5"), ("Business", "H4"), ("Geography", "H5")], ""),
           ("Five subjects + LCVP Distinction", [("English", "H5"), ("Irish", "O3"), ("Mathematics", "O2"), ("Business", "H5"), ("Home Economics", "H4")], "Distinction")]
    res = eng([{"s": [{"subject": s, "grade": g} for s, g in e[1]], "l": e[2]} for e in exs])["res"]
    exrows = [[e[0], ", ".join(f"{g} {s}" for s, g in e[1]) + (f", LCVP {e[2]}" if e[2] else ""), f"<strong>{r['total']}</strong>"] for e, r in zip(exs, res)]
    body = f"""<p class="lead">How many CAO points is each Leaving Cert grade worth? The official points table, the Higher Maths bonus, LCVP and Foundation Level.</p>
<p class="updated">CAO points grid · Checked {CHECKED}</p>
{key_facts(["Your <strong>best six</strong> subjects from <strong>one sitting</strong> of the Leaving Cert count. The maximum is <strong>625</strong>.",
            "<strong>H1 = 100</strong> points, down to H7 = 37. H8 = 0.", "<strong>O1 = 56</strong> – the same as a H5. O6 = 12; O7 and O8 = 0.",
            f"<strong>Higher Level Maths bonus:</strong> +{E['bonus']} for H6 or better. A H6 in Higher Maths (71) beats an O1 (56).",
            "<strong>LCVP Link Modules</strong> can replace a sixth subject: Distinction 66, Merit 46, Pass 28.",
            "<strong>Foundation Level</strong> Maths or Irish: F1 = 20, F2 = 12 – but only some colleges award these points."])}
{table(["Higher", "Points", "Higher Maths", "Ordinary", "Points"], rows)}
<div class="ad" data-slot="content"></div>
<h2>Worked examples</h2>
{table(["Example", "Grades", "Points"], exrows)}
<h2>Is Higher Maths worth the risk?</h2>
<p>Almost always, if you can pass it. A H7 in Higher Maths (37) is worth less than an O1 (56), but a H6 is worth 71 because of the bonus. Moving from O1 to H6 adds {res[2]['total'] - res[1]['total']} points in the example above. Many courses (engineering, some science and computing) also require a minimum grade in Higher Maths.</p>
<h2>Things that don't add points</h2>
{lis(["Repeating subjects in a second sitting – only one sitting counts (but colleges may accept matriculation requirements from different sittings).", "Transition Year and Junior Cycle results.", "Leaving Cert Applied – it doesn't qualify you for CAO points (a QQI FET course is a common route on).", "Extra subjects beyond six – only your best six count."])}
<p>Portfolios, auditions, interviews and the HPAT are scored separately by some courses – see <a href="portfolio-courses.html">portfolio and audition courses</a> and <a href="medicine-hpat.html">medicine and the HPAT</a>.</p>
<div class="cta"><h2>Work out your points</h2><p>Enter your grades and see the courses within reach.</p><a class="btn" href="./">Open the calculator</a></div>"""
    faqs = [("How many points is a H1?", "100. A H1 in Higher Level Maths is worth 125 with the bonus."), ("How many points is an O1?", "56 – the same as a H5."),
            ("Does a H7 in Higher Maths get the bonus?", "No. The 25-point bonus is for H6 and above, so a H7 gets 37 points."), ("What are the maximum CAO points?", "625: six H1s (600) plus the 25-point maths bonus.")]
    app.page("points-table.html", "CAO Points Table 2027 – Points for Every Leaving Cert Grade (H1–H8, O1–O8)",
             "Official CAO points: H1 100, H2 88, H3 77, H4 66, H5 56, H6 46, H7 37; O1 56 to O6 12. Higher Maths +25 bonus, LCVP 66/46/28, Foundation F1 20. With worked examples.",
             body, active="Points table", jsonld=[faq_ld(faqs)], crumbs=[("CAO points", "./"), ("Points table", None)], h1="CAO points table", sources=("grid",), cross=CROSS, priority="0.9")

# ---------- Course pages ----------
LEVEL8 = sorted(c["lp"]["value"] for c in NONPORT if c["level"] == 8)
def pct_below(v):
    import bisect
    return round(bisect.bisect_left(LEVEL8, v) / len(LEVEL8) * 100)

def bars(c):
    items = []
    for y in ("2023", "2024", "2025", "2026"):
        p = pp(c["points"].get(y, {}).get("r1"))
        items.append((y, p))
    vals = [p["value"] for _, p in items if p and p["value"]]
    if len(vals) < 2: return ""
    top = max(vals)
    return '<div class="card"><div class="tl">Round 1 points, 2023–2026</div><div class="bars">' + "".join(
        f'<div><b>{p["raw"] if p else "–"}</b><i style="height:{(p["value"] / top * 100) if p and p["value"] else 2:.0f}%"></i><span>{y}</span></div>' for y, p in items) + "</div></div>"

def entry_notes(c):
    n = []
    for t in c["tags"]:
        if t == "Portfolio": n.append("You must submit a <strong>portfolio</strong> – for many art and design courses it's scored and added to (or replaces) your points.")
        elif t == "Audition": n.append("There's an <strong>audition</strong> as part of entry.")
        elif t == "Interview": n.append("There's an <strong>interview</strong> as part of entry.")
        elif "HPAT" in t: n.append(f"You must sit the <strong>HPAT-Ireland</strong> test (12–15 February 2027). From 2027 your Leaving Cert points count in full and HPAT is weighted to a maximum of {E['med']['hpatMax']}. <a href='medicine-hpat.html'>How medicine entry works →</a>")
        elif "GAMSAT" in t: n.append("Graduate entry – you need a degree and the <strong>GAMSAT</strong> test.")
        else: n.append(t)
    if c["restricted"]: n.append("This is a <strong>restricted application</strong> course: it must be on your CAO list by <strong>1 February 2027</strong> (you can't add it later with a change of mind).")
    for x in c["note"].split(" | "):
        if x: n.append(x.replace("`", "'"))
    return n

def similar(c, k=8):
    same = [x for x in COURSES if x["area"] == c["area"] and x["code"] != c["code"] and x["lp"] and x["lp"]["value"] and x["lp"]["value"] <= 625]
    v = c["lp"]["value"] if c["lp"] and c["lp"]["value"] and c["lp"]["value"] <= 625 else None
    if v is None: return sorted(same, key=lambda x: -x["lp"]["value"])[:k]
    return sorted(same, key=lambda x: abs(x["lp"]["value"] - v))[:k]

def build_course_pages():
    for c in COURSES:
        col = COL[c["college"]]
        y, lp = c["ly"], c["lp"]
        p26 = c["points"].get("2026", {}); p25 = c["points"].get("2025", {})
        where = c["campus"] or col[4]
        facts = [f"<strong>{c['code']} {c['title']}</strong> is a {level_name(c)} at <strong>{DATA['colleges'][c['college']]}</strong> ({where}, Co. {c['county']})." if c["county"] != "Online" else
                 f"<strong>{c['code']} {c['title']}</strong> is a {level_name(c)} at <strong>{DATA['colleges'][c['college']]}</strong>, taught online."]
        a, b = pp(p26.get("r1")), pp(p25.get("r1"))
        if a and a["value"] and not a["aqa"]:
            s = f"In 2026 the Round 1 cut-off was <strong>{p26['r1']} points</strong>"
            if b and b["value"] and not b["aqa"]:
                d = a["value"] - b["value"]
                s += f", {'up' if d > 0 else 'down'} {abs(d)} on 2025 ({p25['r1']})" if d else ", the same as 2025"
            s += "."
            if a["random"]: s += " Not everyone on that score got a place (random selection)."
            facts.append(s)
            if p26.get("r2"): facts.append(f"It fell to <strong>{p26['r2']}</strong> in Round 2.")
            if a["value"] <= 625 and c["level"] == 8: facts.append(f"That's higher than about <strong>{pct_below(a['value'])}%</strong> of Level 8 courses on the CAO list.")
        elif a and a["aqa"]:
            facts.append("In 2026 <strong>all qualified applicants</strong> got an offer – if you met the minimum entry requirements, you got a place.")
        elif "2026" not in c["points"]:
            facts.append("There are no 2026 points for this course – it may be new for 2027 or had no Round 1 offers." + (f" Latest points: {lp['raw']} ({y})." if lp else ""))
        if p25.get("mid"): facts.append(f"Half of those offered a place in 2025 had <strong>{p25['mid']}</strong> points or more (the mid-point).")
        if lp and lp["value"] and lp["value"] > 625: facts.append("Scores above 625 mean a test, portfolio or HPAT is added to the Leaving Cert points – they can't be compared directly with your Leaving Cert points.")
        notes = entry_notes(c)
        hist = []
        for yy in ("2026", "2025", "2024", "2023"):
            r = c["points"].get(yy)
            if r: hist.append([yy, show(r.get("r1")), show(r.get("r2")), show(r.get("eos")) if yy != "2026" else "–", show(r.get("mid")) if yy != "2026" else "–"])
        sim = similar(c)
        same_col = [x for x in COURSES if x["college"] == c["college"] and x["area"] == c["area"] and x["code"] != c["code"]][:8]
        lower = [x for x in sim if lp and lp["value"] and x["lp"]["value"] < lp["value"] - 20][:4]
        cv = lp["value"] if lp and lp["value"] and lp["value"] <= 625 else ""
        mini = (f'<div class="card"><div class="tl">Will your points get you in?</div><form class="mini-check" id="mini" data-cut="{cv}" data-code="{c["code"]}" onsubmit="return false">'
                f'<input type="number" id="miniPts" inputmode="numeric" min="0" max="625" placeholder="Your points" aria-label="Your points"><button class="btn primary" type="submit">Check</button>'
                f'<a class="small" href="./">Don\'t know your points? Work them out →</a></form><div id="miniOut" aria-live="polite"></div></div>') if cv else ""
        official = f'<a class="btn primary" href="{c["url"]}" target="_blank" rel="noopener" data-track="official_course" data-label="{c["code"]}">Official course page ({col[0]}) ↗</a>' if c["url"] else ""
        area = AREAS[c["area"]]
        body = f"""<p class="lead">CAO points for {c['code']} {c['title']} at {col[0]}: 2026 cut-off, the trend since 2023 and what you need for 2027 entry.</p>
<p class="updated">CAO points {PY} · 2027 course list · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="hero-num"><div><span class="tl">2026 Round 1</span><strong>{show(p26.get('r1'))}</strong><span class="muted">points</span></div><div><span class="tl">2025 Round 1</span><strong>{show(p25.get('r1'))}</strong><span class="muted">points</span></div></div>
{mini}
<div class="btn-row">{official}<a class="btn" href="college-{col[1]}.html">All {col[0]} courses</a></div>
{('<h2>Entry requirements to know about</h2>' + lis(notes)) if notes else ''}
<div class="ad" data-slot="content"></div>
<h2>{c['code']} points history</h2>
{bars(c)}
{table(["Year", "Round 1", "Round 2", "End of season", "Mid-point"], hist) if hist else '<p>No points history yet.</p>'}
{POINTS_NOTE}
<h2>Similar {low(area[0])} courses</h2>
<p>Courses in the same area with similar points – good choices to put around {c['code']} on your CAO list.</p>
{ctable(sim)}
{('<h2>Lower-points routes in</h2><p>If you miss out, these related courses needed fewer points in 2026. Many Level 7 and 6 courses let you move on to a Level 8 degree.</p>' + ctable(lower)) if lower else ''}
{('<h2>More ' + low(area[0]) + ' at ' + col[0] + '</h2>' + ctable(same_col, college=False)) if same_col else ''}
<div class="cta"><h2>See every course your points could get</h2><p>Enter your grades – we'll list 10–15 courses within reach.</p><a class="btn" href="./">Open the CAO calculator</a></div>
<div class="chip-list"><a href="subject-{c['area']}.html">{area[1]} All {low(area[0])}</a><a href="county-{slugify(c['county'])}.html">Courses in {c['county']}</a><a href="college-{col[1]}.html">{col[0]}</a><a href="dates-2027.html">CAO dates 2027</a></div>"""
        title = f"{c['code']} {c['title']} – {col[0]} CAO Points 2026" + (f": {show(p26.get('r1'))}" if p26.get("r1") else "")
        desc = (f"CAO points for {c['code']} {c['title']} at {DATA['colleges'][c['college']]}: {show(p26.get('r1'))} points in 2026 Round 1"
                + (f", {show(p25.get('r1'))} in 2025" if p25.get("r1") else "") + f". {level_name(c)}, {c['county']}. Entry requirements, points history and similar courses for 2027.")
        course_ld = {"@context": "https://schema.org", "@type": "Course", "name": c["title"], "courseCode": c["code"], "description": strip_html(facts[0]),
                     "educationalCredentialAwarded": level_name(c), "inLanguage": "en", "url": app.BASE + c["slug"],
                     "provider": {"@type": "CollegeOrUniversity", "name": DATA["colleges"][c["college"]], "sameAs": col[5]},
                     "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online" if c["county"] == "Online" else "onsite", "location": where + ", Ireland"},
                     "offers": {"@type": "Offer", "category": "EU student (free fees scheme applies to eligible students)"}}
        if c["url"]: course_ld["sameAs"] = c["url"]
        faqs = [(f"How many points do you need for {c['code']} {c['title']}?",
                 (f"{show(p26.get('r1'))} points in 2026 Round 1" + (f" ({show(p25.get('r1'))} in 2025)" if p25.get("r1") else "") + ". Points for 2027 will depend on demand and are set when offers are made in August 2027.") if p26.get("r1") else "There were no 2026 Round 1 points for this course. Check the official course page for entry requirements."),
                (f"Where is {c['title']} ({c['code']}) taught?", f"{DATA['colleges'][c['college']]}, {where}.")]
        if notes: faqs.append((f"Does {c['code']} need a portfolio, test or interview?", strip_html(" ".join(notes))))
        srcs = ["pts_l8" if c["level"] == 8 else "pts_l76", "courses"]
        if c["url"]:
            app.SRC["off_" + c["code"]] = (f"{col[0]} – official {c['title']} course page", c["url"]); srcs.append("off_" + c["code"])
        app.page(c["slug"], title, desc, body, active=None, jsonld=[course_ld, faq_ld(faqs)],
                 crumbs=[("CAO points", "./"), (col[0], f"college-{col[1]}.html"), (c["code"], None)], h1=f"{c['code']} {c['title']} – CAO points",
                 sources=srcs, cross=CROSS, priority="0.6",
                 share_text=f"{c['code']} {c['title']} ({col[0]}) needed {show(p26.get('r1'))} CAO points in 2026 – check your points here:")

def strip_html(s): return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&")

# ---------- College, county, subject, points pages ----------
def summary_stats(cs):
    vals = [c["lp"]["value"] for c in cs if c["lp"] and c["lp"]["value"] and c["lp"]["value"] <= 625 and not c["lp"]["aqa"]]
    lv = collections.Counter(c["level"] for c in cs)
    return vals, lv

def build_colleges():
    rows = []
    for cc, col in sorted(COL.items(), key=lambda kv: kv[1][0]):
        cs = sorted([c for c in COURSES if c["college"] == cc], key=lambda c: c["code"])
        if not cs: continue
        vals, lv = summary_stats(cs)
        full = DATA["colleges"][cc]
        rows.append([f'<a href="college-{col[1]}.html">{full}</a>', col[2], col[4], str(len(cs)), f"{min(vals)}–{max(vals)}" if vals else "–"])
        campuses = sorted({c["campus"] for c in cs if c["campus"]})
        areas = collections.Counter(c["area"] for c in cs)
        top = sort_pts([c for c in cs if c["lp"] and c["lp"]["value"] and c["lp"]["value"] <= 625])[:5]
        low = sort_pts([c for c in cs if c["lp"] and c["lp"]["value"] and c["lp"]["value"] <= 625], rev=False)[:5]
        facts = [f"<strong>{full}</strong> is a {col[2].lower()} in {col[4]}.", f"It offers <strong>{len(cs)} CAO courses</strong> for 2027: " + ", ".join(f"{n} at Level {l}" for l, n in sorted(lv.items(), reverse=True)) + "."]
        if vals: facts.append(f"2026 Round 1 points ranged from <strong>{min(vals)}</strong> to <strong>{max(vals)}</strong> (excluding portfolio and HPAT scores).")
        if top: facts.append(f"Highest points: {course_link(top[0])} ({top[0]['lp']['raw']}).")
        if campuses: facts.append("Campuses on the CAO list: " + ", ".join(campuses).replace("`", "'") + ".")
        facts.append("Biggest areas: " + ", ".join(f'<a href="subject-{a}.html">{AREAS[a][0]}</a> ({n})' for a, n in areas.most_common(3)) + ".")
        groups = "".join(f'<h3>{AREAS[a][1]} {AREAS[a][0]}</h3>' + ctable([c for c in cs if c["area"] == a], college=False) for a in AREAS if any(c["area"] == a for c in cs))
        app.SRC["col_" + cc] = (f"{full} – official website", col[5])
        body = f"""<p class="lead">Every {full} course on the CAO for 2027, with 2026 and 2025 Round 1 points and links to each official course page.</p>
<p class="updated">CAO 2027 course list · Points {PY} · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="btn-row"><a class="btn primary" href="{col[5]}" target="_blank" rel="noopener" data-track="official_college" data-label="{cc}">{col[0]} website ↗</a><a class="btn" href="./">Check my points</a></div>
<div class="ad" data-slot="content"></div>
<h2>{col[0]} courses by area</h2>
{groups}
{POINTS_NOTE}
{('<h2>Lowest-points courses at ' + col[0] + '</h2>' + ctable(low, college=False)) if low else ''}
<div class="cta"><h2>Could you get into {col[0]}?</h2><p>Enter your grades to see which courses are within reach.</p><a class="btn" href="./">Open the calculator</a></div>"""
        ld = {"@context": "https://schema.org", "@type": "CollegeOrUniversity", "name": full, "url": col[5], "address": {"@type": "PostalAddress", "addressLocality": col[4], "addressRegion": "Co. " + col[3], "addressCountry": "IE"}}
        app.page(f"college-{col[1]}.html", f"{col[0]} CAO Points 2026 – All {len(cs)} Courses for 2027" if col[0] != full else f"{full} CAO Points 2026 – All {len(cs)} Courses for 2027",
                 f"All {len(cs)} {full} CAO courses for 2027 with 2026 and 2025 points" + (f" ({min(vals)} to {max(vals)})" if vals else "") + ", campuses, entry notes and official course links.",
                 body, active="Colleges", jsonld=[ld], crumbs=[("CAO points", "./"), ("Colleges", "colleges.html"), (col[0], None)], h1=f"{full}: CAO courses and points",
                 sources=("courses", "pts", "col_" + cc), cross=CROSS, priority="0.8")
    body = f"""<p class="lead">All {len(rows)} colleges taking applications through the CAO for 2027, with how many courses each offers and their points range.</p>
<p class="updated">Checked {CHECKED}</p>
{table(["College", "Type", "Where", "Courses", "2026 points"], rows)}
<div class="ad" data-slot="content"></div>
<p>Looking by location instead? <a href="counties.html">Courses by county →</a></p>"""
    app.page("colleges.html", "CAO Colleges 2027 – Every University & College in Ireland with Points",
             "All 29 CAO colleges for 2027 – universities, technological universities and private colleges – with number of courses, 2026 points range and links.",
             body, active="Colleges", crumbs=[("CAO points", "./"), ("Colleges", None)], h1="CAO colleges for 2027", sources=("courses", "pts"), cross=CROSS, priority="0.9")

def build_counties():
    by = collections.defaultdict(list)
    for c in COURSES: by[c["county"]].append(c)
    rows = []
    for county, cs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        slug = slugify(county)
        vals, lv = summary_stats(cs)
        cols = collections.Counter(c["college"] for c in cs)
        rows.append([f'<a href="county-{slug}.html">{county}</a>', str(len(cs)), ", ".join(COL[k][0] for k, _ in cols.most_common())])
        nm = "online" if county == "Online" else f"in {county}"
        facts = [f"There are <strong>{len(cs)} CAO courses {nm}</strong> for 2027, at " + ", ".join(f'<a href="college-{COL[k][1]}.html">{COL[k][0]}</a> ({n})' for k, n in cols.most_common()) + "."]
        if vals: facts.append(f"2026 Round 1 points ranged from <strong>{min(vals)}</strong> to <strong>{max(vals)}</strong>.")
        facts.append(", ".join(f"{n} at Level {l}" for l, n in sorted(lv.items(), reverse=True)) + ".")
        groups = "".join(f'<h3>{AREAS[a][1]} {AREAS[a][0]}</h3>' + ctable(sort_pts([c for c in cs if c["area"] == a])) for a in AREAS if any(c["area"] == a for c in cs))
        rent = ' Moving for college? Check <a href="../rent/" data-track="cross_app" data-label="rent_from_cao">what your landlord can and can\'t do with your rent</a>.' if county != "Online" else ""
        body = f"""<p class="lead">Every CAO course {nm} for 2027, by subject area, with 2026 and 2025 points.{rent}</p>
<p class="updated">Points {PY} · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="ad" data-slot="content"></div>
{groups}
{POINTS_NOTE}
<div class="cta"><h2>Which of these could you get?</h2><p>Enter your grades and filter by {county}.</p><a class="btn" href="./?county={county}">Open the calculator</a></div>"""
        app.page(f"county-{slug}.html", f"CAO Courses {'Online' if county == 'Online' else 'in ' + county} 2027 – {len(cs)} Courses & Points",
                 f"All {len(cs)} CAO courses {nm} for 2027 with 2026 Round 1 points, colleges and campuses, grouped by subject.",
                 body, crumbs=[("CAO points", "./"), ("Counties", "counties.html"), (county, None)], h1=f"CAO courses {nm}", sources=("courses", "pts"), cross=CROSS, priority="0.7")
    body = f"""<p class="lead">Want to study near home – or somewhere new? CAO courses for 2027 by county.</p>
{table(["County", "Courses", "Colleges"], rows)}
<div class="ad" data-slot="content"></div>"""
    app.page("counties.html", "CAO Courses by County 2027 – Study in Dublin, Cork, Galway, Limerick & More",
             "CAO courses for 2027 by county: how many courses and which colleges in Dublin, Cork, Galway, Limerick, Waterford, Sligo, Donegal, Louth and more.",
             body, crumbs=[("CAO points", "./"), ("Counties", None)], h1="CAO courses by county", sources=("courses",), cross=CROSS, priority="0.8")

def build_subjects():
    rows = []
    for a, (name, icon, intro) in AREAS.items():
        cs = sort_pts([c for c in COURSES if c["area"] == a])
        vals, lv = summary_stats(cs)
        rows.append([f'<a href="subject-{a}.html">{icon} {name}</a>', str(len(cs)), f"{min(vals)}–{max(vals)}" if vals else "–"])
        facts = [f"<strong>{len(cs)}</strong> {low(name)} courses on the CAO for 2027 (" + ", ".join(f"{n} at Level {l}" for l, n in sorted(lv.items(), reverse=True)) + ")."]
        if vals: facts.append(f"2026 Round 1 points: from <strong>{min(vals)}</strong> to <strong>{max(vals)}</strong>; half needed {sorted(vals)[len(vals) // 2]} or less.")
        aqa = [c for c in cs if c["lp"] and c["lp"]["aqa"]]
        if aqa: facts.append(f"{len(aqa)} courses took all qualified applicants in their latest round.")
        body = f"""<p class="lead">{intro}</p>
<p class="updated">Points {PY} · Checked {CHECKED}</p>
{key_facts(facts)}
<div class="ad" data-slot="content"></div>
<h2>All {low(name)} courses (highest points first)</h2>
{ctable(cs)}
{POINTS_NOTE}
<div class="cta"><h2>Which ones could you get?</h2><p>Enter your grades and filter by {low(name)}.</p><a class="btn" href="./?area={a}">Open the calculator</a></div>"""
        app.page(f"subject-{a}.html", f"{tc(name)} Courses CAO 2027 – Points for All {len(cs)} Courses in Ireland",
                 f"Every {low(name)} course on the CAO for 2027 with 2026 points" + (f" ({min(vals)}–{max(vals)})" if vals else "") + ", colleges and official course links.",
                 body, active="Courses by subject", crumbs=[("CAO points", "./"), ("Subjects", "subjects.html"), (name, None)], h1=f"{name} courses – CAO points",
                 sources=("courses", "pts"), cross=CROSS, priority="0.8")
    body = f"""<p class="lead">CAO courses for 2027 grouped by area, with the 2026 points range.</p>
{table(["Area", "Courses", "2026 points"], rows)}
<div class="ad" data-slot="content"></div>"""
    app.page("subjects.html", "CAO Courses by Subject 2027 – Business, Nursing, Computing, Engineering & More",
             "Find CAO courses by subject: business, computing, engineering, medicine and nursing, teaching, law, science, arts, design and more, with 2026 points.",
             body, active="Courses by subject", crumbs=[("CAO points", "./"), ("Subjects", None)], h1="CAO courses by subject", sources=("courses",), cross=CROSS, priority="0.8")

BANDS = list(range(200, 601, 50))
def build_bands():
    rows = []
    for n in BANDS:
        lo = n - 49 if n > 200 else 0
        cs = sort_pts([c for c in NONPORT if lo <= c["lp"]["value"] <= n and c["ly"] == "2026"])
        allw = [c for c in NONPORT if c["lp"]["value"] <= n and c["ly"] == "2026"]
        rows.append([f'<a href="courses-with-{n}-points.html">{n} points</a>', str(len(allw)), str(len(cs))])
        areas = collections.Counter(c["area"] for c in cs)
        facts = [f"With <strong>{n} points</strong>, about <strong>{len(allw)} of the {len(COURSES):,}</strong> CAO courses had a 2026 Round 1 cut-off at or below your score.",
                 f"<strong>{len(cs)}</strong> courses had cut-offs between {lo} and {n} – these are the most competitive courses within your reach.",
                 "Most common areas in this range: " + ", ".join(f"{low(AREAS[a][0])} ({k})" for a, k in areas.most_common(3)) + "." if areas else "",
                 "Points change every year. Put courses above and below your expected points on your CAO list, in your genuine order of preference."]
        groups = "".join(f'<h3>{AREAS[a][1]} {AREAS[a][0]}</h3>' + ctable([c for c in cs if c["area"] == a]) for a in AREAS if any(c["area"] == a for c in cs))
        nav = "".join(f'<a href="courses-with-{x}-points.html">{x} points</a>' for x in BANDS if x != n)
        body = f"""<p class="lead">What courses can you get with {n} CAO points? Every 2027 course whose 2026 Round 1 cut-off was between {lo} and {n}.</p>
<p class="updated">CAO points {PY} · Checked {CHECKED}</p>
{key_facts([f for f in facts if f])}
<div class="ad" data-slot="content"></div>
{groups or '<p>No courses in this range.</p>'}
{POINTS_NOTE}
<div class="cta"><h2>Not sure of your points?</h2><p>Enter your grades for your exact total and personal list.</p><a class="btn" href="./">Open the calculator</a></div>
<div class="chip-list">{nav}</div>"""
        app.page(f"courses-with-{n}-points.html", f"What Courses Can I Get With {n} CAO Points? 2027 List ({len(cs)} Courses)",
                 f"CAO courses you could get with {n} points: {len(cs)} courses had 2026 cut-offs between {lo} and {n}, and {len(allw)} at or below {n}. By subject, with colleges.",
                 body, active="By points", crumbs=[("CAO points", "./"), ("By points", "courses-by-points.html"), (f"{n} points", None)], h1=f"Courses you can get with {n} points",
                 sources=("pts", "courses"), cross=CROSS, priority="0.8")
    body = f"""<p class="lead">How many CAO courses could your points get you? Pick your points.</p>
{table(["Your points", "Courses at or below", "Courses in the band"], rows)}
<div class="ad" data-slot="content"></div>"""
    app.page("courses-by-points.html", "CAO Courses by Points 2027 – What Can I Get With 300, 400, 500 Points?",
             "Lists of CAO courses by points: what you can get with 200, 250, 300, 350, 400, 450, 500, 550 or 600 points, using 2026 Round 1 cut-offs.",
             body, active="By points", crumbs=[("CAO points", "./"), ("By points", None)], h1="CAO courses by points", sources=("pts",), cross=CROSS, priority="0.8")

def build_all_and_changes():
    cs = sorted(COURSES, key=lambda c: c["code"])
    h, r = course_rows(cs)
    body = f"""<p class="lead">All {len(cs):,} CAO courses for 2027 with 2026 and 2025 Round 1 points. Type to filter.</p>
<p class="updated">CAO 2027 course list · Points {PY} · Checked {CHECKED} · <a href="data/courses.json">Download as JSON</a></p>
<input type="search" id="filter" class="filter-input" placeholder="Filter: course, college or code (e.g. nursing, UCD, CK701)" aria-label="Filter courses">
{table(h, r, "all")}
{POINTS_NOTE}"""
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": "CAO courses 2027 with 2026 and 2025 points", "description": "Every CAO course for 2027 entry in Ireland with college, level, and 2023-2026 Round 1 points, from the CAO's published lists.",
          "url": app.BASE + "all-courses.html", "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "Tavion"},
          "isBasedOn": [SRC["pts"][1], SRC["courses"][1]], "distribution": {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": app.BASE + "data/courses.json"},
          "temporalCoverage": "2023/2026", "spatialCoverage": "Ireland"}
    app.page("all-courses.html", f"All CAO Courses 2027 & 2026 Points – Full List ({len(cs):,} Courses)",
             f"The full list of {len(cs):,} CAO courses for 2027 with 2026 and 2025 Round 1 points, colleges and levels – searchable.",
             body, jsonld=[ds], crumbs=[("CAO points", "./"), ("All courses", None)], h1="All CAO courses for 2027", sources=("pts_l8", "pts_l76", "courses"), cross=CROSS, priority="0.9",
             scripts=["js/filter.js"])
    ch = []
    for c in NONPORT:
        a, b = pp(c["points"].get("2026", {}).get("r1")), pp(c["points"].get("2025", {}).get("r1"))
        if a and b and a["value"] and b["value"] and not a["aqa"] and not b["aqa"] and a["value"] <= 625 and b["value"] <= 625:
            ch.append((a["value"] - b["value"], c))
    up = sorted(ch, key=lambda x: -x[0])[:25]; down = sorted(ch, key=lambda x: x[0])[:25]
    rise = sum(1 for d, _ in ch if d > 0); fall = sum(1 for d, _ in ch if d < 0)
    def rows_(lst): return [[course_link(c, c["code"] + " " + c["title"]), COL[c["college"]][0], c["points"]["2025"]["r1"], c["points"]["2026"]["r1"], ("+" if d > 0 else "") + str(d)] for d, c in lst]
    big = [c for c in NONPORT if c["ly"] == "2026" and c["level"] == 8]
    body = f"""<p class="lead">Which CAO points went up and down in 2026? The biggest risers and fallers between 2025 and 2026 Round 1.</p>
<p class="updated">CAO Round 1 2025 and 2026 · Checked {CHECKED}</p>
{key_facts([f"Of {len(ch)} courses with points in both years, <strong>{rise} went up</strong>, <strong>{fall} went down</strong> and {len(ch) - rise - fall} stayed the same.",
            f"Biggest rise: {course_link(up[0][1])} (+{up[0][0]}).", f"Biggest fall: {course_link(down[0][1])} ({down[0][0]}).",
            "Points depend on how many people put the course high on their list and how many places there are – a big jump one year often settles the next."])}
<h2>Biggest rises</h2>{table(["Course", "College", "2025", "2026", "Change"], rows_(up))}
<div class="ad" data-slot="content"></div>
<h2>Biggest falls</h2>{table(["Course", "College", "2025", "2026", "Change"], rows_(down))}
<h2>Highest-points Level 8 courses in 2026</h2>{ctable(sort_pts(big)[:20])}"""
    app.page("points-changes-2026.html", "CAO Points 2026 – Biggest Rises and Falls vs 2025",
             f"CAO 2026 Round 1 points compared with 2025: {rise} courses rose and {fall} fell. The biggest risers, fallers and the highest-points courses.",
             body, crumbs=[("CAO points", "./"), ("2026 changes", None)], h1="CAO points 2026: what went up and down", sources=("pts",), cross=CROSS, priority="0.8")

# ---------- Guides ----------
def build_guides():
    body = f"""<p class="lead">The key CAO dates for everyone starting college in 2027 – applying, changing your mind, HEAR/DARE and offers.</p>
<p class="updated">CAO timetable · Checked {CHECKED} · Dates may change – always check the CAO</p>
{key_facts(["<strong>5 November 2026</strong> (12:00): CAO applications open for 2027.", "<strong>20 January 2027</strong> (17:00): apply by now for the discounted <strong>€35</strong> fee.",
            "<strong>1 February 2027</strong> (17:00): normal closing date. Restricted courses must be on your list by now.",
            "<strong>1 March 2027</strong> (17:00): last day to complete the online HEAR/DARE forms and the mature section.", "<strong>5 May – 1 July 2027</strong>: free Change of Mind.",
            "<strong>August 2027</strong>: Leaving Cert results and Round 1 offers (exact dates to be confirmed)."])}
{table(["Date", "What happens"], [["5 Nov 2026", "Applications open"], ["5 Nov 2026 – 15 Jan 2027", "HPAT registration (undergraduate medicine)"], ["20 Jan 2027", "Discounted €35 fee deadline"],
    ["1 Feb 2027", "Normal closing date"], ["5 Feb 2027", "Amend course choices opens (€10)"], ["12–15 Feb 2027", "HPAT test"], ["1 Mar 2027", "Amend choices, mature and HEAR/DARE forms close"],
    ["5 Mar 2027", "Late applications open"], ["10 Mar 2027", "HEAR/DARE documents must reach the CAO"], ["1 May 2027", "Late applications close"], ["5 May 2027", "Change of Mind opens (free)"],
    ["23 Jun 2027", "HEAR/DARE outcomes"], ["1 Jul 2027", "Change of Mind closes"], ["August 2027", "Results, Round 1 offers (date TBC)"]])}
<div class="ad" data-slot="content"></div>
<h2>Tips</h2>{lis(["List courses in your <strong>genuine order of preference</strong> – you're offered the highest one your points reach, so a 'safe' choice high up can cost you a course you'd prefer.",
    "Use all 10 Level 8 and 10 Level 7/6 places.", "Restricted courses (portfolio, audition, some tests) can't be added after 1 February.", "Apply for a <a href='https://susi.ie/' rel='noopener' target='_blank'>SUSI grant</a> from spring – you don't need an offer first."])}"""
    app.page("dates-2027.html", "CAO Dates 2027 – Closing Date 1 February, Change of Mind, Offers",
             "CAO 2027 key dates: applications open 5 November 2026, €35 fee until 20 January, closing date 1 February 2027, Change of Mind 5 May–1 July, HEAR/DARE and HPAT dates.",
             body, active="Dates 2027", crumbs=[("CAO points", "./"), ("Dates 2027", None)], h1="CAO dates 2027", sources=("dates", "tests"), cross=CROSS, priority="0.9")

    body = f"""<p class="lead">HEAR and DARE are college access routes that can get you a place on <strong>reduced points</strong> – plus extra support in college. Here's who qualifies and how to apply.</p>
<p class="updated">CAO and AccessCollege.ie · Checked {CHECKED}</p>
{key_facts(["<strong>HEAR</strong> (Higher Education Access Route) is for school leavers from socio-economically disadvantaged backgrounds – based on things like family income, medical card, social welfare, your school and area.",
            "<strong>DARE</strong> (Disability Access Route to Education) is for school leavers whose disability, condition or learning difficulty has affected their second-level education.",
            "Eligible applicants compete for a <strong>quota of places at reduced points</strong>. How much lower depends on the college and course – it is not a fixed bonus.",
            "Apply through your CAO application by <strong>1 February 2027</strong>, complete the HEAR/DARE forms by <strong>1 March</strong> and get supporting documents to the CAO by <strong>10 March</strong>.",
            "You'll hear if you're eligible by <strong>23 June 2027</strong>, with a review and appeal option until 2 July.",
            "You must still meet the course's minimum entry requirements."])}
<div class="ad" data-slot="content"></div>
<h2>Other routes that can help</h2>
{lis(["<strong>Mature entry</strong> – 23 or over on 1 January 2027: separate places, often assessed by interview or statement. <a href='https://www.cao.ie/index.php?page=mature' target='_blank' rel='noopener'>CAO mature applicants</a>",
      "<strong>QQI FET (PLC) courses</strong> – a Level 5 or 6 award gives up to 390 points and reserved places on many courses. <a href='qqi-fet.html'>QQI FET points explained</a>",
      "<strong>Level 7/6 then add-on</strong> – many Level 7 courses let you progress to Level 8.", "<strong>College-run access programmes</strong> for students from areas with low progression to college."])}
<p>Official guide and forms: <a href="https://accesscollege.ie/" target="_blank" rel="noopener">accesscollege.ie</a>.</p>"""
    faqs = [("How many points do you get off with HEAR?", "There's no fixed number. HEAR and DARE places are allocated on reduced points, and the reduction varies by college and course."),
            ("When do I apply for HEAR or DARE?", "Tick the HEAR/DARE section in your CAO application by 1 February 2027, finish the online forms by 1 March and send documents by 10 March 2027.")]
    app.page("hear-dare.html", "HEAR and DARE 2027 – Reduced Points College Access Routes Explained",
             "HEAR and DARE explained for 2027: who qualifies, reduced-points places, how to apply through the CAO (1 February, 1 March, 10 March) and other access routes.",
             body, active="HEAR & DARE", jsonld=[faq_ld(faqs)], crumbs=[("CAO points", "./"), ("HEAR & DARE", None)], h1="HEAR and DARE: reduced-points routes into college",
             sources=("access", "accesscollege", "dates", "mature"), cross=CROSS, priority="0.8")

    med = [c for c in COURSES if any("HPAT" in t for t in c["tags"])]
    body = f"""<p class="lead">How undergraduate medicine entry works in 2027 – and the big change to how the HPAT counts.</p>
<p class="updated">CAO / medical schools 2027 · Checked {CHECKED}</p>
{key_facts([f"You need at least <strong>{E['med']['minPoints']} Leaving Cert points</strong>, the minimum subject requirements for each medical school, and to sit <strong>HPAT-Ireland</strong> in 2027.",
            "<strong>New for 2027:</strong> Leaving Cert points above 550 are <strong>no longer moderated</strong> – your full points count.",
            f"<strong>New for 2027:</strong> HPAT is weighted to a <strong>maximum of {E['med']['hpatMax']}</strong> (it was 300). So the top combined score is {E['max'] + E['med']['hpatMax']}.",
            "Because of this, <strong>2026 medicine points can't be compared with 2027</strong> – expect very different numbers.",
            "HPAT registration: 5 November 2026 – 15 January 2027 (late until 1 February). Test: 12–15 February 2027. Results: late June 2027.",
            "Ties on the combined score are broken by Leaving Cert points."])}
<h2>Undergraduate medicine courses for 2027</h2>{ctable(med)}
<div class="ad" data-slot="content"></div>
<p class="muted small">2026 and earlier scores use the old scale (Leaving Cert moderated above 550 + HPAT out of 300).</p>"""
    app.page("medicine-hpat.html", "Medicine Entry 2027 Ireland – HPAT Changes, 480 Points Minimum, Combined Score",
             f"Undergraduate medicine 2027: minimum 480 points, HPAT now weighted to 150, Leaving Cert above 550 no longer moderated. Courses, dates and 2026 scores.",
             body, crumbs=[("CAO points", "./"), ("Medicine & HPAT", None)], h1="Medicine and the HPAT in 2027", sources=("med", "medpage", "dates"), cross=CROSS, priority="0.8")

    port = [c for c in COURSES if any(t in ("Portfolio", "Audition", "Interview") for t in c["tags"])]
    body = f"""<p class="lead">{len(port)} CAO courses for 2027 use a portfolio, audition or interview. Here's how it affects your points, and the full list.</p>
<p class="updated">CAO 2027 course list · Checked {CHECKED}</p>
{key_facts(["For many art and design courses the <strong>portfolio is scored</strong> and added to your Leaving Cert points – that's why some cut-offs are over 625 (up to around 1,000).",
            "Some courses only use the portfolio or audition (you must still meet minimum entry requirements).",
            "Most of these are <strong>restricted</strong>: they must be on your CAO list by <strong>1 February 2027</strong>.",
            "Portfolio deadlines are set by each college – usually in early spring. Check the official course page."])}
<div class="ad" data-slot="content"></div>
{ctable(sort_pts(port))}
{POINTS_NOTE}"""
    app.page("portfolio-courses.html", f"CAO Portfolio, Audition & Interview Courses 2027 – Full List ({len(port)})",
             f"All {len(port)} CAO courses for 2027 that need a portfolio, audition or interview, how portfolio scores are added to points, and 2026 cut-offs.",
             body, crumbs=[("CAO points", "./"), ("Portfolio courses", None)], h1="Portfolio, audition and interview courses", sources=("courses", "tests", "pts"), cross=CROSS, priority="0.7")

    body = f"""<p class="lead">Did a PLC or QQI Level 5/6 course? You can get up to <strong>390 CAO points</strong> – and many courses keep places just for you.</p>
<p class="updated">CAO QQI FET scoring scheme · Checked {CHECKED}</p>
{key_facts(["You need a <strong>full QQI FET Level 5 or 6 major award</strong> – usually 8 components. A component certificate isn't enough.",
            "Each component is weighted by grade: <strong>Distinction 3, Merit 2, Pass 1</strong>, times its credit value.",
            "Add your best components up to <strong>120 credits</strong> (distinctions first), then multiply by 13/12. <strong>8 distinctions = 390 points</strong>.",
            "Some courses need specific components or a minimum number of distinctions.", "Many courses have a <strong>reserved quota</strong> for QQI FET applicants, including nursing."])}
<div class="card"><div class="tl">Quick QQI points calculator</div>
<p class="small">Number of 15-credit components at each grade (up to 8):</p>
<div class="three"><label>Distinctions<input type="number" id="qd" min="0" max="8" value="8"></label><label>Merits<input type="number" id="qm" min="0" max="8" value="0"></label><label>Passes<input type="number" id="qp" min="0" max="8" value="0"></label></div>
<div class="pts-hero"><div class="amt" id="qout">390</div><p>CAO points</p></div></div>
<div class="ad" data-slot="content"></div>
<p>Then use your score in the <a href="./">course finder</a> or see <a href="courses-with-350-points.html">courses with 350 points</a>.</p>
<script>(function(){{function g(i){{return Math.max(0,Math.min(8,parseInt(document.getElementById(i).value,10)||0))}}function r(){{var d=g("qd"),m=g("qm"),p=g("qp"),left=8,t=0;[[d,3],[m,2],[p,1]].forEach(function(x){{var n=Math.min(x[0],left);t+=n*15*x[1];left-=n}});document.getElementById("qout").textContent=Math.round(t*13/12)}}["qd","qm","qp"].forEach(function(i){{document.getElementById(i).addEventListener("input",r)}});r()}})();</script>"""
    app.page("qqi-fet.html", "QQI FET (PLC) CAO Points Calculator – Up to 390 Points Explained",
             "How QQI FET / PLC Level 5 and 6 awards are converted to CAO points: distinction 3, merit 2, pass 1, best 120 credits × 13/12, maximum 390. With a calculator.",
             body, crumbs=[("CAO points", "./"), ("QQI FET points", None)], h1="QQI FET points for the CAO", sources=("fet", "fetpage"), cross=CROSS, priority="0.7")

    FAQ = [("How are CAO points calculated?", "Your best six Leaving Cert subjects from one sitting. H1 100 down to H7 37; O1 56 down to O6 12. +25 for Higher Maths at H6 or above. Maximum 625."),
           ("What is the Higher Maths bonus?", "25 extra points for a H6 or better in Higher Level Maths. A H6 is worth 71 instead of 46."),
           ("Does LCVP count for CAO points?", "Yes – the Link Modules can count as a sixth subject: Distinction 66, Merit 46, Pass 28. Not every college accepts LCVP for minimum entry requirements."),
           ("Are last year's points what I'll need?", "No – they're a guide. Points are set by demand and the number of places each August. Use them to judge which courses are realistic, not to rule courses out."),
           ("What does * mean on CAO points?", "Not everyone on that score got a place – places went to some applicants on that score by random selection."),
           ("What does # mean?", "The course has a test, interview, portfolio or audition. Scores over 625 include that element."),
           ("What does AQA mean?", "All qualified applicants – everyone who met the minimum entry requirements and applied got an offer."),
           ("How many courses can I list?", "Up to 10 Level 8 and 10 Level 7/6 courses, in order of preference. The lists are separate – you can get an offer from each."),
           ("What is the difference between Level 6, 7 and 8?", "Level 8 is an honours bachelor degree (usually 4 years), Level 7 an ordinary degree (3 years), Level 6 a higher certificate (2 years). Many Level 6/7 courses lead on to Level 8."),
           ("When does the CAO close for 2027?", "1 February 2027 at 17:00 (discounted €35 fee if you apply by 20 January). Change of Mind is free from 5 May to 1 July 2027."),
           ("What is HEAR and DARE?", "Access routes giving reduced-points places to students from disadvantaged backgrounds (HEAR) or with a disability (DARE). Apply by 1 February."),
           ("Is this the official CAO site?", "No – this is a free, independent tool. Apply only at cao.ie.")]
    app.page("faq.html", "CAO Points FAQ 2027 – Bonus Points, LCVP, AQA, *, # and Levels Explained",
             "CAO questions answered: how points are calculated, the maths bonus, LCVP, what *, # and AQA mean, levels 6/7/8, the 2027 closing date and HEAR/DARE.",
             f'<p class="lead">Common CAO questions, answered simply.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("CAO points", "./"), ("FAQ", None)], h1="CAO points FAQ", sources=("grid", "dates", "ci"), cross=CROSS, priority="0.8")

if __name__ == "__main__":
    write_json()
    build_index(); build_points_table(); build_course_pages(); build_colleges(); build_counties(); build_subjects(); build_bands(); build_all_and_changes(); build_guides()
    og_image(os.path.join(app.root, "og.png"), "LEAVING CERT 2027", "CAO points", "calculator", "Your points · the courses they get you", f"{len(COURSES):,} courses with 2026 points",
             "tavion.ie/cao  ·  free, no sign-up", (165, 180, 252), (67, 56, 202), (30, 25, 80))
    app.update_sitemap()
    app.update_llms("- [CAO Points Calculator](https://tavion.ie/cao/): Leaving Cert CAO points (maths bonus, LCVP), course finder, and a page for every 2027 CAO course with 2023-2026 points, by college, county, subject and points.",
                    "CAO points: key facts",
                    f"""- CAO points: best six Leaving Cert subjects, one sitting. Higher: H1 100, H2 88, H3 77, H4 66, H5 56, H6 46, H7 37, H8 0. Ordinary: O1 56, O2 46, O3 37, O4 28, O5 20, O6 12. Higher Maths +25 for H6 or above. Max 625. LCVP: Distinction 66, Merit 46, Pass 28. Foundation F1 20, F2 12 (some colleges only).
- 2027 CAO: opens 5 Nov 2026; €35 fee to 20 Jan 2027; closes 1 Feb 2027; Change of Mind 5 May-1 Jul 2027; HEAR/DARE forms by 1 Mar, documents by 10 Mar.
- Medicine 2027: minimum 480 points + HPAT; Leaving Cert above 550 no longer moderated; HPAT weighted to max 150 (was 300).
- QQI FET: distinction 3/merit 2/pass 1 x credits, best 120 credits x 13/12, max 390.
- {len(COURSES):,} courses at {len(COL)} colleges for 2027. Pages: [Calculator](https://tavion.ie/cao/), [All courses with points](https://tavion.ie/cao/all-courses.html), [Points table](https://tavion.ie/cao/points-table.html), [Colleges](https://tavion.ie/cao/colleges.html), [By points](https://tavion.ie/cao/courses-by-points.html), [Dates 2027](https://tavion.ie/cao/dates-2027.html). Data: [courses.json](https://tavion.ie/cao/data/courses.json). Source: cao.ie.""")
    print("Built", len(app.files), "pages in", app.root)
