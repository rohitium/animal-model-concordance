"""Part 2 summary: drug-pair concordance for dogs and cats with naturally occurring disease (amendment A6).

Reads data/v04/part2/pairs.json and writes the tables the page-15 replacement draws on, following the
protocol's reporting rules (§3):
  F2  every classified pair is reported; concordance proportions carry exact (Clopper–Pearson) 95% CIs,
      however few pairs there are
  F4  "discordant" only where all evidence points opposite; mixed and indeterminate are counted, never dropped
Strata reported separately, never pooled:
  efficacy vs safety pairs; same-molecule and species-specific biologics (primary) vs class analogues;
  disease-modifying vs symptomatic/preventive use; systematically found vs exemplar-only pairs.
Not produced here: Q4 (within-drug comparison with laboratory models) — not yet built; stated in the output.

Output: data/v04/part2/summary.md, data/v04/part2/summary.json
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from s7_import_review import clopper_pearson

PRIMARY = {"same-molecule", "species-specific-biologic"}

def origin(p):
    """systematic if any veterinary record came from the COTC list or the PubMed frame; else exemplar-only."""
    return "systematic" if any(s.split("+")[0] in ("pubmed", "cotc") or "pubmed" in s for s in p["sources"]) else "exemplar-only"

def tally(pairs):
    c = collections.Counter(p["judgement"]["pair"] for p in pairs)
    classifiable = c["concordant"] + c["discordant"]
    lo, hi = clopper_pearson(c["concordant"], classifiable) if classifiable else (None, None)
    return {"n": len(pairs), "concordant": c["concordant"], "discordant": c["discordant"], "mixed": c["mixed"],
            "indeterminate": c["indeterminate"], "classifiable": classifiable,
            "concordance": round(c["concordant"] / classifiable, 3) if classifiable else None, "ci95": [lo, hi]}

def row(label, t):
    conc = f"{t['concordance']:.0%} ({t['ci95'][0]:.0%}–{t['ci95'][1]:.0%})" if t["classifiable"] else "—"
    return (f"| {label} | {t['n']} | {t['concordant']} | {t['discordant']} | {t['mixed']} | {t['indeterminate']} | "
            f"{t['concordant']}/{t['classifiable']} | {conc} |")

def main():
    allp = [p for p in load("part2/pairs.json").values() if p.get("status") == "classified" and not p.get("flag")]
    flagged = [p for p in load("part2/pairs.json").values() if p.get("flag")]
    other = collections.Counter(p.get("status", "error") for p in load("part2/pairs.json").values() if p.get("status") != "classified")
    for p in allp:
        p["_intent"] = (p.get("terms") or {}).get("treatment_intent", "disease-modifying").lower()
        p["_intent"] = "disease-modifying" if "disease" in p["_intent"] else "symptomatic-or-preventive"
        p["_origin"] = origin(p)
    eff = [p for p in allp if p.get("pair_type", "efficacy") == "efficacy"]
    prim = [p for p in eff if p["relation"] in PRIMARY]
    strata = {
        "Primary: all": prim,
        "Primary: disease-modifying use": [p for p in prim if p["_intent"] == "disease-modifying"],
        "Primary: symptomatic or preventive use": [p for p in prim if p["_intent"] != "disease-modifying"],
        "Primary: systematically found": [p for p in prim if p["_origin"] == "systematic"],
        "Primary: exemplar-only": [p for p in prim if p["_origin"] == "exemplar-only"],
        "Primary, disease-modifying: dog": [p for p in prim if p["_intent"] == "disease-modifying" and p["species"] == ["dog"]],
        "Primary, disease-modifying: cat": [p for p in prim if p["_intent"] == "disease-modifying" and p["species"] == ["cat"]],
        "Class analogues (separate stratum)": [p for p in eff if p["relation"] == "class-analogue"],
        "Safety pairs (separate)": [p for p in allp if p.get("pair_type") == "safety"],
    }
    tallies = {k: tally(v) for k, v in strata.items()}
    save({"built": today(), "tallies": tallies, "excluded_statuses": dict(other), "flagged_invalid_citations": len(flagged)}, "part2/summary.json")

    L = ["# Dog and cat drug pairs: summary (draft)", "", f"Built {today()} by `analysis/v04/d3_summary.py`.", "",
         "Concordance = concordant / (concordant + discordant), with exact 95% CI. Mixed and indeterminate pairs are counted "
         "and shown, never dropped. Strata are never pooled.", "",
         "| stratum | pairs | concordant | discordant | mixed | indeterminate | concordant / classifiable | concordance (95% CI) |",
         "|---|---|---|---|---|---|---|---|"]
    L += [row(k, t) for k, t in tallies.items()]
    L += ["", f"Not classified: {dict(other)}. Judgements set aside for citing a record outside the retrieved set: {len(flagged)}.", "",
          "**Not yet produced:** Q4, the within-drug comparison of companion-animal and laboratory-model concordance "
          "(protocol §7.6). The F1 statement therefore cannot be made yet.", ""]
    dm = [p for p in prim if p["_intent"] == "disease-modifying" and p["judgement"]["pair"] in ("concordant", "discordant", "mixed")]
    L += ["## Primary, disease-modifying pairs with a determinate or mixed result", "",
          "| drug | condition | species | veterinary | human (level) | pair | found by |", "|---|---|---|---|---|---|---|"]
    for p in sorted(dm, key=lambda p: (p["judgement"]["pair"], p["ingredient"])):
        j = p["judgement"]
        L.append(f"| {p['ingredient'].lower()} | {p['veterinary_indication']} | {', '.join(p['species'])} | {j['veterinary']} | "
                 f"{j['human']} ({j['human_top_level']}) | **{j['pair']}** | {p['_origin']} |")
    open(os.path.join(V04, "part2", "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:20]))

if __name__ == "__main__":
    main()
