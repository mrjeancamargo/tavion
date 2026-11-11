# CAO data (tools/data/cao.json)

Built by `parse/parse_cao.py` from files downloaded from cao.ie into a work folder (raw files are not kept in the repo):

| File in work folder | Where it comes from |
|---|---|
| `c27/XX.html` (one per college) | POST to https://www.cao.ie/courses.php?bb=courses with `flag=hei&college=XX&url=XX` – the 2027 course list, incl. each official course page link |
| `l8.html`, `l76.html` | https://www2.cao.ie/points/l8.php and l76.php – latest Round 1 / Round 2 points |
| `CAOPointsCharts2025.xlsx` (2024, 2023) | https://www2.cao.ie/points/CAOPointsCharts2025.xlsx – full-season points, mid-points, ISCED category |

Yearly refresh (after Round 1 in late August, and when the new course list opens in November):
1. Download the files above (the new year's xlsx once CAO publishes it), update the year lists in `parse_cao.py`.
2. `python parse/parse_cao.py <path>/cao.json` from the work folder, then `python tools/build_cao.py`.
3. Update `PY` and `CHECKED` in `tools/build_cao.py`, and the dates on the dates-2027 page.
