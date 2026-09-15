"""Part 1 outputs (amendment A6): final result set, evidence map, draft page-15 rows, and the human spot-check list.

Final result set = every result the adjudicator kept (keep / keep-with-correction, corrections applied), whatever
the verifier said, from studies judged eligible; verified results without an adjudication decision also count. Excluded and dropped results are kept in the file with their reason and never enter
the map or the table.

Outputs (data/v04/part1/):
  final_results.json      every result with provenance: extraction, verifier, adjudication
  evidence_map.json/.md   disease area × species column × level: number of studies and results, direction counts
  table_draft.md          page-15 candidate rows by theme: study counts, value spreads, named studies
  spotcheck.md            20 randomly selected final results (seed 20260914) for the user to check against PDFs
"""
import sys, os, random, statistics, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

SEED, N_SPOT = 20260914, 20

def final_results():
    heads = load("part1/headlines.json")
    ver = load("part1/verified.json")
    adj = load("part1/adjudicated.json")
    studies = load("part1/studies.json")
    decisions = {}
    for k, r in adj.items():
        if k.endswith("|all") or k.endswith("|excl") or k.endswith("|manual"):   # excluded results are adjudicated too (e4 audit); "|manual" = reviewing agent, after API credit ran out
            decisions.update(r.get("decisions") or {})
    rows = []
    for pm, h in heads.items():
        if h.get("status") != "done":
            continue
        for it in h["items"]:
            v = ver.get(it["id"], {})
            d = decisions.get(it["id"])
            status, rec = v.get("status"), dict(it)
            if d and d["decision"] == "drop":
                status = "dropped"
            elif d and d["decision"] in ("keep", "keep-with-correction"):
                if d["decision"] == "keep-with-correction":
                    rec.update({k: d["corrected"][k] for k in ("statement", "value", "unit", "numerator", "denominator",
                                                               "species", "model_type", "disease_area", "level", "direction",
                                                               "pdf_page") if k in d["corrected"]})
                status = "final"
            elif status == "verified":
                status = "final"
            lv = (rec.get("level") or "").strip().upper()[:1]
            rec["level"] = {"A": "A-outcome-concordance", "B": "B-toxicity-safety-concordance", "C": "C-biological-similarity"}.get(lv, rec.get("level"))
            rows.append({"pmid": pm, "title": (studies.get(pm) or {}).get("title"), "year": (studies.get(pm) or {}).get("year"),
                         "design": h.get("design"), "peer_reviewed": h.get("peer_reviewed"), "study_eligible": h.get("eligible"),
                         "status": status if h.get("eligible") else "study-ineligible", "verifier_reasons": v.get("reasons"),
                         "adjudication": d, **rec})
    return rows

HOW = """## What you are checking, and why it matters

Every result on the site was extracted by a model, checked by a second model, then decided by an
adjudicator. For 769 of the 1,494 final results that adjudicator was the same agent that built the
pipeline, working by hand and not blind (limitation L87). **This spot-check is the only independent
check on that.** If it passes, the corpus has been checked by someone who did not build it. If it
fails, we learn where, and re-adjudicate that class of result rather than patching single rows.

Two samples below, drawn by fixed seeds so they can be redrawn and audited:

- **Sample A — 30 random final results** (seed 20260914), an unbiased read of the whole corpus.
- **Sample B — 10 results from hand-adjudicated studies** (seed 20260915), aimed squarely at the
  weakest link. These are the ones to do first if you only have an hour.

## How to check one (about 5 minutes)

1. Open the paper — the PubMed/OpenAlex link, or the DOI. The local PDF path is given too; the PDF
   page number is where the extractor located the quote.
2. Find the quoted sentence. Searching a distinctive phrase from it is faster than reading the page.
3. Then check these four things **in order**, and stop at the first one that fails:

| # | Question | Fails if |
|---|---|---|
| a | Is the quote really in this paper, and is it this paper's own result? | the sentence isn't there, or it is a figure the authors quote from someone else's study |
| b | Does the statement say what the quote says? | the statement asserts more, less, or something different |
| c | Do the value, unit and n match the quote? | a number differs, or a rate is inverted (43% vs 57%) |
| d | Is this an animal-vs-human comparison, with the right species and level? | it is an animal-only result, an animal-vs-animal result, an in-vitro result, or the species/level is wrong |

**Not failures:** paraphrase that preserves the meaning; rounding (71% vs 70.6%); a page number one
off from where you find the quote; a value repeated elsewhere in the paper.

**Failures worth flagging loudly:** (a) and (d). Those mean the result should never have been kept,
and they tend to come in classes rather than singly.

## How to record it

Mark each item ✓ or ✗ below, and for a ✗ write **which letter failed** (a/b/c/d) plus one line of
what you saw. The letter matters more than the prose — it tells me whether to re-run extraction,
re-adjudicate a category, or fix one row.

**Then tell me the count.** Rough reading: 0–1 failures across the 40 is consistent with the error
rate the model-adjudicated portion already showed. Two or more failures on (a) or (d) is a
systematic problem, not bad luck, and I will re-adjudicate that whole class before the site stands.
"""


def spotcheck(fin, n_random=30, n_manual=10):
    """The human check on the corpus: two seeded samples, each item with links and a page number.

    Half the final results were adjudicated by hand and not blind (L87), so sample B deliberately
    oversamples those. Written as markdown for working through offline and as JSON for the site.
    """
    studies = load("part1/studies.json")
    adj = load("part1/adjudicated.json")
    manual_pmids = {k.rsplit("|", 1)[0] for k in adj if k.endswith("|manual")}

    def links(r):
        pm, st = r["pmid"], studies.get(r["pmid"]) or {}
        out = [("PubMed", f"https://pubmed.ncbi.nlm.nih.gov/{pm}/") if pm.isdigit()
               else ("OpenAlex", f"https://openalex.org/{st.get('openalex') or pm}")]
        if st.get("doi"):
            out.append(("DOI", st["doi"] if st["doi"].startswith("http") else f"https://doi.org/{st['doi']}"))
        return out

    def item(r, i, sample):
        st = studies.get(r["pmid"]) or {}
        return {"n": i, "sample": sample, "id": r["id"], "pmid": r["pmid"], "title": r.get("title"),
                "year": r.get("year"), "journal": st.get("journal"),
                "adjudicator": "hand" if r["pmid"] in manual_pmids else "model",
                "statement": r["statement"], "value": r.get("value"), "unit": r.get("unit"),
                "numerator": r.get("numerator"), "denominator": r.get("denominator"),
                "species": species_column(r["species"], r.get("model_type")), "level": (r["level"] or "?")[:1],
                "direction": r.get("direction"), "disease_area": r.get("disease_area"),
                "quote": r.get("quote"), "pdf_page": r.get("pdf_page"),
                "pdf_local": f"data/raw/fulltext/{r['pmid']}.pdf",
                "study_page": f"study/{r['pmid']}.html", "links": links(r)}

    a = random.Random(SEED).sample(fin, min(n_random, len(fin)))
    pool = [r for r in fin if r["pmid"] in manual_pmids]
    b = random.Random(SEED + 1).sample(pool, min(n_manual, len(pool)))
    items = ([item(r, i, "A") for i, r in enumerate(a, 1)] +
             [item(r, i, "B") for i, r in enumerate(b, 1)])
    save(items, "part1/spotcheck.json")

    S = [f"# Spot-check: {len(items)} results to verify by hand", "",
         f"Built {today()} from {len(fin)} final results in {len({r['pmid'] for r in fin})} studies. "
         f"Sample A seed {SEED}, sample B seed {SEED + 1}; both redrawable by re-running `t1_part1_outputs.py`.", "",
         HOW]
    for sample, label in (("A", f"Sample A — {n_random} random final results"),
                          ("B", f"Sample B — {n_manual} results from hand-adjudicated studies")):
        S += [f"## {label}", ""]
        for it in [x for x in items if x["sample"] == sample]:
            ln = " · ".join(f"[{t}]({u})" for t, u in it["links"])
            val = f"{it['value']} {it['unit']}" if it["value"] is not None else "—"
            n = f" (n {it['numerator']}/{it['denominator']})" if it["denominator"] else ""
            S += [f"### {sample}{it['n']}. {(it['title'] or it['pmid'])[:110]}",
                  f"{it['year']} · {it['journal'] or '—'} · record {it['pmid']} · adjudicated by **{it['adjudicator']}**",
                  "",
                  f"- **Open:** {ln} · local PDF `{it['pdf_local']}` · **go to PDF page {it['pdf_page']}**",
                  f"- **Statement:** {it['statement']}",
                  f"- **Value:** {val}{n} · species `{it['species']}` · level {it['level']} · "
                  f"direction {it['direction']} · {it['disease_area']}",
                  f"- **Quote:** “{(it.get('quote') or '')[:300]}”",
                  "- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______", ""]
    open(os.path.join(V04, "part1", "spotcheck.md"), "w").write("\n".join(S) + "\n")


def main():
    rows = final_results()
    save(rows, "part1/final_results.json")
    fin = [r for r in rows if r["status"] == "final"]

    grid = collections.defaultdict(lambda: {"studies": set(), "results": 0, "direction": collections.Counter()})
    for r in fin:
        col = species_column(r["species"], r.get("model_type"))
        g = grid[(r.get("disease_area") or "new", col, r["level"])]
        g["studies"].add(r["pmid"]); g["results"] += 1; g["direction"][r.get("direction")] += 1
    emap = [{"disease_area": a, "species": s, "level": l, "n_studies": len(g["studies"]), "n_results": g["results"],
             "direction": dict(g["direction"])} for (a, s, l), g in sorted(grid.items())]
    save(emap, "part1/evidence_map.json")
    areas = sorted({e["disease_area"] for e in emap}); cols = sorted({e["species"] for e in emap})
    cell_studies = collections.defaultdict(set); cell_levels = collections.defaultdict(set)
    for r in fin:
        key = (r.get("disease_area") or "new", species_column(r["species"], r.get("model_type")))
        cell_studies[key].add(r["pmid"]); cell_levels[key].add((r["level"] or "?")[:1])
    L = ["# Evidence map (draft)", "", "Each cell: highest evidence level present (A outcome > B toxicity/safety > C biology) · "
         "number of distinct studies with a final result.", "",
         "| disease area | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for a in areas:
        cells = [f"{min(cell_levels[(a, c)])}·{len(cell_studies[(a, c)])}" if cell_studies.get((a, c)) else "" for c in cols]
        L.append(f"| {a} | " + " | ".join(cells) + " |")
    open(os.path.join(V04, "part1", "evidence_map.md"), "w").write("\n".join(L) + "\n")

    T = ["# Page-15 replacement: draft rows", "", f"Built {today()} from {len(fin)} final results in {len({r['pmid'] for r in fin})} studies.",
         "Values are grouped only where the unit and metric match; spreads are reported, never a single blended number.", ""]
    for lv, title in (("A-outcome-concordance", "Efficacy / intervention outcomes"), ("B-toxicity-safety-concordance", "Toxicology and safety"),
                      ("C-biological-similarity", "Disease biology")):
        sub = [r for r in fin if r["level"] == lv]
        T += [f"## {title}: {len({r['pmid'] for r in sub})} studies, {len(sub)} results", ""]
        by_metric = collections.defaultdict(list)
        for r in sub:
            if r.get("value") is not None:
                key = (re.sub(r"[^a-z]+", " ", (r.get("metric") or "").lower()).strip()[:40], r.get("unit"), species_column(r["species"], r.get("model_type")))
                by_metric[key].append(r)
        T += ["| metric | unit | species | studies | results | median | range |", "|---|---|---|---|---|---|---|"]
        for (m, u, sp), rs in sorted(by_metric.items(), key=lambda kv: -len({r['pmid'] for r in kv[1]})):
            vals = [r["value"] for r in rs]
            T.append(f"| {m} | {u} | {sp} | {len({r['pmid'] for r in rs})} | {len(rs)} | {statistics.median(vals):g} | {min(vals):g}–{max(vals):g} |")
        dirs = collections.Counter(r.get("direction") for r in sub)
        T += ["", f"Direction of results (as judged per result): {dict(dirs)}", ""]
    open(os.path.join(V04, "part1", "table_draft.md"), "w").write("\n".join(T) + "\n")

    spotcheck(fin)
    print(f"final results {len(fin)} in {len({r['pmid'] for r in fin})} studies; status {dict(collections.Counter(r['status'] for r in rows))}")

if __name__ == "__main__":
    main()
