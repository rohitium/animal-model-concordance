"""Screening pilot: evaluate candidate LLM screeners against a labelled gold set.

The gold labels are MINE, applied from PLAN.md 6.2/6.3, and are provisional until
the user verifies them. Everything downstream depends on their quality, so they are
stored explicitly in data/screening/gold_set.json rather than being implicit."""
import sys, os, json, re, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, openrouter as orr
ROOT = os.path.join(os.path.dirname(__file__), "..")

# Gold labels, revision 2. Revision 1 conflated "landmark paper about translation"
# with "study that measures concordance", so several labels contradicted the rubric
# and the pilot scored the models against an incoherent target.
#
# Rule applied here: INCLUDE iff the record itself reports a quantitative
# animal-to-human agreement statistic. Being influential, or being about the
# translation problem, is not sufficient.
GOLD = {
 # includes -- report an animal<->human agreement statistic
 "17175568":1,  # Perel 2007: animal vs clinical effect sizes, 6 interventions
 "31307492":1,  # Leenaars 2019: concordance rates, scoping review
 "11029269":1,  # Olson 2000: toxicity concordance, 150 compounds
 "29730448":1,  # Clark 2018: big-data tox concordance
 "28893587":1,  # Monticello 2017: nonclinical->FIH translation
 "26753942":1,  # Bailey 2015: NHP predictivity of human toxicity
 "12667944":1,  # Redfern 2003: preclinical QT vs clinical TdP
 "24489990":1,  # Mak 2014: translation rates, oncology
 "23401516":1,  # Seok 2013: quantitative mouse-human genomic correlation
 "25092317":1,  # Takao 2015: same comparison, opposite conclusion
 # excludes -- about translation, but report no agreement statistic
 "20361020":0,  # van der Worp 2010: narrative review
 "30404629":0,  # Pound 2018: narrative review
 "19297654":0,  # Bracken 2009: narrative
 "17988725":0,  # Wall 2008: narrative
 "36883244":0,  # Marshall 2023: self-described narrative review
 "21097827":0,  # Macleod 2010: editorial
 "24678540":0,  # Perrin 2014: commentary
 "20361022":0,  # Sena 2010: measures publication bias -> aux_bias, not an arm
 "18772421":0,  # Contopoulos 2008: bibliometric lifecycle, not concordance
 # excludes -- wrong record type
 "16467546":0,"17687131":0,  # individual trial reports (SAINT I/II)
 "23534501":0,"33427378":0,"34095516":0,  # methods/tools/guidelines
 "29061942":0,"18202698":0,  # comparative-oncology narrative reviews
 "17032985":1,  # Hackam 2006: original data on 76 studies (no abstract; see NOABS rule)
}
RUBRIC = """You are screening titles/abstracts for a systematic review.

INCLUDE only if the record reports a QUANTITATIVE measure of agreement between
non-human animal results and human clinical results - e.g. a concordance rate,
translation/success rate, positive predictive value, sensitivity/specificity of
animal models, or a systematic comparison of animal vs human effect sizes -
across one or more intervention-indication pairs. Regulatory-dataset analyses
and veterinary comparative-oncology concordance analyses count.

EXCLUDE:
- primary animal or human research reporting only its own results
- individual clinical trial reports
- methods/tools/guidelines/reporting checklists
- opinion, editorial, commentary or narrative essay with NO original data and no
  systematic re-analysis
- in vitro / in silico only comparisons
- records with no extractable numerator and denominator

Being an influential paper ABOUT the translation problem is NOT sufficient. The
record must itself report an agreement statistic. A review that only argues that
animal models translate poorly, without measuring it, is EXCLUDE.

When uncertain, INCLUDE (screening favours sensitivity over precision).

Answer with JSON only."""
SCHEMA = {"type":"object","additionalProperties":False,
 "properties":{"decision":{"type":"string","enum":["include","exclude"]},
  "confidence":{"type":"number"},"reason":{"type":"string"}},
 "required":["decision","confidence","reason"]}

def fetch(pmids):
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
           + ",".join(pmids) + "&tool=animal-model-concordance&email=rsatija@stanford.edu")
    xml = urllib.request.urlopen(url, timeout=120).read().decode()
    out = {}
    for art in xml.split("<PubmedArticle>")[1:]:
        pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
        ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
        ab = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S))
        clean = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
        out[pm] = {"title": clean(ti.group(1) if ti else ""), "abstract": clean(ab)}
    return out

recs = fetch(list(GOLD))
json.dump({"labels": GOLD, "records": recs}, open(os.path.join(ROOT,"data","screening","gold_set.json"),"w"), indent=1)
print(f"gold set: {len(recs)} records ({sum(GOLD.values())} include / {len(GOLD)-sum(GOLD.values())} exclude)")

MODELS = ["google/gemini-2.5-flash-lite","openai/gpt-4.1-nano",
          "mistralai/mistral-small-24b-instruct-2501","amazon/nova-lite-v1"]
results = {}
for m in MODELS:
    tp=fp=tn=fn=0; cost=0.0; err=0; preds={}
    for pm, g in GOLD.items():
        r = recs.get(pm)
        if not r: continue
        # Records with no abstract cannot be screened on title alone. Excluding them
        # would silently drop exactly the abstract-less landmark papers Phase 1 found
        # (Hackam 2006, Bracken 2009). They auto-advance to full text instead.
        if not r["abstract"]:
            preds[pm] = 1
            if g: tp += 1
            else: fp += 1
            continue
        msg = [{"role":"system","content":RUBRIC},
               {"role":"user","content":f"TITLE: {r['title']}\n\nABSTRACT: {r['abstract'][:3500] or '(no abstract)'}"}]
        try:
            d = orr.chat(m, msg, schema=SCHEMA, max_tokens=300)
            c = orr.content(d)
            if not c: err += 1; continue
            p = 1 if json.loads(c)["decision"] == "include" else 0
            cost += orr.usd(d)
        except Exception as e:
            err += 1; continue
        preds[pm] = p
        if g and p: tp+=1
        elif g and not p: fn+=1
        elif not g and p: fp+=1
        else: tn+=1
    n = tp+fn
    sens = tp/n if n else 0; spec = tn/(tn+fp) if (tn+fp) else 0
    results[m] = {"tp":tp,"fp":fp,"tn":tn,"fn":fn,"sens":sens,"spec":spec,
                  "cost":cost,"errors":err,"preds":preds}
    print(f"{m:46s} sens={sens:5.1%} spec={spec:5.1%} tp={tp} fn={fn} fp={fp} tn={tn} "
          f"err={err} cost=${cost:.4f}")
json.dump(results, open(os.path.join(ROOT,"data","screening","pilot_results.json"),"w"), indent=1)
tot = sum(r["cost"] for r in results.values())
print(f"\npilot cost: ${tot:.4f}")
if results:
    best = max(results, key=lambda m: (results[m]["sens"], results[m]["spec"]))
    per = results[best]["cost"]/max(1,len(GOLD))
    print(f"projected cost to screen 88,405 records with {best}: ${per*88405:,.2f}")
