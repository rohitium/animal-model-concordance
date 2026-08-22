"""Question-driven extraction from the full-text PDF of each study.

Replaces bottom-up extraction of every number a paper prints. Papers report numbers for
their own purposes; harvesting them wholesale produced twelve NPV rows for organ
subcategories and a leaderboard of incommensurable metrics. Here we decide what we need
to know and ask each PDF those questions.

The PDF goes to the model directly (OpenRouter native file parsing), so tables and
figures are visible rather than flattened to text.
"""
import sys, os, json, base64, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MODEL = "google/gemini-2.5-flash"

COMP = {"type":"object","additionalProperties":False,"properties":{
  "what_compared":{"type":"string"},
  "animal_species":{"type":"array","items":{"type":"string"}},
  "value":{"type":["number","null"]},
  "unit":{"type":"string","enum":["percent","proportion_0_1","correlation","fold","ratio","count","other"]},
  "statistic":{"type":"string"},
  "n":{"type":["integer","null"]},
  "n_counts":{"type":["string","null"]},
  "source_location":{"type":"string"},
  "verbatim":{"type":"string"}},
 "required":["what_compared","animal_species","value","unit","statistic","n","n_counts",
             "source_location","verbatim"]}

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "animal_side":{"type":"object","additionalProperties":False,"properties":{
   "species":{"type":"array","items":{"type":"string"}},
   "grouped_labels":{"type":"array","items":{"type":"string"}},
   "strain_or_model":{"type":["string","null"]},
   "how_disease_arose":{"type":["string","null"]},
   "n":{"type":["integer","null"]},"n_counts":{"type":["string","null"]}},
   "required":["species","grouped_labels","strain_or_model","how_disease_arose","n","n_counts"]},
 "human_side":{"type":"object","additionalProperties":False,"properties":{
   "population":{"type":["string","null"]},"disease":{"type":["string","null"]},
   "stage_or_setting":{"type":["string","null"]},"trial_phase":{"type":["string","null"]},
   "n":{"type":["integer","null"]},"n_counts":{"type":["string","null"]}},
   "required":["population","disease","stage_or_setting","trial_phase","n","n_counts"]},
 "animal_endpoint":{"type":["string","null"]},
 "human_endpoint":{"type":["string","null"]},
 "endpoint_match":{"type":"string","enum":["identical","analogous","non-analogous","not-stated"]},
 "comparisons":{"type":"array","items":COMP},
 "verdict":{"type":"string","enum":["supports","partly-supports","does-not-support","no-data"]},
 "verdict_basis":{"type":"string"},
 "discordance_direction":{"type":"string","enum":[
   "animal-positive-human-negative","animal-negative-human-positive","both","none-reported","not-applicable"]},
 "discordance_note":{"type":["string","null"]},
 "base_rate_caveat":{"type":["string","null"]},
 "scope":{"type":["string","null"]}},
 "required":["animal_side","human_side","animal_endpoint","human_endpoint","endpoint_match",
   "comparisons","verdict","verdict_basis","discordance_direction","discordance_note",
   "base_rate_caveat","scope"]}

PROMPT = """You are reading a scientific paper to determine what its DATA say about whether
results in non-human animals correspond to results in humans.

IGNORE the authors' characterisations. Abstracts and discussions editorialise ("animal
models are essential", "poor translatability"). Read the RESULTS, TABLES and FIGURES and
report what was measured.

Rules that matter:
1. NEVER expand a grouped result onto individual species. If the paper reports "43% of
   rodent studies", record the group label "rodent", NOT mouse/rat/guinea pig separately.
   Put such labels in grouped_labels and leave species empty for them. Only list a species
   in `species` when the paper reports that species separately.
2. Record each value in the unit AS PRINTED. A robustness score of 0.85 on a 0-1 scale is
   unit "proportion_0_1", NOT "percent". 85% is unit "percent" with value 85.
3. source_location: where the number came from ("Table 3", "Figure 2", "Results, p4").
4. comparisons: EVERY quantitative animal-vs-human comparison in the results/tables/figures.
   If the paper reports the same quantity broken down many ways (e.g. NPV per organ system
   per species), give the OVERALL figure plus the per-species figures, not every subcategory.
   Name each organism the way the paper does; do not invent finer species than it reports.
5. verdict: judge from the DATA, not the authors' framing.
   - supports: the animal results corresponded well to the human results
   - partly-supports: mixed, or good for some species/endpoints and not others
   - does-not-support: the animal results did not correspond
   - no-data: the paper reports no animal-human comparison
   verdict_basis: cite the specific numbers, and no adjectives.
6. base_rate_caveat: state anything that would make a figure misleading if quoted alone.
   Negative predictive value is usually high simply because most findings are negative;
   say so when it applies. Also note small n, selected samples, or a denominator that
   excludes failures.
7. If the paper is a review reporting other studies' numbers, that is fine; record them
   with source_location naming the table or section.

Answer with JSON only."""

DB=json.load(open(J("data","db","studies.json")))
FTS=json.load(open(J("data","raw","fulltext_status.json")))
outp=J("data","db","study_answers.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}
targets=[pm for pm,v in DB.items() if v.get("eligible") and (FTS.get(pm) or {}).get("pdf")]
print(f"{len(targets)} eligible studies with a PDF")

def ask(pm):
    pdf=J(FTS[pm]["pdf"])
    b=base64.b64encode(open(pdf,"rb").read()).decode()
    body={"model":MODEL,"messages":[
        {"role":"system","content":PROMPT},
        {"role":"user","content":[
          {"type":"text","text":f'TITLE: {DB[pm].get("title","")}\nPMID: {pm}\n\nAnswer the questions for this paper.'},
          {"type":"file","file":{"filename":f"{pm}.pdf","file_data":f"data:application/pdf;base64,{b}"}}]}],
      "plugins":[{"id":"file-parser","pdf":{"engine":"native"}}],
      "response_format":{"type":"json_schema","json_schema":{"name":"study","strict":True,"schema":SCHEMA}},
      "max_tokens":60000,"temperature":0}
    req=urllib.request.Request(orr.URL,data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {orr._key()}","Content-Type":"application/json",
                 "HTTP-Referer":"https://github.com/animal-model-concordance","X-Title":"amc"})
    with urllib.request.urlopen(req,timeout=300) as r:
        return json.loads(r.read().decode())

cost,errs=0.0,0
for i,pm in enumerate(targets,1):
    if pm in out and "error" not in out[pm]: continue
    try:
        d=ask(pm)
        c=d["choices"][0]["message"].get("content")
        if not c: raise RuntimeError("null content")
        out[pm]=json.loads(c); cost+=(d.get("usage") or {}).get("cost",0)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:200]}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.3)
    if i%10==0: print(f"  {i}/{len(targets)} cost=${cost:.3f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
import collections
print(f"\nanswered {len(ok)}/{len(targets)}  errors={errs}  cost=${cost:.3f}")
print("verdicts:", dict(collections.Counter(v["verdict"] for v in ok.values())))
print("comparisons:", sum(len(v.get("comparisons") or []) for v in ok.values()))
print("with base-rate caveat:", sum(1 for v in ok.values() if v.get("base_rate_caveat")))
