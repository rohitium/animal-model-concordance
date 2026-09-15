"""Stage 4 — checklist verifier (PLAN.md v0.4 §8.1 stage 3).

A model that did not produce the record reads the page(s) where the comparison was located and
answers a fixed checklist. It is given the record and the page text only; it cannot see the
other extraction or any verdict.

The verifier is the extractor family that did NOT produce the canonical record: when A's record is
checked, B's model family checks it, and vice versa, so no model grades its own work.

Input: s3_items.json. Output: data/v04/s4_verify.json keyed by item id.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

CHECKS = ["value_present", "species_correct", "metric_correct", "counts_correct",
          "provenance_correct", "animal_vs_human", "live_animal_index", "level_correct",
          "disease_area_correct"]

ITEM = {"type": "object", "additionalProperties": False, "properties": {
    "answer": {"type": "string", "enum": ["yes", "no", "unclear", "not-applicable"]},
    "note": {"type": "string"}}, "required": ["answer", "note"]}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {k: ITEM for k in CHECKS}, "required": CHECKS}

SYSTEM = """You are checking one record extracted from a scientific paper against the paper's own
text. Answer each question from the PAGE TEXT provided. Do not assume anything the text does not
show. If the text does not let you decide, answer "unclear". Notes: one short sentence each.

value_present: the recorded value (and CI, if any) appears in the text and is the result the
  record describes. "not-applicable" if value is null (qualitative record).
species_correct: the result belongs to the recorded species. If the paper reports a group
  ("rodent", "non-rodent"), the record must say grouped-label, not an individual species.
metric_correct: the recorded metric is the statistic the text reports.
counts_correct: numerator/denominator match the text; "not-applicable" if both are null.
provenance_correct: own-result = computed in this paper; reanalysis-of-other-data = this paper
  pooled others' data; cited-from-other-study = quoted from another publication;
  condensed-from-authors-earlier-work = restating the same authors' earlier results.
animal_vs_human: the result places an animal result against a human result. A treatment effect
  measured in animals only is "no".
live_animal_index: the animal-side result comes from whole, living animals (or data pooled from
  such studies). Cells, tissues, organoids or chips, even from animals, are "no".
level_correct: A = animal intervention results vs human intervention results; B = animal
  toxicity/safety vs human adverse effects; C = biological similarity without intervention outcome.
disease_area_correct: the recorded disease area matches the human condition in the text.
Answer with JSON only."""

MAX_CHARS = 14000

def page_text(pm, loc):
    pg = pages(pm)
    want = []
    for p in (loc.get("best_quote_page"),) + tuple(loc.get("pages_all_values", [])[:2]):
        if p and p not in want:
            want.append(p)
    if not want:
        want = list(range(1, min(len(pg), 3) + 1))
    chunks = [f"--- PDF page {p} ---\n{pg[p-1]}" for p in want]
    return "\n".join(chunks)[:MAX_CHARS], want

def main():
    items = load("s3_items.json", [])
    t = tier("verify")
    out = load("s4_verify.json")
    todo = [x for x in items if x["id"] not in out or "error" in out[x["id"]]]
    byid = {x["id"]: x for x in items}
    print(f"stage 4 verify: {len(todo)} items, tier {t}")

    def run(iid):
        x = byid[iid]
        role = "A" if x["A"] else "B"
        rec = x[role]
        checker = LADDER[t]["B" if role == "A" else "A"]
        text, used = page_text(x["pmid"], x["locate"][role])
        shown = {k: rec[k] for k in ("what_is_compared", "human_condition", "disease_area",
                 "species", "species_as_reported", "model_type", "index_test_kind", "level",
                 "metric", "metric_as_reported", "qualitative", "value", "unit", "ci_low", "ci_high",
                 "numerator", "denominator", "provenance", "quote", "location")}
        user = f"RECORD:\n{json.dumps(shown, indent=1)}\n\nPAGE TEXT:\n{text}"
        r, _ = ask(checker, SYSTEM, user, SCHEMA, max_tokens=16000)
        return {"checked_record": role, "checker": checker, "tier": t, "date": today(),
                "pages_shown": used, "checks": r}

    res = pmap(run, [x["id"] for x in todo], label="verify")
    out.update(res)
    save(out, "s4_verify.json")
    import collections
    tally = collections.Counter()
    for v in out.values():
        if "error" in v:
            tally["error"] += 1; continue
        for k in CHECKS:
            tally[f"{k}:{v['checks'][k]['answer']}"] += 1
    print({k: v for k, v in sorted(tally.items())}, f"${COST['usd']:.3f}")

if __name__ == "__main__":
    main()
