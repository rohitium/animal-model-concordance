"""Re-extract from open-access FULL TEXT where available.

Abstract-only extraction leaves 2x2 tables, per-species results, endpoint detail and
sample sizes unpopulated. This pass reads the OA full text and fills those fields,
recording extraction_source='fulltext' so the two tiers stay distinguishable on the
site. Abstract-derived records are never overwritten by a failed full-text pass."""
import sys, os, json, re, time, html as _html
sys.path.insert(0, os.path.dirname(__file__))
import openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
MODEL = "google/gemini-2.5-flash-lite"
MAXCH = 120_000   # ~30k tokens; keeps per-doc cost near $0.002

db = json.load(open(J("data", "db", "studies.json")))
st = json.load(open(J("data", "raw", "fulltext_status.json")))

def xml_text(p):
    s = open(J(p), encoding="utf-8", errors="replace").read()
    body = re.search(r"<body[^>]*>(.*?)</body>", s, re.S)
    s = body.group(1) if body else s
    s = re.sub(r"<(table-wrap|table)\b", r"\n<\1", s)     # keep table boundaries visible
    s = re.sub(r"</(sec|p|title|tr|table)>", r"\n", s)
    s = _html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", s)).strip()

def pdf_text(p):
    try:
        import subprocess
        r = subprocess.run(["pdftotext", "-q", J(p), "-"], capture_output=True, timeout=90)
        return r.stdout.decode("utf-8", "replace").strip()
    except Exception:
        return ""

SCHEMA = {"type":"object","additionalProperties":False,"properties":{
 "concordance_metric":{"type":["string","null"]},
 "concordance_value":{"type":["number","null"]},
 "n_pairs":{"type":["integer","null"]},
 "n_animal_studies":{"type":["integer","null"]},
 "n_human_studies":{"type":["integer","null"]},
 "species_results":{"type":"array","items":{"type":"object","additionalProperties":False,
   "properties":{"species":{"type":"string"},"metric":{"type":["string","null"]},
                 "value":{"type":["number","null"]},"n":{"type":["integer","null"]}},
   "required":["species","metric","value","n"]}},
 "two_by_two":{"type":["object","null"],"additionalProperties":False,
   "properties":{"tp":{"type":["integer","null"]},"fp":{"type":["integer","null"]},
                 "fn":{"type":["integer","null"]},"tn":{"type":["integer","null"]}},
   "required":["tp","fp","fn","tn"]},
 "sensitivity":{"type":["number","null"]},"specificity":{"type":["number","null"]},
 "ppv":{"type":["number","null"]},"npv":{"type":["number","null"]},
 "endpoints_animal":{"type":"array","items":{"type":"string"}},
 "endpoints_human":{"type":"array","items":{"type":"string"}},
 "endpoint_class":{"type":"string","enum":["primary-hard","secondary-biomarker","mixed","not-stated"]},
 "concordance_definition":{"type":["string","null"]},
 "limitations_stated":{"type":"array","items":{"type":"string"}},
 "funding_conflict":{"type":["string","null"]},
 "key_numbers":{"type":"array","items":{"type":"string"}}},
 "required":["concordance_metric","concordance_value","n_pairs","n_animal_studies",
   "n_human_studies","species_results","two_by_two","sensitivity","specificity","ppv","npv",
   "endpoints_animal","endpoints_human","endpoint_class","concordance_definition",
   "limitations_stated","funding_conflict","key_numbers"]}

PROMPT = """Extract quantitative data from this FULL TEXT of a study relevant to
animal-model concordance with human clinical outcomes.

Rules:
- Use ONLY what the text states. Never infer or supply outside knowledge.
- null / empty array when a field is not reported. Do NOT guess or compute values
  the paper does not give, EXCEPT that if an explicit 2x2 (TP/FP/FN/TN) is given you
  may report it verbatim.
- Proportions as 0-1 (e.g. "71%" -> 0.71).
- species_results: one entry per species where the paper reports a separate figure.
- key_numbers: verbatim quantitative statements, each a SHORT string (<160 chars), with what
  they measure. At most 30 entries -- the most important ones. Do not paste whole paragraphs.
- species_results: at most 25 entries.
- limitations_stated: at most 10 short entries.
- concordance_definition: how THIS paper defines agreement, quoted or closely paraphrased.
Answer with JSON only."""

out = json.load(open(J("data","db","fulltext_extract.json"))) if os.path.exists(J("data","db","fulltext_extract.json")) else {}
cost, done, errs, skipped = 0.0, 0, 0, 0
for pm, s in st.items():
    if pm in out: continue
    if pm not in db: continue
    txt = ""
    if s.get("xml"): txt = xml_text(s["xml"])
    elif s.get("pdf"): txt = pdf_text(s["pdf"])
    if len(txt) < 2000:
        skipped += 1; continue
    try:
        d = orr.chat(MODEL, [{"role":"system","content":PROMPT},
             {"role":"user","content":f"TITLE: {db[pm].get('title','')}\n\nFULL TEXT:\n{txt[:MAXCH]}"}],
             schema=SCHEMA, max_tokens=9000)
        c = orr.content(d)
        if not c: raise RuntimeError("null content")
        out[pm] = {**json.loads(c), "chars": len(txt), "route": s.get("route")}
        cost += orr.usd(d); done += 1
    except Exception as e:
        errs += 1
        out[pm] = {"error": str(e)[:200], "chars": len(txt), "route": s.get("route")}
    json.dump(out, open(J("data","db","fulltext_extract.json"), "w"), indent=1)
    time.sleep(0.2)
    if done % 10 == 0 and done: print(f"  {done} extracted  cost=${cost:.4f} errs={errs}")

ok = [v for v in out.values() if "error" not in v]
print(f"\nfull-text extracted {len(ok)}  errors={errs}  too-short/skipped={skipped}  cost=${cost:.4f}")
print(f"  with 2x2 table:  {sum(1 for v in ok if v.get('two_by_two') and any(x is not None for x in v['two_by_two'].values()))}")
print(f"  with sensitivity:{sum(1 for v in ok if v.get('sensitivity') is not None)}")
print(f"  with per-species:{sum(1 for v in ok if v.get('species_results'))}")
print(f"  with definition: {sum(1 for v in ok if v.get('concordance_definition'))}")
