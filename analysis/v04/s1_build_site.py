"""Build the v0.4 site: one long-form report, plus searchable browsers over the underlying records.

Structure
  index.html        the report, read top to bottom, with a section rail: summary, evidence map,
                    what the results say, drug pairs, companion vs laboratory, methods,
                    limitations, verify
  results.html      all final results, searchable and sortable, filterable by level, species,
                    disease area and direction
  pairs.html        all classified dog and cat drug pairs, same machinery
  spotcheck.html    the seeded sample anyone can check the review against
  study/<id>.html   one page per study: its kept results, each with quote and page
  assets/           one stylesheet and one script, shared by every page
  api/*.json        the same content as data

Two rules hold throughout. Statistics are never recomputed here: the strata, Q4 and recall numbers
are the ones computed by d3/d4/d5/r3 and are embedded from their reports verbatim, with build
provenance stripped. Quotes are reproduced byte-exact, so an asterisk inside a quotation is the
paper's own significance marker and stays.

Species and disease-area labels are normalised for display only (the records keep what the
extractor recorded): stray species spellings fold onto the frozen vocabulary, off-vocabulary
disease areas fold into one "other" row, and results whose species could not be resolved to one
animal are shown in their own labelled column rather than dropped.
"""
import sys, os, re, json, html, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import load, species_column, today, J, V04

OUT = J("site", "v04_build")
e = lambda s: html.escape(str(s if s is not None else ""))
# Paper-derived text (statements) is not markdown; strip stray emphasis characters so they do not
# surface as asterisks. Quotes are never passed through this: they are reproduced exactly.
t = lambda s: e(re.sub(r"\*+", "", str(s if s is not None else "")))

LEVELS = [("A-outcome-concordance", "A", "intervention outcomes"),
          ("B-toxicity-safety-concordance", "B", "toxicity and safety"),
          ("C-biological-similarity", "C", "disease biology")]
DIR_LABEL = {"animal-corresponded": "corresponded", "animal-did-not-correspond": "did not correspond",
             "mixed": "mixed", "not-applicable": "not applicable"}
DIR_CLASS = {"animal-corresponded": "ok", "animal-did-not-correspond": "no", "mixed": "mid"}

# Display-only normalisation. The frozen vocabulary is in common.py; these are spellings that
# reached the final set without folding onto it.
SPECIES_FIX = {"guinea pig": "other-rodent", "cynomolgus monkey": "non-human-primate",
               "Macaca fascicularis": "non-human-primate", "sheep": "sheep-goat"}
UNRESOLVED = {"grouped-label", "human"}
SPECIES_ORDER = ["mouse", "rat", "other-rodent", "rabbit", "pig-minipig", "sheep-goat",
                 "non-human-primate", "laboratory-dog", "companion-dog", "laboratory-cat",
                 "companion-cat", "horse", "zebrafish", "drosophila", "c-elegans", "other-species",
                 "not resolved"]
AREA_ORDER = ["oncology", "neurology", "immunology-inflammation", "cross-cutting-toxicology",
              "cardiovascular", "liver-gi", "infectious-disease", "pain-musculoskeletal",
              "psychiatry-addiction", "metabolic-endocrine", "ophthalmology", "respiratory",
              "reproductive-developmental", "haematology", "renal", "dermatology", "other"]


def sp_display(r):
    """Species column for display: frozen vocabulary, with unresolved labels kept visible."""
    s = r.get("species")
    if s in UNRESOLVED:
        return "not resolved"
    return species_column(SPECIES_FIX.get(s, s), r.get("model_type"))


def area_display(r):
    a = r.get("disease_area") or "other"
    return a if a in AREA_ORDER else "other"


CSS = """
:root{
  --ink:#15181c; --dim:#5c636c; --faint:#878e97; --line:#e3e6ea; --bg:#fbfaf8; --card:#fff;
  --accent:#1d4e79; --accent-soft:#eef3f8; --ok:#2c6a4e; --no:#8f3a2c; --mid:#866416;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 var(--serif);
  -webkit-font-smoothing:antialiased}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
header.top .in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;flex-wrap:wrap;
  gap:8px 22px;align-items:baseline}
header.top .brand{font-weight:600;color:var(--ink);text-decoration:none;font-size:16px;letter-spacing:-.01em}
header.top nav{font-family:var(--sans);font-size:14px;display:flex;gap:18px;flex-wrap:wrap}
header.top nav a{color:var(--dim);text-decoration:none}
header.top nav a:hover,header.top nav a.on{color:var(--accent)}
header.top nav a.on{font-weight:600}
main{max-width:1180px;margin:0 auto;padding:0 22px 80px}
.wrap{display:grid;grid-template-columns:200px minmax(0,1fr);gap:46px;align-items:start}
.rail{position:sticky;top:64px;font-family:var(--sans);font-size:13.5px;padding-top:34px}
.rail a{display:block;color:var(--dim);text-decoration:none;padding:4px 0 4px 10px;
  border-left:2px solid var(--line);line-height:1.35}
.rail a:hover{color:var(--accent)}
.rail a.on{color:var(--accent);border-left-color:var(--accent);font-weight:600}
.doc{padding-top:34px;min-width:0}
h1{font-size:34px;line-height:1.18;margin:.1em 0 .3em;letter-spacing:-.015em;font-weight:600;
  text-wrap:balance;max-width:20ch}
.page h1{max-width:28ch}
h2{font-size:23px;margin:2.4em 0 .5em;font-weight:600;letter-spacing:-.01em;scroll-margin-top:72px}
h3{font-size:18px;margin:1.8em 0 .4em;font-weight:600}
h4{font-size:15px;margin:1.4em 0 .3em;font-weight:600;font-family:var(--sans)}
p,li{max-width:68ch}
p{margin:.75em 0}
.lede{font-size:20px;line-height:1.5;color:#3b424a;max-width:60ch}
.dek{font-family:var(--sans);font-size:13px;color:var(--faint);text-transform:uppercase;
  letter-spacing:.08em;margin:0 0 6px}
a{color:var(--accent)}
.small{font-size:14.5px;color:var(--dim);font-family:var(--sans);line-height:1.5}
code{font-family:var(--mono);font-size:13px;background:#f1f3f5;padding:1px 5px;border-radius:3px}
hr{border:0;border-top:1px solid var(--line);margin:2.6em 0}

.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin:22px 0}
.figs div{background:var(--card);padding:14px 16px}
.figs .n{font-size:27px;font-weight:600;font-family:var(--sans);font-variant-numeric:tabular-nums;
  letter-spacing:-.02em}
.figs .l{font-family:var(--sans);font-size:13px;color:var(--dim);line-height:1.35;margin-top:2px}

table{border-collapse:collapse;width:100%;margin:16px 0;background:var(--card);
  font-family:var(--sans);font-size:14px}
.scroll{overflow-x:auto;margin:16px 0;border:1px solid var(--line);background:var(--card)}
.scroll table{margin:0;border:0}
th,td{border-bottom:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
thead th{background:#f7f8f9;font-weight:600;color:#3b424a;white-space:nowrap;
  border-bottom:1px solid var(--line)}
tbody tr:hover{background:#fafbfc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
caption{caption-side:top;text-align:left;font-family:var(--sans);font-size:13px;color:var(--dim);
  padding:0 0 8px}

.tag{display:inline-block;padding:1px 8px;border-radius:2px;font-size:12.5px;font-family:var(--sans);
  border:1px solid var(--line);white-space:nowrap;color:var(--dim)}
.tag.ok{color:var(--ok);border-color:#c3dbcd;background:#f4f9f6}
.tag.no{color:var(--no);border-color:#e3c4bd;background:#fdf6f4}
.tag.mid{color:var(--mid);border-color:#e4d7a9;background:#fcf9ef}

.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  padding:14px 18px;margin:22px 0;max-width:72ch}
.note p{margin:.4em 0}
.note .h{font-family:var(--sans);font-size:13px;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;color:var(--accent);margin-bottom:4px}
blockquote{margin:.6em 0;padding:.3em 0 .3em 14px;border-left:2px solid var(--line);color:#3b424a;
  font-size:16px}

/* heatmap */
.hmwrap{overflow-x:auto;margin:18px 0;border:1px solid var(--line);background:var(--card)}
table.hm{font-size:13px;margin:0;border:0}
table.hm th{font-weight:500;font-size:12.5px;color:var(--dim);background:var(--card);
  border-bottom:1px solid var(--line)}
table.hm thead th{white-space:nowrap;text-align:center;padding:9px 6px;vertical-align:bottom}
table.hm th.rowh{text-align:left;white-space:nowrap;position:sticky;left:0;background:var(--card);
  border-right:1px solid var(--line);color:var(--ink);font-weight:500;z-index:1}
table.hm td{padding:0;border:0;border-bottom:1px solid #f0f2f4;text-align:center}
table.hm td a{display:block;padding:7px 4px;text-decoration:none;font-variant-numeric:tabular-nums;
  font-family:var(--sans);min-width:38px}
table.hm td a sup{font-size:9px;opacity:.75;margin-left:1px}
table.hm td.empty{background:repeating-linear-gradient(45deg,#fcfcfc,#fcfcfc 4px,#f6f7f8 4px,#f6f7f8 8px)}
table.hm td.tot a,table.hm td.tot{background:#f7f8f9;color:var(--dim);font-weight:600}
.legend{display:flex;align-items:center;gap:8px;font-family:var(--sans);font-size:12.5px;
  color:var(--dim);margin:10px 0 0}
.legend .ramp{display:flex}
.legend .ramp i{width:22px;height:11px;display:block}

/* data browser */
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 10px;
  font-family:var(--sans);font-size:14px}
.controls input[type=search]{flex:1 1 260px;min-width:200px;padding:8px 11px;border:1px solid var(--line);
  border-radius:3px;font:inherit;background:var(--card);color:var(--ink)}
.controls select{padding:7px 9px;border:1px solid var(--line);border-radius:3px;font:inherit;
  background:var(--card);color:var(--ink)}
.controls input[type=search]:focus,.controls select:focus{outline:2px solid var(--accent);outline-offset:1px}
.count{font-family:var(--sans);font-size:13.5px;color:var(--dim);margin-left:auto}
.reset{font-family:var(--sans);font-size:13.5px;background:none;border:0;color:var(--accent);
  cursor:pointer;padding:6px 2px}
th.s{cursor:pointer;user-select:none}
th.s:hover{color:var(--accent)}
th.s::after{content:"";display:inline-block;width:0;height:0;margin-left:5px;vertical-align:middle;
  border-left:4px solid transparent;border-right:4px solid transparent;border-top:4px solid #c2c8cf}
th.s.asc::after{border-top:0;border-bottom:4px solid var(--accent)}
th.s.desc::after{border-top:4px solid var(--accent)}
td .stmt{font-family:var(--serif);font-size:15px;line-height:1.45;display:block;max-width:60ch}
td .src{color:var(--dim);font-size:12.5px}
.empty-state{padding:26px;text-align:center;color:var(--dim);font-family:var(--sans);font-size:14px}

footer{border-top:1px solid var(--line);margin-top:60px;padding:22px;color:var(--faint);
  font-family:var(--sans);font-size:13px}
footer .in{max-width:1180px;margin:0 auto}
@media (max-width:900px){
  .wrap{grid-template-columns:1fr;gap:0}
  .rail{position:static;padding:22px 0 0;display:flex;flex-wrap:wrap;gap:4px 14px;
    border-bottom:1px solid var(--line);padding-bottom:12px}
  .rail a{border-left:0;padding:2px 0}
  .rail a.on{border-left:0}
  body{font-size:16px}
  h1{font-size:28px}
  .lede{font-size:18px}
}
"""

JS = r"""
// Section rail: highlight the section currently in view.
(function () {
  var links = [].slice.call(document.querySelectorAll('.rail a[href^="#"]'));
  if (!links.length) return;
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function mark() {
    var best = 0, top = 90;
    targets.forEach(function (el, i) {
      if (el && el.getBoundingClientRect().top <= top) best = i;
    });
    links.forEach(function (a, i) { a.classList.toggle('on', i === best); });
  }
  window.addEventListener('scroll', mark, { passive: true });
  mark();
})();

// Rows are built as HTML strings, so every value taken from a paper is escaped here. The JSON
// keeps the original text: a finding reading "p < 0.05" must still be findable by searching for it.
window.esc = function (s) {
  return String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
};

// Data browser: search, sort, filter over a table's rows. Rows are embedded in the page as JSON
// so the page works offline and from a local file, with no request and no library.
window.initTable = function (cfg) {
  var data = JSON.parse(document.getElementById(cfg.dataId).textContent);
  var root = document.getElementById(cfg.id);
  var search = root.querySelector('input[type=search]');
  var selects = [].slice.call(root.querySelectorAll('select'));
  var tbody = root.querySelector('tbody');
  var count = root.querySelector('.count');
  var reset = root.querySelector('.reset');
  var heads = [].slice.call(root.querySelectorAll('th.s'));
  var sort = { key: null, dir: 1 };

  selects.forEach(function (sel) {
    var key = sel.dataset.key;
    var vals = {};
    data.forEach(function (r) { if (r[key]) vals[r[key]] = (vals[r[key]] || 0) + 1; });
    Object.keys(vals).sort().forEach(function (v) {
      var o = document.createElement('option');
      o.value = v; o.textContent = v + ' (' + vals[v] + ')';
      sel.appendChild(o);
    });
  });

  var params = new URLSearchParams(location.search);
  if (params.get('q')) search.value = params.get('q');
  selects.forEach(function (sel) {
    var v = params.get(sel.dataset.key);
    if (v) sel.value = v;
  });

  function matches(r) {
    for (var i = 0; i < selects.length; i++) {
      var sel = selects[i];
      if (sel.value && r[sel.dataset.key] !== sel.value) return false;
    }
    var q = search.value.trim().toLowerCase();
    if (!q) return true;
    for (var j = 0; j < q.split(/\s+/).length; j++) {
      var term = q.split(/\s+/)[j], hit = false;
      for (var k = 0; k < cfg.searchKeys.length; k++) {
        var v = r[cfg.searchKeys[k]];
        if (v && String(v).toLowerCase().indexOf(term) >= 0) { hit = true; break; }
      }
      if (!hit) return false;
    }
    return true;
  }

  function render() {
    var rows = data.filter(matches);
    if (sort.key) {
      rows = rows.slice().sort(function (a, b) {
        var x = a[sort.key], y = b[sort.key];
        if (x === null || x === undefined || x === '') return 1;
        if (y === null || y === undefined || y === '') return -1;
        if (typeof x === 'number' && typeof y === 'number') return (x - y) * sort.dir;
        return String(x).localeCompare(String(y)) * sort.dir;
      });
    }
    tbody.innerHTML = rows.length
      ? rows.map(cfg.row).join('')
      : '<tr><td class="empty-state" colspan="' + cfg.cols + '">Nothing matches those filters.</td></tr>';
    count.textContent = rows.length === data.length
      ? data.length.toLocaleString() + ' ' + cfg.noun
      : rows.length.toLocaleString() + ' of ' + data.length.toLocaleString() + ' ' + cfg.noun;
    var p = new URLSearchParams();
    if (search.value.trim()) p.set('q', search.value.trim());
    selects.forEach(function (sel) { if (sel.value) p.set(sel.dataset.key, sel.value); });
    history.replaceState(null, '', p.toString() ? '?' + p : location.pathname);
  }

  var timer;
  search.addEventListener('input', function () {
    clearTimeout(timer); timer = setTimeout(render, 120);
  });
  selects.forEach(function (sel) { sel.addEventListener('change', render); });
  reset.addEventListener('click', function () {
    search.value = ''; selects.forEach(function (s) { s.value = ''; });
    sort = { key: null, dir: 1 };
    heads.forEach(function (h) { h.classList.remove('asc', 'desc'); });
    render();
  });
  heads.forEach(function (th) {
    th.addEventListener('click', function () {
      var key = th.dataset.sort;
      sort = { key: key, dir: sort.key === key ? -sort.dir : 1 };
      heads.forEach(function (h) { h.classList.remove('asc', 'desc'); });
      th.classList.add(sort.dir === 1 ? 'asc' : 'desc');
      render();
    });
  });
  render();
};
"""

NAV = [("index.html", "Report"), ("results.html", "Results"), ("pairs.html", "Drug pairs"),
       ("spotcheck.html", "Verify")]


def page(fname, title, body, depth=0, rail=None, cls="page"):
    up = "../" * depth
    here = fname if depth == 0 else ""
    nav = "".join(f'<a href="{up}{h}"{" class=\"on\"" if h == here else ""}>{lab}</a>' for h, lab in NAV)
    railhtml = ""
    if rail:
        railhtml = '<div class="rail">' + "".join(
            f'<a href="#{i}">{lab}</a>' for i, lab in rail) + "</div>"
        body = f'<div class="wrap">{railhtml}<div class="doc">{body}</div></div>'
    else:
        body = f'<div class="doc {cls}">{body}</div>'
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<link rel="stylesheet" href="{up}assets/site.css">
</head><body>
<header class="top"><div class="in"><a class="brand" href="{up}index.html">Animal-model concordance</a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer><div class="in">A systematic review of studies comparing findings in live non-human animals
with the corresponding findings in humans. Protocol frozen before data collection; every figure
reproducible from the public data and code. Built {today()}.</div></footer>
<script src="{up}assets/site.js" defer></script></body></html>"""
    p = os.path.join(OUT, fname)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(doc)


PATH_RE = re.compile(r"\s*\(?`[^`]*(?:/|\.(?:py|json|md))[^`]*`\)?|\s*\b[\w-]+\.(?:py|json|md)\b|\s*\b(?:analysis|data|site|docs)/[\w./-]+")
PROVENANCE_RE = re.compile(r"^\s*(?:Built|Generated|Computed|Cost)\b", re.I)


def prose(src):
    """Strip build provenance and file paths, and unwrap hard-wrapped paragraphs.

    The pipeline reports are working records: they name the script that wrote them and the files
    they read. That provenance belongs in the repository, not on the page, so it is removed here
    rather than from the reports themselves.
    """
    def clean(s):
        s = PATH_RE.sub("", s)
        s = s.replace("**F1 statement:**", "**In plain terms:**").replace(" (draft)", "")
        s = re.sub(r"[;,]\s*\)", ")", s)
        s = re.sub(r"\(\s*[;,]?\s*\)", "", s)
        return re.sub(r" {2,}", " ", s).replace(" .", ".").rstrip()
    out, para = [], []
    def flush():
        if para:
            out.append(" ".join(para)); para.clear()
    for ln in src.splitlines():
        if (PROVENANCE_RE.match(ln) or "{'" in ln or ln.startswith("**Not yet produced")
                or ln.startswith("# ") or ln.startswith("Confusion (")):
            continue
        s = clean(ln.rstrip())
        if not s.strip() or s.lstrip().startswith(("#", "|", "- ", "* ")):
            flush(); out.append(s)
        else:
            para.append(s.strip())
    flush()
    return "\n".join(out)


def md(path):
    return mdsrc(open(path).read() if os.path.exists(path) else "")


def mdsrc(src):
    """Render the subset of markdown used by the pipeline reports."""
    src = prose(src)
    out, rows, inlist = [], [], False
    def flush_table():
        nonlocal rows
        if not rows:
            return
        head, body = rows[0], [r for r in rows[1:] if not set(r) <= set("-| :")]
        cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
        out.append('<div class="scroll"><table><thead><tr>'
                   + "".join(f"<th>{inline(c)}</th>" for c in cells(head)) + "</tr></thead><tbody>")
        for r in body:
            cs = cells(r)
            out.append("<tr>" + "".join(
                f'<td{" class=\"num\"" if i and re.match(r"^[\d.,%–\-() ]+$", c) else ""}>{inline(c)}</td>'
                for i, c in enumerate(cs)) + "</tr>")
        out.append("</tbody></table></div>")
        rows = []
    def inline(x):
        x = e(x)
        x = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", x)
        x = re.sub(r"`(.+?)`", r"<code>\1</code>", x)
        return x
    for line in src.splitlines():
        if line.startswith("|"):
            rows.append(line); continue
        flush_table()
        s = line.strip()
        if not s:
            if inlist: out.append("</ul>"); inlist = False
            continue
        if s.startswith("#"):
            if inlist: out.append("</ul>"); inlist = False
            n = len(s) - len(s.lstrip("#"))
            out.append(f"<h{min(n+2,4)}>{inline(s.lstrip('# '))}</h{min(n+2,4)}>")
        elif s.startswith(("- ", "* ")):
            if not inlist: out.append("<ul>"); inlist = True
            out.append(f"<li>{inline(s[2:])}</li>")
        else:
            if inlist: out.append("</ul>"); inlist = False
            out.append(f"<p>{inline(s)}</p>")
    flush_table()
    if inlist: out.append("</ul>")
    return "\n".join(out)


def dirtag(d):
    return f'<span class="tag {DIR_CLASS.get(d, "")}">{e(DIR_LABEL.get(d, d or "—"))}</span>'


def figures(pairs):
    return '<div class="figs">' + "".join(
        f'<div><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in pairs) + "</div>"


def ramp(ratio):
    """Single-hue navy ramp. Square-root scaled: the median cell holds 2 studies and the largest
    holds 67, so a linear ramp would render one dark square and a hundred white ones."""
    a, b = (238, 243, 248), (29, 78, 121)
    c = [round(a[i] + (b[i] - a[i]) * ratio) for i in range(3)]
    return f"rgb({c[0]},{c[1]},{c[2]})", ("#fff" if ratio > 0.55 else "#15181c")


def heatmap(fin):
    grid = collections.defaultdict(lambda: {"s": set(), "lv": set()})
    for r in fin:
        g = grid[(area_display(r), sp_display(r))]
        g["s"].add(r["pmid"]); g["lv"].add((r["level"] or "?")[:1])
    areas = [a for a in AREA_ORDER if any(k[0] == a for k in grid)]
    cols = [c for c in SPECIES_ORDER if any(k[1] == c for k in grid)]
    mx = max(len(g["s"]) for g in grid.values())
    rowtot = {a: len({p for (aa, _), g in grid.items() if aa == a for p in g["s"]}) for a in areas}
    coltot = {c: len({p for (_, cc), g in grid.items() if cc == c for p in g["s"]}) for c in cols}

    h = ['<div class="hmwrap"><table class="hm"><thead><tr><th class="rowh">disease area</th>']
    h += [f'<th>{e(c)}</th>' for c in cols]
    h.append('<th class="tot">all</th></tr></thead><tbody>')
    for a in areas:
        h.append(f'<tr><th class="rowh">{e(a)}</th>')
        for c in cols:
            g = grid.get((a, c))
            if not g:
                h.append('<td class="empty"></td>'); continue
            n = len(g["s"])
            bg, fg = ramp((n / mx) ** 0.5)
            lv = min(g["lv"])
            # Filter keys must match the browser's select keys, not the display names.
            href = f"results.html?ar={a}&sp={c}"
            ttl = f"{a} · {c}: {n} studies, highest evidence level {lv}"
            h.append(f'<td><a href="{e(href)}" style="background:{bg};color:{fg}" '
                     f'title="{e(ttl)}">{n}<sup>{lv}</sup></a></td>')
        h.append(f'<td class="tot"><a href="results.html?ar={e(a)}">{rowtot[a]}</a></td></tr>')
    h.append('<tr><th class="rowh">all</th>'
             + "".join(f'<td class="tot"><a href="results.html?sp={e(c)}">{coltot[c]}</a></td>' for c in cols)
             + f'<td class="tot">{len({r["pmid"] for r in fin})}</td></tr>')
    h.append("</tbody></table></div>")
    steps = "".join(f'<i style="background:{ramp(i / 5) [0]}"></i>' for i in range(6))
    h.append(f'<div class="legend"><span>fewer studies</span><span class="ramp">{steps}</span>'
             f'<span>more ({mx} at most)</span><span>· superscript = highest evidence level in the cell '
             f'· click a cell to see those results</span></div>')
    return "\n".join(h)


def browser(tid, data_id, rows_json, columns, filters, noun, search_keys, row_js):
    """A searchable, sortable table. Rows render client-side from JSON embedded in the page."""
    ctl = [f'<div id="{tid}"><div class="controls">',
           f'<input type="search" placeholder="Search {noun}…" aria-label="Search {noun}">']
    for key, label in filters:
        ctl.append(f'<select data-key="{key}" aria-label="{label}"><option value="">{label}: all</option></select>')
    ctl.append('<button class="reset" type="button">Reset</button><span class="count"></span></div>')
    ctl.append('<div class="scroll"><table><thead><tr>')
    for c in columns:
        cls = "s" + (" num" if c.get("num") else "")
        ctl.append(f'<th class="{cls}" data-sort="{c["key"]}">{e(c["label"])}</th>')
    ctl.append("</tr></thead><tbody></tbody></table></div></div>")
    ctl.append(f'<script type="application/json" id="{data_id}">{rows_json}</script>')
    # site.js is deferred, so it has not run while this inline script is parsed. Wait for the
    # document to finish: DOMContentLoaded fires after every deferred script has executed.
    ctl.append(f"""<script>document.addEventListener("DOMContentLoaded",function(){{
initTable({{id:"{tid}",dataId:"{data_id}",cols:{len(columns)},
noun:"{noun}",searchKeys:{json.dumps(search_keys)},row:{row_js}}});}});</script>""")
    return "\n".join(ctl)


def main():
    fin = [r for r in load("part1/final_results.json") if r["status"] == "final"]
    studies = collections.defaultdict(list)
    for r in fin:
        studies[r["pmid"]].append(r)
    n_stud = len(studies)
    by_level = collections.Counter(r["level"] for r in fin)
    by_dir = collections.Counter(r["direction"] for r in fin)
    lvl_dir = collections.defaultdict(collections.Counter)
    for r in fin:
        lvl_dir[r["level"]][r["direction"]] += 1
    unresolved = sum(1 for r in fin if sp_display(r) == "not resolved")

    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets", "site.css"), "w").write(CSS)
    open(os.path.join(OUT, "assets", "site.js"), "w").write(JS)

    # ---------------- the report ----------------
    rail = [("summary", "Summary"), ("map", "Evidence map"), ("results", "What the results say"),
            ("pairs", "Drug pairs"), ("q4", "Companion vs laboratory"), ("methods", "Methods"),
            ("limits", "Limitations"), ("verify", "Verify this work")]
    b = ['<p class="dek">Systematic review</p>',
         "<h1>What the published literature reports about animal-to-human concordance</h1>",
         '<p class="lede">We read every study we could find that compares a finding in live '
         'non-human animals with the corresponding finding in humans, and recorded what it found — '
         'one result at a time, each with the sentence and page it came from.</p>',
         figures([(f"{len(fin):,}", "results kept after checking"), (f"{n_stud}", "studies"),
                  (f"{by_level['A-outcome-concordance']}", "level A · intervention outcomes"),
                  (f"{by_level['B-toxicity-safety-concordance']}", "level B · toxicity and safety"),
                  (f"{by_level['C-biological-similarity']}", "level C · disease biology")]),
         '<h2 id="summary">Summary</h2>',
         "<p>Across every result we kept, the animal finding matched the human finding "
         f"<strong>{by_dir['animal-corresponded']:,}</strong> times, failed to match "
         f"<strong>{by_dir['animal-did-not-correspond']}</strong> times, and was mixed "
         f"<strong>{by_dir['mixed']}</strong> times.</p>",
         '<div class="note"><div class="h">Why there is no headline percentage</div>'
         "<p>Those counts are not a concordance rate and we do not report one. The studies do not "
         "measure the same thing: they report concordance rates, sensitivities, correlation "
         "coefficients, gene-overlap counts and qualitative similarity claims, across different "
         "diseases and species. Pooling them would produce a number with no referent.</p>"
         "<p>The literature is also selective about what gets published and about which comparisons "
         "get made at all, so the balance above reflects what authors chose to report. Values are "
         "grouped only where metric and unit match, and spreads are shown rather than averages.</p></div>",
         '<div class="scroll"><table><caption>Results by evidence level, and how they came out.</caption>'
         "<thead><tr><th>Evidence level</th><th class='num'>studies</th><th class='num'>results</th>"
         "<th class='num'>corresponded</th><th class='num'>did not</th><th class='num'>mixed</th>"
         "</tr></thead><tbody>"]
    for key, letter, label in LEVELS:
        rs = [r for r in fin if r["level"] == key]
        c = lvl_dir[key]
        b.append(f"<tr><td><strong>{letter}</strong> — {label}</td>"
                 f"<td class='num'>{len({r['pmid'] for r in rs})}</td><td class='num'>{len(rs):,}</td>"
                 f"<td class='num'>{c['animal-corresponded']:,}</td>"
                 f"<td class='num'>{c['animal-did-not-correspond']}</td>"
                 f"<td class='num'>{c['mixed']}</td></tr>")
    b.append("</tbody></table></div>")
    b += ["<p>Most of the evidence is level C: how similar the biology looks, rather than what "
          "happened when a disease was treated. That distribution is itself a finding about the "
          "field — the comparison that matters most for drug development is the one made least "
          "often.</p>",

          '<h2 id="map">Evidence map</h2>',
          "<p>Where the evidence actually is. Each cell counts the distinct studies with a kept "
          "result for that disease area and species; the superscript is the highest evidence level "
          "present. Companion dogs and cats — client-owned animals with naturally occurring "
          "disease — are kept separate from laboratory dogs and cats throughout.</p>",
          heatmap(fin),
          f'<p class="small">{unresolved:,} of {len(fin):,} results sit in the '
          "<em>not resolved</em> column: the paper reported several species together, or the "
          "species label is wrong. That column means the species could not be pinned down, not "
          "that something was found. The grid is sparse by nature — most disease-area and species "
          "combinations have never been studied this way.</p>",

          '<h2 id="results">What the results say</h2>',
          "<p>Every kept result is browsable: filter by evidence level, species, disease area or "
          "direction, or search the findings themselves. Each row links to its study page, which "
          "carries the quote and the page number the value came from.</p>",
          f'<p><a href="results.html"><strong>Browse all {len(fin):,} results →</strong></a></p>',

          '<h2 id="pairs">Dog and cat drug pairs</h2>',
          "<p>For agents used both in companion animals with naturally occurring disease and in "
          "people: does the veterinary evidence point the same way as the human evidence? "
          "Concordance is concordant / (concordant + discordant); mixed and indeterminate pairs are "
          "counted in the table and never dropped.</p>",
          md(os.path.join(V04, "part2", "summary_v2.md")),
          '<div class="note"><div class="h">How to read this</div>'
          "<p>Most of these are human medicines later adopted in veterinary practice. The agreement "
          "therefore mostly shows that veterinary medicine adopts drugs that already work — not "
          "that animal evidence predicted the human result. “Discordant” is used only where all the "
          "available evidence points the opposite way.</p></div>",
          '<p><a href="pairs.html"><strong>Browse all classified pairs →</strong></a></p>',

          '<h2 id="q4">Companion animals vs laboratory models</h2>',
          "<p>For the same agent and condition, did the companion-animal evidence and the "
          "laboratory-model evidence each match what happened in people?</p>",
          md(os.path.join(V04, "part2", "q4_report.md")),
          '<div class="note"><div class="h">What this cannot tell you</div>'
          "<p>104 of the 108 pairs have a positive human result, and the laboratory literature is "
          "almost uniformly positive (205 of 214 determinate laboratory sides). A body of evidence "
          "that nearly always reads “it works” will agree with a mostly positive human record "
          "automatically.</p>"
          "<p>Only 4 pairs have a negative human result — the case where predictive value would "
          "actually show — and there laboratory models matched 0 of 4 and companion animals 1 of 4. "
          "This compares <em>agreement</em>, as the protocol asked. It says nothing about "
          "prediction.</p></div>",
          '<p class="small">The laboratory side of each pair is read from abstracts by a language '
          "model. Audited against a stronger judge on a random sample, 79% of those reads were "
          "fully correct (42 of 53), with errors dominated by including studies that should have "
          "been excluded.</p>",

          '<h2 id="methods">Methods</h2>',
          "<h3>Eligibility</h3>",
          "<p>A study is eligible if it reports a finding in live non-human animals alongside the "
          "corresponding finding in humans, so that the two can be compared. Results are classified "
          "by what is being compared: <strong>A</strong>, what happened when a disease was treated; "
          "<strong>B</strong>, toxicity and safety; <strong>C</strong>, disease biology without an "
          "intervention outcome. Animal-only results, animal-to-animal comparisons, in-vitro work, "
          "and figures a paper quotes from another paper are not eligible, whatever they report.</p>",
          "<h3>From search to result</h3>",
          "<ol><li><strong>Retrieval.</strong> Citation chasing from known reviews plus themed "
          "PubMed queries, run as two independent mechanisms so that coverage can be estimated.</li>"
          "<li><strong>Screening</strong> in two stages, the second calibrated against hand-checked "
          "anchor papers.</li>"
          "<li><strong>Extraction</strong> from open-access full text. Every result is recorded with "
          "the sentence it came from and the page that sentence is on; both are published with "
          "it.</li>"
          "<li><strong>Verification.</strong> A second model checks each extracted result against "
          "the located page.</li>"
          "<li><strong>Adjudication.</strong> Every result is then decided against the eligibility "
          "rule above — including the results verification rejected, so that the checking step "
          "cannot quietly remove evidence.</li></ol>",
          "<p>Extraction, screening and verification are performed by language models under fixed "
          "prompts; adjudication decides what appears here. Nothing on this site is summarised by a "
          "model: the counts, rates and intervals are computed from the adjudicated records.</p>",
          "<h3>Coverage of the literature</h3>",
          md(os.path.join(V04, "retrieval", "recall.md")),
          "<h3>How accurate is the checking?</h3>",
          "<p>3,562 candidate results were extracted from 570 screened studies, of which "
          f"{len(fin):,} results in {n_stud} studies survived adjudication. The two checking stages "
          "disagree often enough to be worth reporting: of the results verification accepted, "
          "<strong>34% were later dropped or corrected</strong>; of those it rejected, "
          "<strong>10% were reinstated</strong>. That is why every result is adjudicated rather than "
          "trusted to verification alone.</p>",
          "<p>Roughly half the final results (769 of 1,494) were adjudicated by a single reviewer "
          'who was not blinded to the provisional labels. Those are the results the '
          '<a href="spotcheck.html">spot-check</a> deliberately oversamples.</p>',

          '<h2 id="limits">Limitations</h2>',
          "<p>The ones that bear on how these results should be read:</p>",
          "<ul>"
          "<li><strong>This is a large sample of the field, not a census.</strong> Capture–recapture "
          "across the two search mechanisms estimates 33% coverage of the reachable eligible "
          "literature (95% CI 26–46%), and because the mechanisms are not fully independent that is "
          "an upper bound.</li>"
          "<li><strong>Open-access full text only.</strong> Paywalled studies are absent, and the "
          "veterinary side of the drug-pair analysis is largely read from abstracts.</li>"
          "<li><strong>The results are not commensurable.</strong> Concordance rates, sensitivities, "
          "correlations and gene-overlap counts are different quantities; they are grouped only "
          "where metric and unit match, and never pooled.</li>"
          "<li><strong>The literature is selective.</strong> Preclinical publishing favours positive "
          "findings, and which comparisons get made at all is not random. This inflates apparent "
          "agreement — most visibly in the companion-versus-laboratory comparison.</li>"
          "<li><strong>Agreement is not prediction.</strong> Most drug pairs are human medicines "
          "later adopted in veterinary practice, so the two sides are not independent tests of each "
          "other.</li>"
          "<li><strong>Part of the adjudication was single-reviewer and unblinded</strong>, and the "
          "two adjudicators covered different studies, so agreement between them cannot be "
          "measured.</li>"
          f"<li><strong>Species labels are imperfect.</strong> {unresolved:,} of {len(fin):,} "
          "results could not be resolved to one species, and a handful carry a label that is simply "
          "wrong. In the evidence map, treat that column as unassigned rather than as a "
          "finding.</li>"
          "<li><strong>Regulatory status is read from US sources</strong>, and the review is "
          "unregistered — PROSPERO does not accept preclinical or meta-research reviews.</li>"
          "</ul>",
          '<p class="small">A dated register of all 88 limitations recorded during the work, '
          "including those superseded by later corrections, is kept in the "
          '<a href="https://github.com/rohitium/animal-model-concordance">project repository</a> '
          "along with the protocol, the data and the code that built this site.</p>",

          '<h2 id="verify">Verify this work</h2>',
          "<p>Because part of the adjudication was single-reviewer and unblinded, the review "
          "publishes a fixed, seeded sample of its own results — each with its source, its page and "
          "the sentence it came from — so that anyone can check it rather than take it on trust. "
          "Forty items, about five minutes each.</p>",
          '<p><a href="spotcheck.html"><strong>Open the spot-check →</strong></a></p>']
    page("index.html", "Animal-model concordance: what the literature reports", "\n".join(b), rail=rail)

    # ---------------- results browser ----------------
    rows = []
    for r in fin:
        val = ""
        if r.get("value") is not None:
            unit = "" if r.get("unit") in (None, "none") else f" {r['unit']}"
            val = f"{r['value']:g}{unit}" if isinstance(r["value"], (int, float)) else f"{r['value']}{unit}"
        rows.append({"st": (r["statement"] or "").replace("*", ""), "ti": (r.get("title") or "")[:140],
                     "pm": r["pmid"], "y": r.get("year") or 0, "lv": (r["level"] or "?")[:1],
                     "sp": sp_display(r), "ar": area_display(r),
                     "dr": DIR_LABEL.get(r.get("direction"), "—"),
                     "dc": DIR_CLASS.get(r.get("direction"), ""), "v": val,
                     "vn": r["value"] if isinstance(r.get("value"), (int, float)) else None})
    row_js = ("""function(r){return '<tr><td><span class="stmt">'+esc(r.st)+'</span></td>'
+'<td>'+r.lv+'</td><td>'+esc(r.sp)+'</td><td>'+esc(r.ar)+'</td>'
+'<td><span class="tag '+r.dc+'">'+r.dr+'</span></td>'
+'<td class="num">'+esc(r.v||'')+'</td>'
+'<td><a href="study/'+encodeURIComponent(r.pm)+'.html">'+esc(r.ti)+'</a><br><span class="src">'+(r.y||'')+'</span></td></tr>';}""")
    cols = [{"key": "st", "label": "Finding"}, {"key": "lv", "label": "Level"},
            {"key": "sp", "label": "Species"}, {"key": "ar", "label": "Disease area"},
            {"key": "dr", "label": "Direction"}, {"key": "vn", "label": "Value", "num": True},
            {"key": "ti", "label": "Study"}]
    b = ["<h1>Every result we kept</h1>",
         f'<p class="lede">{len(fin):,} results from {n_stud} studies. Search the findings, sort any '
         "column, or filter down to a species, a disease area or an evidence level. Each row links "
         "to the study page, which carries the quote and the page it came from.</p>",
         browser("results", "resultdata", json.dumps(rows, separators=(",", ":")), cols,
                 [("lv", "Level"), ("sp", "Species"), ("ar", "Disease area"), ("dr", "Direction")],
                 "results", ["st", "ti", "sp", "ar"], row_js),
         '<p class="small">Level A: what happened when a disease was treated. B: toxicity and '
         "safety. C: disease biology, without an intervention outcome. “Not resolved” species means "
         "the paper reported several species together, or the label is wrong — not a finding.</p>"]
    page("results.html", "Results", "\n".join(b))

    # ---------------- pairs browser ----------------
    pairs = load("part2/pairs.json")
    attrs = load("part2/pair_attributes.json")
    classified = {k: v for k, v in pairs.items()
                  if (v.get("judgement") or {}).get("pair") in ("concordant", "discordant", "mixed", "indeterminate")}
    prow = []
    vclass = {"concordant": "ok", "discordant": "no", "mixed": "mid"}
    for k, v in classified.items():
        j, a = v["judgement"], attrs.get(k, {})
        sp = v.get("species")
        prow.append({"ag": v.get("ingredient") or "", "sp": ", ".join(sp) if isinstance(sp, list) else str(sp or ""),
                     "ind": v.get("veterinary_indication") or "", "vd": j["pair"],
                     "vc": vclass.get(j["pair"], ""), "vet": j.get("veterinary") or "",
                     "hu": j.get("human") or "", "ty": a.get("type") or "", "ti": a.get("timing") or ""})
    prow.sort(key=lambda r: ({"concordant": 0, "discordant": 1, "mixed": 2, "indeterminate": 3}[r["vd"]], r["ag"]))
    prow_js = ("""function(r){return '<tr><td><strong>'+esc(r.ag)+'</strong></td><td>'+esc(r.sp)+'</td>'
+'<td>'+esc(r.ind)+'</td><td><span class="tag '+r.vc+'">'+r.vd+'</span></td>'
+'<td>'+esc(r.vet)+'</td><td>'+esc(r.hu)+'</td><td>'+esc(r.ty)+'</td><td>'+esc(r.ti)+'</td></tr>';}""")
    pcols = [{"key": "ag", "label": "Agent"}, {"key": "sp", "label": "Species"},
             {"key": "ind", "label": "Veterinary indication"}, {"key": "vd", "label": "Verdict"},
             {"key": "vet", "label": "Veterinary"}, {"key": "hu", "label": "Human"},
             {"key": "ty", "label": "Type"}, {"key": "ti", "label": "Timing"}]
    b = ["<h1>Dog and cat drug pairs</h1>",
         f'<p class="lede">{len(classified)} agent-and-indication pairs used both in companion '
         "animals with naturally occurring disease and in people, classified by whether the "
         "veterinary and human evidence point the same way.</p>",
         browser("pairs", "pairdata", json.dumps(prow, separators=(",", ":")), pcols,
                 [("vd", "Verdict"), ("sp", "Species"), ("ty", "Type"), ("ti", "Timing")],
                 "pairs", ["ag", "ind", "vet", "hu"], prow_js),
         '<p class="small">“Discordant” is used only where all the available evidence points the '
         "opposite way; “indeterminate” means the evidence on one side was not strong enough to "
         "call, and those pairs are kept in view rather than dropped. Timing says whether the drug "
         "was approved in humans before or after the veterinary evidence — most were approved "
         'first. The strata and confidence intervals are on the <a href="index.html#pairs">report '
         "page</a>.</p>"]
    page("pairs.html", "Dog and cat drug pairs", "\n".join(b))

    # ---------------- study pages ----------------
    for pm, rs in studies.items():
        r0 = rs[0]
        sb = [f'<p class="dek">Study</p><h1>{e(r0.get("title") or pm)}</h1>',
              f'<p class="small">{e(r0.get("year"))} · {e(r0.get("design"))} · peer reviewed: '
              f'{e(r0.get("peer_reviewed"))} · record {e(pm)} · '
              f'<a href="https://pubmed.ncbi.nlm.nih.gov/{e(pm)}/">PubMed</a> · '
              f'<a href="../results.html?q={e((r0.get("title") or "")[:40])}">in the results table</a></p>',
              f"<p>{len(rs)} kept result{'s' if len(rs) != 1 else ''}. Each was extracted from the "
              "full text, checked against the located page, and adjudicated against the review's "
              "definition of an animal-versus-human comparison.</p>"]
        for r in rs:
            meta = [dirtag(r["direction"]), f'level {e((r["level"] or "?")[:1])}',
                    e(sp_display(r)), e(area_display(r))]
            if r.get("value") is not None:
                unit = "" if r.get("unit") in (None, "none") else f" {e(r['unit'])}"
                meta.append(f"<strong>{e(r.get('value'))}{unit}</strong>")
            if r.get("denominator"):
                meta.append(f"n {e(r.get('numerator'))}/{e(r.get('denominator'))}")
            sb += [f"<h3>{t(r['statement'])}</h3>",
                   f'<p class="small">' + " · ".join(meta) + "</p>",
                   f"<blockquote>“{e(r.get('quote'))}”<br><span class='small'>page "
                   f"{e(r.get('pdf_page'))}</span></blockquote>"]
        sb.append('<p class="small">Full texts are copyrighted and are not republished here. The '
                  "quote is the evidence for the extracted value, and the page number lets you "
                  "check it in the original.</p>")
        page(f"study/{pm}.html", (r0.get("title") or pm)[:80], "\n".join(sb), depth=1)

    # ---------------- spot-check ----------------
    items = load("part1/spotcheck.json", [])
    b = ["<h1>Spot-check this review</h1>",
         '<p class="lede">Roughly half the results here were adjudicated by a single reviewer who '
         "was not blinded to the pipeline's provisional labels. Rather than ask you to take that on "
         "trust, this page publishes a fixed sample of results — with the source, the page and the "
         "sentence for each — so anyone can verify them independently.</p>",
         "<h2>What to check</h2>",
         "<p>Open the paper, find the quoted sentence, then ask four questions <strong>in "
         "order</strong> and stop at the first failure:</p>",
         "<ol><li>Is the quote really in this paper, and is it this paper's own result rather than a "
         "figure it quotes from someone else?</li>"
         "<li>Does the statement say what the quote says — no more, no less?</li>"
         "<li>Do the value, unit and denominator match the quote, and is the rate the right way "
         "round?</li>"
         "<li>Is this genuinely an animal-versus-human comparison, with the right species and the "
         "right evidence level?</li></ol>",
         "<p><strong>Not failures:</strong> paraphrase that preserves the meaning, rounding, or a "
         "page number one off from where you find the sentence. <strong>Failures worth reporting "
         "loudly:</strong> questions 1 and 4 — those mean the result should never have been kept, "
         "and they tend to come in classes rather than singly.</p>",
         '<p class="small">Two samples, drawn by fixed seeds so they can be redrawn and audited. '
         "Sample A is random across all kept results; sample B is drawn only from the "
         "single-reviewer studies, and is the one to do first. Reporting which question failed is "
         "more useful than prose: it says whether to re-extract, re-adjudicate a category, or "
         "correct one row.</p>"]
    for s, label in (("A", "Sample A — random across all kept results"),
                     ("B", "Sample B — single-reviewer studies")):
        rows_s = [x for x in items if x["sample"] == s]
        b.append(f'<h2 id="sample{s}">{e(label)} ({len(rows_s)})</h2>')
        for it in rows_s:
            ln = " · ".join(f'<a href="{e(u)}">{e(lbl)}</a>' for lbl, u in it["links"])
            val = ""
            if it["value"] is not None:
                unit = "" if it.get("unit") in (None, "none") else f" {e(it['unit'])}"
                val = f" · <strong>{e(it['value'])}{unit}</strong>"
                if it["denominator"]:
                    val += f" (n {e(it['numerator'])}/{e(it['denominator'])})"
            b += [f"<h3>{e(s)}{it['n']}. {e((it['title'] or it['pmid'])[:110])}</h3>",
                  f'<p class="small">{e(it["year"])} · {e(it["journal"] or "—")} · {ln} · '
                  f'<a href="study/{e(it["pmid"])}.html">study page</a> · <strong>page '
                  f'{e(it["pdf_page"])}</strong> · adjudication: '
                  f'{"single reviewer" if it["adjudicator"] == "hand" else "model"}</p>',
                  f"<p>{t(it['statement'])}</p>",
                  f'<p class="small">species {e(it["species"])} · level {e(it["level"])} · '
                  f'{dirtag(it["direction"])}{val}</p>',
                  f"<blockquote>“{e(it['quote'])}”</blockquote>"]
    b.append('<p class="small">Found something wrong? The item number, the question that failed and '
             "one line of what you saw is enough to act on — that is what the check is for.</p>")
    page("spotcheck.html", "Spot-check this review", "\n".join(b))

    # ---------------- api ----------------
    os.makedirs(os.path.join(OUT, "api"), exist_ok=True)
    json.dump(fin, open(os.path.join(OUT, "api", "results.json"), "w"), indent=1)
    json.dump(load("part1/evidence_map.json"), open(os.path.join(OUT, "api", "evidence_map.json"), "w"), indent=1)
    json.dump({"built": today(), "results": len(fin), "studies": n_stud,
               "by_level": dict(by_level), "by_direction": dict(by_dir),
               "pairs_classified": len(classified)},
              open(os.path.join(OUT, "api", "summary.json"), "w"), indent=1)
    print(f"built {OUT}: {len(fin)} results, {n_stud} study pages, {len(classified)} pairs")


if __name__ == "__main__":
    main()
