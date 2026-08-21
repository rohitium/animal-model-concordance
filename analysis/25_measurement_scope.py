"""Flag each individual measurement as animal-vs-human or not.

r4 judged whole studies. But an included study reports many figures, and most are not
animal-vs-human: inter-rater agreement between data extractors, zebrafish-vs-mammal
comparisons, within-species contrasts, gene counts. Showing those on a findings page
about animal-human concordance is simply wrong, so each figure is scoped individually."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)

SCHEMA={"type":"object","additionalProperties":False,"properties":{
 "scopes":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
   "index":{"type":"integer"},
   "scope":{"type":"string","enum":[
     "animal-vs-human","within-animal","within-human","animal-vs-nonanimal",
     "process-or-methodology","descriptive-only"]}},
   "required":["index","scope"]}}},
 "required":["scopes"]}

PROMPT="""Classify each numbered measurement by WHAT IT COMPARES.

- animal-vs-human: one side is a result in a non-human animal, the other a human result.
  (e.g. animal toxicity vs human adverse events; mouse gene expression vs human patients;
  xenograft response vs the patient's response; animal QT vs clinical torsades)
- within-animal: both sides are non-human animals, INCLUDING one species vs another
  (zebrafish vs mammal, rat vs rabbit), or diseased vs healthy animals, or treated vs sham
- within-human: both sides are human
- animal-vs-nonanimal: animal compared with an in vitro or in silico method, no human side
- process-or-methodology: about the conduct of research, not about biology
  (inter-rater agreement between data extractors, reporting-quality scores, risk-of-bias
  proportions, share of studies doing X, publication counts)
- descriptive-only: a bare count or magnitude with no comparison at all
  (e.g. "4418 differentially expressed genes", "n=52 drugs studied")

Judge only from the text given. Return one entry per index. JSON only."""

MS=json.load(open(J("data","db","measurements.json")))
DB=json.load(open(J("data","db","studies.json")))
outp=J("data","db","measurement_scope.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}
targets=[pm for pm in DB if (MS.get(pm) or {}).get("measurements")]
print(f"scoping measurements for {len(targets)} studies")

cost,errs=0.0,0
for i,pm in enumerate(targets,1):
    if pm in out and "error" not in out[pm]: continue
    mm=MS[pm]["measurements"]
    lines=[f'{k}. {x["statistic"]} = {x["value"]} {x["unit"]} | measures: {x["measures"]} | '
           f'compared: {x["compared"]} | species: {",".join(x.get("species") or []) or "none"}'
           for k,x in enumerate(mm)]
    try:
        d=orr.chat("google/gemini-2.5-flash-lite",
          [{"role":"system","content":PROMPT},
           {"role":"user","content":f'STUDY: {DB[pm].get("title","")}\n\nMEASUREMENTS:\n'+"\n".join(lines)}],
          schema=SCHEMA,max_tokens=4000)
        c=orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm]={s["index"]:s["scope"] for s in json.loads(c)["scopes"]}
        cost+=orr.usd(d)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:150]}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.15)
    if i%20==0: print(f"  {i}/{len(targets)} cost=${cost:.4f} errs={errs}")

import collections
allsc=collections.Counter()
for pm,v in out.items():
    if "error" in v: continue
    allsc.update(v.values())
print(f"\nscoped {len([v for v in out.values() if 'error' not in v])} studies, errors={errs}, cost=${cost:.4f}")
print(dict(allsc))
