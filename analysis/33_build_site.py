"""Build the site: one landing page, one page per study.

Supersedes 24_build_site.py. Everything is driven by the question-driven records in
data/db/study_answers.json, so the pages answer our questions rather than reshaping
whatever numbers each paper happened to print."""
import sys, os, json, html, collections, datetime, re
sys.path.insert(0, os.path.dirname(__file__))
import normalize as N
ROOT=os.path.join(os.path.dirname(__file__),"..")
OUT=os.path.join(ROOT,"site","_build")
J=lambda *p: os.path.join(ROOT,*p)
load=lambda *p: json.load(open(J(*p))) if os.path.exists(J(*p)) else {}

DB=load("data","db","studies.json"); META=load("data","db","metadata.json")
ANS=load("data","db","study_answers.json"); CLS=load("data","db","classification.json")
FTS=load("data","raw","fulltext_status.json")
SYN=load("data","db","row_synthesis.json")
RATER2=load("data","db","second_rater.json")
OBJ=load("data","db","objective_verdict.json")
PROV=load("data","db","figure_provenance.json")
OK={k:v for k,v in ANS.items() if "error" not in v and DB.get(k,{}).get("eligible")}
# Patient-derived xenografts grow the patient's own human tumour in a mouse host, so they
# answer an avatar question rather than whether another species predicts human outcomes.
# Reported separately, never mixed into the organism rows.
PDX={k for k,v in DB.items() if k in OK and v.get("substrate")=="human-tissue-in-animal-host"}
CORE={k:v for k,v in OK.items() if k not in PDX}
EXCL={k:v for k,v in DB.items() if v.get("eligible") is False}
for d in (os.path.join(OUT,"api","study"), os.path.join(OUT,"study")):
    os.makedirs(d,exist_ok=True)
e=lambda s: html.escape(str(s if s is not None else ""))
BUILT=datetime.date.today().isoformat()

def agreement():
    pairs=[(k,ANS[k]["verdict"],RATER2[k]["verdict"]) for k in RATER2
           if "error" not in RATER2[k] and k in OK]
    if not pairs: return None
    n=len(pairs); po=sum(1 for _,x,y in pairs if x==y)/n
    ca=collections.Counter(x for _,x,_ in pairs); cb=collections.Counter(y for _,_,y in pairs)
    cats={v for _,x,y in pairs for v in (x,y)}
    pe=sum((ca[c]/n)*(cb[c]/n) for c in cats)
    return {"n":n,"agree":po,"kappa":(po-pe)/(1-pe) if pe<1 else 0.0,
            "disagree":{k:(x,y) for k,x,y in pairs if x!=y}}

ASSESS_LABEL={"efficacy":"Efficacy","toxicology":"Toxicology",
  "safety-pharmacology":"Safety pharmacology","disease-biology":"Disease biology",
  "veterinary":"Veterinary"}
ASSESS_ORDER=["efficacy","toxicology","safety-pharmacology","disease-biology","veterinary"]
VERDICT_LABEL={"supports":"supports","partly-supports":"partly supports",
  "does-not-support":"does not support","no-data":"no data"}

def arm(pm): return (CLS.get(pm) or {}).get("arm") or "unassigned"
def cite(pm):
    v=DB.get(pm) or {}; md=META.get(pm) or {}
    a=(md.get("authors_full") or v.get("authors") or [])
    if a:
        last=a[0].split()[-1] if " " in a[0] else a[0]
        nm=f"{last} et al." if len(a)>1 else last
    else: nm="Anon."
    return f"{nm} {v.get('year') or 'n.d.'}"
def orgs_of(pm):
    a=OK[pm]["animal_side"]
    return N.organisms(list(a.get("species") or [])+list(a.get("grouped_labels") or [])) or ["not specified"]

UNITS={"percent":"%","proportion_0_1":"","correlation":"","fold":"-fold","ratio":"×","count":"","other":""}
def fmt(c):
    v,u=c.get("value"),c.get("unit")
    if v is None: return "—"
    if u=="percent": return f"{v:g}%"
    if u=="proportion_0_1": return f"{v:g}"
    if u=="correlation": return f"r={v:g}"
    if u=="fold": return f"{v:g}-fold"
    if u=="ratio": return f"{v:g}×"
    return f"{v:g}"

CSS="""
:root{--bg:#fff;--fg:#15171a;--mut:#5f6673;--line:#e3e6ea;--accent:#8a2f2f;--card:#f8f9fa;--chip:#eef0f3;
--sup:#15603a;--supbg:#e7f4ec;--part:#7a5b00;--partbg:#fdf6e3;--not:#8a2727;--notbg:#fbeaea}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0e1013;--fg:#e8eaed;--mut:#98a0ad;
--line:#252a31;--accent:#e59090;--card:#171a1f;--chip:#1f242b;--sup:#7fd6a6;--supbg:#0e2419;--part:#e0c060;
--partbg:#241f00;--not:#f0a0a0;--notbg:#2a1414}}
:root[data-theme=dark]{--bg:#0e1013;--fg:#e8eaed;--mut:#98a0ad;--line:#252a31;--accent:#e59090;--card:#171a1f;
--chip:#1f242b;--sup:#7fd6a6;--supbg:#0e2419;--part:#e0c060;--partbg:#241f00;--not:#f0a0a0;--notbg:#2a1414}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:2rem 1.25rem 4rem}
h1{font-size:1.9rem;line-height:1.22;margin:0 0 .5rem;letter-spacing:-.022em}
h2{font-size:1.18rem;margin:2.4rem 0 .8rem;padding-bottom:.32rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.5rem 0 .4rem}
a{color:var(--accent)}
.lede{color:var(--mut);font-size:1rem;max-width:62ch;margin:0 0 1.5rem}
.sub{color:var(--mut);font-size:.9rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.65rem;margin:1.2rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:7px;padding:.75rem .85rem}
.stat .n{font-size:1.4rem;font-weight:650;letter-spacing:-.02em}
.stat .l{color:var(--mut);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-top:.1rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:.6rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:650;font-size:.73rem;text-transform:uppercase;letter-spacing:.05em}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}
td.assess{white-space:nowrap;font-weight:600}
td.org{white-space:nowrap}
.ev{margin:0 0 .55rem}
.ev:last-child{margin-bottom:0}
.ev .v{font-variant-numeric:tabular-nums;font-weight:650}
.ev .src{color:var(--mut);font-size:.83rem}
.tag{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:3px;padding:.04rem .38rem;font-size:.74rem;color:var(--mut);margin:0 .16rem .16rem 0}
.v-supports{background:var(--supbg);color:var(--sup);border-color:var(--sup)}
.v-partly-supports{background:var(--partbg);color:var(--part);border-color:var(--part)}
.v-does-not-support{background:var(--notbg);color:var(--not);border-color:var(--not)}
.card{background:var(--card);border:1px solid var(--line);border-radius:7px;padding:.9rem 1rem;margin:.7rem 0}
.caveat{border-left:3px solid var(--part);background:var(--partbg);color:var(--part);padding:.55rem .8rem;border-radius:4px;font-size:.87rem;margin:.5rem 0}
.verb{color:var(--mut);font-size:.83rem;font-style:italic}
nav{display:flex;gap:1.4rem;flex-wrap:wrap;padding:.7rem 0 .75rem;border-bottom:1px solid var(--line);
margin:0 0 1.6rem;font-size:.9rem}
nav a{text-decoration:none;font-weight:600}
nav a:hover{text-decoration:underline}
footer{margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.8rem}
code{background:var(--chip);padding:.06rem .3rem;border-radius:3px;font-size:.86em}
details{margin:.5rem 0}summary{cursor:pointer;color:var(--accent);font-size:.9rem}
ul{padding-left:1.15rem}li{margin:.18rem 0}
"""
def page(title, body, depth=0):
    up="../"*depth
    return (f'<meta charset="utf-8"><title>{e(title)}</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>'
            f'<div class="wrap"><nav><a href="{up}index.html">Evidence</a><a href="{up}faq.html">Frequently Asked Questions</a><a href="https://github.com/rohitium/animal-model-concordance">Repository</a></nav>'
            f'{body}<footer>{len(OK)} studies &middot; updated {BUILT} &middot; '
            f'every figure links to the study that reported it. Not peer reviewed.</footer></div>')

def vtag(v): return f'<span class="tag v-{e(v)}">{e(VERDICT_LABEL.get(v,v))}</span>'

# ---------------- evidence cells ----------------
def comparisons_for(pm, organism):
    """Figures attributable to this organism.

    Numeric figures quoted from other work are excluded: their conditions belong to the
    original study and counting them here would double-count.

    QUALITATIVE comparisons are kept. A paper that states "in dogs there is a remarkable
    improvement in the ERG" against "there was no change" in patients has made a real
    animal-to-human comparison; it simply reports no number. Dropping these silently
    deleted the clearest negative result about dog models in the corpus and flipped that
    row from mixed to favourable. They are marked and never enter the numeric score.
    """
    v=OK[pm]
    study_orgs=N.organisms(list(v["animal_side"].get("species") or [])
                           + list(v["animal_side"].get("grouped_labels") or []))
    prov=PROV.get(pm) or {}
    out=[]
    for i,c in enumerate(v.get("comparisons") or []):
        pv=(prov.get(str(i)) or {}) if "error" not in prov else {}
        c["_prov"]=pv.get("provenance","unclear")
        c["_qualitative"]=c.get("value") is None
        c["_cited_source"]=pv.get("cited_source")
        # A number this paper quotes from someone else is not this paper's evidence.
        # Re-analysis of others' data is: pooling published results is the reviewer's
        # own contribution.
        # Qualitative comparisons are kept: a review stating dogs recovered and patients
        # did not has made a real comparison. Dropping them removed the clearest negative
        # dog finding in the corpus.
        if c["_prov"]=="cited-from-other-study" and not c["_qualitative"]:
            continue
        cs=N.organisms(c.get("animal_species") or [])
        if cs:
            if organism in cs: out.append(c)
        elif len(study_orgs)==1 and study_orgs[0]==organism:
            out.append(c)
    return out
_STOP=set("the of a an in and or to for with between from that this is are was were on by "
          "vs versus percentage percent share proportion number rate average mean".split())
def _key(t):
    return frozenset(w for w in re.findall(r"[a-z]+", (t or "").lower())
                     if w not in _STOP and len(w)>2)

def source_label(loc):
    """A locator we can stand behind.

    Table and figure references are verifiable in the published paper and are kept
    verbatim. Page numbers are not: they were read off a PDF, so they may be PDF pages
    rather than journal pages, and "Results, p5" invites a reader to look somewhere we
    cannot vouch for. The section is kept; the page is dropped.
    """
    t=(loc or "").strip()
    if not t: return ""
    low=t.lower()
    if "table" in low or "fig" in low or "appendix" in low or "supplement" in low:
        return t
    t=re.sub(r",?\s*p+\.?\s*\d+[a-z]?", "", t, flags=re.I).strip(" ,;")
    return t

def _family(c):
    import importlib.util as _iu
    global _OV
    try: _OV
    except NameError:
        _sp=_iu.spec_from_file_location("_ov", os.path.join(os.path.dirname(__file__),
                                        "37_objective_verdict.py"))
        _OV=_iu.module_from_spec(_sp); _sp.loader.exec_module(_OV)
    return _OV.classify(c.get("statistic"), c.get("unit"), c.get("what_compared"))

def evidence_cell(pm_set, organism):
    """One cell.

    Figures are bucketed by statistic and unit. Where a paper scores many conditions with
    the same measure -- one model-robustness score per cancer type -- that is a
    distribution, and the cell shows its span, median and ends rather than splitting it up
    or naming it after one member. Ancillary statistics such as differences between
    correlations are steps in an analysis rather than measures of match, and are left to
    the study page.
    """
    buckets={}
    for pm in sorted(pm_set, key=lambda p:-(DB[p].get("cited_by") or 0)):
        for c in comparisons_for(pm, organism):
            if c.get("value") is None: continue
            if _family(c)=="bounded-difference": continue
            buckets.setdefault((c["statistic"].strip().lower(), c["unit"]), []).append((pm,c))
    if not buckets:
        return '<span class="sub">no numeric figure attributable to this organism</span>'
    parts=[]
    for (stat,unit),items in sorted(buckets.items(), key=lambda kv:-len(kv[1]))[:6]:
        vals=sorted(c["value"] for _,c in items)
        m=len(vals)//2
        med=vals[m] if len(vals)%2 else (vals[m-1]+vals[m])/2
        u="%" if unit=="percent" else ""
        rng=f"{vals[0]:g}–{vals[-1]:g}" if len(set(vals))>1 else f"{vals[0]:g}"
        studies=sorted({pm for pm,_ in items}, key=lambda p:-(DB[p].get("cited_by") or 0))
        cites=" · ".join(f'<a href="study/{p}.html">{e(cite(p))}</a>' for p in studies[:3])
        if len(studies)>3: cites+=f' +{len(studies)-3} more'
        _,c0=items[0]
        descs={c["what_compared"] for _,c in items}
        if len(descs)>1:
            lo=min(items,key=lambda t:t[1]["value"]); hi=max(items,key=lambda t:t[1]["value"])
            what=(f'{len(items)} comparisons, median {med:g}{u} — lowest '
                  f'{lo[1]["what_compared"]} ({lo[1]["value"]:g}{u}), highest '
                  f'{hi[1]["what_compared"]} ({hi[1]["value"]:g}{u})')
        else:
            what=c0["what_compared"]
        nc=re.sub(r"^\s*[\d,]+\s*","",(c0.get("n_counts") or "")).strip()
        n=f', n={c0["n"]:,} {e(nc)}'.rstrip() if c0.get("n") and len(descs)==1 else ""
        parts.append(f'<div class="ev"><span class="v">{e(rng)}{u}</span> {e(stat)}'
                     f'{n} <span class="src">— {e(what)} ({cites})</span></div>')
    cav=[OK[pm]["base_rate_caveat"] for pm in pm_set if OK[pm].get("base_rate_caveat")]
    if cav:
        parts.append(f'<div class="caveat"><strong>Caveat.</strong> {e(cav[0])}</div>')
    return "".join(parts)

DIRTAG={"evidence favours the model":"v-supports","mixed":"v-partly-supports",
        "evidence does not favour the model":"v-does-not-support",
        "too little evidence":"v-partly-supports"}
def evidence_synth(a, organism, pm_set):
    """A readable synthesis, with the raw figures kept beneath for checking. A list of
    extracted numbers is not a finding: a reader cannot tell from '3-70% proportion'
    which way the evidence points, or what varies across the range."""
    sy=SYN.get(f"{a}|{organism}")
    out=[]
    if sy and "error" not in sy:
        out.append(f'<p><span class="tag {DIRTAG.get(sy["direction"],"")}">{e(sy["direction"])}</span></p>')
        out.append(f'<p>{e(sy["summary"])}</p>')

        if sy.get("why_range_is_wide"):
            out.append(f'<p class="sub"><strong>What varies across the range:</strong> '
                       f'{e(sy["why_range_is_wide"])}</p>')
    out.append(f'<details><summary>Figures behind this row</summary>{evidence_cell(pm_set,organism)}</details>')
    return "".join(out)

# ---------------- landing page ----------------
# An organism earns a row only if some figure is attributable to it. Reviews often name
# every species they mention while reporting figures for a few; rows reading "no figure
# attributable to this organism" are noise. Those namings are listed as a note instead.
rows=collections.defaultdict(set)
named_only=collections.defaultdict(set)
for pm in CORE:
    for o in orgs_of(pm):
        if comparisons_for(pm,o):
            rows[(arm(pm),o)].add(pm)
        else:
            named_only[o].add(pm)
verd=collections.Counter(v["verdict"] for v in OK.values())
ncomp=sum(len(v.get("comparisons") or []) for v in OK.values())
# what actually survives to become evidence in a row
_own=0; _cited=0
for _pm,_v in OK.items():
    _pr=PROV.get(_pm) or {}
    for _i,_c in enumerate(_v.get("comparisons") or []):
        _p=((_pr.get(str(_i)) or {}) if "error" not in _pr else {}).get("provenance")
        if _p=="cited-from-other-study": _cited+=1
        else: _own+=1
_in_rows=sum(len(comparisons_for(pm,o)) for (a,o),pms in rows.items() for pm in pms)
_studies_in_rows=len({pm for pms in rows.values() for pm in pms})
_scored=len([1 for k_ in OK if (OBJ.get(k_) or {}).get("verdict") not in (None,"insufficient-data")])

b=[f"<h1>How well do animal models predict human clinical outcomes?</h1>",
 '<p class="lede">A structured reading of the published literature that <em>measures</em> '
 'animal-to-human correspondence. Each study was read from its full text and asked the same '
 'questions; figures below are those the studies reported, in their own units. Nothing is '
 'averaged across studies, because studies define concordance differently.</p>',
 '<div class="grid">',
 f'<div class="stat"><div class="n">{len(OK)}</div><div class="l">studies included</div></div>',
 f'<div class="stat"><div class="n">{_studies_in_rows}</div><div class="l">with organism-specific evidence</div></div>',
 f'<div class="stat"><div class="n">{_in_rows:,}</div><div class="l">figures in the table</div></div>',
 f'<div class="stat"><div class="n">{len({o for _,o in rows})}</div><div class="l">model organisms</div></div>',
 f'<div class="stat"><div class="n">{len(rows)}</div><div class="l">evidence rows</div></div>',
 f'<div class="stat"><div class="n">{_scored}</div><div class="l">with a numeric score</div></div>',
'</div>',
 f'<p class="sub">{ncomp:,} figures were extracted from these studies. {_cited:,} are quoted from earlier work and do not count as the quoting study&rsquo;s evidence; {_in_rows:,} of the rest are attributable to a specific model organism and appear below. {_scored} studies report something reducible to a common 0&ndash;1 concordance scale.</p>',
 "<h2>Evidence by assessment and model organism</h2>",
 '<p class="sub">One row per assessment and organism. Values are ranges only where several '
 'studies reported the <em>same</em> statistic; different statistics are listed separately. '
 'Grouped labels such as “rodent” are kept as reported and never expanded into member species.</p>',
 '<div class="scroll"><table><tr><th>Assessment</th><th>Model organism</th><th>Evidence</th></tr>']
for a in ASSESS_ORDER+[x for x in {k[0] for k in rows} if x not in ASSESS_ORDER]:
    orgs=sorted([o for aa,o in rows if aa==a], key=lambda o:(-len(rows[(a,o)]), o))
    for i,o in enumerate(orgs):
        pms=rows[(a,o)]
        vs=collections.Counter(OK[p]["verdict"] for p in pms)
        vtags="".join(vtag(k)+f"<span class='sub'>{v}</span> " for k,v in vs.most_common())
        b.append(f'<tr><td class="assess">{e(ASSESS_LABEL.get(a,a)) if i==0 else ""}</td>'
                 f'<td class="org">{e(o)}<br><span class="sub">{len(pms)} {"study" if len(pms)==1 else "studies"}</span>'
                 f'<br>{vtags}</td><td>{evidence_synth(a,o,pms)}</td></tr>')
b.append("</table></div>")
extra={o:s_ for o,s_ in named_only.items() if not any(o==oo for _,oo in rows)}
if extra:
    b.append('<p class="sub">Organisms named by a study but with no figure attributable to '
             'them, so not given a row: '
             + ", ".join(f'{e(o)} ({len(s_)})' for o,s_ in sorted(extra.items())) + ".</p>")

b+=["<h2>Studies</h2>",'<div class="scroll"><table>'
    "<tr><th>Study</th><th>Assessment</th><th>Organisms</th><th>Verdict</th><th>Cited by</th></tr>"]
for pm in sorted(OK, key=lambda p:-(DB[p].get("cited_by") or 0)):
    b.append(f'<tr><td><a href="study/{pm}.html">{e(cite(pm))}</a><br>'
             f'<span class="sub">{e(DB[pm].get("title"))}</span></td>'
             f'<td>{e(ASSESS_LABEL.get(arm(pm),arm(pm)))}</td>'
             f'<td>{", ".join(e(o) for o in orgs_of(pm))}</td>'
             f'<td>{vtag(OK[pm]["verdict"])}</td><td>{e(DB[pm].get("cited_by"))}</td></tr>')
b.append("</table></div>")

def _kappa(pairs):
    n=len(pairs)
    if not n: return 0,0
    po=sum(1 for x,y in pairs if x==y)/n
    ca=collections.Counter(x for x,_ in pairs); cb=collections.Counter(y for _,y in pairs)
    pe=sum((ca[c]/n)*(cb[c]/n) for c in {c for p in pairs for c in p})
    return po,(po-pe)/(1-pe) if pe<1 else 0.0
_scored={k_:v_ for k_,v_ in OBJ.items() if v_.get("verdict")!="insufficient-data" and k_ in OK}
_p1=[(OBJ[k_]["verdict"],OK[k_]["verdict"]) for k_ in _scored]
_p2=[(OBJ[k_]["verdict"],RATER2[k_]["verdict"]) for k_ in _scored if k_ in RATER2 and "error" not in RATER2[k_]]
_pr=[(OK[k_]["verdict"],RATER2[k_]["verdict"]) for k_ in OK if k_ in RATER2 and "error" not in RATER2[k_]]
_a1,_k1=_kappa(_p1); _a2,_k2=_kappa(_p2); _ar,_kr=_kappa(_pr)
b+=["<h2>How the verdicts are decided, and how far they agree</h2>",
 '<p>Every figure carrying concordance information is put on a 0&ndash;1 scale where 1 means the '
 'animal result tracked the human result; figures pointing the other way are inverted, so a 92% '
 'failure rate becomes 0.08. A study&rsquo;s score is the median of its figures, with cut-offs at '
 '<strong>&ge;0.70 supports</strong>, <strong>0.40&ndash;0.70 partly supports</strong>, '
 '<strong>&lt;0.40 does not support</strong>. Two model raters judged the same PDFs independently.</p>',
 f'<p><strong>{len(_scored)} of {len(OK)}</strong> studies report something reducible to that '
 'scale. The rest report p-values, slopes, distances and odds ratios &mdash; real results that are '
 'not rates of agreement, which is much of why concordance is hard to compare across papers.</p>',
 '<div class="scroll"><table><tr><th>Comparison</th><th>Agreement</th><th>Cohen&rsquo;s &kappa;</th></tr>'
 f'<tr><td>model rater 1 vs model rater 2</td><td>{_ar:.0%}</td><td>{_kr:.2f}</td></tr>'
 f'<tr><td>numeric rule vs rater 1</td><td>{_a1:.0%}</td><td>{_k1:.2f}</td></tr>'
 f'<tr><td>numeric rule vs rater 2</td><td>{_a2:.0%}</td><td>{_k2:.2f}</td></tr></table></div>',
 '<p>The raters agree moderately with each other and poorly with the rule, so the labels are '
 'contested and the numbers beneath them are what to rely on. Each study page shows all three '
 'verdicts; disagreement is displayed, not resolved. '
 '<a href="faq.html">Why, and what each gets wrong</a>.</p>']
if False:
    b+=["<h2>unused</h2>",
     f'<p>Every study was independently re-judged by a second rater — a different model family, '
     f'the same PDFs, the same rubric. The two agree on <strong>{AG["agree"]:.0%}</strong> of '
     f'{AG["n"]} studies (Cohen&rsquo;s &kappa; = <strong>{AG["kappa"]:.2f}</strong>, moderate). '
     f'Nearly all disagreements are one step apart, and the second rater is systematically more '
     f'generous. Read a verdict as indicative and the numbers beneath it as the evidence; '
     f'studies where the raters disagreed are marked on their pages. '
     f'<a href="faq.html">More in the FAQ</a>.</p>']

b+=["<h2>Method</h2>",
 "<p>Studies were found with a multi-strand PubMed search and citation chasing; neither "
 "alone was sufficient, and together they recovered every paper in a 29-study verified "
 "anchor set. A study is included only if it reports a quantitative comparison in which one "
 "side is a result in a live non-human animal and the other a human clinical result. Papers "
 "arguing that animals do or do not predict human outcomes, without measuring it, are "
 "excluded, as are in vitro and in silico predictors.</p>",
 "<p>Each included study was read from its full-text PDF and asked the same questions: which "
 "animals against which humans, whether the endpoints are identical or merely analogous, "
 "every animal-to-human figure with its unit as printed and its table or figure location, "
 "and whether the data support concordance. Verdicts are judged from results, tables and "
 "figures, not from how the authors characterise their findings.</p>",
 f"<p>No estimate is pooled across studies. {verd['supports']} studies support concordance, "
 f"{verd['partly-supports']} partly support it and {verd['does-not-support']} do not — a "
 "tally of studies, not a measure of how well animal models work. Screening and extraction "
 "were model-assisted and have not been verified by a second reader.</p>",
 f'<details><summary>{len(EXCL)} screened studies were excluded</summary><div class="scroll">'
 "<table><tr><th>Study</th><th>Reason</th></tr>"
 + "".join(f'<tr><td>{e(cite(pm))}<br><span class="sub">{e(v.get("title"))}</span></td>'
           f'<td class="sub">{e(v.get("exclusion_reason_display") or v.get("exclusion_reason"))}</td></tr>'
           for pm,v in sorted(EXCL.items(), key=lambda kv:-(kv[1].get("cited_by") or 0)))
 + "</table></div></details>"]
open(os.path.join(OUT,"index.html"),"w").write(page("Animal Model Concordance","".join(b)))

# ---------------- study pages ----------------
for pm,v in OK.items():
    d=DB[pm]; md=META.get(pm,{}); a=v["animal_side"]; h=v["human_side"]
    ident=[f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pm}/">PMID {pm}</a>']
    if md.get("doi"): ident.append(f'<a href="https://doi.org/{e(md["doi"])}">doi:{e(md["doi"])}</a>')
    if md.get("pmcid"): ident.append(f'<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/{e(md["pmcid"])}/">{e(md["pmcid"])}</a>')
    body=[f'<h1>{e(d.get("title"))}</h1>',
      f'<p class="sub">{e(", ".join(md.get("authors_full") or d.get("authors") or []))}<br>'
      f'<em>{e(md.get("journal_full") or d.get("journal"))}</em> · {e(d.get("year"))} · '
      f'cited by {e(d.get("cited_by"))} · {" · ".join(ident)}</p>',
      f'<p>{vtag(v["verdict"])}<span class="sub"> model rater 1</span>'
      + (f' {vtag(RATER2[pm]["verdict"])}<span class="sub"> model rater 2</span>'
         if pm in RATER2 and "error" not in RATER2[pm] else "")
      + ((lambda o: f' {vtag(o["verdict"])}<span class="sub"> numeric rule'
                    f' (median {o["median"]:.2f} of {o["n_usable"]} figures)</span>'
                    if o.get("median") is not None else
                    ' <span class="tag">numeric rule: no figure on a concordance scale</span>')
         (OBJ[pm]) if pm in OBJ else "")
      + f'<span class="tag">{e(ASSESS_LABEL.get(arm(pm),arm(pm)))}</span>'
      + "".join(f'<span class="tag">{e(o)}</span>' for o in orgs_of(pm)) + "</p>",
      f'<div class="card"><strong>Verdict basis</strong><br>{e(v["verdict_basis"])}</div>']
    if v.get("base_rate_caveat"):
        body.append(f'<div class="caveat"><strong>Caveat.</strong> {e(v["base_rate_caveat"])}</div>')
    def side(t, pairs):
        ps=[f"<strong>{e(k)}</strong> {e(x)}" for k,x in pairs if x]
        return f'<div class="card"><strong>{t}</strong><br>' + " · ".join(ps) + "</div>" if ps else ""
    body.append(side("Animal side",[("species", ", ".join(orgs_of(pm))),
        ("strain/model",a.get("strain_or_model")),("disease arose",a.get("how_disease_arose")),
        ("n", f'{a["n"]} {a.get("n_counts") or ""}'.strip() if a.get("n") else None),
        ("endpoint", v.get("animal_endpoint"))]))
    body.append(side("Human side",[("population",h.get("population")),("disease",h.get("disease")),
        ("setting",h.get("stage_or_setting")),("phase",h.get("trial_phase")),
        ("n", f'{h["n"]} {h.get("n_counts") or ""}'.strip() if h.get("n") else None),
        ("endpoint", v.get("human_endpoint"))]))
    body.append(f'<p><span class="tag">endpoints {e(v.get("endpoint_match"))}</span>'
                f'<span class="tag">discordance: {e(v.get("discordance_direction"))}</span>'
                + (f'<span class="tag">{e(v.get("scope"))}</span>' if v.get("scope") else "") + "</p>")
    if v.get("discordance_note"):
        body.append(f'<p class="sub">{e(v["discordance_note"])}</p>')
    _pv=PROV.get(pm) or {}
    allc=list(v.get("comparisons") or [])
    for _i,_c in enumerate(allc):
        _p=(_pv.get(str(_i)) or {}) if "error" not in _pv else {}
        _c["_prov"]=_p.get("provenance","unclear"); _c["_cited_source"]=_p.get("cited_source")
    for _c in allc: _c["_qual"]=_c.get("value") is None
    cited=[c for c in allc if c["_prov"]=="cited-from-other-study" and not c["_qual"]]
    quals=[c for c in allc if c["_qual"]]
    cs=[c for c in allc if not c["_qual"] and c["_prov"]!="cited-from-other-study"]
    if cs:
        body.append(f'<h2>Reported comparisons <span class="tag">{len(cs)}</span></h2>')
        body.append('<div class="scroll"><table><tr><th>Value</th><th>Statistic</th>'
                    "<th>What was compared</th><th>Organism</th><th>n</th><th>Source</th></tr>")
        for c in cs:
            _nc=re.sub(r"^\s*[\d,]+\s*","",(c.get("n_counts") or "")).strip()
            n=f'{c["n"]:,} {e(_nc)}'.strip() if c.get("n") else "—"
            body.append(f'<tr><td class="ev"><span class="v">{e(fmt(c))}</span></td>'
                        f'<td>{e(c["statistic"])}</td>'
                        f'<td>{e(c["what_compared"])}<br><span class="verb">“{e(c["verbatim"])}”</span></td>'
                        f'<td>{", ".join(e(x) for x in N.organisms(c.get("animal_species") or [])) or "—"}</td>'
                        f'<td>{n}</td><td class="sub">{e(c.get("source_location"))}</td></tr>')
        body.append("</table></div>")
    if quals:
        body.append(f'<h2>Comparisons stated without a number '
                    f'<span class="tag">{len(quals)}</span></h2>')
        body.append('<p class="sub">The paper compares animal and human results here in words '
                    'rather than figures. These count as evidence and are shown in full, but they '
                    'cannot enter a numeric score.</p>')
        for c in quals:
            loc=source_label(c.get("source_location"))
            body.append(f'<div class="quote"><span class="t">{e(c["what_compared"])}'
                        + (f' &middot; {e(loc)}' if loc else "") + '</span>'
                        + f'&ldquo;{e(c.get("verbatim") or "")}&rdquo;</div>')
    if cited:
        body.append(f'<h2>Figures this paper quotes from other work '
                    f'<span class="tag">{len(cited)}</span></h2>')
        body.append('<p class="sub">Reported here for context. They are not this study&rsquo;s '
                    'evidence and do not contribute to its verdict or to any row of the main '
                    'table; the conditions that produced them belong to the original work.</p>')
        body.append("<div class='scroll'><table><tr><th>Value</th><th>Statistic</th>"
                    "<th>What was compared</th><th>Credited to</th><th>Source</th></tr>")
        for c in cited:
            body.append(f'<tr><td class="ev"><span class="v">{e(fmt(c))}</span></td>'
                        f'<td>{e(c["statistic"])}</td><td>{e(c["what_compared"])}</td>'
                        f'<td>{e(c.get("_cited_source") or "not named")}</td>'
                        f'<td class="sub">{e(source_label(c.get("source_location")))}</td></tr>')
        body.append("</table></div>")
    if md.get("abstract"):
        body.append(f'<details><summary>Abstract</summary><div class="card">{e(md["abstract"])}</div></details>')
    if md.get("mesh"):
        body.append('<details><summary>MeSH terms</summary><p>'
                    + "".join(f'<span class="tag">{e(t["term"])}</span>' for t in md["mesh"]) + "</p></details>")
    fs=FTS.get(pm,{})
    body.append('<details><summary>Provenance</summary><div class="scroll"><table>'
      f'<tr><th>Assessment</th><td>{e(ASSESS_LABEL.get(arm(pm),arm(pm)))}</td></tr>'
      f'<tr><th>Read from</th><td>full-text PDF</td></tr>'
      f'<tr><th>Source</th><td>{e(fs.get("route") or "—")}</td></tr>'
      f'<tr><th>Publication types</th><td>{e(", ".join(md.get("publication_types") or []))}</td></tr>'
      f'<tr><th>Funding</th><td>{e(", ".join(md.get("grants") or []) or "none listed")}</td></tr>'
      "</table></div></details>")
    open(os.path.join(OUT,"study",f"{pm}.html"),"w").write(page(d.get("title","Study")[:70],"".join(body),depth=1))
    json.dump({**d,"assessment":arm(pm),"organisms":orgs_of(pm),"answers":v,"metadata":md},
              open(os.path.join(OUT,"api","study",f"{pm}.json"),"w"),indent=1)

import faq as _faq
_ctx={"n_studies":len(OK),"n_scored":len(_scored),"n_unscored":len(OK)-len(_scored),
      "r1r2_a":_ar,"r1r2_k":_kr,"rule_r1_a":_a1,"rule_r1_k":_k1,
      "rule_r2_a":_a2,"rule_r2_k":_k2,
      "supports":verd["supports"],"partly":verd["partly-supports"],"not":verd["does-not-support"],
      "cited":_cited,"n_figures":ncomp,"in_rows":_studies_in_rows,
      "pct_cited":(100.0*sum(1 for _p,_v in PROV.items() if "error" not in _v
                             for _it in _v.values() if _it.get("provenance")=="cited-from-other-study")
                   /max(1,sum(len(_v) for _p,_v in PROV.items() if "error" not in _v)))}
fb=["<h1>Frequently Asked Questions</h1>"]
for q,paras in _faq.build(_ctx):
    fb.append(f"<h2>{q}</h2>"); fb.extend(paras)
fb.append('<p class="sub">The protocol, search strings, every analysis script and a running list '
          'of limitations are in the '
          '<a href="https://github.com/rohitium/animal-model-concordance">repository</a>.</p>')
open(os.path.join(OUT,"faq.html"),"w").write(page("FAQ","".join(fb)))

json.dump({"updated":BUILT,"studies":len(OK),"comparisons":ncomp,
  "verdicts":dict(verd),"organisms":sorted({o for _,o in rows}),
  "assessments":sorted({a for a,_ in rows})},
  open(os.path.join(OUT,"api","summary.json"),"w"),indent=1)
json.dump({pm:{**DB[pm],"assessment":arm(pm),"organisms":orgs_of(pm),"answers":OK[pm]} for pm in OK},
  open(os.path.join(OUT,"api","bulk.json"),"w"),indent=1)
open(os.path.join(OUT,".nojekyll"),"w").write("")
for old in ("findings.html","studies.html","species.html","areas.html","arms.html",
            "methods.html","excluded.html","coverage.html","gaps.html"):
    p=os.path.join(OUT,old)
    if os.path.exists(p): os.remove(p)
print(f"built: landing page + {len(OK)} study pages | {len(rows)} table rows | {ncomp} comparisons")
