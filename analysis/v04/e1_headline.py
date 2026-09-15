"""Part 1: headline extraction, one fixed question per study (amendment A6).

For each study with a PDF, one extractor (gemini-2.5-flash) answers:
"What are this paper's headline animal-vs-human results, overall and per species or disease area?"
At most 8 results per paper, each with the exact sentence and its PDF page.

Then, in code:
  - labels are normalised to the frozen vocabularies (the schema uses plain strings: Gemini rejects
    schemas with this many enumerations)
  - each value is located on the PDF text layer (common.locate)
  - every result then goes to an independent per-result check (e2_verify.py); two-extractor agreement is
    NOT used as a gate: in testing it measured how differently two models select results, not whether
    values were correct (6 of 57 agreed while the values were largely right; amendment A6 log)

Input:  data/v04/part1/studies.json  {pmid: {"title":..., "pdf": path}}
Output: data/v04/part1/headlines.json
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

MODELS = {"A": "google/gemini-2.5-flash"}
MAX_RESULTS = 8
LEVELS = {"A": "A-outcome-concordance", "B": "B-toxicity-safety-concordance", "C": "C-biological-similarity"}
DIRECTIONS = ["animal-corresponded", "animal-did-not-correspond", "mixed", "not-applicable"]
UNITS = ["percent", "proportion", "correlation", "r-squared", "ratio", "likelihood-ratio", "auc", "score", "count", "none"]

S = {"type": "string"}
N = {"type": ["number", "null"]}
RESULT = {"type": "object", "additionalProperties": False, "properties": {
    "statement": S, "metric": S, "value": N, "unit": S, "ci_low": N, "ci_high": N,
    "numerator": N, "denominator": N, "denominator_counts": {"type": ["string", "null"]},
    "species": S, "species_as_reported": S, "model_type": S, "disease_area": S, "level": S, "direction": S,
    "quote": S, "pdf_page": {"type": ["integer", "null"]}},
    "required": ["statement", "metric", "value", "unit", "ci_low", "ci_high", "numerator", "denominator",
                 "denominator_counts", "species", "species_as_reported", "model_type", "disease_area", "level",
                 "direction", "quote", "pdf_page"]}
SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "eligible": {"type": "boolean"}, "eligibility_reason": S, "design": S, "peer_reviewed": S,
    "headline_results": {"type": "array", "items": RESULT}},
    "required": ["eligible", "eligibility_reason", "design", "peer_reviewed", "headline_results"]}

SYSTEM = f"""Read this scientific paper and report its HEADLINE results on how results in non-human
animals corresponded to results in humans.

eligible: true only if the paper itself (its own data, or its own pooled or systematic analysis)
compares results in LIVE non-human animals with results in humans. Cell, organoid, tissue or
computational comparisons without live animals are not eligible. Numbers quoted from other papers do
not count.
design: one of primary-comparison | systematic-review-or-meta-analysis | regulatory-or-industry-dataset |
narrative-review | other.
peer_reviewed: yes | no-preprint | unclear.

headline_results: the paper's main answers, at most {MAX_RESULTS}.
FIRST give the paper's overall result. If the paper reports how many of N interventions, drugs, compounds,
toxicities or genes agreed between animals and humans, that count is the first result. Then give results
the paper reports separately by species or by disease. ONE number per result: if a sentence gives two
statistics (e.g. rodents 43%, non-rodents 63%), make two results.

The value must BE the measure of correspondence between animal and human findings: a concordance or
agreement rate, a translation rate, sensitivity, specificity, PPV, NPV, likelihood ratio, a correlation
or similarity between animal and human data, or a count of interventions that agreed.
NEVER put into value:
- a treatment effect measured in animals (odds ratio, % infarct reduction);
- a p-value;
- a duration or time to observation;
- a sample size;
- a cost;
- a number quoted from another study.
A per-intervention or per-condition comparison stated only in words ("benefit in animals, no benefit in
trials") is a result with value null.

Fields:
- statement: one plain sentence a non-specialist can read, including the denominator.
- metric: the statistic's name as printed. unit: one of {", ".join(UNITS)}.
- numerator, denominator: counts when given. denominator_counts: what was counted (interventions,
  compounds, human toxicities, genes, studies).
- species: one of {", ".join(SPECIES)}. Use grouped-label for groups such as "rodents", "non-rodents"
  or "animals". species_as_reported: as written.
- model_type: one of {", ".join(MODEL_TYPES)}.
- disease_area: one of {", ".join(DISEASE_AREAS)}.
- level: A = intervention outcomes in animals vs humans; B = animal toxicity or safety findings vs human
  adverse effects; C = biological similarity without intervention outcome.
- direction: one of {", ".join(DIRECTIONS)}, judged by the paper's own data.
- quote: the exact sentence or table row containing the number. pdf_page: 1-based page of the PDF file.
Answer with JSON only."""

def pick(value, allowed, default):
    v = re.sub(r"[\s_]+", "-", (value or "").strip().lower())
    if v in allowed:
        return v
    for a in allowed:
        if v and (v in a or a in v):
            return a
    return default

def normalise(r):
    r = dict(r)
    r["species"] = pick(r["species"], SPECIES, "other-species")
    r["model_type"] = pick(r["model_type"], MODEL_TYPES, "mixed-or-not-stated")
    area = pick(r["disease_area"], DISEASE_AREAS, "new")
    r["new_disease_area"] = r["disease_area"] if area == "new" else None
    r["disease_area"] = area
    lv = (r["level"] or "").strip().upper()[:1]
    r["level"] = LEVELS.get(lv, "unclear")
    r["direction"] = pick(r["direction"], DIRECTIONS, "not-applicable")
    r["unit"] = pick(r["unit"], UNITS, "none")
    return r

def as_frac(r):
    v = r.get("value")
    if v is None:
        return None
    return v / 100 if r.get("unit") == "percent" else v

def match(a_list, b_list):
    """Pair A and B results that report the same number (percent/proportion tolerant)."""
    pairs, used = [], set()
    for i, a in enumerate(a_list):
        fa, best = as_frac(a), None
        for j, b in enumerate(b_list):
            if j in used:
                continue
            fb = as_frac(b)
            if fa is None or fb is None:
                same = fa is None and fb is None and max(quote_score(a["quote"], b["quote"]), quote_score(b["quote"], a["quote"])) >= 0.5
            else:
                same = abs(fa - fb) <= max(0.005, 0.01 * abs(fa))
            if same:
                best = j
                break
        if best is not None:
            used.add(best)
        pairs.append((i, best))
    pairs += [(None, j) for j in range(len(b_list)) if j not in used]
    return pairs

def main():
    studies = load("part1/studies.json")
    out = load("part1/headlines.json")
    todo = [pm for pm in studies if pm not in out or out[pm].get("status") != "done"]
    print(f"headline extraction: {len(todo)} studies", flush=True)

    def run(pm):
        r, _ = ask(MODELS["A"], SYSTEM, f"TITLE: {studies[pm]['title']}\nPMID: {pm}", SCHEMA, pm=pm,
                   max_tokens=16000, deadline_s=420)
        r["headline_results"] = [normalise(x) for x in r["headline_results"][:MAX_RESULTS]]
        return r
    res = pmap(run, todo, workers=24, label="headline")
    stats = collections.Counter()
    for pm in todo:
        r = res[pm]
        if "error" in r:
            out[pm] = {"status": "error", "error": r["error"]}; stats["error"] += 1; continue
        items = []
        for k, x in enumerate(r["headline_results"]):
            loc = locate(pm, [x.get("value")], x.get("quote"))
            located = (x.get("value") is None and loc["quote_score"] >= 0.6) or \
                      (bool(loc["pages_all_values"]) and loc["quote_score"] >= 0.5)
            items.append({"id": f"{pm}-{k}", **x, "locate": loc, "located": located})
            stats["located" if located else "not-located"] += 1
        out[pm] = {"status": "done", "model": MODELS["A"], "date": today(), "eligible": r["eligible"],
                   "eligibility_reason": r["eligibility_reason"], "design": r["design"],
                   "peer_reviewed": r["peer_reviewed"], "items": items}
        stats["eligible" if r["eligible"] else "ineligible"] += 1
    save(out, "part1/headlines.json")
    print(dict(stats), f"${COST['usd']:.2f}")

if __name__ == "__main__":
    main()
