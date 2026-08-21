"""Extract a LIST of measurements per study, not one scalar.

The previous model stored a single `concordance_value`, which silently mangled any
paper reporting more than one statistic: "recall and precision" collapsed to a bare
"40%" that means nothing. Each measurement now carries its own statistic name, unit,
plain-language description of what it measures, what was compared, the species, the
sample size AND what that size counts, plus the verbatim source sentence.
"""
import sys, os, json, re, time, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MODEL = "google/gemini-2.5-flash-lite"

MEAS = {"type":"object","additionalProperties":False,"properties":{
  "statistic":{"type":"string"},
  "value":{"type":["number","null"]},
  "unit":{"type":"string","enum":["percent","proportion","fold","correlation","count","ratio","other"]},
  "measures":{"type":"string"},
  "compared":{"type":"string"},
  "species":{"type":"array","items":{"type":"string"}},
  "n":{"type":["integer","null"]},
  "n_counts":{"type":["string","null"]},
  "verbatim":{"type":"string"}},
 "required":["statistic","value","unit","measures","compared","species","n","n_counts","verbatim"]}

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
  "measurements":{"type":"array","items":MEAS},
  "headline_index":{"type":["integer","null"]},
  "what_the_study_did":{"type":"string"},
  "what_it_found":{"type":"string"},
  "key_quotes":{"type":"array","items":{"type":"object","additionalProperties":False,
     "properties":{"quote":{"type":"string"},"topic":{"type":"string"}},
     "required":["quote","topic"]}}},
 "required":["measurements","headline_index","what_the_study_did","what_it_found","key_quotes"]}

PROMPT = """Extract every quantitative result this study reports about how well animal
(or non-human) results correspond to human results.

For EACH number, emit a separate measurement. Never merge two statistics into one
entry: "recall and precision of 40% and 55%" is TWO measurements, not one.

Per measurement:
- statistic: its exact name as the paper uses it (e.g. "sensitivity", "Pearson R2",
  "concordance rate", "positive predictive value", "recall").
- value + unit: percent (0-100), proportion (0-1), fold, correlation, count, ratio, other.
  Use the paper's own scale; do not convert.
- measures: ONE plain sentence a non-specialist can read, saying what this number is
  the agreement/accuracy of. E.g. "share of human toxicities that were also seen in
  at least one animal species".
- compared: what was compared with what, e.g. "dog repeat-dose toxicity vs human adverse events".
- species: species involved, [] if none specific.
- n and n_counts: the sample size and WHAT IT COUNTS (e.g. 150 and "compounds",
  52 and "drugs", 6 and "intervention-indication pairs"). null if not stated.
- verbatim: the sentence from the text containing the number.

headline_index: index into measurements of the single figure the paper leads with, or null.
what_the_study_did / what_it_found: one factual sentence each, no interpretation.
key_quotes: up to 6 short verbatim quotes (<300 chars) stating findings or limitations,
each with a 2-4 word topic label.

Use ONLY the text. Never infer or compute. Answer with JSON only."""

db = json.load(open(J("data","db","studies.json")))
absd = json.load(open(J("data","screening","slice_abstracts.json")))
fts = json.load(open(J("data","raw","fulltext_status.json")))
meta = json.load(open(J("data","db","metadata.json")))
outp = J("data","db","measurements.json")
out = json.load(open(outp)) if os.path.exists(outp) else {}

def best_text(pm):
    s = fts.get(pm, {})
    if s.get("xml"):
        t = open(J(s["xml"]), encoding="utf-8", errors="replace").read()
        b = re.search(r"<body[^>]*>(.*?)</body>", t, re.S)
        t = re.sub(r"<[^>]+>", " ", b.group(1) if b else t)
        return re.sub(r"\s+", " ", t).strip()[:100000]
    if s.get("pdf"):
        try:
            r = subprocess.run(["pdftotext","-q",J(s["pdf"]),"-"],capture_output=True,timeout=120)
            t = re.sub(r"\s+"," ",r.stdout.decode("utf-8","replace")).strip()
            if len(t) > 1500: return t[:100000]
        except Exception: pass
    return (absd.get(pm,{}).get("abstract") or (meta.get(pm) or {}).get("abstract") or "").strip()

cost, errs = 0.0, 0
for i, pm in enumerate(db, 1):
    if pm in out and "error" not in out[pm]: continue
    txt = best_text(pm)
    title = db[pm].get("title") or (meta.get(pm) or {}).get("title") or ""
    if len(txt) < 200:
        out[pm] = {"measurements": [], "key_quotes": [], "what_the_study_did": "",
                   "what_it_found": "", "headline_index": None, "note": "insufficient text"}
        continue
    try:
        d = orr.chat(MODEL, [{"role":"system","content":PROMPT},
             {"role":"user","content":f"TITLE: {title}\n\nTEXT:\n{txt}"}],
             schema=SCHEMA, max_tokens=9000)
        c = orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm] = json.loads(c); cost += orr.usd(d)
    except Exception as ex:
        errs += 1; out[pm] = {"error": str(ex)[:180]}
    json.dump(out, open(outp,"w"), indent=1)
    time.sleep(0.15)
    if i % 25 == 0: print(f"  {i}/{len(db)} cost=${cost:.4f} errs={errs}")

ok = {k:v for k,v in out.items() if "error" not in v}
nm = sum(len(v.get("measurements") or []) for v in ok.values())
print(f"\n{len(ok)}/{len(db)} studies, {nm} measurements, errors={errs}, cost=${cost:.4f}")
import collections
print("studies with >=1 measurement:", sum(1 for v in ok.values() if v.get("measurements")))
print("top statistics:", collections.Counter(
    m["statistic"].lower() for v in ok.values() for m in (v.get("measurements") or [])).most_common(12))
