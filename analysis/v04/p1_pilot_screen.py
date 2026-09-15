"""Step 1b, part 1 — pilot screen of drug-pair candidates (PLAN.md v0.4 §7, §11).

Candidates are drawn from the sampling frames in a seeded random order, not chosen: the COTC
trial list and the systematic PubMed frame. Each is screened by two models from different
families on what the record itself states. Screening continues in batches until enough
candidates qualify for the human-counterpart lookup, and every screened record is kept, whether it
qualified or not, so the pilot's denominator is visible.

Output: data/v04/pilot/screen.json
"""
import sys, os, re, html, random, urllib.request, urllib.parse, time
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

SEED = 20260914
BATCH = 40
TARGET_QUALIFYING = 25     # expected to yield >= 10 pairs after human-counterpart lookup
MAX_SCREEN = 400

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "intervention_study": {"type": "boolean"},
    "spontaneous_disease": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "client_owned": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "species": {"type": "string", "enum": ["dog", "cat", "dog-and-cat", "other", "none"]},
    "agents": {"type": "array", "items": {"type": "string"}},
    "agent_type": {"type": "string", "enum": ["small-molecule", "biologic", "cell-or-gene-therapy",
                   "vaccine", "device-or-procedure", "diet-or-supplement", "radiation", "other", "none"]},
    "indication": {"type": ["string", "null"]},
    "design": {"type": "string", "enum": ["randomized-controlled", "single-arm", "dose-escalation",
               "observational", "other", "not-stated"]},
    "n_animals": {"type": ["integer", "null"]},
    "efficacy_result_quote": {"type": ["string", "null"]},
    "safety_result_quote": {"type": ["string", "null"]},
    "reason": {"type": "string"}},
    "required": ["intervention_study", "spontaneous_disease", "client_owned", "species", "agents",
                 "agent_type", "indication", "design", "n_animals", "efficacy_result_quote",
                 "safety_result_quote", "reason"]}

SYSTEM = """You are screening a record describing a study in animals. Answer only from the record.
intervention_study: the study gives a treatment (drug, biologic, cell/gene therapy, vaccine,
  procedure, diet) to animals and reports an outcome of that treatment.
spontaneous_disease: the animals have naturally occurring disease (not induced or engineered).
client_owned: the animals are pets / client-owned / privately owned patients.
agents: the names of the treatments given, as written.
indication: the disease treated, as written.
efficacy_result_quote / safety_result_quote: copy the sentence reporting the main efficacy or
  safety result exactly, or null.
reason: one sentence, no adjectives.
Answer with JSON only."""

def efetch_abstracts(pmids):
    out = {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        cp = os.path.join(CACHE, "text", f"efetch_{sha(','.join(chunk))[:20]}.json")
        if os.path.exists(cp):
            out.update(json.load(open(cp))); continue
        q = urllib.parse.urlencode({"db": "pubmed", "retmode": "xml", "id": ",".join(chunk)})
        xml = urllib.request.urlopen(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{q}",
                                     timeout=120).read().decode("utf-8", errors="ignore")
        got = {}
        for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, flags=re.S):
            pm = re.search(r'<PMID[^>]*>(\d+)</PMID>', art).group(1)
            title = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", art, flags=re.S)
            ab = re.search(r"<Abstract>(.*?)</Abstract>", art, flags=re.S)   # primary abstract only
            year = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", art, flags=re.S)
            clean = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()
            got[pm] = {"title": clean(title.group(1) if title else ""),
                       "abstract": clean(" ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>",
                                                           ab.group(1), flags=re.S)) if ab else ""),
                       "year": year.group(1) if year else None}
        json.dump(got, open(cp, "w")); out.update(got); time.sleep(0.4)
    return out

def main():
    cotc = load("frames/cotc.json")["trials"]
    pmf = load("frames/pubmed_companion.json")
    frame = [("COTC:" + t["trial_id"], "cotc") for t in cotc] + [("PMID:" + p, "pubmed") for p in pmf["pmids"]]
    random.Random(SEED).shuffle(frame)
    cotc_by = {"COTC:" + t["trial_id"]: t for t in cotc}
    out = load("pilot/screen.json")
    t = tier("pilot")
    screened = 0
    while True:
        qualifying = [k for k, v in out.items() if v.get("qualifies")]
        if len(qualifying) >= TARGET_QUALIFYING or screened >= MAX_SCREEN or screened >= len(frame):
            break
        batch = [k for k, _ in frame[screened:screened + BATCH]]
        screened += len(batch)
        abstracts = efetch_abstracts([k[5:] for k in batch if k.startswith("PMID:")])
        recs = {}
        for k in batch:
            if k.startswith("COTC:"):
                c = cotc_by[k]
                recs[k] = {"title": c["title"], "text": f"{c['title']}\n{c['purpose']}\nPublications: {'; '.join(c['publications'])}"}
            else:
                a = abstracts.get(k[5:], {})
                recs[k] = {"title": a.get("title", ""), "year": a.get("year"),
                           "text": f"{a.get('title','')}\n{a.get('abstract','')}"}
        todo = [k for k in batch if k not in out]
        res = {}
        for role in ("A", "B"):
            model = LADDER[t][role]
            res[role] = pmap(lambda k: ask(model, SYSTEM, recs[k]["text"], SCHEMA, max_tokens=8000)[0],
                             todo, label=f"pilot-screen-{role}")
        for k in todo:
            a, b = res["A"][k], res["B"][k]
            rec = {"id": k, "order": screened, "title": recs[k]["title"], "year": recs[k].get("year"),
                   "has_text": len(recs[k]["text"]) > 200, "A": a, "B": b, "models": LADDER[t], "tier": t}
            def q(x):
                return ("error" not in x and x["intervention_study"] and x["spontaneous_disease"] == "yes"
                        and x["species"] in ("dog", "cat", "dog-and-cat")
                        and x["agent_type"] in ("small-molecule", "biologic", "cell-or-gene-therapy", "vaccine"))
            qa, qb = q(a), q(b)
            rec["qualifies"] = qa and qb
            rec["flag"] = None if qa == qb else "models disagree on qualification"
            out[k] = rec
        save(out, "pilot/screen.json")
        print(f"screened {screened}: qualifying {sum(1 for v in out.values() if v['qualifies'])}, "
              f"disagreements {sum(1 for v in out.values() if v['flag'])}")
    print(f"done. ${COST['usd']:.3f}")

if __name__ == "__main__":
    main()
