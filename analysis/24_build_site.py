"""Build the site. Data first: every page is an aggregate of per-study measurements.

Supersedes 15_build_site.py. Changes made on user direction:
 - no provisional banner, no generator credit line
 - arm/species/area tables are two columns
 - full-text vs abstract provenance is demoted to the provenance block; it is a
   detail of how we work, not a property of the evidence
 - study pages lead with what the study did and found, then its actual numbers and
   direct quotes
 - only eligible studies appear; excluded ones live on their own page with reasons
"""
import sys, os, json, html, collections, datetime, re
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "site", "_build")
J = lambda *p: os.path.join(ROOT, *p)
load = lambda *p: json.load(open(J(*p))) if os.path.exists(J(*p)) else {}

DB   = load("data","db","studies.json")
META = load("data","db","metadata.json")
MS   = load("data","db","measurements.json")
CLS  = load("data","db","classification.json")
FTS  = load("data","raw","fulltext_status.json")
XS   = load("data","db","crossspecies.json")
SCOPE= load("data","db","measurement_scope.json")
# Measurements whose value does not appear in the sentence it is attributed to.
# The figure may still be somewhere in the paper, but we cannot show it as sourced,
# so the number is withheld and only the statement is shown.
_AUD = load("data","db","measurement_audit.json") or []
UNSUP = {(a["pmid"], a["index"]) for a in _AUD} if isinstance(_AUD, list) else set()
for d in (os.path.join(OUT,"api","study"), os.path.join(OUT,"study")):
    os.makedirs(d, exist_ok=True)
e = lambda s: html.escape(str(s if s is not None else ""))
BUILT = datetime.date.today().isoformat()

ELIG = {pm: v for pm, v in DB.items() if v.get("eligible")}
# Patient-derived xenografts test the PATIENT'S OWN human tumour tissue in a mouse
# host. The question they answer -- does this patient's tumour, grown in a mouse,
# predict this patient's response -- is not the question this review asks, which is
# whether ANOTHER SPECIES' biology predicts human outcomes. They report very high
# agreement on small samples, so pooling them with animal-model concordance would
# inflate it. Kept, reported separately, never mixed into the aggregates.
PDX  = {pm: v for pm, v in ELIG.items() if v.get("substrate") == "human-tissue-in-animal-host"}
CORE = {pm: v for pm, v in ELIG.items() if pm not in PDX}
EXCL = {pm: v for pm, v in DB.items() if v.get("eligible") is False}
def cls(pm, k, d=None):
    c = CLS.get(pm) or {}
    return c.get(k, d) if "error" not in c else d
def meas(pm, ah_only=False):
    """ah_only: keep just the animal-vs-human figures. A study reports many numbers;
    most compare animals with animals, humans with humans, or describe the conduct of
    the research. Only the animal-vs-human ones belong on aggregate pages."""
    m = MS.get(pm) or {}
    if "error" in m: return []
    mm = m.get("measurements") or []
    sc = SCOPE.get(pm) or {}
    if "error" in sc: sc = {}
    for i, x in enumerate(mm):
        x["_scope"] = sc.get(str(i), sc.get(i, "unscoped"))
        x["_unsupported"] = (pm, i) in UNSUP
    return ([x for x in mm if x["_scope"] == "animal-vs-human" and not x["_unsupported"]]
            if ah_only else mm)

def sortkey(x):
    if x.get("_unsupported"): return (3, 0)
    """Rank only within comparable units. A count of 4,418 genes is not 'bigger' than
    94%, so counts and unitless values sort after the proportional ones."""
    v, u = x.get("value"), x.get("unit")
    if v is None: return (2, 0)
    if u in ("percent",):     return (0, -v)
    if u in ("proportion",):  return (0, -(v*100 if v <= 1 else v))
    if u in ("correlation",): return (1, -abs(v))
    return (2, -v)

def fmt(x):
    v, u = x.get("value"), x.get("unit")
    if x.get("_unsupported"): return "not stated"
    if v is None: return "—"
    if u == "percent":    return f"{v:g}%"
    if u == "proportion": return f"{v:g}" if v > 1 else f"{v*100:g}%"
    if u == "fold":       return f"{v:g}-fold"
    if u == "correlation":return f"r/R² {v:g}"
    if u == "ratio":      return f"{v:g}×"
    if u == "count":      return f"{v:g}"
    return f"{v:g}"

CSS = """
:root{--bg:#fff;--fg:#161616;--mut:#666;--line:#e5e5e5;--accent:#8a2f2f;--card:#fafafa;--chip:#f0f0f0}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0f0f0f;--fg:#eaeaea;--mut:#9b9b9b;--line:#2a2a2a;--accent:#e59090;--card:#181818;--chip:#222}}
:root[data-theme=dark]{--bg:#0f0f0f;--fg:#eaeaea;--mut:#9b9b9b;--line:#2a2a2a;--accent:#e59090;--card:#181818;--chip:#222}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);margin:0;font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:1.4rem 1.25rem 4rem}
h1{font-size:1.8rem;line-height:1.25;margin:0 0 .4rem;letter-spacing:-.021em}
h2{font-size:1.16rem;margin:2.1rem 0 .7rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
h3{font-size:.97rem;margin:1.5rem 0 .4rem}
a{color:var(--accent)}
.sub{color:var(--mut);margin:0 0 1.2rem;font-size:.93rem}
nav{display:flex;gap:1.05rem;flex-wrap:wrap;padding:.65rem 0;border-bottom:1px solid var(--line);margin-bottom:1.3rem;font-size:.87rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:.7rem;margin:1rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.8rem}
.stat .n{font-size:1.45rem;font-weight:600;letter-spacing:-.02em}
.stat .l{color:var(--mut);font-size:.73rem;text-transform:uppercase;letter-spacing:.045em;margin-top:.15rem}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{text-align:left;padding:.46rem .55rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:.74rem;text-transform:uppercase;letter-spacing:.045em}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}
.tag{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:3px;padding:.05rem .38rem;font-size:.75rem;color:var(--mut);margin:0 .18rem .18rem 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.85rem 1rem;margin:.6rem 0}
.quote{border-left:3px solid var(--accent);padding:.5rem .85rem;margin:.55rem 0;font-size:.9rem;background:var(--card)}
.quote .t{display:block;color:var(--mut);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.2rem}
.verb{color:var(--mut);font-size:.8rem;font-style:italic}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.8rem}
code{background:var(--chip);padding:.08rem .28rem;border-radius:3px;font-size:.85em}
ul{padding-left:1.1rem}li{margin:.15rem 0}
.bar{height:6px;background:var(--chip);border-radius:3px;overflow:hidden;min-width:60px}
.bar>i{display:block;height:100%;background:var(--accent)}
"""
NAV=[("index.html","Overview"),("findings.html","Findings"),("studies.html","Studies"),
     ("species.html","Species"),("areas.html","Areas"),("arms.html","Arms"),
     ("methods.html","Methods"),("excluded.html","Excluded")]
def page(title, body, depth=0):
    up="../"*depth
    nav="".join(f'<a href="{up}{h}">{e(t)}</a>' for h,t in NAV)
    return (f'<meta charset="utf-8"><title>{e(title)}</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>'
            f'<div class="wrap"><nav>{nav}</nav>{body}'
            f'<footer>Animal Model Concordance &middot; {len(ELIG)} studies &middot; updated {BUILT}<br>'
            f'Every figure links to the study that reported it. Not peer reviewed.</footer></div>')

# cross-species measurements only: the point of the review
def xsp(pm):
    v = XS.get(pm) or {}
    return v.get("has_animal_human_comparison") is True
ALLM   = [(pm, x) for pm in CORE for x in meas(pm)]
ALLM_AH= [(pm, x) for pm in CORE for x in meas(pm, ah_only=True)]
PDXM_AH= [(pm, x) for pm in PDX  for x in meas(pm, ah_only=True)]

def facet_counts(key, pool=None):
    c = collections.Counter()
    for pm in (pool if pool is not None else CORE):
        val = cls(pm, key)
        for x in (val if isinstance(val, list) else [val]):
            if x: c[x] += 1
    return c

def two_col(title, col, counts, href, anchor=True):
    mx = max(counts.values()) if counts else 1
    out = [f"<h2>{e(title)}</h2>", '<div class="scroll"><table>',
           f"<tr><th>{e(col)}</th><th>Studies</th><th></th></tr>"]
    for k, n in counts.most_common():
        link = f'<a href="{href}#{e(k)}">{e(k)}</a>' if anchor else e(k)
        out.append(f'<tr><td>{link}</td><td class="num">{n}</td>'
                   f'<td><div class="bar"><i style="width:{n/mx*100:.0f}%"></i></div></td></tr>')
    out.append("</table></div>")
    return "".join(out)

# ---------------- overview ----------------
yrs=[v["year"] for v in ELIG.values() if v.get("year")]
nxs=sum(1 for pm in ELIG if xsp(pm))
b=["<h1>Animal Model Concordance with Human Clinical Outcomes</h1>",
   '<p class="sub">What the published literature reports when it measures how well results in '
   'animals correspond to results in humans. Every number below is one a study reported; '
   'nothing is pooled or averaged across studies.</p>',
   '<div class="grid">',
   f'<div class="stat"><div class="n">{len(CORE)}</div><div class="l">studies</div></div>',
   f'<div class="stat"><div class="n">{len(ALLM_AH)}</div><div class="l">animal–human figures</div></div>',
   f'<div class="stat"><div class="n">{sum(1 for pm in CORE if meas(pm, ah_only=True))}</div>'
   f'<div class="l">studies reporting one</div></div>',
   f'<div class="stat"><div class="n">{len(facet_counts("species"))}</div><div class="l">species</div></div>',
   f'<div class="stat"><div class="n">{min(yrs)}–{max(yrs)}</div><div class="l">years</div></div>',
   '</div>',
   two_col("Studies by arm", "Arm", facet_counts("arm"), "arms.html"),
   two_col("Species represented", "Species", facet_counts("species"), "species.html"),
   two_col("Therapeutic areas", "Area", facet_counts("therapeutic_areas"), "areas.html")]
open(os.path.join(OUT,"index.html"),"w").write(page("Animal Model Concordance","".join(b)))

# ---------------- findings ----------------
FAM=[("Agreement and concordance",["concordance","agreement","match","mimic","similar","overlap","correlat"]),
     ("Predictive accuracy",["sensitivit","specificit","ppv","npv","predictive value","recall","precision","accuracy","auc","receiver"]),
     ("Translation and success rates",["translat","success","approval","attrition","failure","replicat","reproducib","response rate"]),
     ("Effect sizes",["odds ratio","risk ratio","hazard","effect size","difference","fold","ratio"])]
def fam_of(stat):
    t=stat.lower()
    for name,keys in FAM:
        if any(k in t for k in keys): return name
    return "Other reported figures"
groups=collections.defaultdict(list)
for pm,x in ALLM_AH:
    groups[fam_of(x["statistic"])].append((pm,x))
b=["<h1>Findings</h1>",
   '<p class="sub">Figures reported by studies that compared a non-human animal result with a '
   'human result. Each row states the statistic the study used and what it measures, in the '
   'study\'s own terms. Different studies define these differently, so they are grouped by kind '
   'and never averaged together.</p>']
for name,_ in FAM+[("Other reported figures",None)]:
    rows=groups.get(name) or []
    if not rows: continue
    b.append(f"<h2>{e(name)} <span class='tag'>{len(rows)}</span></h2>")
    b.append("<div class='scroll'><table><tr><th>Value</th><th>Statistic</th>"
             "<th>What it measures</th><th>Compared</th><th>n</th><th>Study</th></tr>")
    for pm,x in sorted(rows,key=lambda r: sortkey(r[1])):
        nn=f'{x["n"]:,} {e(x["n_counts"] or "")}'.strip() if x.get("n") else "—"
        b.append(f'<tr><td class="num">{e(fmt(x))}</td><td>{e(x["statistic"])}</td>'
                 f'<td>{e(x["measures"][:130])}</td><td>{e(x["compared"][:90])}</td>'
                 f'<td>{nn}</td><td><a href="study/{pm}.html">{e(DB[pm]["title"][:46])}</a></td></tr>')
    b.append("</table></div>")
if PDXM_AH:
    b.append("<h2>Patient-derived xenografts <span class='tag'>%d</span></h2>" % len(PDXM_AH))
    b.append('<p class="sub">Reported separately and <strong>not</strong> included in the figures '
             'above. A patient-derived xenograft grows the patient&rsquo;s own human tumour tissue in '
             'a mouse host, so these studies ask whether a patient&rsquo;s tumour predicts that same '
             'patient&rsquo;s response &mdash; not whether another species&rsquo; biology predicts human '
             'outcomes. They report high agreement on small samples; mixing them with the figures '
             'above would inflate apparent concordance.</p>')
    b.append("<div class='scroll'><table><tr><th>Value</th><th>Statistic</th>"
             "<th>What it measures</th><th>n</th><th>Study</th></tr>")
    for pm,x in sorted(PDXM_AH,key=lambda r: sortkey(r[1])):
        nn=f'{x["n"]:,} {e(x["n_counts"] or "")}'.strip() if x.get("n") else "&mdash;"
        b.append(f'<tr><td class="num">{e(fmt(x))}</td><td>{e(x["statistic"])}</td>'
                 f'<td>{e(x["measures"][:130])}</td><td>{nn}</td>'
                 f'<td><a href="study/{pm}.html">{e(DB[pm]["title"][:46])}</a></td></tr>')
    b.append("</table></div>")
open(os.path.join(OUT,"findings.html"),"w").write(page("Findings","".join(b)))

# ---------------- studies ----------------
b=["<h1>Studies</h1>",'<p class="sub">All studies that report a quantitative comparison between '
   'animal and human results.</p>','<div class="scroll"><table>'
   "<tr><th>Year</th><th>Study</th><th>Arm</th><th>Species</th><th>Figures</th><th>Cited by</th></tr>"]
for pm,v in sorted(ELIG.items(),key=lambda kv:(-(kv[1].get("year") or 0),kv[1].get("title",""))):
    pdxtag = ' <span class="tag">PDX</span>' if pm in PDX else ""
    sp=", ".join(cls(pm,"species") or [])
    b.append(f'<tr><td>{e(v.get("year"))}</td><td><a href="study/{pm}.html">{e(v.get("title","")[:88])}</a><br>'
             f'<span class="tag">{e(v.get("journal"))}</span></td><td>{e(cls(pm,"arm"))}</td>'
             f'<td>{e(sp[:38])}</td><td class="num">{len(meas(pm))}</td><td class="num">{e(v.get("cited_by"))}</td></tr>')
b.append("</table></div>")
open(os.path.join(OUT,"studies.html"),"w").write(page("Studies","".join(b)))

# ---------------- facets ----------------
def facet(key,title,fname):
    c=facet_counts(key); bb=[f"<h1>{e(title)}</h1>"]
    bb.append(f'<p class="sub">{len(c)} {title.lower()} across {len(ELIG)} studies. '
              'Figures shown are those the studies reported.</p>')
    for k,n in c.most_common():
        pms=[pm for pm in CORE if k in ((cls(pm,key) or []) if isinstance(cls(pm,key),list) else [cls(pm,key)])]
        bb.append(f'<h3 id="{e(k)}">{e(k)} <span class="tag">{n} studies</span></h3>')
        rows=[(pm,x) for pm in pms for x in meas(pm, ah_only=True)]
        if rows:
            bb.append("<div class='scroll'><table><tr><th>Value</th><th>Statistic</th>"
                      "<th>What it measures</th><th>Study</th></tr>")
            for pm,x in sorted(rows,key=lambda r: sortkey(r[1]))[:12]:
                bb.append(f'<tr><td class="num">{e(fmt(x))}</td><td>{e(x["statistic"])}</td>'
                          f'<td>{e(x["measures"][:110])}</td>'
                          f'<td><a href="study/{pm}.html">{e(DB[pm]["title"][:44])}</a></td></tr>')
            bb.append("</table></div>")
        bb.append("<ul>"+"".join(
            f'<li><a href="study/{pm}.html">{e(DB[pm]["title"][:84])}</a> '
            f'<span class="tag">{e(DB[pm].get("year"))}</span></li>'
            for pm in sorted(pms,key=lambda p:-(DB[p].get("cited_by") or 0))[:20])+"</ul>")
    open(os.path.join(OUT,fname),"w").write(page(title,"".join(bb)))
facet("species","Species","species.html")
facet("therapeutic_areas","Therapeutic areas","areas.html")
facet("arm","Evidence arms","arms.html")

# ---------------- per-study ----------------
for pm,v in DB.items():
    m=MS.get(pm) or {}; md=META.get(pm,{}); fs=FTS.get(pm,{}); c=CLS.get(pm) or {}
    ident=[f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pm}/">PMID {pm}</a>']
    if md.get("doi"): ident.append(f'<a href="https://doi.org/{e(md["doi"])}">doi:{e(md["doi"])}</a>')
    if md.get("pmcid"): ident.append(f'<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/{e(md["pmcid"])}/">{e(md["pmcid"])}</a>')
    body=[f'<h1>{e(v.get("title"))}</h1>',
      f'<p class="sub">{e(", ".join(md.get("authors_full") or v.get("authors") or [])[:400])}<br>'
      f'<em>{e(md.get("journal_full") or v.get("journal"))}</em> &middot; {e(v.get("year"))} &middot; '
      f'cited by {e(v.get("cited_by"))} &middot; {" &middot; ".join(ident)}</p>']
    if not v.get("eligible"):
        body.append(f'<div class="card"><strong>Not included.</strong> {e(v.get("exclusion_reason",""))}</div>')
    if m.get("what_the_study_did"):
        body.append(f'<div class="card"><strong>What it did</strong><br>{e(m["what_the_study_did"])}</div>')
    if m.get("what_it_found"):
        body.append(f'<div class="card"><strong>What it found</strong><br>{e(m["what_it_found"])}</div>')
    mm_all=meas(pm)
    ah=[x for x in mm_all if x.get("_scope")=="animal-vs-human"]
    other=[x for x in mm_all if x.get("_scope")!="animal-vs-human"]
    def figtable(rows, heading, note=None):
        if not rows: return
        body.append(f"<h2>{heading} <span class='tag'>{len(rows)}</span></h2>")
        if note: body.append(f'<p class="sub">{note}</p>')
        body.append("<div class='scroll'><table><tr><th>Value</th><th>Statistic</th>"
                    "<th>What it measures</th><th>Compared</th><th>Species</th><th>n</th></tr>")
        for x in sorted(rows, key=sortkey):
            nn=f'{x["n"]:,} {e(x["n_counts"] or "")}'.strip() if x.get("n") else "—"
            body.append(f'<tr><td class="num">{e(fmt(x))}</td><td>{e(x["statistic"])}</td>'
                        f'<td>{e(x["measures"])}<br><span class="verb">&ldquo;{e(x["verbatim"][:200])}&rdquo;</span></td>'
                        f'<td>{e(x["compared"])}</td><td>{e(", ".join(x.get("species") or []))}</td><td>{nn}</td></tr>')
        body.append("</table></div>")
    figtable(ah, "Animal compared with human")
    figtable(other, "Other figures reported",
             "Comparisons within a species, with non-animal methods, or about how the "
             "research was conducted. Recorded for completeness; not animal-to-human concordance.")
    for q in (m.get("key_quotes") or []):
        body.append(f'<div class="quote"><span class="t">{e(q.get("topic"))}</span>{e(q.get("quote"))}</div>')
    if md.get("abstract_sections"):
        body.append("<h2>Abstract</h2>"+"".join(
            f'<div class="card"><strong>{e(l)}</strong><br>{e(t)}</div>' for l,t in md["abstract_sections"]))
    elif md.get("abstract"):
        body.append(f'<h2>Abstract</h2><div class="card">{e(md["abstract"])}</div>')
    if md.get("mesh"):
        body.append("<h2>MeSH terms</h2><p>"+"".join(
            f'<span class="tag">{e(t["term"])}</span>' for t in md["mesh"])+"</p>")
    prov=[("Arm",cls(pm,"arm")),("Species",", ".join(cls(pm,"species") or [])),
          ("Therapeutic areas",", ".join(cls(pm,"therapeutic_areas") or [])),
          ("Model type",cls(pm,"model_type")),("Endpoint class",cls(pm,"endpoint_class")),
          ("Comparison type",v.get("r4_comparison_type")),
          ("Publication types",", ".join(md.get("publication_types") or [])),
          ("Funding",", ".join(md.get("grants") or []) or "none listed"),
          ("Source text",("full text" if (fs.get("xml") or fs.get("pdf")) else "abstract"))]
    body.append("<h2>Classification and provenance</h2><div class='scroll'><table>"
        +"".join(f"<tr><th>{e(k)}</th><td>{e(val) if val else '<span class=tag>not recorded</span>'}</td></tr>"
                 for k,val in prov)+"</table></div>")
    open(os.path.join(OUT,"study",f"{pm}.html"),"w").write(page(v.get("title","Study")[:60],"".join(body),depth=1))
    json.dump({**v,"classification":c,"measurements":m,"metadata":md},
              open(os.path.join(OUT,"api","study",f"{pm}.json"),"w"),indent=1)

# ---------------- excluded ----------------
b=["<h1>Excluded studies</h1>",
   f'<p class="sub">{len(EXCL)} records were screened and not included. They are listed with '
   'the reason so the decision can be checked or overturned.</p>',
   "<div class='scroll'><table><tr><th>Study</th><th>Year</th><th>Cited by</th><th>Reason</th></tr>"]
for pm,v in sorted(EXCL.items(),key=lambda kv:-(kv[1].get("cited_by") or 0)):
    b.append(f'<tr><td><a href="study/{pm}.html">{e(v.get("title","")[:62])}</a></td>'
             f'<td>{e(v.get("year"))}</td><td class="num">{e(v.get("cited_by"))}</td>'
             f'<td>{e((v.get("exclusion_reason") or "")[:230])}</td></tr>')
b.append("</table></div>")
open(os.path.join(OUT,"excluded.html"),"w").write(page("Excluded","".join(b)))

# ---------------- methods ----------------
b=["<h1>Methods</h1>",
 "<h2>What counts as a study here</h2>",
 "<p>A study is included when it reports a quantitative comparison in which one side is a "
 "result in a live non-human animal and the other is a human clinical result. Papers that "
 "argue animals do or do not predict human outcomes, without measuring it, are excluded. "
 "So are studies whose predictor is a cell line, organoid, organ-on-chip, isolated assay, "
 "or a computational model &mdash; this review is about animal models. Comparisons within a "
 "single species (diseased vs healthy animals, treated vs sham) do not qualify.</p>",
 "<h2>How studies were found</h2>",
 "<p>Two mechanisms, because neither is sufficient alone. A multi-strand PubMed query "
 "recovered 82.8% of a 29-paper verified anchor set; citation chasing recovered 79.3%. They "
 "fail on different records; together they recovered all 29. This literature has no shared "
 "vocabulary and no MeSH term meaning &ldquo;measures animal-to-human concordance&rdquo;, and "
 "the obvious search terms carry the wrong sense: <code>Predictive Value of Tests</code> indexes "
 "diagnostic-test accuracy, <code>concordan*</code> is dominated by twin studies, and "
 "<code>translat*</code> mostly matches protein translation.</p>",
 "<h2>How figures were extracted</h2>",
 "<p>Each reported figure is stored with the statistic the study used, its value on the "
 "study's own scale, what it measures, what was compared, the species, the sample size and "
 "what that size counts, and the sentence it came from. Figures are never converted between "
 "scales or combined across studies.</p>",
 "<h2>Checks</h2>",
 "<p>An automated audit verifies that every extracted number appears in its source and that "
 "no non-proportional quantity is stored in a proportion field. Screening and extraction are "
 "model-assisted and have not been independently verified by a second reader.</p>",
 "<h2>Not done</h2>",
 "<p>No pooled estimates, no meta-analysis, no conclusions. Studies define concordance "
 "differently; averaging them before recoding onto a common definition would produce a number "
 "with no defensible meaning.</p>"]
open(os.path.join(OUT,"methods.html"),"w").write(page("Methods","".join(b)))

json.dump({"updated":BUILT,"studies":len(CORE),"pdx_separate":len(PDX),"excluded":len(EXCL),
  "reported_figures":len(ALLM),"arms":dict(facet_counts("arm")),
  "species":dict(facet_counts("species")),"areas":dict(facet_counts("therapeutic_areas"))},
  open(os.path.join(OUT,"api","summary.json"),"w"),indent=1)
json.dump({pm:{**v,"classification":CLS.get(pm,{}),"measurements":MS.get(pm,{})} for pm,v in ELIG.items()},
  open(os.path.join(OUT,"api","bulk.json"),"w"),indent=1)
open(os.path.join(OUT,".nojekyll"),"w").write("")
for old in ("coverage.html","gaps.html"):
    p=os.path.join(OUT,old)
    if os.path.exists(p): os.remove(p)
print(f"built: {len(ELIG)} studies, {len(ALLM)} figures, {len(EXCL)} excluded")
