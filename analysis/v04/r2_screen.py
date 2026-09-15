"""Title/abstract screening of expanded-retrieval candidates (amendment A6).

Two fast models from different families (gemini-2.5-flash-lite, gpt-4.1-nano) answer one question.
A record advances to full-text eligibility if EITHER model says include or uncertain, favouring
sensitivity. Records without an abstract are screened on title and flagged; a title-only exclusion by
both models is accepted here (a change from L27, logged as a limitation), because the expanded
candidate set is ~30x the v0.3 slice.

Output: data/v04/retrieval/screen.json, screen_report.md
"""
import sys, os, re, html, collections, urllib.request, urllib.parse, time
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

MODELS = {"A": "google/gemini-2.5-flash-lite", "B": "openai/gpt-4.1-nano"}
THEMES = ["efficacy-translation", "toxicology-safety", "safety-pharmacology", "disease-biology",
          "companion-animal", "methods-or-bias-only", "not-relevant"]

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "decision": {"type": "string", "enum": ["include", "uncertain", "exclude"]},
    "theme": {"type": "string", "enum": THEMES},
    "reason": {"type": "string"}},
    "required": ["decision", "theme", "reason"]}

SYSTEM = """You are screening records for a systematic review of evidence on how well results in
non-human animals correspond to results in humans.

INCLUDE if the record reports its own data or its own pooled/systematic analysis comparing results in
live non-human animals with results in humans. Examples:
- concordance or translation rates between animal studies and clinical trials of the same interventions
- predictive values (sensitivity, specificity, PPV, NPV, likelihood ratios) of animal toxicity or safety
  findings for human adverse effects
- quantitative similarity between an animal disease model and the human disease (gene expression,
  pathology, physiology) measured against human data
- a study in animals with naturally occurring disease that is explicitly compared with human outcomes
EXCLUDE: animal-only or human-only studies; in vitro, organoid or computational comparisons without live
animals; opinion or narrative pieces with no data or systematic analysis; reproducibility of preclinical
studies without human comparison; drug-development success rates without animal data; guidelines.
Use "uncertain" when the abstract suggests such a comparison may be in the full text.
theme: the best-fitting area. reason: one sentence. Answer with JSON only."""

def fill_pubmed_abstracts(cands):
    need = [c["pmid"] for c in cands.values() if not c["abstract"] and c.get("pmid")]
    for i in range(0, len(need), 150):
        chunk = need[i:i + 150]
        q = urllib.parse.urlencode({"db": "pubmed", "retmode": "xml", "id": ",".join(chunk)})
        for a in range(5):
            try:
                xml = urllib.request.urlopen(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{q}", timeout=120).read().decode("utf-8", "ignore")
                break
            except Exception:
                time.sleep(2 * (a + 1)); xml = ""
        for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, flags=re.S):
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
            t = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", art, flags=re.S)
            ab = re.search(r"<Abstract>(.*?)</Abstract>", art, flags=re.S)
            clean = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()
            for c in cands.values():
                if c.get("pmid") == pm:
                    c["title"] = c["title"] or clean(t.group(1) if t else "")
                    if ab:
                        c["abstract"] = clean(" ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", ab.group(1), flags=re.S)))
        time.sleep(0.4)

def main():
    cands = load("retrieval/candidates.json")
    fill_pubmed_abstracts(cands)
    save(cands, "retrieval/candidates.json")
    out = load("retrieval/screen.json")
    todo = [k for k, c in cands.items() if k not in out and (c["title"] or c["abstract"])]
    print(f"screening {len(todo)} of {len(cands)} candidates", flush=True)

    def run(job):
        role, k = job
        c = cands[k]
        text = f"TITLE: {c['title']}\nYEAR: {c.get('year')}\nABSTRACT: {c['abstract'] or '(no abstract available)'}"
        r, _ = ask(MODELS[role], SYSTEM, text, SCHEMA, max_tokens=1500, deadline_s=60)
        return r
    jobs = [(role, k) for k in todo for role in ("A", "B")]
    for i in range(0, len(jobs), 4000):
        res = pmap(run, jobs[i:i + 4000], workers=48, label="screen")
        for (role, k), r in res.items():
            out.setdefault(k, {})[role] = r
        save(out, "retrieval/screen.json")

    dec = collections.Counter(); theme = collections.Counter(); title_only = 0
    for k, r in out.items():
        a, b = r.get("A", {}), r.get("B", {})
        if "error" in a and "error" in b:
            r["advance"], r["basis"] = True, "both screening calls failed; advanced"
        else:
            votes = [x.get("decision") for x in (a, b) if "error" not in x]
            r["advance"] = any(v in ("include", "uncertain") for v in votes)
            r["basis"] = "either model include/uncertain" if r["advance"] else "both models exclude"
        r["title_only"] = not cands[k]["abstract"]
        title_only += r["title_only"]
        dec["advance" if r["advance"] else "exclude"] += 1
        if r["advance"]:
            theme[(a if "error" not in a else b).get("theme")] += 1
    save(out, "retrieval/screen.json")
    agree = sum(1 for r in out.values() if "error" not in r.get("A", {"error": 1}) and "error" not in r.get("B", {"error": 1})
                and (r["A"]["decision"] == "exclude") == (r["B"]["decision"] == "exclude"))
    L = ["# Screening (amendment A6)", "", f"Run {today()}; models {MODELS}.", "",
         f"- screened: {len(out)} (title only: {title_only})",
         f"- advance to full text: {dec['advance']}", f"- excluded by both models: {dec['exclude']}",
         f"- models agree on exclude-vs-advance: {agree}/{len(out)}", "", "## Advanced, by theme (model A)", ""]
    L += [f"- {k}: {v}" for k, v in theme.most_common()]
    L += ["", f"Cost (uncached): ${COST['usd']:.2f}"]
    open(os.path.join(V04, "retrieval", "screen_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
