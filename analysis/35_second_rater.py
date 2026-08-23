"""Independent second verdict, to measure how reliable the verdicts are.

Verdicts carry no numeric thresholds, because the underlying statistics are not
commensurable across studies. That is defensible, but it leaves consistency unmeasured.
A second, independent rater on a different model lets us report an agreement statistic
instead of asking readers to trust a single judgement."""
import sys, os, json, base64, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT=os.path.join(os.path.dirname(__file__),".."); J=lambda *p: os.path.join(ROOT,*p)
MODEL="openai/gpt-5-mini"          # deliberately a different family from the first rater

SCHEMA={"type":"object","additionalProperties":False,"properties":{
 "verdict":{"type":"string","enum":["supports","partly-supports","does-not-support","no-data"]},
 "basis":{"type":"string"},
 "which_numbers":{"type":"array","items":{"type":"string"}}},
 "required":["verdict","basis","which_numbers"]}

PROMPT="""Judge ONLY whether this paper's DATA show that results in non-human animals
corresponded to results in humans.

- supports: the animal results corresponded well to the human results
- partly-supports: mixed — good for some species, endpoints or conditions and not others
- does-not-support: the animal results did not correspond
- no-data: no animal-to-human comparison is reported

Rules:
1. Judge from results, tables and figures. Ignore how the authors characterise their own
   findings in the abstract, introduction or discussion.
2. Negative controls are not failures. If a paper deliberately includes comparisons
   expected to score low in order to validate its metric, exclude them from the judgement
   and say so.
3. Cite the specific numbers you used in `which_numbers`. No adjectives in `basis`.
Answer with JSON only."""

DB=json.load(open(J("data","db","studies.json")))
FTS=json.load(open(J("data","raw","fulltext_status.json")))
ANS=json.load(open(J("data","db","study_answers.json")))
targets=[pm for pm,v in DB.items() if v.get("eligible") and (FTS.get(pm) or {}).get("pdf")
         and "error" not in (ANS.get(pm) or {"error":1})]
outp=J("data","db","second_rater.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}
print(f"{len(targets)} studies to re-rate with {MODEL}")

cost,errs=0.0,0
for i,pm in enumerate(targets,1):
    if pm in out and "error" not in out[pm]: continue
    b=base64.b64encode(open(J(FTS[pm]["pdf"]),"rb").read()).decode()
    body={"model":MODEL,"messages":[{"role":"system","content":PROMPT},
      {"role":"user","content":[
        {"type":"text","text":f'TITLE: {DB[pm].get("title","")}'},
        {"type":"file","file":{"filename":f"{pm}.pdf","file_data":f"data:application/pdf;base64,{b}"}}]}],
      "plugins":[{"id":"file-parser","pdf":{"engine":"native"}}],
      "response_format":{"type":"json_schema","json_schema":{"name":"v","strict":True,"schema":SCHEMA}},
      "max_tokens":8000}
    try:
        req=urllib.request.Request(orr.URL,data=json.dumps(body).encode(),
            headers={"Authorization":f"Bearer {orr._key()}","Content-Type":"application/json"})
        d=json.loads(urllib.request.urlopen(req,timeout=300).read().decode())
        c=d["choices"][0]["message"].get("content")
        if not c: raise RuntimeError("null content")
        out[pm]=json.loads(c); cost+=(d.get("usage") or {}).get("cost",0)
    except Exception as ex:
        errs+=1; out[pm]={"error":str(ex)[:160]}
    json.dump(out,open(outp,"w"),indent=1); time.sleep(0.3)
    if i%10==0: print(f"  {i}/{len(targets)} cost=${cost:.3f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
print(f"\nrated {len(ok)} errors={errs} cost=${cost:.3f}")
