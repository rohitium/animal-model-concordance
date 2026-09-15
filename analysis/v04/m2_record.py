"""Manual adjudication, step 2: record the reviewing agent's decisions (no API calls).

Input: a JSON file of decisions written by the reviewing agent:
  {"<item id>": {"d": "keep" | "fix" | "drop", "why": "<one line>",
                 optional corrections: "value", "unit", "species", "level" (A/B/C), "direction", "statement",
                 "model_type", "disease_area"}}
Unlisted items of a study that has any listed item are recorded as drop with why "not a headline
animal-vs-human correspondence result (reviewer)" only if --drop-unlisted is given; otherwise left undecided.

Decisions are stored in part1/adjudicated.json under "<pmid>|manual", in the same shape as model decisions, with
model "manual: reviewing agent (Claude Opus 5, in-session)".

Usage: python3 m2_record.py decisions.json [--drop-unlisted]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

LEVEL = {"A": "A-outcome-concordance", "B": "B-toxicity-safety-concordance", "C": "C-biological-similarity"}

def main():
    src = json.load(open(sys.argv[1]))
    drop_unlisted = "--drop-unlisted" in sys.argv
    heads = load("part1/headlines.json"); adj = load("part1/adjudicated.json")
    items = {it["id"]: (pm, it) for pm, h in heads.items() if h.get("status") == "done" for it in h["items"]}
    by_pm = collections.defaultdict(dict)
    for iid, d in src.items():
        if iid not in items:
            print(f"unknown id {iid}; skipped"); continue
        pm, it = items[iid]
        corrected = {"statement": d.get("statement", it["statement"]), "value": d.get("value", it["value"]),
                     "unit": d.get("unit", it["unit"]), "numerator": d.get("numerator", it["numerator"]),
                     "denominator": d.get("denominator", it["denominator"]), "species": d.get("species", it["species"]),
                     "model_type": d.get("model_type", it.get("model_type")), "disease_area": d.get("disease_area", it.get("disease_area")),
                     "level": LEVEL.get(str(d.get("level", "")).upper()[:1], it["level"]),
                     "direction": d.get("direction", it["direction"]), "pdf_page": it.get("pdf_page")}
        decision = {"keep": "keep", "fix": "keep-with-correction", "drop": "drop"}[d["d"]]
        by_pm[pm][iid] = {"id": iid, "decision": decision, "drop_reason": d["why"] if decision == "drop" else None,
                          "corrected": corrected, "rationale": d["why"]}
    for pm, decs in by_pm.items():
        if drop_unlisted:
            for it in heads[pm]["items"]:
                if it["id"] not in decs:
                    decs[it["id"]] = {"id": it["id"], "decision": "drop",
                                      "drop_reason": "not a headline animal-vs-human correspondence result (reviewer)",
                                      "corrected": {k: it.get(k) for k in ("statement", "value", "unit", "numerator", "denominator",
                                                                          "species", "model_type", "disease_area", "level", "direction", "pdf_page")},
                                      "rationale": "not a headline animal-vs-human correspondence result (reviewer)"}
        prev = adj.get(f"{pm}|manual", {"decisions": {}})
        prev["decisions"].update(decs)
        adj[f"{pm}|manual"] = {"kind": "manual", "decisions": prev["decisions"], "missing": [],
                               "model": "manual: reviewing agent (Claude Opus 5, in-session)", "date": today()}
    save(adj, "part1/adjudicated.json")
    c = collections.Counter(d["decision"] for decs in by_pm.values() for d in decs.values())
    print(f"recorded {sum(c.values())} decisions for {len(by_pm)} studies: {dict(c)}; "
          f"manual studies total {sum(1 for k in adj if k.endswith('|manual'))}")

if __name__ == "__main__":
    main()
