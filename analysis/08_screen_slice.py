"""Screen the candidate pool with the validated LLM screener, then select the
pilot slice: stratified by strand (diversity), scored on citations (authority)
and recency. Selection is a recorded function, not a judgement call."""
import sys, os, json, re, math, time, urllib.request, collections
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, openrouter as orr
from rubric import RUBRIC, SCHEMA, RUBRIC_VERSION
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, "data", *p)
MODEL = "google/gemini-2.5-flash-lite"
YEAR_NOW = 2026


cands = json.load(open(J("screening", "slice_candidates.json")))
pmids = list(cands)
print(f"candidates: {len(pmids)}")

def fetch_abstracts(pmids):
    out = {}
    for i in range(0, len(pmids), 150):
        ch = pmids[i:i+150]
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
               + ",".join(ch) + "&tool=animal-model-concordance&email=rsatija@stanford.edu")
        for a in range(4):
            try:
                xml = urllib.request.urlopen(url, timeout=120).read().decode(); break
            except Exception:
                import time; time.sleep(2 ** a)
        else:
            continue
        for art in xml.split("<PubmedArticle>")[1:]:
            m = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
            if not m: continue
            ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
            ab = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S))
            cl = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
            out[m.group(1)] = {"title": cl(ti.group(1) if ti else ""), "abstract": cl(ab)}
        print(f"  fetched {len(out)}/{len(pmids)}")
    return out

absd = fetch_abstracts(pmids)
json.dump(absd, open(J("screening", "slice_abstracts.json"), "w"), indent=1)

decisions, cost, errs = {}, 0.0, 0
for n, pm in enumerate(pmids, 1):
    r = absd.get(pm)
    if not r:
        decisions[pm] = {"decision": "include", "reason": "metadata unavailable - auto-advance",
                         "confidence": 0.0, "auto": True}; continue
    if not r["abstract"]:
        decisions[pm] = {"decision": "include", "reason": "no abstract - cannot screen on title alone",
                         "confidence": 0.0, "auto": True}; continue
    try:
        d = orr.chat(MODEL, [{"role": "system", "content": RUBRIC},
             {"role": "user", "content": f"TITLE: {r['title']}\n\nABSTRACT: {r['abstract'][:3500]}"}],
             schema=SCHEMA, max_tokens=300)
        c = orr.content(d)
        if not c: errs += 1; decisions[pm] = {"decision":"include","reason":"screener error - auto-advance","confidence":0.0,"auto":True}; continue
        decisions[pm] = {**json.loads(c), "auto": False}
        cost += orr.usd(d)
    except Exception as e:
        errs += 1
        decisions[pm] = {"decision": "include", "reason": f"screener error - auto-advance: {str(e)[:200]}",
                         "confidence": 0.0, "auto": True}
    time.sleep(0.15)  # pace: unpaced bursts triggered mass 429s on the first run
    if n % 200 == 0: print(f"  screened {n}/{len(pmids)}  cost=${cost:.4f} errs={errs}")

if errs > 0.05 * len(pmids):
    raise SystemExit(f"ABORT: {errs}/{len(pmids)} screener errors (>5%). "
                     "Auto-advancing this many records makes the include rate meaningless. "
                     "Fix the API failure and re-run; cached successes will be reused.")
inc = [p for p, d in decisions.items() if d["decision"] == "include"]
print(f"\nincluded {len(inc)}/{len(pmids)} ({len(inc)/len(pmids):.1%})  errors={errs}  cost=${cost:.4f}")
json.dump(decisions, open(J("screening", "slice_decisions.json"), "w"), indent=1)

# ---- selection ------------------------------------------------------------
# score = authority (log citations, capped) + recency, equally weighted after
# normalisation. Landmarks are not filtered out by recency; they win on authority.
def score(p):
    c = cands[p]
    auth = math.log1p(c["cited_by"]) / math.log1p(3862)
    rec = max(0.0, min(1.0, (c["year"] - 1995) / (YEAR_NOW - 1995))) if c["year"] else 0.3
    bonus = 0.15 if "anchor" in c["sources"] else (0.08 if "citation_hub" in c["sources"] else 0)
    return 0.5 * auth + 0.5 * rec + bonus

TARGET = 100
by_strand = collections.defaultdict(list)
for p in inc:
    for s in cands[p]["sources"]:
        if s.startswith("s") or s == "anchor":
            by_strand[s].append(p)
sel, seen = [], set()
strands = sorted(by_strand)
quota = max(1, TARGET // max(1, len(strands)))
for s in strands:  # diversity quota first
    for p in sorted(by_strand[s], key=score, reverse=True):
        if p in seen: continue
        sel.append(p); seen.add(p)
        if len([x for x in sel if s in cands[x]["sources"]]) >= quota: break
for p in sorted(inc, key=score, reverse=True):  # fill remainder by score
    if len(sel) >= TARGET: break
    if p not in seen: sel.append(p); seen.add(p)

json.dump({"selected": sel, "target": TARGET,
           "scoring": "0.5*log1p(cited_by)/log1p(3862) + 0.5*recency(1995..2026) + source bonus"},
          open(J("screening", "slice_selected.json"), "w"), indent=1)
print(f"\nselected {len(sel)} studies")
yr = [cands[p]["year"] for p in sel if cands[p]["year"]]
cb = [cands[p]["cited_by"] for p in sel]
print(f"  years {min(yr)}-{max(yr)}, median {sorted(yr)[len(yr)//2]}")
print(f"  citations median {sorted(cb)[len(cb)//2]}, max {max(cb)}")
sc = collections.Counter(s for p in sel for s in cands[p]["sources"])
print("  strand coverage:", dict(sc))
