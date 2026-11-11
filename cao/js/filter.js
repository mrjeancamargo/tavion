// Filters the all-courses table as you type.
(function () {
  var box = document.getElementById("filter"), rows = [].slice.call(document.querySelectorAll("table.all tbody tr")), t;
  if (!box) return;
  box.addEventListener("input", function () {
    clearTimeout(t);
    t = setTimeout(function () {
      var q = box.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      rows.forEach(function (r) { var s = r.textContent.toLowerCase(); r.hidden = !q.every(function (w) { return s.indexOf(w) >= 0; }); });
    }, 120);
  });
})();
