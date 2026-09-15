"""Build the v0.4 site from editable content files plus the frozen v0.4 outputs.

All prose lives in content/*.md and is edited there, never here. This module supplies the data,
draws the things that cannot be written by hand (the heatmap, the tables, the browsers), and
renders the markdown around them. content/README.md documents every token for the writer.

Structure
  index.html        the report, from content/report.md, with a section rail built from its headings
  results.html      all final results, searchable and sortable
  pairs.html        all classified dog and cat drug pairs
  spotcheck.html    the seeded sample anyone can check the review against
  study/<id>.html   one page per study, wrapped by content/study.md
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
CONTENT = J("content")
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

SPECIES_FIX = {"guinea pig": "other-rodent", "cynomolgus monkey": "non-human-primate",
               "Macaca fascicularis": "non-human-primate", "sheep": "sheep-goat"}
UNRESOLVED = {"grouped-label", "human"}

# Recovering species from species_as_reported (amendment A7).
#
# Every result in this review compares an animal with a human, so a reported label such as
# "canine and human" names one animal and the comparator — not two animals. The extractor
# collapsed those to "grouped-label", which put 879 results into a column meaning "species
# unknown" and emptied cells that do hold evidence. Where the reported label names exactly one
# animal from the frozen vocabulary, that is the species; where it names several ("both species",
# "rodents", "animals") or none, it stays unresolved. The rule never invents a species, and the
# stored records are unchanged: this is a display mapping, like the spelling fixes above.
ANIMAL_WORDS = {
    "dog": r"\b(dogs?|canine|canis)\b", "cat": r"\b(cats?|feline)\b",
    "mouse": r"\b(mice|mouse|murine|mus musculus)\b", "rat": r"\b(rats?|rattus)\b",
    "non-human-primate": r"\b(monkeys?|macaques?|primates?|rhesus|cynomolgus|marmoset|baboon)\b",
    "pig-minipig": r"\b(pigs?|swine|porcine|minipigs?)\b",
    "rabbit": r"\b(rabbits?|leporine|oryctolagus)\b",
    "sheep-goat": r"\b(sheep|ovine|goats?|caprine)\b", "zebrafish": r"\b(zebrafish|danio)\b",
    "drosophila": r"\b(drosophila|fruit fly|fruit flies)\b",
    "c-elegans": r"\b(c\.? ?elegans|nematode)\b", "horse": r"\b(horses?|equine)\b",
    "other-rodent": r"\b(guinea pigs?|hamsters?|gerbils?)\b",
}
ANIMAL_WORDS["mouse"] += r"|\bGEMMs?\b"


def _one_animal(text):
    found = {k for k, pat in ANIMAL_WORDS.items() if re.search(pat, text or "", re.I)}
    return found.pop() if len(found) == 1 else None


def recovered_species(r):
    """The species this result is about, or None if it cannot be pinned down.

    Sources in order of authority (amendments A7, A8): the extractor's own species_as_reported
    label first; then, only if that is non-specific, the study title or the result's own statement
    and quote. Where both of those fire they agreed in 74 of 74 checked cases. Any source naming
    more than one animal resolves nothing, so the rule cannot invent a species.
    """
    s = _one_animal(str(r.get("species_as_reported") or ""))
    if s:
        return s
    from_title = _one_animal(r.get("title") or "")
    from_text = _one_animal((r.get("statement") or "") + " " + (r.get("quote") or ""))
    if from_title and from_text:
        return from_title if from_title == from_text else None
    return from_title or from_text
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
        s = recovered_species(r)
        if not s:
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
ol,ul{max-width:68ch}
li{margin:.3em 0}
.lede{font-size:20px;line-height:1.5;color:#3b424a;max-width:60ch;margin:.6em 0 1em}
.lede p{margin:.35em 0;max-width:none}
.lede p:first-child{margin-top:0}
.dek{font-family:var(--sans);font-size:13px;color:var(--faint);text-transform:uppercase;
  letter-spacing:.08em;margin:0 0 6px}
.dek p{margin:0}
a{color:var(--accent)}
.small{font-size:14.5px;color:var(--dim);font-family:var(--sans);line-height:1.5}
.small p{margin:.4em 0;max-width:72ch}
.small p:first-child{margin-top:0}
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
.note p:first-of-type{margin-top:0}
.note .h{font-family:var(--sans);font-size:13px;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;color:var(--accent);margin-bottom:4px}
blockquote{margin:.6em 0;padding:.3em 0 .3em 14px;border-left:2px solid var(--line);color:#3b424a;
  font-size:16px}

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
  color:var(--dim);margin:10px 0 0;flex-wrap:wrap}
.legend .ramp{display:flex}
.legend .ramp i{width:22px;height:11px;display:block}

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
tr.row{cursor:pointer}
tr.row.open{background:var(--accent-soft)}
tr.det>td{background:#fafbfc;padding:0}
.pd{padding:14px 18px;max-width:82ch}
.pd h4{margin:.9em 0 .2em;font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--accent);font-family:var(--sans)}
.pd h4:first-child{margin-top:0}
.pd p{margin:.25em 0;font-family:var(--serif);font-size:15px;line-height:1.5;max-width:76ch}
.pd p.src{font-family:var(--sans);font-size:13px;color:var(--dim)}
.hint{font-family:var(--sans);font-size:13.5px;color:var(--dim);margin:0 0 4px}

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
    var terms = q.split(/\s+/);
    for (var j = 0; j < terms.length; j++) {
      var term = terms[j], hit = false;
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
      : '<tr><td class="empty-state" colspan="' + cfg.cols + '">'
        + (root.dataset.empty || 'Nothing matches those filters.') + '</td></tr>';
    count.textContent = rows.length === data.length
      ? data.length.toLocaleString() + ' ' + cfg.noun
      : rows.length.toLocaleString() + ' of ' + data.length.toLocaleString() + ' ' + cfg.noun;
    var p = new URLSearchParams();
    if (search.value.trim()) p.set('q', search.value.trim());
    selects.forEach(function (sel) { if (sel.value) p.set(sel.dataset.key, sel.value); });
    history.replaceState(null, '', p.toString() ? '?' + p : location.pathname);
  }

  // Rows that carry an evidence panel open on click. The panel is a sibling row emitted by the
  // row renderer, so filtering and sorting move it with its row.
  tbody.addEventListener('click', function (ev) {
    if (ev.target.closest('a')) return;
    var tr = ev.target.closest('tr.row');
    if (!tr) return;
    var det = tr.nextElementSibling;
    if (det && det.classList.contains('det')) {
      det.hidden = !det.hidden;
      tr.classList.toggle('open', !det.hidden);
    }
  });

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
    if rail:
        railhtml = '<div class="rail">' + "".join(
            f'<a href="#{i}">{e(lab)}</a>' for i, lab in rail) + "</div>"
        body = f'<div class="wrap">{railhtml}<div class="doc">{body}</div></div>'
    else:
        body = f'<div class="doc {cls}">{body}</div>'
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
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


def strip_working_notes(src):
    """Remove build provenance and file paths from a pipeline report, and unwrap its hard wrapping.

    The reports are working records: they name the script that wrote them and the files they read.
    That provenance belongs in the repository, not on the page.
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


def report_md(path):
    """A pipeline report, cleaned and rendered."""
    return render(strip_working_notes(open(path).read() if os.path.exists(path) else ""))[0]


SLUG = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
HEAD_META = re.compile(r"\s*\{#([^}|]+)(?:\|([^}]+))?\}\s*$")


def inline(x):
    """Markdown inline: escaping first, then bold, italic, code, links."""
    x = e(x)
    x = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", x)
    x = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", x)
    x = re.sub(r"`(.+?)`", r"<code>\1</code>", x)
    x = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', x)
    return x


def render(src):
    """Render the markdown subset used by the content files and the pipeline reports.

    Returns (html, sections) where sections are the (id, rail label) pairs of the h2 headings, so
    the report's rail follows whatever the writer puts in the file.
    """
    out, sections, rows = [], [], []
    listtag, box = None, None

    def flush_table():
        nonlocal rows
        if not rows:
            return
        head, body = rows[0], [r for r in rows[1:] if not set(r) <= set("-| :")]
        cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
        out.append('<div class="scroll"><table><thead><tr>'
                   + "".join(f"<th>{inline(c)}</th>" for c in cells(head)) + "</tr></thead><tbody>")
        for r in body:
            out.append("<tr>" + "".join(
                f'<td{" class=\"num\"" if i and re.match(r"^[\d.,%–\-() ]+$", c) else ""}>{inline(c)}</td>'
                for i, c in enumerate(cells(r))) + "</tr>")
        out.append("</tbody></table></div>")
        rows = []

    def close_list():
        nonlocal listtag
        if listtag:
            out.append(f"</{listtag}>"); listtag = None

    for line in src.splitlines():
        if line.startswith("|"):
            rows.append(line); continue
        flush_table()
        s = line.strip()

        if s.startswith(":::"):
            close_list()
            rest = s[3:].strip()
            if box and not rest:
                out.append("</div>"); box = None
            elif rest:
                kind, _, title = rest.partition(" ")
                box = kind
                if kind == "note":
                    out.append('<div class="note">'
                               + (f'<div class="h">{inline(title)}</div>' if title.strip() else ""))
                else:
                    out.append(f'<div class="{e(kind)}">')
            continue

        if not s:
            close_list(); continue

        if s.startswith("#"):
            close_list()
            n = len(s) - len(s.lstrip("#"))
            text = s.lstrip("# ")
            hid, label = "", ""
            m = HEAD_META.search(text)
            if m:
                hid, label = m.group(1), (m.group(2) or "")
                text = HEAD_META.sub("", text)
            if n == 2:
                hid = hid or SLUG(text)
                sections.append((hid, label or text))
                out.append(f'<h2 id="{e(hid)}">{inline(text)}</h2>')
            else:
                idattr = f' id="{e(hid)}"' if hid else ""
                out.append(f"<h{min(n,4)}{idattr}>{inline(text)}</h{min(n,4)}>")
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            if listtag != "ol":
                close_list(); out.append("<ol>"); listtag = "ol"
            out.append(f"<li>{inline(m.group(2))}</li>"); continue
        if s.startswith(("- ", "* ")):
            if listtag != "ul":
                close_list(); out.append("<ul>"); listtag = "ul"
            out.append(f"<li>{inline(s[2:])}</li>"); continue

        if listtag:
            # a wrapped continuation line inside a list item
            out[-1] = out[-1][:-5] + " " + inline(s) + "</li>"
            continue
        if out and out[-1].startswith("<p>") and out[-1].endswith("</p>"):
            out[-1] = out[-1][:-4] + " " + inline(s) + "</p>"
        else:
            out.append(f"<p>{inline(s)}</p>")

    flush_table(); close_list()
    if box:
        out.append("</div>")
    return "\n".join(out), sections


def load_artifacts():
    """The wording inside the generated artifacts, from content/artifacts.md.

    Sections are "## name"; within a section each line is "key :: text". Missing keys fall back to
    the caller's default, so an edit that removes a line degrades to the built-in wording rather
    than to a blank.
    """
    art, section = {}, None
    path = os.path.join(CONTENT, "artifacts.md")
    if not os.path.exists(path):
        return art
    for line in open(path):
        s = line.strip()
        if s.startswith("## "):
            section = s[3:].strip(); art[section] = {}
        elif section and "::" in s and not s.startswith("#"):
            k, _, v = s.partition("::")
            art[section][k.strip()] = v.strip()
    return art


ART = {}
def A(section, key, default=""):
    return ART.get(section, {}).get(key, default)


def compose(name, scalars, blocks):
    """Read a content file, fill in its tokens, and render it."""
    src = open(os.path.join(CONTENT, name)).read()
    src = re.sub(r"\{\{(\w+)\}\}", lambda m: str(scalars.get(m.group(1), m.group(0))), src)
    parts, buf = [], []
    for line in src.splitlines():
        key = line.strip()[2:-2] if line.strip().startswith("{{") and line.strip().endswith("}}") else None
        if key and key in blocks:
            parts.append(("md", "\n".join(buf))); buf = []
            parts.append(("html", blocks[key]))
        else:
            buf.append(line)
    parts.append(("md", "\n".join(buf)))
    html_out, sections, title = [], [], ""
    for kind, chunk in parts:
        if kind == "html":
            html_out.append(chunk)
        else:
            h, secs = render(chunk)
            html_out.append(h); sections += secs
            m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
            if m and not title:
                title = re.sub(r"<[^>]+>", "", m.group(1))
    return "\n".join(html_out), sections, title


def dir_label(d):
    return A("directions", d, DIR_LABEL.get(d, d or "—"))


def dirtag(d):
    return f'<span class="tag {DIR_CLASS.get(d, "")}">{e(dir_label(d))}</span>'


def figures_block(pairs):
    return '<div class="figs">' + "".join(
        f'<div><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in pairs) + "</div>"


def ramp(ratio):
    """Single-hue navy ramp, square-root scaled: the median cell holds 2 studies and the largest
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

    h = ['<div class="hmwrap"><table class="hm"><thead><tr><th class="rowh">'
         f'{e(A("heatmap", "row_header", "disease area"))}</th>']
    h += [f"<th>{e(c)}</th>" for c in cols]
    h.append(f'<th class="tot">{e(A("heatmap", "total", "all"))}</th></tr></thead><tbody>')
    for a in areas:
        h.append(f'<tr><th class="rowh">{e(a)}</th>')
        for c in cols:
            g = grid.get((a, c))
            if not g:
                h.append('<td class="empty"></td>'); continue
            n = len(g["s"])
            bg, fg = ramp((n / mx) ** 0.5)
            lv = min(g["lv"])
            ttl = (A("heatmap", "cell_title", "{{area}} · {{species}}: {{n}} studies, highest "
                                              "evidence level {{level}}")
                   .replace("{{area}}", a).replace("{{species}}", c)
                   .replace("{{n}}", str(n)).replace("{{level}}", lv))
            h.append(f'<td><a href="results.html?ar={e(a)}&amp;sp={e(c)}" '
                     f'style="background:{bg};color:{fg}" title="{e(ttl)}">{n}<sup>{lv}</sup></a></td>')
        h.append(f'<td class="tot"><a href="results.html?ar={e(a)}">{rowtot[a]}</a></td></tr>')
    h.append('<tr><th class="rowh">all</th>'
             + "".join(f'<td class="tot"><a href="results.html?sp={e(c)}">{coltot[c]}</a></td>' for c in cols)
             + f'<td class="tot">{len({r["pmid"] for r in fin})}</td></tr>')
    h.append("</tbody></table></div>")
    steps = "".join(f'<i style="background:{ramp(i / 5)[0]}"></i>' for i in range(6))
    high = A("heatmap", "legend_high", "more ({{max}} at most)").replace("{{max}}", str(mx))
    h.append(f'<div class="legend"><span>{e(A("heatmap", "legend_low", "fewer studies"))}</span>'
             f'<span class="ramp">{steps}</span><span>{e(high)}</span>'
             f'<span>· {e(A("heatmap", "legend_note", "superscript = highest evidence level in the "
                            "cell · click a cell to see those results"))}</span></div>')
    return "\n".join(h)


def browser(tid, data_id, rows_json, columns, filters, noun, search_keys, row_js,
            placeholder="", empty="", reset="Reset"):
    """A searchable, sortable table. Rows render client-side from JSON embedded in the page."""
    ph = placeholder or f"Search {noun}…"
    ctl = [f'<div id="{tid}" data-empty="{e(empty or "Nothing matches those filters.")}">'
           '<div class="controls">',
           f'<input type="search" placeholder="{e(ph)}" aria-label="{e(ph)}">']
    for key, label in filters:
        ctl.append(f'<select data-key="{key}" aria-label="{e(label)}"><option value="">{e(label)}: all</option></select>')
    ctl.append(f'<button class="reset" type="button">{e(reset)}</button><span class="count"></span></div>')
    ctl.append('<div class="scroll"><table><thead><tr>')
    for c in columns:
        cls = "s" + (" num" if c.get("num") else "")
        ctl.append(f'<th class="{cls}" data-sort="{c["key"]}">{e(c["label"])}</th>')
    ctl.append("</tr></thead><tbody></tbody></table></div></div>")
    ctl.append(f'<script type="application/json" id="{data_id}">{rows_json}</script>')
    # site.js is deferred, so it has not run while this inline script is parsed. DOMContentLoaded
    # fires after every deferred script has executed.
    ctl.append(f"""<script>document.addEventListener("DOMContentLoaded",function(){{
initTable({{id:"{tid}",dataId:"{data_id}",cols:{len(columns)},
noun:"{noun}",searchKeys:{json.dumps(search_keys)},row:{row_js}}});}});</script>""")
    return "\n".join(ctl)


def main():
    global ART
    ART = load_artifacts()
    fin = [r for r in load("part1/final_results.json") if r["status"] == "final"]
    # Amendment A10: model_type decides the companion/laboratory column, and the extractor left it
    # unfilled on dog and cat results across 20 studies, defaulting them all to laboratory. Each
    # study was read and resolved from its own full text; the evidence is in the overrides file.
    mt_over = {k: v for k, v in load("part1/model_type_overrides.json").items() if not k.startswith("_")}
    for r in fin:
        ov = mt_over.get(r["pmid"])
        if ov and r.get("model_type") == "mixed-or-not-stated":
            r["model_type"] = ov["model_type"]
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

    heads = load("part1/headlines.json")
    adj = load("part1/adjudicated.json")
    manual = {k.rsplit("|", 1)[0] for k in adj if k.endswith("|manual")}
    n_single = sum(1 for r in fin if r["pmid"] in manual)
    n_extracted = sum(len(h.get("items") or []) for h in heads.values())
    # Studies whose full text was read, and the subset judged eligible at that stage. These are two
    # different numbers and the page must not conflate them.
    n_extraction_studies = len(heads)
    n_eligible = sum(1 for h in heads.values() if h.get("eligible"))
    # L84 appears twice in the register (superseded, plus the invalid first run), so count distinct
    # limitation numbers rather than heading lines.
    n_limits = len(set(re.findall(r"^\*\*(L\d+)", open(J("docs", "limitations.md")).read(), re.M)))

    pairs = load("part2/pairs.json")
    attrs = load("part2/pair_attributes.json")
    classified = {k: v for k, v in pairs.items()
                  if (v.get("judgement") or {}).get("pair") in ("concordant", "discordant", "mixed", "indeterminate")}
    # Amendment A9: name and type corrections, each justified in the overrides file from the
    # pair's own veterinary_basis; four pairs are dropped as not drug-and-indication comparisons.
    overrides = {k: v for k, v in load("part2/pair_overrides.json").items() if not k.startswith("_")}
    for key, ov in overrides.items():
        if key not in classified:
            continue
        if ov.get("drop"):
            del classified[key]
        else:
            if ov.get("name"):
                classified[key] = {**classified[key], "ingredient": ov["name"]}
            if ov.get("type"):
                attrs[key] = {**attrs.get(key, {}), "type": ov["type"]}

    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets", "site.css"), "w").write(CSS)
    open(os.path.join(OUT, "assets", "site.js"), "w").write(JS)

    scalars = {"n_results": f"{len(fin):,}", "n_studies": f"{n_stud:,}",
               "n_level_a": f"{by_level['A-outcome-concordance']:,}",
               "n_level_b": f"{by_level['B-toxicity-safety-concordance']:,}",
               "n_level_c": f"{by_level['C-biological-similarity']:,}",
               "n_corresponded": f"{by_dir['animal-corresponded']:,}",
               "n_not_corresponded": f"{by_dir['animal-did-not-correspond']:,}",
               "n_mixed": f"{by_dir['mixed']:,}", "n_unresolved": f"{unresolved:,}",
               "n_pairs": f"{len(classified):,}", "n_single_reviewer": f"{n_single:,}",
               "n_extracted": f"{n_extracted:,}", "n_extraction_studies": f"{n_extraction_studies:,}",
               "n_eligible": f"{n_eligible:,}",
               "n_limitations": f"{n_limits:,}", "built_date": today(),
               # Results sharing one quote are the same finding split across rows (one per gene,
               # per cell type, per tissue). Counting distinct quotes says how many findings there
               # actually are, so the prose need not imply that every row is a separate one.
               "n_distinct_findings": f"{len({(r['pmid'], (r.get('quote') or '')[:120]) for r in fin}):,}"}

    # ---------------- blocks the writer cannot type by hand ----------------
    lt = [f'<div class="scroll"><table><caption>'
          f'{e(A("level_table", "caption", "Results by evidence level, and how they came out."))}'
          f'</caption><thead><tr><th>{e(A("level_table", "level", "Evidence level"))}</th>'
          f'<th class="num">{e(A("level_table", "studies", "studies"))}</th>'
          f'<th class="num">{e(A("level_table", "results", "results"))}</th>'
          f'<th class="num">{e(A("level_table", "corresponded", "corresponded"))}</th>'
          f'<th class="num">{e(A("level_table", "did_not", "did not"))}</th>'
          f'<th class="num">{e(A("level_table", "mixed", "mixed"))}</th></tr></thead><tbody>']
    for key, letter, label in LEVELS:
        rs = [r for r in fin if r["level"] == key]
        c = lvl_dir[key]
        label = A("level_table", f"label_{letter.lower()}", label)
        lt.append(f"<tr><td><strong>{letter}</strong> — {e(label)}</td>"
                  f"<td class='num'>{len({r['pmid'] for r in rs})}</td><td class='num'>{len(rs):,}</td>"
                  f"<td class='num'>{c['animal-corresponded']:,}</td>"
                  f"<td class='num'>{c['animal-did-not-correspond']}</td>"
                  f"<td class='num'>{c['mixed']}</td></tr>")
    lt.append("</tbody></table></div>")

    blocks = {
        "figures": figures_block([
            (f"{len(fin):,}", A("figures", "n_results", "results kept after checking")),
            (f"{n_stud}", A("figures", "n_studies", "studies")),
            (f"{by_level['A-outcome-concordance']}", A("figures", "n_level_a", "level A · intervention outcomes")),
            (f"{by_level['B-toxicity-safety-concordance']}", A("figures", "n_level_b", "level B · toxicity and safety")),
            (f"{by_level['C-biological-similarity']}", A("figures", "n_level_c", "level C · disease biology"))]),
        "level_table": "\n".join(lt),
        "heatmap": heatmap(fin),
        "pairs_strata": report_md(os.path.join(V04, "part2", "summary_v2.md")),
        "q4_tables": report_md(os.path.join(V04, "part2", "q4_report.md")),
        "recall": report_md(os.path.join(V04, "retrieval", "recall.md")),
    }
    body, sections, title = compose("report.md", scalars, blocks)
    page("index.html", "Animal-model concordance: what the literature reports", body, rail=sections)

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
                     "dr": dir_label(r.get("direction")),
                     "dc": DIR_CLASS.get(r.get("direction"), ""), "v": val,
                     "vn": r["value"] if isinstance(r.get("value"), (int, float)) else None})
    row_js = ("""function(r){return '<tr><td><span class="stmt">'+esc(r.st)+'</span></td>'
+'<td>'+r.lv+'</td><td>'+esc(r.sp)+'</td><td>'+esc(r.ar)+'</td>'
+'<td><span class="tag '+r.dc+'">'+r.dr+'</span></td>'
+'<td class="num">'+esc(r.v||'')+'</td>'
+'<td><a href="study/'+encodeURIComponent(r.pm)+'.html">'+esc(r.ti)+'</a><br><span class="src">'+(r.y||'')+'</span></td></tr>';}""")
    cols = [{"key": "st", "label": A("results_table", "col_st", "Finding")},
            {"key": "lv", "label": A("results_table", "col_lv", "Level")},
            {"key": "sp", "label": A("results_table", "col_sp", "Species")},
            {"key": "ar", "label": A("results_table", "col_ar", "Disease area")},
            {"key": "dr", "label": A("results_table", "col_dr", "Direction")},
            {"key": "vn", "label": A("results_table", "col_vn", "Value"), "num": True},
            {"key": "ti", "label": A("results_table", "col_ti", "Study")}]
    body, _, title = compose("results.md", scalars, {
        "results_table": browser("results", "resultdata", json.dumps(rows, separators=(",", ":")), cols,
                                 [("lv", A("results_table", "filter_lv", "Level")),
                                  ("sp", A("results_table", "filter_sp", "Species")),
                                  ("ar", A("results_table", "filter_ar", "Disease area")),
                                  ("dr", A("results_table", "filter_dr", "Direction"))],
                                 A("results_table", "noun", "results"), ["st", "ti", "sp", "ar"], row_js,
                                 placeholder=A("results_table", "placeholder", ""),
                                 empty=A("results_table", "empty", ""),
                                 reset=A("results_table", "reset", "Reset"))})
    page("results.html", title or "Results", body)

    # ---------------- pairs browser ----------------
    prow = []
    vclass = {"concordant": "ok", "discordant": "no", "mixed": "mid"}
    for k, v in classified.items():
        j, a = v["judgement"], attrs.get(k, {})
        sp = v.get("species")
        # Provenance for the verdict: the veterinary studies read, and the human studies and US
        # labels cited. PMIDs link to PubMed; label keys resolve through this pair's own label set
        # to DailyMed. A few citations arrive as "PMID 12345678", so digits are taken where present.
        labels = v.get("labels") or {}
        cites = []
        for c in (j.get("human_citations") or []):
            c = str(c).strip()
            digits = re.sub(r"\D", "", c)
            if re.fullmatch(r"L\d+", c) and c in labels:
                lab = labels[c]
                cites.append({"k": "label", "t": f"{lab.get('brand') or c} ({lab.get('application') or 'US label'})",
                              "u": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={lab.get('set_id')}"})
            elif len(digits) >= 6:
                cites.append({"k": "pmid", "t": digits, "u": f"https://pubmed.ncbi.nlm.nih.gov/{digits}/"})
        vrecs = [{"t": rec.split(":", 1)[1], "u": f"https://pubmed.ncbi.nlm.nih.gov/{rec.split(':', 1)[1]}/"}
                 for rec in (v.get("records") or []) if rec.startswith("PMID:")]
        prow.append({"ag": v.get("ingredient") or "", "sp": ", ".join(sp) if isinstance(sp, list) else str(sp or ""),
                     "ind": v.get("veterinary_indication") or "", "vd": j["pair"],
                     "vc": vclass.get(j["pair"], ""), "vet": j.get("veterinary") or "",
                     "hu": j.get("human") or "", "ty": a.get("type") or "", "ti": a.get("timing") or "",
                     "vb": j.get("veterinary_basis") or "", "hb": j.get("human_basis") or "",
                     "cv": j.get("caveats") or "", "tl": j.get("human_top_level") or "",
                     "vr": vrecs, "hc": cites})
    prow.sort(key=lambda r: (r["ag"].lower(), r["ind"].lower()))
    L = {k: A("pairs_table", k, d) for k, d in (
        ("detail_vet", "What the veterinary evidence showed"),
        ("detail_human", "What the human evidence showed"),
        ("detail_caveats", "Caveats"),
        ("detail_vet_records", "Veterinary studies behind this verdict"),
        ("detail_human_records", "Human evidence cited"),
        ("detail_toplevel", "Strongest human evidence found"),
        ("detail_none", "No human evidence was retrieved for this drug and indication."))}
    prow_js = ("""function(r){
var link=function(x){return '<a href="'+x.u+'">'+esc(x.t)+'</a>';};
var L=""" + json.dumps(L) + """;
var det='<div class="pd"><h4>'+L.detail_vet+'</h4><p>'+esc(r.vb)+'</p>'
+(r.vr.length?'<p class="src">'+L.detail_vet_records+': '+r.vr.map(link).join(', ')+'</p>':'')
+'<h4>'+L.detail_human+'</h4><p>'+esc(r.hb)+'</p>'
+(r.hc.length?'<p class="src">'+L.detail_human_records+': '+r.hc.map(link).join(', ')+'</p>'
  :'<p class="src">'+L.detail_none+'</p>')
+(r.tl?'<p class="src">'+L.detail_toplevel+': '+esc(r.tl)+'</p>':'')
+(r.cv?'<h4>'+L.detail_caveats+'</h4><p>'+esc(r.cv)+'</p>':'')+'</div>';
return '<tr class="row"><td><strong>'+esc(r.ag)+'</strong></td><td>'+esc(r.sp)+'</td>'
+'<td>'+esc(r.ind)+'</td><td><span class="tag '+r.vc+'">'+r.vd+'</span></td>'
+'<td>'+esc(r.vet)+'</td><td>'+esc(r.hu)+'</td><td>'+esc(r.ty)+'</td><td>'+esc(r.ti)+'</td></tr>'
+'<tr class="det" hidden><td colspan="8">'+det+'</td></tr>';}""")
    pcols = [{"key": "ag", "label": A("pairs_table", "col_ag", "Drug")},
             {"key": "sp", "label": A("pairs_table", "col_sp", "Species")},
             {"key": "ind", "label": A("pairs_table", "col_ind", "Veterinary indication")},
             {"key": "vd", "label": A("pairs_table", "col_vd", "Verdict")},
             {"key": "vet", "label": A("pairs_table", "col_vet", "Veterinary")},
             {"key": "hu", "label": A("pairs_table", "col_hu", "Human")},
             {"key": "ty", "label": A("pairs_table", "col_ty", "Type")},
             {"key": "ti", "label": A("pairs_table", "col_ti", "Timing")}]
    hint = A("pairs_table", "hint", "")
    body, _, title = compose("pairs.md", scalars, {
        "pairs_table": (f'<p class="hint">{e(hint)}</p>' if hint else "") +
                       browser("pairs", "pairdata", json.dumps(prow, separators=(",", ":")), pcols,
                               [("vd", A("pairs_table", "filter_vd", "Verdict")),
                                ("sp", A("pairs_table", "filter_sp", "Species")),
                                ("ty", A("pairs_table", "filter_ty", "Type")),
                                ("ti", A("pairs_table", "filter_ti", "Timing"))],
                               A("pairs_table", "noun", "pairs"), ["ag", "ind", "vet", "hu", "vb", "hb"],
                               prow_js, placeholder=A("pairs_table", "placeholder", ""),
                               empty=A("pairs_table", "empty", ""), reset=A("pairs_table", "reset", "Reset"))})
    page("pairs.html", title or "Dog and cat drug pairs", body)

    # ---------------- study pages ----------------
    for pm, rs in studies.items():
        r0 = rs[0]
        header = (f'<p class="dek">Study</p><h1>{e(r0.get("title") or pm)}</h1>'
                  f'<p class="small">{e(r0.get("year"))} · {e(r0.get("design"))} · peer reviewed: '
                  f'{e(r0.get("peer_reviewed"))} · record {e(pm)} · '
                  f'<a href="https://pubmed.ncbi.nlm.nih.gov/{e(pm)}/">PubMed</a></p>')
        rblocks = []
        for r in rs:
            meta = [dirtag(r["direction"]), f'level {e((r["level"] or "?")[:1])}',
                    e(sp_display(r)), e(area_display(r))]
            if r.get("value") is not None:
                unit = "" if r.get("unit") in (None, "none") else f" {e(r['unit'])}"
                meta.append(f"<strong>{e(r.get('value'))}{unit}</strong>")
            if r.get("denominator"):
                meta.append(f"n {e(r.get('numerator'))}/{e(r.get('denominator'))}")
            rblocks.append(f"<h3>{t(r['statement'])}</h3>"
                           f'<p class="small">' + " · ".join(meta) + "</p>"
                           f"<blockquote>“{e(r.get('quote'))}”<br><span class='small'>page "
                           f"{e(r.get('pdf_page'))}</span></blockquote>")
        body, _, _ = compose("study.md", {**scalars, "n_results": str(len(rs)),
                                          "result_word": "result" if len(rs) == 1 else "results"},
                             {"study_header": header, "study_results": "\n".join(rblocks)})
        page(f"study/{pm}.html", (r0.get("title") or pm)[:80], body, depth=1)

    # ---------------- spot-check ----------------
    items = load("part1/spotcheck.json", [])
    sb = []
    for s, label in (("A", "Sample A — random across all kept results"),
                     ("B", "Sample B — single-reviewer studies")):
        rows_s = [x for x in items if x["sample"] == s]
        sb.append(f'<h2 id="sample{s}">{e(label)} ({len(rows_s)})</h2>')
        for it in rows_s:
            ln = " · ".join(f'<a href="{e(u)}">{e(lbl)}</a>' for lbl, u in it["links"])
            val = ""
            if it["value"] is not None:
                unit = "" if it.get("unit") in (None, "none") else f" {e(it['unit'])}"
                val = f" · <strong>{e(it['value'])}{unit}</strong>"
                if it["denominator"]:
                    val += f" (n {e(it['numerator'])}/{e(it['denominator'])})"
            sb.append(f"<h3>{e(s)}{it['n']}. {e((it['title'] or it['pmid'])[:110])}</h3>"
                      f'<p class="small">{e(it["year"])} · {e(it["journal"] or "—")} · {ln} · '
                      f'<a href="study/{e(it["pmid"])}.html">study page</a> · <strong>page '
                      f'{e(it["pdf_page"])}</strong> · adjudication: '
                      f'{"single reviewer" if it["adjudicator"] == "hand" else "model"}</p>'
                      f"<p>{t(it['statement'])}</p>"
                      f'<p class="small">species {e(it["species"])} · level {e(it["level"])} · '
                      f'{dirtag(it["direction"])}{val}</p>'
                      f"<blockquote>“{e(it['quote'])}”</blockquote>")
    body, _, title = compose("spotcheck.md", scalars, {"spotcheck_items": "\n".join(sb)})
    page("spotcheck.html", title or "Spot-check this review", body)

    # ---------------- api ----------------
    os.makedirs(os.path.join(OUT, "api"), exist_ok=True)
    json.dump(fin, open(os.path.join(OUT, "api", "results.json"), "w"), indent=1)
    json.dump(load("part1/evidence_map.json"), open(os.path.join(OUT, "api", "evidence_map.json"), "w"), indent=1)
    json.dump({"built": today(), "results": len(fin), "studies": n_stud,
               "by_level": dict(by_level), "by_direction": dict(by_dir),
               "pairs_classified": len(classified)},
              open(os.path.join(OUT, "api", "summary.json"), "w"), indent=1)
    print(f"built {OUT}: {len(fin)} results, {n_stud} study pages, {len(classified)} pairs")
    print(f"tokens: extracted={n_extracted} extraction_studies={n_extraction_studies} "
          f"eligible={n_eligible} single_reviewer={n_single} limitations={n_limits} "
          f"unresolved={unresolved}")


if __name__ == "__main__":
    main()
