"""Re-screen the slice against rubric r3, which requires the index test to be a
whole live non-human animal.

The earlier rubric restated PLAN 6.3's exclusion of in vitro / in silico work too
weakly, and the model_type vocabulary made it worse by offering
'in-vitro-or-in-silico-comparator' as if it were a kind of animal model. This pass
decides each study on what its PREDICTOR actually is."""
import sys, os, json, re, time, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
from rubric import RUBRIC, RUBRIC_VERSION
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "index_test":{"type":"string","enum":[
   "whole-animal-in-vivo","in-vitro-only","in-silico-only","human-only","mixed-animal-and-nonanimal","unclear-from-text"]},
 "index_test_evidence":{"type":"string"},
 "decision":{"type":"string","enum":["include","exclude"]},
 "reason":{"type":"string"}},
 "required":["index_test","index_test_evidence","decision","reason"]}

PROMPT = f"""{RUBRIC}

First identify what this study uses to PREDICT the human outcome (the index test):
- whole-animal-in-vivo: living non-human animals
- in-vitro-only: cells, organoids, organ-on-chip, isolated channels/tissues, 3D cultures
- in-silico-only: QSAR, PBPK, AI/ML, mathematical models
- human-only: only human data
- mixed-animal-and-nonanimal: BOTH whole animals and non-animal methods
- unclear-from-text

Quote the sentence that shows this. Then decide include/exclude.
Exclude in-vitro-only, in-silico-only and human-only. Include whole-animal-in-vivo
and mixed-animal-and-nonanimal (if it otherwise meets the rule).
Answer with JSON only."""

db=json.load(open(J("data","db","studies.json")))
absd=json.load(open(J("data","screening","slice_abstracts.json")))
fts=json.load(open(J("data","raw","fulltext_status.json")))
meta=json.load(open(J("data","db","metadata.json")))
outp=J("data","db","animal_screen.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}

def text(pm):
    s=fts.get(pm,{})
    if s.get("xml"):
        t=open(J(s["xml"]),encoding="utf-8",errors="replace").read()
        b=re.search(r"<body[^>]*>(.*?)</body>",t,re.S)
        return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",b.group(1) if b else t)).strip()[:60000],"fulltext"
    if s.get("pdf"):
        try:
            r=subprocess.run(["pdftotext","-q",J(s["pdf"]),"-"],capture_output=True,timeout=120)
            t=re.sub(r"\s+"," ",r.stdout.decode("utf-8","replace")).strip()
            if len(t)>1500: return t[:60000],"fulltext"
        except Exception: pass
    a=(absd.get(pm,{}).get("abstract") or (meta.get(pm) or {}).get("abstract") or "").strip()
    return a,("abstract" if a else "title-only")

cost,errs=0.0,0
for i,pm in enumerate(db,1):
    if pm in out and "error" not in out[pm]: continue
    t,tier=text(pm)
    title=db[pm].get("title") or (meta.get(pm) or {}).get("title") or ""
    try:
        d=orr.chat("google/gemini-2.5-flash-lite",
          [{"role":"system","content":PROMPT},
           {"role":"user","content":f"TITLE: {title}\n\nTEXT ({tier}):\n{t or '(none)'}"}],
          schema=SCHEMA,max_tokens=900)
        c=orr.content(d)
        if not c: raise RuntimeError("null content")
        r={**json.loads(c),"tier":tier,"rubric_version":RUBRIC_VERSION}
        if tier=="title-only" and r["decision"]=="exclude":
            r["decision_model"]="exclude"; r["decision"]="include"; r["auto_advanced"]=True
            r["reason"]="No abstract; cannot screen on title alone (protocol auto-advance). "+r["reason"][:160]
        out[pm]=r; cost+=orr.usd(d)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:160],"tier":tier}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.15)
    if i%25==0: print(f"  {i}/{len(db)} cost=${cost:.4f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
import collections
print(f"\nscreened {len(ok)}  errors={errs}  cost=${cost:.4f}")
print("index_test:",dict(collections.Counter(v["index_test"] for v in ok.values())))
exc=[k for k,v in ok.items() if v["decision"]=="exclude"]
print(f"excluded: {len(exc)}  remaining: {len(ok)-len(exc)}")
for k in sorted(exc,key=lambda x:-(db[x].get('cited_by') or 0))[:25]:
    print(f"  {db[k].get('cited_by'):>4} [{ok[k]['index_test']:28s}] {db[k]['title'][:62]}")
