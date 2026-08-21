"""Eligibility follows the finest available evidence.

Two checks judge whether a study compares animals with humans:
  - 23_crossspecies: one verdict per STUDY, from a summary of its measurements
  - 25_measurement_scope: one verdict per MEASUREMENT

They disagreed on O'Collins 2006 (1,026 experimental treatments in acute stroke, 643
citations). The study-level judge returned "none-found"; the per-measurement scoper had
already identified two animal-vs-human figures -- the average neuroprotection of drugs
that reached the clinic (31.3%) versus drugs tested only in animals (24.4%), which is
the paper's central result and a direct animal-to-human translation finding.

A per-measurement verdict is strictly better evidence than a summary judgement over the
same measurements, so it wins. The study-level check is retained only where no
measurements were extracted."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
db  = json.load(open(J("data","db","studies.json")))
ms  = json.load(open(J("data","db","measurements.json")))
sc  = json.load(open(J("data","db","measurement_scope.json")))
xs  = json.load(open(J("data","db","crossspecies.json")))
an  = json.load(open(J("data","db","animal_screen.json")))
aud = json.load(open(J("data","db","measurement_audit.json")))
unsup = {(a["pmid"], a["index"]) for a in aud}

def ah_count(pm):
    mm = (ms.get(pm) or {}).get("measurements") or []
    s = sc.get(pm) or {}
    if "error" in s: return None
    # Both categories are concordance evidence: a figure comparing an animal result
    # with a human result, and a figure comparing animal results between groups defined
    # by what happened in humans (does animal efficacy track clinical success?).
    return sum(1 for i in range(len(mm))
               if s.get(str(i)) in ("animal-vs-human", "animal-result-by-human-outcome") and (pm, i) not in unsup)

changed = []
for pm, v in db.items():
    a = an.get(pm) or {}
    # r3 exclusions (not a whole-animal index test) are unaffected by this reconciliation
    if a.get("decision") == "exclude":
        continue
    n = ah_count(pm)
    if n is None or ((ms.get(pm) or {}).get("measurements") is None):
        continue
    if n and n > 0:
        if v.get("eligible") is not True:
            changed.append((pm, "restored", n))
        v["eligible"] = True
        v["exclusion_reason"] = None
        v["r4_comparison_type"] = "animal-vs-human"
        v["ah_measurement_count"] = n
    else:
        v["ah_measurement_count"] = 0
        if v.get("eligible") is not False:
            x = xs.get(pm) or {}
            v["eligible"] = False
            v["exclusion_reason"] = (f"No animal-vs-human figure among its extracted "
                                     f"measurements. {x.get('reason','')[:180]}")
            changed.append((pm, "excluded", 0))

json.dump(db, open(J("data","db","studies.json"), "w"), indent=1)
elig = [p for p, v in db.items() if v.get("eligible")]
print(f"eligible {len(elig)}/{len(db)}")
for pm, what, n in changed:
    print(f"  {what:8s} {pm} ah={n} {db[pm].get('cited_by'):>5} cites  {db[pm]['title'][:56]}")
