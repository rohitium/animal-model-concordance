"""Part 2, step 1: candidate drugs tested in dogs or cats with naturally occurring disease that also exist in
human medicine (amendment A6).

Sources, each recorded per candidate:
  cotc       every NCI Comparative Oncology Trials Consortium trial (frames/cotc.json)
  pubmed     the systematic PubMed frame of client-owned / naturally occurring dog and cat trials
             (frames/pubmed_companion.json, query logged in protocol/search_strings.md)
  exemplar   hand-added well-known cases in both directions, searched by name in PubMed; reported
             separately so their influence on the table is visible

A fast model reads each record and names the TEST agent(s), indication, species and whether the animals
are client-owned with naturally occurring disease. Whether an agent exists in humans is decided by
f7_resolve.resolve (US human-medicine index, or registered interventional human trials in the
ClinicalTrials.gov snapshot, including development-code synonyms), never by the model.

Pair relation (working decision, logged in A6 notes):
  same-molecule                 the same active ingredient in both species (primary table)
  species-specific-biologic     a species-adapted antibody/protein against the same target as a human product
                                (primary table)
  class-analogue                a different molecule with the same mechanism (separate stratum)

Output: data/v04/part2/candidates.json, data/v04/part2/candidates_report.md
"""
import sys, os, re, html, time, collections, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from f7_resolve import resolve
import pubmed

MODEL = "google/gemini-2.5-flash-lite"

# Hand-added exemplars: (veterinary agent, species, human counterpart(s), relation, PubMed search terms).
# Names only; the veterinary study and human evidence are found by search, never typed in.
EXEMPLARS = [
 ("bedinvetmab", "dog", ["tanezumab", "fasinumab"], "species-specific-biologic", '(bedinvetmab OR "anti-NGF") AND dogs AND osteoarthritis'),
 ("frunevetmab", "cat", ["tanezumab", "fasinumab"], "species-specific-biologic", '(frunevetmab OR "anti-NGF") AND cats AND osteoarthritis'),
 ("lokivetmab", "dog", ["nemolizumab"], "species-specific-biologic", 'lokivetmab AND dogs AND "atopic dermatitis"'),
 ("oclacitinib", "dog", ["tofacitinib", "baricitinib", "upadacitinib", "abrocitinib"], "class-analogue", 'oclacitinib AND dogs AND (pruritus OR "atopic dermatitis")'),
 ("toceranib", "dog", ["sunitinib"], "class-analogue", 'toceranib AND dogs AND ("mast cell" OR tumor OR tumour)'),
 ("masitinib", "dog", ["masitinib"], "same-molecule", 'masitinib AND dogs AND ("mast cell" OR tumor)'),
 ("verdinexor", "dog", ["selinexor"], "class-analogue", 'verdinexor AND dogs AND lymphoma'),
 ("rabacfosadine", "dog", ["GS-9219"], "same-molecule", '(rabacfosadine OR "GS-9219" OR VDC-1101) AND dogs AND lymphoma'),
 ("ibrutinib", "dog", ["ibrutinib"], "same-molecule", 'ibrutinib AND (dogs OR canine) AND lymphoma'),
 ("sirolimus", "dog", ["sirolimus", "everolimus"], "same-molecule", '(rapamycin OR sirolimus) AND (dogs OR canine) AND osteosarcoma'),
 ("mavacamten", "cat", ["mavacamten"], "same-molecule", '(mavacamten OR "MYK-461") AND (cats OR feline) AND cardiomyopathy'),
 ("carboplatin", "dog", ["carboplatin"], "same-molecule", 'carboplatin AND dogs AND osteosarcoma AND amputation'),
 ("doxorubicin", "dog", ["doxorubicin"], "same-molecule", 'doxorubicin AND dogs AND (hemangiosarcoma OR lymphoma) AND "client-owned"'),
 ("gabapentin", "cat", ["gabapentin"], "same-molecule", 'gabapentin AND cats AND (osteoarthritis OR pain) AND randomized'),
 ("amlodipine", "cat", ["amlodipine"], "same-molecule", 'amlodipine AND cats AND hypertension'),
]

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "intervention_study": {"type": "boolean"},
    "client_owned_naturally_occurring": {"type": "string"},
    "species": {"type": "string"},
    "test_agents": {"type": "array", "items": {"type": "string"}},
    "indication": {"type": ["string", "null"]},
    "design": {"type": "string"},
    "efficacy_result": {"type": ["string", "null"]}},
    "required": ["intervention_study", "client_owned_naturally_occurring", "species", "test_agents", "indication",
                 "design", "efficacy_result"]}
SYSTEM = """Read this record of a study in animals.
intervention_study: true if a treatment was given and its outcome reported.
client_owned_naturally_occurring: "yes" if the animals are pets or client-owned patients with naturally
  occurring disease; "no" if laboratory-kept or with induced disease; "unclear" otherwise.
species: dog | cat | dog-and-cat | other.
test_agents: the treatment(s) whose effect the study set out to evaluate, by drug name; exclude comparators,
  background therapy and placebo. Empty if not a drug, biologic, cell or gene therapy.
indication: the disease treated, as written.
design: randomized-controlled | single-arm | dose-escalation | observational | other.
efficacy_result: one sentence with the main efficacy result, copied or closely paraphrased, or null.
Answer with JSON only."""

def efetch(pmids):
    got = {}
    for i in range(0, len(pmids), 200):
        chunk = pmids[i:i + 200]
        cp = os.path.join(CACHE, "text", f"efetch200_{sha(','.join(chunk))[:20]}.json")
        if os.path.exists(cp):
            got.update(json.load(open(cp))); continue
        xml = ""
        for a in range(5):
            try:
                q = urllib.parse.urlencode({"db": "pubmed", "retmode": "xml", "id": ",".join(chunk)})
                xml = urllib.request.urlopen(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{q}", timeout=120).read().decode("utf-8", "ignore")
                break
            except Exception:
                time.sleep(2 * (a + 1))
        part = {}
        clean = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()
        for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, flags=re.S):
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
            t = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", art, flags=re.S)
            ab = re.search(r"<Abstract>(.*?)</Abstract>", art, flags=re.S)
            yr = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", art, flags=re.S)
            part[pm] = {"title": clean(t.group(1) if t else ""), "year": yr.group(1) if yr else None,
                        "abstract": clean(" ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", ab.group(1), flags=re.S))) if ab else ""}
        if part:
            json.dump(part, open(cp, "w"))
        got.update(part)
        time.sleep(0.4)
    return got

def main():
    os.makedirs(os.path.join(V04, "part2"), exist_ok=True)
    records = {}   # key -> {source, text, title, year}
    for t in load("frames/cotc.json")["trials"]:
        records["COTC:" + t["trial_id"]] = {"source": "cotc", "title": t["title"], "year": None,
                                            "text": f"{t['title']}\n{t['purpose']}\nPublications: {'; '.join(t['publications'])}"}
    frame = load("frames/pubmed_companion.json")["pmids"]
    ex_hits = {}
    for agent, sp, human, rel, q in EXEMPLARS:
        n, ids, _ = pubmed.esearch(q, retmax=40, sort="relevance")
        ex_hits[agent] = {"query": q, "hits": n, "pmids": ids, "species": sp, "human": human, "relation": rel}
    all_pm = sorted(set(frame) | {p for v in ex_hits.values() for p in v["pmids"]})
    abstracts = efetch(all_pm)
    for pm in all_pm:
        a = abstracts.get(pm)
        if not a:
            continue
        srcs = (["pubmed"] if pm in set(frame) else []) + [f"exemplar:{k}" for k, v in ex_hits.items() if pm in v["pmids"]]
        records["PMID:" + pm] = {"source": "+".join(srcs), "title": a["title"], "year": a["year"],
                                 "text": f"{a['title']}\n{a['abstract']}"}
    print(f"records to read: {len(records)} (cotc {sum(1 for k in records if k.startswith('COTC'))}, "
          f"frame {len(frame)}, exemplar searches {sum(len(v['pmids']) for v in ex_hits.values())})", flush=True)

    res = pmap(lambda k: ask(MODEL, SYSTEM, records[k]["text"][:12000], SCHEMA, max_tokens=2000, deadline_s=60)[0],
               list(records), workers=48, label="read")
    cands, stats = [], collections.Counter()
    for k, rec in records.items():
        r = res[k]
        if "error" in r:
            stats["read-error"] += 1; continue
        if not r["intervention_study"] or not r["test_agents"]:
            stats["not-drug-intervention"] += 1; continue
        if r["client_owned_naturally_occurring"] != "yes" and not k.startswith("COTC"):
            stats["not-client-owned-spontaneous"] += 1; continue
        if r["species"] not in ("dog", "cat", "dog-and-cat"):
            stats["not-dog-or-cat"] += 1; continue
        matched = False
        for agent in r["test_agents"]:
            for m in resolve(agent):
                matched = True
                cands.append({"record": k, "source": rec["source"], "title": rec["title"], "year": rec["year"],
                              "species": r["species"], "agent_as_written": agent, "ingredient": m["ingredient"],
                              "match": m["kind"], "human_status": m["human_status"], "n_human_trials": m["n_trials"],
                              "relation": "same-molecule", "indication": r["indication"], "design": r["design"],
                              "efficacy_result": r["efficacy_result"]})
        for ex, v in ex_hits.items():   # species-specific biologics and class analogues: relation from the exemplar entry
            if k[5:] in v["pmids"] and any(ex in a.lower() or "nerve growth factor" in a.lower() and "ngf" in v["query"].lower()
                                           for a in r["test_agents"]) and v["relation"] != "same-molecule":
                for h in v["human"]:
                    for m in resolve(h)[:1]:
                        matched = True
                        cands.append({"record": k, "source": rec["source"], "title": rec["title"], "year": rec["year"],
                                      "species": r["species"], "agent_as_written": ex, "ingredient": m["ingredient"],
                                      "match": "exemplar-relation", "human_status": m["human_status"], "n_human_trials": m["n_trials"],
                                      "relation": v["relation"], "indication": r["indication"], "design": r["design"],
                                      "efficacy_result": r["efficacy_result"]})
        stats["candidate" if matched else "agent-not-in-us-human-medicine"] += 1
    save({"built": today(), "model": MODEL, "exemplar_searches": ex_hits, "stats": dict(stats), "candidates": cands}, "part2/candidates.json")

    by_drug = collections.defaultdict(lambda: {"records": set(), "indications": collections.Counter(), "species": set(), "sources": set(), "relation": set()})
    for c in cands:
        d = by_drug[(c["ingredient"], c["relation"])]
        d["records"].add(c["record"]); d["indications"][(c["indication"] or "").lower()[:60]] += 1
        d["species"].add(c["species"]); d["sources"].add(c["source"].split(":")[0].split("+")[0]); d["relation"].add(c["relation"])
    L = ["# Part 2 candidates", "", f"Built {today()} by `analysis/v04/d1_candidates.py` ({MODEL} reads; lookup decides human-medicine status).", "",
         "## Records", ""] + [f"- {k}: {v}" for k, v in stats.most_common()]
    L += ["", f"## Candidate drugs: {len(by_drug)}", "", "| ingredient | relation | records | species | sources | most common indications |", "|---|---|---|---|---|---|"]
    for (ing, rel), d in sorted(by_drug.items(), key=lambda kv: -len(kv[1]["records"])):
        L.append(f"| {ing} | {rel} | {len(d['records'])} | {', '.join(sorted(d['species']))} | {', '.join(sorted(d['sources']))} | "
                 f"{'; '.join(i for i, _ in d['indications'].most_common(3))} |")
    open(os.path.join(V04, "part2", "candidates_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))

if __name__ == "__main__":
    main()
