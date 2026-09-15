"""Second, stricter screening pass on records advanced by r2 (amendment A6 execution note).

r2's rule (advance if either fast model says include or uncertain) advanced 15,439 of 26,335 records,
including 4,886 that the first model itself labelled not relevant. Too permissive to take to full text.

Here one stronger model (gemini-2.5-flash) answers a stricter question with the common false positives
named. A record goes to full text if this pass says include or uncertain.

Calibration: sensitivity is measured on ANCHORS, named studies that genuinely measure animal-to-human
concordance with their own data or pooled analysis. The v0.3 stage-1 includes are not a valid benchmark:
many are narrative reviews or in vitro studies that the strict criterion correctly excludes (they were the
v0.3 corpus's false positives). Below 90% anchor sensitivity the pass is not trusted. Two first-draft
anchors were removed as not measuring concordance: van der Worp 2010 (an essay quoting other studies) and
Sena 2010 (publication bias within animal studies, no human comparison).

Records without an abstract cannot be judged strictly; they go to full text if the first pass's
gemini model said include or uncertain (Hackam 2006 and Perrin 2014 have no abstract and were rated
uncertain).

Output: data/v04/retrieval/screen_strict.json, screen_strict_report.md
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

MODEL = "google/gemini-2.5-flash"
# Studies that measure animal-to-human concordance with their own data or pooled analysis (calibration set)
ANCHORS = {"11029269": "Olson 2000", "28893587": "Monticello 2017", "29730448": "Clark 2018", "32868897": "Atkins 2020",
           "26753942": "Bailey 2016", "17175568": "Perel 2007", "16453316": "O'Collins 2006", "23401516": "Seok 2013",
           "25092317": "Takao 2015", "31307492": "Leenaars 2019", "38870090": "Ineichen 2024",
           "17032985": "Hackam 2006", "24678540": "Perrin 2014", "28903488": "Pollard 2017 (QT)",
           "30726989": "Bhatt 2019", "36859342": "tolerable dose translatability", "34558834": "chronic liver disease cross-species",
           "26795250": "Godec 2016 immune signatures", "42245789": "Daluwatumulle 2026", "25671556": "Petersen-Jones 2015"}
SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "decision": {"type": "string", "enum": ["include", "uncertain", "exclude"]},
    "evidence_type": {"type": "string", "enum": ["efficacy-translation", "toxicology-safety", "safety-pharmacology",
                      "disease-biology", "companion-animal", "none"]},
    "reason": {"type": "string"}},
    "required": ["decision", "evidence_type", "reason"]}

SYSTEM = """You screen records for a review of studies that MEASURE how well results in non-human animals
correspond to results in humans.

INCLUDE only if the abstract indicates the paper itself reports data, or its own systematic or pooled
analysis, placing results from LIVE non-human animals against results in HUMANS. Examples:
- how many interventions that worked in animals worked in clinical trials, or effect sizes compared;
- sensitivity, specificity or predictive values of animal toxicity or safety studies for human adverse
  effects;
- gene expression, pathology or physiology of an animal disease model compared quantitatively with human
  patient data;
- a veterinary spontaneous-disease study whose results are explicitly compared with human results.

EXCLUDE — these are the common false positives:
- characterising or validating an animal model with no human data in the same analysis;
- human clinical studies that only mention or cite animal findings;
- narrative, perspective or opinion reviews without their own pooled analysis;
- studies of preclinical reproducibility, bias or reporting quality without human comparison;
- in vitro, organoid, organ-on-chip or computational models, even when compared with humans;
- drug development success rates without animal data;
- basic mechanism studies that use animals and human cells or tissue for different questions.

"uncertain": the abstract strongly suggests such a comparison but does not make clear whether it is the
paper's own. evidence_type: the kind of comparison, or none. reason: one sentence. JSON only."""

def main():
    cands = load("retrieval/candidates.json")
    screen = load("retrieval/screen.json")
    scope = load("s1_scope.json")
    out = load("retrieval/screen_strict.json")
    advanced = [k for k, r in screen.items() if r.get("advance") and k in cands]
    known = set(ANCHORS)
    known_keys = [k for k, c in cands.items() if c.get("pmid") in known]
    todo = sorted(set(advanced) | set(known_keys))
    if os.environ.get("AMC_STRICT_CALIBRATE"):   # calibration-only run on the known includes
        todo = sorted(known_keys)
    todo = [k for k in todo if k not in out]
    print(f"strict screening: {len(advanced)} advanced + {len(known_keys)} known includes; {len(todo)} to run", flush=True)

    def run(k):
        c = cands[k]
        r, _ = ask(MODEL, SYSTEM, f"TITLE: {c['title']}\nYEAR: {c.get('year')}\nABSTRACT: {c['abstract'] or '(no abstract)'}",
                   SCHEMA, max_tokens=3000, deadline_s=90)
        return r
    for i in range(0, len(todo), 3000):
        res = pmap(run, todo[i:i + 3000], workers=48, label="strict")
        out.update(res)
        save(out, "retrieval/screen_strict.json")

    ok = {k: v for k, v in out.items() if "error" not in v}
    passed = {k for k, v in ok.items() if v["decision"] in ("include", "uncertain")}
    no_abstract_advanced = {k for k in advanced if not cands[k]["abstract"] and (screen[k].get("A") or {}).get("decision") in ("include", "uncertain")}
    passed |= no_abstract_advanced
    for k in no_abstract_advanced:
        if k in out and "error" not in out[k]:
            out[k]["decision_final"] = "advance-no-abstract"
    for k, v in out.items():
        if "error" not in v:
            v["passes"] = k in passed
    save(out, "retrieval/screen_strict.json")
    sens_n = [k for k in known_keys if k in ok]
    sens = sum(1 for k in sens_n if k in passed)
    missed = [(cands[k].get("pmid"), cands[k]["title"][:90], ok[k]["reason"]) for k in sens_n if k not in passed]
    adv_pass = [k for k in advanced if k in passed]
    L = ["# Strict screening (second pass)", "", f"Run {today()}; model {MODEL}.", "",
         f"- calibration on known includes: {sens}/{len(sens_n)} passed" + (f" ({sens/len(sens_n):.0%})" if sens_n else ""),
         f"- advanced by first pass: {len(advanced)} → passed strict pass: {len(adv_pass)} "
         f"(of which no-abstract records advanced on first-pass include: {len(no_abstract_advanced & set(adv_pass))})",
         f"- errors: {sum(1 for v in out.values() if 'error' in v)}", "", "## By evidence type (passed)", ""]
    L += [f"- {t}: {n}" for t, n in collections.Counter(ok[k]["evidence_type"] for k in adv_pass).most_common()]
    L += ["", "## Known includes the strict pass would exclude", ""] + [f"- {p} {t} — {r}" for p, t, r in missed]
    L += ["", f"Cost (uncached): ${COST['usd']:.2f}"]
    open(os.path.join(V04, "retrieval", "screen_strict_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
