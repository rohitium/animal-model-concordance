"""Rubric r4: the agreement statistic must have a NON-HUMAN ANIMAL on one side and a
HUMAN clinical result on the other.

r3 required the index test to be a live animal but did not say what it must be compared
WITH. That let within-species work through: a paper computing sensitivity/specificity for
diagnosing osteoarthritis in dogs (dogs vs dogs) satisfied "reports a quantitative measure
of agreement" while containing no human data at all.

This pass judges each eligible study against its own extracted measurements, so the
decision rests on what the study actually reports rather than on title keywords."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "has_animal_human_comparison":{"type":"boolean"},
 "evidence":{"type":"string"},
 "comparison_type":{"type":"string","enum":[
   "animal-vs-human","within-animal-only","within-human-only","animal-vs-nonanimal-method","none-found"]},
 "reason":{"type":"string"}},
 "required":["has_animal_human_comparison","evidence","comparison_type","reason"]}

PROMPT = """Decide whether this study reports at least one quantitative comparison in which
ONE SIDE is a non-human animal result and the OTHER SIDE is a human result.

Qualifies (animal-vs-human):
- concordance/agreement between animal toxicity and human adverse events
- correlation of animal and human gene expression, effect sizes, or endpoints
- sensitivity/specificity/PPV of an animal model for predicting a HUMAN outcome
- comparison of animal-model treatment effect against a human clinical trial result
- xenograft or PDX response compared with the response of the corresponding patient

Does NOT qualify:
- within-animal-only: diseased animals vs healthy animals, treated vs sham, strain vs
  strain, one animal group vs another (e.g. sensitivity of a biomarker for diagnosing
  disease IN DOGS)
- within-human-only: human patients vs human controls
- animal-vs-nonanimal-method: animal results compared only with in vitro or in silico
  predictions, with no human outcome

IMPORTANT: the `species` field is often empty even for genuine cross-species work,
because it was not always captured during extraction. An empty or "none" species field
is a GAP IN OUR DATA, never evidence that no animal-human comparison exists. Judge from
the `measures` and `compared` text and the study description. Words like "preclinical",
"nonclinical", "animal model", "xenograft" on one side and "clinical", "patients",
"human" on the other indicate an animal-vs-human comparison even when species is blank.

Quote the measurement that qualifies, or say which kinds were present if none qualify.
Answer with JSON only."""

db = json.load(open(J("data","db","studies.json")))
ms = json.load(open(J("data","db","measurements.json")))
outp = J("data","db","crossspecies.json")
out = json.load(open(outp)) if os.path.exists(outp) else {}
elig = [pm for pm,v in db.items() if v.get("eligible")]
print(f"checking {len(elig)} eligible studies")

cost, errs, skipped = 0.0, 0, 0
for i, pm in enumerate(elig, 1):
    if pm in out and "error" not in out[pm]: continue
    m = ms.get(pm) or {}
    meas = m.get("measurements") or []
    if not meas:
        out[pm] = {"has_animal_human_comparison": None, "comparison_type": "no-measurements",
                   "reason": "No measurements extracted (usually no full text yet); not judged.",
                   "evidence": ""}
        skipped += 1; continue
    lines = [f"- {x['statistic']}: {x['value']} {x['unit']} | measures: {x['measures']} | "
             f"compared: {x['compared']} | species: {','.join(x.get('species') or []) or 'none'}"
             for x in meas[:40]]
    try:
        d = orr.chat("google/gemini-2.5-flash-lite",
            [{"role":"system","content":PROMPT},
             {"role":"user","content":f"TITLE: {db[pm].get('title','')}\n\n"
                                      f"WHAT IT DID: {m.get('what_the_study_did','')}\n\n"
                                      f"MEASUREMENTS:\n" + "\n".join(lines)}],
            schema=SCHEMA, max_tokens=800)
        c = orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm] = json.loads(c); cost += orr.usd(d)
    except Exception as ex:
        errs += 1; out[pm] = {"error": str(ex)[:160]}
    json.dump(out, open(outp,"w"), indent=1); time.sleep(0.15)
    if i % 25 == 0: print(f"  {i}/{len(elig)} cost=${cost:.4f}")

judged = {k:v for k,v in out.items() if "error" not in v and v.get("has_animal_human_comparison") is not None}
fails = [k for k,v in judged.items() if not v["has_animal_human_comparison"]]
import collections
print(f"\njudged {len(judged)}  not-judged (no measurements) {skipped}  errors {errs}  cost=${cost:.4f}")
print("comparison_type:", dict(collections.Counter(v["comparison_type"] for v in judged.values())))
print(f"\nFAIL r4 ({len(fails)}) -- no animal-vs-human comparison:")
for k in sorted(fails, key=lambda x: -(db[x].get("cited_by") or 0)):
    print(f"  {db[k].get('cited_by'):>4} [{out[k]['comparison_type']:26s}] {db[k]['title'][:60]}")
    print(f"       {out[k]['reason'][:150]}")
