"""Arm 4 supplement. The s5_vet strand had 3.3% precision: its 'spontaneous' and
'naturally occurring' terms match spontaneous mutation/activity/remission in
laboratory work, so it retrieved induced models. This strand instead requires an
explicit client-owned / veterinary-patient marker."""
import sys, os, json, re, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, openrouter as orr
from rubric import RUBRIC, SCHEMA
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, "data", *p)

VET_PATIENT = """("client-owned"[tiab] OR "client owned"[tiab] OR "pet dog"[tiab] OR "pet dogs"[tiab]
 OR "pet cat"[tiab] OR "pet cats"[tiab] OR "companion animal"[tiab] OR "companion animals"[tiab]
 OR "veterinary clinical trial"[tiab] OR "veterinary clinical trials"[tiab]
 OR "canine patients"[tiab] OR "feline patients"[tiab] OR "veterinary patients"[tiab]
 OR "tumor-bearing dogs"[tiab] OR "tumour-bearing dogs"[tiab] OR "dogs with cancer"[tiab]
 OR "comparative oncology"[tiab] OR "naturally occurring cancer"[tiab]
 OR "naturally occurring disease"[tiab] OR "naturally occurring tumors"[tiab]
 OR "spontaneous canine"[tiab] OR "spontaneously occurring"[tiab])"""
TRANSL = """(translat*[tiab] OR concordan*[tiab] OR predict*[tiab] OR "human patients"[tiab]
 OR "human clinical"[tiab] OR "human counterpart"[tiab] OR "One Health"[tiab]
 OR "human medicine"[tiab] OR "bridge"[tiab] OR "model for human"[tiab])"""
Q = f"({VET_PATIENT} AND {TRANSL})".replace("\n", " ") + ' AND ("1980"[dp] : "3000"[dp]) AND hasabstract'

n, ids, _ = pubmed.esearch(Q, retmax=200, sort="relevance")
print(f"Arm-4 targeted strand: pool={n:,}  sampled={len(ids)}")

cands = json.load(open(J("screening", "slice_candidates.json")))
absd = json.load(open(J("screening", "slice_abstracts.json")))
dec = json.load(open(J("screening", "slice_decisions.json")))

new = [p for p in ids if p not in cands]
print(f"new records: {len(new)}")
summ = pubmed.esummary(new)
cited = pubmed.elink(new, "pubmed_pubmed_citedin")
for p in new:
    s = summ.get(p)
    if not s: continue
    try: yr = int(s.get("year") or 0)
    except ValueError: yr = 0
    cands[p] = {"pmid": p, "title": s["title"], "journal": s["journal"], "year": yr,
                "authors": s.get("authors", []), "sources": ["s8_vet_targeted"],
                "cited_by": len(cited.get(p, []))}

# fetch abstracts for the new ones
for i in range(0, len(new), 150):
    ch = new[i:i+150]
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
           + ",".join(ch) + "&tool=animal-model-concordance&email=rsatija@stanford.edu")
    for a in range(4):
        try: xml = urllib.request.urlopen(url, timeout=120).read().decode(); break
        except Exception: time.sleep(2 ** a)
    else: continue
    for art in xml.split("<PubmedArticle>")[1:]:
        m = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
        if not m: continue
        ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
        ab = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S))
        cl = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
        absd[m.group(1)] = {"title": cl(ti.group(1) if ti else ""), "abstract": cl(ab)}

errs = 0; cost = 0.0
for k, p in enumerate(new, 1):
    r = absd.get(p)
    if not r or not r["abstract"]:
        dec[p] = {"decision": "include", "reason": "no abstract - auto-advance", "confidence": 0.0, "auto": True}
        continue
    try:
        d = orr.chat("google/gemini-2.5-flash-lite",
            [{"role": "system", "content": RUBRIC},
             {"role": "user", "content": f"TITLE: {r['title']}\n\nABSTRACT: {r['abstract'][:3500]}"}],
            schema=SCHEMA, max_tokens=300)
        c = orr.content(d)
        dec[p] = {**json.loads(c), "auto": False} if c else {"decision":"include","reason":"null content","confidence":0.0,"auto":True}
        cost += orr.usd(d)
    except Exception as e:
        errs += 1
        dec[p] = {"decision": "include", "reason": f"screener error: {str(e)[:150]}", "confidence": 0.0, "auto": True}
    time.sleep(0.15)

inc_new = [p for p in new if dec[p]["decision"] == "include"]
print(f"included {len(inc_new)}/{len(new)} ({len(inc_new)/max(1,len(new)):.1%})  errs={errs}  cost=${cost:.4f}")
json.dump(cands, open(J("screening", "slice_candidates.json"), "w"), indent=1)
json.dump(absd, open(J("screening", "slice_abstracts.json"), "w"), indent=1)
json.dump(dec, open(J("screening", "slice_decisions.json"), "w"), indent=1)
print("\nTop Arm-4 includes:")
for cb, y, t in sorted([(cands[p]["cited_by"], cands[p]["year"], cands[p]["title"][:78]) for p in inc_new], reverse=True)[:12]:
    print(f"  {cb:>5} {y}  {t}")
