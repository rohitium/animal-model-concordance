"""Stage 1 — study-level scope screen under PLAN.md v0.4 §4.4.

Two models from different families read each PDF independently and classify every index test
the study uses. A study goes forward to extraction if either model finds a live-animal-vs-human
comparison; disagreement is flagged for review rather than resolved by either model.

Input: the v0.3 eligible studies that have a PDF. Output: data/v04/s1_scope.json
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "index_tests": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {
            "description": {"type": "string"},
            "kind": {"type": "string", "enum": ["live-animal", "in-vitro-or-ex-vivo", "in-silico",
                     "patient-derived-xenograft", "human-only", "other"]},
            "species_as_reported": {"type": "array", "items": {"type": "string"}}},
        "required": ["description", "kind", "species_as_reported"]}},
    "live_animal_vs_human_comparison": {"type": "boolean"},
    "comparison_quote": {"type": ["string", "null"]},
    "publication_type": {"type": "string", "enum": ["primary-analysis",
        "systematic-review-or-meta-analysis", "narrative-review", "commentary-or-opinion", "other"]},
    "peer_reviewed": {"type": "string", "enum": ["yes", "no-preprint", "unclear"]},
    "reason": {"type": "string"}},
    "required": ["index_tests", "live_animal_vs_human_comparison", "comparison_quote",
                 "publication_type", "peer_reviewed", "reason"]}

SYSTEM = """You are screening a scientific paper for a review of how results in non-human animals
compare with results in humans. Classify, from the full text, what the paper actually did.

index_tests: every non-human system whose results the paper compares with human results.
  live-animal: a whole, living non-human animal (including animals with naturally occurring
    disease). Data pooled from published live-animal studies also count.
  in-vitro-or-ex-vivo: cells, tissues or organs studied outside a living animal, even if taken
    from an animal (cell lines, primary cultures, organoids, organ-on-chip, 3D microtissues,
    isolated tissue, ion-channel assays).
  in-silico: computational, statistical or mathematical models, QSAR, PBPK, machine learning.
  patient-derived-xenograft: human tumour tissue grown in an animal host.
  human-only: the comparison involves no non-human system.

live_animal_vs_human_comparison: true only if the paper itself reports a comparison, in numbers
  or in words, between results in live animals and results in humans. A paper that describes
  animal results and human results separately without comparing them is false. Treatment effects
  measured in animals alone are not a comparison.
comparison_quote: one sentence copied exactly from the paper showing that comparison, or null.
peer_reviewed: "no-preprint" if the document is a preprint (e.g. Research Square, bioRxiv,
  medRxiv, "posted", line-numbered manuscript without journal formatting).
reason: one or two sentences, no adjectives.
Answer with JSON only."""

def decide(a, b):
    """Consensus rule. Both yes -> include; both no -> exclude; otherwise flag."""
    def live(x):
        return bool(x.get("live_animal_vs_human_comparison")) and any(
            t["kind"] == "live-animal" for t in x.get("index_tests", []))
    def pdx_only(x):
        kinds = {t["kind"] for t in x.get("index_tests", [])}
        return "patient-derived-xenograft" in kinds and "live-animal" not in kinds
    la, lb = live(a), live(b)
    if pdx_only(a) and pdx_only(b):
        return "pdx-stratum", []
    if la and lb:
        return "include", []
    if not la and not lb:
        return "exclude", []
    return "include-provisional", ["models disagree on whether a live-animal-vs-human comparison is reported"]

def main():
    db = json.load(open(J("data", "db", "studies.json")))
    targets = sorted(pm for pm, v in db.items() if v.get("eligible") and pdf_path(pm))
    t = tier("scope")
    print(f"stage 1 scope: {len(targets)} studies, tier {t}")
    out = {}
    for role in ("A", "B"):
        model = LADDER[t][role]
        def run(pm):
            title = db[pm].get("title", "")
            r, meta = ask(model, SYSTEM, f"TITLE: {title}\nPMID: {pm}", SCHEMA, pm=pm, max_tokens=16000)
            return r
        res = pmap(run, targets, label=f"scope-{role}")
        for pm in targets:
            out.setdefault(pm, {"pmid": pm, "title": db[pm].get("title"), "year": db[pm].get("year")})
            out[pm][role] = {"model": model, "tier": t, "date": today(), "result": res[pm]}
    for pm, rec in out.items():
        a, b = rec["A"]["result"], rec["B"]["result"]
        if "error" in a and "error" in b:
            rec["decision"], rec["flags"] = "error", ["both model calls failed"]
            continue
        if "error" in a or "error" in b:
            # One model failed (e.g. runaway output). Never drop the study: go forward on the
            # other model's reading, provisionally, and flag it.
            ok, bad = (b, "A") if "error" in a else (a, "B")
            live = ok.get("live_animal_vs_human_comparison") and any(
                t["kind"] == "live-animal" for t in ok.get("index_tests", []))
            rec["decision"] = "include-provisional" if live else "exclude-provisional"
            rec["flags"] = [f"model {bad} call failed; decision rests on one model"]
            rec["peer_reviewed"] = ok.get("peer_reviewed", "unclear")
            continue
        rec["decision"], rec["flags"] = decide(a, b)
        pr = {a["peer_reviewed"], b["peer_reviewed"]}
        rec["peer_reviewed"] = "no-preprint" if "no-preprint" in pr else ("yes" if pr == {"yes"} else "unclear")
        if len(pr) > 1:
            rec["flags"].append("models disagree on peer-review status")
    save(out, "s1_scope.json")
    import collections
    print(dict(collections.Counter(r["decision"] for r in out.values())), f"${COST['usd']:.3f}")

if __name__ == "__main__":
    main()
