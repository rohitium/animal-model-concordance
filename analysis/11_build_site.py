"""Generate the static site from data/db/studies.json.

Database-first: the site is a VIEW of the data. Nothing is rendered that is not in
the database, and every claim carries a PMID. Output is plain HTML + JSON, no build
step, no runtime dependency -- suitable for GitHub Pages."""
import sys, os, json, html, collections
sys.path.insert(0, os.path.dirname(__file__))
import normalize
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "site", "_build")
DB = json.load(open(os.path.join(ROOT, "data", "db", "studies.json")))
os.makedirs(os.path.join(OUT, "api", "study"), exist_ok=True)
os.makedirs(os.path.join(OUT, "study"), exist_ok=True)
e = lambda s: html.escape(str(s if s is not None else ""))
ok = {k: v for k, v in DB.items() if v.get("extraction_status") == "ok"}
# Add controlled-vocabulary fields; raw extraction is preserved untouched.
for _v in DB.values():
    _v["species_norm"] = normalize.species(_v.get("species"))
    _v["areas_norm"] = normalize.areas(_v.get("therapeutic_areas"))

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#e2e2e2;--accent:#8a2f2f;--card:#fafafa;--warn:#7a5b00;--warnbg:#fff8e1}
:root:not([data-theme=light]) @media (prefers-color-scheme:dark){}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#111;--fg:#e8e8e8;--mut:#999;--line:#2c2c2c;--accent:#e08585;--card:#1a1a1a;--warn:#e0c060;--warnbg:#241f00}}
:root[data-theme=dark]{--bg:#111;--fg:#e8e8e8;--mut:#999;--line:#2c2c2c;--accent:#e08585;--card:#1a1a1a;--warn:#e0c060;--warnbg:#241f00}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;margin:0;padding:0}
.wrap{max-width:1080px;margin:0 auto;padding:2rem 1.25rem 4rem}
h1{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em}
h2{font-size:1.25rem;margin:2.4rem 0 .8rem;padding-bottom:.35rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.4rem 0 .4rem}
a{color:var(--accent)}
.sub{color:var(--mut);margin:0 0 1.5rem}
nav{display:flex;gap:1.2rem;flex-wrap:wrap;padding:.8rem 0;border-bottom:1px solid var(--line);margin-bottom:1.5rem;font-size:.9rem}
.banner{background:var(--warnbg);color:var(--warn);border:1px solid var(--warn);border-radius:6px;padding:.85rem 1rem;font-size:.88rem;margin:1rem 0 1.75rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:1rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.9rem}
.stat .n{font-size:1.6rem;font-weight:600;letter-spacing:-.02em}
.stat .l{color:var(--mut);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tag{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:3px;padding:.08rem .4rem;font-size:.76rem;color:var(--mut);margin:0 .2rem .2rem 0}
.null{color:var(--mut);font-style:italic}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:1rem;margin:.7rem 0}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.82rem}
code{background:var(--card);padding:.1rem .3rem;border-radius:3px;font-size:.85em}
"""
def page(title, body, depth=0):
    up = "../" * depth
    return f"""<meta charset="utf-8"><title>{e(title)}</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>
<div class="wrap"><nav><a href="{up}index.html">Overview</a><a href="{up}studies.html">Studies</a>
<a href="{up}species.html">Species</a><a href="{up}areas.html">Areas</a><a href="{up}arms.html">Arms</a>
<a href="{up}methods.html">Methods</a><a href="{up}gaps.html">Evidence gaps</a></nav>{body}
<footer>Animal Model Concordance &middot; pilot slice, {len(DB)} studies &middot;
Every record resolves to a PMID. Extraction is abstract-derived and provisional.<br>
Generated from <code>data/db/studies.json</code> by <code>analysis/11_build_site.py</code>. Not peer reviewed.</footer></div>"""

BANNER = ('<div class="banner"><strong>Pilot slice — provisional.</strong> '
 f'{len(DB)} studies drawn from a screened candidate pool, not the full systematic review. '
 'Data are extracted from <strong>abstracts only</strong> (full texts require subscription access), '
 'so 2&times;2 tables, per-species breakdowns and endpoint detail are frequently missing and are shown '
 'as <span class="null">not stated</span> rather than omitted. Screening was LLM-assisted and has '
 'not been human-verified. No pooled estimates are computed and no conclusions are drawn.</div>')

def counter(field):
    c = collections.Counter()
    for v in ok.values():
        val = v.get(field)
        if isinstance(val, list):
            for x in val:
                if x: c[str(x).strip().lower()] += 1
        elif val: c[str(val)] += 1
    return c

# ---------- overview ----------
arms = counter("arm"); yrs = [v["year"] for v in DB.values() if v.get("year")]
withval = [v for v in ok.values() if v.get("concordance_value") is not None]
b = [f"<h1>Animal Model Concordance with Human Clinical Outcomes</h1>",
     '<p class="sub">A structured, citation-anchored database of studies measuring how well animal models predict human clinical outcomes.</p>',
     BANNER, '<div class="grid">',
     f'<div class="stat"><div class="n">{len(DB)}</div><div class="l">studies</div></div>',
     f'<div class="stat"><div class="n">{len(withval)}</div><div class="l">with a concordance value</div></div>',
     f'<div class="stat"><div class="n">{len(counter("species_norm"))}</div><div class="l">species</div></div>',
     f'<div class="stat"><div class="n">{len(counter("areas_norm"))}</div><div class="l">therapeutic areas</div></div>',
     f'<div class="stat"><div class="n">{min(yrs)}&ndash;{max(yrs)}</div><div class="l">year range</div></div>',
     '</div>',
     "<h2>Studies by arm</h2>",
     '<div class="scroll"><table><tr><th>Arm</th><th>Studies</th><th>Reporting a concordance value</th></tr>']
for a, n in arms.most_common():
    wv = sum(1 for v in ok.values() if v.get("arm") == a and v.get("concordance_value") is not None)
    b.append(f'<tr><td><a href="arms.html#{e(a)}">{e(a)}</a></td><td>{n}</td><td>{wv}</td></tr>')
b.append("</table></div>")
b.append('<h2>Reported concordance values</h2>')
if withval:
    b.append('<p class="sub">Each value as reported by its source study. Definitions differ between '
             'studies and these are <strong>not</strong> pooled — see Methods.</p><div class="scroll"><table>'
             '<tr><th>Study</th><th>Arm</th><th>Metric</th><th>Value</th><th>Pairs</th></tr>')
    for v in sorted(withval, key=lambda x: -(x.get("concordance_value") or 0)):
        b.append(f'<tr><td><a href="study/{v["pmid"]}.html">{e(v["title"][:70])}</a></td>'
                 f'<td>{e(v.get("arm"))}</td><td>{e(v.get("concordance_metric"))}</td>'
                 f'<td>{v["concordance_value"]:.0%}</td><td>{e(v.get("n_pairs")) or "&mdash;"}</td></tr>')
    b.append("</table></div>")
open(os.path.join(OUT, "index.html"), "w").write(page("Animal Model Concordance", "".join(b)))

# ---------- studies ----------
b = ["<h1>Studies</h1>", BANNER, '<div class="scroll"><table><tr><th>Year</th><th>Study</th>'
     '<th>Arm</th><th>Design</th><th>Cited by</th></tr>']
for v in sorted(DB.values(), key=lambda x: (-(x.get("year") or 0), x.get("title",""))):
    b.append(f'<tr><td>{e(v.get("year"))}</td>'
             f'<td><a href="study/{v["pmid"]}.html">{e(v.get("title","")[:95])}</a><br>'
             f'<span class="tag">{e(v.get("journal"))}</span></td>'
             f'<td>{e(v.get("arm")) or "<span class=null>&mdash;</span>"}</td>'
             f'<td>{e(v.get("study_design")) or "<span class=null>&mdash;</span>"}</td>'
             f'<td>{e(v.get("cited_by"))}</td></tr>')
b.append("</table></div>")
open(os.path.join(OUT, "studies.html"), "w").write(page("Studies", "".join(b)))

# ---------- facets ----------
def facet(field, title, fname):
    c = counter(field)
    bb = [f"<h1>{e(title)}</h1>", BANNER]
    if not c: bb.append('<p class="null">Nothing extracted for this field.</p>')
    for key, n in c.most_common():
        studies = [v for v in ok.values()
                   if (key in [str(x).strip().lower() for x in (v.get(field) or [])])
                   or (str(v.get(field)) == key)]
        bb.append(f'<h3 id="{e(key)}">{e(key)} <span class="tag">{n}</span></h3><ul>')
        for v in sorted(studies, key=lambda x: -(x.get("cited_by") or 0))[:25]:
            bb.append(f'<li><a href="study/{v["pmid"]}.html">{e(v["title"][:88])}</a> '
                      f'<span class="tag">{e(v.get("year"))}</span></li>')
        bb.append("</ul>")
    open(os.path.join(OUT, fname), "w").write(page(title, "".join(bb)))
facet("species_norm", "Species", "species.html")
facet("areas_norm", "Therapeutic areas", "areas.html")
facet("arm", "Evidence arms", "arms.html")

# ---------- per-study ----------
for pm, v in DB.items():
    rows = []
    def row(lbl, val):
        if val in (None, "", [], "not-stated"):
            rows.append(f'<tr><th>{e(lbl)}</th><td class="null">not stated in abstract</td></tr>')
        elif isinstance(val, list):
            rows.append(f'<tr><th>{e(lbl)}</th><td>' + "".join(f'<span class="tag">{e(x)}</span>' for x in val) + "</td></tr>")
        else:
            rows.append(f'<tr><th>{e(lbl)}</th><td>{e(val)}</td></tr>')
    row("Arm", v.get("arm")); row("Species", v.get("species_norm"))
    row("Species (as stated)", v.get("species"))
    row("Therapeutic areas", v.get("areas_norm"))
    row("Areas (as stated)", v.get("therapeutic_areas")); row("Model type", v.get("model_type"))
    row("Study design", v.get("study_design")); row("Endpoint class", v.get("endpoint_class"))
    row("Concordance metric", v.get("concordance_metric"))
    row("Concordance value", f'{v["concordance_value"]:.0%}' if v.get("concordance_value") is not None else None)
    row("Pairs (n)", v.get("n_pairs")); row("Evidence type", v.get("evidence_vs_opinion"))
    qc = v.get("quantitative_claims") or []
    body = [f'<h1>{e(v.get("title"))}</h1>',
            f'<p class="sub">{e(", ".join(v.get("authors") or []))} &middot; '
            f'<em>{e(v.get("journal"))}</em> &middot; {e(v.get("year"))} &middot; '
            f'cited by {e(v.get("cited_by"))} &middot; '
            f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pm}/">PMID {pm}</a></p>',
            f'<div class="banner">Fields below are extracted from the <strong>abstract only</strong> '
            f'({e(v.get("extraction_status"))}). Absent fields are marked <span class="null">not stated '
            f'in abstract</span> — they may well be reported in the full text.</div>']
    if v.get("key_finding"):
        body.append(f'<div class="card"><strong>Stated finding</strong><br>{e(v["key_finding"])}</div>')
    body.append('<div class="scroll"><table>' + "".join(rows) + "</table></div>")
    if qc:
        body.append("<h2>Quantitative statements in the abstract</h2><ul>"
                    + "".join(f"<li>{e(x)}</li>" for x in qc) + "</ul>")
    body.append(f'<h2>Provenance</h2><div class="scroll"><table>'
                f'<tr><th>Retrieved by</th><td>' + "".join(f'<span class="tag">{e(s)}</span>' for s in v.get("sources", [])) + "</td></tr>"
                f'<tr><th>Screening decision</th><td>{e(v.get("screen_reason",""))[:400]}</td></tr>'
                f'<tr><th>Extraction source</th><td>{e(v.get("extraction_source"))}</td></tr>'
                f'<tr><th>Rubric version</th><td>{e(v.get("rubric_version"))}</td></tr></table></div>')
    open(os.path.join(OUT, "study", f"{pm}.html"), "w").write(page(v.get("title","Study")[:60], "".join(body), depth=1))
    json.dump(v, open(os.path.join(OUT, "api", "study", f"{pm}.json"), "w"), indent=1)

# ---------- methods & gaps ----------
meth = open(os.path.join(ROOT, "PLAN.md")).read().count("\n")
b = ["<h1>Methods</h1>", BANNER,
 "<h2>How these studies were found</h2>",
 "<p>Retrieval uses two mechanisms of equal standing, because neither is sufficient alone. "
 "A multi-strand Boolean query union recovered 82.8% of a 29-paper verified anchor set; "
 "citation chasing (forward and backward, leave-one-out) recovered 79.3%. They fail on "
 "<em>different</em> records, and their union recovered 29/29.</p>",
 "<h2>Why no single query works</h2>",
 "<p>This literature has no shared vocabulary and no MeSH descriptor meaning &ldquo;measures "
 "animal-to-human concordance&rdquo;. The high-volume candidate terms carry the wrong sense: "
 "<code>Predictive Value of Tests</code>[Mesh] (245,644 records) indexes diagnostic-test accuracy, "
 "<code>concordan*</code>[tiab] (108,835) is dominated by genetic and twin concordance, and "
 "<code>translat*</code>[tiab] (546,492) largely matches protein translation.</p>",
 "<h2>Screening</h2>",
 "<p>LLM-assisted against a fixed rubric: a record is included only if it itself reports a "
 "quantitative animal-to-human agreement statistic. Being an influential paper <em>about</em> "
 "the translation problem is not sufficient. Records with no abstract are never excluded on the "
 "title alone; they auto-advance. Screening has <strong>not</strong> been human-verified.</p>",
 "<h2>What is deliberately absent</h2>",
 "<p>No pooled estimates, no sensitivity/specificity, no conclusions. Source studies use "
 "incompatible concordance definitions, and pooling them before recoding onto a common scale "
 "would produce a number with no defensible meaning.</p>"]
open(os.path.join(OUT, "methods.html"), "w").write(page("Methods", "".join(b)))

vet = [v for v in ok.values() if v.get("arm") == "veterinary"]
b = ["<h1>Evidence gaps</h1>", BANNER,
 "<h2>Veterinary / naturally occurring disease</h2>",
 f"<p>The veterinary arm contains <strong>{len(vet)}</strong> studies in this slice. This is a "
 "finding, not a sampling artefact. A targeted search for veterinary-patient studies "
 "(<code>client-owned</code>, <code>pet dogs</code>, <code>canine patients</code>, "
 "<code>comparative oncology</code>) returned 174 records, of which 1 met the inclusion rule.</p>",
 "<p>The retrieved papers are on-topic and well cited &mdash; for example Vail &amp; MacEwen 2000, "
 "<em>Spontaneously occurring tumors of companion animals as models for human cancer</em> (213 citations). "
 "They were excluded because they <strong>argue</strong> that companion animals are good models "
 "without <strong>measuring</strong> concordance against human outcomes.</p>",
 '<div class="card">The comparative-oncology literature advocates for the model rather than '
 "quantifying its predictive accuracy. Whether naturally occurring veterinary disease predicts "
 "human outcomes better than induced laboratory models therefore cannot be answered from studies "
 "that measure concordance directly &mdash; it would require extracting paired animal/human "
 "outcomes from primary sources.</div>",
 "<h2>Abstract-only extraction</h2>",
 "<p>2&times;2 tables, per-species breakdowns, and endpoint detail are usually reported in full "
 "text, not abstracts. Fields shown as <span class='null'>not stated in abstract</span> are "
 "unknown here, not absent from the literature.</p>"]
open(os.path.join(OUT, "gaps.html"), "w").write(page("Evidence gaps", "".join(b)))

json.dump({"studies": len(DB), "extracted_ok": len(ok),
           "arms": dict(arms), "species": dict(counter("species_norm")),
           "areas": dict(counter("areas_norm")),
           "note": "Pilot slice. Abstract-derived, LLM-screened, not human-verified. No pooled estimates."},
          open(os.path.join(OUT, "api", "summary.json"), "w"), indent=1)
json.dump(DB, open(os.path.join(OUT, "api", "bulk.json"), "w"), indent=1)
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print(f"built {OUT}: {len(DB)} studies, {len(ok)} extracted, "
      f"{len(os.listdir(os.path.join(OUT,'study')))} study pages")
