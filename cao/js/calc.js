// CAO points calculator + course finder. Points rules live in cao.js (window.IECAO); courses in data/courses.json.
(function () {
  "use strict";
  var C = window.IECAO, KEY = "tavion_cao_v1";
  var $ = function (id) { return document.getElementById(id); };
  var form = $("caoForm"), out = $("result"), box = $("subjects");
  var GRADES = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "F1", "F2"];
  var DATA = null, loading = null;
  var q = new URLSearchParams(location.search);
  var filt = { area: q.get("area") || "", county: q.get("county") || "", level: "" };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function gradeLabel(g, subj) {
    var p = C.gradePoints(g, subj, { countFoundation: true });
    return g + " – " + p + (g[0] === "F" ? " (some colleges)" : "");
  }
  function addRow(subj, grade) {
    var d = document.createElement("div");
    d.className = "subj-row";
    var s = '<select class="sj" aria-label="Subject"><option value="">Choose subject</option>' + C.SUBJECTS.map(function (x) { return "<option" + (x === subj ? " selected" : "") + ">" + esc(x) + "</option>"; }).join("") + "</select>";
    var g = '<select class="gr" aria-label="Grade"><option value="">Grade</option>' + GRADES.map(function (x) { return '<option value="' + x + '"' + (x === grade ? " selected" : "") + ">" + gradeLabel(x, subj) + "</option>"; }).join("") + "</select>";
    d.innerHTML = s + g + '<button type="button" class="del" aria-label="Remove subject">×</button>';
    box.appendChild(d);
  }
  function refreshLabels(row) {
    var subj = row.querySelector(".sj").value, gs = row.querySelector(".gr");
    [].forEach.call(gs.options, function (o) { if (o.value) o.textContent = gradeLabel(o.value, subj); });
  }
  function state() {
    return { rows: [].map.call(box.querySelectorAll(".subj-row"), function (r) { return [r.querySelector(".sj").value, r.querySelector(".gr").value]; }), lcvp: $("lcvp").value, found: $("found").checked };
  }
  var saved = null; try { saved = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
  if (saved && saved.rows && saved.rows.length) { saved.rows.forEach(function (r) { addRow(r[0], r[1]); }); $("lcvp").value = saved.lcvp || ""; $("found").checked = !!saved.found; }
  else ["English", "Irish", "Mathematics", "", "", "", ""].forEach(function (s) { addRow(s, ""); });

  function loadData() {
    if (DATA) return Promise.resolve(DATA);
    if (!loading) loading = fetch("data/courses.json").then(function (r) { return r.json(); }).then(function (d) { DATA = d; return d; });
    return loading;
  }
  var CH = { safe: "Within reach", likely: "Just made it", close: "Close – worth a try", reach: "A stretch", aqa: "All qualified got in" };

  function finderHtml(total) {
    var m = DATA.meta, res = C.findCourses(total, DATA.courses, filt, 15);
    var opt = function (obj, sel, all) { return '<option value="">' + all + "</option>" + Object.keys(obj).map(function (k) { return '<option value="' + esc(k) + '"' + (k === sel ? " selected" : "") + ">" + esc(obj[k]) + "</option>"; }).join(""); };
    var counties = {}; DATA.courses.forEach(function (c) { counties[c[4]] = c[4]; });
    var ck = {}; Object.keys(counties).sort().forEach(function (k) { ck[k] = k; });
    var h = '<h2>Courses your points could get</h2><p class="small muted">Based on ' + m.year + ' Round 1 points for ' + DATA.courses.length.toLocaleString("en-IE") + ' courses on the 2027 CAO list. Closest cut-offs first.</p>';
    h += '<div class="filters"><select id="fArea" aria-label="Subject area">' + opt(m.areas, filt.area, "All subjects") + '</select><select id="fCounty" aria-label="County">' + opt(ck, filt.county, "Anywhere") +
      '</select><select id="fLevel" aria-label="Level">' + opt({ "8": "Level 8 (honours degree)", "7": "Level 7/6" }, filt.level, "All levels") + "</select></div>";
    function li(r) {
      var c = r.c;
      return '<li><span><a href="' + c[9] + '" data-track="finder_click" data-label="' + c[0] + '">' + esc(c[0] + " " + c[1]) + '</a><small>' + esc(m.colleges[c[2]]) + " · " + esc(c[4]) + " · Level " + c[3] +
        (c[8].indexOf("P") >= 0 ? " · portfolio/interview" : "") + '</small></span><span class="pv">' + esc(r.cut.raw) + '<br><span class="chance ' + r.chance + '">' + CH[r.chance] + "</span></span></li>";
    }
    if (res.within.length) h += '<ul class="course-list">' + res.within.map(li).join("") + "</ul>";
    else h += '<p class="callout">No courses in this filter had ' + m.year + ' points at or below ' + total + '. Try "All subjects" or "Anywhere" – or look at Level 7/6 courses, many of which lead on to a degree.</p>';
    if (res.totalWithin > res.within.length) h += '<p class="small">Showing the ' + res.within.length + " closest of <strong>" + res.totalWithin + "</strong> courses at or below your points. <a href='courses-with-" + Math.min(600, Math.max(200, Math.ceil(total / 50) * 50)) + "-points.html'>See the full list →</a></p>";
    if (res.stretch.length) h += "<h3>Worth putting higher on your list</h3><p class='small muted'>Just above your points last year – points can drop.</p><ul class='course-list'>" + res.stretch.map(li).join("") + "</ul>";
    return h;
  }

  function render(scroll) {
    var st = state(); try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
    var subs = st.rows.filter(function (r) { return r[1]; }).map(function (r) { return { subject: r[0] || "Subject", grade: r[1] }; });
    if (!subs.length) { out.innerHTML = ""; return null; }
    var r = C.calculate(subs, st.lcvp, { countFoundation: st.found });
    try { localStorage.setItem("tavion_cao_pts", r.total); } catch (e) {}
    var h = '<div class="pts-hero"><div class="tl">Your CAO points</div><div class="amt">' + r.total + '</div><p>' + (r.bonus ? "including the " + r.bonus + "-point Higher Maths bonus" : "best " + Math.min(6, r.rows.length) + " of " + r.rows.length + " results") + "</p></div>";
    if (r.rows.length < 6) h += '<p class="callout warn">You\'ve entered ' + r.rows.length + " result" + (r.rows.length === 1 ? "" : "s") + ". Six count – add the rest for your full total.</p>";
    h += '<div class="table-wrap"><table><thead><tr><th>Subject</th><th>Grade</th><th class="num">Points</th></tr></thead><tbody>' + r.counted.map(function (x) {
      return "<tr><td>" + esc(x.subject) + "</td><td>" + x.grade + '</td><td class="num">' + x.points + (x.bonus ? " <small>(incl. +" + x.bonus + ")</small>" : "") + "</td></tr>";
    }).join("") + r.dropped.map(function (x) { return '<tr class="sub"><td>' + esc(x.subject) + " <small>(not counted)</small></td><td>" + x.grade + '</td><td class="num">' + x.points + "</td></tr>"; }).join("") +
      '<tr class="total"><th colspan="2">Total (best six)</th><td class="num">' + r.total + "</td></tr></tbody></table></div>";
    if (r.tips.length) h += '<ul class="issues">' + r.tips.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>";
    h += '<div id="finder"><p class="muted">Loading courses…</p></div>';
    out.innerHTML = h;
    loadData().then(function () { var f = $("finder"); if (f) f.innerHTML = finderHtml(r.total); }).catch(function () { var f = $("finder"); if (f) f.innerHTML = '<p>Couldn\'t load the course list – <a href="all-courses.html">see all courses</a>.</p>'; });
    if (scroll) out.scrollIntoView({ behavior: "smooth", block: "start" });
    return r;
  }
  function band(p) { return p < 200 ? "<200" : p < 300 ? "200-299" : p < 400 ? "300-399" : p < 500 ? "400-499" : p < 600 ? "500-599" : "600+"; }

  box.addEventListener("change", function (e) { var row = e.target.closest(".subj-row"); if (row && e.target.classList.contains("sj")) refreshLabels(row); render(); });
  box.addEventListener("click", function (e) { if (e.target.classList.contains("del")) { e.target.closest(".subj-row").remove(); render(); } });
  $("addSubj").addEventListener("click", function () { if (box.children.length < 10) addRow("", ""); });
  $("lcvp").addEventListener("change", function () { render(); });
  $("found").addEventListener("change", function () { render(); });
  out.addEventListener("change", function (e) {
    var id = e.target.id; if (!/^f(Area|County|Level)$/.test(id)) return;
    filt[{ fArea: "area", fCounty: "county", fLevel: "level" }[id]] = e.target.value;
    var r = C.calculate(state().rows.filter(function (x) { return x[1]; }).map(function (x) { return { subject: x[0], grade: x[1] }; }), $("lcvp").value, { countFoundation: $("found").checked });
    $("finder").innerHTML = finderHtml(r.total);
    if (window.TAVION && TAVION.track) TAVION.track("cao_filter", { label: id + ":" + e.target.value });
  });
  form.addEventListener("submit", function (e) {
    e.preventDefault(); var r = render(true); if (!r) return;
    if (window.TAVION && TAVION.track) TAVION.track("cao_calc", { score: r.total, salary_band: band(r.total), total: r.rows.length });
  });
  render();
})();
