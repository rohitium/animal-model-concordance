"""Stage 5 — decision, canaries, audit sample and review queue (PLAN.md v0.4 §8.1 stage 4, §8.3, §8.4).

Every item ends in exactly one status:
  accepted                  both extractions agree, located in the PDF text, every check passes
  excluded-cited            quoted from other work (both extractor and verifier agree)
  excluded-not-live-animal  index test is not a live animal (extractor and verifier agree)
  excluded-pdx              patient-derived xenograft stratum
  excluded-study            the study failed the stage-1 scope screen
  flagged                   anything else; goes to the human review queue with its reasons

Nothing is silently dropped: excluded items keep their reason and remain in the output.
Outputs: s5_decisions.json, review_queue.json, audit_sample.json, canary_report.json, step1_report.md
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from s4_verify import CHECKS

CRITICAL = ["species", "level", "index_test_kind", "provenance", "metric", "numerator", "denominator"]
LOCATED = {"value-and-quote-same-page", "value-and-quote-different-pages", "quote-found"}
AUDIT_N, AUDIT_SEED = 30, 20260914
FLAG_RATE_LIMIT = 0.30

def decide(x, scope, ver):
    role = "A" if x["A"] else "B"
    rec = x[role]
    st = scope.get(x["pmid"], {}).get("decision")
    reasons = []
    if st in ("exclude",):
        return "excluded-study", ["stage 1: no live-animal-vs-human comparison (both models)"]
    if st == "pdx-stratum":
        return "excluded-pdx", ["stage 1: patient-derived xenograft study"]
    if st == "include-provisional":
        reasons.append("stage 1: models disagreed on scope")
    v = ver.get(x["id"], {})
    if "error" in v or not v:
        return "flagged", reasons + ["verifier call failed"]
    ck = v["checks"]

    kinds = {c["index_test_kind"] for c in (x["A"], x["B"]) if c}
    provs = {c["provenance"] for c in (x["A"], x["B"]) if c}
    if kinds == {"patient-derived-xenograft"}:
        return "excluded-pdx", ["patient-derived xenograft"]
    if "live-animal" not in kinds and ck["live_animal_index"]["answer"] == "no":
        return "excluded-not-live-animal", [f"index test: {sorted(kinds)}; verifier: {ck['live_animal_index']['note']}"]
    if provs <= {"cited-from-other-study", "condensed-from-authors-earlier-work"} and \
            ck["provenance_correct"]["answer"] == "yes":
        return "excluded-cited", [f"provenance {sorted(provs)} confirmed by verifier"]

    if not (x["A"] and x["B"]):
        reasons.append(f"found by only one extractor ({role})")
    else:
        bad = [f for f in x.get("disagreements", []) if f in CRITICAL]
        if bad:
            reasons.append("extractors disagree on: " + ", ".join(
                f"{f} (A={x['A'].get(f)!r}, B={x['B'].get(f)!r})" for f in bad))
    loc = x["locate"][role]["status"]
    if loc not in LOCATED:
        reasons.append({"value-only": "value found in PDF text but quote not matched",
                        "quote-only": "quote found but value not in PDF text (check figure/table image)",
                        "not-found": "neither value nor quote found in PDF text layer"}.get(loc, loc))
    for k in CHECKS:
        a = ck[k]["answer"]
        if a in ("no", "unclear"):
            reasons.append(f"verifier {k}: {a} — {ck[k]['note']}")
    if rec["disease_area"] == "new":
        reasons.append(f"new disease area proposed: {rec.get('new_disease_area')}")
    if "live-animal" not in kinds:
        reasons.append(f"index test recorded as {sorted(kinds)}")
    return ("flagged", reasons) if reasons else ("accepted", [])

# --- canaries (§8.3) -------------------------------------------------------------------------
def _vals(c):
    v = c.get("value")
    return None if v is None else (v / 100 if c.get("unit") == "percent" else v)

def near(v, targets, tol=0.006):
    return v is not None and any(abs(v - t) <= tol for t in targets)

def evaluate_canaries(dec, items, scope):
    can = load("canaries.json")["canaries"]
    by_pm = collections.defaultdict(list)
    for x in items:
        by_pm[x["pmid"]].append(x)
    res = []
    for c in can:
        pm, rows = c["pmid"], by_pm.get(c["pmid"], [])
        rec = lambda x: x["A"] or x["B"]
        acc = [x for x in rows if dec[x["id"]]["status"] == "accepted"]
        detail, ok = "", None
        if pm not in scope:
            ok, detail = False, "study not in stage-1 output"
        elif c["rule"] == "perel":
            head = [x for x in rows if dec[x["id"]]["status"] in ("accepted", "flagged") and
                    ((rec(x).get("numerator") == 3 and rec(x).get("denominator") == 6) or
                     near(_vals(rec(x)), [0.5]))]
            effects = [x for x in acc if near(_vals(rec(x)), [0.58, 4.2, 12.5, 1.96, 0.24, 0.29, 0.23, 0.48])]
            ok = bool(head) and not effects
            detail = f"headline 3/6 present: {bool(head)}; animal-only effects auto-accepted: {len(effects)}"
        elif c["rule"] == "out_of_scope":
            ok = not acc
            detail = f"stage-1 decision {scope[pm]['decision']}; auto-accepted items: {len(acc)}"
        elif c["rule"] == "no_in_vitro_accepted":
            ok = None if acc else True
            detail = (f"stage-1 decision {scope[pm]['decision']}; {len(acc)} auto-accepted items need "
                      "human confirmation that each is live-animal") if acc else \
                     f"stage-1 decision {scope[pm]['decision']}; no auto-accepted items"
        elif c["rule"] == "bailey_table4":
            bad = [x for x in acc if rec(x)["species"] in ("rat", "mouse", "rabbit", "dog") and
                   rec(x)["provenance"] == "own-result" and near(rec(x).get("value"), [1.82, 1.39, 1.12, 1.10], 0.005)]
            ok = not bad
            detail = f"Table 4 iNLRs auto-accepted as own result: {len(bad)}"
        elif c["rule"] == "level_c_preprint":
            ab = [x for x in acc if rec(x)["level"] in ("A", "B")]
            pr = scope[pm].get("peer_reviewed")
            ok = not ab and pr == "no-preprint"
            detail = f"auto-accepted level A/B: {len(ab)}; peer_reviewed={pr}"
        elif c["rule"] == "leenaars_tox":
            bad = [x for x in acc if rec(x)["level"] == "A" and near(_vals(rec(x)), [0.44, 0.40, 0.48])]
            ok = not bad
            detail = f"toxicology figures auto-accepted at level A: {len(bad)}"
        res.append({**c, "result": {True: "caught", False: "MISSED", None: "needs-review"}[ok], "detail": detail})
    return res

def main():
    scope = load("s1_scope.json")
    items = load("s3_items.json", [])
    ver = load("s4_verify.json")
    dec = {}
    for x in items:
        s, r = decide(x, scope, ver)
        dec[x["id"]] = {"status": s, "reasons": r}
    save(dec, "s5_decisions.json")

    counts = collections.Counter(d["status"] for d in dec.values())
    decided = sum(v for k, v in counts.items() if k in ("accepted", "flagged"))
    flag_rate = counts["flagged"] / decided if decided else 0

    queue = []
    for x in items:
        d = dec[x["id"]]
        if d["status"] != "flagged":
            continue
        role = "A" if x["A"] else "B"
        queue.append({"id": x["id"], "pmid": x["pmid"], "title": scope.get(x["pmid"], {}).get("title"),
                      "reasons": d["reasons"], "record": x[role], "other_extraction": x["B" if role == "A" else "A"],
                      "pdf_pages": ver.get(x["id"], {}).get("pages_shown"),
                      "resolution": None, "resolved_value": None, "reviewer_note": ""})
    # Study-level exclusions are also reviewed: a study leaving the corpus must be seen by a person.
    for pm, r in sorted(scope.items()):
        if r.get("decision") in ("exclude", "exclude-provisional", "error", "pdx-stratum"):
            ra = r["A"]["result"] if "error" not in r["A"]["result"] else r["B"]["result"]
            queue.append({"id": f"{pm}-scope", "pmid": pm, "title": r.get("title"), "kind": "confirm-study-exclusion",
                          "reasons": [f"stage 1 decision: {r['decision']}"] + r.get("flags", []) +
                                     [f"model A: {r['A']['result'].get('reason', r['A']['result'].get('error'))}",
                                      f"model B: {r['B']['result'].get('reason', r['B']['result'].get('error'))}"],
                          "record": {"index_tests": ra.get("index_tests")}, "other_extraction": None,
                          "pdf_pages": None, "resolution": None, "resolved_value": None, "reviewer_note": ""})
    save(queue, "review_queue.json")

    acc = [x for x in items if dec[x["id"]]["status"] == "accepted"]
    rng = random.Random(AUDIT_SEED)
    sample = rng.sample(acc, min(AUDIT_N, len(acc)))
    save([{"id": x["id"], "pmid": x["pmid"], "record": x["A"] or x["B"],
           "pdf_page": (x["locate"]["A" if x["A"] else "B"]).get("best_quote_page"),
           "audit_correct": None, "audit_note": ""} for x in sample], "audit_sample.json")

    can = evaluate_canaries(dec, items, scope)
    save(can, "canary_report.json")

    triggers = []
    if any(c["result"] == "MISSED" for c in can):
        triggers.append("canary missed: " + ", ".join(c["id"] for c in can if c["result"] == "MISSED"))
    if flag_rate > FLAG_RATE_LIMIT:
        triggers.append(f"flag rate {flag_rate:.0%} > {FLAG_RATE_LIMIT:.0%}")

    reason_tally = collections.Counter()
    for d in dec.values():
        for r in d["reasons"]:
            reason_tally[r.split(":")[0].split(" (")[0].split(" — ")[0]] += 1
    scope_tally = collections.Counter(r["decision"] for r in scope.values())

    lines = [f"# Step 1 report — verification workflow on the v0.3 corpus",
             f"", f"Generated {today()} by `analysis/v04/s5_decide.py`. Tier used: "
             f"{sorted({x['tier'] for x in items})}. Models: {sorted({m for x in items for m in x['models'].values()})}.",
             f"", f"## Stage 1 — scope ({len(scope)} studies)", ""]
    lines += [f"- {k}: {v}" for k, v in scope_tally.most_common()]
    lines += ["", f"## Items ({len(items)})", ""] + [f"- {k}: {v}" for k, v in counts.most_common()]
    lines += ["", f"Flag rate among accepted+flagged: **{flag_rate:.0%}** (limit {FLAG_RATE_LIMIT:.0%}).",
              "", "## Why items were flagged", ""] + [f"- {k}: {v}" for k, v in reason_tally.most_common(20)]
    lines += ["", "## Canaries", "", "| id | study | result | detail |", "|---|---|---|---|"]
    lines += [f"| {c['id']} | {c['study']} | {c['result']} | {c['detail']} |" for c in can]
    lines += ["", "## Escalation triggers (§8.2)", ""]
    lines += [f"- {t}" for t in triggers] or ["- none"]
    lines += ["", f"Audit sample: {len(sample)} accepted items (seed {AUDIT_SEED}) in `audit_sample.json`, "
              "awaiting human check.", f"Review queue: {len(queue)} items in `review_queue.json`.",
              f"", f"Cost this run (uncached calls only): ${COST['usd']:.3f}"]
    open(os.path.join(V04, "step1_report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
