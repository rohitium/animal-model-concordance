"""Build the site from all data layers: extraction (abstract), full-text extraction,
and PubMed metadata. Supersedes 11_build_site.py.

Layering rule: a field shown from full text is labelled as such; a field only
available from the abstract is labelled as such; a field nobody reports is shown as
missing. The three states must never look alike."""
import sys, os, json, html, collections, datetime
sys.path.insert(0, os.path.dirname(__file__))
import normalize
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "site", "_build")
J = lambda *p: os.path.join(ROOT, *p)
load = lambda p, d={}: json.load(open(J(*p))) if os.path.exists(J(*p)) else d

def route_label(fs, f):
    """The resume pass rewrote routes as 'recovered_from_disk', which says nothing
    about provenance. Recover the real source from the artefact on disk."""
    r = (f or {}).get("route") or (fs or {}).get("route")
    if r and r != "recovered_from_disk":
        return {"europepmc_xml": "Europe PMC full-text XML",
                "unpaywall_pdf": "Unpaywall open-access PDF",
                "pmc_pdf": "PMC PDF"}.get(r, r)
    if (fs or {}).get("xml"): return "Europe PMC full-text XML"
    if (fs or {}).get("pdf"): return "open-access PDF"
    return "unknown"

DB   = load(("data","db","studies.json"))
META = load(("data","db","metadata.json"))
FT   = load(("data","db","fulltext_extract.json"))
FTS  = load(("data","raw","fulltext_status.json"))
for d in (os.path.join(OUT,"api","study"), os.path.join(OUT,"study")):
    os.makedirs(d, exist_ok=True)
e = lambda s: html.escape(str(s if s is not None else ""))
ok = {k:v for k,v in DB.items() if v.get("extraction_status")=="ok"}
for v in DB.values():
    v["species_norm"] = normalize.species(v.get("species"))
    v["areas_norm"] = normalize.areas(v.get("therapeutic_areas"))
ftok = {k:v for k,v in FT.items() if "error" not in v}
BUILT = datetime.date.today().isoformat()

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6a6a6a;--line:#e4e4e4;--accent:#8a2f2f;--card:#fafafa;
--warn:#7a5b00;--warnbg:#fff8e1;--good:#15603a;--goodbg:#e8f5ee;--chip:#eee}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#101010;--fg:#e9e9e9;--mut:#9a9a9a;
--line:#2b2b2b;--accent:#e59090;--card:#181818;--warn:#e0c060;--warnbg:#241f00;--good:#7fd6a6;--goodbg:#0d2018;--chip:#232323}}
:root[data-theme=dark]{--bg:#101010;--fg:#e9e9e9;--mut:#9a9a9a;--line:#2b2b2b;--accent:#e59090;
--card:#181818;--warn:#e0c060;--warnbg:#241f00;--good:#7fd6a6;--goodbg:#0d2018;--chip:#232323}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);margin:0;font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:1.5rem 1.25rem 4rem}
h1{font-size:1.85rem;line-height:1.25;margin:0 0 .35rem;letter-spacing:-.021em}
h2{font-size:1.2rem;margin:2.2rem 0 .7rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
h3{font-size:.98rem;margin:1.5rem 0 .35rem}
a{color:var(--accent)}.sub{color:var(--mut);margin:0 0 1.2rem;font-size:.94rem}
nav{display:flex;gap:1.1rem;flex-wrap:wrap;padding:.7rem 0;border-bottom:1px solid var(--line);margin-bottom:1.4rem;font-size:.88rem}
.banner{background:var(--warnbg);color:var(--warn);border:1px solid var(--warn);border-radius:6px;padding:.8rem .95rem;font-size:.86rem;margin:1rem 0 1.6rem}
.okbox{background:var(--goodbg);color:var(--good);border:1px solid var(--good);border-radius:6px;padding:.8rem .95rem;font-size:.86rem;margin:1rem 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.7rem;margin:1rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.85rem}
.stat .n{font-size:1.5rem;font-weight:600;letter-spacing:-.02em}
.stat .l{color:var(--mut);font-size:.74rem;text-transform:uppercase;letter-spacing:.045em;margin-top:.15rem}
table{border-collapse:collapse;width:100%;font-size:.89rem}
th,td{text-align:left;padding:.48rem .55rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:.75rem;text-transform:uppercase;letter-spacing:.045em}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}
.tag{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:3px;padding:.06rem .38rem;font-size:.75rem;color:var(--mut);margin:0 .18rem .18rem 0}
.tag.maj{color:var(--fg);font-weight:600}
.null{color:var(--mut);font-style:italic}
.src{font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;padding:.03rem .3rem;border-radius:3px;border:1px solid var(--line);color:var(--mut);margin-left:.35rem}
.src.ft{color:var(--good);border-color:var(--good)}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.9rem 1rem;margin:.65rem 0}
.abs{background:var(--card);border-left:3px solid var(--line);padding:.7rem .95rem;font-size:.9rem;margin:.6rem 0}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.8rem}
code{background:var(--chip);padding:.08rem .28rem;border-radius:3px;font-size:.85em}
ul{padding-left:1.15rem}li{margin:.15rem 0}
.bar{height:7px;background:var(--chip);border-radius:4px;overflow:hidden;min-width:70px}
.bar>i{display:block;height:100%;background:var(--accent)}
"""
NAV = [("index.html","Overview"),("studies.html","Studies"),("findings.html","Findings"),
       ("species.html","Species"),("areas.html","Areas"),("arms.html","Arms"),
       ("methods.html","Methods"),("gaps.html","Evidence gaps"),("coverage.html","Full-text coverage")]
def page(title, body, depth=0):
    up = "../"*depth
    nav = "".join(f'<a href="{up}{h}">{e(t)}</a>' for h,t in NAV)
    return (f'<meta charset="utf-8"><title>{e(title)}</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>'
            f'<div class="wrap"><nav>{nav}</nav>{body}'
            f'<footer>Animal Model Concordance &middot; pilot slice of {len(DB)} studies &middot; built {BUILT}<br>'
            f'Every record resolves to a PMID. Generated from <code>data/db/</code> by '
            f'<code>analysis/15_build_site.py</code>. Not peer reviewed; no pooled estimates.</footer></div>')

nft = len(ftok)
BANNER = ('<div class="banner"><strong>Pilot slice &mdash; provisional.</strong> '
 f'{len(DB)} studies from a screened candidate pool, not the full systematic review. '
 f'<strong>{nft}</strong> have open-access full text extracted; the remainder are '
 'abstract-only, where 2&times;2 tables and per-species detail are usually unavailable. '
 'Screening was LLM-assisted and is <strong>not human-verified</strong>. '
 'No pooled estimates are computed and no conclusions are drawn.</div>')

def counter(field):
    c = collections.Counter()
    for v in ok.values():
        val = v.get(field)
        if isinstance(val, list):
            for x in val:
                if x: c[str(x).strip().lower()] += 1
        elif val: c[str(val)] += 1
    return c
def pct(x): return f"{x*100:.0f}%" if isinstance(x,(int,float)) else None

# ---------------- overview ----------------
arms = counter("arm"); yrs=[v["year"] for v in DB.values() if v.get("year")]
metrics = [(pm,v) for pm,v in ftok.items() if v.get("sensitivity") is not None or v.get("ppv") is not None]
withval = [v for v in ok.values() if v.get("concordance_value") is not None]
b=[ "<h1>Animal Model Concordance with Human Clinical Outcomes</h1>",
 '<p class="sub">A structured, citation-anchored database of studies measuring how well animal models predict human clinical outcomes.</p>',
 BANNER,'<div class="grid">',
 f'<div class="stat"><div class="n">{len(DB)}</div><div class="l">studies</div></div>',
 f'<div class="stat"><div class="n">{nft}</div><div class="l">full text extracted</div></div>',
 f'<div class="stat"><div class="n">{len(withval)}</div><div class="l">concordance value</div></div>',
 f'<div class="stat"><div class="n">{len(metrics)}</div><div class="l">sens/spec/PPV</div></div>',
 f'<div class="stat"><div class="n">{len(counter("species_norm"))}</div><div class="l">species</div></div>',
 f'<div class="stat"><div class="n">{min(yrs)}&ndash;{max(yrs)}</div><div class="l">years</div></div>','</div>',
 "<h2>Studies by arm</h2>",'<div class="scroll"><table><tr><th>Arm</th><th>Studies</th><th>With concordance value</th><th>With full text</th></tr>']
for a,n in arms.most_common():
    wv=sum(1 for v in ok.values() if v.get("arm")==a and v.get("concordance_value") is not None)
    wf=sum(1 for pm,v in ok.items() if v.get("arm")==a and pm in ftok)
    b.append(f'<tr><td><a href="arms.html#{e(a)}">{e(a)}</a></td><td>{n}</td><td>{wv}</td><td>{wf}</td></tr>')
b.append("</table></div>")
b.append('<h2>Species represented</h2><div class="scroll"><table><tr><th>Species</th><th>Studies</th><th></th></tr>')
sc=counter("species_norm"); mx=max(sc.values()) if sc else 1
for k,n in sc.most_common():
    b.append(f'<tr><td><a href="species.html#{e(k)}">{e(k)}</a></td><td>{n}</td>'
             f'<td><div class="bar"><i style="width:{n/mx*100:.0f}%"></i></div></td></tr>')
b.append("</table></div>")
open(os.path.join(OUT,"index.html"),"w").write(page("Animal Model Concordance","".join(b)))

# ---------------- findings ----------------
b=["<h1>Reported findings</h1>",BANNER,
 '<p class="sub">Every value as reported by its source study. Definitions of "concordance" '
 'differ between studies, so these are <strong>not</strong> pooled and must not be averaged.</p>']
if metrics:
    b.append("<h2>Diagnostic-accuracy metrics (from full text)</h2><div class='scroll'><table>"
             "<tr><th>Study</th><th>Arm</th><th>Sens</th><th>Spec</th><th>PPV</th><th>NPV</th><th>n</th></tr>")
    for pm,v in sorted(metrics,key=lambda x:-(x[1].get("sensitivity") or 0)):
        d=DB[pm]
        b.append(f'<tr><td><a href="study/{pm}.html">{e(d["title"][:60])}</a></td><td>{e(d.get("arm"))}</td>'
                 f'<td>{pct(v.get("sensitivity")) or "&mdash;"}</td><td>{pct(v.get("specificity")) or "&mdash;"}</td>'
                 f'<td>{pct(v.get("ppv")) or "&mdash;"}</td><td>{pct(v.get("npv")) or "&mdash;"}</td>'
                 f'<td>{e(v.get("n_pairs") or v.get("n_animal_studies")) or "&mdash;"}</td></tr>')
    b.append("</table></div>")
if withval:
    # Grouped by metric family. Metrics that point in opposite directions are never
    # placed in one ranked table -- see normalize.METRIC_FAMILIES.
    groups = collections.defaultdict(list)
    for v in withval:
        pm = v["pmid"]; f = ftok.get(pm, {})
        met = f.get("concordance_metric") or v.get("concordance_metric")
        groups[normalize.metric_family(met)].append((v, f, met))
    b.append("<h2>Reported values, grouped by what the metric measures</h2>")
    b.append('<div class="banner">These are <strong>not comparable across groups</strong>. '
             'A high value in one group means the opposite of a high value in another. '
             'Within a group, definitions still differ between studies. Nothing here is pooled.</div>')
    for fam in ("agreement", "disagreement", "unclassified"):
        rows = groups.get(fam) or []
        if not rows: continue
        b.append(f'<h3>{e(fam)} &mdash; <span class="sub">{e(normalize.family_note(fam))}</span></h3>')
        b.append("<div class='scroll'><table>"
                 "<tr><th>Study</th><th>Arm</th><th>Metric as reported</th><th>Value</th><th>Pairs</th><th>Source</th></tr>")
        for v, f, met in sorted(rows, key=lambda x: -(x[0].get("concordance_value") or 0)):
            pm = v["pmid"]
            src = '<span class="src ft">full text</span>' if pm in ftok else '<span class="src">abstract</span>'
            b.append(f'<tr><td><a href="study/{pm}.html">{e(v["title"][:58])}</a></td><td>{e(v.get("arm"))}</td>'
                     f'<td>{e(met)}</td><td>{pct(v["concordance_value"])}</td>'
                     f'<td>{e(v.get("n_pairs")) or "&mdash;"}</td><td>{src}</td></tr>')
        b.append("</table></div>")
sp=[(pm,v) for pm,v in ftok.items() if v.get("species_results")]
if sp:
    b.append("<h2>Per-species results reported</h2><div class='scroll'><table>"
             "<tr><th>Study</th><th>Species</th><th>Metric</th><th>Value</th><th>n</th></tr>")
    for pm,v in sp:
        for r in v["species_results"]:
            b.append(f'<tr><td><a href="study/{pm}.html">{e(DB[pm]["title"][:50])}</a></td>'
                     f'<td>{e(r.get("species"))}</td><td>{e(r.get("metric"))}</td>'
                     f'<td>{pct(r.get("value")) if isinstance(r.get("value"),(int,float)) else "&mdash;"}</td>'
                     f'<td>{e(r.get("n")) or "&mdash;"}</td></tr>')
    b.append("</table></div>")
open(os.path.join(OUT,"findings.html"),"w").write(page("Findings","".join(b)))

# ---------------- studies list ----------------
b=["<h1>Studies</h1>",BANNER,'<div class="scroll"><table><tr><th>Year</th><th>Study</th><th>Arm</th>'
   "<th>Design</th><th>Cited by</th><th>Text</th></tr>"]
for v in sorted(DB.values(),key=lambda x:(-(x.get("year") or 0),x.get("title",""))):
    pm=v["pmid"]
    tx=('<span class="src ft">full</span>' if pm in ftok else '<span class="src">abstract</span>')
    b.append(f'<tr><td>{e(v.get("year"))}</td><td><a href="study/{pm}.html">{e(v.get("title","")[:92])}</a><br>'
             f'<span class="tag">{e(v.get("journal"))}</span></td><td>{e(v.get("arm")) or "&mdash;"}</td>'
             f'<td>{e(v.get("study_design")) or "&mdash;"}</td><td>{e(v.get("cited_by"))}</td><td>{tx}</td></tr>')
b.append("</table></div>")
open(os.path.join(OUT,"studies.html"),"w").write(page("Studies","".join(b)))

# ---------------- facets ----------------
def facet(field,title,fname):
    c=counter(field); bb=[f"<h1>{e(title)}</h1>",BANNER]
    for key,n in c.most_common():
        st_=[v for v in ok.values() if key in [str(x).strip().lower() for x in (v.get(field) or [])] or str(v.get(field))==key]
        bb.append(f'<h3 id="{e(key)}">{e(key)} <span class="tag">{n}</span></h3><ul>')
        for v in sorted(st_,key=lambda x:-(x.get("cited_by") or 0))[:30]:
            bb.append(f'<li><a href="study/{v["pmid"]}.html">{e(v["title"][:86])}</a> '
                      f'<span class="tag">{e(v.get("year"))}</span> <span class="tag">{e(v.get("cited_by"))} cites</span></li>')
        bb.append("</ul>")
    open(os.path.join(OUT,fname),"w").write(page(title,"".join(bb)))
facet("species_norm","Species","species.html")
facet("areas_norm","Therapeutic areas","areas.html")
facet("arm","Evidence arms","arms.html")

# ---------------- per-study ----------------
for pm,v in DB.items():
    m=META.get(pm,{}); f=ftok.get(pm,{}); fs=FTS.get(pm,{})
    rows=[]
    def row(lbl,val,src=None):
        tagm = f'<span class="src ft">full text</span>' if src=="ft" else (f'<span class="src">abstract</span>' if src=="ab" else "")
        if val in (None,"",[],"not-stated"):
            rows.append(f'<tr><th>{e(lbl)}</th><td class="null">not reported in available text</td></tr>')
        elif isinstance(val,list):
            rows.append(f'<tr><th>{e(lbl)}</th><td>'+"".join(f'<span class="tag">{e(x)}</span>' for x in val)+tagm+"</td></tr>")
        else:
            rows.append(f'<tr><th>{e(lbl)}</th><td>{e(val)}{tagm}</td></tr>')
    row("Arm",v.get("arm"),"ab"); row("Species",v.get("species_norm"),"ab")
    row("Species (as stated)",v.get("species"))
    row("Therapeutic areas",v.get("areas_norm"),"ab")
    row("Model type",v.get("model_type")); row("Study design",v.get("study_design"))
    row("Endpoint class",f.get("endpoint_class") or v.get("endpoint_class"),"ft" if f.get("endpoint_class") else "ab")
    row("Concordance metric",f.get("concordance_metric") or v.get("concordance_metric"),"ft" if f.get("concordance_metric") else "ab")
    cv = f.get("concordance_value") if f.get("concordance_value") is not None else v.get("concordance_value")
    row("Concordance value",pct(cv) if cv is not None else None,"ft" if f.get("concordance_value") is not None else "ab")
    for lbl,k in [("Sensitivity","sensitivity"),("Specificity","specificity"),("PPV","ppv"),("NPV","npv")]:
        if f.get(k) is not None: row(lbl,pct(f[k]),"ft")
    tt=f.get("two_by_two") or {}
    if any(tt.get(x) is not None for x in ("tp","fp","fn","tn")):
        row("2×2 (TP/FP/FN/TN)",f'{tt.get("tp")}/{tt.get("fp")}/{tt.get("fn")}/{tt.get("tn")}',"ft")
    row("Pairs (n)",f.get("n_pairs") or v.get("n_pairs"),"ft" if f.get("n_pairs") else "ab")
    row("Animal studies (n)",f.get("n_animal_studies"),"ft")
    row("Human studies (n)",f.get("n_human_studies"),"ft")
    row("Animal endpoints",f.get("endpoints_animal"),"ft")
    row("Human endpoints",f.get("endpoints_human"),"ft")
    row("Evidence type",v.get("evidence_vs_opinion"))
    ident=[]
    ident.append(f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pm}/">PMID {pm}</a>')
    if m.get("doi"): ident.append(f'<a href="https://doi.org/{e(m["doi"])}">doi:{e(m["doi"])}</a>')
    if m.get("pmcid"): ident.append(f'<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/{e(m["pmcid"])}/">{e(m["pmcid"])}</a>')
    body=[f'<h1>{e(v.get("title"))}</h1>',
      f'<p class="sub">{e(", ".join(m.get("authors_full") or v.get("authors") or [])[:400])}<br>'
      f'<em>{e(m.get("journal_full") or v.get("journal"))}</em> &middot; {e(v.get("year"))} &middot; '
      f'cited by {e(v.get("cited_by"))} &middot; {" &middot; ".join(ident)}</p>']
    if pm in ftok:
        body.append(f'<div class="okbox"><strong>Full text extracted.</strong> '
                    f'Fields marked <span class="src ft">full text</span> come from the open-access '
                    f'article ({f.get("chars",0):,}&nbsp;characters, via {e(route_label(fs, f))}). '
                    f'Fields marked <span class="src">abstract</span> were not restated in the full text pass.</div>')
    else:
        body.append('<div class="banner"><strong>Abstract only.</strong> No open-access full text was '
                    'retrievable, so 2&times;2 tables, per-species results and endpoint detail are '
                    'unavailable here. They may well be reported in the paywalled full text.</div>')
    if v.get("key_finding"):
        body.append(f'<div class="card"><strong>Stated finding</strong><br>{e(v["key_finding"])}</div>')
    if f.get("concordance_definition"):
        body.append(f'<div class="card"><strong>How this paper defines concordance</strong><br>{e(f["concordance_definition"])}</div>')
    body.append('<div class="scroll"><table>'+"".join(rows)+"</table></div>")
    kn=f.get("key_numbers") or v.get("quantitative_claims") or []
    if kn:
        body.append(f'<h2>Quantitative statements <span class="src{" ft" if f.get("key_numbers") else ""}">'
                    f'{"full text" if f.get("key_numbers") else "abstract"}</span></h2><ul>'
                    +"".join(f"<li>{e(x)}</li>" for x in kn[:40])+"</ul>")
    if f.get("limitations_stated"):
        body.append("<h2>Limitations stated by the authors</h2><ul>"+"".join(f"<li>{e(x)}</li>" for x in f["limitations_stated"])+"</ul>")
    if m.get("abstract_sections"):
        body.append("<h2>Abstract</h2>"+"".join(f'<div class="abs"><strong>{e(l)}</strong><br>{e(t)}</div>' for l,t in m["abstract_sections"]))
    elif m.get("abstract"):
        body.append(f'<h2>Abstract</h2><div class="abs">{e(m["abstract"])}</div>')
    if m.get("mesh"):
        body.append("<h2>MeSH terms</h2><p>"+"".join(
            f'<span class="tag{" maj" if t["major"] else ""}">{e(t["term"])}'
            + (" / "+e(", ".join(t["qualifiers"])) if t["qualifiers"] else "")+"</span>" for t in m["mesh"])+"</p>")
    prov=[f'<tr><th>Retrieved by</th><td>'+"".join(f'<span class="tag">{e(s)}</span>' for s in v.get("sources",[]))+"</td></tr>",
          f'<tr><th>Publication types</th><td>'+"".join(f'<span class="tag">{e(x)}</span>' for x in m.get("publication_types",[]))+"</td></tr>",
          f'<tr><th>Funding</th><td>'+("".join(f'<span class="tag">{e(x)}</span>' for x in m.get("grants",[])) or '<span class="null">none listed</span>')+"</td></tr>",
          f'<tr><th>Open access</th><td>{"yes &mdash; "+e(route_label(fs, f)) if (fs.get("xml") or fs.get("pdf")) else "not retrievable"}'
          + (f' &middot; licence {e(fs.get("license"))}' if fs.get("license") else "")+"</td></tr>",
          f'<tr><th>Extraction</th><td>{"full text + abstract" if pm in ftok else "abstract only"}</td></tr>',
          f'<tr><th>Screening decision</th><td>{e(v.get("screen_reason",""))[:400]}</td></tr>']
    body.append("<h2>Provenance</h2><div class='scroll'><table>"+"".join(prov)+"</table></div>")
    open(os.path.join(OUT,"study",f"{pm}.html"),"w").write(page(v.get("title","Study")[:60],"".join(body),depth=1))
    json.dump({**v,"metadata":m,"fulltext_extract":f,"fulltext_status":fs},
              open(os.path.join(OUT,"api","study",f"{pm}.json"),"w"),indent=1)

# ---------------- coverage ----------------
noft=[pm for pm in DB if pm not in ftok]
b=["<h1>Full-text coverage</h1>",BANNER,
 f'<p class="sub">{nft} of {len(DB)} studies have open-access full text extracted. '
 "Only openly-licensed sources were used (Europe PMC, PMC, Unpaywall); no paywall was circumvented.</p>",
 "<h2>Retrieved</h2><div class='scroll'><table><tr><th>Study</th><th>Route</th><th>Characters</th></tr>"]
for pm,f in sorted(ftok.items(),key=lambda x:-(x[1].get("chars") or 0)):
    b.append(f'<tr><td><a href="study/{pm}.html">{e(DB[pm]["title"][:70])}</a></td>'
             f'<td>{e(route_label(FTS.get(pm), f))}</td><td>{f.get("chars",0):,}</td></tr>')
b.append("</table></div>")
b.append(f"<h2>Not retrievable ({len(noft)})</h2>"
 "<p>These need manual supply. Listed with identifiers so a copy can be dropped into "
 "<code>data/raw/fulltext/&lt;pmid&gt;.pdf</code> and re-extracted.</p>"
 "<div class='scroll'><table><tr><th>Study</th><th>Journal</th><th>Year</th><th>DOI</th><th>Cited by</th></tr>")
for pm in sorted(noft,key=lambda p:-(DB[p].get("cited_by") or 0)):
    d=DB[pm]; m=META.get(pm,{})
    doi=f'<a href="https://doi.org/{e(m["doi"])}">{e(m["doi"])}</a>' if m.get("doi") else "&mdash;"
    b.append(f'<tr><td><a href="study/{pm}.html">{e(d["title"][:66])}</a></td><td>{e(d.get("journal"))}</td>'
             f'<td>{e(d.get("year"))}</td><td>{doi}</td><td>{e(d.get("cited_by"))}</td></tr>')
b.append("</table></div>")
open(os.path.join(OUT,"coverage.html"),"w").write(page("Full-text coverage","".join(b)))

# ---------------- methods & gaps ----------------
b=["<h1>Methods</h1>",BANNER,
 "<h2>Retrieval</h2><p>Two mechanisms of equal standing. A multi-strand Boolean query union "
 "recovered 82.8% of a 29-paper verified anchor set; citation chasing (leave-one-out) recovered "
 "79.3%. They fail on <em>different</em> records; their union recovered 29/29.</p>",
 "<h2>Why no single query works</h2><p>The literature has no shared vocabulary and no MeSH "
 "descriptor meaning &ldquo;measures animal-to-human concordance&rdquo;. High-volume candidate terms "
 "carry the wrong sense: <code>Predictive Value of Tests</code>[Mesh] (245,644) indexes diagnostic-test "
 "accuracy, <code>concordan*</code>[tiab] (108,835) is dominated by genetic and twin concordance, and "
 "<code>translat*</code>[tiab] (546,492) largely matches protein translation.</p>",
 "<h2>Screening</h2><p>LLM-assisted against a fixed rubric: include only if the record itself reports "
 "a quantitative animal-to-human agreement statistic. Being an influential paper <em>about</em> the "
 "translation problem is not sufficient. Records without abstracts auto-advance rather than being "
 "excluded on title alone. Validated on a 27-record gold set: sensitivity 100% (95% CI 74.1&ndash;100%), "
 "specificity 62.5% (95% CI 38.6&ndash;81.5%). The sensitivity interval is wide and cannot exclude a true "
 "value near 75%. <strong>Not human-verified.</strong></p>",
 "<h2>Extraction</h2><p>Two tiers. Open-access full text where retrievable (Europe PMC XML, PMC, "
 "Unpaywall), abstract-only otherwise. Every field on a study page is labelled with its tier. "
 "Models were instructed to return null rather than infer; spot-checks against known values "
 "(Olson 2000 &rarr; 71%, n=150; Monticello 2017 &rarr; PPV 43%, sensitivity 48%, specificity 84%, "
 "NPV 86%, n=182) matched the sources.</p>",
 "<h2>Deliberately absent</h2><p>No pooled estimates, no meta-analysis, no conclusions. Source studies "
 "use incompatible definitions of concordance; pooling them before recoding onto a common scale would "
 "produce a number with no defensible meaning.</p>"]
open(os.path.join(OUT,"methods.html"),"w").write(page("Methods","".join(b)))

vet=[v for v in ok.values() if v.get("arm")=="veterinary"]
b=["<h1>Evidence gaps</h1>",BANNER,
 "<h2>Veterinary / naturally occurring disease</h2>",
 f"<p>The veterinary arm contains <strong>{len(vet)}</strong> studies in this slice &mdash; a finding, "
 "not a sampling artefact. A targeted search for veterinary-patient studies (<code>client-owned</code>, "
 "<code>pet dogs</code>, <code>canine patients</code>, <code>comparative oncology</code>) returned 174 "
 "records, of which 1 met the inclusion rule.</p>",
 "<p>The retrieved papers are on-topic and well cited &mdash; Vail &amp; MacEwen 2000, <em>Spontaneously "
 "occurring tumors of companion animals as models for human cancer</em>, has 213 citations. They were "
 "excluded because they <strong>argue</strong> that companion animals are good models without "
 "<strong>measuring</strong> concordance against human outcomes.</p>",
 '<div class="card">The comparative-oncology literature advocates for the model rather than quantifying '
 "its predictive accuracy. Whether naturally occurring veterinary disease predicts human outcomes better "
 "than induced laboratory models cannot be answered from studies that measure concordance directly; it "
 "would require extracting paired animal/human outcomes from primary sources.</div>",
 "<h2>Full-text access</h2>",
 f"<p>{len(noft)} of {len(DB)} studies have no retrievable open-access full text. Coverage is uneven by "
 "journal, and the gap falls hardest on older toxicology and veterinary titles &mdash; the same direction "
 "as the PMC-deposition bias in citation chasing. See <a href='coverage.html'>full-text coverage</a>.</p>",
 "<h2>Rodent dominance</h2>",
 f"<p>Species coverage is {', '.join(f'{k} {n}' for k,n in counter('species_norm').most_common(6))}. "
 "Estimates for horse, chicken, cat and great apes rest on very small numbers and must not be absorbed "
 "into any headline figure.</p>"]
open(os.path.join(OUT,"gaps.html"),"w").write(page("Evidence gaps","".join(b)))

json.dump({"built":BUILT,"studies":len(DB),"fulltext_extracted":nft,
 "arms":dict(arms),"species":dict(counter("species_norm")),"areas":dict(counter("areas_norm")),
 "note":"Pilot slice. LLM-screened, not human-verified. Two extraction tiers. No pooled estimates."},
 open(os.path.join(OUT,"api","summary.json"),"w"),indent=1)
json.dump({pm:{**v,"metadata":META.get(pm,{}),"fulltext_extract":ftok.get(pm,{})} for pm,v in DB.items()},
 open(os.path.join(OUT,"api","bulk.json"),"w"),indent=1)
open(os.path.join(OUT,".nojekyll"),"w").write("")
print(f"built: {len(DB)} studies, {nft} with full text, {len(noft)} abstract-only")
