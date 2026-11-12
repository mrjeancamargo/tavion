"""
Builds the Bank Holidays & Leave Planner app (tavion.ie/bank-holidays/).
Run from the repo root:   python tools/build_holidays.py      (needs Node.js)
Dates and plans come from bank-holidays/js/holidays.js (same engine as the planner).
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import App, lis, table, faq_ld, faq_html, key_facts, node, og_image

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.normpath(os.path.join(HERE, "..", "bank-holidays", "js", "holidays.js"))
CHECKED = "November 2026"
YEARS = [2026, 2027, 2028, 2029, 2030]
FOCUS = 2027
NODE = r"""
const H = require(process.argv[1]);
let raw = ""; process.stdin.on("data", d => raw += d).on("end", () => {
  const q = JSON.parse(raw);
  const res = q.map(x => x.k === "hol" ? H.publicHolidays(x.y) : x.k === "plan" ? H.plan(x.y, x.l, x.o || {}) : x.k === "sum" ? H.yearSummary(x.y) :
    x.k === "ics" ? H.ics(x.ys) : x.k === "easter" ? H.easterSunday(x.y) : null);
  process.stdout.write(JSON.stringify({ school: H.SCHOOL, order: H.ORDER, names: H.NAMES, res }));
});
"""
def run(*q): return node(ENGINE, NODE, list(q))
META = run(); SCHOOL, ORDER, NAMES = META["school"], META["order"], META["names"]
def res(*q): return run(*q)["res"]
HOL = {y: h for y, h in zip(YEARS, res(*[{"k": "hol", "y": y} for y in YEARS]))}
SUM = {y: s for y, s in zip(YEARS, res(*[{"k": "sum", "y": y} for y in YEARS]))}

def dt(s): return datetime.date.fromisoformat(s)
def nice(s, wd=True): x = dt(s); return (x.strftime("%A ") if wd else "") + f"{x.day} {x.strftime('%B %Y')}"
def short(s): x = dt(s); return f"{x.strftime('%a')} {x.day} {x.strftime('%b')}"

SRC = {
    "ci": ("Citizens Information – Public holidays", "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/leave-and-holidays/public-holidays/"),
    "ci_leave": ("Citizens Information – Annual leave", "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/leave-and-holidays/annual-leave/"),
    "wrc": ("Workplace Relations Commission – Public holidays", "https://www.workplacerelations.ie/en/what_you_should_know/hours-and-holidays/public-holidays/"),
    "wrc_leave": ("Workplace Relations Commission – Annual leave", "https://www.workplacerelations.ie/en/what_you_should_know/hours-and-holidays/annual-leave/"),
    "act": ("Organisation of Working Time Act 1997 (Irish Statute Book)", "https://www.irishstatutebook.ie/eli/1997/act/20/enacted/en/html"),
    "school": ("Department of Education – Circular 0018/2026: standardised school year 2026/27–2028/29", "https://www.gov.ie/en/department-of-education/circulars/standardisation-of-the-school-year-in-respect-of-primary-post-primary-schools-for-the-years-202627-202728-and-202829"),
    "brigid": ("gov.ie – New public holiday for St Brigid's Day", "https://www.gov.ie/en/press-release/4ae6f-government-confirms-new-public-holiday-to-mark-st-brigids-day/"),
}
TABS = [("./", "2027 & planner"), ("bank-holidays-2026.html", "2026"), ("bank-holidays-2028.html", "2028"), ("leave-planner-2027.html", "Leave planner"),
        ("school-holidays.html", "School holidays"), ("public-holiday-rights.html", "Your rights"), ("annual-leave.html", "Annual leave"), ("faq.html", "FAQ")]
FOOT = ('<a href="./">Bank holidays 2027</a>' + "".join(f'<a href="bank-holidays-{y}.html">Bank holidays {y}</a>' for y in YEARS) +
        '<a href="leave-planner-2027.html">Leave planner 2027</a><a href="long-weekends-2027.html">Long weekends 2027</a><a href="school-holidays.html">School holidays</a>'
        '<a href="public-holiday-rights.html">Public holiday rights</a><a href="bank-holiday-on-weekend.html">Holiday on a weekend</a><a href="annual-leave.html">Annual leave calculator</a>'
        '<a href="good-friday.html">Is Good Friday a bank holiday?</a><a href="faq.html">FAQ</a>')
app = App("bank-holidays", "Bank Holidays Ireland", "📅", None, "#b45309", TABS, FOOT, SRC, None,
          "All the Irish bank holidays for 2027 – and how to turn your annual leave into way more days off:",
          "Planning time off? Send this to the person who books your holidays.", "holidays",
          f"Dates checked against Citizens Information and the Department of Education in {CHECKED}. A free, independent tool from <a href='../'>Tavion</a>. "
          "Your employer's leave policy and contract may give you more than the legal minimum.")
CROSS = ["taxrefund", "salary", "welfare", "cao"]

# ---------- Holiday descriptions (original text) ----------
ABOUT = {
    "newyear": ("A fresh start", "New Year's Day marks the start of the calendar year. Most shops open later, public transport runs a Sunday or holiday service, and it's the last day of the Christmas break for many workers.",
                ["Most offices close; many shops open late morning.", "Public transport usually runs a reduced service.", "Schools are still on Christmas holidays."]),
    "brigid": ("Ireland's newest public holiday", "St Brigid's Day became a public holiday in 2023 – the first named after an Irish woman. Brigid is one of Ireland's patron saints, linked to Kildare, and her day on 1 February marks Imbolc, the old Celtic start of spring. Many families still make a St Brigid's cross from rushes.",
               ["Falls on the first Monday in February – or on 1 February itself if that's a Friday.", "Celebrated with St Brigid's crosses, festivals in Kildare and the 'Brigid' arts events.", "It was the first new public holiday since 1994."]),
    "patrick": ("Ireland's national day", "St Patrick's Day on 17 March celebrates Ireland's patron saint and Irish culture around the world. It has been a bank holiday since 1903. Parades run in nearly every town, with the biggest in Dublin.",
                ["Always 17 March, whatever the weekday.", "Parades and festivals nationwide; Dublin's festival runs over several days.", "If it falls at a weekend, you're still entitled to the public holiday benefit."]),
    "easter": ("The day after Easter Sunday", "Easter Monday follows Easter Sunday, so its date moves every year – from late March to late April. It is also linked to the 1916 Rising, which began on Easter Monday, 24 April 1916.",
               ["Easter can fall between 22 March and 25 April.", "Good Friday is not a public holiday, although many schools and businesses close.", "Schools are usually off for the two weeks around Easter."]),
    "may": ("The start of summer", "The May bank holiday is the first Monday in May. It has been a public holiday since 1994 and is often linked to May Day, the old festival of Bealtaine marking the start of summer.",
            ["Always the first Monday in May.", "A popular weekend for the first trips of the year.", "Close to the Leaving Cert exams starting in June."]),
    "june": ("The early-summer long weekend", "The June bank holiday is the first Monday in June. It replaced Whit Monday as a fixed date in the 1970s and is the start of summer for most people – and the start of the Leaving and Junior Cert exams just after.",
             ["Always the first Monday in June.", "Post-primary schools finish classes before this weekend.", "Busy weekend for festivals and the seaside."]),
    "august": ("The summer bank holiday", "The August bank holiday is the first Monday in August – the height of summer, with festivals and events across the country.",
               ["Always the first Monday in August.", "Peak weekend for travel at home – book early.", "Schools are still on summer holidays."]),
    "october": ("The Halloween bank holiday", "The October bank holiday falls on the last Monday in October, close to Halloween – whose roots are in the Celtic festival of Samhain. It was introduced in 1977.",
                ["Always the last Monday in October.", "Usually the same week as the school mid-term break.", "Halloween (31 October) itself isn't a public holiday."]),
    "christmas": ("Christmas Day", "Christmas Day, 25 December, is the most widely observed holiday of the year – almost everything closes, including most shops and public transport.",
                  ["Always 25 December.", "Most public transport doesn't run on Christmas Day.", "If it falls at a weekend, check how your employer gives you the benefit."]),
    "stephen": ("St Stephen's Day", "St Stephen's Day, 26 December, is known in Irish as Lá an Dreoilín – the Day of the Wren – when 'wren boys' traditionally go door to door. Today it's a big day for sport, sales and visiting family.",
                ["Always 26 December.", "Horse racing at Leopardstown and Limerick, and Wren Day traditions in the west and south.", "Many shops reopen for sales."]),
}
SLUG = {"newyear": "new-years-day", "brigid": "st-brigids-day", "patrick": "st-patricks-day", "easter": "easter-monday", "may": "may-bank-holiday",
        "june": "june-bank-holiday", "august": "august-bank-holiday", "october": "october-bank-holiday", "christmas": "christmas-day", "stephen": "st-stephens-day"}

def hol_rows(y, link=True):
    rows = []
    for h in HOL[y]:
        name = f'<a href="{SLUG[h["key"]]}-{y}.html">{h["name"]}</a>' if link and y in (2026, 2027, 2028) else h["name"]
        rows.append([name, nice(h["date"]), "🏖️ Long weekend" if h["weekday"] in (1, 5) else ("Weekend – see rules" if h["weekend"] else "Midweek")])
    return rows

def plan_html(p, title=None):
    if not p["breaks"]: return "<p>No breaks found.</p>"
    rows = [[f"{short(b['from'])} – {short(b['to'])}", f"{short(b['leaveFrom'])}" + (f" – {short(b['leaveTo'])}" if b['leaveTo'] != b['leaveFrom'] else ""), str(b["leave"]), f"<strong>{b['daysOff']}</strong>",
             ", ".join(b["holidays"]) or "–"] for b in p["breaks"]]
    return table(["Time off", "Book leave", "Leave days", "Days off", "Includes"], rows)

ICS_LINK = '<a class="btn" href="ireland-public-holidays.ics" download data-track="ics_download" data-label="all">📆 Add all bank holidays to your calendar</a>'

# ---------- Index ----------
def build_index():
    y = FOCUS
    p9 = res({"k": "plan", "y": y, "l": 9})[0]
    s26, s27 = SUM[2026], SUM[2027]
    body = f"""<p class="lead">All 10 Irish bank holidays for {y}, a countdown to the next one, and a planner that turns your annual leave into the most days off in a row. Free, no sign-up.</p>
<ul class="facts"><li>10 public holidays</li><li>{s27['longWeekends']} long weekends in {y}</li><li>Christmas {y} on a weekend</li></ul>
<div id="countdown" class="pts-hero" aria-live="polite"><div class="tl">Next bank holiday</div><div class="amt">–</div><p></p></div>
<h2>Bank holidays {y}</h2>
{table(["Holiday", "Date", ""], hol_rows(y))}
<div class="btn-row">{ICS_LINK}</div>
<div class="ad" data-slot="result"></div>
<h2 id="planner">Leave planner: get more days off</h2>
<form id="planForm" class="card" novalidate>
  <div class="two"><label>Days of annual leave you have<input id="leave" type="number" inputmode="numeric" min="1" max="40" value="9"></label>
  <label>Year<select id="year">{''.join(f'<option value="{x}"{" selected" if x == y else ""}>{x}</option>' for x in (2026, 2027, 2028))}</select></label></div>
  <label class="big-label" style="margin-top:6px">Days you normally work</label>
  <div class="seg" id="workDays">{''.join(f'<label><input type="checkbox" value="{i}"{" checked" if 1 <= i <= 5 else ""}><span>{n}</span></label>' for i, n in [(1, "Mon"), (2, "Tue"), (3, "Wed"), (4, "Thu"), (5, "Fri"), (6, "Sat"), (0, "Sun")])}</div>
  <label class="check"><input type="checkbox" id="school"><span>Show school holidays too (to match the kids' breaks)</span></label>
  <div class="btn-row"><button type="submit" class="btn primary">Plan my time off</button></div>
  <p class="muted small" style="margin-bottom:0">🔒 Worked out on your phone. Nothing is sent to us.</p>
</form>
<div id="result" aria-live="polite"></div>
<p>Example: with <strong>{p9['used']} days</strong> of leave in {y} you can get <strong>{p9['daysOff']} days off</strong> in total. <a href="leave-planner-{y}.html">See plans for 1–25 days →</a></p>
<h2>{y} vs 2026</h2>
{key_facts([f"{y} has <strong>{s27['weekdayHolidays']} bank holidays on weekdays</strong>, against {s26['weekdayHolidays']} in 2026 – because Christmas Day and St Stephen's Day {y} fall on a Saturday and Sunday.",
            "You're still entitled to the public holiday <strong>benefit</strong> for those days (a day's pay, an extra day of leave, or a day off within a month) – but not automatically the Monday off. <a href='bank-holiday-on-weekend.html'>How it works</a>",
            f"{y} has <strong>{s27['longWeekends']} long weekends</strong> (holiday on a Monday or Friday) against {s26['longWeekends']} in 2026.", f"Easter Monday {y} is early: <strong>{nice(HOL[y][3]['date'], False)}</strong>."])}
<div class="chip-list">{"".join(f'<a href="{SLUG[k]}.html">{NAMES[k]}</a>' for k in ORDER)}</div>
<div class="cta"><h2>School holidays 2026/27</h2><p>Mid-terms, Christmas and Easter – the official dates.</p><a class="btn" href="school-holidays-2026-27.html">School holiday dates</a></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Bank Holidays & Annual Leave Planner", "url": app.BASE, "applicationCategory": "UtilitiesApplication",
          "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": "en-IE", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
          "description": f"Irish public holidays {y} with a leave planner that finds the best days to book off for the most consecutive days off."}
    events = [{"@context": "https://schema.org", "@type": "Event", "name": f"{h['name']} {y} (public holiday, Ireland)", "startDate": h["date"], "endDate": h["date"],
               "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled", "location": {"@type": "Country", "name": "Ireland"},
               "description": ABOUT[h["key"]][1][:150]} for h in HOL[y]]
    faqs = [(f"How many bank holidays are there in Ireland in {y}?", f"10. {s27['weekdayHolidays']} fall on weekdays; Christmas Day and St Stephen's Day {y} fall on a weekend."),
            (f"When is the next bank holiday in Ireland?", f"See the countdown above. In {y} they are: " + "; ".join(f"{h['name']} {nice(h['date'], False)}" for h in HOL[y]) + ".")]
    app.page("index.html", f"Bank Holidays Ireland {y} – All 10 Dates + Annual Leave Planner",
             f"Irish bank holidays {y}: New Year's Day, St Brigid's Day 1 Feb, St Patrick's Day, Easter Monday 29 Mar, May, June, August, October, Christmas. Plan your leave for the most days off.",
             body, active="2027 & planner", jsonld=[ld, faq_ld(faqs)] + events, slot="calculator", scripts=["js/holidays.js", "js/planner.js"], h1=f"Bank holidays Ireland {y}",
             sources=("ci", "school", "act"), cross=CROSS, priority="1.0",
             share_text=f"All the Irish bank holidays for {y} – and a planner that turns 9 days of leave into {p9['daysOff']} days off:")

# ---------- Per-year pages ----------
def build_years():
    for y in YEARS:
        s = SUM[y]
        p = res({"k": "plan", "y": y, "l": 9})[0]
        prev = SUM.get(y - 1)
        facts = [f"There are <strong>10 public holidays</strong> in {y}; <strong>{s['weekdayHolidays']}</strong> fall on weekdays.", f"<strong>{s['longWeekends']} long weekends</strong> (holiday on a Monday or Friday).",
                 f"Easter Monday is <strong>{nice(HOL[y][3]['date'], False)}</strong>.", f"St Brigid's Day holiday: <strong>{nice(HOL[y][1]['date'], False)}</strong>."]
        wk = [h for h in HOL[y] if h["weekend"]]
        if wk: facts.append("On a weekend: " + ", ".join(f"{h['name']} ({dt(h['date']).strftime('%A')})" for h in wk) + ". You still get the benefit – <a href='bank-holiday-on-weekend.html'>how it works</a>.")
        if prev: facts.append(f"Compared with {y - 1}: {s['weekdayHolidays'] - prev['weekdayHolidays']:+d} weekday bank holidays.")
        body = f"""<p class="lead">Every Irish public holiday in {y}, which ones make a long weekend, and the best days to book off.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts(facts)}
{table(["Holiday", "Date", ""], hol_rows(y))}
<div class="btn-row">{ICS_LINK}</div>
<div class="ad" data-slot="content"></div>
<h2>Best way to use 9 days of leave in {y}</h2>
<p>Book these and you get <strong>{p['daysOff']} days off</strong>:</p>
{plan_html(p)}
<div class="cta"><h2>Plan with your own leave</h2><p>Your days, your working week.</p><a class="btn" href="./?year={y}#planner">Open the leave planner</a></div>
<div class="chip-list">{"".join(f'<a href="bank-holidays-{x}.html">{x}</a>' for x in YEARS if x != y)}</div>"""
        app.page(f"bank-holidays-{y}.html", f"Bank Holidays Ireland {y} – All Public Holiday Dates & Long Weekends",
                 f"Irish public holidays {y}: " + ", ".join(f"{h['name']} {dt(h['date']).day} {dt(h['date']).strftime('%b')}" for h in HOL[y][:5]) + f" and more. {s['longWeekends']} long weekends and the best days to book off.",
                 body, active=str(y) if y in (2026, 2028) else None, jsonld=[faq_ld([(f"What are the bank holidays in Ireland in {y}?", "; ".join(f"{h['name']}: {nice(h['date'])}" for h in HOL[y]))])],
                 crumbs=[("Bank holidays", "./"), (str(y), None)], h1=f"Bank holidays Ireland {y}", sources=("ci", "act"), cross=CROSS, priority="0.9" if y in (2026, 2027, 2028) else "0.6")

# ---------- Per-holiday hub and holiday-year pages ----------
def build_holidays():
    for k in ORDER:
        title_tag, about, facts = ABOUT[k]
        dates = [[str(y), nice(next(h["date"] for h in HOL[y] if h["key"] == k))] for y in YEARS]
        body = f"""<p class="lead">{about}</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(facts)}
<h2>{NAMES[k]} dates</h2>{table(["Year", "Date"], dates)}
<div class="ad" data-slot="content"></div>
<p>{" · ".join(f'<a href="{SLUG[k]}-{y}.html">{NAMES[k]} {y}</a>' for y in (2026, 2027, 2028))}</p>
<div class="cta"><h2>Make it a longer break</h2><p>See which days to book off around it.</p><a class="btn" href="./#planner">Leave planner</a></div>"""
        app.page(f"{SLUG[k]}.html", f"{NAMES[k]} Ireland – Dates {YEARS[0]}–{YEARS[-1]} & What It Means",
                 f"{NAMES[k]} in Ireland: dates for {YEARS[0]}–{YEARS[-1]}, what the day means, and how to turn it into a longer break.",
                 body, crumbs=[("Bank holidays", "./"), (NAMES[k], None)], h1=NAMES[k], sources=("ci",) + (("brigid",) if k == "brigid" else ()), cross=CROSS, priority="0.7")
        for y in (2026, 2027, 2028):
            h = next(x for x in HOL[y] if x["key"] == k)
            x = dt(h["date"]); wd = x.strftime("%A")
            p = res({"k": "plan", "y": y, "l": 4})[0]
            around = [b for b in p["breaks"] if NAMES[k] in b["holidays"]]
            plan_txt = (f"<p>Book <strong>{around[0]['leave']} days</strong> of leave ({short(around[0]['leaveFrom'])} – {short(around[0]['leaveTo'])}) and get <strong>{around[0]['daysOff']} days off</strong> in a row ({short(around[0]['from'])} – {short(around[0]['to'])}).</p>") if around else ""
            if not plan_txt and not h["weekend"]:
                one = res({"k": "plan", "y": y, "l": 9})[0]
                ar = [b for b in one["breaks"] if NAMES[k] in b["holidays"]]
                if ar: plan_txt = f"<p>Book <strong>{ar[0]['leave']} days</strong> ({short(ar[0]['leaveFrom'])} – {short(ar[0]['leaveTo'])}) for <strong>{ar[0]['daysOff']} days off</strong> in a row.</p>"
            lw = "a long weekend 🏖️" if h["weekday"] in (1, 5) else ("at the weekend – see how the benefit works" if h["weekend"] else "midweek")
            body = f"""<p class="lead">{NAMES[k]} {y} is on <strong>{wd} {x.day} {x.strftime('%B')}</strong> – {lw}.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts([f"Date: <strong>{wd} {x.day} {x.strftime('%B %Y')}</strong>.", facts[0]] + ([f"It falls on a {wd}: you're still entitled to the public holiday benefit – <a href='bank-holiday-on-weekend.html'>a day's pay, an extra day's leave or a day off within a month</a>."] if h['weekend'] else []))}
<h2>Turn it into a longer break</h2>{plan_txt or '<p>See the <a href="./#planner">leave planner</a> for the best days to book around it.</p>'}
<div class="ad" data-slot="content"></div>
<h2>About {NAMES[k]}</h2><p>{about}</p>
<h2>All bank holidays {y}</h2>{table(["Holiday", "Date", ""], hol_rows(y))}
<div class="btn-row">{ICS_LINK}</div>"""
            ev = {"@context": "https://schema.org", "@type": "Event", "name": f"{NAMES[k]} {y} (Ireland)", "startDate": h["date"], "endDate": h["date"],
                  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled", "location": {"@type": "Country", "name": "Ireland"}, "description": about[:200]}
            app.page(f"{SLUG[k]}-{y}.html", f"{NAMES[k]} {y} Ireland – {wd} {x.day} {x.strftime('%B')} | Bank Holiday",
                     f"{NAMES[k]} {y} in Ireland is {wd} {x.day} {x.strftime('%B %Y')}. Whether it's a long weekend, the best days to book off, and what the day means.",
                     body, jsonld=[ev, faq_ld([(f"When is {NAMES[k]} {y}?", f"{wd} {x.day} {x.strftime('%B %Y')}.")])], crumbs=[("Bank holidays", "./"), (NAMES[k], f"{SLUG[k]}.html"), (str(y), None)],
                     h1=f"{NAMES[k]} {y}", sources=("ci",), cross=CROSS, priority="0.7" if y == FOCUS else "0.5")

# ---------- Leave planner pages ----------
LEAVES = list(range(1, 11)) + [12, 15, 20, 22, 25]
def build_planner_pages():
    y = FOCUS
    plans = res(*[{"k": "plan", "y": y, "l": l} for l in LEAVES])
    rows = []
    for l, p in zip(LEAVES, plans):
        rows.append([f'<a href="annual-leave-{y}-{l}-days.html">{l} day{"s" if l > 1 else ""}</a>', str(p["used"]), f"<strong>{p['daysOff']}</strong>", f"{p['ratio']:.1f}×"])
        body = f"""<p class="lead">Got {l} day{"s" if l > 1 else ""} of annual leave to use in {y}? Book these and you'll get <strong>{p['daysOff']} days off</strong> in total.</p>
<p class="updated">Bank holidays {y} · Monday–Friday week · Checked {CHECKED}</p>
{key_facts([f"<strong>{p['used']} leave day{'s' if p['used'] != 1 else ''} → {p['daysOff']} days off</strong> – about {p['ratio']:.1f} days off for every day of leave.",
            "Each break joins your leave to weekends and bank holidays.", "Ask early – your employer decides when leave is taken, and must consult you at least a month before."])}
{plan_html(p)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Work weekends or part-time?</h2><p>Set your own working days in the planner.</p><a class="btn" href="./?leave={l}#planner">Open the leave planner</a></div>
<div class="chip-list">{"".join(f'<a href="annual-leave-{y}-{x}-days.html">{x} days</a>' for x in LEAVES if x != l)}</div>"""
        app.page(f"annual-leave-{y}-{l}-days.html", f"{l} Days Annual Leave {y} → {p['daysOff']} Days Off – Best Dates to Book (Ireland)",
                 f"How to turn {l} day{'s' if l > 1 else ''} of annual leave into {p['daysOff']} days off in {y} using Irish bank holidays and weekends – exact dates to book.",
                 body, active="Leave planner", crumbs=[("Bank holidays", "./"), ("Leave planner", "leave-planner-2027.html"), (f"{l} days", None)], h1=f"{l} days of leave → {p['daysOff']} days off in {y}",
                 sources=("ci", "ci_leave"), cross=CROSS, priority="0.6")
    body = f"""<p class="lead">How to get the most days off in {y} from your annual leave – using the bank holidays and weekends.</p>
<p class="updated">Checked {CHECKED}</p>
{key_facts(["The best value is leave next to a bank holiday weekend – 4 days around a Monday holiday gives you 9 days off.",
            f"In {y}, St Brigid's Day (Mon 1 Feb), Easter Monday (29 Mar) and the June, August and October Mondays are the easiest to stretch.", "Christmas {0} falls on a weekend, so the break between Christmas and New Year needs more leave than usual.".format(y)])}
{table(["Leave", "Used", "Days off", "Value"], rows)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Your own plan</h2><p>Your leave, your working days.</p><a class="btn" href="./#planner">Open the planner</a></div>"""
    app.page("leave-planner-2027.html", f"Annual Leave Planner {y} Ireland – Turn Your Leave Into More Days Off",
             f"Maximise your annual leave in {y}: how many days off you get for 1 to 25 days of leave using Irish bank holidays, with the exact dates to book.",
             body, active="Leave planner", crumbs=[("Bank holidays", "./"), ("Leave planner", None)], h1=f"Annual leave planner {y}", sources=("ci", "ci_leave"), cross=CROSS, priority="0.9")
    for yy in (2027, 2028):
        lw = [h for h in HOL[yy] if h["weekday"] in (1, 5)]
        body = f"""<p class="lead">Every long weekend in Ireland in {yy} – and how to turn each into a week off.</p>
{table(["Long weekend", "Dates", "Holiday"], [[f'{short((dt(h["date"]) - datetime.timedelta(days=2 if h["weekday"] == 1 else 0)).isoformat())} – {short((dt(h["date"]) + datetime.timedelta(days=0 if h["weekday"] == 1 else 2)).isoformat())}', nice(h["date"]), h["name"]] for h in lw])}
<p>Book the 4 working days after a Monday holiday (or before a Friday one) and you get 9 days off for 4 days of leave.</p>
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Plan it</h2><p>See the exact days to book.</p><a class="btn" href="./?year={yy}#planner">Open the planner</a></div>"""
        app.page(f"long-weekends-{yy}.html", f"Long Weekends Ireland {yy} – {len(lw)} Bank Holiday Weekends",
                 f"All {len(lw)} long weekends in Ireland in {yy} from bank holidays on a Monday or Friday, and how to turn each into 9 days off with 4 days of leave.",
                 body, crumbs=[("Bank holidays", "./"), (f"Long weekends {yy}", None)], h1=f"Long weekends {yy}", sources=("ci",), cross=CROSS, priority="0.7")

# ---------- School holidays ----------
def build_school():
    hub_rows = []
    for sy, breaks in SCHOOL.items():
        a, b = sy.split("-")
        rows = [[name, f"{nice(s, False)} – {nice(e, False)}"] for name, s, e in breaks]
        hub_rows += [[f'<a href="school-holidays-{sy}.html">{a}/{b}</a> – {name}', f"{short(s)} – {short(e)} {dt(e).year}"] for name, s, e in breaks]
        notes = ["<strong>February mid-term:</strong> post-primary schools close for the full week; primary schools must close Thursday and Friday and may use discretionary days to close the full week.",
                 "<strong>Christmas:</strong> the last school day is " + nice((dt(breaks[1][1]) - datetime.timedelta(days=1)).isoformat()) + ".",
                 "<strong>Easter:</strong> the last day of term is " + nice((dt(breaks[3][1]) - datetime.timedelta(days=3)).isoformat()) + "; schools reopen " + nice((dt(breaks[3][2]) + datetime.timedelta(days=3)).isoformat()) + ".",
                 "Schools may shorten the February and Easter breaks to make up for unplanned closures (for example, storms).", "Start and end of the school year vary by school – check your school's calendar."]
        body = f"""<p class="lead">The official school holiday dates for {a}/{b} for all primary and post-primary schools in Ireland.</p>
<p class="updated">Department of Education Circular 0018/2026 · Checked {CHECKED}</p>
{table(["Break", "Dates (schools closed)"], rows)}
{key_facts(notes)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Match your leave to the kids' holidays</h2><p>Tick "school holidays" in the planner.</p><a class="btn" href="./#planner">Open the leave planner</a></div>
<p>Paying for childcare in the breaks? See what you can claim back: <a href="../tax-refund/" data-track="cross_app" data-label="taxrefund_from_holidays">tax refund checker →</a></p>"""
        app.page(f"school-holidays-{sy}.html", f"School Holidays {a}/{b} Ireland – Mid-Term, Christmas & Easter Dates",
                 f"Official Irish school holidays {a}/{b}: October mid-term {short(breaks[0][1])}–{short(breaks[0][2])}, Christmas, February mid-term and Easter break dates for primary and secondary schools.",
                 body, active="School holidays", jsonld=[faq_ld([(f"When are the school holidays in {a}/{b} in Ireland?", "; ".join(f"{n}: {nice(s, False)} to {nice(e, False)}" for n, s, e in breaks))])],
                 crumbs=[("Bank holidays", "./"), ("School holidays", "school-holidays.html"), (f"{a}/{b}", None)], h1=f"School holidays {a}/{b}", sources=("school",), cross=CROSS, priority="0.9")
        for name, s, e in breaks:
            slug = name.lower().replace(" ", "-") + f"-{dt(s).year}"
            body = f"""<p class="lead">{name} {dt(s).year}: schools in Ireland are closed from <strong>{nice(s)}</strong> to <strong>{nice(e)}</strong>.</p>
<p class="updated">Department of Education Circular 0018/2026 · Checked {CHECKED}</p>
{key_facts(notes[:1] if 'February' in name else notes[1:2] if name == 'Christmas' else notes[2:3] if name == 'Easter' else ["All primary and post-primary schools close for the full week."])}
<h2>All school holidays {a}/{b}</h2>{table(["Break", "Dates"], rows)}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Need time off to match?</h2><p>Find the best days to book.</p><a class="btn" href="./#planner">Leave planner</a></div>"""
            app.page(f"school-{slug}.html", f"{name} {dt(s).year} Ireland – School Holiday Dates ({short(s)} – {short(e)})",
                     f"{name} {dt(s).year} in Ireland: schools close {nice(s, False)} to {nice(e, False)}. Official dates for primary and secondary schools.",
                     body, active="School holidays", crumbs=[("Bank holidays", "./"), ("School holidays", "school-holidays.html"), (f"{name} {dt(s).year}", None)], h1=f"{name} {dt(s).year}", sources=("school",), cross=CROSS, priority="0.7")
    body = f"""<p class="lead">Official school holiday dates in Ireland for the next three school years, agreed by the Department of Education.</p>
{table(["Break", "Dates"], hub_rows)}
<div class="ad" data-slot="content"></div>"""
    app.page("school-holidays.html", "School Holidays Ireland 2026/27, 2027/28, 2028/29 – Official Dates",
             "Official Irish school holiday dates: October and February mid-terms, Christmas and Easter for 2026/27, 2027/28 and 2028/29 (Department of Education).",
             body, active="School holidays", crumbs=[("Bank holidays", "./"), ("School holidays", None)], h1="School holidays in Ireland", sources=("school",), cross=CROSS, priority="0.9")

# ---------- Rights & guides ----------
def build_guides():
    body = f"""<p class="lead">What you're entitled to on a bank holiday in Ireland – full-time, part-time, sick, or on leave.</p>
<p class="updated">Citizens Information · Organisation of Working Time Act 1997 · Checked {CHECKED}</p>
{key_facts(["Full-time employees are entitled to public holiday benefit straight away.", "Part-time employees qualify if they worked <strong>40 hours in the 5 weeks</strong> before the holiday (annual leave counts as time worked).",
            "Your employer chooses one of: <strong>a paid day off on the day</strong>, <strong>an extra day of annual leave</strong>, <strong>an extra day's pay</strong>, or <strong>a paid day off within a month</strong>.",
            "Ask at least <strong>21 days</strong> before which one applies. If your employer doesn't answer 14 days before, you get the day itself off with pay.",
            "Work the holiday? You get one of the other options – usually an extra day's pay or a day in lieu.", "Part-timers who don't normally work that day get <strong>one-fifth of their weekly pay</strong>.",
            "Complaints go to the Workplace Relations Commission within 6 months."])}
<div class="ad" data-slot="content"></div>
<h2>Sick, on leave or laid off</h2>{lis(["On sick leave: you're still entitled to the benefit (unless off more than 26 weeks, or 52 for an occupational injury).", "On maternity, paternity, parent's, parental or adoptive leave: you keep your public holiday entitlement.",
    "Laid off: entitled for the first 13 weeks of lay-off.", "Leaving the job: if you finish in the week before a holiday and worked the previous 4 weeks, you get an extra day's pay."])}
<p><a href="bank-holiday-on-weekend.html">What if the holiday falls on a weekend? →</a> · <a href="annual-leave.html">Annual leave calculator →</a></p>"""
    faqs = [("Do I get paid for a bank holiday in Ireland?", "Most employees do – full-time straight away, part-time after 40 hours in the previous 5 weeks. Your employer gives a paid day off, an extra day's leave, an extra day's pay or a day off within a month."),
            ("Do part-time workers get bank holidays?", "Yes, if they worked 40 hours in the 5 weeks before. If they don't normally work that day, they get one-fifth of their weekly pay.")]
    app.page("public-holiday-rights.html", "Bank Holiday Rights Ireland – Pay, Part-Time, Working on a Public Holiday",
             "Your public holiday entitlements in Ireland: paid day off, extra day's leave, extra day's pay or a day within a month; part-time 40-hour rule; working a bank holiday; sick leave.",
             body, active="Your rights", jsonld=[faq_ld(faqs)], crumbs=[("Bank holidays", "./"), ("Your rights", None)], h1="Your public holiday rights", sources=("ci", "wrc", "act"), cross=CROSS, priority="0.9")

    wk = [(y, h) for y in YEARS for h in HOL[y] if h["weekend"]]
    body = f"""<p class="lead">When a bank holiday falls on a Saturday or Sunday – like Christmas Day and St Stephen's Day {FOCUS} – do you get a day off?</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
{key_facts(["You are <strong>still entitled to the public holiday benefit</strong>, even if it falls on a day you don't work.", "But there's <strong>no automatic right to the next Monday off</strong>.",
            "Your employer gives you one of: a paid day off within a month, an extra day of annual leave, or an extra day's pay.", "Many employers give the following Monday and Tuesday off – check your contract or ask 21 days in advance."])}
<h2>Bank holidays on a weekend, {YEARS[0]}–{YEARS[-1]}</h2>{table(["Year", "Holiday", "Day"], [[str(y), h["name"], nice(h["date"])] for y, h in wk])}
<div class="ad" data-slot="content"></div>"""
    app.page("bank-holiday-on-weekend.html", f"Bank Holiday on a Weekend Ireland – Do You Get the Monday Off? (Christmas {FOCUS})",
             f"When an Irish public holiday falls on a weekend (Christmas Day and St Stephen's Day {FOCUS}), you still get the benefit – but not automatically the Monday off. Your options.",
             body, active="Your rights", jsonld=[faq_ld([("Do you get a day off if a bank holiday falls on a weekend in Ireland?", "You're entitled to the benefit (a paid day off within a month, an extra day's leave or an extra day's pay), but not automatically the next working day off.")])],
             crumbs=[("Bank holidays", "./"), ("Holiday on a weekend", None)], h1="What if a bank holiday falls on a weekend?", sources=("ci", "wrc"), cross=CROSS, priority="0.8")

    body = f"""<p class="lead">How much annual leave you're entitled to in Ireland – full-time, part-time or zero-hours – with a calculator.</p>
<p class="updated">Citizens Information · Checked {CHECKED}</p>
<div class="card"><div class="tl">Annual leave calculator</div>
<div class="three"><label>Hours worked this leave year<input id="alHours" type="number" inputmode="decimal" min="0" value="1000"></label><label>Days per week<input id="alDays" type="number" min="1" max="7" value="3"></label><label>Hours per day<input id="alHpd" type="number" min="1" max="14" step="0.5" value="8"></label></div>
<div class="pts-hero"><div class="amt" id="alOut">–</div><p id="alSub"></p></div></div>
{key_facts(["Most employees get <strong>4 working weeks</strong> a year (20 days for a 5-day week).", "Three ways to calculate – you get whichever is <strong>best</strong> for you: 4 weeks if you worked 1,365+ hours; a third of a week for each month with 117+ hours; or <strong>8% of hours worked</strong> (max 4 weeks).",
            "Part-time workers usually use the 8% method.", "Leave keeps building up while on certified sick leave, maternity, paternity, parental and adoptive leave.", "Sick while on holiday? Get a medical cert and those days don't count as leave.",
            "Your employer decides when you take leave, but must consult you at least a month before. Leave can be carried over up to 6 months by agreement (15 months if you couldn't take it due to illness).",
            "Leaving your job? You must be paid for leave you haven't taken.", "The legal leave year runs 1 April – 31 March, though many employers use January–December."])}
<div class="ad" data-slot="content"></div>
<div class="cta"><h2>Now make it go further</h2><p>Turn your leave into the most days off.</p><a class="btn" href="./#planner">Leave planner</a></div>
<script>(function(){{function n(i){{return parseFloat(document.getElementById(i).value)||0}}function r(){{var o=IEHOL.annualLeave(n("alHours"),n("alDays"),n("alHpd"),0);document.getElementById("alOut").textContent=o.days+" days";document.getElementById("alSub").textContent=o.hours+" hours of paid leave (method "+o.method+")"}}["alHours","alDays","alHpd"].forEach(function(i){{document.getElementById(i).addEventListener("input",r)}});r()}})();</script>"""
    app.page("annual-leave.html", "Annual Leave Entitlement Ireland – Calculator for Full-Time & Part-Time (8% Rule)",
             "How much annual leave are you entitled to in Ireland? 4 working weeks, or 8% of hours worked for part-time. Calculator, sick leave, carry-over and leaving a job.",
             body, active="Annual leave", jsonld=[faq_ld([("How many days annual leave am I entitled to in Ireland?", "4 working weeks a year for most employees. Part-time workers usually get 8% of the hours they work, up to 4 weeks.")])],
             crumbs=[("Bank holidays", "./"), ("Annual leave", None)], h1="Annual leave entitlement", sources=("ci_leave", "wrc_leave", "act"), cross=CROSS, priority="0.9", scripts=["js/holidays.js"])

    gf = [[str(y), nice((dt(res({"k": "easter", "y": y})[0]) - datetime.timedelta(days=2)).isoformat())] for y in YEARS]
    body = f"""<p class="lead">No – Good Friday is <strong>not a public holiday</strong> in Ireland, even though many schools and businesses close.</p>
{key_facts(["You have <strong>no automatic right</strong> to the day off or extra pay on Good Friday.", "Many employers give it off anyway – check your contract.", "Schools are normally already on Easter holidays.", "Easter Monday <strong>is</strong> a public holiday."])}
{table(["Year", "Good Friday"], gf)}
<div class="ad" data-slot="content"></div>"""
    app.page("good-friday.html", "Is Good Friday a Bank Holiday in Ireland? No – Here's Why",
             "Good Friday is not a public holiday in Ireland – no automatic day off or extra pay, though many businesses close. Good Friday dates 2026–2030.",
             body, jsonld=[faq_ld([("Is Good Friday a bank holiday in Ireland?", "No. Good Friday is not a public holiday, although many schools and businesses close.")])],
             crumbs=[("Bank holidays", "./"), ("Good Friday", None)], h1="Is Good Friday a bank holiday?", sources=("ci",), cross=CROSS, priority="0.7")

    FAQ = [("How many public holidays are there in Ireland?", "10 a year since 2023, when St Brigid's Day was added."),
           ("What is the difference between a bank holiday and a public holiday?", "In everyday speech they mean the same thing. 'Public holiday' is the legal term in Ireland."),
           ("Is St Brigid's Day always 1 February?", "No – the holiday is the first Monday in February, unless 1 February is a Friday."),
           ("Is Christmas Eve a bank holiday?", "No. Neither is Good Friday or Halloween."),
           ("Do I get double pay on a bank holiday?", "Not by law. If you work, you're entitled to a paid day off within a month, an extra day's leave or an extra day's pay – your contract may give more."),
           ("Do part-time workers get bank holidays?", "Yes, after 40 hours' work in the previous 5 weeks."),
           ("What happens if a bank holiday falls on a weekend?", "You still get the benefit, but no automatic Monday off."),
           ("When is Easter Monday 2027?", "29 March 2027."),
           ("Can I add these to my phone calendar?", "Yes – use the 'Add to your calendar' button for every holiday from 2026 to 2030.")]
    app.page("faq.html", "Bank Holidays Ireland FAQ – Christmas Eve, Good Friday, Double Pay, Part-Time",
             "Irish bank holiday questions answered: how many there are, St Brigid's Day rule, Christmas Eve and Good Friday, double pay, part-time workers and weekend holidays.",
             f'<p class="lead">Common questions about Irish bank holidays.</p><p class="updated">Checked {CHECKED}</p>' + faq_html(FAQ),
             active="FAQ", jsonld=[faq_ld(FAQ)], crumbs=[("Bank holidays", "./"), ("FAQ", None)], h1="Bank holidays FAQ", sources=("ci", "wrc"), cross=CROSS, priority="0.8")

if __name__ == "__main__":
    build_index(); build_years(); build_holidays(); build_planner_pages(); build_school(); build_guides()
    with open(os.path.join(app.root, "ireland-public-holidays.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(res({"k": "ics", "ys": YEARS})[0])
    og_image(os.path.join(app.root, "og.png"), "IRELAND 2027", "Bank holidays", "& leave planner", "All 10 dates · school holidays", "Turn your leave into more days off",
             "tavion.ie/bank-holidays  ·  free, no sign-up", (252, 211, 77), (180, 83, 9), (70, 35, 5))
    app.update_sitemap()
    h27 = "; ".join(f"{h['name']} {h['date']}" for h in HOL[2027])
    app.update_llms("- [Bank Holidays Ireland & Leave Planner](https://tavion.ie/bank-holidays/): all Irish public holidays 2026-2030, an annual leave planner, school holiday dates 2026/27-2028/29, public holiday and annual leave rights.",
                    "Bank holidays: key facts",
                    f"""- Ireland has 10 public holidays (St Brigid's Day added 2023: first Monday in February, or 1 February if a Friday). Good Friday, Christmas Eve and Halloween are not public holidays.
- 2027: {h27}. Christmas Day and St Stephen's Day 2027 fall on a weekend: employees still get the benefit (paid day off within a month, extra day of annual leave, or extra day's pay) but no automatic next-day off.
- Entitlement: full-time immediately; part-time after 40 hours in the previous 5 weeks (non-working day = one-fifth of weekly pay). Ask 21 days before which option applies.
- Annual leave: 4 working weeks; or 1/3 week per month with 117+ hours; or 8% of hours worked (max 4 weeks), whichever is greater.
- School holidays 2026/27 (Circular 0018/2026): October mid-term 26-30 Oct 2026; Christmas: last day 22 Dec 2026, reopen 6 Jan 2027; February mid-term 15-19 Feb 2027 (primary must close 18-19 Feb); Easter: last day 19 Mar 2027, reopen 5 Apr 2027.
- Pages: [2027 & planner](https://tavion.ie/bank-holidays/), [Leave planner 2027](https://tavion.ie/bank-holidays/leave-planner-2027.html), [School holidays](https://tavion.ie/bank-holidays/school-holidays.html), [Rights](https://tavion.ie/bank-holidays/public-holiday-rights.html), [Calendar file (.ics)](https://tavion.ie/bank-holidays/ireland-public-holidays.ics). Source: citizensinformation.ie, gov.ie.""")
    print("Built", len(app.files), "pages in", app.root)
