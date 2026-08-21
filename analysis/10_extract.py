"""Select the pilot slice from screened includes, then extract structured records.

EXTRACTION SOURCE IS THE ABSTRACT ONLY. Full texts are behind authentication we do
not have, so 2x2 tables, per-species breakdowns and endpoint detail are frequently
absent. Every record carries extraction_source='abstract' and unpopulated fields are
explicit nulls, never silently omitted."""
import sys, os, json, math, time, collections
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
from rubric import RUBRIC_VERSION
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, "data", *p)
MODEL = "google/gemini-2.5-flash-lite"
TARGET = 100

cands = json.load(open(J("screening", "slice_candidates.json")))
absd  = json.load(open(J("screening", "slice_abstracts.json")))
dec   = json.load(open(J("screening", "slice_decisions.json")))
inc = [p for p, d in dec.items() if d["decision"] == "include"]
print(f"includes available: {len(inc)}")

def score(p):
    c = cands[p]
    auth = math.log1p(c["cited_by"]) / math.log1p(3862)
    rec = max(0.0, min(1.0, (c["year"] - 1995) / 31)) if c["year"] else 0.3
    bonus = 0.15 if "anchor" in c["sources"] else (0.08 if "citation_hub" in c["sources"] else 0)
    return 0.5 * auth + 0.5 * rec + bonus

by_strand = collections.defaultdict(list)
for p in inc:
    for s in cands[p]["sources"]:
        by_strand[s].append(p)
sel, seen = [], set()
quota = max(1, TARGET // max(1, len(by_strand)))
for s in sorted(by_strand):                       # diversity first
    got = 0
    for p in sorted(by_strand[s], key=score, reverse=True):
        if p in seen: continue
        sel.append(p); seen.add(p); got += 1
        if got >= quota: break
for p in sorted(inc, key=score, reverse=True):    # fill by score
    if len(sel) >= TARGET: break
    if p not in seen: sel.append(p); seen.add(p)
print(f"selected: {len(sel)}")

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "arm":{"type":"string","enum":["efficacy","safety","toxicology","veterinary","auxiliary","unclear"]},
 "species":{"type":"array","items":{"type":"string"}},
 "therapeutic_areas":{"type":"array","items":{"type":"string"}},
 "model_type":{"type":"string","enum":["induced","genetic","xenograft","surgical","infection","spontaneous-veterinary","mixed","not-stated"]},
 "concordance_reported":{"type":"boolean"},
 "concordance_metric":{"type":["string","null"]},
 "concordance_value":{"type":["number","null"]},
 "n_pairs":{"type":["integer","null"]},
 "endpoint_class":{"type":"string","enum":["primary-hard","secondary-biomarker","mixed","not-stated"]},
 "study_design":{"type":"string","enum":["systematic-review","meta-analysis","scoping-review","cross-sectional","regulatory-dataset","cohort","primary-research","narrative-review","other"]},
 "key_finding":{"type":"string"},
 "quantitative_claims":{"type":"array","items":{"type":"string"}},
 "evidence_vs_opinion":{"type":"string","enum":["data","opinion"]}},
 "required":["arm","species","therapeutic_areas","model_type","concordance_reported",
   "concordance_metric","concordance_value","n_pairs","endpoint_class","study_design",
   "key_finding","quantitative_claims","evidence_vs_opinion"]}

PROMPT = """Extract structured data from this abstract for a systematic review of
animal-model concordance with human clinical outcomes.

Rules:
- Use ONLY what the abstract states. Never infer, complete, or supply outside knowledge.
- If a field is not stated, use null / "not-stated" / an empty array. Do not guess.
- concordance_value: express as a proportion 0-1 if a concordance/translation/predictive
  rate is stated (e.g. "71%" -> 0.71). null if none is stated.
- quantitative_claims: verbatim numeric statements from the abstract, each a short string.
  Empty array if the abstract contains no numbers.
- key_finding: one sentence, strictly supported by the abstract.
- arm: efficacy | safety (safety pharmacology/adverse events) | toxicology |
  veterinary (naturally occurring disease in client-owned animals) | auxiliary
  (publication bias / attrition base rates) | unclear.
Answer with JSON only."""

out, cost, errs = {}, 0.0, 0
for i, pm in enumerate(sel, 1):
    r = absd.get(pm); c = cands[pm]
    if not r or not r["abstract"]:
        out[pm] = {"pmid": pm, **{k: None for k in ["arm","model_type","endpoint_class"]},
                   "extraction_source": "none", "extraction_status": "no abstract available",
                   "title": c["title"], "journal": c["journal"], "year": c["year"],
                   "cited_by": c["cited_by"], "authors": c["authors"], "sources": c["sources"]}
        continue
    try:
        d = orr.chat(MODEL, [{"role":"system","content":PROMPT},
             {"role":"user","content":f"TITLE: {r['title']}\n\nABSTRACT: {r['abstract'][:4000]}"}],
             schema=SCHEMA, max_tokens=900)
        ct = orr.content(d)
        if not ct: raise RuntimeError("null content")
        out[pm] = {"pmid": pm, **json.loads(ct), "title": r["title"], "journal": c["journal"],
                   "year": c["year"], "cited_by": c["cited_by"], "authors": c["authors"],
                   "sources": c["sources"], "extraction_source": "abstract",
                   "extraction_status": "ok", "rubric_version": RUBRIC_VERSION,
                   "screen_reason": dec[pm].get("reason","")}
        cost += orr.usd(d)
    except Exception as e:
        errs += 1
        out[pm] = {"pmid": pm, "title": r["title"], "journal": c["journal"], "year": c["year"],
                   "cited_by": c["cited_by"], "authors": c["authors"], "sources": c["sources"],
                   "extraction_source": "abstract", "extraction_status": f"error: {str(e)[:120]}"}
    time.sleep(0.15)
    if i % 25 == 0: print(f"  extracted {i}/{len(sel)}  cost=${cost:.4f} errs={errs}")

if errs > 0.10 * len(sel):
    raise SystemExit(f"ABORT: {errs}/{len(sel)} extraction errors (>10%).")
json.dump(out, open(J("db", "studies.json"), "w"), indent=1)
print(f"\nextracted {len(out)}  errors={errs}  cost=${cost:.4f}")
ok = [v for v in out.values() if v.get("extraction_status") == "ok"]
print("arms:", dict(collections.Counter(v.get("arm") for v in ok)))
print("with concordance value:", sum(1 for v in ok if v.get("concordance_value") is not None))
