"""Reproducible extraction audit. Checks for the failure mode that matters most in
this project: numbers that are not in the source. Run after any extraction pass."""
import json, re, os, sys
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, *p)
ft = json.load(open(J("data","db","fulltext_extract.json")))
ok = {k: v for k, v in ft.items() if "error" not in v}
report = {"n_fulltext": len(ok), "out_of_range": [], "unmatched_percentages": [],
          "degenerate": [], "fill_rates": {}}

for k, v in ok.items():
    for f in ("concordance_value","sensitivity","specificity","ppv","npv"):
        x = v.get(f)
        if isinstance(x, (int, float)) and not (0 <= x <= 1):
            report["out_of_range"].append({"pmid": k, "field": f, "value": x})

checked = 0
for k, v in ok.items():
    p = J("data","raw","fulltext", f"{k}.xml")
    if not os.path.exists(p): continue
    src = open(p, encoding="utf-8", errors="replace").read()
    nums = set(re.findall(r"\d+\.?\d*%", src))
    for s in (v.get("key_numbers") or [])[:12]:
        for m in re.findall(r"\d+\.?\d*%", s):
            checked += 1
            if m in nums: continue
            # A bare number present without its % sign is a formatting artefact,
            # not a fabrication (source: "70% to just 72 and 70.4%").
            bare = m.rstrip("%")
            artefact = bool(re.search(r"[\s(±]" + re.escape(bare) + r"[\s,)%]", src))
            report["unmatched_percentages"].append(
                {"pmid": k, "token": m, "claim": s[:160],
                 "verdict": "formatting artefact" if artefact else "NOT IN SOURCE"})
report["n_percentages_checked"] = checked
report["degenerate"] = [k for k, v in ok.items()
    if not v.get("key_numbers") and not v.get("species_results")
    and v.get("concordance_value") is None and not v.get("concordance_definition")]
for f in ("concordance_definition","species_results","key_numbers","endpoints_animal",
          "endpoints_human","limitations_stated","n_pairs","two_by_two","sensitivity"):
    n = sum(1 for v in ok.values() if v.get(f) not in (None, "", [], {}))
    report["fill_rates"][f] = {"n": n, "of": len(ok), "pct": round(n/len(ok), 3)}

json.dump(report, open(J("data","db","audit.json"), "w"), indent=1)
fab = [u for u in report["unmatched_percentages"] if u["verdict"] == "NOT IN SOURCE"]
print(f"full texts audited      : {len(ok)}")
print(f"percentages checked     : {checked}")
print(f"out-of-range values     : {len(report['out_of_range'])}")
print(f"degenerate extractions  : {len(report['degenerate'])}")
print(f"formatting artefacts    : {len(report['unmatched_percentages']) - len(fab)}")
print(f"NOT FOUND IN SOURCE     : {len(fab)}")
for u in fab: print("  !", u["pmid"], u["token"], "|", u["claim"][:110])
bad = fab or report["out_of_range"]
if report["out_of_range"]:
    print("  ! out-of-range values are type errors: a quantity that is not a "
          "proportion has been stored in a proportion field.")
    for o in report["out_of_range"]: print("   ", o)
sys.exit(1 if bad else 0)
