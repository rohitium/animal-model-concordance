"""Expanded retrieval of studies reporting animal-to-human concordance evidence (amendment A6).

Three mechanisms, each recorded per candidate so its contribution can be reported:
  backward   references of every seed (OpenAlex)
  forward    works citing every concordance seed (OpenAlex)
  query      five theme-targeted PubMed searches, resolved to OpenAlex for abstracts

Seeds: studies passing the v0.4 stage-1 scope screen plus named concordance anchors. Attrition and
preclinical-reproducibility papers (Hay 2014, Begley 2012, Prinz 2011, Wong 2019, Cummings 2014,
Freedman 2015) are backward seeds only: their thousands of citing works are overwhelmingly about drug
development or reproducibility, not animal-to-human comparison.

Held-out recall check: concordance studies known from the literature but not used as seeds are looked
up by title in OpenAlex; whether retrieval finds them is reported.

Output: data/v04/retrieval/candidates.json, retrieval_report.md; queries appended to
protocol/search_strings.md
"""
import sys, os, re, json, time, urllib.request, urllib.parse, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
import pubmed

OA = "https://api.openalex.org/works"
UA = {"User-Agent": "animal-model-concordance/1.0 (mailto:rsatija@stanford.edu)"}
SELECT = "id,ids,doi,title,publication_year,type,abstract_inverted_index,cited_by_count,primary_location"
SKIP_TYPES = {"erratum", "paratext", "dataset", "retraction", "peer-review", "grant", "supplementary-materials"}
BACKWARD_ONLY = {"24406927", "22460880", "21892149", "29394327", "25024750", "25670378"}

QUERIES = {
 "efficacy_translation": '("animal model*"[tiab] OR preclinical[tiab] OR "pre-clinical"[tiab] OR "animal stud*"[tiab] OR "animal experiment*"[tiab] OR "animal data"[tiab]) AND ("clinical trial*"[tiab] OR "human stud*"[tiab] OR patients[tiab] OR "clinical outcome*"[tiab] OR "clinical stud*"[tiab]) AND (concordan*[tiab] OR discordan*[tiab] OR "translational success"[tiab] OR "translation rate*"[tiab] OR "predictive validity"[tiab] OR "predictive value"[tiab] OR "agreement between"[tiab] OR "animal-to-human"[tiab] OR "bench-to-bedside"[tiab] OR "from animals to humans"[tiab])',
 "tox_safety_concordance": '(toxicit*[tiab] OR "adverse drug reaction*"[tiab] OR "adverse event*"[tiab] OR "target organ"[tiab] OR teratogen*[tiab] OR carcinogen*[tiab] OR hepatotox*[tiab]) AND (concordan*[tiab] OR "predictive value"[tiab] OR "positive predictive"[tiab] OR "negative predictive"[tiab] OR "likelihood ratio*"[tiab] OR "true positive"[tiab] OR "sensitivity and specificity"[tiab]) AND (animal*[tiab] OR preclinical[tiab] OR nonclinical[tiab] OR "non-clinical"[tiab] OR rodent*[tiab] OR "non-rodent"[tiab] OR dog*[tiab] OR monkey*[tiab] OR "non-human primate*"[tiab]) AND (human*[tiab] OR clinical[tiab] OR "first-in-human"[tiab])',
 "cross_species_biology": '("cross-species"[tiab] OR interspecies[tiab] OR "inter-species"[tiab] OR "mouse and human"[tiab] OR "human and mouse"[tiab] OR "murine and human"[tiab] OR "rat and human"[tiab] OR "dog and human"[tiab] OR "canine and human"[tiab]) AND (transcriptom*[tiab] OR "gene expression"[tiab] OR proteom*[tiab] OR pathway*[tiab] OR histopatholog*[tiab]) AND (concordan*[tiab] OR correlat*[tiab] OR "recapitulat*"[tiab] OR mimic*[tiab] OR similarit*[tiab] OR conserved[tiab]) AND (disease[tiab] OR "disease model*"[tiab] OR "animal model*"[tiab])',
 "companion_animal_translation": '("comparative oncology"[tiab] OR "client-owned"[tiab] OR "client owned"[tiab] OR "pet dogs"[tiab] OR "companion animal*"[tiab] OR "naturally occurring"[tiab] OR spontaneous[tiab]) AND (dog*[tiab] OR canine[tiab] OR cat*[tiab] OR feline[tiab]) AND (human*[tiab] OR patients[tiab] OR "clinical trial*"[tiab]) AND (translat*[tiab] OR concordan*[tiab] OR "predictive"[tiab] OR "model for human"[tiab] OR "human counterpart"[tiab] OR "comparative"[tiab]) AND (drug*[tiab] OR therap*[tiab] OR treatment*[tiab] OR inhibitor*[tiab])',
 "safety_pharmacology_qt": '(QT[tiab] OR QTc[tiab] OR hERG[tiab] OR "safety pharmacology"[tiab] OR "torsade*"[tiab] OR hemodynamic*[tiab]) AND (dog*[tiab] OR monkey*[tiab] OR "non-human primate*"[tiab] OR telemetry[tiab] OR "guinea pig*"[tiab] OR "in vivo"[tiab]) AND (clinical[tiab] OR human*[tiab] OR "thorough QT"[tiab]) AND (concordan*[tiab] OR predictiv*[tiab] OR translat*[tiab] OR "sensitivity"[tiab] OR "false positive"[tiab] OR "false negative"[tiab])',
}

# Held out from seeding: known concordance studies used only to measure recall. Located by title search
# in OpenAlex at run time; if a title does not resolve it is reported, not guessed.
HELD_OUT = [
 "Where is the evidence that animal research benefits humans?",
 "Pharmaceutical toxicity: concordance between animal and human",
 "The predictive value of animal studies for human toxicity",
 "Analysis of the relationship between the results of preclinical and clinical studies of drug candidates",
 "Systematic review and meta-analysis of the efficacy of interleukin-1 receptor antagonist in animal models of stroke",
 "Publication bias in reports of animal stroke studies leads to major overstatement of efficacy",
 "A systematic review of the concordance between preclinical and clinical findings",
 "Translational success rate of animal models",
 "Cross-species transcriptomic analysis",
 "Comparative oncology: what dogs and other species can teach us about humans with cancer",
 "Concordance between animal toxicity and human adverse events",
 "Predictivity of animal studies for human injection site reactions",
 "The flaws and human harms of animal experimentation",
 "Animal models of human disease: challenges in enabling translation to the clinic",
]

OA_CACHE = os.path.join(CACHE, "openalex")
os.makedirs(OA_CACHE, exist_ok=True)

def get(url, tries=5):
    """OpenAlex GET, cached on disk so a rerun never refetches."""
    cp = os.path.join(OA_CACHE, sha(url)[:32] + ".json")
    if os.path.exists(cp):
        return json.load(open(cp))
    for a in range(tries):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read())
            json.dump(d, open(cp, "w"))
            return d
        except Exception:
            time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"OpenAlex request failed: {url[:160]}")

def abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)

def slim(w):
    pmid = ((w.get("ids") or {}).get("pmid") or "").rsplit("/", 1)[-1] or None
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    return {"openalex": w["id"].rsplit("/", 1)[-1], "pmid": pmid, "doi": w.get("doi"), "title": w.get("title") or "",
            "year": w.get("publication_year"), "type": w.get("type"), "journal": src,
            "cited_by": w.get("cited_by_count"), "abstract": abstract(w.get("abstract_inverted_index"))}

def by_pmids(pmids):
    out = []
    for i in range(0, len(pmids), 50):
        chunk = "|".join(pmids[i:i + 50])
        out += get(f"{OA}?filter=ids.pmid:{chunk}&per-page=50&select={SELECT}&mailto=rsatija@stanford.edu")["results"]
    return out

def by_ids(ids):
    out = []
    for i in range(0, len(ids), 50):
        chunk = "|".join(ids[i:i + 50])
        out += get(f"{OA}?filter=openalex:{chunk}&per-page=50&select={SELECT}&mailto=rsatija@stanford.edu")["results"]
    return out

def citing(wid):
    out, cursor = [], "*"
    while cursor:
        d = get(f"{OA}?filter=cites:{wid}&per-page=200&cursor={urllib.parse.quote(cursor)}&select={SELECT}&mailto=rsatija@stanford.edu")
        out += d["results"]
        cursor = d["meta"].get("next_cursor")
        if not d["results"]:
            break
    return out

def main():
    os.makedirs(os.path.join(V04, "retrieval"), exist_ok=True)
    scope = load("s1_scope.json")
    probe = load("frames/expand_seeds_probe.json")
    seeds_pm = sorted(set(probe["seeds"]))
    seed_works = {slim(w)["pmid"]: w for w in by_pmids(seeds_pm)}
    print(f"seeds: {len(seeds_pm)} PMIDs, {len(seed_works)} resolved", flush=True)

    cands = {}
    def add(w, source):
        if (w.get("type") or "") in SKIP_TYPES:
            return
        s = slim(w)
        rec = cands.setdefault(s["openalex"], {**s, "sources": set()})
        rec["sources"].add(source)
        if not rec["abstract"] and s["abstract"]:
            rec["abstract"] = s["abstract"]

    for pm, w in seed_works.items():
        add(w, "seed")

    # backward
    ref_ids = sorted({r.rsplit("/", 1)[-1] for pm in seed_works
                      for r in get(f"{OA}/{seed_works[pm]['id'].rsplit('/', 1)[-1]}?select=referenced_works&mailto=rsatija@stanford.edu").get("referenced_works", [])})
    for w in by_ids(ref_ids):
        add(w, "backward")
    print(f"backward: {len(ref_ids)} referenced works; candidates now {len(cands)}", flush=True)

    # forward (concordance seeds only)
    fwd = [w for pm, w in seed_works.items() if pm not in BACKWARD_ONLY]
    with ThreadPoolExecutor(max_workers=6) as ex:
        for ws in ex.map(lambda w: citing(w["id"].rsplit("/", 1)[-1]), fwd):
            for x in ws:
                add(x, "forward")
    print(f"forward: from {len(fwd)} seeds; candidates now {len(cands)}", flush=True)

    # theme queries
    qlog = []
    for name, q in QUERIES.items():
        n, ids, trans = pubmed.esearch(q, retmax=9999)
        got = by_pmids(ids)
        found = {slim(w)["pmid"] for w in got}
        for w in got:
            add(w, f"query:{name}")
        missing = [p for p in ids if p not in found]
        for p in missing:   # PubMed records OpenAlex does not resolve: keep them, abstract fetched at screening
            cands.setdefault(f"PMID{p}", {"openalex": None, "pmid": p, "doi": None, "title": "", "year": None, "type": "article",
                                           "journal": None, "cited_by": None, "abstract": "", "sources": set()})["sources"].add(f"query:{name}")
        qlog.append((name, q, n, len(ids), len(missing)))
        print(f"query {name}: {n} hits, {len(missing)} not in OpenAlex; candidates now {len(cands)}", flush=True)

    for c in cands.values():
        c["sources"] = sorted(c["sources"]) if isinstance(c["sources"], set) else c["sources"]
    save(cands, "retrieval/candidates.json")          # saved before the recall check, which must not lose them

    # held-out recall
    recall = []
    keys_by_title = {re.sub(r"[^a-z0-9]", "", (c["title"] or "").lower()): k for k, c in cands.items()}
    for t in HELD_OUT:
        words = re.sub(r"[^A-Za-z0-9 ]+", " ", t).strip()
        try:
            d = get(f"{OA}?filter=title.search:{urllib.parse.quote(words)}&per-page=1&select=id,title,publication_year&mailto=rsatija@stanford.edu", tries=3)
        except Exception:
            d = {"results": []}
        if not d["results"]:
            recall.append({"query": t, "resolved": None, "retrieved": None}); continue
        w = d["results"][0]
        wid = w["id"].rsplit("/", 1)[-1]
        norm_t = re.sub(r"[^a-z0-9]", "", (w["title"] or "").lower())
        recall.append({"query": t, "resolved": f"{w['title']} ({w['publication_year']})", "openalex": wid,
                       "retrieved": wid in cands or norm_t in keys_by_title})

    src_counts = collections.Counter(s.split(":")[0] for c in cands.values() for s in c["sources"])
    only = collections.Counter(c["sources"][0].split(":")[0] for c in cands.values() if len({s.split(':')[0] for s in c["sources"]}) == 1)
    L = ["# Expanded retrieval (amendment A6)", "", f"Run {today()} by `analysis/v04/r1_retrieve.py`.", "",
         f"- seeds: {len(seed_works)} ({len(fwd)} used for forward chasing)",
         f"- unique candidates: {len(cands)}",
         f"- with abstract: {sum(1 for c in cands.values() if c['abstract'])}", "",
         "| mechanism | records | found only by this mechanism |", "|---|---|---|"]
    L += [f"| {k} | {v} | {only.get(k, 0)} |" for k, v in src_counts.most_common()]
    L += ["", "## Theme queries", "", "| theme | PubMed hits | retrieved | not in OpenAlex |", "|---|---|---|---|"]
    L += [f"| {n} | {h} | {r} | {m} |" for n, q, h, r, m in qlog]
    ok = [r for r in recall if r["resolved"]]
    L += ["", f"## Held-out recall: {sum(1 for r in ok if r['retrieved'])}/{len(ok)} resolved titles retrieved", ""]
    L += [f"- {'✓' if r['retrieved'] else '✗'} {r['resolved'] or 'not resolved: ' + r['query']}" for r in recall]
    open(os.path.join(V04, "retrieval", "retrieval_report.md"), "w").write("\n".join(L) + "\n")
    with open(J("protocol", "search_strings.md"), "a") as f:
        f.write(f"\n\n## v0.4 A6 — theme queries for expanded retrieval (run {today()})\n")
        for n, q, h, r, m in qlog:
            f.write(f"\n### {n} — {h} hits\n\n```\n{q}\n```\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
