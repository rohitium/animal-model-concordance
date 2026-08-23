"""Write a readable synthesis for each row of the main table.

The evidence cells were a mechanical dump of extracted figures: "3-70% proportion —
neuroprotective efficacy in global ischemia models". A reader cannot tell what that range
means, why it is wide, or whether it argues for or against using the model. Worse, the
dump can omit the study's actual finding — the O'Collins row listed six figures without
the one that matters, that drugs reaching the clinic were no more effective in animals
(31.3%) than drugs that never did (24.4%).

This pass gives a capable model everything behind one row and asks for a short, plain
synthesis that states the direction explicitly."""
import sys, os, json, time, collections, re, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr, normalize as N
ROOT=os.path.join(os.path.dirname(__file__),".."); J=lambda *p: os.path.join(ROOT,*p)
MODEL="openai/gpt-5-mini"
load=lambda *p: json.load(open(J(*p)))
DB=load("data","db","studies.json"); META=load("data","db","metadata.json")
ANS=load("data","db","study_answers.json"); CLS=load("data","db","classification.json")
OK={k:v for k,v in ANS.items() if "error" not in v and DB.get(k,{}).get("eligible")}
PDX={k for k,v in DB.items() if k in OK and v.get("substrate")=="human-tissue-in-animal-host"}
CORE={k:v for k,v in OK.items() if k not in PDX}

SCHEMA={"type":"object","additionalProperties":False,"properties":{
 "summary":{"type":"string"},
 "direction":{"type":"string","enum":[
   "evidence favours the model","mixed","evidence does not favour the model","too little evidence"]},
 "key_numbers":{"type":"array","items":{"type":"string"}},
 "why_range_is_wide":{"type":["string","null"]},
 "negative_controls_noted":{"type":["string","null"]}},
 "required":["summary","direction","key_numbers","why_range_is_wide","negative_controls_noted"]}

PROMPT="""You are writing one cell of a table. The row is a MODEL ORGANISM assessed for one
purpose (efficacy, toxicology, safety pharmacology, disease biology, or veterinary). You are
given every quantitative animal-to-human comparison the studies reported for that organism,
each with the sentence it came from, plus each study's verdict and any caveat.

Write `summary`: 2-4 sentences a scientific reader can act on. It must
- lead with what the evidence SHOWS, not with a list of numbers;
- give the most important numbers inline, each with what it is a proportion OF;
- make the direction unmistakable — say whether animal results tracked human results;
- name the studies as "Author et al. Year" where a number is attributed.

Hard rules:
- NEVER write filler like "proportion", "score" or "rate" as if it were a finding. Say what
  was counted.
- If a wide range comes from different sub-analyses, say what varies across it in
  `why_range_is_wide`. Do not present a wide range as a single uncertain estimate.
- If any figure is a NEGATIVE CONTROL — a comparison the authors deliberately expected to
  score low, to validate their metric — exclude it from the summary's direction and record it
  in `negative_controls_noted`. Treating a negative control as poor performance is a
  misreading.
- A study's headline finding must not be omitted because it is inconvenient to summarise. If
  a study reports that animal results failed to discriminate human outcomes, that IS the
  finding.
- Do not compare this organism with other organisms; you cannot see their evidence.
- No adjectives that are not supported by a number ("excellent", "poor", "robust").

`direction` is your reading of this row's evidence only.
`key_numbers`: up to 5 short strings, each a number with what it measures.
Answer with JSON only."""

def arm(pm): return (CLS.get(pm) or {}).get("arm") or "unassigned"
def cite(pm):
    v=DB[pm]; md=META.get(pm) or {}
    a=(md.get("authors_full") or v.get("authors") or [])
    nm=(f"{a[0].split()[-1]} et al." if len(a)>1 else (a[0].split()[-1] if a else "Anon.")) if a else "Anon."
    return f"{nm} {v.get('year') or 'n.d.'}"
def orgs_of(pm):
    a=OK[pm]["animal_side"]
    return N.organisms(list(a.get("species") or [])+list(a.get("grouped_labels") or []))
def comps(pm,o):
    out=[]
    for c in (OK[pm].get("comparisons") or []):
        cs=N.organisms(c.get("animal_species") or [])
        if not cs or o in cs: out.append(c)
    return out

rows=collections.defaultdict(set)
for pm in CORE:
    for o in orgs_of(pm):
        if comps(pm,o): rows[(arm(pm),o)].add(pm)
outp=J("data","db","row_synthesis.json")
out=json.load(open(outp)) if os.path.exists(outp) else {}
print(f"{len(rows)} rows to synthesise")

# The calls are independent, so run them concurrently. Sequentially this took ~25s x 38
# rows; a pool of 8 finishes in about a minute.
lock=threading.Lock(); cost=0.0; errs=0

def build_msg(a,o,pms):
    blocks=[]
    for pm in sorted(pms, key=lambda p:-(DB[p].get("cited_by") or 0)):
        v=OK[pm]; cs=comps(pm,o)
        lines=[f'  - {c["statistic"]} = {c["value"]} {c["unit"]} | {c["what_compared"]}'
               f' | n={c.get("n")} {c.get("n_counts") or ""} | {c.get("source_location")}'
               f' | quote: "{(c.get("verbatim") or "")[:230]}"' for c in cs[:25]]
        blocks.append(f'STUDY {cite(pm)} (PMID {pm}) — verdict: {v["verdict"]}\n'
                      f'  study says: {v.get("verdict_basis","")[:400]}\n'
                      + (f'  caveat: {v["base_rate_caveat"][:300]}\n' if v.get("base_rate_caveat") else "")
                      + "\n".join(lines))
    return (f'ROW: organism "{o}", assessed for {a}. {len(pms)} '
            f'{"study" if len(pms)==1 else "studies"}.\n\n' + "\n\n".join(blocks))

def work(item):
    (a,o),pms = item
    key=f"{a}|{o}"
    if key in out and "error" not in out[key]: return key,None,0.0
    body={"model":MODEL,"messages":[{"role":"system","content":PROMPT},
                                    {"role":"user","content":build_msg(a,o,pms)}],
      "response_format":{"type":"json_schema","json_schema":{"name":"row","strict":True,"schema":SCHEMA}},
      "max_tokens":4000}
    for attempt in range(3):
        try:
            req=urllib.request.Request(orr.URL,data=json.dumps(body).encode(),
                headers={"Authorization":f"Bearer {orr._key()}","Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(req,timeout=300).read().decode())
            c=d["choices"][0]["message"].get("content")
            if not c: raise RuntimeError("null content")
            return key, json.loads(c), (d.get("usage") or {}).get("cost",0)
        except Exception as ex:
            if attempt==2: return key, {"error":str(ex)[:160]}, 0.0
            time.sleep(2*(attempt+1))

todo=[it for it in sorted(rows.items()) if f"{it[0][0]}|{it[0][1]}" not in out
      or "error" in out[f"{it[0][0]}|{it[0][1]}"]]
print(f"{len(todo)} rows to fetch ({len(rows)-len(todo)} cached)")
done=0
with ThreadPoolExecutor(max_workers=8) as ex:
    for fut in as_completed([ex.submit(work,it) for it in todo]):
        key,res,c=fut.result()
        with lock:
            if res is not None:
                out[key]=res
                if "error" in res: errs+=1
            cost+=c; done+=1
            json.dump(out,open(outp,"w"),indent=1)
            if done%10==0: print(f"  {done}/{len(todo)} cost=${cost:.3f} errs={errs}")

ok={k:v for k,v in out.items() if "error" not in v}
print(f"\nsynthesised {len(ok)}/{len(rows)} errors={errs} cost=${cost:.3f}")
print("directions:", dict(collections.Counter(v["direction"] for v in ok.values())))
print("with negative controls flagged:", sum(1 for v in ok.values() if v.get("negative_controls_noted")))
