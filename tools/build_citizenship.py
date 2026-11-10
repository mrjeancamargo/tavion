"""
Builds the static pages of the Irish Citizenship app (tavion.ie/citizenship/).

Run from the repo root:   python tools/build_citizenship.py
Edit the content below (stamps, FAQ, requirements) and re-run to regenerate every page,
so headers, SEO tags, share buttons and ad slots stay consistent.
"""
import json, os
from urllib.parse import quote

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "citizenship")
BASE = "https://tavion.ie/citizenship/"
CHECKED = "November 2026"
ISD = "https://www.irishimmigration.ie/how-to-become-a-citizen/become-an-irish-citizen-by%20-naturalisation/"
ISD_STAMPS = "https://www.irishimmigration.ie/registering-your-immigration-permission/information-on-registering/immigration-permission-stamps/"
ISD_PROOFS = "https://www.irishimmigration.ie/how-to-become-a-citizen/become-an-irish-citizen-by-naturalisation/proofs-of-identity-and-residence/"

TABS = [("./", "Calculator"), ("tracker.html", "Tracker"), ("stamps.html", "Stamps"),
        ("requirements.html", "Requirements"), ("faq.html", "FAQ")]

WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3z"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'

# ---------------------------------------------------------------- stamps
# reck: "yes" | "no" | "check" (treated as counting in the calculator, but confirm with ISD) | "na"
STAMPS = [
    dict(slug="stamp-0", name="Stamp 0", short="Temporary stay for people of independent means", reck="no", work="No, unless your permission letter says you can.",
         what="Stamp 0 is a temporary permission to live in Ireland without working. It is for people who can fully support themselves, or who are fully supported by a sponsor living in Ireland.",
         who=["People retiring to Ireland or living here as a person of independent means", "Visiting academics at an Irish university or college",
              "Elderly dependent relatives of an Irish citizen, or of a non-EU/EEA national living in Ireland"],
         conditions=["You (or your sponsor) must be fully financially self-sufficient", "No social welfare payments or publicly funded services, such as treatment in a public hospital",
                     "You must have private medical insurance", "No work or business unless your letter of permission allows it",
                     "You must apply and be approved for Stamp 0 before you can register it"],
         counts="Stamp 0 is not one of the permissions in ISD's own naturalisation residency calculator, so time on Stamp 0 is generally not treated as reckonable residence for citizenship. If you later move to a permission that counts, such as Stamp 4, only the time from that point is counted. If your situation is unusual, ask ISD.",
         tips=["If citizenship is your long-term goal, check whether you could qualify for a permission that counts", "Keep your Stamp 0 registered and renewed on time – gaps cause problems with any future application"],
         related=["stamp-4", "stamp-5", "stamp-3"]),
    dict(slug="stamp-1", name="Stamp 1", short="Permission to work or run a business", reck="yes", work="Yes – in line with your employment permit, or as your ISD letter allows.",
         what="Stamp 1 is permission to work in Ireland (or run a business) for a set period. You normally need a valid employment permit, or a letter from ISD saying you can work without one.",
         who=["Holders of an employment permit, such as a General Employment Permit or Critical Skills Employment Permit (CSEP)",
              "People given permission to operate a business in Ireland", "People on a Working Holiday Authorisation (this permission can't be renewed or changed)"],
         conditions=["Don't start a job unless you hold an employment permit for it, or your letter says you don't need one", "No business, trade or profession unless your ISD letter allows it",
                     "Apply to renew your permission and registration before they expire"],
         counts="Yes. ISD confirms Stamp 1 is reckonable residence for citizenship by naturalisation. Every day covered by a valid, registered Stamp 1 counts towards the 1,826 days you need.",
         tips=["After 2 years on a Critical Skills Employment Permit, or 5 years on other employment permits, you may be able to move to Stamp 4",
               "Renew before your IRP expires – a gap between permissions isn't reckonable and breaks the continuous year before you apply",
               "Keep payslips, P60s / employment detail summaries and bank statements for each year – you'll need them as proof of residence"],
         related=["stamp-1g", "stamp-4", "stamp-1h"]),
    dict(slug="stamp-1a", name="Stamp 1A", short="Trainee accountants", reck="yes", work="Only in your accountancy traineeship.",
         what="Stamp 1A is permission to take part in full-time, paid accountancy training in Ireland with a training contract with a company based here, for a set period.",
         who=["Non-EU/EEA trainee accountants in full-time, paid training under the immigration rules for trainee accountants"],
         conditions=["No other business, trade or profession unless your ISD letter allows it", "This is a time-limited permission – your accountancy course must be completed within 4 years",
                     "Renew before expiry, or apply for another permission such as an employment permit"],
         counts="Yes. Stamp 1A is one of the reckonable permissions in ISD's naturalisation residency calculator, so time on Stamp 1A counts towards citizenship.",
         tips=["Plan your next permission before your Stamp 1A ends so there is no gap", "Keep proof of residence for every year (for example employment summaries and bank statements)"],
         related=["stamp-1", "stamp-4", "stamp-2"]),
    dict(slug="stamp-1g", name="Stamp 1G", short="Graduates, and spouses of Critical Skills permit holders", reck="yes", work="Yes, full-time without an employment permit (but not self-employed).",
         what="Stamp 1G is given in two situations: to non-EU/EEA students who have finished a qualifying course in Ireland and are looking for work (the Third Level Graduate Programme), and to spouses or de facto partners of Critical Skills Employment Permit holders or of researchers on a Hosting Agreement.",
         who=["Graduates on the Third Level Graduate Programme – usually 12 months, with a possible further 12 months for master's graduates (subject to conditions)",
              "Spouses or de facto partners of Critical Skills Employment Permit holders", "Spouses or de facto partners of researchers in Ireland on a Hosting Agreement"],
         conditions=["You can work full-time without an employment permit", "You can't run a business or be self-employed",
                     "Graduates: your other conditions stay the same as on Stamp 2", "Spouses/partners: renew every year; after 5 years on Stamp 1G you may apply for Stamp 4"],
         counts="Yes. ISD says time on Stamp 1G – both as a graduate and as the spouse or partner of a CSEP holder or researcher – is reckonable residence for citizenship. (On ISD's own calculator you enter Stamp 1G as Stamp 1.)",
         tips=["Your earlier Stamp 2 student years don't count, but your Stamp 1G time does – the clock starts with your first Stamp 1G",
               "Line up your employment permit before Stamp 1G ends so there's no gap", "Spouses: keep renewing on time – the continuous year before you apply can't have gaps"],
         related=["stamp-2", "stamp-1", "stamp-4"]),
    dict(slug="stamp-1h", name="Stamp 1H", short="Hospital doctors (NCHDs) on a multi-site permit", reck="yes", work="Yes, as an NCHD under your permit.",
         what="Stamp 1H is for doctors holding a two-year multi-site General Employment Permit to work as a Non-Consultant Hospital Doctor (NCHD) in public hospitals or health facilities.",
         who=["NCHDs with a two-year multi-site General Employment Permit"],
         conditions=["Your employer must tell the Department of Enterprise, Trade and Employment about changes of location or contract before they happen",
                     "You can move to a different hospital within the HSE group at the end of your initial contract, with a valid contract",
                     "Conditions similar to Critical Skills Employment Permit holders apply, including for your spouse or family"],
         counts="Yes. ISD confirms Stamp 1H is reckonable residence when applying for citizenship by naturalisation.",
         tips=["Doctors can use a Medical Practitioner Employment History Summary as proof of residence", "Renew on time so there are no gaps between permissions"],
         related=["stamp-1", "stamp-1g", "stamp-4"]),
    dict(slug="stamp-2", name="Stamp 2", short="Full-time students on an ILEP course", reck="no", work="Casual work only: up to 20 hours a week in term, 40 hours in holidays.",
         what="Stamp 2 is permission to study a full-time course on the Interim List of Eligible Programmes (ILEP) for a set period.",
         who=["Students of English language courses, higher diplomas, degrees, master's and PhDs on the ILEP"],
         conditions=["Casual work only: up to 20 hours a week during term and 40 hours a week during holidays", "No social welfare or publicly funded services (unless you're entitled another way)",
                     "Student permission is limited to a maximum of 7 years in total", "English language students: maximum three 25-week courses and at least 85% attendance",
                     "You must show progression in your studies each year"],
         counts="No. ISD states Stamp 2 is not reckonable residence. Years spent studying on Stamp 2 do not count towards the 1,826 days for citizenship.",
         tips=["When you graduate, Stamp 1G (Third Level Graduate Programme) does count – that is often where the citizenship clock starts",
               "Keep your student permission valid until you move to your next stamp"],
         related=["stamp-2a", "stamp-1g", "stamp-1"]),
    dict(slug="stamp-2a", name="Stamp 2A", short="Full-time study on a non-ILEP course", reck="no", work="No.",
         what="Stamp 2A is permission for full-time study on a course that is not on the Interim List of Eligible Programmes (ILEP).",
         who=["Semester-abroad students at an Irish university or college", "Students at private secondary schools", "In limited cases, spouses of financially independent students"],
         conditions=["No work, business, trade or profession", "No social welfare or publicly funded services", "You must have private medical insurance"],
         counts="No. ISD states Stamp 2A is not reckonable residence for citizenship by naturalisation.",
         tips=["Only time on a reckonable permission (such as Stamp 1, 1G, 3 or 4) counts – plan your next permission carefully"],
         related=["stamp-2", "stamp-1g", "stamp-3"]),
    dict(slug="stamp-3", name="Stamp 3", short="Volunteers, ministers of religion, and family joining a work-permit holder", reck="yes", work="No.",
         what="Stamp 3 is permission to stay in Ireland for a set period without working. It's often given to family members joining someone here on an employment permit.",
         who=["Volunteers (for example with a charity or non-profit)", "Ministers of religion",
              "Spouses, civil partners or family members joining a non-EU/EEA person who is here on an employment permit"],
         conditions=["You can't work or run a business, trade or profession", "Renew your permission and registration before they expire"],
         counts="Yes. ISD confirms Stamp 3 is reckonable residence for citizenship by naturalisation, even though you can't work on it.",
         tips=["Spouses on Stamp 3 can build up citizenship time in their own right – keep your own proofs of residence (bills, bank statements, letters) in your name",
               "Keep your Stamp 3 renewed with no gaps"],
         related=["stamp-1g", "stamp-4", "stamp-1"]),
    dict(slug="stamp-4", name="Stamp 4", short="Long-term residence, spouses of Irish citizens, refugees and more", reck="yes", work="Yes, without an employment permit, and you can run a business.",
         what="Stamp 4 is permission to stay in Ireland for a set period with the right to work without an employment permit and to set up a business. It's one of the most common routes to citizenship.",
         who=["People who held a Critical Skills Employment Permit for 2 years, another employment permit for 5 years, or were a researcher on a Hosting Agreement for 2 years",
              "Spouses, civil partners or de facto partners of Irish citizens", "Recognised refugees, people with subsidiary protection, and family joining them",
              "Parents of an Irish citizen child", "Investor and Entrepreneur Programme participants and their families", "Long-term residence permission holders"],
         conditions=["You can work without an employment permit and work in a profession (subject to professional body rules)", "You can set up and run a business",
                     "You may access State funds and services as set by Government departments", "Renew your permission and registration before they expire"],
         counts="Yes. ISD confirms Stamp 4 is reckonable residence for citizenship by naturalisation.",
         tips=["Spouses of Irish citizens may qualify after 3 years' residence (with 3 years of marriage) – choose the spouse route in the calculator",
               "Refugees can apply 5 years from the exact date international protection was granted", "Keep renewing on time – a gap breaks the continuous year before you apply"],
         related=["stamp-5", "stamp-1", "stamp-4-eu-fam"]),
    dict(slug="stamp-4d", name="Stamp 4D", short="Non-EU family members of UK citizens", reck="check", work="Yes – similar to Stamp 4.",
         what="Stamp 4D is for eligible non-EU/EEA family members of UK citizens who came to live in Ireland after 1 January 2021 (after Brexit).",
         who=["Non-EEA spouses, partners and family members of UK citizens living in Ireland"],
         conditions=["Conditions are set out in ISD's Brexit policy for family members of UK citizens", "Renew your permission and registration before they expire"],
         counts="Stamp 4D isn't listed separately in ISD's residency calculator. It is usually entered as Stamp 4 (which is reckonable), and our calculator counts it the same way – but confirm with ISD before relying on it for your application.",
         tips=["Keep a copy of your permission letter showing the permission type and dates", "Keep proofs of residence in your own name for every year"],
         related=["stamp-4", "stamp-4-eu-fam", "stamp-5"]),
    dict(slug="stamp-4-eu-fam", name="Stamp 4 EU FAM", short="Family members of EU/EEA/Swiss citizens", reck="check", work="Yes.",
         what="Family members of EU, EEA or Swiss citizens who are exercising their EU Treaty Rights in Ireland can get a residence card (often called Stamp 4 EU FAM).",
         who=["Non-EU spouses, civil partners, children and some dependent relatives of EU/EEA/Swiss citizens living and working in Ireland"],
         conditions=["Your EU family member must be exercising Treaty Rights in Ireland (for example working, self-employed or studying with means)",
                     "The residence card is usually valid for 5 years, after which permanent residence can be applied for"],
         counts="Time as the family member of an EU citizen exercising Treaty Rights is lawful residence and is generally counted. Our calculator counts it, but confirm your own case with ISD.",
         tips=["Keep proof that your EU family member was exercising Treaty Rights during the time you claim", "Keep your residence card renewed with no gaps"],
         related=["stamp-4", "stamp-4d", "stamp-5"]),
    dict(slug="stamp-5", name="Stamp 5", short="Permission without condition as to time", reck="yes", work="Yes.",
         what="Stamp 5 means you have permission to stay in Ireland 'without condition as to time' (WCATT). It's valid until the expiry date of your passport.",
         who=["People granted permission to remain without condition as to time after a long period of lawful residence"],
         conditions=["You must apply and be approved for Stamp 5 before registering it", "It's valid until your passport expires – transfer it to your new passport"],
         counts="Yes. ISD confirms Stamp 5 is reckonable residence for citizenship by naturalisation.",
         tips=["When you renew your passport, make sure your Stamp 5 permission is carried over so there is no gap"],
         related=["stamp-4", "stamp-6", "stamp-1"]),
    dict(slug="stamp-6", name="Stamp 6", short="Dual Irish citizens", reck="na", work="Yes – you're an Irish citizen.",
         what="Stamp 6 is placed in the non-Irish passport of someone who is an Irish citizen with dual citizenship. It shows you don't need immigration permission.",
         who=["Irish citizens who also hold another nationality and travel on their non-Irish passport"],
         conditions=["You don't need to register with immigration – you're a citizen"],
         counts="Not applicable – Stamp 6 holders are already Irish citizens, so they don't need to apply for naturalisation.",
         tips=["You can apply for an Irish passport"],
         related=["stamp-5", "stamp-4", "stamp-1"]),
]
BY_SLUG = {s["slug"]: s for s in STAMPS}
RECK_LABEL = {"yes": ("Counts towards citizenship", "yes"), "no": ("Does not count", "no"),
              "check": ("Generally counts – confirm with ISD", "yes"), "na": ("Not applicable", "")}

# ---------------------------------------------------------------- FAQ
FAQ = [
    ("How many days do I need to apply for Irish citizenship?",
     "<p>On the standard route you need <strong>5 years (1,825 or 1,826 days) of reckonable residence</strong> in the 9 years before you apply. That must include <strong>1 full year of continuous residence</strong> immediately before your application, and 4 years in total in the 8 years before that year. Our calculator uses 1,826 days to be safe.</p>"),
    ("What is reckonable residence?",
     "<p>It's time you lived in Ireland legally on a permission that counts for citizenship. Stamps 1, 1A, 1G, 1H, 3, 4 and 5 count. Stamps 2 and 2A (students) don't count, and neither does time as an international protection applicant or any period without a valid, registered permission. See <a href=\"stamps.html\">all stamps explained</a>.</p>"),
    ("Does time on a student visa (Stamp 2) count?",
     "<p>No. Stamp 2 and Stamp 2A are not reckonable. Time on <a href=\"stamp-1g.html\">Stamp 1G</a> after you graduate does count.</p>"),
    ("How long can I be outside Ireland in the year before I apply?",
     "<p>Up to <strong>70 days</strong> in total in the year before your application, plus up to <strong>30 extra days</strong> if the Minister accepts there were exceptional circumstances (for example family, personal or health reasons, work, study or humanitarian work). This rule has applied since 31 July 2023. Days you travel count as days in Ireland – only full days abroad are absences.</p>"),
    ("Do absences in the earlier years count against me?",
     "<p>ISD's residency calculator counts the days covered by your permissions, but the law talks about residence in Ireland. If you spent long periods abroad, ISD asks you to give as much detail as possible in your application. Our calculator shows both figures so you can see the difference.</p>"),
    ("Can I apply after my IRP or permission has expired?",
     "<p>No – ISD expects you to apply while your current permission is valid, and to keep your permission registered with no gaps. Gaps in registration can make your application ineligible.</p>"),
    ("What if I had a gap between two permissions?",
     "<p>Days in a gap aren't reckonable. A gap inside the final year before you apply also breaks your continuous residence, so you would need to wait until you have a full unbroken year again. The calculator flags gaps for you.</p>"),
    ("I'm married to an Irish citizen. What are the rules?",
     "<p>You need to have been married to (or in a civil partnership with) an Irish citizen for <strong>at least 3 years</strong>, be living together when you apply and when citizenship is granted, and have lived on the island of Ireland for <strong>3 of the last 5 years</strong> (1,095 or 1,096 days), including 1 continuous year immediately before you apply. You'll also need proof of residence for your spouse and a statutory declaration. Choose the spouse route in the <a href=\"./\">calculator</a>.</p>"),
    ("I'm a refugee. When can I apply?",
     "<p>Refugees can apply <strong>5 years from the exact date international protection was granted</strong>. There's no certification fee for recognised refugees, and there are special rules for proving identity if you don't have a passport. See <a href=\"requirements.html#refugees\">requirements for refugees</a>.</p>"),
    ("I'm from the EU, EEA, UK or Switzerland. Do I use this calculator?",
     "<p>No. You don't have immigration stamps, so you prove your residence with documents instead. You must have held EU/EEA, UK or Swiss nationality for more than 5 years – otherwise you apply as a non-EU national. See <a href=\"requirements.html#eu\">requirements for EU, UK and Swiss nationals</a>.</p>"),
    ("How much does Irish citizenship cost?",
     "<p>The application fee is <strong>€175</strong>. If you're approved, the certification fee is <strong>€950</strong> for adults, <strong>€200</strong> for minors and for a widow, widower or surviving civil partner of an Irish citizen, and <strong>€0</strong> for recognised refugees and stateless people.</p>"),
    ("What documents do I need?",
     "<p>Proof of identity worth <strong>150 points</strong> (a certified colour copy of your passport's photo page is worth 150 on its own), and proof of residence worth <strong>150 points for each year</strong> you claim – usually one Type A document (100 points) and one Type B document (50 points) per year. Copies must be certified. See <a href=\"requirements.html#proofs\">documents and the scorecard</a>.</p>"),
    ("How long does the application take?",
     "<p>ISD says most applications are processed within <strong>12 months</strong>. Some take longer. Use our <a href=\"tracker.html\">application tracker</a> to see where you are.</p>"),
    ("Is there a citizenship test or English test?",
     "<p>No. Ireland does not currently have a citizenship knowledge test or an English language test for naturalisation. You must be of good character, intend to keep living in Ireland, and attend a citizenship ceremony.</p>"),
    ("Do I have to attend a citizenship ceremony?",
     "<p>Yes. It's mandatory for successful applicants aged 18 and over. You make a declaration of fidelity to the nation and loyalty to the State, and your certificate of naturalisation arrives by post in the weeks after. Children don't attend.</p>"),
    ("When can I get an Irish passport?",
     "<p>Once you have received your certificate of naturalisation by post, you can apply for an Irish passport.</p>"),
    ("Can my application be refused?",
     "<p>Yes. The Minister for Justice has absolute discretion. If refused, you're given a reason, but there is no appeal – you can apply again. Common reasons for an application failing include not reaching 150 points on the scorecard without an explanatory affidavit, incomplete forms and poor-quality documents. You lose the application fee.</p>"),
    ("Does Stamp 1G count towards citizenship?",
     "<p>Yes. ISD confirms that Stamp 1G counts, both for graduates and for spouses or partners of Critical Skills permit holders and researchers. See <a href=\"stamp-1g.html\">Stamp 1G explained</a>.</p>"),
    ("Does Stamp 3 count towards citizenship?",
     "<p>Yes. Even though you can't work on Stamp 3, ISD confirms the time counts. See <a href=\"stamp-3.html\">Stamp 3 explained</a>.</p>"),
    ("Can I apply for my children?",
     "<p>A minor can't apply themselves – a parent or guardian applies for them. A naturalised parent can apply for their child; the Minister may also grant citizenship to children of Irish descent or association; and children born in Ireland on or after 1 January 2005 who weren't citizens at birth can apply after 1 year of continuous residence plus 2 years in the 8 years before that. See <a href=\"requirements.html#minors\">applying for a child</a>.</p>"),
    ("What is a dependant young adult application?",
     "<p>If you're aged 18–23, came to Ireland legally as part of a family, are in secondary school here (or went straight from secondary school into third level here) and still depend on your parents, you can apply as a dependant young adult. You still need to meet the adult residence requirements.</p>"),
    ("Is this calculator official?",
     "<p>No. It's an independent, free tool from Tavion that follows the same counting method as ISD's own residency calculator, plus the absence rules for the final year. Your official reckonable residence is assessed by ISD when you apply.</p>"),
]

# ---------------------------------------------------------------- page shell
def share_html(text, url, label):
    wa = "https://wa.me/?text=" + quote(text + " " + url, safe="")
    fb = "https://www.facebook.com/sharer/sharer.php?u=" + quote(url, safe="")
    return (f'<h2>Share it</h2><p class="muted">Know someone working out their citizenship date? Send them this.</p><div class="share">'
            f'<a class="btn wa" data-track="share" data-method="whatsapp" data-label="{label}" target="_blank" rel="noopener" href="{wa}">{WA_SVG}WhatsApp</a>'
            f'<a class="btn fb" data-track="share" data-method="facebook" data-label="{label}" target="_blank" rel="noopener" href="{fb}">{FB_SVG}Facebook</a></div>')

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
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in jsonld)
    footer_stamps = " · ".join(f'<a href="{s["slug"]}.html">{s["name"]}</a>' for s in STAMPS)
    extra = "".join(f'<script src="{s}"></script>' for s in scripts)
    share = share_html(share_text or "Free Irish citizenship calculator – find out when you can apply for naturalisation:", url, filename.replace(".html", ""))
    return f"""<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-adsense-account" content="ca-pub-1290266452162223">
<script src="/assets/tavion.js"></script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#12609e">
<link rel="icon" href="../images/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png">
<link rel="stylesheet" href="css/style.css">
{ld}</head>
<body>
<header class="top">
  <div class="wrap bar"><a class="logo" href="./"><b>🛂</b> Citizenship Calculator</a><a class="small" href="../" data-track="apps_click" data-label="citizenship_header">More Tavion apps</a></div>
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
    <nav aria-label="Citizenship pages"><a href="./">Calculator</a><a href="tracker.html">Application tracker</a><a href="stamps.html">All stamps</a><a href="requirements.html">Requirements &amp; fees</a><a href="faq.html">FAQ</a></nav>
    <p>Stamps explained: {footer_stamps}</p>
    <p>Information checked against Immigration Service Delivery (ISD) guidance in {CHECKED}. This is an independent, free tool from <a href="../">Tavion</a> and is not affiliated with ISD or the Department of Justice. It is general information, not legal advice – your official reckonable residence is assessed by ISD when you apply. Official source: <a href="{ISD}" rel="noopener">irishimmigration.ie</a>.</p>
    <p><a href="../privacy.html">Privacy &amp; cookies</a> · <a href="../" data-track="apps_click" data-label="citizenship_footer">More free apps from Tavion</a></p>
  </div>
</footer>
<script src="js/site.js"></script>{extra}
</body>
</html>
"""

def write(name, html):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

def lis(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def reck_badge(s):
    text, cls = RECK_LABEL[s["reck"]]
    return f'<span class="yes-no {cls}">{"✅" if s["reck"] in ("yes", "check") else ("❌" if s["reck"] == "no" else "➖")} {text}</span>'

# ---------------------------------------------------------------- calculator (index)
def build_index():
    reck_rows = "".join(f'<tr><td><a href="{s["slug"]}.html">{s["name"]}</a></td><td>{s["short"]}</td><td>{reck_badge(s)}</td></tr>' for s in STAMPS)
    body = f"""<p class="lead">Work out your reckonable residence and the earliest date you can apply for Irish citizenship by naturalisation. Free, no sign-up, and your dates never leave your phone.</p>
<ul class="facts"><li>1,826 days in 9 years</li><li>1 unbroken year before applying</li><li>Max 70 days abroad that year</li></ul>
<p class="updated">Rules checked against official ISD guidance: {CHECKED}</p>

<form id="calc" class="card" novalidate>
  <fieldset>
    <legend>1. How are you applying?</legend>
    <label class="radio"><input type="radio" name="route" value="standard" checked><span>Residence – 5 years<small>Most people: 1,826 reckonable days in the last 9 years</small></span></label>
    <label class="radio"><input type="radio" name="route" value="spouse"><span>Married to / civil partner of an Irish citizen – 3 years<small>1,096 days in the last 5 years, married 3+ years and living together</small></span></label>
    <p class="muted small">Refugee, EU/UK national or applying for a child? See <a href="requirements.html">requirements for every route</a>.</p>
  </fieldset>

  <fieldset>
    <legend>2. When do you want to apply?</legend>
    <label for="appDate">Application date</label>
    <input type="date" id="appDate">
  </fieldset>

  <fieldset>
    <legend>3. Your immigration permissions (IRP stamps)</legend>
    <p class="muted small">Add each permission from oldest to newest, using the dates on your IRP card or permission letters. Include student stamps too – we'll show which ones count.</p>
    <div id="stamps"></div>
    <button type="button" class="btn block" id="addStamp" style="margin-top:10px">+ Add another permission</button>
    <label class="check" style="margin-top:14px"><input type="checkbox" id="assume" checked><span>My current permission will be renewed with no gaps (used to predict future dates)</span></label>
  </fieldset>

  <fieldset>
    <legend>4. Time spent outside Ireland</legend>
    <p class="muted small">Add holidays and trips abroad, especially in the last 12 months. Travel days count as days in Ireland.</p>
    <div id="trips"></div>
    <button type="button" class="btn block" id="addTrip" style="margin-top:10px">+ Add a trip abroad</button>
  </fieldset>

  <div class="btn-row">
    <button type="submit" class="btn primary">Calculate my date</button>
    <button type="button" class="btn" id="clearAll">Clear all</button>
  </div>
  <p class="muted small">🔒 Your dates are saved only on this device so you can come back and update them. Nothing is sent to us.</p>
</form>

<div id="result" aria-live="polite"></div>

<h2>How the calculator works</h2>
<div class="card">
  <ol class="steps">
    <li><strong>Reckonable days.</strong> We count every day covered by a permission that counts, in the 9 years (or 5 for spouses) up to your application date. Overlapping permissions are only counted once – the same way ISD's own residency calculator works.</li>
    <li><strong>Continuous year.</strong> Your permissions must cover the full year immediately before you apply with no gaps.</li>
    <li><strong>Absences.</strong> You can be abroad for up to 70 full days in that final year (up to 100 if ISD accepts exceptional circumstances).</li>
    <li><strong>Earliest date.</strong> We check every day ahead to find the first date all three conditions are met.</li>
  </ol>
</div>

<h2>Which stamps count?</h2>
<div class="table-wrap"><table><thead><tr><th>Stamp</th><th>Who it's for</th><th>Citizenship</th></tr></thead><tbody>{reck_rows}</tbody></table></div>
<p class="muted small">Time as an international protection applicant, or without a valid registered permission, doesn't count. <a href="stamps.html">Read about every stamp →</a></p>

<div class="cta"><h2>Already applied?</h2><p>Track how long your application has been with ISD and what happens next.</p><a class="btn" href="tracker.html">Open the application tracker</a></div>
"""
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Irish Citizenship Calculator", "url": BASE,
              "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "description": "Calculate reckonable residence days and the earliest date you can apply for Irish citizenship by naturalisation."}
    write("index.html", page("index.html", "Irish Citizenship Calculator 2026 – Reckonable Residence & When You Can Apply",
                             "Free Irish citizenship calculator: enter your IRP stamps and trips abroad to count your reckonable residence days and find the earliest date you can apply for naturalisation.",
                             body, active="Calculator", jsonld=[app_ld], slot="calculator", scripts=["js/calc.js"],
                             h1="Irish Citizenship Calculator",
                             share_text="Free Irish citizenship calculator 🇮🇪 Enter your IRP stamps and it tells you the exact date you can apply for naturalisation:"))

# ---------------------------------------------------------------- tracker
def build_tracker():
    body = """<p class="lead">Already applied for citizenship? Enter your dates to see how long you've been waiting, where you are in the process and what comes next.</p>
<p class="updated">ISD says most applications are processed within 12 months. Some take longer.</p>
<form id="trk" class="card" novalidate>
  <label for="t_applied">Date you submitted your application *</label><input type="date" id="t_applied" data-k="applied">
  <p class="muted small" style="margin-bottom:0">Optional – add any of these when they happen:</p>
  <div class="two">
    <label>Application number / e-vetting link received<input type="date" data-k="number"></label>
    <label>Extra documents requested<input type="date" data-k="docs"></label>
    <label>Approval letter (pay certification fee)<input type="date" data-k="approved"></label>
    <label>Ceremony date<input type="date" data-k="ceremony"></label>
    <label>Certificate received<input type="date" data-k="certificate"></label>
  </div>
  <div class="btn-row"><button type="submit" class="btn primary">Show my progress</button><button type="button" class="btn" id="t_clear">Clear</button></div>
  <p class="muted small">🔒 Saved only on this device.</p>
</form>
<div id="t_out" aria-live="polite"></div>

<h2>The stages of a citizenship application</h2>
<div class="card"><ol class="steps">
<li><strong>Apply online and pay €175.</strong> Upload certified copies of your identity (150 points) and residence proofs (150 points per year).</li>
<li><strong>Application number and e-vetting link.</strong> You get an application number and a link to complete Garda e-vetting.</li>
<li><strong>Checks and possible requests.</strong> ISD may ask for more documents or ask you to explain information in your application.</li>
<li><strong>Approval letter.</strong> ISD tells you the Minister intends to grant a certificate of naturalisation. You pay the certification fee (€950 for adults) and upload a copy of your IRP and travel document if you're from outside the EEA, Switzerland and the UK.</li>
<li><strong>Citizenship ceremony.</strong> You're invited to a ceremony to make your declaration of fidelity. It's mandatory for adults.</li>
<li><strong>Certificate by post.</strong> Your certificate of naturalisation arrives in the weeks after the ceremony – then you can apply for an Irish passport.</li>
</ol></div>
<p class="muted small">If your address or email changes during the process, you must tell ISD's Citizenship Division and give proof of the new address.</p>
<script>
(function () {
  var KEY = "tavion_citizenship_tracker_v1", DAY = 86400000;
  var STAGES = [["applied","Application submitted"],["number","Application number & e-vetting link"],["docs","Extra documents requested (if any)"],["approved","Approval letter – pay certification fee"],["ceremony","Citizenship ceremony"],["certificate","Certificate received – apply for passport"]];
  function d(s){ if(!s) return null; var p=s.split("-"); return Math.floor(Date.UTC(+p[0],+p[1]-1,+p[2])/DAY); }
  function nice(n){ return new Date(n*DAY).toLocaleDateString("en-IE",{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}); }
  var now=new Date(), today=Math.floor(Date.UTC(now.getFullYear(),now.getMonth(),now.getDate())/DAY);
  var st={}; try{ st=JSON.parse(localStorage.getItem(KEY))||{}; }catch(e){}
  var inputs=[].slice.call(document.querySelectorAll("#trk [data-k]"));
  inputs.forEach(function(i){ i.value=st[i.getAttribute("data-k")]||""; i.addEventListener("input",function(){ st[i.getAttribute("data-k")]=i.value; try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){} }); });
  function show(track){
    var out=document.getElementById("t_out"), a=d(st.applied);
    if(a===null){ out.innerHTML='<div class="verdict neutral"><p>Enter the date you submitted your application.</p></div>'; return; }
    var end = d(st.certificate) || today, days=Math.max(0,end-a), months=(days/30.44);
    var twelve=a+365, pct=Math.min(100,Math.round(days/365*100));
    var done=STAGES.filter(function(s){return st[s[0]];}).map(function(s){return s[0];});
    var lastIdx=-1; STAGES.forEach(function(s,i){ if(st[s[0]]) lastIdx=i; });
    var h='<div class="verdict '+(st.certificate?'good':'neutral')+'"><div class="big">'+(st.certificate?'🎉':'⏳')+'</div><h2>'+(st.certificate?'Congratulations – you\\'re an Irish citizen!':'You\\'ve been waiting '+months.toFixed(1)+' months')+'</h2><p>'+days.toLocaleString("en-IE")+' days since you applied on '+nice(a)+'.</p></div>';
    if(!st.certificate){
      h+='<div class="card"><div class="tl">Compared with ISD\\'s 12-month guide</div><div class="progress"><span style="width:'+pct+'%"></span></div><p class="small" style="margin:0">'+(today<twelve?('12-month mark: <strong>'+nice(twelve)+'</strong> ('+(twelve-today)+' days to go).'):('You passed the 12-month mark on <strong>'+nice(twelve)+'</strong>. Many applications take longer – you can ask ISD for an update through its Customer Service Portal.'))+'</p></div>';
    }
    var nextIdx=-1; STAGES.forEach(function(s,i){ if(nextIdx<0 && i>lastIdx && s[0]!=='docs') nextIdx=i; });
    function mo(n){ n=Math.round(n); return n===1?'1 month':n+' months'; }
    h+='<h3>Your timeline</h3><ul class="timeline">';
    STAGES.forEach(function(s,i){
      var dt=d(st[s[0]]), cls=dt!==null?'done':(i===nextIdx?'now':'');
      if(s[0]==='docs' && dt===null && lastIdx>2) return;
      var note=dt!==null?nice(dt)+(i>0?' · '+mo((dt-a)/30.44)+' after applying':''):(cls==='now'?'Next step':(s[0]==='docs'?'Only if ISD asks':'Not yet'));
      h+='<li class="'+cls+'"><span class="dot"></span><strong>'+s[1]+'</strong><br><span class="muted small">'+note+'</span></li>';
    });
    h+='</ul>';
    if(st.approved && !st.ceremony) h+='<div class="callout">Next: pay the certification fee (€950 adult, €200 minor or surviving spouse/civil partner, €0 refugees and stateless people) and watch for your ceremony invitation.</div>';
    out.innerHTML=h;
    if(track && window.TAVION && TAVION.track) TAVION.track("tracker_run",{months_waiting:Math.floor(months),stage:STAGES[Math.max(0,lastIdx)][0]});
  }
  document.getElementById("trk").addEventListener("submit",function(e){ e.preventDefault(); show(true); document.getElementById("t_out").scrollIntoView({behavior:"smooth"}); });
  document.getElementById("t_clear").addEventListener("click",function(){ st={}; try{localStorage.removeItem(KEY);}catch(e){} inputs.forEach(function(i){i.value="";}); document.getElementById("t_out").innerHTML=""; });
  if(st.applied) show(false);
})();
</script>
"""
    write("tracker.html", page("tracker.html", "Irish Citizenship Application Tracker – Processing Time & Next Steps",
                               "Applied for Irish citizenship? Track how long your naturalisation application has been with ISD, compare it with the 12-month guide and see what happens next.",
                               body, active="Tracker", crumbs=[("Citizenship", "./"), ("Application tracker", None)], h1="Citizenship application tracker",
                               share_text="Waiting on your Irish citizenship application? This free tracker shows how long you've waited and what's next:"))

# ---------------------------------------------------------------- stamps overview + detail
def build_stamps():
    cards = "".join(f'<a class="stamp-card" href="{s["slug"]}.html"><strong>{s["name"]}</strong><p>{s["short"]}</p><p>{reck_badge(s)}</p></a>' for s in STAMPS)
    body = f"""<p class="lead">Every Irish immigration stamp explained in plain English – who gets it, what you can do on it, and whether it counts towards citizenship by naturalisation.</p>
<p class="updated">Checked against ISD guidance: {CHECKED}</p>
<div class="stamp-grid">{cards}</div>
<h2>What doesn't count as reckonable residence</h2>
<div class="card">{lis(["Time on Stamp 2 or Stamp 2A (students)", "Time on Stamp 0 (not included in ISD's residency calculator)",
    "Time as an international protection (asylum) applicant – refugees can apply 5 years from the date protection was granted",
    "Any period without a valid, registered permission – for example waiting too long to renew", "Time living in Ireland unlawfully"])}</div>
<div class="callout">Keep your permission registered with no gaps. ISD warns that gaps in registration can make a citizenship application ineligible.</div>
<div class="cta"><h2>Count your days</h2><p>Enter your stamps and dates to find out exactly when you can apply.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("stamps.html", page("stamps.html", "Irish Immigration Stamps Explained (0, 1, 1G, 2, 3, 4, 5) – Which Count for Citizenship?",
                              "All Irish immigration stamps explained: Stamp 0, 1, 1A, 1G, 1H, 2, 2A, 3, 4, 4D, 4 EU FAM, 5 and 6 – who gets them, conditions, and which count as reckonable residence for citizenship.",
                              body, active="Stamps", crumbs=[("Citizenship", "./"), ("Immigration stamps", None)], h1="Irish immigration stamps explained"))

    for s in STAMPS:
        rel = "".join(f'<a class="stamp-card" href="{r}.html"><strong>{BY_SLUG[r]["name"]}</strong><p>{BY_SLUG[r]["short"]}</p></a>' for r in s["related"])
        counts_cls = "callout" if s["reck"] in ("yes", "na") else "callout warn"
        body = f"""<p class="lead">{s["short"]}.</p>
<p>{reck_badge(s)}</p>
<p class="updated">Checked against ISD guidance: {CHECKED}</p>
<h2>What is {s["name"]}?</h2><p>{s["what"]}</p>
<h2>Who gets {s["name"]}?</h2>{lis(s["who"])}
<h2>Main conditions</h2>{lis(s["conditions"])}
<p><strong>Can I work on {s["name"]}?</strong> {s["work"]}</p>
<h2>Does {s["name"]} count towards Irish citizenship?</h2><div class="{counts_cls}"><p style="margin:0">{s["counts"]}</p></div>
<h2>Tips if you're planning to apply for citizenship</h2>{lis(s["tips"])}
<div class="cta"><h2>When can you apply?</h2><p>Add your {s["name"]} dates and any other permissions to see your reckonable days and earliest application date.</p><a class="btn" href="./">Use the free calculator</a></div>
<h2>Related stamps</h2><div class="stamp-grid">{rel}</div>
<p class="muted small">Official conditions: <a href="{ISD_STAMPS}" rel="noopener">ISD – immigration permission stamps</a>.</p>"""
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f"Does {s['name']} count towards Irish citizenship?", "acceptedAnswer": {"@type": "Answer", "text": s["counts"]}},
            {"@type": "Question", "name": f"Can I work on {s['name']}?", "acceptedAnswer": {"@type": "Answer", "text": s["work"]}}]}
        yes = {"yes": "Counts for Citizenship", "no": "Does It Count for Citizenship?", "check": "Does It Count for Citizenship?", "na": "Dual Citizens"}[s["reck"]]
        write(f'{s["slug"]}.html', page(f'{s["slug"]}.html', f'{s["name"]} Ireland Explained – {yes} | Conditions & Who Gets It',
                                        f'{s["name"]} in Ireland: {s["short"].lower()}. Who gets it, what you can do, and whether {s["name"]} counts as reckonable residence for Irish citizenship.',
                                        body, active="Stamps", jsonld=[faq_ld], crumbs=[("Citizenship", "./"), ("Stamps", "stamps.html"), (s["name"], None)],
                                        h1=f'{s["name"]} Ireland explained',
                                        share_text=f'{s["name"]} explained – and whether it counts towards Irish citizenship:'))

# ---------------------------------------------------------------- requirements
def build_requirements():
    body = f"""<p class="lead">Everything you need to apply for Irish citizenship by naturalisation: who's eligible, the residence rules for each route, documents, fees and what happens after you apply.</p>
<p class="updated">Checked against ISD guidance: {CHECKED}</p>
<div class="card"><strong>On this page:</strong> <a href="#residence">5-year residence</a> · <a href="#spouse">Spouse of an Irish citizen</a> · <a href="#refugees">Refugees</a> · <a href="#minors">Children</a> · <a href="#young-adults">Young adults</a> · <a href="#eu">EU/UK/Swiss</a> · <a href="#conditions">All conditions</a> · <a href="#proofs">Documents</a> · <a href="#fees">Fees</a> · <a href="#apply">How to apply</a> · <a href="#after">After you apply</a> · <a href="#refused">If refused</a></div>

<h2 id="residence">1. Adults who have lived in Ireland for 5 years</h2>
{lis(["You must be <strong>18 or over</strong> and able to prove your identity",
      "<strong>1 year of continuous residence</strong> in Ireland immediately before you apply – you can be away for up to <strong>70 days</strong> in that year, plus up to <strong>30 more</strong> in exceptional circumstances at the Minister's discretion",
      "In the <strong>8 years before that year</strong>, a total of <strong>4 years</strong> of residence",
      "Non-EU/EEA/Swiss nationals: <strong>1,825 or 1,826 days of reckonable residence</strong> based on your permission stamps, including 365 or 366 days of continuous residence immediately before you apply",
      "Proof of residence for <strong>every year</strong> you claim",
      "You must <strong>intend to keep living in Ireland</strong>, be willing to attend a <strong>citizenship ceremony</strong> and make a declaration of fidelity, and be of <strong>good character</strong>"])}
<div class="callout">If you had permission to live here but spent long periods abroad, ISD asks you to give as much detail as possible in your application.</div>

<h2 id="spouse">2. Married to, or civil partner of, an Irish citizen</h2>
{lis(["18 or over and able to prove your identity", "Married or in a civil partnership with an Irish citizen for <strong>3 years or more</strong> – the relationship must be genuine and lasting",
      "<strong>Living with your spouse or civil partner</strong> on the date you apply and on the date citizenship is granted",
      "Lived legally on the <strong>island of Ireland for 3 of the last 5 years</strong> (1,095 or 1,096 reckonable days), including 1 full year of continuous residence immediately before you apply – again with up to 70 days abroad (+30 exceptional)",
      "Proof of residence for every year – plus proof of residence for your Irish spouse or civil partner", "A <strong>statutory declaration</strong> signed before a solicitor, Commissioner for Oaths, Peace Commissioner or Notary Public",
      "Intend to keep living in Ireland, attend a ceremony and be of good character"])}

<h2 id="refugees">3. Refugees</h2>
{lis(["18 or over with a declaration as a refugee from the Minister for Justice", "You can apply <strong>5 years from the exact date you were granted international protection</strong>",
      "Proof of residence for the past five years, with your permission kept registered with no gaps",
      "If you don't have a passport, you can prove identity with a certified copy of your Irish travel document, a letter confirming refugee status, and a passport affidavit (with your full name, date of birth, why a passport can't be obtained and how you arrived in Ireland)",
      "<strong>No certification fee</strong> for recognised refugees and stateless people"])}

<h2 id="minors">4. Applying for a child (under 18)</h2>
<p>A child can't apply for themselves – a parent, legal guardian or someone acting <em>in loco parentis</em> applies on their behalf.</p>
{lis(["<strong>Child of a naturalised parent:</strong> the parent is an Irish citizen by naturalisation and the child meets the residence conditions",
      "<strong>Irish descent or association:</strong> the Minister may grant citizenship to a child related by blood or adoption to an Irish citizen (or someone entitled to be one). Decided case by case",
      "<strong>Born in Ireland on or after 1 January 2005</strong> but not a citizen at birth: 1 year of continuous residence immediately before applying, plus 2 years in the 8 years before that. Residence in Northern Ireland doesn't count for this",
      "Documents include the child's passport and birth certificate and original school letters for the 3 years before applying"])}

<h2 id="young-adults">5. Dependant young adults (18–23)</h2>
<p>You can apply as a dependant young adult if you meet the adult requirements and you are aged 18–23, entered Ireland legally as part of a family, are in secondary school here (or went straight from secondary school into third level here), and still depend on your parents financially. A letter from your school or college can be one of your residence proofs.</p>

<h2 id="eu">6. EU, EEA, UK and Swiss nationals</h2>
<p>You don't have immigration stamps, so don't use the stamp calculator. Instead you submit documents proving how long you've lived in Ireland. You must have held EU/EEA, UK or Swiss nationality for <strong>more than 5 years</strong> – otherwise you apply as a non-EU/EEA national.</p>

<h2 id="conditions">Checklist: every condition at a glance</h2>
<div class="table-wrap"><table><thead><tr><th>Condition</th><th>Standard (5 years)</th><th>Spouse of Irish citizen</th></tr></thead><tbody>
<tr><td>Minimum age</td><td>18</td><td>18</td></tr>
<tr><td>Reckonable residence</td><td>1,825/1,826 days in 9 years</td><td>1,095/1,096 days in 5 years (island of Ireland)</td></tr>
<tr><td>Continuous year before applying</td><td>Yes</td><td>Yes</td></tr>
<tr><td>Absences allowed in that year</td><td>70 days (+30 exceptional)</td><td>70 days (+30 exceptional)</td></tr>
<tr><td>Marriage / civil partnership</td><td>–</td><td>3+ years, living together</td></tr>
<tr><td>Identity proof</td><td>150 points</td><td>150 points</td></tr>
<tr><td>Residence proof</td><td>150 points per year</td><td>150 points per year + spouse's proofs</td></tr>
<tr><td>Good character &amp; Garda vetting</td><td>Yes</td><td>Yes</td></tr>
<tr><td>Intend to keep living in Ireland</td><td>Yes</td><td>Yes</td></tr>
<tr><td>Citizenship ceremony</td><td>Yes (adults)</td><td>Yes</td></tr>
<tr><td>Citizenship or language test</td><td>None</td><td>None</td></tr>
</tbody></table></div>

<h2 id="proofs">Documents: the citizenship scorecard</h2>
<h3>Proof of identity – 150 points (once)</h3>
<p>Send one or more documents from ISD's identity scorecard that add up to 150 points. A certified colour copy of the photo page of your valid home-country passport is worth 150 points on its own. Other documents include your IRP card and driving licence. Passports go through anti-fraud checks and ISD can ask for the original.</p>
<h3>Proof of residence – 150 points for every year</h3>
{lis(["<strong>Type A</strong> documents are worth 100 points and <strong>Type B</strong> documents 50 points – send one of each for every year you claim",
      "Each document must show your <strong>name, home address and a date</strong>",
      "Examples: employment detail summary (in your own name), Department of Social Protection contribution or payment statement, bank statements showing at least three consecutive months of point-of-sale transactions in Ireland each year, household bills (gas, electricity, phone, bins, TV licence), RTB letters, hospital appointment letters, Local Property Tax or social welfare correspondence",
      "Child benefit alone isn't proof of residence",
      "Doctors in the HSE or voluntary hospitals can use a Medical Practitioner Employment History Summary",
      "All copies must be <strong>certified</strong> by a practising solicitor, Commissioner for Oaths, Peace Commissioner or Notary Public"])}
<div class="callout warn">If you can't reach 150 points for a year, include an affidavit explaining why. Not reaching the score without one is a common reason applications fail – and the fee isn't refunded.</div>
<p class="muted small">Full scorecard: <a href="{ISD_PROOFS}" rel="noopener">ISD – proofs of identity and residence</a>.</p>

<h2 id="fees">Fees</h2>
<div class="table-wrap"><table><thead><tr><th>Fee</th><th>Amount</th></tr></thead><tbody>
<tr><td>Application fee (paid online when you apply)</td><td><strong>€175</strong></td></tr>
<tr><td>Certification fee – adult</td><td><strong>€950</strong></td></tr>
<tr><td>Certification fee – minor</td><td>€200</td></tr>
<tr><td>Certification fee – widow, widower or surviving civil partner of an Irish citizen</td><td>€200</td></tr>
<tr><td>Certification fee – recognised refugee or stateless person</td><td>€0</td></tr>
</tbody></table></div>
<p class="muted small">The certification fee is only paid after your application is approved. Paper applications pay the €175 by bank draft.</p>

<h2 id="apply">How to apply</h2>
<ol class="steps">
<li><strong>Check you're eligible</strong> – use the <a href="./">calculator</a> to confirm your reckonable days and continuous year.</li>
<li><strong>Gather your proofs</strong> – 150 identity points and 150 residence points for each year, all certified.</li>
<li><strong>Complete the online application</strong> on ISD's portal and tick the statutory declaration. Spouses of Irish citizens also include their statutory declaration.</li>
<li><strong>Pay the €175 application fee</strong> online – your application isn't accepted until it's paid.</li>
<li><strong>Keep your immigration permission valid and registered</strong> while you wait, and tell ISD if your address or email changes.</li>
</ol>
<p class="muted small">Paper forms (Form 8 for adults, Forms 9–11 for minors) are only available on request through ISD's Customer Service Portal if you can't apply online.</p>

<h2 id="after">What happens after you apply</h2>
<p>ISD says most applications are processed within 12 months. You'll get an application number and a Garda e-vetting link; ISD may ask for more documents. If approved, you pay the certification fee, upload a copy of your IRP (non-EEA nationals) and are invited to a citizenship ceremony. Your certificate arrives by post in the following weeks, and then you can apply for an Irish passport. <a href="tracker.html">Track your application →</a></p>

<h2 id="refused">If your application is refused</h2>
<p>The Minister for Justice has absolute discretion. You'll be told the reason, but there's no appeal – you can apply again. Common reasons include not reaching 150 points without an explanatory affidavit and, for paper applications, incomplete forms, missing pages or declarations, and poor-quality copies.</p>
<p class="muted small">Official source: <a href="{ISD}" rel="noopener">ISD – become an Irish citizen by naturalisation</a>.</p>"""
    write("requirements.html", page("requirements.html", "Irish Citizenship Requirements 2026 – Naturalisation Rules, Documents & Fees",
                                    "Every requirement for Irish citizenship by naturalisation: 5-year and spouse routes, refugees, children, the 70-day absence rule, 150-point proofs, €175 and €950 fees, and how to apply.",
                                    body, active="Requirements", crumbs=[("Citizenship", "./"), ("Requirements", None)], h1="Irish citizenship requirements",
                                    share_text="Everything you need to apply for Irish citizenship – rules, documents and fees in one place:"))

# ---------------------------------------------------------------- FAQ
def build_faq():
    items = "".join(f'<details class="faq"><summary>{q}</summary><div>{a}</div></details>' for q, a in FAQ)
    import re
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a in FAQ]}
    body = f"""<p class="lead">Answers to the questions people ask most about Irish citizenship by naturalisation.</p>
<p class="updated">Checked against ISD guidance: {CHECKED}</p>
{items}
<div class="cta"><h2>Work out your date</h2><p>Enter your stamps and trips abroad to see exactly when you can apply.</p><a class="btn" href="./">Open the calculator</a></div>"""
    write("faq.html", page("faq.html", "Irish Citizenship FAQ 2026 – Naturalisation Questions Answered",
                           "Irish citizenship FAQ: how many days you need, which stamps count, the 70-day absence rule, spouse and refugee rules, fees, documents, processing time and ceremonies.",
                           body, active="FAQ", jsonld=[ld], crumbs=[("Citizenship", "./"), ("FAQ", None)], h1="Irish citizenship: frequently asked questions",
                           share_text="Irish citizenship questions answered – days needed, stamps, fees and more:"))

if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    build_index(); build_tracker(); build_stamps(); build_requirements(); build_faq()
    print("Built", len(os.listdir(ROOT)), "entries in", os.path.normpath(ROOT))
