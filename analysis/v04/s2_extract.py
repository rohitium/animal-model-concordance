"""Stage 2 — double extraction of animal-vs-human comparisons (PLAN.md v0.4 §5, §8.1 stage 1).

Two models from different families extract independently from the same PDF. The prompt is blind
to the review's motivation: it asks what was compared and what was found, and says nothing about
which answer is expected.

Input: data/v04/s1_scope.json (include / include-provisional). Output: data/v04/s2_extract.json
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

METRICS = ["concordance-proportion", "translation-rate", "sensitivity", "specificity", "ppv", "npv",
           "likelihood-ratio-positive", "likelihood-ratio-negative-or-inverse", "accuracy", "auc",
           "correlation", "similarity-score", "effect-size-ratio", "other"]

COMP = {"type": "object", "additionalProperties": False, "properties": {
    "what_is_compared": {"type": "string"},
    "human_condition": {"type": "string"},
    "disease_area": {"type": "string", "enum": DISEASE_AREAS},
    "new_disease_area": {"type": ["string", "null"]},
    "species": {"type": "string", "enum": SPECIES},
    "species_as_reported": {"type": "string"},
    "model_type": {"type": "string", "enum": MODEL_TYPES},
    "index_test_kind": {"type": "string", "enum": ["live-animal", "in-vitro-or-ex-vivo", "in-silico",
                                                  "patient-derived-xenograft"]},
    "level": {"type": "string", "enum": LEVELS},
    "metric": {"type": "string", "enum": METRICS},
    "metric_as_reported": {"type": "string"},
    "qualitative": {"type": "boolean"},
    "value": {"type": ["number", "null"]},
    "unit": {"type": "string", "enum": ["percent", "proportion", "ratio", "correlation", "score", "other", "none"]},
    "ci_low": {"type": ["number", "null"]},
    "ci_high": {"type": ["number", "null"]},
    "numerator": {"type": ["number", "null"]},
    "denominator": {"type": ["number", "null"]},
    "n_unit": {"type": ["string", "null"]},
    "dataset": {"type": ["string", "null"]},
    "provenance": {"type": "string", "enum": ["own-result", "reanalysis-of-other-data",
                   "cited-from-other-study", "condensed-from-authors-earlier-work"]},
    "quote": {"type": "string"},
    "location": {"type": "string"},
    "pdf_page": {"type": ["integer", "null"]}},
    "required": ["what_is_compared", "human_condition", "disease_area", "new_disease_area", "species",
                 "species_as_reported", "model_type", "index_test_kind", "level", "metric",
                 "metric_as_reported", "qualitative", "value", "unit", "ci_low", "ci_high", "numerator",
                 "denominator", "n_unit", "dataset", "provenance", "quote", "location", "pdf_page"]}

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "comparisons": {"type": "array", "items": COMP}}, "required": ["comparisons"]}

SYSTEM = """You are extracting data from a scientific paper. Record every result in which the paper
compares an outcome in non-human animals with the corresponding outcome in humans. Record what
the paper measured, exactly as reported. Do not interpret, summarise the authors' opinions, or
judge whether results are good or bad.

WHAT COUNTS AS A COMPARISON
- It must place an animal result against a human result: e.g. a proportion of interventions
  whose animal and clinical results agreed; sensitivity/PPV of animal toxicity findings for human
  adverse events; a correlation between animal and human gene expression.
- A treatment effect measured in animals alone (an odds ratio, an infarct-volume reduction) is
  NOT a comparison, even if a human effect is reported elsewhere. Record the paper's statement of
  whether they agreed instead.
- Give the overall result and any per-species or per-disease results. Do not list per-organ-system
  or other subcategory breakdowns when an overall figure for that species exists.
- If the paper states a comparison only in words, record it with qualitative=true, value=null.

FIELDS
- level: A = intervention results in animals compared with intervention results in humans
  (efficacy or translation). B = animal toxicity/safety findings compared with human adverse
  effects. C = biological similarity (molecular, pathological, physiological) with no
  intervention outcome.
- disease_area: the HUMAN condition's area. Toxicity or safety not tied to one disease is
  "cross-cutting-toxicology". If none fits, use "new" and name it in new_disease_area.
- species: the species the result belongs to. If the paper reports a group ("rodent",
  "non-rodent", "animals"), use "grouped-label" and put the label in species_as_reported. Never
  split a group into species.
- model_type: spontaneous-companion = client-owned/pet animals with naturally occurring disease;
  spontaneous-lab = naturally occurring disease in laboratory-kept animals; induced = disease
  produced by surgery, chemicals, diet or infection; engineered = genetically modified;
  healthy = no disease (e.g. toxicology in normal animals).
- index_test_kind: what produced the animal-side result. Cells, tissues, organoids or chips
  derived from animals are in-vitro-or-ex-vivo.
- value and unit exactly as printed (85% -> 85 percent; 0.85 on a 0-1 scale -> 0.85 proportion).
  numerator/denominator when the paper gives counts (e.g. "3 of 6").
- dataset: the underlying data source if named (e.g. a consortium database, "published stroke
  studies 1957-2003"), else null.
- provenance: own-result = computed in this paper from its data; reanalysis-of-other-data = this
  paper pooled or recomputed others' data (systematic reviews); cited-from-other-study = the number
  is quoted from another publication; condensed-from-authors-earlier-work = restates the same
  authors' previously published results.
- quote: copy the exact sentence containing the result, character for character. For a table,
  copy the table row as printed (row label followed by the cells).
- location: "Table 3", "Figure 2", "Results", "Abstract", etc.
- pdf_page: the 1-based page number of the PDF file where the quote appears.
Answer with JSON only."""

def main():
    scope = load("s1_scope.json")
    targets = sorted(pm for pm, r in scope.items() if r.get("decision") in ("include", "include-provisional"))
    t = tier("extract")
    print(f"stage 2 extraction: {len(targets)} studies, tier {t}")
    out = load("s2_extract.json")
    # Both extractors run at once: jobs are (role, study) pairs in one pool.
    def run(job):
        role, pm = job
        r, _ = ask(LADDER[t][role], SYSTEM, f"TITLE: {scope[pm]['title']}\nPMID: {pm}", SCHEMA, pm=pm, max_tokens=48000)
        return r
    jobs = [(role, pm) for pm in targets for role in ("A", "B")]
    res = pmap(run, jobs, label="extract")
    for role, pm in jobs:
        out.setdefault(pm, {})[role] = {"model": LADDER[t][role], "tier": t, "date": today(), "result": res[(role, pm)]}
    save(out, "s2_extract.json")
    n = {r: sum(len((out[pm][r]["result"].get("comparisons") or [])) for pm in targets if "error" not in out[pm][r]["result"]) for r in ("A", "B")}
    errs = {r: sum(1 for pm in targets if "error" in out[pm][r]["result"]) for r in ("A", "B")}
    print(f"comparisons A={n['A']} B={n['B']}  errors {errs}  ${COST['usd']:.3f}")

if __name__ == "__main__":
    main()
