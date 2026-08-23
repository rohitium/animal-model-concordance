"""Separate a paper's OWN results from figures it quotes from other work.

Martic-Kehl 2012 reports "only three interventions ... out of 494" — but that is Sena
and colleagues' result, quoted in this paper's introduction. Treating it as this study's
finding is wrong twice over: the conditions that produced it are not this paper's, and if
the original is also in the corpus the same number is counted twice.

Each figure is classified as the study's own result, a figure cited from another study, or
a figure the study re-analysed. Cited figures stay visible on the study page, attributed to
their source, but do not count as that study's evidence."""
import sys, os, json, time, urllib.request, collections, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT=os.path.join(os.path.dirname(__file__),".."); J=lambda *p: os.path.join(ROOT,*p)
MODEL="openai/gpt-5-mini"

SCHEMA={"type":"object","additionalProperties":False,"properties":{
 "items":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
   "index":{"type":"integer"},
   "provenance":{"type":"string","enum":["own-result","cited-from-other-study","reanalysis-of-other-data","unclear"]},
   "cited_source":{"type":["string","null"]},
   "evidence":{"type":"string"}},
   "required":["index","provenance","cited_source","evidence"]}}},
 "required":["items"]}

PROMPT="""For each numbered figure from one paper, decide whether the number is that paper's
OWN result or a figure it quotes from other work.

- own-result: the authors generated or computed it in this paper
- cited-from-other-study: the number comes from another publication, quoted or summarised
  here. Signals: "X and colleagues reported", "a previous analysis found", a citation
  marker beside the number, or the figure appearing in the Introduction/Background while
  setting up the problem.
- reanalysis-of-other-data: the authors re-computed something from data others collected
  (systematic reviews and meta-analyses of published studies belong here; the pooling is
  theirs even though the inputs are not)
- unclear: the text does not let you tell

`cited_source`: the study or authors credited, if named. `evidence`: the phrase that decided it.
JSON only."""

ANS=json.load(open(J("data","db","study_answers.json")))
DB=json.load(open(J("data","db","studies.json")))
OK={k:v for k,v in ANS.items() if "error" not in v and DB.get(k,{}).get("eligible")}
outp=J("data","db","figure_provenance.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}
todo=[pm for pm in OK if (OK[pm].get("comparisons") and
      (pm not in out or "error" in out[pm]))]
print(f"{len(todo)} studies to classify")
lock=threading.Lock(); cost=0.0; errs=0

def work(pm):
    cs=OK[pm]["comparisons"]
    lines=[f'{i}. {c["statistic"]} = {c["value"]} {c["unit"]} | {c["what_compared"]} '
           f'| location: {c.get("source_location")} | quote: "{(c.get("verbatim") or "")[:240]}"'
           for i,c in enumerate(cs)]
    body={"model":MODEL,"messages":[{"role":"system","content":PROMPT},
      {"role":"user","content":f'PAPER: {DB[pm].get("title","")}\n\nFIGURES:\n'+"\n".join(lines)}],
      "response_format":{"type":"json_schema","json_schema":{"name":"prov","strict":True,"schema":SCHEMA}},
      "max_tokens":9000}
    for a in range(3):
        try:
            req=urllib.request.Request(orr.URL,data=json.dumps(body).encode(),
                headers={"Authorization":f"Bearer {orr._key()}","Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(req,timeout=300).read().decode())
            c=d["choices"][0]["message"].get("content")
            if not c: raise RuntimeError("null content")
            return pm,{str(it["index"]):it for it in json.loads(c)["items"]},(d.get("usage") or {}).get("cost",0)
        except Exception as ex:
            if a==2: return pm,{"error":str(ex)[:160]},0.0
            time.sleep(2*(a+1))

done=0
with ThreadPoolExecutor(max_workers=8) as ex:
    for fut in as_completed([ex.submit(work,pm) for pm in todo]):
        pm,res,c=fut.result()
        with lock:
            out[pm]=res
            if "error" in res: errs+=1
            cost+=c; done+=1
            json.dump(out,open(outp,"w"),indent=1)
            if done%10==0: print(f"  {done}/{len(todo)} cost=${cost:.3f} errs={errs}")

tally=collections.Counter()
for pm,v in out.items():
    if "error" in v: continue
    for it in v.values(): tally[it["provenance"]]+=1
print(f"\nclassified {len([v for v in out.values() if 'error' not in v])} studies, errors={errs}, cost=${cost:.3f}")
print("provenance:", dict(tally))
