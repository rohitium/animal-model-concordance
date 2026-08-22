"""Re-classify every study using the best available text, with no escape hatches.

Three problems this fixes:
 1. "unclear"/"unspecified"/"unclassified" buckets. At n=100 these are a dodge --
    but the fix is to supply the MISSING REAL CATEGORIES, not to force guesses.
    A toxicology study that is not disease-specific is 'cross-cutting', not
    'unclear'. A study aggregating rodent vs non-rodent is 'multiple (aggregated)',
    not 'unspecified'. Both are meaningful classifications.
 2. Basic fields (therapeutic area, model type) left empty because the abstract
    omitted them. Full text almost always states them.
 3. Screening rationale judged from the abstract alone. Where full text exists the
    decision is re-made against it, and the rationale records which text was used.

Every classification must carry a verbatim supporting quote, so it is auditable.
"""
import sys, os, json, re, time, html as _html
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
from rubric import RUBRIC, RUBRIC_VERSION
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MODEL = "google/gemini-2.5-flash-lite"

# 'methods-and-bias' was removed: it classified studies by what KIND of study they are,
# while every other arm classifies by WHAT IS BEING PREDICTED. Mixing the two axes made
# the arm incoherent. Its contents split cleanly: studies measuring whether the animal's
# biology resembles human disease biology are their own prediction target
# ('disease-biology'), and translation-rate studies belong to the arm whose findings they
# are counting (usually efficacy).
ARMS = ["efficacy","safety-pharmacology","toxicology","disease-biology","veterinary"]
AREAS = ["oncology","cardiovascular","neurology-stroke","neurodegeneration","psychiatric",
         "sepsis-inflammation","infectious-disease","metabolic","hepatic","renal","respiratory",
         "musculoskeletal","ophthalmology","dermatology","pain","reproductive","haematology",
         "cross-cutting"]
# 'in-vitro-or-in-silico-comparator' was removed: it is not a kind of animal model,
# and offering it as one let non-animal studies present as in-scope (rubric r3).
MODELS = ["induced","genetic","xenograft-pdx","surgical","infection-challenge",
          "spontaneous-veterinary","across-multiple-models","regulatory-dataset"]
SPECIES = ["mouse","rat","dog","cat","pig","rabbit","guinea-pig","hamster","sheep","goat",
           "cattle","horse","chicken","ferret","zebrafish","non-human-primate",
           "multiple-aggregated","not-species-specific"]

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "screen_decision":{"type":"string","enum":["include","exclude"]},
 "screen_rationale":{"type":"string"},
 "arm":{"type":"string","enum":ARMS},
 "arm_evidence":{"type":"string"},
 "therapeutic_areas":{"type":"array","minItems":1,"items":{"type":"string","enum":AREAS}},
 "areas_evidence":{"type":"string"},
 "model_type":{"type":"string","enum":MODELS},
 "model_evidence":{"type":"string"},
 "species":{"type":"array","minItems":1,"items":{"type":"string","enum":SPECIES}},
 "species_evidence":{"type":"string"},
 "endpoint_class":{"type":"string","enum":["primary-hard","secondary-biomarker","mixed"]},
 "endpoint_evidence":{"type":"string"}},
 "required":["screen_decision","screen_rationale","arm","arm_evidence","therapeutic_areas",
   "areas_evidence","model_type","model_evidence","species","species_evidence",
   "endpoint_class","endpoint_evidence"]}

PROMPT = f"""Classify this study for a systematic review of animal-model concordance
with human clinical outcomes. Every category below is a real, meaningful bucket --
there is no "unclear" option, because every study belongs somewhere.

arm (choose exactly one):
- efficacy: does the animal model predict human treatment benefit
- safety-pharmacology: acute functional effects (hERG/QT, CNS, respiratory), human AEs
- toxicology: organ toxicity, genotoxicity, carcinogenicity, reproductive toxicity
- veterinary: naturally occurring disease in client-owned animals
- veterinary: the model is naturally occurring disease in CLIENT-OWNED animals (pet dogs,
  cats, horses) studied in veterinary practice. This describes the MODEL rather than the
  readout, so it TAKES PRECEDENCE: choose it whenever the animals are veterinary patients
  with spontaneous disease, whatever is being measured.
- disease-biology: does the model's BIOLOGY resemble the human disease? No treatment is
  being evaluated. Cross-species comparisons of gene expression, transcriptomes, immune
  signatures, pathology, or molecular mechanism between animal models and human patients.
  (e.g. "do mouse inflammatory responses mimic human ones?")

A study that counts how often findings translate belongs to the arm whose findings it
counts: translation rates for treatment efficacy are efficacy; for organ toxicity,
toxicology. If it genuinely spans several, choose the one carrying most of its data.

therapeutic_areas (one or more): {", ".join(AREAS)}
  Use "cross-cutting" when the study spans diseases rather than addressing one --
  this is a real classification (typical of toxicology and safety pharmacology),
  NOT a way of saying "unknown".

model_type (exactly one): {", ".join(MODELS)}
  "across-multiple-models" for reviews spanning model types;
  "regulatory-dataset" for analyses of FDA/EMA submission data.

species (one or more): {", ".join(SPECIES)}
  Use "multiple-aggregated" ONLY when the study reports species pooled together
  (e.g. "rodent vs non-rodent") without separable per-species results.
  Use "not-species-specific" ONLY for studies about research methodology that do
  not analyse any particular species.
  Otherwise name every species actually analysed.

endpoint_class: primary-hard (mortality, survival, MACE, functional outcome),
  secondary-biomarker (lab values, imaging, gene expression, tumour volume), or mixed.

For each classification give a SHORT VERBATIM QUOTE from the text supporting it
(<200 chars). If the text genuinely does not state something, quote the closest
relevant passage and choose the best-supported category.

Also re-apply the screening rule below to THIS text and give a rationale that cites
what the text actually reports.

--- SCREENING RULE ---
{RUBRIC}
Answer with JSON only."""

db = json.load(open(J("data","db","studies.json")))
absd = json.load(open(J("data","screening","slice_abstracts.json")))
fts = json.load(open(J("data","raw","fulltext_status.json")))
meta = json.load(open(J("data","db","metadata.json")))
outp = J("data","db","classification.json")
out = json.load(open(outp)) if os.path.exists(outp) else {}

def best_text(pm):
    s = fts.get(pm, {})
    if s.get("xml"):
        t = open(J(s["xml"]), encoding="utf-8", errors="replace").read()
        body = re.search(r"<body[^>]*>(.*?)</body>", t, re.S)
        t = body.group(1) if body else t
        t = _html.unescape(re.sub(r"<[^>]+>", " ", t))
        return re.sub(r"\s+", " ", t).strip()[:90000], "fulltext"
    if s.get("pdf"):
        import subprocess
        try:
            r = subprocess.run(["pdftotext","-q",J(s["pdf"]),"-"],capture_output=True,timeout=90)
            t = re.sub(r"\s+"," ",r.stdout.decode("utf-8","replace")).strip()
            if len(t) > 2000: return t[:90000], "fulltext"
        except Exception: pass
    a = absd.get(pm, {})
    m = meta.get(pm, {})
    t = (a.get("abstract") or m.get("abstract") or "").strip()
    return t, ("abstract" if t else "title-only")

cost, errs = 0.0, 0
for i, pm in enumerate(db, 1):
    if pm in out: continue
    txt, tier = best_text(pm)
    title = db[pm].get("title") or (meta.get(pm) or {}).get("title") or ""
    if not txt and not title:
        out[pm] = {"error": "no text available"}; continue
    try:
        d = orr.chat(MODEL, [{"role":"system","content":PROMPT},
            {"role":"user","content":f"TITLE: {title}\n\nTEXT ({tier}):\n{txt or '(no abstract)'}"}],
            schema=SCHEMA, max_tokens=2000)
        c = orr.content(d)
        if not c: raise RuntimeError("null content")
        r = {**json.loads(c), "source_tier": tier, "rubric_version": RUBRIC_VERSION}
        # PROTOCOL RULE (docs/limitations.md L13): a record with no abstract cannot
        # be screened on its title. Excluding one is a protocol violation -- it
        # discards exactly the abstract-less landmark papers Phase 1 identified
        # (Hackam 2006 carries original data on 76 animal studies). Force advance.
        if tier == "title-only" and r.get("screen_decision") == "exclude":
            r["screen_decision_model"] = "exclude"
            r["screen_decision"] = "include"
            r["screen_rationale"] = ("No abstract available; cannot be screened on title alone. "
                                     "Auto-advanced to full text per protocol. Model's title-only "
                                     "reading was: " + r.get("screen_rationale","")[:200])
            r["auto_advanced"] = True
        out[pm] = r
        cost += orr.usd(d)
    except Exception as ex:
        errs += 1; out[pm] = {"error": str(ex)[:180], "source_tier": tier}
    json.dump(out, open(outp,"w"), indent=1)
    time.sleep(0.15)
    if i % 25 == 0: print(f"  {i}/{len(db)}  cost=${cost:.4f} errs={errs}")

ok = {k:v for k,v in out.items() if "error" not in v}
print(f"\nclassified {len(ok)}/{len(db)}  errors={errs}  cost=${cost:.4f}")
import collections
for f in ("arm","model_type","endpoint_class","source_tier"):
    print(f"  {f}: {dict(collections.Counter(v.get(f) for v in ok.values()))}")
sp = collections.Counter(s for v in ok.values() for s in (v.get("species") or []))
ar = collections.Counter(a for v in ok.values() for a in (v.get("therapeutic_areas") or []))
print(f"  species: {dict(sp)}")
print(f"  areas: {dict(ar)}")
print(f"  screened include: {sum(1 for v in ok.values() if v.get('screen_decision')=='include')}")
