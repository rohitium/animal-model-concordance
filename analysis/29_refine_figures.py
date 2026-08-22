"""Rewrite each concordance figure as a precise, self-contained statement.

The extractor split paired contrasts into unpaired fragments. One sentence in a
Parkinson's review reports improvement in 90% of mouse, 95% of rat and 67-80% of NHP
studies "however, only 32% of human trials showed any clinical improvement" -- and each
percentage became its own row reading "studies on rats showing improvement for
potentially disease-modifying interventions". True, but meaningless alone: no
denominator, no comparator, no indication of what it is evidence FOR.

Each figure is rewritten to state what the number is a proportion OF, in which
population, and against what human value where the source gives one. Figures that
cannot be made specific from the text are dropped rather than displayed vaguely."""
import sys, os, json, re, time, subprocess, html as _html
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
CONC = ("animal-vs-human", "animal-result-by-human-outcome")

SCHEMA={"type":"object","additionalProperties":False,"properties":{
 "items":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
   "index":{"type":"integer"},
   "keep":{"type":"boolean"},
   "drop_reason":{"type":["string","null"]},
   "precise":{"type":"string"},
   "denominator":{"type":["string","null"]},
   "human_counterpart_value":{"type":["number","null"]},
   "human_counterpart_text":{"type":["string","null"]}},
   "required":["index","keep","drop_reason","precise","denominator",
               "human_counterpart_value","human_counterpart_text"]}}},
 "required":["items"]}

PROMPT = """Rewrite each figure as ONE precise sentence a reader can understand with no
other context.

`precise` MUST state:
  - what the number is a proportion or measure OF (its denominator or population),
  - the specific animal(s) and the specific disease or endpoint,
  - what it is being compared against.
Write the number itself into the sentence.

Good:  "95% of 266 preclinical studies of disease-modifying interventions for Parkinson's
        disease in rats reported improvement, against 32% of the corresponding human
        trials showing any clinical improvement."
Bad:   "studies on rats showing improvement for potentially disease-modifying interventions"
        (no denominator, no comparator, no disease named in context)

`denominator`: what the figure is out of, e.g. "266 preclinical studies", "150 compounds".
`human_counterpart_value` / `human_counterpart_text`: if the SAME passage gives the human
figure this animal figure is contrasted with, report it. Otherwise null.

Set keep=false, with a drop_reason, when the text does not let you name a denominator or a
comparison — a vague figure is worse than none. Never invent. JSON only."""

DB=json.load(open(J("data","db","studies.json")))
MS=json.load(open(J("data","db","measurements.json")))
SC=json.load(open(J("data","db","measurement_scope.json")))
FTS=json.load(open(J("data","raw","fulltext_status.json")))
outp=J("data","db","figure_refined.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}

def text(pm):
    s=FTS.get(pm,{})
    if s.get("xml"):
        t=open(J(s["xml"]),encoding="utf-8",errors="replace").read()
        b=re.search(r"<body[^>]*>(.*?)</body>",t,re.S)
        return re.sub(r"\s+"," ",_html.unescape(re.sub(r"<[^>]+>"," ",b.group(1) if b else t))).strip()[:60000]
    if s.get("pdf"):
        try:
            r=subprocess.run(["pdftotext","-q",J(s["pdf"]),"-"],capture_output=True,timeout=120)
            return re.sub(r"\s+"," ",r.stdout.decode("utf-8","replace")).strip()[:60000]
        except Exception: return ""
    return ""

targets=[]
for pm,m in MS.items():
    if "error" in m: continue
    sc=SC.get(pm) or {}
    idx=[i for i in range(len(m.get("measurements") or [])) if sc.get(str(i)) in CONC]
    if idx: targets.append((pm,idx))
print(f"{len(targets)} studies, {sum(len(i) for _,i in targets)} concordance figures")

cost,errs=0.0,0
for k,(pm,idx) in enumerate(targets,1):
    if pm in out and "error" not in out[pm]: continue
    mm=MS[pm]["measurements"]
    lines=[f'{i}. {mm[i]["statistic"]} = {mm[i]["value"]} {mm[i]["unit"]} | measures: {mm[i]["measures"]} | '
           f'compared: {mm[i]["compared"]} | quote: {mm[i]["verbatim"][:240]}' for i in idx]
    try:
        d=orr.chat("google/gemini-2.5-flash-lite",
          [{"role":"system","content":PROMPT},
           {"role":"user","content":f'STUDY: {DB[pm].get("title","")}\n\nFIGURES:\n'+"\n".join(lines)
                                    +f'\n\nFULL TEXT:\n{text(pm)[:50000]}'}],
          schema=SCHEMA,max_tokens=12000)
        c=orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm]={str(it["index"]):it for it in json.loads(c)["items"]}
        cost+=orr.usd(d)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:150]}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.15)
    if k%15==0: print(f"  {k}/{len(targets)} cost=${cost:.4f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
items=[it for v in ok.values() for it in v.values()]
kept=[it for it in items if it.get("keep")]
print(f"\nrefined {len(items)} figures; keep {len(kept)}; dropped {len(items)-len(kept)}; "
      f"errors={errs}; cost=${cost:.4f}")
print("with denominator:", sum(1 for it in kept if it.get("denominator")))
print("with human counterpart:", sum(1 for it in kept if it.get("human_counterpart_value") is not None))
