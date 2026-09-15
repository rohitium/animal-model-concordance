"""Build the v0.4 site from the frozen v0.4 outputs (no network, no model calls).

Writes to site/v04_build/ so the live v0.3 build under site/_build/ is left alone until the
replacement has been reviewed.

Pages
  index.html     what the review looked for, what it found, and what it cannot say
  evidence.html  the evidence map (disease area x species column x level) and every final result
  pairs.html     dog and cat drug pairs: the strata table and every classified pair
  q4.html        companion animals vs laboratory models within the same drug, with its caveats
  methods.html   protocol, retrieval and recall, quality checks, limitations
  study/<pmid>.html   one page per study with its final results, quotes and page numbers
  api/*.json     the same content as data

Statistics are never recomputed here: the strata, Q4 and recall numbers are the ones already
computed by d3/d4/d5/r3 and are embedded from their reports verbatim. Part 1 counts are derived
from final_results.json, which is the output of the adjudicated pipeline.
"""
import sys, os, re, json, html, collections, statistics
sys.path.insert(0, os.path.dirname(__file__))
from common import load, species_column, today, J, V04
from t1_part1_outputs import HOW  # the spot-check instructions, shared with spotcheck.md

OUT = J("site", "v04_build")
e = lambda s: html.escape(str(s if s is not None else ""))
LEVELS = [("A-outcome-concordance", "A — intervention outcomes"),
          ("B-toxicity-safety-concordance", "B — toxicity and safety"),
          ("C-biological-similarity", "C — disease biology")]
DIRS = [("animal-corresponded", "animal corresponded"), ("animal-did-not-correspond", "animal did not correspond"),
        ("mixed", "mixed"), ("not-applicable", "not applicable")]

CSS = """
:root{--ink:#1a1c1e;--dim:#5b6167;--line:#dfe3e7;--bg:#fbfbfa;--card:#fff;--accent:#1d4e6f;
--good:#2f6b4f;--bad:#8c3a2b;--mix:#8a6d1f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
header{background:var(--card);border-bottom:1px solid var(--line)}
header .in{max-width:1080px;margin:0 auto;padding:18px 20px;display:flex;flex-wrap:wrap;gap:14px;align-items:baseline}
header a.brand{font-weight:700;color:var(--ink);text-decoration:none;font-size:18px}
nav a{color:var(--accent);text-decoration:none;margin-right:14px;font-size:15px}
nav a:hover{text-decoration:underline}
main{max-width:1080px;margin:0 auto;padding:26px 20px 70px}
h1{font-size:30px;line-height:1.2;margin:.2em 0 .35em}
h2{font-size:22px;margin:1.9em 0 .5em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
h3{font-size:17px;margin:1.5em 0 .4em}
p,li{max-width:74ch}
.lede{font-size:18px;color:var(--dim)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:18px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .n{font-size:28px;font-weight:700;font-variant-numeric:tabular-nums}
.card .l{color:var(--dim);font-size:14px}
table{border-collapse:collapse;width:100%;margin:14px 0;background:var(--card);font-size:14px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:#f2f5f7;font-weight:600;position:sticky;top:0}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:12px;border:1px solid var(--line)}
.corresponded{color:var(--good);border-color:#bcd8c8}.did-not{color:var(--bad);border-color:#e4c3ba}
.mixedt{color:var(--mix);border-color:#e6d9a8}
blockquote{margin:.5em 0;padding:.4em 0 .4em .9em;border-left:3px solid var(--line);color:var(--dim);font-size:14px}
.note{background:#fff8e8;border:1px solid #e8dcb8;border-radius:8px;padding:12px 15px;margin:18px 0}
.small{font-size:14px;color:var(--dim)}
footer{border-top:1px solid var(--line);margin-top:40px;padding:18px 20px;color:var(--dim);font-size:13px}
a{color:var(--accent)}
code{background:#f0f2f4;padding:1px 5px;border-radius:4px;font-size:13px}
"""

NAV = [("index.html", "Overview"), ("evidence.html", "Evidence map"), ("pairs.html", "Dog &amp; cat drug pairs"),
       ("q4.html", "Companion vs laboratory"), ("methods.html", "Methods &amp; limitations"),
       ("spotcheck.html", "Spot-check")]


def page(fname, title, body, depth=0):
    up = "../" * depth
    nav = " ".join(f'<a href="{up}{h}">{t}</a>' for h, t in NAV)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>
<header><div class="in"><a class="brand" href="{up}index.html">Animal-model concordance</a>
<nav>{nav}</nav></div></header><main>{body}</main>
<footer>Built {today()} from the v0.4 pipeline outputs. Protocol v0.4, frozen before data collection.
Every number on this site is reproducible from the committed data and scripts.</footer></body></html>"""
    p = os.path.join(OUT, fname)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(doc)


def md(path):
    """Render a pipeline report file."""
    return mdsrc(open(path).read() if os.path.exists(path) else "")


def mdsrc(src):
    """Render the subset of markdown used by the pipeline reports."""
    out, rows, inlist = [], [], False
    def flush_table():
        nonlocal rows
        if not rows:
            return
        head, body = rows[0], [r for r in rows[1:] if not set(r) <= set("-| :")]
        cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
        out.append("<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells(head)) + "</tr>")
        for r in body:
            out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>")
        out.append("</table>")
        rows = []
    def inline(t):
        t = e(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        return t
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
            out.append(f"<h{min(n+1,4)}>{inline(s.lstrip('# '))}</h{min(n+1,4)}>")
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
    cls = {"animal-corresponded": "corresponded", "animal-did-not-correspond": "did-not", "mixed": "mixedt"}.get(d, "")
    return f'<span class="tag {cls}">{e(d or "—")}</span>'


def cards(pairs):
    return '<div class="grid">' + "".join(
        f'<div class="card"><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in pairs) + "</div>"


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

    # ---------- index ----------
    b = [f"<h1>What the published literature actually reports about animal-to-human concordance</h1>",
         '<p class="lede">A systematic review of studies that compare a finding in live non-human animals with '
         'the corresponding finding in humans. It reports what those studies found, one result at a time, '
         'with the quote and page each number came from.</p>',
         cards([(f"{len(fin):,}", "results kept after checking"), (f"{n_stud}", "studies"),
                (f"{by_level['A-outcome-concordance']}", "level A: intervention outcomes"),
                (f"{by_level['B-toxicity-safety-concordance']}", "level B: toxicity and safety"),
                (f"{by_level['C-biological-similarity']}", "level C: disease biology")]),
         "<h2>The short answer</h2>",
         "<p>Across every result we kept, animal findings matched the human finding "
         f"<strong>{by_dir['animal-corresponded']}</strong> times, failed to match "
         f"<strong>{by_dir['animal-did-not-correspond']}</strong> times, and were mixed "
         f"<strong>{by_dir['mixed']}</strong> times. That ratio is <em>not</em> a concordance rate, and we do not "
         "report it as one — see the caution below.</p>",
         "<table><tr><th>Evidence level</th><th class='num'>studies</th><th class='num'>results</th>"
         "<th class='num'>corresponded</th><th class='num'>did not</th><th class='num'>mixed</th></tr>"]
    for key, label in LEVELS:
        rs = [r for r in fin if r["level"] == key]
        c = lvl_dir[key]
        b.append(f"<tr><td>{label}</td><td class='num'>{len({r['pmid'] for r in rs})}</td>"
                 f"<td class='num'>{len(rs)}</td><td class='num'>{c['animal-corresponded']}</td>"
                 f"<td class='num'>{c['animal-did-not-correspond']}</td><td class='num'>{c['mixed']}</td></tr>")
    b.append("</table>")
    b += ['<div class="note"><strong>Why there is no single headline percentage.</strong> These studies do not '
          'measure the same thing. They report concordance rates, sensitivities, correlation coefficients, '
          'gene-overlap counts and qualitative "similar to humans" claims, in different diseases and species. '
          'Pooling them would produce a number with no referent. The literature is also selective about what gets '
          'published and about which comparisons get made at all, so the balance of corresponded / did-not-correspond '
          'above reflects what authors chose to report, not a rate of anything. Values are therefore grouped only '
          'where the metric and unit match, and spreads are shown rather than an average.</div>',
          "<h2>Where the evidence is, and where it is not</h2>",
          f'<p>The <a href="evidence.html">evidence map</a> cuts the {len(fin):,} results by disease area and by '
          'species, keeping companion dogs and cats (client-owned animals with naturally occurring disease) '
          'separate from laboratory dogs and cats. Most cells are thin: the concentration is in oncology, '
          'neurology and immunology, and much of the evidence is level C (disease biology) rather than level A '
          '(what happened when the disease was treated).</p>',
          "<h2>The two purpose-built analyses</h2>",
          '<p><strong><a href="pairs.html">Dog and cat drug pairs.</a></strong> For agents used in both companion '
          'animals and people, we asked whether the veterinary result and the human result point the same way. '
          'Among 586 primary pairs, 185 were classifiable: <strong>82% concordant (95% CI 76–87%)</strong>. '
          'Most of those drugs were already approved in humans before the veterinary evidence existed, which '
          'limits what the agreement can be read as evidence for.</p>',
          '<p><strong><a href="q4.html">Companion animals vs laboratory models.</a></strong> For 108 drug and '
          'condition pairs where all three sides were determinate, companion animals matched the human outcome in '
          '83% and laboratory models in 93%. Stated plainly: in this set laboratory models agreed more often. '
          'A stricter sensitivity analysis found no detectable difference, and neither result can tell you which '
          'kind of model <em>predicts</em> human outcomes — that page explains why.</p>',
          "<h2>How much of the literature this covers</h2>",
          '<p>Capture–recapture on the two independent search mechanisms estimates that the search reached about '
          '<strong>33% of the reachable eligible literature (95% CI 26–46%)</strong>, and that is an upper bound. '
          'This is a large sample of the field, not a census of it. '
          'The <a href="methods.html">methods and limitations</a> page states the rest of what could be wrong, '
          'including that half of the final results were adjudicated by hand and were not independently checked.</p>',
          '<div class="note"><strong>Check us.</strong> Because that hand adjudication was not independent, the '
          '<a href="spotcheck.html">spot-check page</a> lays out a fixed, seeded sample of results with the link '
          'and the page number for each one, and what to look for. Forty items, about five minutes each. If it '
          'turns up a class of result we got wrong, we would rather hear it than not.</div>']
    page("index.html", "Animal-model concordance: what the literature reports", "\n".join(b))

    # ---------- evidence map ----------
    grid = collections.defaultdict(lambda: {"s": set(), "n": 0, "d": collections.Counter()})
    for r in fin:
        g = grid[(r.get("disease_area") or "unassigned", species_column(r["species"], r.get("model_type")))]
        g["s"].add(r["pmid"]); g["n"] += 1; g["d"][r["direction"]] += 1
    areas = sorted({k[0] for k in grid}); cols = sorted({k[1] for k in grid})
    b = ["<h1>Evidence map</h1>",
         '<p class="lede">Disease area by species. Each cell shows the highest evidence level present '
         '(A intervention outcomes &gt; B toxicity/safety &gt; C disease biology) and the number of distinct '
         'studies with a kept result.</p>',
         '<p class="small">Companion dog/cat = client-owned animals with naturally occurring disease. '
         '<code>grouped-label</code> = the paper reported several species together and the result could not be '
         'resolved to one. <code>human</code> = a species label the extractor got wrong and neither adjudication '
         'pass corrected; treat those cells as unassigned, not as a finding.</p>',
         "<table><tr><th>disease area</th>" + "".join(f"<th>{e(c)}</th>" for c in cols) + "</tr>"]
    lvl_rank = {"A-outcome-concordance": "A", "B-toxicity-safety-concordance": "B", "C-biological-similarity": "C"}
    cell_lvl = collections.defaultdict(set)
    for r in fin:
        cell_lvl[(r.get("disease_area") or "unassigned", species_column(r["species"], r.get("model_type")))].add(
            lvl_rank.get(r["level"], "?"))
    for a in areas:
        cells = []
        for c in cols:
            g = grid.get((a, c))
            cells.append(f"{min(cell_lvl[(a, c)])}·{len(g['s'])}" if g else "")
        b.append(f"<tr><td>{e(a)}</td>" + "".join(f"<td class='num'>{x}</td>" for x in cells) + "</tr>")
    b.append("</table>")

    b.append("<h2>Every kept result</h2>")
    b.append('<p class="small">Grouped by study, newest first. Each row links to the study page, which carries the '
             'quote and the PDF page for every result.</p>')
    b.append("<table><tr><th>study</th><th class='num'>year</th><th>design</th><th class='num'>results</th>"
             "<th>levels</th><th>direction of its results</th></tr>")
    for pm, rs in sorted(studies.items(), key=lambda kv: -(kv[1][0].get("year") or 0)):
        dc = collections.Counter(r["direction"] for r in rs)
        lv = "".join(sorted({lvl_rank.get(r["level"], "?") for r in rs}))
        dirs = " ".join(f"{dirtag(d)}&nbsp;{n}" for d, n in dc.most_common())
        b.append(f"<tr><td><a href='study/{e(pm)}.html'>{e((rs[0].get('title') or pm)[:110])}</a></td>"
                 f"<td class='num'>{e(rs[0].get('year'))}</td><td>{e(rs[0].get('design'))}</td>"
                 f"<td class='num'>{len(rs)}</td><td>{lv}</td><td>{dirs}</td></tr>")
    b.append("</table>")
    page("evidence.html", "Evidence map", "\n".join(b))

    # ---------- study pages ----------
    for pm, rs in studies.items():
        r0 = rs[0]
        sb = [f"<h1>{e(r0.get('title') or pm)}</h1>",
              f'<p class="small">PMID/record {e(pm)} · {e(r0.get("year"))} · {e(r0.get("design"))} · '
              f'peer reviewed: {e(r0.get("peer_reviewed"))} · '
              f'<a href="https://pubmed.ncbi.nlm.nih.gov/{e(pm)}/">PubMed</a></p>',
              f"<p>{len(rs)} kept result(s). Each was extracted from the full text, checked against the located "
              "page, and adjudicated against the review's definition of an animal-vs-human correspondence result.</p>"]
        for r in rs:
            sb += [f"<h3>{e(r['statement'])}</h3>",
                   f"<p class='small'>{dirtag(r['direction'])} · level {e(r['level'])} · species "
                   f"{e(species_column(r['species'], r.get('model_type')))} · "
                   f"{e(r.get('disease_area'))}" +
                   (f" · value <strong>{e(r.get('value'))} {e(r.get('unit'))}</strong>" if r.get("value") is not None else "") +
                   (f" · n {e(r.get('numerator'))}/{e(r.get('denominator'))}" if r.get("denominator") else "") + "</p>",
                   f"<blockquote>“{e(r.get('quote'))}”<br><span class='small'>PDF page {e(r.get('pdf_page'))}</span></blockquote>"]
        sb.append('<p class="small">Full texts are copyrighted and are not republished here; the quote is the '
                  'evidence for the extracted value and the page number lets you check it in the original.</p>')
        page(f"study/{pm}.html", (r0.get("title") or pm)[:80], "\n".join(sb), depth=1)

    # ---------- pairs ----------
    pairs = load("part2/pairs.json")
    attrs = load("part2/pair_attributes.json")
    classified = {k: v for k, v in pairs.items()
                  if (v.get("judgement") or {}).get("pair") in ("concordant", "discordant", "mixed", "indeterminate")}
    b = ["<h1>Dog and cat drug pairs</h1>",
         '<p class="lede">For agents used both in companion animals with naturally occurring disease and in people: '
         'does the veterinary evidence point the same way as the human evidence?</p>',
         md(os.path.join(V04, "part2", "summary_v2.md")),
         '<div class="note"><strong>How to read this.</strong> Concordance is concordant / (concordant + discordant). '
         'Mixed and indeterminate pairs are counted in the table and never dropped. “Discordant” is used only where '
         'all the available evidence points the opposite way. Most pairs are drugs already approved in humans before '
         'the veterinary evidence appeared, so the agreement mostly shows that veterinary medicine adopts drugs that '
         'already work, not that the animal evidence predicted the human result.</div>',
         f"<h2>Every classified pair ({len(classified)})</h2>",
         "<table><tr><th>agent</th><th>species</th><th>veterinary indication</th><th>verdict</th>"
         "<th>veterinary</th><th>human</th><th>type</th><th>timing</th></tr>"]
    order = {"concordant": 0, "discordant": 1, "mixed": 2, "indeterminate": 3}
    for k, v in sorted(classified.items(), key=lambda kv: (order[(kv[1]["judgement"])["pair"]], kv[0])):
        j, a = v["judgement"], attrs.get(k, {})
        sp = v.get("species")
        sp = ", ".join(sp) if isinstance(sp, list) else str(sp or "")
        tag = {"concordant": "corresponded", "discordant": "did-not", "mixed": "mixedt"}.get(j["pair"], "")
        b.append(f"<tr><td>{e(v.get('ingredient'))}</td><td>{e(sp)}</td><td>{e(v.get('veterinary_indication'))}</td>"
                 f"<td><span class='tag {tag}'>{e(j['pair'])}</span></td><td>{e(j.get('veterinary'))}</td>"
                 f"<td>{e(j.get('human'))}</td><td>{e(a.get('type'))}</td><td>{e(a.get('timing'))}</td></tr>")
    b.append("</table>")
    page("pairs.html", "Dog and cat drug pairs", "\n".join(b))

    # ---------- q4 ----------
    b = ["<h1>Companion animals vs laboratory models, within the same drug</h1>",
         '<p class="lede">For the same agent and condition, did the companion-animal evidence and the '
         'laboratory-model evidence each match what happened in people?</p>',
         md(os.path.join(V04, "part2", "q4_report.md")),
         '<div class="note"><strong>What this cannot tell you.</strong> 104 of the 108 pairs have a positive human '
         'result, and the laboratory literature is almost uniformly positive (205 of 214 determinate laboratory '
         'sides). A body of evidence that nearly always reads “it works” will agree with a mostly positive human '
         'record automatically. Only 4 pairs have a negative human result — the case where predictive value would '
         'actually show — and there laboratory models matched 0 of 4 and companion animals 1 of 4. '
         'So this compares <em>agreement</em>, as the protocol asked, and says nothing about prediction.</div>',
         md(os.path.join(V04, "part2", "q4_reader_audit.md"))]
    page("q4.html", "Companion animals vs laboratory models", "\n".join(b))

    # ---------- methods ----------
    b = ["<h1>Methods and limitations</h1>",
         '<p class="lede">The protocol was frozen before data collection. Everything below is reproducible from '
         'the committed data and scripts, and the things that could be wrong are listed rather than smoothed over.</p>',
         "<h2>How a result gets onto this site</h2>",
         "<ol><li>Retrieval: citation chasing from known reviews plus themed PubMed queries.</li>"
         "<li>Two-stage screening, the second stage calibrated against hand-checked anchor papers.</li>"
         "<li>Open-access full texts only; each headline result is extracted with the sentence it came from.</li>"
         "<li>A separate verifier model checks each result against the located page.</li>"
         "<li>Adjudication: every result, including the ones the verifier excluded, is decided against a fixed "
         "definition of an animal-vs-human correspondence result.</li></ol>",
         "<h2>Retrieval and recall</h2>", md(os.path.join(V04, "retrieval", "recall.md")),
         "<h2>Quality of the extraction and checking</h2>", md(os.path.join(V04, "part1", "part1_quality.md")),
         '<p class="small">Those quality figures describe the model-adjudicated portion. Half of the final results '
         'were adjudicated by hand after API credit ran out; see limitation L87.</p>',
         "<h2>Limitations</h2>", md(J("docs", "limitations.md"))]
    page("methods.html", "Methods and limitations", "\n".join(b))

    # ---------- spot-check ----------
    items = load("part1/spotcheck.json", [])
    b = ["<h1>Spot-check this review</h1>",
         '<p class="lede">Half of the kept results were adjudicated by hand, by the same agent that built the '
         'pipeline, and were not independently checked (limitation L87). This page is the standing invitation to '
         'check them: a fixed, seeded sample with the link and the page number for every item, so anyone can '
         'verify the corpus without taking our word for it.</p>',
         mdsrc(HOW)]
    for s, label in (("A", "Sample A — random final results"),
                     ("B", "Sample B — results from hand-adjudicated studies")):
        rows_s = [x for x in items if x["sample"] == s]
        b.append(f"<h2>{e(label)} ({len(rows_s)})</h2>")
        for it in rows_s:
            ln = " · ".join(f'<a href="{e(u)}">{e(t)}</a>' for t, u in it["links"])
            val = f"{e(it['value'])} {e(it['unit'])}" if it["value"] is not None else "—"
            n = f" (n {e(it['numerator'])}/{e(it['denominator'])})" if it["denominator"] else ""
            b += [f"<h3>{e(s)}{it['n']}. {e((it['title'] or it['pmid'])[:110])}</h3>",
                  f"<p class='small'>{e(it['year'])} · {e(it['journal'] or '—')} · adjudicated by "
                  f"<strong>{e(it['adjudicator'])}</strong> · {ln} · "
                  f"<a href='{e(it['study_page'])}'>study page</a> · "
                  f"local PDF <code>{e(it['pdf_local'])}</code>, <strong>page {e(it['pdf_page'])}</strong></p>",
                  f"<p>{e(it['statement'])}</p>",
                  f"<p class='small'>value <strong>{val}</strong>{n} · species <code>{e(it['species'])}</code> · "
                  f"level {e(it['level'])} · {dirtag(it['direction'])} · {e(it['disease_area'])}</p>",
                  f"<blockquote>“{e(it['quote'])}”</blockquote>"]
    b.append('<p class="small">Found something wrong? The item number, the letter that failed and one line of '
             'what you saw is enough to act on — that is what the check is for.</p>')
    page("spotcheck.html", "Spot-check this review", "\n".join(b))

    # ---------- api ----------
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
