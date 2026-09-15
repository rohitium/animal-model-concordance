"""Part 1: independent per-result verification (amendment A6).

Every headline result from e1 is checked by a model from a different family (gpt-5-mini) against
the PDF page(s) where it was located (the cited page if not located). The checker sees the result and the
page text only. Each question is answerable from the page:
  value_correct            the value (and CI, counts) is on the page and is the result the statement describes
  is_correspondence        the number measures how animal findings matched human findings, not an animal-only
                           effect, p-value, duration, sample size or quoted figure
  own_result               the paper's own result or its own pooled analysis, not quoted from another study
  species_correct          the species or grouped label matches
  level_correct            A intervention outcomes / B toxicity-safety / C biological similarity
  statement_faithful       the plain statement says what the page says, including the denominator

Status per result: verified (all yes, and located); needs-adjudication (any no/unclear, or not located);
excluded (is_correspondence or own_result is a confident "no" and the value is located, so the
extraction is real but out of scope).

Output: data/v04/part1/verified.json
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

MODEL = "openai/gpt-5-mini"   # chosen on test: rejected 8/10 known-bad results vs 0/10 (gpt-4.1-mini), 3/10 (claude-haiku-4.5)
CHECKS = ["value_correct", "is_correspondence", "own_result", "species_correct", "level_correct", "statement_faithful"]
ANS = {"type": "object", "additionalProperties": False,
       "properties": {"answer": {"type": "string", "enum": ["yes", "no", "unclear"]}, "note": {"type": "string"}},
       "required": ["answer", "note"]}
SCHEMA = {"type": "object", "additionalProperties": False, "properties": {k: ANS for k in CHECKS}, "required": CHECKS}

SYSTEM = """Check one result extracted from a scientific paper against the paper's own page text.
Answer each question from the PAGE TEXT only; "unclear" if the text does not let you decide.
Notes: one short sentence each.
value_correct: the value (and CI and counts, if given) appears in the text and is the result the statement
  describes. If the value is null, answer about the statement's wording instead.
is_correspondence: the number measures how well findings in animals matched findings in humans: a
  concordance or agreement rate, translation rate, sensitivity, specificity, PPV, NPV, likelihood ratio,
  or a correlation or similarity between animal and human data. Answer "no" for a treatment effect in
  animals alone, a p-value, a duration, a sample size, or a comparison between two human groups.
own_result: the paper's own result or its own pooled analysis, not a figure quoted from another study.
species_correct: the result belongs to the recorded species. A result for a group such as "rodents" must be
  recorded as grouped-label.
level_correct: A = intervention outcomes in animals vs humans; B = animal toxicity/safety vs human adverse
  effects; C = biological similarity without intervention outcome.
statement_faithful: the statement says what the text says, including the denominator, and adds nothing.
Answer with JSON only."""

def page_block(pm, it):
    pg = pages(pm)
    want = []
    for p in [it["locate"].get("best_quote_page"), it.get("pdf_page")] + it["locate"].get("pages_all_values", [])[:2]:
        if p and 1 <= p <= len(pg) and p not in want:
            want.append(p)
    want = want[:3] or list(range(1, min(3, len(pg)) + 1))
    return "\n".join(f"--- PDF page {p} ---\n{pg[p-1]}" for p in want)[:16000], want

def main():
    heads = load("part1/headlines.json")
    out = load("part1/verified.json")
    items = [(pm, it) for pm, h in heads.items() if h.get("status") == "done" for it in h["items"] if it["id"] not in out]
    print(f"verifying {len(items)} results", flush=True)
    byid = {it["id"]: (pm, it) for pm, it in items}

    def run(iid):
        pm, it = byid[iid]
        text, used = page_block(pm, it)
        shown = {k: it[k] for k in ("statement", "metric", "value", "unit", "ci_low", "ci_high", "numerator", "denominator",
                                   "denominator_counts", "species", "species_as_reported", "level", "quote")}
        r, _ = ask(MODEL, SYSTEM, f"RESULT:\n{json.dumps(shown, indent=1)}\n\nPAGE TEXT:\n{text}", SCHEMA,
                   max_tokens=8000, deadline_s=240)
        return {"checks": r, "pages_shown": used}
    res = pmap(run, list(byid), workers=48, label="verify")
    stats = collections.Counter()
    for iid, r in res.items():
        pm, it = byid[iid]
        if "error" in r:
            out[iid] = {"pmid": pm, "status": "needs-adjudication", "reasons": [f"verifier failed: {r['error'][:120]}"]}
            stats["needs-adjudication"] += 1; continue
        ck = r["checks"]
        bad = [f"{k}: {ck[k]['answer']} — {ck[k]['note']}" for k in CHECKS if ck[k]["answer"] != "yes"]
        if not it["located"]:
            bad.append("value/quote not located on the PDF text layer")
        if it["located"] and (ck["is_correspondence"]["answer"] == "no" or ck["own_result"]["answer"] == "no") \
                and ck["value_correct"]["answer"] == "yes":
            status = "excluded"
        else:
            status = "verified" if not bad else "needs-adjudication"
        out[iid] = {"pmid": pm, "status": status, "reasons": bad, **r, "model": MODEL, "date": today()}
        stats[status] += 1
    save(out, "part1/verified.json")
    print(dict(stats), f"${COST['usd']:.2f}")

if __name__ == "__main__":
    main()
