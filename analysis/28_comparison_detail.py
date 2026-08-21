"""For each animal-vs-human figure, extract WHO was compared with WHOM.

Two problems this fixes.

1. Bloat. The scoper marked anything mentioning both preclinical and clinical work as
   animal-vs-human, including "$330,000 to characterise a single drug" -- a budget
   figure, not a concordance measurement. Each figure is now tested for whether it
   actually quantifies correspondence between animal and human results.

2. Vacuous detail. "species: animal, human" is useless. The point of the review is which
   animal (species, strain, how the disease was produced) was compared against which
   humans (population, disease, endpoint). That pairing is extracted here.
"""
import sys, os, json, re, time, subprocess, html as _html
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)

SIDE = {"type":"object","additionalProperties":False,"properties":{
  "species":{"type":"array","items":{"type":"string"}},
  "strain_or_model":{"type":["string","null"]},
  "how_disease_arose":{"type":["string","null"]},
  "n":{"type":["integer","null"]},
  "n_unit":{"type":["string","null"]},
  "endpoint":{"type":["string","null"]},
  "sex":{"type":["string","null"]},
  "age_or_stage":{"type":["string","null"]}},
 "required":["species","strain_or_model","how_disease_arose","n","n_unit","endpoint","sex","age_or_stage"]}
HSIDE = {"type":"object","additionalProperties":False,"properties":{
  "population":{"type":["string","null"]},
  "disease":{"type":["string","null"]},
  "n":{"type":["integer","null"]},
  "n_unit":{"type":["string","null"]},
  "endpoint":{"type":["string","null"]},
  "sex":{"type":["string","null"]},
  "age_or_stage":{"type":["string","null"]},
  "trial_phase":{"type":["string","null"]}},
 "required":["population","disease","n","n_unit","endpoint","sex","age_or_stage","trial_phase"]}

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "items":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
   "index":{"type":"integer"},
   "is_concordance_figure":{"type":"boolean"},
   "why_not":{"type":["string","null"]},
   "animal":SIDE,"human":HSIDE,
   "endpoint_match":{"type":"string","enum":["identical","analogous","non-analogous","not-stated"]}},
   "required":["index","is_concordance_figure","why_not","animal","human","endpoint_match"]}}},
 "required":["items"]}

PROMPT = """For each numbered figure, do two things.

FIRST decide `is_concordance_figure`: does this number quantify how well an animal
result corresponds to a human result (agreement, concordance, correlation, predictive
accuracy, translation/success rate, or a side-by-side effect comparison)?

Set it FALSE for anything that is not such a quantity, even if the sentence mentions
both animals and humans — costs and budgets, durations and timelines, numbers of
publications or studies screened, funding amounts, market sizes, counts of compounds
merely tested. Give a short `why_not` when false.

SECOND, when TRUE, describe the two sides ACTUALLY COMPARED, using only the text:
- animal: species (e.g. "rat", not "animal"); strain or model name (SOD1-G93A, Göttingen
  minipig, C57BL/6) if named; how the disease arose (chemically induced, surgical,
  transgenic, spontaneous/naturally occurring, infection challenge); n and what n counts;
  the endpoint measured; sex; age or disease stage.
- human: population (e.g. "patients with acute ischaemic stroke", "healthy volunteers");
  disease; n and what n counts; endpoint; sex; age or stage; trial phase.
- endpoint_match: identical (same measure both sides), analogous (corresponding but not
  identical, e.g. infarct volume vs mRS), non-analogous, or not-stated.

Use null / empty array where the text does not say. Never infer. Never write "animal" or
"human" as a species. JSON only."""

DB=json.load(open(J("data","db","studies.json")))
MS=json.load(open(J("data","db","measurements.json")))
SC=json.load(open(J("data","db","measurement_scope.json")))
FTS=json.load(open(J("data","raw","fulltext_status.json")))
outp=J("data","db","comparison_detail.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}

def text(pm):
    s=FTS.get(pm,{})
    if s.get("xml"):
        t=open(J(s["xml"]),encoding="utf-8",errors="replace").read()
        b=re.search(r"<body[^>]*>(.*?)</body>",t,re.S)
        return re.sub(r"\s+"," ",_html.unescape(re.sub(r"<[^>]+>"," ",b.group(1) if b else t))).strip()[:70000]
    if s.get("pdf"):
        try:
            r=subprocess.run(["pdftotext","-q",J(s["pdf"]),"-"],capture_output=True,timeout=120)
            return re.sub(r"\s+"," ",r.stdout.decode("utf-8","replace")).strip()[:70000]
        except Exception: return ""
    return ""

targets=[]
for pm,m in MS.items():
    if "error" in m: continue
    sc=SC.get(pm) or {}
    idx=[i for i in range(len(m.get("measurements") or [])) if sc.get(str(i))=="animal-vs-human"]
    if idx: targets.append((pm,idx))
print(f"{len(targets)} studies with animal-vs-human figures")

cost,errs=0.0,0
for k,(pm,idx) in enumerate(targets,1):
    if pm in out and "error" not in out[pm]: continue
    mm=MS[pm]["measurements"]
    lines=[f'{i}. {mm[i]["statistic"]} = {mm[i]["value"]} {mm[i]["unit"]} | measures: {mm[i]["measures"]} | '
           f'compared: {mm[i]["compared"]} | quote: {mm[i]["verbatim"][:200]}' for i in idx]
    try:
        d=orr.chat("google/gemini-2.5-flash-lite",
          [{"role":"system","content":PROMPT},
           {"role":"user","content":f'STUDY: {DB[pm].get("title","")}\n\n'
                                    f'FIGURES:\n'+"\n".join(lines)+
                                    f'\n\nFULL TEXT (for context):\n{text(pm)[:60000]}'}],
          schema=SCHEMA,max_tokens=12000)
        c=orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm]={str(it["index"]):it for it in json.loads(c)["items"]}
        cost+=orr.usd(d)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:160]}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.15)
    if k%15==0: print(f"  {k}/{len(targets)} cost=${cost:.4f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
items=[it for v in ok.values() for it in v.values()]
keep=[it for it in items if it.get("is_concordance_figure")]
import collections
print(f"\nstudies {len(ok)}  figures {len(items)}  concordance figures {len(keep)}  "
      f"dropped as not-concordance {len(items)-len(keep)}  errors={errs}  cost=${cost:.4f}")
sp=collections.Counter(s for it in keep for s in (it["animal"]["species"] or []))
print("animal species named:", dict(sp))
print("with strain/model named:", sum(1 for it in keep if it["animal"]["strain_or_model"]))
print("with human population named:", sum(1 for it in keep if it["human"]["population"]))
print("endpoint_match:", dict(collections.Counter(it["endpoint_match"] for it in keep)))
